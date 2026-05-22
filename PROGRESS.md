# vSLAM Benchmark - Progress

BSc thesis benchmarking five SLAM algorithms on agricultural datasets.
Algorithms: **ORB-SLAM3** (classical), **DROID-SLAM** (neural), **MAC-VO** (hybrid), **Basalt** (sliding-window VIO), **AirSLAM** (deep-feature VO, Docker).

---

## Results Summary

> All Rosario single-run results are from an earlier exploratory run (single run, old format).  
> HortiMulti Strawberry-03, Rosario seq1, and Rosario seq5 ORB-SLAM3 results are from the new **3-run multi-run benchmark** (mean ± std).
> HortiMulti Strawberry-02 MAC-VO, Strawberry-03 MAC-VO, and Rosario seq1 MAC-VO are also 3-run complete.
> All 4 sequences are now **Basalt 3-run complete** (strawberry02, strawberry03, seq1, seq5).
> **AirSLAM**: Strawberry-03 + Strawberry-02 3-run complete; Rosario seq1 **DONE** (9.888 ± 0.059 m, 100%); seq5 **DONE** (12.722 ± 0.991 m, 100%).
> Both **Sim(3)** and **SE(3)** ATE reported - see "Sim3 vs SE3" section below.

| Algorithm | Dataset | Seq | ATE Sim3 | ATE SE3 | Scale | Frames | Completion | Runs |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | Rosario v2 | seq1 | **1.176 ± 0.317 m** | **1.59 m** | 1.022 | 13 821 | 100% | **3** ✓ |
| DROID-SLAM | Rosario v2 | seq1 | 45.00 m | - | - | 6 911 | 100% (stride=2) | 1 |
| MAC-VO | Rosario v2 | seq1 | **13.520 ± 0.007 m** | **13.552 ± 0.007 m** | 0.980 | 13 821 | 100% | **3** ✓ |
| Basalt | Rosario v2 | seq1 | **14.279 ± 0.302 m** | **18.693 ± 0.586 m** | 0.791 | 13 821 | 100% | **3** ✓ |
| AirSLAM | Rosario v2 | seq1 | **9.888 ± 0.059 m** | **9.891 ± 0.058 m** | 1.005 | 13 821 | 100% | **3** ✓ |
| ORB-SLAM3 | Rosario v2 | seq5 | **20.207 ± 4.204 m** | **20.85 m** | 0.904 | 11 640 | 91% avg (0 loops) | **3** ✓ |
| DROID-SLAM | Rosario v2 | seq5 | 50.13 m | - | - | 11 640 | 100% (external‡) | 1 |
| MAC-VO | Rosario v2 | seq5 | 19.381 m | - | - | 11 640 | 100% | 1 |
| Basalt | Rosario v2 | seq5 | **15.035 ± 0.062 m** | **15.425 ± 0.068 m** | 0.934 | 11 640 | 100% | **3** ✓ |
| AirSLAM | Rosario v2 | seq5 | **12.722 ± 0.991 m** | **12.777 ± 1.014 m** | 0.977 | 11 640 | 100% | **3** ✓ |
| ORB-SLAM3 | HortiMulti | Strawberry-02 | **0.893 ± 0.171 m** | **2.10 ± 0.12 m** | 1.040 | 4 186–4 980 / 9 530 | 44–52%† | **3** ✓ |
| DROID-SLAM | HortiMulti | Strawberry-02 | 44.91 m | - | - | 4 765 | 100% (stride=2) | 1 |
| MAC-VO | HortiMulti | Strawberry-02 | **10.231 ± 0.502 m** | **10.940 ± 0.545 m** | 1.009 | 9 530 | 100% | **3** ✓ |
| Basalt | HortiMulti | Strawberry-02 | **2.0978 ± 0.0008 m** | **2.664 ± 0.001 m** | 1.034 | 9 530 | 100% | **3** ✓ |
| AirSLAM | HortiMulti | Strawberry-02 | **20.220 ± 0.824 m** | **20.483 ± 0.893 m** | 0.928 | 9 530 | 100% | **3** ✓ |
| ORB-SLAM3 | HortiMulti | Strawberry-03 | **0.1039 ± 0.0013 m** | **0.78 m** | 1.043 | 2 425 | 100% | **3** ✓ |
| MAC-VO | HortiMulti | Strawberry-03 | **0.505 ± 0.010 m** | **0.84 m** | 1.037 | 2 425 | 100% | **3** ✓ |
| Basalt | HortiMulti | Strawberry-03 | **0.2753 ± 0.0000 m** | **0.7151 m** | 1.036 | 2 425 | 100% | **3** ✓ |
| AirSLAM | HortiMulti | Strawberry-03 | **3.631 ± 0.205 m** | **3.771 ± 0.191 m** | 1.064 | 2 425 | 100% | **3** ✓ |

### [NON-AGRICULTURAL REFERENCE] EuRoC-MAV (single-run comparison)

| Sequence | Algorithm | ATE Sim3 [m] | ATE SE3 [m] | RPE [m/m] | Scale | FPS | Frames |
|---|---|---|---|---|---|---|---|
| MH_01_easy | ORB-SLAM3 | 0.0340 | 0.0352 | 0.0156 | 1.0021 | 18.17 | 3682 |
| MH_01_easy | Basalt | 0.0567 | 0.0873 | 0.0085 | 1.0156 | 176.75 | 3682 |
| MH_01_easy | AirSLAM | 0.1107 | 0.1156 | 0.0195 | 1.0073 | 15.33 | 3682 |
| MH_01_easy | MAC-VO | 0.1981 | 0.1993 | 0.0295 | 1.0051 | 1.29 | 3682 |
| MH_03_medium | ORB-SLAM3 | 0.0437 | 0.0520 | 0.0179 | 0.9922 | 17.89 | 2700 |
| MH_03_medium | Basalt | 0.1372 | 0.1397 | 0.0159 | 1.0075 | 113.47 | 2700 |
| MH_03_medium | AirSLAM | 0.1431 | 0.1443 | 0.0188 | 0.9950 | 31.73 | 2700 |
| MH_03_medium | MAC-VO | 0.3403 | 0.3405 | 0.0187 | 0.9961 | 1.15 | 2700 |
| MH_05_difficult | ORB-SLAM3 | 0.0720 | 0.0781 | 0.2282 | 0.9956 | 17.97 | 2273 |
| MH_05_difficult | Basalt | 0.1816 | 0.1931 | 0.0870 | 1.0097 | 108.72 | 2273 |
| MH_05_difficult | AirSLAM | 0.2968 | 0.3066 | 0.0256 | 1.0116 | 34.92 | 2273 |
| MH_05_difficult | MAC-VO | 0.4697 | 0.4836 | 0.0276 | 1.0172 | 0.86 | 2273 |

