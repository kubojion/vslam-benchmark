"""HortiMulti rerun decisions and the OpenVINS frame throttle (2026-10-05).

docs/hortimulti-decisions-20261005.md: one IMU noise profile for every HortiMulti estimator,
one camera-clock IMU input with every native camera-IMU offset at zero, OpenVINS
track_frequency above every camera interval, OV2SLAM's accurate-profile values, repaired
native builds. These tests fail if a configuration drifts back.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'scripts/campaign'))
from protocol_findings import user_rerun_decisions  # noqa: E402

NOISE = dict(gyro=0.0035, accel=0.110, gyro_walk=3.22094e-05, accel_walk=4.584471e-05)
SEQS = ('strawberry02', 'strawberry03')


def opencv_yaml(path):
    text = '\n'.join(l for l in path.read_text().splitlines() if not l.startswith('%YAML'))
    return yaml.safe_load(text.replace('!!opencv-matrix', ''))


def same(values):
    for key, value in values.items():
        assert value == pytest.approx(NOISE[key], rel=1e-9), key


def test_one_imu_profile_for_every_estimator():
    for name in ('hortimulti_stereo_inertial.yaml', 'hortimulti_stereo_inertial_lc.yaml'):
        text = (REPO / 'configs/orbslam3' / name).read_text()
        get = lambda key: float(re.search(rf'^IMU\.{key}:\s*(\S+)', text, re.M).group(1))
        same(dict(gyro=get('NoiseGyro'), accel=get('NoiseAcc'), gyro_walk=get('GyroWalk'), accel_walk=get('AccWalk')))
    for path, value in ((REPO / 'configs/airslam/hortimulti_camera.yaml', None),
                        (REPO / 'configs/openvins/hortimulti/kalibr_imu_chain.yaml', 'imu0'),
                        (REPO / 'configs/voxel_svio/hortimulti.yaml', 'imu_parameter')):
        d = opencv_yaml(path)
        d = d[value] if value else d
        same(dict(gyro=d['gyroscope_noise_density'], accel=d['accelerometer_noise_density'],
                  gyro_walk=d['gyroscope_random_walk'], accel_walk=d['accelerometer_random_walk']))
    basalt = json.loads((REPO / 'configs/basalt/hortimulti_calib.json').read_text())['value0']
    for key, field in (('gyro', 'gyro_noise_std'), ('accel', 'accel_noise_std'),
                       ('gyro_walk', 'gyro_bias_std'), ('accel_walk', 'accel_bias_std')):
        assert len(set(basalt[field])) == 1
        same({key: basalt[field][0]})
    for algo, modes in (('okvis2', ('vio', 'vio_lc')), ('okvis2x', ('vio', 'vio_lc'))):
        for seq in SEQS:
            for mode in modes:
                imu = opencv_yaml(REPO / f'configs/{algo}/hortimulti_{seq}_{mode}.yaml')['imu_parameters']
                same(dict(gyro=imu['sigma_g_c'], accel=imu['sigma_a_c'], gyro_walk=imu['sigma_gw_c'],
                          accel_walk=imu['sigma_aw_c']))
    profile = json.loads((REPO / 'configs/sensors/hortimulti.json').read_text())['imu']
    same(dict(gyro=profile['gyroscope_noise_density'], accel=profile['accelerometer_noise_density'],
              gyro_walk=profile['gyroscope_random_walk'], accel_walk=profile['accelerometer_random_walk']))


def test_every_native_camera_imu_offset_is_zero():
    for seq in SEQS:
        for algo, modes in (('okvis2', ('vio', 'vio_lc')), ('okvis2x', ('vio', 'vio_lc', 'gnss_vio'))):
            for mode in modes:
                assert opencv_yaml(REPO / f'configs/{algo}/hortimulti_{seq}_{mode}.yaml')['camera_parameters']['image_delay'] == 0.0
        assert opencv_yaml(REPO / f'configs/vins_fusion/hortimulti_{seq}.yaml')['td'] == 0.0
    assert json.loads((REPO / 'configs/basalt/hortimulti_calib.json').read_text())['value0']['cam_time_offset_ns'] == 0
    camera = yaml.safe_load((REPO / 'configs/voxel_svio/hortimulti.yaml').read_text())['camera_parameter']
    assert camera['timeshift_cam_imu_left'] == camera['timeshift_cam_imu_right'] == 0.0
    assert json.loads((REPO / 'configs/sensors/hortimulti.json').read_text())['camera_imu_time_offset_s'] == 0.0
    assert 'timeshift_cam_imu' not in (REPO / 'configs/openvins/hortimulti/kalibr_imucam_chain.yaml').read_text()
    for path in REPO.glob('configs/**/*'):
        if path.suffix in ('.yaml', '.yml', '.json', '.ini', '.txt') and ('hortimulti' in path.name or 'hortimulti' in path.parts):
            assert not re.search(r'(?<![\d.])0?\.00916|9160379(?!\d)', re.sub(r'#.*', '', path.read_text())), path


@pytest.mark.parametrize('seq', SEQS)
def test_imu_input_is_on_the_camera_clock(seq):
    folder = REPO / 'datasets/hortimulti' / seq
    if not (folder / 'mav0/imu0/data.csv').is_file():
        pytest.skip('dataset not present')
    import hashlib
    imu = json.loads((folder / 'manifest.json').read_text())['imu']
    assert imu['camera_clock_shift_s'] == pytest.approx(0.009160379, abs=1e-9)
    assert hashlib.sha256((folder / 'mav0/imu0/data.csv').read_bytes()).hexdigest() == imu['camera_clock_file']['sha256']
    original = folder / imu['original']['path']
    assert not str(imu['original']['path']).startswith('mav0/')
    first = lambda p: int(next(l for l in p.read_text().splitlines() if not l.startswith('#')).split(',', 1)[0])
    assert first(original) - first(folder / 'mav0/imu0/data.csv') == 9160379


def kept(stamps, frequency):
    last, n = None, 0
    for t in stamps:
        if last is None or t >= last + 1.0 / frequency:
            last, n = t, n + 1
    return n


@pytest.mark.parametrize('dataset,seqs', [('hortimulti', SEQS), ('zed2i', ('field1_110426_full_10fps_q90',)),
                                          ('citrusfarm', ('seq04', 'seq07'))])
def test_openvins_processes_every_frame(dataset, seqs):
    """OpenVINS' ROS front end drops a frame closer than 1/track_frequency to the last accepted one."""
    config = opencv_yaml(REPO / f'configs/openvins/{dataset}/estimator_config.yaml')
    assert config['track_frequency'] == 31.0
    for seq in seqs:
        path = REPO / 'datasets' / dataset / seq / 'mav0/cam0/data.csv'
        if not path.is_file():
            continue
        stamps = np.loadtxt(path, delimiter=',', comments='#', usecols=0, dtype=np.int64) * 1e-9
        assert kept(stamps, config['track_frequency']) == len(stamps), (dataset, seq)


