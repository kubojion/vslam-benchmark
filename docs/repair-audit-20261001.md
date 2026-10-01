# All-configuration repair audit — 2026-10-01

This is a working audit for [the active repair goal](codex-goal.md), covering VO,
VO-LC, VIO, VIO-LC and GNSS-VIO. The repair is **not yet complete**. Staged numerical
evaluations do not establish publication qualification, and the root CSVs/site
have not yet been replaced by this repair.

## Preservation

- Parent checkpoint: `8e62998c992c9aaef5a0ddc0df2a8d2512fb1f76`.
- Expanded goal: `1926e08`; updated backup record and reusable prompt: `a836fc3`.
- Independent backup: `/data/imoroz/vslam-repair-backups/20261001T102654Z-vo-pre-repair/`.
- `VERIFIED` covers 5,396 files; `VERIFIED_ALL_MODES` covers another 4,634 files.
  All five results trees, the old browser/manifest, logs and experiments are saved.
  Nested repository changes are preserved independently of parent Git links.
- See `RESTORE.md`, checksum inventories, nested patches/archives, and the verified
  parent Git bundle in that directory. No original trajectory or historical run
  config has been replaced. No estimator execution has been started for this repair.

## Evaluation changes being validated

The new implementation is in `scripts/eval/_metrics.py`, `_pose_frames.py`,
`_trajectory_evaluation.py`, `_saved_run.py` and `_run_observations.py`.
`reevaluate_saved_runs.py` writes a separate staging tree and a manifest. During
this transition, `_evaluate_run.py` still contains the old implementation;
promotion and generator integration are outstanding.

### Physical pose frame

The target is the left optical camera: raw camera axes on EuRoC, input-image axes
elsewhere. A rigid world alignment does not correct a rotating sensor lever arm.
The conversion is `T_world_target = T_world_output * T_output_target`, applied
before alignment. A monocular estimate is never given a metric translation before
its scale is established. Instead, the reference is moved to the camera origin.

| Exporter | Evidence and conversion |
|---|---|
| ORB-SLAM3 VO/VO-LC | `System::SaveTrajectoryEuRoC` saves camera poses. EuRoC internal rectification is reproduced from the saved config, then its camera axes are converted back to raw optical axes. |
| ORB-SLAM3 VIO/VIO-LC | The same writer's inertial branch saves body/IMU poses. `Settings::precomputeRectificationMaps` already updates the internal inertial extrinsic. |
| OKVIS2/OKVIS2-X | `TrajectoryOutput` and CSV headers identify `T_WS`, the sensor/IMU pose. VO uses its effective camera extrinsic to recover the physical camera pose. |
| OKVIS2-X final VO optimization | Full BA can optimize camera extrinsics. `Component.cpp` saves them as full-precision `FRAME` records in `final_map.g2o`. Read those values only after checking they are static and the selected trajectory matches the final-BA CSV. Never substitute the initial config. |
| Basalt | Upstream `vio.cpp` queues and saves `T_w_i`. VO may use a virtual IMU/body; recover its camera pose using the saved `T_imu_cam`. The binary hash is recorded, but the installed source revision still needs provenance review. |
| AirSLAM | `Map::SaveKeyframeTrajectory` saves `Frame::GetPose`, a camera pose. Account for EuRoC internal rectification. The saved export is sparse keyframes. |
| OV2SLAM | `include/logger.hpp` serializes `Twc`. Reviewed configs disable internal stereo rectification. |
| DPVO/DPV-SLAM | Camera pose; EuRoC undistortion does not rotate optical axes. Sim(3) is the primary shape metric. |
| MAC-VO | `IOdometry.receive_frames` conjugates internal poses by `T_BS`. EuRoC also uses NED camera coordinates and internal rectification. Undo the output convention using the loader's actual composition, rather than treating it as a direct camera pose. GeneralStereo needs the NED-to-optical axis interpretation. |
| OpenVINS and Voxel-SVIO | IMU poses. Their JPL global-to-IMU quaternion coefficients represent the inverse rotation when interpreted as Hamilton xyzw, which is precisely IMU-to-world; do not invert them again. Source equations and ROS/export writers were checked. |
| Historical GNSS composites | Missing saved calibration/output-selection evidence remains a blocker. A current config does not prove the configuration used for a historical run. |

