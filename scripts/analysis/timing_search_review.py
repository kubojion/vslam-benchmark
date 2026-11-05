#!/usr/bin/env python3
"""Automatic review of one finished dataset of the noise search (PLAN Update 7, Step 1); never launches anything.

Reads the artifact directory's records and main's Rule C cells, then writes

    <art>/reviews/<dataset>.json   the review the next dataset's coordinator requires (passed true or false)
    --report                       the generated Markdown report (CITRUS-SEARCH.md, HORTI-SEARCH.md, ROSARIO-SEARCH.md)

Checks, all of which must hold:
1. every fold has a frozen selection and its test runs finished;
2. no FAULT or stop file, every attempt finished, and every attempt that failed before its estimator started
   was replaced and the replacement finished;
3. every winner reproduces its tuning score within the repeat spread recorded in its selection;
4. the default (C) runs agree with main's Rule C cells within 10 %, or within the known run-to-run spread.

Usage: timing_search_review.py --art DIR --dataset NAME --report FILE
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from noise_campaign_search import combined  # noqa: E402

MAIN_CSV = Path('/data/imoroz/vslam-benchmark/benchmark-vio.csv')
RELATIVE = 0.10
NAMES = {'okvis2': 'OKVIS2', 'okvis2x': 'OKVIS2-X', 'orbslam3': 'ORB-SLAM3', 'openvins': 'OpenVINS',
         'voxel_svio': 'Voxel-SVIO', 'svo_pro': 'SVO Pro', 'basalt': 'Basalt', 'cuvslam': 'cuVSLAM',
         'airslam': 'AirSLAM', 'mast3r_fusion': 'MASt3R-Fusion'}


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def attempt(art, key):
    return load(art / 'attempts' / (key + '.json'))


def runs(art, keys):
    """ATE and status of attempt records, in order."""
    out = []
    for key in keys:
        record = attempt(art, key)
        result = record.get('result') or {}
        out.append(dict(key=key, run=Path(record['run']).name, failed=bool(result.get('failed', True)),
                        status=result.get('numerical_status', 'no_result'), ate=result.get('ate_se3_rmse_m'),
                        loss=result.get('loss'), mode=record.get('mode'), sequence=record.get('sequence')))
    return out


def ok_ates(items):
    return [r['ate'] for r in items if not r['failed'] and r['ate'] is not None]


def summary(items):
    good = ok_ates(items)
    return dict(n=len(items), ok=len(good), median=statistics.median(good) if good else None,
                low=min(good) if good else None, high=max(good) if good else None)


def cell_text(s):
    if s is None or s['n'] == 0:
        return '-'
    if not s['ok']:
        return f"failed 0/{s['n']}"
    text = f"{s['median']:.3f}"
    if s['n'] > 1:
        text += f" ({s['low']:.3f}-{s['high']:.3f})"
    return text + ('' if s['ok'] == s['n'] else f" {s['ok']}/{s['n']}")


def main_cells(dataset):
    cells = {}
    with MAIN_CSV.open() as stream:
        for row in csv.DictReader(stream):
            if row['dataset'] != dataset or row['run_type'] != 'vio':
                continue
            ate = float(row['ate_se3_rmse_m']) if row['ate_se3_rmse_m'] else None
            cells.setdefault((row['seq'], row['algo']), []).append(dict(
                run=row['run'], failed=row['run_status'] != 'ok', status=row['run_status'], ate=ate))
    return cells


def agreement(search, rule_c):
    """C in the search against main's Rule C cell: 10 %, or the larger N=3 range of the two."""
    s, r = summary(search), summary(rule_c)
    if not r['n']:
        return dict(passed=False, reason='no Rule C cell in main')
    if not s['ok'] and not r['ok']:
        return dict(passed=True, reason='both failed in every run')
    if not s['ok'] or not r['ok']:
        return dict(passed=False, reason=f"one side failed in every run (search {s['ok']}/{s['n']}, main {r['ok']}/{r['n']})")
    ratio = s['median'] / r['median'] - 1
    spread = max(s['high'] - s['low'], r['high'] - r['low'])
    within = abs(ratio) <= RELATIVE or abs(s['median'] - r['median']) <= spread
    note = '' if s['ok'] == s['n'] and r['ok'] == r['n'] else f" (ok runs: search {s['ok']}/{s['n']}, main {r['ok']}/{r['n']})"
    return dict(passed=within, ratio=ratio, spread_m=spread,
                reason=(f"{ratio:+.1%}, spread {spread:.3f} m" + note))


