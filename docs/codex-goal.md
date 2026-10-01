# All-configuration benchmark repair and qualification goal

Prepared: 2026-10-01. Workspace: `/data/imoroz/vslam-benchmark`.

## Objective and scope

Repair and reconcile **all five benchmark configurations: VO, VO-LC, VIO, VIO-LC
and GNSS-VIO**, across their existing algorithms, datasets, repetitions and declared
input variants. Saved results, evaluation, CSVs, reports, documentation and every
TODO matrix must agree, and each result must have an evidence-based publication
qualification. The user explicitly expanded the ongoing goal from VO to all
configurations on 2026-10-01; this revised scope supersedes the original VO-only
wording wherever it remains in earlier chat or the initially registered objective.

Scope extension, 2026-10-01: also prepare an executable **future N=3 campaign across
all five modes**, retaining the existing algorithm exclusions. This extends the
active goal; preserve completed repairs, staged evaluations, commits and backups.
Do not restart the audit. Campaign preparation is authorized; campaign execution
is not. Keep the stricter existing restriction against new estimator executions
unless the user explicitly changes it later.

The earlier VO findings are the starting evidence, not an exhaustive issue list.
Audit each additional mode independently, including its sensor inputs, calibration,
loop-closure behavior, failure evidence, evaluation and exports. Shared code fixes
must be tested across all affected modes; do not infer qualification in one mode
from successful results in another.

The user requests no new estimator executions. Use existing trajectories, logs,
config snapshots, calibration sources and metadata. Unit tests, synthetic fixtures,
read-only diagnostics, artifact validation and re-evaluation of saved trajectories
are allowed. Do not start/resume a campaign, run smoke estimators, replace failed
repetitions with new attempts, add algorithms, or download/rebuild large models.

Initial preservation is complete: checkpoint commit
`8e62998c992c9aaef5a0ddc0df2a8d2512fb1f76` and verified backup
`/data/imoroz/vslam-repair-backups/20261001T102654Z-vo-pre-repair/`.
That backup now contains all five results trees, the results site/manifest, logs,
experiments and nested repository changes. The initial 5,396 copied files were
verified against their originals; the extension verified another 4,634 files from
VO-LC, VIO, VIO-LC and GNSS-VIO. The backup records this in `VERIFIED` and
`VERIFIED_ALL_MODES`, with checksum inventories and restoration instructions.
Preserve and verify any additional affected artifacts before changing them.

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

- Use the executed N=3 campaign manifest to enumerate the four non-GNSS modes:
  200 cells and 600 planned repetitions. The preceding audit found 538 evaluated
  repetitions, including 183 VO evaluations. Recount; these are observations, not
  constants to force into the output.
- Inventory GNSS-VIO separately, including default, conventional-GPS, PPK and other
  declared variants. Preserve its historical machine/cohort identities. GNSS was
  excluded from the executed N=3 campaign; inclusion in this audit does not turn its
  N=1 results into N=3 results or claim the older N=5 plan has been fulfilled.
- Reconcile the original N=5/GNSS proposal, actual executed manifests, recovery
  campaigns and current artifacts without silently redefining their run targets.
  Report outstanding repetitions and scope decisions without launching runs.
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

- Establish the physical output frame for every algorithm/dataset/mode from source,
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

- Correct the main-table DPVO/DPV-SLAM mismatch: monocular shape evaluation requires
  the declared Sim(3) metric; metric-scale stereo/VIO evaluation uses SE(3). Label
  both clearly and avoid misleading cross-modality ranking.
- Define GNSS global-frame accuracy separately from freely aligned trajectory
  shape accuracy. Verify ENU/NED/ECEF conventions, origins, antenna lever arms,
  timestamps and any permitted translation/yaw alignment. Evo `align_origin`
  aligns the first pose's rotation as well as translation; do not describe it as
  translation-only or let alignment conceal the global error being studied.
- Document the independence and limitations of each reference trajectory,
  particularly where GNSS used by an estimator also contributes to the reference.
  Keep conventional and PPK input variants separate in comparisons/aggregation.
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

