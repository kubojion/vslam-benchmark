#!/usr/bin/env bash
# Run OpenVINS on a converted sequence (EuRoC-ASL layout under datasets/).
# Usage: scripts/run/run_openvins.sh <dataset> <seq> [run_id=1] [run_type=vio]
#
# OpenVINS is a visual-inertial filter (no loop closure in the open-source
# distribution). Supported run_type values:
#   vio     -> configs/openvins/<dataset>/estimator_config.yaml
#              -> results/vio/<dataset>/<seq>/openvins/run<N>/
# Other modes are not supported (rejected here so the benchmark wrapper
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
    *)
        echo "[openvins] run_type='$RUN_TYPE' not supported - OpenVINS is VIO only (no VO mode, no built-in LC)" >&2
        exit 2 ;;
esac

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
CFG_DIR="$WS/configs/openvins/$DATASET"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/openvins/run${RUN_ID}"
LOG_GLOBAL="$WS/logs/${DATASET}_${SEQ}_openvins_${RUN_TYPE}_run${RUN_ID}.log"
OPENVINS_IMAGE=openvins:humble
if [[ "$DATASET" == euroc_mav ]]; then OPENVINS_IMAGE=openvins:humble-shutdown-20261001; fi

[[ -d "$CFG_DIR" ]] || { echo "[openvins] missing config dir: $CFG_DIR" >&2; exit 2; }
[[ -f "$CFG_DIR/estimator_config.yaml" ]] || { echo "[openvins] missing $CFG_DIR/estimator_config.yaml" >&2; exit 2; }
[[ -d "$SEQ_DIR/mav0/cam0/data" && -d "$SEQ_DIR/mav0/cam1/data" ]] \
    || { echo "[openvins] missing $SEQ_DIR/mav0/cam{0,1}/data" >&2; exit 2; }
[[ -f "$SEQ_DIR/mav0/imu0/data.csv" ]] \
    || { echo "[openvins] missing IMU $SEQ_DIR/mav0/imu0/data.csv" >&2; exit 2; }

if ! docker image inspect "$OPENVINS_IMAGE" >/dev/null 2>&1; then
    echo "[openvins] docker image '$OPENVINS_IMAGE' not found" >&2
    echo "[openvins] build it first:  docker build -t openvins:humble -f src/open_vins/Dockerfile.benchmark src/open_vins" >&2
    exit 2
fi

mkdir -p "$WS/logs"
prepare_fresh_run_dir "$OUT_DIR"
CONTAINER=""
source "$WS/scripts/run/_owned_process.sh"
owned_ros2_domain
echo "[openvins] $DATASET/$SEQ type=${RUN_TYPE} run=${RUN_ID} -> $OUT_DIR" | tee "$LOG_GLOBAL" "$OUT_DIR/run_log.txt"

# Measure the host runner tree plus the ephemeral estimator container.  The
# monitor tolerates the container not existing until docker run starts.
RUN_CONTAINER="vslam_openvins_${DATASET}_${SEQ}_${RUN_ID}_$$"
prepare_resource_window "$OUT_DIR"
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" \
    --pid "$$" --container "$RUN_CONTAINER" --interval 1 \
    --start-file "$OUT_DIR/.resource_start" --stop-file "$OUT_DIR/.resource_stop" &
MONPID=$!
cleanup() {
    [[ -n "${MONPID:-}" ]] && kill "$MONPID" 2>/dev/null || true
    # Docker's unique ID binds cleanup to this attempt even if a name is reused.
    if [[ -s "$OUT_DIR/docker.cid" ]]; then
        docker stop --time 10 "$(cat "$OUT_DIR/docker.cid")" >/dev/null 2>&1 || true
    fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

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
    --cidfile "$OUT_DIR/docker.cid" \
    --network host \
    --user "$(id -u):$(id -g)" \
    --volume "$WS:/ws" \
    "${SEQ_MOUNT[@]}" \
    --workdir /ws \
    --env ROS_HOME=/tmp/vslam_ros \
    --env ROS_DOMAIN_ID="$ROS_DOMAIN_ID" --env ROS_LOCALHOST_ONLY=1 \
    --entrypoint /bin/bash \
    "$OPENVINS_IMAGE" \
    -c "
        set -eo pipefail
        source /opt/ros/humble/setup.bash
        source /colcon_ws/install/setup.bash
        WS=/ws
        OUT_DIR=/ws/${OUT_REL}
        CONTAINER=''
        source /ws/scripts/run/_owned_process.sh
        cleanup_stages() { owned_stop player || true; owned_stop node || true; }
        trap cleanup_stages EXIT
        trap 'exit 130' INT
        trap 'exit 143' TERM
        # Same namespace/parameters as subscribe.launch.py, with the native
        # process directly supervised. ros2 launch can return zero after a node
        # segfault and forward a second SIGINT during attempt cleanup.
        owned_run node /colcon_ws/install/lib/ov_msckf/run_subscribe_msckf \
            --ros-args -r __ns:=/ov_msckf \
            -p config_path:=/ws/configs/openvins/$DATASET/estimator_config.yaml \
            -p use_stereo:=true -p max_cameras:=2 -p verbosity:=INFO \
            -p save_total_state:=false \
            > /ws/${OUT_REL}/openvins_node.log 2>&1 &
        OV_PID=\$!
        sleep 2
        owned_run player python3 /ws/scripts/run/openvins_data_player.py \
            $SEQ_IN \
            /ws/${OUT_REL}/trajectory.txt \
            --rate ${OPENVINS_RATE:-1.0} \
            --start-delay 1.0 --end-wait 3.0 \
            --stats-out /ws/${OUT_REL}/transport_stats.json
        owned_stop node
        # Preserve the native status; separate state records forced shutdown.
        # A produced trajectory cannot conceal a nonzero estimator exit.
        wait \$OV_PID
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
    --param "process_isolation=attempt_token_private_ros2_domain"
    --param "playback_rate=${OPENVINS_RATE:-1.0}"
    --container-image "$OPENVINS_IMAGE"
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
