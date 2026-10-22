#!/usr/bin/env python3
"""Copy the main checkout's native source/build trees for the Sielinko CPU search.

Adapted from the earlier search's prepare_private_sources.py: independent Git
object copies (never hardlinks), dirty sources and existing build artifacts
preserved, the source tree checked unchanged before and after. Nothing is
built or executed. Run only with the user's go and while no run uses main.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess

MAIN = Path('/data/imoroz/vslam-benchmark')
ROOT = Path(__file__).resolve().parents[2]
# The seven CPU estimators; Basalt is the installed binary, outside the checkout.
NAMES = ['ORB_SLAM3', 'okvis2', 'okvis2x', 'open_vins', 'svo_pro', 'voxel_svio']
REPORT = ROOT / 'results/sielinko-private-sources.json'


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()


def runs_using_main():
    """PIDs of benchmark wrappers launched from the main checkout."""
    found = []
    for entry in Path('/proc').iterdir():
        if entry.name.isdigit():
            try:
                argv = (entry / 'cmdline').read_bytes().decode(errors='replace').split('\0')
            except OSError:
                continue
            if any(re.fullmatch(re.escape(str(MAIN)) + r'/scripts/run/run_[a-z0-9_]+\.sh', a) for a in argv[:3]):
                found.append(int(entry.name))
    return found


def clone(source, destination, log):
    if destination.exists() and any(destination.iterdir()):
        raise RuntimeError('Refusing to replace an existing source tree: ' + str(destination))
    subprocess.run(['git', 'clone', '--no-hardlinks', '--no-checkout', '--', str(source), str(destination)],
                   stdout=log, stderr=subprocess.STDOUT, check=True)
    head = git(source, 'rev-parse', 'HEAD')
    subprocess.run(['git', '-C', str(destination), 'checkout', '--detach', head],
                   stdout=log, stderr=subprocess.STDOUT, check=True)
    return dict(source=str(source), destination=str(destination), head=head)


def main():
    if ROOT.resolve() == MAIN.resolve():
        raise RuntimeError('run only from the isolated search checkout')
    if REPORT.exists():
        raise RuntimeError('Private source preparation already recorded; review before changing it')
    active = runs_using_main()
    if active:
        raise RuntimeError('Runs from main are active; copy at a boundary: ' + str(active))
    records = []
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.with_suffix('.log').open('x') as log:
        for name in NAMES:
            source, destination = MAIN / 'src' / name, ROOT / 'src' / name
            before = git(source, 'status', '--porcelain=v1', '--untracked-files=all')
            item = clone(source, destination, log)
            item['children'] = []
            for row in git(source, 'submodule', 'status', '--recursive').splitlines():
                if not row.strip():
                    continue
                relative = row.split()[1]  # submodule paths in these trees contain no whitespace
                if row.startswith('-'):
                    raise RuntimeError('Native dependency source is uninitialized: ' + relative)
                item['children'].append(clone(source / relative, destination / relative, log))
            subprocess.run(['rsync', '-a', '--exclude=.git', '--exclude=__pycache__',
                            str(source) + '/', str(destination) + '/'],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
            if git(source, 'status', '--porcelain=v1', '--untracked-files=all') != before:
                raise RuntimeError('Source tree changed during private copy: ' + name)
            item['original_status'] = before
            item['private_status'] = git(destination, 'status', '--porcelain=v1', '--untracked-files=all')
            # Absolute links back into main mean the copy would still read main's files.
            item['absolute_main_symlinks'] = [dict(path=str(p.relative_to(destination)), target=str(p.readlink()))
                                              for p in destination.rglob('*')
                                              if p.is_symlink() and str(p.readlink()).startswith(str(MAIN))]
            records.append(item)
            print(json.dumps(dict(prepared=name, nested_repositories=len(item['children']),
                                  main_symlinks=len(item['absolute_main_symlinks']))), flush=True)
    REPORT.write_text(json.dumps(dict(prepared_utc=datetime.now(timezone.utc).isoformat(),
        independent_git_objects=True, hardlinks_used=False, estimators_started=False, records=records,
        dependency_resolution_verification_pending=True), indent=2) + '\n')


if __name__ == '__main__':
    main()
