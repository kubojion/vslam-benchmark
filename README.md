# vSLAM Benchmark


| Algorithm | Type | Source |
|---|---|---|
| **ORB-SLAM3** | Classical feature-based | [kubojion/ORB_SLAM3 @ vslam-benchmark-patches](https://github.com/kubojion/ORB_SLAM3/tree/vslam-benchmark-patches) (build portability + Settings.cc fix) |
| **DROID-SLAM** | Neural | [princeton-vl/DROID-SLAM](https://github.com/princeton-vl/DROID-SLAM) (unmodified) |
| **MAC-VO** | Hybrid (learned uncertainty) | [kubojion/MAC-VO @ vslam-benchmark-patches](https://github.com/kubojion/MAC-VO/tree/vslam-benchmark-patches) (`GeneralStereo` resize preprocess) |
| **Basalt** | Optimization-based stereo VO | [VladyslavUsenko/basalt](https://gitlab.com/VladyslavUsenko/basalt) (binary install v0.1.7, vision-only mode) |
| **AirSLAM** | Deep-feature point-line VO (TRO 2025) | [sair-lab/AirSLAM](https://github.com/sair-lab/AirSLAM) (Docker, ROS Noetic + TensorRT) |

## Datasets

* **Rosario v2** - outdoor soybean field, stereo + IMU + GPS.
* **HortiMulti** - indoor strawberry polytunnel, stereo + IMU.
* **EuRoC-MAV** (MH_01_easy, MH_03_medium, MH_05_difficult) - [NON-AGRICULTURAL REFERENCE] indoor MAV flight, stereo. Used as a sanity check only.

Rosario v2 and HortiMulti are the primary benchmarks. EuRoC-MAV is tracked as a [NON-AGRICULTURAL REFERENCE] and run once per algorithm to verify configs and the eval pipeline against a known reference dataset.

## Repository layout

```
configs/           # per-(algo,dataset) configs (yaml/txt)
scripts/
├── data/          # rosbag → TUM-format dataset converters
├── run/           # per-algorithm runners + multi-run benchmark driver
└── eval/          # ATE/RPE + per-segment evaluation + plots
results/           # SLAM outputs, evaluation reports, segment-map plots
docs/              # public documentation (this file + 3 below)
PROGRESS.md        # running log of results and known issues
```

## Quickstart

```bash
git clone https://github.com/kubojion/vslam-benchmark.git
cd vslam-benchmark

# 2. install deps + clone the SLAM source trees (see docs/setup.md)
# 2b. install Basalt binary (see docs/setup.md §6)
# 2c. set up AirSLAM Docker container (see docs/setup.md §7)

# 3. drop a dataset under datasets/<dataset>/<seq>/ and convert it
bash scripts/data/convert_rosario_to_tum.sh datasets/rosariov2/sequence1

# 4. run any algorithm 3x with full evaluation
bash scripts/run/run_benchmark.sh rosariov2 sequence1 orbslam3 3

# 5. read results/rosariov2/sequence1/orbslam3/report.md
```

## Documentation

* [docs/setup.md](docs/setup.md) - system deps, building Pangolin + ORB-SLAM3, conda envs.
* [docs/running_agorithms.md](docs/running_agorithms.md) - how to add a new sequence and run all three algorithms.
* [docs/evaluation.md](docs/evaluation.md) - evaluation pipeline, metric definitions, plot conventions.
* [PROGRESS.md](PROGRESS.md) - current results table, known issues, dataset-specific notes.

## Results snapshot

See [PROGRESS.md](PROGRESS.md) for the full table; representative numbers:

| Algorithm | Dataset | Seq | ATE Sim(3) | Runs |
|---|---|---|---|---|
| ORB-SLAM3 | Rosario v2 | seq1 | **1.18 ± 0.32 m** | 3 |
| ORB-SLAM3 | Rosario v2 | seq5 | 20.21 ± 4.20 m | 3 |
| ORB-SLAM3 | HortiMulti | strawberry02 | 0.893 ± 0.139 m | 3 |
| ORB-SLAM3 | HortiMulti | strawberry03 | **0.104 ± 0.001 m** | 3 |
| DROID-SLAM | Rosario v2 | seq1 | 45.00 m | 1 |
| DROID-SLAM | Rosario v2 | seq5 | 50.13 m | 1 |
| DROID-SLAM | HortiMulti | strawberry02 | 44.91 m | 1 |
| MAC-VO | Rosario v2 | seq1 | 13.52 ± 0.01 m | 3 |
| MAC-VO | Rosario v2 | seq5 | 19.381 m | 1 |
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

### [NON-AGRICULTURAL REFERENCE] EuRoC-MAV (single-run reference)

> [NON-AGRICULTURAL REFERENCE] Not part of the agricultural benchmark. Single runs are used to verify that configs and the evaluation pipeline behave consistently on known indoor sequences.

| Sequence | Algorithm | ATE Sim3 [m] | ATE SE3 [m] | RPE [m/m] | Scale | FPS |
|---|---|---|---|---|---|---|
| MH_01_easy | ORB-SLAM3 | **0.0340** | **0.0352** | 0.0156 | 1.0021 | 18.17 |
| MH_01_easy | Basalt | 0.0567 | 0.0873 | 0.0085 | 1.0156 | 176.75 |
| MH_01_easy | AirSLAM | 0.1107 | 0.1156 | 0.0195 | 1.0073 | 15.33 |
| MH_01_easy | MAC-VO | 0.1981 | 0.1993 | 0.0295 | 1.0051 | 1.29 |
| MH_03_medium | ORB-SLAM3 | 0.0437 | 0.0520 | 0.0179 | 0.9922 | 17.89 |
| MH_03_medium | Basalt | 0.1372 | 0.1397 | 0.0159 | 1.0075 | 113.47 |
| MH_03_medium | AirSLAM | 0.1431 | 0.1443 | 0.0188 | 0.9950 | 31.73 |
| MH_03_medium | MAC-VO | 0.3403 | 0.3405 | 0.0187 | 0.9961 | 1.15 |
| MH_05_difficult | ORB-SLAM3 | 0.0720 | 0.0781 | 0.2282 | 0.9956 | 17.97 |
| MH_05_difficult | Basalt | 0.1816 | 0.1931 | 0.0870 | 1.0097 | 108.72 |
| MH_05_difficult | AirSLAM | 0.2968 | 0.3066 | 0.0256 | 1.0116 | 34.92 |
| MH_05_difficult | MAC-VO | 0.4697 | 0.4836 | 0.0276 | 1.0172 | 0.86 |

## License

This benchmarking framework (configs/, scripts/, docs/, results/) is released
under the MIT License - see [LICENSE](LICENSE).  
The SLAM algorithms remain under their respective upstream licenses
(ORB-SLAM3: GPLv3, DROID-SLAM: BSD-3-Clause, MAC-VO: Apache-2.0, AirSLAM: GPL-3.0).