† ORB-SLAM3 processed all 9 530 input frames but tracking only succeeded for frames
spanning 91 s – 500 s of the 952 s sequence.  Tracking was permanently lost after 500 s
due to the repetitive polytunnel environment.  This is **not** a stride/sampling issue.  
‡ DROID-SLAM sequence5 trajectory provided by collaborator; original ns timestamps converted to seconds for evaluation.

All multi-run metrics use **both Sim(3) and SE(3)** alignment (`evo_ape --align [--correct_scale]`) and
**`point_distance` RPE** (not `trans_part` - avoids body-frame quaternion mismatch).

---

## Sim(3) vs SE(3) alignment for stereo - critical finding

Stereo SLAM has **metric scale** (from the baseline), so SE(3) ATE is the
honest accuracy metric. Sim(3) absorbs residual scale drift into a 7th DoF
alignment scale factor, hiding error. We now report **both**:

| Sequence | Sim3 ATE | SE3 ATE | Scale | Scale drift |
|---|---|---|---|---|
| Rosario seq1 | 1.18 m | 1.59 m | 1.022 | 2.2 % |
| Rosario seq5 | 20.21 m | 20.85 m | 0.904 | 10 % |
| Strawberry-02 | 0.89 m | 2.10 m | 1.040 | 4.0 % |
| **Strawberry-03** | **0.10 m** | **0.78 m** | **1.043** | **4.3 %** |

The Strawberry-03 case is instructive: the "0.10 m" headline number masks a
~8× larger real metric error because Sim(3) absorbs the scale drift. We now
report SE(3) ATE alongside Sim(3) in every `report.md`.

---

## RPE rotation anomaly on HortiMulti (Strawberry-03 17.6 °/m) - resolved as artefact

ORB-SLAM3 outputs poses in the **camera optical frame**; HortiMulti GT is in a
**robot base frame** rotated by a near-constant **≈120°** mount offset. Sim3/SE3
translation alignment does not fix per-frame body orientation. The constant
mismatch makes `R_gt_rel · R_est_rel⁻¹` non-cancelling whenever the body
rotation axis is not aligned with the mismatch axis.

Diagnostic measurement on Strawberry-03 run1:
- Per-frame abs orientation diff: **mean 119.46°, median 119.40°, range 116–120°** (constant)
- Manual RPE rot (1 m windows): mean 13.7°, **median only 3.45°**, RMSE 26.2°
- Distribution is heavy-tailed because high errors occur only on certain body axes

**Conclusion:** RPE rotation = 17.6 °/m on Strawberry-03 is a frame-mismatch
artefact, NOT an ORB-SLAM3 accuracy issue. Documented in
`docs/evalutation/10_evaluation_protocol.md` §14. Future work: pre-multiply
estimate by a learned constant $R_0$ before RPE rotation evaluation.

---

## Infrastructure - Complete

- ORB-SLAM3 built and patched (`src/ORB_SLAM3/`)
- DROID-SLAM conda env `droidenv` with pretrained weights (`droid.pth`)
- MAC-VO conda env `macvo` with FlowFormer weights
- Evaluation toolkit `evo` installed in `macvo` env
- Basalt binary v0.1.7 installed (`~/.local/bin/basalt_vio`, sourced via `~/.basalt/env`)
- **AirSLAM** Docker container (`air_slam`, image `xukuanhit/air_slam:v4`); catkin_make built inside container; TRT engine compiled for hortimulti (640×480); TRT engine for rosariov2 (1280×720) compiled on first seq1 run
- Run scripts: `scripts/run/run_orbslam3.sh` (multi-run, resource monitor), `run_droidslam.sh` (multi-run ✓), `run_macvo.sh` (multi-run ✓), `run_basalt.sh` (single-run ✓), `run_airslam.sh` (multi-run ✓ — polls `trajectory_v0.txt`, pkill roslaunch, `mv -f`, FPS from input frames)
- Resource monitoring: `scripts/run/_resource_monitor.py` (GPU+CPU+RAM every 1 s)
- GT interpolation: `scripts/eval/_interpolate_gt.py` (Slerp + linear, to exact camera timestamps)
- Auto-segmentation: `scripts/eval/_segment_trajectory.py` (**v2: 2 m sliding window of path length, 10° heading & 20 cm chord-deviation cap**)
- Per-run evaluation: `scripts/eval/_evaluate_run.py` → `run_eval.json` (ATE Sim3+SE3, RPE, KITTI, segments)
- Aggregation: `scripts/eval/_aggregate_runs.py` → `metrics.csv` + `report.md` (Sim3 + SE3 columns, alignment notes)
- Visualisation: `scripts/eval/_plot_segments.py` (**v2: 8 K resolution; 3 hierarchies - per-run, per-algo, per-sequence cross-algo; legend outside path**)
- Deprecated scripts removed: `aggregate_results.py`, `evaluate_all.sh`, `_gpu_monitor.sh`, `_rosario_extract.py`, `run_all_on_sequence.sh`
- Documentation updated: `10_evaluation_protocol.md` (RPE metric fix, multi-run workflow, segment ATE note), `11_running_experiments.md` (full multi-run recipe), `12_thesis_deliverables.md` (table format), `00_overview.md` (scripts tree), `dataset_rosario_v2.md` (benchmark workflow + results section), `dataset_hortimulti.md` (str03 3-run results)

---

## Dataset 1 - Rosario v2 - In progress

### Sequence 1 - ORB-SLAM3 × 3 benchmark complete ✓

- **Results in:** `results/rosariov2/sequence1/orbslam3/` - `metrics.csv`, `report.md`, `segment_map.png`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE | **1.176 ± 0.317 m** |
| RPE (point\_distance, 1 m) | 0.115 ± 0.104 m (high var due to tracking-loss reloc boundary) |
| RPE rotation | 0.416 ± 0.139 °/m |
| KITTI drift @ 50 m | 0.429 ± 0.044 m |
| Scale factor | 1.022 ± 0.001 |
| Frames tracked | 100% all 3 runs (tracking-loss + reloc ~t=645s) |
| Loop closures | 5–6 |
| Mean FPS | 12.53 ± 0.14 (0.84× real-time @ 15 fps) |
| Row ATE RMSE (125 segs, avg 6.9 s) | 0.016 ± 0.003 m |
| Turn ATE RMSE (20 segs, avg 3.0 s) | 0.022 ± 0.003 m |

