#!/usr/bin/env python3
"""Replay an EuRoC-format sequence as ROS 1 topics for Voxel-SVIO.

Publishes:
    /cam0/image_raw  sensor_msgs/Image (mono8)
    /cam1/image_raw  sensor_msgs/Image (mono8)
    /imu0            sensor_msgs/Imu

Voxel-SVIO subscribes to these topics and writes its trajectory to
output_path/pose.txt as TUM format (timestamp tx ty tz qx qy qz qw).

Designed to run *inside* the voxel_svio Docker container alongside the
vio_node launched via roslaunch.

Usage:
    python3 voxel_svio_data_player.py <seq_dir> [--rate 1.0] \
        [--start-delay 1.0] [--end-wait 2.0]

`<seq_dir>` is the directory containing mav0/. Image timestamps come from
mav0/cam0/data.csv (and /cam1/data.csv); IMU samples come from
mav0/imu0/data.csv. All timestamps are nanoseconds.
"""
from __future__ import annotations

import argparse
import csv
import sys
import threading
import time
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
import rospy
from sensor_msgs.msg import Image, Imu
from cv_bridge import CvBridge


# ---------------------------------------------------------------------------
# Data loading
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


def _ros_time(t_ns: int) -> rospy.Time:
    return rospy.Time(secs=t_ns // 1_000_000_000, nsecs=t_ns % 1_000_000_000)


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("seq_dir", type=Path,
                    help="Directory containing mav0/")
    ap.add_argument("--rate", type=float, default=1.0,
                    help="Replay rate multiplier (1.0 = real time)")
    ap.add_argument("--start-delay", type=float, default=2.0,
                    help="Seconds to wait before starting publishing")
    ap.add_argument("--end-wait", type=float, default=3.0,
                    help="Seconds to wait after last message before exiting")
    ap.add_argument("--frame-id-cam", default="cam")
    ap.add_argument("--frame-id-imu", default="imu")
    args = ap.parse_args()

    mav0 = args.seq_dir / "mav0"
    cam0_csv = mav0 / "cam0" / "data.csv"
    cam1_csv = mav0 / "cam1" / "data.csv"
    imu_csv  = mav0 / "imu0" / "data.csv"
    cam0_dir = mav0 / "cam0" / "data"
    cam1_dir = mav0 / "cam1" / "data"
    for p in (cam0_csv, cam1_csv, imu_csv, cam0_dir, cam1_dir):
        if not p.exists():
            print(f"[player] missing: {p}", file=sys.stderr)
            return 2

    rospy.init_node("voxel_svio_data_player", anonymous=False, disable_signals=True)

    pub_cam0 = rospy.Publisher("/cam0/image_raw", Image, queue_size=10)
    pub_cam1 = rospy.Publisher("/cam1/image_raw", Image, queue_size=10)
    pub_imu  = rospy.Publisher("/imu0",            Imu,   queue_size=200)

    bridge = CvBridge()

    cam0 = _load_cam(cam0_csv, cam0_dir)
    cam1 = _load_cam(cam1_csv, cam1_dir)
    imu  = _load_imu(imu_csv)

    if not cam0 or not cam1 or not imu:
        print(f"[player] empty data: cam0={len(cam0)} cam1={len(cam1)} imu={len(imu)}",
              file=sys.stderr)
        return 2

    # Index cam1 by timestamp for fast lookup.
    cam1_idx = {t: p for t, p in cam1}

    print(f"[player] cam0={len(cam0)} cam1={len(cam1)} imu={len(imu)}", flush=True)
    print(f"[player] waiting {args.start_delay}s for subscribers ...", flush=True)
    time.sleep(args.start_delay)

    # Merge events: (timestamp_ns, kind, payload)
    events = []
    for t, wx, wy, wz, ax, ay, az in imu:
        events.append((t, "imu", (wx, wy, wz, ax, ay, az)))
    for t, p in cam0:
        events.append((t, "cam", p))
    events.sort(key=lambda e: e[0])

    t0_data_ns = events[0][0]
    t0_wall = time.time()
    n_imu = n_cam = 0

    for ev in events:
        if rospy.is_shutdown():
            break
        t_ns, kind, payload = ev

        # Pace replay according to dataset timestamps.
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
            # Voxel-SVIO does not use the orientation field; leave covariances
            # at 0 (default).
            pub_imu.publish(msg)
            n_imu += 1
        else:  # cam
            p0 = payload
            p1 = cam1_idx.get(t_ns)
            if p1 is None:
                # Not all stereo pairs are perfectly synchronised; skip the cam0
                # frame if cam1 has no matching timestamp.
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
                print(f"[player] cam={n_cam} imu={n_imu} t_data={t_data:.1f}s", flush=True)

    print(f"[player] done: cam={n_cam} imu={n_imu}; waiting {args.end_wait}s ...", flush=True)
    time.sleep(args.end_wait)
    return 0


if __name__ == "__main__":
    sys.exit(main())
