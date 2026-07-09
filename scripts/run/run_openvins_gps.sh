#!/usr/bin/env bash
# Run OpenVINS VIO fused with GPS via robot_localization EKF.
#
# Usage: scripts/run/run_openvins_gps.sh <dataset> <seq> [run_id=1] [run_type=gnss-vio]
#
# Architecture:
#   Docker (--network host):
#     openvins:humble  ->  ros2 launch ov_msckf subscribe.launch.py
#                          publishes /ov_msckf/odomimu
#   Host (ROS 2 Humble):
#     gnss_data_player_ros2.py  ->  /cam0/image_raw, /cam1/image_raw,
#                                    /imu0, /fix
#     ekf_node                  ->  fuses /ov_msckf/odomimu + /odometry/gps
#                                   -> /odometry/filtered
#     navsat_transform_node     ->  /fix (NavSatFix) -> /odometry/gps (local ENU)
#     odom_to_tum_ros2.py       ->  /odometry/filtered -> trajectory.txt
#
# Static TFs published by runner (required for robot_localization frame lookup):
#   odom       -> global     identity  (accepts OpenVINS frame_id "global")
#   base_link  -> imu        identity  (accepts OpenVINS child_frame "imu")
#   base_link  -> gps        lever arm (enables navsat_transform GPS offset)

set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-gnss-vio}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
resolve_run_type "$RUN_TYPE"

if [[ "$RUN_TYPE" != "gnss-vio" ]]; then
    echo "[openvins_gps] only run_type=gnss-vio is supported" >&2
    exit 2
fi

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OV_CFG_DIR="$WS/configs/openvins/$DATASET"
RL_CFG_DIR="$WS/configs/robot_loc_openvins"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/openvins_gps/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_openvins_gps_${RUN_TYPE}_run${RUN_ID}.log"

# ---- Validate inputs -------------------------------------------------------
[[ -f "$OV_CFG_DIR/estimator_config.yaml" ]] \
    || { echo "[openvins_gps] missing $OV_CFG_DIR/estimator_config.yaml" >&2; exit 2; }
[[ -d "$SEQ_DIR/mav0/cam0/data" && -d "$SEQ_DIR/mav0/cam1/data" ]] \
    || { echo "[openvins_gps] missing $SEQ_DIR/mav0/cam{0,1}/data" >&2; exit 2; }
[[ -f "$SEQ_DIR/mav0/imu0/data.csv" ]] \
    || { echo "[openvins_gps] missing IMU data" >&2; exit 2; }
[[ -f "$SEQ_DIR/gps.csv" ]] \
    || { echo "[openvins_gps] missing $SEQ_DIR/gps.csv" >&2; exit 2; }
docker image inspect openvins:humble >/dev/null 2>&1 \
    || { echo "[openvins_gps] openvins:humble image not found - build it first" >&2; exit 2; }
dpkg -l ros-humble-robot-localization &>/dev/null \
    || { echo "[openvins_gps] ros-humble-robot-localization not installed" >&2; exit 2; }

# ---- Per-dataset parameters ------------------------------------------------
case "$DATASET" in
    rosariov2)
        # Rectified intrinsics from ORB-SLAM3 stereo config (1280x720).
        CAM_W=1280; CAM_H=720
        CAM_FX=648.8624169653789; CAM_FY=648.8624169653789
        CAM_CX=645.0113372802734;  CAM_CY=348.24266815185547
        CAM_BASELINE=0.0497336941
        # GPS antenna lever arm: base_link -> gps (from run_rtabmap_gps.sh)
        GPS_TX=0.22183; GPS_TY=0.01088; GPS_TZ=-0.17570
        ;;
    hortimulti)
        # Rectified intrinsics from ORB-SLAM3 stereo config (640x480).
        CAM_W=640; CAM_H=480
        CAM_FX=262.7149; CAM_FY=262.7149
        CAM_CX=329.4310; CAM_CY=219.5617
        CAM_BASELINE=0.139502
        # GPS antenna lever arm: base_link -> gps (from calibration.yaml)
        GPS_TX=0.62; GPS_TY=-0.11; GPS_TZ=0.42
        ;;
    *)
        echo "[openvins_gps] no parameters defined for dataset=$DATASET" >&2; exit 2 ;;
esac

mkdir -p "$OUT_DIR" "$WS/logs"
echo "[openvins_gps] $DATASET/$SEQ run=${RUN_ID} -> $OUT_DIR" | tee "$LOG"

# ---- Source ROS 2 ----------------------------------------------------------
# shellcheck disable=SC1091
source /opt/ros/humble/setup.bash

# ---- Kill any stale nodes from prior runs ----------------------------------
pkill -9 -f 'ekf_node|navsat_transform_node|odom_to_tum_ros2|gnss_data_player_ros2|static_transform_publisher' 2>/dev/null || true
sleep 1

# ---- Resource monitor ------------------------------------------------------
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!

# ---- Static TF publishers --------------------------------------------------
# 1. odom -> global  (EKF odom_frame=odom; OpenVINS frame_id="global")
ros2 run tf2_ros static_transform_publisher \
    --x 0 --y 0 --z 0 --qx 0 --qy 0 --qz 0 --qw 1 \
    --frame-id odom --child-frame-id global &
TF_ODOM_PID=$!

