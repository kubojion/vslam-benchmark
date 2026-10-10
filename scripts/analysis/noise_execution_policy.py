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


def bounded_command(command, protocol, algorithm, runid, environment):
    limits = validated_limits(protocol, algorithm)
    suffix = {'openvins':'OPENVINS', 'svo_pro':'SVO_PRO'}.get(algorithm)
    if suffix:
        expected = str(limits['memory_gib'])+'g'
        if any(environment.get(suffix+'_'+key) != expected
               for key in ('MEMORY_LIMIT', 'MEMORY_SWAP_LIMIT')):
            raise RuntimeError('Docker limits differ from the reviewed attempt policy: '+algorithm)
    token = hashlib.sha256(protocol['campaign_id'].encode()).hexdigest()[:12]
    unit = 'noise-campaign-'+token+'-'+str(runid)
    return ['systemd-run','--user','--scope','--quiet','--unit='+unit,
        '-p','MemoryMax='+str(limits['memory_gib'])+'G','-p','MemorySwapMax=0',*command]


def verify_persistent_limits(protocol, algorithm, item):
    limits = validated_limits(protocol, algorithm)
    if item is None:
        raise RuntimeError('Private persistent container is unavailable')
    expected = limits['memory_gib']*1024**3
    if any(item['HostConfig'].get(k) != expected for k in ('Memory','MemorySwap')):
        raise RuntimeError('Private container resource limits differ from the frozen policy')
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
