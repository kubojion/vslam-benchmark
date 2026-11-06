#!/usr/bin/env python3
"""Resume a dataset of the noise search after a host reset, in a new artifact directory; never launches anything.

User decision of 6 Nov 2026: the host reset at about 22:30 CET on 5 Nov while HortiMulti ran in run5. The attempts
that were running are infrastructure failures, each replaced once with a new run ID of its fold block. Re-freeze for
the new boot and reuse every finished attempt.

    review     write the reviewed replacement of every attempt left running in --old
    freeze     freeze into --new: --old's admitted run IDs, its revisions plus the new ones, one amendment
    carry      copy --old's finished records, ledgers, study records, reviews, completions and budgets into --new
    readiness  write --new's readiness from --old's, with the recovery reason
    verify     activation, order, budget, and a dry replay on a scratch copy: cached records, replacement IDs

--old is never written. Usage: prepare_timing_resume.py STEP --old DIR --new DIR --dataset NAME --recovery DIR [--scratch DIR]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts/analysis'), str(ROOT / 'scripts/run')]
import prepare_timing_dataset as dataset_tools  # noqa: E402
import prepare_timing_search as prepare  # noqa: E402
from prepare_timing_dataset import load, now, row, write_new  # noqa: E402

REVISION = 'host-reset-20261105'
DECISION = ('User, 6 Nov 2026: the host reset (unclean, cause unknown) at about 22:30 CET on 5 Nov while the HortiMulti '
            'search ran. The attempts that were running are infrastructure failures, each replaced once with a new run '
            'ID of its fold block. Re-freeze for the new boot, reuse every finished attempt, then continue PLAN Update 7.')
IDENTITY_FIELDS = ('key', 'campaign_id', 'study', 'phase', 'label', 'params', 'sequence', 'mode', 'repetition', 'native_seed')
FREEZE_KEYS = {'frozen_at', 'reused_from', 'amendments', 'physical_attempt_revisions', 'frozen_source_sha256'}


def boot():
    return Path('/proc/sys/kernel/random/boot_id').read_text().strip()


def interrupted(old, dataset):
    """Attempts left running in --old: the collected copy equals the worker's record, and no result exists."""
    folds = {s['id'] for s in load(old / 'protocol.json')['folds'] if s['dataset'] == dataset}
    found = []
    for path in sorted((old / 'attempts').glob('*.json')):
        record = load(path)
        if record.get('state') == 'finished':
            continue
        worker = old / 'workers' / record['study'] / 'attempts' / path.name
        if (record.get('study') not in folds or record.get('state') != 'running' or 'result' in record
                or 'returncode' in record or not worker.is_file() or load(worker) != record):
            raise RuntimeError('unfinished attempt is not a plain interrupted run: ' + str(path))
        found.append((worker, record))
    if not found:
        raise RuntimeError('no interrupted attempt in ' + str(old))
    return found


