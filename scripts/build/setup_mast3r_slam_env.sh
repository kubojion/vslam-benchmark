#!/usr/bin/env bash
# Create the conda environment 'mast3r_slam' and clone MASt3R-SLAM.
# Repo:  https://github.com/rmurai0610/MASt3R-SLAM
# Paper: Murai et al., "MASt3R-SLAM: Real-Time Dense SLAM with 3D Reconstruction
#        Priors", arXiv:2412.12392
#
# Notes:
#   * Monocular. The retrieval head supports loop closure.
#   * Map this to run_type=vio-lc (monocular + LC) by setting USE_IMU=false
#     inside the run script and routing output to results-vio-lc/. We expose
#     run_type=vo (LC disabled) and run_type=vio-lc (LC enabled) only.
#   * vio (LC off, IMU on) is not supported by this algorithm.
set -eo pipefail
WS=$(cd "$(dirname "$0")/../.." && pwd)
ENV=mast3r_slam
REPO="$WS/src/MASt3R-SLAM"

set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
if ! conda env list | awk '{print $1}' | grep -qx "$ENV"; then
    echo "[mast3r_slam] creating conda env $ENV (python=3.11)"
    conda create -y -n "$ENV" python=3.11
fi
conda activate "$ENV"
set -u

pip install --upgrade pip wheel

# PyTorch 2.5.1 + CUDA 12.1 wheels (upstream supports 11.8 / 12.1 / 12.4).
pip install torch==2.5.1 torchvision==0.20.1 \
    --index-url https://download.pytorch.org/whl/cu121

if [[ ! -d "$REPO" ]]; then
    echo "[mast3r_slam] cloning repo (with submodules) into src/MASt3R-SLAM"
    git clone --recursive https://github.com/rmurai0610/MASt3R-SLAM.git "$REPO"
fi

cd "$REPO"
[[ -f requirements.txt ]] && pip install -r requirements.txt || true

# Install the package itself (per upstream README)
pip install -e . || true

echo "[mast3r_slam] env $ENV ready. Activate with: conda activate $ENV"
echo "[mast3r_slam] NOTE: download MASt3R checkpoints per $REPO/README.md"
echo "             before running scripts/run/run_mast3r_slam.sh."
