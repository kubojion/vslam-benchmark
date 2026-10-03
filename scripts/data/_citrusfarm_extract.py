#!/usr/bin/env python3
"""Extract one CitrusFarm sequence (ROS1 bags, authors' release) into the benchmark layout.

Topics consumed (Teng et al., ISVC 2023, ucr-robotics.github.io/Citrus-Farm-Dataset):
  zed_*.bag   /zed2i/zed_node/left/image_rect_color    sensor_msgs/Image bgra8 1280x720 10 Hz
              /zed2i/zed_node/right/image_rect_color   (factory rectified by the ZED driver)
              /zed2i/zed_node/{left,right}/camera_info  rectified pinhole model
              /zed2i/zed_node/imu/data                 ZED2i internal IMU, camera clock
  base_*.bag  /microstrain/imu/data                    MicroStrain 3DM-GX5, 200 Hz
  ground_truth/<seq>/gt.csv                            RTK position of the GNSS antenna

Image pixels are written unchanged apart from dropping the alpha channel (RGB, lossless
PNG). The MicroStrain samples are kept unchanged. Their host stamps jitter (about 2 ms
std, 17 % duplicates), so each sample is re-stamped on its index at the device's fixed
200 Hz, on the host clock minus the minimum arrival latency (index_restamp). The authors' own fix (imu_filter.py in
the dataset repository) leaves about 0.8 ms std of that jitter; its output and the
original stamps are kept next to the re-stamped file.

Output layout (<out>):
  mav0/cam0/data/<ns>.png, mav0/cam0/data.csv     left
  mav0/cam1/data/<ns>.png, mav0/cam1/data.csv     right
  mav0/imu0/data.csv                              MicroStrain, sample-index stamps (EuRoC columns)
  cam0, cam1, left, right                         symlinks to the image folders
  times.txt                                       left stamps in ns
  gt_antenna_tum.txt                              authors' gt.csv, antenna positions, placeholder quaternions
  sources/microstrain_raw.csv                     same samples, original host stamps
  sources/microstrain_authors_filter.csv          same samples, authors' imu_filter.py stamps
  sources/zed_imu.csv                             ZED2i internal IMU (time-offset measurement only)
  sources/camera_info.json                        first left and right CameraInfo
  manifest.json                                   inputs, counts, timing statistics

Requires: rosbags, numpy, opencv-python (the macvo conda environment has all three).
"""
import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

try:
    from rosbags.highlevel import AnyReader
except ImportError:
    sys.exit('pip install rosbags')
import cv2

LEFT = '/zed2i/zed_node/left/image_rect_color'
RIGHT = '/zed2i/zed_node/right/image_rect_color'
LEFT_INFO = '/zed2i/zed_node/left/camera_info'
RIGHT_INFO = '/zed2i/zed_node/right/camera_info'
ZED_IMU = '/zed2i/zed_node/imu/data'
MS_IMU = '/microstrain/imu/data'
EUROC_IMU_HEADER = ('#timestamp [ns],w_RS_S_x [rad s^-1],w_RS_S_y [rad s^-1],w_RS_S_z [rad s^-1],'
                    'a_RS_S_x [m s^-2],a_RS_S_y [m s^-2],a_RS_S_z [m s^-2]')


def authors_stamp_filter(stamps_s):
    """Offline replica of imu_filter.py (UCR-Robotics/Citrus-Farm-Dataset, main).

    Same constants (Q = 1e-6, R = 0.003**2, fixed 0.005 s step, P0 = 1) and the same order
    of operations, applied to the stamps in recording order. One deliberate difference:
    the state starts one step before the first stamp instead of at 0 s. Started at 0, the
    original needs about 40 samples to converge from epoch 0 to 1.7e9 s and its first
    outputs are hours off; with P0 = 1 the first output equals the first stamp here.
    """
    x, p = (stamps_s[0] - 0.005 if len(stamps_s) else 0.0), 1.0
    q, r, dt = 0.000001, 0.003 ** 2, 0.005
    out = np.empty(len(stamps_s))
    for i, z in enumerate(stamps_s):
        x_pred = x + dt
        p_pred = p + q
        k = p_pred / (p_pred + r)
        x = x_pred + k * (z - x_pred)
        p = (1 - k) * p_pred
        out[i] = x
    return out


