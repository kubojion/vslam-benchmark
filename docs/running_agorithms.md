# Running the algorithms

The framework expects a sequence under

```
datasets/<dataset>/<seq>/
├── cam0/        # rectified left images  (PNG/JPG, sorted by filename)
├── cam1/        # rectified right images
├── times.txt    # one line per frame, nanosecond timestamps
└── gt_tum.txt   # ground truth in TUM format (timestamp tx ty tz qx qy qz qw, seconds)
```

`scripts/data/convert_*.sh` produce this layout from raw rosbags (Rosario v2, HortiMulti, LFSD).

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

```bash
# All five with the standard 3-run + evaluation pipeline:
bash scripts/run/run_benchmark.sh rosariov2 sequence2 orbslam3 3
bash scripts/run/run_benchmark.sh rosariov2 sequence2 droidslam 3
bash scripts/run/run_benchmark.sh rosariov2 sequence2 macvo 3
bash scripts/run/run_benchmark.sh rosariov2 sequence2 basalt 3
bash scripts/run/run_benchmark.sh rosariov2 sequence2 airslam 3
```

`run_benchmark.sh` calls the per-algorithm runner N times then evaluates each
run and aggregates the results (see [evaluation.md](evaluation.md)).

If you only want a single ad-hoc run:

```bash
bash scripts/run/run_orbslam3.sh  rosariov2 sequence2 1
bash scripts/run/run_droidslam.sh rosariov2 sequence2 1
bash scripts/run/run_macvo.sh     rosariov2 sequence2 1
bash scripts/run/run_basalt.sh    rosariov2 sequence2 1
bash scripts/run/run_airslam.sh   rosariov2 sequence2 1
```

Per-run output: `results/<dataset>/<seq>/<algo>/run<N>/{trajectory.txt, run_log.txt, resources.csv}`.

## Notes per algorithm

* **ORB-SLAM3** needs the executable `stereo_euroc` from `src/ORB_SLAM3/Examples/Stereo/`. Re-run `./build.sh` if it's missing.
* **DROID-SLAM** runs in the `droidenv` conda env. With `stride=2` it processes every second frame; trajectory length will be ~half the input.
* **MAC-VO** runs in the `macvo` conda env. The config's `root:` field uses a `__WS__` placeholder that `run_macvo.sh` substitutes with the workspace root at launch - never hardcode a path.
* **Basalt** runs the prebuilt binary `basalt_vio` (installed to `~/.local/bin/`) which `run_basalt.sh` sources via `~/.basalt/env`. Two config files are required: a per-dataset camera calibration (`configs/basalt/<dataset>_calib.json`) and a shared VO config (`configs/basalt/vo_config.json`). The calibration uses the EuRoC JSON format (pinhole camera model, flat vignette for rectified images). `run_basalt.sh` auto-generates `mav0/cam0/data.csv` and `mav0/cam1/data.csv` on first use - no manual data prep needed. Basalt outputs TUM-format timestamps already in SECONDS (no conversion needed, unlike ORB-SLAM3). The `vio_min_triangulation_dist` in `vo_config.json` must be set BELOW the stereo baseline of the smallest-baseline dataset (currently 0.03 m for Rosario v2 baseline of 4.97 cm).
* **AirSLAM** runs inside the `air_slam` Docker container (ROS Noetic + TensorRT). Requires Docker + nvidia-container-toolkit installed and the container created (see [setup.md](setup.md) sections 7a-7d). The container is started automatically by `run_airslam.sh` if it is stopped. On the **first run per dataset**, TensorRT compiles a resolution-specific engine (~5-10 min); subsequent runs reuse the cache. Config files: `configs/airslam/<dataset>_camera.yaml` (intrinsics + extrinsics) and `configs/airslam/<dataset>_vo.yaml` (image size, VO params). The dataset must have a `mav0/cam0/data/` and `mav0/cam1/data/` subfolder in EuRoC ASL format (images named by nanosecond timestamp) - both `hortimulti` and `rosariov2` already satisfy this.

## Adding AirSLAM for a new dataset

1. Prepare the dataset (must have `mav0/cam0/data/` and `mav0/cam1/data/` in EuRoC format).
2. Create `configs/airslam/<dataset>_camera.yaml` - copy the closest existing one and update `intrinsics` and the cam1 T translation with the correct baseline.
3. Create `configs/airslam/<dataset>_vo.yaml` - copy the closest existing one and update `image_height`, `image_width` (both `plnet` and top-level), and set a unique `engine_file` name.
4. Run: `bash scripts/run/run_airslam.sh <dataset> <seq> 1`

## Other datasets

The flow is identical:

```bash
bash scripts/data/convert_hortimulti.sh datasets/hortimulti/strawberry04
bash scripts/run/run_benchmark.sh hortimulti strawberry04 orbslam3 3
bash scripts/run/run_benchmark.sh hortimulti strawberry04 basalt 3
```

For HortiMulti add `configs/macvo/hortimulti_strawberry04.yaml`; ORB-SLAM3 / DROID / Basalt configs are dataset-level and need no change.