> High ATE variation (0.79–1.57 m across 3 runs) is expected: loop closure timing nondeterminism
> causes different GBA corrections. Per-segment ATE is more stable (cv < 20%).
> Run2 RPE outlier (0.261 vs 0.029–0.055) caused by trajectory discontinuity at reloc boundary.

### Sequence 1 - ORB-SLAM3 × 3 + MAC-VO × 3 complete

- **Extracted to:** `datasets/rosariov2/sequence1/`
- **GT:** 8983 poses (GPS/PGT), 13821 camera frames; `gt_interp_tum.txt` generated✔
- **Segments:** 125 row segs (863 s), 20 turn segs (60 s) - `segments_auto.csv` generated✔
- **Config files:** ORB-SLAM3: `configs/orbslam3/rosariov2_stereo.yaml` · DROID-SLAM: `configs/droidslam/rosariov2.txt` · MAC-VO: `configs/macvo/rosariov2_sequence1.yaml`

| Algorithm | ATE RMSE Sim3 | Frames | Completion | Runs |
|---|---|---|---|---|
| ORB-SLAM3 | **1.176 ± 0.317 m** | 13 821 | 100% | **3** ✓ |
| DROID-SLAM | 45.00 m | 6 911 | 100% (stride=2) | 1 |
| MAC-VO | **13.520 ± 0.007 m** | 13 821 | 100% | **3** ✓ |
| Basalt | **14.279 ± 0.302 m** | 13 821 | 100% | **3** ✓ |
| AirSLAM | **9.888 ± 0.059 m** | 13 821 | 100% | **3** ✓ |
#### MAC-VO × 3 - Sequence 1 complete

> Full report: `results/rosariov2/sequence1/macvo/report.md`

#### Basalt × 3 - Sequence 1 complete

> Full report: `results/rosariov2/sequence1/basalt/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **14.279 ± 0.302 m** |
| ATE RMSE SE3 | **18.693 ± 0.586 m** |
| RPE (point\_distance, 1 m) | 1.6454 ± 0.0398 m/m |
| RPE rotation | 0.535 ± 0.013 °/m |
| Scale factor (Sim3) | 0.791 ± 0.008 (**20.9 % drift**) |
| Frames tracked | 100% (13 821 / 13 821, 0 losses, all 3 runs) |
| Mean FPS | 59.44 ± 3.61 (4.0x real-time @ 15 fps) |
| Row ATE RMSE (73 segs) | 0.0140 ± 0.0000 m |
| Turn ATE RMSE (34 segs) | 0.1609 ± 0.0003 m |

> Global ATE 14.3 m vs local row ATE 14 mm - a 1021x ratio, driven by scale drift (scale=0.79).
> Without scale correction (SE3 ATE = 18.7 m) the drift is even more pronounced.
> Local accuracy (row ATE 14 mm) is comparable to ORB-SLAM3 (16 mm) and MAC-VO (20 mm),
> confirming that Basalt tracks accurately per-frame but accumulates large global scale error
> on this long outdoor sequence (~940 m trajectory) without loop closure.
> Runs 2 and 3 nearly identical (ATE 14.04 vs 14.09 m); run1 slightly higher (14.70 m) due to
> multi-threaded input timing variation at startup.

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **13.520 ± 0.007 m** |
| ATE RMSE SE3  | **13.552 ± 0.007 m** |
| RPE (point\_distance, 1 m) | 0.0508 ± 0.0001 m/m |
| Scale factor | 0.980 ± 0.000 (**2.0 % drift**) |
| Frames tracked | 100% (13 821 / 13 821, all 3 runs) |
| Mean FPS | 1.71 ± 0.08 (0.11x real-time @ 15 fps) |
| Row ATE RMSE (73 segs) | 0.0200 ± 0.0000 m |
| Turn ATE RMSE (34 segs) | 0.0174 ± 0.0000 m |

> Exceptionally stable across runs: ATE std only 7 mm over 13821 frames.
> Global ATE (~13.5 m) vs local row ATE (20 mm) - 675x ratio, driven by
> accumulated scale drift. Compare ORB-SLAM3 on same sequence: 1.18 m global
> ATE thanks to 5-6 loop closures correcting drift. MAC-VO has no loop closure.

#### AirSLAM × 3 - Sequence 1 complete ✓

> Full report: `results/rosariov2/sequence1/airslam/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **9.888 ± 0.059 m** |
| ATE RMSE SE3 | **9.891 ± 0.058 m** |
| RPE (point\_distance, 1 m) | 0.0342 m |
| Scale factor (Sim3) | 1.0052 ± 0.0003 (**0.52% drift**) |
| Frames tracked | 100% (13 821 / 13 821, 0 losses, all 3 runs) |
| Loop closures | 0 (all 3 runs) |
| Mean FPS | 23.04 ± 3.61 (wall-clock) |
| Row ATE RMSE | 0.0192 m |
| Turn ATE RMSE | 0.0185 m |

> Near-unity scale (1.005) confirms AirSLAM maintains correct metric scale on this sequence.
> No loop closures needed — direct scale preservation. Global ATE ~9.9 m over ~940 m trajectory
> (1.05% of path length). Comparable to MAC-VO (13.5 m) and Basalt (14.3 m).
> Individual runs: run1=9.958 m (17.98 fps), run2=9.814 m (24.98 fps), run3=9.893 m (26.17 fps).
> High wall-time variance (run1=769s vs run2+3≈540s) due to TRT engine compilation on run1.

#### AirSLAM × 3 - Sequence 5 complete ✓

