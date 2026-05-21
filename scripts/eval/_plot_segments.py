#!/usr/bin/env python3
"""High-quality top-down segment maps for SLAM benchmarking.

Generates three categories of figures per <dataset>/<seq>:

  (1) PER-RUN MAPS  →  results/<dataset>/<seq>/<algo>/run<N>/segment_map.png
      GT colour-coded by row/turn + single algorithm run aligned trajectory.

  (2) PER-ALGORITHM MAPS  →  results/<dataset>/<seq>/<algo>/segment_map.png
      GT colour-coded by row/turn + all of that algorithm's runs overlaid
      (light) + the mean trajectory (bold).

  (3) CROSS-ALGORITHM COMPARISON  →  results/<dataset>/<seq>/segment_map.png
      GT colour-coded by row/turn + mean trajectory of each algorithm.

All figures are rendered at near-8K resolution (figsize 20×20 at dpi=400) so
the user can zoom in to inspect detail. The legend is always placed outside
the plot area to avoid overlapping the trajectory. GT row (green) and turn
(orange) segments are drawn as a thick, semi-transparent ribbon with marker
dots at row/turn boundaries to make them unambiguously visible while the
narrower estimate lines sit on top.

Usage:
    python3 _plot_segments.py <dataset> <seq>
        [--algos orbslam3,droidslam,macvo] [--dpi 400] [--figsize 20]
"""
import argparse
import csv
import re
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

# ── Colours ──────────────────────────────────────────────────────────────────
SEG_COLOUR = {
    "row":   "#2ca02c",      # green
    "turn":  "#ff6f00",      # vivid orange
    "other": "#bbbbbb",
}
ALGO_COLOUR = {
    "orbslam3":  "#1f77b4",  # blue
    "droidslam": "#8c564b",  # brown (was red, to keep individual-run red distinct)
    "macvo":     "#9467bd",  # purple
    "basalt":    "#d62728",  # red-orange
}
ALGO_LABEL = {
    "orbslam3":  "ORB-SLAM3",
    "droidslam": "DROID-SLAM",
    "macvo":     "MAC-VO",
    "basalt":    "Basalt",
}
INDIV_RUN_COLOUR   = "#e41a1c"   # crimson red — visible but distinct from algo means
LOOP_MARKER_COLOUR = "#ffd700"   # gold star outlined in black


def load_tum(path: Path) -> np.ndarray:
    a = np.loadtxt(path)
    return a if a.ndim == 2 else a[np.newaxis, :]


def load_segments(path: Path):
    segs = []
    with open(path) as f:
        for row in csv.DictReader(f):
            segs.append({
                "t_start": float(row["t_start"]),
                "t_end":   float(row["t_end"]),
                "type":    row["type"].strip(),
            })
    return segs


def assign_types(t: np.ndarray, segs) -> list:
    types = ["other"] * len(t)
    for seg in segs:
        for idx in np.where((t >= seg["t_start"]) & (t <= seg["t_end"]))[0]:
            types[idx] = seg["type"]
    return types

# ── Loop closure detection ──────────────────────────────────────────────────
LOOP_RE = re.compile(r"^(\d+\.\d+)\s+\*?Loop detected", re.IGNORECASE)


def find_loop_times(run_dir: Path) -> list:
    """Parse run_log.txt for ORB-SLAM3 'Loop detected' events.

    Returns a list of *sequence-relative* timestamps (seconds) — the same
    timestamps ORB-SLAM3's logger emits. Other algorithms have no equivalent
    log so the returned list is empty.
    """
    log = run_dir / "run_log.txt"
    if not log.exists():
        return []
    out = []
    try:
        with open(log) as f:
            for line in f:
                m = LOOP_RE.match(line)
                if m:
                    out.append(float(m.group(1)))
    except Exception:
        return []
    return out


def loops_to_xy(loop_times, traj_t, traj_xy):
    """Map each loop relative-time to the (x,y) on the aligned estimate."""
    if not len(loop_times) or traj_t is None or traj_xy is None or not len(traj_t):
        return np.empty((0, 2))
    t_abs = np.asarray(loop_times) + traj_t[0]
    idxs = np.argmin(np.abs(traj_t[:, None] - t_abs[None, :]), axis=0)
    return traj_xy[idxs]

