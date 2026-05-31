#!/usr/bin/env bash
# One-shot setup: build the vslam_vins_fusion Docker image and create a
# long-running container with the standard bind mounts.
#
# Run this ONCE after cloning VINS-Fusion:
#   git clone https://github.com/HKUST-Aerial-Robotics/VINS-Fusion src/VINS-Fusion
#
# The image embeds a built copy of the source (catkin_make inside the image).
# Re-run this script if you pull new changes upstream or modify the source.
#
# Usage: bash scripts/setup/setup_vins_fusion_docker.sh
set -eo pipefail

WS=$(cd "$(dirname "$0")/../.." && pwd)
CONTAINER="vins_fusion"
IMAGE="vslam_vins_fusion:noetic"
DOCKERFILE="$WS/scripts/setup/vins_fusion.Dockerfile"
SRC_DIR="$WS/src/VINS-Fusion"

cd "$WS"

if [[ ! -d "$SRC_DIR" ]]; then
    echo "ERROR: $SRC_DIR not found." >&2
    echo "Clone with: git clone https://github.com/HKUST-Aerial-Robotics/VINS-Fusion src/VINS-Fusion" >&2
    exit 2
fi

if ! docker image inspect "$IMAGE" &>/dev/null; then
    echo "[setup] Building $IMAGE (Ceres + VINS-Fusion catkin build; ~20-40 min)..."
    docker build -f "$DOCKERFILE" -t "$IMAGE" "$WS"
fi

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "[setup] Container '$CONTAINER' already exists - skipping creation."
else
    echo "[setup] Creating container '$CONTAINER'..."
    docker run -d \
        --network host \
        --volume "$WS/datasets:/datasets:ro" \
        --volume "$WS/results-vio:/results-vio" \
        --volume "$WS/results-vio-lc:/results-vio-lc" \
        --volume "$WS/results-gnss-vio:/results-gnss-vio" \
        --volume "$WS/configs:/benchmark_configs:ro" \
        --volume "$WS/scripts:/benchmark_scripts:ro" \
        --name "$CONTAINER" \
        "$IMAGE" /bin/bash -c "tail -f /dev/null"
    sleep 3
fi

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    docker start "$CONTAINER"
fi

echo ""
echo "[setup] Done. VINS-Fusion is ready."
echo "  Run:  bash scripts/run/run_vins_fusion_gps.sh rosariov2 sequence1 1 gnss-vio"
