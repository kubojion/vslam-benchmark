#!/usr/bin/env bash
# Run CIFASIS GNSS-Stereo-Inertial Fusion on a sequence via Docker.
# Usage: scripts/run/run_cifasis_gnss_si.sh <dataset> <seq> [run_id=1] [run_type=gnss-vio]
#
# CIFASIS GNSS-SI is a tightly-coupled GNSS+stereo+IMU SLAM built on
# ORB-SLAM3. Loop closure is enabled by default; run_type must be gnss-vio.
#
# Requires:
#   - Docker; image vslam_cifasis_gnss_si:noetic + container 'cifasis_gnss_si'
#     created by scripts/setup/setup_cifasis_gnss_si_docker.sh
#   - configs/cifasis_gnss_si/<dataset>_<seq>.yaml (sequence-specific YAML;
#     falls back to <dataset>.yaml).
#
# Topic remappings inside container (CIFASIS subscribes to):
#   /camera/left/image_raw    <-  /stereo/left/image_raw
#   /camera/right/image_raw   <-  /stereo/right/image_raw
#   /imu                      <-  /imu
#   /gps/fix                  <-  /gps/fix
#
# Trajectory output: $HOME/.ros/CameraTrajectoryGPSOpt.txt (TUM format).
set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-gnss-vio}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"

if [[ "$RUN_TYPE" != "gnss-vio" ]]; then
    echo "[cifasis_gnss_si] only run_type=gnss-vio is supported" >&2
    exit 2
fi

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/cifasis_gnss_si/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_cifasis_gnss_si_${RUN_TYPE}_run${RUN_ID}.log"

CONTAINER="cifasis_gnss_si"

CFG_HOST_SEQ="$WS/configs/cifasis_gnss_si/${DATASET}_${SEQ}.yaml"
CFG_HOST_DSET="$WS/configs/cifasis_gnss_si/${DATASET}.yaml"
if [[ -f "$CFG_HOST_SEQ" ]]; then
    CFG_HOST="$CFG_HOST_SEQ"
elif [[ -f "$CFG_HOST_DSET" ]]; then
    CFG_HOST="$CFG_HOST_DSET"
else
    echo "[cifasis_gnss_si] missing config: tried $CFG_HOST_SEQ and $CFG_HOST_DSET" >&2
    exit 2
fi
CFG_CONT="/benchmark_configs/cifasis_gnss_si/$(basename "$CFG_HOST")"

[[ -d "$SEQ_DIR/mav0/cam0/data" && -d "$SEQ_DIR/mav0/cam1/data" ]] \
    || { echo "[cifasis_gnss_si] missing $SEQ_DIR/mav0/cam{0,1}/data" >&2; exit 2; }
[[ -f "$SEQ_DIR/mav0/imu0/data.csv" ]] \
    || { echo "[cifasis_gnss_si] missing IMU $SEQ_DIR/mav0/imu0/data.csv" >&2; exit 2; }
[[ -f "$SEQ_DIR/gps.csv" ]] \
    || { echo "[cifasis_gnss_si] missing GPS $SEQ_DIR/gps.csv" >&2; exit 2; }

mkdir -p "$OUT_DIR" "$WS/logs"
echo "[cifasis_gnss_si] $DATASET/$SEQ run=${RUN_ID} -> $OUT_DIR" | tee "$LOG"
echo "[cifasis_gnss_si] config: $CFG_HOST" | tee -a "$LOG"

# ---- Ensure container is running ------------------------------------------
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
        docker start "$CONTAINER"
    else
        echo "ERROR: container '$CONTAINER' does not exist." >&2
        echo "Run: bash scripts/setup/setup_cifasis_gnss_si_docker.sh" >&2
        exit 2
    fi
fi

# ---- Resource monitor -----------------------------------------------------
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap "kill $MONPID 2>/dev/null || true" EXIT

# ---- Kill any stale nodes from a previous (possibly orphaned) run ----------
# A leftover player/estimator on the same topics corrupts a fresh run.
docker exec "$CONTAINER" bash -c "
    pgrep -f 'GNSS_Stereo_Inertial|gnss_data_player|roscore|rosmaster|rosout' \
        | xargs -r kill -9 2>/dev/null || true
    pkill -9 Xvfb 2>/dev/null || true
    rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 2>/dev/null || true
" 2>/dev/null || true
sleep 2

DATAROOT_CONT="/datasets/$DATASET/$SEQ"
PLAYER_CONT="/benchmark_scripts/run/gnss_data_player.py"

# Default GPS covariance: 1.0 m^2 horizontal (conventional Rosario gps.csv).
# When using PPK gps.csv, override at the call site or extend this script.
GPS_COV_XY=1.0
GPS_COV_Z=4.0

# ---- Reset trajectory output inside container -----------------------------
docker exec "$CONTAINER" bash -c "rm -f /root/.ros/CameraTrajectoryGPSOpt.txt /root/.ros/KeyFrameTrajectoryGPSOpt.txt /root/.ros/CameraTrajectory.txt /root/.ros/KeyFrameTrajectory.txt /root/catkin_ws/src/gnss-stereo-inertial-fusion/CameraTrajectoryGPSOpt.txt /root/catkin_ws/src/gnss-stereo-inertial-fusion/KeyFrameTrajectoryGPSOpt.txt /root/catkin_ws/src/gnss-stereo-inertial-fusion/CameraTrajectory.txt /root/catkin_ws/src/gnss-stereo-inertial-fusion/KeyFrameTrajectory.txt 2>/dev/null || true"

