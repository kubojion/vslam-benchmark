# Server status audit — 2026-10-01

> Initial inventory, superseded for current counts by [the repair audit](../repair-audit-20261001.md)
> and [TODO](../../TODO.md). Saved-artifact recovery now stages 545 original campaign
> evaluations, versus the 538 marker-qualified evaluations counted below. Preserve
> this report as the pre-repair record. Future five-mode N=3 preparation is tracked
> [separately](future-n3-preparation.md); the old N=5 plan is not retroactively complete.

This is an artifact inventory, not a certification of scientific validity. No estimators,
re-evaluations, campaign resumes, or result replacements were launched during this audit.
Existing uncommitted implementation and calibration work was preserved.

## Scope and counting rules

The executed campaign is `quality-final-n3-no-gnss`: **200 cells / 600 planned runs**,
including N=3 on EuRoC as well as the agricultural sequences. The committed
`configs/campaigns/quality-final.json` still describes **N=5, 220 cells / 1,100 runs**, including
GNSS. These are different scopes; neither the full N=3 execution nor the original N=5 plan
is complete. N=5 is not silently considered fulfilled by N=3.

A cell is `(run_type, dataset, sequence, algorithm)`. An evaluated repetition here means
`run1`, `run2` or `run3` has both `run_eval.json` and `COMPLETE` in the current `results/` tree.
`COMPLETE` is an artifact-validation marker; it also permits `scale_collapse`, and does not
mean accurate or full-coverage tracking. Missing evaluations can include failed attempts or
recoverable trajectories; they are not necessarily never-attempted runs. This audit reads
existing markers and metadata; it does not freshly validate every trajectory.

The executed manifest is preserved as [a documentation snapshot](server-n3-manifest-20260826.json).
Its original path is `logs/server-campaign/quality-final-n3-no-gnss/manifest.json`.
SHA-256: `3a5c34a8ba69cc30f3fd5a485b82fb7affe70bf5ce94cb5e550c4565f210eada`.

## Current completion

| Mode | Target cells | N=3 evaluated | N=1 evaluated | No complete evaluation | Evaluated / target runs |
|---|---:|---:|---:|---:|---:|
| vo | 64 | 61 | 0 | 3 | 183 / 192 |
| vo-lc | 48 | 45 | 0 | 3 | 135 / 144 |
| vio | 56 | 42 | 7 | 7 | 133 / 168 |
| vio-lc | 32 | 28 | 3 | 1 | 87 / 96 |
| **Total** | **200** | **176** | **10** | **14** | **538 / 600** |

Of the 176 N=3 cells, **174 have three `ok` evaluations**, and two have two `ok` evaluations
plus one collapse. Across all 538 evaluated target runs: **535 `ok`, 3 `scale_collapse`**.
All 538 identify the server as `machine-3c9dca59a50f` in run metadata.
There are **62 missing evaluations** to reach the current N=3 target; this is not a claim
that 62 fresh estimator executions are needed. The existing coverage metric puts 47 of the
538 below 95%; coverage semantics still require the review described below.

## Complete matrix of current N=3 target

`3/3` = three evaluated repetitions; `1/3` = one; `0/3` = none.
`C` means a retained scale collapse (not a missing repetition).
N=3 cells still require coverage, provenance and metric review before publication.

### vo

| Algorithm | Rosario 1 | Rosario 5 | Horti 02 | Horti 03 | MH01 | MH03 | MH05 | ZED |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ORB-SLAM3 | 0/3 | 0/3 | 0/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| OKVIS2 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 C |
| OKVIS2-X | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| AirSLAM | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| Basalt | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| OV2SLAM | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| DPVO / DPV-SLAM | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| MAC-VO | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |

### vo-lc

| Algorithm | Rosario 1 | Rosario 5 | Horti 02 | Horti 03 | MH01 | MH03 | MH05 | ZED |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ORB-SLAM3 | 0/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| OKVIS2 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| OKVIS2-X | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| AirSLAM | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| OV2SLAM | 3/3 C | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| DPVO / DPV-SLAM | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |

### vio

