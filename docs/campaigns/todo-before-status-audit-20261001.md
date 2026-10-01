# Archived TODO before the 2026-10-01 status reconciliation

Historical record only. Its checkboxes, matrices, counts, scientific claims and paths are superseded by [the current TODO](../../TODO.md) and [the status audit](server-status-20261001.md).

---

# vSLAM Benchmark - TODO

> **Revised 2026-08-06 (post pipeline-overhaul + machine-B campaign).** All 259 runs are at
> `eval_schema: 2` (fixed GT interpolation, gap-aware coverage, SE3-primary metrics,
> origin-aligned GNSS ATE, global-alignment segments) with `gt_provenance` on every run; the
> five `benchmark-*.csv` are full rebuilds, byte-reproducible on both machines; report tables
> come ONLY from `scripts/eval/make_report_tables.py` (see `docs/generated/tables.md`), prose
> numbers from `scripts/eval/verify_claims.py`. See `PROGRESS.md` "2026-08-05 —
> Evaluation-pipeline fixes", `docs/campaigns/machine-b-report-20260806.md` and
> `docs/campaigns/machine-b-verification-20260806.md`.
> **Next milestone: the N=5 server campaign** (RTX 3090 / 24 GB) — see
> `docs/campaigns/server-campaign-plan.md`. The 🔁 cells below fold into it.

> Older summary (2026-08-03, kept for context): VO has 109 evaluated rows. OV2SLAM VO filled on
> str02/MH_01/MH_03 (OV2SLAM zed2i done — matrix row is authoritative). ORB-SLAM3 rebuilt/run NATIVELY from the submodule
> (no Docker): EuRoC N=1 (~0.05 m, deterministic), agricultural N=3 median+range (str02/seq1/seq5 are
> severely non-deterministic; str03 is stable) - see the VO note and finding 11. VO-LC has 40 rows:
> DPV-SLAM, OKVIS2, OKVIS2-X and ORB-SLAM3 now cover all 8 sequences (the two OKVIS zed2i cells are
> partial-coverage - see note). ORB-SLAM3 VO-LC (LC on) vs VO (LC off) on Rosario shows LC helps
> where a true loop exists (seq1: 4 loops, 1.52 m) and is inert where none does (seq5: 0 loops).
> The core VIO N=1
> matrix has 49 rows (7 algorithms x 7 standard sequences); corrected HortiMulti extrinsics and
> EuRoC MH_03/MH_05 are included. ZED2i adds six usable VIO trajectories plus one failed
> ORB-SLAM3 attempt, so `benchmark-vio.csv` has 55 rows. VIO-LC has 28 rows: OKVIS2, OKVIS2-X,
> AirSLAM and ORB-SLAM3 across all 7 core sequences - ORB-SLAM3 VIO-LC is the best config on Rosario
> (seq1 1.08 m, 127 loops) and fires zero loops on EuRoC (IMU makes LC redundant there)
> (no zed2i VIO-LC cell - no configs). GNSS-VIO N=1 is
> complete: 20 rows (5 algorithms x 4 GPS-bearing sequences), including the retained
> sequence5 PPK-versus-conventional study. Remaining priorities are N=3 validation, corrected-
> extrinsic OpenVINS+GPS HortiMulti reruns and evaluator hardening. OKVIS2-X automation is now
> committed (build script, runner, GPS converter), so its remaining gaps are runs, not tooling.

---

## Status legend

`[x]` done  `[ ]` not started  `[~]` in-progress / partially done  `[!]` blocked

---

## Run combinations matrix

Legend per cell: ✅ run complete | 🟡 run complete with caveat | ⬜ config only |
🔧 config missing | ➖ mode unsupported | **🔁 re-run recommended** (config-fairness
equalization — the cell's published value compares a tuned configuration against untuned
competitors, or vice versa; see `PROGRESS.md` config-deviation findings and
`docs/campaigns/server-campaign-plan.md` §C13. The N=5 server campaign re-runs ALL agricultural cells
anyway; 🔁 marks the ones that additionally need an A/B config decision first)

### VO (no IMU, no loop closure) - `results-vo/`

Legend: ✅ run complete | 🟡 run complete with caveat | ⬜ config only | 🔧 config missing | ➖ mode unsupported

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | 🟡 N=3 | 🟡 N=3 | 🟡 N=3 | ✅ N=3 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 🔁 |
| Basalt | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 |
| MAC-VO | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ⬜ config only |
| AirSLAM | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 |
| DROID-SLAM | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=3 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ⬜ config only |
| DPVO | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 |
| OKVIS2 | ✅ N=1 🔁 | ✅ N=1 🔁 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 |
| OKVIS2-X | ✅ N=1 🔁 | ✅ N=1 🔁 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 |
| OV2SLAM | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 |
| MASt3R-SLAM | 🟡 OOM | 🟡 OOM | 🟡 OOM | 🟡 OOM | 🟡 OOM | 🟡 OOM | 🟡 OOM | 🔧 config missing |
| MegaSaM | 🟡 OOM | 🟡 OOM | 🟡 OOM | 🟡 OOM | 🟡 OOM | 🟡 OOM | 🟡 OOM | 🔧 config missing |

> 🔁 (2026-08-06): OKVIS2/OKVIS2-X Rosario VO ran the stock EuRoC frontend while their
> HortiMulti cells ran a 5-parameter tuned frontend — the "good on HortiMulti, poor on
> Rosario" contrast partly measures tuning. A/B: re-run Rosario with the HortiMulti frontend
> (or HortiMulti with the EuRoC one). Basalt str02/str03 🔁 (VIO matrix): its HortiMulti cells
> carry a dedicated config + ~457x-inflated accel noise left from a superseded debugging sweep.
> ORB-SLAM3 zed2i 🔁: nFeatures 2000 vs 1200 everywhere else — one 1200-run bounds finding 2.
> MASt3R-SLAM/MegaSaM OOM cells: the 24 GB RTX 3090 server may lift the 12 GB OOM — optional
> revisit during the server campaign.

> ORB-SLAM3 VO = LC-off mode required (`LoopClosing: 0` or dedicated build). Old LC-on results are in `obsolete/`.
> **DPVO (2026-07-27):** monocular learned VO, replaces dropped DROID-SLAM. Best VO on Rosario
> seq5 (3.9m, beats all stereo), 2nd on seq1; ~9-13x better than DROID-SLAM. Light (~2-4 GB VRAM,
> runs on all sequences incl. 46k-frame zed2i where MegaSaM/MASt3R OOM). EuRoC calib needs radtan
> distortion (raw images); agricultural configs are rectified. DPV-SLAM is tracked separately as `vo-lc`.

> **zed2i field1** = local ZED2i field dataset (46283 pairs, 1080p, 77 min, RTK GT). Under the
> tested N=1 configurations, ORB-SLAM3 VO (0.256 m) and Basalt VO (0.446 m) outperformed every
> VIO attempt. The evidence is consistent with weak inertial excitation, but the exact factory
> camera-IMU transform and timing still need controlled validation.

### VIO (stereo + IMU, no loop closure) - `results-vio/`

Legend: ✅ run complete | 🟡 run complete with caveat | ⬜ config only | 🔧 config missing | ➖ mode unsupported

