#!/usr/bin/env python3
"""Replay EuRoC-layout stereo images as ROS 1 topics for OV2SLAM."""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import cv2
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from _transport_stats import write_transport_stats


def load_camera(csv_path: Path, image_dir: Path):
    frames = []
    with csv_path.open() as stream:
        for row in csv.reader(stream):
            if not row or row[0].lstrip().startswith("#"):
                continue
            try:
                timestamp_ns = int(row[0])
            except ValueError:
                continue
            frames.append((timestamp_ns, image_dir / row[1].strip()))
    return sorted(frames)


def ros_time(timestamp_ns: int) -> rospy.Time:
    return rospy.Time(
        secs=timestamp_ns // 1_000_000_000,
        nsecs=timestamp_ns % 1_000_000_000,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("seq_dir", type=Path, help="directory containing mav0/")
    parser.add_argument("--rate", type=float, default=1.0)
    parser.add_argument("--start-delay", type=float, default=2.0)
    parser.add_argument("--end-wait", type=float, default=1.0)
    parser.add_argument("--stats-out", type=Path)
    args = parser.parse_args()

    if args.rate <= 0:
        parser.error("--rate must be positive")

    mav0 = args.seq_dir / "mav0"
    cam0 = load_camera(mav0 / "cam0" / "data.csv", mav0 / "cam0" / "data")
    cam1 = load_camera(mav0 / "cam1" / "data.csv", mav0 / "cam1" / "data")
    if not cam0 or not cam1:
        print(f"[ov2slam-player] empty stereo data under {mav0}", file=sys.stderr)
        return 2

    rospy.init_node("ov2slam_data_player", anonymous=False, disable_signals=True)
    left_pub = rospy.Publisher("/cam0/image_raw", Image, queue_size=20)
    right_pub = rospy.Publisher("/cam1/image_raw", Image, queue_size=20)
    bridge = CvBridge()

    events = [(t, 0, path) for t, path in cam0]
    events.extend((t, 1, path) for t, path in cam1)
    events.sort(key=lambda event: (event[0], event[1]))

    print(
        f"[ov2slam-player] cam0={len(cam0)} cam1={len(cam1)}; "
        f"waiting {args.start_delay:.1f}s",
        flush=True,
    )
    time.sleep(args.start_delay)

    first_timestamp = events[0][0]
    start_wall = time.monotonic()
    published = [0, 0]

    for timestamp_ns, camera, image_path in events:
        if rospy.is_shutdown():
            break
        target = start_wall + (timestamp_ns - first_timestamp) * 1e-9 / args.rate
        delay = target - time.monotonic()
        if delay > 0:
            time.sleep(delay)

        image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            print(f"[ov2slam-player] failed to read {image_path}", file=sys.stderr)
            return 1

        message = bridge.cv2_to_imgmsg(image, encoding="mono8")
        message.header.stamp = ros_time(timestamp_ns)
        message.header.frame_id = f"cam{camera}"
        (left_pub if camera == 0 else right_pub).publish(message)
        published[camera] += 1

        if camera == 1 and published[1] % 200 == 0:
            print(
                f"[ov2slam-player] left={published[0]} right={published[1]}",
                flush=True,
            )

    print(
        f"[ov2slam-player] done: left={published[0]} right={published[1]}; "
        f"waiting {args.end_wait:.1f}s",
        flush=True,
    )
    time.sleep(args.end_wait)
    write_transport_stats(
        args.stats_out,
        camera_frames_expected=min(len(cam0), len(cam1)),
        camera_frames_published=min(published),
        imu_messages_published=0,
        gnss_messages_published=0,
        camera_read_failures=max(0, min(len(cam0), len(cam1)) - min(published)),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
