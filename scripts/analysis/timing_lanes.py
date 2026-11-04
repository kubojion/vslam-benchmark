"""Host checks for the noise search lanes (PLAN Update 6). Nothing here starts an estimator.

Copied from the Sielinko search's lanes module, without its lane lock files.

A benchmark run is recognised by its wrapper process (scripts/run/run_<algorithm>.sh,
from any checkout); every run of every controller has one for its whole duration.
That makes the lane rules checkable without a shared registry:

- a lane launches only with enough free memory and disk, no swap in benchmark cgroups (user, 24 Oct),
  and no other run on its cores;
- nothing launches while any Basalt run is active (Basalt runs alone);
- an exclusive (Basalt) attempt launches only when no run and no GPU job exist;
- the GPU lane launches only when no other GPU job exists.

During an attempt a sampler checks the attempt's own processes and containers.
A host thread that widens its own affinity (Mesa's shader-cache worker in ORB-SLAM3
does) is put back on the lane cores and logged, as in Rule C revision 13; a failed
re-pin, or more than max_affinity_corrections episodes in one attempt, is a finding.
A container must carry the lane's CPU set and an exclusive attempt must stay alone.
A finding stops the search at the boundary.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
import time

from noise_execution_policy import cpu_set, lane_cpus

GIB = 1024**3
# Benchmark cgroups whose swap blocks a launch (user, 24 Oct, as Rule C revision 13p): system services
# (tomcat9, Overleaf, editors) may swap; benchmark units, scopes and containers may not.
USER_UNITS = Path(f'/sys/fs/cgroup/user.slice/user-{os.getuid()}.slice/user@{os.getuid()}.service/app.slice')
BENCH_UNIT_PREFIXES = ('vslam-', 'noise-campaign-')
BENCH_CONTAINERS = ('voxel_svio', 'air_slam', 'ov2slam')
QUERY = object()  # ask the GPU now; None means it could not be asked
WRAPPER = re.compile(r'(?:^|/)scripts/run/run_([a-z0-9_]+)\.sh$')


def meminfo():
    return {line.split(':')[0]: int(line.split()[1]) * 1024
            for line in Path('/proc/meminfo').read_text().splitlines()}


def processes(proc=Path('/proc')):
    """Snapshot of host processes: argv, CPU affinity and cgroup."""
    found = []
    for entry in Path(proc).iterdir():
        if not entry.name.isdigit():
            continue
        try:
            argv = (entry / 'cmdline').read_bytes().decode(errors='replace').split('\0')
            cgroup = (entry / 'cgroup').read_text()
            cpus = sorted(os.sched_getaffinity(int(entry.name)))
        except (OSError, ProcessLookupError):
            continue
        found.append(dict(pid=int(entry.name), argv=[a for a in argv if a], cgroup=cgroup, cpus=cpus))
    return found


def benchmark_runs(snapshot):
    """Wrapper processes of active benchmark runs, from any checkout or controller."""
    runs = []
    for item in snapshot:
        for arg in item['argv'][:3]:
            match = WRAPPER.search(arg)
            if match:
                runs.append(dict(pid=item['pid'], algorithm=match[1], wrapper=arg, cpus=item['cpus'],
                                 cgroup=item['cgroup'].strip()))
                break
    return runs


def gpu_compute_pids():
    """PIDs with a GPU context, or None when the GPU cannot be queried."""
    try:
        result = subprocess.run(['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'],
                                capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode:
        return None
    return [int(x) for x in result.stdout.split() if x.strip().isdigit()]


def benchmark_container_groups():
    out = subprocess.run(['/usr/bin/docker', 'ps', '--format', '{{.ID}} {{.Names}}', '--no-trunc'],
                         capture_output=True, text=True, timeout=20, check=True).stdout
    groups = []
    for line in out.splitlines():
        cid, _, name = line.partition(' ')
        if name.startswith('vslam_') or name in BENCH_CONTAINERS:
            groups.append(Path('/sys/fs/cgroup/system.slice') / f'docker-{cid}.scope')
    return groups


def benchmark_swap_bytes(user_units=USER_UNITS, container_groups=None):
    """Swap held by benchmark cgroups only: vslam-* and noise-campaign-* user units/scopes and benchmark containers."""
    groups = [g for g in user_units.iterdir() if g.name.startswith(BENCH_UNIT_PREFIXES)] if user_units.is_dir() else []
    groups += benchmark_container_groups() if container_groups is None else container_groups
    total = 0
    for group in groups:
        try:
            total += int((group / 'memory.swap.current').read_text())
        except (FileNotFoundError, ValueError, OSError):
            continue
    return total


def launch_blockers(protocol, lane, *, snapshot=None, memory=None, gpu=QUERY, disk_free=None, benchmark_swap=None):
    """Reasons this lane may not launch now; an empty list means it may."""
    policy = protocol['launch_policy']
    memory = meminfo() if memory is None else memory
    snapshot = processes() if snapshot is None else snapshot
    disk_free = shutil.disk_usage(protocol['worktree']).free if disk_free is None else disk_free
    reasons = []
    if memory['MemAvailable'] < policy['min_available_gib'] * GIB:
        reasons.append(f"free memory {memory['MemAvailable'] / GIB:.1f} GiB below {policy['min_available_gib']} GiB")
    if policy.get('no_host_swap_use'):
        swapped = benchmark_swap_bytes() if benchmark_swap is None else benchmark_swap
        if swapped > 0:
            reasons.append(f'benchmark cgroups swap in use ({swapped} bytes)')
    if disk_free < policy.get('min_disk_free_gib', 0) * GIB:
        reasons.append(f'free disk {disk_free / GIB:.0f} GiB below {policy["min_disk_free_gib"]} GiB')
    runs = benchmark_runs(snapshot)
    mine = set(cpu_set(lane_cpus(protocol, lane)))
    if protocol['lanes'][lane].get('idle_host'):
        if runs:
            reasons.append('host not idle: ' + ', '.join(f"{r['algorithm']}:{r['pid']}" for r in runs))
        gpu = gpu_compute_pids() if gpu is QUERY else gpu
        if gpu is None:
            reasons.append('GPU use cannot be verified')
        elif gpu:
            reasons.append('GPU jobs active: ' + ', '.join(map(str, gpu)))
    else:
        if protocol['lanes'][lane].get('gpu'):
            gpu = gpu_compute_pids() if gpu is QUERY else gpu
            if gpu is None:
                reasons.append('GPU use cannot be verified')
            elif gpu:
                reasons.append('GPU jobs active: ' + ', '.join(map(str, gpu)))
        for run in runs:
            if run['algorithm'] == 'basalt':
                reasons.append(f"Basalt runs alone: {run['pid']}")
            elif mine & set(run['cpus']):
                reasons.append(f"{run['algorithm']}:{run['pid']} uses lane cores {sorted(mine & set(run['cpus']))}")
    return reasons


def container_cpuset(cidfile):
    """CPU set of an attempt's ephemeral container, or None before it exists."""
    cidfile = Path(cidfile)
    if not cidfile.is_file() or not cidfile.read_text().strip():
        return None
    result = subprocess.run(['docker', 'inspect', '--format', '{{.HostConfig.CpusetCpus}}',
                             cidfile.read_text().strip()], capture_output=True, text=True, timeout=15)
    return result.stdout.strip() if result.returncode == 0 else None


