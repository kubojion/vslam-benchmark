#!/usr/bin/env bash
# Run SVO Pro (rpg_svo_pro_open, semi-direct stereo) on a sequence.
#
# Usage: scripts/run/run_svo_pro.sh <dataset> <seq> [run_id=1] [run_type=vo]
#
# run_type:
#   vo      -> stereo front end only                               -> results/vo/
#   vio     -> front end + sliding-window visual-inertial back end -> results/vio/
#   vio-lc  -> the same with DBoW2 loop closing / pose graph       -> results/vio-lc/
# There is no IMU-free loop closing in SVO Pro (no vo-lc). GNSS fusion is the separate
# rpg_svo_pro_gps code base (scripts/run/run_svo_pro_gps.sh).
#
# The authors' own offline runner (svo_ros/svo_benchmark) is used unmodified: it reads
# images and IMU from disk and waits for the back end after every frame.
#
# Reads:
#   datasets/<dataset>/<seq>/mav0/{cam0,cam1,imu0}   (EuRoC layout)
#   configs/sensors/<dataset>.json                   (shared calibration profile)
#   configs/svo_pro/benchmark.yaml                   (settings, same for all datasets)
#   src/svo_pro/svo_ros/param/vio_stereo.yaml        (upstream parameters)
#   IMU noise: upstream euroc_stereo.yaml for EuRoC, configs/okvis2/<dataset>_<seq>_vio.yaml otherwise
#
# Writes (under $RESULTS_ROOT/<dataset>/<seq>/svo_pro/run<N>/):
#   trajectory.txt   TUM (timestamp_s tx ty tz qx qy qz qw), pose of the IMU (body) frame
#   run_log.txt, resources.csv, run_meta.json, svo_effective_config.yaml, calib.yaml,
#   native/  (the node's trace directory: stamped_traj_estimate.txt, status.txt, ...)
set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"

case "$RUN_TYPE" in
    vo|vio|vio-lc) ;;
    vo-lc) echo "[svo_pro] ERROR: SVO Pro loop closing needs the visual-inertial back end; use vio-lc" >&2; exit 2 ;;
    *) echo "[svo_pro] ERROR: run_type must be vo, vio or vio-lc" >&2; exit 2 ;;
esac

REPO="$WS/src/svo_pro"
SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/svo_pro/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_svo_pro_${RUN_TYPE}_run${RUN_ID}.log"
SENSOR="$WS/configs/sensors/${DATASET}.json"
ALGO_CFG="${SVO_PRO_CONFIG:-$WS/configs/svo_pro/benchmark.yaml}"
BASE_CFG="$REPO/svo_ros/param/vio_stereo.yaml"
SVO_IMAGE="${SVO_PRO_IMAGE:-vslam_svo_pro:noetic}"
# The offline node waits for the back end without a timeout; if the back end rejects a
# frame (for example an IMU gap) it waits forever. Bound the attempt instead.
TIME_LIMIT_S="${SVO_PRO_TIME_LIMIT_S:-21600}"
PREP_ENV="${SVO_PRO_PREP_CONDA_ENV:-cuvslam}"   # host python with numpy, yaml, cv2

if [[ "$DATASET" == "euroc_mav" ]]; then
    IMU_FILE="$REPO/svo_ros/param/calib/euroc_stereo.yaml"; IMU_SRC="upstream:$IMU_FILE"
else
    IMU_FILE="$WS/configs/okvis2/${DATASET}_${SEQ}_vio.yaml"; IMU_SRC="okvis2:$IMU_FILE"
fi

[[ -e "$REPO/.git" ]] || { echo "[svo_pro] ERROR: source checkout missing at $REPO (run scripts/build/build_svo_pro.sh)" >&2; exit 2; }
for f in "$SENSOR" "$ALGO_CFG" "$BASE_CFG" "$IMU_FILE"; do
    [[ -f "$f" ]] || { echo "[svo_pro] ERROR: missing $f" >&2; exit 2; }
done
docker image inspect "$SVO_IMAGE" >/dev/null 2>&1 \
    || { echo "[svo_pro] ERROR: image $SVO_IMAGE not found (run scripts/build/build_svo_pro.sh)" >&2; exit 2; }
for f in mav0/cam0/data.csv mav0/cam1/data.csv mav0/imu0/data.csv; do
    [[ -f "$SEQ_DIR/$f" ]] || { echo "[svo_pro] ERROR: missing $SEQ_DIR/$f" >&2; exit 2; }
done

set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate "$PREP_ENV"
set -u
python3 "$WS/scripts/setup/build_sensor_profiles.py" --repo "$WS" --check > /dev/null \
    || { echo "[svo_pro] ERROR: sensor profiles are stale or inconsistent" >&2; exit 2; }

# One prepared folder per (sequence, sensor profile, IMU-noise source); reused by every repetition.
STAGE_KEY=$(cat "$SENSOR" "$IMU_FILE" | sha256sum | cut -c1-16)
STAGE="$WS/results/.cache/svo-pro-stage/$DATASET/$SEQ/$STAGE_KEY"
mkdir -p "$(dirname "$STAGE")"
python3 "$WS/scripts/run/_svo_pro_stage.py" stage --sequence "$SEQ_DIR" --sensor "$SENSOR" \
    --imu-params "$IMU_SRC" --out "$STAGE"
