#!/usr/bin/env bash
# Run MASt3R-Fusion (monocular feed-forward pointmaps + IMU factor graph) on a sequence.
#
# Usage: scripts/run/run_mast3r_fusion.sh <dataset> <seq> [run_id=1] [run_type=vio]
#
# MASt3R-Fusion always uses the IMU (there is no IMU-free mode) and cam0 only. run_type:
#   vio     -> real-time sliding-window estimate (main.py)                 -> results/vio/
#   vio-lc  -> the same, then loop detection (main_loop.py) and global
#              optimisation with the loop factors (main_global_optimization.py);
#              the trajectory is the globally optimised one                -> results/vio-lc/
# GNSS fusion (main_global_optimization.py --enable_gnss) is not wired up here yet.
#
# Reads:
#   datasets/<dataset>/<seq>/mav0/{cam0,imu0}        (EuRoC layout)
#   configs/sensors/<dataset>.json                   (shared calibration profile)
#   configs/mast3r_fusion/benchmark.yaml             (settings, same for all datasets)
#   src/mast3r_fusion/config/base_euroc.yaml         (upstream parameters)
#   third_party/mast3r-fusion-checkpoints/           (MASt3R weights)
#
# Writes (under $RESULTS_ROOT/<dataset>/<seq>/mast3r_fusion/run<N>/):
#   trajectory.txt   TUM (timestamp_s tx ty tz qx qy qz qw), pose of cam0 (left optical frame)
#   run_log.txt, resources.csv, run_meta.json, mast3r_fusion_config.yaml, intrinsics.yaml,
#   native/{result.txt, graph.pkl[, loop.pkl, result_global.txt]}
#   (the keyframe file data.h5 is large and removed after loop detection unless
#    MAST3R_FUSION_KEEP_H5=1)
set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vio}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"

case "$RUN_TYPE" in
    vio|vio-lc) ;;
    vo|vo-lc) echo "[mast3r_fusion] ERROR: MASt3R-Fusion has no IMU-free mode; use vio or vio-lc" >&2; exit 2 ;;
    *) echo "[mast3r_fusion] ERROR: run_type must be vio or vio-lc" >&2; exit 2 ;;
esac

REPO="$WS/src/mast3r_fusion"
SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/mast3r_fusion/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_mast3r_fusion_${RUN_TYPE}_run${RUN_ID}.log"
SENSOR="$WS/configs/sensors/${DATASET}.json"
ALGO_CFG="${MAST3R_FUSION_CONFIG:-$WS/configs/mast3r_fusion/benchmark.yaml}"
BASE_CFG="$REPO/config/base_euroc.yaml"
CKPT="$WS/third_party/mast3r-fusion-checkpoints"
CONDA_ENV="${MAST3R_FUSION_CONDA_ENV:-mast3r_fusion}"
SEED="${MAST3R_FUSION_SEED:-$((1000 + RUN_ID))}"
GPU_ID="${MAST3R_FUSION_GPU:-0}"

[[ -d "$REPO/.git" ]] || { echo "[mast3r_fusion] ERROR: source checkout missing at $REPO (run scripts/build/setup_mast3r_fusion_env.sh)" >&2; exit 2; }
for f in "$SENSOR" "$ALGO_CFG" "$BASE_CFG" "$CKPT/MASt3R_ViTLarge_BaseDecoder_512_catmlpdpt_metric.pth"; do
    [[ -f "$f" ]] || { echo "[mast3r_fusion] ERROR: missing $f" >&2; exit 2; }
done
for f in mav0/cam0/data.csv mav0/imu0/data.csv; do
    [[ -f "$SEQ_DIR/$f" ]] || { echo "[mast3r_fusion] ERROR: missing $SEQ_DIR/$f" >&2; exit 2; }
done

set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV"
set -u
# The profile check needs OpenCV's YAML reader, which this environment also has.
python3 "$WS/scripts/setup/build_sensor_profiles.py" --repo "$WS" --check > /dev/null \
    || { echo "[mast3r_fusion] ERROR: sensor profiles are stale or inconsistent" >&2; exit 2; }

# One prepared input folder per (sequence, sensor profile); reused by every repetition.
STAGE="$WS/results/.cache/mast3r-fusion-stage/$DATASET/$SEQ/$(sha256sum "$SENSOR" | cut -c1-16)"
mkdir -p "$(dirname "$STAGE")"
python3 "$WS/scripts/run/_mast3r_fusion_stage.py" stage --sequence "$SEQ_DIR" --sensor "$SENSOR" --out "$STAGE"

