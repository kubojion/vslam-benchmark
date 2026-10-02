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
from run_future_manifest import UNREVIEWED_OVERRIDES, verify_files
from configuration_recipe import config_recipe
from acceptance_ledger import LEDGER, DOCUMENT

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
    if decision.get('fresh_cohort'):
        return 'cohort_completion','complete_predeclared_current_implementation_n3_preserve_all_historical_outcomes'
    qualification=attempt.get('qualification',{})
    if (qualification.get('reuse_qualified') and
        (qualification.get('review')=='explicit_claim_review' or decision.get('reuse_qualified')) and
        attempt.get('numerical_status')!='eval_failed' and
        (attempt.get('evaluated') or qualification.get('status')=='valid_observed_failure')):
        return 'reusable','retain_observed_outcome_including_any_genuine_failure'
    if not attempt['trajectory_saved']:
        return 'blocked','retain_failed_or_interrupted_attempt_and_resolve_execution_cause'
    if not attempt['evaluated']:
        return 'blocked','recover_saved_trajectory_before_scheduling_estimation'
    # A validated failure is an outcome, never grounds to sample until successful.
    if (decision.get('reuse_qualified') and attempt.get('qualification',{}).get('reuse_qualified')
        and attempt['numerical_status']!='eval_failed'):
        return 'reusable','retain_observed_outcome_including_any_genuine_failure'
    return 'blocked','saved_result_has_unresolved_scientific_evidence'


def qualification_prerequisites(cell,attempt,decision):
    if decision.get('review_complete'):
        return []
    result=[] if attempt.get('qualification',{}).get('review')=='historical_evidence_review' else ['complete_cell_configuration_input_and_claim_review']
    for blocker in attempt.get('qualification',{}).get('blockers',[]):
        if blocker!='configuration_and_claim_qualification_pending':
            result.append('resolve_or_document_claim_limit:'+blocker)
    # Missing attempts lack an evaluation from which to inherit reference issues.
    ds=cell['dataset'];mode=cell['run_type'];algo=cell['algorithm']
    if ds=='hortimulti':result.extend(['link_february_reference_generation_origin_and_clock_to_each_saved_session',
        'validate_camera_imu_time_compensation_and_output_clock_in_native_path'])
    if ds=='rosariov2':result.append('reconcile_unchanged_recorded_images_with_author_virtual_projection_and_baseline')
    if ds=='zed2i':
        result.append('settle_zed_quality_support_and_horizontal_vs_3d_reference_claim_disclose_unmeasured_clock')
        if mode in ('vio','vio-lc'):result.append('resolve_serial_specific_imu_rotation_and_time_offset_evidence')
    if mode=='gnss-vio' and algo=='vins_fusion_gps':result.append('implement_and_validate_antenna_lever_in_global_position_factor')
    if mode=='gnss-vio' and algo=='openvins_gps':result.append('validate_enu_heading_initialization_and_imu_body_alias')
    if ds=='rosariov2' and (mode=='vio' and algo in ('basalt','openvins','voxel_svio') or algo=='openvins_gps'):
        result.append('replace_identity_imu_camera_profile_with_consistent_matched_camera_model')
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


def resolved_prerequisites(repo, decision):
    """Only reviewed, content-pinned repairs discharge named prerequisites."""
    resolved=set()
    for item in decision.get('resolved_prerequisites', []):
        evidence=item.get('evidence', [])
        if not item.get('prerequisite') or not evidence:
            raise ValueError('prerequisite resolution requires named evidence')
        errors=verify_files(repo, evidence)
        if errors:
            raise ValueError('; '.join(errors))
        resolved.add(item['prerequisite'])
    return resolved


