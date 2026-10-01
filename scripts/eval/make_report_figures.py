#!/usr/bin/env python3
"""Generate provisional, cohort-aware figures from the reconciled CSVs.

No causal IMU/LC narrative or accuracy ranking is inferred. All five modes and
separate GNSS variants are represented; numerical failure counts remain visible.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

from build_benchmark_csv import REPO, RUN_TYPES, preserved_write
from make_report_tables import ALGO_LABEL, SEQ_LABEL
from _report_data import checked_rows, plotted_cell


def accuracy_figure(rows, mode, variant):
    rows = [r for r in rows if r['run_type'] == mode and r['gnss_variant'] == variant]
    algorithms = [a for a in ALGO_LABEL if any(r['algo'] == a for r in rows)]
    sequences = [s for s in SEQ_LABEL if any((r['dataset'], r['seq']) == s for r in rows)]
    alignments = [a for a in ('se3', 'sim3') if any(r['primary_alignment'] == a for r in rows)]
    sizes = [sum(any(r['algo'] == a and r['primary_alignment'] == alignment for r in rows)
                 for a in algorithms) for alignment in alignments]
    fig, axes = plt.subplots(len(alignments), 1, squeeze=False,
        figsize=(max(8.5, len(sequences)*1.45), max(3.8, sum(sizes)*.73+2.8)),
        gridspec_kw={'height_ratios': sizes})
    plotted = []
    for ax, alignment in zip(axes[:, 0], alignments):
        selected = [r for r in rows if r['primary_alignment'] == alignment]
        algos = [a for a in algorithms if any(r['algo'] == a for r in selected)]
        values = np.full((len(algos), len(sequences)), np.nan)
        annotations = []
        for i, algorithm in enumerate(algos):
            for j, (dataset, sequence) in enumerate(sequences):
                group = [r for r in selected if (r['dataset'], r['seq'], r['algo']) == (dataset, sequence, algorithm)]
                if not group: continue
                item = plotted_cell(group)
                value = item['value']
                if value is not None and value > 0: values[i, j] = value
                annotations.append((i, j, item['annotation']))
                plotted.append(dict(identity=[mode, dataset, sequence, algorithm, variant], **item))
        cmap = plt.colormaps['YlGnBu'].copy(); cmap.set_bad('#eeeeee')
        plotted_image = ax.imshow(values, cmap=cmap, norm=LogNorm(vmin=.01, vmax=1000), aspect='auto')
        for i, j, annotation in annotations:
            ax.text(j, i, annotation, ha='center', va='center', fontsize=8,
                    color='white' if np.isfinite(values[i,j]) and values[i,j] > 2 else 'black')
        ax.set_xticks(range(len(sequences)), [SEQ_LABEL[s] for s in sequences])
        ax.set_yticks(range(len(algos)), [ALGO_LABEL[a] for a in algos])
        ax.set_title('Metric stereo / inertial: SE(3)' if alignment == 'se3' else 'Monocular shape: Sim(3) — separate scale model', fontsize=11)
        fig.colorbar(plotted_image, ax=ax, fraction=.025, pad=.025,
                     label='Conditional median ATE RMSE [m]' if len(algos) >= 3 else 'ATE [m]')
    fig.suptitle(f'{mode.upper()} · input {variant} · provisional conditional median ATE', fontsize=13)
    fig.text(.02, .015, 'ok/planned = numerical outcomes, not certified successes. U: unqualified; R: config rerun; X: nonzero exit;\n'
             'P: dense export coverage <95%; K: keyframes (dense coverage unknown). Separate cohorts are not pooled.\n'
             'Failures/missing slots stay in counts. Agricultural reference issues remain; aligned GNSS scores are not global error.', fontsize=8)
    fig.tight_layout(rect=(0, .115, 1, .94))
    return fig, plotted


def outcome_figure(rows):
    modes = list(RUN_TYPES)
    categories = ['ok', 'scale_collapse', 'eval_failed', 'failed_without_trajectory', 'incomplete', 'saved_not_evaluated', 'missing']
    colors = ['#367c9c', '#c85a54', '#a64462', '#edb45f', '#967caf', '#7d9979', '#dddddd']
    fig, ax = plt.subplots(figsize=(10.5, 4.4))
    left = np.zeros(len(modes))
    for category, color in zip(categories, colors):
        counts = [sum(r['run_type'] == m and r['run_status'] == category and r['gnss_variant'] == 'default' for r in rows) for m in modes]
        if not any(counts): continue
        ax.barh(modes, counts, left=left, color=color, label=category)
        for i, count in enumerate(counts):
            if count >= 4: ax.text(left[i]+count/2, i, str(count), ha='center', va='center', fontsize=9)
        left += counts
    ax.set_xlabel('Default logical repetitions (N=3 target; GNSS variants separate)')
    ax.set_title('Saved numerical outcomes and missing repetitions across all five modes')
    ax.legend(loc='upper center', bbox_to_anchor=(.5, -.19), ncol=3, fontsize=8)
    fig.text(.02, .015, 'Numerically ok does not imply clean execution or publication qualification. No failures are removed from the denominator.', fontsize=8)
    fig.tight_layout(rect=(0, .05, 1, 1))
    return fig


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--inventory', type=Path, default=REPO/'results/repair-20261001/inventory.json')
    ap.add_argument('--csv-dir', type=Path, default=REPO)
    ap.add_argument('--output-dir', type=Path, default=REPO/'docs/generated/figures')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    rows, inputs = checked_rows(args.inventory.resolve(), args.csv_dir.resolve())
    outputs = {}; plotted = []
    def save(fig, stem):
        for suffix in ('png', 'pdf'):
            buffer = io.BytesIO()
            metadata = {'CreationDate': None, 'ModDate': None} if suffix == 'pdf' else {'Software': 'vslam schema-3 reporting'}
            fig.savefig(buffer, format=suffix, dpi=160, metadata=metadata)
            outputs[f'{stem}.{suffix}'] = buffer.getvalue()
        plt.close(fig)
    save(outcome_figure(rows), 'fig_campaign_outcomes')
    for mode in RUN_TYPES:
        for variant in sorted({r['gnss_variant'] for r in rows if r['run_type'] == mode}):
            fig, items = accuracy_figure(rows, mode, variant)
            save(fig, f'fig_accuracy_{mode}_{variant}')
            plotted.extend(items)
    outputs['figure-data.json'] = (json.dumps(dict(schema=1,
        inputs=[dict(path=str(Path(i['path']).relative_to(REPO)), sha256=i['sha256']) for i in inputs],
        status='provisional_diagnostics_not_qualified_paper_comparisons', cells=plotted,
        figures=[dict(path=name, sha256=hashlib.sha256(raw).hexdigest()) for name, raw in outputs.items()]),
        indent=2, allow_nan=False)+'\n').encode()
    stale = []
    for name, raw in outputs.items():
        path = args.output_dir/name
        if args.check:
            if not path.is_file() or path.read_bytes() != raw: stale.append(name)
        else: preserved_write(path, raw)
    print(f'[figures] {len(outputs)} outputs; {len(plotted)} cells/variants; {len(stale)} stale')
    return bool(stale)


if __name__ == '__main__':
    raise SystemExit(main())
