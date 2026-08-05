#!/usr/bin/env python3
"""Gap-aware trajectory coverage — the single coverage metric for the benchmark.

Motivation (2026-08-05 audit): the pipeline previously carried three divergent
"coverage" numbers, none reliable:

  * track_pct                      output-pose count / frame count -> ~10 % for
                                   keyframe-only exporters on complete runs,
                                   >1000 % for IMU-rate exporters. Not coverage.
  * trajectory_time_coverage_pct   (t_last - t_first) / sequence_duration ->
                                   endpoint span only; blind to interior
                                   tracking holes (exactly ORB-SLAM3's
                                   agricultural failure mode).
  * ate_pair_coverage_pct          associated-pair count / frame count; depends
                                   on output rate like track_pct.

This module defines ONE metric, computable for every run from artifacts that are
always present (trajectory.txt + the sequence duration):

    coverage_gap_pct = (covered_time / sequence_duration_s) * 100

    covered_time = trajectory time span
                   minus the part of every interior gap that exceeds a
                   per-run gap threshold.

    gap threshold = max(GAP_MIN_S, GAP_MEDIAN_FACTOR * median inter-pose dt)

The adaptive threshold makes the metric safe for keyframe-only exporters (whose
nominal inter-pose dt is large) while still catching genuine tracking holes.
Endpoint truncation is caught because the span itself is short of the sequence
duration. Values are clipped to [0, 100].

Timestamps are sanitized first (unit detection ns/us/ms -> s, non-finite and
non-monotonic rows dropped) so that corrupt trajectories (see the openvins_gps
timestamp bug) yield a *low* coverage instead of a nonsense one.
"""
from __future__ import annotations

import numpy as np

GAP_MIN_S = 2.0            # never call a hole smaller than this a gap
GAP_MEDIAN_FACTOR = 5.0    # ... nor smaller than 5x the run's own median dt


def sanitize_timestamps(t: np.ndarray) -> tuple[np.ndarray, dict]:
    """Return (clean seconds-timestamps, info dict).

    Detects ns/us/ms units by magnitude, drops non-finite entries, and drops
    rows that break monotonicity (keeps the longest reasonable prefix walk).
    """
    info = {"n_raw": int(len(t)), "unit": "s", "n_dropped_nonmono": 0,
            "n_dropped_nonfinite": 0}
    t = np.asarray(t, dtype=np.float64)
    finite = np.isfinite(t)
    info["n_dropped_nonfinite"] = int((~finite).sum())
    t = t[finite]
    if len(t) == 0:
        return t, info
    # Unit detection: epoch seconds are ~1.7e9 in 2026; ns ~1.7e18; us ~1.7e15;
    # ms ~1.7e12. Relative timestamps are small and already seconds.
    med = float(np.median(t))
    if med > 1e17:
        t = t / 1e9
        info["unit"] = "ns"
    elif med > 1e14:
        t = t / 1e6
        info["unit"] = "us"
    elif med > 1e11:
        t = t / 1e3
        info["unit"] = "ms"
    # Drop rows that go backwards (keep first occurrence walk)
    keep = np.ones(len(t), dtype=bool)
    last = -np.inf
    for i, v in enumerate(t):
        if v <= last - 1e-9:
            keep[i] = False
        else:
            last = v
    info["n_dropped_nonmono"] = int((~keep).sum())
    return t[keep], info


def coverage_gap_pct(traj_t: np.ndarray, sequence_duration_s: float) -> dict:
    """Compute the gap-aware coverage of a trajectory over its sequence.

    Returns a dict with:
      coverage_gap_pct    the headline number (0..100, 1 decimal), or None
      traj_span_s         sanitized trajectory time span
      interior_gap_s      total interior time attributed to tracking holes
      gap_threshold_s     the per-run threshold used
      n_gaps              number of interior gaps above the threshold
      ts_unit / ts_dropped  sanitization info
    """
    out = {"coverage_gap_pct": None, "traj_span_s": None, "interior_gap_s": None,
           "gap_threshold_s": None, "n_gaps": None, "ts_unit": None,
           "ts_dropped": None}
    if sequence_duration_s is None or sequence_duration_s <= 0:
        return out
    t, info = sanitize_timestamps(np.asarray(traj_t, dtype=np.float64))
    out["ts_unit"] = info["unit"]
    out["ts_dropped"] = info["n_dropped_nonfinite"] + info["n_dropped_nonmono"]
    if len(t) < 2:
        out["coverage_gap_pct"] = 0.0
        out["traj_span_s"] = 0.0
        out["interior_gap_s"] = 0.0
        out["n_gaps"] = 0
        return out
    dt = np.diff(t)
    med_dt = float(np.median(dt))
    thr = max(GAP_MIN_S, GAP_MEDIAN_FACTOR * med_dt)
    gaps = dt[dt > thr]
    interior = float(np.sum(gaps - thr)) if len(gaps) else 0.0
    span = float(t[-1] - t[0])
    covered = max(0.0, span - interior)
    cov = 100.0 * covered / float(sequence_duration_s)
    out["coverage_gap_pct"] = round(min(100.0, max(0.0, cov)), 1)
    out["traj_span_s"] = round(span, 2)
    out["interior_gap_s"] = round(interior, 2)
    out["gap_threshold_s"] = round(thr, 3)
    out["n_gaps"] = int(len(gaps))
    return out


def coverage_from_traj_file(traj_path, sequence_duration_s: float) -> dict:
    """Convenience: load a TUM trajectory file and compute coverage."""
    try:
        data = np.loadtxt(str(traj_path), usecols=(0,))
    except Exception:
        return coverage_gap_pct(np.array([]), sequence_duration_s)
    return coverage_gap_pct(np.atleast_1d(data), sequence_duration_s)