> Full report: `results/rosariov2/sequence5/airslam/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **12.722 ± 0.991 m** |
| ATE RMSE SE3 | **12.777 ± 1.014 m** |
| RPE (point\_distance, 1 m) | 0.0552 ± 0.0063 m/m |
| RPE rotation | 0.299 ± 0.001 °/m |
| Scale factor (Sim3) | 0.9765 ± 0.0057 (**2.4% drift**) |
| Frames tracked | 100% (11 640 / 11 640, 0 losses, all 3 runs) |
| Loop closures | 0 (all 3 runs) |
| Mean FPS | 23.74 ± 0.48 (wall-clock) |
| Row ATE RMSE | 0.0470 ± 0.0022 m (34 segs) |
| Turn ATE RMSE | 0.0106 ± 0.0001 m (18 segs) |

> Scale factor 0.977 (2.4% drift) is slightly worse than seq1 (1.005, 0.5% drift).
> Global ATE 12.7 m vs local row ATE 47 mm — 270× ratio showing long-range scale accumulation.
> No loop closures detected on all 3 runs. Run3 significantly higher ATE (14.12 m) vs run1+2 (~12 m),
> causing higher std (0.99 m) than other seqs.
> Individual runs: run1=12.114 m (23.82 fps), run2=11.932 m (23.13 fps), run3=14.119 m (24.29 fps).

### Sequence 5 - ORB-SLAM3 × 3 benchmark complete ✓

- **Sequence:** 11 640 frames, 1280×720, ~13 min, stereo + PGT GT
- **Extracted to:** `datasets/rosariov2/sequence5/`
- **GT:** 7577 poses; `gt_interp_tum.txt` generated ✔
- **Segments:** 95 row segs (756 s), 6 turn segs (19 s) - `segments_auto.csv` generated ✔
- **Results in:** `results/rosariov2/sequence5/orbslam3/` - `metrics.csv`, `report.md`, `segment_map.png`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE | **20.207 ± 4.204 m** |
| RPE (point\_distance, 1 m) | 0.140 ± 0.062 m |
| RPE rotation | 0.273 ± 0.031 °/m |
| KITTI drift @ 50 m | 6.063 ± 2.532 m |
| Scale factor | 0.904 ± 0.047 |
| Frames tracked | 91.0 ± 12.7% (run2: 73.1% permanent failure at t≈683s) |
| Loop closures | 0 (all 3 runs) |
| Mean FPS | 11.28 ± 1.56 |
| Row ATE RMSE (~86 segs, avg 8.0 s) | 0.016 ± 0.000 m |
| Turn ATE RMSE (~5 segs, avg 3.3 s) | 0.014 ± 0.003 m |

> Key finding: 0 loop closures → scale drift accumulates over 160 m of straight rows.
> Global ATE 20 m vs local segment ATE 0.016 m - a 1250× ratio.
> Contrast with seq1: 5-6 loop closures → ATE only 1.18 m on a similar-length sequence.

| Algorithm | ATE RMSE | Frames | Completion | Runs |
|---|---|---|---|---|
| ORB-SLAM3 | **20.207 ± 4.204 m** | 11 640 | 91% avg | **3** ✓ |
| DROID-SLAM | **50.13 m** | 11 640 | 100% (external‡) | 1 |
| MAC-VO | **19.381 m** | 11 640 | 100% | 1 |
| Basalt | **15.035 ± 0.062 m** | 11 640 | 100% | **3** ✓ |
| AirSLAM | **12.722 ± 0.991 m** | 11 640 | 100% | **3** ✓ |

‡ Timestamps were in nanoseconds - converted to seconds before evaluation.

#### Basalt × 3 - Sequence 5 complete

> Full report: `results/rosariov2/sequence5/basalt/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **15.035 ± 0.062 m** |
| ATE RMSE SE3 | **15.425 ± 0.068 m** |
| RPE (point\_distance, 1 m) | 0.8021 ± 0.0005 m/m |
| RPE rotation | 0.2797 ± 0.0009 °/m |
| Scale factor (Sim3) | 0.9339 ± 0.0007 (**6.6 % drift**) |
| Frames tracked | 100% (11 640 / 11 640, 0 losses, all 3 runs) |
| Mean FPS | 64.60 ± 2.30 (4.3x real-time @ 15 fps) |
| Row ATE RMSE (34 segs) | 0.0211 ± 0.0001 m |
| Turn ATE RMSE (19 segs) | 0.0911 ± 0.0000 m |

> Better scale than seq1 (0.934 vs 0.791): different route geometry reduces cumulative drift.
> Local row ATE 21 mm is close to ORB-SLAM3 seq5 row ATE (16 mm).
> Global ATE 15.0 m reflects uncorrected scale drift over the full sequence without loop closure.
> Near-symmetric Sim3/SE3 ATEs (15.0 m vs 15.4 m) indicate small scale drift relative to seq1 (14.3 vs 18.7 m).

### Rosario v2 observations (updated with 3-run benchmarks)
- ORB-SLAM3 seq1: 1.176 m - 5-6 loop closures enable global correction → low drift
- ORB-SLAM3 seq5: 20.207 m - 0 loop closures, long straight rows → uncorrected scale drift
- DROID-SLAM consistently very poor (~45 m both seqs)
- MAC-VO seq1: 13.520 ± 0.007 m (3 runs) - no loop closure, scale drift 2%; local row ATE 0.020 m
- MAC-VO seq5: 19.381 m (1 run, run2+3 pending)
- Basalt seq1: 14.279 ± 0.302 m (3 runs) - scale drift 20.9%; local row ATE 14 mm (matches ORB-SLAM3)
- Basalt seq5: 15.035 ± 0.062 m (3 runs) - scale drift 6.6%; better than seq1 due to route geometry
- AirSLAM seq1: **DONE** (9.888 ± 0.059 m Sim3, 100% tracking, scale=1.005, 23.04 fps)
- AirSLAM seq5: **DONE** (12.722 ± 0.991 m Sim3, 100% tracking, scale=0.977, 23.74 fps)
- **Local accuracy is similar for all algorithms**: row ATE 0.016-0.021 m for ORB-SLAM3, MAC-VO, and Basalt on seq1/seq5

---

## Dataset 2 - HortiMulti - In progress

 - ORB-SLAM3 × 3 + MAC-VO × 3 + Basalt × 3 + AirSLAM × 3 complete on all sequences; Rosario seq1 + seq5 **done**

- **Sequence:** Feb2026, 9530 frames, 952 s, 41 GB bag
- **Camera:** Basler acA1920-155uc, fisheye (equidistant) distortion, 2048×1536 native
- **Extracted to:** `datasets/hortimulti/strawberry02/` - 9530 stereo pairs at 640×480
- **Results in:** `results/hortimulti/strawberry02/`

#### ORB-SLAM3 × 3 benchmark (Phase B, current)

