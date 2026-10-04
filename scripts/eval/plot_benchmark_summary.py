#!/usr/bin/env python3
"""Generate section-specific benchmark summary plots from benchmark-<type>.csv.

Writes to <results_root>/:
  ate_bar_agricultural.png       - Rosario v2 + HortiMulti ATE
  ate_bar_euroc.png              - EuRoC-MAV ATE
  ate_bar_zed2i.png              - local ZED2i ATE
  scale_factor_<section>.png     - scale factor deviation from 1.0
  fps_bar_<section>.png          - processing-FPS comparison

Usage:
    python3 scripts/eval/plot_benchmark_summary.py [--type vo|vo-lc|vio|vio-lc|gnss-vio] [--dpi 180]
"""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

WS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _run_type import resolve as resolve_run_type  # noqa: E402


ALGO_COLOUR = {
    "cuvslam": "#31a354",
    "svo_pro": "#e6550d",
    "dsol": "#3182bd",
    "mast3r_fusion": "#756bb1",
    "orbslam3": "#2ca02c",
    "macvo": "#ff7f0e",
    "basalt": "#d62728",
    "airslam": "#17becf",
    "ov2slam": "#1b9e77",
    "mast3r_slam": "#9467bd",
    "megasam": "#e377c2",
    "dpvo": "#ffbb78",
    "okvis2x": "#1f77b4",
    "okvis2": "#bcbd22",
    "openvins": "#7f7f7f",
    "voxel_svio": "#c5b0d5",
    "cifasis_gnss_si": "#1f77b4",
    "vins_fusion_gps": "#bcbd22",
    "rtabmap_gps": "#7f7f7f",
    "openvins_gps": "#ff9896",
}
ALGO_LABEL = {
    "cuvslam": "cuVSLAM",
    "svo_pro": "SVO Pro",
    "dsol": "DSOL",
    "mast3r_fusion": "MASt3R-Fusion",
    "orbslam3": "ORB-SLAM3",
    "macvo": "MAC-VO",
    "basalt": "Basalt",
    "airslam": "AirSLAM",
    "ov2slam": "OV2SLAM",
    "mast3r_slam": "MASt3R-SLAM",
    "megasam": "MegaSaM",
    "dpvo": "DPV-SLAM",
    "okvis2x": "OKVIS2-X",
    "okvis2": "OKVIS2",
    "openvins": "OpenVINS",
    "voxel_svio": "Voxel-SVIO",
    "cifasis_gnss_si": "CIFASIS GNSS-SI",
    "vins_fusion_gps": "VINS-Fusion+GPS",
    "rtabmap_gps": "RTAB-Map+GPS",
    "openvins_gps": "OpenVINS+GPS",
}
ALGO_ORDER = [
    "orbslam3", "macvo", "basalt", "airslam", "ov2slam",
    "mast3r_slam", "megasam", "dpvo", "okvis2", "okvis2x",
    "openvins", "voxel_svio", "cifasis_gnss_si", "vins_fusion_gps",
    "rtabmap_gps", "openvins_gps", "cuvslam", "svo_pro", "dsol", "mast3r_fusion",
]

DATASET_ALIASES = {"euroc": "euroc_mav", "EuRoC-MAV": "euroc_mav"}

AGR_SEQS = [
    ("rosariov2", "sequence1", "Rosario\nseq1"),
    ("rosariov2", "sequence5", "Rosario\nseq5"),
    ("hortimulti", "strawberry02", "Horti\nstraw02"),
    ("hortimulti", "strawberry03", "Horti\nstraw03"),
    ("citrusfarm", "seq04", "Citrus\nseq04"),
    ("citrusfarm", "seq07", "Citrus\nseq07"),
]
REF_SEQS = [
    ("euroc_mav", "MH_01_easy", "MH01"),
    ("euroc_mav", "MH_03_medium", "MH03"),
    ("euroc_mav", "MH_05_difficult", "MH05"),
]
LOCAL_SEQS = [
    ("zed2i", "field1_110426_full_10fps_q90", "ZED2i\nfield1"),
]
SECTION_GROUPS = [
    ("agricultural", AGR_SEQS, "Agricultural Sequences"),
    ("euroc", REF_SEQS, "Non-agricultural EuRoC-MAV"),
    ("zed2i", LOCAL_SEQS, "Local ZED2i"),
]


def canon_dataset(name):
    return DATASET_ALIASES.get(name, name)


def load_data(csv_path: Path):
    rows = list(csv.DictReader(open(csv_path)))
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["algo"], canon_dataset(row["dataset"]), row["seq"])].append(row)

    data = defaultdict(lambda: defaultdict(dict))
    for (algo, ds, seq), rows_for_key in grouped.items():
        sims = [float(r["ate_sim3_rmse_m"]) for r in rows_for_key]
        se3s = [float(r["ate_se3_rmse_m"]) for r in rows_for_key]
        fpss = [float(r["fps"]) for r in rows_for_key if float(r.get("fps") or 0) > 0]
        scales = [float(r["scale_factor"]) for r in rows_for_key]
        data[algo][ds][seq] = {
            "ate_sim3": float(np.mean(sims)),
            "ate_sim3_std": float(np.std(sims)) if len(sims) > 1 else 0.0,
            "ate_se3": float(np.mean(se3s)),
            "ate_se3_std": float(np.std(se3s)) if len(se3s) > 1 else 0.0,
            "fps": float(np.mean(fpss)) if fpss else 0.0,
            "scale": float(np.mean(scales)),
            "n": len(rows_for_key),
        }
    return data