## 4. Resolve configuration inconsistencies across all modes without new runs

- Document author-provided settings separately from benchmark adaptations. Audit
  algorithm parameters embedded in files named camera/calibration configs too.
- ORB-SLAM3 ZED snapshots specify 15 FPS for an approximately 10 Hz input. Correct
  future-run configuration/validation as justified, preserve historical snapshots
  and mark affected results for rerun if estimator behavior could change.
- Basalt Rosario VO runs use triangulation threshold 0.03; six other VO cells use 0.05.
  Reconcile this with the stated parameter policy and physical baseline evidence.
  Do not select settings by final test-set ATE, or silently relabel old runs as
  having used the current configuration. Review ZED's changed shared extrinsics.
- AirSLAM depth limits and ORB depth thresholds vary by dataset. Trace provenance
  and justification; disclose justified adaptations and flag unsupported ones.
- Retain ORB VO startup failures on Rosario 1/5 and Strawberry 02. Fix only source or
  wrapper defects that can actually be established/tested without estimator runs;
  record unresolved crash causes and exact future diagnostic requirements.
- Review the four recorded post-save ORB crashes independently from startup
  failures. A saved valid trajectory may support analysis, but does not prove a
  clean exit or a particular crash cause. Preserve that distinction in status.
- Retain OKVIS2 ZED VO run 2's scale collapse. Do not misattribute it to OKVIS2-X or
  replace it with successful repetitions. Investigate existing artifacts only.
- Clarify MASt3R-SLAM/MegaSaM exclusion history and rationale without claiming a
  Git author proves who approved the decision. Do not add or run them in this goal.

### VIO and VIO-LC qualification

- Trace the actual saved camera-to-IMU transforms, coordinate axes, camera/IMU time
  offsets, rates, noise units/discretization, biases and initialization settings.
  Distinguish measured calibration from defaults or locally chosen noise inflation.
- Separate the corrected ZED IMU N=1 cohort from older identity-transform results.
  Assess the unresolved serial-specific residual rotation and timing evidence;
  corrected files alone do not prove that existing runs used them or are qualified.
- Inspect OpenVINS failed/shutdown attempts for recoverable trajectories, and
  assess its retained ZED collapse. Apply the same inspection to ORB, Voxel-SVIO,
  Basalt and other IMU methods. Do not infer OOM or bad excitation without evidence.
- Incorrect estimator-side IMU calibration generally requires rerunning estimation;
  a post-hoc trajectory transform cannot repair the sensor-fusion computation.

### Loop closure, final optimization and recovery

- Verify effective LC switches for every VO-LC/VIO-LC method and confirm they are
  off in VO/VIO. Distinguish causal online poses, final corrected poses and offline
  full bundle adjustment. Keep their accuracy and runtime claims separate.
- Reconcile the recovered OKVIS2 full-BA-disabled cohort with earlier settings and
  OKVIS2-X. Do not attribute a configuration difference solely to algorithm choice.
- Inspect unscored saved outputs, including OKVIS2 ZED VO-LC run 1, before treating
  missing evaluations as missing executions. Validate and evaluate recoverable
  artifacts without inventing completion evidence or restarting the entire cell.
- Retain OV2SLAM Rosario VO-LC collapse and all other genuine failures. Log-reported
  loop events must not be presented as verified correct/accepted loop closures.

### GNSS-VIO qualification

- Verify source measurements, fix/covariance interpretation, time association,
  antenna offsets, fusion mechanism and mode-specific settings for CIFASIS,
  OKVIS2-X, VINS-Fusion+GPS, RTAB-Map+GPS and OpenVINS+GPS.
- Label benchmark-created fusion composites accurately; they are not necessarily
  an upstream author's endorsed estimator configuration or tightly coupled fusion.
- Review historical GNSS results with missing COMPLETE markers and variant outputs
  against actual artifact/provenance evidence. Recover valid evaluations where
  possible; do not merely add markers to inflate completion counts.
- Keep historical hardware/runtimes and distinct sensor-input variants explicit.
  Flag absent calibration or input-provenance evidence instead of reconstructing
  it from today's files and claiming that it was present at execution time.

