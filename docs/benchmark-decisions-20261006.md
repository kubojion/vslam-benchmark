# Benchmark decisions, 6 October 2026

Decided by the user (project lead), recorded by Claude. Analysis and implementation checklist:
`/data/imoroz/IMU-NOISE-ISSUE/fixes.md` (with `findings-2026-10-06.txt` and
`readiness-and-rosario-2026-10-06.txt`, outside the repository). Machine-readable consequences:
`docs/campaigns/user-rerun-decisions-20261006.json` (superseded attempts) and the readiness blockers
`apply_rosario_kalibr_bundle_and_imu_noise_rule_before_new_attempts` /
`apply_imu_noise_rule_to_citrusfarm_before_new_attempts`.

## 1. IMU noise: rule C on every dataset with a published calibration

The rule of `docs/imu-noise-rule-20261005.md` is unchanged: each estimator receives the dataset's
published Allan-variance values, each quantity multiplied by the factor its authors applied to the
EuRoC calibration in their released EuRoC configuration. It now applies wherever a published
calibration of the recorded IMU exists:

| Dataset | Calibration | Status |
|---|---|---|
| EuRoC | Kalibr calibration published with the dataset | already the authors' released values |
| HortiMulti | published Allan analysis (MicroStrain 3DM-GX5-25) | applied (rule-C batch, 2026-10-05/06) |
| Rosario v2 | authors' Kalibr `imu.yaml` (RealSense D435i) | to apply; every inertial estimator |
| CitrusFarm | authors' MicroStrain GX5 file (`configs/sensors/sources/citrusfarm/microstrain_gx5.yaml`) | to apply; every inertial estimator, ORB-SLAM3 included |
| ZED2i | none (manufacturer figures only) | keeps the recording envelope; reported as a separate case |

This supersedes the "Two regimes" section of `docs/imu-noise-rule-20261005.md`, which stays unchanged
because reviews pin it. That section kept CitrusFarm on the envelope partly because estimators
diverged with its published values, which made the policy depend on observed outcomes. The policy now
depends only on whether a calibration exists. ZED2i must stay out of any statement that every dataset
used calibration-based settings.

Disclosed exploratory evidence seen before this decision: the CitrusFarm seq04 noise-only pilot
(published densities: OpenVINS, Voxel-SVIO and AirSLAM collapsed in scale; ORB-SLAM3 1.23 m against
0.68 m with the envelope) and the HortiMulti envelope-against-rule checks. Failures under the rule are
results and are kept. Existing envelope results stay as a separately labelled adaptation/sensitivity
condition; they never fill a rule-C repetition.

Consequence: every CitrusFarm VIO/VIO-LC attempt made with the envelope is superseded, including the
six ORB-SLAM3 VIO attempts of the rule-C batch. CitrusFarm VO/VO-LC attempts are unaffected.

## 2. Rosario v2: the complete published Kalibr camera–IMU bundle ("Option A")

The current Rosario profile is the authors' released ORB-SLAM3 recipe: virtual rectified intrinsics
(fx = fy = 648.8624, cx = 645.0113, cy = 348.2427, zero distortion) applied to the unremapped
`image_rect_raw` pixels, `Camera.bf` 32.270 (a 49.73 mm baseline) and a zero camera–IMU time offset.
That file contradicts itself: its own `RIGHT.P` and the laboratory Kalibr bundle give a 50.24 mm
baseline (1.02 % larger), and the rectified intrinsics belong to remapped pixels. The authors' reply
points to the laboratory archives.

Decision: use the complete laboratory Kalibr stereo–IMU bundle (`kalibr_ir_stereo_imu.tar.gz`) as one
deterministic rectified input for every algorithm and mode:

- residual Kalibr rectification applied once, at the original 1280×720 resolution (alpha = −1), into
  a new, separately recorded input version; the original images are kept;
- intrinsics fx = fy = 648.8624169653789, cx = 645.0113372802734, cy = 348.24266815185547, zero
  distortion, baseline 0.050240890825 m (bf 32.5994258512);
- camera–IMU transforms rotated into the rectified camera axes;
- IMU timestamps moved once to the camera clock by the published offset (t_imu = t_cam + 4.098308 ms,
  i.e. 4,098,308 ns subtracted in a new copy); native offsets 0, matching HortiMulti and CitrusFarm;
- rule C noise (section 1);
- AirSLAM `depth_upper_thr` stays 50 m: its detectors resize 1280-pixel images to 512, so point
  disparities fall on a 2.5 px grid and the cap does not change point initialisation
  (fixes.md section 4).

The implementation checklist is fixes.md section 2 (R2–R12). Every Rosario VO, VIO, VO-LC and VIO-LC
attempt is superseded: 210 attempts over both sequences at N=3. Historical results stay preserved and
labelled with their old profile.

## 3. HortiMulti reference

The HortiMulti reference as currently evaluated is accepted for the claim review without waiting for
the authors: the reference trajectory and frame handling, with the reference origin of the 2026-10-05
decision, and the reference clock as recorded. Both remain evaluation-side choices and can be revisited
without new estimation. Recorded claim limit:
`hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006`.

## 4. Failures and the TODO marker

A crash or divergence under a verified setup is an algorithm outcome: it stays in the N=3 denominator,
and the TODO marks such a completed cell `✅ N=3 ❗`. Setup defects stay blocked instead. HortiMulti
classifications (`docs/campaigns/production-review-20261006-hortimulti.json`):

- SVO Pro VIO-LC, 5 of 6 attempts: abort on the kindr quaternion-normalisation check inside SVO Pro's
  own depth-filter thread (squared norm 0.99983 < 0.9999). It happens only with loop closure on (SVO
  Pro VIO 6/6 complete), and the saved input rotations are orthonormal. Re-examined when EuRoC SVO Pro
  VIO-LC runs.
- ORB-SLAM3 VIO-LC strawberry02, 1 of 3: segmentation fault after the second visual-inertial BA.
- MASt3R-Fusion strawberry03 VIO and VIO-LC, 3 of 3 each: scale collapse under rule C.

MASt3R-Fusion VIO-LC exports global-optimisation keyframes (about one pose per second across the whole
sequence), so its accuracy is claimed as sparse-keyframe accuracy, like AirSLAM's.

## 5. Order of the remaining Rosario and CitrusFarm work

1. Configuration work without estimation (fixes.md R2–R11, C1–C6), then an independent review.
2. Short native load checks; the gate is correct loading and delivery, not scores.
3. N=1 for every Rosario and CitrusFarm cell (VO, VIO, VO-LC, VIO-LC) as repetition 1 of the final
   setup; then repetitions 2 and 3 with the identical setup. After N=1 only setup defects may be fixed,
   and a fix reruns that cell's repetition 1 as well. EuRoC's 54 loop-closure attempts may run alongside.