def review(old, dataset, recovery):
    identity = load(old / 'execution-identity.json')
    if identity['boot_id'] == boot():
        raise RuntimeError('the host has not restarted since ' + str(old) + ' was frozen')
    protocol = load(old / 'protocol.json')
    items, taken = [], {}
    for record_path, record in interrupted(old, dataset):
        study = record['study']
        first, last = protocol['run_ids']['fold_blocks'][study]
        used = taken.setdefault(study, set(load(old / 'workers' / study / 'run-ids.json').values()))
        run_id = next(v for v in range(first, last + 1) if v not in used)
        used.add(run_id)
        existing = list(ROOT.glob(f'results/*/*/*/*/run{run_id}')) + list(prepare.MAIN.glob(f'results/*/*/*/*/run{run_id}'))
        if existing:
            raise RuntimeError('replacement run ID already exists: ' + str(existing))
        run = Path(record['run'])
        log = record_path.parents[1] / 'wrapper-logs' / (record['key'] + '.log')
        items.append(dict(
            key=record['key'], original_record=str(record_path), original_record_sha256=prepare.sha(record_path),
            collected_copy=row(old / 'attempts' / record_path.name),
            logical_identity={k: record.get(k) for k in IDENTITY_FIELDS}, lane=record.get('lane'), started=record.get('started'),
            original_run=str(run), original_run_contents=sorted(str(p.relative_to(run)) for p in run.rglob('*')) if run.is_dir() else None,
            wrapper_log=row(log) if log.is_file() else None, new_run_id=run_id))
    value = dict(
        classification='host_reset_interruption', revision=REVISION, infrastructure_failed_attempts=[i['key'] for i in items],
        scientific_score=None, optimizer_feedback=False, replacement_count=1, interrupted_boot_id=identity['boot_id'],
        replacement_boot_id=boot(), attempts=items, last_status=row(old / 'status.json'),
        reason=('Infrastructure failure: the host reset while these attempts ran. They have no exit code, no result and no '
                'score; nothing reached the optimizer.'),
        decided_by='user', decided_on='2026-11-06', decision=DECISION, reviewed_at=now(),
        note='The original records and run directories stay on disk in the earlier freeze, unchanged and never scored.')
    path = Path(recovery) / ('replacement-review-' + REVISION + '.json')
    write_new(path, value)
    return dict(review=str(path), sha256=prepare.sha(path), replacements={i['key']: i['new_run_id'] for i in items})


def freeze(old, new, dataset, recovery):
    previous = load(old / 'protocol.json')
    path = Path(recovery) / ('replacement-review-' + REVISION + '.json')
    reviewed = load(path)
    revisions = dict(previous.get('physical_attempt_revisions') or {})
    for item in reviewed['attempts']:
        if item['key'] in revisions:
            raise RuntimeError('attempt already has a reviewed revision: ' + item['key'])
        revisions[item['key']] = dict(revision=REVISION, record=item['original_record'],
                                      record_sha256=item['original_record_sha256'], review=str(path),
                                      review_sha256=prepare.sha(path))
    amendment = dict(
        revision='resume-' + dataset + '-20261106', at=now(), decision=DECISION, prior_art=str(old),
        prior_protocol_sha256=prepare.sha(old / 'protocol.json'), prior_amendments=previous.get('amendments', []),
        kind=('re-freeze after a host reset: one reviewed replacement per interrupted attempt, the host-reset review '
              'class in the attempt policy; no change to noise values, ranges, stages, score, lanes or attempt policy'))
    original = prepare.reused_runs
    prepare.reused_runs = lambda previous_art, campaign: dataset_tools.admitted_runs(Path(previous_art))
    try:
        out = prepare.freeze(new, reuse_from=old, revisions=revisions, amendment=amendment)
    finally:
        prepare.reused_runs = original
    value = load(new / 'protocol.json')
    changed = sorted(k for k in set(value) | set(previous) if k not in FREEZE_KEYS and value.get(k) != previous.get(k))
    if changed:
        raise RuntimeError('the re-freeze changed protocol fields: ' + ', '.join(changed) + '; review ' + str(new))
    trees = algorithm_trees(old)
    write_new(new / 'evidence' / 'source-identity-check.json', dict(
        at=now(), algorithm_trees=trees, source_changed=value['frozen_source_sha256'] != previous['frozen_source_sha256'],
        reading=('frozen_source_sha256 includes the workspace tree (scripts, configs), so a script commit changes it. '
                 'Every native algorithm tree must equal the one captured by the last run of that system.')))
    if any(isinstance(v, dict) and not v['unchanged'] for v in trees.values()):
        raise RuntimeError('a native algorithm source tree changed: ' + json.dumps(trees))
    return dict(out, revisions=sorted(revisions), algorithm_trees_unchanged=True)


