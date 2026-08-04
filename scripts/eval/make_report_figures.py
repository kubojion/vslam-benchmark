#!/usr/bin/env python3
"""Report figures that carry findings 13/14/15 (not in the default figure set)."""
import csv, glob, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WS = "/home/iman/slam_tests/vslam-benchmark"
OUT = os.path.join(WS, "figures"); os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.size": 11, "figure.dpi": 150})

def load_csv(m):
    d = {}
    for r in csv.DictReader(open(f"{WS}/benchmark-{m}.csv")):
        try: d.setdefault((r["algo"], r["dataset"], r["seq"]), []).append(float(r["ate_sim3_rmse_m"]))
        except: pass
    import statistics as st
    return {k: st.median(v) for k, v in d.items()}

def load_tum(p):
    a = np.loadtxt(p)
    return a[:, 0], a[:, 1:4]

def umeyama(P, Q):  # align P -> Q (Sim3)
    muP, muQ = P.mean(0), Q.mean(0)
    Pc, Qc = P - muP, Q - muQ
    C = Qc.T @ Pc / len(P)
    U, D, Vt = np.linalg.svd(C)
    S = np.eye(3)
    if np.linalg.det(U) * np.linalg.det(Vt) < 0: S[2, 2] = -1
    R = U @ S @ Vt
    s = (D * np.diag(S)).sum() / (Pc ** 2).sum() * len(P)
    t = muQ - s * R @ muP
    return s, R, t

def aligned_xy(gt_t, gt_xyz, est_p):
    et, ep = load_tum(est_p)
    # match est ts -> nearest gt ts
    idx = np.searchsorted(gt_t, et); idx = np.clip(idx, 1, len(gt_t) - 1)
    left = np.abs(et - gt_t[idx - 1]) < np.abs(et - gt_t[idx])
    gi = idx - left.astype(int)
    ok = np.abs(et - gt_t[gi]) < 0.1
    if ok.sum() < 10: return None, None
    s, R, t = umeyama(ep[ok], gt_xyz[gi[ok]])
    al = (s * (R @ ep.T).T + t)
    return al, ok.mean()

# ── FIG A: IMU effect is excitation-dependent (VO vs VIO) ────────────────────
def fig_excitation():
    VO, VIO = load_csv("vo"), load_csv("vio")
    panels = [("zed2i", "field1_110426_full_10fps_q90", "ZED2i field  (weak excitation)"),
              ("rosariov2", "sequence5", "Rosario seq5  (adequate excitation)")]
    algos = ["basalt", "okvis2", "okvis2x", "airslam", "orbslam3"]  # VO+VIO only (Voxel-SVIO has no VO)
    lbl = {"basalt": "Basalt", "okvis2": "OKVIS2", "okvis2x": "OKVIS2-X", "airslam": "AirSLAM",
           "voxel_svio": "Voxel-SVIO", "orbslam3": "ORB-SLAM3"}
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, (ds, sq, title) in zip(axes, panels):
        present = [a for a in algos if (a, ds, sq) in VO or (a, ds, sq) in VIO]
        x = np.arange(len(present)); w = 0.38
        vo = [VO.get((a, ds, sq), np.nan) for a in present]
        vio = [VIO.get((a, ds, sq), np.nan) for a in present]
        ax.bar(x - w/2, vo, w, label="VO (no IMU)", color="#4CAF50")
        ax.bar(x + w/2, vio, w, label="VIO (+IMU)", color="#F44336")
        for i, a in enumerate(present):  # mark methods whose VIO failed (e.g. ORB-SLAM3 on ZED2i)
            if np.isnan(vio[i]) and not np.isnan(vo[i]):
                ax.text(x[i] + w/2, vo[i] * 1.15, "VIO\n✗ failed", ha="center", va="bottom", fontsize=7.5, color="#B71C1C", fontweight="bold")
        ax.set_yscale("log"); ax.set_title(title, fontsize=11)
        ax.set_xticks(x); ax.set_xticklabels([lbl[a] for a in present], rotation=30, ha="right")
        ax.set_ylabel("ATE Sim3 (m, log)"); ax.grid(axis="y", alpha=0.3); ax.legend()
    fig.suptitle("The IMU's value is excitation-dependent:  it COLLAPSES on ZED2i, HELPS on Rosario", fontweight="bold")
    fig.tight_layout(); p = f"{OUT}/fig_imu_excitation.png"; fig.savefig(p); print(p)

