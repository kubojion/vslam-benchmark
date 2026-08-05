# Brief for Claude on Ivan's machine (i9-14900HX / RTX 4080 — "machine B")

*Prepared 2026-08-05 on Jion's machine after the evaluation-pipeline fix campaign (commit
`39a4a4c`, see the "2026-08-05 — Evaluation-pipeline fixes" section of PROGRESS.md). Give this
whole file to Claude in this repo's root on Ivan's machine and ask it to execute the tasks in
order. It is addressed directly to that Claude.*

---

You are working in the `vslam-benchmark` repo on the machine that holds the **EuRoC, HortiMulti
and zed2i datasets** (this machine ran all current benchmark results). The evaluation pipeline
was overhauled on the other machine (commit `39a4a4c`): read the "2026-08-05 —
Evaluation-pipeline fixes" section of `PROGRESS.md` first — it defines `eval_schema: 2`,
`coverage_gap_pct`, the GT-interpolation fix, origin-aligned GNSS ATE, global-alignment
segments, the full-rebuild CSV builder, and GT provenance recording. Your job: bring THIS
machine's datasets and results up to the fixed pipeline, verify everything, push in small
commits, and report back the judgment calls instead of deciding them.

## Hard rules

1. `git pull` first; work on `main`; never force-push; small commits, one per task below.
2. **Never hand-edit a `benchmark-*.csv` or a results table** — the only path is
   results/ → `scripts/eval/_evaluate_run.py` → `scripts/eval/build_benchmark_csv.py` →
   `scripts/eval/make_report_tables.py`.
