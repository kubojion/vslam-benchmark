# Setup

Tested on Ubuntu 22.04 with an NVIDIA GPU + CUDA 11.8.

## 1. System packages

```bash
sudo apt update && sudo apt install -y \
  build-essential cmake git pkg-config \
  libeigen3-dev libopencv-dev libboost-all-dev libssl-dev \
  libgl1-mesa-dev libglew-dev libwayland-dev libxkbcommon-dev wayland-protocols
```

## 2. Clone this workspace

```bash
git clone https://github.com/kubojion/vslam-benchmark.git
cd vslam-benchmark
```

## 3. Third-party SLAM sources

These are kept outside this repo. Clone the patched forks (and stock DROID-SLAM)
into the expected paths:

```bash
mkdir -p src third_party

# Patched ORB-SLAM3 fork (build portability + Settings.cc null-ptr fix)
git clone -b vslam-benchmark-patches \
  https://github.com/kubojion/ORB_SLAM3.git src/ORB_SLAM3

# Patched MAC-VO fork (GeneralStereo preprocess for 640x480 rectified)
git clone -b vslam-benchmark-patches \
  https://github.com/kubojion/MAC-VO.git src/MAC-VO

# Stock DROID-SLAM
git clone https://github.com/princeton-vl/DROID-SLAM.git src/DROID-SLAM

# Pangolin (required by ORB-SLAM3)
git clone https://github.com/stevenlovegrove/Pangolin.git third_party/Pangolin
```

## 4. Build Pangolin

```bash
cd third_party/Pangolin
cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build -j$(nproc)
sudo cmake --install build
cd ../..
```

## 5. Build ORB-SLAM3

```bash
cd src/ORB_SLAM3
chmod +x build.sh && ./build.sh
cd ../..
```

If the build dies on `ORBvoc.txt`, decompress it: `cd src/ORB_SLAM3/Vocabulary && tar -xf ORBvoc.txt.tar.gz`.

## 6. Conda environments

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

## 7. Smoke test

```bash
# Drop a dataset under datasets/<dataset>/<seq>/ (see docs/running_agorithms.md)
bash scripts/run/run_orbslam3.sh hortimulti strawberry02 1
```

Output should appear under `results/hortimulti/strawberry02/orbslam3/run1/`.
