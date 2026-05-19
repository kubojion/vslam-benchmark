#!/usr/bin/env python3
"""Interpolate a sparse GT TUM trajectory to the exact camera timestamps.

Usage:
    python3 _interpolate_gt.py <gt_tum.txt> <times_ns.txt> <out_gt_interp.txt>

The GT is re-sampled at each camera timestamp using:
  - Linear interpolation for translation (x, y, z)
  - SLERP for rotation (quaternion, scipy convention: x y z w)

Camera frames whose timestamps fall outside the GT time range are clamped
to the nearest GT boundary (no extrapolation).

The resulting file has the SAME number of rows as camera frames, making
evo timestamp association trivial (t_max_diff ~= 0).

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


def interpolate(gt_t, gt_pos, gt_quat, query_t):
    gt_t = np.asarray(gt_t, dtype=np.float64)
    # Clamp query timestamps to GT range to avoid extrapolation
    query_clamped = np.clip(query_t, gt_t[0], gt_t[-1])

    # Translation: axis-wise linear interpolation
    pos_out = np.zeros((len(query_clamped), 3))
    for ax in range(3):
        pos_out[:, ax] = np.interp(query_clamped, gt_t, gt_pos[:, ax])

    # Rotation: SLERP
    rots = Rotation.from_quat(gt_quat)   # scipy xyzw convention
    slerp = Slerp(gt_t, rots)
    quat_out = slerp(query_clamped).as_quat()   # Nx4 xyzw

    return pos_out, quat_out


def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <gt_tum.txt> <times_ns.txt> <out.txt>",
              file=sys.stderr)
        sys.exit(1)

    gt_path, times_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

    gt_t, gt_pos, gt_quat = load_tum(gt_path)
    query_t = load_times_ns(times_path)

    n_outside = int(((query_t < gt_t[0]) | (query_t > gt_t[-1])).sum())
    if n_outside:
        print(f"[interp_gt] warning: {n_outside}/{len(query_t)} camera frames "
              f"outside GT range — clamped to boundaries", file=sys.stderr)

    pos_i, quat_i = interpolate(gt_t, gt_pos, gt_quat, query_t)

    with open(out_path, "w") as f:
        for i, t in enumerate(query_t):
            x, y, z = pos_i[i]
            qx, qy, qz, qw = quat_i[i]
            f.write(f"{t:.9f} {x:.9f} {y:.9f} {z:.9f} "
                    f"{qx:.9f} {qy:.9f} {qz:.9f} {qw:.9f}\n")

    print(f"[interp_gt] wrote {len(query_t)} poses -> {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
