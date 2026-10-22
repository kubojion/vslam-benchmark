#!/usr/bin/env bash
# Create this checkout's private Voxel-SVIO container for the Sielinko CPU search.
# Usage: scripts/setup/create_sielinko_search_voxel_container.sh [cpus=4-7]
#
# The production container `voxel_svio` mounts the main checkout's configs/,
# scripts/ and results/, so search runs through it would write into main. This
# container is a snapshot of its filesystem (the reviewed native builds live
# there), mounts only this checkout plus main's datasets read-only (the views
# link to those images), and is pinned to the search's lane 2 with a 50 GiB cap.
# It starts no estimator. Run only with the user's go.
set -euo pipefail
WS=$(cd "$(dirname "$0")/../.." && pwd)
MAIN=/data/imoroz/vslam-benchmark
NAME=sielinko_search_voxel_20261022
IMAGE=vslam-sielinko-search-voxel:20261022
CPUS=${1:-4-7}

[[ "$WS" != "$MAIN" ]] || { echo 'run from the isolated search checkout' >&2; exit 2; }
[[ -e "$WS/src/voxel_svio/.git" ]] || { echo 'private src/voxel_svio missing (prepare_sielinko_private_sources.py)' >&2; exit 2; }
if docker container inspect "$NAME" >/dev/null 2>&1; then
    echo "container $NAME already exists; inspect it instead of recreating" >&2; exit 2
fi
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    # Never pause or disturb a production Voxel run: commit only while none is active.
    if pgrep -f 'scripts/run/run_voxel_svio\.sh' >/dev/null; then
        echo 'a Voxel-SVIO run is active; snapshot at a boundary' >&2; exit 2
    fi
    docker commit --pause=false voxel_svio "$IMAGE" >/dev/null
fi
docker create --name "$NAME" \
    --memory 50g --memory-swap 50g --cpuset-cpus "$CPUS" \
    --volume "$WS/configs:/benchmark_configs:ro" \
    --volume "$WS/scripts:/benchmark_scripts:ro" \
    --volume "$WS/datasets:/datasets:ro" \
    --volume "$WS/results:/results" \
    --volume "$MAIN/datasets:$MAIN/datasets:ro" \
    --volume "$WS/src/voxel_svio:/root/catkin_ws/src/voxel_svio" \
    --workdir /root/catkin_ws \
    --entrypoint /ros_entrypoint.sh \
    "$IMAGE" /bin/bash -c 'exec tail -f /dev/null' >/dev/null
docker inspect "$NAME" --format \
    '{{.Name}} image={{.Image}} memory={{.HostConfig.Memory}} swap={{.HostConfig.MemorySwap}} cpus={{.HostConfig.CpusetCpus}} {{range .Mounts}}{{.Source}}={{.Destination}}({{if .RW}}rw{{else}}ro{{end}}) {{end}}'