# ── FIG B: loop closure — mechanism x sequence heatmap (VO -> VO-LC) ─────────
def fig_lc_mechanism():
    VO, VOLC = load_csv("vo"), load_csv("vo-lc")
    # columns: EuRoC (distinctive) then the 4 agricultural sequences
    cols = [("euroc_mav", "MH_01_easy", "EuRoC\nMH01"), ("rosariov2", "sequence1", "seq1"),
            ("rosariov2", "sequence5", "seq5"), ("hortimulti", "strawberry02", "str02"),
            ("hortimulti", "strawberry03", "str03")]
    rows = [("dpvo", "DPV-SLAM  (proximity)"), ("ov2slam", "OV2SLAM  (iBoW)"),
            ("okvis2", "OKVIS2  (DBoW)")]
    M = np.full((len(rows), len(cols)), np.nan)
    for i, (a, _) in enumerate(rows):
        for j, (ds, sq, _) in enumerate(cols):
            vo, vl = VO.get((a, ds, sq)), VOLC.get((a, ds, sq))
            if vo and vl: M[i, j] = 100 * (vl - vo) / vo
    fig, ax = plt.subplots(figsize=(10, 4.6))
    im = ax.imshow(np.clip(M, -100, 100), cmap="RdYlGn_r", vmin=-100, vmax=100, aspect="auto")
    ax.set_xticks(range(len(cols))); ax.set_xticklabels([c[2] for c in cols], fontsize=11)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[1] for r in rows], fontsize=11)
    # vertical divider between EuRoC (distinctive reference) and agri
    ax.axvline(0.5, color="k", lw=2)
    for i in range(len(rows)):
        for j in range(len(cols)):
            v = M[i, j]
            if np.isnan(v): continue
            txt = f"{v:+.0f}%"
            ax.text(j, i, txt, ha="center", va="center", fontsize=11,
                    color="white" if abs(v) > 55 else "black",
                    fontweight="bold" if v > 100 else "normal")
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cb.set_label("ATE change  VO → VO-LC  (%)")
    cb.ax.text(1.3, 1.0, "LC hurts", transform=cb.ax.transAxes, va="top", fontsize=8, color="#B71C1C")
    cb.ax.text(1.3, 0.0, "LC helps", transform=cb.ax.transAxes, va="bottom", fontsize=8, color="#1B5E20")
    ax.set_title("Loop closure helps on distinctive scenes, is unreliable on crops:\n"
                 "proximity always hurts; even verified (iBoW/DBoW) LC can blow up (str02)  —  green = helps, red = hurts", fontweight="bold", fontsize=10.5)
    fig.tight_layout(); p = f"{OUT}/fig_lc_mechanism.png"; fig.savefig(p); print(p)

# ── FIG C: coverage — ORB fails where others complete + IMU rescue ──────────
def load_cov(m):
    d = {}
    for r in csv.DictReader(open(f"{WS}/benchmark-{m}.csv")):
        try: d.setdefault((r["algo"], r["dataset"], r["seq"]), []).append(float(r["trajectory_time_coverage_pct"]))
        except: pass
    import statistics as st
    return {k: st.median(v) for k, v in d.items()}

