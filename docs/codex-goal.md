# VO benchmark repair and qualification goal

Prepared: 2026-10-01. Workspace: `/data/imoroz/vslam-benchmark`.

## Objective and scope

Repair and reconcile the existing **VO-only** benchmark so that saved results,
evaluation, CSVs, reports, documentation and the TODO matrix agree, and each result
has an evidence-based publication qualification. Continue the preceding VO audit;
do not silently expand scientific qualification to VO-LC, VIO, VIO-LC or GNSS.
Shared code changes must preserve those modes and explicitly document any impact
or need for later re-evaluation. Keep other modes' existing matrix entries intact
unless correcting an objectively established inventory fact; do not award them
new scientific qualification as a side effect of this work.

The user requests no new estimator executions. Use existing trajectories, logs,
config snapshots, calibration sources and metadata. Unit tests, synthetic fixtures,
read-only diagnostics, artifact validation and re-evaluation of saved trajectories
are allowed. Do not start/resume a campaign, run smoke estimators, replace failed
repetitions with new attempts, add algorithms, or download/rebuild large models.

This file is the preparation deliverable. The checkpoint below is the first step
of implementation, before editing benchmark code, configs, results or existing docs.

## 1. Preserve all existing progress before implementation

1. Re-read applicable repository instructions. Inventory Git status, active jobs,
   nested repositories, ignored results/logs, available disk space and existing
   backup facilities. A colleague may be working concurrently; never overwrite
   unrelated changes or terminate their jobs.
2. Create a clearly identified local checkpoint commit preserving existing project
   work, including appropriate untracked source/documentation files. Do not use a
   blanket `git add -A` without reviewing the inventory: datasets, model weights,
   environments and large generated binaries should not accidentally enter Git.
3. Preserve dirty/untracked changes inside submodules and the untracked DPVO source
   checkout independently. A parent commit recording a submodule revision does not
   preserve its dirty contents. Capture revisions, binary-safe diffs, and relevant
   untracked source files, or use suitable nested checkpoint commits.
4. Back up every ignored/untracked artifact that will be overwritten or removed,
   including current evaluation JSONs, cell reports, CSVs and generated outputs.
   Preserve trajectories, logs, resource records, effective configs and provenance.
   Prefer a verified snapshot/reflink or archive outside the mutable results tree;
   hard links alone do not protect against in-place writes. Do not duplicate
   immutable multi-terabyte inputs unnecessarily.
5. Record checkpoint hashes, backup locations, checksums and restoration commands.
   Verify that restoration is possible before proceeding. No reset, destructive
   clean, history rewrite, force push or removal of the only copy of evidence.

## 2. Establish the authoritative inventory and protocol

- Use the executed N=3 campaign manifest, not directory count or the older N=5 plan,
  to enumerate target VO cells and repetitions. At the preceding audit there were
  64 cells, 192 target repetitions and 183 current evaluated repetitions. Recount;
  these are observations, not constants to force into the output.
- Distinguish successful execution, valid saved trajectory, evaluated repetition,
  scientifically qualified configuration and genuine estimator failure.
- Preserve every genuine failure. Identify historical DROID runs and smoke tests
  separately; do not include them in the accepted campaign merely because they
  have a `COMPLETE` file.
- Freeze documented definitions for pose frames, SE(3)/Sim(3) alignment, timestamp
  association, reference support, coverage, failure handling and timing semantics.
- Trace effective run configs and algorithm revisions rather than assuming today's
  config produced historical outputs. Verify hashes and within-cell consistency.
- Classify uncertainty explicitly. Absence of a detected defect is not evidence
  that an unknown calibration, pose convention or processing count is correct.

## 3. Correct evaluation using saved trajectories

### Pose frames and reference validity

- Establish the physical output frame for every VO algorithm/dataset from source,
  saved configuration and calibration evidence. Include rectified versus raw
  optical frames, camera/body/IMU transforms and antenna-to-camera lever arms.
- Convert estimates/reference poses consistently before computing metrics. Apply
  translation and orientation correctly; a global alignment is not a substitute
  for the rigid transform between sensor origins.
- The audit found camera/body discrepancies on EuRoC. A diagnostic one-second
  rotation comparison improved markedly after applying the camera extrinsic; this
  diagnostic is not itself a replacement published metric or a universal transform.
- Do not report rotational accuracy for ZED's identity-quaternion reference
  placeholders. Preserve valid positional metrics with their reference limitations.
- Validate interpolation, timestamp units, gaps and reference/calibration hashes.
  Replace existence-only cache reuse where stale inputs would invalidate outputs.

### Metrics, sampling and failures

- Correct the main-table DPVO mismatch: monocular shape evaluation requires the
  declared Sim(3) metric; stereo metric-scale evaluation uses SE(3). Label both
  clearly and avoid misleading cross-modality ranking.
- Correct the use/description of evo `point_distance`. It measures displacement
  magnitude differences, not full relative-pose translation error. Implement the
  intended conventional metric where reference poses permit it, or expose the
  existing quantity under an accurate name. Do not call custom 10/50/100 m windows
  the standard KITTI protocol. Preserve legacy values under an explicit schema if
  needed for traceability.
- AirSLAM exports keyframes. Do not infer tracking loss solely from keyframe gaps,
  count keyframes as processed images, or silently interpolate across unknown loss.
  Recover dense poses only if existing artifacts and verified semantics support
  it. Otherwise retain clearly labeled sparse metrics and qualification blockers;
  do not fabricate dense evidence to obtain a green tick.
- Record success/attempt counts and genuine collapse explicitly. Mixed success
  and failure cells must not qualify through an `any ok` aggregation condition.
