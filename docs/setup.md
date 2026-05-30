# Setup

> Fully revised: 2026-05-30 22:41 - Added Voxel-SVIO Docker section (§12).

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

## 6. Install Basalt (stereo VO, binary)

Basalt is distributed as a prebuilt binary for Ubuntu 22.04 (x86-64). No build step required.

```bash
curl -LsSf https://gitlab.com/VladyslavUsenko/basalt/-/raw/master/scripts/install.sh | sh
```

This installs `basalt_vio` to `~/.local/bin/` and default configs to `~/.local/etc/basalt/`.
The installer also writes `~/.basalt/env`, which `run_basalt.sh` sources automatically to add
`~/.local/bin` to `PATH` for the duration of the run.

No conda environment is needed to run Basalt itself. Evaluation uses the existing `macvo` env.

## 7. AirSLAM (Docker)

AirSLAM requires ROS Noetic, TensorRT 8.6.1.6, and CUDA 12.1 - all bundled in the official
Docker image. This keeps AirSLAM completely isolated from the ROS 2 Humble installation.

### 7a. Install Docker Engine + nvidia-container-toolkit

```bash
# Docker Engine
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu jammy stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER   # log out and back in to activate

# nvidia-container-toolkit (GPU pass-through)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit.gpg] https://#g' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### 7b. Clone AirSLAM source

```bash
git clone https://github.com/sair-lab/AirSLAM.git src/airslam
```

### 7c. Pull the Docker image and create the container

The image is ~17 GB compressed; allow 10-30 min depending on connection speed.

```bash
docker pull xukuanhit/air_slam:v4

docker run -d \
  --runtime nvidia --gpus all \
  --volume "$PWD/src/airslam:/root/catkin_ws/src/air_slam" \
  --volume "$PWD/datasets:/datasets:ro" \
  --volume "$PWD/results:/results" \
  --volume "$PWD/configs:/benchmark_configs:ro" \
  --name air_slam \
  xukuanhit/air_slam:v4 /bin/bash -c "tail -f /dev/null"
```

### 7d. Build AirSLAM inside the container

```bash
docker exec air_slam bash -c "
  source /opt/ros/noetic/setup.bash &&
  cd /root/catkin_ws &&
  catkin_make -DCMAKE_BUILD_TYPE=Release
"
```

Build takes ~5-10 min. On success you will see `[100%] Built target visual_odometry`.

### 7e. TensorRT engine compilation (first run per dataset)

On the first run for each dataset, TensorRT compiles a `.engine` file from the ONNX
model for that image resolution. This takes ~5-10 min and is cached afterwards.
Separate engine files are used per dataset to avoid cache conflicts:

| Dataset | Resolution | Engine file |
|---|---|---|
| hortimulti | 640x480 | `superpoint_lightglue_hortimulti.engine` |
| rosariov2 | 1280x720 | `superpoint_lightglue_rosariov2.engine` |

Engine files are stored in `src/airslam/output/` (inside the container at
`/root/catkin_ws/src/air_slam/output/` - persisted via the volume mount).

### 7f. Container lifecycle

The container `air_slam` is kept running as a long-lived daemon (sleeping with
`tail -f /dev/null`). `run_airslam.sh` starts it automatically if it is stopped.
To stop/remove it manually:

```bash
docker stop air_slam
docker rm air_slam
```

## 8. Smoke test

```bash
# Drop a dataset under datasets/<dataset>/<seq>/ (see docs/running_algorithms.md)
bash scripts/run/run_orbslam3.sh hortimulti strawberry02 1
```

Output should appear under `results-vo/hortimulti/strawberry02/orbslam3/run1/`.

## 9. MegaSaM (optional, monocular)

```bash
bash scripts/build/setup_megasam_env.sh
```

Creates conda env `megasam` (python 3.10, torch 2.0.1+cu118) and clones
`https://github.com/mega-sam/mega-sam` into `src/mega-sam/`. Model weights
must be downloaded manually per the upstream README before the runner will
produce output.

## 10. MASt3R-SLAM (optional, monocular + retrieval-based LC)

```bash
bash scripts/build/setup_mast3r_slam_env.sh
```

Creates conda env `mast3r_slam` (python 3.11, torch 2.5.1+cu121) and clones
`https://github.com/rmurai0610/MASt3R-SLAM` (with submodules) into
`src/MASt3R-SLAM/`. MASt3R checkpoints must be downloaded manually per the
upstream README before the runner will produce output.

## 11. OpenVINS (Docker, ROS 2 Humble)

OpenVINS runs in a Docker container to avoid a host ROS 2 install.

### 11a. Build the image (one-time)

```bash
docker build -t openvins:humble -f src/open_vins/Dockerfile.benchmark src/open_vins
```

Build takes ~10 min on first run (downloads ros2-humble base image + compiles
all ov_* packages). Subsequent builds are cached.

### 11b. Verify

```bash
docker run --rm openvins:humble /bin/bash -c \
    "source /opt/ros/humble/setup.bash && ros2 pkg list | grep ov_msckf"
```

Expect `ov_msckf` in the output.

### 11c. Required dataset layout

Each sequence must have `mav0/imu0/data.csv` in TUM-format
(`timestamp_ns, wx, wy, wz, ax, ay, az`). RosarioV2 and EuRoC-MAV already
have this. HortiMulti does NOT yet - VIO runs on HortiMulti are blocked until
`scripts/data/_hortimulti_extract.py` is updated to export `/ms/imu/data`.

## 12. Voxel-SVIO (Docker, ROS 1 Noetic)

Voxel-SVIO is a stereo MSCKF VIO with a voxel-map landmark layer (RA-L 2025).
It is CPU-only and runs in a ROS 1 Noetic container, fully isolated from the
host ROS install.

### 12a. Clone the source

```bash
git clone https://github.com/ZikangYuan/voxel_svio.git src/voxel_svio
```

### 12b. Build the image and container

```bash
bash scripts/setup/setup_voxel_svio_docker.sh
```

This script:

1. Builds image `vslam_voxel_svio:noetic` from
   `scripts/setup/voxel_svio.Dockerfile` (ROS Noetic + Ceres + glog/gflags).
2. Creates container `voxel_svio` with bind mounts for
   `src/voxel_svio`, `datasets/` (read-only), `results-vio/`,
   `configs/voxel_svio/` and `scripts/`.
3. Runs `catkin_make -DCMAKE_BUILD_TYPE=Release` inside the container.

First build takes ~5-10 min. Subsequent setup re-runs reuse the image.

### 12c. Verify

```bash
docker exec voxel_svio /bin/bash -c \
    "source /opt/ros/noetic/setup.bash && \
     source /root/catkin_ws/devel/setup.bash && \
     rosrun voxel_svio --help 2>/dev/null; rospack find voxel_svio"
```

Expect `/root/catkin_ws/src/voxel_svio` in the output.

### 12d. Required dataset layout

EuRoC-style: `mav0/{cam0,cam1}/data/*.png`, `mav0/{cam0,cam1}/data.csv`,
`mav0/imu0/data.csv`. All three benchmarks (rosariov2, hortimulti, EuRoC-MAV)
are already in this layout. The bundled ROS 1 data player
(`scripts/run/voxel_svio_data_player.py`) reads this directly and publishes
on `/cam0/image_raw`, `/cam1/image_raw`, `/imu0`.