All core agricultural/EuRoC cells have N=1 results as of 2026-07-21. HortiMulti was corrected via
the camera-IMU extrinsic fix and no scale-collapsed core cells remain. ZED2i has six usable VIO
trajectories plus one ORB-SLAM3 failed attempt; every tested VIO configuration underperformed the
two VO baselines. Next step for the core table: **N=5 on the server** (`docs/campaigns/server-campaign-plan.md`).

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 failed |
| Basalt | ✅ N=1 | ✅ N=1 | ✅ N=1 🔁 | ✅ N=1 🔁 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 N=1 |
| OKVIS2 | ✅ N=1 🔁 | ✅ N=1 🔁 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 N=1 |
| OKVIS2-X | ✅ N=1 🔁 | ✅ N=1 🔁 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 N=1 |
| OpenVINS | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 N=1 |
| AirSLAM | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 N=1 |
| Voxel-SVIO | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 N=1 |

> HortiMulti IMU: extracted - str02=190493 samples, str03=48448 samples. Path: `datasets/hortimulti/strawberry{02,03}/mav0/imu0/data.csv`
> **HortiMulti VIO fix (2026-07-20):** the dominant cross-algorithm configuration error was a
> wrong camera-IMU extrinsic (raw fisheye extrinsic used on rectified images = missing 1.22 deg rotation;
> OKVIS2/OKVIS2-X/AirSLAM additionally had it inverted). Corrected in configs - scale now ~1.0
> everywhere. See PROGRESS.md.
> Voxel-SVIO: VIO-only (no VO, no LC). Runs via Docker (`vslam_voxel_svio:noetic`). Wrapper had a
> `pkill` self-match bug (fixed) that reported "no trajectory" on successful runs; it is also
> non-deterministic (real-time player) - ~2x run-to-run spread, so N=3 matters here especially.
> OKVIS2 (standalone) was built 2026-07-20 (`build_okvis2.sh`, needed -DHAVE_LIBREALSENSE=OFF
> -DUSE_CUDA=OFF).
> **zed2i field1 VIO (all 7 algorithms attempted, 2026-07-21):** under the tested N=1
> configurations, all usable VIO trajectories underperform the two VO baselines:
> - **No collapse, but VIO≫VO:** Voxel-SVIO 3.71 m (scale 0.978, ~71 s static-init delay -
>   its log spams "Failed static init: no accel jerk detected" until the first real motion),
>   AirSLAM 3.90 m (scale 0.965), Basalt 9.14 m (scale 0.816). All track cleanly but land
>   ~15-35× worse than VO (ORB-SLAM3 VO 0.256 m, Basalt VO 0.446 m).
> - **Scale collapse (evo Sim3 scale ≈ 0, SE3 ATE explodes to 10^5-10^6 m):** OpenVINS 5.33 m
>   (only 8.7 % tracked), OKVIS2 17.7 m, OKVIS2-X 18.3 m - the tightly-coupled filters.
> - **ORB-SLAM3:** VIO tracking is chronically unstable (repeated "Fail to track local map!")
>   and the committed attempt **segfaults in SaveTrajectoryEuRoC at export** -
>   no usable trajectory. Config authored (`zed2i_field1_..._stereo_inertial.yaml`, identity T_b_c1).
> The pattern is consistent with insufficient rotational excitation (mean |gyro| 4.7 deg/s), but
> it is not yet a proven shared root cause: the runs are N=1 and share calibration/timing assumptions.
> Apply the exact factory camera-IMU transform and validate timing before deciding whether N=3 is useful.

### VO-LC (visual only + loop closure) - `results-vo-lc/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| DPV-SLAM | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 |
| OKVIS2 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 N=1 partial |
| OKVIS2-X | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | 🟡 N=1 partial |
| ORB-SLAM3 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 |
| AirSLAM | 🔧 run as VIO-LC | 🔧 run as VIO-LC | 🔧 run as VIO-LC | 🔧 run as VIO-LC | 🔧 run as VIO-LC | 🔧 run as VIO-LC | 🔧 run as VIO-LC | 🔧 run as VIO-LC |
| OV2SLAM | ⬜ config only | ⬜ config only | ⬜ config only | ⬜ config only | ⬜ config only | ⬜ config only | ⬜ config only | ⬜ config only |
| MASt3R-SLAM | 🟡 OOM | 🟡 OOM | 🟡 OOM | 🟡 OOM | 🟡 OOM | 🟡 OOM | 🟡 OOM | 🔧 config missing |

> DPV-SLAM = DPVO + proximity loop closure (monocular, no IMU). LC **helps 2-3x on EuRoC but hurts every agricultural sequence** (false loops on repetitive crop rows) - see PROGRESS.md finding 10.
> **OKVIS2 / OKVIS2-X VO-LC full-sequence N=1 completed (2026-07-30/31).** IMU residuals off, LC on.
> Both loop-close: real accepted-closure counts (corrected metric, 2026-08-03) are e.g. seq1 OKVIS2 76,
> OKVIS2-X 30. **The earlier "OKVIS2-X = 0 closures" was a log-parsing bug** (its Frontend.cpp logs the
> same `LOOP CLOSURE: current frame` line as OKVIS2; the eval counted the wrong lines - fixed in
> `_evaluate_run.py`, see finding 12). EuRoC ATE is excellent (OKVIS2/OKVIS2-X MH_01 ~0.02 m).
> **The two zed2i cells are partial-coverage (🟡):** OKVIS2 (0.752 m, ~93% of frames) and OKVIS2-X
> (0.294 m, ~78%) both **wedge in end-of-sequence global BA on the 46k-frame zed2i sequence** and
> never terminate; a SIGTERM flushes a usable trajectory that evaluates cleanly over the covered
> span. Budget zed2i OKVIS-family LC as kill-to-flush, or cap the sequence.
> AirSLAM's LC lives in its offline `map_refinement` step; no visual-only `_vo_lc` config exists, and
> the LC that was run uses the inertial `_vio_slam` config, so AirSLAM's loop-closure results are
> tracked in **VIO-LC**, not here (🔧 = no vo-lc config).
> **ORB-SLAM3 VO-LC N=1 all 8 sequences completed (2026-08-03, native).** LC on (`loopClosing: 1`)
> vs the LC-off VO baseline. On the one dataset with a clean LC-off VO baseline (Rosario): seq1 fires
> 4 loops -> 1.52 m (vs VO median 3.00 m, LC **helps**); seq5 fires 0 loops -> 15.55 m (LC inert, no
> revisit). Loops also fired on str03 (1) and MH_05 (1). NOTE the HortiMulti/EuRoC/zed2i *VO* configs
> lack `loopClosing: 0`, so their VO baseline had LC on by default (contaminated) - only Rosario VO is
> a true LC-off baseline; see finding 11 revision.
> OV2SLAM (`configs/ov2slam/<dataset>_vo_lc.yaml`) and MASt3R-SLAM VO-LC runs are still pending. The
> OKVIS2/OKVIS2-X dataset readers still require `mav0/imu0/data.csv` even when IMU residuals are disabled.

### VIO-LC (stereo + IMU + loop closure) - `results-vio-lc/`

