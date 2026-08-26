#!/usr/bin/env python3
"""Safely replace one algorithm result cell beneath results/<run-type>."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


RUN_TYPES = {"vo", "vo-lc", "vio", "vio-lc", "gnss-vio"}
COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


def component(value: str) -> str:
    if not COMPONENT.fullmatch(value) or value in {".", ".."}:
        raise argparse.ArgumentTypeError(f"unsafe path component: {value!r}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("run_type", choices=sorted(RUN_TYPES))
    parser.add_argument("dataset", type=component)
    parser.add_argument("sequence", type=component)
    parser.add_argument("algorithm", type=component)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo = args.repo.resolve()
    results_base = repo / "results"
    if results_base.is_symlink():
        raise SystemExit(f"refusing symlink result root: {results_base}")
    run_root = (repo / "results" / args.run_type).resolve()
    target_raw = run_root / args.dataset / args.sequence / args.algorithm
    target = target_raw.resolve(strict=False)
    if target.parent.parent.parent != run_root:
        raise SystemExit(f"refusing unexpected result depth: {target}")
    if run_root not in target.parents:
        raise SystemExit(f"refusing path outside result root: {target}")
    current = target_raw
    while current != run_root:
        if current.is_symlink():
            raise SystemExit(f"refusing symlink in result cell path: {current}")
        current = current.parent

    if args.dry_run:
        print(f"[results] validated cell: {target}")
        return 0
    print(f"[results] replacing cell: {target}")
    if target_raw.exists():
        if not target_raw.is_dir():
            raise SystemExit(f"refusing non-directory result cell: {target_raw}")
        shutil.rmtree(target_raw)
    target.mkdir(parents=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
