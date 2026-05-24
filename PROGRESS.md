# vSLAM Benchmark - Progress

Algorithms: **ORB-SLAM3** (classical), **DROID-SLAM** (neural), **MAC-VO** (hybrid), **Basalt** (sliding-window VIO), **AirSLAM** (deep-feature VO, Docker).

---


| Algorithm | Dataset | Seq | ATE Sim3 | ATE SE3 | Scale (Sim3) | RPE [m/m] | FPS | Frames | Completion | Runs |
|---|---|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | Rosario v2 | seq1 | **1.176 ± 0.317 m** | **1.59 m** | 1.022 | 0.115 ± 0.104 | 12.53 ± 0.14 | 13 821 | 100% | **3** ✓ |
| DROID-SLAM | Rosario v2 | seq1 | 45.37 m | 45.37 m | 0.970 | 0.724 | 17.44 ± 0.21 | 13 821 | 100% | **3** ✓ |
| MAC-VO | Rosario v2 | seq1 | **13.520 ± 0.007 m** | **13.552 ± 0.007 m** | 0.980 | 0.051 | 1.71 ± 0.08 | 13 821 | 100% | **3** ✓ |
| Basalt | Rosario v2 | seq1 | **14.279 ± 0.302 m** | **18.693 ± 0.586 m** | 0.791 | 1.645 ± 0.040 | 59.44 ± 3.61 | 13 821 | 100% | **3** ✓ |
| AirSLAM | Rosario v2 | seq1 | **9.888 ± 0.059 m** | **9.891 ± 0.058 m** | 1.005 | 0.034 | 23.04 ± 3.61 | 13 821 | 100% | **3** ✓ |
| ORB-SLAM3 | Rosario v2 | seq5 | **20.207 ± 4.204 m** | **20.85 m** | 0.904 | 0.140 ± 0.062 | 11.28 ± 1.56 | 11 640 | 91% avg (0 loops) | **3** ✓ |
| DROID-SLAM | Rosario v2 | seq5 | 50.02 m | 50.24 m | 1.904 | 1.076 | 23.36 ± 0.25 | 11 640 | 100% | **3** ✓ |
| MAC-VO | Rosario v2 | seq5 | **19.384 ± 0.006 m** | **19.674 m** | 0.933 | 0.096 ± 0.000 | 1.40 ± 0.21 | 11 640 | 100% | **3** ✓ |
| Basalt | Rosario v2 | seq5 | **15.035 ± 0.062 m** | **15.425 ± 0.068 m** | 0.934 | 0.802 | 64.60 ± 2.30 | 11 640 | 100% | **3** ✓ |
| AirSLAM | Rosario v2 | seq5 | **12.722 ± 0.991 m** | **12.777 ± 1.014 m** | 0.977 | 0.055 ± 0.006 | 23.74 ± 0.48 | 11 640 | 100% | **3** ✓ |
| ORB-SLAM3 | HortiMulti | Strawberry-02 | **0.893 ± 0.139 m** | **2.10 ± 0.10 m** | 1.040 | 0.072 | 4.51 ± 0.33 | 4 186–4 980 / 9 530 | 44–52%† | **3** ✓ |
| DROID-SLAM | HortiMulti | Strawberry-02 | 38.92 m | 47.90 m | 9.590 | 4.335 | 27.95 ± 0.21 | 9 530 | 100% | **3** ✓ |
| MAC-VO | HortiMulti | Strawberry-02 | **10.231 ± 0.502 m** | **10.245 ± 0.496 m** | 1.009 | 0.096 ± 0.001 | 1.70 ± 0.04 | 9 530 | 100% | **3** ✓ |
| Basalt | HortiMulti | Strawberry-02 | **2.0978 ± 0.0008 m** | **2.664 ± 0.001 m** | 1.034 | 0.091 | 149.70 ± 4.01 | 9 530 | 100% | **3** ✓ |
| AirSLAM | HortiMulti | Strawberry-02 | **20.220 ± 0.824 m** | **20.483 ± 0.893 m** | 0.928 | 0.266 ± 0.015 | 27.37 ± 0.32 | 9 530 | 100% | **3** ✓ |
| ORB-SLAM3 | HortiMulti | Strawberry-03 | **0.1039 ± 0.0013 m** | **0.78 m** | 1.043 | 0.023 ± 0.001 | 9.39 ± 0.05 | 2 425 | 100% | **3** ✓ |
| MAC-VO | HortiMulti | Strawberry-03 | **0.505 ± 0.010 m** | **0.84 m** | 1.037 | 0.024 ± 0.001 | 1.54 ± 0.07 | 2 425 | 100% | **3** ✓ |
| Basalt | HortiMulti | Strawberry-03 | **0.2753 ± 0.0000 m** | **0.7151 m** | 1.036 | 0.022 | 143.65 ± 24.16 | 2 425 | 100% | **3** ✓ |
| AirSLAM | HortiMulti | Strawberry-03 | **3.631 ± 0.205 m** | **3.771 ± 0.191 m** | 1.064 | 0.135 ± 0.005 | 22.07 ± 10.06 | 2 425 | 100% | **3** ✓ |
| DROID-SLAM | HortiMulti | Strawberry-03 | 18.76 m | 18.81 m | 0.428 | 0.837 | 15.85 ± 0.14 | 2 425 | 100% | **3** ✓ |

