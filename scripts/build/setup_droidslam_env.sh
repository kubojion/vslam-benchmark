#!/usr/bin/env bash
# Create the conda environment 'droidenv' and build DROID-SLAM extensions.
#
# Three build issues fixed vs. naive install (all required for torch 2.7+cu126):
#  1. NVCC_PREPEND_FLAGS is set to "UNSET -ccbin=..." by conda activate, which
#     passes the literal string "UNSET" as a filename to nvcc → fatal error.
#     Fix: unset the variable before invoking any nvcc compilation.
#  2. PyTorch 2.7 cpp_extension puts a -c flag in cuda_cflags AND the ninja rule
#     adds another -c explicitly, so nvcc receives -c -c → fatal error.
#     Fix: set TORCH_EXTENSION_SKIP_NVCC_GEN_DEPENDENCIES=1 AND patch one line
#     in torch/utils/cpp_extension.py to strip the extra -c from cuda_cflags.
#  3. CUDA headers (cusparse.h, cublas_v2.h, cusolverDn.h …) are not installed
#     by cuda-nvcc alone; they require the individual -dev packages.
#
set -eo pipefail
WS=$(cd "$(dirname "$0")/../.." && pwd)
ENV=droidenv

# Conda's activation scripts reference variables like SYS_SYSROOT that may be
# unset; sourcing them with -u enabled causes an immediate crash.  Disable -u
# only around conda operations, then restore strict mode for our own code.
set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"

if ! conda env list | awk '{print $1}' | grep -qx "$ENV"; then
    echo "[droidenv] creating env..."
    conda create -y -n "$ENV" python=3.10
fi
conda activate "$ENV"
set -u  # restore strict mode; our own code must not reference unbound variables

# PyTorch with CUDA 12.6 wheels (matches DROID-SLAM frozen reqs).
pip install --upgrade pip wheel
pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 \
    --index-url https://download.pytorch.org/whl/cu126

# CUDA 12.6 compiler + development headers (must match torch wheel's CUDA version)
conda install -y -c "nvidia/label/cuda-12.6.3" \
    cuda-nvcc=12.6.85 \
    libcublas-dev libcusparse-dev libcufft-dev libcurand-dev \
    libcusolver-dev cuda-cudart-dev cuda-profiler-api

# Fix 1: conda activate sets NVCC_PREPEND_FLAGS="UNSET -ccbin=..." which
# passes the literal "UNSET" as a filename to nvcc → always fatal.
unset NVCC_PREPEND_FLAGS

# Fix 2: PyTorch 2.7 cpp_extension puts -c in cuda_cflags AND the ninja
# cuda_compile rule adds -c again.  nvcc rejects the duplicate.
# The env-var disables the --generate-dependencies flag (also incompatible).
# The sed patch removes the stray -c from cuda_cflags so the rule only sees one.
export TORCH_EXTENSION_SKIP_NVCC_GEN_DEPENDENCIES=1
TORCH_CPP_EXT="$(python -c 'import torch.utils.cpp_extension as m; import os; print(os.path.abspath(m.__file__))')"
if ! grep -q "duplicate.*nvcc.*fatal" "$TORCH_CPP_EXT"; then
    sed -i \
      's/cuda_cflags = \[shlex\.quote(f) for f in cuda_cflags\]/cuda_cflags = [shlex.quote(f) for f in cuda_cflags]\n                cuda_cflags = [f for f in cuda_cflags if f != '"'"'-c'"'"']  # -c is added explicitly by ninja rule; duplicate causes nvcc fatal/' \
      "$TORCH_CPP_EXT"
    echo "[droidenv] patched $TORCH_CPP_EXT"
fi

export CUDA_HOME="$CONDA_PREFIX"
export TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST:-8.6}"

cd "$WS/src/DROID-SLAM"
pip install -r requirements.txt
pip install six matplotlib  # transitive deps missing in some environments

# C++/CUDA extensions built with --no-build-isolation so they use the
# already-installed torch (avoids a second torch download in an isolated env).
pip install --no-build-isolation ./thirdparty/lietorch
pip install --no-build-isolation ./thirdparty/pytorch_scatter
pip install --no-build-isolation -e .

# Pretrained model + sample data
[[ -f droid.pth ]] || ./tools/download_model.sh || true
[[ -d data/sfm_bench ]] || ./tools/download_sample_data.sh || true

echo "[droidenv] OK. Activate with: conda activate $ENV"
