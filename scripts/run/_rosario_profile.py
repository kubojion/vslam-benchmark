#!/usr/bin/env python3
"""Select an indexed Rosario candidate explicitly; never certify production readiness.

Uses only the standard library. Snapshot mode copies the complete selected bundle
before native startup, so the estimator loads the exact files captured as evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

BUNDLE = 'configs/candidates/rosario-vio-20261002'
FILES = {
    'basalt-kalibr': ('basalt', ['calibration.json', 'vio_config.json']),
    'voxel-kalibr': ('voxel_svio', ['rosariov2.yaml']),
    'openvins-kalibr': ('openvins', ['estimator_config.yaml', 'kalibr_imu_chain.yaml', 'kalibr_imucam_chain.yaml']),
    'openvins-author': ('openvins', ['estimator_config.yaml', 'kalibr_imu_chain.yaml', 'kalibr_imucam_chain.yaml']),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_profile(repo, algorithm, dataset, sequence, profile):
    repo = Path(repo).resolve()
    if dataset != 'rosariov2' or profile not in FILES or FILES[profile][0] != algorithm:
        raise ValueError('Rosario profile does not match this dataset/algorithm')
    bundle = repo / BUNDLE
    index = json.loads((bundle / 'index.json').read_text())
    source_sequence = sequence
    diagnostic = None
    if sequence not in index['sequences']:
        path = repo / 'datasets' / dataset / sequence / 'diagnostic.json'
        diagnostic = json.loads(path.read_text())
        source_sequence = diagnostic['source_sequence']
        if (diagnostic['source_dataset'] != dataset or source_sequence not in index['sequences']
                or diagnostic['diagnostic_sequence'] != sequence
                or diagnostic['scope'] != 'diagnostic_only_not_a_production_repetition'):
            raise ValueError('candidate diagnostic does not identify an eligible original recording')
    if index['dataset'] != dataset or index['mode'] != 'vio':
        raise ValueError('candidate index dataset/mode mismatch')
    entry = index['profiles'][profile]
    expected = [f'{profile}/{name}' for name in FILES[profile][1]]
    if entry['algorithm'] != algorithm or set(entry['files']) != set(expected):
        raise ValueError('incomplete or inconsistent indexed profile')
    source_index_path = bundle / 'sources/index.json'
    if digest(source_index_path) != index['source_index_sha256']:
        raise ValueError('source index hash mismatch')
    for item in json.loads(source_index_path.read_text())['files']:
        path = (bundle / 'sources' / item['file']).resolve()
        if not path.is_relative_to((bundle / 'sources').resolve()) or digest(path) != item['sha256']:
            raise ValueError('source hash mismatch: ' + item['file'])
    files = []
    for relative in expected:
        path = bundle / relative
        if digest(path) != index['files'][relative]:
            raise ValueError('candidate hash mismatch: ' + relative)
        files.append({'name': path.name, 'source': str(path), 'sha256': digest(path)})
    if algorithm == 'openvins':
        settings = (bundle / profile / 'estimator_config.yaml').read_text()
        for key, name in [('relative_config_imu', 'kalibr_imu_chain.yaml'),
                          ('relative_config_imucam', 'kalibr_imucam_chain.yaml')]:
            if re.findall(r'^' + key + r':\s*(\S+)\s*$', settings, re.M) != [name]:
                raise ValueError('OpenVINS linked calibration differs from selected bundle: ' + key)
    return dict(schema=1, algorithm=algorithm, dataset=dataset, sequence=sequence,
                source_sequence=source_sequence, profile=profile, mode='vio',
                source_index_sha256=index['source_index_sha256'],
                candidate_index_sha256=digest(bundle / 'index.json'),
                files=files, diagnostic=diagnostic is not None,
                production_profile_confirmed=False, production_ready=False,
                limitation='Explicit candidate selection; native execution cannot settle recording-specific camera projection.')


def snapshot_profile(record, destination):
    destination = Path(destination)
    # Read and verify all bytes first; a failed selection never leaves a partial
    # usable bundle. Never reuse a directory from a previous attempt.
    loaded = []
    for item in record['files']:
        raw = Path(item['source']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('candidate changed between selection and snapshot')
        loaded.append((item, raw))
    destination.mkdir(exist_ok=False)
    for item, raw in loaded:
        path = destination / item['name']
        path.write_bytes(raw)
        item['loaded_path'] = str(path.resolve())
    (destination / 'selection.json').write_text(json.dumps(record, indent=2) + '\n')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo', type=Path)
    parser.add_argument('algorithm', choices=('basalt', 'voxel_svio', 'openvins'))
    parser.add_argument('dataset')
    parser.add_argument('sequence')
    parser.add_argument('mode', choices=('vio',))
    parser.add_argument('profile', choices=tuple(FILES))
    parser.add_argument('--snapshot-to', type=Path)
    args = parser.parse_args()
    try:
        record = select_profile(args.repo, args.algorithm, args.dataset, args.sequence, args.profile)
        if args.snapshot_to:
            record = snapshot_profile(record, args.snapshot_to)
        print(json.dumps(record, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
