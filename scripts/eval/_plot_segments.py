#!/usr/bin/env python3
"""High-quality top-down segment maps for SLAM benchmarking.

Generates three categories of figures per <dataset>/<seq>:

  (1) PER-RUN MAPS       -> results/<dataset>/<seq>/<algo>/run<N>/segment_map.png
      GT dashed black + single algorithm run aligned trajectory.

  (2) PER-ALGORITHM MAPS -> results/<dataset>/<seq>/<algo>/segment_map.png
      GT dashed black + all of that algorithm's runs overlaid (grey) +
      the mean trajectory (bold, algo-coloured).

  (3) CROSS-ALGORITHM    -> results/<dataset>/<seq>/segment_map.png
      GT dashed black + mean trajectory of each algorithm.

Alongside each segment_map.png a segment_map_3d.png is generated showing
the same data with X/Y/Z axes.

Usage:
    python3 _plot_segments.py <dataset> <seq>
        [--algos orbslam3,droidslam,macvo,basalt,airslam] [--dpi 400] [--figsize 20]
"""
import argparse
import warnings
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# ---------------------------------------------------------------------------
# Colour palette - consistent across all plots
# ---------------------------------------------------------------------------
ALGO_COLOUR = {
    "orbslam3":  "#2ca02c",   # green
    "droidslam": "#8c564b",   # brown
    "macvo":     "#ff7f0e",   # orange
    "basalt":    "#d62728",   # red
    "airslam":   "#17becf",   # light blue
}
ALGO_LABEL = {
    "orbslam3":  "ORB-SLAM3",
    "droidslam": "DROID-SLAM",
    "macvo":     "MAC-VO",
    "basalt":    "Basalt",
    "airslam":   "AirSLAM",
}

GT_COLOUR    = "black"
GT_LS        = "--"
GT_LW        = 1.6     # slightly thicker so GT stays readable
INDIV_LW     = 0.8     # individual run lines
INDIV_ALPHA  = 0.45
INDIV_COLOUR = "#aaaaaa"   # neutral grey keeps focus on the mean
MEAN_LW      = 1.3     # algo mean / single-run line


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------
def load_tum(path: Path) -> np.ndarray:
    a = np.loadtxt(path)
    return a if a.ndim == 2 else a[np.newaxis, :]


# ---------------------------------------------------------------------------
# evo Sim(3) alignment
# ---------------------------------------------------------------------------
def align_to_gt(gt_path: Path, traj_path: Path, correct_scale: bool = True):
    """Return (positions_xyz (N,3), timestamps (N,)) via evo, or (None, None)."""
    try:
        from evo.core import sync
        from evo.tools import file_interface
        traj_ref = file_interface.read_tum_trajectory_file(str(gt_path))
        traj_est = file_interface.read_tum_trajectory_file(str(traj_path))
        traj_ref, traj_est = sync.associate_trajectories(
            traj_ref, traj_est, max_diff=0.05)
        traj_est.align(traj_ref, correct_scale=correct_scale,
                       correct_only_scale=False)
        return traj_est.positions_xyz, traj_est.timestamps
    except Exception as exc:
        print(f"[plot_segments] alignment failed for {traj_path}: {exc}",
              flush=True)
        return None, None


def resample_to_grid(t: np.ndarray, xyz: np.ndarray,
                     t_grid: np.ndarray):
    """Linearly interpolate xyz (N-col) to t_grid; returns None if too few points."""
    if t is None or xyz is None or len(t) < 2:
        return None
    order = np.argsort(t)
    t_s, xyz_s = t[order], xyz[order]
    ncols = xyz_s.shape[1]
    mask = (t_grid >= t_s[0]) & (t_grid <= t_s[-1])
    if mask.sum() < 5:
        return None
    out = np.full((len(t_grid), ncols), np.nan)
    for c in range(ncols):
        out[mask, c] = np.interp(t_grid[mask], t_s, xyz_s[:, c])
    return out


# ---------------------------------------------------------------------------
# Drawing primitives
# ---------------------------------------------------------------------------
def draw_gt_2d(ax, xy_gt):
    ax.plot(xy_gt[:, 0], xy_gt[:, 1],
            color=GT_COLOUR, lw=GT_LW, ls=GT_LS, zorder=2, alpha=0.9)


def draw_gt_3d(ax, xyz_gt):
    ax.plot(xyz_gt[:, 0], xyz_gt[:, 1], xyz_gt[:, 2],
            color=GT_COLOUR, lw=GT_LW, ls=GT_LS, zorder=2, alpha=0.9)


