#!/usr/bin/env python3
"""Generate the paper completion selection and its pooling record from the campaign's own records.

Writes configs/campaigns/paper-completion-attempts-20261111.json and
configs/campaigns/rule-c-cohort-pooling-20261111.json. Nothing here is typed by hand except the
user decisions in DECISIONS below, each with its evidence file. Re-run it after a listed attempt
finishes (Update 10 D r3): the output is deterministic for the same inputs.

Sources, in order of authority:
1. the counted run of each of the 1,050 planned repetitions, from the progress publisher's export
   that the paper's snapshot uses (rulec-actions.csv);
2. the user's later decisions (DECISIONS): PLAN Update 10 A and D, and the 11 Nov closure of
   OKVIS2-X VO-LC on Sielinko as did-not-finish;
3. cross-checks, which refuse rather than resolve: every new attempt must have a terminal saved
   attempt state whose identity equals the publisher's planned cohort for that repetition, and be
   an attempt the Rule C batch status, the AirSLAM LC completion contract, the publisher's planned
   target or a decision names.

Reads the live run folders only (run it with the repository's results/ visible read-only).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_repair_inventory as inventory  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
SIELINKO = 'zed2i/field1_110426_full_10fps_q90'

# User decisions after the publisher's last export (2 Nov 2026). Each replaces counted runs of one cell.
DECISIONS = {
    'vio-lc/rosariov2/sequence1/airslam': dict(
        runs={1: 40101},
        decided='User, 10 Nov 2026, PLAN Update 10 item A; run 11 Nov (search-gates.md, Update 10 item A)',
        not_counted={'run40009': 'held: unknown native odometry exit, unscored (LC completion queue item '
                                 'rule-c-air-rosariov2-sequence1-vio-lc-r1); kept on disk',
                     'run10001': 'interrupted 7 Oct before any estimator exit; never terminal; kept on disk'},
        evidence=['/data/imoroz/PROGRESS/IMU-TIMING-TUNE/PLAN.md',
                  '/data/imoroz/airslam-lc-completion-20261029/queue.json']),
    f'vio-lc/{SIELINKO}/okvis2x': dict(
        runs={1: 20101, 2: 20102, 3: 20103},
        decided='User, 10 Nov 2026, PLAN Update 10 item D (3 new runs, 8 h timeout, r1 run20001 not counted)',
        not_counted={'run20001': 'stopped at the earlier 2-h final-BA rule; superseding review '
                                 'reviews/379-superseded-20261111.json; kept on disk'},
        evidence=['/data/imoroz/rule-c-batch-20261018/reviews/379-superseded-20261111.json',
                  '/data/imoroz/PROGRESS/IMU-TIMING-TUNE/PLAN.md']),
}
# A cell closed without completion (user, 11 Nov 2026, option a). Its one attempt is kept as r1;
# the two planned repetitions that never ran stay at their default (never-run) slots.
CLOSED = {
    f'vo-lc/{SIELINKO}/okvis2x': dict(
        disposition='did_not_finish', attempt_run=10001,
        decided='User, 11 Nov 2026: no more runs; final bundle adjustment beyond 48 h in the one attempt; '
                'not completed in completion statistics, left out of accuracy comparisons',
        evidence=['/data/imoroz/rule-c-batch-20261018/reviews/097.json',
                  '/data/imoroz/rule-c-batch-20261018/handoff-097.json',
                  '/data/imoroz/PROGRESS/.scripts/paper-readiness-decisions.json',
                  '/data/imoroz/agents/preparations/results-organisation-20261111.md']),
}
# Receipt differences that pool only after a user decision (pending on 11 Nov 2026). Each is one switch
# in the pooling record: pending_user_decisions.<name>.accept. A cell gets the option only when its
# receipts differ in nothing else that the check compares.
POOLING_DECISIONS = {
    'harness_python': dict(
        fields={'/runtime/python'},
        option=dict(ignored_runtime_fields=['python']),
        question='Pool repetitions whose only receipt difference (besides the workspace) is the Python version of the '
                 'harness that launched the estimator (3.10.20 on 7-8 Oct, 3.13.5 in the 18 Oct batch, 3.10.12 in the '
                 'AirSLAM LC completion)?',
        recommendation='Pool, with disclosure (engineer, 11 Nov 2026)'),
    'stage_watchdog': dict(
        fields={'/parameters/stage_timeout_s'},
        option=dict(unreached_harness_limits=dict(
            stage_timeout_s='stage watchdog of the harness; pooled only if every listed run exited 0, so it never acted')),
        question='Pool repetitions whose recorded stage watchdog differs (AirSLAM: 43200 s for run40101 and the 7 Oct '
                 'VO-LC r1 attempts, 7200 s for the LC completion runs), given that no run reached it? Update 10 A '
                 'declared a 10800 s overall limit and no native-stage watchdog (search-gates.md).',
        recommendation='Pool, with disclosure (engineer, 11 Nov 2026)'),
}


def receipt_differences(repo, key, ids):
    """Paths of the cohort receipts that differ between the runs, apart from the workspace."""
    def flat(value, path=''):
        if isinstance(value, dict):
            out = {}
            for k, v in value.items(): out.update(flat(v, path+'/'+str(k)))
            return out
        if isinstance(value, list) and value and all(isinstance(v, dict) for v in value):
            return {path: json.dumps(value, sort_keys=True)}
        return {path: json.dumps(value, sort_keys=True)}
    payloads = []
    for i in ids:
        run = repo/'results'/key/f'run{i}'
        if not run.is_dir():
            continue
        try:
            payload = inventory.cohort_identity(inventory.read(run/'run_meta.json'), key.split('/')[3], run_dir=run)[1] or {}
        except (ValueError, OSError):
            return {'unverifiable'}
        payload = {k: v for k, v in payload.items() if k not in ('workspace', 'implementation_content_sha256')}
        payloads.append(flat(payload))
    if not payloads:
        return set()
    return {k for p in payloads[1:] for k in set(p) | set(payloads[0]) if p.get(k) != payloads[0].get(k)}


# A counted attempt whose saved identity differs from its logical slot, reviewed before r3 ran.
IDENTITY_EXCEPTIONS = {
    f'vo/{SIELINKO}/orbslam3/run10002': dict(
        reason='64 GiB memory-comparison run explicitly reused once as logical r2 in revision 11 '
               '(user, 21 Oct 2026); its original comparison identity is kept unchanged',
        evidence='/data/imoroz/rule-c-batch-20261018/coordinated/revision11-20261021/orb-r2-reuse-review.json'),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pinned(path, role):
    return dict(role=role, path=str(path), sha256=sha(path))


def lower_selections(repo):
    """The selection main has before this record: every earlier layer, as build() applies them."""
    selections = inventory.selected_attempts(repo)
    zed = inventory.completed_zed_selections(repo); selections.update(zed)
    selections.update(inventory.completed_batch_selections(repo, zed))
    corrected = inventory.corrected_selections(repo); selections.update(corrected)
    return {k: [int(i) for i in v] for k, v in selections.items()}, set(corrected)


def workspace_commit(repo, key, run_id):
    meta = inventory.read(repo/'results'/key/f'run{run_id}'/'run_meta.json')
    return ((meta.get('provenance') or {}).get('workspace') or {}).get('commit')


def changed_paths(repo, commits, algorithm, dataset):
    """Tracked paths an estimate could depend on that differ between the pooled workspace commits."""
    commits = sorted(c for c in commits if c)
    names = set()
    for a, b in zip(commits, commits[1:]):
        out = subprocess.run(['git', '-C', str(repo), 'diff', '--name-only', a, b, '--', 'scripts/run', 'configs', 'docker'],
                             check=True, capture_output=True, text=True).stdout.split()
        names.update(out)
    stems = dict(rosariov2='rosario', citrusfarm='citrus', zed2i='zed', euroc_mav='euroc', hortimulti='horti')
    def for_dataset(name):
        return stems[dataset] in name or not any(stem in name for stem in stems.values())
    relevant = sorted(n for n in names if for_dataset(n) and (
        algorithm in n.lower().replace('-', '_') or n.startswith('scripts/run/_')
        or (n.startswith('configs/sensors/') and 'sources/' not in n)))
    return dict(commit_pairs=[f'{a}..{b}' for a, b in zip(commits, commits[1:])], scripts_configs_paths_changed=len(names),
                relevant_paths_changed=relevant)


def build(repo, actions_path, planned_path, batch_dir, lc_contract_path, accept=()):
    lower, corrected = lower_selections(repo)
    planned = {r['id']: r for r in json.loads(Path(planned_path).read_text())}
    status = json.loads((Path(batch_dir)/'status.json').read_text())
    batch_outputs = {r['output']: r['index'] for r in status['records']}
    contract = json.loads(Path(lc_contract_path).read_text())
    lc = {str(Path(e['physical_output']).relative_to('/data/imoroz/vslam-benchmark')): e for e in contract['terminal_entries']}
    counted = defaultdict(lambda: [None]*3); ids_of = {}
    with open(actions_path, newline='') as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1050:
        raise ValueError(f'expected 1050 planned repetitions, found {len(rows)}')
    for r in rows:
        key = '/'.join((r['mode'], r['dataset'], r['seq'], r['alg'])); rep = int(r['rep'])
        counted[key][rep-1] = int(r['run'].removeprefix('run')); ids_of[(key, rep)] = r['id']
    problems = []; cells = {}; previous = {}; attempts = {}; not_counted = {}; closed = {}; sources = {}
    for key in sorted(counted):
        ids = list(counted[key]); decision = DECISIONS.get(key); closure = CLOSED.get(key)
        if decision:
            for rep, run_id in decision['runs'].items(): ids[rep-1] = run_id
            not_counted.update({f'results/{key}/{name}': why for name, why in decision['not_counted'].items()})
        if closure:
            ids = [closure['attempt_run'], 2, 3]
        before = lower.get(key, [1, 2, 3])
        if ids == before:
            continue
        if key in corrected:
            problems.append(f'{key}: publisher differs from the corrected CitrusFarm selection {before} -> {ids}')
            continue
        for rep, run_id in enumerate(ids, 1):
            if run_id == before[rep-1]:
                continue
            relative = f'results/{key}/run{run_id}'
            if closure and run_id == rep:
                if (repo/relative).exists():
                    problems.append(f'{relative}: closed default slot exists on disk')
                continue
            state_path = inventory.attempt_state_path(repo, key, run_id); state = inventory.read(state_path)
            identity = state.get('identity', {})
            if not state:
                problems.append(f'{relative}: no saved attempt state'); continue
            plan = planned.get(ids_of[(key, rep)], {})
            if decision and rep in decision['runs']:
                source = 'user decision: ' + decision['decided']
            elif relative in lc:
                source = 'AirSLAM LC completion contract item ' + lc[relative]['item_id']
            elif relative in batch_outputs:
                source = f'rule-c-batch-20261018 queue index {batch_outputs[relative]}'
            elif plan.get('target') == relative:
                source = 'publisher planned target (earlier Rule C stage of the frozen N=3 plan)'
            elif closure:
                source = 'closed cell: ' + closure['decided']
            else:
                problems.append(f'{relative}: counted by the publisher but named by no batch, contract or plan record'); continue
            exception = IDENTITY_EXCEPTIONS.get(f'{key}/run{run_id}')
            if exception:
                exception['recorded_identity'] = identity
            elif identity.get('repetition') != rep or identity.get('physical_run_id') != run_id:
                problems.append(f'{relative}: saved identity {identity} differs from repetition {rep}')
            if not (decision and rep in decision['runs']) and not exception and plan.get('cohort') != identity.get('cohort'):
                problems.append(f'{relative}: cohort {identity.get("cohort")} differs from the planned {plan.get("cohort")}')
            terminal = state.get('status') in inventory.TERMINAL
            if closure and run_id == closure['attempt_run']:
                closed[key] = dict(disposition=closure['disposition'], decided=closure['decided'],
                                   evidence=[pinned(p, 'closure evidence') for p in closure['evidence']],
                                   open_attempts={relative.removeprefix('results/'): dict(
                                       status=state.get('status'), attempt_state_sha256=sha(state_path))},
                                   never_run_repetitions=[2, 3])
            elif not terminal:
                problems.append(f'{relative}: attempt state {state.get("status")} is not terminal')
            attempts[relative.removeprefix('results/')] = dict(repetition=rep, cohort=identity.get('cohort'),
                status=state.get('status'), source=source, workspace_commit=workspace_commit(repo, key, run_id))
        cells[key] = ids; previous[key] = before
    for key, decision in DECISIONS.items():
        sources[key] = [pinned(p, 'decision evidence') for p in decision['evidence']]
    record = dict(
        schema=1,
        decided='User, 11 Nov 2026 (agents/preparations/results-organisation-20261111.md section 1); '
                'PLAN Update 10 A and D (10 Nov); the 6 Nov scoring decisions; OKVIS2-X VO-LC Sielinko closed as '
                'did-not-finish (11 Nov, option a)',
        policy='Select every counted attempt of the Rule C campaign as the progress publisher and the paper count it, '
               'with the later user decisions applied. An attempt an earlier selection chose and this record replaces '
               'moves to the historical cohort file; none is deleted. Not-counted attempts stay on disk. Corrected '
               'CitrusFarm VIO/VIO-LC (timing-corrected-attempts-20261102.json) is unchanged.',
        generated_by='scripts/campaign/make_paper_completion_selection.py',
        sources=[pinned(actions_path, 'counted runs per planned repetition (paper snapshot rulec-actions.csv)'),
                 pinned(planned_path, 'publisher planned runs and cohorts'),
                 pinned(Path(batch_dir)/'execution-plan.json', 'Rule C batch executed plan'),
                 pinned(Path(batch_dir)/'status.json', 'Rule C batch status'),
                 pinned(lc_contract_path, 'AirSLAM LC completion terminal-review contract')],
        decision_sources=sources,
        user_decisions={key: dict(runs={str(rep): run_id for rep, run_id in d['runs'].items()}, decided=d['decided'],
                                  not_counted=sorted(f'results/{key}/{n}' for n in d['not_counted']))
                        for key, d in DECISIONS.items() if key in cells},
        six_november_decisions=dict(note='Counted as normal scored repetitions with no disclosure (paper side). They are '
                                         'the counted runs of their slots and are selected like any other.',
                                    runs=json.loads(Path('/data/imoroz/PROGRESS/.scripts/paper-readiness-decisions.json')
                                                    .read_text())['include_in_score']['runs']),
        previous=previous, cells=cells, attempts=attempts,
        identity_exceptions={k: dict(v, evidence=pinned(v['evidence'], 'reviewed exception'))
                             for k, v in IDENTITY_EXCEPTIONS.items() if 'recorded_identity' in v},
        closed_cells=closed, not_counted=not_counted)
    missing6 = [r for r in record['six_november_decisions']['runs']
                if r.removeprefix('results/').rsplit('/run', 1)[0] in cells
                and int(r.rsplit('/run', 1)[1]) not in cells[r.removeprefix('results/').rsplit('/run', 1)[0]]]
    if missing6:
        problems.append('6 Nov decided runs not selected: ' + ', '.join(missing6))
    # Pooling: every listed cell whose selected attempts span workspace commits, or whose recorded cohorts
    # differ only through the workspace state (the uncommitted diff of the live tree). The inventory's
    # pooled_cohort check decides; a refusal keeps separate groups and records why.
    pooling_cells = {}
    for key, ids in cells.items():
        present = [i for i in ids if (repo/'results'/key/f'run{i}').is_dir()]
        commits = {workspace_commit(repo, key, i) for i in present}
        cohorts = set()
        for i in present:
            run = repo/'results'/key/f'run{i}'; meta = inventory.read(run/'run_meta.json')
            try:
                cohorts.add(inventory.cohort_identity(meta, key.split('/')[3], run_dir=run)[0])
            except (ValueError, OSError):
                cohorts.add('unverifiable:'+str(i))
        if len(commits) > 1 or len(cohorts) > 1:
            differences = receipt_differences(repo, key, ids)
            entry = dict(runs=ids, workspace_commits=sorted(c or 'none' for c in commits),
                         basis='workspace commits differ' if len(commits) > 1 else 'same workspace commit; recorded cohorts differ',
                         receipt_differences=sorted(differences),
                         reviewed_differences=changed_paths(repo, commits - {None}, key.split('/')[3], key.split('/')[1]))
            covered = set().union(*(d['fields'] for d in POOLING_DECISIONS.values()))
            if differences and differences <= covered:
                entry['options_if_accepted'] = {name: d['option'] for name, d in POOLING_DECISIONS.items()
                                                if differences & d['fields']}
            pooling_cells[key] = entry
    pooling = dict(schema=1, decided=record['decided'],
                   decided_by='user (paper completion, 11 Nov 2026; Update 10 A pooling approved 10 Nov), generated',
                   policy=json.loads((repo/inventory.POOLING).read_text())['policy'],
                   pending_user_decisions={name: dict(accept=name in accept, question=d['question'],
                                                      recommendation=d['recommendation'],
                                                      cells=sorted(k for k, e in pooling_cells.items()
                                                                   if name in e.get('options_if_accepted', {})))
                                           for name, d in POOLING_DECISIONS.items()},
                   cells=pooling_cells)
    return record, pooling, problems


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--actions', type=Path, required=True)
    ap.add_argument('--planned', type=Path, required=True)
    ap.add_argument('--batch', type=Path, default=Path('/data/imoroz/rule-c-batch-20261018'))
    ap.add_argument('--lc-contract', type=Path,
                    default=Path('/data/imoroz/airslam-lc-completion-20261029/rule-c-terminal-review-contract-v2.json'))
    ap.add_argument('--allow-open', action='append', default=[],
                    help='dry run only: leave this still-running cell out of the record, listed as pending')
    ap.add_argument('--accept', action='append', default=[], choices=sorted(POOLING_DECISIONS),
                    help='write this pending pooling decision as accepted (the user\'s answer); default: pending')
    args = ap.parse_args()
    record, pooling, problems = build(REPO, args.actions, args.planned, args.batch, args.lc_contract, set(args.accept))
    pending = []
    for key in args.allow_open:
        live = [p for p in problems if p.startswith(f'results/{key}/')]
        if not live or any('not terminal' not in p and 'no saved attempt state' not in p for p in live):
            raise SystemExit(f'--allow-open {key}: no running attempt or other problems: {live}')
        problems = [p for p in problems if p not in live]
        record['cells'].pop(key); record['previous'].pop(key)
        for name in [n for n in record['attempts'] if n.startswith(key + '/')]: record['attempts'].pop(name)
        pooling['cells'].pop(key, None); pending.append(key)
    if pending:
        record['pending_cells_not_selected'] = pending
    if problems:
        raise SystemExit('refused:\n  ' + '\n  '.join(problems))
    for name, value in ((inventory.PAPER_COMPLETION_SELECTION, record), (inventory.RULEC_POOLING, pooling)):
        (REPO/name).write_text(json.dumps(value, indent=1, sort_keys=False) + '\n')
    print(json.dumps(dict(cells=len(record['cells']), attempts=len(record['attempts']), closed=list(record['closed_cells']),
                          pending=pending, pooling_cells=len(pooling['cells'])), indent=1))


if __name__ == '__main__':
    main()
