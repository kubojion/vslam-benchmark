#!/usr/bin/env python3
"""Paper export of the cross-fit noise search (PLAN Update 8; RESULTS-ORGANISATION.md section 2). Never launches anything.

For each public dataset, reads the tuning campaign (run4 CitrusFarm, run7 HortiMulti, run8 Rosario) and the test-later
campaign that carries its records forward (run9, run10, run11), and writes one generated JSON per dataset:

    <out>/<dataset>-crossfit-n3.json   and   <out>/<dataset>-crossfit-n3.json.sha256

Per fold (system x tuned-on sequence): the frozen winner (label, parameters), the tuning N=3 runs of the winner, of C
(rule_c) and of M (motion); the held-out runs of the winner on the other sequence in VIO and, where supported, VIO-LC
(N=3 each), with run IDs, ATE and the campaign's own failure flag (result.failed); and the held-out medians.
Plus the dataset's generated review verdict and, where one exists, the user's acceptance of a failed review.

Every number is copied or derived from the attempt records; nothing is typed. The output carries no timestamp, so a
re-run on unchanged inputs and the same commit gives the same bytes.

Medians: ``median_m`` follows the paper (a failed run counts as +inf; null with ``median_is_failure`` when the median is
a failure); ``ok_median_m``/``ok_low_m``/``ok_high_m`` are over the runs that did not fail, as in the *-SEARCH.md reports.

Checks (all recorded in the export; any problem makes the script exit 1 after writing):
- each tuning attempt in the test-later campaign is byte-identical to the tuning campaign's record;
- the test-later campaign's selection is the tuning campaign's selection; all held-out records ran on it and finished;
- result.failed agrees with the paper's failure definition (nonzero exit, run_status != ok incl. scale collapse,
  export support < 0.9, ATE missing or non-finite);
- every value agrees with the regenerated *-SEARCH.md tables (--check-reports).

Usage:
  crossfit_export.py --out-dir /data/imoroz/PROGRESS/IMU-TIMING-TUNE/export \
      --check-reports /data/imoroz/PROGRESS/IMU-TIMING-TUNE [--dataset citrusfarm ...]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import subprocess
import sys

SEARCH = Path('/data/imoroz/vslam-timing-search-20261031/timing-search')
DATASETS = {
    # dataset: (tuning campaign, test-later campaign, generated report, user acceptance of a failed review or None)
    'citrusfarm': ('run4', 'run9', 'CITRUS-SEARCH.md', None),
    'hortimulti': ('run7', 'run10', 'HORTI-SEARCH.md', None),
    'rosariov2': ('run8', 'run11', 'ROSARIO-SEARCH.md', 'run8/reviews/rosariov2-user-acceptance.json'),
}
HELD_OUT_FILES = ('final-n1.json', 'final-later.json', 'final-later-lc.json')
MIN_SUPPORT = 0.90
NAMES = {'okvis2': 'OKVIS2', 'okvis2x': 'OKVIS2-X', 'orbslam3': 'ORB-SLAM3', 'openvins': 'OpenVINS',
         'voxel_svio': 'Voxel-SVIO', 'svo_pro': 'SVO Pro', 'basalt': 'Basalt', 'cuvslam': 'cuVSLAM',
         'airslam': 'AirSLAM', 'mast3r_fusion': 'MASt3R-Fusion'}
FAILURE_DEFINITION = ('failed = nonzero exit, or run_status != ok (scale_collapse included), or export support < 0.9, '
                      'or ATE missing/non-finite; copied from the campaign record (result.failed), not recomputed')


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_identity():
    root = Path(__file__).resolve().parents[2]

    def git(*args):
        return subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, check=True).stdout.strip()
    try:
        script = str(Path(__file__).resolve().relative_to(root))
        return dict(repository=str(root), branch=git('rev-parse', '--abbrev-ref', 'HEAD'), commit=git('rev-parse', 'HEAD'),
                    script=script, script_uncommitted=bool(git('status', '--porcelain', '--', script)))
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return dict(repository=str(root), branch=None, commit=None, script=Path(__file__).name, script_uncommitted=None)


# ---------------------------------------------------------------- runs and summaries

def paper_failed(record):
    """The paper's failure definition, evaluated from the record's own fields (a consistency check only)."""
    r = record.get('result') or {}
    ate = r.get('ate_se3_rmse_m')
    support = r.get('export_support_fraction')
    return bool(record.get('returncode') not in (0,) or r.get('numerical_status') != 'ok'
                or support is None or support < MIN_SUPPORT
                or not isinstance(ate, (int, float)) or not math.isfinite(ate) or ate < 0)


def run_entry(record, source, source_sha):
    r = record.get('result') or {}
    return dict(key=record['key'], run_id=Path(record['run']).name, run=record['run'], sequence=record['sequence'],
                mode=record['mode'], repetition=record['repetition'], label=record['label'], state=record.get('state'),
                returncode=record.get('returncode'), timeout=record.get('timeout'),
                failed=bool(r.get('failed', True)), numerical_status=r.get('numerical_status'),
                ate_se3_rmse_m=r.get('ate_se3_rmse_m'), export_support_fraction=r.get('export_support_fraction'),
                loss=r.get('loss'), record=str(source), record_sha256=source_sha)


def summarise(runs):
    """Paper median (failed = +inf) and the ok-run summary of the *-SEARCH.md reports."""
    if not runs:
        return None
    values = [math.inf if r['failed'] else r['ate_se3_rmse_m'] for r in runs]
    ok = sorted(r['ate_se3_rmse_m'] for r in runs if not r['failed'] and r['ate_se3_rmse_m'] is not None)
    median = statistics.median(values)
    return dict(n=len(runs), n_failed=sum(r['failed'] for r in runs), n_ok=len(ok),
                median_m=None if math.isinf(median) else median, median_is_failure=math.isinf(median),
                min_m=None if math.isinf(min(values)) else min(values), max_m=None if math.isinf(max(values)) else max(values),
                max_is_failure=math.isinf(max(values)),
                ok_median_m=statistics.median(ok) if ok else None, ok_low_m=ok[0] if ok else None,
                ok_high_m=ok[-1] if ok else None,
                run_ids=[r['run_id'] for r in runs])


def cell_text(s):
    """The *-SEARCH.md cell format (timing_search_review.cell_text), re-implemented for the cross-check."""
    if s is None or s['n'] == 0:
        return '-'
    if not s['n_ok']:
        return f"failed 0/{s['n']}"
    text = f"{s['ok_median_m']:.3f}"
    if s['n'] > 1:
        text += f" ({s['ok_low_m']:.3f}-{s['ok_high_m']:.3f})"
    return text + ('' if s['n_ok'] == s['n'] else f" {s['n_ok']}/{s['n']}")


# ---------------------------------------------------------------- export

class Export:
    def __init__(self, dataset, search=SEARCH):
        self.dataset = dataset
        tuning, test, self.report_name, acceptance = DATASETS[dataset]
        self.tuning, self.test = search / tuning, search / test
        self.acceptance = search / acceptance if acceptance else None
        self.problems = []

    def problem(self, text):
        self.problems.append(text)

    def tuning_run(self, key):
        """A tuning attempt: read in the test-later campaign, checked byte-identical to the tuning campaign's record."""
        here, origin = self.test / 'attempts' / (key + '.json'), self.tuning / 'attempts' / (key + '.json')
        if not origin.is_file():
            self.problem(f'{key}: not in the tuning campaign {self.tuning.name}')
            record, source = load(here), here
        else:
            source = origin
            if not here.is_file() or here.read_bytes() != origin.read_bytes():
                self.problem(f'{key}: test-later copy differs from the tuning record')
            record = load(origin)
        return self.checked(record, source)

    def test_run(self, key):
        path = self.test / 'attempts' / (key + '.json')
        return self.checked(load(path), path)

    def checked(self, record, source):
        entry = run_entry(record, source, sha(source))
        if record.get('state') != 'finished':
            self.problem(f"{entry['key']}: state {record.get('state')}")
        if entry['failed'] != paper_failed(record):
            self.problem(f"{entry['key']}: result.failed={entry['failed']} disagrees with the paper's failure definition")
        return entry

    def review(self):
        path = self.tuning / 'reviews' / (self.dataset + '.json')
        value = load(path)
        copy = self.test / 'reviews' / (self.dataset + '.json')
        if not copy.is_file() or copy.read_bytes() != path.read_bytes():
            self.problem(f'review copy in {self.test.name} differs from {path}')
        out = dict(file=str(path), sha256=sha(path), passed=value['passed'], at=value['at'], art=value['art'],
                   checks={k: dict(passed=v['passed'], problems=v['problems']) for k, v in value['checks'].items()},
                   folds=value['folds'], attempts=value['attempts'], failures=value['failures'],
                   note='Written by timing_search_review.py on the tuning campaign; its held-out rows predate the N=3 '
                        'repetitions. The N=3 report was regenerated with --report-only from the test-later campaign.')
        accepted = dict(file=None)
        if self.acceptance is not None:
            a = load(self.acceptance)
            if a.get('dataset') != self.dataset:
                self.problem('acceptance file is for another dataset')
            accepted = dict(file=str(self.acceptance), sha256=sha(self.acceptance), **a)
        out['user_acceptance'] = accepted
        out['accepted_for_paper'] = bool(value['passed'] or (accepted.get('accepted') is True
                                                              and accepted.get('decided_by') == 'user'))
        out['verdict'] = ('PASS' if value['passed'] else
                          'FAIL, accepted by the user' if out['accepted_for_paper'] else 'FAIL')
        return out

    def fold(self, spec):
        sid = spec['id']
        study, tune_study = self.test / 'studies' / sid, self.tuning / 'studies' / sid
        selection = load(study / 'selection.json')
        if load(tune_study / 'selection.json') != selection:
            self.problem(f'{sid}: selection differs between {self.tuning.name} and {self.test.name}')
        winner = selection['winner']
        candidates = {c['label']: c for c in selection['repeated_candidates']}
        tuning = dict(winner=[self.tuning_run(k) for k in winner['records']])
        for name, label in (('c', 'rule_c'), ('m', 'motion')):
            tuning[name] = [self.tuning_run(k) for k in candidates[label]['records']] if label in candidates else []
            if label not in candidates:
                self.problem(f'{sid}: no repeated {label} candidate')
        held = []
        files = {}
        modes = spec.get('final_modes', ['vio'])
        for name in HELD_OUT_FILES:
            path = study / name
            if not path.is_file():
                if name != 'final-later-lc.json' or 'vio-lc' in modes:   # the LC stage exists only for LC systems
                    self.problem(f'{sid}: {name} missing')
                continue
            value = load(path)
            files[name] = dict(file=str(path), sha256=sha(path))
            if value.get('selected_at') != selection['selected_at']:
                self.problem(f'{sid}: {name} ran on another selection')
            if value.get('parameters') not in (None, winner['params']):
                self.problem(f'{sid}: {name} parameters differ from the winner')
            held += [self.test_run(k) for k in value['records']]
        test_seq = spec['test_sequences'][0]
        for r in held:
            if r['label'] != winner['label'] or r['sequence'] != test_seq:
                self.problem(f"{r['key']}: held-out run is not the winner on {test_seq}")
        held_out = {}
        for mode in ('vio', 'vio-lc'):
            runs = sorted((r for r in held if r['mode'] == mode), key=lambda r: r['repetition'])
            if mode not in modes:
                if runs:
                    self.problem(f'{sid}: {mode} runs although the fold does not support it')
                held_out[mode] = None
                continue
            if [r['repetition'] for r in runs] != [1, 2, 3]:
                self.problem(f"{sid}: held-out {mode} repetitions {[r['repetition'] for r in runs]}, expected [1, 2, 3]")
            held_out[mode] = dict(summary=summarise(runs), runs=runs)
        for name, runs in tuning.items():
            if [r['repetition'] for r in runs] != [1, 2, 3] and runs:
                self.problem(f"{sid}: tuning {name} repetitions {[r['repetition'] for r in runs]}")
        return dict(
            fold=sid, system=spec['algorithm'], system_name=NAMES.get(spec['algorithm'], spec['algorithm']),
            tuned_on=spec['full_sequences'][0], held_out_sequence=test_seq, supports_vio_lc='vio-lc' in modes,
            selection=dict(file=str(study / 'selection.json'), sha256=sha(study / 'selection.json'),
                           selected_at=selection['selected_at'], winner_score=winner['loss'],
                           winner_failures=winner['failures']),
            winner=dict(label=winner['label'], kind=('rule_c' if winner['label'] == 'rule_c' else 'motion'
                                                     if winner['label'] == 'motion' else 'searched'),
                        params=winner['params']),
            tuning={name: dict(label=('rule_c' if name == 'c' else 'motion' if name == 'm' else winner['label']),
                               summary=summarise(runs), runs=runs) for name, runs in tuning.items()},
            held_out={'vio': held_out['vio'], 'vio_lc': held_out['vio-lc']},
            held_out_median_vio_m=held_out['vio'] and held_out['vio']['summary']['median_m'],
            held_out_median_vio_lc_m=held_out['vio-lc'] and held_out['vio-lc']['summary']['median_m'],
            held_out_records=files)

    def build(self):
        protocol = load(self.test / 'protocol.json')
        folds = [f for f in protocol['folds'] if f['dataset'] == self.dataset]
        tuning_protocol = load(self.tuning / 'protocol.json')
        if [f['id'] for f in tuning_protocol['folds'] if f['dataset'] == self.dataset] != [f['id'] for f in folds]:
            self.problem('fold list differs between the tuning and test-later protocols')
        rows = [self.fold(spec) for spec in folds]
        # Controls on the held-out sequence: the other fold's tuning runs of C and M (as in the reports).
        for row in rows:
            other = next((r for r in rows if r['system'] == row['system'] and r['tuned_on'] == row['held_out_sequence']), None)
            row['held_out_sequence_controls'] = None if other is None else dict(
                from_fold=other['fold'], c=other['tuning']['c']['summary'], m=other['tuning']['m']['summary'])
        carried = self.test / 'carried-from-earlier-freeze.json'
        return dict(
            schema=1, kind='crossfit-n3-export', dataset=self.dataset,
            protocol=dict(design='cross-fit: tune on one sequence (N=3 repeated selection), test the frozen winner on the '
                                 'other sequence (N=3 per mode); both folds',
                          held_out_value='median over the N=3 held-out repetitions, a failed repetition counting as +inf',
                          failure_definition=FAILURE_DEFINITION, independent_test=False,
                          independence_note='The held-out sequence was never used by this tuning, but was inspected in '
                                            'earlier work (final-n1.json note).'),
            sources=dict(tuning_campaign=str(self.tuning), test_later_campaign=str(self.test),
                         tuning_protocol_sha256=sha(self.tuning / 'protocol.json'),
                         test_protocol_sha256=sha(self.test / 'protocol.json'),
                         carried_from_earlier_freeze=dict(file=str(carried), sha256=sha(carried)) if carried.is_file() else None),
            review=self.review(), folds=rows,
            generated_by=git_identity())


