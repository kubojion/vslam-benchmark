#!/usr/bin/env python3
"""Fail-closed guard for a main apply while the Sielinko a33 extended search may run.

Takes a snapshot of everything the search reads from live main, before and after the apply; they must be
identical. Read only, except the scratch blob store of the frozen capture_tree and, on a difference, the search's
FAULT file (create-only), which makes the search's next attempt refuse.

  snapshot --out FILE [--scratch DIR] [--deep]     exit 2 if a pinned file already differs from its pin
  compare BEFORE AFTER [--fault PATH]               exit 0 identical; exit 3 different (FAULT written)
  fullgate --out FILE --scratch DIR                 the search's own full identity gate per system; exit 4 on a failure

What is covered (from the search's own manifests, STATE/manifests/*/manifest.json):
  native   per system: the algorithm source tree exactly as the search's FULL identity gate sees it (its frozen
           imu_pilot.identity.algorithm_tree -> scripts/run/_capture_implementation.capture_tree of the search
           checkout's src/<native>, a link to live src) and its runtime identity (imu_pilot.identity.runtime_identity
           -> scripts/run/_capture_runtime.identity, with the item environment);
  views    every search view: each entry and link target (live datasets/zed2i camera data, times, manifest); linked
           directories (the camera image trees) by stat fingerprint (path, size, mtime_ns, ctime_ns, mode; any write changes ctime), every
           other file by sha256; --deep hashes the images too (~72 GB);
  pinned   the manifests' pinned evidence and each template's historical r1 provenance (implementation, runtime,
           inputs) and r1 config files, by sha256 against their pins;
  cache    live main's results/.cache/input-content.sqlite (and -wal/-shm); the search checkout's own cache is excluded
           because the search itself writes it.
Why it is mandatory: the search's LIGHT gate (every attempt) re-checks only its checkout HEAD, the pinned evidence,
candidate configs, the view IMU and container identity; the FULL gate (native trees, runtime assets, evaluator)
runs only on each system's first run per boot per phase. A native-tree change mid-phase would not be caught.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
STATE = Path('/data/imoroz/sielinko-search-a33-20261117')
LIVE = Path('/data/imoroz/vslam-benchmark')
CACHE = 'results/.cache/input-content.sqlite'


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), default=str).encode()).hexdigest()


def manifests(state=STATE):
    """The search's current phase manifests (superseded copies are history, not inputs)."""
    return sorted(p for p in (state/'manifests').glob('*/manifest.json') if '.superseded' not in p.parent.name)


def file_record(path, deep=True):
    st = os.stat(path)
    # No inode number: an overlay (the dry-run sandbox) reports its own; any write still moves ctime/mtime/size.
    record = dict(size=st.st_size, mtime_ns=st.st_mtime_ns, ctime_ns=st.st_ctime_ns, mode=st.st_mode)
    if deep:
        record['sha256'] = sha(path)
    return record


def tree_record(root, deep):
    """Every file under root (links followed once at the root only), by stat and optionally content."""
    entries = {}
    for base, dirs, files in os.walk(root):
        dirs.sort()
        for name in sorted(files):
            p = Path(base)/name
            entries[str(p.relative_to(root))] = file_record(p, deep)
    return dict(files=len(entries), digest=canonical(entries), dir=file_record(root, False))


def view_record(view_dir, deep):
    out = {}
    for base, dirs, files in os.walk(view_dir):
        for name in sorted(dirs + files):
            p = Path(base)/name
            rel = str(p.relative_to(view_dir))
            if p.is_symlink():
                target = os.readlink(p)
                resolved = p.resolve()
                entry = dict(link=target, resolved=str(resolved))
                if resolved.is_dir():                   # linked directories are the camera image trees
                    entry['tree'] = tree_record(resolved, deep)
                elif resolved.is_file():
                    entry['file'] = file_record(resolved)
                out[rel] = entry
            elif p.is_file():
                out[rel] = dict(file=file_record(p))
        dirs[:] = [d for d in dirs if not (Path(base)/d).is_symlink()]
    return out


def pinned_entries(manifest, checkout):
    entries = [dict(e, source='pinned_evidence') for e in manifest.get('pinned_evidence', [])]
    for name, template in sorted(manifest.get('templates', {}).items()):
        for role, item in sorted(template['reference']['provenance'].items()):
            entries.append(dict(role=f'{name} r1 {role}', path=item['path'], sha256=item['sha256'], source='r1_provenance'))
        for item in template['config']['files']:
            path = Path(item['path'])
            entries.append(dict(role=f"{name} {item['role']}", path=str(path if path.is_absolute() else Path(checkout)/path),
                                sha256=item['sha256'], source='r1_config'))
    return entries


