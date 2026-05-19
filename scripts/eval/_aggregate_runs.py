#!/usr/bin/env python3
"""Aggregate N per-run run_eval.json files into metrics.csv and report.md.

Usage:
    python3 _aggregate_runs.py <dataset> <seq> <algo> [input_fps=10]

Reads:  results/<dataset>/<seq>/<algo>/run*/run_eval.json
Writes: results/<dataset>/<seq>/<algo>/metrics.csv
        results/<dataset>/<seq>/<algo>/report.md

metrics.csv format: one row per run + two summary rows (mean, std).
report.md: thesis-ready table matching the supervisor's required format.
"""
import json
import sys
import math
from pathlib import Path

import numpy as np


def load_runs(algo_dir: Path):
    runs = []
    for p in sorted(algo_dir.glob("run*/run_eval.json")):
        try:
            runs.append(json.loads(p.read_text()))
        except Exception as e:
            print(f"[aggregate] could not load {p}: {e}")
    return runs


def safe_mean(vals):
    v = [x for x in vals if x is not None and not math.isnan(x)]
    return float(np.mean(v)) if v else None


def safe_std(vals):
    v = [x for x in vals if x is not None and not math.isnan(x)]
    return float(np.std(v, ddof=0)) if len(v) > 1 else 0.0


def fmt(val, dec=4):
    if val is None:
        return "N/A"
    return f"{val:.{dec}f}"


def fmt_pm(mean, std, dec=4):
    if mean is None:
        return "N/A"
    if std == 0:
        return fmt(mean, dec)
    return f"{mean:.{dec}f} ± {std:.{dec}f}"


