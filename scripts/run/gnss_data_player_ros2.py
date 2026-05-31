#!/usr/bin/env python3
"""ROS 2 (rclpy) version of gnss_data_player.py.

Replays an EuRoC-format sequence + gps.csv as ROS 2 topics for native ROS 2
GNSS-VIO algorithms (RTAB-Map, etc.).

Publishes:
    /cam0/image_raw    sensor_msgs/Image (mono8)
    /cam1/image_raw    sensor_msgs/Image (mono8)
    /cam0/camera_info  sensor_msgs/CameraInfo
    /cam1/camera_info  sensor_msgs/CameraInfo
    /imu0              sensor_msgs/Imu
    /fix               sensor_msgs/NavSatFix     (configurable)

Camera-info messages are populated from the per-dataset YAML loaded from
configs/<algo>/<dataset>.yaml when --camera-info-yaml is given. When omitted,
camera_info publishing is skipped.

Inputs:
    <seq_dir>/mav0/cam0/data/*.png  +  cam0/data.csv
    <seq_dir>/mav0/cam1/data/*.png  +  cam1/data.csv
    <seq_dir>/mav0/imu0/data.csv
    <seq_dir>/gps.csv               (header: t,lat,lon,alt[,cov_xx,cov_yy,cov_zz,status])
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import cv2  # type: ignore
import rclpy
from cv_bridge import CvBridge  # type: ignore
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image, Imu, NavSatFix, NavSatStatus, CameraInfo
from builtin_interfaces.msg import Time as TimeMsg


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
    out = []
    with csv_path.open() as f:
        rd = csv.reader(f)
        first = next(rd, None)
        if first is None:
            return out
        rows = []
        try:
            float(first[0])
            rows.append(first)
        except (ValueError, IndexError):
            pass
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


def _t_msg(t_ns: int) -> TimeMsg:
    m = TimeMsg()
    m.sec = t_ns // 1_000_000_000
    m.nanosec = t_ns % 1_000_000_000
    return m


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("seq_dir", type=Path)
    ap.add_argument("--rate", type=float, default=1.0)
    ap.add_argument("--start-delay", type=float, default=2.0)
    ap.add_argument("--end-wait", type=float, default=3.0)
    ap.add_argument("--frame-id-cam", default="cam")
    ap.add_argument("--frame-id-imu", default="imu")
    ap.add_argument("--frame-id-gps", default="gps")
    ap.add_argument("--gps-topic", default="/fix")
    ap.add_argument("--cam0-topic", default="/cam0/image_raw")
    ap.add_argument("--cam1-topic", default="/cam1/image_raw")
    ap.add_argument("--imu-topic",  default="/imu0")
    ap.add_argument("--gps-status", type=int, default=NavSatStatus.STATUS_FIX)
    ap.add_argument("--gps-cov-xy", type=float, default=1.0)
    ap.add_argument("--gps-cov-z", type=float, default=4.0)
    ap.add_argument("--no-gps", action="store_true")
    ap.add_argument("--gps-csv", type=Path, default=None)
    # Camera intrinsics for CameraInfo publishing (rectified pinhole stereo).
    # If any of fx/fy/cx/cy/baseline are <=0, CameraInfo is NOT published.
    ap.add_argument("--cam-width",    type=int,   default=0)
    ap.add_argument("--cam-height",   type=int,   default=0)
    ap.add_argument("--cam-fx",       type=float, default=0.0)
    ap.add_argument("--cam-fy",       type=float, default=0.0)
    ap.add_argument("--cam-cx",       type=float, default=0.0)
    ap.add_argument("--cam-cy",       type=float, default=0.0)
    ap.add_argument("--cam-baseline", type=float, default=0.0,
                    help="Stereo baseline (m). cam1 P[0,3] = -fx*baseline.")
    ap.add_argument("--cam0-info-topic", default="/cam0/camera_info")
    ap.add_argument("--cam1-info-topic", default="/cam1/camera_info")
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

    rclpy.init()
    node = Node("gnss_data_player_ros2")

    qos_sensor = QoSProfile(
        reliability=ReliabilityPolicy.RELIABLE,
        history=HistoryPolicy.KEEP_LAST,
        depth=10,
    )

    pub_cam0 = node.create_publisher(Image, args.cam0_topic, qos_sensor)
    pub_cam1 = node.create_publisher(Image, args.cam1_topic, qos_sensor)
    pub_imu  = node.create_publisher(Imu, args.imu_topic, qos_sensor)
    pub_gps  = node.create_publisher(NavSatFix, args.gps_topic, qos_sensor)

    # ---- CameraInfo (rectified pinhole stereo) ----------------------------
    publish_caminfo = (
        args.cam_width > 0 and args.cam_height > 0 and
        args.cam_fx > 0 and args.cam_fy > 0 and
        args.cam_cx > 0 and args.cam_cy > 0
    )
    pub_info0 = pub_info1 = None
    info0_template = info1_template = None
    if publish_caminfo:
        pub_info0 = node.create_publisher(CameraInfo, args.cam0_info_topic, qos_sensor)
        pub_info1 = node.create_publisher(CameraInfo, args.cam1_info_topic, qos_sensor)
        fx = args.cam_fx; fy = args.cam_fy
        cx = args.cam_cx; cy = args.cam_cy
        b  = args.cam_baseline
        K  = [fx, 0.0, cx,  0.0, fy, cy,  0.0, 0.0, 1.0]
        R_ = [1.0, 0.0, 0.0,  0.0, 1.0, 0.0,  0.0, 0.0, 1.0]
        P0 = [fx, 0.0, cx, 0.0,    0.0, fy, cy, 0.0,    0.0, 0.0, 1.0, 0.0]
        P1 = [fx, 0.0, cx, -fx*b,  0.0, fy, cy, 0.0,    0.0, 0.0, 1.0, 0.0]
        for tpl, P in (("info0", P0), ("info1", P1)):
            ci = CameraInfo()
            ci.width = int(args.cam_width)
            ci.height = int(args.cam_height)
            ci.distortion_model = "plumb_bob"
            ci.d = [0.0, 0.0, 0.0, 0.0, 0.0]
            ci.k = K
            ci.r = R_
            ci.p = P
            if tpl == "info0":
                info0_template = ci
            else:
                info1_template = ci

    bridge = CvBridge()

    cam0 = _load_cam(cam0_csv, cam0_dir)
    cam1 = _load_cam(cam1_csv, cam1_dir)
    imu  = _load_imu(imu_csv)
    gps: list = []
    if (not args.no_gps) and gps_csv.exists():
        gps = _load_gps(gps_csv)
    elif args.no_gps:
        node.get_logger().info("--no-gps: skipping GPS publishing")
    else:
        node.get_logger().info(f"no gps.csv at {gps_csv}; running without GPS")

    if not cam0 or not cam1 or not imu:
        node.get_logger().error(
            f"empty data: cam0={len(cam0)} cam1={len(cam1)} imu={len(imu)}"
        )
        return 2

    cam1_idx = {t: p for t, p in cam1}

    node.get_logger().info(
        f"cam0={len(cam0)} cam1={len(cam1)} imu={len(imu)} gps={len(gps)}"
    )
    node.get_logger().info(
        f"gps_topic={args.gps_topic} status={args.gps_status} "
        f"cov_xy={args.gps_cov_xy} cov_z={args.gps_cov_z}"
    )
    node.get_logger().info(f"waiting {args.start_delay}s for subscribers ...")
    time.sleep(args.start_delay)

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
        if not rclpy.ok():
            break
        t_ns, kind, payload = ev

        target_wall = t0_wall + (t_ns - t0_data_ns) * 1e-9 / max(args.rate, 1e-6)
        sleep_s = target_wall - time.time()
        if sleep_s > 0:
            time.sleep(sleep_s)

        stamp = _t_msg(t_ns)

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
            msg.status.status = int(status) if status else int(args.gps_status)
            msg.status.service = NavSatStatus.SERVICE_GPS
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
        else:
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
            if publish_caminfo:
                info0_template.header.stamp = stamp
                info0_template.header.frame_id = args.frame_id_cam
                info1_template.header.stamp = stamp
                info1_template.header.frame_id = args.frame_id_cam
                pub_info0.publish(info0_template)
                pub_info1.publish(info1_template)
            n_cam += 1
            if n_cam % 200 == 0:
                t_data = (t_ns - t0_data_ns) * 1e-9
                node.get_logger().info(
                    f"cam={n_cam} imu={n_imu} gps={n_gps} t_data={t_data:.1f}s"
                )

    node.get_logger().info(
        f"done: cam={n_cam} imu={n_imu} gps={n_gps}; waiting {args.end_wait}s ..."
    )
    time.sleep(args.end_wait)
    node.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
