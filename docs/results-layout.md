# Results layout (as of 2026-10-09)

`results/` is git-ignored and holds about 245 GiB on the server. 92 % of that is SLAM map binaries: AirSLAM `AirSLAM_mapv*.bin`, OKVIS2-X `okvis2-slam-final_map.g2o` and MAC-VO `tensor_map.npz`.

**Do not move or rename anything in `results/`.** Many files are recorded by path and SHA-256 in tracked records:
- `configs/campaigns/*.json`
- `docs/campaigns/paper-acceptance-20261001.json`
- the readiness reviews

Moving a recorded file makes the inventory rebuild fail, or turns accepted cells into `reviewed_evidence_changed`.

## The run store: `vo/ vo-lc/ vio/ vio-lc/ gnss-vio/`

Layout: `results/<mode>/<dataset>/<sequence>/<algorithm>/run<N>/`. Each run folder holds:
- `run_meta.json`, `run_eval.json`
- `trajectory.txt`
- `run_log.txt`
- `provenance/` (the configs the run actually used)
- `native/` and maps

Each cell folder also has a generated `metrics.csv`, `summary.json` and `report.md`.

Superseded and failed runs stay here on purpose: the acceptance ledger records them.

| run numbers | meaning |
|---|---|
| `run1`–`run3` | original campaign slots (physical id = repetition) |
| `run4`–`run6` | corrected EuRoC AirSLAM VIO/VIO-LC cohort |
| `run10001`+ | new attempts from the future manifest. The logical repetition is recorded in `.attempt-state/` and `configs/campaigns/*.json`. A cell can reach run10006 when an attempt was replaced. |
| `run90001`+ | readiness checks and pilots; never selected as results |
| `run9901`–`run9902` | smoke tests |
| `run1_conventional_gps`, `run1_ppk_full`, `run1_hybrid_alt` | GNSS-VIO variants |
| ≥ `run1000000000` | noise-search pilot; only in the experiment worktree |

Folders that look like sequences but are clips are readiness and diagnostic inputs, not benchmark sequences:
- `*_readiness60_*`, `*_readiness30_*`, `*_readiness10_*`
- `*_diag40*`, `field1_diag60/180`
- `smoke_mh_01_easy_200`

## Everything else in `results/`

| entry | class | what it is |
|---|---|---|
| `repair-20261001/` | **live pipeline state** (the name is historical) | `inventory.json` (which run is selected for each cell and repetition), `future-n3-manifest.json` (the executor's input), staged evaluations, prepared inputs. About 17 scripts read it. |
| `acceptance-20261001/` | pipeline state | acceptance evidence and the regenerated hand-off |
| `.attempt-state/`, `.locks/`, `.implementation-blobs/` | pipeline state | per-attempt identity and status, controller mutexes (also used by the noise-search worktree), exact source bytes for provenance |
| `zed-preparation-20261002/` | **runtime dependency** plus records | `orb-build/` holds `libg2o.so` and `libORB_SLAM3.so`, loaded by every ORB-SLAM3 run (`run_orbslam3.sh`) |
| `reference-review-20261001/`, `euroc-focused-20261001/`, `execution-readiness-20261002/`, `rosario-main-integration-20261002/`, `zed-vio-n3-20261003/`, `window-20261004/`, `window-20261005/` | recorded evidence plus campaign records | upstream calibration sources, executed manifests, executor states and readiness checks. The untracked tooling scripts that wrote several tracked records also live here. |
| `window-20261006/` | **live campaign** | `step1`, `checks-r`, `n1` (Rosario + CitrusFarm repetition 1), `r2`, `r3` |
| `citrusfarm-pilots-20261004/`, `zed-reference-inspection-20261002/`, `protocol-review-20261002/` | records not read by code | candidates for a future `_campaigns/` folder (docs link to the last two) |
| `site/`, `manifest.json`, `historical-cohorts/` | derived | result browser (`scripts/results/serve_site.sh 8080`), its manifest, reports for superseded cohorts |
| `.cache/` | cache | DSOL, SVO Pro and MASt3R staging plus an input-hash cache; regenerable |
| `.derived-history/`, `.derived-sites/` | write-only history | earlier bytes of every regenerated CSV and figure; 37 earlier browser builds (about 18 GiB) |

Outside `results/`: `logs/` is also operational. A log file's existence reserves its attempt ID. It also holds the ROS-domain locks and the campaign controller state (`logs/server-campaign/`).

## Finding the current numbers

1. **Root CSVs** `benchmark-{vo,vo-lc,vio,vio-lc,gnss-vio}.csv` have one row per planned slot (cell × 3), including missing and failed slots.
   - Useful columns: `attempt_exists`, `run_path`, `campaign_membership`, `run_status`, `scientific_status`, `primary_ate_rmse_m`.
   - `benchmark-historical-cohorts.csv` lists superseded attempts that recalibrated reruns replaced. Never pool it with current rows.
2. **Generated tables:** [`docs/generated/`](generated/tables.md).
3. **Selection source of truth:** `results/repair-20261001/inventory.json` → `cells[].attempts`.

The CSVs, tables and inventory are only as fresh as the last inventory rebuild. Batches finished since then (for example `window-20261006/n1` and `r2`) appear only after their batch-selection record and an inventory rebuild.

## Backup

Git does not cover `results/`, and as of 2026-10-09 there is no copy outside this server. An off-server backup still has to be set up (restic or borg to institute storage, with the pinned state and per-run evidence first).
