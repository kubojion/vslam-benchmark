#!/usr/bin/env python3
"""Evaluate a single algorithm run and write run_eval.json.

Usage:
    python3 _evaluate_run.py <dataset> <seq> <algo> <run_id>

Looks for:
  datasets/<dataset>/<seq>/gt_interp_tum.txt   (preferred)
  datasets/<dataset>/<seq>/gt_tum.txt          (fallback, uses t_max_diff=0.1)
  datasets/<dataset>/<seq>/times.txt           (for GT interpolation trigger)
  datasets/<dataset>/<seq>/segments_auto.csv   (optional agri segments)
  results/<dataset>/<seq>/<algo>/run<N>/trajectory.txt
  results/<dataset>/<seq>/<algo>/run<N>/run_meta.json
  results/<dataset>/<seq>/<algo>/run<N>/resources.csv
  results/<dataset>/<seq>/<algo>/run<N>/run_log.txt

Writes:
  results/<dataset>/<seq>/<algo>/run<N>/run_eval.json

Algorithm-specific log parsing is keyed on <algo>. Add new algos to
LOG_PATTERNS to extend support.
"""
import json
import os
import re
import sys
import subprocess
from pathlib import Path

import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# Per-algorithm patterns to extract robustness events from the run log.
# Patterns are matched line-by-line against the timestamped log.
# ──────────────────────────────────────────────────────────────────────────────
LOG_PATTERNS = {
    "orbslam3": {
        "init_success":    re.compile(r"New Map created with \d+ points"),
        "tracking_loss":   re.compile(r"\bLOST\b"),
        "loop_closure":    re.compile(r"\*Loop detected"),
        "map_reset":       re.compile(r"Map id:\s*\d+"),
    },
    "droidslam": {
        "init_success":    re.compile(r"Running DROID"),
        "tracking_loss":   None,
        "loop_closure":    None,
        "map_reset":       None,
    },
    "macvo": {
        "init_success":    re.compile(r"Start running|Tracking starts"),
        "tracking_loss":   None,
        "loop_closure":    None,
        "map_reset":       None,
    },
    "basalt": {
        # Basalt prints frame count updates and marginalisation info.
        # "Initialized!" signals the first successful stereo triangulation.
        "init_success":    re.compile(r"Initialized!|initialized|Starting"),
        "tracking_loss":   re.compile(r"Tracking lost|tracking lost|LOST"),
        "loop_closure":    None,
        "map_reset":       None,
    },
    "airslam": {
        # visual_odometry.cpp prints "dataset done" once all frames are loaded,
        # then "i ====== 0" for the first frame processed.
        # No tracking-loss or loop-closure output (stereo VO only).
        "init_success":    re.compile(r"dataset done"),
        "tracking_loss":   None,
        "loop_closure":    None,
        "map_reset":       None,
    },
}


# ──────────────────────────────────────────────────────────────────────────────
# evo helpers — call evo_ape / evo_rpe as subprocess, parse text output
# ──────────────────────────────────────────────────────────────────────────────
_EVO_STAT_RE = re.compile(
    r"^\s*(max|mean|median|min|rmse|sse|std)\s+([0-9eE+\-.]+)")


def _parse_evo_stats(text):
    stats = {}
    for line in text.splitlines():
        m = _EVO_STAT_RE.match(line)
        if m:
            stats[m.group(1)] = float(m.group(2))
    return stats


def _parse_scale(text):
    """Extract Sim3 scale from evo --verbose output."""
    m = re.search(r"Scale correction:\s*([0-9eE+\-.]+)", text)
    return float(m.group(1)) if m else None


