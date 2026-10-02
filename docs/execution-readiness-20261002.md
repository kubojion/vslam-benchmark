# Focused execution readiness — 2026-10-02

Status: **in progress**. Continue the completed main integration at `03c7c0e`;
checkpoint `0fa0066` preserves its final documentation. This task does not repeat
the broad benchmark audit. The exact authorized objective is preserved in
`results/execution-readiness-20261002/authorized-goal.txt`.

## Required work and completion evidence

| Work | Current status | Required evidence |
|---|---|---|
| Explicit Rosario candidate selection | Implemented and tested | `ROSARIO_VIO_PROFILE` selects indexed snapshots; Basalt calibration/settings overrides are separate; conflicting/tampered/missing selections are rejected |
| Rosario native handling | Bounded handling checks completed | Both sequences exercised for all four candidates; corrected Voxel initializer offset verified; Basalt native calibration/settings and final wrapper regression verified; OpenVINS online-calibration export scope remains limited |
| Recording-specific Rosario camera profile | Pending authors | Diagnostic success cannot settle the image/rectification question or select a profile by score |
| Voxel ZED first 180 seconds | Native check completed; wrapper capture violation retained | Native/player exit 0; initialization at 39.456 s, 1,406 poses; wrapper exit 1 because shared sources changed during that diagnostic. Subsequent short checks verify actual loading fixes; this is not a clean production repetition |
| Shutdown versus trajectory outcomes | Individual review and reporting implementation prepared | 154 attempts inspected; 79 completed exports with shutdown errors, two partial exports with shutdown errors, five without usable exports. A scale-collapse outcome remains a trajectory failure even when export completed |
| Non-ZED ORB build compatibility | Historical audit and seven bounded checks completed | 76 historical attempts unknown, none confirmed incompatible/compatible; current reviewed libraries loaded and clean native exit in all seven checks. No blanket rerun authorized |
| Completed ZED first repetitions | Reviewed; accepted with position-reference and reproducibility limitations | ORB/OKVIS2/OKVIS2-X run10001 retained; effective setup, coverage, references, exits and counters reviewed. These are N=1 observations, not N=3 cells |
| Remaining ZED VIO first repetitions | Pending engineering | New sequential continuation for AirSLAM, Basalt, OpenVINS, and Voxel only if setup verified; immediate evaluation; no repetitions 2/3 or other modes |
| Final reporting and commit | Reporting reconciled and committed; identity/preflight refresh pending | TODO/details, focused tests, blockers, reviewed outcomes and local commit completed; refreshed identities/preflights and the executable next list follow the bounded ZED rechecks; no push |

## Verified engineering findings

Source checkpoint `3be9197` repairs Voxel initialization's omitted camera–IMU
offset and the ZED YAML numeric spelling that previously selected ROS's
`1e-15` fallback instead of the declared `1e-12`. The native v3 dumps now show
the declared threshold and identical propagation/initialization offsets. These
are loading repairs, not accuracy tuning. ZED's fixed first-ten-second check
remains a valid noninitialization outcome: all inputs arrived and both native
and player exited zero, without a trajectory.

Basalt now receives an attempt-local IMU CSV with the declared offset subtracted
and an effective native calibration offset of zero. Camera timestamps and all
measurement values stay unchanged. Both Rosario 60-second checks and the ZED
10-second check exited cleanly with finite camera-clock exports. GDB factory
inspection verifies both full transforms, camera types/intrinsics/distortion,
resolutions, IMU rate and noise vectors against the loaded native calibration.
The native settings serializer exposes 48 fields; four fields in the requested
profiles are unsupported by installed release 0.1.7. Their explicit removal from
the effective input, preservation in provenance, and runtime-hash guard are
implemented; the final wrapper regression passed at `3cee23b`. Ordinary float32
rounding is distinguished from omitted settings.

The [final Basalt regression](campaigns/basalt-final-review-20261002.json) has
three clean native/wrapper exits: one Rosario check and two identical-input ZED
checks. Both ZED attempts have the same cohort fingerprint. The preceding
diagnostic produced a trajectory but failed metadata finalization because the
grouping marker was supplied twice; that wrapper failure remains preserved.

The [OpenVINS review](campaigns/openvins-native-review-20261002.json) verifies
both cameras' loaded transforms, intrinsics and distortion in all four existing
Rosario checks, clean node/player exits, complete publication, and finite ordered
IMU-clock exports. Its upstream DEBUG print formats integer `init_max_features`
as a float, misleadingly showing 10.00. A loading-only native argument probe
verifies 50 in both profiles. The original debug-format defect remains disclosed;
it is not evidence that the estimator used 10 or that a parameter was tuned.
The author profile estimates spatial calibration online without saving its
per-pose history, so these diagnostics do not qualify static camera-origin scoring.

The [bounded native review](../results/execution-readiness-20261002/post-repair-native-review.json)
records all 13 checks and the independent Basalt memory inspection. The
[180-second review](../results/execution-readiness-20261002/voxel-180-review.json)
preserves the earlier capture failure. No second 180-second window was selected
to obtain a favorable result. The nine earlier candidate checks remain in
`results/execution-readiness-20261002/rosario-native-state.json`.

