# vSLAM Benchmark - TODO

> Created: 2026-05-20 | Revised: 2026-07-21. VO has 67 evaluated rows. The core VIO N=1
> matrix has 49 rows (7 algorithms x 7 standard sequences); corrected HortiMulti extrinsics and
> EuRoC MH_03/MH_05 are included. ZED2i adds six usable VIO trajectories plus one failed
> ORB-SLAM3 attempt, so `benchmark-vio.csv` has 55 rows. VIO-LC has 3 rows. GNSS-VIO N=1 is
> complete: 16 headline runs (4 algorithms x 4 GPS-bearing sequences), including the retained
> sequence5 PPK-versus-conventional study. Remaining priorities are N=3 validation, corrected-
> extrinsic OpenVINS+GPS HortiMulti reruns and evaluator hardening. OKVIS2-X automation is now
> committed (build script, runner, GPS converter), so its remaining gaps are runs, not tooling.

---

## Status legend

`[x]` done  `[ ]` not started  `[~]` in-progress / partially done  `[!]` blocked

---

## Run combinations matrix

Legend per cell: **done-N3** = 3 runs evaluated and aggregated | **done-N1** = 1 run evaluated
**ready** = config + data exist, not yet run | **no-imu** = imu0 not extracted (blocker)
**no-config** = config not written | **no-mode** = algorithm does not support this mode

### VO (no IMU, no loop closure) - `results-vo/`

Legend: ✅ successful run (N=x) | 🟡 completed with errors/scale collapse/divergence | ⬜ ready (config+data exist) | 🔧 no-config | ➖ no-mode (unsupported)

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | ⬜ ready | ✅ N=1 | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ✅ N=1 |
| Basalt | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 |
| MAC-VO | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🔧 no-config |
| AirSLAM | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🔧 no-config |
| DROID-SLAM | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ⬜ config only |
| OKVIS2 | ✅ N=1 | ✅ N=1 | 🔧 no-config | 🔧 no-config | 🔧 no-config | 🔧 no-config | 🔧 no-config | 🔧 no-config |
| OKVIS2-X | ✅ N=1 | ✅ N=1 | ⬜ config only | ⬜ config only | ⬜ config only | ⬜ config only | ⬜ config only | 🔧 no-config |
| MASt3R-SLAM | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | 🔧 no-config |
| MegaSaM | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | 🔧 no-config |

> ORB-SLAM3 VO = LC-off mode required (`LoopClosing: 0` or dedicated build). Old LC-on results are in `obsolete/`.
> **zed2i field1** = local ZED2i field dataset (46283 pairs, 1080p, 77 min, RTK GT). Under the
> tested N=1 configurations, ORB-SLAM3 VO (0.256 m) and Basalt VO (0.446 m) outperformed every
> VIO attempt. The evidence is consistent with weak inertial excitation, but the exact factory
> camera-IMU transform and timing still need controlled validation.

### VIO (stereo + IMU, no loop closure) - `results-vio/`

Legend: ✅ successful run (N=x) | 🟡 completed with errors/scale collapse/divergence | ⬜ ready (config+data exist) | 🔧 no-config | ➖ no-mode (unsupported)

All core agricultural/EuRoC cells have N=1 results as of 2026-07-21. HortiMulti was corrected via
the camera-IMU extrinsic fix and no scale-collapsed core cells remain. ZED2i has six usable VIO
trajectories plus one ORB-SLAM3 failed attempt; every tested VIO configuration underperformed the
two VO baselines. Next step for the core table is N=1 -> N=3.

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 failed attempt (no trajectory) |
| Basalt | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 N=1 (9.14 m, VIO<VO) |
| OKVIS2 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 N=1 (scale collapse, 17.7 m) |
| OKVIS2-X | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 N=1 (scale collapse, 18.3 m) |
| OpenVINS | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 N=1 (scale collapse, 5.33 m) |
| AirSLAM | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 N=1 (3.90 m, no collapse, VIO<VO) |
| Voxel-SVIO | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 N=1 (3.71 m, no collapse, VIO<VO; ~71 s init delay) |

