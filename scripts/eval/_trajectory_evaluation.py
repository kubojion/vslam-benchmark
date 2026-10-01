"""Schema-3 numerical evaluation on actual saved poses, without estimator runs."""
from __future__ import annotations

import numpy as np

from _metrics import (apply_alignment, camera_association, distance_pairs,
                      fit_alignment, interpolate_reference, relative_errors,
                      right_transform, statistics, translation_origin_errors,
                      validate_poses)


def evaluate_arrays(reference, estimate, camera_times, frames, *, monocular=False,
                    sparse_export=False, gnss=False, tolerance_s=0.005,
                    reference_max_gap_s=0.5):
    """Return JSON-ready metrics and paired arrays for independent verification.

    Missing frame evidence permits clearly provisional position diagnostics only.
    It never permits full relative-pose errors or publication qualification.
    The reference is interpolated; the estimator output is never interpolated.
    """
    g, e = validate_poses(reference), validate_poses(estimate)
    camera_times = np.asarray(camera_times, dtype=float)
    sampled, camera_ids, dt = camera_association(e, camera_times, tolerance_s)
    reference_at_est, support = interpolate_reference(g, sampled[:, 0], reference_max_gap_s)
    sampled, camera_ids, dt = sampled[support], camera_ids[support], dt[support]
    _, camera_support = interpolate_reference(g, camera_times, reference_max_gap_s)
    if frames.get('estimate_transform') is not None:
        t = np.asarray(frames['estimate_transform'])
        if monocular and not np.allclose(t[:3, 3], 0):
            raise ValueError('a metric lever arm cannot be applied to unscaled monocular poses')
        sampled = right_transform(sampled, t)
    if frames.get('reference_transform') is not None:
        reference_at_est = right_transform(reference_at_est, frames['reference_transform'])
    rotations_valid = bool(frames.get('orientation_valid') and frames.get('common_origin_verified'))
    missing = statistics([])
    out = {
        'eval_schema': 3,
        'n_pairs_ate': len(sampled),
        'run_status': 'eval_failed',
        'ate': dict(missing), 'ate_se3': dict(missing), 'ate_origin': {},
        'rpe_trans_1m': dict(missing), 'rpe_trans_1m_se3': dict(missing),
        'rpe_rot_1m_deg': dict(missing),
        'displacement_magnitude_error_1m': {}, 'window_drift': {},
        'scale_factor': None, 'final_drift_m': None, 'final_drift_sim3_m': None,
        'primary_alignment': 'sim3' if monocular else 'se3',
        'metric_validity': {
            'position': 'common_camera_origin' if frames.get('common_origin_verified') else 'provisional_sensor_origin',
            'relative_pose': 'available' if rotations_valid else 'unavailable_frame_or_orientation',
            'global_gnss_accuracy': 'unverified_global_frame' if gnss else 'not_applicable',
        },
        'metric_protocol': {
            'name': 'camera_association_common_origin_v3',
            'pose_convention': 'T_world_sensor; Hamilton xyzw',
            'association': 'one actual estimate per camera timestamp; reference interpolated at estimate time',
            'association_tolerance_s': tolerance_s,
            'reference_max_gap_s': reference_max_gap_s,
            'estimate_interpolation': False,
            'ate': 'Sim3 Umeyama translation residual in metres; diagnostic for metric-scale estimators',
            'ate_se3': 'SE3 Umeyama translation residual in metres',
            'rpe_translation': 'norm of translation in inverse(delta_reference) * delta_estimate, metres',
            'rpe_rotation': 'angle of rotation in inverse(delta_reference) * delta_estimate, degrees',
            'distance_windows': 'custom overlapping reference path-distance windows; first endpoint at/above length; tolerance +10%; not KITTI',
            'window_percentage': 'per-window translation norm / actual reference path length * 100',
            'sparse_export': sparse_export,
            'scale_failure_policy': 'metric estimators only: fitted scale outside [0.1, 10]; retained historical diagnostic threshold',
        },
    }
    duration = float(camera_times[-1] - camera_times[0])
    gap_threshold = max(0.5, 5 * float(np.median(np.diff(camera_times))))
    out['metric_protocol']['maximum_estimate_gap_s_for_windows'] = gap_threshold
    out['coverage'] = {
        'semantics': 'observed exported poses, not proof of tracking success',
        'export_kind': 'keyframes' if sparse_export else 'poses',
        'input_camera_frames': len(camera_times), 'output_poses': len(e),
        'reference_supported_camera_frames': int(camera_support.sum()),
        'associated_camera_frames': len(sampled),
        'camera_pose_coverage_pct': 100*len(sampled)/len(camera_times),
        'reference_supported_pose_pct': 100*len(sampled)/int(camera_support.sum()) if camera_support.any() else None,
        'association_dt_max_s': float(dt.max()) if len(dt) else None,
        'association_dt_mean_s': float(dt.mean()) if len(dt) else None,
        'sequence_duration_s': duration,
        'coverage_gap_pct': None,
    }
    if len(sampled):
        span = float(sampled[-1, 0] - sampled[0, 0])
        gaps = np.diff(sampled[:, 0])
        out['coverage'].update(export_span_s=span, export_span_pct=100*span/duration,
                               maximum_export_gap_s=float(gaps.max()) if len(gaps) else None)
        # Keyframe spacing is not tracking instrumentation. Withhold this field
        # rather than interpreting sparse export as lost tracking.
        if not sparse_export:
            supported_span = float(np.sum(gaps[gaps <= gap_threshold]))
            out['coverage']['coverage_gap_pct'] = 100*supported_span/duration
    if len(sampled) < 10:
        out['failure_reason'] = 'fewer than ten reference-supported camera pose pairs'
        return out, {'reference': reference_at_est, 'estimate': sampled, 'camera_ids': camera_ids}
    try:
        sim3 = fit_alignment(sampled[:, 1:4], reference_at_est[:, 1:4], True)
        se3 = fit_alignment(sampled[:, 1:4], reference_at_est[:, 1:4], False)
    except ValueError as exc:
        out['failure_reason'] = str(exc)
        out['run_status'] = 'tracking_failed' if np.max(np.linalg.norm(sampled[:, 1:4]-sampled[0, 1:4], axis=1)) <= 1e-6 else 'eval_failed'
        return out, {'reference': reference_at_est, 'estimate': sampled, 'camera_ids': camera_ids}
    sim_est, se_est = apply_alignment(sampled, sim3), apply_alignment(sampled, se3)
    sim_error = np.linalg.norm(sim_est[:, 1:4]-reference_at_est[:, 1:4], axis=1)
    se_error = np.linalg.norm(se_est[:, 1:4]-reference_at_est[:, 1:4], axis=1)
    out.update(ate=statistics(sim_error), ate_se3=statistics(se_error), scale_factor=sim3[2],
               final_drift_m=float(se_error[-1]), final_drift_sim3_m=float(sim_error[-1]),
               alignment_transforms={'se3': {'R': se3[0].tolist(), 't': se3[1].tolist()},
                                     'sim3': {'R': sim3[0].tolist(), 't': sim3[1].tolist(), 'scale': sim3[2]}})
    out['run_status'] = 'scale_collapse' if not monocular and not 0.1 <= sim3[2] <= 10 else 'ok'
    if gnss:
        # Numerically useful diagnostic, but global heading/reference origins
        # have not been established for the historical GNSS cohorts.
        out['ate_translation_only_diagnostic'] = translation_origin_errors(reference_at_est, sampled)
        out['metric_protocol']['gnss_translation_diagnostic'] = 'first-position translation only; no rotation or scale; global frame unverified'
    path_distance = np.r_[0, np.cumsum(np.linalg.norm(np.diff(reference_at_est[:, 1:4], axis=0), axis=1))]
    for length in (1, 10, 50, 100):
        pairs = distance_pairs(reference_at_est, length, gap_threshold)
        trans_sim, angle, displacement_sim = relative_errors(reference_at_est, sim_est, pairs)
        trans_se, _, displacement_se = relative_errors(reference_at_est, se_est, pairs)
        distances = path_distance[pairs[:, 1]] - path_distance[pairs[:, 0]] if len(pairs) else np.array([])
        window = {
            'requested_distance_m': length, 'pairs': len(pairs),
            'actual_distance_m': statistics(distances),
            'translation_sim3_m': statistics(trans_sim) if rotations_valid else dict(missing),
            'translation_se3_m': statistics(trans_se) if rotations_valid else dict(missing),
            'rotation_deg': statistics(angle) if rotations_valid else dict(missing),
            'translation_se3_pct': statistics(100*trans_se/distances) if rotations_valid else dict(missing),
            'translation_sim3_pct': statistics(100*trans_sim/distances) if rotations_valid else dict(missing),
            'displacement_magnitude_sim3_m': statistics(displacement_sim),
            'displacement_magnitude_se3_m': statistics(displacement_se),
        }
        out['window_drift'][f'{length}m'] = window
        if length == 1:
            out.update(rpe_trans_1m=window['translation_sim3_m'], rpe_trans_1m_se3=window['translation_se3_m'],
                       rpe_rot_1m_deg=window['rotation_deg'],
                       displacement_magnitude_error_1m={'sim3': window['displacement_magnitude_sim3_m'],
                                                        'se3': window['displacement_magnitude_se3_m']})
    return out, {'reference': reference_at_est, 'estimate': sampled, 'camera_ids': camera_ids,
                 'sim3_estimate': sim_est, 'se3_estimate': se_est,
                 'sim3_errors': sim_error, 'se3_errors': se_error}