> Full report: `results/hortimulti/strawberry02/orbslam3/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim(3) | **0.893 ± 0.171 m** |
| ATE RMSE SE(3)  | **2.103 ± 0.118 m** |
| RPE (point_distance, 1 m) | 0.0716 ± 0.0008 m |
| RPE rotation (1 m) | 10.56 ± 1.11 °/m (frame-mismatch artefact - see §RPE rotation) |
| Scale factor (Sim3) | 1.040 ± 0.001 (**4 % drift**) |
| Frames tracked | 4 186 / 4 441 / 4 980 of 9 530 → **44–52 % timeline coverage** |
| Loop closures | 0 (all 3 runs) |
| Tracking losses | 0 hard losses; Atlas Map 2 created at t≈541 s every run |
| Wall-clock per run | ~1 005 s (≈ real-time at 10 Hz input) |
| Row ATE RMSE | 0.0845 ± 0.0064 m (~9 segs/run, avg ~50 s) |
| Turn ATE RMSE | 0.0665 ± 0.0038 m (~5 segs/run, avg ~12 s) |

> Strawberry-02 is significantly harder than Strawberry-03: tracking dies
> permanently around 541 s of the 952 s sequence due to the repetitive
> polytunnel imagery (every run reproduces this). Sim3 hides 4 % scale drift;
> SE3 ATE is **2.36× larger** (0.89 → 2.10 m). No loop closures means the
> drift is uncorrected.

| Algorithm | ATE RMSE Sim3 | Frames | Completion | Runs |
|---|---|---|---|---|
| ORB-SLAM3 (old) | 0.866 m | 4 105 / 9 530 | 43% of timeline | 1 |
| **ORB-SLAM3 × 3** | **0.893 ± 0.171 m** (SE3 2.10 ± 0.12) | 4 186-4 980 | 44-52% timeline | **3** ✓ |
| DROID-SLAM | 44.91 m | 4 765 | 100% (stride=2) | 1 |
| MAC-VO | **10.231 ± 0.502 m** | 9 530 | 100% | **3** ✓ |
| Basalt | **2.0978 ± 0.0008 m** | 9 530 | 100% | **3** ✓ |
| AirSLAM | **20.220 ± 0.824 m** | 9 530 | **100%** | **3** ✓ |

#### MAC-VO × 3 - Strawberry-02 complete

> Full report: `results/hortimulti/strawberry02/macvo/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **10.231 ± 0.502 m** |
| ATE RMSE SE3  | **10.940 ± 0.545 m** |
| RPE (point\_distance, 1 m) | 0.0960 ± 0.0012 m/m |
| Scale factor | 1.009 ± 0.003 (**0.9 % drift**) |
| Frames tracked | 100% (9 530 / 9 530, all 3 runs) |
| Mean FPS | 1.70 ± 0.04 (0.17x real-time @ 10 fps) |
| Row ATE RMSE (16 segs) | 0.587 ± 0.008 m |
| Turn ATE RMSE (9 segs) | 0.0845 ± 0.0001 m |

> MAC-VO tracks 100% of frames (vs ORB-SLAM3 44-52%) at the cost of ~6x lower
> speed. Global ATE (~10 m over 952 s) reflects scale drift on the much longer
> sequence; scale factor is near 1.0 (only 0.9% drift) so Sim3 and SE3 ATEs
> converge. Turn ATE (0.085 m) is tighter than row ATE (0.587 m) as expected.

#### Basalt × 3 - Strawberry-02 complete

