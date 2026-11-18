#!/usr/bin/env python3
"""Stage schema-3 re-evaluations of every saved Sielinko run after a reference change (repaired-evaluation route).

Runs: every results/<mode>/zed2i/field1_110426_full_10fps_q90/<algo>/run* with a saved trajectory, plus the
attempts of the a33 alias record (configs/campaigns/sielinko-a33-attempts-20261118.json) that have one. Each is
evaluated with the frozen evaluator against the reference its selector names now, reviewed (apply_review) and
written ONLY to the staging tree results/repair-20261001/evaluations/<run>/run_eval.json; an earlier staged file is
preserved first (content-addressed .evaluation_history beside it). Run folders are never written here: publishing
is promote_repaired_evaluations.py --apply --only <this manifest>. Never starts an estimator or marks COMPLETE.

  python -B scripts/eval/stage_reference_reevaluation.py [--workers 4]
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _saved_run import atomic_json, evaluate_saved_run, evaluator_identity  # noqa: E402
from _evaluate_run import preserve_evaluation  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'campaign'))
from qualification_review import apply_review  # noqa: E402

WS = Path(__file__).resolve().parents[2]
STAGE = WS/'results/repair-20261001'
MANIFEST = 'reference-v4-staging-manifest.json'
DATASET, SEQUENCE = 'zed2i', 'field1_110426_full_10fps_q90'
ALIAS_RECORD = 'configs/campaigns/sielinko-a33-attempts-20261118.json'
MODES = ('vo', 'vo-lc', 'vio', 'vio-lc', 'gnss-vio')


def runs(ws=WS):
    found = {p for mode in MODES for p in (ws/'results'/mode/DATASET/SEQUENCE).glob('*/run*') if p.is_dir()}
    record = ws/ALIAS_RECORD
    if record.is_file():
        found |= {ws/a for a in json.loads(record.read_text())['attempts']}
    return sorted(found)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).is_file() else None


def stage_one(run):
    ws = WS
    relative = run.relative_to(ws/'results')
    record = dict(run=str(relative), published_sha256=digest(run/'run_eval.json'))
    if not (run/'trajectory.txt').is_file():
        record.update(status='skipped_no_trajectory')
        return record
    try:
        out, _ = evaluate_saved_run(ws, run)
        apply_review(ws, run, out)
        target = STAGE/'evaluations'/relative/'run_eval.json'
        preserve_evaluation(target)
        atomic_json(target, out)
        old = json.loads((run/'run_eval.json').read_text()) if (run/'run_eval.json').is_file() else {}
        record.update(status='staged', staged=str(target.relative_to(ws)), staged_sha256=digest(target),
                      evaluator=out['evaluation_provenance']['evaluator']['sha256'],
                      reference_version=out['pose_frames'].get('reference_version'),
                      previous_reference_version=old.get('pose_frames', {}).get('reference_version'),
                      run_status=out['run_status'], previous_run_status=old.get('run_status'),
                      ate_se3=out.get('ate_se3', {}).get('rmse'), ate_sim3=out.get('ate', {}).get('rmse'),
                      scale_factor=out.get('scale_factor'), n_pairs=out.get('n_pairs_ate'),
                      previous_ate_se3=old.get('ate_se3', {}).get('rmse'),
                      qualification=out['qualification'].get('status'),
                      previous_qualification=old.get('qualification', {}).get('status'))
    except Exception as exc:  # noqa: BLE001  recorded, and the command exits 1
        record.update(status='error', error=f'{type(exc).__name__}: {exc}')
    return record


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--workers', type=int, default=4)
    args = ap.parse_args(argv)
    started = time.monotonic()
    identity = evaluator_identity()
    targets = runs()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        records = list(pool.map(stage_one, targets))
    if any(r.get('evaluator') not in (None, identity['sha256']) for r in records):
        raise SystemExit('evaluator source changed during staging; restart with one version')
    failed = sum(r['status'] == 'error' for r in records)
    atomic_json(STAGE/MANIFEST, dict(schema=1, evaluator=identity, dataset=DATASET, sequence=SEQUENCE,
                                     alias_record=dict(path=ALIAS_RECORD, sha256=digest(WS/ALIAS_RECORD)),
                                     expected=len(targets), staged=sum(r['status'] == 'staged' for r in records),
                                     skipped=sum(r['status'].startswith('skipped') for r in records), errors=failed,
                                     elapsed_s=time.monotonic()-started, runs=records))
    print(f'staged {sum(r["status"] == "staged" for r in records)} of {len(targets)}; '
          f'skipped {sum(r["status"].startswith("skipped") for r in records)}; errors {failed}; {time.monotonic()-started:.0f}s')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