> HortiMulti IMU: extracted - str02=190493 samples, str03=48448 samples. Path: `datasets/hortimulti/strawberry{02,03}/mav0/imu0/data.csv`
> **HortiMulti VIO fix (2026-07-20):** the dominant cross-algorithm configuration error was a
> wrong camera-IMU extrinsic (raw fisheye extrinsic used on rectified images = missing 1.22 deg rotation;
> OKVIS2/OKVIS2-X/AirSLAM additionally had it inverted). Corrected in configs - scale now ~1.0
> everywhere. See PROGRESS.md.
> Voxel-SVIO: VIO-only (no VO, no LC). Runs via Docker (`vslam_voxel_svio:noetic`). Wrapper had a
> `pkill` self-match bug (fixed) that reported "no trajectory" on successful runs; it is also
> non-deterministic (real-time player) - ~2x run-to-run spread, so N=3 matters here especially.
> OKVIS2 (standalone) was built 2026-07-20 (`build_okvis2.sh`, needed -DHAVE_LIBREALSENSE=OFF
> -DUSE_CUDA=OFF).
> **zed2i field1 VIO (all 7 algorithms attempted, 2026-07-21):** under the tested N=1
> configurations, all usable VIO trajectories underperform the two VO baselines:
> - **No collapse, but VIO≫VO:** Voxel-SVIO 3.71 m (scale 0.978, ~71 s static-init delay -
>   its log spams "Failed static init: no accel jerk detected" until the first real motion),
>   AirSLAM 3.90 m (scale 0.965), Basalt 9.14 m (scale 0.816). All track cleanly but land
>   ~15-35× worse than VO (ORB-SLAM3 VO 0.256 m, Basalt VO 0.446 m).
> - **Scale collapse (evo Sim3 scale ≈ 0, SE3 ATE explodes to 10^5-10^6 m):** OpenVINS 5.33 m
>   (only 8.7 % tracked), OKVIS2 17.7 m, OKVIS2-X 18.3 m - the tightly-coupled filters.
> - **ORB-SLAM3:** VIO tracking is chronically unstable (repeated "Fail to track local map!")
>   and the committed attempt **segfaults in SaveTrajectoryEuRoC at export** -
>   no usable trajectory. Config authored (`zed2i_field1_..._stereo_inertial.yaml`, identity T_b_c1).
> The pattern is consistent with insufficient rotational excitation (mean |gyro| 4.7 deg/s), but
> it is not yet a proven shared root cause: the runs are N=1 and share calibration/timing assumptions.
> Apply the exact factory camera-IMU transform and validate timing before deciding whether N=3 is useful.

### VIO-LC (stereo + IMU + loop closure) - `results-vio-lc/`

Legend: ✅ successful run (N=x) | 🟡 completed with errors/scale collapse/divergence | ⬜ ready (config+data exist) | 🔧 no-config | ➖ no-mode (unsupported)

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 |
|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | ⬜ ready | ✅ N=1 | ⬜ ready | ⬜ ready | 🔧 no-config | 🔧 no-config | 🔧 no-config |
| OKVIS2 | ✅ N=1 | ✅ N=1 | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready |
| OKVIS2-X | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready |
| AirSLAM (VI-SLAM) | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready |
| MASt3R-SLAM (LC-on) | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready | ⬜ ready |

> MASt3R-SLAM in `vio-lc` = monocular + LC-on (no IMU; bucket reused for its only real mode).
> HortiMulti IMU: extracted. Path: `datasets/hortimulti/strawberry{02,03}/mav0/imu0/data.csv`

### GNSS-VIO (stereo + IMU + GNSS) - `results-gnss-vio/`

Legend: ✅ successful run (N=x) | 🟡 completed but needs validation/rerun | ⬜ ready | 🔧 automation missing

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 |
|---|---|---|---|---|
| CIFASIS GNSS-SI | ✅ N=1 | ✅ N=1 (PPK) | ✅ N=1 | ✅ N=1 |
| RTAB-Map | ✅ N=1 | 🟡 N=1 (PPK; nondeterministic/partial) | ✅ N=1 | ✅ N=1 |
| VINS-Fusion | ✅ N=1 | ✅ N=1 (PPK) | ✅ N=1 | ✅ N=1 |
| OpenVINS+GPS (robot_localization) | 🟡 N=1 (validate) | 🟡 N=1 PPK (validate) | 🟡 N=1 (pre-extrinsic-fix) | 🟡 N=1 (pre-extrinsic-fix) |

> EuRoC-MAV is **not** part of the gnss-vio track (no GPS in the dataset).
> Runners: `run_cifasis_gnss_si.sh`, `run_rtabmap_gps.sh`, `run_vins_fusion_gps.sh`, `run_openvins_gps.sh` (all accept `<dataset> <seq> [run_id] gnss-vio`).
>
> OKVIS2-X is not one of these 16 runs. Build script, runner and GPS converter are now
> committed and its Rosario GNSS configs exist, so seq1/seq5 are ready to run; HortiMulti
> GNSS configs are still absent.
> Use `run_benchmark.sh <dataset> <seq> <algo> <N> gnss-vio` to run + evaluate automatically.
>
> **GPS quality:** rosariov2 **seq5 now uses high-quality PPK GPS** (`/reach_1/ppk/fix`, vertical RMSE
> ~0.12 m vs ~1.44 m conventional); the seq5 GNSS-VIO results above are PPK. **seq1 still uses
> conventional GPS** - no seq1 PPK log is available locally, so seq1 has NOT been re-run on PPK (do not
> confuse the two). PPK upgrade improved vertical RMSE -23% to -86% and overall ATE for the
> loosely-coupled estimators (VINS-Fusion, OpenVINS); CIFASIS vertical improved but overall ATE rose
> (horizontal re-balance); RTAB-Map inconclusive (odometry non-determinism), hence 🟡. HortiMulti has
> **no** higher-grade GPS available (only consumer `/antobot_gps`, status=0, vertical sigma 6.5-7.7 m),
> so its vertical error is a hardware limit. See `PROGRESS.md` GNSS-VIO GPS-quality study +
> `scripts/eval/_gps_noise_analysis.py`.
>
> **Remaining:** re-run seq1 on PPK if/when the seq1 PPK log becomes available.

