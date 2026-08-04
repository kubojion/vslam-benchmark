# Progress report on vSLAM benchmarking — 04.08.26

**Ivan Moroz / Jion Kubo**

---

## Summary

Since the last report (24.05.26: 5 algorithms, stereo-VO only, 3 datasets) the benchmark has grown to
**15 algorithms, 5 operating modes (VO / VO-LC / VIO / VIO-LC / GNSS-VIO), 4 datasets — 210 evaluated
configurations, 256 individual runs**, including our own RTK-referenced ZED2i field dataset. The headline
outcome is not a ranking: on the EuRoC reference every method works (0.03–0.2 m), while **agriculture
breaks three assumptions visual-inertial SLAM depends on** — feature distinctiveness, place uniqueness,
and inertial excitation — and each algorithm's agricultural result is governed by which assumption its
design leans on and how it fails when that assumption breaks.

**Key findings**

1. **The IMU helps only with excitation.** On the slow, smooth ZED2i field run the tightly-coupled VIO
   filters scale-collapse (5–18 m) while stereo VO stays at 0.26–0.45 m; on the more agile Rosario
   sequences the same IMU rescues tracking and wins (ORB-SLAM3 VIO-LC 1.08 m, best on the benchmark).
2. **Classical sparse-feature tracking hard-fails on crops.** ORB-SLAM3 loses tracking on 40–60 % of the
   outdoor sequences and its low agricultural "VO" ATE is an artifact of the shorter tracked sub-path;
   flow-based, learned, and sliding-window front-ends degrade gracefully at 100 % coverage.
3. **Loop closure on crops is mechanism-dependent and never fully safe.** Proximity closure always hurts;
   verified iBoW/DBoW closure helps on distinctive scenes and true revisits but each blew up on at least
   one aliased agricultural sequence (up to +308 %).
4. **Single runs can mislead.** ORB-SLAM3 varies up to ~4× between identical runs on agricultural
   sequences (its agri cells are reported as N=3 median + range); most real-time estimators are
   structurally non-deterministic and are so far single-run.

---

## 1. Experimental setup

### 1.1 Datasets

| Dataset | Environment | Motion / excitation | Camera | Ground truth | Frames / path |
|---|---|---|---|---|---|
| Rosario v2 (seq1, seq5) | outdoor soybean rows | turns, varied — **adequate** | RealSense D435i stereo, 1280×720 @15 Hz | PPK GPS+INS | 13.8k / 11.6k |
| HortiMulti (str02, str03) | indoor strawberry polytunnel | short loop, row markers | Basler stereo, 1936×1216 @10 Hz | mocap / lidar ref | 9.5k / 2.4k |
| **ZED2i field1** (ours) | outdoor agricultural field | slow, smooth, straight — **weak** | ZED2i stereo, 1920×1080 @10 Hz | RTK-GPS (position) | 46.3k / 413 m / 77 min |
| EuRoC-MAV (MH_01/03/05) | *[non-agricultural reference]* indoor MAV | agile, all-DoF | VI-Sensor stereo, 752×480 @20 Hz | Vicon | 3.7k / 2.7k / 2.3k |

### 1.2 Algorithms

| Algorithm | Type | Front-end | LC mechanism | Modes run |
|---|---|---|---|---|
| ORB-SLAM3 | classical feature | ORB descriptor matching | DBoW2 + geometric verif. | VO, VO-LC, VIO, VIO-LC |
| OKVIS2 / OKVIS2-X | sliding-window MAP VIO | descriptors + IMU | DBoW + Sim3 | VO†, VO-LC†, VIO, VIO-LC (+GNSS for -X) |
| Basalt | sliding-window VIO | optical flow + IMU | — | VO, VIO |
| OV2SLAM | online stereo VO | KLT optical flow | online iBoW | VO, VO-LC |
| AirSLAM | deep-feature VO/VIO | SuperPoint-style | offline map-refinement | VO, VIO, VIO-LC |
| DPVO / DPV-SLAM | learned **monocular** VO | patch network | proximity | VO, VO-LC |
| MAC-VO | learned-uncertainty stereo VO | learned matching | — | VO |
| OpenVINS / Voxel-SVIO | MSCKF filter VIO | KLT + IMU | — | VIO |
| VINS-Fusion, CIFASIS GNSS-SI, RTAB-Map, OpenVINS+GPS | GNSS fusion | — | — | GNSS-VIO |

