"""Audit of delivered inputs and the unchanged native Voxel camera gate.

This module checks recorded evidence only. It does not run estimators.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import yaml


def timestamps(path):
    with Path(path).open() as stream:
        values=[int(row[0]) for row in csv.reader(stream) if row and not row[0].startswith('#')]
    if not values or any(a>=b for a,b in zip(values,values[1:])):
        raise ValueError('Expected nonempty strictly increasing input timestamps')
    return values


def ros_seconds(ns):
    sec,nsec=divmod(ns,1_000_000_000)
    return float(sec)+1e-9*float(nsec)


def native_rate_prediction(stamps,frequency):
    if not math.isfinite(frequency) or frequency<=0:
        raise ValueError('Native camera frequency must be positive and finite')
    previous=None
    skipped=[]
    for index,stamp in enumerate(stamps):
        current=ros_seconds(stamp)
        # Preserve the native double comparison and update only on acceptance.
        if previous is not None and current<previous+1.0/frequency:
            skipped.append(dict(index=index,timestamp_ns=stamp))
        else:
            previous=current
    return dict(queued=len(stamps)-len(skipped),rate_skipped=skipped)


def audit(run,dataset):
    run,dataset=Path(run),Path(dataset)
    tx=json.loads((run/'transport_stats.json').read_text())
    rx=json.loads((run/'native/input_receipt.json').read_text())
    native=re.findall(r'^track_frequency:\s*([0-9.eE+-]+)\s*$',
                      (run/'native/parameter_list.txt').read_text(),re.M)
    if len(native)!=1:
        raise ValueError('Expected one native camera-frequency declaration')
    frequency=float(native[0])
    effective=yaml.safe_load((run/'effective_ros_parameters.yaml').read_text())
    declared=float(effective['odometry_parameter']['track_frequency'])
    files={name:dataset/'mav0'/name/'data.csv' for name in ('cam0','cam1','imu0')}
    series={name:timestamps(path) for name,path in files.items()}
    camera,imu=series['cam0'],series['imu0']
    prediction=native_rate_prediction(camera,frequency)
    checks=dict(
        frequency_matches_effective_configuration=frequency==declared,
        stereo_input_timestamps_agree=camera==series['cam1'],
        publisher_expected_camera_count=tx['camera_frames_expected']==len(camera),
        publisher_camera_count=tx['camera_frames_published']==len(camera),
        publisher_imu_count=tx['imu_messages_published']==len(imu),
        no_camera_read_failures=tx['camera_read_failures']==0,
        native_camera_count=rx['stereo_received']==len(camera),
        native_imu_count=rx['imu_received']==len(imu),
        native_queued_matches_unchanged_rate_gate=rx['stereo_queued_after_rate_gate']==prediction['queued'],
        camera_first_timestamp=rx['first_camera_s']==ros_seconds(camera[0]),
        camera_last_timestamp=rx['last_camera_s']==ros_seconds(camera[-1]),
        imu_first_timestamp=rx['first_imu_s']==ros_seconds(imu[0]),
        imu_last_timestamp=rx['last_imu_s']==ros_seconds(imu[-1]),
    )
    return dict(schema=1,passed=all(checks.values()),checks=checks,
        native_frequency_hz=frequency,expected=prediction,published=tx,received=rx,
        input_csv_sha256={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in files.items()},
        limitation='Counts and endpoints are audited. Existing native instrumentation does not prove every received timestamp or its order.',
        policy='Do not alter native sampling. Require exactly the camera count predicted by its configured timestamp gate; any additional missing input fails.')