For **physical IMU outputs on EuRoC**, use the independent dataset `sensor.yaml`
camera-to-IMU transform to express the IMU estimate at the camera origin. Estimating
camera extrinsics online does not change the identity of the physical IMU frame.
This differs from VO's virtual body, whose definition depends on the effective
camera calibration. Record and hash every calibration used for evaluation.

The Basalt output convention was checked against
[the upstream source](https://github.com/VladyslavUsenko/basalt/blob/0f3b2b52c807f70ff4e2973ce253c73329eea7bc/src/vio.cpp).
The Rosario reference camera lever arm comes from
[the published CIFASIS evaluation configuration](https://github.com/CIFASIS/rosariov2/blob/82115db620b57a5decb48ffe70b4639f00ce3ec9/data/evaluation/orb-slam3_rosariov2.yaml).

### Reference limitations still open

- **HortiMulti:** the original Strawberry02 CSV identifies `TagMap/base_link`;
  Strawberry03 identifies `odom/odom_mapping`. The available camera-to-IMU transform
  does not establish either reference-to-IMU transform. No shared reference frame
  is assumed. Position diagnostics remain provisional; full relative-pose metrics
  are withheld pending that chain. These CSVs contain nonzero z/roll/pitch values;
  a planar upstream implementation alone does not prove these files are planar.
- **Rosario:** the extractor selects `/mins/imu/pose` and the images are
  `/realsense/infra1/image_rect_raw`. Resolve the precise rectified camera axes and
  reference chain before qualifying rotation metrics. The published ORB example
  uses `ThDepth: 80`; that setting is author-provided, not automatically an
  undocumented local adaptation. Its `Camera.bf` and `RIGHT.P` also imply different
  baselines; trace which calibration applies to the actual input images before
  changing estimator configs.
- **ZED:** reference quaternions are identity placeholders. Positional scores may
  be useful, but rotational RPE and full relative-pose translation RPE are not
  supported by this reference. Camera lever-arm and altitude assumptions, and the
  residual serial-specific IMU calibration/timing uncertainty, still need explicit
  qualification for the relevant claims.
- **GNSS:** independently verify global heading, frame, origin, fusion inputs and
  reference independence. A translation-only diagnostic is now calculated without
  rotating the first pose; it is not promoted to verified global GNSS accuracy.

### Metrics and sampling

- Validate finite poses, increasing timestamps in seconds and quaternion norms.
  Do not silently sort or discard corrupt trajectory rows.
- Use at most one observed estimate per input camera timestamp (5 ms tolerance).
  High-rate IMU exports no longer overweight a score. Never interpolate estimator
  poses to manufacture dense tracking evidence.
- Interpolate raw reference poses at the selected estimate timestamps; do not
  extrapolate or bridge reference intervals above 0.5 s. Exact measured reference
  samples remain valid next to a long gap. Hash raw GT and camera times; avoid
  existence-only interpolation caches.
- Retain both SE(3) and Sim(3) ATE. Metric-scale stereo/VIO primarily uses SE(3);
  monocular shape primarily uses Sim(3). An arbitrary monocular scale outside
  `[0.1, 10]` is not, by itself, a collapse. The historical scale-collapse diagnostic
  threshold is retained only for metric-scale estimators and is explicitly recorded.
- Full translation RPE is the translation norm of
  `inverse(delta_reference) * delta_estimate`. Keep displacement-magnitude error
  under its own accurate name; it can be zero even when travel direction is wrong.
- Distance windows are overlapping custom 1/10/50/100 m windows with a first endpoint
  at/above the requested reference path distance and a +10% tolerance. They cannot
  bridge export gaps above `max(0.5 s, 5 * median camera interval)`. Normalize each
  window by its actual path distance when reporting percentages. This is not KITTI.
- Distinguish exported-pose coverage from tracking success. Withhold gap-based
  tracking interpretations for keyframe-only AirSLAM. Its sparse accuracy cannot
  silently join a dense-frame comparison.
- Regenerate geometric row/turn labels from reference path heading, not an optical
  frame's Euler yaw. Coalesce adjacent equal labels after removing short segments,
  retaining the joining path distance. Keep one global alignment for all segments;
  the monocular segment metric uses global Sim(3). These are automatic geometric
  labels, not manually verified agricultural manoeuvres.
- Missing initialization messages mean unknown. Startup/readiness text does not
  prove initialization. Recorded log-pattern counts do not establish the number of
  unique tracking failures or correctly accepted loop closures.

## Validation and remaining work

The initial 31 tests pass in `/data/imoroz/conda/envs/macvo/bin/python`, including
independent numerical comparisons with evo for SE(3), Sim(3), translation RPE,
rotation RPE and displacement-magnitude error. Synthetic cases exercise rotating
lever arms, rectification direction, reference gaps, sparse/high-rate exports,
invalid input, GNSS heading preservation, saved-config hashes, final calibration
recovery, missing log evidence and segment coalescing.

Staging is under `results/repair-20261001/`. Its manifest records every processed
artifact and errors. The execution log is `schema3-staging.log` in the backup
directory. This inventory includes historical/smoke/variant artifacts; membership
in staging does not make them members of the executed 600-attempt campaign.

The first complete staging pass processed **593 artifacts in 95 seconds**, with
no staging exceptions: VO 202, VO-LC 136, VIO 142, VIO-LC 87 and GNSS-VIO 26.
Evaluator digest: `839ef9f89adc753ea61f6e8c80ae79ad48be7e1ce715a2372704ebb0a6646eeb`.
This produced nine previously absent evaluation records: seven campaign attempts
and two smoke attempts. Smoke attempts remain outside campaign counts.

| Recovered campaign artifact | Staged position result | Execution evidence retained |
|---|---|---|
| OKVIS2 VO-LC, ZED, run1 | SE(3) ATE 0.720 m; reference limitations still apply | Exit 0; no historical COMPLETE marker |
| OpenVINS VIO, EuRoC MH01, run1 | SE(3) ATE 0.067 m | Exit 134 |
| OpenVINS VIO, EuRoC MH03, run1 | SE(3) ATE 0.137 m | Exit 134 |
| OpenVINS VIO, Horti Strawberry02, run1 | Provisional SE(3) position ATE 2.621 m | Exit 134; reference transform unresolved |
| OpenVINS VIO, Horti Strawberry03, run1 | Provisional SE(3) position ATE 0.672 m | Exit 134; reference transform unresolved |
| OpenVINS VIO, Rosario sequence1, run1 | Catastrophic scale failure; SE(3) position residual about 83 km | Exit 134; retain as a failure |
| OpenVINS VIO, Rosario sequence5, run1 | Catastrophic scale failure; SE(3) position residual about 27 km | Exit 134; retain as a failure |

Thus, a shutdown error does not explain away the Rosario OpenVINS failures. Saved
poses allow their failure to be evaluated; they do not turn those attempts into
successful or qualified runs. The previously known OKVIS2 ZED VO run2, OV2SLAM
Rosario1 VO-LC run2 and OpenVINS ZED VIO run1 collapses remain present as well.

One legacy GNSS artifact fails quaternion validation: VINS-Fusion+GPS Strawberry02
run1 has 153/4,753 quaternion norms outside the 0.01 tolerance, with a maximum norm
of about 1.479. Investigate the original export and retain position-only diagnostics
where justified; do not silently normalize away the evidence or certify rotation.

Twenty-four independent ATE checks on twelve real saved trajectories spanning all
five modes agree with evo to a maximum absolute difference of `5.33e-15` m. These
check both SE(3) and Sim(3), including recovered OpenVINS/OKVIS2 outputs, final BA,
monocular DPVO, sparse AirSLAM and historical GNSS. The record is
`results/repair-20261001/independent-validation.json`. This proves numerical
agreement on the supplied paired poses, not the correctness of unresolved input
calibration or reference conventions.

## Configuration selection and native-export checks

Read-only checks in `results/repair-20261001/config-export-validation.json` cover
all 48 ORB/Basalt mode–sequence selections and all 24 saved MAC-VO VO repetitions.

- ORB now selects the existing sequence-specific ZED 10 FPS profile in VO/VO-LC.
  The previous runner selected the generic 15 FPS profile. The six historical
  VO/VO-LC repetitions retain their original snapshots and require a corrected
  configuration cohort; editing evaluation cannot change estimator behavior.
  Preflight checks the configured rate against the observed mean input rate, with
  a fixed 5% acquisition tolerance. ZED's irregular 15-to-10 Hz decimation has a
  median interval near 1/15 s, so using median interval here would be incorrect.
- Basalt's upstream VO triangulation gate compares squared camera translation
  against `vio_min_triangulation_dist` squared. Rosario's 0.0497336941 m baseline
  cannot pass the 0.05 m initial stereo gate. Keep the recovered Rosario 0.03 m
  setting as an explicit dataset compatibility exception in
  `configs/basalt/rosariov2_vo_config.json`; restore the upstream 0.05 m setting for
  the other six VO cells, matching their historical snapshots. This reconciles a
  post hoc compatibility repair with the policy; it is not a prespecified universal
  parameter or a setting selected from test-set ATE. The runner now validates the
  gate against the calibration baseline. Source:
  [Basalt VO triangulation](https://github.com/VladyslavUsenko/basalt/blob/0f3b2b52c807f70ff4e2973ce253c73329eea7bc/src/vi_estimator/sqrt_keypoint_vo.cpp).
- Basalt ZED's previous and current transforms have identical relative stereo
  geometry (maximum matrix difference `1.39e-17`); the virtual body frame changed.
  Pure VO evaluation uses its saved frame. This finding does not validate the old
  VIO extrinsic or fix sensor fusion after execution.
- All 24 MAC-VO saved exports have the complete native pose count. EuRoC native
  nanosecond timestamps and GeneralStereo's verified left/right image order give
  exactly the timestamps in the existing TUM files. Pose differences are bounded
  by the previous six-decimal export rounding (`5.01e-7` per component). Original
  trajectories were not overwritten. The converter now rejects unknown loaders,
  partial/nonsequential exports and mismatched image ordering instead of assigning
  an invented frame rate or blindly attaching the first N input timestamps. The
  runner requires a unique fresh sandbox for the exact dataset/odometry project.

The configuration/export changes pass 57 evaluation/result tests and shell syntax
checks. These are static and saved-artifact checks, not estimator execution tests.
Remaining reference-frame and publication qualification blockers still apply.

## Future campaign scope extension

Attribution bookkeeping on 2026-10-01 rewrote eight repair-era commit identities
to kubojion. All eleven mapped old/new commit trees (including three unchanged
August commits) were independently checked and are identical. See the preserved
[mapping](campaigns/git-author-rewrite-20261001.json). The original history is kept
at `backup/author-before-20261001T114608Z` and in the external author-rewrite backup.
Historical run/source and backup hashes remain unchanged. The initial push failed;
the user subsequently reported a successful push and explicitly revoked the
temporary maintenance pause. The repair continues from saved work under the
existing no-push and no-estimator restrictions; the obsolete pause must not be
reapplied after context compaction.

The user extended the active goal to prepare an executable future N=3 campaign in
all five modes, retaining the current exclusions and the no-estimator-execution
restriction. The original four-mode campaign remains a historical 600-attempt
protocol. Future GNSS repetitions and input variants need explicit cohort and
action identities. Safe per-run resumption and immediate evaluation replace the
old destructive cell-wide workflow. Repair/audit completion and verified execution
readiness must be reported separately; native crashes are not resolved by wrapper
or syntax checks. See [the extended goal](codex-goal.md#7-prepare-the-future-n3-campaign-without-executing-it).

The wrapper now delegates to `scripts/campaign/run_repetitions.py`. Existing
physical run IDs are never estimated again: saved trajectories are evaluated,
partial outputs/failures are retained, and missing outputs after interruption
require an explicitly planned new attempt. Each new repetition is evaluated before
the next begins. Atomic per-attempt state, global/cell locks, independent evaluation
backups, and input/evaluator hash checks protect resumption. The legacy campaign
driver no longer trusts an old `status=ok` cell entry to skip artifact validation,
retains prior invocation history, and disables automatic retries. Direct runners
claim a fresh output directory atomically rather than accepting an occupied one.

Validation: 74 tests plus three subtests pass, including fake-executor interruption,
partial-output retention, nonzero-exit trajectory recovery, immediate evaluation,
evaluation-only retry, identity conflict and concurrent-lock cases. One real saved
ORB/EuRoC trajectory was evaluated through the new CLI into a separate staging path
and passed its read-only cache check. No estimator was invoked. Container cleanup,
native crashes and future manifest readiness still need the remaining audit; this
is not a claim that execution problems are fixed.

The reconciled inventory now counts 545 original campaign evaluations: VO 183,
VO-LC 136, VIO 139 and VIO-LC 87. There are 176 N=3 cells, 17 N=1 cells and seven
without a staged evaluation. The five scale failures remain in these counts.
GNSS has 20 default evaluation records (one invalid trajectory) and six separate
variant records. Fifteen historical excluded artifacts and nine other attempts
(seven scored) remain outside the default campaign.

The draft future manifest has 660 logical repetitions across 220 default cells.
Initial categories are six confirmed ORB FPS reruns, 87 absent repetitions and
567 cases pending recovery/qualification decisions. No reusable result or action
readiness has yet been certified; this is an intermediate review state, not a
recommendation to rerun 567 results. Hash-checked manifest validation passes and
`--require-ready` correctly fails with 660 unready actions. Eighty tests plus three
subtests pass, including matrix-format preservation and no partial launch before
detecting a blocked selection. See [the preparation record](campaigns/future-n3-preparation.md)
for commands, scope, runtime limits and unresolved historical GNSS provenance.

The subsequent GNSS input repair binds every future run to a preserved CSV/hash
and recorded variance/status policy. All five wrappers select that saved input;
OKVIS2-X converts into a private input view rather than an existence-only dataset
cache. ROS 1, ROS 2 and the native converter share strict parsing, preserve status 0,
exclude explicit no-fix rows and fill missing covariance per axis. The four current
CSV files validate, and their old native caches match position/uncertainty values
(at most 232 ns timestamp rounding difference). No historical source bytes were
overwritten or retroactively attributed to a run. Ninety tests plus three subtests
pass; see [the detailed validation](campaigns/future-n3-preparation.md#gnss-input-repair-validation).

Outstanding before this goal is complete:

1. Complete final numerical/claim reconciliation. All 593 saved artifacts are
   staged and the seven known unscored campaign trajectories have been recovered;
   their nonzero exits and missing historical COMPLETE markers remain unchanged.
   Independent numerical checks cover every mode; qualification is still pending.
2. Finish configuration, calibration, input, source, runtime and scope qualification
   for all modes, including GNSS variants and final-optimization policy differences.
3. Integrate the evaluator and qualification inventory into all export/report/site
   generators. Preserve failures and cohort identities. Validate and promote staged
   evaluations only with their provenance intact.
4. Rebuild all CSVs, cell reports and relevant figures; reconcile identities and
   metrics. Update the five original TODO matrices without changing their layouts.
5. Safely archive obsolete derived outputs; finish contradictory-documentation
   cleanup and record an exact future rerun/diagnostic list. Commit and validate the
   complete repair, including explicit qualification counts and remaining blockers.
6. Deliver the future N=3 manifest with separate reuse/rerun/missing/blocked actions,
   prerequisites, runtime estimates and readiness evidence; validate safe per-run
   execution/recovery behavior with synthetic fixtures only.

## Coverage and export reconciliation stage

Export availability is now counted before reference support is applied: a GT
outage no longer reduces the estimator's exported-pose coverage. Separate fields
report camera-pose coverage and reference-supported evaluation coverage. Tolerance
edges are clipped to input endpoints. Sparse AirSLAM exports still have unknown
dense coverage. A verified independent 600-file snapshot of the earlier staging
tree is preserved at
`/data/imoroz/vslam-repair-backups/20261001T115859Z-staging-before-coverage-repair/`.

All 593 staged evaluations were rebuilt without errors. Comparison with that
snapshot confirms unchanged SE(3)/Sim(3) ATE, RPE, paired counts and numerical
statuses in every record; 592 coverage records changed. See
`results/repair-20261001/coverage-restaging-validation.json`. The current numerical
evaluator digest is `85161e55398004ecc1f11b765deedf4b1a08300b4f650193d82ce58c073a4acb`.

VINS-Fusion+GPS Strawberry02 run1 still fails quaternion validation. Its 4,413
supported positions permit an explicitly unqualified sensor-origin diagnostic:
SE(3) RMSE 5.2624189032 m and Sim(3) RMSE 5.0125903328 m. Independent evo alignment
agrees within 3.56e-15 m (`position-diagnostic-validation.json`). No quaternion was
changed on disk; full-pose/global-GNSS accuracy remains invalid/unverified.

The CSV generator now exports all 660 planned default slots plus six GNSS variants,
including failures and missing attempts. Staged row counts are 192/144/168/96/66
for VO/VO-LC/VIO/VIO-LC/GNSS-VIO. All 226 cell/variant report groups and six report
table documents regenerate identically. Runtime/tracking fields stay unknown when
unrecorded. DPVO headline accuracy uses Sim(3); diagnostic alignment and drift
semantics are explicit. Failed repetitions cannot qualify through another run's
`ok` status. Sample standard deviation is unknown at N<2. `--check` detects changed
source CSVs or rendered bytes without writing them. Replaced derived bytes are
preserved independently under `results/.derived-history/`.

Cohort signatures now include recorded source/binary/model/parameter/environment,
workspace and hardware identities, not only config snapshots. Only DPVO's explicit
repetition seed varies within its signature. Three cells have differing recorded
workspace provenance: OKVIS2-X Rosario1 VO-LC, ORB-SLAM3 ZED VO-LC and AirSLAM ZED
VO-LC. Their cohorts remain separate pending review of that difference; matching
configs alone do not justify pooling them. This finding does not establish that
their algorithm parameters changed. Unverified legacy runs are not pooled.

Validation: 100 tests plus three subtests pass, with regression coverage for these
semantics, preserved failures/variants, inventory hash invalidation and read-only
regeneration checks. Outputs remain in staging while qualification, browser/figure
integration and promotion are finished. This is an export-repair milestone, not
completion of the goal or certification of future execution readiness.

## Confirmed AirSLAM fusion-frame issue

The subsequent [AirSLAM rectification audit](airslam-rectification-audit.md)
confirms a raw/rectified camera-to-IMU mismatch in recorded source and all 18
EuRoC VIO/VIO-LC saved configurations. Its source patch passes apply-check and
transform-composition validation but is not applied, built or execution tested.
The historical source/binary attribution limitation remains explicit. Future
map-refinement retries are now disabled instead of deleting and retrying partial
stage outputs; original stage trajectories are retained when exporting the common
trajectory filename. Shell syntax and a synthetic early-rejection test pass.
Shared-container process ownership and native stage exit accounting still need
repair/verification.

TODO's existing six affected cells now include `rerun: rectified IMU`, preserving
their N=3 observation counts and exact matrix layout. The inventory and future
manifest derive the finding only from hash-verified historical snapshots and the
recorded clean source revision. Current action counts are 24 required reruns
(six ORB FPS plus 18 AirSLAM fusion cases), 87 missing and 549 blocked/review;
no qualified reuse or execution readiness is claimed. The runtime subtotal remains
36.1 hours for 19 known actions; 92 missing/rerun actions have unknown runtime.

## Browser integration stage

The browser now uses the authoritative inventory rather than scanning COMPLETE
markers. Its 690 entries comprise 660 planned default repetitions and all 30
separately identified variant/historical/smoke artifacts. Numerical outcomes,
execution, source provenance, scientific qualification, cohorts and variants are
shown separately; absent run hardware is not replaced by the generator host.
Stale inventory/CSV/evaluation hashes are rejected. Current numerical JSONs are
linked separately from historical saved evaluation artifacts.

Legacy images are retained and labelled `historical_derived`, with no previews
suggesting that they were regenerated under schema 3. Historical/smoke artifacts
are outside the initial browser filter. New builds use a unique temporary directory;
an existing site is moved into `results/.derived-sites/` before replacement.
The staged browser is under `results/repair-20261001/site/`; root promotion and
validated figure replacement remain outstanding. Browser regression tests pass,
and a local link audit is saved as `browser-validation.json` in the staging tree.
