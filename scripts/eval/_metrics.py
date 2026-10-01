"""Explicit trajectory metrics; no estimator execution or filesystem mutation.

Poses are T_world_sensor, with seconds, metres and Hamilton xyzw quaternions.
The caller must establish a common physical sensor frame before using these
functions. Metric validity and publication qualification are separate decisions.
"""
from __future__ import annotations

import numpy as np
from scipy.spatial.transform import Rotation, Slerp


def validate_poses(poses):
    """Reject malformed trajectories instead of silently sanitizing evidence."""
    a = np.asarray(poses, dtype=float)
    if a.ndim != 2 or a.shape[1] != 8 or len(a) < 2:
        raise ValueError("expected at least two TUM poses with eight columns")
    if not np.isfinite(a).all():
        raise ValueError("non-finite trajectory data")
    if np.any(np.diff(a[:, 0]) <= 0):
        raise ValueError("timestamps must be strictly increasing seconds")
    if np.median(np.abs(a[:, 0])) > 1e11:
        raise ValueError("timestamps are not in seconds")
    norms = np.linalg.norm(a[:, 4:], axis=1)
    if np.any(np.abs(norms - 1) > 0.01):
        raise ValueError("invalid quaternion norm (tolerance 0.01)")
    a = a.copy()
    a[:, 4:] /= norms[:, None]
    return a


def right_transform(poses, sensor_T_target):
    """Change the tracked physical frame: T_W_target = T_W_sensor T_sensor_target.

    Unlike a world-frame alignment this moves the origin along its rotating
    lever arm. Do not use a metric translation on an unscaled monocular estimate.
    """
    a = np.asarray(poses).copy()
    t = np.asarray(sensor_T_target, dtype=float)
    if t.shape != (4, 4) or not np.allclose(t[3], [0, 0, 0, 1]):
        raise ValueError("expected a homogeneous 4x4 transform")
    if not np.allclose(t[:3, :3].T @ t[:3, :3], np.eye(3), atol=2e-5):
        raise ValueError("extrinsic rotation is not orthonormal")
    if not np.isclose(np.linalg.det(t[:3, :3]), 1, atol=2e-5):
        raise ValueError("extrinsic contains a reflection")
    rot = Rotation.from_quat(a[:, 4:])
    a[:, 1:4] += rot.apply(t[:3, 3])
    a[:, 4:] = (rot * Rotation.from_matrix(t[:3, :3])).as_quat()
    return a


def interpolate_reference(reference, times, max_gap_s=0.5):
    """Interpolate reference only; never extrapolate or bridge a reference gap.

    Exact samples remain valid even if the following reference interval is large.
    Returns the supported poses and a mask into the query timestamps.
    """
    g = validate_poses(reference)
    q = np.asarray(times, dtype=float)
    idx = np.searchsorted(g[:, 0], q, side="left")
    hi = np.clip(idx, 0, len(g) - 1)
    lo = np.maximum(hi - 1, 0)
    exact = np.abs(g[hi, 0] - q) <= 1e-8
    keep = (q >= g[0, 0]) & (q <= g[-1, 0])
    keep &= exact | ((g[hi, 0] - g[lo, 0]) <= max_gap_s)
    result = np.empty((int(keep.sum()), 8))
    result[:, 0] = q[keep]
    for j in range(1, 4):
        result[:, j] = np.interp(q[keep], g[:, 0], g[:, j])
    if len(result):
        result[:, 4:] = Slerp(g[:, 0], Rotation.from_quat(g[:, 4:]))(q[keep]).as_quat()
    return result, keep


def camera_association(estimate, camera_times, tolerance_s=0.005):
    """At most one actual estimated pose per camera timestamp; no estimate filling.

    Sparse exporters stay sparse. High-rate IMU exporters do not overweight the
    score. An estimate can occur in at most one pair. Returns poses, camera indices
    and measured timestamp differences. Ties choose the earlier estimate.
    """
    a = validate_poses(estimate)
    t = np.asarray(camera_times, dtype=float)
    if len(t) < 2 or np.any(np.diff(t) <= 0):
        raise ValueError("camera timestamps must be strictly increasing")
    hi = np.clip(np.searchsorted(a[:, 0], t), 0, len(a) - 1)
    lo = np.maximum(hi - 1, 0)
    idx = np.where(np.abs(a[lo, 0] - t) <= np.abs(a[hi, 0] - t), lo, hi)
    dt = np.abs(a[idx, 0] - t)
    valid = np.flatnonzero(dt <= tolerance_s)
    # Greedy nearest-time assignment resolves rare overlapping tolerance windows.
    selected, used = [], set()
    for k in sorted(valid, key=lambda k: (dt[k], k)):
        if int(idx[k]) not in used:
            selected.append(int(k))
            used.add(int(idx[k]))
    selected = np.array(sorted(selected), dtype=int)
    return a[idx[selected]].copy(), selected, dt[selected]


