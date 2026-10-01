#!/usr/bin/env bash
# Run ORB-SLAM3 on a converted sequence (cam0/, cam1/, times.txt).
# Usage: scripts/run/run_orbslam3.sh <dataset> <seq> [run_id=1] [run_type=vo]
#
# run_type selects binary + config + results tree:
#   vo      -> stereo_euroc          + <dataset>_stereo.yaml          (LC off)
#              -> results/vo/<dataset>/<seq>/orbslam3/run<N>/
#   vo-lc   -> stereo_euroc          + <dataset>_stereo_lc.yaml       (LC on)
#              -> results/vo-lc/<dataset>/<seq>/orbslam3/run<N>/
#   vio     -> stereo_inertial_euroc + <dataset>_stereo_inertial.yaml (LC off)
#              -> results/vio/<dataset>/<seq>/orbslam3/run<N>/
#   vio-lc  -> stereo_inertial_euroc + <dataset>_stereo_inertial_lc.yaml (LC on)
#              -> results/vio-lc/<dataset>/<seq>/orbslam3/run<N>/
#
# vio / vio-lc require:
#   - <dataset_seq>/mav0/cam0/data, /mav0/cam1/data, /mav0/imu0/data.csv  (EuRoC)
#   - <dataset_seq>/times.txt                                              (ns)
# The stereo_inertial_euroc binary reads the IMU CSV from mav0/imu0/data.csv.
set -euo pipefail
DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"
SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/orbslam3/run${RUN_ID}"
LOG_GLOBAL="$WS/logs/${DATASET}_${SEQ}_orbslam3_${RUN_TYPE}_run${RUN_ID}.log"

case "$RUN_TYPE" in
    vo)
        BIN=./Examples/Stereo/stereo_euroc
        CFG="$WS/configs/orbslam3/${DATASET}_stereo.yaml"
        ;;
    vo-lc)
        BIN=./Examples/Stereo/stereo_euroc
        CFG="$WS/configs/orbslam3/${DATASET}_stereo_lc.yaml"
        ;;
    vio)
        BIN=./Examples/Stereo-Inertial/stereo_inertial_euroc
        CFG="$WS/configs/orbslam3/${DATASET}_stereo_inertial.yaml"
        ;;
    vio-lc)
        BIN=./Examples/Stereo-Inertial/stereo_inertial_euroc
        CFG="$WS/configs/orbslam3/${DATASET}_stereo_inertial_lc.yaml"
        ;;
    *)
        echo "[orbslam3] unknown run_type: $RUN_TYPE (expected vo|vo-lc|vio|vio-lc)" >&2
        exit 2
        ;;
esac
# Select sequence-specific calibration first and reject a camera-rate mismatch
# before creating an output directory. Previously the 10 Hz field sequence used
# the generic 15 Hz VO config despite a correct sequence file already existing.
CONFIG_ARGS=(orbslam3 "$WS" "$DATASET" "$SEQ" "$RUN_TYPE")
[[ -n "${ORBSLAM3_CONFIG:-}" ]] && CONFIG_ARGS+=(--override "$ORBSLAM3_CONFIG")
CFG_SOURCE=$(python3 "$WS/scripts/run/_config_preflight.py" "${CONFIG_ARGS[@]}")

# This checkout reads the lower-case `loopClosing` key. Some legacy configs
# also contain `System.LoopClosing`, which upstream ignores. Generate the
# effective mode config so the result bucket and estimator behavior agree.
EFFECTIVE_CFG=$(mktemp -t orbslam3_cfg_XXXXXX.yaml)
LC_VALUE=0
[[ "$USE_LC" == "true" ]] && LC_VALUE=1
awk -v lc="$LC_VALUE" '
    BEGIN { saw_lc=0 }
    /^loopClosing:[[:space:]]*/ { print "loopClosing: " lc; saw_lc=1; next }
    /^System\.LoopClosing:[[:space:]]*/ { print "System.LoopClosing: " lc; next }
    { print }
    END { if (!saw_lc) print "loopClosing: " lc }
' "$CFG_SOURCE" > "$EFFECTIVE_CFG"
CFG="$EFFECTIVE_CFG"
[[ "$RUN_TYPE" =~ vio ]] && [[ ! -f "$SEQ_DIR/mav0/imu0/data.csv" ]] && {
    echo "[orbslam3] missing IMU: $SEQ_DIR/mav0/imu0/data.csv" >&2
    echo "[orbslam3] hint: python3 scripts/data/imu_to_euroc.py $SEQ_DIR" >&2
    exit 2
}
mkdir -p "$WS/logs"
prepare_fresh_run_dir "$OUT_DIR"

