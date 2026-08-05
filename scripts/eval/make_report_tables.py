#!/usr/bin/env python3
"""Generate every report results table directly from the benchmark CSVs.

Usage:
    python3 make_report_tables.py [--check]

Writes docs/generated/tables-<runtype>.md plus a combined docs/generated/tables.md.

Rationale (2026-08-05): report2's tables were hand-transcribed, which produced
unsourced cells, stale coverage tags, and inconsistent bolding. This script is
now the ONLY sanctioned path from results to report tables:
results/ -> run_eval.json -> benchmark-*.csv (build_benchmark_csv.py) -> here.
Never hand-type a results number.

Table rules (encoded, not stylistic):
  * PRIMARY metric: ATE SE(3) RMSE [m] — the honest metric for stereo/VIO
    (PROGRESS finding 4). Sim(3) + scale appear as secondary columns in the
    per-mode detail tables. Monocular DPVO reports Sim(3) (scale unobservable)
    and is marked (mono); it is never eligible for bold.
  * Aggregation: N>=2 -> "median (min-max)". N=1 -> bare value. Never "±" at
    N<=3.
  * Coverage: cells with coverage_gap_pct < 95 get "@NN%" and are excluded
    from bolding (finding 14: sub-path ATE is not comparable).
  * Scale collapse (run_status == scale_collapse): cell prints "✗ collapse"
    with no number (a Sim3-inflated shape residual would invite comparison).
  * Bold: lowest median SE3 ATE among eligible cells (stereo, ok-status,
    coverage>=95), only when the margin to the runner-up exceeds the winner's
    dispersion band (its own min-max range when N>=2; else 10% for
    deterministic file-fed algorithms, 50% for non-deterministic or
    real-time-fed ones). Otherwise NO bold in that column — an honest tie.
  * Loop-closure event counts are NOT embedded in ATE cells; they get their
    own table (they are heterogeneous log-greps, not accepted-loop counts).
  * GNSS-VIO: only gnss_variant == "default" rows are in the main table;
    variants (conventional/ppk/hybrid) get a dedicated comparison table.
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "docs" / "generated"

RUN_TYPES = ["vo", "vo-lc", "vio", "vio-lc", "gnss-vio"]

SEQ_LABEL = {
    ("rosariov2", "sequence1"): "seq1",
    ("rosariov2", "sequence5"): "seq5",
    ("hortimulti", "strawberry02"): "str02",
    ("hortimulti", "strawberry03"): "str03",
    ("zed2i", "field1_110426_full_10fps_q90"): "zed2i",
    ("euroc_mav", "MH_01_easy"): "MH01",
    ("euroc_mav", "MH_03_medium"): "MH03",
    ("euroc_mav", "MH_05_difficult"): "MH05",
}
AGRI_ORDER = ["seq1", "seq5", "str02", "str03", "zed2i"]
EUROC_ORDER = ["MH01", "MH03", "MH05"]

ALGO_LABEL = {
    "orbslam3": "ORB-SLAM3", "ov2slam": "OV2SLAM", "macvo": "MAC-VO",
    "basalt": "Basalt", "airslam": "AirSLAM", "okvis2": "OKVIS2",
    "okvis2x": "OKVIS2-X", "openvins": "OpenVINS", "voxel_svio": "Voxel-SVIO",
    "dpvo": "DPVO (mono)", "droidslam": "DROID-SLAM",
    "vins_fusion_gps": "VINS-Fusion+GPS", "rtabmap_gps": "RTAB-Map+GPS",
    "cifasis_gnss_si": "CIFASIS GNSS-SI", "openvins_gps": "OpenVINS+GPS",
}
MONO_ALGOS = {"dpvo"}
EXCLUDED_ALGOS = {"droidslam"}          # dropped from the benchmark scope
# Deterministic when file-fed (finding 8); everything else treated as
# non-deterministic for the bold dispersion band.
DETERMINISTIC = {"basalt", "macvo", "okvis2", "okvis2x", "dpvo", "droidslam"}
COV_THRESHOLD = 95.0
BAND_DET, BAND_NONDET = 0.10, 0.50


def load(rt: str) -> pd.DataFrame:
    df = pd.read_csv(REPO / f"benchmark-{rt}.csv")
    df = df[~df["algo"].isin(EXCLUDED_ALGOS)].copy()
    df["seqlbl"] = df.apply(
        lambda r: SEQ_LABEL.get((r["dataset"], r["seq"]),
                                f'{r["dataset"]}/{r["seq"]}'), axis=1)
    if "gnss_variant" not in df.columns:
        df["gnss_variant"] = "default"
    df["gnss_variant"] = df["gnss_variant"].fillna("default")
    return df


def agg_cell(g: pd.DataFrame, metric: str) -> dict:
    """Aggregate the runs of one (algo, seq) cell."""
    vals = pd.to_numeric(g[metric], errors="coerce").dropna()
    cov = pd.to_numeric(g["coverage_gap_pct"], errors="coerce").dropna()
    statuses = set(g["run_status"].astype(str))
    collapsed = statuses == {"scale_collapse"}
    n = len(vals)
    if n == 0:
        return {"n": 0, "collapsed": collapsed, "text": "—", "median": None,
                "cov": None, "eligible": False, "band": None}
    med = float(vals.median())
    cov_min = float(cov.min()) if len(cov) else None
    if collapsed:
        return {"n": n, "collapsed": True, "text": "✗ collapse", "median": None,
                "cov": cov_min, "eligible": False, "band": None}
    if n >= 2:
        text = f"{med:.3g} ({vals.min():.3g}–{vals.max():.3g})"
        band = (float(vals.max()) - float(vals.min())) / med if med > 0 else 0.0
    else:
        text = f"{med:.3g}"
        algo = g["algo"].iloc[0]
        band = BAND_DET if algo in DETERMINISTIC else BAND_NONDET
    partial = cov_min is not None and cov_min < COV_THRESHOLD
    if partial:
        text = f"*{text} @{cov_min:.0f}%*"
    algo = g["algo"].iloc[0]
    eligible = (not partial) and (algo not in MONO_ALGOS) and ("ok" in statuses)
    return {"n": n, "collapsed": False, "text": text, "median": med,
            "cov": cov_min, "eligible": eligible, "band": band}


def build_table(df: pd.DataFrame, metric: str, seq_order: list[str],
                bold: bool = True) -> tuple[str, list[str]]:
    """Return (markdown table, notes)."""
    algos = [a for a in ALGO_LABEL if a in set(df["algo"])]
    cells: dict[tuple, dict] = {}
    for a in algos:
        for s in seq_order:
            g = df[(df["algo"] == a) & (df["seqlbl"] == s)]
            if len(g):
                cells[(a, s)] = agg_cell(g, metric)

    # Bold decision per column
    bold_cells = set()
    ties = []
    if bold:
        for s in seq_order:
            ranked = sorted(
                ((cells[(a, s)]["median"], a) for a in algos
                 if (a, s) in cells and cells[(a, s)]["eligible"]
                 and cells[(a, s)]["median"] is not None),
            )
            if len(ranked) >= 2:
                (m1, a1), (m2, _) = ranked[0], ranked[1]
                band = cells[(a1, s)]["band"] or BAND_NONDET
                if m1 > 0 and (m2 - m1) / m1 > band:
                    bold_cells.add((a1, s))
                else:
                    ties.append(s)
            elif len(ranked) == 1:
                bold_cells.add((ranked[0][1], s))

    lines = ["| Algorithm | " + " | ".join(seq_order) + " |",
             "|---" * (len(seq_order) + 1) + "|"]
    for a in algos:
        row = [ALGO_LABEL[a]]
        for s in seq_order:
            c = cells.get((a, s))
            if c is None:
                row.append("—")
            else:
                t = c["text"]
                if (a, s) in bold_cells:
                    t = f"**{t}**"
                row.append(t)
        lines.append("| " + " | ".join(row) + " |")

    notes = []
    if ties:
        notes.append("No bold in column(s) " + ", ".join(ties) +
                     ": top-2 margin is inside the winner's dispersion band (honest tie).")
    return "\n".join(lines), notes


def lc_events_table(df: pd.DataFrame, seq_order: list[str]) -> str:
    lines = ["| Algorithm | " + " | ".join(seq_order) + " |",
             "|---" * (len(seq_order) + 1) + "|"]
    for a in [a for a in ALGO_LABEL if a in set(df["algo"])]:
        row = [ALGO_LABEL[a]]
        for s in seq_order:
            g = df[(df["algo"] == a) & (df["seqlbl"] == s)]
            if not len(g):
                row.append("—")
            else:
                v = pd.to_numeric(g["loop_closures"], errors="coerce").dropna()
                row.append(f"{int(v.median())}" if len(v) else "n/i")
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


HEADER_NOTE = """<!-- AUTO-GENERATED by scripts/eval/make_report_tables.py — do not edit by hand.
     Source of truth: benchmark-*.csv (built by build_benchmark_csv.py from results-*/). -->

