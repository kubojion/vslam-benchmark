#!/usr/bin/env python3
"""Prepare current source, input and known build identities; never run estimators.

Existing identities are preserved by hash before a reviewed --refresh. Run after
committing code, then rebuild the future manifest. These identities do not prove
physical calibration, loaded dependency closure, or source-to-binary linkage.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'run'))
from _capture_inputs import identity as input_identity,verify_identity as verify_inputs
from _capture_runtime import identity as runtime_identity,verify_identity as verify_runtime
from _capture_implementation import capture,verify_capture,digest_file

REPO=Path(__file__).resolve().parents[2]


def preserve(repo,path):
    if not path.is_file():return
    archive=repo/'results/.derived-history/execution-assets'/digest_file(path)/path.name
    archive.parent.mkdir(parents=True,exist_ok=True)
    if archive.exists():
        if archive.read_bytes()!=path.read_bytes():raise ValueError('archive mismatch')
    else:archive.write_bytes(path.read_bytes())
    if digest_file(archive)!=digest_file(path):raise ValueError('archive verification failed')


def write(repo,path,value,refresh):
    raw=(json.dumps(value,indent=2)+'\n').encode()
    if path.exists() and path.read_bytes()==raw:return
    if path.exists():
        if not refresh:raise ValueError('identity changed; review then use --refresh: '+str(path))
        preserve(repo,path)
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp');temp.write_bytes(raw);temp.replace(path)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--refresh',action='store_true',help='preserve and replace stale current identities after review')
    ap.add_argument('--verify',action='store_true',help='check current identities without replacing them')
    ap.add_argument('--inputs',action='store_true');ap.add_argument('--runtime',action='store_true');ap.add_argument('--sources',action='store_true')
    ap.add_argument('--dataset', action='append', help='restrict input identities to named datasets (requires --inputs only)')
    args=ap.parse_args()
    if args.verify and args.refresh:ap.error('choose verify or refresh')
    scope=[n for n in ('inputs','runtime','sources') if getattr(args,n)] or ['inputs','runtime','sources']
    if args.dataset and scope != ['inputs']:ap.error('--dataset requires --inputs only')
    folder=REPO/'results/repair-20261001'
    inventory=json.loads((folder/'inventory.json').read_text());records=[]
    if args.dataset:
        known = {c['dataset'] for c in inventory['cells']}
        if not set(args.dataset) <= known:ap.error('unknown dataset')
    targets=[]
    if 'inputs' in scope:
        targets.extend(('inputs',(ds,seq),folder/'prepared-inputs'/f'{ds}--{seq}.json')
            for ds,seq in sorted({(c['dataset'],c['sequence']) for c in inventory['cells']})
            if not args.dataset or ds in args.dataset)
    algorithms=sorted({c['algorithm'] for c in inventory['cells']})
    if 'runtime' in scope:targets.extend(('runtime',(a,),folder/'runtime-assets'/f'{a}.json') for a in algorithms)
    if 'sources' in scope:targets.extend(('sources',(a,),folder/'implementation-capture-current'/a/'provenance/implementation.json') for a in algorithms)
    for kind,identity,path in targets:
        start=time.monotonic()
        if args.verify:
            value=json.loads(path.read_text())
            if kind=='inputs':verify_inputs(REPO,value)
            elif kind=='runtime':verify_runtime(REPO,value)
            else:verify_capture(REPO,path,check_live=True)
        elif kind=='sources':
            current=False
            if path.exists():
                try:verify_capture(REPO,path,check_live=True);current=True
                except (OSError,ValueError):
                    if not args.refresh:raise
                    preserve(REPO,path);path.unlink()
            if not current:capture(REPO,path.parents[1],identity[0])
            value=json.loads(path.read_text());verify_capture(REPO,path,check_live=True)
        else:
            value=input_identity(REPO,*identity) if kind=='inputs' else runtime_identity(REPO,*identity)
            write(REPO,path,value,args.refresh)
        record=dict(kind=kind,identity=list(identity),path=str(path.relative_to(REPO)),sha256=digest_file(path),
            files=len(value.get('files',[])),missing=value.get('missing',[]),elapsed_s=time.monotonic()-start)
        records.append(record);print(json.dumps(record),flush=True)
    report=dict(schema=1,estimation_started=False,scope=scope,verification_only=args.verify,records=records,
                native_execution_verified=False,native_build_source_linkage_verified=False)
    report_path=folder/('execution-assets-verification.json' if args.verify else 'execution-assets-preparation.json')
    write(REPO,report_path,report,True)


if __name__=='__main__':main()
