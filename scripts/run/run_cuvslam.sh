#!/usr/bin/env bash
# Run NVIDIA cuVSLAM (PyCuVSLAM 17.0.0) on a sequence.
#
# Usage: scripts/run/run_cuvslam.sh <dataset> <seq> [run_id=1] [run_type=vo]
#
# cuVSLAM is stereo here (cam0 + cam1). run_type:
#   vo      -> stereo odometry                                   -> results/vo/
#   vo-lc   -> stereo odometry + SLAM (loop closure, pose graph)  -> results/vo-lc/
#   vio     -> stereo-inertial odometry                          -> results/vio/
#   vio-lc  -> stereo-inertial odometry + SLAM                   -> results/vio-lc/
#
# Reads:
#   datasets/<dataset>/<seq>/mav0/{cam0,cam1,imu0}   (EuRoC layout)
#   configs/sensors/<dataset>.json                   (shared calibration profile)
#   configs/cuvslam/default.json                     (estimator settings, same for all datasets)
#
# Writes (under $RESULTS_ROOT/<dataset>/<seq>/cuvslam/run<N>/):
#   trajectory.txt   TUM (timestamp_s tx ty tz qx qy qz qw), pose of cam0 (left optical frame)
#   run_log.txt, resources.csv, run_meta.json, cuvslam_effective_config.json,
#   cuvslam_summary.json, native/{odometry_tum.txt,tracking_times.csv[,slam_live_tum.txt]}
#
# Frames are pushed as fast as the estimator accepts them (max throughput); bundle
# adjustment and loop closure run synchronously, so the result does not depend on feed rate.
set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"

case "$RUN_TYPE" in
    vo|vo-lc|vio|vio-lc) ;;
    *) echo "[cuvslam] ERROR: run_type must be vo, vo-lc, vio or vio-lc" >&2; exit 2 ;;
esac

REPO="$WS/src/cuvslam"
SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/cuvslam/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_cuvslam_${RUN_TYPE}_run${RUN_ID}.log"
SENSOR="$WS/configs/sensors/${DATASET}.json"
ALGO_CFG="${CUVSLAM_CONFIG:-$WS/configs/cuvslam/default.json}"
CONDA_ENV="${CUVSLAM_CONDA_ENV:-cuvslam}"
CUDA_LIB="${CUVSLAM_CUDA_LIB:-/usr/local/cuda-12.4/lib64}"

[[ -d "$REPO/.git" ]] || { echo "[cuvslam] ERROR: source checkout missing at $REPO (run scripts/build/setup_cuvslam_env.sh)" >&2; exit 2; }
[[ -f "$SENSOR" ]] || { echo "[cuvslam] ERROR: no sensor profile at $SENSOR (run scripts/setup/build_sensor_profiles.py)" >&2; exit 2; }
[[ -f "$ALGO_CFG" ]] || { echo "[cuvslam] ERROR: no config at $ALGO_CFG" >&2; exit 2; }
[[ -d "$CUDA_LIB" ]] || { echo "[cuvslam] ERROR: CUDA 12 runtime not found at $CUDA_LIB" >&2; exit 2; }
for f in mav0/cam0/data.csv mav0/cam1/data.csv mav0/imu0/data.csv; do
    [[ -f "$SEQ_DIR/$f" ]] || { echo "[cuvslam] ERROR: missing $SEQ_DIR/$f" >&2; exit 2; }
done

set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV"
set -u
export LD_LIBRARY_PATH="$CUDA_LIB${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

# The profile must still equal what the reference configs declare, and agree with the
# OKVIS2/Basalt configs of the same dataset, before an attempt ID is consumed.
python3 "$WS/scripts/setup/build_sensor_profiles.py" --repo "$WS" --check > /dev/null \
    || { echo "[cuvslam] ERROR: sensor profiles are stale or inconsistent" >&2; exit 2; }

mkdir -p "$WS/logs"
prepare_fresh_run_dir "$OUT_DIR"
CONTAINER=""
source "$WS/scripts/run/_owned_process.sh"
: > "$OUT_DIR/run_log.txt"

