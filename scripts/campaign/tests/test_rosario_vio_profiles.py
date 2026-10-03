"""The Rosario VIO rerun configs carry the decided camera-IMU transform (2026-10-03).

Decision: the authors' published Kalibr result (0.365 deg, 33.9 mm, in
configs/sensors/rosariov2.json) for every algorithm, the authors' ORB-SLAM3 camera model,
time offset 0. These tests fail if a Basalt, OpenVINS, Voxel-SVIO or AirSLAM Rosario VIO
file drifts from the shared profile or falls back to the historical identity transform.
"""
import json
from pathlib import Path

import numpy as np
import yaml
from scipy.spatial.transform import Rotation

REPO = Path(__file__).resolve().parents[3]
PROFILE = json.loads((REPO / 'configs/sensors/rosariov2.json').read_text())


def opencv_yaml(path):
    return yaml.safe_load('\n'.join(l for l in path.read_text().splitlines() if not l.startswith('%YAML')))


def expected():
    t0 = np.array(PROFILE['imu']['T_imu_cam0'], dtype=float)
    u, _, vt = np.linalg.svd(t0[:3, :3])
    t0[:3, :3] = u @ vt
    return t0, t0 @ np.array(PROFILE['T_cam0_cam1'], dtype=float)


def check(t0, t1):
    e0, e1 = expected()
    assert np.allclose(t0, e0, atol=1e-9) and np.allclose(t1, e1, atol=1e-9)
    assert abs(np.degrees(Rotation.from_matrix(t0[:3, :3]).magnitude()) - 0.365) < 0.001
    assert abs(np.linalg.norm(t0[:3, 3]) - 0.0339) < 0.0001
    assert abs(np.linalg.norm((np.linalg.inv(t0) @ t1)[:3, 3]) - PROFILE['baseline_m']) < 1e-9


def test_basalt():
    calib = json.loads((REPO / 'configs/basalt/rosariov2_calib.json').read_text())['value0']
    def pose(d):
        t = np.eye(4)
        t[:3, :3] = Rotation.from_quat([d['qx'], d['qy'], d['qz'], d['qw']]).as_matrix()
        t[:3, 3] = [d['px'], d['py'], d['pz']]
        return t
    check(*(pose(d) for d in calib['T_imu_cam']))
    assert calib['cam_time_offset_ns'] == 0


def test_openvins():
    chain = opencv_yaml(REPO / 'configs/openvins/rosariov2/kalibr_imucam_chain.yaml')
    check(*(np.array(chain[c]['T_imu_cam'], dtype=float) for c in ('cam0', 'cam1')))
    imu = opencv_yaml(REPO / 'configs/openvins/rosariov2/kalibr_imu_chain.yaml')
    assert imu['imu0']['time_offset'] == 0.0


def test_voxel_svio():
    camera = yaml.safe_load((REPO / 'configs/voxel_svio/rosariov2.yaml').read_text())['camera_parameter']
    check(*(np.array(camera[f'T_imu_cam_{s}'], dtype=float).reshape(4, 4) for s in ('left', 'right')))
    assert camera['timeshift_cam_imu_left'] == camera['timeshift_cam_imu_right'] == 0.0


def test_airslam():
    # T_type 0: T is T_bc, the camera pose in the IMU body frame (src/airslam/src/camera.cc).
    camera = opencv_yaml(REPO / 'configs/airslam/rosariov2_camera_vio.yaml')
    assert camera['cam0']['T_type'] == camera['cam1']['T_type'] == 0
    check(*(np.array(camera[c]['T'], dtype=float) for c in ('cam0', 'cam1')))


def test_camera_model_is_the_authors_orb_profile():
    cam = PROFILE['cameras'][0]
    assert (cam['fx'], cam['fy'], PROFILE['baseline_m']) == (648.8624169653789, 648.8624169653789, 0.0497336941)
    assert PROFILE['camera_imu_time_offset_s'] == 0.0
