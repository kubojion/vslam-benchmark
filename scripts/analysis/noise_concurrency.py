#!/usr/bin/env python3
"""Validate workload concurrency with independent attempt records and a parent lease.

The coordinator exclusively holds both the search-controller lock and production
execution lock. Children inherit the execution lock descriptor, so it remains
held until every worker has exited, even if the coordinator unexpectedly dies.
"""
from contextlib import contextmanager
import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import statistics
import subprocess
import sys
import time

import noise_reliable as search

ENGINE = search.engine
FOLLOWUP = search.ART
ART = FOLLOWUP.parent/'noise-concurrency-20261009'
LOCK = ENGINE.MAIN/'results/.locks/execution.lock'


@contextmanager
def leased_slot(fd, parent_pid):
    """Only replace the per-attempt lock with a verified, inherited parent lock."""
    a, b = os.fstat(fd), LOCK.stat()
    if (a.st_dev, a.st_ino) != (b.st_dev, b.st_ino):
        raise RuntimeError('Worker lease is not the production execution lock')
    if os.getppid() != parent_pid:
        raise RuntimeError('Coordinator no longer owns this worker')
    with LOCK.open('rb') as independent:
        try:
            fcntl.flock(independent, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            pass
        else:
            raise RuntimeError('Coordinator execution lock is not held')
    if ENGINE.production_processes():
        raise RuntimeError('Production process active during exclusive experiment')
    yield


def configure_worker(art, fd, parent_pid):
    search.ART = art
    ENGINE.ART = art
    ENGINE.machine_slot = lambda: leased_slot(fd, parent_pid)
    ENGINE.render_report = search.render_report


def worker(args):
    job = json.loads(Path(args.job).read_text())
    art = Path(job['art'])
    configure_worker(art, args.lease_fd, args.parent_pid)
    # Native wrapper children already handle their own process groups on error.
    def interrupt(signum, frame):
        raise KeyboardInterrupt(f'signal {signum}')
    signal.signal(signal.SIGTERM, interrupt)
    ENGINE.run_attempt(job['spec'], 'concurrency_probe', job['params'],
        job['sequence'], 'vio', job['repetition'], 'concurrency_'+job['condition'])


def protocol():
    source = json.loads(search.PROTOCOL.read_text())
    by_id = {s['id']:s for s in source['studies']}
    cases = []
    for name, choice in [('orbslam3_rosariov2','pilot'),
                         ('voxel_svio_citrusfarm','legacy'),
                         ('airslam_citrusfarm','pilot')]:
        spec = by_id[name]
        params = spec['legacy'] if choice=='legacy' else spec['pilot_candidates'][0]['params']
        cases.append(dict(spec=spec, params=params, sequence=spec['clips'][0]))
    return dict(schema=1, frozen_before_execution=True, repetitions=3,
        conditions=['serial','parallel'], cases=cases,
        order='serial then concurrent in each of three rounds; same three cases each round',
        acceptance=dict(all_attempts_pass=True, minimum_batch_speedup=1.3,
            median_rmse_relative_tolerance=.10, median_rmse_absolute_tolerance_m=.02,
            maximum_rmse_above_serial_max_uses_same_tolerance=True,
            minimum_support_drop_allowed=.005, voxel_input_receipt_equal=True),
        limitations=['Small diagnostic comparison, not statistical equivalence proof.',
            'Only one job per algorithm/container; at most one GPU estimator.',
            'Does not validate concurrent loop-closure optimization.',
            'Concurrent timing/resource measurements are excluded from benchmark performance tables.',
            'Validation observations never enter noise candidate selection.'],
        search_protocol_sha256=ENGINE.sha(search.PROTOCOL))


def prepare():
    ART.mkdir(exist_ok=True)
    target = ART/'protocol.json'
    proposed = protocol()
    if target.exists():
        if json.loads(target.read_text()) != proposed:
            raise RuntimeError('Concurrency protocol changed after freezing')
    else:
        ENGINE.write(target, proposed)
    return proposed


def launch(job, lease):
    art = Path(job['art'])
    art.mkdir(parents=True, exist_ok=True)
    before = art/'main-before.json'
    if not before.exists():
        before.write_bytes((FOLLOWUP/'main-before.json').read_bytes())
    name = job['condition']+f"-{job['repetition']}"
    jobfile = art/(name+'.job.json')
    ENGINE.write(jobfile, job)
    log = (art/(name+'.controller.log')).open('ab')
    p = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--worker',
        '--job',str(jobfile),'--lease-fd',str(lease.fileno()),'--parent-pid',str(os.getpid())],
        cwd=search.ROOT, pass_fds=(lease.fileno(),), stdout=log, stderr=subprocess.STDOUT)
    log.close()
    return p


def receipt(record):
    path = Path(record['run'])/'native/input_receipt.json'
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return {k:data[k] for k in ('imu_received','stereo_received','stereo_queued_after_rate_gate')}


