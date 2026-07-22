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

# ---------------------------------------------------------------------------
# Pretrained checkpoints. MegaSaM is a multi-stage pipeline and needs three:
#   checkpoints/megasam_final.pth                    ships in the repo (20 MB)
#   Depth-Anything/checkpoints/depth_anything_vitl14.pth   HuggingFace (1.3 GB)
#   cvd_opt/raft-things.pth                          RAFT release (21 MB)
#
# Upstream points at a Google Drive folder for the RAFT weight, but gdown fails
# on it ("AttributeError: 'NoneType' object has no attribute 'groups'" -- Drive's
# current HTML). raft-things.pth originates from princeton-vl/RAFT, whose own
# download_models.sh pulls the same file from Dropbox, so fetch it there instead.
# ---------------------------------------------------------------------------
mkdir -p "$REPO/Depth-Anything/checkpoints" "$REPO/cvd_opt"

DA="$REPO/Depth-Anything/checkpoints/depth_anything_vitl14.pth"
if [[ ! -f "$DA" ]]; then
    echo "[megasam] downloading DepthAnything checkpoint (1.3 GB)..."
    wget -q --show-progress -O "$DA" \
      "https://huggingface.co/spaces/LiheYoung/Depth-Anything/resolve/main/checkpoints/depth_anything_vitl14.pth"
fi

RAFT="$REPO/cvd_opt/raft-things.pth"
if [[ ! -f "$RAFT" ]]; then
    echo "[megasam] downloading RAFT checkpoints (79 MB zip)..."
    TMPZ=$(mktemp -t raft_models_XXXXXX.zip)
    wget -q --show-progress -O "$TMPZ" "https://dl.dropboxusercontent.com/s/4j4z58wuv8o0mfz/models.zip"
    TMPD=$(mktemp -d)
    unzip -o -q "$TMPZ" -d "$TMPD"
    cp "$(find "$TMPD" -name raft-things.pth | head -1)" "$RAFT"
    rm -rf "$TMPZ" "$TMPD"
fi

for f in "$REPO/checkpoints/megasam_final.pth" "$DA" "$RAFT"; do
    [[ -f "$f" ]] || { echo "[megasam] ERROR: missing checkpoint $f" >&2; exit 1; }
done

echo "[megasam] env $ENV ready. Activate with: conda activate $ENV"
echo "[megasam] checkpoints present: megasam_final, depth_anything_vitl14, raft-things"