def algos_for_section(data, seqs):
    return [
        algo for algo in ALGO_ORDER
        if any(data[algo][ds].get(seq) for ds, seq, _ in seqs)
    ]


def sections_present(data):
    sections = []
    for slug, seqs, title in SECTION_GROUPS:
        algos = algos_for_section(data, seqs)
        if algos:
            sections.append((slug, seqs, title, algos))
    return sections


def section_figsize(seqs, algos, height):
    width = max(6.5, len(seqs) * max(1.65, 0.38 * len(algos)) + 2.8)
    return width, height


def add_legend(fig, algos, extra_handles=None):
    handles = [Patch(color=ALGO_COLOUR[a], label=ALGO_LABEL[a]) for a in algos]
    if extra_handles:
        handles.extend(extra_handles)
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=min(len(handles), 6),
        fontsize=10,
        bbox_to_anchor=(0.5, -0.08),
        framealpha=0.9,
    )


def plot_grouped_bars(ax, data, algos, seqs, field, yerr_field=None,
                      require_positive=False):
    n_algos = max(len(algos), 1)
    width = 0.8 / n_algos
    x = np.arange(len(seqs))

    for algo_idx, algo in enumerate(algos):
        vals = []
        errs = []
        for ds, seq, _label in seqs:
            entry = data[algo][ds].get(seq)
            val = entry[field] if entry else np.nan
            if require_positive and (np.isnan(val) or val <= 0):
                val = np.nan
            vals.append(val)
            errs.append(entry[yerr_field] if entry and yerr_field else 0.0)

        vals = np.asarray(vals, dtype=float)
        errs = np.asarray(errs, dtype=float)
        mask = ~np.isnan(vals)
        yerr = errs[mask] if yerr_field and np.any(errs[mask] > 0) else None
        offset = (algo_idx - n_algos / 2 + 0.5) * width
        ax.bar(
            x[mask] + offset,
            vals[mask],
            width * 0.9,
            color=ALGO_COLOUR[algo],
            label=ALGO_LABEL[algo],
            yerr=yerr,
            error_kw={"elinewidth": 1.1, "capsize": 3},
            alpha=0.9,
        )

    ax.set_xticks(x)
    ax.set_xticklabels([seq[2] for seq in seqs], fontsize=11)
    ax.grid(axis="y", alpha=0.3)


def save_plot(fig, out_path, dpi):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[plot_summary] saved {out_path}")


def plot_ate_bar(data, seqs, title, algos, out_path, dpi):
    fig, ax = plt.subplots(figsize=section_figsize(seqs, algos, 5.8))
    plot_grouped_bars(ax, data, algos, seqs, "ate_se3", "ate_se3_std")
    ax.set_ylabel("ATE SE(3) RMSE [m]  (log scale)", fontsize=12)
    ax.set_title(f"ATE SE(3) RMSE - {title}", fontsize=13)
    ax.set_yscale("log")
    ax.set_ylim(bottom=0.01)
    ax.axhspan(50, ax.get_ylim()[1], color="red", alpha=0.05)
    add_legend(fig, algos)
    fig.tight_layout()
    save_plot(fig, out_path, dpi)


def plot_scale_factor(data, seqs, title, algos, out_path, dpi):
    fig, ax = plt.subplots(figsize=section_figsize(seqs, algos, 5.4))
    plot_grouped_bars(ax, data, algos, seqs, "scale")
    ax.axhline(1.0, color="black", linewidth=1.2, linestyle="--")
    ax.set_ylabel("Sim(3) scale factor", fontsize=12)
    ax.set_title(f"Sim(3) Scale Factor - {title}", fontsize=13)
    add_legend(fig, algos, [
        plt.Line2D([0], [0], color="black", linestyle="--", label="1.0")
    ])
    fig.tight_layout()
    save_plot(fig, out_path, dpi)


def plot_fps_bar(data, seqs, title, algos, out_path, dpi):
    fig, ax = plt.subplots(figsize=section_figsize(seqs, algos, 5.2))
    plot_grouped_bars(ax, data, algos, seqs, "fps", require_positive=True)
    ax.set_ylabel("Mean processing FPS", fontsize=12)
    ax.set_title(f"Processing Speed - {title}", fontsize=13)
    ax.set_ylim(bottom=0)
    add_legend(fig, algos)
    fig.tight_layout()
    save_plot(fig, out_path, dpi)


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
    sections = sections_present(data)
    if not sections:
        raise SystemExit(f"No section data in {rt.csv_path.name}")

    for slug, seqs, title, algos in sections:
        plot_ate_bar(data, seqs, title, algos,
                     rt.results_root / f"ate_bar_{slug}.png", args.dpi)
        plot_scale_factor(data, seqs, title, algos,
                          rt.results_root / f"scale_factor_{slug}.png", args.dpi)
        plot_fps_bar(data, seqs, title, algos,
                     rt.results_root / f"fps_bar_{slug}.png", args.dpi)


if __name__ == "__main__":
    main()
