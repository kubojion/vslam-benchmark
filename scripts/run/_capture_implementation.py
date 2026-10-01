#!/usr/bin/env python3
"""Preserve exact checkout bytes before estimation, including nested dirty sources.

Private content-addressed blobs are outside the browsable per-run artifact tree.
This captures the current checkout, not proof that a native binary was built from
it. Ignored models/build outputs require their own runtime artifact identities.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import time

SOURCES = {
    'orbslam3':'ORB_SLAM3', 'okvis2':'okvis2', 'okvis2x':'okvis2x',
    'airslam':'airslam', 'ov2slam':'ov2slam', 'openvins':'open_vins',
    'openvins_gps':'open_vins', 'voxel_svio':'voxel_svio', 'dpvo':'DPVO',
    'macvo':'MAC-VO', 'cifasis_gnss_si':'cifasis_gnss_si', 'vins_fusion_gps':'VINS-Fusion',
    'basalt':None, 'rtabmap_gps':None,
}


def git(path, *args):
    result = subprocess.run(['git','-C',str(path),*args],capture_output=True,check=True,timeout=60)
    return result.stdout


def signature(path):
    s = path.lstat()
    return [s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns]


def digest_file(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(2**20),b''): h.update(chunk)
    return h.hexdigest()


def safe_relative(value):
    path=Path(value)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('unsafe capture path')
    return path


def inventory_tree(path, scope=()):
    """Gitlinks remain explicit even when their worktrees are unavailable."""
    command=['ls-files','--stage','-z']+(['--',*scope] if scope else [])
    tracked={}
    for record in git(path,*command).split(b'\0'):
        if not record: continue
        header,name=record.split(b'\t',1)
        mode,oid,stage=header.decode().split()
        if stage!='0': raise ValueError('unmerged source index prevents coherent capture')
        tracked[os.fsdecode(name)]=dict(git_mode=mode,index_object=oid,tracked=True)
    command=['ls-files','--others','--exclude-standard','-z']+(['--',*scope] if scope else [])
    for name in git(path,*command).split(b'\0'):
        if name: tracked[os.fsdecode(name)]=dict(tracked=False)
    return tracked


def store_file(path, store, before):
    store.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.capture-',dir=store)
    try:
        h=hashlib.sha256();size=0
        with os.fdopen(fd,'wb') as output:
            if stat.S_ISLNK(before[2]):
                raw=os.fsencode(os.readlink(path));h.update(raw);output.write(raw);size=len(raw)
            elif stat.S_ISREG(before[2]):
                with path.open('rb') as source:
                    for chunk in iter(lambda:source.read(2**20),b''):
                        h.update(chunk);output.write(chunk);size+=len(chunk)
            else: raise ValueError('unsupported non-file source entry')
            output.flush();os.fsync(output.fileno())
        if signature(path)!=before: raise ValueError('source changed during capture')
        digest=h.hexdigest();target=store/digest
        try: os.link(name,target)  # publish once; never overwrite an existing blob
        except FileExistsError: pass
        if target.is_symlink() or not target.is_file() or target.stat().st_size!=size or digest_file(target)!=digest:
            raise ValueError('implementation archive blob mismatch')
        return digest,size
    finally:
        if os.path.exists(name):os.unlink(name)


def capture_tree(repo,path,store,*,scope=(),seen=None):
    seen=seen if seen is not None else set()
    real=path.resolve()
    if real in seen: raise ValueError('recursive source checkout')
    seen.add(real)
    commit=git(path,'rev-parse','HEAD').decode().strip()
    entries=inventory_tree(path,scope);records=[];signatures={}
    for name,info in sorted(entries.items()):
        relative=safe_relative(name);source=path/relative
        record=dict(path=name,**info)
        if info.get('git_mode')=='160000':
            if source.is_dir() and (source/'.git').exists():
                record.update(kind='gitlink',checkout=capture_tree(repo,source,store,seen=seen))
            else:record.update(kind='gitlink',checkout=None,limitation='submodule_worktree_unavailable')
        elif not source.exists() and not source.is_symlink():
            record['kind']='absent_tracked_file'
            signatures[name]=None
        else:
            before=signature(source);digest,size=store_file(source,store,before)
            record.update(kind='symlink' if stat.S_ISLNK(before[2]) else 'file',sha256=digest,size_bytes=size,
                          mode=stat.S_IMODE(before[2]))
            signatures[name]=before
        records.append(record)
    if git(path,'rev-parse','HEAD').decode().strip()!=commit or inventory_tree(path,scope)!=entries:
        raise ValueError('source index or revision changed during capture')
    for name,before in signatures.items():
        source=path/name
        if before is None:
            if source.exists() or source.is_symlink():raise ValueError('deleted source reappeared during capture')
        elif signature(source)!=before:raise ValueError('source changed before snapshot completion')
    seen.remove(real)
    return dict(path=path.relative_to(repo).as_posix(),commit=commit,scope=list(scope),entries=records,
                current_checkout_only_not_binary_build_proof=True)


def capture(repo,run,algorithm):
    repo=Path(repo).resolve();run=Path(run).resolve()
    if algorithm not in SOURCES:raise ValueError('algorithm is outside the reviewed capture registry')
    if (repo/'results') not in run.parents:raise ValueError('capture requires a result attempt path')
    target=run/'provenance/implementation.json'
    if target.exists():raise ValueError('implementation capture already exists; never replace it')
    started=time.monotonic();store=repo/'results/.implementation-blobs/sha256'
    trees=[dict(role='workspace',**capture_tree(repo,repo,store,scope=('scripts','configs','.gitmodules')))]
    if SOURCES[algorithm]:
        trees.append(dict(role='algorithm',**capture_tree(repo,repo/'src'/SOURCES[algorithm],store)))
    value=dict(schema=1,captured_at=datetime.now(timezone.utc).isoformat(),phase='before_estimation',
        blob_store=store.relative_to(repo).as_posix(),trees=trees,elapsed_s=time.monotonic()-started,
        limitations=['ignored_build_model_and_environment_files_require_separate_runtime_identity',
                     'captured_checkout_is_not_proof_of_native_binary_source_linkage'])
    expected=os.environ.get('VSLAM_EXPECTED_SOURCE_SHA256')
    actual=hashlib.sha256(json.dumps(trees,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if expected and actual!=expected:raise ValueError('source implementation disagrees with reviewed campaign')
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x') as stream:
        json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    return target,value


def verify_capture(repo,path,*,check_live=False):
    repo=Path(repo).resolve();value=json.loads(Path(path).read_text())
    if value.get('schema')!=1 or value.get('phase')!='before_estimation':raise ValueError('unexpected implementation capture schema/phase')
    store=repo/safe_relative(value['blob_store'])
    if store!=repo/'results/.implementation-blobs/sha256':raise ValueError('unexpected implementation blob store')
    checked=set();count=0
    def check(tree):
        nonlocal count
        root=repo/safe_relative(tree['path'])
        if check_live:
            if git(root,'rev-parse','HEAD').decode().strip()!=tree['commit']:
                raise ValueError('source revision changed since capture')
            if set(inventory_tree(root,tree['scope']))!={r['path'] for r in tree['entries']}:
                raise ValueError('source file membership changed since capture')
        for entry in tree['entries']:
            source=root/safe_relative(entry['path']);kind=entry['kind'];count+=1
            if kind not in ('gitlink','absent_tracked_file','file','symlink'):
                raise ValueError('unknown source capture entry kind')
            if kind=='gitlink':
                if entry['checkout'] is not None:check(entry['checkout'])
                elif check_live and (source/'.git').exists():raise ValueError('submodule availability changed since capture')
                continue
            if kind=='absent_tracked_file':
                if check_live and (source.exists() or source.is_symlink()):raise ValueError('deleted source changed since capture')
                continue
            digest=entry['sha256']
            if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):raise ValueError('invalid blob digest')
            if digest not in checked:
                blob=store/digest
                if blob.is_symlink() or not blob.is_file() or blob.stat().st_size!=entry['size_bytes'] or digest_file(blob)!=digest:
                    raise ValueError('missing or changed source archive blob')
                checked.add(digest)
            if check_live:
                before=signature(source)
                if stat.S_IMODE(before[2])!=entry['mode']:raise ValueError('source permissions changed since capture')
                if kind=='symlink':
                    if not source.is_symlink():raise ValueError('source type changed since capture')
                    actual=hashlib.sha256(os.fsencode(os.readlink(source))).hexdigest()
                else:
                    if not stat.S_ISREG(before[2]):raise ValueError('source type changed since capture')
                    actual=digest_file(source)
                if actual!=digest or signature(source)!=before:raise ValueError('source bytes changed since capture')
    for tree in value['trees']:check(tree)
    return dict(entries=count,unique_blobs=len(checked),archive_verified=True,live_checkout_verified=check_live)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',required=True,type=Path)
    ap.add_argument('--run',required=True,type=Path)
    ap.add_argument('--verify',action='store_true')
    args=ap.parse_args();repo=args.repo.resolve();run=args.run.resolve()
    if args.verify:
        result=verify_capture(repo,run/'provenance/implementation.json',check_live=True)
    else:
        relative=run.relative_to(repo/'results')
        if len(relative.parts)!=5:raise ValueError('unexpected physical attempt path')
        target,value=capture(repo,run,relative.parts[3])
        result=dict(captured=True,trees=len(value['trees']),elapsed_s=value['elapsed_s'])
    print(json.dumps(result))


if __name__=='__main__':main()