---

## High-priority open tasks (Phase 2)

| # | Task | Status |
|---|---|---|
| 1 | Extract HortiMulti IMU (`/ms/imu/data` -> `mav0/imu0/data.csv`) | `[x]` |
| 2 | Run core VIO N=1 matrix | `[x]` 49 rows (7 algorithms x 7 standard sequences); ZED2i adds 6 usable rows + 1 failed attempt |
| 3 | Diagnose and fix hortimulti VIO scale collapse | `[x]` **root cause was a camera-IMU EXTRINSIC bug, NOT vibration** (the earlier "vibration floor" conclusion was wrong). Fixed in config; all algos scale ~1.0. See PROGRESS.md "RESOLVED". |
| 3b | Build OKVIS2 standalone (was never built) | `[x]` (`build_okvis2.sh`; -DHAVE_LIBREALSENSE=OFF -DUSE_CUDA=OFF) |
| 3c | Re-run 2 stale bad VIO runs (Voxel EuRoC, OpenVINS seq5) | `[x]` (were bad runs, not algorithm limits) |
| 3d | Add EuRoC MH_03/MH_05 VIO coverage + fix EuRoC times.txt (s->ns) | `[x]` |
| 4 | Run ORB-SLAM3 VIO on rosariov2/seq1 N=3 | `[ ]` |
| 5 | Run Basalt VIO on rosariov2/seq1 N=3 | `[ ]` |
| 6 | Run OpenVINS VIO on rosariov2/seq5 N=3 | `[~]` N=1 re-run done (10.76 m); needs N=3 |
| 7 | Download MASt3R-SLAM weights; smoke test on EuRoC; then agri datasets N=3 | `[ ]` |
| 8 | ORB-SLAM3 VO-clean: enable LC-off mode and re-run rosariov2/seq1+hortimulti/EuRoC | `[ ]` |
| 9 | **Scale all N=1 VIO results to N=3** (biggest remaining item; OpenVINS + Voxel-SVIO are load-sensitive - run unloaded) | `[ ]` |
| 10 | Complete GNSS-VIO N=1 sweep | `[x]` 16 headline runs (4 algorithms x 4 sequences); N=3 still pending |
| 10b | Re-run OpenVINS+GPS HortiMulti with corrected extrinsics; validate all four rows | `[ ]` |
| 11 | Normalize EuRoC dataset aliases and result/config paths to `euroc_mav` | `[x]` central shell/Python canonicalization; obsolete aliases removed |
| 12 | Commit local-only runtime prerequisites in their owning submodules/forks | `[!]` AirSLAM VIO launch files, OpenVINS `Dockerfile.benchmark`, OKVIS2 DBoW2/opengv CMake patches |

---

## Phase 2 per-algorithm tasks

### ORB-SLAM3

| Task | Status |
|---|---|
| VO-clean (LC-off) on rosariov2/seq1 N=3 | `[ ]` |
| VO-clean on hortimulti str02+03 N=3 | `[ ]` |
| VO-clean on EuRoC MH_01/03/05 N=1 | `[ ]` |
| VIO rosariov2/seq1 N=3 | `[ ]` |
| VIO-LC rosariov2/seq1 N=3 | `[ ]` |
| VIO EuRoC MH_01/03/05 N=1 | `[x]`; N=3 pending |
| VIO-LC EuRoC N=1 | `[ ]` |

### Basalt

| Task | Status |
|---|---|
| VIO rosariov2/seq1 N=3 | `[ ]` |
| VIO EuRoC MH_01/03/05 N=1 | `[x]`; N=3 pending |
| VIO hortimulti (after IMU extraction) | `[x]` |
| hortimulti VIO scale collapse | `[x]` **FIXED via extrinsic correction** (was misdiagnosed as vibration floor; the 5-run noise sweep searched the wrong parameter). With rectified T_imu_cam: str02 22.9->2.49 m, str03 2.85->0.19 m, scale 0.57->1.03. |

### OpenVINS

| Task | Status |
|---|---|
| VIO rosariov2/seq5 N=3 | `[ ]` |
| VIO EuRoC MH_01/03/05 N=1 | `[x]`; N=3 pending |
| VIO hortimulti (after IMU extraction) | `[x]` |

### AirSLAM

