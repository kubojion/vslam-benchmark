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
# Trajectory output: attempt/native/CameraTrajectoryGPSOpt.txt (TUM seconds).
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
source "$WS/scripts/run/_owned_process.sh"
OUT_CONT="/results/$RUN_TYPE/$DATASET/$SEQ/cifasis_gnss_si/run${RUN_ID}"

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

mkdir -p "$WS/logs"
prepare_fresh_run_dir "$OUT_DIR"
prepare_gnss_input "$OUT_DIR" "$SEQ_DIR"
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

owned_require_idle roscore rosmaster roslaunch GNSS_Stereo_Inertial
owned_ros1_port
mkdir "$OUT_DIR/native"

# ---- Resource monitor -----------------------------------------------------
prepare_resource_window "$OUT_DIR"
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" --container "$CONTAINER" --interval 1 \
    --start-file "$OUT_DIR/.resource_start" --stop-file "$OUT_DIR/.resource_stop" &
MONPID=$!
cleanup() {
    [[ -n "${MONPID:-}" ]] && kill "$MONPID" 2>/dev/null || true
    owned_stop player || true
    owned_stop stack || true
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

DATAROOT_CONT="/datasets/$DATASET/$SEQ"
PLAYER_CONT="/benchmark_scripts/run/gnss_data_player.py"

# Covariance/status defaults and overrides were frozen by prepare_gnss_input.
GNSS_VARIANT="${GNSS_VARIANT:-default}"

START=$(date +%s.%N)
mark_resource_start "$OUT_DIR"

# ---- Start roscore + GNSS_SI node -----------------------------------------
# We don't use the upstream rosario.launch (it expects a rosbag input). Instead
# we run roscore + the GNSS_Stereo_Inertial node directly with topic remaps,
# then push data via the data player. Use plain ;-separated lines (not
# `&&` chains terminated with `&`) so source commands take effect in this
# parent shell.
owned_run stack bash -c "
    set -e
    export ROS_MASTER_URI='$ROS_MASTER_URI'
    cd '$OUT_CONT/native'
    source /opt/ros/noetic/setup.bash
    export ROS_PACKAGE_PATH=\$ROS_PACKAGE_PATH:/root/catkin_ws/src/gnss-stereo-inertial-fusion/Examples/ROS
    # The GNSS_SI ROS node hardcodes bUseViewer=true; run under a virtual X
    # display so Pangolin can initialise headless (no real display in Docker).
    # Xvfb chooses an unused display; no global lock/socket deletion.
    Xvfb -displayfd 3 -screen 0 1280x720x24 3>'$OUT_CONT/x_display.txt' >/dev/null 2>&1 &
    for i in \$(seq 1 20); do [[ -s '$OUT_CONT/x_display.txt' ]] && break; sleep 0.5; done
    [[ -s '$OUT_CONT/x_display.txt' ]] || { echo 'Xvfb did not allocate a display' >&2; exit 1; }
    export DISPLAY=:\$(cat '$OUT_CONT/x_display.txt')
    roscore -p '$ROS_PORT' &
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
owned_run player bash -c "
    export ROS_MASTER_URI='$ROS_MASTER_URI'
    source /opt/ros/noetic/setup.bash &&
    python3 $PLAYER_CONT $DATAROOT_CONT \
        --gps-csv $GNSS_INPUT_CONT --gps-status $GPS_STATUS \
        --rate 1.0 --start-delay 1.0 --end-wait 5.0 \
        --cam0-topic /stereo/left/image_raw \
        --cam1-topic /stereo/right/image_raw \
        --imu-topic  /imu \
        --gps-topic  /gps/fix \
        --gps-cov-xy $GPS_COV_XY --gps-cov-z $GPS_COV_Z \
        --stats-out /results/$RUN_TYPE/$DATASET/$SEQ/cifasis_gnss_si/run${RUN_ID}/transport_stats.json
" 2>&1 | tee -a "$LOG"

# ---- Stop GNSS_Stereo_Inertial --------------------------------------------
echo "[cifasis_gnss_si] data player done; stopping GNSS_SI ..." | tee -a "$LOG"
OWNED_STOP_GRACE=30 owned_stop stack
wait "$NODE_PID" 2>/dev/null || true

END=$(date +%s.%N)
finish_resource_window "$OUT_DIR" "$MONPID"
MONPID=""

# ---- Collect trajectory ---------------------------------------------------
# Require the known GPS-optimized dense export from this attempt's working
# directory. A keyframe-only or non-GNSS fallback is a different experiment.
RAW_TRAJ="$OUT_DIR/native/CameraTrajectoryGPSOpt.txt"
if [[ -s "$RAW_TRAJ" ]]; then
    cp -p "$RAW_TRAJ" "$OUT_DIR/trajectory.txt"
    printf '%s\n' 'native/CameraTrajectoryGPSOpt.txt' > "$OUT_DIR/trajectory_source.txt"
fi
[[ ! -f "$OUT_DIR/native/KeyFrameTrajectory.txt" ]] || \
    cp -p "$OUT_DIR/native/KeyFrameTrajectory.txt" "$OUT_DIR/keyframe_trajectory.txt"

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
enrich_run_meta "$OUT_DIR/run_meta.json" \
    --artifact "gnss_input=$GNSS_INPUT" --artifact "gnss_input_manifest=$OUT_DIR/gnss_input.json" \
    --param "gps_cov_xy=$GPS_COV_XY" --param "gps_cov_z=$GPS_COV_Z" --param "gps_status=$GPS_STATUS" \
    --measurement-mode transport \
    --transport-stats "$OUT_DIR/transport_stats.json" \
    --artifact "estimator_config=$CFG_HOST" \
    --artifact "vocabulary=$WS/src/cifasis_gnss_si/Vocabulary/ORBvoc.txt.tar.gz" \
    --source "algorithm=$WS/src/cifasis_gnss_si" \
    --param "process_isolation=attempt_token_private_ros_master" \
    --param "trajectory_source=CameraTrajectoryGPSOpt.txt" \
    --param "playback_rate=1.0" --param "gnss_variant=$GNSS_VARIANT" \
    --container "$CONTAINER"

echo "[cifasis_gnss_si] done (run ${RUN_ID})" | tee -a "$LOG"
