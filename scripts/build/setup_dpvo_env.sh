#!/usr/bin/env bash
# Create the conda env 'dpvo' and build DPVO / DPV-SLAM.
# Repo:  https://github.com/princeton-vl/DPVO   (MIT)
# Paper: Teed et al., "Deep Patch Visual Odometry / SLAM", NeurIPS 2023
#
# Monocular, no IMU. Light: ~2.2 GB VRAM on our sequences (cf. MegaSaM/MASt3R-SLAM
# which OOM a 12 GB card). Replaces the dropped DROID-SLAM as the learned-VO entry.
set -eo pipefail
WS=$(cd "$(dirname "$0")/../.." && pwd)
ENV=dpvo
REPO="$WS/src/DPVO"

[[ -d "$REPO" ]] || git clone --recursive https://github.com/princeton-vl/DPVO.git "$REPO"

set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
if ! conda env list | awk '{print $1}' | grep -qx "$ENV"; then
    echo "[dpvo] creating conda env $ENV from environment.yml (torch 2.3.1 / cu121)"
    conda env create -f "$REPO/environment.yml"
fi
conda activate "$ENV"
set -u

# The env ships pytorch-cuda=12.1 (runtime) but no nvcc; the system nvcc is
# usually older and PyTorch hard-refuses to build extensions against a mismatch.
# Install a matching nvcc INTO the env.
if [[ "$(nvcc --version 2>/dev/null | grep -o 'release [0-9.]*')" != "release 12.1" ]]; then
    echo "[dpvo] installing cuda-nvcc 12.1 into env (matches torch's CUDA)"
    conda install -y -c nvidia cuda-nvcc=12.1 cuda-cudart-dev=12.1 cuda-cccl=12.1
fi

# Eigen 3.4 (header-only) into thirdparty/, per upstream README.
if [[ ! -f "$REPO/thirdparty/eigen-3.4.0/Eigen/Core" ]]; then
    echo "[dpvo] fetching Eigen 3.4.0"
    ( cd "$REPO"
      wget -q https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.zip
      unzip -q eigen-3.4.0.zip -d thirdparty && rm eigen-3.4.0.zip )
fi

# Build the CUDA extensions (cuda_corr, cuda_ba, lietorch_backends).
# --no-build-isolation is REQUIRED: with isolation, pip's build sandbox has no
# torch and setup.py dies with "No module named 'torch'".
echo "[dpvo] building CUDA extensions (cuda_corr, cuda_ba, lietorch_backends)"
( cd "$REPO"
  export CUDA_HOME="$CONDA_PREFIX"
  export PATH="$CONDA_PREFIX/bin:$PATH"
  export TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST:-8.9}"   # 8.9 = RTX 40-series
  pip install . --no-build-isolation )

# Pretrained weights (Dropbox, not Google Drive -- no gdown needed).
if [[ ! -f "$REPO/dpvo.pth" ]]; then
    echo "[dpvo] downloading weights (models.zip)"
    ( cd "$REPO"
      wget -q "https://www.dropbox.com/s/nap0u8zslspdwm4/models.zip" && unzip -o -q models.zip )
fi
[[ -f "$REPO/dpvo.pth" ]] || { echo "[dpvo] ERROR: dpvo.pth missing after download" >&2; exit 1; }

# DPV-SLAM loop closure additionally needs DPRetrieval; DPViewer (GUI) is not
# needed for headless benchmarking and is skipped.
#   ( cd "$REPO" && pip install ./DPRetrieval --no-build-isolation )

echo "[dpvo] env $ENV ready. Verify:"
echo "       conda run -n $ENV python -c 'from dpvo.dpvo import DPVO; import cuda_corr'"
