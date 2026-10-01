# AirSLAM rectified camera/IMU audit

Reviewed 2026-10-01 from preserved configurations and local source. This finding
concerns EuRoC VIO and VIO-LC. During the subsequent authorized
[focused EuRoC campaign](euroc-focused-campaign-20261001.md), the patch was applied
and built in a separate workspace. Native camera composition and short VIO and
VIO-LC execution/export gates passed. **All 18 corrected attempts are complete: 17 final exports and one retained MH05 VIO-LC refinement SIGSEGV without final output.**
See [the completed campaign](euroc-focused-campaign-20261001.md); sparse-keyframe limitations remain. The original build remains intact.
No existing trajectory or recorded configuration was changed.

## Established issue

The 18 saved EuRoC VIO/VIO-LC repetitions record clean AirSLAM source revision
`1b70ff63ea5f7c5654a4ec986abc59c838793208`, `use_imu: 1`, raw EuRoC camera-to-body
transforms and `distortion_type: 1`. Saved config hashes were verified for every
repetition. This source's `Camera` constructor sets `_Tbc = Tbc0` before stereo
rectification, then rectifies the images and updates the projection intrinsics
without updating `_Tbc`/`_Tcb`.

`Frame::SetPose` computes the IMU pose as `T_world_camera * T_camera_body`;
`SetIMUPose` and the g2o IMU constraints use the same camera/body conversion.
Visual rays and poses are therefore expressed in rectified axes while the fusion
extrinsic describes the raw axes. OpenCV's left rectification rotates those axes
by **0.6197749343 degrees** for the saved EuRoC calibration. A global alignment or
post-hoc output transform cannot repair the optimization performed with that mismatch.

This issue is present in the recorded source; it is not evidence of local
accuracy tuning. Historical metadata lacks executable hashes, so it does not prove
which exact binary was loaded. Nor does this establish the cause of every poor
AirSLAM trajectory or initialization failure. Preserve the upstream/configured
cohort and its observed outcomes. A corrected implementation is a disclosed new
cohort, not a silent revision of the original algorithm's results.

## Prepared correction

`R0` from OpenCV maps raw left-camera coordinates into rectified coordinates.
The required composition is:

```
T_body_rectified = T_body_raw * T_raw_rectified
R_body_rectified = R_body_raw * transpose(R0)
```

The camera center in body coordinates stays unchanged. The patch
[`airslam-rectified-imu-extrinsic.patch`](../scripts/patches/airslam-rectified-imu-extrinsic.patch)
updates the rotation and recomputes the inverse after either radtan or fisheye
rectification. Already rectified (`distortion_type: 0`) inputs retain their existing
transform. The patch applies cleanly to the recorded source under `git apply --check`.
Numerical composition checks using every saved EuRoC VIO/VIO-LC config recover an
arbitrary body pose within 1.12e-16; using the uncorrected extrinsic produces the
0.6198-degree body orientation inconsistency. Validation evidence is saved in
`results/repair-20261001/airslam-rectification-validation.json`.

Configuration comments now correctly describe `T_bc`/EuRoC `T_BS` as mapping camera
coordinates into body coordinates. Numeric calibration values are unchanged.

## Disposition and prerequisites

All **18 saved repetitions in six cells** require a new cohort to support claims
about correctly calibrated AirSLAM inertial fusion. Original scores remain available
as affected-cohort observations. These repetitions are explicit required-rerun
actions in the future manifest, with no execution readiness granted.

The focused continuation uses isolated source/build evidence, records executable
and shared-library hashes, and verifies rectified/body composition through the
compiled library. Direct native supervision retains stage failures and waits for
map serialization before cleanup. Sparse keyframe accuracy remains a separately
labelled limited claim; it is not dense tracking accuracy or real-time evidence.
The earlier no-estimator restriction was explicitly superseded for the focused
EuRoC campaign; other benchmark paths remain outside this authorization.

VO/VO-LC use no IMU residuals and do not acquire this fusion blocker. Agricultural
camera configs currently set `distortion_type: 0`; the above source path does not
by itself imply their calibration is valid or invalid. Their separate calibration
and reference-frame reviews still apply.
