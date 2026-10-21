#!/usr/bin/env python3
"""Build the Sielinko engine-on noise profile: a labelled sensitivity, never Rule C.

The profile replaces only the white-noise densities: engine-on standstill values
(configs/sensors/sources/zed2i/allan-20261018.json, engine_on_standstill.selected)
with the engine-off random walks, each times the estimator's own EuRoC ratio, exactly
as Rule C scales the engine-off reference. Every profile file is a copy of the
estimator's Rule C config with only the four noise values changed, so the two
variants differ in IMU noise alone. VIO on field1_110426_full_10fps_q90 only.

A run selects the profile through the environment variables listed in profile.json
(absolute paths under the repository); results are sensitivity runs and never count
toward a Rule C cell.
"""
import argparse
import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'scripts/run'), str(ROOT/'scripts/setup')]
import _imu_noise_rule as rule
import _imu_noise_override as override
from prepare_rule_c_20261021 import MARKER, BASALT_NOTE, with_noise

DATASET = 'zed2i'
SEQUENCE = 'field1_110426_full_10fps_q90'
NAME = 'zed2i-engine-on-20261021'
PROFILE = ROOT/'configs/sensitivity'/NAME
SOURCE = ROOT/'configs/sensors/sources/zed2i/allan-20261018.json'
PROFILE_MARKER = ('# IMU noise: SENSITIVITY profile zed2i-engine-on-20261021, NOT Rule C: engine-on standstill white '
                  'densities + engine-off random walks, x this estimator\'s EuRoC ratios.')
PROFILE_NOTE = ('Sensitivity profile zed2i-engine-on-20261021, NOT Rule C: engine-on standstill white densities and '
                'engine-off random walks x Basalt EuRoC ratios.')
# Estimator -> (Rule C config it copies, environment variable that selects the copy).
FILES = {
    'orbslam3': (f'configs/orbslam3/{DATASET}_{SEQUENCE}_stereo_inertial.yaml', 'ORBSLAM3_CONFIG'),
    'okvis2': (f'configs/okvis2/{DATASET}_{SEQUENCE}_vio.yaml', 'OKVIS2_CONFIG'),
    'okvis2x': (f'configs/okvis2x/{DATASET}_{SEQUENCE}_vio.yaml', 'OKVIS2X_CONFIG'),
    'basalt': (f'configs/basalt/{DATASET}_calib.json', 'BASALT_CALIBRATION'),
    'voxel_svio': (f'configs/voxel_svio/{DATASET}.yaml', 'VOXEL_SVIO_CONFIG'),
    'openvins': (f'configs/openvins/{DATASET}', 'OPENVINS_CONFIG_DIR'),
    'svo_pro': (None, 'SVO_PRO_IMU_NOISE'),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def reference(source=SOURCE):
    s = json.loads(Path(source).read_text())
    on, off = s['engine_on_standstill']['selected'], s['engine_off_static']['reference']
    return dict(gyroscope_noise_density=on['gyroscope_noise_density'],
                accelerometer_noise_density=on['accelerometer_noise_density'],
                gyroscope_random_walk=off['gyroscope_random_walk'],
                accelerometer_random_walk=off['accelerometer_random_walk'])


def noise(algorithm, source=SOURCE):
    """Rule C's scaling applied to the profile reference instead of the engine-off reference."""
    r = copy.deepcopy(rule.load())
    r['dataset_allan'][DATASET] = dict(r['dataset_allan'][DATASET], **reference(source))
    return rule.noise(algorithm, DATASET, r)


def build(root=ROOT):
    root = Path(root)
    out = root/'configs/sensitivity'/NAME
    if out.exists():
        shutil.rmtree(out)
    previous = {MARKER: '{marker}'}
    entries = {}
    for algorithm, (source, variable) in FILES.items():
        n = noise(algorithm)
        target_dir = out/algorithm
        target_dir.mkdir(parents=True)
        if algorithm == 'svo_pro':
            target = target_dir/'imu-noise.json'
            target.write_text(json.dumps(override.document(algorithm, DATASET, n), indent=2) + '\n')
            copied = {}
        elif algorithm == 'openvins':
            target = target_dir/DATASET
            shutil.copytree(root/source, target)
            chain = target/'kalibr_imu_chain.yaml'
            chain.write_text(with_noise(chain, algorithm, n, PROFILE_MARKER, PROFILE_NOTE, previous))
            copied = {str(p.relative_to(root)): sha(p) for p in sorted((root/source).iterdir())}
        else:
            target = target_dir/Path(source).name
            target.write_text(with_noise(root/source, algorithm, n, PROFILE_MARKER, PROFILE_NOTE, previous))
            copied = {source: sha(root/source)}
        files = [target] if target.is_file() else sorted(target.iterdir())
        entries[algorithm] = dict(
            environment={variable: str(target.relative_to(root))},
            noise=n,
            files={str(p.relative_to(root)): sha(p) for p in files},
            copied_from_rule_c=copied)
    profile = dict(
        schema=1,
        name=NAME,
        label='Sielinko operating-idle (engine-on) IMU noise sensitivity',
        not_rule_c=True,
        counts_toward_rule_c_cells=False,
        dataset=DATASET, sequence=SEQUENCE, modes=['vio'],
        decided='2026-10-21 (user): run as a labelled sensitivity at N=1, CPU estimators only',
        reference=reference(),
        reference_source=dict(path=str(SOURCE.relative_to(ROOT)), sha256=sha(root/SOURCE.relative_to(ROOT))),
        scaling='Rule C factors: authors EuRoC value / EuRoC Kalibr value per quantity (configs/sensors/imu-noise-rule.json)',
        environment_paths='relative to the repository root; set them as absolute paths ($REPO/<path>)',
        estimators=entries)
    (out/'profile.json').write_text(json.dumps(profile, indent=2) + '\n')
    return out


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(build().relative_to(ROOT))


if __name__ == '__main__':
    main()
