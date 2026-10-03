# Rosario VIO candidate preparation — 2026-10-02

**Candidate selection is integrated and bounded native checks have run.
Recording-specific production profile selection remains unresolved.** The
preparation phase launched no estimator; the subsequent explicitly authorized
[readiness work](execution-readiness-20261002.md) exercised all four candidates
on fixed initial windows. Historical attempts and scores remain preserved.
Candidates stay opt-in and do not replace the default Rosario profiles.

The final destination is `/data/imoroz/vslam-benchmark` on `main`.
[Integration and validation](rosario-main-integration-20261002.md) reuse the work
from the separate checkout. Native evidence and remaining gates are tracked
separately from the unresolved image/rectification choice.

The [validation record](rosario-vio-candidate-validation-20261002.json) identifies
source hashes, exact historical attempts, existing planned replacement paths,
sampled data checks and current runner selections. It is a preparation report,
**not a launch manifest or an acceptance-ledger amendment**.

## Candidate files and policy

All paths below are relative to
`/data/imoroz/vslam-benchmark/configs/candidates/rosario-vio-20261002/`.
The bundle's `index.json` hashes every candidate and sets
`verified_ready_to_run: false` and `activated_in_runners: false`.
These retained preparation flags mean not activated by default and not approved
for production. Explicit diagnostic selection is now available in the runners.

| Directory | Sensor calibration | Estimator policy | Status |
|---|---|---|---|
| `basalt-kalibr/` | Complete published Kalibr stereo/IMU bundle, full inverted transforms, residual radtan | Requested historical `vio_config.json`; four unsupported native keys disclosed | Native calibration and normalized clock verified; final settings-materialization regression pending |
| `voxel-kalibr/` | Same Kalibr bundle, both camera transforms and shifts, published IMU noise | Preserved historical non-calibration settings; spatial/intrinsic/time calibration disabled | Native loaded values, repaired initializer offset and clean bounded exports verified |
| `openvins-kalibr/` | Same Kalibr bundle; `T_cam_imu` retained for OpenVINS' inversion-capable parser | Preserved historical estimator settings; spatial/intrinsic disabled, time enabled | Both bounded checks exited cleanly; propagated IMU-clock export must stay distinct from camera-clock output |
| `openvins-author/` | Author OpenVINS sensor bundle, including its different extrinsics and time offsets | Author estimator YAML, including spatial/intrinsic/time calibration enabled | Both bounded checks exited cleanly; online extrinsics require per-pose calibration for camera-origin scoring; no author-score reproduction claim |

Basalt supplies `calibration.json` and `vio_config.json`; Voxel supplies
`rosariov2.yaml`; each OpenVINS directory supplies `estimator_config.yaml`,
`kalibr_imucam_chain.yaml` and `kalibr_imu_chain.yaml`.