## 5. Re-evaluate, reconcile and clean up

1. Validate corrected evaluation on representative saved trajectories and synthetic
   tests. Stage new outputs separately so failure cannot erase the existing set.
2. Re-evaluate all affected existing runs across all five modes with the selected
   evaluator schema, including recoverable unscored outputs and declared variants.
   Retain immutable original trajectories and source provenance. Record evaluator
   identity, transforms, inputs and old/new metric changes.
3. Rebuild all five mode CSVs, per-cell summaries, tables and relevant figures
   from one authoritative inventory. Report missing/failed attempts explicitly.
   Reconcile run identifiers, statuses, N, metrics and provenance across all layers.
   Include the results browser/manifest and combined reports in this reconciliation.
4. Ensure shared generators cannot accidentally mix smoke, historical, accepted,
   superseded and differently configured repetitions. Regeneration must preserve
   qualification warnings and input-variant distinctions in every mode.
5. Archive superseded reports and unused derived material after checking references
   and backups. Remove only confirmed disposable duplicates/caches with no evidence
   value. Failed logs, old configs and original metrics are not automatically junk.
6. Update README, PROGRESS, evaluation/configuration documentation, campaign records,
   generated-report notes and any other relevant contradictory status statements.
   Keep historical records clearly dated rather than rewriting what happened.

## 6. Preserve the TODO matrix and qualify cells honestly

Keep all five of the user's existing matrix layouts, cells, sequence order,
headings and task tables. Update cell contents and a concise consistent legend;
do not replace matrices with prose checklists. Audit every mode's green ticks
against the new qualification criteria rather than retaining legacy completion
ticks as if they established publication readiness.

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
- `N=1` or `N=2`: preserve the actual count and any validated single-run claims;
  never display an N=3 qualification tick for fewer than three repetitions.

Use the same meanings wherever results are marked. Do not lower qualification
criteria to make the matrix green. If data needed to decide are unavailable, leave
the specific blocker explicit and continue other authorized work.

## 7. Prepare the future N=3 campaign without executing it

- Establish the future campaign's explicit dataset, algorithm, mode and input-variant
  membership from the existing scope. Retain existing exclusions, including
  MASt3R-SLAM and MegaSaM, and keep historical/smoke algorithms outside the campaign.
  GNSS-VIO now has a future N=3 target; this does not retroactively place its legacy
  runs in the previously executed four-mode campaign. Distinct GNSS input variants
  must have separate cohort identities and repetition counts.
- Deliver a versioned, executable campaign manifest and a validated runner that
  distinguish **reusable runs, required reruns, missing repetitions and blocked
  cases**. Every planned repetition must have an explicit action, evidence links,
  effective configuration identity, prerequisites and readiness status. A blocked
  case must not become executable merely because it lacks a COMPLETE marker.
- Recover and evaluate usable saved trajectories before scheduling estimation.
  A genuine algorithm failure under a valid protocol remains an observed outcome;
  do not selectively rerun failures until three successes appear. Replacement of
  an invalid configuration belongs to a new, recorded cohort, with the original
  attempt and failure retained.
- Replace destructive cell-wide preparation with safe **per-run resumption**.
  Preserve prior attempts and their logs/configs/metadata; do not overwrite an
  existing run directory. Distinguish repetition identity from attempt identity.
  Resume using verified artifact/configuration evidence, not markers alone.
  Reject conflicting or stale manifest state and protect concurrent execution.
- Evaluate each completed repetition immediately, before moving to the next
  repetition. On an estimator or evaluator error, preserve partial artifacts and
  persist that attempt's status. Recovery/re-evaluation must not require restarting
  a whole cell or erase previous outcomes. Make interruption and retry behavior
  explicit and test it using synthetic fixtures without invoking estimators.
- Audit and repair applicable configurations, runners and evaluation scripts across
  all five modes. Test preflight checks and command generation against real inputs
  and saved configuration evidence. Unresolved native crashes, missing calibration,
  unavailable executables or unverified sensor conventions remain explicit blockers.
