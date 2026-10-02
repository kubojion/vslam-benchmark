#!/usr/bin/env bash
# Run Basalt stereo VO / VIO on a sequence.
# Usage: scripts/run/run_basalt.sh <dataset> <seq> [run_id=1] [run_type=vo]
#
# run_type selects results tree AND whether IMU is used:
#   vo      -> results/vo/<dataset>/<seq>/basalt/run<N>/         (--use-imu false)
#   vio     -> results/vio/<dataset>/<seq>/basalt/run<N>/        (--use-imu true)
# Basalt does not implement loop closure, so LC run types are rejected.
#
# Outputs:
#   trajectory.txt  - TUM format (timestamp_s tx ty tz qx qy qz qw)
#   run_log.txt     - timestamped console output
#   resources.csv   - CPU+RAM sampled every 1 s
#   run_meta.json   - frames, duration, fps
#
# Dependencies:
#   basalt_vio must be on PATH (source ~/.basalt/env or add ~/.local/bin to PATH)
#   configs/basalt/<dataset>_calib.json  - stereo calibration (pinhole, rectified)
#   configs/basalt/{vo,vio}_config.json  - upstream estimator profiles
set -euo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"
SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/basalt/run${RUN_ID}"
LOG_GLOBAL="$WS/logs/${DATASET}_${SEQ}_basalt_${RUN_TYPE}_run${RUN_ID}.log"
CALIB="${BASALT_CALIBRATION:-$WS/configs/basalt/${DATASET}_calib.json}"
case "$RUN_TYPE" in
    vo|vio) ;;
    *)
        echo "[basalt] ERROR: Basalt supports only vo and vio (no loop closure)" >&2
        exit 2
        ;;
esac
source "$WS/scripts/run/_rosario_profile.sh"
check_rosario_candidate basalt

# Rosario's 49.7 mm baseline needs the recorded 30 mm VO triangulation gate.
# Other datasets retain the upstream 50 mm gate; do not change them implicitly.
CONFIG_ARGS=(basalt "$WS" "$DATASET" "$SEQ" "$RUN_TYPE" --calibration "$CALIB")
[[ -n "${BASALT_CONFIG:-}" ]] && CONFIG_ARGS+=(--override "$BASALT_CONFIG")
if [[ -n "${ROSARIO_VIO_PROFILE:-}" ]]; then
    CALIB="$WS/configs/candidates/rosario-vio-20261002/$ROSARIO_VIO_PROFILE/calibration.json"
    CONFIG_ARGS=(basalt "$WS" "$DATASET" "$SEQ" "$RUN_TYPE" --calibration "$CALIB"
        --override "$WS/configs/candidates/rosario-vio-20261002/$ROSARIO_VIO_PROFILE/vio_config.json")
fi
ESTIMATOR_CFG=$(python3 "$WS/scripts/run/_config_preflight.py" "${CONFIG_ARGS[@]}")
CALIB=$(realpath -e "$CALIB")
ESTIMATOR_CFG=$(realpath -e "$ESTIMATOR_CFG")

# ── PATH: source Basalt env to ensure basalt_vio is available ────────────────
if [[ -f "$HOME/.basalt/env" ]]; then
    # shellcheck source=/dev/null
    source "$HOME/.basalt/env"
fi
if ! command -v basalt_vio &>/dev/null; then
    echo "[basalt] ERROR: basalt_vio not found. Run: curl -LsSf https://gitlab.com/VladyslavUsenko/basalt/-/raw/master/scripts/install.sh | sh" >&2
    exit 1
fi
BASALT_BIN=$(command -v basalt_vio)
BASALT_LIBRARY=$(ldd "$BASALT_BIN" | awk '$1 == "libbasalt.so" && $2 == "=>" { print $3 }')
[[ -f "$BASALT_LIBRARY" ]] || { echo '[basalt] loaded libbasalt.so identity unavailable' >&2; exit 2; }

mkdir -p "$WS/logs"
prepare_fresh_run_dir "$OUT_DIR"
snapshot_rosario_candidate
if [[ -n "${ROSARIO_VIO_PROFILE:-}" ]]; then
    CALIB="$ROSARIO_PROFILE_DIR/calibration.json"
    ESTIMATOR_CFG="$ROSARIO_PROFILE_DIR/vio_config.json"
fi
REQUESTED_ESTIMATOR_CFG="$ESTIMATOR_CFG"
ESTIMATOR_CFG="$OUT_DIR/effective-estimator-settings.json"
python3 "$WS/scripts/run/_basalt_native_profile.py" "$WS" "$REQUESTED_ESTIMATOR_CFG" \
    "$ESTIMATOR_CFG" "$BASALT_BIN" "$BASALT_LIBRARY" > "$OUT_DIR/native-settings-policy.json"
PROFILE_PROV_ARGS+=(--artifact "requested_estimator_config=$REQUESTED_ESTIMATOR_CFG"
    --artifact "native_settings_policy=$OUT_DIR/native-settings-policy.json"
    --artifact "native_settings_review=$WS/docs/campaigns/basalt-native-profile-20261002.json")
