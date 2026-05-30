# Running the algorithms

> Fully revised: 2026-05-30 22:41 - Added Voxel-SVIO (RA-L 2025) Docker setup, configs, and per-algo notes.
> Updated: 2026-06-01 - Added AirSLAM VIO/VIO-LC support (separate `_camera_vio.yaml` + two-step map_refinement); OKVIS2 configs added for HortiMulti and EuRoC; OpenVINS HortiMulti config added; DPVO removed.

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

* `vo`     - no IMU, no LC, output -> `results-vo/`        (`benchmark-vo.csv`)
* `vio`    - IMU on, no LC, output -> `results-vio/`       (`benchmark-vio.csv`)
* `vio-lc` - IMU on, LC on, output -> `results-vio-lc/`    (`benchmark-vio-lc.csv`)

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

# Monocular scaffolded algorithms:
bash scripts/run/run_benchmark.sh euroc_mav MH_01_easy megasam     1 vo
bash scripts/run/run_benchmark.sh euroc_mav MH_01_easy mast3r_slam 1 vio-lc  # LC enabled
```

Direct single runs forward run_type as the 4th positional:

```bash
bash scripts/run/run_orbslam3.sh    rosariov2 sequence2 1 vo
bash scripts/run/run_okvis2.sh      rosariov2 sequence2 1 vio
bash scripts/run/run_openvins.sh    rosariov2 sequence2 1 vio
bash scripts/run/run_droidslam.sh   rosariov2 sequence2 1 vo
bash scripts/run/run_macvo.sh       rosariov2 sequence2 1 vo
bash scripts/run/run_basalt.sh      rosariov2 sequence2 1 vio
bash scripts/run/run_airslam.sh     rosariov2 sequence2 1 vio-lc
bash scripts/run/run_megasam.sh     rosariov2 sequence2 1 vo
bash scripts/run/run_mast3r_slam.sh rosariov2 sequence2 1 vio-lc
```

Per-run output: `<RESULTS_ROOT>/<dataset>/<seq>/<algo>/run<N>/{trajectory.txt, run_log.txt, resources.csv}`
where `<RESULTS_ROOT>` is `results-vo/`, `results-vio/`, or `results-vio-lc/` depending on `run_type`.

### Per-algorithm run-type support

| Algorithm   | `vo` | `vio` | `vio-lc` | Notes |
|-------------|------|-------|----------|-------|
| ORB-SLAM3   | yes (needs LC-off build, see PROGRESS.md) | yes (stereo-inertial) | yes (stereo-inertial + LC) | |
| OKVIS2      | yes | yes | yes | configs exist for rosariov2, EuRoC, and hortimulti; use OKVIS2-compatible IMU noise values (not raw Allan) - see PROGRESS.md Phase 4.6 |
| OpenVINS    | no (MSCKF requires IMU) | yes | no (no built-in LC) | Runs inside `openvins:humble` Docker image; datasets need `mav0/imu0/data.csv` |
| Voxel-SVIO  | no (MSCKF requires IMU) | yes | no (no built-in LC) | Runs inside `vslam_voxel_svio:noetic` Docker image (ROS 1 Noetic, CPU-only); datasets need `mav0/imu0/data.csv` |
| AirSLAM     | yes | yes | yes | VIO/VIO-LC require `_camera_vio.yaml` (use_imu: 1) + `mav0/imu0/data.csv`; VIO-LC runs two-step (visual_odometry + map_refinement) |
| Basalt      | yes (`--use-imu false`) | yes (`--use-imu true`) | no (Basalt has no LC) | |
| MAC-VO      | yes | no (vision-only) | no (vision-only) | |
| DROID-SLAM  | yes (dropped; results kept) | no | no | |
| MegaSaM     | yes | no | no | monocular only |
| MASt3R-SLAM | yes (LC disabled) | no | yes (LC enabled, IMU still off) | monocular only |


## Notes per algorithm

* **ORB-SLAM3** needs the executable `stereo_euroc` from `src/ORB_SLAM3/Examples/Stereo/`. Re-run `./build.sh` if it's missing.
* **OKVIS2** uses the binary `src/okvis2/build/okvis_app_synchronous`. Config files: `configs/okvis2/<dataset>_<seq>_vio.yaml` (or `_vio_lc.yaml` / `_vo.yaml` - per-sequence, per-mode). Run type is controlled by the `--run-type` flag passed by `run_okvis2.sh`. Configs exist for rosariov2 (seq1, seq5), EuRoC (MH_01/03/05), and HortiMulti (strawberry02/03). **IMU noise params must use OKVIS2-compatible values** - raw Allan-variance numbers from sensor calibration are typically 12-840x too tight for OKVIS2's MAP estimator and cause scale collapse. Use the D435i reference values in the rosariov2 configs as a starting point. See PROGRESS.md Phase 4.6 for the full diagnosis and corrected params.
* **DROID-SLAM** runs in the `droidenv` conda env. The key VRAM-tuning parameter is `--filter_thresh`: the minimum optical-flow confidence required to keep a frame in the bundle adjustment window. Lower values process more frames but consume more VRAM. The default in `run_droidslam.sh` is `--filter_thresh 6.0`, which was empirically the lowest value that fits in VRAM on long sequences (Rosario, HortiMulti) without OOM. `--stride` defaults to 1 (all frames). The initial Rosario seq1 benchmark used `stride=2` (50% of frames); the final 3-run benchmark used `stride=1 --filter_thresh 6.0`. ATE barely changed between the two (45.37 vs 45.00 m), confirming the failure is domain-mismatch, not frame density.
* **MAC-VO** runs in the `macvo` conda env. The config's `root:` field uses a `__WS__` placeholder that `run_macvo.sh` substitutes with the workspace root at launch - never hardcode a path.
* **Basalt** runs the prebuilt binary `basalt_vio` (installed to `~/.local/bin/`) which `run_basalt.sh` sources via `~/.basalt/env`. Two config files are required: a per-dataset camera calibration (`configs/basalt/<dataset>_calib.json`) and a shared VO config (`configs/basalt/vo_config.json`). The calibration uses the EuRoC JSON format (pinhole camera model, flat vignette for rectified images). `run_basalt.sh` auto-generates `mav0/cam0/data.csv` and `mav0/cam1/data.csv` on first use - no manual data prep needed. Basalt outputs TUM-format timestamps already in SECONDS (no conversion needed, unlike ORB-SLAM3). The `vio_min_triangulation_dist` in `vo_config.json` must be set BELOW the stereo baseline of the smallest-baseline dataset (currently 0.03 m for Rosario v2 baseline of 4.97 cm).
* **AirSLAM** runs inside the `air_slam` Docker container (ROS Noetic + TensorRT). Requires Docker + nvidia-container-toolkit installed and the container created (see [setup.md](setup.md) sections 7a-7d). The container is started automatically by `run_airslam.sh` if it is stopped. On the **first run per dataset**, TensorRT compiles a resolution-specific engine (~5-10 min); subsequent runs reuse the cache. Config files: `configs/airslam/<dataset>_camera.yaml` (VO, use_imu: 0), `configs/airslam/<dataset>_camera_vio.yaml` (VIO/VIO-LC, use_imu: 1), and `configs/airslam/<dataset>_<vo|vio|vio_slam>.yaml` (VO-keyframe params). For hortimulti, `_camera.yaml` is the VIO config and `_camera_vo.yaml` is the VO override. VIO-LC is a two-step process: `run_airslam.sh` runs `visual_odometry` (produces `trajectory_v0.txt`), then automatically runs `map_refinement` (produces `trajectory_v1.txt`) using `configs/airslam/<dataset>_mr.yaml`. The dataset must have `mav0/cam0/data/` and `mav0/cam1/data/` in EuRoC ASL format (images named by nanosecond timestamp), plus `mav0/imu0/data.csv` for VIO/VIO-LC.
* **OpenVINS** runs inside the `openvins:humble` Docker image (ROS 2 Humble + colcon build of `ov_core/ov_init/ov_msckf/ov_eval`). Build it once with `docker build -t openvins:humble -f src/open_vins/Dockerfile.benchmark src/open_vins`. Configs live in `configs/openvins/<dataset>/{estimator_config.yaml, kalibr_imu_chain.yaml, kalibr_imucam_chain.yaml}`. The wrapper launches `ros2 launch ov_msckf subscribe.launch.py` plus a Python data player (`scripts/run/openvins_data_player.py`) that replays `mav0/cam{0,1}/data/` and `mav0/imu0/data.csv` over `/cam{0,1}/image_raw` and `/imu0` and dumps the resulting TUM trajectory by subscribing to `/ov_msckf/odomimu`. Only `vio` is supported - OpenVINS has no VO mode and no built-in loop closure.
* **Voxel-SVIO** runs inside the `vslam_voxel_svio:noetic` Docker container (ROS 1 Noetic, CPU-only). Build it once with `bash scripts/setup/setup_voxel_svio_docker.sh` (clones nothing - run `git clone https://github.com/ZikangYuan/voxel_svio.git src/voxel_svio` first). Configs live in `configs/voxel_svio/` as a single YAML per sequence (or per dataset for rosariov2/hortimulti). The runner `scripts/run/run_voxel_svio.sh` `rosparam load`s the config, starts `vio_node`, then launches a ROS 1 data player (`scripts/run/voxel_svio_data_player.py`) that replays `mav0/cam{0,1}/data/` and `mav0/imu0/data.csv` over `/cam{0,1}/image_raw` and `/imu0`. After the player finishes the runner SIGINTs `vio_node` and copies `src/voxel_svio/output/pose.txt` (TUM format) to `results-vio/<dataset>/<seq>/voxel_svio/run<N>/trajectory.txt`. Only `vio` is supported.

## Adding AirSLAM for a new dataset

1. Prepare the dataset (must have `mav0/cam0/data/` and `mav0/cam1/data/` in EuRoC format, and `mav0/imu0/data.csv` for VIO/VIO-LC).
2. Create `configs/airslam/<dataset>_camera_vo.yaml` (VO, use_imu: 0) - copy the closest existing one and update intrinsics and cam1 T baseline.
3. Create `configs/airslam/<dataset>_camera_vio.yaml` (VIO, use_imu: 1) - add IMU noise params + correct T_cam_imu transforms.
4. Create `configs/airslam/<dataset>_vo.yaml`, `<dataset>_vio.yaml`, `<dataset>_vio_slam.yaml` - copy the closest existing one and update `image_height`, `image_width`, and set a unique `engine_file` name.
5. Create `configs/airslam/<dataset>_mr.yaml` - map_refinement config for VIO-LC (update `image_width/height` and `engine_file`).
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
- `hortimulti` currently lacks extracted `mav0/imu0/data.csv` (the IMU topic `/ms/imu/data` exists in the raw bag but has not yet been extracted). VIO modes are blocked until `scripts/data/_hortimulti_extract.py` is updated.
- `EuRoC-MAV` has IMU in the standard mav0 layout; VIO modes work.
