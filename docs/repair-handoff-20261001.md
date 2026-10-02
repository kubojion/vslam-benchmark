# Five-mode repair handoff — 2026-10-01

> Historical checkpoint. Later [ZED preparation](zed-preparation-20261002.md)
> supersedes its ZED calibration/reference blockers and current aggregate counts.
> Original observations, provenance hashes and non-ZED decisions remain preserved.

> Historical checkpoint. Current focused EuRoC execution, counts and remaining limitations are in
> [the campaign record](euroc-focused-campaign-20261001.md) and [current handoff](acceptance-handoff-20261001.md).

> Historical repair-completion checkpoint. The subsequent [acceptance handoff](acceptance-handoff-20261001.md)
> supersedes its blanket qualification counts. The later [matched-session review](reference-review-20261001.md)
> additionally corrects Rosario metrics; this document remains the historical checkpoint.

**Repair/audit complete within the no-new-estimation scope. No action is certified
ready to execute, and no cell has a publication-qualified N=3 green tick.** These
are separate conclusions. The retained numerical results remain useful provisional
evidence; missing provenance is not a blanket instruction to rerun everything.

## Delivered results

All 593 saved-artifact evaluations are reconciled and published in their ordinary
result directories, with previous JSONs archived. The original four-mode campaign
now has 545 evaluated repetitions, including seven recovered trajectories. GNSS
contributes 20 default and six separate variant evaluations; historical excluded
and smoke artifacts remain outside headline comparisons. Five original-campaign
scale collapses and the invalid GNSS full-pose export remain visible.

| Mode | Default evaluations | Cells with three evaluations | Qualified green cells | Confirmed reruns | Missing repetitions | Blocked/review actions |
|---|---:|---:|---:|---:|---:|---:|
| VO | 183 / 192 | 61 | 0 | 3 | 6 | 183 |
| VO-LC | 136 / 144 | 45 | 0 | 3 | 5 | 136 |
| VIO | 139 / 168 | 42 | 0 | 9 | 28 | 131 |
| VIO-LC | 87 / 96 | 28 | 0 | 15 | 8 | 73 |
| GNSS-VIO | 20 / 60 | 0 | 0 | 0 | 40 | 20 |
| Total | 565 / 660 | 176 | 0 | 30 | 87 | 543 |

The last three columns partition the 660 future default logical repetitions. They
are not additional runs already performed. The six GNSS variants stay separate;
DROID-SLAM, MASt3R-SLAM and MegaSaM exclusions are retained.

The five root CSVs contain 666 planned/variant rows, including missing/failure rows.
There are 226 cell/variant reports, current tables and figures, and 690 browser
records. TODO preserves its five matrices and task-table layouts. Historical
reports/configs/metrics/logs are retained; obsolete generated material and former
storage/running guides are explicitly archived.

## Confirmed estimator-side reruns

These cannot be repaired through evaluation alone:

- ORB-SLAM3 ZED VO and VO-LC, three repetitions each: 15 FPS configuration for 10 Hz
  input. Future settings are corrected.
- AirSLAM EuRoC MH01/MH03/MH05 VIO and VIO-LC, three repetitions each: raw IMU-camera
  extrinsics used with internally rectified visual axes. A source patch and numerical
  transform check are prepared. Application, build and native validation are pending.
- ORB-SLAM3 Horti strawberry02/03 VIO-LC, three repetitions each: raw-camera IMU
  rotation with rectified images. Future settings are corrected.

The original cohorts remain intact. Genuine failures are not selectively replaced
until three successes are obtained.

## Remaining prerequisites outside this repair

