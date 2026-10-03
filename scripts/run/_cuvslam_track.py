#!/usr/bin/env python3
"""Run cuVSLAM (PyCuVSLAM) over one benchmark sequence and export a TUM trajectory.

Inputs are the EuRoC-style layout every sequence in this workspace has
(mav0/cam{0,1}/data.csv + data/, mav0/imu0/data.csv) plus two JSON files:
  --sensor  configs/sensors/<dataset>.json   shared calibration (see build_sensor_profiles.py)
  --config  configs/cuvslam/default.json     estimator settings, identical for every dataset

Run types map to cuVSLAM as
  vo      stereo odometry (OdometryMode.Multicamera), SLAM off
  vo-lc   stereo odometry + SLAM (map, loop closure, pose-graph optimisation)
  vio     stereo-inertial odometry (OdometryMode.Inertial), SLAM off
  vio-lc  stereo-inertial odometry + SLAM

Exported pose: world_from_rig with the rig placed at cam0 (left camera optical frame,
x right / y down / z forward); the world is that frame at the first tracked image.
Without loop closure the per-frame odometry poses are written as they were produced.
With loop closure the trajectory is Tracker.get_all_slam_poses() after the last frame,
i.e. every frame re-expressed in the final optimised pose graph, which is the same
kind of output the other loop-closing rows export (final optimised trajectory).
"""
import argparse
import csv
import json
import sys
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np
from scipy.spatial.transform import Rotation

import cuvslam

MODES = {'vo': ('Multicamera', False), 'vo-lc': ('Multicamera', True),
         'vio': ('Inertial', False), 'vio-lc': ('Inertial', True)}


def to_pose(t):
    t = np.asarray(t, dtype=float)
    u, _, vt = np.linalg.svd(t[:3, :3])          # configs store rounded matrices
    r = u @ np.diag([1.0, 1.0, np.linalg.det(u @ vt)]) @ vt
    return cuvslam.Pose(rotation=Rotation.from_matrix(r).as_quat(), translation=t[:3, 3])


def build_rig(sensor, use_imu):
    width, height = sensor['image']['width'], sensor['image']['height']
    transforms = [np.eye(4), np.asarray(sensor['T_cam0_cam1'], dtype=float)]
    cameras = []
    for spec, rig_from_camera in zip(sensor['cameras'], transforms):
        cam = cuvslam.Camera()
        cam.size = [width, height]
        cam.focal = [spec['fx'], spec['fy']]
        cam.principal = [spec['cx'], spec['cy']]
        if spec['distortion_model'] == 'none':
            cam.distortion = cuvslam.Distortion(cuvslam.Distortion.Model.Pinhole, [])
        elif spec['distortion_model'] == 'radtan':
            k1, k2, p1, p2 = spec['distortion']
            # cuVSLAM Brown order is k1 k2 k3 p1 p2.
            cam.distortion = cuvslam.Distortion(cuvslam.Distortion.Model.Brown, [k1, k2, 0.0, p1, p2])
        else:
            raise ValueError('unsupported distortion model ' + spec['distortion_model'])
        cam.rig_from_camera = to_pose(rig_from_camera)
        cameras.append(cam)
    rig = cuvslam.Rig()
    rig.cameras = cameras
    if use_imu:
        spec = sensor['imu']
        imu = cuvslam.ImuCalibration()
        imu.rig_from_imu = to_pose(np.linalg.inv(np.asarray(spec['T_imu_cam0'], dtype=float)))
        imu.gyroscope_noise_density = spec['gyroscope_noise_density']
        imu.gyroscope_random_walk = spec['gyroscope_random_walk']
        imu.accelerometer_noise_density = spec['accelerometer_noise_density']
        imu.accelerometer_random_walk = spec['accelerometer_random_walk']
        imu.frequency = spec['frequency_hz']
        rig.imus = [imu]
    return rig


def read_frames(sequence):
    def table(cam):
        rows = [r for r in csv.reader((sequence / 'mav0' / cam / 'data.csv').open())
                if r and not r[0].startswith('#')]
        return [(int(r[0]), sequence / 'mav0' / cam / 'data' / r[1].strip()) for r in rows]
    left, right = table('cam0'), table('cam1')
    if [t for t, _ in left] != [t for t, _ in right]:
        raise ValueError('cam0 and cam1 timestamps differ')
    stamps = [t for t, _ in left]
    if any(b <= a for a, b in zip(stamps, stamps[1:])):
        raise ValueError('camera timestamps must be strictly increasing')
    return [(t, l, r) for (t, l), (_, r) in zip(left, right)]


