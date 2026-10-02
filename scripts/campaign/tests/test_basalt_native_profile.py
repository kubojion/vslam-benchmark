import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'run'))
from _basalt_native_profile import REVIEW, effective_profile, materialize


def test_effective_profile_preserves_values_and_rejects_unreviewed_keys():
    review = dict(accepted_keys=['loaded'], unsupported_requested_keys=['unsupported'])
    requested = {'value0': {'loaded': 0.005, 'unsupported': 4}}
    assert effective_profile(requested, review) == {'value0': {'loaded': 0.005}}
    assert requested['value0']['unsupported'] == 4
    with pytest.raises(ValueError, match='unknown'):
        effective_profile({'value0': {'loaded': 1, 'new_knob': 2}}, review)
    with pytest.raises(ValueError, match='missing'):
        effective_profile({'value0': {'unsupported': 4}}, review)


def test_native_change_blocks_materialization_and_requested_input_is_preserved(tmp_path):
    binary = tmp_path/'native'; binary.write_bytes(b'inspected build')
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    review = dict(accepted_keys=['loaded'], unsupported_requested_keys=['unsupported'],
        policy='inspection', native_binary={'sha256': digest}, native_library={'sha256': digest})
    path = tmp_path/REVIEW; path.parent.mkdir(parents=True); path.write_text(json.dumps(review))
    requested = tmp_path/'request.json'; requested.write_text('{"value0":{"loaded":0.005,"unsupported":4}}')
    before = requested.read_bytes(); destination = tmp_path/'effective.json'
    record = materialize(tmp_path, requested, destination, binary, binary)
    assert record['omitted_unsupported_settings'] == {'unsupported': 4}
    assert json.loads(destination.read_text())['value0'] == {'loaded': 0.005}
    assert requested.read_bytes() == before
    with pytest.raises(FileExistsError):
        materialize(tmp_path, requested, destination, binary, binary)
    binary.write_bytes(b'changed build')
    with pytest.raises(ValueError, match='runtime changed'):
        materialize(tmp_path, requested, tmp_path/'second.json', binary, binary)
    assert not (tmp_path/'second.json').exists()
