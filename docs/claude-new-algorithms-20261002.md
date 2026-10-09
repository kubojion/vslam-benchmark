# New algorithms for the benchmark — proposal (Claude, 2026-10-02)

Scope: which algorithms to add to the five-mode matrix, what each one fills, what integration needs,
and what could go wrong. Four additions are decided (cuVSLAM, SVO Pro, MASt3R-Fusion, DSOL); two more
are under consideration (VGGT-SLAM 2.0, SuperVINS 2.0).

*Updated 2026-10-02: DSOL moved from "under consideration" to "decided".*

**How this was checked.** I cloned each repository and read its README, launch/config files and the
relevant source on 2 October 2026. Nothing was installed, built or run, and nothing in this workspace
other than this file was changed. Every "should work" below is a reading of the code, not a test.
The candidate pool came from a survey of roughly 130 open-source systems from 2021-2026 (classical,
learned, feed-forward/Gaussian-splatting, GNSS fusion).

---

## 1. Verdict

| Algorithm | Decision | Family it adds | Tables it fills | Integration risk |
|---|---|---|---|---|
| **cuVSLAM** | add | classical, GPU-accelerated, industrial | VO, VO-LC, VIO, VIO-LC | low |
| **SVO Pro** | add | semi-direct | VO, VIO, VIO-LC, GNSS-VIO | medium |
| **MASt3R-Fusion** | add | feed-forward 3D model + IMU | VIO, VIO-LC, GNSS-VIO | high |
| **DSOL** | add | direct (photometric), stereo | VO | medium |
| VGGT-SLAM 2.0 | pilot first | feed-forward, vision only | VO-LC (scale-free) | low to integrate, likely weak results |
| SuperVINS 2.0 | only together with VINS-Fusion; otherwise skip | learned features on a classical back end | VO, VO-LC, VIO, VIO-LC | medium |

The four decided additions are a sound set: they add four method families the matrix does not have
and 12 new rows across all five tables. With SVO Pro (semi-direct) and DSOL (direct) the taxonomy now
covers photometric tracking in both forms. Weaknesses to accept knowingly: SVO Pro and DSOL are not
recent (2021-2022 code), DSOL is a reduced release with frozen code, and MASt3R-Fusion is the only
learned addition and uses one camera.

---

## 2. Decided additions

### 2.1 cuVSLAM (NVIDIA)

- **Source:** `github.com/nvidia-isaac/cuVSLAM`, version 17.0.0 (repo commit of 2026-10-01). Paper: arXiv 2506.04359, no peer-reviewed venue.
- **Licence:** NVIDIA Community License. Source is included, but it is not an open-source licence; describe it as "source-available". Use is tied to NVIDIA hardware, which the server satisfies.
- **Why it belongs:** it is the default visual SLAM in NVIDIA's ROS 2 stack and widely deployed on field robots, so reviewers will expect it. It is the only addition that runs one codebase in four of the five modes.
- **Install:** prebuilt pip wheel for Ubuntu 22.04, Python 3.10, CUDA 12 or 13. No build needed.
- **Input:** Python API with offline (synchronous) tracker modes. The bundled EuRoC example reads the `mav0/cam*/data` + `imu0/data.csv` layout the benchmark datasets already use. Rectified or raw stereo via `rectified_stereo_camera`.

| Benchmark mode | cuVSLAM setting |
|---|---|
| VO | `OdometryMode.Multicamera` (stereo), tracker `OdometryOnlyOffline` |
| VO-LC | same odometry, tracker `OdometryWithSlamOffline` |
| VIO | `OdometryMode.Inertial` (one stereo pair + one IMU), tracker `OdometryOnlyOffline` |
| VIO-LC | `Inertial` + `OdometryWithSlamOffline` — I found nothing in the code that forbids the combination, but I did not see an example of it. Confirm in the pilot. |

- **Things to state in the paper:**
  - NVIDIA's own `TROUBLESHOOTING.md` says: "The cuVSLAM implementation of IMU fusion does not add extra accuracy in scenarios where visual input works, and the IMU can even slightly decrease accuracy." The IMU is a robustness fallback. This is directly relevant to the VO-versus-VIO comparison.
  - The README says "no parameter tuning is required or expected", which fits the author-default policy.
  - The guide prefers high frame rates ("100 fps at VGA can be better than 30 fps at 2K"). The benchmark data is 10-20 fps; the robots are slow, so inter-frame motion is small, but this is a deviation from the recommended operating point.
