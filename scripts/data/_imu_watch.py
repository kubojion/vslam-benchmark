#!/usr/bin/env python3
"""Watch for imu0/data.csv to appear and update TODO.md automatically."""
import sys
import time
import re
from pathlib import Path

WS = Path(__file__).resolve().parents[2]
TODO = WS / "TODO.md"

FILES = {
    "strawberry02": WS / "datasets/hortimulti/strawberry02/mav0/imu0/data.csv",
    "strawberry03": WS / "datasets/hortimulti/strawberry03/mav0/imu0/data.csv",
}

def wait_for(path, label):
    print(f"[imu_watch] waiting for {label}: {path}", flush=True)
    while not path.exists() or path.stat().st_size == 0:
        time.sleep(10)
    n = sum(1 for _ in open(path)) - 1  # subtract header
    print(f"[imu_watch] {label} done: {n} samples", flush=True)
    return n


def update_todo(counts):
    text = TODO.read_text()
    original = text

    # Replace all ⏳ imu-pending in hortimulti str02/str03 columns -> ⬜ ready
    # Tables use fixed column order; every ⏳ imu-pending cell is hortimulti
    text = re.sub(r"⏳ imu-pending", "⬜ ready", text)

    # Update the extraction note in VIO table
    text = text.replace(
        "> HortiMulti IMU: bags available at `/media/jion_kubo/Buffalo\\ SSD/datasets/`. "
        "Extraction running via `--imu-only` flag. All ⏳ cells become ⬜ once `imu0/data.csv` lands.",
        f"> HortiMulti IMU: extracted - "
        f"str02={counts['strawberry02']} samples, str03={counts['strawberry03']} samples. "
        f"Path: `datasets/hortimulti/strawberry{{02,03}}/mav0/imu0/data.csv`"
    )

    # Update the extraction note in VIO-LC table
    text = text.replace(
        "> HortiMulti ⏳ cells: IMU extraction running, configs created. Unblock once `imu0/data.csv` lands.",
        f"> HortiMulti IMU: extracted. Path: `datasets/hortimulti/strawberry{{02,03}}/mav0/imu0/data.csv`"
    )

    # Mark task #1 done: [~] -> [x] for VIO hortimulti tasks
    text = re.sub(
        r"(\| VIO hortimulti \(after IMU extraction\) \| )`\[~\]`",
        r"\1`[x]`",
        text
    )
    text = re.sub(
        r"(\| VIO/VI-SLAM hortimulti \(after IMU extraction\) \| )`\[~\]`",
        r"\1`[x]`",
        text
    )

    if text == original:
        print("[imu_watch] WARNING: no changes made to TODO.md - patterns may have changed", flush=True)
    else:
        TODO.write_text(text)
        print(f"[imu_watch] TODO.md updated", flush=True)


if __name__ == "__main__":
    import threading

    counts = {}
    threads = []

    def watch(label, path):
        counts[label] = wait_for(path, label)

    for label, path in FILES.items():
        t = threading.Thread(target=watch, args=(label, path))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("[imu_watch] both files ready - updating TODO.md ...", flush=True)
    update_todo(counts)
    print("[imu_watch] done", flush=True)
