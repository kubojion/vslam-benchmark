#!/usr/bin/env bash
# One-shot setup: create the air_slam Docker container and build AirSLAM inside it.
# Run this ONCE after cloning the repo (after Docker + nvidia-container-toolkit
# are installed and the image is pulled).
#
# Usage: bash scripts/setup/setup_airslam_docker.sh
set -eo pipefail

WS=$(cd "$(dirname "$0")/../.." && pwd)
CONTAINER="air_slam"
IMAGE="xukuanhit/air_slam:v4"

cd "$WS"

# ---- Pull image if missing -------------------------------------------------
if ! docker image inspect "$IMAGE" &>/dev/null; then
    echo "[setup] Pulling $IMAGE (~17 GB)..."
    docker pull "$IMAGE"
fi

# ---- Create container if missing -------------------------------------------
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "[setup] Container '$CONTAINER' already exists - skipping creation."
else
    echo "[setup] Creating container '$CONTAINER'..."
    docker run -d \
        --runtime nvidia --gpus all \
        --volume "$WS/src/airslam:/root/catkin_ws/src/air_slam" \
        --volume "$WS/datasets:/datasets:ro" \
        --volume "$WS/results-vo:/results-vo" \
        --volume "$WS/results-vio:/results-vio" \
        --volume "$WS/results-vio-lc:/results-vio-lc" \
        --volume "$WS/configs:/benchmark_configs:ro" \
        --name "$CONTAINER" \
        "$IMAGE" /bin/bash -c "tail -f /dev/null"
    echo "[setup] Waiting for container to initialise..."
    sleep 3
fi

# ---- Ensure container is running -------------------------------------------
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    docker start "$CONTAINER"
fi

# ---- Build AirSLAM ---------------------------------------------------------
echo "[setup] Building AirSLAM inside container (catkin_make)..."
docker exec "$CONTAINER" bash -c "
    source /opt/ros/noetic/setup.bash &&
    cd /root/catkin_ws &&
    catkin_make -DCMAKE_BUILD_TYPE=Release -j\$(nproc)
"

echo ""
echo "[setup] Done. AirSLAM is ready."
echo "  Run:  bash scripts/run/run_airslam.sh hortimulti strawberry02 1"