Legend: ✅ run complete | 🟡 run complete with caveat | ⬜ config only | 🔧 config missing | ➖ mode unsupported

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 |
|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 |
| OKVIS2 | ✅ N=1 | ✅ N=1 | ✅ N=1 🔁 | ✅ N=1 🔁 | ✅ N=1 | ✅ N=1 | ✅ N=1 |
| OKVIS2-X | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 |
| AirSLAM | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 | ✅ N=1 |
> 🔁 OKVIS2 hortimulti VIO-LC kept the stock EuRoC frontend while every other OKVIS2 hortimulti
> mode AND all OKVIS2-X hortimulti modes use the tuned 5-param frontend — the OKVIS2-vs-OKVIS2-X
> VIO-LC comparison on str02/str03 is not like-for-like until re-run with the tuned frontend.
> HortiMulti IMU: extracted. Path: `datasets/hortimulti/strawberry{02,03}/mav0/imu0/data.csv`
> **VIO-LC full-sequence N=1 completed (2026-07-30/31)** for OKVIS2 and OKVIS2-X (all 7 core
> sequences) and AirSLAM (4 agricultural sequences). AirSLAM = front-end (`vio_euroc.launch`) +
> offline `map_refinement`; the runner previously referenced a non-existent `vio_slam_euroc.launch`
> - fixed in `run_airslam.sh`. AirSLAM EuRoC MH_01/03/05 are done (see the matrix above; the
> earlier "re-queued but not yet run" note was stale — consistency sweep 2026-08-05).
> There is **no zed2i VIO-LC column**: OKVIS2 has no zed2i `_vio_lc` config, AirSLAM has no
> zed2i `_vio_slam` config, and OKVIS2-X zed2i VIO-LC was cut before running (the long pole, ~5-6 h,
> same end-of-sequence stall as its VO-LC cell). Consistent with finding 10: LC yields no meaningful
> ATE gain over VIO on the agricultural sequences (OKVIS2 seq1 18.3 m VIO-LC vs 18.9 m VO-LC).

### GNSS-VIO (stereo + IMU + GNSS) - `results-gnss-vio/`

Legend: ✅ run complete | 🟡 run complete with caveat | ⬜ config only | 🔧 config missing

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 |
|---|---|---|---|---|
| CIFASIS GNSS-SI | ✅ N=1 | ✅ N=1 PPK | ✅ N=1 | ✅ N=1 |
| RTAB-Map | ✅ N=1 | 🟡 N=1 PPK | ✅ N=1 | ✅ N=1 |
| VINS-Fusion | ✅ N=1 | ✅ N=1 PPK | ✅ N=1 | ✅ N=1 |
| OpenVINS+GPS | 🟡 N=1 | 🟡 N=1 PPK | 🟡 N=1 | 🟡 N=1 |
| OKVIS2-X (tight) | ✅ N=1 🔁 | ✅ N=1 🔁 | ✅ N=1 | ✅ N=1 |

> 🔁 OKVIS2-X tight-GNSS Rosario: antenna lever arm hard-coded `r_SA=[0,0,0]` (unmeasured) AND
> the untuned EuRoC frontend, while its winning HortiMulti cells run the tuned frontend — the
> "loose beats tight coupling" conclusion flips exactly along this boundary and must not be
> published until these cells are re-run with a measured lever arm + equalized config.

> EuRoC-MAV is **not** part of the gnss-vio track (no GPS in the dataset).
> Runners: `run_cifasis_gnss_si.sh`, `run_rtabmap_gps.sh`, `run_vins_fusion_gps.sh`, `run_openvins_gps.sh` (all accept `<dataset> <seq> [run_id] gnss-vio`).
>
> ~~OKVIS2-X is not one of these 16 runs~~ stale — OKVIS2-X tight-GNSS ran on all four
> GPS-bearing sequences 2026-08-05 (see the matrix row above, with its 🔁 caveat).
> Use `run_benchmark.sh <dataset> <seq> <algo> <N> gnss-vio` to run + evaluate automatically.
>
> **GPS quality:** rosariov2 **seq5 now uses high-quality PPK GPS** (`/reach_1/ppk/fix`, vertical RMSE
> ~0.12 m vs ~1.44 m conventional); the seq5 GNSS-VIO results above are PPK. **seq1 still uses
> conventional GPS** - no seq1 PPK log is available locally, so seq1 has NOT been re-run on PPK (do not
> confuse the two). PPK upgrade improved vertical RMSE -23% to -86% and overall ATE for the
> loosely-coupled estimators (VINS-Fusion, OpenVINS); CIFASIS vertical improved but overall ATE rose
> (horizontal re-balance); RTAB-Map inconclusive (odometry non-determinism), hence 🟡. HortiMulti has
> **no** higher-grade GPS available (only consumer `/antobot_gps`, status=0, vertical sigma 6.5-7.7 m),
> so its vertical error is a hardware limit. See `PROGRESS.md` GNSS-VIO GPS-quality study +
> `scripts/eval/_gps_noise_analysis.py`.
>
> **Remaining:** re-run seq1 on PPK if/when the seq1 PPK log becomes available.

---

## High-priority open tasks (Phase 2)

