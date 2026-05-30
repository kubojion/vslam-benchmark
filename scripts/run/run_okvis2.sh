#!/usr/bin/env bash
# Run OKVIS2 on a converted sequence (EuRoC-ASL layout under datasets/).
# Usage: scripts/run/run_okvis2.sh <dataset> <seq> [run_id=1] [run_type=vio]
#
# run_type -> config file + results tree:
#   vo      -> configs/okvis2/<dataset>_<seq>_vo.yaml
#              -> results-vo/<dataset>/<seq>/okvis2/run<N>/
#   vio     -> configs/okvis2/<dataset>_<seq>_vio.yaml
#              -> results-vio/<dataset>/<seq>/okvis2/run<N>/
#   vio-lc  -> configs/okvis2/<dataset>_<seq>_vio_lc.yaml
#              -> results-vio-lc/<dataset>/<seq>/okvis2/run<N>/
#
# Note: OKVIS2 is fundamentally a Visual-INERTIAL estimator. Running with
# `imu_parameters.use: false` (vo) is supported by the parameter reader but
# the front-end is not designed for IMU-less stereo; results may be poor or
# the run may fail to initialise. Logged as best-effort.
#
# The synchronous app writes its trajectory CSV next to mav0/, so we copy it
# into the per-run results dir afterwards and convert to TUM format.
set -euo pipefail
DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vio}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
resolve_run_type "$RUN_TYPE"

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/okvis2/run${RUN_ID}"
LOG_GLOBAL="$WS/logs/${DATASET}_${SEQ}_okvis2_${RUN_TYPE}_run${RUN_ID}.log"

case "$RUN_TYPE" in
    vo)     CFG="$WS/configs/okvis2/${DATASET}_${SEQ}_vo.yaml"     ; OKMODE=vio  ;;
    vio)    CFG="$WS/configs/okvis2/${DATASET}_${SEQ}_vio.yaml"    ; OKMODE=vio  ;;
    vio-lc) CFG="$WS/configs/okvis2/${DATASET}_${SEQ}_vio_lc.yaml" ; OKMODE=slam ;;
    *)      echo "[okvis2] unknown run_type: $RUN_TYPE" >&2; exit 2 ;;
esac
[[ -f "$CFG" ]] || { echo "[okvis2] missing config: $CFG" >&2; exit 2; }
[[ -d "$SEQ_DIR/mav0/cam0/data" && -d "$SEQ_DIR/mav0/cam1/data" ]] \
    || { echo "[okvis2] missing $SEQ_DIR/mav0/cam{0,1}/data" >&2; exit 2; }
[[ -f "$SEQ_DIR/mav0/imu0/data.csv" ]] \
    || { echo "[okvis2] missing IMU $SEQ_DIR/mav0/imu0/data.csv" >&2;
         echo "[okvis2] hint: python3 scripts/data/imu_to_euroc.py $SEQ_DIR" >&2;
         exit 2; }

APP="$WS/src/okvis2/build/okvis_app_synchronous"
[[ -x "$APP" ]] || { echo "[okvis2] missing $APP — run scripts/build/build_okvis2.sh first" >&2; exit 2; }

mkdir -p "$OUT_DIR" "$WS/logs"
echo "[okvis2] $DATASET/$SEQ type=${RUN_TYPE} run=${RUN_ID} -> $OUT_DIR" | tee "$LOG_GLOBAL"

# Resource monitor (matches the other run_*.sh wrappers)
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap "kill $MONPID 2>/dev/null || true" EXIT

# OKVIS2 calls cv::imshow; run under a virtual X server if no DISPLAY.
RUN_PREFIX=()
if [[ -z "${DISPLAY:-}" ]]; then
    if command -v xvfb-run >/dev/null; then
        RUN_PREFIX=(xvfb-run -a -s "-screen 0 1280x720x24")
    else
        export QT_QPA_PLATFORM=offscreen
        echo "[okvis2] no DISPLAY and xvfb-run missing; setting QT_QPA_PLATFORM=offscreen" | tee -a "$LOG_GLOBAL"
    fi
fi

START=$(date +%s.%N)
"${RUN_PREFIX[@]}" "$APP" "$CFG" "$SEQ_DIR/mav0" 2>&1 | \
  python3 -u -c "
import sys, time
t0 = time.time()
for line in sys.stdin:
    sys.stdout.write(f'{time.time()-t0:.3f} {line}')
    sys.stdout.flush()
" | tee -a "$OUT_DIR/run_log.txt" "$LOG_GLOBAL" || true
END=$(date +%s.%N)

# OKVIS2 writes okvis2-<vio|slam>_trajectory.csv next to mav0/.
RAW="$SEQ_DIR/mav0/okvis2-${OKMODE}_trajectory.csv"
RAW_FINAL="$SEQ_DIR/mav0/okvis2-${OKMODE}-final_trajectory.csv"
if [[ ! -f "$RAW" ]]; then
    echo "[okvis2] ERROR: no $RAW produced — run failed" | tee -a "$LOG_GLOBAL"
    exit 1
fi
cp "$RAW" "$OUT_DIR/okvis2_raw_trajectory.csv"
[[ -f "$RAW_FINAL" ]] && cp "$RAW_FINAL" "$OUT_DIR/okvis2_final_trajectory.csv"

# Convert OKVIS2 CSV (ns-timestamp, comma-separated, 18 cols with bias+vel)
# into TUM-style trajectory.txt:  timestamp_s tx ty tz qx qy qz qw
python3 - <<PY
import csv, sys
src = "$OUT_DIR/okvis2_raw_trajectory.csv"
dst = "$OUT_DIR/trajectory.txt"
n = 0
with open(src) as fin, open(dst, "w") as fout:
    rd = csv.reader(fin)
    next(rd, None)   # skip header
    for row in rd:
        if not row: continue
        t_ns = int(row[0].strip())
        x, y, z = (row[1].strip(), row[2].strip(), row[3].strip())
        qx, qy, qz, qw = (row[4].strip(), row[5].strip(), row[6].strip(), row[7].strip())
        fout.write(f"{t_ns/1e9:.9f} {x} {y} {z} {qx} {qy} {qz} {qw}\n")
        n += 1
print(f"[okvis2] wrote {dst} ({n} poses)")
PY

# Move OKVIS2 outputs out of the dataset dir so re-runs do not stale-read them.
rm -f "$RAW" "$RAW_FINAL" "$SEQ_DIR/mav0/okvis2-${OKMODE}-final_map.csv" 2>/dev/null || true

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt")
python3 -c "
import json
print(json.dumps({
    'algo':'okvis2','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
    'run_type':'$RUN_TYPE',
    'duration_s':$DUR,'frames':$NFR,
    'fps':$NFR/$DUR if $DUR>0 else 0
}))
" > "$OUT_DIR/run_meta.json"
echo "[okvis2] run ${RUN_ID} done in ${DUR}s, ${NFR} poses"