START=$(date +%s.%N)

# ---- Start roscore + GNSS_SI node -----------------------------------------
# We don't use the upstream rosario.launch (it expects a rosbag input). Instead
# we run roscore + the GNSS_Stereo_Inertial node directly with topic remaps,
# then push data via the data player. Use plain ;-separated lines (not
# `&&` chains terminated with `&`) so source commands take effect in this
# parent shell.
docker exec "$CONTAINER" bash -c "
    source /opt/ros/noetic/setup.bash
    export ROS_PACKAGE_PATH=\$ROS_PACKAGE_PATH:/root/catkin_ws/src/gnss-stereo-inertial-fusion/Examples/ROS
    # The GNSS_SI ROS node hardcodes bUseViewer=true; run under a virtual X
    # display so Pangolin can initialise headless (no real display in Docker).
    pkill -9 Xvfb 2>/dev/null || true
    rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 2>/dev/null || true
    Xvfb :99 -screen 0 1280x720x24 >/dev/null 2>&1 &
    export DISPLAY=:99
    for i in \$(seq 1 20); do xdpyinfo -display :99 >/dev/null 2>&1 && break; sleep 0.5; done
    if ! xdpyinfo -display :99 >/dev/null 2>&1; then echo '[cifasis_gnss_si] ERROR: Xvfb :99 not ready' >&2; fi
    roscore &
    sleep 4
    rosparam set /use_sim_time false
    rosrun GNSS_SI GNSS_Stereo_Inertial \
        /root/catkin_ws/src/gnss-stereo-inertial-fusion/Vocabulary/ORBvoc.txt \
        $CFG_CONT true \
        /camera/left/image_raw:=/stereo/left/image_raw \
        /camera/right/image_raw:=/stereo/right/image_raw
" 2>&1 | tee -a "$LOG" &
NODE_PID=$!

sleep 8

# ---- Run data player (publishes /stereo/left, /stereo/right, /imu, /gps/fix) -
docker exec "$CONTAINER" bash -c "
    source /opt/ros/noetic/setup.bash &&
    python3 $PLAYER_CONT $DATAROOT_CONT \
        --rate 1.0 --start-delay 1.0 --end-wait 5.0 \
        --cam0-topic /stereo/left/image_raw \
        --cam1-topic /stereo/right/image_raw \
        --imu-topic  /imu \
        --gps-topic  /gps/fix \
        --gps-cov-xy $GPS_COV_XY --gps-cov-z $GPS_COV_Z
" 2>&1 | tee -a "$LOG"

# ---- Stop GNSS_Stereo_Inertial --------------------------------------------
echo "[cifasis_gnss_si] data player done; stopping GNSS_SI ..." | tee -a "$LOG"
docker exec "$CONTAINER" bash -c "pkill -SIGINT -f GNSS_Stereo_Inertial 2>/dev/null || true"
sleep 5
docker exec "$CONTAINER" bash -c "pkill -SIGKILL -f GNSS_Stereo_Inertial 2>/dev/null || true; pkill -SIGKILL -f roscore 2>/dev/null || true; pkill -SIGKILL -f rosmaster 2>/dev/null || true; pkill -9 Xvfb 2>/dev/null || true"
wait "$NODE_PID" 2>/dev/null || true

END=$(date +%s.%N)

# ---- Collect trajectory ---------------------------------------------------
# The GNSS_SI node saves trajectories to its working directory (the source
# tree), NOT /root/.ros. Check both locations.
TRAJ_DIR=/root/catkin_ws/src/gnss-stereo-inertial-fusion
docker exec "$CONTAINER" bash -c "ls -la $TRAJ_DIR/*.txt /root/.ros/*.txt 2>/dev/null || true" | tee -a "$LOG"
docker cp "$CONTAINER:$TRAJ_DIR/CameraTrajectoryGPSOpt.txt" "$OUT_DIR/trajectory.txt" 2>/dev/null || \
    docker cp "$CONTAINER:/root/.ros/CameraTrajectoryGPSOpt.txt" "$OUT_DIR/trajectory.txt" 2>/dev/null || \
    docker cp "$CONTAINER:$TRAJ_DIR/KeyFrameTrajectoryGPSOpt.txt" "$OUT_DIR/trajectory.txt" 2>/dev/null || \
    docker cp "$CONTAINER:$TRAJ_DIR/CameraTrajectory.txt" "$OUT_DIR/trajectory.txt" 2>/dev/null || true
docker cp "$CONTAINER:$TRAJ_DIR/KeyFrameTrajectory.txt" "$OUT_DIR/keyframe_trajectory.txt" 2>/dev/null || true

if [[ ! -s "$OUT_DIR/trajectory.txt" ]]; then
    echo "[cifasis_gnss_si] ERROR: no trajectory produced" | tee -a "$LOG"
    exit 1
fi

cp "$LOG" "$OUT_DIR/run_log.txt"

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt")
python3 -c "
import json
print(json.dumps({
    'algo':'cifasis_gnss_si','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
    'run_type':'$RUN_TYPE',
    'duration_s':$DUR,'frames':$NFR,
    'fps':$NFR/$DUR if $DUR>0 else 0
}))
" > "$OUT_DIR/run_meta.json"

echo "[cifasis_gnss_si] done (run ${RUN_ID})" | tee -a "$LOG"
