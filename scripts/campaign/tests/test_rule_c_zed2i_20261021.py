"""Sielinko (zed2i) Rule C and the engine-on sensitivity profile (user decisions 2026-10-21).

Rule C admits zed2i with its engine-off static Allan reference; every Sielinko inertial
config carries reference x the estimator's EuRoC ratio; earlier datasets' rule records are
unchanged; the engine-on profile differs from Rule C in the four noise values only and is
selected through opt-in environment variables that leave default runs untouched.
"""
import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(REPO/'scripts/run'), str(REPO/'scripts/setup')]
import _imu_noise_rule as rule  # noqa: E402
import _imu_noise_override as override  # noqa: E402
import build_zed2i_allan_source_20261021 as source_builder  # noqa: E402
import prepare_noise_profile_20261021 as profile  # noqa: E402
import prepare_rule_c_20261021 as prepare  # noqa: E402
from test_imu_noise_rule_20261005 import basalt, cv_yaml, kalibr_style, okvis, orb  # noqa: E402

SOURCE = REPO/'configs/sensors/sources/zed2i/allan-20261018.json'
EXTENSION = REPO/'configs/sensors/imu-noise-rule-20261021.json'
PROFILE = REPO/'configs/sensitivity/zed2i-engine-on-20261021'
def voxel(path):
    return {k: cv_yaml(path)['imu_parameter'][k] for k in rule.load()['keys']}


READ = {'orbslam3': orb, 'okvis2': okvis, 'okvis2x': okvis, 'basalt': basalt,
        'openvins': kalibr_style, 'voxel_svio': voxel, 'airslam': kalibr_style}


def close(a, b):
    return math.isclose(float(a), float(b), rel_tol=1e-12)


def test_source_record_reference_is_the_rule_input():
    s = json.loads(SOURCE.read_text())
    ext = json.loads(EXTENSION.read_text())['dataset_allan']['zed2i']
    assert {k: ext[k] for k in rule.load()['keys']} == s['engine_off_static']['reference']
    assert s['engine_off_static']['reference'] == dict(gyroscope_noise_density=1.5e-4, accelerometer_noise_density=1.1e-3,
                                                       gyroscope_random_walk=2.1e-6, accelerometer_random_walk=3.5e-5)
    on = s['engine_on_standstill']
    fits = on['fits'].values()
    assert on['unrounded']['gyroscope_noise_density'] == max(max(f['white_noise_axis_values'][:3]) for f in fits)
    assert on['unrounded']['accelerometer_noise_density'] == max(max(f['white_noise_axis_values'][3:]) for f in fits)
    assert on['selected'] == {k: source_builder.round_up(v) for k, v in on['unrounded'].items()}


def test_round_up_matches_engine_off_convention():
    assert [source_builder.round_up(v) for v in (1.4806e-4, 1.0476e-3, 2.0735e-6, 3.4978e-5, 3.1119e-3, 1.9710e-2)] \
        == [1.5e-4, 1.1e-3, 2.1e-6, 3.5e-5, 3.2e-3, 2.0e-2]


def test_rule_admits_zed2i_and_scales_by_euroc_ratios():
    r = rule.load()
    assert r['datasets'] == ['hortimulti', 'rosariov2', 'citrusfarm', 'zed2i']
    reference = json.loads(SOURCE.read_text())['engine_off_static']['reference']
    for algorithm in r['authors_euroc']:
        f, n = rule.factors(algorithm, r), rule.noise(algorithm, 'zed2i', r)
        assert all(close(n[k], reference[k] * f[k]) for k in r['keys'])


def test_earlier_dataset_records_exclude_the_new_extension():
    for dataset in ('rosariov2', 'citrusfarm'):
        paths = [f['path'] for f in rule.record(dataset=dataset)['files']]
        assert 'configs/sensors/imu-noise-rule-20261006.json' in paths
        assert not any('20261021' in p or 'zed2i' in p for p in paths)
    paths = [f['path'] for f in rule.record(dataset='zed2i')['files']]
    assert paths == ['configs/sensors/imu-noise-rule.json', 'configs/sensors/imu-noise-rule-20261021.json',
                     'configs/sensors/sources/zed2i/allan-20261018.json']
    assert rule.record(dataset='hortimulti')['path'].endswith('configs/sensors/imu-noise-rule.json')


def test_sielinko_inertial_configs_carry_rule_c_and_are_current():
    configs = prepare.inertial_configs()
    assert [p.name for p in configs['orbslam3']] == ['zed2i_field1_110426_full_10fps_q90_stereo_inertial.yaml']
    assert [p.name for p in configs['okvis2x']] == ['zed2i_field1_110426_full_10fps_q90_vio.yaml',
                                                    'zed2i_field1_110426_full_10fps_q90_vio_lc.yaml']
    for algorithm, paths in configs.items():
        n = rule.noise(algorithm, 'zed2i')
        for path in paths:
            assert prepare.with_noise(path, algorithm, n) == path.read_text(), f'{path} is stale; rerun the generator'
            values = READ[algorithm](path)
            assert all(close(values[k], n[k]) for k in rule.load()['keys']), path
    sensors = json.loads((REPO/'configs/sensors/zed2i.json').read_text())
    assert all(close(sensors['imu'][k], rule.noise('orbslam3', 'zed2i')[k]) for k in rule.load()['keys'])


