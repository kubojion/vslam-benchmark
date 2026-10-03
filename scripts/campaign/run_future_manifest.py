#!/usr/bin/env python3
"""Validate a future per-repetition manifest; execution requires --run explicitly.

An executable manifest can contain blocked cases. Validation does not certify
execution readiness, and blocked actions are never silently attempted.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_repetitions import atomic_json, lock, now, run_command
from prepare_cell import component

REPO=Path(__file__).resolve().parents[2]
MODES={'vo','vo-lc','vio','vio-lc','gnss-vio'}
EXCLUDED={'droidslam','mast3r_slam','megasam'}
CATEGORIES={'reusable','required_rerun','missing','blocked','cohort_completion'}
UNREVIEWED_OVERRIDES=(
    'BASALT_CONFIG','BASALT_CALIBRATION','ROSARIO_VIO_PROFILE','ORBSLAM3_CONFIG','ORBSLAM3_GDB','ORBSLAM3_LIBRARY_TRACE','VOXEL_SVIO_BACKTRACE','OKVIS2_CONFIG','OKVIS2X_CONFIG',
    'OKVIS_INTERACTIVE','OV2SLAM_CONFIG','OV2SLAM_PLAYBACK_RATE','OV2SLAM_FINISH_TIMEOUT',
    'OPENVINS_RATE','DPVO_STRIDE','DPVO_SKIP','DPVO_SEED','GNSS_CSV','GNSS_VARIANT',
    'GPS_COV_XY','GPS_COV_Z','GPS_STATUS','GT_OVERRIDE','AIRSLAM_STAGE_TIMEOUT_S',
    'AIRSLAM_STARTUP_TIMEOUT_S','AIRSLAM_REFINEMENT_MAX_ATTEMPTS','OWNED_STOP_GRACE',
    'CUVSLAM_CONFIG','CUVSLAM_CONDA_ENV','CUVSLAM_CUDA_LIB','DSOL_CONFIG','DSOL_IMAGE',
    'DSOL_PREP_CONDA_ENV','SVO_PRO_CONFIG','SVO_PRO_IMAGE','SVO_PRO_TIME_LIMIT_S',
    'SVO_PRO_PREP_CONDA_ENV','MAST3R_FUSION_CONFIG','MAST3R_FUSION_CONDA_ENV',
    'MAST3R_FUSION_SEED','MAST3R_FUSION_GPU','MAST3R_FUSION_KEEP_H5','MPLBACKEND',
    'CUDA_VISIBLE_DEVICES','NVIDIA_VISIBLE_DEVICES','OMP_NUM_THREADS','MKL_NUM_THREADS',
    'OPENBLAS_NUM_THREADS','CUBLAS_WORKSPACE_CONFIG','NVIDIA_TF32_OVERRIDE',
    'LD_LIBRARY_PATH','LD_PRELOAD','PYTHONPATH','ROS_PACKAGE_PATH','AMENT_PREFIX_PATH',
    'CMAKE_PREFIX_PATH','COLCON_PREFIX_PATH','VSLAM_EXPECTED_INPUT_SHA256',
    'VSLAM_EXPECTED_RUNTIME_SHA256',
    'VSLAM_EXPECTED_SOURCE_SHA256',
)


def check_execution_environment(environment=None):
    environment=os.environ if environment is None else environment
    overrides=[key for key in UNREVIEWED_OVERRIDES if environment.get(key)]
    if overrides:
        raise ValueError('unreviewed inherited execution overrides: '+', '.join(overrides))


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(2**20),b''):h.update(chunk)
    return h.hexdigest()


def verify_files(repo,items):
    errors=[]
    for item in items:
        path=Path(item['path'])
        if path.is_absolute() or '..' in path.parts:
            errors.append('unsafe evidence path: '+str(path));continue
        actual=repo/path
        if not actual.is_file() or digest(actual)!=item['sha256']:
            errors.append('stale or absent evidence: '+str(path))
    return errors


def validate(repo,manifest,*,check_files=True):
    errors=[];seen=set();outputs=set();by_cell={}
    if manifest.get('schema_version')!=2:errors.append('expected manifest schema_version 2')
    if manifest.get('target',{}).get('repetitions')!=3:errors.append('future target must be N=3')
    for action in manifest.get('actions',[]):
        name=action.get('id')
        if name in seen:errors.append('duplicate action: '+str(name))
        seen.add(name)
        parts=action.get('cell','').split('/')
        if len(parts)!=4:
            errors.append('invalid cell path');continue
        mode,ds,seq,algo=parts
        try:
            for part in parts:component(part)
            component(action['cohort'])
        except (ValueError,argparse.ArgumentTypeError,KeyError):
            errors.append('unsafe cell or cohort');continue
        if mode not in MODES or algo in EXCLUDED:errors.append('unsupported mode or excluded algorithm')
        rep=action.get('repetition')
        if rep not in (1,2,3):errors.append('invalid logical repetition')
        by_cell.setdefault(action['cell'],[]).append(rep)
        category=action.get('category')
        if category not in CATEGORIES:errors.append('unknown action category')
        recipe=action.get('configuration_recipe')
        if manifest.get('input_identity_schema')==1 and not action.get('prepared_inputs'):
            errors.append('action is missing prepared input identity')
        if manifest.get('runtime_identity_schema')==1 and not action.get('runtime_assets'):
            errors.append('action is missing runtime asset identity')
        if manifest.get('implementation_capture_schema')==1 and not action.get('implementation_capture'):
            errors.append('action is missing source implementation capture')
        if manifest.get('configuration_recipe_schema')==1 and not recipe:
            errors.append('action is missing its configuration recipe')
        if recipe:
            claimed=recipe.get('sha256')
            payload={k:v for k,v in recipe.items() if k!='sha256'}
            actual=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            if claimed!=actual:errors.append('configuration recipe digest mismatch')
            if action.get('readiness',{}).get('verified_ready_to_run') and recipe.get('selection_errors'):
                errors.append('ready action has unresolved configuration selection errors')
        if category=='reusable' and (action.get('prerequisites') or not action.get('review_evidence')):
            errors.append('reusable action lacks completed qualification evidence')
        if category in ('missing','required_rerun','cohort_completion'):
            path=Path(action.get('planned_output') or '')
            base=Path('results')/action['cell']
            if path.parent!=base or not path.name.startswith('run') or not path.name[3:].isdigit():
                errors.append('invalid new attempt path');continue
            if str(path) in outputs:errors.append('duplicate new attempt path')
            outputs.add(str(path))
            expected=['python3','scripts/campaign/run_repetitions.py',ds,seq,algo,'3',mode,'--run-id',path.name[3:],
                      '--repetition',str(rep),'--cohort',action['cohort']]
            if action.get('command')!=expected:errors.append('command disagrees with action identity')
            ready=action.get('readiness',{})
            if ready.get('verified_ready_to_run') and (action.get('prerequisites') or
                ready.get('static_checks')!='verified' or ready.get('execution_validation')!='verified' or not action.get('review_evidence')):
                errors.append('execution readiness claim lacks prerequisite evidence')
    for key,reps in by_cell.items():
        if sorted(reps)!=[1,2,3]:errors.append('cell lacks exactly three logical repetitions: '+key)
    if len(seen)!=manifest.get('target',{}).get('logical_repetitions'):errors.append('logical repetition total mismatch')
    if len(by_cell)!=manifest.get('target',{}).get('default_cells'):errors.append('cell total mismatch')
    if check_files:
        items=[manifest['inventory']]+manifest.get('pipeline_files',[])
        items+=manifest.get('completed_attempt_selection_evidence',[])
        items+=(manifest.get('qualification_review') or {}).get('evidence',[])
        for action in manifest.get('actions',[]):
            items+=action.get('prior_evidence',[])+action.get('review_evidence',[])
            items+=action.get('configuration_recipe',{}).get('source_files',[])
            if action.get('prepared_inputs'):items.append(action['prepared_inputs'])
            if action.get('runtime_assets'):items.append(action['runtime_assets'])
            if action.get('implementation_capture'):items.append(action['implementation_capture'])
        by_path={}
        for item in items:
            if item['path'] in by_path and by_path[item['path']]['sha256']!=item['sha256']:
                errors.append('conflicting evidence hashes: '+item['path'])
            by_path[item['path']]=item
        errors+=verify_files(repo,list(by_path.values()))
        inventory_path=repo/manifest['inventory']['path']
        if inventory_path.is_file():
            inventory=json.loads(inventory_path.read_text())
            if set(by_cell)!={c['key'] for c in inventory['cells']}:
                errors.append('manifest cells disagree with the authoritative inventory')
    return errors


def execute(repo,manifest,manifest_hash,actions,*,executor=run_command):
    # Check every selected action before starting any estimator.
    check_execution_environment()
    for action in actions:
        if action['category']=='blocked' or action['prerequisites']:
            raise ValueError('selected action is blocked: '+action['id'])
        if action['category']!='reusable' and not action['readiness']['verified_ready_to_run']:
            raise ValueError('selected action is not verified ready to run: '+action['id'])
        errors=verify_files(repo,action['prior_evidence']+action.get('review_evidence',[])+
                            action.get('configuration_recipe',{}).get('source_files',[]))
        if errors:raise ValueError('; '.join(errors))
    verify_prepared_inputs(repo,actions)
    verify_implementations(repo,actions)
    root=repo/'logs/server-campaign'/component(manifest['campaign_id'])
    with lock(root/'manifest.lock'):
        path=root/'state.json'
        state=json.loads(path.read_text()) if path.exists() else dict(manifest_sha256=manifest_hash,actions={})
        if state['manifest_sha256']!=manifest_hash:
            raise ValueError('manifest changed since execution began; preserve state and use an explicit new campaign revision')
        for action in actions:
            key=action['id'];previous=state['actions'].get(key,{})
            if action['category']=='reusable':
                state['actions'][key]=dict(status='retained',at=now(),outcome=action['observed_outcome'])
            else:
                record=dict(status='running',at=now(),command=action['command'],
                            history=previous.get('history',[])+([previous] if previous else []))
                # Avoid recursively duplicating the history on repeated resumes.
                if previous:record['history'][-1]={k:v for k,v in previous.items() if k!='history'}
                state['actions'][key]=record;atomic_json(path,state)
                # Each runner compares its own pre-estimation capture to this
                # reviewed identity, closing the gap between preflight and start.
                expected=action.get('prepared_inputs',{}).get('content_sha256')
                if expected:os.environ['VSLAM_EXPECTED_INPUT_SHA256']=expected
                runtime_expected=action.get('runtime_assets',{}).get('content_sha256')
                if runtime_expected:os.environ['VSLAM_EXPECTED_RUNTIME_SHA256']=runtime_expected
                source_expected=action.get('implementation_capture',{}).get('content_sha256')
                if source_expected:os.environ['VSLAM_EXPECTED_SOURCE_SHA256']=source_expected
                try:result=executor(action['command'],check=False)
                finally:
                    os.environ.pop('VSLAM_EXPECTED_INPUT_SHA256',None)
                    os.environ.pop('VSLAM_EXPECTED_RUNTIME_SHA256',None)
                    os.environ.pop('VSLAM_EXPECTED_SOURCE_SHA256',None)
                record.update(status='evaluated' if result.returncode==0 else 'failure_or_review',exit_code=result.returncode,finished_at=now())
            atomic_json(path,state)
    return state


def verify_prepared_inputs(repo,actions):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'run'))
    from _capture_inputs import verify_identity
    seen=set()
    for action in actions:
        item=action.get('prepared_inputs')
        if not item or item['path'] in seen:continue
        errors=verify_files(repo,[item])
        if errors:raise ValueError('; '.join(errors))
        value=json.loads((repo/item['path']).read_text())
        if value['sha256']!=item['content_sha256']:raise ValueError('prepared input identity disagrees with action')
        verify_identity(repo,value,check_live=True);seen.add(item['path'])


def verify_implementations(repo,actions):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'run'))
    from _capture_runtime import verify_identity
    from _capture_implementation import verify_capture
    seen=set()
    for action in actions:
        for field in ('runtime_assets','implementation_capture'):
            item=action.get(field)
            if not item or item['path'] in seen:continue
            errors=verify_files(repo,[item])
            if errors:raise ValueError('; '.join(errors))
            path=repo/item['path']
            if field=='runtime_assets':
                value=json.loads(path.read_text())
                if value['sha256']!=item['content_sha256']:raise ValueError('runtime identity disagrees with action')
                verify_identity(repo,value,check_live=True)
            else:
                value=json.loads(path.read_text())
                actual=hashlib.sha256(json.dumps(value['trees'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
                if actual!=item['content_sha256']:raise ValueError('source identity disagrees with action')
                verify_capture(repo,path,check_live=True)
            seen.add(item['path'])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('manifest',type=Path)
    ap.add_argument('--action',action='append',help='select exact action ID (repeatable); default all')
    ap.add_argument('--run',action='store_true',help='execute selected verified-ready actions; default only validates')
    ap.add_argument('--require-ready',action='store_true',help='fail preflight if any selected action is blocked/unverified')
    ap.add_argument('--check-inputs',action='store_true',help='also verify current prepared sensor bytes (read-only; cached by file identity)')
    ap.add_argument('--check-implementations',action='store_true',help='also verify source archives/current trees and known native/model/container assets; no estimator execution')
    args=ap.parse_args();raw=args.manifest.read_bytes();manifest=json.loads(raw)
    errors=validate(REPO,manifest)
    selected=[a for a in manifest.get('actions',[]) if not args.action or a['id'] in args.action]
    if args.action and set(args.action)-{a['id'] for a in selected}:errors.append('unknown selected action')
    unready=[a for a in selected if a['prerequisites'] or a['category']=='blocked' or
             (a['category']!='reusable' and not a['readiness']['verified_ready_to_run'])]
    if args.require_ready and unready:errors.append(f'{len(unready)} selected actions are not verified ready')
    if args.require_ready or args.run:
        try:check_execution_environment()
        except ValueError as exc:errors.append(str(exc))
    if args.check_inputs:
        try:verify_prepared_inputs(REPO,selected)
        except (OSError,ValueError,KeyError) as exc:errors.append(str(exc))
    if args.check_implementations:
        try:verify_implementations(REPO,selected)
        except (OSError,ValueError,KeyError,subprocess.SubprocessError) as exc:errors.append(str(exc))
    if errors:
        for error in errors:print('[manifest] '+error,file=sys.stderr)
        return 2
    print(json.dumps(dict(manifest_valid=True,selected=len(selected),categories=dict(Counter(a['category'] for a in selected)),
                         unready=len(unready),audit_status=manifest['audit_status'],estimation_started=False),indent=2))
    if args.run:
        try:
            state=execute(REPO,manifest,hashlib.sha256(raw).hexdigest(),selected)
            return 0 if all(state['actions'][a['id']]['status'] in ('retained','evaluated') for a in selected) else 1
        except (ValueError,RuntimeError,OSError) as exc:
            print('[manifest] '+str(exc),file=sys.stderr);return 2
    return 0


if __name__=='__main__':raise SystemExit(main())
