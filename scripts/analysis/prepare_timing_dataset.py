#!/usr/bin/env python3
"""Prepare the next dataset of the noise search in a new artifact directory (PLAN Update 7, Steps 2-3); never launches.

The protocol does not change between datasets. Each dataset gets its own frozen directory, because readiness and
activation bind one dataset, and the swap-guard fix of 5 Nov 2026 changed the source identity.

    freeze     freeze into --new, admitting every run ID --old admitted; keep its attempt revisions; record the amendment
    carry      copy --old's finished records, study records, reviews and budgets into --new
    starts     write --new's start scripts: the dataset's clip check, then its search
    readiness  after the clip check passed: write --new's readiness for --dataset from the check report
    verify     activation and order checks for --dataset on --new

--old is never written. Usage: prepare_timing_dataset.py STEP --old DIR --new DIR --dataset NAME
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts/analysis'), str(ROOT / 'scripts/run')]
import prepare_timing_search as prepare  # noqa: E402

DECISION = ('User, 5 Nov 2026 (PLAN Update 7): after CitrusFarm passes its automatic review, fix the swap guard so it '
            'counts swap only in the cgroups of active estimator runs, re-freeze, and run HortiMulti, then Rosario, '
            'each after its clip check and readiness. Nothing else in the protocol changes.')
# Keys a re-freeze may change; everything else must equal the earlier freeze.
FREEZE_KEYS = {'frozen_at', 'reused_from', 'amendments'}


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


def admitted_runs(old):
    """Run directories the earlier freeze admitted: its attempt records, and what it reused itself (run 70445)."""
    protocol = load(old / 'protocol.json')
    runs = prepare.reused_runs(old, protocol['campaign_id'])
    earlier = set((protocol.get('reused_from') or {}).get('run_ids', []))
    for path in prepare.used_run_ids(ROOT):
        if int(path.name[3:]) in earlier:
            runs.add(str(path))
    return runs


def freeze(old, new, dataset):
    previous = load(old / 'protocol.json')
    if dataset not in previous['run_order'] or dataset == previous['run_order'][0]:
        raise RuntimeError('a dataset re-freeze is for a later dataset of the run order')
    amendment = dict(
        revision='dataset-' + dataset + '-20261105', at=now(), decision=DECISION, prior_art=str(old),
        prior_protocol_sha256=prepare.sha(old / 'protocol.json'), prior_amendments=previous.get('amendments', []),
        kind=('re-freeze for the next dataset: swap guard counts only active estimator runs (timing_lanes.py), and the '
              'automatic review script; no change to noise values, ranges, stages, score, lanes or attempt policy'))
    original = prepare.reused_runs
    prepare.reused_runs = lambda previous_art, campaign: admitted_runs(Path(previous_art))
    try:
        out = prepare.freeze(new, reuse_from=old, revisions=previous.get('physical_attempt_revisions'), amendment=amendment)
    finally:
        prepare.reused_runs = original
    value = load(new / 'protocol.json')
    changed = sorted(k for k in set(value) | set(previous)
                     if k not in FREEZE_KEYS and value.get(k) != previous.get(k))
    if changed:
        raise RuntimeError('the re-freeze changed protocol fields: ' + ', '.join(changed) + '; review ' + str(new))
    return dict(out, unchanged_fields=len(set(value) - FREEZE_KEYS))


def carry(old, new):
    """Records only: wrapper logs, lane samples, events and worker directories stay in the source."""
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

    for path in sorted((old / 'attempts').glob('*.json')):
        if load(path).get('state') == 'finished':
            copy(path, new / 'attempts' / path.name)
        else:
            skipped.append(str(path))
    for folder in ('superseded-attempts', 'studies', 'reviews'):
        for path in sorted((old / folder).rglob('*.json')):
            copy(path, new / folder / path.relative_to(old / folder))
    for path in sorted(old.glob('budget-*.json')):
        copy(path, new / path.name)
    if skipped:
        raise RuntimeError('unfinished records in the source: ' + ', '.join(skipped[:5]))
    write_new(new / 'carried-from-earlier-freeze.json', dict(
        at=now(), source=str(old), source_protocol_sha256=prepare.sha(old / 'protocol.json'), copied=copies,
        note='Wrapper logs, lane samples, events and worker directories stay in the source; records point at them by absolute path.'))
    return dict(copied=len(copies))


def starts(new, dataset):
    for stage, unit, text in (('check', 'vslam-timing-search-' + dataset + '-check', 'clip check'),
                              ('all', 'vslam-timing-search-' + dataset, 'develop, then test')):
        name = new / ('start-' + dataset + ('-check' if stage == 'check' else '') + '.sh')
        if name.exists():
            raise FileExistsError(str(name))
        name.write_text(f"""#!/usr/bin/env bash
