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


## Evaluation recorded 25 October 2026

The approved text above is byte-for-byte unchanged (SHA-256 `d1cd0561840c6cfd3d94fde31be97c81a822e653decef138b02a2d3322c4e4ff`). Its retained DRAFT label is historical: approval is recorded in `coordinated/revision12-20261021/predictions-user-approval.json`.

This evaluates logical Rule C **r1 only**, plus engine-on **N=1**, for the seven CPU estimators specified above. It does not use N=3 medians, search-selected runs or the later GPU sensitivities. Explicit infrastructure replacements 361/363 supply Voxel-SVIO/SVO Pro r1; superseded attempts 282/283 receive no primary credit.

| Estimator | Rule C r1 SE(3) ATE (m) | Rule C collapse | Engine-on SE(3) ATE (m) | Engine-on collapse | Threshold (m) |
|---|---:|:---:|---:|:---:|---:|
| ORB-SLAM3 | 58462.5 † | Yes | 1157.4 † | Yes | 0.885 |
| OKVIS2 | 3.07738e+07 † | Yes | 0.681902 | No | 1.398 |
| OKVIS2-X | 2.1634e+06 † | Yes | 0.458155 | No | 1.272 |
| Basalt | 0.462546 | No | 0.421997 † | Yes | 1.446 |
| OpenVINS | 3.59756e+07 † | Yes | 1.00769 | No | 1.4 |
| Voxel-SVIO | 1.35908e+07 † | Yes | 342236 † | Yes | 3.06 |
| SVO Pro | 0.506894 | No | 0.452215 | No | 2.01 |

† Diagnostic ATE from a failed observation, not an accepted accuracy score. Collapse uses the original failure-or-threshold definition. Basalt engine-on is a failed observation despite evaluator status `ok`: native SIGSEGV occurred during trajectory saving; the exported trajectory ends 131 s early. Review 290 explicitly rejects it as a clean result. No failure is retried or relabelled here.

1. **Prediction 1: holds at the stated aggregate level (5/7 collapses; threshold at least 4).** The expected identities were not all right: ORB-SLAM3 collapses, while SVO Pro survives alongside Basalt.

2. **Prediction 2: fails (3/7 engine-on collapses; allowed at most 2).** ORB-SLAM3 and Voxel-SVIO retain scale collapse; Basalt has the reviewed native/export failure. The separate lower-ATE clause holds numerically for all five Rule C collapses, but ORB-SLAM3/Voxel-SVIO remain failed observations.

3. **Prediction 3: the literal numerical median-ratio test holds (1.271932253 <= 2).** Ratios use the six envelope values printed in the approved table and each engine-on `run_eval.json` SE(3) ATE. This includes diagnostic values for failed observations, as marked above; it does not establish six clean near-envelope results. Three engine-on observations in this six-estimator subset failed, including Basalt. No survivor-only median or substituted failure score is used.

**Interpretation:** the document's joint condition that predictions 1 and 2 hold is not met. These N=1 observations support substantial improvement for several estimators, including OpenVINS (1.007693209 m engine-on versus failed Rule C r1), but do not support the pre-written claim that operating-condition noise generally avoids failure on this platform.

**Provenance and limits:** exact runs, review/meta/evaluation hashes and computed values are in `sielinko-vio-predictions-results-20261025.json`. The OpenVINS no-envelope threshold remains the literal 1.4 m written above, rather than recomputing its rounded parenthetical arithmetic. Failed diagnostic ratios are not copied into successful-score tables. Preserve the benchmark's Sielinko reference/calibration qualifications and exported-coverage limitations. Concurrent runtimes are not isolated performance measurements.
