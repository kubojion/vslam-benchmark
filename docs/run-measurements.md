# Run measurements

New runs use **measurement schema 2**. Input availability, published messages,
exported poses and processed frames are different quantities. No current runner
provides instrumented estimator frame counts or internal processing timers, so
`processed_frames`, `dropped_frames`, `processing_time_s` and `processing_fps`
remain `null` in every execution mode. A zero exit does not prove every frame was
processed, and a keyframe count is not an image-processing count.

## Common fields

`run_meta.json` stores a `measurements` object with:

- `input_frames`: timestamps available in the dataset;
- `published_frames`: camera pairs emitted by the benchmark ROS player;
- `publisher_dropped_frames`: expected pairs the player did not publish;
- `output_poses`: rows in the canonical trajectory;
- `input_duration_s` and `trajectory_duration_s`: their respective timestamp spans;
- `end_to_end_time_s`: the elapsed window explicitly measured by the wrapper;
- `end_to_end_fps`: **nominal available input frames per elapsed second**, not an
  observed estimator processing rate;
- `command_time_s` and `command_input_fps`: the maximum-throughput command window
  and nominal input count divided by that window, including initialization and
  finalization; unavailable for paced/transport pipelines;
- `trajectory_pose_rate`: output poses divided by trajectory duration;
- `realtime_factor`: dataset duration divided by wrapper elapsed time; this does
  not establish latency, deadline compliance, or complete processing;
- phase times, deadline misses and queue depth: `null` until directly instrumented.

The intended timing window is documented by `command_time_scope`. Wrapper windows
are not guaranteed to have equal phase boundaries across algorithms. Native or
ROS runtime validation must establish the actual scope before timing comparisons
are qualified. Deliberate pacing also limits comparisons of nominal rates.

## Execution modes

| Mode | Nominal command input FPS | Measured processing FPS/count | Intended use |
|---|---:|---:|---|
| `max_throughput` | Available | Unknown | Direct dataset command without deliberate pacing |
| `paced` | Unavailable | Unknown | Executors with dataset-time sleeps |
| `transport` | Unavailable | Unknown | Publisher/subscriber pipelines |

Adding real processing counters requires a documented instrumentation adapter and
an explicit validation contract. Schema 2 currently rejects processing claims
instead of accepting a number simply because it equals the dataset size.

## Historical schema 1 correction

Schema 1 assigned all input frames to `processed_frames` for direct/paced runs.
Its maximum-throughput `processing_fps` therefore used an assumed count. The
2026-10-01 audit found no per-run counter evidence establishing that assumption.

Original metadata is preserved. Schema-3 reevaluation now stores those original
claims under `runtime.legacy_processing_claims`, withholds them from processing
fields, and exposes the old command ratio under `command_input_fps` with an
unverified legacy scope label. The interpretation is versioned separately as
`measurement_interpretation_schema=2`. Browser schema-1 status is
`legacy_assumed_processing`, not current measurement completeness. Structural
schema-1 validation remains available for historical inspection.

The old top-level `fps` is also preserved as legacy metadata. Corrected CSV `fps`
and processing columns stay blank without instrumentation. These changes do not
alter pose accuracy, reference associations or numerical failure outcomes.

## Scoped resources and transport

`resources.csv` is sampled between explicit start/stop markers. Native and Conda
runners target their process tree; persistent Docker runners target the container;
hybrid OpenVINS pipelines include both. Fields include cumulative CPU time,
interval CPU percentage, aggregate RSS and available per-PID GPU measurements.
Container scope does not itself prove that unrelated manual work was absent.

Missing GPU telemetry is unknown, never zero. Whole-machine resource values are
not accepted as scoped schema-2 measurements. Older unscoped observations remain
historical evidence.

ROS players atomically record expected/published camera pairs, IMU/GNSS messages
and read failures in `transport_stats.json`. These establish source emissions;
they do not establish estimator receipt, processing or drops. Attempt process
states and shutdown signal logs are separate execution evidence, described in the
[runner audit](runner-isolation-audit.md).

## Validation

The repetition controller requires provenance schema 2 and measurement schema 2
for new attempts before completion validation:

```bash
python3 scripts/results/validate_run.py \
  results/<type>/<dataset>/<sequence>/<algorithm>/run<N> \
  --check-only --require-provenance 2 --require-measurements 2
```

Historical recovery can still evaluate a saved trajectory without a new schema-2
metadata record. It does not fabricate a COMPLETE marker, processing counter or
publication qualification. No estimator executions were used to validate this
measurement repair.
