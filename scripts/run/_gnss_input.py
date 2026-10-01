#!/usr/bin/env python3
"""Validate and preserve the exact GNSS input used by a future attempt.

No ROS dependency. Missing/zero variances use explicitly recorded fallback values;
CSV status 0 is a real fix status, not a missing value. No-fix rows are excluded.
"""
import argparse
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from pathlib import Path
import re


def read_gnss_csv(path):
    rows=[];previous=None
    with Path(path).open() as stream:
        reader=csv.DictReader(stream)
        if not {'t','lat','lon','alt'}.issubset(reader.fieldnames or []):
            raise ValueError('GNSS CSV requires named t,lat,lon,alt columns')
        for line,row in enumerate(reader,2):
            try:
                seconds=Decimal(row['t'])
                if not seconds.is_finite() or abs(seconds)>Decimal('1e11'):
                    raise ValueError('timestamp must be finite seconds')
                stamp=int(round(seconds*1000000000))
                if previous is not None and stamp<=previous:raise ValueError('timestamps must increase strictly')
                previous=stamp
                status=int(row['status']) if row.get('status') not in (None,'') else None
                if status not in (None,-1,0,1,2):raise ValueError('unknown NavSatFix status')
                if status==-1:continue
                lat,lon,alt=[float(row[k]) for k in ('lat','lon','alt')]
                if not all(math.isfinite(v) for v in (lat,lon,alt)) or abs(lat)>90 or abs(lon)>180:
                    raise ValueError('invalid geodetic position')
                covariance=[]
                for k in ('cov_xx','cov_yy','cov_zz'):
                    value=float(row[k]) if row.get(k) not in (None,'') else None
                    if value is not None and (not math.isfinite(value) or value<0):raise ValueError('invalid GNSS variance')
                    covariance.append(value if value else None)
                rows.append((stamp,lat,lon,alt,*covariance,status))
            except (ValueError,TypeError,OverflowError,InvalidOperation) as exc:
                raise ValueError(f'GNSS CSV row {line}: {exc}') from exc
    if not rows:raise ValueError('GNSS CSV has no usable fixes')
    return rows


def fix_uncertainty(covariance,status,cov_xy=1.0,cov_z=4.0,default_status=0):
    if len(covariance)!=3 or any(v is not None and (not math.isfinite(v) or v<0) for v in covariance):
        raise ValueError('expected three nonnegative finite variances or missing values')
    if not all(math.isfinite(v) and v>0 for v in (cov_xy,cov_z)):
        raise ValueError('GNSS fallback variances must be finite and positive')
    if default_status not in (0,1,2):raise ValueError('invalid default fix status')
    resolved=tuple(v if v is not None and v>0 else fallback for v,fallback in zip(covariance,(cov_xy,cov_xy,cov_z)))
    return resolved,status if status is not None else default_status


def prepare(source,output,variant,explicit_source,*,cov_xy=1.0,cov_z=4.0,default_status=0):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',variant):raise ValueError('unsafe variant name')
    if variant!='default' and not explicit_source:
        raise ValueError('a named GNSS variant requires an explicit GNSS_CSV input file')
    fix_uncertainty((None,None,None),None,cov_xy,cov_z,default_status)
    source,output=Path(source),Path(output)
    raw=source.read_bytes()
    # Validate the bytes copied, rather than re-reading a source another process
    # could replace between validation and copying.
    if output.exists() or output.with_suffix('.json').exists():
        raise ValueError('GNSS attempt input already exists; refusing replacement')
    with output.open('xb') as stream:stream.write(raw)
    # Keep invalid input as evidence; no estimator is started by this helper.
    rows=read_gnss_csv(output)
    record=dict(schema=1,variant=variant,explicit_input=explicit_source,
        source_name=source.name,input_sha256=hashlib.sha256(raw).hexdigest(),usable_fixes=len(rows),
        first_timestamp_ns=rows[0][0],last_timestamp_ns=rows[-1][0],
        fallback_variance_m2=dict(x=cov_xy,y=cov_xy,z=cov_z),default_status=default_status,
        no_fix_policy='exclude_status_minus_one',zero_or_missing_covariance='fallback_per_axis',
        csv_status_zero_is_preserved=True)
    with output.with_suffix('.json').open('x') as stream:
        stream.write(json.dumps(record,indent=2)+'\n')
    return record


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',type=Path);ap.add_argument('output',type=Path)
    ap.add_argument('--variant',default='default');ap.add_argument('--explicit-source',action='store_true')
    ap.add_argument('--cov-xy',type=float,default=1.0);ap.add_argument('--cov-z',type=float,default=4.0)
    ap.add_argument('--status',type=int,default=0)
    args=ap.parse_args()
    try:
        record=prepare(args.source,args.output,args.variant,args.explicit_source,cov_xy=args.cov_xy,cov_z=args.cov_z,default_status=args.status)
    except (ValueError,OSError) as exc:ap.error(str(exc))
    print(f"[gnss] preserved {record['usable_fixes']} fixes; variant={args.variant}; sha256={record['input_sha256']}")


if __name__=='__main__':main()
