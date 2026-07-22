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
git submodule update --init --recursive src/mega-sam
bash scripts/build/setup_megasam_env.sh
```

Creates conda env `megasam` (python 3.10, torch 2.0.1+cu118) and downloads all
three checkpoints (`megasam_final.pth` ships in the repo; DepthAnything and RAFT
are fetched). The script fails loudly if any is missing.

MegaSaM is a **multi-stage pipeline**, not a single binary. `run_megasam.sh`
drives three of upstream's four stages:

| Stage | Script | Produces |
|---|---|---|
| 1a | `Depth-Anything/run_videos.py` | relative mono-depth |
| 1b | `UniDepth/scripts/demo_mega-sam.py` | metric depth prior |
| 2 | `camera_tracking_scripts/test_demo.py` | `reconstructions/<scene>/poses.npy` |

Stage 3 (`cvd_opt`) refines depth only and does not change the camera
trajectory, so it is skipped.

Three extra install steps the upstream README does not mention, all of which the
runner needs:

```bash
# a) vendored CUDA extensions (lietorch + droid_backends) are never built by
#    upstream's setup. They need an nvcc matching torch's CUDA build -- the
#    system nvcc is usually older, and PyTorch hard-refuses on a mismatch.
conda install -y -n megasam -c nvidia cuda-nvcc=11.8 cuda-cudart-dev=11.8 cuda-cccl=11.8
conda run -n megasam pip install "setuptools<81"   # base/setup.py needs pkg_resources
cd src/mega-sam/base && conda run -n megasam bash -c \
  'CUDA_HOME=$CONDA_PREFIX PATH=$CONDA_PREFIX/bin:$PATH TORCH_CUDA_ARCH_LIST=8.9 python setup.py install'
# NB: `pip install -e .` does NOT work here -- base/setup.py has two setup()
# calls (one per extension) and pip only processes the first.

# b) runtime deps missing from the env
conda run -n megasam pip install torch_scatter -f https://data.pyg.org/whl/torch-2.0.1+cu118.html
conda run -n megasam pip install huggingface_hub timm wandb einops h5py xformers==0.0.22 opencv-python==4.10.0.84

# c) torch 2.0.1 predates numpy 2 -- otherwise every stage dies with
#    "RuntimeError: Numpy is not available"
conda run -n megasam pip install "numpy<2"
```

UniDepth downloads `unidepth-v2-vitl14` from HuggingFace on first run (several GB).

**Grayscale note:** UniDepth loads frames with `np.array(Image.open(p))[..., :3]`,
which silently mis-slices grayscale images (PIL mode `L` gives a 2-D array, so
the slice takes 3 *columns*, not 3 channels). Every dataset here is grayscale, so
`run_megasam.sh` materialises a temporary RGB copy for stage 1b. Stages 1a and 2
use `cv2.imread` and are unaffected.

## 10. MASt3R-SLAM (optional, monocular + retrieval-based LC)

```bash
git submodule update --init --recursive src/MASt3R-SLAM
bash scripts/build/setup_mast3r_slam_env.sh
```

Creates conda env `mast3r_slam` (python 3.11, torch 2.5.1+cu121). Checkpoints
must still be fetched manually (~2.9 GB):

```bash
cd src/MASt3R-SLAM && mkdir -p checkpoints
B=https://download.europe.naverlabs.com/ComputerVision/MASt3R
wget -P checkpoints/ $B/MASt3R_ViTLarge_BaseDecoder_512_catmlpdpt_metric.pth
wget -P checkpoints/ $B/MASt3R_ViTLarge_BaseDecoder_512_catmlpdpt_metric_retrieval_trainingfree.pth
wget -P checkpoints/ $B/MASt3R_ViTLarge_BaseDecoder_512_catmlpdpt_metric_retrieval_codebook.pkl
```

The setup script ends with `pip install -e . || true`, which **swallows build
failures** -- it prints "env ready" even when the package did not install. Verify
with `conda run -n mast3r_slam python -c "import mast3r_slam"` before trusting it.
If that fails, the usual causes are:

```bash
# CUDA mismatch (system nvcc vs torch's cu121) breaks the CUDA extensions
conda install -y -n mast3r_slam -c nvidia cuda-nvcc=12.1 cuda-cudart-dev=12.1 cuda-cccl=12.1
cd src/MASt3R-SLAM && conda run -n mast3r_slam bash -c \
  'CUDA_HOME=$CONDA_PREFIX PATH=$CONDA_PREFIX/bin:$PATH pip install -e . --no-build-isolation'

