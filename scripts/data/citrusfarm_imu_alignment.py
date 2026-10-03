#!/usr/bin/env python3
"""Measure the CitrusFarm camera-to-MicroStrain time offset and check the rotation chain.

The ZED2i's internal IMU is stamped on the camera clock (ZED SDK, hardware-synchronised
with the stereo images), so both gyroscopes see the same rigid-body rotation:

  time offset   cross-correlation of |omega| (rotation-invariant) between the ZED IMU and
                the re-stamped MicroStrain, reported as offset_s = t_imu - t_cam for the
                same instant (Kalibr's timeshift convention, the sensor profile's
                camera_imu_time_offset_s). Also per 60 s window, to show it is stable.
  rotation      least-squares rotation between the two angular-velocity streams after the
                time shift, compared with the authors' Kalibr chain (MicroStrain -> Blackfly
                -> ZED left) combined with the nominal ZED2i IMU axes. This checks the chain's
                direction conventions; the ZED IMU's own factory misalignment (unpublished,
                typically below 1 degree) is part of the residual.

Uses only the two IMU streams and the authors' calibration files, no images, estimator
output or ground truth.

Usage: citrusfarm_imu_alignment.py <extracted sequence> <calibration results folder> [--json out]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import yaml
from scipy.spatial.transform import Rotation

# ZED2i left optical frame (x right, y down, z forward) from the ZED IMU link frame
# (x forward, y left, z up): nominal axes only.
R_OPTICAL_ZEDIMU = np.array([[0., -1., 0.], [0., 0., -1.], [1., 0., 0.]])


def load(path):
    a = np.loadtxt(path, delimiter=',', comments='#')
    return a[:, 0].astype(np.int64), a[:, 1:4]


def chain(calibration):
    """T_zedleft_microstrain from the authors' two Kalibr results."""
    imu_cam = yaml.safe_load((calibration / '02-imu-cam-result.yaml').read_text())
    multi = yaml.safe_load((calibration / '01-multi-cam-result.yaml').read_text())
    t_blackfly_imu = np.array(imu_cam['cam0']['T_cam_imu'], dtype=float)
    t_zedleft_blackfly = np.array(multi['cam1']['T_cn_cnm1'], dtype=float)   # cam1 = ZED left, cam0 = Blackfly
    if multi['cam1']['rostopic'] != '/zed2i/zed_node/left/image_rect_color':
        raise ValueError('multi-camera cam1 is not the rectified ZED left image')
    return t_zedleft_blackfly @ t_blackfly_imu, float(imu_cam['cam0']['timeshift_cam_imu'])


def correlate(t_ref, x_ref, t_other, x_other, lags_s):
    """Pearson correlation of x_other(t + lag) with x_ref(t) on the reference stamps."""
    out = []
    for lag in lags_s:
        y = np.interp(t_ref + lag, t_other, x_other, left=np.nan, right=np.nan)
        ok = np.isfinite(y)
        out.append(np.corrcoef(x_ref[ok], y[ok])[0, 1] if ok.sum() > 100 else np.nan)
    return np.array(out)


def peak(lags, corr):
    i = int(np.nanargmax(corr))
    if 0 < i < len(corr) - 1:
        a, b, c = corr[i - 1:i + 2]
        d = (a - c) / (2 * (a - 2 * b + c)) if (a - 2 * b + c) != 0 else 0.0
        return float(lags[i] + d * (lags[1] - lags[0])), float(b)
    return float(lags[i]), float(corr[i])


def smooth(x, n):
    return np.convolve(x, np.ones(n) / n, mode='same') if n > 1 else x


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('sequence', type=Path)
    ap.add_argument('calibration', type=Path, help="authors' Calibration/results folder")
    ap.add_argument('--json', type=Path)
    ap.add_argument('--max-lag-ms', type=float, default=150.0)
    args = ap.parse_args()

    tz_ns, wz = load(args.sequence / 'sources/zed_imu.csv')
    tm_ns, wm = load(args.sequence / 'mav0/imu0/data.csv')
    t0 = min(tz_ns[0], tm_ns[0])
    tz, tm = (tz_ns - t0) * 1e-9, (tm_ns - t0) * 1e-9
    nz, nm = np.linalg.norm(wz, axis=1), np.linalg.norm(wm, axis=1)

    coarse = np.arange(-args.max_lag_ms, args.max_lag_ms + 1e-9, 1.0) * 1e-3
    lag, rho = peak(coarse, correlate(tz, nz, tm, nm, coarse))
    fine = lag + np.arange(-3.0, 3.0001, 0.1) * 1e-3
    lag, rho = peak(fine, correlate(tz, nz, tm, nm, fine))

    windows = []
    for start in np.arange(tz[0], tz[-1] - 60, 60):
        m = (tz >= start) & (tz < start + 60)
        if m.sum() < 1000:
            continue
        lw, rw = peak(coarse, correlate(tz[m], nz[m], tm, nm, coarse))
        windows.append(dict(start_s=round(float(start - tz[0]), 1), offset_ms=round(lw * 1e3, 2), correlation=round(rw, 3)))

    # Rotation between the two gyroscopes, after the time shift, on low-pass rates
    # (vibration above ~10 Hz is not common-mode for two separately mounted IMUs).
    k = 20
    wm_at = np.column_stack([np.interp(tz + lag, tm, smooth(wm[:, i], k)) for i in range(3)])
    wz_s = np.column_stack([smooth(wz[:, i], k) for i in range(3)])
    ok = (tz + lag > tm[0]) & (tz + lag < tm[-1])
    r_est, rssd = Rotation.align_vectors(wz_s[ok], wm_at[ok])         # omega_zedimu = R omega_ms
    t_zedleft_ms, kalibr_shift = chain(args.calibration)
    r_pred = Rotation.from_matrix(R_OPTICAL_ZEDIMU.T @ t_zedleft_ms[:3, :3])
    diff_deg = float(np.degrees((r_est.inv() * r_pred).magnitude()))
    resid = wz_s[ok] - r_est.apply(wm_at[ok])

    report = dict(
        time_offset_s=round(lag, 6), correlation=round(rho, 4),
        convention='offset = t_imu - t_cam for the same instant (camera clock = ZED IMU clock)',
        per_60s_windows=windows,
        window_offset_ms=dict(median=round(float(np.median([w['offset_ms'] for w in windows])), 2) if windows else None,
                              min=min((w['offset_ms'] for w in windows), default=None),
                              max=max((w['offset_ms'] for w in windows), default=None)),
        kalibr_blackfly_timeshift_s=kalibr_shift,
        rotation=dict(estimated_R_zedimu_microstrain=r_est.as_matrix().round(6).tolist(),
                      predicted_from_kalibr_chain_and_nominal_zed_axes=r_pred.as_matrix().round(6).tolist(),
                      angle_between_deg=round(diff_deg, 3),
                      fit_residual_rad_s_rms=round(float(np.sqrt((resid ** 2).sum(1).mean())), 5),
                      excitation_rad_s_rms=round(float(np.sqrt((wm_at[ok] ** 2).sum(1).mean())), 4)),
        T_zedleft_microstrain_kalibr_chain=t_zedleft_ms.round(9).tolist(),
        samples=dict(zed_imu=int(len(tz)), microstrain=int(len(tm))))
    text = json.dumps(report, indent=1)
    print(text)
    if args.json:
        args.json.write_text(text + '\n')


if __name__ == '__main__':
    main()
