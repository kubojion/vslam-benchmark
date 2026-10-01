#!/usr/bin/env python3
"""Update existing matrix cells in place without changing tables, headers or order."""
import json
from pathlib import Path
import re

REPO=Path(__file__).resolve().parents[2]
NAMES={'ORB-SLAM3':'orbslam3','Basalt':'basalt','MAC-VO':'macvo','AirSLAM':'airslam','DPVO':'dpvo','DPV-SLAM':'dpvo','OKVIS2':'okvis2','OKVIS2-X':'okvis2x','OV2SLAM':'ov2slam','OpenVINS':'openvins','Voxel-SVIO':'voxel_svio','CIFASIS GNSS-SI':'cifasis_gnss_si','RTAB-Map':'rtabmap_gps','VINS-Fusion':'vins_fusion_gps','OpenVINS+GPS':'openvins_gps','OKVIS2-X (tight)':'okvis2x'}
SEQUENCES=[('rosariov2','sequence1'),('rosariov2','sequence5'),('hortimulti','strawberry02'),('hortimulti','strawberry03'),('euroc_mav','MH_01_easy'),('euroc_mav','MH_03_medium'),('euroc_mav','MH_05_difficult'),('zed2i','field1_110426_full_10fps_q90')]


def render_cell(cell):
    mode,algo,ds=cell['run_type'],cell['algorithm'],cell['dataset']
    n=cell['evaluated'];flags=[]
    failed=[i+1 for i,a in enumerate(cell['attempts']) if a['numerical_status']=='scale_collapse']
    if failed:flags.append('collapse '+','.join(f'r{i}' for i in failed))
    findings={f['code'] for a in cell['attempts'] for f in a.get('confirmed_protocol_findings',[])}
    if 'airslam_rectified_camera_imu_extrinsic' in findings:flags.append('rerun: rectified IMU')
    if any(a['numerical_status']=='eval_failed' for a in cell['attempts']):flags.append('invalid trajectory')
    if mode=='gnss-vio':flags.append('legacy; provenance')
    elif algo=='orbslam3' and ds=='zed2i' and mode in ('vo','vo-lc'):flags.append('rerun: FPS')
    elif ds=='zed2i' and mode in ('vio','vio-lc'):flags.append('IMU review')
    elif algo=='airslam':flags.append('sparse; review')
    elif ds in ('rosariov2','hortimulti'):flags.append('reference review')
    else:flags.append('review')
    nonzero={a['process'].get('exit_code') for a in cell['attempts'] if a['evaluated'] and a['process'].get('exit_code') not in (0,None)}
    if nonzero:flags.append('exit '+','.join(map(str,sorted(nonzero))))
    if n<3:flags.append('+'+str(3-n))
    return '🟡 N='+str(n)+'; '+'; '.join(flags)


def update(text,inventory):
    cells={(c['run_type'],c['algorithm'],c['dataset'],c['sequence']):c for c in inventory['cells']}
    mode=None;out=[];seen=set()
    for line in text.splitlines():
        if line.startswith('## '):mode=None
        match=re.match(r'### .*`results/([^/]+)/`',line)
        if match:mode=match[1];seen.add(mode)
        if mode and line.startswith('| '):
            parts=line.split('|');algo=NAMES.get(parts[1].strip())
            if algo:
                sequences=SEQUENCES[:4] if mode=='gnss-vio' else SEQUENCES
                if len(parts)!=len(sequences)+3:raise ValueError('unexpected TODO matrix column layout')
                for i,(ds,seq) in enumerate(sequences,2):
                    cell=cells[(mode,algo,ds,seq)]
                    if cell['evaluated']:parts[i]=' '+render_cell(cell)+' '
                line='|'.join(parts)
        out.append(line)
    if seen!={'vo','vo-lc','vio','vio-lc','gnss-vio'}:raise ValueError('missing one or more existing mode matrices')
    return '\n'.join(out)+'\n'


if __name__=='__main__':
    path=REPO/'TODO.md'
    inventory=json.loads((REPO/'results/repair-20261001/inventory.json').read_text())
    path.write_text(update(path.read_text(),inventory))
