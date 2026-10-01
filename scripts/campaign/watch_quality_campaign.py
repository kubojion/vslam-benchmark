#!/usr/bin/env python3
"""Watch an in-progress quality campaign and terminate overlong cells.

This is intentionally separate from the campaign controller so it can also
protect a controller that was started before the controller's own timeout
support was installed.  It kills only the matching run_benchmark.sh subtree,
never the controller process itself.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import signal
import time


REPO = Path(__file__).resolve().parents[2]


def process_snapshot() -> dict[int, tuple[int, str]]:
    result: dict[int, tuple[int, str]] = {}
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            stat = (entry / "stat").read_text()
            # The comm field may contain spaces/parentheses; parse after the
            # final ')' where the state and parent-PID fields begin.
            tail = stat.rsplit(")", 1)[1].split()
            ppid = int(tail[1])
            raw_cmdline = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
            cmdline = raw_cmdline.strip() or stat
            result[int(entry.name)] = (ppid, cmdline)
        except (FileNotFoundError, PermissionError, ValueError, IndexError):
            continue
    return result


def descendants(snapshot: dict[int, tuple[int, str]], root: int) -> list[int]:
    children: dict[int, list[int]] = {}
    for pid, (ppid, _) in snapshot.items():
        children.setdefault(ppid, []).append(pid)
    result: list[int] = []
    stack = list(children.get(root, []))
    while stack:
        pid = stack.pop()
        result.append(pid)
        stack.extend(children.get(pid, []))
    return result


def find_controller(snapshot: dict[int, tuple[int, str]], campaign_id: str) -> int | None:
    marker = f"run_quality_campaign.py"
    for pid, (_, cmdline) in snapshot.items():
        argv0 = cmdline.split(maxsplit=1)[0] if cmdline else ""
        if (
            Path(argv0).name in {"python", "python3"}
            and marker in cmdline
            and campaign_id in cmdline
        ):
            return pid
    return None


def terminate_tree(root: int, snapshot: dict[int, tuple[int, str]]) -> None:
    targets = descendants(snapshot, root) + [root]
    for pid in reversed(targets):
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        live = [pid for pid in targets if Path(f"/proc/{pid}").exists()]
        if not live:
            return
        time.sleep(0.25)
    for pid in targets:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def parse_started(value: str) -> float:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z").timestamp()


def watch(state_path: Path, timeout_s: float, interval_s: float) -> int:
    log_path = state_path.with_name("watchdog.log")
    campaign_id = state_path.parent.name
    while True:
        try:
            state = json.loads(state_path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            time.sleep(interval_s)
            continue
        running = [
            (key, value) for key, value in state.get("cells", {}).items()
            if value.get("status") == "running"
        ]
        if not running:
            if state.get("status") == "complete":
                return 0
            if find_controller(process_snapshot(), campaign_id) is None:
                # The controller has exited (possibly with failed/timeout
                # cells); there is no live process left for this watcher to
                # protect.
                return 0
            time.sleep(interval_s)
            continue
        now = time.time()
        snapshot = process_snapshot()
        controller = find_controller(snapshot, campaign_id)
        for key, entry in running:
            try:
                age = now - parse_started(entry["started_at"])
            except (KeyError, ValueError):
                continue
            if age <= timeout_s:
                continue
            message = f"{time.strftime('%Y-%m-%dT%H:%M:%S%z')} timeout key={key} age_s={age:.1f}"
            if controller is None:
                message += " controller_not_found"
            else:
                candidates = [
                    pid for pid in descendants(snapshot, controller)
                    if "scripts/run/run_benchmark.sh" in snapshot[pid][1]
                    and all(part in snapshot[pid][1] for part in key.split("/"))
                ]
                if len(candidates) == 1:
                    terminate_tree(candidates[0], snapshot)
                    message += f" terminated_pid={candidates[0]}"
                else:
                    message += f" runner_candidates={candidates}"
            with log_path.open("a") as log:
                log.write(message + "\n")
            print(message, flush=True)
        time.sleep(interval_s)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--timeout-s", type=float, default=21600.0)
    parser.add_argument("--interval-s", type=float, default=30.0)
    args = parser.parse_args()
    if args.timeout_s <= 0 or args.interval_s <= 0:
        parser.error("--timeout-s and --interval-s must be positive")
    return watch(args.state.resolve(), args.timeout_s, args.interval_s)


if __name__ == "__main__":
    raise SystemExit(main())
