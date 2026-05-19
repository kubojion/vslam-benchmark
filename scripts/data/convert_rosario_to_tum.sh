#!/usr/bin/env bash
# Convert a Rosario v2 rosbag sequence into EuRoC-compatible image folders
# + times.txt, imu.csv, gt_tum.txt.
#
# Usage:
#   bash scripts/convert_rosario_to_tum.sh datasets/rosariov2/sequence1
#
# The script auto-detects the main bag (any *.bag not ending in _pgt.bag)
# and the PGT bag (*_pgt.bag) inside the sequence directory.
#
# Output layout (EuRoC-compatible, required by ORB-SLAM3 stereo_euroc):
#   <seq>/mav0/cam0/data/<ns_stamp>.png   left IR (infra1)
#   <seq>/mav0/cam1/data/<ns_stamp>.png   right IR (infra2)
#   <seq>/times.txt                       nanosecond stamps, one per line
#   <seq>/cam0  ->  mav0/cam0/data        convenience symlink
#   <seq>/cam1  ->  mav0/cam1/data        convenience symlink
#   <seq>/gt_tum.txt                      TUM format from MINS PGT
#   <seq>/imu.csv                         realsense IMU
#   <seq>/gps.csv                         reach_1 GNSS (raw lat/lon/alt)
#
# To do a quick smoke-test with only the first 400 frames add --max_frames 400.
#
# Requires: pip install rosbags pyproj numpy opencv-python
set -euo pipefail

SEQ_DIR=${1:?"Usage: $0 <sequence_directory>"}
[[ -d "$SEQ_DIR" ]] || { echo "ERROR: no such dir: $SEQ_DIR"; exit 1; }

# Auto-detect bags
BAG=$(ls "$SEQ_DIR"/*.bag 2>/dev/null | grep -v '_pgt' | head -n1)
PGT_BAG=$(ls "$SEQ_DIR"/*_pgt*.bag 2>/dev/null | head -n1 || true)

[[ -n "$BAG" ]] || { echo "ERROR: no main .bag found in $SEQ_DIR"; exit 1; }
echo "[convert] main bag : $BAG"
[[ -n "$PGT_BAG" ]] && echo "[convert] PGT bag  : $PGT_BAG" || echo "[convert] no PGT bag found; will derive GT from GPS"

EXTRA_ARGS=""
[[ -n "$PGT_BAG" ]] && EXTRA_ARGS="--gt_bag $PGT_BAG --gt /mins/imu/pose"

# Pass any additional CLI args (e.g. --max_frames 400) straight through
python3 "$(dirname "$0")/_rosario_extract.py" \
    --bag   "$BAG" \
    --out   "$SEQ_DIR" \
    --left  /realsense/infra1/image_rect_raw \
    --right /realsense/infra2/image_rect_raw \
    --imu   /realsense/imu \
    --gps   /reach_1/fix \
    $EXTRA_ARGS \
    "${@:2}"

echo "[convert] done -> $SEQ_DIR"