cd "$WS/src/ORB_SLAM3"
echo "[orbslam3] $DATASET/$SEQ type=${RUN_TYPE} run=${RUN_ID} -> $OUT_DIR" | tee "$LOG_GLOBAL" "$OUT_DIR/run_log.txt"
echo "[orbslam3] binary=$BIN  config_source=$CFG_SOURCE  effective_config=$CFG" | tee -a "$LOG_GLOBAL"

# Pangolin creates an X11 window even when its viewer is disabled in the
# benchmark config.  Supply a virtual display automatically on headless hosts.
RUN_PREFIX=()
if [[ -z "${DISPLAY:-}" ]]; then
    command -v xvfb-run >/dev/null || {
        echo "[orbslam3] ERROR: DISPLAY is unset and xvfb-run is not installed" | tee -a "$LOG_GLOBAL"
        exit 2
    }
    RUN_PREFIX=(xvfb-run -a)
    echo "[orbslam3] DISPLAY is unset; using xvfb-run -a" | tee -a "$LOG_GLOBAL"
fi

ESTIMATOR_COMMAND=(
    "$BIN"
    Vocabulary/ORBvoc.txt
    "$CFG"
    "$SEQ_DIR"
    "$SEQ_DIR/times.txt"
    "${DATASET}_${SEQ}_orbslam3"
)
if [[ "${ORBSLAM3_GDB:-0}" == "1" ]]; then
    command -v gdb >/dev/null || {
        echo "[orbslam3] ERROR: ORBSLAM3_GDB=1 but gdb is unavailable" | tee -a "$LOG_GLOBAL"
        exit 2
    }
    ESTIMATOR_COMMAND=(
        gdb --batch --return-child-result
        -ex "set pagination off"
        -ex "set print thread-events off"
        -ex run
        -ex "thread apply all backtrace"
        --args "${ESTIMATOR_COMMAND[@]}"
    )
    echo "[orbslam3] diagnostic mode: capturing all-thread backtrace with gdb" \
        | tee -a "$LOG_GLOBAL"
fi

# Resource monitor: GPU + CPU + RAM sampled every 1 s
prepare_resource_window "$OUT_DIR"
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" --pid "$$" --interval 1 \
    --start-file "$OUT_DIR/.resource_start" --stop-file "$OUT_DIR/.resource_stop" &
MONPID=$!
cleanup() {
    [[ -n "${MONPID:-}" ]] && kill "$MONPID" 2>/dev/null || true
    [[ -n "${EFFECTIVE_CFG:-}" ]] && rm -f "$EFFECTIVE_CFG"
}
trap cleanup EXIT

START=$(date +%s.%N)
mark_resource_start "$OUT_DIR"
# Pipe through a Python timestamper so each log line gets a relative offset (s).
set +e
"${RUN_PREFIX[@]}" "${ESTIMATOR_COMMAND[@]}" 2>&1 | \
  python3 -u -c "
import sys, time
t0 = time.time()
for line in sys.stdin:
    sys.stdout.write(f'{time.time()-t0:.3f} {line}')
    sys.stdout.flush()
" | tee -a "$OUT_DIR/run_log.txt" "$LOG_GLOBAL"
ORB_RC=${PIPESTATUS[0]}
set -e
END=$(date +%s.%N)
finish_resource_window "$OUT_DIR" "$MONPID"
MONPID=""

PROV_ARGS=(
    --artifact "estimator_config=$CFG"
    --artifact "estimator_config_source=$CFG_SOURCE"
    --artifact "vocabulary=$WS/src/ORB_SLAM3/Vocabulary/ORBvoc.txt"
    --source "algorithm=$WS/src/ORB_SLAM3"
    --binary "estimator=$WS/src/ORB_SLAM3/${BIN#./}"
    --param "use_imu=$USE_IMU"
    --param "use_lc=$USE_LC"
    --param "pacing_policy=dataset_timestamps"
    --param "gdb_diagnostic=${ORBSLAM3_GDB:-0}"
)
TRAJ_SRC="f_${DATASET}_${SEQ}_orbslam3.txt"
PROCESS_ARGS=(--process-exit-code "$ORB_RC")
POST_SAVE_NONZERO=false