| Evidence needed | Consequence / next authorized step |
|---|---|
| Historical dirty runner/nested-source bytes and build linkage | Recover from original machines, archives or build records where possible. Current source snapshots cannot certify old runs. Decide claim eligibility before requesting additional estimation. |
| Horti reference-to-camera chain; Rosario rectification/reference chain; ZED serial-specific IMU rotation/time offset and reference lever-arm/altitude assumptions | Obtain original calibration/extraction evidence. Restrict claims until verified; do not hide physical origin errors with trajectory alignment. |
| Historical GNSS source, covariance, antenna frame, fusion output and reference independence | Preserve default/variant cohorts and shape-vs-global-accuracy distinctions. Current GNSS input copies do not retroactively establish old provenance. |
| Rig-specific thresholds, initialization/online calibration and final BA policy | Freeze and disclose the protocol using the saved-parameter review; avoid ranking tuned profiles as identical algorithm defaults. |
| AirSLAM sparse export semantics and uninstrumented processing counts | Use explicitly sparse accuracy claims; do not infer dense tracking coverage, processing FPS or real-time deadlines from pose counts/wall time. |
| ORB startup/shutdown failures and other failed attempts | Retain exact exits/logs. Native diagnosis requires separately authorized estimator execution; wrapper repairs are not proof that the underlying crashes are fixed. |
| Native config loading, source-to-binary linkage, library/Python/ROS resolution, repaired lifecycle and AirSLAM patch validation | Review current asset/source identities, establish build evidence, then perform a separately authorized diagnostic validation before marking any action execution-ready. |

The [qualification review](publication-qualification-20261001.md),
[saved-parameter review](saved-parameter-review-20261001.md),
[runner audit](runner-isolation-audit.md) and
[repair audit](repair-audit-20261001.md) retain the detailed evidence.

## Executable future plan

`results/repair-20261001/future-n3-manifest.json` contains all 660 actions, evidence
links, selected configuration recipes, input/source/runtime identities, prerequisites,
cohorts, unused physical IDs, and per-action timing evidence. The known serialized
runtime subtotal is **37.2 hours for 25 of the 117 missing/rerun actions**. The other
92 are unknown. This excludes blocked cases, readiness diagnostics, capture and
evaluation overhead; it is not a total-campaign estimate.

Read-only preflight:

```bash
python3 scripts/campaign/run_future_manifest.py results/repair-20261001/future-n3-manifest.json --check-inputs --check-implementations
```

Add `--require-ready` to check readiness; it currently refuses all 660 actions.
The inherited `LD_LIBRARY_PATH` in the current shell is also an unreviewed launch
override. Select and record an appropriate environment before future execution.
The execution interface adds `--run` and optional repeated `--action <exact-id>`;
execution remains unauthorized in this repair. Blocked/unverified actions are
rejected before an estimator starts.

After a reviewed change, commit the code, then preserve/refresh the identities and
rebuild the plan. `build_execution_assets.py --refresh` archives outdated manifests.
Use `--audit-status repair_audit_complete` on inventory/plan builders only when the
changed scope has been rechecked; their ordinary default remains `in_progress`.
No prior physical attempt is overwritten. Recovery evaluates saved output, and each
new completed repetition is evaluated before the next repetition starts.

## Validation and preservation

The final suite has 149 passing tests plus three passing subtests. Tests cover
numerical transforms/metrics, failures/cohorts, safe resume/interruption, owned
synthetic process cleanup, configuration selection, GNSS inputs, exact source
archives, data changes and known runtime assets. No estimator was run. Independent
numerical checks already cover all five modes; the final qualification clarification
changes no numerical fields in any of the 593 evaluations. Regeneration and browser
link checks, original-evidence hash checks, and input/source/asset preflight results
are recorded under `results/repair-20261001/`.

Original verified preservation:
`/data/imoroz/vslam-repair-backups/20261001T102654Z-vo-pre-repair/`.
It contains all five original result trees, logs, Git bundle, nested changes,
checksums and `RESTORE.md`. Later staging backups preserve intermediate evaluator
states. The final repair backup is recorded in
`results/repair-20261001/final-backup.json`; it supplements the original backup with
repaired derived artifacts, exact source blobs and current repository history.
Large immutable dataset inputs are identified by hashes, not duplicated.

Key local commits: `38e0bf3` published reconciled outputs; `66ba9f4` pinned configuration
recipes and corrected the DPVO LC prerequisite; `34007d9` added exact source/input/runtime
capture and the OpenVINS provenance clarification. Subsequent handoff commits record
this document and final validation. Re-read Git status/history before any later
commit. Collaborator changes in nested repositories remain untouched. Nothing was
pushed by the repair agent.

Historical provenance hashes remain historical after the authorized author rewrite;
use [the mapping](campaigns/git-author-rewrite-20261001.json). The temporary maintenance
pause was explicitly revoked and was not reapplied. The goal ends because its
no-new-estimation repair scope is complete, not because it is paused or because
publication qualification has been achieved.