def review(art, dataset):
    art = Path(art).resolve()
    protocol = load(art / 'protocol.json')
    folds = [f for f in protocol['folds'] if f['dataset'] == dataset]
    by_id = {f['id']: f for f in folds}
    checks, rows, held_out, failures = {1: [], 2: [], 3: [], 4: []}, [], [], []
    rule_c = main_cells(dataset)
    selections = {}

    # Check 2: faults, stop files, unfinished or unreplaced attempts.
    for name in ('FAULT', 'STOP', 'STOP_AFTER_CURRENT'):
        if (art / name).exists():
            checks[2].append(f'{name} exists: ' + (art / name).read_text().strip()[:300])
    ours = {f['id'] for f in folds}
    records = [load(p) for p in sorted((art / 'attempts').glob('*.json'))]
    records = [r for r in records if r.get('study') in ours]
    for record in records:
        if record.get('state') != 'finished':
            checks[2].append(f"attempt not finished: {record['key']} state={record.get('state')}")
    replaced = {(r.get('automatic_replacement') or {}).get('superseded', {}).get('run') for r in records}
    superseded = [load(p) for p in sorted((art / 'superseded-attempts').glob('*.json'))]
    superseded = [r for r in superseded if r.get('study') in ours]
    for record in superseded:
        if record.get('run') not in replaced:
            checks[2].append(f"pre-estimation failure without a finished replacement: {record['key']} {record.get('run')}")

    for spec in folds:
        study = art / 'studies' / spec['id']
        selection_path, final_path = study / 'selection.json', study / 'final-n1.json'
        completion = art / 'workers' / spec['id'] / 'test-completion.json'
        if not selection_path.is_file() or 'selected_at' not in load(selection_path):
            checks[1].append(f"{spec['id']}: no frozen selection")
            continue
        selection = selections[spec['id']] = load(selection_path)
        if not final_path.is_file():
            checks[1].append(f"{spec['id']}: no test record (final-n1.json)")
        elif not completion.is_file() or load(completion).get('complete') is not True:
            checks[1].append(f"{spec['id']}: test stage not complete")
        else:
            final = load(final_path)
            if final.get('selected_at') != selection['selected_at']:
                checks[1].append(f"{spec['id']}: test ran on another selection")
            if any(attempt(art, k).get('state') != 'finished' for k in final['records']):
                checks[1].append(f"{spec['id']}: a test run did not finish")

        # Check 3: the winner's tuning score against its N=3 repeats.
        winner = selection['winner']
        repeats = [attempt(art, k)['result'] for k in winner['records']]
        rescored = combined([dict(result=r) for r in repeats])
        if not math.isclose(rescored, winner['loss'], rel_tol=0, abs_tol=1e-12):
            checks[3].append(f"{spec['id']}: N=3 score {winner['loss']} does not re-score from its records ({rescored})")
        per_run = [r['loss'] + 10 * int(r['failed']) for r in repeats]
        tuning = next((t for t in selection['full_trial_ranking'] if t['label'] == winner['label']), None)
        if tuning is None:
            checks[3].append(f"{spec['id']}: winner {winner['label']} has no tuning score in the full search")
        elif not min(per_run) - 1e-12 <= tuning['loss'] <= max(per_run) + 1e-12:
            checks[3].append(f"{spec['id']}: tuning score {tuning['loss']:.6f} outside the repeat spread "
                             f"{min(per_run):.6f}-{max(per_run):.6f}")

        # Check 4: C in the search against main's Rule C cell on the tuning sequence.
        candidates = {c['label']: c for c in selection['repeated_candidates']}
        tuned_seq = spec['full_sequences'][0]
        c_runs = runs(art, candidates['rule_c']['records']) if 'rule_c' in candidates else []
        main_runs = rule_c.get((tuned_seq, spec['algorithm']), [])
        agree = agreement(c_runs, main_runs)
        if not agree['passed']:
            checks[4].append(f"{spec['id']}: C {cell_text(summary(c_runs))} m against main {cell_text(summary(main_runs))} m, {agree['reason']}")
        rows.append(dict(fold=spec['id'], algorithm=spec['algorithm'], tune=tuned_seq, test=spec['test_sequences'][0],
                         winner=winner['label'], winner_failures=winner['failures'],
                         tuned=summary(runs(art, winner['records'])), c=summary(c_runs),
                         m=summary(runs(art, candidates['motion']['records'])) if 'motion' in candidates else None,
                         main=summary(main_runs), agreement=agree, tuning_score=tuning and tuning['loss'],
                         repeat_scores=per_run, score=winner['loss'],
                         same_run=bool(tuning) and tuning['records'][0] in winner['records']))

    # Held-out: the winner on the other sequence, next to C and M measured on that sequence by the other fold.
    for row in rows:
        spec = by_id[row['fold']]
        final = art / 'studies' / spec['id'] / 'final-n1.json'
        tests = runs(art, load(final)['records']) if final.is_file() else []
        other = next((r for r in rows if r['algorithm'] == row['algorithm'] and r['tune'] == row['test']), None)
        held_out.append(dict(fold=row['fold'], algorithm=row['algorithm'], sequence=row['test'],
                             vio=next((summary([t]) for t in tests if t['mode'] == 'vio'), None),
                             vio_lc=next((summary([t]) for t in tests if t['mode'] == 'vio-lc'), None),
                             c=other and other['c'], m=other and other['m'],
                             main=summary(rule_c.get((row['test'], row['algorithm']), []))))

    for record in records:
        result = record.get('result') or {}
        if result.get('failed') or record.get('returncode') not in (0, None) or record.get('timeout'):
            failures.append(dict(study=record['study'], phase=record.get('phase'), status=result.get('numerical_status'),
                                 returncode=record.get('returncode'), timeout=record.get('timeout')))
    passed = not any(checks.values())
    value = dict(schema=1, dataset=dataset, passed=passed, at=datetime.now(timezone.utc).isoformat(),
                 written_by='timing_search_review.py (PLAN Update 7, Step 1, automatic review)',
                 protocol_sha256=sha(art / 'protocol.json'), art=str(art), main_csv=str(MAIN_CSV), main_csv_sha256=sha(MAIN_CSV),
                 checks={str(k): dict(passed=not v, problems=v) for k, v in checks.items()},
                 folds=len(folds), attempts=len(records), superseded=len(superseded), failures=len(failures),
                 rows=rows, held_out=held_out)
    return value, failures


