#!/usr/bin/env python3
"""Extract stereo images, GT, and IMU data from a HortiMulti ROS1 bag.

Topics consumed:
  /forwardLeft/image_raw/compressed   sensor_msgs/CompressedImage  ~10 Hz
  /forwardRight/image_raw/compressed  sensor_msgs/CompressedImage  ~10 Hz
  /ms/imu/data                        sensor_msgs/Imu              ~200 Hz

Processing pipeline per frame:
  1. Decode JPEG bytes → grayscale numpy array
  2. Apply pre-computed fisheye stereo rectification (OpenCV fisheye module)
  3. Resize to target resolution (default 640×480)
  4. Save as PNG

Ground truth is read from an external GT_trajectory.csv (not the bag).

Output layout:
  <out>/mav0/cam0/data/<ns_stamp>.png   ← forwardLeft  (rectified)
  <out>/mav0/cam1/data/<ns_stamp>.png   ← forwardRight (rectified)
  <out>/cam0  →  mav0/cam0/data         (symlink)
  <out>/cam1  →  mav0/cam1/data         (symlink)
  <out>/left  →  mav0/cam0/data         (MAC-VO symlink)
  <out>/right →  mav0/cam1/data         (MAC-VO symlink)
  <out>/times.txt                       nanosecond stamps, one per line
  <out>/gt_tum.txt                      TUM format  (seconds tx ty tz qx qy qz qw)
  <out>/mav0/imu0/data.csv              EuRoC format (ns, wx, wy, wz, ax, ay, az)  [unless --no-imu]

Requires: pip install rosbags numpy opencv-python
"""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np

try:
    from rosbags.rosbag1 import Reader
    from rosbags.typesys import Stores, get_typestore
except ImportError:
    sys.exit("pip install rosbags")

import cv2

# ── Camera calibration (from calibration.yaml, cam1=forwardLeft, cam2=forwardRight)
# Equidistant (fisheye) distortion model, native resolution 2048×1536.
K1 = np.array([[1057.8085759554679, 0.0, 1031.0394456453769],
               [0.0, 1057.8344071878955, 727.7604933179784],
               [0.0, 0.0, 1.0]])
D1 = np.array([[-0.03999018098363963],
               [0.0035531756082936186],
               [-0.0006681279528559426],
               [-0.0009677749839773924]])

K2 = np.array([[1058.4010918263214, 0.0, 1029.3052164899436],
               [0.0, 1058.5035544505658, 717.0103196643621],
               [0.0, 0.0, 1.0]])
D2 = np.array([[-0.03124164248538125],
               [-0.02633329423472931],
               [0.03894424132096168],
               [-0.019217878957815994]])

# T_forwardRight_cam_forwardLeft_cam  (right camera pose expressed in left frame)
R_L2R = np.array([
    [0.9997098979861837, -0.00024386552740930396, -0.02408444307115879],
    [0.00022409754414127157, 0.9999996358356008, -0.0008234737067051285],
    [0.024084635117311973, 0.0008178375507802361, 0.9997095885771006],
])
T_L2R = np.array([-0.13950074274105580,
                  -0.00027495044190387356,
                  -0.00040285996536457207])

SRC_SIZE = (2048, 1536)   # native resolution (width, height)
OUT_SIZE  = (640,  480)   # target resolution after rectification + resize

TYPESTORE = None  # initialised in main()


def build_rectify_maps(src_size=SRC_SIZE, out_size=OUT_SIZE):
    """Compute and return (map1_L, map2_L, map1_R, map2_R, P1, P2)."""
    R1, R2, P1, P2, _Q = cv2.fisheye.stereoRectify(
        K1, D1, K2, D2,
        src_size,
        R_L2R, T_L2R.reshape(3, 1),
        cv2.CALIB_ZERO_DISPARITY,
        newImageSize=src_size,   # keep at native for the maps; resize separately
        balance=0.0,
    )
    map1_L, map2_L = cv2.fisheye.initUndistortRectifyMap(
        K1, D1, R1, P1, src_size, cv2.CV_16SC2)
    map1_R, map2_R = cv2.fisheye.initUndistortRectifyMap(
        K2, D2, R2, P2, src_size, cv2.CV_16SC2)
    return map1_L, map2_L, map1_R, map2_R, P1, P2


def decode_compressed(msg) -> np.ndarray:
    """Decode sensor_msgs/CompressedImage → grayscale numpy array."""
    raw = bytes(msg.data)
    buf = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise RuntimeError("cv2.imdecode returned None — bad compressed image")
    return img


def header_stamp_ns(msg) -> int:
    s = msg.header.stamp
    return int(s.sec) * 1_000_000_000 + int(s.nanosec)


