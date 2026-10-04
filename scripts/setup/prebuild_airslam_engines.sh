#!/usr/bin/env bash
# Build the dataset-named AirSLAM LightGlue TensorRT caches without processing
# or writing any benchmark result cell. Engines are hardware/runtime-specific.
set -euo pipefail

WS=$(cd "$(dirname "$0")/../.." && pwd)
CONTAINER=air_slam

docker ps --format '{{.Names}}' | grep -qx "$CONTAINER" || {
    echo "ERROR: AirSLAM container is not running: $CONTAINER" >&2
    exit 2
}

if docker exec "$CONTAINER" pgrep -f '[v]isual_odometry' >/dev/null; then
    echo "ERROR: AirSLAM visual_odometry is already running; refusing to interfere" >&2
    exit 2
fi

build_one() {
    local dataset=$1
    local config="$WS/configs/airslam/${dataset}_vo.yaml"
    local camera="$WS/configs/airslam/${dataset}_camera_vo.yaml"
    [[ -f "$camera" ]] || camera="$WS/configs/airslam/${dataset}_camera.yaml"
    [[ -f "$config" && -f "$camera" ]] || {
        echo "ERROR: missing AirSLAM config for $dataset" >&2
        return 2
    }

    local engine
    engine=$(awk '/^[[:space:]]*engine_file:/ {print $2; exit}' "$config" | tr -d '"')
    [[ -n "$engine" ]] || { echo "ERROR: no engine_file in $config" >&2; return 2; }
    if [[ -s "$WS/src/airslam/output/$engine" ]]; then
        echo "[airslam-engine] already present: $engine"
        return 0
    fi

    echo "[airslam-engine] building $engine for the installed GPU/TensorRT runtime"
    docker exec \
        -e AIRSLAM_CONFIG="/benchmark_configs/airslam/${dataset}_vo.yaml" \
        -e AIRSLAM_CAMERA="/benchmark_configs/airslam/$(basename "$camera")" \
        "$CONTAINER" bash -lc '
            set -e
            source /opt/ros/noetic/setup.bash
            source /root/catkin_ws/devel/setup.bash
            build_root=/tmp/airslam_engine_build
            mkdir -p "$build_root/mav0/cam0/data" "$build_root/mav0/cam1/data" "$build_root/out"
            roscore >"$build_root/roscore.log" 2>&1 &
            master_pid=$!
            cleanup() { kill "$master_pid" 2>/dev/null || true; }
            trap cleanup EXIT
            sleep 2
            rosrun air_slam visual_odometry \
                _config_path:="$AIRSLAM_CONFIG" \
                _camera_config_path:="$AIRSLAM_CAMERA" \
                _model_dir:=/root/catkin_ws/src/air_slam/output \
                _dataroot:="$build_root/mav0" \
                _saving_dir:="$build_root/out"
        '
    [[ -s "$WS/src/airslam/output/$engine" ]] || {
        echo "ERROR: AirSLAM did not produce $engine" >&2
        return 1
    }
    echo "[airslam-engine] ready: $engine ($(stat -c %s "$WS/src/airslam/output/$engine") bytes)"
}

build_one euroc_mav
build_one hortimulti
build_one rosariov2
build_one zed2i
build_one citrusfarm

echo "[airslam-engine] all campaign engines are ready"