> Full report: `results/hortimulti/strawberry02/basalt/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **2.0978 ± 0.0008 m** |
| ATE RMSE SE3 | **2.664 ± 0.001 m** |
| RPE (point\_distance, 1 m) | 0.0910 ± 0.0000 m/m |
| RPE rotation | 10.966 ± 0.000 °/m (frame-mismatch artefact) |
| Scale factor (Sim3) | 1.034 (**3.4 % drift**) |
| Frames tracked | 100% (9 530 / 9 530, 0 losses, all 3 runs) |
| Mean FPS | 149.70 ± 4.01 (15.0x real-time @ 10 fps) |
| Row ATE RMSE (16 segs) | 0.1366 ± 0.0000 m |
| Turn ATE RMSE (9 segs) | 0.0806 ± 0.0000 m |

> Unlike ORB-SLAM3 (44-52% timeline coverage), Basalt tracks 100% of the 952 s sequence.
> Global ATE 2.10 m vs ORB-SLAM3 0.89 m Sim3 - but ORB-SLAM3 only covers half the trajectory.
> Scale drift only 3.4% (Sim3 ATE 2.10 m vs SE3 ATE 2.66 m - 1.27x ratio).
> Local row ATE 137 mm is larger than str03 (27 mm) due to the longer, more repetitive sequence.
> Perfectly deterministic across 3 runs: ATE std = 0.8 mm.

#### AirSLAM × 3 - Strawberry-02 complete

> Full report: `results/hortimulti/strawberry02/airslam/report.md`

| Metric | Value (mean ± std, N=3) |
|---|---|
| ATE RMSE Sim(3) [m] | **20.220 ± 0.824** |
| ATE RMSE SE(3) [m]  | **20.483 ± 0.893** |
| RPE (point_distance, 1 m) [m] | 0.2662 ± 0.0152 |
| RPE rotation (1 m) [°/m] | 13.94 ± 0.27 |
| Scale factor (Sim3) | 0.9278 ± 0.0103 (**7.2 % under-scale**) |
| Frames tracked | 9 530 / 9 530 → **100 %** (all 3 runs) |
| Keyframes per run | 1 938 |
| Tracking losses / loop closures | 0 / 0 |
| Wall-clock [s] | 348 / 343 / 353 |
| FPS (wall-clock) | **27.37 ± 0.32** |
| VRAM mean / peak [MiB] | 2 994 / 3 061 |
| Final drift [m] | 71.43 ± 6.39 |
| Row ATE RMSE (15 segs) | 0.3977 ± 0.0060 m |
| Turn ATE RMSE (7 segs) | 0.1163 ± 0.0004 m |

> AirSLAM achieves 100% tracking on the full 952 s sequence (no loop closure needed for tracking),
> but without global optimization drifts to 20.22 m global ATE (significantly worse than ORB-SLAM3's
> 0.89 m on 44–52% coverage, or Basalt's 2.10 m on 100%). Under-scale 7.2% contributes to SE3 ≈ Sim3.

### Strawberry-03 - ORB-SLAM3 × 3 + MAC-VO × 3 + Basalt × 3 complete

- **Sequence:** Feb2026, 2425 frames, 242 s, 11 GB bag
- **Extracted to:** `datasets/hortimulti/strawberry03/` - 2425 stereo pairs at 640×480
- **Results in:** `results/hortimulti/strawberry03/orbslam3/` + `results/hortimulti/strawberry03/macvo/` - 3 runs each, `metrics.csv`, `report.md`, `segment_map.png`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE | **0.1039 ± 0.0013 m** |
| RPE (point\_distance, 1 m) | **0.0226 ± 0.0006 m** |
| RPE rotation | 17.62 ± 0.06 °/m |
| KITTI drift @ 10 m | 0.051 ± 0.001 m |
| KITTI drift @ 50 m | 0.148 ± 0.004 m |
| KITTI drift @ 100 m | 0.004 ± 0.003 m |
| Scale factor (Sim3) | 1.0428 ± 0.0002 |
| Frames tracked | 100% (0 losses, 1 loop closure) |
| Mean FPS | 9.39 ± 0.05 (0.94× real-time @ 10 fps) |
| Row ATE RMSE (8 segs, avg 28 s) | 0.030 ± 0.001 m |
| Turn ATE RMSE (4 segs, avg 4.4 s) | 0.012 ± 0.0001 m |

> **Turn ATE < Row ATE** is expected: turns are 4-8 s vs rows 22-65 s.
> Shorter segments accumulate less drift and fit more tightly in per-segment Sim3 alignment.

#### MAC-VO × 3 - Strawberry-03 complete

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **0.505 ± 0.010 m** |
| ATE RMSE SE3  | **0.838 ± 0.008 m** |
| RPE (point\_distance, 1 m) | 0.0236 ± 0.0005 m/m |
| Scale factor | 1.037 ± 0.000 |
| Frames tracked | 100% (5 row segs, 5 turn segs) |
| Mean FPS | 1.54 ± 0.07 (0.154x real-time @ 10 fps) |
| Row ATE RMSE (5 segs) | 0.166 ± 0.001 m |
| Turn ATE RMSE (5 segs) | 0.031 ± 0.000 m |

> MAC-VO drift on rows (0.166 m) is ~5.5x the ORB-SLAM3 row ATE (0.030 m).
> Turn ATE (0.031 m) is comparable to ORB-SLAM3 (0.012 m × 2.5).
> Speed: 1.54 fps vs ORB-SLAM3 9.39 fps - ~6x slower.

#### Basalt × 3 - Strawberry-03 complete

> Full report: `results/hortimulti/strawberry03/basalt/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **0.2753 ± 0.0000 m** |
| ATE RMSE SE3 | **0.7151 m** |
| RPE (point\_distance, 1 m) | 0.0223 ± 0.0000 m/m |
| RPE rotation | 17.605 ± 0.000 °/m (frame-mismatch artefact) |
| Scale factor (Sim3) | 1.036 |
| Frames tracked | 100% (2 425 / 2 425, 0 losses, all 3 runs) |
| Mean FPS | 143.65 ± 24.16 (10.9-16.2x real-time @ 10 fps; varies with system load) |
| Row ATE RMSE (5 segs) | 0.0274 ± 0.0000 m |
| Turn ATE RMSE (5 segs) | 0.0280 ± 0.0000 m |

> Basalt sits between ORB-SLAM3 (0.10 m) and MAC-VO (0.505 m) on global ATE.
> RPE 22 mm/m and row ATE 27 mm are close to ORB-SLAM3 (RPE 22.6 mm, row 30 mm),
> confirming that Basalt's sliding-window optimizer matches ORB-SLAM3 local accuracy
> without loop closure. Speed: 143 fps mean - the fastest algorithm on this sequence.
> Perfectly deterministic (ATE std = 0.0000 m): all 3 runs produce identical trajectory to 4 decimal places.

| Algorithm | ATE RMSE Sim3 | ATE SE3 | Scale | FPS | Frames | Completion | Runs |
|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | **0.1039 ± 0.0013 m** | 0.78 m | 1.043 | 9.39 | 2 425 | **100%** | **3** ✓ |
| Basalt | **0.2753 ± 0.0000 m** | 0.72 m | 1.036 | 143.65 | 2 425 | **100%** | **3** ✓ |
| MAC-VO | **0.505 ± 0.010 m** | 0.84 m | 1.037 | 1.54 | 2 425 | **100%** | **3** ✓ |
| AirSLAM | **3.631 ± 0.205 m** | **3.771 ± 0.191 m** | 1.064 | 22.07 | 2 425 | **100%** | **3** ✓ |
| DROID-SLAM | TBD | - | - | - | - | - | - |

#### AirSLAM × 3 - Strawberry-03 complete

> Full report: `results/hortimulti/strawberry03/airslam/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **3.6314 ± 0.2047 m** |
| ATE RMSE SE3 | **3.7711 ± 0.1906 m** |
| RPE (point\_distance, 1 m) | 0.1350 ± 0.0052 m/m |
| RPE rotation | 19.514 ± 0.004 °/m (frame-mismatch artefact) |
| Scale factor (Sim3) | 1.0639 ± 0.0029 (**6.4 % drift**) |
| Frames tracked | 100% (2 425 / 2 425, 0 losses, all 3 runs) |
| Mean FPS | 22.07 ± 10.06 (run1: 7.83 fps incl. TRT compile; run2+3: 29.18 fps) |
| VRAM mean | 2841 MiB (3061 MiB peak) |
| Row ATE RMSE (5 segs, avg 34.7 s) | 0.2025 ± 0.0124 m |
| Turn ATE RMSE (4 segs, avg 16.0 s) | 0.0505 ± 0.0207 m |

> AirSLAM global ATE (3.63 m) is significantly higher than ORB-SLAM3 (0.10 m), Basalt (0.28 m),
> and MAC-VO (0.51 m) on this short sequence. 100% completion and 0 tracking losses, but large
> accumulated drift without loop closure. Run1 was slow (7.83 fps) due to TRT engine compilation;
> runs 2+3 run at 29.18 fps (~3x real-time at 10 fps input). Local turn ATE (50.5 mm) is
> reasonable; row ATE (202.5 mm) is ~7x worse than ORB-SLAM3 (30 mm).

### Config files

- ORB-SLAM3: `configs/orbslam3/hortimulti_stereo.yaml` (shared across all HortiMulti seqs)
- DROID-SLAM: `configs/droidslam/hortimulti.txt` (**no comments** - parser crashes on `#`)
- MAC-VO: `configs/macvo/hortimulti_sequence.yaml` (update `root:` path per sequence)