mapfile -t STAGE_MOUNTS < <(python3 -c "
import json
for m in json.load(open('$STAGE/stage.json'))['mounts']: print('--volume'); print(f'{m}:{m}:ro')")

mkdir -p "$WS/logs"
prepare_fresh_run_dir "$OUT_DIR"
CONTAINER=""
source "$WS/scripts/run/_owned_process.sh"
mkdir "$OUT_DIR/native"
OUT_REL=$(realpath --relative-to="$WS" "$OUT_DIR")
STAGE_REL=$(realpath --relative-to="$WS" "$STAGE")
python3 "$WS/scripts/run/_svo_pro_stage.py" config --stage "$STAGE" --base "$BASE_CFG" --override "$ALGO_CFG" \
    --mode "$RUN_TYPE" --stage-in-container "/ws/$STAGE_REL" --trace-in-container "/ws/$OUT_REL/native" \
    --out "$OUT_DIR/svo_effective_config.yaml"
cp "$STAGE/calib.yaml" "$OUT_DIR/calib.yaml"
echo "[svo_pro] $DATASET/$SEQ type=${RUN_TYPE} run=${RUN_ID} -> $OUT_DIR" | tee "$LOG" "$OUT_DIR/run_log.txt"

RUN_CONTAINER="vslam_svo_pro_${DATASET}_${SEQ}_${RUN_ID}_$$"
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

PROV_ARGS=(
    --artifact "camera_calibration=$SENSOR"
    --artifact "imu_noise_source=$IMU_FILE"
    --artifact "algorithm_config=$ALGO_CFG"
    --artifact "algorithm_defaults=$BASE_CFG"
    --artifact "effective_config=$OUT_DIR/svo_effective_config.yaml"
    --artifact "camera_imu_calibration=$OUT_DIR/calib.yaml"
    --source "algorithm=$REPO"
    --param "process_isolation=attempt_token_private_ros1_master"
    --param "output_frame=imu_body"
    --param "loop_closure=$USE_LC" --param "use_imu=$USE_IMU"
    --param "feed=authors_offline_benchmark_node_backend_synchronous"
    --param "time_limit_s=$TIME_LIMIT_S"
    --container-image "$SVO_IMAGE"
)

# The container has its own network namespace, so its ROS master cannot be seen
# by, or collide with, any other run on the host.
START=$(date +%s.%N)
mark_resource_start "$OUT_DIR"
set +e
timeout --signal=TERM --kill-after=60 "$TIME_LIMIT_S" docker run --rm \
    --name "$RUN_CONTAINER" \
    --cidfile "$OUT_DIR/docker.cid" \
    --user "$(id -u):$(id -g)" \
    --volume "$WS:/ws" \
    "${STAGE_MOUNTS[@]}" \
    --workdir /ws \
    --env HOME=/tmp --env ROS_HOME=/tmp/vslam_ros --env ROS_LOG_DIR=/tmp/vslam_ros/log \
    --entrypoint /bin/bash \
    "$SVO_IMAGE" \
    -c "
        set -eo pipefail
        source /opt/ros/noetic/setup.bash
        source /svo_ws/devel/setup.bash
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
        rosparam load /ws/${OUT_REL}/svo_effective_config.yaml /svo
        # Same invocation as the authors' svo_benchmarking/scripts/benchmark.py.
        owned_run node /svo_ws/devel/lib/svo_ros/svo_benchmark __name:=svo \
            --v=0 --logtostderr=1 --trial_idx=-1
    " 2>&1 | python3 -u -c "
import sys, time
t0 = time.time()
for line in sys.stdin:
    sys.stdout.write(f'{time.time()-t0:.3f} {line}'); sys.stdout.flush()
" | tee -a "$OUT_DIR/run_log.txt" "$LOG" > /dev/null
SVO_RC=${PIPESTATUS[0]}
set -e
END=$(date +%s.%N)
finish_resource_window "$OUT_DIR" "$MONPID"
MONPID=""
if (( SVO_RC != 0 )); then
    REASON="container pipeline exited nonzero"
    (( SVO_RC == 124 || SVO_RC == 137 )) && REASON="time limit of ${TIME_LIMIT_S}s reached (node did not finish)"
    record_failed_run_meta "$OUT_DIR/run_meta.json" svo_pro "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" "$SVO_RC" "$REASON" "${PROV_ARGS[@]}"
    echo "[svo_pro] ERROR: container exited with status $SVO_RC" | tee -a "$LOG"
    exit "$SVO_RC"
fi

RAW="$OUT_DIR/native/stamped_traj_estimate.txt"
if [[ -s "$RAW" ]]; then
    python3 "$WS/scripts/run/_svo_pro_stage.py" export --stage "$STAGE" --raw "$RAW" \
        --trajectory "$OUT_DIR/trajectory.txt" | tee -a "$LOG"
fi
if [[ ! -s "$OUT_DIR/trajectory.txt" ]]; then
    record_failed_run_meta "$OUT_DIR/run_meta.json" svo_pro "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" 1 "trajectory was not produced" "${PROV_ARGS[@]}"
    echo "[svo_pro] ERROR: no trajectory — run failed" | tee -a "$LOG"; exit 1
fi

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt")
NOFF=$(python3 -c "import json; print(json.load(open('$STAGE/stage.json'))['frames'])")
python3 -c "
import json
print(json.dumps({'algo':'svo_pro','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
                  'run_type':'$RUN_TYPE','use_imu':'$USE_IMU'=='true','use_lc':'$USE_LC'=='true',
                  'duration_s':$DUR,'frames':$NFR,'fps':$NOFF/$DUR if $DUR>0 else 0,
                  'frames_offered':$NOFF}))
" > "$OUT_DIR/run_meta.json"
enrich_run_meta "$OUT_DIR/run_meta.json" --measurement-mode max_throughput "${PROV_ARGS[@]}"
echo "[svo_pro] run ${RUN_ID} done in ${DUR}s, ${NFR} poses" | tee -a "$LOG"
