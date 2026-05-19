# Setup

Tested on Ubuntu 22.04 with an NVIDIA GPU + CUDA 11.8.

## 1. System packages

```bash
sudo apt update && sudo apt install -y \
  build-essential cmake git pkg-config \
  libeigen3-dev libopencv-dev libboost-all-dev libssl-dev \
  libgl1-mesa-dev libglew-dev libwayland-dev libxkbcommon-dev wayland-protocols
```

## 2. Clone this workspace (with submodules)

The three SLAM source trees (`src/ORB_SLAM3`, `src/MAC-VO`, `src/DROID-SLAM`)
and Pangolin (`third_party/Pangolin`) are tracked as git submodules. Always
clone with `--recurse-submodules`, or run the explicit init line below:

```bash
git clone --recurse-submodules https://github.com/kubojion/vslam-benchmark.git
cd vslam-benchmark

# If you forgot --recurse-submodules:
git submodule update --init --recursive
```

This pulls:

| Path | Upstream | Branch / pin |
|---|---|---|
| `src/ORB_SLAM3`      | `kubojion/ORB_SLAM3` (fork)   | `vslam-benchmark-patches` |
| `src/MAC-VO`         | `kubojion/MAC-VO` (fork)      | `vslam-benchmark-patches` |
| `src/DROID-SLAM`     | `princeton-vl/DROID-SLAM`     | pinned commit             |
| `third_party/Pangolin` | `stevenlovegrove/Pangolin`  | pinned commit             |

## 3. Build Pangolin

```bash
cd third_party/Pangolin
cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build -j$(nproc)
sudo cmake --install build
cd ../..
```

## 4. Build ORB-SLAM3

```bash
cd src/ORB_SLAM3
chmod +x build.sh && ./build.sh
cd ../..
```

If the build dies on `ORBvoc.txt`, decompress it: `cd src/ORB_SLAM3/Vocabulary && tar -xf ORBvoc.txt.tar.gz`.

## 5. Conda environments

```bash
# DROID-SLAM
conda env create -f src/DROID-SLAM/environment.yaml   # creates `droidenv`

# MAC-VO + evaluation toolkit
conda create -n macvo python=3.10 -y
conda activate macvo
pip install -r src/MAC-VO/requirements.txt
pip install evo  # for ATE/RPE metrics
```

MAC-VO model weights:

```bash
cd src/MAC-VO/Model
# download MACVO_FrontendCov.pth and MACVO_posenet.pkl per upstream README
cd ../../..
```

## 6. Smoke test

```bash
# Drop a dataset under datasets/<dataset>/<seq>/ (see docs/running_agorithms.md)
bash scripts/run/run_orbslam3.sh hortimulti strawberry02 1
```

Output should appear under `results/hortimulti/strawberry02/orbslam3/run1/`.