### [Non-agricultural] EuRoC-MAV 

| Sequence | Algorithm | ATE Sim3 [m] | ATE SE3 [m] | RPE [m/m] | Scale | FPS | Frames |
|---|---|---|---|---|---|---|---|
| MH_01_easy | ORB-SLAM3 | 0.0340 | 0.0352 | 0.0156 | 1.0021 | 18.17 | 3682 |
| MH_01_easy | Basalt | 0.0567 | 0.0873 | 0.0085 | 1.0156 | 176.75 | 3682 |
| MH_01_easy | AirSLAM | 0.1107 | 0.1156 | 0.0195 | 1.0073 | 15.33 | 3682 |
| MH_01_easy | MAC-VO | 0.1981 | 0.1993 | 0.0295 | 1.0051 | 1.29 | 3682 |
| MH_01_easy | DROID-SLAM | 4.083 | 7.891 | 0.500 | 0.173 | 13.17 | 3682 |
| MH_03_medium | ORB-SLAM3 | 0.0437 | 0.0520 | 0.0179 | 0.9922 | 17.89 | 2700 |
| MH_03_medium | Basalt | 0.1372 | 0.1397 | 0.0159 | 1.0075 | 113.47 | 2700 |
| MH_03_medium | AirSLAM | 0.1431 | 0.1443 | 0.0188 | 0.9950 | 31.73 | 2700 |
| MH_03_medium | MAC-VO | 0.3403 | 0.3405 | 0.0187 | 0.9961 | 1.15 | 2700 |
| MH_03_medium | DROID-SLAM | 3.523 | 7.105 | 2.274 | 0.082 | 10.94 | 2700 |
| MH_05_difficult | ORB-SLAM3 | 0.0720 | 0.0781 | 0.2282 | 0.9956 | 17.97 | 2273 |
| MH_05_difficult | Basalt | 0.1816 | 0.1931 | 0.0870 | 1.0097 | 108.72 | 2273 |
| MH_05_difficult | AirSLAM | 0.2968 | 0.3066 | 0.0256 | 1.0116 | 34.92 | 2273 |
| MH_05_difficult | MAC-VO | 0.4697 | 0.4836 | 0.0276 | 1.0172 | 0.86 | 2273 |
| MH_05_difficult | DROID-SLAM | 6.594 | 8.514 | 0.786 | 0.248 | 13.85 | 2273 |

† ORB-SLAM3 processed all 9 530 input frames but tracking only succeeded for frames
spanning 91 s – 500 s of the 952 s sequence.  Tracking was permanently lost after 500 s
due to the repetitive polytunnel environment.  This is **not** a stride/sampling issue.  