NATIVE_SEQ_DIR="$SEQ_DIR"
REQUESTED_CALIB="$CALIB"
if [[ "$USE_IMU" == true ]]; then
    python3 "$WS/scripts/run/_basalt_input_clock.py" "$SEQ_DIR" "$CALIB" "$OUT_DIR/native-inputs" \
        > "$OUT_DIR/input-clock-preparation.json"
    NATIVE_SEQ_DIR="$OUT_DIR/native-inputs/dataset"
    CALIB="$OUT_DIR/native-inputs/effective-calibration.json"
    PROFILE_PROV_ARGS+=(--artifact "requested_camera_calibration=$REQUESTED_CALIB"
        --artifact "input_clock_policy=$OUT_DIR/native-inputs/clock-policy.json"
        --artifact "effective_imu_input=$NATIVE_SEQ_DIR/mav0/imu0/data.csv")
fi
CONTAINER=""
source "$WS/scripts/run/_owned_process.sh"

PROV_ARGS=(
    "${PROFILE_PROV_ARGS[@]}"
    --param "process_isolation=attempt_token"
    --artifact "camera_calibration=$CALIB"
    --artifact "estimator_config=$ESTIMATOR_CFG"
    --binary "estimator=$BASALT_BIN"
    --binary "estimator_shared=$BASALT_LIBRARY"
    --param "use_imu=$USE_IMU"
    --param "num_threads=0"
    --param "playback_rate=offline"
)

echo "[basalt] $DATASET/$SEQ run=${RUN_ID} -> $OUT_DIR" | tee "$LOG_GLOBAL"

# Prepared datasets are immutable during estimation. Missing manifests must be
# repaired in a separate reviewed data-preparation step, never by this runner.
for camera in cam0 cam1; do
    [[ -s "$SEQ_DIR/mav0/$camera/data.csv" ]] || {
        echo "[basalt] missing prepared $camera/data.csv; prepare and audit the dataset first" >&2
        exit 2
    }
done

# ── Resource monitor: CPU + RAM sampled every 1 s ────────────────────────────
prepare_resource_window "$OUT_DIR"
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" --pid "$$" --interval 1 \
    --start-file "$OUT_DIR/.resource_start" --stop-file "$OUT_DIR/.resource_stop" &
MONPID=$!
trap 'owned_stop estimator || true; [[ -n "${MONPID:-}" ]] && kill "$MONPID" 2>/dev/null || true' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# ── Run Basalt VIO (vision-only, no IMU) ─────────────────────────────────────
# basalt_vio saves trajectory.txt in the CWD; cd to $OUT_DIR so it lands there.
cd "$OUT_DIR"

START=$(date +%s.%N)
mark_resource_start "$OUT_DIR"
set +e
owned_run estimator "$BASALT_BIN" \
    --show-gui 0 \
    --dataset-path "$NATIVE_SEQ_DIR" \
    --dataset-type euroc \
    --cam-calib "$CALIB" \
    --config-path "$ESTIMATOR_CFG" \
    --use-imu "$USE_IMU" \
    --save-trajectory tum \
    --num-threads 0 > "$OUT_DIR/run_log.txt" 2>&1
BASALT_RC=$?
set -e
# Mirror run_log.txt to the global log
cat "$OUT_DIR/run_log.txt" >> "$LOG_GLOBAL" || true
END=$(date +%s.%N)
finish_resource_window "$OUT_DIR" "$MONPID"
MONPID=""

if [[ "$BASALT_RC" -ne 0 ]]; then
    record_failed_run_meta "$OUT_DIR/run_meta.json" basalt "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" "$BASALT_RC" "basalt_vio exited nonzero" "${PROV_ARGS[@]}"
    echo "[basalt] ERROR: basalt_vio exited with status $BASALT_RC" | tee -a "$LOG_GLOBAL"
    exit "$BASALT_RC"
fi

# ── Verify output ─────────────────────────────────────────────────────────────
# basalt_vio writes trajectory.txt in TUM format (timestamp in seconds).
# Timestamps are already in seconds - no conversion needed.
if [[ ! -f "$OUT_DIR/trajectory.txt" ]]; then
    record_failed_run_meta "$OUT_DIR/run_meta.json" basalt "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" 1 "trajectory was not produced" "${PROV_ARGS[@]}"
    echo "[basalt] ERROR: trajectory.txt not found - Basalt likely failed" | tee -a "$LOG_GLOBAL"
    exit 1
fi

NFR=$(grep -vc '^#' "$OUT_DIR/trajectory.txt" 2>/dev/null || true)
NFR=${NFR:-0}
DUR=$(python3 -c "print($END-$START)")
python3 -c "
import json
print(json.dumps({
    'algo':     'basalt',
    'dataset':  '$DATASET',
    'seq':      '$SEQ',
    'run_id':   $RUN_ID,
    'run_type': '$RUN_TYPE',
    'use_imu':  $([[ "$USE_IMU" == "true" ]] && echo True || echo False),
    'duration_s': $DUR,
    'frames':   $NFR,
    'fps':      $NFR/$DUR if $DUR > 0 else 0,
}))
" > "$OUT_DIR/run_meta.json"
enrich_run_meta "$OUT_DIR/run_meta.json" --measurement-mode max_throughput "${PROV_ARGS[@]}"

echo "[basalt] run ${RUN_ID} done in ${DUR}s, ${NFR} frames"
