# Evaluation

Status: 2026-10-01, repair in progress. Schema-3 evaluations and reconciled exports
are validated in `results/repair-20261001/`. Root CSVs, old per-cell reports and the
results browser remain legacy snapshots until promotion. Scientific qualification
is still incomplete; numerical evaluation alone never awards an N=3 green tick.
See [the repair audit](repair-audit-20261001.md) and [the goal](codex-goal.md).

## Run types and inventory

| Mode | IMU | Loop closure | GNSS | Results | CSV |
|---|---|---|---|---|---|
| VO | off | off | off | `results/vo/` | `benchmark-vo.csv` |
| VO-LC | off | on | off | `results/vo-lc/` | `benchmark-vo-lc.csv` |
| VIO | on | off | off | `results/vio/` | `benchmark-vio.csv` |
| VIO-LC | on | on | off | `results/vio-lc/` | `benchmark-vio-lc.csv` |
| GNSS-VIO | on | algorithm/config dependent | on | `results/gnss-vio/` | `benchmark-gnss-vio.csv` |

`build_repair_inventory.py` enumerates the executed four-mode N=3 campaign and the
20 legacy GNSS default cells with a future N=3 target. The five CSVs contain all
660 planned default slots, including missing and failed attempts, plus six separate
legacy GNSS input-variant rows: **192 VO, 144 VO-LC, 168 VIO, 96 VIO-LC, 66 GNSS-VIO**.
They are not 666 successful runs. Historical excluded algorithms and smoke attempts
remain in the inventory and are excluded from headline CSVs.

Inventory evidence hashes are verified before export. The cohort identity includes
saved config/model hashes, source revisions/diffs, binary hashes, parameters,
workspace provenance, environment/container records and machine identity. DPVO's
repetition seed is deliberately excluded from the cohort signature, but retained
in attempt metadata; no other parameter is ignored. A signature groups recorded
evidence, not proof that missing provenance has been recovered. Unverified legacy
attempts remain separate rather than being pooled by a common `unknown` label.
Historical Git hashes remain historical after the author rewrite; see the
[mapping](campaigns/git-author-rewrite-20261001.json).

## Evaluation definitions

The evaluator reads immutable saved poses and the raw reference, verifies saved
configuration evidence, and transforms sensor origins only where supported by
source/calibration evidence. It never substitutes a current config for an absent
historical snapshot. See `_pose_frames.py` and each evaluation's `pose_frames`.

| Field | Schema-3 meaning |
|---|---|
| `primary_ate_rmse_m` | SE(3) rigid alignment for metric stereo/VIO; Sim(3) shape alignment for monocular DPVO. Metres. |
| `ate_se3_rmse_m`, `ate_sim3_rmse_m` | Both residuals retained explicitly. Sim(3) absorbs scale error and is diagnostic for metric methods. |
| `position_metric_validity` | Verified common camera origin or provisional sensor-origin diagnostic. Unknown agricultural reference frames remain explicit. |
| `rpe_trans_1m_se3_rmse_m` | Norm of the translation of `inverse(delta_reference) * delta_estimate`, after SE(3) alignment. Blank when orientation/origin evidence is inadequate. |
| `rpe_trans_1m_rmse_m` | Corresponding full relative-pose translation residual after Sim(3) alignment; retained compatibility name. |
| `rpe_rot_1m_rmse_deg` | Full relative rotation residual, degrees. Withheld for identity-quaternion ZED references and unknown frame chains. |
| `displacement_magnitude_error_1m_*_rmse_m` | Absolute displacement-magnitude difference (the old evo `point_distance` quantity). This is a different metric from full relative-pose translation error. |
| `drift_{10,50,100}m_pct` | RMSE of full SE(3) relative translation divided by each actual reference path-window length ×100. Custom overlapping windows, **not KITTI**; unavailable without valid reference poses. |
| `scale_factor` | Sim(3) fitted scale. For metric estimators, the retained diagnostic collapse threshold is outside [0.1, 10]. Monocular scale is unobservable and is not subjected to that failure threshold. |
| `ate_origin_*` | Intentionally blank. Legacy evo origin alignment rotated and translated the first pose; it was not verified GNSS global error. |
| `position_only_diagnostic_ate_se3_rmse_m` | Optional positional diagnostic for an invalid-orientation GNSS export. Does not change failed full-pose status or establish global accuracy. |
| `ate_row_rmse_m`, `ate_turn_rmse_m` | Mean of geometric path-segment RMSEs after one whole-trajectory alignment: SE(3) for metric methods, Sim(3) for DPVO. Segment labels are geometric, not human annotated. |

