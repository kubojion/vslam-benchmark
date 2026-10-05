#!/usr/bin/env python3
"""Record which physical attempts a completed batch contributes to each cell.

Run once after a batch ends and before any plan is regenerated:

  python3 scripts/campaign/record_batch_selection.py \\
      --status logs/zed-vio-n3-20261003c/status.json \\
      --manifest results/zed-preparation-20261002/campaign/manifest.json \\
      --frozen results/zed-vio-n3-20261003/executed-zed-manifest.json \\
      --output configs/campaigns/zed-vio-n3-attempts-20261003.json

The executed plan is copied to --frozen only if its hash equals the one the batch
recorded at launch. Every finished attempt is selected regardless of outcome; failures
stay in the denominator. Repetitions the batch did not run are taken from the earlier
verified selection (configs/campaigns/zed-vio-first-attempts-20261002.json) or keep the
cell's default slot (physical id = repetition).
build_repair_inventory.completed_batch_selections re-checks everything on each build.

--status may also be a run_future_manifest state (logs/server-campaign/<campaign>/state.json);
it is then copied to --frozen-status, since the live state changes with later executions.
An attempt that did not finish, or whose failure was caused outside the estimator (a host
restart, a capacity setting), is left unselected only when named with --exclude ID=REASON;
its repetition keeps its default slot and is planned again.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EARLIER = 'configs/campaigns/zed-vio-first-attempts-20261002.json'


def evidence(path):
    return dict(path=str(path.relative_to(REPO)), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    for name in ('status', 'manifest', 'frozen', 'output'):
        ap.add_argument('--' + name, type=Path, required=True)
    ap.add_argument('--frozen-status', type=Path, help='copy of a run_future_manifest state (required for one)')
    ap.add_argument('--exclude', action='append', default=[], metavar='ACTION_ID=REASON')
    ap.add_argument('--carry', type=Path, action='append', default=[],
                    help='earlier batch selection whose listing fills repetitions this batch did not run')
    args = ap.parse_args()
    status_path, manifest_path, frozen, output = (REPO / p for p in (args.status, args.manifest, args.frozen, args.output))
    status = json.loads(status_path.read_text())
    excluded = dict(item.split('=', 1) for item in args.exclude)
    if 'actions' in status:  # run_future_manifest state -> the attempt list a batch driver writes
        if args.frozen_status is None:
            raise SystemExit('--frozen-status is required for a run_future_manifest state')
        frozen_status = REPO / args.frozen_status
        if frozen_status.exists() and frozen_status.read_bytes() != status_path.read_bytes():
            raise SystemExit(f'{frozen_status} exists with different content')
        frozen_status.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(status_path, frozen_status)
        status_path = frozen_status
        status = dict(manifest_sha256=status['manifest_sha256'],
                      attempts=[dict(id=i, status='finished' if a.get('status') in ('evaluated', 'failure_or_review')
                                     else a.get('status'), runner_exit_code=a.get('exit_code'))
                                for i, a in status['actions'].items()])
    unknown = set(excluded) - {a['id'] for a in status['attempts']}
    if unknown:
        raise SystemExit(f'excluded actions not in the batch: {sorted(unknown)}')
    if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != status['manifest_sha256']:
        raise SystemExit('the executed plan changed after launch; recover the launch copy before recording')
    if frozen.exists() and frozen.read_bytes() != manifest_path.read_bytes():
        raise SystemExit(f'{frozen} exists with different content')
    frozen.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(manifest_path, frozen)
    manifest = json.loads(frozen.read_text())
    actions = {a['id']: a for a in manifest['actions']}
    earlier = json.loads((REPO / EARLIER).read_text())['cells'] if (REPO / EARLIER).is_file() else {}
    carried = {}
    for path in args.carry:
        carried.update(json.loads((REPO / path).read_text())['cells'])

    completed, cells, left_out = [], {}, []
    for attempt in status['attempts']:
        if attempt['id'] in excluded:
            left_out.append(dict(action_id=attempt['id'], status=attempt.get('status'),
                                 path=actions[attempt['id']]['planned_output'], reason=excluded[attempt['id']]))
            continue
        if attempt.get('status') != 'finished':
            raise SystemExit(f"batch attempt {attempt['id']} is {attempt.get('status')}; record only a completed batch")
        action = actions[attempt['id']]
        run_id = int(Path(action['planned_output']).name.removeprefix('run'))
        state = REPO / 'results/.attempt-state' / action['cell'].replace('/', '__') / f'run{run_id}.json'
        completed.append(dict(cell=action['cell'], repetition=action['repetition'], physical_run_id=run_id,
                              action_id=attempt['id'], path=action['planned_output'],
                              runner_exit_code=attempt.get('runner_exit_code'), attempt_state=evidence(state)))
        cells.setdefault(action['cell'], {})[action['repetition']] = run_id
    listing = {}
    for key, reps in sorted(cells.items()):
        ids = []
        for repetition in (1, 2, 3):
            if repetition in reps:
                ids.append(reps[repetition])
            elif key in carried:
                ids.append(carried[key][repetition - 1])
            elif key in earlier and earlier[key][repetition - 1] >= 10001:
                ids.append(earlier[key][repetition - 1])
            else:
                ids.append(repetition)
        listing[key] = ids
    record = dict(schema=1,
                  policy='Select every finished attempt of the batch regardless of outcome; repetitions not run in '
                         'the batch come from the earlier verified selection or keep the default slot; attempts '
                         'excluded with a reason stay unselected; qualification needs claim review.',
                  source_manifest=evidence(frozen), batch_status=evidence(status_path),
                  earlier_selection=evidence(REPO / EARLIER) if (REPO / EARLIER).is_file() else None,
                  carried_selections=[evidence(REPO / p) for p in args.carry],
                  cells=listing, completed=sorted(completed, key=lambda r: (r['cell'], r['repetition'])),
                  excluded=left_out)
    output.write_text(json.dumps(record, indent=1) + '\n')
    print(json.dumps(listing, indent=1))


if __name__ == '__main__':
    main()
