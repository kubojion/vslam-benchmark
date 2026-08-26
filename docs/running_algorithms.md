# Running the algorithms

> Fully revised: 2026-05-30 22:41 - Added Voxel-SVIO (RA-L 2025) Docker setup, configs, and per-algo notes.
> Updated: 05-31 - rosariov2 seq5 re-run with high-quality PPK GPS (GPS-quality study in PROGRESS.md); seq5 gps.csv is now PPK (conventional preserved as gps_conventional.csv). Fixed stale hortimulti IMU note (IMU extracted); added GNSS-VIO run examples.

The framework expects a sequence under

```
datasets/<dataset>/<seq>/
├── cam0/        # rectified left images  (PNG/JPG, sorted by filename)
├── cam1/        # rectified right images
├── times.txt    # one line per frame, nanosecond timestamps
└── gt_tum.txt   # ground truth in TUM format (timestamp tx ty tz qx qy qz qw, seconds)
```

`scripts/data/convert_*.sh` produce this layout from raw rosbags (Rosario v2, HortiMulti).

Worked example: a new **Rosario sequence 2**.

## 1. Prepare the dataset

```bash
# put the .bag and *_pgt.bag inside datasets/rosariov2/sequence2/
bash scripts/data/convert_rosario_to_tum.sh datasets/rosariov2/sequence2
```

This populates `cam0/`, `cam1/`, `times.txt`, `gt_tum.txt`.

## 2. Add config files

* ORB-SLAM3 - reuse the dataset-level file `configs/orbslam3/rosariov2_stereo.yaml` (same calibration).
* DROID-SLAM - reuse `configs/droidslam/rosariov2.txt`.
* MAC-VO - add a new per-sequence file `configs/macvo/rosariov2_sequence2.yaml` (copy `rosariov2_sequence1.yaml` and change `name:` + `root:` - keep the `__WS__` placeholder).
* Basalt - reuse the dataset-level calibration `configs/basalt/rosariov2_calib.json` and the shared `configs/basalt/vo_config.json` (no per-sequence file needed).

## 3. Run each algorithm three times

`run_benchmark.sh` takes an optional 5th positional `run_type`:

```
bash scripts/run/run_benchmark.sh <dataset> <seq> <algo> [N=3] [run_type=vo]
```

* `vo`     - no IMU, no LC, output -> `results/vo/`        (`benchmark-vo.csv`)
* `vo-lc`  - no IMU, LC on, output -> `results/vo-lc/`     (`benchmark-vo-lc.csv`)
* `vio`    - IMU on, no LC, output -> `results/vio/`       (`benchmark-vio.csv`)
* `vio-lc` - IMU on, LC on, output -> `results/vio-lc/`    (`benchmark-vio-lc.csv`)

```bash
# Default (vo) - all five with the standard 3-run + evaluation pipeline:
bash scripts/run/run_benchmark.sh rosariov2 sequence2 orbslam3 3
bash scripts/run/run_benchmark.sh rosariov2 sequence2 droidslam 3
bash scripts/run/run_benchmark.sh rosariov2 sequence2 macvo 3
bash scripts/run/run_benchmark.sh rosariov2 sequence2 basalt 3
bash scripts/run/run_benchmark.sh rosariov2 sequence2 airslam 3

# Visual-inertial run of Basalt or AirSLAM:
bash scripts/run/run_benchmark.sh rosariov2 sequence2 basalt  3 vio
bash scripts/run/run_benchmark.sh rosariov2 sequence2 airslam 3 vio

# Full V-SLAM (IMU + LC) with AirSLAM:
bash scripts/run/run_benchmark.sh rosariov2 sequence2 airslam 3 vio-lc

# Monocular visual SLAM with loop closure:
bash scripts/run/run_benchmark.sh rosariov2 sequence2 dpvo 1 vo-lc

# Monocular algorithms (MegaSaM: 3-stage pipeline; MASt3R-SLAM: needs >12 GB VRAM):
bash scripts/run/run_benchmark.sh euroc_mav MH_01_easy megasam     1 vo
bash scripts/run/run_benchmark.sh euroc_mav MH_01_easy mast3r_slam 1 vo-lc  # LC enabled
```

Direct single runs forward run_type as the 4th positional:

