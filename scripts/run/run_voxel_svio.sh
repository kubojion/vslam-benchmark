#!/usr/bin/env bash
# Run Voxel-SVIO (stereo VIO, MSCKF + voxel map) on a sequence via Docker.
# Usage: scripts/run/run_voxel_svio.sh <dataset> <seq> [run_id=1] [run_type=vio]
#
# Voxel-SVIO is a pure stereo VIO (no VO mode, no loop closure). Running with
# run_type other than `vio` is rejected.
#
# Requires:
#   - Docker (no GPU needed; voxel_svio is CPU-only)
#   - Image vslam_voxel_svio:noetic and container 'voxel_svio' built by
#     scripts/setup/setup_voxel_svio_docker.sh
#   - configs/voxel_svio/<dataset>_<seq>.yaml  (per-sequence config; falls
#                                              back to <dataset>.yaml if absent)
#
# Dataset layout (EuRoC-ASL under datasets/<dataset>/<seq>/mav0/):
#   cam0/data/*.png      cam1/data/*.png
#   cam0/data.csv        cam1/data.csv      imu0/data.csv
#
# Runtime flow:
#   1. Start vio_node inside container via roslaunch (rviz disabled).
#   2. Run the data player inside the container; it publishes EuRoC images
#      and IMU samples to /cam0/image_raw, /cam1/image_raw, /imu0.
#   3. After the player exits, send SIGINT to roslaunch.
#   4. Voxel-SVIO writes pose.txt to the attempt native/ directory; preserve it
#      and export the camera-clock trajectory.txt beside it.
set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vio}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"

if [[ "$RUN_TYPE" != "vio" ]]; then
    echo "[voxel_svio] only run_type=vio is supported (no VO, no LC)" >&2
    exit 2
fi
source "$WS/scripts/run/_rosario_profile.sh"
check_rosario_candidate voxel_svio

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/voxel_svio/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_voxel_svio_${RUN_TYPE}_run${RUN_ID}.log"

CONTAINER="voxel_svio"
VOXEL_PREFIX=/root/catkin_ws/devel
if [[ "$DATASET" == zed2i || -n "${ROSARIO_VIO_PROFILE:-}" ]]; then
    VOXEL_PREFIX=/root/catkin_ws_shutdown_20261002/devel
fi
VOXEL_BIN="$VOXEL_PREFIX/lib/voxel_svio/vio_node"
if [[ "$DATASET" == zed2i || -n "${ROSARIO_VIO_PROFILE:-}" ]]; then
    VOXEL_BIN=/root/vslam_voxel_audit_20261002_v2/vio_node
fi
source "$WS/scripts/run/_owned_process.sh"
OUT_CONT="/results/$RUN_TYPE/$DATASET/$SEQ/voxel_svio/run${RUN_ID}"

# Per-sequence config first, then per-dataset fallback.
CFG_HOST_SEQ="$WS/configs/voxel_svio/${DATASET}_${SEQ}.yaml"
CFG_HOST_DSET="$WS/configs/voxel_svio/${DATASET}.yaml"
if [[ -n "${ROSARIO_VIO_PROFILE:-}" ]]; then
    CFG_HOST="$WS/configs/candidates/rosario-vio-20261002/$ROSARIO_VIO_PROFILE/rosariov2.yaml"
elif [[ -f "$CFG_HOST_SEQ" ]]; then
    CFG_HOST="$CFG_HOST_SEQ"
elif [[ -f "$CFG_HOST_DSET" ]]; then
    CFG_HOST="$CFG_HOST_DSET"
else
    echo "[voxel_svio] missing config: tried $CFG_HOST_SEQ and $CFG_HOST_DSET" >&2
    exit 2
fi
CFG_CONT="/benchmark_configs/voxel_svio/$(basename "$CFG_HOST")"

[[ -d "$SEQ_DIR/mav0/cam0/data" && -d "$SEQ_DIR/mav0/cam1/data" ]] \
    || { echo "[voxel_svio] missing $SEQ_DIR/mav0/cam{0,1}/data" >&2; exit 2; }
[[ -f "$SEQ_DIR/mav0/imu0/data.csv" ]] \
    || { echo "[voxel_svio] missing IMU $SEQ_DIR/mav0/imu0/data.csv" >&2; exit 2; }

mkdir -p "$WS/logs"
prepare_fresh_run_dir "$OUT_DIR"
snapshot_rosario_candidate
if [[ -n "${ROSARIO_VIO_PROFILE:-}" ]]; then
    CFG_HOST="$ROSARIO_PROFILE_DIR/rosariov2.yaml"
    CFG_CONT="$OUT_CONT/configuration-profile/rosariov2.yaml"