def fit_alignment(source, target, correct_scale=False):
    """Umeyama least-squares SE(3) or Sim(3), including degeneracy checks."""
    x, y = np.asarray(source, dtype=float), np.asarray(target, dtype=float)
    if x.shape != y.shape or x.ndim != 2 or x.shape[1] != 3 or len(x) < 3:
        raise ValueError("alignment requires at least three corresponding positions")
    xc, yc = x - x.mean(0), y - y.mean(0)
    covariance = yc.T @ xc / len(x)
    u, d, vt = np.linalg.svd(covariance)
    if d[0] <= 1e-15 or d[1] <= d[0] * 1e-10:
        raise ValueError("alignment is degenerate (stationary or collinear positions)")
    s = np.ones(3)
    s[-1] = np.sign(np.linalg.det(u @ vt))
    r = u @ np.diag(s) @ vt
    scale = float(d @ s / np.mean(np.sum(xc * xc, axis=1))) if correct_scale else 1.0
    return r, y.mean(0) - scale * r @ x.mean(0), scale


def apply_alignment(poses, alignment):
    r, t, scale = alignment
    a = np.asarray(poses).copy()
    a[:, 1:4] = scale * (a[:, 1:4] @ r.T) + t
    a[:, 4:] = (Rotation.from_matrix(r) * Rotation.from_quat(a[:, 4:])).as_quat()
    return a


def statistics(values):
    v = np.asarray(values, dtype=float)
    if not len(v):
        return {k: None for k in ("rmse", "mean", "median", "std", "max", "min")} | {"n": 0}
    if not np.isfinite(v).all():
        raise ValueError("non-finite metric residuals")
    return dict(rmse=float(np.sqrt(np.mean(v*v))), mean=float(np.mean(v)),
                median=float(np.median(v)), std=float(np.std(v)),
                max=float(np.max(v)), min=float(np.min(v)), n=len(v))


def relative_errors(reference, estimate, pairs):
    """Full relative-pose translation, rotation and displacement-magnitude errors."""
    i, j = np.asarray(pairs, dtype=int).T if len(pairs) else ([], [])
    if not len(i):
        return np.array([]), np.array([]), np.array([])
    gr, er = Rotation.from_quat(reference[:, 4:]), Rotation.from_quat(estimate[:, 4:])
    gd = reference[j, 1:4] - reference[i, 1:4]
    ed = estimate[j, 1:4] - estimate[i, 1:4]
    gt = gr[i].inv().apply(gd)
    et = er[i].inv().apply(ed)
    # Norm of inv(delta_GT) @ delta_est translation equals ||et - gt||.
    translation = np.linalg.norm(et - gt, axis=1)
    rotation = ((gr[i].inv()*gr[j]).inv() * (er[i].inv()*er[j])).magnitude() * 180/np.pi
    displacement = np.abs(np.linalg.norm(ed, axis=1) - np.linalg.norm(gd, axis=1))
    return translation, rotation, displacement


def distance_pairs(reference, distance_m, max_gap_s, relative_tolerance=0.1):
    """Overlapping reference-distance windows, first sample at/above each length.

    Endpoints must be within 10% of the requested distance. A pair cannot cross
    a sampling hole. This documented custom protocol is NOT the KITTI benchmark.
    """
    g = np.asarray(reference)
    if distance_m <= 0 or max_gap_s <= 0:
        raise ValueError("distance and maximum gap must be positive")
    cumulative = np.r_[0, np.cumsum(np.linalg.norm(np.diff(g[:, 1:4], axis=0), axis=1))]
    holes = np.r_[0, np.cumsum(np.diff(g[:, 0]) > max_gap_s)]
    i = np.arange(len(g))
    j = np.searchsorted(cumulative, cumulative + distance_m)
    keep = j < len(g)
    i, j = i[keep], j[keep]
    keep = ((cumulative[j] - cumulative[i]) <= distance_m*(1 + relative_tolerance))
    keep &= holes[i] == holes[j]
    return np.c_[i[keep], j[keep]]


def translation_origin_errors(reference, estimate):
    """Translation-only origin registration, with no rotation or scale fitting."""
    aligned = estimate[:, 1:4] + reference[0, 1:4] - estimate[0, 1:4]
    return statistics(np.linalg.norm(aligned - reference[:, 1:4], axis=1))