```bash
bash scripts/run/run_orbslam3.sh    rosariov2 sequence2 1 vo
bash scripts/run/run_okvis2.sh      rosariov2 sequence2 1 vio
bash scripts/run/run_okvis2x.sh     rosariov2 sequence2 1 vio
bash scripts/run/run_openvins.sh    rosariov2 sequence2 1 vio
bash scripts/run/run_droidslam.sh   rosariov2 sequence2 1 vo
bash scripts/run/run_macvo.sh       rosariov2 sequence2 1 vo
bash scripts/run/run_basalt.sh      rosariov2 sequence2 1 vio
bash scripts/run/run_airslam.sh     rosariov2 sequence2 1 vio-lc
bash scripts/run/run_dpvo.sh        rosariov2 sequence2 1 vo-lc
bash scripts/run/run_megasam.sh     rosariov2 sequence2 1 vo
bash scripts/run/run_mast3r_slam.sh rosariov2 sequence2 1 vo-lc
```

Per-run output: `<RESULTS_ROOT>/<dataset>/<seq>/<algo>/run<N>/{trajectory.txt, run_log.txt, resources.csv}`
where `<RESULTS_ROOT>` is `results/<run-type>/`. A direct runner refuses a
nonempty run directory; use `run_benchmark.sh` to replace an existing algorithm
cell safely and create its `COMPLETE` markers.

### Per-algorithm run-type support

| Algorithm   | `vo` | `vo-lc` | `vio` | `vio-lc` | Notes |
|-------------|------|---------|-------|----------|-------|
| ORB-SLAM3   | yes (needs LC-off build, see PROGRESS.md) | yes (stereo + LC) | yes (stereo-inertial) | yes (stereo-inertial + LC) | `vo-lc` uses `configs/orbslam3/<dataset>_stereo_lc.yaml` |
| OKVIS2      | yes | yes (experimental) | yes | yes | `vo-lc` sets `imu_parameters.use: false` + `do_loop_closures: true`; dataset reader still requires `mav0/imu0/data.csv` |
| OKVIS2-X    | yes (best-effort) | yes (experimental) | yes | yes | also supports `gnss-vio`; `mav0/imu0/data.csv` is required for **every** run type, including `vo` / `vo-lc` |
| DPVO / DPV-SLAM | yes | yes | no | no | monocular; `vo-lc` enables DPV-SLAM loop closure |
| OpenVINS    | no (MSCKF requires IMU) | no | yes | no (no built-in LC) | Runs inside `openvins:humble` Docker image; datasets need `mav0/imu0/data.csv` |
| Voxel-SVIO  | no (MSCKF requires IMU) | no | yes | no (no built-in LC) | Runs inside `vslam_voxel_svio:noetic` Docker image (ROS 1 Noetic, CPU-only); datasets need `mav0/imu0/data.csv` |
| AirSLAM     | yes | yes | yes | yes | `vo-lc` runs visual odometry with `use_imu: 0`, then map_refinement; VIO/VIO-LC require `_camera_vio.yaml` + `mav0/imu0/data.csv` |
| Basalt      | yes (`--use-imu false`) | no | yes (`--use-imu true`) | no (Basalt has no LC) | |
| MAC-VO      | yes | no | no (vision-only) | no (vision-only) | |
| DROID-SLAM  | yes (dropped; results kept) | no | no | no | |
| MegaSaM     | yes | no | no | no | monocular only; 3-stage pipeline, see note below |
| MASt3R-SLAM | yes (retrieval.k=0) | yes (retrieval.k=3) | no | no | monocular only; **needs >12 GB VRAM**, see note below |


## Notes per algorithm