# undeclared runtime deps; opencv 5 forces numpy>=2 and breaks the pinned 1.26.4
conda run -n mast3r_slam pip install tqdm "opencv-python==4.10.0.84" "numpy==1.26.4" \
    moderngl moderngl-window PyGLM trimesh glfw imgui
# vendored packages that are not pip-installable
conda run -n mast3r_slam pip install -e src/MASt3R-SLAM/thirdparty/mast3r --no-build-isolation
conda run -n mast3r_slam pip install -e src/MASt3R-SLAM/thirdparty/in3d --no-deps --no-build-isolation
# dust3r is a plain package dir; expose it on the path
echo "$PWD/src/MASt3R-SLAM/thirdparty/mast3r/dust3r" \
  > "$(conda run -n mast3r_slam python -c 'import site;print(site.getsitepackages()[0])')/dust3r_vendored.pth"
```

> **Known limitation:** MASt3R-SLAM does not fit in 12 GB of VRAM on sequences of
> this length. It keeps every keyframe on-GPU and offers no way to bound that:
> `local_opt.window_size` is read but never applied upstream, and
> `dataset.img_downsample` breaks the model (the checkpoint has a fixed 512-wide
> input). `dataset.subsample: 2` was tried on rosariov2 and still OOM'd. It needs
> a larger card.

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

## 13. OKVIS2-X (native, no ROS)

OKVIS2-X is the successor to OKVIS2 (tightly-coupled GNSS, LiDAR, dense depth
submapping). Only the sparse estimator is built here. It is wired in completely
independently of OKVIS2 - separate source tree, configs, runner and results -
so the two can be compared head-to-head in the same CSV.

`src/okvis2x` is a git submodule, so a `--recurse-submodules` clone already has
the source. Then:

```bash
# 1. system packages (Ubuntu 22.04)
sudo apt install cmake libgoogle-glog-dev libeigen3-dev libsuitesparse-dev \
                 libboost-dev libboost-filesystem-dev libopencv-dev \
                 libpcl-dev libgeographic-dev
# Ubuntu 24.04: libgeographic-dev -> libgeographiclib-dev
# Ceres needs BLAS/LAPACK; libopenblas-dev + liblapack-dev is enough
# (upstream suggests libatlas-base-dev, but any implementation works).

