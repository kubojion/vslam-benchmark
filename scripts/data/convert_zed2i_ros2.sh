#!/usr/bin/env bash
# Convert a ZED 2i ROS 2 bag plus matching RTK ROS 2 bag into the benchmark layout.
#
# Usage:
#   scripts/data/convert_zed2i_ros2.sh <out_seq_dir> <zed_bag_dir> <rtk_bag_dir> [extra args]
#
# Example:
#   scripts/data/convert_zed2i_ros2.sh \
#     datasets/zed2i/field1_110426_5k \
#     /home/iman/datasets/zed2i_bags/zed2i_vislam_rtk_hd1080_compressed_20260703_110426 \
#     /home/iman/Downloads/field-test-0703/field1/field1-all-rows-follow-0703-nav2-3 \
#     --max_frames 5000 --image_format jpg
set -euo pipefail

OUT=${1:?"Usage: $0 <out_seq_dir> <zed_bag_dir> <rtk_bag_dir> [extra args]"}
ZED_BAG=${2:?"Usage: $0 <out_seq_dir> <zed_bag_dir> <rtk_bag_dir> [extra args]"}
RTK_BAG=${3:?"Usage: $0 <out_seq_dir> <zed_bag_dir> <rtk_bag_dir> [extra args]"}
shift 3

python3 "$(dirname "$0")/_zed2i_ros2_extract.py" \
  --out "$OUT" \
  --zed_bag "$ZED_BAG" \
  --rtk_bag "$RTK_BAG" \
  "$@"
