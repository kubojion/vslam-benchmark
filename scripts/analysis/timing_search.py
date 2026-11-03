#!/usr/bin/env python3
"""Cross-fit IMU noise search, PLAN Update 6 Job C: the Sielinko search stages on the frozen protocol.

Default is a dry plan that runs nothing. Stages, each needing its own reviewed go:

    check       gate: one sentinel attempt per system on a short clip of one dataset
    gate-repro  gate: OpenVINS and Voxel-SVIO at Rule C on full seq04, P-core lanes
    develop     tuning of every fold of one dataset (clip screen, full candidates, N=3 selection)
    test        the frozen winners, N=1 VIO and N=1 VIO-LC where supported, on the other sequence
    test-later  two more VIO repetitions per fold, on the same commit and worktree

A fold keeps to its declared lanes, one fold per lane, serial inside a fold. An exclusive fold (Basalt) starts
only after every other fold, with the host idle. Datasets run in the protocol's order, each after the review
of the one before. develop, test and test-later need a frozen protocol, its execution identity and the
reviewed readiness file. Create STOP_AFTER_CURRENT in the artifact directory to stop between attempts.
No part of this search takes a results/.locks file or looks at Rule C's stop file: Rule C is closed.
"""
import argparse
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import noise_campaign as campaign
import noise_campaign_engine as execution
from noise_campaign_search import DevelopmentSearch
from noise_execution_policy import campaign_budget
import timing_lanes as lanes

BASE = execution.base
EXCLUSIVE = 'exclusive'
LANES = ('cpu_a', 'cpu_b', 'gpu', EXCLUSIVE)
GATE_HOURS = 6
GATE_STAGES = ('check', 'gate-repro')
RUN_STAGES = ('develop', 'test', 'test-later')


def stopped(art):
    return (Path(art) / 'STOP_AFTER_CURRENT').exists()


def stop_reason(art):
    return 'Campaign requested stop at attempt boundary' if stopped(art) else None


def control(spec, label):
    return next(c['params'] for c in spec['controls'] if c['label'] == label)


def sentinel(spec):
    """Distinct from every control, so the native receipts prove the candidate reached the estimator."""
    return {key: 2 * value for key, value in control(spec, 'rule_c').items()}


def stage_folds(protocol, stage, dataset):
    """The folds a stage covers. The gates use one fold per system; the run stages all of one dataset."""
    by_id = {s['id']: s for s in protocol['folds']}
    if stage == 'gate-repro':
        lane = protocol['gates']['repro'].get('lane')
        return [dict(by_id[item['fold']], lanes=[lane]) if lane else by_id[item['fold']]
                for item in protocol['gates']['repro']['targets']]
    if dataset not in protocol['run_order']:
        raise ValueError('A stage needs one dataset of the run order')
    if stage == 'check':
        return [by_id[i] for i in protocol['gates']['check_folds'][dataset]]
    return [s for s in protocol['folds'] if s['dataset'] == dataset]


def lane_for(spec, active, pending, protocol):
    """The lane a fold may start in now, or None. Never two folds in one lane."""
    if EXCLUSIVE in active:
        return None
    if spec['lanes'] == [EXCLUSIVE]:
        others = [s for s in pending if s['lanes'] != [EXCLUSIVE]]
        return EXCLUSIVE if not active and not others else None
    # Native output names are shared by sequence and container, as in the Rule C controller.
    running = {item[0]['algorithm'] for item in active.values()}
    if spec['algorithm'] in running and spec['algorithm'] not in protocol['scheduling']['same_algorithm_concurrent']:
        return None
    return next((lane for lane in spec['lanes'] if lane not in active), None)


@contextmanager
def lane_slot(art, protocol, lane, parent):
    """Wait for this lane's launch conditions, then sample the attempt while it runs."""
    poll, previous = protocol['launch_policy']['poll_s'], None
    while True:
        reason = stop_reason(art)
        if reason:
            raise InterruptedError(reason)
        if os.getppid() != parent:
            raise RuntimeError('Coordinator is no longer the parent of this worker')
        reasons = lanes.launch_blockers(protocol, lane)
        if not reasons:
            break
        if reasons != previous:  # record changes, not every poll
            BASE.event('waiting_for_lane', lane=lane, reasons=reasons)
            previous = reasons
        time.sleep(poll)
    sampler = lanes.Sampler(protocol, lane, execution.CURRENT, Path(execution.ART) / 'lane-samples')
    sampler.start()
    try:
        yield
    except BaseException:
        sampler.stop()
        raise
    summary = sampler.stop()
    if summary['errors']:
        raise RuntimeError('Lane check failed for ' + execution.CURRENT['key'] + ': ' + '; '.join(summary['errors']))


