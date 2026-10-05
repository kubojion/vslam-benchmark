"""A later batch's finished attempts are selected regardless of outcome, nothing else."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_repair_inventory import BATCH_SELECTIONS, completed_batch_selections

KEY = 'vio/zed2i/field1_110426_full_10fps_q90/'


def write(root, name, value):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))
    return dict(path=name, sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def fixture(root, state_status='evaluated_failure_or_review'):
    """okvis2 r2/r3 in this batch (r1 carried from batch 1); openvins r1-r3 in this batch."""
    plan = {'okvis2': [(2, 10003), (3, 10004)], 'openvins': [(1, 10001), (2, 10002), (3, 10003)]}
    actions, attempts, completed = [], [], []
    for algo, reps in plan.items():
        for repetition, run_id in reps:
            key = KEY + algo
            action = dict(id=f'{key}/default/r{repetition}', cell=key, repetition=repetition,
                          planned_output=f'results/{key}/run{run_id}', cohort='zed-current-n3-' + algo)
            actions.append(action)
            attempts.append(dict(id=action['id'], status='finished', output=f'/srv/repo/{action["planned_output"]}'))
            state = write(root, f'results/.attempt-state/{key.replace("/", "__")}/run{run_id}.json',
                          dict(status=state_status, identity=dict(cohort=action['cohort'], repetition=repetition,
                                                                  physical_run_id=run_id)))
            completed.append(dict(cell=key, repetition=repetition, physical_run_id=run_id, action_id=action['id'],
                                  path=action['planned_output'], attempt_state=state))
    value = dict(schema=1, source_manifest=write(root, 'frozen.json', dict(actions=actions)),
                 batch_status=write(root, 'status.json', dict(attempts=attempts)),
                 cells={KEY + 'okvis2': [10001, 10003, 10004], KEY + 'openvins': [10001, 10002, 10003]},
                 completed=completed)
    write(root, BATCH_SELECTIONS[0], value)
    return value


EARLIER = {KEY + 'okvis2': [10001, 2, 3]}


@pytest.mark.parametrize('state_status', ['evaluated', 'evaluated_failure_or_review', 'no_trajectory'])
def test_finished_attempts_are_selected_with_the_carried_first_repetition(tmp_path, state_status):
    value = fixture(tmp_path, state_status)
    assert completed_batch_selections(tmp_path, EARLIER) == value['cells']


def test_a_live_attempt_is_refused(tmp_path):
    fixture(tmp_path, state_status='running')
    with pytest.raises(ValueError, match='not terminal'):
        completed_batch_selections(tmp_path, EARLIER)


def test_carried_repetition_must_be_the_earlier_selection(tmp_path):
    fixture(tmp_path)
    with pytest.raises(ValueError, match='neither in this batch'):
        completed_batch_selections(tmp_path, {KEY + 'okvis2': [1, 2, 3]})


def test_changed_status_or_plan_evidence_is_refused(tmp_path):
    fixture(tmp_path)
    (tmp_path / 'status.json').write_text('{"attempts": []}')
    with pytest.raises(ValueError, match='stale'):
        completed_batch_selections(tmp_path, EARLIER)


def test_absent_record_selects_nothing(tmp_path):
    assert completed_batch_selections(tmp_path, EARLIER) == {}


def executor_fixture(root, plan_hash=None):
    """A run_future_manifest batch that ran only r1 of a cell; r2/r3 keep their default slots."""
    key = 'vo/citrusfarm/seq04/okvis2'
    action = dict(id=f'{key}/default/r1', cell=key, repetition=1, planned_output=f'results/{key}/run10001',
                  cohort='repair-n3-okvis2')
    frozen = write(root, 'frozen-plan.json', dict(actions=[action]))
    state = write(root, f'results/.attempt-state/{key.replace("/", "__")}/run10001.json',
                  dict(status='evaluated', identity=dict(cohort=action['cohort'], repetition=1, physical_run_id=10001)))
    executor = write(root, 'executor-state.json', dict(manifest_sha256=plan_hash or frozen['sha256'],
                                                      actions={action['id']: dict(status='evaluated', exit_code=0)}))
    value = dict(schema=1, source_manifest=frozen, batch_status=executor, cells={key: [10001, 2, 3]},
                 completed=[dict(cell=key, repetition=1, physical_run_id=10001, action_id=action['id'],
                                 path=action['planned_output'], attempt_state=state)])
    write(root, BATCH_SELECTIONS[1], value)
    return value


def test_executor_state_batch_keeps_default_slots_for_repetitions_it_did_not_run(tmp_path):
    value = executor_fixture(tmp_path)
    labels = {}
    assert completed_batch_selections(tmp_path, {}, labels) == value['cells']
    assert labels == {'vo/citrusfarm/seq04/okvis2': 'production_20261004'}


def test_executor_state_of_another_plan_revision_is_refused(tmp_path):
    executor_fixture(tmp_path, plan_hash='0' * 64)
    with pytest.raises(ValueError, match='another plan revision'):
        completed_batch_selections(tmp_path, {})
