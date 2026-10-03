#!/usr/bin/env bash
# Run DSOL (Direct Sparse Odometry Lite, stereo, direct) on a sequence.
#
# Usage: scripts/run/run_dsol.sh <dataset> <seq> [run_id=1] [run_type=vo]
#
# DSOL is visual odometry only: no IMU, no loop closure. run_type must be vo.
# The unmodified upstream offline node (sv_dsol_node_data) is used with its generic
# stereo-folder reader. That reader has no ground-truth input; the node's motion
# model is constant velocity (the gyro prior of the live node is not used).
#
# Reads:
#   datasets/<dataset>/<seq>/mav0/{cam0,cam1}       (EuRoC layout)
#   configs/sensors/<dataset>.json                  (shared calibration profile)
#   configs/dsol/benchmark.yaml                     (estimator settings, same for all datasets)
#   src/dsol/config/dsol.yaml                       (upstream defaults)
#
# Writes (under $RESULTS_ROOT/<dataset>/<seq>/dsol/run<N>/):
#   trajectory.txt   TUM (timestamp_s tx ty tz qx qy qz qw), pose of cam0 (left optical frame)
#   run_log.txt, resources.csv, run_meta.json, dsol_effective_config.yaml,
#   native/dsol_raw.txt (frame-index poses of the rectified left camera)
#
# Image preparation (results/.cache/dsol-stage/) happens before the timed window:
# symlinks for pre-rectified datasets, rectified PNGs for raw EuRoC.
set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"

[[ "$RUN_TYPE" == "vo" ]] || { echo "[dsol] ERROR: DSOL is stereo VO only; run_type must be vo" >&2; exit 2; }

REPO="$WS/src/dsol"
SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/dsol/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_dsol_${RUN_TYPE}_run${RUN_ID}.log"
SENSOR="$WS/configs/sensors/${DATASET}.json"
ALGO_CFG="${DSOL_CONFIG:-$WS/configs/dsol/benchmark.yaml}"
BASE_CFG="$REPO/config/dsol.yaml"
DSOL_IMAGE="${DSOL_IMAGE:-vslam_dsol:noetic}"
PREP_ENV="${DSOL_PREP_CONDA_ENV:-cuvslam}"   # host python with cv2, numpy, scipy, yaml

[[ -d "$REPO/.git" ]] || { echo "[dsol] ERROR: source checkout missing at $REPO (run scripts/build/build_dsol.sh)" >&2; exit 2; }
[[ -f "$SENSOR" ]] || { echo "[dsol] ERROR: no sensor profile at $SENSOR" >&2; exit 2; }
[[ -f "$ALGO_CFG" && -f "$BASE_CFG" ]] || { echo "[dsol] ERROR: missing $ALGO_CFG or $BASE_CFG" >&2; exit 2; }
docker image inspect "$DSOL_IMAGE" >/dev/null 2>&1 \
    || { echo "[dsol] ERROR: image $DSOL_IMAGE not found (run scripts/build/build_dsol.sh)" >&2; exit 2; }
for f in mav0/cam0/data.csv mav0/cam1/data.csv; do
    [[ -f "$SEQ_DIR/$f" ]] || { echo "[dsol] ERROR: missing $SEQ_DIR/$f" >&2; exit 2; }
done

set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate "$PREP_ENV"
set -u
python3 "$WS/scripts/setup/build_sensor_profiles.py" --repo "$WS" --check > /dev/null \
    || { echo "[dsol] ERROR: sensor profiles are stale or inconsistent" >&2; exit 2; }

