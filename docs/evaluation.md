# Evaluation

The pipeline turns raw trajectories into per-segment ATE numbers and plots.
`scripts/run/run_benchmark.sh` runs the full chain automatically; this page
explains the individual steps and how to read the output.

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

# 1. interpolate GT to the SLAM timestamps (once per sequence)
python3 $EVAL/_interpolate_gt.py datasets/<ds>/<seq>

# 2. auto-segment GT into "row" / "turn" segments (once per sequence)
python3 $EVAL/_segment_trajectory.py datasets/<ds>/<seq>

# 3. evaluate every run for a given algo
for r in results/<ds>/<seq>/<algo>/run*; do
    python3 $EVAL/_evaluate_run.py <ds> <seq> <algo> "${r##*run}"
done

# 4. aggregate runs into mean ± std
python3 $EVAL/_aggregate_runs.py <ds> <seq> <algo>

# 5. plot trajectories (2D + 3D)
python3 $EVAL/_plot_segments.py <ds> <seq>

# 6. ATE vs FPS comparison across all sequences (run once after all data is in)
python3 $EVAL/plot_ate_vs_fps.py
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

`results/<ds>/<seq>/segment_map.png` overlays all algorithms vs ground truth.
`results/<ds>/<seq>/segment_map_3d.png` is the same view with an added Z axis.
Individual runs are drawn in light grey; the per-algorithm mean trajectory is
drawn thick in the algorithm's colour (ORB-SLAM3 green, DROID-SLAM brown,
MAC-VO orange, Basalt red, AirSLAM light blue). Ground truth is a dashed black line.

Per-algorithm plots (`results/<ds>/<seq>/<algo>/segment_map.png` and `segment_map_3d.png`) zoom in on
one algorithm, again with individual runs + mean.

`results/ate_vs_fps.png` shows ATE SE(3) vs FPS for every algo/sequence combination
(run `scripts/eval/plot_ate_vs_fps.py` to regenerate after adding new results).

## Sim(3) vs SE(3)

ORB-SLAM3 with stereo input is metric, so Sim(3) and SE(3) ATE should be
close. Large gaps (e.g. Rosario seq5: Sim3 ≈ 20 m, SE3 ≈ 21 m, scale 0.90)
indicate scale drift over a long straight section without loop closures.
DROID-SLAM and MAC-VO produce up-to-scale trajectories — always read Sim3
ATE for them.

## Re-evaluating without re-running SLAM

After tweaking `_evaluate_run.py` (e.g. a new metric), just re-run steps 3–5;
the SLAM trajectory files in `results/.../trajectory.txt` are the only input
needed.
