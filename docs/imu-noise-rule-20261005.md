# IMU noise rule: the authors' operating point (5 October 2026)

Decided by the user on 5 October 2026, recorded by Claude; applied per dataset by the two-regime
decision of the same day (section "Two regimes"). Supersedes the IMU-noise row of
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

## Two regimes

Decided by the user on 5 October 2026 (about 22:50), recorded by Claude. The rule needs a published
Allan-variance calibration that describes the dataset's IMU as recorded. Where no such calibration
exists, or where it is not usable, every estimator on that dataset keeps one shared noise profile: the
recording envelope of `docs/okvis-imu-noise-derivation.md`. The envelope is the 95th percentile of the
one-second robust noise density over the whole recording, with the published random walks; it reads
no ground truth. The regime is chosen per dataset, never per estimator, and within a dataset every
estimator receives the same sensor values.

| Dataset | Regime | Basis |
|---|---|---|
| EuRoC | Rule (equals the authors' released values) | Kalibr calibration of the ADIS16448 published with the dataset |
| HortiMulti | Rule (commit 7b8437e) | Published Allan analysis of the MicroStrain 3DM-GX5-25 |
| ZED2i | Envelope: gyro 0.0195, accel 0.18, gyro random walk 7.400196e-4, accel random walk 2.02e-2 | No Allan analysis of the unit exists, only the manufacturer's factory figures |
| CitrusFarm | Envelope: gyro 0.003, accel 0.05, published random walks 3.563656e-6 and 6.706088e-6 | The published densities sit at the stationary noise floor; with them the estimators that use calibrated values diverge (controlled pilot below) |
| Rosario v2 | Decided later, by the same criterion, with the other parked Rosario items | |

Criterion, as it should be stated in the paper: a dataset is under the rule when it publishes an Allan
calibration of the IMU used in the recording, and the estimators that consume that calibration unchanged
(factor 1: ORB-SLAM3, OpenVINS, Voxel-SVIO, AirSLAM) do not diverge with it on the dataset. Otherwise
the dataset uses its recording envelope for every estimator. Trajectory evidence enters only as a
binary divergence test. No noise value was chosen by accuracy.

### Evidence

**ZED2i** (one sequence, 77 min). Until 26 August 2026 the configurations used the factory figures:
gyro 4.992e-3 and accel 4.4e-4, with the gyro random walk in degree-based units, later corrected
(commit 388767c, `benchmark-vio.csv` at that commit). With them:
- OKVIS2, OKVIS2-X and OpenVINS collapsed in scale (ATE 1.6e6, 4.9e5 and 6.4e5 m);
- Basalt reached 9.98 m and Voxel-SVIO 3.73 m;
- AirSLAM reached 3.97 m while tracking 6 % of the sequence.

Commit 6c06c70 switched to the envelope together with the authors' quality configurations, so this
comparison is not noise-only. The runs saved since then:

| ZED2i VIO estimator | ATE SE(3) | Runs |
|---|---|---|
| ORB-SLAM3 | 0.29–0.30 m | 3 |
| OKVIS2-X | 0.37–0.48 m | 4 |
| OKVIS2 | 0.42–0.53 m | 4 |
| Basalt | 0.43–0.49 m | 4 |
| SVO Pro | 0.67 m | 1 |
| Voxel-SVIO | 0.67–1.14 m | 4 |
| AirSLAM | 3.3–3.8 m | 4 |
| cuVSLAM | 3.80 m | 1 |
| MASt3R-Fusion | 18.3 m | 1 |

ZED2i has no dataset Allan values, so the rule has no input there. Applying the rule to the factory
figures would return the factor-1 estimators to the July values.

**CitrusFarm** seq04, a controlled pilot on 4 October 2026: run 90001 at commit d5c366e against run
90002 at commit 46e15bc. Between the two commits the CitrusFarm configurations differ only in the two
noise densities. The published densities are gyro 1.0427e-4 and accel 2.2768e-4; the envelope is
gyro 0.003 and accel 0.05.

| Estimator | Published densities | Envelope |
|---|---|---|
| OpenVINS | 22 853 m, scale 1.3e-4 (collapse) | 6.72 m |
| Voxel-SVIO | 70 432 m, scale 4.0e-5 (collapse) | 1.45 m |
| AirSLAM | 539 m, scale 3.6e-3 (collapse) | 7.10 m |
| ORB-SLAM3 | 1.23 m | 0.68 m |

The published densities equal the stationary noise floor measured from the first seconds of the
recordings (`docs/campaigns/citrusfarm-imu-noise-20261003.json`): gyro 5.7e-5 to 6.6e-5 and accel
1.9e-4 to 3.8e-4. In motion, the 95th percentile is gyro 1.0e-3 to 2.5e-3 and accel 0.024 to 0.044,
10 to 200 times larger. HortiMulti's published values, for the same MicroStrain family, are 5 to 6
times CitrusFarm's.

**HortiMulti** strawberry03, envelope against the rule. One run each, same evaluator, ATE SE(3) in
metres, from the 2026-10-05 checks `results/window-20261005/checks` and `checks-c`:

| VIO estimator | Envelope | Rule |
|---|---|---|
| ORB-SLAM3 | 0.845 | 0.812 |
| AirSLAM | 3.616 | 1.057 |
| OKVIS2 | 0.691 | 0.742 |
| OKVIS2-X | 0.678 | 0.711 |
| Basalt | 0.674 | 0.662 |
| Voxel-SVIO | 0.933 | 0.659 |
| OpenVINS | 0.610 | 0.514 |
| cuVSLAM | 0.896 | 0.739 |
| SVO Pro | 0.689 | 0.643 |
| MASt3R-Fusion | 18.43 | 72.6 (scale collapse) |

VIO-LC, envelope then rule:
- ORB-SLAM3: 0.809, then 0.652.
- OKVIS2: 0.645, then 0.642.
- OKVIS2-X: 0.658, then 1.357.
- cuVSLAM: 0.762, then 0.706.
- SVO Pro: 0.613, then 0.625.
- MASt3R-Fusion: 18.33, then 73.5 (scale collapse).
- AirSLAM: under the rule its map refinement aborted with heap corruption while loading the map. This
  is the first occurrence in 41 AirSLAM loop-closure logs; it is retried.

MASt3R-Fusion's authors' EuRoC bias random walks are about 55 to 60 times below EuRoC's Kalibr values
(factors 0.016 and 0.019), and the rule carries that ratio to HortiMulti. Its collapse is reported as
the outcome under the rule. Keeping the rule for it is the recommendation, pending the user's
confirmation.

### Limitations to state

- The two regimes give different kinds of values. Rule datasets use calibration-based values with each
  estimator's own inflation; envelope datasets use one recording-derived value. Compare estimators
  within a dataset, and qualify any cross-dataset VIO statement by regime.
- Under the envelope, the estimators designed for calibrated noise (cuVSLAM, MASt3R-Fusion, AirSLAM,
  Voxel-SVIO) run away from their authors' operating point. The HortiMulti runs above, envelope
  against rule, quantify that sensitivity and are kept as a noise-sensitivity observation.
- The regime split was decided after the CitrusFarm pilot, with the ZED2i history known. This record
  gives that evidence.

## Consequences

| Dataset | Status | Runs |
|---|---|---|
| EuRoC | Already the authors' values | none |
| HortiMulti | Rule applied (commit 7b8437e) | every VIO/VIO-LC cell, in the HortiMulti batch. The superseded attempts, including the three envelope runs of the stopped batch, are pinned in `user-rerun-decisions-20261005b.json` |
| ZED2i, CitrusFarm | Envelope kept for every estimator (two regimes) | no rerun for the noise. Remaining repetitions as before; ZED2i VIO/VIO-LC not queued yet (user) |
| Rosario v2 | Parked with the other Rosario items | decided later |

The first version of this table (commit 7b8437e) marked ZED2i and CitrusFarm for a rerun under the rule
(commits 38cd91a and 90ac5d8). The two-regime decision withdraws those marks and readiness blockers. A
simulation of the inventory and future plans confirmed that the ZED2i and CitrusFarm findings, actions
and readiness then equal their state before the rule, and that the other datasets are unchanged.
