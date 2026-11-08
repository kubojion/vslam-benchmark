#!/usr/bin/env python3
"""Prepare the later held-out repetitions of one dataset in a new artifact directory (PLAN Update 8); never launches.

Update 8, steps 1 and 2 (user, 8 Nov 2026): the declared test-later stage (VIO repetitions 2 and 3 of every fold's
frozen winner on its held-out sequence) and the amendment test-later-lc (VIO-LC repetitions 2 and 3), declared after
the N=1 VIO-LC results were seen. Nothing feeds back into selection.

    freeze     freeze into --new, admitting every run ID of the --admit directories; record the amendment
    carry      copy --source's records and this dataset's worker ledgers, studies and completions; reviews from --admit[-1]
    readiness  write --new's readiness from --source's, with the reason
    verify     activation, order, and a dry replay of test-later on a scratch copy: next run IDs per fold

--source is the directory the dataset's develop and test ran in. Earlier directories are never written.
Usage: prepare_timing_later.py STEP --new DIR --dataset NAME --source DIR --admit DIR [DIR ...] [--scratch DIR]
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
import prepare_timing_resume as resume  # noqa: E402
import prepare_timing_search as prepare  # noqa: E402
from prepare_timing_dataset import load, now, row, write_new  # noqa: E402

DECISION = ('User, 8 Nov 2026 (PLAN Update 8): after the Rosario review, run the declared test-later stage (two more VIO '
            'repetitions of every frozen winner on its held-out sequence, N=3) on all three datasets, then two more VIO-LC '
            'repetitions (amendment approved by the user, declared after the N=1 VIO-LC results were seen). No selection changes.')
# Fields a later-stage freeze may change; everything else must equal the latest freeze.
FREEZE_KEYS = {'frozen_at', 'reused_from', 'amendments', 'physical_attempt_revisions', 'frozen_source_sha256', 'test_later_lc'}


def admitted(arts):
    runs = set()
    for art in arts:
        runs |= dataset_tools.admitted_runs(art)
    return runs


def freeze(new, dataset, source, arts):
    latest = load(arts[-1] / 'protocol.json')
    revisions = {}
    for art in arts:
        revisions.update(load(art / 'protocol.json').get('physical_attempt_revisions') or {})
    amendment = dict(
        revision='later-' + dataset + '-20261108', at=now(), decision=DECISION, source_art=str(source),
        admitted_from=[str(a) for a in arts], prior_protocol_sha256=prepare.sha(arts[-1] / 'protocol.json'),
        prior_amendments=latest.get('amendments', []),
        kind=('re-freeze for the later held-out repetitions: test-later as declared, test-later-lc added by amendment; '
              'no change to noise values, ranges, selection, score, lanes or attempt policy'))
    original = prepare.reused_runs
    prepare.reused_runs = lambda previous_art, campaign: admitted(arts)
    try:
        out = prepare.freeze(new, reuse_from=arts[-1], revisions=revisions, amendment=amendment)
    finally:
        prepare.reused_runs = original
    value = load(new / 'protocol.json')
    changed = sorted(k for k in set(value) | set(latest) if k not in FREEZE_KEYS and value.get(k) != latest.get(k))
    if changed:
        raise RuntimeError('the re-freeze changed protocol fields: ' + ', '.join(changed) + '; review ' + str(new))
    trees = resume.algorithm_trees(source)
    write_new(new / 'evidence' / 'source-identity-check.json', dict(
        at=now(), compared_with_art=str(source), algorithm_trees=trees,
        reading=('frozen_source_sha256 includes the workspace tree (scripts, configs), so a script commit changes it. '
                 'Every native algorithm tree must equal the one captured by the last run of that system.')))
    if any(isinstance(v, dict) and not v['unchanged'] for v in trees.values()):
        raise RuntimeError('a native algorithm source tree changed: ' + json.dumps(trees))
    return dict(out, test_later_lc=value.get('test_later_lc'), algorithm_trees_unchanged=True)


def carry(new, dataset, source, arts):
    """The engine's cache for this dataset; budgets are not carried, the later stages bind their own."""
    if not (new / 'protocol.json').is_file() or (new / 'carried-from-earlier-freeze.json').exists():
        raise RuntimeError('carry needs a fresh frozen directory')
    folds = {s['id'] for s in load(new / 'protocol.json')['folds'] if s['dataset'] == dataset}
    copies, skipped = [], []

    def copy(path, target):
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise FileExistsError(str(target))
        shutil.copy2(path, target)
        if prepare.sha(target) != prepare.sha(path):
            raise RuntimeError('copy differs: ' + str(target))
        copies.append(row(target))

    for path in sorted((source / 'attempts').glob('*.json')):
        if load(path).get('study') in folds:
            (copy(path, new / 'attempts' / path.name) if load(path).get('state') == 'finished' else skipped.append(str(path)))
    for fold in sorted(folds):
        for path in sorted((source / 'studies' / fold).rglob('*.json')):
            copy(path, new / 'studies' / path.relative_to(source / 'studies'))
        worker = source / 'workers' / fold
        target = new / 'workers' / fold
        for path in sorted((worker / 'attempts').glob('*.json')):
            (copy(path, target / 'attempts' / path.name) if load(path).get('state') == 'finished' else skipped.append(str(path)))
        copy(worker / 'run-ids.json', target / 'run-ids.json')
        for path in sorted((worker / 'studies').rglob('*.json')):
            copy(path, target / 'studies' / path.relative_to(worker / 'studies'))
        for name in ('develop-completion.json', 'test-completion.json'):
            if load(worker / name).get('complete') is not True:
                raise RuntimeError(fold + ': ' + name + ' is not complete in ' + str(source))
            copy(worker / name, target / name)
    for path in sorted((arts[-1] / 'reviews').glob('*.json')):
        copy(path, new / 'reviews' / path.name)
    if skipped:
        raise RuntimeError('unfinished records in the source: ' + ', '.join(skipped[:5]))
    write_new(new / 'carried-from-earlier-freeze.json', dict(
        at=now(), source=str(source), reviews_from=str(arts[-1]), copied=copies,
        note='Only this dataset; wrapper logs, lane samples and events stay in the source directory.'))
    return dict(copied=len(copies))


