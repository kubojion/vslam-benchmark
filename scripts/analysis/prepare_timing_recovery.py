#!/usr/bin/env python3
"""Recover the stopped CitrusFarm noise search into a new artifact directory; never launches anything.

User decision of 4 Nov 2026, after run 70445 stopped the search: the system-Python helper _capture_inputs.py
segfaulted (exit 139) inside prepare_fresh_run_dir, before the estimator started.

    review     write the reviewed replacement of that attempt (one new run ID of the same fold block)
    freeze     freeze the protocol into --new, admitting exactly the run IDs of --old's attempt records
    carry      copy --old's finished records, ledgers, study records, complete-fold files and budget into --new
    readiness  write --new's CitrusFarm readiness from --old's, with the recovery reason and new evidence
    verify     activation, order, and a dry replay on a scratch copy: cached records, the new ID, the folds

--old is never written. Usage: prepare_timing_recovery.py STEP --old DIR --new DIR --recovery DIR [--scratch DIR]
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts/analysis'), str(ROOT / 'scripts/run')]
import prepare_timing_search as prepare  # noqa: E402

DATASET = 'citrusfarm'
STUDY = 'orbslam3_citrusfarm__tune_seq04'
KEY = 'full__' + STUDY + '__motion__seq04__vio__rep1'
REVISION = 'capture-inputs-segv-20261104'
DECISION = ('User, 4 Nov 2026: run 70445 is an infrastructure failure (system-Python helper _capture_inputs.py '
            'segfaulted, exit 139, inside prepare_fresh_run_dir, before the estimator started); replace it once with '
            'a new run ID from the same fold block. Fix the lane sampler (import time). An attempt that fails before '
            'its estimator starts gets one automatic replacement. Re-freeze into a new artifact directory, reusing '
            'every finished attempt.')
IDENTITY_FIELDS = ('key', 'campaign_id', 'study', 'phase', 'label', 'params', 'sequence', 'mode', 'repetition', 'native_seed')


def load(path):
    return json.loads(Path(path).read_text())


def write_new(path, value):
    path = Path(path)
    if path.exists():
        raise FileExistsError('refusing to overwrite: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(prepare.json_text(value))


def row(path):
    return dict(path=str(path), sha256=prepare.sha(path))


def now():
    return datetime.now(timezone.utc).isoformat()


def failed_attempt(old):
    study = STUDY
    record_path = old / 'workers' / study / 'attempts' / (KEY + '.json')
    record = load(record_path)
    log = old / 'workers' / study / 'wrapper-logs' / (KEY + '.log')
    text = log.read_text(errors='replace')
    run = Path(record['run'])
    if (record.get('key') != KEY or record.get('state') != 'running' or 'returncode' in record or 'result' in record
            or (run / 'run_meta.json').exists() or (run / 'processes').exists()
            or 'Segmentation fault' not in text or '_capture_inputs.py' not in text
            or load(old / 'attempts' / (KEY + '.json')) != record
            or not (old / 'STOP_AFTER_CURRENT').is_file()):
        raise RuntimeError('attempt is not the stopped pre-estimation helper crash: ' + KEY)
    return record_path, record, log, run


def next_block_id(old, record):
    """The ID the engine gives the reviewed replacement: the first free ID of the fold block."""
    protocol = load(old / 'protocol.json')
    first, last = protocol['run_ids']['fold_blocks'][record['study']]
    ledger = load(old / 'workers' / record['study'] / 'run-ids.json')
    used = set(ledger.values())
    run_id = next(v for v in range(first, last + 1) if v not in used)
    existing = list(ROOT.glob(f'results/*/*/*/*/run{run_id}')) + list(prepare.MAIN.glob(f'results/*/*/*/*/run{run_id}'))
    if existing:
        raise RuntimeError('replacement run ID already exists: ' + str(existing))
    return run_id


def review(old, recovery):
    record_path, record, log, run = failed_attempt(old)
    run_id = next_block_id(old, record)
    new_run = run.with_name('run' + str(run_id))
    value = dict(
        classification='pre_estimation_infrastructure_failure', revision=REVISION, infrastructure_failed_attempts=[KEY],
        estimator_started=False, scientific_score=None, optimizer_feedback=False, replacement_count=1,
        original_record_sha256=prepare.sha(record_path), original_record=str(record_path),
        collected_copy=row(old / 'attempts' / (KEY + '.json')),
        logical_identity={k: record.get(k) for k in IDENTITY_FIELDS},
        original_run=str(run), original_run_contents=sorted(str(p.relative_to(run)) for p in run.rglob('*')),
        new_run=str(new_run), new_run_id=run_id,
        reason=('Infrastructure failure: the system-Python helper _capture_inputs.py segfaulted (exit 139) inside '
                'prepare_fresh_run_dir, before the estimator started. No run_meta.json, no trajectory, no score. '
                'The engine raised "Wrapper did not create metadata" and the worker wrote STOP_AFTER_CURRENT.'),
        evidence=dict(wrapper_log=row(log), stop_request=row(old / 'STOP_AFTER_CURRENT'),
                      worker_completion=row(record_path.parents[1] / 'develop-completion.json')),
        decided_by='user', decided_on='2026-11-04', decision=DECISION, reviewed_at=now(),
        note='The original record and run directory stay on disk in the earlier freeze, unchanged and never scored.')
    path = Path(recovery) / ('replacement-review-' + REVISION + '.json')
    write_new(path, value)
    return dict(review=str(path), sha256=prepare.sha(path), new_run_id=run_id)


def freeze(old, new, recovery):
    record_path, _, _, _ = failed_attempt(old)
    path = Path(recovery) / ('replacement-review-' + REVISION + '.json')
    revisions = {KEY: dict(revision=REVISION, record=str(record_path), record_sha256=prepare.sha(record_path),
                           review=str(path), review_sha256=prepare.sha(path))}
    amendment = dict(
        revision='recovery-20261104', at=now(), decision=DECISION, prior_protocol_sha256=prepare.sha(old / 'protocol.json'),
        prior_art=str(old), kind=('re-freeze after a pre-estimation helper crash: one reviewed replacement, lane sampler '
                                  'fix, one automatic replacement of pre-estimation failures; no change to noise values, '
                                  'ranges, stages, score or lanes'))
    return prepare.freeze(new, reuse_from=old, revisions=revisions, amendment=amendment)


def carry(old, new):
    """Copy what the engine's cache needs; a running record stays only in the earlier freeze."""
    old, new = Path(old), Path(new)
    if not (new / 'protocol.json').is_file() or (new / 'carried-from-earlier-freeze.json').exists():
        raise RuntimeError('carry needs a fresh frozen directory')
    copies, skipped = [], []

    def copy(source, target):
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise FileExistsError(str(target))
        shutil.copy2(source, target)
        if prepare.sha(target) != prepare.sha(source):
            raise RuntimeError('copy differs: ' + str(target))
        copies.append(dict(source=str(source), target=str(target), sha256=prepare.sha(target)))

    for path in sorted((old / 'attempts').glob('*.json')):
        if load(path).get('state') == 'finished':
            copy(path, new / 'attempts' / path.name)
        else:
            skipped.append(str(path))
    for path in sorted((old / 'studies').rglob('*.json')):
        copy(path, new / 'studies' / path.relative_to(old / 'studies'))
    budget = old / ('budget-' + DATASET + '.json')
    shared = old.parent / (DATASET + '-' + load(old / 'protocol.json')['shared_budget_file'])
    if load(budget) != load(shared):
        raise RuntimeError('phase budget differs from the shared budget')
    copy(budget, new / budget.name)
    for worker in sorted((old / 'workers').iterdir()):
        target = new / 'workers' / worker.name
        for path in sorted((worker / 'attempts').glob('*.json')):
            if load(path).get('state') == 'finished':
                copy(path, target / 'attempts' / path.name)
            else:
                skipped.append(str(path))
        copy(worker / 'run-ids.json', target / 'run-ids.json')
        for path in sorted((worker / 'studies').rglob('*.json')):
            copy(path, target / 'studies' / path.relative_to(worker / 'studies'))
        if (worker / 'budget.json').read_bytes() == budget.read_bytes():
            copy(worker / 'budget.json', target / 'budget.json')
        completion = worker / 'develop-completion.json'
        if completion.is_file() and load(completion).get('complete') is True:
            copy(completion, target / completion.name)
    manifest = dict(at=now(), source=str(old), source_protocol_sha256=prepare.sha(old / 'protocol.json'),
                    copied=copies, not_copied_unfinished=skipped,
                    note=('Wrapper logs, lane samples, events and controller logs stay in the source directory; '
                          'records point at them by absolute path.'))
    write_new(new / 'carried-from-earlier-freeze.json', manifest)
    return dict(copied=len(copies), unfinished_left_in_source=skipped)