def thread_affinities(pid):
    result = {}
    try:
        for task in Path(f'/proc/{pid}/task').iterdir():
            try:
                result[int(task.name)] = sorted(os.sched_getaffinity(int(task.name)))
            except (OSError, ProcessLookupError):
                pass
    except OSError:
        pass
    return result


def escaped_threads(protocol, lane, attempt, snapshot):
    """(pid, tid, affinity) of the attempt's host threads outside the lane cores."""
    allowed = set(cpu_set(lane_cpus(protocol, lane)))
    scope = '/' + attempt['unit'] + '.scope'
    return [(item['pid'], task, cpus) for item in snapshot if scope in item['cgroup']
            for task, cpus in thread_affinities(item['pid']).items() if not set(cpus) <= allowed]


def repin(protocol, lane, escapes):
    """Put escaped threads back on the lane cores; returns (corrections, findings)."""
    cpus = cpu_set(lane_cpus(protocol, lane))
    corrections, errors = [], []
    for pid, tid, before in escapes:
        row = dict(pid=pid, tid=tid, before=before)
        try:
            row['thread'] = Path(f'/proc/{pid}/task/{tid}/comm').read_text().strip()
        except OSError:
            row['thread'] = None
        try:
            os.sched_setaffinity(tid, cpus)
            row['after'] = sorted(os.sched_getaffinity(tid))
        except ProcessLookupError:
            continue  # the thread has already ended
        except OSError as exc:
            row['error'] = repr(exc)
        corrections.append(row)
        if row.get('after') != cpus:
            errors.append(f"could not re-pin thread {tid} ({row['thread']}) of {pid} to lane {lane}")
    return corrections, errors


