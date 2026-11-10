"""Identity gate: a new repetition must be identical to its system's first run.

Not an outcome gate. Checks (engineer, 10 Nov 2026, item 3):
  worktree commit, tracked scripts/configs bytes and membership, native source state,
  parameter/config file hash, input hashes, container image and limits, runtime/binary hashes,
  and the evaluator interpreter.
The live checks reuse the frozen worktree's own provenance verifiers
(scripts/run/_capture_implementation.py, _capture_inputs.py, _capture_runtime.py) against the
reference run's provenance files, in a subprocess with python -B so nothing is written there.
Only the input verifier updates the worktree's untracked hash cache (results/.cache), exactly as
every wrapper preflight does; it runs in execution mode only.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

from .common import sha, load

VERIFY = r'''
import json, sys, hashlib
sys.path.insert(0, sys.argv[1] + '/scripts/run')
kind, ref = sys.argv[2], sys.argv[3]
value = json.loads(open(ref).read())
if kind == 'implementation':
    import _capture_implementation as m
    out = m.verify_capture(sys.argv[1], ref, check_live=True)
    out['trees_sha256'] = hashlib.sha256(json.dumps(value['trees'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
elif kind == 'runtime':
    import _capture_runtime as m
    m.verify_identity(sys.argv[1], value, check_live=True)
    out = dict(sha256=value['sha256'], files=len(value['files']))
elif kind == 'inputs':
    import _capture_inputs as m
    m.verify_identity(sys.argv[1], value, check_live=True)
    out = dict(sha256=value['sha256'], files=len(value['files']))
print(json.dumps(out))
'''


def git_head(root):
    return subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], capture_output=True, text=True,
                          check=True, timeout=30).stdout.strip()


def docker_inspect(name):
    result = subprocess.run(['docker', 'inspect', name], capture_output=True, text=True, timeout=30)
    if result.returncode:
        return None
    return json.loads(result.stdout)[0]


def container_projection(info):
    """The identity-bearing part of `docker inspect`: never changes by docker start/stop."""
    host = info['HostConfig']
    return dict(Id=info['Id'], Image=info['Image'], Name=info['Name'].lstrip('/'),
                CpusetCpus=host.get('CpusetCpus'), Memory=host.get('Memory'), MemorySwap=host.get('MemorySwap'),
                gpu=bool(host.get('DeviceRequests')), Runtime=host.get('Runtime'),
                Mounts=sorted([m['Source'], m['Destination'], bool(m['RW'])] for m in info['Mounts']),
                Env=sorted(info['Config'].get('Env') or []), Cmd=info['Config'].get('Cmd'))


class Gate:
    def __init__(self):
        self.checks = []

    def check(self, name, ok, detail=None):
        self.checks.append(dict(check=name, passed=bool(ok), detail=detail))
        return ok

    @property
    def passed(self):
        return bool(self.checks) and all(c['passed'] for c in self.checks)

    def failures(self):
        return [c for c in self.checks if not c['passed']]


def light_gate(item, *, head=git_head, inspect=docker_inspect, gate=None):
    """Cheap checks, before every attempt: commit, pinned evidence, config bytes, container."""
    gate = gate or Gate()
    root = item['worktree']['path']
    reference = item['reference']
    try:
        actual = head(root)
    except Exception as exc:  # a broken checkout is a mismatch, never a pass
        actual = 'unreadable: ' + repr(exc)
    gate.check('worktree HEAD equals manifest commit', actual == item['worktree']['commit'],
               dict(actual=actual, expected=item['worktree']['commit']))
    implementation = reference['provenance']['implementation']
    if Path(implementation['path']).is_file():
        workspace = next((t for t in load(implementation['path'])['trees'] if t['role'] == 'workspace'), {})
        gate.check('reference run was made at the manifest commit', workspace.get('commit') == item['worktree']['commit'],
                   dict(reference=workspace.get('commit')))
    for entry in item['pinned_evidence']:
        path = Path(entry['path'])
        ok = path.is_file() and sha(path) == entry['sha256']
        gate.check('pinned evidence unchanged: ' + entry['role'], ok, entry['path'])
    config = item['config']
    for entry in config['sources']:
        path = Path(root) / entry['path']
        gate.check('config source unchanged: ' + entry['path'], path.is_file() and sha(path) == entry['sha256'])
    if config['mode'] == 'reuse':
        for entry in config['files']:
            path = Path(entry['path'])
            gate.check('parameter/config file unchanged: ' + path.name, path.is_file() and sha(path) == entry['sha256'],
                       entry['path'])
    container = item.get('container')
    if container:
        info = inspect(container['name'])
        if info is None:
            gate.check('private container exists (never created by the dispatcher)', False, container['name'])
        else:
            live = container_projection(info)
            diff = {k: dict(expected=container['identity'][k], live=live.get(k))
                    for k in container['identity'] if live.get(k) != container['identity'][k]}
            gate.check('container identity equals recorded identity', not diff, diff or container['identity_source'])
    return gate


def run_verifier(root, kind, reference_path, env, python, scripts_root=None):
    """Run one frozen provenance verifier against the live checkout; returns (ok, detail)."""
    result = subprocess.run([python, '-B', '-c', VERIFY, str(scripts_root or root), kind, str(reference_path)],
                            cwd=str(root), env=env, capture_output=True, text=True, timeout=7200)
    if result.returncode:
        return False, (result.stderr.strip().splitlines() or ['verifier failed'])[-1]
    return True, json.loads(result.stdout.strip().splitlines()[-1])


def full_gate(item, env, python, *, include_inputs=True, head=git_head, inspect=docker_inspect, verifier=run_verifier):
    """Light gate plus the frozen live verifiers and the frozen campaign identities."""
    gate = light_gate(item, head=head, inspect=inspect)
    root = item['worktree']['path']
    provenance = item['reference']['provenance']
    expected = item['frozen_identity']
    kinds = ['implementation', 'runtime'] + (['inputs'] if include_inputs else [])
    for kind in kinds:
        ok, detail = verifier(root, kind, provenance[kind]['path'], env, python)
        gate.check('live ' + kind + ' equals reference provenance', ok, detail)
        if ok:
            digest = detail.get('trees_sha256') if kind == 'implementation' else detail.get('sha256')
            gate.check(kind + ' digest equals frozen campaign identity', digest == expected[kind], dict(live=digest, frozen=expected[kind]))
    evaluator = item['evaluator']
    probe = subprocess.run([evaluator['python'], '-B', '-c', 'import sys,json,importlib.metadata as m;'
                            'print(json.dumps(dict(python=sys.version,package_versions={n:m.version(n) for n in '
                            '("numpy","scipy","optuna","PyYAML")})))'], capture_output=True, text=True, timeout=120)
    live = json.loads(probe.stdout) if probe.returncode == 0 else None
    want = evaluator['controller_environment']
    gate.check('evaluator interpreter and packages equal the first run', live is not None and live['python'] == want['python']
               and live['package_versions'] == want['package_versions'], dict(live=live))
    return gate
