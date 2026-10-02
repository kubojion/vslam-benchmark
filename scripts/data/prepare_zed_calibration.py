#!/usr/bin/env python3
"""Derive the July ZED calibration from the preserved serial SDK export.

Default is read-only validation; --apply updates only the reviewed extrinsics.
T_A_B maps coordinates in B into A. SDK IMAGE uses right/down/forward; recorded
zed_imu_link uses forward/left/up. See docs/zed-preparation-20261002.md.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts/eval'))
from _pose_frames import matrix, read_yaml

SDK = ROOT/'docs/campaigns/zed-sdk-calibration-20261002.json'
MANIFEST = ROOT/'datasets/zed2i/field1_110426_full_10fps_q90/manifest.json'
DERIVED = ROOT/'docs/campaigns/zed-physical-calibration-20261002.json'


def derive(sdk, recording):
    if (sdk['serial_number'] != 30291010 or sdk['coordinate_system'] != 'IMAGE'
            or sdk['translation_units'] != 'metres'):
        raise ValueError('unexpected serial, coordinate system or units')
    raw = matrix(sdk['camera_imu_transform_4x4'])
    camera_T_imu = raw.copy()
    # SDK exports float32 rotations. Project only their rounding residual onto SO(3).
    camera_T_imu[:3, :3] = Rotation.from_matrix(raw[:3, :3]).as_matrix()
    if np.max(np.abs(camera_T_imu - raw)) > 1e-6:
        raise ValueError('SDK matrix needs more than float32 rounding normalization')
    ros_T_image = np.eye(4)
    ros_T_image[:3, :3] = [[0, 0, 1], [-1, 0, 0], [0, -1, 0]]
    imu_T_left = ros_T_image @ np.linalg.inv(camera_T_imu)
    info = recording['camera_info']['right']
    # July recording projection controls stereo geometry, not today's SDK mode.
    baseline = -float(info['p'][3]) / float(info['p'][0])
    left_T_right = np.eye(4); left_T_right[0, 3] = baseline
    return dict(schema=1, serial_number=30291010, dataset='zed2i',
        sequences=['field1_110426_full_10fps_q90'],
        convention='T_A_B maps B coordinates into A; metres; ROS IMU and rectified optical cameras',
        derivation='T_imu_left = Q_IMAGE_to_ROS @ inverse(T_left_imu_SDK_IMAGE); T_imu_right = T_imu_left @ Tx(recorded_baseline)',
        Q_IMAGE_to_ROS=ros_T_image.tolist(), T_left_imu_SDK_IMAGE=camera_T_imu.tolist(),
        T_imu_left=imu_T_left.tolist(), T_imu_right=(imu_T_left@left_T_right).tolist(),
        recorded_baseline_m=baseline,
        sdk_rounding_normalization_max_abs=float(np.max(np.abs(camera_T_imu-raw))),
        residual_rotation_deg=float(Rotation.from_matrix(camera_T_imu[:3,:3]).magnitude()*180/np.pi),
        image_calibration_policy='retain July 3 recording CameraInfo; already rectified; no raw-stereo rectification applied',
        imu_time_shift_s=0.0,
        limitations=['factory export recovered October 2 for the same serial; no historical calibration change reported',
                     'hardware-synchronised camera/IMU; field camera-versus-RTK clock offset remains unknown'])


def configurations():
    return {
        'orb': ['configs/orbslam3/zed2i_field1_110426_full_10fps_q90_stereo_inertial.yaml'],
        'okvis': ['configs/okvis2/zed2i_field1_110426_full_10fps_q90_vio.yaml',
                  'configs/okvis2x/zed2i_field1_110426_full_10fps_q90_vio.yaml',
                  'configs/okvis2x/zed2i_field1_110426_full_10fps_q90_vio_lc.yaml'],
        'basalt': ['configs/basalt/zed2i_calib.json'],
        'air': ['configs/airslam/zed2i_camera_vio.yaml'],
        'open': ['configs/openvins/zed2i/kalibr_imucam_chain.yaml'],
        'voxel': ['configs/voxel_svio/zed2i.yaml'],
    }


def extrinsics_and_other(config, kind):
    cfg=copy.deepcopy(config)
    if kind=='orb': ts=[cfg.pop('IMU.T_b_c1')]
    elif kind=='okvis': ts=[c.pop('T_SC') for c in cfg['cameras']]
    elif kind=='basalt':
        entries=cfg['value0'].pop('T_imu_cam'); ts=[]
        cfg['value0'].pop('_comment_extrinsic',None)
        for c in entries:
            t=np.eye(4);t[:3,:3]=Rotation.from_quat([c[k] for k in ('qx','qy','qz','qw')]).as_matrix()
            t[:3,3]=[c[k] for k in ('px','py','pz')];ts.append(t)
    elif kind in ('air','open'): ts=[cfg[f'cam{i}'].pop('T' if kind=='air' else 'T_imu_cam') for i in (0,1)]
    elif kind=='voxel': ts=[cfg['camera_parameter'].pop(f'T_imu_cam_{side}') for side in ('left','right')]
    else: raise ValueError(kind)
    return [matrix(t) for t in ts],cfg


def replacement(text, kind, ts):
    flat=lambda t:'['+',\n          '.join(', '.join(f'{v:.15g}' for v in row) for row in t)+']'
    if kind=='orb':
        text,n=re.subn(r'(IMU\.T_b_c1:[\s\S]*?data:\s*)\[[^\]]+\]',lambda m:m[1]+flat(ts[0]),text)
        assert n==1
    elif kind=='okvis':
        values=iter(ts)
        text,n=re.subn(r'(T_SC:\s*)\[[^\]]+\]',lambda m:m[1]+flat(next(values)),text);assert n==2
    elif kind=='voxel':
        for side,t in zip(('left','right'),ts):
            text,n=re.subn(r'(T_imu_cam_'+side+r':\s*)\[[^\]]+\]',lambda m:m[1]+flat(t),text);assert n==1
    elif kind in ('air','open'):
        key='T' if kind=='air' else 'T_imu_cam';values=iter(ts)
        def rows(m):
            indent=m[2];return m[1]+''.join(indent+'- ['+', '.join(f'{v:.15g}' for v in row)+']\n' for row in next(values))
        text,n=re.subn(r'(^  '+key+r':\n)( +)- \[[^\n]+\]\n(?: +- \[[^\n]+\]\n){3}',rows,text,flags=re.M);assert n==2
    elif kind=='basalt':
        cfg=json.loads(text);cfg['value0']['T_imu_cam']=[]
        for t in ts:
            vals=[*t[:3,3],*Rotation.from_matrix(t[:3,:3]).as_quat()]
            cfg['value0']['T_imu_cam'].append(dict(zip(('px','py','pz','qx','qy','qz','qw'),map(float,vals))))
        cfg['value0']['_comment_extrinsic']='Recovered SN30291010 factory transform, SDK IMAGE -> recorded ROS IMU axes; see docs/zed-preparation-20261002.md. July CameraInfo retained.'
        return json.dumps(cfg,indent=4)+'\n'
    # Remove obsolete identity-residual statements only; keep parameter comments.
    text=re.sub(r'^# The serial-specific residual rotation[^\n]*\n# retained in the bag; identity[^\n]*\n','',text,flags=re.M)
    if '# Recovered factory rotation' not in text:
        marker='# Recovered factory rotation: docs/campaigns/zed-physical-calibration-20261002.json.\n'
        text=text.replace('%YAML:1.0\n','%YAML:1.0\n'+marker,1) if text.startswith('%YAML:') else marker+text
    return text


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    value=derive(json.loads(SDK.read_text()),json.loads(MANIFEST.read_text()))
    value['evidence']=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (SDK,MANIFEST)]
    ts=[np.array(value[k]) for k in ('T_imu_left','T_imu_right')]
    for kind,paths in configurations().items():
        for relative in paths:
            p=ROOT/relative;before=json.loads(p.read_text()) if kind=='basalt' else read_yaml(p)
            if args.apply:
                updated=replacement(p.read_text(),kind,ts);p.write_text(updated)
            after=json.loads(p.read_text()) if kind=='basalt' else read_yaml(p)
            actual,other=extrinsics_and_other(after,kind)
            if other!=extrinsics_and_other(before,kind)[1]:raise ValueError('unexpected non-extrinsic change: '+relative)
            for a,t in zip(actual,ts):np.testing.assert_allclose(a,t,atol=1e-12,rtol=0)
            print('verified',relative)
    if args.apply: DERIVED.write_text(json.dumps(value,indent=2)+'\n')
    elif json.loads(DERIVED.read_text())!=value:raise ValueError('derived calibration record is stale')
    print('seven algorithm families; eight files; July image and IMU noise/timing settings retained')


if __name__=='__main__':main()