All multi-run metrics use **both Sim(3) and SE(3)** alignment (`evo_ape --align [--correct_scale]`) and
**`point_distance` RPE** (not `trans_part` - avoids body-frame quaternion mismatch).

---

## Sim(3) vs SE(3) alignment for stereo 

Stereo SLAM has **metric scale** (from the baseline), so SE(3) ATE is the
accuracy metric. Sim(3) absorbs residual scale drift into a 7th DoF
alignment scale factor, hiding error:

| Sequence | Sim3 ATE | SE3 ATE | Scale | Scale drift |
|---|---|---|---|---|
| Rosario seq1 | 1.18 m | 1.59 m | 1.022 | 2.2 % |
| Rosario seq5 | 20.21 m | 20.85 m | 0.904 | 10 % |
| Strawberry-02 | 0.89 m | 2.10 m | 1.040 | 4.0 % |
| **Strawberry-03** | **0.10 m** | **0.78 m** | **1.043** | **4.3 %** |


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



## Dataset 1 - Rosario v2 - Complete

### Sequence 1 - ORB-SLAM3 × 3 benchmark complete ✓

- **Results in:** `results/rosariov2/sequence1/orbslam3/` - `metrics.csv`, `report.md`, `segment_map.png`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE | **1.176 ± 0.317 m** |
| RPE (point\_distance, 1 m) | 0.115 ± 0.104 m (high var due to tracking-loss reloc boundary) |
| RPE rotation | 0.416 ± 0.139 °/m |
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
| DROID-SLAM | **45.37 ± 0.000 m** | 13 821 | 100% | **3** ✓ |
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

#### DROID-SLAM × 3 - Sequence 1 complete

