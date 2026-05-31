#!/usr/bin/env bash
# One-shot setup: build the vslam_cifasis_gnss_si Docker image and create a
# long-running container with the standard bind mounts.
#
# Run this ONCE after cloning CIFASIS GNSS-SI:
#   git clone https://github.com/CIFASIS/gnss-stereo-inertial-fusion src/cifasis_gnss_si
#
# The image embeds a built copy of the source (because upstream's Dockerfile
# uses COPY + build inside the image). Re-run this script if you pull new
# changes upstream.
#
# Usage: bash scripts/setup/setup_cifasis_gnss_si_docker.sh
set -eo pipefail

WS=$(cd "$(dirname "$0")/../.." && pwd)
CONTAINER="cifasis_gnss_si"
IMAGE="vslam_cifasis_gnss_si:noetic"
DOCKERFILE="$WS/scripts/setup/cifasis_gnss_si.Dockerfile"
SRC_DIR="$WS/src/cifasis_gnss_si"

cd "$WS"

if [[ ! -d "$SRC_DIR" ]]; then
    echo "ERROR: $SRC_DIR not found." >&2
    echo "Clone with: git clone https://github.com/CIFASIS/gnss-stereo-inertial-fusion src/cifasis_gnss_si" >&2
    exit 2
fi

if ! docker image inspect "$IMAGE" &>/dev/null; then
    echo "[setup] Building $IMAGE (Pangolin + ORB-SLAM3 + GNSS-SI; ~30-60 min)..."
    # Use the source tree as build context so upstream Dockerfile's COPY ./ works.
    docker build -f "$DOCKERFILE" -t "$IMAGE" "$SRC_DIR"
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
echo "[setup] Done. CIFASIS GNSS-SI is ready."
echo "  Run:  bash scripts/run/run_cifasis_gnss_si.sh rosariov2 sequence1 1 gnss-vio"
