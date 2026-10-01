"""Replay explicit, evidence-pinned claim decisions; never infer acceptance from ATE."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from functools import lru_cache
from pathlib import Path

LEDGER = 'docs/campaigns/paper-acceptance-20261001.json'
DOCUMENT = 'docs/paper-acceptance-20261001.md'
USABLE = {'accepted', 'accepted_with_limitation', 'valid_observed_failure'}


@lru_cache(maxsize=32)
def _read_ledger(path, mtime, size):
    return json.loads(Path(path).read_text())


@lru_cache(maxsize=16384)
def _hash_file(path, mtime, size):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def numerical_digest(evaluation):
    value = {k: v for k, v in evaluation.items()
             if k not in ('qualification', 'qualification_provenance')}
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


def reviewed_decision(repo, relative, meta, evaluation, findings, snapshots, exists):
    path = repo / LEDGER
    if not path.is_file():
        return None
    stat = path.stat()
    ledger = _read_ledger(str(path), stat.st_mtime_ns, stat.st_size)
    record = ledger.get('attempts', {}).get(relative)
    if record is None:
        return None
    errors = []
    if bool(exists) != record['exists']:
        errors.append('attempt_presence_changed_since_claim_review')
    if numerical_digest(evaluation) != record['evaluation_sha256']:
        errors.append('numerical_evidence_changed_since_claim_review')
    # Check original evidence directly as well as the evaluation signature. This
    # catches changed logs/configs even when old evaluation bytes remain in place.
    for item in record['evidence'] + ledger['supporting_evidence']:
        file = repo / item['path']
        stat = file.stat() if file.is_file() else None
        if stat is None or _hash_file(str(file), stat.st_mtime_ns, stat.st_size) != item['sha256']:
            errors.append('reviewed_evidence_changed:' + item['path'])
    if findings and record['status'] in USABLE:
        errors.append('confirmed_estimator_defect_prevents_acceptance')
    if record['status'] in USABLE and (not snapshots or any(not s['verified'] for s in snapshots)):
        errors.append('reviewed_configuration_no_longer_verified')
    if errors:
        return dict(status='blocked', blockers=sorted(set(errors)), claim_limits=[],
                    reuse_qualified=False, paper_usable=False, accuracy_eligible=False,
                    review='explicit_claim_review_stale', rerun_decision='resolve_changed_evidence_first')
    return dict(status=record['status'], blockers=record['blockers'],
                claim_limits=record['claim_limits'], disclosures=record['disclosures'],
                native_error_observations=record.get('native_error_observations', []),
                claim=record['claim'], review='explicit_claim_review',
                decision_path=LEDGER, review_document=DOCUMENT,
                reuse_qualified=record['status'] in USABLE,
                paper_usable=record['status'] in USABLE,
                accuracy_eligible=record['status'] in ('accepted', 'accepted_with_limitation'),
                rerun_decision='confirmed_estimator_side_defect' if record['status']=='rerun_required'
                    else 'not_requested_by_evidence_gap_preserve_and_resolve_first')


def cell_acceptance(attempts, consistent=True):
    counts = Counter(a.get('qualification', {}).get('status', 'blocked') for a in attempts)
    missing = counts['not_executed']
    clean = (len(attempts) == 3 and consistent and counts['accepted'] == 3 and all(
        a.get('numerical_status') == 'ok' and a.get('process', {}).get('exit_code') == 0
        and not a.get('qualification', {}).get('native_error_observations')
        and isinstance(a.get('coverage', {}).get('coverage_gap_pct'), (int, float))
        and a['coverage']['coverage_gap_pct'] >= 95 for a in attempts))
    if counts['rerun_required']:
        status = 'rerun_required'
    elif counts['blocked'] or not consistent:
        status = 'blocked'
    elif missing:
        status = 'missing_repetitions'
    elif counts['valid_observed_failure']:
        status = 'valid_observed_failure'
    elif counts['accepted_with_limitation']:
        status = 'accepted_with_limitation'
    else:
        status = 'accepted' if clean else 'blocked'
    return dict(status=status, attempts=dict(counts), clean_qualified_n3=clean,
                paper_usable_attempts=sum(counts[s] for s in USABLE),
                missing_repetitions=missing, verified_ready_to_run=False)
