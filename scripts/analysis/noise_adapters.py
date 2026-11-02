"""Materialize candidates without changing geometry, modes or production files.

The ten VIO estimators, selected through the same hooks as main's labelled
sensitivity profiles (configs/sensitivity/).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'run'))
from _imu_noise_override import KEYS, document, validate_parameters

ORB_KEYS = ('IMU.NoiseGyro', 'IMU.NoiseAcc', 'IMU.GyroWalk', 'IMU.AccWalk')
OKVIS_KEYS = ('sigma_g_c', 'sigma_a_c', 'sigma_gw_c', 'sigma_aw_c')
BASALT_KEYS = ('gyro_noise_std', 'accel_noise_std', 'gyro_bias_std', 'accel_bias_std')
SUPPORTED = {'orbslam3', 'okvis2', 'okvis2x', 'airslam', 'basalt',
             'openvins', 'voxel_svio', 'cuvslam', 'svo_pro', 'mast3r_fusion'}
VIO_ONLY = {'basalt', 'openvins', 'voxel_svio'}
SNAPSHOT_ROLES = {
    'orbslam3': 'estimator_config', 'okvis2': 'estimator_config',
    'okvis2x': 'estimator_config', 'airslam': 'camera_config',
    'basalt': 'camera_calibration', 'openvins': 'imu_calibration',
    'voxel_svio': 'estimator_config', 'cuvslam': 'imu_noise_override',
    'svo_pro': 'camera_imu_calibration', 'mast3r_fusion': 'effective_config',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text() != content:
            raise RuntimeError('Refusing to replace an existing candidate: ' + str(path))
    else:
        with path.open('x') as stream:
            stream.write(content)


def json_text(value):
    return json.dumps(value, indent=2, allow_nan=False) + '\n'


def read_effective(path, algorithm):
    path = Path(path)
    text = path.read_text()
    if path.suffix == '.json':
        data = json.loads(text)
    else:
        text = '\n'.join(line for line in text.splitlines() if not line.startswith('%YAML'))
        data = yaml.safe_load(text.replace('!!opencv-matrix', ''))
    if algorithm == 'orbslam3':
        values = [data[k] for k in ORB_KEYS]
    elif algorithm in ('okvis2', 'okvis2x'):
        values = [data['imu_parameters'][k] for k in OKVIS_KEYS]
    elif algorithm == 'basalt':
        values = []
        for field in BASALT_KEYS:
            axes = data['value0'][field]
            if len(axes) != 3 or len(set(axes)) != 1:
                raise ValueError('Expected the same scalar noise on all three Basalt axes')
            values.append(axes[0])
    elif algorithm == 'svo_pro':
        fields = ('sigma_omega_c', 'sigma_acc_c', 'sigma_omega_bias_c', 'sigma_acc_bias_c')
        values = [data['imu_params'][k] for k in fields]
    elif algorithm == 'cuvslam':
        values = [data['parameters'][k] for k in KEYS]
    elif algorithm == 'mast3r_fusion':
        a, b = data['ms_opt']['imu_noise'], data['global_opt']['imu_noise']
        if len(a) != 4 or a != b:
            raise ValueError('Fusion noise must agree in sliding-window and global optimizers')
        values = [a[1], a[0], a[3], a[2]]
    else:
        for container in ('imu0', 'imu_parameter', 'imu'):
            if isinstance(data.get(container), dict) and all(k in data[container] for k in KEYS):
                data = data[container]
                break
        values = [data[k] for k in KEYS]
    return validate_parameters(dict(zip(KEYS, values)))


def verify_snapshot(run, algorithm, parameters):
    """Verify the wrapper's immutable effective-config evidence after execution.

    This is a config-flow check, not proof of numerical influence inside a closed
    implementation. Native diagnostics and launched paths are checked separately.
    """
    run = Path(run)
    meta = json.loads((run / 'run_meta.json').read_text())
    evidence = [item for item in meta.get('provenance', {}).get('artifacts', [])
                if item.get('role') == SNAPSHOT_ROLES[algorithm] and item.get('snapshot')]
    if len(evidence) != 1:
        raise RuntimeError('Missing or ambiguous effective-config snapshot for ' + algorithm)
    path = (run / evidence[0]['snapshot']).resolve()
    path.relative_to(run.resolve())
    actual = read_effective(path, algorithm)
    if actual != validate_parameters(parameters):
        raise RuntimeError('Saved native noise differs from proposed candidate: ' + algorithm)
    return dict(path=str(path), sha256=sha(path), parameters=actual)


def replace_scalars(text, fields, parameters):
    # Keep OpenCV's YAML header, tags, comments and every non-noise byte intact.
    for key, field in zip(KEYS, fields):
        pattern = r'^(\s*' + re.escape(field) + r':\s*)([-+0-9.eE]+)(?=\s|$)'
        text, count = re.subn(pattern, lambda m: m[1] + format(parameters[key], '.17g'),
                              text, flags=re.M)
        if count != 1:
            raise ValueError('Noise field missing or ambiguous: ' + field)
    return text


def noise_source(root, algorithm, dataset, parent_sequence, mode):
    """Repository path of the file holding a run's default noise; None where the Rule C helper applies it."""
    if algorithm in ('svo_pro', 'cuvslam', 'mast3r_fusion'):
        return None
    if algorithm == 'basalt':
        return f'configs/basalt/{dataset}_calib.json'
    if algorithm == 'openvins':
        return f'configs/openvins/{dataset}/kalibr_imu_chain.yaml'
    if algorithm == 'voxel_svio':
        return f'configs/voxel_svio/{dataset}.yaml'
    if algorithm == 'orbslam3':
        # Same order as the runner's preflight (_config_preflight.select_orb_config):
        # the recording's own file first, then the dataset file. LC is materialized by the runner.
        suffix = {'vio': 'stereo_inertial', 'vio-lc': 'stereo_inertial_lc'}[mode]
        return next(name for name in (
            f'configs/orbslam3/{dataset}_{parent_sequence}_{suffix}.yaml',
            f'configs/orbslam3/{dataset}_{parent_sequence}_stereo_inertial.yaml',
            f'configs/orbslam3/{dataset}_{suffix}.yaml') if (Path(root) / name).is_file())
    if algorithm == 'airslam':
        # Same order as run_airslam.sh: the inertial camera file if the dataset has one.
        return next(name for name in (f'configs/airslam/{dataset}_camera_vio.yaml',
                                      f'configs/airslam/{dataset}_camera.yaml') if (Path(root) / name).is_file())
    if algorithm in ('okvis2', 'okvis2x'):
        relative = f'configs/{algorithm}/{dataset}_{parent_sequence}_{mode.replace("-", "_")}.yaml'
        # Match OKVIS2's existing runner fallback. Supplying an explicit
        # candidate file would otherwise bypass its LC materialization.
        if algorithm == 'okvis2' and mode == 'vio-lc' and not (Path(root) / relative).is_file():
            relative = f'configs/okvis2/{dataset}_{parent_sequence}_vio.yaml'
        return relative
    raise ValueError('Unsupported experimental algorithm')