# One prepared copy per (sequence, sensor profile); reused by every repetition.
STAGE="$WS/results/.cache/dsol-stage/$DATASET/$SEQ/$(sha256sum "$SENSOR" | cut -c1-16)/realsense"
mkdir -p "$(dirname "$STAGE")"
python3 "$WS/scripts/run/_dsol_stage.py" stage --sequence "$SEQ_DIR" --sensor "$SENSOR" --out "$STAGE" > /dev/null
FPS=$(python3 -c "import json; print(json.load(open('$STAGE/stage.json'))['fps'])")
mapfile -t STAGE_MOUNTS < <(python3 -c "
import json
for m in json.load(open('$STAGE/stage.json'))['mounts']: print('--volume'); print(f'{m}:{m}:ro')")

mkdir -p "$WS/logs"
prepare_fresh_run_dir "$OUT_DIR"
CONTAINER=""
source "$WS/scripts/run/_owned_process.sh"
mkdir "$OUT_DIR/native"
python3 "$WS/scripts/run/_dsol_stage.py" merge-config --base "$BASE_CFG" --override "$ALGO_CFG" \
    --out "$OUT_DIR/dsol_effective_config.yaml"
cp "$STAGE/calib.txt" "$OUT_DIR/native/calib.txt"
echo "[dsol] $DATASET/$SEQ type=${RUN_TYPE} run=${RUN_ID} -> $OUT_DIR" | tee "$LOG" "$OUT_DIR/run_log.txt"

RUN_CONTAINER="vslam_dsol_${DATASET}_${SEQ}_${RUN_ID}_$$"
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
STAGE_REL=$(realpath --relative-to="$WS" "$STAGE")

PROV_ARGS=(
    --artifact "camera_calibration=$SENSOR"
    --artifact "algorithm_config=$ALGO_CFG"
    --artifact "algorithm_defaults=$BASE_CFG"
    --artifact "effective_config=$OUT_DIR/dsol_effective_config.yaml"
    --artifact "stage_calibration=$OUT_DIR/native/calib.txt"
    --source "algorithm=$REPO"
    --param "process_isolation=attempt_token_private_ros1_master"
    --param "output_frame=cam0_left_optical"
    --param "motion_model=constant_velocity_alpha_0.5_no_gyro"
    --param "tbb=1" --param "freq=$FPS"
    --param "image_preparation=outside_timed_window"
    --container-image "$DSOL_IMAGE"
)

# The container has its own network namespace, so its ROS master cannot be seen
# by, or collide with, any other run on the host.
START=$(date +%s.%N)
mark_resource_start "$OUT_DIR"
set +e
docker run --rm \
    --name "$RUN_CONTAINER" \
    --cidfile "$OUT_DIR/docker.cid" \
    --user "$(id -u):$(id -g)" \
    --volume "$WS:/ws" \
    "${STAGE_MOUNTS[@]}" \
    --workdir /ws \
    --env HOME=/tmp --env ROS_HOME=/tmp/vslam_ros --env ROS_LOG_DIR=/tmp/vslam_ros/log \
    --entrypoint /bin/bash \
    "$DSOL_IMAGE" \
    -c "
        set -eo pipefail
        source /opt/ros/noetic/setup.bash
        source /catkin_ws/devel/setup.bash
        WS=/ws
        OUT_DIR=/ws/${OUT_REL}
        CONTAINER=''
        source /ws/scripts/run/_owned_process.sh
        cleanup_stages() { owned_stop node || true; owned_stop master || true; }
        trap cleanup_stages EXIT
        trap 'exit 130' INT
        trap 'exit 143' TERM
        owned_run master roscore > /ws/${OUT_REL}/native/roscore.log 2>&1 &
        for i in \$(seq 1 50); do rosparam list >/dev/null 2>&1 && break; sleep 0.2; done
        rosparam load /ws/${OUT_REL}/dsol_effective_config.yaml /dsol_data
        # Same private parameters as upstream launch/dsol_data.launch, without display.
        owned_run node /catkin_ws/devel/lib/dsol/sv_dsol_node_data __name:=dsol_data \
            _tbb:=1 _log:=0 _vis:=0 _wait_ms:=0 _freq:=$FPS \
            _data_dir:=/ws/${STAGE_REL} _save:=/ws/${OUT_REL}/native/dsol_raw.txt \
            _data_max_depth:=100.0 _cloud_max_depth:=50.0 _motion_alpha:=0.5 \
            _start:=0 _end:=0 _reverse:=false
    " 2>&1 | python3 -u -c "
import sys, time
t0 = time.time()
for line in sys.stdin:
    sys.stdout.write(f'{time.time()-t0:.3f} {line}'); sys.stdout.flush()
" | tee -a "$OUT_DIR/run_log.txt" "$LOG" > /dev/null
DSOL_RC=${PIPESTATUS[0]}
set -e
END=$(date +%s.%N)
finish_resource_window "$OUT_DIR" "$MONPID"
MONPID=""
if (( DSOL_RC != 0 )); then
    record_failed_run_meta "$OUT_DIR/run_meta.json" dsol "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" "$DSOL_RC" "container pipeline exited nonzero" "${PROV_ARGS[@]}"
    echo "[dsol] ERROR: container exited with status $DSOL_RC" | tee -a "$LOG"
    exit "$DSOL_RC"
fi

if [[ -s "$OUT_DIR/native/dsol_raw.txt" ]]; then
    python3 "$WS/scripts/run/_dsol_stage.py" export --stage "$STAGE" \
        --raw "$OUT_DIR/native/dsol_raw.txt" --trajectory "$OUT_DIR/trajectory.txt" | tee -a "$LOG"
fi
if [[ ! -s "$OUT_DIR/trajectory.txt" ]]; then
    record_failed_run_meta "$OUT_DIR/run_meta.json" dsol "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" 1 "trajectory was not produced" "${PROV_ARGS[@]}"
    echo "[dsol] ERROR: no trajectory — run failed" | tee -a "$LOG"; exit 1
fi

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt")
NOFF=$(python3 -c "import json; print(json.load(open('$STAGE/stage.json'))['frames'])")
NFAIL=$(grep -c 'Tracking failed' "$OUT_DIR/run_log.txt" || true)
python3 -c "
import json
print(json.dumps({'algo':'dsol','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
                  'run_type':'$RUN_TYPE','use_imu':False,'use_lc':False,
                  'duration_s':$DUR,'frames':$NFR,'fps':$NFR/$DUR if $DUR>0 else 0,
                  'frames_offered':$NOFF,'tracking_failed_warnings':$NFAIL}))
" > "$OUT_DIR/run_meta.json"
enrich_run_meta "$OUT_DIR/run_meta.json" --measurement-mode max_throughput "${PROV_ARGS[@]}"
echo "[dsol] run ${RUN_ID} done in ${DUR}s, ${NFR} poses" | tee -a "$LOG"
