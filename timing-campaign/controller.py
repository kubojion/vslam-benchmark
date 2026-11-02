#!/usr/bin/python3
"""Resumable 3 + 1 lane controller for corrected CitrusFarm Rule C and the Sielinko timing test.

PLAN Update 3. One queue. Workers use the Rule C entry point (execute_attempt, commands), each in its
own systemd scope, and leave a done file, so a controller restart never touches a running job. A host
reset stops everything: state from another boot raises FAULT and nothing resumes.
"""
import csv, json, os, shutil, statistics, subprocess, sys, time
from pathlib import Path

W = Path(__file__).resolve().parents[1]; T = W/'timing-campaign'; RUN = T/'run'
STATE, STATUS, STOP, FAULT, GO, HOLD = (RUN/n for n in ('state.json', 'status.md', 'STOP', 'FAULT', 'GO', 'HOLD'))
JOBS = RUN/'jobs'
VIO = 'okvis2 okvis2x orbslam3 openvins voxel_svio svo_pro cuvslam airslam mast3r_fusion'.split()
LC = 'okvis2 okvis2x orbslam3 svo_pro cuvslam airslam mast3r_fusion'.split()
GPU = {'cuvslam', 'airslam', 'mast3r_fusion'}; SMALL = {'openvins', 'voxel_svio'}
LANES = {'cpu1': '0-2', 'cpu2': '3-5', 'cpu3': '6-7', 'gpu': '16-23'}
CPU_MEM, GPU_MEM, GPU_HIGH = 68719476736, 53687091200, 42949672960   # Rule C caps, no swap
TIMEOUT_S, MIN_FREE, MIN_DISK = 10800, 40*2**30, 100*2**30
BOOT = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
WORKER_PY = '/data/imoroz/conda/envs/cuvslam/bin/python'; EVAL_PY = '/data/imoroz/conda/envs/macvo/bin/python'
CONTAINERS = ('vslam_corrected_voxel_20261031', 'vslam_corrected_air_20261031')
Z = 'field1_110426_full_10fps_q90'
COHORT, ZCOHORT = 'timing-corrected-20261031', 'sielinko-timing-test-20261101'
ORBCOHORT, Z2COHORT = 'timing-corrected-orbslam3-4core-20261101', 'sielinko-corrected-rule-c-20261101'
FOUR_CORE = {'cpu1': '0-3', 'cpu2': '4-7'}   # Update 4, from group 3 on
REFERENCE = Path('/data/imoroz/PAPER/vslam-paper/notes/timing-test-20261030/results.csv')
REGRESSION = {'openvins', 'basalt', 'mast3r_fusion'}


def job(block, ds, seq, alg, mode, run, rep, variant, cohort):
    return dict(id=f'{block}__{mode}__{seq[:6]}__{alg}__run{run}', block=block, ds=ds, seq=seq, alg=alg, mode=mode,
                run=run, rep=rep, variant=variant, cohort=cohort)


def plan():
    citrus = lambda block, alg, mode, s, r: job(block, 'citrusfarm', s, alg, mode, 50000+r, r, 'corrected', COHORT)
    seqs = ('seq07', 'seq04')
    checks = [job('CHECK', 'citrusfarm', 'seq04', a, 'vio', 59000+i, 1, 'corrected', 'gate-check')
              for i, a in enumerate(('okvis2', 'openvins', 'cuvslam'), 1)]
    basalt = [citrus('CITRUS', 'basalt', 'vio', s, r) for r in (1, 2, 3) for s in seqs]
    main = [citrus('CITRUS', a, 'vio', s, r) for r in (1, 2, 3) for s in seqs for a in VIO]
    main += [citrus('CITRUS', a, 'vio-lc', s, r) for r in (1, 2, 3) for s in seqs for a in LC]
    z = 'airslam okvis2 okvis2x openvins orbslam3 voxel_svio svo_pro'.split()
    main += [job('SIELINKO', 'zed2i', Z, a, 'vio', 60001+i, 1, 'drift', ZCOHORT) for i, a in enumerate(z)]
    main += [job('SIELINKO', 'zed2i', Z, 'okvis2', 'vio', 60008, 1, 'unchanged', ZCOHORT)]
    # Update 4: Job 1 on 4-core lanes, then Job 2. AirSLAM stays out: it reaches the 50 GiB cap on Sielinko, and the cap must not be relaxed.
    orb = [job('ORB4', 'citrusfarm', s, 'orbslam3', m, 51000+r, r, 'corrected', ORBCOHORT) for r in (1, 2, 3) for m in ('vio', 'vio-lc') for s in seqs]
    job2 = [job('SIELINKO2', 'zed2i', Z, a, 'vio', 61000+r, r, 'drift', Z2COHORT) for r in (1, 2, 3)
            for a in 'basalt okvis2 okvis2x orbslam3 openvins voxel_svio svo_pro cuvslam mast3r_fusion'.split()]
    return [checks, basalt, main, orb, job2]