def markdown(value, failures):
    names = {'1': 'Every fold has a frozen selection and finished test runs',
             '2': 'No FAULT, stop file, unfinished attempt or unreplaced pre-estimation failure',
             '3': 'Every winner reproduces its tuning score within its repeat spread',
             '4': f"C agrees with main's Rule C within {RELATIVE:.0%} or the run-to-run spread"}
    lines = [f"# Noise search review: {value['dataset']}", '',
             f"Generated {value['at'][:16].replace('T', ' ')} UTC by `scripts/analysis/timing_search_review.py` from `{value['art']}`. "
             'Do not edit by hand.', '',
             f"**Verdict: {'PASS' if value['passed'] else 'FAIL'}.** {value['folds']} folds, {value['attempts']} attempts, "
             f"{value['superseded']} replaced before their estimator started, {value['failures']} failed runs (results, not faults).", '',
             '| Check | Result |', '|---|---|']
    for key, check in value['checks'].items():
        lines.append(f"| {key}. {names[key]} | {'PASS' if check['passed'] else 'FAIL'} |")
    for key, check in value['checks'].items():
        if check['problems']:
            lines += ['', f"**Check {key} problems:**"] + [f"- {p}" for p in check['problems']]
    lines += ['', '## Tuning sequence, N=3', '',
              'ATE SE(3) RMSE in m: median (range), with ok runs shown when some failed. Main is the Rule C cell in `benchmark-vio.csv`.', '',
              '| System | Tuned on | Winner | Tuned | C | M | Main Rule C | C vs main |', '|---|---|---|---|---|---|---|---|']
    for r in value['rows']:
        lines.append(f"| {NAMES[r['algorithm']]} | {r['tune']} | {r['winner']} | {cell_text(r['tuned'])} | {cell_text(r['c'])} | "
                     f"{cell_text(r['m'])} | {cell_text(r['main'])} | {r['agreement']['reason']} |")
    lines += ['', '## Held-out test', '',
              'The winner N=1 on the other sequence. C and M are the other fold\'s N=3 runs on the same sequence.', '',
              '| System | Test sequence | Winner VIO | Winner VIO-LC | C | M | Main Rule C |', '|---|---|---|---|---|---|---|']
    for h in value['held_out']:
        lines.append(f"| {NAMES[h['algorithm']]} | {h['sequence']} | {cell_text(h['vio'])} | {cell_text(h['vio_lc'])} | "
                     f"{cell_text(h['c'])} | {cell_text(h['m'])} | {cell_text(h['main'])} |")
    lines += ['', '## Check 3 detail', '',
              "The tuning score is the winner's N=1 score in the full search. Its first repetition is that same run "
              '(the attempt is cached), so the score lies inside the spread by construction; the check also re-scores N=3 from the records.', '',
              '| Fold | Tuning score | Repeat scores | N=3 score |', '|---|---|---|---|']
    for r in value['rows']:
        tuning = '-' if r['tuning_score'] is None else f"{r['tuning_score']:.5f}"
        lines.append(f"| {r['fold']} | {tuning} | {', '.join(f'{x:.5f}' for x in r['repeat_scores'])} | {r['score']:.5f} |")
    lines += ['', '## Failures', '']
    if not failures:
        lines.append('None.')
    else:
        counts = {}
        for f in failures:
            key = (f['study'], f['phase'], f['status'], f['returncode'], bool(f['timeout']))
            counts[key] = counts.get(key, 0) + 1
        lines += ['| Fold | Phase | Status | Exit | Timeout | Runs |', '|---|---|---|---|---|---|']
        lines += [f"| {k[0]} | {k[1]} | {k[2]} | {k[3]} | {'yes' if k[4] else 'no'} | {n} |" for k, n in sorted(counts.items(), key=str)]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--art', type=Path, required=True)
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--dry-run', action='store_true', help='print the verdict, write nothing')
    args = parser.parse_args()
    value, failures = review(args.art, args.dataset)
    if not args.dry_run:
        target = Path(args.art) / 'reviews' / (args.dataset + '.json')
        if target.exists():
            raise FileExistsError('review already written: ' + str(target))
        target.parent.mkdir(exist_ok=True)
        target.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
        args.report.write_text(markdown(value, failures))
    print(json.dumps(dict(passed=value['passed'], checks=value['checks']), indent=2))
    return 0 if value['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
