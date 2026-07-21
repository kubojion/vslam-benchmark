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
# HAVE_LIBREALSENSE defaults ON upstream and hard-requires librealsense2 via
# find_package(REQUIRED), which aborts cmake if the SDK is absent. RealSense is
# only used for live camera input (Realsense.cpp / RealsenseRgbd.cpp); the
# dataset-playback app okvis_app_synchronous does not need it, so disable it.
# USE_CUDA=OFF: the bundled ceres-solver defaults USE_CUDA=ON, and its CUDA
# kernels fail to compile with nvcc against GCC 11's libstdc++ headers
# ("parameter packs not expanded with '...'" in std_function.h). The CUDA linear
# solvers are not used by okvis; CPU (SuiteSparse/Eigen) solvers are.
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_ROS2=OFF -DUSE_NN=OFF \
      -DHAVE_LIBREALSENSE=OFF -DUSE_CUDA=OFF .. 2>&1 | tail -20
make -j"$(nproc)" 2>&1 | tail -30

# Verify the synchronous app was built.
# Upstream places the app at build/okvis_app_synchronous (not build/okvis_apps/),
# which is also where run_okvis2.sh looks for it.
if [[ -x "$REPO/build/okvis_app_synchronous" ]]; then
    echo "[okvis2] OK: $REPO/build/okvis_app_synchronous"
else
    echo "[okvis2] ERROR: okvis_app_synchronous not found after build" >&2
    exit 1
fi