- **Decisions needed during integration:**
  - Which SLAM output to score. `track()` returns a per-frame SLAM pose (causal), and `slam.get_all_slam_poses()` returns the corrected trajectory at the end. Pick one and label it, as was done for the other loop-closure systems.
  - IMU calibration takes `rig_from_imu`, noise densities, random walks and frequency. Use the same physical values as the other inertial methods (see section 5).

### 2.2 SVO Pro (UZH RPG)

- **Source:** `github.com/uzh-rpg/rpg_svo_pro_open` (last commit 2022-08-04) and, for GNSS, `github.com/uzh-rpg/rpg_svo_pro_gps` (last commit 2023-04-18). GPLv3.
- **What it is:** **semi-direct**, not direct. It tracks by sparse direct image alignment and then refines with feature-based optimisation. Call it "semi-direct" in the taxonomy. The inertial back end is a sliding-window optimiser adapted from OKVIS.
- **Why it belongs:** the matrix has no method that tracks photometrically. SVO Pro is the standard representative, supports stereo, and was included in the JFR 2025 loop-closing benchmark (Schmidt et al.).
- **Platform:** README lists Ubuntu 18.04 + ROS Melodic **and Ubuntu 20.04 + ROS Noetic** as tested. The reason recorded in `TODO.md` for dropping it ("ROS1 Melodic only; frozen toolchain") is therefore not accurate; it needs a Noetic container, like other ROS 1 systems already in the benchmark. `scripts/run/run_rpg_svo.sh` is currently a stub that exits with "NOT INSTALLED".

| Benchmark mode | SVO Pro setting | Status |
|---|---|---|
| VO | stereo front end only (`pipeline_is_stereo: True`, `use_imu: False`) | The shipped stereo front-end launch files use an IMU rotation prior; an IMU-free stereo run is a parameter change that I did not see exercised. Confirm in the pilot. |
| VIO | `euroc_vio_stereo.launch` with `runlc: false` | supported |
| VIO-LC | same with `runlc: true` (DBoW2 loop closure + pose graph) | supported; the authors call their loop acceptance "relatively conservative" |
| GNSS-VIO | `rpg_svo_pro_gps`, `euroc_vio_gp_stereo.launch` | supported with preparation, see below |
| VO-LC | — | not available as far as I can see: loop closure sits inside the visual-inertial pipeline |

- **Do not use the iSAM2 "global map".** `doc/global_map.md`: "the global map function is only tested with monocular configuration and is relatively unstable".
- **GNSS variant, preparation needed:**
  - It subscribes to global positions on one topic (`/gp_data`) in a local Cartesian frame, with settings in `gp_settings.yaml`; fixes must be converted from latitude/longitude beforehand.
  - Its only shipped example uses simulated positions (EuRoC ground truth plus 0.20 m Gaussian noise).
  - It is a separate fork, so the VIO and GNSS-VIO rows come from two codebases. Record both commits.
- **Known weak points from the authors** (`doc/known_issues_and_improvements.md`): visual-inertial initialisation is "relatively naive" (wait for the back end to converge, then rescale the front-end map).
- **Feeding:** ROS topics or rosbag. It will be a real-time transport run, so frame drops must be measured as for OV2SLAM, OpenVINS and Voxel-SVIO.

### 2.3 MASt3R-Fusion (Wuhan University, GREAT group)

- **Source:** `github.com/GREAT-WHU/MASt3R-Fusion` (commit of 2026-09-06). Paper: arXiv 2509.20757; a journal version may exist, which I did not confirm.
- **Licence:** the repository has no licence file. The MASt3R weights it downloads are under a non-commercial licence. Ask the authors or note this in the paper.
- **Why it belongs:** it represents the 2025-2026 feed-forward 3D foundation-model line, it is the only learned method in the set that uses the IMU, and it adds a learned entry to the GNSS track. Its README claims "arbitrarily long sequences based on 8 GB GPU memory".
- **Install:** Python 3.11, PyTorch 2.5.1 (CUDA 12.4), and the authors' **modified GTSAM** (`github.com/yuxuanzhou97/gtsam`) built from source with Python bindings. This build is the main integration risk.
- **Input:** `main.py` reads the EuRoC layout directly. Calibration YAML holds `width`, `height`, intrinsics + radial-tangential distortion and `Tic` (camera to IMU). IMU noise is four numbers in the config; `--imu_dt` is a constant camera-IMU time offset.

| Benchmark mode | MASt3R-Fusion step | Output |
|---|---|---|
| VIO | `main.py` (real-time sliding window, monocular + IMU) | `result.txt` |
| VIO-LC | `main_loop.py` then `main_global_optimization.py` on the saved graph | `result_post.txt` |
| GNSS-VIO | `main_global_optimization.py --enable_gnss --gnss_path ...` | global result |
| VO, VO-LC | — | not available: I found no option to run without the IMU |

