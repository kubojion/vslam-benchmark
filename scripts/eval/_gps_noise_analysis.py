#!/usr/bin/env python3
"""One-off analysis: quantify Rosario v2 GPS noise (conventional vs PPK) vs GT.

For seq5 (we have both bags locally):
  - extract /reach_1/gps/fix (conventional) and /reach_1/ppk/fix (PPK)
  - convert lat/lon/alt -> local ENU (pyproj, first-fix origin)
  - align each to gt_tum.txt via Umeyama Sim3 (GPS and GT live in different frames)
  - report 3D / horizontal / vertical RMSE residuals

This tells us the *actual* GPS accuracy that was fed to the GNSS-VIO algorithms.
"""
import sys
from pathlib import Path
import numpy as np
from rosbags.rosbag1 import Reader
from rosbags.typesys import Stores, get_typestore
from pyproj import Transformer, CRS

TS = get_typestore(Stores.ROS1_NOETIC)


def read_navsatfix(bag, topic):
    out = []
    with Reader(bag) as r:
        avail = {c.topic for c in r.connections}
        if topic not in avail:
            print(f"[warn] {topic} not in {bag}; have: {sorted(avail)}")
            return np.empty((0, 4))
        for c, _t, raw in r.messages():
            if c.topic != topic:
                continue
            m = TS.deserialize_ros1(raw, c.msgtype)
            t = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
            out.append([t, m.latitude, m.longitude, m.altitude])
    return np.array(out)


def llh_to_enu(llh):
    """llh: Nx3 lat,lon,alt -> Nx3 ENU about first fix using local UTM."""
    lat0, lon0 = llh[0, 0], llh[0, 1]
    # geodetic -> ECEF -> local ENU is overkill; for a few-hundred-m track a
    # UTM projection is accurate to mm. Pick the UTM zone of the first fix.
    zone = int((lon0 + 180) / 6) + 1
    south = lat0 < 0
    epsg = 32700 + zone if south else 32600 + zone
    tr = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(epsg), always_xy=True)
    e, n = tr.transform(llh[:, 1], llh[:, 0])
    u = llh[:, 2]
    enu = np.column_stack([e, n, u])
    return enu - enu[0]


def load_tum(path):
    rows = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        p = line.split()
        rows.append([float(p[0]), float(p[1]), float(p[2]), float(p[3])])
    return np.array(rows)


def match(t_a, t_b, max_dt=0.05):
    """For each a, nearest b within max_dt. Returns (idx_a, idx_b)."""
    ia, ib = [], []
    j = 0
    for i, t in enumerate(t_a):
        while j + 1 < len(t_b) and abs(t_b[j + 1] - t) <= abs(t_b[j] - t):
            j += 1
        if abs(t_b[j] - t) <= max_dt:
            ia.append(i)
            ib.append(j)
    return np.array(ia), np.array(ib)


def umeyama(src, dst):
    """Sim3 align src->dst. Returns aligned src."""
    mu_s = src.mean(0)
    mu_d = dst.mean(0)
    s0 = src - mu_s
    d0 = dst - mu_d
    H = s0.T @ d0 / len(src)
    U, D, Vt = np.linalg.svd(H)
    S = np.eye(3)
    if np.linalg.det(U) * np.linalg.det(Vt) < 0:
        S[2, 2] = -1
    R = Vt.T @ S @ U.T
    var = (s0 ** 2).sum() / len(src)
    scale = np.trace(np.diag(D) @ S) / var
    t = mu_d - scale * R @ mu_s
    return (scale * (R @ src.T).T + t)


def analyse(label, llh, gt):
    if len(llh) == 0:
        print(f"{label}: NO DATA")
        return
    enu = llh_to_enu(llh[:, 1:4])
    ia, ib = match(llh[:, 0], gt[:, 0])
    if len(ia) < 10:
        print(f"{label}: only {len(ia)} matches")
        return
    src = enu[ia]
    dst = gt[ib, 1:4]
    aligned = umeyama(src, dst)
    err = aligned - dst
    h = np.linalg.norm(err[:, :2], axis=1)
    v = np.abs(err[:, 2])
    d3 = np.linalg.norm(err, axis=1)
    print(f"{label}:  N={len(ia)}")
    print(f"   3D  RMSE={np.sqrt((d3**2).mean()):.3f}m  median={np.median(d3):.3f}m  max={d3.max():.3f}m")
    print(f"   HOR RMSE={np.sqrt((h**2).mean()):.3f}m  median={np.median(h):.3f}m  max={h.max():.3f}m")
    print(f"   VER RMSE={np.sqrt((v**2).mean()):.3f}m  median={np.median(v):.3f}m  max={v.max():.3f}m")


def main():
    base = Path("/home/jion_kubo/Downloads/rosariov2-seq5")
    conv_bag = base / "2023-12-26-15-10-15_conventional_gnss.bag"
    ppk_bag = base / "2023-12-26-15-10-15_ppk_gnss.bag"
    gt = load_tum("datasets/rosariov2/sequence5/gt_tum.txt")
    print(f"GT poses: {len(gt)}  span={gt[-1,0]-gt[0,0]:.1f}s\n")

    print("=== seq5 conventional /reach_1/gps/fix (what GNSS-VIO actually used) ===")
    conv = read_navsatfix(conv_bag, "/reach_1/gps/fix")
    analyse("CONV", conv, gt)
    print()
    print("=== seq5 PPK /reach_1/ppk/fix (available, NOT used) ===")
    ppk = read_navsatfix(ppk_bag, "/reach_1/ppk/fix")
    analyse("PPK", ppk, gt)


if __name__ == "__main__":
    main()
