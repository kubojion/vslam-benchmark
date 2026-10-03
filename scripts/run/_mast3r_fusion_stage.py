#!/usr/bin/env python3
"""Prepare a sequence for MASt3R-Fusion and convert its output back.

MASt3R-Fusion reads the EuRoC folder layout, but takes the camera model from
mav0/cam0/sensor.yaml, which only real EuRoC sequences have. One uniform input folder
is therefore built for every dataset:

  stage    mav0/cam0/{data.csv, data -> original image directory, sensor.yaml}
           mav0/imu0/data.csv   IMU samples on the camera clock (values unchanged)
           intrinsics.yaml      width, height, [fx fy cx cy k1 k2 p1 p2], Tic (= T_imu_cam0)
           all from the shared sensor profile; no image is copied or changed.
  config   The run's parameter file: the authors' EuRoC parameter file with the
           benchmark overrides and the per-dataset frame subsampling and IMU noise.
  export   "t x y z qx qy qz qw" in seconds -> TUM trajectory.txt (rows sorted, finite).

The monocular front end uses cam0 only.
"""
import argparse
import csv
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import yaml


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stage(args):
    sensor = json.loads(args.sensor.read_text())
    out = args.out
    key = dict(sensor_sha256=sha(args.sensor), sequence=str(args.sequence))
    if (out / 'stage.json').is_file():
        old = json.loads((out / 'stage.json').read_text())
        if any(old.get(k) != v for k, v in key.items()):
            sys.exit('[mast3r_fusion] stale stage directory: ' + str(out))
        return
    if out.exists():
        sys.exit('[mast3r_fusion] incomplete stage directory, remove it first: ' + str(out))
    cam_csv = args.sequence / 'mav0/cam0/data.csv'
    rows = [r for r in csv.reader(cam_csv.open()) if r and not r[0].startswith('#')]
    stamps = [int(r[0]) for r in rows]
    if any(b <= a for a, b in zip(stamps, stamps[1:])):
        raise ValueError('camera timestamps must be strictly increasing')
    (out / 'mav0/cam0').mkdir(parents=True)
    (out / 'mav0/imu0').mkdir(parents=True)
    image_dir = (args.sequence / 'mav0/cam0/data').resolve(strict=True)
    os.symlink(image_dir, out / 'mav0/cam0/data')
    with (out / 'mav0/cam0/data.csv').open('w') as stream:
        stream.write('#timestamp [ns],filename\n')
        for r in rows:
            if not (image_dir / r[1].strip()).exists():
                raise FileNotFoundError(image_dir / r[1].strip())
            stream.write(f'{int(r[0])},{r[1].strip()}\n')

    cam = sensor['cameras'][0]
    distortion = [float(v) for v in cam['distortion']] if cam['distortion_model'] == 'radtan' else [0.0] * 4
    intrinsics = [cam['fx'], cam['fy'], cam['cx'], cam['cy']]
    width, height = sensor['image']['width'], sensor['image']['height']
    (out / 'mav0/cam0/sensor.yaml').write_text(yaml.safe_dump(dict(
        sensor_type='camera', comment='generated from ' + args.sensor.name, rate_hz=sensor['image']['fps'],
        resolution=[width, height], camera_model='pinhole', intrinsics=intrinsics,
        distortion_model='radial-tangential', distortion_coefficients=distortion), default_flow_style=None))
    t_imu_cam0 = np.array(sensor['imu']['T_imu_cam0'], dtype=float)
    u, _, vt = np.linalg.svd(t_imu_cam0[:3, :3])     # configs store rounded matrices
    t_imu_cam0[:3, :3] = u @ np.diag([1.0, 1.0, np.linalg.det(u @ vt)]) @ vt
    (out / 'intrinsics.yaml').write_text(yaml.safe_dump(dict(
        width=width, height=height, calibration=intrinsics + distortion,
        Tic=[[float(v) for v in row] for row in t_imu_cam0]), default_flow_style=None, sort_keys=False))

    # t_imu = t_camera + offset  ->  camera-clock time of a sample is t_imu - offset.
    offset_ns = int(round(sensor['camera_imu_time_offset_s'] * 1e9))
    imu_csv = args.sequence / 'mav0/imu0/data.csv'
    with (out / 'mav0/imu0/data.csv').open('w') as stream:
        stream.write('#timestamp [ns],w_x,w_y,w_z [rad s^-1],a_x,a_y,a_z [m s^-2]\n')
        count = 0
        for r in csv.reader(imu_csv.open()):
            if not r or r[0].startswith('#'):
                continue
            stream.write(','.join([str(int(r[0]) - offset_ns), *[v.strip() for v in r[1:7]]]) + '\n')
            count += 1
    record = dict(schema=1, **key, frames=len(rows), imu_samples=count, imu_time_offset_ns=offset_ns,
                  fps=sensor['image']['fps'], mounts=[str(image_dir)], dataset=sensor['dataset'],
                  imu=sensor['imu'])
    (out / 'stage.json').write_text(json.dumps(record) + '\n')


