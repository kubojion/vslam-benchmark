#!/usr/bin/env bash
# Snapshot environment for thesis reproducibility appendix.
set -e
WS=$(cd "$(dirname "$0")/../.." && pwd)
OUT="$WS/results-vo/env_snapshot"
mkdir -p "$OUT"

uname -a > "$OUT/uname.txt"
lsb_release -a > "$OUT/distro.txt" 2>/dev/null || true
nvidia-smi > "$OUT/nvidia-smi.txt" 2>&1 || true
gcc --version > "$OUT/gcc.txt"
cmake --version > "$OUT/cmake.txt"
pkg-config --modversion opencv4 > "$OUT/opencv.txt" 2>/dev/null || true
pkg-config --modversion pangolin > "$OUT/pangolin.txt" 2>/dev/null || true

for d in src/ORB_SLAM3 src/DROID-SLAM src/MAC-VO third_party/Pangolin; do
    if [[ -d "$WS/$d/.git" ]]; then
        echo "$d $(git -C "$WS/$d" rev-parse HEAD)" >> "$OUT/repo_hashes.txt"
    fi
done

source "$HOME/miniconda3/etc/profile.d/conda.sh"
for env in droidenv macvo; do
    if conda env list | awk '{print $1}' | grep -qx "$env"; then
        conda env export -n "$env" > "$OUT/env_${env}.yaml"
    fi
done
echo "[snapshot] -> $OUT"
