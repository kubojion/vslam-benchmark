#!/usr/bin/env bash
# Run MegaSaM (monocular structure-and-motion) on a sequence.
#
# Usage: scripts/run/run_megasam.sh <dataset> <seq> [run_id=1] [run_type=vo]
#
# MegaSaM is monocular, no IMU, no LC. Only run_type=vo is supported.
#
# Reads:
#   datasets/<dataset>/<seq>/cam0/*.png    (or mav0/cam0/data/*.png)
#   configs/megasam/<dataset>_<seq>.yaml   (camera intrinsics + optional
#                                            overrides for stride, max frames)
#
# Writes (under $RESULTS_ROOT/<dataset>/<seq>/megasam/run<N>/):
#   trajectory.txt   TUM (timestamp_s tx ty tz qx qy qz qw)
#   run_log.txt      stdout
#   resources.csv    CPU+RAM sampled every 1s
#   run_meta.json    frames / duration / fps
#
# This is a scaffolding script. The upstream demo entrypoint differs across
# revisions of github.com/mega-sam/mega-sam; the actual invocation may need
# to be adjusted to match your checkout (see TODO comments below).
set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
resolve_run_type "$RUN_TYPE"
if [[ "$RUN_TYPE" != "vo" ]]; then
    echo "[megasam] ERROR: MegaSaM is monocular VO only; run_type must be 'vo'" >&2
    exit 2
fi

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/megasam/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_megasam_${RUN_TYPE}_run${RUN_ID}.log"
CFG="$WS/configs/megasam/${DATASET}_${SEQ}.yaml"
REPO="$WS/src/mega-sam"

[[ -f "$CFG" ]] || { echo "ERROR: no MegaSaM config at $CFG"; exit 2; }
[[ -d "$REPO" ]] || { echo "ERROR: MegaSaM repo missing at $REPO (run scripts/build/setup_megasam_env.sh)"; exit 2; }

# Pick the monocular image folder. Prefer cam0/, fall back to mav0/cam0/data.
IMG_DIR=""
for candidate in "$SEQ_DIR/cam0" "$SEQ_DIR/mav0/cam0/data"; do
    if [[ -d "$candidate" ]]; then IMG_DIR="$candidate"; break; fi
done
[[ -n "$IMG_DIR" ]] || { echo "ERROR: no cam0 image folder under $SEQ_DIR"; exit 2; }

mkdir -p "$OUT_DIR" "$WS/logs"

set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate megasam
set -u

python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap "kill $MONPID 2>/dev/null || true" EXIT

cd "$REPO"
START=$(date +%s.%N)

# TODO: replace the entrypoint with the actual MegaSaM demo script for your
#       checkout. The upstream README is the source of truth.
python3 -m megasam.demo \
    --image-dir "$IMG_DIR" \
    --config    "$CFG" \
    --output    "$OUT_DIR/trajectory.txt" \
    2>&1 | tee "$LOG"

END=$(date +%s.%N)

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt" 2>/dev/null || echo 0)
python3 -c "
import json
print(json.dumps({'algo':'megasam','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
                  'run_type':'$RUN_TYPE','use_imu':False,'use_lc':False,
                  'duration_s':$DUR,'frames':$NFR,'fps':$NFR/$DUR if $DUR>0 else 0}))
" > "$OUT_DIR/run_meta.json"
echo "[megasam] done (run ${RUN_ID})"
