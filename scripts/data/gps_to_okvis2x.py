#!/usr/bin/env python3
"""
Convert a per-sequence gps.csv into the GNSS layout OKVIS2-X expects.

OKVIS2-X reads GNSS from inside the dataset folder it is pointed at (the same
folder that holds cam0/ and imu0/, i.e. <seq_dir>/mav0/), and the filename
depends on `gps_parameters.data_type` in the config:

  data_type: cartesian        ->  mav0/gps0/data.csv
                                  timestamp_ns,x,y,z,hErr1,hErr2,vErr
  data_type: geodetic         ->  mav0/gps0/data_raw.csv
                                  timestamp_ns,lat,lon,alt,hErr,vErr
  data_type: geodetic-leica   ->  mav0/gnss.csv

This script writes the *geodetic* form, which is what configs/okvis2x/*_gnss_vio.yaml
select: it hands OKVIS2-X the raw WGS84 fix and lets it estimate the
world<->GNSS transform itself, rather than pre-projecting into a local ENU
frame (which is what scripts/data/gps_to_tum.py does for ground truth).

Source gps.csv format (written by the rosbag converters):
  t,lat,lon,alt[,cov_xx,cov_yy,cov_zz,status]    t in seconds (float)

Positional accuracy: OKVIS2-X wants standard deviations in metres, not
variances. When cov_* columns are present they are converted (sigma = sqrt(cov));
otherwise the defaults below are used. These match the conventional-GPS defaults
in scripts/run/gnss_data_player.py (1.0 m^2 horizontal / 4.0 m^2 vertical),
so GNSS uncertainty is stated consistently across the gnss-vio algorithms.
For PPK-quality fixes pass --h-err 0.2 --v-err 0.3.

Note on timestamps: OKVIS2-X subtracts a GNSS_LEAP_NANOSECONDS constant from
every GNSS timestamp, but that constant is 0 in ViSensorBase.hpp. So plain UTC
epoch nanoseconds -- the same clock as imu0/data.csv -- are correct here and
need no leap-second correction.

Usage:
    python3 scripts/data/gps_to_okvis2x.py <seq_dir> [--h-err 1.0] [--v-err 2.0]

Outputs <seq_dir>/mav0/gps0/data_raw.csv
"""
import argparse
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'run'))
from _gnss_input import read_gnss_csv, fix_uncertainty

HEADER = "#timestamp [ns],latitude [deg],longitude [deg],altitude [m],hErr [m],vErr [m]"


def convert(source, destination, *, h_err=1.0, v_err=2.0):
    if not all(math.isfinite(v) and v>0 for v in (h_err,v_err)):
        raise ValueError('fallback standard deviations must be finite and positive')
    fixes=read_gnss_csv(source)
    destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    # An existing native input is evidence, not an existence-only reusable cache.
    with destination.open('x') as stream:
        stream.write(HEADER+'\n')
        for stamp,lat,lon,alt,cxx,cyy,czz,status in fixes:
            covariance,_=fix_uncertainty((cxx,cyy,czz),status,h_err*h_err,v_err*v_err)
            horizontal=math.sqrt((covariance[0]+covariance[1])/2)
            vertical=math.sqrt(covariance[2])
            stream.write(f'{stamp},{lat:.9f},{lon:.9f},{alt:.4f},{horizontal:.4f},{vertical:.4f}\n')
    return len(fixes)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('seq_dir',type=Path)
    ap.add_argument('--source',type=Path,help='explicit preserved source CSV')
    ap.add_argument('--output',type=Path,help='fresh per-attempt native CSV; never overwrite an existing file')
    ap.add_argument('--h-err',type=float,default=1.0,help='fallback horizontal standard deviation in metres')
    ap.add_argument('--v-err',type=float,default=2.0,help='fallback vertical standard deviation in metres')
    args=ap.parse_args()
    source=args.source or args.seq_dir/'gps.csv'
    output=args.output or args.seq_dir/'mav0/gps0/data_raw.csv'
    try:
        n=convert(source,output,h_err=args.h_err,v_err=args.v_err)
    except (ValueError,OSError) as exc:ap.error(str(exc))
    print(f'[gps_to_okvis2x] wrote {output} ({n} usable fixes)')


if __name__=='__main__':main()