| Task | Status |
|---|---|
| VIO rosariov2/seq1+seq5 N=3 | `[ ]` |
| VI-SLAM (VIO-LC) rosariov2 N=3 | `[ ]` |
| VIO/VI-SLAM hortimulti (after IMU extraction) | `[x]` |
| VIO EuRoC MH_01/03/05 N=1 | `[x]`; N=3 pending |
| hortimulti str02/str03 scale collapse | `[x]` **FIXED**: extrinsic was inverted AND missing rectification. str02 46.3->5.30 m, str03 16.3->1.24 m, scale ~1.0. (Also recovered lost `vio_euroc.launch`; TensorRT needed a host reboot after a driver update.) |

### OKVIS2

| Task | Status |
|---|---|
| Scale seq1+seq5 to N=3 | `[ ]` |
| Add hortimulti + EuRoC configs | `[x]` |
| VIO EuRoC MH_01/03/05 N=1 | `[x]`; N=3 pending |
| hortimulti failure | `[x]` **FIXED via extrinsic correction** (the tracking failures were largely self-inflicted by the wrong extrinsic, not greenhouse texture). str02 49.9->2.14 m, str03 15.5->0.40 m, scale 0->1.03. Independent check: freshly-built binary + config patched hours earlier. |

### OKVIS2-X

Source and result integration exists independently of OKVIS2. The top-level build, run and
GPS-conversion automation is now committed; the existing VO/VIO result artifacts predate it and
came from manual runs, so they have not yet been reproduced through the runner.

| Task | Status |
|---|---|
| Source submodule/gitlink pinned (`src/okvis2x`) | `[x]` |
| Reproducible top-level build script (`build_okvis2x.sh`) | `[x]` |
| Top-level multi-mode runner (`run_okvis2x.sh`) | `[x]` (all four run types; `OKVIS2X_CONFIG` override for sweeps) |
| Configs for rosariov2 / EuRoC / HortiMulti / ZED2i | `[x]` (27 committed files) |
| gnss-vio configs (rosariov2 seq1+seq5) | `[x]` |
| `gps.csv` -> `mav0/gps0/data_raw.csv` converter | `[x]` |
| Register in eval pipeline (LOG_PATTERNS, plot dicts) | `[x]` |
| Measure `r_SA` (GNSS antenna lever arm) on the robot | `[ ]` (configs currently assume `[0,0,0]`) |
| First gnss-vio runs (rosariov2 seq1+seq5) | `[ ]` |
| Reproduce VO/VIO results through `run_okvis2x.sh` | `[ ]` (current artifacts are manual) |
| Manual N=1 VIO results | `[x]` all 7 core sequences plus ZED2i (see VIO matrix); N=3 pending |
| Recover HortiMulti IMU + GPS from hortimulti.zip | `[x]` (str02 190493/7620, str03 48448/1939 - counts match bag) |
| HortiMulti gnss_vio configs | `[ ]` (GPS recovered for both sequences, so unblocked) |
| Head-to-head OKVIS2 vs OKVIS2-X on rosariov2 vio | `[x]` seq1: OKVIS2 18.89 / OKVIS2-X 18.89; seq5: 20.29 / 20.40 - near-identical (shared estimator core) |

### MASt3R-SLAM

| Task | Status |
|---|---|
| Download checkpoints | `[ ]` |
| Smoke test EuRoC MH_01 | `[ ]` |
| VO mode rosariov2/seq1+seq5, hortimulti str02+03 N=3 | `[ ]` |
| VIO-LC mode (LC-on) same sequences N=3 | `[ ]` |

### DPVO / DPV-SLAM (replaces DROID-SLAM)

Removed from active tracking - not set up in repo. See Dropped section below.

### Voxel-SVIO

| Task | Status |
|---|---|
| Docker image + container build (`scripts/setup/setup_voxel_svio_docker.sh`) | `[x]` (NOTE: setup guard skips clone if `src/voxel_svio/` exists even when empty - source must actually be present) |
| Configs: euroc_mav (per-seq), rosariov2, hortimulti | `[x]` |
| Run script (`scripts/run/run_voxel_svio.sh`) + ROS1 data player | `[x]` |
| Smoke test EuRoC MH_01_easy N=1 | `[x]` (0.083 m; earlier 3.03 m row was a stale bad run) |
| VIO rosariov2/seq1+seq5 N=3 | `[ ]` |
| VIO hortimulti str02+str03 N=3 | `[ ]` |
| VIO EuRoC MH_01/03/05 N=1 -> N=3 | `[ ]` |

---

## Aggregation and reporting

| Task | Status |
|---|---|
| Rebuild `benchmark-vo.csv` after ORB-SLAM3 VO-clean results land | `[ ]` |
| Rebuild `benchmark-vio.csv` after N=3 runs (Basalt/ORB-SLAM3/OpenVINS) | `[ ]` |
| Add MASt3R-SLAM to applicable CSVs | `[ ]` |
| Generate segment maps for all new Phase 2 sequences | `[ ]` |
| Final cross-algo ATE plots (VO vs VIO per sequence) | `[ ]` |
| Thesis-ready LaTeX table | `[ ]` |

