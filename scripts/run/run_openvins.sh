#!/usr/bin/env bash
# Run OpenVINS on a converted sequence (EuRoC-ASL layout under datasets/).
# Usage: scripts/run/run_openvins.sh <dataset> <seq> [run_id=1] [run_type=vio]
#
# OpenVINS is a visual-inertial filter (no loop closure in the open-source
# distribution). Supported run_type values:
#   vio     -> configs/openvins/<dataset>/estimator_config.yaml
#              -> results/vio/<dataset>/<seq>/openvins/run<N>/
# vo and vio-lc are NOT supported (rejected here so the benchmark wrapper
# does not silently misclassify the run).
#
# How it works:
#   - Spawns a Docker container from the openvins:humble image (built with
#     src/open_vins/Dockerfile.benchmark).
#   - Inside the container we:
#       1. ros2 launch ov_msckf subscribe.launch.py config_path=...
#       2. python3 openvins_data_player.py <seq_dir> <out_traj>
#         (publishes /cam0,/cam1 images and /imu0; subscribes to
#          /ov_msckf/odomimu and writes a TUM trajectory).
#   - The container exits when the player finishes; trajectory.txt and the run
#     log are written into the per-run results directory.

set -euo pipefail
DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vio}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"

case "$RUN_TYPE" in
    vio) ;;
    vo|vio-lc)
        echo "[openvins] run_type='$RUN_TYPE' not supported - OpenVINS is VIO only (no VO mode, no built-in LC)" >&2
        exit 2 ;;
esac

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
CFG_DIR="$WS/configs/openvins/$DATASET"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/openvins/run${RUN_ID}"
LOG_GLOBAL="$WS/logs/${DATASET}_${SEQ}_openvins_${RUN_TYPE}_run${RUN_ID}.log"

[[ -d "$CFG_DIR" ]] || { echo "[openvins] missing config dir: $CFG_DIR" >&2; exit 2; }
[[ -f "$CFG_DIR/estimator_config.yaml" ]] || { echo "[openvins] missing $CFG_DIR/estimator_config.yaml" >&2; exit 2; }
[[ -d "$SEQ_DIR/mav0/cam0/data" && -d "$SEQ_DIR/mav0/cam1/data" ]] \
    || { echo "[openvins] missing $SEQ_DIR/mav0/cam{0,1}/data" >&2; exit 2; }
[[ -f "$SEQ_DIR/mav0/imu0/data.csv" ]] \
    || { echo "[openvins] missing IMU $SEQ_DIR/mav0/imu0/data.csv" >&2; exit 2; }

if ! docker image inspect openvins:humble >/dev/null 2>&1; then
    echo "[openvins] docker image 'openvins:humble' not found" >&2
    echo "[openvins] build it first:  docker build -t openvins:humble -f src/open_vins/Dockerfile.benchmark src/open_vins" >&2
    exit 2
fi

mkdir -p "$WS/logs"
prepare_fresh_run_dir "$OUT_DIR"
echo "[openvins] $DATASET/$SEQ type=${RUN_TYPE} run=${RUN_ID} -> $OUT_DIR" | tee "$LOG_GLOBAL" "$OUT_DIR/run_log.txt"

# Measure the host runner tree plus the ephemeral estimator container.  The
# monitor tolerates the container not existing until docker run starts.
RUN_CONTAINER="vslam_openvins_${DATASET}_${SEQ}_${RUN_ID}_$$"
prepare_resource_window "$OUT_DIR"
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" \
    --pid "$$" --container "$RUN_CONTAINER" --interval 1 \
    --start-file "$OUT_DIR/.resource_start" --stop-file "$OUT_DIR/.resource_stop" &
MONPID=$!
trap '[[ -n "${MONPID:-}" ]] && kill "$MONPID" 2>/dev/null || true' EXIT

OUT_REL=$(realpath --relative-to="$WS" "$OUT_DIR")

