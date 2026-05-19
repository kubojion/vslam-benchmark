# vSLAM Benchmark - Progress

BSc thesis benchmarking three SLAM algorithms on agricultural datasets.
Algorithms: **ORB-SLAM3** (classical), **DROID-SLAM** (neural), **MAC-VO** (hybrid).

---

## Results Summary

> All Rosario single-run results are from an earlier exploratory run (single run, old format).  
> HortiMulti Strawberry-03, Rosario seq1, and Rosario seq5 ORB-SLAM3 results are from the new **3-run multi-run benchmark** (mean ± std).
> Both **Sim(3)** and **SE(3)** ATE reported - see "Sim3 vs SE3" section below.

| Algorithm | Dataset | Seq | ATE Sim3 | ATE SE3 | Scale | Frames | Completion | Runs |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | Rosario v2 | seq1 | **1.176 ± 0.317 m** | **1.59 m** | 1.022 | 13 821 | 100% | **3** ✓ |
| DROID-SLAM | Rosario v2 | seq1 | 45.05 m | - | - | 6 911 | 100% (stride=2) | 1 |
| MAC-VO | Rosario v2 | seq1 | 13.519 m | - | - | 13 821 | 100% | 1 |
| ORB-SLAM3 | Rosario v2 | seq5 | **20.207 ± 4.204 m** | **20.85 m** | 0.904 | 11 640 | 91% avg (0 loops) | **3** ✓ |
| DROID-SLAM | Rosario v2 | seq5 | 44.94 m | - | - | 11 640 | 100% (external‡) | 1 |
| MAC-VO | Rosario v2 | seq5 | 19.381 m | - | - | 11 640 | 100% | 1 |
| ORB-SLAM3 | HortiMulti | Strawberry-02 | **0.893 ± 0.171 m** | **2.10 ± 0.12 m** | 1.040 | 4 186–4 980 / 9 530 | 44–52%† | **3** ✓ |
| DROID-SLAM | HortiMulti | Strawberry-02 | 44.91 m | - | - | 4 765 | 100% (stride=2) | 1 |
| MAC-VO | HortiMulti | Strawberry-02 | 10.007 m | - | - | 9 530 | 100% | 1 (run2+3 in progress) |
| ORB-SLAM3 | HortiMulti | Strawberry-03 | **0.1039 ± 0.0013 m** | **0.78 m** | 1.043 | 2 425 | 100% | **3** ✓ |
| MAC-VO | HortiMulti | Strawberry-03 | **0.505 ± 0.010 m** | **0.84 m** | 1.037 | 2 425 | 100% | **3** ✓ |

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
- Run scripts: `scripts/run/run_orbslam3.sh` (multi-run, resource monitor), `run_droidslam.sh` (multi-run ✓), `run_macvo.sh` (multi-run ✓)
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

### Sequence 1 - All three algorithms complete (single run)

- **Extracted to:** `datasets/rosariov2/sequence1/`
- **GT:** 8983 poses (GPS/PGT), 13821 camera frames; `gt_interp_tum.txt` generated✔
- **Segments:** 125 row segs (863 s), 20 turn segs (60 s) - `segments_auto.csv` generated✔
- **Config files:** ORB-SLAM3: `configs/orbslam3/rosariov2_stereo.yaml` · DROID-SLAM: `configs/droidslam/rosariov2.txt` · MAC-VO: `configs/macvo/rosario_v2_sequence.yaml`

| Algorithm | ATE RMSE | Frames | Completion | Runs |
|---|---|---|---|---|
| ORB-SLAM3 | 1.361 m (old single run) | 13 821 | 100% | 1 (old) |
| ORB-SLAM3 | **1.176 ± 0.317 m** | 13 821 | 100% | **3** ✓ |
| DROID-SLAM | 45.05 m | 6 911 | 100% (stride=2) | 1 |
| MAC-VO | 13.519 m | 13 821 | 100% | 1 |

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
| DROID-SLAM | **44.94 m** | 11 640 | 100% (external‡) | 1 |
| MAC-VO | **19.381 m** | 11 640 | 100% | 1 |

‡ Timestamps were in nanoseconds - converted to seconds before evaluation.

