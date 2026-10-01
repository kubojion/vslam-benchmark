#!/usr/bin/env python3
"""Select and validate saved-input configurations without executing estimators.

Uses the standard library so it can run before estimator environments are loaded.
"""
import argparse
import json
import math
from pathlib import Path
import re


def camera_rate(times_path):
    times = [int(line.strip()) for line in Path(times_path).read_text().splitlines()
             if line.strip() and not line.lstrip().startswith('#')]
    if len(times) < 2 or any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError('camera times must contain increasing nanosecond timestamps')
    # Deliberate 15 -> 10 Hz decimation alternates short and long intervals.
    # Its median interval can still be ~1/15 s, so use the observed mean rate.
    return (len(times)-1)*1e9 / (times[-1]-times[0])


def orb_camera_rate(config):
    values = re.findall(r'^Camera\.fps:\s*([0-9.eE+-]+)', Path(config).read_text(), re.M)
    if len(values) != 1:
        raise ValueError('expected exactly one Camera.fps setting')
    rate = float(values[0])
    if not math.isfinite(rate) or rate <= 0:
        raise ValueError('Camera.fps must be finite and positive')
    return rate


def select_orb_config(repo, dataset, sequence, mode, override=None):
    root = Path(repo)/'configs/orbslam3'
    suffix = {'vo': 'stereo', 'vo-lc': 'stereo_lc',
              'vio': 'stereo_inertial', 'vio-lc': 'stereo_inertial_lc'}[mode]
    if override:
        candidates = [Path(override)]
    else:
        # A sequence-specific sensor file takes precedence over the dataset
        # fallback. LC is materialized by the runner after selection.
        candidates = [root/f'{dataset}_{sequence}_{suffix}.yaml']
        if mode.startswith('vio'):
            candidates.append(root/f'{dataset}_{sequence}_stereo_inertial.yaml')
        else:
            candidates.extend([root/f'{dataset}_{sequence}_stereo.yaml', root/f'{dataset}_{sequence}.yaml'])
        candidates.append(root/f'{dataset}_{suffix}.yaml')
    config = next((p for p in candidates if p.is_file()), None)
    if config is None:
        raise ValueError(f'no ORB config found in {[str(p) for p in candidates]}')
    measured = camera_rate(Path(repo)/'datasets'/dataset/sequence/'times.txt')
    configured = orb_camera_rate(config)
    # Small acquisition gaps make Rosario's mean rate ~14.6 Hz at nominal 15.
    # A fixed 5% acquisition tolerance admits that, but rejects 15 vs 10 Hz.
    if not math.isclose(measured, configured, rel_tol=.05):
        raise ValueError(f'Camera.fps={configured:g} disagrees with input mean rate {measured:.6g} Hz: {config}')
    return config


def basalt_baseline(calibration):
    cams = json.loads(Path(calibration).read_text())['value0']['T_imu_cam']
    if len(cams) != 2:
        raise ValueError('reviewed Basalt profile requires a stereo calibration')
    baseline = math.sqrt(sum((float(cams[1][k])-float(cams[0][k]))**2 for k in ('px','py','pz')))
    if not math.isfinite(baseline) or baseline <= 0:
        raise ValueError('invalid stereo baseline')
    return baseline


def validate_basalt(config, calibration, mode):
    values = json.loads(Path(config).read_text())['value0']
    if values.get('config.vio_enforce_realtime') is not False:
        raise ValueError('quality profile must disable Basalt real-time frame dropping')
    if mode == 'vo':
        threshold = float(values['config.vio_min_triangulation_dist'])
        baseline = basalt_baseline(calibration)
        if not math.isfinite(threshold) or threshold <= 0 or threshold >= baseline:
            raise ValueError(f'VO triangulation gate {threshold:g} m must be positive and below stereo baseline {baseline:.9g} m')


def select_basalt_config(repo, dataset, mode, override=None):
    if mode not in ('vo', 'vio'):
        raise ValueError('Basalt supports vo/vio only')
    root = Path(repo)/'configs/basalt'
    name = 'rosariov2_vo_config.json' if dataset == 'rosariov2' and mode == 'vo' else f'{mode}_config.json'
    config = Path(override) if override else root/name
    validate_basalt(config, root/f'{dataset}_calib.json', mode)
    return config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('algorithm', choices=('orbslam3', 'basalt'))
    parser.add_argument('repo', type=Path)
    parser.add_argument('dataset')
    parser.add_argument('sequence')
    parser.add_argument('mode')
    parser.add_argument('--override')
    args = parser.parse_args()
    try:
        path = (select_orb_config(args.repo, args.dataset, args.sequence, args.mode, args.override)
                if args.algorithm == 'orbslam3' else select_basalt_config(args.repo, args.dataset, args.mode, args.override))
    except (ValueError, KeyError, OSError) as exc:
        parser.error(str(exc))
    print(path)


if __name__ == '__main__':
    main()
