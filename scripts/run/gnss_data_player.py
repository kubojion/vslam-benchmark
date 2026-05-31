#!/usr/bin/env python3
"""Replay an EuRoC-format sequence + gps.csv as ROS 1 topics for GNSS-VIO.

Extends voxel_svio_data_player.py by also publishing GPS fixes as
sensor_msgs/NavSatFix messages on a configurable topic.

Publishes:
    /cam0/image_raw    sensor_msgs/Image (mono8)
    /cam1/image_raw    sensor_msgs/Image (mono8)
    /imu0              sensor_msgs/Imu
    /fix               sensor_msgs/NavSatFix     (configurable via --gps-topic)

Inputs:
    <seq_dir>/mav0/cam0/data/*.png  +  cam0/data.csv
    <seq_dir>/mav0/cam1/data/*.png  +  cam1/data.csv
    <seq_dir>/mav0/imu0/data.csv
    <seq_dir>/gps.csv               (header: t,lat,lon,alt[,cov_xx,cov_yy,cov_zz,status])

GPS CSV timestamps are seconds (Unix epoch). Image / IMU timestamps in the
mav0 CSVs are nanoseconds. The player aligns all three to the cam0 t0 for
relative pacing and publishes ROS messages at their original (Unix epoch ns)
stamps.

Usage (typically inside an algorithm Docker container):
    python3 gnss_data_player.py <seq_dir>
        [--rate 1.0] [--start-delay 1.0] [--end-wait 3.0]
        [--gps-topic /fix]
        [--gps-status 2]
        [--gps-cov-xy 0.04] [--gps-cov-z 0.09]
        [--no-gps]
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, Imu, NavSatFix, NavSatStatus


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

def _load_imu(csv_path: Path):
    out = []
    with csv_path.open() as f:
        rd = csv.reader(f)
        for row in rd:
            if not row or row[0].lstrip().startswith("#"):
                continue
            try:
                t_ns = int(row[0])
            except ValueError:
                continue
            wx, wy, wz, ax, ay, az = (float(x) for x in row[1:7])
            out.append((t_ns, wx, wy, wz, ax, ay, az))
    out.sort(key=lambda r: r[0])
    return out


def _load_cam(csv_path: Path, img_dir: Path):
    out = []
    with csv_path.open() as f:
        rd = csv.reader(f)
        for row in rd:
            if not row or row[0].lstrip().startswith("#"):
                continue
            try:
                t_ns = int(row[0])
            except ValueError:
                continue
            fname = row[1].strip()
            out.append((t_ns, img_dir / fname))
    out.sort(key=lambda r: r[0])
    return out


def _load_gps(csv_path: Path):
    """Return list of (t_ns, lat, lon, alt, cov_xx, cov_yy, cov_zz, status).

    Columns 4-7 (cov + status) default to 0 when not present in the file.
    Input timestamps are seconds (float) and converted to nanoseconds.
    """
    out = []
    with csv_path.open() as f:
        rd = csv.reader(f)
        # Skip header line.
        first = next(rd, None)
        if first is None:
            return out
        # First row may be header or data: try to parse.
        rows = []
        try:
            float(first[0])
            rows.append(first)
        except (ValueError, IndexError):
            pass  # header
        rows.extend(rd)
        for row in rows:
            if not row:
                continue
            try:
                t_s = float(row[0])
                lat = float(row[1])
                lon = float(row[2])
                alt = float(row[3])
            except (ValueError, IndexError):
                continue
            cov_xx = float(row[4]) if len(row) > 4 and row[4] else 0.0
            cov_yy = float(row[5]) if len(row) > 5 and row[5] else 0.0
            cov_zz = float(row[6]) if len(row) > 6 and row[6] else 0.0
            status = int(float(row[7])) if len(row) > 7 and row[7] else 0
            out.append((int(t_s * 1e9), lat, lon, alt, cov_xx, cov_yy, cov_zz, status))
    out.sort(key=lambda r: r[0])
    return out


def _ros_time(t_ns: int) -> rospy.Time:
    return rospy.Time(secs=t_ns // 1_000_000_000, nsecs=t_ns % 1_000_000_000)


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("seq_dir", type=Path,
                    help="Directory containing mav0/ and (optionally) gps.csv")
    ap.add_argument("--rate", type=float, default=1.0,
                    help="Replay rate multiplier (1.0 = real time)")
    ap.add_argument("--start-delay", type=float, default=2.0,
                    help="Seconds to wait before publishing")
    ap.add_argument("--end-wait", type=float, default=3.0,
                    help="Seconds to wait after last message before exiting")
    ap.add_argument("--frame-id-cam", default="cam")
    ap.add_argument("--frame-id-imu", default="imu")
    ap.add_argument("--frame-id-gps", default="gps")
    ap.add_argument("--gps-topic", default="/fix",
                    help="GPS publish topic (default /fix)")
    ap.add_argument("--cam0-topic", default="/cam0/image_raw")
    ap.add_argument("--cam1-topic", default="/cam1/image_raw")
    ap.add_argument("--imu-topic",  default="/imu0")
    ap.add_argument("--gps-status", type=int, default=NavSatStatus.STATUS_FIX,
                    help="NavSatStatus.status to use when not in CSV "
                         "(default STATUS_FIX=0; use 2 for STATUS_GBAS_FIX/RTK)")
    ap.add_argument("--gps-cov-xy", type=float, default=1.0,
                    help="Default horizontal cov [m^2] when CSV has no covariance "
                         "(0.04 for PPK, 1.0 for conventional GPS)")
    ap.add_argument("--gps-cov-z", type=float, default=4.0,
                    help="Default vertical cov [m^2] when CSV has no covariance")
    ap.add_argument("--no-gps", action="store_true",
                    help="Skip GPS publishing even if gps.csv exists")
    ap.add_argument("--gps-csv", type=Path, default=None,
                    help="Override path to gps.csv (default <seq_dir>/gps.csv)")
    args = ap.parse_args()

    mav0 = args.seq_dir / "mav0"
    cam0_csv = mav0 / "cam0" / "data.csv"
    cam1_csv = mav0 / "cam1" / "data.csv"
    imu_csv  = mav0 / "imu0" / "data.csv"
    cam0_dir = mav0 / "cam0" / "data"
    cam1_dir = mav0 / "cam1" / "data"
    gps_csv  = args.gps_csv if args.gps_csv else (args.seq_dir / "gps.csv")

    for p in (cam0_csv, cam1_csv, imu_csv, cam0_dir, cam1_dir):
        if not p.exists():
            print(f"[player] missing: {p}", file=sys.stderr)
            return 2

    rospy.init_node("gnss_data_player", anonymous=False, disable_signals=True)

    pub_cam0 = rospy.Publisher(args.cam0_topic, Image, queue_size=10)
    pub_cam1 = rospy.Publisher(args.cam1_topic, Image, queue_size=10)
    pub_imu  = rospy.Publisher(args.imu_topic, Imu, queue_size=200)
    pub_gps  = rospy.Publisher(args.gps_topic, NavSatFix, queue_size=20)

    bridge = CvBridge()

    cam0 = _load_cam(cam0_csv, cam0_dir)
    cam1 = _load_cam(cam1_csv, cam1_dir)
    imu  = _load_imu(imu_csv)
    gps: list = []
    if (not args.no_gps) and gps_csv.exists():
        gps = _load_gps(gps_csv)
    elif args.no_gps:
        print("[player] --no-gps: skipping GPS publishing", flush=True)
    else:
        print(f"[player] no gps.csv at {gps_csv}; running without GPS", flush=True)

    if not cam0 or not cam1 or not imu:
        print(f"[player] empty data: cam0={len(cam0)} cam1={len(cam1)} imu={len(imu)}",
              file=sys.stderr)
        return 2

    cam1_idx = {t: p for t, p in cam1}

    print(f"[player] cam0={len(cam0)} cam1={len(cam1)} imu={len(imu)} gps={len(gps)}",
          flush=True)
    print(f"[player] gps_topic={args.gps_topic} status={args.gps_status} "
          f"cov_xy={args.gps_cov_xy} cov_z={args.gps_cov_z}", flush=True)
    print(f"[player] waiting {args.start_delay}s for subscribers ...", flush=True)
    time.sleep(args.start_delay)

    # Merge events: (timestamp_ns, kind, payload)
    events = []
    for t, wx, wy, wz, ax, ay, az in imu:
        events.append((t, "imu", (wx, wy, wz, ax, ay, az)))
    for t, p in cam0:
        events.append((t, "cam", p))
    for fix in gps:
        events.append((fix[0], "gps", fix[1:]))
    events.sort(key=lambda e: e[0])

    t0_data_ns = events[0][0]
    t0_wall = time.time()
    n_imu = n_cam = n_gps = 0

    for ev in events:
        if rospy.is_shutdown():
            break
        t_ns, kind, payload = ev

        target_wall = t0_wall + (t_ns - t0_data_ns) * 1e-9 / max(args.rate, 1e-6)
        sleep_s = target_wall - time.time()
        if sleep_s > 0:
            time.sleep(sleep_s)

        stamp = _ros_time(t_ns)

        if kind == "imu":
            wx, wy, wz, ax, ay, az = payload
            msg = Imu()
            msg.header.stamp = stamp
            msg.header.frame_id = args.frame_id_imu
            msg.angular_velocity.x = wx
            msg.angular_velocity.y = wy
            msg.angular_velocity.z = wz
            msg.linear_acceleration.x = ax
            msg.linear_acceleration.y = ay
            msg.linear_acceleration.z = az
            pub_imu.publish(msg)
            n_imu += 1
        elif kind == "gps":
            lat, lon, alt, cov_xx, cov_yy, cov_zz, status = payload
            msg = NavSatFix()
            msg.header.stamp = stamp
            msg.header.frame_id = args.frame_id_gps
            msg.latitude = lat
            msg.longitude = lon
            msg.altitude = alt
            # Status / service: prefer CSV value when present, else CLI default.
            msg.status.status = int(status) if status else int(args.gps_status)
            msg.status.service = NavSatStatus.SERVICE_GPS
            # Covariance: prefer CSV values when nonzero, else CLI defaults.
            if cov_xx > 0 or cov_yy > 0 or cov_zz > 0:
                cxx, cyy, czz = cov_xx, cov_yy, cov_zz
            else:
                cxx, cyy, czz = args.gps_cov_xy, args.gps_cov_xy, args.gps_cov_z
            msg.position_covariance = [
                cxx, 0.0, 0.0,
                0.0, cyy, 0.0,
                0.0, 0.0, czz,
            ]
            msg.position_covariance_type = NavSatFix.COVARIANCE_TYPE_DIAGONAL_KNOWN
            pub_gps.publish(msg)
            n_gps += 1
        else:  # cam
            p0 = payload
            p1 = cam1_idx.get(t_ns)
            if p1 is None:
                continue
            img0 = cv2.imread(str(p0), cv2.IMREAD_GRAYSCALE)
            img1 = cv2.imread(str(p1), cv2.IMREAD_GRAYSCALE)
            if img0 is None or img1 is None:
                continue
            m0 = bridge.cv2_to_imgmsg(img0, encoding="mono8")
            m1 = bridge.cv2_to_imgmsg(img1, encoding="mono8")
            m0.header.stamp = m1.header.stamp = stamp
            m0.header.frame_id = m1.header.frame_id = args.frame_id_cam
            pub_cam0.publish(m0)
            pub_cam1.publish(m1)
            n_cam += 1
            if n_cam % 200 == 0:
                t_data = (t_ns - t0_data_ns) * 1e-9
                print(f"[player] cam={n_cam} imu={n_imu} gps={n_gps} t_data={t_data:.1f}s",
                      flush=True)

    print(f"[player] done: cam={n_cam} imu={n_imu} gps={n_gps}; "
          f"waiting {args.end_wait}s ...", flush=True)
    time.sleep(args.end_wait)
    return 0


if __name__ == "__main__":
    sys.exit(main())