def read_imu(sequence, offset_ns):
    """EuRoC columns: t, gyro xyz [rad/s], accel xyz [m/s^2]. The sensor profile declares
    t_imu = t_camera + offset, so samples are moved onto the camera clock (t - offset);
    cuVSLAM has no time-offset parameter. Values are not modified."""
    data = np.loadtxt(sequence / 'mav0/imu0/data.csv', delimiter=',', comments='#', dtype=np.float64,
                      usecols=range(1, 7))
    stamps = np.loadtxt(sequence / 'mav0/imu0/data.csv', delimiter=',', comments='#', dtype=np.int64,
                        usecols=0) - offset_ns
    if np.any(np.diff(stamps) < 0):
        raise ValueError('IMU timestamps must be non-decreasing')
    return stamps, data


def load_pair(left, right):
    images = [cv2.imread(str(p), cv2.IMREAD_GRAYSCALE) for p in (left, right)]
    if any(i is None for i in images):
        raise FileNotFoundError(f'cannot read {left} / {right}')
    return images


def tum(stamp_ns, pose):
    t, q = pose.translation, pose.rotation
    return (f'{stamp_ns / 1e9:.9f} {t[0]:.9f} {t[1]:.9f} {t[2]:.9f} '
            f'{q[0]:.9f} {q[1]:.9f} {q[2]:.9f} {q[3]:.9f}\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--sequence', required=True, type=Path)
    ap.add_argument('--sensor', required=True, type=Path)
    ap.add_argument('--config', required=True, type=Path)
    ap.add_argument('--mode', required=True, choices=sorted(MODES))
    ap.add_argument('--out', required=True, type=Path, help='run directory')
    ap.add_argument('--max-frames', type=int, default=0, help='diagnostic only: stop after N frames')
    ap.add_argument('--prefetch', type=int, default=8)
    args = ap.parse_args()

    sensor = json.loads(args.sensor.read_text())
    config = json.loads(args.config.read_text())
    odometry_mode, use_slam = MODES[args.mode]
    use_imu = odometry_mode == 'Inertial'

    odom = dict(config['odometry'])
    odom_kwargs = dict(
        odometry_mode=getattr(cuvslam.Tracker.OdometryMode, odometry_mode),
        multicam_mode=getattr(cuvslam.Tracker.MulticameraMode, odom.pop('multicam_mode')),
        # Pre-rectified datasets satisfy cuVSLAM's rectified-stereo assumption; raw
        # EuRoC images do not, so the distortion model is used instead.
        rectified_stereo_camera=bool(sensor['rectified_input']),
        enable_observations_export=False, enable_landmarks_export=False,
        enable_final_landmarks_export=False, **odom)
    slam_kwargs = dict(config['slam']) if use_slam else None
    cuvslam.set_verbosity(int(config.get('verbosity', 0)))
    rig = build_rig(sensor, use_imu)
    tracker = cuvslam.Tracker(rig, cuvslam.Tracker.OdometryConfig(**odom_kwargs),
                              cuvslam.Tracker.SlamConfig(**slam_kwargs) if use_slam else None)

    frames = read_frames(args.sequence)
    if args.max_frames:
        frames = frames[:args.max_frames]
    offset_ns = int(round(sensor['camera_imu_time_offset_s'] * 1e9))
    imu_t, imu_v = read_imu(args.sequence, offset_ns) if use_imu else (np.empty(0, np.int64), None)

    effective = dict(
        cuvslam_version=cuvslam.get_version()[0], run_type=args.mode, sequence=str(args.sequence),
        sensor_profile=str(args.sensor), estimator_config=str(args.config),
        odometry={k: (v.name if hasattr(v, 'name') else v) for k, v in odom_kwargs.items()},
        slam=slam_kwargs, rig_origin='cam0',
        imu_time_policy=('t_imu_on_camera_clock = original_t_imu - camera_imu_time_offset_s'
                         if use_imu else None),
        imu_time_offset_ns=offset_ns if use_imu else None,
        image_decode='cv2.IMREAD_GRAYSCALE (mono8)', frames_offered=len(frames),
        imu_samples_available=int(len(imu_t)),
        trajectory_source='get_all_slam_poses' if use_slam else 'per_frame_odometry')
    (args.out / 'cuvslam_effective_config.json').write_text(json.dumps(effective, indent=2) + '\n')
    print('[cuvslam] ' + json.dumps(effective), flush=True)

    odom_lines, timing, slam_live = [], [], []
    lost = imu_used = lc_events = 0
    last_lc_stamp = None
    imu_index = 0
    pool = ThreadPoolExecutor(max_workers=max(1, args.prefetch))
    pending = deque()
    cursor = 0
    started = time.perf_counter()
    try:
        for index, (stamp, _, _) in enumerate(frames):
            while cursor < len(frames) and len(pending) < args.prefetch:
                pending.append(pool.submit(load_pair, frames[cursor][1], frames[cursor][2]))
                cursor += 1
            images = pending.popleft().result()
            # All IMU samples up to and including this image time, in time order.
            while imu_index < len(imu_t) and imu_t[imu_index] <= stamp:
                m = cuvslam.ImuMeasurement()
                m.timestamp_ns = int(imu_t[imu_index])
                m.angular_velocities = imu_v[imu_index, 0:3]
                m.linear_accelerations = imu_v[imu_index, 3:6]
                tracker.register_imu_measurement(0, m)
                imu_index += 1
                imu_used += 1
            t0 = time.perf_counter()
            estimate, slam_pose = tracker.track(stamp, images)
            dt = time.perf_counter() - t0
            ok = estimate.world_from_rig is not None
            timing.append((stamp, dt, int(ok)))
            if ok:
                odom_lines.append(tum(stamp, estimate.world_from_rig.pose))
                if use_slam and slam_pose is not None:
                    slam_live.append(tum(stamp, slam_pose))
            else:
                lost += 1
            if use_slam:
                metrics = tracker.get_slam_metrics()
                if metrics is not None and metrics.lc_status and metrics.timestamp_ns != last_lc_stamp:
                    last_lc_stamp = metrics.timestamp_ns
                    lc_events += 1
                    print(f'[cuvslam] loop closure at frame {index} t={stamp / 1e9:.3f} '
                          f'(pnp landmarks {metrics.lc_pnp_landmarks_count}, '
                          f'good {metrics.lc_good_landmarks_count})', flush=True)
            if index % 500 == 0:
                print(f'[cuvslam] frame {index}/{len(frames)} lost={lost} '
                      f'elapsed={time.perf_counter() - started:.1f}s', flush=True)
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
    wall = time.perf_counter() - started

    native = args.out / 'native'
    native.mkdir(exist_ok=True)
    (native / 'odometry_tum.txt').write_text(''.join(odom_lines))
    with (native / 'tracking_times.csv').open('w') as stream:
        stream.write('timestamp_ns,track_call_s,tracked\n')
        stream.writelines(f'{s},{d:.6f},{k}\n' for s, d, k in timing)
    final = odom_lines
    if use_slam:
        (native / 'slam_live_tum.txt').write_text(''.join(slam_live))
        poses = tracker.get_all_slam_poses(0)
        final = [tum(p.timestamp_ns, p.pose) for p in sorted(poses, key=lambda p: p.timestamp_ns)]
    (args.out / 'trajectory.txt').write_text(''.join(final))

    calls = np.array([d for _, d, _ in timing]) if timing else np.zeros(1)
    summary = dict(frames_offered=len(frames), odometry_poses=len(odom_lines), final_poses=len(final),
                   frames_without_pose=lost, imu_samples_fed=imu_used, loop_closure_events=lc_events,
                   wall_s=wall, track_call_mean_ms=float(calls.mean() * 1e3),
                   track_call_p95_ms=float(np.percentile(calls, 95) * 1e3),
                   track_call_max_ms=float(calls.max() * 1e3))
    (args.out / 'cuvslam_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('[cuvslam] summary ' + json.dumps(summary), flush=True)
    if not final:
        sys.exit('[cuvslam] no pose was produced')


if __name__ == '__main__':
    main()
