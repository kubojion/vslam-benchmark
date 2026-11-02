#!/usr/bin/env python3
"""Record native source state that a commit alone cannot reproduce, for PLAN Update 6 Job C. Read-only.

For each estimator's source tree, and each submodule nested in it: the recorded commit, the checked-out commit,
git status, the diff against the checked-out commit, the diff from the recorded commit when they differ, and the
size and SHA-256 of every untracked file. Roots are the live checkout, which the search's src/ links point to,
and the first search's run worktree. No git command here takes a lock (GIT_OPTIONAL_LOCKS=0).
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / 'docs/campaigns/imu-timing-search-20261031/native-sources'
ROOTS = {'live': Path('/data/imoroz/vslam-benchmark'),
         'first-search': Path('/data/imoroz/vslam-noise-reliable-20261009')}
TREES = ('ORB_SLAM3', 'okvis2', 'okvis2x', 'open_vins', 'voxel_svio', 'svo_pro', 'cuvslam', 'airslam', 'mast3r_fusion')
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')


def git(path, *args, check=True):
    done = subprocess.run(['git', '-C', str(path), *args], capture_output=True, env=ENV, timeout=300)
    if check and done.returncode:
        raise RuntimeError(f'git {args} failed in {path}: {done.stderr.decode(errors="replace")}')
    return done.stdout


def text(path, *args):
    return git(path, *args).decode(errors='replace').strip()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(2**20), b''):
            h.update(chunk)
    return h.hexdigest()


def gitlinks(path):
    links = []
    for row in text(path, 'ls-files', '--stage').splitlines():
        head, name = row.split('\t', 1)
        mode, oid, _ = head.split()
        if mode == '160000':
            links.append((name, oid))
    return links


def save(root_label, label, kind, data):
    if not data:
        return None
    folder = TARGET / root_label
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"{label.replace('/', '__')}.{kind}.diff"
    target.write_bytes(data)
    return dict(path=str(target.relative_to(ROOT)), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def capture(root_label, path, label, recorded):
    if not (path / '.git').exists():
        return dict(tree=label, recorded=recorded, available=False)
    head = text(path, 'rev-parse', 'HEAD')
    status = text(path, 'status', '--porcelain=v1', '--untracked-files=all', '--ignore-submodules=none').splitlines()
    untracked = []
    for name in git(path, 'ls-files', '--others', '--exclude-standard', '-z').split(b'\0'):
        if name:
            file = path / os.fsdecode(name)
            untracked.append(dict(path=os.fsdecode(name), bytes=file.stat().st_size, sha256=digest(file)))
    record = dict(tree=label, recorded=recorded, head=head, at_recorded=recorded in (None, head), status=status,
                  worktree_diff=save(root_label, label, 'worktree', git(path, 'diff', 'HEAD', '--binary')), untracked=untracked)
    if recorded not in (None, head):
        record['recorded_to_head_diff'] = save(root_label, label, 'recorded-to-head',
                                               git(path, 'diff', '--binary', recorded, head, check=False))
    record['submodules'] = [capture(root_label, path / name, f'{label}/{name}', oid) for name, oid in gitlinks(path)]
    return record


def main():
    report = dict(schema=1, purpose=__doc__.splitlines()[0], branch_base='b653776', roots={})
    for label, root in ROOTS.items():
        recorded = {name: oid for name, oid in gitlinks(root)}
        report['roots'][label] = dict(path=str(root), head=text(root, 'rev-parse', 'HEAD'), trees=[
            capture(label, root / 'src' / name, name, recorded.get('src/' + name)) for name in TREES])
    TARGET.mkdir(parents=True, exist_ok=True)
    (TARGET / 'index.json').write_text(json.dumps(report, indent=1) + '\n')
    dirty = [f"{label}:{t['tree']}" for label, r in report['roots'].items() for t in r['trees'] if t.get('status')]
    print(json.dumps(dict(index=str(TARGET / 'index.json'), dirty=dirty), indent=1))


if __name__ == '__main__':
    main()
