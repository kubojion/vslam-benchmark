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
from protocol_findings import historical_findings, USER_RERUN_DECISIONS
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


BATCH_SELECTIONS=('configs/campaigns/zed-vio-n3-attempts-20261003.json','configs/campaigns/production-attempts-20261004.json',
                  'configs/campaigns/production-replacements-20261005.json','configs/campaigns/production-replacements-20261005b.json',
                  'configs/campaigns/production-attempts-20261005c.json')
# Comparison group recorded on the cells each batch selection lists.
BATCH_LABELS={'configs/campaigns/zed-vio-n3-attempts-20261003.json':'zed_vio_n3_20261003',
              'configs/campaigns/production-attempts-20261004.json':'production_20261004',
              'configs/campaigns/production-replacements-20261005.json':'production_20261004',
              'configs/campaigns/production-replacements-20261005b.json':'production_20261004',
              'configs/campaigns/production-attempts-20261005c.json':'production_20261005_rule_c'}
TERMINAL=('evaluated','evaluated_failure_or_review','no_trajectory','evaluation_failed')


def decided_replacement(repo, attempt):
    """True when a recorded user rerun decision supersedes this attempt (path relative to results/)."""
    for name in USER_RERUN_DECISIONS:
        path=repo/name
        if path.is_file() and attempt in read(path).get('attempts',{}):return True
    return False


def completed_batch_selections(repo, earlier, labels=None):
    """Select the terminal attempts of a completed later batch, regardless of outcome.

    Every repetition listed for a cell is either an attempt of this batch (checked
    against the frozen executed plan, the batch status and its attempt state), the
    same physical attempt an earlier verified selection already chose, or the cell's
    default slot (physical id = repetition) when the batch did not run it. The batch
    status is a batch driver's attempt list or a frozen run_future_manifest state.
    A later record may list a cell an earlier record listed, filling only repetitions
    still at their default slot; it never replaces an attempt already selected, unless a
    recorded user rerun decision (protocol_findings.USER_RERUN_DECISIONS) supersedes that
    attempt.
    """
    selected={}
    for name in BATCH_SELECTIONS:
        path=repo/name
        if not path.is_file():continue
        value=read(path)
        if value.get('schema')!=1:raise ValueError('unsupported batch selection schema')
        def checked(item):
            relative=Path(item['path'])
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('unsafe batch-selection evidence path')
            p=repo/relative
            if not p.is_file() or evidence(p,repo)['sha256']!=item['sha256']:
                raise ValueError('stale batch-selection evidence: '+str(relative))
            return p
        manifest=read(checked(value['source_manifest']))
        status=read(checked(value['batch_status']))
        if 'attempts' in status:
            finished={str(a.get('output','')).split('/results/',1)[-1]:a for a in status['attempts'] if a.get('status')=='finished'}
        else:  # run_future_manifest state: per-action status, outputs from the executed plan
            if status.get('manifest_sha256')!=value['source_manifest']['sha256']:
                raise ValueError('executor state belongs to another plan revision')
            outputs={a['id']:a['planned_output'] for a in manifest['actions']}
            finished={outputs[i].removeprefix('results/'):a for i,a in status['actions'].items()
                      if a.get('status') in ('evaluated','failure_or_review')}
        records={(r['cell'],r['repetition']):r for r in value['completed']}
        if len(records)!=len(value['completed']):raise ValueError('duplicate batch-selection record')
        listed=set()
        for key,ids in value['cells'].items():
            if key in listed or len(ids)!=3:raise ValueError('batch selection must list three repetitions once per cell')
            listed.add(key)
            prior=selected.get(key) or earlier.get(key,[None]*3)
            for repetition,run_id in enumerate(ids,1):
                record=records.pop((key,repetition),None)
                if record is None:
                    if prior[repetition-1]!=run_id and run_id!=repetition:
                        raise ValueError(f'{key} r{repetition}: neither in this batch, previously selected nor the default slot')
                    continue
                if (key in selected and selected[key][repetition-1]!=repetition
                        and not decided_replacement(repo,f'{key}/run{selected[key][repetition-1]}')):
                    raise ValueError(f'{key} r{repetition}: a later batch may not replace an attempt an earlier batch selected')
                if record['physical_run_id']!=run_id or record['path']!=f'results/{key}/run{run_id}':
                    raise ValueError('batch record differs from its cell listing: '+key)
                actions=[a for a in manifest['actions'] if a['id']==record['action_id']]
                if (len(actions)!=1 or actions[0]['cell']!=key or actions[0]['repetition']!=repetition
                        or actions[0]['planned_output']!=record['path']):
                    raise ValueError('completed attempt differs from executed plan: '+record['action_id'])
                if record['path'].removeprefix('results/') not in finished:
                    raise ValueError('batch status does not list a finished attempt at '+record['path'])
                state=read(checked(record['attempt_state']))
                if state.get('identity')!=dict(cohort=actions[0]['cohort'],repetition=repetition,physical_run_id=run_id):
                    raise ValueError('completed attempt identity differs from executed plan: '+record['path'])
                if state.get('status') not in TERMINAL:
                    raise ValueError('attempt is not terminal; do not select a live or interrupted capture')
            selected[key]=list(ids)
            if labels is not None:labels[key]=BATCH_LABELS[name]
        if records:raise ValueError('batch records without a cell listing: '+', '.join(r['path'] for r in records.values()))
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


