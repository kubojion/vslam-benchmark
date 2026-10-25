"""Explicit concurrency and resource policy for the experimental campaign.

Activate only with frozen inputs, native assets, and reviewed scheduling evidence.
"""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import sys
import time


def reviewed_attempt_revision(protocol, key):
    """Allow only an explicitly reviewed replacement of a failed physical attempt.

    A replacement keeps the logical candidate/repetition and native seed, but
    receives a different physical run directory. The archived record is required
    evidence, never deleted or silently reclassified as a successful run.
    """
    item = protocol.get('physical_attempt_revisions', {}).get(key)
    if item is None:
        return None
    if (set(item) != {'revision', 'record', 'record_sha256', 'review', 'review_sha256'}
            or not isinstance(item['revision'], str)
            or re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', item['revision']) is None):
        raise RuntimeError('Invalid reviewed attempt revision: ' + key)
    evidence = {}
    for name in ('record', 'review'):
        path = Path(item[name])
        if (not path.is_absolute() or not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != item[name+'_sha256']):
            raise RuntimeError('Replacement evidence missing or changed: ' + key)
        evidence[name] = json.loads(path.read_text())
    old, review = evidence['record'], evidence['review']
    if old.get('key') == key and old.get('state') == 'running' and review.get('classification') == 'pre_estimation_infrastructure_failure':
        # Sielinko search, 25 Oct: refused by the harness before its estimator started (empty run directory).
        if (review.get('revision') != item['revision']
                or key not in review.get('infrastructure_failed_attempts', [])
                or review.get('estimator_started') is not False
                or review.get('scientific_score') is not None
                or review.get('optimizer_feedback') is not False
                or review.get('replacement_count') != 1
                or review.get('original_record_sha256') != item['record_sha256']):
            raise RuntimeError('Incomplete attempt lacks a reviewed pre-estimation replacement: ' + key)
        return item
    if old.get('key') == key and old.get('state') == 'running' and review.get('classification') == 'post_native_helper_crash':
        # Sielinko search, 25 Oct: the native run finished but the post-native provenance helper
        # crashed, leaving the attempt incomplete. Only an explicit helper-crash review admits it.
        # A replacement that failed before its estimator started is listed, never scored, and counted.
        superseded = review.get('superseded_replacements', [])
        if (review.get('revision') != item['revision']
                or key not in review.get('helper_crash_attempts', [])
                or review.get('native_finished') is not True
                or review.get('scientific_score') is not None
                or review.get('optimizer_feedback') is not False
                or not isinstance(superseded, list)
                or any(s.get('estimator_started') is not False or not s.get('record_sha256') for s in superseded)
                or review.get('replacement_count') != 1 + len(superseded)
                or review.get('original_record_sha256') != item['record_sha256']):
            raise RuntimeError('Incomplete attempt lacks a reviewed helper-crash replacement: ' + key)
        return item
    if (old.get('key') != key or old.get('state') != 'finished'
            or not old.get('returncode') or not old.get('result', {}).get('failed')):
        raise RuntimeError('Replacement must reference the reviewed failed attempt: ' + key)
    if (review.get('revision') != item['revision']
            or key not in review.get('resource_censored_attempts', [])):
        raise RuntimeError('Attempt is absent from resource amendment review: ' + key)
    return item


def controller_environment():
    """Record interpreter and relevant package versions, not a dependency hash closure."""
    return dict(python=sys.version, executable=str(Path(sys.executable).resolve()),
        package_versions={name:importlib.metadata.version(name)
                          for name in ('numpy','scipy','optuna','PyYAML')})


def can_launch(spec, active_specs, schedule):
    algorithm = spec['algorithm']
    active = [s['algorithm'] for s in active_specs]
    if algorithm in active:
        return False
    resource = schedule['resource_class'][algorithm]
    occupied = sum(schedule['resource_class'][name] == resource for name in active)
    if occupied >= schedule['slots'][resource]:
        return False
    if not active:
        return True
    proposed = set(active + [algorithm])
    # A count of free slots alone does not validate arbitrary combinations.
    # Missing/empty evidence permits only serial execution.
    return any(proposed <= set(group) for group in schedule.get('validated_concurrent_groups', []))


def validated_limits(protocol, algorithm):
    limits = protocol.get('attempt_resource_limits', {}).get(algorithm)
    if not limits:
        raise RuntimeError('No reviewed resource policy for '+algorithm)
    memory = limits.get('memory_gib')
    if isinstance(memory, bool) or not isinstance(memory, int) or not 1 <= memory <= 64:
        raise RuntimeError('Invalid native memory limit for '+algorithm)
    if limits.get('swap_gib') != 0:
        raise RuntimeError('This validated execution policy requires no swap')
    return limits


DOCKER_PREFIX = {'openvins':'OPENVINS', 'svo_pro':'SVO_PRO'}


def lane_cpus(protocol, lane):
    """The pinned CPU list of a declared execution lane, e.g. '0-3'."""
    item = protocol.get('lanes', {}).get(lane)
    if not item or not isinstance(item.get('cpus'), str) or re.fullmatch(
            r'[0-9]+(-[0-9]+)?(,[0-9]+(-[0-9]+)?)*', item['cpus']) is None:
        raise RuntimeError('No reviewed CPU lane: '+str(lane))
    return item['cpus']


def cpu_set(text):
    """Expand a CPU list such as '0-3,8' into a sorted list of integers."""
    result = set()
    for part in text.split(','):
        first, _, last = part.partition('-')
        result.update(range(int(first), int(last or first)+1))
    return sorted(result)


def lane_environment(protocol, algorithm, lane):
    """Docker estimators run under dockerd, so the lane's limits must reach docker run."""
    prefix = DOCKER_PREFIX.get(algorithm)
    if lane is None or prefix is None:
        return {}
    memory = str(validated_limits(protocol, algorithm)['memory_gib'])+'g'
    return {prefix+'_MEMORY_LIMIT': memory, prefix+'_MEMORY_SWAP_LIMIT': memory,
            prefix+'_CPUSET': lane_cpus(protocol, lane)}


def bounded_command(command, protocol, algorithm, runid, environment, lane=None):
    limits = validated_limits(protocol, algorithm)
    suffix = DOCKER_PREFIX.get(algorithm)
    if suffix:
        expected = str(limits['memory_gib'])+'g'
        if any(environment.get(suffix+'_'+key) != expected
               for key in ('MEMORY_LIMIT', 'MEMORY_SWAP_LIMIT')):
            raise RuntimeError('Docker limits differ from the reviewed attempt policy: '+algorithm)
        if lane is not None and environment.get(suffix+'_CPUSET') != lane_cpus(protocol, lane):
            raise RuntimeError('Docker CPU set differs from the attempt lane: '+algorithm)
    if lane is not None:
        # The user cgroup has no cpuset controller, so AllowedCPUs on the scope
        # would be ignored. Affinity is inherited by every host child process.
        command = ['taskset', '--cpu-list', lane_cpus(protocol, lane), *command]
    token = hashlib.sha256(protocol['campaign_id'].encode()).hexdigest()[:12]
    unit = 'noise-campaign-'+token+'-'+str(runid)
    return ['systemd-run','--user','--scope','--quiet','--unit='+unit,
        '-p','MemoryMax='+str(limits['memory_gib'])+'G','-p','MemorySwapMax=0',*command]


def verify_persistent_limits(protocol, algorithm, item, lane=None):
    limits = validated_limits(protocol, algorithm)
    if item is None:
        raise RuntimeError('Private persistent container is unavailable')
    expected = limits['memory_gib']*1024**3
    if any(item['HostConfig'].get(k) != expected for k in ('Memory','MemorySwap')):
        raise RuntimeError('Private container resource limits differ from the frozen policy')
    if lane is not None and cpu_set(item['HostConfig'].get('CpusetCpus') or '0-1023') != cpu_set(lane_cpus(protocol, lane)):
        raise RuntimeError('Private container CPU set differs from the attempt lane')
    if protocol['scheduling']['resource_class'][algorithm]=='cpu' and item['HostConfig'].get('DeviceRequests'):
        raise RuntimeError('CPU-only phase has an unexpected GPU-enabled container')


def identity_environment(protocol, algorithm, dataset, sequence):
    """Make existing wrapper preflight enforce the frozen input/native identity."""
    values = {
        'VSLAM_EXPECTED_INPUT_SHA256': protocol.get('frozen_input_sha256', {}).get(dataset+'/'+sequence),
        'VSLAM_EXPECTED_RUNTIME_SHA256': protocol.get('frozen_runtime_sha256', {}).get(algorithm),
        'VSLAM_EXPECTED_SOURCE_SHA256': protocol.get('frozen_source_sha256', {}).get(algorithm),
    }
    if any(not isinstance(value,str) or re.fullmatch(r'[0-9a-f]{64}',value) is None for value in values.values()):
        raise RuntimeError('Complete frozen input/runtime/source identities are required before execution')
    return values


def campaign_budget(art, protocol):
    """All phased executions share one deadline; a restart never buys more time.

    The caller holds the production execution lease before invoking this.
    """
    art = Path(art)
    name = protocol.get('shared_budget_file')
    if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9_-]+\.json', name):
        raise RuntimeError('A shared campaign budget filename is required')
    shared = art.parent/name
    local = art/'budget.json'
    hours = protocol['max_wall_hours']
    if isinstance(hours, bool) or not isinstance(hours, (int, float)) or not 0 < hours <= 264:
        raise RuntimeError('Invalid campaign wall-time budget')
    if shared.exists():
        value = json.loads(shared.read_text())
    else:
        if local.exists():
            raise RuntimeError('Existing phase budget without its shared source requires review')
        start = time.time()
        value = dict(started_unix=start, deadline_unix=start+hours*3600)
        with shared.open('x') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')
    if (set(value) != {'started_unix','deadline_unix'}
            or value['deadline_unix']-value['started_unix'] != hours*3600):
        raise RuntimeError('Shared campaign budget differs from the frozen protocol')
    if time.time() >= value['deadline_unix']:
        raise InterruptedError('Shared campaign wall-time budget has expired')
    if local.exists():
        if json.loads(local.read_text()) != value:
            raise RuntimeError('Phase deadline differs from the shared campaign budget')
    else:
        with local.open('x') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')
    return value
