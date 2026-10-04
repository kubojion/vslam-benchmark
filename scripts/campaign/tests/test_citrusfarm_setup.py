"""CitrusFarm configs follow the authors' calibration, the recorded images and one profile.

Fails when a generated config, the sensor profile or the evaluator's physical calibration
drifts from the authors' Kalibr chain (configs/sensors/sources/citrusfarm), or when a
sequence's recorded camera model or clock shift disagrees with what the configs assume.
"""
import json
import re
from pathlib import Path

import numpy as np
import pytest
import yaml
from scipy.spatial.transform import Rotation

REPO = Path(__file__).resolve().parents[3]
SOURCES = REPO / 'configs/sensors/sources/citrusfarm'
PROFILE = json.loads((REPO / 'configs/sensors/citrusfarm.json').read_text())
SEQUENCES = ('seq04', 'seq07')


def opencv_yaml(path):
    return yaml.safe_load('\n'.join(l for l in path.read_text().splitlines() if not l.startswith('%YAML')))


def kalibr_chain():
    imu_cam = yaml.safe_load((SOURCES / '02-imu-cam-result.yaml').read_text())['cam0']['T_cam_imu']
    multi = yaml.safe_load((SOURCES / '01-multi-cam-result.yaml').read_text())['cam1']['T_cn_cnm1']
    return np.linalg.inv(np.array(multi) @ np.array(imu_cam))


def profile_poses():
    t0 = np.array(PROFILE['imu']['T_imu_cam0'])
    return t0, t0 @ np.array(PROFILE['T_cam0_cam1'])


def test_profile_and_physical_record_are_the_inverse_kalibr_chain():
    chain = kalibr_chain()
    t0, _ = profile_poses()
    assert np.degrees(Rotation.from_matrix(chain[:3, :3].T @ t0[:3, :3]).magnitude()) < 1e-6
    assert np.allclose(chain[:3, 3], t0[:3, 3], atol=1e-9)
    record = json.loads((REPO / 'docs/campaigns/citrusfarm-physical-calibration-20261003.json').read_text())
    assert np.allclose(record['T_imu_left'], t0, atol=1e-9) and record['sequences'] == list(SEQUENCES)
    for check in record['independent_checks'].values():
        assert check['gyro_rotation_vs_kalibr_chain_deg'] < 1.0 and abs(check['offset_after_shift_s']) < 5e-4


@pytest.mark.parametrize('sequence', SEQUENCES)
def test_recorded_camera_model_and_clock(sequence):
    manifest = json.loads((REPO / 'datasets/citrusfarm' / sequence / 'manifest.json').read_text())
    left, right = manifest['camera_info']['left'], manifest['camera_info']['right']
    cam = PROFILE['cameras'][0]
    assert abs(left['k'][0] - cam['fx']) < 0.2 and abs(left['k'][2] - cam['cx']) < 0.2 and abs(left['k'][5] - cam['cy']) < 0.2
    assert abs(-right['p'][3] / right['p'][0] - PROFILE['baseline_m']) < 1e-5
    assert (left['width'], left['height']) == (PROFILE['image']['width'], PROFILE['image']['height'])
    assert 'camera_clock_shift_s' in manifest['imu'] and PROFILE['camera_imu_time_offset_s'] == 0.0


def check(t0, t1):
    e0, e1 = profile_poses()
    assert np.allclose(t0, e0, atol=1e-9) and np.allclose(t1, e1, atol=1e-9)


def test_inertial_configs_carry_the_profile():
    camera = opencv_yaml(REPO / 'configs/airslam/citrusfarm_camera_vio.yaml')
    check(*(np.array(camera[c]['T'], dtype=float) for c in ('cam0', 'cam1')))
    chain = opencv_yaml(REPO / 'configs/openvins/citrusfarm/kalibr_imucam_chain.yaml')
    check(*(np.array(chain[c]['T_imu_cam'], dtype=float) for c in ('cam0', 'cam1')))
    voxel = yaml.safe_load((REPO / 'configs/voxel_svio/citrusfarm.yaml').read_text())['camera_parameter']
    check(*(np.array(voxel[f'T_imu_cam_{s}'], dtype=float).reshape(4, 4) for s in ('left', 'right')))
    assert voxel['timeshift_cam_imu_left'] == voxel['timeshift_cam_imu_right'] == 0.0
    imu = opencv_yaml(REPO / 'configs/openvins/citrusfarm/kalibr_imu_chain.yaml')['imu0']
    assert imu['update_rate'] == 200.0 and imu['time_offset'] == 0.0


