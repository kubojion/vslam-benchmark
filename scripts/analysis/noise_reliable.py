#!/usr/bin/env python3
"""Bounded short-to-full IMU parameter development experiment.

No main-worktree writes. Defaults to a dry plan. The first pilot is immutable.
Only the low-level, verified run/evaluation machinery is reused in this worktree.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
from pathlib import Path
import signal
import time

import numpy as np
import optuna
import noise_pilot as engine
from prepare_noise_pilot import KEYS

ROOT = Path(__file__).resolve().parents[2]
ART = Path('/data/imoroz/IMU-NOISE-ISSUE2/noise-reliable-20261009')
PROTOCOL = ROOT/'configs/experiments/noise-reliable-20261009.json'
engine.ART = ART
engine.PROTOCOL = PROTOCOL
DEADLINE = None


class BudgetFinished(Exception):
    pass


def identity(params):
    return tuple(float(params[k]) for k in KEYS)


def label_for(spec, params):
    if identity(params) == identity(spec['rule_c']):
        return 'rule_c'
    if identity(params) == identity(spec['legacy']):
        return 'legacy'
    digest = hashlib.sha256(json.dumps(identity(params)).encode()).hexdigest()[:16]
    return 'noise_'+digest


def combined(records):
    if not records:
        raise ValueError('empty observation cohort')
    residual = [r['result']['loss']-10*int(r['result']['failed']) for r in records]
    failures = sum(int(r['result']['failed']) for r in records)
    return float(10*failures + .5*np.mean(residual) + .5*max(residual))


def record_key(spec, params, sequence, mode, repetition, phase):
    return '__'.join([phase,spec['id'],label_for(spec,params),sequence,mode,f'rep{repetition}'])


def attempt(spec, params, sequence, mode='vio', repetition=1, phase='screen'):
    key = record_key(spec,params,sequence,mode,repetition,phase)
    existing = ART/'attempts'/(key+'.json')
    if not existing.exists():
        maximum = 900 if phase != 'full' else 5400
        if DEADLINE is not None and time.time()+maximum+120 > DEADLINE:
            raise BudgetFinished('Insufficient reserved time for next attempt: '+key)
    result = engine.run_attempt(spec,label_for(spec,params),params,sequence,mode,repetition,phase)
    if 'solver_warnings' not in result:
        text = Path(result['wrapper_log']).read_text(errors='replace')
        result['solver_warnings'] = {'cholesky_failure':text.count('Cholesky failure')}
        engine.write(existing,result)
    return result


def candidate(spec, params, records, **extra):
    return dict(label=label_for(spec,params),params=params,loss=combined(records),
        records=[r['key'] for r in records],**extra)


def unique_candidates(items):
    seen = set()
    for item in items:
        key = identity(item['params'])
        if key not in seen:
            seen.add(key)
            yield item


def choose_full_seeds(spec, screens, n=6):
    # Controls and pilot finalists remain represented even if a short proxy ranks
    # them poorly. Include each independent screening winner, then fill by score.
    controls = [dict(params=spec['rule_c']),dict(params=spec['legacy'])]
    winners = [min(group,key=lambda r:(r['loss'],r['label'])) for group in screens]
    ranked = sorted([r for group in screens for r in group],key=lambda r:(r['loss'],r['label']))
    items = controls+spec['pilot_candidates']+winners+ranked
    out = list(unique_candidates(items))[:n]
    if len(out) != n:
        raise RuntimeError('not enough distinct seed configurations')
    return out


def optimize(spec, protocol, seed, n, startup, seeded, phase, sequences, filename):
    sampler = optuna.samplers.TPESampler(seed=seed,n_startup_trials=startup,multivariate=True)
    study = optuna.create_study(direction='minimize',sampler=sampler)
    for item in seeded:
        study.enqueue_trial(item['params'])
    directory = ART/'studies'/spec['id']/filename
    directory.mkdir(parents=True,exist_ok=True)
    trials = []
    for i in range(n):
        trial = study.ask()
        params = {k:trial.suggest_float(k,*spec['bounds'][k],log=True) for k in KEYS}
        target = directory/f'trial{i:02}.json'
        if target.exists() and json.loads(target.read_text())['params'] != params:
            raise RuntimeError('Optimizer replay mismatch: '+str(target))
        records = [attempt(spec,params,seq,phase=phase) for seq in sequences]
        result = candidate(spec,params,records,trial=i,optimizer_seed=seed,phase=phase)
        study.tell(trial,result['loss'])
        engine.write(target,result)
        trials.append(result)
        engine.event('candidate_scored',study=spec['id'],phase=phase,seed=seed,
                     trial=i,label=result['label'],loss=result['loss'])
    return trials


def screening(spec, protocol):
    groups = []
    for i,seed in enumerate(protocol['screen_seeds']):
        groups.append(optimize(spec,protocol,seed,protocol['screen_candidates_per_seed'],
            protocol['screen_startup_trials'],[dict(params=spec['rule_c']),dict(params=spec['legacy'])],
            'screen',spec['clips'],f'screen_seed{i}'))
    return groups


def full_search(spec, protocol, screens):
    seeds = choose_full_seeds(spec,screens,protocol['full_seed_candidates'])
    engine.write(ART/'studies'/spec['id']/'full-seeds.json',seeds)
    return optimize(spec,protocol,protocol['full_seed'],protocol['full_candidates'],
        protocol['full_seed_candidates'],seeds,'full',spec['full_sequences'],'full_search')


def repeated_selection(spec, protocol, trials):
    ranked = sorted(unique_candidates(trials),key=lambda r:(r['loss'],r['label']))
    controls = [dict(params=spec['rule_c']),dict(params=spec['legacy'])]
    shortlist = list(unique_candidates(ranked[:protocol['finalists']]+controls))
    finalists = []
    for item in shortlist:
        records = [attempt(spec,item['params'],seq,repetition=rep,phase='full')
            for rep in range(1,protocol['repetitions']+1) for seq in spec['full_sequences']]
        finalists.append(candidate(spec,item['params'],records,
            failures=sum(r['result']['failed'] for r in records)))
    finalists.sort(key=lambda r:(r['loss'],r['label']))
    selection = dict(selected_at=engine.now(),winner=finalists[0],repeated_candidates=finalists,
        full_trial_ranking=ranked,independent_test=False,
        note='Selected on repeated full development recordings. LC results never change this selection.')
    target = ART/'studies'/spec['id']/'selection.json'
    if target.exists():
        previous = json.loads(target.read_text())
        if previous['winner']['params'] != selection['winner']['params']:
            raise RuntimeError('Frozen selection changed on replay')
        return previous
    engine.write(target,selection)
    return selection


def lc_checks(spec, selection):
    if not spec['supports_lc']:
        return
    records = []
    for item in unique_candidates([dict(params=spec['rule_c']),selection['winner']]):
        records.append(attempt(spec,item['params'],spec['target_sequence'],mode='vio-lc',phase='full'))
    engine.write(ART/'studies'/spec['id']/'lc-diagnostics.json',dict(
        records=[r['key'] for r in records],selected_before_lc=selection['selected_at'],
        note='N=1 on target sequence; not a final N=3 test or part of VIO selection.'))


def render_report(protocol):
    records = [json.loads(p.read_text()) for p in sorted((ART/'attempts').glob('*.json'))]
    done = [r for r in records if r.get('state')=='finished']
    lines = ['# Repeated full-development IMU-noise search','',
        'All recordings are development data. No independent final-test claim. Main Rule C remains unchanged.','',
        f'Completed attempts: {len(done)}. Measured wrapper time: {sum(r["wall_s"] for r in done)/3600:.2f} h.','',
        '| Study | Phase | Sequence | Mode | Configuration | Repeat | RMSE (m) | Support | Outcome | Solver warnings |',
        '|---|---|---|---|---|---:|---:|---:|---|---:|']
    for r in done:
        q=r['result'];err=q['ate_se3_rmse_m'];val='—' if err is None else f'{err:.3f}'
        lines.append(f'| {r["study"]} | {r["phase"]} | {r["sequence"]} | {r["mode"]} | {r["label"]} | {r["repetition"]} | {val} | {100*q["export_support_fraction"]:.1f}% | '+('failed' if q['failed'] else 'passed')+f' | {r.get("solver_warnings",{}).get("cholesky_failure",0)} |')
    (ART/'report.md').write_text('\n'.join(lines)+'\n')


engine.render_report = render_report


def run(protocol, stage):
    screen_results = {}
    for spec in protocol['studies']:
        if stage=='smoke':
            attempt(spec,spec['rule_c'],spec['clips'][0])
        else:
            screen_results[spec['id']] = screening(spec,protocol)
    if stage in ['smoke','screen']:
        return
    full_results = {spec['id']:full_search(spec,protocol,screen_results[spec['id']]) for spec in protocol['studies']}
    if stage=='full-search':
        return
    selections = {spec['id']:repeated_selection(spec,protocol,full_results[spec['id']]) for spec in protocol['studies']}
    for spec in protocol['studies']:
        lc_checks(spec,selections[spec['id']])


def main():
    global DEADLINE
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--stage',choices=['smoke','screen','full-search','all'],default='all')
    args=parser.parse_args()
    if ROOT.name!='vslam-noise-reliable-20261009' or ROOT==engine.MAIN:
        raise RuntimeError('Wrong worktree')
    protocol=json.loads(PROTOCOL.read_text())
    if not args.execute:
        print(json.dumps(dict(studies=[s['id'] for s in protocol['studies']],
            short_proposals=2*16*5,short_attempts_max=320,full_search_attempts_max=120,
            full_repeat_attempts_max=80,lc_attempts_max=8,max_wall_hours=protocol['max_wall_hours'],
            note='Exact duplicate configurations reuse the same measured observation, including shared short controls.'),indent=2))
        return
    def interrupt(signum,frame):
        raise KeyboardInterrupt(f'signal {signum}')
    signal.signal(signal.SIGTERM,interrupt)
    ART.mkdir(exist_ok=True)
    with (ART/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        frozen=ART/'protocol.json'
        if frozen.exists() and frozen.read_bytes()!=PROTOCOL.read_bytes():
            raise RuntimeError('Protocol changed after start')
        if not frozen.exists():
            frozen.write_bytes(PROTOCOL.read_bytes())
        budget=ART/'budget.json'
        if not budget.exists():
            start=time.time()
            engine.write(budget,dict(started_unix=start,deadline_unix=start+3600*protocol['max_wall_hours']))
        DEADLINE=json.loads(budget.read_text())['deadline_unix']
        engine.verify_main()
        engine.event('controller_started',stage=args.stage,protocol_sha256=engine.sha(PROTOCOL),deadline_unix=DEADLINE)
        try:
            run(protocol,args.stage)
            engine.verify_main()
            render_report(protocol)
            engine.event('stage_finished',stage=args.stage)
        except BudgetFinished as exc:
            render_report(protocol)
            engine.event('budget_finished',reason=str(exc),complete=False)
        except BaseException as exc:
            render_report(protocol)
            engine.event('controller_stopped',reason=f'{type(exc).__name__}: {exc}')
            raise


if __name__=='__main__':
    main()
