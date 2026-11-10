"""Shared helpers for the Sielinko N=3 repetition dispatcher (Update 10 B, C, D search).

Nothing in this package starts an estimator on import. Identities follow the frozen
campaign engine (scripts/analysis/noise_campaign_engine.py, identities()) so that a new
repetition gets a fresh, deterministic run ID under a new phase name.
"""
from __future__ import annotations

import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

GIB = 1024 ** 3
PHASE = 'paper_n3'
OUT = Path('/data/imoroz/sielinko-n3-20261110')
LIVE_REPO = Path('/data/imoroz/vslam-benchmark')
DATASET = 'zed2i'
H2 = 'field1_sielinko_h2_20261022'
FULL = 'field1_110426_full_10fps_q90'


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(2 ** 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def dumps(value):
    return json.dumps(value, indent=2, sort_keys=False, allow_nan=False) + '\n'


def write_json(path, value, *, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = dumps(value)
    if exclusive:
        with path.open('x') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        return
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('w') as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def boot_id(path='/proc/sys/kernel/random/boot_id'):
    return Path(path).read_text().strip()


def logical_key(phase, study, label, sequence, mode, repetition):
    return '__'.join((phase, study, label, sequence, mode, 'rep' + str(repetition)))


def run_id(campaign_id, key):
    """noise_campaign_engine.identities(): 2e9 + first 10 hex digits of sha256(campaign:key)."""
    return 2_000_000_000 + int(hashlib.sha256((campaign_id + ':' + key).encode()).hexdigest()[:10], 16)


def native_seed(campaign_id, study, sequence, phase, repetition):
    """noise_campaign_engine.identities(): common random numbers across labels, per phase/repetition."""
    return int(hashlib.sha256(':'.join((campaign_id, study, sequence, phase, str(repetition))).encode()).hexdigest()[:8], 16)


def unit_name(campaign_id, rid):
    """noise_execution_policy.bounded_command(): the transient scope that owns the attempt."""
    return 'noise-campaign-' + hashlib.sha256(campaign_id.encode()).hexdigest()[:12] + '-' + str(rid)


def run_dir(root, mode, dataset, sequence, algorithm, rid):
    return Path(root) / 'results' / mode / dataset / sequence / algorithm / ('run' + str(rid))


def config_environment_names(engine_path):
    """The engine's CONFIG_ENVIRONMENT tuple, read from the frozen source without importing it."""
    tree = ast.parse(Path(engine_path).read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, 'id', None) == 'CONFIG_ENVIRONMENT' for t in node.targets):
            return list(ast.literal_eval(node.value))
    raise RuntimeError('CONFIG_ENVIRONMENT not found in ' + str(engine_path))


def load_frozen_module(path, name):
    """Import one stdlib-only module from a frozen worktree under a unique name, writing no bytecode."""
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def manifest_sidecar(path):
    return Path(str(path) + '.sha256')


def verify_manifest(path, expected=None):
    """The manifest must equal its sidecar hash and, when given, the reviewed hash."""
    path = Path(path)
    actual = sha(path)
    sidecar = manifest_sidecar(path)
    if not sidecar.is_file():
        raise RuntimeError('Manifest hash sidecar missing: ' + str(sidecar))
    recorded = sidecar.read_text().split()[0]
    if recorded != actual:
        raise RuntimeError('Manifest changed since it was frozen (sidecar ' + recorded + ', now ' + actual + ')')
    if expected is not None and expected != actual:
        raise RuntimeError('Manifest differs from the reviewed hash ' + expected)
    return load(path), actual
