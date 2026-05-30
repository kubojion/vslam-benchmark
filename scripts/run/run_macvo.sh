#!/usr/bin/env bash
# Run MAC-VO on a sequence.
# Usage: scripts/run/run_macvo.sh <dataset> <seq> [run_id=1] [run_type=vo]
#
# MAC-VO is monocular VO without IMU or LC, so it only makes sense under
# run_type=vo. The flag is accepted for uniformity but vio / vio-lc will
# print a warning and still run vision-only.
set -eo pipefail
DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
resolve_run_type "$RUN_TYPE"
if [[ "$RUN_TYPE" != "vo" ]]; then
    echo "[macvo] WARNING: MAC-VO has no IMU / LC support; routing output to $RESULTS_ROOT anyway" >&2
fi
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/macvo/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_macvo_${RUN_TYPE}_run${RUN_ID}.log"
# Use the upstream MACVO_Performant config directly
ODOM_CFG="$WS/src/MAC-VO/Config/Experiment/MACVO/MACVO_Performant.yaml"
DATA_CFG_SRC="$WS/configs/macvo/${DATASET}_${SEQ}.yaml"
[[ -f "$DATA_CFG_SRC" ]] || { echo "ERROR: no MAC-VO config for ${DATASET}/${SEQ} at $DATA_CFG_SRC"; exit 2; }
mkdir -p "$OUT_DIR" "$WS/logs"
# Substitute __WS__ placeholder so configs are portable across machines.
DATA_CFG="$(mktemp -t macvo_cfg_XXXXXX.yaml)"
sed "s|__WS__|$WS|g" "$DATA_CFG_SRC" > "$DATA_CFG"
set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate macvo
set -u

cd "$WS/src/MAC-VO"
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap 'kill $MONPID 2>/dev/null || true; rm -f "$DATA_CFG"' EXIT

START=$(date +%s.%N)
python3 MACVO.py \
    --odom "$ODOM_CFG" \
    --data "$DATA_CFG" \
    --resultRoot "$WS/src/MAC-VO/Results" \
    --useRR \
    --noeval \
    2>&1 | tee "$LOG"
END=$(date +%s.%N)

# MAC-VO writes to Results/<project_name>/<timestr>/
# Only consider sandbox dirs created/modified after this run started
SBX=$(find "$WS/src/MAC-VO/Results" -mindepth 2 -maxdepth 2 -type d -newer "$DATA_CFG" 2>/dev/null | sort -t/ -k8 | tail -n1)
[[ -d "$SBX" ]] || { echo "no Results space produced"; exit 1; }
python3 "$WS/scripts/eval/_macvo_to_tum.py" "$SBX" "$OUT_DIR/trajectory.txt"

# If times.txt exists (nanosecond timestamps), replace fake frame-index timestamps
TIMES="$WS/datasets/$DATASET/$SEQ/times.txt"
if [[ -f "$TIMES" ]]; then
    python3 - "$OUT_DIR/trajectory.txt" "$TIMES" <<'PYEOF'
import sys
traj, times_file = sys.argv[1], sys.argv[2]
ts = [float(t)/1e9 for t in open(times_file).read().split()]
lines = open(traj).readlines()
with open(traj, "w") as f:
    for i, line in enumerate(lines):
        if i >= len(ts): break  # trajectory longer than times.txt - stop here
        parts = line.split(); parts[0] = f"{ts[i]:.9f}"
        f.write(" ".join(parts) + "\n")
PYEOF
fi

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt" 2>/dev/null || echo 0)
python3 -c "
import json
print(json.dumps({'algo':'macvo','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
                  'duration_s':$DUR,'frames':$NFR,'fps':$NFR/$DUR if $DUR>0 else 0,
                  'sandbox':'$SBX'}))
" > "$OUT_DIR/run_meta.json"
echo "[macvo] done (run ${RUN_ID})"
