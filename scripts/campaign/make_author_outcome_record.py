#!/usr/bin/env python3
"""Write the user's decision of 13 Nov 2026: three author-reported attempts are the repetitions of one Rule C cell.

Writes configs/campaigns/rule-c-author-outcomes-20261113.json from the paper-owned source record (pinned by path and
sha256; never copied into main as a run). The attempt ids and outcomes are read from that file; nothing about a run
directory, runtime, exit, hardware or receipt is recorded or derived. The server attempt run10001 (review 097) stays a
historical attempt and is not selected; the never-run server slots 2 and 3 are not observations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_repair_inventory as inventory  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
SOURCE = Path('/data/imoroz/PAPER/vslam-paper/data/metadata/author-outcomes-20261113.json')
DECIDED = ('User, 13 Nov 2026 (engineer session): "I ran OKVIS2-X VO-LC on Sielinko three times on my own computer, each '
           'over 60 hours in final bundle adjustment without finishing. Count those three as the cell\'s repetitions, '
           'replacing the 11 Nov one-attempt decision."')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, default=SOURCE)
    args = ap.parse_args()
    source = json.loads(args.source.read_text())
    cell = '/'.join(source['cell'][k] for k in ('mode', 'dataset', 'seq', 'alg'))
    selection_path = REPO/inventory.PAPER_COMPLETION_SELECTION
    selection = json.loads(selection_path.read_text())
    if cell not in selection.get('closed_cells', {}):
        raise SystemExit('the author record must supersede an existing closed cell: ' + cell)
    closed = selection['closed_cells'][cell]
    historical = sorted(closed['open_attempts'])
    attempts = []
    for a in sorted(source['attempts'], key=lambda a: a['rep']):
        if a['outcome'] != 'dnf' or any(a.get(k) is not None for k in ('run_dir', 'exact_runtime_s', 'machine_receipt')):
            raise SystemExit('an author-reported attempt may carry no machine fields: ' + a['id'])
        attempts.append(dict(repetition=a['rep'], id=a['id'], outcome='dnf', provenance='author_report'))
    if [a['repetition'] for a in attempts] != [1, 2, 3] or len({a['id'] for a in attempts}) != 3:
        raise SystemExit('expected three distinct author-reported repetitions')
    record = dict(
        schema=1,
        decided=DECIDED,
        policy='The three author-reported attempts are the repetitions r1-r3 of the cell, outcome did not finish, '
               'provenance author_report. No run directory, runtime, exit code, hardware or receipt exists for them and '
               'none is recorded or derived. The server attempt kept by the 11 Nov closure stays on disk as a historical '
               'attempt, not selected and not a fourth attempt; the never-run server slots are not observations.',
        source=dict(kind=source['source']['kind'], path=str(args.source), sha256=sha(args.source),
                    statement=source['source']['statement']),
        supersedes=dict(path=inventory.PAPER_COMPLETION_SELECTION, sha256=sha(selection_path),
                        entry=f'closed_cells["{cell}"]', disposition=closed['disposition'], decided=closed['decided']),
        generated_by='scripts/campaign/make_author_outcome_record.py',
        cells={cell: dict(attempts=attempts,
                          historical_not_selected=[dict(attempt=f'results/{h}', reason=source['historical_excluded']['reason'],
                                                        review=source['historical_excluded']['review'])
                                                   for h in historical],
                          never_run_server_slots=closed.get('never_run_repetitions', []))})
    (REPO/inventory.AUTHOR_OUTCOMES).write_text(json.dumps(record, indent=1) + '\n')
    print(json.dumps(record['cells'], indent=1))


if __name__ == '__main__':
    main()
