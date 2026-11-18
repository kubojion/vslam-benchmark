#!/usr/bin/env python3
"""Carry explicit Sielinko claim reviews over from reference v2 to reference v4 (user decision D1, 18 Nov 2026).

The paper-acceptance ledger pins each reviewed attempt's evaluation digest, and the completed ZED selection pins three
run_eval.json files byte for byte. A reference change re-evaluates those runs. This module accepts the re-evaluation
in place of the reviewed one ONLY for the attempts the generated, pinned record lists, and only when the current
evaluation differs from the reviewed one in nothing but the reference:
  - the reviewed v2 evaluation is found by its pinned file sha256 (run_eval.json, or the content-addressed copy in
    .evaluation_history that the repaired-evaluation route keeps) and its digest equals the ledger's;
  - same run (dataset, sequence, algorithm, run, folder, mode, variant);
  - every evaluation input except the reference inputs has the same sha256 (trajectory, metadata, times, logs, ...),
    and the reference inputs are exactly the record's v2 set before and v4 set after;
  - the same qualification inputs: run_status, failure_reason, coverage_gap_pct, and pose_frames apart from the three
    reference-derived keys (reference_valid_intervals, reference_version, reference_limitations).
Numbers, reference coverage and segments may differ (they are computed against the reference). Anything else fails.

  python -B scripts/campaign/reference_carryover.py [--check]     generate (or check) the record from the ledger and
                                                                  the current evaluations (run after v4 is staged)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RECORD = 'configs/campaigns/sielinko-reference-v4-carryover-20261118.json'
LEDGER = 'docs/campaigns/paper-acceptance-20261001.json'
ZED_SELECTION = 'configs/campaigns/zed-vio-first-attempts-20261002.json'
SEQUENCE_PREFIX = 'zed2i/field1_110426_full_10fps_q90/'
DECISION = "User, 18 Nov 2026 (relayed verbatim by the lead): \"d1 pool yes apply mid search\" (D1: carry the reviews over)"
SELECTOR = 'configs/references/zed2i_field1_110426_full_10fps_q90.json'
V2_DIR = 'datasets/zed2i/field1_110426_full_10fps_q90/references/gnss-position-v2-20261002'
V4_DIR = 'datasets/zed2i/field1_110426_full_10fps_q90/references/gnss-epoch-v4-20261117'
REFERENCE_NAMES = ('reference.json', 'primary.tum', 'primary-support.json')
V2_SELECTOR_SHA256 = 'bce242a75c1d48e41b9e2eb71c4ae7e613f0b5c4d5044108f13346a73f1e8ced'
POSE_FRAME_REFERENCE_KEYS = ('reference_valid_intervals', 'reference_version', 'reference_limitations')
IDENTITY_KEYS = ('dataset', 'seq', 'algo', 'run', 'run_directory', 'run_type', 'gnss_variant')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def numerical_digest(evaluation):
    value = {k: v for k, v in evaluation.items() if k not in ('qualification', 'qualification_provenance')}
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def same(a, b):
    """Equality that treats NaN as equal to NaN (older evaluations stored NaN in observation fields)."""
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def reference_inputs(repo, directory, selector_sha):
    return dict({SELECTOR: selector_sha}, **{f'{directory}/{n}': sha(Path(repo)/directory/n) for n in REFERENCE_NAMES})


def load_record(repo=REPO):
    path = Path(repo)/RECORD
    if not path.is_file():
        return None
    record = json.loads(path.read_text())
    if record.get('schema') != 1 or record.get('decision', {}).get('accept') is not True:
        raise ValueError('reference carry-over record is not an accepted schema-1 decision')
    return record


def reviewed_evaluation(run_dir, file_sha):
    """The reviewed v2 evaluation by its pinned bytes: run_eval.json or its content-addressed preserved copy."""
    for path in (Path(run_dir)/'run_eval.json', Path(run_dir)/'.evaluation_history'/f'{file_sha}.json'):
        if path.is_file() and sha(path) == file_sha:
            return json.loads(path.read_text())
    return None


def only_reference_changed(v2, current, record):
    """Reasons why `current` differs from the reviewed `v2` evaluation in more than the reference (empty: carried)."""
    reasons = []
    for key in IDENTITY_KEYS:
        if v2.get(key) != current.get(key):
            reasons.append('run identity differs: '+key)
    inputs = [{i['path']: i['sha256'] for i in e.get('evaluation_provenance', {}).get('inputs', [])} for e in (v2, current)]
    before, after = record['reference']['v2'], record['reference']['v4']
    for path in sorted(set(inputs[0]) | set(inputs[1])):
        if path in before or path in after:
            continue
        if inputs[0].get(path) != inputs[1].get(path):
            reasons.append('non-reference input differs: '+path)
    if {p: inputs[0].get(p) for p in before} != before:
        reasons.append('reviewed evaluation does not use exactly the v2 reference inputs')
    if {p: inputs[1].get(p) for p in after} != after:
        reasons.append('current evaluation does not use exactly the v4 reference inputs')
    for key in ('run_status', 'failure_reason'):
        if not same(v2.get(key), current.get(key)):
            reasons.append(key+' differs')
    if not same((v2.get('coverage') or {}).get('coverage_gap_pct'), (current.get('coverage') or {}).get('coverage_gap_pct')):
        reasons.append('coverage_gap_pct differs')
    frames = [{k: v for k, v in (e.get('pose_frames') or {}).items() if k not in POSE_FRAME_REFERENCE_KEYS} for e in (v2, current)]
    if not same(frames[0], frames[1]):
        reasons.append('pose_frames differ beyond the reference-derived keys')
    return reasons


def carried_review(repo, relative, evaluation, ledger_record, record=None):
    """(True, entry) when the record carries this attempt's review over to the current evaluation."""
    record = record if record is not None else load_record(repo)
    entry = (record or {}).get('reviews', {}).get(relative)
    if not entry or entry['ledger_evaluation_sha256'] != ledger_record.get('evaluation_sha256'):
        return False, None
    v2 = reviewed_evaluation(Path(repo)/'results'/relative, entry['v2_run_eval_sha256'])
    if v2 is None or numerical_digest(v2) != entry['ledger_evaluation_sha256']:
        return False, None
    return not only_reference_changed(v2, evaluation, record), entry