def config(args):
    record = json.loads((args.stage / 'stage.json').read_text())
    params = yaml.safe_load(args.base.read_text())
    override = yaml.safe_load(args.override.read_text()) or {}
    for section, values in (override.get('all') or {}).items():
        if isinstance(values, dict):
            params.setdefault(section, {}).update(values)
        else:
            params[section] = values
    # The authors process EuRoC (20 Hz) and their other datasets at 10 Hz.
    params['dataset']['subsample'] = max(1, int(math.floor(record['fps'] / 10.0 + 1e-9)))
    if record['dataset'] not in (override.get('keep_upstream_imu_noise') or []):
        imu = record['imu']
        noise = [imu['accelerometer_noise_density'], imu['gyroscope_noise_density'],
                 imu['accelerometer_random_walk'], imu['gyroscope_random_walk']]
        params['ms_opt']['imu_noise'] = noise
        params['global_opt']['imu_noise'] = noise
    params['ms_opt']['imu_format'] = 'euroc'
    args.out.write_text(yaml.safe_dump(params, sort_keys=False))
    print(json.dumps(dict(subsample=params['dataset']['subsample'], imu_noise=params['ms_opt']['imu_noise'])))


def export(args):
    rows = []
    for line in args.raw.read_text().splitlines():
        p = line.replace(',', ' ').split()
        if len(p) < 8 or p[0].startswith('#'):
            continue
        v = [float(x) for x in p[:8]]
        if not np.all(np.isfinite(v)) or abs(np.linalg.norm(v[4:8]) - 1.0) > 1e-3:
            continue
        rows.append(v)
    rows.sort()
    unique = [r for i, r in enumerate(rows) if i == 0 or r[0] > rows[i - 1][0]]
    args.trajectory.write_text(''.join(
        f'{r[0]:.9f} ' + ' '.join(f'{x:.9f}' for x in r[1:]) + '\n' for r in unique))
    print(json.dumps(dict(poses=len(unique))))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='command', required=True)
    s = sub.add_parser('stage')
    s.add_argument('--sequence', required=True, type=Path)
    s.add_argument('--sensor', required=True, type=Path)
    s.add_argument('--out', required=True, type=Path)
    s.set_defaults(run=stage)
    c = sub.add_parser('config')
    c.add_argument('--stage', required=True, type=Path)
    c.add_argument('--base', required=True, type=Path, help='upstream config/base_euroc.yaml')
    c.add_argument('--override', required=True, type=Path)
    c.add_argument('--out', required=True, type=Path)
    c.set_defaults(run=config)
    e = sub.add_parser('export')
    e.add_argument('--raw', required=True, type=Path)
    e.add_argument('--trajectory', required=True, type=Path)
    e.set_defaults(run=export)
    args = ap.parse_args()
    args.run(args)


if __name__ == '__main__':
    main()
