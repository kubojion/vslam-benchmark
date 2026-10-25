#!/usr/bin/env python3
"""Replace one Sielinko search attempt whose post-native provenance helper crashed; never launch.

The native estimator finished cleanly, but _enrich_run_meta segfaulted, leaving the attempt
incomplete ("running"). The original record and its evidence are archived, an explicit
helper-crash review is written, and the protocol gains one physical_attempt_revisions entry,
so the same logical candidate and repetition run again under a new physical run ID.
Execution identity and readiness are re-hashed (priors kept); activation is recreated on resume.
Usage: prepare_sielinko_helper_crash_amendment.py --art DIR --key KEY --revision REV --decision TEXT
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts/analysis'), str(ROOT / 'scripts/run')]
import prepare_sielinko_search as prepare  # noqa: E402
import noise_campaign as campaign  # noqa: E402
import noise_campaign_engine as execution  # noqa: E402
import noise_execution_policy as policy  # noqa: E402

IDENTITY_FIELDS = ('key', 'campaign_id', 'study', 'phase', 'label', 'params', 'sequence', 'mode', 'repetition', 'native_seed')


def load(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(prepare.json_text(value))


def evidence_row(path):
    return dict(path=str(path), sha256=prepare.sha(path))


def amend(art, key, revision, decision):
    art = Path(art).resolve()
    study = key.split('__')[1]
    worker = art / 'workers' / study
    record_path = worker / 'attempts' / (key + '.json')
    folder = art / 'amendments' / revision
    if folder.exists():
        raise FileExistsError('amendment already prepared: ' + str(folder))
    record = load(record_path)
    run = Path(record['run'])
    log = worker / 'wrapper-logs' / (key + '.log')
    log_text = log.read_text(errors='replace')
    run_log = (run / 'run_log.txt').read_text(errors='replace')
    meta = load(run / 'run_meta.json')
    if (record.get('key') != key or record.get('state') != 'running' or 'returncode' in record or 'result' in record
            or 'Segmentation fault' not in log_text or '_enrich_run_meta.py' not in log_text
            or 'Finished!' not in run_log or not (run / 'trajectory.txt').is_file()
            or 'provenance_schema' in meta):
        raise RuntimeError('attempt is not an incomplete post-native helper crash: ' + key)
    if (art / 'STOP_AFTER_CURRENT').exists() is False:
        raise RuntimeError('the search must be stopped (STOP_AFTER_CURRENT) while amending')
    prior = folder / 'prior'
    prior.mkdir(parents=True)
    for name in ('protocol.json', 'execution-identity.json', 'readiness.json', 'activation.json'):
        if (art / name).is_file():
            shutil.copy2(art / name, prior / name)
    original = folder / 'original-attempt.json'
    os.replace(record_path, original)
    review = dict(
        classification='post_native_helper_crash', revision=revision, helper_crash_attempts=[key],
        native_finished=True, scientific_score=None, optimizer_feedback=False, replacement_count=1,
        original_record_sha256=prepare.sha(original),
        logical_identity={k: record.get(k) for k in IDENTITY_FIELDS},
        original_run=str(run), decision=decision, reviewed_at=datetime.now(timezone.utc).isoformat(),
        evidence=dict(wrapper_log=evidence_row(log), run_log=evidence_row(run / 'run_log.txt'),
                      trajectory=evidence_row(run / 'trajectory.txt'), run_meta=evidence_row(run / 'run_meta.json')),
        note=('Native estimator finished ("Finished!") and exported its trajectory; the system-Python provenance helper '
              '(_enrich_run_meta) segfaulted, so the attempt never completed. No score is taken from it; the same '
              'candidate and repetition run again under a new physical run ID.'))
    write(folder / 'replacement-review.json', review)
    protocol = load(art / 'protocol.json')
    protocol.setdefault('physical_attempt_revisions', {})[key] = dict(
        revision=revision, record=str(original), record_sha256=prepare.sha(original),
        review=str(folder / 'replacement-review.json'), review_sha256=prepare.sha(folder / 'replacement-review.json'))
    protocol.setdefault('amendments', []).append(dict(
        revision=revision, at=review['reviewed_at'], prior_protocol_sha256=prepare.sha(prior / 'protocol.json'),
        decision=decision, kind='one reviewed helper-crash replacement; no protocol, bound or scoring change'))
    write(art / 'protocol.json', protocol)
    files = [dict(path=p, sha256=prepare.sha(ROOT / p)) for p in prepare.git('ls-files', '--', 'scripts', 'configs').split('\n')
             if p and (ROOT / p).is_file()]
    identity = dict(schema=1, worktree_head=prepare.git('rev-parse', 'HEAD').strip(),
                    boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                    protocol_sha256=prepare.sha(art / 'protocol.json'),
                    controller_environment=policy.controller_environment(), files=files)
    write(art / 'execution-identity.json', identity)
    readiness = load(art / 'readiness.json')
    readiness.update(protocol_sha256=prepare.sha(art / 'protocol.json'),
                     execution_manifest_sha256=prepare.sha(art / 'execution-identity.json'))
    readiness.setdefault('amendments', []).append(dict(
        revision=revision, prior_readiness_sha256=prepare.sha(prior / 'readiness.json'),
        note='check-clip evidence unchanged; identity re-hashed for the helper retry and one reviewed replacement'))
    write(art / 'readiness.json', readiness)
    if (art / 'activation.json').is_file():
        (art / 'activation.json').unlink()
    for directory in sorted((art / 'workers').iterdir()):
        for name in ('protocol.json', 'execution-identity.json'):
            if (directory / name).is_file():
                (directory / name).write_bytes((art / name).read_bytes())
    # Verify as the coordinator will on resume.
    campaign.verify_activation(art, protocol)
    item = policy.reviewed_attempt_revision(protocol, key)
    if item is None or item['revision'] != revision:
        raise RuntimeError('reviewed revision not admitted')
    execution.configure(art, protocol, None)
    execution.verify_frozen()
    summary = dict(passed=True, at=datetime.now(timezone.utc).isoformat(), key=key, revision=revision,
                   protocol_sha256=prepare.sha(art / 'protocol.json'),
                   execution_manifest_sha256=prepare.sha(art / 'execution-identity.json'),
                   readiness_sha256=prepare.sha(art / 'readiness.json'))
    write(folder / 'prepared-review.json', summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--art', required=True, type=Path)
    parser.add_argument('--key', required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--decision', required=True)
    args = parser.parse_args()
    print(json.dumps(amend(args.art, args.key, args.revision, args.decision), indent=2))


if __name__ == '__main__':
    main()
