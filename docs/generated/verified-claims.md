# Reconciled evidence counts

Generated from hash-checked schema-3 evaluations and matching CSVs. These are inventory facts, not certification of scientific claims. Numerical `ok` is separate from execution, calibration, reference validity and publication qualification.

| Mode | Planned defaults | Evaluated | Numerical ok | Scale collapse | Invalid trajectory | Nonzero exits | Qualified clean N=3 cells |
|---|---:|---:|---:|---:|---:|---:|---:|
| vo | 192 | 183 | 182 | 1 | 0 | 7 | 0 |
| vo-lc | 144 | 136 | 135 | 1 | 0 | 9 | 0 |
| vio | 168 | 139 | 136 | 3 | 0 | 7 | 0 |
| vio-lc | 96 | 87 | 87 | 0 | 0 | 1 | 0 |
| gnss-vio | 60 | 20 | 19 | 0 | 1 | 0 | 0 |

Legacy GNSS variants: 6 separate rows; not included in default repetition counts.

Scientific statuses among existing headline attempts: blocked=549, rerun_required=30.

## Retained adverse outcomes

| Run | Numerical status | Exit | Scientific status |
|---|---|---:|---|
| `results/gnss-vio/hortimulti/strawberry02/vins_fusion_gps/run1` | eval_failed | unknown | blocked |
| `results/vio/euroc_mav/MH_01_easy/openvins/run1` | ok | 134 | blocked |
| `results/vio/euroc_mav/MH_03_medium/openvins/run1` | ok | 134 | blocked |
| `results/vio/hortimulti/strawberry02/openvins/run1` | ok | 134 | blocked |
| `results/vio/hortimulti/strawberry03/openvins/run1` | ok | 134 | blocked |
| `results/vio/rosariov2/sequence1/openvins/run1` | scale_collapse | 134 | blocked |
| `results/vio/rosariov2/sequence5/openvins/run1` | scale_collapse | 134 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run1` | scale_collapse | 0 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | failed_without_trajectory | 134 | blocked |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | failed_without_trajectory | 139 | blocked |
| `results/vo/euroc_mav/MH_03_medium/orbslam3/run2` | ok | 139 | blocked |
| `results/vo/hortimulti/strawberry02/orbslam3/run1` | failed_without_trajectory | 139 | blocked |
| `results/vo/hortimulti/strawberry03/orbslam3/run2` | ok | 139 | blocked |
| `results/vo/rosariov2/sequence1/orbslam3/run1` | failed_without_trajectory | 134 | blocked |
| `results/vo/rosariov2/sequence5/orbslam3/run1` | failed_without_trajectory | 139 | blocked |
| `results/vo/zed2i/field1_110426_full_10fps_q90/okvis2/run2` | scale_collapse | 0 | blocked |
| `results/vo/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | ok | 139 | rerun_required |
| `results/vo/zed2i/field1_110426_full_10fps_q90/orbslam3/run2` | ok | 139 | rerun_required |
| `results/vo-lc/euroc_mav/MH_01_easy/orbslam3/run3` | ok | 139 | blocked |
| `results/vo-lc/euroc_mav/MH_03_medium/orbslam3/run3` | ok | 139 | blocked |
| `results/vo-lc/euroc_mav/MH_05_difficult/orbslam3/run1` | ok | 134 | blocked |
| `results/vo-lc/hortimulti/strawberry02/orbslam3/run1` | ok | 134 | blocked |
| `results/vo-lc/hortimulti/strawberry02/orbslam3/run2` | ok | 139 | blocked |
| `results/vo-lc/hortimulti/strawberry03/orbslam3/run1` | ok | 139 | blocked |
| `results/vo-lc/rosariov2/sequence1/orbslam3/run1` | failed_without_trajectory | 134 | blocked |
| `results/vo-lc/rosariov2/sequence1/ov2slam/run2` | scale_collapse | 0 | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run2` | incomplete | unknown | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x/run1` | failed_without_trajectory | 141 | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | ok | 139 | rerun_required |

## Claim boundaries

- Primary ATE is SE(3) for metric stereo/inertial methods and Sim(3) for monocular DPVO. No cross-scale winner is inferred.
- Conditional accuracy in the tables excludes numerical failures from the score calculation only; all failures and missing repetitions remain in the denominator. Distinct cohorts and GNSS variants are separate.
- AirSLAM keyframe density does not measure tracking loss or processed-image throughput. Exported-pose coverage and reference-supported score coverage have separate fields.
- Nominal input divided by elapsed time is not measured estimator processing speed or real-time latency.
- Mode comparisons alone do not establish that excitation or a particular loop mechanism caused an error. Reference, config and final-optimization differences must be resolved before drawing those conclusions.
- Aligned GNSS shape error is not absolute global positioning accuracy. Historical input/reference independence remains unqualified.

## Source identities

| Source | SHA-256 |
|---|---|
| `inventory.json` | `bf29a252333853b0563be7ffc315e195140eba7347692a2c23a8dc24e50f4317` |
| `benchmark-vo.csv` | `00bcfb4a4874ee335774a48250cd4d3dc0f814100906359a240b1295722cfbc7` |
| `benchmark-vo-lc.csv` | `8189ee0b28d53869cb1349c3f74764236ec0bebe67b6980d96f135e9cf9dd2e6` |
| `benchmark-vio.csv` | `f05079137c9537454fab2a10b5b275b0e2589ab58e03ef734687f6880bf3b9df` |
| `benchmark-vio-lc.csv` | `8414dac0064feb425dcbd7a7b8f84a58fedd0e364305a1da46c9d53422f16b83` |
| `benchmark-gnss-vio.csv` | `97224381ae15f94661a59370126d5ed50e02040565f66c78b370f1fa172dbf13` |