mkdir -p "$WS/logs"
prepare_fresh_run_dir "$OUT_DIR"
CONTAINER=""
source "$WS/scripts/run/_owned_process.sh"
: > "$OUT_DIR/run_log.txt"
NATIVE="$OUT_DIR/native"
mkdir "$NATIVE"
# main.py resolves "checkpoints/" and writes graph.pkl / data.h5 relative to the
# working directory, so each attempt gets its own.
ln -s "$CKPT" "$NATIVE/checkpoints"
python3 "$WS/scripts/run/_mast3r_fusion_stage.py" config --stage "$STAGE" --base "$BASE_CFG" \
    --override "$ALGO_CFG" --out "$OUT_DIR/mast3r_fusion_config.yaml" > "$NATIVE/config_summary.json"
cp "$STAGE/intrinsics.yaml" "$OUT_DIR/intrinsics.yaml"

echo "[mast3r_fusion] $DATASET/$SEQ type=${RUN_TYPE} run=${RUN_ID} -> $OUT_DIR" | tee "$LOG"

prepare_resource_window "$OUT_DIR"
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" --pid "$$" --interval 1 \
    --start-file "$OUT_DIR/.resource_start" --stop-file "$OUT_DIR/.resource_stop" &
MONPID=$!
trap 'owned_stop estimator || true; owned_stop loop || true; owned_stop global || true; [[ -n "${MONPID:-}" ]] && kill "$MONPID" 2>/dev/null || true' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

PROV_ARGS=(
    --param "process_isolation=attempt_token"
    --artifact "camera_calibration=$SENSOR"
    --artifact "algorithm_config=$ALGO_CFG"
    --artifact "algorithm_defaults=$BASE_CFG"
    --artifact "effective_config=$OUT_DIR/mast3r_fusion_config.yaml"
    --artifact "camera_imu_calibration=$OUT_DIR/intrinsics.yaml"
    --source "algorithm=$REPO"
    --param "loop_closure=$USE_LC" --param "use_imu=true"
    --param "output_frame=cam0_left_optical"
    --param "trajectory_source=$([[ "$RUN_TYPE" == vio-lc ]] && echo global_optimisation || echo real_time)"
    --seed "$SEED"
    --conda-env "$CONDA_ENV"
)