def rectify_and_save(img: np.ndarray, map1, map2, out_path: Path,
                     out_size: tuple) -> None:
    rect = cv2.remap(img, map1, map2, cv2.INTER_LINEAR)
    if (rect.shape[1], rect.shape[0]) != out_size:
        rect = cv2.resize(rect, out_size, interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(out_path), rect)


def stream_and_extract(bag_path, left_topic, right_topic,
                       cam0_dir, cam1_dir, map1_L, map2_L, map1_R, map2_R,
                       out_size, max_frames):
    """Stream the bag, rectify+save each image with its original timestamp.

    Returns (left_stamps, right_stamps) — nanosecond integer lists.
    Right frames are saved under their own timestamps; a subsequent
    match_stereo_pairs() call renames them to match left timestamps.
    """
    left_stamps, right_stamps = [], []

    with Reader(bag_path) as r:
        topics_in_bag = {c.topic for c in r.connections}
        for t in (left_topic, right_topic):
            if t not in topics_in_bag:
                print(f"[warn] topic {t!r} not found in bag — check topic name")

        for c, _t_ns, raw in r.messages():
            if c.topic == left_topic:
                msg = TYPESTORE.deserialize_ros1(raw, c.msgtype)
                ns  = header_stamp_ns(msg)
                img = decode_compressed(msg)
                rectify_and_save(img, map1_L, map2_L,
                                 cam0_dir / f"{ns}.png", out_size)
                left_stamps.append(ns)
                if len(left_stamps) % 200 == 0:
                    print(f"  [extract] {len(left_stamps)} left frames ...",
                          flush=True)
                if max_frames and len(left_stamps) >= max_frames:
                    break

            elif c.topic == right_topic:
                msg = TYPESTORE.deserialize_ros1(raw, c.msgtype)
                ns  = header_stamp_ns(msg)
                img = decode_compressed(msg)
                rectify_and_save(img, map1_R, map2_R,
                                 cam1_dir / f"{ns}.png", out_size)
                right_stamps.append(ns)

    return left_stamps, right_stamps


def match_stereo_pairs(cam0_dir: Path, cam1_dir: Path,
                       left_stamps: list, right_stamps: list,
                       max_diff_ns: int = 50_000_000) -> list:
    """Match left and right frames by nearest timestamp.

    The forward stereo cameras are not hardware-synchronized and have a
    ~12 ms clock offset.  This function:
      1. Finds the closest right timestamp for each left timestamp.
      2. Renames the right image file to the left timestamp so that both
         directories share identical filenames (required by ORB-SLAM3 and
         expected by DROID-SLAM / MAC-VO which pair by sort order).
      3. Removes unmatched right images.

    Returns the list of matched left timestamps (nanoseconds).
    """
    import bisect

    right_sorted = sorted(right_stamps)
    right_set    = set(right_sorted)
    matched_left = []
    used_right   = set()

    for l_ns in sorted(left_stamps):
        # Binary-search for the closest right timestamp
        idx = bisect.bisect_left(right_sorted, l_ns)
        candidates = []
        if idx < len(right_sorted):
            candidates.append(right_sorted[idx])
        if idx > 0:
            candidates.append(right_sorted[idx - 1])

        if not candidates:
            continue
        r_ns = min(candidates, key=lambda x: abs(x - l_ns))

        if r_ns in used_right:
            continue  # already consumed by a closer left frame

        diff = abs(r_ns - l_ns)
        if diff > max_diff_ns:
            print(f"  [match] skipping l={l_ns}: closest right diff={diff/1e6:.1f} ms > {max_diff_ns/1e6:.0f} ms")
            continue

        used_right.add(r_ns)
        matched_left.append(l_ns)

        if r_ns != l_ns:
            src = cam1_dir / f"{r_ns}.png"
            dst = cam1_dir / f"{l_ns}.png"
            src.rename(dst)

    # Remove unmatched right images
    for r_ns in right_set - used_right:
        p = cam1_dir / f"{r_ns}.png"
        if p.exists():
            p.unlink()

    # Also remove unmatched left images
    matched_set = set(matched_left)
    for l_ns in left_stamps:
        if l_ns not in matched_set:
            p = cam0_dir / f"{l_ns}.png"
            if p.exists():
                p.unlink()

    print(f"  [match] {len(matched_left)} matched pairs "
          f"(dropped {len(left_stamps) - len(matched_left)} left, "
          f"{len(right_stamps) - len(matched_left)} right)")
    return sorted(matched_left)