---

## Dropped / out of scope

| Algorithm | Reason |
|---|---|
| DROID-SLAM | "Bulky, old, requires tons of resources" (supervisor). N=3 results kept in `results-vo/` as historical reference. |
| DPVO / DPV-SLAM | Not set up in repo; removed from active tracking. |
| Stella-VSLAM | "Mostly reimplementation of ORB-SLAM3, adds nothing" (supervisor). |
| VINS-Fusion | Overlaps Basalt + OpenVINS; ROS1 only. |
| SVO Pro Open | ROS1 Melodic only; frozen toolchain. |
| DSO / Stereo-DSO | Misaligned with stereo-IMU direction. |
| cuVSLAM | Closed-source (NVIDIA). Cite KITTI numbers only. |
| Kimera-VIO | Overlaps OpenVINS. |
| MegaSaM | Lower priority than MASt3R-SLAM and DPVO; keep as optional. |

---

## Adding a new algorithm

1. Build / containerize under `src/<algo>/`.
2. Write `scripts/run/run_<algo>.sh` with signature `<dataset> <seq> [run_id=1] [run_type=vo]`.
3. Write config(s) under `configs/<algo>/`.
4. Add a row to each table above.
5. Smoke-test on EuRoC MH_01_easy first.

## Adding a new dataset

1. Write extraction script in `scripts/data/`.
2. Create `docs/private/dataset-specific/dataset_<name>.md`.
3. Extract to `datasets/<name>/<seq>/mav0/` with standard layout.
4. Add a column to each table above.

---

## DONE (Phase 1 - VO benchmark)

All Phase 1 VO runs are complete (N=3) and evaluated. See PROGRESS.md Phase 1 for the full
results table. Summary:

- ORB-SLAM3 (LC-on): rosariov2 seq1+seq5, hortimulti str02+str03 - results in `obsolete/` (LC-on confound)
- Basalt VO: all agri + EuRoC - done-N3 / done-N1
- MAC-VO: all agri + EuRoC - done-N3 / done-N1
- AirSLAM VO: all agri + EuRoC - done-N3 / done-N1
- DROID-SLAM: all agri + EuRoC - done-N3 / done-N1
- OKVIS2 VO: rosariov2/seq1+seq5 - done-N1

Kept as Phase 2 restructure (Phase 4.5):
- [ ] Rebuild ORB-SLAM3 with loop closure disabled (or wire up the
      stereo-inertial example) so it slots back into `vo` / `vio` / `vio-lc`.
- [ ] Re-run AirSLAM with `run_type=vio` and `vio-lc` on Rosario v2 and
      HortiMulti once `mav0/imu0/data.csv` is available for both datasets.
- [ ] Re-run Basalt with `run_type=vio` on Rosario v2 and HortiMulti.
- [ ] Extract IMU streams: HortiMulti needs `mav0/imu0/data.csv` from the
      `/ms/imu/data` topic (`scripts/data/_hortimulti_extract.py`).
      Rosario v2 needs the same generated from its `imu.csv`.
- [ ] Download MegaSaM checkpoints, run on EuRoC sanity sequence, then on
      Rosario / HortiMulti (`run_type=vo`).
- [ ] Download MASt3R-SLAM checkpoints, run on EuRoC sanity sequence, then
      on the agricultural sequences (`run_type=vo` and `vio-lc`).
- [ ] Add a `vio_slam` ORB-SLAM3 binary path and configs once the build
      lands.

## How to read this file

- `[x]` = done   `[ ]` = pending   `[~]` = partially done / blocked
- Sections are organised by **dataset → algorithm**; add new blocks using the
  same template when extending to more algorithms or datasets.
- The **cross-algorithm comparison** section at the bottom is filled after
  every algorithm on a dataset is complete.

---

## Standard vSLAM benchmarking pipeline (reference)

The community-standard evaluation workflow (Sturm 2012, TUM RGB-D; Geiger 2012,
KITTI; Grupp 2017, evo) has the following stages:

1. **Data prep** — extract bag → EuRoC layout (`cam0/`, `cam1/`, `times.txt`),
   create `gt_tum.txt` in TUM format (timestamp tx ty tz qx qy qz qw, seconds).
2. **Algorithm config** — write a correctly-named YAML config file for each
   (algorithm, dataset) pair; verify all required parameters are present.
3. **Run** — execute the algorithm, capture trajectory + runtime metadata
   (FPS, peak GPU MB); save to `results/<dataset>/<seq>/<algo>/`.
4. **Timestamp normalisation** — ensure all estimated trajectories use
   second-epoch timestamps matching the GT file's epoch.
5. **ATE / APE** (`evo_ape`) — absolute trajectory error after rigid SE(3)
   alignment; primary global accuracy metric.  Report RMSE and mean.