stamp() { python3 -u -c "
import sys, time
t0 = time.time()
for line in sys.stdin:
    sys.stdout.write(f'{time.time()-t0:.3f} {line}'); sys.stdout.flush()
"; }

# Thread counts as in the authors' batch scripts. No bytecode files: they would appear
# inside the source checkout during the run and change the captured implementation.
# The loop and global stages draw figures; Agg keeps them off any display.
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 CUDA_VISIBLE_DEVICES="$GPU_ID" PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg
SAVE_H5=(); [[ "$RUN_TYPE" == "vio-lc" ]] && SAVE_H5=(--save_h5)
cd "$NATIVE"
START=$(date +%s.%N)
mark_resource_start "$OUT_DIR"
# Stop sampling, record the failed attempt and exit (defined after the window opens).
fail() {
    finish_resource_window "$OUT_DIR" "$MONPID"; MONPID=""
    record_failed_run_meta "$OUT_DIR/run_meta.json" mast3r_fusion "$DATASET" "$SEQ" \
        "$RUN_ID" "$RUN_TYPE" "$1" "$2" "${PROV_ARGS[@]}"
    echo "[mast3r_fusion] ERROR: $2" | tee -a "$LOG"; exit "$1"
}
set +e
owned_run estimator python3 "$WS/scripts/run/_seeded_python.py" "$SEED" "$REPO/main.py" \
    --dataset "$STAGE" --config "$OUT_DIR/mast3r_fusion_config.yaml" --calib "$STAGE/intrinsics.yaml" \
    --imu_path "$STAGE/mav0/imu0/data.csv" --imu_dt 0.0 \
    --result_path "$NATIVE/result.txt" "${SAVE_H5[@]}" --no-viz 2>&1 | stamp | tee -a "$OUT_DIR/run_log.txt" "$LOG" > /dev/null
RC=${PIPESTATUS[0]}
set -e
(( RC == 0 )) || fail "$RC" "real-time stage exited nonzero"
[[ -s "$NATIVE/result.txt" && -s "$NATIVE/graph.pkl" ]] || fail 1 "real-time stage produced no result"
VIO_END=$(date +%s.%N)

RAW="$NATIVE/result.txt"
if [[ "$RUN_TYPE" == "vio-lc" ]]; then
    set +e
    owned_run loop python3 "$WS/scripts/run/_seeded_python.py" "$SEED" "$REPO/main_loop.py" \
        --config "$OUT_DIR/mast3r_fusion_config.yaml" --h5_file "$NATIVE/data.h5" \
        --loop_output "$NATIVE/loop.pkl" 2>&1 | stamp | tee -a "$OUT_DIR/run_log.txt" "$LOG" > /dev/null
    RC=${PIPESTATUS[0]}
    set -e
    (( RC == 0 )) && [[ -s "$NATIVE/loop.pkl" ]] || fail "$(( RC ? RC : 1 ))" "loop detection failed"
    set +e
    owned_run global python3 "$WS/scripts/run/_seeded_python.py" "$SEED" "$REPO/main_global_optimization.py" \
        --config "$OUT_DIR/mast3r_fusion_config.yaml" --graph_path "$NATIVE/graph.pkl" \
        --loop_path "$NATIVE/loop.pkl" --calib_path "$STAGE/intrinsics.yaml" \
        --imu_path "$STAGE/mav0/imu0/data.csv" --imu_dt 0.0 \
        --result_path "$NATIVE/result_global.txt" 2>&1 | stamp | tee -a "$OUT_DIR/run_log.txt" "$LOG" > /dev/null
    RC=${PIPESTATUS[0]}
    set -e
    (( RC == 0 )) && [[ -s "$NATIVE/result_global.txt" ]] || fail "$(( RC ? RC : 1 ))" "global optimisation failed"
    RAW="$NATIVE/result_global.txt"
fi
END=$(date +%s.%N)
finish_resource_window "$OUT_DIR" "$MONPID"
MONPID=""
cd "$WS"

H5_BYTES=0
if [[ -f "$NATIVE/data.h5" ]]; then
    H5_BYTES=$(stat -c %s "$NATIVE/data.h5")
    [[ "${MAST3R_FUSION_KEEP_H5:-0}" == "1" ]] || rm -f "$NATIVE/data.h5"
fi
python3 "$WS/scripts/run/_mast3r_fusion_stage.py" export --raw "$RAW" --trajectory "$OUT_DIR/trajectory.txt" | tee -a "$LOG"
[[ -s "$OUT_DIR/trajectory.txt" ]] || { MONPID=""; record_failed_run_meta "$OUT_DIR/run_meta.json" mast3r_fusion \
    "$DATASET" "$SEQ" "$RUN_ID" "$RUN_TYPE" 1 "trajectory was not produced" "${PROV_ARGS[@]}"; exit 1; }

python3 - "$OUT_DIR" "$DATASET" "$SEQ" "$RUN_ID" "$RUN_TYPE" "$USE_LC" "$START" "$VIO_END" "$END" "$STAGE" "$H5_BYTES" <<'PY' > "$OUT_DIR/run_meta.json"
import json, sys
out, dataset, seq, run_id, run_type, use_lc, start, vio_end, end, stage, h5 = sys.argv[1:]
start, vio_end, end = float(start), float(vio_end), float(end)
frames = sum(1 for _ in open(out + '/trajectory.txt'))
summary = json.load(open(out + '/native/config_summary.json'))
offered = json.load(open(stage + '/stage.json'))['frames']
processed = -(-offered // summary['subsample'])
print(json.dumps({'algo': 'mast3r_fusion', 'dataset': dataset, 'seq': seq, 'run_id': int(run_id),
                  'run_type': run_type, 'use_imu': True, 'use_lc': use_lc == 'true',
                  'duration_s': end - start, 'frames': frames,
                  'fps': processed / (vio_end - start) if vio_end > start else 0,
                  'frames_offered': offered, 'frames_processed': processed,
                  'subsample': summary['subsample'], 'realtime_stage_s': vio_end - start,
                  'global_stage_s': end - vio_end, 'keyframe_file_bytes': int(h5)}))
PY
enrich_run_meta "$OUT_DIR/run_meta.json" --measurement-mode max_throughput "${PROV_ARGS[@]}"
echo "[mast3r_fusion] run ${RUN_ID} done in $(python3 -c "print($END-$START)")s" | tee -a "$LOG"
