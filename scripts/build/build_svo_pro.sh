#!/usr/bin/env bash
# Build the SVO Pro image used by scripts/run/run_svo_pro.sh.
#
# Usage: scripts/build/build_svo_pro.sh
#
# Upstream master at a pinned commit, unmodified, built in a ROS Noetic image as the
# upstream README describes (front end + Ceres back end + loop closing, without the
# optional iSAM2 global map). Upstream pins its catkin dependencies by branch name only;
# the commits that were actually built are stored in the image at
# /svo_ws/dependencies.exact.yaml and printed here.
set -euo pipefail

WS=$(cd "$(dirname "$0")/../.." && pwd)
COMMIT="ca371f304637e7fb355cf4624d0a02da4e3da220"
IMAGE="${SVO_PRO_IMAGE:-vslam_svo_pro:noetic}"

if [[ ! -d "$WS/src/svo_pro/.git" ]]; then
    git clone -q https://github.com/uzh-rpg/rpg_svo_pro_open.git "$WS/src/svo_pro"
    git -C "$WS/src/svo_pro" checkout -q "$COMMIT"
fi
[[ "$(git -C "$WS/src/svo_pro" rev-parse HEAD)" == "$COMMIT" ]] \
    || { echo "[svo_pro] ERROR: src/svo_pro is not at $COMMIT" >&2; exit 2; }
[[ -z "$(git -C "$WS/src/svo_pro" status --porcelain)" ]] \
    || { echo "[svo_pro] ERROR: src/svo_pro has local changes" >&2; exit 2; }

docker build -f "$WS/scripts/setup/Dockerfile.svo_pro" -t "$IMAGE" "$WS/src/svo_pro"
docker run --rm --entrypoint /bin/bash "$IMAGE" -c \
    'test -x /svo_ws/devel/lib/svo_ros/svo_benchmark && cat /svo_ws/dependencies.exact.yaml'
echo "[svo_pro] built $IMAGE ($(docker image inspect -f '{{.Id}}' "$IMAGE"))"
