"""The four added algorithms take their calibration from one sensor profile per dataset.

These tests fail when a profile no longer matches the reference configs it is derived
from, or when a staging script writes something other than what the profile says.
They need numpy, PyYAML and OpenCV (any of the conda environments the runners use).
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
DATASETS = ('euroc_mav', 'rosariov2', 'hortimulti', 'zed2i')


def load(name):
    spec = importlib.util.spec_from_file_location(name, REPO / 'scripts/run' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def profile(dataset):
    return json.loads((REPO / 'configs/sensors' / f'{dataset}.json').read_text())


def fake_sequence(root, camera_ns, imu_ns):
    for cam in ('cam0', 'cam1'):
        (root / 'mav0' / cam / 'data').mkdir(parents=True)
        lines = ['#timestamp [ns],filename']
        for t in camera_ns:
            (root / 'mav0' / cam / 'data' / f'{t}.png').write_bytes(b'')
            lines.append(f'{t},{t}.png')
        (root / 'mav0' / cam / 'data.csv').write_text('\n'.join(lines) + '\n')
    (root / 'mav0/imu0').mkdir(parents=True)
    (root / 'mav0/imu0/data.csv').write_text(
        '#t,wx,wy,wz,ax,ay,az\n' + ''.join(f'{t},0.01,0.02,0.03,0.1,0.2,9.8\n' for t in imu_ns))
    return root


def test_profiles_match_reference_configs():
    result = subprocess.run([sys.executable, str(REPO / 'scripts/setup/build_sensor_profiles.py'),
                             '--repo', str(REPO), '--check'], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize('dataset', DATASETS)
def test_profile_is_self_consistent(dataset):
    p = profile(dataset)
    t = np.array(p['T_cam0_cam1'])
    assert abs(np.linalg.norm(t[:3, 3]) - p['baseline_m']) < 1e-9
    assert t[0, 3] > 0, 'cam1 must be the right camera'
    assert abs(np.linalg.det(np.array(p['imu']['T_imu_cam0'])[:3, :3]) - 1) < 1e-4
    assert p['rectified_input'] == all(c['distortion_model'] == 'none' for c in p['cameras'])


@pytest.mark.parametrize('dataset,offset_ms', [('hortimulti', 9.160379), ('zed2i', 0.0)])
def test_svo_pro_stage_follows_profile_and_trims_to_imu(tmp_path, dataset, offset_ms):
    stage = load('_svo_pro_stage')
    p = profile(dataset)
    camera = [1_000_000_000 + i * 100_000_000 for i in range(20)]
    # IMU starts 0.25 s after the first image and stops 0.15 s before the last one.
    imu = list(range(camera[0] + 250_000_000, camera[-1] - 150_000_000, 5_000_000))
    sequence = fake_sequence(tmp_path / 'seq', camera, imu)
    okvis = next((REPO / 'configs/okvis2').glob(f'{dataset}_*_vio.yaml'))
    out = tmp_path / 'stage'
    args = type('A', (), dict(sequence=sequence, sensor=REPO / 'configs/sensors' / f'{dataset}.json',
                              imu_params=f'okvis2:{okvis}', out=out, max_frames=0))
    stage.stage(args)
    calib = yaml.safe_load((out / 'calib.yaml').read_text())
    record = json.loads((out / 'stage.json').read_text())

    t_b_c0 = np.array(calib['cameras'][0]['T_B_C']['data']).reshape(4, 4)
    t_b_c1 = np.array(calib['cameras'][1]['T_B_C']['data']).reshape(4, 4)
    assert np.allclose(t_b_c0, np.array(p['imu']['T_imu_cam0']), atol=1e-4)
    assert abs(np.linalg.norm((np.linalg.inv(t_b_c0) @ t_b_c1)[:3, 3]) - p['baseline_m']) < 1e-6
    assert np.allclose(t_b_c0[:3, :3].T @ t_b_c0[:3, :3], np.eye(3), atol=1e-12)
    assert calib['cameras'][0]['camera']['intrinsics']['data'] == [
        p['cameras'][0][k] for k in ('fx', 'fy', 'cx', 'cy')]

    # IMU on the camera clock: first staged stamp = (t_imu - offset) - first camera stamp.
    first = float((out / 'data/imu.txt').read_text().splitlines()[1].split()[1])
    assert abs(first - (0.25 - offset_ms / 1e3)) < 1e-6
    # Inertial run types only use frames that have IMU samples on both sides.
    shifted = [t - record['imu_time_offset_ns'] for t in imu]
    assert camera[record['first_frame_with_imu']] > shifted[1] >= camera[record['first_frame_with_imu'] - 1]
    assert camera[record['end_frame_with_imu'] - 1] < shifted[-2] <= camera[record['end_frame_with_imu']]


def test_mast3r_fusion_stage_follows_profile(tmp_path):
    stage = load('_mast3r_fusion_stage')
    p = profile('hortimulti')
    camera = [1_000_000_000 + i * 100_000_000 for i in range(5)]
    imu = list(range(camera[0], camera[-1], 5_000_000))
    sequence = fake_sequence(tmp_path / 'seq', camera, imu)
    out = tmp_path / 'stage'
    stage.stage(type('A', (), dict(sequence=sequence, sensor=REPO / 'configs/sensors/hortimulti.json', out=out)))
    intr = yaml.safe_load((out / 'intrinsics.yaml').read_text())
    cam = p['cameras'][0]
    assert intr['calibration'] == [cam['fx'], cam['fy'], cam['cx'], cam['cy'], 0.0, 0.0, 0.0, 0.0]
    assert np.allclose(np.array(intr['Tic']), np.array(p['imu']['T_imu_cam0']), atol=1e-4)
    first = int((out / 'mav0/imu0/data.csv').read_text().splitlines()[1].split(',')[0])
    assert first == imu[0] - int(round(p['camera_imu_time_offset_s'] * 1e9))


def test_dsol_rectification_keeps_the_profile_baseline():
    pytest.importorskip('cv2')
    stage = load('_dsol_stage')
    p = profile('euroc_mav')
    _, r0, p0, baseline = stage.rectification(p)
    assert abs(baseline - p['baseline_m']) < 1e-6
    assert abs(np.linalg.det(r0) - 1) < 1e-9 and p0[0, 0] == p0[1, 1]
