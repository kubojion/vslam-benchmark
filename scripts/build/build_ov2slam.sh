#!/usr/bin/env bash
# Build the OV2SLAM ROS Noetic image from the pinned submodule.
set -euo pipefail

WS=$(cd "$(dirname "$0")/../.." && pwd)
IMAGE="vslam_ov2slam:noetic"
DOCKERFILE="$WS/scripts/setup/ov2slam.Dockerfile"
SOURCE="$WS/src/ov2slam"

if [[ ! -f "$SOURCE/CMakeLists.txt" ]]; then
    echo "ERROR: OV2SLAM submodule is not initialized at $SOURCE" >&2
    echo "Run: git submodule update --init src/ov2slam" >&2
    exit 2
fi

BUILD_ARGS=()
if [[ "${OV2SLAM_NO_CACHE:-0}" == "1" ]]; then
    BUILD_ARGS+=(--no-cache)
fi

echo "[build] Building $IMAGE from pinned OV2SLAM source..."
docker build "${BUILD_ARGS[@]}" -f "$DOCKERFILE" -t "$IMAGE" "$WS"
echo "[build] Built $IMAGE"
