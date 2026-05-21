#!/usr/bin/env bash
# Run AirSLAM (stereo VO) on a sequence via Docker.
# Usage: scripts/run/run_airslam.sh <dataset> <seq> [run_id=1]
#
# Requires:
#   - Docker with nvidia-container-toolkit (see docs/setup.md)
#   - Docker image xukuanhit/air_slam:v4 pulled and container built
#     (run: bash scripts/setup/setup_airslam_docker.sh)
#   - configs/airslam/<dataset>_camera.yaml
#   - configs/airslam/<dataset>_vo.yaml
#
# Dataset layout expected under datasets/<dataset>/<seq>/mav0/:
#   cam0/data/*.png   (images named by nanosecond timestamp)
#   cam1/data/*.png
#   cam0/data.csv     (EuRoC manifest: #timestamp [ns],filename)
#   cam1/data.csv
set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}
WS=$(cd "$(dirname "$0")/../.." && pwd)
SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$WS/results/$DATASET/$SEQ/airslam/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_airslam_run${RUN_ID}.log"

# Paths inside the Docker container (via volume mounts in the container)
CAM_CFG="/benchmark_configs/airslam/${DATASET}_camera.yaml"
VO_CFG="/benchmark_configs/airslam/${DATASET}_vo.yaml"
DATAROOT="/datasets/$DATASET/$SEQ/mav0"
SAVING_DIR="/results/$DATASET/$SEQ/airslam/run${RUN_ID}"
MODEL_DIR="/root/catkin_ws/src/air_slam/output"

CONTAINER="air_slam"

[[ -f "$WS/configs/airslam/${DATASET}_camera.yaml" ]] || {
    echo "ERROR: no AirSLAM camera config for ${DATASET} at configs/airslam/${DATASET}_camera.yaml"; exit 2; }
[[ -f "$WS/configs/airslam/${DATASET}_vo.yaml" ]] || {
    echo "ERROR: no AirSLAM VO config for ${DATASET} at configs/airslam/${DATASET}_vo.yaml"; exit 2; }
[[ -d "$SEQ_DIR/mav0/cam0/data" ]] || {
    echo "ERROR: missing EuRoC image folder $SEQ_DIR/mav0/cam0/data"; exit 2; }

mkdir -p "$OUT_DIR" "$WS/logs"

# ---- Ensure Docker container is running -----------------------------------
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
        echo "[airslam] starting existing container $CONTAINER..."
        docker start "$CONTAINER"
    else
        echo "[airslam] creating container $CONTAINER from xukuanhit/air_slam:v4..."
        docker run -d \
            --runtime nvidia --gpus all \
            --volume "$WS/src/airslam:/root/catkin_ws/src/air_slam" \
            --volume "$WS/datasets:/datasets:ro" \
            --volume "$WS/results:/results" \
            --volume "$WS/configs:/benchmark_configs:ro" \
            --name "$CONTAINER" \
            xukuanhit/air_slam:v4 /bin/bash -c "tail -f /dev/null"
        echo "[airslam] waiting for container to initialise..."
        sleep 3
    fi
fi

# ---- Resource monitor (host-side) -----------------------------------------
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap "kill $MONPID 2>/dev/null || true" EXIT

# ---- Run AirSLAM inside container -----------------------------------------
START=$(date +%s.%N)
docker exec "$CONTAINER" bash -c "
    source /opt/ros/noetic/setup.bash &&
    source /root/catkin_ws/devel/setup.bash &&
    mkdir -p '$SAVING_DIR' &&
    roslaunch air_slam vo_euroc.launch \
        dataroot:='$DATAROOT' \
        camera_config_path:='$CAM_CFG' \
        config_path:='$VO_CFG' \
        model_dir:='$MODEL_DIR' \
        saving_dir:='$SAVING_DIR' \
        visualization:=false
" 2>&1 | tee "$LOG"
END=$(date +%s.%N)

# ---- Locate trajectory output from saving_dir -----------------------------
# AirSLAM writes keyframe_trajectory.txt (TUM, timestamps already in SECONDS)
# to saving_dir. Rename to trajectory.txt for consistency with other runners.
RAW_TRAJ="$OUT_DIR/keyframe_trajectory.txt"
if [[ ! -f "$RAW_TRAJ" ]]; then
    echo "ERROR: no keyframe_trajectory.txt found in $OUT_DIR after AirSLAM run" >&2
    echo "Files in output dir:" >&2
    ls "$OUT_DIR" >&2
    exit 1
fi

# Timestamps are already in seconds (AirSLAM parses ns filenames to double seconds).
# Just rename to the standard trajectory.txt name.
mv "$RAW_TRAJ" "$OUT_DIR/trajectory.txt"

cp "$LOG" "$OUT_DIR/run_log.txt"

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt" 2>/dev/null || echo 0)
python3 -c "
import json
print(json.dumps({'algo':'airslam','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
                  'duration_s':$DUR,'frames':$NFR,'fps':$NFR/$DUR if $DUR>0 else 0}))
" > "$OUT_DIR/run_meta.json"

echo "[airslam] done (run ${RUN_ID})"
