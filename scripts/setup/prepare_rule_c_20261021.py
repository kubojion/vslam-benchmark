#!/usr/bin/env python3
"""Apply Rule C to the Sielinko (zed2i) inertial configs (user decision 2026-10-21).

Only the four IMU noise values change: each estimator receives the engine-off static
Allan reference (configs/sensors/sources/zed2i/allan-20261018.json, admitted to the
rule by configs/sensors/imu-noise-rule-20261021.json) times its own EuRoC ratio.
Visual settings, geometry and every VO/VO-LC config stay as they are. SVO Pro and
MASt3R-Fusion read the rule at runtime; configs/sensors/zed2i.json (cuVSLAM, SVO Pro
camera profile) is regenerated from the ORB-SLAM3 profile. No estimator is run.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'scripts/run'), str(ROOT/'scripts/setup')]
import _imu_noise_rule as rule

DATASET = 'zed2i'
KEYS = ('gyroscope_noise_density', 'accelerometer_noise_density', 'gyroscope_random_walk', 'accelerometer_random_walk')
NAMES = {'orbslam3': ('IMU.NoiseGyro', 'IMU.NoiseAcc', 'IMU.GyroWalk', 'IMU.AccWalk'),
         'okvis2': ('sigma_g_c', 'sigma_a_c', 'sigma_gw_c', 'sigma_aw_c'),
         'okvis2x': ('sigma_g_c', 'sigma_a_c', 'sigma_gw_c', 'sigma_aw_c'),
         'basalt': ('gyro_noise_std', 'accel_noise_std', 'gyro_bias_std', 'accel_bias_std')}
MARKER = '# IMU noise: Rule C, Sielinko engine-off static Allan values x this estimator\'s EuRoC ratios (2026-10-21).'
BASALT_NOTE = ('Rule C (2026-10-21): Sielinko engine-off static Allan values x Basalt EuRoC ratios; '
               'configs/sensors/imu-noise-rule-20261021.json.')
# Comments that described the superseded field-envelope profile -> their replacement.
SUPERSEDED = {
    '# Common ZED field IMU profile (SN30291010), continuous-time densities.': '{marker}',
    "# IMU noise model: RealSense D435i.\n# Using OKVIS2 author's own D435i reference values, NOT raw Allan-variance.": '{marker}',
    '# IMU noise model: common ZED2i field profile (SN30291010), ~100 Hz as recorded.': '{marker}',
    '# Common recording-derived ZED profile. T_i_b': '{marker}\n# T_i_b',
    '# ZED2i field1 IMU. Common recording-derived profile shared by all estimators.': '{marker}',
    '# Common ZED field IMU profile, recorded ~100 Hz.': '{marker}',
}
STALE_INLINE = re.compile(r'envelope|factory', re.I)


def inertial_configs(root=ROOT):
    c = Path(root)/'configs'
    return {'orbslam3': sorted(c.glob(f'orbslam3/{DATASET}_*stereo_inertial*.yaml')),
            'okvis2': sorted(c.glob(f'okvis2/{DATASET}_*_vio*.yaml')),
            'okvis2x': sorted(c.glob(f'okvis2x/{DATASET}_*_vio*.yaml')),
            'airslam': [c/f'airslam/{DATASET}_camera_vio.yaml'],
            'openvins': [c/f'openvins/{DATASET}/kalibr_imu_chain.yaml'],
            'voxel_svio': [c/f'voxel_svio/{DATASET}.yaml'],
            'basalt': [c/f'basalt/{DATASET}_calib.json']}


def with_noise(path, algorithm, noise, marker=MARKER, note=BASALT_NOTE, previous=SUPERSEDED):
    """Text of `path` with exactly its four IMU noise values (and their comments) replaced."""
    path = Path(path)
    names = dict(zip(NAMES.get(algorithm, KEYS), KEYS))
    if path.suffix == '.json':
        value = json.loads(path.read_text())
        c = value['value0']
        for name, key in names.items():
            if len(c[name]) != 3:
                raise ValueError((str(path), name))
            c[name] = [noise[key]] * 3
        if '_comment_noise' in c:
            c['_comment_noise'] = note
        return json.dumps(value, indent=4) + '\n'
    text = path.read_text()
    for name, key in names.items():
        def replace(m):
            comment = m[3] or ''
            return m[1] + repr(float(noise[key])) + ('' if STALE_INLINE.search(comment) else comment)
        text, n = re.subn(r'(?m)^(\s*' + re.escape(name) + r':[ \t]*)(\S+)([ \t]*#[^\n]*)?$', replace, text)
        if n != 1:
            raise ValueError((str(path), name, n))
    for old, new in previous.items():
        text = text.replace(old, new.format(marker=marker))
    if text.count(marker) != 1:
        raise ValueError((str(path), 'expected exactly one noise comment', text.count(marker)))
    return text


def apply_rule_c(root=ROOT):
    changed = []
    for algorithm, paths in inertial_configs(root).items():
        noise = rule.noise(algorithm, DATASET)
        for path in paths:
            text = with_noise(path, algorithm, noise)
            if path.read_text() != text:
                path.write_text(text)
                changed.append(path)
    from build_sensor_profiles import orb_profile
    path = Path(root)/f'configs/sensors/{DATASET}.json'
    text = json.dumps(orb_profile(Path(root), DATASET), indent=2) + '\n'
    if path.read_text() != text:
        path.write_text(text)
        changed.append(path)
    return changed


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    for path in apply_rule_c():
        print(path.relative_to(ROOT))


if __name__ == '__main__':
    main()
