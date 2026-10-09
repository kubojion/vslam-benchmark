#!/usr/bin/env python3
"""Run independent noise studies in three validated algorithm lanes.

Each optimizer retains serial ask/tell ordering. Global screen/full/repeat/LC
barriers are retained. LC diagnostics run serially because the concurrency probe
does not cover map refinement. The original deadline and protocol are unchanged.
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

import noise_concurrency as concurrency
import noise_reliable as search

ENGINE = search.engine
ART = concurrency.FOLLOWUP
PARALLEL = ART/'parallel'
STAGES = ('screen','full-search','repeat','lc')


def lanes(protocol):
    result = {}
    for spec in protocol['studies']:
        result.setdefault(spec['algorithm'],[]).append(spec['id'])
    if len(result)>3 or set(result)-{'orbslam3','voxel_svio','airslam'}:
        raise RuntimeError('Unvalidated lane layout')
    return result


def immutable_or_advance(target, value):
    """Finished observations are immutable; only running -> finished may advance."""
    if target.exists():
        previous = json.loads(target.read_text())
        if previous==value:
            return
        if previous.get('state')=='finished':
            # run_attempt commits the measurement before attempt() appends its
            # deterministic solver-warning count. Collection may observe either
            # version. Accept only that one added field; never change a measured
            # value, identity, timestamp, parameter, or existing annotation.
            annotated = ('solver_warnings' not in previous and
                'solver_warnings' in value and
                {k:v for k,v in value.items() if k!='solver_warnings'}==previous)
            if not annotated:
                raise RuntimeError('Refusing to replace a finished observation: '+str(target))
        if previous.get('key')!=value.get('key') or previous.get('run')!=value.get('run'):
            raise RuntimeError('Observation identity changed: '+str(target))
    ENGINE.write(target,value)


def prepare_lane(algorithm, study_ids):
    destination = PARALLEL/'workers'/algorithm
    destination.mkdir(parents=True,exist_ok=True)
    before = destination/'main-before.json'
    if before.exists() and before.read_bytes()!=(ART/'main-before.json').read_bytes():
        raise RuntimeError('Main baseline differs in lane '+algorithm)
    if not before.exists():
        before.write_bytes((ART/'main-before.json').read_bytes())
    # Existing completed observations are reused by exact identity. Output data
    # and wrapper logs remain at their original immutable physical paths.
    for p in (ART/'attempts').glob('*.json'):
        r=json.loads(p.read_text())
        if r['study'] in study_ids:
            if r['state']!='finished':
                raise RuntimeError('Unfinished attempt needs explicit review: '+r['key'])
            target=destination/'attempts'/p.name
            if not target.exists():
                ENGINE.write(target,r)
            elif json.loads(target.read_text())!=r:
                raise RuntimeError('Lane cache disagrees with original observation: '+r['key'])
    for study in study_ids:
        for p in (ART/'studies'/study).rglob('*.json'):
            target=destination/'studies'/study/p.relative_to(ART/'studies'/study)
            if not target.exists():
                ENGINE.write(target,json.loads(p.read_text()))
            elif json.loads(target.read_text())!=json.loads(p.read_text()):
                raise RuntimeError('Existing optimizer state differs: '+str(p))
    return destination


def collect(lane_dirs):
    statuses={}
    for algorithm,directory in lane_dirs.items():
        for p in (directory/'attempts').glob('*.json'):
            immutable_or_advance(ART/'attempts'/p.name,json.loads(p.read_text()))
        for p in (directory/'studies').rglob('*.json'):
            target=ART/'studies'/p.relative_to(directory/'studies')
            incoming=json.loads(p.read_text())
            if target.exists() and json.loads(target.read_text())==incoming:
                continue
            if target.name=='selection.json' and target.exists():
                raise RuntimeError('Frozen selection differs during collection')
            ENGINE.write(target,incoming)
        if (directory/'status.json').exists():
            statuses[algorithm]=json.loads((directory/'status.json').read_text())
    return statuses


def lane_worker(args):
    protocol=json.loads(search.PROTOCOL.read_text())
    directory=PARALLEL/'workers'/args.algorithm
    concurrency.configure_worker(directory,args.lease_fd,args.parent_pid)
    search.DEADLINE=json.loads((ART/'budget.json').read_text())['deadline_unix']

    @contextmanager
    def slot():
        if (ART/'STOP_AFTER_CURRENT').exists():
            raise InterruptedError('Coordinator requested stop after current attempt')
        with concurrency.leased_slot(args.lease_fd,args.parent_pid):
            yield
    ENGINE.machine_slot=slot

    def interrupt(signum,frame):
        raise KeyboardInterrupt(f'signal {signum}')
    signal.signal(signal.SIGTERM,interrupt)
    result=dict(algorithm=args.algorithm,stage=args.stage,started=ENGINE.now())
    try:
        for spec in protocol['studies']:
            if spec['algorithm']!=args.algorithm:
                continue
            screens=search.screening(spec,protocol)
            if args.stage=='screen':
                continue
            full=search.full_search(spec,protocol,screens)
            if args.stage=='full-search':
                continue
            selected=search.repeated_selection(spec,protocol,full)
            if args.stage=='lc':
                search.lc_checks(spec,selected)
        result.update(complete=True,finished=ENGINE.now())
    except (search.BudgetFinished,InterruptedError) as exc:
        result.update(complete=False,finished=ENGINE.now(),reason=f'{type(exc).__name__}: {exc}')
    except BaseException as exc:
        result.update(complete=False,finished=ENGINE.now(),reason=f'{type(exc).__name__}: {exc}')
        raise
    finally:
        ENGINE.write(directory/(args.stage+'-completion.json'),result)
        ENGINE.event('lane_stage_finished',**result)


def launch(algorithm,stage,lease):
    directory=PARALLEL/'workers'/algorithm
    log=(directory/(stage+'.controller.log')).open('ab')
    p=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',
        '--algorithm',algorithm,'--stage',stage,'--lease-fd',str(lease.fileno()),
        '--parent-pid',str(os.getpid())],cwd=search.ROOT,
        pass_fds=(lease.fileno(),),stdout=log,stderr=subprocess.STDOUT)
    log.close()
    return p


def stage_batch(algorithms,stage,lease,lane_dirs,protocol):
    workers={algorithm:launch(algorithm,stage,lease) for algorithm in algorithms}
    last=None
    try:
        while True:
            statuses=collect(lane_dirs)
            encoded=json.dumps(statuses,sort_keys=True)
            if encoded!=last:
                ENGINE.write(ART/'status.json',dict(time=ENGINE.now(),event='parallel_progress',
                    stage=stage,lanes=statuses))
                search.render_report(protocol)
                last=encoded
            failed=[name for name,p in workers.items() if p.poll() not in (None,0)]
            if failed and not (ART/'STOP_AFTER_CURRENT').exists():
                (ART/'STOP_AFTER_CURRENT').write_text('Worker infrastructure failure: '+str(failed)+'\n')
            if all(p.poll() is not None for p in workers.values()):
                break
            time.sleep(10)
    except BaseException:
        for p in workers.values():
            if p.poll() is None:
                p.terminate()
        for p in workers.values():
            p.wait()
        collect(lane_dirs)
        raise
    collect(lane_dirs)
    results={a:json.loads((lane_dirs[a]/(stage+'-completion.json')).read_text()) for a in algorithms}
    if any(p.returncode!=0 for p in workers.values()):
        raise RuntimeError('Worker infrastructure failure; remaining workers stopped at an attempt boundary')
    return all(r['complete'] for r in results.values())


def coordinator():
    if (ART/'STOP_AFTER_CURRENT').exists():
        raise RuntimeError('Remove the reviewed stop request explicitly before resuming')
    assessment=json.loads((concurrency.ART/'assessment.json').read_text())
    if not assessment['passed']:
        raise RuntimeError('Concurrency validation did not pass; retain serial scheduling')
    protocol=json.loads(search.PROTOCOL.read_text())
    if search.PROTOCOL.read_bytes()!=(ART/'protocol.json').read_bytes():
        raise RuntimeError('Frozen scientific protocol changed')
    layout=lanes(protocol)
    PARALLEL.mkdir(exist_ok=True)
    with (ART/'controller.lock').open('a') as controller, concurrency.LOCK.open('rb') as lease:
        fcntl.flock(controller,fcntl.LOCK_EX|fcntl.LOCK_NB)
        fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if ENGINE.production_processes():
            raise RuntimeError('Production process active')
        ENGINE.verify_main()
        lane_dirs={a:prepare_lane(a,ids) for a,ids in layout.items()}
        amendment=PARALLEL/'scheduling-amendment.json'
        if not amendment.exists():
            ENGINE.write(amendment,dict(created=ENGINE.now(),lanes=layout,
                acceptance_source=str(concurrency.ART/'assessment.json'),
                acceptance_sha256=ENGINE.sha(concurrency.ART/'assessment.json'),
                scientific_protocol_sha256=ENGINE.sha(search.PROTOCOL),
                budget=json.loads((ART/'budget.json').read_text()),
                behavior='Parallel independent studies; serial proposal order within each study; original stage barriers; LC serial.',
                limitations='Small concurrency validation does not prove equivalence for all candidate configurations. Keep coverage checks and exclude concurrent runtime from benchmark tables.'))
        ENGINE.event('parallel_controller_started',lanes=layout,deadline=json.loads((ART/'budget.json').read_text())['deadline_unix'])
        complete=True
        for stage in STAGES:
            done=PARALLEL/(stage+'-complete.json')
            if done.exists():
                continue
            if stage=='lc':
                # No concurrent LC claim: run supported algorithms in isolation.
                for algorithm in layout:
                    if not stage_batch([algorithm],stage,lease,lane_dirs,protocol):
                        complete=False
                        break
            else:
                complete=stage_batch(list(layout),stage,lease,lane_dirs,protocol)
            if not complete:
                break
            ENGINE.write(done,dict(complete=True,finished=ENGINE.now()))
            ENGINE.verify_main()
        search.render_report(protocol)
        ENGINE.verify_main()
        ENGINE.event('parallel_controller_finished',complete=complete)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--worker',action='store_true')
    parser.add_argument('--algorithm')
    parser.add_argument('--stage',choices=STAGES)
    parser.add_argument('--lease-fd',type=int)
    parser.add_argument('--parent-pid',type=int)
    args=parser.parse_args()
    if args.worker:
        lane_worker(args)
    elif args.execute:
        coordinator()
    else:
        print(json.dumps(dict(lanes=lanes(json.loads(search.PROTOCOL.read_text())),
            stages=STAGES,loop_closure='serial',activation='Requires passed concurrency assessment'),indent=2))


if __name__=='__main__':
    main()
