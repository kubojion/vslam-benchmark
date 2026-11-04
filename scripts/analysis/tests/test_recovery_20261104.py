"""Recovery of 4 Nov 2026: the lane sampler records, and a pre-estimation failure is replaced once. No estimator runs."""
from contextlib import nullcontext
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

import noise_campaign
import noise_campaign_engine as engine
import prepare_timing_search as prepare
import timing_lanes as lanes

PARAMS = dict(gyroscope_noise_density=1e-3, accelerometer_noise_density=1e-2,
              gyroscope_random_walk=1e-5, accelerometer_random_walk=1e-4)
STUDY = 'okvis2_citrusfarm__tune_seq04'
KEY = 'full__' + STUDY + '__motion__seq04__vio__rep1'
SPEC = dict(id=STUDY, algorithm='okvis2', dataset='citrusfarm', sequence_parents={'seq04': 'seq04'}, clips=[])
PROTOCOL = dict(campaign_id='unit-test-recovery', run_ids=dict(fold_blocks={STUDY: [70000, 70099]}),
                runtime_environment={}, attempt_timeouts_s={'okvis2': dict(vio=5400)},
                lanes=dict(cpu_a=dict(cpus='0-3')),
                launch_policy=dict(sample_s=0.05, max_affinity_corrections=3))


class SamplerRecords(unittest.TestCase):
    def test_sampler_run_writes_samples(self):
        with tempfile.TemporaryDirectory() as directory:
            attempt = dict(key=KEY, run=str(Path(directory) / 'run70001'), unit='noise-campaign-none-70001')
            sampler = lanes.Sampler(PROTOCOL, 'cpu_a', attempt, Path(directory) / 'lane-samples')
            with patch.object(lanes, 'processes', return_value=[]):
                sampler.start()
                deadline = time.time() + 10
                while sampler.samples < 2 and time.time() < deadline:
                    time.sleep(.02)
                summary = sampler.stop()
            self.assertFalse(sampler.is_alive())
            rows = [json.loads(line) for line in Path(summary['path']).read_text().splitlines()]
            self.assertGreaterEqual(len(rows), 1)
            self.assertEqual(len(rows), summary['samples'])
            self.assertEqual(summary['errors'], [])
            self.assertTrue(all(isinstance(r['at'], float) and r['lane'] == 'cpu_a' and r['errors'] == [] for r in rows))


class FakeProcess:
    def __init__(self, behaviour):
        self.behaviour = behaviour

    def wait(self, timeout=None):
        return self.behaviour()