def readiness(old, new, recovery):
    old, new = Path(old), Path(new)
    previous = load(old / 'readiness.json')
    protocol = load(new / 'protocol.json')
    _, _, log, _ = failed_attempt(old)
    review_path = Path(recovery) / ('replacement-review-' + REVISION + '.json')
    wanted = {s['id'] for s in protocol['folds'] if s['dataset'] == DATASET}
    if set(previous['studies']) != wanted or previous.get('dataset') != DATASET:
        raise RuntimeError('earlier readiness does not cover exactly CitrusFarm')
    # A progress report bound by the earlier readiness has since been appended to (hourly checks). It is not an
    # immutable artifact: it is dropped and listed; the earlier readiness, which bound it, is evidence itself.
    kept = [e for e in previous['evidence'] if Path(e['path']).is_file() and prepare.sha(e['path']) == e['sha256']]
    dropped = [dict(e, reason='changed since the earlier readiness; a progress report, not an artifact')
               for e in previous['evidence'] if e not in kept]
    if any(not e['path'].startswith('/data/imoroz/PROGRESS/') for e in dropped):
        raise RuntimeError('earlier readiness evidence changed: ' + str(dropped))
    evidence = kept + [row(p) for p in (
        old / 'readiness.json', old / 'protocol.json', old / 'execution-identity.json', old / ('activation-' + DATASET + '.json'),
        protocol['physical_attempt_revisions'][KEY]['record'], log, review_path, new / 'carried-from-earlier-freeze.json')]
    value = dict(previous, written_by='claude (recovery of 4 Nov 2026)',
                 decision=previous['decision'] + ' ' + DECISION,
                 protocol_sha256=prepare.sha(new / 'protocol.json'),
                 execution_manifest_sha256=prepare.sha(new / 'execution-identity.json'),
                 validated_scheduling=protocol['scheduling'], evidence=evidence,
                 recovery=dict(
                     at=now(), decided_by='user', decided_on='2026-11-04', prior_readiness_sha256=prepare.sha(old / 'readiness.json'),
                     dropped_evidence=dropped,
                     reasons=['helper crash replacement: run 70445, _capture_inputs.py exit 139 before the estimator; '
                              'one reviewed replacement under revision ' + REVISION,
                              'lane sampler fix: timing_lanes.py imports time, so every attempt records lane samples',
                              'pre-estimation auto-replacement: an attempt that fails before its estimator starts is '
                              'replaced once with a new run ID of its fold block; a second failure stops the campaign',
                              'finished attempts reused from ' + str(old) + ', never rerun; the 120 h budget keeps its start']))
    write_new(new / 'readiness.json', value)
    return dict(readiness=str(new / 'readiness.json'), sha256=prepare.sha(new / 'readiness.json'))


