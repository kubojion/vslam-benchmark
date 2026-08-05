#!/usr/bin/env python3
"""
Scan every run-type results tree and write one CSV per run type.

Usage:
    python3 build_benchmark_csv.py [run_type]

    run_type ∈ {vo, vo-lc, vio, vio-lc, gnss-vio, all}  (default: all)

Layouts:
    results-<type>/<dataset>/<seq>/<algo>/run<N>[_variant]/run_eval.json
        -> benchmark-<type>.csv

Rebuilt 2026-08-05 (see PROGRESS "aggregation fixes"):
  * FULL REBUILD every time. The old builder was append-only, deduped by
    (dataset, seq, algo, duration_s) — re-evaluated runs were silently skipped
    (stale rows survived every metric fix) and GNSS input-variant runs sharing
    a duration were silently dropped. Now the CSV is always regenerated from
    every run_eval.json on disk, deterministically sorted. results/ -> CSV is
    the only path; never hand-edit a benchmark CSV.
  * `run` and `gnss_variant` are columns: run1_conventional_gps -> run "1",
    variant "conventional_gps"; plain run1 -> variant "default".
  * `run_status` is computed for every row (also for legacy run_eval.json
    files): ok / scale_collapse (Sim3 scale <0.1 or >10) / eval_failed.
  * `coverage_gap_pct` — the single gap-aware coverage metric (_coverage.py) —
    is computed here from trajectory.txt for every row.
  * machine_cpu / machine_gpu recorded from run_eval.json's machine block.
  * Sequence metadata falls back to scripts/eval/_seq_meta_cache.json when
    datasets/<ds>/<seq> is not present on this machine.
  * zed2i is classified agricultural (was "unknown").
"""
from __future__ import annotations
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _run_type import resolve as resolve_run_type, all_types, RUN_TYPES  # noqa: E402
from _coverage import coverage_from_traj_file  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DATASETS = REPO / "datasets"
SEQ_META_CACHE = Path(__file__).resolve().parent / "_seq_meta_cache.json"

ENV_TYPE: dict[str, str] = {
    "euroc_mav": "indoor",
    "hortimulti": "agricultural",
    "rosariov2": "agricultural",
    "zed2i": "agricultural",
}

_RUN_DIR_RE = re.compile(r"^run(\d+)(?:_(.+))?$")