# ── Loop closure detection ─────────────────────────────────────────────
LOOP_RE = re.compile(r"^(\d+\.\d+)\s+\*?Loop detected", re.IGNORECASE)


def find_loop_times(run_dir: Path) -> list:
    """Parse run_log.txt for ORB-SLAM3 'Loop detected' events.

    Returns a list of *sequence-relative* timestamps in seconds. These match the
    timestamps used inside ORB-SLAM3's logger; the wrapper preserves them.
    Other algorithms (DROID-SLAM, MAC-VO) have no log of this kind so the
    returned list is empty.
    """
    log = run_dir / "run_log.txt"
    if not log.exists():
        return []
    out = []
    try:
        with open(log) as f:
            for line in f:
                m = LOOP_RE.match(line)
                if m:
                    out.append(float(m.group(1)))
    except Exception:
        return []
    return out


def loops_to_xy(loop_times, traj_t, traj_xy):
    """Map each loop relative-time to the (x,y) on the aligned estimate.

    `traj_t` are the wrapper-rewritten absolute camera timestamps (seconds);
    relative loop times are converted by adding traj_t[0]. Closest neighbour.
    """
    if not len(loop_times) or traj_t is None or traj_xy is None or not len(traj_t):
        return np.empty((0, 2))
    t_abs = np.asarray(loop_times) + traj_t[0]
    idxs = np.argmin(np.abs(traj_t[:, None] - t_abs[None, :]), axis=0)
    return traj_xy[idxs]


# ── evo Sim3 / SE3 alignment ────────────────────────────────────────────────
def align_to_gt(gt_path: Path, traj_path: Path, correct_scale: bool):
    """Return aligned (N,3) positions, or None on failure."""
    try:
        from evo.core import sync
        from evo.tools import file_interface
        traj_ref = file_interface.read_tum_trajectory_file(str(gt_path))
        traj_est = file_interface.read_tum_trajectory_file(str(traj_path))
        traj_ref, traj_est = sync.associate_trajectories(traj_ref, traj_est, max_diff=0.05)
        traj_est.align(traj_ref, correct_scale=correct_scale, correct_only_scale=False)
        return traj_est.positions_xyz, traj_est.timestamps
    except Exception as e:
        print(f"[plot_segments] alignment failed for {traj_path}: {e}", flush=True)
        return None, None


def resample_to_grid(t: np.ndarray, xy: np.ndarray, t_grid: np.ndarray):
    """Linear-interpolate xy to the common t_grid (skip out-of-range points)."""
    if t is None or xy is None or len(t) < 2:
        return None
    order = np.argsort(t)
    t_s = t[order]
    xy_s = xy[order]
    mask = (t_grid >= t_s[0]) & (t_grid <= t_s[-1])
    if mask.sum() < 5:
        return None
    out = np.full((len(t_grid), 2), np.nan)
    out[mask, 0] = np.interp(t_grid[mask], t_s, xy_s[:, 0])
    out[mask, 1] = np.interp(t_grid[mask], t_s, xy_s[:, 1])
    return out


# ── Drawing primitives ──────────────────────────────────────────────────────
def draw_gt_segments(ax, xy_gt, types):
    """Draw GT as a thick, partially transparent ribbon coloured by segment."""
    segments, colors = [], []
    for i in range(len(xy_gt) - 1):
        segments.append([xy_gt[i], xy_gt[i + 1]])
        colors.append(SEG_COLOUR.get(types[i], SEG_COLOUR["other"]))
    # Wide, lighter band first (ribbon)
    ax.add_collection(LineCollection(
        segments, colors=colors, linewidths=6.0, alpha=0.35, zorder=1,
        capstyle="round"))
    # Narrow, dark line on top
    ax.add_collection(LineCollection(
        segments, colors=colors, linewidths=1.4, alpha=0.95, zorder=2,
        capstyle="round"))


def draw_segment_boundaries(ax, t_gt, xy_gt, segs):
    """Tiny black dots at each segment boundary along GT."""
    for seg in segs:
        for tb in (seg["t_start"], seg["t_end"]):
            idx = int(np.argmin(np.abs(t_gt - tb)))
            ax.plot(xy_gt[idx, 0], xy_gt[idx, 1],
                    marker="o", markersize=2.5, color="black",
                    zorder=4, alpha=0.7)