The 15 verbatim small files in `sources/` include published author profiles and
the actual run1 provenance snapshots, not inferred historical settings from
today's configs. `sources/index.json` records original paths and SHA-256 hashes.
Author files come from preserved [Rosario v2 commit
82115db](https://github.com/CIFASIS/rosariov2/tree/82115db620b57a5decb48ffe70b4639f00ce3ec9/data/evaluation)
and the authors' `kalibr_ir_stereo_imu.tar.gz`, already downloaded for the
[reference audit](reference-review-20261001.md).
Historical commit identifiers remain historical after the attribution rewrite.

No parameter was selected from ATE or another benchmark score. The three Kalibr
candidates use one complete published sensor bundle with each algorithm's saved
benchmark policy. That policy is disclosed and is not presented as an author
benchmark reproduction. The OpenVINS-author alternative stays a separate profile;
choose and document the experimental policy before any future comparison. Do not
run both and retain whichever produces the better score.

## Confirmed defect versus unresolved camera review

The saved Basalt and Voxel configurations place the left camera at the IMU origin
with identity rotation. Saved OpenVINS does the same and disables spatial
calibration. The extracted IMU samples are unchanged RealSense optical-frame
measurements, not samples rotated or translated into a fictitious camera-coincident
IMU. Published full camera–IMU calibration contradicts that identity model. This
is the confirmed estimator-input defect behind **14 required replacements**.
Changing evaluation cannot retroactively repair it.

Separately, the original bag-prefix audit establishes that saved pixels match
the recorded `image_rect_raw` messages. No additional Kalibr/ORB rectification
was applied during extraction. That topic name alone does not settle which
published projection fits those pixels. The published Kalibr profile itself uses
those topics and estimates small nonzero residual radial/tangential distortion.
The author ORB launcher sets `do_rectify=false`, although its YAML contains
rectification matrices and virtual projections. The three geometries differ:

| Evidence/profile | Focal length x / y (pixels) | Stereo baseline (metres) |
|---|---|---|
| Recorded CameraInfo | 647.0064697 / 647.0064697 | about 0.050211 from right P and TF |
| Author Kalibr | left 645.4064993 / 648.5756187; right 645.9158470 / 649.1492152 | 0.0502408908250, full relative rotation/translation |
| Author ORB virtual camera | 648.8624170 / 648.8624170 | `Camera.bf / fx` = 0.0497336941; **RIGHT.P instead implies 0.0502408908250** |

The candidates use the complete Kalibr or complete author OpenVINS camera model
directly on unchanged pixels, with no extra rectification, cropping or resizing.
This is an internally consistent published-profile hypothesis. Which profile
applies to sequences 1 and 5 remains an author question; preparation does not
resolve that question. The mismatch alone does not establish that every nearby
historical result requires a rerun.

## Transform, noise and time conventions

`T_A_B` maps coordinates in frame B into frame A. Published `T_cam_imu` maps IMU
to camera; Basalt and Voxel need its rigid inverse:
`R_imu_cam = R_cam_imuᵀ`, `t_imu_cam = −R_cam_imuᵀ t_cam_imu`.
Basalt stores Hamilton quaternion **x, y, z, w** plus translation; Voxel stores a
row-major 4×4 array. OpenVINS accepts the published `T_cam_imu` key and inverts it
when the loader requests `T_imu_cam`. No additional optical/body axis flip is
applied. Translations are metres and angles are radians.

For Kalibr cam0, the resulting camera centre in IMU coordinates is
`[-0.004483027810, 0.019179699213, 0.027584143037]` m, with nonidentity rotation.
Both independently inverted camera transforms reproduce the published stereo
transform and 0.0502408908250 m baseline. If rectification is introduced later,
it must change both the pixels and camera frame:
`T_I_Crect = T_I_C × diag(R_rectᵀ, 1)`. Synthetic stereo/point tests cover this
relation; the current candidates do not apply rectification.

Basalt's `pinhole-radtan8` represents the four published distortion coefficients
exactly when k3–k6 are zero. Its `rpmax: -1` requests the model's native valid-domain
calculation. This follows the pinned [Basalt serializer](https://github.com/VladyslavUsenko/basalt-headers/blob/b7f915b195c87c8373bf93f97a0710bcdaffd718/include/basalt/serialization/headers_serialization.h)
and [camera implementation](https://github.com/VladyslavUsenko/basalt-headers/blob/b7f915b195c87c8373bf93f97a0710bcdaffd718/include/basalt/camera/pinhole_radtan8_camera.hpp).
Installed native parsing and domain behavior still require validation.

All Kalibr candidates now use published continuous noise densities/random walks,
without multiplying by sample rate:

| Quantity | Saved benchmark | Published candidate |
|---|---|---|
| Accelerometer noise density | 0.016 | 0.0009943860019903928 |
| Accelerometer random walk | 0.001 | 0.00004750972547867261 |
| Gyroscope noise density | 0.000282 | 0.00023249699924838475 |
| Gyroscope random walk | 0.0001 | 0.0000018236185367375672 |

The sensor is RealSense, not the ZED stated in old copied comments. The published
IMU rate is 200 Hz. OpenVINS requires Tw, Ta, R_IMUtoGYRO, R_IMUtoACC and Tg fields
even when intrinsic calibration is disabled. The Kalibr adapter explicitly
represents its calibrated/ideal IMU with identity matrices and zero Tg; these
are format/model declarations, not newly recovered measurements. The author
OpenVINS bundle already contains those same declarations.

Five saved Voxel scalar values (`init_dyn_min_rec_cond`, `init_lamda`, `max_lamda`,
`min_dx`, `min_dcost`) use scientific notation such as `1e-12` that plain PyYAML
loads as strings. The candidate explicitly emits numeric scalars with the same
intended values (`1.0e-12`, etc.), matching the C++ double parameters. This is a
representation repair, not score tuning. Historical ROS-loader behavior and any
fallback to defaults remain unverified; it does not create additional rerun
counts beyond the already-invalid Voxel cohort. OpenCV numeric values in the
author estimator profile are checked against the original before/after conversion.

Published timing uses **t_imu = t_camera + offset**:

| Bundle | Left offset (seconds) | Right offset (seconds) |
|---|---|---|
| Kalibr | 0.004098308327610102 | 0.004110891358806293 |
| Author OpenVINS | 0.006482764254944565 | 0.006491480658385266 |

These algorithms use a common stereo timestamp/offset from the left camera.
The right-minus-left residual is disclosed: 12.583 μs for Kalibr and 8.716 μs
for author OpenVINS. It is not silently averaged. Basalt encodes left shift as
4,098,308 ns, with less than 0.5 ns rounding. Voxel stores both published shifts,
but its source consumes the left one; online time calibration remains disabled.

**Native timing review:** the inspected [upstream Basalt VIO source](https://github.com/VladyslavUsenko/basalt/blob/0f3b2b52c807f70ff4e2973ce253c73329eea7bc/src/vi_estimator/sqrt_keypoint_vio.cpp#L183)
has camera-offset application commented out. This does not prove what the
installed binary does. The runner now explicitly subtracts the declared shift
from an attempt-local IMU CSV and supplies native offset zero; its original
inputs stay intact and exports retain camera time. Native factory inspection
confirms the effective offset and all sensor values. Voxel's original initializer
silently retained offset zero; the repaired native path now loads the configured
left-camera offset into both initialization and propagation. Voxel adds its offset
to native pose timestamps; the runner subtracts the configured fixed offset.
OpenVINS `/odomimu` is propagated/exported on IMU-message timestamps, while stereo
updates use camera timestamps. Verify each exported trajectory's time basis
against the reference before scoring. Do not fit an offset using trajectory error.

The existing Rosario evaluation frame adapter uses Kalibr's IMU-to-left-camera
transform and a `/mins/imu/pose` reference. Confirm how each newly selected native
output represents that physical IMU/camera frame. In particular, the alternate
OpenVINS calibration must not silently replace the reference-generation calibration.
Any justified evaluation-adapter change needs a versioned, evidence-backed update;
the existing adapter and historical evaluations remain unchanged in this task.

## OpenVINS author comparison

| Estimator setting | Saved / Kalibr-policy candidate | Author-reproduction candidate |
|---|---|---|
| Spatial calibration | false | true |
| Intrinsic camera calibration | false | true |
| Camera–IMU time calibration | true | true — unchanged |
| IMU intrinsic / g-sensitivity calibration | false / false | false / false |
| Dynamic initialization | true | false |
| Initialization IMU threshold | 1.0 | 1.5 |
| Gravity magnitude | 9.7958 | 9.81 |
| Features per camera (`num_pts`) | 200 | 1200 |

Other estimator YAML values match; relative filenames are remapped to the
benchmark layout. Author camera/IMU topics become `/cam0/image_raw`,
`/cam1/image_raw`, `/imu0`. Intrinsics/distortion and stereo geometry match Kalibr,
but the author's full camera–IMU transforms and shifts differ, so they remain
together in the author bundle. The author ROS1 launcher also overrides timing
recording; this ROS2 benchmark does not reproduce that launch environment or
establish the author's implementation revision. A YAML reproduction is a
configuration comparison, not a claim to reproduce the paper's numerical results.

## Historical attempts and future slots

Paths are `results/vio/rosariov2/<sequence>/<algorithm>/run<id>`.
All exact paths, outcomes, source hashes and planned IDs are in the validation
record. **No saved file or acceptance decision has changed.**

| Algorithm | Sequence 1 | Sequence 5 | Confirmed replacements | Recorded outcomes |
|---|---|---|---:|---|
| Basalt | run1, run2, run3 | run1, run2, run3 | 6 | A6/E6/S6/F0; clean exports do not validate the identity configuration |
| Voxel-SVIO | run1, run2, run3 | run1, run2, run3 | 6 | A6/E6/S0/F6; saved trajectories and reported failures retained, even with recorded exit 0 |
| OpenVINS | run1 | run1 | 2 | A2/E2/S0/F2; exit 134 and scale-collapse observations retained |

The existing blocked plan names run10001–run10003 for each Basalt/Voxel cell and
run10001 for each OpenVINS replacement. OpenVINS logical repetitions 2 and 3
in each sequence are **four missing attempts**, not observed failures or setup
reruns. One selected corrected profile per algorithm therefore needs **18 future
attempts: 14 replacements + four missing**. Existing planned IDs are reservations
in an old plan, not permission to run it; recheck collisions and regenerate the
manifest after profiles/native paths are resolved. The old runtime entries for
these replacements are unknown, so no defensible new runtime estimate is asserted.

The observed failures are preserved without claiming that the identity defect
caused each crash or export problem. Its presence independently invalidates the
experimental setup. By contrast, **24 nearby VIO attempts** (ORB-SLAM3, AirSLAM,
OKVIS2 and OKVIS2-X; two sequences × three repetitions) and **six Basalt VO
attempts** remain camera-review cases, not newly confirmed estimator reruns.

> **Correction (3 October 2026):** the six AirSLAM attempts among these use an identity camera–IMU transform and are required reruns like Basalt/OpenVINS/Voxel-SVIO. The candidate bundles use the Kalibr camera model and time shift; the 3 October decision keeps the authors' ORB-SLAM3 camera model and zero offset for all Rosario rows, so the replacements need profiles built from that decision. See [the rerun plan](rerun-plan-20261003.md).
Their eventual reuse depends on resolving the projection review. Other original
reference/claim limitations, including the fused reference's non-independence,
remain in force.

## Static validation and remaining native gates

The focused suite passes **31 tests**: source integrity and deterministic generation;
OpenCV/PyYAML parsing and linked files; required IMU fields; transform inversion,
quaternion order and lever arms; stereo closure; radtan4/radtan8 projection equality;
rectification-frame geometry; unchanged author policy; timing units/sign; invalid
profile rejection; ROS numeric scalar types; and default runner selection. With
TODO, acceptance-ledger, protocol-status and repair-plan checks, **70 tests pass**.
These tests do not instantiate
Basalt, ROS, Voxel or OpenVINS.
The subsequent main integration passed **89 focused tests**, adding completed-slot
preservation, configuration-recipe and source-capture checks. Both full read-only
campaign preflights also passed; none of these checks establishes Rosario native
readiness. See [the final integration receipt](rosario-main-integration-20261002.md).

Read-only data validation confirms 13,821 synchronized stereo pairs / 187,362 IMU
samples for sequence 1 and 11,640 / 158,462 for sequence 5. Both camera CSVs have
identical strictly increasing timestamps. Eight sampled images are 1280×720
mono8 and pixel-identical to the preserved original-message hashes; four sampled
RealSense IMU messages preserve their numeric values and axes (timestamp
float-roundtrip differences: −82, −55, +39 and −13 ns). This is a sampled identity
check, not a complete re-decode of the original bags.

Sequence 5's first camera image precedes the first IMU sample by 9.08331 ms;
sequence 1 has 50.258957 ms of initial IMU lead. IMU continues past the final
image in both sequences. Native initialization/bracketing must handle the sequence
5 boundary explicitly and log any skipped frame; no dataset was silently trimmed.

Runner selection now accepts `ROSARIO_VIO_PROFILE=basalt-kalibr`,
`voxel-kalibr`, `openvins-kalibr` or `openvins-author`, matched to the correct
algorithm. It checks the indexed file hashes and snapshots every loaded profile
file before execution. Basalt's `BASALT_CALIBRATION` is independent from
`BASALT_CONFIG`; combining either override with an indexed candidate is rejected.
Voxel candidates use the reviewed destructor/parameter-loading repair; OpenVINS
candidates use the shutdown-corrected image. Defaults are unchanged. Native
diagnostics do not approve any of these profiles for the recorded pixels.

Reproduce preparation and static checks from `/data/imoroz/vslam-benchmark`:

```bash
/data/imoroz/conda/envs/macvo/bin/python scripts/campaign/prepare_rosario_vio_candidates.py
/data/imoroz/conda/envs/macvo/bin/python -m pytest -q scripts/campaign/tests/test_rosario_vio_candidates.py
/data/imoroz/conda/envs/macvo/bin/python scripts/campaign/validate_rosario_vio_candidates.py --evidence-root /data/imoroz/vslam-benchmark --output results/rosario-main-integration-20261002/candidate-validation-current.json
```

## Questions for the dataset authors

1. Which complete calibration applies to sequence1 and sequence5, and were their
   recorded IR pixels rectified by the camera/driver? Which projection and residual
   distortion should be used directly with the released images?
2. Why does ORB's `Camera.bf` imply 0.0497336941 m while `RIGHT.P` and Kalibr imply
   0.0502408908250 m, and CameraInfo/TF imply about 0.050211 m? Was the published
   `do_rectify=false` launcher the one used for the reported experiments?
3. Are the differing Kalibr versus OpenVINS full IMU transforms/time shifts from
   distinct sessions, calibration refinements, or different frame definitions?
   Which bundle and OpenVINS calibration/initialization switches were actually used?
4. What are the time bases of the released camera, IMU and fused reference outputs?
   Confirm the sign/application of the published shifts and any clock correction
   used to generate the reference. Also identify the implementation/launch revisions
   needed for a defensible author-result reproduction.

## Exact steps before later reruns

1. Integration prerequisite satisfied: the ZED controller was stopped, the three
   started attempts and evidence capture finished, and their results were preserved
   before these files were integrated. The three unstarted actions remain unstarted.
2. Resolve the recording/projection questions from authoritative evidence, select
   one internally consistent profile and predeclare each cohort's algorithm policy.
   Keep the alternate OpenVINS profile separate if a later ablation is authorized.
3. Explicit selection and loaded-file snapshots are implemented. Finish the
   final Basalt effective-settings regression and bind the eventually selected
   profile into its production manifest; defaults must not change implicitly.
4. Retain the completed native calibration/timing/shutdown evidence and its
   limits. Basalt's exact upstream build linkage remains distinct from verified
   loaded values. OpenVINS' propagated IMU clock and online author-profile
   extrinsics need explicit scoring conventions, including per-pose calibration
   if camera-origin accuracy is claimed. Keep sequence 5's first-frame IMU gap
   disclosed; no input was silently trimmed.
5. The focused continuation already authorizes bounded diagnostics; preserve
   their completed records and failed outcomes. Any final regression stays
   separate from production. Native success cannot choose the camera profile.
6. Regenerate fresh source/input/runtime captures and an execution manifest naming
   the 14 replacements and four missing slots, with non-colliding physical run IDs,
   previous-attempt links and measured runtime estimates where available. Keep all
   previous attempts; evaluate each completed repetition immediately. Launch only
   after its separate authorization. Correctly configured observed failures count
   toward verified N=3 and must not be repeated until success.

The TODO matrices retain A/E/S/F (and U when present), red confirmed reruns and
yellow unresolved review. ✅ N=3 means three verified attempts under consistent
settings, including valid observed failures; it does not require three successes.
Candidate preparation does not change those historical counts or qualification.
