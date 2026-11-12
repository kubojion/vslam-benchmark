"""A listed cell pools across workspace commits only when its estimate receipts are identical."""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_repair_inventory import POOLING, pooled_cohort  # noqa: E402

KEY = 'vio/zed2i/field1_110426_full_10fps_q90/okvis2'


def run(tmp, run_id, commit, binary='aa', parameters=None, algorithm_tree='src-1'):
    d = tmp / 'results' / KEY / f'run{run_id}'
    (d / 'provenance').mkdir(parents=True)
    snapshot = d / 'provenance/implementation.json'
    snapshot.write_text(json.dumps(dict(schema=1, trees=[
        dict(role='workspace', path='.', commit=commit, entries=[commit]),
        dict(role='algorithm', path='src/okvis2', commit='abc', entries=[algorithm_tree])])))
    digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    (d / 'run_meta.json').write_text(json.dumps(dict(provenance=dict(
        implementation_capture=dict(snapshot='provenance/implementation.json', snapshot_sha256=digest)))))
    payload = dict(workspace=dict(commit=commit), implementation_content_sha256=commit,
                   binaries=[dict(role='estimator', path='okvis_app', sha256=binary)],
                   parameters=parameters if parameters is not None else dict(use_imu='true'), machine_id='m')
    return dict(path=f'results/{KEY}/run{run_id}', cohort_fingerprint=commit + binary, cohort_evidence=payload)


def record(tmp, **spec):
    path = tmp / POOLING
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(schema=1, cells={KEY: dict(runs=[10001, 10003, 10004], **spec)})))


def test_pools_when_only_the_workspace_differs(tmp_path):
    record(tmp_path)
    attempts = [run(tmp_path, 10001, 'old'), run(tmp_path, 10003, 'new'), run(tmp_path, 10004, 'new')]
    result = pooled_cohort(tmp_path, KEY, attempts)
    assert result['status'] == 'pooled' and result['workspace_commits'] == ['new', 'old']


def test_refuses_on_any_estimate_receipt_difference(tmp_path):
    record(tmp_path)
    attempts = [run(tmp_path, 10001, 'old', binary='bb'), run(tmp_path, 10003, 'new'), run(tmp_path, 10004, 'new')]
    assert pooled_cohort(tmp_path, KEY, attempts)['status'] == 'refused'


def test_refuses_on_algorithm_source_difference(tmp_path):
    record(tmp_path)
    attempts = [run(tmp_path, 10001, 'old', algorithm_tree='src-0'), run(tmp_path, 10003, 'new'),
                run(tmp_path, 10004, 'new')]
    assert pooled_cohort(tmp_path, KEY, attempts)['status'] == 'refused'


def test_listed_diagnostic_parameter_only_at_its_default(tmp_path):
    record(tmp_path, ignored_parameters=dict(trace=0))
    old = run(tmp_path, 10001, 'old', parameters=dict(use_imu='true'))
    on = run(tmp_path, 10003, 'new', parameters=dict(use_imu='true', trace=1))
    off = run(tmp_path, 10004, 'new', parameters=dict(use_imu='true', trace=0))
    assert pooled_cohort(tmp_path, KEY, [old, on, off])['status'] == 'refused'
    on['cohort_evidence']['parameters']['trace'] = 0
    assert pooled_cohort(tmp_path, KEY, [old, on, off])['status'] == 'pooled'


def test_unlisted_cells_and_other_runs_are_not_pooled(tmp_path):
    record(tmp_path)
    attempts = [run(tmp_path, 10001, 'old'), run(tmp_path, 10003, 'new'), run(tmp_path, 10004, 'new')]
    assert pooled_cohort(tmp_path, KEY.replace('okvis2', 'basalt'), attempts) is None
    assert pooled_cohort(tmp_path, KEY, attempts[:2])['status'] == 'refused'


