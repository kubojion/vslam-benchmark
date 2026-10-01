import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _pose_frames import (FrameEvidenceError, Snapshots, matrix, okvis_final_extrinsic,
                          read_yaml, rectified_to_raw, physical_rosario_imu_to_camera,
                          estimate_transform)


def test_saved_config_hash_is_required(tmp_path):
    p = tmp_path / 'effective.yaml'; p.write_text('x: 1\n')
    artifact = {'role': 'estimator_config', 'snapshot': p.name,
                'snapshot_sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
    snapshots = Snapshots(tmp_path, {'provenance': {'artifacts': [artifact]}}, tmp_path)
    assert snapshots.read('estimator_config')['x'] == 1
    p.write_text('x: 2\n')
    with pytest.raises(FrameEvidenceError, match='hash'):
        snapshots.read('estimator_config')


def test_current_config_is_not_a_historical_snapshot(tmp_path):
    (tmp_path/'estimator_config.yaml').write_text('x: 1\n')
    with pytest.raises(FrameEvidenceError, match='found 0'):
        Snapshots(tmp_path, {}, tmp_path).read('estimator_config')


def test_read_opencv_matrix_and_reject_reflection(tmp_path):
    p = tmp_path/'camera.yaml'
    p.write_text('%YAML:1.0\nT: !!opencv-matrix\n  rows: 4\n  cols: 4\n  data: '+json.dumps(np.eye(4).reshape(-1).tolist()))
    np.testing.assert_allclose(matrix(read_yaml(p)['T']), np.eye(4))
    t = np.eye(4); t[0, 0] = -1
    with pytest.raises(FrameEvidenceError, match='reflection'):
        matrix(t)


def test_rectification_transform_direction():
    k = np.array([[400, 0, 320], [0, 400, 240], [0, 0, 1.]])
    t = np.eye(4); t[:3, :3] = Rotation.from_euler('z', .1).as_matrix(); t[:3, 3] = [-.1, .01, 0]
    rect_to_raw = rectified_to_raw(k, [0]*5, k, [0]*5, [640, 480], t)
    # Right camera centre expressed in raw-left axes becomes horizontal in the
    # rectified-left coordinate system. Using R1 inverse would fail this test.
    centre = np.linalg.inv(t)[:3, 3]
    in_rectified = rect_to_raw[:3, :3] @ centre
    assert abs(in_rectified[1]) < 1e-12 and abs(in_rectified[2]) < 1e-12


def test_saved_final_extrinsics_require_matching_final_trajectory(tmp_path):
    path = tmp_path/'okvis2-slam-final_map.g2o'
    path.write_text('FRAME 1 0 1 .1 .2 .3 0 0 0 1 1000000000\nFRAME 2 0 1 .1 .2 .3 0 0 0 1 2000000000\n')
    csv = tmp_path/'okvis2-slam-final-ba_trajectory.csv'
    csv.write_text('header\n1000000000,0,0,0,0,0,0,1\n2000000000,1,0,0,0,0,0,1\n')
    selected = tmp_path/'trajectory.txt'; selected.write_text('1 0 0 0 0 0 0 1\n2 1 0 0 0 0 0 1\n')
    snapshots = Snapshots(tmp_path, {}, tmp_path)
    np.testing.assert_allclose(okvis_final_extrinsic(snapshots)[:3, 3], [.1, .2, .3])
    selected.write_text('1 0 0 0 0 0 0 1\n2 2 0 0 0 0 0 1\n')
    with pytest.raises(FrameEvidenceError, match='does not match'):
        okvis_final_extrinsic(snapshots)


def test_physical_rosario_frame_is_independent_of_wrong_estimator_extrinsic(tmp_path):
    path = tmp_path / 'docs/campaigns/rosario-reference-calibration-20261001.json'
    path.parent.mkdir(parents=True)
    t = np.eye(4)
    t[:3, :3] = Rotation.from_euler('xyz', [.01, -.02, .03]).as_matrix()
    t[:3, 3] = [.04, -.02, .03]
    path.write_text(json.dumps(dict(dataset='rosariov2', sequences=['sequence1'],
                                    T_imu_left=t.tolist())))
    calibration = tmp_path / 'saved.json'
    calibration.write_text(json.dumps({'value0': {'T_imu_cam': [dict(
        px=0, py=0, pz=0, qx=0, qy=0, qz=0, qw=1)]}}))
    meta = {'provenance': {'artifacts': [dict(role='camera_calibration',
        snapshot=calibration.name, snapshot_sha256=hashlib.sha256(calibration.read_bytes()).hexdigest())]}}
    snapshots = Snapshots(tmp_path, meta, tmp_path)
    _, inertial, _ = estimate_transform(tmp_path, 'rosariov2', 'sequence1', 'basalt', True, snapshots)
    _, visual, _ = estimate_transform(tmp_path, 'rosariov2', 'sequence1', 'basalt', False, snapshots)
    np.testing.assert_allclose(inertial, t)
    np.testing.assert_allclose(visual, np.eye(4))
    assert any(e['path'] == str(path.relative_to(tmp_path)) for e in snapshots.evidence)
    with pytest.raises(FrameEvidenceError, match='recording'):
        physical_rosario_imu_to_camera(tmp_path, 'unreviewed_sequence', snapshots)
