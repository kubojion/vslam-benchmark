# Future N=3 campaign preparation — in progress

The user extended the existing repair goal on 2026-10-01. Preserve completed work,
prepare the next campaign across VO, VO-LC, VIO, VIO-LC and GNSS-VIO, and retain the
DROID-SLAM, MASt3R-SLAM and MegaSaM exclusions. **No new estimator execution is
permitted during this work.** See [the detailed goal](../codex-goal.md).

## Scope and evidence

The future default scope has **220 cells × 3 repetitions = 660 logical repetitions**:
200 cells in the original four-mode campaign plus 20 GNSS-VIO cells. This changes
the future target of the earlier N=5 proposal; it does not claim that proposal was
completed. A logical repetition can retain an existing qualified observation or
require a fresh physical attempt under a corrected configuration cohort.

Six historical GNSS input-variant experiments remain separate from those default
cells. They are retained, evaluated and audited, not merged to obtain three default
repetitions or automatically expanded into new experiments. Their input provenance
and historical variant provenance need review. The repaired runners now require an
explicit `GNSS_CSV` for a non-default `GNSS_VARIANT`, copy the selected CSV into the
attempt, and record its hash, fallback covariance and status policy. Players consume
that preserved copy. A label alone still does not establish the physical source or
accuracy of historical GNSS measurements; missing run-time evidence is not recreated
from today's files.

Inventory: `results/repair-20261001/inventory.json`. This reconciles all 660 default
slots, plus 15 historical excluded artifacts, six GNSS variants and nine other
smoke/out-of-protocol attempts (seven have staged evaluations). Each record includes
saved config hashes, source metadata, numerical and execution outcomes, evaluation
input hashes and provenance blockers. Original trajectories are unchanged.

## Current draft manifest

`results/repair-20261001/future-n3-manifest.json` is a schema-2 executable action
manifest consumed by `scripts/campaign/run_future_manifest.py`. It is deliberately
**in progress**, not a final campaign release or a claim of readiness.

Current classification before qualification decisions are complete:

| Category | Logical repetitions | Meaning |
|---|---:|---|
| Required rerun | 30 | Six ORB ZED FPS cases, 18 AirSLAM EuRoC inertial rectification cases and six ORB Horti VIO-LC rectification cases; preserve previous cohorts |
| Missing | 87 | No saved default attempt directory for that repetition |
| Blocked/review | 543 | Saved results or failed/partial attempts need the specified review/recovery |
| Reusable, qualified | 0 certified yet | Existing outcomes are being assessed; this does not mean all must be rerun |

All 660 actions are currently unverified for future execution. The 30 reruns and
87 missing repetitions retain prerequisites; their category is not permission to
start them. Review will move eligible saved observations into reusable status,
including genuine failures under a valid protocol. Invalid estimator settings
require a separate corrected cohort; failures must not be repeatedly sampled until
three successes remain.

The current runtime calculation covers **25 of the 117 missing/rerun actions**, with
a combined historical median estimate of about **37.2 hours**. The other 92 lack a
comparable complete same-cell run on this server. **This is not a total campaign
estimate.** It excludes unresolved blocked actions, validation diagnostics and
re-evaluation overhead. Each action records the source runs, observed range, pacing
mode and uncertainty. Old-machine GNSS times and early failures are not treated as
full server-runtime estimates. Execution is serialized because estimators share
containers, CPU/GPU resources and some native output locations.

## Read-only validation and regeneration

These commands do not invoke estimators:

```bash
python scripts/campaign/build_repair_inventory.py
python scripts/campaign/build_future_manifest.py
python scripts/campaign/run_future_manifest.py results/repair-20261001/future-n3-manifest.json
```

`--require-ready` additionally fails if selected actions have unmet prerequisites or
unverified readiness. A successful ordinary validation means that the manifest is
well formed and its inventory/pipeline hashes match. It does not mean actions are
ready. Regenerate after reviewed code, configuration or evidence changes.

The future execution interface is the same manifest command with `--run`, optionally
selecting exact action IDs using repeated `--action` arguments. Do not invoke it
during this repair. It refuses blocked or unverified selections before any estimator
starts and checks the original evidence hashes. Changes to a campaign manifest after
execution begins require an explicit new campaign revision, preserving old state.

## Attempt lifecycle

- `run_repetitions.py` keeps physical attempt IDs separate from logical repetition
  numbers and cohorts. The manifest allocates unused IDs above 10000 for new attempts,
  preserving existing `run1`, `run2`, `run3`, variants, smoke outputs and logs.
- Every completed repetition is evaluated immediately, including a recoverable saved
  trajectory after nonzero estimator exit. Original process evidence is retained.
- Existing directories are never deleted or estimated again in place. Partial and
  interrupted attempts remain visible. Recovery retries evaluation, not estimation.
- Atomic state and global/cell locks protect controller use. Eight ROS wrappers now
  use attempt-owned cleanup and private transport; see the [runner audit](../runner-isolation-audit.md).
  Native/container startup and shutdown still require execution validation; controller
  locks do not control unrelated manually launched jobs.
