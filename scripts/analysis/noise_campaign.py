"""Frozen-identity helpers of the noise search. Nothing here starts an estimator.

Search copy, reduced to the helpers timing_search.py uses. The original lease coordinator and its
production lock (results/.locks) are removed: this search never opens a results/.locks file.
"""
import json
from pathlib import Path

import noise_campaign_engine as execution

BASE = execution.base


def artifact_root(path):
    path = Path(path).resolve()
    if path == BASE.MAIN.resolve() or BASE.MAIN.resolve() in path.parents:
        raise RuntimeError('Refusing to put campaign artifacts in the production worktree')
    return path


def immutable(path, value):
    path = Path(path)
    if path.exists():
        if json.loads(path.read_text()) != value:
            raise RuntimeError('Frozen campaign asset changed: ' + str(path))
    else:
        BASE.write(path, value)


def copy_identity(source, target):
    if target.exists() and target.read_bytes() != source.read_bytes():
        raise RuntimeError('Worker identity differs: ' + str(target))
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())


def verify_activation(art, protocol):
    readiness = json.loads((art / 'readiness.json').read_text())
    if readiness.get('passed') is not True or readiness.get('pending'):
        raise RuntimeError('Native/input/concurrency readiness is incomplete')
    if readiness['protocol_sha256'] != BASE.sha(art / 'protocol.json'):
        raise RuntimeError('Readiness belongs to another protocol')
    if readiness['execution_manifest_sha256'] != BASE.sha(art / 'execution-identity.json'):
        raise RuntimeError('Readiness belongs to another native/code identity')
    wanted = {s['id'] for s in protocol['folds']}
    if set(readiness['studies']) != wanted or not all(
            v.get('ready') is True for v in readiness['studies'].values()):
        raise RuntimeError('Some requested studies have no native validation')
    if readiness['validated_scheduling'] != protocol['scheduling']:
        raise RuntimeError('Proposed concurrency differs from validated scheduling')
    for item in readiness['evidence']:
        if BASE.sha(Path(item['path'])) != item['sha256']:
            raise RuntimeError('Readiness evidence changed: ' + item['path'])
    return readiness


def collect(art, specs):
    for spec in specs:
        directory = art / 'workers' / spec['id']
        for path in (directory / 'attempts').glob('*.json'):
            record = json.loads(path.read_text())
            target = art / 'attempts' / path.name
            if target.exists():
                old = json.loads(target.read_text())
                if old == record:
                    continue
                if old.get('state') == 'finished' or any(
                        old.get(k) != record.get(k) for k in ('key', 'run', 'params', 'campaign_id')):
                    raise RuntimeError('Collected observation identity changed: ' + str(target))
            BASE.write(target, record)
        for path in (directory / 'studies').rglob('*.json'):
            immutable(art / 'studies' / path.relative_to(directory / 'studies'), json.loads(path.read_text()))


def stop_request(art, reason):
    target = art / 'STOP_AFTER_CURRENT'
    if not target.exists():
        target.write_text(reason + '\n')
