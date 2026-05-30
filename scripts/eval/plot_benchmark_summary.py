#!/usr/bin/env python3
"""Generate benchmark summary plots from benchmark-<type>.csv.

Writes to <results_root>/ (e.g. results-vo/, results-vio/, results-vio-lc/):
  ate_bar.png           - grouped ATE bar chart per sequence
  scale_factor.png      - scale factor deviation from 1.0
  fps_bar.png           - FPS (speed) comparison

Usage:
    python3 scripts/eval/plot_benchmark_summary.py [--type vo|vio|vio-lc] [--dpi 180]
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
from matplotlib.patches import Patch

WS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _run_type import resolve as resolve_run_type  # noqa: E402

# ---------------------------------------------------------------------------
# Shared palette - in sync with _plot_segments.py
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

# Ordered algo list for consistent bar ordering
ALGO_ORDER = ["orbslam3", "droidslam", "macvo", "basalt", "airslam", "mast3r_slam", "megasam"]

# Display labels for sequences (grouped by dataset section)
AGR_SEQS = [
    ("rosariov2",  "sequence1",       "Rosario\nseq1"),
    ("rosariov2",  "sequence5",       "Rosario\nseq5"),
    ("hortimulti", "strawberry02",    "Horti\nstraw02"),
    ("hortimulti", "strawberry03",    "Horti\nstraw03"),
]
REF_SEQS = [
    ("euroc_mav",  "MH_01_easy",      "MH01"),
    ("euroc_mav",  "MH_03_medium",    "MH03"),
    ("euroc_mav",  "MH_05_difficult", "MH05"),
]


def load_data(csv_path: Path):
    """Return nested dict: data[algo][dataset][seq] = {ate_sim3, ate_se3, fps, scale, track_pct, std_ate}"""
    rows = list(csv.DictReader(open(csv_path)))
    grouped = defaultdict(list)
    for r in rows:
        grouped[(r["algo"], r["dataset"], r["seq"])].append(r)

    data = defaultdict(lambda: defaultdict(dict))
    for (algo, ds, seq), rs in grouped.items():
        sims = [float(r["ate_sim3_rmse_m"]) for r in rs]
        se3s = [float(r["ate_se3_rmse_m"]) for r in rs]
        fpss = [float(r["fps"]) for r in rs if float(r.get("fps") or 0) > 0]
        scales = [float(r["scale_factor"]) for r in rs]
        tracks = [float(r.get("track_pct") or 100.0) for r in rs]
        # Use frames_tracked % from a rough measure: just use ate as proxy
        data[algo][ds][seq] = {
            "ate_sim3":  float(np.mean(sims)),
            "ate_sim3_std": float(np.std(sims)) if len(sims) > 1 else 0.0,
            "ate_se3":   float(np.mean(se3s)),
            "ate_se3_std": float(np.std(se3s)) if len(se3s) > 1 else 0.0,
            "fps":       float(np.mean(fpss)) if fpss else 0.0,
            "scale":     float(np.mean(scales)),
            "n":         len(rs),
        }
    return data


# ---------------------------------------------------------------------------
# Plot 1: ATE Sim3 grouped bar chart
# ---------------------------------------------------------------------------
def plot_ate_bar(data, out_path, dpi):
    fig, axes = plt.subplots(1, 2, figsize=(16, 6),
                             gridspec_kw={"width_ratios": [4, 3]})

    for ax, seqs, title in [
        (axes[0], AGR_SEQS, "Agricultural Sequences"),
        (axes[1], REF_SEQS, "[Non-agricultural] EuRoC-MAV"),
    ]:
        n_seqs = len(seqs)
        n_algos = len(ALGO_ORDER)
        width = 0.8 / n_algos
        x = np.arange(n_seqs)

        for ai, algo in enumerate(ALGO_ORDER):
            vals = []
            errs = []
            for ds, seq, _ in seqs:
                entry = data[algo][ds].get(seq)
                if entry:
                    vals.append(entry["ate_se3"])
                    errs.append(entry["ate_se3_std"])
                else:
                    vals.append(np.nan)
                    errs.append(0.0)

            offset = (ai - n_algos / 2 + 0.5) * width
            mask = ~np.isnan(vals)
            xpos = x[mask] + offset
            ypos = np.array(vals)[mask]
            yerr = np.array(errs)[mask]

            ax.bar(xpos, ypos, width * 0.9,
                   color=ALGO_COLOUR[algo], label=ALGO_LABEL[algo],
                   yerr=yerr, error_kw={"elinewidth": 1.2, "capsize": 3},
                   alpha=0.9)

        ax.set_xticks(x)
        ax.set_xticklabels([s[2] for s in seqs], fontsize=11)
        ax.set_ylabel("ATE SE(3) RMSE [m]", fontsize=12)
        ax.set_title(title, fontsize=12)
        ax.grid(axis="y", alpha=0.3)
        ax.set_ylim(bottom=0)

    handles = [Patch(color=ALGO_COLOUR[a], label=ALGO_LABEL[a])
               for a in ALGO_ORDER]
    fig.legend(handles=handles, loc="lower center", ncol=len(ALGO_ORDER),
               fontsize=11, bbox_to_anchor=(0.5, -0.08), framealpha=0.9)
    fig.suptitle("ATE SE(3) RMSE by Algorithm and Sequence", fontsize=14, y=1.01)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[plot_summary] saved {out_path}")


# ---------------------------------------------------------------------------
# Plot 2: Scale factor (distance from 1.0)
# ---------------------------------------------------------------------------
def plot_scale_factor(data, out_path, dpi):
    fig, axes = plt.subplots(1, 2, figsize=(16, 5),
                             gridspec_kw={"width_ratios": [4, 3]})

    for ax, seqs, title in [
        (axes[0], AGR_SEQS, "Agricultural Sequences"),
        (axes[1], REF_SEQS, "[Non-agricultural] EuRoC-MAV"),
    ]:
        n_seqs = len(seqs)
        n_algos = len(ALGO_ORDER)
        width = 0.8 / n_algos
        x = np.arange(n_seqs)

        for ai, algo in enumerate(ALGO_ORDER):
            vals = []
            for ds, seq, _ in seqs:
                entry = data[algo][ds].get(seq)
                vals.append(entry["scale"] if entry else np.nan)

            offset = (ai - n_algos / 2 + 0.5) * width
            mask = ~np.isnan(vals)
            xpos = x[mask] + offset
            ypos = np.array(vals)[mask]

            ax.bar(xpos, ypos, width * 0.9,
                   color=ALGO_COLOUR[algo], label=ALGO_LABEL[algo], alpha=0.9)

        ax.axhline(1.0, color="black", linewidth=1.2, linestyle="--",
                   label="1.0")
        ax.set_xticks(x)
        ax.set_xticklabels([s[2] for s in seqs], fontsize=11)
        ax.set_ylabel("Sim(3) scale factor", fontsize=12)
        ax.set_title(title, fontsize=12)
        ax.grid(axis="y", alpha=0.3)

    handles = [Patch(color=ALGO_COLOUR[a], label=ALGO_LABEL[a])
               for a in ALGO_ORDER]
    handles.append(plt.Line2D([0], [0], color="black", linestyle="--", label="1.0"))
    fig.legend(handles=handles, loc="lower center", ncol=len(ALGO_ORDER) + 1,
               fontsize=11, bbox_to_anchor=(0.5, -0.08), framealpha=0.9)
    fig.suptitle("Sim(3) Scale Factor", fontsize=14, y=1.01)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[plot_summary] saved {out_path}")


# ---------------------------------------------------------------------------
# Plot 3: FPS comparison
# ---------------------------------------------------------------------------
def plot_fps_bar(data, out_path, dpi):
    # Combine agr + ref sequences for a single overview
    all_seqs = AGR_SEQS + REF_SEQS
    fig, ax = plt.subplots(figsize=(16, 5))

    n_seqs = len(all_seqs)
    n_algos = len(ALGO_ORDER)
    width = 0.8 / n_algos
    x = np.arange(n_seqs)

    for ai, algo in enumerate(ALGO_ORDER):
        vals = []
        for ds, seq, _ in all_seqs:
            entry = data[algo][ds].get(seq)
            vals.append(entry["fps"] if entry and entry["fps"] > 0 else np.nan)

        offset = (ai - n_algos / 2 + 0.5) * width
        mask = ~np.isnan(vals)
        xpos = x[mask] + offset
        ypos = np.array(vals)[mask]

        ax.bar(xpos, ypos, width * 0.9,
               color=ALGO_COLOUR[algo], label=ALGO_LABEL[algo], alpha=0.9)

    # Dataset separator
    ax.axvline(3.5, color="gray", linewidth=1, linestyle=":")
    ax.text(1.5, ax.get_ylim()[1] * 0.97, "Agricultural", ha="center", fontsize=10,
            color="gray", va="top")
    ax.text(5.0, ax.get_ylim()[1] * 0.97, "EuRoC-MAV (ref)", ha="center", fontsize=10,
            color="gray", va="top")

    ax.set_xticks(x)
    ax.set_xticklabels([s[2] for s in all_seqs], fontsize=11)
    ax.set_ylabel("Mean FPS", fontsize=12)
    ax.set_title("Processing Speed by Algorithm and Sequence", fontsize=13)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)

    handles = [Patch(color=ALGO_COLOUR[a], label=ALGO_LABEL[a])
               for a in ALGO_ORDER if a in ALGO_COLOUR]
    ax.legend(handles=handles, loc="upper right", fontsize=11, framealpha=0.9)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[plot_summary] saved {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", dest="run_type", default="vo",
                    choices=["vo", "vio", "vio-lc"])
    ap.add_argument("--dpi", type=int, default=180)
    args = ap.parse_args()

    rt = resolve_run_type(args.run_type, WS)
    if not rt.csv_path.exists():
        raise SystemExit(f"{rt.csv_path.name} not found at {rt.csv_path}")

    data = load_data(rt.csv_path)
    results = rt.results_root

    plot_ate_bar(data, results / "ate_bar.png", args.dpi)
    plot_scale_factor(data, results / "scale_factor.png", args.dpi)
    plot_fps_bar(data, results / "fps_bar.png", args.dpi)


if __name__ == "__main__":
    main()