* **ORB-SLAM3** needs the executable `stereo_euroc` from `src/ORB_SLAM3/Examples/Stereo/`. Re-run `./build.sh` if it's missing.
* **OKVIS2** uses the binary `src/okvis2/build/okvis_app_synchronous`. Config files: `configs/okvis2/<dataset>_<seq>_<vo|vo_lc|vio|vio_lc>.yaml` (per-sequence, per-mode). Run type is controlled by the `--run-type` flag passed by `run_okvis2.sh`. Configs exist for rosariov2 (seq1, seq5), EuRoC (MH_01/03/05), HortiMulti (strawberry02/03), and zed2i. **IMU noise params must use OKVIS2-compatible values** - raw Allan-variance numbers from sensor calibration are typically 12-840x too tight for OKVIS2's MAP estimator and cause scale collapse. Use the D435i reference values in the rosariov2 configs as a starting point. See PROGRESS.md Phase 4.6 for the full diagnosis and corrected params.
* **OKVIS2-X** uses the binary `src/okvis2x/build/okvis_app_synchronous`, built by `bash scripts/build/build_okvis2x.sh` (see [setup.md](setup.md) §13). It is wired in **completely independently of OKVIS2** - separate source tree, configs, runner and results dir - so the two can be compared head-to-head in the same CSV. Config files: `configs/okvis2x/<dataset>_<seq>_<vo|vo_lc|vio|vio_lc|gnss_vio>.yaml`. Things worth knowing:
  * The app signature is `okvis_app_synchronous <config.yaml> <dataset-folder> <output-dir>`. The dataset folder is `mav0/` (the directory holding `cam0/`, `imu0/`, `gps0/`) - **not** the sequence root. Unlike OKVIS2 it writes straight to the output dir, so nothing lands in `datasets/`. (The upstream README documents a 4-argument form with a second `se2-config`; that applies to the `okvis2x_app_*` mapping apps, not this one.)
  * `mav0/imu0/data.csv` is opened unconditionally by the dataset reader, so it is required even for `vo` / `vo-lc` (where `imu_parameters.use: false`). Generate it with `python3 scripts/data/imu_to_euroc.py <seq_dir>`.
  * The reader takes its image list from `mav0/cam{0,1}/data.csv` and aborts with `no images found for camera N` if absent - it does **not** fall back to listing `data/`. `run_okvis2x.sh` auto-generates both manifests on first use, as `run_basalt.sh` does.
  * **IMU noise params must use OKVIS2-compatible values** - the shipped configs carry the corrected D435i-reference values; see PROGRESS.md Phase 4.6. `vo` / `vo-lc` are best-effort: the front-end is not designed for IMU-less stereo.
  * For `vo-lc` / `vio-lc` the runner takes the post-BA loop-closed trajectory (`okvis2-slam-final-ba_trajectory.csv`); for the other run types it takes the causal estimate. All raw CSVs are kept in the run dir.
  * OKVIS2-X does not log *accepted* visual loop closures, so `loop_closures` stays empty for `vio-lc` runs. That is a logging limitation, not a sign that LC is off.
  * **Parameter sweeps**: set `OKVIS2X_CONFIG=<path>` to override the run-type -> config mapping, and give the run its own `run_id` so it lands in a separate `run<N>/`:
    ```bash
    OKVIS2X_CONFIG=configs/okvis2x/sweeps/my_variant.yaml \
      bash scripts/run/run_okvis2x.sh rosariov2 sequence1 9002 vio
    ```
    The runner reads `do_loop_closures` / `do_extrinsics` back out of whichever config it used to derive the app's output filenames, so an overridden config cannot desync them.
* **DROID-SLAM** runs in the `droidenv` conda env. The key VRAM-tuning parameter is `--filter_thresh`: the minimum optical-flow confidence required to keep a frame in the bundle adjustment window. Lower values process more frames but consume more VRAM. The default in `run_droidslam.sh` is `--filter_thresh 6.0`, which was empirically the lowest value that fits in VRAM on long sequences (Rosario, HortiMulti) without OOM. `--stride` defaults to 1 (all frames). The initial Rosario seq1 benchmark used `stride=2` (50% of frames); the final 3-run benchmark used `stride=1 --filter_thresh 6.0`. ATE barely changed between the two (45.37 vs 45.00 m), confirming the failure is domain-mismatch, not frame density.
* **MegaSaM** runs in the `megasam` conda env and is a **multi-stage pipeline**, not a single binary. `run_megasam.sh` drives three of upstream's four stages: Depth-Anything (relative mono-depth) -> UniDepth (metric depth prior) -> camera tracking. Upstream's 4th stage (`cvd_opt`) only refines depth and does not change the camera trajectory, so it is skipped. Things worth knowing:
  * Upstream ships no single entrypoint - the documented workflow is three shell scripts with hard-coded paths (`tools/evaluate_demo.sh` etc.). The runner reproduces them with our dataset paths and a per-run scene name, so concurrent/repeat runs do not overwrite each other's intermediates.
  * The trajectory comes from `reconstructions/<scene>/poses.npy`, which holds lietorch SE3 7-vectors for **world->camera**. The runner applies `SE3(...).inv()` to get camera->world before writing TUM.
  * **Grayscale datasets need a workaround.** UniDepth loads frames as `np.array(Image.open(p))[..., :3]`; for a grayscale PNG (PIL mode `L`) that is a 2-D array, so the slice takes 3 *columns* rather than 3 channels and the next `.permute(2,0,1)` fails. Every dataset here is grayscale, so the runner materialises a temporary RGB copy for that stage only. Stages 1a/2 use `cv2.imread` and are unaffected.
  * UniDepth pulls `unidepth-v2-vitl14` from HuggingFace on first use (several GB).
  * Cost: three ViT-scale passes over every frame, so expect it to be one of the slowest algorithms here - budget hours per sequence, not minutes.

