#!/usr/bin/env python3
"""Validate/create a result cell without deleting any existing attempt."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


RUN_TYPES = {"vo", "vo-lc", "vio", "vio-lc", "gnss-vio"}
COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


def component(value: str) -> str:
    if not COMPONENT.fullmatch(value) or value in {".", ".."}:
        raise argparse.ArgumentTypeError(f"unsafe path component: {value!r}")
    return value


def validate_cell(repo, run_type, dataset, sequence, algorithm):
    if run_type not in RUN_TYPES:
        raise ValueError('unknown run type')
    for value in (dataset, sequence, algorithm):
        component(value)
    repo = Path(repo).resolve()
    target = repo/'results'/run_type/dataset/sequence/algorithm
    for current in (target, *target.parents):
        if current == repo:
            break
        if current.is_symlink():
            raise ValueError(f'refusing symlink in result cell path: {current}')
        if current.exists() and not current.is_dir():
            raise ValueError(f'refusing non-directory result path: {current}')
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("run_type", choices=sorted(RUN_TYPES))
    parser.add_argument("dataset", type=component)
    parser.add_argument("sequence", type=component)
    parser.add_argument("algorithm", type=component)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    target = validate_cell(args.repo, args.run_type, args.dataset, args.sequence, args.algorithm)

    if args.dry_run:
        print(f"[results] validated cell: {target}")
        return 0
    print(f"[results] preserving cell: {target}")
    target.mkdir(parents=True, exist_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