- **Limits to state:**
  - Monocular: it uses the left camera only. Metric scale comes from the IMU alone, which is exactly where the constant-velocity field robot is weak. A poor scale there is a finding, not a bug.
  - Loop closure and GNSS fusion are offline post-processing of a stored factor graph. Label them "offline global optimisation", in the same way as AirSLAM's map refinement.
  - Images are resized to 512 px on the long side. For the 1920x1080 ZED sequence that is a heavy downscale.
  - The EuRoC config processes every second frame (`subsample: 2`).
- **GNSS file format** (from `main_global_optimization.py`): a whitespace text file with time and ECEF x, y, z per row; the code converts to a local frame and applies a lever arm read from the calibration file (`lever`). The antenna lever arm must therefore be supplied per dataset.
- **Repetitions:** VIO-LC and GNSS-VIO are computed from the graph saved by a VIO run. Define a repetition as one complete front-end run plus its post-processing, so the three rows of one repetition share one execution.
- **Recent fix worth knowing:** the 2026-09-05 update addresses "sequences with stationary starts and IMUs whose z-axis does not point upward". Use that commit or later.

### 2.4 DSOL — Direct Sparse Odometry Lite (UPenn, IROS 2022)

- **Source:** `github.com/versatran01/dsol`, Apache-2.0, paper arXiv 2203.08182. Branches: `main` and `iros22` (last commit 2022-03-16). Code on `main` is effectively frozen since 2023; later commits only remove CI.
- **What it is:** a **direct** (photometric) sparse stereo odometry: it selects high-gradient pixels, gets their depth by stereo matching, and estimates motion by direct image alignment and a small windowed photometric bundle adjustment (4 keyframes by default). No features, no descriptors.
- **Why it belongs:** it is the only open, peer-reviewed stereo direct method found in the survey. SVO Pro is semi-direct; DSOL lets the paper report a fully direct row.
- **Platform:** ROS 1 Noetic on Ubuntu 20.04 (the repository's CI build file documents the build). It can share the SVO Pro container.

| Benchmark mode | DSOL setting |
|---|---|
| VO | stereo, rectified input; `init_stereo: true`, `init_depth: false` (depth from stereo, not from a depth sensor) |
| VO-LC, VIO, VIO-LC, GNSS-VIO | not available: windowed odometry only, no loop closure, no inertial fusion |

- **Two ways to feed it, and which to use:**
  - `sv_dsol_node_odom` (`dsol_odom.launch`) subscribes to two rectified images and their `camera_info`. The shipped launch file is written for RealSense `infra1/infra2 image_rect_raw`, which is the same kind of stream as Rosario v2. **Use this node**, fed by the existing ROS 1 data player.
  - `sv_dsol_node_data` (`dsol_data.launch`) reads KITTI, VKITTI2, TartanAir or ICL-NUIM folders offline and can write a TUM trajectory (`save`). Its loaders read the dataset's ground-truth poses (to publish a reference path and to initialise the motion model with the first, identity, relative pose). I saw no ground truth entering the estimate, but a benchmark run should not have reference poses in the estimator's input at all, so avoid this node or strip that code path.
- **Things that must be handled explicitly:**
  - **Gyroscope.** The odometry node subscribes to a gyro topic (`~gyr`) and, when messages arrive, uses them to predict rotation between frames. For a VO row the topic must stay unconnected, and the run metadata should record that. A gyro-aided variant would be a different configuration, not VO.
  - **Dataset-specific thresholds.** The KITTI config sets minimum stereo depth to 4 m (`vis_min_depth`, `stereo.min_depth`); the base config uses 1 m, and there is a RealSense D455 config. Choose per rig by one stated rule and record it; do not select by test accuracy.
  - **Brightness model.** `affine: false` in the shipped configs, so no affine brightness compensation. Outdoor exposure changes are a known weak point of direct methods; a poor result there is a finding.
  - **Which branch.** The README says: "For reproducing the results in the paper, place use the `iros22` branch. This is the open-source version, advanced features are not included." Decide `main` or `iros22` once and record the commit.
  - **Transport.** It is a real-time ROS run, so frame drops must be measured as for the other transport-fed systems.
- **Evidence available:** KITTI, VKITTI2, TartanAir and a RealSense sample. No agricultural and no 10 Hz results.

---

## 3. Under consideration

### 3.1 VGGT-SLAM 2.0 (MIT SPARK, RSS 2026)

- **Source:** `github.com/MIT-SPARK/VGGT-SLAM` (commit of 2026-06-29), BSD-2 for the code; VGGT weights under their own licence.
- **What it adds:** a vision-only feed-forward system with a recognisable name and a strong venue. Input is a plain image folder; it works in submaps (default 16 frames) and selects keyframes by optical-flow disparity.
- **Modes:** monocular, uncalibrated, scale-free. It has loop closure (`--max_loops 1`), so it would sit in VO-LC under Sim(3), next to DPV-SLAM.
- **Risks:** its own evaluation scripts cover TUM and 7-Scenes (indoor). An independent paper reports about 93 m average error on KITTI with tracking lost on three sequences (reported by a survey agent from the AMB3R-SLAM paper; I did not read that table myself). Expect weak results on long crop rows.
- **Verdict:** cheap to try, so run a pilot on HortiMulti str03. A failure is still a reportable result for the most visible feed-forward SLAM of 2026. Re-running MASt3R-SLAM (runner already exists) is the free alternative and pairs naturally with MASt3R-Fusion; note that MASt3R-SLAM keeps a fixed 512-keyframe GPU buffer and will probably not finish the long sequences.

### 3.2 SuperVINS 2.0 (Wuhan University, IEEE Sensors Journal 2025; v2.0 May 2026)

- **Source:** `github.com/luohongk/SuperVINS` (commit of 2026-06-24), GPLv3. ROS 1 Noetic, Docker provided, rosbag input.
- **What it is:** VINS-Fusion with SuperPoint + LightGlue replacing the front end, and DBoW3 + LightGlue for loop closure. Stereo-only and stereo + IMU configs exist. No GNSS module.
- **Problem:** it is the same family as AirSLAM (learned features on a classical stereo/inertial back end), which is already in the matrix and is the stronger publication. On its own it adds a near-duplicate row.
- **When it would be worth it:** together with plain VINS-Fusion in the same modes. The pair is then a controlled test of a learned versus a handcrafted front end on an identical back end. VINS-Fusion is already built for the GNSS track.
- **Verdict:** skip, unless that specific ablation is wanted, in which case add both.

### 3.3 Considered and not proposed

| System | Why not |
|---|---|
| OTPL-VIO (arXiv 2603.09653) | no public code; its idea (points + lines with deep descriptors) overlaps AirSLAM |
| DROID-SLAM | excluded by decision; MAC-VO covers learned stereo |
| DM-VIO | fully direct, but monocular + IMU only; excluded by decision, DSOL covers the direct family |
| MINS | its GNSS mode cannot be scored on Rosario v2, whose reference trajectory was produced by MINS |
| VIGS-SLAM (ECCV 2026) | Gaussian splatting + IMU, monocular; a reasonable future addition, shown only on handheld/indoor data |
| Photo-SLAM, DiskChunGS, GLAM-SLAM, GigaSLAM | poses come from ORB-SLAM2/3 or DPVO, so the trajectory repeats existing rows |
| GVINS, InGVIO | need raw pseudorange/Doppler, which the datasets do not provide |
| HyVGGT-VO (RA-L 2026) | "initial draft code", per-sequence configs, custom GTSAM |

---

## 4. Matrix coverage after the four additions

| Algorithm | Camera | VO | VO-LC | VIO | VIO-LC | GNSS-VIO |
|---|---|---|---|---|---|---|
| cuVSLAM | stereo | new | new | new | new (confirm) | – |
| SVO Pro | stereo | new (confirm) | – | new | new | new |
| MASt3R-Fusion | mono (left) | – | – | new | new | new |
| DSOL | stereo | new | – | – | – | – |
| *VGGT-SLAM 2.0 (if added)* | mono | – | new, Sim(3) | – | – | – |

Rows added by the four decided systems: VO +3, VO-LC +1, VIO +3, VIO-LC +3, GNSS-VIO +2.

### Runs this implies (N=3)

| Algorithm | Non-GNSS (8 sequences) | GNSS track (4 sequences) | Total repetitions |
|---|---|---|---|
| cuVSLAM | 4 modes × 8 × 3 = 96 | – | 96 |
| SVO Pro | 3 modes × 8 × 3 = 72 | 4 × 3 = 12 | 84 |
| DSOL | 1 mode × 8 × 3 = 24 | – | 24 |
| MASt3R-Fusion | 2 modes × 8 × 3 = 48 rows | 4 × 3 = 12 rows | 60 rows from 24 front-end executions (loop closure and GNSS are post-processing of the same saved graph) |

SVO Pro and DSOL run at sensor rate: one pass over the eight sequences is about 2.2 hours, so SVO Pro's
72 non-GNSS repetitions are roughly 20 hours and DSOL's 24 are roughly 7 hours. cuVSLAM should be faster than real time; MASt3R-Fusion's speed on
this hardware is unknown until the pilot.

---

## 5. Requirements for the new rows

These follow from the defects found in the existing runs (see `claude-fidings.md`), so the new rows
do not repeat them.

1. **Same physical calibration as the other methods.** Camera-IMU transform, intrinsics and baseline
   must be the dataset values used by the already-accepted rows. On Rosario v2 that means the authors'
   transform (0.37°, 34 mm), not identity. For rectified datasets the transform must be the rectified one.
2. **One IMU-noise policy.** Use the sensor values the dataset authors publish, or state and apply one
   inflation rule for all methods. Do not carry over values from another algorithm's defaults.
3. **Camera rate and time offset set per dataset** (10, 15 or 20 Hz), not left at an example value.
4. **No setting that lets the estimator rewrite the calibration** unless it is the upstream default
   (the OKVIS2-X final-BA lesson). MASt3R-Fusion's `enable_excalib` is `False` in its EuRoC config; keep it so.
5. **Author-default parameters, recorded with the upstream commit.** cuVSLAM is run untuned by design.
6. **Save the effective configs per run** in `provenance/`, as for the existing systems.
7. **Record what the loop-closure output is** (causal per-frame pose, final corrected trajectory, or
   offline global optimisation) so LC rows are comparable in kind.
8. **No reference data on the estimator's input, and no undeclared sensors.** DSOL must be fed through
   its topic-based node without the gyro topic (section 2.4); the same check applies to any loader that
   reads a dataset's ground-truth file.
9. **Monocular rows** (MASt3R-Fusion with IMU is metric; VGGT-SLAM 2.0 is not) go in the table that
   matches their scale: SE(3) for metric, Sim(3) for scale-free.

---

## 6. Pilot before production

Run each new system once on EuRoC MH_01 (sanity against published numbers) and once on HortiMulti
str03 (short agricultural sequence, 2,425 frames), then on one long sequence.

| System | Pilot must show |
|---|---|
| cuVSLAM | stereo VO and inertial runs complete offline; inertial + SLAM combination works; which SLAM output is exported |
| SVO Pro | Noetic container builds; stereo front end runs with `use_imu: False`; no frames dropped at transport; GNSS variant accepts converted fixes |
| MASt3R-Fusion | modified GTSAM builds; EuRoC result near the paper's; memory stays bounded on the 46,283-frame ZED sequence; runtime per sequence |
| DSOL | Noetic build (shared container); topic-fed node runs with rectified stereo + `camera_info` and no gyro; completes str03 and one Rosario sequence at 10-15 fps; frame drops measured |
| VGGT-SLAM 2.0 (optional) | completes str03; memory and runtime on a long sequence |

---

## 7. Not verified

- Nothing was built or run. All capability statements come from READMEs, launch files, configs and source.
- cuVSLAM: inertial odometry combined with SLAM mode; behaviour at 10-20 fps and at 1920x1080.
- SVO Pro: stereo front end without the IMU prior; loop closure without the IMU; behaviour of the GNSS fork with real fixes.
- MASt3R-Fusion: memory and runtime on sequences of this length; publication venue; licence terms.
- DSOL: any outdoor agricultural or low-frame-rate behaviour; that the data node's ground-truth read never affects the estimate (I read the call sites, not every path); which branch performs better.
- VGGT-SLAM 2.0: any outdoor agricultural behaviour.
- The KITTI figure quoted for VGGT-SLAM comes from a survey agent's reading of another paper.

## 8. Sources

- cuVSLAM: https://github.com/nvidia-isaac/cuVSLAM , https://arxiv.org/abs/2506.04359
- SVO Pro: https://github.com/uzh-rpg/rpg_svo_pro_open , https://github.com/uzh-rpg/rpg_svo_pro_gps
- MASt3R-Fusion: https://github.com/GREAT-WHU/MASt3R-Fusion , https://arxiv.org/abs/2509.20757
- DSOL: https://github.com/versatran01/dsol , https://arxiv.org/abs/2203.08182
- VGGT-SLAM: https://github.com/MIT-SPARK/VGGT-SLAM , https://arxiv.org/abs/2601.19887
- SuperVINS: https://github.com/luohongk/SuperVINS , https://arxiv.org/abs/2407.21348
- OTPL-VIO: https://arxiv.org/abs/2603.09653
- Candidate lists consulted: https://github.com/3D-Vision-World/awesome-NeRF-and-3DGS-SLAM , https://github.com/KwanWaiPang/Awesome-Transformer-based-SLAM
