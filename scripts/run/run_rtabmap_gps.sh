#!/usr/bin/env bash
# Run RTAB-Map (ROS 2 Humble, native install via apt) on a stereo+IMU+GPS
# sequence and emit a TUM-format trajectory.
#
# Usage:
#   scripts/run/run_rtabmap_gps.sh <dataset> <seq> [run_id=1] [run_type=gnss-vio]
#
# Requires:
#   - ros-humble-rtabmap-ros (apt-installed)
#   - ros-humble-cv-bridge, ros-humble-image-transport
#   - python3-rosbag2 + rclpy (provided by the rtabmap_ros stack)
#   - configs/rtabmap_gps/<dataset>.yaml
#
# Dataset layout (EuRoC-ASL under datasets/<dataset>/<seq>/mav0/):
#   cam0/data/*.png      cam1/data/*.png
#   cam0/data.csv        cam1/data.csv      imu0/data.csv
#   gps.csv              (header: t,lat,lon,alt[,cov_*,status])
#
# Runtime flow:
#   1. Source ROS 2 humble.
#   2. Launch rtabmap stereo_outdoor_gps.launch.py with overlaid YAML.
#   3. Run the gnss_data_player to publish /cam0,/cam1,/imu0,/fix.
#   4. After playback ends, kill rtabmap, export DB to TUM trajectory.
set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-gnss-vio}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
resolve_run_type "$RUN_TYPE"

if [[ "$RUN_TYPE" != "gnss-vio" ]]; then
    echo "[rtabmap_gps] only run_type=gnss-vio is supported" >&2
    exit 2
fi

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/rtabmap_gps/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_rtabmap_gps_${RUN_TYPE}_run${RUN_ID}.log"

CFG_HOST_SEQ="$WS/configs/rtabmap_gps/${DATASET}_${SEQ}.yaml"
CFG_HOST_DSET="$WS/configs/rtabmap_gps/${DATASET}.yaml"
if [[ -f "$CFG_HOST_SEQ" ]]; then
    CFG_HOST="$CFG_HOST_SEQ"
elif [[ -f "$CFG_HOST_DSET" ]]; then
    CFG_HOST="$CFG_HOST_DSET"
else
    echo "[rtabmap_gps] missing config: tried $CFG_HOST_SEQ and $CFG_HOST_DSET" >&2
    exit 2
fi

[[ -d "$SEQ_DIR/mav0/cam0/data" && -d "$SEQ_DIR/mav0/cam1/data" ]] \
    || { echo "[rtabmap_gps] missing $SEQ_DIR/mav0/cam{0,1}/data" >&2; exit 2; }
[[ -f "$SEQ_DIR/mav0/imu0/data.csv" ]] \
    || { echo "[rtabmap_gps] missing IMU $SEQ_DIR/mav0/imu0/data.csv" >&2; exit 2; }
[[ -f "$SEQ_DIR/gps.csv" ]] \
    || { echo "[rtabmap_gps] missing GPS $SEQ_DIR/gps.csv" >&2; exit 2; }

mkdir -p "$OUT_DIR" "$WS/logs"
echo "[rtabmap_gps] $DATASET/$SEQ run=${RUN_ID} -> $OUT_DIR" | tee "$LOG"
echo "[rtabmap_gps] config: $CFG_HOST" | tee -a "$LOG"

# ---- Verify rtabmap_ros is installed --------------------------------------
if ! dpkg -l ros-humble-rtabmap-ros &>/dev/null; then
    echo "ERROR: ros-humble-rtabmap-ros not installed." >&2
    echo "Run: sudo apt install ros-humble-rtabmap-ros" >&2
    exit 2
fi

# ---- Resource monitor ------------------------------------------------------
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!

DB_PATH="/tmp/rtabmap_${DATASET}_${SEQ}_run${RUN_ID}.db"
rm -f "$DB_PATH"

cleanup() {
    kill "$MONPID" 2>/dev/null || true
    pkill -INT -f "rtabmap" 2>/dev/null || true
    pkill -INT -f "stereo_odometry" 2>/dev/null || true
    sleep 1
    pkill -KILL -f "rtabmap" 2>/dev/null || true
    pkill -KILL -f "stereo_odometry" 2>/dev/null || true
}
trap cleanup EXIT

# ---- Source ROS 2 ----------------------------------------------------------
# shellcheck disable=SC1091
source /opt/ros/humble/setup.bash

START=$(date +%s.%N)

# ---- Launch RTAB-Map (stereo_outdoor.launch.py) ---------------------------
# We use the rtabmap_launch package's stereo_outdoor.launch.py and overlay
# our YAML via params_file.
ros2 launch rtabmap_launch rtabmap.launch.py \
    stereo:=true \
    rgb_topic:= \
    left_image_topic:=/cam0/image_raw \
    right_image_topic:=/cam1/image_raw \
    left_camera_info_topic:=/cam0/camera_info \
    right_camera_info_topic:=/cam1/camera_info \
    imu_topic:=/imu0 \
    wait_imu_to_init:=true \
    gps_topic:=/fix \
    frame_id:=base_link \
    approx_sync:=true \
    qos:=2 \
    rtabmap_args:="--delete_db_on_start --Mem/IncrementalMemory true" \
    rtabmap_viz:=false \
    rviz:=false \
    database_path:="$DB_PATH" \
    cfg:="$CFG_HOST" \
    >>"$LOG" 2>&1 &
