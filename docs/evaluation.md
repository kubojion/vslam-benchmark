# Evaluation

> Fully revised: 2026-05-30 - Added run-type flag examples; clarified CSV rebuild step; added segment-map and ATE-vs-FPS plot commands.

The pipeline turns raw trajectories into per-segment ATE numbers and plots.
`scripts/run/run_benchmark.sh` runs the full chain automatically; this page
explains the individual steps and how to read the output.

## Run types and result layout

Every run is classified by a `run_type`:

| run_type | IMU | LC  | Results tree         | Aggregated CSV         |
|----------|-----|-----|----------------------|------------------------|
| `vo`     | off | off | `results-vo/`        | `benchmark-vo.csv`     |
| `vio`    | on  | off | `results-vio/`       | `benchmark-vio.csv`    |
| `vio-lc` | on  | on  | `results-vio-lc/`    | `benchmark-vio-lc.csv` |

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
TYPE=vo          # or: vio, vio-lc
DS=rosariov2     # or: hortimulti, euroc_mav
SEQ=sequence1    # or: sequence5, strawberry02, strawberry03, MH_01_easy ...
ALGO=macvo       # or: orbslam3, basalt, airslam, openvins, okvis2, ...

# 1. Interpolate GT to SLAM timestamps (once per sequence, shared across run types)
python3 $EVAL/_interpolate_gt.py datasets/$DS/$SEQ

# 2. Auto-segment GT into row / turn segments (once per sequence)
python3 $EVAL/_segment_trajectory.py datasets/$DS/$SEQ

# 3. Evaluate every run for a given algo
for r in results-$TYPE/$DS/$SEQ/$ALGO/run*; do
    RUN_ID="${r##*run}"
    python3 $EVAL/_evaluate_run.py $DS $SEQ $ALGO "$RUN_ID" $TYPE
done

# 4. Aggregate runs into mean +/- std
python3 $EVAL/_aggregate_runs.py $DS $SEQ $ALGO 10 $TYPE

# 5. Plot trajectories (2D + 3D segment maps, all algos on this sequence)
python3 $EVAL/_plot_segments.py --type $TYPE $DS $SEQ

# 6. ATE vs FPS comparison across all sequences (per run-type)
python3 $EVAL/plot_ate_vs_fps.py --type $TYPE

# 7. Rebuild the 3 aggregated CSVs from per-run JSONs
python3 $EVAL/build_benchmark_csv.py all
```

## What `report.md` contains

For each algorithm, on each sequence:

| Column | Meaning |
|---|---|
| `ATE Sim3` | RMSE of absolute pose error after Sim(3) alignment (scale + rotation + translation). Use this to compare monocular / scale-ambiguous methods fairly. |
| `ATE SE3` | RMSE after rigid SE(3) alignment only (no scale). Reflects what a real robot would see. |
| `Scale` | Sim(3) scale factor recovered by the alignment. Far from 1.0 → systematic drift. |
| `RPE trans / rot` | Relative pose error on 1-metre windows. Local odometry quality. |
| `ATE [row]` | Per-segment ATE over straight rows only (no turns). |
| `ATE [turn]` | Per-segment ATE over turning segments only. |
| `Frames` | Number of poses in `trajectory.txt`. |
| `Loops` | Loop closures detected (ORB-SLAM3 only). |
| `Duration` / `FPS` | Wall-clock and frames per second. |

Multi-run aggregations report **mean ± std** across `run1`…`runN`.

## What the plots show

`results-<type>/<ds>/<seq>/segment_map.png` overlays all algorithms vs ground truth.
`results-<type>/<ds>/<seq>/segment_map_3d.png` is the same view with an added Z axis.
Individual runs are drawn in light grey; the per-algorithm mean trajectory is
drawn thick in the algorithm's colour (ORB-SLAM3 green, MAC-VO orange, Basalt red,
AirSLAM light blue, OpenVINS purple). Ground truth is a dashed black line.

Per-algorithm plots (`results-<type>/<ds>/<seq>/<algo>/segment_map.png`) zoom in on
one algorithm with individual runs + mean.

`results-<type>/ate_vs_fps.png` shows ATE SE(3) vs FPS for every algo/sequence combination
(run `scripts/eval/plot_ate_vs_fps.py --type <type>` to regenerate).

## Sim(3) vs SE(3)

ORB-SLAM3 with stereo input is metric, so Sim(3) and SE(3) ATE should be
close. Large gaps (e.g. Rosario seq5: Sim3 approx 20 m, SE3 approx 21 m, scale 0.90)
indicate scale drift over long straight sections without loop closures.
MAC-VO produces up-to-scale trajectories - always read Sim3 ATE for it.
OpenVINS / OKVIS2 / Basalt are metric (stereo+IMU), so Sim3 and SE3 should
agree; a scale far from 1.0 suggests IMU noise parameters are miscalibrated.

## Re-evaluating without re-running SLAM

After tweaking `_evaluate_run.py` (e.g. a new metric), just re-run steps 3-5;
the SLAM trajectory files in `results/.../trajectory.txt` are the only input
needed.
