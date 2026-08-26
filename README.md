# vSLAM Benchmark

> **Updated 2026-08-06.** 259 runs (VO 110 / VO-LC 40 / VIO 55 / VIO-LC 28 / GNSS-VIO 26) across
> Rosario v2, HortiMulti, the own ZED2i field sequence and EuRoC (control), all at
> `eval_schema: 2` — the 2026-08-05 evaluation overhaul (fixed GT interpolation, gap-aware
> coverage, SE3-primary metrics, origin-aligned GNSS ATE, GT + machine provenance per run) —
> verified byte-reproducible across both benchmark machines. Results: see
> [docs/generated/tables.md](docs/generated/tables.md) (never hand-transcribed); status + open
> work: [TODO.md](TODO.md); narrative + findings 1–15: [PROGRESS.md](PROGRESS.md); next
> milestone: the **N=5 server campaign**
> ([docs/campaigns/server-campaign-plan.md](docs/campaigns/server-campaign-plan.md)).

| Algorithm | Type | Source |
|---|---|---|
| **ORB-SLAM3** | Classical feature-based, stereo / stereo-inertial, optional LC | [kubojion/ORB_SLAM3 @ vslam-benchmark-patches](https://github.com/kubojion/ORB_SLAM3/tree/vslam-benchmark-patches). Built + run natively (no Docker). VO filled: EuRoC N=1 (stable), agricultural N=3 median/range (severely non-deterministic — see PROGRESS finding 11). Old LC-on results quarantined in `obsolete/`. |
| **OKVIS2** | Sliding-window MAP stereo-inertial, optional DBoW + Sim3 LC | [ethz-mrl/okvis2](https://github.com/ethz-mrl/okvis2) (cmake build, system deps) |
| **OKVIS2-X** | Multi-sensor OKVIS2 extension; VO/VIO/VIO-LC/GNSS capability | [ethz-mrl/OKVIS2-X](https://github.com/ethz-mrl/OKVIS2-X) (cmake build, system deps). Wired in independently of OKVIS2: own source tree, configs, runner and results. |
| **MAC-VO** | Hybrid (learned uncertainty), stereo VO | [kubojion/MAC-VO @ vslam-benchmark-patches](https://github.com/kubojion/MAC-VO/tree/vslam-benchmark-patches) |
| **Basalt** | Optimization-based stereo VO / VIO | [VladyslavUsenko/basalt](https://gitlab.com/VladyslavUsenko/basalt) (binary install v0.1.7) |
| **AirSLAM** | Deep-feature point-line VO / VIO / V-SLAM (TRO 2025) | [kubojion/AirSLAM @ vslam-benchmark-patches](https://github.com/kubojion/AirSLAM/tree/vslam-benchmark-patches) (Docker, ROS Noetic + TensorRT; fork carries the VIO launch files) |
| **OV2SLAM** | Fully online feature/KLT stereo VO with BA and optional online-BoW LC | [ov2slam/ov2slam](https://github.com/ov2slam/ov2slam) (Docker, ROS 1 Noetic) |
| **OpenVINS** | MSCKF stereo-IMU filter (VIO only, no LC) | [kubojion/open_vins @ vslam-benchmark-patches](https://github.com/kubojion/open_vins/tree/vslam-benchmark-patches) (Docker, ROS 2 Humble; fork carries Dockerfile.benchmark) |
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
* [docs/result-storage-design.md](docs/result-storage-design.md) - result replacement, completeness, manifest, and browser behavior.
* [PROGRESS.md](PROGRESS.md) - current results tables (VO / VIO / VIO-LC), known issues, dataset-specific notes.

## Results snapshot

**Published source of truth:** the five tracked `benchmark-*.csv` files (rebuilt from complete runs under `results/`, one row
per run, `eval_schema: 2`). **The only sanctioned rendering** is
[docs/generated/tables.md](docs/generated/tables.md) — regenerate with
`python3 scripts/eval/make_report_tables.py` (SE3-primary, coverage-gated, machine-checkable
bolding). Numbers for prose come from
[docs/generated/verified-claims.md](docs/generated/verified-claims.md); report figures live in
[docs/generated/figures/](docs/generated/figures/). Never hand-transcribe a results number.

Current state (2026-08-06): 259 runs across VO / VO-LC / VIO / VIO-LC / GNSS-VIO on
Rosario v2, HortiMulti, the ZED2i field sequence, and EuRoC (control). All runs carry GT
provenance (sha256) and run-host machine identity; CSVs are byte-reproducible on any clone.
Most cells are N=1 — the **N=5 server campaign**
([docs/campaigns/server-campaign-plan.md](docs/campaigns/server-campaign-plan.md)) is the next
milestone; cells marked 🔁 in [TODO.md](TODO.md) additionally need a config-fairness A/B first.

Headline findings (stated with their caveats in [PROGRESS.md](PROGRESS.md) findings 1–15):
loop-closure benefit on crops is mechanism- and revisit-dependent (finding 15); the IMU's value
is excitation-dependent — helps on Rosario, collapses on the constant-velocity ZED2i field run
(finding 13, calibration confounds still open); ORB-SLAM3's low agricultural VO ATE is a
partial-coverage artifact (finding 14); GNSS fusion bounds error outdoors but the loose-vs-tight
comparison is on hold pending the 🔁 re-runs.

## License

This benchmarking framework (configs/, scripts/, docs/, results/) is released
under the MIT License - see [LICENSE](LICENSE).
The SLAM algorithms remain under their respective upstream licenses
(ORB-SLAM3: GPLv3, MAC-VO: Apache-2.0, AirSLAM: GPL-3.0, OpenVINS: GPL-3.0,
DROID-SLAM: BSD-3-Clause, MASt3R-SLAM: CC-BY-NC-SA-4.0, OKVIS2-X: BSD-3-Clause).
