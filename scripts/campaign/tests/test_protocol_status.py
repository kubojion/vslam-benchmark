from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from protocol_status import attempt_protocol, summarize_attempts, summarize_protocol


def attempt(**changes):
    return dict(exists=True, evaluated=True, trajectory_saved=True, numerical_status='ok',
        process={'exit_code': 0}, cohort_fingerprint='same',
        qualification={'protocol': {'status': 'verified'}}) | changes


def test_missing_is_not_failed_and_failure_does_not_demand_success_resampling():
    good = attempt()
    failed = dict(good, evaluated=False, trajectory_saved=False, numerical_status=None,
                  process={'exit_code': 139})
    result = summarize_attempts([good, good, failed])
    assert result['protocol_verified_n3']
    assert (result['attempt_count'], result['evaluated_trajectory_count'],
            result['successful_run_count'], result['verified_failure_count']) == (3, 2, 2, 1)
    missing = dict(failed, exists=False, qualification={'protocol': {'status': 'not_executed'}})
    result = summarize_attempts([good, good, missing])
    assert result['protocol_state'] == 'verified_missing_repetitions'
    assert result['missing_attempt_count'] == 1 and result['observed_failure_count'] == 0


def test_native_error_overrides_wrapper_zero_and_preserves_saved_accuracy_scope():
    a = attempt(coverage={'coverage_gap_pct': 20})
    a['qualification']['native_error_observations'] = [{'text': 'native terminate'}]
    p = attempt_protocol(a)
    assert p['protocol_status'] == 'verified'
    assert p['observed_outcome'] == 'failure_with_saved_trajectory'
    assert p['attempt_completed'] and not p['successful_run']


def test_reviewed_complete_export_shutdown_remains_failure_and_never_clean():
    a = attempt()
    a['qualification'].update(native_error_observations=[{'text': 'native terminate'}],
        export_review={'export_completion': 'complete', 'shutdown_error': True,
                       'label': 'completed export; shutdown error'})
    outcome = attempt_protocol(a)
    assert outcome['observed_outcome'] == 'completed_export_shutdown_error'
    assert outcome['observed_failure'] and not outcome['successful_run']
    result = summarize_attempts([a, a, a])
    assert result['protocol_verified_n3']
    assert (result['attempt_count'], result['evaluated_trajectory_count'],
            result['successful_run_count'], result['observed_failure_count']) == (3, 3, 0, 3)
    assert result['completed_export_shutdown_error_count'] == 3
    a['numerical_status'] = 'scale_collapse'
    assert attempt_protocol(a)['observed_outcome'] == 'failure_scale_collapse'
    a['numerical_status'] = 'ok'
    a['qualification']['export_review']['export_completion'] = 'partial'
    assert attempt_protocol(a)['observed_outcome'] == 'failure_with_saved_trajectory'


def test_distinct_implementations_remain_one_plus_two_and_unknown_is_not_completion():
    old = attempt()
    patched = dict(old, cohort_fingerprint='patched')
    result = summarize_attempts([old, patched, patched])
    assert result['protocol_state'] == 'separate_implementation_cohorts'
    assert not result['protocol_verified_n3']
    assert sorted(g['verified_completed'] for g in result['protocol_cohorts']) == [1, 2]
    assert sorted(g['missing_to_n3'] for g in result['protocol_cohorts']) == [1, 2]
    unknown = dict(old, process={'exit_code': None})
    assert summarize_attempts([old, old, unknown])['unknown_outcome_count'] == 1
    assert not summarize_attempts([old, old, unknown])['protocol_verified_n3']
    assert summarize_attempts([old, old, unknown])['protocol_state'] == 'blocked'
    invalid = dict(unknown, numerical_status='scale_collapse')
    assert attempt_protocol(invalid)['observed_failure']
    assert not attempt_protocol(invalid)['attempt_completed']


def test_calibration_blocked_failure_does_not_become_verified_from_failed_outcome():
    a = attempt(numerical_status='scale_collapse')
    a['qualification']['protocol']['status'] = 'blocked'
    result = summarize_attempts([a, a, a])
    assert result['observed_failure_count'] == 3
    assert result['verified_failure_count'] == 0 and not result['protocol_verified_n3']
    a['qualification']['protocol']['status'] = 'invalid_setup'
    assert summarize_attempts([a])['protocol_state'] == 'invalid_setup'


def test_unidentified_implementations_are_not_pooled_and_match_csv_identity():
    a = dict(attempt(), cohort_fingerprint=None, path='results/vo/test/seq/algorithm/run1')
    b = dict(a, path='results/vo/test/seq/algorithm/run2')
    result = summarize_attempts([a, b])
    assert [g['cohort'] for g in result['protocol_cohorts']] == [
        'unverified:' + a['path'], 'unverified:' + b['path']]
    assert not result['protocol_verified_n3']
