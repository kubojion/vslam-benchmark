#!/usr/bin/env python3
"""Isolated, resumable short-clip noise search; never writes the main worktree.

Run with .venv/bin/python. Defaults to a dry plan; --execute starts trials.
Create STOP_AFTER_CURRENT in the artifact directory to stop between attempts.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

import numpy as np
import optuna

from prepare_noise_pilot import KEYS, ORB_KEYS, values

ROOT = Path(__file__).resolve().parents[2]
MAIN = Path('/data/imoroz/vslam-benchmark')
ART = Path('/data/imoroz/IMU-NOISE-ISSUE2/noise-search-20261009')
PROTOCOL = ROOT/'configs/experiments/noise-search-20261009.json'
sys.path.insert(0, str(ROOT/'scripts/eval'))
from _saved_run import evaluate_saved_run
from _reference_source import selected_reference
from _metrics import interpolate_reference, reference_interval_ids


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
    tmp.replace(path)


def event(kind, **data):
    record = dict(time=now(), event=kind, **data)
    with (ART/'events.jsonl').open('a') as f:
        f.write(json.dumps(record, allow_nan=False)+'\n')
    print(json.dumps(record, allow_nan=False), flush=True)
    write(ART/'status.json', record)


def verify_main():
    before = json.loads((ART/'main-before.json').read_text())
    changed = [p for p, h in before['sha256'].items() if not (MAIN/p).is_file() or sha(MAIN/p) != h]
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=MAIN, text=True).strip()
    report = dict(checked=now(), files=len(before['sha256']), changed=changed,
                  main_head_unchanged=head == before['main_head'])
    write(ART/'main-integrity.json', report)
    if changed or not report['main_head_unchanged']:
        raise RuntimeError('main changed during experiment; pause to review provenance: '+str(changed))


def production_processes():
    found = []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name) == os.getpid():
            continue
        try:
            args = (proc/'cmdline').read_bytes().decode(errors='replace').split('\0')
            cwd = (proc/'cwd').resolve()
        except (OSError, RuntimeError):
            continue
        for arg in args:
            path = Path(arg) if arg else Path('.')
            if not path.is_absolute():
                path = cwd/path
            if str(path).startswith(str(MAIN/'scripts/run/run_')) and str(path).endswith('.sh'):
                found.append(int(proc.name)); break
            if str(path).startswith(str(MAIN/'src/')) and path.name in ('okvis_app_synchronous', 'stereo_inertial_euroc', 'stereo_euroc'):
                found.append(int(proc.name)); break
    return found


@contextmanager
def machine_slot():
    # Open the existing production lock read-only: no creation, truncation or
    # content change. Share its scheduling exclusion with the normal campaign.
    with (MAIN/'results/.locks/execution.lock').open('rb') as f:
        while True:
            if (ART/'STOP_AFTER_CURRENT').exists():
                raise InterruptedError('STOP_AFTER_CURRENT requested')
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                event('waiting_for_production_lock'); time.sleep(15); continue
            active = production_processes()
            if not active:
                break
            fcntl.flock(f, fcntl.LOCK_UN)
            event('waiting_for_production_process', pids=active); time.sleep(15)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def candidate_config(spec, label, params):
    path = ROOT/'configs/experiments/generated'/spec['id']/(label+'.yaml')
    text = (ROOT/spec['config']).read_text()
    actual_keys = ORB_KEYS if spec['algorithm'] == 'orbslam3' else KEYS
    for key, actual in zip(KEYS, actual_keys):
        pattern = r'^(\s*'+re.escape(actual)+r':\s*)([-+0-9.eE]+)'
        text, count = re.subn(pattern, lambda m: m[1]+format(params[key], '.17g'), text, flags=re.M)
        if count != 1:
            raise ValueError('noise override was not unique: '+actual)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text() != text:
            raise RuntimeError('refusing to overwrite a candidate configuration')
    else:
        path.write_text(text)
    if values(path, spec['algorithm']) != params:
        raise RuntimeError('candidate noise round-trip mismatch')
    return path


def reference_distance(dataset, sequence):
    directory = ROOT/'datasets'/dataset/sequence
    selected = selected_reference(ROOT, dataset, sequence)
    gt = np.loadtxt(selected['path'] if selected else directory/'gt_tum.txt', ndmin=2)
    times = np.loadtxt(directory/'times.txt', ndmin=1)/1e9
    intervals = selected['valid_intervals'] if selected else None
    grid, support = interpolate_reference(gt, times, valid_intervals=intervals)
    idx = np.flatnonzero(support)
    usable = np.diff(idx) == 1
    if intervals is not None:
        usable &= np.diff(reference_interval_ids(grid[:, 0], intervals)) == 0
    distance = float(np.linalg.norm(np.diff(grid[:, 1:4], axis=0), axis=1)[usable].sum())
    if not math.isfinite(distance) or distance < 1:
        raise RuntimeError('development clip has insufficient reference motion')
    return distance


def verify_native_parameters(run, spec, params, cfg, returncode):
    """Check native diagnostics where exposed, plus AirSLAM's launched path."""
    algorithm = spec['algorithm']
    if algorithm == 'voxel_svio':
        path = run/'native/parameter_list.txt'
        names = ['sigma_w', 'sigma_a', 'sigma_wb', 'sigma_ab']
        text = path.read_text() if path.exists() else ''
        patterns = [r'^'+n+r':\s*([-+0-9.eE]+)' for n in names]
    elif algorithm == 'orbslam3':
        path = run/'run_log.txt'
        text = path.read_text() if path.exists() else ''
        names = ['Gyro noise', 'Accelerometer noise', 'Gyro walk', 'Accelerometer walk']
        patterns = [re.escape(n)+r':\s*([-+0-9.eE]+)' for n in names]
    else:
        path = run/'processes/odometry.json'
        if path.exists():
            command = json.loads(path.read_text())['command']
            expected = '/benchmark_configs/'+str(cfg.relative_to(ROOT/'configs'))
            if expected not in '\n'.join(command):
                raise RuntimeError('AirSLAM did not launch with the candidate camera config')
        elif returncode == 0:
            raise RuntimeError('AirSLAM native command evidence missing')
        return
    for key, pattern in zip(KEYS, patterns):
        found = re.findall(pattern, text, re.M)
        if not found and returncode == 0:
            raise RuntimeError('native noise diagnostic missing: '+key)
        if found and not math.isclose(float(found[0]), params[key], rel_tol=2e-6):
            raise RuntimeError('native noise disagrees with candidate: '+key)


