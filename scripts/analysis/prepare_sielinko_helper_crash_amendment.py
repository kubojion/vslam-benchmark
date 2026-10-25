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


def refresh_identities(art, protocol):
    """A committed harness change alters the workspace tree inside every source identity (Rule C precedent:
    re-capture after a scripts change). Old values stay on record in the amendment entry."""
    import _capture_runtime
    prior = dict(source=protocol.get('frozen_source_sha256'), runtime=protocol.get('frozen_runtime_sha256'))
    os.environ.update(protocol['runtime_environment']['voxel_svio'])
    protocol['frozen_source_sha256'] = {s['algorithm']: prepare.source_identity(s['algorithm']) for s in protocol['studies']}
    runtime = {}
    for spec in protocol['studies']:
        identity = _capture_runtime.identity(ROOT, spec['algorithm'])
        if identity['missing']:
            raise RuntimeError(spec['algorithm'] + ' runtime incomplete: ' + '; '.join(identity['missing']))
        runtime[spec['algorithm']] = identity['sha256']
    protocol['frozen_runtime_sha256'] = runtime
    return prior


def archive_collected(art, key, folder):
    """The campaign keeps a top-level copy of every record; collect() refuses a changed one."""
    collected = art / 'attempts' / (key + '.json')
    if collected.is_file():
        os.replace(collected, folder / 'collected-copy.json')
        return evidence_row(folder / 'collected-copy.json')
    return None


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
    collected = archive_collected(art, key, folder)
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
    if collected:
        review['collected_copy'] = collected
    write(folder / 'replacement-review.json', review)
    protocol = load(art / 'protocol.json')
    protocol.setdefault('physical_attempt_revisions', {})[key] = dict(
        revision=revision, record=str(original), record_sha256=prepare.sha(original),
        review=str(folder / 'replacement-review.json'), review_sha256=prepare.sha(folder / 'replacement-review.json'))
    protocol.setdefault('amendments', []).append(dict(
        revision=revision, at=review['reviewed_at'], prior_protocol_sha256=prepare.sha(prior / 'protocol.json'),
        decision=decision, kind='one reviewed helper-crash replacement; no protocol, bound or scoring change'))
    write(art / 'protocol.json', protocol)
    return finish(art, protocol, key, revision, folder, prior)


def amend_supersede(art, key, revision, decision):
    """Supersede a helper-crash replacement that failed before its estimator started."""
    art = Path(art).resolve()
    study = key.split('__')[1]
    worker = art / 'workers' / study
    protocol = load(art / 'protocol.json')
    previous = protocol.get('physical_attempt_revisions', {}).get(key)
    if not previous:
        raise RuntimeError('no earlier revision to supersede: ' + key)
    folder = art / 'amendments' / revision
    if folder.exists():
        raise FileExistsError('amendment already prepared: ' + str(folder))
    if not (art / 'STOP_AFTER_CURRENT').exists():
        raise RuntimeError('the search must be stopped (STOP_AFTER_CURRENT) while amending')
    record_path = worker / 'attempts' / (key + '.json')
    failed = load(record_path)
    run = Path(failed['run'])
    log = worker / 'wrapper-logs' / (key + '__physical_' + previous['revision'] + '.log')
    log_text = log.read_text(errors='replace')
    if (failed.get('state') != 'running' or (failed.get('physical_attempt_revision') or {}).get('revision') != previous['revision']
            or (run / 'run_meta.json').exists() or (run / 'trajectory.txt').exists() or any(run.iterdir())
            or 'source implementation disagrees with reviewed campaign' not in log_text):
        raise RuntimeError('replacement is not a pre-estimation failure: ' + key)
    prior = folder / 'prior'
    prior.mkdir(parents=True)
    for name in ('protocol.json', 'execution-identity.json', 'readiness.json', 'activation.json'):
        if (art / name).is_file():
            shutil.copy2(art / name, prior / name)
    superseded_record = folder / ('superseded-' + previous['revision'] + '.json')
    os.replace(record_path, superseded_record)
    collected = archive_collected(art, key, folder)
    original = folder / 'original-attempt.json'
    shutil.copy2(previous['record'], original)
    old_review = load(previous['review'])
    review = dict(old_review, revision=revision, reviewed_at=datetime.now(timezone.utc).isoformat(), decision=decision,
                  replacement_count=old_review.get('replacement_count', 1) + 1,
                  original_record_sha256=prepare.sha(original),
                  superseded_replacements=old_review.get('superseded_replacements', []) + [dict(
                      revision=previous['revision'], run=str(run), record_sha256=prepare.sha(superseded_record),
                      estimator_started=False, wrapper_log=evidence_row(log),
                      cause=('pre-estimation implementation capture refused: the harness commit changed the workspace '
                             'source identity and the amendment had not refreshed frozen_source_sha256'))],
                  prior_review=evidence_row(previous['review']))
    if collected:
        review['collected_copy'] = collected
    write(folder / 'replacement-review.json', review)
    identities = refresh_identities(art, protocol)
    protocol['physical_attempt_revisions'][key] = dict(
        revision=revision, record=str(original), record_sha256=prepare.sha(original),
        review=str(folder / 'replacement-review.json'), review_sha256=prepare.sha(folder / 'replacement-review.json'))
    protocol.setdefault('amendments', []).append(dict(
        revision=revision, at=review['reviewed_at'], prior_protocol_sha256=prepare.sha(prior / 'protocol.json'),
        decision=decision, supersedes=previous['revision'], prior_frozen_identities=identities,
        kind='supersede a never-started replacement; refresh source/runtime identities after the harness commit'))
    write(art / 'protocol.json', protocol)
    return finish(art, protocol, key, revision, folder, prior)


