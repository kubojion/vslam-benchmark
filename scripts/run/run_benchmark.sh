#!/usr/bin/env bash
# Run an algorithm N times on a sequence, then run the full evaluation pipeline.
#
# Usage:
#   bash scripts/run/run_benchmark.sh <dataset> <seq> <algo> [N=3] [run_type=vo]
#
# run_type ∈ {vo, vo-lc, vio, vio-lc, gnss-vio} selects the results tree:
#   vo       -> results/vo/
#   vo-lc    -> results/vo-lc/
#   vio      -> results/vio/
#   vio-lc   -> results/vio-lc/
#   gnss-vio -> results/gnss-vio/
#
# Currently supports: orbslam3, droidslam, macvo, basalt, airslam, ov2slam,
#                     okvis2, okvis2x, openvins, mast3r_slam, megasam, voxel_svio,
#                     cifasis_gnss_si, rtabmap_gps, vins_fusion_gps,
#                     openvins_gps
# For other algos: run_<algo>.sh must accept arguments <dataset> <seq> <run_id> <run_type>.
#
# Pipeline:
#   1. Run algorithm N times  ->  <RESULTS_ROOT>/<dataset>/<seq>/<algo>/run{1..N}/
#   2. Build interpolated GT  ->  datasets/<dataset>/<seq>/gt_interp_tum.txt
#   3. Auto-segment GT        ->  datasets/<dataset>/<seq>/segments_auto.csv
#   4. Evaluate each run      ->  run*/run_eval.json
#   5. Aggregate              ->  metrics.csv + report.md
set -euo pipefail

DATASET=$1; SEQ=$2; ALGO=$3; N=${4:-3}; RUN_TYPE=${5:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"
EVAL="$WS/scripts/eval"
DS_DIR="$WS/datasets/$DATASET/$SEQ"

[[ "$N" =~ ^[1-9][0-9]*$ ]] || { echo "ERROR: N must be a positive integer" >&2; exit 2; }
RUNNER="$WS/scripts/run/run_${ALGO}.sh"
[[ -f "$RUNNER" ]] || { echo "ERROR: runner not found: $RUNNER" >&2; exit 2; }
[[ -d "$DS_DIR" ]] || { echo "ERROR: dataset sequence not found: $DS_DIR" >&2; exit 2; }
command -v flock >/dev/null || { echo "ERROR: flock is required for result-cell locking" >&2; exit 2; }

# Validate every path component before creating a lock or replacing anything.
python3 "$WS/scripts/results/prepare_cell.py" \
    "$WS" "$RUN_TYPE" "$DATASET" "$SEQ" "$ALGO" --dry-run
mkdir -p "$WS/results/.locks"
LOCK_PATH="$WS/results/.locks/${RUN_TYPE}__${DATASET}__${SEQ}__${ALGO}.lock"
exec {RESULT_LOCK_FD}>"$LOCK_PATH"
flock -n "$RESULT_LOCK_FD" || {
    echo "ERROR: another benchmark is writing this result cell: $RUN_TYPE/$DATASET/$SEQ/$ALGO" >&2
    exit 2
}

# Old results for this exact comparison cell are intentionally replaced as one
# unit, including run directories, aggregate reports, and generated plots.
python3 "$WS/scripts/results/prepare_cell.py" \
    "$WS" "$RUN_TYPE" "$DATASET" "$SEQ" "$ALGO"

echo "================================================================"
echo " BENCHMARK: $ALGO on $DATASET/$SEQ  ($N runs, type=$RUN_TYPE)"
echo "================================================================"

# ── Step 1: Run algorithm N times ────────────────────────────────────────────
for i in $(seq 1 "$N"); do
    echo ""
    echo "[benchmark] ─── Run $i / $N ───────────────────────────────────────"
    bash "$RUNNER" "$DATASET" "$SEQ" "$i" "$RUN_TYPE"
done

# ── Step 2: Interpolate GT to camera timestamps ───────────────────────────────
GT_INTERP="$DS_DIR/gt_interp_tum.txt"
TIMES="$DS_DIR/times.txt"
GT_RAW="$DS_DIR/gt_tum.txt"

if [[ -f "$GT_INTERP" ]]; then
    echo "[benchmark] gt_interp_tum.txt already exists — skipping interpolation"
elif [[ -f "$TIMES" && -f "$GT_RAW" ]]; then
    echo "[benchmark] interpolating GT to camera timestamps ..."
    conda run -n macvo python3 \
        "$EVAL/_interpolate_gt.py" "$GT_RAW" "$TIMES" "$GT_INTERP"
else
    echo "[benchmark] WARNING: no times.txt or gt_tum.txt found — " \
         "evaluation will use raw GT with t_max_diff=0.1"
fi

# ── Step 3: Auto-segment GT ───────────────────────────────────────────────────
SEG_AUTO="$DS_DIR/segments_auto.csv"
if [[ -f "$SEG_AUTO" ]]; then
    echo "[benchmark] segments_auto.csv already exists — skipping segmentation"
elif [[ -f "$GT_INTERP" ]]; then
    echo "[benchmark] auto-segmenting GT trajectory ..."
    conda run -n macvo python3 \
        "$EVAL/_segment_trajectory.py" "$GT_INTERP" "$SEG_AUTO"
elif [[ -f "$GT_RAW" ]]; then
    echo "[benchmark] auto-segmenting GT trajectory (from raw GT) ..."
    conda run -n macvo python3 \
        "$EVAL/_segment_trajectory.py" "$GT_RAW" "$SEG_AUTO"
fi

# ── Step 4: Evaluate each run ─────────────────────────────────────────────────
for i in $(seq 1 "$N"); do
    echo ""
    echo "[benchmark] ─── Evaluating run $i ────────────────────────────────"
    conda run -n macvo python3 \
        "$EVAL/_evaluate_run.py" "$DATASET" "$SEQ" "$ALGO" "$i" "$RUN_TYPE"
    python3 "$WS/scripts/results/validate_run.py" \
        "$RESULTS_ROOT/$DATASET/$SEQ/$ALGO/run${i}" --require-provenance 2
done

# ── Step 5: Aggregate ─────────────────────────────────────────────────────────
echo ""
echo "[benchmark] ─── Aggregating $N runs ──────────────────────────────────"
conda run -n macvo python3 \
    "$EVAL/_aggregate_runs.py" "$DATASET" "$SEQ" "$ALGO" auto "$RUN_TYPE"

python3 "$WS/scripts/results/build_manifest.py"
python3 "$WS/scripts/results/build_site.py"

echo ""
echo "================================================================"
echo " DONE -> $RESULTS_ROOT/$DATASET/$SEQ/$ALGO/"
echo "================================================================"
