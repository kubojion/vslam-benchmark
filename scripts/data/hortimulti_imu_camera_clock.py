#!/usr/bin/env python3
"""Move a HortiMulti MicroStrain IMU file onto the camera clock (decision 2026-10-05).

The February-session Kalibr calibration (Feb2026/Strawberry/calibration.yaml, imu0 block)
gives timeshift_cam_imu = 0.009160379134269684 s, Kalibr convention t_imu = t_cam + shift.
Every estimator gets the same correction by reading IMU stamps already on the camera clock,
t_imu - shift, with every native camera-IMU offset set to zero (OKVIS image_delay, Basalt
cam_time_offset_ns, Voxel-SVIO/OpenVINS timeshift, VINS-Fusion td, sensor-profile
camera_imu_time_offset_s). Camera stamps, IMU values and the reference are unchanged.

--apply keeps the IMU-clock file as sources/microstrain_imu_clock.csv (outside mav0/, so no
loader or input capture picks it up), rewrites mav0/imu0/data.csv and records both SHA-256
digests in manifest.json. Applying twice is refused. Re-extracting the sequence from the bags
restores IMU-clock stamps; apply this script again afterwards.

Usage: hortimulti_imu_camera_clock.py <sequence dir> [--apply]
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

SHIFT_S = 0.009160379134269684
SHIFT_NS = round(SHIFT_S * 1e9)          # 9160379 ns, as Basalt's cam_time_offset_ns used it
SOURCE = ('https://s3.eidf.ac.uk/eidf258-hortimulti-a-multi-sensor-dataset-for-polytunnels/'
          'Feb2026/Strawberry/calibration.yaml (imu0: timeshift_cam_imu)')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def shifted(text):
    """Only the leading stamp of each sample changes; header, values and line endings are kept."""
    newline = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(newline)
    if not lines or not lines[0].startswith('#') or lines[-1] != '':
        raise ValueError('expected the EuRoC header line and a final line ending')
    body = []
    previous = None
    for line in lines[1:-1]:
        stamp, rest = line.split(',', 1)
        value = int(stamp) - SHIFT_NS
        if previous is not None and value <= previous:
            raise ValueError('IMU stamps must be strictly increasing')
        previous = value
        body.append(f'{value},{rest}')
    return newline.join([lines[0]] + body + ['']), len(body)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('sequence', type=Path)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    sequence = args.sequence
    imu = sequence / 'mav0/imu0/data.csv'
    original = sequence / 'sources/microstrain_imu_clock.csv'
    manifest_path = sequence / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
    if 'camera_clock_shift_s' in manifest.get('imu', {}) or original.exists():
        raise SystemExit(f'{sequence}: IMU stamps are already on the camera clock; refusing to shift twice')
    text, samples = shifted(imu.read_bytes().decode('ascii'))   # bytes: keep CRLF files as CRLF
    report = dict(sequence=str(sequence), samples=samples, shift_ns=SHIFT_NS,
                  original_sha256=sha256(imu), camera_clock_sha256=hashlib.sha256(text.encode()).hexdigest())
    print(json.dumps(report, indent=1))
    if not args.apply:
        return
    original.parent.mkdir(exist_ok=True)
    shutil.copy2(imu, original)
    imu.write_bytes(text.encode('ascii'))
    if sha256(imu) != report['camera_clock_sha256'] or sha256(original) != report['original_sha256']:
        raise SystemExit('written files do not match the computed digests')
    manifest.setdefault('dataset', 'hortimulti')
    manifest.setdefault('sequence', sequence.name)
    manifest['imu'] = dict(
        sensor='MicroStrain 3DM-GX5-25 (/ms/imu/data), 200 Hz',
        camera_clock_shift_s=SHIFT_NS * 1e-9,
        camera_clock=('mav0/imu0/data.csv stamps = IMU-clock stamps - camera_clock_shift_s (Kalibr '
                      't_imu = t_cam + timeshift_cam_imu); IMU-clock copy in sources/microstrain_imu_clock.csv; '
                      'every estimator uses a zero camera-IMU time offset'),
        source=SOURCE, samples=samples,
        original=dict(path='sources/microstrain_imu_clock.csv', sha256=report['original_sha256']),
        camera_clock_file=dict(path='mav0/imu0/data.csv', sha256=report['camera_clock_sha256']),
        decided='2026-10-05 (user): one shared camera-clock IMU input for every HortiMulti estimator',
        script='scripts/data/hortimulti_imu_camera_clock.py')
    manifest_path.write_text(json.dumps(manifest, indent=1) + '\n')
    print(f'applied: {sequence} IMU stamps shifted by -{SHIFT_NS} ns onto the camera clock')


if __name__ == '__main__':
    main()
