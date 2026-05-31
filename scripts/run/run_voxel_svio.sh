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
#   4. Voxel-SVIO writes pose.txt to its src/voxel_svio/output/ directory;
#      copy and rename to results-vio/<dataset>/<seq>/voxel_svio/run<N>/trajectory.txt.
set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vio}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
resolve_run_type "$RUN_TYPE"

if [[ "$RUN_TYPE" != "vio" ]]; then
    echo "[voxel_svio] only run_type=vio is supported (no VO, no LC)" >&2
    exit 2
fi

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/voxel_svio/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_voxel_svio_${RUN_TYPE}_run${RUN_ID}.log"

CONTAINER="voxel_svio"

# Per-sequence config first, then per-dataset fallback.
CFG_HOST_SEQ="$WS/configs/voxel_svio/${DATASET}_${SEQ}.yaml"
CFG_HOST_DSET="$WS/configs/voxel_svio/${DATASET}.yaml"
if [[ -f "$CFG_HOST_SEQ" ]]; then
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

mkdir -p "$OUT_DIR" "$WS/logs"
echo "[voxel_svio] $DATASET/$SEQ run=${RUN_ID} -> $OUT_DIR" | tee "$LOG"

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

# ---- Resource monitor -----------------------------------------------------
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap "kill $MONPID 2>/dev/null || true" EXIT

# ---- Reset voxel_svio output dir before the run ---------------------------
# Voxel-SVIO appends to pose.txt; clear it so each run is fresh.
docker exec "$CONTAINER" bash -c "
    mkdir -p /root/catkin_ws/src/voxel_svio/output &&
    rm -f /root/catkin_ws/src/voxel_svio/output/pose.txt \
          /root/catkin_ws/src/voxel_svio/output/parameter_list.txt
"

DATAROOT_CONT="/datasets/$DATASET/$SEQ"
PLAYER_HOST="/benchmark_scripts/run/voxel_svio_data_player.py"

START=$(date +%s.%N)

# ---- Start roscore inside the container ------------------------------------
docker exec "$CONTAINER" bash -c "
    source /opt/ros/noetic/setup.bash &&
    roscore
" 2>&1 >> "$LOG" &
ROSCORE_PID=$!
# Wait until rosmaster is reachable (up to 10 s).
for i in $(seq 1 10); do
    docker exec "$CONTAINER" bash -c "
        source /opt/ros/noetic/setup.bash &&
        rostopic list" &>/dev/null && break
    sleep 1
done

# Use a local launch wrapper that loads our config (the upstream launch file
# loads its bundled config/euroc.yaml). We pass the config path via rosparam
# load on the command line instead.
docker exec "$CONTAINER" bash -c "
    set -e
    source /opt/ros/noetic/setup.bash &&
    source /root/catkin_ws/devel/setup.bash &&
    rosparam load $CFG_CONT &&
    rosparam set /output_path /root/catkin_ws/src/voxel_svio/output &&
    rosrun voxel_svio vio_node
" 2>&1 | tee -a "$LOG" &
NODE_PID=$!

# Give the node a moment to start subscribing.
sleep 3

# ---- Run data player inside container -------------------------------------
docker exec "$CONTAINER" bash -c "
    source /opt/ros/noetic/setup.bash &&
    python3 $PLAYER_HOST $DATAROOT_CONT --rate 1.0 --start-delay 1.0 --end-wait 3.0
" 2>&1 | tee -a "$LOG"

# ---- Stop vio_node and roscore --------------------------------------------
echo "[voxel_svio] data player done; stopping vio_node ..." | tee -a "$LOG"
docker exec "$CONTAINER" bash -c "pkill -SIGINT -f vio_node 2>/dev/null || true"
sleep 2
wait "$NODE_PID" 2>/dev/null || true
docker exec "$CONTAINER" bash -c "pkill -f roscore 2>/dev/null || true; pkill -f rosmaster 2>/dev/null || true"
kill "$ROSCORE_PID" 2>/dev/null || true

END=$(date +%s.%N)

# ---- Collect trajectory ---------------------------------------------------
POSE_HOST="$WS/src/voxel_svio/output/pose.txt"
if [[ ! -s "$POSE_HOST" ]]; then
    echo "[voxel_svio] ERROR: $POSE_HOST is missing or empty" | tee -a "$LOG"
    exit 1
fi
cp "$POSE_HOST" "$OUT_DIR/trajectory.txt"
[[ -f "$WS/src/voxel_svio/output/parameter_list.txt" ]] && \
    cp "$WS/src/voxel_svio/output/parameter_list.txt" "$OUT_DIR/parameter_list.txt"
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

echo "[voxel_svio] done (run ${RUN_ID})" | tee -a "$LOG"
