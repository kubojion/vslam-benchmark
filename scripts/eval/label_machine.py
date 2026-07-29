#!/usr/bin/env python3
"""Label existing run_eval.json files with the machine that produced them.

run_eval.json embeds a "machine" block (see _system_info.py) recording the
hardware behind its runtime numbers. New runs get it automatically at eval time;
this tool backfills EXISTING runs - but only the ones you can attribute to THIS
machine. Run it ON the machine that produced the runs, and select those runs.

HOW TO KNOW WHICH RUNS ARE YOURS
  - Runs already committed on origin/main were produced by whoever made
    origin/main. If that's you, use  --in-git origin/main.
  - Runs are timestamped by their trajectory.txt (written when the algorithm
    actually ran; re-evaluation never rewrites it). Use  --until / --since
    to select a date range you recognise as yours.
  - Combine with  --unlabeled-only  (default) so you never overwrite a run that
    already names a machine.

EXAMPLES
  # preview every unlabeled run whose trajectory predates 2026-07-17 (dry run)
  python3 scripts/eval/label_machine.py --until 2026-07-17 --dry-run

  # label all runs that exist on origin/main as this machine
  python3 scripts/eval/label_machine.py --in-git origin/main

  # label specific runs
  python3 scripts/eval/label_machine.py --paths results-vo/rosariov2/*/*/run1
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _system_info import collect  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
RESULT_ROOTS = ["results-vo", "results-vo-lc", "results-vio", "results-vio-lc", "results-gnss-vio"]


def _mdate(run_dir: Path) -> str | None:
    traj = run_dir / "trajectory.txt"
    if not traj.exists():
        return None
    return datetime.date.fromtimestamp(traj.stat().st_mtime).isoformat()


def _in_git(rel: str, ref: str) -> bool:
    try:
        subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", f"{ref}:{rel}"],
                       check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--paths", nargs="*", help="explicit run dirs or globs")
    ap.add_argument("--since", help="only runs with trajectory mtime >= YYYY-MM-DD")
    ap.add_argument("--until", help="only runs with trajectory mtime < YYYY-MM-DD")
    ap.add_argument("--in-git", metavar="REF",
                    help="only runs whose run_eval.json exists at REF (e.g. origin/main)")
    ap.add_argument("--unlabeled-only", action="store_true", default=True,
                    help="skip runs that already have a machine block (default)")
    ap.add_argument("--force", action="store_true",
                    help="overwrite existing machine blocks")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would change, write nothing")
    args = ap.parse_args()

    os.chdir(REPO)
    if args.paths:
        evals = []
        for p in args.paths:
            for hit in glob.glob(p):
                ev = Path(hit) / "run_eval.json" if Path(hit).is_dir() else Path(hit)
                if ev.name == "run_eval.json" and ev.exists():
                    evals.append(ev)
    else:
        evals = [Path(p) for root in RESULT_ROOTS
                 for p in glob.glob(f"{root}/**/run_eval.json", recursive=True)]

    machine = collect()
    print(f"[label] this machine: {machine.get('cpu')} / "
          f"{(machine.get('gpus') or [{}])[0].get('name', 'no gpu')} / "
          f"{machine.get('ram_total_gb')} GB / {machine.get('os')}")

    changed = skipped = 0
    for ev in sorted(evals):
        run_dir = ev.parent
        rel = os.path.relpath(ev.resolve(), REPO)
        d = json.loads(ev.read_text())

        if d.get("machine") and not args.force:
            skipped += 1
            continue
        md = _mdate(run_dir)
        if args.since and (md is None or md < args.since):
            continue
        if args.until and (md is None or md >= args.until):
            continue
        if args.in_git and not _in_git(rel, args.in_git):
            continue

        print(f"  {'would label' if args.dry_run else 'label'}: {rel}  (traj {md})")
        if not args.dry_run:
            new = {}
            for k, v in d.items():
                if k == "agri_segments":
                    new["machine"] = machine
                new[k] = v
            if "machine" not in new:
                new["machine"] = machine
            ev.write_text(json.dumps(new, indent=2))
        changed += 1

    verb = "would label" if args.dry_run else "labeled"
    print(f"[label] {verb} {changed} run(s); skipped {skipped} already-labeled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