- Missing log patterns must produce unknown instrumentation, not a false claim of
  failed initialization or zero tracking loss.
- Keep paced, transport-driven and maximum-throughput timing distinct. Do not
  infer real-time latency or deadline performance from an offline wall-clock rate.

## 4. Resolve configuration inconsistencies without new runs

- Document author-provided settings separately from benchmark adaptations. Audit
  algorithm parameters embedded in files named camera/calibration configs too.
- ORB-SLAM3 ZED snapshots specify 15 FPS for an approximately 10 Hz input. Correct
  future-run configuration/validation as justified, preserve historical snapshots
  and mark affected results for rerun if estimator behavior could change.
- Basalt Rosario runs use triangulation threshold 0.03; six other cells use 0.05.
  Reconcile this with the stated parameter policy and physical baseline evidence.
  Do not select settings by final test-set ATE, or silently relabel old runs as
  having used the current configuration. Review ZED's changed shared extrinsics.
- AirSLAM depth limits and ORB depth thresholds vary by dataset. Trace provenance
  and justification; disclose justified adaptations and flag unsupported ones.
- Retain ORB startup failures on Rosario 1/5 and Strawberry 02. Fix only source or
  wrapper defects that can actually be established/tested without estimator runs;
  record unresolved crash causes and exact future diagnostic requirements.
- Review the four recorded post-save ORB crashes independently from startup
  failures. A saved valid trajectory may support analysis, but does not prove a
  clean exit or a particular crash cause. Preserve that distinction in status.
- Retain OKVIS2 ZED run 2's scale collapse. Do not misattribute it to OKVIS2-X or
  replace it with successful repetitions. Investigate existing artifacts only.
- Clarify MASt3R-SLAM/MegaSaM exclusion history and rationale without claiming a
  Git author proves who approved the decision. Do not add or run them in this goal.

## 5. Re-evaluate, reconcile and clean up

1. Validate corrected evaluation on representative saved trajectories and synthetic
   tests. Stage new outputs separately so failure cannot erase the existing set.
2. Re-evaluate all affected current VO runs with the selected evaluator schema.
   Retain immutable original trajectories and source provenance. Record evaluator
   identity, transforms, inputs and old/new metric changes.
3. Rebuild target-filtered VO CSVs, per-cell summaries, tables and relevant figures
   from one authoritative inventory. Report missing/failed attempts explicitly.
   Reconcile run identifiers, statuses, N, metrics and provenance across all layers.
4. Ensure shared generators cannot accidentally mix smoke, historical, accepted,
   superseded and differently configured repetitions. Avoid silently refreshing
   unqualified non-VO results under changed scientific assumptions.
5. Archive superseded reports and unused derived material after checking references
   and backups. Remove only confirmed disposable duplicates/caches with no evidence
   value. Failed logs, old configs and original metrics are not automatically junk.
6. Update README, PROGRESS, evaluation/configuration documentation, campaign records,
   generated-report notes and any other relevant contradictory status statements.
   Keep historical records clearly dated rather than rewriting what happened.

## 6. Preserve the TODO matrix and qualify cells honestly

Keep the user's existing matrix layout, cells, sequence order, headings and task
tables. Update cell contents and a concise legend; do not replace the matrix with
a prose checklist.

Maintain separate machine-readable fields for run count, observed outcome and
scientific qualification, and derive displayed statuses from them where practical:

- `N=3 ✅`: all three target repetitions have verified provenance, justified and
  consistent effective settings, validated inputs/output conventions, appropriate
  evaluation, sufficient evidenced coverage, reconciled exports and no unresolved
  issue affecting the reported claim. A tick does not mean high accuracy or prove
  correctness with absolute certainty.
- `N=3 ⚠ review`: three evaluations exist but a material issue remains unresolved.
- `N=3 ⚠ 1 failure` or equivalent: retain the full outcome distribution. A valid
  algorithm failure can be publishable evidence without being a clean-success tick.
- `rerun required`: identify the exact cells/repetitions and why saved-artifact
  correction cannot recover the needed evidence. Do not execute those reruns.
- `missing/failed attempt`: distinguish absent evidence from a completed evaluation.

Use the same meanings wherever results are marked. Do not lower qualification
criteria to make the matrix green. If data needed to decide are unavailable, leave
the specific blocker explicit and continue other authorized work.

## 7. Validation and completion

- Add meaningful tests for transform direction/lever arms, rotation-reference
  availability, metric semantics, sparse coverage, campaign filtering, mixed failure
  aggregation and cache invalidation where changed. Run relevant existing tests.
- Cross-check representative numerical results independently. Reconcile all current
  VO identities and per-run exports; verify reproducible report generation.
- Keep an audit of confirmed fixes, metric changes, archived paths, unresolved
  assumptions and the exact future rerun list. Note effects of shared code on modes
  outside VO without certifying them.
- Commit completed repairs and documentation in reviewable local commits. Preserve
  collaborators' subsequent changes; do not push or publish externally.
- Deliver checkpoint/final commit hashes, backup locations, validation results,
  qualified-cell counts, remaining blockers and required future runs.

The goal is complete when every issue repairable within the no-new-runs scope has
been addressed and validated, all relevant outputs/docs agree, and irrecoverable
or unproven cases have explicit actionable statuses. Completion does not require
all cells to be green, successful new runs, or a promise of publication acceptance.

## Initial effort estimate

Approximately 8–16 hours of active work plus any additional machine time required
for backup and re-evaluation. This is a planning estimate, not a deadline promise;
calibration provenance gaps or unexpectedly large artifacts may change it. Give
progress updates and continue until the defined scope is complete.
