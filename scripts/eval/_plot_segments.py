#!/usr/bin/env python3
"""High-quality top-down segment maps for SLAM benchmarking.

Generates three categories of figures per <dataset>/<seq>:

  (1) PER-RUN MAPS       -> results/<run-type>/<dataset>/<seq>/<algo>/run<N>/segment_map.png
      GT dashed black + single algorithm run aligned trajectory.

  (2) PER-ALGORITHM MAPS -> results/<run-type>/<dataset>/<seq>/<algo>/segment_map.png
      GT dashed black + all of that algorithm's runs overlaid (grey) +
      the mean trajectory (bold, algo-coloured).

  (3) CROSS-ALGORITHM    -> results/<run-type>/<dataset>/<seq>/segment_map.png
      GT dashed black + mean trajectory of each algorithm.

Alongside each segment_map.png a segment_map_3d.png is generated showing
the same data with X/Y/Z axes.

Usage:
    python3 _plot_segments.py <dataset> <seq>
        [--algos orbslam3,macvo,basalt,airslam,mast3r_slam,megasam]
        [--type vo|vo-lc|vio|vio-lc|gnss-vio] [--dpi 400] [--figsize 20]
"""
import argparse
import sys
import warnings
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _run_type import canonicalize_dataset, resolve as resolve_run_type  # noqa: E402

