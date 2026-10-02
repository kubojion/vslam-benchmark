"""Scientific invariants of prepared profiles; no estimator or dataset changes."""
import copy
import json
from pathlib import Path
import shutil
import sys

import cv2
import numpy as np
import pytest
import yaml
from scipy.spatial.transform import Rotation

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_rosario_vio_candidates import (BUNDLE, NOISE, digest, invert, prepare,
                                          read_yaml, select_candidate, verified_sources)
from configuration_recipe import config_recipe

SOURCE = BUNDLE / 'sources'
KALIBR = read_yaml(SOURCE / 'kalibr-cameras.yaml')
AUTHOR = read_yaml(SOURCE / 'author-openvins-cameras.yaml')


def intrinsic(cam):
    fx, fy, cx, cy = cam['intrinsics']
    return np.array([[fx, 0., cx], [0., fy, cy], [0., 0., 1.]])


def basalt_transforms():
    values = json.loads((BUNDLE / 'basalt-kalibr/calibration.json').read_text())['value0']
    result = []
    for pose in values['T_imu_cam']:
        t = np.eye(4)
        t[:3, :3] = Rotation.from_quat([pose[k] for k in ('qx', 'qy', 'qz', 'qw')]).as_matrix()
        t[:3, 3] = [pose[k] for k in ('px', 'py', 'pz')]
        result.append(t)
    return result


@pytest.mark.parametrize('profile', ['basalt-kalibr', 'voxel-kalibr', 'openvins-kalibr', 'openvins-author'])
def test_prepared_is_never_execution_ready(profile):
    for seq in ('sequence1', 'sequence5'):
        selected = select_candidate(profile, seq)
        assert selected['config_prepared'] and selected['inspection_only']
        assert not selected['verified_ready_to_run'] and not selected['activated_in_runners']
        assert len(selected['prerequisites']) >= 7


@pytest.mark.parametrize('kwargs', [{'sequence': 'sequence2'}, {'sequence': 'sequence1', 'mode': 'vo'},
                                  {'sequence': 'sequence1', 'dataset': 'zed2i'}])
def test_wrong_recording_or_mode_rejected(kwargs):
    with pytest.raises(ValueError):
        select_candidate('basalt-kalibr', **kwargs)


def test_reproducible_from_preserved_sources_and_tamper_rejected(tmp_path):
    bundle = tmp_path / 'bundle'
    shutil.copytree(BUNDLE, bundle)
    old = json.loads((bundle / 'index.json').read_text())
    assert prepare(bundle) == old
    with (bundle / 'sources/kalibr-cameras.yaml').open('a') as stream:
        stream.write('\n# changed source\n')
    with pytest.raises(ValueError, match='source hash mismatch'):
        prepare(bundle)


def test_candidate_edit_cannot_be_silently_selected(tmp_path):
    bundle = tmp_path / 'bundle'
    shutil.copytree(BUNDLE, bundle)
    with (bundle / 'basalt-kalibr/calibration.json').open('a') as stream:
        stream.write(' ')
    with pytest.raises(ValueError, match='candidate hash mismatch'):
        select_candidate('basalt-kalibr', 'sequence1', bundle=bundle)


@pytest.mark.parametrize('bad', [np.diag([2, 1, 1, 1]), np.diag([-1, 1, 1, 1]), np.zeros((4, 4))])
def test_nonrigid_transform_rejected(bad):
    with pytest.raises(ValueError):
        invert(bad)


@pytest.mark.parametrize('i', [0, 1])
def test_camera_to_imu_conversion_and_physical_lever_arm(i):
    c = KALIBR[f'cam{i}']
    expected = np.linalg.inv(c['T_cam_imu'])
    voxel = read_yaml(BUNDLE / 'voxel-kalibr/rosariov2.yaml')['camera_parameter']
    side = ('left', 'right')[i]
    actuals = [basalt_transforms()[i], np.reshape(voxel[f'T_imu_cam_{side}'], (4, 4))]
    for actual in actuals:
        np.testing.assert_allclose(actual, expected, rtol=0, atol=2e-15)
        # IMU coordinates of the camera centre are the translated optical origin.
        np.testing.assert_allclose(np.asarray(c['T_cam_imu']) @ actual @ [0, 0, 0, 1],
                                   [0, 0, 0, 1], rtol=0, atol=1e-15)
        assert .03 < np.linalg.norm(actual[:3, 3]) < .06  # metres, never mm or identity
        assert np.linalg.norm(actual[:3, :3] - np.eye(3)) > .005