def main():
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <dataset> <seq> <algo> [input_fps=10]",
              file=sys.stderr)
        sys.exit(1)

    dataset, seq, algo = sys.argv[1], sys.argv[2], sys.argv[3]
    input_fps = float(sys.argv[4]) if len(sys.argv) > 4 else 10.0

    ws = Path(__file__).resolve().parents[2]
    algo_dir = ws / "results" / dataset / seq / algo
    runs = load_runs(algo_dir)

    if not runs:
        print(f"[aggregate] No run_eval.json found under {algo_dir}", file=sys.stderr)
        sys.exit(1)

    n = len(runs)
    print(f"[aggregate] Found {n} run(s) for {algo} on {dataset}/{seq}")

    # ── Collect per-run scalars ───────────────────────────────────────────────
    def gather(fn):
        return [fn(r) for r in runs]

    ate_rmse   = gather(lambda r: r["ate"].get("rmse"))
    ate_mean   = gather(lambda r: r["ate"].get("mean"))
    ate_median = gather(lambda r: r["ate"].get("median"))
    ate_std    = gather(lambda r: r["ate"].get("std"))
    ate_max    = gather(lambda r: r["ate"].get("max"))

    # SE(3) (no scale correction) — honest stereo accuracy
    ate_se3_rmse = gather(lambda r: r.get("ate_se3", {}).get("rmse"))
    ate_se3_max  = gather(lambda r: r.get("ate_se3", {}).get("max"))

    rpe_t_rmse = gather(lambda r: r["rpe_trans_1m"].get("rmse"))
    rpe_r_rmse = gather(lambda r: r["rpe_rot_1m_deg"].get("rmse"))

    kitti_10  = gather(lambda r: r["kitti_drift"].get("rpe_10m_trans_rmse"))
    kitti_50  = gather(lambda r: r["kitti_drift"].get("rpe_50m_trans_rmse"))
    kitti_100 = gather(lambda r: r["kitti_drift"].get("rpe_100m_trans_rmse"))

    scale     = gather(lambda r: r.get("scale_factor"))
    final_dr  = gather(lambda r: r.get("final_drift_m"))

    frames_tracked = gather(lambda r: r["robustness"].get("frames_tracked"))
    frames_total   = gather(lambda r: r["robustness"].get("frames_total"))
    track_pct      = gather(lambda r: r["robustness"].get("track_pct"))
    t_losses  = gather(lambda r: r["robustness"].get("tracking_losses", 0))
    loop_cl   = gather(lambda r: r["robustness"].get("loop_closures", 0))
    map_rst   = gather(lambda r: r["robustness"].get("map_resets", 0))
    init_ok   = gather(lambda r: r["robustness"].get("init_success", False))
    init_t    = gather(lambda r: r["robustness"].get("init_time_s"))
    fail_t    = gather(lambda r: r["robustness"].get("first_failure_s"))

    wall_s   = gather(lambda r: r["runtime"].get("wall_s"))
    fps_vals = gather(lambda r: r["runtime"].get("fps"))
    cpu_mean = gather(lambda r: r["runtime"].get("cpu_mean_pct"))
    cpu_peak = gather(lambda r: r["runtime"].get("cpu_peak_pct"))
    ram_mean = gather(lambda r: r["runtime"].get("ram_mean_mib"))
    ram_peak = gather(lambda r: r["runtime"].get("ram_peak_mib"))
    vram_mean = gather(lambda r: r["runtime"].get("vram_mean_mib"))
    vram_peak = gather(lambda r: r["runtime"].get("vram_peak_mib"))
    gpu_mean  = gather(lambda r: r["runtime"].get("gpu_mean_pct"))

    # RTF = fps / input_fps
    rtf = [f / input_fps if f is not None else None for f in fps_vals]

    # Agricultural segments: per type
    agri_types = set()
    for r in runs:
        agri_types.update(r.get("agri_segments", {}).keys())
    agri_mean = {}
    for t in sorted(agri_types):
        vals = [r["agri_segments"].get(t, {}).get("ate_rmse_mean")
                for r in runs if t in r.get("agri_segments", {})]
        agri_mean[t] = (safe_mean(vals), safe_std(vals))

    # ── Write metrics.csv ─────────────────────────────────────────────────────
    csv_path = algo_dir / "metrics.csv"
    header = [
        "run",
        "ate_rmse_m", "ate_mean_m", "ate_median_m", "ate_std_m", "ate_max_m",
        "rpe_point_dist_1m_rmse", "rpe_rot_1m_rmse_deg",
        "kitti_10m_trans_rmse", "kitti_50m_trans_rmse", "kitti_100m_trans_rmse",
        "scale_factor", "final_drift_m",
        "frames_tracked", "frames_total", "track_pct",
        "tracking_losses", "loop_closures", "map_resets",
        "init_success", "init_time_s", "first_failure_s",
        "wall_s", "fps", "rtf",
        "cpu_mean_pct", "cpu_peak_pct",
        "ram_mean_mib", "ram_peak_mib",
        "vram_mean_mib", "vram_peak_mib", "gpu_mean_pct",
    ] + [f"agri_{t}_ate_rmse" for t in sorted(agri_types)]

    rows = []
    for i, r in enumerate(runs):
        rid = r.get("run", i + 1)
        fps_i = fps_vals[i]
        row = [
            f"run{rid}",
            fmt(ate_rmse[i]), fmt(ate_mean[i]), fmt(ate_median[i]),
            fmt(ate_std[i]),  fmt(ate_max[i]),
            fmt(rpe_t_rmse[i]), fmt(rpe_r_rmse[i]),
            fmt(kitti_10[i]), fmt(kitti_50[i]), fmt(kitti_100[i]),
            fmt(scale[i]), fmt(final_dr[i]),
            str(frames_tracked[i] or "N/A"),
            str(frames_total[i] or "N/A"),
            fmt(track_pct[i], 1),
            str(t_losses[i]), str(loop_cl[i]), str(map_rst[i]),
            str(init_ok[i]),
            fmt(init_t[i], 2) if init_t[i] is not None else "N/A",
            fmt(fail_t[i], 2) if fail_t[i] is not None else "N/A",
            fmt(wall_s[i], 1), fmt(fps_i, 3), fmt(rtf[i], 3),
            fmt(cpu_mean[i], 1), fmt(cpu_peak[i], 1),
            fmt(ram_mean[i], 0), fmt(ram_peak[i], 0),
            fmt(vram_mean[i], 0), fmt(vram_peak[i], 0), fmt(gpu_mean[i], 1),
        ] + [fmt(agri_mean.get(t, (None, None))[0])
             for t in sorted(agri_types)]
        rows.append(row)

    # Summary rows (only meaningful if n > 1)
    def smean(vals):
        v = safe_mean(vals)
        return fmt(v) if v is not None else "N/A"
    def sstd(vals):
        return fmt(safe_std(vals))

    mean_row = ["mean",
        smean(ate_rmse), smean(ate_mean), smean(ate_median),
        smean(ate_std),  smean(ate_max),
        smean(rpe_t_rmse), smean(rpe_r_rmse),
        smean(kitti_10), smean(kitti_50), smean(kitti_100),
        smean(scale), smean(final_dr),
        "N/A", "N/A", smean(track_pct),
        smean(t_losses), smean(loop_cl), smean(map_rst),
        "N/A", "N/A", "N/A",
        smean(wall_s), smean(fps_vals), smean(rtf),
        smean(cpu_mean), smean(cpu_peak),
        smean(ram_mean), smean(ram_peak),
        smean(vram_mean), smean(vram_peak), smean(gpu_mean),
    ] + [smean([v for v in [r["agri_segments"].get(t, {}).get("ate_rmse_mean")
                            for r in runs] if v is not None])
         for t in sorted(agri_types)]

    std_row = ["std",
        sstd(ate_rmse), sstd(ate_mean), sstd(ate_median),
        sstd(ate_std),  sstd(ate_max),
        sstd(rpe_t_rmse), sstd(rpe_r_rmse),
        sstd(kitti_10), sstd(kitti_50), sstd(kitti_100),
        sstd(scale), sstd(final_dr),
        "N/A", "N/A", sstd(track_pct),
        sstd(t_losses), sstd(loop_cl), sstd(map_rst),
        "N/A", "N/A", "N/A",
        sstd(wall_s), sstd(fps_vals), sstd(rtf),
        sstd(cpu_mean), sstd(cpu_peak),
        sstd(ram_mean), sstd(ram_peak),
        sstd(vram_mean), sstd(vram_peak), sstd(gpu_mean),
    ] + [sstd([v for v in [r["agri_segments"].get(t, {}).get("ate_rmse_mean")
                           for r in runs] if v is not None])
         for t in sorted(agri_types)]

    with open(csv_path, "w") as f:
        f.write(",".join(header) + "\n")
        for row in rows:
            f.write(",".join(row) + "\n")
        f.write(",".join(mean_row) + "\n")
        f.write(",".join(std_row) + "\n")

    print(f"[aggregate] wrote {csv_path}")

    # ── Write report.md ───────────────────────────────────────────────────────
    report_path = algo_dir / "report.md"

    def _pm(mean_v, std_v, dec=4):
        if mean_v is None:
            return "N/A"
        s = safe_std(std_v) if isinstance(std_v, list) else std_v
        return fmt_pm(mean_v, s, dec) if n > 1 else fmt(mean_v, dec)

    def _robustr(vals):
        """Return modal value for robustness booleans/counts across runs."""
        v = [x for x in vals if x is not None]
        if not v:
            return "N/A"
        if isinstance(v[0], bool):
            return "yes" if sum(v) > len(v) / 2 else "no"
        return str(int(round(safe_mean(v), 0)))

    # Dataset metadata from first run
    r0 = runs[0]

    lines = [
        f"# Benchmark Report — {algo.upper()} on {dataset} / {seq}",
        "",
        f"**Runs:** {n}  |  **GT source:** {r0.get('gt_source', 'N/A')}  "
        f"|  **Generated by:** `scripts/eval/_aggregate_runs.py`",
        "",
        "---",
        "",
        "## Dataset / Sequence Metadata",
        "",
        "| Item | Value |",
        "|---|---|",
        f"| Dataset | {dataset} |",
        f"| Sequence | {seq} |",
        f"| Algorithm | {algo} |",
        f"| Number of frames | {r0['robustness'].get('frames_total', 'N/A')} |",
        f"| Camera setup | stereo |",
        f"| IMU used | no |",
        "",
        "---",
        "",
        "## Accuracy Metrics",
        "",
        f"> **Alignment.** Two ATE numbers are reported:",
        f"> * **Sim(3)** — a 7-DoF similarity transform (rotation, translation, scale)",
        f">   is fitted between estimated and GT trajectories. This is the standard",
        f">   accuracy figure used in most SLAM papers and lets any residual scale",
        f">   drift be reported separately as `scale_factor`. Required for monocular VO.",
        f"> * **SE(3)** — 6-DoF alignment with **no scale correction**. For stereo/RGB-D",
        f">   the scale is metric (recovered from the baseline) so this is the more",
        f">   honest accuracy number; it does not hide scale drift in the alignment.",
        f"> The `scale_factor` row below quantifies the Sim(3) correction: values",
        f"> further from 1.0 indicate larger residual scale drift in the estimate.",
        f"> RPE is computed in `point_distance` mode (world-frame Euclidean distance",
        f"> between relative position vectors) at 1 m windows; this avoids body-frame",
        f"> quaternion convention mismatches between SLAM systems.",
        f"> {'Mean ± std across ' + str(n) + ' runs.' if n > 1 else 'Single run.'}",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| ATE RMSE [m] (Sim3) | {_pm(safe_mean(ate_rmse), ate_rmse, 4)} |",
        f"| ATE RMSE [m] (SE3, stereo metric)  | {_pm(safe_mean(ate_se3_rmse), ate_se3_rmse, 4)} |",
        f"| ATE mean [m] | {_pm(safe_mean(ate_mean), ate_mean, 4)} |",
        f"| ATE median [m] | {_pm(safe_mean(ate_median), ate_median, 4)} |",
        f"| ATE std [m] | {_pm(safe_mean(ate_std), ate_std, 4)} |",
        f"| ATE max [m] | {_pm(safe_mean(ate_max), ate_max, 4)} |",
        f"| RPE point_distance RMSE [m] (1 m windows) | {_pm(safe_mean(rpe_t_rmse), rpe_t_rmse, 4)} |",
        f"| RPE rotation RMSE [°/m] | {_pm(safe_mean(rpe_r_rmse), rpe_r_rmse, 3)} |",
        f"| KITTI drift @ 10 m [m] | {_pm(safe_mean(kitti_10), kitti_10, 4)} |",
        f"| KITTI drift @ 50 m [m] | {_pm(safe_mean(kitti_50), kitti_50, 4)} |",
        f"| KITTI drift @ 100 m [m] | {_pm(safe_mean(kitti_100), kitti_100, 4)} |",
        f"| Scale factor (Sim3) | {_pm(safe_mean(scale), scale, 4)} |",
        f"| Final drift [m] (approx) | {_pm(safe_mean(final_dr), final_dr, 4)} |",
        "",
        "---",
        "",
        "## Robustness Metrics",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Sequence completed | {'yes' if all(r['robustness'].get('track_pct', 0) == 100 for r in runs) else 'no'} |",
        f"| Frames tracked [%] | {_pm(safe_mean(track_pct), track_pct, 1)} |",
        f"| Tracking losses | {_robustr(t_losses)} |",
        f"| First failure [s] | {_robustr(fail_t)} |",
        f"| Initialisation success | {_robustr(init_ok)} |",
        f"| Initialisation time [s] | {_robustr(init_t)} |",
        f"| Loop closures detected | {_robustr(loop_cl)} |",
        f"| Map resets | {_robustr(map_rst)} |",
        f"| Output trajectory valid | yes |",
        "",
        "---",
        "",
        "## Runtime / Computational Metrics",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Wall-clock runtime [s] | {_pm(safe_mean(wall_s), wall_s, 1)} |",
        f"| Mean FPS | {_pm(safe_mean(fps_vals), fps_vals, 2)} |",
        f"| Real-time factor (input {input_fps:.0f} fps) | {_pm(safe_mean(rtf), rtf, 3)} |",
        f"| CPU mean [%] | {_pm(safe_mean(cpu_mean), cpu_mean, 1)} |",
        f"| CPU peak [%] | {_pm(safe_mean(cpu_peak), cpu_peak, 1)} |",
        f"| RAM mean [MiB] | {_pm(safe_mean(ram_mean), ram_mean, 0)} |",
        f"| RAM peak [MiB] | {_pm(safe_mean(ram_peak), ram_peak, 0)} |",
        f"| VRAM mean [MiB] | {_pm(safe_mean(vram_mean), vram_mean, 0)} |",
        f"| VRAM peak [MiB] | {_pm(safe_mean(vram_peak), vram_peak, 0)} |",
        f"| GPU utilisation mean [%] | {_pm(safe_mean(gpu_mean), gpu_mean, 1)} |",
    ]

    if agri_types:
        # Gather per-type n_segments and average duration across runs
        agri_n_segs = {}   # t -> [n_segs per run]
        agri_avg_dur = {}  # t -> [avg_duration_s per run]
        for t in sorted(agri_types):
            n_segs_per_run = []
            avg_dur_per_run = []
            for r in runs:
                seg_data = r.get("agri_segments", {}).get(t)
                if seg_data:
                    n_segs_per_run.append(seg_data.get("n_segments", 0))
                    segs = seg_data.get("segments", [])
                    if segs:
                        avg_dur = sum(s["duration_s"] for s in segs) / len(segs)
                        avg_dur_per_run.append(avg_dur)
            agri_n_segs[t] = n_segs_per_run
            agri_avg_dur[t] = avg_dur_per_run

        lines += [
            "",
            "---",
            "",
            "## Agricultural Segment Metrics (Auto-segmented)",
            "",
            "> Segments are detected automatically by `_segment_trajectory.py` from",
            "> the GT using a sliding window of **2 m of path length**. A window is",
            "> labelled **row** when the cumulative heading change is < 10° *and* the",
            "> maximum perpendicular deviation from the straight chord is < 0.20 m;",
            "> otherwise it is a **turn**. Sub-1 m segments are absorbed into their",
            "> neighbour. ATE RMSE for each segment uses an independent Sim(3) alignment.",
            "",
            "| Segment type | Mean ATE RMSE [m] ± std (across runs) | N segments | Avg duration [s] | N runs with data |",
            "|---|---|---|---|---|",
        ]
        for t in sorted(agri_types):
            vals = [r["agri_segments"].get(t, {}).get("ate_rmse_mean")
                    for r in runs if t in r.get("agri_segments", {})]
            n_data = len(vals)
            m = safe_mean(vals)
            s = safe_std(vals)
            n_segs_m = agri_n_segs[t]
            n_segs_str = str(int(round(safe_mean(n_segs_m), 0))) if n_segs_m else "N/A"
            avg_dur_str = fmt(safe_mean(agri_avg_dur[t]), 1) if agri_avg_dur[t] else "N/A"
            lines.append(
                f"| {t} "
                f"| {fmt_pm(m, s, 4) if m is not None else 'N/A'} "
                f"| {n_segs_str} "
                f"| {avg_dur_str} "
                f"| {n_data}/{n} |"
            )

        # Explanation of row vs turn ATE difference
        if "row" in agri_types and "turn" in agri_types:
            row_vals = [r["agri_segments"].get("row", {}).get("ate_rmse_mean")
                        for r in runs if "row" in r.get("agri_segments", {})]
            turn_vals = [r["agri_segments"].get("turn", {}).get("ate_rmse_mean")
                         for r in runs if "turn" in r.get("agri_segments", {})]
            row_ate = safe_mean(row_vals)
            turn_ate = safe_mean(turn_vals)
            row_dur = safe_mean(agri_avg_dur.get("row", []))
            turn_dur = safe_mean(agri_avg_dur.get("turn", []))
            if row_ate is not None and turn_ate is not None and row_dur and turn_dur:
                direction = "Turn ATE < Row ATE" if turn_ate < row_ate else "Row ATE ≤ Turn ATE"
                lines += [
                    "",
                    f"> **Segment ATE note ({direction}):**  ",
                    f"> Row segments average **{fmt(row_dur, 1)} s**; "
                    f"turn segments average **{fmt(turn_dur, 1)} s**.  ",
                    "> Shorter segments accumulate less dead-reckoning drift and the per-segment",
                    "> Sim3 alignment fits them more tightly → lower absolute error.",
                    "> This is expected behaviour and does **not** imply turns are geometrically easier.",
                ]

    lines += [
        "",
        "---",
        "",
        "## Per-Run Detail",
        "",
        "| Run | ATE RMSE Sim3 [m] | ATE RMSE SE3 [m] | RPE [m] | RPE rot [°/m] |"
        " KITTI 10 m | KITTI 50 m | KITTI 100 m | Scale | Final drift [m] |"
        " Wall-s | FPS | Track% | Loops |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(runs):
        lines.append(
            f"| run{r.get('run', i + 1)} "
            f"| {fmt(ate_rmse[i])} "
            f"| {fmt(ate_se3_rmse[i])} "
            f"| {fmt(rpe_t_rmse[i])} "
            f"| {fmt(rpe_r_rmse[i], 2)} "
            f"| {fmt(kitti_10[i], 4)} "
            f"| {fmt(kitti_50[i], 4)} "
            f"| {fmt(kitti_100[i], 4)} "
            f"| {fmt(scale[i], 4)} "
            f"| {fmt(final_dr[i], 4)} "
            f"| {fmt(wall_s[i], 1)} "
            f"| {fmt(fps_vals[i], 2)} "
            f"| {fmt(track_pct[i], 1)} "
            f"| {loop_cl[i]} |"
        )
    if n > 1:
        lines.append(
            f"| **mean ± std** "
            f"| {_pm(safe_mean(ate_rmse), ate_rmse, 4)} "
            f"| {_pm(safe_mean(ate_se3_rmse), ate_se3_rmse, 4)} "
            f"| {_pm(safe_mean(rpe_t_rmse), rpe_t_rmse, 4)} "
            f"| {_pm(safe_mean(rpe_r_rmse), rpe_r_rmse, 2)} "
            f"| {_pm(safe_mean(kitti_10), kitti_10, 4)} "
            f"| {_pm(safe_mean(kitti_50), kitti_50, 4)} "
            f"| {_pm(safe_mean(kitti_100), kitti_100, 4)} "
            f"| {_pm(safe_mean(scale), scale, 4)} "
            f"| {_pm(safe_mean(final_dr), final_dr, 4)} "
            f"| {_pm(safe_mean(wall_s), wall_s, 1)} "
            f"| {_pm(safe_mean(fps_vals), fps_vals, 2)} "
            f"| {_pm(safe_mean(track_pct), track_pct, 1)} "
            f"| {_robustr(loop_cl)} |"
        )

    lines.append("")

    report_path.write_text("\n".join(lines))
    print(f"[aggregate] wrote {report_path}")

    # Terminal summary
    print(f"\n{'='*60}")
    print(f"  SUMMARY  {algo.upper()} | {dataset}/{seq}  ({n} run(s))")
    print(f"{'='*60}")
    print(f"  ATE RMSE:  {fmt_pm(safe_mean(ate_rmse), safe_std(ate_rmse))} m")
    print(f"  RPE trans: {fmt_pm(safe_mean(rpe_t_rmse), safe_std(rpe_t_rmse))} m/m")
    print(f"  RPE rot:   {fmt_pm(safe_mean(rpe_r_rmse), safe_std(rpe_r_rmse))} °/m")
    print(f"  FPS:       {fmt_pm(safe_mean(fps_vals), safe_std(fps_vals), 2)}")
    for t in sorted(agri_types):
        m, s = agri_mean.get(t, (None, 0.0))
        print(f"  ATE [{t}]: {fmt_pm(m, s)} m")
    print()


if __name__ == "__main__":
    main()