# ── FIG C: whole-benchmark ATE heatmap (VO) — the overview ──────────────────
def fig_master():
    from matplotlib.colors import LogNorm
    VO, COV = load_csv("vo"), load_cov("vo")
    rows = [("orbslam3", "ORB-SLAM3"), ("ov2slam", "OV2SLAM"), ("dpvo", "DPVO (mono)"),
            ("basalt", "Basalt"), ("okvis2", "OKVIS2"), ("okvis2x", "OKVIS2-X"),
            ("macvo", "MAC-VO"), ("airslam", "AirSLAM"), ("droidslam", "DROID-SLAM")]
    cols = [("rosariov2", "sequence1", "seq1"), ("rosariov2", "sequence5", "seq5"),
            ("hortimulti", "strawberry02", "str02"), ("hortimulti", "strawberry03", "str03"),
            ("euroc_mav", "MH_01_easy", "MH01"), ("euroc_mav", "MH_03_medium", "MH03"),
            ("euroc_mav", "MH_05_difficult", "MH05"), ("zed2i", "field1_110426_full_10fps_q90", "zed2i")]
    M = np.full((len(rows), len(cols)), np.nan)
    for i, (a, _) in enumerate(rows):
        for j, (ds, sq, _) in enumerate(cols):
            if (a, ds, sq) in VO: M[i, j] = VO[(a, ds, sq)]
    fig, ax = plt.subplots(figsize=(11, 6))
    im = ax.imshow(M, cmap="RdYlGn_r", norm=LogNorm(vmin=0.03, vmax=50), aspect="auto")
    ax.set_xticks(range(len(cols))); ax.set_xticklabels([c[2] for c in cols], fontsize=11)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[1] for r in rows], fontsize=11)
    ax.axvline(3.5, color="k", lw=2); ax.axvline(6.5, color="k", lw=2)   # agri | euroc | zed2i
    for xc, lab, col in [(1.5, "AGRICULTURAL", "#33691E"), (5, "EuRoC (reference)", "#555"), (7, "ZED2i", "#004D40")]:
        ax.text(xc, -0.62, lab, ha="center", fontweight="bold", fontsize=9, color=col)
    for i, (a, _) in enumerate(rows):
        for j, (ds, sq, _) in enumerate(cols):
            v = M[i, j]
            if np.isnan(v): ax.text(j, i, "—", ha="center", va="center", color="#999"); continue
            partial = COV.get((a, ds, sq), 100) < 90
            ax.text(j, i, f"{v:.2f}" + ("*" if partial else ""), ha="center", va="center", fontsize=8.5,
                    color="white" if (v < 0.12 or v > 8) else "black")
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02); cb.set_label("ATE Sim3 RMSE (m, log)")
    ax.set_title("Whole-benchmark VO accuracy: every method is fine on EuRoC, agriculture is where they diverge\n"
                 "* = partial coverage (ATE not comparable — method lost tracking);  — = not run",
                 fontweight="bold", fontsize=10.5, pad=30)
    fig.tight_layout(); p = f"{OUT}/fig_master_vo_heatmap.png"; fig.savefig(p); print(p)

# ── FIG D: ORB-SLAM3 mode progression — IMU rescues coverage, LC fixes ATE ───
def fig_progression():
    VO, VIO, VIOLC = load_csv("vo"), load_csv("vio"), load_csv("vio-lc")
    CV, CVi, CVl = load_cov("vo"), load_cov("vio"), load_cov("vio-lc")
    cells = [("rosariov2", "sequence1", "Rosario seq1"), ("hortimulti", "strawberry02", "HortiMulti str02")]
    fig, axes = plt.subplots(1, len(cells), figsize=(12, 5))
    for ax, (ds, sq, title) in zip(axes, cells):
        modes = ["VO", "VIO", "VIO-LC"]
        ate = [VO.get(("orbslam3", ds, sq)), VIO.get(("orbslam3", ds, sq)), VIOLC.get(("orbslam3", ds, sq))]
        cov = [CV.get(("orbslam3", ds, sq)), CVi.get(("orbslam3", ds, sq)), CVl.get(("orbslam3", ds, sq))]
        x = np.arange(3)
        bars = ax.bar(x, ate, 0.5, color=["#90A4AE", "#42A5F5", "#1B5E20"])
        for b, a in zip(bars, ate):
            if a is not None: ax.text(b.get_x() + b.get_width()/2, a + 0.05, f"{a:.2f} m", ha="center", fontsize=10, fontweight="bold")
        # the VO bar's ATE covers only the tracked sub-path — flag it so the short
        # grey bar is not read as "VO more accurate than VIO"
        if cov[0] is not None and cov[0] < 90:
            ax.text(0, ate[0] / 2, f"ATE over only\n{cov[0]:.0f}% of path", ha="center", va="center",
                    fontsize=8.5, color="white", fontweight="bold")
        ax.set_xticks(x); ax.set_xticklabels(["VO\n(no IMU)", "VIO\n(+IMU)", "VIO-LC\n(+IMU +LC)"])
        ax.set_ylabel("ATE Sim3 (m)"); ax.set_title(f"ORB-SLAM3 on {title}", fontweight="bold")
        ax2 = ax.twinx()
        ax2.plot(x, cov, "o--", color="#D84315", lw=2, ms=9)
        for xi, c in zip(x, cov):
            if c is not None: ax2.text(xi, c - 6, f"{c:.0f}%", ha="center", color="#D84315", fontsize=9, fontweight="bold")
        ax2.set_ylabel("Coverage (%)", color="#D84315"); ax2.set_ylim(0, 115); ax2.tick_params(axis="y", colors="#D84315")
    fig.suptitle("How ORB-SLAM3 is fixed on agriculture:  the IMU restores coverage (orange), then loop closure cuts the error (bars)",
                 fontweight="bold", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.94]); p = f"{OUT}/fig_orb_progression.png"; fig.savefig(p); print(p)

fig_excitation(); fig_lc_mechanism(); fig_master(); fig_progression()
print("done ->", OUT)
