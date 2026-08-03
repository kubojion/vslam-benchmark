# vSLAM Benchmark

> Updated: 2026-08-03 - VO has 109 evaluated rows (incl. native ORB-SLAM3: EuRoC N=1, agri N=3
> median/range - non-deterministic, see PROGRESS finding 11); VO-LC has 24 (DPV-SLAM + OKVIS2 + OKVIS2-X across
> all 8 sequences); VIO has 55 (49-row core matrix plus six usable ZED2i trajectories); VIO-LC has 19
> (OKVIS2 + OKVIS2-X core, AirSLAM agricultural, ORB-SLAM3 seq5); GNSS-VIO has 20 N=1 headline runs.
> HortiMulti VIO uses corrected camera-IMU extrinsics, EuRoC MH_03/MH_05 and the local ZED2i field
> sequence are included, and the Rosario sequence5 PPK-versus-conventional study is retained. See
> [PROGRESS.md](PROGRESS.md) for limitations and current results.

| Algorithm | Type | Source |
|---|---|---|
| **ORB-SLAM3** | Classical feature-based, stereo / stereo-inertial, optional LC | [kubojion/ORB_SLAM3 @ vslam-benchmark-patches](https://github.com/kubojion/ORB_SLAM3/tree/vslam-benchmark-patches). Built + run natively (no Docker). VO filled: EuRoC N=1 (stable), agricultural N=3 median/range (severely non-deterministic — see PROGRESS finding 11). Old LC-on results quarantined in `obsolete/`. |
| **OKVIS2** | Sliding-window MAP stereo-inertial, optional DBoW + Sim3 LC | [ethz-mrl/okvis2](https://github.com/ethz-mrl/okvis2) (cmake build, system deps) |
| **OKVIS2-X** | Multi-sensor OKVIS2 extension; VO/VIO/VIO-LC/GNSS capability | [ethz-mrl/OKVIS2-X](https://github.com/ethz-mrl/OKVIS2-X) (cmake build, system deps). Wired in independently of OKVIS2: own source tree, configs, runner and results. |
| **MAC-VO** | Hybrid (learned uncertainty), stereo VO | [kubojion/MAC-VO @ vslam-benchmark-patches](https://github.com/kubojion/MAC-VO/tree/vslam-benchmark-patches) |
| **Basalt** | Optimization-based stereo VO / VIO | [VladyslavUsenko/basalt](https://gitlab.com/VladyslavUsenko/basalt) (binary install v0.1.7) |
| **AirSLAM** | Deep-feature point-line VO / VIO / V-SLAM (TRO 2025) | [sair-lab/AirSLAM](https://github.com/sair-lab/AirSLAM) (Docker, ROS Noetic + TensorRT) |
| **OV2SLAM** | Fully online feature/KLT stereo VO with BA and optional online-BoW LC | [ov2slam/ov2slam](https://github.com/ov2slam/ov2slam) (Docker, ROS 1 Noetic) |
| **OpenVINS** | MSCKF stereo-IMU filter (VIO only, no LC) | [rpng/open_vins](https://github.com/rpng/open_vins) (Docker, ROS 2 Humble) |
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
* **HortiMulti** - indoor strawberry polytunnel, stereo + IMU.
* **ZED2i `field1_110426_full_10fps_q90`** - the project's own agricultural field sequence, stereo + IMU + RTK position reference.
* **EuRoC-MAV** (MH_01_easy, MH_03_medium, MH_05_difficult) - [NON-AGRICULTURAL REFERENCE] indoor MAV flight, stereo + IMU. Used as a sanity check only.

Rosario v2, HortiMulti and the local ZED2i field sequence are the agricultural scope. A separate
GREENBOT dataset is not part of the current benchmark. EuRoC-MAV is tracked as a
[NON-AGRICULTURAL REFERENCE] and run once per algorithm to verify configs and the evaluation pipeline.
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
results-vo/          # vo runs           (no IMU, no LC, no GNSS)
results-vo-lc/       # vo-lc runs        (no IMU, LC on, no GNSS)
results-vio/         # vio runs          (IMU on, LC off, no GNSS)
results-vio-lc/      # vio-lc runs       (IMU on, LC on, no GNSS)
results-gnss-vio/    # gnss-vio runs     (IMU on, LC off, GNSS on)
benchmark-vo.csv     # aggregated metrics for vo runs
benchmark-vo-lc.csv  # aggregated metrics for vo-lc runs
benchmark-vio.csv    # aggregated metrics for vio runs
benchmark-vio-lc.csv # aggregated metrics for vio-lc runs
benchmark-gnss-vio.csv # aggregated metrics for gnss-vio runs
obsolete/            # quarantined data (e.g. ORB-SLAM3 stereo+LC runs that
                     # don't fit the current run-type scheme)
experiments/          # smoke/failed artifacts excluded from benchmark discovery
docs/                # public documentation (this file + 3 below)
PROGRESS.md          # running log of results and known issues
TODO.md              # authoritative open-work matrix
```

## Run-type abstraction

Every run is tagged with one of five `run_type`s. The tag controls
*both* the SLAM configuration that is launched *and* the on-disk
location of its output:

| run_type | IMU | Loop closure | GNSS | Results folder | Aggregated CSV |
|---|---|---|---|---|---|
| `vo` | off | off | off | `results-vo/` | `benchmark-vo.csv` |
| `vo-lc` | off | on | off | `results-vo-lc/` | `benchmark-vo-lc.csv` |
| `vio` | on | off | off | `results-vio/` | `benchmark-vio.csv` |
| `vio-lc` | on | on | off | `results-vio-lc/` | `benchmark-vio-lc.csv` |
| `gnss-vio` | on | off | on | `results-gnss-vio/` | `benchmark-gnss-vio.csv` |

Not every algorithm supports every run type. The runners reject or
warn for unsupported combinations:

| Algorithm   | `vo` | `vo-lc` | `vio` | `vio-lc` |
|-------------|------|---------|-------|----------|
| ORB-SLAM3   | yes (requires LC-off build) | yes | yes | yes |
| OKVIS2      | yes | yes (experimental) | yes | yes (IMU sigmas need 5-10x inflation, see PROGRESS.md) |
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

# Note: TODO.md lists small local-only AirSLAM/OpenVINS/OKVIS2 prerequisites
# that still need commits in their owning submodules before every runner is reproducible.

# 3. drop a dataset under datasets/<dataset>/<seq>/ and convert it
bash scripts/data/convert_rosario_to_tum.sh datasets/rosariov2/sequence1

# 4. run any algorithm 3x with full evaluation (default run_type=vo)
bash scripts/run/run_benchmark.sh rosariov2 sequence1 macvo 3

# 4b. same sequence as VIO (IMU on, LC off) - writes to results-vio/
bash scripts/run/run_benchmark.sh rosariov2 sequence1 basalt 3 vio

# 4c. AirSLAM full V-SLAM (IMU + LC) - writes to results-vio-lc/
bash scripts/run/run_benchmark.sh rosariov2 sequence1 airslam 3 vio-lc

# 4d. DPV-SLAM visual-only loop closure - writes to results-vo-lc/
bash scripts/run/run_benchmark.sh rosariov2 sequence1 dpvo 1 vo-lc

# 4e. CIFASIS GNSS-SI (stereo + IMU + GNSS) - writes to results-gnss-vio/
bash scripts/run/run_benchmark.sh rosariov2 sequence1 cifasis_gnss_si 3 gnss-vio

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

See [PROGRESS.md](PROGRESS.md) for full VO, VO-LC, VIO, VIO-LC and GNSS-VIO tables. The
`benchmark-*.csv` files are the source of truth for headline aggregates.

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

ZED2i field VO (N=1; the project's own agricultural field sequence, 46 k frames @ 1080p):

| Algorithm | ATE Sim(3) | Scale |
|---|---|---|
| ORB-SLAM3 | **0.256 m** | 0.992 |
| Basalt | 0.446 m | 0.990 |
| OKVIS2-X | 1.436 m | 0.990 |
| OKVIS2 | 3.372 m | 0.970 |
| AirSLAM | 3.866 m | 0.965 |

> ZED2i ground truth is derived from the RTK GNSS stream, so it is not independent of a GNSS
> input; these VO numbers use no GNSS and are position-only. MAC-VO on ZED2i (~6 h) is pending.
> OKVIS2/OKVIS2-X VO are best-effort (IMU disabled); they do far better here (weak-excitation
> stereo) than in their scale-collapsed ZED2i *VIO* runs.

> **ORB-SLAM3 agricultural/EuRoC VO** (rosariov2, hortimulti, EuRoC) is reported from the
> original native build (the numbers above). A Docker-ROS2 ORB-SLAM3 build available on this
> machine was found to diverge from the native build on hard agricultural sequences (e.g.
> hortimulti str02: 1.88 m native-ref 0.893 m, reproducibly 2.1x worse at 7 %% CV; rosariov2 seq1
> 6.8 +/- 3.8 m vs 1.18 m), so it is **not** mixed into the table — only its ZED2i result (0.256 m)
> is retained.

DPVO (monocular learned VO; replaces the dropped DROID-SLAM, N=1, Sim(3) ATE):

| Dataset | Seq | DPVO | DROID-SLAM | best stereo |
|---|---|---|---|---|
| Rosario v2 | seq5 | **3.92 m** | 50.02 m | 12.72 (AirSLAM) |
| Rosario v2 | seq1 | 4.93 m | 45.37 m | 1.18 (ORB-SLAM3) |
| ZED2i | field1 | 1.43 m | - | 0.256 (ORB-SLAM3) |
| HortiMulti | str03 | 1.82 m | 18.76 m | 0.104 (ORB-SLAM3) |
| HortiMulti | str02 | 14.59 m | 38.92 m | 0.893 (ORB-SLAM3) |
| EuRoC | MH_01/03/05 | 0.12 / 0.13 / 0.12 m | 4.08 / 3.52 / 6.59 m | - |

> DPVO is the standout on the **outdoor** agricultural data: on Rosario seq5 it beats every
> stereo method (monocular!), and on both Rosario sequences it improves ~9-13x over DROID-SLAM,
> the method it replaces. It is weaker on the long low-texture greenhouse traverse (str02) - the
> opposite failure profile from feature-based methods. Its loop-closure variant DPV-SLAM helps
> 2-3x on EuRoC but **hurts on every agricultural sequence** (false loops from repetitive crop
> rows -- see PROGRESS.md finding 10). It is **light**: ~2-4 GB VRAM even on the
> 46 k-frame ZED2i sequence, where MegaSaM and MASt3R-SLAM both OOM a 12 GB card. Monocular ->
> up-to-scale, so only Sim(3) ATE is comparable.

Representative VIO numbers (Phase 2, N=1 unless noted):

| Algorithm | Dataset | Seq | ATE Sim3 | N |
|---|---|---|---|---|
| ORB-SLAM3 | Rosario v2 | seq5 | **2.29 m** | 1 |
| ORB-SLAM3 | HortiMulti | strawberry03 | **0.396 m** | 1 |
| Basalt | Rosario v2 | seq5 | **4.74 m** | 1 |
| Basalt | HortiMulti | strawberry02 | **2.492 m** | 1 |
| Basalt | HortiMulti | strawberry03 | **0.194 m** | 1 |
| OKVIS2 | HortiMulti | strawberry02 | **2.145 m** | 1 |
| OKVIS2-X | HortiMulti | strawberry02 | **2.130 m** | 1 |
| OpenVINS | Rosario v2 | seq1 | 2.32 m | 1 |
| OpenVINS | EuRoC | MH_01_easy | 0.058 m | 1 |
| Voxel-SVIO | Rosario v2 | seq1 | 4.40 m | 1 |
| Voxel-SVIO | HortiMulti | strawberry02 | 5.83 m | 1 |

Representative GNSS-VIO numbers (N=1, all 16 runs; source `benchmark-gnss-vio.csv`):

| Algorithm | Dataset | Seq | ATE Sim3 | Scale | N |
|---|---|---|---|---|---|
| VINS-Fusion+GPS | Rosario v2 | seq1 | **1.188 m** | 1.006 | 1 |
| RTAB-Map+GPS | Rosario v2 | seq1 | 2.138 m | 1.019 | 1 |
| OpenVINS+GPS | Rosario v2 | seq1 | 2.388 m | 1.022 | 1 |
| CIFASIS GNSS-SI | Rosario v2 | seq1 | 3.583 m | 1.019 | 1 |
| VINS-Fusion+GPS | Rosario v2 | seq5 | **0.911 m** | 1.002 | 1 |
| CIFASIS GNSS-SI | Rosario v2 | seq5 | 2.062 m | 1.019 | 1 |
| OpenVINS+GPS | Rosario v2 | seq5 | 4.179 m | 1.013 | 1 |
| RTAB-Map+GPS | Rosario v2 | seq5 | 4.901 m | 1.011 | 1 |
| VINS-Fusion+GPS | HortiMulti | strawberry02 | **4.899 m** | 1.034 | 1 |
| RTAB-Map+GPS | HortiMulti | strawberry02 | 6.298 m | 1.043 | 1 |
| CIFASIS GNSS-SI | HortiMulti | strawberry02 | 7.256 m | 1.022 | 1 |
| OpenVINS+GPS | HortiMulti | strawberry02 | 30.865 m | 0.554 | 1 |
| CIFASIS GNSS-SI | HortiMulti | strawberry03 | **1.502 m** | 1.042 | 1 |
| RTAB-Map+GPS | HortiMulti | strawberry03 | 1.764 m | 1.027 | 1 |
| VINS-Fusion+GPS | HortiMulti | strawberry03 | 2.395 m | 1.033 | 1 |
| OpenVINS+GPS | HortiMulti | strawberry03 | 16.496 m | 0.165 | 1 |

GNSS fusion is the strongest track on the agricultural sequences: VINS-Fusion+GPS
wins three of the four, and every method except OpenVINS+GPS holds scale within
4% of metric. OpenVINS+GPS collapses on both HortiMulti sequences (scale 0.554
and 0.165) - the `robot_localization` filter never converges there, so those two
rows are failures rather than accuracy figures. Note the two Rosario sequences
use PPK-quality GPS; see PROGRESS.md for the GPS-quality study (measured PPK vs
conventional) and the vertical-noise investigation.

All seven VIO algorithms now have corrected-extrinsic N=1 results on both HortiMulti sequences,
with scale near 1. The older vibration-floor/algorithm-limit conclusion was invalidated by applying
the rectification rotation and correcting transform direction. These are provisional validation
runs; N=3 repeatability remains pending. See [PROGRESS.md](PROGRESS.md) for the controlled evidence.

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
DROID-SLAM: BSD-3-Clause, MASt3R-SLAM: CC-BY-NC-SA-4.0, OKVIS2-X: BSD-3-Clause).