6. **RPE** (`evo_rpe`) — relative pose error over a fixed window (~1 s);
   measures local drift.  Report RMSE of translational and rotational error.
7. **Completion rate** — `N_estimated / N_total × 100 %`; captures how often
   the system loses tracking.
8. **Runtime metrics** — wall-clock FPS, peak GPU memory, CPU usage.
9. **Multi-run benchmark** — run algorithm N times (N=3); `run_orbslam3.sh <dataset> <seq> <run_id>`.
10. **Per-run evaluation** — `scripts/eval/_evaluate_run.py <dataset> <seq> <algo> <run_id>` → `run_eval.json`.
11. **Aggregate runs** — `scripts/eval/_aggregate_runs.py <dataset> <seq> <algo>` → `metrics.csv`, `report.md`.
12. **Segment visualisation** — `scripts/eval/_plot_segments.py <dataset> <seq>` → `segment_map.png`.

---

## Phase 0 – Infrastructure

| Task | Status |
|---|---|
| Clone + build ORB-SLAM3 (UZH upstream) | `[x]` |
| Patch ORB-SLAM3 for C++14 (sigslot) | `[x]` |
| Fix ORB-SLAM3 `Rectified` null-ptr bug (`Settings.cc`) | `[x]` |
| Build Pangolin v0.9.5 | `[x]` |
| Install `evo` evaluation toolkit | `[x]` |
| Script layout: `build/`, `data/`, `run/`, `eval/` | `[x]` |
| `run_orbslam3.sh` — multi-run with resource monitoring | `[x]` |
| `_resource_monitor.py` — GPU+CPU+RAM every 1s | `[x]` |
| `_interpolate_gt.py` — sparse GT → camera timestamps (Slerp) | `[x]` |
| `_segment_trajectory.py` — **v2: 2 m sliding-window path-length, 10° heading / 20 cm chord deviation** | `[x]` |
| `_evaluate_run.py` — full per-run evaluation (ATE Sim3 + **SE3**) → `run_eval.json` | `[x]` |
| `_aggregate_runs.py` — N runs → `metrics.csv` + `report.md` (Sim3 + SE3 columns) | `[x]` |
| `_plot_segments.py` — **8 K segment map, 3 hierarchies (per-run, per-algo, cross-algo)** | `[x]` |
| `run_benchmark.sh` — one-shot pipeline: run N times + interpolate GT + segment + evaluate + aggregate | `[x]` |
| RPE metric: use `point_distance` not `trans_part` (frame mismatch fix) | `[x]` |
| **Sim(3) vs SE(3) reporting**: both alignments computed every run | `[x]` |
| **Body↔camera mount mismatch documented** (Strawberry-03 RPE rot artefact) | `[x]` |
| `run_droidslam.sh` / `run_macvo.sh` upgraded to **multi-run framework** (`<run_id>` arg, `_resource_monitor.py`) | `[x]` |
| DROID-SLAM conda env (`droidenv`) | `[x]` | lietorch, torch_scatter, droid_backends all built |
| MAC-VO conda env | `[x]` | `macvo` env created; models downloaded |
| **Basalt binary install** (`~/.local/bin/basalt_vio`, v0.1.7) | `[x]` | Binary installer for Ubuntu 22.04; sources `~/.basalt/env` |
| `run_basalt.sh` | `[x]` | EuRoC format, auto-generates `mav0/cam*/data.csv`, `--use-imu false` |
| `configs/basalt/hortimulti_calib.json` + `rosariov2_calib.json` + `vo_config.json` | `[x]` | Pinhole + `vio_min_triangulation_dist: 0.03` |
| **AirSLAM Docker** (`air_slam` container, `xukuanhit/air_slam:v4`) | `[x]` | Docker Engine + nvidia-container-toolkit; catkin_make inside container |
| `scripts/setup/setup_airslam_docker.sh` | `[x]` | One-shot pull + create + build |
| `run_airslam.sh` | `[x]` | Polls `trajectory_v0.txt`, `pkill roslaunch`, `mv -f`, FPS from input frames |
| `configs/airslam/{hortimulti,rosariov2}_{camera,vo}.yaml` | `[x]` | Per-dataset intrinsics + TRT engine name |

---

## Phase 1 – Dataset: Rosario v2

> Agricultural field rows, stereo + GPS GT, 15 fps, 1280×720.
> Full sequence 1 = 13 821 frames, ~18 min.
> Official evaluation: https://github.com/CIFASIS/rosariov2

### 1-A  Data preparation

| Task | Status |
|---|---|
| `scripts/data/convert_rosario_to_tum.sh` — OOM-safe streaming extractor | `[x]` |
| Extract sequence 1 (13 821 frames) | `[x]` |
| `gt_tum.txt` present (GPS PGT, second-epoch timestamps) | `[x]` |
| Extract sequence 5 (11 640 frames) | `[x]` |
| Extract sequences 2–4 (if needed) | `[ ]` |

### 1-B  ORB-SLAM3

