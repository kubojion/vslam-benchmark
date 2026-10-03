#!/usr/bin/env bash
# Install NVIDIA cuVSLAM (PyCuVSLAM) 17.0.0 for the benchmark.
#
# Usage: scripts/build/setup_cuvslam_env.sh
#
# cuVSLAM ships as a prebuilt wheel (CUDA 12, CPython 3.10, glibc 2.35 = Ubuntu 22.04);
# nothing is compiled. The source checkout is only examples/bindings for reference and
# for the per-run implementation capture. Licence: NVIDIA Community License (research use).
set -euo pipefail

WS=$(cd "$(dirname "$0")/../.." && pwd)
TAG="v17.0.0"
COMMIT="57f42cc92d93eef47577d726789852a350b2a369"
WHEEL="cuvslam-17.0.0+cu12-cp310-cp310-manylinux_2_35_x86_64.whl"
WHEEL_SHA256="0ae3113e43902e0c15423992450510aef241f84207718ed77a1d2d39f28744c1"
WHEEL_URL="https://github.com/nvidia-isaac/cuVSLAM/releases/download/${TAG}/${WHEEL//+/%2B}"
ENV_NAME="${CUVSLAM_CONDA_ENV:-cuvslam}"
CUDA_LIB="${CUVSLAM_CUDA_LIB:-/usr/local/cuda-12.4/lib64}"

if [[ ! -d "$WS/src/cuvslam/.git" ]]; then
    git clone -q --branch "$TAG" --depth 1 https://github.com/nvidia-isaac/cuVSLAM.git "$WS/src/cuvslam"
fi
[[ "$(git -C "$WS/src/cuvslam" rev-parse HEAD)" == "$COMMIT" ]] \
    || { echo "[cuvslam] ERROR: src/cuvslam is not at $COMMIT" >&2; exit 2; }

mkdir -p "$WS/third_party/wheels"
[[ -f "$WS/third_party/wheels/$WHEEL" ]] || curl -fsSL -o "$WS/third_party/wheels/$WHEEL" "$WHEEL_URL"
echo "$WHEEL_SHA256  $WS/third_party/wheels/$WHEEL" | sha256sum -c -

set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda env list | awk '{print $1}' | grep -qx "$ENV_NAME" || conda create -y -q -n "$ENV_NAME" python=3.10
conda activate "$ENV_NAME"
set -u
pip install -q "$WS/third_party/wheels/$WHEEL" numpy pyyaml pillow opencv-python-headless scipy

LD_LIBRARY_PATH="$CUDA_LIB${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
    python3 -c "import cuvslam; print('[cuvslam] installed', cuvslam.get_version()[0])"
python3 "$WS/scripts/setup/build_sensor_profiles.py" --repo "$WS" --check
