#!/usr/bin/env python3
"""Apply the frozen Rosario/Citrus policy to existing reviewed configs only.

No estimator execution. Preserves unrelated visual settings and historical files.
Rosario geometry is computed from the hash-pinned Kalibr source. Citrus changes
are limited to inertial noise scalars; its visual configs are never regenerated.
"""
import argparse
import json
import re
import sys
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts/run'))
import _imu_noise_rule as rule
from _rosario_rectified import geometry


def scalar(text, key, value, expected=1):
    text, n = re.subn(r'(?m)^(\s*'+re.escape(key)+r':[ \t]*)[^\n]*',
                     lambda m:m[1]+repr(float(value)), text)
    if n != expected:
        raise ValueError((key, n, expected))
    return text


def array(text, key, value, expected=1):
    text, n = re.subn(r'('+re.escape(key)+r':\s*)\[[^\]]*\]',
                     lambda m:m[1]+json.dumps(np.asarray(value).reshape(-1).tolist()), text)
    if n != expected:
        raise ValueError((key,n,expected))
    return text


def cvmatrix(text, key, value):
    pat = r'('+re.escape(key)+r': !!opencv-matrix\n\s+rows: \d+\n\s+cols: \d+\n\s+dt: )[fd](\n\s+data: )\[[^\]]*\]'
    text,n = re.subn(pat,lambda m:m[1]+'d'+m[2]+json.dumps(np.asarray(value).reshape(-1).tolist()),text)
    if n != 1: raise ValueError((key,n))
    return text


def comments(text):
    replacements = {
        'CitrusFarm profile (recording-derived densities, authors Allan random walks)': 'CitrusFarm rule C (published Allan values x estimator EuRoC ratios)',
        'CitrusFarm IMU profile (all estimators): recording-derived densities, authors Allan random walks.': 'CitrusFarm rule C: this estimator uses its own EuRoC ratios.',
        'OpenVINS IMU chain config for Rosario v2 (ZED + integrated IMU, 200 Hz).': 'OpenVINS IMU chain for Rosario v2 (RealSense D435i, 200 Hz).',
        '# Noise values match configs/basalt/rosariov2_calib.json (validated by Basalt\n# and OKVIS2 runs). T_i_b = identity (IMU = body frame).': '# Rule C uses OpenVINS ratios. T_i_b = identity (IMU = body frame).',
        '# Basalt and OKVIS2 runs).': '# Rule C uses Voxel-SVIO ratios.',
        '# Camera model unchanged (authors ORB-SLAM3 profile), time offset 0, IMU noise unchanged.': '# Option A: residual Kalibr rectification, transformed extrinsics, pre-shifted IMU and rule C.',
        '# rotation projected onto SO(3). Decision 2026-10-03: same transform for every algorithm.': '# Rotation composed into the common rectified axes (decision 2026-10-06).',
        '# IMU intrinsics + Tbc: taken verbatim from the same CIFASIS evaluation config.': '# Tbc: full published stereo-IMU Kalibr bundle, composed into rectified axes.',
        '# Derived from the official config: Camera.bf / fx = 32.27032495 / 648.8624169653789': '# Derived from the full Kalibr stereo transform norm; bf = 32.599425851220396.',
    }
    for old,new in replacements.items(): text=text.replace(old,new)
    return text


def write(path,text):
    if path.suffix == '.yaml': text=comments(text)
    if path.read_text()!=text:
        path.write_text(text)
        print(path.relative_to(ROOT))


def noise_configs(dataset):
    mappings = {'orbslam3':dict(zip(('IMU.NoiseGyro','IMU.NoiseAcc','IMU.GyroWalk','IMU.AccWalk'),rule.load()['keys'])),
                'okvis2':dict(zip(('sigma_g_c','sigma_a_c','sigma_gw_c','sigma_aw_c'),rule.load()['keys']))}
    for algo in ('orbslam3','okvis2','okvis2x','airslam','openvins','voxel_svio'):
        if algo=='orbslam3': paths=sorted((ROOT/'configs'/algo).glob(f'{dataset}_stereo_inertial*.yaml'))
        elif algo in ('okvis2','okvis2x'): paths=sorted((ROOT/'configs'/algo).glob(f'{dataset}_*_vio*.yaml'))
        elif algo=='airslam': paths=[ROOT/f'configs/airslam/{dataset}_camera_vio.yaml']
        elif algo=='openvins': paths=[ROOT/f'configs/openvins/{dataset}/kalibr_imu_chain.yaml']
        else: paths=[ROOT/f'configs/voxel_svio/{dataset}.yaml']
        n=rule.noise(algo,dataset)
        mapping=mappings.get('okvis2' if algo=='okvis2x' else algo,{k:k for k in n})
        for path in paths:
            if 'gnss' in path.name: continue
            text=path.read_text()
            for key,quantity in mapping.items(): text=scalar(text,key,n[quantity])
            # Supersede old noise comments without changing unrelated settings.
            text=re.sub(r'(?m)^# (?:IMU: .*Effective recording-noise envelope.*|scripts/analysis/derive_okvis_imu_noise.py; random walks.*|ZED 2 IMU.*|kalibr_imu_chain.yaml and configs/basalt/rosariov2_calib.json.*|#? Basalt and OKVIS2 runs.*)$','',text)
            marker='# IMU noise: rule C, published Allan values x estimator EuRoC ratios (2026-10-06).\n'
            if marker not in text: text=text.replace('%YAML:1.0\n','%YAML:1.0\n'+marker,1) if text.startswith('%YAML:1.0') else marker+text
            write(path,text)
    path=ROOT/f'configs/basalt/{dataset}_calib.json'; value=json.loads(path.read_text());c=value['value0'];n=rule.noise('basalt',dataset)
    for key,quantity in zip(('gyro_noise_std','accel_noise_std','gyro_bias_std','accel_bias_std'),rule.load()['keys']): c[key]=[n[quantity]]*3
    if '_comment_noise' in c:c['_comment_noise']='Rule C: published Allan values x Basalt EuRoC ratios (2026-10-06).'
    write(path,json.dumps(value,indent=4)+'\n')