# 2. build (~15 min: bundled Ceres, OpenGV, BRISK, DBoW2)
bash scripts/build/build_okvis2x.sh
# -> src/okvis2x/build/okvis_app_synchronous
```

Four upstream quirks the build script handles for you, worth knowing if you
ever build by hand:

* OKVIS2-X's own `supereight2` submodule is declared with an **SSH** URL in its
  `.gitmodules`, so a recursive clone fails without a GitHub SSH key even though
  the repo is public. The script rewrites it to HTTPS.
* If an earlier clone aborted partway, some nested submodules are left
  registered-but-empty and a plain `git submodule update --init --recursive`
  will **not** repair them (cmake then fails with "doesn't exist. Did you forget
  to update the git submodules?"). The script passes `--force` and then verifies
  each one.
* The bundled Ceres defaults to `USE_CUDA=ON`. With a CUDA toolkit present it
  tries to compile its CUDA kernels with nvcc against GCC 11 headers and fails
  (`parameter packs not expanded with '...'`). The estimator is CPU-only, so the
  script passes `-DUSE_CUDA=OFF`.
* `okvis_app_synchronous` loads its DBoW2 vocabulary from its **own directory**
  and exits if it is missing; nothing in upstream CMake puts it there. The script
  copies `resources/small_voc.yml.gz` next to the binary.

The build is estimator-only (`-DBUILD_ROS2=OFF -DHAVE_LIBREALSENSE=OFF
-DUSE_NN=OFF -DUSE_CUDA=OFF`); the dense depth / LiDAR submapping apps
(`okvis2x_app_*`) are not built, as the benchmark has no metrics for their
submap meshes.

Verify with the 200-frame smoke sequence (~15 s):

```bash
bash scripts/run/run_okvis2x.sh euroc smoke_mh_01_easy_200 9001 vio
```

## 14. GNSS-VIO algorithms

The `gnss-vio` run-type adds four GPS-aware algorithms. Each writes to
`results-gnss-vio/` and `benchmark-gnss-vio.csv`.

| Algorithm | Setup | ROS |
|---|---|---|
| CIFASIS GNSS-SI | Docker image, builds Pangolin + ORB-SLAM3 + GNSS-SI inside | ROS 1 Noetic |
| RTAB-Map | `sudo apt install ros-humble-rtabmap-ros` | ROS 2 Humble |
| VINS-Fusion | Docker image, builds Ceres + VINS-Fusion inside | ROS 1 Noetic |
| OKVIS2-X | native cmake build, see §13 | none |

All four consume the same EuRoC-format data layout plus a `gps.csv` file
(header `t,lat,lon,alt[,cov_xx,cov_yy,cov_zz,status]`, timestamps in seconds).

### 13a. CIFASIS GNSS-SI (Cremona et al., JFR 2023)

```bash
git clone https://github.com/CIFASIS/gnss-stereo-inertial-fusion src/cifasis_gnss_si
bash scripts/setup/setup_cifasis_gnss_si_docker.sh
```

This builds image `vslam_cifasis_gnss_si:noetic` and creates container
`cifasis_gnss_si`. The image runs upstream's `build.sh` and `build_ros.sh`
internally; first build takes ~30-60 min (Pangolin + DBoW2 + g2o + ORB-SLAM3).

Configs: `configs/cifasis_gnss_si/<dataset>_<seq>.yaml` (Rosario seq1/seq5
configs are copied from upstream's Examples directory). The `t_b_g` antenna
offset is dataset-specific and pre-set per upstream's published values.

### 13b. RTAB-Map (introlab)

```bash
sudo apt install ros-humble-rtabmap-ros
```

No Docker needed - native ROS 2 Humble. The runner sources
`/opt/ros/humble/setup.bash` and launches `rtabmap_launch/rtabmap.launch.py`
with our YAML overlay. Trajectories are extracted from the rtabmap database
via `rtabmap-export --poses --poses_format 11`.

Configs: `configs/rtabmap_gps/<dataset>.yaml`.

### 13c. VINS-Fusion (HKUST)

```bash
git clone https://github.com/HKUST-Aerial-Robotics/VINS-Fusion src/VINS-Fusion
bash scripts/setup/setup_vins_fusion_docker.sh
```

This builds image `vslam_vins_fusion:noetic` (Ceres 2.1 + catkin_make).
First build takes ~20-40 min. The runner starts `vins_node`,
`global_fusion_node`, and a small Python recorder that writes
`/globalEstimator/global_odometry` to a TUM trajectory file.

Configs: `configs/vins_fusion/<dataset>_<seq>.yaml` plus
`<dataset>_cam{0,1}.yaml` per-camera intrinsics.

### 13d. GPS prerequisites

- Rosario v2: `gps.csv` is generated by the existing `_rosario_extract.py`
  (default topic `/reach_1/fix`).
- HortiMulti: `gps.csv` is extracted by the updated `_hortimulti_extract.py`
  (default topic `/antobot_gps`):

  ```bash
  python3 scripts/data/_hortimulti_extract.py \
      --bag /path/to/Strawberry-02.bag \
      --gt_csv unused.csv \
      --out datasets/hortimulti/strawberry02 \
      --gps-only
  ```

  Use `--gps-only` to skip image/IMU re-extraction when those have already
  been done. The output `gps.csv` matches the Rosario layout.

The shared data player (`scripts/run/gnss_data_player.py` for ROS 1,
`gnss_data_player_ros2.py` for ROS 2) reads `gps.csv` and republishes as
`sensor_msgs/NavSatFix` at original timestamps. Default covariance overrides
are `0.04 m^2` horizontal for PPK-quality fixes and `1.0 m^2` for
conventional GPS; see the `--gps-cov-xy` / `--gps-cov-z` flags.