@pytest.mark.parametrize('chain', [KALIBR, AUTHOR])
def test_each_published_bundle_has_same_closed_stereo_geometry(chain):
    relative = np.array(chain['cam1']['T_cam_imu']) @ np.linalg.inv(chain['cam0']['T_cam_imu'])
    np.testing.assert_allclose(relative, chain['cam1']['T_cn_cnm1'], atol=2e-15, rtol=0)
    assert np.linalg.norm(relative[:3, 3]) == pytest.approx(.05024089082502646, abs=1e-15)
    # The real stereo rotation is small but nonzero: do not replace it with a pure-x baseline.
    assert np.linalg.norm(relative[:3, :3] - np.eye(3)) > .001


@pytest.mark.parametrize('profile,source', [('openvins-kalibr', KALIBR), ('openvins-author', AUTHOR)])
def test_opencv_camera_parse_keeps_entire_source_profile(profile, source):
    path = BUNDLE / profile / 'kalibr_imucam_chain.yaml'
    actual = read_yaml(path)
    expected = copy.deepcopy(source)
    for i in (0, 1):
        expected[f'cam{i}']['rostopic'] = f'/cam{i}/image_raw'
    assert actual == expected
    fs = cv2.FileStorage(str(path), cv2.FILE_STORAGE_READ)
    assert fs.isOpened()
    for i in (0, 1):
        cam = fs.getNode(f'cam{i}')
        parsed = np.array([[cam.getNode('T_cam_imu').at(row).at(col).real()
                            for col in range(4)] for row in range(4)])
        np.testing.assert_array_equal(parsed, source[f'cam{i}']['T_cam_imu'])
        assert cam.getNode('intrinsics').size() == 4
        assert cam.getNode('distortion_coeffs').size() == 4
        assert cam.getNode('rostopic').string() == f'/cam{i}/image_raw'
    fs.release()


def test_author_openvins_numerical_policy_exact_only_relative_paths_change():
    saved = read_yaml(SOURCE / 'saved-openvins-estimator.yaml')
    author = read_yaml(SOURCE / 'author-openvins-estimator.yaml')
    candidate = read_yaml(BUNDLE / 'openvins-author/estimator_config.yaml')
    differences = {key for key in set(saved) | set(author) if saved.get(key) != author.get(key)}
    assert differences == {'calib_cam_extrinsics', 'calib_cam_intrinsics', 'init_dyn_use', 'init_imu_thresh',
                           'gravity_mag', 'num_pts', 'relative_config_imu', 'relative_config_imucam'}
    for key in author:
        if key not in ('relative_config_imu', 'relative_config_imucam'):
            assert candidate[key] == author[key]
    for key in ('calib_cam_extrinsics', 'calib_cam_intrinsics', 'calib_cam_timeoffset'):
        assert candidate[key] is True
    assert saved['calib_cam_timeoffset'] is True  # NOT a newly enabled setting
    assert read_yaml(BUNDLE / 'openvins-kalibr/estimator_config.yaml') == saved
    assert KALIBR['cam0']['T_cam_imu'] != AUTHOR['cam0']['T_cam_imu']


