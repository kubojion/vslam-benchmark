#!/usr/bin/env python3
"""Prepare a sequence for DSOL's offline node and convert its output back.

DSOL's generic stereo reader ("realsense" layout) takes rectified image pairs from
<dir>/infra1 and <dir>/infra2 (sorted *.png) and one calib.txt line "fx fy cx cy baseline".

  stage    Pre-rectified datasets: one symlink per frame to the original file (no pixel
           is copied or changed). Raw EuRoC: images are rectified here with the stereo
           calibration from the shared sensor profile (cv2.stereoRectify, alpha=0 so no
           black border reaches the direct photometric front end) and written as PNG.
  export   DSOL writes "frame_index tx ty tz qx qy qz qw" for the (rectified) left camera.
           Index i is mapped to the i-th camera timestamp, and for rectified-by-us data the
           pose is turned back into the original cam0 frame (T_w_cam0 = T_w_rect * R_rect).
"""
import argparse
import csv
import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np
from scipy.spatial.transform import Rotation


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def frames(sequence):
    def table(cam):
        rows = [r for r in csv.reader((sequence / 'mav0' / cam / 'data.csv').open())
                if r and not r[0].startswith('#')]
        return [(int(r[0]), sequence / 'mav0' / cam / 'data' / r[1].strip()) for r in rows]
    left, right = table('cam0'), table('cam1')
    if [t for t, _ in left] != [t for t, _ in right]:
        raise ValueError('cam0 and cam1 timestamps differ')
    if any(b[0] <= a[0] for a, b in zip(left, left[1:])):
        raise ValueError('camera timestamps must be strictly increasing')
    return left, right


def rectification(sensor):
    """Maps and rectified calibration for raw input. OpenCV wants the transform that takes
    cam0 coordinates into cam1, i.e. the inverse of the profile's T_cam0_cam1."""
    size = (sensor['image']['width'], sensor['image']['height'])
    k, d = [], []
    for cam in sensor['cameras']:
        if cam['distortion_model'] != 'radtan':
            raise ValueError('raw input needs a radtan model')
        k.append(np.array([[cam['fx'], 0, cam['cx']], [0, cam['fy'], cam['cy']], [0, 0, 1]], dtype=float))
        d.append(np.array(cam['distortion'] + [0.0], dtype=float))  # k1 k2 p1 p2 k3
    t_c1_c0 = np.linalg.inv(np.asarray(sensor['T_cam0_cam1'], dtype=float))
    r0, r1, p0, p1, _, _, _ = cv2.stereoRectify(k[0], d[0], k[1], d[1], size,
                                                np.ascontiguousarray(t_c1_c0[:3, :3]),
                                                np.ascontiguousarray(t_c1_c0[:3, 3]).reshape(3, 1),
                                                flags=cv2.CALIB_ZERO_DISPARITY, alpha=0)
    maps = [cv2.initUndistortRectifyMap(k[i], d[i], r, p, size, cv2.CV_32FC1)
            for i, (r, p) in enumerate(((r0, p0), (r1, p1)))]
    baseline = -p1[0, 3] / p1[0, 0]
    return maps, r0, p0, baseline