if (( ORB_RC != 0 )); then
    if [[ "$ORB_RC" =~ ^(134|135|139)$ ]] && [[ -s "$TRAJ_SRC" ]] \
        && grep -Fq "End of saving trajectory to $TRAJ_SRC" "$OUT_DIR/run_log.txt"; then
        POST_SAVE_NONZERO=true
        echo "[orbslam3] deferring post-save shutdown signal acceptance (exit $ORB_RC) until trajectory validation" \
            | tee -a "$LOG_GLOBAL"
    else
        record_failed_run_meta "$OUT_DIR/run_meta.json" orbslam3 "$DATASET" "$SEQ" \
            "$RUN_ID" "$RUN_TYPE" "$ORB_RC" "estimator exited nonzero" "${PROV_ARGS[@]}"
        echo "[orbslam3] ERROR: estimator exited with status $ORB_RC" | tee -a "$LOG_GLOBAL"
        exit "$ORB_RC"
    fi
fi

if [[ ! -f "$TRAJ_SRC" ]]; then
    record_failed_run_meta "$OUT_DIR/run_meta.json" orbslam3 "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" 1 "trajectory was not produced" "${PROV_ARGS[@]}"
    echo "[orbslam3] ERROR: trajectory file not found — SLAM likely failed" | tee -a "$LOG_GLOBAL"
    exit 1
fi
mv "$TRAJ_SRC" "$OUT_DIR/trajectory_raw_ns.txt"
mv "kf_${DATASET}_${SEQ}_orbslam3.txt" "$OUT_DIR/keyframes.txt" 2>/dev/null || true

# stereo_euroc emits nanosecond timestamps and can repeat its last exact pose
# while tracking is lost. Preserve the source and remove only exact duplicate
# timestamp+pose rows; conflicting duplicates and time reversal are failures.
if ! python3 "$WS/scripts/results/canonicalize_orb_trajectory.py" \
    "$OUT_DIR/trajectory_raw_ns.txt" "$OUT_DIR/trajectory.txt" \
    --stats "$OUT_DIR/trajectory_filter.json" | tee -a "$LOG_GLOBAL"; then
    record_failed_run_meta "$OUT_DIR/run_meta.json" orbslam3 "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" "$ORB_RC" "trajectory canonicalization failed" "${PROV_ARGS[@]}"
    echo "[orbslam3] ERROR: trajectory failed canonical validation" | tee -a "$LOG_GLOBAL"
    exit 1
fi

PROV_ARGS+=(--param "trajectory_canonicalization=drop_exact_duplicate_timestamp_pose_rows")
if [[ "$POST_SAVE_NONZERO" == "true" ]]; then
    PROCESS_ARGS+=(
        --accepted-nonzero-exit
        --failure-reason "post-save shutdown signal after canonical trajectory validation"
    )
    echo "[orbslam3] accepting post-save shutdown signal (exit $ORB_RC); trajectory is canonical" \
        | tee -a "$LOG_GLOBAL"
fi

[[ -f "$OUT_DIR/keyframes.txt" ]] && \
awk '{printf "%.9f %s %s %s %s %s %s %s\n",$1/1e9,$2,$3,$4,$5,$6,$7,$8}' \
    "$OUT_DIR/keyframes.txt" > "$OUT_DIR/keyframes_s.txt" && \
mv "$OUT_DIR/keyframes_s.txt" "$OUT_DIR/keyframes.txt"

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt")
python3 -c "
import json
trajectory_filter=json.load(open('$OUT_DIR/trajectory_filter.json'))
print(json.dumps({
    'algo':'orbslam3','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
    'run_type':'$RUN_TYPE','use_imu':$([[ "$USE_IMU" == "true" ]] && echo True || echo False),
    'use_lc':$([[ "$USE_LC" == "true" ]] && echo True || echo False),
    'duration_s':$DUR,'frames':$NFR,
    'fps':$NFR/$DUR if $DUR>0 else 0,
    'trajectory_canonicalization':trajectory_filter
}))
" > "$OUT_DIR/run_meta.json"
enrich_run_meta "$OUT_DIR/run_meta.json" --measurement-mode paced "${PROV_ARGS[@]}" "${PROCESS_ARGS[@]}"
echo "[orbslam3] run ${RUN_ID} done in ${DUR}s, ${NFR} frames"
