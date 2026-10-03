#!/usr/bin/env python3
"""Build one neutral sensor profile per dataset from the configs the benchmark already runs.

New algorithms must not carry their own hand-copied calibration. Each profile in
configs/sensors/<dataset>.json is derived from the reference stereo-inertial ORB-SLAM3
config of that dataset (camera model, baseline, camera-IMU transform, sensor IMU noise)
plus the camera-IMU time offset declared in the Basalt calibration. --check compares the
result with the OKVIS2 and Basalt configs of the same dataset and fails on disagreement,
so a profile cannot silently drift from what the existing rows use.

Requires OpenCV (cv2) for the OpenCV-YAML reader; run it in the cuvslam conda env.
"""
import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import cv2
import numpy as np

# dataset -> (ORB stereo-inertial config, Basalt calibration, one OKVIS2 VIO config)
DATASETS = {
    'euroc_mav': ('configs/orbslam3/euroc_mav_stereo_inertial.yaml',
                  'configs/basalt/euroc_mav_calib.json',
                  'configs/okvis2/euroc_mav_MH_01_easy_vio.yaml'),
    'rosariov2': ('configs/orbslam3/rosariov2_stereo_inertial.yaml',
                  'configs/basalt/rosariov2_calib.json',
                  'configs/okvis2/rosariov2_sequence1_vio.yaml'),
    'hortimulti': ('configs/orbslam3/hortimulti_stereo_inertial.yaml',
                   'configs/basalt/hortimulti_calib.json',
                   'configs/okvis2/hortimulti_strawberry02_vio.yaml'),
    'zed2i': ('configs/orbslam3/zed2i_field1_110426_full_10fps_q90_stereo_inertial.yaml',
              'configs/basalt/zed2i_calib.json',
              'configs/okvis2/zed2i_field1_110426_full_10fps_q90_vio.yaml'),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def nearest_rotation(r):
    u, _, vt = np.linalg.svd(np.asarray(r, dtype=float))
    return u @ np.diag([1.0, 1.0, np.linalg.det(u @ vt)]) @ vt


def rotation_angle_deg(a, b):
    """Angle between two rotations. Configs store rounded, slightly non-orthonormal
    matrices, so both are projected onto SO(3) first; otherwise the rounding itself
    reads as a ~0.1 degree difference."""
    r = nearest_rotation(a).T @ nearest_rotation(b)
    return math.degrees(math.atan2(np.linalg.norm([r[2, 1] - r[1, 2], r[0, 2] - r[2, 0], r[1, 0] - r[0, 1]]),
                                   np.trace(r) - 1.0))


def orb_profile(repo, dataset):
    orb_rel, basalt_rel, _ = DATASETS[dataset]
    fs = cv2.FileStorage(str(repo / orb_rel), cv2.FILE_STORAGE_READ)
    if not fs.isOpened():
        raise ValueError('cannot read ' + orb_rel)

    def real(key, required=True):
        node = fs.getNode(key)
        if node.empty():
            if required:
                raise KeyError(f'{orb_rel}: missing {key}')
            return None
        return float(node.real())

    def matrix(key):
        node = fs.getNode(key)
        if node.empty():
            raise KeyError(f'{orb_rel}: missing {key}')
        m = node.mat()
        # Single-precision matrices (dt: f) are returned as float32; take the shortest
        # decimal that round-trips so the profile shows the declared values, not
        # float32 artefacts such as 0.9999920129776001.
        return np.array([[float(np.format_float_positional(v, unique=True)) for v in row] for row in m])

    kind = fs.getNode('Camera.type').string()
    width, height = int(real('Camera.width')), int(real('Camera.height'))
    cam0 = dict(name='cam0', fx=real('Camera1.fx'), fy=real('Camera1.fy'),
                cx=real('Camera1.cx'), cy=real('Camera1.cy'))
    if kind == 'Rectified':
        # Pre-rectified input: both images share the left intrinsics and differ by a pure
        # x translation of one baseline.
        baseline = real('Stereo.b')
        cam0.update(distortion_model='none', distortion=[])
        cam1 = dict(cam0, name='cam1')
        t_cam0_cam1 = np.eye(4)
        t_cam0_cam1[0, 3] = baseline
        rectified = True
    elif kind == 'PinHole':
        def brown(prefix):
            # ORB-SLAM3 order is k1 k2 p1 p2 (k3 absent -> 0).
            return [real(f'{prefix}.k1'), real(f'{prefix}.k2'), real(f'{prefix}.p1'), real(f'{prefix}.p2')]
        cam0.update(distortion_model='radtan', distortion=brown('Camera1'))
        cam1 = dict(name='cam1', fx=real('Camera2.fx'), fy=real('Camera2.fy'),
                    cx=real('Camera2.cx'), cy=real('Camera2.cy'),
                    distortion_model='radtan', distortion=brown('Camera2'))
        # Stereo.T_c1_c2 maps camera-2 coordinates into camera 1: pose of cam1 (right) in cam0.
        t_cam0_cam1 = matrix('Stereo.T_c1_c2')
        baseline = float(np.linalg.norm(t_cam0_cam1[:3, 3]))
        rectified = False
    else:
        raise ValueError(f'{orb_rel}: unsupported Camera.type {kind}')

    t_imu_cam0 = matrix('IMU.T_b_c1')
    if t_imu_cam0.shape != (4, 4) or abs(np.linalg.det(t_imu_cam0[:3, :3]) - 1.0) > 1e-4:
        raise ValueError(f'{orb_rel}: IMU.T_b_c1 is not a rigid transform')
    basalt = json.loads((repo / basalt_rel).read_text())['value0']
    offset_ns = basalt.get('cam_time_offset_ns', 0)
    profile = dict(
        schema=1, dataset=dataset,
        image=dict(width=width, height=height, fps=real('Camera.fps')),
        rectified_input=rectified,
        cameras=[cam0, cam1],
        T_cam0_cam1=t_cam0_cam1.tolist(), baseline_m=baseline,
        imu=dict(T_imu_cam0=t_imu_cam0.tolist(),
                 gyroscope_noise_density=real('IMU.NoiseGyro'),
                 accelerometer_noise_density=real('IMU.NoiseAcc'),
                 gyroscope_random_walk=real('IMU.GyroWalk'),
                 accelerometer_random_walk=real('IMU.AccWalk'),
                 frequency_hz=real('IMU.Frequency')),
        camera_imu_time_offset_s=offset_ns / 1e9,
        time_offset_convention='t_imu = t_camera + camera_imu_time_offset_s',
        frames='cam0 is the rig origin; T_cam0_cam1 is the pose of cam1 in cam0; '
               'T_imu_cam0 maps cam0 coordinates into the IMU frame',
        sources=[dict(path=orb_rel, sha256=sha(repo / orb_rel),
                      fields='camera model, baseline or stereo transform, T_imu_cam0, IMU noise, rate'),
                 dict(path=basalt_rel, sha256=sha(repo / basalt_rel),
                      fields='camera_imu_time_offset_s (cam_time_offset_ns)')])
    return profile


def numbers(text):
    return [float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', text)]


def cross_check(repo, dataset, profile):
    """Return a list of (what, difference, tolerance, ok) against OKVIS2 and Basalt."""
    _, basalt_rel, okvis_rel = DATASETS[dataset]
    rows = []
    t_imu_cam0 = np.asarray(profile['imu']['T_imu_cam0'])
    t_imu_cam1 = t_imu_cam0 @ np.asarray(profile['T_cam0_cam1'])
    cam0 = profile['cameras'][0]

    def compare(label, other, mine, tol_deg=0.02, tol_m=2e-4):
        other = np.asarray(other).reshape(4, 4)
        angle = rotation_angle_deg(other[:3, :3], mine[:3, :3])
        shift = float(np.linalg.norm(other[:3, 3] - mine[:3, 3]))
        rows.append((f'{label} rotation [deg]', angle, tol_deg, angle <= tol_deg))
        rows.append((f'{label} translation [m]', shift, tol_m, shift <= tol_m))

    okvis = re.sub(r'#.*', '', (repo / okvis_rel).read_text())
    t_sc = [numbers(m.group(1)) for m in re.finditer(r'T_SC:\s*\[([^\]]*)\]', okvis)]
    if len(t_sc) != 2 or any(len(t) != 16 for t in t_sc):
        raise ValueError(okvis_rel + ': expected two 4x4 T_SC entries')
    compare('OKVIS2 T_SC cam0 vs T_imu_cam0', t_sc[0], t_imu_cam0)
    compare('OKVIS2 T_SC cam1 vs T_imu_cam1', t_sc[1], t_imu_cam1)
    focal = numbers(re.search(r'focal_length:\s*\[([^\]]*)\]', okvis).group(1))
    principal = numbers(re.search(r'principal_point:\s*\[([^\]]*)\]', okvis).group(1))
    d = max(abs(focal[0] - cam0['fx']), abs(focal[1] - cam0['fy']),
            abs(principal[0] - cam0['cx']), abs(principal[1] - cam0['cy']))
    rows.append(('OKVIS2 cam0 intrinsics [px]', d, 1e-3, d <= 1e-3))

    basalt = json.loads((repo / basalt_rel).read_text())['value0']
    intr = basalt['intrinsics'][0]
    if intr['camera_type'] == 'pinhole':
        # (EuRoC uses Basalt's own double-sphere calibration; not comparable field by field.)
        i = intr['intrinsics']
        d = max(abs(i['fx'] - cam0['fx']), abs(i['fy'] - cam0['fy']),
                abs(i['cx'] - cam0['cx']), abs(i['cy'] - cam0['cy']))
        rows.append(('Basalt cam0 intrinsics [px]', d, 1e-3, d <= 1e-3))
        b = basalt['T_imu_cam']
        base = math.dist([b[0][k] for k in ('px', 'py', 'pz')], [b[1][k] for k in ('px', 'py', 'pz')])
        d = abs(base - profile['baseline_m'])
        rows.append(('Basalt stereo baseline [m]', d, 2e-5, d <= 2e-5))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument('--check', action='store_true',
                    help='do not write; verify stored profiles and cross-check against OKVIS2/Basalt')
    args = ap.parse_args()
    repo = args.repo.resolve()
    out_dir = repo / 'configs/sensors'
    failed = False
    for dataset in DATASETS:
        profile = orb_profile(repo, dataset)
        text = json.dumps(profile, indent=2) + '\n'
        target = out_dir / f'{dataset}.json'
        if args.check:
            if not target.is_file() or target.read_text() != text:
                print(f'[{dataset}] STALE: {target.relative_to(repo)} differs from its sources')
                failed = True
        else:
            out_dir.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
        t = np.asarray(profile['imu']['T_imu_cam0'])
        print(f"[{dataset}] {profile['image']['width']}x{profile['image']['height']} @ {profile['image']['fps']:g} Hz, "
              f"baseline {profile['baseline_m']:.6f} m, T_imu_cam0 lever {np.linalg.norm(t[:3, 3]) * 1000:.1f} mm, "
              f"time offset {profile['camera_imu_time_offset_s'] * 1000:.3f} ms")
        for what, diff, tol, ok in cross_check(repo, dataset, profile):
            print(f"    {'ok  ' if ok else 'FAIL'} {what}: {diff:.3g} (tolerance {tol:g})")
            failed |= not ok
    if failed:
        sys.exit('sensor profile check failed')


if __name__ == '__main__':
    main()
