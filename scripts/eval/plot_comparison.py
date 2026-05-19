#!/usr/bin/env python3
"""
Generate thesis comparison plots for a single sequence.
Usage:
    python3 scripts/eval/plot_comparison.py <dataset> <seq>
    e.g.: python3 scripts/eval/plot_comparison.py rosariov2 sequence1
"""
import sys, os, pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation

WS = pathlib.Path(__file__).resolve().parents[2]

# ── helpers ──────────────────────────────────────────────────────────────────

def load_tum(path):
    """Return (N,8) array: [t, tx, ty, tz, qx, qy, qz, qw]"""
    data = []
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        data.append([float(x) for x in line.split()])
    return np.array(data)


def umeyama_align(src, dst):
    """Sim(3) Umeyama alignment. Returns aligned src (scale + R + t applied)."""
    n = src.shape[0]
    mu_src, mu_dst = src.mean(0), dst.mean(0)
    src_c, dst_c   = src - mu_src, dst - mu_dst
    var_src = (src_c ** 2).sum() / n
    cov     = dst_c.T @ src_c / n
    U, D, Vt = np.linalg.svd(cov)
    det_sign = np.linalg.det(U @ Vt)
    S = np.eye(3); S[2, 2] = det_sign
    R = U @ S @ Vt
    c = (D * S.diagonal()).sum() / var_src
    t = mu_dst - c * R @ mu_src
    return (c * (R @ src.T).T + t), c, R, t


def associate(ref, est, max_diff=0.1):
    """Return matched (ref_xyz, est_xyz) using nearest-timestamp association."""
    ref_ts, est_ts = ref[:, 0], est[:, 0]
    matched_ref, matched_est = [], []
    for i, t in enumerate(est_ts):
        j = np.argmin(np.abs(ref_ts - t))
        if np.abs(ref_ts[j] - t) <= max_diff:
            matched_ref.append(ref[j, 1:4])
            matched_est.append(est[i, 1:4])
    return np.array(matched_ref), np.array(matched_est)


