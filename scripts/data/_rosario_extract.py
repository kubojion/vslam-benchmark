#!/usr/bin/env python3
"""Extract images, IMU, GPS, and GT from a Rosario v2 ROS1 bag using `rosbags`.

Image layout produced is EuRoC-compatible so that ORB-SLAM3's stereo_euroc
binary can read it directly:
  <out>/mav0/cam0/data/<nanosec_stamp>.png   (left / infra1)
  <out>/mav0/cam1/data/<nanosec_stamp>.png   (right / infra2)
  <out>/times.txt                            (one nanosecond stamp per line)

Convenience symlinks are also created:
  <out>/cam0  ->  mav0/cam0/data
  <out>/cam1  ->  mav0/cam1/data

Ground truth comes from a *separate* PGT bag (--gt_bag / --gt topic).
GPS from reach_1/fix is projected to local ENU and saved as TUM fallback.

Requires: pip install rosbags pyproj numpy opencv-python
"""
import argparse, csv, sys
from pathlib import Path
import numpy as np

try:
    from rosbags.rosbag1 import Reader
    from rosbags.typesys import Stores, get_typestore
except ImportError:
    sys.exit("pip install rosbags  (also: pyproj numpy opencv-python)")

import cv2

TYPESTORE = None  # initialised once in main()


def msg_to_image(msg):
    """ROS sensor_msgs/Image -> numpy array (grayscale or BGR)."""
    h, w = msg.height, msg.width
    enc = msg.encoding
    buf = np.frombuffer(msg.data, dtype=np.uint8).reshape(h, msg.step)
    if enc == "mono8":
        return buf[:, :w].copy()
    if enc in ("rgb8", "bgr8"):
        img = buf[:, :w * 3].reshape(h, w, 3).copy()
        if enc == "rgb8":
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img
    if enc in ("mono16", "16UC1"):
        return np.frombuffer(msg.data, dtype=np.uint16).reshape(h, w).copy()
    if enc == "bayer_rggb8":
        return cv2.cvtColor(buf[:, :w].copy(), cv2.COLOR_BAYER_RG2BGR)
    raise RuntimeError(f"unsupported encoding {enc!r}")


def header_stamp_ns(msg):
    """Return header timestamp as integer nanoseconds."""
    s = msg.header.stamp
    return int(s.sec) * 1_000_000_000 + int(s.nanosec)


def gps_to_enu(lats, lons, alts):
    from pyproj import Transformer, CRS
    lat0, lon0, alt0 = lats[0], lons[0], alts[0]
    crs_geo = CRS.from_epsg(4326)
    crs_enu = CRS.from_proj4(
        f"+proj=tmerc +lat_0={lat0} +lon_0={lon0} +k=1 +x_0=0 +y_0=0 +ellps=WGS84"
    )
    tr = Transformer.from_crs(crs_geo, crs_enu, always_xy=True)
    xs, ys = tr.transform(lons, lats)
    zs = np.array(alts) - alt0
    return np.array(xs), np.array(ys), zs


