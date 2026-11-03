"""The frozen protocol of PLAN Update 6 Job C: range, M, folds, stages, clips, IDs, inputs, lanes, test logic. No run."""
from contextlib import nullcontext
import copy
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

import imu_motion_noise as motion
import noise_campaign_engine as engine
import noise_campaign_search as policy
import noise_execution_policy as execution_policy
import prepare_timing_search as prepare
import timing_lanes as lanes
import timing_search as coordinator
from test_noise_campaign import FakeEngine

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = json.loads(prepare.PROTOCOL.read_text())
MOTION = json.loads(prepare.MOTION.read_text())
KEYS = prepare.KEYS
GIB = 1024**3
SECOND = 10**9
CITRUS_A = dict(zip(KEYS, (0.00010426654551109309, 0.0002276846771973415, 3.5636559575381104e-06, 6.706087584689249e-06)))
OKVIS_RATIO = dict(zip(KEYS, (2e-3 / 1.6968e-4, 2e-2 / 2e-3, 2e-4 / 1.9393e-5, 2e-2 / 3e-3)))
CITRUS_M = (0.0025292599144778874, 0.04400142625416013)


def study(identifier):
    return next(s for s in PROTOCOL['studies'] if s['id'] == identifier)


def folds_of(identifier):
    return [f for f in PROTOCOL['folds'] if f['study'] == identifier]


class Range(unittest.TestCase):
    def test_formula_uses_the_lower_of_a_and_c_and_the_higher_of_100c_and_3m(self):
        bounds = prepare.noise_bounds(dict.fromkeys(KEYS, 2.), dict.fromkeys(KEYS, 1.), dict.fromkeys(KEYS, 50.))
        self.assertEqual(bounds[KEYS[0]], [.1, 150.])
        bounds = prepare.noise_bounds(dict.fromkeys(KEYS, .5), dict.fromkeys(KEYS, 1.), dict.fromkeys(KEYS, 1.))
        self.assertEqual(bounds[KEYS[0]], [.05, 100.])

    def test_known_values_okvis2_on_citrusfarm(self):
        bounds = study('okvis2_citrusfarm')['bounds']
        for key in KEYS:
            c = CITRUS_A[key] * OKVIS_RATIO[key]
            self.assertTrue(math.isclose(bounds[key][0], CITRUS_A[key] / 10, rel_tol=1e-6), key)
            self.assertTrue(math.isclose(bounds[key][1], 100 * c, rel_tol=1e-5), key)

    def test_known_values_where_m_sets_the_upper_bound(self):
        # Factor-1 systems on CitrusFarm: 3M beats 100C for the accelerometer density only.
        bounds = study('orbslam3_citrusfarm')['bounds']
        self.assertTrue(math.isclose(bounds[KEYS[1]][1], 3 * CITRUS_M[1], rel_tol=1e-12))
        self.assertTrue(math.isclose(bounds[KEYS[0]][1], 100 * CITRUS_A[KEYS[0]], rel_tol=1e-3))
        # MASt3R-Fusion's random-walk factors are below 0.03, so the released value decides.
        bounds = study('mast3r_fusion_citrusfarm')['bounds']
        for key in KEYS[2:]:
            self.assertTrue(math.isclose(bounds[key][1], 3 * CITRUS_A[key], rel_tol=1e-12), key)

    def test_every_study_holds_both_starting_candidates_inside_its_range(self):
        for item in PROTOCOL['studies']:
            for key in KEYS:
                low, high = item['bounds'][key]
                self.assertEqual(low, min(item['A'][key], item['C'][key]) / 10)
                self.assertEqual(high, max(100 * item['C'][key], 3 * item['M'][key]))
                self.assertTrue(low < item['C'][key] < high and low < item['M'][key] < high, (item['id'], key))
        self.assertEqual({f['id']: f['bounds'] for f in PROTOCOL['folds']},
                         {f['id']: study(f['study'])['bounds'] for f in PROTOCOL['folds']})

    def test_sources_of_a_c_and_m_are_recorded(self):
        for item in PROTOCOL['studies']:
            self.assertTrue(set(item['sources']) == {'A', 'C', 'M'} and all(item['sources'].values()))
            self.assertTrue((ROOT / item['sources']['A'].split(': ')[0]).is_file())
            self.assertTrue((ROOT / item['sources']['M']).is_file())


