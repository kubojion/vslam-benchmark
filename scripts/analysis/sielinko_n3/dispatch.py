#!/usr/bin/env python3
"""Manifest-driven dispatcher for the Sielinko N=3 repetitions (Update 10 B, C, D search).

Dry run (default) prints, for each item, the exact command, environment, scope settings, launch
checks and identity-gate checks. It starts nothing:
  python -B dispatch.py --manifest M (--item ID ... | --all) [--probe]
--probe additionally runs the read-only parts of the identity gate now (HEAD, pinned evidence,
config bytes, container inspect, frozen implementation and runtime verifiers; not the inputs).

Execution runs exactly one item per invocation and only with the reviewed manifest hash:
  python -B dispatch.py --manifest M --item ID --execute --manifest-sha256 H
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack, contextmanager
import fcntl
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import threading
import time

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = 'sielinko_n3'

from . import guard, identity
from .common import GIB, OUT, boot_id, load, now, sha, verify_manifest, write_json

HERE = Path(__file__).resolve().parent
INFRA = 'infrastructure'


def item_env(item, base=None):
    """The wrapper environment, built as noise_campaign_engine.run_attempt builds it."""
    env = dict(os.environ if base is None else base)
    for name in item['environment']['removed']:
        env.pop(name, None)
    env.update(item['environment']['set'])
    for name, prefix in item['environment']['prepend'].items():
        env[name] = prefix + ':' + env.get(name, '')
    return env


def out_dir(manifest):
    return Path(manifest['budget']['file']).parent


def select(manifest, ids, everything):
    items = manifest['items']
    if everything:
        return items
    by_id = {i['id']: i for i in items}
    missing = [i for i in ids if i not in by_id]
    if missing:
        raise SystemExit('Unknown item(s): ' + ', '.join(missing))
    return [by_id[i] for i in ids]


# ---------------------------------------------------------------- static launch checks

def static_refusals(manifest, item, *, boot=None, clock=time.time):
    """Refusals that need no host snapshot: stops, boot, budget, existing outputs, records."""
    reasons = []
    boot = boot_id() if boot is None else boot
    if boot != manifest['boot_id']:
        reasons.append('host restarted since the manifest was frozen (boot ' + boot + '); the user decides after a reset')
    for path in manifest['stops']['stop_files'] + manifest['stops']['fault_files']:
        if Path(path).exists():
            reasons.append('stop/fault file present: ' + path)
    if Path(item['run_dir']).exists():
        reasons.append('run directory already exists; never retried in place: ' + item['run_dir'])
    if Path(item['record']).exists():
        reasons.append('attempt record already exists: ' + item['record'])
    budget = Path(manifest['budget']['file'])
    if budget.is_file():
        value = load(budget)
        if value['deadline_unix'] - value['started_unix'] != manifest['budget']['hours'] * 3600:
            reasons.append('budget file differs from the manifest budget')
        if clock() + item['timeout_s'] + 120 > value['deadline_unix']:
            reasons.append('insufficient budget for this attempt plus cleanup')
    return reasons


def consecutive_infrastructure_failures(manifest):
    records = []
    for path in (out_dir(manifest) / 'attempts').glob('*.json'):
        value = load(path)
        if value.get('state') in ('finished', 'fault'):
            records.append(value)
    records.sort(key=lambda r: r.get('finished') or '')
    count = 0
    for record in reversed(records):
        if record.get('classification') != INFRA:
            break
        count += 1
    return count


# ---------------------------------------------------------------- dry run

def gate_plan(item):
    plan = ['worktree HEAD == ' + item['worktree']['commit'] + ' (git rev-parse HEAD in ' + item['worktree']['path'] + ')',
            'reference implementation.json workspace commit == manifest commit']
    plan += ['sha256 unchanged: ' + e['role'] + ' ' + e['path'] for e in item['pinned_evidence']]
    plan += ['config source sha256: ' + s['path'] + ' ' + s['sha256'] for s in item['config']['sources']]
    if item['config']['mode'] == 'reuse':
        plan += ['parameter/config file sha256: ' + f['path'] + ' ' + f['sha256'] for f in item['config']['files']]
    else:
        plan += ['materialize with frozen noise_adapters.prepare() -> ' + item['config']['destination']
                 + '; receipt must equal expected_receipt; files: ' + ', '.join(f['sha256'][:16] for f in item['config']['files'])]
    if item['container']:
        c = item['container']
        plan.append('docker inspect ' + c['name'] + ' == recorded identity (' + c['identity_source'] + '): Id '
                    + c['identity']['Id'][:12] + ', image ' + c['identity']['Image'][:19] + ', cpuset ' + str(c['identity']['CpusetCpus'])
                    + ', memory ' + str(c['identity']['Memory']) + ', swap ' + str(c['identity']['MemorySwap'])
                    + ', ' + str(len(c['identity']['Mounts'])) + ' mounts, gpu ' + str(c['identity']['gpu'])
                    + '; missing -> refuse (never created); stopped -> docker start, then cgroup memory.max, memory.swap.max=0, cpuset')
    fi = item['frozen_identity']
    plan += ['[first run of system this boot] frozen _capture_implementation.verify_capture(check_live) vs '
             + item['reference']['provenance']['implementation']['path'] + '; trees digest == ' + fi['implementation'],
             '[first run of system this boot] frozen _capture_runtime.verify_identity(check_live) vs runtime-assets.json; digest == ' + fi['runtime'],
             '[first run of system this boot] frozen _capture_inputs.verify_identity(check_live) vs inputs.json; digest == ' + fi['inputs'],
             '[first run of system this boot] evaluator ' + item['evaluator']['python'] + ' == '
             + item['evaluator']['controller_environment']['python'].split()[0] + ' with numpy/scipy/optuna/PyYAML '
             + json.dumps(item['evaluator']['controller_environment']['package_versions'])]
    return plan


def launch_plan(manifest, item):
    p, a = manifest['launch_policy'], item['admission']
    plan = [f"MemAvailable >= {p['min_available_gib']} GiB", f"free disk on worktree >= {p['min_disk_free_gib']} GiB",
            'swap == 0 in cgroups of active run wrappers, and in benchmark containers only while a wrapper of their algorithm runs',
            'no run wrapper with affinity on lane cores ' + item['lane']['cpus'], 'no Basalt run active (Basalt runs alone)',
            'boot id == manifest boot ' + manifest['boot_id'], 'budget: now + timeout + 120 s <= deadline (' + manifest['budget']['file'] + ', 120 h from first launch)',
            'manifest sha256 == sidecar == --manifest-sha256', 'no STOP/FAULT file: ' + ', '.join(manifest['stops']['stop_files'] + manifest['stops']['fault_files']),
            'run directory absent: ' + item['run_dir'], 'attempt record absent: ' + item['record'],
            f"fewer than {p['consecutive_infrastructure_failures_stop']} consecutive infrastructure failures"]
    if a['exclusive_host']:
        plan.append('exclusive: no other run wrapper anywhere and no GPU compute process')
    if a['requires_no_gpu_jobs'] and not a['exclusive_host']:
        plan.append('no GPU compute process (nvidia-smi)')
    if a['gpu']:
        plan += ['no other GPU estimator wrapper', 'no OKVIS2-X VIO-LC wrapper (GPU idle during D)',
                 'flock (read-only open, never created) ' + str(a['gpu_lock']) + ' for the whole attempt']
    if a['requires_cpu_idle']:
        plan.append('no CPU benchmark wrapper (AirSLAM policy inherited from the first runs)')
    elif not a['gpu']:
        plan.append('no AirSLAM wrapper active (inherited policy)')
    if a['one_at_a_time']:
        plan.append('no other ' + item['algorithm'] + ' wrapper (one at a time)')
    return plan


def describe(manifest, item, probe=None):
    env = item['environment']
    lines = [f"=== {item['id']}  [{item['group']}]  {item['system']} {item['test']} rep{item['repetition']}",
             f"key        {item['key']}", f"run_id     {item['run_id']}   seed {item['native_seed']}",
             f"run_dir    {item['run_dir']}  (exists: {Path(item['run_dir']).exists()})",
             f"lane       {item['lane']['name']} cpus {item['lane']['cpus']}; container {item['container']['name'] if item['container'] else '-'}",
             f"scope      unit {item['unit']}.scope MemoryMax={item['memory']['max_gib']}G MemorySwapMax=0"
             + (f" MemoryHigh={item['memory']['high_gib']}G" if item['memory']['high_gib'] else '') + f" taskset {item['lane']['cpus']}",
             f"timeout    {item['timeout_s']} s", f"cwd        {item['cwd']}",
             'command    ' + shlex.join(item['command']),
             'env unset  ' + ' '.join(env['removed']),
             'env set    ' + '\n           '.join(f'{k}={shlex.quote(v)}' for k, v in env['set'].items()),
             'env prepend ' + ' '.join(f'{k}={v}:$' + k for k, v in env['prepend'].items()),
             f"evaluator  {item['evaluator']['python']} -B {HERE / 'postrun.py'} evaluate <item> <rc> <timed_out> <log>"
             + (f"; gpu auditor {item['evaluator']['gpu_auditor']['module']}" if item['evaluator']['gpu_auditor'] else ''),
             f"record     {item['record']}   log {item['wrapper_log']}",
             f"reference  {item['reference']['kind']}: {item['reference']['run']}  rc={item['reference']['returncode']} "
             f"status={item['reference']['numerical_status']} failed={item['reference']['failed']} ate={item['reference']['ate_se3_rmse_m']}",
             f"repeat     {item['repeat_check']}",
             'launch checks:'] + ['  - ' + x for x in launch_plan(manifest, item)]
    lines += ['identity gate:'] + ['  - ' + x for x in gate_plan(item)]
    refusals = static_refusals(manifest, item)
    lines.append('static refusals now: ' + ('; '.join(refusals) if refusals else 'none'))
    if probe is not None:
        lines.append('identity probe now (read-only): ' + ('PASS' if probe.passed else 'FAIL'))
        lines += [f"  - [{'ok' if c['passed'] else 'FAIL'}] {c['check']}" + ('' if c['passed'] else ': ' + json.dumps(c['detail'], default=str)[:400])
                  for c in probe.checks]
    return '\n'.join(lines)


def probe_identity(item):
    """Read-only gate parts: no input hashing (that updates the worktree's hash cache)."""
    gate = identity.light_gate(item)
    env = item_env(item)
    for kind in ('implementation', 'runtime'):
        ok, detail = identity.run_verifier(item['worktree']['path'], kind, item['reference']['provenance'][kind]['path'],
                                           env, item['evaluator']['python'])
        gate.check('live ' + kind + ' equals reference provenance', ok, detail)
        if ok:
            digest = detail.get('trees_sha256') if kind == 'implementation' else detail.get('sha256')
            gate.check(kind + ' digest equals frozen campaign identity', digest == item['frozen_identity'][kind])
    return gate


def dry_run(manifest_path, ids, everything, probe, stream=None):
    stream = sys.stdout if stream is None else stream
    manifest, digest = verify_manifest(manifest_path)
    print(f"# DRY RUN - nothing is executed. manifest {manifest_path} sha256 {digest}", file=stream)
    print(f"# campaign {manifest['campaign_id']} boot {manifest['boot_id']} (now {boot_id()}) counts {json.dumps(manifest['counts'])}", file=stream)
    print('# disclosure: ' + manifest['disclosure'], file=stream)
    probed = {}
    for item in select(manifest, ids, everything):
        result = None
        if probe:
            # One read-only probe per system and reference run; identical for its other repetitions.
            cache = (item['system'], item['reference']['run'])
            if cache not in probed:
                probed[cache] = probe_identity(item)
            result = probed[cache]
        print(describe(manifest, item, result), file=stream)
        print(file=stream)


# ---------------------------------------------------------------- execution

def acquire(path):
    """Blocking exclusive lock on a dispatcher-owned lock file; the caller closes the handle."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open('a')
    fcntl.flock(handle, fcntl.LOCK_EX)
    return handle


@contextmanager
def flocked(path, *, create=True, wait=False):
    path = Path(path)
    if create:
        path.parent.mkdir(parents=True, exist_ok=True)
        handle = path.open('a')
    else:
        if not path.is_file():
            raise RuntimeError('Lock file missing (never created here): ' + str(path))
        handle = path.open('rb')
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | (0 if wait else fcntl.LOCK_NB))
        yield handle
    finally:
        handle.close()


def fault(manifest, reason, **evidence):
    path = Path(manifest['stops']['fault_files'][0])
    write_json(path.with_name('FAULT.json'), dict(at=now(), reason=reason, **evidence))
    path.write_text(now() + ' ' + reason + '\n')


def event(manifest, kind, **data):
    path = out_dir(manifest) / 'events.jsonl'
    with path.open('a') as stream:
        stream.write(json.dumps(dict(at=now(), event=kind, **data), default=str) + '\n')


def ensure_container(item):
    """docker start an existing, identity-checked private container; never create one."""
    c = item['container']
    info = identity.docker_inspect(c['name'])
    if info is None:
        raise RuntimeError('Private container missing; refusing (never created): ' + c['name'])
    if not info['State']['Running']:
        subprocess.run(['docker', 'start', c['name']], check=True, timeout=120, capture_output=True)
        info = identity.docker_inspect(c['name'])
    if identity.container_projection(info) != c['identity']:
        raise RuntimeError('Container identity changed after start: ' + c['name'])
    pid = info['State']['Pid']
    group = Path('/sys/fs/cgroup') / Path(f'/proc/{pid}/cgroup').read_text().split('0::', 1)[1].strip().lstrip('/')
    live = {k: (group / k).read_text().strip() for k in ('memory.max', 'memory.swap.max', 'memory.swap.current', 'cpuset.cpus.effective')}
    want = c['effective_cgroup']
    if (live['memory.max'] != want['memory_max'] or live['memory.swap.max'] != want['memory_swap_max']
            or guard.cpu_set(live['cpuset.cpus.effective']) != guard.cpu_set(want['cpuset']) or int(live['memory.swap.current'])):
        raise RuntimeError('Container cgroup limits differ: ' + json.dumps(live))
    return live


def materialize(item):
    """Run the frozen adapters.prepare() for a test that never ran; bytes must equal the manifest."""
    config = item['config']
    code = ('import json,sys;from pathlib import Path;root=Path(sys.argv[1]);'
            "sys.path[:0]=[str(root/'scripts/analysis'),str(root/'scripts/run')];import noise_adapters as a;"
            "print(json.dumps(a.prepare(root,sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],json.loads(sys.argv[6]),Path(sys.argv[7]))))")
    receipt = json.loads(subprocess.run([item['evaluator']['python'], '-B', '-c', code, item['worktree']['path'], item['algorithm'],
                                         item['dataset'], config['expected_receipt']['parent_sequence'], item['mode'],
                                         json.dumps(item['parameters']), config['destination']],
                                        capture_output=True, text=True, check=True, timeout=120).stdout)
    if receipt != config['expected_receipt']:
        raise RuntimeError('Materialized candidate differs from the frozen manifest')
    return receipt


def scope_group(unit):
    result = subprocess.run(['systemctl', '--user', 'show', unit + '.scope', '-p', 'ControlGroup', '--value'],
                            capture_output=True, text=True, timeout=10)
    group = result.stdout.strip()
    return Path('/sys/fs/cgroup') / group.lstrip('/') if result.returncode == 0 and group else None


class GpuSampler(threading.Thread):
    """Light in-run guard for GPU attempts: scope OOM/max events, swap, affinity, host free memory."""

    def __init__(self, item, policy, abort):
        super().__init__(daemon=True)
        self.item, self.policy, self.abort = item, policy, abort
        self.finished, self.errors, self.samples, self.aborted = threading.Event(), [], 0, False
        self.path = Path(item['evaluator']['audit_dir']) / 'n3-samples.jsonl'

    def run(self):
        allowed = set(guard.cpu_set(self.item['lane']['cpus']))
        with self.path.open('a') as stream:
            while not self.finished.wait(self.policy['sample_s']):
                errors = []
                try:
                    group = scope_group(self.item['unit'])
                    if group and group.is_dir():
                        events = dict(line.split() for line in (group / 'memory.events').read_text().splitlines())
                        if any(int(events.get(k, 0)) for k in ('oom', 'oom_kill')):
                            errors.append('native OOM event')
                        if int((group / 'memory.swap.current').read_text()):
                            errors.append('native swap use')
                        for pid in (group / 'cgroup.procs').read_text().split():
                            for task in Path(f'/proc/{pid}/task').glob('*'):
                                try:
                                    if not set(os.sched_getaffinity(int(task.name))) <= allowed:
                                        errors.append('thread affinity outside lane: ' + task.name)
                                except (OSError, ProcessLookupError):
                                    pass
                    available = guard.meminfo()['MemAvailable']
                    if available < 24 * GIB:   # gpu6 GUARD_POLICY abort_available_below_bytes
                        errors.append(f'host available memory {available / GIB:.1f} GiB below 24 GiB')
                        if not self.aborted:
                            self.aborted = True
                            self.abort()
                except Exception as exc:
                    errors.append(f'sampler fault: {type(exc).__name__}: {exc}')
                self.samples += 1
                self.errors.extend(e for e in errors if e not in self.errors)
                stream.write(json.dumps(dict(at=time.time(), errors=errors)) + '\n')
                stream.flush()

    def stop(self):
        self.finished.set()
        self.join(timeout=60)
        return dict(samples=self.samples, errors=self.errors, path=str(self.path))


def kill_scope(item):
    if item['algorithm'] == 'airslam' and item['container']:
        subprocess.run(['docker', 'stop', '--time', '10', item['container']['name']], timeout=60)
    for _ in range(60):
        subprocess.run(['systemctl', '--user', 'kill', '--kill-who=all', '--signal=SIGKILL', item['unit'] + '.scope'],
                       capture_output=True, timeout=10)
        group = scope_group(item['unit'])
        if not group or not group.is_dir() or not (group / 'cgroup.procs').read_text().strip():
            return
        time.sleep(1)
    raise RuntimeError('Scope did not drain: ' + item['unit'])


def run_gate(manifest, digest, item, env):
    """Full gate before the system's first new run this boot, light gate before every other run."""
    gates = out_dir(manifest) / 'identity-gates'
    path = gates / (item['system'] + '.json')
    previous = load(path) if path.is_file() else None
    full = not (previous and previous.get('passed') and previous.get('boot_id') == manifest['boot_id']
                and previous.get('manifest_sha256') == digest)
    gate = identity.full_gate(item, env, item['evaluator']['python']) if full else identity.light_gate(item)
    record = dict(at=now(), item=item['id'], system=item['system'], full=full, passed=gate.passed, checks=gate.checks,
                  boot_id=boot_id(), manifest_sha256=digest)
    write_json(gates / (item['id'] + ('.full' if full else '.light') + '.json'), record)
    if gate.passed and full:
        write_json(path, record)
    if not gate.passed:
        raise RuntimeError('Identity gate failed for ' + item['id'] + ': ' + json.dumps(gate.failures(), default=str)[:2000])
    return record


def repeat_assessment(manifest, item, result):
    ref = item['reference']['ate_se3_rmse_m']
    ate = result.get('ate_se3_rmse_m')
    relative = abs(ate - ref) / ref if isinstance(ate, (int, float)) and isinstance(ref, (int, float)) and ref else None
    first = not any(load(p).get('system') == item['system'] and load(p).get('state') == 'finished'
                    for p in (out_dir(manifest) / 'attempts').glob('*.json') if p != Path(item['record']))
    enforced = item['repeat_check'] == 'match_within_1pct' and first
    return dict(reference_ate=ref, ate=ate, relative_difference=relative, enforced=enforced,
                passed=(relative is not None and relative <= 0.01) if enforced else None)


def execute(manifest_path, expected, item_id, *, poll=None):
    manifest, digest = verify_manifest(manifest_path, expected)
    item = select(manifest, [item_id], False)[0]
    art = out_dir(manifest)
    policy = manifest['launch_policy']
    poll = policy['poll_s'] if poll is None else poll
    root = Path(item['worktree']['path'])
    sys.path[:0] = [str(root / 'scripts/analysis')]
    with ExitStack() as stack:
        stack.enter_context(flocked(art / 'locks' / (item['id'] + '.lock')))
        refusals = static_refusals(manifest, item)
        if consecutive_infrastructure_failures(manifest) >= policy['consecutive_infrastructure_failures_stop']:
            refusals.append('three infrastructure failures in a row')
        if refusals:
            raise SystemExit('Refused: ' + '; '.join(refusals))
        env = item_env(item)
        try:
            gate = run_gate(manifest, digest, item, env)
            if item['container']:
                ensure_container(item)
            if item['config']['mode'] == 'materialize':
                materialize(item)
        except Exception as exc:
            fault(manifest, 'identity/preparation refusal: ' + str(exc), item=item['id'])
            raise
        stack.enter_context(flocked(OUT / 'locks' / ('lane-' + item['lane']['cpus'] + '.lock'), wait=True))
        previous = None
        while True:
            launch = acquire(OUT / 'locks' / 'launch.lock')
            stack.callback(launch.close)
            refusals = static_refusals(manifest, item)
            if refusals:
                raise SystemExit('Refused: ' + '; '.join(refusals))
            state = guard.host_state(item['worktree']['path'], gpu=item['admission']['requires_no_gpu_jobs'])
            reasons = guard.launch_blockers(item, policy, **{k: state[k] for k in
                                            ('runs', 'mem_available', 'disk_free', 'gpu_pids', 'swap_bytes')})
            if not reasons:
                break
            launch.close()
            if reasons != previous:
                event(manifest, 'waiting_for_lane', item=item['id'], reasons=reasons)
                previous = reasons
            time.sleep(poll)
        if item['admission']['gpu_lock']:
            stack.enter_context(flocked(item['admission']['gpu_lock'], create=False))
        budget = Path(manifest['budget']['file'])
        if not budget.exists():
            start = time.time()
            write_json(budget, dict(started_unix=start, deadline_unix=start + manifest['budget']['hours'] * 3600), exclusive=True)
        if static_refusals(manifest, item):
            raise SystemExit('Refused at launch: ' + '; '.join(static_refusals(manifest, item)))
        if item['container']:
            ensure_container(item)   # again, right before launch: run_airslam.sh must never create one
        record = dict(item=item['id'], key=item['key'], campaign_id=item['campaign_id'], phase=item['phase'], state='running',
                      started=now(), boot_id=boot_id(), manifest=str(manifest_path), manifest_sha256=digest,
                      system=item['system'], study=item['study'], group=item['group'], test=item['test'], label=item['label'],
                      params=item['parameters'], sequence=item['sequence'], mode=item['mode'], repetition=item['repetition'],
                      run=item['run_dir'], run_id=item['run_id'], native_seed=item['native_seed'], command=item['command'],
                      environment_set=item['environment']['set'], base_path=os.environ.get('PATH'),
                      timeout_limit_s=item['timeout_s'], lane=item['lane'], identity_gate=dict(full=gate['full'], passed=gate['passed']),
                      host_at_launch={k: state[k] for k in ('mem_available', 'disk_free', 'gpu_pids', 'swap_bytes', 'swap_groups')},
                      reference=dict(record=item['reference']['record'], run=item['reference']['run']))
        write_json(item['record'], record, exclusive=True)
        if item['evaluator']['audit_dir']:
            Path(item['evaluator']['audit_dir']).mkdir(parents=True, exist_ok=False)
        item_file = str(art / 'item-copies' / (item['id'] + '.json'))
        write_json(item_file, item, exclusive=True)
        if item['algorithm'] == 'airslam':   # gpu6 guard: container memory.events baseline before launch
            subprocess.run([item['evaluator']['python'], '-B', str(HERE / 'postrun.py'), 'air-baseline', item_file],
                           check=True, timeout=120, capture_output=True)
        log = Path(item['wrapper_log'])
        log.parent.mkdir(parents=True, exist_ok=True)
        event(manifest, 'attempt_started', item=item['id'], run=item['run_dir'])
        started = time.monotonic()
        with log.open('xb') as stream:
            process = subprocess.Popen(item['command'], cwd=item['cwd'], env=env, stdout=stream, stderr=subprocess.STDOUT,
                                       start_new_session=True)
            time.sleep(15)   # the wrapper is visible before the next dispatcher may launch
            launch.close()
            sampler = None
            timed_out = False
            try:
                if item['admission']['gpu']:
                    sampler = GpuSampler(item, policy, lambda: kill_scope(item))
                else:
                    import sielinko_lanes   # the first runs' own lane sampler (affinity re-pin, exclusivity)
                    protocol = load(next(e['path'] for e in item['pinned_evidence'] if e['role'] == 'env_protocol'))
                    sampler = sielinko_lanes.Sampler(protocol, item['lane']['name'],
                                                     dict(run=item['run_dir'], unit=item['unit']), art / 'lane-samples')
                sampler.start()
                returncode = process.wait(timeout=item['timeout_s'])
            except subprocess.TimeoutExpired:
                timed_out, returncode = True, 124
                stop_attempt(item, process)
            except BaseException:
                stop_attempt(item, process)
                raise
            finally:
                samples = sampler.stop() if sampler else None
        elapsed = time.monotonic() - started
        record.update(finished=now(), returncode=returncode, timeout=timed_out, wall_s=elapsed, wrapper_log=str(log),
                      samples=samples)
        try:
            result = subprocess.run([item['evaluator']['python'], '-B', str(HERE / 'postrun.py'), 'evaluate', item_file,
                                     str(returncode), '1' if timed_out else '0', str(log)],
                                    cwd=item['cwd'], capture_output=True, text=True, timeout=7200)
            if result.returncode:
                raise RuntimeError('post-run evaluation failed: ' + (result.stderr.strip().splitlines() or ['?'])[-1])
            record.update(json.loads(result.stdout.strip().splitlines()[-1]))
            if samples and samples['errors']:
                raise RuntimeError('in-run check failed: ' + '; '.join(samples['errors']))
            record['classification'] = 'timeout_failure' if timed_out else (
                'scientific_failure' if record['result'].get('failed') else 'ok')
            record['repeat'] = repeat_assessment(manifest, item, record['result'])
            record['state'] = 'finished'
            write_json(item['record'], record)
            event(manifest, 'attempt_finished', item=item['id'], returncode=returncode, classification=record['classification'])
            if record['repeat']['enforced'] and not record['repeat']['passed']:
                fault(manifest, 'reproduction check failed (first new run vs first test run, 1 %); write to the engineer',
                      item=item['id'], repeat=record['repeat'])
        except Exception as exc:
            record.update(state='fault', classification=INFRA, error=repr(exc))
            write_json(item['record'], record)
            fault(manifest, 'attempt needs review: ' + str(exc), item=item['id'])
            raise
        return record


def stop_attempt(item, process):
    if item['admission']['gpu']:
        kill_scope(item)
        return
    import noise_cleanup   # the frozen worktree's owned-process cleanup, as the engine used it
    noise_cleanup.stop_owned_attempt(process, Path(item['run_dir']), Path(item['worktree']['path']))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--item', action='append', default=[])
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--dry-run', action='store_true', help='the default')
    parser.add_argument('--probe', action='store_true', help='also run the read-only identity probe')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--manifest-sha256')
    args = parser.parse_args(argv)
    if args.execute:
        if args.dry_run or args.all or len(args.item) != 1 or not args.manifest_sha256:
            raise SystemExit('--execute needs exactly one --item and the reviewed --manifest-sha256')
        signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
        print(json.dumps(execute(args.manifest, args.manifest_sha256, args.item[0]), indent=2, default=str))
        return
    if not args.all and not args.item:
        raise SystemExit('--item ID or --all')
    dry_run(args.manifest, args.item, args.all, args.probe)


if __name__ == '__main__':
    main()
