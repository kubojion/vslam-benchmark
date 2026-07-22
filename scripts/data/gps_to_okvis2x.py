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
import csv
import math
from pathlib import Path


HEADER = "#timestamp [ns],latitude [deg],longitude [deg],altitude [m],hErr [m],vErr [m]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seq_dir", type=Path, help="sequence dir containing gps.csv")
    ap.add_argument("--h-err", type=float, default=1.0,
                    help="fallback horizontal stdev [m] when gps.csv has no cov columns")
    ap.add_argument("--v-err", type=float, default=2.0,
                    help="fallback vertical stdev [m] when gps.csv has no cov columns")
    args = ap.parse_args()

    src = args.seq_dir / "gps.csv"
    if not src.is_file():
        raise SystemExit(f"[gps_to_okvis2x] missing {src}")

    dst = args.seq_dir / "mav0" / "gps0" / "data_raw.csv"
    dst.parent.mkdir(parents=True, exist_ok=True)

    n = 0
    with src.open() as fin, dst.open("w", newline="") as fout:
        rd = csv.DictReader(fin)
        fout.write(HEADER + "\n")
        for row in rd:
            t_ns = round(float(row["t"]) * 1e9)

            # Variances -> standard deviations. Horizontal combines the two
            # in-plane terms; OKVIS2-X takes a single isotropic hErr.
            if row.get("cov_xx") and row.get("cov_yy"):
                h_err = math.sqrt((float(row["cov_xx"]) + float(row["cov_yy"])) / 2.0)
            else:
                h_err = args.h_err
            v_err = math.sqrt(float(row["cov_zz"])) if row.get("cov_zz") else args.v_err

            fout.write(f"{t_ns},{float(row['lat']):.9f},{float(row['lon']):.9f},"
                       f"{float(row['alt']):.4f},{h_err:.4f},{v_err:.4f}\n")
            n += 1

    if n == 0:
        raise SystemExit(f"[gps_to_okvis2x] no rows read from {src}")
    print(f"[gps_to_okvis2x] wrote {dst} ({n} fixes)")


if __name__ == "__main__":
    main()
