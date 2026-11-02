#!/usr/bin/env python3
"""The in-motion IMU level M of the noise search (PLAN Update 6). Reads only IMU streams.

One definition, the paper's (PAPER/vslam-paper/scripts/imu_envelope.py and paperdata/noise.py), which the
plan's range table was checked with; the estimator is that of docs/okvis-imu-noise-derivation.md:

    per axis and non-overlapping 1-s window: 1.4826 * MAD(adjacent differences) / sqrt(2 * f_s)
    per sequence and sensor: 95th percentile over windows, the largest of the three axes
    per dataset: the largest of its two sequences; never rounded

The two random-walk terms of M are the released values (the dataset's static calibration), because the
recordings cannot identify them. Rounded values in earlier protocols are not used anywhere.
"""
import hashlib
from pathlib import Path

import numpy as np

KEYS = ('gyroscope_noise_density', 'accelerometer_noise_density',
        'gyroscope_random_walk', 'accelerometer_random_walk')
DEFINITION = ('1.4826*MAD(adjacent differences)/sqrt(2*fs) per axis in non-overlapping 1-s windows; 95th percentile '
              'over windows; largest over axes; largest over the dataset\'s two sequences; unrounded')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(2**20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def window_densities(t, x, fs):
    """Per 1-s window robust white-noise density of one axis."""
    edges = np.arange(t[0], t[-1], 1.0)
    idx = np.searchsorted(t, edges)
    out = []
    for a, b in zip(idx[:-1], idx[1:]):
        if b - a < 0.5 * fs:
            continue
        d = np.diff(x[a:b])
        mad = np.median(np.abs(d - np.median(d)))
        out.append(1.4826 * mad / np.sqrt(2 * fs))
    return np.array(out)


def sequence_levels(path):
    """The per-sequence statistics of one EuRoC IMU table (t[ns], gyro xyz, accel xyz)."""
    arr = np.loadtxt(path, delimiter=',', comments='#')
    t = arr[:, 0] * 1e-9
    fs = (len(t) - 1) / (t[-1] - t[0])
    stats = {}
    for name, cols in (('gyro', (1, 2, 3)), ('accel', (4, 5, 6))):
        stats[name + '_q95'] = float(max(np.percentile(window_densities(t, arr[:, c], fs), 95) for c in cols))
    stats.update(rate_hz=float(fs), duration_s=float(t[-1] - t[0]), samples=int(len(t)), sha256=sha(path))
    return stats


def dataset_level(per_sequence, static):
    """M for one dataset: unrounded in-motion densities with the released random walks."""
    return {KEYS[0]: max(s['gyro_q95'] for s in per_sequence.values()),
            KEYS[1]: max(s['accel_q95'] for s in per_sequence.values()),
            KEYS[2]: float(static[KEYS[2]]), KEYS[3]: float(static[KEYS[3]])}
