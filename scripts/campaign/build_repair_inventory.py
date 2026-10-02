#!/usr/bin/env python3
"""Reconcile original campaign attempts, staged evaluations and legacy GNSS.

Read-only with respect to evidence; emits a separate inventory. This inventory
counts evaluated artifacts, never grants publication qualification from counts.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_quality_campaign import expand_cells, cell_key, load_manifest
from run_repetitions import atomic_json
from protocol_findings import historical_findings
from qualification_review import review_saved, review_identity
from acceptance_ledger import cell_acceptance

REPO=Path(__file__).resolve().parents[2]
MODES=('vo','vo-lc','vio','vio-lc','gnss-vio')
SERVER='machine-3c9dca59a50f'
SELECTION='configs/campaigns/euroc-focused-attempts-20261001.json'
ZED_SELECTION='configs/campaigns/zed-vio-first-attempts-20261002.json'


def completed_zed_selections(repo):
    """Retain predeclared completed slots, including failures, without granting acceptance."""
    path=repo/ZED_SELECTION
    if not path.is_file():return {}
    value=read(path)
    if value.get('schema')!=1:raise ValueError('unsupported completed ZED selection schema')
    def checked(item):
        relative=Path(item['path'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('unsafe completed-selection evidence path')
        p=repo/relative
        if not p.is_file() or evidence(p,repo)['sha256']!=item['sha256']:
            raise ValueError('stale completed-selection evidence: '+str(relative))
        return p
    manifest=read(checked(value['source_manifest']))
    checked(value['batch_selection']);checked(value['pause_record'])
    selected={};allowed={'orbslam3','okvis2','okvis2x'}
    for record in value['completed']:
        key=record['cell'];parts=key.split('/')
        if (len(parts)!=4 or parts[:3]!=['vio','zed2i','field1_110426_full_10fps_q90']
                or parts[3] not in allowed or key in selected):
            raise ValueError('unexpected or duplicate completed ZED cell')
        if record['repetition']!=1 or record['physical_run_id']!=10001:
            raise ValueError('selection must retain the predeclared first physical attempt')
        actions=[a for a in manifest['actions'] if a['id']==record['action_id']]
        if (len(actions)!=1 or actions[0]['cell']!=key or actions[0]['repetition']!=1
                or actions[0]['planned_output']!=record['path']
                or record['path']!=f'results/{key}/run10001'):
            raise ValueError('completed attempt differs from executed plan')
        for item in record['evidence']:checked(item)
        state=read(checked(record['attempt_state']))
        if state.get('identity')!=dict(cohort=actions[0]['cohort'],repetition=1,physical_run_id=10001):
            raise ValueError('completed attempt identity differs from executed plan')
        if state.get('status') not in ('evaluated','evaluated_failure_or_review','no_trajectory','evaluation_failed'):
            raise ValueError('attempt is not terminal; do not select a live or interrupted capture')
        selected[key]=[10001,2,3]
    if len(selected)!=3 or value.get('cells')!=selected:
        raise ValueError('completed selection must retain all three started cells, regardless of outcome')
    return selected


def selected_attempts(repo):
    path=repo/SELECTION
    if not path.is_file():return {}
    value=read(path)
    if value.get('schema')!=1:raise ValueError('unsupported selected-attempt schema')
    result={}
    for key,ids in value['cells'].items():
        mode,ds,seq,algo=key.split('/')
        if (mode not in ('vio','vio-lc') or ds!='euroc_mav' or algo!='airslam'
            or seq not in ('MH_01_easy','MH_03_medium','MH_05_difficult')
            or ids!=[4,5,6]):
            raise ValueError('selection must match the outcome-blind corrected EuRoC campaign')
        result[key]=ids
    if len(result)!=6:raise ValueError('corrected cohort must include all six declared cells')
    return result


def evidence(path,repo):
    return dict(path=str(path.relative_to(repo)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def read(path):
    return json.loads(path.read_text()) if path.is_file() else {}


def cohort_artifacts(provenance, run_dir=None):
    """Group new receipts by settings, not attempt paths or measured outcomes.

    Historical signatures stay byte-based. Schema 2 is explicitly declared by
    new runners; every normalized receipt is verified against its saved hash.
    Raw receipts remain in the evidence inventory and are never rewritten.
    """
    semantic = provenance.get('parameters', {}).get('cohort_artifact_semantics') == 2
    receipts = {'candidate_selection', 'input_clock_policy', 'native_settings_policy',
                'native_parameter_list.txt', 'native_camera_load.txt'}
    result = []
    for artifact in provenance.get('artifacts', []):
        role = artifact.get('role')
        digest = artifact.get('snapshot_sha256') or artifact.get('sha256')
        if semantic and (role in receipts or role == 'native_input_receipt.json'):
            if run_dir is None or not artifact.get('snapshot'):
                raise ValueError('saved receipt required for cohort normalization')
            path = Path(run_dir)/artifact['snapshot']
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != digest:
                raise ValueError('changed cohort receipt: '+str(path))
            if role == 'native_input_receipt.json':
                # Received/processed frame counts are observations, never
                # experimental settings or grounds for merging different inputs.
                continue
            text = raw.decode()
            attempt = Path(run_dir).resolve()
            parts = attempt.parts
            index = len(parts)-1-list(reversed(parts)).index('results')
            container_path = '/'+Path(*parts[index:]).as_posix()
            for prefix in sorted({str(attempt), container_path}, key=len, reverse=True):
                text = text.replace(prefix, '<attempt>')
            digest = hashlib.sha256(text.encode()).hexdigest()
        result.append(dict(role=role, sha256=digest))
    return sorted(result, key=lambda r: json.dumps(r, sort_keys=True))


def cohort_identity(meta, algorithm, *, run_dir=None):
    """Group recorded effective settings, not just similarly named config files.

    Historical hashes identify historical bytes: never translate run records
    through an author-rewrite map. DPVO's recorded repetition seed is the sole
    excluded parameter; different seeds are intentional repeated trials.
    A signature groups evidence, it does not certify its completeness.
    """
    provenance = meta.get('provenance', {})
    if not provenance:
        return None, None
    parameters = dict(provenance.get('parameters', {}))
    if algorithm == 'dpvo':
        parameters.pop('seed', None)
    def ordered(records):
        return sorted(records, key=lambda r: json.dumps(r, sort_keys=True))
    payload = dict(
        artifacts=cohort_artifacts(provenance, run_dir),
        sources=ordered([{k: s.get(k) for k in ('role','path','commit','dirty','diff_sha256')}
                         for s in provenance.get('sources', [])]),
        binaries=ordered([{k: b.get(k) for k in ('role','path','sha256')}
                          for b in provenance.get('binaries', [])]),
        parameters=parameters, workspace=provenance.get('workspace'),
        environment={k: v for k, v in provenance.get('environment', {}).items() if k != 'snapshot'},
        container=provenance.get('container'), runtime=provenance.get('runtime'),
        machine_id=meta.get('machine_id'),
    )
    # Source-capture receipts include wall time and capture duration. Group by
    # verified content instead, while retaining historical signatures exactly.
    capture = provenance.get('implementation_capture')
    if capture:
        if run_dir is None:
            raise ValueError('run directory required to verify implementation capture')
        def verified_snapshot(record):
            path = Path(run_dir) / record['snapshot']
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != record['snapshot_sha256']:
                raise ValueError('changed or missing cohort capture: ' + str(path))
            return json.loads(path.read_text())
        implementation = verified_snapshot(capture)
        if implementation.get('schema') != 1 or not implementation.get('trees'):
            raise ValueError('unsupported or empty implementation capture')
        workspace = provenance.get('workspace') or {}
        if (workspace.get('snapshot') != capture['snapshot'] or
                workspace.get('snapshot_sha256') != capture['snapshot_sha256']):
            raise ValueError('workspace and implementation capture disagree')
        payload['workspace'] = {k: v for k, v in workspace.items()
                                if k not in ('snapshot', 'snapshot_sha256', 'capture_role')}
        payload['implementation_content_sha256'] = hashlib.sha256(json.dumps(
            implementation['trees'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        assets = provenance.get('runtime_assets')
        if assets:
            runtime = verified_snapshot(assets)
            content = hashlib.sha256(json.dumps({k: v for k, v in runtime.items() if k != 'sha256'},
                sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
            if runtime.get('sha256') != content or assets.get('content_sha256') != content:
                raise ValueError('runtime cohort content digest disagrees')
            payload['runtime_content_sha256'] = content
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return digest, payload


def saved_attempt(repo,relative,stage):
    run=repo/'results'/relative;meta=read(run/'run_meta.json')
    staged=stage/'evaluations'/relative/'run_eval.json'
    published=run/'run_eval.json'
    value=read(staged if staged.is_file() else published)
    current=published if not staged.is_file() or (published.is_file() and staged.read_bytes()==published.read_bytes()) else staged
    blockers=[]
    if value:
        for item in value.get('evaluation_provenance',{}).get('inputs',[])+value.get('pose_frames',{}).get('evidence',[]):
            p=repo/item['path']
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:
                blockers.append('staged_input_changed:'+item['path'])
    if blockers:
        raise ValueError('; '.join(blockers))
    mode,ds,seq,algo,name=Path(relative).parts
    snapshot_records=[]
    for item in meta.get('provenance',{}).get('artifacts',[]):
        if item.get('snapshot'):
            p=run/item['snapshot'];actual=evidence(p,repo) if p.is_file() else None
            snapshot_records.append(dict(role=item['role'],saved=item.get('snapshot_sha256'),actual=actual,
                verified=actual is not None and actual['sha256']==item.get('snapshot_sha256')))
    files=[evidence(run/n,repo) for n in ('trajectory.txt','run_meta.json','run_eval.json','run_log.txt') if (run/n).is_file()]
    files.extend(value.get('evaluation_provenance',{}).get('inputs',[]))
    files.extend(value.get('pose_frames',{}).get('evidence',[]))
    files.extend(s['actual'] for s in snapshot_records if s['actual'])
    if staged.is_file():files.append(evidence(staged,repo))
    files=list({item['path']:item for item in files}.values())
    process=meta.get('process',{})
    cohort,cohort_evidence=cohort_identity(meta,algo,run_dir=run)
    findings=historical_findings(repo,relative,meta)
    qualification=review_saved(relative,meta,value,findings,snapshot_records,exists=run.is_dir(),repo=repo)
    return dict(path='results/'+relative,exists=run.is_dir(),files=files,
        trajectory_saved=(run/'trajectory.txt').is_file(),historical_complete=(run/'COMPLETE').is_file(),
        evaluated=bool(value),evaluation_path=str(current.relative_to(repo)) if value else None,
        staged_evaluation_path=str(staged.relative_to(repo)) if staged.is_file() and value else None,
        numerical_status=value.get('run_status'),process=process,
        qualification=qualification,confirmed_protocol_findings=findings,
        pose_frame_blockers=value.get('pose_frames',{}).get('blockers',[]),
        snapshots=snapshot_records,source_records=meta.get('provenance',{}).get('sources',[]),
        parameters=meta.get('provenance',{}).get('parameters',{}),
        cohort_fingerprint=cohort,cohort_evidence=cohort_evidence,
        config_fingerprint=(hashlib.sha256(json.dumps(cohort_artifacts(meta['provenance'],run),sort_keys=True).encode()).hexdigest()
            if meta.get('provenance',{}).get('parameters',{}).get('cohort_artifact_semantics')==2
            else hashlib.sha256(json.dumps(sorted((s['role'],s['saved']) for s in snapshot_records),sort_keys=True).encode()).hexdigest() if snapshot_records else None),
        machine_id=meta.get('machine_id'),runtime=meta.get('measurements',{}),
        coverage=value.get('coverage',{}),failure_reason=process.get('failure_reason') or value.get('failure_reason'))


def runtime_estimate(attempts):
    # Use the same cell and server only. Failed/partial/shutdown attempts and
    # confirmed invalid configurations cannot establish a corrected run's time.
    times=[];sources=[];modes=set()
    for a in attempts:
        runtime=a['runtime'];seconds=runtime.get('end_to_end_time_s')
        coverage=a.get('coverage',{}).get('coverage_gap_pct')
        if (a['machine_id']==SERVER and a['process'].get('exit_code')==0 and
            not a.get('confirmed_protocol_findings') and
            not a.get('qualification',{}).get('native_error_observations') and
            a['numerical_status']=='ok' and isinstance(seconds,(int,float)) and seconds>0 and
            isinstance(coverage,(int,float)) and coverage>=95):
            times.append(seconds);sources.append(a['path']);modes.add(runtime.get('mode'))
    if not times:
        return dict(estimate_s=None,observed_range_s=None,reason='no complete comparable same-cell server sample',sources=[])
    return dict(estimate_s=statistics.median(times),observed_range_s=[min(times),max(times)],
                measurement_modes=sorted(modes),sources=sources,
                uncertainty='observed historical range, not a confidence interval; configuration/runner changes may alter runtime')


def attempt_directories(repo):
    # Interrupted startup can leave logs/process evidence before run_meta exists.
    # Directory presence is an attempted slot, never a successful evaluation.
    return {p for mode in MODES for p in (repo/'results'/mode).glob('*/*/*/run*') if p.is_dir()}


def build(repo,stage):
    executed,executed_hash=load_manifest(repo/'logs/server-campaign/quality-final-n3-no-gnss/manifest.json')
    future,future_hash=load_manifest(repo/'configs/campaigns/quality-final.json')
    cells=[];members=set();selections=selected_attempts(repo);superseded=set()
    zed_selections=completed_zed_selections(repo);selections.update(zed_selections)
    for cell in expand_cells(future):
        key=cell_key(cell);attempts=[]
        ids=selections.get(key,[1,2,3])
        if key in selections:superseded.update(f'{key}/run{i}' for i in (1,2,3))
        for repetition,physical_id in enumerate(ids,1):
            relative=f'{key}/run{physical_id}';members.add(relative)
            attempt=saved_attempt(repo,relative,stage)
            attempt['logical_repetition']=repetition
            attempts.append(attempt)
        cells.append(dict(**cell,variant='default',key=key,target_repetitions=3,
            comparison_membership=('corrected_zed_first_20261002_pending_claim_review' if key in zed_selections
                else 'corrected_euroc_20261001' if key in selections else None),
            original_campaign_member=cell['algorithm'] in executed['tables'][cell['run_type']],
            attempts=attempts,evaluated=sum(a['evaluated'] for a in attempts),
            outcomes=dict(Counter(a['numerical_status'] for a in attempts if a['evaluated'])),
            within_cell_config_consistent=len({a['config_fingerprint'] for a in attempts if a['config_fingerprint']})<=1,
            within_cell_cohort_consistent=len({a['cohort_fingerprint'] for a in attempts if a['cohort_fingerprint']})<=1,
            runtime_estimate=runtime_estimate(attempts),
            acceptance=cell_acceptance(attempts, len({a['cohort_fingerprint'] for a in attempts if a['cohort_fingerprint']})<=1)))
    other=[]
    paths=attempt_directories(repo)
    for run in sorted(paths):
        relative=str(run.relative_to(repo/'results'))
        if relative in members:continue
        name=run.name;algo=run.parent.name;mode=run.relative_to(repo/'results').parts[0]
        category=('superseded_calibration_cohort' if relative in superseded else
                  'gnss_variant' if mode=='gnss-vio' and '_' in name else
                  'historical_excluded' if algo in future['excluded'] else 'smoke_or_outside_protocol')
        other.append(dict(category=category,**saved_attempt(repo,relative,stage)))
    totals={}
    for mode in MODES:
        selected=[c for c in cells if c['run_type']==mode]
        totals[mode]=dict(cells=len(selected),target_attempts=3*len(selected),evaluated=sum(c['evaluated'] for c in selected),
             evaluated_n3=sum(c['evaluated']==3 for c in selected),evaluated_n1=sum(c['evaluated']==1 for c in selected),
             evaluated_n0=sum(c['evaluated']==0 for c in selected),
             outcomes=dict(sum((Counter(c['outcomes']) for c in selected),Counter())))
    return dict(schema_version=1,audit_status='in_progress',qualification_review=review_identity(repo),
        attempt_selection=evidence(repo/SELECTION,repo) if (repo/SELECTION).is_file() else None,
        additional_attempt_selections=[evidence(repo/ZED_SELECTION,repo)] if zed_selections else [],
        original_manifest=dict(path='logs/server-campaign/quality-final-n3-no-gnss/manifest.json',sha256=executed_hash),
        scope_source=dict(path='configs/campaigns/quality-final.json',sha256=future_hash,
                          note='algorithm/dataset membership retained; future repeat target is 3, not the historical proposal of 5'),
        staged_evaluator=read(stage/'staging_manifest.json').get('evaluator'),
        excluded=future['excluded'],counts=totals,cells=cells,other_artifacts=other)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stage',type=Path,default=REPO/'results/repair-20261001')
    ap.add_argument('--output',type=Path,default=REPO/'results/repair-20261001/inventory.json')
    ap.add_argument('--audit-status',choices=('in_progress','repair_audit_complete'),default='in_progress',
                    help='repair handoff status only; publication qualification remains separate')
    args=ap.parse_args();out=build(REPO,args.stage.resolve())
    out['audit_status']=args.audit_status
    atomic_json(args.output,out)
    print(json.dumps(dict(counts=out['counts'],other_artifacts=dict(Counter(a['category'] for a in out['other_artifacts']))),indent=2))


if __name__=='__main__':main()
