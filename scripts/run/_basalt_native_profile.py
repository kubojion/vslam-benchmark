#!/usr/bin/env python3
"""Make Basalt's requested/effective settings explicit for the inspected release."""
import argparse
import hashlib
import json
from pathlib import Path

REVIEW = 'docs/campaigns/basalt-native-profile-20261002.json'


def effective_profile(document, review):
    values = document['value0']
    accepted = set(review['accepted_keys'])
    omitted = set(review['unsupported_requested_keys'])
    unknown, missing = set(values)-accepted-omitted, accepted-set(values)
    if unknown or missing:
        raise ValueError(f'unreviewed Basalt settings: unknown={sorted(unknown)}, missing={sorted(missing)}')
    return {'value0': {key: value for key, value in values.items() if key in accepted}}


def materialize(repo, requested, destination, binary, library):
    repo, requested, destination = map(Path, (repo, requested, destination))
    review = json.loads((repo/REVIEW).read_text())
    for role, path in (('native_binary', binary), ('native_library', library)):
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != review[role]['sha256']:
            raise ValueError('Basalt runtime changed; repeat native settings inspection: '+role)
    original = json.loads(requested.read_text())
    effective = effective_profile(original, review)
    with destination.open('x') as stream:
        stream.write(json.dumps(effective, indent=2)+'\n')
    return dict(policy=review['policy'], requested_path=str(requested),
        requested_sha256=hashlib.sha256(requested.read_bytes()).hexdigest(),
        effective_path=str(destination),
        effective_sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
        omitted_unsupported_settings={key: value for key, value in original['value0'].items()
                                      if key not in effective['value0']},
        native_review=REVIEW, native_binary=review['native_binary'], native_library=review['native_library'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repo', 'requested', 'destination', 'binary', 'library'):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    print(json.dumps(materialize(**vars(args)), indent=2))