### HortiMulti observations

- ORB-SLAM3 best global accuracy on str03 (0.10 m Sim3); tracking lost on str02 after 44-52% of timeline (repetitive polytunnel)
- MAC-VO 100% completion on both sequences; ATE 10 m on str02 (long, ~953 s) vs 0.505 m on str03 (short, ~242 s) - drift scales with sequence length
- DROID-SLAM: 44.91 m on str02 (fresh eval, previously reported as 41.91 m with old eval)
- Basalt str03: 0.2753 ± 0.0000 m (3 runs, 143 fps, 100% tracking) - between ORB-SLAM3 and MAC-VO globally; local row ATE 27 mm matches ORB-SLAM3
- Basalt str02: 2.0978 ± 0.0008 m (3 runs, 150 fps, 100% tracking) - completes full sequence vs ORB-SLAM3 44-52% coverage
- AirSLAM str03: 3.6314 ± 0.2047 m (3 runs, 22 fps avg, 100% tracking) - highest global ATE on str03; 0 loop closures; local turn ATE 50 mm reasonable; run1 slow (TRT compile), run2+3 fast at 29 fps
- AirSLAM str02: **complete** (3.run, 20.22 ± 0.82 m, 100% tracking)

---

## Dataset 3 - LFSD - Not started

- Download and extract sequences
- Configure and run all three algorithms
- Evaluate ATE/RPE

---

## Dataset 4 - [NON-AGRICULTURAL REFERENCE] EuRoC-MAV

> **[NON-AGRICULTURAL REFERENCE]** EuRoC-MAV MH_01_easy was run once per
> algorithm (N=1, no stats) as a sanity check to confirm configs and the eval
> pipeline produce results consistent with the published literature.
> DROID-SLAM was not run (stereo-only check).

**Sequence:** MH_01_easy - 752x480, 20 fps, 3682 stereo frames, baseline 0.110 m, indoor MAV flight.

| Algorithm | ATE Sim3 [m] | ATE SE3 [m] | RPE [m/m] | Scale | FPS | Frames | Runs |
|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | **0.034** | **0.035** | 0.016 | 1.002 | 18.2 | 3682 / 3682 | 1 |
| Basalt | 0.057 | 0.087 | 0.009 | 1.016 | 176.8 | 3682 / 3682 | 1 |
| AirSLAM | 0.111 | 0.116 | 0.020 | 1.007 | 15.3 | 268 kf / 3682 input | 1 |
| MAC-VO | 0.198 | 0.199 | 0.030 | 1.005 | 1.3 | 3682 / 3682 | 1 |

> ORB-SLAM3 ATE 0.034 m matches published EuRoC results (~0.03-0.06 m on MH_01_easy).
> Basalt achieves the highest throughput (177 fps, 17.7x real-time).
> AirSLAM outputs keyframe-only poses (268 of 3682 input frames).

### ORB-SLAM3 - MH_01_easy complete

| Metric | Value |
|---|---|
| ATE RMSE Sim3 | **0.0340 m** |
| ATE RMSE SE3 | **0.0352 m** |
| RPE (point_distance, 1 m) | 0.0156 m/m |
| Scale factor | 1.002 |
| Frames tracked | 100% (3682 / 3682) |
| Loop closures | 0 |
| Wall time | 202.6 s |
| FPS | 18.17 |

### Basalt - MH_01_easy complete

| Metric | Value |
|---|---|
| ATE RMSE Sim3 | **0.0567 m** |
| ATE RMSE SE3 | **0.0873 m** |
| RPE (point_distance, 1 m) | 0.0085 m/m |
| Scale factor | 1.016 |
| Frames tracked | 100% (3682 / 3682) |
| Wall time | 20.8 s |
| FPS | 176.8 |

### AirSLAM - MH_01_easy complete

| Metric | Value |
|---|---|
| ATE RMSE Sim3 | **0.1107 m** |
| ATE RMSE SE3 | **0.1156 m** |
| RPE (point_distance, 1 m) | 0.0195 m/m |
| Scale factor | 1.007 |
| Frames tracked | 268 keyframe poses from 3682 input frames |
| Wall time | 240.2 s |
| FPS | 15.3 (input frames) |

### MAC-VO - MH_01_easy complete

| Metric | Value |
|---|---|
| ATE RMSE Sim3 | **0.1981 m** |
| ATE RMSE SE3 | **0.1993 m** |
| RPE (point_distance, 1 m) | 0.0295 m/m |
| Scale factor | 1.005 |
| Frames tracked | 100% (3682 / 3682) |
| Wall time | 2861.2 s |
| FPS | 1.287 |

> Segment maps generated at run-level, algo-level, and sequence-level under `results/euroc_mav/MH_01_easy/`.

---

## Pending work

| Task | Priority | Status |
|---|---|---|
| **AirSLAM × 3 on rosariov2/sequence1** | High | **DONE** (9.888 ± 0.059 m) |
| **AirSLAM × 3 on rosariov2/sequence5** | High | **DONE** (12.722 ± 0.991 m, 100% × 3) |
| **MAC-VO × 3 on Rosario seq5** - run1 done, run2+3 pending | High | Blocked (low priority) |
| **DROID-SLAM × 3 on all 4 evaluated sequences** | High | Not started |
| Segment maps for all 4 sequences with 5 algos | High | After AirSLAM rosariov2 completes |
| Rebuild benchmark.csv | High | After AirSLAM rosariov2 completes |
| Add Rosario v2 sequences 2, 3, 4 (already downloaded - TODO: extract + run) | Medium | Not started |
| LFSD dataset: download, extract, run, evaluate | Medium | Not started |
| Cross-sequence aggregation (`evo_res`) once we have ≥3 sequences × 3 algorithms × 3 runs | Medium | Possible now (ORB-SLAM3, Basalt) |
| Thesis comparison plots (LaTeX-ready PDFs) | High (before submission) | Not started |

---

## Research-paper readiness - honest assessment

**Current data inventory** (post AirSLAM HortiMulti + Rosario in progress):

