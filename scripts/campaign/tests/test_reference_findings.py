import hashlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import protocol_findings as findings


def fixture(tmp_path, monkeypatch):
    relative = 'vio/rosariov2/sequence1/openvins/run1'
    run = tmp_path / 'results' / relative
    run.mkdir(parents=True)
    artifacts = []
    for role, text in [('estimator_config', 'calib_cam_extrinsics: false\n'),
                       ('camera_imu_calibration', 'reviewed identity profile\n')]:
        path = run / (role + '.yaml')
        path.write_text(text)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        artifacts.append(dict(role=role, snapshot=path.name, snapshot_sha256=digest))
    monkeypatch.setitem(findings.ROSARIO_IDENTITY_PROFILES, 'openvins',
                        ('camera_imu_calibration', artifacts[1]['snapshot_sha256']))
    return relative, dict(provenance=dict(artifacts=artifacts)), run


def test_identity_finding_requires_verified_saved_profile(tmp_path, monkeypatch):
    relative, meta, run = fixture(tmp_path, monkeypatch)
    result = findings.historical_findings(tmp_path, relative, meta)
    assert [r['code'] for r in result] == ['rosario_identity_camera_imu_extrinsic']
    (run / 'camera_imu_calibration.yaml').write_text('changed since run\n')
    assert findings.historical_findings(tmp_path, relative, meta) == []


def test_changed_spatial_calibration_policy_is_not_inferred_from_old_profile(tmp_path, monkeypatch):
    relative, meta, run = fixture(tmp_path, monkeypatch)
    path = run / 'estimator_config.yaml'
    path.write_text('calib_cam_extrinsics: true\n')
    meta['provenance']['artifacts'][0]['snapshot_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert findings.historical_findings(tmp_path, relative, meta) == []


def test_visual_only_virtual_body_is_not_an_inertial_defect(tmp_path, monkeypatch):
    relative, meta, run = fixture(tmp_path, monkeypatch)
    visual = relative.replace('vio/', 'vo/', 1)
    target = tmp_path / 'results' / visual
    target.parent.mkdir(parents=True)
    run.rename(target)
    assert findings.historical_findings(tmp_path, visual, meta) == []


def test_native_log_finding_requires_unchanged_log_even_without_metadata(tmp_path):
    import json
    relative = 'gnss-vio/rosariov2/sequence1/okvis2x/run1'
    log = tmp_path / 'results' / relative / 'run_log.txt'
    log.parent.mkdir(parents=True)
    log.write_text('r_SA: 0 0 0\n')
    review = tmp_path / 'docs/campaigns/gnss-lever-findings-20261001.json'
    review.parent.mkdir(parents=True)
    review.write_text(json.dumps({'attempts': {relative: {
        'log': {'path': str(log.relative_to(tmp_path)),
                'sha256': hashlib.sha256(log.read_bytes()).hexdigest()},
        'code': 'gnss_zero_antenna_lever_arm_in_native_log',
        'disposition': 'required_rerun', 'prerequisite': 'review_lever', 'evidence': []}}}))
    assert findings.historical_findings(tmp_path, relative, {})[0]['disposition'] == 'required_rerun'
    log.write_text('r_SA: changed\n')
    assert findings.historical_findings(tmp_path, relative, {}) == []


def test_time_offset_finding_requires_both_saved_configuration_and_source(tmp_path):
    import json
    relative = 'vio/hortimulti/strawberry02/okvis2/run1'
    run = tmp_path / 'results' / relative
    run.mkdir(parents=True)
    path = run / 'config.yaml'
    path.write_text('camera_parameters:\n    image_delay: 0.0\n')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    source = dict(role='algorithm', commit='historical-source', dirty=False)
    review = tmp_path / 'docs/campaigns/horti-time-offset-findings-20261001.json'
    review.parent.mkdir(parents=True)
    review.write_text(json.dumps({'attempts': {relative: {
        'role': 'estimator_config', 'config_sha256': digest, 'algorithm_source': source,
        'code': 'horti_camera_imu_time_offset_uncompensated',
        'disposition': 'required_rerun', 'prerequisite': 'review_time', 'evidence': []}}}))
    meta = {'provenance': {'sources': [source], 'artifacts': [
        dict(role='estimator_config', snapshot=path.name, snapshot_sha256=digest)]}}
    assert findings.historical_findings(tmp_path, relative, meta)[0]['disposition'] == 'required_rerun'
    source['dirty'] = True
    assert findings.historical_findings(tmp_path, relative, meta) == []


def test_matched_levers_close_physical_frame_chains():
    import json
    import numpy as np
    repo = Path(__file__).resolve().parents[3]
    record = json.loads((repo / 'docs/campaigns/gnss-lever-calibration-20261001.json').read_text())
    r = record['rosariov2']; c = {k: np.array(v) for k, v in r['components'].items()}
    actual = c['T_box_screw'] @ c['T_screw_left'] @ c['T_left_imu'] @ r['T_imu_gps']
    np.testing.assert_allclose(actual, c['T_box_gps'], atol=1e-10)
    np.testing.assert_allclose(np.array(r['T_imu_gps'])[:3, 3], r['author_gnss_v2_rounded_t_b_g'], atol=5e-4)
    h = record['hortimulti']; c = {k: np.array(v) for k, v in h['components'].items()}
    actual = c['T_base_mount'] @ c['T_mount_os'] @ np.linalg.inv(c['T_imu_os']) @ h['T_imu_gps']
    np.testing.assert_allclose(actual, c['T_base_gps'], atol=1e-10)
    # Reusing base_link's antenna translation as an IMU lever cannot close this chain.
    assert np.linalg.norm(np.array(h['T_imu_gps'])[:3, 3] - c['T_base_gps'][:3, 3]) > .9
