# IMU-noise policy (current, 2026-10-09)

This page summarises the policy in force. It does not replace the frozen decision records:
- [imu-noise-rule-20261005](imu-noise-rule-20261005.md): rule and factors.
- [benchmark-decisions-20261006 §1](benchmark-decisions-20261006.md): scope, which supersedes the "Two regimes" section of the rule document.

The policy only affects inertial modes: VIO, VIO-LC and GNSS-VIO.

## Rule C ("authors' operating point")

For each estimator and each of the four noise quantities (gyro and accel noise density, gyro and accel bias random walk):

```
value = dataset published calibration × (authors' released EuRoC value / EuRoC Kalibr value)
```

No value is tuned on benchmark data. On EuRoC the rule reproduces each author's released configuration exactly.

Factors (gyro density / accel density / gyro random walk / accel random walk), from `configs/sensors/imu-noise-rule.json`:

| estimator | factors |
|---|---|
| ORB-SLAM3, OpenVINS, Voxel-SVIO, AirSLAM, cuVSLAM | 1 / 1 / 1 / 1 |
| OKVIS2, OKVIS2-X | 11.8 / 10 / 10.3 / 6.67 |
| Basalt | 1.66 / 8 / 5.16 / 0.333 |
| SVO Pro | 7.07 / 4 / 1547 / 33.3 |
| MASt3R-Fusion | 6.06 / 0.981 / 0.0187 / 0.0163 |

## Where it applies

| dataset | base calibration | policy |
|---|---|---|
| EuRoC | Kalibr `sensor.yaml` | authors' released values (= Rule C) |
| HortiMulti | published Allan, MicroStrain 3DM-GX5-25 (g 6.037e-4, a 1.094e-3, RW 3.22e-5 / 4.58e-5) | Rule C |
| Rosario v2 | authors' Kalibr `imu.yaml` (g 2.325e-4, a 9.944e-4, RW 1.824e-6 / 4.751e-5) | Rule C |
| CitrusFarm | authors' MicroStrain GX5 file (g 1.043e-4, a 2.277e-4, RW 3.564e-6 / 6.706e-6) | Rule C |
| ZED2i | none published (factory figures only) | recording envelope (g 0.0195, a 0.18, RW 7.4e-4 / 2.02e-2); reported as a separate case |

The CitrusFarm and Rosario values are in `configs/sensors/imu-noise-rule-20261006.json`.

## Known limitation

The rule assumes each dataset's published calibration was measured in a comparable way. That assumption is visibly violated:
- **Same IMU family, different published values.** CitrusFarm and HortiMulti use the same IMU family, yet CitrusFarm's published densities are 4.8–5.8× smaller and its random walks 6.8–9× smaller. CitrusFarm's values sit at the stationary floor.
- **Consequence.** Under Rule C, CitrusFarm estimators trust the IMU about 23–34× more than on HortiMulti.
- **Outcome.** On CitrusFarm, 7 of 18 Rule C VIO first repetitions collapsed, against 1 of 18 under the envelope.
- **HortiMulti.** On strawberry03, Rule C was equal or better for 9 of 10 estimators; MASt3R-Fusion collapsed.

Evidence is in `/data/imoroz/IMU-NOISE-ISSUE2/comparison-20261008/` and `findings-2026-10-08.txt`.

## Sensitivity conditions (never mixed into Rule C repetitions)

- **Envelope results** on HortiMulti and CitrusFarm are kept as a labelled sensitivity / adaptation condition (benchmark-decisions §1). They never fill a Rule C repetition and are never chosen per cell by outcome.
- **IMU-noise search pilot.** It runs on branch `experiment/imu-noise-search-20261009` and is exploratory. Its development clips are prefixes of the scored sequences, so its outcomes are not test results. Any tuned condition used in the paper needs:
  - held-out tuning data, e.g. leave-one-sequence-out;
  - the same budget for every inertial estimator;
  - a frozen selection rule.
