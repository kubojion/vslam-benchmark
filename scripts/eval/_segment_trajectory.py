#!/usr/bin/env python3
"""Auto-segment a TUM trajectory into 'row' (straight) and 'turn' segments.

A sliding window of PATH LENGTH (not time) is used so the result is robot-speed
invariant. A sample belongs to a TURN if EITHER:
  (1) cumulative heading change inside the window exceeds yaw_thresh_deg, OR
  (2) the maximum perpendicular deviation from the straight chord through the
      window exceeds straight_tol_m.
Otherwise it is a ROW.

Defaults follow the user's intuition: 2 m window, 50 cm tolerance, 10° heading
cap. After per-sample classification, contiguous samples are merged into
segments and any segment shorter than min_seg_path_m metres is absorbed into
its neighbour to remove noise spikes.

Output CSV: t_start, t_end, type, n_frames, duration_s, path_m

Usage:
    python3 _segment_trajectory.py <gt_tum.txt> <out.csv>
        [--win_path_m 2.0] [--yaw_thresh_deg 10] [--straight_tol_m 0.50]
        [--min_seg_path_m 1.0]
"""
import sys
import argparse
import numpy as np
from scipy.spatial.transform import Rotation


def cumulative_path(xy):
    d = np.linalg.norm(np.diff(xy, axis=0), axis=1)
    return np.concatenate([[0.0], np.cumsum(d)])


def window_indices(s, i, half):
    n = len(s)
    lo = i
    while lo > 0 and s[i] - s[lo - 1] < half:
        lo -= 1
    hi = i
    while hi < n - 1 and s[hi + 1] - s[i] < half:
        hi += 1
    return lo, hi


def max_perp_dev(xy_win):
    if len(xy_win) < 3:
        return 0.0
    p0, pN = xy_win[0], xy_win[-1]
    d = pN - p0
    L = np.linalg.norm(d)
    if L < 1e-6:
        return float(np.linalg.norm(xy_win - p0, axis=1).max())
    n = np.array([-d[1], d[0]]) / L
    return float(np.abs((xy_win - p0) @ n).max())


def classify(t, xy, yaw_deg, win_path_m, yaw_thresh_deg, straight_tol_m):
    s = cumulative_path(xy)
    yaw_u = np.unwrap(np.deg2rad(yaw_deg))
    half = 0.5 * win_path_m
    is_turn = np.zeros(len(t), dtype=bool)
    for i in range(len(t)):
        lo, hi = window_indices(s, i, half)
        path_in_win = s[hi] - s[lo]
        d_yaw_deg = np.rad2deg(abs(yaw_u[hi] - yaw_u[lo]))
        max_dev = max_perp_dev(xy[lo:hi + 1])
        if path_in_win < 0.3 * win_path_m:
            # Slow / stationary zone — only call turn if heading change is large.
            is_turn[i] = d_yaw_deg > 2 * yaw_thresh_deg
        else:
            is_turn[i] = (d_yaw_deg > yaw_thresh_deg) or (max_dev > straight_tol_m)
    return is_turn, s


def merge_segments(t, is_turn, s, min_seg_path_m):
    segs = []
    i = 0
    while i < len(t):
        j = i + 1
        while j < len(t) and is_turn[j] == is_turn[i]:
            j += 1
        segs.append({
            "t_start": float(t[i]),
            "t_end":   float(t[j - 1]),
            "is_turn": bool(is_turn[i]),
            "n":       int(j - i),
            "path":    float(s[j - 1] - s[i]),
        })
        i = j

    changed = True
    while changed:
        changed = False
        out = []
        k = 0
        while k < len(segs):
            seg = segs[k]
            if seg["path"] < min_seg_path_m and len(segs) > 1:
                changed = True
                prev_ok = k > 0 and len(out) > 0
                next_ok = k + 1 < len(segs)
                if prev_ok and next_ok:
                    target_next = out[-1]["path"] < segs[k + 1]["path"]
                elif prev_ok:
                    target_next = False
                else:
                    target_next = True
                if target_next:
                    nxt = segs[k + 1]
                    out.append({
                        "t_start": seg["t_start"],
                        "t_end":   nxt["t_end"],
                        "is_turn": nxt["is_turn"],
                        "n":       seg["n"] + nxt["n"],
                        "path":    seg["path"] + nxt["path"],
                    })
                    k += 2
                else:
                    prev = out[-1]
                    prev["t_end"] = seg["t_end"]
                    prev["n"]    += seg["n"]
                    prev["path"] += seg["path"]
                    k += 1
            else:
                out.append(seg)
                k += 1
        segs = out
    return segs


def main():
    ap = argparse.ArgumentParser(
        description="Segment a GT TUM trajectory into row/turn using "
                    "sliding-window straightness + heading change.")
    ap.add_argument("gt_tum")
    ap.add_argument("out_csv")
    ap.add_argument("--win_path_m",     type=float, default=2.0)
    ap.add_argument("--yaw_thresh_deg", type=float, default=10.0)
    ap.add_argument("--straight_tol_m", type=float, default=0.50)
    ap.add_argument("--min_seg_path_m", type=float, default=1.0)
    args = ap.parse_args()

    data = np.loadtxt(args.gt_tum)
    t   = data[:, 0]
    xy  = data[:, 1:3]
    quat = data[:, 4:8]
    yaw = Rotation.from_quat(quat).as_euler("zyx", degrees=True)[:, 0]

    is_turn, s = classify(
        t, xy, yaw,
        win_path_m=args.win_path_m,
        yaw_thresh_deg=args.yaw_thresh_deg,
        straight_tol_m=args.straight_tol_m,
    )
    segs = merge_segments(t, is_turn, s, min_seg_path_m=args.min_seg_path_m)

    with open(args.out_csv, "w") as f:
        f.write("t_start,t_end,type,n_frames,duration_s,path_m\n")
        for seg in segs:
            stype = "turn" if seg["is_turn"] else "row"
            dur = seg["t_end"] - seg["t_start"]
            f.write(f"{seg['t_start']:.9f},{seg['t_end']:.9f},{stype},"
                    f"{seg['n']},{dur:.3f},{seg['path']:.3f}\n")

    n_row  = sum(1 for x in segs if not x["is_turn"])
    n_turn = sum(1 for x in segs if x["is_turn"])
    row_d  = sum(x["t_end"] - x["t_start"] for x in segs if not x["is_turn"])
    turn_d = sum(x["t_end"] - x["t_start"] for x in segs if x["is_turn"])
    row_p  = sum(x["path"] for x in segs if not x["is_turn"])
    turn_p = sum(x["path"] for x in segs if x["is_turn"])
    print(f"[segment_traj] {len(segs)} segments: "
          f"{n_row} row ({row_d:.1f}s, {row_p:.1f}m), "
          f"{n_turn} turn ({turn_d:.1f}s, {turn_p:.1f}m) -> {args.out_csv}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
