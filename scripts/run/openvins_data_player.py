#!/usr/bin/env python3
"""Replay an EuRoC-format sequence as ROS 2 topics for OpenVINS, and record
the resulting trajectory in TUM format.

Publishes:
    /cam0/image_raw  sensor_msgs/Image (mono8)
    /cam1/image_raw  sensor_msgs/Image (mono8)
    /imu0            sensor_msgs/Imu

Subscribes:
    /ov_msckf/odomimu  nav_msgs/Odometry  -> writes TUM trajectory.
    /ov_msckf/poseimu  geometry_msgs/PoseWithCovarianceStamped, the filter state after each
                       camera update (stamped camera time + online time offset)
                       -> <out_traj stem>_poseimu.txt beside it (TUM).

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
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image, Imu
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseWithCovarianceStamped
from std_msgs.msg import UInt64MultiArray
from _transport_stats import write_transport_stats
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
                 start_delay: float, end_wait: float, stats_out: Path | None):
        super().__init__("openvins_data_player")
        self.seq_dir = seq_dir
        self.out_traj = out_traj
        self.rate = rate
        self.start_delay = start_delay
        self.end_wait = end_wait
        self.stats_out = stats_out
        self.published_cam0 = 0
        self.published_cam1 = 0
        self.published_imu = 0
        end_policy = os.environ.get('OPENVINS_END_OF_STREAM_DRAIN', '0')
        if end_policy not in ('0', '1'):
            raise ValueError('Invalid end-of-recording drain policy')
        self.end_drain = end_policy == '1'
        self.end_ack = None
        self.end_ack_event = threading.Event()
        flow_policy = os.environ.get('OPENVINS_FLOW_CONTROL', '0')
        if flow_policy not in ('0', '1') or (flow_policy == '1' and not self.end_drain):
            raise ValueError('Flow control requires a valid policy and end-of-recording drain')
        self.flow_control = flow_policy == '1'
        self.progress_condition = threading.Condition()
        self.progress_ack = None
        self.progress_checkpoints = 0
        self.progress_wait_s = 0.0
        self.progress_last_imu = 0
        self.delivery = {}
        if self.end_drain:
            end_qos = QoSProfile(reliability=ReliabilityPolicy.RELIABLE,
                                 history=HistoryPolicy.KEEP_LAST, depth=1)
            self.pub_end = self.create_publisher(UInt64MultiArray, '/ov_msckf/input_end_request', end_qos)
            self.sub_end_ack = self.create_subscription(
                UInt64MultiArray, '/ov_msckf/input_end_ack', self._on_end_ack, end_qos)
        if self.flow_control:
            self.pub_progress = self.create_publisher(UInt64MultiArray, '/ov_msckf/input_progress_request', end_qos)
            self.sub_progress = self.create_subscription(
                UInt64MultiArray, '/ov_msckf/input_progress_ack', self._on_progress_ack, end_qos)

        # Publishers. OpenVINS' ROS2Visualizer uses different QoS per topic:
        #   - cameras (message_filters::Subscriber): RELIABLE, depth=10  (default)
        #   - imu  (rclcpp::SensorDataQoS()):        BEST_EFFORT, depth=5
        # The input-delivery image can request RELIABLE with a larger receive
        # buffer (run_openvins.sh sets it by default). Both sides use the
        # explicitly recorded policy; the player defaults keep the old one.
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
        self.imu_reliability = os.environ.get('OPENVINS_IMU_RELIABILITY', 'best_effort')
        if self.imu_reliability not in ('best_effort', 'reliable'):
            raise ValueError('Invalid OPENVINS_IMU_RELIABILITY')
        imu_qos = QoSProfile(
            reliability=(ReliabilityPolicy.RELIABLE if self.imu_reliability == 'reliable'
                         else ReliabilityPolicy.BEST_EFFORT),
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
        # Updated state at each processed camera frame; recorded beside the
        # IMU-rate odometry so either can be evaluated.
        self.sub_pose = self.create_subscription(
            PoseWithCovarianceStamped, "/ov_msckf/poseimu", self._on_pose, 50)

        self.bridge = CvBridge()
        self.poses: List[Tuple[float, float, float, float, float, float, float, float]] = []
        self.update_poses: List[Tuple[float, float, float, float, float, float, float, float]] = []

        # Load data.
        mav0 = seq_dir / "mav0"
        self.imu = _load_imu(mav0 / "imu0" / "data.csv")
        self.cam0 = _load_cam(mav0 / "cam0" / "data.csv", mav0 / "cam0" / "data")
        self.cam1 = _load_cam(mav0 / "cam1" / "data.csv", mav0 / "cam1" / "data")
        if not self.imu or not self.cam0 or not self.cam1:
            raise RuntimeError(f"empty data in {seq_dir} (imu={len(self.imu)} "
                               f"cam0={len(self.cam0)} cam1={len(self.cam1)})")
        if self.flow_control and [r[0] for r in self.cam0] != [r[0] for r in self.cam1]:
            raise ValueError('Flow-controlled benchmark replay requires the prepared exact stereo pairs')
        self.get_logger().info(
            f"loaded imu={len(self.imu)} cam0={len(self.cam0)} cam1={len(self.cam1)} "
            f"from {seq_dir}")

    # ------------------------------------------------------------------
    def _on_odom(self, msg: Odometry):
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        self.poses.append((t, p.x, p.y, p.z, q.x, q.y, q.z, q.w))

    def _on_pose(self, msg: PoseWithCovarianceStamped):
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        self.update_poses.append((t, p.x, p.y, p.z, q.x, q.y, q.z, q.w))

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

        # Wait for the OpenVINS node to come up and our publishers to be
        # discovered. OpenVINS uses subscription_count gates on output topics
        # and we want to be sure the ROS graph is settled.
        self.get_logger().info(f"start delay {self.start_delay:.1f}s for ROS graph...")
        time.sleep(self.start_delay)
        if self.flow_control:
            self.wait_for_input_subscribers()
            self.wait_for_input_receipt()

        t0_ns = events[0][0]
        t0_wall = time.time()
        # Preserve sensor timestamps and the nominal rate. Optional receipt
        # barriers allow wall-clock playback to slow down instead of losing input.
        audit = True
        delivery = None
        if audit:
            delivery = dict(schema=1, rate=self.rate, imu_reliability=self.imu_reliability,
                expected_imu=len(self.imu),
                expected_left=len(self.cam0), expected_right=len(self.cam1),
                subscribers_at_start=dict(imu=self.pub_imu.get_subscription_count(),
                    left=self.pub_cam0.get_subscription_count(), right=self.pub_cam1.get_subscription_count()),
                maximum_schedule_lateness_s=0.0, maximum_event_processing_s=0.0,
                camera_events_over_10ms_late=0, camera_events_over_100ms_late=0,
                start_delay_s=self.start_delay, end_wait_s=self.end_wait)
            self.delivery = delivery

        for i, (t_ns, kind, payload) in enumerate(events):
            if not rclpy.ok():
                break
            # Real-time pacing.
            target_wall = t0_wall + (t_ns - t0_ns) / 1e9 / self.rate
            now = time.time()
            if target_wall > now:
                time.sleep(target_wall - now)

            if audit:
                started = time.monotonic()
                lateness = max(0.0, time.time() - target_wall)
                delivery['maximum_schedule_lateness_s'] = max(delivery['maximum_schedule_lateness_s'], lateness)
                if kind != 'imu':
                    delivery['camera_events_over_10ms_late'] += int(lateness > 0.01)
                    delivery['camera_events_over_100ms_late'] += int(lateness > 0.1)

            if kind == "imu":
                self.pub_imu.publish(self._make_imu_msg(t_ns, *payload))
                self.published_imu += 1
            elif kind == "cam0":
                self.pub_cam0.publish(self._make_image_msg(t_ns, payload, "cam0"))
                self.published_cam0 += 1
            elif kind == "cam1":
                self.pub_cam1.publish(self._make_image_msg(t_ns, payload, "cam1"))
                self.published_cam1 += 1

            if audit:
                delivery['maximum_event_processing_s'] = max(delivery['maximum_event_processing_s'], time.monotonic()-started)

            if self.flow_control and self.published_cam0 == self.published_cam1 and (
                    kind == 'cam1' or self.published_imu - self.progress_last_imu >= 100):
                self.wait_for_input_receipt()

            if i % 5000 == 0:
                pct = 100.0 * i / len(events)
                self.get_logger().info(
                    f"played {i}/{len(events)} ({pct:.1f}%), "
                    f"poses_received={len(self.poses)}")

        self.get_logger().info(
            f"all events published; waiting {self.end_wait:.1f}s for filter flush...")
        time.sleep(self.end_wait)

        if self.end_drain:
            if self.flow_control:
                self.wait_for_input_receipt()
            self.drain_end_of_recording()
            # Keep output subscribers alive while the final camera updates arrive.
            time.sleep(self.end_wait)

    def write_delivery(self, error=None):
        import json
        delivery = dict(self.delivery)
        delivery.update(published_imu=self.published_imu, published_left=self.published_cam0,
            published_right=self.published_cam1, camera_update_outputs=len(self.update_poses),
            propagated_outputs=len(self.poses), player_error=error,
            first_update_stamp_s=self.update_poses[0][0] if self.update_poses else None,
            last_update_stamp_s=self.update_poses[-1][0] if self.update_poses else None,
            flow_control=dict(enabled=self.flow_control, completed_checkpoints=self.progress_checkpoints,
                wait_s=self.progress_wait_s, last_acknowledgement=self.progress_ack),
            estimator_received_imu=None, estimator_received_camera_pairs=None,
            limitation='Publisher counts are not estimator receipts. Exact native receipts and end acknowledgement are required. Wall-clock flow-control delays do not change sensor timestamps.')
        self.out_traj.parent.mkdir(parents=True, exist_ok=True)
        self.out_traj.with_name('openvins_delivery.json').write_text(json.dumps(delivery, indent=2)+'\n')
        expected = min(len(self.cam0), len(self.cam1))
        published = min(self.published_cam0, self.published_cam1)
        write_transport_stats(
            self.stats_out,
            camera_frames_expected=expected,
            camera_frames_published=published,
            imu_messages_published=self.published_imu,
            gnss_messages_published=0,
            camera_read_failures=max(0, expected - published),
            estimator_output_messages=len(self.poses),
        )

    def wait_for_input_subscribers(self):
        deadline = time.monotonic() + 30.0
        publishers = (self.pub_imu, self.pub_cam0, self.pub_cam1, self.pub_progress)
        while not (all(p.get_subscription_count() >= 1 for p in publishers)
                   and self.count_publishers('/ov_msckf/input_progress_ack') >= 1):
            if time.monotonic() >= deadline:
                raise RuntimeError('Native input/control subscriptions did not become ready')
            time.sleep(0.02)

    def _on_progress_ack(self, message):
        data = list(message.data)
        if len(data) != 4 or data[0] != 1 or data[2] != data[3]:
            return
        with self.progress_condition:
            self.progress_ack = data
            self.progress_condition.notify_all()

    def wait_for_input_receipt(self):
        if self.published_cam0 != self.published_cam1:
            raise RuntimeError('Cannot wait on half of a prepared stereo pair')
        expected = [1, self.published_imu, self.published_cam0, self.published_cam0]
        request = UInt64MultiArray()
        request.data = expected[:3]
        start = time.monotonic()
        while True:
            with self.progress_condition:
                if self.progress_ack == expected:
                    self.progress_checkpoints += 1
                    self.progress_wait_s += time.monotonic() - start
                    self.progress_last_imu = self.published_imu
                    return
                if time.monotonic() - start >= 30.0:
                    raise RuntimeError(f'Native input receipt stalled at {expected}; last acknowledgement {self.progress_ack}')
                self.pub_progress.publish(request)
                self.progress_condition.wait(timeout=0.02)

    # ------------------------------------------------------------------
    def _on_end_ack(self, message):
        data = list(message.data)
        if (len(data) == 7 and data[0] == 1 and data[1] == self.published_imu
                and data[2] == min(self.published_cam0, self.published_cam1)
                and data[3] == data[2] and data[4] + data[5] == data[3]
                and data[6] <= data[4]):
            self.end_ack = data
            self.end_ack_event.set()

    def drain_end_of_recording(self):
        import json
        request = UInt64MultiArray()
        request.data = [1, self.published_imu, min(self.published_cam0, self.published_cam1)]
        deadline = time.monotonic() + 30.0
        while not self.end_ack_event.is_set():
            if time.monotonic() >= deadline:
                raise RuntimeError('Native end-of-recording acknowledgement missing; do not qualify this delivery')
            self.pub_end.publish(request)
            self.end_ack_event.wait(0.2)
        self.out_traj.parent.mkdir(parents=True, exist_ok=True)
        self.out_traj.with_name('openvins_end_ack.json').write_text(
            json.dumps(dict(schema=1, request=list(request.data), acknowledgement=self.end_ack), indent=2)+'\n')
        self.get_logger().info(f'native end-of-recording acknowledged: {self.end_ack}')

    def write_trajectory(self):
        self.out_traj.parent.mkdir(parents=True, exist_ok=True)
        with self.out_traj.open("w") as f:
            for row in self.poses:
                f.write("{:.9f} {:.9f} {:.9f} {:.9f} {:.9f} {:.9f} {:.9f} {:.9f}\n".format(*row))
        self.get_logger().info(
            f"wrote {len(self.poses)} poses to {self.out_traj}")
        updates = self.out_traj.with_name(self.out_traj.stem + "_poseimu" + self.out_traj.suffix)
        with updates.open("w") as f:
            for row in self.update_poses:
                f.write("{:.9f} {:.9f} {:.9f} {:.9f} {:.9f} {:.9f} {:.9f} {:.9f}\n".format(*row))
        self.get_logger().info(
            f"wrote {len(self.update_poses)} updated poses to {updates}")


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
    p.add_argument("--stats-out", type=Path)
    args = p.parse_args()

    if not (args.seq_dir / "mav0").is_dir():
        print(f"ERROR: {args.seq_dir}/mav0 not found", file=sys.stderr)
        sys.exit(2)

    rclpy.init()
    node = Player(
        args.seq_dir, args.out_traj, args.rate, args.start_delay, args.end_wait,
        args.stats_out,
    )
    # Own the executor explicitly. rclpy.spin(node) creates a hidden executor;
    # destroying the node while its daemon thread is still in spin() aborts
    # ROS 2 Humble after the trajectory has already been written.
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    spin_thread = threading.Thread(
        target=executor.spin,
        name="openvins-data-player-executor",
        daemon=False,
    )
    spin_thread.start()
    error = None
    try:
        node.play()
    except BaseException as exc:
        error = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        executor.shutdown(timeout_sec=5.0)
        spin_thread.join(timeout=5.0)
        if spin_thread.is_alive():
            node.get_logger().error("ROS executor did not stop cleanly")
        # Preserve partial receipts and poses on a delivery exception as well as
        # on success. The original nonzero exit still disqualifies the attempt.
        node.write_trajectory()
        node.write_delivery(error)
        executor.remove_node(node)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
