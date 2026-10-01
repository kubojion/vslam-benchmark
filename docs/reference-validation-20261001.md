# Matched-session review validation — 2026-10-01

> Historical checkpoint. Current focused EuRoC execution, counts and remaining limitations are in
> [the campaign record](euroc-focused-campaign-20261001.md) and [current handoff](acceptance-handoff-20261001.md).

This extends the [previous acceptance checkpoint](acceptance-validation-20261001.md).
The [reference review](reference-review-20261001.md) explains the scientific findings;
the [current handoff](acceptance-handoff-20261001.md) lists exact remaining actions.
Audit completion does not certify repaired native execution.

- **161 tests and three subtests pass.** The new checks cover independent Rosario
  physical versus virtual-body conversion, fail-closed saved-config/source/native-log
  findings, antenna-chain composition and rejection of runtime samples with confirmed
  invalid configurations. No estimator is invoked by these tests.
- All **593 saved evaluations** are refreshed and their previous JSONs independently
  archived. **159 Rosario evaluations** change frame-dependent metrics; all **434
  other evaluations** retain numerical fields exactly. No observed numerical outcome
  status changes. The 147 accepted and 54 limited EuRoC repetitions are preserved.
- **3,471 original non-evaluation evidence files** remain hash-identical to the
  original inventory. Trajectories, native logs, metadata, saved effective configs
  and historical provenance hashes are unchanged. No historical attempt is overwritten.
- The **666 CSV rows**, 220 default cell decisions, 226 default/variant summaries,
  generated tables/figures and five TODO matrices reconcile. Matrix rows, columns
  and order are preserved. Reports retain every failure and missing repetition.
- The browser retains **690 records, 696 HTML pages and 12,918 checked local
  links**, with no broken links or historical plot previews. All 226 reports,
  tables and 19 figure/data outputs pass read-only regeneration checks.
- The future manifest has **210 reusable observations, 91 required reruns, 87 missing
  repetitions and 272 blocked cases**. No new green cell is granted; the existing
  **45 clean N=3 EuRoC cells** remain. There are zero verified-ready estimator actions.
- Runtime preparation uses complete comparable server samples and rejects native
  errors and confirmed invalid configurations. Only **11 of 178** required/missing
  actions have a defensible historical estimate, totalling **24.1 serialized hours**;
  167 have no comparable estimate. This excludes diagnostics, blocked actions and
  evaluation overhead, and is not a total campaign duration.
- Original ZED source bags remain read-only outside the repository. Their provided
  checksums, all matching saved GPS rows and all 23,105 cross-recorder GPS payloads
  are independently verified. The owner's later README/clock-note clarification is
  recorded with its new hashes and earlier document identity retained. The complete
  benchmark evaluator reproduces the five requested clock-sensitivity examples;
  zero-offset published metrics match. No clock is fitted or applied. Clock
  uncertainty is disclosed, not a blocker; physical 3D/quality and serial IMU
  calibration requirements remain separate.

Reproducible checks and evidence are in `results/reference-review-20261001/`:
`numerical-comparison.json`, `validation.json`, `validate_outputs.py`, `tests.log`,
`zed-source-verification.json` and `zed-clock-example-reproduction.json`.
The source index and acceptance ledger pin the evidence used for decisions. Original
external ZED files are referenced by absolute path/checksum, never copied into the
repository; their hashes are checked separately from the repository-output guards.

The pre-promotion snapshot is
`/data/imoroz/vslam-repair-backups/20261001T200909Z-reference-before-promotion/`:
1,583 independently verified files (79,062,115 bytes), working-tree patch and a Git
bundle at `e0ee49be0e536fc89c266b40d64e15c9d57cd0c9`. The previous raw and acceptance
backups remain intact. Final evidence backup and current source/input/runtime
refresh records are saved beside the validation artifact after the local commit.
The authorized authorship mapping is preserved. No estimator, tuning, history
rewrite or push occurred. The obsolete temporary pause remains revoked.
