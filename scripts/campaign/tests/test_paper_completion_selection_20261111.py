"""The paper completion record replaces only the selection it was made against, with checked attempts."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_repair_inventory as inventory

KEY = 'vio/rosariov2/sequence1/basalt'
CLOSED = 'vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x'
COHORT = 'repair-n3-test'


def state(repo, key, run_id, repetition, status='evaluated', cohort=COHORT):
    path = inventory.attempt_state_path(repo, key, run_id); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(status=status, identity=dict(cohort=cohort, repetition=repetition, physical_run_id=run_id))))
    (repo/'results'/key/f'run{run_id}').mkdir(parents=True, exist_ok=True)
    return path


def write(repo, **value):
    record = dict(schema=1, previous={KEY: [10001, 10002, 10003]}, cells={KEY: [10001, 10005, 10006]},
                  attempts={f'{KEY}/run10005': dict(repetition=2, cohort=COHORT), f'{KEY}/run10006': dict(repetition=3, cohort=COHORT)})
    record.update(value)
    path = repo/inventory.PAPER_COMPLETION_SELECTION; path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record))


def repo_with(tmp_path):
    for run_id, repetition in ((10005, 2), (10006, 3)):
        state(tmp_path, KEY, run_id, repetition)
    write(tmp_path)
    return tmp_path


LOWER = {KEY: [10001, 10002, 10003]}


def test_absent_record_changes_nothing(tmp_path):
    assert inventory.paper_completion_selections(tmp_path, LOWER) == ({}, set(), {})


def test_replaces_previous_attempts_and_supersedes_them(tmp_path):
    cells, superseded, closed = inventory.paper_completion_selections(repo_with(tmp_path), LOWER)
    assert cells == {KEY: [10001, 10005, 10006]}
    assert superseded == {f'{KEY}/run10002', f'{KEY}/run10003'} and closed == {}


def test_record_made_against_another_main_is_refused(tmp_path):
    with pytest.raises(ValueError, match='earlier selection differs'):
        inventory.paper_completion_selections(repo_with(tmp_path), {KEY: [1, 2, 3]})


def test_unlisted_lower_cell_defaults_to_first_slots(tmp_path):
    repo = repo_with(tmp_path); write(repo, previous={KEY: [1, 2, 3]}, cells={KEY: [1, 10005, 10006]})
    cells, superseded, _ = inventory.paper_completion_selections(repo, {})
    assert cells == {KEY: [1, 10005, 10006]} and superseded == {f'{KEY}/run2', f'{KEY}/run3'}


def test_corrected_cell_cannot_be_changed(tmp_path):
    with pytest.raises(ValueError, match='corrected'):
        inventory.paper_completion_selections(repo_with(tmp_path), LOWER, corrected={KEY})


def test_identity_must_match_the_record(tmp_path):
    repo = repo_with(tmp_path); state(repo, KEY, 10006, 3, cohort='other')
    with pytest.raises(ValueError, match='identity'):
        inventory.paper_completion_selections(repo, LOWER)


def test_reviewed_identity_exception_is_exact(tmp_path):
    repo = repo_with(tmp_path); state(repo, KEY, 10006, 1, cohort='comparison')
    recorded = dict(cohort='comparison', repetition=1, physical_run_id=10006)
    write(repo, identity_exceptions={f'{KEY}/run10006': dict(recorded_identity=recorded)})
    assert inventory.paper_completion_selections(repo, LOWER)[0] == {KEY: [10001, 10005, 10006]}
    write(repo, identity_exceptions={f'{KEY}/run10006': dict(recorded_identity=dict(recorded, repetition=2))})
    with pytest.raises(ValueError, match='identity'):
        inventory.paper_completion_selections(repo, LOWER)


def test_live_attempt_is_refused(tmp_path):
    repo = repo_with(tmp_path); state(repo, KEY, 10006, 3, status='estimator_starting')
    with pytest.raises(ValueError, match='terminal'):
        inventory.paper_completion_selections(repo, LOWER)


def test_unrecorded_attempt_is_refused(tmp_path):
    repo = repo_with(tmp_path); write(repo, attempts={f'{KEY}/run10005': dict(repetition=2, cohort=COHORT)})
    with pytest.raises(ValueError, match='not recorded'):
        inventory.paper_completion_selections(repo, LOWER)


def closed_repo(tmp_path, status='estimator_starting'):
    path = state(tmp_path, CLOSED, 10001, 1, status=status)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    (tmp_path/'results'/CLOSED/'run1').mkdir(parents=True)
    write(tmp_path, previous={CLOSED: [1, 2, 3]}, cells={CLOSED: [10001, 2, 3]},
          attempts={f'{CLOSED}/run10001': dict(repetition=1, cohort=COHORT)},
          closed_cells={CLOSED: dict(disposition='did_not_finish', open_attempts={
              f'{CLOSED}/run10001': dict(status='estimator_starting', attempt_state_sha256=digest)})})
    return tmp_path, path


def test_closed_cell_keeps_its_one_pinned_attempt_and_never_run_slots(tmp_path):
    repo, _ = closed_repo(tmp_path)
    cells, superseded, closed = inventory.paper_completion_selections(repo, {})
    assert cells == {CLOSED: [10001, 2, 3]} and superseded == {f'{CLOSED}/run1'}
    assert closed[CLOSED]['disposition'] == 'did_not_finish'


def test_closed_cell_attempt_that_changed_is_refused(tmp_path):
    repo, path = closed_repo(tmp_path)
    value = json.loads(path.read_text()); value['events'] = [{}]; path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match='terminal'):
        inventory.paper_completion_selections(repo, {})


def test_closed_cell_default_slot_that_ran_is_refused(tmp_path):
    repo, _ = closed_repo(tmp_path); (repo/'results'/CLOSED/'run2').mkdir()
    with pytest.raises(ValueError, match='default slot that was run'):
        inventory.paper_completion_selections(repo, {})


def test_open_attempt_outside_a_closed_cell_is_refused(tmp_path):
    repo, _ = closed_repo(tmp_path)
    value = json.loads((repo/inventory.PAPER_COMPLETION_SELECTION).read_text()); value['closed_cells'] = {}
    (repo/inventory.PAPER_COMPLETION_SELECTION).write_text(json.dumps(value))
    with pytest.raises(ValueError, match='terminal|not recorded'):
        inventory.paper_completion_selections(repo, {})


def test_unknown_disposition_is_refused(tmp_path):
    repo, _ = closed_repo(tmp_path)
    value = json.loads((repo/inventory.PAPER_COMPLETION_SELECTION).read_text())
    value['closed_cells'][CLOSED]['disposition'] = 'predicted'
    (repo/inventory.PAPER_COMPLETION_SELECTION).write_text(json.dumps(value))
    with pytest.raises(ValueError, match='disposition'):
        inventory.paper_completion_selections(repo, {})
