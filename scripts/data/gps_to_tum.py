#!/usr/bin/env python3
"""Project a GPS CSV (t,lat,lon,alt) into local ENU and write TUM."""
import sys, csv, numpy as np
from pyproj import Transformer, CRS

if len(sys.argv) < 2:
    sys.exit("usage: gps_to_tum.py gps.csv > gt_tum.txt")
rows = list(csv.DictReader(open(sys.argv[1])))
ts   = np.array([float(r['t']) for r in rows])
lats = np.array([float(r['lat']) for r in rows])
lons = np.array([float(r['lon']) for r in rows])
alts = np.array([float(r['alt']) for r in rows])
crs_geo = CRS.from_epsg(4326)
crs_enu = CRS.from_proj4(f"+proj=tmerc +lat_0={lats[0]} +lon_0={lons[0]} "
                         "+k=1 +x_0=0 +y_0=0 +ellps=WGS84")
tr = Transformer.from_crs(crs_geo, crs_enu, always_xy=True)
xs, ys = tr.transform(lons, lats)
zs = alts - alts[0]
for t, x, y, z in zip(ts, xs, ys, zs):
    print(f"{t:.9f} {x:.6f} {y:.6f} {z:.6f} 0 0 0 1")
