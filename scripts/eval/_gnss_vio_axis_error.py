#!/usr/bin/env python3
"""Per-axis (X/Y/Z) RMSE decomposition of GNSS-VIO trajectories vs ground truth.

Aligns each estimated TUM trajectory to GT via Umeyama Sim3 (same alignment the
main evaluator uses) and reports horizontal vs vertical RMSE, so the vertical
(z) share of the ATE is visible. On near-flat agricultural terrain a large
vertical share indicates GPS vertical noise propagating into the fused estimate
rather than genuine terrain following.

Usage:
    python3 scripts/eval/_gnss_vio_axis_error.py

Reads results-gnss-vio/<dataset>/<seq>/<algo>/run1/trajectory.txt against
datasets/<dataset>/<seq>/gt_tum.txt for every GNSS-VIO algorithm/sequence.
"""
from pathlib import Path
import numpy as np

WS = Path(__file__).resolve().parents[2]


def load_tum(p):
    a = []
    for ln in Path(p).read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        v = ln.split()
        if len(v) >= 4:
            a.append([float(v[0]), float(v[1]), float(v[2]), float(v[3])])
    return np.array(a)


def assoc(est, gt, tol=0.05):
    eo, go = [], []
    gts = gt[:, 0]
    for r in est:
        j = int(np.argmin(np.abs(gts - r[0])))
        if abs(gts[j] - r[0]) <= tol:
            eo.append(r[1:4])
            go.append(gt[j, 1:4])
    return np.array(eo), np.array(go)


def umeyama(src, dst):
    mu_s = src.mean(0)
    mu_d = dst.mean(0)
    s_c = src - mu_s
    d_c = dst - mu_d
    cov = (d_c.T @ s_c) / len(src)
    U, D, Vt = np.linalg.svd(cov)
    S = np.eye(3)
    if np.linalg.det(U) * np.linalg.det(Vt) < 0:
        S[2, 2] = -1
    R = U @ S @ Vt
    var_s = (s_c ** 2).sum() / len(src)
    s = np.trace(np.diag(D) @ S) / var_s
    t = mu_d - s * R @ mu_s
    return s, R, t


def analyse(label, est_path, gt_path):
    est = load_tum(est_path)
    gt = load_tum(gt_path)
    e, g = assoc(est, gt)
    if len(e) < 10:
        print(f"{label}: too few associations ({len(e)})")
        return
    s, R, t = umeyama(e, g)
    ea = (s * (R @ e.T).T) + t
    err = ea - g
    rx = np.sqrt((err[:, 0] ** 2).mean())
    ry = np.sqrt((err[:, 1] ** 2).mean())
    rz = np.sqrt((err[:, 2] ** 2).mean())
    rh = np.sqrt((err[:, 0] ** 2 + err[:, 1] ** 2).mean())
    r3 = np.sqrt((err ** 2).sum(1).mean())
    gz = g[:, 2]
    print(f"{label}: N={len(e)} scale={s:.4f}")
    print(f"   3D RMSE={r3:.3f}  X={rx:.3f}  Y={ry:.3f}  Z={rz:.3f}  | HOR={rh:.3f} VER={rz:.3f}")
    print(f"   vertical share of variance = {rz ** 2 / r3 ** 2 * 100:.0f}%   GT z-span={gz.max() - gz.min():.2f}m")


def main():
    algos = ["vins_fusion_gps", "cifasis_gnss_si", "rtabmap_gps", "openvins_gps"]
    seqs = [
        ("rosariov2", "sequence1"),
        ("rosariov2", "sequence5"),
        ("hortimulti", "strawberry02"),
        ("hortimulti", "strawberry03"),
    ]
    for algo in algos:
        for ds, sq in seqs:
            est = WS / "results-gnss-vio" / ds / sq / algo / "run1" / "trajectory.txt"
            gtp = WS / "datasets" / ds / sq / "gt_tum.txt"
            if not est.exists() or not gtp.exists():
                continue
            try:
                analyse(f"{algo:16s} {ds}/{sq}", est, gtp)
            except Exception as ex:  # noqa: BLE001
                print(f"{algo} {ds}/{sq}: ERROR {ex}")


if __name__ == "__main__":
    main()
