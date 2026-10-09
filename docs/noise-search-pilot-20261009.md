# Short-clip IMU-noise search pilot

This experiment is separate from the Rule C N=3 campaign. The main worktree
remains `/data/imoroz/vslam-benchmark`. This branch uses its own prepared
metadata, source/build copies, containers, configs, evaluation outputs and logs.
The only shared scheduling mechanism is the existing main execution lock,
opened read-only and held during each attempt. Production images are mounted
read-only. Never launch this pilot concurrently with an unmanaged production run.

## Fixed experimental protocol

- Cases: ORB-SLAM3/Rosario; AirSLAM/Citrus; Voxel-SVIO/Citrus;
  AirSLAM/HortiMulti. Full targets: sequence1, seq04, seq04, strawberry03.
- Development: exact first 180 seconds of both prepared recordings per dataset.
  Preserve the original initial stationary/motion history, integer camera stamps,
  camera geometry and camera-clock IMU data. Keep IMU samples until 20 ms after
  the last retained image for interpolation. Do not retime or reinitialize
  arbitrary middle-of-recording windows.
- Per case: 16 candidate vectors × 2 clips = 32 attempts. This is a small
  fixed-budget search, not evidence of an optimum. Optuna 4.5.0 multivariate TPE,
  seed 20261009, eight startup trials (including two enqueued controls).
- Four positive continuous standard-deviation parameters are searched in log
  space: gyro/accelerometer noise density and gyro/accelerometer bias random
  walk. Bounds per component are `[min(C, historical)/10,
  max(100*C, 3*historical)]`. The same bound-construction rule applies to every
  case. Historical settings informed the seeds and bounds; disclose this.
- Controls: current Rule C and archived historical noise values. For Rosario
  ORB-SLAM3 the historical values are essentially rounded Rule C, not an
  envelope. All controls receive the same current non-noise settings and builds.
- Repeat the top two short-screening candidates twice on each clip: eight
  additional attempts per case. Choose between these two using all three
  repetitions. This limited shortlist verification does not estimate every
  candidate's run-to-run distribution.
- Full VIO: Rule C, historical control and the two repeated finalists; deduplicate
  by candidate identity. Full VIO-LC: Rule C and the short-selected winner where
  supported. Voxel-SVIO has no LC. Each full diagnostic is N=1; these are not the
  production N=3 results. No full result feeds back into the search.
- Maximum: 160 short attempts and 22 full attempts, including smoke tests which
  count as the first Rule C screening attempt and are reused, never discarded.

## Scoring and limitations

Use the existing evaluator's SE(3) position RMSE, camera-clock association,
reference support and pose-frame handling. Experimental prefix aliases must
match their parent timestamps exactly and satisfy stored SHA-256 checks.
Keep existing frame/reference qualification limitations; these are exploratory
results, not automatically publication-qualified measurements.

For each clip define exported support `s`: minimum of export span and gap-aware
temporal coverage for dense exporters; export span for AirSLAM. AirSLAM exports
keyframes, so its low pose/frame count is not interpreted as dropped tracking.
Span alone cannot prove uninterrupted tracking; report keyframe counts and gaps.
Fail a clip if the wrapper exits nonzero, the evaluator reports failure or scale
collapse, RMSE is missing/non-finite, or `s < 0.9`.

Candidate loss = `10 * number_of_failed_clips + mean(RMSE/(reference_path_length + RMSE) + (1-s))`.
Missing RMSE contributes 1 to its bounded error term. Average over the same
clips/repetitions for every compared candidate. Failure count dominates bounded
error/coverage terms, including during the six-observation repeat stage.
Reference path length uses the full clip's
supported camera times, not the estimator's shorter exported trajectory.
This is a declared operational ranking, not a universal definition of success.

The clips and full targets have already been inspected, and full targets contain
their development prefixes. Full runs test short-to-long ranking stability;
they are **not independent final testing**. A later paper experiment needs a
frozen development/test split and equal budgets. HortiMulti strawberry03 is only
about four minutes: its full extension is particularly weak evidence of
generalization. No promise is made that tuning improves Rule C or the envelope.

## Running and stopping

From this worktree:

```bash
.venv/bin/python scripts/analysis/noise_pilot.py
.venv/bin/python scripts/analysis/noise_pilot.py --execute --stage smoke
.venv/bin/python scripts/analysis/noise_pilot.py --execute --stage short
.venv/bin/python scripts/analysis/noise_pilot.py --execute --stage all
```

Artifacts: `/data/imoroz/IMU-NOISE-ISSUE2/noise-search-20261009/`.
Create `STOP_AFTER_CURRENT` there to stop between attempts. It never terminates
an active production run. A partial experimental attempt halts resume for review;
it is never silently overwritten or retried. The controller preserves candidate
configs, wrapper logs, native runtime/config/input provenance and all failures.
Optuna replay reconstructs the seeded sampler from completed scores and checks
candidate identities before resuming.
All four short searches finish before any full validation begins. A whole-attempt
timeout is retained as an experimental failure even if the wrapper could not
finish its final metadata; ordinary missing metadata stops the controller for
infrastructure review.

Sources: [Optuna TPE](https://optuna.readthedocs.io/en/v4.5.0/reference/samplers/generated/optuna.samplers.TPESampler.html),
[ask-and-tell](https://optuna.readthedocs.io/en/v4.5.0/tutorial/20_recipes/009_ask_and_tell.html).
