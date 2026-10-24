"""Engine-on sensitivity for cuVSLAM, MASt3R-Fusion and AirSLAM (user, 2026-10-24).

Same method as the CPU profile: engine-on white densities, engine-off random walks, each
estimator's EuRoC ratio. Each wrapper takes the profile only through an explicit, validated
override; with the variable unset every run stays Rule C, byte for byte.
"""
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(REPO/'scripts/run'), str(REPO/'scripts/setup')]
import _imu_noise_override as override  # noqa: E402
import _imu_noise_rule as rule  # noqa: E402
import _mast3r_fusion_stage as mast3r  # noqa: E402
import prepare_noise_profile_20261021 as profile  # noqa: E402
import prepare_rule_c_20261021 as prepare  # noqa: E402

PROFILE = REPO/'configs/sensitivity/zed2i-engine-on-20261021'
GPU = ('cuvslam', 'mast3r_fusion', 'airslam')
VARIABLES = dict(cuvslam='CUVSLAM_IMU_NOISE', mast3r_fusion='MAST3R_FUSION_IMU_NOISE', airslam='AIRSLAM_CAMERA_CONFIG')


def entry(algorithm):
    return json.loads((PROFILE/'profile.json').read_text())['estimators'][algorithm]


def test_profile_adds_the_three_gpu_estimators_with_the_same_method():
    p = json.loads((PROFILE/'profile.json').read_text())
    assert list(p['estimators'])[-3:] == list(GPU)
    assert p['additions'][0]['estimators'] == list(GPU) and 'not part of the predictions' in p['additions'][0]['note']
    reference = profile.reference()
    for algorithm in GPU:
        e = entry(algorithm)
        (variable, target), = e['environment'].items()
        assert variable == VARIABLES[algorithm] and target.startswith('configs/sensitivity/zed2i-engine-on-20261021/')
        expected = profile.noise(algorithm)
        assert e['noise'] == expected
        # engine-on densities and engine-off walks, each times this estimator's EuRoC ratio
        for key in rule.load()['keys']:
            ratio = rule.noise(algorithm, 'zed2i')[key] / rule.load()['dataset_allan']['zed2i'][key]
            assert expected[key] == pytest.approx(reference[key] * ratio, rel=1e-12)


def test_cpu_estimators_are_unchanged():
    old = json.loads(subprocess.run(['git', 'show', 'ad1470c:configs/sensitivity/zed2i-engine-on-20261021/profile.json'],
                                    cwd=REPO, capture_output=True, text=True, check=True).stdout)
    new = json.loads((PROFILE/'profile.json').read_text())
    assert {k: v for k, v in new['estimators'].items() if k not in GPU} == old['estimators']
    assert {k: v for k, v in new.items() if k not in ('estimators', 'additions')} == {
        k: v for k, v in old.items() if k != 'estimators'}


def test_documents_are_bound_to_their_estimator():
    for algorithm in ('cuvslam', 'mast3r_fusion'):
        path = REPO/next(iter(entry(algorithm)['environment'].values()))
        values, receipt = override.load(path, algorithm, 'zed2i')
        assert values == entry(algorithm)['noise']
        with pytest.raises(ValueError, match='different algorithm'):
            override.load(path, 'svo_pro', 'zed2i')


def test_airslam_copy_differs_from_rule_c_only_in_noise():
    target = REPO/entry('airslam')['environment']['AIRSLAM_CAMERA_CONFIG']
    back = {profile.PROFILE_MARKER: '{marker}'}
    original = REPO/'configs/airslam/zed2i_camera_vio.yaml'
    assert prepare.with_noise(target, 'airslam', rule.noise('airslam', 'zed2i'), prepare.MARKER, prepare.BASALT_NOTE, back) \
        == original.read_text()
    assert entry('airslam')['copied_from_rule_c'] == {'configs/airslam/zed2i_camera_vio.yaml': profile.sha(original)}


def test_select_keeps_defaults_without_a_document():
    defaults = dict(gyroscope_noise_density=1.0, accelerometer_noise_density=2.0, gyroscope_random_walk=3.0,
                    accelerometer_random_walk=4.0, frequency_hz=100)
    values, receipt = override.select(defaults, None, 'cuvslam', 'zed2i')
    assert receipt is None and values == {k: defaults[k] for k in override.KEYS}


