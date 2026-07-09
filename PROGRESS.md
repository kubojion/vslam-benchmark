# vSLAM Benchmark - Progress

> Updated: 2026-05-31 - GNSS-VIO N=1 sweep complete (16 runs, 4 algorithms x 4 sequences). rosariov2 seq5 re-run with high-quality PPK GPS (GPS-quality study added). VIO N=1 complete (30 rows, 6 algorithms). VO N=3 complete.

Algorithms run: **ORB-SLAM3** (classical), **MAC-VO** (hybrid), **Basalt** (sliding-window VIO), **AirSLAM** (deep-feature VO, Docker), **OKVIS2** (MAP VIO+LC), **OpenVINS** (MSCKF VIO, Docker). GNSS-VIO: **VINS-Fusion+GPS**, **CIFASIS GNSS-SI**, **RTAB-Map+GPS**, **OpenVINS+GPS** (robot_localization EKF). Scaffolded: **MASt3R-SLAM**, **MegaSaM**. Dropped: **DROID-SLAM** (supervisor feedback).

---

## VO - Visual Odometry

**N=3** for main VO-phase algorithms (ORB-SLAM3, MAC-VO, Basalt, AirSLAM, DROID-SLAM). **N=1** for OKVIS2 VO-mode runs.
All ATE values: Sim3 RMSE, with SE3 column for scale-aware comparison.

| Algorithm | Dataset | Seq | ATE Sim3 | ATE SE3 | Scale | RPE [m/m] | FPS | N |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | rosariov2 | seq5 | **14.16 m** | 14.40 m | 0.949 | 0.0845 | 5.93 | 1 |
| OKVIS2 | rosariov2 | seq5 | 17.48 m | 17.68 m | 0.947 | 0.0781 | 8.44 | 1 |
| OKVIS2 | rosariov2 | seq1 | 20.03 m | 20.63 m | 0.897 | 0.1381 | 8.91 | 1 |
| AirSLAM | rosariov2 | seq1 | **9.89 ± 0.06 m** | 9.89 m | 1.005 | 0.034 | 23.04 | 3 |
| AirSLAM | rosariov2 | seq5 | 12.72 ± 0.99 m | 12.78 m | 0.977 | 0.055 | 23.74 | 3 |
| AirSLAM | hortimulti | str02 | 20.22 ± 0.82 m | 20.48 m | 0.928 | 0.266 | 27.37 | 3 |
| AirSLAM | hortimulti | str03 | 3.63 ± 0.21 m | 3.77 m | 1.064 | 0.135 | 22.07 | 3 |
| AirSLAM | euroc_mav | MH_01 | 0.111 m | 0.116 m | 1.007 | 0.0195 | 15.33 | 1 |
| AirSLAM | euroc_mav | MH_03 | 0.143 m | 0.144 m | 0.995 | 0.0188 | 31.73 | 1 |
| AirSLAM | euroc_mav | MH_05 | 0.297 m | 0.307 m | 1.012 | 0.0256 | 34.92 | 1 |
| Basalt† | rosariov2 | seq1 | 14.28 ± 0.30 m | 18.69 m | 0.791 | 1.645 | 59.44 | 3 |
| Basalt† | rosariov2 | seq5 | 15.04 ± 0.06 m | 15.43 m | 0.934 | 0.802 | 64.60 | 3 |
| Basalt† | hortimulti | str02 | **2.10 ± 0.00 m** | 2.66 m | 1.034 | 0.091 | 149.70 | 3 |
| Basalt† | hortimulti | str03 | **0.275 m** | 0.715 m | 1.036 | 0.022 | 143.65 | 3 |
| Basalt† | euroc_mav | MH_01 | **0.057 m** | 0.087 m | 1.016 | 0.0085 | 176.75 | 1 |
| Basalt† | euroc_mav | MH_03 | 0.137 m | 0.140 m | 1.008 | 0.0159 | 113.47 | 1 |
| Basalt† | euroc_mav | MH_05 | 0.182 m | 0.193 m | 1.010 | 0.0870 | 108.72 | 1 |
| DROID-SLAM | rosariov2 | seq1 | 45.37 m | 45.37 m | 0.970 | 0.724 | 17.44 | 3 |
| DROID-SLAM | rosariov2 | seq5 | 50.02 m | 50.24 m | 1.904 | 1.076 | 23.36 | 3 |
| DROID-SLAM | hortimulti | str02 | 38.92 m | 47.90 m | 9.590 | 4.335 | 27.95 | 3 |
| DROID-SLAM | hortimulti | str03 | 18.76 m | 18.81 m | 0.428 | 0.837 | 15.85 | 3 |
| DROID-SLAM | euroc_mav | MH_01 | 4.08 m | 7.89 m | 0.173 | 0.500 | 13.17 | 1 |
| DROID-SLAM | euroc_mav | MH_03 | 3.52 m | 7.10 m | 0.082 | 2.274 | 10.94 | 1 |
| DROID-SLAM | euroc_mav | MH_05 | 6.59 m | 8.51 m | 0.248 | 0.786 | 13.85 | 1 |
| MAC-VO | rosariov2 | seq1 | **13.52 ± 0.01 m** | 13.55 m | 0.980 | 0.051 | 1.71 | 3 |
| MAC-VO | rosariov2 | seq5 | 19.38 ± 0.01 m | 19.67 m | 0.933 | 0.096 | 1.40 | 3 |
| MAC-VO | hortimulti | str02 | 10.23 ± 0.50 m | 10.25 m | 1.009 | 0.096 | 1.70 | 3 |
| MAC-VO | hortimulti | str03 | **0.505 ± 0.01 m** | 0.84 m | 1.037 | 0.024 | 1.54 | 3 |
| MAC-VO | euroc_mav | MH_01 | 0.198 m | 0.199 m | 1.005 | 0.0295 | 1.29 | 1 |
| MAC-VO | euroc_mav | MH_03 | 0.340 m | 0.341 m | 0.996 | 0.0187 | 1.15 | 1 |
| MAC-VO | euroc_mav | MH_05 | 0.470 m | 0.484 m | 1.017 | 0.0276 | 0.86 | 1 |

† Basalt pre-restructure (run_type=None): hortimulti entries ran without IMU (no imu0 in mav0/);
rosariov2 entries likely VO mode given 21% scale drift on seq1 (scale=0.79).
See VIO table for the Basalt VIO re-run (rosariov2/seq5: 4.74 m with IMU).

ORB-SLAM3 VO-clean (LC-off) run exists for rosariov2/seq5 only. Old seq1/hortimulti/EuRoC
ORB-SLAM3 results used the LC-enabled binary and are in `obsolete/` - not shown above.

### Remarks: VO

- **Loop closure dominates global accuracy on long agricultural sequences.** ORB-SLAM3 seq1: 1.18 m (5-6 LCs) vs seq5: 20.2 m (0 LCs) on similar geometry. 5-6 LCs = 17x ATE improvement. Algorithms without LC (MAC-VO, Basalt, AirSLAM) all cluster in the 9-20 m range on Rosario.
- **Local accuracy is excellent and consistent across all algorithms** - per-row ATE: ORB-SLAM3 16 mm, MAC-VO 20 mm, Basalt 14 mm, AirSLAM 19 mm. 1000x ratio between local (16 mm) and global (16 m) accuracy. Within-row precision is adequate for all algorithms.
- **Scale drift follows geometry, not just length.** Basalt: 20.9% drift on Rosario seq1 vs 6.6% on seq5 (similar length, different route shape). Monotone straight-line motion provides weaker stereo triangulation constraints.
- **SE3 is the honest metric for stereo; Sim3 hides scale drift.** Example: ORB-SLAM3 str03 0.10 m (Sim3) vs 0.78 m (SE3).
- **DROID-SLAM fails on agricultural data** (domain mismatch - trained on TartanAir/synthetic data). Scale collapse severe: str02 scale 9.59, str03 scale 0.428, Rosario seq5 ATE 50 m.
- **RPE rotation ~17-20 deg/m on HortiMulti** is a frame-mismatch artefact (body vs camera GT frame), not real rotational error. RPE translation [m/m] is unaffected and remains the valid metric.
- **Repeatability:** Basalt/MAC-VO are deterministic (ATE std < 1 mm). ORB-SLAM3 and AirSLAM show run-to-run variation from LC timing nondeterminism (ORB-SLAM3 seq5: 4.2 m std). 3-run averages recommended.
- See Phase 1 (below) for full per-algorithm per-sequence detailed results and analysis.

---

## VIO - Visual-Inertial Odometry

All N=1 (best single run). Sequences: rosariov2 seq1/seq5, hortimulti str02/str03, EuRoC MH_01_easy.
hortimulti VIO: ORB-SLAM3 produces the best trajectories on both sequences via its VO-first then
IMU-fusion strategy. All other algorithms show scale collapse (see "hortimulti VIO scale collapse"
section). Basalt is closest after extensive noise tuning: str03=2.85 m (vs VO 0.275 m), str02=22.9 m
(vs VO 2.1 m). OKVIS2 completely fails on both sequences (scale~0, 40% tracking failures).

| Algorithm | Dataset | Seq | ATE Sim3 | ATE SE3 | Scale | RPE [m/m] | FPS | N |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | rosariov2 | seq1 | 4.696 m | 4.800 m | 1.021 | 0.0300 | 12.32 | 1 |
| ORB-SLAM3 | rosariov2 | seq5 | **2.29 m** | 2.62 m | 1.026 | 0.0293 | 11.94 | 1 |
| ORB-SLAM3 | hortimulti | str02 | **2.792 m** | 3.329 m | 1.038 | 0.093 | 9.2 | 1 |
| ORB-SLAM3 | hortimulti | str03 | **0.568 m** | 0.930 m | 1.041 | 0.025 | 8.9 | 1 |
| ORB-SLAM3 | EuRoC | MH_01 | **0.022 m** | 0.022 m | 1.001 | 0.0138 | 36.41 | 1 |
| Basalt | rosariov2 | seq1 | 2.995 m | 3.006 m | 1.008 | 0.0126 | 63.44 | 1 |
| Basalt | rosariov2 | seq5 | **4.74 m** | 4.77 m | 1.011 | 0.0157 | **46.5** | 1 |
| Basalt | hortimulti | str02 | 22.905 m | 40.503 m | 0.570 | 0.184 | 62.7 | 1 |
| Basalt | hortimulti | str03 | **2.852 m** | 10.607 m | 0.645 | 0.056 | 46.8 | 1 |
| Basalt | EuRoC | MH_01 | **0.035 m** | 0.035 m | 1.004 | 0.0068 | 119.82 | 1 |
| OKVIS2 | rosariov2 | seq1 | 18.89 m | 19.39 m | 0.909 | 0.1236 | 9.93 | 1 |
| OKVIS2 | rosariov2 | seq5 | 20.29 m | 20.68 m | 0.921 | 0.1082 | 8.46 | 1 |
| OKVIS2 | hortimulti | str02 | 49.851 m | - | ~0 | - | 13.9 | 1 |
| OKVIS2 | hortimulti | str03 | 15.461 m | - | ~0 | - | 14.0 | 1 |
| OKVIS2 | EuRoC | MH_01 | **0.054 m** | 0.054 m | 1.000 | 0.0165 | 25.44 | 1 |
| OpenVINS | rosariov2 | seq1 | **2.316 m** | 2.542 m | 1.022 | 0.024 | - | 1 |
| OpenVINS | rosariov2 | seq5 | 38.240 m | 38.266 m | 1.003 | 0.103 | - | 1 |
| OpenVINS | hortimulti | str02 | 49.43 m | 35484 m | ~0 | - | 172.8 | 1 |
| OpenVINS | hortimulti | str03 | 17.03 m | 3377 m | ~0 | - | 167.6 | 1 |
| OpenVINS | EuRoC | MH_01 | **0.058 m** | 0.058 m | 1.000 | 0.019 | - | 1 |
| AirSLAM | rosariov2 | seq1 | 16.502 m | 16.769 m | 1.001 | 0.052 | 23.43 | 1 |
| AirSLAM | rosariov2 | seq5 | 12.148 m | 12.191 m | 0.998 | 0.048 | 24.89 | 1 |
| AirSLAM | hortimulti | str02 | 46.349 m | 49.571 m | 0.130 | - | 5.8 | 1 |
| AirSLAM | hortimulti | str03 | 16.329 m | 16.329 m | 1.021 | - | 31.0 | 1 |
| AirSLAM | EuRoC | MH_01 | **0.102 m** | 0.102 m | 1.005 | - | 31.15 | 1 |
| Voxel-SVIO | rosariov2 | seq1 | 4.398 m | 4.469 m | 1.017 | 0.0275 | - | 1 |
| Voxel-SVIO | rosariov2 | seq5 | 6.795 m | 6.812 m | 1.010 | 0.0279 | - | 1 |
| Voxel-SVIO | hortimulti | str02 | 6.464 m | 15.307 m | 0.781 | 0.132 | - | 1 |
| Voxel-SVIO | hortimulti | str03 | 17.918 m | 3022 m | ~0 | - | - | 1 |
| Voxel-SVIO | EuRoC | MH_01 | 3.027 m | 3.098 m | 0.001 | 1.887 | - | 1 |

OKVIS2 hortimulti: IMU noise inflated 50x Allan values; tracking failures (~40% of frames on str02)
cause backend divergence regardless of noise parameters. OKVIS2 rosariov2: D435i reference noise (see corrected results section).

#### hortimulti VIO scale collapse - analysis and partial fix

**Bug fixes (N/A -> real trajectories):**

- **OpenVINS** - `feat_rep_aruco: "CPI_ARUCO"` is not a valid
  `LandmarkRepresentation::Representation` enum value
  ([src/open_vins/ov_core/src/types/LandmarkRepresentation.h](src/open_vins/ov_core/src/types/LandmarkRepresentation.h)).
  `from_string` returned `UNKNOWN`, causing a SIGSEGV at startup before any
  image was processed. Fixed: set `feat_rep_aruco: "ANCHORED_MSCKF_INVERSE_DEPTH"`,
  added `try_zupt` block, `init_window_time: 2.0`, `init_imu_thresh: 1.0`.
- **Voxel-SVIO** - `timeshift_cam_imu_left: 0.009160379134` caused output poses
  to be on the IMU clock (+9.16 ms), so evo_ape found 0 pairs at
  `t_max_diff=0.005`. Fixed in [scripts/run/run_voxel_svio.sh](scripts/run/run_voxel_svio.sh):
  subtract the offset post-run. Verified `dt(traj-gt) = 0.000 ms`.

