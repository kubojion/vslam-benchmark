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
canonicalize_dataset "$DATASET"
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

# ---- Pre-run cleanup (orphaned ROS 2 nodes corrupt subsequent runs) --------
# NB: patterns must NOT match this script's own command line
# (run_rtabmap_gps.sh contains the substring "rtabmap"), so target the actual
# node executables / launch file rather than the bare word "rtabmap".
pkill -9 -f 'rtabmap_slam|rtabmap_odom|rtabmap_sync|rtabmap.launch|stereo_odometry|gnss_data_player_ros2|static_transform_publisher|imu_filter_madgwick' 2>/dev/null || true
sleep 2

# ---- Resource monitor ------------------------------------------------------
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!

DB_PATH="/tmp/rtabmap_${DATASET}_${SEQ}_run${RUN_ID}.db"
rm -f "$DB_PATH"

cleanup() {
    kill "$MONPID" 2>/dev/null || true
    kill "$TF_CAM_PID" "$TF_IMU_PID" "$TF_GPS_PID" "$IMU_FILTER_PID" 2>/dev/null || true
    pkill -INT -f 'rtabmap_slam|rtabmap_odom|rtabmap_sync|rtabmap.launch|stereo_odometry|gnss_data_player_ros2|imu_filter_madgwick' 2>/dev/null || true
    sleep 1
    pkill -KILL -f 'rtabmap_slam|rtabmap_odom|rtabmap_sync|rtabmap.launch|stereo_odometry|gnss_data_player_ros2|imu_filter_madgwick' 2>/dev/null || true
}
trap cleanup EXIT

# ---- Source ROS 2 ----------------------------------------------------------
# shellcheck disable=SC1091
source /opt/ros/humble/setup.bash

# ---- Per-dataset intrinsics + extrinsics -----------------------------------
# CAM_*  : rectified pinhole intrinsics for the synthesised CameraInfo.
# CAM_Q* / CAM_T* : base_link(IMU body) -> camera optical frame transform.
#                   Taken directly from Tbc in the matching cifasis config
#                   (Tbc maps IMU body -> camera optical).
# GPS_T* : base_link -> gps frame lever arm (System.t_b_g in the cifasis config).
# RTAB-Map needs these TFs to initialise stereo+IMU odometry and to fuse GPS;
# the data player publishes sensor data only, not TF, so we publish them here.
case "$DATASET" in
    rosariov2)
        # Rectified intrinsics from the working ORB-SLAM3 stereo config.
        # Images are 1280x720 (verified via cv2.imread). The earlier 672x376
        # half-resolution values produced a ~200x scale explosion.
        CAM_W=1280; CAM_H=720
        CAM_FX=648.8624169653789; CAM_FY=648.8624169653789
        CAM_CX=645.0113372802734;  CAM_CY=348.24266815185547
        CAM_BASELINE=0.0497336941
        # Tbc near-identity (RealSense D435i): q(xyzw), t.
        CAM_QX=0.002505; CAM_QY=-0.000293; CAM_QZ=0.001948; CAM_QW=0.999995
        CAM_TX=-0.004483; CAM_TY=0.019179; CAM_TZ=0.027584
        GPS_TX=0.22183; GPS_TY=0.01088; GPS_TZ=-0.17570
        ;;
    hortimulti)
        CAM_W=640; CAM_H=480
        CAM_FX=262.7149; CAM_FY=262.7149
        CAM_CX=329.4310; CAM_CY=219.5617
        CAM_BASELINE=0.139502
        # Tbc 90-deg camera/body rotation (Kalibr): q(xyzw), t.
        CAM_QX=-0.511409; CAM_QY=0.4924; CAM_QZ=-0.492013; CAM_QW=0.50391
        CAM_TX=0.1219040939; CAM_TY=0.0366053924; CAM_TZ=-0.0562970105
        GPS_TX=0.62; GPS_TY=-0.11; GPS_TZ=0.42
        ;;
    *)
        echo "[rtabmap_gps] no intrinsics defined for dataset=$DATASET" >&2
        exit 2
        ;;
esac

START=$(date +%s.%N)