def test_record_matching_the_selected_runs_applies_when_several_list_the_cell(tmp_path):
    from build_repair_inventory import RULEC_POOLING
    record(tmp_path)  # earlier selection: 10001, 10003, 10004
    later = tmp_path / RULEC_POOLING
    later.write_text(json.dumps(dict(schema=1, cells={KEY: dict(runs=[20001, 20002, 20003])})))
    attempts = [run(tmp_path, 20001, 'old'), run(tmp_path, 20002, 'new'), run(tmp_path, 20003, 'new')]
    result = pooled_cohort(tmp_path, KEY, attempts)
    assert result['status'] == 'pooled' and result['record']['path'] == RULEC_POOLING
    earlier = [run(tmp_path, 10001, 'old'), run(tmp_path, 10003, 'new'), run(tmp_path, 10004, 'new')]
    assert pooled_cohort(tmp_path, KEY, earlier)['record']['path'] == POOLING
    # Only the later record consulted (a reselected cell): the earlier runs are refused, not pooled.
    assert pooled_cohort(tmp_path, KEY, earlier, (RULEC_POOLING,))['status'] == 'refused'


def test_unreached_harness_limit_may_differ_only_after_clean_exits(tmp_path):
    record(tmp_path, unreached_harness_limits=dict(stage_timeout_s='watchdog, never reached'))
    attempts = [run(tmp_path, 10001, 'old', parameters=dict(use_imu='true', stage_timeout_s=7200)),
                run(tmp_path, 10003, 'new', parameters=dict(use_imu='true', stage_timeout_s=43200)),
                run(tmp_path, 10004, 'new', parameters=dict(use_imu='true', stage_timeout_s=7200))]
    for a in attempts:
        a['process'] = dict(exit_code=0)
    assert pooled_cohort(tmp_path, KEY, attempts)['status'] == 'pooled'
    attempts[1]['process'] = dict(exit_code=124)
    assert pooled_cohort(tmp_path, KEY, attempts)['status'] == 'refused'
    record(tmp_path)  # not listed: any difference refuses, as before
    attempts[1]['process'] = dict(exit_code=0)
    assert pooled_cohort(tmp_path, KEY, attempts)['status'] == 'refused'


def pending_record(tmp, accept):
    from build_repair_inventory import RULEC_POOLING
    path = tmp / RULEC_POOLING
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(schema=1, pending_user_decisions=dict(harness_python=dict(accept=accept, disclosure='d')),
        cells={KEY: dict(runs=[20001, 20002, 20003],
                         options_if_accepted=dict(harness_python=dict(ignored_runtime_fields=['python'])))})))


def python_runs(tmp):
    attempts = [run(tmp, 20001, 'old'), run(tmp, 20002, 'new'), run(tmp, 20003, 'new')]
    for a, version in zip(attempts, ('3.10.20', '3.13.5', '3.13.5')):
        a['cohort_evidence']['runtime'] = dict(python=version)
    return attempts


def test_pending_option_is_ignored_until_its_decision_is_accepted(tmp_path):
    attempts = python_runs(tmp_path)
    pending_record(tmp_path, False)
    assert pooled_cohort(tmp_path, KEY, attempts)['status'] == 'refused'
    pending_record(tmp_path, True)
    result = pooled_cohort(tmp_path, KEY, attempts)
    assert result['status'] == 'pooled' and result['accepted_decisions'] == ['harness_python']
    assert result['disclosures'] == ['d']


def test_accepted_option_ignores_only_its_listed_field(tmp_path):
    pending_record(tmp_path, True)
    attempts = python_runs(tmp_path)
    attempts[2]['cohort_evidence']['binaries'][0]['sha256'] = 'other'
    assert pooled_cohort(tmp_path, KEY, attempts)['status'] == 'refused'


def test_option_without_a_decision_entry_is_an_error(tmp_path):
    import pytest
    from build_repair_inventory import RULEC_POOLING
    (tmp_path / RULEC_POOLING).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / RULEC_POOLING).write_text(json.dumps(dict(schema=1, cells={KEY: dict(
        runs=[20001, 20002, 20003], options_if_accepted=dict(other=dict(ignored_runtime_fields=['python'])))})))
    with pytest.raises(ValueError, match='decision'):
        pooled_cohort(tmp_path, KEY, python_runs(tmp_path))