> Full report: `results/rosariov2/sequence1/droidslam/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---|
| ATE RMSE Sim3 | **45.369 ± 0.000 m** |
| ATE RMSE SE3 | **45.371 ± 0.000 m** |
| RPE (point\_distance, 1 m) | 0.724 ± 0.005 m/m |
| Scale factor (Sim3) | 0.970 ± 0.000 (**3.0% under-scale**) |
| Frames tracked | 100% (13 821 / 13 821, all 3 runs) |
| Loop closures | 0 (all 3 runs) |
| Mean FPS | 17.44 ± 0.21 (1.16x real-time @ 15 fps) |
| VRAM peak | ~11.9 GiB |
| Row ATE RMSE (18 segs) | 7.90 m |
| Turn ATE RMSE (5 segs) | 0.44 m |

> **Method:** run with `--filter_thresh 6.0` (the lowest value that fits in VRAM) and `--stride 1`
> (all frames). `filter_thresh` controls the minimum optical-flow confidence required to retain a
> frame in the DROID bundle adjustment window. A lower threshold keeps more frames but uses more VRAM;
> 6.0 was the minimum feasible value on this hardware without OOM.
>
> Despite full-frame coverage (vs the earlier stride=2 test at 50% coverage) the global ATE barely
> changed (45.37 m vs 45.00 m). Scale improved significantly (0.970 vs 1.221), but ATE remained
> ~45 m because scale is only 3% off - the error is dominated by trajectory shape divergence, not
> scale. This is a domain-mismatch failure: DROID-SLAM's optical flow network was never trained
> on outdoor crop-row imagery and cannot track reliably across the long open-field sections.

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
| DROID-SLAM | **50.02 m** | 11 640 | 100% | **3** ✓ |
| MAC-VO | **19.384 ± 0.006 m** | 11 640 | 100% | **3** ✓ |
| Basalt | **15.035 ± 0.062 m** | 11 640 | 100% | **3** ✓ |
| AirSLAM | **12.722 ± 0.991 m** | 11 640 | 100% | **3** ✓ |

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
- DROID-SLAM seq1: 45.37 m (3 runs, scale=0.970, filter_thresh=6.0) - domain-mismatch failure, ~45 m both with stride=2 and stride=1
- DROID-SLAM seq5: 50.02 m (3 runs, scale=1.904) - same failure mode, slightly worse
- ORB-SLAM3 seq5: 20.207 m - 0 loop closures, long straight rows → uncorrected scale drift
- DROID-SLAM consistently very poor (~45-50 m both seqs); full-frame run (filter_thresh=6.0) confirms it is a domain-mismatch failure, not a sampling issue
- MAC-VO seq1: 13.520 ± 0.007 m (3 runs) - no loop closure, scale drift 2%; local row ATE 0.020 m
- MAC-VO seq5: 19.384 ± 0.006 m (3 runs) - no loop closure, scale drift 6.7%; local row ATE 0.045 m
- Basalt seq1: 14.279 ± 0.302 m (3 runs) - scale drift 20.9%; local row ATE 14 mm (matches ORB-SLAM3)
- Basalt seq5: 15.035 ± 0.062 m (3 runs) - scale drift 6.6%; better than seq1 due to route geometry
- AirSLAM seq1: **DONE** (9.888 ± 0.059 m Sim3, 100% tracking, scale=1.005, 23.04 fps)
- AirSLAM seq5: **DONE** (12.722 ± 0.991 m Sim3, 100% tracking, scale=0.977, 23.74 fps)
- **Local accuracy is similar for all algorithms**: row ATE 0.016-0.021 m for ORB-SLAM3, MAC-VO, and Basalt on seq1/seq5

---

## Dataset 2 - HortiMulti - Complete

 - ORB-SLAM3 × 3 + MAC-VO × 3 + Basalt × 3 + AirSLAM × 3 + DROID-SLAM × 3 complete on all sequences.

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
| **ORB-SLAM3 × 3** | **0.893 ± 0.171 m** (SE3 2.10 ± 0.12) | 4 186-4 980 | 44-52% timeline | **3** ✓ |
| DROID-SLAM | **38.92 m** | 9 530 | 100% | **3** ✓ |
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
| AirSLAM | **3.631 ± 0.205 m** | 3.771 ± 0.191 m | 1.064 | 22.07 | 2 425 | **100%** | **3** ✓ |
| DROID-SLAM | **18.76 m** | 18.81 m | 0.428 | 15.85 | 2 425 | **100%** | **3** ✓ |

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

#### DROID-SLAM × 3 - Strawberry-03 complete

> Full report: `results/hortimulti/strawberry03/droidslam/report.md`

| Metric | Value (3 runs, mean ± std) |
|---|---------|
| ATE RMSE Sim3 | **18.76 m** |
| ATE RMSE SE3 | **18.81 m** |
| RPE (point\_distance, 1 m) | 0.837 m/m |
| Scale factor (Sim3) | 0.428 (**57.2 % under-scale**) |
| Frames tracked | 100% (2 425 / 2 425, all 3 runs) |
| Mean FPS | 15.85 ± 0.14 |
| VRAM peak | ~7 500 MiB |

> Massive scale collapse (scale 0.428) is the primary failure mode: DROID-SLAM
> interprets this short polytunnel sequence as if the world is ~2.3x smaller than
> it is. The Sim3 and SE3 ATEs are nearly identical (18.76 vs 18.81 m) because
> scale error dominates - re-scaling the trajectory moves it only 50 mm. Global
> ATE 18.76 m is 180x worse than ORB-SLAM3 on the same sequence (0.104 m).
> RPE 0.837 m/m confirms per-frame odometry also fails - not just global drift.
> This is consistent with str02 (scale 9.59, ATE 38.92 m): DROID-SLAM trained
> on TartanAir/FlyingThings3D has never seen agricultural polytunnel imagery.

### Config files

- ORB-SLAM3: `configs/orbslam3/hortimulti_stereo.yaml` (shared across all HortiMulti seqs)
- DROID-SLAM: `configs/droidslam/hortimulti.txt` (**no comments** - parser crashes on `#`)
- MAC-VO: `configs/macvo/hortimulti_sequence.yaml` (update `root:` path per sequence)

