#!/usr/bin/env bash
# Build OKVIS2-X (https://github.com/ethz-mrl/OKVIS2-X) standalone, no ROS.
# Outputs binaries under src/okvis2x/build/
#
# OKVIS2-X is the successor to OKVIS2 (not a fork): it adds tightly-coupled
# GNSS, LiDAR and dense depth submapping. Only the sparse estimator app
# `okvis_app_synchronous` is built here -- the dense mapping apps
# (okvis2x_app_*) need LibTorch/PCL and produce submap meshes that the
# benchmark has no metrics for.
#
# System deps (Ubuntu 22.04, install manually with apt):
#   cmake libgoogle-glog-dev libeigen3-dev libsuitesparse-dev \
#   libboost-dev libboost-filesystem-dev libopencv-dev libpcl-dev \
#   libgeographic-dev
#
# Ceres needs BLAS/LAPACK. Upstream suggests `libatlas-base-dev`, but any
# implementation works -- `libopenblas-dev` + `liblapack-dev` (already pulled
# in by libsuitesparse-dev) is sufficient and is what this build uses.
#
# NOTE: on Ubuntu 24.04 the GeographicLib package is `libgeographiclib-dev`
# instead of `libgeographic-dev`. GeographicLib is required for the geodetic
# GNSS mode used by the gnss-vio run type.
set -euo pipefail
WS=$(cd "$(dirname "$0")/../.." && pwd)
REPO="$WS/src/okvis2x"
[[ -d "$REPO" ]] || { echo "[okvis2x] clone first: git clone https://github.com/ethz-mrl/OKVIS2-X.git $REPO"; exit 1; }

cd "$REPO"

# The `supereight2` submodule is declared with an SSH URL (git@github.com:...)
# in .gitmodules, which fails without a GitHub SSH key even though the repo is
# public. Rewrite it to HTTPS before initialising.
git submodule set-url supereight2 https://github.com/ethz-mrl/supereight2.git
git submodule sync --recursive 2>&1 | tail -1

# --force is required, not cosmetic: if the initial `clone --recurse-submodules`
# aborted partway (e.g. on the SSH URL above), some submodules are left
# registered-but-empty, and a plain `update --init --recursive` silently leaves
# them that way. cmake then fails with "doesn't exist. Did you forget to update
# the git submodules?".
git submodule update --init --recursive --force 2>&1 | tail -3

for sm in external/DBoW2 external/brisk external/ceres-solver external/opengv supereight2; do
    [[ -f "$REPO/$sm/CMakeLists.txt" ]] || {
        echo "[okvis2x] ERROR: submodule '$sm' is empty after init" >&2; exit 1; }
done

mkdir -p build && cd build
# Release build. BUILD_ROS2 / HAVE_LIBREALSENSE / USE_NN all default to ON
# upstream, so each must be disabled explicitly for a lean estimator-only build.
#
# USE_CUDA=OFF targets the *bundled* ceres-solver (external/ceres-solver), whose
# own USE_CUDA defaults to ON. If a CUDA toolkit is present, ceres tries to build
# its CUDA kernels with nvcc, which fails against GCC 11 headers
# ("parameter packs not expanded with '...'" in std_function.h). The estimator is
# CPU-only, so CUDA buys nothing here.
cmake -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_ROS2=OFF \
      -DHAVE_LIBREALSENSE=OFF \
      -DUSE_NN=OFF \
      -DUSE_CUDA=OFF \
      .. 2>&1 | tail -20
# Keep full compiler output on failure -- `| tail` would swallow the first error.
make -j"$(nproc)" okvis_app_synchronous

APP="$REPO/build/okvis_app_synchronous"
if [[ ! -x "$APP" ]]; then
    echo "[okvis2x] ERROR: okvis_app_synchronous not found after build" >&2
    exit 1
fi

# okvis_app_synchronous loads the DBoW2 vocabulary from its own directory
# (dBowVocDir = dirname(argv[0])) and aborts if it is missing. Nothing in
# CMake copies it there, so do it here.
cp -n "$REPO/resources/small_voc.yml.gz" "$REPO/build/small_voc.yml.gz"
[[ -f "$REPO/build/small_voc.yml.gz" ]] || {
    echo "[okvis2x] ERROR: small_voc.yml.gz not staged next to the binary" >&2
    exit 1
}

echo "[okvis2x] OK: $APP"
