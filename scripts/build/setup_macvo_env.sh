#!/usr/bin/env bash
# Create the conda environment 'macvo' and download MAC-VO pretrained models.
set -eo pipefail
WS=$(cd "$(dirname "$0")/../.." && pwd)
ENV=macvo
set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"

if ! conda env list | awk '{print $1}' | grep -qx "$ENV"; then
    echo "[macvo] creating env..."
    conda create -y -n "$ENV" python=3.10
fi
conda activate "$ENV"
set -u

pip install --upgrade pip wheel

# Torch first; xformers==0.0.27.post2 needs torch 2.4.x cu121.
pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 \
    --index-url https://download.pytorch.org/whl/cu121

cd "$WS/src/MAC-VO"
pip install -r requirements.txt

# Extra packages not listed in requirements.txt but required at runtime
pip install jaxtyping typeguard

mkdir -p Model
[[ -f Model/MACVO_FrontendCov.pth ]] || \
    wget -O Model/MACVO_FrontendCov.pth \
        https://github.com/MAC-VO/MAC-VO/releases/download/model/MACVO_FrontendCov.pth
[[ -f Model/MACVO_posenet.pkl ]] || \
    wget -O Model/MACVO_posenet.pkl \
        https://github.com/MAC-VO/MAC-VO/releases/download/model/MACVO_posenet.pkl

echo "[macvo] OK. Activate with: conda activate $ENV"
