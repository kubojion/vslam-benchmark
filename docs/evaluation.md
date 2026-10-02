# Evaluation

Status: 2026-10-02, saved ZED re-evaluation and reporting reconciliation. The
[protocol review](protocol-review-20261002.md) and [ZED preparation](zed-preparation-20261002.md)
separate validity from success: 81 verified N=3 cells, with all failures retained.
ZED uses the pinned, gap-aware nominal 3D position reference; no rotational metric
is supported. Other agricultural/GNSS limits and native readiness remain separate.
Numerical scores alone never grant verification. Short-check exports are diagnostic
artifacts and do not fill production repetition slots.

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

The [explicit acceptance ledger](campaigns/paper-acceptance-20261001.json) pins each
reviewed default observation and numerical content. `paper_usable` includes stated
limited claims and observed failures; `accuracy_eligible` excludes failure-only
claims. `paper_ready` describes an accepted repetition, while `clean_qualified_n3` (legacy audit field)
additionally requires three consistent, dense, zero-exit repetitions with no native
fatal log observations. `native_error_observation_count` exposes errors masked by a
wrapper zero exit. Claim limits and reproducibility disclosures accompany the score;
neither acceptance flag grants future execution readiness.

## Runtime

Processing claims require instrumentation, not just a recorded number. Historical
schema-1 processing counts/FPS were inferred from input availability and are now
withheld, with their original values retained in evaluation audit fields. `fps`
is a compatibility alias for measured processing FPS and is currently blank.
`command_input_fps` and `end_to_end_fps` are explicitly nominal input/time ratios;
neither establishes complete processing or real-time latency. Dataset rate is
observed from integer-nanosecond input timestamps.
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

The following commands rebuild published derived outputs from saved evidence;
they never launch estimators:

```bash
PY=/data/imoroz/conda/envs/macvo/bin/python
python3 scripts/campaign/build_repair_inventory.py
$PY scripts/eval/build_benchmark_csv.py all
$PY scripts/eval/_aggregate_runs.py --all
$PY scripts/eval/make_report_tables.py
$PY scripts/eval/verify_claims.py
$PY scripts/eval/make_report_figures.py
$PY scripts/results/build_manifest.py
$PY scripts/results/build_site.py
$PY scripts/eval/_aggregate_runs.py --all --check
$PY scripts/eval/make_report_tables.py --check
$PY scripts/eval/verify_claims.py --check
$PY scripts/eval/make_report_figures.py --check
```

`--check` is read-only: it regenerates expected bytes in memory and rejects stale
source CSVs or report contents. This proves reconciliation with the hash-checked
inventory, not scientific correctness by itself. Replaced derived files are
preserved under `results/.derived-history/` before atomic replacement.

After an explicit claim-review change, run `build_repair_inventory.py`,
`reconcile_qualification.py`, rebuild the inventory, promote with
`promote_repaired_evaluations.py --apply`, and rebuild the inventory again before
the CSV/report commands. These steps preserve numerical fields and earlier JSONs.
Then run `update_todo_matrices.py`, `build_acceptance_handoff.py` and
`build_future_manifest.py`. Changed pinned evidence blocks a prior decision;
normal regeneration never makes new acceptance decisions automatically.

For changed evaluation code or input evidence, back up staging and regenerate with
`reevaluate_saved_runs.py --stage results/repair-20261001`, then rebuild/check the
inventory. `promote_repaired_evaluations.py` performs a read-only promotion preflight;
`--apply` preserves previous JSONs and promotes checked staging. Rebuild the inventory
after promotion, then regenerate the dependent outputs above. An interrupted promotion
can resume after inventory reconstruction; matching targets are skipped. Do not change
original run metadata to make qualification checks pass.

The browser generator consumes the same inventory, with separate numerical,
execution, qualification, variant and membership fields. Its schema-2 manifest and
690-entry browser are at `results/manifest.json` and `results/site/`. Each detail
page links the current numerical evaluation separately from historical artifacts;
legacy figures are labelled and not previewed as repaired plots. Historical/smoke
entries are outside the default browser filter.

Current all-mode figures use checked CSVs, separate scale models/cohorts and carry
explicit acceptance/limitation/blocker labels. Their exact inputs, cell data and PNG/PDF hashes are in
`docs/generated/figures/figure-data.json`. Old report figures are archived under
`docs/generated/historical-before-repair-20261001/`. Legacy per-run plots remain raw
historical artifacts in the browser and must not be presented as repaired evidence.
The earlier hand-transcribed/legacy report definitions are preserved in Git and the
verified pre-repair backup, rather than mixed with this protocol.

## Experimental protocol versus outcome

`protocol_status` is the separately reviewed attempt validity. `protocol_state` and
`protocol_verified_n3` describe same-cohort cell completeness. `attempt_completed`,
`observed_outcome`, `successful_run` and `observed_failure` describe execution and
export outcomes; `implementation_label` exposes the patched/historical distinction.
`protocol_blockers` remain separate from claim limitations. A/E/S/F in matrices
counts attempts/evaluated trajectories/clean final exports/observed failures. A
post-save native failure can support evaluated accuracy and must still count as a
failure. Sparse keyframes and low coverage do not alone invalidate protocol.
The old clean-qualified flag retains its old calculation for reproducibility only;
it does not drive current green ticks. No alignment, metric, parameter or score
changes were made for this reporting revision.
