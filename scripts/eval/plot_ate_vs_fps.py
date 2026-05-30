#!/usr/bin/env python3
"""ATE (SE3) vs FPS scatter plot across all algorithms and sequences.

Reads benchmark-<type>.csv and writes <results_root>/ate_vs_fps.png.
Each point = one (algo, dataset, seq) combination, mean across runs.
Error bars show std over runs when more than one run exists.
Color = algorithm. Marker shape = dataset.

Usage:
    python3 scripts/eval/plot_ate_vs_fps.py [--type vo|vio|vio-lc]
                                            [--dpi 200] [--figsize 12 7]
"""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

WS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _run_type import resolve as resolve_run_type  # noqa: E402

# ---------------------------------------------------------------------------
# Shared palette - must stay in sync with _plot_segments.py
# ---------------------------------------------------------------------------
ALGO_COLOUR = {
    "orbslam3":    "#2ca02c",
    "droidslam":   "#8c564b",
    "macvo":       "#ff7f0e",
    "basalt":      "#d62728",
    "airslam":     "#17becf",
    "mast3r_slam": "#9467bd",
    "megasam":     "#e377c2",
}
ALGO_LABEL = {
    "orbslam3":    "ORB-SLAM3",
    "droidslam":   "DROID-SLAM",
    "macvo":       "MAC-VO",
    "basalt":      "Basalt",
    "airslam":     "AirSLAM",
    "mast3r_slam": "MASt3R-SLAM",
    "megasam":     "MegaSaM",
}
DATASET_MARKER = {
    "euroc_mav":  "o",
    "hortimulti": "s",
    "rosariov2":  "D",
}
DATASET_LABEL = {
    "euroc_mav":  "EuRoC-MAV",
    "hortimulti": "HortiMulti",
    "rosariov2":  "RosarioV2",
}
# Short sequence labels for annotation
SEQ_SHORTNAME = {
    "MH_01_easy":      "MH01",
    "MH_03_medium":    "MH03",
    "MH_05_difficult": "MH05",
    "strawberry02":    "straw02",
    "strawberry03":    "straw03",
    "sequence1":       "seq1",
    "sequence5":       "seq5",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", dest="run_type", default="vo",
                    choices=["vo", "vio", "vio-lc"])
    ap.add_argument("--dpi",     type=int,   default=200)
    ap.add_argument("--figsize", nargs=2, type=float, default=[13, 8])
    args = ap.parse_args()

    rt = resolve_run_type(args.run_type, WS)
    csv_path = rt.csv_path
    if not csv_path.exists():
        raise SystemExit(f"{csv_path.name} not found at {csv_path}")

    # Collect (ate_se3, fps) per (algo, dataset, seq)
    groups = defaultdict(list)
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            try:
                ate = float(row["ate_se3_rmse_m"])
                fps = float(row["fps"])
            except (KeyError, ValueError):
                continue
            if fps <= 0 or ate <= 0:
                continue
            groups[(row["algo"], row["dataset"], row["seq"])].append((ate, fps))

    if not groups:
        raise SystemExit(f"No valid data in {csv_path.name}")

    # Compute per-group stats
    points = []
    for (algo, dataset, seq), vals in groups.items():
        ates = [v[0] for v in vals]
        fpss = [v[1] for v in vals]
        points.append({
            "algo":    algo,
            "dataset": dataset,
            "seq":     seq,
            "ate":     float(np.mean(ates)),
            "fps":     float(np.mean(fpss)),
            "ate_std": float(np.std(ates)),
            "fps_std": float(np.std(fpss)),
            "n":       len(vals),
        })

    fig, ax = plt.subplots(figsize=args.figsize)
    ax.set_facecolor("#fafafa")
    ax.grid(True, alpha=0.25, lw=0.5)

    for p in points:
        color  = ALGO_COLOUR.get(p["algo"], "#888888")
        marker = DATASET_MARKER.get(p["dataset"], "o")
        ax.scatter(p["ate"], p["fps"],
                   color=color, marker=marker, s=130,
                   edgecolors="black", linewidths=0.7,
                   zorder=4, alpha=0.88)
        # Error bars for multi-run entries
        if p["n"] > 1:
            ax.errorbar(p["ate"], p["fps"],
                        xerr=p["ate_std"] if p["ate_std"] > 0 else None,
                        yerr=p["fps_std"] if p["fps_std"] > 0 else None,
                        color=color, alpha=0.35, lw=0.9,
                        capsize=2, zorder=3)
        # Sequence label
        sname = SEQ_SHORTNAME.get(p["seq"], p["seq"])
        ax.annotate(sname, (p["ate"], p["fps"]),
                    textcoords="offset points", xytext=(4, 4),
                    fontsize=7, color="#444444", zorder=5)

    ax.set_xlabel("ATE SE(3) RMSE [m]", fontsize=13)
    ax.set_ylabel("FPS", fontsize=13)
    ax.set_title(f"ATE vs FPS - {rt.name} run-type", fontsize=14, pad=12)
    ax.tick_params(labelsize=11)

    # Legend - two separate groups: algorithms (colour) and datasets (marker)
    present_algos = sorted(
        {p["algo"] for p in points},
        key=lambda a: list(ALGO_COLOUR).index(a) if a in ALGO_COLOUR else 99)
    present_ds = sorted({p["dataset"] for p in points})

    handles_algo = [
        Line2D([0], [0], marker="o", color="w",
               markerfacecolor=ALGO_COLOUR.get(a, "#888"),
               markersize=10, markeredgecolor="black", markeredgewidth=0.7,
               label=ALGO_LABEL.get(a, a))
        for a in present_algos
    ]
    handles_ds = [
        Line2D([0], [0], marker=DATASET_MARKER.get(d, "o"), color="w",
               markerfacecolor="#888888", markersize=10,
               markeredgecolor="black", markeredgewidth=0.7,
               label=DATASET_LABEL.get(d, d))
        for d in present_ds
    ]

    leg1 = ax.legend(handles=handles_algo, loc="upper right",
                     fontsize=11, title="Algorithm", title_fontsize=11,
                     framealpha=0.95)
    ax.add_artist(leg1)
    ax.legend(handles=handles_ds, loc="lower right",
              fontsize=11, title="Dataset", title_fontsize=11,
              framealpha=0.95)

    out = rt.results_root / "ate_vs_fps.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=args.dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[plot_ate_vs_fps] saved {out}")


if __name__ == "__main__":
    main()