Association selects one observed estimate within 5 ms of each camera timestamp;
estimates are not interpolated. Reference position/orientation are interpolated at
the selected estimate time with a maximum reference gap of 0.5 s. Scoring requires
at least ten supported pairs. Distance windows use the first endpoint at/above the
requested path length, at most 10% overshoot, and reject unsupported time gaps.
The complete protocol and evaluator source hashes are stored in every JSON.

### Coverage is separate from reference availability

- `camera_pose_coverage_pct`: distinct associated exported poses / input camera frames.
- `reference_pairs_pct_of_input`: reference-supported evaluated pairs / input frames.
- `reference_supported_pose_pct`: evaluated poses associated to reference-supported
  camera timestamps / reference-supported camera frames.
- `trajectory_time_coverage_pct`: export endpoint span clipped to the input interval.
- `coverage_gap_pct`: sum of exported intervals no longer than
  `max(0.5 s, 5 × median camera interval)`, divided by input duration. It measures
  observed export support, not proven tracking success.

Ground-truth outages do not reduce exported-pose coverage. AirSLAM keyframe exports
have no dense `coverage_gap_pct`; their gaps do not establish tracking loss.
Output poses are never renamed processed images or tracked frames. Unknown tracking
loss/initialization instrumentation stays blank. Deprecated raw-path-length and
path-normalized ATE CSV fields are also blank pending a defensible common-support
path definition; old unsupported numbers are not copied forward.

### Execution, failure and qualification

The CSV separates numerical `run_status`, process exit, artifact presence and
scientific qualification. `ok` means the saved trajectory could be evaluated under
the stated metric/frame limitations; it does not prove a clean estimator exit or
publication readiness. Nonzero exits with usable trajectories remain visible.
Missing attempts, invalid trajectories and scale collapses remain in the denominator.

Per-cell `metrics.csv` contains only repetition records; `summary.json` holds
cohort-specific counts and conditional statistics. `report.md` shows counts,
failures, exits and blockers. Sample SD is unknown for N<2. Main tables use median
(min–max), report evaluated/planned counts, separate cohorts and input variants, and
do not rank unqualified results. No `any ok` condition creates a green tick.

## Runtime

Only explicitly recorded measurement fields are exported. `fps` is a compatibility
alias for known processing FPS; output-pose density and legacy wall FPS are not
substitutes. Dataset rate is observed from integer-nanosecond input timestamps.
Paced, transport-driven and maximum-throughput modes stay distinct. Unknown machine
identity is not replaced by the evaluation/report host. See [run measurements](run-measurements.md).

## Re-evaluation and regeneration

`run_benchmark.sh` delegates to the safe per-run controller. Existing attempt IDs
are never estimated again or deleted; saved trajectories are evaluated immediately,
even after a nonzero estimator exit. Cached evaluation reuse requires matching input,
configuration and evaluator hashes. Previous metrics are independently preserved in
`.evaluation_history/`; historical `COMPLETE` markers remain unchanged.
`--recover-only` forbids estimation. No estimator execution is authorized during
this repair. Legacy GT interpolation and segmentation caches are not consumed by
the schema-3 evaluator.

The following commands only rebuild derived staging outputs from saved evidence:

```bash
PY=/data/imoroz/conda/envs/macvo/bin/python
python3 scripts/campaign/build_repair_inventory.py
$PY scripts/eval/build_benchmark_csv.py all --output-dir results/repair-20261001/exports
$PY scripts/eval/_aggregate_runs.py --all --output-root results/repair-20261001/cell-reports
$PY scripts/eval/make_report_tables.py --csv-dir results/repair-20261001/exports --output-dir results/repair-20261001/tables
$PY scripts/eval/_aggregate_runs.py --all --output-root results/repair-20261001/cell-reports --check
$PY scripts/eval/make_report_tables.py --csv-dir results/repair-20261001/exports --output-dir results/repair-20261001/tables --check
```

`--check` is read-only: it regenerates expected bytes in memory and rejects stale
source CSVs or report contents. This proves reconciliation with the hash-checked
inventory, not scientific correctness by itself. Replaced derived files are
preserved under `results/.derived-history/` before atomic replacement.

Legacy trajectory/segment/FPS figures and the browser still need schema-3
integration and promotion. They must not be presented as current repaired evidence.
The earlier hand-transcribed/legacy report definitions are preserved in Git and the
verified pre-repair backup, rather than mixed with this protocol.
