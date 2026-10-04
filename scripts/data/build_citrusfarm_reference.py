#!/usr/bin/env python3
"""Build an immutable CitrusFarm camera-position reference from the authors' RTK track.

The authors' gt.csv gives the GNSS antenna position only (single receiver, RTK fixed
throughout, 10 Hz host stamps). The benchmark compares positions of the left camera, so
each antenna position is moved by the calibrated antenna-to-camera lever arm:

  lever    from the authors' calibration chain (configs/sensors/sources/citrusfarm):
           base_link -> LiDAR and LiDAR -> antenna (CAD), LiDAR -> Blackfly (ACFR),
           Blackfly -> ZED left (Kalibr multi-camera). About 0.43 m horizontal, 0.31 m vertical.
  heading  direction of travel from the antenna track itself (chord over +-0.5 m of path);
           the robot drives forward only (wheel odometry: no reversing, no turns on the spot).
  attitude level platform (no roll or pitch is available from one antenna).

Samples where the chord cannot be formed within 3 s (the robot standing at start and end)
have no heading and are left out of the support. No estimator output, image, or fitted
time correction enters the construction; the authors' timestamps are kept as recorded.
Run once per sequence; an existing version is never overwritten.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import yaml
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[2]
CALIBRATION = ROOT / 'configs/sensors/sources/citrusfarm'
VERSION = 'rtk-position-v1-20261003'
CHORD_M = 0.5
CHORD_MAX_S = 3.0


def evidence(path):
    p = Path(path).resolve()
    return dict(path=str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
                sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def numbers(path, key):
    """'x, y, z' style values after a line starting with `key` in the authors' result files."""
    for line in Path(path).read_text().splitlines():
        if line.replace(' ', '').startswith(key.replace(' ', '')):
            return [float(v) for v in line.split('=', 1)[1].split(',')]
    raise ValueError(f'{key} not found in {path}')


def lever_arm():
    """Antenna position minus left-camera position, in base_link axes (x forward, y left, z up)."""
    def pose(rotation, translation):
        t = np.eye(4)
        t[:3, :3] = rotation
        t[:3, 3] = translation
        return t
    base_lidar = pose(np.eye(3), numbers(CALIBRATION / '05-baselink-lidar-result.txt', 'x, y, z, qx')[:3])
    if numbers(CALIBRATION / '05-baselink-lidar-result.txt', 'x, y, z, qx')[3:] != [0.0, 0.0, 0.0, 1.0]:
        raise ValueError('base_link -> LiDAR rotation is expected to be identity')
    xyzq = numbers(CALIBRATION / '03-lidar-cam-result.txt', 'x, y, z, qx')
    lidar_blackfly = pose(Rotation.from_quat(xyzq[3:]).as_matrix(), xyzq[:3])
    multi = yaml.safe_load((CALIBRATION / '01-multi-cam-result.yaml').read_text())
    if multi['cam1']['rostopic'] != '/zed2i/zed_node/left/image_rect_color':
        raise ValueError('multi-camera cam1 is not the rectified ZED left image')
    zedleft_blackfly = np.array(multi['cam1']['T_cn_cnm1'], dtype=float)   # Kalibr chain: T_cam1_cam0
    base_zedleft = base_lidar @ lidar_blackfly @ np.linalg.inv(zedleft_blackfly)
    antenna = base_lidar @ np.r_[numbers(CALIBRATION / '04-lidar-gps-result.txt', 'x, y, z'), 1.0]
    return antenna[:3] - base_zedleft[:3, 3], base_zedleft


def chord_heading(t, xy):
    """Heading of travel at each sample from the positions CHORD_M before and after it."""
    s = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(xy, axis=0), axis=1))]
    heading = np.full(len(t), np.nan)
    ok = (s - CHORD_M >= 0) & (s + CHORD_M <= s[-1])
    a = np.column_stack([np.interp(s[ok] - CHORD_M, s, xy[:, i]) for i in range(2)])
    b = np.column_stack([np.interp(s[ok] + CHORD_M, s, xy[:, i]) for i in range(2)])
    span = np.interp(s[ok] + CHORD_M, s, t) - np.interp(s[ok] - CHORD_M, s, t)
    h = np.arctan2(b[:, 1] - a[:, 1], b[:, 0] - a[:, 0])
    h[span > CHORD_MAX_S] = np.nan
    heading[ok] = h
    return heading


def retained_intervals(times, keep, maximum_gap_s=0.5):
    selected = np.flatnonzero(keep)
    split = np.flatnonzero((np.diff(selected) != 1) | (np.diff(times[selected]) > maximum_gap_s)) + 1
    return [[float(times[a[0]]), float(times[a[-1]])] for a in np.split(selected, split)]


