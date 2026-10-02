# Reconciled evidence counts

Generated from hash-checked schema-3 evaluations and matching CSVs. These are inventory facts, not certification of scientific claims. Numerical `ok` is separate from execution, calibration, reference validity and publication qualification.

| Mode | Planned defaults | Evaluated | Numerical ok | Scale collapse | Invalid trajectory | Nonzero exits | Protocol-verified N=3 cells |
|---|---:|---:|---:|---:|---:|---:|---:|
| vo | 192 | 183 | 182 | 1 | 0 | 7 | 24 |
| vo-lc | 144 | 136 | 135 | 1 | 0 | 9 | 18 |
| vio | 168 | 145 | 142 | 3 | 0 | 7 | 18 |
| vio-lc | 96 | 86 | 86 | 0 | 0 | 2 | 12 |
| gnss-vio | 60 | 20 | 19 | 0 | 1 | 0 | 0 |

Legacy GNSS variants: 6 separate rows; not included in default repetition counts.

Scientific statuses among existing headline attempts: accepted=151, accepted_with_limitation=73, blocked=278, rerun_required=73, valid_observed_failure=10.

## Retained adverse outcomes

| Run | Numerical status | Exit | Scientific status |
|---|---|---:|---|
| `results/gnss-vio/hortimulti/strawberry02/vins_fusion_gps/run1` | eval_failed | unknown | blocked |
| `results/gnss-vio/rosariov2/sequence1/cifasis_gnss_si/run1` | ok | unknown | rerun_required |
| `results/vio/euroc_mav/MH_01_easy/openvins/run1` | ok | 134 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run1` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run2` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run3` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_03_medium/openvins/run1` | ok | 134 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run1` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run2` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run3` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run1` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run2` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run3` | ok | 0 | accepted_with_limitation |
| `results/vio/hortimulti/strawberry02/openvins/run1` | ok | 134 | blocked |
| `results/vio/hortimulti/strawberry02/voxel_svio/run1` | ok | 0 | blocked |
| `results/vio/hortimulti/strawberry02/voxel_svio/run2` | ok | 0 | blocked |
| `results/vio/hortimulti/strawberry02/voxel_svio/run3` | ok | 0 | blocked |
| `results/vio/hortimulti/strawberry03/openvins/run1` | ok | 134 | blocked |
| `results/vio/hortimulti/strawberry03/voxel_svio/run1` | ok | 0 | blocked |
| `results/vio/hortimulti/strawberry03/voxel_svio/run2` | ok | 0 | blocked |
| `results/vio/hortimulti/strawberry03/voxel_svio/run3` | ok | 0 | blocked |
| `results/vio/rosariov2/sequence1/openvins/run1` | scale_collapse | 134 | rerun_required |
| `results/vio/rosariov2/sequence1/voxel_svio/run1` | ok | 0 | rerun_required |
| `results/vio/rosariov2/sequence1/voxel_svio/run2` | ok | 0 | rerun_required |
| `results/vio/rosariov2/sequence1/voxel_svio/run3` | ok | 0 | rerun_required |
| `results/vio/rosariov2/sequence5/openvins/run1` | scale_collapse | 134 | rerun_required |
| `results/vio/rosariov2/sequence5/voxel_svio/run1` | ok | 0 | rerun_required |
| `results/vio/rosariov2/sequence5/voxel_svio/run2` | ok | 0 | rerun_required |
| `results/vio/rosariov2/sequence5/voxel_svio/run3` | ok | 0 | rerun_required |
| `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run1` | scale_collapse | 0 | valid_observed_failure |
| `results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | failed_without_trajectory | 134 | valid_observed_failure |
| `results/vio/zed2i/field1_110426_full_10fps_q90/voxel_svio/run1` | ok | 0 | blocked |
| `results/vio-lc/euroc_mav/MH_05_difficult/airslam/run4` | failed_without_trajectory | 139 | valid_observed_failure |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | failed_without_trajectory | 139 | valid_observed_failure |
| `results/vo/euroc_mav/MH_01_easy/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_01_easy/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_01_easy/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_03_medium/orbslam3/run2` | ok | 139 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_03_medium/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_03_medium/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_03_medium/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_05_difficult/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_05_difficult/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_05_difficult/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo/hortimulti/strawberry02/orbslam3/run1` | failed_without_trajectory | 139 | valid_observed_failure |
| `results/vo/hortimulti/strawberry02/ov2slam/run1` | ok | 0 | blocked |
| `results/vo/hortimulti/strawberry02/ov2slam/run2` | ok | 0 | blocked |
| `results/vo/hortimulti/strawberry02/ov2slam/run3` | ok | 0 | blocked |
| `results/vo/hortimulti/strawberry03/orbslam3/run2` | ok | 139 | blocked |
| `results/vo/hortimulti/strawberry03/ov2slam/run1` | ok | 0 | blocked |
| `results/vo/hortimulti/strawberry03/ov2slam/run2` | ok | 0 | blocked |
| `results/vo/hortimulti/strawberry03/ov2slam/run3` | ok | 0 | blocked |
| `results/vo/rosariov2/sequence1/orbslam3/run1` | failed_without_trajectory | 134 | valid_observed_failure |
| `results/vo/rosariov2/sequence1/ov2slam/run1` | ok | 0 | blocked |
| `results/vo/rosariov2/sequence1/ov2slam/run2` | ok | 0 | blocked |
| `results/vo/rosariov2/sequence1/ov2slam/run3` | ok | 0 | blocked |
| `results/vo/rosariov2/sequence5/orbslam3/run1` | failed_without_trajectory | 139 | valid_observed_failure |
| `results/vo/rosariov2/sequence5/ov2slam/run1` | ok | 0 | blocked |
| `results/vo/rosariov2/sequence5/ov2slam/run2` | ok | 0 | blocked |
| `results/vo/rosariov2/sequence5/ov2slam/run3` | ok | 0 | blocked |
| `results/vo/zed2i/field1_110426_full_10fps_q90/okvis2/run2` | scale_collapse | 0 | valid_observed_failure |
| `results/vo/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | ok | 139 | rerun_required |
| `results/vo/zed2i/field1_110426_full_10fps_q90/orbslam3/run2` | ok | 139 | rerun_required |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run1` | ok | 0 | blocked |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run2` | ok | 0 | blocked |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run3` | ok | 0 | blocked |
| `results/vo-lc/euroc_mav/MH_01_easy/orbslam3/run3` | ok | 139 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_03_medium/orbslam3/run3` | ok | 139 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_05_difficult/orbslam3/run1` | ok | 134 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/hortimulti/strawberry02/orbslam3/run1` | ok | 134 | blocked |
| `results/vo-lc/hortimulti/strawberry02/orbslam3/run2` | ok | 139 | blocked |
| `results/vo-lc/hortimulti/strawberry02/ov2slam/run1` | ok | 0 | blocked |
| `results/vo-lc/hortimulti/strawberry02/ov2slam/run2` | ok | 0 | blocked |
| `results/vo-lc/hortimulti/strawberry02/ov2slam/run3` | ok | 0 | blocked |
| `results/vo-lc/hortimulti/strawberry03/orbslam3/run1` | ok | 139 | blocked |
| `results/vo-lc/hortimulti/strawberry03/ov2slam/run1` | ok | 0 | blocked |
| `results/vo-lc/hortimulti/strawberry03/ov2slam/run2` | ok | 0 | blocked |
| `results/vo-lc/hortimulti/strawberry03/ov2slam/run3` | ok | 0 | blocked |
| `results/vo-lc/rosariov2/sequence1/orbslam3/run1` | failed_without_trajectory | 134 | valid_observed_failure |
| `results/vo-lc/rosariov2/sequence1/ov2slam/run1` | ok | 0 | blocked |
| `results/vo-lc/rosariov2/sequence1/ov2slam/run2` | scale_collapse | 0 | valid_observed_failure |
| `results/vo-lc/rosariov2/sequence1/ov2slam/run3` | ok | 0 | blocked |
| `results/vo-lc/rosariov2/sequence5/ov2slam/run1` | ok | 0 | blocked |
| `results/vo-lc/rosariov2/sequence5/ov2slam/run2` | ok | 0 | blocked |
| `results/vo-lc/rosariov2/sequence5/ov2slam/run3` | ok | 0 | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run2` | incomplete | unknown | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x/run1` | failed_without_trajectory | 141 | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | ok | 139 | rerun_required |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run1` | ok | 0 | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run2` | ok | 0 | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run3` | ok | 0 | blocked |

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
| `inventory.json` | `1938ae45ec8c86f303fdeafd9d9ff077501eddd302ebbe6ab2c9a60ad87d99e3` |
| `benchmark-vo.csv` | `cf4f7f65e4971fb59a5845e2fce4c0632ffaf31b8c5484982542be4ecbbdf22c` |
| `benchmark-vo-lc.csv` | `a6d66622e420682ad7620ff43bd731875cf5ee0730bda0a2d3e6dd88da5a4e50` |
| `benchmark-vio.csv` | `691163d32444c76e92dc3f14e8d87977e22b506caa3f2db5e8040765dae1dd7d` |
| `benchmark-vio-lc.csv` | `9037550fce7983d12e00fc145bee855df44063bb7fb3c351de77b1d60b9fb32d` |
| `benchmark-gnss-vio.csv` | `0228190305646ddf6844ec7abfd74951f6d2bc3b1846663f73df777a920b0ea3` |