Voxel's historical EuRoC gaps exactly match its native floating-point 20 Hz
gate. The last historical ZED image occurs after the final IMU sample and is
therefore unsupported by Voxel's native buffer gate. These explain coverage
limits; complete export does not imply every camera frame was tracked. The
[individual export review](campaigns/export-completion-review-20261002.json)
preserves native errors and never promotes a shutdown error into S.

ORB's completed ZED run10001 has five recoverable local-tracking failure
messages, 96 LocalMapping reset messages, 96 IMU-initialization reset requests,
one map-creation message and zero explicit full Tracking map-reset messages.
These overlap and are message counts, not unique failure episodes. The
[log overlays](campaigns/log-observation-review-20261002.json) correct reporting
without modifying original evaluations.

## Historical ORB exposure and reporting hold

The [exact 76-attempt audit](campaigns/orb-historical-exposure-20261002.json)
finds saved executable hashes but no historical per-run shared-library/g2o
identities. Today's incompatible libraries, similar crash symptoms and matching
scores cannot establish historical compatibility. All 76 remain **unknown**;
there are no newly confirmed ABI replacements. Previously confirmed setup
replacements remain required for their original reasons.

This material evidence gap withholds 12 previously green EuRoC ORB cells;
the current verified protocol total is **69**, down from 81. Original decisions
are retained in the ledger alongside the new hold; all scores and attempts stay
preserved. First recover historical dependency/build records if available. A
proportionate current-path check has already covered both executables, all four
modes, and the Rosario/Strawberry02 startup cases. It cannot prove historical
memory safety. The contingency subtotal for replacing all unknown observations
would be 6.17 hours for 57 estimated attempts plus 19 with unknown runtime; this
is neither a campaign recommendation nor execution permission.

Future manifest identities/preflights still need refresh. No remaining full ZED
first repetition has been launched by this work.

Eight ZED readiness entries pin runner or configuration bytes that changed after
their 60-second checks: ORB-SLAM3 in all four modes, Basalt VIO, OpenVINS VIO and
Voxel-SVIO VIO. The reviewed plan cannot verify their readiness until one bounded
recheck per entry is recorded with the current bytes; the AirSLAM, OKVIS2 and
OKVIS2-X entries remain current. Source identities include the checkout commit,
so the identity, manifest and preflight refresh must follow the final commit and
immediately precede a launch. Neither step has been run by this checkpoint.

The [completed ZED review](campaigns/completed-zed-first-review-20261002.json)
accepts each of the three saved run10001 observations for nominal left-camera
position accuracy with stated limitations. All have 46,280 poses for 46,283
input pairs and native exit zero. Saved effective transforms match the recovered
serial calibration; VIO disables loop closure and final BA. Re-evaluation
reproduces primary ATE exactly. Fixed-only ATE is 0.29857 / 0.52967 / 0.42545 m
for ORB / OKVIS2 / OKVIS2-X; primary ATE is 0.29713 / 0.52824 / 0.42423 m.
Clock sensitivity at ±0.1 s is at most 1.42 mm across these three outputs; no
offset is fitted or applied. Nominal terrain/mounting assumptions, RTK float,
unavailable orientation, and incomplete transitive build reconstruction remain
explicit limits. Acceptance preserves their recorded implementations and does
not establish real-time performance or a three-repetition cohort.

Reporting checkpoint: **285 tests and seven subtests pass** across campaign,
evaluation and results-browser tests. All five CSVs, the historical-cohort CSV,
cell reports, tables, figures, browser and TODO/details are reconciled. All 252
matrix cells retain A/E/S/F counts. The preservation check verifies **5,128
unchanged historical evidence files**. Reviewed log counters are visible for the
three completed ZED first attempts. Their subsequent explicit claim review is
complete and replayed in this refresh: the three cells report ✔ N=1 with two
missing repetitions, while 69 verified N=3 cells and 552/600 evaluations are
unchanged.
Future plans are visibly unready until their changed implementation identities
and review prerequisites are refreshed; this is not a claim that their earlier
bounded execution observations failed.

New Basalt/Voxel receipt grouping verifies every saved receipt hash, normalizes
only attempt-local paths in named configuration receipts, and keeps input-receipt
counts as outcomes rather than settings. It requires an explicit schema marker;
historical cohort signatures are preserved. The final bounded Basalt regression
verified effective settings and equal cohort identities across two isolated
identical-input diagnostics.

## Preservation and execution boundaries

Historical trajectories, logs, evaluations, configuration snapshots and executed
manifests remain immutable. The initial evidence hash inventory is
`results/execution-readiness-20261002/preservation-baseline.json`; prior verified
snapshots remain available. New reviews are separate records. Existing algorithm
exclusions and all unrelated colleague changes are preserved.

No active benchmark wrapper, native estimator or evidence-capture process was
found before the checkpoint. Shared engineering changes must finish, be committed,
and have refreshed execution identities before production resumes. Bounded
candidate diagnostics are authorized and stay outside production comparison
cohorts. The subsequent long attempts must use a standalone sequential controller;
continuous AI polling is not part of the execution plan.

Rosario retains **14 confirmed historical replacements** for the erroneous IMU
extrinsic and **four missing OpenVINS repetitions**. Corrected profiles are prepared;
the final profile and native handling are separate readiness gates. Green protocol
ticks include valid observed failures. No clean-exit label is awarded to a native
shutdown error, and unrelated scientific blockers remain explicit.