| Task | Status | Notes |
|---|---|---|
| Config `configs/orbslam3/rosariov2_stereo.yaml` | `[x]` | Rectified, fx=648.86 |
| Run full sequence 1 (single, old format) | `[x]` | 13 821 frames, 12.55 fps, 1101 s |
| ATE on sequence 1 (old single run) | `[x]` | **RMSE 1.361 m**, mean 1.311 m |
| RPE (15-frame window) on sequence 1 | `[x]` | trans RMSE **0.115 m**, rot RMSE **3.56 °** |
| Interpolate GT for seq1 (`gt_interp_tum.txt`) | `[x]` | 13821 poses at camera timestamps |
| Auto-segment seq1 (`segments_auto.csv`) | `[x]` | 145 segs: 125 row (863 s), 20 turn (60 s) |
| **Run seq1 × 3 (multi-run benchmark)** | `[x]` | ATE 1.176 ± 0.317 m, 100%, 5-6 loops |
| **Evaluate + aggregate seq1 × 3** | `[x]` | `metrics.csv` + `report.md` + `segment_map.png` done |
| Run sequence 5 (single, old format) | `[x]` | 11 640 frames, 11.55 fps, 1008 s, 100% completion |
| Evaluate sequence 5 (old single run) | `[x]` | **ATE RMSE 8.274 m** (Sim3 alignment) |
| Interpolate GT for seq5 (`gt_interp_tum.txt`) | `[x]` | 11640 poses at camera timestamps |
| Auto-segment seq5 (`segments_auto.csv`) | `[x]` | 101 segs: 95 row (756 s), 6 turn (19 s) |
| **Run seq5 × 3 (multi-run benchmark)** | `[x]` | ATE 20.207 ± 4.204 m, 91% avg, 0 loops |
| **Evaluate + aggregate seq5 × 3** | `[x]` | `metrics.csv` + `report.md` + `segment_map.png` done |
| Segment map visualisation seq1 | `[x]` | `results/rosariov2/sequence1/segment_map.png` |
| Segment map visualisation seq5 | `[x]` | `results/rosariov2/sequence5/segment_map.png` |
| Run remaining sequences | `[ ]` |  |
| Evaluate remaining sequences | `[ ]` |  |

### 1-C  DROID-SLAM

| Task | Status | Notes |
|---|---|---|
| Set up conda env + install dependencies | `[x]` | torch 2.7+cu126, lietorch 0.2, torch_scatter 2.1.2 |
| `scripts/run/run_droidslam.sh` + `_droid_demo_wrapper.py` | `[x]` | stereo, TUM trajectory output |
| `configs/droidslam/rosariov2.txt` intrinsics file | `[x]` | fx=fy=648.86, cx=645.01, cy=348.24 |
| `droid.pth` pretrained weights | `[x]` | downloaded to `src/DROID-SLAM/` |
| Run sequence 1 | `[x]` | full sequence (6911 frames, stride=2), skip_backend |
| Evaluate sequence 1 | `[x]` | **ATE RMSE 45.05 m** (Sim3 alignment) |
| Sequence 5 trajectory | `[x]` | 3 runs provided by collaborator; timestamps converted ns→s |
| Evaluate sequence 5 | `[x]` | **ATE RMSE 50.02 m** (Sim3, mean of 3 runs) |

### 1-D  MAC-VO

| Task | Status | Notes |
|---|---|---|
| Set up conda env + install dependencies | `[x]` | `macvo` env created; models downloaded |
| `scripts/run/run_macvo.sh` | `[x]` | fixed: conda set-u, upstream odom config, `--useRR`, correct Results path |
| `configs/macvo/rosario_v2_sequence.yaml` | `[x]` | GeneralStereo format; intrinsics=648.86, bl=0.04973; `left/right` symlinks created |
| Run sequence 1 | `[x]` | 13821 frames, 100% completion |
| Evaluate sequence 1 | `[x]` | **ATE RMSE 13.277 m** (Sim3 alignment) |
| `configs/macvo/rosariov2_sequence5.yaml` | `[x]` | same intrinsics/bl; root→sequence5; `left/right` symlinks created |
| Run sequence 5 | `[x]` | 11 640 frames, 100% completion (3 runs done) |
| Evaluate sequence 5 | `[x]` | **ATE RMSE 19.384 ± 0.006 m** (Sim3, 3 runs) |

### 1-E  Cross-algorithm comparison (Rosario v2)