def readiness(new, dataset, source):
    previous = load(source / 'readiness.json')
    protocol = load(new / 'protocol.json')
    if previous.get('dataset') != dataset:
        raise RuntimeError('source readiness does not cover ' + dataset)
    kept = [e for e in previous['evidence'] if Path(e['path']).is_file() and prepare.sha(e['path']) == e['sha256']]
    if kept != previous['evidence']:
        raise RuntimeError('source readiness evidence changed')
    value = dict(previous, written_by='claude-tester (PLAN Update 8, later repetitions)',
                 decision=previous['decision'] + ' ' + DECISION,
                 protocol_sha256=prepare.sha(new / 'protocol.json'),
                 execution_manifest_sha256=prepare.sha(new / 'execution-identity.json'),
                 validated_scheduling=protocol['scheduling'],
                 evidence=kept + [row(p) for p in (source / 'readiness.json', source / 'protocol.json',
                                                   source / 'execution-identity.json', new / 'carried-from-earlier-freeze.json')],
                 later=dict(at=now(), decided_by='user', decided_on='2026-11-08', source=str(source),
                            reasons=['develop and test of this dataset finished in ' + str(source) + ' and passed review',
                                     'runners and containers unchanged; native algorithm trees checked at the freeze']))
    write_new(new / 'readiness.json', value)
    return dict(readiness=str(new / 'readiness.json'), sha256=prepare.sha(new / 'readiness.json'))


class WouldLaunch(Exception):
    pass


def verify(new, dataset, scratch):
    import noise_campaign as campaign
    import noise_campaign_engine as engine
    from noise_campaign_search import DevelopmentSearch
    import timing_search as coordinator
    protocol = load(new / 'protocol.json')
    campaign.verify_activation(new, protocol, dataset)
    coordinator.verify_order(new, protocol, dataset)
    folds = coordinator.stage_folds(protocol, 'test-later', dataset)
    coordinator.verify_stage_order(new, 'test-later', folds)
    coordinator.verify_stage_order(new, 'test-later-lc', folds)
    copy = Path(scratch).resolve() / new.name
    if copy.exists():
        raise FileExistsError(str(copy))
    shutil.copytree(new, copy)
    launches, result = [], {}

    def would_launch(spec, label, parameters, sequence, mode, repetition, phase, key, run_id, *rest):
        launches.append(dict(key=key, run_id=run_id, mode=mode, repetition=repetition))
        raise WouldLaunch(key)
    with patch.object(engine, 'execute_attempt', side_effect=would_launch):
        engine.configure(copy, protocol, None)
        engine.verify_frozen()
        for spec in folds:
            worker = coordinator.worker_directory(copy, spec, 'test-later')
            engine.configure(worker, protocol, None)
            launches.clear()
            try:
                DevelopmentSearch(engine, spec, protocol).final_later()
                result[spec['id']] = 'NO LAUNCH: unexpected'
            except WouldLaunch:
                item = launches[0]
                low, high = protocol['run_ids']['fold_blocks'][spec['id']]
                exists = list(ROOT.glob(f"results/*/*/*/*/run{item['run_id']}"))
                result[spec['id']] = dict(item, in_block=low <= item['run_id'] <= high, run_dir_exists=bool(exists))
    return dict(folds=result, protocol_sha256=prepare.sha(new / 'protocol.json'))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('step', choices=('freeze', 'carry', 'readiness', 'verify'))
    parser.add_argument('--new', type=Path, required=True)
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--admit', type=Path, nargs='+', required=True)
    parser.add_argument('--scratch', type=Path)
    args = parser.parse_args()
    new, source, arts = args.new.resolve(), args.source.resolve(), [a.resolve() for a in args.admit]
    if prepare.MAIN.resolve() in new.parents or ROOT.resolve() == prepare.MAIN.resolve():
        raise RuntimeError('run only from the isolated search checkout, outside main')
    if args.step == 'verify' and not args.scratch:
        parser.error('verify needs --scratch')
    out = dict(freeze=lambda: freeze(new, args.dataset, source, arts),
               carry=lambda: carry(new, args.dataset, source, arts),
               readiness=lambda: readiness(new, args.dataset, source),
               verify=lambda: verify(new, args.dataset, args.scratch))[args.step]()
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