def convert_gt_csv(csv_path: Path, out_path: Path) -> int:
    """Convert GT_trajectory.csv → TUM-format gt_tum.txt.

    CSV columns of interest:
      %time                      (nanoseconds or seconds — auto-detected)
      field.pose.pose.position.x/y/z
      field.pose.pose.orientation.x/y/z/w
    """
    count = 0
    with open(csv_path) as f_in, open(out_path, "w") as f_out:
        reader = csv.DictReader(f_in)
        for row in reader:
            t = float(row["%time"])
            # Auto-detect nanoseconds: realistic ROS epoch seconds are ~1.7e9;
            # nanoseconds are ~1.7e18.  Threshold at 1e12 is unambiguous.
            if t > 1e12:
                t /= 1e9
            tx = float(row["field.pose.pose.position.x"])
            ty = float(row["field.pose.pose.position.y"])
            tz = float(row["field.pose.pose.position.z"])
            qx = float(row["field.pose.pose.orientation.x"])
            qy = float(row["field.pose.pose.orientation.y"])
            qz = float(row["field.pose.pose.orientation.z"])
            qw = float(row["field.pose.pose.orientation.w"])
            f_out.write(
                f"{t:.9f} {tx:.9f} {ty:.9f} {tz:.9f} "
                f"{qx:.9f} {qy:.9f} {qz:.9f} {qw:.9f}\n"
            )
            count += 1
    return count


def print_rectified_intrinsics(P1, P2, out_size, src_size):
    sx = out_size[0] / src_size[0]
    sy = out_size[1] / src_size[1]
    fx = P1[0, 0] * sx
    fy = P1[1, 1] * sy
    cx = P1[0, 2] * sx
    cy = P1[1, 2] * sy
    # Baseline is physical (metres): P2[0,3] = -fx_native * baseline_m
    # so baseline_m = -P2[0,3] / P1[0,0]  (P1[0,0] is native-resolution fx)
    baseline = -P2[0, 3] / P1[0, 0]
    print()
    print("=" * 60)
    print(f"Rectified intrinsics at {out_size[0]}×{out_size[1]}")
    print(f"  fx = {fx:.4f}")
    print(f"  fy = {fy:.4f}")
    print(f"  cx = {cx:.4f}")
    print(f"  cy = {cy:.4f}")
    print(f"  baseline = {baseline:.6f} m")
    print(f"\nDROID-SLAM calib line:")
    print(f"  {fx:.4f} {fy:.4f} {cx:.4f} {cy:.4f}")
    print("=" * 60)
    print()


def extract_imu(bag_path, imu_topic, out_dir, typestore):
    """Extract imu_topic from bag -> mav0/imu0/data.csv in EuRoC format.

    EuRoC IMU CSV header:
      #timestamp [ns],w_RS_S_x [rad s^-1],w_RS_S_y [rad s^-1],w_RS_S_z [rad s^-1],\
 a_RS_S_x [m s^-2],a_RS_S_y [m s^-2],a_RS_S_z [m s^-2]
    """
    imu0_dir = out_dir / "mav0" / "imu0"
    imu0_dir.mkdir(parents=True, exist_ok=True)
    csv_path = imu0_dir / "data.csv"
    header = (
        "#timestamp [ns],"
        "w_RS_S_x [rad s^-1],w_RS_S_y [rad s^-1],w_RS_S_z [rad s^-1],"
        "a_RS_S_x [m s^-2],a_RS_S_y [m s^-2],a_RS_S_z [m s^-2]"
    )
    rows = []
    with Reader(bag_path) as reader:
        topics_in_bag = {c.topic for c in reader.connections}
        if imu_topic not in topics_in_bag:
            raise RuntimeError(
                f"IMU topic '{imu_topic}' not found in bag.  "
                f"Available: {sorted(topics_in_bag)}"
            )
        conns = [c for c in reader.connections if c.topic == imu_topic]
        for _conn, _timestamp, rawdata in reader.messages(connections=conns):
            msg = typestore.deserialize_ros1(rawdata, _conn.msgtype)
            ts_ns = header_stamp_ns(msg)
            gx = msg.angular_velocity.x
            gy = msg.angular_velocity.y
            gz = msg.angular_velocity.z
            ax = msg.linear_acceleration.x
            ay = msg.linear_acceleration.y
            az = msg.linear_acceleration.z
            rows.append(f"{ts_ns},{gx},{gy},{gz},{ax},{ay},{az}")
    with open(csv_path, "w") as f:
        f.write(header + "\n")
        f.write("\n".join(rows))
        if rows:
            f.write("\n")
    return len(rows)


def make_symlink(src: str, dst: Path) -> None:
    if not dst.exists() and not dst.is_symlink():
        dst.symlink_to(src)