def finish(art, protocol, key, revision, folder, prior):
    files = [dict(path=p, sha256=prepare.sha(ROOT / p)) for p in prepare.git('ls-files', '--', 'scripts', 'configs').split('\n')
             if p and (ROOT / p).is_file()]
    identity = dict(schema=1, worktree_head=prepare.git('rev-parse', 'HEAD').strip(),
                    boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                    protocol_sha256=prepare.sha(art / 'protocol.json'),
                    controller_environment=policy.controller_environment(), files=files)
    write(art / 'execution-identity.json', identity)
    readiness = load(art / 'readiness.json')
    readiness['evidence'] = [e for e in readiness['evidence'] if not e['path'].endswith('/main-integrity.json')]
    readiness.update(protocol_sha256=prepare.sha(art / 'protocol.json'),
                     execution_manifest_sha256=prepare.sha(art / 'execution-identity.json'))
    readiness.setdefault('amendments', []).append(dict(
        revision=revision, prior_readiness_sha256=prepare.sha(prior / 'readiness.json'),
        note='check-clip evidence unchanged; identities re-hashed for the reviewed replacement'))
    write(art / 'readiness.json', readiness)
    if (art / 'activation.json').is_file():
        (art / 'activation.json').unlink()
    for directory in sorted((art / 'workers').iterdir()):
        for name in ('protocol.json', 'execution-identity.json'):
            if (directory / name).is_file():
                (directory / name).write_bytes((art / name).read_bytes())
    campaign.verify_activation(art, protocol)
    item = policy.reviewed_attempt_revision(protocol, key)
    if item is None or item['revision'] != revision:
        raise RuntimeError('reviewed revision not admitted')
    execution.configure(art, protocol, None)
    execution.verify_frozen()
    _, run_id, _ = execution.identities(key.split('__')[1], key.split('__')[2], key.split('__')[3], key.split('__')[4],
                                        int(key.split('__')[5].removeprefix('rep')), key.split('__')[0])
    summary = dict(passed=True, at=datetime.now(timezone.utc).isoformat(), key=key, revision=revision, new_run_id=run_id,
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
    parser.add_argument('--supersede', action='store_true', help='supersede a never-started replacement of this key')
    args = parser.parse_args()
    run = amend_supersede if args.supersede else amend
    print(json.dumps(run(args.art, args.key, args.revision, args.decision), indent=2))


if __name__ == '__main__':
    main()
