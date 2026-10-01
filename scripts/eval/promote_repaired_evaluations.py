#!/usr/bin/env python3
"""Promote checked staged evaluations, preserving every previous evaluation.

Default is read-only. --apply changes derived JSONs only, never trajectories,
metadata, configs, logs or completion markers. If interrupted, rebuild the
inventory and repeat; already matching targets are skipped.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from build_benchmark_csv import REPO, load_inventory, preserved_write
from _evaluate_run import preserve_evaluation
from _saved_run import evaluator_identity


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def plan_promotion(inventory, repo=REPO, *, evaluator=None):
    evaluator = evaluator or evaluator_identity()['sha256']
    plan = []
    for attempt in [a for c in inventory['cells'] for a in c['attempts']]+inventory['other_artifacts']:
        if not attempt.get('evaluation_path'): continue
        relative = Path(attempt['path'])
        if len(relative.parts) != 6 or relative.parts[0] != 'results' or '..' in relative.parts:
            raise ValueError('unsafe or unexpected attempt path')
        run = repo/relative
        source = repo/(attempt.get('staged_evaluation_path') or attempt['evaluation_path'])
        target = run/'run_eval.json'
        if repo.resolve() not in source.resolve().parents or source == target:
            raise ValueError('evaluation must be staged separately inside the repository')
        value = json.loads(source.read_text())
        expected = relative.parts[1:5]
        actual = tuple(value.get(k) for k in ('run_type','dataset','seq','algo'))
        if actual != expected or value.get('run_directory') != relative.name:
            raise ValueError('staged evaluation disagrees with target identity')
        if value.get('eval_schema') != 3 or value.get('evaluation_provenance', {}).get('evaluator', {}).get('sha256') != evaluator:
            raise ValueError('stale staged evaluator')
        if (value.get('qualification') != attempt['qualification'] or
            value.get('qualification_provenance') != inventory['qualification_review']):
            raise ValueError('staged and inventory qualification disagree')
        old, new = digest(target), digest(source)
        archive = run/'.evaluation_history'/f'{old}.json' if old and old != new else None
        plan.append(dict(source=str(source.relative_to(repo)), target=str(target.relative_to(repo)),
            previous_sha256=old, promoted_sha256=new,
            archive=str(archive.relative_to(repo)) if archive else None, already_current=old == new))
    if len({r['target'] for r in plan}) != len(plan):
        raise ValueError('duplicate promotion target')
    return plan


def apply_plan(plan, repo=REPO):
    # Validate all mutable sources/targets before publishing any of them.
    for record in plan:
        if digest(repo/record['source']) != record['promoted_sha256']:
            raise ValueError('staging changed after preflight')
        if digest(repo/record['target']) != record['previous_sha256']:
            raise ValueError('target changed after preflight')
    for record in plan:
        if record['already_current']: continue
        source, target = repo/record['source'], repo/record['target']
        if digest(source) != record['promoted_sha256'] or digest(target) != record['previous_sha256']:
            raise ValueError('concurrent change during promotion; stop and reconcile inventory')
        preserve_evaluation(target)
        if record['archive'] and digest(repo/record['archive']) != record['previous_sha256']:
            raise ValueError('previous evaluation was not preserved')
        preserved_write(target, source.read_bytes(), repo)
        if digest(target) != record['promoted_sha256']:
            raise ValueError('promoted evaluation mismatch')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--inventory', type=Path, default=REPO/'results/repair-20261001/inventory.json')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    inventory = load_inventory(args.inventory)
    plan = plan_promotion(inventory)
    output = args.inventory.parent/'promotion-manifest.json'
    if args.apply:
        # Preserve the plan before mutation, including every old hash/location.
        ledger = dict(schema=1, inventory_sha256=digest(args.inventory), records=plan, status='prepared')
        preserved_write(output, json.dumps(ledger, indent=2)+'\n')
        apply_plan(plan)
        ledger['status'] = 'promoted_and_hash_verified'
        preserved_write(output, json.dumps(ledger, indent=2)+'\n')
    print(json.dumps(dict(evaluations=len(plan), already_current=sum(r['already_current'] for r in plan),
                         applied=args.apply, note='Rebuild inventory after promotion.'), indent=2))


if __name__ == '__main__':
    main()
