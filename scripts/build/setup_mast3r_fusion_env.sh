#!/usr/bin/env bash
# Install MASt3R-Fusion (monocular feed-forward front end + IMU/GNSS factor graph).
#
# Usage: scripts/build/setup_mast3r_fusion_env.sh
#
# Follows the upstream README: conda env (Python 3.11.9, torch 2.5.1 + CUDA 12.4), the
# authors' modified GTSAM built with its Python wrapper, then the project and its two
# vendored packages, and the three MASt3R checkpoints. Source trees are pinned.
set -euo pipefail

WS=$(cd "$(dirname "$0")/../.." && pwd)
REPO="$WS/src/mast3r_fusion"
COMMIT="f4469ea8e05a9b556611033871b94c3da3cb5164"
GTSAM_DIR="$WS/third_party/gtsam-mast3r-fusion"
ENV_NAME="${MAST3R_FUSION_CONDA_ENV:-mast3r_fusion}"
CKPT_URL="https://download.europe.naverlabs.com/ComputerVision/MASt3R"

if [[ ! -d "$REPO/.git" ]]; then
    git clone -q --recursive https://github.com/GREAT-WHU/MASt3R-Fusion.git "$REPO"
    git -C "$REPO" checkout -q "$COMMIT" && git -C "$REPO" submodule update -q --init --recursive
fi
[[ "$(git -C "$REPO" rev-parse HEAD)" == "$COMMIT" ]] \
    || { echo "[mast3r_fusion] ERROR: $REPO is not at $COMMIT" >&2; exit 2; }

set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda env list | awk '{print $1}' | grep -qx "$ENV_NAME" || conda create -y -q -n "$ENV_NAME" python=3.11.9
conda activate "$ENV_NAME"
set -u

pip install -q torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124
pip install -q opencv-python==4.10.0.84 opencv-contrib-python==4.10.0.84 h5py pyparsing

# Modified GTSAM (marginalisation, Sim(3) visual factors). The upstream branch head is
# recorded in third_party/gtsam-mast3r-fusion.commit for the runtime identity.
# Its CMake prefers a system pybind11; Ubuntu 22.04's is too old for Python 3.11, so
# the lookup is disabled and the copy bundled with GTSAM is used.
if [[ ! -d "$GTSAM_DIR/.git" ]]; then
    git clone -q https://github.com/yuxuanzhou97/gtsam.git "$GTSAM_DIR"
fi
git -C "$GTSAM_DIR" rev-parse HEAD > "$WS/third_party/gtsam-mast3r-fusion.commit"
python -c "import gtsam" 2>/dev/null || {
    pip install -q "pyparsing" "pybind11-stubgen" "numpy==1.26.4"
    mkdir -p "$GTSAM_DIR/build" && cd "$GTSAM_DIR/build"
    cmake .. -DCMAKE_BUILD_TYPE=Release -DGTSAM_BUILD_PYTHON=1 -DGTSAM_PYTHON_VERSION=3.11.9 \
        -DPYTHON_EXECUTABLE="$(which python)" -DGTSAM_BUILD_TESTS=OFF \
        -DCMAKE_DISABLE_FIND_PACKAGE_pybind11=ON \
        -DGTSAM_BUILD_EXAMPLES_ALWAYS=OFF -DGTSAM_BUILD_UNSTABLE=ON > cmake.log
    make python-install -j"$(nproc)" > make.log 2>&1 || { tail -40 make.log; exit 1; }
}

# thirdparty/mast3r compiles a CUDA extension against the installed torch, so it must see
# the environment (no build isolation) and the CUDA 12.4 toolkit. thirdparty/in3d (the
# viewer, imported even with --no-viz) needs the opposite: its own isolated build
# requirements to generate the imgui sources.
export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda-12.4}"
export PATH="$CUDA_HOME/bin:$PATH"
pip install -q "setuptools==70.0.0" wheel
cd "$REPO"
pip install -q --no-build-isolation -e thirdparty/mast3r
pip install -q -e thirdparty/in3d
pip install -q --no-build-isolation -e .
# main_global_optimization.py calls matplotlib.cm.get_cmap (removed in matplotlib 3.9)
# after it has written its result; without this pin the stage exits with an error.
pip install -q "matplotlib==3.8.4"

# Kept outside the checkout (the runner links them into each attempt's working directory).
CKPT="$WS/third_party/mast3r-fusion-checkpoints"
mkdir -p "$CKPT"
for f in MASt3R_ViTLarge_BaseDecoder_512_catmlpdpt_metric.pth \
         MASt3R_ViTLarge_BaseDecoder_512_catmlpdpt_metric_retrieval_trainingfree.pth \
         MASt3R_ViTLarge_BaseDecoder_512_catmlpdpt_metric_retrieval_codebook.pkl; do
    [[ -s "$CKPT/$f" ]] || wget -q "$CKPT_URL/$f" -O "$CKPT/$f"
done
sha256sum "$CKPT"/* | tee "$WS/third_party/mast3r-fusion-checkpoints.sha256"

# Bytecode caches inside the checkout would count as source changes for the per-run capture.
find "$REPO" -name __pycache__ -not -path "*/.git/*" -prune -exec rm -rf {} +
PYTHONDONTWRITEBYTECODE=1 python -c "
import torch, gtsam, lietorch, mast3r_fusion
print('[mast3r_fusion] torch', torch.__version__, 'cuda', torch.cuda.is_available(), 'gtsam', gtsam.__file__)"
