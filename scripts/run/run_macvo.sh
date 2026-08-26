#!/usr/bin/env bash
# Run MAC-VO on a sequence.
# Usage: scripts/run/run_macvo.sh <dataset> <seq> [run_id=1] [run_type=vo]
#
# MAC-VO is stereo VO without IMU or LC, so it only makes sense under
# run_type=vo. Unsupported sensor modes are rejected instead of being silently
# routed into a misleading results table.
set -eo pipefail
DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"
if [[ "$RUN_TYPE" != "vo" ]]; then
    echo "[macvo] ERROR: MAC-VO supports only run_type=vo" >&2
    exit 2
fi
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/macvo/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_macvo_${RUN_TYPE}_run${RUN_ID}.log"
# Use the upstream MACVO_Performant config directly
ODOM_CFG="$WS/src/MAC-VO/Config/Experiment/MACVO/MACVO_Performant.yaml"
DATA_CFG_SRC="$WS/configs/macvo/${DATASET}_${SEQ}.yaml"
[[ -f "$DATA_CFG_SRC" ]] || { echo "ERROR: no MAC-VO config for ${DATASET}/${SEQ} at $DATA_CFG_SRC"; exit 2; }
mkdir -p "$WS/logs"
prepare_fresh_run_dir "$OUT_DIR"
# Substitute __WS__ placeholder so configs are portable across machines.
DATA_CFG="$(mktemp -t macvo_cfg_XXXXXX.yaml)"
sed "s|__WS__|$WS|g" "$DATA_CFG_SRC" > "$DATA_CFG"
set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate macvo
set -u

cd "$WS/src/MAC-VO"
prepare_resource_window "$OUT_DIR"
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" --pid "$$" --interval 1 \
    --start-file "$OUT_DIR/.resource_start" --stop-file "$OUT_DIR/.resource_stop" &
MONPID=$!
trap '[[ -n "${MONPID:-}" ]] && kill "$MONPID" 2>/dev/null || true; rm -f "$DATA_CFG"' EXIT

PROV_ARGS=(
    --artifact "odometry_config=$ODOM_CFG"
    --artifact "dataset_config=$DATA_CFG_SRC"
    --artifact "effective_dataset_config=$DATA_CFG"
    --artifact "model=$WS/src/MAC-VO/Model/MACVO_FrontendCov.pth"
    --source "algorithm=$WS/src/MAC-VO"
    --param "use_rerun_viewer=false" --param "matmul_precision=medium"
    --conda-env macvo
)

START=$(date +%s.%N)
mark_resource_start "$OUT_DIR"
set +e
python3 MACVO.py \
    --odom "$ODOM_CFG" \
    --data "$DATA_CFG" \
    --resultRoot "$WS/src/MAC-VO/Results" \
    --noeval \
    2>&1 | tee "$LOG"
MACVO_RC=${PIPESTATUS[0]}
set -e
END=$(date +%s.%N)
finish_resource_window "$OUT_DIR" "$MONPID"
MONPID=""
if (( MACVO_RC != 0 )); then
    record_failed_run_meta "$OUT_DIR/run_meta.json" macvo "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" "$MACVO_RC" "estimator exited nonzero" "${PROV_ARGS[@]}"
    exit "$MACVO_RC"
fi

# MAC-VO writes to Results/<project_name>/<timestr>/
# Only consider sandbox dirs created/modified after this run started
SBX=$(find "$WS/src/MAC-VO/Results" -mindepth 2 -maxdepth 2 -type d -newer "$DATA_CFG" 2>/dev/null | sort -t/ -k8 | tail -n1)
if [[ ! -d "$SBX" ]]; then
    record_failed_run_meta "$OUT_DIR/run_meta.json" macvo "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" 1 "result sandbox was not produced" "${PROV_ARGS[@]}"
    echo "no Results space produced"
    exit 1
fi
python3 "$WS/scripts/eval/_macvo_to_tum.py" "$SBX" "$OUT_DIR/trajectory.txt"

# If times.txt exists (nanosecond timestamps), replace fake frame-index timestamps
TIMES="$WS/datasets/$DATASET/$SEQ/times.txt"
if [[ -f "$TIMES" ]]; then
    python3 - "$OUT_DIR/trajectory.txt" "$TIMES" <<'PYEOF'
import sys
traj, times_file = sys.argv[1], sys.argv[2]
ts = [float(t)/1e9 for t in open(times_file).read().split()]
lines = open(traj).readlines()
if len(lines) > len(ts):
    raise SystemExit(f"trajectory has {len(lines)} poses but only {len(ts)} timestamps")
with open(traj, "w") as f:
    for i, line in enumerate(lines):
        parts = line.split(); parts[0] = f"{ts[i]:.9f}"
        f.write(" ".join(parts) + "\n")
PYEOF
fi

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt" 2>/dev/null || echo 0)
python3 -c "
import json
print(json.dumps({'algo':'macvo','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
                  'run_type':'$RUN_TYPE','use_imu':False,'use_lc':False,
                  'duration_s':$DUR,'frames':$NFR,'fps':$NFR/$DUR if $DUR>0 else 0,
                  'sandbox':'Results/' + '$SBX'.split('/Results/', 1)[-1]}))
" > "$OUT_DIR/run_meta.json"
enrich_run_meta "$OUT_DIR/run_meta.json" --measurement-mode max_throughput "${PROV_ARGS[@]}"
echo "[macvo] done (run ${RUN_ID})"
