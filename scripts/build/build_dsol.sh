#!/usr/bin/env bash
# Build the DSOL image used by scripts/run/run_dsol.sh.
#
# Usage: scripts/build/build_dsol.sh
#
# Upstream main at a pinned commit, unmodified, built in a ROS Noetic image with the
# dependency versions of the upstream CI recipe (see scripts/setup/Dockerfile.dsol).
set -euo pipefail

WS=$(cd "$(dirname "$0")/../.." && pwd)
COMMIT="2b059e6781244a5758208bab19b26bd3a7912a71"
IMAGE="${DSOL_IMAGE:-vslam_dsol:noetic}"

if [[ ! -d "$WS/src/dsol/.git" ]]; then
    git clone -q https://github.com/versatran01/dsol.git "$WS/src/dsol"
    git -C "$WS/src/dsol" checkout -q "$COMMIT"
fi
[[ "$(git -C "$WS/src/dsol" rev-parse HEAD)" == "$COMMIT" ]] \
    || { echo "[dsol] ERROR: src/dsol is not at $COMMIT" >&2; exit 2; }
[[ -z "$(git -C "$WS/src/dsol" status --porcelain)" ]] \
    || { echo "[dsol] ERROR: src/dsol has local changes" >&2; exit 2; }

docker build -f "$WS/scripts/setup/Dockerfile.dsol" -t "$IMAGE" "$WS/src/dsol"
docker run --rm "$IMAGE" test -x /catkin_ws/devel/lib/dsol/sv_dsol_node_data
echo "[dsol] built $IMAGE ($(docker image inspect -f '{{.Id}}' "$IMAGE"))"
