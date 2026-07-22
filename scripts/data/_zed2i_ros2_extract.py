#!/usr/bin/env python3
"""Extract a ZED 2i ROS 2 MCAP + matching RTK ROS 2 bag for benchmarking.

Output layout:
  <out>/mav0/cam0/data/<ns_stamp>.<format>
  <out>/mav0/cam1/data/<ns_stamp>.<format>
  <out>/cam0, cam1, left, right symlinks
  <out>/times.txt
  <out>/imu.csv
  <out>/gps.csv
  <out>/gt_tum.txt
  <out>/manifest.json

The ZED topics are already rectified. JPEG export writes the original
CompressedImage JPEG payload directly, avoiding an extra generation loss.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import shutil
import sys
from bisect import bisect_left
from pathlib import Path

import rosbag2_py
import yaml
from PIL import Image
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import CameraInfo, CompressedImage, Imu, NavSatFix


LEFT_TOPIC = "/zed/zed_node/left/color/rect/image/compressed"
RIGHT_TOPIC = "/zed/zed_node/right/color/rect/image/compressed"
LEFT_INFO_TOPIC = "/zed/zed_node/left/color/rect/camera_info"
RIGHT_INFO_TOPIC = "/zed/zed_node/right/color/rect/camera_info"
IMU_TOPIC = "/zed/zed_node/imu/data_raw"
GPS_MOVING_TOPIC = "/gps/fix"
GPS_ROVER_TOPIC = "/ublox_rover/fix"


def load_metadata(bag_dir: Path) -> dict:
    meta = bag_dir / "metadata.yaml"
    if not meta.exists():
        raise FileNotFoundError(f"metadata.yaml not found in {bag_dir}")
    return yaml.safe_load(meta.read_text())["rosbag2_bagfile_information"]


def open_reader(bag_dir: Path) -> rosbag2_py.SequentialReader:
    info = load_metadata(bag_dir)
    reader = rosbag2_py.SequentialReader()
    reader.open(
        rosbag2_py.StorageOptions(uri=str(bag_dir), storage_id=info["storage_identifier"]),
        rosbag2_py.ConverterOptions("", ""),
    )
    return reader


def stamp_ns(msg) -> int:
    return int(msg.header.stamp.sec) * 1_000_000_000 + int(msg.header.stamp.nanosec)


def make_symlink(target: Path, link: Path) -> None:
    if link.exists() or link.is_symlink():
        return
    link.symlink_to(target)


def ensure_out(out: Path, overwrite: bool) -> None:
    if out.exists() and overwrite:
        shutil.rmtree(out)
    if out.exists() and any(out.iterdir()):
        raise RuntimeError(f"output exists and is not empty: {out}")
    (out / "mav0" / "cam0" / "data").mkdir(parents=True, exist_ok=True)
    (out / "mav0" / "cam1" / "data").mkdir(parents=True, exist_ok=True)


def write_image(payload: bytes, path: Path, fmt: str, jpeg_quality: int, recompress_jpeg: bool) -> None:
    if fmt == "jpg" and not recompress_jpeg:
        path.write_bytes(payload)
        return
    img = Image.open(io.BytesIO(payload)).convert("RGB")
    if fmt == "jpg":
        img.save(path, format="JPEG", quality=jpeg_quality)
    else:
        img.save(path, format="PNG", compress_level=1)


def extract_stereo(
    zed_bag: Path,
    out: Path,
    max_frames: int,
    target_fps: float,
    image_format: str,
    jpeg_quality: int,
    recompress_jpeg: bool,
) -> tuple[list[int], dict]:
    cam0 = out / "mav0" / "cam0" / "data"
    cam1 = out / "mav0" / "cam1" / "data"
    ext = "jpg" if image_format == "jpg" else "png"
    left_pending: dict[int, bytes] = {}
    right_pending: dict[int, bytes] = {}
    matched: list[int] = []
    camera_info: dict[str, dict] = {}
    min_period_ns = int(round(1_000_000_000 / target_fps)) if target_fps > 0 else 0
    next_accept_ns: int | None = None

    reader = open_reader(zed_bag)
    while reader.has_next():
        topic, raw, _ts = reader.read_next()

        if topic == LEFT_INFO_TOPIC and "left" not in camera_info:
            msg = deserialize_message(raw, CameraInfo)
            camera_info["left"] = camera_info_to_dict(msg)
            continue
        if topic == RIGHT_INFO_TOPIC and "right" not in camera_info:
            msg = deserialize_message(raw, CameraInfo)
            camera_info["right"] = camera_info_to_dict(msg)
            continue

        if topic not in (LEFT_TOPIC, RIGHT_TOPIC):
            continue

        msg = deserialize_message(raw, CompressedImage)
        ns = stamp_ns(msg)
        payload = bytes(msg.data)
        if topic == LEFT_TOPIC:
            left_pending[ns] = payload
        else:
            right_pending[ns] = payload

        if ns in left_pending and ns in right_pending:
            if min_period_ns:
                if next_accept_ns is None:
                    next_accept_ns = ns
                if ns < next_accept_ns:
                    left_pending.pop(ns)
                    right_pending.pop(ns)
                    continue
                while next_accept_ns <= ns:
                    next_accept_ns += min_period_ns

            out_left = cam0 / f"{ns}.{ext}"
            out_right = cam1 / f"{ns}.{ext}"
            write_image(left_pending.pop(ns), out_left, image_format, jpeg_quality, recompress_jpeg)
            write_image(right_pending.pop(ns), out_right, image_format, jpeg_quality, recompress_jpeg)
            matched.append(ns)
            if len(matched) % 500 == 0:
                print(f"[zed2i] extracted {len(matched)} stereo pairs", flush=True)
            if max_frames and len(matched) >= max_frames:
                break

    (out / "times.txt").write_text("".join(f"{ns}\n" for ns in matched))
    return matched, camera_info


def camera_info_to_dict(msg: CameraInfo) -> dict:
    return {
        "width": int(msg.width),
        "height": int(msg.height),
        "distortion_model": msg.distortion_model,
        "frame_id": msg.header.frame_id,
        "k": [float(x) for x in msg.k],
        "d": [float(x) for x in msg.d],
        "r": [float(x) for x in msg.r],
        "p": [float(x) for x in msg.p],
    }


def extract_imu(zed_bag: Path, out: Path, start_ns: int, end_ns: int) -> int:
    rows = []
    reader = open_reader(zed_bag)
    while reader.has_next():
        topic, raw, _ts = reader.read_next()
        if topic != IMU_TOPIC:
            continue
        msg = deserialize_message(raw, Imu)
        ns = stamp_ns(msg)
        if ns < start_ns:
            continue
        if ns > end_ns:
            break
        rows.append([
            ns / 1e9,
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z,
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z,
        ])
    with (out / "imu.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "ax", "ay", "az", "gx", "gy", "gz"])
        w.writerows(rows)
    return len(rows)


def wgs84_to_ecef(lat_deg: float, lon_deg: float, alt: float) -> tuple[float, float, float]:
    a = 6378137.0
    e2 = 6.69437999014e-3
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    sin_lat = math.sin(lat)
    cos_lat = math.cos(lat)
    n = a / math.sqrt(1.0 - e2 * sin_lat * sin_lat)
    x = (n + alt) * cos_lat * math.cos(lon)
    y = (n + alt) * cos_lat * math.sin(lon)
    z = (n * (1.0 - e2) + alt) * sin_lat
    return x, y, z


def ecef_to_enu(
    xyz: tuple[float, float, float],
    origin_xyz: tuple[float, float, float],
    origin_lat_deg: float,
    origin_lon_deg: float,
) -> tuple[float, float, float]:
    dx = xyz[0] - origin_xyz[0]
    dy = xyz[1] - origin_xyz[1]
    dz = xyz[2] - origin_xyz[2]
    lat = math.radians(origin_lat_deg)
    lon = math.radians(origin_lon_deg)
    sin_lat, cos_lat = math.sin(lat), math.cos(lat)
    sin_lon, cos_lon = math.sin(lon), math.cos(lon)
    east = -sin_lon * dx + cos_lon * dy
    north = -sin_lat * cos_lon * dx - sin_lat * sin_lon * dy + cos_lat * dz
    up = cos_lat * cos_lon * dx + cos_lat * sin_lon * dy + sin_lat * dz
    return east, north, up


def nearest_by_time(rows: list[tuple[int, NavSatFix]], query_ns: int, max_dt_ns: int):
    if not rows:
        return None
    stamps = [r[0] for r in rows]
    idx = bisect_left(stamps, query_ns)
    cand = []
    if idx < len(rows):
        cand.append(rows[idx])
    if idx > 0:
        cand.append(rows[idx - 1])
    if not cand:
        return None
    best = min(cand, key=lambda x: abs(x[0] - query_ns))
    if abs(best[0] - query_ns) > max_dt_ns:
        return None
    return best


def extract_gps_gt(
    rtk_bag: Path,
    out: Path,
    start_ns: int,
    end_ns: int,
    lever_x_m: float,
    lever_z_m: float,
) -> dict:
    moving: list[tuple[int, NavSatFix]] = []
    rover: list[tuple[int, NavSatFix]] = []
    reader = open_reader(rtk_bag)
    while reader.has_next():
        topic, raw, _ts = reader.read_next()
        if topic not in (GPS_MOVING_TOPIC, GPS_ROVER_TOPIC):
            continue
        msg = deserialize_message(raw, NavSatFix)
        ns = stamp_ns(msg)
        if ns < start_ns:
            continue
        if ns > end_ns:
            # Bags are time-ordered enough for this to be useful.
            if topic == GPS_MOVING_TOPIC:
                break
            continue
        if topic == GPS_MOVING_TOPIC:
            moving.append((ns, msg))
        else:
            rover.append((ns, msg))

    if not moving:
        raise RuntimeError("no /gps/fix messages found in overlap")

    lat0, lon0, alt0 = moving[0][1].latitude, moving[0][1].longitude, moving[0][1].altitude
    origin = wgs84_to_ecef(lat0, lon0, alt0)

    moving_enu = []
    rover_enu = []
    for ns, msg in moving:
        enu = ecef_to_enu(wgs84_to_ecef(msg.latitude, msg.longitude, msg.altitude), origin, lat0, lon0)
        moving_enu.append((ns, msg, enu))
    for ns, msg in rover:
        enu = ecef_to_enu(wgs84_to_ecef(msg.latitude, msg.longitude, msg.altitude), origin, lat0, lon0)
        rover_enu.append((ns, msg, enu))

    rover_lookup = [(ns, enu) for ns, _msg, enu in rover_enu]
    gt_rows = []
    gps_rows = []
    used_heading = 0
    for ns, msg, base_enu in moving_enu:
        gps_rows.append([ns / 1e9, msg.latitude, msg.longitude, msg.altitude, msg.status.status])
        rv = nearest_by_time(rover_lookup, ns, 250_000_000)
        if rv is None:
            heading = None
        else:
            _rns, renu = rv
            dx = renu[0] - base_enu[0]
            dy = renu[1] - base_enu[1]
            norm = math.hypot(dx, dy)
            heading = (dx / norm, dy / norm) if norm > 0.2 else None
        if heading is None:
            cam_e, cam_n = base_enu[0], base_enu[1]
        else:
            used_heading += 1
            cam_e = base_enu[0] + lever_x_m * heading[0]
            cam_n = base_enu[1] + lever_x_m * heading[1]
        cam_u = base_enu[2] + lever_z_m
        gt_rows.append([ns / 1e9, cam_e, cam_n, cam_u, 0.0, 0.0, 0.0, 1.0])

    with (out / "gps.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "lat", "lon", "alt", "status"])
        w.writerows(gps_rows)
    with (out / "gt_tum.txt").open("w") as f:
        for row in gt_rows:
            f.write(
                f"{row[0]:.9f} {row[1]:.9f} {row[2]:.9f} {row[3]:.9f} "
                f"{row[4]:.9f} {row[5]:.9f} {row[6]:.9f} {row[7]:.9f}\n"
            )
    return {
        "gps_rows": len(gps_rows),
        "gt_rows": len(gt_rows),
        "heading_rows": used_heading,
        "origin_lat_lon_alt": [lat0, lon0, alt0],
        "lever_x_m": lever_x_m,
        "lever_z_m": lever_z_m,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zed_bag", required=True)
    ap.add_argument("--rtk_bag", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max_frames", type=int, default=5000)
    ap.add_argument("--target_fps", type=float, default=0.0, help="downsample stereo pairs by timestamp; 0 keeps every pair")
    ap.add_argument("--image_format", choices=["jpg", "png"], default="jpg")
    ap.add_argument("--jpeg_quality", type=int, default=95)
    ap.add_argument("--recompress_jpeg", action="store_true", help="decode and re-encode JPEG instead of copying original CompressedImage payload")
    ap.add_argument("--gps_to_camera_x", type=float, default=1.86)
    ap.add_argument("--gps_to_camera_z", type=float, default=0.0)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    zed_bag = Path(args.zed_bag).expanduser().resolve()
    rtk_bag = Path(args.rtk_bag).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    ensure_out(out, args.overwrite)

    print(f"[zed2i] output: {out}")
    matched, camera_info = extract_stereo(
        zed_bag, out, args.max_frames, args.target_fps, args.image_format, args.jpeg_quality, args.recompress_jpeg
    )
    if not matched:
        raise RuntimeError("no stereo pairs extracted")
    start_ns, end_ns = matched[0], matched[-1]
    print(f"[zed2i] image window: {start_ns} -> {end_ns}")

    imu_count = extract_imu(zed_bag, out, start_ns, end_ns)
    print(f"[zed2i] imu rows: {imu_count}")

    gps_summary = extract_gps_gt(
        rtk_bag, out, start_ns, end_ns, args.gps_to_camera_x, args.gps_to_camera_z
    )
    print(f"[zed2i] gps rows: {gps_summary['gps_rows']}")

    for name, target in [
        ("cam0", Path("mav0/cam0/data")),
        ("cam1", Path("mav0/cam1/data")),
        ("left", Path("mav0/cam0/data")),
        ("right", Path("mav0/cam1/data")),
    ]:
        make_symlink(target, out / name)

    manifest = {
        "dataset": out.name,
        "zed_bag": str(zed_bag),
        "rtk_bag": str(rtk_bag),
        "image_format": args.image_format,
        "jpeg_quality": args.jpeg_quality if args.image_format == "jpg" else None,
        "recompress_jpeg": bool(args.recompress_jpeg) if args.image_format == "jpg" else None,
        "target_fps": args.target_fps if args.target_fps > 0 else None,
        "stereo_pairs": len(matched),
        "start_ns": start_ns,
        "end_ns": end_ns,
        "duration_s": (end_ns - start_ns) / 1e9,
        "topics": {
            "left": LEFT_TOPIC,
            "right": RIGHT_TOPIC,
            "imu": IMU_TOPIC,
            "gps_moving_base": GPS_MOVING_TOPIC,
            "gps_rover_heading": GPS_ROVER_TOPIC,
        },
        "camera_info": camera_info,
        "gps_gt": gps_summary,
        "notes": [
            "gt_tum.txt is RTK moving-base GPS shifted horizontally by gps_to_camera_x using rover/moving-base heading.",
            "gt_tum.txt orientation is identity; use position metrics for validation.",
            "gps_to_camera_z is relative antenna-to-camera height, not camera height from ground.",
        ],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"[zed2i] done: {len(matched)} stereo pairs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