**Root cause of scale collapse:**

The HortiMulti robot is a ground rover that rocks and vibrates significantly -
it is NOT a stable platform. Measured IMU statistics confirm this:

| Sequence | accel std [m/s^2] | gyro std [deg/s] | gyro max [deg/s] |
|---|---|---|---|
| hortimulti str02 | **3.08** | **7.66** | **114.3** |
| hortimulti str03 | **2.51** | **6.99** | **76.4** |
| rosariov2 seq1 | 1.42 | 6.11 | 36.1 |
| rosariov2 seq5 | 1.42 | 3.93 | 30.4 |

The Allan variance values in the calibration file (accel: 1.094e-3 m/s^2/sqrt(Hz),
gyro: 6.037e-4 rad/s/sqrt(Hz)) describe the IMU's thermal noise floor -
measured while stationary in a lab. During field operation on this robot,
effective noise is ~200x higher for accel and ~20x higher for gyro.

Algorithms that initialise IMU scale tightly from the first few seconds
(Basalt, AirSLAM, OKVIS2, OpenVINS, Voxel-SVIO) receive corrupted
gravity+velocity+scale estimates during the init window. ORB-SLAM3 survives
because it runs VO for ~10 s, converges on geometric scale first, and only
fuses IMU once the map is stable - the IMU cannot override an already-locked
scale.

Note: hortimulti str02 also contains ArUco markers placed regularly in the
polytunnel rows, but none of the algorithms configured here use them (OpenVINS
`use_aruco: false`). These markers could in principle help any algorithm that
knows the physical marker size.

**Config fix (Basalt):**

Inflating `accel_noise_std` from the Allan value (0.001093618) to 0.01 (10x)
in [configs/basalt/hortimulti_calib.json](configs/basalt/hortimulti_calib.json)
reduces the weight of IMU measurements during VIO initialisation, allowing
the visual scale constraints to dominate. Results:

| Algorithm | str02 scale (run1) | str03 scale (run1) | str02 scale (run2) | str03 scale (run2) |
|---|---|---|---|---|
| Basalt | 0.537 | 0.0005 | 0.559 | **0.660** |

str03 improved from full collapse to reasonable scale (3.28 m ATE Sim3 vs 16.52 m).
str02 barely changed (25.46 m vs 26.68 m) - the 940 m long sequence accumulates
too much IMU drift over 952 s regardless of initialisation quality. Noise inflation
for gyro_noise_std (0.003, 5x) and tighter bias priors (set to Allan random-walk
values) were applied together with the accel inflation.

**AirSLAM VIO: why str02 is much worse than VO (and str03):**

AirSLAM VO on str02 scores 19.51 m (scale 0.935), but VIO scores 45.96 m
(scale 0.115). On str03 VO scores 3.35 m and VIO scores 16.33 m (scale 1.021).
On rosariov2 seq5, VIO and VO are essentially equal (12.15 m vs 11.93 m).

AirSLAM uses a delayed IMU init (ORB-SLAM3-style): it runs VO-only for the
first 3+ s and >=10 keyframes, then calls `InitializeIMU()` which jointly
solvees for gravity direction, velocity, and scale bias from the preintegrated
IMU and visual keyframe positions. The issue:

1. During the str02 init window (first ~6 s), visual keyframe displacements
   are 0.01-0.02 m (rover moving very slowly through narrow polytunnel rows).
2. The IMU has accel std of ~3.8 m/s^2 per axis at this time. With
   accel_noise_density=1.094e-3 m/s^2/sqrt(Hz), the preintegration covariance
   treats this as 200-sigma outliers rather than absorbing it as process noise.
3. `ComputeVelocity()` estimates velocities from visual displacements + IMU
   integrals. Vibration-corrupted preintegration yields incorrect velocity
   magnitudes (~0.004-0.06 m/s from the log), and the joint scale optimizer
   settles on scale=0.13 to reconcile these with the visual geometry.
4. str03 happens to be shorter (236 s vs 944 s) and has slightly lower
   vibration (gyro max 76 deg/s vs 114 deg/s). The init window happens to
   yield a consistent enough velocity estimate that scale converges correctly.

Noise inflation was tested for AirSLAM (accel_noise_density 10x, gyro 5x)
but made results *worse* on both sequences (str03 scale 1.021 -> 0.202,
str02 scale 0.130 -> 0.115). Unlike Basalt, AirSLAM has already committed
to a VO scale before IMU init; weakening IMU constraints allows the optimizer
to deviate from the visual scale rather than reinforcing it. AirSLAM config
reverted to Allan-variance noise values.

**Basalt extended tuning (5 parameter-sweep runs, best kept):**

Extensive noise parameter search was conducted to maximise Basalt's performance:
- accel_noise_std tested from 10x to 500x Allan (0.01, 0.05, 0.1, 0.5 m/s^2/sqrt(Hz))
- vio_init_ba_weight reduced from 10 (default) to 1.0 to relax initialization bias constraints
- Per-dataset vo_config (`configs/basalt/hortimulti_vo_config.json`) created with these relaxed weights

Best results (run5: accel_noise_std=0.5, vio_init_ba_weight=1.0):
- str02: ATE=22.9 m, scale=0.570 (vs VO: 2.1 m, scale=1.034)
- str03: ATE=2.85 m, scale=0.645 (vs VO: 0.275 m, scale=1.036)

Scale=0.57 means VIO overestimates travel distance by 1.75x consistently across all 5 runs
(scale ranged 0.537-0.570 for str02, 0.641-0.660 for str03). The invariance across 50x accel
noise range confirms the error is NOT driven by the noise model - it is caused by low-frequency
vibration (0.5-3 Hz from ground traversal) adding spurious acceleration that cannot be
distinguished from legitimate motion within the 100 ms camera frame interval.

**OKVIS2 hortimulti (failed - fundamental tracking issue):**

OKVIS2 run with 50x Allan noise inflation (sigma_a_c=0.0547, sigma_g_c=0.0302). Frontend
statistics from str02: 3791 TRACKING FAILURE events + 3262 RANSAC FAIL events out of 9529
frames (~40% failure rate). Trajectory diverges to millions of metres. The run with 100x
Allan + improved frontend (lower detection threshold, octaves=2, 1000 keypoints) crashed
at 85% without writing a trajectory. This is a frontend-limited failure: repetitive
greenhouse tunnel texture causes persistent 3D-2D tracking loss, not an IMU noise issue.

**Summary table (best run per algo/seq, final benchmark):**

| Algorithm | str02 ATE Sim3 | str02 scale | str03 ATE Sim3 | str03 scale | Fixable? |
|---|---|---|---|---|---|
| ORB-SLAM3 | **2.79 m** | 1.038 | **0.57 m** | 1.041 | - (best) |
| Voxel-SVIO | 6.46 m | 0.781 | 17.92 m | ~0 | no |
| Basalt (500x accel) | 22.9 m | 0.570 | 2.85 m | 0.645 | no - vibration floor |
| AirSLAM | 46.35 m | 0.130 | 16.33 m | 1.021 | no |
| OKVIS2 | 49.85 m | ~0 | 15.46 m | ~0 | no - tracking failure |
| OpenVINS | 49.43 m | ~0 | 17.03 m | ~0 | no |

**Conclusion - no further improvement possible via config tuning:**

Basalt VO (pure stereo, no IMU) achieves scale=1.034 on str02, confirming the camera
calibration is correct and visual odometry works well. Adding IMU degrades scale to 0.57
regardless of noise parameters. This is the fundamental limit: the robot's low-frequency
vibration creates systematic IMU integration errors that VIO initialization cannot
distinguish from real acceleration. The only paths to improvement on this platform are:
1. Hardware pre-filtering (vibration isolator between IMU and chassis)
2. IMU outlier rejection at the firmware level (e.g. median filter at 50+ Hz)
3. Running VO-only (Basalt VO, MAC-VO, AirSLAM VO) and accepting metric scale loss
4. Using ORB-SLAM3's deferred IMU fusion (VO-first then IMU, which already works)

For AirSLAM/OKVIS2/OpenVINS/Voxel-SVIO, no config-only fix is available. Tight-coupled
VIO systems designed for smooth MAV or automotive motion cannot reliably initialise on
this rocking ground rover.

#### OpenVINS rosariov2/sequence5 silent divergence (algorithm-level limitation)

OpenVINS on rosariov2/seq5 shows ATE 38 m / scale 0.46. The node log
(`results-vio/rosariov2/sequence5/openvins/run1/openvins_node.log`) confirms
successful initialisation and clean tracking up to ~92% of the sequence,
followed by frame-to-frame jumps of >2 m and a final position drift of
hundreds of metres. There are zero loop closures (OpenVINS has no LC mode).
This matches classic MSCKF unobserved-IMU-bias divergence on long, gently
moving outdoor sequences. No config-only fix.

### Remarks: VIO

- **hortimulti vibration floor - no config fix possible.** The robot's low-frequency vibration (0.5-3 Hz) creates systematic IMU integration errors that VIO initialization cannot distinguish from real acceleration. Only ORB-SLAM3 survives via its deferred IMU fusion (VO-first then IMU). Basalt 500x accel noise inflation confirms this: scale still collapses to 0.57 (invariant across 50x noise range = hardware limit, not a model parameter issue).
- **OKVIS2 MAP estimator requires correctly scaled IMU noise parameters.** Raw Allan-variance measurements are 12-840x too small, causing scale collapse. Corrected D435i reference values eliminate scale collapse but VIO still underperforms ORB-SLAM3 VIO (20.3 m vs 2.3 m on seq5). Proper sensor-specific Kalibr calibration would be needed for OKVIS2 to match ORB-SLAM3 VIO. OKVIS2 VO is the usable mode for this benchmark.
- **ORB-SLAM3 is the only reliable VIO algorithm on hortimulti.** All other algorithms (Basalt, AirSLAM, OKVIS2, OpenVINS, Voxel-SVIO) fail or significantly degrade due to the vibration-heavy ground rover platform.
- See detailed analysis in the hortimulti scale collapse section below, and Phase 1 detailed per-algo results.

---

## VIO-LC - Visual-Inertial + Loop Closure

| Algorithm | Dataset | Seq | ATE Sim3 | ATE SE3 | Scale | RPE [m/m] | FPS | N |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | rosariov2 | seq5 | **2.45 m** | 2.71 m | 1.023 | 0.0292 | 12.00 | 1 |
| OKVIS2 | rosariov2 | seq1 | 18.32 m | 18.77 m | 0.916 | 0.1152 | 4.72 | 1 |
| OKVIS2 | rosariov2 | seq5 | 21.25 m | 21.71 m | 0.913 | 0.1179 | 4.40 | 1 |

All N=1. ORB-SLAM3 seq5: 0 loop closures accepted (identical crop rows).
OKVIS2 seq5: 0 closures. OKVIS2 seq1: marginal improvement over VIO (18.32 vs 18.89 m).
Basalt has no loop closure mode.

### Remarks: VIO-LC

- **Loop closure provides no benefit on perceptually aliased crop-row sequences.** ORB-SLAM3 VIO-LC on rosariov2 seq5: 0 closures accepted, no ATE improvement (2.45 m vs 2.29 m VIO). Identical row appearance prevents bag-of-words place recognition.
- OKVIS2 seq1 benefits slightly (18.32 vs 18.89 m VIO) because seq1 has more turns providing revisit opportunities.
- LC roughly halves throughput for OKVIS2 (8.5 fps VIO -> 4.4 fps VIO-LC) with no meaningful ATE gain on these sequences.

---

## GNSS-VIO - Visual-Inertial + GNSS

All N=1. GPS-bearing sequences only: rosariov2 seq1/seq5, hortimulti str02/str03. EuRoC-MAV not included (no GPS).
On Rosario all four estimators recover near-metric scale (1.00-1.04); GPS provides absolute metric scale. On HortiMulti the EKF-loose `openvins_gps` instead inherits OpenVINS' VIO scale collapse (see remarks).

**seq5 now uses high-quality PPK GPS** (`/reach_1/ppk/fix`, RTK fix status 2, vertical RMSE 0.12 m vs 1.44 m conventional). seq1 still uses conventional GPS (no PPK log available locally for seq1). The seq5 rows below are the PPK results; conventional-GPS seq5 numbers are kept in the GPS-quality study further down. PPK positions were resampled onto the conventional GPS sample times so the comparison isolates data quality, not the timestamp grid (see study, point 5).

| Algorithm | Dataset | Seq | ATE Sim3 | ATE SE3 | Scale | RPE [m/m] | FPS | N |
|---|---|---|---|---|---|---|---|---|
| VINS-Fusion+GPS | rosariov2 | seq1 | 1.188 m | 1.224 m | 1.0063 | 0.180 | - | 1 |
| VINS-Fusion+GPS | rosariov2 | seq5 (PPK) | 0.911 m | 0.915 m | 1.0016 | 0.193 | - | 1 |
| VINS-Fusion+GPS | hortimulti | str02 | 4.899 m | 5.161 m | 1.0339 | 0.437 | - | 1 |
| VINS-Fusion+GPS | hortimulti | str03 | 2.395 m | 2.468 m | 1.0330 | 0.242 | - | 1 |
| CIFASIS GNSS-SI | rosariov2 | seq1 | 3.583 m | 3.695 m | 1.0194 | 0.0315 | 14.7 | 1 |
| CIFASIS GNSS-SI | rosariov2 | seq5 (PPK) | 2.062 m | 2.274 m | 1.0193 | 0.0369 | 14.6 | 1 |
| CIFASIS GNSS-SI | hortimulti | str02 | 7.256 m | 7.333 m | 1.0221 | 0.0949 | 10.0 | 1 |
| CIFASIS GNSS-SI | hortimulti | str03 | 1.502 m | 1.681 m | 1.0422 | 0.0294 | 10.0 | 1 |
| RTAB-Map+GPS | rosariov2 | seq1 | 2.138 m | 2.309 m | 1.0187 | 0.0505 | 0.91 | 1 |
| RTAB-Map+GPS | rosariov2 | seq5 (PPK) | 4.901 m | 4.926 m | 1.0110 | 0.0518 | 0.35 | 1 |
| RTAB-Map+GPS | hortimulti | str02 | 6.298 m | 6.611 m | 1.0429 | 0.1401 | 0.90 | 1 |
| RTAB-Map+GPS | hortimulti | str03 | 1.764 m | 1.829 m | 1.0269 | 0.0264 | 0.86 | 1 |
| OpenVINS+GPS (EKF) | rosariov2 | seq1 | 2.388 m | 2.589 m | 1.0216 | 0.073 | 9.8 | 1 |
| OpenVINS+GPS (EKF) | rosariov2 | seq5 (PPK) | 4.179 m | 4.227 m | 1.0132 | 0.345 | 7.8 | 1 |
| OpenVINS+GPS (EKF) | hortimulti | str02 | 30.865 m | 42.375 m | 0.5540 | 2.708 | 9.9 | 1 |
| OpenVINS+GPS (EKF) | hortimulti | str03 | 16.496 m | 48.011 m | 0.1647 | 2.897 | 9.7 | 1 |