def link_variant(j):
    link = W/'datasets'/j['ds']/j['seq']/'mav0/imu0'; target = f"../../../.timing-imu/{j['ds']}__{j['seq']}/{j['variant']}"
    if link.is_symlink() and os.readlink(link) == target: return
    assert (link.parent/target/'data.csv').is_file()
    tmp = link.with_name('.imu0.tmp'); tmp.unlink(missing_ok=True); tmp.symlink_to(target); os.replace(tmp, link)


def cgroup():
    return Path('/sys/fs/cgroup')/next(x[3:] for x in Path('/proc/self/cgroup').read_text().splitlines() if x.startswith('0::')).lstrip('/')


def worker(path):
    """Runs inside the job's scope. Verifies its own limits, then the Rule C entry point."""
    j = json.loads(Path(path).read_text()); out = dict(j); key = '__'.join((j['mode'], j['ds'], j['seq'], j['alg']))
    run = W/'results'/j['mode']/j['ds']/j['seq']/j['alg']/f"run{j['run']}"
    imu = W/'datasets'/j['ds']/j['seq']/'mav0/imu0'; before = os.readlink(imu); t0 = time.time()
    try:
        c = cgroup(); limits = {n: (c/n).read_text().strip() for n in ('memory.max', 'memory.swap.max')}
        if limits != {'memory.max': str(j['mem']), 'memory.swap.max': '0'}: raise RuntimeError(f'safety: scope limits {limits}')
        sys.path[:0] = [str(W/'scripts/campaign'), str(W/'scripts/results')]
        from run_repetitions import commands, execute_attempt
        cmd = commands(W, j['ds'], j['seq'], j['alg'], j['run'], j['mode'])
        cmd['runner'] = ['timeout', '--signal=TERM', '--kill-after=120', str(TIMEOUT_S)]+cmd['runner']
        result = execute_attempt(run, W/'results/.attempt-state'/key/f"run{j['run']}.json", **cmd,
                                 identity=dict(cohort=j['cohort'], repetition=j['rep'], physical_run_id=j['run'], input_variant=j['variant']))
        out.update(attempt_status=result.get('status'), estimator_exit_code=result.get('estimator_exit_code'))
        out['timed_out'] = result.get('estimator_exit_code') in (124, 137)
    except Exception as exc:   # infrastructure by definition: the worker itself failed
        out['infra'] = f'{type(exc).__name__}: {exc}'[:300]
    if out.get('timed_out'):
        names = subprocess.run(['docker', 'ps', '--format', '{{.Names}}', '--filter', f"name=vslam_{j['alg']}_{j['ds']}_{j['seq']}_{j['run']}_"],
                               capture_output=True, text=True).stdout.split()
        for n in names: subprocess.run(['docker', 'stop', '--time', '30', n], timeout=60)
    out['duration_s'] = time.time()-t0
    meta = run/'run_meta.json'; out['run_meta'] = meta.is_file()
    if meta.is_file():
        process = json.loads(meta.read_text()).get('process', {})
        out['process_exit_code'] = process.get('exit_code'); out['failure_reason'] = process.get('failure_reason')
    if (run/'run_eval.json').is_file():
        doc = json.loads((run/'run_eval.json').read_text()); out['run_status'] = doc.get('run_status')
        out['ate_m'] = (doc.get('ate' if doc.get('primary_alignment') == 'sim3' else 'ate_se3') or {}).get('rmse')
        out['scale'] = doc.get('scale_factor')
    try:
        events = dict(l.split() for l in (cgroup()/'memory.events').read_text().splitlines()); out['oom_kill'] = int(events.get('oom_kill', 0))
    except OSError:
        out['oom_kill'] = None
    if before != os.readlink(imu) or not before.endswith('/'+j['variant']): out['infra'] = 'imu variant changed under the run'
    elif not out.get('infra') and not out['run_meta']: out['infra'] = 'no run_meta: failed before the estimator could record a result'
    # Voxel-SVIO after a full recording: the runner stops the node, and a diverged node answers 143. A result, not a crash.
    stopped = out.get('process_exit_code') == 143 and str(out.get('failure_reason', '')).startswith('player_exit=0') and out.get('run_status')
    if stopped: out['stopped_at_end'] = True
    if not stopped and not out.get('infra') and not out.get('timed_out') and (out.get('process_exit_code') or out.get('estimator_exit_code')):
        out['crash'] = f"estimator exit {out.get('estimator_exit_code')}, recorded {out.get('process_exit_code')}"
    tmp = JOBS/(j['id']+'.done.tmp'); tmp.write_text(json.dumps(out, indent=1)); os.replace(tmp, JOBS/(j['id']+'.done'))


