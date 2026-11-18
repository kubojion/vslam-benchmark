"""The a33 selection layer (alias view -> canonical Sielinko cell), its CSV rows and the a33 pooling switches."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'eval'))
import build_repair_inventory as B  # noqa: E402
import build_benchmark_csv as C  # noqa: E402

KEY = 'vio/zed2i/field1_110426_full_10fps_q90/okvis2'
VIEW = 'vio/zed2i/sielinko_imupilot_full_a33/okvis2'


def repo_with(tmp_path, *, previous=(20001, 20002, 20003), times_equal=True, state_status='evaluated'):
    repo = tmp_path
    for seq, text in (('field1_110426_full_10fps_q90', '1\n2\n'), ('sielinko_imupilot_full_a33', '1\n2\n' if times_equal else '1\n3\n')):
        (repo/'datasets/zed2i'/seq).mkdir(parents=True); (repo/'datasets/zed2i'/seq/'times.txt').write_text(text)
    attempts = {}
    for rep, run_id in enumerate((63003, 64003, 64013), 1):
        state = repo/'results/.attempt-state'/VIEW.replace('/', '__')/f'run{run_id}.json'
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(json.dumps(dict(status=state_status, identity=dict(cohort='c', repetition=1, physical_run_id=run_id))))
        (repo/'results'/VIEW/f'run{run_id}').mkdir(parents=True); (repo/'results'/VIEW/f'run{run_id}'/'run_meta.json').write_text('{}')
        attempts[f'results/{VIEW}/run{run_id}'] = dict(cell=KEY, repetition=rep, run_id=run_id, cohort='c',
                                                     attempt_state=dict(sha256=hashlib.sha256(state.read_bytes()).hexdigest()))
    record = dict(schema=1, alias=dict(dataset='zed2i', view='sielinko_imupilot_full_a33', canonical='field1_110426_full_10fps_q90',
                                       modes=['vio', 'vio-lc']),
                  previous={KEY: list(previous)}, cells={KEY: [63003, 64003, 64013]}, attempts=attempts)
    (repo/B.A33_SELECTION).parent.mkdir(parents=True); (repo/B.A33_SELECTION).write_text(json.dumps(record))
    return repo


def test_alias_attempts_fill_the_canonical_cell_and_supersede_the_previous_selection(tmp_path):
    repo = repo_with(tmp_path)
    paths, superseded, record = B.a33_selections(repo, {KEY: [20001, 20002, 20003]})
    assert paths == {KEY: [f'{VIEW}/run63003', f'{VIEW}/run64003', f'{VIEW}/run64013']}
    assert superseded == {f'{KEY}/run{i}' for i in (20001, 20002, 20003)} and record['path'] == B.A33_SELECTION


@pytest.mark.parametrize('change,message', [(dict(previous=(20004, 20002, 20003)), 'earlier selection differs'),
                                            (dict(times_equal=False), 'times differ'),
                                            (dict(state_status='running'), 'not terminal')])
def test_the_layer_refuses_a_changed_main_view_or_live_attempt(tmp_path, change, message):
    repo = repo_with(tmp_path, **change)
    with pytest.raises(ValueError, match=message):
        B.a33_selections(repo, {KEY: [20001, 20002, 20003]})


def test_a_changed_attempt_state_refuses(tmp_path):
    repo = repo_with(tmp_path)
    state = repo/'results/.attempt-state'/VIEW.replace('/', '__')/'run64003.json'
    state.write_text(state.read_text()+' ')
    with pytest.raises(ValueError, match='attempt state differs'):
        B.a33_selections(repo, {KEY: [20001, 20002, 20003]})


def test_alias_rows_belong_to_the_canonical_cell_and_keep_their_folder(tmp_path):
    attempt = dict(path=f'results/{VIEW}/run63003', exists=True, trajectory_saved=True, process={}, qualification={},
                   sequence_alias=dict(view='sielinko_imupilot_full_a33', canonical='field1_110426_full_10fps_q90'))
    row = C.row_from_attempt(attempt, {}, dict(key=KEY), repo=tmp_path)
    assert row['seq'] == 'field1_110426_full_10fps_q90' and row['run_path'] == f'results/{VIEW}/run63003' and row['run'] == '63003'
    with pytest.raises(ValueError, match='alias'):
        C.row_from_attempt(attempt, {}, dict(key='vio/zed2i/field1_110426_full_10fps_q90/okvis2x'), repo=tmp_path)


def test_ignored_post_run_receipts_count_as_one_configuration():
    attempts = [dict(config_fingerprint='a'), dict(config_fingerprint='b')]
    assert not B.config_consistent(attempts, dict(status='pooled'))
    assert B.config_consistent(attempts, dict(status='pooled', ignored_artifact_roles=['delivery_audit']))
    assert not B.config_consistent(attempts, dict(status='refused', ignored_artifact_roles=['delivery_audit']))
