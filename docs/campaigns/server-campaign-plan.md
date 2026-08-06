# N=5 server campaign plan (RTX 3090 / 24 GB)

*Written 2026-08-06. Answers: can this repo run the whole benchmark automatically at N=5 on the
server? — **Yes.** The laptop phase already built exactly what a server campaign needs: one
command per cell (`run_benchmark.sh <ds> <seq> <algo> 5 <type>`), run-time provenance
(config sha256, playback rate, machine identity), deterministic results→CSV→tables regeneration,
GT files in git, and vendored runtime prerequisites. What remains is setup + three decisions.*

---

## 1. What already works for the server (nothing to build)

- `run_benchmark.sh` takes N as an argument — `... <algo> 5 <type>` is the N=5 loop.
- Every run records provenance (`_enrich_run_meta.py`): config hash, playback rate, env
  overrides, container image, **run-host machine** — server runs will be attributed correctly
  and automatically.
- Evaluation → CSV → tables → claims is fully scripted and proven byte-reproducible across
  machines (`build_benchmark_csv.py` full-rebuild; `make_report_tables.py --check`).
- Aggregation emits median/min/max — the N=5 statistics the report needs come out of the
  pipeline without new code.
- Fork submodules carry the AirSLAM launch files + OpenVINS Dockerfile; `vendor/prerequisites/install.sh` applies the remaining OKVIS2 external CMake patches.
- Rosario GT/times are git-tracked (machine B: commit euroc/hortimulti/zed2i GT the same way —
  then the server gets ALL ground truth via `git pull`).

## 2. Setup checklist (one-time, before the campaign)

| step | detail |
|---|---|
| S1 | Clone with `--recurse-submodules`; run `vendor/prerequisites/install.sh` |
| S2 | **Datasets**: rsync from machine B (the reference copy): rosariov2, hortimulti, zed2i, euroc_mav under `datasets/`. Verify GT against git-tracked files (sha256 must match) |
| S3 | **Builds**: `scripts/build/` for native (ORB_SLAM3 + Pangolin, OKVIS2, OKVIS2-X); Basalt binary — **record the exact version** in a `BASALT_VERSION` file (currently unpinned, audit item); conda envs for DPVO/MAC-VO; `docker build` the six containers from the committed Dockerfiles — **pin base images by digest** and record image IDs |
| S4 | **GPU-specific**: RTX 3090 = Ampere sm_86. DPVO/MAC-VO torch wheels must match CUDA; **AirSLAM's TensorRT engines are GPU-specific — they must be rebuilt on the 3090** (first run regenerates them; do a smoke run before the campaign); MASt3R/MegaSaM optional revisit (24 GB may clear the 12 GB OOM) |
| S5 | **Headless**: viewers are off in configs; if any tool still wants X, use `xvfb-run`. Smoke-test one cell per algorithm (EuRoC MH_01 is the cheap check) and compare against the committed values — the evaluator's legacy fields must reproduce |
| S6 | Idle-machine guard: campaign driver refuses to start a run if loadavg is high (the real-time-fed algorithms are load-sensitive — PROGRESS.md:308) |

## 3. Three decisions to make BEFORE launching (they define the protocol)

1. **Feeding protocol (C2)** — the current split (7 algorithms offline file-fed at max speed,
   7 real-time ROS-fed at rate 1.0, OV2SLAM once at 0.5) is the benchmark's biggest fairness
   hole. Recommendation: define protocol **A (accuracy)** = every ROS-fed algorithm at ONE
   uniform slowed rate (e.g. `*_PLAYBACK_RATE=0.5`) so no frames drop — used for all ATE
   tables; protocol **B (real-time)** = rate 1.0, run once per cell, used only for the
   robustness/FPS discussion. The rate is now recorded in run_meta, so the two protocols are
   distinguishable in the artifacts forever.
2. **The 🔁 config A/Bs (C13)** — fold into the same campaign as extra cells: OKVIS2 +
   OKVIS2-X Rosario with the HortiMulti frontend (8 cells), OKVIS2 hortimulti VIO-LC with the
   tuned frontend (2), Basalt hortimulti with default config + non-inflated IMU noise (4),
   ORB-SLAM3 zed2i VO at nFeatures 1200 (1), OKVIS2-X Rosario GNSS with measured `r_SA`
   (needs the Rosario robot's antenna offset from the dataset paper/authors — if
   unobtainable, document as limitation). Name variant runs `run<N>_<variant>` — the CSV's
   `gnss_variant`/run-dir mechanism already keeps them separate.
3. **Scope of N=5** — recommendation: all agricultural cells at N=5; EuRoC control at N=5
   only for the non-deterministic group (ORB-SLAM3, AirSLAM, OV2SLAM, OpenVINS, Voxel-SVIO,
   RTAB-Map), N=1 confirmation for the deterministic group (Basalt, MAC-VO, OKVIS2, OKVIS2-X,
   DPVO — finding 8). zed2i (77 min/run) is the long pole: N=5 x ~10 algo-modes ≈ 2.5-3
   machine-days alone; decide whether MAC-VO zed2i (~6 h/run) is in.

## 4. Runtime envelope (rough, serial execution)

Sequence wall-times ≈ real-time or slower for ROS-fed at 0.5x: seq1 ~16 min, seq5 ~13 min,
str02 ~16 min, str03 ~4 min, zed2i ~77 min (x2 at 0.5 rate for ROS-fed). Order of magnitude:

- Core agri (seq1/seq5/str02/str03) x ~30 algo-mode combinations x N=5 ≈ **6-9 machine-days**
- zed2i x ~10 combinations x N=5 ≈ **3-5 machine-days** (dominated by slow algorithms)
- EuRoC non-deterministic control ≈ 1-2 machine-days
- 🔁 A/B cells ≈ 1 machine-day

**Total ≈ 2-3 machine-weeks serial.** Parallelism caution: never run two REAL-TIME-fed cells
concurrently (accuracy is load-dependent); offline file-fed cells could run 2-way parallel at
the cost of contaminated CPU/RAM columns — recommend serial for anything feeding the report,
parallel only for smoke tests.

## 5. Campaign driver

A ~40-line queue script (to write at setup time): reads a cell list
(`dataset seq algo N run_type [VARIANT_ENV=...]`), loops `run_benchmark.sh`, checks loadavg
before each run, logs to `logs/server-campaign/`, applies the documented retry policy
(re-run once on `run_status != ok` with the trigger logged, keep both runs), and on completion
runs `build_benchmark_csv.py all && make_report_tables.py --check && verify_claims.py`.
Keep the cell list in git — it IS the campaign definition.

## 6. After the campaign

`git add results-*/ benchmark-*.csv docs/generated/ && git commit` — the tables and claims
regenerate themselves; the N=5 `median (min-max)` cells appear automatically wherever N≥2
exists. Then the paper's evaluation chapter is writable directly from `docs/generated/`.