- `_evaluate_run.py` uses schema 3, checks input/evaluator hashes and saves independent
  content-addressed copies of earlier evaluation JSONs before replacing them.
  It does not create historical COMPLETE markers or scientific qualification ticks.
- No report aggregation is allowed to infer success from one successful attempt in
  a mixed cell. Report/site integration with the authoritative inventory is ongoing.

## Completion and readiness are distinct

**Repair/audit complete** means all repairs possible without estimation are validated,
results and documentation agree, cleanup is safe, and the final manifest identifies
remaining prerequisites. This status has **not** been reached yet.

**Verified ready to run** is an action-specific claim supported by configuration,
input, static and required execution evidence. It is not established by syntax
checks, successful manifest generation, or a saved valid trajectory alone. Native
ORB crashes, ZED inertial calibration uncertainty, AirSLAM rectification/keyframe
semantics, GNSS provenance and remaining reference transforms stay explicit until
resolved. No execution problem is claimed fixed solely because the wrapper changed.

The manifest now carries each saved attempt's qualification and specific unresolved
reference/frame, sparse-export, final-BA and failure prerequisites, including
dataset prerequisites for missing attempts. A corrected AirSLAM cohort is no longer
incorrectly described as an FPS-15 cohort. All original invalid-config cohorts must
be preserved. The current 30 reruns, 87 missing repetitions and 543 blocked/review
cases include the six newly confirmed ORB Horti VIO-LC cases; 0 actions are certified ready.

Execution uses the recorded runner-default recipe. The preflight rejects nonempty
inherited configuration, playback, GNSS input/covariance, seed and numerical-runtime
overrides listed in `environment_policy`; it does not silently discard them. Such
changes require a separately reviewed recipe. DPVO's planned seed is explicit and
deterministically derived from its fresh physical attempt ID. Runtime estimates
remain historical planning estimates: about 37.2 serialized hours for the 25 actions
with comparable timing, with 92 of the 117 rerun/missing actions unestimated. This
is not an estimate for the entire remaining campaign.

The repetition controller now requires measurement schema 2 for new attempts.
Uninstrumented processing counts/FPS stay unknown; available-input/wall-time ratios
are nominal. See [measurement semantics](../run-measurements.md). Historical saved
metadata and processing claims remain preserved as evidence.

Current validation: 126 tests plus three subtests pass. Manifest structure and
evidence hashes validate for all 660 actions; `--require-ready` correctly refuses
all 660 because readiness prerequisites remain unresolved. The staged browser has
690 entries/696 pages, with 8,174 checked local links and no broken link or legacy
image preview. Evidence is under `results/repair-20261001/` in
`future-manifest-validation.json` and `browser-validation.json`. This does not
complete the outstanding scientific qualification, root-output promotion or cleanup.

The [AirSLAM source audit](../airslam-rectification-audit.md) establishes that the
recorded EuRoC fusion configuration mixes rectified visual axes with raw-camera
IMU extrinsics. A source patch is prepared and its transform algebra checked;
application, build and execution validation remain prerequisites. Eighteen existing
VIO/VIO-LC repetitions require a corrected cohort. Historical executable hashes
were not captured, so exact loaded-binary attribution remains limited. Future
AirSLAM map-refinement retries are disabled and partial stage artifacts are retained;
the previous up-to-three-stage-attempt policy remains in historical metadata.

## GNSS input repair validation

All five GNSS wrappers now preserve the selected input, including the default
`gps.csv`, before execution. Non-default labels require `GNSS_CSV=<explicit file>`;
relative paths are resolved against the repository. Covariance fallbacks remain
`GPS_COV_XY=1.0` and `GPS_COV_Z=4.0` in square metres unless explicitly supplied.
`GPS_STATUS=0` is the fallback only when the CSV lacks a status. CSV status 0 is
preserved; status -1 fixes are excluded. Invalid order, non-finite positions and
negative variances are rejected rather than silently sorted/skipped.

OKVIS2-X generates a new native GPS CSV in a private per-attempt input view. It
links the existing camera/IMU directories and never mutates or trusts the shared
`mav0/gps0/data_raw.csv` merely because that file exists. Horizontal covariance is
converted to the isotropic standard deviation its reader requires; vertical
variance is square-rooted independently. The converter refuses replacement.

The four current source files pass read-only validation (4,703/3,982 Rosario fixes;
7,620/1,939 Horti fixes). Their existing native caches have identical position and
standard-deviation values to fresh conversion. Timestamp differences are at most
232 ns from previous floating-point conversion. Thus this audit found no current
cache position mismatch; the repair prevents future stale-input reuse. It does not
prove which bytes legacy runs actually consumed. Evidence is recorded in
`results/repair-20261001/gnss-input-validation.json`.

Ninety tests plus three subtests pass, including variant/file binding, immutable
input copies, zero-status handling, covariance units, invalid inputs, no-fix
filtering and container-path mapping. Shell syntax and Python compilation pass.
No ROS estimator or GNSS campaign was run; fusion, native crashes, reference frames
and process isolation remain separate readiness checks.
