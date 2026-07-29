#!/usr/bin/env bash
# Build OV2SLAM and create its long-running benchmark container.
set -euo pipefail

WS=$(cd "$(dirname "$0")/../.." && pwd)
CONTAINER="ov2slam"
IMAGE="vslam_ov2slam:noetic"

if [[ ! -f "$WS/src/ov2slam/CMakeLists.txt" ]]; then
    echo "ERROR: OV2SLAM submodule is not initialized." >&2
    echo "Run: git submodule update --init src/ov2slam" >&2
    exit 2
fi

if ! docker image inspect "$IMAGE" &>/dev/null; then
    bash "$WS/scripts/build/build_ov2slam.sh"
fi

if docker inspect "$CONTAINER" &>/dev/null; then
    echo "[setup] Container '$CONTAINER' already exists."
else
    echo "[setup] Creating container '$CONTAINER'..."
    docker run -d \
        --network host \
        --volume "$WS/datasets:/datasets:ro" \
        --volume "$WS/results-vo:/results-vo" \
        --volume "$WS/results-vo-lc:/results-vo-lc" \
        --volume "$WS/configs:/benchmark_configs:ro" \
        --volume "$WS/scripts:/benchmark_scripts:ro" \
        --name "$CONTAINER" \
        "$IMAGE" /bin/bash -c "tail -f /dev/null"
fi

if [[ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER")" != "true" ]]; then
    docker start "$CONTAINER"
fi

echo "[setup] OV2SLAM is ready."
echo "  Run: bash scripts/run/run_ov2slam.sh euroc_mav MH_01_easy 1 vo-lc"