† OKVIS2/OKVIS2-X "VO" = IMU residuals disabled (best-effort degraded mode of a VI system).
DROID-SLAM was dropped early (replaced by DPVO, 9–13× more accurate); MASt3R-SLAM and MegaSaM are
installed but **hardware-blocked** (OOM on the 12 GB GPU).

### 1.3 Metrics and protocol

- **ATE Sim3** RMSE (monocular-comparable) and **ATE SE3** (scale-aware); the **scale factor** is a
  scale-collapse diagnostic (stereo/VI methods should sit at ≈ 1.0).
- **RPE** (local drift), FPS, and **trajectory coverage** — the fraction of the sequence for which the
  method produced poses. *ATE is uninterpretable without coverage: a method that quits early is scored
  only on the easy sub-path it completed.*
- N=1 per cell, except non-deterministic cells (ORB-SLAM3 agricultural: **N=3, median + range**).
- One machine (i9-14900HX / RTX 4080 12 GB) unless noted; a subset of earlier runs came from a second
  machine (provenance stamped in each `run_eval.json` where available).

**Caveat legend** (used in all tables): **‡** non-deterministic, N=3 median · **(NN %)** coverage when
< 95 % (partial path) · **✗** scale collapse (Sim3 scale ≈ 0) · **†** preliminary (pre-extrinsic-fix)
· **—** not run / failed · `(n)` accepted loop closures.

---

## 2. Results by operating mode

### 2.1 Overview

![Whole-benchmark VO accuracy](../figures/fig_master_vo_heatmap.png)

![Whole-benchmark VIO accuracy](../figures/fig_master_vio_heatmap.png)

The two heatmaps carry the thesis: the EuRoC block is uniformly green for every method (the pipeline and
configurations are sound), the agricultural block is where methods diverge by orders of magnitude, and
the ZED2i VIO column shows the weak-excitation collapse (✗) that its VO column does not have.

### 2.2 Visual Odometry (VO)

| Algorithm | seq1 | seq5 | str02 | str03 | MH01 | MH03 | MH05 | zed2i |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | 3.00 (58 %)‡ | 6.93 (52 %)‡ | 1.38 (47 %)‡ | 0.22‡ | **0.036** | 0.046 | **0.047** | **0.256** |
| OV2SLAM | **7.24** | 8.05 | 5.76 | 0.35 | 0.058 | **0.042** | 0.099 | 0.348 |
| DPVO (mono) | 4.93 | **3.92** | 14.59 | 1.82 | 0.122 | 0.134 | 0.121 | 1.431 |
| Basalt | 14.09 | 15.05 | **2.10** | **0.28** | 0.057 | 0.137 | 0.182 | 0.446 |
| OKVIS2 | 20.03 | 17.48 | 1.69 | 0.37 | 0.078 | 0.133 | 0.153 | 3.372 |
| OKVIS2-X | 18.02 | 14.91 | 1.97 | 0.68 | 0.132 | 0.169 | 0.153 | 1.436 |
| MAC-VO | 13.52 | 19.38 | 10.01 | 0.51 | 0.198 | 0.340 | 0.470 | — |
| AirSLAM | 9.89 | 12.11 | 19.77 | 3.74 | 0.111 | 0.143 | 0.297 | 3.866 |

