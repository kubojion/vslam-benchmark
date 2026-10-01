#!/usr/bin/env python3
"""Canonicalize ORB-SLAM3's EuRoC trajectory without hiding bad poses.

The ORB-SLAM3 EuRoC examples write timestamps in nanoseconds and can repeat
the last timestamp/pose while tracking is lost.  evo requires strictly
increasing timestamps.  This helper removes only byte-equivalent numeric pose
duplicates at the same timestamp; conflicting duplicates and time reversal
remain hard failures.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


class TrajectoryError(ValueError):
    """The source trajectory cannot be canonicalized safely."""


def canonicalize(source: Path, destination: Path) -> dict[str, int | str]:
    raw_rows = 0
    output_rows = 0
    duplicates = 0
    previous: tuple[float, ...] | None = None

    with source.open() as input_stream, destination.open("w") as output_stream:
        for line_number, line in enumerate(input_stream, 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            fields = line.split()
            if len(fields) < 8:
                raise TrajectoryError(
                    f"line {line_number}: expected at least 8 columns, got {len(fields)}"
                )
            try:
                row = tuple(float(value) for value in fields[:8])
            except ValueError as exc:
                raise TrajectoryError(f"line {line_number}: non-numeric pose") from exc
            if not all(math.isfinite(value) for value in row):
                raise TrajectoryError(f"line {line_number}: non-finite pose")

            raw_rows += 1
            if previous is not None:
                if row[0] < previous[0]:
                    raise TrajectoryError(
                        f"line {line_number}: timestamp decreased ({row[0]} < {previous[0]})"
                    )
                if row[0] == previous[0]:
                    if row[1:] != previous[1:]:
                        raise TrajectoryError(
                            f"line {line_number}: duplicate timestamp has conflicting pose"
                        )
                    duplicates += 1
                    continue

            output_stream.write(
                f"{row[0] / 1e9:.9f} " + " ".join(fields[1:8]) + "\n"
            )
            previous = row
            output_rows += 1

    if output_rows < 2:
        raise TrajectoryError(f"trajectory contains only {output_rows} unique poses")

    return {
        "policy": "drop_exact_duplicate_timestamp_pose_rows",
        "raw_rows": raw_rows,
        "output_rows": output_rows,
        "exact_duplicates_removed": duplicates,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--stats", type=Path)
    args = parser.parse_args()

    try:
        stats = canonicalize(args.source, args.destination)
    except (OSError, TrajectoryError) as exc:
        args.destination.unlink(missing_ok=True)
        parser.error(str(exc))

    encoded = json.dumps(stats, sort_keys=True)
    if args.stats:
        args.stats.write_text(json.dumps(stats, indent=2) + "\n")
    print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