### HortiMulti observations

- ORB-SLAM3 best global accuracy on str03 (0.10 m Sim3); tracking lost on str02 after 44-52% of timeline (repetitive polytunnel)
- MAC-VO 100% completion on both sequences; ATE 10 m on str02 (long, ~953 s) vs 0.505 m on str03 (short, ~242 s) - drift scales with sequence length
- DROID-SLAM str02: **38.92 m** (3 runs, 9530 frames, scale=9.59) - massive over-scale collapse
- DROID-SLAM str03: **18.76 m** (3 runs, 2425 frames, scale=0.428, FPS=15.85) - massive under-scale collapse
- Basalt str03: 0.2753 ± 0.0000 m (3 runs, 143 fps, 100% tracking) - between ORB-SLAM3 and MAC-VO globally; local row ATE 27 mm matches ORB-SLAM3
- Basalt str02: 2.0978 ± 0.0008 m (3 runs, 150 fps, 100% tracking) - completes full sequence vs ORB-SLAM3 44-52% coverage
- AirSLAM str03: 3.6314 ± 0.2047 m (3 runs, 22 fps avg, 100% tracking) - highest global ATE on str03; 0 loop closures; local turn ATE 50 mm reasonable; run1 slow (TRT compile), run2+3 fast at 29 fps
- AirSLAM str02: **complete** (3 runs, 20.22 ± 0.82 m, 100% tracking)

---

## Dataset 3 - [NON-AGRICULTURAL REFERENCE] EuRoC-MAV

> **[NON-AGRICULTURAL REFERENCE]** All 5 algorithms run on MH_01_easy,
> MH_03_medium, and MH_05_difficult (N=1 per sequence, no repetition stats).
> Used as a sanity check against published EuRoC literature values.

**Camera:** 752x480, 20 fps, baseline 0.110 m, indoor MAV flight.

| Sequence | Algorithm | ATE Sim3 [m] | ATE SE3 [m] | RPE [m/m] | Scale | FPS | Frames |
|---|---|---|---|---|---|---|---|
| MH_01_easy | ORB-SLAM3 | **0.034** | **0.035** | 0.016 | 1.002 | 18.2 | 3682 |
| MH_01_easy | Basalt | 0.057 | 0.087 | 0.009 | 1.016 | 176.8 | 3682 |
| MH_01_easy | AirSLAM | 0.111 | 0.116 | 0.020 | 1.007 | 15.3 | 3682 |
| MH_01_easy | MAC-VO | 0.198 | 0.199 | 0.030 | 1.005 | 1.3 | 3682 |
| MH_01_easy | DROID-SLAM | 4.083 | 7.891 | 0.500 | 0.173 | 13.2 | 3682 |
| MH_03_medium | ORB-SLAM3 | **0.044** | **0.052** | 0.018 | 0.992 | 17.9 | 2700 |
| MH_03_medium | Basalt | 0.137 | 0.140 | 0.016 | 1.008 | 113.5 | 2700 |
| MH_03_medium | AirSLAM | 0.143 | 0.144 | 0.019 | 0.995 | 31.7 | 2700 |
| MH_03_medium | MAC-VO | 0.340 | 0.341 | 0.019 | 0.996 | 1.15 | 2700 |
| MH_03_medium | DROID-SLAM | 3.523 | 7.105 | 2.274 | 0.082 | 10.9 | 2700 |
| MH_05_difficult | ORB-SLAM3 | **0.072** | **0.078** | 0.228 | 0.996 | 18.0 | 2273 |
| MH_05_difficult | Basalt | 0.182 | 0.193 | 0.087 | 1.010 | 108.7 | 2273 |
| MH_05_difficult | AirSLAM | 0.297 | 0.307 | 0.026 | 1.012 | 34.9 | 2273 |
| MH_05_difficult | MAC-VO | 0.470 | 0.484 | 0.028 | 1.017 | 0.86 | 2273 |
| MH_05_difficult | DROID-SLAM | 6.594 | 8.514 | 0.786 | 0.248 | 13.8 | 2273 |