*ATE Sim3 (m); bold = best full-coverage result per column. ORB-SLAM3's low agricultural values are
partial-path artifacts (§3.2) — among full-coverage methods OV2SLAM/DPVO lead outdoors, Basalt indoors.
The ORB-SLAM3 "VO" baseline was re-run with `loopClosing: 0` after we found the default config silently
left LC enabled (str03 went 0.10 → 0.22 m once genuinely LC-off).*

### 2.3 VO + Loop Closure (VO-LC)

| Algorithm (LC type) | seq1 | seq5 | str02 | str03 | MH01 | MH03 | MH05 | zed2i |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 (DBoW) | 1.52 (4) | 15.55 (0) | 0.72 (0, 53 %) | 0.10 (1) | 0.048 (0) | 0.043 (0) | 0.044 (1) | **0.202** (0) |
| OKVIS2 (DBoW) | 18.87 (76) | 16.26 (0) | 1.39 (7) | 0.12 (54) | **0.021** (36) | **0.023** (44) | 0.057 (18) | 0.75 (1261, 93 %) |
| OKVIS2-X (DBoW) | 19.40 (30) | 13.91 (1) | 1.22 (7) | 2.53 (7) | 0.018 (37) | 0.030 (37) | 0.061 (20) | 0.29 (357, 78 %) |
| OV2SLAM (iBoW) | **3.86** | **2.25** | 23.50 | **0.10** | 0.048 | 0.047 | 0.063 | 0.314 |
| DPV-SLAM (proximity) | 9.32 | 6.48 | 22.00 | 8.83 | 0.047 | 0.042 | 0.058 | 2.364 |

*`(n)` = accepted loop closures. DPV-SLAM's proximity closer and OV2SLAM's iBoW count are not surfaced by
their logs. High counts on repetitive scenes (OKVIS2 zed2i: 1261 ≈ 27/1000 frames, mostly short-baseline
look-alike matches) are a perceptual-aliasing signature, not a benefit measure — OKVIS2 fired 54 closures
on str03 and improved, OKVIS2-X fired 7 and regressed +271 %.*

### 2.4 Visual-Inertial Odometry (VIO)

| Algorithm | seq1 | seq5 | str02 | str03 | MH01 | MH03 | MH05 | zed2i |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | 4.70 | **2.29** | **1.48** | 0.40 | **0.025** | **0.030** | 0.048 | — ✗ failed |
| Basalt | **3.00** | 4.74 | 2.49 | **0.19** | 0.035 | 0.046 | 0.111 | 9.14 |
| OKVIS2 | 18.89 | 20.29 | 2.15 | 0.40 | 0.054 | 0.098 | 0.151 | 17.67 (65 %) ✗ |
| OKVIS2-X | 19.33 | 20.40 | 2.13 | 0.34 | 0.046 | 0.072 | 0.144 | 18.32 (60 %) ✗ |
| OpenVINS | **2.32** | 10.76 | 2.24 | 0.43 | 0.058 | 0.126 | 0.205 | 5.33 (15 %) ✗ |
| Voxel-SVIO | 4.40 | 6.80 | 5.83 | 0.44 | 0.082 | 0.081 | 0.162 | **3.71** |
| AirSLAM | 16.50 | 12.15 | 5.30 | 1.24 | 0.102 | 0.088 | 0.136 | 3.90 |

*On ZED2i every VIO lands ≥ 3.7 m (the tightly-coupled filters collapse, ✗) against VO at ≤ 0.45 m; on
Rosario the picture inverts — see §3.1.*

### 2.5 VIO + Loop Closure (VIO-LC)

| Algorithm | seq1 | seq5 | str02 | str03 | MH01 | MH03 | MH05 |
|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | **1.08** (127) | **2.45** (0) | **0.88** (1) | 0.19 (1) | — | — | — |
| OKVIS2 | 18.32 | 21.25 | 1.33 (4) | **0.10** (64) | 0.020 (34) | 0.024 (42) | 0.049 (20) |
| OKVIS2-X | 17.95 (27) | 20.05 (1) | 1.78 (8) | 0.11 (16) | **0.014** (29) | 0.028 (39) | **0.045** (14) |
| AirSLAM | 15.87 | 24.26 | 5.36 | 0.62 | 0.040 | 0.041 | 0.050 |

