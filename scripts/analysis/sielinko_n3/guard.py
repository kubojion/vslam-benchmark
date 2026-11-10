"""Launch checks for the N=3 dispatcher. Pure functions over injected host snapshots.

A benchmark run is recognised by its wrapper process (scripts/run/run_<algorithm>.sh, from
any checkout, including the live repo's Rule C runs).

Swap guard (fixed, engineer 10 Nov 2026): swap counts only in
  - the cgroups of active run wrappers, and
  - a benchmark container while a wrapper of that container's algorithm is active.
Idle controllers, idle persistent containers, left-over scopes and system services never
block a launch (the 10 Nov 17:05 false positive was an idle Voxel container).
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess

from .common import GIB

CGROUP_ROOT = Path('/sys/fs/cgroup')
WRAPPER = re.compile(r'(?:^|/)scripts/run/run_([a-z0-9_]+)\.sh$')
GPU_ALGORITHMS = frozenset({'airslam', 'cuvslam', 'mast3r_fusion', 'macvo', 'dpvo', 'droid_slam'})
# Persistent or named benchmark containers and the algorithm whose wrapper drives them.
CONTAINER_ALGORITHMS = {
    'sielinko_search_voxel_20261022': 'voxel_svio', 'noise_reliable_voxel_20261009': 'voxel_svio',
    'voxel_svio': 'voxel_svio', 'sielinko_gpu_airslam_20261026': 'airslam', 'air_slam': 'airslam',
    'noise_reliable_airslam_20261009': 'airslam', 'ov2slam': 'ov2slam',
}
NAME_TOKENS = (('voxel', 'voxel_svio'), ('airslam', 'airslam'), ('air_slam', 'airslam'),
               ('openvins', 'openvins'), ('svo', 'svo_pro'), ('ov2slam', 'ov2slam'), ('dsol', 'dsol'))


def cpu_set(text):
    result = set()
    for part in str(text).split(','):
        first, _, last = part.partition('-')
        result.update(range(int(first), int(last or first) + 1))
    return sorted(result)


def meminfo(path='/proc/meminfo'):
    return {line.split(':')[0]: int(line.split()[1]) * 1024 for line in Path(path).read_text().splitlines()}


def processes(proc=Path('/proc')):
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
    """Active run wrappers: pid, algorithm, mode (when visible in argv), cpus and cgroup."""
    runs = []
    for item in snapshot:
        argv = item['argv']
        for index, arg in enumerate(argv[:3]):
            match = WRAPPER.search(arg)
            if match:
                rest = argv[index + 1:]
                runs.append(dict(pid=item['pid'], algorithm=match[1], wrapper=arg, cpus=item['cpus'],
                                 cgroup=item['cgroup'].strip(), mode=rest[3] if len(rest) >= 4 else None))
                break
    return runs


def run_cgroups(runs, root=CGROUP_ROOT):
    groups = set()
    for run in runs:
        for line in run['cgroup'].splitlines():
            if line.startswith('0::'):
                groups.add(Path(root) / line[3:].strip().lstrip('/'))
    return sorted(groups)


def container_algorithm(name):
    if name in CONTAINER_ALGORITHMS:
        return CONTAINER_ALGORITHMS[name]
    if name.startswith('vslam_') or name.startswith('noise_') or name.startswith('sielinko_'):
        for token, algorithm in NAME_TOKENS:
            if token in name:
                return algorithm
    return None


def running_containers():
    """(name, cgroup directory) of running containers."""
    out = subprocess.run(['/usr/bin/docker', 'ps', '--format', '{{.ID}} {{.Names}}', '--no-trunc'],
                         capture_output=True, text=True, timeout=20, check=True).stdout
    rows = []
    for line in out.splitlines():
        cid, _, name = line.partition(' ')
        rows.append((name, CGROUP_ROOT / 'system.slice' / f'docker-{cid}.scope'))
    return rows


def read_swap(group):
    try:
        return int((Path(group) / 'memory.swap.current').read_text())
    except (FileNotFoundError, ValueError, OSError):
        return 0


def counted_swap_groups(runs, containers, root=CGROUP_ROOT):
    active = {r['algorithm'] for r in runs}
    groups = run_cgroups(runs, root)
    groups += [Path(group) for name, group in containers if container_algorithm(name) in active]
    return groups


def benchmark_swap_bytes(runs, containers, root=CGROUP_ROOT, reader=read_swap):
    return sum(reader(group) for group in counted_swap_groups(runs, containers, root))


def gpu_compute_pids():
    try:
        result = subprocess.run(['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'],
                                capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode:
        return None
    return [int(x) for x in result.stdout.split() if x.strip().isdigit()]


def describe(runs):
    return ', '.join(f"{r['algorithm']}:{r['pid']}" for r in runs)


def launch_blockers(item, policy, *, runs, mem_available, disk_free, gpu_pids, swap_bytes):
    """Reasons this item may not launch now; an empty list means it may.

    item: a manifest item (uses algorithm, mode, lane.cpus, admission).
    policy: manifest launch_policy (min_available_gib, min_disk_free_gib).
    """
    reasons = []
    admission = item['admission']
    if mem_available < policy['min_available_gib'] * GIB:
        reasons.append(f"free memory {mem_available / GIB:.1f} GiB below {policy['min_available_gib']} GiB")
    if disk_free < policy['min_disk_free_gib'] * GIB:
        reasons.append(f"free disk {disk_free / GIB:.0f} GiB below {policy['min_disk_free_gib']} GiB")
    if swap_bytes > 0:
        reasons.append(f'active benchmark runs hold swap ({swap_bytes} bytes)')
    mine = set(cpu_set(item['lane']['cpus']))
    for run in runs:
        if mine & set(run['cpus']):
            reasons.append(f"{run['algorithm']}:{run['pid']} uses lane cores {sorted(mine & set(run['cpus']))}")
    basalt = [r for r in runs if r['algorithm'] == 'basalt']
    if basalt:
        reasons.append('Basalt runs alone: ' + describe(basalt))
    if admission.get('exclusive_host') and runs:
        reasons.append('host not idle for an exclusive attempt: ' + describe(runs))
    if admission.get('requires_no_gpu_jobs'):
        if gpu_pids is None:
            reasons.append('GPU use cannot be verified')
        elif gpu_pids:
            reasons.append('GPU jobs active: ' + ', '.join(map(str, gpu_pids)))
    if admission.get('gpu'):
        others = [r for r in runs if r['algorithm'] in GPU_ALGORITHMS]
        if others:
            reasons.append('one GPU estimator at a time: ' + describe(others))
        d_runs = [r for r in runs if r['algorithm'] == 'okvis2x' and r['mode'] == 'vio-lc']
        if d_runs:
            reasons.append('GPU lane stays idle during OKVIS2-X VIO-LC (Update 10 D): ' + describe(d_runs))
    if admission.get('requires_cpu_idle'):
        cpu_runs = [r for r in runs if r['algorithm'] not in GPU_ALGORITHMS]
        if cpu_runs:
            reasons.append('AirSLAM requires no CPU benchmark run (inherited policy): ' + describe(cpu_runs))
    elif not admission.get('gpu'):
        air = [r for r in runs if r['algorithm'] == 'airslam']
        if air:
            reasons.append('CPU runs wait while AirSLAM runs (inherited policy): ' + describe(air))
    if admission.get('one_at_a_time'):
        same = [r for r in runs if r['algorithm'] == item['algorithm']]
        if same:
            reasons.append('one ' + item['algorithm'] + ' run at a time: ' + describe(same))
    return reasons


def host_state(worktree, *, gpu=True):
    """Collect a live snapshot for launch_blockers (read-only)."""
    snapshot = processes()
    runs = benchmark_runs(snapshot)
    containers = running_containers()
    return dict(runs=runs, mem_available=meminfo()['MemAvailable'], disk_free=shutil.disk_usage(worktree).free,
                gpu_pids=gpu_compute_pids() if gpu else [], swap_bytes=benchmark_swap_bytes(runs, containers),
                swap_groups=[str(g) for g in counted_swap_groups(runs, containers)])