def score(evaluation, returncode, algo, path_m):
    coverage = evaluation.get('coverage', {})
    span = float(coverage.get('export_span_pct') or 0)/100
    gap = coverage.get('coverage_gap_pct')
    support = span if algo == 'airslam' else min(span, float(gap or 0)/100)
    support = max(0., min(1., support))
    rmse = evaluation.get('ate_se3', {}).get('rmse')
    valid_error = rmse is not None and math.isfinite(rmse) and rmse >= 0
    failed = returncode != 0 or evaluation.get('run_status') != 'ok' or support < .90 or not valid_error
    bounded_error = rmse/(path_m+rmse) if valid_error else 1.
    return dict(failed=bool(failed), loss=10*int(failed)+bounded_error+(1-support),
                ate_se3_rmse_m=rmse if valid_error else None, reference_path_m=path_m,
                export_support_fraction=support, export_span_fraction=span,
                camera_pose_coverage_pct=coverage.get('camera_pose_coverage_pct'),
                scale_factor=evaluation.get('scale_factor'), numerical_status=evaluation.get('run_status'),
                sparse_export=algo == 'airslam', qualification=evaluation.get('qualification'))


def stop_owned_attempt(proc, run):
    # Signal only the process group we created; wrapper traps clean up its own
    # Docker processes. Never use name-based kill or touch production containers.
    if proc.poll() is None:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=45)
        except subprocess.TimeoutExpired:
            for state in (run/'processes').glob('*.json'):
                container = {'airslam': 'noise_search_airslam_20261009',
                             'voxel_svio': 'noise_search_voxel_20261009'}.get(run.parent.name)
                args = [sys.executable, str(ROOT/'scripts/run/_owned_process.py'), '--state', str(state)]
                if container:
                    args += ['--container', container, '--container-state', '/results/'+str(state.relative_to(ROOT/'results'))]
                subprocess.run(args+['stop'], timeout=30, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=15)