def test_ov2slam_hortimulti_uses_the_profile_of_every_other_dataset():
    def values(path):
        d = opencv_yaml(path)
        return d['finit_parallax'], d['nmin_covscore']
    reference = values(REPO / 'configs/ov2slam/euroc_mav_vo.yaml')
    assert reference == (20.0, 25)
    for path in REPO.glob('configs/ov2slam/*_vo*.yaml'):
        assert values(path) == reference, path


def test_repaired_native_builds_include_hortimulti():
    voxel = (REPO / 'scripts/run/run_voxel_svio.sh').read_text()
    assert voxel.count('"$DATASET" == hortimulti') == 3
    openvins = (REPO / 'scripts/run/run_openvins.sh').read_text()
    line = next(l for l in openvins.splitlines() if 'OPENVINS_IMAGE=openvins:humble-shutdown-20261001' in l)
    assert '"$DATASET" == hortimulti' in line


def test_second_decision_file_adds_findings_without_changing_the_first(tmp_path):
    binaries = [dict(role='estimator', path='bin/x', sha256='0' * 64)]
    meta = dict(provenance=dict(binaries=binaries))
    decision = dict(code='c', disposition='required_rerun', prerequisite='p', evidence=['e'])
    folder = tmp_path / 'docs/campaigns'
    folder.mkdir(parents=True)
    (folder / 'user-rerun-decisions-20261003.json').write_text(json.dumps(dict(
        decisions=dict(a=decision), attempts={'vio/d/s/x/run1': dict(decision='a', binaries=binaries)})))
    (folder / 'user-rerun-decisions-20261005.json').write_text(json.dumps(dict(
        decisions=dict(b=dict(decision, code='d'), c=dict(decision, code='e')),
        attempts={'vio/d/s/x/run1': dict(decisions=['b', 'c'], binaries=binaries),
                  'vio/d/s/x/run2': dict(decisions=['b'], binaries=[])})))
    assert [f['code'] for f in user_rerun_decisions(tmp_path, 'vio/d/s/x/run1', meta)] == ['c', 'd', 'e']
    assert user_rerun_decisions(tmp_path, 'vio/d/s/x/run2', meta) == []      # other binaries
    assert user_rerun_decisions(tmp_path, 'vio/d/s/x/run3', meta) == []


def test_recorded_decisions_cover_the_decided_attempts():
    record = json.loads((REPO / 'docs/campaigns/user-rerun-decisions-20261005.json').read_text())
    counts = record['counts']
    assert (counts['horti_inertial_one_profile'], counts['ov2slam_horti_parameters'],
            counts['openvins_frame_throttle'], counts['orb_source_commit_single_group']) == (62, 12, 7, 4)
    for path, pinned in record['attempts'].items():
        mode, ds, seq, algo, run = path.split('/')
        # Container-based estimators save no host binaries; the record still pins the exact path.
        assert pinned['binaries'] is not None and set(pinned['decisions']) <= set(record['decisions'])
        assert ds in ('hortimulti', 'zed2i', 'citrusfarm') and not run.startswith('run9')