fi
echo "[voxel_svio] $DATASET/$SEQ run=${RUN_ID} -> $OUT_DIR" | tee "$LOG"
PROV_ARGS=(
    "${PROFILE_PROV_ARGS[@]}"
    --artifact "estimator_config=$CFG_HOST"
    --source "algorithm=$WS/src/voxel_svio"
    --param "process_isolation=attempt_token_private_ros_master"
    --param "playback_rate=1.0"
    --param "native_prefix=$VOXEL_PREFIX"
    --param "native_executable=$VOXEL_BIN"
    --param "abort_backtrace_diagnostic=${VOXEL_SVIO_BACKTRACE:-0}"
    --container "$CONTAINER"
)
if [[ "$DATASET" == zed2i || -n "${ROSARIO_VIO_PROFILE:-}" ]]; then
    PROV_ARGS+=(--artifact "shutdown_source_patch=$WS/docs/upstream/voxel-svio-subscriber-lifetime.patch"
        --artifact "native_build_review=$WS/docs/campaigns/voxel-zed-shutdown-build-20261002.json"
        --artifact "parameter_audit_build=$WS/docs/campaigns/voxel-parameter-audit-build-20261002.json")
fi

# ---- Ensure Docker container is running -----------------------------------
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
        echo "[voxel_svio] starting existing container $CONTAINER ..." | tee -a "$LOG"
        docker start "$CONTAINER"
    else
        echo "ERROR: container '$CONTAINER' does not exist." >&2
        echo "Run: bash scripts/setup/setup_voxel_svio_docker.sh" >&2
        exit 2
    fi
fi

owned_require_idle roscore rosmaster roslaunch vio_node
owned_ros1_port

# ---- Resource monitor -----------------------------------------------------
prepare_resource_window "$OUT_DIR"
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" --container "$CONTAINER" --interval 1 \
    --start-file "$OUT_DIR/.resource_start" --stop-file "$OUT_DIR/.resource_stop" &
