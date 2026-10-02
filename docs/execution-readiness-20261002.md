# Focused execution readiness — 2026-10-02

Status: **in progress**. Continue the completed main integration at `03c7c0e`;
checkpoint `0fa0066` preserves its final documentation. This task does not repeat
the broad benchmark audit. The exact authorized objective is preserved in
`results/execution-readiness-20261002/authorized-goal.txt`.

## Required work and completion evidence

| Work | Current status | Required evidence |
|---|---|---|
| Explicit Rosario candidate selection | Pending | Basalt calibration/settings selected independently; consistent indexed profiles; snapshots of every loaded file; reject bad selections |
| Rosario native handling | Pending | Bounded diagnostic records of effective calibration, transforms, image transport, timing, first-frame IMU bracketing, export frames/times and shutdown |
| Recording-specific Rosario camera profile | Pending authors | Diagnostic success cannot settle the image/rectification question or select a profile by score |
| Voxel ZED first 180 seconds | Pending | Predeclared first-window checks, unchanged thresholds, destructor repair, input receipt, initialization outcome, frame/time validation, independent native/export outcomes |
| Shutdown versus trajectory outcomes | Pending | Individual evidence for complete exports, partial/tracking failure and no usable export; preserved exits; consistent ledger/CSV/TODO semantics |
| Non-ZED ORB build compatibility | Pending | Historical executable/library/g2o evidence classified compatible/incompatible/unknown; repaired-path short checks; exact affected list and timing estimate |
| Completed ZED first repetitions | Pending | Review ORB/OKVIS2/OKVIS2-X run10001 effective setup, coverage, references, exits and counters; retain completed attempts |
| Remaining ZED VIO first repetitions | Pending engineering | New sequential continuation for AirSLAM, Basalt, OpenVINS, and Voxel only if setup verified; immediate evaluation; no repetitions 2/3 or other modes |
| Final reporting and commit | Pending | TODO/details, focused tests, blockers, reviewed outcomes, executable next list, refreshed identities/preflights, local commit; no push |

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