def draw_start_end(ax, xy_gt):
    ax.scatter(*xy_gt[0],  marker="^", s=180, facecolor="white",
               edgecolor="black", linewidths=1.5, zorder=6)
    ax.scatter(*xy_gt[-1], marker="s", s=140, facecolor="white",
               edgecolor="black", linewidths=1.5, zorder=6)


def draw_loops(ax, loop_xy):
    """Plot loop-closure detections as gold stars outlined in black."""
    if loop_xy is None or len(loop_xy) == 0:
        return
    ax.scatter(loop_xy[:, 0], loop_xy[:, 1],
               marker="*", s=380, facecolor=LOOP_MARKER_COLOUR,
               edgecolor="black", linewidths=1.2, zorder=7, alpha=0.95)


def build_legend(segs, algos_drawn, show_runs=False, n_loops=None):
    n_row  = sum(1 for s in segs if s["type"] == "row")
    n_turn = sum(1 for s in segs if s["type"] == "turn")
    d_row  = sum(s["t_end"] - s["t_start"] for s in segs if s["type"] == "row")
    d_turn = sum(s["t_end"] - s["t_start"] for s in segs if s["type"] == "turn")
    handles = [
        mpatches.Patch(color=SEG_COLOUR["row"],  alpha=0.6,
                       label=f"GT row  ({n_row} segs, {d_row:.0f} s)"),
        mpatches.Patch(color=SEG_COLOUR["turn"], alpha=0.6,
                       label=f"GT turn ({n_turn} segs, {d_turn:.0f} s)"),
    ]
    for algo, label in algos_drawn:
        handles.append(Line2D([0], [0], color=ALGO_COLOUR.get(algo, "#888"),
                              lw=1.8, label=label))
    if show_runs:
        handles.append(Line2D([0], [0], color=INDIV_RUN_COLOUR, lw=1.0,
                              alpha=0.55, label="individual runs"))
    handles.append(Line2D([0], [0], marker="^", color="black",
                          markerfacecolor="white", markersize=9, lw=0,
                          label="Start"))
    handles.append(Line2D([0], [0], marker="s", color="black",
                          markerfacecolor="white", markersize=8, lw=0,
                          label="End"))
    handles.append(Line2D([0], [0], marker="o", color="black", markersize=4,
                          lw=0, label="segment boundary"))
    if n_loops is not None and n_loops > 0:
        handles.append(Line2D([0], [0], marker="*", color="black",
                              markerfacecolor=LOOP_MARKER_COLOUR,
                              markersize=14, lw=0,
                              label=f"loop closure ({n_loops})"))
    return handles


def base_figure(dataset, seq, title_extra, figsize):
    fig, ax = plt.subplots(figsize=(figsize, figsize))
    ax.set_aspect("equal")
    ax.set_facecolor("#fafafa")
    ax.set_xlabel("X [m]", fontsize=14)
    ax.set_ylabel("Y [m]", fontsize=14)
    ax.tick_params(labelsize=12)
    ax.grid(True, which="both", alpha=0.25, lw=0.4)
    ax.set_title(f"{dataset} / {seq} — {title_extra}", fontsize=15, pad=14)
    return fig, ax


def finalise(fig, ax, handles, out_path: Path, dpi):
    # Place legend outside the plot to the right so it never overlaps.
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1.02, 0.5),
              fontsize=11, framealpha=0.95, borderaxespad=0.,
              title="Legend", title_fontsize=12)
    ax.autoscale_view()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[plot_segments] saved {out_path}", flush=True)