def algorithm_trees(old):
    """Each system's native source tree now, against the one its last attempt in --old captured."""
    import _capture_implementation as implementation
    store = ROOT / 'results/.implementation-blobs/sha256'
    latest = {}
    for path in (old / 'attempts').glob('*.json'):
        record = load(path)
        if record.get('state') != 'finished':
            continue
        algorithm = record['candidate']['algorithm']
        if record['finished'] > latest.get(algorithm, ('',))[0]:
            latest[algorithm] = (record['finished'], record['run'])
    trees = {}
    for algorithm, (_, run) in sorted(latest.items()):
        name = implementation.SOURCES[algorithm]
        if not name:
            trees[algorithm] = 'no algorithm tree (workspace only)'
            continue
        before = [t for t in load(Path(run) / 'provenance/implementation.json')['trees'] if t['role'] == 'algorithm'][0]
        now_tree = implementation.capture_tree(ROOT, ROOT / 'src' / name, store)
        trees[algorithm] = dict(compared_with=run, unchanged=before.get('commit') == now_tree.get('commit')
                                and before.get('entries') == now_tree.get('entries'))
    return trees


def carry(old, new, dataset):
    """Copy what the engine's cache needs; a running record stays only in the earlier freeze."""
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
        copies.append(row(target))

    def finished(source, target):
        for path in sorted(source.glob('*.json')):
            if load(path).get('state') == 'finished':
                copy(path, target / path.name)
            else:
                skipped.append(str(path))

    finished(old / 'attempts', new / 'attempts')
    for folder in ('superseded-attempts', 'studies', 'reviews'):
        for path in sorted((old / folder).rglob('*.json')):
            copy(path, new / folder / path.relative_to(old / folder))
    budget = old / ('budget-' + dataset + '.json')
    shared = old.parent / (dataset + '-' + load(old / 'protocol.json')['shared_budget_file'])
    if load(budget) != load(shared):
        raise RuntimeError('phase budget differs from the shared budget')
    for path in sorted(old.glob('budget-*.json')):
        copy(path, new / path.name)
    for worker in sorted((old / 'workers').iterdir()):
        target = new / 'workers' / worker.name
        finished(worker / 'attempts', target / 'attempts')
        copy(worker / 'run-ids.json', target / 'run-ids.json')
        for path in sorted((worker / 'studies').rglob('*.json')):
            copy(path, target / 'studies' / path.relative_to(worker / 'studies'))
        if (worker / 'budget.json').read_bytes() == budget.read_bytes():
            copy(worker / 'budget.json', target / 'budget.json')
        for name in ('develop-completion.json', 'test-completion.json'):
            if (worker / name).is_file() and load(worker / name).get('complete') is True:
                copy(worker / name, target / name)
    write_new(new / 'carried-from-earlier-freeze.json', dict(
        at=now(), source=str(old), source_protocol_sha256=prepare.sha(old / 'protocol.json'), copied=copies,
        not_copied_unfinished=skipped,
        note='Wrapper logs, lane samples, events and controller logs stay in the source; records point at them by absolute path.'))
    return dict(copied=len(copies), unfinished_left_in_source=skipped)


