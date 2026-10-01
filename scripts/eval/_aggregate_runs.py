#!/usr/bin/env python3
"""Aggregate authoritative schema-3 CSV rows without dropping failures or mixing cohorts.

Compatibility CLI: <dataset> <seq> <algo> [auto] [mode]. --all builds every cell.
The old FPS argument is accepted but never used to manufacture runtime metrics.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import statistics

from build_benchmark_csv import REPO, build_rows, build_historical_rows, csv_text, load_inventory, preserved_write
from _run_type import canonicalize_dataset


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def summary(values):
    values = [v for v in values if numeric(v)]
    return dict(n=len(values), mean=statistics.mean(values) if values else None,
                median=statistics.median(values) if values else None,
                min=min(values) if values else None, max=max(values) if values else None,
                sample_std=statistics.stdev(values) if len(values)>1 else None)


def cohort_summary(rows):
    # Accuracy among numerically valid saved trajectories is conditional. A
    # nonzero process exit remains in counts and prevents a clean-success tick.
    selected = [r for r in rows if r['run_status']=='ok']
    alignments = {r['primary_alignment'] for r in rows}
    if len(alignments)!=1:
        raise ValueError('cannot aggregate different primary alignments')
    return dict(cohort=rows[0]['cohort'], planned_members=len(rows),
                evaluated=sum(r['eval_schema']==3 for r in rows),
                outcomes=dict(Counter(r['run_status'] for r in rows)),
                qualified=sum(r['paper_ready'] is True for r in rows),
                paper_usable=sum(r.get('paper_usable') is True for r in rows),
                accepted_primary_ate=summary([r['primary_ate_rmse_m'] for r in selected if r.get('accuracy_eligible')]),
                nonzero_exits=sum(r['process_exit_code'] not in (None,0) for r in rows),
                alignment=next(iter(alignments)),
                conditional_primary_ate=summary([r['primary_ate_rmse_m'] for r in selected]),
                dense_coverage_pct=summary([r['coverage_gap_pct'] for r in rows]),
                run_paths=[r['run_path'] for r in rows])


def summarize_cell(rows):
    if not rows:
        raise ValueError('empty cell')
    identities={(r['run_type'],r['dataset'],r['seq'],r['algo'],r['gnss_variant']) for r in rows}
    if len(identities)!=1:
        raise ValueError('variants/cells must be summarized separately')
    groups=defaultdict(list)
    for row in rows:
        if row['attempt_exists']:
            groups[row['cohort']].append(row)
    outcomes=dict(Counter(r['run_status'] for r in rows))
    return dict(identity=list(next(iter(identities))), planned_slots=len(rows),
                attempted=sum(r['attempt_exists'] for r in rows),
                evaluated=sum(r['eval_schema']==3 for r in rows), outcomes=outcomes,
                acceptance=dict(Counter(r['scientific_status'] for r in rows)),
                paper_usable=sum(r.get('paper_usable') is True for r in rows),
                claim_limits=sorted({limit for r in rows for limit in json.loads(r.get('claim_limits') or '[]')}),
                clean_qualified_n3=(len(rows)==3 and len(groups)==1 and all(
                    r['paper_ready'] is True and r['run_status']=='ok' and r['process_exit_code']==0
                    and not r.get('native_error_observation_count')
                    and numeric(r['coverage_gap_pct']) and r['coverage_gap_pct']>=95 for r in rows)),
                cohorts=[cohort_summary(group) for _,group in sorted(groups.items())],
                scientific_blockers=sorted({blocker for r in rows for blocker in json.loads(r['scientific_blockers'])}))


def number(value):
    return 'unknown' if value is None else f'{value:.6g}'


def render_report(rows, result):
    mode,ds,seq,algo,variant=result['identity']
    lines=[f'# {algo} — {mode}, {ds}/{seq}, input {variant}', '',
           'Generated from the hash-checked attempt inventory and schema-3 evaluations.', '',
           f"Planned slots: {result['planned_slots']}; attempted: {result['attempted']}; "
           f"evaluated: {result['evaluated']}. Outcomes: `{json.dumps(result['outcomes'],sort_keys=True)}`.", '',
           '**N=3 ✅ qualified**' if result['clean_qualified_n3'] else '**Not a qualified clean N=3 cell.**', '',
           f"Acceptance decisions: `{json.dumps(result['acceptance'],sort_keys=True)}`; paper-usable observations: {result['paper_usable']}.", '',
           'ATE below describes numerically valid saved trajectories only. Failures and missing '
           'repetitions stay in the denominator; conditional accuracy is not a success rate. '
           'Separate source/configuration/hardware cohorts are never pooled. '
           'Unverified legacy attempts each retain a separate identity.', '',
           '| Run | Numerical outcome | Exit | Qualification | Primary alignment | ATE RMSE [m] | Dense coverage [%] |',
           '|---|---|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['run']} | {r['run_status']} | {r['process_exit_code'] if r['process_exit_code'] is not None else 'unknown'} | "
                     f"{r['scientific_status']} | {r['primary_alignment']} | {number(r['primary_ate_rmse_m'])} | {number(r['coverage_gap_pct'])} |")
    for group in result['cohorts']:
        stats=group['conditional_primary_ate']
        lines+=['',f"## Recorded cohort `{group['cohort']}`", '',
                f"Conditional {group['alignment'].upper()} ATE: N={stats['n']}; median {number(stats['median'])} m; "
                f"range {number(stats['min'])}–{number(stats['max'])} m; sample SD {number(stats['sample_std'])} m.",
                f"Evaluated {group['evaluated']}; qualified {group['qualified']}; nonzero exits {group['nonzero_exits']}."]
    lines+=['', '## Accepted claim limits', '']
    lines += ['- '+s for s in result['claim_limits']] or ['None recorded.']
    lines+=['', '## Interpretation', '',
            'Sparse keyframes do not establish dense tracking coverage. Unknown fields stay unknown. '
            'SE(3) shape alignment does not measure absolute GNSS global error. DPVO uses Sim(3); '
            'its unknown metric scale prevents direct ranking with metric stereo/VIO. '
            'Displacement-magnitude errors and custom distance windows are separately named in the CSV; '
            'the windows are not the KITTI protocol.', '', '## Qualification blockers', '']
    lines += ['- '+s for s in result['scientific_blockers']] or ['None recorded.']
    return '\n'.join(lines)+'\n'


def write_cells(rows,output_root,repo=REPO,check=False):
    groups=defaultdict(list)
    for row in rows:
        groups[(row['run_type'],row['dataset'],row['seq'],row['algo'],row['gnss_variant'])].append(row)
    differences=[]
    for identity,group in sorted(groups.items()):
        mode,ds,seq,algo,variant=identity
        folder=Path(output_root)/mode/ds/seq/algo
        if variant!='default':
            folder=folder/'variants'/variant
        result=summarize_cell(group)
        outputs={'metrics.csv':csv_text(group), 'summary.json':json.dumps(result,indent=2,allow_nan=False)+'\n',
                 'report.md':render_report(group,result)}
        for name,content in outputs.items():
            path=folder/name
            if check:
                if not path.is_file() or path.read_text()!=content: differences.append(str(path))
            else:
                preserved_write(path,content,repo)
    return len(groups),differences


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('dataset',nargs='?');ap.add_argument('sequence',nargs='?');ap.add_argument('algorithm',nargs='?')
    ap.add_argument('input_fps',nargs='?',default='auto');ap.add_argument('mode',nargs='?',default='vo')
    ap.add_argument('--all',action='store_true');ap.add_argument('--check',action='store_true')
    ap.add_argument('--inventory',type=Path,default=REPO/'results/repair-20261001/inventory.json')
    ap.add_argument('--output-root',type=Path,default=REPO/'results')
    args=ap.parse_args()
    if not args.all and not all((args.dataset,args.sequence,args.algorithm)):
        ap.error('specify --all or dataset sequence algorithm')
    rows=build_rows(load_inventory(args.inventory))
    if not args.all:
        rows=[r for r in rows if (r['dataset'],r['seq'],r['algo'],r['run_type'])==(
            canonicalize_dataset(args.dataset),args.sequence,args.algorithm,args.mode)]
    if not rows:
        ap.error('no matching protocol cell')
    n,differences=write_cells(rows,args.output_root,check=args.check)
    if args.all:
        historical=build_historical_rows(load_inventory(args.inventory))
        if historical:
            hn,hd=write_cells(historical,Path(args.output_root)/'historical-cohorts',check=args.check)
            n+=hn;differences+=hd
    print(f'[aggregate] {n} cells/variants; {len(differences)} stale outputs')
    for path in differences:print(path)
    return bool(differences)


if __name__=='__main__':raise SystemExit(main())