# ── Map generators ──────────────────────────────────────────────────────────
def plot_per_run(dataset, seq, algo, run_id, gt_xy, t_gt, types, segs,
                 ws: Path, dpi, figsize):
    res = ws / "results" / dataset / seq / algo / f"run{run_id}"
    traj = res / "trajectory.txt"
    if not traj.exists():
        return False
    gt_path = ws / "datasets" / dataset / seq / "gt_tum.txt"
    pos, ts = align_to_gt(gt_path, traj, correct_scale=True)
    loops = find_loop_times(res)
    loop_xy = loops_to_xy(loops, ts, pos[:, :2]) if pos is not None else np.empty((0, 2))
    fig, ax = base_figure(dataset, seq, f"{ALGO_LABEL.get(algo, algo)} run {run_id}",
                          figsize)
    draw_gt_segments(ax, gt_xy, types)
    draw_segment_boundaries(ax, t_gt, gt_xy, segs)
    if pos is not None:
        ax.plot(pos[:, 0], pos[:, 1], color=ALGO_COLOUR.get(algo, "#444"),
                lw=1.8, alpha=0.95, zorder=3,
                label=f"{ALGO_LABEL.get(algo, algo)} run {run_id}")
    draw_loops(ax, loop_xy)
    draw_start_end(ax, gt_xy)
    handles = build_legend(segs, [(algo, f"{ALGO_LABEL.get(algo, algo)} run {run_id}")],
                           n_loops=len(loops))
    finalise(fig, ax, handles, res / "segment_map.png", dpi)
    return True


def plot_per_algo(dataset, seq, algo, gt_xy, t_gt, types, segs,
                  ws: Path, dpi, figsize):
    algo_dir = ws / "results" / dataset / seq / algo
    if not algo_dir.exists():
        return False
    run_dirs = sorted(algo_dir.glob("run*"))
    if not run_dirs:
        return False
    gt_path = ws / "datasets" / dataset / seq / "gt_tum.txt"
    per_run = []
    all_loop_xy = []
    for rd in run_dirs:
        traj = rd / "trajectory.txt"
        if not traj.exists():
            continue
        pos, ts = align_to_gt(gt_path, traj, correct_scale=True)
        if pos is None:
            continue
        per_run.append((rd.name, ts, pos[:, :2]))
        lt = find_loop_times(rd)
        if lt:
            all_loop_xy.append(loops_to_xy(lt, ts, pos[:, :2]))
    if not per_run:
        return False
    # Common time grid = GT timestamps (drop NaN later)
    grid = t_gt
    resampled = []
    for name, ts, xy in per_run:
        rs = resample_to_grid(ts, xy, grid)
        if rs is not None:
            resampled.append(rs)
    fig, ax = base_figure(dataset, seq,
                          f"{ALGO_LABEL.get(algo, algo)} — {len(per_run)} runs + mean",
                          figsize)
    draw_gt_segments(ax, gt_xy, types)
    draw_segment_boundaries(ax, t_gt, gt_xy, segs)
    # Individual runs (semi-transparent red)
    for name, ts, xy in per_run:
        ax.plot(xy[:, 0], xy[:, 1], color=INDIV_RUN_COLOUR,
                lw=1.0, alpha=0.55, zorder=3)
    # Mean (bold)
    if resampled:
        stack = np.stack(resampled, axis=0)
        mean_xy = np.nanmean(stack, axis=0)
        valid = ~np.isnan(mean_xy[:, 0])
        ax.plot(mean_xy[valid, 0], mean_xy[valid, 1],
                color=ALGO_COLOUR.get(algo, "#444"),
                lw=2.2, alpha=0.98, zorder=4,
                label=f"{ALGO_LABEL.get(algo, algo)} mean ({len(resampled)})")
    n_loops = 0
    if all_loop_xy:
        draw_loops(ax, np.vstack(all_loop_xy))
        n_loops = sum(len(x) for x in all_loop_xy)
    draw_start_end(ax, gt_xy)
    handles = build_legend(segs,
                           [(algo, f"{ALGO_LABEL.get(algo, algo)} mean")],
                           show_runs=True, n_loops=n_loops)
    finalise(fig, ax, handles, algo_dir / "segment_map.png", dpi)
    return True