echo "[cuvslam] $DATASET/$SEQ type=${RUN_TYPE} run=${RUN_ID} -> $OUT_DIR" | tee "$LOG"

prepare_resource_window "$OUT_DIR"
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" --pid "$$" --interval 1 \
    --start-file "$OUT_DIR/.resource_start" --stop-file "$OUT_DIR/.resource_stop" &
MONPID=$!
trap 'owned_stop estimator || true; [[ -n "${MONPID:-}" ]] && kill "$MONPID" 2>/dev/null || true' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

PROV_ARGS=(
    --param "process_isolation=attempt_token"
    --artifact "camera_calibration=$SENSOR"
    --artifact "algorithm_config=$ALGO_CFG"
    --source "algorithm=$REPO"
    --param "loop_closure=$USE_LC" --param "use_imu=$USE_IMU"
    --param "output_frame=cam0_left_optical"
    --param "feed=max_throughput_synchronous_sba_and_slam"
    --conda-env "$CONDA_ENV"
)

START=$(date +%s.%N)
mark_resource_start "$OUT_DIR"
set +e
owned_run estimator python3 "$WS/scripts/run/_cuvslam_track.py" \
    --sequence "$SEQ_DIR" --sensor "$SENSOR" --config "$ALGO_CFG" \
    --mode "$RUN_TYPE" --out "$OUT_DIR" 2>&1 | python3 -u -c "
import sys, time
t0 = time.time()
for line in sys.stdin:
    sys.stdout.write(f'{time.time()-t0:.3f} {line}'); sys.stdout.flush()
" | tee -a "$OUT_DIR/run_log.txt" "$LOG" | grep --line-buffered -v -e 'loop closure at' -e 'no pose at frame' -e '^[0-9.]* \[cuvslam\] {'
CUV_RC=${PIPESTATUS[0]}
set -e
END=$(date +%s.%N)
finish_resource_window "$OUT_DIR" "$MONPID"
MONPID=""
if (( CUV_RC != 0 )); then
    record_failed_run_meta "$OUT_DIR/run_meta.json" cuvslam "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" "$CUV_RC" "estimator exited nonzero" "${PROV_ARGS[@]}"
    exit "$CUV_RC"
fi
if [[ ! -s "$OUT_DIR/trajectory.txt" ]]; then
    record_failed_run_meta "$OUT_DIR/run_meta.json" cuvslam "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" 1 "trajectory was not produced" "${PROV_ARGS[@]}"
    echo "[cuvslam] ERROR: no trajectory — run failed" | tee -a "$LOG"; exit 1
fi
PROV_ARGS+=(--artifact "effective_config=$OUT_DIR/cuvslam_effective_config.json")

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt")
python3 - "$OUT_DIR" "$DATASET" "$SEQ" "$RUN_ID" "$RUN_TYPE" "$USE_IMU" "$USE_LC" "$DUR" "$NFR" <<'PY' > "$OUT_DIR/run_meta.json"
import json, sys
out, dataset, seq, run_id, run_type, use_imu, use_lc, dur, frames = sys.argv[1:]
summary = json.load(open(out + '/cuvslam_summary.json'))
dur, frames = float(dur), int(frames)
print(json.dumps({'algo': 'cuvslam', 'dataset': dataset, 'seq': seq, 'run_id': int(run_id),
                  'run_type': run_type, 'use_imu': use_imu == 'true', 'use_lc': use_lc == 'true',
                  'duration_s': dur, 'frames': frames, 'fps': frames / dur if dur > 0 else 0,
                  'frames_offered': summary['frames_offered'],
                  'frames_without_pose': summary['frames_without_pose'],
                  'loop_closure_events': summary['loop_closure_events'],
                  'track_call_mean_ms': summary['track_call_mean_ms']}))
PY
enrich_run_meta "$OUT_DIR/run_meta.json" --measurement-mode max_throughput "${PROV_ARGS[@]}"
echo "[cuvslam] run ${RUN_ID} done in ${DUR}s, ${NFR} poses" | tee -a "$LOG"
