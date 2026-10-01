# Focused EuRoC OpenVINS / corrected AirSLAM campaign

The current authorized goal supersedes the previous no-estimator restriction only
for these EuRoC paths. No push is authorized. Preserve all historical attempts and
the 45 accepted N=3 cells at parent commit `0505d68`.

## Fixed scope and execution gates

- OpenVINS VIO: MH_01_easy, MH_03_medium, MH_05_difficult, logical repetitions 2
  and 3 (six missing repetitions). Retain each original run1, including its
  shutdown failure and qualification limits; do not silently count it as clean.
- AirSLAM VIO and VIO-LC: the same three sequences, three corrected repetitions
  each (18 total), physical run4/run5/run6 mapped to logical repetitions 1/2/3.
  Original run1/run2/run3 remain the affected upstream-calibration cohort.
- Integration uses the fixed first 40 seconds of MH01, with a separately named
  diagnostic sequence. Diagnostics never count toward production N=3.
- Check short VIO and refinement execution, output capture and shutdown first.
  Evaluate and inspect the first full repetition of each path before continuing.
- Every new physical attempt is used once. Evaluate available output immediately,
  including after failures. Preserve failures; do not retry to obtain successes.
- Sensor values and accuracy-related thresholds are frozen. Disclose the AirSLAM
  implementation correction and retained sparse-keyframe accuracy limitation.

## Preservation and evidence

`results/euroc-focused-20261001/baseline.json` records the starting commit, accepted
cells and historical evidence identities. The previous complete independent backup
is `/data/imoroz/vslam-repair-backups/20261001T204310Z-reference-complete`.
New diagnostics, build logs and native-camera verification are kept in the focused
evidence directory. Root/source commits and executable identities will be frozen
before production execution. Do not reinterpret historical provenance hashes.

## Integration findings so far

The AirSLAM correction was applied to the previously clean source. It was built
in `/root/catkin_ws_rectified_20261001` inside `air_slam`; the prior workspace and
binaries remain intact. An executable verifier loading the corrected library
matches `T_body_raw * inverse(R_rectified_raw)` to within 1.55e-14, with unchanged
camera translation. Source bytes match the patched checkout.

The corrected EuRoC inertial runner directly supervises native odometry/refinement
exits and waits for map serialization to finish. The previous appearance-of-
trajectory gate could interrupt serialization. A short VIO diagnostic has completed
with clean native exit, preserved provenance and immediate evaluation. The short
VIO-LC diagnostic also completed refinement and final-map serialization cleanly.
Full-sequence validation remains pending.

The repaired OpenVINS player no longer aborts at shutdown, but the native ROS2
estimator initially still segfaulted after SIGINT. ROS launch concealed this behind exit zero;
direct native supervision records exit -11 / wrapper 139. The saved diagnostic
trajectory is evaluated. The backtrace identifies publisher destruction during
global teardown after DDS resources have become invalid. The corrected image
`openvins:humble-shutdown-20261001` preserves the original image/dependencies and
rebuilds only the shutdown lifetime changes: drain background work and release
visualizer/state before static destruction. Its short diagnostic records native
exit zero, successful player shutdown, export and immediate evaluation. Active
filter parameters and update behavior are unchanged. Full-sequence gating remains.

The bounded OpenVINS interruption diagnostic also terminated its unique container;
evaluation-only recovery preserved the consumed attempt and did not restart it.
It had no saved trajectory and remains an interrupted diagnostic. Preparation
checks pass: 163 tests and three subtests. Local algorithm correction commits are
AirSLAM `1e0ad79` and OpenVINS `7a496c5`; their original revisions remain in history.

The 24 physical production IDs are frozen in
`configs/campaigns/euroc-focused-20261001.json`; the corrected AirSLAM comparison
selection is frozen before production in `euroc-focused-attempts-20261001.json`.
Current comparison CSVs and plots use that declared cohort, independent of outcome.
The affected original AirSLAM rows remain in `benchmark-historical-cohorts.csv`,
their original directories, the browser, and separate historical cohort reports.
The original 45 accepted cells are outside this selection change.

Diagnostic failures remain visible: the first subset revision used host-absolute
image links that were inaccessible in Docker; revision 2 uses portable relative
links to the same image bytes. AirSLAM's first native diagnostic exposed root-owned
process-state permissions; the supervisor now writes readable public process
evidence, and a new diagnostic attempt validated the repair. These are integration
attempts, not production failures or algorithm accuracy comparisons.