def plot_compare(dataset, seq, algos, gt_xy, t_gt, types, segs,
                 ws: Path, dpi, figsize):
    gt_path = ws / "datasets" / dataset / seq / "gt_tum.txt"
    means = {}
    loops_all = {}
    for algo in algos:
        algo_dir = ws / "results" / dataset / seq / algo
        if not algo_dir.exists():
            continue
        per_run = []
        loop_xy_list = []
        for rd in sorted(algo_dir.glob("run*")):
            traj = rd / "trajectory.txt"
            if not traj.exists():
                continue
            pos, ts = align_to_gt(gt_path, traj, correct_scale=True)
            if pos is None:
                continue
            rs = resample_to_grid(ts, pos[:, :2], t_gt)
            if rs is not None:
                per_run.append(rs)
            lt = find_loop_times(rd)
            if lt:
                loop_xy_list.append(loops_to_xy(lt, ts, pos[:, :2]))
        # Fallback: flat layout (no run*) — old single-run results
        if not per_run:
            traj = algo_dir / "trajectory.txt"
            if traj.exists():
                pos, ts = align_to_gt(gt_path, traj, correct_scale=True)
                if pos is not None:
                    rs = resample_to_grid(ts, pos[:, :2], t_gt)
                    if rs is not None:
                        per_run.append(rs)
        if per_run:
            stack = np.stack(per_run, axis=0)
            means[algo] = (np.nanmean(stack, axis=0), len(per_run))
        if loop_xy_list:
            loops_all[algo] = np.vstack(loop_xy_list)
    fig, ax = base_figure(dataset, seq, "cross-algorithm comparison (run mean)",
                          figsize)
    draw_gt_segments(ax, gt_xy, types)
    draw_segment_boundaries(ax, t_gt, gt_xy, segs)
    drawn = []
    for algo in algos:
        if algo not in means:
            continue
        mxy, n = means[algo]
        valid = ~np.isnan(mxy[:, 0])
        label = f"{ALGO_LABEL.get(algo, algo)} mean ({n} run{'s' if n > 1 else ''})"
        ax.plot(mxy[valid, 0], mxy[valid, 1],
                color=ALGO_COLOUR.get(algo, "#444"),
                lw=2.2, alpha=0.95, zorder=3, label=label)
        drawn.append((algo, label))
    # Combined loop closures (any algorithm)
    n_loops_total = 0
    if loops_all:
        combined = np.vstack(list(loops_all.values()))
        draw_loops(ax, combined)
        n_loops_total = sum(len(x) for x in loops_all.values())
    draw_start_end(ax, gt_xy)
    handles = build_legend(segs, drawn, n_loops=n_loops_total)
    finalise(fig, ax,
             handles, ws / "results" / dataset / seq / "segment_map.png", dpi)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("seq")
    ap.add_argument("--algos", default="orbslam3,droidslam,macvo,basalt")
    ap.add_argument("--dpi", type=int, default=400)
    ap.add_argument("--figsize", type=float, default=20.0)
    args = ap.parse_args()

    ws = Path(__file__).resolve().parents[2]
    ds_dir = ws / "datasets" / args.dataset / args.seq
    gt_path  = ds_dir / "gt_tum.txt"
    seg_path = ds_dir / "segments_auto.csv"
    if not gt_path.exists():
        raise SystemExit(f"GT missing: {gt_path}")
    if not seg_path.exists():
        raise SystemExit(f"segments missing: {seg_path}")

    gt = load_tum(gt_path)
    t_gt  = gt[:, 0]
    xy_gt = gt[:, 1:3]
    segs  = load_segments(seg_path)
    types = assign_types(t_gt, segs)

    algos = [a.strip() for a in args.algos.split(",") if a.strip()]

    # (1) per-run
    for algo in algos:
        algo_dir = ws / "results" / args.dataset / args.seq / algo
        if not algo_dir.exists():
            continue
        for rd in sorted(algo_dir.glob("run*")):
            run_id = rd.name.replace("run", "")
            plot_per_run(args.dataset, args.seq, algo, run_id,
                         xy_gt, t_gt, types, segs, ws, args.dpi, args.figsize)
    # (2) per-algo
    for algo in algos:
        plot_per_algo(args.dataset, args.seq, algo,
                      xy_gt, t_gt, types, segs, ws, args.dpi, args.figsize)
    # (3) cross-algorithm comparison
    plot_compare(args.dataset, args.seq, algos,
                 xy_gt, t_gt, types, segs, ws, args.dpi, args.figsize)


if __name__ == "__main__":
    main()
