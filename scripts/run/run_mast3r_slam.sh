#!/usr/bin/env bash
# Run MASt3R-SLAM (monocular SLAM with optional loop closure) on a sequence.
#
# Usage: scripts/run/run_mast3r_slam.sh <dataset> <seq> [run_id=1] [run_type=vo|vio-lc]
#
# Supported run types:
#   vo     -> LC disabled, output -> results-vo/<dataset>/<seq>/mast3r_slam/run<N>/
#   vio-lc -> LC enabled,  output -> results-imu-lc/<dataset>/<seq>/mast3r_slam/run<N>/

#
# 'vio' (LC off, IMU on) is rejected: MASt3R-SLAM has no IMU support.
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
resolve_run_type "$RUN_TYPE"

case "$RUN_TYPE" in
    vo)      LC_FLAG="--no-retrieval" ;;
    vio-lc)  LC_FLAG="" ;;  # LC is on by default
    *)       echo "[mast3r_slam] ERROR: run_type must be vo or vio-lc (got: $RUN_TYPE)" >&2; exit 2 ;;
esac

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/mast3r_slam/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_mast3r_slam_${RUN_TYPE}_run${RUN_ID}.log"
CFG="$WS/configs/mast3r_slam/${DATASET}.yaml"
REPO="$WS/src/MASt3R-SLAM"

[[ -f "$CFG" ]] || { echo "ERROR: no MASt3R-SLAM config at $CFG"; exit 2; }
[[ -d "$REPO" ]] || { echo "ERROR: MASt3R-SLAM repo missing at $REPO (run scripts/build/setup_mast3r_slam_env.sh)"; exit 2; }

IMG_DIR=""
for candidate in "$SEQ_DIR/cam0" "$SEQ_DIR/mav0/cam0/data"; do
    if [[ -d "$candidate" ]]; then IMG_DIR="$candidate"; break; fi
done
[[ -n "$IMG_DIR" ]] || { echo "ERROR: no cam0 image folder under $SEQ_DIR"; exit 2; }

mkdir -p "$OUT_DIR" "$WS/logs"

set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate mast3r_slam
set -u

python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap "kill $MONPID 2>/dev/null || true" EXIT

cd "$REPO"
START=$(date +%s.%N)

# TODO: the upstream entrypoint name varies (main_vo.py / demo.py / scripts/...).
# Adjust the command below to match your checkout. Trajectory should be saved
# in TUM format directly to $OUT_DIR/trajectory.txt.
python3 main.py \
    --dataset "$IMG_DIR" \
    --config  "$CFG" \
    --save-trajectory "$OUT_DIR/trajectory.txt" \
    --no-viz \
    $LC_FLAG \
    2>&1 | tee "$LOG"

END=$(date +%s.%N)

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt" 2>/dev/null || echo 0)
USE_LC_PY=$([[ "$RUN_TYPE" == "vio-lc" ]] && echo True || echo False)
python3 -c "
import json
print(json.dumps({'algo':'mast3r_slam','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
                  'run_type':'$RUN_TYPE','use_imu':False,'use_lc':$USE_LC_PY,
                  'duration_s':$DUR,'frames':$NFR,'fps':$NFR/$DUR if $DUR>0 else 0}))
" > "$OUT_DIR/run_meta.json"
echo "[mast3r_slam] done (run ${RUN_ID})"