def native_records(manifest, scratch, tree=None, runtime=None):
    """Per template system: the frozen full-gate tree and runtime identity, computed once per (system, source), and
    (with the real gate code) the full gate's own comparison of both with the historical Rule C r1 provenance."""
    checkout = manifest['checkout']['path']
    gate = None
    if tree is None or runtime is None:
        sys.path.insert(0, str(Path(checkout)/'scripts/analysis'))
        from imu_pilot import identity                      # the search's frozen gate code, read only
        tree = tree or identity.algorithm_tree
        runtime = runtime or identity.runtime_identity
        gate = identity
    out = {}
    for name, template in sorted(manifest.get('templates', {}).items()):
        algorithm = name.split('/')[0]
        if algorithm in out:
            continue
        env = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME', 'LANG') if k in os.environ}
        env.update(template.get('environment_base', {}))
        env.update(template['config'].get('environment', {}))
        env.update((template.get('container') or {}).get('environment', {}))
        record = dict(source_rel=template['native'].get('source_rel'))
        try:
            reference = template['reference']['provenance']
            if record['source_rel']:
                live = tree(checkout, record['source_rel'], scratch, manifest['helper_python'])
                record['tree_digest'] = canonical({k: live.get(k) for k in ('path', 'commit', 'scope', 'entries')})
                record['tree_entries'] = len(live.get('entries') or [])
                if gate is not None and reference.get('implementation'):
                    record['full_gate_tree_equals_r1'] = gate.compare_algorithm_tree(
                        live, json.loads(Path(reference['implementation']['path']).read_text()))[0]
            identity_value = runtime(checkout, algorithm, manifest['helper_python'], env)
            record['runtime_digest'] = canonical({k: v for k, v in identity_value.items() if k != 'sha256'})
            if gate is not None:
                record['full_gate_runtime_equals_r1'] = gate.compare_runtime(
                    identity_value, json.loads(Path(reference['runtime']['path']).read_text()),
                    private_container=bool(template.get('container')))[0]
        except Exception as exc:  # noqa: BLE001  an unreadable identity is recorded; compare treats it as data
            record['error'] = f'{type(exc).__name__}: {exc}'[:500]
        out[algorithm] = record
    return out


def snapshot(state=STATE, live=LIVE, scratch=None, deep=False, tree=None, runtime=None):
    if scratch is None:
        raise ValueError('a scratch blob store outside every campaign folder is required')
    result = dict(schema=1, taken_at=datetime.now(timezone.utc).isoformat(), state=str(state), deep=deep,
                  manifests={}, native={}, views={}, pinned={}, cache={}, pin_mismatches=[])
    checkouts = set()
    for path in manifests(state):
        manifest = json.loads(path.read_text())
        result['manifests'][str(path)] = sha(path)
        checkout = manifest['checkout']['path']
        checkouts.add(checkout)
        for system, record in native_records(manifest, scratch, tree, runtime).items():
            result['native'].setdefault(system, record)
        for view in manifest.get('views', {}).values():
            if view['dir'] not in result['views']:
                result['views'][view['dir']] = view_record(Path(view['dir']), deep)
        for entry in pinned_entries(manifest, checkout):
            p = Path(entry['path'])
            actual = sha(p) if p.is_file() else None
            result['pinned'][entry['path']] = dict(role=entry['role'], source=entry['source'], pinned=entry['sha256'], actual=actual)
            if actual != entry['sha256']:
                result['pin_mismatches'].append(entry['path'])
    # Live main's input-content cache only: the search checkout's own cache changes with the search's own runs.
    for root in [Path(live)]:
        for suffix in ('', '-wal', '-shm'):
            p = root/(CACHE+suffix)
            result['cache'][str(p)] = file_record(p) if p.is_file() else None
    result['pin_mismatches'] = sorted(set(result['pin_mismatches']))
    return result


def differences(before, after, path=''):
    if isinstance(before, dict) and isinstance(after, dict):
        out = []
        for key in sorted(set(before) | set(after)):
            if not path and key in ('taken_at',):
                continue
            out += differences(before.get(key), after.get(key), f'{path}/{key}')
        return out
    return [] if before == after else [dict(path=path, before=before, after=after)]