def stream_images_to_disk(bag_path, left_topic, right_topic, imu_topic,
                          gps_topic, max_frames, cam0_dir, cam1_dir):
    """Stream images directly to disk (no in-memory buffering).

    Each frame is decoded and written to cam0_dir / cam1_dir immediately,
    so peak memory is just one frame at a time instead of the whole sequence.
    Returns (left_stamps, right_stamps, imu_rows, gps_rows) — stamp lists
    are plain Python lists of ints (~110 KB for a full sequence).
    """
    left_stamps, right_stamps, imu_rows, gps_rows = [], [], [], []

    with Reader(bag_path) as r:
        topics_in_bag = {c.topic for c in r.connections}
        for t in [left_topic, right_topic]:
            if t not in topics_in_bag:
                print(f"[warn] topic {t!r} not found in bag")

        for c, _t_ns, raw in r.messages():
            tp = c.topic
            if tp == left_topic:
                msg = TYPESTORE.deserialize_ros1(raw, c.msgtype)
                ns = header_stamp_ns(msg)
                cv2.imwrite(str(cam0_dir / f"{ns}.png"), msg_to_image(msg))
                left_stamps.append(ns)
                if len(left_stamps) % 500 == 0:
                    print(f"  [extract] {len(left_stamps)} left frames...",
                          flush=True)
                if max_frames and len(left_stamps) >= max_frames:
                    break
            elif tp == right_topic:
                msg = TYPESTORE.deserialize_ros1(raw, c.msgtype)
                ns = header_stamp_ns(msg)
                cv2.imwrite(str(cam1_dir / f"{ns}.png"), msg_to_image(msg))
                right_stamps.append(ns)
            elif tp == imu_topic:
                msg = TYPESTORE.deserialize_ros1(raw, c.msgtype)
                t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
                imu_rows.append([t,
                    msg.linear_acceleration.x, msg.linear_acceleration.y,
                    msg.linear_acceleration.z,
                    msg.angular_velocity.x, msg.angular_velocity.y,
                    msg.angular_velocity.z])
            elif tp == gps_topic:
                msg = TYPESTORE.deserialize_ros1(raw, c.msgtype)
                t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
                gps_rows.append([t, msg.latitude, msg.longitude, msg.altitude])

    return left_stamps, right_stamps, imu_rows, gps_rows


