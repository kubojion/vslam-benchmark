#!/usr/bin/env python3
"""Restore timestamps on OV2SLAM's optimized loop-closed trajectory."""
from __future__ import annotations

import argparse
from pathlib import Path


def load_rows(path: Path):
    rows = []
    for line in path.read_text().splitlines():
        fields = line.split()
        if not fields or fields[0].startswith("#"):
            continue
        if len(fields) != 8:
            raise ValueError(f"{path}: expected 8 fields, got {len(fields)}")
        rows.append(fields)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path, help="timestamped ov2slam_traj.txt")
    parser.add_argument("optimized", type=Path, help="indexed post-LC trajectory")
    parser.add_argument("output", type=Path, help="output TUM trajectory")
    args = parser.parse_args()

    raw = load_rows(args.raw)
    optimized = load_rows(args.optimized)
    if len(raw) != len(optimized):
        raise SystemExit(
            f"trajectory length mismatch: raw={len(raw)} optimized={len(optimized)}"
        )

    with args.output.open("w") as stream:
        for raw_row, optimized_row in zip(raw, optimized):
            stream.write(" ".join([raw_row[0], *optimized_row[1:]]) + "\n")

    print(f"[ov2slam] restored {len(raw)} timestamps -> {args.output}")


if __name__ == "__main__":
    main()
