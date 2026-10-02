#!/usr/bin/env python3
"""Normalize Basalt IMU timestamps to the camera clock without changing source data.

For t_imu = t_camera + offset, feed t_imu - offset and set the effective native
calibration offset to zero. This avoids relying on an optional/disabled native
offset path, or double applying it. All measurements and camera stamps stay intact.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(sequence, calibration, destination):
    sequence, calibration, destination = map(lambda p: Path(p).resolve(), (sequence, calibration, destination))
    requested = json.loads(calibration.read_text())
    offset = requested['value0'].get('cam_time_offset_ns', 0)
    if isinstance(offset, bool) or not isinstance(offset, (int, float)) or not math.isfinite(offset) or int(offset) != offset:
        raise ValueError('Basalt offset must be an integer number of nanoseconds')
    offset = int(offset)
    imu = sequence / 'mav0/imu0/data.csv'
    camera = sequence / 'mav0/cam0/data.csv'
    rows = list(csv.reader(imu.open()))
    valid = [r for r in rows if r and not r[0].startswith('#')]
    stamps = [int(r[0]) for r in valid]
    cameras = [int(r[0]) for r in csv.reader(camera.open()) if r and not r[0].startswith('#')]
    if not stamps or not cameras or any(b <= a for a, b in zip(stamps, stamps[1:])):
        raise ValueError('nonempty strictly increasing IMU and camera input required')
    if any(b <= a for a, b in zip(cameras, cameras[1:])):
        raise ValueError('camera stamps must be strictly increasing')
    destination.mkdir(exist_ok=False)
    dataset = destination / 'dataset'
    (dataset / 'mav0/imu0').mkdir(parents=True)
    # Basalt's EuRoC reader resolves image filenames through the camera manifests.
    for sensor in ('cam0', 'cam1'):
        (dataset / 'mav0' / sensor).symlink_to(sequence / 'mav0' / sensor, target_is_directory=True)
    for sensor in ('state_groundtruth_estimate0', 'leica0', 'vicon0'):
        if (sequence / 'mav0' / sensor).exists():
            (dataset / 'mav0' / sensor).symlink_to(sequence / 'mav0' / sensor, target_is_directory=True)
    effective_imu = dataset / 'mav0/imu0/data.csv'
    with effective_imu.open('w') as stream:
        writer = csv.writer(stream)
        for row in rows:
            if row and not row[0].startswith('#'):
                row = [str(int(row[0]) - offset), *row[1:]]
            writer.writerow(row)
    effective = json.loads(json.dumps(requested))
    effective['value0']['cam_time_offset_ns'] = 0
    effective_calib = destination / 'effective-calibration.json'
    effective_calib.write_text(json.dumps(effective, indent=2) + '\n')
    record = dict(schema=1, policy='t_imu_on_camera_clock = original_t_imu - configured_offset_ns',
        requested_offset_ns=offset, native_offset_ns=0, camera_timestamps_changed=False,
        imu_values_changed=False, input_rows_removed=0, imu_samples=len(stamps),
        first_camera_ns=cameras[0], first_original_imu_ns=stamps[0],
        first_effective_imu_ns=stamps[0]-offset,
        first_frame_has_prior_imu=stamps[0]-offset <= cameras[0],
        last_frame_has_following_imu=stamps[-1]-offset >= cameras[-1],
        first_imu_lead_s=(cameras[0]-(stamps[0]-offset))/1e9,
        requested_calibration={'path':str(calibration),'sha256':sha(calibration)},
        effective_calibration={'path':str(effective_calib),'sha256':sha(effective_calib)},
        original_imu={'path':str(imu),'sha256':sha(imu)},
        effective_imu={'path':str(effective_imu),'sha256':sha(effective_imu)},
        export_timestamp_convention='camera clock; no post-export timestamp correction')
    (destination / 'clock-policy.json').write_text(json.dumps(record, indent=2) + '\n')
    return record


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sequence',type=Path)
    parser.add_argument('calibration',type=Path)
    parser.add_argument('destination',type=Path)
    args=parser.parse_args()
    print(json.dumps(prepare(args.sequence,args.calibration,args.destination),indent=2))