def run_evo_ape(gt, est, t_max_diff=0.005, correct_scale=True):
    """Run evo_ape, return (stats_dict, scale_factor, n_pairs)."""
    cmd = [
        "evo_ape", "tum", gt, est,
        "--align", "--t_max_diff", str(t_max_diff),
        "--verbose", "--no_warnings",
    ]
    if correct_scale:
        cmd += ["--correct_scale", "-s"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    out = result.stdout + result.stderr
    stats = _parse_evo_stats(out)
    scale = _parse_scale(out)
    m = re.search(r"Compared (\d+) absolute pose pairs", out)
    n_pairs = int(m.group(1)) if m else None
    return stats, scale, n_pairs


def run_evo_rpe(gt, est, delta, delta_unit="m",
                pose_relation="point_distance", t_max_diff=0.005,
                correct_scale=True):
    """Run evo_rpe, return stats_dict.

    Uses point_distance (world-frame Euclidean distance between relative
    position vectors) to avoid body-frame quaternion convention mismatch
    between different SLAM systems and GT sources.
    """
    cmd = [
        "evo_rpe", "tum", gt, est,
        "--align", "--t_max_diff", str(t_max_diff),
        "-r", pose_relation,
        "--delta", str(delta), "-u", delta_unit,
        "--no_warnings",
    ]
    if correct_scale:
        cmd += ["--correct_scale", "-s"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    out = result.stdout + result.stderr
    return _parse_evo_stats(out)


# ──────────────────────────────────────────────────────────────────────────────
# Segment-level ATE  (call evo_ape with --t_start / --t_end per segment)
# ──────────────────────────────────────────────────────────────────────────────
def ape_for_segment(gt, est, t_start, t_end, t_max_diff=0.005):
    """ATE RMSE for a single time window. Returns None if too few pairs."""
    cmd = [
        "evo_ape", "tum", gt, est,
        "--align", "--correct_scale", "-s",
        "--t_max_diff", str(t_max_diff),
        "--t_start", str(t_start),
        "--t_end",   str(t_end),
        "--verbose", "--no_warnings",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    out = result.stdout + result.stderr
    stats = _parse_evo_stats(out)
    m = re.search(r"Compared (\d+) absolute pose pairs", out)
    n = int(m.group(1)) if m else (len(stats) > 0 and 99 or 0)
    if n < 5:
        return None
    return stats


# ──────────────────────────────────────────────────────────────────────────────
# Log parsing
# ──────────────────────────────────────────────────────────────────────────────
def parse_log(log_path, algo):
    """Parse a timestamped run log. Returns dict of robustness fields."""
    result = {
        "init_success":      False,
        "init_time_s":       None,
        "tracking_losses":   0,
        "loop_closures":     0,
        "map_resets":        0,
        "output_valid":      True,
        "first_failure_s":   None,
    }

    if not os.path.isfile(log_path):
        return result

    patterns = LOG_PATTERNS.get(algo, {})
    # Log lines have format: "<rel_time_s> <original line>"
    # or plain ORB-SLAM3 style without timestamps (backward compat).

    map_ids_seen = set()
    run_start_t = None

    with open(log_path) as f:
        for raw_line in f:
            raw_line = raw_line.rstrip()
            # Try to strip leading float timestamp added by run script
            m_ts = re.match(r"^(\d+\.\d+)\s+(.*)", raw_line)
            if m_ts:
                rel_t = float(m_ts.group(1))
                line = m_ts.group(2)
                if run_start_t is None:
                    run_start_t = 0.0
            else:
                rel_t = None
                line = raw_line

            pat_init = patterns.get("init_success")
            if pat_init and pat_init.search(line) and not result["init_success"]:
                result["init_success"] = True
                result["init_time_s"] = rel_t

            pat_loss = patterns.get("tracking_loss")
            if pat_loss and pat_loss.search(line):
                result["tracking_losses"] += 1
                if result["first_failure_s"] is None and rel_t is not None:
                    result["first_failure_s"] = rel_t

            pat_loop = patterns.get("loop_closure")
            if pat_loop and pat_loop.search(line):
                result["loop_closures"] += 1

            pat_map = patterns.get("map_reset")
            if pat_map:
                mm = re.search(r"Map id:\s*(\d+)", line)
                if mm:
                    map_ids_seen.add(int(mm.group(1)))

    if map_ids_seen:
        result["map_resets"] = max(0, len(map_ids_seen) - 1)

    return result


# ──────────────────────────────────────────────────────────────────────────────
# Resource stats from CSV
# ──────────────────────────────────────────────────────────────────────────────
def parse_resources(csv_path):
    """Parse resources.csv -> dict of mean/max values. Returns None on failure."""
    if not os.path.isfile(csv_path):
        return None
    try:
        import csv as _csv
        rows = list(_csv.DictReader(open(csv_path)))
        if not rows:
            return None

        def col(name, default=0.0):
            vals = []
            for r in rows:
                try:
                    vals.append(float(r.get(name, default)))
                except ValueError:
                    pass
            return vals if vals else [default]

        vram = col("vram_mib")
        gpu  = col("gpu_util_pct")
        cpu  = col("cpu_pct")
        ram  = col("ram_mib")

        return {
            "vram_mean_mib":  round(float(np.mean(vram)), 1),
            "vram_peak_mib":  round(float(np.max(vram)), 1),
            "gpu_mean_pct":   round(float(np.mean(gpu)), 1),
            "gpu_peak_pct":   round(float(np.max(gpu)), 1),
            "cpu_mean_pct":   round(float(np.mean(cpu)), 1),
            "cpu_peak_pct":   round(float(np.max(cpu)), 1),
            "ram_mean_mib":   round(float(np.mean(ram)), 1),
            "ram_peak_mib":   round(float(np.max(ram)), 1),
        }
    except Exception as e:
        print(f"[eval] resource parse failed: {e}", file=sys.stderr)
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Final drift — Euclidean distance between last aligned pose and last GT pose
# ──────────────────────────────────────────────────────────────────────────────
def compute_final_drift(gt_path, est_path, t_max_diff=0.005):
    """Final positional drift (m) after Sim3 alignment."""
    try:
        gt  = np.loadtxt(gt_path)
        est = np.loadtxt(est_path)
        if gt.ndim == 1:
            gt = gt[np.newaxis]
        if est.ndim == 1:
            est = est[np.newaxis]
        # Match last timestamps
        t_last_est = est[-1, 0]
        diffs = np.abs(gt[:, 0] - t_last_est)
        nearest_gt_pos = gt[np.argmin(diffs), 1:4]
        # Rough: directly compare unaligned last poses (scale ~1 after Sim3).
        # True final drift requires the aligned trajectory — we approximate here.
        last_est_pos = est[-1, 1:4]
        return round(float(np.linalg.norm(last_est_pos - nearest_gt_pos)), 4)
    except Exception:
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) != 5:
        print(f"Usage: {sys.argv[0]} <dataset> <seq> <algo> <run_id>",
              file=sys.stderr)
        sys.exit(1)

    dataset, seq, algo, run_id = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

    ws = Path(__file__).resolve().parents[2]
    ds_dir  = ws / "datasets" / dataset / seq
    run_dir = ws / "results" / dataset / seq / algo / f"run{run_id}"

    traj_path = run_dir / "trajectory.txt"
    if not traj_path.exists():
        print(f"[eval] ERROR: trajectory not found: {traj_path}", file=sys.stderr)
        sys.exit(1)

    # Choose GT: prefer interpolated GT (exact timestamps), fallback to raw GT.
    gt_interp = ds_dir / "gt_interp_tum.txt"
    gt_raw    = ds_dir / "gt_tum.txt"
    if gt_interp.exists():
        gt_path    = str(gt_interp)
        t_max_diff = 0.005      # tight: timestamps should match exactly
        gt_source  = "interpolated"
    else:
        gt_path    = str(gt_raw)
        t_max_diff = 0.1        # loose: raw GT at different rate
        gt_source  = "raw_tmax0.1"
    print(f"[eval] GT source: {gt_source} ({gt_path})", file=sys.stderr)

    est_path = str(traj_path)

    # ── Accuracy metrics ──────────────────────────────────────────────────────
    # Sim(3) alignment (--correct_scale): standard practice for monocular VO,
    # also used by us for stereo so all algorithms are on the same footing and
    # so that scale drift can be quantified via the reported scale_factor.
    print("[eval] running ATE (Sim3, --correct_scale) ...", file=sys.stderr)
    ate_stats, scale, n_pairs = run_evo_ape(gt_path, est_path, t_max_diff, correct_scale=True)
    # SE(3) alignment (no scale correction): for stereo/RGB-D the scale is
    # supposed to be metric (from the baseline) so this is the more honest
    # accuracy number — it does NOT absorb any real scale drift.
    print("[eval] running ATE (SE3, no scale correction) ...", file=sys.stderr)
    ate_se3_stats, _, _ = run_evo_ape(gt_path, est_path, t_max_diff, correct_scale=False)

    print("[eval] running RPE (point_distance, 1 m) ...", file=sys.stderr)
    rpe_t = run_evo_rpe(gt_path, est_path, delta=1.0, delta_unit="m",
                        pose_relation="point_distance", t_max_diff=t_max_diff)

    print("[eval] running RPE (rotation, 1 m) ...", file=sys.stderr)
    rpe_r = run_evo_rpe(gt_path, est_path, delta=1.0, delta_unit="m",
                        pose_relation="angle_deg", t_max_diff=t_max_diff)

    # KITTI-style: RPE at 10 m, 50 m, 100 m windows
    print("[eval] running KITTI-style drift (10/50/100 m) ...", file=sys.stderr)
    kitti = {}
    for d in [10, 50, 100]:
        st = run_evo_rpe(gt_path, est_path, delta=float(d), delta_unit="m",
                         pose_relation="point_distance", t_max_diff=t_max_diff)
        kitti[f"rpe_{d}m_trans_rmse"] = st.get("rmse")

    final_drift = compute_final_drift(gt_path, est_path, t_max_diff)

    # ── Robustness ────────────────────────────────────────────────────────────
    log_path = run_dir / "run_log.txt"
    robustness = parse_log(str(log_path), algo)
    meta_path = run_dir / "run_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        # True total = number of GT frames (interpolated GT has one row per camera frame)
        gt_total = sum(1 for _ in open(gt_path)) if gt_path else meta.get("frames", None)
        tracked  = meta.get("frames", None)
        robustness["frames_total"]   = gt_total
        robustness["frames_tracked"] = tracked
        if gt_total and tracked:
            robustness["track_pct"] = round(100.0 * tracked / gt_total, 1)
        elif meta.get("frames"):
            robustness["track_pct"] = 100.0
        robustness["output_valid"] = True
    else:
        meta = {}

    # ── Runtime ───────────────────────────────────────────────────────────────
    res_path = run_dir / "resources.csv"
    runtime = parse_resources(str(res_path)) or {}
    if meta:
        runtime["wall_s"] = round(meta.get("duration_s", 0), 2)
        fps = meta.get("fps", 0)
        runtime["fps"] = round(fps, 3)
        # Real-time factor: fps / input_fps (we don't know input fps here,
        # so leave it as fps and let aggregate compute RTF from sequence metadata)
        runtime["fps_raw"] = round(fps, 3)

    # ── Agricultural segment metrics ──────────────────────────────────────────
    seg_path = ds_dir / "segments_auto.csv"
    agri = {}
    if seg_path.exists():
        print("[eval] computing per-segment ATE ...", file=sys.stderr)
        import csv
        with open(seg_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Accumulate per type
        type_errors = {}
        for row in rows:
            seg_type = row["type"]
            t0 = float(row["t_start"])
            t1 = float(row["t_end"])
            stats = ape_for_segment(gt_path, est_path, t0, t1, t_max_diff)
            if stats and "rmse" in stats:
                if seg_type not in type_errors:
                    type_errors[seg_type] = []
                type_errors[seg_type].append({
                    "t_start":    t0,
                    "t_end":      t1,
                    "ate_rmse":   stats["rmse"],
                    "ate_mean":   stats.get("mean"),
                    "n_frames":   int(row["n_frames"]),
                    "duration_s": float(row["duration_s"]),
                })

        for stype, segs in type_errors.items():
            rmse_vals = [s["ate_rmse"] for s in segs]
            agri[stype] = {
                "n_segments":     len(segs),
                "ate_rmse_mean":  round(float(np.mean(rmse_vals)), 6),
                "ate_rmse_std":   round(float(np.std(rmse_vals)), 6),
                "segments":       segs,
            }

    # ── Assemble output ───────────────────────────────────────────────────────
    out = {
        "run":     run_id,
        "algo":    algo,
        "dataset": dataset,
        "seq":     seq,
        "gt_source": gt_source,
        "n_pairs_ate": n_pairs,
        "ate": {
            "rmse":   ate_stats.get("rmse"),
            "mean":   ate_stats.get("mean"),
            "median": ate_stats.get("median"),
            "std":    ate_stats.get("std"),
            "max":    ate_stats.get("max"),
        },
        "ate_se3": {
            "rmse":   ate_se3_stats.get("rmse"),
            "mean":   ate_se3_stats.get("mean"),
            "median": ate_se3_stats.get("median"),
            "std":    ate_se3_stats.get("std"),
            "max":    ate_se3_stats.get("max"),
        },
        "rpe_trans_1m": {
            "rmse": rpe_t.get("rmse"),
            "mean": rpe_t.get("mean"),
            "std":  rpe_t.get("std"),
            "max":  rpe_t.get("max"),
        },
        "rpe_rot_1m_deg": {
            "rmse": rpe_r.get("rmse"),
            "mean": rpe_r.get("mean"),
            "std":  rpe_r.get("std"),
        },
        "kitti_drift": kitti,
        "scale_factor":  scale,
        "final_drift_m": final_drift,
        "robustness":    robustness,
        "runtime":       runtime,
        "agri_segments": agri,
    }

    out_path = run_dir / "run_eval.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"[eval] wrote {out_path}", file=sys.stderr)

    # Quick summary to stdout
    print(f"\n{'='*60}")
    print(f"  {algo.upper()}  |  {dataset}/{seq}  |  run {run_id}")
    print(f"{'='*60}")
    print(f"  ATE RMSE (Sim3):{out['ate']['rmse']:.4f} m  ({n_pairs} pairs, GT: {gt_source})")
    if out['ate_se3']['rmse'] is not None:
        print(f"  ATE RMSE (SE3): {out['ate_se3']['rmse']:.4f} m   (no scale correction)")
    print(f"  RPE trans RMSE: {out['rpe_trans_1m']['rmse']:.4f} m/m  (1-metre windows)")
    print(f"  RPE rot RMSE:   {out['rpe_rot_1m_deg']['rmse']:.3f} °/m")
    print(f"  Scale factor:   {scale:.4f}" if scale else "  Scale factor:   n/a")
    print(f"  Wall-clock:     {runtime.get('wall_s','?')} s  |  {runtime.get('fps','?')} fps")
    if agri:
        for stype, v in agri.items():
            print(f"  ATE [{stype}]:   {v['ate_rmse_mean']:.4f} m  ({v['n_segments']} segs)")
    print()


if __name__ == "__main__":
    main()
