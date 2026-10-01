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
and variant selection need repair: `GNSS_VARIANT` currently labels metadata while
the runners still consume `gps.csv`. A label alone does not establish which GNSS
measurements or covariances were used. The players support explicit CSV selection,
but that selection still needs wiring and validation in the runners.

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
| Required rerun | 6 | ORB ZED VO/VO-LC used 15 FPS with 10 Hz inputs; keep the previous cohort |
| Missing | 87 | No saved default attempt directory for that repetition |
| Blocked/review | 567 | Saved results or failed/partial attempts need the specified review/recovery |
| Reusable, qualified | 0 certified yet | Existing outcomes are being assessed; this does not mean all must be rerun |

All 660 actions are currently unverified for future execution. The six reruns and
87 missing repetitions retain prerequisites; their category is not permission to
start them. Review will move eligible saved observations into reusable status,
including genuine failures under a valid protocol. Invalid estimator settings
require a separate corrected cohort; failures must not be repeatedly sampled until
three successes remain.

The current runtime calculation covers **19 of the 93 missing/rerun actions**, with
a combined historical median estimate of about **36.1 hours**. The other 74 lack a
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
- Atomic state and global/cell locks protect controller use. Native/container cleanup
  semantics still need review; locks do not control unrelated manually launched jobs.
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