def align_and_trim(ref_tum, est_tum, max_diff=0.1, correct_scale=True):
    """Align est to ref; return (aligned_xyz, ref_xyz, ate_per_frame)."""
    ref_xyz, est_xyz = associate(ref_tum, est_tum, max_diff)
    if len(ref_xyz) < 3:
        return None, None, None
    aligned, c, R, t = umeyama_align(est_xyz, ref_xyz)
    if not correct_scale:
        c = 1.0
        aligned, _, _, _ = umeyama_align(est_xyz, ref_xyz)
    err = np.linalg.norm(aligned - ref_xyz, axis=1)
    return aligned, ref_xyz, err


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    dataset = sys.argv[1] if len(sys.argv) > 1 else "rosariov2"
    seq     = sys.argv[2] if len(sys.argv) > 2 else "sequence1"

    base    = WS / "results" / dataset / seq
    gt_path = WS / "datasets" / dataset / seq / "gt_tum.txt"
    out_dir = base / "plots"
    out_dir.mkdir(exist_ok=True)

    ALGOS = {
        "ORB-SLAM3":   {"path": base / "orbslam3/trajectory.txt",  "color": "#2196F3"},
        "DROID-SLAM":  {"path": base / "droidslam/trajectory.txt", "color": "#FF9800"},
        "MAC-VO":      {"path": base / "macvo/trajectory.txt",     "color": "#4CAF50"},
    }

    if not gt_path.exists():
        sys.exit(f"GT not found: {gt_path}")

    ref_tum = load_tum(gt_path)

    results = {}
    for name, cfg in ALGOS.items():
        if not cfg["path"].exists():
            print(f"  [skip] {name}: {cfg['path']} not found")
            continue
        est_tum = load_tum(cfg["path"])
        aligned, ref_xyz, err = align_and_trim(ref_tum, est_tum)
        if aligned is None:
            print(f"  [skip] {name}: too few matches")
            continue
        results[name] = {"aligned": aligned, "ref": ref_xyz,
                         "err": err, "color": cfg["color"],
                         "ate_rmse": float(np.sqrt((err**2).mean()))}
        print(f"  {name}: {len(aligned)} poses, ATE RMSE={results[name]['ate_rmse']:.3f} m")

    if not results:
        sys.exit("No trajectories found.")

    # ── Figure 1: top-down (XY) trajectory overlay ───────────────────────────
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.plot(ref_tum[:, 1], ref_tum[:, 2], color="black",
            linewidth=1.2, linestyle="--", label="Ground Truth", zorder=5)
    for name, r in results.items():
        ax.plot(r["aligned"][:, 0], r["aligned"][:, 1],
                color=r["color"], linewidth=1.0, label=f"{name}  (ATE={r['ate_rmse']:.2f} m)")
    ax.set_xlabel("X (m)"); ax.set_ylabel("Y (m)")
    ax.set_title(f"Trajectory comparison — {dataset} / {seq}")
    ax.legend(fontsize=9); ax.set_aspect("equal"); ax.grid(alpha=0.3)
    fig.tight_layout()
    p = out_dir / "traj_xy.pdf"
    fig.savefig(p, dpi=150); print(f"Saved {p}")
    fig.savefig(p.with_suffix(".png"), dpi=150)
    plt.close()

    # ── Figure 2: ATE error over time ────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 4))
    for name, r in results.items():
        ref_ts = ref_tum[:, 0]
        est_tum_path = ALGOS[name]["path"]
        est_tum = load_tum(est_tum_path)
        _, matched_ref_xyz = associate(ref_tum, est_tum)  # just need timestamps
        # use matched GT timestamps for x-axis
        matched_ref_arr, _ = associate(ref_tum, est_tum)
        # get time axis from GT matched indices
        ref_xyz_m, est_xyz_m = associate(ref_tum, load_tum(est_tum_path))
        # re-do with timestamps
        ref_ts_arr = []
        est_ts = load_tum(est_tum_path)[:, 0]
        for t in est_ts:
            j = np.argmin(np.abs(ref_tum[:, 0] - t))
            if np.abs(ref_tum[j, 0] - t) <= 0.1:
                ref_ts_arr.append(ref_tum[j, 0])
        t_rel = [t - ref_tum[0, 0] for t in ref_ts_arr[:len(r["err"])]]
        ax.plot(t_rel, r["err"], color=r["color"], linewidth=0.7,
                label=f"{name}  (RMSE={r['ate_rmse']:.2f} m)", alpha=0.85)
    ax.set_xlabel("Time (s)"); ax.set_ylabel("ATE (m)")
    ax.set_title(f"ATE over time — {dataset} / {seq}")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)
    fig.tight_layout()
    p = out_dir / "ate_over_time.pdf"
    fig.savefig(p, dpi=150); print(f"Saved {p}")
    fig.savefig(p.with_suffix(".png"), dpi=150)
    plt.close()

    # ── Figure 3: ATE box plot ────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(5, 5))
    names_list = list(results.keys())
    data_list  = [results[n]["err"] for n in names_list]
    colors     = [results[n]["color"] for n in names_list]
    bp = ax.boxplot(data_list, patch_artist=True, notch=False,
                    medianprops={"color": "black", "linewidth": 1.5})
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color); patch.set_alpha(0.7)
    ax.set_xticks(range(1, len(names_list)+1))
    ax.set_xticklabels(names_list, fontsize=9)
    ax.set_ylabel("ATE (m)")
    ax.set_title(f"ATE distribution — {dataset} / {seq}")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    p = out_dir / "ate_boxplot.pdf"
    fig.savefig(p, dpi=150); print(f"Saved {p}")
    fig.savefig(p.with_suffix(".png"), dpi=150)
    plt.close()

    print("\nAll plots written to", out_dir)


if __name__ == "__main__":
    main()