| Algorithm | Rosario 1 | Rosario 5 | Horti 02 | Horti 03 | MH01 | MH03 | MH05 | ZED |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ORB-SLAM3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| OKVIS2 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/3 |
| OKVIS2-X | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/3 |
| AirSLAM | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/3 |
| Basalt | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/3 |
| OpenVINS | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 1/3 | 1/3 C |
| Voxel-SVIO | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/3 |

### vio-lc

| Algorithm | Rosario 1 | Rosario 5 | Horti 02 | Horti 03 | MH01 | MH03 | MH05 | ZED |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ORB-SLAM3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| OKVIS2 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/3 |
| OKVIS2-X | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/3 |
| AirSLAM | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/3 |

## Exact missing evaluations

| Mode | Dataset / sequence | Algorithm | Missing run IDs |
|---|---|---|---|
| vo | rosariov2 / sequence1 | ORB-SLAM3 | 1, 2, 3 |
| vo | rosariov2 / sequence5 | ORB-SLAM3 | 1, 2, 3 |
| vo | hortimulti / strawberry02 | ORB-SLAM3 | 1, 2, 3 |
| vo-lc | rosariov2 / sequence1 | ORB-SLAM3 | 1, 2, 3 |
| vo-lc | zed2i / field1_110426_full_10fps_q90 | OKVIS2 | 1, 2, 3 |
| vo-lc | zed2i / field1_110426_full_10fps_q90 | OKVIS2-X | 1, 2, 3 |
| vio | rosariov2 / sequence1 | OpenVINS | 1, 2, 3 |
| vio | rosariov2 / sequence5 | OpenVINS | 1, 2, 3 |
| vio | hortimulti / strawberry02 | OpenVINS | 1, 2, 3 |
| vio | hortimulti / strawberry03 | OpenVINS | 1, 2, 3 |
| vio | euroc_mav / MH_01_easy | OpenVINS | 1, 2, 3 |
| vio | euroc_mav / MH_03_medium | OpenVINS | 1, 2, 3 |
| vio | euroc_mav / MH_05_difficult | OpenVINS | 2, 3 |
| vio | zed2i / field1_110426_full_10fps_q90 | ORB-SLAM3 | 1, 2, 3 |
| vio | zed2i / field1_110426_full_10fps_q90 | OKVIS2 | 2, 3 |
| vio | zed2i / field1_110426_full_10fps_q90 | OKVIS2-X | 2, 3 |
| vio | zed2i / field1_110426_full_10fps_q90 | AirSLAM | 2, 3 |
| vio | zed2i / field1_110426_full_10fps_q90 | Basalt | 2, 3 |
| vio | zed2i / field1_110426_full_10fps_q90 | OpenVINS | 2, 3 |
| vio | zed2i / field1_110426_full_10fps_q90 | Voxel-SVIO | 2, 3 |
| vio-lc | zed2i / field1_110426_full_10fps_q90 | ORB-SLAM3 | 1, 2, 3 |
| vio-lc | zed2i / field1_110426_full_10fps_q90 | OKVIS2 | 2, 3 |
| vio-lc | zed2i / field1_110426_full_10fps_q90 | OKVIS2-X | 2, 3 |
| vio-lc | zed2i / field1_110426_full_10fps_q90 | AirSLAM | 2, 3 |

The retained collapses are ZED OKVIS2 VO run2, Rosario sequence1 OV2SLAM VO-LC run2,
and ZED OpenVINS VIO run1. Preserve these outcomes in failure-rate reporting; do not
replace failed trials until three successes remain.

## Recovery evidence and activity

No matching campaign driver, watcher or estimator process was found during the audit.
The only running Docker containers were unrelated document-service containers.
Three campaign state files still contain `running` cells (two refer to the same OKVIS2-X cell).
They are stale state records, not evidence that computation is continuing. State files were
not rewritten as part of this documentation audit.

| State directory under `logs/server-campaign/` | Recorded cell states |
|---|---|
| `quality-final-n3-no-gnss` | 23 failed, 177 ok |
| `quality-n3-recovery-01-rosario-vo` | 2 failed, 2 ok |
| `quality-n3-recovery-02-hortimulti-vo` | 1 failed |
| `quality-n3-recovery-03-rosario-sequence1-vo-lc` | 1 failed |
| `quality-n3-recovery-04-rosario-sequence5-vo-lc` | 1 ok |
| `quality-n3-recovery-05-zed2i-vo-lc` | 1 failed, 1 running |
| `quality-n3-recovery-05b-okvis2-vo-lc-all` | 7 ok, 1 running |
| `quality-n3-recovery-05c-zed2i-okvis2x-vo-lc` | 1 running |
| `zed2i-imu-recalibration-n1` | 2 failed, 9 ok |

