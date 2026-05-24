#!/usr/bin/env bash
# NOTE: DROPPED - LFSD was removed from scope. This script is kept for reference only.
# Build associations.txt for ORB-SLAM3 RGB-D from an LFSD run.
# Usage: scripts/convert_lfsd.sh datasets/lfsd/run_01
set -euo pipefail
RUN=$1
[[ -d "$RUN/rgb"   ]] || { echo "no $RUN/rgb"; exit 1; }
[[ -d "$RUN/depth" ]] || { echo "no $RUN/depth"; exit 1; }

python3 - "$RUN" <<'PY'
import os, sys, re, pathlib
run = pathlib.Path(sys.argv[1])
def index(folder):
    out = {}
    for p in sorted(folder.iterdir()):
        m = re.match(r'([\d.]+)\.(png|jpg|jpeg)$', p.name)
        if not m: continue
        out[float(m.group(1))] = p.relative_to(run).as_posix()
    return out
rgb   = index(run/'rgb')
depth = index(run/'depth')
if not rgb or not depth:
    sys.exit("could not parse timestamps from filenames; "
             "rename images to '<seconds>.png' or write a custom association")
out = run/'associations.txt'
with out.open('w') as f:
    drs = sorted(depth)
    import bisect
    for tr, prgb in sorted(rgb.items()):
        i = bisect.bisect_left(drs, tr)
        cands = [j for j in (i-1,i) if 0<=j<len(drs)]
        td = min(cands, key=lambda j: abs(drs[j]-tr))
        td = drs[td]
        if abs(td-tr) > 0.05: continue
        f.write(f"{tr:.6f} {prgb} {td:.6f} {depth[td]}\n")
print(f"wrote {out}")
PY
