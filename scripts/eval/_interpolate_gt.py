#!/usr/bin/env python3
"""Interpolate a sparse GT TUM trajectory to the exact camera timestamps.

Usage:
    python3 _interpolate_gt.py <gt_tum.txt> <times_ns.txt> <out_gt_interp.txt> [--max-gap S]

The GT is re-sampled at each camera timestamp using:
  - Linear interpolation for translation (x, y, z)
  - SLERP for rotation (quaternion, scipy convention: x y z w)

Fabricated-pose policy (changed 2026-08-05 — see PROGRESS "GT interpolation fix"):
  * Camera frames whose timestamps fall OUTSIDE the GT time range are DROPPED
    (previously they were clamped to a frozen boundary pose, which injected up
    to hundreds of fake zero-motion correspondences into the ATE association
    and the Umeyama alignment — e.g. 164 frozen poses on rosariov2/sequence5).
  * Camera frames that fall inside a GT gap larger than --max-gap seconds are
    DROPPED (previously any GT outage — e.g. an RTK dropout — was silently
    bridged by a straight line and treated as authoritative GT).

--max-gap defaults to max(0.5 s, 3x the median GT inter-pose interval), so a
5 Hz GPS-based GT tolerates its nominal 0.2 s spacing but not an outage.

The output therefore has AT MOST as many rows as camera frames; evo timestamp
association (t_max_diff ~= 0.005) simply skips estimate poses without a GT row.

This script is dataset/algorithm agnostic: re-run it whenever gt_tum.txt or
times.txt changes; the output gt_interp_tum.txt is stored alongside gt_tum.txt.
"""
import sys
import numpy as np
from scipy.spatial.transform import Rotation, Slerp


def load_tum(path):
    """Load TUM file -> (timestamps_s, positions Nx3, quaternions Nx4 xyzw)."""
    data = np.loadtxt(path)
    return data[:, 0], data[:, 1:4], data[:, 4:8]   # t, xyz, qxqyqzqw


def load_times_ns(path):
    """Load one-timestamp-per-line nanosecond file -> seconds array."""
    ts = np.loadtxt(path, dtype=np.float64)
    return ts / 1e9


def valid_query_mask(gt_t, query_t, max_gap_s):
    """Mask of camera timestamps that have trustworthy GT support.

    A query time is valid iff it lies inside the GT range AND the GT gap it
    falls into is <= max_gap_s wide.
    """
    gt_t = np.asarray(gt_t, dtype=np.float64)
    inside = (query_t >= gt_t[0]) & (query_t <= gt_t[-1])
    # Index of the GT interval each query falls into
    idx = np.clip(np.searchsorted(gt_t, query_t, side="right") - 1, 0, len(gt_t) - 2)
    gap = gt_t[idx + 1] - gt_t[idx]
    return inside & (gap <= max_gap_s)


def interpolate(gt_t, gt_pos, gt_quat, query_t):
    gt_t = np.asarray(gt_t, dtype=np.float64)

    # Translation: axis-wise linear interpolation
    pos_out = np.zeros((len(query_t), 3))
    for ax in range(3):
        pos_out[:, ax] = np.interp(query_t, gt_t, gt_pos[:, ax])

    # Rotation: SLERP
    rots = Rotation.from_quat(gt_quat)   # scipy xyzw convention
    slerp = Slerp(gt_t, rots)
    quat_out = slerp(query_t).as_quat()   # Nx4 xyzw

    return pos_out, quat_out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    max_gap_s = None
    for i, a in enumerate(sys.argv[1:]):
        if a == "--max-gap" and i + 2 < len(sys.argv):
            max_gap_s = float(sys.argv[i + 2])
            args = [x for x in args if x != sys.argv[i + 2]]
    if len(args) != 3:
        print(f"Usage: {sys.argv[0]} <gt_tum.txt> <times_ns.txt> <out.txt> [--max-gap S]",
              file=sys.stderr)
        sys.exit(1)

    gt_path, times_path, out_path = args

    gt_t, gt_pos, gt_quat = load_tum(gt_path)
    query_t = load_times_ns(times_path)

    if max_gap_s is None:
        med_dt = float(np.median(np.diff(gt_t)))
        max_gap_s = max(0.5, 3.0 * med_dt)

    mask = valid_query_mask(gt_t, query_t, max_gap_s)
    n_outside = int(((query_t < gt_t[0]) | (query_t > gt_t[-1])).sum())
    n_gap = int((~mask).sum() - n_outside)
    if n_outside:
        print(f"[interp_gt] dropped {n_outside}/{len(query_t)} camera frames "
              f"outside GT range (no extrapolation, no clamping)", file=sys.stderr)
    if n_gap > 0:
        print(f"[interp_gt] dropped {n_gap}/{len(query_t)} camera frames inside "
              f"GT gaps > {max_gap_s:.2f} s (no bridging)", file=sys.stderr)

    query_valid = query_t[mask]
    pos_i, quat_i = interpolate(gt_t, gt_pos, gt_quat, query_valid)

    with open(out_path, "w") as f:
        for i, t in enumerate(query_valid):
            x, y, z = pos_i[i]
            qx, qy, qz, qw = quat_i[i]
            f.write(f"{t:.9f} {x:.9f} {y:.9f} {z:.9f} "
                    f"{qx:.9f} {qy:.9f} {qz:.9f} {qw:.9f}\n")

    print(f"[interp_gt] wrote {len(query_valid)} poses "
          f"({len(query_t) - len(query_valid)} dropped, max_gap={max_gap_s:.2f} s) "
          f"-> {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
