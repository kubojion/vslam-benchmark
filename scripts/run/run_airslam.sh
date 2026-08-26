#!/usr/bin/env bash
# Run AirSLAM (stereo VO / V-SLAM / VI-SLAM) on a sequence via Docker.
# Usage: scripts/run/run_airslam.sh <dataset> <seq> [run_id=1] [run_type=vo]
#
# run_type selects results tree AND launch file:
#   vo      -> results/vo/.../airslam/run<N>/       launch=vo_euroc.launch        cfg=<dataset>_vo.yaml
#   vo-lc   -> results/vo-lc/.../airslam/run<N>/    launch=vo_euroc.launch        cfg=<dataset>_vo_lc.yaml + map_refinement
#   vio     -> results/vio/.../airslam/run<N>/      launch=vio_euroc.launch       cfg=<dataset>_vio.yaml      (requires IMU)
#   vio-lc  -> results/vio-lc/.../airslam/run<N>/   launch=vio_euroc.launch       cfg=<dataset>_vio_slam.yaml + map_refinement (full V-SLAM with LC)
#
# Requires:
#   - Docker with nvidia-container-toolkit (see docs/setup.md)
#   - Docker image xukuanhit/air_slam:v4 pulled and container built
#     (run: bash scripts/setup/setup_airslam_docker.sh)
#   - configs/airslam/<dataset>_camera.yaml      (VO mode, use_imu: 0)
#   - configs/airslam/<dataset>_camera_vio.yaml  (VIO/VIO-LC mode, use_imu: 1) - if it exists
#   - configs/airslam/<dataset>_camera_vo.yaml   (VO override, use_imu: 0) - if it exists
#   - configs/airslam/<dataset>_<vo|vo_lc|vio|vio_slam>.yaml
#   - configs/airslam/<dataset>_mr.yaml          (VO-LC / VIO-LC map_refinement params)
#
# Dataset layout expected under datasets/<dataset>/<seq>/mav0/:
#   cam0/data/*.png   (images named by nanosecond timestamp)
#   cam1/data/*.png
#   cam0/data.csv     (EuRoC manifest: #timestamp [ns],filename)
#   cam1/data.csv
#   imu0/data.csv     (required for vio / vio-lc)
set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"

case "$RUN_TYPE" in
    vo)      LAUNCH_FILE="vo_euroc.launch";       CFG_TAG="vo" ;;
    vo-lc)   LAUNCH_FILE="vo_euroc.launch";       CFG_TAG="vo_lc" ;;
    vio)     LAUNCH_FILE="vio_euroc.launch";      CFG_TAG="vio" ;;
    vio-lc)  LAUNCH_FILE="vio_euroc.launch";      CFG_TAG="vio_slam" ;;
    *)       echo "[airslam] unknown run_type: $RUN_TYPE (expected vo|vo-lc|vio|vio-lc)" >&2; exit 2 ;;
esac

# Loop closure is performed by the separate map_refinement stage below.  The
# odometry sensor profile is therefore shared between VIO and VIO-LC when a
# duplicated *_vio_slam.yaml is not present (currently the ZED2i profile).
PROFILE_TAG="$CFG_TAG"
if [[ "$RUN_TYPE" == "vio-lc" \
      && ! -f "$WS/configs/airslam/${DATASET}_${PROFILE_TAG}.yaml" ]]; then
    PROFILE_TAG="vio"
fi

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/airslam/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_airslam_${RUN_TYPE}_run${RUN_ID}.log"

# Paths inside the Docker container (via volume mounts in the container)
# For VIO/VIO-LC, use a separate camera config with use_imu: 1 if one exists.
if [[ "$USE_IMU" == "true" && -f "$WS/configs/airslam/${DATASET}_camera_vio.yaml" ]]; then
    CAM_CFG="/benchmark_configs/airslam/${DATASET}_camera_vio.yaml"
elif [[ "$USE_IMU" == "false" && -f "$WS/configs/airslam/${DATASET}_camera_vo.yaml" ]]; then
    CAM_CFG="/benchmark_configs/airslam/${DATASET}_camera_vo.yaml"
else
    CAM_CFG="/benchmark_configs/airslam/${DATASET}_camera.yaml"
fi
VO_CFG="/benchmark_configs/airslam/${DATASET}_${PROFILE_TAG}.yaml"
DATAROOT="/datasets/$DATASET/$SEQ/mav0"
CONT_RESULTS_DIR="/results/$RUN_TYPE"
SAVING_DIR="${CONT_RESULTS_DIR}/$DATASET/$SEQ/airslam/run${RUN_ID}"
MODEL_DIR="/root/catkin_ws/src/air_slam/output"

CONTAINER="air_slam"

CAM_CFG_HOST="$WS/configs/airslam/$(basename "$CAM_CFG")"
VO_CFG_HOST="$WS/configs/airslam/${DATASET}_${PROFILE_TAG}.yaml"
[[ -f "$CAM_CFG_HOST" ]] || {
    echo "ERROR: no AirSLAM camera config at $CAM_CFG_HOST"; exit 2; }
