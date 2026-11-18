#!/usr/bin/env python3
"""Generate the cohort-pooling record of the 10 Sielinko a33 VIO cells (user decision, 18 Nov 2026: "pool yes").

VIO repetition 1 is the full N=1 at checkout 80ecf61; repetitions 2-3 ran at bb2e1e7. The lead's identical-execution
statement (/data/imoroz/sielinko-imu-pilot-20261116/readiness/n3-identical-execution.json, pinned) compares 17
must-equal fields per system and repetition; every field is copied from it, none typed. The record follows the
11 Nov format (configs/campaigns/rule-c-cohort-pooling-20261111.json); pooled_cohort still checks every
algorithm-relevant receipt byte for byte and refuses a cell on any other difference. OpenVINS: the post-run receipts
delivery_audit/native_outcome are set aside, as the user decided for the same receipts on 12 Nov
(configs/campaigns/rule-c-nonacting-differences-20261112.json, pinned).

  python -B scripts/campaign/make_a33_pooling_record.py [--check]
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUTPUT = 'configs/campaigns/sielinko-a33-cohort-pooling-20261118.json'
STATEMENT = Path('/data/imoroz/sielinko-imu-pilot-20261116/readiness/n3-identical-execution.json')
STATEMENT_SHA256 = '023c3721785845266eb0977a3de989f7bfa93a6efa859c534a98575882197287'
SELECTION = 'configs/campaigns/sielinko-a33-attempts-20261118.json'
NONACTING = 'configs/campaigns/rule-c-nonacting-differences-20261112.json'
MUST_EQUAL = 17
RECEIPT_ROLES = ('delivery_audit', 'native_outcome')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(repo=REPO, statement_path=STATEMENT):
    if sha(statement_path) != STATEMENT_SHA256:
        raise ValueError('identical-execution statement differs from its pin')
    statement = json.loads(Path(statement_path).read_text())
    if statement.get('condition_holds') is not True:
        raise ValueError('the identical-execution condition does not hold')
    selection = json.loads((repo/SELECTION).read_text())
    nonacting = json.loads((repo/NONACTING).read_text())
    openvins = nonacting['cells']['vio/zed2i/field1_110426_full_10fps_q90/openvins']['differences']
    cells = {}
    for system in statement['systems']:
        key = f"vio/zed2i/field1_110426_full_10fps_q90/{system['system']}"
        runs = selection['cells'][key]
        if [system['full_run_id']] + [r['run_id'] for r in sorted(system['reps'], key=lambda r: r['rep'])] != runs:
            raise ValueError('statement runs differ from the a33 selection: '+key)
        if system.get('condition_holds') is not True:
            raise ValueError('identical execution does not hold for '+key)
        reps = []
        for rep in sorted(system['reps'], key=lambda r: r['rep']):
            must = [f for f in rep['fields'] if f['category'] == 'must equal']
            if len({f['field'] for f in must}) != MUST_EQUAL or not all(f['equal'] is True for f in must):
                raise ValueError(f'{key} r{rep["rep"]}: not {MUST_EQUAL} equal must-equal fields')
            reps.append(dict(repetition=rep['rep'], run=rep['run_id'], compared_with=system['full_run_id'],
                             must_equal=[dict(field=f['field'], equal=True, value=f['full']) for f in must],
                             other=[dict(field=f['field'], category=f['category'], equal=f['equal']) for f in rep['fields']
                                    if f['category'] != 'must equal']))
        spec = dict(runs=runs, workspace_commits=[statement['full_manifest']['commit'], statement['n3_manifest']['commit']],
                    basis='identical-execution statement (camera-IMU lead, 16 Nov 2026): rep 1 = the full N=1 attempt; '
                          f'{MUST_EQUAL} must-equal fields equal for reps 2 and 3',
                    identical_execution=reps, lane=system['lane'])
        if system['system'] == 'openvins':
            spec['ignored_artifact_roles'] = {d['role']: dict(reason=d['reason'], decision=nonacting['decided'],
                                                              record=dict(path=NONACTING, sha256=sha(repo/NONACTING)))
                                              for d in openvins if d['role'] in RECEIPT_ROLES}
        cells[key] = spec
    if len(cells) != 10:
        raise ValueError('expected the 10 a33 VIO cells')
    return dict(schema=1, decided='User, 18 Nov 2026 (relayed verbatim by the lead): "d1 pool yes apply mid search"',
                decided_by='user, generated', generated_by='scripts/campaign/make_a33_pooling_record.py',
                policy='Pool a listed a33 VIO cell across checkouts 80ecf61 (rep 1) and bb2e1e7 (reps 2-3) only if every '
                       'algorithm-relevant receipt is byte-identical (pooled_cohort); only the workspace commit and the '
                       'scripts/configs tree may differ, and for OpenVINS the listed post-run receipts. A mismatch keeps '
                       'separate groups.',
                statement=dict(path=str(statement_path), sha256=STATEMENT_SHA256, rule=statement['rule'],
                               verdict=statement['verdict'], code_diff_files=len(statement['code_diff']['files'])),
                selection=dict(path=SELECTION, sha256=sha(repo/SELECTION)), pending_user_decisions={}, cells=cells)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args(argv)
    text = json.dumps(build(), indent=1)+'\n'
    path = REPO/OUTPUT
    if args.check:
        ok = path.is_file() and path.read_text() == text
        print('record matches' if ok else 'RECORD DIFFERS'); return 0 if ok else 1
    path.write_text(text)
    print(f'{path}: {len(json.loads(text)["cells"])} cells, sha256 {sha(path)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
