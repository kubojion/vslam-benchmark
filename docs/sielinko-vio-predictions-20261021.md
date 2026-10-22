# Sielinko VIO noise predictions (written 2026-10-21, before any run)

Status: **DRAFT, awaiting user sign-off.** Once committed, this file is not edited; later notes go below the
results line.

## What will run
- **Rule C (primary):** Sielinko `field1_110426_full_10fps_q90`, VIO, N=1, one run for each CPU estimator: ORB-SLAM3,
  OKVIS2, OKVIS2-X, Basalt, OpenVINS, Voxel-SVIO, SVO Pro. Each gets the engine-off static Allan reference
  (g 1.5e-4, a 1.1e-3, bg 2.1e-6, ba 3.5e-5) times its own EuRoC ratio
  (`configs/sensors/imu-noise-rule-20261021.json`).
- **Engine-on sensitivity:** the same 7 runs with `configs/sensitivity/zed2i-engine-on-20261021`. White densities
  come from the engine-on standstill recordings (g 3.2e-3, a 2.0e-2), random walks stay engine-off, and the same
  ratios apply. This is reported as a sensitivity and is never counted in a Rule C cell.
- **Comparisons that already exist** (not rerun):
  - each estimator's Sielinko VO result;
  - the earlier common field-envelope VIO runs (g 0.0195, a 0.18 for every estimator).

| Estimator | Sielinko VO ATE (m) | Envelope VIO ATE (m) | Rule C accel nd | Engine-on accel nd |
|---|---|---|---|---|
| ORB-SLAM3 | 0.222 | 0.295 | 1.1e-3 | 2.0e-2 |
| OKVIS2 | 3.73 | 0.466 | 1.1e-2 | 0.20 |
| OKVIS2-X | 1.79 | 0.424 | 1.1e-2 | 0.20 |
| Basalt | 0.490 | 0.482 | 8.8e-3 | 0.16 |
| OpenVINS | none (no VO mode) | none | 1.1e-3 | 2.0e-2 |
| Voxel-SVIO | none (no VO mode) | 1.02 | 1.1e-3 | 2.0e-2 |
| SVO Pro | 3.93 | 0.67 | 4.4e-3 | 8.0e-2 |

## Definitions
- **ATE:** the benchmark's SE(3) ATE RMSE, as reported in `run_eval.json`.
- **Collapse:** either the benchmark's own validation fails the run, or the ATE is at least 3x that estimator's
  envelope VIO ATE. For OpenVINS, which has no envelope run, the threshold is 3x the median envelope ATE of the
  other six (3 x 0.47 = 1.4 m).

## Predictions
1. **Rule C collapses on Sielinko as it did on CitrusFarm.** At least 4 of the 7 estimators collapse under Rule C.
   - Expected to collapse: OKVIS2, OKVIS2-X, OpenVINS, Voxel-SVIO, SVO Pro.
   - Expected to survive: ORB-SLAM3 and Basalt, which also survived Rule C on CitrusFarm.
2. **Operating-condition noise prevents the collapse.** Under the engine-on profile, at most 2 of the 7 collapse.
   Every estimator that collapses under Rule C has a lower ATE under the engine-on profile.
3. **Engine-on comes close to the envelope.** For the estimators with an envelope run, the median ratio of
   engine-on ATE to envelope ATE is at most 2.

## How the result is read
- If 1 and 2 hold, the paper reports that a correct static calibration is the wrong input on this platform, and
  that noise measured with the engine running, without ground truth, avoids the failure.
- Any prediction that fails is reported as failed. Values, thresholds and definitions are not changed after the
  runs.

---
Results (filled in after the runs):