MONPID=$!
cleanup() {
    [[ -n "${MONPID:-}" ]] && kill "$MONPID" 2>/dev/null || true
    owned_stop player || true
    owned_stop node || true
    owned_stop roscore || true
    [[ ! -f "$LOG" ]] || cp "$LOG" "$OUT_DIR/run_log.txt"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# The native exporter appends; give this attempt its own fresh directory.
# Never delete another attempt's shared source/output files.
mkdir "$OUT_DIR/native"

DATAROOT_CONT="/datasets/$DATASET/$SEQ"
PLAYER_HOST="/benchmark_scripts/run/voxel_svio_data_player.py"

START=$(date +%s.%N)
mark_resource_start "$OUT_DIR"

# ---- Start roscore inside the container ------------------------------------
owned_run roscore bash -c "
    export ROS_MASTER_URI='$ROS_MASTER_URI'
    source /opt/ros/noetic/setup.bash &&
    exec roscore -p '$ROS_PORT'
" 2>&1 >> "$LOG" &
ROSCORE_PID=$!
# Wait until rosmaster is reachable (up to 10 s).
for i in $(seq 1 10); do
    docker exec "$CONTAINER" bash -c "
        export ROS_MASTER_URI='$ROS_MASTER_URI'
        source /opt/ros/noetic/setup.bash &&
        rostopic list" &>/dev/null && break
    sleep 1
done

# Use a local launch wrapper that loads our config (the upstream launch file
# loads its bundled config/euroc.yaml). We pass the config path via rosparam
# load on the command line instead.
NODE_COMMAND="exec $VOXEL_BIN"
if [[ "${VOXEL_SVIO_BACKTRACE:-0}" == 1 ]]; then
    NODE_COMMAND="exec env LD_PRELOAD=/lib/x86_64-linux-gnu/libSegFault.so SEGFAULT_SIGNALS=abrt $VOXEL_BIN"
fi
owned_run node bash -c "
    export ROS_MASTER_URI='$ROS_MASTER_URI'
    set -e
    source /opt/ros/noetic/setup.bash &&
    source $VOXEL_PREFIX/setup.bash &&
    rosparam load $CFG_CONT &&
    rosparam set /output_path '$OUT_CONT/native' &&
    rosparam dump '$OUT_CONT/effective_ros_parameters.yaml' &&
    $NODE_COMMAND
" >> "$LOG" 2>&1 &
NODE_PID=$!

# Give the node a moment to start subscribing.
sleep 3

# ---- Run data player inside container -------------------------------------
set +e
owned_run player bash -c "
    export ROS_MASTER_URI='$ROS_MASTER_URI'
    source /opt/ros/noetic/setup.bash &&
    exec python3 $PLAYER_HOST $DATAROOT_CONT --rate 1.0 --start-delay 1.0 --end-wait 3.0 \
        --stats-out /results/$RUN_TYPE/$DATASET/$SEQ/voxel_svio/run${RUN_ID}/transport_stats.json
" 2>&1 | tee -a "$LOG"
PLAYER_RC=${PIPESTATUS[0]}
set -e

# ---- Stop vio_node and roscore --------------------------------------------
echo "[voxel_svio] data player done; stopping vio_node ..." | tee -a "$LOG"
owned_stop node
set +e
wait "$NODE_PID"
NODE_RC=$?
set -e
owned_stop roscore
wait "$ROSCORE_PID" 2>/dev/null || true

END=$(date +%s.%N)
finish_resource_window "$OUT_DIR" "$MONPID"
MONPID=""
cp "$LOG" "$OUT_DIR/run_log.txt"

# ---- Collect trajectory ---------------------------------------------------
POSE_HOST="$OUT_DIR/native/pose.txt"
for report in parameter_list.txt camera_load.txt input_receipt.json; do
    if [[ -f "$OUT_DIR/native/$report" ]]; then
        PROV_ARGS+=(--artifact "native_$report=$OUT_DIR/native/$report")
    fi
done
if [[ ! -s "$POSE_HOST" ]]; then
    FAILURE_RC=$NODE_RC
    (( FAILURE_RC != 0 )) || FAILURE_RC=$PLAYER_RC
    (( FAILURE_RC != 0 )) || FAILURE_RC=1
    record_failed_run_meta "$OUT_DIR/run_meta.json" voxel_svio "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" "$FAILURE_RC" "no saved trajectory; player_exit=$PLAYER_RC native_exit=$NODE_RC" "${PROV_ARGS[@]}"
    echo "[voxel_svio] ERROR: $POSE_HOST is missing or empty" | tee -a "$LOG"
    exit "$FAILURE_RC"
fi
cp "$POSE_HOST" "$OUT_DIR/trajectory.txt"
[[ -f "$OUT_DIR/native/parameter_list.txt" ]] && \
    cp "$OUT_DIR/native/parameter_list.txt" "$OUT_DIR/parameter_list.txt"
cp "$LOG" "$OUT_DIR/run_log.txt"

# ---- Compensate cam-IMU timeshift in output timestamps --------------------
# Voxel-SVIO writes pose timestamps on the IMU clock. The host-side GT and the
# rest of the benchmark expect camera-clock timestamps. Subtract the configured
# timeshift_cam_imu_left so trajectory.txt is on the camera clock and evo_ape
# can match poses within --t_max_diff 0.005.
python3 - "$CFG_HOST" "$OUT_DIR/trajectory.txt" <<'PYEOF'
import re, sys
cfg_path, traj_path = sys.argv[1], sys.argv[2]
shift = 0.0
with open(cfg_path) as fh:
    for line in fh:
        m = re.match(r'\s*timeshift_cam_imu_left\s*:\s*([-+0-9.eE]+)', line)
        if m:
            shift = float(m.group(1))
            break
if shift == 0.0:
    sys.exit(0)
with open(traj_path) as fh:
    lines = fh.readlines()
out = []
for l in lines:
    s = l.strip()
    if not s or s.startswith('#'):
        out.append(l); continue
    parts = s.split()
    parts[0] = f"{float(parts[0]) - shift:.9f}"
    out.append(' '.join(parts) + '\n')
with open(traj_path, 'w') as fh:
    fh.writelines(out)
print(f"[voxel_svio] shifted trajectory timestamps by -{shift}s (cam-IMU offset)")
PYEOF

# Preserve any exported trajectory for recovery, but never hide native failure.
if (( NODE_RC != 0 || PLAYER_RC != 0 )); then
    FAILURE_RC=$NODE_RC
    (( FAILURE_RC != 0 )) || FAILURE_RC=$PLAYER_RC
    record_failed_run_meta "$OUT_DIR/run_meta.json" voxel_svio "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" "$FAILURE_RC" "player_exit=$PLAYER_RC native_exit=$NODE_RC; retained exported trajectory" "${PROV_ARGS[@]}"
    exit "$FAILURE_RC"
fi

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt")
python3 -c "
import json
print(json.dumps({
    'algo':'voxel_svio','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
    'run_type':'$RUN_TYPE',
    'duration_s':$DUR,'frames':$NFR,
    'fps':$NFR/$DUR if $DUR>0 else 0
}))
" > "$OUT_DIR/run_meta.json"
enrich_run_meta "$OUT_DIR/run_meta.json" \
    --measurement-mode transport \
    --transport-stats "$OUT_DIR/transport_stats.json" \
    --process-exit-code "$NODE_RC" "${PROV_ARGS[@]}"

echo "[voxel_svio] done (run ${RUN_ID})" | tee -a "$LOG"