# ---------------------------------------------------------------- cross-check against the generated report

def table(markdown, heading):
    """Rows of the first table after a '## heading' line, as lists of cells."""
    lines = markdown.splitlines()
    start = lines.index('## ' + heading)
    rows = []
    for line in lines[start + 1:]:
        if line.startswith('## '):
            break
        if line.startswith('|') and not line.startswith('|---'):
            rows.append([c.strip() for c in line.strip().strip('|').split('|')])
    return rows[1:]


def cross_check(export, report):
    """Compare the export with the generated *-SEARCH.md tables; returns (checked cell count, mismatches)."""
    text = Path(report).read_text()
    mismatches, checked = [], 0
    verdict = re.search(r'\*\*Verdict: (PASS|FAIL)\.\*\*', text)
    if not verdict or (verdict.group(1) == 'PASS') != export['review']['passed']:
        mismatches.append(f"verdict: report {verdict and verdict.group(1)}, review passed={export['review']['passed']}")
    tune = table(text, 'Tuning sequence, N=3')
    held = table(text, 'Held-out test')
    if len(tune) != len(export['folds']) or len(held) != len(export['folds']):
        mismatches.append(f"row count: report {len(tune)}/{len(held)}, export {len(export['folds'])}")
    for row, t, h in zip(export['folds'], tune, held):
        want = [row['system_name'], row['tuned_on'], row['winner']['label'], cell_text(row['tuning']['winner']['summary']),
                cell_text(row['tuning']['c']['summary']), cell_text(row['tuning']['m']['summary'])]
        for name, got, exp in zip(('system', 'tuned on', 'winner', 'tuned', 'C', 'M'), t[:6], want):
            checked += 1
            if got != exp:
                mismatches.append(f"{row['fold']} tuning {name}: report '{got}', export '{exp}'")
        controls = row['held_out_sequence_controls'] or {}
        want = [row['system_name'], row['held_out_sequence'],
                cell_text(row['held_out']['vio'] and row['held_out']['vio']['summary']),
                cell_text(row['held_out']['vio_lc'] and row['held_out']['vio_lc']['summary']),
                cell_text(controls.get('c')), cell_text(controls.get('m'))]
        for name, got, exp in zip(('system', 'test sequence', 'winner VIO', 'winner VIO-LC', 'C', 'M'), h[:6], want):
            checked += 1
            if got != exp:
                mismatches.append(f"{row['fold']} held-out {name}: report '{got}', export '{exp}'")
    return checked, mismatches