The RTAB-Map seq5 (PPK) row is reported with low confidence: RTAB-Map's stereo odometry is non-deterministic on this sequence (exported pose counts of 363 / 284 / 134 / 22 across four runs from repeated odometry inlier loss), so a single-run conventional-vs-PPK comparison for RTAB-Map reflects odometry variance more than GPS quality. The 4.901 m row is the best full-length PPK track obtained (284 of ~363 poses). See the GPS-quality study below.

VINS-Fusion+GPS FPS not recorded (no run_meta.json). RTAB-Map+GPS: 0.35-0.91 fps (below real-time).
CIFASIS GNSS-SI: real-time (10.0 fps hortimulti, 14.6-14.7 fps rosariov2).
OpenVINS+GPS: real-time (9.7-9.9 fps). Good on Rosario, scale-collapses on HortiMulti (see remarks).

#### RTAB-Map runner fixes

Six bugs fixed in `scripts/run/run_rtabmap_gps.sh` to get correct results:

1. **pkill scope** - `pkill -f rtabmap` killed the data player too. Scoped to container process only.
2. **rgb_topic mismatch** - expected `/rgb/image_rect_color` but player published to `/cam0/image_raw`. Fixed remapping.
3. **TF missing** - no `base_link -> camera` TF published; silent pose drop. Added static TF broadcast.
4. **IMU/madgwick filter** - filter node not publishing to expected topic. Removed filter; pass IMU directly.
5. **Export path** - `rtabmap-export --output` resolves relative to the `.db` directory, mangling absolute paths into a nonexistent nested dir (silent fail). Switched to basename in db's dir + `awk` to strip `#`-header and trailing id column.
6. **GPS priors disabled** - `[Core]` section had `Optimizer\PriorsIgnored = true` (rosariov2 cfg) or loaded no INI (hortimulti cfg). Added `--Optimizer/PriorsIgnored false --Optimizer/Strategy 1 --Optimizer/Robust true`.

Result: pre-fix rosariov2 seq1 had ATE 24.26 m, scale 0.80 (GPS not fused at all). Post-fix: 2.14 m, scale 1.019.

### Remarks: GNSS-VIO