class InMotionLevel(unittest.TestCase):
    def test_one_definition_white_noise_recovers_its_density(self):
        fs, density = 200., .01
        generator = np.random.default_rng(3)
        t = np.arange(0, 120, 1 / fs)
        values = motion.window_densities(t, generator.normal(0, density * math.sqrt(fs), len(t)), fs)
        self.assertEqual(len(values), 119)
        self.assertAlmostEqual(float(np.median(values)), density, delta=.05 * density)

    def test_a_table_gives_the_largest_axis_at_the_95th_percentile(self):
        with tempfile.TemporaryDirectory() as directory:
            fs, n = 200, 200 * 60
            generator = np.random.default_rng(5)
            t = (np.arange(n) * 1e9 / fs).astype(np.int64)
            data = generator.normal(0, 1, (n, 6)) * np.array([.1, .2, .3, 1, 2, 3])
            path = Path(directory) / 'data.csv'
            with path.open('w') as stream:
                stream.write('#t\n')
                for stamp, row in zip(t, data):
                    stream.write(str(stamp) + ',' + ','.join(map(repr, row.tolist())) + '\n')
            levels = motion.sequence_levels(path)
            seconds = t * 1e-9
            real = (n - 1) / (seconds[-1] - seconds[0])
            axes = [np.percentile(motion.window_densities(seconds, data[:, c], real), 95) for c in range(6)]
            self.assertEqual(levels['gyro_q95'], float(max(axes[:3])))
            self.assertEqual(levels['accel_q95'], float(max(axes[3:])))
            self.assertEqual(levels['samples'], n)

    def test_dataset_level_is_the_larger_sequence_with_released_random_walks(self):
        level = motion.dataset_level({'a': dict(gyro_q95=1., accel_q95=4.), 'b': dict(gyro_q95=2., accel_q95=3.)},
                                     dict(zip(KEYS, (9, 9, 7e-6, 8e-6))))
        self.assertEqual(list(level.values()), [2., 4., 7e-6, 8e-6])

    def test_m_is_unrounded_and_the_same_for_every_system_of_a_dataset(self):
        for dataset, seqs in prepare.DATASETS.items():
            record = MOTION['datasets'][dataset]
            expected = motion.dataset_level(record['sequences'], study('okvis2_' + dataset)['A'])
            self.assertEqual(record['M'], expected)
            for item in PROTOCOL['studies']:
                if item['dataset'] == dataset:
                    self.assertEqual(item['M'], expected)
        # Earlier rounded profiles (docs/imu-noise-rule-20261005.md) must not come back.
        citrus = MOTION['datasets']['citrusfarm']['M']
        self.assertEqual((citrus[KEYS[0]], citrus[KEYS[1]]), CITRUS_M)
        self.assertNotIn(citrus[KEYS[0]], (.003, .0025))
        self.assertNotIn(citrus[KEYS[1]], (.05, .044))

    def test_m_agrees_with_the_values_the_plan_checked(self):
        for record in MOTION['datasets'].values():
            for sequence in record['sequences'].values():
                for name in ('gyro_q95', 'accel_q95'):
                    self.assertTrue(math.isclose(sequence[name], sequence['paper_snapshot'][name], rel_tol=1e-9))


class Folds(unittest.TestCase):
    def test_thirty_studies_of_ten_systems_on_three_datasets(self):
        self.assertEqual(len(PROTOCOL['studies']), 30)
        self.assertEqual({(s['algorithm'], s['dataset']) for s in PROTOCOL['studies']},
                         {(a, d) for a in prepare.SYSTEMS for d in prepare.DATASETS})
        self.assertEqual(len(prepare.SYSTEMS), 10)

    def test_each_study_tunes_on_one_sequence_and_tests_on_the_other_both_ways(self):
        self.assertEqual(len(PROTOCOL['folds']), 60)
        for item in PROTOCOL['studies']:
            first, second = folds_of(item['id'])
            pair = set(prepare.DATASETS[item['dataset']])
            self.assertEqual({first['tune_sequence'], first['test_sequence']}, pair)
            self.assertEqual((first['tune_sequence'], first['test_sequence']), (second['test_sequence'], second['tune_sequence']))
            for fold in (first, second):
                self.assertEqual(fold['full_sequences'], [fold['tune_sequence']])
                self.assertEqual(fold['test_sequences'], [fold['test_sequence']])
                self.assertEqual(fold['clips'], [prepare.clip_name(fold['tune_sequence'], n) for n in (1, 2)])
                self.assertEqual({fold['sequence_parents'][c] for c in fold['clips']}, {fold['tune_sequence']})

    def test_pairs_named_by_the_plan(self):
        self.assertEqual(prepare.DATASETS, {'citrusfarm': ('seq04', 'seq07'), 'hortimulti': ('strawberry02', 'strawberry03'),
                                            'rosariov2': ('sequence1', 'sequence5')})

    def test_starting_candidates_are_c_and_m(self):
        for fold in PROTOCOL['folds']:
            item = study(fold['study'])
            self.assertEqual([c['label'] for c in fold['controls']], ['rule_c', 'motion'])
            self.assertEqual([c['params'] for c in fold['controls']], [item['C'], item['M']])


