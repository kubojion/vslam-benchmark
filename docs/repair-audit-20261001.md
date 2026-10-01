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

Outstanding before this goal is complete:

1. Audit staged numerical changes and failures against actual saved artifacts;
   resolve recoverable timestamp/export issues and independently check real cases
   in every mode. Recover the seven known unscored campaign trajectories without
   changing their recorded process-exit evidence.
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