| # | Task | Status |
|---|---|---|
| 1 | Extract HortiMulti IMU (`/ms/imu/data` -> `mav0/imu0/data.csv`) | `[x]` |
| 2 | Run core VIO N=1 matrix | `[x]` 49 rows (7 algorithms x 7 standard sequences); ZED2i adds 6 usable rows + 1 failed attempt |
| 3 | Diagnose and fix hortimulti VIO scale collapse | `[x]` **root cause was a camera-IMU EXTRINSIC bug, NOT vibration** (the earlier "vibration floor" conclusion was wrong). Fixed in config; all algos scale ~1.0. See PROGRESS.md "RESOLVED". |
| 3b | Build OKVIS2 standalone (was never built) | `[x]` (`build_okvis2.sh`; -DHAVE_LIBREALSENSE=OFF -DUSE_CUDA=OFF) |
| 3c | Re-run 2 stale bad VIO runs (Voxel EuRoC, OpenVINS seq5) | `[x]` (were bad runs, not algorithm limits) |
| 3d | Add EuRoC MH_03/MH_05 VIO coverage + fix EuRoC times.txt (s->ns) | `[x]` |
| 4 | ~~Run ORB-SLAM3 VIO on rosariov2/seq1 N=3~~ | folded into task 9 (server campaign) |
| 5 | ~~Run Basalt VIO on rosariov2/seq1 N=3~~ | folded into task 9 (server campaign) |
| 6 | ~~Run OpenVINS VIO on rosariov2/seq5 N=3~~ | folded into task 9 (server campaign) |
| 7 | MASt3R-SLAM / MegaSaM revisit on the 24 GB server (optional — both OOM'd at 12 GB) | `[ ]` |
| 8 | ORB-SLAM3 VO-clean LC-off re-runs | `[x]` done 2026-08-04 (truly LC-off re-runs are the current VO table) |
| 9 | **N=5 server campaign** (supersedes all N=3 items): every agricultural cell x 5 run types at N=5, one machine, uniform feeding protocol, incl. the 🔁 config-equalization A/Bs | `[ ]` see `docs/campaigns/server-campaign-plan.md` |
| 10 | Complete GNSS-VIO N=1 sweep | `[x]` 20 headline runs (5 algorithms incl. OKVIS2-X x 4 sequences) |
| 10b | Re-run OpenVINS+GPS HortiMulti with corrected extrinsics; validate all four rows | `[ ]` folded into task 9 |
| 11 | Normalize EuRoC dataset aliases and result/config paths to `euroc_mav` | `[x]` central shell/Python canonicalization; obsolete aliases removed |
| 12 | Commit local-only runtime prerequisites | `[x]` **DONE 2026-08-06**: AirSLAM launch files + OpenVINS Dockerfile live in the forks (`kubojion/AirSLAM`, `kubojion/open_vins` @ `vslam-benchmark-patches`, wired in `.gitmodules`); OKVIS2 external CMake patches remain vendored in `vendor/prerequisites/` (nested upstream submodules — patch dir is the clean carrier) |
| 13 | Finish remaining LC/VO cells | `[x]` … Still open: OKVIS2-X zed2i VIO-LC (~5-6 h, kill-to-flush), MAC-VO zed2i VO (~6 h) — candidates for the server |
| 14 | OKVIS2-X "0 loop closures" | `[x]` **RESOLVED: log-parsing bug, not the algorithm.** See finding 12 |
| 15 | Add `loopClosing: 0` to hortimulti/euroc/zed2i `_stereo.yaml` | `[x]` clean LC-off baselines are the current VO table (2026-08-04) |
| 16 | Re-evaluate the 2 colleague-machine OKVIS2 VIO-LC runs with corrected LC metric | `[x]` closed by the machine-B re-evaluation campaign (2026-08-06, all EuRoC/HortiMulti runs re-parsed) |
| 17 | ~~Create GitHub forks~~ | `[x]` **DONE 2026-08-06** — forks created, branches pushed (airslam 1b70ff6, open_vins 289bca3), `.gitmodules` re-pointed |
| 18 | ~~Machine B: zed2i segment maps + GT tracking~~ | `[x]` **DONE 2026-08-06** (commits 9b0fc92 + 42c3492): vio/vo-lc maps regenerated on 2.86 m GT; euroc/hortimulti/zed2i GT + times + segments + alias symlinks tracked — verified byte-reproducible CSVs on any clone |
| 19 | ~~Fix zed2i turn detection~~ | `[x]` **DONE 2026-08-06** (5d71cbd): tangent-derived headings (2 m path smoothing) → zed2i now 10 row + 5 turn segments; zed2i runs re-evaluated. Known limitation (documented in-code): short absorbed segments can split one row into several — coalescing deferred to the server-campaign re-eval since it re-segments every dataset |

---

> **ZED2i TURN DETECTION (task 19, 2026-08-06, machine B):** the "2 pseudo-row segments / 0 turns"
> symptom was **not** a turn-angle threshold problem. `_segment_trajectory.py` derived heading from
> the GT quaternion, but the ZED2i GT is built from GPS position only — every row carries an
> **identity quaternion**, so yaw was constant 0 deg and no turn could ever be detected. Fix: a
> `yaw_from_path()` fallback that derives heading from the path tangent (2 m smoothing window) when
> the GT orientations are all identity. Verified neutral for rosariov2/hortimulti/euroc (those have
> real orientations, so the fallback never fires). ZED2i also needs `--min_seg_path_m 5` (the 25 m
> default merges its short 6-row pattern). Result: **15 segments {10 row, 5 turn}** (was 2 row / 0
> turn), and all 18 zed2i runs now report both row and turn ATE — e.g. ORB-SLAM3 VO 0.292 m row /
> 0.283 m turn, Basalt 0.448 / 0.642, DPVO 12.24 / 20.02.
>
> Two related issues found and **deliberately not fixed** (brief rule 5 — no improvised pipeline
> changes):
> 1. **`merge_segments` coalescing bug** — adjacent same-type segments are not merged. Fixing it
>    changes segmentation repo-wide (rosariov2 seq1 107 -> 43 segments, hortimulti 25 -> 14,
>    euroc 0 -> 11) and would require re-evaluating every rosariov2 run, which rule 3 forbids on
>    this machine. A `NOTE` documenting this sits at the call site.
> 2. **`datasets/rosariov2/sequence1/segments_auto.csv` is stale** relative to that sequence's
>    repaired PGT ground truth. Not regenerated here (rule 3).

> **ORB-SLAM3 VO NATIVE (2026-07-31, this machine):** the submodule builds and runs natively (no
> Docker) - `src/ORB_SLAM3/Examples/Stereo/stereo_euroc` linked against a local Pangolin, driven by
> `run_orbslam3.sh`. The agricultural/EuRoC VO cells were filled natively here. **The earlier
> "shim-vs-native divergence" was NOT a Docker artefact - it is ORB-SLAM3's inherent non-determinism
> on agricultural sequences.** Determinism check + 1200->2000 feature sweep (finding 11): EuRoC is
> deterministic (~0.05 m every run); str02 varies {1.85, 4.3, 21.1} m (scale collapses to 0.89,
> coverage 31-100%), seq1 {1.16, 3.0, 4.86} m, seq5 {4.0, 6.9, 14.8} m across N=3 - a config cannot
> fix it. str03 alone is stable (0.11 m x3). So agri cells are recorded as **N=3 median (range)**;
> the old 0.893 m / 1.18 m references were single lucky draws. EuRoC + ZED2i (0.256 m) stay N=1.
> `ORBSLAM3_CONFIG` env override added to the runner for config sweeps.
> OKVIS2/OKVIS2-X VO on agri sequences are best-effort (IMU off) and expectedly weaker than their VIO.

## Phase 2 per-algorithm tasks

### ORB-SLAM3

| Task | Status |
|---|---|
| VO-clean (LC-off) on rosariov2/seq1 N=3 | `[ ]` |
| VO-clean on hortimulti str02+03 N=3 | `[ ]` |
| VO-clean on EuRoC MH_01/03/05 N=1 | `[ ]` |
| VIO rosariov2/seq1 N=3 | `[ ]` |
| VIO-LC rosariov2/seq1 N=3 | `[ ]` |
| VIO EuRoC MH_01/03/05 N=1 | `[x]`; N=3 pending |
| VIO-LC EuRoC N=1 | `[ ]` |

### Basalt

| Task | Status |
|---|---|
| VIO rosariov2/seq1 N=3 | `[ ]` |
| VIO EuRoC MH_01/03/05 N=1 | `[x]`; N=3 pending |
| VIO hortimulti (after IMU extraction) | `[x]` |
| hortimulti VIO scale collapse | `[x]` **FIXED via extrinsic correction** (was misdiagnosed as vibration floor; the 5-run noise sweep searched the wrong parameter). With rectified T_imu_cam: str02 22.9->2.49 m, str03 2.85->0.19 m, scale 0.57->1.03. |

### OpenVINS

| Task | Status |
|---|---|
| VIO rosariov2/seq5 N=3 | `[ ]` |
| VIO EuRoC MH_01/03/05 N=1 | `[x]`; N=3 pending |
| VIO hortimulti (after IMU extraction) | `[x]` |

### AirSLAM

| Task | Status |
|---|---|
| VIO rosariov2/seq1+seq5 N=3 | `[ ]` |
| VI-SLAM (VIO-LC) rosariov2 N=3 | `[ ]` |
| VIO/VI-SLAM hortimulti (after IMU extraction) | `[x]` |
| VIO EuRoC MH_01/03/05 N=1 | `[x]`; N=3 pending |
| hortimulti str02/str03 scale collapse | `[x]` **FIXED**: extrinsic was inverted AND missing rectification. str02 46.3->5.30 m, str03 16.3->1.24 m, scale ~1.0. (Also recovered lost `vio_euroc.launch`; TensorRT needed a host reboot after a driver update.) |

### OKVIS2

| Task | Status |
|---|---|
| Scale seq1+seq5 to N=3 | `[ ]` |
| Add hortimulti + EuRoC configs | `[x]` |
| VIO EuRoC MH_01/03/05 N=1 | `[x]`; N=3 pending |
| hortimulti failure | `[x]` **FIXED via extrinsic correction** (the tracking failures were largely self-inflicted by the wrong extrinsic, not greenhouse texture). str02 49.9->2.14 m, str03 15.5->0.40 m, scale 0->1.03. Independent check: freshly-built binary + config patched hours earlier. |

### OKVIS2-X

Source and result integration exists independently of OKVIS2. The top-level build, run and
GPS-conversion automation is now committed; the existing VO/VIO result artifacts predate it and
came from manual runs, so they have not yet been reproduced through the runner.

| Task | Status |
|---|---|
| Source submodule/gitlink pinned (`src/okvis2x`) | `[x]` |
| Reproducible top-level build script (`build_okvis2x.sh`) | `[x]` |
| Top-level multi-mode runner (`run_okvis2x.sh`) | `[x]` (all five run types; `OKVIS2X_CONFIG` override for sweeps) |
| Configs for rosariov2 / EuRoC / HortiMulti / ZED2i | `[x]` (40 files, including experimental `vo_lc`) |
| gnss-vio configs (rosariov2 seq1+seq5) | `[x]` |
| `gps.csv` -> `mav0/gps0/data_raw.csv` converter | `[x]` |
| Register in eval pipeline (LOG_PATTERNS, plot dicts) | `[x]` |
| Measure `r_SA` (GNSS antenna lever arm) on the robot | `[ ]` (configs currently assume `[0,0,0]`) |
| First gnss-vio runs (rosariov2 seq1+seq5) | `[ ]` |
| Reproduce VO/VIO results through `run_okvis2x.sh` | `[ ]` (current artifacts are manual) |
| Manual N=1 VIO results | `[x]` all 7 core sequences plus ZED2i (see VIO matrix); N=3 pending |
| Recover HortiMulti IMU + GPS from hortimulti.zip | `[x]` (str02 190493/7620, str03 48448/1939 - counts match bag) |
| HortiMulti gnss_vio configs | `[ ]` (GPS recovered for both sequences, so unblocked) |
| Head-to-head OKVIS2 vs OKVIS2-X on rosariov2 vio | `[x]` seq1: OKVIS2 18.89 / OKVIS2-X 18.89; seq5: 20.29 / 20.40 - near-identical (shared estimator core) |

### MASt3R-SLAM

| Task | Status |
|---|---|
| Download checkpoints | `[x]` 2.9 GB, Naver Labs direct URLs (see setup.md §10) |
| Build env (CUDA 12.1 nvcc, vendored dust3r/in3d, numpy/opencv pins) | `[x]` |
| Port runner to upstream API (`--save-as`, `--calib`, retrieval.k) | `[x]` |
| Smoke test | `[!]` **blocked: OOM on 12 GB VRAM** |
| VO / VIO-LC runs on agri sequences | `[!]` blocked by the above - needs a larger card |

> Not a wiring problem: the env and runner work and reach real execution. MASt3R-SLAM
> keeps every keyframe on-GPU with no supported bound (`local_opt.window_size` is read
> but never applied upstream; `dataset.img_downsample` breaks the fixed-512 checkpoint;
> `dataset.subsample: 2` still OOM'd on rosariov2). Checkpoints are CC-BY-NC-SA-4.0.

### MegaSaM

| Task | Status |
|---|---|
| Checkpoints (megasam_final, DepthAnything, RAFT) | `[x]` automated in `setup_megasam_env.sh` |
| Build vendored CUDA extensions (`lietorch`, `droid_backends`) | `[x]` needs cuda-nvcc 11.8 + `setuptools<81`; `python setup.py install` (not `pip -e`) |
| Runtime deps (torch_scatter, xformers, huggingface_hub, `numpy<2`) | `[x]` |
| Port runner to the real 3-stage pipeline | `[x]` was calling a non-existent `megasam.demo` module |
| Grayscale workaround for UniDepth stage | `[x]` PIL mis-slices mode-`L` images; runner feeds it an RGB copy |
| First end-to-end run (hortimulti str03) | `[~]` in progress - stages 1a/1b pass, stage 2 untested |
| Runs on remaining sequences | `[ ]` |
| zed2i config | `[ ]` |

> Upstream has no single entrypoint: Depth-Anything -> UniDepth -> camera tracking, each a
> separate script with hard-coded demo paths. Stage 3 (`cvd_opt`) refines depth only and is
> skipped. Cost is three ViT-scale passes per frame, so budget hours per sequence.
> Monocular: comparable under Sim(3) only.

### DPVO / DPV-SLAM (replaces DROID-SLAM)

| Task | Status |
|---|---|
| Setup script, configs and runner | `[x]` |
| DPVO VO N=1 on all 8 sequences | `[x]` (`results-vo/`, `benchmark-vo.csv`) |
| DPV-SLAM VO-LC N=1 on all 8 sequences | `[x]` (`results-vo-lc/`, `benchmark-vo-lc.csv`) |
| Keep DPV-SLAM out of true VIO-LC bucket | `[x]` moved out of `results-vio-lc/` |

### VO-LC Candidates

| Task | Status |
|---|---|
| OKVIS2 VO-LC full N=1 (all 8 sequences) | `[x]` done; zed2i partial-coverage (kill-to-flush, see VO-LC note) |
| OKVIS2-X VO-LC full N=1 (all 8 sequences) | `[x]` done; zed2i partial. ~~0 accepted closures - verify LC~~ resolved: that was the log-parser bug (task 14 / finding 12); corrected counts are comparable to OKVIS2 (e.g. 30 vs 76 on seq1) |
| ORB-SLAM3 runner + configs for rosariov2/hortimulti/EuRoC/zed2i | `[x]` configured; 200-frame VO-LC smoke passed; full-sequence VO-LC still pending |
| MASt3R-SLAM runner + configs for rosariov2/hortimulti/EuRoC | `[x]` configured, blocked on >12 GB VRAM for full sequences |
| AirSLAM VO-LC | `[x]` reclassified as VIO-LC (LC is inseparable from its inertial pipeline) |
| OV2SLAM VO full N=1 (str02/MH_01/MH_03 filled) | `[x]` done; only zed2i VO still pending (~2 h) |
| OV2SLAM VO-LC full-sequence runs | `[ ]` configs exist; not yet run |

### OV2SLAM

| Task | Status |
|---|---|
| Accuracy-first configs (`force_realtime: 0`, half-speed replay for measured runs) | `[x]` |
| VO N=1 on Rosario seq1+seq5, EuRoC MH_05 and HortiMulti str03 | `[x]` 7.236 m / 8.045 m / 0.099 m / 0.351 m Sim3 ATE |
| Complete VO N=1 sweep on the remaining four standard sequences | `[ ]` HortiMulti str02, EuRoC MH_01/MH_03, ZED2i field1 |

### Voxel-SVIO

| Task | Status |
|---|---|
| Docker image + container build (`scripts/setup/setup_voxel_svio_docker.sh`) | `[x]` (NOTE: setup guard skips clone if `src/voxel_svio/` exists even when empty - source must actually be present) |
| Configs: euroc_mav (per-seq), rosariov2, hortimulti | `[x]` |
| Run script (`scripts/run/run_voxel_svio.sh`) + ROS1 data player | `[x]` |
| Smoke test EuRoC MH_01_easy N=1 | `[x]` (0.083 m; earlier 3.03 m row was a stale bad run) |
| VIO rosariov2/seq1+seq5 N=3 | `[ ]` |
| VIO hortimulti str02+str03 N=3 | `[ ]` |
| VIO EuRoC MH_01/03/05 N=1 -> N=3 | `[ ]` |

---

## Aggregation and reporting

| Task | Status |
|---|---|
| Rebuild `benchmark-vo.csv` after ORB-SLAM3 VO-clean results land | `[ ]` |
| Rebuild `benchmark-vio.csv` after N=3 runs (Basalt/ORB-SLAM3/OpenVINS) | `[ ]` |
| Add MASt3R-SLAM to applicable CSVs | `[ ]` |
| Generate segment maps for all new Phase 2 sequences | `[ ]` |
| Final cross-algo ATE plots (VO vs VIO per sequence) | `[ ]` |
| Thesis-ready LaTeX table | `[ ]` |

---

## Dropped / out of scope

| Algorithm | Reason |
|---|---|
| DROID-SLAM | "Bulky, old, requires tons of resources" (supervisor). N=3 results kept in `results-vo/` as historical reference. |
| Stella-VSLAM | "Mostly reimplementation of ORB-SLAM3, adds nothing" (supervisor). |
| VINS-Fusion | Overlaps Basalt + OpenVINS; ROS1 only. |
| SVO Pro Open | ROS1 Melodic only; frozen toolchain. |
| DSO / Stereo-DSO | Misaligned with stereo-IMU direction. |
| cuVSLAM | Closed-source (NVIDIA). Cite KITTI numbers only. |
| Kimera-VIO | Overlaps OpenVINS. |
| MegaSaM | Lower priority than MASt3R-SLAM and DPVO; keep as optional. |

---

## Adding a new algorithm

1. Build / containerize under `src/<algo>/`.
2. Write `scripts/run/run_<algo>.sh` with signature `<dataset> <seq> [run_id=1] [run_type=vo]`.
3. Write config(s) under `configs/<algo>/`.
4. Add a row to each table above.
5. Smoke-test on EuRoC MH_01_easy first.

## Adding a new dataset

1. Write extraction script in `scripts/data/`.
2. Create `docs/private/dataset-specific/dataset_<name>.md`.
3. Extract to `datasets/<name>/<seq>/mav0/` with standard layout.
4. Add a column to each table above.

---

## DONE (Phase 1 - VO benchmark)

All Phase 1 VO runs are complete (N=3) and evaluated. See PROGRESS.md Phase 1 for the full
results table. Summary:

- ORB-SLAM3 (LC-on): rosariov2 seq1+seq5, hortimulti str02+str03 - results in `obsolete/` (LC-on confound)
- Basalt VO: all agri + EuRoC - done-N3 / done-N1
- MAC-VO: all agri + EuRoC - done-N3 / done-N1
- AirSLAM VO: all agri + EuRoC - done-N3 / done-N1
- DROID-SLAM: all agri + EuRoC - done-N3 / done-N1
- OKVIS2 VO: rosariov2/seq1+seq5 - done-N1

Kept as Phase 2 restructure (Phase 4.5):
- [ ] Rebuild ORB-SLAM3 with loop closure disabled (or wire up the
      stereo-inertial example) so it slots back into `vo` / `vio` / `vio-lc`.
- [ ] Re-run AirSLAM with `run_type=vio` and `vio-lc` on Rosario v2 and
      HortiMulti once `mav0/imu0/data.csv` is available for both datasets.
- [ ] Re-run Basalt with `run_type=vio` on Rosario v2 and HortiMulti.
- [ ] Extract IMU streams: HortiMulti needs `mav0/imu0/data.csv` from the
      `/ms/imu/data` topic (`scripts/data/_hortimulti_extract.py`).
      Rosario v2 needs the same generated from its `imu.csv`.
- [ ] Download MegaSaM checkpoints, run on EuRoC sanity sequence, then on
      Rosario / HortiMulti (`run_type=vo`).
- [ ] Download MASt3R-SLAM checkpoints, run on EuRoC sanity sequence, then
      on the agricultural sequences (`run_type=vo` and `vo-lc`).
- [ ] Add a `vio_slam` ORB-SLAM3 binary path and configs once the build
      lands.

## How to read this file

- `[x]` = done   `[ ]` = pending   `[~]` = partially done / blocked
- Sections are organised by **dataset → algorithm**; add new blocks using the
  same template when extending to more algorithms or datasets.
- The **cross-algorithm comparison** section at the bottom is filled after
  every algorithm on a dataset is complete.

---

## Standard vSLAM benchmarking pipeline (reference)

The community-standard evaluation workflow (Sturm 2012, TUM RGB-D; Geiger 2012,
KITTI; Grupp 2017, evo) has the following stages:

1. **Data prep** — extract bag → EuRoC layout (`cam0/`, `cam1/`, `times.txt`),
   create `gt_tum.txt` in TUM format (timestamp tx ty tz qx qy qz qw, seconds).
2. **Algorithm config** — write a correctly-named YAML config file for each
   (algorithm, dataset) pair; verify all required parameters are present.
3. **Run** — execute the algorithm, capture trajectory + runtime metadata
   (FPS, peak GPU MB); save to `results/<dataset>/<seq>/<algo>/`.
4. **Timestamp normalisation** — ensure all estimated trajectories use
   second-epoch timestamps matching the GT file's epoch.
5. **ATE / APE** (`evo_ape`) — absolute trajectory error after rigid SE(3)
   alignment; primary global accuracy metric.  Report RMSE and mean.
6. **RPE** (`evo_rpe`) — relative pose error over a fixed window (~1 s);
   measures local drift.  Report RMSE of translational and rotational error.
7. **Completion rate** — `N_estimated / N_total × 100 %`; captures how often
   the system loses tracking.
8. **Runtime metrics** — wall-clock FPS, peak GPU memory, CPU usage.
9. **Multi-run benchmark** — run algorithm N times (N=3); `run_orbslam3.sh <dataset> <seq> <run_id>`.
10. **Per-run evaluation** — `scripts/eval/_evaluate_run.py <dataset> <seq> <algo> <run_id>` → `run_eval.json`.
11. **Aggregate runs** — `scripts/eval/_aggregate_runs.py <dataset> <seq> <algo>` → `metrics.csv`, `report.md`.
12. **Segment visualisation** — `scripts/eval/_plot_segments.py <dataset> <seq>` → `segment_map.png`.

---

## Phase 0 – Infrastructure

| Task | Status |
|---|---|
| Clone + build ORB-SLAM3 (UZH upstream) | `[x]` |
| Patch ORB-SLAM3 for C++14 (sigslot) | `[x]` |
| Fix ORB-SLAM3 `Rectified` null-ptr bug (`Settings.cc`) | `[x]` |
| Build Pangolin v0.9.5 | `[x]` |
| Install `evo` evaluation toolkit | `[x]` |
| Script layout: `build/`, `data/`, `run/`, `eval/` | `[x]` |
| `run_orbslam3.sh` — multi-run with resource monitoring | `[x]` |
| `_resource_monitor.py` — GPU+CPU+RAM every 1s | `[x]` |
| `_interpolate_gt.py` — sparse GT → camera timestamps (Slerp) | `[x]` |
| `_segment_trajectory.py` — **v2: 2 m sliding-window path-length, 10° heading / 20 cm chord deviation** | `[x]` |
| `_evaluate_run.py` — full per-run evaluation (ATE Sim3 + **SE3**) → `run_eval.json` | `[x]` |
| `_aggregate_runs.py` — N runs → `metrics.csv` + `report.md` (Sim3 + SE3 columns) | `[x]` |
| `_plot_segments.py` — **8 K segment map, 3 hierarchies (per-run, per-algo, cross-algo)** | `[x]` |
| `run_benchmark.sh` — one-shot pipeline: run N times + interpolate GT + segment + evaluate + aggregate | `[x]` |
| RPE metric: use `point_distance` not `trans_part` (frame mismatch fix) | `[x]` |
| **Sim(3) vs SE(3) reporting**: both alignments computed every run | `[x]` |
| **Body↔camera mount mismatch documented** (Strawberry-03 RPE rot artefact) | `[x]` |
| `run_droidslam.sh` / `run_macvo.sh` upgraded to **multi-run framework** (`<run_id>` arg, `_resource_monitor.py`) | `[x]` |
| DROID-SLAM conda env (`droidenv`) | `[x]` | lietorch, torch_scatter, droid_backends all built |
| MAC-VO conda env | `[x]` | `macvo` env created; models downloaded |
| **Basalt binary install** (`~/.local/bin/basalt_vio`, v0.1.7) | `[x]` | Binary installer for Ubuntu 22.04; sources `~/.basalt/env` |
| `run_basalt.sh` | `[x]` | EuRoC format, auto-generates `mav0/cam*/data.csv`, `--use-imu false` |
| `configs/basalt/hortimulti_calib.json` + `rosariov2_calib.json` + `vo_config.json` | `[x]` | Pinhole + `vio_min_triangulation_dist: 0.03` |
| **AirSLAM Docker** (`air_slam` container, `xukuanhit/air_slam:v4`) | `[x]` | Docker Engine + nvidia-container-toolkit; catkin_make inside container |
| `scripts/setup/setup_airslam_docker.sh` | `[x]` | One-shot pull + create + build |
| `run_airslam.sh` | `[x]` | Polls `trajectory_v0.txt`, `pkill roslaunch`, `mv -f`, FPS from input frames |
| `configs/airslam/{hortimulti,rosariov2}_{camera,vo}.yaml` | `[x]` | Per-dataset intrinsics + TRT engine name |

---

## Phase 1 – Dataset: Rosario v2

> Agricultural field rows, stereo + GPS GT, 15 fps, 1280×720.
> Full sequence 1 = 13 821 frames, ~18 min.
> Official evaluation: https://github.com/CIFASIS/rosariov2

### 1-A  Data preparation

| Task | Status |
|---|---|
| `scripts/data/convert_rosario_to_tum.sh` — OOM-safe streaming extractor | `[x]` |
| Extract sequence 1 (13 821 frames) | `[x]` |
| `gt_tum.txt` present (GPS PGT, second-epoch timestamps) | `[x]` |
| Extract sequence 5 (11 640 frames) | `[x]` |
| Extract sequences 2–4 (if needed) | `[ ]` |

### 1-B  ORB-SLAM3

| Task | Status | Notes |
|---|---|---|
| Config `configs/orbslam3/rosariov2_stereo.yaml` | `[x]` | Rectified, fx=648.86 |
| Run full sequence 1 (single, old format) | `[x]` | 13 821 frames, 12.55 fps, 1101 s |
| ATE on sequence 1 (old single run) | `[x]` | **RMSE 1.361 m**, mean 1.311 m |
| RPE (15-frame window) on sequence 1 | `[x]` | trans RMSE **0.115 m**, rot RMSE **3.56 °** |
| Interpolate GT for seq1 (`gt_interp_tum.txt`) | `[x]` | 13821 poses at camera timestamps |
| Auto-segment seq1 (`segments_auto.csv`) | `[x]` | 145 segs: 125 row (863 s), 20 turn (60 s) |
| **Run seq1 × 3 (multi-run benchmark)** | `[x]` | ATE 1.176 ± 0.317 m, 100%, 5-6 loops |
| **Evaluate + aggregate seq1 × 3** | `[x]` | `metrics.csv` + `report.md` + `segment_map.png` done |
| Run sequence 5 (single, old format) | `[x]` | 11 640 frames, 11.55 fps, 1008 s, 100% completion |
| Evaluate sequence 5 (old single run) | `[x]` | **ATE RMSE 8.274 m** (Sim3 alignment) |
| Interpolate GT for seq5 (`gt_interp_tum.txt`) | `[x]` | 11640 poses at camera timestamps |
| Auto-segment seq5 (`segments_auto.csv`) | `[x]` | 101 segs: 95 row (756 s), 6 turn (19 s) |
| **Run seq5 × 3 (multi-run benchmark)** | `[x]` | ATE 20.207 ± 4.204 m, 91% avg, 0 loops |
| **Evaluate + aggregate seq5 × 3** | `[x]` | `metrics.csv` + `report.md` + `segment_map.png` done |
| Segment map visualisation seq1 | `[x]` | `results/rosariov2/sequence1/segment_map.png` |
| Segment map visualisation seq5 | `[x]` | `results/rosariov2/sequence5/segment_map.png` |
| Run remaining sequences | `[ ]` |  |
| Evaluate remaining sequences | `[ ]` |  |

### 1-C  DROID-SLAM

| Task | Status | Notes |
|---|---|---|
| Set up conda env + install dependencies | `[x]` | torch 2.7+cu126, lietorch 0.2, torch_scatter 2.1.2 |
| `scripts/run/run_droidslam.sh` + `_droid_demo_wrapper.py` | `[x]` | stereo, TUM trajectory output |
| `configs/droidslam/rosariov2.txt` intrinsics file | `[x]` | fx=fy=648.86, cx=645.01, cy=348.24 |
| `droid.pth` pretrained weights | `[x]` | downloaded to `src/DROID-SLAM/` |
| Run sequence 1 | `[x]` | full sequence (6911 frames, stride=2), skip_backend |
| Evaluate sequence 1 | `[x]` | **ATE RMSE 45.05 m** (Sim3 alignment) |
| Sequence 5 trajectory | `[x]` | 3 runs provided by collaborator; timestamps converted ns→s |
| Evaluate sequence 5 | `[x]` | **ATE RMSE 50.02 m** (Sim3, mean of 3 runs) |

### 1-D  MAC-VO

| Task | Status | Notes |
|---|---|---|
| Set up conda env + install dependencies | `[x]` | `macvo` env created; models downloaded |
| `scripts/run/run_macvo.sh` | `[x]` | fixed: conda set-u, upstream odom config, `--useRR`, correct Results path |
| `configs/macvo/rosario_v2_sequence.yaml` | `[x]` | GeneralStereo format; intrinsics=648.86, bl=0.04973; `left/right` symlinks created |
| Run sequence 1 | `[x]` | 13821 frames, 100% completion |
| Evaluate sequence 1 | `[x]` | **ATE RMSE 13.277 m** (Sim3 alignment) |
| `configs/macvo/rosariov2_sequence5.yaml` | `[x]` | same intrinsics/bl; root→sequence5; `left/right` symlinks created |
| Run sequence 5 | `[x]` | 11 640 frames, 100% completion (3 runs done) |
| Evaluate sequence 5 | `[x]` | **ATE RMSE 19.384 ± 0.006 m** (Sim3, 3 runs) |

### 1-E  Cross-algorithm comparison (Rosario v2)

| Task | Status |
|---|---|
| All four algorithms run on sequence 1 (single run) | `[x]` |
| ORB-SLAM3 + DROID-SLAM run on sequence 5 | `[x]` |
| MAC-VO on sequence 5 × 3 | `[x]` | ATE Sim3 **19.384 ± 0.006 m** (3 runs; scale=0.933, 100% tracking) |
| ORB-SLAM3 × 3 multi-run benchmark seq1 | `[x]` | ATE 1.176 ± 0.317 m, `report.md` + `segment_map.png` |
| ORB-SLAM3 × 3 multi-run benchmark seq5 | `[x]` | ATE 20.207 ± 4.204 m, `report.md` + `segment_map.png` |
| Segment maps for seq1 and seq5 | `[x]` | seq1 ✓, seq5 ✓ |
| `metrics.csv` + `report.md` for seq1 | `[x]` | done |
| `metrics.csv` + `report.md` for seq5 | `[x]` | done |
| Comparison table for thesis chapter | `[ ]` | Final LaTeX/PDF table for thesis |

### 1-F  Basalt (stereo VO)

| Task | Status | Notes |
|---|---|---|
| `configs/basalt/rosariov2_calib.json` | `[x]` | EuRoC format, pinhole, `vio_min_triangulation_dist: 0.03` |
| Run seq1 × 3 + evaluate | `[x]` | ATE Sim3 **14.279 ± 0.302 m**, SE3 **18.693 ± 0.586 m**, 100% |
| Run seq5 × 3 + evaluate | `[x]` | ATE Sim3 **15.035 ± 0.062 m**, SE3 **15.425 ± 0.068 m**, 100% |
| Segment maps with Basalt | `[x]` | seq1 + seq5 regenerated |

### 1-G  AirSLAM (deep-feature stereo VO)

| Task | Status | Notes |
|---|---|---|
| `configs/airslam/rosariov2_camera.yaml` + `rosariov2_vo.yaml` | `[x]` | 1280×720, baseline 0.04973m |
| TensorRT engine compiled for rosariov2 (1280×720) | `[x]` | Compiled on seq1 run1 startup |
| Run seq1 × 3 + evaluate | `[x]` | **DONE** (9.888 ± 0.059 m Sim3, 9.891 ± 0.058 m SE3, 100% × 3) |
| Run seq5 × 3 + evaluate | `[x]` | **DONE** (12.722 ± 0.991 m Sim3, 12.777 ± 1.014 m SE3, 100% × 3) |



---

## GNSS-VIO (stereo + IMU + GNSS) - `results-gnss-vio/`

Phase F: GPS-aware algorithms with full Sim(3)+SE(3) eval pipeline.

Infrastructure status:
- [x] `run_type=gnss-vio` registered in `_paths.sh` and `_run_type.py`
- [x] `results-gnss-vio/` + `benchmark-gnss-vio.csv` wired into the eval pipeline
- [x] Shared GPS data players (`gnss_data_player.py` ROS 1, `gnss_data_player_ros2.py` ROS 2)
- [x] HortiMulti GPS extraction added to `_hortimulti_extract.py` (`--gps-only`,
      `--no-gps`, `--gps`); topic default `/antobot_gps`. Handles the upstream
      quirk where `header.stamp` is constant in `/antobot_gps` (falls back to
      bag-arrival time) and altitude is published in millimetres (auto-rescales
      when `max(alt) > 1000 m`).
- [x] CIFASIS GNSS-SI: clone + Dockerfile + setup script + configs for rosariov2
      seq1/seq5 + hortimulti str02/str03 + runner.
- [x] RTAB-Map: configs (rosariov2, hortimulti) + ROS 2 launch runner.
      `gnss_data_player_ros2.py` publishes `/cam{0,1}/camera_info` from per-dataset
      rectified intrinsics passed via `run_rtabmap_gps.sh`.
- [x] VINS-Fusion: clone + Dockerfile + setup script + configs for rosariov2
      seq1/seq5 + hortimulti str02/str03 (incl. per-cam YAMLs) + runner.
      Ceres pinned to `1.14.0` (2.1+ uses `std::integer_sequence`, incompatible
      with VINS-Fusion's hard-coded `-std=c++11`). All `CV_*` legacy macros are
      sed-rewritten to `cv::*` after `COPY src/VINS-Fusion` in the Dockerfile.
      HortiMulti `body_T_cam0` is `T_imu_cam0_raw @ blkdiag(R1.T, 1)` where
      `R1` comes from `cv2.fisheye.stereoRectify` in `_hortimulti_extract.py`.
- [x] OpenVINS+GPS: OpenVINS odometry + `robot_localization` EKF runner and four N=1 artifacts.
- [x] HortiMulti GPS extraction completed for str02/str03 (7620/1939 fixes;
      consumer-grade fixes with large vertical covariance).
- [x] CIFASIS GNSS-SI N=1 on rosariov2 seq1/seq5 + HortiMulti str02/str03; N=3 pending.
- [x] RTAB-Map N=1 on all four sequences; seq5 PPK is partial/nondeterministic; N=3 pending.
- [x] VINS-Fusion N=1 on all four sequences; N=3 pending.
- [~] OpenVINS+GPS N=1 on all four sequences; validate all rows and rerun HortiMulti with the
      corrected extrinsic before N=3.
- [x] Rosario sequence5 PPK-versus-conventional four-algorithm study completed.
