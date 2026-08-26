#!/usr/bin/env bash
# Run OV2SLAM in stereo VO or stereo VO-LC mode through ROS 1 Docker.
# Usage: scripts/run/run_ov2slam.sh <dataset> <seq> [run_id=1] [run_type=vo]
set -euo pipefail

DATASET=$1
SEQ=$2
RUN_ID=${3:-1}
RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"

if [[ "$RUN_TYPE" != "vo" && "$RUN_TYPE" != "vo-lc" ]]; then
    echo "[ov2slam] supported run types: vo, vo-lc" >&2
    exit 2
fi

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/ov2slam/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_ov2slam_${RUN_TYPE}_run${RUN_ID}.log"
CONTAINER="ov2slam"
MODE=${RUN_TYPE//-/_}

CFG_SEQ="$WS/configs/ov2slam/${DATASET}_${SEQ}_${MODE}.yaml"
CFG_DATASET="$WS/configs/ov2slam/${DATASET}_${MODE}.yaml"
if [[ -n "${OV2SLAM_CONFIG:-}" ]]; then
    CFG_HOST="$OV2SLAM_CONFIG"
    [[ "$CFG_HOST" = /* ]] || CFG_HOST="$WS/$CFG_HOST"
elif [[ -f "$CFG_SEQ" ]]; then
    CFG_HOST="$CFG_SEQ"
else
    CFG_HOST="$CFG_DATASET"
fi
[[ -f "$CFG_HOST" ]] || {
    echo "[ov2slam] missing config: tried $CFG_SEQ and $CFG_DATASET" >&2
    exit 2
}

EXPECTED_LC=0
[[ "$USE_LC" == "true" ]] && EXPECTED_LC=1
CONFIG_LC=$(awk '/^[[:space:]]*buse_loop_closer:/ { print $2; exit }' "$CFG_HOST")
if [[ "$CONFIG_LC" != "$EXPECTED_LC" ]]; then
    echo "[ov2slam] config/run-type LC mismatch: config=$CONFIG_LC expected=$EXPECTED_LC" >&2
    exit 2
fi

[[ -d "$SEQ_DIR/mav0/cam0/data" && -d "$SEQ_DIR/mav0/cam1/data" ]] || {
    echo "[ov2slam] missing $SEQ_DIR/mav0/cam{0,1}/data" >&2
    exit 2
}
[[ -f "$SEQ_DIR/mav0/cam0/data.csv" && -f "$SEQ_DIR/mav0/cam1/data.csv" ]] || {
    echo "[ov2slam] missing stereo data.csv files" >&2
    exit 2
}

if [[ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null || true)" != "true" ]]; then
    if docker inspect "$CONTAINER" &>/dev/null; then
        docker start "$CONTAINER"
    else
        echo "ERROR: container '$CONTAINER' does not exist." >&2
        echo "Run: bash scripts/setup/setup_ov2slam_docker.sh" >&2
        exit 2
    fi
fi

mkdir -p "$WS/logs"
prepare_fresh_run_dir "$OUT_DIR"
rm -f "$OUT_DIR"/ov2slam_*.txt "$OUT_DIR/trajectory.txt" "$OUT_DIR/run_log.txt"
echo "[ov2slam] $DATASET/$SEQ run=$RUN_ID type=$RUN_TYPE -> $OUT_DIR" | tee "$LOG"

CFG_CONT="/benchmark_configs/ov2slam/$(basename "$CFG_HOST")"
DATA_CONT="/datasets/$DATASET/$SEQ"
OUT_CONT="/results/$RUN_TYPE/$DATASET/$SEQ/ov2slam/run${RUN_ID}"
PLAYER_CONT="/benchmark_scripts/run/ov2slam_data_player.py"

if ! docker inspect -f '{{range .Mounts}}{{println .Destination}}{{end}}' "$CONTAINER" | grep -qx /results; then
    echo "[ov2slam] ERROR: container '$CONTAINER' is missing the /results mount" >&2
    echo "[ov2slam] recreate it with scripts/setup/setup_ov2slam_docker.sh" >&2
    exit 2
fi

MONPID=""
ROSCORE_PID=""
NODE_PID=""
cleanup() {
    [[ -n "$MONPID" ]] && kill "$MONPID" 2>/dev/null || true
    docker exec "$CONTAINER" bash -c \
        "pkill -SIGINT -f '[o]v2slam_node' 2>/dev/null || true; \
         pkill -f '[r]oscore' 2>/dev/null || true; \
         pkill -f '[r]osmaster' 2>/dev/null || true" 2>/dev/null || true
    [[ -n "$NODE_PID" ]] && kill "$NODE_PID" 2>/dev/null || true
    [[ -n "$ROSCORE_PID" ]] && kill "$ROSCORE_PID" 2>/dev/null || true
}
trap cleanup EXIT

python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!

docker exec "$CONTAINER" bash -c "
    source /opt/ros/noetic/setup.bash
    exec roscore
" >> "$LOG" 2>&1 &
ROSCORE_PID=$!

for _ in $(seq 1 15); do
    if docker exec "$CONTAINER" bash -c \
        "source /opt/ros/noetic/setup.bash && rostopic list" &>/dev/null; then
        break
    fi
    sleep 1
done
docker exec "$CONTAINER" bash -c \
    "source /opt/ros/noetic/setup.bash && rostopic list" &>/dev/null || {
    echo "[ov2slam] roscore did not become ready" | tee -a "$LOG"
    exit 1
}

START=$(date +%s.%N)
docker exec "$CONTAINER" bash -c "
    set -e
    source /opt/ros/noetic/setup.bash
    source /root/catkin_ws/devel/setup.bash
    cd '$OUT_CONT'
    exec rosrun ov2slam ov2slam_node '$CFG_CONT'
" 2>&1 | tee -a "$LOG" &
NODE_PID=$!

sleep 3
kill -0 "$NODE_PID" 2>/dev/null || {
    echo "[ov2slam] node exited before playback" | tee -a "$LOG"
    exit 1
}

docker exec "$CONTAINER" bash -c "
    source /opt/ros/noetic/setup.bash
    exec python3 '$PLAYER_CONT' '$DATA_CONT' \
        --rate '${OV2SLAM_PLAYBACK_RATE:-1.0}' --start-delay 1.0 --end-wait 1.0
" 2>&1 | tee -a "$LOG"

RAW="$OUT_DIR/ov2slam_traj.txt"
LC_OPT="$OUT_DIR/ov2slam_full_traj_wlc_opt.txt"
TARGET="$RAW"
[[ "$USE_LC" == "true" ]] && TARGET="$LC_OPT"

TIMEOUT=${OV2SLAM_FINISH_TIMEOUT:-180}
for _ in $(seq 1 "$TIMEOUT"); do
    [[ -s "$TARGET" ]] && break
    kill -0 "$NODE_PID" 2>/dev/null || break
    sleep 1
done

if [[ ! -s "$TARGET" ]] && kill -0 "$NODE_PID" 2>/dev/null; then
    echo "[ov2slam] finish timeout after ${TIMEOUT}s" | tee -a "$LOG"
    docker exec "$CONTAINER" bash -c \
        "pkill -SIGINT -f '[o]v2slam_node' 2>/dev/null || true" || true
fi
wait "$NODE_PID" 2>/dev/null || true
END=$(date +%s.%N)

if [[ ! -s "$RAW" ]]; then
    echo "[ov2slam] no raw trajectory produced" | tee -a "$LOG"
    exit 1
fi

if [[ "$USE_LC" == "true" ]]; then
    if [[ ! -s "$LC_OPT" ]]; then
        echo "[ov2slam] no optimized loop-closed trajectory produced" | tee -a "$LOG"
        exit 1
    fi
    python3 "$WS/scripts/run/ov2slam_to_tum.py" \
        "$RAW" "$LC_OPT" "$OUT_DIR/trajectory.txt" | tee -a "$LOG"
else
    cp "$RAW" "$OUT_DIR/trajectory.txt"
fi

cp "$LOG" "$OUT_DIR/run_log.txt"
kill "$MONPID" 2>/dev/null || true
MONPID=""

DURATION=$(python3 -c "print($END - $START)")
FRAMES=$(wc -l < "$OUT_DIR/trajectory.txt")
FRAMES_TOTAL=$(awk 'BEGIN{n=0} $1 !~ /^#/ && NF {n++} END{print n}' \
    "$SEQ_DIR/mav0/cam0/data.csv")
python3 - "$OUT_DIR/run_meta.json" <<PY
import json
from pathlib import Path

meta = {
    "algo": "ov2slam",
    "dataset": "$DATASET",
    "seq": "$SEQ",
    "run_id": int("$RUN_ID"),
    "run_type": "$RUN_TYPE",
    "use_imu": False,
    "use_lc": $([[ "$USE_LC" == "true" ]] && echo True || echo False),
    "duration_s": float("$DURATION"),
    "frames": int("$FRAMES"),
    "frames_total": int("$FRAMES_TOTAL"),
}
meta["fps"] = meta["frames"] / meta["duration_s"] if meta["duration_s"] else 0.0
Path("$OUT_DIR/run_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
PY
python3 "$(dirname "$0")/_enrich_run_meta.py" "$OUT_DIR/run_meta.json" \
    --config "${OV2SLAM_CONFIG:-}" --container "${CONTAINER:-}" \
    --playback-rate "${OV2SLAM_PLAYBACK_RATE:-}" || true

echo "[ov2slam] done: $FRAMES/$FRAMES_TOTAL poses" | tee -a "$LOG"
