import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _metrics import apply_alignment, fit_alignment, relative_errors, right_transform
from _trajectory_evaluation import evaluate_arrays


def curve():
    t = np.arange(201) / 20
    angle = t / 2
    return np.c_[t, 3*np.cos(angle), 3*np.sin(angle), .1*t,
                 Rotation.from_euler('z', angle).as_quat()]


def frames(**overrides):
    return dict(estimate_transform=np.eye(4), reference_transform=np.eye(4),
                orientation_valid=True, common_origin_verified=True) | overrides


def test_frame_conversion_recovers_rotating_lever_arm():
    g = curve()
    t = np.eye(4); t[:3, 3] = [1, 2, -.3]
    camera = right_transform(g, t)
    out, _ = evaluate_arrays(g, camera, g[:, 0], frames(reference_transform=t))
    assert out['ate_se3']['rmse'] < 1e-12
    assert out['rpe_trans_1m_se3']['rmse'] < 1e-12
    wrong, _ = evaluate_arrays(g, camera, g[:, 0], frames())
    assert wrong['ate_se3']['rmse'] > .2


def test_invalid_reference_rotation_withholds_relative_pose_metrics():
    g = curve()
    out, _ = evaluate_arrays(g, g, g[:, 0], frames(orientation_valid=False))
    assert out['ate_se3']['rmse'] < 1e-12
    assert out['rpe_rot_1m_deg']['rmse'] is None
    assert out['rpe_trans_1m_se3']['rmse'] is None
    assert out['displacement_magnitude_error_1m']['se3']['rmse'] < 1e-12


def test_unknown_origin_cannot_produce_valid_full_pose_metrics():
    g = curve()
    out, _ = evaluate_arrays(g, g, g[:, 0], frames(common_origin_verified=False))
    assert out['metric_validity']['position'] == 'provisional_sensor_origin'
    assert out['rpe_trans_1m_se3']['rmse'] is None


def test_keyframes_remain_sparse_and_are_not_tracking_loss():
    g = curve()
    out, paired = evaluate_arrays(g, g[::10], g[:, 0], frames(), sparse_export=True)
    assert out['n_pairs_ate'] == 21
    assert len(paired['estimate']) == 21
    assert out['coverage']['coverage_gap_pct'] is None
    assert out['coverage']['camera_pose_coverage_pct'] < 11
    assert out['coverage']['export_span_pct'] == 100


def test_monocular_scale_is_not_misclassified_as_metric_collapse():
    g = curve(); e = g.copy(); e[:, 1:4] *= 100
    mono, _ = evaluate_arrays(g, e, g[:, 0], frames(), monocular=True)
    stereo, _ = evaluate_arrays(g, e, g[:, 0], frames())
    assert mono['run_status'] == 'ok'
    assert mono['ate']['rmse'] < 1e-12
    assert stereo['run_status'] == 'scale_collapse'
    assert stereo['ate_se3']['rmse'] > 1


def test_monocular_metric_lever_arm_rejected():
    g = curve(); t = np.eye(4); t[0, 3] = 1
    with pytest.raises(ValueError, match='unscaled monocular'):
        evaluate_arrays(g, g, g[:, 0], frames(estimate_transform=t), monocular=True)


def test_gnss_translation_diagnostic_does_not_become_verified_global_accuracy():
    g = curve()
    e = apply_alignment(g, (Rotation.from_euler('z', np.pi/2).as_matrix(), [3, 4, 0], 1))
    out, _ = evaluate_arrays(g, e, g[:, 0], frames(), gnss=True)
    assert out['ate_se3']['rmse'] < 1e-12
    assert out['ate_translation_only_diagnostic']['rmse'] > 1
    assert out['ate_origin'] == {}
    assert out['metric_validity']['global_gnss_accuracy'] == 'unverified_global_frame'


def test_no_supported_pairs_returns_explicit_failure():
    g = curve(); e = g.copy(); e[:, 0] += 100
    out, _ = evaluate_arrays(g, e, g[:, 0], frames())
    assert out['run_status'] == 'eval_failed'
    assert out['ate']['rmse'] is None


