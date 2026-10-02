#!/usr/bin/env bash
# Isolated shutdown-only build; original checkout/container executable stay intact.
set -euo pipefail
WS=$(cd "$(dirname "$0")/../.." && pwd)
PREFIX=${1:?usage: build_voxel_shutdown.sh /root/fresh_catkin_workspace}
[[ "$PREFIX" =~ ^/root/[a-zA-Z0-9_-]+$ ]] || exit 2
docker exec voxel_svio test ! -e "$PREFIX"
PATCH_PATH=$(docker exec voxel_svio mktemp /tmp/voxel-shutdown-XXXXXXXX.patch)
trap 'docker exec voxel_svio rm -f "$PATCH_PATH"' EXIT
docker cp "$WS/docs/upstream/voxel-svio-subscriber-lifetime.patch" "voxel_svio:$PATCH_PATH"
docker exec voxel_svio bash -c "
    set -e
    mkdir -p '$PREFIX/src'
    cp -a /root/catkin_ws/src/voxel_svio '$PREFIX/src/'
    patch -d '$PREFIX/src/voxel_svio' -p1 < '$PATCH_PATH'
    source /opt/ros/noetic/setup.bash
    catkin_make -C '$PREFIX' -DCMAKE_BUILD_TYPE=Release -j4
"