def run_worker_stage(stage, spec, protocol):
    search = DevelopmentSearch(execution, spec, protocol)
    if stage == 'check':
        execution.run_attempt(spec, 'sentinel', sentinel(spec), spec['clips'][0], 'vio', 1, 'check')
    elif stage == 'gate-repro':
        execution.run_attempt(spec, 'rule_c', control(spec, 'rule_c'), spec['full_sequences'][0], 'vio', 1, 'gate_repro')
    elif stage == 'develop':
        search.develop()
    elif stage == 'test':
        search.final_n1()
    elif stage == 'test-later':
        search.final_later()
    else:
        raise ValueError('Invalid worker stage')


def worker(args, protocol):
    art = Path(args.art).resolve()
    spec = next(s for s in protocol['folds'] if s['id'] == args.study)
    directory = worker_directory(art, spec, args.stage)
    result = dict(study=spec['id'], stage=args.stage, lane=args.lane, started=BASE.now())
    try:
        execution.configure(directory, protocol, lambda: lane_slot(art, protocol, args.lane, args.parent_pid),
                            lane=args.lane)
        execution.verify_frozen()
        run_worker_stage(args.stage, spec, protocol)
        result.update(complete=True, finished=BASE.now())
    except InterruptedError as exc:
        result.update(complete=False, finished=BASE.now(), reason=str(exc))
    except BaseException as exc:
        result.update(complete=False, finished=BASE.now(), reason=f'{type(exc).__name__}: {exc}')
        raise
    finally:
        BASE.write(directory / (args.stage + '-completion.json'), result)


def worker_directory(art, spec, stage):
    # Gate attempts keep their own records and budget; they never enter selection.
    group = {'check': 'checks', 'gate-repro': 'gates'}.get(stage, 'workers')
    return Path(art) / group / spec['id']


def prepare_worker(art, spec, stage):
    directory = worker_directory(art, spec, stage)
    directory.mkdir(parents=True, exist_ok=True)
    for name in ('protocol.json', 'execution-identity.json', 'main-before.json'):
        campaign.copy_identity(art / name, directory / name)
    if stage in GATE_STAGES:
        if not (directory / 'budget.json').exists():
            start = time.time()
            BASE.write(directory / 'budget.json', dict(started_unix=start, deadline_unix=start + GATE_HOURS * 3600))
    else:
        campaign.copy_identity(art / ('budget-' + spec['dataset'] + '.json'), directory / 'budget.json')
    return directory


def launch(art, spec, stage, lane):
    directory = prepare_worker(art, spec, stage)
    with (directory / (stage + '.controller.log')).open('ab') as log:
        return subprocess.Popen([sys.executable, '-B', str(Path(__file__).resolve()),
            '--worker', '--art', str(art), '--study', spec['id'], '--stage', stage,
            '--lane', lane, '--parent-pid', str(os.getpid())],
            cwd=execution.ROOT, stdout=log, stderr=subprocess.STDOUT)


def complete(art, spec, stage):
    path = worker_directory(art, spec, stage) / (stage + '-completion.json')
    return path.is_file() and json.loads(path.read_text()).get('complete') is True


def run_stage(art, protocol, stage, folds):
    pending = [s for s in folds if not complete(art, s, stage)]
    active = {}
    try:
        while pending or active:
            if not stopped(art):
                for spec in list(pending):
                    lane = lane_for(spec, active, pending, protocol)
                    if lane is not None:
                        active[lane] = (spec, launch(art, spec, stage, lane))
                        pending.remove(spec)
            if stage not in GATE_STAGES:
                campaign.collect(art, folds)
            for lane, (spec, process) in list(active.items()):
                if process.poll() is None:
                    continue
                if process.returncode != 0 or not complete(art, spec, stage):
                    campaign.stop_request(art, 'Worker stopped or failed: ' + spec['id'] + ' stage=' + stage)
                del active[lane]
            BASE.write(art / 'status.json', dict(time=BASE.now(), event='campaign_progress', stage=stage,
                active={lane: spec['id'] for lane, (spec, _) in active.items()},
                pending=[s['id'] for s in pending], stopping=stopped(art)))
            if stopped(art) and not active:
                return False
            if pending or active:
                time.sleep(10)
    except BaseException:
        for _, process in active.values():
            if process.poll() is None:
                process.terminate()
        for _, process in active.values():
            process.wait()
        raise
    if stage not in GATE_STAGES:
        campaign.collect(art, folds)
    return True


