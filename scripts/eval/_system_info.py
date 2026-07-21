#!/usr/bin/env python3
"""Collect the host's hardware/OS specs for provenance of benchmark results.

Dependency-free: uses only the standard library, /proc, and nvidia-smi (if
present). Every result's runtime numbers (FPS, CPU%, GPU%, RAM) are
machine-dependent, so run_eval.json embeds this block under "machine" to record
*which* machine produced them - it does not change any metric.

Usage:
    python3 scripts/eval/_system_info.py            # prints JSON
    from _system_info import collect; collect()     # returns a dict
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess


def _cpu_model() -> str:
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown"


def _cpu_cores() -> dict:
    logical = os.cpu_count() or 0
    physical = None
    try:
        ids = set()
        cur = {}
        for line in open("/proc/cpuinfo"):
            if line.strip() == "":
                if "physical id" in cur and "core id" in cur:
                    ids.add((cur["physical id"], cur["core id"]))
                cur = {}
            elif ":" in line:
                k, v = line.split(":", 1)
                cur[k.strip()] = v.strip()
        if ids:
            physical = len(ids)
    except OSError:
        pass
    return {"physical": physical, "logical": logical}


def _ram_total_gb() -> float | None:
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemTotal"):
                kb = float(line.split()[1])
                return round(kb / (1024.0 * 1024.0), 1)
    except OSError:
        pass
    return None


def _os_pretty() -> str:
    try:
        for line in open("/etc/os-release"):
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return platform.platform()


def _gpus() -> list:
    if not shutil.which("nvidia-smi"):
        return []
    try:
        out = subprocess.run(
            ["nvidia-smi",
             "--query-gpu=name,memory.total,driver_version",
             "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10,
        )
        gpus = []
        for line in out.stdout.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 3:
                gpus.append({"name": parts[0], "memory": parts[1],
                             "driver": parts[2]})
        return gpus
    except (OSError, subprocess.SubprocessError):
        return []


def collect() -> dict:
    """Return a machine-spec dict. Never raises - fields fall back to None.

    Deliberately excludes hostname/username - only non-identifying hardware/OS
    specs, so results can carry provenance without leaking who ran them.
    """
    return {
        "os": _os_pretty(),
        "kernel": platform.release(),
        "cpu": _cpu_model(),
        "cpu_cores": _cpu_cores(),
        "ram_total_gb": _ram_total_gb(),
        "gpus": _gpus(),
        "python": platform.python_version(),
    }


if __name__ == "__main__":
    print(json.dumps(collect(), indent=2))