def draw_start_end_2d(ax, xy):
    ax.scatter(xy[0, 0],  xy[0, 1],
               marker="^", s=180, facecolor="white",
               edgecolor="black", linewidths=1.5, zorder=6)
    ax.scatter(xy[-1, 0], xy[-1, 1],
               marker="s", s=140, facecolor="white",
               edgecolor="black", linewidths=1.5, zorder=6)


def draw_start_end_3d(ax, xyz):
    ax.scatter(xyz[0, 0],  xyz[0, 1],  xyz[0, 2],
               marker="^", s=180, facecolor="white",
               edgecolor="black", linewidths=1.5, zorder=6)
    ax.scatter(xyz[-1, 0], xyz[-1, 1], xyz[-1, 2],
               marker="s", s=140, facecolor="white",
               edgecolor="black", linewidths=1.5, zorder=6)


def build_legend(algos_drawn, show_runs=False):
    handles = [
        Line2D([0], [0], color=GT_COLOUR, lw=GT_LW, ls=GT_LS,
               label="Ground Truth"),
    ]
    for algo, label in algos_drawn:
        handles.append(
            Line2D([0], [0], color=ALGO_COLOUR.get(algo, "#888"),
                   lw=MEAN_LW, label=label))
    if show_runs:
        handles.append(
            Line2D([0], [0], color=INDIV_COLOUR, lw=INDIV_LW,
                   alpha=0.8, label="individual runs"))
    handles += [
        Line2D([0], [0], marker="^", color="black",
               markerfacecolor="white", markersize=9, lw=0, label="Start"),
        Line2D([0], [0], marker="s", color="black",
               markerfacecolor="white", markersize=8, lw=0, label="End"),
    ]
    return handles


# ---------------------------------------------------------------------------
# Figure factories
# ---------------------------------------------------------------------------
def base_figure(dataset, seq, title_extra, figsize):
    fig, ax = plt.subplots(figsize=(figsize, figsize))
    ax.set_aspect("equal")
    ax.set_facecolor("#fafafa")
    ax.set_xlabel("X [m]", fontsize=14)
    ax.set_ylabel("Y [m]", fontsize=14)
    ax.tick_params(labelsize=12)
    ax.grid(True, which="both", alpha=0.25, lw=0.4)
    ax.set_title(f"{dataset} / {seq} - {title_extra}", fontsize=15, pad=14)
    return fig, ax


def base_figure_3d(dataset, seq, title_extra, figsize):
    fig = plt.figure(figsize=(figsize, figsize))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlabel("x (m)", fontsize=13, labelpad=8)
    ax.set_ylabel("y (m)", fontsize=13, labelpad=8)
    ax.set_zlabel("z (m)", fontsize=13, labelpad=8)
    ax.tick_params(labelsize=11)
    ax.set_title(f"{dataset} / {seq} - {title_extra}", fontsize=15, pad=14)
    ax.view_init(elev=25, azim=-60)
    return fig, ax


# ---------------------------------------------------------------------------
# Save helpers
# ---------------------------------------------------------------------------
def finalise_2d(fig, ax, handles, out_path, dpi):
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1.02, 0.5),
              fontsize=11, framealpha=0.95, borderaxespad=0.,
              title="Legend", title_fontsize=12)
    ax.autoscale_view()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[plot_segments] saved {out_path}", flush=True)


def finalise_3d(fig, ax, handles, out_path, dpi):
    ax.legend(handles=handles, loc="upper right",
              fontsize=11, framealpha=0.95, borderaxespad=0.8,
              title="Legend", title_fontsize=12)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[plot_segments] saved {out_path}", flush=True)


# ---------------------------------------------------------------------------
# Per-run
# ---------------------------------------------------------------------------
def plot_per_run(dataset, seq, algo, run_id, gt_xyz, t_gt,
                 ws, dpi, figsize):
    res = ws / "results" / dataset / seq / algo / f"run{run_id}"
    traj = res / "trajectory.txt"
    if not traj.exists():
        return False

    gt_path = ws / "datasets" / dataset / seq / "gt_tum.txt"
    pos, _ts = align_to_gt(gt_path, traj, correct_scale=True)

    label = f"{ALGO_LABEL.get(algo, algo)} run {run_id}"
    handles = build_legend([(algo, label)])

    # -- 2D --
    fig, ax = base_figure(dataset, seq, label, figsize)
    draw_gt_2d(ax, gt_xyz[:, :2])
    if pos is not None:
        ax.plot(pos[:, 0], pos[:, 1],
                color=ALGO_COLOUR.get(algo, "#444"),
                lw=MEAN_LW, alpha=0.95, zorder=3)
    draw_start_end_2d(ax, gt_xyz[:, :2])
    finalise_2d(fig, ax, handles, res / "segment_map.png", dpi)

    # -- 3D --
    fig3, ax3 = base_figure_3d(dataset, seq, label, figsize)
    draw_gt_3d(ax3, gt_xyz)
    if pos is not None:
        ax3.plot(pos[:, 0], pos[:, 1], pos[:, 2],
                 color=ALGO_COLOUR.get(algo, "#444"),
                 lw=MEAN_LW, alpha=0.95, zorder=3)
    draw_start_end_3d(ax3, gt_xyz)
    finalise_3d(fig3, ax3, handles, res / "segment_map_3d.png", dpi)

    return True


