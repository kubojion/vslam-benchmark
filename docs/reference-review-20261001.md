# Agricultural reference and calibration review — 2026-10-01

This extends acceptance checkpoint `e0ee49b`. The matched-session audit is complete
within its no-estimation scope; unresolved physical/reference questions remain
explicit. **This is not verified readiness to run.** Existing accepted EuRoC
claims, exclusions and original attempts remain intact. No estimator, tuning,
history rewrite or push was performed. The old temporary pause is revoked.

## Disposition

No additional clean N=3 cell qualifies. The existing 45 EuRoC cells, 147 accepted
repetitions and 54 limited repetitions remain accepted. Nine configured-attempt
failures remain reusable as failure observations; two previously retained OpenVINS
Rosario collapses now also have confirmed invalid inertial calibration. Their
failure observations remain in the denominator, but their configurations require
correction rather than supporting an intrinsic algorithm-failure claim.

There are **91 distinct required reruns**, including the previous 30 and 61 newly
established cases. The generated [handoff](acceptance-handoff-20261001.md), explicit
[ledger](campaigns/paper-acceptance-20261001.json) and future manifest identify every
physical attempt and prerequisite. Missing repetitions are separate.

| Confirmed defect | Existing attempts | Newly added reruns |
|---|---:|---:|
| Previous ORB ZED camera FPS, Air EuRoC rectification, ORB Horti VIO-LC rectification | 30 | 0 |
| Rosario identity IMU/camera extrinsics: Basalt 6, Voxel-SVIO 6, OpenVINS 2 | 14 | 14 |
| Horti uncompensated camera/IMU offset: ORB, Air, OKVIS2, OKVIS2-X; two sequences × two inertial modes × three repetitions | 48 | 42 (six ORB already require rectification reruns) |
| Native GNSS logs: four OKVIS2-X default attempts loaded zero lever; CIFASIS Rosario seq1 loaded the old Rosario-v1 lever | 5 | 5 |

Every new finding is tied to verified historical snapshot/source identities or a
hash-verified native log. Today's config is never substituted as evidence of what
an old run loaded. No rerun is inferred solely from a high error or missing audit.

## Matched author material

[Source identities](campaigns/reference-sources-20261001.json) pin original author
archives, exact Git revisions, reference CSVs and bounded original ROS bag reads.
Files and diagnostic scripts are retained in `results/reference-review-20261001/`.
No benchmark dataset was replaced with a newer release. Bag sampling checks are
explicitly bounded; they do not claim a full-bag integrity or synchronization audit.