def readiness(old, new, dataset, recovery):
    previous = load(old / 'readiness.json')
    protocol = load(new / 'protocol.json')
    review_path = Path(recovery) / ('replacement-review-' + REVISION + '.json')
    if previous.get('dataset') != dataset:
        raise RuntimeError('earlier readiness does not cover ' + dataset)
    kept = [e for e in previous['evidence'] if Path(e['path']).is_file() and prepare.sha(e['path']) == e['sha256']]
    if kept != previous['evidence']:
        raise RuntimeError('earlier readiness evidence changed')
    evidence = kept + [row(p) for p in (
        old / 'readiness.json', old / 'protocol.json', old / 'execution-identity.json', old / ('activation-' + dataset + '.json'),
        review_path, new / 'carried-from-earlier-freeze.json')]
    value = dict(previous, written_by='claude-tester (host-reset resume, 6 Nov 2026)',
                 decision=previous['decision'] + ' ' + DECISION,
                 protocol_sha256=prepare.sha(new / 'protocol.json'),
                 execution_manifest_sha256=prepare.sha(new / 'execution-identity.json'),
                 validated_scheduling=protocol['scheduling'], evidence=evidence,
                 recovery=dict(at=now(), decided_by='user', decided_on='2026-11-06',
                               prior_readiness_sha256=prepare.sha(old / 'readiness.json'),
                               reasons=['host reset at about 22:30 CET on 5 Nov: the attempts that were running are '
                                        'infrastructure failures, replaced once under revision ' + REVISION,
                                        'finished attempts reused from ' + str(old) + ', never rerun; the budget keeps its start',
                                        'clip check of this dataset passed in ' + str(old) + '; runners and containers unchanged']))
    write_new(new / 'readiness.json', value)
    return dict(readiness=str(new / 'readiness.json'), sha256=prepare.sha(new / 'readiness.json'))


class WouldLaunch(Exception):
    pass


def verify(old, new, dataset, recovery, scratch):
    """Dry checks on a scratch copy of --new; nothing launches (execute_attempt is replaced)."""
    import noise_campaign as campaign
    import noise_campaign_engine as engine
    from noise_campaign_search import DevelopmentSearch
    import timing_search as coordinator
    protocol = load(new / 'protocol.json')
    campaign.verify_activation(new, protocol, dataset)
    coordinator.verify_order(new, protocol, dataset)
    shared = load(new.parent / (dataset + '-' + protocol['shared_budget_file']))
    if load(new / ('budget-' + dataset + '.json')) != shared or shared != load(old / ('budget-' + dataset + '.json')):
        raise RuntimeError('budget differs from the shared start')
    copy = Path(scratch).resolve() / new.name
    if copy.exists():
        raise FileExistsError(str(copy))
    shutil.copytree(new, copy)
    folds = {s['id']: s for s in protocol['folds'] if s['dataset'] == dataset}
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
                low, high = protocol['run_ids']['fold_blocks'][fold]
                exists = list(ROOT.glob(f"results/*/*/*/*/run{item['run_id']}"))
                result['folds'][fold] = dict(continues_with=item['key'], run_id=item['run_id'],
                                             in_block=low <= item['run_id'] <= high, run_dir_exists=bool(exists))
    reviewed = load(Path(recovery) / ('replacement-review-' + REVISION + '.json'))
    result['replacements'] = {i['key']: dict(expected=i['new_run_id'], continues=next(
        (f for f in result['folds'].values() if isinstance(f, dict) and f['continues_with'] == i['key']), None))
        for i in reviewed['attempts']}
    result['finished_in_source'] = len(finished)
    result['protocol_sha256'] = prepare.sha(new / 'protocol.json')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('step', choices=('review', 'freeze', 'carry', 'readiness', 'verify'))
    parser.add_argument('--old', type=Path, required=True)
    parser.add_argument('--new', type=Path, required=True)
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--recovery', type=Path, required=True)
    parser.add_argument('--scratch', type=Path)
    args = parser.parse_args()
    old, new, recovery = args.old.resolve(), args.new.resolve(), args.recovery.resolve()
    if prepare.MAIN.resolve() in new.parents or ROOT.resolve() == prepare.MAIN.resolve():
        raise RuntimeError('run only from the isolated search checkout, outside main')
    if args.step == 'verify' and not args.scratch:
        parser.error('verify needs --scratch')
    out = dict(review=lambda: review(old, args.dataset, recovery),
               freeze=lambda: freeze(old, new, args.dataset, recovery),
               carry=lambda: carry(old, new, args.dataset),
               readiness=lambda: readiness(old, new, args.dataset, recovery),
               verify=lambda: verify(old, new, args.dataset, recovery, args.scratch))[args.step]()
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