def test_compare_se3_and_sim3_with_independent_evo_implementation():
    evo_geometry = pytest.importorskip('evo.core.geometry')
    g = curve(); e = g.copy()
    e[:, 1:4] = e[:, 1:4] @ Rotation.from_euler('xyz', [.2, .5, .3]).as_matrix().T * 1.4 + [1, 5, 7]
    e[:, 1] += .04*np.sin(e[:, 0]*3)
    for correct_scale in (False, True):
        actual = fit_alignment(e[:, 1:4], g[:, 1:4], correct_scale)
        expected = evo_geometry.umeyama_alignment(e[:, 1:4].T, g[:, 1:4].T, with_scale=correct_scale)
        for a, b in zip(actual, expected):
            np.testing.assert_allclose(a, b, atol=1e-12)


def test_compare_full_relative_pose_residuals_with_evo():
    metrics = pytest.importorskip('evo.core.metrics')
    trajectory = pytest.importorskip('evo.core.trajectory')
    units = pytest.importorskip('evo.core.units')
    g = curve(); e = g.copy()
    e[:, 2] += .1*np.sin(e[:, 0]*3)
    e[:, 4:] = (Rotation.from_euler('x', .1*np.sin(e[:, 0])) * Rotation.from_quat(e[:, 4:])).as_quat()
    pairs = np.c_[np.arange(len(g)-1), np.arange(1, len(g))]
    trans, angle, displacement = relative_errors(g, e, pairs)
    def to_evo(a):
        return trajectory.PoseTrajectory3D(positions_xyz=a[:, 1:4],
                orientations_quat_wxyz=a[:, [7, 4, 5, 6]], timestamps=a[:, 0])
    for relation, expected in [(metrics.PoseRelation.translation_part, trans),
                               (metrics.PoseRelation.rotation_angle_deg, angle),
                               (metrics.PoseRelation.point_distance, displacement)]:
        metric = metrics.RPE(pose_relation=relation, delta=1, delta_unit=units.Unit.frames, all_pairs=True)
        metric.process_data((to_evo(g), to_evo(e)))
        np.testing.assert_allclose(metric.error, expected, atol=1e-9)


def test_ground_truth_gaps_do_not_become_exported_pose_gaps():
    g=curve();reference=g[(g[:,0]>=1)&~((g[:,0]>4)&(g[:,0]<5))]
    out,_=evaluate_arrays(reference,g,g[:,0],frames())
    coverage=out['coverage']
    assert coverage['camera_pose_coverage_pct']==100
    assert coverage['coverage_gap_pct']==100
    assert coverage['associated_camera_frames']==len(g)
    assert coverage['reference_paired_camera_frames']<len(g)
    assert coverage['reference_pairs_pct_of_input']<100
    assert out['ate_se3']['rmse']<1e-12


def test_tolerance_boundary_cannot_make_export_span_exceed_sequence():
    g=curve();estimate=g.copy();estimate[0,0]-=.001;estimate[-1,0]+=.001
    out,_=evaluate_arrays(g,estimate,g[:,0],frames())
    assert out['coverage']['export_span_pct']==100
    assert out['coverage']['coverage_gap_pct']==100


def test_nonfinite_sensor_transform_and_camera_grid_are_rejected():
    from _metrics import camera_association
    g=curve();t=np.eye(4);t[0,3]=np.nan
    with pytest.raises(ValueError,match='homogeneous'):right_transform(g,t)
    for times in (np.array([0.,np.nan]),np.array([[0.,1.]])):
        with pytest.raises(ValueError,match='camera timestamps'):camera_association(g,times)
    with pytest.raises(ValueError,match='tolerance'):camera_association(g,g[:,0],np.nan)


def test_invalid_orientation_can_only_yield_explicit_position_diagnostic():
    from _trajectory_evaluation import position_only_diagnostic
    g=curve();broken=g.copy();broken[:,4:]*=1.5
    diag=position_only_diagnostic(g,broken,g[:,0],frames())
    assert diag['status']=='position_diagnostic_only'
    assert diag['ate_se3']['rmse']<1e-12
    assert diag['saved_orientations_valid'] is False
    assert diag['publication_qualified'] is False
    assert np.allclose(np.linalg.norm(broken[:,4:],axis=1),1.5)
    transform=np.eye(4);transform[0,3]=1
    assert position_only_diagnostic(g,broken,g[:,0],frames(estimate_transform=transform)) is None
    broken[0,0]=broken[1,0]
    assert position_only_diagnostic(g,broken,g[:,0],frames()) is None
