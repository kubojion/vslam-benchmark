#!/usr/bin/env bash
# Run MASt3R-SLAM (monocular SLAM with optional loop closure) on a sequence.
#
# Usage: scripts/run/run_mast3r_slam.sh <dataset> <seq> [run_id=1] [run_type=vo|vo-lc]
#
# Supported run types:
#   vo    -> LC disabled, output -> results/vo/<dataset>/<seq>/mast3r_slam/run<N>/
#   vo-lc -> LC enabled,  output -> results/vo-lc/<dataset>/<seq>/mast3r_slam/run<N>/

#
# 'vio' / 'vio-lc' are rejected: MASt3R-SLAM has no IMU support.
#
# Reads:
#   datasets/<dataset>/<seq>/cam0/*.png   (or mav0/cam0/data/*.png)
#   configs/mast3r_slam/<dataset>.yaml    (intrinsics + LC threshold overrides)
#
# Writes:
#   trajectory.txt   TUM
#   run_log.txt
#   resources.csv
#   run_meta.json
set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"

# main.py exposes no --no-retrieval flag; loop closure is governed by
# retrieval.k in the config (0 = no candidates). Hence one config per mode.
case "$RUN_TYPE" in
    vo)      CFG_MODE="vo" ;;
    vo-lc)   CFG_MODE="vo_lc" ;;
    vio|vio-lc)
             echo "[mast3r_slam] ERROR: MASt3R-SLAM is visual-only; use run_type=vo or vo-lc, not $RUN_TYPE" >&2; exit 2 ;;
    *)       echo "[mast3r_slam] ERROR: run_type must be vo or vo-lc (got: $RUN_TYPE)" >&2; exit 2 ;;
esac

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/mast3r_slam/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_mast3r_slam_${RUN_TYPE}_run${RUN_ID}.log"
CFG="$WS/configs/mast3r_slam/${DATASET}_${CFG_MODE}.yaml"
CALIB="$WS/configs/mast3r_slam/${DATASET}_calib.yaml"
REPO="$WS/src/MASt3R-SLAM"

[[ -f "$CFG" ]] || { echo "ERROR: no MASt3R-SLAM config at $CFG"; exit 2; }
[[ -f "$CALIB" ]] || { echo "ERROR: no MASt3R-SLAM calib at $CALIB"; exit 2; }
[[ -d "$REPO" ]] || { echo "ERROR: MASt3R-SLAM repo missing at $REPO (run scripts/build/setup_mast3r_slam_env.sh)"; exit 2; }

IMG_DIR=""
for candidate in "$SEQ_DIR/cam0" "$SEQ_DIR/mav0/cam0/data"; do
    if [[ -d "$candidate" ]]; then IMG_DIR="$candidate"; break; fi
done
[[ -n "$IMG_DIR" ]] || { echo "ERROR: no cam0 image folder under $SEQ_DIR"; exit 2; }

mkdir -p "$WS/logs"
prepare_fresh_run_dir "$OUT_DIR"

set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate mast3r_slam
set -u

python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap "kill $MONPID 2>/dev/null || true" EXIT

cd "$REPO"
START=$(date +%s.%N)

# main.py takes --save-as as a LABEL, not a path: it writes
#   logs/<save-as>/<basename of --dataset>.txt
# relative to its own cwd (the repo). Use a run-unique label, then move the
# result into $OUT_DIR ourselves.
SAVE_AS="bench_${DATASET}_${SEQ}_${RUN_TYPE}_run${RUN_ID}"
rm -rf "$REPO/logs/$SAVE_AS"

python3 main.py \
    --dataset "$IMG_DIR" \
    --config  "$CFG" \
    --calib   "$CALIB" \
    --save-as "$SAVE_AS" \
    --no-viz \
    2>&1 | tee "$LOG"

END=$(date +%s.%N)

SEQ_STEM=$(basename "$IMG_DIR")
TRAJ_SRC="$REPO/logs/$SAVE_AS/${SEQ_STEM}.txt"
if [[ ! -f "$TRAJ_SRC" ]]; then
    TRAJ_SRC=$(find "$REPO/logs/$SAVE_AS" -maxdepth 1 -name '*.txt' 2>/dev/null | head -1)
fi
if [[ -z "$TRAJ_SRC" || ! -s "$TRAJ_SRC" ]]; then
    echo "[mast3r_slam] ERROR: no trajectory produced under $REPO/logs/$SAVE_AS" | tee -a "$LOG"
    exit 1
fi
cp "$TRAJ_SRC" "$OUT_DIR/trajectory.txt"
echo "[mast3r_slam] trajectory: $TRAJ_SRC -> $OUT_DIR/trajectory.txt" | tee -a "$LOG"

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt" 2>/dev/null || echo 0)
USE_LC_PY=$([[ "$RUN_TYPE" == "vo-lc" ]] && echo True || echo False)
python3 -c "
import json
print(json.dumps({'algo':'mast3r_slam','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
                  'run_type':'$RUN_TYPE','use_imu':False,'use_lc':$USE_LC_PY,
                  'duration_s':$DUR,'frames':$NFR,'fps':$NFR/$DUR if $DUR>0 else 0}))
" > "$OUT_DIR/run_meta.json"
python3 "$(dirname "$0")/_enrich_run_meta.py" "$OUT_DIR/run_meta.json" \
    --config "${CONFIG:-${CONFIG_FILE:-${CFG:-}}}" --container "${CONTAINER:-}" \
    --playback-rate "${PLAYBACK_RATE:-${OV2SLAM_PLAYBACK_RATE:-${OPENVINS_RATE:-}}}" || true
echo "[mast3r_slam] done (run ${RUN_ID})"
