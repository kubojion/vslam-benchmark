#!/usr/bin/env bash
# Run DROID-SLAM (stereo) on a converted sequence.
# Usage: scripts/run/run_droidslam.sh <dataset> <seq> [run_id=1] [run_type=vo] [extra demo.py args]
#
# DROID-SLAM has no IMU or LC support. Only run_type=vo is meaningful.
set -eo pipefail
DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}; shift 4 2>/dev/null || true
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
resolve_run_type "$RUN_TYPE"
if [[ "$RUN_TYPE" != "vo" ]]; then
    echo "[droidslam] WARNING: DROID-SLAM has no IMU / LC; routing output anyway" >&2
fi
SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/droidslam/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_droidslam_${RUN_TYPE}_run${RUN_ID}.log"
CALIB="$WS/configs/droidslam/${DATASET}.txt"
mkdir -p "$OUT_DIR" "$WS/logs"
# Conda's activate/deactivate scripts reference variables (SYS_SYSROOT,
# _CONDA_PYTHON_SYSCONFIGDATA_NAME_USED, …) that may be unset; -u makes bash
# treat that as a fatal error.  Disable it only around conda operations.
set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate droidenv
set -u
# conda activate sets NVCC_PREPEND_FLAGS="UNSET -ccbin=..." which passes the
# literal string "UNSET" as a filename to nvcc → always fatal.
unset NVCC_PREPEND_FLAGS
# Reduce CUDA allocator fragmentation: lets PyTorch reuse reserved-but-unallocated
# blocks instead of requesting new ones (fixes OOM when 1.7 GiB is reserved-idle).
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
# Key VRAM tuning parameter: --filter_thresh controls the minimum optical-flow
# confidence to keep a frame in the bundle adjustment window. Lower = more frames
# retained = higher VRAM. 6.0 is empirically the lowest value that fits without
# OOM on long sequences (Rosario ~940 m / HortiMulti ~950 m). Reduce if OOM.

cd "$WS/src/DROID-SLAM"
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap "kill $MONPID 2>/dev/null || true" EXIT

START=$(date +%s.%N)
python3 "$WS/scripts/run/_droid_demo_wrapper.py" \
    --imagedir "$SEQ_DIR/cam0" \
    --rightimagedir "$SEQ_DIR/cam1" \
    --calib "$CALIB" \
    --stereo \
    --reconstruction_path "$OUT_DIR/recon.pth" \
    --trajectory_out "$OUT_DIR/trajectory.txt" \
    --timestamps "$SEQ_DIR/times.txt" \
    --disable_vis \
    --stride 1 \
    --buffer 1024 \
    --filter_thresh 6.0 \
    --frontend_window 16 \
    --skip_backend \
    "$@" 2>&1 | tee "$LOG"
END=$(date +%s.%N)

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt" 2>/dev/null || echo 0)
python3 -c "
import json
print(json.dumps({'algo':'droidslam','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
                  'duration_s':$DUR,'frames':$NFR,'fps':$NFR/$DUR if $DUR>0 else 0}))
" > "$OUT_DIR/run_meta.json"
echo "[droidslam] done (run ${RUN_ID})"