def run_attempt(spec, label, params, sequence, mode, repetition, phase):
    key = f'{phase}__{spec["id"]}__{label}__{sequence}__{mode}__rep{repetition}'
    record_path = ART/'attempts'/(key+'.json')
    if record_path.exists():
        old = json.loads(record_path.read_text())
        if old.get('state') == 'finished':
            return old
        raise RuntimeError('incomplete attempt needs explicit recovery; refusing silent retry: '+key)
    if (ART/'STOP_AFTER_CURRENT').exists():
        raise InterruptedError('STOP_AFTER_CURRENT requested')
    cfg = candidate_config(spec, label, params)
    # Derived solely from identity, independent of scheduling; fresh directory
    # refusal protects against accidental collisions.
    run_id = 1_000_000_000 + int(hashlib.sha256(key.encode()).hexdigest()[:10], 16)
    run = ROOT/'results'/mode/spec['dataset']/sequence/spec['algorithm']/f'run{run_id}'
    if run.exists():
        raise RuntimeError('existing physical attempt has no completed pilot record: '+str(run))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', NOISE_PILOT_CONFIG=str(cfg),
               ORBSLAM3_CONFIG=str(cfg), AIRSLAM_STAGE_TIMEOUT_S='3600',
               BENCHMARK_EVAL_PYTHON=sys.executable)
    env['LD_LIBRARY_PATH'] = str(ROOT/'src/ORB_SLAM3/Thirdparty/DBoW2/lib')+':'+env.get('LD_LIBRARY_PATH', '')
    for name in ('ROSARIO_VIO_PROFILE', 'VSLAM_EXPECTED_INPUT_SHA256', 'VSLAM_EXPECTED_SOURCE_SHA256', 'VSLAM_EXPECTED_RUNTIME_SHA256'):
        env.pop(name, None)
    cmd = ['bash', str(ROOT/f'scripts/run/run_{spec["algorithm"]}.sh'), spec['dataset'], sequence, str(run_id), mode]
    path_m = reference_distance(spec['dataset'], sequence)
    with machine_slot():
        verify_main()
        record = dict(key=key, state='running', started=now(), study=spec['id'], phase=phase,
            label=label, params=params, sequence=sequence, mode=mode, repetition=repetition,
            run=str(run), config=str(cfg), config_sha256=sha(cfg), command=cmd)
        write(record_path, record)
        event('attempt_started', key=key, run=str(run))
        log = ART/'wrapper-logs'/(key+'.log')
        log.parent.mkdir(exist_ok=True)
        started = time.monotonic()
        with log.open('xb') as stream:
            proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                # Bound whole-attempt overhead too. Three-minute clips receive
                # 15 minutes; full targets 90 minutes. Timeouts remain failures.
                rc = proc.wait(timeout=900 if phase != 'full' else 5400)
                timed_out = False
            except subprocess.TimeoutExpired:
                stop_owned_attempt(proc, run); rc = 124; timed_out = True
            except BaseException:
                stop_owned_attempt(proc, run)
                raise
        elapsed = time.monotonic()-started
        evaluation = {}
        evaluation_error = None
        if (run/'trajectory.txt').is_file():
            try:
                evaluation, _ = evaluate_saved_run(ROOT, run)
                evaluation['qualification'] = dict(status='exploratory_development_only',
                    blockers=evaluation.get('qualification', {}).get('blockers', [])+['noise_selected_on_development_ground_truth', 'not_independent_final_test'])
                write(run/'run_eval.json', evaluation)
            except Exception as exc:
                evaluation_error = f'{type(exc).__name__}: {exc}'
        if (run/'run_meta.json').is_file():
            meta = json.loads((run/'run_meta.json').read_text())
            artifacts = meta.get('provenance', {}).get('artifacts', [])
            actual = next((a for a in artifacts if a.get('role') == ('camera_config' if spec['algorithm'] == 'airslam' else 'estimator_config')), None)
            if actual is None or values(run/actual['snapshot'], spec['algorithm']) != params:
                raise RuntimeError('saved effective noise does not match candidate: '+key)
        elif not timed_out:
            # A wrapper/setup error is not an estimator result. Halt and inspect
            # before wasting the remaining budget or misleading the optimiser.
            raise RuntimeError('no run_meta.json; inspect infrastructure failure: '+str(log))
        if evaluation_error:
            raise RuntimeError('evaluator infrastructure failure: '+evaluation_error)
        verify_native_parameters(run, spec, params, cfg, rc)
        record.update(state='finished', finished=now(), returncode=rc, timeout=timed_out,
            wall_s=elapsed, result=score(evaluation, rc, spec['algorithm'], path_m), wrapper_log=str(log))
        write(record_path, record)
        event('attempt_finished', key=key, returncode=rc, wall_s=round(elapsed, 2), result=record['result'])
        verify_main()
        render_report(json.loads(PROTOCOL.read_text()))
        return record


