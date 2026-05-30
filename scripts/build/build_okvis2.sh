#!/usr/bin/env bash
# Build OKVIS2 (https://github.com/ethz-mrl/okvis2) standalone, no ROS.
# Outputs binaries under src/okvis2/build/okvis_apps/
#
# System deps (must be installed manually with apt):
#   libgoogle-glog-dev libgflags-dev libatlas-base-dev libeigen3-dev \
#   libsuitesparse-dev libboost-filesystem-dev libopencv-dev
#
# If `libgoogle-glog-dev` is missing, ceres-solver bundled inside the OKVIS2
# `external/` tree falls back to MINIGLOG automatically, but OKVIS2 itself
# expects google::InitGoogleLogging(); we therefore install glog explicitly.
set -euo pipefail
WS=$(cd "$(dirname "$0")/../.." && pwd)
REPO="$WS/src/okvis2"
[[ -d "$REPO" ]] || { echo "[okvis2] clone first: git clone --recurse-submodules https://github.com/ethz-mrl/okvis2.git $REPO"; exit 1; }

cd "$REPO"
# Make sure the submodules are populated.
git submodule update --init --recursive 2>&1 | tail -3

mkdir -p build && cd build
# Release build, no ROS2, no CNN (libtorch optional).
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_ROS2=OFF -DUSE_NN=OFF .. 2>&1 | tail -20
make -j"$(nproc)" 2>&1 | tail -30

# Verify the synchronous app was built.
if [[ -x "$REPO/build/okvis_apps/okvis_app_synchronous" ]]; then
    echo "[okvis2] OK: $REPO/build/okvis_apps/okvis_app_synchronous"
else
    echo "[okvis2] ERROR: okvis_app_synchronous not found after build" >&2
    exit 1
fi
