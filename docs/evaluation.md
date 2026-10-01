# Evaluation

> Status reviewed 2026-10-01. The field definitions below describe current implementation,
> including known limitations. Publication blockers and current run counts are tracked in
> [the server audit](campaigns/server-status-20261001.md). Numeric reports are provisional.


The pipeline turns raw trajectories into per-segment ATE numbers and plots.
`scripts/run/run_benchmark.sh` runs the full chain automatically; this page
explains the individual steps and how to read the output.

## Run types and result layout

Every run is classified by a `run_type`:

| run_type   | IMU | LC  | GNSS | Results tree           | Aggregated CSV            |
|------------|-----|-----|------|------------------------|---------------------------|
| `vo`       | off | off | off  | `results/vo/`          | `benchmark-vo.csv`        |
| `vo-lc`    | off | on  | off  | `results/vo-lc/`       | `benchmark-vo-lc.csv`     |
| `vio`      | on  | off | off  | `results/vio/`         | `benchmark-vio.csv`       |
| `vio-lc`   | on  | on  | off  | `results/vio-lc/`      | `benchmark-vio-lc.csv`    |
| `gnss-vio` | on  | -   | on   | `results/gnss-vio/`    | `benchmark-gnss-vio.csv`  |

Paths are resolved by `scripts/_paths.sh` (bash, `resolve_run_type`) and
`scripts/eval/_run_type.py` (python, `resolve(name)` / `all_types()`).
Every eval and plotting script accepts a `--type` flag (Python) or a
fourth/fifth positional argument (Bash) selecting the run type.

## Pipeline

```
trajectory.txt  ──►  _evaluate_run.py    →  run_eval.json
multiple runs   ──►  _aggregate_runs.py  →  metrics.csv + report.md
all algos       ──►  _plot_segments.py   →  segment_map.png + segment_map_3d.png
benchmark.csv   ──►  plot_ate_vs_fps.py  →  ate_vs_fps.png
```

Steps are sequenced inside `scripts/run/run_benchmark.sh`. Run them by hand
when re-evaluating without re-running SLAM:

```bash
WS=$(pwd)
EVAL=$WS/scripts/eval
TYPE=vo          # or: vo-lc, vio, vio-lc, gnss-vio
DS=rosariov2     # or: hortimulti, euroc_mav
SEQ=sequence1    # or: sequence5, strawberry02, strawberry03, MH_01_easy ...
ALGO=macvo       # or: orbslam3, basalt, airslam, openvins, okvis2,
                 #     cifasis_gnss_si, rtabmap_gps, vins_fusion_gps (gnss-vio only)

# 1. Interpolate GT to SLAM timestamps (once per sequence, shared across run types).
#    Since 2026-08-05: out-of-range camera frames are DROPPED (no boundary clamping)
#    and GT gaps > max(0.5 s, 3x median GT dt) are masked (no bridging of RTK outages).
python3 $EVAL/_interpolate_gt.py datasets/$DS/$SEQ/gt_tum.txt \
    datasets/$DS/$SEQ/times.txt datasets/$DS/$SEQ/gt_interp_tum.txt  # [--max-gap S]

# 2. Auto-segment GT into row / turn segments (once per sequence)
python3 $EVAL/_segment_trajectory.py datasets/$DS/$SEQ

# 3. Evaluate every run for a given algo
for r in results/$TYPE/$DS/$SEQ/$ALGO/run*; do
    RUN_ID="${r##*run}"
    python3 $EVAL/_evaluate_run.py $DS $SEQ $ALGO "$RUN_ID" $TYPE
done

# 4. Aggregate runs (mean/std/median/min/max rows; input fps auto-resolved per dataset)
python3 $EVAL/_aggregate_runs.py $DS $SEQ $ALGO auto $TYPE

# 5. Plot trajectories (2D + 3D segment maps, all algos on this sequence)
python3 $EVAL/_plot_segments.py --type $TYPE $DS $SEQ

# 6. ATE vs FPS comparison across all sequences (per run-type)
python3 $EVAL/plot_ate_vs_fps.py --type $TYPE

# 7. Rebuild all aggregated CSVs from per-run JSONs (vo, vo-lc, vio, vio-lc, gnss-vio)
python3 $EVAL/build_benchmark_csv.py all
```

## What `report.md` contains

For each algorithm, on each sequence:

