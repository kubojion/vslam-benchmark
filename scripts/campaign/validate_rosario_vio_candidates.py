#!/usr/bin/env python3
"""Read-only Rosario candidate/evidence validation; writes one explicit report.

Does not run estimators, change datasets, score trajectories or edit acceptance.
Native execution remains unverified even if every assertion here passes.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

import cv2
import numpy as np

from configuration_recipe import config_recipe
from protocol_status import attempt_protocol
from prepare_rosario_vio_candidates import BUNDLE, digest, read_yaml, select_candidate, verified_sources


def csv_rows(path):
    with path.open() as stream:
        return list(csv.reader(line for line in stream if not line.startswith('#')))


def validate(main, bundle=BUNDLE):
    source = verified_sources(bundle)
    source_index = json.loads((source / 'index.json').read_text())
    for row in source_index['files']:
        assert digest(main / row['original_path']) == row['sha256'], row['original_path']
    inventory_path = main / 'results/repair-20261001/inventory.json'
    inventory = json.loads(inventory_path.read_text())
    manifest_path = main / 'results/repair-20261001/future-n3-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    report = dict(checked_at=datetime.now(timezone.utc).isoformat(),
        scope='static candidate preparation and preserved evidence only; no native execution or scoring',
        main_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=main, text=True).strip(),
        config_prepared=True, verified_ready_to_run=False, candidates_activated=False,
        inventory_sha256=digest(inventory_path), existing_manifest_sha256=digest(manifest_path),
        source_index=source_index, candidate_index=json.loads((bundle / 'index.json').read_text()),
        datasets={}, confirmed_reruns=[], missing_repetitions=[], camera_review_only=[],
        current_runner_selection={}, native_source_evidence=[])
    review_root = bundle.parents[2]
    upstream = json.loads((review_root / 'review-evidence/rosario-vio-20261002/upstream/sources.json').read_text())
    for row in upstream:
        assert digest(review_root / row['path']) == row['sha256'], row['path']
    report['upstream_source_evidence'] = upstream

    for cell in inventory['cells']:
        if cell['dataset'] != 'rosariov2':
            continue
        affected = cell['run_type'] == 'vio' and cell['algorithm'] in ('basalt', 'voxel_svio', 'openvins')
        camera_review_only = ((cell['run_type'] == 'vio' and cell['algorithm'] in
                              ('orbslam3', 'airslam', 'okvis2', 'okvis2x')) or
                             (cell['run_type'] == 'vo' and cell['algorithm'] == 'basalt'))
        if not (affected or camera_review_only):
            continue
        for i, a in enumerate(cell['attempts'], 1):
            if not a['exists']:
                if affected:
                    report['missing_repetitions'].append(dict(cell=cell['key'], repetition=i,
                                                             absent_historical_path=a['path']))
                continue
            # Check immutable saved artifacts against the previously reviewed inventory.
            for f in a['files']:
                assert digest(main / f['path']) == f['sha256'], f['path']
            findings = [f['code'] for f in a.get('confirmed_protocol_findings', [])]
            record = dict(path=a['path'], observed_outcome=attempt_protocol(a)['observed_outcome'], evaluated=a['evaluated'],
                          exit_code=a['process']['exit_code'], findings=findings,
                          historical_artifact_hashes=a['files'], claim_limits=a['qualification']['claim_limits'])
            if affected:
                assert 'rosario_identity_camera_imu_extrinsic' in findings
                actions = [x for x in manifest['actions'] if x['cell'] == cell['key'] and x['repetition'] == i]
                assert len(actions) == 1 and actions[0]['category'] == 'required_rerun'
                action = actions[0]
                record['existing_plan'] = {k: action[k] for k in ('id', 'planned_output', 'readiness', 'runtime_estimate')}
                report['confirmed_reruns'].append(record)
            else:
                assert not findings
                report['camera_review_only'].append(record)
        if affected:
            recipe = config_recipe(main, cell)
            assert not recipe['selection_errors']
            assert all('candidates/' not in item['path'] for item in recipe['source_files'])
            report['current_runner_selection'][cell['key']] = recipe

    assert len(report['confirmed_reruns']) == 14
    assert len(report['missing_repetitions']) == 4
    assert len(report['camera_review_only']) == 30  # 24 adjacent VIO + six Basalt VO

    prefix_path = main / 'results/reference-review-20261001/author-downloads/bag-prefix-evidence.json'
    prefix = json.loads(prefix_path.read_text())
    report['bag_prefix_evidence_sha256'] = digest(prefix_path)
    for seq, bag_label in (('sequence1', 'rosario-seq1-bag-prefix'), ('sequence5', 'rosario-seq5-bag-prefix')):
        dataset = main / 'datasets/rosariov2' / seq / 'mav0'
        lists = [csv_rows(dataset / cam / 'data.csv') for cam in ('cam0', 'cam1')]
        stamps = [np.array([int(row[0]) for row in rows], dtype=np.int64) for rows in lists]
        for times in stamps:
            assert np.all(np.diff(times) > 0)
        np.testing.assert_array_equal(*stamps)
        checks = []
        for entry in prefix:
            if not entry.get('file', '').endswith(bag_label) or 'local_path' not in entry or 'infra' not in entry['topic']:
                continue
            pixels = cv2.imread(str(main / entry['local_path']), cv2.IMREAD_UNCHANGED)
            assert pixels.shape == (720, 1280) and pixels.dtype == np.uint8
            assert entry['encoding'] == 'mono8' and entry['local_pixels_identical']
            assert hashlib.sha256(pixels.tobytes()).hexdigest() == entry['sha256']
            checks.append({k: entry[k] for k in ('topic', 'stamp_ns', 'local_path', 'sha256')})
        assert len(checks) == 4
        imu_path = dataset / 'imu0/data.csv'
        rows = csv_rows(imu_path)
        imu_stamps = np.array([int(row[0]) for row in rows], dtype=np.int64)
        assert np.all(np.diff(imu_stamps) > 0)
        originals = [x for x in prefix if x.get('file', '').endswith(bag_label)
                     and x['topic'] == '/realsense/imu' and x['type'].endswith('/Imu')]
        sample_checks = []
        for original in originals:
            idx = int(np.argmin(np.abs(imu_stamps - original['stamp_ns'])))
            delta_ns = int(imu_stamps[idx]) - original['stamp_ns']
            assert abs(delta_ns) <= 256  # preserved float-roundtrip nanosecond rounding
            np.testing.assert_array_equal([float(x) for x in rows[idx][1:]], original['w'] + original['a'])
            sample_checks.append(dict(original_stamp_ns=original['stamp_ns'], rounding_ns=delta_ns,
                                      frame=original['frame'], values_unchanged=True))
        assert sample_checks
        report['datasets'][seq] = dict(stereo_pairs=len(stamps[0]), imu_samples=len(rows),
            csv_hashes={str(p.relative_to(main)): digest(p) for p in
                        [dataset / 'cam0/data.csv', dataset / 'cam1/data.csv', imu_path]},
            camera_stamps_equal=True, stamps_strictly_increasing=True,
            sampled_pixel_identity=checks, sampled_unrotated_imu=sample_checks,
            image_checks_scope='four saved images per sequence; reuses original bag-prefix audit',
            first_imu_minus_first_camera_s=(int(imu_stamps[0]) - int(stamps[0][0])) * 1e-9,
            last_imu_minus_last_camera_s=(int(imu_stamps[-1]) - int(stamps[0][-1])) * 1e-9,
            imu_covers_camera_start=bool(imu_stamps[0] < stamps[0][0]),
            imu_covers_camera_end=bool(imu_stamps[-1] > stamps[0][-1]))

    # Document code interpretation without claiming these sources prove installed binaries.
    native_paths = [
        'src/open_vins/ov_msckf/src/core/VioManagerOptions.h',
        'src/open_vins/ov_core/src/utils/opencv_yaml_parse.h',
        'src/open_vins/ov_msckf/src/ros/ROS2Visualizer.cpp',
        'src/voxel_svio/src/stereoVio.cpp',
        'scripts/run/run_basalt.sh', 'scripts/run/run_openvins.sh', 'scripts/run/run_voxel_svio.sh',
        'scripts/run/openvins_data_player.py', 'scripts/run/voxel_svio_data_player.py',
    ]
    for name in native_paths:
        report['native_source_evidence'].append(dict(path=name, sha256=digest(main / name)))
    for player in ('openvins_data_player.py', 'voxel_svio_data_player.py'):
        text = (main / 'scripts/run' / player).read_text()
        for topic in ('/cam0/image_raw', '/cam1/image_raw', '/imu0'):
            assert topic in text
        assert 'encoding="mono8"' in text
    for profile in report['candidate_index']['profiles']:
        for seq in ('sequence1', 'sequence5'):
            assert not select_candidate(profile, seq, bundle=bundle)['verified_ready_to_run']

    # Use OpenCV's published virtual projection only as a comparison, never materialize it.
    kalibr = read_yaml(source / 'kalibr-cameras.yaml')
    fs = cv2.FileStorage(str(source / 'author-orb.yaml'), cv2.FILE_STORAGE_READ)
    report['stereo_geometry'] = dict(
        kalibr_baseline_m=float(np.linalg.norm(np.array(kalibr['cam1']['T_cn_cnm1'])[:3, 3])),
        author_orb_bf=fs.getNode('Camera.bf').real(),
        author_orb_fx=fs.getNode('Camera.fx').real(),
        author_orb_RIGHT_P=fs.getNode('RIGHT.P').mat().tolist(),
        kalibr_T_imu_cam0=np.linalg.inv(kalibr['cam0']['T_cam_imu']).tolist())
    fs.release()
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = validate(args.evidence_root)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(confirmed_reruns=len(result['confirmed_reruns']),
        missing=len(result['missing_repetitions']), review_only=len(result['camera_review_only']),
        datasets={key: {k: value[k] for k in ('stereo_pairs', 'imu_samples')} for key, value in result['datasets'].items()},
        config_prepared=True, verified_ready_to_run=False)))