def sample_errors(protocol, lane, attempt, snapshot, *, cpuset=None, gpu=None):
    """Check one sample of a running attempt (container and exclusivity); returns findings."""
    allowed = set(cpu_set(lane_cpus(protocol, lane)))
    scope = '/' + attempt['unit'] + '.scope'
    errors = []
    if cpuset is not None and cpu_set(cpuset or '0-1023') != sorted(allowed):
        errors.append(f'attempt container CPU set {cpuset!r} differs from lane {lane}')
    if protocol['lanes'][lane].get('idle_host'):
        others = [r for r in benchmark_runs(snapshot) if scope not in r['cgroup']]
        if others:
            errors.append('run beside an exclusive attempt: ' + ', '.join(f"{r['algorithm']}:{r['pid']}" for r in others))
        if gpu:
            errors.append('GPU job beside an exclusive attempt: ' + ', '.join(map(str, gpu)))
    return errors


class Sampler(threading.Thread):
    """Samples one attempt until stopped; findings are kept with the attempt's samples."""

    def __init__(self, protocol, lane, attempt, directory):
        super().__init__(daemon=True)
        self.protocol, self.lane, self.attempt = protocol, lane, attempt
        self.path = Path(directory) / (Path(attempt['run']).name + '.jsonl')
        self.finished = threading.Event()
        self.errors, self.samples, self.episodes = [], 0, 0

    def run(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('a') as stream:
            while True:
                stopping = self.finished.is_set()
                try:
                    snapshot = processes()
                    cpuset = container_cpuset(Path(self.attempt['run']) / 'docker.cid')
                    exclusive = self.protocol['lanes'][self.lane].get('idle_host')
                    gpu = gpu_compute_pids() if exclusive else None
                    errors = sample_errors(self.protocol, self.lane, self.attempt, snapshot, cpuset=cpuset, gpu=gpu)
                    if exclusive and gpu is None:
                        errors.append('GPU use cannot be verified')
                    corrections = []
                    escapes = escaped_threads(self.protocol, self.lane, self.attempt, snapshot)
                    if escapes:
                        # One correction episode per sample with escapes; every thread is logged.
                        self.episodes += 1
                        corrections, failed = repin(self.protocol, self.lane, escapes)
                        errors += failed
                        limit = self.protocol['launch_policy']['max_affinity_corrections']
                        if self.episodes > limit:
                            errors.append(f'more than {limit} affinity corrections in one attempt')
                    memory = meminfo()['MemAvailable']
                except Exception as exc:  # a sampler fault is a finding, never a silent pass
                    errors, cpuset, memory, corrections = [f'sampler fault: {type(exc).__name__}: {exc}'], None, None, []
                self.samples += 1
                self.errors.extend(e for e in errors if e not in self.errors)
                stream.write(json.dumps(dict(at=time.time(), lane=self.lane, container_cpuset=cpuset,
                                             available_bytes=memory, affinity_corrections=corrections,
                                             errors=errors)) + '\n')
                stream.flush()
                if stopping or self.finished.wait(self.protocol['launch_policy']['sample_s']):
                    if stopping:
                        return

    def stop(self):
        self.finished.set()
        self.join(timeout=60)
        return dict(samples=self.samples, errors=self.errors, affinity_correction_episodes=self.episodes,
                    path=str(self.path))