LAUNCH_PID=$!

# Give rtabmap a few seconds to spin up subscribers + tf publishers.
sleep 5

# ---- Run data player -------------------------------------------------------
# The gnss_data_player is a ROS 1 script. Convert via a thin ROS 2 wrapper
# below, or invoke directly if rclpy environment is available.
# NOTE: This script currently assumes a ROS 2-aware gnss_data_player exists.
# See scripts/run/gnss_data_player_ros2.py (TODO) for the ROS 2 port.
# Rectified pinhole intrinsics for CameraInfo (per dataset).
case "$DATASET" in
    rosariov2)
        CAM_W=672; CAM_H=376
        CAM_FX=347.6564367181238; CAM_FY=347.6564367181238
        CAM_CX=339.375789642334;  CAM_CY=198.58967208862305
        CAM_BASELINE=0.11872
        ;;
    hortimulti)
        CAM_W=640; CAM_H=480
        CAM_FX=262.7149; CAM_FY=262.7149
        CAM_CX=329.4310; CAM_CY=219.5617
        CAM_BASELINE=0.139502
        ;;
    *)
        echo "[rtabmap_gps] no intrinsics defined for dataset=$DATASET" >&2
        cleanup; exit 2
        ;;
esac

if [[ -x "$WS/scripts/run/gnss_data_player_ros2.py" ]]; then
    python3 "$WS/scripts/run/gnss_data_player_ros2.py" "$SEQ_DIR" \
        --rate 1.0 --start-delay 1.0 --end-wait 3.0 \
        --gps-topic /fix \
        --cam-width  "$CAM_W"  --cam-height   "$CAM_H" \
        --cam-fx     "$CAM_FX" --cam-fy       "$CAM_FY" \
        --cam-cx     "$CAM_CX" --cam-cy       "$CAM_CY" \
        --cam-baseline "$CAM_BASELINE" \
        2>&1 | tee -a "$LOG"
else
    echo "[rtabmap_gps] WARNING: gnss_data_player_ros2.py not found." | tee -a "$LOG"
    echo "[rtabmap_gps] First run requires creating the ROS 2 player." | tee -a "$LOG"
    echo "[rtabmap_gps] (rtabmap is ROS 2 native; the existing ROS 1 player won't work.)" | tee -a "$LOG"
    cleanup
    exit 2
fi

# ---- Stop launch ----------------------------------------------------------
echo "[rtabmap_gps] data player done; stopping rtabmap ..." | tee -a "$LOG"
kill -INT "$LAUNCH_PID" 2>/dev/null || true
sleep 3
kill -KILL "$LAUNCH_PID" 2>/dev/null || true
wait "$LAUNCH_PID" 2>/dev/null || true

END=$(date +%s.%N)

# ---- Export trajectory from rtabmap database -------------------------------
# rtabmap-export writes <stem>_poses.txt in TUM format with --poses flag.
TRAJ="$OUT_DIR/trajectory.txt"
if [[ -f "$DB_PATH" ]]; then
    rtabmap-export --poses --poses_format 11 --output "$OUT_DIR/rtabmap_export" \
        "$DB_PATH" >>"$LOG" 2>&1 || true
    # poses_format=11 is the TUM "timestamp tx ty tz qx qy qz qw" RGB-D SLAM
    # benchmark format. The output filename has _poses.txt suffix.
    EXPORTED=$(ls "$OUT_DIR"/rtabmap_export*_poses.txt 2>/dev/null | head -1 || true)
    if [[ -n "$EXPORTED" && -s "$EXPORTED" ]]; then
        cp "$EXPORTED" "$TRAJ"
    else
        echo "[rtabmap_gps] ERROR: rtabmap-export produced no poses file" | tee -a "$LOG"
    fi
fi

if [[ ! -s "$TRAJ" ]]; then
    echo "[rtabmap_gps] ERROR: $TRAJ is missing or empty" | tee -a "$LOG"
    exit 1
fi

cp "$LOG" "$OUT_DIR/run_log.txt"
[[ -f "$DB_PATH" ]] && cp "$DB_PATH" "$OUT_DIR/rtabmap.db" || true

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$TRAJ")
python3 -c "
import json
print(json.dumps({
    'algo':'rtabmap_gps','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
    'run_type':'$RUN_TYPE',
    'duration_s':$DUR,'frames':$NFR,
    'fps':$NFR/$DUR if $DUR>0 else 0
}))
" > "$OUT_DIR/run_meta.json"

echo "[rtabmap_gps] done (run ${RUN_ID})" | tee -a "$LOG"
