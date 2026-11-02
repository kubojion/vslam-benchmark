"""Corrected CitrusFarm attempts replace every earlier attempt of their cells, and only if their identity holds."""
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_repair_inventory as inventory

KEY = 'vio/citrusfarm/seq07/okvis2'
COHORT = 'timing-corrected-20261031'


def repo_with(tmp_path, ids=(50001, 50002, 50203), **change):
    (tmp_path/'configs/campaigns').mkdir(parents=True)
    (tmp_path/inventory.CORRECTED_SELECTION).write_text(json.dumps(dict(schema=1, input_variant='corrected', cohorts=[COHORT], cells={KEY: list(ids)})))
    state = tmp_path/'results/.attempt-state'/KEY.replace('/', '__'); state.mkdir(parents=True)
    for repetition, run_id in enumerate(ids, 1):
        identity = dict(cohort=COHORT, repetition=repetition, physical_run_id=run_id, input_variant='corrected', **change)
        (state/f'run{run_id}.json').write_text(json.dumps(dict(status='evaluated', identity=identity)))
    return tmp_path


def test_valid_selection_is_returned(tmp_path):
    assert inventory.corrected_selections(repo_with(tmp_path)) == {KEY: [50001, 50002, 50203]}


def test_absent_selection_changes_nothing(tmp_path):
    assert inventory.corrected_selections(tmp_path) == {}


def test_wrong_input_variant_is_refused(tmp_path):
    repo = repo_with(tmp_path)
    path = repo/'results/.attempt-state'/KEY.replace('/', '__')/'run50001.json'
    value = json.loads(path.read_text()); value['identity']['input_variant'] = 'other'; path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match='identity'):
        inventory.corrected_selections(repo)


def test_live_attempt_is_refused(tmp_path):
    repo = repo_with(tmp_path)
    path = repo/'results/.attempt-state'/KEY.replace('/', '__')/'run50002.json'
    value = json.loads(path.read_text()); value['status'] = 'estimator_starting'; path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match='terminal'):
        inventory.corrected_selections(repo)


def test_older_attempts_are_superseded_and_new_ones_are_not(tmp_path):
    for name in ('run1', 'run3', 'run10002', 'run50001', 'run50201', 'run51001'):
        (tmp_path/'results'/KEY/name).mkdir(parents=True)
    (tmp_path/'results'/KEY/'summary.json').write_text('{}')
    assert inventory.corrected_superseded(tmp_path, KEY) == {f'{KEY}/run1', f'{KEY}/run3', f'{KEY}/run10002'}
