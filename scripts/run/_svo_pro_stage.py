#!/usr/bin/env python3
"""Prepare a sequence for SVO Pro's offline benchmark node and convert its output back.

SVO Pro ships its own offline runner (svo_ros/svo_benchmark, used by the authors'
svo_benchmarking package). It reads a self-contained folder:
    data/images.txt   "id stamp_s left_image right_image"   (paths relative to data/)
    data/imu.txt      "id stamp_s wx wy wz ax ay az"
    calib.yaml        camera rig (T_B_C per camera, B = IMU) + imu_params + imu_initialization

  stage    Build that folder: symlinks to the original images (no pixel is touched; SVO Pro
           applies the distortion model itself, so raw EuRoC images stay raw), IMU samples
           moved onto the camera clock, calibration from the shared sensor profile.
           Timestamps are written relative to the first image to keep full precision in
           the node's double-precision seconds; export adds the offset back.
  config   Write the single parameter file the node loads for one run type.
  export   stamped_traj_estimate.txt (pose of the IMU/body frame) -> TUM trajectory.txt.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import yaml

import _imu_noise_rule

# The upstream calibration files use 752 px wide EuRoC images; the upstream parameter
# file marks these settings as "increase for larger images".
REFERENCE_WIDTH = 752


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


def imu_parameters(args, sensor):
    """IMU noise for the OKVIS-style sliding-window back end.

    upstream:<file>  the authors' own values (EuRoC).
    okvis2:<file>    the benchmark's OKVIS2 configuration of the same dataset. SVO Pro's
                     back end is the OKVIS formulation with the same parameter meaning, and
                     the authors publish no values for these sensors."""
    kind, _, path = args.imu_params.partition(':')
    text = Path(path).read_text()
    if kind == 'upstream':
        p = yaml.safe_load(text)['imu_params']
        params = {k: float(p[k]) for k in ('acc_max', 'omega_max', 'sigma_omega_c', 'sigma_acc_c',
                                           'sigma_omega_bias_c', 'sigma_acc_bias_c', 'g', 'imu_rate')}
    elif kind == 'okvis2':
        def value(key):
            m = re.search(rf'^\s*{key}:\s*([-+0-9.eE]+)', text, re.M)
            if not m:
                raise KeyError(f'{path}: {key}')
            return float(m.group(1))
        params = dict(acc_max=value('a_max'), omega_max=value('g_max'),
                      sigma_omega_c=value('sigma_g_c'), sigma_acc_c=value('sigma_a_c'),
                      sigma_omega_bias_c=value('sigma_gw_c'), sigma_acc_bias_c=value('sigma_aw_c'),
                      g=value('g'), imu_rate=float(sensor['imu']['frequency_hz']))
    else:
        raise ValueError('--imu-params must be upstream:<file> or okvis2:<file>')
    # IMU noise rule "authors' operating point" (configs/sensors/imu-noise-rule.json): on its datasets the
    # four noise quantities are the dataset's Allan values x SVO Pro's EuRoC factors.
    noise_rule = None
    if _imu_noise_rule.applies(sensor['dataset']):
        n = _imu_noise_rule.noise('svo_pro', sensor['dataset'])
        params.update(sigma_omega_c=n['gyroscope_noise_density'], sigma_acc_c=n['accelerometer_noise_density'],
                      sigma_omega_bias_c=n['gyroscope_random_walk'], sigma_acc_bias_c=n['accelerometer_random_walk'])
        noise_rule = _imu_noise_rule.record(dataset=sensor['dataset'])
    # A frame is rejected when the newest IMU sample is older than this; upstream uses
    # 10 ms for a 200 Hz IMU (two sample periods).
    params.update(delay_imu_cam=0.0, sigma_integration=0.0,
                  max_imu_delta_t=max(0.01, 2.0 / float(sensor['imu']['frequency_hz'])))
    return params, dict(kind=kind, path=str(path), sha256=sha(path), noise_rule=noise_rule)


def matrix_node(m):
    # Configs store rounded rotation matrices; SVO Pro's pose type refuses anything that
    # is not orthonormal to machine precision, so take the nearest rotation.
    m = np.array(m, dtype=float)
    u, _, vt = np.linalg.svd(m[:3, :3])
    m[:3, :3] = u @ np.diag([1.0, 1.0, np.linalg.det(u @ vt)]) @ vt
    m[3] = [0.0, 0.0, 0.0, 1.0]
    return dict(cols=4, rows=4, data=[float(v) for v in m.reshape(-1)])


def stage(args):
    sensor = json.loads(args.sensor.read_text())
    left, right = frames(args.sequence)
    out = args.out
    key = dict(stage_schema=2, sensor_sha256=sha(args.sensor), imu_params=args.imu_params,
               timestamps_ns=[t for t, _ in left], max_frames=args.max_frames)
    if sensor['dataset'] == 'rosariov2':
        key['prepared_manifest_sha256'] = sha(args.sequence / 'manifest.json')
    if _imu_noise_rule.applies(sensor['dataset']):     # a rule edit must not reuse a staged calibration
        key['noise_rule'] = _imu_noise_rule.record(dataset=sensor['dataset'])['sha256']
    if (out / 'stage.json').is_file():
        old = json.loads((out / 'stage.json').read_text())
        if any(old.get(k) != v for k, v in key.items()):
            sys.exit('[svo_pro] stale stage directory: ' + str(out))
        return
    if out.exists():
        sys.exit('[svo_pro] incomplete stage directory, remove it first: ' + str(out))
    if args.max_frames:
        left, right = left[:args.max_frames], right[:args.max_frames]
    (out / 'data/img').mkdir(parents=True)
    t0 = left[0][0]
    mounts = set()
    with (out / 'data/images.txt').open('w') as stream:
        stream.write('# id timestamp_s(relative) left right\n')
        for index, ((stamp, lp), (_, rp)) in enumerate(zip(left, right)):
            names = []
            for tag, path in (('l', lp), ('r', rp)):
                real = path.resolve(strict=True)
                mounts.add(str(real.parent))
                name = f'img/{tag}_{index:06d}{real.suffix.lower()}'
                os.symlink(real, out / 'data' / name)
                names.append(name)
            stream.write(f'{index} {(stamp - t0) / 1e9:.9f} {names[0]} {names[1]}\n')

    # t_imu = t_camera + offset  ->  camera-clock time of a sample is t_imu - offset.
    offset_ns = int(round(sensor['camera_imu_time_offset_s'] * 1e9))
    imu_csv = args.sequence / 'mav0/imu0/data.csv'
    stamps = np.loadtxt(imu_csv, delimiter=',', comments='#', dtype=np.int64, usecols=0) - offset_ns
    values = np.loadtxt(imu_csv, delimiter=',', comments='#', dtype=np.float64, usecols=range(1, 7))
    if np.any(np.diff(stamps) <= 0):
        raise ValueError('IMU timestamps must be strictly increasing')
    with (out / 'data/imu.txt').open('w') as stream:
        stream.write('# id timestamp_s(relative, camera clock) wx wy wz ax ay az\n')
        for index, (stamp, v) in enumerate(zip(stamps, values)):
            stream.write(f'{index} {(int(stamp) - t0) / 1e9:.9f} ' + ' '.join(f'{x:.12g}' for x in v) + '\n')

    t_imu_cam0 = np.asarray(sensor['imu']['T_imu_cam0'], dtype=float)
    transforms = [t_imu_cam0, t_imu_cam0 @ np.asarray(sensor['T_cam0_cam1'], dtype=float)]
    cameras = []
    for index, (cam, t_b_c) in enumerate(zip(sensor['cameras'], transforms)):
        if cam['distortion_model'] == 'radtan':
            distortion = dict(type='radial-tangential',
                              parameters=dict(cols=1, rows=4, data=[float(v) for v in cam['distortion']]))
        elif cam['distortion_model'] == 'none':
            distortion = dict(type='radial-tangential', parameters=dict(cols=1, rows=4, data=[0.0] * 4))
        else:
            raise ValueError('unsupported distortion model')
        cameras.append({'camera': {
            'label': f'cam{index}', 'id': hashlib.md5(f'{sensor["dataset"]}-cam{index}'.encode()).hexdigest(),
            'line-delay-nanoseconds': 0, 'image_height': sensor['image']['height'],
            'image_width': sensor['image']['width'], 'type': 'pinhole',
            'intrinsics': dict(cols=1, rows=4, data=[cam['fx'], cam['fy'], cam['cx'], cam['cy']]),
            'distortion': distortion}, 'T_B_C': matrix_node(t_b_c)})
    imu_params, imu_source = imu_parameters(args, sensor)
    calib = {'label': sensor['dataset'], 'id': hashlib.md5(sensor['dataset'].encode()).hexdigest(),
             'cameras': cameras, 'imu_params': imu_params,
             # Upstream EuRoC initial state: at rest, zero biases, same prior widths.
             'imu_initialization': dict(velocity=[0.0, 0.0, 0.0], omega_bias=[0.0, 0.0, 0.0],
                                        acc_bias=[0.0, 0.0, 0.0], velocity_sigma=2.0,
                                        omega_bias_sigma=0.01, acc_bias_sigma=0.1)}
    (out / 'calib.yaml').write_text(yaml.safe_dump(calib, sort_keys=False, default_flow_style=None))
    # The back end accepts a frame only if IMU samples exist on both sides of it; the
    # offline node otherwise waits forever. Recordings where the IMU starts after the
    # camera (HortiMulti) or stops before it (ZED) are therefore trimmed for the inertial
    # run types to the frames with two samples before and two after.
    first_imu_frame = next((i for i, (stamp, _) in enumerate(left) if stamp > int(stamps[1])), None)
    end_imu_frame = sum(1 for stamp, _ in left if stamp < int(stamps[-2]))
    if first_imu_frame is None or end_imu_frame <= first_imu_frame:
        raise ValueError('camera and IMU records do not overlap')
    record = dict(schema=1, **key, frames=len(left), t0_ns=t0, imu_samples=int(len(stamps)),
                  first_frame_with_imu=first_imu_frame, end_frame_with_imu=end_imu_frame,
                  imu_time_offset_ns=offset_ns, imu_source=imu_source, mounts=sorted(mounts),
                  image_width=sensor['image']['width'], sequence=str(args.sequence))
    (out / 'stage.json').write_text(json.dumps(record) + '\n')


MODES = {
    # "Normally the prior should be 0 if not using IMU" (upstream parameter file).
    'vo': dict(use_imu=False, use_ceres_backend=False, runlc=False,
               img_align_prior_lambda_rot=0.0, poseoptim_prior_lambda=0.0),
    'vio': dict(use_imu=True, use_ceres_backend=True, runlc=False),
    'vio-lc': dict(use_imu=True, use_ceres_backend=True, runlc=True),
}


def config(args):
    record = json.loads((args.stage / 'stage.json').read_text())
    params = yaml.safe_load(args.base.read_text())
    override = yaml.safe_load(args.override.read_text()) or {}
    params.update(override.get('all', {}))
    scale = max(1.0, record['image_width'] / REFERENCE_WIDTH)
    large = scale >= 1.5
    params.update(grid_size=int(round(25 * scale)),
                  n_pyr_levels=4 if large else 3,
                  img_align_max_level=5 if large else 4,
                  poseoptim_thresh=round(2.0 * scale, 3),
                  init_min_disparity=int(round(30 * scale)))
    params.update(MODES[args.mode])
    params.update(dataset_directory=args.stage_in_container, calib_file=args.stage_in_container + '/calib.yaml',
                  trace_dir=args.trace_in_container, dataset_is_stereo=True, dataset_is_kitti=False,
                  dataset_is_blender=False)
    # dataset_last_frame is exclusive; 0 means "to the end".
    inertial = MODES[args.mode]['use_imu']
    trimmed_end = record['end_frame_with_imu'] < record['frames']
    params.update(dataset_first_frame=record['first_frame_with_imu'] if inertial else 0,
                  dataset_last_frame=record['end_frame_with_imu'] if inertial and trimmed_end else 0)
    args.out.write_text(yaml.safe_dump(params, sort_keys=True))


def export(args):
    record = json.loads((args.stage / 'stage.json').read_text())
    t0 = record['t0_ns']
    lines = []
    for line in args.raw.read_text().splitlines():
        p = line.split()
        if len(p) != 8 or p[0].startswith('#'):
            continue
        v = [float(x) for x in p]
        if not np.all(np.isfinite(v)):
            continue
        stamp_ns = t0 + int(round(v[0] * 1e9))
        lines.append((stamp_ns, f'{stamp_ns / 1e9:.9f} ' + ' '.join(f'{x:.9f}' for x in v[1:]) + '\n'))
    lines.sort()
    args.trajectory.write_text(''.join(text for _, text in lines))
    print(json.dumps(dict(poses=len(lines), frames=record['frames'])))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='command', required=True)
    s = sub.add_parser('stage')
    s.add_argument('--sequence', required=True, type=Path)
    s.add_argument('--sensor', required=True, type=Path)
    s.add_argument('--imu-params', required=True, help='upstream:<calib yaml> or okvis2:<config yaml>')
    s.add_argument('--out', required=True, type=Path)
    s.add_argument('--max-frames', type=int, default=0, help='diagnostic only')
    s.set_defaults(run=stage)
    c = sub.add_parser('config')
    c.add_argument('--stage', required=True, type=Path)
    c.add_argument('--base', required=True, type=Path, help='upstream svo_ros/param/vio_stereo.yaml')
    c.add_argument('--override', required=True, type=Path)
    c.add_argument('--mode', required=True, choices=sorted(MODES))
    c.add_argument('--stage-in-container', required=True)
    c.add_argument('--trace-in-container', required=True)
    c.add_argument('--out', required=True, type=Path)
    c.set_defaults(run=config)
    e = sub.add_parser('export')
    e.add_argument('--stage', required=True, type=Path)
    e.add_argument('--raw', required=True, type=Path)
    e.add_argument('--trajectory', required=True, type=Path)
    e.set_defaults(run=export)
    args = ap.parse_args()
    args.run(args)


if __name__ == '__main__':
    main()
