"""Sielinko CPU search: split, views, controls, lanes and scheduling, without any run."""
import copy
import fcntl
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ART = Path(__file__).resolve().parent
WORK = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(WORK / 'scripts/analysis'), str(WORK / 'scripts/run'), str(WORK / 'scripts/eval')]
import noise_campaign_search as policy
import noise_execution_policy as execution_policy
import noise_pilot
import prepare_sielinko_search as prepare
import sielinko_lanes as lanes
import sielinko_search as coordinator
from _reference_source import selected_reference

from test_noise_campaign import FakeEngine

GIB = 1024**3
SECOND = 10**9


def synthetic_recording(root, frames=400, period_ns=SECOND // 10, start=1_000_000_000_000):
    """EuRoC-layout recording: 10 Hz stereo, 100 Hz IMU starting after the first image."""
    root = Path(root)
    times = [start + i * period_ns for i in range(frames)]
    (root / 'mav0/imu0').mkdir(parents=True)
    (root / 'times.txt').write_text('\n'.join(map(str, times)) + '\n')
    for camera in ('cam0', 'cam1'):
        data = root / 'mav0' / camera / 'data'
        data.mkdir(parents=True)
        rows = ['#timestamp [ns],filename']
        for t in times:
            (data / f'{t}.jpg').write_bytes(b'pixels')
            rows.append(f'{t},{t}.jpg')
        (data.parent / 'data.csv').write_text('\n'.join(rows) + '\n')
    imu = [start + 5_000_000 + i * 10_000_000 for i in range(frames * 10)]
    (root / 'mav0/imu0/data.csv').write_text('#timestamp [ns],wx,wy,wz,ax,ay,az\n' +
                                             ''.join(f'{t},0,0,0,0,0,9.8\n' for t in imu))
    (root / 'manifest.json').write_text(json.dumps(dict(dataset='synthetic', duration_s=frames / 10)))
    return times, imu


class SplitAndViews(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sielinko-views-', dir=ART)
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_windows_split_at_time_midpoint_with_clips_inside_first_half(self):
        times = [i * SECOND // 10 for i in range(46283)]
        views = prepare.windows(times)
        first, count = views['half1']
        self.assertEqual(views['half2'], (count, len(times) - count))
        self.assertLess(times[count - 1], times[-1] / 2)
        self.assertGreaterEqual(times[count], times[-1] / 2)
        self.assertEqual(views['clip1'], (0, 1800))
        start, length = views['clip2']
        self.assertAlmostEqual(times[start], times[count - 1] / 2, delta=SECOND // 10)
        self.assertLessEqual(start + length, count)
        self.assertEqual(views['full'], (0, len(times)))

    def test_windows_refuse_a_recording_too_short_for_clips(self):
        with self.assertRaises(ValueError):
            prepare.windows([i * SECOND for i in range(200)])

    def test_real_recording_plan_matches_the_posted_design(self):
        plan = prepare.plan(prepare.MAIN / 'datasets/zed2i' / prepare.PARENT)
        self.assertEqual((plan['half1']['count'], plan['half2']['count']), (23141, 23142))
        self.assertAlmostEqual(plan['clip2']['start_s'], 1157.3, delta=0.1)
        self.assertTrue(all(abs(plan[c]['duration_s'] - 180) < 0.2 for c in ('clip1', 'clip2')))

    def test_view_is_an_exact_window_with_linked_images_and_bounded_imu(self):
        source = self.root / 'parent'
        times, imu = synthetic_recording(source)
        target = self.root / 'window'
        record = prepare.build_view(source, target, 100, 50, 'parent')
        self.assertEqual([int(x) for x in (target / 'times.txt').read_text().split()], times[100:150])
        self.assertEqual(record['times_sha256'], noise_pilot.sha(target / 'times.txt'))
        for camera in ('cam0', 'cam1'):
            links = sorted((target / 'mav0' / camera / 'data').iterdir())
            self.assertEqual(len(links), 50)
            self.assertTrue(all(p.is_symlink() and p.resolve().parent == (source / 'mav0' / camera / 'data').resolve()
                                for p in links))
        kept = [int(r.split(',')[0]) for r in (target / 'mav0/imu0/data.csv').read_text().splitlines()[1:]]
        self.assertEqual(kept, [t for t in imu if times[100] - 20_000_000 <= t <= times[149] + 20_000_000])
        manifest = json.loads((target / 'manifest.json').read_text())['experiment_subset']
        self.assertEqual((manifest['kind'], manifest['parent_offset'], manifest['input_frames']), ('exact_window', 100, 50))
        self.assertEqual((target / 'cam0').resolve(), (target / 'mav0/cam0/data').resolve())
        with self.assertRaises(FileExistsError):
            prepare.build_view(source, target, 100, 50, 'parent')

    def test_prefix_view_keeps_the_parent_imu_head(self):
        source = self.root / 'parent'
        times, imu = synthetic_recording(source)
        target = self.root / 'prefix'
        prepare.build_view(source, target, 0, 30, 'parent')
        kept = [int(r.split(',')[0]) for r in (target / 'mav0/imu0/data.csv').read_text().splitlines()[1:]]
        self.assertEqual(kept, [t for t in imu if t <= times[29] + 20_000_000])
        self.assertEqual(json.loads((target / 'manifest.json').read_text())['experiment_subset']['kind'], 'exact_prefix')

    def test_view_records_match_built_views(self):
        source = self.root / 'parent'
        synthetic_recording(source, frames=4000)
        with patch.object(prepare, 'CLIP_S', 30):
            records = prepare.view_records(source)
            for view, (first, count) in prepare.windows([int(x) for x in (source / 'times.txt').read_text().split()]).items():
                built = prepare.build_view(source, self.root / view, first, count, 'parent')
                self.assertEqual(built['times_sha256'], records[view]['times_sha256'])

    def test_window_reference_selector_accepts_exact_window_only(self):
        ws = self.root / 'ws'
        parent, window = ws / 'datasets/zed2i/parent', ws / 'datasets/zed2i/window'
        times, _ = synthetic_recording(parent)
        prepare.build_view(parent, window, 100, 50, 'parent')
        reference_dir = parent / 'references/v1'
        reference_dir.mkdir(parents=True)
        (reference_dir / 'primary.tum').write_text(''.join(f'{t / 1e9} {i * .1} 0 0 0 0 0 1\n' for i, t in enumerate(times)))
        (reference_dir / 'support.json').write_text(json.dumps(dict(valid_intervals=[[times[0] / 1e9, times[-1] / 1e9]])))
        def bound(path):
            return dict(path=str(path.relative_to(ws)), sha256=noise_pilot.sha(path))
        document = dict(dataset='zed2i', sequence='parent', version='v1', limitations=[], orientation_valid=False,
                        nominal_geometry=True, variants=dict(primary=dict(trajectory=bound(reference_dir / 'primary.tum'),
                                                                          support=bound(reference_dir / 'support.json'))))
        (reference_dir / 'reference.json').write_text(json.dumps(document))
        selector = dict(schema=1, dataset='zed2i', sequence='window', variant='primary',
                        reference=bound(reference_dir / 'reference.json'), diagnostic_parent_sequence='parent',
                        diagnostic_only=True, subset_times=bound(window / 'times.txt'),
                        parent_times=bound(parent / 'times.txt'), parent_offset=100)
        path = ws / 'configs/references/zed2i_window.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(selector))
        self.assertEqual(selected_reference(ws, 'zed2i', 'window')['physical_sequence'], 'parent')
        for offset, message in ((99, 'exact parent window'), (0, 'exact parent prefix'), (-1, 'offset')):
            path.write_text(json.dumps(dict(selector, parent_offset=offset)))
            with self.subTest(offset=offset), self.assertRaisesRegex(ValueError, message):
                selected_reference(ws, 'zed2i', 'window')


class ProtocolChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        records = {view: dict(first=0, count=1, times_sha256='0' * 64) for view in prepare.VIEWS}
        cls.protocol = prepare.protocol(records)

    def test_three_distinct_controls_in_fixed_order_and_bounds_cover_them(self):
        for spec in self.protocol['studies']:
            with self.subTest(study=spec['id']):
                self.assertEqual([c['label'] for c in spec['controls']], ['rule_c', 'engine_on', 'envelope'])
                self.assertEqual(len(policy.controls(spec)), 3)
                for control in spec['controls']:
                    for key, (low, high) in spec['bounds'].items():
                        self.assertLess(low, control['params'][key])
                        self.assertGreater(high, control['params'][key])
                self.assertEqual(policy.label_for(spec, spec['controls'][1]['params']), 'engine_on')

    def test_rule_c_control_is_the_production_rule(self):
        import _imu_noise_rule
        for spec in self.protocol['studies']:
            rule = _imu_noise_rule.noise(spec['algorithm'], 'zed2i')
            for key in policy.KEYS:
                self.assertTrue(math.isclose(spec['controls'][0]['params'][key], rule[key], rel_tol=1e-12))

    def test_selection_never_sees_the_second_half(self):
        half2 = prepare.VIEWS['half2']
        for spec in self.protocol['studies']:
            self.assertNotIn(half2, spec['clips'] + spec['full_sequences'])
            self.assertEqual(spec['test_sequences'], [half2, prepare.PARENT])
            self.assertEqual((spec['final_controls'], spec['final_control_sequences']), (['rule_c'], [half2]))
            self.assertEqual(spec['final_modes'], ['vio'])
            self.assertEqual(set(spec['sequence_roles'].values()), {'short', 'half', 'full'})
            self.assertTrue(set(spec['sequence_roles'].values()) <= set(self.protocol['attempt_timeouts_s'][spec['algorithm']]))

    def test_private_voxel_container_is_the_one_the_engine_owns(self):
        import noise_cleanup
        import noise_campaign_engine as engine
        container = self.protocol['runtime_environment']['voxel_svio']['VOXEL_SVIO_CONTAINER']
        self.assertEqual(container, noise_cleanup.PERSISTENT['voxel_svio'])
        self.assertNotEqual(container, 'voxel_svio')
        # Stray hook values in the controller environment never reach an attempt.
        for name in ('VOXEL_SVIO_CONFIG', 'SVO_PRO_IMU_NOISE', 'VOXEL_SVIO_CONTAINER', 'OPENVINS_CPUSET',
                     'SVO_PRO_CPUSET', 'ORBSLAM3_CONFIG', 'OKVIS2_CONFIG', 'OKVIS2X_CONFIG', 'BASALT_CALIBRATION',
                     'OPENVINS_CONFIG_DIR', 'SVO_PRO_IMU_FILE', 'OPENVINS_MEMORY_LIMIT', 'SVO_PRO_MEMORY_LIMIT'):
            self.assertIn(name, engine.CONFIG_ENVIRONMENT)

    def test_lanes_and_limits(self):
        lanes_ = self.protocol['lanes']
        self.assertEqual((lanes_['lane1']['cpus'], lanes_['lane2']['cpus'], lanes_['exclusive']['cpus']), ('0-3', '4-7', '0-7'))
        self.assertEqual({s['id']: s['lane'] for s in self.protocol['studies'] if s['lane']},
                         {'voxel_svio_zed2i': 'lane2', 'basalt_zed2i': 'exclusive'})
        self.assertEqual(self.protocol['studies'][-1]['algorithm'], 'basalt')
        self.assertTrue(all(v == dict(memory_gib=50, swap_gib=0) for v in self.protocol['attempt_resource_limits'].values()))
        self.assertLessEqual(max(t['full'] for t in self.protocol['attempt_timeouts_s'].values()), 6 * 3600)
        self.assertIsNone(self.protocol['lane_handover'])
        self.assertTrue(all(lane['locks'] == [] for lane in lanes_.values()))
        with lanes.lane_locks(self.protocol, 'lane1', stop=lambda: True):
            pass  # no declared lock: nothing to wait for


class SearchWithHeldOutTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sielinko-policy-', dir=ART)
        self.engine = FakeEngine(Path(self.temp.name))
        self.spec = dict(id='synthetic', algorithm='orbslam3', dataset='zed2i', supports_lc=True, final_modes=['vio'],
            controls=[dict(label='rule_c', params={k: 1. for k in policy.KEYS}),
                      dict(label='engine_on', params={k: 3. for k in policy.KEYS}),
                      dict(label='envelope', params={k: 9. for k in policy.KEYS})],
            bounds={k: [.1, 100.] for k in policy.KEYS}, clips=['clip1', 'clip2'], full_sequences=['half1'],
            test_sequences=['half2', 'full'], final_controls=[])
        self.protocol = dict(
            preliminary=dict(seed=20261009, candidates=16, startup=8, finalists=2, repetitions=3),
            screen=dict(seeds=[202610091, 202610092], candidates_per_seed=16, startup=8),
            full=dict(seed=202610093, candidates=12, seed_candidates=6, finalists=2, repetitions=3))
        self.search = policy.DevelopmentSearch(self.engine, self.spec, self.protocol)

    def tearDown(self):
        self.temp.cleanup()

    def test_development_uses_only_first_half_material_and_all_controls(self):
        selected = self.search.develop()
        used = {r['sequence'] for r in self.engine.records.values()}
        self.assertEqual(used, {'clip1', 'clip2', 'half1'})
        confirmed = {policy.identity(c['params']) for c in selected['repeated_candidates']}
        self.assertTrue({policy.identity(c['params']) for c in self.spec['controls']} <= confirmed)
        for candidate in selected['repeated_candidates']:
            self.assertEqual(len(candidate['records']), 3)
        short = [r for r in self.engine.records.values() if r['sequence'].startswith('clip')]
        half = [r for r in self.engine.records.values() if r['sequence'] == 'half1']
        self.assertEqual(len(short), 98)
        self.assertLessEqual(len(half), 22)

    def test_final_runs_winner_on_test_sequences_and_declared_controls(self):
        self.search.develop()
        development = set(self.engine.records)
        final = self.search.final_n1()
        self.assertEqual([self.engine.records[k]['sequence'] for k in final['records']], ['half2', 'full'])
        self.assertFalse(set(final['records']) & development)
        self.assertIn('never measured the test sequences', final['note'])
        self.spec.update(final_controls=['rule_c'], final_control_sequences=['half2'])
        (self.search.directory / 'final-n1.json').unlink()
        final = self.search.final_n1()
        rows = [(self.engine.records[k]['params'][policy.KEYS[0]], self.engine.records[k]['sequence'])
                for k in final['records']]
        winner = json.loads((self.search.directory / 'selection.json').read_text())['winner']['params']
        if policy.identity(winner) == policy.identity(self.spec['controls'][0]['params']):
            self.assertEqual([s for _, s in rows], ['half2', 'full'])
        else:
            self.assertEqual(rows[2:], [(1., 'half2')])  # Rule C only on the held-out half
            self.assertEqual(len(rows), 3)


class LaneChecks(unittest.TestCase):
    def setUp(self):
        records = {view: dict(first=0, count=1, times_sha256='0' * 64) for view in prepare.VIEWS}
        self.protocol = prepare.protocol(records)
        self.protocol['campaign_id'] = 'lane-test'
        self.free = dict(MemAvailable=100 * GIB, SwapTotal=130 * GIB, SwapFree=130 * GIB)

    @staticmethod
    def wrapper(algorithm, cpus, pid=10, scope='other.scope'):
        return dict(pid=pid, argv=['bash', f'/data/x/scripts/run/run_{algorithm}.sh', 'zed2i'], cgroup='0::/' + scope,
                    cpus=cpus)

    def blockers(self, lane, snapshot, memory=None, gpu=(), benchmark_swap=0):
        return lanes.launch_blockers(self.protocol, lane, snapshot=snapshot, memory=memory or self.free,
                                     gpu=list(gpu) if gpu is not None else None, disk_free=500 * GIB,
                                     benchmark_swap=benchmark_swap)

    def test_free_lane_launches_beside_the_other_lane(self):
        self.assertEqual(self.blockers('lane1', [self.wrapper('orbslam3', [4, 5, 6, 7])]), [])
        self.assertEqual(self.blockers('lane1', [dict(pid=1, argv=['python3', 'x.py'], cgroup='', cpus=[0])]), [])

    def test_memory_foreign_run_on_lane_cores_and_basalt_block(self):
        self.assertTrue(self.blockers('lane1', [], memory=dict(MemAvailable=39 * GIB)))
        self.assertTrue(self.blockers('lane1', [], benchmark_swap=4096))
        self.assertTrue(lanes.launch_blockers(self.protocol, 'lane1', snapshot=[], memory=self.free, disk_free=99 * GIB,
                                              benchmark_swap=0))
        self.assertTrue(self.blockers('lane1', [self.wrapper('okvis2', list(range(24)))]))
        self.assertTrue(self.blockers('lane2', [self.wrapper('okvis2', [3, 4])]))
        self.assertTrue(self.blockers('lane1', [self.wrapper('basalt', [16, 17])]))
        relative = dict(pid=3, argv=['bash', 'scripts/run/run_openvins.sh'], cgroup='', cpus=[0])
        self.assertTrue(self.blockers('lane1', [relative]))

    def test_system_service_swap_does_not_block_benchmark_swap_does(self):
        # User, 24 Oct (Rule C revision 13p): only benchmark cgroups count; here they must hold none at all.
        system = dict(self.free, SwapFree=128 * GIB)
        self.assertEqual(self.blockers('lane1', [], memory=system, benchmark_swap=0), [])
        self.assertIn('benchmark cgroups swap in use (1 bytes)', self.blockers('lane1', [], memory=system, benchmark_swap=1))

    def test_benchmark_swap_counts_only_benchmark_groups(self):
        with tempfile.TemporaryDirectory() as temporary:
            units = Path(temporary) / 'app.slice'
            for name, swap in (('vslam-sielinko-check.service', 10), ('noise-campaign-abc-1.scope', 20),
                               ('tomcat9.service', 1000), ('vscode.scope', 500)):
                (units / name).mkdir(parents=True)
                (units / name / 'memory.swap.current').write_text(str(swap))
            container = Path(temporary) / 'docker-x.scope'
            container.mkdir()
            (container / 'memory.swap.current').write_text('5')
            self.assertEqual(lanes.benchmark_swap_bytes(units, [container]), 35)
            self.assertEqual(lanes.benchmark_swap_bytes(Path(temporary) / 'absent', []), 0)

    def test_exclusive_needs_an_idle_host_and_a_verifiable_idle_gpu(self):
        self.assertEqual(self.blockers('exclusive', []), [])
        self.assertTrue(self.blockers('exclusive', [self.wrapper('orbslam3', [20, 21])]))
        self.assertTrue(self.blockers('exclusive', [], gpu=[1234]))
        self.assertTrue(self.blockers('exclusive', [], gpu=None))

    def test_sampler_findings(self):
        attempt = dict(unit='noise-campaign-x-1', run='/tmp/run1')
        mine = dict(pid=os.getpid(), argv=['bash', '/w/scripts/run/run_basalt.sh'], cgroup='0::/a/noise-campaign-x-1.scope', cpus=[0])
        other = dict(mine, pid=1, cgroup='0::/other.scope')
        with patch.object(lanes, 'thread_affinities', return_value={1: [0, 1, 2, 3], 2: [0, 1]}):
            self.assertEqual(lanes.escaped_threads(self.protocol, 'lane1', attempt, [mine]), [])
        with patch.object(lanes, 'thread_affinities', return_value={7: list(range(24))}):
            self.assertEqual(lanes.escaped_threads(self.protocol, 'lane1', attempt, [mine, other]),
                             [(os.getpid(), 7, list(range(24)))])  # only the attempt's own scope
        self.assertTrue(lanes.sample_errors(self.protocol, 'lane1', attempt, [mine], cpuset='0-7'))
        self.assertEqual(lanes.sample_errors(self.protocol, 'lane1', attempt, [mine], cpuset='0-3'), [])
        self.assertEqual(lanes.sample_errors(self.protocol, 'exclusive', attempt, [mine], gpu=[]), [])
        self.assertTrue(lanes.sample_errors(self.protocol, 'exclusive', attempt, [mine, self.wrapper('cuvslam', [20])], gpu=[]))
        self.assertTrue(lanes.sample_errors(self.protocol, 'exclusive', attempt, [mine], gpu=[99]))

    def test_escaped_thread_is_put_back_on_the_lane_and_logged(self):
        allowed = sorted(os.sched_getaffinity(0))
        self.protocol['lanes']['lane1']['cpus'] = str(allowed[0])
        child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])
        try:
            corrections, errors = lanes.repin(self.protocol, 'lane1', [(child.pid, child.pid, allowed)])
            self.assertEqual(errors, [])
            self.assertEqual(corrections[0]['after'], [allowed[0]])
            self.assertEqual(sorted(os.sched_getaffinity(child.pid)), [allowed[0]])
        finally:
            child.kill(); child.wait()
        # A thread that has ended is not a finding; a refused re-pin is.
        self.assertEqual(lanes.repin(self.protocol, 'lane1', [(child.pid, child.pid, allowed)]), ([], []))
        with patch.object(lanes.os, 'sched_setaffinity', side_effect=PermissionError('denied')):
            corrections, errors = lanes.repin(self.protocol, 'lane1', [(os.getpid(), os.getpid(), allowed)])
        self.assertTrue(errors and 'error' in corrections[0])

    def test_more_than_the_allowed_correction_episodes_is_a_finding(self):
        self.protocol['launch_policy'].update(sample_s=0.001, max_affinity_corrections=3)
        attempt = dict(unit='u', run=str(Path(tempfile.mkdtemp(dir=ART)) / 'run9'))
        self.addCleanup(lambda: __import__('shutil').rmtree(Path(attempt['run']).parent))
        def episodes(count):
            sampler = lanes.Sampler(self.protocol, 'lane1', attempt, Path(attempt['run']).parent)
            calls = iter([[(1, 2, [0, 9])]] * count + [[]] * 1000)
            with patch.object(lanes, 'processes', return_value=[]), patch.object(lanes, 'container_cpuset', return_value=None), \
                    patch.object(lanes, 'meminfo', return_value=dict(MemAvailable=GIB)), \
                    patch.object(lanes, 'escaped_threads', side_effect=lambda *a: next(calls)), \
                    patch.object(lanes, 'repin', return_value=([dict(pid=1, tid=2, after=[0])], [])):
                sampler.start()
                while sampler.episodes < count:
                    time.sleep(0.001)
                return sampler.stop()
        self.assertEqual(episodes(3)['errors'], [])
        self.assertEqual(episodes(4)['errors'], ['more than 3 affinity corrections in one attempt'])

    def test_lane_locks_are_never_created_and_wait_for_other_holders(self):
        with tempfile.TemporaryDirectory(dir=ART) as directory:
            paths = [Path(directory) / 'cpu-lane-1.lock', Path(directory) / 'cpu-lane-2.lock']
            self.protocol['lanes']['exclusive']['locks'] = [str(p) for p in paths]
            with self.assertRaisesRegex(RuntimeError, 'missing'):
                with lanes.lane_locks(self.protocol, 'exclusive', stop=lambda: False):
                    pass
            self.assertFalse(any(p.exists() for p in paths))
            for p in paths:
                p.touch()
            with lanes.lane_locks(self.protocol, 'exclusive', stop=lambda: False, poll_s=0):
                with paths[1].open('rb') as other:
                    with self.assertRaises(BlockingIOError):
                        fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with paths[1].open('rb') as holder:
                fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
                waits = []
                with self.assertRaises(InterruptedError):
                    with lanes.lane_locks(self.protocol, 'exclusive', stop=lambda: len(waits) > 2, poll_s=0,
                                          on_wait=waits.append):
                        pass

    def test_lane_commands_and_docker_limits(self):
        command = execution_policy.bounded_command(['bash', 'run.sh'], self.protocol, 'okvis2', 7, {}, lane='lane2')
        self.assertEqual(command[-5:], ['taskset', '--cpu-list', '4-7', 'bash', 'run.sh'])
        self.assertIn('MemoryMax=50G', command)
        env = execution_policy.lane_environment(self.protocol, 'openvins', 'lane1')
        self.assertEqual(env, dict(OPENVINS_MEMORY_LIMIT='50g', OPENVINS_MEMORY_SWAP_LIMIT='50g', OPENVINS_CPUSET='0-3'))
        self.assertTrue(execution_policy.bounded_command(['bash'], self.protocol, 'openvins', 1, env, lane='lane1'))
        with self.assertRaisesRegex(RuntimeError, 'CPU set differs'):
            execution_policy.bounded_command(['bash'], self.protocol, 'openvins', 1, env, lane='lane2')
        self.assertEqual(execution_policy.lane_environment(self.protocol, 'okvis2', 'lane1'), {})
        container = {'HostConfig': dict(Memory=50 * GIB, MemorySwap=50 * GIB, CpusetCpus='4-7', DeviceRequests=None)}
        execution_policy.verify_persistent_limits(self.protocol, 'voxel_svio', container, lane='lane2')
        for cpus in ('0-3', ''):
            bad = copy.deepcopy(container)
            bad['HostConfig']['CpusetCpus'] = cpus
            with self.subTest(cpus=cpus), self.assertRaisesRegex(RuntimeError, 'CPU set differs'):
                execution_policy.verify_persistent_limits(self.protocol, 'voxel_svio', bad, lane='lane2')

    def test_docker_limit_helper(self):
        def call(**env):
            script = (f'source {WORK}/scripts/run/_docker_limits.sh; docker_limit_args OPENVINS || exit $?; '
                      'printf "%s\\n" "${DOCKER_LIMIT_ARGS[@]}"')
            return subprocess.run(['bash', '-c', script], env=dict(PATH=os.environ['PATH'], **env),
                                  capture_output=True, text=True)
        self.assertEqual(call().stdout.strip(), '')
        result = call(OPENVINS_MEMORY_LIMIT='50g', OPENVINS_MEMORY_SWAP_LIMIT='50g', OPENVINS_CPUSET='0-3')
        self.assertEqual(result.stdout.split(), ['--memory', '50g', '--memory-swap', '50g', '--cpuset-cpus', '0-3'])
        self.assertEqual(call(OPENVINS_MEMORY_LIMIT='50g').returncode, 2)
        self.assertEqual(call(OPENVINS_CPUSET='0-3;rm').returncode, 2)


class Scheduling(unittest.TestCase):
    def setUp(self):
        records = {view: dict(first=0, count=1, times_sha256='0' * 64) for view in prepare.VIEWS}
        self.studies = prepare.protocol(records)['studies']
        self.by = {s['algorithm']: s for s in self.studies}

    def test_two_lanes_fixed_voxel_lane_and_basalt_alone_and_last(self):
        pending = list(self.studies)
        self.assertEqual(coordinator.lane_for(self.by['orbslam3'], {}, pending), 'lane1')
        active = {'lane1': (self.by['orbslam3'], None)}
        self.assertEqual(coordinator.lane_for(self.by['okvis2'], active, pending), 'lane2')
        active['lane2'] = (self.by['okvis2'], None)
        self.assertIsNone(coordinator.lane_for(self.by['openvins'], active, pending))
        del active['lane2']
        self.assertEqual(coordinator.lane_for(self.by['voxel_svio'], active, pending), 'lane2')
        del active['lane1']
        active['lane1'] = (self.by['openvins'], None)
        self.assertIsNone(coordinator.lane_for(self.by['voxel_svio'], {'lane2': (self.by['okvis2x'], None)}, pending))
        self.assertIsNone(coordinator.lane_for(self.by['basalt'], {}, pending))
        self.assertIsNone(coordinator.lane_for(self.by['basalt'], active, [self.by['basalt']]))
        self.assertEqual(coordinator.lane_for(self.by['basalt'], {}, [self.by['basalt']]), 'exclusive')
        self.assertIsNone(coordinator.lane_for(self.by['orbslam3'], {'exclusive': (self.by['basalt'], None)}, pending))

    def test_sentinel_differs_from_every_control(self):
        for spec in self.studies:
            self.assertEqual(policy.label_for(spec, coordinator.sentinel(spec))[:6], 'noise_')

    def test_handover_must_release_both_lanes_with_their_cores(self):
        with tempfile.TemporaryDirectory(dir=ART) as directory:
            path = Path(directory) / 'handover.json'
            protocol = prepare.protocol({v: dict(first=0, count=1, times_sha256='0' * 64) for v in prepare.VIEWS})
            with self.assertRaisesRegex(RuntimeError, 'No written lane handover'):
                coordinator.verify_handover(protocol)
            record = dict(lanes=dict(lane1=dict(cpus='0-3', handed_over=True), lane2=dict(cpus='4-7', handed_over=True)))
            path.write_text(json.dumps(record))
            protocol['lane_handover'] = dict(path=str(path), sha256=noise_pilot.sha(path))
            coordinator.verify_handover(protocol)
            record['lanes']['lane2']['cpus'] = '4-8'
            path.write_text(json.dumps(record))
            with self.assertRaisesRegex(RuntimeError, 'changed'):
                coordinator.verify_handover(protocol)
            protocol['lane_handover']['sha256'] = noise_pilot.sha(path)
            with self.assertRaisesRegex(RuntimeError, 'lane2'):
                coordinator.verify_handover(protocol)


class LaneSlot(unittest.TestCase):
    """The slot waits for the lane, samples the attempt, and stops the search on a finding."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sielinko-slot-', dir=ART)
        self.art = Path(self.temp.name)
        self.protocol = prepare.protocol({v: dict(first=0, count=1, times_sha256='0' * 64) for v in prepare.VIEWS})
        self.protocol['launch_policy'].update(poll_s=0, sample_s=0.01)
        import noise_campaign_engine as engine
        self.engine = engine
        patcher = patch.multiple(engine, ART=self.art, CURRENT=dict(key='k', run=str(self.art / 'run7'), unit='u-7'))
        patcher.start()
        self.addCleanup(patcher.stop)
        events = patch.object(noise_pilot, 'ART', self.art)
        events.start()
        self.addCleanup(events.stop)
        self.addCleanup(self.temp.cleanup)

    def slot(self):
        return coordinator.lane_slot(self.art, self.protocol, 'lane1', os.getppid())

    def test_waits_until_the_lane_is_free_then_samples(self):
        answers = [['busy'], ['busy'], []]
        with patch.object(lanes, 'launch_blockers', side_effect=lambda *a, **k: answers.pop(0)), \
                patch.object(lanes, 'sample_errors', return_value=[]):
            with self.slot():
                pass
        self.assertEqual(answers, [])
        events = [json.loads(x)['event'] for x in (self.art / 'events.jsonl').read_text().splitlines()]
        self.assertEqual(events, ['waiting_for_lane'])  # changes are recorded, not every poll
        self.assertTrue((self.art / 'lane-samples/run7.jsonl').read_text())

    def test_finding_stops_after_the_attempt_and_stop_file_before_it(self):
        with patch.object(lanes, 'launch_blockers', return_value=[]), \
                patch.object(lanes, 'sample_errors', return_value=['thread outside lane']):
            with self.assertRaisesRegex(RuntimeError, 'Lane check failed'):
                with self.slot():
                    time.sleep(0.05)
        external = self.art / 'rule-c-stop'
        external.touch()
        with patch.object(coordinator, 'EXTERNAL_STOPS', (external,)):
            with self.assertRaisesRegex(InterruptedError, 'External stop'):
                with self.slot():
                    self.fail('must not launch after a Rule C stop request')
        (self.art / 'STOP_AFTER_CURRENT').touch()
        with self.assertRaises(InterruptedError):
            with self.slot():
                self.fail('must not launch after a stop request')


class MainPins(unittest.TestCase):
    def test_main_head_is_enforced_unless_the_campaign_pins_only_its_inputs(self):
        with tempfile.TemporaryDirectory(dir=ART) as directory:
            art = Path(directory)
            pinned = 'datasets/zed2i/' + prepare.PARENT + '/times.txt'
            before = dict(main_head='0' * 40, sha256={pinned: noise_pilot.sha(noise_pilot.MAIN / pinned)})
            with patch.object(noise_pilot, 'ART', art):
                noise_pilot.write(art / 'main-before.json', before)
                with self.assertRaisesRegex(RuntimeError, 'main changed'):
                    noise_pilot.verify_main()
                noise_pilot.write(art / 'main-before.json', dict(before, enforce_main_head=False))
                noise_pilot.verify_main()
                self.assertFalse(json.loads((art / 'main-integrity.json').read_text())['main_head_enforced'])
                noise_pilot.write(art / 'main-before.json', dict(before, enforce_main_head=False,
                                                                 sha256={pinned: '0' * 64}))
                with self.assertRaisesRegex(RuntimeError, 'main changed'):
                    noise_pilot.verify_main()


if __name__ == '__main__':
    unittest.main(verbosity=2)