def rosario():
    g=geometry(ROOT);k=np.array(g['K']);intr=[k[0,0],k[1,1],k[0,2],k[1,2]]
    poses=[np.array(t) for t in g['T_imu_cam']];b=g['baseline_m'];right=np.eye(4);right[0,3]=b
    for path in (ROOT/'configs/orbslam3').glob('rosariov2_stereo*.yaml'):
        text=scalar(path.read_text(),'Stereo.b',b)
        for side in ('LEFT','RIGHT'):
            for name,v in [('K',k),('R',np.eye(3)),('D',np.zeros(5)),('P',g['P'][side=='RIGHT'])]:
                if side+'.'+name+':' in text:text=cvmatrix(text,side+'.'+name,v)
        if 'IMU.T_b_c1:' in text:text=cvmatrix(text,'IMU.T_b_c1',poses[0])
        write(path,text)
    for algo in ('okvis2','okvis2x'):
        for path in (ROOT/'configs'/algo).glob('rosariov2_*.yaml'):
            if 'gnss' in path.name: continue
            text=path.read_text();i=iter(poses)
            text,n=re.subn(r'(T_SC:\s*)\[[^\]]*\]',lambda m:m[1]+json.dumps(next(i).reshape(-1).tolist()),text)
            if n!=2:raise ValueError((path,n))
            write(path,text)
    for path in (ROOT/'configs/airslam').glob('rosariov2_camera*.yaml'):
        text=path.read_text();v=yaml.safe_load(text.replace('%YAML:1.0',''))
        for i,t in enumerate(poses if v['use_imu'] else (np.eye(4),right)):
            v[f'cam{i}'].update(intrinsics=[float(x) for x in intr],T_type=0,T=t.tolist())
        write(path,'%YAML:1.0\n# Rosario Option A: common Kalibr rectified pixels, original resolution; depth cap unchanged.\n'+yaml.safe_dump(v,sort_keys=False,default_flow_style=None))
    path=ROOT/'configs/openvins/rosariov2/kalibr_imucam_chain.yaml';v=yaml.safe_load(path.read_text().replace('%YAML:1.0',''))
    for i,t in enumerate(poses):
        v[f'cam{i}']['T_imu_cam']=t.tolist();v[f'cam{i}']['timeshift_cam_imu']=0.0
    write(path,'%YAML:1.0\n# Rosario Option A; input IMU already on camera clock.\n'+yaml.safe_dump(v,sort_keys=False,default_flow_style=None))
    path=ROOT/'configs/voxel_svio/rosariov2.yaml';text=path.read_text()
    for side,t in zip(('left','right'),poses): text=array(text,'T_imu_cam_'+side,t)
    write(path,text)
    path=ROOT/'configs/basalt/rosariov2_calib.json';v=json.loads(path.read_text())
    for i,t in enumerate(poses):
        v['value0']['T_imu_cam'][i]=dict(zip(('px','py','pz','qx','qy','qz','qw'),[*t[:3,3].tolist(),*Rotation.from_matrix(t[:3,:3]).as_quat().tolist()]))
    v['value0']['cam_time_offset_ns']=0
    write(path,json.dumps(v,indent=4)+'\n')
    for path in (ROOT/'configs/ov2slam').glob('rosariov2_*.yaml'):
        write(path,cvmatrix(path.read_text(),'body_T_cam1',right))
    for path in (ROOT/'configs/macvo').glob('rosariov2_*.yaml'):
        text=scalar(path.read_text(),'bl',b)
        for key,val in zip(('fx','fy','cx','cy'),intr):text=scalar(text,key,val)
        write(path,text)
    # Monocular calibration uses the same virtual K, even though only left pixels are consumed.
    for algo in ('dpvo','droidslam'):
        path=ROOT/f'configs/{algo}/rosariov2.txt'
        write(path,' '.join(repr(float(x)) for x in intr)+'\n')


def sensors(datasets):
    from build_sensor_profiles import orb_profile
    for dataset in datasets:
        path=ROOT/f'configs/sensors/{dataset}.json'
        write(path,json.dumps(orb_profile(ROOT,dataset),indent=2)+'\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dataset',choices=['rosariov2','citrusfarm'],action='append',required=True)
    args=ap.parse_args()
    if 'rosariov2' in args.dataset:rosario()
    for ds in args.dataset:noise_configs(ds)
    sensors(args.dataset)

if __name__=='__main__':main()
