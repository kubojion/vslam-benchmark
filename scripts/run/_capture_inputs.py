#!/usr/bin/env python3
"""Hash prepared sensor/reference bytes without changing or copying the dataset.

The local cache is keyed by resolved path plus device/inode/size/mtime/ctime.
It avoids re-reading identical camera aliases. It is not a dataset backup or
evidence of the inputs used in a historical attempt.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def signature(path):
    s=path.stat()
    return [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns]


class HashCache:
    def __init__(self,repo):
        path=Path(repo)/'results/.cache/input-content.sqlite'
        path.parent.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(path,timeout=120)
        self.db.execute('CREATE TABLE IF NOT EXISTS hashes (path TEXT PRIMARY KEY, signature TEXT, sha256 TEXT)')

    def file(self,path):
        path=path.resolve(strict=True)
        before=signature(path);key=str(path);encoded=json.dumps(before)
        row=self.db.execute('SELECT signature,sha256 FROM hashes WHERE path=?',(key,)).fetchone()
        if row and row[0]==encoded:return row[1],before
        h=hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda:stream.read(2**20),b''):h.update(chunk)
        if signature(path)!=before:raise ValueError('input changed while hashing')
        value=h.hexdigest()
        self.db.execute('INSERT OR REPLACE INTO hashes VALUES (?,?,?)',(key,encoded,value))
        return value,before

    def close(self):
        self.db.commit();self.db.close()


def selection(sequence):
    required=['times.txt','mav0/cam0/data.csv','mav0/cam1/data.csv','mav0/imu0/data.csv']
    paths=set(required)
    for camera in ('cam0','cam1'):
        root=sequence/'mav0'/camera
        data=root/'data'
        if not data.is_dir():raise ValueError('missing prepared camera directory: '+str(data))
        images=[p for p in data.iterdir() if p.suffix.lower() in ('.png','.jpg','.jpeg')]
        if not images:raise ValueError('empty prepared camera directory')
        paths.update(p.relative_to(sequence).as_posix() for p in images)
        if (root/'sensor.yaml').is_file():paths.add(f'mav0/{camera}/sensor.yaml')
    for name in ('imu.csv','gps.csv','gt_tum.txt','segments_auto.csv','manifest.json',
                 'mav0/imu0/sensor.yaml','mav0/body.yaml',
                 'mav0/state_groundtruth_estimate0/data.csv','mav0/state_groundtruth_estimate0/sensor.yaml'):
        if (sequence/name).is_file():paths.add(name)
    aliases={}
    for alias,camera in [('cam0','cam0'),('left','cam0'),('cam1','cam1'),('right','cam1')]:
        p=sequence/alias
        if p.exists() or p.is_symlink():
            if p.resolve()!= (sequence/'mav0'/camera/'data').resolve():
                raise ValueError('camera alias disagrees with prepared sensor directory: '+alias)
            aliases[alias]=f'mav0/{camera}/data'
    return sorted(paths),aliases


def identity(repo,dataset,sequence_name):
    for part in (dataset,sequence_name):
        if not part or Path(part).name!=part or part in ('.','..'):raise ValueError('unsafe sequence identity')
    repo=Path(repo);sequence=repo/'datasets'/dataset/sequence_name
    names,aliases=selection(sequence);entries=[];checks=[];cache=HashCache(repo)
    try:
        for name in names:
            p=sequence/name
            if not p.is_file():raise ValueError('missing prepared input: '+name)
            value,before=cache.file(p)
            entries.append(dict(path=name,sha256=value,size_bytes=before[2]))
            checks.append((p,p.resolve(),before))
        if selection(sequence)!=(names,aliases):raise ValueError('input membership changed during capture')
        for path,resolved,before in checks:
            if path.resolve()!=resolved or signature(path)!=before:raise ValueError('input changed before capture finished')
    finally:cache.close()
    value=dict(schema=1,dataset=dataset,sequence=sequence_name,files=entries,camera_aliases=aliases,
        scope='prepared stereo/IMU/timestamp/default GNSS and reference inputs; custom GNSS copy recorded separately',
        limitations=['content identity is not calibration correctness or reference independence',
                     'no historical input attribution; no copy of large sensor files',
                     'external runtime overrides require a separately reviewed recipe'])
    value['sha256']=digest(value)
    return value


def verify_identity(repo,value,*,check_live=True):
    if value.get('schema')!=1 or digest({k:v for k,v in value.items() if k!='sha256'})!=value.get('sha256'):
        raise ValueError('input identity manifest digest mismatch')
    if check_live and identity(repo,value['dataset'],value['sequence'])!=value:
        raise ValueError('prepared input bytes or file membership changed')


def capture(repo,run):
    repo=Path(repo).resolve();run=Path(run).resolve()
    parts=run.relative_to(repo/'results').parts
    if len(parts)!=5:raise ValueError('unexpected physical attempt path')
    value=identity(repo,parts[1],parts[2]);target=run/'provenance/inputs.json'
    expected=os.environ.get('VSLAM_EXPECTED_INPUT_SHA256')
    if expected and value['sha256']!=expected:raise ValueError('prepared inputs disagree with the reviewed campaign')
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x') as stream:
        json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    if parts[1] == 'rosariov2':
        manifest = repo/'datasets'/parts[1]/parts[2]/'manifest.json'
        if manifest.is_file():
            prepared = json.loads(manifest.read_text())
            if prepared.get('profile') == 'rosario-kalibr-rectified-ruleC-20261006':
                if parts[0] not in ('vo', 'vio', 'vo-lc', 'vio-lc'):
                    raise ValueError('Rosario Option A is not approved for GNSS recipes')
                profile = dict(schema=1, profile=prepared['profile'], geometry=prepared['geometry'],
                               input_sha256=value['sha256'],
                               manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest())
                with (run/'provenance/rosario-input-profile.json').open('x') as stream:
                    json.dump(profile,stream,indent=2);stream.write('\n')
    return value


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',required=True,type=Path);ap.add_argument('--run',required=True,type=Path)
    args=ap.parse_args();value=capture(args.repo,args.run)
    print(json.dumps(dict(input_capture=True,files=len(value['files']),sha256=value['sha256'])))


if __name__=='__main__':main()