# {dataset}: {text}. It stops by itself when the stage ends. PLAN Update 7.
W={ROOT}
systemd-run --user --unit={unit} \\
    --description='Extended search, {dataset} {text} (PLAN Update 7)' \\
    -p KillMode=process -p WorkingDirectory=$W \\
    --setenv=PATH="$PATH" --setenv=HOME="$HOME" --setenv=PYTHONDONTWRITEBYTECODE=1 --setenv=GIT_OPTIONAL_LOCKS=0 \\
    $W/.venv/bin/python -B $W/scripts/analysis/timing_search.py --art {new} --execute --stage {stage} --dataset {dataset}
""")
        name.chmod(0o775)
    return dict(starts=sorted(str(p) for p in new.glob('start-' + dataset + '*.sh')))


def check_findings(new, protocol, dataset):
    """A check attempt proves the plumbing: finished, exit 0, evaluated, and the sentinel noise reached the estimator."""
    report_path = new / ('check-' + dataset + '-report.json')
    report = load(report_path)
    if report['protocol_sha256'] != prepare.sha(new / 'protocol.json'):
        raise RuntimeError('check report belongs to another protocol')
    wanted = protocol['gates']['check_folds'][dataset]
    problems, diverged = [], []
    if sorted(report['studies']) != sorted(wanted):
        problems.append('check report does not cover every system')
    for study in wanted:
        records = [load(p) for p in sorted((new / 'checks' / study / 'attempts').glob('*.json'))]
        if len(records) != 1:
            problems.append(f'{study}: {len(records)} check attempts')
            continue
        record = records[0]
        result = record.get('result') or {}
        evidence = (record.get('effective_noise_evidence') or {}).get('parameters')
        if record.get('state') != 'finished' or record.get('returncode') != 0 or record.get('timeout') or not result:
            problems.append(f"{study}: state={record.get('state')} exit={record.get('returncode')} timeout={record.get('timeout')}")
        elif evidence != record['params']:
            problems.append(f'{study}: native receipt does not show the sentinel noise')
        elif result.get('failed'):
            diverged.append(f"{study}: {result.get('numerical_status')} (exit 0, sentinel noise delivered)")
    return report_path, problems, diverged


def readiness(old, new, dataset):
    protocol = load(new / 'protocol.json')
    report_path, problems, diverged = check_findings(new, protocol, dataset)
    if problems:
        raise RuntimeError('clip check failed: ' + '; '.join(problems))
    previous = load(old / 'readiness.json')
    reviews = sorted((new / 'reviews').glob('*.json'))
    basis = dataset + ' clip check of every system passed in this freeze'
    value = dict(
        schema=1, passed=True, pending=[], dataset=dataset, written_by='claude-tester (PLAN Update 7, automatic)',
        decision=DECISION, protocol_sha256=prepare.sha(new / 'protocol.json'),
        execution_manifest_sha256=prepare.sha(new / 'execution-identity.json'),
        studies={s['id']: dict(ready=True, basis=basis) for s in protocol['folds'] if s['dataset'] == dataset},
        validated_scheduling=protocol['scheduling'],
        evidence=[row(p) for p in [report_path, *sorted((new / 'checks').glob('*/attempts/*.json')), *reviews,
                                   old / 'readiness.json', new / 'carried-from-earlier-freeze.json']],
        limits=[*previous.get('limits', []),
                'The check runs one sentinel clip per system; a divergence with exit 0 and the sentinel delivered is a result, not a plumbing fault.',
                *diverged])
    write_new(new / 'readiness.json', value)
    return dict(readiness=str(new / 'readiness.json'), sha256=prepare.sha(new / 'readiness.json'), diverged=diverged)


def verify(new, dataset):
    import noise_campaign as campaign
    import timing_search as coordinator
    protocol = load(new / 'protocol.json')
    campaign.verify_activation(new, protocol, dataset)
    coordinator.verify_order(new, protocol, dataset)
    return dict(dataset=dataset, activation='ok', order='ok', protocol_sha256=prepare.sha(new / 'protocol.json'))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('step', choices=('freeze', 'carry', 'starts', 'readiness', 'verify'))
    parser.add_argument('--old', type=Path, required=True)
    parser.add_argument('--new', type=Path, required=True)
    parser.add_argument('--dataset', required=True)
    args = parser.parse_args()
    old, new = args.old.resolve(), args.new.resolve()
    if prepare.MAIN.resolve() in new.parents or ROOT.resolve() == prepare.MAIN.resolve():
        raise RuntimeError('run only from the isolated search checkout, outside main')
    out = dict(freeze=lambda: freeze(old, new, args.dataset), carry=lambda: carry(old, new),
               starts=lambda: starts(new, args.dataset), readiness=lambda: readiness(old, new, args.dataset),
               verify=lambda: verify(new, args.dataset))[args.step]()
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
