"""Cancel only the processes/containers recorded for an experimental attempt."""
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys


# This checkout's private persistent containers (run_voxel_svio.sh, run_airslam.sh).
PERSISTENT = {'voxel_svio': 'vslam_search_voxel_20261031', 'airslam': 'vslam_search_air_20261031'}
EPHEMERAL = {'openvins', 'svo_pro'}


def inspect_container(identity):
    result = subprocess.run(['docker', 'inspect', identity], capture_output=True,
                            text=True, timeout=15)
    if result.returncode:
        if 'No such object:' in result.stderr or 'No such container:' in result.stderr:
            return None
        raise RuntimeError('Cannot verify attempt container identity: ' + result.stderr.strip())
    items = json.loads(result.stdout)
    if len(items) != 1:
        raise RuntimeError('Ambiguous container identity')
    return items[0]


def owned_container(run, root):
    """Never trust a process namespace or a saved PID without container ownership."""
    root, run = Path(root).resolve(), Path(run).resolve()
    parts = run.relative_to(root / 'results').parts
    if len(parts) != 5:
        raise ValueError('Unexpected attempt path')
    mode, dataset, sequence, algorithm, run_name = parts
    if not re.fullmatch(r'run[0-9]+', run_name):
        raise ValueError('Unexpected run identity')
    if algorithm in EPHEMERAL:
        cidfile = run / 'docker.cid'
        if not cidfile.exists():
            return None, 'ephemeral_not_created'
        cid = cidfile.read_text().strip()
        if not re.fullmatch(r'[a-f0-9]{64}', cid):
            raise RuntimeError('Invalid saved container ID')
        item = inspect_container(cid)
        if item is None:
            return None, 'ephemeral_removed'
        prefix = f'vslam_{algorithm}_{dataset}_{sequence}_{run_name[3:]}_'
        owned = (item['Id'] == cid and item['Name'].lstrip('/').startswith(prefix)
                 and any(m['Source'] == str(root) and m['Destination'] == '/ws'
                         for m in item['Mounts']))
        if not owned:
            raise RuntimeError('Ephemeral container ownership mismatch; refusing to stop it')
        return item, 'ephemeral'
    if algorithm in PERSISTENT:
        name = PERSISTENT[algorithm]
        item = inspect_container(name)
        if item is None:
            return None, 'persistent_absent'
        if (item['Name'].lstrip('/') != name or not any(
                m['Source'] == str(root / 'results') and m['Destination'] == '/results'
                for m in item['Mounts'])):
            raise RuntimeError('Persistent container ownership mismatch; refusing cleanup')
        return item, 'persistent'
    return None, 'host'


def stop_owned_attempt(process, run, root):
    """Let wrapper traps finish, then verify and clean any recorded descendants.

    Cleanup also runs when a wrapper exits early, since its child may have
    detached. Container process records are never interpreted as host PIDs.
    """
    run, root = Path(run), Path(root)
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=45)
        except subprocess.TimeoutExpired:
            pass
    container, location = owned_container(run, root)
    if location == 'host' or (container and container['State']['Running']):
        for state in sorted((run / 'processes').glob('*.json')):
            args = [sys.executable, str(root / 'scripts/run/_owned_process.py'),
                    '--state', str(state)]
            if container:
                inside = ('/ws/' + str(state.relative_to(root)) if location == 'ephemeral'
                          else '/results/' + str(state.relative_to(root / 'results')))
                args += ['--container', container['Id'], '--container-state', inside]
            subprocess.run(args + ['stop'], check=True, timeout=30,
                           stdout=subprocess.DEVNULL)
    if location == 'ephemeral' and container:
        # Reinspect the immutable ID because --rm may remove it during stage cleanup.
        current = inspect_container(container['Id'])
        if current and current['State']['Running']:
            subprocess.run(['docker', 'stop', '--time', '10', container['Id']],
                           check=True, timeout=20, stdout=subprocess.DEVNULL)
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=15)
    return {'location': location, 'container_id': container['Id'] if container else None}