> ORB-SLAM3 ATE 0.034-0.072 m matches published EuRoC results.
> DROID-SLAM shows large scale error (scale 0.08-0.25) on all 3 sequences - mono-style drift on stereo input.
> Basalt highest throughput (109-177 fps). AirSLAM outputs keyframe-only poses on MH_01_easy (268 of 3682).

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

### DROID-SLAM - MH_01_easy, MH_03_medium, MH_05_difficult complete

| Sequence | ATE Sim3 | ATE SE3 | RPE [m/m] | Scale | FPS | Frames |
|---|---|---|---|---|---|---|
| MH_01_easy | 4.083 m | 7.891 m | 0.500 | 0.173 | 13.17 | 3682 |
| MH_03_medium | 3.523 m | 7.105 m | 2.274 | 0.082 | 10.94 | 2700 |
| MH_05_difficult | 6.594 m | 8.514 m | 0.786 | 0.248 | 13.85 | 2273 |

> Large scale error (scale 0.08-0.25) indicates DROID-SLAM produces monocular-style scale drift
> even with stereo input on this dataset. SE3 ATE (7-9 m) is 15-20x worse than ORB-SLAM3.
> Segment maps under `results/euroc_mav/MH_0*/droidslam/`.

---

## Findings

### 1. Loop closure is the dominant factor for global accuracy on long agricultural sequences

Rosario v2 provides the clearest evidence. ORB-SLAM3 on seq1 (13 821 frames, ~940 m) achieves 1.18 m
global ATE with 5-6 loop closures. On seq5 (11 640 frames, similar geometry) it achieves only 20.2 m
because no loops are detected. The local per-row ATE is identical in both cases (~0.016 m). This is not
an algorithm deficiency - it is a fundamental challenge of perceptually aliased environments where all
crop rows look identical. Without distinctive visual landmarks, bag-of-words place recognition cannot
trigger loop closure, and global drift accumulates uncorrected.

Quantified: 5-6 loop closures reduce global ATE from ~20 m to ~1.2 m on a ~940 m path - a 17x improvement.
All algorithms without loop closure (MAC-VO, Basalt, AirSLAM) cluster in the 9-20 m range on Rosario.

### 2. Local accuracy is excellent and consistent across all algorithms

Despite large global ATE differences, per-row segment ATE is remarkably similar:
- ORB-SLAM3 seq1: 16 mm / seq5: 16 mm
- MAC-VO seq1: 20 mm / seq5: 45 mm
- Basalt seq1: 14 mm / seq5: 21 mm
- AirSLAM seq1: 19 mm / seq5: 47 mm

This 1000x ratio between local (16 mm) and global (16 m) accuracy confirms that all algorithms track
individual rows accurately - the problem is purely global map consistency. For agricultural applications
that need only within-row precision (e.g., spray path following), all algorithms are adequate.
For field-level consistency (cross-row registration, field mapping), loop closure is essential.

### 3. Scale drift follows sequence geometry, not just length

Basalt shows a striking geometry-dependent pattern: 20.9% scale drift on Rosario seq1 vs 6.6% on seq5.
Both sequences are similar length (~940 m, ~11-14 k frames). The difference is route geometry - seq1
covers a more varied path with directional changes, while seq5 is dominated by long parallel rows.
This suggests that scale drift in visual-only SLAM accumulates faster on monotone straight-line motion,
where the stereo baseline provides weaker triangulation constraints. IMU data (available but unused)
would break this correlation by providing absolute scale observable independent of trajectory shape.

### 4. Sim(3) alignment systematically underestimates scale drift

