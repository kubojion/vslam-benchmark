#!/usr/bin/env python3
"""Validate one evaluated run and write its COMPLETE marker last."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


REQUIRED = ("trajectory.txt", "run_meta.json", "run_eval.json")
VALID_EVALUATION_STATUSES = {"ok", "scale_collapse"}


def validate_location(run_dir: Path) -> list[str]:
    repo = Path(__file__).resolve().parents[2]
    results = (repo / "results").resolve()
    try:
        relative = run_dir.resolve().relative_to(results)
    except ValueError:
        return [f"run directory is outside {results}"]
    if len(relative.parts) != 5 or relative.parts[0] not in {
        "vo", "vo-lc", "vio", "vio-lc", "gnss-vio"
    } or not relative.parts[-1].startswith("run"):
        return [f"unexpected run directory layout: {relative}"]
    return []


def validate(run_dir: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED:
        path = run_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty {name}")
    for name in ("run_meta.json", "run_eval.json"):
        path = run_dir / name
        if path.is_file():
            try:
                data = json.loads(path.read_text())
                if name == "run_eval.json" and data.get("run_status") not in VALID_EVALUATION_STATUSES:
                    errors.append(
                        f"run_eval.json status is {data.get('run_status')!r}; "
                        f"expected one of {sorted(VALID_EVALUATION_STATUSES)}"
                    )
            except Exception as exc:
                errors.append(f"invalid {name}: {exc}")
    trajectory = run_dir / "trajectory.txt"
    if trajectory.is_file():
        rows = 0
        try:
            with trajectory.open() as stream:
                for line in stream:
                    if not line.strip() or line.lstrip().startswith("#"):
                        continue
                    if len(line.split()) < 8:
                        errors.append("trajectory contains a row with fewer than 8 columns")
                        break
                    rows += 1
            if rows < 2:
                errors.append("trajectory contains fewer than 2 poses")
        except OSError as exc:
            errors.append(f"cannot read trajectory: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    location_errors = validate_location(run_dir)
    if location_errors:
        for error in location_errors:
            print(f"[validate] {run_dir}: {error}")
        return 1
    marker = run_dir / "COMPLETE"
    if marker.exists() and not args.check_only:
        marker.unlink()
    errors = validate(run_dir)
    if errors:
        for error in errors:
            print(f"[validate] {run_dir}: {error}")
        return 1
    if not args.check_only:
        tmp = run_dir / ".COMPLETE.tmp"
        tmp.write_bytes(b"")
        os.replace(tmp, marker)
        print(f"[validate] complete -> {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
