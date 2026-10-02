# Protocol reporting validation — 2026-10-02

> Historical checkpoint. Later [ZED preparation](zed-preparation-20261002.md)
> supersedes its ZED calibration/reference blockers and current aggregate counts.
> Original observations, provenance hashes and non-ZED decisions remain preserved.

The reporting/audit continuation is complete. Existing results and implementation
identities are preserved. See [the protocol review](protocol-review-20261002.md)
for counts, claim scopes and unresolved prerequisites. This does not certify
remaining production actions: the manifest has **zero verified-ready actions**.

- **178 tests and three subtests passed** across campaign, evaluation and results
  suites. Guards cover failure denominators, sparse/partial exports, mixed versions,
  missing/interrupted attempts and separate unidentified legacy implementations.
- All **622 canonical evaluations** match checked staging/review metadata. Numerical
  digests of **11,319 preserved evaluation copies** are unchanged. All 45 previously
  clean-qualified cells remain the identical set.
- Original values in every pre-existing column of **684 CSV records** are unchanged:
  666 main rows and 18 historical AirSLAM rows. Protocol/outcome fields are additional.
- **3,471 original raw files** and **608 focused-campaign evidence files** retain
  their recorded hashes. All 24 focused attempt outcomes and numerical digests are
  unchanged; no production attempt was added during this continuation.
- All **232 reports**, tables and **19 figure artifacts** pass regeneration checks.
  Five TODO matrix layouts, columns and the user's current row ordering are preserved.
- The browser has **716 records**, **722 pages** and **17,548 checked local links**,
  with no broken links. Protocol/outcome fields agree with the CSVs and inventory.
- The future manifest validates, preserving 234 reusable observations, 73 confirmed
  setup reruns, 81 missing slots and 272 blocked actions. Three potential patched
  OpenVINS cohort additions are documented separately, not scheduled.
- AirSLAM geometry regression: current upstream passes 2/6 controls/cases, the patch
  passes 6/6. Two bounded saved-map diagnostic outcomes remain separate from production.
  Root-cause uncertainty and OpenVINS lifecycle review limits remain explicit.

Machine-readable checks: [reporting proof](campaigns/protocol-reporting-validation-20261002.json),
[diagnostic evidence](campaigns/protocol-diagnostics-20261002.json), and
[prepared contribution identities](upstream/prepared-contributions-20261002.json).
Detailed commands/logs are under `results/protocol-review-20261002/`.

Checkpoint: `cb014d5`. Pre-change incremental preservation:
`/data/imoroz/vslam-repair-backups/20261002T074823Z-protocol-before-repair`.
Final snapshot record: `/data/imoroz/vslam-repair-backups/20261002T081230Z-protocol-reporting-complete/summary.json`.
This supplements the complete focused-campaign snapshot and original raw backups;
its restoration instructions identify these dependencies. The root commit and both
prepared contribution branches are preserved as verified Git bundles. No push or
PR submission occurred. Unrelated nested changes and the colleague's review file
remain outside this repair commit.
