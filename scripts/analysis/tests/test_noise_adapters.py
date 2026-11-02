"""Configuration-only checks; no estimators or active-worktree writes."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

ART = Path(__file__).resolve().parent
WORK = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(WORK / 'scripts/analysis'), str(WORK / 'scripts/run')]
import noise_adapters as adapters
import _imu_noise_override as override

PARAMS = dict(zip(override.KEYS, [.011, .123, .000023, .00034]))
SIELINKO = 'field1_110426_full_10fps_q90'
# Parent recordings whose configs the search derives candidates from.
PARENTS = {'zed2i': [SIELINKO], 'rosariov2': ['sequence1', 'sequence5'],
           'citrusfarm': ['seq04', 'seq07'], 'hortimulti': ['strawberry02', 'strawberry03']}
VIO_ONLY = ('basalt', 'openvins', 'voxel_svio')
DOCUMENTS = {'svo_pro': 'SVO_PRO_IMU_NOISE', 'cuvslam': 'CUVSLAM_IMU_NOISE', 'mast3r_fusion': 'MAST3R_FUSION_IMU_NOISE'}


def parsed(path):
    text = Path(path).read_text()
    if str(path).endswith('.json'):
        return json.loads(text)
    return yaml.safe_load('\n'.join(x for x in text.splitlines() if not x.startswith('%YAML'))
                          .replace('!!opencv-matrix', ''))


class AdapterChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='noise-adapter-', dir=ART)
        self.root = Path(self.temp.name)
        shutil.copytree(WORK / 'configs', self.root / 'configs',
                        ignore=shutil.ignore_patterns('generated'))

    def tearDown(self):
        self.temp.cleanup()

    def write_noise(self, algorithm, params=PARAMS, name='noise.json', dataset='zed2i'):
        target = self.root / name
        target.write_text(json.dumps(override.document(algorithm, dataset, params)))
        return target

    def test_every_candidate_preserves_non_noise_fields(self):
        count = 0
        for dataset, sequences in PARENTS.items():
            for algorithm in sorted(adapters.SUPPORTED):
                for sequence in sequences:
                    for mode in ['vio'] if algorithm in VIO_ONLY else ['vio', 'vio-lc']:
                        with self.subTest(algorithm=algorithm, dataset=dataset, sequence=sequence, mode=mode):
                            destination = self.root / 'configs/experiments/generated' / f'{algorithm}_{dataset}_{sequence}_{mode}'
                            receipt = adapters.prepare(self.root, algorithm, dataset, sequence, mode, PARAMS, destination)
                            self.assertEqual(receipt, adapters.prepare(self.root, algorithm, dataset, sequence, mode, PARAMS, destination))
                            if algorithm in DOCUMENTS:
                                actual, _ = override.load(receipt['environment'][DOCUMENTS[algorithm]], algorithm, dataset)
                                self.assertEqual(actual, PARAMS)
                                if algorithm == 'svo_pro':
                                    self.assertEqual(receipt['environment']['SVO_PRO_IMU_FILE'],
                                        str(self.root / f'configs/okvis2/{dataset}_{sequence}_vio.yaml'))
                                    self.assertTrue(Path(receipt['environment']['SVO_PRO_IMU_FILE']).is_file())
                            else:
                                for source, generated in zip(receipt['sources'], receipt['files']):
                                    original = parsed(self.root / source['path'])
                                    expected = copy.deepcopy(original)
                                    if algorithm == 'orbslam3':
                                        expected.update(dict(zip(adapters.ORB_KEYS, PARAMS.values())))
                                    elif algorithm in ('okvis2', 'okvis2x'):
                                        expected['imu_parameters'].update(dict(zip(adapters.OKVIS_KEYS, PARAMS.values())))
                                        if algorithm == 'okvis2' and receipt['mode_materialization']:
                                            expected['estimator_parameters']['do_loop_closures'] = True
                                    elif algorithm == 'basalt':
                                        expected['value0'].update({k: [v] * 3 for k, v in zip(adapters.BASALT_KEYS, PARAMS.values())})
                                    elif algorithm == 'openvins':
                                        if source['path'].endswith('/kalibr_imu_chain.yaml'):
                                            expected['imu0'].update(PARAMS)
                                        else:
                                            self.assertEqual((self.root / source['path']).read_bytes(), Path(generated['path']).read_bytes())
                                    else:
                                        target = expected
                                        if isinstance(expected.get('imu_parameter'), dict):
                                            target = expected['imu_parameter']
                                        target.update(PARAMS)
                                    self.assertEqual(parsed(generated['path']), expected)
                                    if algorithm != 'openvins' or source['path'].endswith('/kalibr_imu_chain.yaml'):
                                        self.assertEqual(adapters.read_effective(generated['path'], algorithm), PARAMS)
                            count += 1
        self.assertEqual(count, 17 + 6 * 17)

    def test_sielinko_candidates_use_main_sensitivity_hooks_and_parent_files(self):
        env = {}
        for algorithm in sorted(adapters.SUPPORTED):
            destination = self.root / 'configs/experiments/generated' / algorithm
            receipt = adapters.prepare(self.root, algorithm, 'zed2i', SIELINKO, 'vio', PARAMS, destination)
            env.update(receipt['environment'])
            self.assertTrue(all(Path(value).resolve().is_relative_to(self.root / 'configs')
                                for value in receipt['environment'].values()))
        self.assertEqual(set(env), {'ORBSLAM3_CONFIG', 'OKVIS2_CONFIG', 'OKVIS2X_CONFIG', 'BASALT_CALIBRATION',
                                    'OPENVINS_CONFIG_DIR', 'VOXEL_SVIO_CONFIG', 'SVO_PRO_IMU_NOISE', 'SVO_PRO_IMU_FILE',
                                    'CUVSLAM_IMU_NOISE', 'MAST3R_FUSION_IMU_NOISE', 'AIRSLAM_CAMERA_CONFIG'})
        # The 10 Hz recording's own ORB-SLAM3 file, not the dataset's generic one.
        orb = adapters.prepare(self.root, 'orbslam3', 'zed2i', SIELINKO, 'vio', PARAMS,
                               self.root / 'configs/experiments/generated/orb')
        self.assertEqual(orb['sources'][0]['path'], f'configs/orbslam3/zed2i_{SIELINKO}_stereo_inertial.yaml')
        lc = adapters.prepare(self.root, 'orbslam3', 'zed2i', SIELINKO, 'vio-lc', PARAMS,
                              self.root / 'configs/experiments/generated/orb-lc')
        self.assertEqual(lc['sources'][0]['path'], f'configs/orbslam3/zed2i_{SIELINKO}_stereo_inertial.yaml')

    def test_production_rule_c_values_round_trip(self):
        sys.path.insert(0, str(WORK / 'scripts/run'))
        import _imu_noise_rule
        files = {'orbslam3': f'configs/orbslam3/zed2i_{SIELINKO}_stereo_inertial.yaml',
                 'okvis2': f'configs/okvis2/zed2i_{SIELINKO}_vio.yaml',
                 'okvis2x': f'configs/okvis2x/zed2i_{SIELINKO}_vio.yaml',
                 'basalt': 'configs/basalt/zed2i_calib.json',
                 'openvins': 'configs/openvins/zed2i/kalibr_imu_chain.yaml',
                 'voxel_svio': 'configs/voxel_svio/zed2i.yaml'}
        for algorithm, path in files.items():
            with self.subTest(algorithm=algorithm):
                actual = adapters.read_effective(WORK / path, algorithm)
                rule = _imu_noise_rule.noise(algorithm, 'zed2i')
                for key in override.KEYS:
                    self.assertAlmostEqual(actual[key], rule[key], delta=1e-12 * rule[key])

    def test_unsupported_algorithms_and_modes_fail(self):
        for algorithm in ('dsol', 'macvo'):
            with self.subTest(algorithm=algorithm), self.assertRaises(ValueError):
                adapters.prepare(self.root, algorithm, 'zed2i', SIELINKO, 'vio', PARAMS,
                                 self.root / 'configs/experiments/generated/x')
        with self.assertRaises(ValueError):
            adapters.prepare(self.root, 'openvins', 'zed2i', SIELINKO, 'vio-lc', PARAMS,
                             self.root / 'configs/experiments/generated/x')
        with self.assertRaises(ValueError):
            adapters.prepare(self.root, 'orbslam3', 'zed2i', SIELINKO, 'vio', PARAMS, self.root / 'elsewhere')

    def test_invalid_or_mismatched_override_fails(self):
        path = self.write_noise('svo_pro')
        with self.assertRaises(ValueError):
            override.load(path, 'okvis2', 'zed2i')
        with self.assertRaises(ValueError):
            override.load(path, 'svo_pro', 'rosariov2')
        for bad in (0, -1, float('nan'), float('inf'), True, '0.1'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                override.validate_parameters(dict(PARAMS, gyroscope_noise_density=bad))
        path.write_text('{"schema":1,"schema":1}')
        with self.assertRaises(ValueError):
            override.load(path, 'svo_pro', 'zed2i')

    def test_shell_syntax(self):
        for path in (WORK / 'scripts/run').glob('*.sh'):
            subprocess.run(['bash', '-n', str(path)], check=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
