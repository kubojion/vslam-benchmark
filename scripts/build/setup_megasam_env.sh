#!/usr/bin/env bash
# Create the conda environment 'megasam' and clone MegaSaM.
# Repo:  https://github.com/mega-sam/mega-sam   (Apache-2.0)
# Paper: Li et al., "MegaSaM: Accurate, Fast and Robust Structure and Motion
#        from Casual Dynamic Videos", arXiv:2412.04463
#
# Notes:
#   * Monocular VO. No IMU. No loop closure.
#   * Only run_type=vo is meaningful for this algorithm.
#   * Upstream is research code; this script wires up a conda env and clones
#     the repo; you will likely need to follow the upstream README to download
#     model weights before run_megasam.sh succeeds.
set -eo pipefail
WS=$(cd "$(dirname "$0")/../.." && pwd)
ENV=megasam
REPO="$WS/src/mega-sam"

set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
if ! conda env list | awk '{print $1}' | grep -qx "$ENV"; then
    echo "[megasam] creating conda env $ENV (python=3.10)"
    conda create -y -n "$ENV" python=3.10
fi
conda activate "$ENV"
set -u

pip install --upgrade pip wheel

# PyTorch 2.0.1 + CUDA 11.8 wheels (matches upstream requirements).
pip install torch==2.0.1 torchvision==0.15.2 \
    --index-url https://download.pytorch.org/whl/cu118

if [[ ! -d "$REPO" ]]; then
    echo "[megasam] cloning repo into src/mega-sam"
    git clone https://github.com/mega-sam/mega-sam.git "$REPO"
fi

cd "$REPO"
[[ -f requirements.txt ]] && pip install -r requirements.txt || true

# Common extras used by the MegaSaM demo
pip install opencv-python imageio[ffmpeg] scipy matplotlib tqdm einops

echo "[megasam] env $ENV ready. Activate with: conda activate $ENV"
echo "[megasam] NOTE: follow $REPO/README.md to download model weights"
echo "          before running scripts/run/run_megasam.sh."
