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
    algos = ["basalt", "okvis2", "okvis2x", "airslam", "voxel_svio", "orbslam3"]
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
            ("okvis2", "OKVIS2  (DBoW)"), ("okvis2x", "OKVIS2-X  (DBoW)")]
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
    ax.set_title("Loop closure helps on distinctive scenes, is unreliable on crops — and no mechanism is immune\n"
                 "green = LC helps · red = LC hurts (values >±100% clipped in colour, true % shown)", fontweight="bold", fontsize=10.5)
    fig.tight_layout(); p = f"{OUT}/fig_lc_mechanism.png"; fig.savefig(p); print(p)

# ── FIG C: coverage — ORB fails where others complete + IMU rescue ──────────
def load_cov(m):
    d = {}
    for r in csv.DictReader(open(f"{WS}/benchmark-{m}.csv")):
        try: d.setdefault((r["algo"], r["dataset"], r["seq"]), []).append(float(r["trajectory_time_coverage_pct"]))
        except: pass
    import statistics as st
    return {k: st.median(v) for k, v in d.items()}

def fig_coverage():
    COV = load_cov("vo"); COVv = load_cov("vio")
    lbl = {"orbslam3": "ORB-SLAM3", "basalt": "Basalt", "macvo": "MAC-VO", "dpvo": "DPVO",
           "droidslam": "DROID-SLAM", "airslam": "AirSLAM", "okvis2": "OKVIS2", "okvis2x": "OKVIS2-X", "ov2slam": "OV2SLAM"}
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    # LEFT: coverage per algo, Rosario seq1 VO — ORB is the lone outlier
    ds, sq = "rosariov2", "sequence1"
    algos = [a for a in lbl if (a, ds, sq) in COV]
    covs = [COV[(a, ds, sq)] for a in algos]
    order = np.argsort(covs)
    algos = [algos[i] for i in order]; covs = [covs[i] for i in order]
    cols = ["#F44336" if c < 90 else "#4CAF50" for c in covs]
    axes[0].barh([lbl[a] for a in algos], covs, color=cols)
    axes[0].axvline(90, color="gray", ls="--", lw=0.8)
    axes[0].set_xlabel("Trajectory coverage (%)"); axes[0].set_xlim(0, 105)
    axes[0].set_title("Only ORB-SLAM3 fails to complete the sequence\nRosario seq1, VO — others track 100%", fontweight="bold")
    for i, c in enumerate(covs): axes[0].text(c + 1, i, f"{c:.0f}%", va="center", fontsize=9)
    # RIGHT: ORB-SLAM3 VO vs VIO coverage across agri — the IMU rescue
    seqs = [("rosariov2", "sequence1", "seq1"), ("rosariov2", "sequence5", "seq5"),
            ("hortimulti", "strawberry02", "str02"), ("hortimulti", "strawberry03", "str03")]
    x = np.arange(len(seqs)); w = 0.38
    vo = [COV.get(("orbslam3", d, s), np.nan) for d, s, _ in seqs]
    vio = [COVv.get(("orbslam3", d, s), np.nan) for d, s, _ in seqs]
    axes[1].bar(x - w/2, vo, w, label="VO (no IMU)", color="#2196F3")
    axes[1].bar(x + w/2, vio, w, label="VIO (+IMU)", color="#FF5722")
    axes[1].set_xticks(x); axes[1].set_xticklabels([s[2] for s in seqs])
    axes[1].set_ylabel("Trajectory coverage (%)"); axes[1].set_ylim(0, 105)
    axes[1].set_title("The IMU rescues ORB-SLAM3's tracking\nsame algorithm: VO fragments, VIO completes", fontweight="bold")
    axes[1].legend(); axes[1].grid(axis="y", alpha=0.3)
    fig.tight_layout(); p = f"{OUT}/fig_orb_coverage.png"; fig.savefig(p); print(p)

fig_excitation(); fig_lc_mechanism(); fig_coverage()
print("done ->", OUT)