# ---- Launch RTAB-Map (stereo_outdoor.launch.py) ---------------------------
# We use the rtabmap_launch package's stereo_outdoor.launch.py and overlay
# our YAML via params_file.
ros2 launch rtabmap_launch rtabmap.launch.py \
    stereo:=true \
    left_image_topic:=/cam0/image_raw \
    right_image_topic:=/cam1/image_raw \
    left_camera_info_topic:=/cam0/camera_info \
    right_camera_info_topic:=/cam1/camera_info \
    imu_topic:=/imu/data \
    wait_imu_to_init:=true \
    gps_topic:=/fix \
    frame_id:=base_link \
    approx_sync:=true \
    qos:=2 \
    rtabmap_args:="--delete_db_on_start --Mem/IncrementalMemory true --Optimizer/PriorsIgnored false --Optimizer/Strategy 1 --Optimizer/Robust true" \
    rtabmap_viz:=false \
    rviz:=false \
    database_path:="$DB_PATH" \
    cfg:="$CFG_HOST" \
    >>"$LOG" 2>&1 &
LAUNCH_PID=$!

# ---- Static TF tree: base_link -> {cam, imu, gps} --------------------------
# The data player publishes "cam"/"imu"/"gps" frames but no TF. RTAB-Map needs
# base_link -> sensor transforms to run stereo+IMU odometry and fuse GPS.
ros2 run tf2_ros static_transform_publisher \
    --x "$CAM_TX" --y "$CAM_TY" --z "$CAM_TZ" \
    --qx "$CAM_QX" --qy "$CAM_QY" --qz "$CAM_QZ" --qw "$CAM_QW" \
    --frame-id base_link --child-frame-id cam >>"$LOG" 2>&1 &
TF_CAM_PID=$!
ros2 run tf2_ros static_transform_publisher \
    --x 0 --y 0 --z 0 --qx 0 --qy 0 --qz 0 --qw 1 \
    --frame-id base_link --child-frame-id imu >>"$LOG" 2>&1 &
TF_IMU_PID=$!
ros2 run tf2_ros static_transform_publisher \
    --x "$GPS_TX" --y "$GPS_TY" --z "$GPS_TZ" --qx 0 --qy 0 --qz 0 --qw 1 \
    --frame-id base_link --child-frame-id gps >>"$LOG" 2>&1 &
TF_GPS_PID=$!

# ---- IMU orientation filter ------------------------------------------------
# The player publishes raw IMU (accel+gyro, no orientation). RTAB-Map ignores
# IMU without orientation, so odometry would be stereo-only. Madgwick fuses
# accel+gyro into an orientation quaternion on /imu/data for gravity-aligned
# odometry + graph gravity constraints (parity with VINS/CIFASIS).
ros2 run imu_filter_madgwick imu_filter_madgwick_node --ros-args \
    -p use_mag:=false -p publish_tf:=false -p world_frame:=enu \
    -r imu/data_raw:=/imu0 -r imu/data:=/imu/data >>"$LOG" 2>&1 &
IMU_FILTER_PID=$!

# Give rtabmap a few seconds to spin up subscribers + tf publishers.
sleep 5

# ---- Run data player -------------------------------------------------------
# The gnss_data_player is a ROS 1 script. Convert via a thin ROS 2 wrapper
# below, or invoke directly if rclpy environment is available.
# NOTE: This script currently assumes a ROS 2-aware gnss_data_player exists.
# See scripts/run/gnss_data_player_ros2.py (TODO) for the ROS 2 port.
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
    # rtabmap-export resolves --output relative to the database's directory and
    # mangles absolute output paths (e.g. /tmp//home/...), so use a basename:
    # the file lands next to the .db (in $DB_PATH's dir) and we copy it out.
    DB_DIR="$(dirname "$DB_PATH")"
    EXPORT_STEM="rtabmap_export_${DATASET}_${SEQ}_run${RUN_ID}"
    rm -f "$DB_DIR/${EXPORT_STEM}_poses.txt"
    rtabmap-export --poses --poses_format 11 --output "$EXPORT_STEM" \
        "$DB_PATH" >>"$LOG" 2>&1 || true
    # poses_format=11 is the TUM "timestamp tx ty tz qx qy qz qw" RGB-D SLAM
    # benchmark format. The output filename has _poses.txt suffix.
    EXPORTED="$DB_DIR/${EXPORT_STEM}_poses.txt"
    if [[ -s "$EXPORTED" ]]; then
        # rtabmap format 11 emits a "#timestamp ..." header and a trailing id
        # column. evo_ape tum requires exactly 8 columns, so strip both.
        awk '!/^#/ && NF>=8 {print $1,$2,$3,$4,$5,$6,$7,$8}' "$EXPORTED" > "$TRAJ"
        rm -f "$EXPORTED"
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
