"""Tests of the cross-fit paper export (crossfit_export.py) on synthetic campaigns, plus a read-only check on the real ones."""
import copy
import json
import math
from pathlib import Path
import shutil
import tempfile
import unittest

import crossfit_export as X

PARAMS = {'gyroscope_noise_density': 1e-3, 'accelerometer_noise_density': 1e-2,
          'gyroscope_random_walk': 1e-5, 'accelerometer_random_walk': 1e-4}
SEARCHED = {k: 2 * v for k, v in PARAMS.items()}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def record(key, study, label, seq, mode, rep, run, ate, *, failed=False, status='ok', returncode=0, support=1.0):
    return dict(key=key, study=study, label=label, sequence=seq, mode=mode, repetition=rep, state='finished',
                run=f'/results/{mode}/ds/{seq}/sys/run{run}', returncode=returncode, timeout=False,
                params=PARAMS if label == 'rule_c' else SEARCHED,
                result=dict(failed=failed, loss=0.001, ate_se3_rmse_m=ate, export_support_fraction=support,
                            numerical_status=status))


class Campaigns:
    """A tuning campaign (two folds of one system) and its test-later copy."""

    def __init__(self, root):
        self.root = Path(root)
        self.tuning, self.test = self.root / 'run4', self.root / 'run9'
        self.next_run = 100
        folds = []
        for tune, other in (('seq04', 'seq07'), ('seq07', 'seq04')):
            fid = f'okvis2_citrusfarm__tune_{tune}'
            folds.append(dict(id=fid, algorithm='okvis2', dataset='citrusfarm', full_sequences=[tune],
                              test_sequences=[other], final_modes=['vio', 'vio-lc']))
            winner = 'noise_a' if tune == 'seq04' else 'motion'
            cands = {}
            for label, base in ((winner, 1.0), ('rule_c', 2.0), ('motion', 1.5)):
                if label in cands:
                    continue
                keys = []
                for rep in (1, 2, 3):
                    key = f'full__{fid}__{label}__{tune}__vio__rep{rep}'
                    self.attempt(self.tuning, record(key, fid, label, tune, 'vio', rep, self.run(), base + rep / 100))
                    keys.append(key)
                cands[label] = keys
            selection = dict(winner=dict(label=winner, params=SEARCHED, loss=0.001, records=cands[winner], failures=0),
                             repeated_candidates=[dict(label=k, records=v) for k, v in cands.items()],
                             full_trial_ranking=[], selected_at='2026-11-03T00:00:00+00:00')
            write(self.tuning / 'studies' / fid / 'selection.json', selection)
            stages = {'final-n1.json': [('vio', 1), ('vio-lc', 1)], 'final-later.json': [('vio', 2), ('vio', 3)],
                      'final-later-lc.json': [('vio-lc', 2), ('vio-lc', 3)]}
            for name, items in stages.items():
                keys = []
                for mode, rep in items:
                    key = f'final_n1__{fid}__{winner}__{other}__{mode}__rep{rep}'
                    failed = (tune == 'seq04' and mode == 'vio' and rep > 1)   # two of three held-out VIO runs fail
                    self.attempt(self.test, record(key, fid, winner, other, mode, rep, self.run(), 9e6 if failed else 3.0 + rep,
                                                   failed=failed, status='scale_collapse' if failed else 'ok'))
                    keys.append(key)
                write(self.test / 'studies' / fid / name, dict(selected_at=selection['selected_at'], parameters=SEARCHED,
                                                               records=keys))
        for camp in (self.tuning, self.test):
            write(camp / 'protocol.json', dict(folds=folds))
        review = dict(passed=False, at='2026-11-05T00:00:00+00:00', art=str(self.tuning), folds=2, attempts=18, failures=0,
                      checks={'1': dict(passed=True, problems=[]), '4': dict(passed=False, problems=['C vs main'])})
        write(self.tuning / 'reviews' / 'citrusfarm.json', review)
        # The test-later campaign carries the tuning records and the review forward, byte-identical.
        shutil.copytree(self.tuning / 'attempts', self.test / 'attempts', dirs_exist_ok=True)
        shutil.copytree(self.tuning / 'reviews', self.test / 'reviews')
        for fid in ('okvis2_citrusfarm__tune_seq04', 'okvis2_citrusfarm__tune_seq07'):
            shutil.copy(self.tuning / 'studies' / fid / 'selection.json', self.test / 'studies' / fid / 'selection.json')

    def run(self):
        self.next_run += 1
        return self.next_run

    def attempt(self, campaign, value):
        write(campaign / 'attempts' / (value['key'] + '.json'), value)

    def export(self, acceptance=None):
        saved = dict(X.DATASETS)
        X.DATASETS['citrusfarm'] = ('run4', 'run9', 'CITRUS-SEARCH.md', acceptance)
        try:
            e = X.Export('citrusfarm', self.root)
            return e, e.build()
        finally:
            X.DATASETS.clear()
            X.DATASETS.update(saved)


