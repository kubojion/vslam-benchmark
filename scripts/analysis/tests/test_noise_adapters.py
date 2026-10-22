"""Configuration-only checks; no estimators or active-worktree writes."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

import yaml

ART = Path(__file__).resolve().parent
WORK = Path(__file__).resolve().parents[3]
MAIN = Path('/data/imoroz/vslam-benchmark')
DRAFT = WORK
sys.path[:0] = [str(DRAFT / 'scripts/analysis'), str(DRAFT / 'scripts/run'), str(WORK / 'scripts/run')]
import noise_adapters as adapters
import _experimental_imu_noise as override

PARAMS = dict(zip(override.KEYS, [.011, .123, .000023, .00034]))
PAIRS = {'rosariov2': ['sequence1', 'sequence5'], 'citrusfarm': ['seq04', 'seq07'],
         'hortimulti': ['strawberry02', 'strawberry03']}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


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

    def write_noise(self, algorithm, params=PARAMS, name='noise.json'):
        target = self.root / name
        target.write_text(json.dumps(override.document(algorithm, 'citrusfarm', params)))
        return target

    def test_all_102_native_candidates_preserve_non_noise_fields(self):
        count = 0
        for dataset, sequences in PAIRS.items():
            for algorithm in sorted(adapters.SUPPORTED):
                for sequence in sequences:
                    modes = ['vio'] if algorithm in ('basalt', 'openvins', 'voxel_svio') else ['vio', 'vio-lc']
                    for mode in modes:
                        with self.subTest(algorithm=algorithm, dataset=dataset, sequence=sequence, mode=mode):
                            destination = self.root / 'configs/experiments/generated' / f'{algorithm}_{dataset}_{sequence}_{mode}'
                            receipt = adapters.prepare(self.root, algorithm, dataset, sequence, mode, PARAMS, destination)
                            self.assertEqual(receipt, adapters.prepare(self.root, algorithm, dataset, sequence, mode, PARAMS, destination))
                            if algorithm in ('svo_pro', 'mast3r_fusion'):
                                actual, _ = override.load(destination / 'noise.json', algorithm, dataset)
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
                                        if algorithm == 'okvis2' and dataset == 'citrusfarm' and mode == 'vio-lc':
                                            expected['estimator_parameters']['do_loop_closures'] = True
                                    elif algorithm == 'basalt':
                                        expected['value0'].update({k: [v] * 3 for k, v in zip(adapters.BASALT_KEYS, PARAMS.values())})
                                    elif algorithm == 'cuvslam':
                                        expected['imu'].update(PARAMS)
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
        self.assertEqual(count, 102)

    def test_invalid_or_mismatched_override_fails(self):
        path = self.write_noise('svo_pro')
        with self.assertRaises(ValueError):
            override.load(path, 'mast3r_fusion', 'citrusfarm')
        with self.assertRaises(ValueError):
            override.load(path, 'svo_pro', 'rosariov2')
        for bad in (0, -1, float('nan'), float('inf'), True, '0.1'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                override.validate_parameters(dict(PARAMS, gyroscope_noise_density=bad))
        path.write_text('{"schema":1,"schema":1}')
        with self.assertRaises(ValueError):
            override.load(path, 'svo_pro', 'citrusfarm')

    def test_svo_stage_noise_override_and_cache_identity(self):
        new = module('draft_svo', DRAFT / 'scripts/run/_svo_pro_stage.py')
        old = module('original_svo', MAIN / 'scripts/run/_svo_pro_stage.py')
        sensor_file = WORK / 'configs/sensors/citrusfarm.json'
        sensor = json.loads(sensor_file.read_text())
        args = SimpleNamespace(imu_params='okvis2:' + str(WORK / 'configs/okvis2/citrusfarm_seq04_vio.yaml'))
        self.assertEqual(new.imu_parameters(args, sensor), old.imu_parameters(args, sensor))
        before, _ = old.imu_parameters(args, sensor)
        args.noise_override = self.write_noise('svo_pro')
        expected = dict(before, sigma_omega_c=.011, sigma_acc_c=.123,
                        sigma_omega_bias_c=.000023, sigma_acc_bias_c=.00034)
        actual, receipt = new.imu_parameters(args, sensor)
        self.assertEqual(actual, expected)
        self.assertEqual(receipt['experimental_noise']['parameters'], PARAMS)
        seq = self.root / 'sequence'
        for camera in ('cam0', 'cam1'):
            data = seq / 'mav0' / camera / 'data'
            data.mkdir(parents=True)
            rows = ['#timestamp,filename']
            for i in range(4):
                (data / f'{i}.png').write_bytes(b'no pixel processing in staging')
                rows.append(f'{1_000_000_000 + i * 100_000_000},{i}.png')
            (data.parent / 'data.csv').write_text('\n'.join(rows) + '\n')
        imu = seq / 'mav0/imu0'
        imu.mkdir()
        (imu / 'data.csv').write_text('#timestamp,wx,wy,wz,ax,ay,az\n' + ''.join(
            f'{800_000_000 + i * 5_000_000},0,0,0,0,0,9.8\n' for i in range(140)))
        args.sequence, args.sensor, args.out, args.max_frames = seq, sensor_file, self.root / 'stage', 0
        new.stage(args)
        staged = parsed(args.out / 'calib.yaml')
        self.assertEqual(staged['imu_params'], expected)
        new.stage(args)  # Exact reuse is safe.
        changed = dict(PARAMS, gyroscope_noise_density=.022)
        args.noise_override = self.write_noise('svo_pro', changed, 'different.json')
        with self.assertRaises(SystemExit):
            new.stage(args)  # Changed noise cannot reuse the old calibration.
        args.out = self.root / 'other-stage'
        new.stage(args)
        self.assertEqual(parsed(args.out / 'calib.yaml')['imu_params']['sigma_omega_c'], .022)

    def test_fusion_both_optimizers_and_default_preservation(self):
        new = module('draft_fusion', DRAFT / 'scripts/run/_mast3r_fusion_stage.py')
        old = module('original_fusion', MAIN / 'scripts/run/_mast3r_fusion_stage.py')
        sensor = parsed(WORK / 'configs/sensors/citrusfarm.json')
        stage = self.root / 'stage'
        stage.mkdir()
        (stage / 'stage.json').write_text(json.dumps(dict(dataset='citrusfarm', fps=10, imu=sensor['imu'])))
        args = SimpleNamespace(stage=stage, base=MAIN / 'src/mast3r_fusion/config/base_euroc.yaml',
                               override=WORK / 'configs/mast3r_fusion/benchmark.yaml', out=self.root / 'old.yaml')
        old.config(args)
        expected = parsed(args.out)
        args.out = self.root / 'new-default.yaml'
        new.config(args)
        self.assertEqual(parsed(args.out), expected)
        args.noise_override = self.write_noise('mast3r_fusion')
        args.out = self.root / 'experiment.yaml'
        new.config(args)
        for section in ('ms_opt', 'global_opt'):
            expected[section]['imu_noise'] = [.123, .011, .00034, .000023]
        self.assertEqual(parsed(args.out), expected)
        self.assertEqual(adapters.read_effective(args.out, 'mast3r_fusion'), PARAMS)
        self.assertEqual(parsed(args.out.with_suffix('.noise-override.json'))['parameters'], PARAMS)
        corrupted = parsed(args.out)
        corrupted['global_opt']['imu_noise'][0] *= 2
        args.out.write_text(yaml.safe_dump(corrupted))
        with self.assertRaises(ValueError):
            adapters.read_effective(args.out, 'mast3r_fusion')

    def test_shell_syntax(self):
        for path in (DRAFT / 'scripts/run').glob('*.sh'):
            subprocess.run(['bash', '-n', str(path)], check=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