def index_restamp(stamps_ns, period_s=0.005, window_s=10.0, envelope_pct=0.0):
    """Stamp each sample on its index, at the host stamp minus the minimum arrival latency.

    The 3DM-GX5 samples on its own clock at a fixed 200 Hz; the recorded host stamps add
    arrival latency (about 2 ms std, duplicates, and a median that switches between modes
    about 1.8 ms apart). Host stamp = sample time + latency >= sample time + minimum
    latency, so the lower envelope of the residual to a linear fit on the sample index k
    follows the device clock. Stamps are a + b*k plus that envelope (minimum per
    `window_s`, linearly interpolated). A dropped sample shifts the envelope by one period;
    the function refuses to stamp across an envelope step of more than half a period. The
    constant minimum latency stays in the stamps; it is part of the camera-IMU time offset
    measured afterwards on these stamps.
    """
    t = (np.asarray(stamps_ns, dtype=np.int64) - int(stamps_ns[0])) * 1e-9
    k = np.arange(len(t), dtype=float)
    b, a = np.polyfit(k, t, 1)
    r = t - (a + b * k)
    window = max(int(round(window_s / period_s)), 1)
    starts = np.arange(0, len(r), window)
    envelope = np.array([np.percentile(r[i:i + window], envelope_pct) for i in starts])
    centres = np.array([k[i:i + window].mean() for i in starts])
    steps = np.flatnonzero(np.abs(np.diff(envelope)) > period_s / 2)
    if len(steps):
        raise ValueError(f'minimum-latency envelope steps > {period_s * 500:.1f} ms between {window_s:.0f} s '
                         f'windows at samples {[int(starts[i + 1]) for i in steps[:10]]}: dropped samples?')
    slow = np.interp(k, centres, envelope)
    fitted = a + b * k + slow
    if np.any(np.diff(fitted) <= 0):
        raise ValueError('index re-stamping produced non-increasing stamps')
    latency = r - slow
    stats = dict(period_s=float(b), samples=int(len(t)), rate_hz=float((len(t) - 1) / t[-1]),
                 arrival_latency_above_minimum_ms=dict(zip(
                     ('median', 'p99', 'max'), np.percentile(latency * 1e3, [50, 99, 100]).round(3).tolist())),
                 envelope_ms=dict(min=round(float(envelope.min() * 1e3), 3), max=round(float(envelope.max() * 1e3), 3),
                                  largest_step=round(float(np.abs(np.diff(envelope)).max() * 1e3), 3) if len(envelope) > 1 else 0.0),
                 window_s=window_s, envelope_percentile=envelope_pct)
    return int(stamps_ns[0]) + np.round(fitted * 1e9).astype(np.int64), stats


def stamp_ns(msg):
    return int(msg.header.stamp.sec) * 1_000_000_000 + int(msg.header.stamp.nanosec)


def imu_row(msg):
    w, a = msg.angular_velocity, msg.linear_acceleration
    return [w.x, w.y, w.z, a.x, a.y, a.z]


def camera_info(msg):
    # ROS1 definitions name the arrays D, K, R, P; ROS2 ones d, k, r, p.
    field = lambda name: [float(v) for v in getattr(msg, name, getattr(msg, name.upper(), []))]
    return dict(width=int(msg.width), height=int(msg.height), distortion_model=msg.distortion_model,
                frame_id=msg.header.frame_id, d=field('d'), k=field('k'), r=field('r'), p=field('p'),
                stamp_ns=stamp_ns(msg))


def save_png(path, image):
    if not cv2.imwrite(str(path), image):
        raise OSError(f'could not write {path}')


def gaps(stamps_ns, nominal_s):
    d = np.diff(np.asarray(stamps_ns, dtype=np.int64)) * 1e-9
    return dict(count=len(stamps_ns), first_ns=int(stamps_ns[0]), last_ns=int(stamps_ns[-1]),
                median_dt_s=float(np.median(d)), min_dt_s=float(d.min()), max_dt_s=float(d.max()),
                non_increasing=int((d <= 0).sum()), gaps_over_1p5_nominal=int((d > 1.5 * nominal_s).sum()))


def md5_list(raw):
    listing = raw / 'dataset_file_list.yaml'
    if not listing.is_file():
        return {}
    import yaml
    tree = yaml.safe_load(listing.read_text())['citrus-farm-dataset']
    return {f'{folder}/{name}': meta['md5'] for folder, files in tree.items() for name, meta in files.items()}


