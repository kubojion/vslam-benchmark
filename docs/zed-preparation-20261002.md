# ZED calibration and reference preparation — 2026-10-02

Calibration, the versioned reference and saved-trajectory sensitivity checks are
complete. Fifteen applicable native paths passed bounded execution checks; Voxel
initialization/export remains unverified. See the [validation record](zed-validation-20261002.md)
and [exact campaign plan](zed-campaign-20261002.md) for reporting checks, preservation,
remaining attempts and runtime estimates. No full repetitions are authorized.

## Preserved evidence

Checkpoint `f59854e` preserves the supplied mounting document. Current evaluations,
metadata, references and the complete earlier inspection folder are backed up
under `/data/imoroz/vslam-repair-backups/20261002T092232Z-zed-before-preparation`.
Unchanged root CSVs are in the preceding complete backup,
`/data/imoroz/vslam-repair-backups/20261002T081230Z-protocol-reporting-complete`.
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

### Completed sensitivity results

The initial 46 saved ZED exports were evaluated against 18 frozen scenarios; none selected
the primary calibration/reference. Results and pair counts are retained in
`results/zed-preparation-20261002/sensitivity.json`. Across numerically valid
outputs, fixed-only scoring changed SE(3) ATE by at most 0.1703 m. Clock query
shifts of ±0.1 s changed it by at most 0.00233 m; ±0.5 s by at most 0.0124 m.
The primary offset remains zero. DPVO's publishable headline remains Sim(3) shape
accuracy; its SE(3) sensitivity is only a diagnostic.

Height changes of ±0.5 m disappear under rigid alignment, to numerical precision;
that does not validate the nominal height. Constant roll/pitch scenarios changed
SE(3) ATE by at most 0.118 m. Their instantaneous lever displacement reached
0.527 m for 10-degree pitch, showing why small aligned-ATE changes do not certify
the mounting geometry. The baseline-derived-pitch diagnostic changed ATE by at
most 0.0044 m. Arbitrary terrain roll/pitch is not bounded by these scenarios.

## Saved-result claim decisions

The approved mask and independently documented mounting model support **qualified
nominal 3D position** claims on retained reference support. Identity reference
quaternions do not support rotation or full relative-pose claims. Verified saved
VO/VO-LC profiles can therefore be retained with these limits and existing
execution/configuration evidence. Sparse AirSLAM keyframes remain sparse; DPVO
remains monocular Sim(3); the MAC-VO performant profile remains disclosed.
OKVIS2 VO repetition 2 remains a scale-collapse observation in the denominator.
OV2SLAM's six saved ZED exports retain their native shutdown-error observations;
the wrapper's zero exit is not evidence of clean native completion.

AirSLAM VO-LC's historical N=1 and N=2 workspace cohorts support individually
qualified observations, but cannot be pooled into one verified N=3 cohort.
OKVIS2 VO-LC's interrupted attempt still has no saved trajectory. OKVIS2-X VO-LC
exit 141 left 354 causal poses spanning 35.30249 s. These are now recovered by an
exact, hash-pinned CSV-to-TUM conversion, using the saved initial extrinsic because
online extrinsic optimization was disabled. They are **not final bundle-adjusted
poses**. The recovered prefix has 352 supported pairs and SE(3) ATE 0.04350 m;
its short duration and unexplained execution prevent a qualified completed-trial
claim. Its separate 18-scenario sensitivity record supplements the original 46;
clock changes are at most 0.00064 m (±0.1 s) and 0.00393 m (±0.5 s). The original
CSV, metadata, exit 141 and missing final BA remain unchanged. A passing short
check cannot retrospectively establish either historical outcome as complete.

All 11 historical inertial run-1 attempts omitted the recovered factory rotation.
Their calibration snapshots and source identities are pinned in
`docs/campaigns/zed-calibration-findings-20261002.json`. Re-evaluation can correct
exported frames but cannot repair the preceding fusion. Retain those results and
native failures as the old configuration cohort; require corrected-cohort estimation.
The six historical ORB VO/VO-LC repetitions retain the separate 15-versus-10 Hz
configuration finding. No existing native failure is silently replaced.

## Native defects isolated during this preparation

