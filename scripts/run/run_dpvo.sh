#!/usr/bin/env bash
# Run DPVO / DPV-SLAM (deep patch visual odometry) on a sequence.
#
# Usage: scripts/run/run_dpvo.sh <dataset> <seq> [run_id=1] [run_type=vo]
#
# DPVO is monocular (cam0 only), no IMU. run_type:
#   vo      -> DPVO (odometry only)                -> results-vo/
#   vio-lc  -> DPV-SLAM (LOOP_CLOSURE True)         -> results-vio-lc/
#             (the vio-lc bucket is reused for its monocular+LC mode, as with
#              MASt3R-SLAM; there is no IMU.)
#
# Monocular -> the trajectory is up-to-scale; only Sim(3)-aligned ATE is
# meaningful against the metric ground truth.
#
# Reads:
#   datasets/<dataset>/<seq>/cam0/*            (or mav0/cam0/data/*)
#   datasets/<dataset>/<seq>/times.txt         (one timestamp per frame)
#   configs/dpvo/<dataset>.txt                 (fx fy cx cy, rectified cam0)
#
# Writes (under $RESULTS_ROOT/<dataset>/<seq>/dpvo/run<N>/):
#   trajectory.txt   TUM (timestamp_s tx ty tz qx qy qz qw)
#   run_log.txt, resources.csv, run_meta.json
set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"

case "$RUN_TYPE" in
    vo)     DPVO_OPTS=() ;;
    vio-lc) DPVO_OPTS=(--opts LOOP_CLOSURE True) ;;   # DPV-SLAM
    *)      echo "[dpvo] ERROR: run_type must be vo (DPVO) or vio-lc (DPV-SLAM)" >&2; exit 2 ;;
esac

REPO="$WS/src/DPVO"
SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/dpvo/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_dpvo_${RUN_TYPE}_run${RUN_ID}.log"
CALIB="$WS/configs/dpvo/${DATASET}.txt"
NET="$REPO/dpvo.pth"
STRIDE="${DPVO_STRIDE:-1}"   # 1 = every frame (most comparable to the other VO methods)
SKIP="${DPVO_SKIP:-0}"

[[ -d "$REPO" ]] || { echo "[dpvo] ERROR: repo missing at $REPO (run scripts/build/setup_dpvo_env.sh)" >&2; exit 2; }
[[ -f "$NET" ]]  || { echo "[dpvo] ERROR: weights missing at $NET" >&2; exit 2; }
[[ -f "$CALIB" ]] || { echo "[dpvo] ERROR: no calib at $CALIB" >&2; exit 2; }

# Monocular: cam0 only.
IMG_DIR=""
for c in "$SEQ_DIR/cam0" "$SEQ_DIR/mav0/cam0/data"; do
    [[ -d "$c" ]] && { IMG_DIR="$c"; break; }
done
[[ -n "$IMG_DIR" ]] || { echo "[dpvo] ERROR: no cam0 image folder under $SEQ_DIR" >&2; exit 2; }
[[ -f "$SEQ_DIR/times.txt" ]] || { echo "[dpvo] ERROR: missing $SEQ_DIR/times.txt" >&2; exit 2; }

mkdir -p "$OUT_DIR" "$WS/logs"
: > "$OUT_DIR/run_log.txt"
NAME="bench_${DATASET}_${SEQ}_${RUN_TYPE}_run${RUN_ID}"

echo "[dpvo] $DATASET/$SEQ type=${RUN_TYPE} run=${RUN_ID} stride=${STRIDE} -> $OUT_DIR" | tee "$LOG"

set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate dpvo
set -u

python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap "kill $MONPID 2>/dev/null || true" EXIT

cd "$REPO"
rm -f "saved_trajectories/${NAME}.txt"

START=$(date +%s.%N)
python3 demo.py \
    --imagedir "$IMG_DIR" \
    --calib "$CALIB" \
    --network "$NET" \
    --name "$NAME" \
    --stride "$STRIDE" \
    --skip "$SKIP" \
    --save_trajectory \
    "${DPVO_OPTS[@]}" 2>&1 | python3 -u -c "
import sys, time
t0 = time.time()
for line in sys.stdin:
    sys.stdout.write(f'{time.time()-t0:.3f} {line}'); sys.stdout.flush()
" | tee -a "$OUT_DIR/run_log.txt" "$LOG"
END=$(date +%s.%N)

RAW="$REPO/saved_trajectories/${NAME}.txt"
if [[ ! -s "$RAW" ]]; then
    echo "[dpvo] ERROR: no trajectory at $RAW — run failed" | tee -a "$LOG"; exit 1
fi

# demo.py stamps poses with the FRAME INDEX (0,1,2,...) over the strided image
# list, not the real time. Remap index i -> times.txt[skip + i*stride].
python3 - "$RAW" "$SEQ_DIR/times.txt" "$OUT_DIR/trajectory.txt" "$STRIDE" "$SKIP" <<'PY'
import sys
raw, times_p, out_p, stride, skip = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
ts = [l.split()[0] for l in open(times_p) if l.strip()]
def to_s(t): return float(t)/1e9 if "." not in t else float(t)
n = 0
with open(raw) as fin, open(out_p, "w") as fout:
    for line in fin:
        p = line.split()
        if len(p) != 8:
            continue
        idx = skip + int(round(float(p[0]))) * stride   # p[0] is the frame index
        if idx >= len(ts):
            raise SystemExit(f"[dpvo] pose index {idx} beyond {len(ts)} timestamps")
        fout.write(f"{to_s(ts[idx]):.9f} " + " ".join(p[1:8]) + "\n")
        n += 1
print(f"[dpvo] wrote {out_p} ({n} poses)")
PY

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt")
USE_LC=$([[ "$RUN_TYPE" == "vio-lc" ]] && echo True || echo False)
python3 -c "
import json
print(json.dumps({'algo':'dpvo','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
                  'run_type':'$RUN_TYPE','use_imu':False,'use_lc':$USE_LC,
                  'duration_s':$DUR,'frames':$NFR,'fps':$NFR/$DUR if $DUR>0 else 0}))
" > "$OUT_DIR/run_meta.json"
echo "[dpvo] run ${RUN_ID} done in ${DUR}s, ${NFR} poses" | tee -a "$LOG"