def extract(args):
    raw, out, seq = Path(args.raw), Path(args.out), args.sequence
    bags = sorted((raw / seq).glob('zed_*.bag')) + sorted((raw / seq).glob('base_*.bag'))
    if not bags:
        sys.exit(f'no zed_*.bag / base_*.bag in {raw / seq}')
    gt_csv = raw / 'ground_truth' / seq / 'gt.csv'
    for d in ('mav0/cam0/data', 'mav0/cam1/data', 'mav0/imu0', 'sources'):
        (out / d).mkdir(parents=True, exist_ok=True)

    left, right, info = {}, {}, {}
    ms_stamps, ms_rows, zed_rows = [], [], []
    pool = concurrent.futures.ThreadPoolExecutor(args.writers)
    pending = []
    with AnyReader(bags) as reader:
        wanted = {LEFT, RIGHT, LEFT_INFO, RIGHT_INFO, ZED_IMU, MS_IMU}
        connections = [c for c in reader.connections if c.topic in wanted]
        for connection, _, raw_msg in reader.messages(connections=connections):
            topic = connection.topic
            if topic in (LEFT_INFO, RIGHT_INFO):
                if topic not in info:
                    info[topic] = camera_info(reader.deserialize(raw_msg, connection.msgtype))
                continue
            msg = reader.deserialize(raw_msg, connection.msgtype)
            if topic == MS_IMU:
                ms_stamps.append(stamp_ns(msg))
                ms_rows.append(imu_row(msg))
            elif topic == ZED_IMU:
                zed_rows.append([stamp_ns(msg)] + imu_row(msg))
            else:
                if msg.encoding != 'bgra8':
                    sys.exit(f'unexpected encoding {msg.encoding} on {topic}')
                ns = stamp_ns(msg)
                image = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.step)[:, :msg.width * 4]
                bgr = np.ascontiguousarray(image.reshape(msg.height, msg.width, 4)[:, :, :3])
                (left if topic == LEFT else right)[ns] = True
                cam = 'cam0' if topic == LEFT else 'cam1'
                pending.append(pool.submit(save_png, out / 'mav0' / cam / 'data' / f'{ns}.png', bgr))
                if len(pending) > 4 * args.writers:
                    pending.pop(0).result()
                if args.max_frames and len(left) >= args.max_frames and len(right) >= args.max_frames:
                    break
    for job in pending:
        job.result()
    pool.shutdown()

    # IMU: sample-index re-stamping (primary) and the authors' filter (kept for comparison),
    # both on the original stamps in recording order.
    ms_stamps = np.asarray(ms_stamps, dtype=np.int64)
    try:
        filtered_ns, restamp_stats = index_restamp(ms_stamps)
    except ValueError as exc:
        sys.exit(f'MicroStrain re-stamping refused: {exc}; not writing an IMU file')
    authors_ns = np.round(authors_stamp_filter(ms_stamps * 1e-9) * 1e9).astype(np.int64)

    # Stereo pairs that exist on both sides and lie inside the IMU span (inertial modes
    # need samples on both sides of every frame; all modes use the same frames).
    lo, hi = filtered_ns[0] + args.margin_ns, filtered_ns[-1] - args.margin_ns
    pairs = sorted(ns for ns in left if ns in right and lo <= ns <= hi)
    dropped = sorted((set(left) | set(right)) - set(pairs))
    for ns in dropped:
        for cam in ('cam0', 'cam1'):
            (out / 'mav0' / cam / 'data' / f'{ns}.png').unlink(missing_ok=True)

    for cam in ('cam0', 'cam1'):
        with open(out / 'mav0' / cam / 'data.csv', 'w') as f:
            f.write('#timestamp [ns],filename\n')
            f.writelines(f'{ns},{ns}.png\n' for ns in pairs)
    (out / 'times.txt').write_text(''.join(f'{ns}\n' for ns in pairs))
    with open(out / 'mav0/imu0/data.csv', 'w', newline='') as f:
        f.write(EUROC_IMU_HEADER + '\n')
        w = csv.writer(f)
        w.writerows([int(t)] + [repr(float(v)) for v in row] for t, row in zip(filtered_ns, ms_rows))
    for name, stamps in (('microstrain_raw.csv', ms_stamps), ('microstrain_authors_filter.csv', authors_ns)):
        with open(out / 'sources' / name, 'w', newline='') as f:
            f.write(EUROC_IMU_HEADER + '\n')
            w = csv.writer(f)
            w.writerows([int(t)] + [repr(float(v)) for v in row] for t, row in zip(stamps, ms_rows))
    with open(out / 'sources/zed_imu.csv', 'w', newline='') as f:
        f.write(EUROC_IMU_HEADER + '\n')
        csv.writer(f).writerows([int(r[0])] + [repr(float(v)) for v in r[1:]] for r in zed_rows)
    (out / 'sources/camera_info.json').write_text(json.dumps(
        {'left': info.get(LEFT_INFO), 'right': info.get(RIGHT_INFO)}, indent=1) + '\n')

    gt = np.loadtxt(gt_csv, delimiter=',', comments='#')
    with open(out / 'gt_antenna_tum.txt', 'w') as f:
        f.writelines(f'{t:.9f} {x:.6f} {y:.6f} {z:.6f} 0 0 0 1\n' for t, x, y, z in gt[:, :4])

    for name in ('cam0', 'cam1', 'left', 'right'):
        link = out / name
        if link.is_symlink() or link.exists():
            link.unlink()
        os.symlink(f"mav0/{'cam0' if name in ('cam0', 'left') else 'cam1'}/data", link)

    checksums = md5_list(raw)
    inputs = [dict(path=str(p.relative_to(raw)), md5=checksums.get(str(p.relative_to(raw)))) for p in bags + [gt_csv]]
    manifest = dict(
        dataset='citrusfarm', sequence=args.name, source_sequence=seq,
        source='https://ucr-robotics.github.io/Citrus-Farm-Dataset/ (AWS s3://ucr-robotics/citrus-farm-dataset)',
        inputs=inputs, topics=dict(left=LEFT, right=RIGHT, imu=MS_IMU, camera_clock_imu=ZED_IMU),
        images=dict(format='png', colour='rgb (bgra8 alpha dropped, pixels unchanged)',
                    rectification='ZED driver factory rectification (image_rect_color)',
                    stereo_pairs=len(pairs), unpaired_or_outside_imu_span_removed=len(dropped),
                    timing=gaps(pairs, 0.1)),
        imu=dict(stamps='sample-index re-stamping: linear fit on the sample index plus the minimum-latency '
                        'envelope of the host stamps; samples and their order unchanged',
                 restamping=restamp_stats, original_stamps='sources/microstrain_raw.csv',
                 authors_filter_stamps='sources/microstrain_authors_filter.csv (imu_filter.py, started at the first stamp)',
                 raw_timing=gaps(ms_stamps, 0.005), restamped_timing=gaps(filtered_ns, 0.005),
                 authors_filter_timing=gaps(authors_ns, 0.005),
                 restamped_minus_raw_ms=dict(zip(('p1', 'median', 'p99'),
                                                 np.percentile((filtered_ns - ms_stamps) * 1e-6, [1, 50, 99]).round(3).tolist())),
                 authors_filter_minus_restamped_ms=dict(zip(('p1', 'median', 'p99'),
                                                            np.percentile((authors_ns - filtered_ns) * 1e-6, [1, 50, 99]).round(3).tolist()))),
        zed_imu=dict(timing=gaps([r[0] for r in zed_rows], 0.005) if zed_rows else None,
                     use='camera-IMU time offset measurement only'),
        camera_info=dict(left=info.get(LEFT_INFO), right=info.get(RIGHT_INFO)),
        ground_truth=dict(file='gt_antenna_tum.txt', source=str(gt_csv.relative_to(raw)), samples=len(gt),
                          point='GNSS antenna (SwiftNav Duro), position only; quaternions are placeholders'),
        margin_ns=args.margin_ns, max_frames=args.max_frames)
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=1) + '\n')
    print(json.dumps(dict(stereo_pairs=len(pairs), removed=len(dropped), imu=len(ms_stamps),
                          zed_imu=len(zed_rows), gt=len(gt)), indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--raw', required=True, help='download folder with <seq>/*.bag and ground_truth/')
    ap.add_argument('--sequence', required=True, help="authors' folder name, e.g. 04_13D_Jackal")
    ap.add_argument('--name', required=True, help='benchmark sequence name, e.g. seq04')
    ap.add_argument('--out', required=True)
    ap.add_argument('--writers', type=int, default=3, help='PNG writer threads')
    ap.add_argument('--margin-ns', dest='margin_ns', type=int, default=50_000_000)
    ap.add_argument('--max-frames', dest='max_frames', type=int, default=0, help='smoke test only')
    extract(ap.parse_args())


if __name__ == '__main__':
    main()