def combined(records):
    # Preserve failure-count priority also for the six finalist observations.
    failures = sum(int(r['result']['failed']) for r in records)
    residual = np.mean([r['result']['loss']-10*int(r['result']['failed']) for r in records])
    return float(10*failures+residual)


def run_study(spec, protocol, stage):
    directory = ART/'studies'/spec['id']
    directory.mkdir(parents=True, exist_ok=True)
    sampler = optuna.samplers.TPESampler(seed=protocol['seed'], n_startup_trials=8, multivariate=True)
    study = optuna.create_study(direction='minimize', sampler=sampler)
    study.enqueue_trial(spec['rule_c']); study.enqueue_trial(spec['legacy'])
    trials = []
    for i in range(protocol['candidates_per_study']):
        trial = study.ask()
        params = {k: trial.suggest_float(k, *spec['bounds'][k], log=True) for k in KEYS}
        label = ('rule_c' if i == 0 else 'legacy' if i == 1 else f'candidate{i:02}')
        saved = directory/f'{label}.json'
        if saved.exists():
            old = json.loads(saved.read_text())
            if old['params'] != params:
                raise RuntimeError('deterministic optimiser replay mismatch')
        runs = [run_attempt(spec, label, params, clip, 'vio', 1, 'screen') for clip in spec['clips']]
        loss = combined(runs)
        study.tell(trial, loss)
        result = dict(label=label, params=params, loss=loss, records=[r['key'] for r in runs])
        write(saved, result); trials.append(result)
        event('candidate_scored', study=spec['id'], label=label, loss=loss)
    top = sorted(trials, key=lambda x: (x['loss'], x['label']))[:2]
    for candidate in top:
        repeat_runs = [json.loads((ART/'attempts'/(key+'.json')).read_text()) for key in candidate['records']]
        for repetition in (2, 3):
            for clip in spec['clips']:
                repeat_runs.append(run_attempt(spec, candidate['label'], candidate['params'], clip, 'vio', repetition, 'repeat'))
        candidate['repeated_loss'] = combined(repeat_runs)
    top.sort(key=lambda x: (x['repeated_loss'], x['label']))
    selection = dict(selected_before_full=now(), winner=top[0], top_two=top, all_short_candidates=trials,
                     independent_final_test=False)
    selection_path = directory/'short-selection.json'
    if selection_path.exists():
        previous = json.loads(selection_path.read_text())
        if previous['winner']['label'] != selection['winner']['label']:
            raise RuntimeError('short winner changed on replay')
        selection = previous
    else:
        write(selection_path, selection)
    if stage == 'short':
        return selection
    promoted = {x['label']: x for x in [trials[0], trials[1]]+selection['top_two']}
    full = []
    for label, candidate in promoted.items():
        full.append(run_attempt(spec, label, candidate['params'], spec['target_sequence'], 'vio', 1, 'full'))
    if spec['supports_lc']:
        lc = {x['label']: x for x in [trials[0], selection['winner']]}
        for label, candidate in lc.items():
            full.append(run_attempt(spec, label, candidate['params'], spec['target_sequence'], 'vio-lc', 1, 'full'))
    write(directory/'full-validation.json', dict(selection=selection, full_records=[r['key'] for r in full],
        note='No full result is fed back into the short search; report ranking reversals and failures.'))
    return selection


