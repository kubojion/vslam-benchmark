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
#   - Spawns a Docker container from the input-delivery image (openvins:humble
#     from src/open_vins/Dockerfile.benchmark, plus the native patches in
#     scripts/patches/; build record in openvins-ros2-input-delivery-v6.json).
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
source "$WS/scripts/run/_rosario_profile.sh"
check_rosario_candidate openvins

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
CFG_DIR="$WS/configs/openvins/$DATASET"
if [[ -n "${ROSARIO_VIO_PROFILE:-}" ]]; then
    CFG_DIR="$WS/configs/candidates/rosario-vio-20261002/$ROSARIO_VIO_PROFILE"
fi
# Optional alternative configuration directory (a labelled sensitivity profile).
# It must resolve inside $WS/configs so it is part of the reviewed source tree.
if [[ -n "${OPENVINS_CONFIG_DIR:-}" ]]; then
    [[ -z "${ROSARIO_VIO_PROFILE:-}" ]] \
        || { echo '[openvins] OPENVINS_CONFIG_DIR and ROSARIO_VIO_PROFILE are mutually exclusive' >&2; exit 2; }
    case "$OPENVINS_CONFIG_DIR" in
        /*) CFG_DIR="$OPENVINS_CONFIG_DIR" ;;
        *)  CFG_DIR="$WS/$OPENVINS_CONFIG_DIR" ;;
    esac
    CFG_DIR=$(realpath -e "$CFG_DIR") \
        || { echo "[openvins] OPENVINS_CONFIG_DIR does not exist: $OPENVINS_CONFIG_DIR" >&2; exit 2; }
    [[ "$CFG_DIR" == "$(realpath -e "$WS")/configs/"* ]] \
        || { echo "[openvins] OPENVINS_CONFIG_DIR must resolve under \$WS/configs: $CFG_DIR" >&2; exit 2; }
fi
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/openvins/run${RUN_ID}"
LOG_GLOBAL="$WS/logs/${DATASET}_${SEQ}_openvins_${RUN_TYPE}_run${RUN_ID}.log"
OPENVINS_VERBOSITY=INFO
if [[ -n "${ROSARIO_VIO_PROFILE:-}" ]]; then OPENVINS_VERBOSITY=DEBUG; fi
# Input-delivery image (21 October 2026): the shutdown-repaired build plus the
# application receipt barriers of scripts/patches/openvins-ros2-input-delivery-v6.patch.
# Validated on full Rosario and CitrusFarm recordings in the noise experiment.
# The tag is checked against the validated image ID before every run.
OPENVINS_IMAGE=openvins:noise-delivery-audit-20261010-v6
OPENVINS_IMAGE_ID=sha256:2f74b56e67a7f887d0a495d38226379584e90c267090d1d21efdd07618d7aa31

# Input delivery. Defaults are the production policy: reliable IMU QoS,
# application receipt barriers (flow control) with an explicit end-of-recording
# drain, and the large shared-memory transport for full-size images. Wall-clock
# playback may slow down; sensor timestamps never change. Other values exist
# only to reproduce the earlier delivery for diagnostics and are recorded.
OPENVINS_IMU_RELIABILITY=${OPENVINS_IMU_RELIABILITY:-reliable}
OPENVINS_END_OF_STREAM_DRAIN=${OPENVINS_END_OF_STREAM_DRAIN:-1}
OPENVINS_FLOW_CONTROL=${OPENVINS_FLOW_CONTROL:-1}
OPENVINS_TRANSPORT_PROFILE=${OPENVINS_TRANSPORT_PROFILE:-large_shm}
TRANSPORT_ARGS=()
TRANSPORT_ARTIFACTS=()
OPENVINS_LOCALHOST_ONLY=1
case "$OPENVINS_TRANSPORT_PROFILE" in
    default) ;;
    large_shm)
        TRANSPORT_XML="$WS/configs/ros/openvins-local-large-images.xml"
        [[ -f "$TRANSPORT_XML" ]] || { echo '[openvins] missing local transport profile' >&2; exit 2; }
        # Humble's localhost-only switch appends another default-size SHM
        # transport. The XML instead specifies ONLY loopback UDP plus 32MiB SHM.
        OPENVINS_LOCALHOST_ONLY=0
        TRANSPORT_ARGS=(--shm-size 128m --env RMW_IMPLEMENTATION=rmw_fastrtps_cpp
            --env FASTRTPS_DEFAULT_PROFILES_FILE=/ws/configs/ros/openvins-local-large-images.xml)
        TRANSPORT_ARTIFACTS=(--artifact "dds_transport_profile=$TRANSPORT_XML")
        ;;
    *) echo '[openvins] invalid transport profile' >&2; exit 2 ;;
esac
case "$OPENVINS_FLOW_CONTROL" in
    0) ;;
    1) [[ "$OPENVINS_END_OF_STREAM_DRAIN" == 1 ]] || { echo '[openvins] flow control requires end drain' >&2; exit 2; } ;;
    *) echo '[openvins] invalid flow-control policy' >&2; exit 2 ;;
esac
case "$OPENVINS_END_OF_STREAM_DRAIN" in
    0|1) ;;
    *) echo '[openvins] invalid end-of-recording policy' >&2; exit 2 ;;
esac
case "$OPENVINS_IMU_RELIABILITY" in
    best_effort|reliable) ;;
    *) echo '[openvins] invalid IMU reliability policy' >&2; exit 2 ;;
esac
# The post-run delivery gate applies to the production policy only.
DELIVERY_GATE=not_applied_nonproduction_policy
if [[ "$OPENVINS_IMU_RELIABILITY" == reliable && "$OPENVINS_END_OF_STREAM_DRAIN" == 1 \
      && "$OPENVINS_FLOW_CONTROL" == 1 && "$OPENVINS_TRANSPORT_PROFILE" == large_shm ]]; then
    DELIVERY_GATE=exact_receipt_end_drain_flow_control
fi

[[ -d "$CFG_DIR" ]] || { echo "[openvins] missing config dir: $CFG_DIR" >&2; exit 2; }
[[ -f "$CFG_DIR/estimator_config.yaml" ]] || { echo "[openvins] missing $CFG_DIR/estimator_config.yaml" >&2; exit 2; }
[[ -d "$SEQ_DIR/mav0/cam0/data" && -d "$SEQ_DIR/mav0/cam1/data" ]] \
    || { echo "[openvins] missing $SEQ_DIR/mav0/cam{0,1}/data" >&2; exit 2; }
[[ -f "$SEQ_DIR/mav0/imu0/data.csv" ]] \
    || { echo "[openvins] missing IMU $SEQ_DIR/mav0/imu0/data.csv" >&2; exit 2; }

if ! docker image inspect "$OPENVINS_IMAGE" >/dev/null 2>&1; then
    echo "[openvins] docker image '$OPENVINS_IMAGE' not found" >&2
    echo "[openvins] see scripts/patches/openvins-ros2-input-delivery-v6.json for its build record" >&2
    exit 2
fi
[[ "$(docker image inspect --format '{{.Id}}' "$OPENVINS_IMAGE")" == "$OPENVINS_IMAGE_ID" ]] \
    || { echo "[openvins] $OPENVINS_IMAGE is not the validated image $OPENVINS_IMAGE_ID" >&2; exit 2; }

mkdir -p "$WS/logs"
prepare_fresh_run_dir "$OUT_DIR"
snapshot_rosario_candidate
if [[ -n "${ROSARIO_VIO_PROFILE:-}" ]]; then
    CFG_DIR="$ROSARIO_PROFILE_DIR"
fi
CFG_REL=$(realpath --relative-to="$WS" "$CFG_DIR")
[[ "$CFG_REL" != ../* ]] || { echo '[openvins] selected config must be within workspace' >&2; exit 2; }
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

# Prepared prefixes and clips keep absolute per-image symlinks into the original
# read-only dataset. Mount their resolved image directories as well as the
# sequence table; mounting /ws alone does not make those targets accessible.
python3 "$WS/scripts/run/_openvins_image_mounts.py" "$SEQ_DIR" > "$OUT_DIR/image-bind-mounts.json"
mapfile -t IMAGE_DIRECTORIES < <(python3 -c 'import json,sys; print("\n".join(json.load(open(sys.argv[1]))["directories"]))' "$OUT_DIR/image-bind-mounts.json")
IMAGE_MOUNTS=()
for image_directory in "${IMAGE_DIRECTORIES[@]}"; do
    IMAGE_MOUNTS+=(--volume "$image_directory:$image_directory:ro")
done

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
    "${IMAGE_MOUNTS[@]}" \
    --workdir /ws \
    --env ROS_HOME=/tmp/vslam_ros \
    --env OPENVINS_IMU_RELIABILITY="$OPENVINS_IMU_RELIABILITY" \
    --env OPENVINS_END_OF_STREAM_DRAIN="$OPENVINS_END_OF_STREAM_DRAIN" \
    --env OPENVINS_FLOW_CONTROL="$OPENVINS_FLOW_CONTROL" \
    "${TRANSPORT_ARGS[@]}" \
    --env ROS_DOMAIN_ID="$ROS_DOMAIN_ID" --env ROS_LOCALHOST_ONLY="$OPENVINS_LOCALHOST_ONLY" \
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
        export OPENVINS_INPUT_RECEIPT=/ws/${OUT_REL}/openvins_input_receipt.json
        owned_run node /colcon_ws/install/lib/ov_msckf/run_subscribe_msckf \
            --ros-args -r __ns:=/ov_msckf \
            -p config_path:=/ws/$CFG_REL/estimator_config.yaml \
            -p use_stereo:=true -p max_cameras:=2 -p verbosity:=$OPENVINS_VERBOSITY \
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
    "${PROFILE_PROV_ARGS[@]}"
    "${TRANSPORT_ARTIFACTS[@]}"
    --artifact "estimator_config=$CFG_DIR/estimator_config.yaml"
    --artifact "imu_calibration=$CFG_DIR/kalibr_imu_chain.yaml"
    --artifact "camera_imu_calibration=$CFG_DIR/kalibr_imucam_chain.yaml"
    --artifact "image_bind_mounts=$OUT_DIR/image-bind-mounts.json"
    --source "algorithm=$WS/src/open_vins"
    --param "process_isolation=attempt_token_private_ros2_domain"
    --param "playback_rate=${OPENVINS_RATE:-1.0}"
    --param "config_dir=$CFG_REL"
    --param "imu_reliability=$OPENVINS_IMU_RELIABILITY"
    --param "end_of_recording_drain=$OPENVINS_END_OF_STREAM_DRAIN"
    --param "flow_control=$OPENVINS_FLOW_CONTROL"
    --param "transport_profile=$OPENVINS_TRANSPORT_PROFILE"
    --param "ros_localhost_only=$OPENVINS_LOCALHOST_ONLY"
    --param "delivery_gate=$DELIVERY_GATE"
    --param "container_image_id=$OPENVINS_IMAGE_ID"
    --param "native_verbosity=$OPENVINS_VERBOSITY"
    --container-image "$OPENVINS_IMAGE"
)
# Audit native input receipts whenever they exist (also after a failed
# pipeline, as review evidence). Only the production policy is gated.
if [[ -s "$OUT_DIR/openvins_input_receipt.json" && -s "$OUT_DIR/transport_stats.json" ]]; then
    set +e
    python3 "$WS/scripts/run/_openvins_delivery.py" "$OUT_DIR" "$SEQ_DIR" \
        > "$OUT_DIR/openvins_delivery_audit.json"
    GATE_RC=$?
    set -e
    PROV_ARGS+=(--artifact "delivery_audit=$OUT_DIR/openvins_delivery_audit.json")
else
    GATE_RC=2
fi
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

# Input loss is an infrastructure fault, never an estimator result.
if [[ "$DELIVERY_GATE" != not_applied_nonproduction_policy ]] && (( GATE_RC != 0 )); then
    record_failed_run_meta "$OUT_DIR/run_meta.json" openvins "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" 3 "input delivery audit failed" "${PROV_ARGS[@]}"
    echo "[openvins] ERROR: input delivery audit failed - see $OUT_DIR/openvins_delivery_audit.json" | tee -a "$LOG_GLOBAL"
    exit 3
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
