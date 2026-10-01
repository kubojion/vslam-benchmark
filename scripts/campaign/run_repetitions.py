#!/usr/bin/env python3
"""Resume individual repetitions without replacing any previous attempt.

A physical run ID is consumed at most once. Existing trajectories are evaluated
before new estimation; an interrupted/failed attempt is never retried in place.
Publication qualification and manifest-approved reuse are separate operations.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO/'scripts/results'))
from prepare_cell import component, validate_cell


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.'+path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f'another process holds {path.name}') from exc
        yield


def now():
    return datetime.now(timezone.utc).isoformat()


def run_command(command, *, check=False):
    """Forward interruption to the active subprocess group and preserve state."""
    process = subprocess.Popen(command, cwd=REPO, start_new_session=True)
    try:
        code = process.wait()
    except BaseException:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        raise
    return subprocess.CompletedProcess(command, code)


def execute_attempt(run_dir, state_path, *, runner, evaluator, cache_check, validator,
                    execute=run_command, identity=None, recover_only=False):
    """No shell strings or deletion. Injectable executor permits estimator-free tests."""
    state = json.loads(state_path.read_text()) if state_path.exists() else {'events': []}
    identity = identity or {}
    if state.get('identity', identity) != identity:
        raise RuntimeError('attempt identity changed; use a new physical run ID')
    state['identity'] = identity

    def event(status, **fields):
        state.update(status=status, **fields)
        state['events'].append(dict(at=now(), status=status, **fields))
        atomic_json(state_path, state)

    trajectory = run_dir/'trajectory.txt'
    launched = False
    if not trajectory.is_file():
        if recover_only and not run_dir.exists() and not state.get('events'):
            # Inspection does not consume a future physical attempt ID.
            return dict(state, status='no_saved_attempt')
        if run_dir.exists() or state.get('events') or recover_only:
            event('preserved_without_trajectory', reason='existing attempt or recovery-only; estimation was not restarted')
            return state
        # Persist before spawn so interruption cannot cause an invisible retry.
        event('estimator_starting', command=runner)
        launched = True
        try:
            code = execute(runner, check=False).returncode
            event('estimator_finished', estimator_exit_code=code)
        except BaseException as exc:
            event('interrupted', error=f'{type(exc).__name__}: {exc}')
            raise
    if not trajectory.is_file():
        event('no_trajectory', reason='attempt retained; no automatic retry')
        return state
    # Always try to recover a saved trajectory, including after a nonzero exit.
    try:
        current = execute(cache_check, check=False).returncode == 0
        if not current:
            event('evaluating')
            code = execute(evaluator, check=False).returncode
            if code:
                event('evaluation_failed', evaluation_exit_code=code)
                return state
        doc = json.loads((run_dir/'run_eval.json').read_text())
        meta = json.loads((run_dir/'run_meta.json').read_text()) if (run_dir/'run_meta.json').is_file() else {}
        process_code = meta.get('process', {}).get('exit_code')
        # A zero wrapper exit cannot erase the estimator's recorded nonzero exit.
        clean_exit = process_code == 0 and state.get('estimator_exit_code', 0) == 0
        valid = execute(validator, check=False).returncode == 0
        # Do not manufacture historical completion markers. New attempts can get
        # a marker only after immediate evaluation and clean process evidence.
        if launched and valid and clean_exit:
            marker = run_dir/'COMPLETE'
            with marker.open('x'):
                pass
        status = ('evaluated' if valid and clean_exit and doc.get('run_status') == 'ok'
                  else 'evaluated_failure_or_review')
        event(status, numerical_status=doc.get('run_status'), validation_passed=valid,
              recorded_process_exit_code=process_code,
              qualification=doc.get('qualification', {}).get('status', 'unreviewed'))
    except BaseException as exc:
        event('evaluation_interrupted', error=f'{type(exc).__name__}: {exc}')
        raise
    return state


def commands(repo, dataset, sequence, algorithm, run_id, mode):
    args = [dataset, sequence, algorithm, str(run_id), mode]
    python = os.environ.get('BENCHMARK_EVAL_PYTHON')
    prefix = [python] if python else ['conda', 'run', '--no-capture-output', '-n', 'macvo', 'python3']
    evaluate = prefix+[str(repo/'scripts/eval/_evaluate_run.py')]+args
    run = repo/'results'/mode/dataset/sequence/algorithm/f'run{run_id}'
    return dict(runner=['bash', str(repo/'scripts/run'/f'run_{algorithm}.sh'), dataset, sequence, str(run_id), mode],
                evaluator=evaluate, cache_check=evaluate+['--check-current'],
                validator=[sys.executable, str(repo/'scripts/results/validate_run.py'), str(run),
                           '--check-only', '--require-provenance', '2', '--require-measurements', '1'])


def main():
    def interrupted(signum, frame):
        raise InterruptedError(f'interrupted by signal {signum}')
    signal.signal(signal.SIGTERM, interrupted)
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('dataset', type=component); ap.add_argument('sequence', type=component)
    ap.add_argument('algorithm', type=component); ap.add_argument('repeats', type=int, nargs='?', default=3)
    ap.add_argument('run_type', choices=('vo','vo-lc','vio','vio-lc','gnss-vio'), nargs='?', default='vo')
    ap.add_argument('--run-id', type=int, help='one fresh physical attempt ID selected by a campaign manifest')
    ap.add_argument('--repetition', type=int, help='logical repetition when physical ID is different')
    ap.add_argument('--cohort', type=component, default='legacy-direct')
    ap.add_argument('--recover-only', action='store_true', help='evaluate saved outputs; never invoke estimators')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    if args.dataset in ('euroc','EuRoC-MAV'):
        args.dataset = 'euroc_mav'
    if args.repeats < 1 or (args.run_id is not None and args.run_id < 1):
        ap.error('repetition count and run ID must be positive')
    if args.repetition is not None and (args.run_id is None or args.repetition < 1):
        ap.error('--repetition requires --run-id and must be positive')
    cell = validate_cell(REPO, args.run_type, args.dataset, args.sequence, args.algorithm)
    ids = [args.run_id] if args.run_id is not None else range(1, args.repeats+1)
    key = '__'.join([args.run_type,args.dataset,args.sequence,args.algorithm])
    if args.dry_run:
        for run_id in ids:
            run = cell/f'run{run_id}'
            action = ('recover_evaluation' if (run/'trajectory.txt').is_file() else
                      'preserve_existing_attempt' if run.exists() else
                      'no_saved_attempt' if args.recover_only else 'new_attempt')
            print(json.dumps(dict(run=str(run.relative_to(REPO)),action=action,
                                 **commands(REPO,args.dataset,args.sequence,args.algorithm,run_id,args.run_type))))
        return 0
    if not (REPO/'datasets'/args.dataset/args.sequence).is_dir():
        ap.error('missing dataset sequence')
    if not (REPO/'scripts/run'/f'run_{args.algorithm}.sh').is_file():
        ap.error('missing runner')
    statuses = []
    # Global lock serializes estimator access to shared containers, GPU and native
    # output names. Evaluation-only recovery also respects active campaign writes.
    try:
        with lock(REPO/'results/.locks/execution.lock'), lock(REPO/'results/.locks'/f'{key}.lock'):
            for run_id in ids:
                run = cell/f'run{run_id}'
                state_path = REPO/'results/.attempt-state'/key/f'run{run_id}.json'
                orphan_log = REPO/'logs'/f'{args.dataset}_{args.sequence}_{args.algorithm}_{args.run_type}_run{run_id}.log'
                if not run.exists() and orphan_log.exists():
                    print(f'[resume] retained orphan log; physical ID run{run_id} is occupied', file=sys.stderr)
                    statuses.append('orphan_log'); continue
                outcome = execute_attempt(run,state_path,
                    **commands(REPO,args.dataset,args.sequence,args.algorithm,run_id,args.run_type),
                    identity=dict(cohort=args.cohort,repetition=args.repetition or run_id,physical_run_id=run_id),
                    recover_only=args.recover_only)
                statuses.append(outcome['status'])
                print(f"[resume] {key}/run{run_id}: {outcome['status']}", flush=True)
    except (ValueError,OSError,RuntimeError) as exc:
        print(f'[resume] {exc}',file=sys.stderr); return 2
    # This is execution/evaluation status, never a publication qualification tick.
    return 0 if all(s == 'evaluated' for s in statuses) else 1


if __name__ == '__main__':
    raise SystemExit(main())