[[ -f "$VO_CFG_HOST" ]] || {
    echo "ERROR: no AirSLAM ${PROFILE_TAG} config at configs/airslam/${DATASET}_${PROFILE_TAG}.yaml"; exit 2; }
if [[ "$USE_LC" == "true" && ! -f "$WS/configs/airslam/${DATASET}_mr.yaml" ]]; then
    echo "ERROR: no AirSLAM map-refinement config at configs/airslam/${DATASET}_mr.yaml"; exit 2;
fi
ENGINE_NAME=$(awk '/^[[:space:]]*engine_file:/ {print $2; exit}' "$VO_CFG_HOST" | tr -d "\"'")
[[ -n "$ENGINE_NAME" ]] || { echo "ERROR: no engine_file in $VO_CFG_HOST" >&2; exit 2; }
ENGINE_HOST="$WS/src/airslam/output/$ENGINE_NAME"
PROV_ARGS=(
    --artifact "camera_config=$CAM_CFG_HOST"
    --artifact "odometry_config=$VO_CFG_HOST"
    --source "algorithm=$WS/src/airslam"
    --param "use_imu=$USE_IMU" --param "use_lc=$USE_LC"
    --param "playback_rate=offline"
    --container "$CONTAINER"
)
if [[ "$USE_LC" == "true" ]]; then
    PROV_ARGS+=(--artifact "map_refinement_config=$WS/configs/airslam/${DATASET}_mr.yaml")
fi
[[ -d "$SEQ_DIR/mav0/cam0/data" ]] || {
    echo "ERROR: missing EuRoC image folder $SEQ_DIR/mav0/cam0/data"; exit 2; }
if [[ "$USE_IMU" == "true" && ! -f "$SEQ_DIR/mav0/imu0/data.csv" ]]; then
    echo "ERROR: $RUN_TYPE requires $SEQ_DIR/mav0/imu0/data.csv (run IMU extraction)"; exit 2;
fi

mkdir -p "$WS/logs"
prepare_fresh_run_dir "$OUT_DIR"
rm -f "$OUT_DIR/trajectory.txt" "$OUT_DIR/trajectory_v0.txt" "$OUT_DIR/trajectory_v1.txt"

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

MOUNT_DEST="/results"
if ! docker inspect -f '{{range .Mounts}}{{println .Destination}}{{end}}' "$CONTAINER" | grep -qx "$MOUNT_DEST"; then
    echo "[airslam] ERROR: container '$CONTAINER' is missing mount $MOUNT_DEST" >&2
    echo "[airslam] recreate it so $RESULTS_ROOT is mounted before running $RUN_TYPE" >&2
    exit 2
fi

# ---- Resource monitor (host-side) -----------------------------------------
prepare_resource_window "$OUT_DIR"
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" --container "$CONTAINER" --interval 1 \
    --start-file "$OUT_DIR/.resource_start" --stop-file "$OUT_DIR/.resource_stop" &
MONPID=$!
trap '[[ -n "${MONPID:-}" ]] && kill "$MONPID" 2>/dev/null || true' EXIT

# ---- Run AirSLAM inside container -----------------------------------------
# roslaunch (ROS1) does not auto-exit when processing finishes because the node
# is not marked required="true". We run docker exec in the background, poll for
# trajectory_v0.txt (written by visual_odometry.cpp after all frames), then send
# SIGINT to roslaunch inside the container to shut it down cleanly.
START=$(date +%s.%N)
mark_resource_start "$OUT_DIR"

docker exec "$CONTAINER" bash -c "
    source /opt/ros/noetic/setup.bash &&
    source /root/catkin_ws/devel/setup.bash &&
    mkdir -p '$SAVING_DIR' &&
    roslaunch air_slam $LAUNCH_FILE \
        dataroot:='$DATAROOT' \
        camera_config_path:='$CAM_CFG' \
        config_path:='$VO_CFG' \
        model_dir:='$MODEL_DIR' \
        saving_dir:='$SAVING_DIR' \
        visualization:=false
" 2>&1 | tee "$LOG" &
EXEC_PID=$!

# Wait for trajectory_v0.txt to appear. AirSLAM creates it after processing all
# frames; it can be empty when the estimator fails to initialise.
TRAJ_HOST="$OUT_DIR/trajectory_v0.txt"
echo "[airslam] waiting for trajectory_v0.txt ..."
while [[ ! -e "$TRAJ_HOST" ]]; do
    sleep 5
    if ! kill -0 "$EXEC_PID" 2>/dev/null; then break; fi  # exited early (crash)
done

# Stop roslaunch (it won't exit on its own after processing)
if kill -0 "$EXEC_PID" 2>/dev/null; then
    echo "[airslam] trajectory saved, stopping roslaunch..."
    docker exec "$CONTAINER" bash -c "pkill -SIGINT -f roslaunch 2>/dev/null || true"
    sleep 3
    wait "$EXEC_PID" 2>/dev/null || true
