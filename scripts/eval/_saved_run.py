"""Assemble a traceable schema-3 evaluation without changing run evidence."""
from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import tempfile

import numpy as np

from _metrics import interpolate_reference, reference_interval_ids, right_transform, statistics, validate_poses
from _pose_frames import file_evidence, frame_policy
from _run_observations import parse_log, parse_resources
from _run_type import resolve
from _segment_trajectory import classify, merge_segments, yaw_from_path
from _trajectory_evaluation import evaluate_arrays, position_only_diagnostic
from _reference_source import selected_reference


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def evaluator_identity():
    files = ['_saved_run.py', '_metrics.py', '_pose_frames.py', '_trajectory_evaluation.py',
             '_run_observations.py', '_segment_trajectory.py', '_run_type.py', '_reference_source.py']
    parent = Path(__file__).resolve().parent
    evidence = [file_evidence(parent/f, parent) for f in files]
    return dict(schema=3, files=evidence,
                sha256=hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest())


@lru_cache(maxsize=24)
def load_reference(path, digest):
    """Digest is part of the cache key, so a replaced GT is never reused."""
    return validate_poses(np.loadtxt(path, ndmin=2))


@lru_cache(maxsize=24)
def generated_segments(gt_path, gt_digest, times_path, times_digest, transform_json, dataset,
                       support_json='null'):
    reference = load_reference(gt_path, gt_digest)
    times = np.loadtxt(times_path, ndmin=1) / 1e9
    intervals=json.loads(support_json)
    grid, _ = interpolate_reference(reference, times, valid_intervals=intervals)
    if len(grid) < 2:
        return []
    if transform_json != 'null':
        grid = right_transform(grid, json.loads(transform_json))
    # These are geometric path classes, not human-labelled vehicle manoeuvres.
    # Use path heading for every agricultural reference, since an optical-frame
    # Euler yaw is not the vehicle heading and ZED has no reference orientation.
    split=np.diff(grid[:,0])>.5
    if intervals is not None:
        split |= np.diff(reference_interval_ids(grid[:,0],intervals))!=0
    boundaries = np.r_[0, np.flatnonzero(split)+1, len(grid)]
    rows = []
    for start, stop in zip(boundaries[:-1], boundaries[1:]):
        chunk = grid[start:stop]
        if len(chunk) < 2:
            continue
        t, xy = chunk[:, 0], chunk[:, 1:3]
        turn, distance = classify(t, xy, yaw_from_path(xy), 2.0, 10.0, .50)
        segments = merge_segments(t, turn, distance, 1.0)
        for s in segments:
            rows.append(dict(type='all' if dataset == 'euroc_mav' else 'turn' if s['is_turn'] else 'row',
                             t_start=s['t_start'], t_end=s['t_end'], n_frames=s['n'],
                             duration_s=s['t_end']-s['t_start'], path_m=s['path']))
    return rows


def segment_metrics(paired, rows, monocular):
    errors = paired.get('sim3_errors' if monocular else 'se3_errors')
    if errors is None:
        return {}
    times = paired['estimate'][:, 0]
    groups = {}
    for row in rows:
        selected = (times >= row['t_start']) & (times <= row['t_end'])
        if selected.sum() < 5:
            continue
        stats = statistics(errors[selected])
        groups.setdefault(row['type'], []).append(dict(row, ate_rmse=stats['rmse'], ate_mean=stats['mean'], n_pairs=stats['n']))
    return {kind: dict(n_segments=len(segs),
                        ate_rmse_mean=float(np.mean([s['ate_rmse'] for s in segs])),
                        ate_rmse_std=float(np.std([s['ate_rmse'] for s in segs], ddof=1)) if len(segs)>1 else None,
                        alignment='global_sim3' if monocular else 'global_se3', segments=segs)
            for kind, segs in groups.items()}