def test_every_inertial_estimator_uses_the_one_citrusfarm_imu_profile():
    """Recording-derived densities with the authors' Allan random walks, as for ZED2i (decided 2026-10-04)."""
    noise = json.loads((REPO / 'docs/campaigns/citrusfarm-imu-noise-20261003.json').read_text())['datasets']['citrusfarm']['recommended']
    allan = yaml.safe_load((SOURCES / 'microstrain_gx5.yaml').read_text())
    assert (noise['sigma_gw_c'], noise['sigma_aw_c']) == (allan['gyroscope_random_walk'], allan['accelerometer_random_walk'])
    expected = (noise['sigma_g_c'], noise['sigma_a_c'], noise['sigma_gw_c'], noise['sigma_aw_c'])
    kalibr = ('gyroscope_noise_density', 'accelerometer_noise_density', 'gyroscope_random_walk', 'accelerometer_random_walk')
    found = {'sensor profile': [PROFILE['imu'][k] for k in kalibr]}
    for name in ('citrusfarm_stereo_inertial', 'citrusfarm_stereo_inertial_lc'):
        text = (REPO / f'configs/orbslam3/{name}.yaml').read_text()   # !!opencv-matrix: read the scalars directly
        found[name] = [float(re.search(rf'(?m)^{re.escape(k)}:\s*([0-9.eE+-]+)', text).group(1))
                       for k in ('IMU.NoiseGyro', 'IMU.NoiseAcc', 'IMU.GyroWalk', 'IMU.AccWalk')]
    found['openvins'] = [opencv_yaml(REPO / 'configs/openvins/citrusfarm/kalibr_imu_chain.yaml')['imu0'][k] for k in kalibr]
    voxel = yaml.safe_load((REPO / 'configs/voxel_svio/citrusfarm.yaml').read_text())['imu_parameter']
    found['voxel_svio'] = [voxel[k] for k in kalibr]
    airslam = opencv_yaml(REPO / 'configs/airslam/citrusfarm_camera_vio.yaml')
    found['airslam'] = [airslam[k] for k in kalibr]
    basalt = json.loads((REPO / 'configs/basalt/citrusfarm_calib.json').read_text())['value0']
    found['basalt'] = [basalt[k][0] for k in ('gyro_noise_std', 'accel_noise_std', 'gyro_bias_std', 'accel_bias_std')]
    for name, values in found.items():
        assert values == pytest.approx(expected, rel=1e-6), name


@pytest.mark.parametrize('sequence', SEQUENCES)
def test_okvis_files_use_the_recording_envelope_and_zero_delay(sequence):
    noise = json.loads((REPO / 'docs/campaigns/citrusfarm-imu-noise-20261003.json').read_text())['datasets']['citrusfarm']
    for algorithm, modes in (('okvis2', ('vio', 'vo', 'vo_lc')), ('okvis2x', ('vio', 'vio_lc', 'vo', 'vo_lc'))):
        for mode in modes:
            cfg = opencv_yaml(REPO / f'configs/{algorithm}/citrusfarm_{sequence}_{mode}.yaml')
            assert cfg['imu_parameters']['sigma_a_c'] == noise['recommended']['sigma_a_c']
            assert np.allclose(cfg['imu_parameters']['g0'], noise['sequences'][sequence]['gyro_bias_rad_s'], atol=1e-9)
            assert cfg['camera_parameters']['image_delay'] == 0.0
            check(*(np.array(c['T_SC'], dtype=float).reshape(4, 4) for c in cfg['cameras']))


def test_references_are_selected_for_both_sequences():
    import sys
    sys.path.insert(0, str(REPO / 'scripts/eval'))
    from _reference_source import selected_reference
    for sequence in SEQUENCES:
        reference = selected_reference(REPO, 'citrusfarm', sequence)
        assert reference['orientation_valid'] is False and len(reference['valid_intervals']) == 1