- Estimate runtime from comparable historical attempts, documenting hardware,
  input length, pacing, final optimization and uncertainty. Give per-action and
  total serialized estimates/ranges where supported; use unknown for unsupported
  estimates. Reuse and evaluation-only work must not incur a fictitious full-run
  estimate. Include prerequisites and resource/concurrency constraints.
- Provide a dry-run/preflight command and a future execution command. Validate the
  manifest and runner now, but do not launch any full/partial campaign or estimator
  smoke run. Update all documentation and the existing TODO matrices consistently.

Keep these statuses separate:

1. **Repair/audit complete**: all work possible without new estimation is done,
   evidence is reconciled, the future manifest is usable, and remaining blockers
   have concrete prerequisites and planned actions.
2. **Verified ready to run**: the particular manifest action has passed its required
   static/input/configuration checks and any necessary execution validation has
   supporting evidence. If execution validation is missing, label it explicitly;
   a shell syntax check or a generated command does not establish execution readiness.

Neither status certifies a publishable result before evaluation/qualification.
Do not claim an unresolved execution problem was fixed, or that every action is
ready merely because the repair/audit goal has been completed.

## 8. Validation and completion

- Add meaningful tests for transform direction/lever arms, rotation-reference
  availability, metric semantics, sparse coverage, campaign filtering, mixed failure
  aggregation and cache invalidation where changed. Run relevant existing tests.
- Cross-check representative numerical results independently in every mode,
  including sensor fusion, loop closure and GNSS alignment/variant cases.
  Reconcile all current identities and per-run exports; verify reproducible report
  generation and shared-code compatibility across all five configurations.
- Keep an audit of confirmed fixes, metric changes, archived paths, unresolved
  assumptions and the exact future rerun list, grouped by mode, dataset, algorithm,
  input/configuration cohort and repetition. Clearly distinguish re-evaluation
  already completed from estimation that must be rerun later.
- Commit completed repairs and documentation in reviewable local commits. Preserve
  collaborators' subsequent changes; do not push or publish externally.
- Deliver checkpoint/final commit hashes, backup locations, validation results,
  qualified-cell counts per mode, remaining blockers and required future runs.
  Include the executable future N=3 manifest, preflight command, runtime estimates,
  prerequisite list and a separate readiness assessment for its actions.

The goal is complete when every issue repairable within the no-new-runs scope has
been addressed and validated, all relevant outputs/docs agree, and irrecoverable
or unproven cases have explicit actionable statuses. Completion does not require
all cells to be green, successful new runs, or a promise of publication acceptance.

## Initial effort estimate

The expanded five-mode scope is provisionally 24–40 hours of active work plus any
additional machine time required for backups and re-evaluation. This supersedes
the original VO-only 8–16 hour estimate. It is a planning estimate, not a deadline
promise; calibration provenance gaps or unexpectedly large artifacts may change
it. Give progress updates and continue until the defined scope is complete.

## Copyable goal prompt

Complete the benchmark repair for **VO, VO-LC, VIO, VIO-LC and GNSS-VIO**, following
`/data/imoroz/vslam-benchmark/docs/codex-goal.md`. Preserve existing progress with
verified commits and backups. Do not launch new estimator runs or add algorithms.

Audit every configuration, repair issues recoverable from existing artifacts,
re-evaluate saved trajectories, reconcile CSVs and reports, update documentation,
and safely archive obsolete material. Preserve all TODO matrix formats. Award
`N=3 ✅` only after documented scientific qualification; retain genuine failures,
actual repetition counts, distinct input variants and explicit rerun requirements.

Validate and commit the repairs. Report qualified results, unresolved blockers,
required future runs, backup locations and commit hashes. Continue until all work
possible within this scope is complete. Also prepare and validate an executable
future N=3 campaign across all five modes, retaining existing algorithm exclusions.
Fix safe per-run resumption, preserve previous attempts and evaluate each completed
repetition immediately. Separate reusable runs, required reruns, missing repetitions
and blocked cases, with prerequisites and runtime estimates. Distinguish repair/audit
completion from verified execution readiness; do not run a campaign or claim that
unresolved execution problems are fixed.