def main():
    global TYPESTORE

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bag",       required=True, help="Path to .bag file")
    ap.add_argument("--gt_csv",    required=True,
                    help="Path to GT_trajectory.csv")
    ap.add_argument("--out",       required=True, help="Output directory")
    ap.add_argument("--left",      default="/forwardLeft/image_raw/compressed")
    ap.add_argument("--right",     default="/forwardRight/image_raw/compressed")
    ap.add_argument("--width",     type=int, default=640,
                    help="Output image width (default 640)")
    ap.add_argument("--height",    type=int, default=480,
                    help="Output image height (default 480)")
    ap.add_argument("--max_frames", type=int, default=0,
                    help="Extract only first N left frames (0=all)")
    ap.add_argument("--imu",        default="/ms/imu/data",
                    help="IMU topic name (default /ms/imu/data)")
    ap.add_argument("--no-imu",     dest="no_imu", action="store_true",
                    help="Skip IMU extraction")
    ap.add_argument("--imu-only",   dest="imu_only", action="store_true",
                    help="Extract only IMU (skip image extraction, GT, symlinks)")
    args = ap.parse_args()

    TYPESTORE = get_typestore(Stores.ROS1_NOETIC)
    out_size  = (args.width, args.height)
    out       = Path(args.out)

    # ── IMU-only fast path
    if args.imu_only:
        imu_dir = out / "mav0" / "imu0"
        imu_dir.mkdir(parents=True, exist_ok=True)
        print(f"[extract] --imu-only: extracting IMU from '{args.imu}' ...", flush=True)
        n_imu = extract_imu(Path(args.bag), args.imu, out, TYPESTORE)
        print(f"[extract] imu0/data.csv -> {out / 'mav0' / 'imu0' / 'data.csv'}  ({n_imu} samples)")
        print(f"[extract] done")
        return

    # ── Output directories
    cam0_dir = out / "mav0" / "cam0" / "data"
    cam1_dir = out / "mav0" / "cam1" / "data"
    cam0_dir.mkdir(parents=True, exist_ok=True)
    cam1_dir.mkdir(parents=True, exist_ok=True)

    # ── Compute rectification maps (once, at native resolution)
    print("[extract] computing stereo rectification maps ...", flush=True)
    map1_L, map2_L, map1_R, map2_R, P1, P2 = build_rectify_maps(
        src_size=SRC_SIZE, out_size=SRC_SIZE  # maps at native size
    )
    print_rectified_intrinsics(P1, P2, out_size, SRC_SIZE)

    # ── Extract images
    print(f"[extract] processing bag: {args.bag}", flush=True)
    left_stamps, right_stamps = stream_and_extract(
        Path(args.bag), args.left, args.right,
        cam0_dir, cam1_dir,
        map1_L, map2_L, map1_R, map2_R,
        out_size, args.max_frames,
    )
    print(f"[extract] left={len(left_stamps)}  right={len(right_stamps)} frames")

    if not left_stamps:
        print("[extract] ERROR: no left frames extracted — check --left topic")
        sys.exit(1)

    # ── Match stereo pairs by nearest timestamp (cameras have ~12 ms offset)
    print("[extract] matching stereo pairs ...", flush=True)
    matched_stamps = match_stereo_pairs(cam0_dir, cam1_dir, left_stamps, right_stamps)

    # ── Write times.txt (nanosecond timestamps, one per line, matched pairs only)
    times_path = out / "times.txt"
    with open(times_path, "w") as f:
        for ns in matched_stamps:
            f.write(f"{ns}\n")
    print(f"[extract] times.txt  → {times_path}")

    # ── Write gt_tum.txt from CSV
    gt_out = out / "gt_tum.txt"
    if Path(args.gt_csv).exists():
        n_gt = convert_gt_csv(Path(args.gt_csv), gt_out)
        print(f"[extract] gt_tum.txt → {gt_out}  ({n_gt} poses)")
    else:
        print(f"[extract] WARNING: GT CSV not found at {args.gt_csv}")

    # ── Convenience symlinks
    for name, target in [
        ("cam0",  Path("mav0/cam0/data")),
        ("cam1",  Path("mav0/cam1/data")),
        ("left",  Path("mav0/cam0/data")),   # MAC-VO expects left/right
        ("right", Path("mav0/cam1/data")),
    ]:
        make_symlink(str(target), out / name)

    # ── Extract IMU
    if not args.no_imu:
        print(f"[extract] extracting IMU from '{args.imu}' ...", flush=True)
        n_imu = extract_imu(Path(args.bag), args.imu, out, TYPESTORE)
        print(f"[extract] imu0/data.csv → {out / 'mav0' / 'imu0' / 'data.csv'}  ({n_imu} samples)")
    else:
        print("[extract] --no-imu: skipping IMU extraction")

    total = len(matched_stamps)
    print(f"\n[extract] done — {total} stereo pairs → {out}")


if __name__ == "__main__":
    main()
