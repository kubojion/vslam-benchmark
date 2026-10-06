"""IMU noise rule "authors' operating point" (2026-10-05, docs/imu-noise-rule-20261005.md).

Every factor traces to the authors' released EuRoC file; EuRoC configurations already carry the
authors' values; every HortiMulti inertial configuration carries Allan x factor; the SVO Pro and
MASt3R-Fusion stages apply the rule only on its datasets.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'scripts/run'))
import _imu_noise_rule as rule_module  # noqa: E402

RULE = rule_module.load()
KEYS = RULE['keys']
SEQS = ('strawberry02', 'strawberry03')


def cv_yaml(path):
    text = '\n'.join(l for l in Path(path).read_text().splitlines() if not l.startswith('%YAML'))
    return yaml.safe_load(text.replace('!!opencv-matrix', ''))


def close(a, b, rel=1e-6):
    return abs(float(a) - float(b)) <= rel * abs(float(b))


def kalibr_style(path):
    d = cv_yaml(path)
    d = d.get('imu0', d)
    return {k: d[k] for k in KEYS}


def okvis(path):
    i = cv_yaml(path)['imu_parameters']
    return dict(gyroscope_noise_density=i['sigma_g_c'], accelerometer_noise_density=i['sigma_a_c'],
                gyroscope_random_walk=i['sigma_gw_c'], accelerometer_random_walk=i['sigma_aw_c'])


def orb(path):
    text = Path(path).read_text()
    get = lambda k: float(re.search(rf'^IMU\.{k}:\s*(\S+)', text, re.M).group(1))
    return dict(gyroscope_noise_density=get('NoiseGyro'), accelerometer_noise_density=get('NoiseAcc'),
                gyroscope_random_walk=get('GyroWalk'), accelerometer_random_walk=get('AccWalk'))


def basalt(path):
    v = json.loads(Path(path).read_text())['value0']
    assert all(len(set(v[f])) == 1 for f in ('gyro_noise_std', 'accel_noise_std', 'gyro_bias_std', 'accel_bias_std'))
    return dict(gyroscope_noise_density=v['gyro_noise_std'][0], accelerometer_noise_density=v['accel_noise_std'][0],
                gyroscope_random_walk=v['gyro_bias_std'][0], accelerometer_random_walk=v['accel_bias_std'][0])


AUTHOR_FILES = {
    'orbslam3': lambda: orb(REPO / 'src/ORB_SLAM3/Examples/Stereo-Inertial/EuRoC.yaml'),
    'openvins': lambda: kalibr_style(REPO / 'src/open_vins/config/euroc_mav/kalibr_imu_chain.yaml'),
    'voxel_svio': lambda: {k: v for k, v in cv_yaml(REPO / 'src/voxel_svio/config/euroc.yaml')['imu_parameter'].items() if k in KEYS},
    'airslam': lambda: kalibr_style(REPO / 'src/airslam/configs/camera/euroc.yaml'),
    'cuvslam': lambda: kalibr_style(REPO / 'src/cuvslam/examples/euroc/sensor_imu0.yaml'),
    'okvis2': lambda: okvis(REPO / 'src/okvis2/config/euroc.yaml'),
    'okvis2x': lambda: okvis(REPO / 'src/okvis2x/config/euroc/okvis2.yaml'),
    'basalt': lambda: basalt(REPO / 'results/reference-review-20261001/author-sources/basalt/data/euroc_ds_calib.json'),
    'svo_pro': lambda: (lambda p: dict(gyroscope_noise_density=p['sigma_omega_c'], accelerometer_noise_density=p['sigma_acc_c'],
                                        gyroscope_random_walk=p['sigma_omega_bias_c'], accelerometer_random_walk=p['sigma_acc_bias_c']))(
        yaml.safe_load((REPO / 'src/svo_pro/svo_ros/param/calib/euroc_stereo.yaml').read_text())['imu_params']),
    'mast3r_fusion': lambda: dict(zip(('accelerometer_noise_density', 'gyroscope_noise_density', 'accelerometer_random_walk',
                                       'gyroscope_random_walk'),
                                      yaml.safe_load((REPO / 'src/mast3r_fusion/config/base_euroc.yaml').read_text())['ms_opt']['imu_noise'])),
}


@pytest.mark.parametrize('algorithm', sorted(AUTHOR_FILES))
def test_rule_values_are_the_authors_released_euroc_values(algorithm):
    path_check = AUTHOR_FILES[algorithm]
    if algorithm == 'basalt' and not (REPO / 'results/reference-review-20261001/author-sources').exists():
        pytest.skip('Basalt author source copy not present')
    released = path_check()
    entry = RULE['authors_euroc'][algorithm]
    reference = RULE['euroc_reference']
    for k in KEYS:
        if entry.get('copies_reference'):
            assert close(released[k], reference[k], rel=0.005), (algorithm, k)   # ORB-SLAM3 rounds 1.6968e-4 to 1.7e-4
        else:
            assert close(released[k], entry[k]), (algorithm, k)


def test_euroc_configurations_already_carry_the_authors_values():
    reference = RULE['euroc_reference']
    for name, values in (('orbslam3', orb(REPO / 'configs/orbslam3/euroc_mav_stereo_inertial.yaml')),
                         ('openvins', kalibr_style(REPO / 'configs/openvins/euroc_mav/kalibr_imu_chain.yaml')),
                         ('airslam', kalibr_style(REPO / 'configs/airslam/euroc_mav_camera_vio.yaml')),
                         ('basalt', basalt(REPO / 'configs/basalt/euroc_mav_calib.json'))):
        expected = {k: reference[k] * f for k, f in rule_module.factors(name, RULE).items()}
        assert all(close(values[k], expected[k], rel=0.005) for k in KEYS), name
    for seq in ('MH_01_easy', 'MH_03_medium', 'MH_05_difficult'):
        for algo in ('okvis2', 'okvis2x'):
            assert okvis(REPO / f'configs/{algo}/euroc_mav_{seq}_vio.yaml') == AUTHOR_FILES[algo]()
        voxel = cv_yaml(REPO / f'configs/voxel_svio/euroc_mav_{seq}.yaml')['imu_parameter']
        assert all(close(voxel[k], reference[k]) for k in KEYS)


def test_hortimulti_configurations_follow_the_rule():
    expect = lambda algo: rule_module.noise(algo, 'hortimulti', RULE)
    def check(algo, values):
        e = expect(algo)
        assert all(close(values[k], e[k]) for k in KEYS), (algo, values, e)
    for name in ('hortimulti_stereo_inertial.yaml', 'hortimulti_stereo_inertial_lc.yaml'):
        check('orbslam3', orb(REPO / 'configs/orbslam3' / name))
    check('airslam', kalibr_style(REPO / 'configs/airslam/hortimulti_camera.yaml'))
    check('openvins', kalibr_style(REPO / 'configs/openvins/hortimulti/kalibr_imu_chain.yaml'))
    check('voxel_svio', {k: v for k, v in cv_yaml(REPO / 'configs/voxel_svio/hortimulti.yaml')['imu_parameter'].items() if k in KEYS})
    check('basalt', basalt(REPO / 'configs/basalt/hortimulti_calib.json'))
    for algo in ('okvis2', 'okvis2x'):
        for seq in SEQS:
            for mode in ('vio', 'vio_lc'):
                check(algo, okvis(REPO / f'configs/{algo}/hortimulti_{seq}_{mode}.yaml'))
    profile = json.loads((REPO / 'configs/sensors/hortimulti.json').read_text())['imu']
    check('cuvslam', {k: profile[k] for k in KEYS})


def load_stage(name):
    spec = importlib.util.spec_from_file_location(name, REPO / 'scripts/run' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('dataset', ['hortimulti', 'zed2i', 'citrusfarm', 'rosariov2'])
def test_svo_pro_stage_applies_the_rule_only_on_rule_datasets(dataset):
    stage = load_stage('_svo_pro_stage')
    sensor = json.loads((REPO / 'configs/sensors' / f'{dataset}.json').read_text())
    okvis_cfg = next((REPO / 'configs/okvis2').glob(f'{dataset}_*_vio.yaml'))
    args = type('A', (), dict(imu_params=f'okvis2:{okvis_cfg}'))
    params, source = stage.imu_parameters(args, sensor)
    got = dict(gyroscope_noise_density=params['sigma_omega_c'], accelerometer_noise_density=params['sigma_acc_c'],
               gyroscope_random_walk=params['sigma_omega_bias_c'], accelerometer_random_walk=params['sigma_acc_bias_c'])
    if dataset in RULE['datasets']:
        e = rule_module.noise('svo_pro', dataset, RULE)
        assert all(close(got[k], e[k]) for k in KEYS) and source['noise_rule']
    else:
        assert got == okvis(okvis_cfg) and not source.get('noise_rule')


@pytest.mark.parametrize('dataset', ['hortimulti', 'zed2i', 'euroc_mav', 'rosariov2', 'citrusfarm'])
def test_mast3r_fusion_stage_applies_the_rule_only_on_rule_datasets(tmp_path, dataset):
    stage = load_stage('_mast3r_fusion_stage')
    sensor = json.loads((REPO / 'configs/sensors' / f'{dataset}.json').read_text())
    (tmp_path / 'stage.json').write_text(json.dumps(dict(dataset=dataset, fps=sensor['image']['fps'], imu=sensor['imu'])))
    out = tmp_path / 'config.yaml'
    args = type('A', (), dict(stage=tmp_path, base=REPO / 'src/mast3r_fusion/config/base_euroc.yaml',
                              override=REPO / 'configs/mast3r_fusion/benchmark.yaml', out=out))
    stage.config(args)
    noise = yaml.safe_load(out.read_text())['ms_opt']['imu_noise']
    got = dict(zip(('accelerometer_noise_density', 'gyroscope_noise_density', 'accelerometer_random_walk', 'gyroscope_random_walk'), noise))
    if dataset in RULE['datasets']:
        e = rule_module.noise('mast3r_fusion', dataset, RULE)
        assert all(close(got[k], e[k]) for k in KEYS)
    elif dataset == 'euroc_mav':
        assert got == AUTHOR_FILES['mast3r_fusion']()
    else:
        assert all(close(got[k], sensor['imu'][k]) for k in KEYS)


def test_rule_applies_to_calibrated_field_datasets():
    assert RULE['datasets'] == ['hortimulti', 'rosariov2', 'citrusfarm']
    assert not rule_module.applies('euroc_mav') and not rule_module.applies('zed2i')
    assert set(RULE['authors_euroc']) == set(AUTHOR_FILES)
