#!/usr/bin/env python3
"""Stage evaluations of saved trajectories; never start an estimator or mark COMPLETE.

The staging tree is separate from results/<mode>. Publishing validated staged
evaluations and rebuilding reports are subsequent, explicitly audited operations.
"""
import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _run_type import RUN_TYPES
from _saved_run import atomic_json, evaluate_saved_run, evaluator_identity


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stage', type=Path, required=True)
    ap.add_argument('--mode', choices=RUN_TYPES, action='append')
    ap.add_argument('--limit', type=int)
    args = ap.parse_args()
    ws = Path(__file__).resolve().parents[2]
    stage = args.stage.resolve()
    if any(stage == ws/'results'/mode or (ws/'results'/mode) in stage.parents for mode in RUN_TYPES):
        ap.error('staging must be outside the five source result trees')
    started = time.monotonic()
    identity = evaluator_identity()
    dirs = sorted({p.parent for mode in (args.mode or RUN_TYPES)
                   for name in ('trajectory.txt', 'run_eval.json')
                   for p in (ws/'results'/mode).glob(f'*/*/*/run*/{name}')})
    if args.limit is not None:
        dirs = dirs[:args.limit]
    records = []
    for index, run in enumerate(dirs, 1):
        relative = run.relative_to(ws/'results')
        record = dict(run=str(relative))
        try:
            out, _ = evaluate_saved_run(ws, run)
            if out['evaluation_provenance']['evaluator']['sha256'] != identity['sha256']:
                raise RuntimeError('evaluator source changed during staging; restart with one version')
            atomic_json(stage/'evaluations'/relative/'run_eval.json', out)
            record.update(status='staged', run_status=out['run_status'],
                          ate_se3=out.get('ate_se3', {}).get('rmse'), ate_sim3=out.get('ate', {}).get('rmse'),
                          n_pairs=out.get('n_pairs_ate'), frame_blockers=out['pose_frames']['blockers'])
        except Exception as exc:
            record.update(status='error', error=f'{type(exc).__name__}: {exc}')
        records.append(record)
        atomic_json(stage/'staging_manifest.json', dict(evaluator=identity, expected=len(dirs),
                    processed=index, elapsed_s=time.monotonic()-started, runs=records))
        print(f"[{index}/{len(dirs)}] {relative}: {record['status']} {record.get('run_status', record.get('error', ''))}", flush=True)
    failed = sum(r['status'] == 'error' for r in records)
    print(f'Staged {len(records)-failed}; errors {failed}; {time.monotonic()-started:.1f}s', flush=True)
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