These campaign counts overlap and must not be summed. The current result inventory above
supersedes old scheduler success counts after a cell has been replaced.

The September 23 OKVIS2 VO-LC recovery completed N=3 on all seven non-ZED sequences. On ZED, run1 finished with exit code 0, 46,282 output poses and
22,199.5 seconds of recorded runtime. Its trajectory and metadata exist, but it has no
`run_eval.json` or `COMPLETE`. Run2's log ends in `Killed` on September 24. Determine the
termination cause from system evidence; the text alone does not establish OOM.
Preserve and evaluate run1 before scheduling replacement work. The wrapper currently runs
all N repetitions before evaluating any of them, so a later failure can leave earlier output
unscored. It also replaces the whole cell on launch; a naive N=3 restart would erase run1.

ZED OKVIS2-X VO-LC has no evaluated repetition; its latest recovery log stops shortly after
initialization. ORB-SLAM3 lacks the three agricultural VO cells, Rosario sequence1 VO-LC,
and both ZED IMU modes listed above. Recovery logs record native crashes; fixes require
qualification before another broad run batch.

OpenVINS is the largest core gap: seven non-ZED cells retain only one evaluated run total
(MH05 run1). For example, Rosario sequence1's campaign log records a trajectory export
followed by a Python/player shutdown abort (exit 134). Separate wrapper/shutdown problems
from estimator tracking failure and inspect recoverable outputs. The modified player and
MH05 N=1 recovery are not evidence that all missing cells have been rerun.

## Corrected ZED IMU cohort

The September 16 recalibration campaign attempted all 11 VIO/VIO-LC cells: nine completed,
two ORB-SLAM3 cells failed. Of the nine evaluated repetitions, eight are `ok` and OpenVINS
VIO is `scale_collapse`. All are N=1 in the current result tree. The earlier blanket claim
that every current ZED VIO artifact uses the identity optical/IMU transform is obsolete.
The serial-specific residual camera–IMU rotation and timing qualification remain open;
see [the calibration record](../zed2i-imu-extrinsics.md).

## Configuration and provenance decisions

- Basalt VO Rosario sequence1/sequence5 were recovered using a triangulation threshold
  of 0.03. The other six VO cells retain 0.05 in their saved configuration; the current
  shared `configs/basalt/vo_config.json` is 0.03. All six have N=3, but a uniform configuration
  claim needs an explicit cohort decision and appropriate reruns. Their completion does
  not imply that they match today's config.
- Basalt ZED VO also snapshots the earlier calibration. It shares a calibration file with
  VIO, so check exported pose-frame handling before asserting VO is unaffected by the edit.
- AirSLAM ZED VO/VO-LC camera-config hash differences inspected here are comment-only;
  these do not by themselves justify rerunning those cells.
- OKVIS2 VO-LC's seven recovered N=3 cells use the later full-BA-disabled configuration.
  Record that setting and compare it with the OKVIS2-X cohort before attributing differences
  solely to algorithm choice. Loop closure and final full BA are different settings.
- Generated temporary config filenames vary across ORB-SLAM3 and MAC-VO repetitions.
  Compare normalized effective contents, not temporary filenames, when testing equivalence.
- The worktree contains uncommitted runner, evaluator, calibration and submodule changes.
  Freeze the chosen configuration, source revisions/diffs and binary identities before the
  final campaign; do not imply that the last parent commit alone reproduces current runs.

## Exports and legacy GNSS

| Mode | Root CSV rows at audit | Current COMPLETE + evaluation artifacts |
|---|---:|---:|
| vo | 110 | 202 |
| vo-lc | 40 | 135 |
| vio | 55 | 134 |
| vio-lc | 28 | 87 |
| gnss-vio | 26 | 19 |