- **GPS fusion is effective on the optimisation-based estimators** - VINS-Fusion, CIFASIS and RTAB-Map all recover near-metric scale (1.00-1.04) on every sequence, including hortimulti, with no scale collapse. GPS provides absolute metric scale that overrides VIO drift. The EKF-loose `OpenVINS+GPS` is the exception: it inherits OpenVINS' VIO scale collapse on hortimulti (see below).
- **VINS-Fusion+GPS** is strongest overall, best or tied-best on three of four sequences (rosariov2 seq1: 1.19 m, seq5 PPK: 0.91 m, hortimulti str02: 4.90 m). Loosely-coupled global GPS fusion keeps trajectory globally consistent without hurting local odometry. High RPE (0.18-0.44 m/m on rosariov2) reflects small jumps from the global_fusion node, not poor local tracking. It also benefits most cleanly from the PPK GPS upgrade on seq5 (vertical RMSE -86%, ATE -5%; see GPS-quality study).
- **CIFASIS GNSS-SI** is strongest on hortimulti str03 (1.50 m) and competitive on rosariov2 seq1 (3.58 m), but weakest on hortimulti str02 (7.26 m). Tight GNSS-inertial coupling rewards clean GPS locally (lowest RPE, 0.02-0.09 m/m) but is more sensitive to noisier str02 fixes (vibration-heavy environment with GPS multipath). On seq5 the PPK upgrade improved its vertical channel (-23%) yet raised overall ATE (0.94 m -> 2.06 m) through horizontal re-balancing / run variance, illustrating that tight coupling does not guarantee an overall gain from better GPS (see GPS-quality study).
- **RTAB-Map+GPS** lands in the middle. Higher RPE (0.05-0.14 m/m) reflects sparser pose output (0.45-0.91 fps export rate) rather than poor local accuracy. The six runner fixes were essential; pre-fix GPS was not fused at all.
- **OpenVINS+GPS (robot_localization EKF)** is the only loosely-coupled *online* fusion (an EKF blends OpenVINS VIO odometry with GPS local-ENU position in real time, vs VINS-Fusion's offline pose-graph). On Rosario it is competitive (2.39 m seq1, 4.18 m seq5 PPK, scale 1.02) and real-time (7.8-9.9 fps), and notably its residual is almost purely horizontal (vertical share 1-3%) - the EKF's velocity smoothing absorbs the noisy GPS vertical channel that hurts the tighter estimators. The PPK upgrade on seq5 improved its ATE -10% (4.66 m -> 4.18 m). On HortiMulti it collapses (ATE 16-31 m, scale 0.55 and 0.16): the EKF cannot rescale a VIO that is already losing metric scale, because GPS enters only as a position correction, not as a structural scale constraint. VINS-Fusion's pose-graph and CIFASIS's tight GNSS-inertial factors both re-anchor scale globally and so survive HortiMulti where the EKF does not. This is the same VIO scale-collapse seen on the pure-VIO HortiMulti track, now visible because the loose EKF does not repair it.
- **hortimulti str02 is hardest** for the optimisation-based estimators (4.9-7.3 m ATE), consistent with the vibration-heavy, GPS-degraded conditions documented on the VIO track. The EKF-loose OpenVINS+GPS is worse still (30.9 m) because its scale collapses there.
- **Infrastructure note:** HortiMulti GPS extraction from the Buffalo SSD failed with `OSError: [Errno 5] Input/output error` (hardware read fault). GPS data recovered from already-extracted `gps.csv` files. VINS-Fusion+GPS FPS not recorded (no run_meta.json).

### GNSS-VIO accuracy investigation: vertical GPS noise

Why GNSS-VIO is not as accurate as expected, and why the residual concentrates in the vertical (z) axis.

**1. The GPS feed is vertically noisy.** Rosario v2 ships two GPS streams. The benchmark used the conventional real-time fix (`/reach_1/gps/fix`); a post-processed PPK fix (`/reach_1/ppk/fix`) is also available locally but was not extracted. Aligned to ground truth (Umeyama Sim3) on seq5:

| GPS stream | 3D RMSE | Horizontal RMSE | Vertical RMSE | Max vertical |
|---|---|---|---|---|
| Conventional (used) | 1.561 m | 0.612 m | 1.436 m | 6.18 m |
| PPK (available, unused) | 0.460 m | 0.459 m | 0.033 m | 0.16 m |

Horizontal accuracy is acceptable (~0.6 m), but the conventional vertical RMSE is 1.44 m with spikes past 6 m. PPK collapses vertical error to 3 cm (43x better). The conventional receiver's vertical channel is the weak link.

**2. The vertical error propagates into the fused trajectory.** Per-axis decomposition of the GNSS-VIO outputs (Sim3-aligned to GT) shows the vertical axis carrying most of the ATE on the tighter-coupled estimators, even though the robot is on near-flat ground (GT z-span < 0.8 m on Rosario):

| Run | 3D RMSE | Z RMSE | Vertical share of variance |
|---|---|---|---|
| CIFASIS GNSS-SI seq1 | 3.57 m | 2.98 m | 70% |
| CIFASIS GNSS-SI str03 | 1.52 m | 1.27 m | 70% |
| RTAB-Map+GPS str03 | 1.71 m | 1.64 m | 92% |
| VINS-Fusion+GPS str03 | 2.39 m | 2.04 m | 73% |
| VINS-Fusion+GPS seq5 | 0.92 m | 0.31 m | 12% |
| OpenVINS+GPS seq1 (EKF) | 2.27 m | 0.37 m | 3% |
| OpenVINS+GPS seq5 (EKF) | 4.54 m | 0.55 m | 1% |

A 1-3 m vertical RMSE on terrain that only moves 0.3-0.8 m vertically is not the robot following the ground; it is GPS vertical noise injected through the fusion. The two `OpenVINS+GPS` rows are the exception that proves the rule: the EKF's velocity-smoothed loose coupling almost entirely rejects the vertical GPS noise (3% and 1% vertical share), so its Rosario error is horizontal drift, not GPS-z leakage.

**3. Tighter GPS coupling makes it worse, not better.** This answers the natural question of whether the RTK is simply "not trusted enough". The opposite holds. The four estimators form a coupling spectrum, and vertical-noise rejection tracks looseness almost monotonically. The loosest, `OpenVINS+GPS` (a robot_localization EKF that fuses GPS only as a velocity-smoothed position correction), rejects nearly all of it (1-3% vertical share). VINS-Fusion (loose global pose-graph) is next (12-36%). CIFASIS (semi-tight, GPS as g2o position factors) and RTAB-Map (GPS as graph priors) weight the GPS measurement hardest, so the noisy vertical channel pulls the estimate most (42-92% vertical share). The assigned vertical covariance (cov_z = 4.0 m^2, i.e. 2 m sigma) is reasonable for conventional GPS; the problem is the measurement, not an overly tight weight. The caveat is that maximum looseness has its own cost: the EKF that best rejects the noise also fails to re-anchor scale, so it collapses on HortiMulti where the VIO itself drifts (see GNSS-VIO remarks).

**4. HortiMulti is worse because its GPS is consumer-grade, not RTK.** The HortiMulti `gps.csv` carries per-sample covariance and a fix-status flag. Vertical covariance is `cov_zz` 41.7 m^2 on str02 (6.5 m sigma) and 59.9 m^2 on str03 (7.7 m sigma), with `status = 0` (standard fix, not RTK = 2). Every HortiMulti GPS sample is several metres uncertain vertically, which is why HortiMulti GNSS-VIO ATE (4.9-7.3 m on str02) sits far above Rosario.

**Actionable fix (predicted):** re-extract `datasets/rosariov2/sequence5/gps.csv` from the PPK bag (`/reach_1/ppk/fix`) and re-run the GNSS-VIO sweep. Based on the noise numbers this should cut vertical error by an order of magnitude. The PPK bag is only available locally for seq5; seq1 would need its corresponding PPK log. HortiMulti has no higher-grade GPS available, so its vertical error is a hardware limit. Analysis scripts: `scripts/eval/_gps_noise_analysis.py` (stream comparison) and the per-axis decomposition documented above.

### GNSS-VIO GPS-quality study: measured PPK vs conventional (seq5)

The PPK fix above was carried out on rosariov2 seq5. All four GNSS-VIO algorithms were re-run with the high-quality PPK GPS and compared head-to-head against the conventional-GPS baseline. This is the direct measurement of how GPS data quality affects each fusion strategy.

**Method.** The PPK stream (`/reach_1/ppk/fix`, RTK fix status 2, 4201 samples) was extracted and its lat/lon/alt resampled onto the conventional GPS sample times before feeding the same players, players, covariances and runners as the baseline. Resampling onto the conventional (irregular) timestamps is deliberate: the raw PPK product ships on an exact regular 0.2 s grid, and feeding that grid directly warped VINS-Fusion's `global_fusion` 4DOF pose-graph (ATE 10.5 m, vertical span 4x ground truth) even though the PPK position values are good. Resampling removes that timestamp-grid confound so the comparison isolates GPS data quality. Horizontal PPK and conventional are near-identical (0.87 m RMS difference); only the vertical channel differs materially (PPK vertical std 0.12 m vs conventional 1.40 m).

| Algorithm | Coupling | Conv ATE Sim3 | PPK ATE Sim3 | Conv SE3 | PPK SE3 | Vertical RMSE conv -> PPK |
|---|---|---|---|---|---|---|
| VINS-Fusion+GPS | loose 4DOF pose-graph | 0.961 m | **0.911 m** | 0.964 m | 0.915 m | 0.332 m -> 0.048 m (-86%) |
| CIFASIS GNSS-SI | tight GPS factor (g2o) | 0.942 m | 2.062 m | 1.340 m | 2.274 m | 0.634 m -> 0.491 m (-23%) |
| OpenVINS+GPS (EKF) | loose EKF position | 4.661 m | **4.179 m** | 4.749 m | 4.227 m | horizontal-dominated |
| RTAB-Map+GPS | graph + GPS prior | 1.640 m | 4.901 m | 1.769 m | 4.926 m | inconclusive (see below) |

**What the PPK GPS actually fixed: the vertical channel.** The clean, repeatable result is that PPK collapses the vertical component of the fused trajectory wherever the GPS vertical actually enters the estimator. VINS-Fusion's vertical RMSE drops from 0.33 m to 0.05 m (-86%) and its overall ATE improves to 0.911 m. CIFASIS's vertical RMSE drops from 0.63 m to 0.49 m (-23%). This is exactly the predicted effect: better GPS altitude -> less vertical leakage. The vertical fix is the unambiguous GPS-quality signal.

**Overall ATE does not improve uniformly, and that is the nuanced finding.** Only the two loosely-coupled estimators improve in 3D ATE (VINS-Fusion -5%, OpenVINS -10%). The tightly-coupled CIFASIS gets worse overall (0.94 m -> 2.06 m) despite its vertical channel improving: with the vertical residual removed, its bundle adjustment re-balanced the horizontal axes and the horizontal error grew (X 0.46 m -> 1.57 m, Y 0.52 m -> 1.25 m). Two readings are consistent with this: (a) a genuine response of the tight GPS factor to a changed vertical-error profile, and (b) ORB-SLAM3 run-to-run variance (the conventional 0.94 m was a single non-deterministic run). Either way, the practical lesson is that better GPS does not automatically mean a better tightly-coupled global fit; the vertical gain is real but can be offset by horizontal re-balancing.

**RTAB-Map is inconclusive due to odometry non-determinism.** Across four PPK runs RTAB-Map's stereo odometry exported 363 / 284 / 134 / 22 poses, repeatedly logging "Not enough inliers" and "Odom quality=0" under real-time playback. GPS enters RTAB-Map only in the graph optimisation, so it cannot recover poses the odometry never produced. The conventional-vs-PPK ATE swing (1.64 m -> 4.90 m on the best 284-pose track) reflects this odometry variance, not GPS quality. A fair RTAB-Map GPS-quality comparison would need multiple runs of each condition with matched track lengths.

**Takeaways.**
- High-quality (PPK/RTK) GPS reliably improves the **vertical** accuracy of the fused estimate (-23% to -86% vertical RMSE here), because the conventional receiver's weakness is purely vertical.
- The improvement carries through to overall ATE for **loosely-coupled** fusion (VINS-Fusion, OpenVINS EKF), which is the more robust way to consume GPS.
- **Tight** coupling (CIFASIS) can re-distribute error across axes, so a vertical gain does not guarantee an overall-ATE gain.
- Estimator **non-determinism** (RTAB-Map odometry, ORB-SLAM3 bundle) can exceed the GPS-quality effect on a single run; multi-run sweeps are needed to separate the two.
- Scope: PPK applied to **seq5 only**. seq1 still uses conventional GPS (no seq1 PPK log available locally). HortiMulti has no higher-grade GPS available at all (only `/antobot_gps`, consumer fix status 0, vertical sigma ~7-8 m), so its vertical error is a hardware limit, not a fixable extraction.

---

## Algorithm coverage

| Algorithm | VO | VIO | VIO-LC | GNSS-VIO | rosariov2 | hortimulti | EuRoC |
|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | yes | yes | yes | no | seq1+seq5 VIO done (N=1) | str02+str03 VIO done (N=1) | MH_01 VIO done (N=1) |
| Basalt | yes (`--use-imu false`) | yes | no LC mode | no | seq1+seq5 VIO done (N=1) | str02+str03 VIO done (N=1, 5-run sweep) | MH_01 VIO done (N=1) |
| DROID-SLAM | yes | no IMU support | no IMU support | no | done (N=3) | done (N=3) | done (N=1) |
| MAC-VO | yes | no IMU support | no IMU support | no | done (N=3) | done (N=3) | done (N=1) |
| AirSLAM | yes | yes | yes | no | seq1+seq5 VIO done (N=1) | str02+str03 VIO done (N=1) | MH_01 VIO done (N=1) |
| OKVIS2 | yes | yes | yes | no | seq1+seq5 VIO done (N=1) | str02+str03 VIO done (N=1, failed) | MH_01 VIO done (N=1) |
| OpenVINS | no | yes | no | no | seq1+seq5 VIO done (N=1) | str02+str03 VIO done (N=1, scale collapse) | MH_01 VIO done (N=1) |
| Voxel-SVIO | no | yes | no | no | seq1+seq5 VIO done (N=1) | str02+str03 VIO done (N=1, scale collapse) | MH_01 VIO done (N=1) |
| VINS-Fusion+GPS | no | yes (base) | no | **yes** | seq1+seq5 done (N=1) | str02+str03 done (N=1) | no GPS |
| CIFASIS GNSS-SI | no | yes (base) | no | **yes** | seq1+seq5 done (N=1) | str02+str03 done (N=1) | no GPS |
| RTAB-Map+GPS | no | yes (base) | no | **yes** | seq1+seq5 done (N=1) | str02+str03 done (N=1) | no GPS |
| OpenVINS+GPS (EKF) | no | yes (base) | no | **yes** | seq1+seq5 done (N=1) | str02+str03 done (N=1, scale collapse) | no GPS |

**Gaps - possible but not yet done:**
- ORB-SLAM3 VO clean run on rosariov2/seq1, hortimulti, EuRoC (configs exist)
- Scale all N=1 VIO results to N=3 (ORB-SLAM3, Basalt, OpenVINS, AirSLAM priority)
- GNSS-VIO N=3 sweep (currently N=1)

**Not possible without hardware/code changes:**
- Reliable VIO on hortimulti for any algorithm except ORB-SLAM3 (vibration floor confirmed)
- DROID-SLAM VIO, MAC-VO VIO (no IMU support)
- Basalt VIO-LC, OpenVINS VIO-LC (no built-in loop closure)
- OpenVINS VO (MSCKF requires IMU; no vision-only mode)
- GNSS-VIO on EuRoC (no GPS in that dataset)


---

## Phase 2 - VIO Benchmark Results

## VIO Smoke Tests - rosariov2/sequence5

New multi-mode benchmarks on `rosariov2/sequence5` (11 640 frames, 15 fps, ~776 s). OKVIS2 added
as a new algorithm alongside ORB-SLAM3 and Basalt under the VO/VIO/VIO-LC structure.

### ORB-SLAM3 - rosariov2/sequence5

| Mode | ATE Sim3 | ATE SE3 | Scale | RPE [m/m] | FPS | Notes |
|---|---|---|---|---|---|---|
| VO (stereo-only) | **14.16 m** | 14.40 m | 0.949 | 0.0845 | 5.93 | No IMU; 5613 pairs |
| VIO (stereo+IMU) | **2.29 m** | 2.62 m | 1.026 | 0.0293 | 11.94 | IMU corrects scale |
| VIO-LC | **2.45 m** | 2.71 m | 1.023 | 0.0292 | 12.00 | LC on seq5 = 0 closures |

IMU reduces global ATE from 14 m to 2.3 m. VIO-LC provides no additional benefit on seq5 (0 loop
closures - long straight rows offer no revisit opportunities).

### OKVIS2 - rosariov2/sequence5 *(initial run, bad IMU params - see corrected results below)*

| Mode | ATE Sim3 | ATE SE3 | Scale | RPE [m/m] | FPS | Notes |
|---|---|---|---|---|---|---|
| VO (stereo-only) | 15.62 m | 15.74 m | 0.962 | 0.0618 | 7.29 | 11640 pairs |
| VIO (stereo+IMU) | **50.33 m** | 6085577 m | ~0 | 17.34 | 5.10 | Scale collapse - tracking failure |
| VIO-LC | **47.01 m** | 486820 m | ~0 | 4.97 | 1.71 | Scale collapse - tracking failure |

OKVIS2 VO performs comparably to ORB-SLAM3 VO (15.6 m vs 14.2 m). Both VIO and VIO-LC suffer scale
collapse (scale factor ~0): OKVIS2's IMU integration diverges on this long outdoor sequence.
A known OKVIS2 issue on sequences with large appearance changes and repetitive structure.

> **Root cause (investigated):** the CIFASIS IMU noise values are correct Allan-variance
> measurements but are **12-840x smaller** than the OKVIS2 author's own `realsense_D435i.yaml`
> defaults (`sigma_aw_c` 4.75e-05 vs 0.04 = 840x). OKVIS2's MAP estimator trusts sigmas
> literally - with too-tight noise the accel-bias state diverges and global scale collapses.
> ORB-SLAM3 and Basalt are more forgiving of tight IMU sigmas. Fix is to use OKVIS2's
> reference noise values (or any 5-10x inflation of the Allan numbers). See
> `docs/private/algorithm_comparison.md` for the full diagnostic.

### Basalt - rosariov2/sequence5

| Mode | ATE Sim3 | ATE SE3 | Scale | RPE [m/m] | FPS | Notes |
|---|---|---|---|---|---|---|
| VIO (stereo+IMU) | **4.74 m** | 4.77 m | 1.0108 | 0.0157 | **46.5** | Row ATE 18 mm, turn ATE 18 mm |

Basalt VIO is the fastest at 46x real-time with low local error (RPE 15.7 mm/m).
Global ATE 4.74 m reflects moderate scale drift without loop closure.

### Summary - rosariov2/sequence5

| Algorithm | Mode | ATE Sim3 | RPE [m/m] | FPS |
|---|---|---|---|---|
| ORB-SLAM3 | VIO | **2.29 m** | 0.0293 | 11.94 |
| ORB-SLAM3 | VIO-LC | **2.45 m** | 0.0292 | 12.00 |
| Basalt | VIO | **4.74 m** | 0.0157 | **46.5** |
| ORB-SLAM3 | VO | 14.16 m | 0.0845 | 5.93 |
| OKVIS2 | VO | 17.48 m | 0.0781 | 8.44 |
| OKVIS2 | VIO | 20.29 m | 0.1082 | 8.46 |
| OKVIS2 | VIO-LC | 21.25 m | 0.1179 | 4.40 |

OKVIS2 values are from the corrected IMU-params re-run (old bad-param results in the initial OKVIS2 table above).

ORB-SLAM3 VIO is the clear winner on seq5 (2.3 m ATE, near-real-time).
Basalt suits high-speed applications (46 fps) with moderate accuracy (4.7 m).
OKVIS2 VO (17.5 m) is comparable to ORB-SLAM3 VO (14.2 m); VIO/VIO-LC still lag ORB-SLAM3 VIO due to uncalibrated IMU noise for this specific sensor (see OKVIS2 corrected results below).

---

## OKVIS2 - corrected IMU noise re-run (rosariov2/sequence5 + sequence1)

**Root cause fixed:** CIFASIS Allan-variance IMU sigmas were 12-840x too tight for OKVIS2's MAP
estimator. Replaced with OKVIS2 D435i reference values in all 6 rosariov2 configs.
See `docs/private/algorithm_comparison.md` for the full diagnostic.

**Corrected params** (OKVIS2 D435i ref, applied to all seq1/seq5 VIO + VIO-LC configs):

| Param | Old (CIFASIS Allan) | New (OKVIS2 D435i ref) | Ratio |
|---|---|---|---|
| sigma_g_c  | 2.324e-04 | 0.00278  | 12x |
| sigma_a_c  | 9.943e-04 | 0.0252   | 25x |
| sigma_gw_c | 1.823e-06 | 0.0008   | 440x |
| sigma_aw_c | 4.750e-05 | 0.04     | 840x |

### OKVIS2 - rosariov2/sequence5 (corrected re-run, N=1)

| Mode | ATE Sim3 | ATE SE3 | Scale | RPE [m/m] | FPS | Turn ATE | Row ATE |
|---|---|---|---|---|---|---|---|
| VO (stereo-only) | **17.48 m** | 17.68 m | 0.9474 | 0.0781 | 8.44 | 0.0149 m | 0.0435 m |
| VIO (stereo+IMU) | **20.29 m** | 20.68 m | 0.9211 | 0.1082 | 8.46 | 0.0150 m | 0.0451 m |
| VIO-LC | **21.25 m** | 21.71 m | 0.9128 | 0.1179 | 4.40 | 0.0154 m | 0.0479 m |

> VO result: 17.48 m vs 15.62 m (old, bad-params) - ~2 m run-to-run variance (IMU disabled for VO).
> VIO: 20.29 m, scale 0.9211 - scale collapse is fixed (old: scale ~0, ATE 50 m), but IMU still
> hurts vs VO. Local accuracy: turn ATE 15 mm, row ATE 45 mm. D435i reference values are better
> than raw Allan but not calibrated for this specific sensor.
> VIO-LC: 21.25 m - worse than VIO because 0 actual loop closures were accepted (identical to
> ORB-SLAM3 VIO-LC on seq5). LC overhead halves throughput (8.5 fps -> 4.4 fps) with no benefit.
> 0 RANSAC failures in all three modes - clean frontend throughout.

### OKVIS2 - rosariov2/sequence1 (first run, N=1)

| Mode | ATE Sim3 | ATE SE3 | Scale | RPE [m/m] | FPS | Notes |
|---|---|---|---|---|---|---|
| VO (stereo-only) | **20.03 m** | 20.63 m | 0.8974 | 0.1381 | 8.91 | 13821 pairs |
| VIO (stereo+IMU) | **18.89 m** | 19.39 m | 0.9085 | 0.1236 | 9.93 | IMU helps on seq1 |
| VIO-LC | **18.32 m** | 18.77 m | 0.9155 | 0.1152 | 4.72 | |

> seq1 shows VIO-LC > VIO > VO (18.32 < 18.89 < 20.03 m): both IMU and loop closure help.
> Contrast with seq5 where 0 closures fired and VIO-LC hurt vs VIO.
> seq1 has more turns and revisits, giving loop closure some opportunities to fire.
> 0 RANSAC failures across all three modes - clean frontend throughout.

---


## OpenVINS integration

OpenVINS (rpng/open_vins, MSCKF stereo+IMU filter, GPL-3) added to the benchmark.
Wired via Docker only (no host build) to keep the host environment clean.

### Build & runtime

- Image: `openvins:humble` (~1.5 GB), built from
  [src/open_vins/Dockerfile.benchmark](../src/open_vins/Dockerfile.benchmark) on top of
  `ros:humble-ros-base-jammy`. Builds packages `ov_core`, `ov_init`, `ov_msckf`, `ov_eval`
  with `-DENABLE_ARUCO_TAGS=OFF`.
- Wrapper: [scripts/run/run_openvins.sh](../scripts/run/run_openvins.sh) launches
  `ros2 launch ov_msckf subscribe.launch.py` inside the image, then runs a Python
  data player ([scripts/run/openvins_data_player.py](../scripts/run/openvins_data_player.py))
  in the same container that streams `mav0/cam{0,1}/data/` and `mav0/imu0/data.csv`
  over `/cam{0,1}/image_raw` and `/imu0`, and saves `/ov_msckf/odomimu` as TUM.
- `OPENVINS_RATE` env var controls playback speed (default 1.0 = real-time).

### Run-type support

- `vio` only. OpenVINS' MSCKF requires IMU; there is no vision-only mode and no
  built-in loop closure. `vo` and `vio-lc` are rejected by the wrapper.

### Configs

`configs/openvins/<dataset>/{estimator_config.yaml, kalibr_imu_chain.yaml, kalibr_imucam_chain.yaml}`.

EuRoC-MAV: verbatim copy of the upstream `config/euroc_mav/` files.
rosariov2: hand-written from the ZED IR rectified intrinsics (fx=fy=648.86, cx=645.01,
cy=348.24, baseline=0.04973 m, gravity=9.7958) and Basalt's tuned IMU noise
(accel=1.6e-2, gyro=2.82e-4). T_imu_body identity. Distortion zeros (pre-rectified).

### Findings

1. **Dockerfile ENTRYPOINT bug.** The first build had `ENTRYPOINT ["/bin/bash","-c"]`
   which mangled the `bash -c "..."` arg vector and produced silent empty output.
   Source is fixed; the existing image is worked around at runtime with
   `--entrypoint /bin/bash`. A clean rebuild would remove the workaround.
2. **QoS mismatch silently drops messages.** OpenVINS' ROS2Visualizer subscribes
   to cameras with default `RELIABLE` QoS but to the IMU with
   `rclcpp::SensorDataQoS()` (`BEST_EFFORT`). The data player must publish each
   topic with matching QoS or `requesting incompatible QoS` warnings appear and
   no data flows.
3. **Publisher queue depth must be deep.** With `RELIABLE` QoS and the default
   depth=10, a transient slowdown in the OV node back-pressures the player's
   publish call, which (single-threaded) also stalls IMU pacing - the entire
   pipeline freezes. Cam queue is now 2000 (~67 s buffer at 30 Hz), IMU 200.
4. **Static initialization fails on moving start.** EuRoC MH_01_easy starts
   already in motion (drone hand-held). `init_dyn_use: true` is required for
   both EuRoC and rosariov2 - the static-jerk detector never trips.
5. **`ros2 launch` does not exit on SIGINT.** The wrapper now sends SIGINT, waits
   5 s, then SIGTERM, then SIGKILL on `run_subscribe_msckf` to guarantee the
   container exits.
6. **Subscriber callbacks starve under load.** The player originally interleaved
   `rclpy.spin_once()` calls between events. Once playback got even slightly
   behind real time the slack vanished, callbacks stopped firing, and pose
   collection froze while OpenVINS happily kept publishing. Fixed by spinning
   the executor in a dedicated daemon thread (`threading.Thread(rclpy.spin)`),
   so subscription delivery is decoupled from the publish-pacing loop.

### Smoke-test results (N=1)

| Dataset | Seq | ATE Sim3 | ATE SE3 | Scale | RPE [m/m] | Notes |
|---|---|---|---|---|---|---|
| EuRoC-MAV | MH_01_easy | **0.058 m** | 0.058 m | 1.0001 | 0.019 | Matches published OpenVINS benchmark (~0.09 m). 36219 poses, 3622 ATE pairs. |
| rosariov2 | sequence1 | **2.316 m** | 2.542 m | 1.0225 | 0.024 | 159863 poses, 13716 ATE pairs. RPE rot 0.227 deg/m. Per-segment ATE: turn 0.019 m, row 0.015 m. |

> EuRoC result confirms the integration is correct end-to-end.
> rosariov2 is N=1; full 3-run benchmark deferred.



---

## Phase 1 - VO-only Benchmark Results

---

## Run-type structure

The repository tracks runs along three buckets:

* `vo`     - no IMU, no LC      -> `results-vo/`, `benchmark-vo.csv`
* `vio`    - IMU on, no LC      -> `results-vio/`, `benchmark-vio.csv`
* `vio-lc` - IMU on, LC on      -> `results-vio-lc/`, `benchmark-vio-lc.csv`

The ORB-SLAM3 results in the table below were produced by the stock
`stereo_euroc` binary with loop closure enabled. Because that binary is a
pure stereo-SLAM-with-LC (no IMU), it does not fit any of the three
buckets above; the trajectories and the per-run CSV have been moved to
`obsolete/` until a VO-only build is wired in. The table is preserved
below as a reference snapshot.

---

| Algorithm | Dataset | Seq | ATE Sim3 | ATE SE3 | Scale (Sim3) | RPE [m/m] | FPS | Frames | Completion | Runs |
|---|---|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | Rosario v2 | seq1 | **1.176 ± 0.317 m** | **1.59 m** | 1.022 | 0.115 ± 0.104 | 12.53 ± 0.14 | 13 821 | 100% | **3** ✓ |
| DROID-SLAM | Rosario v2 | seq1 | 45.37 m | 45.37 m | 0.970 | 0.724 | 17.44 ± 0.21 | 13 821 | 100% | **3** ✓ |
| MAC-VO | Rosario v2 | seq1 | **13.520 ± 0.007 m** | **13.552 ± 0.007 m** | 0.980 | 0.051 | 1.71 ± 0.08 | 13 821 | 100% | **3** ✓ |
| Basalt | Rosario v2 | seq1 | **14.279 ± 0.302 m** | **18.693 ± 0.586 m** | 0.791 | 1.645 ± 0.040 | 59.44 ± 3.61 | 13 821 | 100% | **3** ✓ |
| AirSLAM | Rosario v2 | seq1 | **9.888 ± 0.059 m** | **9.891 ± 0.058 m** | 1.005 | 0.034 | 23.04 ± 3.61 | 13 821 | 100% | **3** ✓ |
| ORB-SLAM3 | Rosario v2 | seq5 | **20.207 ± 4.204 m** | **20.85 m** | 0.904 | 0.140 ± 0.062 | 11.28 ± 1.56 | 11 640 | 91% avg (0 loops) | **3** ✓ |
| DROID-SLAM | Rosario v2 | seq5 | 50.02 m | 50.24 m | 1.904 | 1.076 | 23.36 ± 0.25 | 11 640 | 100% | **3** ✓ |
| MAC-VO | Rosario v2 | seq5 | **19.384 ± 0.006 m** | **19.674 m** | 0.933 | 0.096 ± 0.000 | 1.40 ± 0.21 | 11 640 | 100% | **3** ✓ |
| Basalt | Rosario v2 | seq5 | **15.035 ± 0.062 m** | **15.425 ± 0.068 m** | 0.934 | 0.802 | 64.60 ± 2.30 | 11 640 | 100% | **3** ✓ |
| AirSLAM | Rosario v2 | seq5 | **12.722 ± 0.991 m** | **12.777 ± 1.014 m** | 0.977 | 0.055 ± 0.006 | 23.74 ± 0.48 | 11 640 | 100% | **3** ✓ |
| ORB-SLAM3 | HortiMulti | Strawberry-02 | **0.893 ± 0.139 m** | **2.10 ± 0.10 m** | 1.040 | 0.072 | 4.51 ± 0.33 | 4 186-4 980 / 9 530 | 44-52%† | **3** ✓ |
| DROID-SLAM | HortiMulti | Strawberry-02 | 38.92 m | 47.90 m | 9.590 | 4.335 | 27.95 ± 0.21 | 9 530 | 100% | **3** ✓ |
| MAC-VO | HortiMulti | Strawberry-02 | **10.231 ± 0.502 m** | **10.245 ± 0.496 m** | 1.009 | 0.096 ± 0.001 | 1.70 ± 0.04 | 9 530 | 100% | **3** ✓ |
| Basalt | HortiMulti | Strawberry-02 | **2.0978 ± 0.0008 m** | **2.664 ± 0.001 m** | 1.034 | 0.091 | 149.70 ± 4.01 | 9 530 | 100% | **3** ✓ |
| AirSLAM | HortiMulti | Strawberry-02 | **20.220 ± 0.824 m** | **20.483 ± 0.893 m** | 0.928 | 0.266 ± 0.015 | 27.37 ± 0.32 | 9 530 | 100% | **3** ✓ |
| ORB-SLAM3 | HortiMulti | Strawberry-03 | **0.1039 ± 0.0013 m** | **0.78 m** | 1.043 | 0.023 ± 0.001 | 9.39 ± 0.05 | 2 425 | 100% | **3** ✓ |
| MAC-VO | HortiMulti | Strawberry-03 | **0.505 ± 0.010 m** | **0.84 m** | 1.037 | 0.024 ± 0.001 | 1.54 ± 0.07 | 2 425 | 100% | **3** ✓ |
| Basalt | HortiMulti | Strawberry-03 | **0.2753 ± 0.0000 m** | **0.7151 m** | 1.036 | 0.022 | 143.65 ± 24.16 | 2 425 | 100% | **3** ✓ |
| AirSLAM | HortiMulti | Strawberry-03 | **3.631 ± 0.205 m** | **3.771 ± 0.191 m** | 1.064 | 0.135 ± 0.005 | 22.07 ± 10.06 | 2 425 | 100% | **3** ✓ |
| DROID-SLAM | HortiMulti | Strawberry-03 | 18.76 m | 18.81 m | 0.428 | 0.837 | 15.85 ± 0.14 | 2 425 | 100% | **3** ✓ |

### [Non-agricultural] EuRoC-MAV 

| Sequence | Algorithm | ATE Sim3 [m] | ATE SE3 [m] | RPE [m/m] | Scale | FPS | Frames |
|---|---|---|---|---|---|---|---|
| MH_01_easy | ORB-SLAM3 | 0.0340 | 0.0352 | 0.0156 | 1.0021 | 18.17 | 3682 |
| MH_01_easy | Basalt | 0.0567 | 0.0873 | 0.0085 | 1.0156 | 176.75 | 3682 |
| MH_01_easy | AirSLAM | 0.1107 | 0.1156 | 0.0195 | 1.0073 | 15.33 | 3682 |
| MH_01_easy | MAC-VO | 0.1981 | 0.1993 | 0.0295 | 1.0051 | 1.29 | 3682 |
| MH_01_easy | DROID-SLAM | 4.083 | 7.891 | 0.500 | 0.173 | 13.17 | 3682 |
| MH_03_medium | ORB-SLAM3 | 0.0437 | 0.0520 | 0.0179 | 0.9922 | 17.89 | 2700 |
| MH_03_medium | Basalt | 0.1372 | 0.1397 | 0.0159 | 1.0075 | 113.47 | 2700 |
| MH_03_medium | AirSLAM | 0.1431 | 0.1443 | 0.0188 | 0.9950 | 31.73 | 2700 |
| MH_03_medium | MAC-VO | 0.3403 | 0.3405 | 0.0187 | 0.9961 | 1.15 | 2700 |
| MH_03_medium | DROID-SLAM | 3.523 | 7.105 | 2.274 | 0.082 | 10.94 | 2700 |
| MH_05_difficult | ORB-SLAM3 | 0.0720 | 0.0781 | 0.2282 | 0.9956 | 17.97 | 2273 |
| MH_05_difficult | Basalt | 0.1816 | 0.1931 | 0.0870 | 1.0097 | 108.72 | 2273 |
| MH_05_difficult | AirSLAM | 0.2968 | 0.3066 | 0.0256 | 1.0116 | 34.92 | 2273 |
| MH_05_difficult | MAC-VO | 0.4697 | 0.4836 | 0.0276 | 1.0172 | 0.86 | 2273 |
| MH_05_difficult | DROID-SLAM | 6.594 | 8.514 | 0.786 | 0.248 | 13.85 | 2273 |

† ORB-SLAM3 processed all 9 530 input frames but tracking only succeeded for frames
spanning 91 s - 500 s of the 952 s sequence.  Tracking was permanently lost after 500 s
due to the repetitive polytunnel environment.  This is **not** a stride/sampling issue.  

All multi-run metrics use **both Sim(3) and SE(3)** alignment (`evo_ape --align [--correct_scale]`) and
**`point_distance` RPE** (not `trans_part` - avoids body-frame quaternion mismatch).

---

## Sim(3) vs SE(3) alignment for stereo 

Stereo SLAM has **metric scale** (from the baseline), so SE(3) ATE is the
accuracy metric. Sim(3) absorbs residual scale drift into a 7th DoF
alignment scale factor, hiding error:

| Sequence | Sim3 ATE | SE3 ATE | Scale | Scale drift |
|---|---|---|---|---|
| Rosario seq1 | 1.18 m | 1.59 m | 1.022 | 2.2 % |
| Rosario seq5 | 20.21 m | 20.85 m | 0.904 | 10 % |
| Strawberry-02 | 0.89 m | 2.10 m | 1.040 | 4.0 % |
| **Strawberry-03** | **0.10 m** | **0.78 m** | **1.043** | **4.3 %** |


---

## RPE rotation anomaly on HortiMulti (Strawberry-03 17.6 °/m) - resolved as artefact

ORB-SLAM3 outputs poses in the **camera optical frame**; HortiMulti GT is in a
**robot base frame** rotated by a near-constant **≈120°** mount offset. Sim3/SE3
translation alignment does not fix per-frame body orientation. The constant
mismatch makes `R_gt_rel · R_est_rel⁻¹` non-cancelling whenever the body
rotation axis is not aligned with the mismatch axis.

Diagnostic measurement on Strawberry-03 run1:
- Per-frame abs orientation diff: **mean 119.46°, median 119.40°, range 116-120°** (constant)
- Manual RPE rot (1 m windows): mean 13.7°, **median only 3.45°**, RMSE 26.2°
- Distribution is heavy-tailed because high errors occur only on certain body axes

**Conclusion:** RPE rotation = 17.6 °/m on Strawberry-03 is a frame-mismatch
artefact, NOT an ORB-SLAM3 accuracy issue. Documented in
`docs/evalutation/10_evaluation_protocol.md` §14. Future work: pre-multiply
estimate by a learned constant $R_0$ before RPE rotation evaluation.

---



## Dataset 1 - Rosario v2 - Complete

### Sequence 1 - ORB-SLAM3 × 3 benchmark complete ✓

- **Results in:** `results/rosariov2/sequence1/orbslam3/` - `metrics.csv`, `report.md`, `segment_map.png`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE | **1.176 ± 0.317 m** |
| RPE (point\_distance, 1 m) | 0.115 ± 0.104 m (high var due to tracking-loss reloc boundary) |
| RPE rotation | 0.416 ± 0.139 °/m |
| Scale factor | 1.022 ± 0.001 |
| Frames tracked | 100% all 3 runs (tracking-loss + reloc ~t=645s) |
| Loop closures | 5-6 |
| Mean FPS | 12.53 ± 0.14 (0.84× real-time @ 15 fps) |
| Row ATE RMSE (125 segs, avg 6.9 s) | 0.016 ± 0.003 m |
| Turn ATE RMSE (20 segs, avg 3.0 s) | 0.022 ± 0.003 m |

> High ATE variation (0.79-1.57 m across 3 runs) is expected: loop closure timing nondeterminism
> causes different GBA corrections. Per-segment ATE is more stable (cv < 20%).
> Run2 RPE outlier (0.261 vs 0.029-0.055) caused by trajectory discontinuity at reloc boundary.

### Sequence 1 - ORB-SLAM3 × 3 + MAC-VO × 3 complete

- **Extracted to:** `datasets/rosariov2/sequence1/`
- **GT:** 8983 poses (GPS/PGT), 13821 camera frames; `gt_interp_tum.txt` generated✔
- **Segments:** 125 row segs (863 s), 20 turn segs (60 s) - `segments_auto.csv` generated✔
- **Config files:** ORB-SLAM3: `configs/orbslam3/rosariov2_stereo.yaml` · DROID-SLAM: `configs/droidslam/rosariov2.txt` · MAC-VO: `configs/macvo/rosariov2_sequence1.yaml`

| Algorithm | ATE RMSE Sim3 | Frames | Completion | Runs |
|---|---|---|---|---|
| ORB-SLAM3 | **1.176 ± 0.317 m** | 13 821 | 100% | **3** ✓ |
| DROID-SLAM | **45.37 ± 0.000 m** | 13 821 | 100% | **3** ✓ |
| MAC-VO | **13.520 ± 0.007 m** | 13 821 | 100% | **3** ✓ |
| Basalt | **14.279 ± 0.302 m** | 13 821 | 100% | **3** ✓ |
| AirSLAM | **9.888 ± 0.059 m** | 13 821 | 100% | **3** ✓ |
#### MAC-VO × 3 - Sequence 1 complete

> Full report: `results/rosariov2/sequence1/macvo/report.md`

#### Basalt × 3 - Sequence 1 complete

> Full report: `results/rosariov2/sequence1/basalt/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **14.279 ± 0.302 m** |
| ATE RMSE SE3 | **18.693 ± 0.586 m** |
| RPE (point\_distance, 1 m) | 1.6454 ± 0.0398 m/m |
| RPE rotation | 0.535 ± 0.013 °/m |
| Scale factor (Sim3) | 0.791 ± 0.008 (**20.9 % drift**) |
| Frames tracked | 100% (13 821 / 13 821, 0 losses, all 3 runs) |
| Mean FPS | 59.44 ± 3.61 (4.0x real-time @ 15 fps) |
| Row ATE RMSE (73 segs) | 0.0140 ± 0.0000 m |
| Turn ATE RMSE (34 segs) | 0.1609 ± 0.0003 m |

> Global ATE 14.3 m vs local row ATE 14 mm - a 1021x ratio, driven by scale drift (scale=0.79).
> Without scale correction (SE3 ATE = 18.7 m) the drift is even more pronounced.
> Local accuracy (row ATE 14 mm) is comparable to ORB-SLAM3 (16 mm) and MAC-VO (20 mm),
> confirming that Basalt tracks accurately per-frame but accumulates large global scale error
> on this long outdoor sequence (~940 m trajectory) without loop closure.
> Runs 2 and 3 nearly identical (ATE 14.04 vs 14.09 m); run1 slightly higher (14.70 m) due to
> multi-threaded input timing variation at startup.

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **13.520 ± 0.007 m** |
| ATE RMSE SE3  | **13.552 ± 0.007 m** |
| RPE (point\_distance, 1 m) | 0.0508 ± 0.0001 m/m |
| Scale factor | 0.980 ± 0.000 (**2.0 % drift**) |
| Frames tracked | 100% (13 821 / 13 821, all 3 runs) |
| Mean FPS | 1.71 ± 0.08 (0.11x real-time @ 15 fps) |
| Row ATE RMSE (73 segs) | 0.0200 ± 0.0000 m |
| Turn ATE RMSE (34 segs) | 0.0174 ± 0.0000 m |

> Exceptionally stable across runs: ATE std only 7 mm over 13821 frames.
> Global ATE (~13.5 m) vs local row ATE (20 mm) - 675x ratio, driven by
> accumulated scale drift. Compare ORB-SLAM3 on same sequence: 1.18 m global
> ATE thanks to 5-6 loop closures correcting drift. MAC-VO has no loop closure.

#### AirSLAM × 3 - Sequence 1 complete ✓

> Full report: `results/rosariov2/sequence1/airslam/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **9.888 ± 0.059 m** |
| ATE RMSE SE3 | **9.891 ± 0.058 m** |
| RPE (point\_distance, 1 m) | 0.0342 m |
| Scale factor (Sim3) | 1.0052 ± 0.0003 (**0.52% drift**) |
| Frames tracked | 100% (13 821 / 13 821, 0 losses, all 3 runs) |
| Loop closures | 0 (all 3 runs) |
| Mean FPS | 23.04 ± 3.61 (wall-clock) |
| Row ATE RMSE | 0.0192 m |
| Turn ATE RMSE | 0.0185 m |

> Near-unity scale (1.005) confirms AirSLAM maintains correct metric scale on this sequence.
> No loop closures needed  -  direct scale preservation. Global ATE ~9.9 m over ~940 m trajectory
> (1.05% of path length). Comparable to MAC-VO (13.5 m) and Basalt (14.3 m).
> Individual runs: run1=9.958 m (17.98 fps), run2=9.814 m (24.98 fps), run3=9.893 m (26.17 fps).
> High wall-time variance (run1=769s vs run2+3≈540s) due to TRT engine compilation on run1.

#### DROID-SLAM × 3 - Sequence 1 complete

> Full report: `results/rosariov2/sequence1/droidslam/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **45.369 ± 0.000 m** |
| ATE RMSE SE3 | **45.371 ± 0.000 m** |
| RPE (point\_distance, 1 m) | 0.724 ± 0.005 m/m |
| Scale factor (Sim3) | 0.970 ± 0.000 (**3.0% under-scale**) |
| Frames tracked | 100% (13 821 / 13 821, all 3 runs) |
| Loop closures | 0 (all 3 runs) |
| Mean FPS | 17.44 ± 0.21 (1.16x real-time @ 15 fps) |
| VRAM peak | ~11.9 GiB |
| Row ATE RMSE (18 segs) | 7.90 m |
| Turn ATE RMSE (5 segs) | 0.44 m |

> **Method:** run with `--filter_thresh 6.0` (the lowest value that fits in VRAM) and `--stride 1`
> (all frames). `filter_thresh` controls the minimum optical-flow confidence required to retain a
> frame in the DROID bundle adjustment window. A lower threshold keeps more frames but uses more VRAM;
> 6.0 was the minimum feasible value on this hardware without OOM.
>
> Despite full-frame coverage (vs the earlier stride=2 test at 50% coverage) the global ATE barely
> changed (45.37 m vs 45.00 m). Scale improved significantly (0.970 vs 1.221), but ATE remained
> ~45 m because scale is only 3% off - the error is dominated by trajectory shape divergence, not
> scale. This is a domain-mismatch failure: DROID-SLAM's optical flow network was never trained
> on outdoor crop-row imagery and cannot track reliably across the long open-field sections.

#### AirSLAM × 3 - Sequence 5 complete ✓

> Full report: `results/rosariov2/sequence5/airslam/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **12.722 ± 0.991 m** |
| ATE RMSE SE3 | **12.777 ± 1.014 m** |
| RPE (point\_distance, 1 m) | 0.0552 ± 0.0063 m/m |
| RPE rotation | 0.299 ± 0.001 °/m |
| Scale factor (Sim3) | 0.9765 ± 0.0057 (**2.4% drift**) |
| Frames tracked | 100% (11 640 / 11 640, 0 losses, all 3 runs) |
| Loop closures | 0 (all 3 runs) |
| Mean FPS | 23.74 ± 0.48 (wall-clock) |
| Row ATE RMSE | 0.0470 ± 0.0022 m (34 segs) |
| Turn ATE RMSE | 0.0106 ± 0.0001 m (18 segs) |

> Scale factor 0.977 (2.4% drift) is slightly worse than seq1 (1.005, 0.5% drift).
> Global ATE 12.7 m vs local row ATE 47 mm  -  270× ratio showing long-range scale accumulation.
> No loop closures detected on all 3 runs. Run3 significantly higher ATE (14.12 m) vs run1+2 (~12 m),
> causing higher std (0.99 m) than other seqs.
> Individual runs: run1=12.114 m (23.82 fps), run2=11.932 m (23.13 fps), run3=14.119 m (24.29 fps).

### Sequence 5 - ORB-SLAM3 × 3 benchmark complete ✓

- **Sequence:** 11 640 frames, 1280×720, ~13 min, stereo + PGT GT
- **Extracted to:** `datasets/rosariov2/sequence5/`
- **GT:** 7577 poses; `gt_interp_tum.txt` generated ✔
- **Segments:** 95 row segs (756 s), 6 turn segs (19 s) - `segments_auto.csv` generated ✔
- **Results in:** `results/rosariov2/sequence5/orbslam3/` - `metrics.csv`, `report.md`, `segment_map.png`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE | **20.207 ± 4.204 m** |
| RPE (point\_distance, 1 m) | 0.140 ± 0.062 m |
| RPE rotation | 0.273 ± 0.031 °/m |
| Scale factor | 0.904 ± 0.047 |
| Frames tracked | 91.0 ± 12.7% (run2: 73.1% permanent failure at t≈683s) |
| Loop closures | 0 (all 3 runs) |
| Mean FPS | 11.28 ± 1.56 |
| Row ATE RMSE (~86 segs, avg 8.0 s) | 0.016 ± 0.000 m |
| Turn ATE RMSE (~5 segs, avg 3.3 s) | 0.014 ± 0.003 m |

> Key finding: 0 loop closures → scale drift accumulates over 160 m of straight rows.
> Global ATE 20 m vs local segment ATE 0.016 m - a 1250× ratio.
> Contrast with seq1: 5-6 loop closures → ATE only 1.18 m on a similar-length sequence.

| Algorithm | ATE RMSE | Frames | Completion | Runs |
|---|---|---|---|---|
| ORB-SLAM3 | **20.207 ± 4.204 m** | 11 640 | 91% avg | **3** ✓ |
| DROID-SLAM | **50.02 m** | 11 640 | 100% | **3** ✓ |
| MAC-VO | **19.384 ± 0.006 m** | 11 640 | 100% | **3** ✓ |
| Basalt | **15.035 ± 0.062 m** | 11 640 | 100% | **3** ✓ |
| AirSLAM | **12.722 ± 0.991 m** | 11 640 | 100% | **3** ✓ |

#### Basalt × 3 - Sequence 5 complete

> Full report: `results/rosariov2/sequence5/basalt/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **15.035 ± 0.062 m** |
| ATE RMSE SE3 | **15.425 ± 0.068 m** |
| RPE (point\_distance, 1 m) | 0.8021 ± 0.0005 m/m |
| RPE rotation | 0.2797 ± 0.0009 °/m |
| Scale factor (Sim3) | 0.9339 ± 0.0007 (**6.6 % drift**) |
| Frames tracked | 100% (11 640 / 11 640, 0 losses, all 3 runs) |
| Mean FPS | 64.60 ± 2.30 (4.3x real-time @ 15 fps) |
| Row ATE RMSE (34 segs) | 0.0211 ± 0.0001 m |
| Turn ATE RMSE (19 segs) | 0.0911 ± 0.0000 m |

> Better scale than seq1 (0.934 vs 0.791): different route geometry reduces cumulative drift.
> Local row ATE 21 mm is close to ORB-SLAM3 seq5 row ATE (16 mm).
> Global ATE 15.0 m reflects uncorrected scale drift over the full sequence without loop closure.
> Near-symmetric Sim3/SE3 ATEs (15.0 m vs 15.4 m) indicate small scale drift relative to seq1 (14.3 vs 18.7 m).

### Rosario v2 observations (updated with 3-run benchmarks)
- ORB-SLAM3 seq1: 1.176 m - 5-6 loop closures enable global correction → low drift
- DROID-SLAM seq1: 45.37 m (3 runs, scale=0.970, filter_thresh=6.0) - domain-mismatch failure, ~45 m both with stride=2 and stride=1
- DROID-SLAM seq5: 50.02 m (3 runs, scale=1.904) - same failure mode, slightly worse
- ORB-SLAM3 seq5: 20.207 m - 0 loop closures, long straight rows → uncorrected scale drift
- DROID-SLAM consistently very poor (~45-50 m both seqs); full-frame run (filter_thresh=6.0) confirms it is a domain-mismatch failure, not a sampling issue
- MAC-VO seq1: 13.520 ± 0.007 m (3 runs) - no loop closure, scale drift 2%; local row ATE 0.020 m
- MAC-VO seq5: 19.384 ± 0.006 m (3 runs) - no loop closure, scale drift 6.7%; local row ATE 0.045 m
- Basalt seq1: 14.279 ± 0.302 m (3 runs) - scale drift 20.9%; local row ATE 14 mm (matches ORB-SLAM3)
- Basalt seq5: 15.035 ± 0.062 m (3 runs) - scale drift 6.6%; better than seq1 due to route geometry
- AirSLAM seq1: **DONE** (9.888 ± 0.059 m Sim3, 100% tracking, scale=1.005, 23.04 fps)
- AirSLAM seq5: **DONE** (12.722 ± 0.991 m Sim3, 100% tracking, scale=0.977, 23.74 fps)
- **Local accuracy is similar for all algorithms**: row ATE 0.016-0.021 m for ORB-SLAM3, MAC-VO, and Basalt on seq1/seq5

---

## Dataset 2 - HortiMulti - Complete

 - ORB-SLAM3 × 3 + MAC-VO × 3 + Basalt × 3 + AirSLAM × 3 + DROID-SLAM × 3 complete on all sequences.

- **Sequence:** Feb2026, 9530 frames, 952 s, 41 GB bag
- **Camera:** Basler acA1920-155uc, fisheye (equidistant) distortion, 2048×1536 native
- **Extracted to:** `datasets/hortimulti/strawberry02/` - 9530 stereo pairs at 640×480
- **Results in:** `results/hortimulti/strawberry02/`

#### ORB-SLAM3 × 3 benchmark (Phase B, current)

> Full report: `results/hortimulti/strawberry02/orbslam3/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim(3) | **0.893 ± 0.171 m** |
| ATE RMSE SE(3)  | **2.103 ± 0.118 m** |
| RPE (point_distance, 1 m) | 0.0716 ± 0.0008 m |
| RPE rotation (1 m) | 10.56 ± 1.11 °/m (frame-mismatch artefact - see §RPE rotation) |
| Scale factor (Sim3) | 1.040 ± 0.001 (**4 % drift**) |
| Frames tracked | 4 186 / 4 441 / 4 980 of 9 530 → **44-52 % timeline coverage** |
| Loop closures | 0 (all 3 runs) |
| Tracking losses | 0 hard losses; Atlas Map 2 created at t≈541 s every run |
| Wall-clock per run | ~1 005 s (≈ real-time at 10 Hz input) |
| Row ATE RMSE | 0.0845 ± 0.0064 m (~9 segs/run, avg ~50 s) |
| Turn ATE RMSE | 0.0665 ± 0.0038 m (~5 segs/run, avg ~12 s) |

> Strawberry-02 is significantly harder than Strawberry-03: tracking dies
> permanently around 541 s of the 952 s sequence due to the repetitive
> polytunnel imagery (every run reproduces this). Sim3 hides 4 % scale drift;
> SE3 ATE is **2.36× larger** (0.89 → 2.10 m). No loop closures means the
> drift is uncorrected.

| Algorithm | ATE RMSE Sim3 | Frames | Completion | Runs |
|---|---|---|---|---|
| **ORB-SLAM3 × 3** | **0.893 ± 0.171 m** (SE3 2.10 ± 0.12) | 4 186-4 980 | 44-52% timeline | **3** ✓ |
| DROID-SLAM | **38.92 m** | 9 530 | 100% | **3** ✓ |
| MAC-VO | **10.231 ± 0.502 m** | 9 530 | 100% | **3** ✓ |
| Basalt | **2.0978 ± 0.0008 m** | 9 530 | 100% | **3** ✓ |
| AirSLAM | **20.220 ± 0.824 m** | 9 530 | **100%** | **3** ✓ |

#### MAC-VO × 3 - Strawberry-02 complete

> Full report: `results/hortimulti/strawberry02/macvo/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **10.231 ± 0.502 m** |
| ATE RMSE SE3  | **10.940 ± 0.545 m** |
| RPE (point\_distance, 1 m) | 0.0960 ± 0.0012 m/m |
| Scale factor | 1.009 ± 0.003 (**0.9 % drift**) |
| Frames tracked | 100% (9 530 / 9 530, all 3 runs) |
| Mean FPS | 1.70 ± 0.04 (0.17x real-time @ 10 fps) |
| Row ATE RMSE (16 segs) | 0.587 ± 0.008 m |
| Turn ATE RMSE (9 segs) | 0.0845 ± 0.0001 m |

> MAC-VO tracks 100% of frames (vs ORB-SLAM3 44-52%) at the cost of ~6x lower
> speed. Global ATE (~10 m over 952 s) reflects scale drift on the much longer
> sequence; scale factor is near 1.0 (only 0.9% drift) so Sim3 and SE3 ATEs
> converge. Turn ATE (0.085 m) is tighter than row ATE (0.587 m) as expected.

#### Basalt × 3 - Strawberry-02 complete

> Full report: `results/hortimulti/strawberry02/basalt/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **2.0978 ± 0.0008 m** |
| ATE RMSE SE3 | **2.664 ± 0.001 m** |
| RPE (point\_distance, 1 m) | 0.0910 ± 0.0000 m/m |
| RPE rotation | 10.966 ± 0.000 °/m (frame-mismatch artefact) |
| Scale factor (Sim3) | 1.034 (**3.4 % drift**) |
| Frames tracked | 100% (9 530 / 9 530, 0 losses, all 3 runs) |
| Mean FPS | 149.70 ± 4.01 (15.0x real-time @ 10 fps) |
| Row ATE RMSE (16 segs) | 0.1366 ± 0.0000 m |
| Turn ATE RMSE (9 segs) | 0.0806 ± 0.0000 m |

> Unlike ORB-SLAM3 (44-52% timeline coverage), Basalt tracks 100% of the 952 s sequence.
> Global ATE 2.10 m vs ORB-SLAM3 0.89 m Sim3 - but ORB-SLAM3 only covers half the trajectory.
> Scale drift only 3.4% (Sim3 ATE 2.10 m vs SE3 ATE 2.66 m - 1.27x ratio).
> Local row ATE 137 mm is larger than str03 (27 mm) due to the longer, more repetitive sequence.
> Perfectly deterministic across 3 runs: ATE std = 0.8 mm.

#### AirSLAM × 3 - Strawberry-02 complete

> Full report: `results/hortimulti/strawberry02/airslam/report.md`

| Metric | Value (mean ± std, N=3) |
|---|---|
| ATE RMSE Sim(3) [m] | **20.220 ± 0.824** |
| ATE RMSE SE(3) [m]  | **20.483 ± 0.893** |
| RPE (point_distance, 1 m) [m] | 0.2662 ± 0.0152 |
| RPE rotation (1 m) [°/m] | 13.94 ± 0.27 |
| Scale factor (Sim3) | 0.9278 ± 0.0103 (**7.2 % under-scale**) |
| Frames tracked | 9 530 / 9 530 → **100 %** (all 3 runs) |
| Keyframes per run | 1 938 |
| Tracking losses / loop closures | 0 / 0 |
| Wall-clock [s] | 348 / 343 / 353 |
| FPS (wall-clock) | **27.37 ± 0.32** |
| VRAM mean / peak [MiB] | 2 994 / 3 061 |
| Final drift [m] | 71.43 ± 6.39 |
| Row ATE RMSE (15 segs) | 0.3977 ± 0.0060 m |
| Turn ATE RMSE (7 segs) | 0.1163 ± 0.0004 m |

> AirSLAM achieves 100% tracking on the full 952 s sequence (no loop closure needed for tracking),
> but without global optimization drifts to 20.22 m global ATE (significantly worse than ORB-SLAM3's
> 0.89 m on 44-52% coverage, or Basalt's 2.10 m on 100%). Under-scale 7.2% contributes to SE3 ≈ Sim3.

### Strawberry-03 - ORB-SLAM3 × 3 + MAC-VO × 3 + Basalt × 3 complete

- **Sequence:** Feb2026, 2425 frames, 242 s, 11 GB bag
- **Extracted to:** `datasets/hortimulti/strawberry03/` - 2425 stereo pairs at 640×480
- **Results in:** `results/hortimulti/strawberry03/orbslam3/` + `results/hortimulti/strawberry03/macvo/` - 3 runs each, `metrics.csv`, `report.md`, `segment_map.png`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE | **0.1039 ± 0.0013 m** |
| RPE (point\_distance, 1 m) | **0.0226 ± 0.0006 m** |
| RPE rotation | 17.62 ± 0.06 °/m |
| Scale factor (Sim3) | 1.0428 ± 0.0002 |
| Frames tracked | 100% (0 losses, 1 loop closure) |
| Mean FPS | 9.39 ± 0.05 (0.94× real-time @ 10 fps) |
| Row ATE RMSE (8 segs, avg 28 s) | 0.030 ± 0.001 m |
| Turn ATE RMSE (4 segs, avg 4.4 s) | 0.012 ± 0.0001 m |

> **Turn ATE < Row ATE** is expected: turns are 4-8 s vs rows 22-65 s.
> Shorter segments accumulate less drift and fit more tightly in per-segment Sim3 alignment.

#### MAC-VO × 3 - Strawberry-03 complete

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **0.505 ± 0.010 m** |
| ATE RMSE SE3  | **0.838 ± 0.008 m** |
| RPE (point\_distance, 1 m) | 0.0236 ± 0.0005 m/m |
| Scale factor | 1.037 ± 0.000 |
| Frames tracked | 100% (5 row segs, 5 turn segs) |
| Mean FPS | 1.54 ± 0.07 (0.154x real-time @ 10 fps) |
| Row ATE RMSE (5 segs) | 0.166 ± 0.001 m |
| Turn ATE RMSE (5 segs) | 0.031 ± 0.000 m |

> MAC-VO drift on rows (0.166 m) is ~5.5x the ORB-SLAM3 row ATE (0.030 m).
> Turn ATE (0.031 m) is comparable to ORB-SLAM3 (0.012 m × 2.5).
> Speed: 1.54 fps vs ORB-SLAM3 9.39 fps - ~6x slower.

#### Basalt × 3 - Strawberry-03 complete

> Full report: `results/hortimulti/strawberry03/basalt/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **0.2753 ± 0.0000 m** |
| ATE RMSE SE3 | **0.7151 m** |
| RPE (point\_distance, 1 m) | 0.0223 ± 0.0000 m/m |
| RPE rotation | 17.605 ± 0.000 °/m (frame-mismatch artefact) |
| Scale factor (Sim3) | 1.036 |
| Frames tracked | 100% (2 425 / 2 425, 0 losses, all 3 runs) |
| Mean FPS | 143.65 ± 24.16 (10.9-16.2x real-time @ 10 fps; varies with system load) |
| Row ATE RMSE (5 segs) | 0.0274 ± 0.0000 m |
| Turn ATE RMSE (5 segs) | 0.0280 ± 0.0000 m |

> Basalt sits between ORB-SLAM3 (0.10 m) and MAC-VO (0.505 m) on global ATE.
> RPE 22 mm/m and row ATE 27 mm are close to ORB-SLAM3 (RPE 22.6 mm, row 30 mm),
> confirming that Basalt's sliding-window optimizer matches ORB-SLAM3 local accuracy
> without loop closure. Speed: 143 fps mean - the fastest algorithm on this sequence.
> Perfectly deterministic (ATE std = 0.0000 m): all 3 runs produce identical trajectory to 4 decimal places.

| Algorithm | ATE RMSE Sim3 | ATE SE3 | Scale | FPS | Frames | Completion | Runs |
|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | **0.1039 ± 0.0013 m** | 0.78 m | 1.043 | 9.39 | 2 425 | **100%** | **3** ✓ |
| Basalt | **0.2753 ± 0.0000 m** | 0.72 m | 1.036 | 143.65 | 2 425 | **100%** | **3** ✓ |
| MAC-VO | **0.505 ± 0.010 m** | 0.84 m | 1.037 | 1.54 | 2 425 | **100%** | **3** ✓ |
| AirSLAM | **3.631 ± 0.205 m** | 3.771 ± 0.191 m | 1.064 | 22.07 | 2 425 | **100%** | **3** ✓ |
| DROID-SLAM | **18.76 m** | 18.81 m | 0.428 | 15.85 | 2 425 | **100%** | **3** ✓ |

#### AirSLAM × 3 - Strawberry-03 complete

> Full report: `results/hortimulti/strawberry03/airslam/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **3.6314 ± 0.2047 m** |
| ATE RMSE SE3 | **3.7711 ± 0.1906 m** |
| RPE (point\_distance, 1 m) | 0.1350 ± 0.0052 m/m |
| RPE rotation | 19.514 ± 0.004 °/m (frame-mismatch artefact) |
| Scale factor (Sim3) | 1.0639 ± 0.0029 (**6.4 % drift**) |
| Frames tracked | 100% (2 425 / 2 425, 0 losses, all 3 runs) |
| Mean FPS | 22.07 ± 10.06 (run1: 7.83 fps incl. TRT compile; run2+3: 29.18 fps) |
| VRAM mean | 2841 MiB (3061 MiB peak) |
| Row ATE RMSE (5 segs, avg 34.7 s) | 0.2025 ± 0.0124 m |
| Turn ATE RMSE (4 segs, avg 16.0 s) | 0.0505 ± 0.0207 m |

> AirSLAM global ATE (3.63 m) is significantly higher than ORB-SLAM3 (0.10 m), Basalt (0.28 m),
> and MAC-VO (0.51 m) on this short sequence. 100% completion and 0 tracking losses, but large
> accumulated drift without loop closure. Run1 was slow (7.83 fps) due to TRT engine compilation;
> runs 2+3 run at 29.18 fps (~3x real-time at 10 fps input). Local turn ATE (50.5 mm) is
> reasonable; row ATE (202.5 mm) is ~7x worse than ORB-SLAM3 (30 mm).

#### DROID-SLAM × 3 - Strawberry-03 complete

> Full report: `results/hortimulti/strawberry03/droidslam/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---------|
| ATE RMSE Sim3 | **18.76 m** |
| ATE RMSE SE3 | **18.81 m** |
| RPE (point\_distance, 1 m) | 0.837 m/m |
| Scale factor (Sim3) | 0.428 (**57.2 % under-scale**) |
| Frames tracked | 100% (2 425 / 2 425, all 3 runs) |
| Mean FPS | 15.85 ± 0.14 |
| VRAM peak | ~7 500 MiB |

> Massive scale collapse (scale 0.428) is the primary failure mode: DROID-SLAM
> interprets this short polytunnel sequence as if the world is ~2.3x smaller than
> it is. The Sim3 and SE3 ATEs are nearly identical (18.76 vs 18.81 m) because
> scale error dominates - re-scaling the trajectory moves it only 50 mm. Global
> ATE 18.76 m is 180x worse than ORB-SLAM3 on the same sequence (0.104 m).
> RPE 0.837 m/m confirms per-frame odometry also fails - not just global drift.
> This is consistent with str02 (scale 9.59, ATE 38.92 m): DROID-SLAM trained
> on TartanAir/FlyingThings3D has never seen agricultural polytunnel imagery.

### Config files

- ORB-SLAM3: `configs/orbslam3/hortimulti_stereo.yaml` (shared across all HortiMulti seqs)
- DROID-SLAM: `configs/droidslam/hortimulti.txt` (**no comments** - parser crashes on `#`)
- MAC-VO: `configs/macvo/hortimulti_sequence.yaml` (update `root:` path per sequence)

### HortiMulti observations

- ORB-SLAM3 best global accuracy on str03 (0.10 m Sim3); tracking lost on str02 after 44-52% of timeline (repetitive polytunnel)
- MAC-VO 100% completion on both sequences; ATE 10 m on str02 (long, ~953 s) vs 0.505 m on str03 (short, ~242 s) - drift scales with sequence length
- DROID-SLAM str02: **38.92 m** (3 runs, 9530 frames, scale=9.59) - massive over-scale collapse
- DROID-SLAM str03: **18.76 m** (3 runs, 2425 frames, scale=0.428, FPS=15.85) - massive under-scale collapse
- Basalt str03: 0.2753 ± 0.0000 m (3 runs, 143 fps, 100% tracking) - between ORB-SLAM3 and MAC-VO globally; local row ATE 27 mm matches ORB-SLAM3
- Basalt str02: 2.0978 ± 0.0008 m (3 runs, 150 fps, 100% tracking) - completes full sequence vs ORB-SLAM3 44-52% coverage
- AirSLAM str03: 3.6314 ± 0.2047 m (3 runs, 22 fps avg, 100% tracking) - highest global ATE on str03; 0 loop closures; local turn ATE 50 mm reasonable; run1 slow (TRT compile), run2+3 fast at 29 fps
- AirSLAM str02: **complete** (3 runs, 20.22 ± 0.82 m, 100% tracking)

---

## Dataset 3 - [NON-AGRICULTURAL REFERENCE] EuRoC-MAV

> **[NON-AGRICULTURAL REFERENCE]** All 5 algorithms run on MH_01_easy,
> MH_03_medium, and MH_05_difficult (N=1 per sequence, no repetition stats).
> Used as a sanity check against published EuRoC literature values.

**Camera:** 752x480, 20 fps, baseline 0.110 m, indoor MAV flight.

| Sequence | Algorithm | ATE Sim3 [m] | ATE SE3 [m] | RPE [m/m] | Scale | FPS | Frames |
|---|---|---|---|---|---|---|---|
| MH_01_easy | ORB-SLAM3 | **0.034** | **0.035** | 0.016 | 1.002 | 18.2 | 3682 |
| MH_01_easy | Basalt | 0.057 | 0.087 | 0.009 | 1.016 | 176.8 | 3682 |
| MH_01_easy | AirSLAM | 0.111 | 0.116 | 0.020 | 1.007 | 15.3 | 3682 |
| MH_01_easy | MAC-VO | 0.198 | 0.199 | 0.030 | 1.005 | 1.3 | 3682 |
| MH_01_easy | DROID-SLAM | 4.083 | 7.891 | 0.500 | 0.173 | 13.2 | 3682 |
| MH_03_medium | ORB-SLAM3 | **0.044** | **0.052** | 0.018 | 0.992 | 17.9 | 2700 |
| MH_03_medium | Basalt | 0.137 | 0.140 | 0.016 | 1.008 | 113.5 | 2700 |
| MH_03_medium | AirSLAM | 0.143 | 0.144 | 0.019 | 0.995 | 31.7 | 2700 |
| MH_03_medium | MAC-VO | 0.340 | 0.341 | 0.019 | 0.996 | 1.15 | 2700 |
| MH_03_medium | DROID-SLAM | 3.523 | 7.105 | 2.274 | 0.082 | 10.9 | 2700 |
| MH_05_difficult | ORB-SLAM3 | **0.072** | **0.078** | 0.228 | 0.996 | 18.0 | 2273 |
| MH_05_difficult | Basalt | 0.182 | 0.193 | 0.087 | 1.010 | 108.7 | 2273 |
| MH_05_difficult | AirSLAM | 0.297 | 0.307 | 0.026 | 1.012 | 34.9 | 2273 |
| MH_05_difficult | MAC-VO | 0.470 | 0.484 | 0.028 | 1.017 | 0.86 | 2273 |
| MH_05_difficult | DROID-SLAM | 6.594 | 8.514 | 0.786 | 0.248 | 13.8 | 2273 |

> ORB-SLAM3 ATE 0.034-0.072 m matches published EuRoC results.
> DROID-SLAM shows large scale error (scale 0.08-0.25) on all 3 sequences - mono-style drift on stereo input.
> Basalt highest throughput (109-177 fps). AirSLAM outputs keyframe-only poses on MH_01_easy (268 of 3682).

### ORB-SLAM3 - MH_01_easy complete

| Metric | Value |
|---|---|
| ATE RMSE Sim3 | **0.0340 m** |
| ATE RMSE SE3 | **0.0352 m** |
| RPE (point_distance, 1 m) | 0.0156 m/m |
| Scale factor | 1.002 |
| Frames tracked | 100% (3682 / 3682) |
| Loop closures | 0 |
| Wall time | 202.6 s |
| FPS | 18.17 |

### Basalt - MH_01_easy complete

| Metric | Value |
|---|---|
| ATE RMSE Sim3 | **0.0567 m** |
| ATE RMSE SE3 | **0.0873 m** |
| RPE (point_distance, 1 m) | 0.0085 m/m |
| Scale factor | 1.016 |
| Frames tracked | 100% (3682 / 3682) |
| Wall time | 20.8 s |
| FPS | 176.8 |

### AirSLAM - MH_01_easy complete

| Metric | Value |
|---|---|
| ATE RMSE Sim3 | **0.1107 m** |
| ATE RMSE SE3 | **0.1156 m** |
| RPE (point_distance, 1 m) | 0.0195 m/m |
| Scale factor | 1.007 |
| Frames tracked | 268 keyframe poses from 3682 input frames |
| Wall time | 240.2 s |
| FPS | 15.3 (input frames) |

### MAC-VO - MH_01_easy complete

| Metric | Value |
|---|---|
| ATE RMSE Sim3 | **0.1981 m** |
| ATE RMSE SE3 | **0.1993 m** |
| RPE (point_distance, 1 m) | 0.0295 m/m |
| Scale factor | 1.005 |
| Frames tracked | 100% (3682 / 3682) |
| Wall time | 2861.2 s |
| FPS | 1.287 |

> Segment maps generated at run-level, algo-level, and sequence-level under `results/euroc_mav/MH_01_easy/`.

### DROID-SLAM - MH_01_easy, MH_03_medium, MH_05_difficult complete

| Sequence | ATE Sim3 | ATE SE3 | RPE [m/m] | Scale | FPS | Frames |
|---|---|---|---|---|---|---|
| MH_01_easy | 4.083 m | 7.891 m | 0.500 | 0.173 | 13.17 | 3682 |
| MH_03_medium | 3.523 m | 7.105 m | 2.274 | 0.082 | 10.94 | 2700 |
| MH_05_difficult | 6.594 m | 8.514 m | 0.786 | 0.248 | 13.85 | 2273 |

> Large scale error (scale 0.08-0.25) indicates DROID-SLAM produces monocular-style scale drift
> even with stereo input on this dataset. SE3 ATE (7-9 m) is 15-20x worse than ORB-SLAM3.
> Segment maps under `results/euroc_mav/MH_0*/droidslam/`.

---

## Findings

### 1. Loop closure is the dominant factor for global accuracy on long agricultural sequences

Rosario v2 provides the clearest evidence. ORB-SLAM3 on seq1 (13 821 frames, ~940 m) achieves 1.18 m
global ATE with 5-6 loop closures. On seq5 (11 640 frames, similar geometry) it achieves only 20.2 m
because no loops are detected. The local per-row ATE is identical in both cases (~0.016 m). This is not
an algorithm deficiency - it is a fundamental challenge of perceptually aliased environments where all
crop rows look identical. Without distinctive visual landmarks, bag-of-words place recognition cannot
trigger loop closure, and global drift accumulates uncorrected.

Quantified: 5-6 loop closures reduce global ATE from ~20 m to ~1.2 m on a ~940 m path - a 17x improvement.
All algorithms without loop closure (MAC-VO, Basalt, AirSLAM) cluster in the 9-20 m range on Rosario.

### 2. Local accuracy is excellent and consistent across all algorithms

Despite large global ATE differences, per-row segment ATE is remarkably similar:
- ORB-SLAM3 seq1: 16 mm / seq5: 16 mm
- MAC-VO seq1: 20 mm / seq5: 45 mm
- Basalt seq1: 14 mm / seq5: 21 mm
- AirSLAM seq1: 19 mm / seq5: 47 mm

This 1000x ratio between local (16 mm) and global (16 m) accuracy confirms that all algorithms track
individual rows accurately - the problem is purely global map consistency. For agricultural applications
that need only within-row precision (e.g., spray path following), all algorithms are adequate.
For field-level consistency (cross-row registration, field mapping), loop closure is essential.

### 3. Scale drift follows sequence geometry, not just length

Basalt shows a striking geometry-dependent pattern: 20.9% scale drift on Rosario seq1 vs 6.6% on seq5.
Both sequences are similar length (~940 m, ~11-14 k frames). The difference is route geometry - seq1
covers a more varied path with directional changes, while seq5 is dominated by long parallel rows.
This suggests that scale drift in visual-only SLAM accumulates faster on monotone straight-line motion,
where the stereo baseline provides weaker triangulation constraints. IMU data (available but unused)
would break this correlation by providing absolute scale observable independent of trajectory shape.

### 4. Sim(3) alignment systematically underestimates scale drift

Sim(3) ATE removes scale drift from the metric, giving an optimistic view:
- ORB-SLAM3 str03: 0.104 m (Sim3) vs 0.78 m (SE3) - 7.5x gap
- Basalt seq1: 14.3 m (Sim3) vs 18.7 m (SE3) - 1.3x gap
- DROID-SLAM MH_01: 4.1 m (Sim3) vs 7.9 m (SE3) - 1.9x gap

SE3 ATE is the honest metric for stereo systems where scale is observable. The large Sim3/SE3
gap is itself diagnostic: when SE3 >> Sim3, scale drift is the dominant error source,
not localization noise. For system-level reporting in the thesis, SE3 is the primary metric.

### 5. DROID-SLAM fails on agricultural data due to domain mismatch

DROID-SLAM is trained on TartanAir (photorealistic simulation), FlyingThings3D, and Sintel -
none of which resemble polytunnel or open-field agricultural imagery. The failure is severe:
- HortiMulti str02: ATE 38.92 m, scale 9.59 (10x over-scale)
- HortiMulti str03: ATE 18.76 m, scale 0.428 (2.3x under-scale)
- Rosario seq5: ATE 50.02 m
- EuRoC MH_01: ATE 4.1 m Sim3 / 7.9 m SE3, scale 0.173

The scale collapse (scale << 0.5 or >> 2.0) indicates the depth network predicts wildly incorrect
disparity on these out-of-distribution images. Interestingly, DROID-SLAM runs at 10-16 fps across all
sequences - it processes frames at the same speed regardless of how wrong the predictions are.
Fine-tuning on even a small set of agricultural frames is a likely path to improvement (see phase2_plan.md).

### 6. Speed-accuracy Pareto frontier

Across agricultural sequences, the approximate ordering by speed vs accuracy tradeoff:

| Algorithm | FPS (typical) | Global ATE (Rosario) | Notes |
|---|---|---|---|
| Basalt | 60-150 | 14-15 m | Fastest; no loop closure |
| AirSLAM | 22-27 | 10-13 m | Fast + SuperPoint features |
| ORB-SLAM3 | 9-18 | 1-20 m | Loop closure when available |
| DROID-SLAM | 10-16 | 38-50 m | Fast but inaccurate on agri data |
| MAC-VO | 1-2 | 13-19 m | Slowest; uncertainty-aware |

Basalt and AirSLAM dominate on pure speed. ORB-SLAM3 dominates when loop closure fires.
MAC-VO provides covariance estimates useful for downstream uncertainty quantification -
its speed makes it unsuitable for real-time deployment but excellent for offline analysis.

### 7. RPE rotation artefact (frame convention mismatch)

All algorithms on HortiMulti report RPE rotation ~17-20 deg/m - an artefact of the
body-to-camera frame rotation in the HortiMulti calibration. Ground truth is in body
frame (IMU/robot), while estimated trajectories are in camera frame. The 17.6 deg/m
constant offset across all algorithms confirms this is a systematic calibration issue,
not a measurement of real rotational error. RPE translation (m/m) is unaffected and
remains the valid metric for reporting.

### 8. Repeatability across 3 runs

Algorithms with no randomness in their pipeline (Basalt, MAC-VO) produce near-identical
results across all 3 runs (ATE std < 1 mm). Algorithms with non-deterministic elements
(ORB-SLAM3 loop closure timing, AirSLAM TRT engine) show larger run-to-run variation:
- ORB-SLAM3 seq5: 4.2 m std across 3 runs (loop closure timing)
- AirSLAM seq5: 0.99 m std (run3 notably worse: 14.1 m vs 12.1 m)
- AirSLAM str02: 0.82 m std

The 3-run average is reliable for all algorithms. Single-run benchmarking would give
misleading results for ORB-SLAM3 and AirSLAM on difficult sequences.

### 9. OKVIS2 IMU noise sensitivity differs from ORB-SLAM3 and Basalt

OKVIS2's MAP estimator requires correctly scaled IMU noise parameters. Using raw Allan-variance
measurements (which are 12-840x smaller than needed) causes scale collapse (scale ~0, ATE 50 m+).
With corrected D435i reference values:
- Scale collapse is eliminated (scale ~0.92 vs ~0 before)
- Frontend errors drop to 0 (vs 206 RANSAC failures + 3375 reprojection errors with bad params)
- But VIO still underperforms vs ORB-SLAM3 VIO (20.3 m vs 2.3 m on seq5)

The remaining gap is because ORB-SLAM3 uses preintegration which is inherently more robust to
IMU miscalibration, while OKVIS2 tightly couples raw IMU measurements. The D435i reference values
are generic defaults, not a calibration for the specific Rosario v2 RealSense unit. Proper
sensor-specific calibration (e.g., via Kalibr with the actual sensor) would be needed for OKVIS2 to
approach ORB-SLAM3's VIO performance. For this benchmark, OKVIS2 VO is the usable configuration.

---

## Key commands

```bash
# Run an algorithm on a sequence (multi-run; <run_id> default 1)
bash scripts/run/run_orbslam3.sh   <dataset> <seq> <run_id>
bash scripts/run/run_droidslam.sh  <dataset> <seq> <run_id>
bash scripts/run/run_macvo.sh      <dataset> <seq> <run_id>

# Per-run evaluation (writes run_eval.json)
conda run -n macvo python3 scripts/eval/_evaluate_run.py <dataset> <seq> <algo> <run_id>

# Aggregate N runs (writes metrics.csv + report.md with Sim3 + SE3 ATE)
conda run -n macvo python3 scripts/eval/_aggregate_runs.py <dataset> <seq> <algo> <fps>

# Segmentation (writes segment_map.png at 8K; per-run, per-algo, cross-algo)
conda run -n macvo python3 scripts/eval/_plot_segments.py <dataset> <seq>

# Re-segment GT (v2 algorithm: 2 m sliding window, 10° / 20 cm thresholds)
conda run -n macvo python3 scripts/eval/_segment_trajectory.py \
    datasets/<ds>/<seq>/gt_tum.txt datasets/<ds>/<seq>/segments_auto.csv

# Ad-hoc ATE (Sim3 + SE3)
conda run -n macvo evo_ape tum gt_interp_tum.txt traj.txt -a --correct_scale  # Sim3
conda run -n macvo evo_ape tum gt_interp_tum.txt traj.txt -a                  # SE3

# MAC-VO post-run conversion (if script exits early due to X11/Rerun crash)
SBX=$(ls -dt src/MAC-VO/Results/*/*/ | head -1)
conda run -n macvo python3 scripts/eval/_macvo_to_tum.py "$SBX" \
    results/<dataset>/<seq>/macvo/trajectory.txt
```

---

*Last updated: 2026-05-31 - GNSS-VIO N=1 sweep complete. Restructured into VO/VIO/VIO-LC/GNSS-VIO mode sections.*
