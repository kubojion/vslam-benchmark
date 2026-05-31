#!/usr/bin/env bash
# Run VINS-Fusion (stereo+IMU+GPS) on a sequence via Docker.
# Usage: scripts/run/run_vins_fusion_gps.sh <dataset> <seq> [run_id=1] [run_type=gnss-vio]
#
# VINS-Fusion fuses GPS loosely on top of the VIO using a separate
# global_fusion_node. Output topics:
#   /vins_estimator/odometry         <- VIO-only odometry
#   /globalEstimator/global_odometry <- after GPS fusion (preferred)
#
# Requires:
#   - Docker; image vslam_vins_fusion:noetic + container 'vins_fusion'
#     created by scripts/setup/setup_vins_fusion_docker.sh
#   - configs/vins_fusion/<dataset>_<seq>.yaml plus per-cam YAMLs.
set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-gnss-vio}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
resolve_run_type "$RUN_TYPE"

if [[ "$RUN_TYPE" != "gnss-vio" ]]; then
    echo "[vins_fusion] only run_type=gnss-vio is supported by this runner" >&2
    exit 2
fi

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/vins_fusion_gps/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_vins_fusion_gps_${RUN_TYPE}_run${RUN_ID}.log"

CONTAINER="vins_fusion"

CFG_HOST_SEQ="$WS/configs/vins_fusion/${DATASET}_${SEQ}.yaml"
CFG_HOST_DSET="$WS/configs/vins_fusion/${DATASET}.yaml"
if [[ -f "$CFG_HOST_SEQ" ]]; then
    CFG_HOST="$CFG_HOST_SEQ"
elif [[ -f "$CFG_HOST_DSET" ]]; then
    CFG_HOST="$CFG_HOST_DSET"
else
    echo "[vins_fusion] missing config: tried $CFG_HOST_SEQ and $CFG_HOST_DSET" >&2
    exit 2
fi
CFG_CONT="/benchmark_configs/vins_fusion/$(basename "$CFG_HOST")"

[[ -d "$SEQ_DIR/mav0/cam0/data" && -d "$SEQ_DIR/mav0/cam1/data" ]] \
    || { echo "[vins_fusion] missing $SEQ_DIR/mav0/cam{0,1}/data" >&2; exit 2; }
[[ -f "$SEQ_DIR/mav0/imu0/data.csv" ]] \
    || { echo "[vins_fusion] missing IMU $SEQ_DIR/mav0/imu0/data.csv" >&2; exit 2; }
[[ -f "$SEQ_DIR/gps.csv" ]] \
    || { echo "[vins_fusion] missing GPS $SEQ_DIR/gps.csv" >&2; exit 2; }

mkdir -p "$OUT_DIR" "$WS/logs"
echo "[vins_fusion] $DATASET/$SEQ run=${RUN_ID} -> $OUT_DIR" | tee "$LOG"

# ---- Ensure container ------------------------------------------------------
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
        docker start "$CONTAINER"
    else
        echo "ERROR: container '$CONTAINER' does not exist." >&2
        echo "Run: bash scripts/setup/setup_vins_fusion_docker.sh" >&2
        exit 2
    fi
fi

python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap "kill $MONPID 2>/dev/null || true" EXIT

DATAROOT_CONT="/datasets/$DATASET/$SEQ"
PLAYER_CONT="/benchmark_scripts/run/gnss_data_player.py"
RECORDER_CONT="/benchmark_scripts/run/odometry_to_tum.py"
TRAJ_CONT="/results-gnss-vio/$DATASET/$SEQ/vins_fusion_gps/run${RUN_ID}/trajectory.txt"

START=$(date +%s.%N)

# ---- Start roscore + vins + global_fusion ---------------------------------
docker exec "$CONTAINER" bash -c "
    set -e
    source /opt/ros/noetic/setup.bash &&
    source /root/catkin_ws/devel/setup.bash &&
    rosparam set /use_sim_time false &&
    roscore &
    sleep 2 &&
    rosrun vins vins_node $CFG_CONT &
    sleep 2 &&
    rosrun global_fusion global_fusion_node &
    sleep 2 &&
    python3 $RECORDER_CONT \
        --topic /globalEstimator/global_odometry \
        --out $TRAJ_CONT \
        --type odom &
    wait
" 2>&1 | tee -a "$LOG" &
NODE_PID=$!

sleep 6

# ---- Run data player (publishes /imu0, /cam{0,1}/image_raw, /gps) ---------
docker exec "$CONTAINER" bash -c "
    source /opt/ros/noetic/setup.bash &&
    python3 $PLAYER_CONT $DATAROOT_CONT \
        --rate 1.0 --start-delay 1.0 --end-wait 5.0 \
        --imu-topic /imu0 \
        --cam0-topic /cam0/image_raw \
        --cam1-topic /cam1/image_raw \
        --gps-topic /gps \
        --gps-cov-xy 1.0 --gps-cov-z 4.0
" 2>&1 | tee -a "$LOG"

# ---- Stop everything ------------------------------------------------------
echo "[vins_fusion] data player done; stopping nodes ..." | tee -a "$LOG"
docker exec "$CONTAINER" bash -c "
    pkill -SIGINT -f vins_node 2>/dev/null || true
    pkill -SIGINT -f global_fusion_node 2>/dev/null || true
    pkill -SIGINT -f odometry_to_tum 2>/dev/null || true
"
sleep 5
docker exec "$CONTAINER" bash -c "
    pkill -SIGKILL -f vins_node 2>/dev/null || true
    pkill -SIGKILL -f global_fusion_node 2>/dev/null || true
    pkill -SIGKILL -f odometry_to_tum 2>/dev/null || true
    pkill -SIGKILL -f roscore 2>/dev/null || true
    pkill -SIGKILL -f rosmaster 2>/dev/null || true
"
wait "$NODE_PID" 2>/dev/null || true

END=$(date +%s.%N)

# ---- Verify trajectory ----------------------------------------------------
if [[ ! -s "$OUT_DIR/trajectory.txt" ]]; then
    echo "[vins_fusion] ERROR: $OUT_DIR/trajectory.txt missing or empty" | tee -a "$LOG"
    exit 1
fi

cp "$LOG" "$OUT_DIR/run_log.txt"

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt")
python3 -c "
import json
print(json.dumps({
    'algo':'vins_fusion_gps','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
    'run_type':'$RUN_TYPE',
    'duration_s':$DUR,'frames':$NFR,
    'fps':$NFR/$DUR if $DUR>0 else 0
}))
" > "$OUT_DIR/run_meta.json"

echo "[vins_fusion] done (run ${RUN_ID})" | tee -a "$LOG"
