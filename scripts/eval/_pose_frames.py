"""Evidence-backed output-frame conversions for saved benchmark trajectories.

Target: the left optical camera (raw axes on EuRoC, input-image axes elsewhere).
Never read a current estimator config in place of a missing run-time snapshot.
Unknown conventions remain explicit blockers; they are not identity calibrations.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
import yaml
from scipy.spatial.transform import Rotation


class FrameEvidenceError(ValueError):
    pass


class OpenCVLoader(yaml.SafeLoader):
    pass


def _opencv_matrix(loader, node):
    value = loader.construct_mapping(node, deep=True)
    return np.asarray(value['data'], dtype=float).reshape(value['rows'], value['cols']).tolist()


OpenCVLoader.add_constructor('tag:yaml.org,2002:opencv-matrix', _opencv_matrix)


def read_yaml(path):
    text = Path(path).read_text()
    text = '\n'.join(line for line in text.splitlines() if not line.startswith('%YAML:'))
    return yaml.load(text, Loader=OpenCVLoader)


def file_evidence(path, root):
    path, root = Path(path), Path(root)
    try:
        name = str(path.relative_to(root))
    except ValueError:
        name = str(path)
    return {'path': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


class Snapshots:
    def __init__(self, run_dir, meta, ws):
        self.run_dir, self.ws = Path(run_dir), Path(ws)
        self.artifacts = meta.get('provenance', {}).get('artifacts', [])
        self.evidence = []
        self.export_stage = 'recorded_estimator_export'

    def read(self, role):
        items = [a for a in self.artifacts if a.get('role') == role and a.get('snapshot')]
        if len(items) != 1:
            raise FrameEvidenceError(f'expected one saved {role}, found {len(items)}')
        item = items[0]
        path = self.run_dir / item['snapshot']
        if not path.is_file():
            raise FrameEvidenceError(f'missing snapshot: {item["snapshot"]}')
        evidence = file_evidence(path, self.ws)
        expected = item.get('snapshot_sha256')
        if not expected or evidence['sha256'] != expected:
            raise FrameEvidenceError(f'unverified snapshot hash: {item["snapshot"]}')
        self.evidence.append(evidence)
        return json.loads(path.read_text()) if path.suffix == '.json' else read_yaml(path)


def matrix(value):
    if isinstance(value, dict):
        value = value['data']
    out = np.asarray(value, dtype=float).reshape(4, 4)
    if not np.isfinite(out).all() or not np.allclose(out[3], [0, 0, 0, 1]):
        raise FrameEvidenceError('invalid homogeneous calibration')
    if not np.allclose(out[:3, :3].T @ out[:3, :3], np.eye(3), atol=2e-5):
        raise FrameEvidenceError('calibration rotation is not orthonormal')
    if not np.isclose(np.linalg.det(out[:3, :3]), 1, atol=2e-5):
        raise FrameEvidenceError('calibration rotation contains a reflection')
    return out


def rotation_transform(r):
    t = np.eye(4)
    t[:3, :3] = r
    return t


def intrinsic(values):
    fx, fy, cx, cy = values
    return np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=float)


def rectified_to_raw(k0, d0, k1, d1, size, right_T_left, alpha=-1):
    """T_rectified_raw. OpenCV R1 maps raw coordinates into rectified axes."""
    r1 = cv2.stereoRectify(k0, np.asarray(d0, dtype=float), k1, np.asarray(d1, dtype=float),
                         tuple(size), right_T_left[:3, :3], right_T_left[:3, 3],
                         flags=cv2.CALIB_ZERO_DISPARITY, alpha=alpha)[0]
    return rotation_transform(r1)


def euroc_sensors(ws, seq):
    paths = [Path(ws) / 'datasets/euroc_mav' / seq / f'mav0/cam{i}/sensor.yaml' for i in (0, 1)]
    return [read_yaml(p) for p in paths], [file_evidence(p, ws) for p in paths]


def physical_euroc_imu_to_camera(ws, seq, snapshots):
    sensors, evidence = euroc_sensors(ws, seq)
    snapshots.evidence.extend(evidence)
    return matrix(sensors[0]['T_BS'])


def physical_rosario_imu_to_camera(ws, seq, snapshots):
    """Physical calibration for the unchanged image_rect_raw input axes.

    This is independent of an estimator's assumed/optimized extrinsic. Matching
    a physical output frame does not validate those estimator-side assumptions.
    """
    path = Path(ws) / 'docs/campaigns/rosario-reference-calibration-20261001.json'
    value = json.loads(path.read_text())
    if seq not in value['sequences'] or value['dataset'] != 'rosariov2':
        raise FrameEvidenceError('unreviewed Rosario reference recording')
    snapshots.evidence.append(file_evidence(path, ws))
    return matrix(value['T_imu_left'])


# Datasets whose inertial outputs are compared through an independent, reviewed physical
# IMU-to-left-camera calibration rather than the estimator's own saved extrinsic.
PHYSICAL_IMU_DATASETS = ('euroc_mav', 'rosariov2', 'zed2i', 'citrusfarm')


def physical_imu_to_camera(ws, dataset, seq, snapshots):
    if dataset == 'euroc_mav':
        return physical_euroc_imu_to_camera(ws, seq, snapshots)
    if dataset == 'rosariov2':
        return physical_rosario_imu_to_camera(ws, seq, snapshots)
    if dataset == 'zed2i':
        path=Path(ws)/'docs/campaigns/zed-physical-calibration-20261002.json'
        value=json.loads(path.read_text())
        if seq not in value['sequences'] or value['serial_number']!=30291010:
            raise FrameEvidenceError('unreviewed ZED camera serial or recording')
        snapshots.evidence.append(file_evidence(path,ws))
        for item in value['evidence']:
            actual=file_evidence(Path(ws)/item['path'],ws)
            if actual['sha256']!=item['sha256']:raise FrameEvidenceError('ZED calibration source changed')
            snapshots.evidence.append(actual)
        return matrix(value['T_imu_left'])
    if dataset == 'citrusfarm':
        # The authors' Kalibr chain, checked against the ZED IMU's gyro on both sequences.
        path=Path(ws)/'docs/campaigns/citrusfarm-physical-calibration-20261003.json'
        value=json.loads(path.read_text())
        if seq not in value['sequences']:
            raise FrameEvidenceError('unreviewed CitrusFarm recording')
        snapshots.evidence.append(file_evidence(path,ws))
        for item in value['evidence']:
            actual=file_evidence(Path(ws)/item['path'],ws)
            if actual['sha256']!=item['sha256']:raise FrameEvidenceError('CitrusFarm calibration source changed')
            snapshots.evidence.append(actual)
        return matrix(value['T_imu_left'])
    raise FrameEvidenceError('independent physical IMU calibration not established')


def okvis_final_extrinsic(snapshots):
    """Recover final static T_SC0, validating map and selected pose export.

    A variable extrinsic per frame is deliberately not replaced by an average.
    The map stores full-precision values (Component::save), unlike config guesses.
    """
    paths = list(snapshots.run_dir.glob('okvis2-*-final_map.g2o'))
    if len(paths) != 1:
        raise FrameEvidenceError('final extrinsics require one saved final_map.g2o')
    path = paths[0]
    csv_path = path.with_name(path.name.replace('final_map.g2o', 'final-ba_trajectory.csv'))
    if not csv_path.is_file():
        raise FrameEvidenceError('no final-ba trajectory to verify final-map correspondence')
    # Validate the selected export against every saved CSV pose, including its
    # timestamps and rotations. The runners round TUM output to six decimals.
    selected = np.loadtxt(snapshots.run_dir / 'trajectory.txt', ndmin=2)
    original = np.loadtxt(csv_path, delimiter=',', skiprows=1, usecols=range(8), ndmin=2)
    original[:, 0] /= 1e9
    if selected.shape != original.shape or not np.allclose(selected, original, atol=1.1e-6, rtol=0):
        raise FrameEvidenceError('selected trajectory does not match saved final-ba CSV')
    matrices = []
    with path.open() as stream:
        for line in stream:
            if not line.startswith('FRAME '):
                continue
            fields = line.split()
            if fields[2] != '0':
                continue
            t = rotation_transform(Rotation.from_quat([float(x) for x in fields[7:11]]).as_matrix())
            t[:3, 3] = [float(x) for x in fields[4:7]]
            matrices.append(t)
    if not matrices or not np.allclose(matrices, matrices[0], atol=1e-9, rtol=0):
        raise FrameEvidenceError('missing or time-varying final camera extrinsics')
    snapshots.evidence.extend(file_evidence(p, snapshots.ws) for p in (path, csv_path))
    return matrix(matrices[0])


def verified_okvis_causal_recovery(snapshots, cfg):
    """Accept only an exact, hash-pinned causal CSV conversion, never final BA.

    Without per-pose extrinsics, online extrinsic calibration is unsupported.
    Configured final BA does not change poses exported before that stage ran.
    """
    receipt = snapshots.run_dir / 'trajectory_recovery.json'
    if not receipt.is_file():
        return False
    value = json.loads(receipt.read_text())
    if (value.get('schema') != 1 or value.get('stage') != 'recovered_causal_prefix'
            or value.get('native_csv') != 'okvis2-slam_trajectory.csv'):
        raise FrameEvidenceError('unsupported OKVIS recovery receipt')
    if cfg.get('camera_parameters', {}).get('online_calibration', {}).get('do_extrinsics', True):
        raise FrameEvidenceError('causal recovery with online extrinsic calibration is unsupported')
    expected = {value['native_csv'], 'trajectory.txt', 'run_meta.json'}
    evidence = value.get('evidence', [])
    if {e.get('path') for e in evidence} != expected or len(evidence) != len(expected):
        raise FrameEvidenceError('incomplete causal recovery evidence')
    for item in evidence:
        actual = file_evidence(snapshots.run_dir / item['path'], snapshots.ws)
        if actual['sha256'] != item.get('sha256'):
            raise FrameEvidenceError('causal recovery evidence hash mismatch')
        snapshots.evidence.append(actual)
    selected = np.loadtxt(snapshots.run_dir / 'trajectory.txt', ndmin=2)
    original = np.loadtxt(snapshots.run_dir / value['native_csv'], delimiter=',',
                          skiprows=1, usecols=range(8), ndmin=2)
    original[:, 0] /= 1e9
    if (selected.shape != original.shape or len(selected) != value.get('poses')
            or not np.isfinite(original).all()
            or not np.allclose(selected, original, atol=5e-7, rtol=0)):
        raise FrameEvidenceError('causal recovery does not match every native pose')
    snapshots.evidence.append(file_evidence(receipt, snapshots.ws))
    snapshots.export_stage = 'recovered_causal_prefix'
    return True


def estimate_transform(ws, dataset, seq, algo, use_imu, snapshots):
    """Return output-frame name, T_output_left and source locations reviewed."""
    if algo in ('okvis2', 'okvis2x'):
        cfg = snapshots.read('estimator_config')
        online = cfg.get('camera_parameters', {}).get('online_calibration', {})
        final_ba = cfg.get('estimator_parameters', {}).get('do_final_ba', False)
        source = [f'src/{algo}/okvis_multisensor_processing/src/TrajectoryOutput.cpp']
        recovered = verified_okvis_causal_recovery(snapshots, cfg)
        if use_imu and dataset in PHYSICAL_IMU_DATASETS:
            return 'physical_imu_sensor', physical_imu_to_camera(ws, dataset, seq, snapshots), source
        if recovered:
            return 'sensor_with_saved_initial_calibration_causal_prefix', matrix(cfg['cameras'][0]['T_SC']), source
        if online.get('do_extrinsics') or (final_ba and online.get('do_extrinsics_final_ba')):
            return 'sensor_with_saved_final_calibration', okvis_final_extrinsic(snapshots), source + [f'src/{algo}/okvis_ceres/src/Component.cpp']
        return 'imu_sensor', matrix(cfg['cameras'][0]['T_SC']), source
    if algo == 'basalt':
        cfg = snapshots.read('camera_calibration')['value0']['T_imu_cam'][0]
        t = rotation_transform(Rotation.from_quat([cfg[k] for k in ('qx', 'qy', 'qz', 'qw')]).as_matrix())
        t[:3, 3] = [cfg[k] for k in ('px', 'py', 'pz')]
        if use_imu and dataset in PHYSICAL_IMU_DATASETS:
            t = physical_imu_to_camera(ws, dataset, seq, snapshots)
        return 'imu_or_virtual_body', matrix(t), ['https://github.com/VladyslavUsenko/basalt/blob/0f3b2b52c807f70ff4e2973ce253c73329eea7bc/src/vio.cpp']
    if algo == 'openvins':
        cfg = snapshots.read('estimator_config')
        if cfg.get('calib_cam_extrinsics', False) and dataset != 'euroc_mav':
            raise FrameEvidenceError('online camera extrinsics require saved calibration per pose')
        cam = snapshots.read('camera_imu_calibration')['cam0']
        t = matrix(cam['T_imu_cam']) if 'T_imu_cam' in cam else np.linalg.inv(matrix(cam['T_cam_imu']))
        if dataset in PHYSICAL_IMU_DATASETS:
            t = physical_imu_to_camera(ws, dataset, seq, snapshots)
        return 'imu', t, ['src/open_vins/ov_msckf/src/ros/ROS2Visualizer.cpp', 'src/open_vins/ov_core/src/utils/quat_ops.h']
    if algo == 'voxel_svio':
        cfg = snapshots.read('estimator_config')
        if cfg.get('state_parameter', {}).get('calib_cam_extrinsics', False):
            raise FrameEvidenceError('online camera extrinsics require saved calibration per pose')
        t = physical_imu_to_camera(ws, dataset, seq, snapshots) if dataset in PHYSICAL_IMU_DATASETS else matrix(cfg['camera_parameter']['T_imu_cam_left'])
        return 'imu', t, ['src/voxel_svio/src/stereoVio.cpp', 'src/voxel_svio/src/quatOps.cpp']
    if algo == 'orbslam3':
        cfg = snapshots.read('estimator_config')
        source = ['src/ORB_SLAM3/src/System.cc', 'src/ORB_SLAM3/src/Settings.cc']
        if use_imu:
            t = physical_imu_to_camera(ws, dataset, seq, snapshots) if dataset in PHYSICAL_IMU_DATASETS else matrix(cfg['IMU.T_b_c1'])
            return 'imu_body', t, source
        if cfg['Camera.type'] == 'Rectified':
            return 'left_camera_input_axes', np.eye(4), source
        if cfg['Camera.type'] != 'PinHole' or dataset != 'euroc_mav':
            raise FrameEvidenceError('unreviewed ORB camera model or rectification')
        ks, ds = [], []
        for c in ('Camera1', 'Camera2'):
            ks.append(intrinsic([cfg[f'{c}.{k}'] for k in ('fx', 'fy', 'cx', 'cy')]))
            ds.append([cfg.get(f'{c}.{k}', 0) for k in ('k1', 'k2', 'p1', 'p2', 'k3')])
        t = rectified_to_raw(ks[0], ds[0], ks[1], ds[1], [cfg['Camera.width'], cfg['Camera.height']],
                             np.linalg.inv(matrix(cfg['Stereo.T_c1_c2'])))
        return 'left_camera_internally_rectified', t, source
    if algo == 'airslam':
        cfg = snapshots.read('camera_config')
        source = ['src/airslam/src/map.cc', 'src/airslam/src/camera.cc', 'src/airslam/src/frame.cc']
        if cfg['distortion_type'] == 0:
            return 'left_camera_input_axes_keyframes', np.eye(4), source
        if cfg['distortion_type'] != 1 or dataset != 'euroc_mav':
            raise FrameEvidenceError('unreviewed AirSLAM rectification')
        cameras = [cfg[f'cam{i}'] for i in (0, 1)]
        ts = [matrix(c['T']) if c['T_type'] == 0 else np.linalg.inv(matrix(c['T'])) for c in cameras]
        t = rectified_to_raw(intrinsic(cameras[0]['intrinsics']), cameras[0]['distortion_coeffs'],
                             intrinsic(cameras[1]['intrinsics']), cameras[1]['distortion_coeffs'],
                             [cfg['image_width'], cfg['image_height']], np.linalg.inv(ts[1]) @ ts[0], alpha=0)
        return 'left_camera_internally_rectified_keyframes', t, source
    if algo == 'ov2slam':
        cfg = snapshots.read('estimator_config')
        if cfg.get('bdo_stereo_rect', 0):
            raise FrameEvidenceError('unreviewed OV2SLAM internal rectification')
        return 'left_camera_input_axes', np.eye(4), ['src/ov2slam/include/logger.hpp']
    if algo == 'dpvo':
        # DPVO undistorts radtan images but does not rotate optical axes.
        snapshots.read('camera_calibration')
        return 'left_camera_input_axes_monocular', np.eye(4), ['src/DPVO/demo.py']
    if algo == 'macvo':
        source = ['src/MAC-VO/Odometry/Interface.py', 'src/MAC-VO/DataLoader/Dataset/EuRoC.py',
                  'src/MAC-VO/DataLoader/Dataset/GeneralStereo.py']
        cfg = snapshots.read('effective_dataset_config')
        expected = 'EuRoC_NoIMU' if dataset == 'euroc_mav' else 'GeneralStereo'
        if cfg.get('type') != expected or cfg.get('args', {}).get('gt_pose', False):
            raise FrameEvidenceError('unreviewed MAC-VO loader or ground-truth input enabled')
        if dataset != 'euroc_mav':
            # Internal NED camera axes -> optical EDN coordinates.
            return 'camera_ned_axes', rotation_transform(np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])), source
        sensors, evidence = euroc_sensors(ws, seq)
        snapshots.evidence.extend(evidence)
        ts = [matrix(c['T_BS']) for c in sensors]
        r = rectified_to_raw(intrinsic(sensors[0]['intrinsics']), sensors[0]['distortion_coefficients'],
                             intrinsic(sensors[1]['intrinsics']), sensors[1]['distortion_coefficients'],
                             sensors[0]['resolution'], np.linalg.inv(ts[1]) @ ts[0])
        # Saved P = (B_C NED2EDN) P_NED (B_C NED2EDN)^-1.
        # P B_C Rrect is a raw-optical camera pose, up to a constant world gauge.
        return 'conjugated_camera_pose', ts[0] @ r, source
    if algo == 'cuvslam':
        # The rig is placed at cam0 (rig_from_camera = identity); exported poses are
        # world_from_rig, i.e. the left camera in its input axes. Raw EuRoC images are
        # handled with cuVSLAM's own distortion model, which does not rotate the axes.
        cfg = snapshots.read('effective_config')
        if cfg.get('rig_origin') != 'cam0':
            raise FrameEvidenceError('cuVSLAM rig origin is not the left camera')
        return 'left_camera_input_axes', np.eye(4), ['scripts/run/_cuvslam_track.py',
                                                     'src/cuvslam/python/cuvslam/pycuvslam.pyi']
    if algo == 'dsol':
        # DSOL estimates the rectified left camera; the export multiplies the saved
        # rectification rotation back in, so trajectory.txt holds the input left camera.
        stage = snapshots.read('stage_record')
        expected = 'rectified_here_stereoRectify_alpha0_bilinear' if dataset == 'euroc_mav' else 'symlink_original_images'
        if stage.get('mode') != expected:
            raise FrameEvidenceError('unreviewed DSOL image preparation')
        return 'left_camera_input_axes_after_inverse_rectification', np.eye(4), [
            'scripts/run/_dsol_stage.py', 'src/dsol/sv/dsol/node_data.cpp']
    if algo == 'svo_pro':
        # svo_benchmark writes T_W_B; B is the body frame of the saved calib.yaml
        # (T_B_C per camera). As for the other IMU-output rows, inertial runs use the
        # independent physical calibration where one is established.
        calib = snapshots.read('camera_imu_calibration')
        t = matrix(np.asarray(calib['cameras'][0]['T_B_C']['data'], dtype=float).reshape(4, 4))
        source = ['src/svo_pro/svo_ros/src/benchmark_node.cpp', 'scripts/run/_svo_pro_stage.py']
        if use_imu and dataset in PHYSICAL_IMU_DATASETS:
            return 'imu_body', physical_imu_to_camera(ws, dataset, seq, snapshots), source
        return 'imu_body_from_saved_calibration', t, source
    if algo == 'mast3r_fusion':
        # Real-time states.T_WC and globally optimised wTc are camera poses; raw EuRoC
        # images are undistorted without changing the optical axes (monocular, cam0).
        snapshots.read('effective_config')
        return 'left_camera_input_axes', np.eye(4), ['src/mast3r_fusion/main.py',
                                                     'src/mast3r_fusion/main_global_optimization.py']
    raise FrameEvidenceError(f'output frame not established for {algo}')


def frame_policy(ws, run_dir, meta, dataset, seq, algo, use_imu):
    snapshots = Snapshots(run_dir, meta, ws)
    policy = dict(target_frame='left_camera_raw_optical' if dataset == 'euroc_mav' else 'left_camera_input_axes',
                  estimate_frame=None, reference_frame=None, estimate_transform=None,
                  reference_transform=None, orientation_valid=False, common_origin_verified=False,
                  blockers=[], evidence=[], source_locations=[])
    try:
        name, transform, sources = estimate_transform(ws, dataset, seq, algo, use_imu, snapshots)
        if dataset == 'rosariov2' and any(a.get('role') == 'rosario_input_profile' for a in snapshots.artifacts):
            profile = snapshots.read('rosario_input_profile')
            if profile.get('profile') != 'rosario-kalibr-rectified-ruleC-20261006':
                raise FrameEvidenceError('unreviewed Rosario prepared profile')
            # Inertial body exports were already converted through the immutable
            # physical reference calibration. Camera/virtual-body exports are
            # currently in the NEW image axes and require T_rect_original = R0.
            physical_body = use_imu and algo in ('orbslam3', 'okvis2', 'okvis2x', 'basalt', 'openvins', 'voxel_svio', 'svo_pro')
            if not physical_body:
                transform = transform @ rotation_transform(np.asarray(profile['geometry']['R'][0]))
            policy['input_profile'] = profile['profile']
            policy['target_frame'] = 'left_camera_original_input_axes'
        policy.update(estimate_frame=name, estimate_transform=matrix(transform).tolist(), source_locations=sources)
    except (FrameEvidenceError, KeyError, OSError, ValueError, yaml.YAMLError) as exc:
        policy['blockers'].append(f'estimate_frame_unverified: {exc}')
    if dataset == 'euroc_mav':
        try:
            sensors, evidence = euroc_sensors(ws, seq)
            policy['evidence'].extend(evidence)
            policy.update(reference_frame='body_imu', reference_transform=matrix(sensors[0]['T_BS']).tolist(),
                          orientation_valid=True, common_origin_verified=policy['estimate_transform'] is not None)
        except (KeyError, OSError, ValueError) as exc:
            policy['blockers'].append(f'reference_frame_unverified: {exc}')
    elif dataset == 'rosariov2':
        try:
            t = physical_rosario_imu_to_camera(ws, seq, snapshots)
            policy.update(reference_frame='mins_imu_pose', reference_transform=t.tolist(),
                          orientation_valid=True,
                          common_origin_verified=policy['estimate_transform'] is not None,
                          reference_limitations=['fused_stereo_imu_ppk_reference_not_independent_ground_truth'])
            policy['source_locations'].append('docs/reference-review-20261001.md')
        except (FrameEvidenceError, KeyError, OSError, ValueError) as exc:
            policy['blockers'].append(f'reference_frame_unverified: {exc}')
    elif dataset == 'zed2i':
        policy.update(reference_frame='lever_arm_corrected_camera_position_identity_quaternion',
                      reference_transform=np.eye(4).tolist(),
                      common_origin_verified=policy['estimate_transform'] is not None)
        policy['blockers'].append('zed_reference_orientation_unavailable')
    elif dataset == 'citrusfarm':
        # Single-antenna RTK positions moved to the left camera (lever arm, path heading).
        policy.update(reference_frame='lever_arm_corrected_camera_position_identity_quaternion',
                      reference_transform=np.eye(4).tolist(),
                      common_origin_verified=policy['estimate_transform'] is not None)
        policy['blockers'].append('citrusfarm_reference_orientation_unavailable')
    elif dataset == 'hortimulti':
        policy['reference_frame'] = {'strawberry02': 'TagMap/base_link', 'strawberry03': 'odom/odom_mapping'}.get(seq)
        policy['blockers'].append('horti_reference_to_camera_extrinsic_unverified')
    else:
        policy['blockers'].append('reference_frame_unverified')
    policy['orientation_valid'] &= policy['estimate_transform'] is not None
    policy['evidence'].extend(snapshots.evidence)
    policy['trajectory_export_stage'] = snapshots.export_stage
    return policy