class Sizes(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.engine = FakeEngine(self.root)
        self.fold = copy.deepcopy(PROTOCOL['folds'][0])
        self.search = policy.DevelopmentSearch(self.engine, self.fold, PROTOCOL)

    def tearDown(self):
        self.temp.cleanup()

    def records(self, phase):
        return [r for r in self.engine.records.values() if r['phase'] == phase]

    def test_declared_sizes(self):
        self.assertEqual((len(PROTOCOL['screen']['seeds']), PROTOCOL['screen']['candidates_per_seed']), (2, 12))
        self.assertEqual((PROTOCOL['full']['candidates'], PROTOCOL['full']['finalists'], PROTOCOL['full']['repetitions']), (10, 2, 3))
        self.assertNotIn('preliminary', PROTOCOL)

    def test_stage_sizes_measured_through_the_search(self):
        selected = self.search.develop()
        screen = self.records('screen')
        self.assertEqual(len(screen), coordinator.fold_runs(PROTOCOL, self.fold)['short_clip_runs'])
        self.assertEqual(len(screen), 44)  # 2 x 12 x 2, with C and M measured once
        self.assertEqual({r['sequence'] for r in screen}, set(self.fold['clips']))
        self.assertTrue(all(r['repetition'] == 1 and r['mode'] == 'vio' for r in screen))
        full = self.records('full')
        self.assertEqual({r['sequence'] for r in full}, {self.fold['tune_sequence']})
        self.assertEqual(sum(r['repetition'] == 1 for r in full), 10)
        self.assertLessEqual(len(full), 10 + coordinator.fold_runs(PROTOCOL, self.fold)['selection_runs_at_most'])
        for item in selected['repeated_candidates']:
            self.assertEqual(sorted(self.engine.records[k]['repetition'] for k in item['records']), [1, 2, 3])
        confirmed = {policy.identity(c['params']) for c in selected['repeated_candidates']}
        self.assertTrue({policy.identity(c['params']) for c in self.fold['controls']} <= confirmed)
        self.assertLessEqual(len(confirmed), 4)

    def test_the_dry_plan_counts_and_runs_nothing(self):
        with patch.object(subprocess, 'Popen', side_effect=AssertionError('nothing may start')):
            plan = coordinator.dry_plan(self.root, PROTOCOL)
        self.assertFalse(plan['executed'])
        self.assertEqual((plan['studies'], plan['folds']), (30, 60))
        self.assertEqual(plan['runs_per_fold']['short_clip_runs'], 44)
        self.assertEqual(plan['runs_per_fold']['full_candidate_runs'], 10)
        self.assertEqual(plan['runs_per_fold']['selection_runs_at_most'], 8)
        lc = sum('vio-lc' in f['final_modes'] for f in PROTOCOL['folds'])
        self.assertEqual(lc, 7 * 3 * 2)
        self.assertEqual(plan['runs_now_at_most'], 60 * (44 + 10 + 8 + 1) + lc)
        self.assertEqual(plan['datasets']['citrusfarm']['runs']['test_later_vio'], 40)
        self.assertGreater(plan['wall_hours_now'], 0)


class Clips(unittest.TestCase):
    @staticmethod
    def times(seconds, rate=10):
        return [1000 * SECOND + i * SECOND // rate for i in range(int(seconds * rate) + 1)]

    def test_start_and_midpoint(self):
        times = self.times(800)
        windows = prepare.clip_windows(times)
        self.assertEqual(windows[1][0], 0)
        self.assertEqual(times[windows[2][0]], times[0] + 400 * SECOND)
        for first, count in windows.values():
            self.assertAlmostEqual((times[first + count - 1] - times[first]) / SECOND, 180, delta=1)
        self.assertEqual(prepare.overlap_seconds(times, windows), 0)

    def test_a_short_recording_keeps_180_seconds_and_reports_its_overlap(self):
        times = self.times(242)
        windows = prepare.clip_windows(times)
        first, count = windows[2]
        self.assertEqual(first + count, len(times))
        self.assertAlmostEqual((times[-1] - times[first]) / SECOND, 180, delta=1)
        self.assertAlmostEqual(prepare.overlap_seconds(times, windows), 118, delta=1)
        with self.assertRaisesRegex(ValueError, 'shorter than one clip'):
            prepare.clip_windows(self.times(170))

    def test_the_real_windows_and_the_disclosed_overlap(self):
        for dataset, sequences in PROTOCOL['views'].items():
            for sequence, view in sequences.items():
                times = prepare.read_times(ROOT / 'datasets' / dataset / sequence / 'times.txt')
                midpoint = (times[-1] - times[0]) / 2e9
                records, overlap = prepare.view_records(times)
                self.assertEqual({str(k): v for k, v in records.items()}, view['clips'])
                self.assertEqual(view['clips']['1']['start_s'], 0)
                if sequence == 'strawberry03':
                    self.assertGreater(overlap, 100)
                else:
                    self.assertEqual(overlap, 0)
                    self.assertAlmostEqual(view['clips']['2']['start_s'], midpoint, delta=.2)
                for clip in view['clips'].values():
                    self.assertAlmostEqual(clip['duration_s'], 180, delta=1)
        self.assertTrue(any('strawberry03' in text and 'overlap' in text for text in PROTOCOL['disclosures']))
        self.assertTrue(any('checked against the first search' in text for text in PROTOCOL['disclosures']))

    def test_a_view_is_an_exact_window_with_copied_tables_and_image_links(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'seq'
            times = self.times(300)
            (source / 'mav0/imu0').mkdir(parents=True)
            (source / 'times.txt').write_text(prepare.times_text(times))
            (source / 'gt_tum.txt').write_text('0 0 0 0 0 0 0 1\n')
            (source / 'manifest.json').write_text('{"profile": "kept"}')
            for camera in ('cam0', 'cam1'):
                data = source / 'mav0' / camera / 'data'
                data.mkdir(parents=True)
                for t in times:
                    (data / f'{t}.png').write_bytes(b'x')
                (data.parent / 'data.csv').write_text('#t,f\n' + ''.join(f'{t},{t}.png\n' for t in times))
            stamps = [times[0] - SECOND + i * SECOND // 100 for i in range(32000)]
            (source / 'mav0/imu0/data.csv').write_text('#t\n' + ''.join(f'{t},0,0,0,0,0,9.8\n' for t in stamps))
            first, count = prepare.clip_windows(times)[2]
            target = Path(directory) / 'clip'
            record = prepare.build_view(source, target, first, count, 'seq')
            self.assertEqual(prepare.read_times(target / 'times.txt'), times[first:first + count])
            self.assertTrue((target / 'gt_tum.txt').is_file())
            self.assertTrue(next((target / 'mav0/cam0/data').iterdir()).is_symlink())
            imu = [r[0] for r in prepare.rows(target / 'mav0/imu0/data.csv')[1]]
            self.assertGreaterEqual(imu[0], times[first] - prepare.IMU_MARGIN_NS)
            self.assertLessEqual(imu[-1], times[first + count - 1] + prepare.IMU_MARGIN_NS)
            manifest = json.loads((target / 'manifest.json').read_text())
            self.assertEqual(manifest['profile'], 'kept')
            self.assertEqual(manifest['experiment_subset']['parent_offset'], first)
            prefix = json.loads((target / 'experiment-prefix.json').read_text())
            self.assertEqual((prefix['parent_sequence'], prefix['parent_offset'], prefix['diagnostic_only']), ('seq', first, True))
            self.assertEqual(record['times_sha256'], prefix['subset_times_sha256'])


class RunIds(unittest.TestCase):
    def blocks(self):
        ids = PROTOCOL['run_ids']
        return list(ids['fold_blocks'].values()) + list(ids['check_blocks'].values()) + list(ids['gate_blocks'].values())

    def test_blocks_are_disjoint_inside_70000_76999(self):
        self.assertEqual(PROTOCOL['run_ids']['range'], [70000, 76999])
        ordered = sorted(self.blocks())
        self.assertTrue(all(a[1] < b[0] for a, b in zip(ordered, ordered[1:])))
        self.assertGreaterEqual(ordered[0][0], 70000)
        self.assertLessEqual(ordered[-1][1], 76999)
        self.assertEqual(set(PROTOCOL['run_ids']['fold_blocks']), {f['id'] for f in PROTOCOL['folds']})

    def test_a_fold_block_holds_every_planned_attempt_with_room_for_replacements(self):
        first, last = PROTOCOL['run_ids']['fold_blocks'][PROTOCOL['folds'][0]['id']]
        self.assertGreaterEqual(last - first + 1, 2 * sum(coordinator.fold_runs(PROTOCOL, PROTOCOL['folds'][0]).values()) - 40)

    def test_ids_come_from_the_block_and_replay_to_the_same_id(self):
        fold = PROTOCOL['folds'][3]['id']
        with tempfile.TemporaryDirectory() as directory, patch.object(engine, 'CAMPAIGN', PROTOCOL['campaign_id']), \
                patch.object(engine, 'PROTOCOL', PROTOCOL), patch.object(engine, 'ART', Path(directory)):
            first = engine.identities(fold, 'a', 'seq04', 'vio', 1, 'screen')
            second = engine.identities(fold, 'b', 'seq04', 'vio', 1, 'screen')
            self.assertEqual(first, engine.identities(fold, 'a', 'seq04', 'vio', 1, 'screen'))
        low, high = PROTOCOL['run_ids']['fold_blocks'][fold]
        self.assertEqual((first[1], second[1]), (low, low + 1))
        self.assertLessEqual(second[1], high)

    def test_an_exhausted_block_fails_closed(self):
        protocol = dict(run_ids=dict(fold_blocks={'x': [70000, 70000]}))
        with tempfile.TemporaryDirectory() as directory, patch.object(engine, 'CAMPAIGN', 'c'), \
                patch.object(engine, 'PROTOCOL', protocol), patch.object(engine, 'ART', Path(directory)):
            engine.identities('x', 'a', 's', 'vio', 1, 'full')
            with self.assertRaisesRegex(RuntimeError, 'exhausted'):
                engine.identities('x', 'b', 's', 'vio', 1, 'full')

    def test_checks_and_gates_use_their_own_blocks(self):
        with patch.object(engine, 'PROTOCOL', PROTOCOL):
            fold = PROTOCOL['gates']['repro']['targets'][0]['fold']
            self.assertGreaterEqual(engine.run_block(fold, 'gate_repro')[0], 76300)
            self.assertGreaterEqual(engine.run_block(fold, 'check')[0], 76000)
            self.assertLess(engine.run_block(fold, 'full')[1], 76000)


class Exclusions(unittest.TestCase):
    def test_no_sielinko_study_view_or_pin(self):
        text = json.dumps({k: v for k, v in PROTOCOL.items() if k not in ('exclusions', 'decisions', 'limitations')})
        self.assertEqual({f['dataset'] for f in PROTOCOL['folds']}, {'citrusfarm', 'hortimulti', 'rosariov2'})
        self.assertEqual(set(PROTOCOL['run_order']), {'citrusfarm', 'hortimulti', 'rosariov2'})
        self.assertNotIn('zed2i', text)
        self.assertNotIn('field1', text)

    def test_the_search_depends_on_no_rule_c_stop_file_and_no_results_lock(self):
        self.assertFalse(hasattr(coordinator, 'EXTERNAL_STOPS'))
        for name in ('timing_search', 'timing_lanes', 'noise_campaign', 'noise_campaign_engine', 'noise_pilot', 'prepare_timing_search'):
            text = (ROOT / 'scripts/analysis' / (name + '.py')).read_text()
            self.assertNotIn('rule-c-batch', text)
            self.assertNotIn('execution.lock', text)
            self.assertNotIn("'.locks", text)
        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNone(coordinator.stop_reason(directory))

    def test_the_protocol_file_is_what_the_builder_writes(self):
        self.assertEqual(prepare.json_text(prepare.protocol(ROOT, prepare.view_data(), MOTION)), prepare.PROTOCOL.read_text())


class Inputs(unittest.TestCase):
    def test_corrected_citrusfarm_is_selected_by_hash(self):
        variants = PROTOCOL['input_variants']['citrusfarm']
        self.assertTrue(variants['seq07']['imu_sha256'].startswith('1629baf2'))
        self.assertTrue(variants['seq04']['imu_sha256'].startswith('9ec219ee'))
        self.assertEqual({v['variant'] for v in variants.values()}, {'corrected'})
        self.assertEqual({v['variant'] for d in ('hortimulti', 'rosariov2') for v in PROTOCOL['input_variants'][d].values()},
                         {'authors_unchanged'})
        for sequence, record in MOTION['datasets']['citrusfarm']['sequences'].items():
            self.assertEqual(record['sha256'], variants[sequence]['imu_sha256'])
        script = (ROOT / 'timing-search/setup_private.sh').read_text()
        for value in prepare.CORRECTED_IMU_SHA256.values():
            self.assertIn(value, script)

    def fake_tree(self, directory, link='corrected', content=b'corrected'):
        root = Path(directory)
        for sequence in ('seq04', 'seq07'):
            folder = root / f'datasets/.timing-imu/citrusfarm__{sequence}/{link}'
            folder.mkdir(parents=True)
            (folder / 'data.csv').write_bytes(content)
            mav0 = root / 'datasets/citrusfarm' / sequence / 'mav0'
            mav0.mkdir(parents=True)
            (mav0 / 'imu0').symlink_to(f'../../../.timing-imu/citrusfarm__{sequence}/{link}')
        return root

    def test_input_selection_refuses_the_wrong_variant_or_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, 'corrected IMU'):
                prepare.verify_input_selection(self.fake_tree(directory, link='unchanged'))
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, 'corrected IMU'):
                prepare.verify_input_selection(self.fake_tree(directory))

    @unittest.skipUnless((ROOT / 'datasets/citrusfarm/seq04/mav0/imu0').is_symlink(), 'private datasets not set up')
    def test_this_worktree_reads_the_selected_inputs(self):
        prepare.verify_input_selection(ROOT)

    def test_m_refuses_uncorrected_citrusfarm(self):
        with patch.object(prepare, 'CORRECTED_IMU_SHA256', dict.fromkeys(('seq04', 'seq07'), '0' * 64)):
            with self.assertRaisesRegex(RuntimeError, 'corrected IMU'):
                prepare.motion_document(ROOT)


class Lanes(unittest.TestCase):
    def test_lanes_per_system(self):
        self.assertEqual({k: v['cpus'] for k, v in PROTOCOL['lanes'].items()},
                         dict(cpu_a='0-3', cpu_b='4-7', gpu='16-23', exclusive='0-7'))
        expected = dict(orbslam3=['cpu_a', 'cpu_b'], okvis2=['cpu_a', 'cpu_b'], okvis2x=['cpu_a', 'cpu_b'],
                        openvins=['cpu_a', 'cpu_b'], voxel_svio=['cpu_a', 'cpu_b'], svo_pro=['cpu_a', 'cpu_b'],
                        cuvslam=['gpu'], airslam=['gpu'], mast3r_fusion=['gpu'], basalt=['exclusive'])
        for fold in PROTOCOL['folds']:
            self.assertEqual(fold['lanes'], expected[fold['algorithm']])

    def test_each_estimator_stays_on_one_core_type(self):
        for fold in PROTOCOL['folds']:
            self.assertEqual(len({PROTOCOL['lanes'][l]['core_type'] for l in fold['lanes']}), 1)

    def test_memory_caps_and_launch_policy_as_rule_c(self):
        limits = PROTOCOL['attempt_resource_limits']
        for algorithm, limit in limits.items():
            gpu = algorithm in ('cuvslam', 'airslam', 'mast3r_fusion')
            self.assertEqual(limit['memory_gib'], 50 if gpu else 64)
            self.assertEqual(limit['swap_gib'], 0)
        self.assertEqual(PROTOCOL['launch_policy']['min_available_gib'], 40)

    def fold(self, algorithm, dataset='citrusfarm'):
        return next(f for f in PROTOCOL['folds'] if f['algorithm'] == algorithm and f['dataset'] == dataset)

    def lane(self, algorithm, active=(), pending=()):
        running = {lane: (self.fold(name), None) for lane, name in active}
        return coordinator.lane_for(self.fold(algorithm), running, list(pending), PROTOCOL)

    def test_one_fold_per_lane_and_one_algorithm_at_a_time_except_orbslam3(self):
        self.assertEqual(self.lane('orbslam3'), 'cpu_a')
        self.assertEqual(self.lane('okvis2', [('cpu_a', 'orbslam3')]), 'cpu_b')
        self.assertIsNone(self.lane('okvis2x', [('cpu_a', 'orbslam3'), ('cpu_b', 'okvis2')]))
        self.assertIsNone(self.lane('okvis2', [('cpu_a', 'okvis2')]))
        self.assertEqual(self.lane('orbslam3', [('cpu_a', 'orbslam3')]), 'cpu_b')
        self.assertEqual(self.lane('svo_pro', [('cpu_a', 'openvins')]), 'cpu_b')
        self.assertIsNone(self.lane('svo_pro', [('cpu_a', 'openvins'), ('cpu_b', 'voxel_svio')]))
        self.assertIsNone(self.lane('voxel_svio', [('cpu_a', 'voxel_svio')]))
        self.assertIsNone(self.lane('airslam', [('gpu', 'cuvslam')]))

    def test_basalt_runs_alone_and_last(self):
        self.assertIsNone(self.lane('basalt', pending=[self.fold('okvis2')]))
        self.assertIsNone(self.lane('basalt', [('gpu', 'cuvslam')]))
        self.assertEqual(self.lane('basalt', pending=[self.fold('basalt')]), 'exclusive')
        self.assertIsNone(self.lane('okvis2', [('exclusive', 'basalt')]))

    def blockers(self, lane, **overrides):
        values = dict(snapshot=[], memory={'MemAvailable': 100 * GIB}, gpu=[], disk_free=500 * GIB, benchmark_swap=0)
        values.update(overrides)
        return lanes.launch_blockers(PROTOCOL, lane, **values)

    def wrapper(self, algorithm, cpus):
        return dict(pid=5, argv=['bash', f'/x/scripts/run/run_{algorithm}.sh'], cpus=cpus, cgroup='0::/x')

    def test_launch_needs_memory_free_cores_and_a_free_gpu(self):
        self.assertEqual(self.blockers('cpu_b'), [])
        self.assertTrue(self.blockers('cpu_b', memory={'MemAvailable': 39 * GIB}))
        self.assertTrue(self.blockers('cpu_b', snapshot=[self.wrapper('openvins', [4, 5, 6, 7])]))
        self.assertEqual(self.blockers('cpu_b', snapshot=[self.wrapper('openvins', [0, 1, 2, 3])]), [])
        self.assertTrue(self.blockers('cpu_b', snapshot=[self.wrapper('basalt', [4, 5, 6, 7])]))
        self.assertTrue(self.blockers('gpu', gpu=[123]))
        self.assertTrue(self.blockers('gpu', gpu=None))
        self.assertEqual(self.blockers('cpu_a', gpu=[123]), [])
        self.assertTrue(self.blockers('exclusive', snapshot=[self.wrapper('cuvslam', [16])]))


class WinnerAndTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.engine = FakeEngine(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def search(self, algorithm='okvis2'):
        fold = next(f for f in PROTOCOL['folds'] if f['algorithm'] == algorithm and f['dataset'] == 'citrusfarm')
        return fold, policy.DevelopmentSearch(self.engine, fold, PROTOCOL)

    def test_the_winner_is_the_best_n3_candidate_and_runs_only_on_the_other_sequence(self):
        fold, search = self.search()
        selected = search.develop()
        loss = [c['loss'] for c in selected['repeated_candidates']]
        self.assertEqual(selected['winner']['loss'], min(loss))
        tuning = set(self.engine.records)
        final = search.final_n1()
        rows = [self.engine.records[k] for k in final['records']]
        self.assertEqual({(r['sequence'], r['mode'], r['repetition']) for r in rows},
                         {(fold['test_sequence'], 'vio', 1), (fold['test_sequence'], 'vio-lc', 1)})
        self.assertTrue(all(r['params'] == selected['winner']['params'] for r in rows))
        self.assertFalse(tuning & set(final['records']))
        self.assertFalse({r['sequence'] for k, r in self.engine.records.items() if k in tuning} & {fold['test_sequence']})

    def test_vio_only_systems_skip_loop_closure(self):
        fold, search = self.search('openvins')
        search.develop()
        rows = [self.engine.records[k] for k in search.final_n1()['records']]
        self.assertEqual([r['mode'] for r in rows], ['vio'])

    def test_test_later_adds_two_vio_repetitions_and_needs_the_first(self):
        fold, search = self.search()
        search.develop()
        with self.assertRaisesRegex(RuntimeError, 'first test repetition'):
            search.final_later()
        search.final_n1()
        rows = [self.engine.records[k] for k in search.final_later()['records']]
        self.assertEqual({(r['sequence'], r['mode'], r['repetition']) for r in rows},
                         {(fold['test_sequence'], 'vio', 2), (fold['test_sequence'], 'vio', 3)})

    def test_a_test_run_never_changes_the_selection(self):
        _, search = self.search()
        search.develop()
        before = (search.directory / 'selection.json').read_bytes()
        search.final_n1()
        search.final_later()
        self.assertEqual(before, (search.directory / 'selection.json').read_bytes())

    def test_a_test_sequence_used_in_tuning_is_refused(self):
        fold, search = self.search()
        search.develop()
        search.spec = dict(fold, test_sequences=fold['full_sequences'])
        with self.assertRaisesRegex(RuntimeError, 'used in tuning'):
            search.final_n1()


class Coordinator(unittest.TestCase):
    def test_gate_stages_cover_the_systems_and_the_two_reproduction_folds(self):
        check = coordinator.stage_folds(PROTOCOL, 'check', 'citrusfarm')
        self.assertEqual({f['algorithm'] for f in check}, set(prepare.SYSTEMS))
        self.assertEqual(len(check), 10)
        repro = coordinator.stage_folds(PROTOCOL, 'gate-repro', None)
        self.assertEqual({(f['algorithm'], f['tune_sequence']) for f in repro}, {('openvins', 'seq04'), ('voxel_svio', 'seq04')})
        self.assertEqual({tuple(f['lanes']) for f in repro}, {('cpu_a', 'cpu_b')})
        self.assertEqual(len(coordinator.stage_folds(PROTOCOL, 'develop', 'rosariov2')), 20)
        with self.assertRaises(ValueError):
            coordinator.stage_folds(PROTOCOL, 'develop', 'zed2i')

    def test_reproduction_verdict(self):
        targets = {t['fold']: t['expected_m'] for t in PROTOCOL['gates']['repro']['targets']}
        report = dict(studies={k: dict(ate_se3_rmse_m=[v * 1.05]) for k, v in targets.items()})
        self.assertTrue(coordinator.repro_verdict(report, PROTOCOL)['passed'])
        first = next(iter(targets))
        report['studies'][first]['ate_se3_rmse_m'] = [targets[first] * 1.2]
        self.assertFalse(coordinator.repro_verdict(report, PROTOCOL)['passed'])
        report['studies'][first]['ate_se3_rmse_m'] = []
        self.assertFalse(coordinator.repro_verdict(report, PROTOCOL)['passed'])

    def test_datasets_run_in_order_after_review(self):
        self.assertEqual(PROTOCOL['run_order'], ['citrusfarm', 'hortimulti', 'rosariov2'])
        with tempfile.TemporaryDirectory() as directory:
            art = Path(directory)
            coordinator.verify_order(art, PROTOCOL, 'citrusfarm')
            with self.assertRaisesRegex(RuntimeError, 'review of citrusfarm'):
                coordinator.verify_order(art, PROTOCOL, 'hortimulti')
            (art / 'reviews').mkdir()
            (art / 'reviews/citrusfarm.json').write_text('{"passed": true}')
            coordinator.verify_order(art, PROTOCOL, 'hortimulti')
            with self.assertRaisesRegex(RuntimeError, 'review of hortimulti'):
                coordinator.verify_order(art, PROTOCOL, 'rosariov2')

    def test_test_needs_develop_and_later_needs_test(self):
        folds = coordinator.stage_folds(PROTOCOL, 'develop', 'citrusfarm')[:1]
        with tempfile.TemporaryDirectory() as directory:
            art = Path(directory)
            with self.assertRaisesRegex(RuntimeError, 'needs develop'):
                coordinator.verify_stage_order(art, 'test', folds)
            completion = coordinator.worker_directory(art, folds[0], 'develop') / 'develop-completion.json'
            completion.parent.mkdir(parents=True)
            completion.write_text('{"complete": true}')
            coordinator.verify_stage_order(art, 'test', folds)
            with self.assertRaisesRegex(RuntimeError, 'needs test'):
                coordinator.verify_stage_order(art, 'test-later', folds)


class Launched(unittest.TestCase):
    """Run the attempt code up to the point of launch, for each system. Popen is replaced, so nothing starts."""

    class Launch(Exception):
        pass

    def attempt(self, algorithm, dataset, lane, mode='vio', sequence=None):
        fold = next(f for f in PROTOCOL['folds'] if f['algorithm'] == algorithm and f['dataset'] == dataset)
        protocol = copy.deepcopy(PROTOCOL)
        protocol.update(campaign_id='unit-test-only', frozen_input_sha256={f"{dataset}/{s}": '0' * 64 for s in fold['sequence_parents']},
                        frozen_runtime_sha256={algorithm: '1' * 64}, frozen_source_sha256={algorithm: '2' * 64})
        seen = {}

        def popen(command, **kwargs):
            seen.update(command=command, env=kwargs['env'])
            raise self.Launch()

        generated = ROOT / 'configs/experiments/generated/unit-test-only'
        self.addCleanup(shutil.rmtree, generated, ignore_errors=True)
        with tempfile.TemporaryDirectory() as directory:
            art = Path(directory)
            (art / 'budget.json').write_text(json.dumps(dict(started_unix=0, deadline_unix=4e9)))
            with patch.object(engine.base, 'reference_distance', return_value=100.), \
                    patch.object(engine, 'verify_frozen'), patch.object(engine.noise_cleanup, 'owned_container', return_value=(None, 'persistent')), \
                    patch.object(engine.execution_policy, 'verify_persistent_limits'), \
                    patch.object(engine.noise_cleanup, 'stop_owned_attempt'), \
                    patch.object(engine.subprocess, 'Popen', side_effect=popen):
                engine.configure(art, protocol, nullcontext, lane=lane)
                sequence = sequence or fold['clips'][1]
                with self.assertRaises(self.Launch):
                    engine.run_attempt(fold, 'probe', fold['controls'][0]['params'], sequence, mode, 1, 'screen')
                record = json.loads((art / 'attempts' / f"screen__{fold['id']}__probe__{sequence}__{mode}__rep1.json").read_text())
                ledger = json.loads((art / 'run-ids.json').read_text())
        return fold, seen, record, ledger

    def test_each_system_reaches_its_lane_wrapper_with_its_noise_file(self):
        lanes_by_system = dict(orbslam3='cpu_a', okvis2='cpu_b', okvis2x='cpu_a', openvins='cpu_b', voxel_svio='cpu_a',
                               svo_pro='cpu_b', basalt='exclusive', cuvslam='gpu', airslam='gpu', mast3r_fusion='gpu')
        hooks = dict(orbslam3='ORBSLAM3_CONFIG', okvis2='OKVIS2_CONFIG', okvis2x='OKVIS2X_CONFIG', openvins='OPENVINS_CONFIG_DIR',
                     voxel_svio='VOXEL_SVIO_CONFIG', svo_pro='SVO_PRO_IMU_NOISE', basalt='BASALT_CALIBRATION',
                     cuvslam='CUVSLAM_IMU_NOISE', airslam='AIRSLAM_CAMERA_CONFIG', mast3r_fusion='MAST3R_FUSION_IMU_NOISE')
        for algorithm, lane in lanes_by_system.items():
            for dataset in prepare.DATASETS:
                with self.subTest(algorithm=algorithm, dataset=dataset):
                    fold, seen, record, ledger = self.attempt(algorithm, dataset, lane)
                    command, env = seen['command'], seen['env']
                    self.assertEqual(command[:5], ['systemd-run', '--user', '--scope', '--quiet', command[4]])
                    self.assertIn(f"MemoryMax={PROTOCOL['attempt_resource_limits'][algorithm]['memory_gib']}G", command)
                    self.assertIn('MemorySwapMax=0', command)
                    at = command.index('taskset')
                    self.assertEqual(command[at + 1:at + 3], ['--cpu-list', PROTOCOL['lanes'][lane]['cpus']])
                    self.assertEqual(command[at + 3:at + 5], ['bash', str(ROOT / f'scripts/run/run_{algorithm}.sh')])
                    self.assertEqual(command[at + 5:at + 7], [dataset, fold['clips'][1]])
                    self.assertTrue(Path(env[hooks[algorithm]]).exists())
                    self.assertEqual(env['GIT_OPTIONAL_LOCKS'], '0')
                    run_id = int(command[at + 7])
                    low, high = PROTOCOL['run_ids']['fold_blocks'][fold['id']]
                    self.assertTrue(low <= run_id <= high and run_id in ledger.values())
                    if algorithm in ('openvins', 'svo_pro'):
                        self.assertEqual(env['TIMING_CPUS'], PROTOCOL['lanes'][lane]['cpus'])
                        self.assertEqual(env['TIMING_MEM'], str(64 * GIB))

    def test_loop_closure_reaches_the_wrapper_on_a_test_sequence(self):
        for algorithm, lane in (('okvis2', 'cpu_a'), ('orbslam3', 'cpu_b'), ('airslam', 'gpu'), ('svo_pro', 'cpu_a'),
                                ('cuvslam', 'gpu'), ('mast3r_fusion', 'gpu'), ('okvis2x', 'cpu_b')):
            with self.subTest(algorithm=algorithm):
                fold = next(f for f in PROTOCOL['folds'] if f['algorithm'] == algorithm and f['dataset'] == 'citrusfarm')
                _, seen, _, _ = self.attempt(algorithm, 'citrusfarm', lane, mode='vio-lc', sequence=fold['test_sequence'])
                self.assertEqual(seen['command'][-1], 'vio-lc')


if __name__ == '__main__':
    unittest.main()