| Item | Count | Threshold for SLAM paper |
|---|---|---|
| Multi-run benchmarks (3+ runs, statistics) | 4 seqs × 3-4 algos = **20 cells** (ORB-SLAM3 ×4, MAC-VO ×3: str02, str03, seq1; Basalt ×4; AirSLAM ×4: str02, str03, seq1, seq5) | ≥ 5 sequences × ≥ 3 algos × ≥ 3 runs = 45 cells |
| AirSLAM rosariov2 | 2 cells complete (seq1 ✓, seq5 ✓) | — |
| Single-run sanity points | 6 cells (DROID, MAC-VO across 3 seqs) | not publishable alone |
| Datasets | 2 (Rosario v2, HortiMulti) | typically 3–4 |
| Algorithms | 3 fully benched (ORB-SLAM3 ×4, Basalt ×4, AirSLAM ×4) + MAC-VO partially (×3 on 3 seqs) | 3+ |
| Novel-contribution candidates | Row/turn segmentation, scale-drift quantification on agricultural rows | Strong |

**Scientific findings worth reporting** (already in data):

1. **Loop-closure dependence dominates global accuracy on long agricultural rows.**
   Rosario seq1 (5–6 loops, ATE 1.18 m) vs seq5 (0 loops, ATE 20.2 m) on
   similar 11–14 k frame sequences. Local ATE is identical (≈ 0.016 m/row).
2. **Sim(3) alignment hides 4–10 % scale drift on stereo runs.** SE(3) ATE is
   the honest metric (Strawberry-03: 0.10 m Sim3 → 0.78 m SE3, 7.8×).
3. **Row vs Turn ATE inverts when turns are short** - segment-length effect,
   not localisation difficulty (documented in §9 of protocol).
4. **Body↔camera frame conventions matter for RPE rotation** - uncorrected
   mount offset gives 17.6 °/m artefact (Strawberry-03).

**Gaps preventing immediate publication:**

- DROID-SLAM and MAC-VO have no multi-run statistics yet.
- Only 2 datasets evaluated; LFSD remains untouched.
- No real-time-factor (RTF) comparison across algorithms.

**Recommended path to paper-grade dataset** (priority order):

1. **(now)** Complete ORB-SLAM3 × 3 on Strawberry-02 (in progress).
2. **(next)** DROID-SLAM × 3 on all 4 sequences (framework now consistent).
3. **(next)** MAC-VO × 3 on all 4 sequences (framework now consistent).
4. Extract & run Rosario seq2-4 (more loop-closure variation data).
5. LFSD dataset for third domain.
6. Cross-sequence aggregation + LaTeX tables.

---

## Outstanding framework notes

- **DROID-SLAM & MAC-VO multi-run support** - added in this phase
  (`run_droidslam.sh`, `run_macvo.sh` now take `<run_id>` and write to
  `results/<ds>/<seq>/<algo>/run<N>/`). Old single-run outputs at the flat
  `results/<ds>/<seq>/<algo>/trajectory.txt` paths remain in place for
  reference but are no longer the default write location.
- Workspace audit (this phase): no orphaned `__pycache__`, no `TODO/FIXME`
  in scripts. Only stale references are in `docs/00_overview.md` and
  `TODO.md` mentioning the removed `run_benchmark.sh` - corrected.

---

## Key commands

```bash
# Run an algorithm on a sequence (multi-run; <run_id> default 1)
bash scripts/run/run_orbslam3.sh   <dataset> <seq> <run_id>
bash scripts/run/run_droidslam.sh  <dataset> <seq> <run_id>
bash scripts/run/run_macvo.sh      <dataset> <seq> <run_id>

# Per-run evaluation (writes run_eval.json)
conda run -n macvo python3 scripts/eval/_evaluate_run.py <dataset> <seq> <algo> <run_id>

# Aggregate N runs (writes metrics.csv + report.md with Sim3 + SE3 ATE)
conda run -n macvo python3 scripts/eval/_aggregate_runs.py <dataset> <seq> <algo> <fps>

# Segmentation (writes segment_map.png at 8K; per-run, per-algo, cross-algo)
conda run -n macvo python3 scripts/eval/_plot_segments.py <dataset> <seq>

# Re-segment GT (v2 algorithm: 2 m sliding window, 10° / 20 cm thresholds)
conda run -n macvo python3 scripts/eval/_segment_trajectory.py \
    datasets/<ds>/<seq>/gt_tum.txt datasets/<ds>/<seq>/segments_auto.csv

# Ad-hoc ATE (Sim3 + SE3)
conda run -n macvo evo_ape tum gt_interp_tum.txt traj.txt -a --correct_scale  # Sim3
conda run -n macvo evo_ape tum gt_interp_tum.txt traj.txt -a                  # SE3

# MAC-VO post-run conversion (if script exits early due to X11/Rerun crash)
SBX=$(ls -dt src/MAC-VO/Results/*/*/ | head -1)
conda run -n macvo python3 scripts/eval/_macvo_to_tum.py "$SBX" \
    results/<dataset>/<seq>/macvo/trajectory.txt
```

---

*Last updated: 2026-05-19 - Phase B (segmentation v2, SE3 ATE, RPE rot diagnosis, framework consistency)*

---

## 2025-05-19 - repository publication

* Cleaned `configs/macvo/` duplicates. Each sequence now has its own file
  (`hortimulti_strawberry02.yaml`, `hortimulti_strawberry03.yaml`,
  `rosariov2_sequence1.yaml`, `rosariov2_sequence5.yaml`).
* Paths in `configs/macvo/*.yaml` are now portable: they contain a
  `__WS__` placeholder that `scripts/run/run_macvo.sh` expands to the
  workspace root at launch.
* **Bug fixed:** `run_macvo.sh` previously fell back to
  `<dataset>_sequence.yaml` when a per-sequence file was missing, which
  silently loaded the wrong sequence's images (HortiMulti strawberry-03
  runs were actually running strawberry-02 data). The fallback is removed;
  missing configs now error out immediately. **MAC-VO strawberry-03 must
  be re-run** with the new `hortimulti_strawberry03.yaml` config.
* SLAM source trees (`src/ORB_SLAM3`, `src/MAC-VO`, `src/DROID-SLAM`,
  `third_party/Pangolin`) are now excluded from this repo; clone them
  separately per `docs/setup.md`. The two patched forks live at
  [kubojion/ORB_SLAM3](https://github.com/kubojion/ORB_SLAM3) and
  [kubojion/MAC-VO](https://github.com/kubojion/MAC-VO) on branch
  `vslam-benchmark-patches`.