# Effective configurations whose native node needs the attempt's own output directory written into
# them (SVO Pro: trace_dir); that path is not a setting and is normalized like receipt paths.
ATTEMPT_PATH_CONFIGS = {('svo_pro', 'effective_config')}


def cohort_artifacts(provenance, run_dir=None, algorithm=None):
    """Group new receipts by settings, not attempt paths or measured outcomes.

    Historical signatures stay byte-based, except configurations listed in
    ATTEMPT_PATH_CONFIGS. Schema 2 is explicitly declared by new runners; every
    normalized receipt is verified against its saved hash. Raw receipts remain in
    the evidence inventory and are never rewritten.
    """
    semantic = provenance.get('parameters', {}).get('cohort_artifact_semantics') == 2
    receipts = {'candidate_selection', 'input_clock_policy', 'native_settings_policy',
                'native_parameter_list.txt', 'native_camera_load.txt'}
    result = []
    for artifact in provenance.get('artifacts', []):
        role = artifact.get('role')
        digest = artifact.get('snapshot_sha256') or artifact.get('sha256')
        if (semantic and (role in receipts or role == 'native_input_receipt.json')) or (algorithm, role) in ATTEMPT_PATH_CONFIGS:
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
    through an author-rewrite map. The recorded repetition seed of DPVO and
    MASt3R-Fusion (1000 + physical run id) is excluded; different seeds are
    intentional repeated trials. So is ORB-SLAM3's trajectory_canonicalization
    marker: the runner records it only after a trajectory was exported, so an
    attempt that crashed earlier lacks it, and its policy lives in the runner,
    which the implementation capture already pins.
    A signature groups evidence, it does not certify its completeness.
    """
    provenance = meta.get('provenance', {})
    if not provenance:
        return None, None
    parameters = dict(provenance.get('parameters', {}))
    if algorithm in ('dpvo', 'mast3r_fusion'):
        parameters.pop('seed', None)
    if algorithm == 'orbslam3':
        parameters.pop('trajectory_canonicalization', None)
    def ordered(records):
        return sorted(records, key=lambda r: json.dumps(r, sort_keys=True))
    payload = dict(
        artifacts=cohort_artifacts(provenance, run_dir, algorithm),
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


POOLING='configs/campaigns/zed-vio-cohort-pooling-20261003.json'
# Rule C cells whose counted repetitions span workspace commits (11 Nov 2026). Same policy and check.
RULEC_POOLING='configs/campaigns/rule-c-cohort-pooling-20261111.json'
POOLING_RECORDS=(POOLING,RULEC_POOLING)
# User decision of 12 Nov 2026 (option b): receipt differences in six named Rule C cells that cannot act on the
# estimate, each recorded with its exact per-run value and the reason. A decision with reasons, not a disclosure.
NONACTING='configs/campaigns/rule-c-nonacting-differences-20261112.json'
NONACTING_KINDS=('artifact','parameter')


def nonacting_record(repo):
    path=repo/NONACTING
    if not path.is_file():return None,{}
    record=read(path)
    if record.get('schema')!=1:raise ValueError('unsupported non-acting difference schema')
    for key,spec in record['cells'].items():
        if not spec.get('differences') or any(d.get('kind') not in NONACTING_KINDS or not d.get('reason')
                                              or set(d['per_run'])!={str(i) for i in spec['runs']} for d in spec['differences']):
            raise ValueError('non-acting difference needs a kind, a reason and a value for every listed run: '+key)
    return path,record['cells']


def config_consistent(attempts,pooling):
    """One configuration per cell. A cell the user's non-acting record pooled counts as one configuration: its
    configuration receipts differ only in the declared fields with their recorded values (pooled_cohort checked
    every other receipt byte for byte). Every other cell keeps the plain fingerprint comparison."""
    if len({a['config_fingerprint'] for a in attempts if a['config_fingerprint']})<=1:return True
    return bool(pooling and pooling.get('status')=='pooled' and pooling.get('nonacting_user_decision'))


def check_nonacting_scope(repo,completion,corrected):
    """The record may name only reselected Rule C cells listed with the same runs in the Rule C pooling record."""
    path,cells=nonacting_record(repo)
    if not cells:return
    pooling=read(repo/RULEC_POOLING).get('cells',{})
    for key,spec in cells.items():
        if key in corrected:raise ValueError('non-acting record may not name a corrected CitrusFarm cell: '+key)
        if completion.get(key)!=spec['runs'] or (pooling.get(key) or {}).get('runs')!=spec['runs']:
            raise ValueError('non-acting record names a cell or runs outside the Rule C pooling: '+key)


def accepted_options(record, spec):
    """Merge a cell's options whose named user decision in the record is accepted.

    A record may list a difference that pools only after a user decision
    (`pending_user_decisions.<name>.accept`, one switch per decision); until then the
    option is ignored and the cell is checked without it.
    """
    spec=dict(spec);decisions=record.get('pending_user_decisions') or {}
    for name,option in (spec.get('options_if_accepted') or {}).items():
        if name not in decisions or type(decisions[name].get('accept')) is not bool:
            raise ValueError('pooling option without a recorded decision: '+name)
        if decisions[name]['accept']:
            for field,value in option.items():
                spec[field]=({**spec.get(field,{}),**value} if isinstance(value,dict)
                             else sorted(set(spec.get(field,[]))|set(value)))
            spec.setdefault('accepted_decisions',[]).append(name)
            if decisions[name].get('disclosure'):spec.setdefault('disclosures',[]).append(decisions[name]['disclosure'])
    return spec


def pooled_cohort(repo, key, attempts, records=POOLING_RECORDS):
    """Pool one listed cell across workspace commits only when its receipts allow it.

    The reviewed record names the cell, its physical runs and any diagnostic parameter
    that may be absent in older runs at its default value. Everything else recorded for
    the estimate must be byte-identical: effective configuration, binaries, runtime
    assets, algorithm source tree, parameters, environment, container and machine. Only
    the workspace commit and the scripts/configs tree may differ. A mismatch refuses
    pooling (separate groups stay separate) and records why.

    A cell may be listed by more than one record (an earlier selection and a later one);
    the record whose runs equal the selected attempts applies. A cell listed only with
    other runs is refused, as before.
    """
    listed=[]
    for name in records:
        path=repo/name
        if not path.is_file():continue
        record=read(path)
        if record.get('schema')!=1:raise ValueError('unsupported cohort pooling schema')
        spec=record['cells'].get(key)
        if spec:listed.append((path,accepted_options(record,spec)))
    if not listed:return None
    selected=[a['path'] for a in attempts]
    path,spec=next(((p,s) for p,s in listed if [f'results/{key}/run{i}' for i in s['runs']]==selected),listed[-1])
    expected=[f'results/{key}/run{i}' for i in spec['runs']]
    def refused(reason):
        return dict(status='refused',reason=reason,record=evidence(path,repo),runs=expected)
    if [a['path'] for a in attempts]!=expected:
        return refused('selected attempts differ from the pooling record')
    nonacting_path,nonacting_cells=nonacting_record(repo) if path==repo/RULEC_POOLING else (None,{})
    nonacting=nonacting_cells.get(key)
    if nonacting is not None and nonacting['runs']!=spec['runs']:
        return refused('non-acting record was made for other runs')
    reduced=[];commits=set()
    for a in attempts:
        payload=dict(a.get('cohort_evidence') or {})
        if not payload:return refused('missing cohort receipt: '+a['path'])
        commits.add((payload.pop('workspace',None) or {}).get('commit'))
        payload.pop('implementation_content_sha256',None)
        parameters=dict(payload.get('parameters',{}))
        for name,default in spec.get('ignored_parameters',{}).items():
            if parameters.pop(name,default)!=default:
                return refused(f'{name} differs from its default in {a["path"]}')
        # A listed harness limit (a stage watchdog) may differ only if no listed run stopped at a
        # limit or failed: every one exited 0, so the limit never acted on the estimate.
        for name in spec.get('unreached_harness_limits',{}):
            if name in parameters and (a.get('process') or {}).get('exit_code')!=0:
                return refused(f'{name} differs and {a["path"]} did not exit 0')
            parameters.pop(name,None)
        if nonacting is not None:
            # Only the recorded field, only with exactly the recorded value of this run.
            run_id=a['path'].rsplit('/run',1)[1]
            for d in nonacting['differences']:
                recorded=d['per_run'][run_id]
                if d['kind']=='artifact':
                    found=[x['sha256'] for x in payload.get('artifacts',[]) if x['role']==d['role']]
                    if (found[0] if len(found)==1 else None if not found else 'several')!=recorded:
                        return refused(f"{d['role']} of {a['path']} differs from the non-acting record")
                    payload['artifacts']=[x for x in payload.get('artifacts',[]) if x['role']!=d['role']]
                else:
                    if parameters.get(d['name'])!=recorded:
                        return refused(f"{d['name']} of {a['path']} differs from the non-acting record")
                    parameters.pop(d['name'],None)
        payload['parameters']=parameters
        if spec.get('ignored_runtime_fields'):
            # Harness runtime facts (e.g. the wrapper's Python version), listed after a user decision.
            payload['runtime']={k:v for k,v in (payload.get('runtime') or {}).items() if k not in spec['ignored_runtime_fields']}
        meta=read(repo/a['path']/'run_meta.json')
        capture=meta.get('provenance',{}).get('implementation_capture') or {}
        snapshot=repo/a['path']/capture.get('snapshot','')
        if not capture or not snapshot.is_file() or hashlib.sha256(snapshot.read_bytes()).hexdigest()!=capture.get('snapshot_sha256'):
            return refused('missing or changed implementation capture: '+a['path'])
        payload['algorithm_trees']=[t for t in read(snapshot)['trees'] if t.get('role')=='algorithm']
        if not payload['algorithm_trees']:return refused('no algorithm source tree in '+a['path'])
        reduced.append(payload)
    if any(r!=reduced[0] for r in reduced[1:]):
        return refused('algorithm-relevant receipts differ between the listed runs')
    cohort='pooled-'+hashlib.sha256(json.dumps(reduced[0],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return dict(status='pooled',cohort=cohort,record=evidence(path,repo),runs=expected,
                workspace_commits=sorted(c for c in commits if c),
                recorded_cohorts=[a['cohort_fingerprint'] for a in attempts],
                ignored_parameters=spec.get('ignored_parameters',{}),
                unreached_harness_limits=spec.get('unreached_harness_limits',{}),
                ignored_runtime_fields=spec.get('ignored_runtime_fields',[]),
                accepted_decisions=spec.get('accepted_decisions',[]),
                disclosures=spec.get('disclosures',[]),
                **(dict(nonacting_user_decision=dict(record=evidence(nonacting_path,repo),
                    fields=[d.get('role') or d.get('name') for d in nonacting['differences']])) if nonacting is not None else {}))


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
        config_fingerprint=(hashlib.sha256(json.dumps(cohort_artifacts(meta['provenance'],run,algo),sort_keys=True).encode()).hexdigest()
            if (meta.get('provenance',{}).get('parameters',{}).get('cohort_artifact_semantics')==2
                or (snapshot_records and any(a==algo for a,_ in ATTEMPT_PATH_CONFIGS)))
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


# CitrusFarm with its camera-IMU offset removed: user-accepted attempts that replace every
# earlier attempt of these cells, without changing any dataset file in place (2 Nov 2026).
CORRECTED_SELECTION='configs/campaigns/timing-corrected-attempts-20261102.json'
CORRECTED_LABEL='timing_corrected_20261102'
CORRECTED_FIRST_ID=50000


def corrected_selections(repo):
    path=repo/CORRECTED_SELECTION
    if not path.is_file():return {}
    value=read(path)
    if value.get('schema')!=1:raise ValueError('unsupported corrected selection schema')
    result={}
    for key,ids in value['cells'].items():
        if len(ids)!=3 or min(ids)<=CORRECTED_FIRST_ID:raise ValueError('corrected selection needs three new attempts: '+key)
        for repetition,run_id in enumerate(ids,1):
            state=read(repo/'results/.attempt-state'/key.replace('/','__')/f'run{run_id}.json')
            identity=state.get('identity',{})
            if (identity.get('cohort') not in value['cohorts'] or identity.get('repetition')!=repetition
                    or identity.get('physical_run_id')!=run_id or identity.get('input_variant')!=value['input_variant']):
                raise ValueError(f'corrected attempt identity differs from the selection: {key}/run{run_id}')
            if state.get('status') not in TERMINAL:
                raise ValueError('attempt is not terminal; do not select a live or interrupted capture')
        result[key]=list(ids)
    return result


def corrected_superseded(repo,key):
    """Every earlier attempt of a corrected cell, selected before or not, is the uncorrected cohort."""
    return {f'{key}/{p.name}' for p in (repo/'results'/key).glob('run*')
            if p.is_dir() and int(p.name[3:])<CORRECTED_FIRST_ID}


# Every counted Rule C attempt that the progress publisher and the paper use, plus the user's
# later decisions (PLAN Update 10 A and D, 11 Nov 2026 Sielinko VO-LC closure). It is the top
# layer: it may replace an attempt any earlier layer selected, but only the one that layer
# selected at the time (recorded as `previous`), and never a corrected CitrusFarm cell.
PAPER_COMPLETION_SELECTION='configs/campaigns/paper-completion-attempts-20261111.json'
PAPER_COMPLETION_LABEL='rule_c_paper_completion_20261111'
CLOSED_DISPOSITIONS=('did_not_finish',)


def attempt_state_path(repo,key,run_id):
    return repo/'results/.attempt-state'/key.replace('/','__')/f'run{run_id}.json'


def paper_completion_selections(repo,lower,corrected=()):
    """Return (cells, superseded attempts, closed-cell dispositions) of the paper completion record.

    `lower` is the selection every earlier layer produced. For each listed cell the record states
    that earlier selection as `previous`; a difference refuses the record (it was made against
    another main). A repetition keeps its previous attempt, or names a new attempt whose saved
    attempt state is terminal and whose identity (repetition, physical id, cohort) equals the
    record, unless the record lists that exact differing identity as a reviewed exception.
    A closed cell (did not finish) may keep one non-terminal attempt, pinned by the hash of
    its attempt state, and default slots that were never run. Previously selected attempts the
    record replaces are returned as superseded (historical cohort), never deleted.
    """
    path=repo/PAPER_COMPLETION_SELECTION
    if not path.is_file():return {},set(),{}
    value=read(path)
    if value.get('schema')!=1:raise ValueError('unsupported paper completion selection schema')
    attempts=value.get('attempts',{});exceptions=value.get('identity_exceptions',{});closed=value.get('closed_cells',{})
    cells={};superseded=set()
    for key,ids in value['cells'].items():
        if len(ids)!=3 or len(set(ids))!=3:raise ValueError('paper completion selection needs three distinct attempts: '+key)
        if key in corrected:raise ValueError('paper completion selection may not change a corrected CitrusFarm cell: '+key)
        previous=[int(i) for i in lower.get(key,[1,2,3])]
        if value['previous'].get(key)!=previous:
            raise ValueError(f'{key}: earlier selection differs from the one this record replaces')
        disposition=closed.get(key)
        if disposition is not None and disposition.get('disposition') not in CLOSED_DISPOSITIONS:
            raise ValueError('unknown closed-cell disposition: '+key)
        for repetition,run_id in enumerate(ids,1):
            relative=f'{key}/run{run_id}'
            state_path=attempt_state_path(repo,key,run_id)
            if disposition is not None and run_id==repetition:
                # A default slot of a closed cell: never run, so it must not exist.
                if (repo/'results'/relative).exists() or state_path.exists():
                    raise ValueError('closed cell lists a default slot that was run: '+relative)
                continue
            if run_id==previous[repetition-1]:continue
            record=attempts.get(relative)
            if record is None or record.get('repetition')!=repetition:
                raise ValueError('selected attempt is not recorded for its repetition: '+relative)
            state=read(state_path);identity=state.get('identity',{})
            expected=dict(cohort=record['cohort'],repetition=repetition,physical_run_id=run_id)
            if identity!=expected:
                allowed=exceptions.get(relative)
                if not allowed or allowed.get('recorded_identity')!=identity or identity.get('physical_run_id')!=run_id:
                    raise ValueError('selected attempt identity differs from the record: '+relative)
            if state.get('status') not in TERMINAL:
                pinned=(disposition or {}).get('open_attempts',{}).get(relative)
                if (not pinned or state.get('status')!=pinned.get('status') or not state_path.is_file()
                        or hashlib.sha256(state_path.read_bytes()).hexdigest()!=pinned.get('attempt_state_sha256')):
                    raise ValueError('attempt is not terminal; do not select a live or interrupted capture: '+relative)
        cells[key]=list(ids)
        superseded.update(f'{key}/run{i}' for i in previous if i not in ids)
    if set(closed)-set(cells):raise ValueError('closed cell without a selection: '+', '.join(sorted(set(closed)-set(cells))))
    return cells,superseded,{key:closed[key] for key in closed}


def build(repo,stage):
    executed,executed_hash=load_manifest(repo/'logs/server-campaign/quality-final-n3-no-gnss/manifest.json')
    future,future_hash=load_manifest(repo/'configs/campaigns/quality-final.json')
    cells=[];members=set();selections=selected_attempts(repo);superseded=set()
    zed_selections=completed_zed_selections(repo);selections.update(zed_selections)
    batch_labels={};batch_selections=completed_batch_selections(repo,zed_selections,batch_labels);selections.update(batch_selections)
    corrected=corrected_selections(repo);selections.update(corrected);batch_labels.update(dict.fromkeys(corrected,CORRECTED_LABEL))
    completion,completion_superseded,dispositions=paper_completion_selections(repo,selections,corrected)
    selections.update(completion);batch_labels.update(dict.fromkeys(completion,PAPER_COMPLETION_LABEL))
    superseded.update(completion_superseded)
    check_nonacting_scope(repo,completion,corrected)
    for cell in expand_cells(future):
        key=cell_key(cell);attempts=[]
        ids=selections.get(key,[1,2,3])
        if key in selections:superseded.update(f'{key}/run{i}' for i in (1,2,3))
        if key in corrected:superseded.update(corrected_superseded(repo,key))
        for repetition,physical_id in enumerate(ids,1):
            relative=f'{key}/run{physical_id}';members.add(relative)
            attempt=saved_attempt(repo,relative,stage)
            attempt['logical_repetition']=repetition
            attempts.append(attempt)
        # A reselected cell is pooled only by the record made for its new attempts.
        pooling=pooled_cohort(repo,key,attempts,(RULEC_POOLING,) if key in completion else POOLING_RECORDS)
        if pooling and pooling['status']=='pooled':
            for attempt in attempts:
                attempt['recorded_cohort_fingerprint']=attempt['cohort_fingerprint']
                attempt['cohort_fingerprint']=pooling['cohort']
        cells.append(dict(**cell,variant='default',key=key,target_repetitions=3,cohort_pooling=pooling,
            comparison_membership=(batch_labels[key] if key in batch_labels else
                'corrected_zed_first_20261002' if key in zed_selections
                else 'corrected_euroc_20261001' if key in selections else None),
            original_campaign_member=cell['algorithm'] in executed['tables'][cell['run_type']],
            attempts=attempts,evaluated=sum(a['evaluated'] for a in attempts),
            outcomes=dict(Counter(a['numerical_status'] for a in attempts if a['evaluated'])),
            within_cell_config_consistent=config_consistent(attempts,pooling),
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
        additional_attempt_selections=([evidence(repo/ZED_SELECTION,repo)] if zed_selections else [])
            +[evidence(repo/name,repo) for name in BATCH_SELECTIONS if batch_selections and (repo/name).is_file()]
            +[evidence(repo/name,repo) for name in (PAPER_COMPLETION_SELECTION,RULEC_POOLING,NONACTING) if completion and (repo/name).is_file()],
        cell_dispositions=dispositions,
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