def stage_report(art, protocol, stage, folds):
    """Summarize gate attempts for review; readiness itself is written by the reviewer."""
    studies, evidence = {}, []
    for spec in folds:
        records = sorted((worker_directory(art, spec, stage) / 'attempts').glob('*.json'))
        rows = [json.loads(p.read_text()) for p in records]
        evidence += [dict(path=str(p), sha256=BASE.sha(p)) for p in records]
        ok = bool(rows) and all(r.get('state') == 'finished' and r.get('returncode') == 0
                                and not r['result']['failed'] for r in rows)
        studies[spec['id']] = dict(attempts=[r['key'] for r in rows], passed=ok,
                                   returncodes=[r.get('returncode') for r in rows],
                                   numerical_status=[r['result'].get('numerical_status') for r in rows if 'result' in r],
                                   ate_se3_rmse_m=[r['result'].get('ate_se3_rmse_m') for r in rows if 'result' in r])
    return dict(time=BASE.now(), stage=stage, protocol_sha256=BASE.sha(art / 'protocol.json'),
                execution_manifest_sha256=BASE.sha(art / 'execution-identity.json'),
                studies=studies, evidence=evidence,
                note=('A passing attempt is necessary, not sufficient: review its native receipts and lane samples. '
                      'An estimator that diverges with exit code 0 shows passed false: a divergence is a result, not a plumbing fault.'))


def repro_verdict(report, protocol):
    """Compare the two full seq04 runs with the corrected Rule C values."""
    policy, rows = protocol['gates']['repro'], {}
    for item in policy['targets']:
        values = report['studies'].get(item['fold'], {}).get('ate_se3_rmse_m') or []
        value = values[0] if len(values) == 1 else None
        rows[item['algorithm']] = dict(expected_m=item['expected_m'], measured_m=value, passed=(
            value is not None and abs(value / item['expected_m'] - 1) <= policy['relative_tolerance']))
    return dict(relative_tolerance=policy['relative_tolerance'], targets=rows,
                passed=all(r['passed'] for r in rows.values()))


def verify_order(art, protocol, dataset):
    """CitrusFarm, then stop for review, then HortiMulti, then Rosario."""
    order = protocol['run_order']
    for earlier in order[:order.index(dataset)]:
        path = Path(art) / 'reviews' / (earlier + '.json')
        if not path.is_file() or json.loads(path.read_text()).get('passed') is not True:
            raise RuntimeError('The review of ' + earlier + ' must pass first: ' + str(path))


def verify_stage_order(art, stage, folds):
    needed = {'test': 'develop', 'test-later': 'test'}.get(stage)
    missing = [s['id'] for s in folds if needed and not complete(art, s, needed)]
    if missing:
        raise RuntimeError(stage + ' needs ' + needed + ' to finish first: ' + ', '.join(missing))


def coordinator(args, protocol):
    art = campaign.artifact_root(args.art)
    if stopped(art):
        raise RuntimeError('Existing stop request requires review before resuming')
    stages = ['develop', 'test'] if args.stage == 'all' else [args.stage]
    groups = {stage: stage_folds(protocol, stage, args.dataset) for stage in stages}
    gated = stages[0] in RUN_STAGES
    if gated:
        readiness = campaign.verify_activation(art, protocol, args.dataset)
        verify_order(art, protocol, args.dataset)
    with (art / 'controller.lock').open('a') as controller:  # the artifact directory's own file
        fcntl.flock(controller, fcntl.LOCK_EX | fcntl.LOCK_NB)
        execution.configure(art, protocol, None)
        execution.verify_frozen()
        if gated:
            campaign_budget(art, protocol, args.dataset)
            campaign.immutable(art / ('activation-' + args.dataset + '.json'), dict(
                protocol_sha256=BASE.sha(art / 'protocol.json'),
                execution_manifest_sha256=BASE.sha(art / 'execution-identity.json'),
                readiness_sha256=BASE.sha(art / 'readiness.json'), scheduling=readiness['validated_scheduling']))
        finished = True
        for stage in stages:
            verify_stage_order(art, stage, groups[stage])
            if not run_stage(art, protocol, stage, groups[stage]):
                finished = False
                break
        if stages[0] in GATE_STAGES:
            report = stage_report(art, protocol, stages[0], groups[stages[0]])
            if stages[0] == 'gate-repro':
                report['verdict'] = repro_verdict(report, protocol)
            name = stages[0] + ('-' + args.dataset if args.dataset else '') + '-report.json'
            BASE.write(art / name, report)
        execution.verify_frozen()
        BASE.event('campaign_finished', complete=finished, stages=stages, dataset=args.dataset)


