#!/usr/bin/env python3
"""Generate the Sielinko a33 Rule C selection: the camera-IMU timing-corrected attempts fill the Sielinko Rule C
VIO (10 systems) and VIO-LC (7 systems) cells of main; every attempt main selected there before goes to the
historical file.

Sources (read only, every one pinned by sha256 in the record):
  campaign  /data/imoroz/sielinko-imu-pilot-20261116: manifests/{full,n3}/manifest.json (repetition, job, run id),
            attempts/run<ID>.json, reviews/run<ID>.json, results/{full-n1,n3}-results.csv (the reviewed tables)
  checkout  /data/imoroz/vslam-sielinko-imu-pilot-20261116: results/.attempt-state (terminal state, identity)
  spec      /data/imoroz/CAMERA-IMU-GNSS-TIMING-ISSUE/imu-pilot/input-views.json (the a33 IMU hashes)
  main      results/repair-20261001/inventory.json of this checkout: the selection each cell replaces (`previous`)
Repetitions: VIO r1 is the full N=1 (63001-63010), r2/r3 the N=3 VIO repetitions (64001-64020); VIO-LC r1-r3 the
N=3 VIO-LC repetitions (65001-65021). Run ids and run paths are kept: the attempts stay under the view
sielinko_imupilot_full_a33 and the record declares that view an alias of field1_110426_full_10fps_q90.
Every listed attempt must be finished, reviewed, terminal, and agree across manifest, record, review and state.

  python -B scripts/campaign/make_sielinko_a33_selection.py [--output PATH]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUTPUT = 'configs/campaigns/sielinko-a33-attempts-20261118.json'
CAMPAIGN = Path('/data/imoroz/sielinko-imu-pilot-20261116')
CHECKOUT = Path('/data/imoroz/vslam-sielinko-imu-pilot-20261116')
SPEC = Path('/data/imoroz/CAMERA-IMU-GNSS-TIMING-ISSUE/imu-pilot/input-views.json')
DATASET, CANONICAL, VIEW = 'zed2i', 'field1_110426_full_10fps_q90', 'sielinko_imupilot_full_a33'
COHORT = 'sielinko-imu-pilot-20261116'
VIO = ('orbslam3', 'okvis2', 'okvis2x', 'airslam', 'basalt', 'openvins', 'voxel_svio', 'cuvslam', 'svo_pro', 'mast3r_fusion')
VIO_LC = ('orbslam3', 'okvis2', 'okvis2x', 'airslam', 'cuvslam', 'svo_pro', 'mast3r_fusion')
TERMINAL = ('evaluated', 'evaluated_failure_or_review', 'no_trajectory', 'evaluation_failed')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path))


def load(path):
    return json.loads(Path(path).read_text())


def table(path):
    return {int(r['run_id']): r for r in csv.DictReader(open(path, newline=''))}


def build(repo=REPO, campaign=CAMPAIGN, checkout=CHECKOUT, spec=SPEC, inventory=None):
    manifests = {name: campaign/f'manifests/{name}/manifest.json' for name in ('full', 'n3')}
    tables = {'full': campaign/'results/full-n1-results.csv', 'n3': campaign/'results/n3-results.csv'}
    reviewed = {**table(tables['full']), **table(tables['n3'])}
    items = []
    for name, path in manifests.items():
        side = path.with_name(path.name+'.sha256')
        if side.is_file() and side.read_text().split()[0] != sha(path):
            raise ValueError('manifest sidecar disagrees: '+str(path))
        for item in load(path)['items']:
            repetition = item.get('repetition', 1) if name == 'n3' else 1
            mode = item.get('mode', 'vio')
            items.append((mode, item['system'], repetition, item, name, path))
    view = load(spec)['views']['a33']['full']
    if view['view'] != VIEW:
        raise ValueError('spec full view is not '+VIEW)
    cells, attempts = {}, {}
    for mode, system, repetition, item, phase, manifest in items:
        key = f'{mode}/{DATASET}/{CANONICAL}/{system}'
        run_id = item['run_id']
        relative = f'{mode}/{DATASET}/{VIEW}/{system}/run{run_id}'
        run = checkout/'results'/relative
        if Path(item['run_dir']) != run or item['variant'] != 'a33' or item.get('attempt') != 1:
            raise ValueError('manifest item is not a first a33 attempt at its run dir: '+item['job_id'])
        record = load(campaign/f'attempts/run{run_id}.json')
        review_path = campaign/f'reviews/run{run_id}.json'
        review = load(review_path)
        state_path = checkout/'results/.attempt-state'/f'{mode}__{DATASET}__{VIEW}__{system}'/f'run{run_id}.json'
        state = load(state_path)
        row = reviewed.get(run_id)
        checks = {
            'record finished': record.get('state') == 'finished' and record.get('job_id') == item['job_id'],
            'record manifest': record.get('manifest_sha256') == sha(manifest),
            'review reviewed': review.get('review_state') == 'reviewed' and review.get('job_id') == item['job_id']
                               and review.get('supersedes') is None,
            'table row reviewed': bool(row) and row['job_id'] == item['job_id'] and row['review_state'] == 'reviewed',
            'state terminal': state.get('status') in TERMINAL,
            'state identity': state.get('identity') == dict(cohort=COHORT, repetition=1, physical_run_id=run_id),
            'run dir': run.is_dir() and (run/'run_meta.json').is_file(),
        }
        if not all(checks.values()):
            raise ValueError(f'{relative}: '+', '.join(k for k, v in checks.items() if not v))
        if repetition in cells.get(key, {}):
            raise ValueError(f'duplicate repetition {repetition} for {key}')
        cells.setdefault(key, {})[repetition] = run_id
        attempts['results/'+relative] = dict(
            cell=key, repetition=repetition, run_id=run_id, job_id=item['job_id'], phase=phase,
            cohort=state['identity']['cohort'], attempt_state=pin(state_path), attempt_record=pin(campaign/f'attempts/run{run_id}.json'),
            review=pin(review_path), reviewed_outcome=dict(valid=row['valid'], eval_status=row['eval_status'],
                                                           native_status=row['native_status'], exit_code=row['exit_code']))
    expected = {f'vio/{DATASET}/{CANONICAL}/{s}' for s in VIO} | {f'vio-lc/{DATASET}/{CANONICAL}/{s}' for s in VIO_LC}
    if set(cells) != expected or any(sorted(v) != [1, 2, 3] for v in cells.values()):
        raise ValueError('the a33 selection must fill exactly the 17 Sielinko VIO/VIO-LC cells with r1-r3')
    inventory = load(inventory or repo/'results/repair-20261001/inventory.json')
    lower = {c['key']: [int(a['path'].rsplit('/run', 1)[1]) for a in c['attempts']] for c in inventory['cells']
             if c['key'] in expected}
    if set(lower) != expected:
        raise ValueError('main inventory lacks a Sielinko VIO/VIO-LC cell')
    return dict(
        schema=1, label='rule_c_sielinko_a33_20261118',
        decision='User go, 16 Nov 2026 ("yes go for n=3 vio + vio lc", confirmed to the runner "please go"): Sielinko Rule C '
                 'VIO and VIO-LC at N=3 on the a33 camera-IMU timing-corrected input. Promotion into main: pending the '
                 "user's OK of PROGRESS/IMU-TIMING-TUNE/PROMOTION-A33.md",
        alias=dict(dataset=DATASET, view=VIEW, canonical=CANONICAL, modes=['vio', 'vio-lc'],
                   meaning='same images and times as the canonical recording; IMU stamps corrected by a33 '
                           '(t - 0.033 s - 5.572e-6 t)',
                   imu0_sha256=view['imu0_sha256'], imu_csv_sha256=view['imu_csv_sha256'], spec=pin(spec)),
        sources=dict(manifests={k: pin(v) for k, v in manifests.items()}, tables={k: pin(v) for k, v in tables.items()}),
        previous={k: lower[k] for k in sorted(expected)},
        cells={k: [cells[k][r] for r in (1, 2, 3)] for k in sorted(expected)},
        attempts=dict(sorted(attempts.items())))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--output', type=Path, default=REPO/OUTPUT)
    ap.add_argument('--inventory', type=Path)
    args = ap.parse_args(argv)
    value = build(inventory=args.inventory)
    args.output.write_text(json.dumps(value, indent=2)+'\n')
    print(f'{args.output}: {len(value["cells"])} cells, {len(value["attempts"])} attempts, sha256 {sha(args.output)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
