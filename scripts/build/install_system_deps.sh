#!/usr/bin/env bash
# Install Ubuntu 22.04 system packages required by ORB-SLAM3 + Pangolin.
# Safe to re-run.
set -euo pipefail

PKGS=(
  build-essential cmake git pkg-config
  libeigen3-dev libopencv-dev libboost-all-dev libssl-dev
  libglew-dev libgl1-mesa-dev libegl1-mesa-dev libepoxy-dev
  libwayland-dev libxkbcommon-dev wayland-protocols
  python3-pip python3-venv python3-dev
  ffmpeg
)

echo "[install_system_deps] sudo apt update + install of:"
printf '  - %s\n' "${PKGS[@]}"
sudo apt update
sudo apt install -y "${PKGS[@]}"
echo "[install_system_deps] done."
