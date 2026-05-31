#!/usr/bin/env python3
"""ROS 1 odometry-to-TUM recorder.

Subscribes to a nav_msgs/Odometry (or geometry_msgs/PoseStamped) topic and
writes a TUM-format trajectory file:

    timestamp tx ty tz qx qy qz qw

Used by run_vins_fusion_gps.sh to capture VINS-Fusion's /globalEstimator/
global_odometry (after GPS fusion) into trajectory.txt.

Usage:
    python3 odometry_to_tum.py --topic /globalEstimator/global_odometry \
                               --out /tmp/trajectory.txt
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry


def _open(out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    f = out_path.open("w")
    return f


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--type", choices=("odom", "pose"), default="odom")
    args = ap.parse_args()

    rospy.init_node("odometry_to_tum", anonymous=True, disable_signals=True)
    f = _open(args.out)
    n = [0]  # mutable counter

    def cb_odom(msg: Odometry):
        t = msg.header.stamp.to_sec()
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        f.write(f"{t:.9f} {p.x} {p.y} {p.z} {q.x} {q.y} {q.z} {q.w}\n")
        n[0] += 1
        if n[0] % 200 == 0:
            f.flush()

    def cb_pose(msg: PoseStamped):
        t = msg.header.stamp.to_sec()
        p = msg.pose.position
        q = msg.pose.orientation
        f.write(f"{t:.9f} {p.x} {p.y} {p.z} {q.x} {q.y} {q.z} {q.w}\n")
        n[0] += 1
        if n[0] % 200 == 0:
            f.flush()

    if args.type == "odom":
        rospy.Subscriber(args.topic, Odometry, cb_odom, queue_size=200)
    else:
        rospy.Subscriber(args.topic, PoseStamped, cb_pose, queue_size=200)

    print(f"[recorder] subscribing to {args.topic} -> {args.out}", flush=True)
    try:
        rospy.spin()
    except KeyboardInterrupt:
        pass
    f.flush()
    f.close()
    print(f"[recorder] wrote {n[0]} poses to {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
