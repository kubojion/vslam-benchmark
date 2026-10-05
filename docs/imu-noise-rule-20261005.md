# IMU noise rule: the authors' operating point (5 October 2026)

Decided by the user on 5 October 2026, recorded by Claude. Supersedes the IMU-noise row of
`docs/hortimulti-decisions-20261005.md` (one shared, recording-derived envelope), which stays
unchanged because reviews pin it. Machine-readable rule: `configs/sensors/imu-noise-rule.json`;
helper: `scripts/run/_imu_noise_rule.py`; tests: `scripts/campaign/tests/test_imu_noise_rule_20261005.py`.

## Rule

Each estimator receives the dataset's published Allan-variance IMU noise (white-noise densities and
bias random walks), each quantity multiplied by the factor its authors applied to the EuRoC Kalibr
calibration in their released EuRoC configuration:

    value(estimator, dataset, q) = Allan(dataset, q) x  authors_EuRoC(estimator, q) / Kalibr_EuRoC(q)

Sensor quantities come from the dataset and are the same for every estimator (camera model,
camera–IMU transform, time offset, Allan noise). How much an estimator inflates the IMU noise is an
algorithm choice and comes from its authors' released configuration. Nothing is tuned on benchmark
data. On EuRoC the rule reproduces the authors' released values, which the EuRoC configurations of
this benchmark already use.

| Estimator | Authors' EuRoC factor: gyro / accel density, gyro / accel random walk | Source |
|---|---|---|
| ORB-SLAM3, OpenVINS, Voxel-SVIO, AirSLAM, cuVSLAM | 1 / 1, 1 / 1 (Kalibr values) | each project's EuRoC configuration |
| MASt3R-Fusion | 6.06 / 0.98, 0.019 / 0.016 | `config/base_euroc.yaml` |
| SVO Pro | 7.07 / 4, 1547 / 33.3 | `svo_ros/param/calib/euroc_stereo.yaml` |
| Basalt | 1.66 / 8, 5.16 / 0.33 | `data/euroc_ds_calib.json` |
| OKVIS2, OKVIS2-X | 11.8 / 10, 10.3 / 6.67 | `config/euroc.yaml`, `config/euroc/okvis2.yaml` |

HortiMulti (MicroStrain 3DM-GX5-25, published Allan values: gyro 6.0369579e-4 rad/s/√Hz,
accel 1.093618e-3 m/s²/√Hz, gyro random walk 3.22094e-5, accel random walk 4.584471e-5) is the
first dataset under the rule (`datasets` in the rule file). Every HortiMulti inertial configuration
and the sensor profile (cuVSLAM) carry the rule's values; the SVO Pro and MASt3R-Fusion stages apply
it for the listed datasets only, so their behaviour on other datasets is unchanged.

## Why

- Published VIO benchmarks keep each algorithm at its own settings rather than imposing one noise
  value: Delmerico & Scaramuzza (ICRA 2018) used the parameters recommended by each algorithm's
  authors, fixed across all trials; Cremona et al. (JFR 2022, agriculture) tuned each system's
  parameters, including the IMU noise; Schmidt et al. (JFR 2025, outdoor) tuned each system's
  front end. The rule keeps the authors' choices without tuning on benchmark data.
- Authors' inflation of the same EuRoC calibration ranges from 1x (ORB-SLAM3, OpenVINS, Voxel-SVIO,
  AirSLAM, cuVSLAM) to about 10x (OKVIS2) and 50x (VINS-Fusion). OpenVINS' documentation suggests
  inflating by 10-20x and Kalibr's by 10x or more for low-cost sensors, yet the released EuRoC
  configurations are what each estimator was demonstrated with; the rule follows the released files.
- A shared envelope (gyro 6x, accel 100x the HortiMulti Allan values) degraded the estimators designed
  for calibrated noise in the 2026-10-05 readiness checks on strawberry03 (same evaluator, one run each):
  cuVSLAM VIO 0.74 -> 0.90 m, VIO-LC 0.71 -> 0.76 m and MASt3R-Fusion VIO 8.4 -> 18.4 m,
  VIO-LC 2.6 -> 18.3 m (only the noise differed); AirSLAM VIO 1.28 -> 3.62 m; Voxel-SVIO 0.72 -> 0.92 m;
  OKVIS2, OKVIS2-X, Basalt, SVO Pro level. These runs are kept as a noise-sensitivity observation.

Limitation to state: the rule assumes an estimator's inflation factor is a property of the estimator
rather than of EuRoC's sensor.

## Consequences

| Dataset | Status | Runs |
|---|---|---|
| EuRoC | Already the authors' values | none |
| HortiMulti | Rule applied (this commit) | every VIO/VIO-LC cell, in the HortiMulti batch |
| ZED2i, CitrusFarm | Envelope for every estimator; marked for rerun under the rule (`user-rerun-decisions-20261005b.json`), not queued | ZED VIO/VIO-LC, CitrusFarm VIO/VIO-LC, later |
| Rosario v2 | Mixed; parked with the other Rosario items | decided later |

ZED2i has no published Allan analysis (factory specification only) and CitrusFarm's published values
made three estimators diverge on 2026-10-04; how the rule's dataset values are taken there is decided
before those reruns.