| Column | Meaning |
|---|---|
| `ATE SE3` | RMSE after rigid SE(3) alignment only (no scale). **Primary metric for stereo/VIO** (finding 4) — does not absorb scale drift. |
| `ATE Sim3` | RMSE after Sim(3) alignment (scale + rotation + translation). Primary only for monocular methods; secondary/diagnostic for stereo. |
| `ATE origin` | GNSS-VIO ATE after evo `--align_origin`: rigid rotation **and** translation aligning the first poses. It is not translation-only or raw global-frame GNSS error; initial heading error is absorbed. |
| `Scale` | Sim(3) scale factor recovered by the alignment. Far from 1.0 → systematic scale drift. |
| `RPE trans / rot` | The current translation field uses evo `point_distance`, the absolute difference of the two displacement magnitudes over 1-metre windows, **not** full relative-pose translation error. `*_se3` omits scale correction. Rotation requires valid orientation GT and consistent body/camera frames; ZED identity-quaternion placeholders do not qualify. |
| `drift_{10,50,100}m_pct` | Current point-distance residual over 10/50/100 m windows divided by the window length. No scale correction. This is **not standard KITTI translational drift**; fix/relabel before comparison with published KITTI numbers. |
| `coverage_gap_pct` | Current gap-aware time-support estimate (`_coverage.py`). Its gap threshold is max(2 s, 5 × median output interval), so very sparse outputs can hide long gaps. A common-support audit remains required. `track_pct` measures output rate; endpoint-span coverage ignores interior holes. |
| `ATE [row]` / `ATE [turn]` | Per-segment RMSE of the **globally SE(3)-aligned** trajectory (`segment_alignment=global_se3`, 2026-08-05). Legacy rows used an independent per-segment Sim(3) fit, which is degenerate on straight rows — do not compare across the two semantics. |
| `Frames` | Number of poses in `trajectory.txt` (keyframe-only for some algorithms). |
| `Loops` | Log-reported loop-closure events, parsed per-algorithm (orbslam3/okvis2/okvis2x/ov2slam/airslam/mast3r_slam). NOT verified accepted loops; blank = not instrumented. |
| `Duration` / `FPS` | Legacy reports may use output-poses per wall second. Current CSV builder uses `fps` as a processing-FPS alias when processing time is known, otherwise blank. Read explicit `processing_fps`, `end_to_end_fps`, `trajectory_pose_rate`, measurement mode and resource scope; see [run measurements](run-measurements.md). |
| `run_status` | ok / scale_collapse (Sim3 scale <0.1 or >10) / eval_failed. |

Multi-run aggregations report mean ± std (ddof=1) **plus median / min / max rows**; report tables
use `median (min–max)`, generated exclusively by `scripts/eval/make_report_tables.py`.

## What the plots show

`results/<type>/<ds>/<seq>/segment_map.png` overlays all algorithms vs ground truth.
`results/<type>/<ds>/<seq>/segment_map_3d.png` is the same view with an added Z axis.
Individual runs are drawn in light grey; the per-algorithm mean trajectory is
drawn thick in the algorithm's colour (ORB-SLAM3 green, MAC-VO orange, Basalt red,
AirSLAM light blue, OpenVINS purple). Ground truth is a dashed black line.

Per-algorithm plots (`results/<type>/<ds>/<seq>/<algo>/segment_map.png`) zoom in on
one algorithm with individual runs + mean.

`results/<type>/ate_vs_fps.png` shows ATE SE(3) vs FPS for every algo/sequence combination
(run `scripts/eval/plot_ate_vs_fps.py --type <type>` to regenerate).

## Sim(3) vs SE(3)

ORB-SLAM3 with stereo input is metric, so Sim(3) and SE(3) ATE should be
close. Large gaps (e.g. Rosario seq5: Sim3 approx 20 m, SE3 approx 21 m, scale 0.90)
indicate scale drift over long straight sections without loop closures.
MAC-VO uses calibrated stereo and belongs to the metric-scale comparison: use SE(3)
ATE as primary. DPVO/DPV-SLAM is monocular and needs Sim(3) for trajectory-shape comparison.
The current table generator incorrectly passes SE(3) for DPVO headline cells despite
claiming Sim(3) in its header; fix this before publication.
OpenVINS / OKVIS2 / Basalt are metric (stereo+IMU), so Sim3 and SE3 should
agree in successful tracking; a large scale error can reflect calibration, initialization,
tracking or estimator failure and does not uniquely diagnose IMU noise.

## Re-evaluating without re-running SLAM

After evaluator fixes, re-evaluate affected saved trajectories using the matching GT,
configuration/pose-frame provenance, run metadata and logs. Revalidate artifacts, then refresh
aggregates, CSVs, tables, claims and plots together. Preserve the earlier evaluations as a
separate version when semantics change; `eval_schema: 2` alone does not prove equivalent code.

`run_benchmark.sh` currently reuses GT interpolation and segmentation files whenever they
exist. It does not invalidate them by input hash. Verify these caches after any GT or timing
change before evaluating; do not assume that launching another benchmark repairs them.

`make_report_tables.py --check` checks its own rendering rules, not correctness of metric
semantics or completeness against a campaign manifest. Mixed-status cells currently qualify
for ranking if any repetition is `ok`, and bolding uses a dispersion heuristic rather than a
statistical significance test. Report attempted/evaluated/successful counts explicitly.

Before rebuilding exports, exclude the five COMPLETE smoke runs documented in the
[status audit](campaigns/server-status-20261001.md). Root CSVs, generated reports and the
browser are currently different snapshots; regeneration remains pending these repairs.
