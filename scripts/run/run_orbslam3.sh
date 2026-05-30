#!/usr/bin/env bash
# Run ORB-SLAM3 on a converted sequence (cam0/, cam1/, times.txt).
# Usage: scripts/run/run_orbslam3.sh <dataset> <seq> [run_id=1] [run_type=vo]
#
# run_type selects binary + config + results tree:
#   vo      -> stereo_euroc          + <dataset>_stereo.yaml          (LC off)
#              -> results-vo/<dataset>/<seq>/orbslam3/run<N>/
#   vio     -> stereo_inertial_euroc + <dataset>_stereo_inertial.yaml (LC off)
#              -> results-vio/<dataset>/<seq>/orbslam3/run<N>/
#   vio-lc  -> stereo_inertial_euroc + <dataset>_stereo_inertial_lc.yaml (LC on)
#              -> results-vio-lc/<dataset>/<seq>/orbslam3/run<N>/
#
# vio / vio-lc require:
#   - <dataset_seq>/mav0/cam0/data, /mav0/cam1/data, /mav0/imu0/data.csv  (EuRoC)
#   - <dataset_seq>/times.txt                                              (ns)
# The stereo_inertial_euroc binary reads the IMU CSV from mav0/imu0/data.csv.
set -euo pipefail
DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
resolve_run_type "$RUN_TYPE"
SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/orbslam3/run${RUN_ID}"
LOG_GLOBAL="$WS/logs/${DATASET}_${SEQ}_orbslam3_${RUN_TYPE}_run${RUN_ID}.log"

case "$RUN_TYPE" in
    vo)
        BIN=./Examples/Stereo/stereo_euroc
        CFG="$WS/configs/orbslam3/${DATASET}_stereo.yaml"
        ;;
    vio)
        BIN=./Examples/Stereo-Inertial/stereo_inertial_euroc
        CFG="$WS/configs/orbslam3/${DATASET}_stereo_inertial.yaml"
        ;;
    vio-lc)
        BIN=./Examples/Stereo-Inertial/stereo_inertial_euroc
        CFG="$WS/configs/orbslam3/${DATASET}_stereo_inertial_lc.yaml"
        ;;
    *)
        echo "[orbslam3] unknown run_type: $RUN_TYPE (expected vo|vio|vio-lc)" >&2
        exit 2
        ;;
esac
[[ -f "$CFG" ]] || { echo "[orbslam3] missing config: $CFG" >&2; exit 2; }
[[ "$RUN_TYPE" =~ vio ]] && [[ ! -f "$SEQ_DIR/mav0/imu0/data.csv" ]] && {
    echo "[orbslam3] missing IMU: $SEQ_DIR/mav0/imu0/data.csv" >&2
    echo "[orbslam3] hint: python3 scripts/data/imu_to_euroc.py $SEQ_DIR" >&2
    exit 2
}
mkdir -p "$OUT_DIR" "$WS/logs"

cd "$WS/src/ORB_SLAM3"
echo "[orbslam3] $DATASET/$SEQ type=${RUN_TYPE} run=${RUN_ID} -> $OUT_DIR" | tee "$LOG_GLOBAL"
echo "[orbslam3] binary=$BIN  cfg=$CFG" | tee -a "$LOG_GLOBAL"

# Resource monitor: GPU + CPU + RAM sampled every 1 s
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap "kill $MONPID 2>/dev/null || true" EXIT

START=$(date +%s.%N)
# ORB-SLAM3 may crash in Pangolin destructor after saving trajectories; that is
# harmless — we only care that the trajectory file was written before exit.
# Pipe through a Python timestamper so each log line gets a relative offset (s).
"$BIN" \
    Vocabulary/ORBvoc.txt \
    "$CFG" \
    "$SEQ_DIR" \
    "$SEQ_DIR/times.txt" \
    "${DATASET}_${SEQ}_orbslam3" 2>&1 | \
  python3 -u -c "
import sys, time
t0 = time.time()
for line in sys.stdin:
    sys.stdout.write(f'{time.time()-t0:.3f} {line}')
    sys.stdout.flush()
" | tee -a "$OUT_DIR/run_log.txt" "$LOG_GLOBAL" || true
END=$(date +%s.%N)

TRAJ_SRC="f_${DATASET}_${SEQ}_orbslam3.txt"
if [[ ! -f "$TRAJ_SRC" ]]; then
    echo "[orbslam3] ERROR: trajectory file not found — SLAM likely failed" | tee -a "$LOG_GLOBAL"
    exit 1
fi
mv "$TRAJ_SRC" "$OUT_DIR/trajectory.txt"
mv "kf_${DATASET}_${SEQ}_orbslam3.txt" "$OUT_DIR/keyframes.txt" 2>/dev/null || true

# stereo_euroc emits nanosecond timestamps; evo and gt_tum.txt use seconds.
# Convert in-place: divide column 1 by 1e9, preserve full 9-decimal precision.
awk '{printf "%.9f %s %s %s %s %s %s %s\n",$1/1e9,$2,$3,$4,$5,$6,$7,$8}' \
    "$OUT_DIR/trajectory.txt" > "$OUT_DIR/trajectory_s.txt"
mv "$OUT_DIR/trajectory_s.txt" "$OUT_DIR/trajectory.txt"
[[ -f "$OUT_DIR/keyframes.txt" ]] && \
awk '{printf "%.9f %s %s %s %s %s %s %s\n",$1/1e9,$2,$3,$4,$5,$6,$7,$8}' \
    "$OUT_DIR/keyframes.txt" > "$OUT_DIR/keyframes_s.txt" && \
mv "$OUT_DIR/keyframes_s.txt" "$OUT_DIR/keyframes.txt"

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt")
python3 -c "
import json
print(json.dumps({
    'algo':'orbslam3','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,    'run_type':'$RUN_TYPE',    'duration_s':$DUR,'frames':$NFR,
    'fps':$NFR/$DUR if $DUR>0 else 0
}))
" > "$OUT_DIR/run_meta.json"
echo "[orbslam3] run ${RUN_ID} done in ${DUR}s, ${NFR} frames"
