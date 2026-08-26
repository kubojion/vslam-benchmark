#!/usr/bin/env python3
"""Sample resources for an estimator process tree and/or Docker container.

The old monitor sampled the entire GPU and host.  Those numbers included Xorg,
unrelated containers, filesystem cache, and every other user process, so they
were unsuitable for algorithm comparisons.  This monitor only accounts for
the explicitly selected PID trees and container PIDs.

Usage::

    _resource_monitor.py resources.csv --pid 1234 [--container name] [--interval 1]

``--pid`` and ``--container`` are repeatable and may be combined for hybrid
pipelines such as a Docker estimator plus host-side ROS fusion nodes.  The
monitor runs until SIGINT/SIGTERM, matching the existing runner lifecycle.
Unavailable driver metrics are written as empty cells, never as fabricated
zeroes.
"""

from __future__ import annotations

import argparse
import csv
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

STOP = False
CLOCK_TICKS = os.sysconf("SC_CLK_TCK")
PAGE_SIZE = os.sysconf("SC_PAGE_SIZE")


def _stop(_signum, _frame) -> None:
    global STOP
    STOP = True


def _command(args: list[str], timeout: float = 2.0) -> str | None:
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=timeout, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout if result.returncode == 0 else None


def container_pids(container: str) -> set[int]:
    """Return host PIDs currently belonging to *container*."""
    raw = _command(["docker", "top", container, "-eo", "pid"])
    if not raw:
        return set()
    result: set[int] = set()
    for line in raw.splitlines()[1:]:
        token = line.strip().split(maxsplit=1)[0] if line.strip() else ""
        try:
            result.add(int(token))
        except ValueError:
            continue
    return result


def process_tree_pids(roots: list[int]) -> set[int]:
    """Resolve descendants from Linux /proc without interpreter packages."""
    parents: dict[int, int] = {}
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            rest = (entry / "stat").read_text().rsplit(")", 1)[1].split()
            parents[int(entry.name)] = int(rest[1])
        except (OSError, ValueError, IndexError):
            continue
    result = {pid for pid in roots if pid in parents}
    changed = True
    while changed:
        changed = False
        for pid, parent in parents.items():
            if parent in result and pid not in result:
                result.add(pid)
                changed = True
    return result


def process_stats(pids: set[int], excluded: set[int]) -> tuple[float, float, int]:
    """Return cumulative CPU seconds, aggregate RSS MiB and live PID count."""
    cpu_seconds = 0.0
    rss_bytes = 0
    count = 0
    for pid in sorted(pids - excluded):
        try:
            rest = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
            statm = Path(f"/proc/{pid}/statm").read_text().split()
            cpu_seconds += (int(rest[11]) + int(rest[12])) / CLOCK_TICKS
            rss_bytes += int(statm[1]) * PAGE_SIZE
            count += 1
        except (OSError, ValueError, IndexError):
            continue
    return cpu_seconds, rss_bytes / (1024.0 * 1024.0), count


def gpu_memory_by_pid() -> dict[int, float] | None:
    raw = _command([
        "nvidia-smi", "--query-compute-apps=pid,used_memory",
        "--format=csv,noheader,nounits",
    ])
    if raw is None:
        return None
    values: dict[int, float] = {}
    for line in raw.splitlines():
        fields = [field.strip() for field in line.split(",")]
        if len(fields) < 2:
            continue
        try:
            values[int(fields[0])] = values.get(int(fields[0]), 0.0) + float(fields[1])
        except ValueError:
            continue
    return values


def gpu_util_by_pid() -> dict[int, float] | None:
    """Read one NVIDIA pmon sample; return None when unsupported."""
    raw = _command(["nvidia-smi", "pmon", "-c", "1", "-s", "u"], timeout=4.0)
    if raw is None:
        return None
    values: dict[int, float] = {}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.split()
        # pmon columns: gpu pid type sm mem enc dec jpg ofa command
        if len(fields) < 4 or fields[1] == "-":
            continue
        try:
            pid = int(fields[1])
            sm = float(fields[3])
        except ValueError:
            continue
        values[pid] = values.get(pid, 0.0) + sm
    return values


def selected_gpu_value(values: dict[int, float] | None, pids: set[int]) -> float | None:
    if values is None:
        return None
    return sum(value for pid, value in values.items() if pid in pids)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("output", type=Path)
    p.add_argument("legacy_interval", nargs="?", type=float, help=argparse.SUPPRESS)
    p.add_argument("--interval", type=float, default=None)
    p.add_argument("--pid", type=int, action="append", default=[])
    p.add_argument("--container", action="append", default=[])
    p.add_argument("--label", default="estimator_pipeline")
    p.add_argument("--start-file", type=Path)
    p.add_argument("--stop-file", type=Path)
    return p


def main() -> int:
    args = parser().parse_args()
    interval = args.interval if args.interval is not None else (args.legacy_interval or 1.0)
    if interval <= 0:
        raise SystemExit("--interval must be positive")
    if not args.pid and not args.container:
        raise SystemExit("select at least one --pid or --container; whole-system sampling is forbidden")

    while args.start_file and not args.start_file.exists() and not STOP:
        time.sleep(0.05)
    if STOP:
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    excluded = {os.getpid()}
    started = time.monotonic()
    previous_wall = started
    previous_cpu: float | None = None
    scope = "+".join(filter(None, [
        "process_tree" if args.pid else "",
        "container" if args.container else "",
    ]))

    with args.output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "t_s", "scope", "label", "target_available", "process_count",
            "cpu_pct", "cpu_time_s", "ram_mib", "vram_mib", "gpu_util_pct",
        ])
        writer.writeheader()
        while not STOP and not (args.stop_file and args.stop_file.exists()):
            now = time.monotonic()
            pids = process_tree_pids(args.pid)
            for container in args.container:
                pids.update(container_pids(container))
            cpu_seconds, rss_mib, count = process_stats(pids, excluded)
            if previous_cpu is None or now <= previous_wall:
                cpu_pct: float | None = None
            else:
                # Process CPU percentage may exceed 100 on multicore systems.
                cpu_pct = 100.0 * max(0.0, cpu_seconds - previous_cpu) / (now - previous_wall)
            previous_cpu = cpu_seconds
            previous_wall = now

            gpu_memory = selected_gpu_value(gpu_memory_by_pid(), pids)
            gpu_util = selected_gpu_value(gpu_util_by_pid(), pids)
            writer.writerow({
                "t_s": f"{now - started:.3f}",
                "scope": scope,
                "label": args.label,
                "target_available": "true" if count else "false",
                "process_count": count,
                "cpu_pct": "" if cpu_pct is None else f"{cpu_pct:.3f}",
                "cpu_time_s": f"{cpu_seconds:.6f}",
                "ram_mib": f"{rss_mib:.3f}",
                "vram_mib": "" if gpu_memory is None else f"{gpu_memory:.3f}",
                "gpu_util_pct": "" if gpu_util is None else f"{gpu_util:.3f}",
            })
            stream.flush()
            deadline = now + interval
            while (
                not STOP and not (args.stop_file and args.stop_file.exists())
                and time.monotonic() < deadline
            ):
                time.sleep(min(0.1, max(0.0, deadline - time.monotonic())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