# ---------------------------------------------------------------------------
# Per-algo (all runs + mean)
# ---------------------------------------------------------------------------
def plot_per_algo(dataset, seq, algo, gt_xyz, t_gt, ws, dpi, figsize):
    algo_dir = ws / "results" / dataset / seq / algo
    if not algo_dir.exists():
        return False
    run_dirs = sorted(algo_dir.glob("run*"))
    if not run_dirs:
        return False

    gt_path = ws / "datasets" / dataset / seq / "gt_tum.txt"
    per_run = []
    for rd in run_dirs:
        traj = rd / "trajectory.txt"
        if not traj.exists():
            continue
        pos, ts = align_to_gt(gt_path, traj, correct_scale=True)
        if pos is not None:
            per_run.append((rd.name, ts, pos))

    if not per_run:
        return False

    resampled_2d, resampled_3d = [], []
    for _name, ts, pos in per_run:
        rs2 = resample_to_grid(ts, pos[:, :2], t_gt)
        rs3 = resample_to_grid(ts, pos[:, :3], t_gt)
        if rs2 is not None:
            resampled_2d.append(rs2)
        if rs3 is not None:
            resampled_3d.append(rs3)

    algo_label = ALGO_LABEL.get(algo, algo)
    n = len(per_run)
    title_extra = f"{algo_label} - {n} run{'s' if n > 1 else ''} + mean"
    handles = build_legend([(algo, f"{algo_label} mean")], show_runs=(n > 1))

    # -- 2D --
    fig, ax = base_figure(dataset, seq, title_extra, figsize)
    draw_gt_2d(ax, gt_xyz[:, :2])
    for _name, _ts, pos in per_run:
        ax.plot(pos[:, 0], pos[:, 1],
                color=INDIV_COLOUR, lw=INDIV_LW, alpha=INDIV_ALPHA, zorder=3)
    if resampled_2d:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            mean_xy = np.nanmean(np.stack(resampled_2d, axis=0), axis=0)
        valid = ~np.isnan(mean_xy[:, 0])
        ax.plot(mean_xy[valid, 0], mean_xy[valid, 1],
                color=ALGO_COLOUR.get(algo, "#444"),
                lw=MEAN_LW, alpha=0.98, zorder=4)
    draw_start_end_2d(ax, gt_xyz[:, :2])
    finalise_2d(fig, ax, handles, algo_dir / "segment_map.png", dpi)

    # -- 3D --
    fig3, ax3 = base_figure_3d(dataset, seq, title_extra, figsize)
    draw_gt_3d(ax3, gt_xyz)
    for _name, _ts, pos in per_run:
        ax3.plot(pos[:, 0], pos[:, 1], pos[:, 2],
                 color=INDIV_COLOUR, lw=INDIV_LW, alpha=INDIV_ALPHA, zorder=3)
    if resampled_3d:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            mean_xyz = np.nanmean(np.stack(resampled_3d, axis=0), axis=0)
        valid = ~np.isnan(mean_xyz[:, 0])
        ax3.plot(mean_xyz[valid, 0], mean_xyz[valid, 1], mean_xyz[valid, 2],
                 color=ALGO_COLOUR.get(algo, "#444"),
                 lw=MEAN_LW, alpha=0.98, zorder=4)
    draw_start_end_3d(ax3, gt_xyz)
    finalise_3d(fig3, ax3, handles, algo_dir / "segment_map_3d.png", dpi)

    return True


