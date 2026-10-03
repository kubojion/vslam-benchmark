#!/usr/bin/env python3
"""Read-only repetition exceptions, native exports and bundled-profile comparison.

This produces evidence, not acceptance decisions. Bundled examples are supported
starting points, not optimal parameters or proof of historical binary linkage.
"""
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO/'scripts/eval'))
from audit_saved_parameters import audit, parse_snapshot
from build_benchmark_csv import preserved_write


def evidence(path):
    return dict(path=str(path.relative_to(REPO)), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def author_path(algo, mode, role):
    if algo == 'orbslam3' and role == 'estimator_config':
        return 'src/ORB_SLAM3/Examples/' + ('Stereo-Inertial' if mode.startswith('vio') else 'Stereo') + '/EuRoC.yaml'
    return {
        ('okvis2', 'estimator_config'): 'src/okvis2/config/euroc.yaml',
        ('okvis2x', 'estimator_config'): 'src/okvis2x/config/euroc/okvis2.yaml',
        ('ov2slam', 'estimator_config'): 'src/ov2slam/parameters_files/accurate/euroc/euroc_stereo.yaml',
        ('openvins', 'estimator_config'): 'src/open_vins/config/euroc_mav/estimator_config.yaml',
        ('voxel_svio', 'estimator_config'): 'src/voxel_svio/config/euroc.yaml',
        ('airslam', 'camera_config'): 'src/airslam/configs/camera/euroc.yaml',
        ('airslam', 'odometry_config'): 'src/airslam/configs/visual_odometry/vo_euroc.yaml',
        ('airslam', 'map_refinement_config'): 'src/airslam/configs/map_refinement/mr_euroc.yaml',
        ('dpvo', 'algorithm_config'): 'src/DPVO/config/default.yaml',
        ('macvo', 'odometry_config'): 'src/MAC-VO/Config/Experiment/MACVO/MACVO_Performant.yaml',
        ('dsol', 'algorithm_config'): 'src/dsol/config/dsol_tta.yaml',
        ('dsol', 'algorithm_defaults'): 'src/dsol/config/dsol.yaml',
        ('svo_pro', 'algorithm_defaults'): 'src/svo_pro/svo_ros/param/vio_stereo.yaml',
        ('mast3r_fusion', 'algorithm_defaults'): 'src/mast3r_fusion/config/base_euroc.yaml',
    }.get((algo, role))


def differences(first, second):
    return {k: dict(example=first.get(k), saved=second.get(k))
            for k in sorted(first.keys() | second.keys()) if first.get(k) != second.get(k)}


def main():
    inventory = json.loads((REPO/'results/repair-20261001/inventory.json').read_text())
    selected = audit(inventory)
    profiles = {}; records = []
    for cell in inventory['cells']:
        for attempt in cell['attempts']:
            if not attempt['exists']:
                continue
            run = REPO/attempt['path']; meta_path = run/'run_meta.json'
            meta = json.loads(meta_path.read_text()) if meta_path.is_file() else {}
            record = dict(path=attempt['path'], config_verified=bool(attempt['snapshots']) and
                all(s['verified'] for s in attempt['snapshots']),
                numerical_status=attempt['numerical_status'], process=attempt['process'],
                coverage=attempt['coverage'], cohort=attempt['cohort_fingerprint'],
                current_config_differences=[], profile_groups=[], native_export_checks=[])
            for item in meta.get('provenance', {}).get('artifacts', []):
                if not item.get('snapshot'):
                    continue
                snapshot = run/item['snapshot']
                if snapshot.suffix not in ('.json', '.yaml', '.yml'):
                    continue
                saved = parse_snapshot(snapshot)
                current = REPO/item['path']
                if item['path'].startswith('configs/') and current.is_file():
                    delta = differences(parse_snapshot(current), saved)
                    if delta:
                        record['current_config_differences'].append(dict(current=evidence(current),
                            saved=evidence(snapshot), differences=delta))
                author = author_path(cell['algorithm'], cell['run_type'], item['role'])
                if cell['dataset'] != 'euroc_mav' or not author:
                    continue
                group = '|'.join((cell['algorithm'], cell['run_type'], item['role'], item['snapshot_sha256']))
                if group not in profiles:
                    profiles[group] = dict(author=evidence(REPO/author), saved=evidence(snapshot),
                        differences=differences(parse_snapshot(REPO/author), saved), attempts=[])
                profiles[group]['attempts'].append(attempt['path']); record['profile_groups'].append(group)
            log = run/'run_log.txt'
            if log.is_file():
                content = log.read_text(errors='replace')
                record['log'] = evidence(log)
                record['native_error_observations'] = [dict(line=i, text=line[-600:])
                    for i, line in enumerate(content.splitlines(), 1)
                    if re.search(r'terminate called|Segmentation fault|bad_alloc|Assertion.*failed|Killed$', line)]
                # These are observations. A RANSAC/init warning is not a fatal exit.
                patterns = r'Input sensor was set|Opened configuration|Camera Parameters|Image resolution|FPS:|Number of Features|No\. cam [01] images|Finished VIO|config_file:|save.*trajectory|Saving.*trajectory|Segmentation fault|terminate called|bad_alloc|Assertion.*failed|Killed$'
                record['startup_completion_observations'] = [dict(line=i, text=line[-600:])
                    for i, line in enumerate(content.splitlines(), 1) if re.search(patterns, line, re.I)][:100]
            trajectory = run/'trajectory.txt'
            if trajectory.is_file() and cell['algorithm'] in ('okvis2', 'okvis2x', 'ov2slam', 'airslam'):
                tum = np.loadtxt(trajectory, ndmin=2)
                paths = list(run.glob('*trajectory.csv')) if cell['algorithm'] != 'ov2slam' else list(run.glob('ov2slam_traj.txt')) + list(run.glob('ov2slam_full_traj_wlc_opt.txt'))
                if cell['algorithm']=='airslam':
                    paths=list(run.glob('trajectory_v1.txt' if cell['run_type'].endswith('lc') else 'trajectory_v0.txt'))
                for native in paths:
                    try:
                        original = np.loadtxt(native, delimiter=',' if native.suffix=='.csv' else None,
                            skiprows=1 if native.suffix=='.csv' else 0, usecols=range(8), ndmin=2)
                        if native.suffix=='.csv': original[:, 0] /= 1e9
                        if native.name == 'ov2slam_full_traj_wlc_opt.txt':
                            raw = np.loadtxt(run/'ov2slam_traj.txt', ndmin=2)
                            indices = original[:, 0].astype(int)
                            if not np.array_equal(original[:, 0], indices) or np.any(indices < 0) or np.any(indices >= len(raw)):
                                raise ValueError('invalid optimized export frame index')
                            original[:, 0] = raw[indices, 0]
                        equal = original.shape == tum.shape and bool(np.allclose(original, tum, atol=1.1e-6, rtol=0))
                        record['native_export_checks'].append(dict(source=evidence(native),
                            selected=evidence(trajectory), same_shape=original.shape==tum.shape,
                            matches_selected_tum=equal, native_poses=len(original), selected_poses=len(tum)))
                    except ValueError as exc:
                        record['native_export_checks'].append(dict(source=evidence(native), error=str(exc)))
            records.append(record)
    result = dict(schema=1, scope='all_existing_default_repetitions', profiles=profiles, records=records,
                  selected_parameter_audit=selected,
                  summary=dict(existing_attempts=len(records), shared_euroc_profiles=len(profiles),
                    selected_mode_checks=selected['summary'],
                    native_exports_correspond=sum(any(n.get('matches_selected_tum') for n in r['native_export_checks']) for r in records)))
    preserved_write(REPO/'results/acceptance-20261001/evidence.json', json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    main()
