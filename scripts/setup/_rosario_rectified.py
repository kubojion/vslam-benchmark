"""Deterministic Rosario Option A geometry; no calibration fitting or GT input."""
import hashlib
from pathlib import Path
import cv2
import numpy as np
import yaml

PROFILE = 'rosario-kalibr-rectified-ruleC-20261006'
SOURCE = 'configs/candidates/rosario-vio-20261002/sources/kalibr-cameras.yaml'
SOURCE_SHA256 = '76b3309c2b9c56989d8e38d9254259ed4834a20c17cfc1f5771623f610370afb'


def geometry(repo):
    raw = (Path(repo) / SOURCE).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError('Rosario calibration source hash mismatch')
    c = yaml.safe_load(raw)
    ks = []
    for i in range(2):
        fx, fy, cx, cy = c[f'cam{i}']['intrinsics']
        ks.append(np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1.]]))
    t = np.array(c['cam1']['T_cn_cnm1'])
    size = tuple(c['cam0']['resolution'])
    r0, r1, p0, p1, q, roi0, roi1 = cv2.stereoRectify(
        ks[0], np.array(c['cam0']['distortion_coeffs']), ks[1], np.array(c['cam1']['distortion_coeffs']),
        size, t[:3, :3], t[:3, 3], flags=cv2.CALIB_ZERO_DISPARITY, alpha=-1)
    poses = []
    for i, r in enumerate((r0, r1)):
        rotate = np.eye(4); rotate[:3, :3] = r.T
        poses.append(np.linalg.inv(np.array(c[f'cam{i}']['T_cam_imu'])) @ rotate)
    return dict(profile=PROFILE, source=SOURCE, source_sha256=SOURCE_SHA256,
                size=list(size), K=p0[:3, :3].tolist(), P=[p0.tolist(), p1.tolist()],
                R=[r0.tolist(), r1.tolist()], T_imu_cam=[x.tolist() for x in poses],
                baseline_m=float(-p1[0, 3]/p1[0, 0]), bf=float(-p1[0, 3]),
                imu_shift_ns=-int(round(c['cam0']['timeshift_cam_imu'] * 1e9)),
                right_minus_left_offset_s=c['cam1']['timeshift_cam_imu']-c['cam0']['timeshift_cam_imu'],
                roi=[list(roi0), list(roi1)], alpha=-1, interpolation='INTER_LINEAR', border='BORDER_CONSTANT_0',
                opencv_version=cv2.__version__)


def maps(repo, g):
    c = yaml.safe_load((Path(repo)/SOURCE).read_text())
    out = []
    for i in range(2):
        fx, fy, cx, cy = c[f'cam{i}']['intrinsics']
        k = np.array([[fx,0,cx],[0,fy,cy],[0,0,1.]])
        out.append(cv2.initUndistortRectifyMap(k, np.array(c[f'cam{i}']['distortion_coeffs']),
            np.array(g['R'][i]), np.array(g['K']), tuple(g['size']), cv2.CV_32FC1))
    return out