# The sequence dir may be a symlink whose real path is OUTSIDE $WS (e.g.
# datasets/hortimulti/strawberry03 -> /home/.../data/horti/Strawberry-03). It
# then appears as a dangling symlink inside the /ws mount and the data player
# finds no frames. Detect that and bind-mount the real path at /seqdata.
SEQ_REAL=$(realpath "$SEQ_DIR")
SEQ_REL=$(realpath --relative-to="$WS" "$SEQ_DIR")
SEQ_MOUNT=()
if [[ "$SEQ_REL" != ../* ]]; then
    SEQ_IN="/ws/datasets/$DATASET/$SEQ"
else
    SEQ_IN="/seqdata"
    SEQ_MOUNT=(--volume "$SEQ_REAL:/seqdata:ro")
    echo "[openvins] sequence resolves outside \$WS ($SEQ_REAL); bind-mounting at /seqdata"
fi

# We mount the workspace at /ws inside the container. host UID/GID is passed
# through so the trajectory file is owned by the user (not root).
START=$(date +%s.%N)
mark_resource_start "$OUT_DIR"
set +e
docker run --rm \
    --name "$RUN_CONTAINER" \
    --network host \
    --user "$(id -u):$(id -g)" \
    --volume "$WS:/ws" \
    "${SEQ_MOUNT[@]}" \
    --workdir /ws \
    --env HOME=/tmp \
    --entrypoint /bin/bash \
    openvins:humble \
    -c "
        set -e
        source /opt/ros/humble/setup.bash
        source /colcon_ws/install/setup.bash
        ros2 launch ov_msckf subscribe.launch.py \
            config_path:=/ws/configs/openvins/$DATASET/estimator_config.yaml \
            use_stereo:=true max_cameras:=2 verbosity:=INFO \
            > /ws/${OUT_REL}/openvins_node.log 2>&1 &
        OV_PID=\$!
        sleep 2
        python3 /ws/scripts/run/openvins_data_player.py \
            $SEQ_IN \
            /ws/${OUT_REL}/trajectory.txt \
            --rate ${OPENVINS_RATE:-1.0} \
            --start-delay 1.0 --end-wait 3.0 \
            --stats-out /ws/${OUT_REL}/transport_stats.json
        kill -INT \$OV_PID 2>/dev/null || true
        # ros2 launch doesn't always exit on SIGINT; force-kill after a grace period.
        for i in 1 2 3 4 5; do
            kill -0 \$OV_PID 2>/dev/null || break
            sleep 1
        done
        if kill -0 \$OV_PID 2>/dev/null; then
            pkill -TERM -P \$OV_PID 2>/dev/null || true
            kill -TERM \$OV_PID 2>/dev/null || true
            sleep 2
            pkill -KILL -f run_subscribe_msckf 2>/dev/null || true
            kill -KILL \$OV_PID 2>/dev/null || true
        fi
        wait \$OV_PID 2>/dev/null || true
    " 2>&1 | \
  python3 -u -c "
import sys, time
t0 = time.time()
for line in sys.stdin:
    sys.stdout.write(f'{time.time()-t0:.3f} {line}')
    sys.stdout.flush()
" | tee -a "$OUT_DIR/run_log.txt" "$LOG_GLOBAL"
OPENVINS_RC=${PIPESTATUS[0]}
set -e
END=$(date +%s.%N)
finish_resource_window "$OUT_DIR" "$MONPID"
MONPID=""

PROV_ARGS=(
    --artifact "estimator_config=$CFG_DIR/estimator_config.yaml"
    --artifact "imu_calibration=$CFG_DIR/kalibr_imu_chain.yaml"
    --artifact "camera_imu_calibration=$CFG_DIR/kalibr_imucam_chain.yaml"
    --source "algorithm=$WS/src/open_vins"
    --param "playback_rate=${OPENVINS_RATE:-1.0}"
    --container-image openvins:humble
)
if (( OPENVINS_RC != 0 )); then
    record_failed_run_meta "$OUT_DIR/run_meta.json" openvins "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" "$OPENVINS_RC" "container pipeline exited nonzero" "${PROV_ARGS[@]}"
    echo "[openvins] ERROR: container exited with status $OPENVINS_RC" | tee -a "$LOG_GLOBAL"
    exit "$OPENVINS_RC"
fi

if [[ ! -s "$OUT_DIR/trajectory.txt" ]]; then
    record_failed_run_meta "$OUT_DIR/run_meta.json" openvins "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" 1 "trajectory was not produced" "${PROV_ARGS[@]}"
    echo "[openvins] ERROR: empty/missing $OUT_DIR/trajectory.txt - run failed" | tee -a "$LOG_GLOBAL"
    exit 1
fi

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt")
python3 -c "
import json
print(json.dumps({
    'algo':'openvins','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
    'run_type':'$RUN_TYPE',
    'duration_s':$DUR,'frames':$NFR,
    'fps':$NFR/$DUR if $DUR>0 else 0
}))
" > "$OUT_DIR/run_meta.json"
enrich_run_meta "$OUT_DIR/run_meta.json" --measurement-mode transport \
    --transport-stats "$OUT_DIR/transport_stats.json" "${PROV_ARGS[@]}"
echo "[openvins] run ${RUN_ID} done in ${DUR}s, ${NFR} poses"
