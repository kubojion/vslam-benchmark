#!/usr/bin/env python3
"""Evaluate a single algorithm run and write run_eval.json.

Usage:
    python3 _evaluate_run.py <dataset> <seq> <algo> <run_id> [run_type=vo]

run_type selects which results-tree this run lives in:
  vo       -> results-vo/<dataset>/<seq>/<algo>/run<N>/
  vo-lc    -> results-vo-lc/<dataset>/<seq>/<algo>/run<N>/
  vio      -> results-vio/<dataset>/<seq>/<algo>/run<N>/
  vio-lc   -> results-vio-lc/<dataset>/<seq>/<algo>/run<N>/
  gnss-vio -> results-gnss-vio/<dataset>/<seq>/<algo>/run<N>/

Looks for:
  datasets/<dataset>/<seq>/gt_interp_tum.txt   (preferred)
  datasets/<dataset>/<seq>/gt_tum.txt          (fallback, uses t_max_diff=0.1)
  datasets/<dataset>/<seq>/times.txt           (for GT interpolation trigger)
  datasets/<dataset>/<seq>/segments_auto.csv   (optional agri segments)
  <results_root>/<dataset>/<seq>/<algo>/run<N>/trajectory.txt
  <results_root>/<dataset>/<seq>/<algo>/run<N>/run_meta.json
  <results_root>/<dataset>/<seq>/<algo>/run<N>/resources.csv
  <results_root>/<dataset>/<seq>/<algo>/run<N>/run_log.txt

Writes:
  <results_root>/<dataset>/<seq>/<algo>/run<N>/run_eval.json

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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _run_type import canonicalize_dataset, resolve as resolve_run_type  # noqa: E402

# Segment split policy
# Default behavior is to keep row/turn distinction.
# Dataset overrides can disable this (used for non-agricultural references).
DISTINGUISH_ROW_TURN_DEFAULT = True
DISTINGUISH_ROW_TURN_BY_DATASET = {
    "euroc_mav": False,
}


def distinguish_row_turn_for_dataset(dataset: str) -> bool:
    """Return whether row/turn split should be preserved for this dataset.

    Configuration precedence:
    1) Dataset-specific env var: VSLAM_DISTINGUISH_ROW_TURN_<DATASET>
    2) Global env var: VSLAM_DISTINGUISH_ROW_TURN
    3) Dataset override map
    4) Global default (True)
    """
    ds_env_name = "VSLAM_DISTINGUISH_ROW_TURN_" + re.sub(r"[^A-Z0-9]", "_", dataset.upper())
    for env_name in (ds_env_name, "VSLAM_DISTINGUISH_ROW_TURN"):
        raw = os.getenv(env_name)
        if raw is None:
            continue
        raw = raw.strip().lower()
        if raw in {"1", "true", "yes", "on"}:
            return True
        if raw in {"0", "false", "no", "off"}:
            return False
    if dataset in DISTINGUISH_ROW_TURN_BY_DATASET:
        return DISTINGUISH_ROW_TURN_BY_DATASET[dataset]
    return DISTINGUISH_ROW_TURN_DEFAULT

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
    "fasttrack_partial_gpu": {
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
        "loop_closure":    re.compile(r"Loop closure detected|loop detected"),
        "map_reset":       None,
    },
    "ov2slam": {
        "init_success":    re.compile(r"OV.*SLAM is ready to process incoming images"),
        "tracking_loss":   re.compile(r"RESET REQUIRED"),
        "loop_closure":    re.compile(r"\[PoseGraph\].*Closing a loop between"),
        "map_reset":       re.compile(r"RESET APPLIED"),
    },
    "megasam": {
        # MegaSaM prints per-frame depth+pose progress and a final
        # "Saved trajectory" banner.
        "init_success":    re.compile(r"Loading model|Running MegaSaM"),
        "tracking_loss":   None,
        "loop_closure":    None,
        "map_reset":       None,
    },
    "mast3r_slam": {
        # MASt3R-SLAM uses the MASt3R retrieval head for loop closures; the
        # demo prints "Loop closure" when one is accepted.
        "init_success":    re.compile(r"MASt3R-SLAM|Initialised"),
        "tracking_loss":   re.compile(r"Tracking lost"),
        "loop_closure":    re.compile(r"Loop closure"),
        "map_reset":       None,
    },
    "okvis2": {
        # okvis_app_synchronous prints "Initialised!" after IMU init,
        # "Marginalisation... SLAM frame" for ongoing tracking,
        # and "Finishing..." before writing the trajectory.
        # Loop closures: Frontend.cpp logs one "LOOP CLOSURE: current frame N,
        # matching to keyframe M, ..." line per detected closure. NOTE: do NOT
        # match bare "loop closure" -- that hits the per-frame timing-profile
        # rows ("loop closure query", "attempt loop closure") and overcounts by
        # ~100x (e.g. 6337 timing rows vs 76 real closures on Rosario seq1).
        "init_success":    re.compile(r"Initialised!|Initialized!|SLAM started"),
        "tracking_loss":   re.compile(r"Tracking LOST|tracking lost"),
        "loop_closure":    re.compile(r"LOOP CLOSURE: current frame"),
        "map_reset":       None,
    },
    "okvis2x": {
        # Frontend.cpp logs "Initialized!" (INFO) once the IMU-aided front-end
        # bootstraps, and "3d2d tracking lost. Number of 3d2d-matches: N"
        # (WARNING) when it loses the map.
        # Loop closures: OKVIS2-X shares OKVIS2's Frontend.cpp and logs the same
        # "LOOP CLOSURE: current frame N, matching to keyframe M, ..." events
        # (the earlier "OKVIS2-X never logs an accepted closure" assumption was
        # wrong -- it does, e.g. 27 on Rosario seq1, 29 on EuRoC MH_01; the only
        # thing it never logs here is a GPS loop closure).
        "init_success":    re.compile(r"Initialized!"),
        "tracking_loss":   re.compile(r"3d2d tracking lost"),
        "loop_closure":    re.compile(r"LOOP CLOSURE: current frame"),
        "map_reset":       None,
    },
    "openvins": {
        # OpenVINS' MSCKF prints "[init]: successful initialization in ..."
        # once the static-IMU/dynamic init succeeds. "Reset System" appears
        # if the filter explicitly resets. No built-in loop closure.
        "init_success":    re.compile(r"successful initialization|Initialized System"),
        "tracking_loss":   re.compile(r"failed to track|Reset System|TRACKING LOST"),
        "loop_closure":    None,
        "map_reset":       re.compile(r"Reset System"),
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


def run_evo_ape(gt, est, t_max_diff=0.005, correct_scale=True, align_origin=False):
    """Run evo_ape, return (stats_dict, scale_factor, n_pairs).

    align_origin=True uses --align_origin (translate the estimate so its first
    pose coincides with GT — no rotation, no scale). This is the honest metric
    for GNSS-fused estimates, whose global orientation and scale are supposed
    to be anchored by GNSS: a full Sim(3)/SE(3) fit would absorb exactly the
    global-frame errors GNSS is meant to bound.
    """
    cmd = [
        "evo_ape", "tum", gt, est,
        "--t_max_diff", str(t_max_diff),
        "--verbose", "--no_warnings",
    ]
    if align_origin:
        cmd += ["--align_origin"]
    else:
        cmd += ["--align"]
        if correct_scale:
            cmd += ["--correct_scale"]
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
# Segment-level ATE under a SINGLE GLOBAL alignment.
#
# Changed 2026-08-05: the previous implementation ran evo_ape with
# --align --correct_scale independently per ~2 m time window. Sim(3) on a
# near-collinear point set is geometrically degenerate (rotation about the row
# axis unconstrained, per-segment scale absorbs residual error), which
# structurally flattered the "row" ATE vs the "turn" ATE. The metric is now:
# align ONCE over the whole trajectory (SE3 Umeyama, no scale), then report the
# RMSE of the globally-aligned error within each segment window. Old
# run_eval.json files carry the biased per-segment values; the CSV builder
# tags which semantics a row uses via `segment_alignment`.
# ──────────────────────────────────────────────────────────────────────────────
def _load_tum(path):
    data = np.loadtxt(str(path))
    if data.ndim == 1:
        data = data[np.newaxis, :]
    return data


def _associate(gt, est, t_max_diff=0.005):
    """Nearest-timestamp association. Returns (gt_xyz, est_xyz, t) matched."""
    gt_t, est_t = gt[:, 0], est[:, 0]
    idx = np.searchsorted(gt_t, est_t)
    idx = np.clip(idx, 1, len(gt_t) - 1)
    left = gt_t[idx - 1]
    right = gt_t[idx]
    use_left = (est_t - left) < (right - est_t)
    nearest = np.where(use_left, idx - 1, idx)
    dt = np.abs(gt_t[nearest] - est_t)
    ok = dt <= t_max_diff
    return gt[nearest[ok], 1:4], est[ok, 1:4], est_t[ok]


def _umeyama_se3(src, dst):
    """Rigid SE(3) Umeyama fit src->dst (no scale). Returns (R, t) or None."""
    if len(src) < 3:
        return None
    mu_s, mu_d = src.mean(0), dst.mean(0)
    cov = (dst - mu_d).T @ (src - mu_s) / len(src)
    U, _, Vt = np.linalg.svd(cov)
    S = np.eye(3)
    if np.linalg.det(U @ Vt) < 0:
        S[2, 2] = -1
    R = U @ S @ Vt
    t = mu_d - R @ mu_s
    return R, t


def segment_ate_global(gt_path, est_path, seg_rows, keep_row_turn,
                       t_max_diff=0.005, min_pairs=5):
    """Per-segment ATE RMSE of the globally SE(3)-aligned trajectory.

    seg_rows: list of dicts with type/t_start/t_end/n_frames/duration_s.
    Returns {seg_type: {n_segments, ate_rmse_mean, ate_rmse_std, alignment,
                        segments: [...]}} in the same shape as the legacy
    agri_segments block, plus an "alignment" marker.
    """
    try:
        gt = _load_tum(gt_path)
        est = _load_tum(est_path)
    except Exception:
        return {}
    gt_xyz, est_xyz, t = _associate(gt, est, t_max_diff)
    if len(t) < 10:
        return {}
    fit = _umeyama_se3(est_xyz, gt_xyz)
    if fit is None:
        return {}
    R, tr = fit
    err = np.linalg.norm((est_xyz @ R.T + tr) - gt_xyz, axis=1)

    type_errors = {}
    for row in seg_rows:
        seg_type = row["type"] if keep_row_turn else "all"
        t0, t1 = float(row["t_start"]), float(row["t_end"])
        m = (t >= t0) & (t <= t1)
        n = int(m.sum())
        if n < min_pairs:
            continue
        rmse = float(np.sqrt(np.mean(err[m] ** 2)))
        type_errors.setdefault(seg_type, []).append({
            "t_start":    t0,
            "t_end":      t1,
            "ate_rmse":   round(rmse, 6),
            "ate_mean":   round(float(np.mean(err[m])), 6),
            "n_pairs":    n,
            "n_frames":   int(row["n_frames"]),
            "duration_s": float(row["duration_s"]),
        })

    agri = {}
    for stype, segs in type_errors.items():
        rmse_vals = [s["ate_rmse"] for s in segs]
        agri[stype] = {
            "n_segments":     len(segs),
            "ate_rmse_mean":  round(float(np.mean(rmse_vals)), 6),
            "ate_rmse_std":   round(float(np.std(rmse_vals, ddof=1)), 6) if len(rmse_vals) > 1 else 0.0,
            "alignment":      "global_se3",
            "segments":       segs,
        }
    return agri


# ──────────────────────────────────────────────────────────────────────────────
# Log parsing
# ──────────────────────────────────────────────────────────────────────────────
_MAP_ID_RE = re.compile(r"Map id:\s*(\d+)")


def parse_log(log_path, algo):
    """Parse a timestamped run log. Returns dict of robustness fields.

    Semantics (fixed 2026-08-05):
      * A field is None (not 0) when the algorithm has NO log pattern for it —
        "not instrumented" must be distinguishable from "genuinely zero".
        (Previously DPVO/Voxel-SVIO/all GNSS runners silently reported 0 loop
        closures / 0 tracking losses.)
      * map_resets now uses the algorithm's OWN configured pattern. The old
        code fetched it and then re-grepped ORB's "Map id:" regex regardless,
        so OV2SLAM's "RESET APPLIED" and OpenVINS' "Reset System" never
        counted. For ORB-style "Map id: N" patterns the count is
        (distinct ids - 1); for event-style patterns it is the match count.
    """
    patterns = LOG_PATTERNS.get(algo, {})

    def _has(key):
        return patterns.get(key) is not None

    result = {
        "init_success":      False if _has("init_success") else None,
        "init_time_s":       None,
        "tracking_losses":   0 if _has("tracking_loss") else None,
        "loop_closures":     0 if _has("loop_closure") else None,
        "map_resets":        0 if _has("map_reset") else None,
        "output_valid":      True,
        "first_failure_s":   None,
        "log_instrumented":  bool(patterns),
    }

    if not os.path.isfile(log_path):
        return result

    map_ids_seen = set()
    map_event_count = 0
    pat_map = patterns.get("map_reset")
    map_is_id_style = bool(pat_map and "Map id" in pat_map.pattern)

    with open(log_path) as f:
        for raw_line in f:
            raw_line = raw_line.rstrip()
            # Try to strip leading float timestamp added by run script
            m_ts = re.match(r"^(\d+\.\d+)\s+(.*)", raw_line)
            if m_ts:
                rel_t = float(m_ts.group(1))
                line = m_ts.group(2)
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

            if pat_map:
                if map_is_id_style:
                    mm = _MAP_ID_RE.search(line)
                    if mm:
                        map_ids_seen.add(int(mm.group(1)))
                elif pat_map.search(line):
                    map_event_count += 1

    if pat_map:
        if map_is_id_style:
            result["map_resets"] = max(0, len(map_ids_seen) - 1) if map_ids_seen else 0
        else:
            result["map_resets"] = map_event_count

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
    """Final positional error (m) of the globally SE(3)-aligned trajectory.

    Fixed 2026-08-05: the old implementation compared the UNALIGNED last
    estimate pose against GT in a different coordinate frame ("we approximate
    here"), which is not a drift measure. Now: associate timestamps, fit one
    rigid SE(3) alignment over all matched pairs, and report the aligned error
    at the last matched timestamp.
    """
    try:
        gt = _load_tum(gt_path)
        est = _load_tum(est_path)
        gt_xyz, est_xyz, t = _associate(gt, est, t_max_diff)
        if len(t) < 3:
            return None
        fit = _umeyama_se3(est_xyz, gt_xyz)
        if fit is None:
            return None
        R, tr = fit
        err = np.linalg.norm((est_xyz @ R.T + tr) - gt_xyz, axis=1)
        return round(float(err[-1]), 4)
    except Exception:
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) not in (5, 6):
        print(f"Usage: {sys.argv[0]} <dataset> <seq> <algo> <run_id> [run_type=vo]",
              file=sys.stderr)
        sys.exit(1)

    dataset = canonicalize_dataset(sys.argv[1])
    seq, algo, run_id = sys.argv[2], sys.argv[3], sys.argv[4]
    run_type_name = sys.argv[5] if len(sys.argv) == 6 else "vo"

    ws = Path(__file__).resolve().parents[2]
    rt = resolve_run_type(run_type_name, ws)
    ds_dir  = ws / "datasets" / dataset / seq
    run_dir = rt.results_root / dataset / seq / algo / f"run{run_id}"

    print(f"[eval] run_type={rt.name}  results_root={rt.results_root}", file=sys.stderr)

    traj_path = run_dir / "trajectory.txt"
    if not traj_path.exists():
        print(f"[eval] ERROR: trajectory not found: {traj_path}", file=sys.stderr)
        sys.exit(1)

    # Choose GT: allow an explicit override, otherwise prefer interpolated GT.
    gt_override = os.environ.get("GT_OVERRIDE")
    gt_interp = ds_dir / "gt_interp_tum.txt"
    gt_raw    = ds_dir / "gt_tum.txt"
    if gt_override:
        gt_path    = str(Path(gt_override).expanduser())
        t_max_diff = 0.005
        gt_source  = f"override:{Path(gt_path).name}"
    elif gt_interp.exists():
        gt_path    = str(gt_interp)
        t_max_diff = 0.005      # tight: timestamps should match exactly
        gt_source  = "interpolated"
    else:
        gt_path    = str(gt_raw)
        t_max_diff = 0.1        # loose: raw GT at different rate
        gt_source  = "raw_tmax0.1"
    print(f"[eval] GT source: {gt_source} ({gt_path})", file=sys.stderr)

    # GT provenance (added 2026-08-05): record exactly WHICH ground-truth file
    # scored this run — the bare gt_source string cannot distinguish e.g. two
    # lever-arm variants manually copied over gt_interp_tum.txt (the zed2i
    # forensics this closes out).
    gt_provenance = {"file": str(Path(gt_path).name), "source": gt_source}
    try:
        import hashlib
        _h = hashlib.sha256()
        with open(gt_path, "rb") as _f:
            for chunk in iter(lambda: _f.read(1 << 20), b""):
                _h.update(chunk)
        gt_provenance["sha256"] = _h.hexdigest()
        gt_provenance["mtime"] = int(Path(gt_path).stat().st_mtime)
        gt_provenance["n_rows"] = sum(1 for _ in open(gt_path))
    except Exception as _e:
        gt_provenance["error"] = str(_e)

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

    # Origin-only alignment for GNSS-fused runs: their global orientation and
    # scale are supposed to be anchored by GNSS, so free Sim3/SE3 alignment
    # would absorb exactly the error GNSS is meant to bound (added 2026-08-05).
    ate_origin_stats = {}
    if rt.use_gnss:
        print("[eval] running ATE (origin-aligned, GNSS run) ...", file=sys.stderr)
        ate_origin_stats, _, _ = run_evo_ape(gt_path, est_path, t_max_diff,
                                             align_origin=True)

    print("[eval] running RPE (point_distance, 1 m) ...", file=sys.stderr)
    # Legacy field (Sim3 scale-corrected) kept for backward comparability with
    # pre-2026-08-05 run_eval.json files ...
    rpe_t = run_evo_rpe(gt_path, est_path, delta=1.0, delta_unit="m",
                        pose_relation="point_distance", t_max_diff=t_max_diff)
    # ... and the honest variant WITHOUT scale correction (scale drift is a
    # studied failure mode; the drift metric must not remove it).
    rpe_t_se3 = run_evo_rpe(gt_path, est_path, delta=1.0, delta_unit="m",
                            pose_relation="point_distance", t_max_diff=t_max_diff,
                            correct_scale=False)

    print("[eval] running RPE (rotation, 1 m) ...", file=sys.stderr)
    rpe_r = run_evo_rpe(gt_path, est_path, delta=1.0, delta_unit="m",
                        pose_relation="angle_deg", t_max_diff=t_max_diff)

    # Drift over 10/50/100 m windows. Legacy: Sim3-scale-corrected raw metres.
    # New (2026-08-05): un-scale-corrected, plus % of window length (the actual
    # KITTI convention).
    print("[eval] running drift windows (10/50/100 m) ...", file=sys.stderr)
    kitti = {}
    for d in [10, 50, 100]:
        st = run_evo_rpe(gt_path, est_path, delta=float(d), delta_unit="m",
                         pose_relation="point_distance", t_max_diff=t_max_diff)
        kitti[f"rpe_{d}m_trans_rmse"] = st.get("rmse")
        st_se3 = run_evo_rpe(gt_path, est_path, delta=float(d), delta_unit="m",
                             pose_relation="point_distance", t_max_diff=t_max_diff,
                             correct_scale=False)
        kitti[f"rpe_{d}m_trans_rmse_se3"] = st_se3.get("rmse")
        if st_se3.get("rmse") is not None:
            kitti[f"drift_{d}m_pct"] = round(st_se3["rmse"] / d * 100.0, 3)

    final_drift = compute_final_drift(gt_path, est_path, t_max_diff)

    # ── Robustness ────────────────────────────────────────────────────────────
    log_path = run_dir / "run_log.txt"
    robustness = parse_log(str(log_path), algo)
    meta_path = run_dir / "run_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        # Modern runners record the input camera count explicitly. Some legacy
        # "interpolated" GT files retain a higher-rate pose stream, so their
        # line count is not a reliable camera-frame total.
        gt_total = meta.get("frames_total")
        if not gt_total:
            gt_total = sum(1 for _ in open(gt_path)) if gt_path else meta.get("frames")
        tracked  = meta.get("frames", None)
        robustness["frames_total"]   = gt_total
        robustness["frames_tracked"] = tracked
        if gt_total and tracked:
            robustness["track_pct"] = round(100.0 * tracked / gt_total, 1)
        elif meta.get("frames"):
            robustness["track_pct"] = 100.0
    else:
        meta = {}

    # Real output validation (2026-08-05; previously output_valid was
    # unconditionally True whenever run_meta.json existed).
    ate_ok = ate_stats.get("rmse") is not None and (n_pairs or 0) >= 10
    scale_collapsed = scale is not None and (scale < 0.1 or scale > 10.0)
    robustness["output_valid"] = bool(ate_ok and not scale_collapsed)
    if not ate_ok:
        run_status = "eval_failed"
    elif scale_collapsed:
        run_status = "scale_collapse"
    else:
        run_status = "ok"

    # ── Coverage (gap-aware; the ONE coverage metric — see _coverage.py) ─────
    try:
        from _coverage import coverage_from_traj_file
        seq_dur_meta = meta.get("sequence_duration_s")
        if not seq_dur_meta:
            # fall back to the dataset times file if present
            times_f = ds_dir / "times.txt"
            if times_f.exists():
                _tt = np.loadtxt(str(times_f), dtype=np.float64) / 1e9
                seq_dur_meta = float(_tt[-1] - _tt[0]) if len(_tt) > 1 else None
        coverage = coverage_from_traj_file(traj_path, seq_dur_meta)
    except Exception as _e:
        coverage = {"coverage_gap_pct": None, "error": str(_e)}

    # ── Runtime ───────────────────────────────────────────────────────────────
    res_path = run_dir / "resources.csv"
    runtime = parse_resources(str(res_path)) or {}
    if meta:
        runtime["wall_s"] = round(meta.get("duration_s") or 0, 2)
        fps = meta.get("fps") or 0
        runtime["fps"] = round(fps, 3)
        # Real-time factor: fps / input_fps (we don't know input fps here,
        # so leave it as fps and let aggregate compute RTF from sequence metadata)
        runtime["fps_raw"] = round(fps, 3)

    # ── Machine specs (provenance for the runtime numbers above) ──────────────
    # Policy (fixed 2026-08-05): the machine block must identify the RUN host,
    # not the evaluation host — re-evaluating on another laptop must never
    # re-attribute the hardware. Priority:
    #   1. run_meta.json "machine" (written at run time by provenance-aware
    #      runners — the only fully trustworthy source);
    #   2. the machine block already present in a previous run_eval.json
    #      (recorded closer to run time; preserved, never overwritten);
    #   3. fresh collection, explicitly tagged collected_at="evaluation" so it
    #      can never be mistaken for verified run-host identity.
    machine_info = None
    if isinstance(meta.get("machine"), dict) and meta["machine"]:
        machine_info = dict(meta["machine"])
        machine_info["collected_at"] = "run"
    else:
        prev_eval = run_dir / "run_eval.json"
        if prev_eval.exists():
            try:
                prev = json.loads(prev_eval.read_text())
                pm = prev.get("machine")
                if isinstance(pm, dict) and pm and "error" not in pm:
                    machine_info = pm
            except Exception:
                pass
    if machine_info is None:
        try:
            from _system_info import collect as _collect_machine
            machine_info = _collect_machine()
            machine_info["collected_at"] = "evaluation"
            machine_info["note"] = ("machine of the EVALUATION host; run host "
                                    "unverified (run predates run-time capture)")
        except Exception as _e:  # pragma: no cover - best-effort
            machine_info = {"error": str(_e)}

    # ── Agricultural segment metrics (global SE3 alignment, 2026-08-05) ──────
    seg_path = ds_dir / "segments_auto.csv"
    agri = {}
    if seg_path.exists():
        print("[eval] computing per-segment ATE (global SE3 alignment) ...",
              file=sys.stderr)
        import csv
        keep_row_turn = distinguish_row_turn_for_dataset(dataset)
        with open(seg_path) as f:
            rows = list(csv.DictReader(f))
        agri = segment_ate_global(gt_path, est_path, rows, keep_row_turn,
                                  t_max_diff)

    # ── Assemble output ───────────────────────────────────────────────────────
    out = {
        "run":     run_id,
        "algo":    algo,
        "dataset": dataset,
        "seq":     seq,
        "run_type": rt.name,
        "use_imu": rt.use_imu,
        "use_lc":  rt.use_lc,
        "gt_source": gt_source,
        "gt_provenance": gt_provenance,
        "eval_schema": 2,          # 2 = 2026-08-05 metric fixes (see PROGRESS)
        "run_status": run_status,
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
        # Origin-only alignment (GNSS runs only; empty dict otherwise)
        "ate_origin": {
            "rmse":   ate_origin_stats.get("rmse"),
            "mean":   ate_origin_stats.get("mean"),
            "median": ate_origin_stats.get("median"),
            "max":    ate_origin_stats.get("max"),
        } if ate_origin_stats else {},
        "rpe_trans_1m": {
            "rmse": rpe_t.get("rmse"),
            "mean": rpe_t.get("mean"),
            "std":  rpe_t.get("std"),
            "max":  rpe_t.get("max"),
        },
        # No scale correction — does not absorb scale drift (2026-08-05)
        "rpe_trans_1m_se3": {
            "rmse": rpe_t_se3.get("rmse"),
            "mean": rpe_t_se3.get("mean"),
            "std":  rpe_t_se3.get("std"),
        },
        "rpe_rot_1m_deg": {
            "rmse": rpe_r.get("rmse"),
            "mean": rpe_r.get("mean"),
            "std":  rpe_r.get("std"),
        },
        "kitti_drift": kitti,
        "scale_factor":  scale,
        "final_drift_m": final_drift,
        "coverage":      coverage,
        "robustness":    robustness,
        "runtime":       runtime,
        "machine":       machine_info,
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
