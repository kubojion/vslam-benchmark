# Documentation index (reviewed 2026-10-09)

This page says which documents are current, which are frozen evidence, and which are history. Several older documents contain statements that later decisions superseded. Read the [errata](#errata) before quoting any of them.

## Start here

| need | read |
|---|---|
| What is left to run, per cell | [TODO matrices](../TODO.md), [per-cell details](todo-status-details.md), [acceptance hand-off](acceptance-handoff-20261001.md). All three are generated; never edit them by hand. |
| Current numbers | [generated tables](generated/tables.md), [verified claims](generated/verified-claims.md), [figures](generated/README.md). The root `benchmark-*.csv` files have one row per planned repetition; filter on `attempt_exists`. |
| Where results live, what the folders and run numbers mean | [results layout](results-layout.md) |
| Current IMU-noise policy | [IMU-noise policy](imu-noise-policy.md) |
| How a claim becomes "accepted" | [paper acceptance criteria](paper-acceptance-20261001.md), [protocol tick definitions](protocol-review-20261002.md) |

## Current policies (one line each)

| topic | policy | record |
|---|---|---|
| IMU noise | Rule C (dataset Allan × each estimator's authors' EuRoC ratio) on EuRoC, HortiMulti, Rosario v2 and CitrusFarm. ZED2i keeps the recording envelope and is reported separately. Envelope results are a labelled sensitivity condition only. | [benchmark-decisions-20261006 §1](benchmark-decisions-20261006.md), [imu-noise-rule-20261005](imu-noise-rule-20261005.md) |
| Rosario v2 geometry | "Option A": the complete published Kalibr camera–IMU bundle as rectified input (K' 648.862/645.011/348.243, baseline 0.050240890825 m), IMU shifted −4,098,308 ns, native offset 0 | [benchmark-decisions §2](benchmark-decisions-20261006.md), [rosario-citrus-preparation-20261006](rosario-citrus-preparation-20261006.md) |
| HortiMulti | Camera-clock IMU input (9.16 ms applied once at preparation, every native offset 0); OpenVINS 31 Hz; reference accepted as evaluated | [hortimulti-decisions-20261005](hortimulti-decisions-20261005.md), [benchmark-decisions §3](benchmark-decisions-20261006.md) |
| CitrusFarm | seq04 + seq07, MicroStrain IMU re-stamped on sample index with per-sequence offsets; Rule C noise | [benchmark-decisions §1](benchmark-decisions-20261006.md), `campaigns/citrusfarm-*.json` |
| ZED2i | v2 GNSS-position reference, nominal 3D position claims only | [zed-preparation-20261002](zed-preparation-20261002.md) |
| Failures | Reviewed algorithm-side failures (crash, divergence, collapse) are observed outcomes and are kept; "✅ N=3 ❗" marks a cell whose N=3 includes one | [benchmark-decisions-20261006](benchmark-decisions-20261006.md) |
| Algorithms | 4 new: cuVSLAM, SVO Pro, MASt3R-Fusion, DSOL. Excluded: DROID-SLAM (replaced by DPVO), MegaSaM, MASt3R-SLAM. | [claude-new-algorithms-20261002](claude-new-algorithms-20261002.md), `configs/campaigns/quality-final.json` |

## Frozen files: do not edit or move

The pipeline records these files by path and SHA-256: the inventory, future manifest, acceptance ledger, readiness reviews and ZED reference. Editing or moving one turns accepted cells into `reviewed_evidence_changed`, or makes the inventory or manifest rebuild fail.

To supersede a frozen document:
1. Write a new dated record.
2. Refresh the readiness entries and the ledger.
3. Add a line to the errata below.

**Frozen as of 2026-10-09 (hash recorded):**
- **Decision and review records:**
  - `benchmark-decisions-20261006.md`, `imu-noise-rule-20261005.md`, `hortimulti-decisions-20261005.md`
  - `rosario-citrus-preparation-20261006.md`, `rerun-plan-20261003.md`, `okvis-imu-noise-derivation.md`
  - `claude-new-algorithms-setup-20261003.md`, `zed-preparation-20261002.md`, `reference-review-20261001.md`
  - `protocol-review-20261002.md`, `publication-qualification-20261001.md`, `paper-acceptance-20261001.md`
- **Geometry evidence:** `CAMERA_ANTENNA_GEOMETRY_20261002.txt`.
- **Patches:** `upstream/{airslam-review,open_vins-review,orb-slam3-wait-for-workers,voxel-svio-subscriber-lifetime}.patch`.
- **30 files in `campaigns/`:**
  - `paper-acceptance-20261001.json` (the living ledger, rewritten only by its tools)
  - `user-rerun-decisions-*.json`
  - `citrusfarm-*`, `zed-*` (except `zed-readiness-review`), `gnss-lever-*`, `horti-time-offset-findings`
  - `reference-sources`, `rosario-reference-calibration`, `rerun-findings`, `orb-zed-g2o-build`
  - `voxel-zed-shutdown-build`, `voxel-parameter-audit-build-20261002{,-v3}`
  - `euroc-focused-validation`
  - the `*-review-2026100x.json` evidence reviews (completed-zed-first, export-completion, log-observation, native-check, orb-historical-exposure, zed-vio-n3)

**Not hashed but named by code or records: keep the path, content may be edited.**
- `airslam-rectification-audit.md`, `repair-audit-20261001.md` and `saved-parameter-review-20261001.md` (protocol findings).
- `author-quality-config-audit.md` and `execution-readiness-20261002.md` (rerun-findings evidence).
- `rosario-main-integration-20261002.md` (TODO generator).
- `rosario-vio-candidates-20261002.md` and `rosario-vio-candidate-validation-20261002.json` (candidate configs).
- `zed2i-imu-extrinsics.md` and `setup.md` (comments in pinned configs and scripts).
- `campaigns/production-review-*.json` (ledger `review_document`).
- `campaigns/basalt-native-profile-20261002.json` (Basalt runner).

**Generated: regenerate, never edit.**
- `../TODO.md` (matrices and marker blocks), `todo-status-details.md`, `acceptance-handoff-20261001.md`, `zed-campaign-20261002.md` and `generated/*`.
- The readiness reviews `campaigns/readiness-review-2026*.json` and `campaigns/zed-readiness-review-20261002.json`. They are written by the campaign tools.

Never add another file matching `campaigns/readiness-review-2026*.json`: `build_future_manifest.py` reads that glob.

## Decision log

| date | record | decides | later superseded parts |
|---|---|---|---|
| 08-26 | [okvis-imu-noise-derivation](okvis-imu-noise-derivation.md) | Recording-envelope IMU noise | Rosario and HortiMulti rows → Rule C (only the ZED2i row is current) |
| 10-01 | [reference-review-20261001](reference-review-20261001.md) | Calibration and reference review for all datasets | Rosario → Option A; HortiMulti timing → hortimulti-decisions; ZED → zed-preparation |
| 10-01 | [paper-acceptance-20261001](paper-acceptance-20261001.md) | Claim-acceptance criteria | current |
| 10-01 | [publication-qualification-20261001](publication-qualification-20261001.md) | Blanket provenance hold | replaced by paper-acceptance |
| 10-01 | [repair-audit-20261001](repair-audit-20261001.md), [repair-handoff-20261001](repair-handoff-20261001.md) | Five-mode repair | counts → acceptance hand-off |
| 10-01 | [euroc-focused-campaign-20261001](euroc-focused-campaign-20261001.md), [airslam-rectification-audit](airslam-rectification-audit.md) | Corrected EuRoC AirSLAM/OpenVINS cohort (runs 4–6) | ZED parts → zed-preparation |
| 10-02 | [protocol-review-20261002](protocol-review-20261002.md) | Protocol validity and tick definitions | current |
| 10-02 | [zed-preparation-20261002](zed-preparation-20261002.md) | ZED calibration, reference v2, claims | current |
| 10-02 | [execution-readiness-20261002](execution-readiness-20261002.md) | Native readiness, ORB ABI hold | status line stale |
| 10-02 | [rosario-vio-candidates-20261002](rosario-vio-candidates-20261002.md) | Rosario candidate bundles | never used → Option A |
| 10-02/03 | [claude-new-algorithms-20261002](claude-new-algorithms-20261002.md), [claude-new-algorithms-setup-20261003](claude-new-algorithms-setup-20261003.md) | Selection and setup of the 4 new algorithms | setup doc partly stale (see errata) |
| 10-03 | [rerun-plan-20261003](rerun-plan-20261003.md) | Rosario camera model, Kalibr transform, offset 0 | Rosario → Option A |
| 10-05 | [hortimulti-decisions-20261005](hortimulti-decisions-20261005.md) | HortiMulti camera-clock IMU, builds, throttles | noise row → Rule C; §4 reference → accepted |
| 10-05 | [imu-noise-rule-20261005](imu-noise-rule-20261005.md) | Rule C definition and factors | "Two regimes" section → benchmark-decisions §1 |
| 10-06 | [benchmark-decisions-20261006](benchmark-decisions-20261006.md) | Rule C on every calibrated dataset, Option A, HortiMulti reference, ❗ marker, run order | current |
| 10-06 | [rosario-citrus-preparation-20261006](rosario-citrus-preparation-20261006.md) | Implementation of Option A and CitrusFarm Rule C | current |

Machine-readable counterparts: `campaigns/user-rerun-decisions-*.json` (superseded attempts), `campaigns/production-review-*.json` (claim reviews) and `campaigns/readiness-review-*.json` (readiness).

## Errata

These statements in older, mostly frozen, documents are no longer true. Quote the replacement instead.

| document | outdated statement | now true |
|---|---|---|
| imu-noise-rule-20261005, "Two regimes" | CitrusFarm (and ZED2i) use the envelope; Rosario decided later | Rule C on Rosario and CitrusFarm (ORB-SLAM3 included); only ZED2i keeps the envelope (benchmark-decisions §1) |
| hortimulti-decisions-20261005 §1 | HortiMulti noise = envelope 0.0035 / 0.110 | Rule C (commit 7b8437e) |
| hortimulti-decisions-20261005 §4 | Reference origin waits for the authors | Reference accepted as evaluated (benchmark-decisions §3) |
| okvis-imu-noise-derivation, "Frozen values" | Rosario 0.0015/0.070 and HortiMulti 0.0035/0.110 are production values | Only the ZED2i row is used; Rosario and HortiMulti use Rule C |
| rerun-plan-20261003 §1/§3/§5 | Rosario uses the authors' ORB profile (baseline 0.0497337, offset 0) and "closes without reruns"; 32 Rosario cells can become ✅ | Option A (baseline 0.050240890825, Kalibr remap, IMU −4,098,308 ns); all Rosario attempts before it are superseded |
| claude-new-algorithms-setup-20261003 | Separate checkout, nothing committed; Rosario row 0.0497 m and offset 0; HortiMulti 9.16 ms applied by the runner; cuVSLAM noise = sensor profile | All four algorithms are in main; Option A; camera-clock IMU; Rule C |
| reference-review-20261001 | Rosario profile inconsistency and HortiMulti timing defect open | Resolved by Option A and hortimulti-decisions |
| rosario-vio-candidates-20261002 | Candidate bundles pending selection | Never used; replaced by Option A |
| archive/2026-10/claude-findings-20261001 | Rosario: keep 33 cells, reference blocker closable | Superseded by Option A |
| README.md, PROGRESS.md, evaluation.md, running_algorithms.md, setup.md, generated/README.md, TODO.md header | "69 verified N=3 cells", "no execution authorized", "`--require-ready` rejects all" | Status lines are dated 2026-10-02; use the generated TODO and acceptance hand-off |
| author-quality-config-audit, archive/2026-08/algorithm-setup-fairness-audit | N=5 repetitions and the August noise policy | N=3; Rule C |
| okvis2x configs (comments) | "see PROGRESS.md Phase 4.6" | That section never existed |

## Map of the remaining documents

| area | documents |
|---|---|
| Methodology | [evaluation](evaluation.md), [run provenance](run-provenance.md), [run measurements](run-measurements.md), [result storage](result-storage-design.md), [results layout](results-layout.md), [literature methods](vslam-comparison-literature-methods.md), [IMU-noise policy](imu-noise-policy.md) |
| Operations | [setup](setup.md) (lacks the 4 new algorithms; see the setup doc of 10-03), [running algorithms](running_algorithms.md) |
| Datasets | ZED2i: [setup](zed2i_setup.md), [IMU extrinsics](zed2i-imu-extrinsics.md), [preparation](zed-preparation-20261002.md), [validation](zed-validation-20261002.md), [campaign plan (generated)](zed-campaign-20261002.md). Rosario, HortiMulti, CitrusFarm: see the decision records above; there is no separate CitrusFarm prose document yet. |
| Algorithm investigations | [AirSLAM refinement diagnostic](airslam-refinement-diagnostic-20261002.md), [saved-parameter review](saved-parameter-review-20261001.md), [author-quality config audit](author-quality-config-audit.md), `upstream/` (patches and upstream drafts) |
| campaigns/ | Code inputs and evidence records (see the frozen list); `readiness-review-*` (generated); `production-review-*` (claim reviews) |
| generated/ | Tables, claims, figures; `historical-before-repair-20261001/` is the archived pre-repair set |
| archive/ | `2026-08/`: machine-B and N=5 campaign records, fairness audit. `2026-10/`: validation receipts, agent goal/hand-off notes, pre-repair designs, Rosario candidate receipts, Claude findings of 10-01. History only. |

## Not on main

- **IMU-noise search pilot:** branch `experiment/imu-noise-search-20261009` (worktree `/data/imoroz/vslam-noise-search-20261009`), `docs/noise-search-pilot-20261009.md`. It is exploratory and not part of the Rule C N=3 campaign.
- **Investigation notes outside the repository:** `/data/imoroz/IMU-NOISE-ISSUE/` (fixes.md etc., cited by benchmark-decisions) and `/data/imoroz/IMU-NOISE-ISSUE2/`.
