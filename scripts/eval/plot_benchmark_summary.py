#!/usr/bin/env python3
"""Generate benchmark summary plots from benchmark-<type>.csv.

Writes to <results_root>/ (e.g. results-vo/, results-vo-lc/, results-vio/, results-vio-lc/):
  ate_bar.png           - grouped ATE bar chart per sequence
  scale_factor.png      - scale factor deviation from 1.0
  fps_bar.png           - FPS (speed) comparison

Usage:
    python3 scripts/eval/plot_benchmark_summary.py [--type vo|vo-lc|vio|vio-lc|gnss-vio] [--dpi 180]
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
    "okvis2x":     "#1f77b4",
    "okvis2":      "#bcbd22",
    "openvins":    "#7f7f7f",
    "voxel_svio":  "#c5b0d5",
}
ALGO_LABEL = {
    "orbslam3":    "ORB-SLAM3",
    "droidslam":   "DROID-SLAM",
    "macvo":       "MAC-VO",
    "basalt":      "Basalt",
    "airslam":     "AirSLAM",
    "mast3r_slam": "MASt3R-SLAM",
    "megasam":     "MegaSaM",
    "okvis2x":     "OKVIS2-X",
    "okvis2":      "OKVIS2",
    "openvins":    "OpenVINS",
    "voxel_svio":  "Voxel-SVIO",
}

# Preferred bar ordering. The actual per-plot list is filtered to algorithms
# present in the data (see algos_present), so VO/VIO/VIO-LC each show only their
# own algorithms and nothing is silently dropped or shown as an empty legend.
ALGO_ORDER = ["orbslam3", "droidslam", "macvo", "basalt", "airslam",
              "mast3r_slam", "megasam", "okvis2", "okvis2x", "openvins", "voxel_svio"]

# EuRoC is stored under three interchangeable spellings in the CSVs
# (euroc / euroc_mav / EuRoC-MAV are symlinks to the same data). Canonicalise
# to one key so a plot lookup matches regardless of which spelling a run used.
DATASET_ALIASES = {"euroc": "euroc_mav", "EuRoC-MAV": "euroc_mav"}


def canon_dataset(name):
    return DATASET_ALIASES.get(name, name)


def algos_present(data):
    """ALGO_ORDER filtered to algorithms that actually have >=1 entry in data."""
    return [a for a in ALGO_ORDER
            if a in data and any(data[a][ds] for ds in data[a])]


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
        grouped[(r["algo"], canon_dataset(r["dataset"]), r["seq"])].append(r)

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

    algos = algos_present(data)
    any_multi = any(e["n"] > 1 for a in algos for ds in data[a] for e in [data[a][ds].get(s) for s in data[a][ds]] if e)
    for ax, seqs, title in [
        (axes[0], AGR_SEQS, "Agricultural Sequences"),
        (axes[1], REF_SEQS, "[Non-agricultural] EuRoC-MAV"),
    ]:
        n_seqs = len(seqs)
        n_algos = len(algos)
        width = 0.8 / n_algos
        x = np.arange(n_seqs)

        for ai, algo in enumerate(algos):
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
            yerr = np.array(errs)[mask] if any_multi else None

            ax.bar(xpos, ypos, width * 0.9,
                   color=ALGO_COLOUR[algo], label=ALGO_LABEL[algo],
                   yerr=yerr, error_kw={"elinewidth": 1.2, "capsize": 3},
                   alpha=0.9)

        ax.set_xticks(x)
        ax.set_xticklabels([s[2] for s in seqs], fontsize=11)
        ax.set_ylabel("ATE SE(3) RMSE [m]  (log scale)", fontsize=12)
        ax.set_title(title, fontsize=12)
        ax.grid(axis="y", alpha=0.3, which="both")
        # SE(3) ATE spans ~8 decades because scale-collapsed runs reach 1e5-1e7 m
        # while good runs are ~0.2 m. A linear axis hides every good result, so use
        # log. Bars start at 0.01 m; anything taller than ~50 m is a diverged run.
        ax.set_yscale("log")
        ax.set_ylim(bottom=0.01)
        ax.axhspan(50, ax.get_ylim()[1], color="red", alpha=0.05)

    handles = [Patch(color=ALGO_COLOUR[a], label=ALGO_LABEL[a])
               for a in algos]
    fig.legend(handles=handles, loc="lower center", ncol=min(len(algos), 8),
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

    algos = algos_present(data)
    for ax, seqs, title in [
        (axes[0], AGR_SEQS, "Agricultural Sequences"),
        (axes[1], REF_SEQS, "[Non-agricultural] EuRoC-MAV"),
    ]:
        n_seqs = len(seqs)
        n_algos = len(algos)
        width = 0.8 / n_algos
        x = np.arange(n_seqs)

        for ai, algo in enumerate(algos):
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
               for a in algos]
    handles.append(plt.Line2D([0], [0], color="black", linestyle="--", label="1.0"))
    fig.legend(handles=handles, loc="lower center", ncol=min(len(algos) + 1, 8),
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

    algos = algos_present(data)
    n_seqs = len(all_seqs)
    n_algos = len(algos)
    width = 0.8 / n_algos
    x = np.arange(n_seqs)

    for ai, algo in enumerate(algos):
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
               for a in algos]
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
                    choices=["vo", "vo-lc", "vio", "vio-lc", "gnss-vio"])
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