def test_vo_configs_are_not_inertial_targets():
    names = {p.name for paths in prepare.inertial_configs().values() for p in paths}
    assert not any('_vo' in n and '_vio' not in n for n in names)


def test_profile_differs_from_rule_c_only_in_noise():
    p = json.loads((PROFILE/'profile.json').read_text())
    assert p['not_rule_c'] is True and p['counts_toward_rule_c_cells'] is False and p['modes'] == ['vio']
    assert p['reference'] == profile.reference()
    back = {profile.PROFILE_MARKER: '{marker}'}
    for algorithm, entry in p['estimators'].items():
        assert all(close(entry['noise'][k], profile.noise(algorithm)[k]) for k in rule.load()['keys'])
        for rel, digest in entry['files'].items():
            assert profile.sha(REPO/rel) == digest, rel
        (variable, target), = entry['environment'].items()
        assert (REPO/target).exists() and target.startswith('configs/sensitivity/')
        rule_c = rule.noise(algorithm, 'zed2i')
        if algorithm == 'svo_pro':
            values, receipt = override.load(REPO/target, 'svo_pro', 'zed2i')
            assert values == entry['noise'] and variable == 'SVO_PRO_IMU_NOISE'
            continue
        if algorithm == 'openvins':
            for f in (REPO/target).iterdir():
                original = REPO/'configs/openvins/zed2i'/f.name
                if f.name == 'kalibr_imu_chain.yaml':
                    assert prepare.with_noise(f, algorithm, rule_c, prepare.MARKER, prepare.BASALT_NOTE, back) \
                        == original.read_text()
                else:
                    assert f.read_bytes() == original.read_bytes()
            continue
        (original, _), = entry['copied_from_rule_c'].items()
        assert prepare.with_noise(REPO/target, algorithm, rule_c, prepare.MARKER, prepare.BASALT_NOTE, back) \
            == (REPO/original).read_text()


def test_profile_noise_is_engine_on_density_with_engine_off_walks():
    s = json.loads(SOURCE.read_text())
    ref = profile.reference()
    assert ref['gyroscope_noise_density'] == s['engine_on_standstill']['selected']['gyroscope_noise_density']
    assert ref['accelerometer_noise_density'] == s['engine_on_standstill']['selected']['accelerometer_noise_density']
    assert ref['gyroscope_random_walk'] == s['engine_off_static']['reference']['gyroscope_random_walk']
    assert ref['accelerometer_random_walk'] == s['engine_off_static']['reference']['accelerometer_random_walk']


def test_svo_pro_stage_applies_rule_then_override(tmp_path):
    import _svo_pro_stage as stage
    sensor = {'dataset': 'zed2i', 'imu': {'frequency_hz': 100.0}}
    imu = 'okvis2:' + str(REPO/'configs/okvis2/zed2i_field1_110426_full_10fps_q90_vio.yaml')
    names = ('sigma_omega_c', 'sigma_acc_c', 'sigma_omega_bias_c', 'sigma_acc_bias_c')
    params, receipt = stage.imu_parameters(argparse.Namespace(imu_params=imu), sensor)
    rule_c = rule.noise('svo_pro', 'zed2i')
    assert all(close(params[a], rule_c[k]) for a, k in zip(names, rule.load()['keys']))
    assert 'noise_override' not in receipt and receipt['noise_rule']['dataset'] == 'zed2i'
    doc = PROFILE/'svo_pro/imu-noise.json'
    params, receipt = stage.imu_parameters(argparse.Namespace(imu_params=imu, noise_override=doc), sensor)
    on = profile.noise('svo_pro')
    assert all(close(params[a], on[k]) for a, k in zip(names, rule.load()['keys']))
    assert receipt['noise_override']['sha256'] == profile.sha(doc)


def test_noise_document_is_bound_to_estimator_and_dataset():
    doc = PROFILE/'svo_pro/imu-noise.json'
    with pytest.raises(ValueError):
        override.load(doc, 'svo_pro', 'rosariov2')
    with pytest.raises(ValueError):
        override.load(doc, 'basalt', 'zed2i')
    with pytest.raises(ValueError):
        override.validate_parameters({k: -1.0 for k in override.KEYS})


@pytest.mark.parametrize('script', ['run_svo_pro.sh', 'run_voxel_svio.sh'])
def test_runner_overrides_parse_and_are_confined_to_configs(script):
    path = REPO/'scripts/run'/script
    subprocess.run(['bash', '-n', str(path)], check=True)
    text = path.read_text()
    variable = {'run_svo_pro.sh': 'SVO_PRO_IMU_NOISE', 'run_voxel_svio.sh': 'VOXEL_SVIO_CONFIG'}[script]
    assert f'== "$WS/configs/"*' in text and variable in text
    enrich = (REPO/'scripts/run/_enrich_run_meta.py').read_text()
    assert f'"{variable}"' in enrich