def test_noise_units_and_no_unrelated_voxel_policy_changes():
    imu = read_yaml(SOURCE / 'kalibr-imu.yaml')['imu0']
    b = json.loads((BUNDLE / 'basalt-kalibr/calibration.json').read_text())['value0']
    saved = read_yaml(SOURCE / 'saved-voxel.yaml')
    new = read_yaml(BUNDLE / 'voxel-kalibr/rosariov2.yaml')
    for key, source in zip(('accel_noise_std', 'accel_bias_std', 'gyro_noise_std', 'gyro_bias_std'), NOISE):
        assert b[key] == [imu[source]] * 3  # densities, no multiplication by sqrt(200 Hz)
        assert new['imu_parameter'][source] == imu[source]
    for key in saved:
        if key not in ('camera_parameter', 'imu_parameter'):
            assert saved[key] == new[key]
    for key in saved['imu_parameter']:
        if key not in NOISE:
            assert saved['imu_parameter'][key] == new['imu_parameter'][key]
    assert new['state_parameter']['calib_cam_timeoffset'] is False
    assert (BUNDLE / 'basalt-kalibr/vio_config.json').read_bytes() == (SOURCE / 'saved-basalt-estimator.json').read_bytes()


@pytest.mark.parametrize('profile', ['openvins-kalibr', 'openvins-author'])
def test_required_imu_matrices_and_linked_opencv_files(profile):
    folder = BUNDLE / profile
    settings = read_yaml(folder / 'estimator_config.yaml')
    for key in ('relative_config_imu', 'relative_config_imucam'):
        fs = cv2.FileStorage(str(folder / settings[key]), cv2.FILE_STORAGE_READ)
        assert fs.isOpened()
        fs.release()
    imu = read_yaml(folder / settings['relative_config_imu'])['imu0']
    for key in ('Tw', 'Ta', 'R_IMUtoGYRO', 'R_IMUtoACC'):
        np.testing.assert_array_equal(imu[key], np.eye(3))
    np.testing.assert_array_equal(imu['Tg'], np.zeros((3, 3)))
    assert imu['rostopic'] == '/imu0'
    fs = cv2.FileStorage(str(folder / 'estimator_config.yaml'), cv2.FILE_STORAGE_READ)
    assert fs.isOpened() and fs.getNode('max_cameras').real() == 2
    assert fs.getNode('relative_config_imu').string() == settings['relative_config_imu']
    fs.release()


def test_ros_parameter_scientific_notation_is_numeric_not_string():
    # rosparam loads YAML before passing typed values to nh.param<double>.
    data = yaml.safe_load((BUNDLE / 'voxel-kalibr/rosariov2.yaml').read_text())
    expected = {'initializer_parameter': {'init_dyn_min_rec_cond': 1e-12},
                'feature_parameter': {'init_lamda': 1e-3, 'max_lamda': 1e10, 'min_dx': 1e-6, 'min_dcost': 1e-6}}
    for group, values in expected.items():
        for name, value in values.items():
            assert isinstance(data[group][name], float) and data[group][name] == value


def test_opencv_author_estimator_numeric_values_survive_reserialization():
    old = cv2.FileStorage(str(SOURCE / 'author-openvins-estimator.yaml'), cv2.FILE_STORAGE_READ)
    new = cv2.FileStorage(str(BUNDLE / 'openvins-author/estimator_config.yaml'), cv2.FILE_STORAGE_READ)
    for key in old.root().keys():
        node = old.getNode(key)
        if node.isInt() or node.isReal():
            assert new.getNode(key).real() == node.real(), key
    assert new.getNode('init_dyn_min_rec_cond').real() == 1e-12
    old.release(); new.release()


def test_time_offset_units_sign_and_stereo_approximation_disclosed():
    b = json.loads((BUNDLE / 'basalt-kalibr/calibration.json').read_text())['value0']
    shift = KALIBR['cam0']['timeshift_cam_imu']
    assert b['cam_time_offset_ns'] == 4098308
    assert abs(b['cam_time_offset_ns'] * 1e-9 - shift) < .5e-9
    v = read_yaml(BUNDLE / 'voxel-kalibr/rosariov2.yaml')
    assert v['camera_parameter']['timeshift_cam_imu_left'] == shift
    assert v['state_parameter']['calib_cam_timeoffset'] is False
    # Native Voxel export adds the fixed offset; the runner removes exactly it.
    camera_time = 12.25
    assert (camera_time + shift) - v['camera_parameter']['timeshift_cam_imu_left'] == pytest.approx(camera_time)
    for profile in ('basalt-kalibr', 'voxel-kalibr', 'openvins-kalibr', 'openvins-author'):
        entry = select_candidate(profile, 'sequence1')
        assert entry['published_timeshifts_s'][0] > 0
        assert entry['common_stereo_time_uses_left']
        assert 8e-6 < entry['unused_right_minus_left_s'] < 13e-6


