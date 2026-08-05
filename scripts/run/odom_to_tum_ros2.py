#!/usr/bin/env python3
"""Minimal ROS 2 (rclpy) odometry -> TUM trajectory recorder.

Subscribes to a nav_msgs/Odometry topic and writes TUM format:
    timestamp tx ty tz qx qy qz qw

Exits cleanly after --idle-timeout seconds with no new messages (i.e. the
sequence playback has ended and the EKF has flushed).

Usage:
    python3 odom_to_tum_ros2.py --topic /odometry/filtered --out /tmp/traj.txt
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


class TumRecorder(Node):
    def __init__(self, topic: str, out: Path, idle_timeout: float) -> None:
        super().__init__("odom_to_tum_ros2")
        self._f = out.open("w")
        self._n = 0
        self._last_t = time.monotonic()
        self._idle = idle_timeout
        self._prev_stamp = None
        self._max_jump = 60.0     # s; see timestamp-jump guard in _cb
        self._jump_warned = False
        self.create_subscription(Odometry, topic, self._cb, 100)
        self.create_timer(1.0, self._check_idle)
        self.get_logger().info(f"recording {topic} -> {out}")

    def _cb(self, msg: Odometry) -> None:
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        # Timestamp-jump guard (2026-08-05): when playback ends,
        # robot_localization's ekf_node keeps publishing predict-only states
        # stamped with wall-clock now(), i.e. a jump of ~1e7 s from bag time,
        # with positions extrapolated to 1e11-1e15 m. Those poses poisoned
        # every openvins_gps trajectory (coverage in millions of %). Drop any
        # pose that jumps more than --max-stamp-jump (default 60 s) past the
        # previous one instead of recording garbage.
        if self._prev_stamp is not None and t - self._prev_stamp > self._max_jump:
            if not self._jump_warned:
                self.get_logger().warning(
                    f"timestamp jump {t - self._prev_stamp:.0f}s > "
                    f"{self._max_jump}s — dropping post-playback poses")
                self._jump_warned = True
            return
        self._prev_stamp = t
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        self._f.write(f"{t:.9f} {p.x} {p.y} {p.z} {q.x} {q.y} {q.z} {q.w}\n")
        self._n += 1
        self._last_t = time.monotonic()
        if self._n % 200 == 0:
            self._f.flush()

    def _check_idle(self) -> None:
        if self._n > 0 and time.monotonic() - self._last_t > self._idle:
            self.get_logger().info(f"idle timeout - {self._n} poses written")
            self._f.flush()
            self._f.close()
            rclpy.shutdown()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", default="/odometry/filtered")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--idle-timeout", type=float, default=10.0,
                    help="exit after this many seconds with no new messages")
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)

    rclpy.init()
    node = TumRecorder(args.topic, args.out, args.idle_timeout)
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, Exception):
        pass
    finally:
        if not node._f.closed:
            node._f.flush()
            node._f.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
