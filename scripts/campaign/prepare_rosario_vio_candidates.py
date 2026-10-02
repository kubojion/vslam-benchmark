#!/usr/bin/env python3
"""Generate isolated, NOT execution-ready Rosario calibration candidates.

Only reads the hash-pinned small source bundle and writes inside its parent.
No estimator, dataset rewrite, campaign selection or acceptance change occurs.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re

import numpy as np
from scipy.spatial.transform import Rotation
import yaml

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / 'configs/candidates/rosario-vio-20261002'
NOISE = ('accelerometer_noise_density', 'accelerometer_random_walk',
         'gyroscope_noise_density', 'gyroscope_random_walk')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class ScientificLoader(yaml.SafeLoader):
    """OpenCV accepts 1e-12, but PyYAML's default YAML 1.1 resolver does not."""


ScientificLoader.add_implicit_resolver('tag:yaml.org,2002:float',
    re.compile(r'^[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)[eE][-+]?[0-9]+$'),
    list('-+0123456789.'))


def read_yaml(path):
    # OpenCV's YAML 1.0 directive is not a PyYAML directive.
    return yaml.load('\n'.join(line for line in Path(path).read_text().splitlines()
                               if not line.startswith('%YAML:')), Loader=ScientificLoader)


class FlowLists(yaml.SafeDumper):
    pass


FlowLists.add_representer(list, lambda dumper, value:
                         dumper.represent_sequence('tag:yaml.org,2002:seq', value, flow_style=True))


def dump_yaml(data, opencv=False):
    return ('%YAML:1.0\n---\n' if opencv else '') + (
        '# CANDIDATE ONLY: see index.json and docs/rosario-vio-candidates-20261002.md.\n'
        '# Published calibration; no extra image rectification; not approved for execution.\n'
    ) + yaml.dump(data, Dumper=FlowLists, sort_keys=False, width=160)


def invert(transform):
    """T_A_B maps coordinates in B into A; invert both rotation AND lever arm."""
    t = np.asarray(transform, dtype=float)
    if t.shape != (4, 4) or not np.all(np.isfinite(t)):
        raise ValueError('expected finite 4x4 rigid transform')
    if (not np.allclose(t[3], [0, 0, 0, 1], atol=1e-12, rtol=0)
            or not np.allclose(t[:3, :3].T @ t[:3, :3], np.eye(3), atol=1e-10, rtol=0)
            or not np.isclose(np.linalg.det(t[:3, :3]), 1., atol=1e-10, rtol=0)):
        raise ValueError('not an SE(3) transform')
    result = np.eye(4)
    result[:3, :3] = t[:3, :3].T
    result[:3, 3] = -t[:3, :3].T @ t[:3, 3]
    return result


def verified_sources(bundle):
    sources = bundle / 'sources'
    index = json.loads((sources / 'index.json').read_text())
    for record in index['files']:
        if digest(sources / record['file']) != record['sha256']:
            raise ValueError('source hash mismatch: ' + record['file'])
    return sources


def camera_chain(chain):
    result = copy.deepcopy(chain)
    for i in (0, 1):
        result[f'cam{i}']['rostopic'] = f'/cam{i}/image_raw'
    return result


