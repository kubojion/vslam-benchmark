# Reconciled evidence counts

Generated from hash-checked schema-3 evaluations and matching CSVs. These are inventory facts, not certification of scientific claims. Numerical `ok` is separate from execution, calibration, reference validity and publication qualification.

| Mode | Planned defaults | Evaluated | Numerical ok | Scale collapse | Invalid trajectory | Nonzero exits | Protocol-verified N=3 cells |
|---|---:|---:|---:|---:|---:|---:|---:|
| vo | 192 | 183 | 182 | 1 | 0 | 7 | 31 |
| vo-lc | 144 | 137 | 136 | 1 | 0 | 9 | 20 |
| vio | 168 | 145 | 142 | 3 | 0 | 7 | 18 |
| vio-lc | 96 | 86 | 86 | 0 | 0 | 2 | 12 |
| gnss-vio | 60 | 20 | 19 | 0 | 1 | 0 | 0 |

Legacy GNSS variants: 6 separate rows; not included in default repetition counts.

Scientific statuses among existing headline attempts: accepted=151, accepted_with_limitation=103, blocked=240, rerun_required=84, valid_observed_failure=7.

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
| `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run1` | scale_collapse | 0 | rerun_required |
| `results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | failed_without_trajectory | 134 | rerun_required |
| `results/vio/zed2i/field1_110426_full_10fps_q90/voxel_svio/run1` | ok | 0 | rerun_required |
| `results/vio-lc/euroc_mav/MH_05_difficult/airslam/run4` | failed_without_trajectory | 139 | valid_observed_failure |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | failed_without_trajectory | 139 | rerun_required |
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
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run3` | ok | 0 | accepted_with_limitation |
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
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x/run1` | ok | 141 | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | ok | 139 | rerun_required |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run3` | ok | 0 | accepted_with_limitation |

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
| `inventory.json` | `1ae640358005f25e140a9951569a6eae8480ea6b3c65e419158bac7a5da01d8e` |
| `benchmark-vo.csv` | `d8b993d602d796d18e6dac369349d6aac76f2f143aa85b410f3c4c3a959c9e90` |
| `benchmark-vo-lc.csv` | `f8b8fcab4d9ef8dd55868f563ef3c81ce372a460339efe7e740f94c6a2444f9c` |
| `benchmark-vio.csv` | `51fd2f26511ad98f43fc88b3814cec921fdbf58f8da2364dcc21ecc7aa0ab007` |
| `benchmark-vio-lc.csv` | `f5da4d13875316cacd3f2667158d3acf678f4fe8ad9748e7cecdff1b31e5e6a7` |
| `benchmark-gnss-vio.csv` | `da52154da12792ac68c70abc6e6b64ff6450a9d0c996b6b8fc79b46aee50f421` |
