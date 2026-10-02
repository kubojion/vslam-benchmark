# Rosario/TODO integration into main — 2026-10-02

**Files are integrated into `/data/imoroz/vslam-benchmark` on main. Rosario
execution readiness remains unverified.** The review checkout was reused; no new
checkout, estimator run or push was made. Candidate profiles remain inactive.
Source integration is committed locally as `03c7c0e`. The
[final preservation and validation receipt](../results/rosario-main-integration-20261002/final-validation.json)
records the completed evidence refresh. Generated reports and final handoff updates
remain working-tree documentation, preserved in the final snapshot below; the
source commit stays fixed because current implementation captures pin it exactly.

## What was integrated

The committed review change `18dc9d9` and its uncommitted refinements were reviewed
together. Thirty-eight individually hash-checked code/config/test/evidence files
were merged, including the acceptance-test change and five upstream-evidence files
that the earlier standalone patch omitted. The existing main goal was extended,
not replaced. Newer main notes and colleagues' unrelated files were preserved.

- Four candidate bundles: `configs/candidates/rosario-vio-20261002/`.
- Preparation and verification: `scripts/campaign/prepare_rosario_vio_candidates.py`
  and `scripts/campaign/validate_rosario_vio_candidates.py`.
- TODO generator and formatting/acceptance tests, with counts and valid failures
  preserved. Candidate notes now name main as their location.
- The validator's pinned Basalt source evidence under
  `review-evidence/rosario-vio-20261002/upstream/`.
- Receipt-backed selection of completed ZED first attempts, and planner checks
  preventing those logical slots from being scheduled again while review is pending.

See [candidate configurations and author questions](rosario-vio-candidates-20261002.md),
[main candidate validation](rosario-main-candidate-validation-20261002.json), and
[the source/integration inventory](rosario-main-integration-20261002.json).

## ZED state and preservation

The controller PID 1519727 was deliberately stopped by the separate batch operator;
its original `status.json` still says running and is retained as historical evidence.
`pause-after-current.json` documents that intervention. The ORB-SLAM3, OKVIS2 and
OKVIS2-X run10001 wrappers, native estimators, evaluation and capture processes
subsequently finished. Their final attempt states are `evaluated`, with native exit
0. The AirSLAM, OpenVINS and Voxel first actions were never started by that batch.
No batch was restarted or stopped by this integration.

The three completed attempts retain their blocked claim-review status; completion
is not publication qualification. Their first logical slots have no new estimator
command. The original run1 histories are preserved separately, including their
failures and missing exports. Only these three selected cells changed; the other
217 cells and all 85 pre-existing additional artifacts are unchanged. The total of
81 verified N=3 cells remains unchanged. The four-mode selected evaluation count
is now 552/600; raw historical trajectories, metadata, evaluations and hashes remain
unchanged. CSVs, tables and figures are reconciled from saved results, not reruns.

The executed manifest is preserved at
`results/rosario-main-integration-20261002/executed-zed-manifest.json`; final receipt
selection is `configs/campaigns/zed-vio-first-attempts-20261002.json`. Refreshed future
plans are distinct from that executed snapshot. The ZED future plan uses a new
campaign identity so the stopped controller's state cannot be silently reused.

Before changes, **5,166 files** were copied and verified in
`/data/imoroz/vslam-repair-backups/20261002T155907Z-rosario-main-before-integration`.
Final attempt-state files were also copied and checked. Checkpoint `558b8fd` preserves
the main documentation before integration. The initial handoff and source hashes
remain in that backup/checkpoint and the integration inventory. Historical provenance
identifiers were not rewritten.

## Validation and remaining prerequisites

**89 focused tests pass in main**: candidate parsing/geometry/timing and isolation;
TODO formatting and failure counts; acceptance/protocol behavior; completed-slot
selection including failed outcomes and stale receipts; configuration recipes;
and exact source capture. No test invokes a real estimator. Main data validation
retains the original 14 Rosario replacements, four missing OpenVINS repetitions
and 30 adjacent camera-review-only histories.

After the integration source commit, **14 implementation captures were refreshed**;
eight dataset identities and 14 runtime identities were verified against current
files. Both campaign preflights passed with `--check-inputs --check-implementations`
and `estimation_started: false`: all 660 five-mode slots and all 75 coherent ZED
slots. Readiness rejection checks still reject an unverified Rosario candidate
and a completed ZED slot awaiting review, while accepting a previously checked
ZED second repetition. These checks do not establish new native readiness.

The coherent ZED plan retains 27 qualified observations, holds three completed
first attempts for explicit claim/cohort review, and names **45 remaining new
attempts**: 14 replacements, 25 missing repetitions and six cohort-completion
attempts. Of those 45, 42 retain previously verified bounded readiness; three
Voxel attempts remain unready. The known historical timing proxy subtotal is
68.12 hours for 37 attempts; eight have no estimate. This is not a total runtime
prediction. The coherent plan replaces the ZED selection in the five-mode plan;
the two plans must not be added together or both executed.

The final read-only preservation check verified **5,107 historical evidence files**
and 62 completed-attempt/executed-plan evidence records without changes. All 252
matrix cells retain A/E/S/F counts, all five layouts are preserved, and TODO/details
match their generator. The CSV/table/figure checks passed; the browser contains
748 selected, historical and diagnostic entries. Saved automatic blocker lists
remain intact; integration neither qualifies those results nor turns them into
new setup defects.

Rosario still needs author confirmation of the matching projection/baseline and
published calibration bundle, selection of the intended profile before execution,
Basalt parser/offset-consumption validation, Voxel timing/export/shutdown checks,
and OpenVINS native image/time/frame checks. The calibrated candidates are prepared;
default runners continue to select their existing configurations. No Rosario
experiment is authorized. Red Rosario rerun/readiness markers remain red; no
static test or integration step turns them into verified-ready markers.

Final reporting and evidence snapshot:
`/data/imoroz/vslam-repair-backups/20261002T163421Z-rosario-main-final`.
Its `snapshot.json` and `VERIFIED` record the exact final files independently of
the source commit. Integration/audit work is complete; native Rosario readiness
and the outstanding ZED claim review are explicitly unfinished.
