#!/usr/bin/env python3
"""Generate checked outcome counts and limitations, without canned scientific claims."""
import argparse
from collections import Counter
from pathlib import Path

from build_benchmark_csv import REPO, RUN_TYPES, preserved_write
from _report_data import checked_rows, cells


def render(rows, inputs):
    lines = ['# Reconciled evidence counts', '',
        'Generated from hash-checked schema-3 evaluations and matching CSVs. These are inventory '
        'facts, not certification of scientific claims. Numerical `ok` is separate from '
        'execution, calibration, reference validity and publication qualification.', '',
        '| Mode | Planned defaults | Evaluated | Numerical ok | Scale collapse | Invalid trajectory | Nonzero exits | Qualified clean N=3 cells |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for mode in RUN_TYPES:
        group = [r for r in rows if r['run_type'] == mode and r['gnss_variant'] == 'default']
        counts = Counter(r['run_status'] for r in group)
        n3 = sum(s['clean_qualified_n3'] for _, _, s in cells(group))
        lines.append(f"| {mode} | {len(group)} | {sum(r['eval_schema'] == 3 for r in group)} | "
            f"{counts['ok']} | {counts['scale_collapse']} | {counts['eval_failed']} | "
            f"{sum(r['process_exit_code'] not in (0, None) for r in group)} | {n3} |")
    variants = [r for r in rows if r['gnss_variant'] != 'default']
    statuses = Counter(r['scientific_status'] for r in rows if r['attempt_exists'])
    lines += ['', f'Legacy GNSS variants: {len(variants)} separate rows; not included in default repetition counts.', '',
        'Scientific statuses among existing headline attempts: ' + ', '.join(f'{k}={v}' for k,v in sorted(statuses.items())) + '.', '',
        '## Retained adverse outcomes', '',
        '| Run | Numerical status | Exit | Scientific status |', '|---|---|---:|---|']
    for row in rows:
        if row['run_status'] not in ('ok', 'missing') or row['process_exit_code'] not in (None, 0):
            lines.append(f"| `{row['run_path']}` | {row['run_status']} | {row['process_exit_code'] if row['process_exit_code'] is not None else 'unknown'} | {row['scientific_status']} |")
    lines += ['', '## Claim boundaries', '',
        '- Primary ATE is SE(3) for metric stereo/inertial methods and Sim(3) for monocular DPVO. No cross-scale winner is inferred.',
        '- Conditional accuracy in the tables excludes numerical failures from the score calculation only; all failures and missing repetitions remain in the denominator. Distinct cohorts and GNSS variants are separate.',
        '- AirSLAM keyframe density does not measure tracking loss or processed-image throughput. Exported-pose coverage and reference-supported score coverage have separate fields.',
        '- Nominal input divided by elapsed time is not measured estimator processing speed or real-time latency.',
        '- Mode comparisons alone do not establish that excitation or a particular loop mechanism caused an error. Reference, config and final-optimization differences must be resolved before drawing those conclusions.',
        '- Aligned GNSS shape error is not absolute global positioning accuracy. Historical input/reference independence remains unqualified.', '',
        '## Source identities', '', '| Source | SHA-256 |', '|---|---|']
    lines += [f"| `{Path(item['path']).name}` | `{item['sha256']}` |" for item in inputs]
    return '\n'.join(lines)+'\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--inventory', type=Path, default=REPO/'results/repair-20261001/inventory.json')
    ap.add_argument('--csv-dir', type=Path, default=REPO)
    ap.add_argument('--output', type=Path, default=REPO/'docs/generated/verified-claims.md')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    rows, inputs = checked_rows(args.inventory, args.csv_dir)
    content = render(rows, inputs)
    if args.check:
        return not args.output.is_file() or args.output.read_text() != content
    preserved_write(args.output, content)
    print(f'[claims] Reconciled counts and claim boundaries -> {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
