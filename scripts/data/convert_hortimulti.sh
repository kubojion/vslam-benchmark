#!/usr/bin/env bash
# Convert a HortiMulti ROS1 bag into rectified stereo images + gt_tum.txt.
#
# Usage:
#   bash scripts/data/convert_hortimulti.sh <sequence_dir> [extra python args]
#
# Example:
#   bash scripts/data/convert_hortimulti.sh datasets/hortimulti/strawberry02
#
# Expected input layout:
#   <seq_dir>/
#   ├── *.bag              ← one bag file (Strawberry-02-001.bag, etc.)
#   └── GT_trajectory.csv  ← ground truth from PolyTagSLAM
#
# Output layout (in same <seq_dir>):
#   mav0/cam0/data/*.png   ← forwardLeft (fisheye-rectified, 640×480, grayscale)
#   mav0/cam1/data/*.png   ← forwardRight
#   cam0  → mav0/cam0/data   (symlink)
#   cam1  → mav0/cam1/data   (symlink)
#   left  → mav0/cam0/data   (symlink for MAC-VO)
#   right → mav0/cam1/data   (symlink for MAC-VO)
#   times.txt              ← nanosecond timestamps (one per line)
#   gt_tum.txt             ← TUM-format ground truth
#
# For a quick smoke-test (first 500 frames only) add: --max_frames 500
#
# Requires: pip install rosbags numpy opencv-python
set -euo pipefail

SEQ_DIR=${1:?"Usage: $0 <sequence_directory> [extra args]"}
[[ -d "$SEQ_DIR" ]] || { echo "ERROR: directory not found: $SEQ_DIR"; exit 1; }

BAG=$(ls "$SEQ_DIR"/*.bag 2>/dev/null | head -n1)
[[ -n "$BAG" ]] || { echo "ERROR: no .bag file found in $SEQ_DIR"; exit 1; }

GT_CSV="$SEQ_DIR/GT_trajectory.csv"
[[ -f "$GT_CSV" ]] || { echo "WARNING: GT_trajectory.csv not found — skipping GT"; GT_CSV=""; }

echo "[hortimulti] bag     : $BAG"
echo "[hortimulti] GT csv  : ${GT_CSV:-<none>}"
echo "[hortimulti] output  : $SEQ_DIR"

python3 "$(dirname "$0")/_hortimulti_extract.py" \
    --bag  "$BAG" \
    --gt_csv "${GT_CSV:-$SEQ_DIR/GT_trajectory.csv}" \
    --out  "$SEQ_DIR" \
    "${@:2}"

echo "[hortimulti] done → $SEQ_DIR"