def interpreted_measurements(meta):
    """Withhold inferred schema-1 processing counts without altering raw metadata."""
    values = dict(meta.get('measurements') or {})
    if not values:
        return values
    values['measurement_interpretation_schema'] = 2
    values['end_to_end_fps_semantics'] = 'available_input_frames_per_wrapper_elapsed_second'
    if meta.get('measurement_schema') != 2:
        legacy = {key: values.get(key) for key in (
            'processed_frames', 'processing_time_s', 'processing_fps', 'processing_time_scope')}
        values['legacy_processing_claims'] = legacy
        if any(legacy[key] is not None for key in ('processed_frames','processing_time_s','processing_fps')):
            values['measurement_warning'] = 'legacy_input_count_assumed_processed; processing_claims_withheld'
        if values.get('mode') == 'max_throughput':
            values['command_time_s'] = legacy['processing_time_s']
            values['command_input_fps'] = legacy['processing_fps']
            values['command_time_scope'] = 'legacy_recorded_command_scope_unverified'
        values.update(processed_frames=None, processing_time_s=None, processing_fps=None,
                      processing_time_scope='unavailable', processed_frames_evidence='unavailable')
    return values


def evaluate_saved_run(ws, run_dir, *, gt_override=None):
    ws, run_dir = Path(ws).resolve(), Path(run_dir).resolve()
    mode, dataset, seq, algo, run_name = run_dir.relative_to(ws/'results').parts
    rt = resolve(mode, ws)
    meta_path, old_path = run_dir/'run_meta.json', run_dir/'run_eval.json'
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    old = json.loads(old_path.read_text()) if old_path.exists() else {}
    run_id, _, variant = run_name.removeprefix('run').partition('_')
    ds = ws/'datasets'/dataset/seq
    gt_path, times_path, trajectory = Path(gt_override) if gt_override else ds/'gt_tum.txt', ds/'times.txt', run_dir/'trajectory.txt'
    selected=selected_reference(ws,dataset,seq) if not gt_override else None
    if selected:gt_path=selected['path']
    inputs = [file_evidence(p, ws) for p in (gt_path, times_path, trajectory)]
    inputs.extend(file_evidence(p, ws) for p in (meta_path,) if p.exists())
    physical_sequence=selected.get('physical_sequence',seq) if selected else seq
    policy = frame_policy(ws, run_dir, meta, dataset, physical_sequence, algo, rt.use_imu)
    if physical_sequence!=seq:
        policy['diagnostic_parent_sequence']=physical_sequence
    if selected:
        if dataset!='zed2i' or selected['orientation_valid']:
            raise ValueError('only the reviewed position-only ZED reference is supported')
        policy.update(reference_frame='nominal_left_camera_position_enu',
                      reference_transform=np.eye(4).tolist(),orientation_valid=False,
                      reference_valid_intervals=selected['valid_intervals'],
                      reference_version=selected['version'],reference_variant=selected['variant'],
                      reference_limitations=selected['limitations'])
        inputs.extend(selected['evidence'])
    if gt_override:
        policy.update(reference_transform=None, orientation_valid=False, common_origin_verified=False,
                      reference_frame='unverified_override')
        policy['blockers'].append('override_reference_frame_requires_explicit_review')
    reference = load_reference(str(gt_path), inputs[0]['sha256'])
    times = np.loadtxt(times_path, ndmin=1) / 1e9
    estimate = np.loadtxt(trajectory, ndmin=2)
    # Validate failure records too. Never sort, deduplicate or guess units here.
    try:
        numerical, paired = evaluate_arrays(reference, estimate, times, policy,
                         monocular=algo in ('dpvo', 'droidslam', 'mast3r_slam', 'megasam'),
                         sparse_export=algo == 'airslam', gnss=rt.use_gnss)
    except ValueError as exc:
        numerical = dict(eval_schema=3, run_status='eval_failed', failure_reason=str(exc), n_pairs_ate=0,
                         ate=statistics([]), ate_se3=statistics([]), ate_origin={},
                         rpe_trans_1m=statistics([]), rpe_trans_1m_se3=statistics([]),
                         rpe_rot_1m_deg=statistics([]), window_drift={}, scale_factor=None,
                         final_drift_m=None, coverage={'coverage_gap_pct': None, 'validation_error': str(exc)})
        paired = {}
        if rt.use_gnss:
            diagnostic=position_only_diagnostic(reference,estimate,times,policy)
            if diagnostic is not None:
                numerical['position_only_diagnostic']=diagnostic
    # OpenVINS estimator messages are in a separate saved node log.
    log_path = run_dir/('openvins_node.log' if algo == 'openvins' and (run_dir/'openvins_node.log').exists() else 'run_log.txt')
    robustness = parse_log(str(log_path), algo)
    measurements = interpreted_measurements(meta)
    robustness.update(output_valid=numerical['run_status'] == 'ok',
                      frames_total=measurements.get('input_frames'), frames_processed=measurements.get('processed_frames'),
                      frames_published=measurements.get('published_frames'), output_poses=len(estimate),
                      dropped_frames=measurements.get('dropped_frames'))
    runtime = parse_resources(str(run_dir/'resources.csv')) or {}
    if measurements:
        runtime.update(measurements)
        runtime.update(measurement_schema=meta.get('measurement_schema'), measurement_mode=measurements.get('mode'),
                       wall_s=measurements.get('end_to_end_time_s'))
    elif meta.get('duration_s') is not None:
        runtime.update(wall_s=meta['duration_s'], legacy_fps=meta.get('fps'),
                       legacy_fps_semantics=meta.get('legacy_fps_semantics', 'unverified'))
    machine = meta.get('machine') or old.get('machine') or {'collected_at': 'unknown', 'note': 'run hardware not recorded'}
    if meta.get('machine'):
        machine = dict(machine, collected_at='run')
    process = dict(meta.get('process', {}))
    execution = dict(complete_marker=(run_dir/'COMPLETE').is_file(), recorded_run_status=meta.get('run_status'),
                     process=process, status='unknown')
    if process.get('exit_code') == 0:
        execution['status'] = 'exited_zero'
    elif process.get('exit_code') is not None:
        execution['status'] = 'exited_nonzero'
    blockers = list(policy['blockers'])
    if execution['status'] != 'exited_zero':
        blockers.append('execution_exit_nonzero_or_unverified')
    if not meta.get('provenance'):
        blockers.append('run_time_configuration_provenance_missing')
    if algo == 'airslam':
        blockers.append('keyframe_only_accuracy_not_dense_frame_comparison')
    if numerical['run_status'] != 'ok':
        blockers.append('trajectory_'+numerical['run_status'])
    # Completion of numerical evaluation does not certify the configuration.
    # The all-mode audit will supply the remaining per-run qualification gates.
    blockers.append('configuration_and_claim_qualification_pending')
    out = dict(numerical, dataset=dataset, seq=seq, algo=algo, run=run_id, run_directory=run_name,
               run_type=mode, gnss_variant=variant or 'default',
               use_imu=rt.use_imu, use_lc=meta.get('use_lc') if rt.use_gnss else rt.use_lc,
               use_gnss=rt.use_gnss, gt_source='raw_reference_interpolated_at_observed_estimates',
               gt_provenance=inputs[0], pose_frames=policy, execution=execution,
               robustness=robustness, runtime=runtime, machine=machine,
               evaluation_provenance=dict(evaluator=evaluator_identity(), inputs=inputs,
                                         timestamp_utc=datetime.now(timezone.utc).isoformat()),
               qualification=dict(status='pending_review', blockers=blockers), agri_segments={})
    if old_path.exists():
        out['evaluation_provenance']['previous_evaluation'] = dict(file_evidence(old_path, ws), schema=old.get('eval_schema'),
                    ate_se3_rmse=old.get('ate_se3', {}).get('rmse'), ate_sim3_rmse=old.get('ate', {}).get('rmse'),
                    rpe_rotation_rmse=old.get('rpe_rot_1m_deg', {}).get('rmse'))
    for path in (log_path, run_dir/'resources.csv'):
        if path.exists():
            out['evaluation_provenance']['inputs'].append(file_evidence(path, ws))
    if paired.get('se3_errors') is not None:
        # No existence-only segments_auto.csv cache is consumed.
        rows = generated_segments(str(gt_path), inputs[0]['sha256'], str(times_path), inputs[1]['sha256'],
                                  json.dumps(policy['reference_transform']), dataset,
                                  json.dumps(policy.get('reference_valid_intervals')))
        out['agri_segments'] = segment_metrics(paired, rows, algo in ('dpvo', 'droidslam', 'mast3r_slam', 'megasam'))
        out['segment_provenance'] = dict(method='geometric_horizontal_path_heading',
                                        win_path_m=2.0, heading_threshold_deg=10, straight_tolerance_m=.5,
                                        minimum_segment_path_m=1.0, reference_max_gap_s=.5,
                                        source_sha256=inputs[0]['sha256'], camera_times_sha256=inputs[1]['sha256'],
                                        human_labelled=False, segment_count=len(rows))
    return out, paired