def read_gt_from_bag(gt_bag_path, gt_topic):
    """Read GT poses from a separate PGT bag."""
    gt_rows = []
    with Reader(gt_bag_path) as r:
        topics_in_bag = {c.topic for c in r.connections}
        if gt_topic not in topics_in_bag:
            print(f"[warn] GT topic {gt_topic!r} not found in {gt_bag_path}")
            return gt_rows
        for c, _t_ns, raw in r.messages():
            if c.topic != gt_topic:
                continue
            msg = TYPESTORE.deserialize_ros1(raw, c.msgtype)
            t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            # PoseWithCovarianceStamped -> .pose.pose; PoseStamped -> .pose
            p = msg.pose.pose if hasattr(msg.pose, "pose") else msg.pose
            gt_rows.append([t,
                p.position.x,    p.position.y,    p.position.z,
                p.orientation.x, p.orientation.y, p.orientation.z,
                p.orientation.w])
    return gt_rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bag",    required=True, help="Main sensor bag")
    ap.add_argument("--out",    required=True, help="Output directory")
    # Rosario v2 defaults (RealSense D435i stereo IR)
    ap.add_argument("--left",   default="/realsense/infra1/image_rect_raw")
    ap.add_argument("--right",  default="/realsense/infra2/image_rect_raw")
    ap.add_argument("--imu",    default="/realsense/imu")
    ap.add_argument("--gps",    default="/reach_1/fix")
    # Separate PGT bag for ground truth
    ap.add_argument("--gt_bag", default="", help="PGT bag path (leave empty to derive GT from GPS)")
    ap.add_argument("--gt",     default="/mins/imu/pose",
                    help="GT topic inside --gt_bag")
    # Quick test mode: extract only the first N left frames
    ap.add_argument("--max_frames", type=int, default=0,
                    help="Stop after N left frames (0=all). Use 300-500 for a quick smoke-test.")
    args = ap.parse_args()

    global TYPESTORE
    TYPESTORE = get_typestore(Stores.ROS1_NOETIC)

    out = Path(args.out)

    # EuRoC-compatible image directories (required by stereo_euroc binary)
    cam0_dir = out / "mav0" / "cam0" / "data"
    cam1_dir = out / "mav0" / "cam1" / "data"
    cam0_dir.mkdir(parents=True, exist_ok=True)
    cam1_dir.mkdir(parents=True, exist_ok=True)

    # Convenience symlinks: cam0 -> mav0/cam0/data  (used by other scripts)
    for link_name, target in [("cam0", Path("mav0/cam0/data")),
                               ("cam1", Path("mav0/cam1/data"))]:
        link = out / link_name
        if not link.exists() and not link.is_symlink():
            link.symlink_to(target)

    # ── Stream main bag: write images to disk immediately ────────────────────
    # Frames are written one-at-a-time so peak RAM is a single decoded image
    # (~900 KB) instead of the entire sequence (~25 GB for 13 k frames).
    print(f"[extract] reading {args.bag}")
    print(f"          left={args.left}")
    print(f"          right={args.right}")
    left_stamps, right_stamps, imu_rows, gps_rows = stream_images_to_disk(
        args.bag, args.left, args.right, args.imu, args.gps, args.max_frames,
        cam0_dir, cam1_dir)
    print(f"[extract] got {len(left_stamps)} left, {len(right_stamps)} right frames")

    # ── Pair timestamps only (images already on disk) ────────────────────────
    rights_ns = np.array(right_stamps, dtype=np.int64) \
                if right_stamps else np.array([], dtype=np.int64)
    MATCH_THRESH_NS = 50_000_000  # 50 ms
    matched_stamps = []
    for ns in left_stamps:
        if rights_ns.size == 0:
            matched_stamps.append(ns)
            continue
        j = int(np.argmin(np.abs(rights_ns - ns)))
        if abs(int(rights_ns[j]) - ns) <= MATCH_THRESH_NS:
            matched_stamps.append(ns)

    # ── Write times.txt (only matched left timestamps) ────────────────────────
    with open(out / "times.txt", "w") as f:
        for ns in matched_stamps:
            f.write(f"{ns}\n")
    print(f"[ok] {len(matched_stamps)} stereo pairs -> mav0/cam0/data + mav0/cam1/data")

    # ── IMU ───────────────────────────────────────────────────────────────────
    if imu_rows:
        with open(out / "imu.csv", "w") as f:
            f.write("t,ax,ay,az,gx,gy,gz\n")
            csv.writer(f).writerows(imu_rows)
        print(f"[ok] imu.csv  ({len(imu_rows)} rows)")

    # ── GPS ───────────────────────────────────────────────────────────────────
    if gps_rows:
        with open(out / "gps.csv", "w") as f:
            f.write("t,lat,lon,alt\n")
            csv.writer(f).writerows(gps_rows)
        print(f"[ok] gps.csv  ({len(gps_rows)} rows)")

    # ── Ground truth (PGT bag preferred, GPS ENU as fallback) ────────────────
    gt_rows = []
    if args.gt_bag and Path(args.gt_bag).is_file():
        print(f"[extract] reading GT from {args.gt_bag}  (topic: {args.gt})")
        gt_rows = read_gt_from_bag(args.gt_bag, args.gt)
        if gt_rows:
            with open(out / "gt_tum.txt", "w") as f:
                for row in gt_rows:
                    f.write(" ".join(f"{v:.9f}" for v in row) + "\n")
            print(f"[ok] gt_tum.txt from PGT ({len(gt_rows)} poses)")
    elif gps_rows:
        ts   = np.array([row[0] for row in gps_rows])
        lats = [row[1] for row in gps_rows]
        lons = [row[2] for row in gps_rows]
        alts = [row[3] for row in gps_rows]
        x, y, z = gps_to_enu(lats, lons, alts)
        with open(out / "gt_tum.txt", "w") as f:
            for i, t in enumerate(ts):
                f.write(f"{t:.9f} {x[i]:.6f} {y[i]:.6f} {z[i]:.6f} 0 0 0 1\n")
        print(f"[ok] gt_tum.txt from GPS ENU ({len(ts)} poses, orientation=identity)")
    else:
        print("[warn] no GT or GPS found; gt_tum.txt not written")


if __name__ == "__main__":
    main()