The root CSVs contain **259 rows**, whereas **577 complete evaluated artifacts** currently
exist across all modes. The latter include 15 historical/out-of-scope DROID-SLAM runs and five smoke runs
under `euroc_mav/smoke_mh_01_easy_200` (VO: AirSLAM, OV2SLAM, ORB-SLAM3, DPVO; VIO:
OKVIS2). They are not 577 executions of the N=3 campaign. The CSV builder currently
accepts these smoke artifacts because they have COMPLETE markers. Quarantine or explicitly
exclude them before rebuilding headline exports; preserve their debugging evidence. There
are 584 evaluation JSONs in total, seven lacking COMPLETE (all in GNSS).
Generated tables and the browser have been built at different times; do not mix their counts
or treat them as an accepted final campaign. Neither the CSVs nor generated numeric reports
were rewritten during this documentation audit: the metric/reporting blockers below must be
resolved before their next publication refresh. The matrix here is the current completion record.

GNSS was excluded from the executed N=3 campaign. Its 19 complete artifacts are historical,
from the earlier machines: 16 default N=1 cells plus three conventional-GPS variants.
VINS-Fusion+GPS's four default cells have evaluation JSONs but no COMPLETE markers, as do
three additional GNSS variant directories. Investigate and validate them; do not manufacture
markers. The original 20-cell GNSS N=5 plan and corrected-extrinsic OpenVINS+GPS reruns
are not demonstrated complete by these legacy files.

## Work required before publication / adding algorithms

1. Preserve interrupted outputs and make campaign status agree with actual processes.
   Evaluate salvageable runs, then schedule the exact missing repetitions. Preserve crash,
   collapse and tracking-loss outcomes separately from infrastructure failures.
2. Resolve the Basalt cohort split and finish corrected ZED N=3 qualification. Decide and
   document whether N=3/no-GNSS is the final paper scope or whether N=5/GNSS remains required.
3. Fix or explicitly relabel the existing evaluation/reporting issues before refreshing results:
   - `make_report_tables.py` passes `ate_se3_rmse_m` for all headline rows while claiming
     DPVO uses Sim(3). The current main table therefore mislabels DPVO's metric.
   - Mixed-status cells are eligible whenever any status is `ok`; collapse/failure counts
     and repeat denominators must remain visible. Bolding is a heuristic, not significance.
   - `_evaluate_run.py` uses evo `point_distance`: absolute difference of displacement
     magnitudes, not relative-pose translation error. Its derived drift is not standard KITTI
     translational drift. Correct frame conventions before changing to full pose metrics.
   - Installed evo's `align_origin` applies rotation and translation from the first poses,
     not translation alone. Do not call it an unmodified global GNSS-frame error.
   - ZED GT has identity placeholder orientations: its rotational RPE is not a valid
     orientation accuracy measurement.
   - Coverage's threshold grows with the trajectory's own median sampling interval;
     very sparse outputs can bridge long gaps. Validate against a common time support.
   - GT interpolation and segmentation caches are reused by existence, not input hashes.
     Revisit the deferred segment-coalescing issue and cache freshness before re-evaluation.
   - `verify_claims.py` contains legacy fixed narrative and Sim(3)-based IMU comparisons;
     regeneration alone does not validate those conclusions or update timing semantics.
4. Exclude the five smoke artifacts from headline discovery without deleting evidence.
   Re-evaluate affected saved trajectories after metric fixes; regenerate all five CSVs,
   tables, claims, segment/comparison figures and browser together. Audit training/config
   provenance, failure rates and input/measurement regimes before interpreting rankings.
5. Produce the final thesis/LaTeX tables and a reproducible frozen experiment record.
   Only then expand the algorithm set. New algorithms and additional Rosario sequences
   are scope extensions, not requirements of the executed 200-cell manifest.

## Reproducing the count

Expand the saved N=3 manifest by `tables` × `sequences` (GNSS list is empty), then inspect
`results/<mode>/<dataset>/<sequence>/<algorithm>/run{1,2,3}/`. Count only a JSON with its
sibling COMPLETE marker; keep `run_status`, missing IDs and coverage alongside each count.
Do not count directories, old CSV rows, log start messages or scheduler `ok` entries as
current completed runs. Re-run the inventory after any cell replacement.