def assess(records, batches, spec):
    checks = spec['acceptance']
    comparisons = []
    passed = True
    for case in spec['cases']:
        study = case['spec']['id']
        rows = [r for r in records if r['study']==study]
        serial = [r for r in rows if r['phase']=='concurrency_serial']
        parallel = [r for r in rows if r['phase']=='concurrency_parallel']
        if len(serial)!=spec['repetitions'] or len(parallel)!=spec['repetitions']:
            raise RuntimeError('Incomplete comparison: '+study)
        all_ok = all(r['state']=='finished' and not r['result']['failed'] and
            not r['timeout'] and r['returncode']==0 for r in rows)
        s = [r['result']['ate_se3_rmse_m'] for r in serial]
        p = [r['result']['ate_se3_rmse_m'] for r in parallel]
        valid_errors = all(isinstance(x,(int,float)) and __import__('math').isfinite(x) for x in s+p)
        tolerance = max(checks['median_rmse_absolute_tolerance_m'],
                        checks['median_rmse_relative_tolerance']*statistics.median(s)) if valid_errors else None
        median_ok = valid_errors and abs(statistics.median(p)-statistics.median(s)) <= tolerance
        tail_ok = valid_errors and max(p) <= max(s)+tolerance
        support_drop = min(r['result']['export_support_fraction'] for r in serial)-min(
            r['result']['export_support_fraction'] for r in parallel)
        support_ok = support_drop <= checks['minimum_support_drop_allowed']
        receipt_ok = True
        receipts = [receipt(r) for r in rows]
        if case['spec']['algorithm']=='voxel_svio':
            receipt_ok = all(x is not None and x==receipts[0] for x in receipts)
        ok = all_ok and median_ok and tail_ok and support_ok and receipt_ok
        passed &= ok
        comparisons.append(dict(study=study,passed=ok,all_attempts_pass=all_ok,
            serial_rmse_m=s,parallel_rmse_m=p,rmse_tolerance_m=tolerance,
            median_ok=median_ok,tail_ok=tail_ok,support_drop=support_drop,
            support_ok=support_ok,input_receipt_equal=receipt_ok,input_receipts=receipts,
            serial_wall_s=[r['wall_s'] for r in serial],parallel_wall_s=[r['wall_s'] for r in parallel]))
    serial_s = sum(b['wall_s'] for b in batches if b['condition']=='serial')
    parallel_s = sum(b['wall_s'] for b in batches if b['condition']=='parallel')
    speedup = serial_s/parallel_s
    passed &= speedup >= checks['minimum_batch_speedup']
    return dict(checked=ENGINE.now(),passed=bool(passed),serial_batch_s=serial_s,
        parallel_batch_s=parallel_s,speedup=speedup,comparisons=comparisons,
        interpretation='Predeclared practical diagnostic only; no universal or bitwise equivalence claim.')


def coordinator():
    spec = prepare()
    batches = []
    with (FOLLOWUP/'controller.lock').open('a') as controller, LOCK.open('rb') as lease:
        fcntl.flock(controller, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if ENGINE.production_processes():
            raise RuntimeError('Production processes still active')
        ENGINE.verify_main()
        for repetition in range(1, spec['repetitions']+1):
            for condition in spec['conditions']:
                if (ART/'STOP_AFTER_CURRENT').exists():
                    raise InterruptedError('Concurrency stop requested')
                batchfile = ART/f'batch-{repetition}-{condition}.json'
                if batchfile.exists():
                    batches.append(json.loads(batchfile.read_text()))
                    continue
                ENGINE.write(ART/'status.json',dict(time=ENGINE.now(),event='batch_started',
                    repetition=repetition,condition=condition))
                started = time.monotonic()
                active = []
                try:
                    for case in spec['cases']:
                        job = dict(case,art=str(ART/'workers'/case['spec']['id']),
                                   condition=condition,repetition=repetition)
                        p = launch(job,lease)
                        active.append(p)
                        if condition=='serial' and p.wait()!=0:
                            raise RuntimeError('Validation worker failed; inspect its controller log')
                    codes = [p.wait() for p in active]
                    if any(codes):
                        raise RuntimeError('Validation worker failed: '+str(codes))
                except BaseException:
                    for p in active:
                        if p.poll() is None:
                            p.terminate()
                    for p in active:
                        p.wait()
                    raise
                batch = dict(repetition=repetition,condition=condition,
                             wall_s=time.monotonic()-started,finished=ENGINE.now())
                ENGINE.write(batchfile,batch)
                batches.append(batch)
        records = [json.loads(p.read_text()) for p in (ART/'workers').glob('*/attempts/*.json')]
        result = assess(records,batches,spec)
        ENGINE.write(ART/'assessment.json',result)
        ENGINE.verify_main()
        ENGINE.write(ART/'status.json',dict(time=ENGINE.now(),event='validation_finished',
                                         passed=result['passed'],speedup=result['speedup']))
        print(json.dumps(result,indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--worker',action='store_true')
    parser.add_argument('--job')
    parser.add_argument('--lease-fd',type=int)
    parser.add_argument('--parent-pid',type=int)
    args=parser.parse_args()
    if args.worker:
        worker(args)
    elif args.execute:
        coordinator()
    else:
        print(json.dumps(protocol(),indent=2))


if __name__=='__main__':
    main()
