#!/usr/bin/env python3
"""Sielinko CPU noise search: the existing search stages on two pinned CPU lanes.

Default is a dry plan. Stages, each needing its own reviewed go:

    check    one sentinel attempt per study on the first clip (plumbing, pinning, receipts)
    develop  the unchanged development search per study (preliminary, screen, full, N=3)
    final    fresh N=1 runs of each frozen selection on the test sequences

Studies run one per lane, serial inside a study. A study keeps a declared lane;
an exclusive study (Basalt) starts only after every other study, with the host
idle. Activation needs a frozen protocol, its execution identity, the lane
owner's written handover and, for develop/final, the reviewed check readiness.
Create STOP_AFTER_CURRENT in the artifact directory to stop between attempts.
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
import sielinko_lanes as lanes

BASE = execution.base
LANES = ('lane1', 'lane2')
EXCLUSIVE = 'exclusive'
CHECK_HOURS = 6


# Rule C's graceful stop also stops new search launches (revision 13 restart procedure).
EXTERNAL_STOPS = (Path('/data/imoroz/rule-c-batch-20261018/STOP_AFTER_CURRENT'),)


def stopped(art):
    return (Path(art) / 'STOP_AFTER_CURRENT').exists()


def stop_reason(art):
    if stopped(art):
        return 'Campaign requested stop at attempt boundary'
    found = [str(p) for p in EXTERNAL_STOPS if p.exists()]
    return 'External stop request: ' + ', '.join(found) if found else None


def sentinel(spec):
    """Distinct from every control, so the native receipts prove the candidate reached the estimator."""
    rule = next(c['params'] for c in spec['controls'] if c['label'] == 'rule_c')
    return {key: 2 * value for key, value in rule.items()}


def verify_handover(protocol):
    handover = protocol.get('lane_handover')
    if not handover:
        raise RuntimeError('No written lane handover from the lane owner')
    path = Path(handover['path'])
    if not path.is_file() or BASE.sha(path) != handover['sha256']:
        raise RuntimeError('Lane handover missing or changed: ' + str(path))
    record = json.loads(path.read_text())
    for lane in LANES:
        declared = record.get('lanes', {}).get(lane, {})
        if declared.get('cpus') != protocol['lanes'][lane]['cpus'] or declared.get('handed_over') is not True:
            raise RuntimeError('Handover does not release ' + lane + ' with its declared cores')
    return record


def lane_for(spec, active, pending):
    """The lane a study may start in now, or None. Never two studies in one lane."""
    if EXCLUSIVE in active:
        return None
    if spec.get('lane') == EXCLUSIVE:
        others = [s for s in pending if s.get('lane') != EXCLUSIVE]
        return EXCLUSIVE if not active and not others else None
    wanted = [spec['lane']] if spec.get('lane') else list(LANES)
    return next((lane for lane in wanted if lane not in active), None)


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


def worker(args, protocol):
    art = Path(args.art).resolve()
    spec = next(s for s in protocol['studies'] if s['id'] == args.study)
    directory = worker_directory(art, spec, args.stage)
    result = dict(study=spec['id'], stage=args.stage, lane=args.lane, started=BASE.now())
    try:
        with lanes.lane_locks(protocol, args.lane, stop=lambda: stop_reason(art) is not None,
                              on_wait=lambda path: BASE.event('waiting_for_lane_lock', lock=path)):
            execution.configure(directory, protocol, lambda: lane_slot(art, protocol, args.lane, args.parent_pid),
                                lane=args.lane)
            execution.verify_frozen()
            search = DevelopmentSearch(execution, spec, protocol)
            if args.stage == 'check':
                execution.run_attempt(spec, 'sentinel', sentinel(spec), spec['clips'][0], 'vio', 1, 'check')
            elif args.stage == 'develop':
                search.develop()
            elif args.stage == 'final':
                search.final_n1()
            else:
                raise ValueError('Invalid worker stage')
        result.update(complete=True, finished=BASE.now())
    except InterruptedError as exc:
        result.update(complete=False, finished=BASE.now(), reason=str(exc))
    except BaseException as exc:
        result.update(complete=False, finished=BASE.now(), reason=f'{type(exc).__name__}: {exc}')
        raise
    finally:
        BASE.write(directory / (args.stage + '-completion.json'), result)


def worker_directory(art, spec, stage):
    # Check attempts keep their own records and budget; they never enter selection.
    return art / ('checks' if stage == 'check' else 'workers') / spec['id']


def prepare_worker(art, spec, stage):
    directory = worker_directory(art, spec, stage)
    directory.mkdir(parents=True, exist_ok=True)
    for name in ('protocol.json', 'execution-identity.json', 'main-before.json'):
        campaign.copy_identity(art / name, directory / name)
    if stage == 'check':
        if not (directory / 'budget.json').exists():
            start = time.time()
            BASE.write(directory / 'budget.json', dict(started_unix=start, deadline_unix=start + CHECK_HOURS * 3600))
    else:
        campaign.copy_identity(art / 'budget.json', directory / 'budget.json')
    return directory


def launch(art, spec, stage, lane):
    directory = prepare_worker(art, spec, stage)
    with (directory / (stage + '.controller.log')).open('ab') as log:
        return subprocess.Popen([sys.executable, '-B', str(Path(__file__).resolve()),
            '--worker', '--art', str(art), '--study', spec['id'], '--stage', stage,
            '--lane', lane, '--parent-pid', str(os.getpid())],
            cwd=execution.ROOT, stdout=log, stderr=subprocess.STDOUT)


def run_stage(art, protocol, stage):
    pending = [s for s in protocol['studies']
               if not (worker_directory(art, s, stage) / (stage + '-completion.json')).is_file()
               or not json.loads((worker_directory(art, s, stage) / (stage + '-completion.json')).read_text()).get('complete')]
    active = {}
    try:
        while pending or active:
            if not stopped(art):
                for spec in list(pending):
                    lane = lane_for(spec, active, pending)
                    if lane is not None:
                        active[lane] = (spec, launch(art, spec, stage, lane))
                        pending.remove(spec)
            if stage != 'check':
                campaign.collect(art, protocol['studies'])
            for lane, (spec, process) in list(active.items()):
                if process.poll() is None:
                    continue
                path = worker_directory(art, spec, stage) / (stage + '-completion.json')
                if process.returncode != 0 or not (path.is_file() and json.loads(path.read_text()).get('complete')):
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
    if stage != 'check':
        campaign.collect(art, protocol['studies'])
    return True


def check_report(art, protocol):
    """Summarize the check attempts for review; readiness itself is written by the reviewer."""
    studies, evidence = {}, []
    for spec in protocol['studies']:
        records = sorted((worker_directory(art, spec, 'check') / 'attempts').glob('*.json'))
        rows = [json.loads(p.read_text()) for p in records]
        evidence += [dict(path=str(p), sha256=BASE.sha(p)) for p in records]
        ok = bool(rows) and all(r.get('state') == 'finished' and r.get('returncode') == 0
                                and not r['result']['failed'] for r in rows)
        studies[spec['id']] = dict(attempts=[r['key'] for r in rows], passed=ok,
                                   returncodes=[r.get('returncode') for r in rows])
    return dict(time=BASE.now(), protocol_sha256=BASE.sha(art / 'protocol.json'),
                execution_manifest_sha256=BASE.sha(art / 'execution-identity.json'),
                studies=studies, evidence=evidence,
                note='A passing attempt is necessary, not sufficient: review its native receipts and lane samples.')


def coordinator(args, protocol):
    art = campaign.artifact_root(args.art)
    if stopped(art):
        raise RuntimeError('Existing stop request requires review before resuming')
    stages = ['develop', 'final'] if args.stage == 'all' else [args.stage]
    if stages != ['check']:
        readiness = campaign.verify_activation(art, protocol)
    verify_handover(protocol)
    with (art / 'controller.lock').open('a') as controller:
        fcntl.flock(controller, fcntl.LOCK_EX | fcntl.LOCK_NB)
        execution.configure(art, protocol, None)
        execution.verify_frozen()
        if stages != ['check']:
            campaign_budget(art, protocol)
            campaign.immutable(art / 'activation.json', dict(protocol_sha256=BASE.sha(art / 'protocol.json'),
                execution_manifest_sha256=BASE.sha(art / 'execution-identity.json'),
                readiness_sha256=BASE.sha(art / 'readiness.json'), scheduling=readiness['validated_scheduling']))
        complete = True
        for stage in stages:
            if not run_stage(art, protocol, stage):
                complete = False
                break
        if stages == ['check']:
            BASE.write(art / 'check-report.json', check_report(art, protocol))
        execution.verify_frozen()
        BASE.event('campaign_finished', complete=complete, stages=stages)


def dry_plan(art, protocol):
    clip = len(protocol['studies'][0]['clips'])
    pre, screen, full = protocol['preliminary'], protocol['screen'], protocol['full']
    controls = len(protocol['studies'][0]['controls'])
    short = (pre['candidates'] * clip + pre['finalists'] * (pre['repetitions'] - 1) * clip
             + len(screen['seeds']) * screen['candidates_per_seed'] * clip - (len(screen['seeds']) - 1) * controls * clip)
    development = full['candidates'] + (full['finalists'] + controls) * (full['repetitions'] - 1)
    return dict(campaign=protocol['campaign_id'], status=protocol['status'], studies=[s['id'] for s in protocol['studies']],
                lanes={k: v['cpus'] for k, v in protocol['lanes'].items()},
                attempts_per_study=dict(short_clip_runs=short, first_half_runs_at_most=development,
                                        final_runs=len(protocol['studies'][0]['test_sequences'])
                                        + len(protocol['studies'][0].get('final_control_sequences', []))),
                pending=protocol.get('pending', []), artifacts=str(art),
                readiness_exists=(Path(art) / 'readiness.json').is_file(), executed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--art', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, help='draft protocol for a dry plan before freezing')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--stage', choices=('check', 'develop', 'final', 'all'), default='all')
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--study')
    parser.add_argument('--lane', choices=LANES + (EXCLUSIVE,))
    parser.add_argument('--parent-pid', type=int)
    args = parser.parse_args()
    args.art = campaign.artifact_root(args.art)

    def interrupt(signum, frame):
        raise KeyboardInterrupt(f'signal {signum}')
    signal.signal(signal.SIGTERM, interrupt)
    if not args.execute and not args.worker:
        source = args.protocol or args.art / 'protocol.json'
        print(json.dumps(dry_plan(args.art, json.loads(Path(source).read_text())), indent=2))
        return
    protocol = json.loads((args.art / 'protocol.json').read_text())
    if args.worker:
        worker(args, protocol)
    else:
        coordinator(args, protocol)


if __name__ == '__main__':
    main()
