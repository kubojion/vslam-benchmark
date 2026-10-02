#!/usr/bin/env python3
"""Recover a failed OKVIS causal export without replacing any original artifact.

This adds a separately labelled TUM conversion and receipt. It does not mark the
attempt complete, alter the native exit or substitute for final bundle adjustment.
"""
import argparse
import csv
import io
import json
from pathlib import Path

import numpy as np

from _pose_frames import Snapshots, file_evidence, verified_okvis_causal_recovery


def recover(repo, run):
    run = run.resolve()
    mode, dataset, sequence, algorithm, _ = run.relative_to(repo / 'results').parts
    if algorithm not in ('okvis2', 'okvis2x') or mode not in ('vo', 'vo-lc'):
        raise ValueError('only reviewed OKVIS visual causal CSV recovery is supported')
    trajectory, receipt = run / 'trajectory.txt', run / 'trajectory_recovery.json'
    if trajectory.exists() or receipt.exists():
        raise FileExistsError('preserve the existing selected trajectory and recovery record')
    if list(run.glob('*final-ba_trajectory.csv')):
        raise ValueError('a final-BA export exists; review it before recovering a causal prefix')
    meta = json.loads((run / 'run_meta.json').read_text())
    if meta.get('process', {}).get('exit_code') in (None, 0):
        raise ValueError('this recovery is for a recorded failed attempt')
    snapshots = Snapshots(run, meta, repo)
    cfg = snapshots.read('estimator_config')
    if cfg.get('camera_parameters', {}).get('online_calibration', {}).get('do_extrinsics', True):
        raise ValueError('online extrinsic calibration lacks per-pose evidence')
    source = run / 'okvis2-slam_trajectory.csv'
    with source.open() as stream:
        rows = list(csv.reader(stream))[1:]
    stamps = [int(row[0]) for row in rows]
    poses = np.array([[float(x) for x in row[1:8]] for row in rows])
    if (len(stamps) < 3 or poses.shape != (len(stamps), 7)
            or not np.isfinite(poses).all() or any(b <= a for a, b in zip(stamps, stamps[1:]))
            or not np.allclose(np.linalg.norm(poses[:, 3:], axis=1), 1, atol=1e-5)):
        raise ValueError('invalid native causal poses; do not repair by dropping/sorting rows')
    text = ''.join(f'{ns // 10**9}.{ns % 10**9:09d} ' +
                   ' '.join(f'{x:.17g}' for x in pose) + '\n' for ns, pose in zip(stamps, poses))
    with trajectory.open('x') as stream:
        stream.write(text)
    record = dict(schema=1, stage='recovered_causal_prefix', native_csv=source.name,
                  poses=len(stamps), first_timestamp_ns=stamps[0], last_timestamp_ns=stamps[-1],
                  duration_s=(stamps[-1]-stamps[0])/1e9, execution_status_unchanged=True,
                  limitation='Partial online poses only; configured final BA was not completed; native failure cause unresolved.',
                  evidence=[file_evidence(p, run) for p in (source, trajectory, run/'run_meta.json')],
                  converter=file_evidence(Path(__file__), repo))
    with receipt.open('x') as stream:
        stream.write(json.dumps(record, indent=2)+'\n')
    assert verified_okvis_causal_recovery(snapshots, cfg)
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    print(json.dumps(recover(Path(__file__).resolve().parents[2], args.run), indent=2))
