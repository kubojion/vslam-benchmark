#!/usr/bin/env python3
"""
Scan every run-type results tree and write one CSV per run type.

Usage:
    python3 build_benchmark_csv.py [run_type]

    run_type \u2208 {vo, vio, vio-lc, all}  (default: all)

Layouts:
    results/<dataset>/<seq>/<algo>/run<N>/run_eval.json    -> benchmark-vo.csv
    results-vio/<dataset>/<seq>/<algo>/run<N>/run_eval.json -> benchmark-vio.csv
    results-vio-lc/<dataset>/<seq>/<algo>/run<N>/run_eval.json -> benchmark-vio-lc.csv

Each CSV is append-only: existing rows (matched by dataset/seq/algo/duration_s)
are kept. Rows are ordered by the mtime of run_eval.json.
"""
from __future__ import annotations
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _run_type import resolve as resolve_run_type, all_types, RUN_TYPES  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DATASETS = REPO / "datasets"

ENV_TYPE: dict[str, str] = {
    "euroc_mav": "indoor",
    "hortimulti": "agricultural",
    "rosariov2": "agricultural",
}

COLUMNS = [
    # Identity
    "dataset", "seq", "environment_type", "algo",
    "run_type", "use_imu", "use_lc",
    # Sequence metadata
    "input_fps", "image_width", "image_height",
    "sequence_duration_s", "sequence_frames_total",
    # Tracking coverage (keep only the three most useful)
    "frames_tracked", "track_pct",
    "trajectory_duration_s", "trajectory_time_coverage_pct",
    # ATE SE(3) - RMSE and Max only
    "ate_se3_rmse_m", "ate_se3_max_m",
    # ATE Sim(3) - scale-corrected, RMSE and Max only
    "ate_sim3_rmse_m", "ate_sim3_max_m",
    # Scale
    "scale_factor", "scale_error_pct",
    # RPE
    "rpe_trans_1m_rmse_m", "rpe_rot_1m_rmse_deg",
    # Path length and normalised error
    "path_length_gt_m", "path_length_est_m", "ate_se3_rmse_pct_path",
    # Robustness (loop closures only)
    "loop_closures",
    # Timing
    "duration_s", "fps", "real_time_factor", "processing_ms_per_frame",
    # Resource usage
    "cpu_mean_pct", "cpu_peak_pct", "ram_mean_mib", "ram_peak_mib",
    "vram_mean_mib", "vram_peak_mib", "gpu_mean_pct", "gpu_peak_pct",
    # Agricultural segments
    "ate_row_rmse_m", "ate_turn_rmse_m", "n_segments_row", "n_segments_turn",
    # Meta
    "final_drift_m", "gt_source",
]


def _g(d: dict, *path, default=None):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur if cur is not None else default


def _round(v, n=4):
    return round(v, n) if v is not None else None


def load_seq_meta(dataset: str, seq: str) -> dict:
    """Load per-sequence metadata once (shared across all runs of that seq)."""
    seq_dir = DATASETS / dataset / seq
    meta: dict = {}

    # --- timestamps ---
    times_file = seq_dir / "times.txt"
    if times_file.exists():
        try:
            t = np.loadtxt(str(times_file)) / 1e9  # ns -> s
            n = len(t)
            dur = float(t[-1] - t[0]) if n > 1 else 0.0
            meta["sequence_frames_total"] = n
            meta["sequence_duration_s"] = _round(dur, 2)
            meta["input_fps"] = _round(n / dur if dur > 0 else 0.0, 2)
        except Exception:
            pass

    # --- image dimensions (first frame, any cam0 layout) ---
    try:
        from PIL import Image as _PIL
        for glob in ("cam0/*.png", "cam0/*.jpg",
                     "mav0/cam0/data/*.png", "mav0/cam0/data/*.jpg"):
            imgs = sorted(seq_dir.glob(glob))
            if imgs:
                img = _PIL.open(imgs[0])
                meta["image_width"], meta["image_height"] = img.size
                break
    except Exception:
        pass

    # --- GT path length ---
    for gt_name in ("gt_interp_tum.txt", "gt_tum.txt"):
        gt_file = seq_dir / gt_name
        if gt_file.exists():
            try:
                data = np.loadtxt(str(gt_file))
                xyz = data[:, 1:4]
                meta["path_length_gt_m"] = _round(
                    float(np.sum(np.linalg.norm(np.diff(xyz, axis=0), axis=1))), 2
                )
            except Exception:
                pass
            break

    return meta


def load_traj_info(traj_path: Path) -> dict:
    """Parse trajectory.txt for output-frame count, path length, and time span."""
    if not traj_path.exists():
        return {}
    try:
        data = np.loadtxt(str(traj_path))
        if data.ndim == 1:
            data = data[np.newaxis, :]
        n = len(data)
        t = data[:, 0]
        traj_dur = float(t[-1] - t[0]) if n > 1 else 0.0
        xyz = data[:, 1:4]
        path_est = float(np.sum(np.linalg.norm(np.diff(xyz, axis=0), axis=1))) if n > 1 else 0.0
        return {
            "frames_output": n,
            "path_length_est_m": _round(path_est, 2),
            "trajectory_duration_s": _round(traj_dur, 2),
        }
    except Exception:
        return {}


