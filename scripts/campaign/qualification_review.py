"""Conservative, reproducible claim review of the retained historical evidence.

This is separate from numerical evaluation. It never promotes a result merely
because no automated check failed, and never converts an evidence gap to a rerun.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from functools import lru_cache
from acceptance_ledger import reviewed_decision, LEDGER, DOCUMENT

REVIEW_DOCUMENT = 'docs/publication-qualification-20261001.md'


@lru_cache(maxsize=4096)
def _evidence_hash(path, mtime_ns, ctime_ns, size):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def review_identity(repo):
    paths = ['scripts/campaign/qualification_review.py', 'scripts/campaign/protocol_findings.py', REVIEW_DOCUMENT,
             'scripts/campaign/acceptance_ledger.py', 'scripts/campaign/protocol_status.py',
             'docs/protocol-review-20261002.md']
    paths += [p for p in ('docs/campaigns/horti-time-offset-findings-20261001.json',
                          'docs/campaigns/gnss-lever-findings-20261001.json',
                          'docs/campaigns/reference-sources-20261001.json',
                          'docs/reference-review-20261001.md') if (repo/p).is_file()]
    paths += [p for p in (LEDGER, DOCUMENT) if (repo/p).is_file()]
    if (repo/LEDGER).is_file():
        paths += [r['path'] for r in json.loads((repo/LEDGER).read_text()).get('supporting_evidence', [])]
    evidence = []
    for p in dict.fromkeys(paths):
        path = repo/p
        stat = path.stat()
        evidence.append(dict(path=p, sha256=_evidence_hash(
            str(path), stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size)))
    return dict(schema=1, evidence=evidence)


def review_saved(relative, meta, evaluation, findings, snapshots, *, exists, repo=None):
    if repo is not None:
        reviewed = reviewed_decision(repo, relative, meta, evaluation, findings, snapshots, exists)
        if reviewed is not None:
            return reviewed
    mode, dataset, sequence, algorithm, name = Path(relative).parts
    # Recompute review-derived fields from original evidence, not a previous
    # decision. Numerical/frame/execution checks are independently retained.
    blockers = list(evaluation.get('pose_frames', {}).get('blockers', []))
    limitations = ['no_measured_processing_rate_or_realtime_deadline_claim',
                   'accuracy_conditional_on_observed_exports_and_reference_support',
                   'configuration_choices_are_not_evidence_of_algorithm_optimality']
    if not exists:
        return dict(status='not_executed', blockers=['missing_repetition'], claim_limits=limitations,
                    review='historical_evidence_review', reuse_qualified=False)
    provenance = meta.get('provenance', {})
    if not provenance:
        blockers.append('historical_effective_configuration_and_implementation_evidence_missing')
    else:
        workspace = provenance.get('workspace', {})
        runtime_capture=provenance.get('runtime_assets',{})
        if runtime_capture and not (runtime_capture.get('native_binary_source_linkage_verified') and
                                    runtime_capture.get('loaded_dependency_closure_verified')):
            blockers.append('native_build_source_linkage_and_loaded_dependency_closure_unverified')
        if workspace.get('dirty') and not workspace.get('snapshot'):
            blockers.append('historical_dirty_runner_tree_recorded_only_as_nonreconstructable_digest')
        elif not workspace.get('commit'):
            blockers.append('historical_runner_revision_missing')
        for source in provenance.get('sources', []):
            if source.get('dirty') and not source.get('snapshot'):
                blockers.append('historical_dirty_algorithm_or_nested_source_bytes_unpreserved')
        if not snapshots or any(not s.get('verified') for s in snapshots):
            blockers.append('historical_config_snapshot_missing_or_unverified')
        if algorithm == 'basalt':
            blockers.append('installed_basalt_binary_to_source_revision_not_established')
        if algorithm in ('airslam', 'ov2slam', 'voxel_svio') and not provenance.get('binaries') and not runtime_capture:
            blockers.append('historical_mutable_container_native_executable_not_identified')
        if algorithm == 'openvins' and not provenance.get('runtime_assets'):
            blockers.append('historical_container_runtime_resolution_and_build_source_linkage_unverified')
        if algorithm == 'orbslam3' and not runtime_capture:
            blockers.append('historical_orb_shared_estimator_library_not_identified')
    if not evaluation:
        blockers.append('no_evaluated_saved_trajectory_retain_execution_evidence')
    else:
        if meta.get('process', {}).get('exit_code') != 0:
            blockers.append('execution_exit_nonzero_or_unverified')
        if evaluation.get('run_status') != 'ok':
            limitations.append('retain_observed_' + str(evaluation.get('run_status')) + '_in_attempt_denominator')
        if evaluation.get('run_status') == 'eval_failed':
            blockers.append('invalid_saved_trajectory_not_full_pose_accuracy_evidence')
        coverage = evaluation.get('coverage', {}).get('coverage_gap_pct')
        if isinstance(coverage, (int, float)) and coverage < 95:
            limitations.append('export_coverage_below_95_percent_no_clean_success_tick')
    if dataset == 'zed2i':
        blockers.append('zed_reference_camera_lever_arm_heading_and_altitude_assumptions_unverified')
        if mode in ('vio', 'vio-lc', 'gnss-vio'):
            blockers.append('zed_serial_specific_imu_rotation_and_time_offset_unverified')
    if algorithm == 'airslam':
        blockers.append('keyframe_only_accuracy_not_dense_frame_comparison')
    if algorithm in ('orbslam3', 'airslam', 'ov2slam', 'openvins'):
        limitations.append('disclose_rig_specific_algorithm_parameters_in_saved_parameter_review')
    if algorithm in ('okvis2', 'okvis2x') and mode in ('vo-lc', 'vio-lc'):
        limitations.append('final_ba_disabled' if algorithm == 'okvis2' else 'final_ba_enabled_with_extrinsic_optimization')
    if algorithm == 'macvo':
        limitations.append('official_performant_profile_not_paper_reproduction_profile')
    if algorithm == 'dpvo':
        limitations.append('monocular_sim3_shape_only_not_metric_stereo_ranking')
    if mode == 'gnss-vio':
        blockers.extend(['historical_gnss_input_covariance_antenna_and_fusion_output_unverified',
                         'gnss_reference_independence_and_global_frame_not_established'])
    blockers.extend(f['code'] for f in findings)
    # An explicit independently reviewed claim decision is necessary even for a
    # future record that passes these historical evidence checks.
    if not blockers:
        blockers.append('explicit_configuration_input_and_claim_review_not_recorded')
    return dict(status='rerun_required' if findings else 'blocked',
                blockers=sorted(set(blockers)), claim_limits=sorted(set(limitations)),
                review='historical_evidence_review', reuse_qualified=False,
                rerun_decision='confirmed_estimator_side_defect' if findings else
                    'not_requested_by_evidence_gap_preserve_and_resolve_first')


def apply_review(repo, run, evaluation):
    from protocol_findings import historical_findings
    meta_path = run/'run_meta.json'
    meta = json.loads(meta_path.read_text()) if meta_path.is_file() else {}
    snapshots = []
    for item in meta.get('provenance', {}).get('artifacts', []):
        if item.get('snapshot'):
            path = run/item['snapshot']
            snapshots.append(dict(verified=path.is_file() and
                hashlib.sha256(path.read_bytes()).hexdigest() == item.get('snapshot_sha256')))
    relative = str(run.relative_to(repo/'results'))
    evaluation['qualification'] = review_saved(relative, meta, evaluation,
        historical_findings(repo, relative, meta), snapshots, exists=run.is_dir(), repo=repo)
    evaluation['qualification_provenance'] = review_identity(repo)
    return evaluation
