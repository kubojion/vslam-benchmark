#!/usr/bin/env bash
# Run an algorithm N times on a sequence, then run the full evaluation pipeline.
#
# Usage:
#   bash scripts/run/run_benchmark.sh <dataset> <seq> <algo> [N=3]
#
# Currently supports: orbslam3
# For other algos: run_<algo>.sh must accept a third argument <run_id>.
#
# Pipeline:
#   1. Run algorithm N times  →  results/<dataset>/<seq>/<algo>/run{1..N}/
#   2. Build interpolated GT  →  datasets/<dataset>/<seq>/gt_interp_tum.txt
#   3. Auto-segment GT        →  datasets/<dataset>/<seq>/segments_auto.csv
#   4. Evaluate each run      →  run*/run_eval.json
#   5. Aggregate              →  metrics.csv + report.md
set -euo pipefail

DATASET=$1; SEQ=$2; ALGO=$3; N=${4:-3}
WS=$(cd "$(dirname "$0")/../.." && pwd)
EVAL="$WS/scripts/eval"
DS_DIR="$WS/datasets/$DATASET/$SEQ"

echo "================================================================"
echo " BENCHMARK: $ALGO on $DATASET/$SEQ  ($N runs)"
echo "================================================================"

# ── Step 1: Run algorithm N times ────────────────────────────────────────────
for i in $(seq 1 "$N"); do
    echo ""
    echo "[benchmark] ─── Run $i / $N ───────────────────────────────────────"
    bash "$WS/scripts/run/run_${ALGO}.sh" "$DATASET" "$SEQ" "$i"
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
        "$EVAL/_evaluate_run.py" "$DATASET" "$SEQ" "$ALGO" "$i"
done

# ── Step 5: Aggregate ─────────────────────────────────────────────────────────
echo ""
echo "[benchmark] ─── Aggregating $N runs ──────────────────────────────────"
conda run -n macvo python3 \
    "$EVAL/_aggregate_runs.py" "$DATASET" "$SEQ" "$ALGO"

echo ""
echo "================================================================"
echo " DONE — results/$DATASET/$SEQ/$ALGO/"
echo "================================================================"