class WouldLaunch(Exception):
    pass


def verify(old, new, scratch):
    """Dry checks on a scratch copy of --new; nothing launches (execute_attempt is replaced)."""
    import noise_campaign as campaign
    import noise_campaign_engine as engine
    from noise_campaign_search import DevelopmentSearch
    import timing_search as coordinator
    old, new = Path(old).resolve(), Path(new).resolve()
    protocol = load(new / 'protocol.json')
    campaign.verify_activation(new, protocol, DATASET)
    coordinator.verify_order(new, protocol, DATASET)
    shared = load(new.parent / (DATASET + '-' + protocol['shared_budget_file']))
    if load(new / ('budget-' + DATASET + '.json')) != shared or shared != load(old / ('budget-' + DATASET + '.json')):
        raise RuntimeError('budget differs from the shared start')
    copy = Path(scratch).resolve() / new.name
    if copy.exists():
        raise FileExistsError(str(copy))
    shutil.copytree(new, copy)
    folds = {s['id']: s for s in protocol['folds'] if s['dataset'] == DATASET}
    launches = []

    def would_launch(spec, label, parameters, sequence, mode, repetition, phase, key, run_id, *rest):
        launches.append(dict(key=key, run_id=run_id))
        raise WouldLaunch(key)
    result = dict(cached=0, not_cached=[], folds={})
    finished = {p.name: load(p) for p in (old / 'attempts').glob('*.json') if load(p).get('state') == 'finished'}
    with patch.object(engine, 'execute_attempt', side_effect=would_launch):
        engine.configure(copy, protocol, None)
        engine.verify_frozen()
        for worker in sorted((copy / 'workers').iterdir()):
            engine.configure(worker, protocol, None)
            for path in sorted((worker / 'attempts').glob('*.json')):
                record = load(path)
                try:
                    got = engine.run_attempt(folds[record['study']], record['label'], record['params'], record['sequence'],
                                             record['mode'], record['repetition'], record['phase'])
                except WouldLaunch:
                    got = None
                if got == record == finished.get(path.name):
                    result['cached'] += 1
                else:
                    result['not_cached'].append(record['key'])
        missing = sorted(set(finished) - {p.name for p in (copy / 'workers').glob('*/attempts/*.json')})
        result['finished_in_source'] = len(finished)
        result['finished_missing_from_workers'] = missing
        for fold, spec in folds.items():
            if coordinator.complete(copy, spec, 'develop'):
                result['folds'][fold] = 'complete, skipped by run_stage'
                continue
            worker = coordinator.worker_directory(copy, spec, 'develop')
            worker.mkdir(parents=True, exist_ok=True)
            engine.configure(worker, protocol, None)
            launches.clear()
            try:
                DevelopmentSearch(engine, spec, protocol).develop()
                result['folds'][fold] = 'NO LAUNCH: unexpected'
            except WouldLaunch:
                item = launches[0]
                run_id = item['run_id']
                exists = list(ROOT.glob(f'results/*/*/*/*/run{run_id}')) + list(prepare.MAIN.glob(f'results/*/*/*/*/run{run_id}'))
                low, high = protocol['run_ids']['fold_blocks'][fold]
                cached = len(list((worker / 'attempts').glob('*.json')))
                result['folds'][fold] = dict(continues_with=item['key'], run_id=run_id, in_block=low <= run_id <= high,
                                             run_dir_exists=bool(exists), cached_records=cached)
    result['replacement'] = result['folds'].get(STUDY)
    ledger_old = load(old / 'workers' / STUDY / 'run-ids.json')
    result['replacement_id_unused'] = (result['replacement'] or {}).get('run_id') not in ledger_old.values()
    result['complete_folds'] = sum(v == 'complete, skipped by run_stage' for v in result['folds'].values())
    result['protocol_sha256'] = prepare.sha(new / 'protocol.json')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('step', choices=('review', 'freeze', 'carry', 'readiness', 'verify'))
    parser.add_argument('--old', type=Path, required=True)
    parser.add_argument('--new', type=Path, required=True)
    parser.add_argument('--recovery', type=Path, required=True)
    parser.add_argument('--scratch', type=Path)
    args = parser.parse_args()
    old, new = args.old.resolve(), args.new.resolve()
    if prepare.MAIN.resolve() in new.parents or ROOT.resolve() == prepare.MAIN.resolve():
        raise RuntimeError('run only from the isolated search checkout, outside main')
    if args.step == 'review':
        out = review(old, args.recovery.resolve())
    elif args.step == 'freeze':
        out = freeze(old, new, args.recovery.resolve())
    elif args.step == 'carry':
        out = carry(old, new)
    elif args.step == 'readiness':
        out = readiness(old, new, args.recovery.resolve())
    else:
        if not args.scratch:
            parser.error('verify needs --scratch')
        out = verify(old, new, args.scratch)
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
