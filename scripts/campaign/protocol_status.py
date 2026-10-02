"""Experimental validity and recorded outcomes are independent of accuracy.

Protocol decisions come from the evidence-pinned ledger, never from an ATE or
coverage threshold. Success here means a clean final export, not accurate/full
tracking; native errors after saving are failures with usable output.
"""
from collections import Counter, defaultdict


def observed_outcome(exists, evaluated, numerical_status, exit_code, native_errors,
                     trajectory_saved=False):
    if not exists:
        return 'not_attempted'
    if numerical_status == 'scale_collapse':
        return 'failure_scale_collapse'
    if numerical_status == 'eval_failed':
        return 'failure_invalid_export'
    if exit_code not in (None, 0) or native_errors:
        return 'failure_with_saved_trajectory' if trajectory_saved else 'failure_without_final_trajectory'
    if exit_code == 0 and evaluated and numerical_status == 'ok':
        return 'success'
    return 'unknown'


def attempt_protocol(attempt):
    q = attempt.get('qualification', {})
    review = q.get('protocol', {})
    outcome = observed_outcome(attempt.get('exists', False), attempt.get('evaluated', False),
        attempt.get('numerical_status'), attempt.get('process', {}).get('exit_code'),
        q.get('native_error_observations'), attempt.get('trajectory_saved', False))
    return dict(protocol_status=review.get('status', 'blocked'),
                protocol_basis=review.get('basis', 'no_explicit_protocol_review'),
                protocol_blockers=review.get('blockers', q.get('blockers', [])),
                attempt_completed=bool(attempt.get('exists') and (
                    attempt.get('process', {}).get('exit_code') is not None
                    or q.get('native_error_observations'))),
                observed_outcome=outcome,
                successful_run=outcome == 'success',
                observed_failure=outcome.startswith('failure_'))


def summarize_protocol(rows, consistent=True):
    """Rows use identical normalized fields in inventory and CSV aggregations."""
    # Re-derive outcome counts from primary CSV facts so a caller's updated exit
    # or numerical outcome cannot leave stale success flags in an aggregation.
    normalized = []
    for row in rows:
        if 'run_status' in row:
            outcome = observed_outcome(row.get('attempt_exists'), row.get('evaluated'),
                row.get('run_status'), row.get('process_exit_code'),
                row.get('native_error_observation_count'), row.get('trajectory_saved'))
            row = dict(row, observed_outcome=outcome,
                       attempt_completed=bool(row.get('attempt_exists') and (
                           row.get('process_exit_code') is not None or row.get('native_error_observation_count'))))
        normalized.append(row)
    rows = normalized
    groups = defaultdict(list)
    for row in rows:
        if row.get('attempt_exists'):
            groups[row.get('cohort') or 'unverified'].append(row)
    statuses = Counter(r.get('protocol_status', 'blocked') for r in rows)
    verified = [r for r in rows if r.get('protocol_status') == 'verified']
    completed = sum(bool(r.get('attempt_completed')) for r in rows)
    n3 = (len(rows) == 3 and len(verified) == 3 and completed == 3
          and consistent and len(groups) == 1 and 'unverified' not in groups
          and not next(iter(groups), '').startswith('unverified:'))
    if statuses['invalid_setup']:
        state = 'invalid_setup'
    elif statuses['blocked'] or any(not r.get('attempt_completed') for r in verified):
        state = 'blocked'
    elif n3:
        state = 'verified_n3'
    elif len(groups) > 1 or not consistent:
        state = 'separate_implementation_cohorts'
    elif verified:
        state = 'verified_missing_repetitions'
    else:
        state = 'not_executed_protocol_unverified'
    cohorts = []
    for name, members in sorted(groups.items()):
        n = sum(r.get('protocol_status') == 'verified' and bool(r.get('attempt_completed')) for r in members)
        cohorts.append(dict(cohort=name, attempts=len(members), verified_completed=n,
            missing_to_n3=max(0, 3-n) if n else None,
            run_paths=[r.get('run_path') for r in members]))
    return dict(protocol_state=state, protocol_verified_n3=n3,
        attempt_count=sum(bool(r.get('attempt_exists')) for r in rows),
        completed_attempt_count=completed,
        evaluated_trajectory_count=sum(bool(r.get('evaluated')) for r in rows),
        successful_run_count=sum(r.get('observed_outcome') == 'success' for r in rows),
        observed_failure_count=sum(str(r.get('observed_outcome', '')).startswith('failure_') for r in rows),
        unknown_outcome_count=sum(r.get('observed_outcome') == 'unknown' for r in rows),
        protocol_verified_attempts=len(verified),
        verified_failure_count=sum(str(r.get('observed_outcome', '')).startswith('failure_') for r in verified),
        missing_attempt_count=sum(not r.get('attempt_exists') for r in rows),
        protocol_status_counts=dict(statuses), protocol_cohorts=cohorts)


def summarize_attempts(attempts, consistent=True):
    return summarize_protocol([dict(attempt_protocol(a), attempt_exists=a.get('exists', False),
        evaluated=a.get('evaluated', False),
        cohort=a.get('cohort_fingerprint') or ('unverified:' + str(a.get('path')) if a.get('exists') else 'not_executed'),
        run_path=a.get('path'))
        for a in attempts], consistent)