def report_for(export):
    """A *-SEARCH.md shaped like timing_search_review.markdown() output, from an export."""
    lines = ['# Noise search review: citrusfarm', '', f"**Verdict: {'PASS' if export['review']['passed'] else 'FAIL'}.** x",
             '', '## Tuning sequence, N=3', '', '| System | Tuned on | Winner | Tuned | C | M | Main Rule C | C vs main |',
             '|---|---|---|---|---|---|---|---|']
    for r in export['folds']:
        lines.append(f"| {r['system_name']} | {r['tuned_on']} | {r['winner']['label']} | {X.cell_text(r['tuning']['winner']['summary'])} | "
                     f"{X.cell_text(r['tuning']['c']['summary'])} | {X.cell_text(r['tuning']['m']['summary'])} | - | - |")
    lines += ['', '## Held-out test', '', '| System | Test sequence | Winner VIO | Winner VIO-LC | C | M | Main Rule C |',
              '|---|---|---|---|---|---|---|']
    for r in export['folds']:
        c = r['held_out_sequence_controls']
        lines.append(f"| {r['system_name']} | {r['held_out_sequence']} | {X.cell_text(r['held_out']['vio']['summary'])} | "
                     f"{X.cell_text(r['held_out']['vio_lc']['summary'])} | {X.cell_text(c['c'])} | {X.cell_text(c['m'])} | - |")
    return '\n'.join(lines + ['', '## Check 3 detail', '']) + '\n'


class CrossfitExportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.c = Campaigns(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_fold_values_come_from_the_records(self):
        e, value = self.c.export()
        self.assertEqual(e.problems, [])
        fold = value['folds'][0]
        self.assertEqual(fold['winner']['label'], 'noise_a')
        self.assertEqual(fold['winner']['params'], SEARCHED)
        self.assertEqual(fold['tuning']['winner']['summary']['median_m'], 1.02)
        self.assertEqual(fold['tuning']['c']['summary']['median_m'], 2.02)
        self.assertEqual(fold['tuning']['m']['summary']['median_m'], 1.52)
        self.assertEqual(len(fold['tuning']['c']['summary']['run_ids']), 3)
        # Held-out VIO: one ok run (4.0) and two failures -> the paper median is a failure; the ok summary is 4.0, 1/3.
        vio = fold['held_out']['vio']['summary']
        self.assertTrue(vio['median_is_failure'])
        self.assertIsNone(vio['median_m'])
        self.assertIsNone(fold['held_out_median_vio_m'])
        self.assertEqual((vio['n'], vio['n_failed'], vio['ok_median_m']), (3, 2, 4.0))
        self.assertEqual(X.cell_text(vio), '4.000 (4.000-4.000) 1/3')
        self.assertEqual(fold['held_out_median_vio_lc_m'], 5.0)
        self.assertEqual([r['repetition'] for r in fold['held_out']['vio_lc']['runs']], [1, 2, 3])
        # The second fold's winner is M itself; its held-out controls come from the first fold.
        self.assertEqual(value['folds'][1]['winner']['kind'], 'motion')
        self.assertEqual(value['folds'][1]['held_out_sequence_controls']['from_fold'], 'okvis2_citrusfarm__tune_seq04')

    def test_tuning_record_must_match_the_tuning_campaign(self):
        path = next((self.c.test / 'attempts').glob('full__*rule_c__seq04__vio__rep2.json'))
        value = json.loads(path.read_text())
        value['result']['ate_se3_rmse_m'] = 0.5
        path.write_text(json.dumps(value))
        e, export = self.c.export()
        self.assertTrue(any('test-later copy differs' in p for p in e.problems))
        # the exported value is the tuning campaign's, not the altered copy
        self.assertEqual(export['folds'][0]['tuning']['c']['summary']['ok_low_m'], 2.01)

    def test_failed_flag_is_copied_and_checked_against_the_paper_definition(self):
        path = next((self.c.test / 'attempts').glob('final_n1__*tune_seq07*__vio__rep1.json'))
        value = json.loads(path.read_text())
        value['result']['export_support_fraction'] = 0.5     # support < 0.9, yet the record says not failed
        path.write_text(json.dumps(value))
        e, export = self.c.export()
        self.assertTrue(any("disagrees with the paper's failure definition" in p for p in e.problems))
        self.assertFalse(export['folds'][1]['held_out']['vio']['runs'][0]['failed'])   # copied, never recomputed

    def test_missing_repetition_and_other_selection_are_problems(self):
        stage = self.c.test / 'studies' / 'okvis2_citrusfarm__tune_seq04' / 'final-later.json'
        value = json.loads(stage.read_text())
        value['records'] = value['records'][:1]
        value['selected_at'] = 'other'
        stage.write_text(json.dumps(value))
        e, _ = self.c.export()
        self.assertTrue(any('ran on another selection' in p for p in e.problems))
        self.assertTrue(any('expected [1, 2, 3]' in p for p in e.problems))

    def test_review_verdict_and_user_acceptance(self):
        _, value = self.c.export()
        self.assertEqual(value['review']['verdict'], 'FAIL')
        self.assertFalse(value['review']['accepted_for_paper'])
        write(self.c.tuning / 'reviews' / 'acc.json', dict(dataset='citrusfarm', accepted=True, decided_by='user',
                                                            decided_on='2026-11-09'))
        _, value = self.c.export('run4/reviews/acc.json')
        self.assertEqual(value['review']['verdict'], 'FAIL, accepted by the user')
        self.assertTrue(value['review']['accepted_for_paper'])
        self.assertEqual(value['review']['user_acceptance']['decided_on'], '2026-11-09')

    def test_report_cross_check(self):
        _, value = self.c.export()
        report = Path(self.tmp) / 'CITRUS-SEARCH.md'
        report.write_text(report_for(value))
        checked, mismatches = X.cross_check(value, report)
        self.assertEqual((checked, mismatches), (24, []))
        report.write_text(report_for(value).replace('2.020 (2.010-2.030)', '2.021 (2.010-2.030)', 1))
        _, mismatches = X.cross_check(value, report)
        self.assertEqual(len(mismatches), 1)
        self.assertIn('tuning C', mismatches[0])

    def test_output_is_deterministic_with_sha256(self):
        _, value = self.c.export()
        out = Path(self.tmp) / 'out'
        path, first = X.write(out, 'citrusfarm', value)
        _, value2 = self.c.export()
        _, second = X.write(out, 'citrusfarm', value2)
        self.assertEqual(first, second)
        self.assertEqual((out / 'citrusfarm-crossfit-n3.json.sha256').read_text(), f'{first}  citrusfarm-crossfit-n3.json\n')
        self.assertNotIn('Infinity', path.read_text())

    def test_summary_failure_handling(self):
        runs = [dict(failed=True, ate_se3_rmse_m=None, run_id='a'), dict(failed=False, ate_se3_rmse_m=2.0, run_id='b'),
                dict(failed=False, ate_se3_rmse_m=1.0, run_id='c')]
        s = X.summarise(runs)
        self.assertEqual((s['median_m'], s['min_m'], s['max_m'], s['max_is_failure']), (2.0, 1.0, None, True))
        self.assertEqual(X.cell_text(s), '1.500 (1.000-2.000) 2/3')
        self.assertEqual(X.cell_text(X.summarise([dict(failed=True, ate_se3_rmse_m=None, run_id='a')] * 3)), 'failed 0/3')


@unittest.skipUnless((X.SEARCH / 'run9' / 'protocol.json').is_file(), 'real campaigns not on this host')
class RealCampaignsTest(unittest.TestCase):
    """Read-only: the real campaigns export without problems and match the generated reports."""

    def test_real_exports(self):
        reports = Path('/data/imoroz/PROGRESS/IMU-TIMING-TUNE')
        for dataset in X.DATASETS:
            e = X.Export(dataset)
            value = e.build()
            self.assertEqual(e.problems, [], dataset)
            self.assertEqual(len(value['folds']), 20)
            if (reports / e.report_name).is_file():
                checked, mismatches = X.cross_check(value, reports / e.report_name)
                self.assertEqual(mismatches, [], dataset)
                self.assertEqual(checked, 240)


if __name__ == '__main__':
    unittest.main()