def carried_evidence(repo, item, relative, evaluation, record=None):
    """A pinned evidence file that changed only because of the carried reference change."""
    record = record if record is not None else load_record(repo)
    if not record:
        return False
    path = Path(repo)/item['path']
    if item['path'] == SELECTOR:
        return item['sha256'] == V2_SELECTOR_SHA256 and path.is_file() and sha(path) == record['reference']['v4'][SELECTOR]
    if item['path'] == f'results/{relative}/run_eval.json':
        entry = record.get('reviews', {}).get(relative) or record.get('selection_pins', {}).get(item['path'])
        if not entry or entry['v2_run_eval_sha256'] != item['sha256']:
            return False
        v2 = reviewed_evaluation(path.parent, item['sha256'])
        current = json.loads(path.read_text()) if path.is_file() else None
        return (v2 is not None and current is not None and numerical_digest(current) == numerical_digest(evaluation)
                and not only_reference_changed(v2, current, record))
    return False


def carried_selection_pin(repo, item, record=None):
    """completed_zed_selections: a pinned run_eval.json superseded only by the carried reference change."""
    record = record if record is not None else load_record(repo)
    entry = (record or {}).get('selection_pins', {}).get(item['path'])
    if not entry or entry['v2_run_eval_sha256'] != item['sha256']:
        return False
    path = Path(repo)/item['path']
    v2 = reviewed_evaluation(path.parent, item['sha256'])
    current = json.loads(path.read_text()) if path.is_file() else None
    return v2 is not None and current is not None and not only_reference_changed(v2, current, record)