def render_report(protocol):
    records = [json.loads(p.read_text()) for p in sorted((ART/'attempts').glob('*.json'))]
    done = [r for r in records if r.get('state') == 'finished']
    lines = ['# Noise-search pilot — 9 October 2026', '',
        'Exploratory tuning in a separate worktree. Rule C production is unchanged.', '',
        f'Completed attempts: {len(done)}. Measured wrapper time: {sum(r["wall_s"] for r in done)/3600:.2f} h.', '',
        'The full targets overlap the short development prefixes. These are fidelity checks, not independent test results.', '',
        '| Study | Phase | Sequence | Mode | Candidate | Repeat | SE3 RMSE (m) | Export support | Outcome |',
        '|---|---|---|---|---|---|---:|---:|---|']
    for r in done:
        v = r['result']; rmse = v['ate_se3_rmse_m']
        lines.append(f'| {r["study"]} | {r["phase"]} | {r["sequence"]} | {r["mode"]} | {r["label"]} | {r["repetition"]} | '
                     + ('—' if rmse is None else f'{rmse:.3f}')+f' | {100*v["export_support_fraction"]:.1f}% | '+('failed gate' if v['failed'] else 'passed gate')+' |')
    (ART/'report.md').write_text('\n'.join(lines)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--stage', choices=('smoke', 'short', 'all'), default='all')
    args = parser.parse_args()
    def interrupt(signum, frame):
        raise KeyboardInterrupt(f'signal {signum}')
    signal.signal(signal.SIGTERM, interrupt)
    if ROOT == MAIN or ROOT.name != 'vslam-noise-search-20261009':
        raise RuntimeError('refusing to run outside experimental worktree')
    protocol = json.loads(PROTOCOL.read_text())
    if not args.execute:
        print(json.dumps(dict(studies=[s['id'] for s in protocol['studies']],
            screening_runs=4*16*2, finalist_repeat_runs=4*2*2*2,
            maximum_full_vio_runs=16, maximum_full_vio_lc_runs=6,
            stage=args.stage), indent=2)); return
    with (ART/'controller.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        frozen = ART/'protocol.json'
        if frozen.exists() and frozen.read_bytes() != PROTOCOL.read_bytes():
            raise RuntimeError('protocol changed after the pilot was frozen')
        if not frozen.exists():
            frozen.write_bytes(PROTOCOL.read_bytes())
        event('controller_started', pid=os.getpid(), stage=args.stage, protocol_sha256=sha(PROTOCOL))
        try:
            for spec in protocol['studies']:
                if args.stage == 'smoke':
                    # First Rule C clip is a counted screening attempt, reused
                    # on resume; smoke testing consumes no hidden tuning budget.
                    run_attempt(spec, 'rule_c', spec['rule_c'], spec['clips'][0], 'vio', 1, 'screen')
                else:
                    run_study(spec, protocol, 'short')
                render_report(protocol)
            if args.stage == 'all':
                event('all_short_searches_finished')
                for spec in protocol['studies']:
                    # Replay saved short results, without estimator reruns.
                    run_study(spec, protocol, 'all')
                    render_report(protocol)
            verify_main()
            event('stage_finished', stage=args.stage)
        except BaseException as exc:
            render_report(protocol)
            event('controller_stopped', reason=f'{type(exc).__name__}: {exc}')
            raise


if __name__ == '__main__':
    main()
