#!/usr/bin/env python3
"""Derive reproducible IMU priors from the benchmark recordings.

The script deliberately does not read estimated or ground-truth trajectories.
It reports stationary gyro bias, stationary white-noise density, and a robust
95th-percentile one-second operational noise envelope. The latter is used as
the effective measurement density for field recordings with platform vibration.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sqlite3
import statistics
from pathlib import Path


SEQUENCES = {
    "rosariov2": [
        ("sequence1", 0.0, 5.0),
        ("sequence5", 0.0, 10.0),
    ],
    "hortimulti": [
        ("strawberry02", 0.0, 2.0),
        ("strawberry03", 0.0, 0.75),
    ],
    # The field recording starts in motion. Its stationary bias is supplied by
    # the separate same-camera steering-test bag in main().
    "zed2i": [
        ("field1_110426_full_10fps_q90", 0.0, 30.0),
    ],
}

ZED_IMU_TOPIC = "/zed/zed_node/imu/data_raw"
ZED_EXPECTED_SERIAL = b"30291010"

# Published Allan-deviation random walks from each dataset's sensor
# calibration. The recordings' short stationary heads cannot identify these.
BIAS_RANDOM_WALK = {
    "rosariov2": {"sigma_gw_c": 1.823e-6, "sigma_aw_c": 4.750e-5},
    "hortimulti": {"sigma_gw_c": 3.22094e-5, "sigma_aw_c": 4.584471e-5},
    # ZED SDK reports gyro quantities in degrees. Convert the factory gyro
    # random walk (0.0424 deg/s^2/sqrt(Hz)) to radians for the estimators.
    "zed2i": {"sigma_gw_c": math.radians(0.0424), "sigma_aw_c": 0.0202},
}


def median_abs_deviation(values: list[float]) -> float:
    center = statistics.median(values)
    return statistics.median(abs(value - center) for value in values)


def robust_density(rows: list[list[float]], fs: float, offset: int) -> list[float]:
    result = []
    for axis in range(offset, offset + 3):
        differences = [b[axis] - a[axis] for a, b in zip(rows, rows[1:])]
        robust_std = 1.4826 * median_abs_deviation(differences)
        result.append(robust_std / math.sqrt(2.0 * fs))
    return result


def quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def load_imu(path: Path) -> tuple[list[int], list[list[float]]]:
    timestamps, samples = [], []
    with path.open(newline="") as stream:
        reader = csv.reader(line for line in stream if not line.startswith("#"))
        for row in reader:
            timestamps.append(int(row[0]))
            samples.append([float(value) for value in row[1:7]])
    if len(samples) < 3:
        raise ValueError(f"too few IMU samples in {path}")
    return timestamps, samples


def load_ros2_imu(bag_dir: Path) -> tuple[list[int], list[list[float]]]:
    """Load ZED raw IMU samples from a ROS 2 SQLite bag.

    ROS Humble's Python bindings require the system Python on Ubuntu 22.04;
    invoke this script with /usr/bin/python3 after sourcing Humble.
    """
    try:
        from rclpy.serialization import deserialize_message
        from sensor_msgs.msg import Imu
    except ImportError as error:
        raise RuntimeError(
            "ROS 2 Python bindings are required for the ZED calibration bag; "
            "source /opt/ros/humble/setup.bash and use /usr/bin/python3"
        ) from error

    db_files = sorted(bag_dir.glob("*.db3"))
    if len(db_files) != 1:
        raise ValueError(f"expected one db3 file in {bag_dir}, found {len(db_files)}")
    database = sqlite3.connect(f"file:{db_files[0]}?mode=ro", uri=True)
    topic_row = database.execute(
        "SELECT id FROM topics WHERE name = ?", (ZED_IMU_TOPIC,)
    ).fetchone()
    if topic_row is None:
        raise ValueError(f"{ZED_IMU_TOPIC} not found in {bag_dir}")

    # Refuse a different camera when diagnostic records are available.
    diagnostic_row = database.execute(
        "SELECT id FROM topics WHERE name = '/diagnostics'"
    ).fetchone()
    if diagnostic_row is not None:
        serial_found = any(
            ZED_EXPECTED_SERIAL in data
            for (data,) in database.execute(
                "SELECT data FROM messages WHERE topic_id = ?", diagnostic_row
            )
        )
        if not serial_found:
            raise ValueError(
                f"calibration bag does not identify ZED S/N "
                f"{ZED_EXPECTED_SERIAL.decode()}"
            )

    timestamps, samples = [], []
    for (data,) in database.execute(
        "SELECT data FROM messages WHERE topic_id = ? ORDER BY timestamp", topic_row
    ):
        message = deserialize_message(data, Imu)
        timestamps.append(
            int(message.header.stamp.sec) * 1_000_000_000
            + int(message.header.stamp.nanosec)
        )
        samples.append([
            message.angular_velocity.x,
            message.angular_velocity.y,
            message.angular_velocity.z,
            message.linear_acceleration.x,
            message.linear_acceleration.y,
            message.linear_acceleration.z,
        ])
    database.close()
    if len(samples) < 3:
        raise ValueError(f"too few ZED IMU samples in {bag_dir}")
    return timestamps, samples


def round_up(value: float, quantum: float) -> float:
    return math.ceil(value / quantum - 1e-12) * quantum


def analyse(
    path: Path,
    stationary_start_seconds: float,
    stationary_seconds: float,
    stationary_recording: tuple[Path, list[int], list[list[float]]] | None = None,
) -> dict:
    timestamps, samples = load_imu(path)
    periods = [(b - a) * 1e-9 for a, b in zip(timestamps, timestamps[1:])]
    fs = 1.0 / statistics.median(periods)

    if stationary_recording is None:
        stationary_path = path
        stationary_timestamps, stationary_samples = timestamps, samples
    else:
        stationary_path, stationary_timestamps, stationary_samples = stationary_recording
    stationary_periods = [
        (b - a) * 1e-9
        for a, b in zip(stationary_timestamps, stationary_timestamps[1:])
    ]
    stationary_fs = 1.0 / statistics.median(stationary_periods)
    start_ns = stationary_timestamps[0] + round(stationary_start_seconds * 1e9)
    end_ns = start_ns + round(stationary_seconds * 1e9)
    stationary = [
        sample
        for timestamp, sample in zip(stationary_timestamps, stationary_samples)
        if start_ns <= timestamp < end_ns
    ]
    if len(stationary) < 3:
        raise ValueError(
            f"stationary interval {stationary_start_seconds}+{stationary_seconds}s "
            f"has too few samples in {stationary_path}"
        )
    gyro_bias = [statistics.mean(row[axis] for row in stationary) for axis in range(3)]

    window_size = max(3, round(fs))
    window_densities = []
    for start in range(0, len(samples) - window_size + 1, window_size):
        window = samples[start : start + window_size]
        window_densities.append({
            "gyro": robust_density(window, fs, 0),
            "accel": robust_density(window, fs, 3),
        })

    operational_q95 = {
        sensor: [
            quantile([window[sensor][axis] for window in window_densities], 0.95)
            for axis in range(3)
        ]
        for sensor in ("gyro", "accel")
    }
    return {
        "path": str(path),
        "sample_rate_hz": fs,
        "stationary_path": str(stationary_path),
        "stationary_sample_rate_hz": stationary_fs,
        "stationary_start_seconds": stationary_start_seconds,
        "stationary_seconds": stationary_seconds,
        "stationary_samples": len(stationary),
        "gyro_bias_rad_s": gyro_bias,
        "stationary_density": {
            "gyro_rad_s_sqrt_hz": robust_density(stationary, stationary_fs, 0),
            "accel_m_s2_sqrt_hz": robust_density(stationary, stationary_fs, 3),
        },
        "operational_density_q95": {
            "gyro_rad_s_sqrt_hz": operational_q95["gyro"],
            "accel_m_s2_sqrt_hz": operational_q95["accel"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--zed-stationary-bag",
        type=Path,
        help="ROS 2 bag from the same ZED containing a stationary first 30 s",
    )
    args = parser.parse_args()

    zed_bag = args.zed_stationary_bag or args.workspace.parent / "steering-test1-light"
    zed_timestamps, zed_samples = load_ros2_imu(zed_bag)
    zed_stationary = (zed_bag, zed_timestamps, zed_samples)

    report = {"method": "1 s robust first-difference density, q95 envelope", "datasets": {}}
    for dataset, sequence_specs in SEQUENCES.items():
        sequences = {}
        for sequence, stationary_start_seconds, stationary_seconds in sequence_specs:
            path = args.workspace / "datasets" / dataset / sequence / "mav0/imu0/data.csv"
            sequences[sequence] = analyse(
                path,
                stationary_start_seconds,
                stationary_seconds,
                zed_stationary if dataset == "zed2i" else None,
            )

        gyro_max = max(
            max(result["operational_density_q95"]["gyro_rad_s_sqrt_hz"])
            for result in sequences.values()
        )
        accel_max = max(
            max(result["operational_density_q95"]["accel_m_s2_sqrt_hz"])
            for result in sequences.values()
        )
        report["datasets"][dataset] = {
            "sequences": sequences,
            "recommended": {
                "sigma_g_c": round_up(gyro_max, 0.0005),
                "sigma_a_c": round_up(accel_max, 0.01),
                **BIAS_RANDOM_WALK[dataset],
            },
        }

    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
