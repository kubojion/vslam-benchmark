#!/usr/bin/env python3
"""Materialise and optionally select Rosario Option A. Never starts an estimator.

Original inputs are retained under .profiles/original-20261006 on activation.
Canonical sequence directories and tracked reference/timing files stay in place. New data and every source/derived hash live in a separate version.
Canonical aliases are relative so existing /datasets container mounts still work.
"""
import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

import cv2
import numpy as np
import yaml
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/setup'))
from _rosario_rectified import geometry, maps, PROFILE


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()


def shifted(raw, shift):
    lines=raw.splitlines(keepends=True);out=[];previous=None
    for line in lines:
        if line.startswith(b'#') or not line.strip():out.append(line);continue
        stamp,rest=line.split(b',',1);n=int(stamp)+shift
        if previous is not None and n<=previous:raise ValueError('nonmonotonic IMU')
        previous=n;out.append(str(n).encode()+b','+rest)
    return b''.join(out)


def prepare(base,seq):
    g=geometry(ROOT);source=base/seq
    out=base/'.profiles'/PROFILE/seq
    if source.is_symlink() or out.exists():raise ValueError('already prepared or selected; refusing double application')
    if shutil.disk_usage(base).free < 60*2**30:raise ValueError('less than 60 GiB free')
    rows={}
    for i in range(2):
        rows[i]=[r for r in csv.reader((source/f'mav0/cam{i}/data.csv').open()) if r and not r[0].startswith('#')]
    if [r[0] for r in rows[0]]!=[r[0] for r in rows[1]]:raise ValueError('stereo timestamps differ')
    out.mkdir(parents=True);evidence=[]
    # Copy supporting files without modifying them; no symlinks back through the
    # canonical path, which will point to this derived directory after activation.
    for p in source.rglob('*'):
        rel=p.relative_to(source)
        if p.is_symlink() or not p.is_file() or '/data/' in str(rel) or p.suffix=='.g2o':continue
        dst=out/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
        evidence.append(dict(path=str(rel),source_sha256=sha(p),derived_sha256=sha(dst)))
    cv2.setNumThreads(1);rectmaps=maps(ROOT,g)
    def image_job(item):
        i,row=item;rel=f'mav0/cam{i}/data/{row[1].strip()}';p=source/rel;dst=out/rel
        raw=p.read_bytes();im=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_UNCHANGED)
        if im is None or list(im.shape[:2])!=[720,1280]:raise ValueError('invalid input image: '+str(p))
        result=cv2.remap(im,*rectmaps[i],cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
        if not cv2.imwrite(str(dst),result,[cv2.IMWRITE_PNG_COMPRESSION,3]):raise ValueError('PNG write failed')
        return dict(path=rel,source_sha256=hashlib.sha256(raw).hexdigest(),derived_sha256=sha(dst))
    for i in range(2):(out/f'mav0/cam{i}/data').mkdir(parents=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for j,e in enumerate(pool.map(image_job,((i,row) for i in range(2) for row in rows[i]))):
            evidence.append(e)
            if j%2000==0:print(seq,'images',j,flush=True)
    imu=out/'mav0/imu0/data.csv';imu.write_bytes(shifted((source/'mav0/imu0/data.csv').read_bytes(),g['imu_shift_ns']))
    # Alternate CSV is rebuilt from the same integer timestamps and exact value
    # strings, avoiding the legacy float-second rounding difference.
    with (out/'imu.csv').open('w') as f:
        f.write('t,ax,ay,az,gx,gy,gz\n')
        for row in csv.reader(imu.open()):
            if not row or row[0].startswith('#'):continue
            stamp=int(row[0]);sec,ns=divmod(stamp,10**9)
            f.write(f'{sec}.{ns:09d},'+','.join(row[4:7]+row[1:4])+'\n')
    for e in evidence:
        if e['path'] in ('imu.csv','mav0/imu0/data.csv'):e['derived_sha256']=sha(out/e['path'])
    for alias,target in [('cam0','mav0/cam0/data'),('cam1','mav0/cam1/data'),('left','cam0'),('right','cam1')]:
        (out/alias).symlink_to(target,target_is_directory=True)
    record=dict(schema=1,dataset='rosariov2',sequence=seq,profile=PROFILE,geometry=g,
                source_directory=f'.profiles/original-20261006/{seq}',
                source_directory_before_activation=seq,frames=len(rows[0]),files=sorted(evidence,key=lambda x:x['path']),
                evaluation_target='original_left_camera_axes',native_fixed_time_offset_ns=0,
                start_policy='No fabricated IMU; each inertial loader must reject unsupported initial frames; native verification pending.',
                scope='VO,VIO,VO-LC,VIO-LC only; GNSS recipes remain on original inputs')
    (out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
    print('prepared',out,flush=True)


def verify(base,seq):
    out=base/'.profiles'/PROFILE/seq;v=json.loads((out/'manifest.json').read_text())
    if v['profile']!=PROFILE or v['geometry']!=geometry(ROOT):raise ValueError('geometry identity changed')
    src=base/v['source_directory']
    if not src.exists():src=base/seq
    if src.is_symlink():raise ValueError('original input unavailable')
    for e in v['files']:
        if sha(src/e['path'])!=e['source_sha256'] or sha(out/e['path'])!=e['derived_sha256']:
            raise ValueError('input hash mismatch: '+e['path'])
    if (out/'mav0/imu0/data.csv').read_bytes()!=shifted((src/'mav0/imu0/data.csv').read_bytes(),v['geometry']['imu_shift_ns']):
        raise ValueError('IMU shift not exact')
    for alias,cam in [('cam0',0),('left',0),('cam1',1),('right',1)]:
        if (out/alias).resolve()!=(out/f'mav0/cam{cam}/data').resolve():raise ValueError('alias mismatch')
    print('verified',seq,len(v['files']),'files',flush=True)


def activate(base,seq):
    verify(base,seq)
    source=base/seq;backup=base/'.profiles/original-20261006'/seq
    out=base/'.profiles'/PROFILE/seq
    if (source/'manifest.json').exists() or backup.exists():raise ValueError('already activated')
    backup.mkdir(parents=True)
    # Keep the complete original layout, including aliases, without moving the
    # tracked references or timing files at their canonical locations.
    for p in source.rglob('*'):
        rel=p.relative_to(source)
        if p.is_symlink() or not p.is_file() or '/data/' in str(rel) or p.suffix=='.g2o':continue
        dst=backup/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
    for i in range(2):
        rel=Path(f'mav0/cam{i}/data');old=source/rel;dst=backup/rel
        dst.parent.mkdir(parents=True,exist_ok=True);old.rename(dst)
        old.symlink_to(os.path.relpath(out/rel,old.parent),target_is_directory=True)
    for rel in ('mav0/imu0/data.csv','imu.csv'):
        dst=source/rel
        # Original bytes were copied and hashed above; atomic replacement with a
        # relative link makes every consumer select the same prepared IMU.
        temp=dst.with_name(dst.name+'.option-a-link')
        temp.symlink_to(os.path.relpath(out/rel,dst.parent));os.replace(temp,dst)
    for alias,target in [('cam0','mav0/cam0/data'),('cam1','mav0/cam1/data'),('left','cam0'),('right','cam1')]:
        (backup/alias).symlink_to(target,target_is_directory=True)
    (source/'manifest.json').symlink_to(os.path.relpath(out/'manifest.json',source))
    verify(base,seq)
    print('selected',source,'original retained at',backup,flush=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('command',choices=['prepare','verify','activate'])
    ap.add_argument('--sequence',choices=['sequence1','sequence5'],action='append',required=True)
    a=ap.parse_args();base=ROOT/'datasets/rosariov2'
    for seq in a.sequence:globals()[a.command](base,seq)
if __name__=='__main__':main()
