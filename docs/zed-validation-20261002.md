# ZED repair validation and preservation — 2026-10-02

**Repair/audit complete; execution readiness is conditional.** Fifteen applicable
algorithm/mode paths passed fixed 60-second checks. Voxel's shutdown and failure
capture are repaired, but initialization and successful export remain unverified.
No ZED production repetitions, full campaign, new algorithm or push were performed.
Original algorithm failures, historical cohorts and provenance hashes remain intact.

The [preparation report](zed-preparation-20261002.md) records calibration/reference
semantics and limitations. The [campaign plan](zed-campaign-20261002.md) lists all
remaining actions and cost estimates. TODO retains all five existing matrices and
row/column order. Protocol N=3 ticks count three verified attempts, including
properly recorded failures; they are not promises of three successful trajectories.

## Verification

- **198 tests and seven subtests passed**, including coordinate inversion/stereo
  geometry, approved-gap support, causal-prefix recovery, diagnostic parent identity,
  native exit handling, resumption, qualification and manifest guards.
- All eight applicable calibration files verify against the recovered transform.
  Parser-level comparison preserves July image calibration and non-extrinsic settings.
- Independent source verification matches 23,160 GPS messages, 23,160 PVT messages
  and 23,156 dual-antenna messages to the original robot bag. The exact approved
  15 intervals / 448 exclusions reproduce from hash-verified raw input and code.
- **639 saved trajectories evaluated without staging errors**, then promoted with
  original evaluations retained by hash. This includes diagnostics and historical
  exports outside the paper selection. All **576 non-ZED numerical evaluations**
  remain unchanged. Twenty-seven COMPLETE-marker observations refresh from false
  to true because their earlier evaluation preceded marker creation; their other
  execution fields remain unchanged. The new export-stage label is metadata only.
- All **47 production ZED exports** agree exactly with their primary sensitivity
  results. The first 46 have 828 scenario results; the recovered OKVIS2-X prefix
  adds 18. The combined CSV has 846 rows. Clock offset stays zero, RTK float remains
  included in the primary, and excluded gaps remain unsupported.
- Reconciled default counts: **551/600** selected four-mode evaluations; **20/60**
  GNSS default evaluations; six legacy GNSS variants remain separate. The root
  CSVs have 666 comparison rows plus 18 historical-cohort rows. Diagnostics never
  fill production slots. There are **81 protocol-verified N=3 cells**, **256 verified
  attempts**, and **41 verified failure observations**; the original 45 clean-qualified
  cells remain unchanged. The ZED review yields 31 individually verified
  observations across the dataset, including seven failures; 27 belong to the nine
  complete N=3 cohorts, and four remain individually qualified outside them.
- Inventory, explicit acceptance ledger, run evaluations, aggregates, CSVs, tables,
  figures, browser and TODO are reconciled. Generation checks reproduce current
  aggregates, tables, claim summaries and figure data. The browser exposes reference
  version and causal-export stage and includes the selected corrected EuRoC cohort
  in its default view.
- The all-mode manifest retains **261 reusable / 84 setup reruns / 81 missing /
  234 blocked** slot dispositions. The alternative coherent ZED plan retains 27
  observations and prepares **17 setup replacements / 25 missing / six cohort
  completions**. Forty-five new attempts have bounded native-path readiness; Voxel's
  three remain blocked. Historical-cost proxies cover 39 attempts (70.7 hours);
  nine lack a defensible estimate. No whole-campaign duration is asserted.

Strict read-only preflight passes for all 45 ready ZED actions with current sensor,
source and runtime verification. Voxel is correctly rejected by `--require-ready`;
no estimator is launched. Original run-evidence checks verify 2,899 file hashes,
and all 603 non-ZED claim decisions are unchanged. The legacy reference SHA256
remains `d5c25dce4641dadd24b0270519e2c2516301550e59c0c0180327befdea0f295f`.

Detailed check outputs are under `results/zed-preparation-20261002/`, including
`final-numerical-validation.json`, `final-all-tests.log`, the final short-check
states, source validation, sensitivity and manifest preflight records. New native
builds are isolated; original nested source checkouts and executable paths remain
preserved. The non-ZED ORB default still needs separate ABI/shutdown validation.
Historical OKVIS2 interruption and OKVIS2-X exit 141 remain unexplained.

## Preservation and restoration

Local checkpoints `f59854e`, `055e7e7` and `2efd79f` preserve the supplied geometry,
calibration/reference construction and isolated native repairs. The final reporting
commit is recorded in the backup's Git bundle and final checkpoint receipt.

The final independent snapshot is
`/data/imoroz/vslam-repair-backups/20261002-zed-preparation-complete`.
Its `files.json`, `symlinks.json`, `summary.json` and `RESTORE.md` define the exact
verified coverage and restoration procedure. It preserves the complete ZED result
trees, new reference construction arrays, diagnostic inputs, isolated ORB build,
Voxel container workspace, evaluation history, current reports and capture records.
It extends the earlier complete protocol-reporting and raw-result backup chain;
it does not claim to duplicate the external source bags or camera images.

The July source records under `/data/imoroz/vslam-source-records/zed2i-20260703`
remain read-only external evidence. Original `gt_tum.txt` is unchanged. The new
reference is immutable and selected by hash. The only added historical production
trajectory is the explicitly labelled OKVIS2-X causal conversion; original native
CSV, metadata, logs and completion state are preserved.

The authorship rewrite mapping remains `docs/campaigns/git-author-rewrite-20261001.json`;
historical provenance hashes were not rewritten. The obsolete temporary pause
remains revoked. No production execution or push is authorized by this handoff.