# 2. base_link -> imu  (EKF base_link_frame=base_link; OpenVINS child="imu")
ros2 run tf2_ros static_transform_publisher \
    --x 0 --y 0 --z 0 --qx 0 --qy 0 --qz 0 --qw 1 \
    --frame-id base_link --child-frame-id imu &
TF_IMU_PID=$!

# 3. base_link -> gps  (GPS antenna lever arm for navsat_transform)
ros2 run tf2_ros static_transform_publisher \
    --x "$GPS_TX" --y "$GPS_TY" --z "$GPS_TZ" \
    --qx 0 --qy 0 --qz 0 --qw 1 \
    --frame-id base_link --child-frame-id gps &
TF_GPS_PID=$!

sleep 0.5

# ---- EKF node (fuses VIO odometry + GPS local-ENU odometry) ---------------
ros2 run robot_localization ekf_node \
    --ros-args --params-file "$RL_CFG_DIR/ekf_gps.yaml" \
    > "$OUT_DIR/ekf_node.log" 2>&1 &
EKF_PID=$!

# ---- navsat_transform_node (NavSatFix -> local ENU odometry) ---------------
ros2 run robot_localization navsat_transform_node \
    --ros-args --params-file "$RL_CFG_DIR/navsat.yaml" \
    -r gps/fix:=/fix \
    -r odometry/filtered:=/odometry/filtered \
    -r odometry/gps:=/odometry/gps \
    > "$OUT_DIR/navsat.log" 2>&1 &
NAVSAT_PID=$!

# ---- TUM recorder (subscribes /odometry/filtered) --------------------------
python3 "$WS/scripts/run/odom_to_tum_ros2.py" \
    --topic /odometry/filtered \
    --out "$OUT_DIR/trajectory.txt" \
    --idle-timeout 15.0 \
    > "$OUT_DIR/tum_recorder.log" 2>&1 &
REC_PID=$!

sleep 1.5

# ---- OpenVINS in Docker (detached, --network host) -------------------------
OUT_REL=$(realpath --relative-to="$WS" "$OUT_DIR")
DOCKER_CID=$(docker run --detach --rm \
    --network host \
    --user "$(id -u):$(id -g)" \
    --volume "$WS:/ws" \
    --workdir /ws \
    --env HOME=/tmp \
    --entrypoint /bin/bash \
    openvins:humble \
    -c "
        source /opt/ros/humble/setup.bash
        source /colcon_ws/install/setup.bash
        ros2 launch ov_msckf subscribe.launch.py \
            config_path:=/ws/configs/openvins/$DATASET/estimator_config.yaml \
            use_stereo:=true max_cameras:=2 verbosity:=INFO \
            > /ws/${OUT_REL}/openvins_node.log 2>&1
    ")
echo "[openvins_gps] Docker container: $DOCKER_CID" | tee -a "$LOG"

cleanup() {
    kill "$MONPID" "$TF_ODOM_PID" "$TF_IMU_PID" "$TF_GPS_PID" \
         "$EKF_PID" "$NAVSAT_PID" "$REC_PID" 2>/dev/null || true
    docker kill "$DOCKER_CID" 2>/dev/null || true
    pkill -KILL -f 'ekf_node|navsat_transform_node|odom_to_tum_ros2|static_transform_publisher|gnss_data_player_ros2' 2>/dev/null || true
}
trap cleanup EXIT

sleep 3

# ---- Data player (foreground; publishes cam0/cam1/imu0/fix) ----------------
START=$(date +%s.%N)
python3 "$WS/scripts/run/gnss_data_player_ros2.py" \
    "$SEQ_DIR" \
    --rate 1.0 \
    --start-delay 1.0 \
    --end-wait 3.0 \
    --imu-best-effort \
    --cam-width "$CAM_W" --cam-height "$CAM_H" \
    --cam-fx "$CAM_FX" --cam-fy "$CAM_FY" \
    --cam-cx "$CAM_CX" --cam-cy "$CAM_CY" \
    --cam-baseline "$CAM_BASELINE" \
    --frame-id-gps gps \
    2>&1 | tee -a "$OUT_DIR/player.log" "$LOG"
END=$(date +%s.%N)

echo "[openvins_gps] player done, waiting for EKF flush..." | tee -a "$LOG"
sleep 8

if [[ ! -s "$OUT_DIR/trajectory.txt" ]]; then
    echo "[openvins_gps] ERROR: empty/missing trajectory.txt" | tee -a "$LOG"
    exit 1
fi

DUR=$(python3 -c "print($END - $START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt")
FPS=$(python3 -c "d=$DUR; print(round($NFR / d, 3) if d > 0 else 0)")

python3 - <<PYEOF
import json
from pathlib import Path
d = {
    "algo": "openvins_gps",
    "dataset": "$DATASET",
    "seq": "$SEQ",
    "run_id": $RUN_ID,
    "run_type": "gnss-vio",
    "duration_s": $DUR,
    "frames": $NFR,
    "fps": $FPS,
}
Path("$OUT_DIR/run_meta.json").write_text(json.dumps(d, indent=2))
print("[openvins_gps] run_meta.json written")
PYEOF

echo "[openvins_gps] done: $NFR frames, ${FPS} fps, ${DUR}s" | tee -a "$LOG"
