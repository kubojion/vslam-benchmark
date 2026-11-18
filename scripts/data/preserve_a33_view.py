#!/usr/bin/env python3
"""Preserve the a33 camera-IMU timing-corrected Sielinko input in main, add-only (as Job A's datasets/.timing-imu).

From the pilot checkout's view (read only), each file checked against input-views.json:
  datasets/.timing-imu/zed2i__field1_110426_full_10fps_q90/a33/{data.csv,imu.csv,record.json}
and the alias view the a33 runs name (datasets/zed2i/sielinko_imupilot_full_a33/), relative links only:
  times.txt (tracked; equal to the canonical times), manifest.json, cam0/cam1/left/right, mav0/cam0, mav0/cam1 ->
  the canonical recording; mav0/imu0/data.csv and imu.csv -> the preserved copies.
Create-once: an existing path is accepted only if it is already exactly the intended file or link; nothing in the
canonical recording is touched.

  python -B scripts/data/preserve_a33_view.py [--check]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil

REPO = Path(__file__).resolve().parents[2]
SPEC = Path('/data/imoroz/CAMERA-IMU-GNSS-TIMING-ISSUE/imu-pilot/input-views.json')
SPEC_SHA256 = '1526f6ed0651c8d684e900e6647e62f5796af070aeb92676b082c07d7104f78b'
MODEL = Path('/data/imoroz/CAMERA-IMU-GNSS-TIMING-ISSUE/imu-pilot/model-variants.json')
SOURCE = Path('/data/imoroz/vslam-sielinko-imu-pilot-20261116/datasets/zed2i/sielinko_imupilot_full_a33')
CANONICAL, VIEW = 'field1_110426_full_10fps_q90', 'sielinko_imupilot_full_a33'
KEEP = f'datasets/.timing-imu/zed2i__{CANONICAL}/a33'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def plan():
    if sha(SPEC) != SPEC_SHA256:
        raise RuntimeError('input-views.json differs from its pin')
    view = json.loads(SPEC.read_text())['views']['a33']['full']
    model = json.loads(MODEL.read_text())
    canonical = REPO/'datasets/zed2i'/CANONICAL
    imu0, imu_csv = SOURCE/'mav0/imu0/data.csv', SOURCE/'imu.csv'
    if view['view'] != VIEW or sha(imu0) != view['imu0_sha256'] or sha(imu_csv) != view['imu_csv_sha256']:
        raise RuntimeError('pilot a33 IMU differs from input-views.json')
    record = dict(dataset='zed2i', sequence=CANONICAL, variant='a33', view=VIEW,
                  a_ms=model['variants']['a33']['a_ms'], slope_ppm=model['slope']['ppm'], formula=model['formula'],
                  source=dict(imu0=str(canonical/'mav0/imu0/data.csv'), imu0_sha256=sha(canonical/'mav0/imu0/data.csv'),
                              imu_csv=str(canonical/'imu.csv'), imu_csv_sha256=sha(canonical/'imu.csv')),
                  copied_from=str(SOURCE), output_sha256=view['imu0_sha256'], imu_csv_sha256=view['imu_csv_sha256'],
                  samples=view['rows'], spec=dict(path=str(SPEC), sha256=SPEC_SHA256),
                  model=dict(path=str(MODEL), sha256=sha(MODEL)), applied=True)
    copies = {f'{KEEP}/data.csv': imu0, f'{KEEP}/imu.csv': imu_csv}
    files = {f'{KEEP}/record.json': (json.dumps(record, indent=1)+'\n').encode()}
    up = f'../../{CANONICAL}'
    links = {f'datasets/zed2i/{VIEW}/{name}': target for name, target in (
        ('manifest.json', f'../{CANONICAL}/manifest.json'), ('cam0', 'mav0/cam0/data'), ('cam1', 'mav0/cam1/data'),
        ('left', 'mav0/cam0/data'), ('right', 'mav0/cam1/data'), ('mav0/cam0', f'{up}/mav0/cam0'),
        ('mav0/cam1', f'{up}/mav0/cam1'), ('mav0/imu0/data.csv', f'../../../../.timing-imu/zed2i__{CANONICAL}/a33/data.csv'),
        ('imu.csv', f'../../.timing-imu/zed2i__{CANONICAL}/a33/imu.csv'))}
    return copies, files, links, view


def apply(check=False, repo=REPO):
    copies, files, links, view = plan()
    actions = {}
    times = repo/f'datasets/zed2i/{VIEW}/times.txt'
    if not times.is_file() or times.read_bytes() != (repo/f'datasets/zed2i/{CANONICAL}/times.txt').read_bytes():
        raise RuntimeError('the alias view times.txt (tracked) must exist and equal the canonical times')
    for rel, source in copies.items():
        path = repo/rel
        if path.exists():
            if path.is_symlink() or sha(path) != sha(source):raise RuntimeError('refusing to replace '+rel)
            actions[rel] = 'same'; continue
        actions[rel] = 'would copy' if check else 'copied'
        if not check:
            path.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, path)
            if sha(path) != sha(source):raise RuntimeError('copy verification failed: '+rel)
    for rel, data in files.items():
        path = repo/rel
        if path.exists():
            if path.read_bytes() != data:raise RuntimeError('refusing to replace '+rel)
            actions[rel] = 'same'; continue
        actions[rel] = 'would write' if check else 'written'
        if not check:
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
    for rel, target in links.items():
        path = repo/rel
        if path.is_symlink():
            if os.readlink(path) != target:raise RuntimeError('existing link differs: '+rel)
            actions[rel] = 'same'; continue
        if path.exists():raise RuntimeError('refusing to replace '+rel)
        actions[rel] = 'would link' if check else 'linked'
        if not check:
            path.parent.mkdir(parents=True, exist_ok=True); os.symlink(target, path)
    if not check:
        imu = repo/f'datasets/zed2i/{VIEW}/mav0/imu0/data.csv'
        if sha(imu) != view['imu0_sha256'] or sha(repo/f'datasets/zed2i/{VIEW}/imu.csv') != view['imu_csv_sha256']:
            raise RuntimeError('alias view IMU does not resolve to the preserved a33 copy')
    return actions


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args(argv)
    actions = apply(check=args.check)
    for rel, action in actions.items():
        print(action, rel)
    return 1 if args.check and any(a != 'same' for a in actions.values()) else 0


if __name__ == '__main__':
    raise SystemExit(main())