def fold_runs(protocol, spec):
    """Attempts of one fold. C and M are enqueued in both seeds and measured once; duplicates merge at N=3."""
    screen, full = protocol['screen'], protocol['full']
    clips, controls = len(spec['clips']), len(spec['controls'])
    short = (len(screen['seeds']) * screen['candidates_per_seed'] - (len(screen['seeds']) - 1) * controls) * clips
    selection = (full['finalists'] + controls) * (full['repetitions'] - 1)
    return dict(short_clip_runs=short, full_candidate_runs=full['candidates'],
                selection_runs_at_most=selection, test_vio=len(spec['test_sequences']),
                test_vio_lc=len(spec['test_sequences']) if 'vio-lc' in spec['final_modes'] else 0,
                test_later_vio=len(protocol['test_later']['repetitions']) * len(spec['test_sequences']))


def fold_hours(protocol, spec, runs):
    wall = protocol['wall_estimates_s'][spec['dataset']][spec['algorithm']]
    tuning = runs['short_clip_runs'] * wall['clip'] + (runs['full_candidate_runs'] + runs['selection_runs_at_most']) * wall['vio']
    now = tuning + runs['test_vio'] * wall['vio'] + runs['test_vio_lc'] * wall.get('vio-lc', 0)
    return now / 3600, runs['test_later_vio'] * wall['vio'] / 3600


def dataset_plan(protocol, dataset):
    """Runs and hours of one dataset. Lanes are filled evenly; nothing waits for other work on the host."""
    groups, runs, machine, later = {}, {}, 0, 0
    for spec in protocol['folds']:
        if spec['dataset'] != dataset:
            continue
        counts = fold_runs(protocol, spec)
        for key, value in counts.items():
            runs[key] = runs.get(key, 0) + value
        now_h, later_h = fold_hours(protocol, spec, counts)
        machine, later = machine + now_h, later + later_h
        group = '+'.join(spec['lanes'])
        groups[group] = groups.get(group, 0) + now_h
    exclusive = groups.pop(EXCLUSIVE, 0)
    wall = max(hours / (group.count('+') + 1) for group, hours in groups.items()) + exclusive
    return dict(folds=sum(s['dataset'] == dataset for s in protocol['folds']), runs=runs,
                runs_now_at_most=sum(v for k, v in runs.items() if k != 'test_later_vio'),
                machine_hours_now=round(machine, 1), wall_hours_now=round(wall, 1),
                machine_hours_test_later=round(later, 1))


def dry_plan(art, protocol, dataset=None):
    datasets = [dataset] if dataset else protocol['run_order']
    plan = {name: dataset_plan(protocol, name) for name in datasets}
    studies = [s for s in protocol['studies'] if s['dataset'] in datasets]
    return dict(campaign=protocol['campaign_id'], status=protocol['status'], studies=len(studies),
                folds=sum(p['folds'] for p in plan.values()), run_order=protocol['run_order'],
                stages=[dict(name='screen', description=f"{len(protocol['screen']['seeds'])} seeds x "
                             f"{protocol['screen']['candidates_per_seed']} candidates, N=1, two 180-s clips"),
                        dict(name='full', description=f"{protocol['full']['candidates']} full-sequence candidates, N=1"),
                        dict(name='selection', description=f"best {protocol['full']['finalists']} + C + M, "
                             f"N={protocol['full']['repetitions']} on the tuning sequence"),
                        dict(name='test', description='winner N=1 VIO and N=1 VIO-LC where supported, other sequence'),
                        dict(name='test-later', description='two more VIO repetitions per fold')],
                runs_per_fold=fold_runs(protocol, protocol['folds'][0]), datasets=plan,
                runs_now_at_most=sum(p['runs_now_at_most'] for p in plan.values()),
                wall_hours_now=round(sum(p['wall_hours_now'] for p in plan.values()), 1),
                wall_hours_note='Estimate from the first search\'s median wall times, lanes full, no faults or review time.',
                lanes={k: v['cpus'] for k, v in protocol['lanes'].items()},
                run_ids=protocol['run_ids']['range'], pending=protocol.get('pending', []), artifacts=str(art),
                readiness_exists=(Path(art) / 'readiness.json').is_file(), executed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--art', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, help='draft protocol for a dry plan before freezing')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--stage', choices=GATE_STAGES + RUN_STAGES + ('all',), default='all')
    parser.add_argument('--dataset')
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--study')
    parser.add_argument('--lane', choices=LANES)
    parser.add_argument('--parent-pid', type=int)
    args = parser.parse_args()
    args.art = campaign.artifact_root(args.art)

    def interrupt(signum, frame):
        raise KeyboardInterrupt(f'signal {signum}')
    signal.signal(signal.SIGTERM, interrupt)
    if not args.execute and not args.worker:
        source = args.protocol or args.art / 'protocol.json'
        print(json.dumps(dry_plan(args.art, json.loads(Path(source).read_text()), args.dataset), indent=2))
        return
    protocol = json.loads((args.art / 'protocol.json').read_text())
    if args.worker:
        worker(args, protocol)
    else:
        coordinator(args, protocol)


if __name__ == '__main__':
    main()
