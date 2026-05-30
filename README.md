# vSLAM Benchmark

> Fully revised: 2026-05-30 22:41 - Added Voxel-SVIO (RA-L 2025) Docker setup, configs, run script.

| Algorithm | Type | Source |
|---|---|---|
| **ORB-SLAM3** | Classical feature-based, stereo / stereo-inertial, optional LC | [kubojion/ORB_SLAM3 @ vslam-benchmark-patches](https://github.com/kubojion/ORB_SLAM3/tree/vslam-benchmark-patches). LC-on results quarantined in `obsolete/`; VO-clean re-run pending. |
| **OKVIS2** | Sliding-window MAP stereo-inertial, optional DBoW + Sim3 LC | [ethz-mrl/okvis2](https://github.com/ethz-mrl/okvis2) (cmake build, system deps) |
| **MAC-VO** | Hybrid (learned uncertainty), stereo VO | [kubojion/MAC-VO @ vslam-benchmark-patches](https://github.com/kubojion/MAC-VO/tree/vslam-benchmark-patches) |
| **Basalt** | Optimization-based stereo VO / VIO | [VladyslavUsenko/basalt](https://gitlab.com/VladyslavUsenko/basalt) (binary install v0.1.7) |
| **AirSLAM** | Deep-feature point-line VO / VIO / V-SLAM (TRO 2025) | [sair-lab/AirSLAM](https://github.com/sair-lab/AirSLAM) (Docker, ROS Noetic + TensorRT) |
| **OpenVINS** | MSCKF stereo-IMU filter (VIO only, no LC) | [rpng/open_vins](https://github.com/rpng/open_vins) (Docker, ROS 2 Humble) |
| **Voxel-SVIO** | Voxel-map-augmented stereo MSCKF VIO (RA-L 2025) | [ZikangYuan/voxel_svio](https://github.com/ZikangYuan/voxel_svio) (Docker, ROS 1 Noetic) |
| **DROID-SLAM** | Neural dense stereo VO (Phase 1 only; dropped per supervisor) | [princeton-vl/DROID-SLAM](https://github.com/princeton-vl/DROID-SLAM). Replaced by DPVO. |
| **MASt3R-SLAM** | Monocular dense SLAM with retrieval-based LC (scaffolded) | [rmurai0610/MASt3R-SLAM](https://github.com/rmurai0610/MASt3R-SLAM) (arXiv:2412.12392) |
| **MegaSaM** | Monocular structure-and-motion, learned (scaffolded) | [mega-sam/mega-sam](https://github.com/mega-sam/mega-sam) (arXiv:2412.04463) |

## Datasets

* **Rosario v2** - outdoor soybean field, stereo + IMU + GPS.
* **HortiMulti** - indoor strawberry polytunnel, stereo + IMU.
* **EuRoC-MAV** (MH_01_easy, MH_03_medium, MH_05_difficult) - [NON-AGRICULTURAL REFERENCE] indoor MAV flight, stereo. Used as a sanity check only.

Rosario v2 and HortiMulti are the primary benchmarks. EuRoC-MAV is tracked as a [NON-AGRICULTURAL REFERENCE] and run once per algorithm to verify configs and the eval pipeline against a known reference dataset.

## Repository layout

```
configs/             # per-(algo,dataset) configs (yaml/txt)
scripts/
├── _paths.sh        # bash helper: resolve_run_type <vo|vio|vio-lc>
├── build/           # build / env-setup scripts (one per algo)
├── data/            # rosbag / euroc converters
├── run/             # per-algorithm runners + multi-run benchmark driver
└── eval/            # ATE/RPE + per-segment evaluation + plots
                     # (_run_type.py defines the python-side run-type table)
results-vo/          # vo runs           (no IMU, no LC)
results-vio/         # vio runs          (IMU on, LC off)
results-vio-lc/      # vio-lc runs       (IMU on, LC on)
benchmark-vo.csv     # aggregated metrics for vo runs
benchmark-vio.csv    # aggregated metrics for vio runs
benchmark-vio-lc.csv # aggregated metrics for vio-lc runs
obsolete/            # quarantined data (e.g. ORB-SLAM3 stereo+LC runs that
                     # don't fit the 3-bucket scheme)
docs/                # public documentation (this file + 3 below)
PROGRESS.md          # running log of results and known issues
```

## Run-type abstraction

Every run is tagged with one of three `run_type`s. The tag controls
*both* the SLAM configuration that is launched *and* the on-disk
location of its output:

| run_type | IMU | Loop closure | Results folder        | Aggregated CSV         |
|----------|-----|--------------|-----------------------|------------------------|
| `vo`     | off | off          | `results-vo/`         | `benchmark-vo.csv`     |
| `vio`    | on  | off          | `results-vio/`        | `benchmark-vio.csv`    |
| `vio-lc` | on  | on           | `results-vio-lc/`     | `benchmark-vio-lc.csv` |

Not every algorithm supports every run type. The runners reject or
warn for unsupported combinations:

| Algorithm   | `vo` | `vio` | `vio-lc` |
|-------------|------|-------|----------|
| ORB-SLAM3   | yes (requires LC-off build) | yes | yes |
| OKVIS2      | yes | yes | yes (IMU sigmas need 5-10x inflation, see PROGRESS.md) |
| AirSLAM     | yes | yes | yes |
| Basalt      | yes | yes | (no LC) |
| OpenVINS    | (no VO mode) | yes | (no LC) |
| Voxel-SVIO  | (no VO mode) | yes | (no LC) |
| MAC-VO      | yes | (not supported) | (not supported) |
| DROID-SLAM  | yes (dropped; results kept) | (not supported) | (not supported) |
| MegaSaM     | yes | (not supported) | (not supported) |
| MASt3R-SLAM | yes (LC disabled) | (no IMU) | yes (LC enabled, IMU still off) |

("MASt3R-SLAM" is monocular: the `vio-lc` bucket is re-used for the
 monocular+LC configuration because that is the only combination it
 offers.)

## Quickstart

```bash
git clone https://github.com/kubojion/vslam-benchmark.git
cd vslam-benchmark

# 2. install deps + clone the SLAM source trees (see docs/setup.md)
# 2b. install Basalt binary (see docs/setup.md §6)
# 2c. set up AirSLAM Docker container (see docs/setup.md §7)
# 2d. (optional) MegaSaM + MASt3R-SLAM envs:
#       bash scripts/build/setup_megasam_env.sh
#       bash scripts/build/setup_mast3r_slam_env.sh

# 3. drop a dataset under datasets/<dataset>/<seq>/ and convert it
bash scripts/data/convert_rosario_to_tum.sh datasets/rosariov2/sequence1

# 4. run any algorithm 3x with full evaluation (default run_type=vo)
bash scripts/run/run_benchmark.sh rosariov2 sequence1 macvo 3

# 4b. same sequence as VIO (IMU on, LC off) - writes to results-vio/
bash scripts/run/run_benchmark.sh rosariov2 sequence1 basalt 3 vio

# 4c. AirSLAM full V-SLAM (IMU + LC) - writes to results-vio-lc/
bash scripts/run/run_benchmark.sh rosariov2 sequence1 airslam 3 vio-lc

# 5. rebuild aggregated CSVs from per-run JSONs
conda run -n macvo python3 scripts/eval/build_benchmark_csv.py all

# 6. read results-vo/rosariov2/sequence1/macvo/report.md (or the equivalent
#    file under results-vio / results-vio-lc)
```

## Documentation

* [docs/setup.md](docs/setup.md) - system deps, building Pangolin + ORB-SLAM3, conda envs, Docker containers.
* [docs/running_algorithms.md](docs/running_algorithms.md) - how to run any algorithm on any dataset / run-type combination.
* [docs/evaluation.md](docs/evaluation.md) - evaluation pipeline, metric definitions, plot conventions.
* [PROGRESS.md](PROGRESS.md) - current results tables (VO / VIO / VIO-LC), known issues, dataset-specific notes.

## Results snapshot

See [PROGRESS.md](PROGRESS.md) for full results (VO / VIO / VIO-LC tables).
The aggregated CSVs (`benchmark-vo.csv`, `benchmark-vio.csv`, `benchmark-vio-lc.csv`) are the source of truth.

Representative VO numbers (N=3 unless noted):

| Algorithm | Dataset | Seq | ATE Sim(3) | Runs |
|---|---|---|---|---|
| ORB-SLAM3 | Rosario v2 | seq1 | **1.18 ± 0.32 m** | 3 |
| ORB-SLAM3 | Rosario v2 | seq5 | 20.21 ± 4.20 m | 3 |
| ORB-SLAM3 | HortiMulti | strawberry02 | 0.893 ± 0.139 m | 3 |
| ORB-SLAM3 | HortiMulti | strawberry03 | **0.104 ± 0.001 m** | 3 |
| DROID-SLAM | Rosario v2 | seq1 | 45.37 m | 3 |
| DROID-SLAM | Rosario v2 | seq5 | 50.02 m | 3 |
| DROID-SLAM | HortiMulti | strawberry02 | 38.92 m | 3 |
| DROID-SLAM | HortiMulti | strawberry03 | 18.76 m | 3 |
| MAC-VO | Rosario v2 | seq1 | 13.52 ± 0.01 m | 3 |
| MAC-VO | Rosario v2 | seq5 | 19.384 ± 0.006 m | 3 |
| MAC-VO | HortiMulti | strawberry03 | 0.505 ± 0.010 m | 3 |
| MAC-VO | HortiMulti | strawberry02 | 10.23 ± 0.50 m | 3 |
| Basalt | Rosario v2 | seq1 | 14.28 ± 0.30 m | 3 |
| Basalt | Rosario v2 | seq5 | 15.04 ± 0.06 m | 3 |
| Basalt | HortiMulti | strawberry02 | 2.098 ± 0.001 m | 3 |
| Basalt | HortiMulti | strawberry03 | **0.275 ± 0.000 m** | 3 |
| AirSLAM | HortiMulti | strawberry03 | 3.631 ± 0.205 m | 3 |
| AirSLAM | HortiMulti | strawberry02 | 20.220 ± 0.824 m | 3 |
| AirSLAM | Rosario v2 | seq1 | 9.89 ± 0.06 m | 3 |
| AirSLAM | Rosario v2 | seq5 | 12.72 ± 0.99 m | 3 |

Representative VIO numbers (Phase 2, N=1 unless noted):

| Algorithm | Dataset | Seq | ATE Sim3 | N |
|---|---|---|---|---|
| ORB-SLAM3 | Rosario v2 | seq5 | **2.29 m** | 1 |
| Basalt | Rosario v2 | seq5 | **4.74 m** | 1 |
| OpenVINS | Rosario v2 | seq1 | 2.32 m | 1 |
| OpenVINS | EuRoC | MH_01_easy | 0.058 m | 1 |

### [NON-AGRICULTURAL REFERENCE] EuRoC-MAV (single-run reference)

> [NON-AGRICULTURAL REFERENCE] Not part of the agricultural benchmark. Single runs are used to verify that configs and the evaluation pipeline behave consistently on known indoor sequences.

| Sequence | Algorithm | ATE Sim3 [m] | ATE SE3 [m] | RPE [m/m] | Scale | FPS |
|---|---|---|---|---|---|---|
| MH_01_easy | ORB-SLAM3 | **0.0340** | **0.0352** | 0.0156 | 1.0021 | 18.17 |
| MH_01_easy | Basalt | 0.0567 | 0.0873 | 0.0085 | 1.0156 | 176.75 |
| MH_01_easy | AirSLAM | 0.1107 | 0.1156 | 0.0195 | 1.0073 | 15.33 |
| MH_01_easy | MAC-VO | 0.1981 | 0.1993 | 0.0295 | 1.0051 | 1.29 |
| MH_01_easy | DROID-SLAM | 4.083 | 7.891 | 0.500 | 0.173 | 13.17 |
| MH_03_medium | ORB-SLAM3 | 0.0437 | 0.0520 | 0.0179 | 0.9922 | 17.89 |
| MH_03_medium | Basalt | 0.1372 | 0.1397 | 0.0159 | 1.0075 | 113.47 |
| MH_03_medium | AirSLAM | 0.1431 | 0.1443 | 0.0188 | 0.9950 | 31.73 |
| MH_03_medium | MAC-VO | 0.3403 | 0.3405 | 0.0187 | 0.9961 | 1.15 |
| MH_03_medium | DROID-SLAM | 3.523 | 7.105 | 2.274 | 0.082 | 10.94 |
| MH_05_difficult | ORB-SLAM3 | 0.0720 | 0.0781 | 0.2282 | 0.9956 | 17.97 |
| MH_05_difficult | Basalt | 0.1816 | 0.1931 | 0.0870 | 1.0097 | 108.72 |
| MH_05_difficult | AirSLAM | 0.2968 | 0.3066 | 0.0256 | 1.0116 | 34.92 |
| MH_05_difficult | MAC-VO | 0.4697 | 0.4836 | 0.0276 | 1.0172 | 0.86 |
| MH_05_difficult | DROID-SLAM | 6.594 | 8.514 | 0.786 | 0.248 | 13.85 |

## License

This benchmarking framework (configs/, scripts/, docs/, results/) is released
under the MIT License - see [LICENSE](LICENSE).
The SLAM algorithms remain under their respective upstream licenses
(ORB-SLAM3: GPLv3, MAC-VO: Apache-2.0, AirSLAM: GPL-3.0, OpenVINS: GPL-3.0,
DROID-SLAM: BSD-3-Clause, MASt3R-SLAM: CC-BY-NC-SA-4.0).