# ---------------------------------------------------------------------------
# Colour palette - consistent across all plots
# ---------------------------------------------------------------------------
ALGO_COLOUR = {
    "orbslam3":        "#2ca02c",   # green
    "macvo":           "#ff7f0e",   # orange
    "basalt":          "#d62728",   # red
    "airslam":         "#17becf",   # light blue
    "ov2slam":         "#1b9e77",   # teal-green
    "mast3r_slam":     "#9467bd",   # purple
    "megasam":         "#e377c2",   # pink
    "dpvo":            "#ffbb78",   # light orange
    # GNSS-VIO algorithms
    "cifasis_gnss_si": "#1f77b4",   # blue
    "vins_fusion_gps": "#bcbd22",   # yellow-green
    "rtabmap_gps":     "#7f7f7f",   # grey
    "openvins_gps":    "#ff9896",   # salmon (was label-only: fell back to a
                                    # default indistinguishable from rtabmap_gps)
    # VIO algorithms.
    # NOTE: the ten tab10 colours are all claimed above, so these use tab20b
    # darks to stay mutually distinguishable. plot_ate_vs_fps.py and
    # plot_benchmark_summary.py assign okvis2x=#1f77b4 / okvis2=#bcbd22, which
    # collide with cifasis_gnss_si / vins_fusion_gps *here* -- those files plot
    # one run-type at a time so they never draw both, but the "shared palette"
    # comment in them is aspirational, not actual.
    "okvis2x":         "#393b79",   # dark indigo
    "okvis2":          "#8c6d31",   # dark olive
    "openvins":        "#843c39",   # dark brick
    "voxel_svio":      "#7b4173",   # dark magenta
}
ALGO_LABEL = {
    "orbslam3":        "ORB-SLAM3",
    "macvo":           "MAC-VO",
    "basalt":          "Basalt",
    "airslam":         "AirSLAM",
    "ov2slam":         "OV2SLAM",
    "mast3r_slam":     "MASt3R-SLAM",
    "megasam":         "MegaSaM",
    "dpvo":            "DPV-SLAM",
    # GNSS-VIO algorithms
    "cifasis_gnss_si": "CIFASIS GNSS-SI",
    "vins_fusion_gps": "VINS-Fusion+GPS",
    "rtabmap_gps":     "RTAB-Map+GPS",
    "openvins_gps":    "OpenVINS+GPS",
    # VIO algorithms
    "okvis2x":         "OKVIS2-X",
    "okvis2":          "OKVIS2",
    "openvins":        "OpenVINS",
    "voxel_svio":      "Voxel-SVIO",
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
# Sim(3) alignment
# ---------------------------------------------------------------------------
def associate_tum(ref: np.ndarray, est: np.ndarray, max_diff: float = 0.05):
    """Nearest-timestamp association for TUM arrays."""
    ref_t = ref[:, 0]
    ref_xyz = []
    est_xyz = []
    est_ts = []
    for row in est:
        j = int(np.argmin(np.abs(ref_t - row[0])))
        if abs(ref_t[j] - row[0]) <= max_diff:
            ref_xyz.append(ref[j, 1:4])
            est_xyz.append(row[1:4])
            est_ts.append(row[0])
    if len(ref_xyz) < 3:
        return None, None, None
    return np.asarray(ref_xyz), np.asarray(est_xyz), np.asarray(est_ts)


def umeyama_align(src: np.ndarray, dst: np.ndarray, correct_scale: bool = True):
    """Align src to dst with SE(3) or Sim(3), matching evo's plot use."""
    src_mean = src.mean(axis=0)
    dst_mean = dst.mean(axis=0)
    src_c = src - src_mean
    dst_c = dst - dst_mean

    cov = (dst_c.T @ src_c) / len(src)
    u, singular_values, vt = np.linalg.svd(cov)
    sign = np.eye(3)
    if np.linalg.det(u @ vt) < 0:
        sign[-1, -1] = -1
    rot = u @ sign @ vt

    scale = 1.0
    if correct_scale:
        var_src = np.sum(src_c * src_c) / len(src)
        if var_src <= 0:
            return None
        scale = float(np.sum(singular_values * np.diag(sign)) / var_src)

    trans = dst_mean - scale * (rot @ src_mean)
    return (scale * (rot @ src.T)).T + trans


def align_to_gt(gt_path: Path, traj_path: Path, correct_scale: bool = True):
    """Return aligned positions_xyz (N,3) and timestamps, or (None, None)."""
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
        try:
            ref = load_tum(gt_path)
            est = load_tum(traj_path)
            ref_xyz, est_xyz, est_ts = associate_tum(ref, est)
            if ref_xyz is None:
                raise RuntimeError("too few timestamp associations") from exc
            aligned = umeyama_align(est_xyz, ref_xyz, correct_scale=correct_scale)
            if aligned is None:
                raise RuntimeError("degenerate trajectory") from exc
            return aligned, est_ts
        except Exception as fallback_exc:
            print(f"[plot_segments] alignment failed for {traj_path}: "
                  f"{exc}; fallback failed: {fallback_exc}", flush=True)
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
    # Equal data aspect: make one metre look the same length on every axis so
    # the vertical (z) is not squashed relative to x/y. The autoscaled limits
    # are final by now; scale the box to the actual data spans (guard against a
    # degenerate/flat axis producing a zero-size box).
    spans = [hi - lo for lo, hi in
             (ax.get_xlim3d(), ax.get_ylim3d(), ax.get_zlim3d())]
    spans = [s if s > 1e-9 else 1e-9 for s in spans]
    ax.set_box_aspect(spans)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[plot_segments] saved {out_path}", flush=True)


# ---------------------------------------------------------------------------
# Per-run
# ---------------------------------------------------------------------------
def plot_per_run(dataset, seq, algo, run_id, gt_xyz, t_gt,
                 ws, results_root, dpi, figsize):
    res = results_root / dataset / seq / algo / f"run{run_id}"
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
def plot_per_algo(dataset, seq, algo, gt_xyz, t_gt, ws, results_root, dpi, figsize):
    algo_dir = results_root / dataset / seq / algo
    if not algo_dir.exists():
        return False
    run_dirs = [rd for rd in sorted(algo_dir.glob("run*"))
                if (rd / "COMPLETE").is_file()]
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
def plot_compare(dataset, seq, algos, gt_xyz, t_gt, ws, results_root, dpi, figsize):
    gt_path = ws / "datasets" / dataset / seq / "gt_tum.txt"

    means_2d = {}
    means_3d = {}

    for algo in algos:
        algo_dir = results_root / dataset / seq / algo
        if not algo_dir.exists():
            continue
        runs_2d, runs_3d = [], []
        for rd in sorted(algo_dir.glob("run*")):
            if not (rd / "COMPLETE").is_file():
                continue
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
                results_root / dataset / seq / "segment_map.png", dpi)

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
                results_root / dataset / seq / "segment_map_3d.png", dpi)

    return True


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("seq")
    ap.add_argument("--algos",
                    default="orbslam3,macvo,basalt,airslam,ov2slam,mast3r_slam,"
                            "megasam,dpvo,okvis2,okvis2x,openvins,voxel_svio,"
                            "cifasis_gnss_si,vins_fusion_gps,rtabmap_gps,"
                            "openvins_gps")
    ap.add_argument("--type", dest="run_type", default="vo",
                    choices=["vo", "vo-lc", "vio", "vio-lc", "gnss-vio"],
                    help="Which results tree to read (default: vo)")
    ap.add_argument("--dpi",     type=int,   default=400)
    ap.add_argument("--figsize", type=float, default=20.0)
    args = ap.parse_args()
    args.dataset = canonicalize_dataset(args.dataset)

    ws = Path(__file__).resolve().parents[2]
    rt = resolve_run_type(args.run_type, ws)
    results_root = rt.results_root

    gt_path = ws / "datasets" / args.dataset / args.seq / "gt_tum.txt"
    if not gt_path.exists():
        raise SystemExit(f"GT missing: {gt_path}")

    gt     = load_tum(gt_path)
    t_gt   = gt[:, 0]
    gt_xyz = gt[:, 1:4]   # x, y, z

    algos = [a.strip() for a in args.algos.split(",") if a.strip()]

    # (1) per-run
    for algo in algos:
        algo_dir = results_root / args.dataset / args.seq / algo
        if not algo_dir.exists():
            continue
        for rd in sorted(algo_dir.glob("run*")):
            if not (rd / "COMPLETE").is_file():
                continue
            run_id = rd.name.replace("run", "")
            plot_per_run(args.dataset, args.seq, algo, run_id,
                         gt_xyz, t_gt, ws, results_root, args.dpi, args.figsize)

    # (2) per-algo
    for algo in algos:
        plot_per_algo(args.dataset, args.seq, algo,
                      gt_xyz, t_gt, ws, results_root, args.dpi, args.figsize)

    # (3) cross-algorithm comparison
    plot_compare(args.dataset, args.seq, algos,
                 gt_xyz, t_gt, ws, results_root, args.dpi, args.figsize)


if __name__ == "__main__":
    main()
