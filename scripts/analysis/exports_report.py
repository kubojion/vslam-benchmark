#!/usr/bin/env python3
"""Render PROGRESS/IMU-TIMING-TUNE/EXPORTS.md from the generated paper exports (never from typed numbers).

Inputs: <export dir>/<ds>-crossfit-n3.json (crossfit_export.py) and the Sielinko N=3 completion reviews
(/data/imoroz/sielinko-n3-20261110/<cpu|gpu>/final-completion-review-n3.json, export_paper.py on branch
eng/sielinko-n3-export-20261113).

Usage: exports_report.py --out /data/imoroz/PROGRESS/IMU-TIMING-TUNE/EXPORTS.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

EXPORT_DIR = Path('/data/imoroz/PROGRESS/IMU-TIMING-TUNE/export')
SIELINKO = Path('/data/imoroz/sielinko-n3-20261110')
DATASETS = ('citrusfarm', 'hortimulti', 'rosariov2')
SEARCH_CLONE = '/data/imoroz/vslam-search-export-20261113'
N3_CLONE = '/data/imoroz/vslam-sielinko-n3-export-20261113'
PY = '/data/imoroz/conda/envs/macvo/bin/python'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def m(value):
    return '-' if value is None else f'{value:.3f}'


def held(cell):
    if cell is None:
        return '-'
    s = cell['summary']
    text = 'failed' if s['median_is_failure'] else m(s['median_m'])
    return text + (f" ({s['n_failed']}/{s['n']} failed)" if s['n_failed'] else '')


def section2(export_dir):
    lines = ['## Section 2: public datasets, cross-fit (N=3 held-out)', '',
             'One export per dataset. Held-out median: the median of the winner\'s N=3 runs on the other sequence, with a '
             'failed run counted as +inf ("failed" when the median itself is a failure). The *-SEARCH.md reports show '
             'the median of the ok runs instead; the two differ only where a held-out run failed (listed below).', '',
             '| Dataset | Export | sha256 | Review | Folds | Report cells checked | Mismatches | Problems |',
             '|---|---|---|---|---|---|---|---|']
    exports = {}
    for ds in DATASETS:
        path = export_dir / f'{ds}-crossfit-n3.json'
        e = exports[ds] = json.loads(path.read_text())
        x = e['checks']['report_cross_check'] or {}
        lines.append(f"| {ds} | `{path}` | `{sha(path)}` | {e['review']['verdict']} | {len(e['folds'])} | "
                     f"{x.get('cells_checked', '-')} | {len(x.get('mismatches', []))} | {len(e['checks']['problems'])} |")
    for ds, e in exports.items():
        r = e['review']
        lines += ['', f'### {ds}', '',
                  f"Review: `{r['file']}` (sha256 `{r['sha256']}`), passed {str(r['passed']).lower()}; "
                  + ', '.join(f"check {k} {'PASS' if v['passed'] else 'FAIL'}" for k, v in r['checks'].items()) + '.']
        if r['user_acceptance'].get('file'):
            a = r['user_acceptance']
            lines.append(f"User acceptance: `{a['file']}` (sha256 `{a['sha256']}`), accepted {str(a['accepted']).lower()} "
                         f"by {a['decided_by']} on {a['decided_on']}.")
        lines += ['', '| System | Tuned on | Winner | Tuned N=3 median | Held-out | VIO median | VIO-LC median |',
                  '|---|---|---|---|---|---|---|']
        for f in e['folds']:
            lines.append(f"| {f['system_name']} | {f['tuned_on']} | {f['winner']['label']} | "
                         f"{held(f['tuning']['winner'])} | {f['held_out_sequence']} | {held(f['held_out']['vio'])} | "
                         f"{held(f['held_out']['vio_lc'])} |")
        differ = [(f, mode) for f in e['folds'] for mode in ('vio', 'vio_lc')
                  if f['held_out'][mode] and f['held_out'][mode]['summary']['n_failed']]
        if differ:
            lines += ['', 'Held-out cells with a failed run (paper median vs the report\'s ok-run median):']
            for f, mode in differ:
                s = f['held_out'][mode]['summary']
                paper = 'failed' if s['median_is_failure'] else m(s['median_m'])
                lines.append(f"- {f['fold']} {mode.replace('_', '-').upper()}: {s['n_failed']}/{s['n']} failed; "
                             f"paper median {paper}, report ok-run median {m(s['ok_median_m'])}.")
    return lines


def section3(root):
    lines = ['', '## Section 3: Sielinko N=3 (Update 10 B, C, D search)', '',
             '| Campaign | Review | sha256 | Passed | Items terminal | Tests at N=3 | Paper files (new / first runs) |',
             '|---|---|---|---|---|---|---|']
    reviews = {}
    for c in ('cpu', 'gpu'):
        path = root / c / 'final-completion-review-n3.json'
        if not path.is_file():
            lines.append(f'| {c} | missing | - | - | - | - | - |')
            continue
        v = reviews[c] = json.loads(path.read_text())
        n = v['counts']
        lines.append(f"| {c} | `{path}` | `{sha(path)}` | {str(v['passed']).lower()} | "
                     f"{n['items'] - n['pending']}/{n['items']} | {n['tests_at_n3']}/{n['tests']} | "
                     f"{n['exported_new_runs']} / {n['exported_first_runs']} |")
    for c, v in reviews.items():
        lines += ['', f'### {c}', '', '| Check | Result |', '|---|---|']
        lines += [f"| {k} | {'PASS' if v['checks'][k]['passed'] else 'FAIL'} |" for k in v['gating_checks']]
        pend = v['checks']['all_items_terminal']['not_terminal']
        if pend:
            lines.append('')
            lines += [f"- Not terminal: {p['item']} ({p['state']})." for p in pend]
        f = v['checks']['no_unresolved_fault_or_stop']
        for r in f['resolved_renamed_faults']:
            first = (r['decision'] or '').splitlines()[0]
            title = first.split('**')[1].rstrip(':') if first.count('**') >= 2 else first[:120]
            lines.append(f"- Resolved: `{Path(r['file']).name}`, by the recorded decision \"{title}\" "
                         f"(`{Path(r['decision_source']).name}`).")
        rep = v['checks']['reproduction_within_1pct']
        for g in rep['gating']:
            lines.append(f"- 1 % rule (gating): {g['item']} {g['relative_difference']:.2%} against the first run.")
        for item in rep['reported_not_gating_outside_1pct']:
            row = next(r for r in rep['all_items'] if r['item'] == item)
            lines.append(f"- Outside 1 %, reported, not gating: {item} {row['relative_difference']:.2%} "
                         f"({row['ate_m']:.4f} m against {row['reference_ate_m']:.4f} m).")
        lines.append(f"- Record-only systems: {', '.join(rep['record_only_systems'])}.")
        lines += ['', '| Test | Mode | N | Failed | Median (primary reference) |', '|---|---|---|---|---|']
        for t in v['per_test']:
            med = 'failed' if t['median_is_failure'] else m(t['median_primary_reference_m'])
            lines.append(f"| {t['study']} {t['kind']} ({t['label']}) | {t['mode']} | {t['n']} | {t['n_failed']} | {med} |")
    return lines


LOADER_NOTE = '''
## For the paper session (the loader is not changed here)
`PAPER/vslam-paper/scripts/paperdata/search.py` needs these changes to read the exports:

**Section 2 (cross-fit):**
1. A new reader for `export/<ds>-crossfit-n3.json`: per fold, the held-out value is `held_out_median_vio_m` (and
   `held_out_median_vio_lc_m`), a failed run counting as +inf (`median_is_failure`). Do not use `analyse()`/`_one()`:
   they model select-on-A-then-one-fresh-run and take `iloc[0]`.
2. "Reviewed" for these datasets is `review.accepted_for_paper` (Rosario: FAIL on check 4, accepted by the user), not a
   `final-completion-review*.json`.
3. Treat the old pilot/cpu15/cpu6/gpu6/air3 CitrusFarm, HortiMulti and Rosario studies as superseded by the cross-fit.

**Section 3 (Sielinko, `lpit()`):**
1. Add `sielinko-n3-20261110/cpu` and `sielinko-n3-20261110/gpu` to `LPIT_DIRS` (or the snapshot copy), and read
   `attempts-paper/*.json` there instead of `attempts/*.json` (the dispatcher's own `attempts/` names do not start with
   `final_n1` and would be skipped anyway). `studies/*/selection.json` and `final-completion-review-n3.json` are in
   place for the existing joins; the n3 review sets the status of every Sielinko study it lists.
2. Filter by mode: `lpit()` does not read `mode`, so the VIO-LC runs (C items, D search, and the three first VIO-LC
   runs exported from the supplemental validation) are mixed into `full_sel`. Read `a['mode']` into the rows and use
   `mode == 'vio'` for h2_sel, h2_aop and full_sel; add a separate VIO-LC full_sel value (the "--" in `tab:accuracy`
   from item C) and OKVIS2-X VIO-LC (D search) as a new row.
3. The GPU first campaign on the server has no top-level `attempts/`; the snapshot's copy is built from
   `workers/<study>/attempts/`. Keep that for the first runs; the new runs come only from `attempts-paper/`.
4. RTK-fixed scoring: `lpit()` takes the value from `derived/zed-fixed-only.json` and silently falls back to the
   primary-reference ATE for runs not in it. Run `scripts/rescore_fixed.py` for the new run directories (their paths are
   the `run` fields) before the rebuild, or the new repetitions are scored against a different reference.
5. `assert ... min(len(h2_sel), len(h2_aop), len(full_sel)) >= 1` stays true; `n_test` and `planned_n=3` now reach 3.
6. `lpit_time()` sums `wall_s` over every attempt in `LPIT_DIRS`; with the n3 folders added it also counts the test
   repetitions and the copied first VIO-LC runs (`origin == "first_run_outside_first_campaign"`, already counted
   nowhere in `LPIT_DIRS` before). Decide whether the reported search time should include them.
'''


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--export-dir', type=Path, default=EXPORT_DIR)
    parser.add_argument('--sielinko', type=Path, default=SIELINKO)
    args = parser.parse_args(argv)
    lines = ['# Paper exports: extended search (results organisation, sections 2 and 3)', '',
             f'Generated by `scripts/analysis/exports_report.py` ({SEARCH_CLONE}, branch `eng/search-export-20261113`) '
             'from the generated exports below. Do not edit by hand; every number comes from the attempt records '
             'through the two generators.', '']
    lines += section2(args.export_dir) + section3(args.sielinko)
    lines += LOADER_NOTE.strip('\n').splitlines()
    lines += ['', '## How to regenerate', '', '```',
              '# Section 2 (reads run4/7/8 and run9/10/11; checks every cell against *-SEARCH.md)',
              f'cd {SEARCH_CLONE} && {PY} -B scripts/analysis/crossfit_export.py \\',
              '    --out-dir /data/imoroz/PROGRESS/IMU-TIMING-TUNE/export --check-reports /data/imoroz/PROGRESS/IMU-TIMING-TUNE',
              '# Section 3 (reads the manifests and attempt records; writes attempts-paper/, studies/, the n3 reviews)',
              f'cd {N3_CLONE}/scripts/analysis && {PY} -B sielinko_n3/export_paper.py',
              '# This file',
              f'cd {SEARCH_CLONE} && {PY} -B scripts/analysis/exports_report.py --out /data/imoroz/PROGRESS/IMU-TIMING-TUNE/EXPORTS.md',
              '# Tests',
              f'cd {SEARCH_CLONE} && {PY} -B -m pytest -q -p no:cacheprovider scripts/analysis/tests/test_crossfit_export.py',
              f'cd {N3_CLONE} && {PY} -B -m pytest -q -p no:cacheprovider scripts/analysis/sielinko_n3/tests/test_export_paper.py',
              '```']
    args.out.write_text('\n'.join(lines) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
