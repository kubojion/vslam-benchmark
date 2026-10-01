#!/usr/bin/env python3
"""Evaluate one saved run with schema 3, preserving earlier evaluation bytes.

This command never starts an estimator or creates a COMPLETE marker. Numerical
completion is separate from execution success and scientific qualification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from _run_type import canonicalize_dataset, resolve
from _saved_run import atomic_json, evaluate_saved_run, evaluator_identity


def evaluation_current(ws, run_dir, document):
    """A marker alone cannot establish that cached metrics still match their inputs."""
    provenance = document.get('evaluation_provenance', {})
    if document.get('eval_schema') != 3 or provenance.get('evaluator', {}).get('sha256') != evaluator_identity()['sha256']:
        return False
    inputs = provenance.get('inputs', [])
    required = {str((run_dir/name).relative_to(ws)) for name in ('trajectory.txt', 'run_meta.json')}
    if not required.issubset({x.get('path') for x in inputs}):
        return False
    for item in inputs + document.get('pose_frames', {}).get('evidence', []):
        path = ws / item['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get('sha256'):
            return False
    return True


def preserve_evaluation(path):
    """Content-addressed independent copy, verified before atomic replacement."""
    if not path.exists():
        return
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    archive = path.parent/'.evaluation_history'/f'{digest}.json'
    archive.parent.mkdir(exist_ok=True)
    try:
        with archive.open('xb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        pass
    if archive.read_bytes() != raw:
        raise RuntimeError(f'evaluation backup verification failed: {archive}')


def component(value):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', value):
        raise argparse.ArgumentTypeError('unsafe path component')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dataset', type=component)
    parser.add_argument('sequence', type=component)
    parser.add_argument('algorithm', type=component)
    parser.add_argument('run_id', type=component)
    parser.add_argument('run_type', nargs='?', default='vo')
    parser.add_argument('--output', type=Path, help='stage to this path instead of the run directory')
    parser.add_argument('--check-current', action='store_true', help='read-only cache/evidence check')
    args = parser.parse_args()
    ws = Path(__file__).resolve().parents[2]
    rt = resolve(args.run_type, ws)
    run = rt.results_root/canonicalize_dataset(args.dataset)/args.sequence/args.algorithm/f'run{args.run_id}'
    target = args.output or run/'run_eval.json'
    try:
        if args.check_current:
            document = json.loads(target.read_text())
            return 0 if evaluation_current(ws, run, document) else 1
        result, _ = evaluate_saved_run(ws, run, gt_override=os.environ.get('GT_OVERRIDE'))
        # Verify the inputs still match before publishing derived metrics.
        if not evaluation_current(ws, run, result):
            # Legacy runs can lack run_meta. They may be evaluated, with explicit
            # provenance blockers, but cannot pass the strict resume cache gate.
            if (run/'run_meta.json').exists():
                raise RuntimeError('evaluation inputs changed while evaluating')
        preserve_evaluation(target)
        atomic_json(target, result)
        print(f"[eval] {run.relative_to(ws)}: {result['run_status']}; schema=3; qualification={result['qualification']['status']}")
        return 1 if result['run_status'] == 'eval_failed' else 0
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print(f'[eval] {type(exc).__name__}: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