*No ZED2i column: weak-excitation VIO is unusable there. AirSLAM's LC runs in its offline map-refinement
step (count not surfaced). **ORB-SLAM3 VIO-LC is the most accurate configuration on Rosario/HortiMulti**
(seq1 1.08 m at 99 % coverage). Note ORB-SLAM3's EuRoC VIO-LC configs do not exist yet.*

### 2.6 GNSS-VIO

| Algorithm | seq1 | seq5 (PPK) | str02† | str03† |
|---|---|---|---|---|
| VINS-Fusion+GPS | **1.19** | **0.91** | 4.90 | 2.40 |
| RTAB-Map+GPS | 2.14 | 1.64 (38 %) | 6.30 | 1.76 |
| CIFASIS GNSS-SI | 3.58 | 2.06 | 7.26 | 1.50 |
| OKVIS2-X (tight GNSS) | 8.79 | 8.15 | 2.38 | **0.28** |
| OpenVINS+GPS | 2.39 | 4.66 | 30.86† | 16.50† |

*GPS-bearing sequences only (EuRoC has no GPS). seq5 uses PPK-grade GPS. † OpenVINS+GPS HortiMulti rows
predate the camera-IMU extrinsic fix and are preliminary; its trajectories also carry a corrupt timestamp
that invalidates the coverage metric (ATE unaffected). PPK vs conventional study: high-grade GPS improves
**vertical** RMSE by 23–86 % for loosely-coupled fusion; HortiMulti's consumer GPS (σ_z ≈ 7 m) is a
hardware floor.*

---

## 3. Findings

### 3.1 The IMU's value is excitation-dependent

![IMU excitation](../figures/fig_imu_excitation.png)

Under the near-constant-velocity ZED2i motion, scale and IMU biases are unobservable: OKVIS2, OKVIS2-X
and OpenVINS scale-collapse (Sim3 scale → 0, SE3 error diverging to 10⁵–10⁶ m) and ORB-SLAM3's VIO fails
outright, while stereo VO keeps metric scale at 0.26–0.45 m. On Rosario, with genuine turning, the same
inertial constraint corrects Basalt's scale drift (14 m/0.80 → 3 m/1.02) and rescues ORB-SLAM3 (below).
**An IMU on a field robot pays off only if the platform moves enough to excite it; on slow smooth
traversals it is actively harmful.**

### 3.2 Classical feature tracking hard-fails on crops — and ATE hides it

![ORB-SLAM3 mode progression](../figures/fig_orb_progression.png)

On low-texture repetitive rows ORB-SLAM3's descriptor matching collapses (135 "tracking lost" events and
8 map resets on Rosario seq1); it fragments into sub-maps and exports 40–60 % of the trajectory. Since
ATE is computed only over produced poses, its low agricultural VO error reflects the easy sub-path, not
accuracy — flow-based (OV2SLAM), learned (DPVO, MAC-VO) and sliding-window (OKVIS2, Basalt) front-ends
complete 100 % and drift instead of quitting. The progression figure shows the fix: **the IMU restores
coverage (58 → 99 %), then loop closure cuts the error (1.08 m)** — making ORB-SLAM3 VIO-LC the best
configuration on the benchmark's outdoor sequences. Coverage must accompany ATE in any comparison.

### 3.3 Loop closure is mechanism-dependent — and no mechanism is immune

![Loop-closure mechanism heatmap](../figures/fig_lc_mechanism.png)