def active(unit):
    return subprocess.run(['systemctl', '--user', 'is-active', '--quiet', unit+'.scope']).returncode == 0


def launch(j):
    unit = ('vslam-corrected-'+j['id']).replace('__', '-').replace('_', '-').lower()
    subprocess.run(['systemctl', '--user', 'reset-failed', unit+'.scope'], stderr=subprocess.DEVNULL)
    (JOBS/(j['id']+'.json')).write_text(json.dumps(j))
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', BENCHMARK_EVAL_PYTHON=EVAL_PY, TIMING_CPUS=j['cpus'], TIMING_MEM=str(j['mem']),
               PYTHONDONTWRITEBYTECODE='1', CUVSLAM_CONDA_ENV='/data/imoroz/conda/envs/cuvslam',
               MAST3R_FUSION_CONDA_ENV='/data/imoroz/conda/envs/mast3r_fusion')
    high = ['-p', f'MemoryHigh={GPU_HIGH}'] if j['lane'] == 'gpu' else []
    log = open(JOBS/(j['id']+'.log'), 'a')
    subprocess.Popen(['systemd-run', '--user', '--scope', '--quiet', '--unit='+unit, '-p', f"MemoryMax={j['mem']}", '-p', 'MemorySwapMax=0', *high,
                      'taskset', '-c', j['cpus'], WORKER_PY, str(T/'controller.py'), '--worker', str(JOBS/(j['id']+'.json'))],
                     cwd=W, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    return unit


def available():
    return int(next(l.split()[1] for l in open('/proc/meminfo') if l.startswith('MemAvailable')))*1024


def gpu_free():
    q = subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'], capture_output=True, text=True)
    return q.returncode == 0 and int(q.stdout.split()[0]) < 1024


def references():
    rows = [r for r in csv.DictReader(REFERENCE.open()) if r['block'] == 'B' and r['alg'] in REGRESSION and r['status'] == 'ok']
    keys = {(r['seq'], r['alg']) for r in rows}
    return {k: statistics.median(float(r['ate']) for r in rows if (r['seq'], r['alg']) == k) for k in keys}


def regression(d, refs):
    """Update 3: OpenVINS, Basalt or MASt3R-Fusion more than 10 % from the timing test means 3 + 1 changed results."""
    ref = refs.get((d['seq'], d['alg']))
    if d['mode'] != 'vio' or d['block'] != 'CITRUS' or ref is None: return None
    if d.get('run_status') != 'ok' or d.get('ate_m') is None: return f"{d['id']}: status {d.get('run_status')}, timing test was ok"
    if abs(d['ate_m']/ref-1) > .10: return f"{d['id']}: ATE {d['ate_m']:.3f} against timing test {ref:.3f}"
    return None


def save(s):
    tmp = STATE.with_suffix('.tmp'); tmp.write_text(json.dumps(s, indent=1)); os.replace(tmp, STATE)


def status(s, note, total):
    done = s['done']; per = {}
    for v in done.values(): per[v['block']] = per.get(v['block'], 0)+1
    tmp = STATUS.with_suffix('.tmp')
    tmp.write_text('\n'.join((f"# corrected timing campaign {time.strftime('%F %T %Z')}", f"group {s['group']} {note}",
                              f"finished {len(done)}, planned {total} plus replacements; per block {per}",
                              f"running {[r['id'] for r in s['running'].values()]}",
                              f"infrastructure {[k for k, v in done.items() if v.get('infra')]}",
                              f"crashes {[k for k, v in done.items() if v.get('crash')]}"))+'\n')
    os.replace(tmp, STATUS)


def fault(reason):
    if not FAULT.exists(): FAULT.write_text(reason+'\n')


def main():
    JOBS.mkdir(parents=True, exist_ok=True)
    s = json.loads(STATE.read_text()) if STATE.exists() else dict(boot=BOOT, group=0, done={}, running={}, infra_streak=0, replacements=[])
    if s['boot'] != BOOT:
        fault('host reset: nothing resumes'); status(s, 'FAULT: host reset', 0); return 0
    groups = plan(); total = sum(len(g) for g in groups); refs = references()
    while True:
        changed = False
        for lane, r in list(s['running'].items()):
            done = JOBS/(r['id']+'.done')
            if done.exists(): d = json.loads(done.read_text())
            elif active(r['unit']) or time.time()-r['started'] < 15: continue
            else: d = dict(r, infra='scope gone without a result')
            del s['running'][lane]; changed = True
            d['counted'] = True
            if d.get('oom_kill'): fault(f"safety: oom_kill in {d['id']}")
            if d.get('process_exit_code') == 137: fault(f"safety: exit 137, memory kill likely, in {d['id']}")
            if str(d.get('infra', '')).startswith('safety'): fault(d['infra'])
            kind = 'infra' if d.get('infra') else 'crash' if d.get('crash') else None
            replaceable = kind and not r.get('replacement') and r['block'] != 'CHECK'
            s['infra_streak'] = s['infra_streak']+1 if kind == 'infra' else 0
            if replaceable:
                offset = 100 if kind == 'infra' else 200
                new = dict({k: r[k] for k in ('block', 'ds', 'seq', 'alg', 'mode', 'rep', 'variant', 'cohort')}, run=r['run']+offset,
                           id=r['id']+f'_rep{kind}', replacement=r['id'], reason=d[kind])
                s['replacements'].append(new); d['replaced_by'] = new['id']; d['counted'] = False
            s['done'][d['id']] = d
            problem = regression(d, refs)
            if problem: fault('regression: '+problem)
            save(s)
        if (RUN/'inject.json').exists():   # repaired jobs, controller plumbing only
            s['replacements'].extend(json.loads((RUN/'inject.json').read_text())); s['infra_streak'] = 0; save(s)
            os.replace(RUN/'inject.json', RUN/f'inject.applied.{int(time.time())}.json')
        if s['infra_streak'] >= 3: fault('three infrastructure failures in a row')
        if HOLD.exists():
            status(s, 'HOLD', total); time.sleep(20); continue
        stopping = STOP.exists() or FAULT.exists()
        group = groups[s['group']] if s['group'] < len(groups) else []
        running = [r['id'] for r in s['running'].values()]
        pending = [j for j in group+s['replacements'] if j['id'] not in s['done'] and j['id'] not in running]
        if s['group'] >= len(groups) and not s['running'] and not pending:
            status(s, 'FINISHED', total); return 0
        if stopping and not s['running']:
            status(s, 'FAULT: '+FAULT.read_text().strip() if FAULT.exists() else 'STOP', total); time.sleep(30)
            if STOP.exists() or FAULT.exists(): return 0
            continue
        if not pending and not s['running'] and not stopping:
            if s['group'] == 0 and not GO.exists():
                status(s, 'HOLD: gates under review', total); time.sleep(20); continue
            if s['group'] == 3 and not (RUN/'GO2').exists():
                status(s, 'HOLD: Job 2 conditions under review', total); time.sleep(20); continue
            s['group'] += 1; save(s); continue
        note = 'stopping' if stopping else ''
        if pending and not stopping:
            for name in CONTAINERS:
                if subprocess.run(['docker', 'inspect', '-f', '{{.State.Running}}', name], capture_output=True, text=True).stdout.strip() != 'true':
                    fault('private container down: '+name)
            if shutil.disk_usage(W).free < MIN_DISK: fault('less than 100 GiB disk free')
            if available() < MIN_FREE: note = f'launch held: {available()/2**30:.0f} GiB available'
            elif not FAULT.exists():
                busy = {r['alg'] for r in s['running'].values()}
                for j in pending:
                    if available() < MIN_FREE or 'basalt' in busy: break
                    if j['alg'] == 'basalt':
                        if s['running']: continue
                        lane, cpus = 'cpu1', '0-7'
                    else:
                        if j['alg'] in busy and j['alg'] != 'orbslam3': continue   # shared container and native output names; ORB-SLAM3 works in its run folder
                        if s['group'] >= 3:
                            lanes = ['gpu'] if j['alg'] in GPU else ['cpu2'] if j['alg'] == 'voxel_svio' else ['cpu1', 'cpu2']
                        else:
                            lanes = ['gpu'] if j['alg'] in GPU else ['cpu3'] if j['alg'] in SMALL else ['cpu1', 'cpu2']
                        free = [l for l in lanes if l not in s['running']]
                        if not free: continue
                        lane, cpus = free[0], (FOUR_CORE if s['group'] >= 3 else LANES).get(free[0], LANES[free[0]])
                        if lane == 'gpu' and not s['running'].get('gpu') and not gpu_free():
                            note = 'GPU in use by another process; lane held'; continue
                    if any(r['seq'] == j['seq'] and r['variant'] != j['variant'] for r in s['running'].values()): continue
                    link_variant(j)
                    j = dict(j, lane=lane, cpus=cpus, mem=GPU_MEM if lane == 'gpu' else CPU_MEM, started=time.time())
                    j['unit'] = launch(j); s['running'][lane] = j; busy.add(j['alg']); save(s); changed = True
                    time.sleep(5)
                    if j['alg'] == 'basalt': break
        status(s, note, total)
        time.sleep(5 if changed else 20)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        worker(sys.argv[2])
    else:
        sys.exit(main())