The existing ORB library was built without `-march=native` (16-byte Eigen
alignment), but its bundled Release g2o was built with it (32-byte alignment).
The same public `VertexSE3Expmap` is 272 versus 288 bytes; a pose edge is 304
versus 320 bytes. A graph-allocation/destruction fixture segfaults against the old
library and passes against the compatible build. The short ZED trace places the
initial failure in g2o pose optimization. This establishes a current build
incompatibility; it does not establish the cause of every historical ORB crash
whose loaded g2o bytes were not recorded.

The compatible library processed the full 600-image diagnostic and saved its
trajectory, exposing a second fault. GDB then showed `Viewer::Run` inside
OpenCV/TBB while the main thread was running exit/library-unload handlers.
`System::Shutdown` had worker waits commented out. The isolated repair requests
viewer shutdown, joins local mapping and loop closing, waits for any recorded
in-progress global BA, then joins the viewer before export/exit. No image, feature,
solver or initialization settings changed. The original library remains intact.
The build/retained object identities and source patch are in
[camera-run native build evidence](campaigns/orb-zed-g2o-build-20261002.json).

Voxel's native abort backtrace reaches `message_filters::Signal1::removeCallback`
while destroying its stereo synchronizer. Members were destroyed in reverse order,
so subscriber signals disappeared first. The isolated destructor patch clears
synchronizers before subscribers. The original source checkout and executable are
unchanged; the ZED runner selects a separate build prefix. See
[Voxel build evidence](campaigns/voxel-zed-shutdown-build-20261002.json).
The wrapper now saves native/player exits, log and failed metadata even when no
trajectory exists, and cannot report success merely because a pose file exists.

The fixed first-60-second Voxel window logs insufficient initialization excitation
and no trajectory. That is separate from the shutdown defect; no initialization
threshold or test window was tuned. Its first repaired check ended with native
exit zero, but metadata publication was correctly rejected because unrelated
benchmark source files changed during the check. That diagnostic is preserved and
is not a clean wrapper validation. The final short-check batch freezes code at
`2efd79f` and records fresh diagnostic identities. Full production repetitions
remain prohibited.

## Execution boundary

Short isolated checks are authorized only after static validation. Use separate
diagnostic sequence/output identities, fixed input windows and bounded process
lifetimes. Do not replace production attempts or turn an expected early stop into
a successful full run. No repeated search for favorable settings is authorized.
The final fixed-window checks passed for ORB VO, VO-LC, VIO and VIO-LC; OKVIS2
and OKVIS2-X VO-LC; and AirSLAM VO-LC. The initial checks had already passed for
Basalt, OKVIS2, OKVIS2-X, AirSLAM and OpenVINS VIO, plus OKVIS2, OKVIS2-X and
AirSLAM VIO-LC. That is **15 distinct successful paths**. Voxel's final check
recorded native/player exit zero and wrapper exit one for no initialization/export:
shutdown and failure capture are repaired, successful export remains unverified.
All diagnostic attempts, including failed/debugger/intermediate checks, remain
separate from production counts. No test window or initialization threshold was
changed to seek success. Diagnostic evaluation now explicitly binds its exact
600-image timestamp prefix to the parent recording's physical calibration and
versioned reference; it is never treated as a new production sequence.

The existing nine ZED protocol-verified N=3 cells retain 27 observations. Four
additional qualified historical observations remain individually usable, including
the separate AirSLAM VO-LC cohorts. To finish coherent N=3 across all 25 ZED cells,
the other 16 cells need **48 new attempts**: 17 setup replacements, 25 missing
slots and six cohort-completion attempts. The six comprise two OKVIS2 VO-LC, one
OKVIS2-X VO-LC and three AirSLAM VO-LC slots needed for fresh, consistent cohorts;
they are not six additional proven configuration defects. Historical interruptions,
partial exports and previously qualified observations remain in the evidence.

`results/zed-preparation-20261002/campaign/manifest.json` is an executable prepared
selection with unique new physical IDs, immediate evaluation and guarded resumption.
It is an alternative to the overlapping ZED portion of the all-mode manifest,
**not an additional campaign to execute on top of that plan**. Fifteen new N=3
cells (45 attempts) have bounded execution evidence; Voxel's three attempts retain
an explicit readiness blocker. First authorized full repetitions must be evaluated
as production gates; short checks do not certify full-sequence stability or timing.
Existing algorithm exclusions remain. The non-ZED ORB runners still select their
original library path and require separate ABI/shutdown validation; this ZED repair
must not be generalized to those untested paths.