Same-algorithm LC-on-vs-off comparisons across three independent implementations: proximity closure
(DPV-SLAM) fires false loops between look-alike rows and worsens every agricultural sequence; verified
iBoW/DBoW closure helps reliably on distinctive scenes (EuRoC −18 to −73 %) and on true revisits
(Rosario seq1: 4 loops → 1.52 m for ORB-SLAM3), but OV2SLAM blew up on str02 (+308 %) and OKVIS2-X on
str03 (+271 %) — single false matches that slipped past verification on short, aliased loops. Better
verification lowers the blow-up frequency; it does not eliminate it.

### 3.4 Reproducibility: one run is not enough on agricultural data

![Run-to-run determinism](../figures/fig_determinism.png)

With identical binaries and configs, Basalt / MAC-VO / AirSLAM reproduce within < 8 % CV and DROID-SLAM
was bit-exact, but ORB-SLAM3 varies up to ~4× between runs on the agricultural sequences (it operates at
its tracking-failure boundary, so thread timing decides *where* it fails; on texture-rich EuRoC it is
stable). Its agricultural cells are therefore reported as N=3 median + range. Ten further methods —
including all real-time/ROS-replay estimators, two of which (Voxel-SVIO, RTAB-Map) already showed
2×+ spread — are single-run so far; N≥3 for the VIO matrix is the main open rigor item.

---

## 4. Conclusions

Across the benchmark, every algorithm attains low ATE on the EuRoC reference, confirming the
implementations are sound and that agricultural degradation is environment-driven. The agricultural
spread is not a quality ranking but a map of robustness to three broken assumptions:

| Assumption broken by agriculture | Who breaks | Who survives |
|---|---|---|
| **Distinctive features** (low-texture rows) | ORB-SLAM3 → tracking loss + map fragmentation | optical-flow, learned, sliding-window → graceful drift |
| **Unique places** (identical rows) | proximity LC always; iBoW/DBoW occasionally (single false loops) | verified LC *on true revisits*; LC-off |
| **Inertial excitation** (slow smooth motion) | tightly-coupled VIO on ZED2i → scale collapse | stereo VO; or VIO where excitation exists |

Practical guidance for field robots: **choose by which assumption your platform violates.** Low texture →
avoid pure descriptor matching or add an IMU to bridge tracking gaps. Repetitive rows → disable loop
closure or use geometrically-verified closure and accept residual blow-up risk. Slow, smooth motion → do
not trust a tightly-coupled IMU; use stereo VO. Where excitation and true revisits both exist (Rosario),
the full stereo-inertial-LC stack (ORB-SLAM3 VIO-LC, 1.08 m) is the strongest configuration. Conventional
benchmarks obscure all of this by satisfying every assumption at once — which is precisely why an
agricultural benchmark, and the weak-excitation ZED2i sequence in particular, is needed.

## 5. Limitations / open items

- **N=1** for most VIO/GNSS cells (real-time estimators are structurally non-deterministic) — N≥3 pending.
- MASt3R-SLAM / MegaSaM require > 12 GB VRAM (21 cells hardware-blocked); MAC-VO ZED2i deferred (~6 h).
- ZED2i ground truth is position-only RTK; OKVIS-family LC on the 46k-frame ZED2i wedges in final BA
  (partial-coverage kill-to-flush results, 🟡).
- OpenVINS+GPS rows are pre-extrinsic-fix and must be re-run; two colleague-machine OKVIS2 VIO-LC runs
  retain an outdated loop-count metric pending re-evaluation on their origin machine.
- Machine provenance is stamped for all new runs but missing for ~100 early runs.

## 6. Appendix pointers

- Full per-mode CSVs: `benchmark-{vo,vo-lc,vio,vio-lc,gnss-vio}.csv` (110/40/55/25/22 rows).
- Per-mode aggregate plots (ATE / scale / FPS bars, ATE-vs-FPS Pareto): `results-<mode>/*.png`.
- Per-sequence multi-algorithm trajectory overlays: `results-<mode>/<dataset>/<seq>/plots/`.
- Detailed findings log and per-dataset notes: `PROGRESS.md` (findings 1–15); open work: `TODO.md`.