| Task | Status |
|---|---|
| All four algorithms run on sequence 1 (single run) | `[x]` |
| ORB-SLAM3 + DROID-SLAM run on sequence 5 | `[x]` |
| MAC-VO on sequence 5 × 3 | `[x]` | ATE Sim3 **19.384 ± 0.006 m** (3 runs; scale=0.933, 100% tracking) |
| ORB-SLAM3 × 3 multi-run benchmark seq1 | `[x]` | ATE 1.176 ± 0.317 m, `report.md` + `segment_map.png` |
| ORB-SLAM3 × 3 multi-run benchmark seq5 | `[x]` | ATE 20.207 ± 4.204 m, `report.md` + `segment_map.png` |
| Segment maps for seq1 and seq5 | `[x]` | seq1 ✓, seq5 ✓ |
| `metrics.csv` + `report.md` for seq1 | `[x]` | done |
| `metrics.csv` + `report.md` for seq5 | `[x]` | done |
| Comparison table for thesis chapter | `[ ]` | Final LaTeX/PDF table for thesis |

### 1-F  Basalt (stereo VO)

| Task | Status | Notes |
|---|---|---|
| `configs/basalt/rosariov2_calib.json` | `[x]` | EuRoC format, pinhole, `vio_min_triangulation_dist: 0.03` |
| Run seq1 × 3 + evaluate | `[x]` | ATE Sim3 **14.279 ± 0.302 m**, SE3 **18.693 ± 0.586 m**, 100% |
| Run seq5 × 3 + evaluate | `[x]` | ATE Sim3 **15.035 ± 0.062 m**, SE3 **15.425 ± 0.068 m**, 100% |
| Segment maps with Basalt | `[x]` | seq1 + seq5 regenerated |

### 1-G  AirSLAM (deep-feature stereo VO)

| Task | Status | Notes |
|---|---|---|
| `configs/airslam/rosariov2_camera.yaml` + `rosariov2_vo.yaml` | `[x]` | 1280×720, baseline 0.04973m |
| TensorRT engine compiled for rosariov2 (1280×720) | `[x]` | Compiled on seq1 run1 startup |
| Run seq1 × 3 + evaluate | `[x]` | **DONE** (9.888 ± 0.059 m Sim3, 9.891 ± 0.058 m SE3, 100% × 3) |
| Run seq5 × 3 + evaluate | `[x]` | **DONE** (12.722 ± 0.991 m Sim3, 12.777 ± 1.014 m SE3, 100% × 3) |



---

## GNSS-VIO (stereo + IMU + GNSS) - `results-gnss-vio/`

Phase F: GPS-aware algorithms with full Sim(3)+SE(3) eval pipeline.

Infrastructure status:
- [x] `run_type=gnss-vio` registered in `_paths.sh` and `_run_type.py`
- [x] `results-gnss-vio/` + `benchmark-gnss-vio.csv` wired into the eval pipeline
- [x] Shared GPS data players (`gnss_data_player.py` ROS 1, `gnss_data_player_ros2.py` ROS 2)
- [x] HortiMulti GPS extraction added to `_hortimulti_extract.py` (`--gps-only`,
      `--no-gps`, `--gps`); topic default `/antobot_gps`. Handles the upstream
      quirk where `header.stamp` is constant in `/antobot_gps` (falls back to
      bag-arrival time) and altitude is published in millimetres (auto-rescales
      when `max(alt) > 1000 m`).
- [x] CIFASIS GNSS-SI: clone + Dockerfile + setup script + configs for rosariov2
      seq1/seq5 + hortimulti str02/str03 + runner.
- [x] RTAB-Map: configs (rosariov2, hortimulti) + ROS 2 launch runner.
      `gnss_data_player_ros2.py` publishes `/cam{0,1}/camera_info` from per-dataset
      rectified intrinsics passed via `run_rtabmap_gps.sh`.
- [x] VINS-Fusion: clone + Dockerfile + setup script + configs for rosariov2
      seq1/seq5 + hortimulti str02/str03 (incl. per-cam YAMLs) + runner.
      Ceres pinned to `1.14.0` (2.1+ uses `std::integer_sequence`, incompatible
      with VINS-Fusion's hard-coded `-std=c++11`). All `CV_*` legacy macros are
      sed-rewritten to `cv::*` after `COPY src/VINS-Fusion` in the Dockerfile.
      HortiMulti `body_T_cam0` is `T_imu_cam0_raw @ blkdiag(R1.T, 1)` where
      `R1` comes from `cv2.fisheye.stereoRectify` in `_hortimulti_extract.py`.
- [x] OpenVINS+GPS: OpenVINS odometry + `robot_localization` EKF runner and four N=1 artifacts.
- [x] HortiMulti GPS extraction completed for str02/str03 (7620/1939 fixes;
      consumer-grade fixes with large vertical covariance).
- [x] CIFASIS GNSS-SI N=1 on rosariov2 seq1/seq5 + HortiMulti str02/str03; N=3 pending.
- [x] RTAB-Map N=1 on all four sequences; seq5 PPK is partial/nondeterministic; N=3 pending.
- [x] VINS-Fusion N=1 on all four sequences; N=3 pending.
- [~] OpenVINS+GPS N=1 on all four sequences; validate all rows and rerun HortiMulti with the
      corrected extrinsic before N=3.
- [x] Rosario sequence5 PPK-versus-conventional four-algorithm study completed.