def stage_config(tmp_path, dataset='zed2i', keep=(), noise=None):
    stage = tmp_path/'stage'; stage.mkdir()
    imu = dict(gyroscope_noise_density=1e-3, accelerometer_noise_density=1e-2, gyroscope_random_walk=1e-5,
               accelerometer_random_walk=1e-4)
    (stage/'stage.json').write_text(json.dumps(dict(fps=10.0, dataset=dataset, imu=imu)))
    base = tmp_path/'base.yaml'
    base.write_text(yaml.safe_dump(dict(dataset=dict(subsample=1), ms_opt=dict(imu_noise=None), global_opt=dict(imu_noise=None))))
    over = tmp_path/'override.yaml'
    over.write_text(yaml.safe_dump(dict(keep_upstream_imu_noise=list(keep))))
    out = tmp_path/'out.yaml'
    args = type('Args', (), dict(stage=stage, base=base, override=over, out=out, noise_override=noise))
    mast3r.config(args)
    return yaml.safe_load(out.read_text())


def as_list(n):
    return [n['accelerometer_noise_density'], n['gyroscope_noise_density'],
            n['accelerometer_random_walk'], n['gyroscope_random_walk']]


def test_mast3r_stage_is_rule_c_without_the_override(tmp_path, capsys):
    cfg = stage_config(tmp_path)
    assert cfg['ms_opt']['imu_noise'] == cfg['global_opt']['imu_noise'] == as_list(rule.noise('mast3r_fusion', 'zed2i'))
    assert 'noise_override' not in json.loads(capsys.readouterr().out)


def test_mast3r_stage_applies_the_profile_document(tmp_path, capsys):
    document = REPO/entry('mast3r_fusion')['environment']['MAST3R_FUSION_IMU_NOISE']
    cfg = stage_config(tmp_path, noise=document)
    assert cfg['ms_opt']['imu_noise'] == cfg['global_opt']['imu_noise'] == as_list(entry('mast3r_fusion')['noise'])
    summary = json.loads(capsys.readouterr().out)
    assert summary['noise_override']['sha256'] == profile.sha(document)


def test_mast3r_override_refused_where_upstream_noise_is_kept(tmp_path):
    document = REPO/entry('mast3r_fusion')['environment']['MAST3R_FUSION_IMU_NOISE']
    with pytest.raises(ValueError):
        stage_config(tmp_path, keep=['zed2i'], noise=document)


def test_cuvslam_tracker_reads_the_override_only_for_inertial_runs():
    text = (REPO/'scripts/run/_cuvslam_track.py').read_text()
    assert "_imu_noise_override.select(spec, noise_override, 'cuvslam', sensor['dataset'])" in text
    assert "if args.noise_override and not use_imu:" in text
    assert "build_rig(sensor, use_imu, args.noise_override)" in text


@pytest.mark.parametrize('wrapper,variable', [('run_cuvslam.sh', 'CUVSLAM_IMU_NOISE'),
                                              ('run_mast3r_fusion.sh', 'MAST3R_FUSION_IMU_NOISE'),
                                              ('run_airslam.sh', 'AIRSLAM_CAMERA_CONFIG')])
def test_wrappers_validate_and_record_the_override(wrapper, variable):
    text = (REPO/'scripts/run'/wrapper).read_text()
    assert f'[[ -n "${{{variable}:-}}" ]]' in text
    assert f'{variable}=$(realpath -e "${variable}")' in text
    assert f'[[ "${variable}" == "$WS/configs/"* ]]' in text
    # validated before an attempt ID is consumed
    assert text.index(f'{variable}=$(realpath') < text.index('prepare_fresh_run_dir "$OUT_DIR"')
    assert variable in (REPO/'scripts/run/_enrich_run_meta.py').read_text()
    if wrapper != 'run_airslam.sh':
        assert f'(--artifact "imu_noise_override=${variable}")' in text


def test_airslam_default_camera_config_path_is_unchanged():
    text = (REPO/'scripts/run/run_airslam.sh').read_text()
    assert 'CAM_CFG_HOST="$WS/configs/${CAM_CFG#/benchmark_configs/}"' in text
    assert 'CAM_CFG="/benchmark_configs/${AIRSLAM_CAMERA_CONFIG#"$WS/configs/"}"' in text
    # Default: CAM_CFG=/benchmark_configs/airslam/<file> maps to the same host file as before.
    out = subprocess.run(['bash', '-c', 'WS=/w; CAM_CFG=/benchmark_configs/airslam/zed2i_camera_vio.yaml; '
                          'echo "$WS/configs/${CAM_CFG#/benchmark_configs/}"'], capture_output=True, text=True, check=True).stdout
    assert out.strip() == '/w/configs/airslam/zed2i_camera_vio.yaml'