**Reading the tables.** Primary metric: **ATE SE(3) RMSE [m]** (scale-aware — the honest metric for
stereo/VIO; PROGRESS finding 4). DPVO is monocular: its values are Sim(3) trajectory-shape error and
never bolded. Cells: `median (min–max)` when N≥2, bare value when N=1. `*value @NN%*` = gap-aware
trajectory coverage below 95% — scored only on the completed sub-path, NOT comparable, never bolded
(finding 14). `✗ collapse` = Sim(3) scale ≈ 0 (SE3 error diverges; no number is printed on purpose).
`—` = not run / failed. **Bold** = lowest median among eligible (full-coverage, stereo, ok-status)
cells, only when the margin to the runner-up exceeds the winner's dispersion band (min–max range when
N≥2, else 10% deterministic / 50% non-deterministic per finding 8/11); columns whose top-2 gap is
inside the band carry no bold — that is an honest tie, not an omission.
"""


def main() -> int:
    check = "--check" in sys.argv
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    combined = [f"# Benchmark result tables (auto-generated)\n", HEADER_NOTE]
    problems = []

    for rt in RUN_TYPES:
        df = load(rt)
        main_df = df[df["gnss_variant"] == "default"] if rt == "gnss-vio" else df
        parts = [f"# {rt.upper()} results (auto-generated)\n", HEADER_NOTE]

        for scope, order in (("Agricultural", AGRI_ORDER),
                             ("EuRoC reference (non-agricultural control)", EUROC_ORDER)):
            sub = main_df[main_df["seqlbl"].isin(order)]
            if not len(sub):
                continue
            present = [s for s in order if s in set(sub["seqlbl"])]
            tbl, notes = build_table(sub, "ate_se3_rmse_m", present)
            parts.append(f"## {scope} — ATE SE(3) RMSE [m]\n\n{tbl}\n")
            for nline in notes:
                parts.append(f"> {nline}\n")
            tbl2, _ = build_table(sub, "ate_sim3_rmse_m", present, bold=False)
            parts.append(f"<details><summary>{scope} — ATE Sim(3) [m] (secondary; "
                         f"absorbs scale error)</summary>\n\n{tbl2}\n\n</details>\n")

        if rt.endswith("lc"):
            sub = main_df[main_df["seqlbl"].isin(AGRI_ORDER + EUROC_ORDER)]
            parts.append("## Log-reported loop-closure events (NOT verified accepted "
                         "loops — heterogeneous per-algorithm log greps; n/i = not "
                         "instrumented)\n\n" +
                         lc_events_table(sub, [s for s in AGRI_ORDER + EUROC_ORDER
                                               if s in set(sub['seqlbl'])]) + "\n")

        if rt == "gnss-vio":
            var = df[df["gnss_variant"] != "default"]
            if len(var):
                lines = ["| Algorithm | Sequence | Variant | ATE SE3 [m] | ATE Sim3 [m] | Scale |",
                         "|---|---|---|---|---|---|"]
                for _, r in var.sort_values(["algo", "seqlbl", "gnss_variant"]).iterrows():
                    lines.append(
                        f"| {ALGO_LABEL.get(r['algo'], r['algo'])} | {r['seqlbl']} | "
                        f"{r['gnss_variant']} | {r['ate_se3_rmse_m']:.3g} | "
                        f"{r['ate_sim3_rmse_m']:.3g} | {r['scale_factor']:.3f} |")
                parts.append("## GNSS input-variant runs (PPK / conventional study — "
                             "not aggregated into the main table)\n\n" + "\n".join(lines) + "\n")
            n_origin = df["ate_origin_rmse_m"].notna().sum()
            parts.append(f"> Origin-aligned ATE (global-frame error, the honest GNSS metric) is "
                         f"available for {n_origin}/{len(df)} runs (re-evaluated ones); remaining "
                         f"runs need re-evaluation on the machine holding their datasets.\n")

        out = OUT_DIR / f"tables-{rt}.md"
        out.write_text("\n".join(parts))
        combined.append("\n".join(parts[1:]).replace(HEADER_NOTE, "") if rt != "vo" else "\n".join(parts[1:]))
        print(f"[tables] wrote {out}")

        if check and not len(main_df):
            problems.append(f"{rt}: no rows")

    (OUT_DIR / "tables.md").write_text("\n".join(combined))
    print(f"[tables] wrote {OUT_DIR/'tables.md'}")

    if check:
        for rt in RUN_TYPES:
            df = load(rt)
            need = {"ate_se3_rmse_m", "ate_sim3_rmse_m", "coverage_gap_pct", "run_status"}
            missing = need - set(df.columns)
            if missing:
                problems.append(f"{rt}: missing columns {missing}")
        if problems:
            print("[tables] CHECK FAILED:", problems, file=sys.stderr)
            return 1
        print("[tables] check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