def prepare(bundle=BUNDLE):
    bundle = Path(bundle).resolve()
    s = verified_sources(bundle)
    kalibr = read_yaml(s / 'kalibr-cameras.yaml')
    imu = read_yaml(s / 'kalibr-imu.yaml')['imu0']
    output = {}
    basalt = json.loads((s / 'saved-basalt-calibration.json').read_text())
    b = basalt['value0']
    for i in (0, 1):
        c = kalibr[f'cam{i}']
        t = invert(c['T_cam_imu'])
        q = Rotation.from_matrix(t[:3, :3]).as_quat()  # Hamilton x,y,z,w
        b['T_imu_cam'][i] = dict(zip(('px', 'py', 'pz', 'qx', 'qy', 'qz', 'qw'),
                                     [*t[:3, 3].tolist(), *q.tolist()]))
        params = dict(zip(('fx', 'fy', 'cx', 'cy'), c['intrinsics']))
        params.update(zip(('k1', 'k2', 'p1', 'p2'), c['distortion_coeffs']))
        # radtan8 reduces exactly to Kalibr's radtan4 when k3..k6 are zero.
        # -1 requests Basalt's native domain-radius computation, not a fitted mask.
        params.update(k3=0., k4=0., k5=0., k6=0., rpmax=-1.)
        b['intrinsics'][i] = {'camera_type': 'pinhole-radtan8', 'intrinsics': params}
        b['resolution'][i] = c['resolution']
    for key, source in zip(('accel_noise_std', 'accel_bias_std', 'gyro_noise_std', 'gyro_bias_std'), NOISE):
        b[key] = [imu[source]] * 3
    b['imu_update_rate'] = imu['update_rate']
    b['cam_time_offset_ns'] = round(kalibr['cam0']['timeshift_cam_imu'] * 1e9)
    output['basalt-kalibr/calibration.json'] = json.dumps(basalt, indent=2) + '\n'
    output['basalt-kalibr/vio_config.json'] = (s / 'saved-basalt-estimator.json').read_text()

    voxel = read_yaml(s / 'saved-voxel.yaml')
    for name in NOISE:
        voxel['imu_parameter'][name] = imu[name]
    for i, side in enumerate(('left', 'right')):
        c = kalibr[f'cam{i}']; dest = voxel['camera_parameter']
        for name in ('distortion_model', 'intrinsics', 'distortion_coeffs', 'resolution', 'timeshift_cam_imu'):
            dest[f'{name}_{side}'] = c[name]
        dest[f'T_imu_cam_{side}'] = invert(c['T_cam_imu']).flatten().tolist()
    output['voxel-kalibr/rosariov2.yaml'] = dump_yaml(voxel)

    for profile, cameras, estimator, imu_source in (
        ('openvins-kalibr', kalibr, 'saved-openvins-estimator.yaml', 'kalibr-imu.yaml'),
        ('openvins-author', read_yaml(s / 'author-openvins-cameras.yaml'),
         'author-openvins-estimator.yaml', 'author-openvins-imu.yaml'),
    ):
        settings = read_yaml(s / estimator)
        settings['relative_config_imu'] = 'kalibr_imu_chain.yaml'
        settings['relative_config_imucam'] = 'kalibr_imucam_chain.yaml'
        inertial = read_yaml(s / imu_source)
        inertial['imu0']['rostopic'] = '/imu0'
        if profile == 'openvins-kalibr':
            # Required by this OpenVINS parser even with IMU calibration disabled.
            # Kalibr supplies a calibrated IMU without skew/g-sensitivity estimates:
            # express that ideal model explicitly; these are not new measurements.
            for name in ('Tw', 'Ta', 'R_IMUtoGYRO', 'R_IMUtoACC'):
                inertial['imu0'][name] = np.eye(3).tolist()
            inertial['imu0']['Tg'] = np.zeros((3, 3)).tolist()
        output[f'{profile}/estimator_config.yaml'] = dump_yaml(settings, True)
        output[f'{profile}/kalibr_imucam_chain.yaml'] = dump_yaml(camera_chain(cameras), True)
        output[f'{profile}/kalibr_imu_chain.yaml'] = dump_yaml(inertial, True)

    for path, content in output.items():
        destination = bundle / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content)
    common = ['author_confirmation_of_profile_for_sequence1_and_sequence5_pixels',
              'predeclare_one_profile_per_cohort_without_score_selection',
              'native_loaded_configuration_and_timestamp_path_validation',
              'explicit_runner_selection_and_fresh_source_input_capture',
              'separate_authorization_for_execution']
    index = dict(schema=1, dataset='rosariov2', sequences=['sequence1', 'sequence5'], mode='vio',
                 config_prepared=True, verified_ready_to_run=False, activated_in_runners=False,
                 source_index_sha256=digest(s / 'index.json'),
                 files={name: digest(bundle / name) for name in sorted(output)}, profiles={})
    for profile, algorithm, source_profile, extra in (
        ('basalt-kalibr', 'basalt', 'published Kalibr sensor bundle; saved benchmark estimator policy',
         ['verify_installed_pinhole_radtan8_parser_and_rpmax', 'resolve_actual_camera_time_offset_consumption']),
        ('voxel-kalibr', 'voxel_svio', 'published Kalibr sensor bundle; saved benchmark estimator policy',
         ['verify_fixed_time_offset_export_compensation', 'validate_Rosario_native_shutdown_build']),
        ('openvins-kalibr', 'openvins', 'published Kalibr sensor bundle; saved benchmark estimator policy',
         ['validate_Rosario_native_shutdown_image', 'verify_odomimu_time_basis_and_reference_association']),
        ('openvins-author', 'openvins', 'author OpenVINS YAML reproduction; topic/path remapping only',
         ['validate_Rosario_native_shutdown_image', 'verify_odomimu_time_basis_and_reference_association',
          'author_implementation_and_launch_differences_remain']),
    ):
        source = read_yaml(s / 'author-openvins-cameras.yaml') if profile == 'openvins-author' else kalibr
        shifts = [source[f'cam{i}']['timeshift_cam_imu'] for i in (0, 1)]
        index['profiles'][profile] = dict(algorithm=algorithm, source_profile=source_profile,
            files=[f for f in sorted(output) if f.startswith(profile + '/')],
            config_prepared=True, verified_ready_to_run=False, activated_in_runners=False,
            image_policy='unchanged saved pixels; published residual radtan; no extra rectification',
            time_convention='t_imu = t_camera + timeshift_cam_imu',
            published_timeshifts_s=shifts, common_stereo_time_uses_left=True,
            unused_right_minus_left_s=shifts[1] - shifts[0], prerequisites=common + extra)
    (bundle / 'index.json').write_text(json.dumps(index, indent=2) + '\n')
    return index


def select_candidate(profile, sequence, *, dataset='rosariov2', mode='vio', bundle=BUNDLE):
    """Read-only inspection, deliberately NOT connected to any execution runner."""
    if dataset != 'rosariov2' or mode != 'vio' or sequence not in ('sequence1', 'sequence5'):
        raise ValueError('candidate only applies to Rosario sequences 1/5 in VIO')
    index = json.loads((bundle / 'index.json').read_text())
    if digest(bundle / 'sources/index.json') != index['source_index_sha256']:
        raise ValueError('source index changed')
    verified_sources(bundle)
    entry = copy.deepcopy(index['profiles'][profile])
    for name in entry['files']:
        if digest(bundle / name) != index['files'][name]:
            raise ValueError('candidate hash mismatch: ' + name)
    # No file, caller, or metadata edit can certify execution through this selector.
    entry.update(verified_ready_to_run=False, activated_in_runners=False,
                 sequence=sequence, inspection_only=True)
    return entry


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, default=BUNDLE)
    parser.add_argument('--inspect', choices=('basalt-kalibr', 'voxel-kalibr', 'openvins-kalibr', 'openvins-author'))
    parser.add_argument('--sequence', choices=('sequence1', 'sequence5'), default='sequence1')
    args = parser.parse_args()
    record = select_candidate(args.inspect, args.sequence, bundle=args.bundle) if args.inspect else prepare(args.bundle)
    print(json.dumps(record, indent=2))