def row_from_eval(eval_path: Path, seq_meta: dict, rt) -> dict | None:
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
            pass

    traj_info = load_traj_info(run_dir / "trajectory.txt")

    seg = ev.get("agri_segments", {}) or {}
    row_seg = seg.get("row", {}) or {}
    turn_seg = seg.get("turn", {}) or {}
    rob = ev.get("robustness", {}) or {}
    runtime = ev.get("runtime", {}) or {}

    dataset = ds_dir.name
    seq = seq_dir.name

    # Derived: scale error
    scale = _g(ev, "scale_factor")
    scale_error_pct = _round(abs(scale - 1.0) * 100, 2) if scale is not None else None

    # Derived: ATE as % of path
    ate_se3_rmse = _g(ev, "ate_se3", "rmse")
    path_gt = seq_meta.get("path_length_gt_m")
    ate_pct_path = _round(ate_se3_rmse / path_gt * 100, 2) if (ate_se3_rmse and path_gt) else None

    # Derived: timing
    wall_s = runtime.get("wall_s") or _g(meta, "duration_s")
    fps_val = runtime.get("fps") or _g(meta, "fps")
    seq_dur = seq_meta.get("sequence_duration_s")
    rtf = _round(seq_dur / wall_s, 3) if (seq_dur and wall_s) else None
    frames_tracked = rob.get("frames_tracked") or _g(meta, "frames")
    ms_per_frame = _round(wall_s * 1000 / frames_tracked, 2) if (wall_s and frames_tracked) else None

    # Derived: trajectory coverage
    seq_frames_total = seq_meta.get("sequence_frames_total")
    n_pairs = ev.get("n_pairs_ate")
    ate_cov_pct = _round(n_pairs / seq_frames_total * 100, 1) if (n_pairs and seq_frames_total) else None
    traj_dur = traj_info.get("trajectory_duration_s")
    traj_time_cov = _round(traj_dur / seq_dur * 100, 1) if (traj_dur and seq_dur) else None

    # run_status
    output_valid = rob.get("output_valid", True)
    run_status = "ok" if output_valid else "failed"

    return {
        "dataset": dataset,
        "seq": seq,
        "environment_type": ENV_TYPE.get(dataset, "unknown"),
        "algo": algo_dir.name,
        "run_type": rt.name,
        "use_imu": rt.use_imu,
        "use_lc": rt.use_lc,
        "run": run_dir.name.replace("run", ""),
        "run_status": run_status,
        # Sequence
        "input_fps": seq_meta.get("input_fps"),
        "image_width": seq_meta.get("image_width"),
        "image_height": seq_meta.get("image_height"),
        "sequence_duration_s": seq_meta.get("sequence_duration_s"),
        "sequence_frames_total": seq_frames_total,
        # Coverage
        "frames_output": traj_info.get("frames_output"),
        "frames_tracked": frames_tracked,
        "frames_total": rob.get("frames_total"),
        "track_pct": rob.get("track_pct"),
        "n_pairs_ate": n_pairs,
        "ate_pair_coverage_pct": ate_cov_pct,
        "trajectory_duration_s": traj_dur,
        "trajectory_time_coverage_pct": traj_time_cov,
        # ATE SE(3)
        "ate_se3_rmse_m": _g(ev, "ate_se3", "rmse"),
        "ate_se3_mean_m": _g(ev, "ate_se3", "mean"),
        "ate_se3_median_m": _g(ev, "ate_se3", "median"),
        "ate_se3_std_m": _g(ev, "ate_se3", "std"),
        "ate_se3_max_m": _g(ev, "ate_se3", "max"),
        # ATE Sim(3)
        "ate_sim3_rmse_m": _g(ev, "ate", "rmse"),
        "ate_sim3_mean_m": _g(ev, "ate", "mean"),
        "ate_sim3_median_m": _g(ev, "ate", "median"),
        "ate_sim3_std_m": _g(ev, "ate", "std"),
        "ate_sim3_max_m": _g(ev, "ate", "max"),
        # Scale
        "scale_factor": scale,
        "scale_error_pct": scale_error_pct,
        # RPE
        "rpe_trans_1m_rmse_m": _g(ev, "rpe_trans_1m", "rmse"),
        "rpe_rot_1m_rmse_deg": _g(ev, "rpe_rot_1m_deg", "rmse"),
        # KITTI
        "kitti_10m_trans_rmse_m": _g(ev, "kitti_drift", "rpe_10m_trans_rmse"),
        "kitti_50m_trans_rmse_m": _g(ev, "kitti_drift", "rpe_50m_trans_rmse"),
        "kitti_100m_trans_rmse_m": _g(ev, "kitti_drift", "rpe_100m_trans_rmse"),
        # Path
        "path_length_gt_m": path_gt,
        "path_length_est_m": traj_info.get("path_length_est_m"),
        "ate_se3_rmse_pct_path": ate_pct_path,
        # Robustness
        "loop_closures": rob.get("loop_closures"),
        "tracking_losses": rob.get("tracking_losses"),
        "map_resets": rob.get("map_resets"),
        "init_success": rob.get("init_success"),
        "init_time_s": rob.get("init_time_s"),
        "first_failure_s": rob.get("first_failure_s"),
        # Timing
        "duration_s": wall_s,
        "fps": fps_val,
        "real_time_factor": rtf,
        "processing_ms_per_frame": ms_per_frame,
        # Resources
        "cpu_mean_pct": runtime.get("cpu_mean_pct"),
        "cpu_peak_pct": runtime.get("cpu_peak_pct"),
        "ram_mean_mib": runtime.get("ram_mean_mib"),
        "ram_peak_mib": runtime.get("ram_peak_mib"),
        "vram_mean_mib": runtime.get("vram_mean_mib"),
        "vram_peak_mib": runtime.get("vram_peak_mib"),
        "gpu_mean_pct": runtime.get("gpu_mean_pct"),
        "gpu_peak_pct": runtime.get("gpu_peak_pct"),
        # Agricultural segments
        "ate_row_rmse_m": row_seg.get("ate_rmse_mean"),
        "ate_turn_rmse_m": turn_seg.get("ate_rmse_mean"),
        "n_segments_row": row_seg.get("n_segments"),
        "n_segments_turn": turn_seg.get("n_segments"),
        # Meta
        "final_drift_m": _g(ev, "final_drift_m"),
        "gt_source": _g(ev, "gt_source"),
        "eval_mtime": int(eval_path.stat().st_mtime),
    }


