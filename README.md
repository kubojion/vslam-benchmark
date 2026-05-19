# vSLAM Benchmark

BSc thesis framework for benchmarking three visual SLAM algorithms on
agricultural stereo datasets.

| Algorithm | Type | Source |
|---|---|---|
| **ORB-SLAM3** | Classical feature-based | [kubojion/ORB_SLAM3 @ vslam-benchmark-patches](https://github.com/kubojion/ORB_SLAM3/tree/vslam-benchmark-patches) (build portability + Settings.cc fix) |
| **DROID-SLAM** | Neural | [princeton-vl/DROID-SLAM](https://github.com/princeton-vl/DROID-SLAM) (unmodified) |
| **MAC-VO** | Hybrid (learned uncertainty) | [kubojion/MAC-VO @ vslam-benchmark-patches](https://github.com/kubojion/MAC-VO/tree/vslam-benchmark-patches) (`GeneralStereo` resize preprocess) |

## Datasets

* **Rosario v2** — outdoor soybean field, stereo + IMU + GPS.
* **HortiMulti** — indoor strawberry polytunnel, stereo + IMU.
* **LFSD** — Light Field Stereo Dataset.

Only Rosario v2 + HortiMulti are actively benchmarked at the moment.

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

# 1. install deps + clone the 3 SLAM source trees (see docs/setup.md)

# 2. drop a dataset under datasets/<dataset>/<seq>/ and convert it
bash scripts/data/convert_rosario_to_tum.sh datasets/rosariov2/sequence1

# 3. run any algorithm 3x with full evaluation
bash scripts/run/run_benchmark.sh rosariov2 sequence1 orbslam3 3

# 4. read results/rosariov2/sequence1/orbslam3/report.md
```

## Documentation

* [docs/setup.md](docs/setup.md) — system deps, building Pangolin + ORB-SLAM3, conda envs.
* [docs/running_agorithms.md](docs/running_agorithms.md) — how to add a new sequence and run all three algorithms.
* [docs/evaluation.md](docs/evaluation.md) — evaluation pipeline, metric definitions, plot conventions.
* [PROGRESS.md](PROGRESS.md) — current results table, known issues, dataset-specific notes.

## Results snapshot

See [PROGRESS.md](PROGRESS.md) for the full table; representative numbers:

| Algorithm | Dataset | Seq | ATE Sim(3) | Runs |
|---|---|---|---|---|
| ORB-SLAM3 | Rosario v2 | seq1 | **1.18 ± 0.32 m** | 3 |
| ORB-SLAM3 | HortiMulti | strawberry03 | **0.104 ± 0.001 m** | 3 |
| DROID-SLAM | Rosario v2 | seq1 | 45.05 m | 1 |
| MAC-VO | Rosario v2 | seq1 | 13.28 m | 1 |

## License

This benchmarking framework (configs/, scripts/, docs/, results/) is released
under the MIT License — see [LICENSE](LICENSE).  
The three SLAM algorithms remain under their respective upstream licenses
(ORB-SLAM3: GPLv3, DROID-SLAM: BSD-3-Clause, MAC-VO: Apache-2.0).
