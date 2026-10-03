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
verified selection (configs/campaigns/zed-vio-first-attempts-20261002.json).
build_repair_inventory.completed_batch_selections re-checks everything on each build.
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
    args = ap.parse_args()
    status_path, manifest_path, frozen, output = (REPO / p for p in (args.status, args.manifest, args.frozen, args.output))
    status = json.loads(status_path.read_text())
    if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != status['manifest_sha256']:
        raise SystemExit('the executed plan changed after launch; recover the launch copy before recording')
    if frozen.exists() and frozen.read_bytes() != manifest_path.read_bytes():
        raise SystemExit(f'{frozen} exists with different content')
    frozen.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(manifest_path, frozen)
    manifest = json.loads(frozen.read_text())
    actions = {a['id']: a for a in manifest['actions']}
    earlier = json.loads((REPO / EARLIER).read_text())['cells'] if (REPO / EARLIER).is_file() else {}

    completed, cells = [], {}
    for attempt in status['attempts']:
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
            elif key in earlier and earlier[key][repetition - 1] >= 10001:
                ids.append(earlier[key][repetition - 1])
            else:
                raise SystemExit(f'{key} r{repetition}: not run in this batch and no earlier selected attempt')
        listing[key] = ids
    record = dict(schema=1,
                  policy='Select every finished attempt of the batch regardless of outcome; repetitions not run in '
                         'the batch come from the earlier verified selection; qualification needs claim review.',
                  source_manifest=evidence(frozen), batch_status=evidence(status_path),
                  earlier_selection=evidence(REPO / EARLIER) if (REPO / EARLIER).is_file() else None,
                  cells=listing, completed=sorted(completed, key=lambda r: (r['cell'], r['repetition'])))
    output.write_text(json.dumps(record, indent=1) + '\n')
    print(json.dumps(listing, indent=1))


if __name__ == '__main__':
    main()