def load_existing_keys(csv_path: Path) -> set[tuple]:
    if not csv_path.exists():
        return set()
    keys = set()
    with csv_path.open() as f:
        for r in csv.DictReader(f):
            # Use (dataset, seq, algo, duration_s) as proxy key since `run` is no longer a column.
            keys.add((r["dataset"], r["seq"], r["algo"], r.get("duration_s", "")))
    return keys


def build_one(rt) -> int:
    """Scan one results tree and append new rows to its CSV. Returns row count added."""
    results_root = rt.results_root
    csv_path = rt.csv_path
    if not results_root.is_dir():
        print(f"[info] {rt.name}: results dir missing ({results_root}), skipping")
        return 0

    eval_files = sorted(
        results_root.glob("*/*/*/run*/run_eval.json"),
        key=lambda p: p.stat().st_mtime,
    )
    if not eval_files:
        print(f"[info] {rt.name}: no run_eval.json under {results_root}")
        # Still ensure header exists if file missing
        if not csv_path.exists():
            with csv_path.open("w", newline="") as f:
                csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore").writeheader()
        return 0

    # Pre-load sequence metadata
    seq_meta_cache: dict[tuple, dict] = {}
    for ep in eval_files:
        seq_dir = ep.parent.parent.parent
        ds_dir = seq_dir.parent
        key = (ds_dir.name, seq_dir.name)
        if key not in seq_meta_cache:
            seq_meta_cache[key] = load_seq_meta(ds_dir.name, seq_dir.name)

    existing = load_existing_keys(csv_path)
    new_rows = []
    for ep in eval_files:
        seq_dir = ep.parent.parent.parent
        ds_dir = seq_dir.parent
        sm = seq_meta_cache.get((ds_dir.name, seq_dir.name), {})
        row = row_from_eval(ep, sm, rt)
        if row is None:
            continue
        key = (row["dataset"], row["seq"], row["algo"], str(row.get("duration_s", "")))
        if key in existing:
            continue
        new_rows.append(row)

    write_header = not csv_path.exists()
    if not new_rows:
        print(f"[info] {rt.name}: no new rows ({csv_path.name} has {len(existing)} entries)")
        if write_header:
            with csv_path.open("w", newline="") as f:
                csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore").writeheader()
        return 0

    with csv_path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        if write_header:
            w.writeheader()
        for r in new_rows:
            w.writerow(r)

    print(f"[ok] {rt.name}: appended {len(new_rows)} row(s) to {csv_path.name}")
    for r in new_rows:
        run_label = f"run{r.get('run', '?')}"
        print(f"      + {r['dataset']}/{r['seq']}/{r['algo']}/{run_label}  ATE Sim3={r['ate_sim3_rmse_m']}")
    return len(new_rows)


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target == "all":
        types = all_types(REPO)
    elif target in RUN_TYPES:
        types = [resolve_run_type(target, REPO)]
    else:
        print(f"Usage: {sys.argv[0]} [vo|vio|vio-lc|all]", file=sys.stderr)
        return 1

    total = 0
    for rt in types:
        total += build_one(rt)
    print(f"[done] {total} new row(s) added across {len(types)} CSV(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