COLUMNS = [
    # Identity
    "dataset", "seq", "environment_type", "algo",
    "run_type", "use_imu", "use_lc",
    "run", "gnss_variant", "run_status", "eval_schema",
    # Sequence metadata
    "input_fps", "image_width", "image_height",
    "sequence_duration_s", "sequence_frames_total",
    # Coverage — coverage_gap_pct is THE coverage metric (gap-aware; see
    # _coverage.py). track_pct / trajectory_time_coverage_pct are retained for
    # continuity but are NOT reliable across algorithms (output-rate artifacts
    # / endpoint-span blindness).
    "coverage_gap_pct",
    "frames_tracked", "track_pct",
    "trajectory_duration_s", "trajectory_time_coverage_pct",
    "n_pairs_ate",
    # ATE SE(3) — primary accuracy metric for stereo/VIO (finding 4)
    "ate_se3_rmse_m", "ate_se3_max_m",
    # ATE Sim(3) — scale-corrected (primary only for monocular)
    "ate_sim3_rmse_m", "ate_sim3_max_m",
    # ATE origin-aligned — GNSS-fused runs only (global-frame error)
    "ate_origin_rmse_m", "ate_origin_max_m",
    # Scale
    "scale_factor", "scale_error_pct",
    # RPE — *_se3 = no scale correction (honest local drift); unsuffixed =
    # legacy Sim3-scale-corrected values
    "rpe_trans_1m_rmse_m", "rpe_trans_1m_se3_rmse_m", "rpe_rot_1m_rmse_deg",
    # Drift windows (% of window length, no scale correction)
    "drift_10m_pct", "drift_50m_pct", "drift_100m_pct",
    # Path length and normalised error
    "path_length_gt_m", "path_length_est_m",
    "ate_se3_rmse_pct_path", "ate_sim3_rmse_pct_path",
    # Robustness (None/blank = not instrumented for this algorithm)
    "loop_closures", "tracking_losses", "map_resets", "init_success",
    # Timing
    "duration_s", "fps", "real_time_factor", "processing_ms_per_frame",
    # Resource usage
    "cpu_mean_pct", "cpu_peak_pct", "ram_mean_mib", "ram_peak_mib",
    "vram_mean_mib", "vram_peak_mib", "gpu_mean_pct", "gpu_peak_pct",
    # Agricultural segments (+ which alignment semantics produced them:
    # global_se3 = fixed metric; per_segment_sim3 = legacy biased metric)
    "ate_row_rmse_m", "ate_turn_rmse_m", "n_segments_row", "n_segments_turn",
    "segment_alignment",
    # Machine provenance
    "machine_cpu", "machine_gpu",
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


def _load_seq_meta_cache() -> dict:
    if SEQ_META_CACHE.exists():
        try:
            return json.loads(SEQ_META_CACHE.read_text()).get("sequences", {})
        except Exception:
            pass
    return {}


_CACHE = _load_seq_meta_cache()


def load_seq_meta(dataset: str, seq: str) -> dict:
    """Per-sequence metadata: from datasets/ when present, else the cache."""
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

    # --- fall back to the committed cache for anything still missing ---
    cached = _CACHE.get(f"{dataset}/{seq}", {})
    for k, v in cached.items():
        meta.setdefault(k, v)

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


def compute_run_status(ev: dict) -> str:
    """Status for any run_eval.json, legacy or current."""
    explicit = ev.get("run_status")
    if explicit:
        return explicit
    ate = _g(ev, "ate", "rmse")
    n_pairs = ev.get("n_pairs_ate") or 0
    scale = ev.get("scale_factor")
    if ate is None or n_pairs < 10:
        return "eval_failed"
    if scale is not None and (scale < 0.1 or scale > 10.0):
        return "scale_collapse"
    return "ok"


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

    m_run = _RUN_DIR_RE.match(run_dir.name)
    run_no = m_run.group(1) if m_run else run_dir.name.replace("run", "")
    variant = (m_run.group(2) if (m_run and m_run.group(2)) else "default")

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
    seg_alignment = None
    for blk in (row_seg, turn_seg, seg.get("all", {}) or {}):
        if blk:
            seg_alignment = blk.get("alignment", "per_segment_sim3")
            break
    rob = ev.get("robustness", {}) or {}
    runtime = ev.get("runtime", {}) or {}
    machine = ev.get("machine", {}) or {}

    dataset = ds_dir.name
    seq = seq_dir.name

    # Derived: scale error
    scale = _g(ev, "scale_factor")
    scale_error_pct = _round(abs(scale - 1.0) * 100, 2) if scale is not None else None

    # Derived: ATE as % of path (SE3 and Sim3)
    ate_se3_rmse = _g(ev, "ate_se3", "rmse")
    ate_sim3_rmse = _g(ev, "ate", "rmse")
    path_gt = seq_meta.get("path_length_gt_m")
    ate_pct_path = _round(ate_se3_rmse / path_gt * 100, 2) if (ate_se3_rmse and path_gt) else None
    ate_sim3_pct_path = _round(ate_sim3_rmse / path_gt * 100, 2) if (ate_sim3_rmse and path_gt) else None

    # Derived: timing
    wall_s = runtime.get("wall_s") or _g(meta, "duration_s")
    fps_val = runtime.get("fps") or _g(meta, "fps")
    seq_dur = seq_meta.get("sequence_duration_s")
    rtf = _round(seq_dur / wall_s, 3) if (seq_dur and wall_s) else None
    frames_tracked = rob.get("frames_tracked") or _g(meta, "frames")
    ms_per_frame = _round(wall_s * 1000 / frames_tracked, 2) if (wall_s and frames_tracked) else None

    # Coverage: gap-aware (computed here for every row so legacy runs get it
    # too; identical helper to what _evaluate_run.py records for new runs)
    cov_gap = _g(ev, "coverage", "coverage_gap_pct")
    if cov_gap is None:
        cov_gap = coverage_from_traj_file(run_dir / "trajectory.txt", seq_dur).get("coverage_gap_pct")

    # Legacy coverage variants (kept, unreliable — see COLUMNS comment)
    n_pairs = ev.get("n_pairs_ate")
    traj_dur = traj_info.get("trajectory_duration_s")
    traj_time_cov = _round(traj_dur / seq_dur * 100, 1) if (traj_dur and seq_dur) else None

    return {
        "dataset": dataset,
        "seq": seq,
        "environment_type": ENV_TYPE.get(dataset, "unknown"),
        "algo": algo_dir.name,
        "run_type": rt.name,
        "use_imu": rt.use_imu,
        "use_lc": rt.use_lc,
        "run": run_no,
        "gnss_variant": variant if rt.use_gnss else ("default" if variant == "default" else variant),
        "run_status": compute_run_status(ev),
        "eval_schema": ev.get("eval_schema", 1),
        # Sequence
        "input_fps": seq_meta.get("input_fps"),
        "image_width": seq_meta.get("image_width"),
        "image_height": seq_meta.get("image_height"),
        "sequence_duration_s": seq_meta.get("sequence_duration_s"),
        "sequence_frames_total": seq_meta.get("sequence_frames_total"),
        # Coverage
        "coverage_gap_pct": cov_gap,
        "frames_tracked": frames_tracked,
        "track_pct": rob.get("track_pct"),
        "trajectory_duration_s": traj_dur,
        "trajectory_time_coverage_pct": traj_time_cov,
        "n_pairs_ate": n_pairs,
        # ATE
        "ate_se3_rmse_m": ate_se3_rmse,
        "ate_se3_max_m": _g(ev, "ate_se3", "max"),
        "ate_sim3_rmse_m": ate_sim3_rmse,
        "ate_sim3_max_m": _g(ev, "ate", "max"),
        "ate_origin_rmse_m": _g(ev, "ate_origin", "rmse"),
        "ate_origin_max_m": _g(ev, "ate_origin", "max"),
        # Scale
        "scale_factor": scale,
        "scale_error_pct": scale_error_pct,
        # RPE
        "rpe_trans_1m_rmse_m": _g(ev, "rpe_trans_1m", "rmse"),
        "rpe_trans_1m_se3_rmse_m": _g(ev, "rpe_trans_1m_se3", "rmse"),
        "rpe_rot_1m_rmse_deg": _g(ev, "rpe_rot_1m_deg", "rmse"),
        # Drift windows (% of length, no scale correction; new runs only)
        "drift_10m_pct": _g(ev, "kitti_drift", "drift_10m_pct"),
        "drift_50m_pct": _g(ev, "kitti_drift", "drift_50m_pct"),
        "drift_100m_pct": _g(ev, "kitti_drift", "drift_100m_pct"),
        # Path
        "path_length_gt_m": path_gt,
        "path_length_est_m": traj_info.get("path_length_est_m"),
        "ate_se3_rmse_pct_path": ate_pct_path,
        "ate_sim3_rmse_pct_path": ate_sim3_pct_path,
        # Robustness
        "loop_closures": rob.get("loop_closures"),
        "tracking_losses": rob.get("tracking_losses"),
        "map_resets": rob.get("map_resets"),
        "init_success": rob.get("init_success"),
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
        "segment_alignment": seg_alignment,
        # Machine (from _system_info.collect(): keys "cpu" and "gpus" list).
        # Blocks explicitly tagged collected_at="evaluation" identify the
        # evaluation host, not the run host — excluded from attribution.
        "machine_cpu": machine.get("cpu")
                       if machine.get("collected_at") != "evaluation" else None,
        "machine_gpu": ((machine.get("gpus") or [{}])[0].get("name")
                        if isinstance(machine.get("gpus"), list) else None)
                       if machine.get("collected_at") != "evaluation" else None,
        # Meta
        "final_drift_m": _g(ev, "final_drift_m"),
        "gt_source": _g(ev, "gt_source"),
    }


def build_one(rt) -> int:
    """Rebuild one run type's CSV from scratch. Returns row count."""
    results_root = rt.results_root
    csv_path = rt.csv_path
    if not results_root.is_dir():
        print(f"[info] {rt.name}: results dir missing ({results_root}), skipping")
        return 0

    eval_files = sorted(results_root.glob("*/*/*/run*/run_eval.json"))
    # Pre-load sequence metadata
    seq_meta_cache: dict[tuple, dict] = {}
    rows = []
    for ep in eval_files:
        seq_dir = ep.parent.parent.parent
        ds_dir = seq_dir.parent
        key = (ds_dir.name, seq_dir.name)
        if key not in seq_meta_cache:
            seq_meta_cache[key] = load_seq_meta(ds_dir.name, seq_dir.name)
        row = row_from_eval(ep, seq_meta_cache[key], rt)
        if row is not None:
            rows.append(row)

    rows.sort(key=lambda r: (r["dataset"], r["seq"], r["algo"],
                             r["gnss_variant"] or "", int(r["run"] or 0)))

    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore",
                           lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"[ok] {rt.name}: wrote {len(rows)} row(s) -> {csv_path.name}")
    return len(rows)


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target == "all":
        types = all_types(REPO)
    elif target in RUN_TYPES:
        types = [resolve_run_type(target, REPO)]
    else:
        print(f"Usage: {sys.argv[0]} [vo|vo-lc|vio|vio-lc|gnss-vio|all]", file=sys.stderr)
        return 1

    total = 0
    for rt in types:
        total += build_one(rt)
    print(f"[done] {total} row(s) across {len(types)} CSV(s) (full rebuild)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
