#!/usr/bin/env python3
"""Sample GPU (via nvidia-smi), CPU%, and RAM every INTERVAL seconds into a CSV.

Usage:
    python3 _resource_monitor.py <out.csv> [interval_s=1]

Replaces _gpu_monitor.sh and adds CPU + RAM columns.
Output columns: t_s, vram_mib, gpu_util_pct, cpu_pct, ram_mib
"""
import sys
import time
import csv
import subprocess

out_path = sys.argv[1]
interval = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0


def get_gpu():
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used,utilization.gpu",
             "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL
        ).decode()
        parts = out.strip().split(",")
        return float(parts[0].strip()), float(parts[1].strip())
    except Exception:
        return 0.0, 0.0


def get_cpu_ram():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().used / (1024.0 * 1024.0)
        return cpu, ram
    except ImportError:
        pass
    # Fallback: parse /proc/meminfo for RAM (no CPU without psutil)
    try:
        mem = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k, v = line.split(":")
                mem[k.strip()] = int(v.split()[0])
        ram = (mem["MemTotal"] - mem["MemAvailable"]) / 1024.0
        return 0.0, ram
    except Exception:
        return 0.0, 0.0


# Prime psutil CPU counter (first call always returns 0)
try:
    import psutil as _p
    _p.cpu_percent()
    time.sleep(0.2)
except ImportError:
    pass

start = time.time()
with open(out_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["t_s", "vram_mib", "gpu_util_pct", "cpu_pct", "ram_mib"])
    while True:
        t = time.time() - start
        vram, gpu_util = get_gpu()
        cpu, ram = get_cpu_ram()
        writer.writerow([
            f"{t:.1f}",
            f"{vram:.0f}",
            f"{gpu_util:.0f}",
            f"{cpu:.1f}",
            f"{ram:.0f}",
        ])
        f.flush()
        time.sleep(interval)
