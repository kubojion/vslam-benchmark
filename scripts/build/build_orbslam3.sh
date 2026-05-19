#!/usr/bin/env bash
# Build ORB-SLAM3 with patches needed for Ubuntu 22.04 / gcc-11 / OpenCV 4.5+.
# Safe to re-run; patches use idempotent sed/grep guards.
set -euo pipefail
WS=$(cd "$(dirname "$0")/../.." && pwd)
ORB="$WS/src/ORB_SLAM3"
cd "$ORB"

apply_patch() {
    local file=$1 marker=$2
    local insert=$3
    if grep -qF "$marker" "$file"; then return; fi
    echo "[patch] $file  (+ $marker)"
    sed -i "1i $insert" "$file"
}

echo "[orbslam3] applying Ubuntu 22.04 / gcc-11 / Pangolin-0.9 patches..."

# 0) Pangolin >= 0.9 uses sigslot/signal.hpp which requires C++14 (std::decay_t).
#    Patch CMakeLists.txt to use C++14 if not already done.
if grep -q "CMAKE_CXX_STANDARD 14" "$ORB/CMakeLists.txt"; then
    echo "[patch] CMakeLists.txt: C++14 already set, skipping."
else
    python3 - "$ORB/CMakeLists.txt" << 'PYEOF'
import re, sys
path = sys.argv[1]
content = open(path).read()
pattern = r"# Check C\+\+11.*?endif\(\)"
replacement = (
    "# C++14 required by Pangolin >= 0.9 (sigslot uses std::decay_t etc.)\n"
    "set(CMAKE_CXX_STANDARD 14)\n"
    "set(CMAKE_CXX_STANDARD_REQUIRED ON)\n"
    "add_definitions(-DCOMPILEDWITHC11)\n"
    "message(STATUS \"Using C++14 (Pangolin v0.9+ requires C++14).\")"
)
result = re.sub(pattern, replacement, content, flags=re.DOTALL)
if result == content:
    print("[patch] CMakeLists.txt: pattern not found, may already be patched.")
else:
    open(path, "w").write(result)
    print("[patch] CMakeLists.txt: replaced C++11 block with C++14.")
PYEOF
fi

# 1) Missing <unistd.h> for usleep
for f in include/System.h include/Tracking.h include/LoopClosing.h \
         include/LocalMapping.h include/Viewer.h \
         Examples/Monocular/mono_euroc.cc Examples/Stereo/stereo_euroc.cc \
         Examples/RGB-D/rgbd_tum.cc; do
    [[ -f "$f" ]] || continue
    apply_patch "$f" "<unistd.h>" "#include <unistd.h>"
done

# 2) Force C++14 in the bundled Sophus and g2o submodules to keep gcc-11 happy.
for d in Thirdparty/Sophus Thirdparty/g2o Thirdparty/DBoW2; do
    cml="$d/CMakeLists.txt"
    [[ -f "$cml" ]] || continue
    if ! grep -q "CMAKE_CXX_STANDARD 14" "$cml"; then
        echo "[patch] $cml  (CXX_STANDARD 14)"
        sed -i '1iset(CMAKE_CXX_STANDARD 14)\nset(CMAKE_CXX_STANDARD_REQUIRED ON)' "$cml"
    fi
done

# 3) Common Sophus / Tardos patch: replace .matrix() on SE3f with eigen()
#    Only applied if the symptom is detected.
if grep -rqs "SE3f::matrix" include/ src/ 2>/dev/null; then
    echo "[orbslam3] (manual) Sophus matrix() patch may be required, see docs/13."
fi

echo "[orbslam3] running build.sh..."
chmod +x build.sh
./build.sh 2>&1 | tee "$WS/logs/build_orbslam3.log"
echo "[orbslam3] done. Examples should be under $ORB/Examples/"