def build(repo,inventory,inventory_path,decisions):
    actions=[];target_paths=set()
    for cell in inventory['cells']:
        key=cell['key'];decision=decisions.get('cells',{}).get(key,{})
        resolved=resolved_prerequisites(repo,decision)
        recipe=config_recipe(repo,cell)
        input_path=repo/'results/repair-20261001/prepared-inputs'/f"{cell['dataset']}--{cell['sequence']}.json"
        input_record=None
        if input_path.is_file():
            value=json.loads(input_path.read_text())
            input_record=dict(path=str(input_path.relative_to(repo)),sha256=digest(input_path),content_sha256=value['sha256'])
        runtime_path=repo/'results/repair-20261001/runtime-assets'/f"{cell['algorithm']}.json"
        runtime_record=None;runtime_missing=[]
        if runtime_path.is_file():
            value=json.loads(runtime_path.read_text());runtime_missing=value['missing']
            runtime_record=dict(path=str(runtime_path.relative_to(repo)),sha256=digest(runtime_path),content_sha256=value['sha256'])
        source_path=repo/'results/repair-20261001/implementation-capture-current'/cell['algorithm']/'provenance/implementation.json'
        source_record=dict(path=str(source_path.relative_to(repo)),sha256=digest(source_path)) if source_path.is_file() else None
        if source_record:
            trees=json.loads(source_path.read_text())['trees']
            source_record['content_sha256']=hashlib.sha256(json.dumps(trees,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        occupied={p.name for p in (repo/'results'/key).glob('run*')}
        next_id=10001
        for repetition,attempt in enumerate(cell['attempts'],1):
            category,reason=action_category(cell,attempt,decision)
            prerequisites=list(decision.get('blockers',[]))
            if not input_record:prerequisites.append('capture_and_verify_prepared_input_content')
            if not runtime_record:prerequisites.append('capture_current_native_model_container_assets')
            if not source_record:prerequisites.append('capture_current_exact_source_implementation')
            prerequisites.extend(runtime_missing)
            prerequisites.extend(recipe['selection_errors'])
            if not decision.get('effective_configuration_verified'):
                prerequisites.extend(recipe['unresolved'])
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
            if cell['algorithm'] in ('ov2slam','voxel_svio'):
                prerequisites.append('capture_native_exit_separately_and_diagnose_logged_shutdown_errors')
            if cell['algorithm']=='orbslam3' and cell['dataset']!='zed2i':
                prerequisites.append('validate_non_zed_orb_eigen_abi_and_shutdown_native_build')
            prerequisites=[p for p in prerequisites if p not in resolved]
            review_evidence=list(decision.get('evidence',[]))
            for resolution in decision.get('resolved_prerequisites', []):
                review_evidence.extend(resolution['evidence'])
            if attempt.get('qualification',{}).get('review')=='explicit_claim_review':
                review_evidence += [dict(path=p,sha256=digest(repo/p)) for p in (LEDGER,DOCUMENT)]
            # Acceptance permits retaining this observation. Future build/config
            # validation applies to new estimation, not to keeping saved evidence.
            if category=='reusable':prerequisites=[]
            # Unique physical IDs preserve every original directory and log.
            while f'run{next_id}' in occupied or (repo/'logs'/f"{cell['dataset']}_{cell['sequence']}_{cell['algorithm']}_{cell['run_type']}_run{next_id}.log").exists():
                next_id+=1
            run_id=next_id;next_id+=1
            output=f'results/{key}/run{run_id}';target_paths.add(output)
            cohort='repair-n3-'+hashlib.sha256(key.encode()).hexdigest()[:12]
            command=['python3','scripts/campaign/run_repetitions.py',cell['dataset'],cell['sequence'],cell['algorithm'],'3',cell['run_type'],
                     '--run-id',str(run_id),'--repetition',str(repetition),'--cohort',cohort]
            run_required=category in ('missing','required_rerun','cohort_completion')
            ready=bool(decision.get('execution_verified') and decision.get('static_verified') and
                       decision.get('evidence')) and not prerequisites and run_required
            runtime=cell['runtime_estimate'] if run_required else dict(estimate_s=0 if category=='reusable' else None,
                reason='reuse requires no estimation' if category=='reusable' else 'action blocked; resolve prerequisites before estimation')
            actions.append(dict(id=f'{key}/default/r{repetition}',cell=key,repetition=repetition,input_variant='default',
                category=category,reason=reason,prior_attempt=attempt['path'],prior_evidence=attempt['files'],
                observed_outcome=attempt['numerical_status'],recorded_process=attempt['process'],
                prior_qualification=attempt.get('qualification'),
                configuration_recipe=recipe,
                prepared_inputs=input_record,
                runtime_assets=runtime_record,implementation_capture=source_record,
                planned_random_seed=1000+run_id if cell['algorithm']=='dpvo' and run_required else None,
                planned_output=output if run_required else None,command=command if run_required else None,
                cohort=cohort,prerequisites=sorted(set(prerequisites)),runtime_estimate=runtime,
                readiness=dict(verified_ready_to_run=ready,static_checks='verified' if decision.get('static_verified') else 'pending',
                    execution_validation='verified' if decision.get('execution_verified') else 'not_verified_after_repairs'),
                review_evidence=review_evidence))
    estimates=[a['runtime_estimate'].get('estimate_s') for a in actions if a['category'] in ('missing','required_rerun','cohort_completion')]
    return dict(schema_version=2,configuration_recipe_schema=1,input_identity_schema=1,runtime_identity_schema=1,
        implementation_capture_schema=1,campaign_id='future-n3-five-modes',audit_status='in_progress',
        target=dict(default_cells=len(inventory['cells']),repetitions=3,logical_repetitions=len(actions),
                    note='Original four-mode 600-attempt campaign plus 20 GNSS default cells at N=3; legacy GNSS experiments remain separate'),
        exclusions=inventory['excluded'],inventory=dict(path=str(inventory_path.relative_to(repo)),sha256=digest(inventory_path)),
        pipeline_files=pipeline_evidence(repo),qualification_review=inventory.get('qualification_review'),actions=actions,
        environment_policy=dict(kind='runner_defaults_only',reject_nonempty=list(UNREVIEWED_OVERRIDES),
            note='An inherited config, playback, input, seed or numerical-runtime override requires a separately reviewed campaign recipe.'),
        retained_gnss_variants=[dict(path=a['path'],status='preserved_separate_experiment',
             prerequisites=['explicit_variant_file_selection_and_historical_provenance_review'],
             note='not merged into default N=3 repetitions or automatically scheduled')
             for a in inventory['other_artifacts'] if a['category']=='gnss_variant'],
        summary=dict(categories=dict(Counter(a['category'] for a in actions)),
            configuration_recipes=len(inventory['cells']),
            configuration_selection_errors=sum(bool(a['configuration_recipe']['selection_errors']) for a in actions if a['repetition']==1),
            verified_ready_to_run=sum(a['readiness']['verified_ready_to_run'] for a in actions),
            estimated_serial_estimation_s=sum(x for x in estimates if x is not None),
            actions_with_unknown_runtime=sum(x is None for x in estimates),
            estimate_scope='Known missing/rerun actions only; excludes unresolved blocked actions, readiness diagnostics and evaluation overhead',
            resource_policy='serial execution; exclusive shared GPU/containers; check host contention before launch'))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--inventory',type=Path,default=REPO/'results/repair-20261001/inventory.json')
    reviewed=REPO/'docs/campaigns/zed-readiness-review-20261002.json'
    ap.add_argument('--decisions',type=Path,default=reviewed if reviewed.is_file() else None)
    ap.add_argument('--output',type=Path,default=REPO/'results/repair-20261001/future-n3-manifest.json')
    ap.add_argument('--audit-status',choices=('in_progress','repair_audit_complete'),default='in_progress',
                    help='repair handoff status only; never changes action readiness')
    args=ap.parse_args();path=args.inventory.resolve();inventory=json.loads(path.read_text())
    decisions=json.loads(args.decisions.read_text()) if args.decisions else {}
    result=build(REPO,inventory,path,decisions)
    result['audit_status']=args.audit_status
    atomic_json(args.output,result)
    print(json.dumps(result['summary'],indent=2))


if __name__=='__main__':main()