def compare(before, after, fault=None):
    diff = differences(before, after)
    if diff and fault is not None:
        fault = Path(fault)
        text = json.dumps(dict(schema=1, kind='main_apply_guard', at=datetime.now(timezone.utc).isoformat(),
                               reason='live-main inputs of the a33 search changed during a main apply; the next attempt '
                                      'must refuse until the lead and the user have reviewed',
                               differences=diff[:200], count=len(diff)), indent=1, default=str)+'\n'
        try:
            with fault.open('x') as stream:            # create-only: an existing FAULT is never replaced
                stream.write(text)
        except FileExistsError:
            pass
    return diff


def full_gates(state=STATE, scratch=None):
    """The search's own FULL identity gate (imu_pilot.identity.full_gate), once per system, read only (scratch blobs):
    the light checks (checkout HEAD, pinned evidence, r1 configs, view IMU, container identity) plus the native tree,
    runtime assets and evaluator probe against the historical r1 provenance. Items are built from the manifests'
    templates; the view is the manifest's first view."""
    if scratch is None:
        raise ValueError('a scratch blob store outside every campaign folder is required')
    results = {}
    for path in manifests(state):
        manifest = json.loads(path.read_text())
        sys.path.insert(0, str(Path(manifest['checkout']['path'])/'scripts/analysis'))
        from imu_pilot import identity
        view = next(iter(manifest['views'].values()))
        for name, template in sorted(manifest.get('templates', {}).items()):
            algorithm = name.split('/')[0]
            if algorithm in results:
                continue
            env = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME', 'LANG') if k in os.environ}
            env.update(template.get('environment_base', {})); env.update(template['config'].get('environment', {}))
            item = dict(template, algorithm=algorithm, checkout=manifest['checkout'], pinned_evidence=manifest['pinned_evidence'],
                        view=dict(imu0=view['imu0'], expected_imu0_sha256=view['expected_imu0_sha256']))
            gate = identity.full_gate(item, manifest['helper_python'], Path(scratch), env=env)
            results[algorithm] = dict(passed=gate.passed, template=name, manifest=str(path),
                                      checks=len(gate.checks), failures=gate.failures())
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='command', required=True)
    s = sub.add_parser('snapshot'); s.add_argument('--out', type=Path, required=True)
    s.add_argument('--scratch', type=Path, required=True, help='blob store of capture_tree; never a campaign folder')
    s.add_argument('--deep', action='store_true')
    s.add_argument('--state', type=Path, default=STATE)
    g = sub.add_parser('fullgate'); g.add_argument('--out', type=Path, required=True)
    g.add_argument('--scratch', type=Path, required=True); g.add_argument('--state', type=Path, default=STATE)
    c = sub.add_parser('compare'); c.add_argument('before', type=Path); c.add_argument('after', type=Path)
    c.add_argument('--fault', type=Path, default=STATE/'FAULT')
    args = ap.parse_args(argv)
    if args.command == 'snapshot':
        value = snapshot(args.state, scratch=args.scratch, deep=args.deep)
        if args.out.exists():
            raise SystemExit('refusing to overwrite '+str(args.out))
        args.out.write_text(json.dumps(value, indent=1, sort_keys=True, default=str)+'\n')
        errors = [s for s, r in value['native'].items() if 'error' in r]
        print(f"{args.out}: {len(value['native'])} systems, {len(value['views'])} views, {len(value['pinned'])} pinned files, "
              f"{sum(v is not None for v in value['cache'].values())} cache files; pin mismatches {len(value['pin_mismatches'])}; "
              f"native errors {errors}")
        return 2 if value['pin_mismatches'] else 0
    if args.command == 'fullgate':
        value = full_gates(args.state, args.scratch)
        args.out.write_text(json.dumps(value, indent=1, default=str)+'\n')
        print(json.dumps({k: v['passed'] for k, v in value.items()}), f"{sum(v['passed'] for v in value.values())}/{len(value)} pass")
        return 0 if value and all(v['passed'] for v in value.values()) else 4
    diff = compare(json.loads(args.before.read_text()), json.loads(args.after.read_text()), args.fault)
    print(json.dumps(dict(identical=not diff, differences=len(diff), first=diff[:5], fault=str(args.fault) if diff else None), indent=1, default=str))
    return 3 if diff else 0


if __name__ == '__main__':
    raise SystemExit(main())