class AutomaticReplacement(unittest.TestCase):
    """run_attempt up to and after the wrapper, with Popen replaced by a fake that only writes files."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'root'
        self.art = Path(self.tmp.name) / 'art'
        self.art.mkdir()
        (self.art / 'budget.json').write_text(json.dumps(dict(started_unix=0, deadline_unix=4e9)))
        self.launches = []
        self.protocol = copy.deepcopy(PROTOCOL)

    def tearDown(self):
        self.tmp.cleanup()

    def behaviours(self, *items):
        self.queue = list(items)

    def popen(self, command, **kwargs):
        run = self.root / 'results/vio/citrusfarm/seq04/okvis2' / ('run' + command[-2])
        self.launches.append(run)
        kind = self.queue.pop(0)

        def behaviour():
            run.mkdir(parents=True)
            (run / 'provenance').mkdir()
            if kind == 'helper_crash':
                return 139
            if kind == 'timeout':
                raise subprocess.TimeoutExpired(command, 1)
            if kind == 'launched_then_crash':
                (run / 'processes').mkdir()
                (run / 'processes/estimator.json').write_text('{}')
                return 139
            (run / 'run_meta.json').write_text('{}')
            return 0 if kind == 'ok' else 1
        return FakeProcess(behaviour)

    def call(self):
        command = ['systemd-run', '--user', '--scope', '--quiet', '--unit=noise-campaign-test']
        engine.configure(self.art, self.protocol, nullcontext)
        with patch.object(engine, 'ROOT', self.root), patch.object(engine, 'verify_frozen'), \
                patch.object(engine.adapters, 'prepare', return_value=dict(environment={})), \
                patch.object(engine.adapters, 'verify_snapshot', return_value={}), \
                patch.object(engine.execution_policy, 'identity_environment', return_value={}), \
                patch.object(engine.execution_policy, 'bounded_command', side_effect=lambda c, *a, **k: command + c), \
                patch.object(engine.base, 'reference_distance', return_value=100.), \
                patch.object(engine.noise_cleanup, 'stop_owned_attempt'), \
                patch.object(engine.subprocess, 'Popen', side_effect=self.popen):
            return engine.run_attempt(SPEC, 'motion', PARAMS, 'seq04', 'vio', 1, 'full')

    def events(self):
        return [json.loads(line)['event'] for line in (self.art / 'events.jsonl').read_text().splitlines()]

    def ledger(self):
        return json.loads((self.art / 'run-ids.json').read_text())

    def test_first_pre_estimation_failure_is_replaced_once_with_a_new_id(self):
        self.behaviours('helper_crash', 'ok')
        record = self.call()
        first, second = self.launches
        self.assertEqual((first.name, second.name), ('run70000', 'run70001'))
        self.assertEqual(record['state'], 'finished')
        self.assertEqual(record['run'], str(second))
        replacement = record['automatic_replacement']
        self.assertEqual(replacement['count'], 1)
        self.assertEqual(replacement['run_id'], 70001)
        self.assertEqual(replacement['superseded']['run'], str(first))
        self.assertEqual(replacement['superseded']['returncode'], 139)
        archived = json.loads(Path(replacement['superseded']['record']).read_text())
        self.assertEqual(archived['state'], engine.PRE_ESTIMATION_FAILED)
        self.assertEqual(archived['run'], str(first))
        self.assertIs(archived['estimator_started'], False)
        self.assertTrue(first.is_dir() and second.is_dir())  # the old run directory is kept
        self.assertEqual(sorted(self.ledger().values()), [70000, 70001])
        self.assertIn('attempt_pre_estimation_failure', self.events())
        self.assertIn('attempt_automatic_replacement', self.events())
        # A replay returns the finished replacement and launches nothing.
        self.assertEqual(self.call(), record)
        self.assertEqual(len(self.launches), 2)

    def test_second_pre_estimation_failure_stops(self):
        self.behaviours('helper_crash', 'helper_crash')
        with self.assertRaisesRegex(RuntimeError, 'Wrapper did not create metadata'):
            self.call()
        self.assertEqual(len(self.launches), 2)
        record = json.loads((self.art / 'attempts' / (KEY + '.json')).read_text())
        self.assertEqual(record['state'], 'running')
        self.assertEqual(record['automatic_replacement']['superseded']['run'], str(self.launches[0]))
        self.assertTrue(all(run.is_dir() for run in self.launches))
        with self.assertRaisesRegex(RuntimeError, 'requires explicit recovery'):
            self.call()
        self.assertEqual(len(self.launches), 2)

    def test_failures_after_the_estimator_started_are_not_replaced(self):
        for kind, returncode in (('estimator_failure', 1), ('timeout', 124)):
            with self.subTest(kind=kind):
                self.setUp()
                self.behaviours(kind)
                record = self.call()
                self.assertEqual((record['state'], record['returncode']), ('finished', returncode))
                self.assertTrue(record['result']['failed'])
                self.assertNotIn('automatic_replacement', record)
                self.assertEqual(len(self.launches), 1)
                self.assertEqual(list(self.ledger().values()), [70000])
                self.assertFalse((self.art / 'superseded-attempts').exists())

    def test_a_launched_native_process_without_metadata_stops_as_before(self):
        self.behaviours('launched_then_crash')
        with self.assertRaisesRegex(RuntimeError, 'Wrapper did not create metadata'):
            self.call()
        self.assertEqual(len(self.launches), 1)
        self.assertEqual(json.loads((self.art / 'attempts' / (KEY + '.json')).read_text())['state'], 'running')

    def test_a_reviewed_replacement_is_never_replaced_automatically(self):
        predecessor = self.art / 'predecessor.json'
        predecessor.write_text(json.dumps(dict(params=PARAMS)))
        item = dict(revision='review-1', record=str(predecessor))
        self.behaviours('helper_crash')
        with patch.object(engine.execution_policy, 'reviewed_attempt_revision', return_value=item):
            with self.assertRaisesRegex(RuntimeError, 'Wrapper did not create metadata'):
                self.call()
        self.assertEqual(len(self.launches), 1)

    def test_a_stop_between_failure_and_replacement_resumes_with_the_replacement(self):
        self.behaviours('helper_crash', 'ok')
        original = engine.execute_attempt
        calls = []

        def stop_before_replacement(*args, **kwargs):
            calls.append(args)
            if len(calls) == 2:
                (self.art / 'STOP_AFTER_CURRENT').write_text('test\n')
            return original(*args, **kwargs)
        with patch.object(engine, 'execute_attempt', side_effect=stop_before_replacement):
            with self.assertRaises(InterruptedError):
                self.call()
        record = json.loads((self.art / 'attempts' / (KEY + '.json')).read_text())
        self.assertEqual(record['state'], engine.PRE_ESTIMATION_FAILED)
        (self.art / 'STOP_AFTER_CURRENT').unlink()
        record = self.call()
        self.assertEqual(record['state'], 'finished')
        self.assertEqual([r.name for r in self.launches], ['run70000', 'run70001'])
        self.assertEqual(record['automatic_replacement']['superseded']['run'], str(self.launches[0]))

    def test_collect_accepts_the_replacement_and_keeps_the_failure(self):
        art = Path(self.tmp.name) / 'campaign'
        self.art = art / 'workers' / STUDY
        self.art.mkdir(parents=True)
        (self.art / 'budget.json').write_text(json.dumps(dict(started_unix=0, deadline_unix=4e9)))
        self.behaviours('helper_crash', 'ok')
        original = engine.execute_attempt

        def collect_each_time(*args, **kwargs):
            noise_campaign.collect(art, [SPEC])
            return original(*args, **kwargs)
        with patch.object(engine, 'execute_attempt', side_effect=collect_each_time):
            record = self.call()
        noise_campaign.collect(art, [SPEC])
        self.assertEqual(json.loads((art / 'attempts' / (KEY + '.json')).read_text()), record)
        kept = list((art / 'superseded-attempts').glob('*.json'))
        self.assertEqual(len(kept), 1)
        self.assertEqual(json.loads(kept[0].read_text())['run'], str(self.launches[0]))
        # A changed run without a replacement link is still refused.
        changed = dict(record, run=str(self.launches[0]) + 'x', state='running')
        changed.pop('automatic_replacement')
        (art / 'attempts' / (KEY + '.json')).write_text(json.dumps(dict(changed, run=str(self.launches[0]))))
        (self.art / 'attempts' / (KEY + '.json')).write_text(json.dumps(changed))
        with self.assertRaisesRegex(RuntimeError, 'identity changed'):
            noise_campaign.collect(art, [SPEC])


class RecoveryFreeze(unittest.TestCase):
    def test_freeze_refuses_an_existing_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(FileExistsError, 'freeze only into a new one'):
                prepare.freeze(directory)

    def test_reuse_admits_exactly_the_earlier_records_of_the_same_campaign(self):
        with tempfile.TemporaryDirectory() as directory:
            old = Path(directory)
            (old / 'attempts').mkdir()
            runs = [str(prepare.ROOT / 'results/vio/citrusfarm/seq04/okvis2' / f'run{i}') for i in (70000, 70001)]
            for i, run in enumerate(runs):
                (old / 'attempts' / f'a{i}.json').write_text(json.dumps(dict(campaign_id='c', run=run)))
            self.assertEqual(prepare.reused_runs(old, 'c'), set(runs))
            with self.assertRaisesRegex(RuntimeError, 'another campaign'):
                prepare.reused_runs(old, 'other')
            (old / 'attempts' / 'a2.json').write_text(json.dumps(dict(campaign_id='c', run='/elsewhere/results/vio/c/s/a/run70002')))
            with self.assertRaisesRegex(RuntimeError, 'another campaign or checkout'):
                prepare.reused_runs(old, 'c')


if __name__ == '__main__':
    unittest.main()