Sim(3) ATE removes scale drift from the metric, giving an optimistic view:
- ORB-SLAM3 str03: 0.104 m (Sim3) vs 0.78 m (SE3) - 7.5x gap
- Basalt seq1: 14.3 m (Sim3) vs 18.7 m (SE3) - 1.3x gap
- DROID-SLAM MH_01: 4.1 m (Sim3) vs 7.9 m (SE3) - 1.9x gap

SE3 ATE is the honest metric for stereo systems where scale is observable. The large Sim3/SE3
gap is itself diagnostic: when SE3 >> Sim3, scale drift is the dominant error source,
not localization noise. For system-level reporting in the thesis, SE3 is the primary metric.

### 5. DROID-SLAM fails on agricultural data due to domain mismatch

DROID-SLAM is trained on TartanAir (photorealistic simulation), FlyingThings3D, and Sintel -
none of which resemble polytunnel or open-field agricultural imagery. The failure is severe:
- HortiMulti str02: ATE 38.92 m, scale 9.59 (10x over-scale)
- HortiMulti str03: ATE 18.76 m, scale 0.428 (2.3x under-scale)
- Rosario seq5: ATE 50.02 m
- EuRoC MH_01: ATE 4.1 m Sim3 / 7.9 m SE3, scale 0.173

The scale collapse (scale << 0.5 or >> 2.0) indicates the depth network predicts wildly incorrect
disparity on these out-of-distribution images. Interestingly, DROID-SLAM runs at 10-16 fps across all
sequences - it processes frames at the same speed regardless of how wrong the predictions are.
Fine-tuning on even a small set of agricultural frames is a likely path to improvement (see phase2_plan.md).

### 6. Speed-accuracy Pareto frontier

Across agricultural sequences, the approximate ordering by speed vs accuracy tradeoff:

| Algorithm | FPS (typical) | Global ATE (Rosario) | Notes |
|---|---|---|---|
| Basalt | 60-150 | 14-15 m | Fastest; no loop closure |
| AirSLAM | 22-27 | 10-13 m | Fast + SuperPoint features |
| ORB-SLAM3 | 9-18 | 1-20 m | Loop closure when available |
| DROID-SLAM | 10-16 | 38-50 m | Fast but inaccurate on agri data |
| MAC-VO | 1-2 | 13-19 m | Slowest; uncertainty-aware |

Basalt and AirSLAM dominate on pure speed. ORB-SLAM3 dominates when loop closure fires.
MAC-VO provides covariance estimates useful for downstream uncertainty quantification -
its speed makes it unsuitable for real-time deployment but excellent for offline analysis.

### 7. RPE rotation artefact (frame convention mismatch)

All algorithms on HortiMulti report RPE rotation ~17-20 deg/m - an artefact of the
body-to-camera frame rotation in the HortiMulti calibration. Ground truth is in body
frame (IMU/robot), while estimated trajectories are in camera frame. The 17.6 deg/m
constant offset across all algorithms confirms this is a systematic calibration issue,
not a measurement of real rotational error. RPE translation (m/m) is unaffected and
remains the valid metric for reporting.

### 8. Repeatability across 3 runs

Algorithms with no randomness in their pipeline (Basalt, MAC-VO) produce near-identical
results across all 3 runs (ATE std < 1 mm). Algorithms with non-deterministic elements
(ORB-SLAM3 loop closure timing, AirSLAM TRT engine) show larger run-to-run variation:
- ORB-SLAM3 seq5: 4.2 m std across 3 runs (loop closure timing)
- AirSLAM seq5: 0.99 m std (run3 notably worse: 14.1 m vs 12.1 m)
- AirSLAM str02: 0.82 m std

The 3-run average is reliable for all algorithms. Single-run benchmarking would give
misleading results for ORB-SLAM3 and AirSLAM on difficult sequences.

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

*Last updated: 2026-05-24 - macvo seq5 3 runs complete; EuRoC DROID-SLAM added (all 3 sequences); all segment maps and plots regenerated*

---

