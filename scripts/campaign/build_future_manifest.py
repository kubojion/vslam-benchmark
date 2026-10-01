#!/usr/bin/env python3
"""Prepare future N=3 actions from reconciled evidence; never start estimation.

Actions remain blocked until scientific/configuration review and the required
execution-readiness evidence are recorded. The manifest distinguishes that status
from whether a saved trajectory, missing repetition or invalid cohort exists.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_repetitions import atomic_json
from run_future_manifest import UNREVIEWED_OVERRIDES

REPO=Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pipeline_evidence(repo):
    paths=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','--','scripts','configs'],cwd=repo,text=True).splitlines()
    return [{'path':p,'sha256':digest(repo/p)} for p in sorted(set(paths))
            if (repo/p).is_file() and not p.startswith('configs/campaigns/future-n3')]


def action_category(cell,attempt,decision):
    findings=attempt.get('confirmed_protocol_findings',[])
    if findings:
        return 'required_rerun',';'.join(f['code'] for f in findings)
    if cell['algorithm']=='orbslam3' and cell['dataset']=='zed2i' and cell['run_type'] in ('vo','vo-lc'):
        return 'required_rerun','camera_fps_changed_15_to_10'
    if not attempt['exists']:
        return 'missing','no_saved_attempt'
    if not attempt['trajectory_saved']:
        return 'blocked','retain_failed_or_interrupted_attempt_and_resolve_execution_cause'
    if not attempt['evaluated']:
        return 'blocked','recover_saved_trajectory_before_scheduling_estimation'
    # A validated failure is an outcome, never grounds to sample until successful.
    if decision.get('reuse_qualified') and attempt['numerical_status']!='eval_failed':
        return 'reusable','retain_observed_outcome_including_any_genuine_failure'
    return 'blocked','saved_result_qualification_pending'


def qualification_prerequisites(cell,attempt,decision):
    if decision.get('review_complete'):
        return []
    result=['complete_cell_configuration_input_and_claim_review']
    for blocker in attempt.get('qualification',{}).get('blockers',[]):
        if blocker!='configuration_and_claim_qualification_pending':
            result.append('resolve_or_document_claim_limit:'+blocker)
    # Missing attempts lack an evaluation from which to inherit reference issues.
    ds=cell['dataset'];mode=cell['run_type'];algo=cell['algorithm']
    if ds=='hortimulti':result.append('establish_reference_to_camera_extrinsic_from_original_calibration')
    if ds=='rosariov2':result.append('verify_rectified_camera_axes_and_reference_sensor_chain')
    if ds=='zed2i':
        result.append('restrict_reference_claims_to_position_and_review_lever_arm_assumptions')
        if mode in ('vio','vio-lc'):result.append('resolve_serial_specific_imu_rotation_and_time_offset_evidence')
    if algo=='airslam':result.append('declare_sparse_keyframe_claim_or_validate_dense_export_before_dense_comparison')
    if algo in ('orbslam3','airslam','ov2slam','openvins'):
        result.append('document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review')
    if algo=='okvis2x' and mode=='vio-lc' and ds=='zed2i':
        result.append('declare_three_frame_lc_window_variant_versus_five_frame_other_rigs')
    if algo in ('okvis2','okvis2x') and mode in ('vo-lc','vio-lc'):
        result.append('freeze_and_label_final_bundle_adjustment_and_extrinsic_optimization_policy')
    if attempt.get('process',{}).get('exit_code') not in (None,0):
        result.append('retain_nonzero_exit_and_review_saved_native_failure_evidence')
    return result


def build(repo,inventory,inventory_path,decisions):
    actions=[];target_paths=set()
    for cell in inventory['cells']:
        key=cell['key'];decision=decisions.get('cells',{}).get(key,{})
        occupied={p.name for p in (repo/'results'/key).glob('run*')}
        next_id=10001
        for repetition,attempt in enumerate(cell['attempts'],1):
            category,reason=action_category(cell,attempt,decision)
            prerequisites=list(decision.get('blockers',[]))
            prerequisites.extend(f['prerequisite'] for f in attempt.get('confirmed_protocol_findings',[]))
            prerequisites.extend(qualification_prerequisites(cell,attempt,decision))
            if category=='blocked':prerequisites.append(reason)
            if category=='required_rerun' and not decision.get('historical_cohort_preserved'):
                prerequisites.append('keep_original_invalid_configuration_cohort_separate')
            if cell['run_type']=='gnss-vio' and not decision.get('gnss_protocol_verified'):
                prerequisites.extend(['verify_gnss_input_variant_covariance_and_antenna_frame','verify_reference_independence_and_fusion_output'])
            if not cell['within_cell_config_consistent']:
                prerequisites.append('resolve_within_cell_configuration_mismatch')
            if not cell.get('within_cell_cohort_consistent', True):
                prerequisites.append('resolve_recorded_source_binary_parameter_or_hardware_cohort_difference')
            # Unique physical IDs preserve every original directory and log.
            while f'run{next_id}' in occupied or (repo/'logs'/f"{cell['dataset']}_{cell['sequence']}_{cell['algorithm']}_{cell['run_type']}_run{next_id}.log").exists():
                next_id+=1
            run_id=next_id;next_id+=1
            output=f'results/{key}/run{run_id}';target_paths.add(output)
            cohort='repair-n3-'+hashlib.sha256(key.encode()).hexdigest()[:12]
            command=['python3','scripts/campaign/run_repetitions.py',cell['dataset'],cell['sequence'],cell['algorithm'],'3',cell['run_type'],
                     '--run-id',str(run_id),'--repetition',str(repetition),'--cohort',cohort]
            run_required=category in ('missing','required_rerun')
            ready=bool(decision.get('execution_verified') and decision.get('static_verified') and
                       decision.get('evidence')) and not prerequisites and run_required
            runtime=cell['runtime_estimate'] if run_required else dict(estimate_s=0 if category=='reusable' else None,
                reason='reuse requires no estimation' if category=='reusable' else 'action blocked; resolve prerequisites before estimation')
            actions.append(dict(id=f'{key}/default/r{repetition}',cell=key,repetition=repetition,input_variant='default',
                category=category,reason=reason,prior_attempt=attempt['path'],prior_evidence=attempt['files'],
                observed_outcome=attempt['numerical_status'],recorded_process=attempt['process'],
                prior_qualification=attempt.get('qualification'),
                planned_random_seed=1000+run_id if cell['algorithm']=='dpvo' and run_required else None,
                planned_output=output if run_required else None,command=command if run_required else None,
                cohort=cohort,prerequisites=sorted(set(prerequisites)),runtime_estimate=runtime,
                readiness=dict(verified_ready_to_run=ready,static_checks='verified' if decision.get('static_verified') else 'pending',
                    execution_validation='verified' if decision.get('execution_verified') else 'not_verified_after_repairs'),
                review_evidence=decision.get('evidence',[])))
    estimates=[a['runtime_estimate'].get('estimate_s') for a in actions if a['category'] in ('missing','required_rerun')]
    return dict(schema_version=2,campaign_id='future-n3-five-modes',audit_status='in_progress',
        target=dict(default_cells=len(inventory['cells']),repetitions=3,logical_repetitions=len(actions),
                    note='Original four-mode 600-attempt campaign plus 20 GNSS default cells at N=3; legacy GNSS experiments remain separate'),
        exclusions=inventory['excluded'],inventory=dict(path=str(inventory_path.relative_to(repo)),sha256=digest(inventory_path)),
        pipeline_files=pipeline_evidence(repo),actions=actions,
        environment_policy=dict(kind='runner_defaults_only',reject_nonempty=list(UNREVIEWED_OVERRIDES),
            note='An inherited config, playback, input, seed or numerical-runtime override requires a separately reviewed campaign recipe.'),
        retained_gnss_variants=[dict(path=a['path'],status='preserved_separate_experiment',
             prerequisites=['explicit_variant_file_selection_and_historical_provenance_review'],
             note='not merged into default N=3 repetitions or automatically scheduled')
             for a in inventory['other_artifacts'] if a['category']=='gnss_variant'],
        summary=dict(categories=dict(Counter(a['category'] for a in actions)),
            verified_ready_to_run=sum(a['readiness']['verified_ready_to_run'] for a in actions),
            estimated_serial_estimation_s=sum(x for x in estimates if x is not None),
            actions_with_unknown_runtime=sum(x is None for x in estimates),
            estimate_scope='Known missing/rerun actions only; excludes unresolved blocked actions, readiness diagnostics and evaluation overhead',
            resource_policy='serial execution; exclusive shared GPU/containers; check host contention before launch'))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--inventory',type=Path,default=REPO/'results/repair-20261001/inventory.json')
    ap.add_argument('--decisions',type=Path)
    ap.add_argument('--output',type=Path,default=REPO/'results/repair-20261001/future-n3-manifest.json')
    args=ap.parse_args();path=args.inventory.resolve();inventory=json.loads(path.read_text())
    decisions=json.loads(args.decisions.read_text()) if args.decisions else {}
    result=build(REPO,inventory,path,decisions);atomic_json(args.output,result)
    print(json.dumps(result['summary'],indent=2))


if __name__=='__main__':main()