def build(sequence):
    ds = ROOT / 'datasets/citrusfarm' / sequence
    manifest = json.loads((ds / 'manifest.json').read_text())
    gt_path = ds / 'gt_antenna_tum.txt'
    gt = np.loadtxt(gt_path)
    times, antenna = gt[:, 0], gt[:, 1:4]
    if np.any(np.diff(times) <= 0):
        raise ValueError('reference timestamps must increase')
    lever, base_zedleft = lever_arm()
    heading = chord_heading(times, antenna[:, :2])
    keep = np.isfinite(heading)
    c, s = np.cos(heading[keep]), np.sin(heading[keep])
    camera = antenna[keep].copy()
    camera[:, 0] -= c * lever[0] - s * lever[1]
    camera[:, 1] -= s * lever[0] + c * lever[1]
    camera[:, 2] -= lever[2]

    out = ds / 'references' / VERSION
    if out.exists():
        raise FileExistsError(f'preserve existing reference version: {out}')
    out.mkdir(parents=True)
    poses = np.c_[times[keep], camera, np.zeros((int(keep.sum()), 3)), np.ones(int(keep.sum()))]
    trajectory = out / 'primary.tum'
    np.savetxt(trajectory, poses, fmt='%.9f')
    support = out / 'primary-support.json'
    support.write_text(json.dumps(dict(valid_intervals=retained_intervals(times, keep)), indent=2) + '\n')
    np.savez_compressed(out / 'construction.npz', times=times, antenna=antenna, heading=heading, keep=keep,
                        lever_base=lever, base_from_zed_left=base_zedleft)
    stamps = np.diff(times)
    result = dict(
        schema=1, version=VERSION, dataset='citrusfarm', sequence=sequence,
        source_sequence=manifest['source_sequence'], orientation_valid=False, nominal_geometry=True,
        point='ZED2i left camera (rectified optical centre)',
        lever_antenna_minus_camera_base_m=lever.round(6).tolist(),
        heading=f'direction of travel of the antenna track, chord over +-{CHORD_M} m of path (max {CHORD_MAX_S} s); '
                'forward-only driving checked on the wheel odometry',
        attitude='level platform assumed (single antenna)', clock_offset_s=0.0,
        retained_samples=int(keep.sum()), total_samples=int(len(times)),
        authors_timestamp_spacing_s=dict(median=float(np.median(stamps)), min=float(stamps.min()), max=float(stamps.max())),
        limitations=['position-only reference; identity quaternions are placeholders',
                     'single-antenna heading from the path and a level platform: lever errors of a few centimetres '
                     'at 0.43 m horizontal lever, mostly in turns and with roll/pitch rocking',
                     'authors timestamps are host arrival times at 10 Hz (spacing 0.01-0.19 s); no time '
                     'correction fitted, so a few centimetres of along-track error remain',
                     'lever arm combines CAD values (antenna, base_link) with calibrated LiDAR-camera and '
                     'camera-camera transforms; no surveyed mounting covariance'],
        evidence=[evidence(p) for p in (gt_path, ds / 'manifest.json', Path(__file__),
                                        *sorted(CALIBRATION.glob('0*')), CALIBRATION / 'index.json')],
        variants=dict(primary=dict(trajectory=evidence(trajectory), support=evidence(support),
                                   retained_samples=int(keep.sum()))),
        construction=evidence(out / 'construction.npz'))
    (out / 'reference.json').write_text(json.dumps(result, indent=2) + '\n')
    # Plot and segment tools read gt_tum.txt / gt_interp_tum.txt; both are this reference
    # (the evaluator itself uses the hash-bound selector below).
    np.savetxt(ds / 'gt_tum.txt', poses, fmt='%.9f')
    image_s = np.array([int(v) for v in (ds / 'times.txt').read_text().split()]) * 1e-9
    inside = np.zeros(len(image_s), dtype=bool)
    for a, b in json.loads(support.read_text())['valid_intervals']:
        inside |= (image_s >= a) & (image_s <= b)
    at_images = np.column_stack([image_s[inside]] + [np.interp(image_s[inside], poses[:, 0], poses[:, i])
                                                      for i in (1, 2, 3)])
    np.savetxt(ds / 'gt_interp_tum.txt', np.c_[at_images, np.zeros((len(at_images), 3)), np.ones(len(at_images))],
               fmt='%.9f')
    selector = ROOT / 'configs/references' / f'citrusfarm_{sequence}.json'
    selector.write_text(json.dumps(dict(schema=1, dataset='citrusfarm', sequence=sequence, variant='primary',
                                        reference=evidence(out / 'reference.json')), indent=2) + '\n')
    print(json.dumps(dict(reference=str(out.relative_to(ROOT)), retained=int(keep.sum()), of=int(len(times)),
                          lever=lever.round(4).tolist()), indent=1))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('sequence', help='benchmark sequence name, e.g. seq04')
    build(ap.parse_args().sequence)