@pytest.mark.parametrize('i', [0, 1])
def test_radtan8_projection_equals_published_radtan4(i):
    b = json.loads((BUNDLE / 'basalt-kalibr/calibration.json').read_text())['value0']['intrinsics'][i]
    assert b['camera_type'] == 'pinhole-radtan8'
    params = b['intrinsics']; cam = KALIBR[f'cam{i}']
    points = np.array([[x, y, 1.] for x in np.linspace(-1., 1., 9) for y in np.linspace(-.6, .6, 9)])
    d8 = np.array([params[k] for k in ('k1', 'k2', 'p1', 'p2', 'k3', 'k4', 'k5', 'k6')])
    a, _ = cv2.projectPoints(points, np.zeros(3), np.zeros(3), intrinsic(cam), d8)
    b, _ = cv2.projectPoints(points, np.zeros(3), np.zeros(3), intrinsic(cam), np.array(cam['distortion_coeffs']))
    np.testing.assert_allclose(a, b, rtol=0, atol=1e-12)
    assert params['rpmax'] == -1.


def test_rectification_changes_optical_frame_not_imu_or_world():
    c0, c1 = KALIBR['cam0'], KALIBR['cam1']
    t10 = np.array(c1['T_cn_cnm1'])
    r0, r1, p0, p1, *_ = cv2.stereoRectify(intrinsic(c0), np.array(c0['distortion_coeffs']),
        intrinsic(c1), np.array(c1['distortion_coeffs']), (1280, 720), t10[:3, :3], t10[:3, 3], alpha=-1)
    # Synthetic points must land on matching epipolar rows and positive disparity.
    for point in (np.array([.1, .05, 2., 1.]), np.array([-.2, -.1, 4., 1.])):
        left, right = r0 @ point[:3], r1 @ (t10 @ point)[:3]
        uv0 = p0[:3, :3] @ left; uv0 /= uv0[2]
        uv1 = p1[:3, :3] @ right; uv1 /= uv1[2]
        assert uv0[1] == pytest.approx(uv1[1], abs=1e-8)
        assert uv0[0] > uv1[0]
        rect_to_raw = np.eye(4); rect_to_raw[:3, :3] = r0.T
        rect_to_imu = invert(c0['T_cam_imu']) @ rect_to_raw
        np.testing.assert_allclose(rect_to_imu @ [*left, 1.],
                                   invert(c0['T_cam_imu']) @ point, atol=2e-15, rtol=0)
    assert -p1[0, 3] / p1[0, 0] == pytest.approx(np.linalg.norm(t10[:3, 3]), abs=1e-15)


@pytest.mark.parametrize('algorithm', ['basalt', 'voxel_svio', 'openvins'])
def test_current_default_runner_selection_never_activates_candidates(algorithm):
    repo = BUNDLE.parents[2]
    for seq in ('sequence1', 'sequence5'):
        recipe = config_recipe(repo, dict(dataset='rosariov2', sequence=seq, algorithm=algorithm, run_type='vio'))
        assert not recipe['selection_errors']
        assert all('candidates/' not in item['path'] for item in recipe['source_files'])
        # Requested and materialized roles may refer to the same source file;
        # default selection must still use exactly the original file set.
        calibration = {item['path'] for item in recipe['source_files'] if item['path'].startswith('configs/')}
        assert len(calibration) == {'basalt': 2, 'voxel_svio': 1, 'openvins': 3}[algorithm]
        assert not recipe['runtime_materialization_verified']
