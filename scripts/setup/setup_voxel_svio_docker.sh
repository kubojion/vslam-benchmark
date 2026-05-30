#!/usr/bin/env bash
# One-shot setup: build the vslam_voxel_svio Docker image, create the container,
# and build voxel_svio inside it.
#
# Run this ONCE after cloning the repo (after Docker is installed and the
# voxel_svio source is checked out under src/voxel_svio).
#
# Usage: bash scripts/setup/setup_voxel_svio_docker.sh
set -eo pipefail

WS=$(cd "$(dirname "$0")/../.." && pwd)
CONTAINER="voxel_svio"
IMAGE="vslam_voxel_svio:noetic"
DOCKERFILE="$WS/scripts/setup/voxel_svio.Dockerfile"

cd "$WS"

# ---- Sanity ----------------------------------------------------------------
if [[ ! -d "$WS/src/voxel_svio" ]]; then
    echo "ERROR: $WS/src/voxel_svio not found." >&2
    echo "Clone with: git clone https://github.com/ZikangYuan/voxel_svio.git src/voxel_svio" >&2
    exit 2
fi

# ---- Build image if missing ------------------------------------------------
if ! docker image inspect "$IMAGE" &>/dev/null; then
    echo "[setup] Building image $IMAGE (~3 GB)..."
    docker build -f "$DOCKERFILE" -t "$IMAGE" "$WS"
fi

# ---- Create container if missing -------------------------------------------
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "[setup] Container '$CONTAINER' already exists - skipping creation."
else
    echo "[setup] Creating container '$CONTAINER'..."
    docker run -d \
        --network host \
        --volume "$WS/src/voxel_svio:/root/catkin_ws/src/voxel_svio" \
        --volume "$WS/datasets:/datasets:ro" \
        --volume "$WS/results-vo:/results-vo" \
        --volume "$WS/results-vio:/results-vio" \
        --volume "$WS/results-vio-lc:/results-vio-lc" \
        --volume "$WS/configs:/benchmark_configs:ro" \
        --volume "$WS/scripts:/benchmark_scripts:ro" \
        --name "$CONTAINER" \
        "$IMAGE" /bin/bash -c "tail -f /dev/null"
    echo "[setup] Waiting for container to initialise..."
    sleep 3
fi

# ---- Ensure container is running -------------------------------------------
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    docker start "$CONTAINER"
fi

# ---- Make sure the output dir exists (voxel_svio writes pose.txt here) -----
mkdir -p "$WS/src/voxel_svio/output"

# ---- Build voxel_svio ------------------------------------------------------
echo "[setup] Building voxel_svio inside container (catkin_make)..."
docker exec "$CONTAINER" bash -c "
    set -e
    source /opt/ros/noetic/setup.bash &&
    cd /root/catkin_ws &&
    catkin_make -DCMAKE_BUILD_TYPE=Release -j\$(nproc)
"

echo ""
echo "[setup] Done. Voxel-SVIO is ready."
echo "  Run:  bash scripts/run/run_voxel_svio.sh euroc_mav MH_01_easy 1 vio"
