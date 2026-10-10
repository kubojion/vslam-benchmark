#!/usr/bin/env python3
"""Coordinate validated independent development studies, then serial final N=1.

Default is a dry plan. Activation requires a frozen protocol, matching readiness
evidence, and the exclusive production execution lock. No production file is
modified, and this controller cannot run alongside the earlier pilot.
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

import noise_campaign_engine as execution
from noise_campaign_search import DevelopmentSearch
from noise_execution_policy import can_launch, campaign_budget

BASE = execution.base
LOCK = BASE.MAIN / 'results/.locks/execution.lock'


def artifact_root(path):
    path = Path(path).resolve()
    if path == BASE.MAIN.resolve() or BASE.MAIN.resolve() in path.parents:
        raise RuntimeError('Refusing to put campaign artifacts in the production worktree')
    return path


def immutable(path, value):
    path = Path(path)
    if path.exists():
        if json.loads(path.read_text()) != value:
            raise RuntimeError('Frozen campaign asset changed: ' + str(path))
    else:
        BASE.write(path, value)


def copy_identity(source, target):
    if target.exists() and target.read_bytes() != source.read_bytes():
        raise RuntimeError('Worker identity differs: ' + str(target))
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())


def verify_activation(art, protocol):
    readiness = json.loads((art / 'readiness.json').read_text())
    if readiness.get('passed') is not True or readiness.get('pending'):
        raise RuntimeError('Native/input/concurrency readiness is incomplete')
    if readiness['protocol_sha256'] != BASE.sha(art / 'protocol.json'):
        raise RuntimeError('Readiness belongs to another protocol')
    if readiness['execution_manifest_sha256'] != BASE.sha(art / 'execution-identity.json'):
        raise RuntimeError('Readiness belongs to another native/code identity')
    wanted = {s['id'] for s in protocol['studies']}
    if set(readiness['studies']) != wanted or not all(
            v.get('ready') is True for v in readiness['studies'].values()):
        raise RuntimeError('Some requested studies have no native validation')
    if readiness['validated_scheduling'] != protocol['scheduling']:
        raise RuntimeError('Proposed concurrency differs from validated scheduling')
    for item in readiness['evidence']:
        if BASE.sha(Path(item['path'])) != item['sha256']:
            raise RuntimeError('Readiness evidence changed: ' + item['path'])
    return readiness


@contextmanager
def leased_slot(art, fd, parent):
    if (art / 'STOP_AFTER_CURRENT').exists():
        raise InterruptedError('Campaign requested stop at attempt boundary')
    if os.getppid() != parent:
        raise RuntimeError('Coordinator is no longer the parent of this worker')
    a, b = os.fstat(fd), LOCK.stat()
    if (a.st_dev, a.st_ino) != (b.st_dev, b.st_ino):
        raise RuntimeError('Worker does not hold the inherited machine lease')
    with LOCK.open('rb') as check:
        try:
            fcntl.flock(check, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            pass
        else:
            raise RuntimeError('Coordinator machine lease is not locked')
    if BASE.production_processes():
        raise RuntimeError('Production execution detected under the experiment lease')
    yield


def worker(args, protocol):
    art = Path(args.art).resolve()
    spec = next(s for s in protocol['studies'] if s['id'] == args.study)
    directory = art / 'workers' / spec['id']
    execution.configure(directory, protocol,
                        lambda: leased_slot(art, args.lease_fd, args.parent_pid))
    result = dict(study=spec['id'], stage=args.stage, started=BASE.now())
    search = DevelopmentSearch(execution, spec, protocol)
    try:
        execution.verify_frozen()
        if args.stage == 'develop':
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


def prepare_worker(art, spec):
    directory = art / 'workers' / spec['id']
    directory.mkdir(parents=True, exist_ok=True)
    for name in ('protocol.json', 'execution-identity.json', 'main-before.json', 'budget.json'):
        copy_identity(art / name, directory / name)
    return directory


def launch(art, spec, stage, lease):
    directory = prepare_worker(art, spec)
    with (directory / (stage + '.controller.log')).open('ab') as log:
        return subprocess.Popen([sys.executable, '-B', str(Path(__file__).resolve()),
            '--worker', '--art', str(art), '--study', spec['id'], '--stage', stage,
            '--lease-fd', str(lease.fileno()), '--parent-pid', str(os.getpid())],
            cwd=execution.ROOT, pass_fds=(lease.fileno(),), stdout=log, stderr=subprocess.STDOUT)


def collect(art, specs):
    for spec in specs:
        directory = art / 'workers' / spec['id']
        for path in (directory / 'attempts').glob('*.json'):
            record = json.loads(path.read_text())
            target = art / 'attempts' / path.name
            if target.exists():
                old = json.loads(target.read_text())
                if old == record:
                    continue
                if old.get('state') == 'finished' or any(
                        old.get(k) != record.get(k) for k in ('key', 'run', 'params', 'campaign_id')):
                    raise RuntimeError('Collected observation identity changed: ' + str(target))
            BASE.write(target, record)
        for path in (directory / 'studies').rglob('*.json'):
            immutable(art / 'studies' / path.relative_to(directory / 'studies'), json.loads(path.read_text()))


def stop_request(art, reason):
    target = art / 'STOP_AFTER_CURRENT'
    if not target.exists():
        target.write_text(reason + '\n')


def run_stage(art, protocol, lease, stage):
    pending = []
    for spec in protocol['studies']:
        previous = art / 'workers' / spec['id'] / (stage + '-completion.json')
        if not previous.exists() or not json.loads(previous.read_text()).get('complete'):
            pending.append(spec)
    active = {}
    try:
        while pending or active:
            stopped = (art / 'STOP_AFTER_CURRENT').exists()
            if not stopped:
                for spec in list(pending):
                    if stage == 'final' and active:
                        break
                    if stage == 'develop' and not can_launch(
                            spec, [x[0] for x in active.values()], protocol['scheduling']):
                        continue
                    active[spec['id']] = (spec, launch(art, spec, stage, lease))
                    pending.remove(spec)
            collect(art, protocol['studies'])
            for study, (spec, process) in list(active.items()):
                if process.poll() is None:
                    continue
                completed_path = art / 'workers' / study / (stage + '-completion.json')
                complete = completed_path.is_file() and json.loads(completed_path.read_text()).get('complete')
                if process.returncode != 0 or not complete:
                    stop_request(art, 'Worker stopped or failed: ' + study + ' stage=' + stage)
                del active[study]
            BASE.write(art / 'status.json', dict(time=BASE.now(), event='campaign_progress',
                stage=stage, active=list(active), pending=[s['id'] for s in pending],
                stopping=(art / 'STOP_AFTER_CURRENT').exists()))
            if (art / 'STOP_AFTER_CURRENT').exists() and not active:
                return False
            if pending or active:
                time.sleep(10)
    except BaseException:
        for _, process in active.values():
            if process.poll() is None:
                process.terminate()
        for _, process in active.values():
            process.wait()
        collect(art, protocol['studies'])
        raise
    collect(art, protocol['studies'])
    return True


def coordinator(args, protocol):
    art = artifact_root(args.art)
    if (art / 'STOP_AFTER_CURRENT').exists():
        raise RuntimeError('Existing stop request requires review before resuming')
    readiness = verify_activation(art, protocol)
    with (art / 'controller.lock').open('a') as controller, LOCK.open('rb') as lease:
        fcntl.flock(controller, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
        execution.configure(art, protocol, lambda: leased_slot(art, lease.fileno(), os.getppid()))
        execution.verify_frozen()
        if BASE.production_processes():
            raise RuntimeError('Production process active')
        campaign_budget(art, protocol)
        immutable(art / 'activation.json', dict(protocol_sha256=BASE.sha(art / 'protocol.json'),
            execution_manifest_sha256=BASE.sha(art / 'execution-identity.json'),
            readiness_sha256=BASE.sha(art / 'readiness.json'),
            scheduling=readiness['validated_scheduling']))
        stages = ['develop', 'final'] if args.stage == 'all' else [args.stage]
        complete = True
        for stage in stages:
            if not run_stage(art, protocol, lease, stage):
                complete = False
                break
        execution.verify_frozen()
        BASE.event('campaign_finished', complete=complete, stages=stages)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--art', type=Path, required=True)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--stage', choices=('develop', 'final', 'all'), default='all')
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--study')
    parser.add_argument('--lease-fd', type=int)
    parser.add_argument('--parent-pid', type=int)
    args = parser.parse_args()
    args.art = artifact_root(args.art)
    protocol = json.loads((args.art / 'protocol.json').read_text())

    def interrupt(signum, frame):
        raise KeyboardInterrupt(f'signal {signum}')
    signal.signal(signal.SIGTERM, interrupt)
    if args.worker:
        worker(args, protocol)
    elif args.execute:
        coordinator(args, protocol)
    else:
        print(json.dumps(dict(campaign=protocol['campaign_id'], studies=len(protocol['studies']),
            requested_schedule=protocol['scheduling'], stage=args.stage,
            final='serial fresh N=1; development recordings remain development data',
            readiness_exists=(args.art / 'readiness.json').is_file(), executed=False), indent=2))


if __name__ == '__main__':
    main()
