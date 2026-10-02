#!/usr/bin/env python3
"""Build an immutable version of the approved ZED reference; never overwrite GT.

Uses only hash-pinned raw GNSS evidence and approved exclusions. No trajectory
scores, smoothing or fitted time correction enter reference construction.
"""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from _zed_reference import camera_positions, enu_positions, retained_intervals

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/eval'))
from _metrics import interpolate_reference


def evidence(path):
    p=Path(path)
    return dict(path=str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
                sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def build():
    audit_path=ROOT/'docs/campaigns/zed-approved-screening-20261002.json'
    audit=json.loads(audit_path.read_text())
    dependencies=[]
    for path,digest in audit['source_sha256'].items():
        item=evidence(path)
        if item['sha256']!=digest:raise ValueError('screening input changed: '+path)
        dependencies.append(item)
    # The raw NPZ inputs have independently been matched to all original bag headers,
    # geodetic positions, PVT status messages and dual-antenna baseline messages.
    verification=ROOT/'results/zed-preparation-20261002/independent-source-validation.json'
    checked=json.loads(verification.read_text())
    if not checked['filter_exactly_reproduced']:raise ValueError('source verification required')
    g=np.load(next(p for p in audit['source_sha256'] if p.endswith('/gnss.npz')))
    h=np.load(next(p for p in audit['source_sha256'] if p.endswith('/heading.npz')))
    ds=ROOT/'datasets/zed2i/field1_110426_full_10fps_q90';manifest=json.loads((ds/'manifest.json').read_text())
    image=manifest;ns=g['raw_header_timestamp_ns'];times=ns.astype(float)/1e9
    raw_keep=np.ones(len(ns),dtype=bool)
    for exc in audit['excursions']:
        start,stop=exc['rejected_raw_index_start'],exc['rejected_raw_index_stop_exclusive']
        if [int(ns[start]),int(ns[stop])]!=exc['timestamps_ns']:raise ValueError('exclusion binding differs')
        raw_keep[start:stop]=False
    if int((~raw_keep).sum())!=448:raise ValueError('approved exclusions changed')
    span=(ns>=image['start_ns'])&(ns<=image['end_ns'])
    first=np.flatnonzero(span)[0];origin=g['raw_geodetic_deg_m'][first]
    antenna=enu_positions(g['raw_geodetic_deg_m'],origin)
    hn=h['raw_header_timestamp_ns'];ned=h['raw_baseline_ned_m']
    heading_valid=h['raw_valid']&(h['raw_carrier_status']==2)
    heading_times=hn.astype(float)/1e9
    heading_support=retained_intervals(heading_times,heading_valid)
    heading_poses=np.c_[heading_times,ned[:,1],ned[:,0],-ned[:,2],np.zeros((len(hn),3)),np.ones(len(hn))]
    baseline,heading_ok=interpolate_reference(heading_poses,times,.5,heading_support)
    vectors=np.full((len(ns),3),np.nan);vectors[heading_ok]=baseline[:,1:4]
    valid=span&raw_keep&heading_ok&(g['raw_fix_status']>=0)&np.isin(g['raw_carrier_status'],[1,2])
    xyz=np.full((len(ns),3),np.nan);xyz[heading_ok]=camera_positions(antenna[heading_ok],vectors[heading_ok])
    out=ds/'references/gnss-position-v2-20261002'
    if out.exists():raise FileExistsError(f'preserve existing reference version: {out}')
    out.mkdir(parents=True)
    result=dict(schema=1,version='gnss-position-v2-20261002',dataset='zed2i',sequence=ds.name,
        orientation_valid=False,nominal_geometry=True,
        origin_lat_lon_alt=origin.tolist(),antenna_above_left_camera_m=1.,
        body_roll_deg=0.,body_pitch_deg=0.,clock_offset_s=0.,
        heading='fixed valid RELPOSNED baseline interpolated at robot GPS header times; lateral baseline bias removed',
        float_policy='primary retains RTK float epochs outside approved spikes; fixed_only excludes float and preserves resulting gaps',
        approved_rejected_raw_samples=448,approved_excursions=15,
        image_span_raw_samples=int(span.sum()),
        limitations=['nominal height and level platform; no surveyed full 3D mounting covariance',
                     'position-only reference; identity quaternions are placeholders',
                     'field camera/robot clock offset unmeasured; no correction fitted',
                     'RTK float retained in primary; fixed-only sensitivity is mandatory'],
        evidence=dependencies+[evidence(p) for p in (audit_path,verification,ds/'manifest.json',
                 ROOT/'docs/CAMERA_ANTENNA_GEOMETRY_20261002.txt',Path(__file__),ROOT/'scripts/data/_zed_reference.py')],variants={})
    for name,keep in [('primary',valid),('fixed_only',valid&(g['raw_carrier_status']==2))]:
        poses=np.c_[times[keep],xyz[keep],np.zeros((int(keep.sum()),3)),np.ones(int(keep.sum()))]
        path=out/f'{name}.tum';np.savetxt(path,poses,fmt='%.9f')
        support=out/f'{name}-support.json'
        support.write_text(json.dumps(dict(valid_intervals=retained_intervals(times,keep)),indent=2)+'\n')
        result['variants'][name]=dict(trajectory=evidence(path),support=evidence(support),
            retained_samples=int(keep.sum()),fixed_samples=int((keep&(g['raw_carrier_status']==2)).sum()),
            float_samples=int((keep&(g['raw_carrier_status']==1)).sum()))
    # Preserve masked raw data for reproducible sensitivity, never estimator inputs.
    np.savez_compressed(out/'construction.npz',timestamp_ns=ns,antenna_enu=antenna,baseline_enu=vectors,
                        primary_keep=valid,carrier_status=g['raw_carrier_status'])
    result['construction']=evidence(out/'construction.npz')
    (out/'reference.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(path=str(out),variants=result['variants']),indent=2))


if __name__=='__main__':build()