def current_evaluation(repo, relative):
    """The evaluation under the installed (v4) selector, computed in memory with the frozen evaluator; nothing written."""
    import sys
    sys.path.insert(0, str(Path(repo)/'scripts/eval'))
    from _saved_run import evaluate_saved_run
    return evaluate_saved_run(repo, Path(repo)/'results'/relative)[0]


CRITERION = ('reviewed v2 evaluation found by its pinned bytes, digest equal to the ledger; same run identity; every '
             'non-reference evaluation input equal; reference inputs exactly the v2 set before and the v4 set after; '
             'same run_status, failure_reason and coverage_gap_pct; pose_frames equal apart from '+', '.join(POSE_FRAME_REFERENCE_KEYS))


def build(repo=REPO):
    """Generate the record: every Sielinko attempt whose explicit review is current today, and the selection pins."""
    repo = Path(repo)
    ledger = json.loads((repo/LEDGER).read_text())
    record = dict(schema=1, decision=dict(accept=True, text=DECISION),
                  ledger=dict(path=LEDGER, sha256=sha(repo/LEDGER)),
                  reference=dict(v2=reference_inputs(repo, V2_DIR, V2_SELECTOR_SHA256),
                                 v4=reference_inputs(repo, V4_DIR, sha(repo/SELECTOR))),
                  criterion=CRITERION,
                  reviews={}, not_carried={}, selection_pins={}, not_current_today={})
    for relative, entry in sorted(ledger['attempts'].items()):
        if SEQUENCE_PREFIX not in relative:
            continue
        run = repo/'results'/relative
        published = run/'run_eval.json'
        if not published.is_file():
            record['not_current_today'][relative] = 'no evaluation'
            continue
        v2 = json.loads(published.read_text())
        if numerical_digest(v2) != entry['evaluation_sha256']:
            record['not_current_today'][relative] = 'review already stale under v2'
            continue
        current = current_evaluation(repo, relative)
        reasons = only_reference_changed(v2, current, record)
        item = dict(ledger_status=entry['status'], ledger_evaluation_sha256=entry['evaluation_sha256'],
                    v2_run_eval_sha256=sha(published))
        if reasons:
            record['not_carried'][relative] = dict(item, reasons=reasons)
        else:
            record['reviews'][relative] = item
    for cell in json.loads((repo/ZED_SELECTION).read_text())['completed']:
        for item in cell['evidence']:
            if item['path'].endswith('/run_eval.json'):
                relative = item['path'].removeprefix('results/').rsplit('/', 1)[0]
                published = repo/item['path']
                if sha(published) != item['sha256']:
                    raise ValueError('selection pin already differs from its v2 bytes: '+item['path'])
                reasons = only_reference_changed(json.loads(published.read_text()), current_evaluation(repo, relative), record)
                if reasons:
                    raise ValueError(f'selection pin {item["path"]} cannot carry over: {reasons}')
                record['selection_pins'][item['path']] = dict(record=ZED_SELECTION, v2_run_eval_sha256=item['sha256'])
    return record


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true', help='regenerate and compare with the committed record')
    ap.add_argument('--output', type=Path, default=REPO/RECORD)
    args = ap.parse_args(argv)
    text = json.dumps(build(), indent=1, sort_keys=True)+'\n'
    if args.check:
        same_bytes = args.output.is_file() and args.output.read_text() == text
        print('record matches' if same_bytes else 'RECORD DIFFERS: '+str(args.output))
        return 0 if same_bytes else 1
    args.output.write_text(text)
    value = json.loads(text)
    print(f'{args.output}: carried {len(value["reviews"])}, not carried {len(value["not_carried"])}, '
          f'selection pins {len(value["selection_pins"])}, sha256 {sha(args.output)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
