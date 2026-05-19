#!/usr/bin/env bash
# Build and install Pangolin (system-wide). One-time.
set -euo pipefail
WS=$(cd "$(dirname "$0")/../.." && pwd)
cd "$WS/third_party/Pangolin"

# Use the bundled Pangolin installer if present (path relative to Pangolin src dir).
if [[ -x scripts/install_prerequisites.sh ]]; then
  echo "[pangolin] installing system prereqs via Pangolin script..."
  yes | ./scripts/install_prerequisites.sh recommended || true
fi

mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . -j"$(nproc)"
sudo cmake --install .
sudo ldconfig
echo "[pangolin] installed. Version: $(pkg-config --modversion pangolin || echo unknown)"