# ---------------------------------------------------------------------------
# Cross-algorithm comparison
# ---------------------------------------------------------------------------
def plot_compare(dataset, seq, algos, gt_xyz, t_gt, ws, dpi, figsize):
    gt_path = ws / "datasets" / dataset / seq / "gt_tum.txt"

    means_2d = {}
    means_3d = {}

    for algo in algos:
        algo_dir = ws / "results" / dataset / seq / algo
        if not algo_dir.exists():
            continue
        runs_2d, runs_3d = [], []
        for rd in sorted(algo_dir.glob("run*")):
            traj = rd / "trajectory.txt"
            if not traj.exists():
                continue
            pos, ts = align_to_gt(gt_path, traj, correct_scale=True)
            if pos is None:
                continue
            rs2 = resample_to_grid(ts, pos[:, :2], t_gt)
            rs3 = resample_to_grid(ts, pos[:, :3], t_gt)
            if rs2 is not None:
                runs_2d.append(rs2)
            if rs3 is not None:
                runs_3d.append(rs3)
        # Fallback: flat layout (no run*/) - legacy single-run results
        if not runs_2d:
            traj = algo_dir / "trajectory.txt"
            if traj.exists():
                pos, ts = align_to_gt(gt_path, traj, correct_scale=True)
                if pos is not None:
                    rs2 = resample_to_grid(ts, pos[:, :2], t_gt)
                    rs3 = resample_to_grid(ts, pos[:, :3], t_gt)
                    if rs2 is not None:
                        runs_2d.append(rs2)
                    if rs3 is not None:
                        runs_3d.append(rs3)
        if runs_2d:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                means_2d[algo] = (
                    np.nanmean(np.stack(runs_2d, axis=0), axis=0), len(runs_2d))
        if runs_3d:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                means_3d[algo] = (
                    np.nanmean(np.stack(runs_3d, axis=0), axis=0), len(runs_3d))

    drawn = []
    for algo in algos:
        if algo in means_2d:
            n = means_2d[algo][1]
            drawn.append(
                (algo, f"{ALGO_LABEL.get(algo, algo)} mean"
                        f" ({n} run{'s' if n > 1 else ''})"))

    title_extra = "cross-algorithm comparison (run mean)"
    handles = build_legend(drawn)

    # -- 2D --
    fig, ax = base_figure(dataset, seq, title_extra, figsize)
    draw_gt_2d(ax, gt_xyz[:, :2])
    for algo in algos:
        if algo not in means_2d:
            continue
        mxy, _n = means_2d[algo]
        valid = ~np.isnan(mxy[:, 0])
        ax.plot(mxy[valid, 0], mxy[valid, 1],
                color=ALGO_COLOUR.get(algo, "#444"),
                lw=MEAN_LW, alpha=0.95, zorder=3)
    draw_start_end_2d(ax, gt_xyz[:, :2])
    finalise_2d(fig, ax, handles,
                ws / "results" / dataset / seq / "segment_map.png", dpi)

    # -- 3D --
    fig3, ax3 = base_figure_3d(dataset, seq, title_extra, figsize)
    draw_gt_3d(ax3, gt_xyz)
    for algo in algos:
        if algo not in means_3d:
            continue
        mxyz, _n = means_3d[algo]
        valid = ~np.isnan(mxyz[:, 0])
        ax3.plot(mxyz[valid, 0], mxyz[valid, 1], mxyz[valid, 2],
                 color=ALGO_COLOUR.get(algo, "#444"),
                 lw=MEAN_LW, alpha=0.95, zorder=3)
    draw_start_end_3d(ax3, gt_xyz)
    finalise_3d(fig3, ax3, handles,
                ws / "results" / dataset / seq / "segment_map_3d.png", dpi)

    return True


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("seq")
    ap.add_argument("--algos",
                    default="orbslam3,droidslam,macvo,basalt,airslam")
    ap.add_argument("--dpi",     type=int,   default=400)
    ap.add_argument("--figsize", type=float, default=20.0)
    args = ap.parse_args()

    ws = Path(__file__).resolve().parents[2]

    gt_path = ws / "datasets" / args.dataset / args.seq / "gt_tum.txt"
    if not gt_path.exists():
        raise SystemExit(f"GT missing: {gt_path}")

    gt     = load_tum(gt_path)
    t_gt   = gt[:, 0]
    gt_xyz = gt[:, 1:4]   # x, y, z

    algos = [a.strip() for a in args.algos.split(",") if a.strip()]

    # (1) per-run
    for algo in algos:
        algo_dir = ws / "results" / args.dataset / args.seq / algo
        if not algo_dir.exists():
            continue
        for rd in sorted(algo_dir.glob("run*")):
            run_id = rd.name.replace("run", "")
            plot_per_run(args.dataset, args.seq, algo, run_id,
                         gt_xyz, t_gt, ws, args.dpi, args.figsize)

    # (2) per-algo
    for algo in algos:
        plot_per_algo(args.dataset, args.seq, algo,
                      gt_xyz, t_gt, ws, args.dpi, args.figsize)

    # (3) cross-algorithm comparison
    plot_compare(args.dataset, args.seq, algos,
                 gt_xyz, t_gt, ws, args.dpi, args.figsize)


if __name__ == "__main__":
    main()
