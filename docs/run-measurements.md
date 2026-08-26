# Run measurements

New benchmark runs use measurement schema 1. The schema separates estimator
throughput, pipeline elapsed time, trajectory density, and dataset pacing so a
sparse or deliberately real-time estimator is not rewarded or penalized by an
ambiguous `poses / wall time` value.

## Common fields

`run_meta.json` stores a `measurements` object with:

- `input_frames`: stereo timestamps available to the run;
- `processed_frames`: frames submitted by a completed direct dataset loop, or
  `null` when a ROS subscriber does not expose a receive counter;
- `published_frames`: stereo pairs emitted by a benchmark ROS player;
- `dropped_frames`: estimator-side drops, kept `null` unless measured by the
  estimator;
- `publisher_dropped_frames`: source frames that the benchmark player could
  not publish, reported separately from downstream drops;
- `output_poses`: rows in the canonical trajectory;
- `processing_time_s` and `processing_fps`: available only when the estimator
  runs at maximum throughput without artificial pacing;
- `initialization_time_s`, `steady_state_time_s`,
  `final_optimization_time_s`, and `shutdown_time_s`: nullable phase timings,
  left `null` until an estimator exposes trustworthy boundaries;
- `end_to_end_time_s` and `end_to_end_fps`: elapsed pipeline time and input
  frames per elapsed second;
- `trajectory_pose_rate`: output poses per second of trajectory time;
- `realtime_factor`: dataset duration divided by end-to-end elapsed time.
- `deadline_misses` and `max_queue_depth`: nullable real-time diagnostics,
  never inferred from trajectory sparsity.

The old top-level `fps` remains in runner metadata for compatibility and is
explicitly labelled `legacy_fps_semantics`. New evaluation, CSV, manifest, and
HTTP pages do not use it as processing throughput.

## Execution modes

| Mode | Processing FPS | Processed frames | Intended use |
|---|---:|---:|---|
| `max_throughput` | Recorded | All input frames after successful completion | Offline direct-dataset algorithms |
| `paced` | Unavailable | All input frames after successful completion | Executors with deliberate dataset-time sleeps |
| `transport` | Unavailable | Unavailable unless the estimator exposes it | ROS publisher/subscriber pipelines |

For `max_throughput`, processing time covers the estimator command including
its initialization and finalization. It does not pretend to be tracker-only
kernel time. Paced and transport runs never derive processing speed from
trajectory rows.

## Scoped resources

`resources.csv` is sampled only between the runner's explicit measurement
start and stop markers. It excludes setup, stale-process cleanup, provenance
hashing, and evaluation.

Native and Conda runners measure their runner process tree. Persistent Docker
runners measure the host PIDs in that container. Hybrid OpenVINS pipelines
measure both the host process tree and the estimator container. Recorded
columns are cumulative CPU time, interval CPU percentage, aggregate RSS,
per-PID NVIDIA memory, and per-PID NVIDIA SM utilization.

GPU fields are empty when the NVIDIA driver does not expose a per-PID value;
empty never means zero. Whole-machine GPU, CPU, or RAM values are not accepted
for schema-1 runs.

## ROS transport accounting

The repository ROS players atomically write `transport_stats.json` with
expected and published camera pairs, published IMU/GNSS messages, and camera
read failures. These prove what the benchmark source emitted. They do not
prove what an estimator subscriber received, processed, or dropped. Those
fields remain `null` until an algorithm provides a trustworthy counter.

## Validation

`run_benchmark.sh` requires both provenance schema 2 and measurement schema 1
before writing `COMPLETE`:

```bash
python3 scripts/results/validate_run.py \
  results/<type>/<dataset>/<sequence>/<algorithm>/run<N> \
  --check-only --require-provenance 2 --require-measurements 1
```

Historical runs without measurement schema 1 remain browseable as `legacy`.
They are not retroactively assigned scoped resource or processing metrics.
