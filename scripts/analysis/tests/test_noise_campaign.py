"""Exercise search/replay/selection policy without launching any estimator."""
import copy
import json
import math
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ART = Path(__file__).resolve().parent
WORK = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(WORK / 'scripts/analysis'), str(WORK / 'scripts/analysis')]
import noise_campaign_search as policy
import noise_campaign_engine as execution
import noise_campaign as coordinator


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


class FakeEngine:
    def __init__(self, path):
        self.ART = path
        self.records = {}
        self.base = SimpleNamespace(write=write, now=lambda: 'synthetic-clock', event=lambda *a, **kw: None)

    def run_attempt(self, spec, label, params, sequence, mode, repetition, phase):
        key = '__'.join((phase, spec['id'], label, sequence, mode, str(repetition)))
        if key not in self.records:
            distance = sum((math.log10(v) - (.4 if sequence.endswith('1') else .7))**2
                           for v in params.values())
            # The LC outcome is deliberately poor: it must not influence VIO selection.
            failed = mode == 'vio-lc'
            residual = distance / (10 + distance) + repetition * .0001
            self.records[key] = dict(key=key, phase=phase, sequence=sequence, mode=mode,
                repetition=repetition, params=copy.deepcopy(params),
                result=dict(failed=failed, loss=10 * int(failed) + residual))
        return self.records[key]


class SearchChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='search-policy-', dir=ART)
        self.root = Path(self.temp.name)
        self.engine = FakeEngine(self.root)
        self.spec = dict(id='synthetic', algorithm='orbslam3', dataset='rosariov2',
            controls=[dict(label='rule_c', params={k: 1. for k in policy.KEYS}),
                      dict(label='motion', params={k: 3. for k in policy.KEYS})],
            bounds={k: [.1, 100.] for k in policy.KEYS},
            clips=['clip1', 'clip2'], full_sequences=['full1'], test_sequences=['test1'],
            final_modes=['vio', 'vio-lc'], supports_lc=True)
        self.protocol = dict(
            screen=dict(seeds=[202610091, 202610092], candidates_per_seed=12, startup=8),
            full=dict(seed=202610093, candidates=10, seed_candidates=6, finalists=2, repetitions=3),
            test_later=dict(repetitions=[2, 3], mode='vio'))
        self.search = policy.DevelopmentSearch(self.engine, self.spec, self.protocol)

    def tearDown(self):
        self.temp.cleanup()

    def test_equal_control_repeat_cohorts_frozen_selection_and_fresh_final(self):
        selected = self.search.develop()
        for candidate in selected['repeated_candidates']:
            records = [self.engine.records[key] for key in candidate['records']]
            self.assertEqual(len(records), 3)
            self.assertEqual({(r['sequence'], r['repetition']) for r in records},
                             {(seq, rep) for seq in self.spec['full_sequences'] for rep in (1, 2, 3)})
        confirmed = {policy.identity(c['params']) for c in selected['repeated_candidates']}
        self.assertTrue({policy.identity(c['params']) for c in self.spec['controls']} <= confirmed)
        before = (self.search.directory / 'selection.json').read_bytes()
        development_keys = set(self.engine.records)
        final = self.search.final_n1()
        self.assertEqual(len(final['records']), 2)
        self.assertFalse(set(final['records']) & development_keys)
        self.assertEqual(before, (self.search.directory / 'selection.json').read_bytes())
        for key in final['records']:
            self.assertEqual(self.engine.records[key]['params'], selected['winner']['params'])
        count = len(self.engine.records)
        self.assertEqual(self.search.develop(), selected)
        self.assertEqual(len(self.engine.records), count)

    def test_changed_optimizer_state_is_rejected(self):
        self.search.screening()
        path = self.search.directory / 'screen_seed0/trial00.json'
        changed = json.loads(path.read_text())
        changed['params'][policy.KEYS[0]] *= 2
        write(path, changed)
        with self.assertRaisesRegex(RuntimeError, 'differs on replay'):
            self.search.screening()

    def test_identical_controls_are_not_two_comparisons(self):
        self.spec['controls'][1]['params'] = dict(self.spec['controls'][0]['params'])
        self.assertEqual(len(policy.controls(self.spec)), 1)
        selected = self.search.develop()
        values = [policy.identity(x['params']) for x in selected['repeated_candidates']]
        self.assertEqual(len(values), len(set(values)))
        # Deduplication does not shrink the declared proposal count.
        self.assertEqual(len(list((self.search.directory / 'screen_seed0').glob('trial*.json'))), 12)

    def test_one_failure_cannot_beat_successes_with_large_residuals(self):
        success = [dict(result=dict(failed=False, loss=2.))] * 6
        failure = [dict(result=dict(failed=False, loss=0.))] * 5 + [dict(result=dict(failed=True, loss=10.))]
        for objective in ('mean', 'mean_worst'):
            self.assertLess(policy.combined(success, objective), policy.combined(failure, objective))

    def test_voxel_success_requires_receipts_and_expected_native_sampling(self):
        run = self.root / 'voxel'
        run.mkdir()
        spec = dict(algorithm='voxel_svio', dataset='synthetic')
        with self.assertRaisesRegex(RuntimeError, 'lacks input-delivery evidence'):
            execution.verify_transport(run, spec, 'unused', 0)
        dataset = self.root / 'datasets/synthetic/unused'
        for name in ('cam0','cam1','imu0'):
            path = dataset / 'mav0' / name / 'data.csv'
            path.parent.mkdir(parents=True)
            path.write_text('0,data\n33000000,data\n100000000,data\n')
        write(run / 'transport_stats.json', dict(camera_frames_expected=3,
            camera_frames_published=3, imu_messages_published=3, camera_read_failures=0))
        receipt = dict(stereo_received=3, imu_received=3, stereo_queued_after_rate_gate=2,
            first_camera_s=0., last_camera_s=.1, first_imu_s=0., last_imu_s=.1)
        write(run / 'native/input_receipt.json', receipt)
        (run / 'native/parameter_list.txt').write_text('track_frequency: 20.0\n')
        (run / 'effective_ros_parameters.yaml').write_text('odometry_parameter:\n  track_frequency: 20.0\n')
        with patch.object(execution, 'ROOT', self.root):
            self.assertTrue(execution.verify_transport(run, spec, 'unused', 0)['passed'])
            receipt['stereo_queued_after_rate_gate'] = 1
            write(run / 'native/input_receipt.json', receipt)
            with self.assertRaisesRegex(RuntimeError, 'native rate gate audit failed'):
                execution.verify_transport(run, spec, 'unused', 0)

    def test_collection_never_replaces_finished_measurement(self):
        art = self.root / 'collection'
        key = 'synthetic_attempt'
        path = art / 'workers/synthetic/attempts' / (key + '.json')
        original = dict(key=key, run='synthetic_run', params={'x': 1}, campaign_id='test', state='running')
        write(path, original)
        coordinator.collect(art, [self.spec])
        finished = dict(original, state='finished', loss=1.)
        write(path, finished)
        coordinator.collect(art, [self.spec])
        write(path, dict(finished, loss=2.))
        with self.assertRaisesRegex(RuntimeError, 'identity changed'):
            coordinator.collect(art, [self.spec])
        self.assertEqual(json.loads((art / 'attempts' / path.name).read_text()), finished)

    def test_production_artifact_destination_is_refused(self):
        with self.assertRaisesRegex(RuntimeError, 'production worktree'):
            coordinator.artifact_root(execution.base.MAIN / 'results/unwanted-experiment')


if __name__ == '__main__':
    __import__('optuna').logging.set_verbosity(__import__('optuna').logging.WARNING)
    unittest.main(verbosity=2)