fi

# ---- Locate trajectory output from saving_dir -----------------------------
# visual_odometry.cpp writes trajectory_v0.txt (TUM format, timestamps in SECONDS).
# For LC run types: run map_refinement (step 2) which reads the saved map and
# produces trajectory_v1.txt (globally consistent poses after LC).
if [[ "$USE_LC" == "true" && -s "$TRAJ_HOST" ]]; then
    MR_CFG="/benchmark_configs/airslam/${DATASET}_mr.yaml"
    VOC_PATH="/root/catkin_ws/src/air_slam/voc/point_voc_L4.bin"
    echo "[airslam] running map_refinement (step 2 of ${RUN_TYPE})..."
    docker exec "$CONTAINER" bash -c "
        source /opt/ros/noetic/setup.bash &&
        source /root/catkin_ws/devel/setup.bash &&
        roslaunch air_slam mr_euroc.launch \
            map_root:='$SAVING_DIR' \
            config_path:='$MR_CFG' \
            model_dir:='$MODEL_DIR' \
            voc_path:='$VOC_PATH' \
            visualization:=false
    " 2>&1 | tee -a "$LOG" &
    MR_PID=$!
    MR_TRAJ="$OUT_DIR/trajectory_v1.txt"
    echo "[airslam] waiting for trajectory_v1.txt ..."
    while [[ ! -s "$MR_TRAJ" ]]; do
        sleep 5
        if ! kill -0 "$MR_PID" 2>/dev/null; then break; fi
    done
    if kill -0 "$MR_PID" 2>/dev/null; then
        docker exec "$CONTAINER" bash -c "pkill -SIGINT -f roslaunch 2>/dev/null || true"
        sleep 3
        wait "$MR_PID" 2>/dev/null || true
    fi
fi

END=$(date +%s.%N)
finish_resource_window "$OUT_DIR" "$MONPID"
MONPID=""

# Rename to trajectory.txt for consistency with other runners.
# For LC run types use trajectory_v1.txt (post-LC) if available, else fall back to v0.
if [[ "$USE_LC" == "true" && -s "$OUT_DIR/trajectory_v1.txt" ]]; then
    RAW_TRAJ="$OUT_DIR/trajectory_v1.txt"
else
    RAW_TRAJ="$OUT_DIR/trajectory_v0.txt"
fi
if [[ ! -s "$RAW_TRAJ" ]]; then
    FAILED_PROV=("${PROV_ARGS[@]}")
    [[ -f "$ENGINE_HOST" ]] && FAILED_PROV+=(--artifact "tensorrt_engine=$ENGINE_HOST")
    record_failed_run_meta "$OUT_DIR/run_meta.json" airslam "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" 1 "trajectory was not produced" "${FAILED_PROV[@]}"
    echo "ERROR: no non-empty trajectory found in $OUT_DIR after AirSLAM run" >&2
    echo "Files in output dir:" >&2
    ls "$OUT_DIR" >&2
    exit 1
fi

# Timestamps are already in seconds (AirSLAM parses ns filenames to double seconds).
mv -f "$RAW_TRAJ" "$OUT_DIR/trajectory.txt"
[[ -f "$ENGINE_HOST" ]] || { echo "ERROR: TensorRT engine missing after run: $ENGINE_HOST" >&2; exit 1; }
PROV_ARGS+=(--artifact "tensorrt_engine=$ENGINE_HOST")

cp "$LOG" "$OUT_DIR/run_log.txt"

DUR=$(python3 -c "print($END-$START)")
# Use total input frames (count images in cam0/data) to compute processing FPS.
# AirSLAM only outputs keyframe poses in trajectory.txt, which is a subset.
# Count poses in the produced trajectory (keyframes). The old approach counted
# input mav0/cam0/data/*.png, which breaks on datasets that store images
# elsewhere or as .jpg (e.g. zed2i, cam0/*.jpg, no mav0/) -- the empty glob
# piped to wc gave frames=0 and corrupted run_meta.json.
NFR=$(wc -l < "$OUT_DIR/trajectory.txt" 2>/dev/null || echo 0)
python3 -c "
import json
print(json.dumps({'algo':'airslam','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
                  'run_type':'$RUN_TYPE',
                  'use_imu':$([[ "$USE_IMU" == "true" ]] && echo True || echo False),
                  'use_lc':$([[ "$USE_LC" == "true" ]] && echo True || echo False),
                  'duration_s':$DUR,'frames':$NFR,'fps':$NFR/$DUR if $DUR>0 else 0}))
" > "$OUT_DIR/run_meta.json"
enrich_run_meta "$OUT_DIR/run_meta.json" --measurement-mode max_throughput "${PROV_ARGS[@]}"

echo "[airslam] done (run ${RUN_ID})"
