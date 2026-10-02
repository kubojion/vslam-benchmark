#!/usr/bin/env python3
"""Execute the frozen 60-second ZED integration checks once; never a full campaign."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/eval'))
from _saved_run import atomic_json


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    out=ROOT/'results/zed-preparation-20261002';plan_path=out/'short-check-plan.json'
    plan=json.loads(plan_path.read_text());seq=plan['diagnostic_sequence']
    if seq!='field1_diag60_20261002' or plan['camera_frames']!=600:
        raise ValueError('only the fixed diagnostic window is authorized by this controller')
    if plan['last_camera_ns']-plan['first_camera_ns']>60_000_000_000:
        raise ValueError('diagnostic window too long')
    for a in plan['actions']:
        if a['command'][2:]!=['zed2i',seq,'1',a['mode']] or a['timeout_s']>420:
            raise ValueError('unexpected command or time budget')
        expected=ROOT/f'results/{a["mode"]}/zed2i/{seq}/{a["algorithm"]}/run1'
        if ROOT/a['result_directory']!=expected or expected.exists():
            raise ValueError('attempt path consumed or inconsistent: '+str(expected))
    state_path=out/'short-check-state.json'
    if state_path.exists():raise FileExistsError('checks already started; preserve prior state and attempts')
    if not args.execute:
        print(f'Validated {len(plan["actions"])} separate 60-second checks; use --execute to run once.');return
    state=dict(schema=1,scope='integration_diagnostics_only',plan_sha256=hashlib.sha256(plan_path.read_bytes()).hexdigest(),
               started_at=datetime.now(timezone.utc).isoformat(),actions=[])
    atomic_json(state_path,state)
    for index,a in enumerate(plan['actions']):
        log=out/f'short-check-{index:02}-{a["algorithm"]}-{a["mode"]}.log'
        row=dict(index=index,algorithm=a['algorithm'],mode=a['mode'],result_directory=a['result_directory'],
                 status='running',started_at=datetime.now(timezone.utc).isoformat(),log=str(log.relative_to(ROOT)))
        state['actions'].append(row);atomic_json(state_path,state)
        start=time.monotonic()
        with log.open('xb') as stream:
            proc=subprocess.Popen(a['command'],cwd=ROOT,env=os.environ|a['env'],stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
            row['wrapper_pid']=proc.pid;atomic_json(state_path,state)
            try:
                code=proc.wait(timeout=a['timeout_s']);row.update(status='exited',wrapper_exit_code=code)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGTERM)
                try:code=proc.wait(timeout=40)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid,signal.SIGKILL);code=proc.wait()
                row.update(status='diagnostic_timeout',wrapper_exit_code=code)
            except BaseException:
                os.killpg(proc.pid,signal.SIGTERM);proc.wait(timeout=40)
                row.update(status='interrupted',wrapper_exit_code=proc.returncode)
                atomic_json(state_path,state);raise
        row.update(elapsed_s=time.monotonic()-start,finished_at=datetime.now(timezone.utc).isoformat())
        # Immediate saved-output evaluation is a separate diagnostic, never N=3 evidence.
        trajectory=ROOT/a['result_directory']/'trajectory.txt'
        if trajectory.is_file():
            target=out/f'diagnostic-evaluations/{a["mode"]}-{a["algorithm"]}.json';target.parent.mkdir(exist_ok=True)
            command=[sys.executable,str(ROOT/'scripts/eval/_evaluate_run.py'),'zed2i',seq,a['algorithm'],'1',a['mode'],'--output',str(target)]
            with (out/f'short-check-{index:02}-evaluation.log').open('xb') as stream:
                result=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,timeout=90)
            row.update(evaluation_exit_code=result.returncode,evaluation=str(target.relative_to(ROOT)))
        else:row['evaluation']='no_saved_trajectory'
        atomic_json(state_path,state)
        print(index,a['algorithm'],a['mode'],row['status'],row['wrapper_exit_code'],flush=True)
    state['finished_at']=datetime.now(timezone.utc).isoformat();atomic_json(state_path,state)


if __name__=='__main__':main()