### Rosario v2 observations (updated with 3-run benchmarks)
- ORB-SLAM3 seq1: 1.176 m - 5-6 loop closures enable global correction → low drift
- ORB-SLAM3 seq5: 20.207 m - 0 loop closures, long straight rows → uncorrected scale drift
- DROID-SLAM consistently very poor (~45 m both seqs)
- MAC-VO: seq1 13.3 m, seq5 15.8 m - intermediate, consistent scale drift
- **Local accuracy is similar for all 3 ORB-SLAM3 sequences**: row ATE ≈ 0.016 m in seq1 AND seq5

---

## Dataset 2 - HortiMulti - In progress

### Strawberry-02 - All three algorithms complete

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
| MAC-VO | 10.007 m (run2+3 in progress) | 9 530 | 100% | 1 |

### Strawberry-03 - ORB-SLAM3 × 3 + MAC-VO × 3 complete

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

| Algorithm | ATE RMSE Sim3 | ATE SE3 | Scale | FPS | Frames | Completion | Runs |
|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | **0.1039 ± 0.0013 m** | 0.78 m | 1.043 | 9.39 | 2 425 | **100%** | **3** ✓ |
| MAC-VO | **0.505 ± 0.010 m** | 0.84 m | 1.037 | 1.54 | 2 425 | **100%** | **3** ✓ |
| DROID-SLAM | TBD | - | - | - | - | - | - |

### Config files

- ORB-SLAM3: `configs/orbslam3/hortimulti_stereo.yaml` (shared across all HortiMulti seqs)
- DROID-SLAM: `configs/droidslam/hortimulti.txt` (**no comments** - parser crashes on `#`)
- MAC-VO: `configs/macvo/hortimulti_sequence.yaml` (update `root:` path per sequence)

### HortiMulti observations

- ORB-SLAM3 best global accuracy on str03 (0.10 m Sim3); tracking lost on str02 after 44-52% of timeline (repetitive polytunnel)
- MAC-VO 100% completion on both sequences; ATE 10 m on str02 (long, ~953 s) vs 0.505 m on str03 (short, ~242 s) - drift scales with sequence length
- DROID-SLAM: 44.91 m on str02 (fresh eval, previously reported as 41.91 m with old eval)
- ORB-SLAM3 vs MAC-VO on str03: ORB-SLAM3 5x better globally (0.10 m vs 0.505 m) but MAC-VO completes more of long sequences

---

## Dataset 3 - LFSD - Not started

- Download and extract sequences
- Configure and run all three algorithms
- Evaluate ATE/RPE

---

## Pending work

| Task | Priority |
|---|---|
| **MAC-VO × 3 on Strawberry-02** - run1 done, run2+3 in progress | High |
| **MAC-VO × 3 on Rosario seq1** - run1 done, run2+3 pending | High |
| **MAC-VO × 3 on Rosario seq5** - run1 done, run2+3 pending | High |
| **DROID-SLAM × 3 on all 4 evaluated sequences** | High |
| Add Rosario v2 sequences 2, 3, 4 (already downloaded - TODO: extract + run) | Medium |
| LFSD dataset: download, extract, run, evaluate | Medium |
| Additional HortiMulti sequences (Strawberry-01, -04 if available) | Low |
| Detect & remove constant body↔camera rotation for proper RPE rotation evaluation on HortiMulti | Low |
| Cross-sequence aggregation (`evo_res`) once we have ≥3 sequences × 3 algorithms × 3 runs | Medium |
| Thesis comparison plots (LaTeX-ready PDFs) | High (before submission) |

---

## Research-paper readiness - honest assessment

**Current data inventory** (post Phase B):

| Item | Count | Threshold for SLAM paper |
|---|---|---|
| Multi-run benchmarks (3+ runs, statistics) | 4 sequences × 1-2 algos = **7 cells** (ORB-SLAM3 ×4, MAC-VO str03) | ≥ 5 sequences × ≥ 3 algos × ≥ 3 runs = 45 cells |
| Single-run sanity points | 6 cells (DROID, MAC-VO across 3 seqs) | not publishable alone |
| Datasets | 2 (Rosario v2, HortiMulti) | typically 3–4 |
| Algorithms | 1 fully benched (ORB-SLAM3) + 2 single-run | 3+ |
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
