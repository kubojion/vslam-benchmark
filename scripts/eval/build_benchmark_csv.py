#!/usr/bin/env python3
"""
Scan results/ and append every per-run evaluation into a flat CSV.

Layout assumed (produced by scripts/run/run_benchmark.sh):
    results/<dataset>/<seq>/<algo>/run<N>/run_eval.json
    results/<dataset>/<seq>/<algo>/run<N>/run_meta.json   (optional)

Output:
    benchmark.csv at the repo root, one row per (dataset, seq, algo, run).

This script is read-only on results/. It appends new rows to benchmark.csv;
existing rows are kept. Rows are ordered by the mtime of run_eval.json
(chronological evaluation time).
"""
from __future__ import annotations
import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "results"
CSV_PATH = REPO / "benchmark.csv"

COLUMNS = [
    "dataset", "seq", "algo", "run",
    "frames",
    "ate_sim3_rmse_m", "ate_se3_rmse_m", "scale_factor",
    "rpe_trans_rmse_mpm", "rpe_rot_rmse_dpm",
    "ate_row_rmse_m", "ate_turn_rmse_m",
    "n_segments_row", "n_segments_turn",
    "loops", "duration_s", "fps",
    "final_drift_m", "gt_source",
    "eval_mtime",
]


def _g(d: dict, *path, default=None):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur if cur is not None else default


def row_from_eval(eval_path: Path) -> dict | None:
    try:
        ev = json.loads(eval_path.read_text())
    except Exception as e:
        print(f"[warn] could not parse {eval_path}: {e}", file=sys.stderr)
        return None
    run_dir = eval_path.parent
    algo_dir = run_dir.parent
    seq_dir = algo_dir.parent
    ds_dir = seq_dir.parent

    meta_path = run_dir / "run_meta.json"
    meta = {}
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text())
        except Exception:
            meta = {}

    seg = ev.get("agri_segments", {}) or {}
    row_seg = seg.get("row", {}) or {}
    turn_seg = seg.get("turn", {}) or {}
    rob = ev.get("robustness", {}) or {}
    rt = ev.get("runtime", {}) or {}

    return {
        "dataset": ds_dir.name,
        "seq": seq_dir.name,
        "algo": algo_dir.name,
        "run": run_dir.name.replace("run", ""),
        "frames": rob.get("frames_total") or _g(meta, "frames"),
        "ate_sim3_rmse_m": _g(ev, "ate", "rmse"),
        "ate_se3_rmse_m": _g(ev, "ate_se3", "rmse"),
        "scale_factor": _g(ev, "scale_factor"),
        "rpe_trans_rmse_mpm": _g(ev, "rpe_trans_1m", "rmse"),
        "rpe_rot_rmse_dpm": _g(ev, "rpe_rot_1m_deg", "rmse"),
        "ate_row_rmse_m": row_seg.get("ate_rmse_mean"),
        "ate_turn_rmse_m": turn_seg.get("ate_rmse_mean"),
        "n_segments_row": row_seg.get("n_segments"),
        "n_segments_turn": turn_seg.get("n_segments"),
        "loops": rob.get("loop_closures"),
        "duration_s": rt.get("wall_s") or _g(meta, "duration_s"),
        "fps": rt.get("fps") or _g(meta, "fps"),
        "final_drift_m": _g(ev, "final_drift_m"),
        "gt_source": _g(ev, "gt_source"),
        "eval_mtime": int(eval_path.stat().st_mtime),
    }


def load_existing_keys() -> set[tuple]:
    if not CSV_PATH.exists():
        return set()
    keys = set()
    with CSV_PATH.open() as f:
        for r in csv.DictReader(f):
            keys.add((r["dataset"], r["seq"], r["algo"], r["run"]))
    return keys


def main() -> int:
    if not RESULTS.is_dir():
        print(f"[err] no results dir at {RESULTS}", file=sys.stderr)
        return 1
    eval_files = sorted(
        RESULTS.glob("*/*/*/run*/run_eval.json"),
        key=lambda p: p.stat().st_mtime,
    )
    if not eval_files:
        print("[info] no run_eval.json files found")
        return 0

    existing = load_existing_keys()
    new_rows = []
    for ep in eval_files:
        row = row_from_eval(ep)
        if row is None:
            continue
        key = (row["dataset"], row["seq"], row["algo"], row["run"])
        if key in existing:
            continue
        new_rows.append(row)

    write_header = not CSV_PATH.exists()
    if not new_rows:
        print(f"[info] no new rows (benchmark.csv has {len(existing)} entries)")
        return 0

    with CSV_PATH.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        if write_header:
            w.writeheader()
        for r in new_rows:
            w.writerow(r)

    print(f"[ok] appended {len(new_rows)} row(s) to {CSV_PATH}")
    for r in new_rows:
        print(f"      + {r['dataset']}/{r['seq']}/{r['algo']}/run{r['run']}  ATE Sim3={r['ate_sim3_rmse_m']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