* **MASt3R-SLAM** runs in the `mast3r_slam` conda env. Two config files per sequence, because upstream separates them: `configs/mast3r_slam/<dataset>_calib.yaml` (camera intrinsics, passed via `--calib`) and `configs/mast3r_slam/<dataset>_{vo,vo_lc}.yaml` (algorithm config inheriting upstream's `config/base.yaml`, passed via `--config`). Notes:
  * `main.py` has no `--no-retrieval` flag; loop closure is governed by `retrieval.k` (0 = no candidates), hence one config per mode rather than a CLI switch.
  * `--save-as` is a **label, not a path**: output lands at `logs/<label>/<sequence-stem>.txt` relative to the repo, and the runner copies it into the run dir afterwards.
  * **Known limitation: it does not fit in 12 GB of VRAM** on sequences of this length. It keeps every keyframe on-GPU with no supported way to bound that - `local_opt.window_size` is read but never applied upstream, `dataset.img_downsample` breaks the model (fixed 512-wide checkpoint), and `dataset.subsample: 2` still OOM'd on rosariov2. Needs a larger card.
  * The MASt3R checkpoints are **CC-BY-NC-SA-4.0 (non-commercial)** - this covers the weights, not just the code.

* **MAC-VO** runs in the `macvo` conda env. The config's `root:` field uses a `__WS__` placeholder that `run_macvo.sh` substitutes with the workspace root at launch - never hardcode a path.
* **Basalt** runs the prebuilt binary `basalt_vio` (installed to `~/.local/bin/`) which `run_basalt.sh` sources via `~/.basalt/env`. It uses a per-dataset camera/IMU calibration (`configs/basalt/<dataset>_calib.json`) and the installed upstream estimator profile copied as `configs/basalt/vo_config.json` or `configs/basalt/vio_config.json`. The runner selects the profile by run type; Basalt has no loop closure, so LC modes are rejected. `run_basalt.sh` auto-generates `mav0/cam0/data.csv` and `mav0/cam1/data.csv` on first use. Basalt outputs TUM-format timestamps in seconds.
* **AirSLAM** runs inside the `air_slam` Docker container (ROS Noetic + TensorRT). Requires Docker + nvidia-container-toolkit installed and the container created (see [setup.md](setup.md) sections 7a-7d). The container is started automatically by `run_airslam.sh` if it is stopped. On the **first run per dataset**, TensorRT compiles a resolution-specific engine (~5-10 min); subsequent runs reuse the cache. Config files: `configs/airslam/<dataset>_camera.yaml` (VO, use_imu: 0), `configs/airslam/<dataset>_camera_vio.yaml` (VIO/VIO-LC, use_imu: 1), and `configs/airslam/<dataset>_<vo|vo_lc|vio|vio_slam>.yaml` (VO-keyframe params). For hortimulti, `_camera.yaml` is the VIO config and `_camera_vo.yaml` is the VO override. `vo-lc` and `vio-lc` are two-step processes: `run_airslam.sh` runs `visual_odometry` (produces `trajectory_v0.txt`), then automatically runs `map_refinement` (produces `trajectory_v1.txt`) using `configs/airslam/<dataset>_mr.yaml`. The dataset must have `mav0/cam0/data/` and `mav0/cam1/data/` in EuRoC ASL format (images named by nanosecond timestamp), plus `mav0/imu0/data.csv` for VIO/VIO-LC.
* **OpenVINS** runs inside the `openvins:humble` Docker image (ROS 2 Humble + colcon build of `ov_core/ov_init/ov_msckf/ov_eval`). Build it once with `docker build -t openvins:humble -f src/open_vins/Dockerfile.benchmark src/open_vins`. Configs live in `configs/openvins/<dataset>/{estimator_config.yaml, kalibr_imu_chain.yaml, kalibr_imucam_chain.yaml}`. The wrapper launches `ros2 launch ov_msckf subscribe.launch.py` plus a Python data player (`scripts/run/openvins_data_player.py`) that replays `mav0/cam{0,1}/data/` and `mav0/imu0/data.csv` over `/cam{0,1}/image_raw` and `/imu0` and dumps the resulting TUM trajectory by subscribing to `/ov_msckf/odomimu`. Only `vio` is supported - OpenVINS has no VO mode and no built-in loop closure.
* **Voxel-SVIO** runs inside the `vslam_voxel_svio:noetic` Docker container (ROS 1 Noetic, CPU-only). Build it once with `bash scripts/setup/setup_voxel_svio_docker.sh` (clones nothing - run `git clone https://github.com/ZikangYuan/voxel_svio.git src/voxel_svio` first). Configs live in `configs/voxel_svio/` as a single YAML per sequence (or per dataset for rosariov2/hortimulti). The runner `scripts/run/run_voxel_svio.sh` `rosparam load`s the config, starts `vio_node`, then launches a ROS 1 data player (`scripts/run/voxel_svio_data_player.py`) that replays `mav0/cam{0,1}/data/` and `mav0/imu0/data.csv` over `/cam{0,1}/image_raw` and `/imu0`. After the player finishes the runner SIGINTs `vio_node` and copies `src/voxel_svio/output/pose.txt` (TUM format) to `results/vio/<dataset>/<seq>/voxel_svio/run<N>/trajectory.txt`. Only `vio` is supported.

## Adding AirSLAM for a new dataset

1. Prepare the dataset (must have `mav0/cam0/data/` and `mav0/cam1/data/` in EuRoC format, and `mav0/imu0/data.csv` for VIO/VIO-LC).
2. Create `configs/airslam/<dataset>_camera_vo.yaml` (VO, use_imu: 0) - copy the closest existing one and update intrinsics and cam1 T baseline.
3. Create `configs/airslam/<dataset>_camera_vio.yaml` (VIO, use_imu: 1) - add IMU noise params + correct T_cam_imu transforms.
4. Create `configs/airslam/<dataset>_vo.yaml`, `<dataset>_vo_lc.yaml`, `<dataset>_vio.yaml`, `<dataset>_vio_slam.yaml` - copy the closest existing one and update `image_height`, `image_width`, and set a unique `engine_file` name.
5. Create `configs/airslam/<dataset>_mr.yaml` - map_refinement config for VO-LC/VIO-LC (update `image_width/height` and `engine_file`).
6. Run: `bash scripts/run/run_airslam.sh <dataset> <seq> 1 vo`

## Other datasets

The flow is identical:

```bash
bash scripts/data/convert_hortimulti.sh datasets/hortimulti/strawberry04
bash scripts/run/run_benchmark.sh hortimulti strawberry04 orbslam3 3
bash scripts/run/run_benchmark.sh hortimulti strawberry04 basalt 3
```

For HortiMulti add `configs/macvo/hortimulti_strawberry04.yaml`; ORB-SLAM3 / Basalt / AirSLAM / DROID-SLAM configs are dataset-level and need no change.

**IMU availability:**
- `rosariov2` has `mav0/imu0/data.csv` available - VIO modes work for all algorithms that support them.
- `hortimulti` has `mav0/imu0/data.csv` extracted from the `/ms/imu/data` bag topic via `scripts/data/_hortimulti_extract.py` (str02=190493 samples, str03=48448 samples). VIO modes are available.
- `EuRoC-MAV` has IMU in the standard mav0 layout; VIO modes work.

## GNSS-VIO algorithms (run_type=gnss-vio)

Five algorithms are wired into the `gnss-vio` track. All five require a
`gps.csv` file in the sequence directory (header
`t,lat,lon,alt[,cov_xx,cov_yy,cov_zz,status]`). They write to
`results/gnss-vio/` and contribute to `benchmark-gnss-vio.csv`.

The four ROS-based runners below replay `gps.csv` over a ROS topic via a data
player. **OKVIS2-X is the exception**: it is not a ROS node and reads GNSS from
a file inside the dataset, so `run_okvis2x.sh` converts `gps.csv` into
`mav0/gps0/data_raw.csv` on first use via `scripts/data/gps_to_okvis2x.py`. Run
that by hand to override the assumed accuracy, e.g. for PPK fixes:

```bash
python3 scripts/data/gps_to_okvis2x.py datasets/rosariov2/sequence1 --h-err 0.2 --v-err 0.3
```

* **CIFASIS GNSS-SI** runs inside the `vslam_cifasis_gnss_si:noetic` Docker
  container (ROS 1 Noetic). Build it once with `bash scripts/setup/setup_cifasis_gnss_si_docker.sh`
  (clone first: `git clone https://github.com/CIFASIS/gnss-stereo-inertial-fusion src/cifasis_gnss_si`).
  Configs live in `configs/cifasis_gnss_si/<dataset>_<seq>.yaml`. The runner
  `scripts/run/run_cifasis_gnss_si.sh` starts `roscore` + the
  `GNSS_Stereo_Inertial` ROS node, then publishes data via
  `scripts/run/gnss_data_player.py` on `/stereo/left/image_raw`,
  `/stereo/right/image_raw`, `/imu`, `/gps/fix`. Trajectory is
  `/root/.ros/CameraTrajectoryGPSOpt.txt` (TUM format). Only `gnss-vio` is
  supported.

* **RTAB-Map** runs natively on ROS 2 Humble (no Docker). Install once with
  `sudo apt install ros-humble-rtabmap-ros`. Configs live in
  `configs/rtabmap_gps/<dataset>.yaml`. The runner
  `scripts/run/run_rtabmap_gps.sh` calls `ros2 launch rtabmap_launch rtabmap.launch.py`
  with stereo + IMU + GPS topic remappings, then runs the ROS 2 player
  `scripts/run/gnss_data_player_ros2.py`. Trajectory is exported from the
  rtabmap database via `rtabmap-export --poses --poses_format 11`.

* **VINS-Fusion** runs inside the `vslam_vins_fusion:noetic` Docker container
  (ROS 1 Noetic). Build it once with `bash scripts/setup/setup_vins_fusion_docker.sh`
  (clone first: `git clone https://github.com/HKUST-Aerial-Robotics/VINS-Fusion src/VINS-Fusion`).
  Configs: `configs/vins_fusion/<dataset>_<seq>.yaml` plus
  `<dataset>_cam{0,1}.yaml`. The runner
  `scripts/run/run_vins_fusion_gps.sh` starts `vins_node`,
  `global_fusion_node`, and a small Python recorder that subscribes to
  `/globalEstimator/global_odometry` and writes a TUM file directly to
  `results/gnss-vio/`. Only `gnss-vio` is supported by this runner.

* **OpenVINS+GPS** fuses OpenVINS VIO with GPS through a `robot_localization`
  EKF (ROS 2 Humble, `sudo apt install ros-humble-robot-localization`).
  OpenVINS runs in the `openvins:humble` Docker image and publishes
  `/ov_msckf/odomimu`; on the host, `ekf_node` blends that VIO odometry with
  GPS local-ENU odometry from `navsat_transform_node`. Configs live in
  `configs/robot_loc_openvins/{ekf_gps,navsat}.yaml`. The runner
  `scripts/run/run_openvins_gps.sh` starts the Docker VIO node, the two
  robot_localization nodes, the ROS 2 player (with `--imu-best-effort`, which
  is required - OpenVINS silently drops RELIABLE-QoS IMU), and a recorder on
  `/odometry/filtered`. This is the only *online* loose-GPS estimator (the EKF
  corrects in real time, vs VINS-Fusion's offline pose-graph). Only `gnss-vio`
  is supported.

* **OKVIS2-X** runs natively (no Docker, no ROS) from
  `src/okvis2x/build/okvis_app_synchronous` with
  `configs/okvis2x/<dataset>_<seq>_gnss_vio.yaml`, which sets
  `gps_parameters.data_type: geodetic`. GNSS is fused **tightly-coupled**, the
  same class as CIFASIS GNSS-SI (VINS-Fusion and OpenVINS+GPS are loosely
  coupled). Note `r_SA` - the GNSS antenna position in the IMU frame - is
  currently `[0, 0, 0]` in the shipped configs; measure it on the robot before
  trusting absolute accuracy.

`scripts/run/gnss_data_player.py` (ROS 1) and
`scripts/run/gnss_data_player_ros2.py` (ROS 2) replay an EuRoC-style
sequence + `gps.csv` and publish all four sensor streams. Topics are
configurable per algorithm (`--cam0-topic`, `--cam1-topic`, `--imu-topic`,
`--gps-topic`). Default GPS covariance is `1.0 m^2` horizontal /
`4.0 m^2` vertical (conventional GPS); use `--gps-cov-xy 0.04 --gps-cov-z 0.09`
for PPK-quality fixes. When `gps.csv` already contains per-sample
covariance columns, those are used directly.

**rosariov2 seq5 GPS is the high-quality PPK fix.**
`datasets/rosariov2/sequence5/gps.csv` holds PPK positions
(`/reach_1/ppk/fix`, RTK status 2, vertical RMSE ~0.12 m vs ~1.44 m
conventional). The original conventional fix is preserved as
`gps_conventional.csv` next to it. The PPK lat/lon/alt are resampled onto the
conventional GPS sample times: the raw PPK product ships on an exact 0.2 s grid
that warps VINS-Fusion's pose-graph, so resampling onto the irregular
conventional timestamps isolates GPS data quality from the timestamp grid. To
reproduce the conventional baseline, copy `gps_conventional.csv` over `gps.csv`
and re-run. seq1 still ships the conventional fix (no seq1 PPK log available).
See the GNSS-VIO GPS-quality study in `PROGRESS.md`.

### Running GNSS-VIO algorithms

Use `run_benchmark.sh` with `run_type=gnss-vio` for the full run+eval pipeline:

```bash
# N=3 runs + evaluate + aggregate + append to benchmark-gnss-vio.csv:
bash scripts/run/run_benchmark.sh rosariov2 sequence1 cifasis_gnss_si 3 gnss-vio
bash scripts/run/run_benchmark.sh rosariov2 sequence1 vins_fusion_gps 3 gnss-vio
bash scripts/run/run_benchmark.sh rosariov2 sequence1 rtabmap_gps     3 gnss-vio
bash scripts/run/run_benchmark.sh rosariov2 sequence1 openvins_gps    3 gnss-vio

bash scripts/run/run_benchmark.sh hortimulti strawberry02 cifasis_gnss_si 3 gnss-vio
bash scripts/run/run_benchmark.sh hortimulti strawberry02 vins_fusion_gps 3 gnss-vio
bash scripts/run/run_benchmark.sh hortimulti strawberry02 rtabmap_gps     3 gnss-vio
bash scripts/run/run_benchmark.sh hortimulti strawberry02 openvins_gps    3 gnss-vio
```

Or call the dedicated runners directly for a single run:

```bash
bash scripts/run/run_cifasis_gnss_si.sh  rosariov2 sequence1    1 gnss-vio
bash scripts/run/run_vins_fusion_gps.sh  rosariov2 sequence1    1 gnss-vio
bash scripts/run/run_rtabmap_gps.sh      rosariov2 sequence1    1 gnss-vio
bash scripts/run/run_openvins_gps.sh     rosariov2 sequence1    1 gnss-vio
```

Rebuild the gnss-vio CSV after runs complete:

```bash
python3 scripts/eval/build_benchmark_csv.py gnss-vio
# or rebuild all benchmark CSVs at once:
python3 scripts/eval/build_benchmark_csv.py all
```

Generate plots (segment map + ATE-vs-FPS) for gnss-vio results:

```bash
python3 scripts/eval/_plot_segments.py --type gnss-vio rosariov2 sequence1
python3 scripts/eval/plot_ate_vs_fps.py --type gnss-vio
```