def prepare(root, algorithm, dataset, parent_sequence, mode, parameters, destination):
    """Return wrapper environment, all candidate files, and base-file identities.

    parent_sequence is explicit: prefixes use their physical parent's model.
    Destination must be under this worktree's private generated-config tree.
    """
    root = Path(root).resolve()
    destination = Path(destination).resolve()
    destination.relative_to(root / 'configs/experiments/generated')
    if algorithm not in SUPPORTED or mode not in ('vio', 'vio-lc'):
        raise ValueError('Unsupported experimental algorithm or mode')
    if mode == 'vio-lc' and algorithm in VIO_ONLY:
        raise ValueError('Algorithm has no VIO-LC mode')
    for token in (dataset, parent_sequence):
        if not re.fullmatch(r'[A-Za-z0-9_]+', token):
            raise ValueError('Invalid dataset or sequence identifier')
    parameters = validate_parameters(parameters)
    sources, files, env, mode_materialization = [], [], {}, []

    def source(relative):
        path = root / relative
        sources.append(dict(path=str(path.relative_to(root)), sha256=sha(path)))
        return path

    def output(name, text):
        path = destination / name
        save(path, text)
        files.append(dict(path=str(path), sha256=sha(path)))
        return str(path)

    if algorithm in ('svo_pro', 'cuvslam', 'mast3r_fusion'):
        path = output('noise.json', json_text(document(algorithm, dataset, parameters)))
        env[{'svo_pro': 'SVO_PRO_IMU_NOISE', 'cuvslam': 'CUVSLAM_IMU_NOISE',
             'mast3r_fusion': 'MAST3R_FUSION_IMU_NOISE'}[algorithm]] = path
        if algorithm == 'svo_pro':
            env['SVO_PRO_IMU_FILE'] = str(source(f'configs/okvis2/{dataset}_{parent_sequence}_vio.yaml'))
    elif algorithm == 'basalt':
        data = json.loads(source(f'configs/basalt/{dataset}_calib.json').read_text())
        for key, field in zip(KEYS, BASALT_KEYS):
            if len(data['value0'][field]) != 3:
                raise ValueError('Basalt noise must have three axes')
            data['value0'][field] = [parameters[key]] * 3
        env['BASALT_CALIBRATION'] = output('calibration.json', json_text(data))
    elif algorithm == 'openvins':
        for filename in ('estimator_config.yaml', 'kalibr_imucam_chain.yaml', 'kalibr_imu_chain.yaml'):
            text = source(f'configs/openvins/{dataset}/{filename}').read_text()
            if filename == 'kalibr_imu_chain.yaml':
                text = replace_scalars(text, KEYS, parameters)
            output(filename, text)
        env['OPENVINS_CONFIG_DIR'] = str(destination)
    else:
        relative = noise_source(root, algorithm, dataset, parent_sequence, mode)
        fields = {'orbslam3': ORB_KEYS, 'okvis2': OKVIS_KEYS, 'okvis2x': OKVIS_KEYS}.get(algorithm, KEYS)
        variable = {'orbslam3': 'ORBSLAM3_CONFIG', 'airslam': 'AIRSLAM_CAMERA_CONFIG',
                    'voxel_svio': 'VOXEL_SVIO_CONFIG'}.get(algorithm, algorithm.upper() + '_CONFIG')
        if algorithm == 'okvis2' and mode == 'vio-lc' and relative.endswith('_vio.yaml'):
            mode_materialization.append('do_loop_closures=true')
        text = replace_scalars(source(relative).read_text(), fields, parameters)
        if mode_materialization:
            text, count = re.subn(r'^(\s*do_loop_closures:\s*)(true|false)\b',
                                  lambda m: m[1] + 'true', text, flags=re.M)
            if count != 1:
                raise ValueError('Cannot uniquely materialize OKVIS2 VIO-LC mode')
        env[variable] = output('estimator.yaml', text)
    receipt = dict(schema=1, algorithm=algorithm, dataset=dataset,
                   parent_sequence=parent_sequence, mode=mode, parameters=parameters,
                   sources=sources, files=files, environment=env,
                   mode_materialization=mode_materialization)
    save(destination / 'candidate.json', json_text(receipt))
    return receipt
