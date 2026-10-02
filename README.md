# vSLAM Benchmark

> **Native review in progress (2026-10-02): 69 cells have verified protocol N=3.**
> Twelve previously green EuRoC ORB cells are held because historical ORB/g2o
> library identities are unknown; this does not establish incompatibility or
> request blanket reruns. Scores and original decisions remain preserved.
> Green verifies three consistently configured attempts, including valid failures.
> ZED claims remain nominal 3D **position** only, with mounting, RTK-float and
> clock limits. See [TODO](TODO.md) and [current readiness work](docs/execution-readiness-20261002.md).
> Only the specifically authorized remaining ZED VIO first repetitions may run
> after engineering and preflight refresh; no full campaign, repetitions 2/3 or push.



| Algorithm | Type | Source |
|---|---|---|
| **ORB-SLAM3** | Classical feature-based, stereo / stereo-inertial, optional LC | [kubojion/ORB_SLAM3 @ vslam-benchmark-patches](https://github.com/kubojion/ORB_SLAM3/tree/vslam-benchmark-patches). Built and run natively. Current repeat coverage and crash gaps are recorded in TODO; older results are historical. |
| **OKVIS2** | Sliding-window MAP stereo-inertial, optional DBoW + Sim3 LC | [ethz-mrl/okvis2](https://github.com/ethz-mrl/okvis2) (cmake build, system deps) |
| **OKVIS2-X** | Multi-sensor OKVIS2 extension; VO/VIO/VIO-LC/GNSS capability | [ethz-mrl/OKVIS2-X](https://github.com/ethz-mrl/OKVIS2-X) (cmake build, system deps). Wired in independently of OKVIS2: own source tree, configs, runner and results. |
| **MAC-VO** | Hybrid (learned uncertainty), stereo VO | [kubojion/MAC-VO @ vslam-benchmark-patches](https://github.com/kubojion/MAC-VO/tree/vslam-benchmark-patches) |
| **Basalt** | Optimization-based stereo VO / VIO | [VladyslavUsenko/basalt](https://gitlab.com/VladyslavUsenko/basalt) (binary install v0.1.7) |
| **AirSLAM** | Deep-feature point-line VO / VIO / V-SLAM (TRO 2025) | [kubojion/AirSLAM @ vslam-benchmark-patches](https://github.com/kubojion/AirSLAM/tree/vslam-benchmark-patches) (Docker, ROS Noetic + TensorRT; fork carries VIO launch files; corrected inertial results use rectification patch `1e0ad79c28d4`) |
| **OV2SLAM** | Fully online feature/KLT stereo VO with BA and optional online-BoW LC | [ov2slam/ov2slam](https://github.com/ov2slam/ov2slam) (Docker, ROS 1 Noetic) |
| **OpenVINS** | MSCKF stereo-IMU filter (VIO only, no LC) | [kubojion/open_vins @ vslam-benchmark-patches](https://github.com/kubojion/open_vins/tree/vslam-benchmark-patches) (Docker, ROS 2 Humble; fork carries Dockerfile.benchmark; new EuRoC runs use shutdown patch `7a496c53d9ee`) |
| **Voxel-SVIO** | Voxel-map-augmented stereo MSCKF VIO (RA-L 2025) | [ZikangYuan/voxel_svio](https://github.com/ZikangYuan/voxel_svio) (Docker, ROS 1 Noetic) |
| **CIFASIS GNSS-SI** | Tightly-coupled GNSS+stereo+inertial SLAM, ORB-SLAM3-based (JFR 2023) | [CIFASIS/gnss-stereo-inertial-fusion](https://github.com/CIFASIS/gnss-stereo-inertial-fusion) (Docker, ROS 1 Noetic) |
| **RTAB-Map** | Graph-based stereo SLAM with optional IMU + GNSS factors | [introlab/rtabmap_ros](https://github.com/introlab/rtabmap_ros) (apt, ROS 2 Humble) |
| **VINS-Fusion** | Optimization-based stereo+IMU VIO with loose GPS fusion | [HKUST-Aerial-Robotics/VINS-Fusion](https://github.com/HKUST-Aerial-Robotics/VINS-Fusion) (Docker, ROS 1 Noetic) |
| **DROID-SLAM** | Neural dense stereo VO (Phase 1 only; dropped per supervisor) | [princeton-vl/DROID-SLAM](https://github.com/princeton-vl/DROID-SLAM). Historical results retained. |
| **DPVO / DPV-SLAM** | Monocular deep patch VO (+ optional loop closure); DROID-SLAM successor | [princeton-vl/DPVO](https://github.com/princeton-vl/DPVO) (MIT). ~2-4 GB VRAM. |
| **MASt3R-SLAM** | Monocular dense SLAM with retrieval-based LC (needs >12 GB VRAM) | [rmurai0610/MASt3R-SLAM](https://github.com/rmurai0610/MASt3R-SLAM) (arXiv:2412.12392) |
| **MegaSaM** | Monocular structure-and-motion, learned (3-stage pipeline) | [mega-sam/mega-sam](https://github.com/mega-sam/mega-sam) (arXiv:2412.04463) |

## Datasets

* **Rosario v2** - outdoor soybean field, stereo + IMU + GPS.
* **HortiMulti** - indoor strawberry polytunnel, stereo + IMU + consumer GNSS.
* **ZED2i `field1_110426_full_10fps_q90`** - the project's own agricultural field sequence, stereo + IMU + RTK position reference.
* **EuRoC-MAV** (MH_01_easy, MH_03_medium, MH_05_difficult) - [NON-AGRICULTURAL REFERENCE] indoor MAV flight, stereo + IMU. Used as a sanity check only.

Rosario v2, HortiMulti and the local ZED2i field sequence are the agricultural scope. A separate
GREENBOT dataset is not part of the current benchmark. EuRoC-MAV is tracked as a
[NON-AGRICULTURAL REFERENCE] for configuration/evaluation checks; the executed server campaign includes three repetitions per cell.
Its canonical repository identifier/path is `euroc_mav`; CLI aliases `EuRoC-MAV` and `euroc` are
normalized before result/config paths are constructed.

## Repository layout

```
configs/             # per-(algo,dataset) configs (yaml/txt)
scripts/
├── _paths.sh        # bash helper: resolve_run_type <vo|vo-lc|vio|vio-lc|gnss-vio>
├── build/           # build / env-setup scripts (one per algo)
├── data/            # rosbag / euroc converters
├── run/             # per-algorithm runners + multi-run benchmark driver
└── eval/            # ATE/RPE + per-segment evaluation + plots
                     # (_run_type.py defines the python-side run-type table)
results/             # generated artifacts, manifest, and local browser (Git-ignored)
├── vo/              # visual-only, no loop closure
├── vo-lc/           # visual-only with loop closure
├── vio/             # visual-inertial, no loop closure
├── vio-lc/          # visual-inertial with loop closure
├── gnss-vio/        # visual-inertial with GNSS
└── site/            # generated static result browser
benchmark-vo.csv     # aggregated metrics for vo runs
benchmark-vo-lc.csv  # aggregated metrics for vo-lc runs
benchmark-vio.csv    # aggregated metrics for vio runs
benchmark-vio-lc.csv # aggregated metrics for vio-lc runs
benchmark-gnss-vio.csv # aggregated metrics for gnss-vio runs
obsolete/            # quarantined data (e.g. ORB-SLAM3 stereo+LC runs that
                     # don't fit the current run-type scheme)
experiments/          # smoke/failed artifacts excluded from benchmark discovery
vendor/prerequisites/ # OKVIS2 external CMake patches + install.sh (see its README)
datasets/            # bulk data untracked; gt_*.txt / times.txt / manifest.json
                     # / segments_auto.csv ARE git-tracked (GT provenance)
docs/                # documentation — see docs/README.md for the layout:
                     # core how-tos | generated/ (tables, claims, figures) |
                     # campaigns/ (agent briefs + campaign records) | private/
PROGRESS.md          # running log of results and known issues
TODO.md              # authoritative open-work matrix (🔁 = re-run recommended)
```

## Run-type abstraction

Every run is tagged with one of five `run_type`s. The tag controls
*both* the SLAM configuration that is launched *and* the on-disk
location of its output:

| run_type | IMU | Loop closure | GNSS | Results folder | Aggregated CSV |
|---|---|---|---|---|---|
| `vo` | off | off | off | `results/vo/` | `benchmark-vo.csv` |
| `vo-lc` | off | on | off | `results/vo-lc/` | `benchmark-vo-lc.csv` |
| `vio` | on | off | off | `results/vio/` | `benchmark-vio.csv` |
| `vio-lc` | on | on | off | `results/vio-lc/` | `benchmark-vio-lc.csv` |
| `gnss-vio` | on | off | on | `results/gnss-vio/` | `benchmark-gnss-vio.csv` |

Not every algorithm supports every run type. The runners reject or
warn for unsupported combinations:

| Algorithm   | `vo` | `vo-lc` | `vio` | `vio-lc` |
|-------------|------|---------|-------|----------|
| ORB-SLAM3   | yes (requires LC-off build) | yes | yes | yes |
| OKVIS2      | yes | yes (experimental) | yes | yes (see docs/okvis-imu-noise-derivation.md) |
| OKVIS2-X    | yes (best-effort, no IMU) | yes (experimental) | yes | yes (also `gnss-vio`: tightly-coupled GNSS) |
| AirSLAM     | yes | yes | yes | yes |
| OV2SLAM     | yes | yes | no | no |
| Basalt      | yes | no | yes | (no LC) |
| DPVO / DPV-SLAM | yes | yes (DPV-SLAM) | no | no |
| MASt3R-SLAM | yes | yes (retrieval LC, needs >12 GB VRAM) | no | no |
| OpenVINS    | (no VO mode) | no | yes (+gnss-vio via robot_localization) | (no LC) |
| Voxel-SVIO  | (no VO mode) | no | yes | (no LC) |
| CIFASIS GNSS-SI | (no VO mode) | no | (gnss-vio only) | (gnss-vio only) |
| RTAB-Map    | (gnss-vio only) | no | (gnss-vio only) | (gnss-vio only) |
| VINS-Fusion | (no VO mode) | no | (gnss-vio only) | (gnss-vio only) |
| MAC-VO      | yes | no | (not supported) | (not supported) |
| DROID-SLAM  | yes (dropped; results kept) | no | (not supported) | (not supported) |
| MegaSaM     | yes | no | (not supported) | (not supported) |

## Quickstart

```bash
git clone --recurse-submodules https://github.com/kubojion/vslam-benchmark.git
cd vslam-benchmark

# 2. install deps + clone the SLAM source trees (see docs/setup.md)
# 2b. install Basalt binary (see docs/setup.md §6)
# 2c. set up AirSLAM Docker container (see docs/setup.md §7)
# 2d. (optional) MegaSaM + MASt3R-SLAM envs:
#       bash scripts/build/setup_megasam_env.sh
#       bash scripts/build/setup_mast3r_slam_env.sh

# Future execution requires readiness and authorization. The controller preserves
# existing attempts and evaluates each repetition before continuing. See TODO.md.

# 3. drop a dataset under datasets/<dataset>/<seq>/ and convert it
bash scripts/data/convert_rosario_to_tum.sh datasets/rosariov2/sequence1

# 4. run any algorithm 3x with full evaluation (default run_type=vo)
bash scripts/run/run_benchmark.sh rosariov2 sequence1 macvo 3

# 4b. same sequence as VIO (IMU on, LC off) - writes to results/vio/
bash scripts/run/run_benchmark.sh rosariov2 sequence1 basalt 3 vio

# 4c. AirSLAM full V-SLAM (IMU + LC) - writes to results/vio-lc/
bash scripts/run/run_benchmark.sh rosariov2 sequence1 airslam 3 vio-lc

# 4d. DPV-SLAM visual-only loop closure - writes to results/vo-lc/
bash scripts/run/run_benchmark.sh rosariov2 sequence1 dpvo 1 vo-lc

# 4e. CIFASIS GNSS-SI (stereo + IMU + GNSS) - writes to results/gnss-vio/
bash scripts/run/run_benchmark.sh rosariov2 sequence1 cifasis_gnss_si 3 gnss-vio

# 5. rebuild aggregated CSVs from per-run JSONs
conda run -n macvo python3 scripts/eval/build_benchmark_csv.py all

# 6. read results/vo/rosariov2/sequence1/macvo/report.md (or the equivalent
#    file under another results/<run-type>/ directory)

# 7. browse local artifacts, plots, logs, and the five tracked comparisons
bash scripts/results/serve_site.sh 8080
```

## Documentation

* [docs/setup.md](docs/setup.md) - system deps, building Pangolin + ORB-SLAM3, conda envs, Docker containers.
* [docs/running_algorithms.md](docs/running_algorithms.md) - how to run any algorithm on any dataset / run-type combination.
* [docs/evaluation.md](docs/evaluation.md) - evaluation pipeline, metric definitions, plot conventions.
* [docs/result-storage-design.md](docs/result-storage-design.md) - attempt preservation, evaluation history, manifest, and browser behavior.
* [PROGRESS.md](PROGRESS.md) - current results tables (VO / VIO / VIO-LC), known issues, dataset-specific notes.

## Results snapshot

Current numerical and execution status is documented in [TODO](TODO.md) and
[the focused campaign](docs/euroc-focused-campaign-20261001.md). The four-mode
comparison has 551/600 evaluated repetitions, including retained collapses. Across
all scopes, 622 evaluations are reconciled. The original 593 numerical
evaluations and all historical attempts remain intact.

The five root CSVs contain **666 rows**: 660 planned default repetitions plus six
separate GNSS variants. The corrected AirSLAM inertial cohort uses physical runs
4–6. Its 18 affected original runs remain in `benchmark-historical-cohorts.csv`,
their original directories and separate reports. Missing runs and failures remain
explicit. [Tables](docs/generated/tables.md), [counts](docs/generated/verified-claims.md),
[figures](docs/generated/README.md) and the browser use the same checked inventory.

The [current native review](docs/execution-readiness-20261002.md) retains **69 N=3 cells**: 60 EuRoC and nine ZED. Twelve historical ORB cells previously qualified at the 81-cell checkpoint are now under explicit dependency/ABI review. Their previous decisions and numerical results remain preserved. Future manifests require identity and preflight refresh after the ongoing engineering changes; older category totals are dated snapshots.
Readiness is per action and requires its recorded native/configuration checks.
ZED nominal position qualification does not resolve Rosario, Horti or GNSS blockers.
Older generated reports and figures remain [archived](docs/generated/historical-before-repair-20261001/README.md).

The historical observations in [PROGRESS.md](PROGRESS.md) require reassessment against the
corrected calibration, declared configuration cohorts, failures and coverage. In particular,
old ZED VIO collapse cannot be attributed solely to weak excitation after discovery of the
optical-camera/IMU frame error. The next milestone is closing the current execution and
validation gaps before expanding the algorithm set.

## License

This benchmarking framework (configs/, scripts/, docs/, results/) is released
under the MIT License - see [LICENSE](LICENSE).
The SLAM algorithms remain under their respective upstream licenses
(ORB-SLAM3: GPLv3, MAC-VO: Apache-2.0, AirSLAM: GPL-3.0, OpenVINS: GPL-3.0,
DROID-SLAM: BSD-3-Clause, MASt3R-SLAM: CC-BY-NC-SA-4.0, OKVIS2-X: BSD-3-Clause).