def stage(args):
    sensor = json.loads(args.sensor.read_text())
    left, right = frames(args.sequence)
    if (args.out / 'stage.json').is_file():
        # Reuse a finished stage only if it describes exactly this input.
        old = json.loads((args.out / 'stage.json').read_text())
        if (old.get('sensor_sha256') != sha(args.sensor) or old.get('timestamps_ns') != [t for t, _ in left]
                or args.max_frames):
            sys.exit('[dsol] stale stage directory: ' + str(args.out))
        print(json.dumps({k: v for k, v in old.items() if k != 'timestamps_ns'}))
        return
    if args.max_frames:
        left, right = left[:args.max_frames], right[:args.max_frames]
    out = args.out
    if out.exists():
        sys.exit('[dsol] incomplete stage directory, remove it first: ' + str(out))
    for name in ('infra1', 'infra2'):
        (out / name).mkdir(parents=True)
    record = dict(schema=1, frames=len(left), timestamps_ns=[t for t, _ in left],
                  sensor_profile=str(args.sensor), sensor_sha256=sha(args.sensor),
                  sequence=str(args.sequence))
    mounts = set()
    if sensor['rectified_input']:
        cam = sensor['cameras'][0]
        calib = [cam['fx'], cam['fy'], cam['cx'], cam['cy'], sensor['baseline_m']]
        for name, table in (('infra1', left), ('infra2', right)):
            for index, (_, path) in enumerate(table):
                real = path.resolve(strict=True)
                mounts.add(str(real.parent))
                os.symlink(real, out / name / f'{index:06d}.png')
        record.update(mode='symlink_original_images', rect_from_cam0=np.eye(3).tolist())
    else:
        maps, r0, p0, baseline = rectification(sensor)
        calib = [p0[0, 0], p0[1, 1], p0[0, 2], p0[1, 2], baseline]

        def remap(job):
            name, index, path, (m1, m2) = job
            image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise FileNotFoundError(path)
            if not cv2.imwrite(str(out / name / f'{index:06d}.png'), cv2.remap(image, m1, m2, cv2.INTER_LINEAR)):
                raise OSError('cannot write rectified image')
        jobs = [(name, i, p, maps[c]) for c, (name, table) in enumerate((('infra1', left), ('infra2', right)))
                for i, (_, p) in enumerate(table)]
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(remap, jobs))
        record.update(mode='rectified_here_stereoRectify_alpha0_bilinear', rect_from_cam0=r0.tolist())
    (out / 'calib.txt').write_text(' '.join(f'{v:.10f}' for v in calib) + '\n')
    record.update(calib_fx_fy_cx_cy_baseline=calib, mounts=sorted(mounts), fps=sensor['image']['fps'])
    # Written last: its presence marks a complete stage.
    (out / 'stage.json').write_text(json.dumps(record) + '\n')
    print(json.dumps({k: v for k, v in record.items() if k != 'timestamps_ns'}))


def export(args):
    record = json.loads((args.stage / 'stage.json').read_text())
    stamps = record['timestamps_ns']
    r_rect = Rotation.from_matrix(np.asarray(record['rect_from_cam0']))
    lines = []
    for line in args.raw.read_text().splitlines():
        p = line.split()
        if len(p) != 8:
            continue
        index = int(p[0])
        if not 0 <= index < len(stamps):
            sys.exit(f'[dsol] pose index {index} outside {len(stamps)} frames')
        v = [float(x) for x in p[1:]]
        if not np.all(np.isfinite(v)):
            continue
        q = (Rotation.from_quat(v[3:7]) * r_rect).as_quat()
        lines.append(f'{stamps[index] / 1e9:.9f} {v[0]:.9f} {v[1]:.9f} {v[2]:.9f} '
                     f'{q[0]:.9f} {q[1]:.9f} {q[2]:.9f} {q[3]:.9f}\n')
    args.trajectory.write_text(''.join(lines))
    print(json.dumps(dict(poses=len(lines), frames=len(stamps))))


def merge_config(args):
    """Write the single parameter file the node loads: upstream defaults with the
    benchmark override applied key by key (what roslaunch does with two <rosparam> loads)."""
    import yaml
    base = yaml.safe_load(args.base.read_text())
    for section, values in yaml.safe_load(args.override.read_text()).items():
        base.setdefault(section, {}).update(values)
    args.out.write_text(yaml.safe_dump(base, sort_keys=True))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='command', required=True)
    s = sub.add_parser('stage')
    s.add_argument('--sequence', required=True, type=Path)
    s.add_argument('--sensor', required=True, type=Path)
    s.add_argument('--out', required=True, type=Path)
    s.add_argument('--max-frames', type=int, default=0, help='diagnostic only')
    s.set_defaults(run=stage)
    e = sub.add_parser('export')
    e.add_argument('--stage', required=True, type=Path)
    e.add_argument('--raw', required=True, type=Path)
    e.add_argument('--trajectory', required=True, type=Path)
    e.set_defaults(run=export)
    m = sub.add_parser('merge-config')
    m.add_argument('--base', required=True, type=Path)
    m.add_argument('--override', required=True, type=Path)
    m.add_argument('--out', required=True, type=Path)
    m.set_defaults(run=merge_config)
    args = ap.parse_args()
    args.run(args)


if __name__ == '__main__':
    main()