def dumps(value):
    return json.dumps(value, indent=2, allow_nan=False) + '\n'


def write(out_dir, dataset, value):
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / (dataset + '-crossfit-n3.json')
    text = dumps(value)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(text)
    tmp.replace(path)
    digest = hashlib.sha256(text.encode()).hexdigest()
    (out_dir / (path.name + '.sha256')).write_text(f'{digest}  {path.name}\n')
    return path, digest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--check-reports', type=Path, help='directory with CITRUS/HORTI/ROSARIO-SEARCH.md')
    parser.add_argument('--dataset', action='append', choices=sorted(DATASETS))
    parser.add_argument('--search', type=Path, default=SEARCH, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    status = 0
    for dataset in args.dataset or list(DATASETS):
        export = Export(dataset, args.search)
        value = export.build()
        report = None
        if args.check_reports:
            path = args.check_reports / export.report_name
            checked, mismatches = cross_check(value, path)
            report = dict(file=str(path), sha256=sha(path), cells_checked=checked, mismatches=mismatches,
                          passed=not mismatches)
        value['checks'] = dict(problems=export.problems, passed=not export.problems, report_cross_check=report)
        path, digest = write(args.out_dir, dataset, value)
        ok = not export.problems and (report is None or report['passed'])
        status |= not ok
        print(json.dumps(dict(dataset=dataset, file=str(path), sha256=digest, verdict=value['review']['verdict'],
                              problems=len(export.problems),
                              report_cells_checked=report and report['cells_checked'],
                              report_mismatches=report and len(report['mismatches']))))
        for p in export.problems + ((report or {}).get('mismatches') or []):
            print('  ' + p)
    return status


if __name__ == '__main__':
    sys.exit(main())
