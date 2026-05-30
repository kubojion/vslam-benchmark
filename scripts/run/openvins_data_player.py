#!/usr/bin/env python3
"""Replay an EuRoC-format sequence as ROS 2 topics for OpenVINS, and record
the resulting trajectory in TUM format.

Publishes:
    /cam0/image_raw  sensor_msgs/Image (mono8)
    /cam1/image_raw  sensor_msgs/Image (mono8)
    /imu0            sensor_msgs/Imu

Subscribes:
    /ov_msckf/odomimu  nav_msgs/Odometry  -> writes TUM trajectory.

Designed to run inside the openvins:humble container next to the OpenVINS node
launched via `ros2 launch ov_msckf subscribe.launch.py ...`.

Usage:
    python3 openvins_data_player.py <seq_dir> <out_traj.txt> [--rate 1.0] \
        [--start-delay 1.0] [--end-wait 2.0]

`<seq_dir>` is the directory containing mav0/. Image timestamps are read from
mav0/cam0/data.csv (and /cam1/data.csv); IMU samples come from
mav0/imu0/data.csv. All timestamps are nanoseconds.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import threading
import time
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image, Imu
from nav_msgs.msg import Odometry
from cv_bridge import CvBridge


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

def _load_imu(csv_path: Path) -> List[Tuple[int, float, float, float, float, float, float]]:
    """Return [(t_ns, wx, wy, wz, ax, ay, az)] sorted by timestamp."""
    out = []
    with csv_path.open() as f:
        reader = csv.reader(f)
        for row in reader:
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


def _load_cam(csv_path: Path, img_dir: Path) -> List[Tuple[int, Path]]:
    """Return [(t_ns, full_image_path)] sorted by timestamp."""
    out = []
    with csv_path.open() as f:
        reader = csv.reader(f)
        for row in reader:
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


# ---------------------------------------------------------------------------
# Player node
# ---------------------------------------------------------------------------

class Player(Node):
    def __init__(self, seq_dir: Path, out_traj: Path, rate: float,
                 start_delay: float, end_wait: float):
        super().__init__("openvins_data_player")
        self.seq_dir = seq_dir
        self.out_traj = out_traj
        self.rate = rate
        self.start_delay = start_delay
        self.end_wait = end_wait

        # Publishers. OpenVINS' ROS2Visualizer uses different QoS per topic:
        #   - cameras (message_filters::Subscriber): RELIABLE, depth=10  (default)
        #   - imu  (rclcpp::SensorDataQoS()):        BEST_EFFORT, depth=10
        # Mismatched QoS silently drops messages, so reliability must match.
        # The publisher queue depth is set high so a transient slowdown in the
        # OV node does not back-pressure RELIABLE publishes and stall the
        # player thread (which would also halt IMU pacing because the player
        # is single-threaded). 2000 frames at 30 Hz buffers ~66 s of camera
        # data without blocking.
        cam_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=2000,
        )
        imu_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=200,
        )
        self.pub_cam0 = self.create_publisher(Image, "/cam0/image_raw", cam_qos)
        self.pub_cam1 = self.create_publisher(Image, "/cam1/image_raw", cam_qos)
        self.pub_imu = self.create_publisher(Imu, "/imu0", imu_qos)

        # Subscriber for OpenVINS odometry output. Reliable so we don't drop
        # poses; OpenVINS publishes at ~20 Hz (per camera frame).
        self.sub_odom = self.create_subscription(
            Odometry, "/ov_msckf/odomimu", self._on_odom, 50)

        self.bridge = CvBridge()
        self.poses: List[Tuple[float, float, float, float, float, float, float, float]] = []

        # Load data.
        mav0 = seq_dir / "mav0"
        self.imu = _load_imu(mav0 / "imu0" / "data.csv")
        self.cam0 = _load_cam(mav0 / "cam0" / "data.csv", mav0 / "cam0" / "data")
        self.cam1 = _load_cam(mav0 / "cam1" / "data.csv", mav0 / "cam1" / "data")
        if not self.imu or not self.cam0 or not self.cam1:
            raise RuntimeError(f"empty data in {seq_dir} (imu={len(self.imu)} "
                               f"cam0={len(self.cam0)} cam1={len(self.cam1)})")
        self.get_logger().info(
            f"loaded imu={len(self.imu)} cam0={len(self.cam0)} cam1={len(self.cam1)} "
            f"from {seq_dir}")

    # ------------------------------------------------------------------
    def _on_odom(self, msg: Odometry):
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        self.poses.append((t, p.x, p.y, p.z, q.x, q.y, q.z, q.w))

    # ------------------------------------------------------------------
    def _make_imu_msg(self, t_ns: int, wx, wy, wz, ax, ay, az) -> Imu:
        m = Imu()
        m.header.stamp.sec = t_ns // 1_000_000_000
        m.header.stamp.nanosec = t_ns % 1_000_000_000
        m.header.frame_id = "imu"
        m.angular_velocity.x = wx
        m.angular_velocity.y = wy
        m.angular_velocity.z = wz
        m.linear_acceleration.x = ax
        m.linear_acceleration.y = ay
        m.linear_acceleration.z = az
        # Empty covariances signal "unknown" (-1 on first element by REP-145).
        m.orientation_covariance[0] = -1.0
        return m

    def _make_image_msg(self, t_ns: int, img_path: Path, frame_id: str) -> Image:
        img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise RuntimeError(f"failed to read image {img_path}")
        msg = self.bridge.cv2_to_imgmsg(img, encoding="mono8")
        msg.header.stamp.sec = t_ns // 1_000_000_000
        msg.header.stamp.nanosec = t_ns % 1_000_000_000
        msg.header.frame_id = frame_id
        return msg

    # ------------------------------------------------------------------
    def play(self):
        # Build a unified event list: (t_ns, kind, payload).
        events: List[Tuple[int, str, object]] = []
        for r in self.imu:
            events.append((r[0], "imu", r[1:]))
        for r in self.cam0:
            events.append((r[0], "cam0", r[1]))
        for r in self.cam1:
            events.append((r[0], "cam1", r[1]))
        events.sort(key=lambda e: e[0])

        # Spin the executor in a background thread so subscription callbacks
        # (the /ov_msckf/odomimu pose stream) keep firing while the main
        # thread is busy with pacing and image I/O. Without this the player
        # silently drops poses once it falls slightly behind real time.
        spin_thread = threading.Thread(
            target=lambda: rclpy.spin(self), daemon=True)
        spin_thread.start()

        # Wait for the OpenVINS node to come up and our publishers to be
        # discovered. OpenVINS uses subscription_count gates on output topics
        # and we want to be sure the ROS graph is settled.
        self.get_logger().info(f"start delay {self.start_delay:.1f}s for ROS graph...")
        time.sleep(self.start_delay)

        t0_ns = events[0][0]
        t0_wall = time.time()

        for i, (t_ns, kind, payload) in enumerate(events):
            if not rclpy.ok():
                break
            # Real-time pacing.
            target_wall = t0_wall + (t_ns - t0_ns) / 1e9 / self.rate
            now = time.time()
            if target_wall > now:
                time.sleep(target_wall - now)

            if kind == "imu":
                self.pub_imu.publish(self._make_imu_msg(t_ns, *payload))
            elif kind == "cam0":
                self.pub_cam0.publish(self._make_image_msg(t_ns, payload, "cam0"))
            elif kind == "cam1":
                self.pub_cam1.publish(self._make_image_msg(t_ns, payload, "cam1"))

            if i % 5000 == 0:
                pct = 100.0 * i / len(events)
                self.get_logger().info(
                    f"played {i}/{len(events)} ({pct:.1f}%), "
                    f"poses_received={len(self.poses)}")

        self.get_logger().info(
            f"all events published; waiting {self.end_wait:.1f}s for filter flush...")
        time.sleep(self.end_wait)

        self.write_trajectory()

    # ------------------------------------------------------------------
    def write_trajectory(self):
        self.out_traj.parent.mkdir(parents=True, exist_ok=True)
        with self.out_traj.open("w") as f:
            for row in self.poses:
                f.write("{:.9f} {:.9f} {:.9f} {:.9f} {:.9f} {:.9f} {:.9f} {:.9f}\n".format(*row))
        self.get_logger().info(
            f"wrote {len(self.poses)} poses to {self.out_traj}")


# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("seq_dir", type=Path, help="dir containing mav0/")
    p.add_argument("out_traj", type=Path, help="output TUM trajectory file")
    p.add_argument("--rate", type=float, default=1.0, help="playback rate (1.0=realtime)")
    p.add_argument("--start-delay", type=float, default=2.0,
                   help="seconds to wait before publishing (let OpenVINS register)")
    p.add_argument("--end-wait", type=float, default=3.0,
                   help="seconds to spin after last event before writing trajectory")
    args = p.parse_args()

    if not (args.seq_dir / "mav0").is_dir():
        print(f"ERROR: {args.seq_dir}/mav0 not found", file=sys.stderr)
        sys.exit(2)

    rclpy.init()
    node = Player(args.seq_dir, args.out_traj, args.rate, args.start_delay, args.end_wait)
    try:
        node.play()
    except KeyboardInterrupt:
        node.get_logger().warning("interrupted; writing partial trajectory")
        node.write_trajectory()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
