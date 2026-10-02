# ZED calibration and reference preparation — 2026-10-02

Work in progress. The calibration and versioned position reference are prepared;
saved-result reconciliation and short native checks are still pending. This does
not yet certify the remaining campaign ready. No full repetitions are authorized.

## Preserved evidence

Checkpoint `f59854e` preserves the supplied mounting document. Current evaluations,
metadata, references, CSVs and the complete earlier inspection folder are backed up
under `/data/imoroz/vslam-repair-backups/20261002T092232Z-zed-before-preparation`.
Original bags under `/data/imoroz/vslam-source-records/zed2i-20260703` remain read-only.
Historical provenance hashes and prior attempts are unchanged.

The recovered [SDK export](campaigns/zed-sdk-calibration-20261002.json) identifies
S/N 30291010, SDK 5.4.0, camera firmware 1523 and sensor firmware 777. The original
capture script and terminal transcript remain in
`results/zed-reference-inspection-20261002/`. The factory transform is assumed
unchanged between the July recording and October recovery for this same device;
it is not a new calibration fitted to benchmark trajectories.

## Camera–IMU conversion

Use `T_A_B` to mean coordinates in B mapped into A. Stereolabs documents
`camera_imu_transform` as **IMU to left camera**. In the supplied IMAGE convention,
axes are right/down/forward. The ROS wrapper publishes raw sensor components in
`zed_imu_link` using forward/left/up axes, and publishes the SDK transform with the
left camera as parent and IMU as child. Its optical TF is the fixed axis conversion.
Sources: [SDK API](https://www.stereolabs.com/docs/api/structsl_1_1SensorsConfiguration.html)
and [pinned wrapper implementation](https://github.com/stereolabs/zed-ros2-wrapper/blob/cce25d32f88362b50f3aec08876519487be724c3/zed_components/src/zed_camera/src/zed_camera_component_main.cpp).

Let `Q = [[0,0,1],[-1,0,0],[0,-1,0]]`. Then
`T_imu_left = diag(Q,1) * inverse(T_left_imu_SDK_IMAGE)`.
The right transform is `T_imu_left * Tx(recorded_baseline)`.
The SDK's float32 rotation is projected onto SO(3) only to remove rounding error;
the original numbers are retained. The recovered residual is about 0.675 degrees.
See [derived calibration](campaigns/zed-physical-calibration-20261002.json).

`scripts/data/prepare_zed_calibration.py --apply` updates the eight applicable
configuration files for ORB-SLAM3, Basalt, OKVIS2, OKVIS2-X, AirSLAM, OpenVINS and
Voxel-SVIO. Without `--apply`, it verifies them. Tests check inversion, coordinate
conversion and relative stereo geometry. Parser-level comparison checks that only
extrinsics changed; image calibration, IMU noise, timing and algorithm settings
remain as before. OKVIS2 VIO-LC materializes from the VIO file. Basalt shares its
calibration with VO; its virtual output frame must use each saved run's own config.

July CameraInfo remains authoritative: 1920×1080 rectified images,
`fx=fy=1118.6947021484375`, `cx=964.8566284179688`, `cy=559.3102416992188`,
baseline `0.11984625036568344 m`. The new SDK raw-stereo matrix and later HD720
intrinsics are not substituted. The prepared images are JPEG color images that
algorithms convert to grayscale, not infrared images. Future ORB configs use the
recorded 10 Hz input rate. Historical 15 Hz ORB VO/VO-LC attempts retain their
existing setup-rerun finding.

## Frozen GNSS reference construction

The [approved screening audit](campaigns/zed-approved-screening-20261002.json)
defines exactly **15 intervals / 448 rejected raw samples**. Its input hashes and
all excluded indices/timestamps were reproduced. All 23,160 raw GPS headers and
geodetic positions, 23,160 PVT status messages and 23,156 relative-baseline messages
match the original robot bag. Derived floating diagnostics differ only at rounding
level across NumPy environments. Carrier status uses the nearest PVT header; these
pair one-to-one, 0.087–27.3 ms before the corresponding GPS header.

`scripts/data/build_zed_reference.py` creates an immutable version under
`datasets/zed2i/field1_110426_full_10fps_q90/references/gnss-position-v2-20261002/`
and refuses overwrite. The original `gt_tum.txt` remains unchanged. The selector
under `configs/references/` pins the version, trajectory and explicit support mask.
At 5 Hz, an isolated excluded epoch could leave a 0.4-second gap; the older generic
0.5-second interpolation limit alone would fill it. Explicit retained intervals now
also constrain interpolation, distance windows and path segmentation.

The new reference uses full ENU position, a fixed physical rear-axle convention,
the documented camera/internal offsets, and the approved nominal **1 m vertical
separation from antenna to left camera**. No additional internal vertical offset
is added to that 1 m. The horizontal lever is `[2.855648945, 0.059990261] m`.
Heading comes from valid fixed dual-antenna RELPOSNED, linearly interpolated within
0.5-second support at GPS header times. Remove `atan2(0.037,1.385)` once to obtain
physical body heading. The camera mount uses 20.17 degrees down and +0.130281398
degrees yaw relative to physical forward. **Primary body roll and pitch are zero**;
mount pitch and terrain/body tilt are distinct quantities.

The primary mask retains RTK float outside approved spikes, yielding **22,659
reference samples: 21,696 fixed and 963 float**. The fixed-only variant removes the
963 float samples and preserves the resulting holes. Both use exactly the same
geometry. Filtering uses raw GNSS only; no SLAM residual controls the mask.
Identity quaternions remain explicit placeholders. Rotational/full-relative-pose
accuracy is unavailable. This is a qualified nominal **3D position reference**,
not a surveyed 6-DoF ground-truth certificate.

## Sensitivity protocol fixed before scoring

Evaluate all saved ZED exports using the benchmark evaluator with the following
predeclared controls, retaining every outcome and reporting pair counts:

- Primary and fixed-only masks, plus the old reference under the same estimator
  frame conversion to isolate reference effects.
- Antenna-above-camera separation 0.5, 1.0 and 1.5 m. With a level platform, changing
  height adds a global vertical translation and SE(3) alignment removes it. This
  test cannot establish the true height.
- Constant body roll or pitch of ±5 and ±10 degrees, one axis at a time, at 1 m
  separation. These are sensitivity scenarios, not confidence intervals or fitted
  corrections. Report the positional lever-arm displacement as well as ATE changes.
- A separate baseline-derived pitch scenario with zero assumed roll, as a diagnostic
  of the level-platform approximation; never select it by the resulting SLAM score.
- Reference query offsets −0.5, −0.1, 0, +0.1 and +0.5 seconds, shifting support
  intervals with the reference. Convention: query reference at `image_time + dt`.
  No clock offset is fitted or adopted. The hangar +0.10-second estimate does not
  apply to this field recording.

Scoring on fixed-only support may change the observed portion of a partial
trajectory; compare pair counts and report changes as sensitivity, not proof that
float epochs are unbiased. Constant attitude perturbations do not bound arbitrary
terrain motion. These mounting and timing limitations remain disclosed.

## Execution boundary

Short isolated checks are authorized only after static validation. Use separate
diagnostic sequence/output identities, fixed input windows and bounded process
lifetimes. Do not replace production attempts or turn an expected early stop into
a successful full run. No repeated search for favorable settings is authorized.
Short-check outcomes, exact remaining attempts, estimates and publication decisions
will be recorded here after validation. Existing algorithm exclusions remain.