3. **Do NOT re-evaluate any `rosariov2` run** — those were re-evaluated on the other machine
   under the fixed GT and are final; re-running them here would only churn artifacts (and would
   use this machine's possibly-divergent seq1 GT until Task 1 is done).
4. **Do NOT overwrite `machine` blocks** in existing `run_eval.json` files; the evaluator
   preserves them — that behavior is intentional.
5. If any acceptance check fails, STOP that task, write what you found into the report
   (Task 5), and move on — do not improvise fixes to the pipeline itself.
6. Tuning re-runs (config-deviation follow-ups), N≥5 replication, and any SLAM re-runs are
   **out of scope** — they are team decisions; list them in the report only.

## Task 0 — Preflight (verify environment compatibility BEFORE touching anything)

- `git pull` and confirm `git log` contains `39a4a4c`.
- Find a python env with numpy/scipy/pandas and `evo_ape` on PATH (reference machine used
  evo **v1.36.4**; record your version).
- Compatibility smoke test: pick one existing **EuRoC** run (e.g.
  `results-vio/euroc_mav/MH_01_easy/basalt/run1`), back up its `run_eval.json`, re-run
  `python3 scripts/eval/_evaluate_run.py euroc_mav MH_01_easy basalt 1 vio`, and diff the
  legacy fields (`ate.rmse`, `ate_se3.rmse`, `rpe_trans_1m.rmse`, `scale_factor`,
  `n_pairs_ate`) against the backup — **they must match exactly** (GT unchanged at this
  point). If they differ, STOP: your evo/scipy version disagrees with the reference machine —
  report versions and the diff.

## Task 1 — Rosario seq1 dataset copy (forensics FIRST, then repair)

This machine's `datasets/rosariov2/sequence1/` is believed to hold a **divergent, wrong GT**
(a `conv.py` script and a 4703-row, 5 Hz, identity-quaternion `gt_tum.txt` built from raw
GPS). The authoritative GT is genuine PGT. Datasets are gitignored, so git did not carry the
fix.

1. **Capture forensics before changing anything** (into the Task-5 report): `ls -la` of the
   directory; `wc -l` of `gt_tum.txt`, `gt_interp_tum.txt`, `gps.csv`, `times.txt`; first 2
   rows of `gt_tum.txt`; full content of `conv.py` if present; mtimes.
2. Obtain the authoritative files from Jion (any channel — they are ~4 MB total) and verify
   sha256 prefixes and row counts:

   | file | sha256 (first 16) | rows |
   |---|---|---|
   | sequence1/gt_tum.txt | `6eef4e8ed3f0ce8f` | 8983 |
   | sequence1/gt_interp_tum.txt | `5b2bc209a5119873` | 13745 |
   | sequence1/times.txt | `2df7d34b8e144e6b` | 13821 |
   | sequence5/gt_tum.txt | `a886d339de70f9ac` | 7577 |
   | sequence5/gt_interp_tum.txt | `4b68867faf6fe8c8` | 11476 |
   | sequence5/times.txt | `896e64e6d5d88375` | 11640 |

   (Recommended alternative: Jion adds a `.gitignore` exception for `datasets/**/gt_*.txt` +
   `times.txt` and commits them — then this is just `git pull`. Check whether that commit
   exists before asking for a manual transfer.)
3. Replace this machine's seq1 (and, if hashes differ, seq5) GT files with the authoritative
   ones; archive the old ones as `gt_tum.txt.divergent-raw-gps` and move `conv.py` to the same
   archive naming — do not leave it executable in place.
4. Acceptance: sha256 of all six files match the table.

## Task 2 — Re-interpolate GT + re-evaluate EuRoC and HortiMulti (all run types)

1. For each of `euroc_mav/{MH_01_easy,MH_03_medium,MH_05_difficult}` and
   `hortimulti/{strawberry02,strawberry03}`:
   `python3 scripts/eval/_interpolate_gt.py datasets/<ds>/<seq>/gt_tum.txt datasets/<ds>/<seq>/times.txt datasets/<ds>/<seq>/gt_interp_tum.txt`
   — record the reported dropped-frame counts in the report.
2. Re-evaluate every euroc_mav and hortimulti run in all five results trees (adapt the loop
   pattern; run id must keep any variant suffix):
   ```bash
   for root in results-vo results-vo-lc results-vio results-vio-lc results-gnss-vio; do
     rt=${root#results-}
     for d in "$root"/{euroc_mav,hortimulti}/*/*/run*/; do
       [ -f "$d/trajectory.txt" ] || continue
       seq=$(echo "$d" | cut -d/ -f3); algo=$(echo "$d" | cut -d/ -f4)
       runid=$(basename "$d"); runid=${runid#run}
       python3 scripts/eval/_evaluate_run.py "$(echo "$d" | cut -d/ -f2)" "$seq" "$algo" "$runid" "$rt"
     done
   done
   ```
3. Rebuild everything: `python3 scripts/eval/build_benchmark_csv.py all`, then
   `python3 scripts/eval/make_report_tables.py --check`, then
   `python3 scripts/eval/verify_claims.py`, then `python3 scripts/eval/make_report_figures.py`.
4. Acceptance: zero failed evaluations; `--check` passes; produce an old→new shift table
   (per dataset, cells shifting >2%) for the report. Expectation: EuRoC shifts ≈0 (Vicon GT
   spans the sequences; if EuRoC moves >1% investigate before pushing); HortiMulti may move
   a few % if its GT had boundary clamping.
5. Commit + push (`run_eval.json`s, CSVs, `docs/generated/`, figures).

## Task 3 — zed2i: correct-lever-arm GT everywhere + re-evaluate

Published zed2i ATEs already used the correct 2.86 m interpolated GT (verified by exact
reproduction), **but** this machine's `gt_tum.txt` is the wrong 1.86 m file and it feeds the
segment maps, `segments_auto.csv`, and trajectory-overlay plots; the extractor default is
fixed to 2.86 in `scripts/data/_zed2i_ros2_extract.py`.

1. Regenerate/replace `datasets/zed2i/field1_110426_full_10fps_q90/gt_tum.txt` with the
   2.86 m version (either re-run the extractor's GT stage, or promote the existing
   `gt_measured_2p86*` data); archive the 1.86 file as `gt_tum.txt.wrong-1p86-lever`.
2. Regenerate `gt_interp_tum.txt` with the fixed interpolator; then regenerate
   `segments_auto.csv` (`_segment_trajectory.py`), the segment maps (`_plot_segments.py`) and
   `plot_comparison.py` figures for zed2i in all result trees.
3. Re-evaluate all zed2i runs (~18) across the five results trees (same loop as Task 2 with
   `zed2i`), rebuild CSVs/tables/claims/figures.
4. Acceptance: for full-coverage runs the new ATEs should match the published values closely
   (they were already scored against 2.86 interp; the interp fix may move them slightly —
   report the deltas); every zed2i `run_eval.json` now carries `gt_provenance` with the
   2.86-GT sha256; `environment_type` = agricultural in CSVs.
5. Also update `docs/zed2i_setup.md`: correct machine paths, state that the 1.86 file is
   wrong and archived, document the 2.86 derivation (see `PROGRESS.md` provenance note) and
   the 0.10 s camera↔robot clock offset.
6. Commit + push.

## Task 4 — Commit the local-only runtime prerequisites (fresh-clone reproducibility)

Check for uncommitted files this machine may hold: AirSLAM VIO launch files, OpenVINS
`Dockerfile.benchmark`, OKVIS2 DBoW2/opengv CMake patches (see TODO task 12). Commit them to
the appropriate fork branches (`vslam-benchmark-patches` pattern, as ORB_SLAM3/MAC-VO already
do) or, if a fork does not exist, stage them and list in the report. Do not commit large
binaries or datasets.

## Task 5 — Report back (committed file, not chat)

Write `docs/machine-b-report-<YYYYMMDD>.md` containing: Task-1 forensic capture; evo/python
versions; dropped-frame counts per sequence; the old→new shift tables for EuRoC/HortiMulti and
zed2i; every acceptance check result; anything skipped or failed and why; and a list of
**decisions needed from the team** (at minimum: the ~14 equalized tuning re-runs from
`PROGRESS.md`/config-deviation findings, the N≥5 replication campaign, uniform feeding
protocol re-runs, whether to git-track GT files). Commit + push it. Jion's machine will pull
and independently verify (GT hashes, spot re-evaluations, CSV diffs).