Rosario seq1/seq5 match December 22/26, 2023. All 8,983 and 7,577 saved reference
rows match the authors' MINS plaintext reference: identical timestamps and at most
5e-10 pose-component formatting differences. The [dataset documentation](https://cifasis.github.io/rosariov2/)
identifies a RealSense IMU reference from stereo/IMU/three-antenna PPK fusion.
It shares estimator inputs; it is not independent sensor ground truth, particularly
for GNSS comparisons. PPK and conventional variants remain separate experiments.

Horti is specifically **February 2026, Strawberry 2 and 3**, not a later harvest
or another camera rig. The [session calibration](https://s3.eidf.ac.uk/eidf258-hortimulti-a-multi-sensor-dataset-for-polytunnels/Feb2026/Strawberry/calibration.yaml)
matches the extractor's 2048×1536 camera constants and stereo geometry. The generic
README's 1936×1216 description does not match these recorded camera-info messages.
The calibration was retrieved from the current author distribution, then matched
to the old local extraction and original recorded camera info; its retrieval date
alone is not treated as historical applicability. Its repeated `imu0` YAML key and
nonstandard `%` comments require careful parsing: a normal mapping loader can lose
the first extrinsic block. The original bytes are preserved.

All 5,173 Strawberry 2 reference rows are numerically identical after quaternion
column reordering. All 2,039 Strawberry 3 rows agree within 0.48 microseconds,
5e-8 m and 5e-10 quaternion-component rounding. Thus the newer CSV presentation
does not justify substituting a different reference. Original local CSVs stay intact.

The first two left/right Strawberry 2 images reproduce pixel for pixel with the
existing native fisheye rectification followed by INTER_AREA resize to 640×480.
The resulting rectified intrinsics and approximately 0.139502 m baseline match
current profiles. Right headers differ from the paired left headers by 12.024 ms
and 0.903 ms in these samples and were renamed to left timestamps. The authors
describe hardware triggering and midpoint-of-exposure timestamps, so header
inequality alone is not proof of unsynchronized exposures. Later-pair timing and
the reference time convention remain specific prerequisites, not presumed fixed.

## Rosario: evaluation correction and remaining profile inconsistency

The original Kalibr archive calibrates the actual `image_rect_raw` topics. Bounded
reads from both original bags reproduce the corresponding saved images exactly;
no additional Kalibr rectification or resize occurred. The calibrated left-camera
optical axes therefore remain the output target. The author ORB launcher also uses
`do_rectify=false`.

The evaluator now converts the reference's **physical IMU pose** to the left camera
using the independently sourced inverse of `T_cam_imu`. Inertial algorithm exports
use this physical transform even if the estimator assumed an incorrect extrinsic.
Visual-only virtual-body exports retain their saved-config/final-map transform.
These are distinct frame conventions. [The exact transform](campaigns/rosario-reference-calibration-20261001.json)
records direction, source hash, session match and the shared-reference limitation.
This repairs evaluation, not erroneous estimation. Saved trajectories are unchanged.

All 593 saved trajectories were staged through the checked evaluator; **159 Rosario
evaluations have changed frame-dependent metrics**, with no change in observed
numerical outcome status. The other 434 retain their numerical fields exactly;
provenance/qualification is refreshed. Previously unsupported Rosario rotational
metrics become available where both physical frames are established, but remain
subject to the calibration/reference claim blockers. Previous derived JSONs are
archived before promotion.

A remaining shared inconsistency prevents agricultural accuracy acceptance:

| Projection evidence | Focal length / baseline |
|---|---|
| Original bag CameraInfo, both matched sessions | fx=fy=647.0064697265625; cx=648.2323608398438; cy=350.12701416015625; zero D; right P[0,3]=-32.48686599731445 |
| Saved benchmark/author ORB-derived profile | fx=fy=648.8624169653789; cx=645.0113372802734; cy=348.24266815185547; baseline 0.0497336941 m |
| Author profile's RIGHT.P | -32.599425851220396, implying approximately 0.05024 m at that focal length |
| Original Kalibr stereo | approximately 0.05024089 m plus a small nonidentity stereo rotation; distinct calibrated intrinsics/distortion |

The benchmark uses virtual projection values while the saved pixels are unchanged
recorded rectified images. The author example itself mixes baseline conventions;
its OpenVINS example also differs from its Kalibr/ORB camera–IMU calibration.
Literal example replication is not proof of one consistent physical camera model.
**Do not automatically declare every Rosario attempt invalid or approved.** Resolve
and document the intended image/projection/rectification profile, then determine
which saved profiles remain supportable and which need corrected estimation.
Changing the profile now would create a new cohort. No ATE-based choice was made.

Fourteen inertial attempts already have an unambiguous separate defect: identity
camera–IMU transforms despite raw unrotated IMU samples and independently calibrated
nonidentity geometry. OpenVINS spatial calibration was explicitly disabled; time
calibration cannot repair that. Basalt/Voxel identity profiles likewise cannot be
justified by calling the IMU a virtual camera body. Their joint camera-profile
replacement is still a production prerequisite. False colocation comments are
corrected; those future profiles are explicitly blocked pending a consistent model.

## Horti: timing defect and reference-origin uncertainty

The February calibration defines `t_imu = t_camera + 0.009160379134269684 s`.
Raw sample checks and extractor source establish that this offset was not already
applied to stored IMU/image inputs. In 48 saved ORB/Air/OKVIS2/OKVIS2-X inertial
attempts the offset was uncompensated; saved source/config evidence is pinned in
[the timing findings](campaigns/horti-time-offset-findings-20261001.json). A comment
claiming online timing refinement does not make a fixed zero delay correct.

Ten future Horti OKVIS2/OKVIS2-X VIO, VIO-LC and GNSS config files now use
`image_delay=-0.009160379134269684`, since the native loader subtracts that value.
They have not been loaded by a running estimator. ORB/Air still need a reviewed
input-time adapter and output-time handling; Air's separate rectification patch
also still needs application/build/native checks.

Basalt's available source has its `cam_time_offset_ns` addition commented out;
linking that source to the installed historical binary is unresolved. Its nonzero
JSON field alone cannot certify compensation. Voxel exports IMU-clock poses, while
its wrapper subtracts the configured shift to label them on the camera clock.
OpenVINS publishes IMU-time odometry. Exact **reference timestamp semantics must be
settled before changing evaluation timestamps**, including VO camera-clock outputs
and the camera-grid coverage denominator. No blanket 9.16 ms score-driven shift
was applied, and this conversion question remains blocked rather than claimed fixed.

Strawberry 2's original reference says `TagMap/base_link`; Strawberry 3 says
`odom/odom_mapping`. The available Poly-TagSLAM code labels outputs `base_link` but
consumes incoming odometry directly. The author's [Semantic-LIOSAM parameters](https://github.com/shuoyuanxu/Semantic-LIOSAM/blob/9cc51f618da6f1341fd1e4db15b9015c91dfc6a8/config/params.yaml)
match February Ouster/IMU geometry, and its odometry publisher uses the LiDAR state
with child `odom_mapping`. This supports an Ouster-origin hypothesis for str03,
but no exact generation manifest links that revision to these exported references.
A separate public URDF aliases base/IMU/Ouster origins; substituting it for the
physical session calibration would be unjustified. The supplied tag-map check also
does not close either candidate chain: one matched observation gives about
0.49–0.69 m residuals under base-link and 1.05–1.23 m under Ouster hypotheses.
No transform was fitted and neither hypothesis was selected by the smaller error.

Needed: the actual generation configuration/TF tree, map gauge and timestamp
convention for each saved reference. The user confirms no such session configuration
is held on the server/workstation/SSD and that the released bags omit TF; the
public Poly-TagSLAM configuration is generic. Str03 origin requires author clarification. This is **specific missing linkage**, not a
claim that author calibration is unavailable. Strawberry 2's maximum GT gap is
3.298 s and only 92.58% of its input grid has supported reference interpolation;
Strawberry 3 has about 99.75%. Preserve that support mask and conditional accuracy.
Surveyed tag-landmark error is not per-pose trajectory-reference accuracy.

## GNSS lever correction

[The composed transforms](campaigns/gnss-lever-calibration-20261001.json) are
expressed in the IMU frame, in metres:

- Rosario reach1: `[-0.3859020972, -0.0843042662, -0.2863138543]`, composing the
  v2 sensor-box/screw/left-camera/IMU chain. It independently matches the author
  v2 rounded `[-0.386, -0.084, -0.286]`. Our old `[0.22183, 0.01088, -0.17570]`
  came from Rosario v1. The day-dependent third antenna is not the selected reach1.
- Horti: `[0.3731801128, -0.1555276923, -0.4936645975]`, composing
  `T_imu_os @ inverse(T_base_mount @ T_mount_os) @ T_base_gps`.
  Directly using base-link's `[0.62, -0.11, 0.42]` as an IMU-frame lever is wrong
  by approximately 0.948 m.

Four CIFASIS and four OKVIS2-X future config files, plus OpenVINS+GPS and RTAB-Map
wrapper TFs, now contain these composed translations. The wrappers' `base_link`
alias denotes the IMU body, not the platform frame named base_link in calibration.
Native loading/global-frame behavior remains unverified. No old config is rewritten.

Exactly five saved native logs establish incorrect loaded levers, independently
of missing snapshots: four OKVIS2-X default r1 logs print zero, and CIFASIS Rosario
seq1 r1 prints the v1 offset. [Hash-pinned findings](campaigns/gnss-lever-findings-20261001.json)
retain that proof. Other GNSS attempts still need their actual input/covariance,
antenna selection and fusion-output evidence; current defaults cannot prove their
historical settings. VINS-Fusion's current global position factor has no lever-arm
term and needs a reviewed integration change, not an invented YAML parameter.
The OpenVINS localization wrapper also needs its ENU-heading initialization checked.

## ZED: original records verified, remaining uncertainty narrowed

The user supplied matching original records at the read-only external directory
`/data/imoroz/vslam-source-records/zed2i-20260703/`. All supplied SHA256 checks pass.
[Paths and checksums](campaigns/zed-source-records-20261001.json) identify the
robot sqlite3 bag, camera-laptop GPS/TF extract and geometry record; none was moved
into the repository or edited. The 142 GB merged camera bag remains on the user's
SSD; copying it is unnecessary for this GPS/TF verification.

Independent parsing confirms 23,160 robot `/gps/fix` and 23,156 rover fixes, with
recording start 2026-07-03 09:04:17 UTC. All 23,106 saved `gps_regen_2p86.csv` rows
match the robot messages. All 23,105 camera-laptop fixes have identical original
header stamps and serialized payloads in the robot bag. The first saved fix is
1783069468.3356447 s, latitude 52.291369976, longitude 16.392196270, altitude 120.9482 m.
The old `gps.csv` has those same shared rows plus one final fix; this is not a second
recording. Reproducing the historical nearest-rover heading and 2.86 m horizontal
shift matches every saved GT position within 5e-10 m. Original GT has unchanged
antenna altitude and identity quaternions; reproducing it does not establish 3D truth.
The old manifest's 1.86 m entry remains historical, not an instruction to undo the
already-corrected longitudinal lever.

The robot TF evidence contains 13 successive antenna-transform states (12 changes
after the initial state), alternating CAR/4WS origins. The physical rear-axle
layout, 3.180−0.320=2.860 m, avoids those aliases. The detached ZED subtree confirms
camera-link→center `[0,0,0.015]` and center→left `[-0.010,0.060,0]` m. A missing
base→camera TF must not be filled with whichever wheel-mode origin appears first.

The 0.037 m front-antenna left offset rotates the antenna line by **1.53028°**
relative to the vehicle. Correcting that heading alone would introduce roughly
7.6 cm of lever displacement; the left-camera lateral offset largely cancels it.
Composing both supplied offsets gives **16.38 mm** horizontal difference from the
old GT using the documented calibrated mount (20.17° pitch, −1.40° yaw, zero roll),
or **16.48 mm** using the nominal 24.5° pitch/zero yaw. This is a geometric result,
not fitted to any SLAM score. The original 3.7 cm antenna measurement has not been
rechecked for July; antenna heights and robot/camera roll are not measured.
Consequently this does not yet justify an unqualified new 3D camera reference.

Receiver evidence narrows the quality claim: over the saved-reference span, 23,101
relative-position messages report fixed carrier solution, valid baseline and valid
heading, but rear absolute-position PVT reports **22,082 fixed and 1,023 float**
epochs (23,105 total). Thus “all GT samples are RTK-fixed” would be false. Native
receiver accuracy fields are estimates, not independently measured error bounds.
The original bag lacks embedded custom UBX definitions; decoding used the pinned
upstream message schema with successful complete deserialization and consistent
field values. Exact counts/intervals and schema identities are retained in the
verification artifact. Fix-quality eligibility must be declared before publication;
no inconvenient interval was silently discarded.

Camera-minus-robot bag receive-time differences range 5.8–540.8 ms, median 170.0 ms;
robot receive-minus-header median is 1.84 ms. These include transport and recorder
scheduling, so **170 ms is not a measured clock correction**. The user's subsequent
`CLOCK-OFFSET-NOTE.md` clarifies that **+0.10 s belongs to the earlier 07:51 UTC
hangar recording, not this 09:04 UTC field recording**. That project's convention
is `t_robot=t_camera_header+offset`; the field offset was explicitly unknown. The
external README was updated by its owner to include this clarification; the five
original checksum-listed data files are unchanged. Historical document hashes are
retained in the source index.

**Clock alignment is closed as a disclosed limitation at the user's direction.**
The benchmark retains zero applied offset. The camera receipt-minus-robot-header
minimum supplies a one-sided bound (camera at most approximately 8 ms ahead), not
a two-sided estimate. No time offset was fitted from the trajectories. The complete
benchmark `evaluate_arrays` reproduces the five requested examples using temporary
reference timestamps only; the saved reference and canonical results are unchanged.

| Saved example | −0.5 s | −0.1 s | 0 s | +0.1 s | +0.5 s |
|---|---:|---:|---:|---:|---:|
| ORB VO r3 | 0.2721 | 0.2636 | 0.2622 | 0.2610 | 0.2593 |
| OKVIS2 VIO-LC r1 | 0.3327 | 0.3325 | 0.3331 | 0.3338 | 0.3389 |
| OV2SLAM VO r1 | 0.4256 | 0.4181 | 0.4167 | 0.4154 | 0.4121 |
| Basalt VIO r1 | 0.4359 | 0.4309 | 0.4300 | 0.4294 | 0.4285 |
| OKVIS2-X VIO r1 | 0.4652 | 0.4684 | 0.4696 | 0.4709 | 0.4778 |

Values are diagnostic SE(3) ATE in metres using the benchmark's current frame
conversion; small differences from the source note's independent computation are
not hidden. Across all 46 retained exports, the same evaluator association/frame/
alignment functions reproduce each zero-offset published ATE exactly. Excluding
the already catastrophic OpenVINS collapse, changes at sampled ±0.1 s are at most
2.08 mm and across the five sampled hypotheses at most 11.45 mm. The collapsed
OpenVINS export has approximately 26.7 million m SE(3) ATE; changed endpoint support
makes its sensitivity large and meaningless as a clock certificate. It is retained,
not silently omitted from the artifact. These tests neither bound the true offset
nor certify every value between the sampled hypotheses.

The full five-example reproduction, all-export sensitivity, evaluator identity
and exact scope are in `results/reference-review-20261001/zed-clock-*.json`.
The remaining ZED blockers concern GNSS-quality support and physical 3D/serial
calibration—not clock alignment or an unspecified missing robot bag. A horizontal-
only claim may avoid unmeasured antenna height, but still needs explicit target
geometry and quality support. Per-serial camera-to-IMU rotation is absent from
recordings and requires camera S/N 30291010 on the SDK. Current ZED accuracy remains
provisional for those reasons, with clock uncertainty disclosed rather than gated.

## Before production

Resolve the Rosario image/projection and Horti reference-origin/clock cases above,
and ZED physical-reference/quality policy; fix
remaining native timing/fusion support; apply/build the reviewed Air patch; verify
corrected effective configs, loaded native binaries and dependencies; capture native
exits and diagnose recorded ORB/OKVIS/OV2/Voxel execution failures. Then separately
authorize bounded integration checks and a full first repetition evaluated before
continuation. The executable manifest reserves new physical attempt IDs, preserves
old cohorts, and has zero verified-ready estimator actions. More repetitions do
not close a calibration or reference-definition gap.
