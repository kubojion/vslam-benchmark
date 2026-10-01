# Acceptance handoff — 2026-10-01

Generated from the checked inventory. The [claim review](paper-acceptance-20261001.md) defines eligibility, limitations and evidence. This supersedes the earlier blanket hold; numerical values and historical attempt records are unchanged. **Acceptance review complete; native execution remains unverified.**

| Mode | Clean accepted N=3 cells | Accepted repetitions | Limited repetitions | Observed failures accepted | Required reruns | Missing | Blocked |
|---|---:|---:|---:|---:|---:|---:|---:|
| vo | 17 | 53 | 19 | 4 | 3 | 6 | 107 |
| vo-lc | 9 | 33 | 21 | 2 | 3 | 5 | 80 |
| vio | 11 | 35 | 13 | 4 | 9 | 28 | 79 |
| vio-lc | 8 | 26 | 1 | 1 | 15 | 8 | 45 |
| gnss-vio | 0 | 0 | 0 | 0 | 0 | 40 | 20 |

Future default actions: 212 reusable observations, 30 required reruns, 87 missing repetitions, 331 blocked. Retaining an observation does not certify a repaired runner. No new estimator run or push occurred.

## Clean N=3 cells

| Cell | Accepted claim |
|---|---|
| `vo/euroc_mav/MH_01_easy/orbslam3` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_01_easy/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_01_easy/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_01_easy/basalt` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_01_easy/dpvo` | recorded_profile_euroc_final_trajectory_sim3_monocular_shape |
| `vo/euroc_mav/MH_01_easy/macvo` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_03_medium/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_03_medium/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_03_medium/basalt` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_03_medium/dpvo` | recorded_profile_euroc_final_trajectory_sim3_monocular_shape |
| `vo/euroc_mav/MH_03_medium/macvo` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_05_difficult/orbslam3` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_05_difficult/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_05_difficult/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_05_difficult/basalt` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_05_difficult/dpvo` | recorded_profile_euroc_final_trajectory_sim3_monocular_shape |
| `vo/euroc_mav/MH_05_difficult/macvo` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_01_easy/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_01_easy/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_01_easy/dpvo` | recorded_profile_euroc_final_trajectory_sim3_monocular_shape |
| `vo-lc/euroc_mav/MH_03_medium/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_03_medium/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_03_medium/dpvo` | recorded_profile_euroc_final_trajectory_sim3_monocular_shape |
| `vo-lc/euroc_mav/MH_05_difficult/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_05_difficult/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_05_difficult/dpvo` | recorded_profile_euroc_final_trajectory_sim3_monocular_shape |
| `vio/euroc_mav/MH_01_easy/orbslam3` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_01_easy/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_01_easy/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_01_easy/basalt` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_03_medium/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_03_medium/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_03_medium/basalt` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_05_difficult/orbslam3` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_05_difficult/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_05_difficult/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_05_difficult/basalt` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_01_easy/orbslam3` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_01_easy/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_01_easy/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_03_medium/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_03_medium/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_05_difficult/orbslam3` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_05_difficult/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_05_difficult/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |

## Limited results and accepted failures

| Attempt | Acceptance | Specific limit |
|---|---|---|
| `results/vo/rosariov2/sequence1/orbslam3/run1` | valid_observed_failure | no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator |
| `results/vo/rosariov2/sequence5/orbslam3/run1` | valid_observed_failure | no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator |
| `results/vo/hortimulti/strawberry02/orbslam3/run1` | valid_observed_failure | no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator |
| `results/vo/euroc_mav/MH_01_easy/airslam/run1` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_01_easy/airslam/run2` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_01_easy/airslam/run3` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_01_easy/ov2slam/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_01_easy/ov2slam/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_01_easy/ov2slam/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_03_medium/orbslam3/run2` | accepted_with_limitation | saved_accuracy_with_recorded_nonzero_exit_no_clean_success |
| `results/vo/euroc_mav/MH_03_medium/airslam/run1` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_03_medium/airslam/run2` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_03_medium/airslam/run3` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_03_medium/ov2slam/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_03_medium/ov2slam/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_03_medium/ov2slam/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_05_difficult/airslam/run1` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_05_difficult/airslam/run2` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_05_difficult/airslam/run3` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_05_difficult/ov2slam/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_05_difficult/ov2slam/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_05_difficult/ov2slam/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/zed2i/field1_110426_full_10fps_q90/okvis2/run2` | valid_observed_failure | collapse_under_recorded_reference_diagnostic_not_verified_physical_scale; no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator |
| `results/vo-lc/rosariov2/sequence1/orbslam3/run1` | valid_observed_failure | no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator |
| `results/vo-lc/rosariov2/sequence1/ov2slam/run2` | valid_observed_failure | collapse_under_recorded_reference_diagnostic_not_verified_physical_scale; no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator |
| `results/vo-lc/euroc_mav/MH_01_easy/orbslam3/run3` | accepted_with_limitation | saved_accuracy_with_recorded_nonzero_exit_no_clean_success |
| `results/vo-lc/euroc_mav/MH_01_easy/airslam/run1` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_01_easy/airslam/run2` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_01_easy/airslam/run3` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_03_medium/orbslam3/run3` | accepted_with_limitation | saved_accuracy_with_recorded_nonzero_exit_no_clean_success |
| `results/vo-lc/euroc_mav/MH_03_medium/airslam/run1` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_03_medium/airslam/run2` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_03_medium/airslam/run3` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_05_difficult/orbslam3/run1` | accepted_with_limitation | saved_accuracy_with_recorded_nonzero_exit_no_clean_success |
| `results/vo-lc/euroc_mav/MH_05_difficult/airslam/run1` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_05_difficult/airslam/run2` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_05_difficult/airslam/run3` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/rosariov2/sequence1/openvins/run1` | valid_observed_failure | collapse_under_recorded_reference_diagnostic_not_verified_physical_scale; no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator |
| `results/vio/rosariov2/sequence5/openvins/run1` | valid_observed_failure | collapse_under_recorded_reference_diagnostic_not_verified_physical_scale; no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator |
| `results/vio/euroc_mav/MH_01_easy/openvins/run1` | accepted_with_limitation | saved_accuracy_with_recorded_nonzero_exit_no_clean_success |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run1` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick; native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run2` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick; native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run3` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick; native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_03_medium/orbslam3/run2` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick |
| `results/vio/euroc_mav/MH_03_medium/openvins/run1` | accepted_with_limitation | saved_accuracy_with_recorded_nonzero_exit_no_clean_success |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_05_difficult/openvins/run1` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | valid_observed_failure | no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator; serial_specific_imu_rotation_and_timing_unverified |
| `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run1` | valid_observed_failure | collapse_under_recorded_reference_diagnostic_not_verified_physical_scale; no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator; serial_specific_imu_rotation_and_timing_unverified |
| `results/vio-lc/euroc_mav/MH_03_medium/orbslam3/run1` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | valid_observed_failure | no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator; serial_specific_imu_rotation_and_timing_unverified |

## Exact required reruns

These are the existing 30 confirmed cases, not 30 newly discovered defects. Preserve every original attempt and use a new physical ID/cohort.

| Cell | Logical repetitions | Concrete defect |
|---|---|---|
| `vo/zed2i/field1_110426_full_10fps_q90/orbslam3` | r1, r2, r3 | camera_fps_changed_15_to_10 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | r1, r2, r3 | camera_fps_changed_15_to_10 |
| `vio/euroc_mav/MH_01_easy/airslam` | r1, r2, r3 | airslam_rectified_camera_imu_extrinsic |
| `vio/euroc_mav/MH_03_medium/airslam` | r1, r2, r3 | airslam_rectified_camera_imu_extrinsic |
| `vio/euroc_mav/MH_05_difficult/airslam` | r1, r2, r3 | airslam_rectified_camera_imu_extrinsic |
| `vio-lc/hortimulti/strawberry02/orbslam3` | r1, r2, r3 | orb_horti_rectified_camera_imu_extrinsic |
| `vio-lc/hortimulti/strawberry03/orbslam3` | r1, r2, r3 | orb_horti_rectified_camera_imu_extrinsic |
| `vio-lc/euroc_mav/MH_01_easy/airslam` | r1, r2, r3 | airslam_rectified_camera_imu_extrinsic |
| `vio-lc/euroc_mav/MH_03_medium/airslam` | r1, r2, r3 | airslam_rectified_camera_imu_extrinsic |
| `vio-lc/euroc_mav/MH_05_difficult/airslam` | r1, r2, r3 | airslam_rectified_camera_imu_extrinsic |

## Exact missing repetitions

Missing means no original attempt directory; an existing failed attempt is not reclassified as missing.

| Cell | Missing logical repetitions |
|---|---|
| `vo/rosariov2/sequence1/orbslam3` | r2, r3 |
| `vo/rosariov2/sequence5/orbslam3` | r2, r3 |
| `vo/hortimulti/strawberry02/orbslam3` | r2, r3 |
| `vo-lc/rosariov2/sequence1/orbslam3` | r2, r3 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2` | r3 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x` | r2, r3 |
| `vio/rosariov2/sequence1/openvins` | r2, r3 |
| `vio/rosariov2/sequence5/openvins` | r2, r3 |
| `vio/hortimulti/strawberry02/openvins` | r2, r3 |
| `vio/hortimulti/strawberry03/openvins` | r2, r3 |
| `vio/euroc_mav/MH_01_easy/openvins` | r2, r3 |
| `vio/euroc_mav/MH_03_medium/openvins` | r2, r3 |
| `vio/euroc_mav/MH_05_difficult/openvins` | r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/orbslam3` | r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/okvis2` | r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/okvis2x` | r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/airslam` | r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/basalt` | r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/openvins` | r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/voxel_svio` | r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2` | r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2x` | r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/airslam` | r2, r3 |
| `gnss-vio/rosariov2/sequence1/cifasis_gnss_si` | r2, r3 |
| `gnss-vio/rosariov2/sequence1/okvis2x` | r2, r3 |
| `gnss-vio/rosariov2/sequence1/openvins_gps` | r2, r3 |
| `gnss-vio/rosariov2/sequence1/rtabmap_gps` | r2, r3 |
| `gnss-vio/rosariov2/sequence1/vins_fusion_gps` | r2, r3 |
| `gnss-vio/rosariov2/sequence5/cifasis_gnss_si` | r2, r3 |
| `gnss-vio/rosariov2/sequence5/okvis2x` | r2, r3 |
| `gnss-vio/rosariov2/sequence5/openvins_gps` | r2, r3 |
| `gnss-vio/rosariov2/sequence5/rtabmap_gps` | r2, r3 |
| `gnss-vio/rosariov2/sequence5/vins_fusion_gps` | r2, r3 |
| `gnss-vio/hortimulti/strawberry02/cifasis_gnss_si` | r2, r3 |
| `gnss-vio/hortimulti/strawberry02/okvis2x` | r2, r3 |
| `gnss-vio/hortimulti/strawberry02/openvins_gps` | r2, r3 |
| `gnss-vio/hortimulti/strawberry02/rtabmap_gps` | r2, r3 |
| `gnss-vio/hortimulti/strawberry02/vins_fusion_gps` | r2, r3 |
| `gnss-vio/hortimulti/strawberry03/cifasis_gnss_si` | r2, r3 |
| `gnss-vio/hortimulti/strawberry03/okvis2x` | r2, r3 |
| `gnss-vio/hortimulti/strawberry03/openvins_gps` | r2, r3 |
| `gnss-vio/hortimulti/strawberry03/rtabmap_gps` | r2, r3 |
| `gnss-vio/hortimulti/strawberry03/vins_fusion_gps` | r2, r3 |

## Material blockers

Exact affected attempt IDs and evidence are in `results/acceptance-20261001/handoff.json` and the future manifest. Counts overlap across blockers.

| Evidence needed | Blocked attempts |
|---|---:|
| estimate_frame_unverified: expected one saved estimator_config, found 0 | 4 |
| estimate_frame_unverified: output frame not established for cifasis_gnss_si | 4 |
| estimate_frame_unverified: output frame not established for openvins_gps | 4 |
| estimate_frame_unverified: output frame not established for rtabmap_gps | 4 |
| estimate_frame_unverified: output frame not established for vins_fusion_gps | 4 |
| gnss_reference_independence_and_global_frame_not_established | 20 |
| historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified | 20 |
| historical_workspace_digest_differs_keep_cohorts_separate | 6 |
| horti_reference_to_camera_extrinsic_unverified | 147 |
| native_execution_cause_and_usable_export_missing | 2 |
| rosario_rectified_camera_axes_and_reference_chain_require_verification | 144 |
| rosario_rectified_camera_reference_chain_and_baseline_convention_unverified | 134 |
| zed_reference_camera_lever_arm_heading_altitude_unverified | 40 |
| zed_reference_orientation_unavailable | 38 |
| zed_serial_specific_imu_rotation_and_time_offset_unverified | 8 |

## Next execution, after authorization

First resolve static prerequisites: apply/build the reviewed AirSLAM rectification patch; verify the corrected ORB FPS/IMU profiles load; capture actual native exits separately from wrapper/player exits; diagnose OV2SLAM/Voxel shutdown and the remaining ORB/OKVIS ZED execution failures. Retain the existing final-optimization/profile choices; do not tune them on these test scores. Agricultural reference and GNSS evidence must be obtained before qualified production comparisons.

**Smallest useful first batch: three diagnostic targets** — OpenVINS EuRoC MH01 VIO, AirSLAM EuRoC MH01 VIO, and AirSLAM EuRoC MH01 VIO-LC. These cover the shutdown/capture path and both patched Air inertial stages needed for the immediately actionable EuRoC missing/rerun cases. Freeze a separately labelled bounded-input diagnostic recipe, preserve its input subset and all output, and exercise normal completion plus safe interruption/resume without overwriting. A truncated diagnostic cannot certify full-sequence stability, LC occurrence or runtime. After it passes, the first production repetition is the full-sequence gate and must be evaluated before continuing.

**Whole-scope readiness remains conditional:** the following 31 representative targets cover each of the 30 repaired algorithm/mode paths once, plus ORB ZED inertial+LC. This is the minimum branch-coverage target set used here, not proof that all dataset-specific paths behave identically. Defer blocked agricultural/GNSS targets until their prerequisites are resolved; do not launch this as a campaign. Passing the first three does not certify the other paths. Tests of failure/interruption can be combined with each integration target; no arbitrary extra N=3 diagnostic campaign is proposed.

| Diagnostic target | First batch | Full-sequence historical seconds (not diagnostic estimate) |
|---|---|---:|
| `vio/euroc_mav/MH_01_easy/airslam` | yes | unknown |
| `vio-lc/euroc_mav/MH_01_easy/airslam` | yes | unknown |
| `vo/euroc_mav/MH_01_easy/airslam` | deferred | unknown |
| `vo-lc/euroc_mav/MH_01_easy/airslam` | deferred | unknown |
| `vio/euroc_mav/MH_01_easy/basalt` | deferred | 9.6 |
| `vo/euroc_mav/MH_01_easy/basalt` | deferred | 10.6 |
| `gnss-vio/rosariov2/sequence1/cifasis_gnss_si` | deferred | unknown |
| `vo/euroc_mav/MH_01_easy/dpvo` | deferred | 86.2 |
| `vo-lc/euroc_mav/MH_01_easy/dpvo` | deferred | 95.0 |
| `vo/euroc_mav/MH_01_easy/macvo` | deferred | 721.6 |
| `vio/euroc_mav/MH_01_easy/okvis2` | deferred | 208.2 |
| `vio-lc/euroc_mav/MH_01_easy/okvis2` | deferred | 231.2 |
| `vo/euroc_mav/MH_01_easy/okvis2` | deferred | 229.8 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2` | deferred | 22199.5 |
| `gnss-vio/rosariov2/sequence1/okvis2x` | deferred | unknown |
| `vio/euroc_mav/MH_01_easy/okvis2x` | deferred | 203.5 |
| `vio-lc/euroc_mav/MH_01_easy/okvis2x` | deferred | 228.3 |
| `vo/euroc_mav/MH_01_easy/okvis2x` | deferred | 220.2 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x` | deferred | unknown |
| `vio/euroc_mav/MH_01_easy/openvins` | yes | unknown |
| `gnss-vio/rosariov2/sequence1/openvins_gps` | deferred | unknown |
| `vio/zed2i/field1_110426_full_10fps_q90/orbslam3` | deferred | unknown |
| `vio-lc/hortimulti/strawberry02/orbslam3` | deferred | 1012.8 |
| `vo/zed2i/field1_110426_full_10fps_q90/orbslam3` | deferred | 5666.9 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | deferred | 5731.7 |
| `vo/euroc_mav/MH_01_easy/ov2slam` | deferred | unknown |
| `vo-lc/euroc_mav/MH_01_easy/ov2slam` | deferred | unknown |
| `gnss-vio/rosariov2/sequence1/rtabmap_gps` | deferred | unknown |
| `gnss-vio/rosariov2/sequence1/vins_fusion_gps` | deferred | unknown |
| `vio/euroc_mav/MH_03_medium/voxel_svio` | deferred | unknown |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | deferred | unknown |

The timing subtotal is 34.6 serialized hours for 23 of the 117 required/missing actions; 94 have no comparable complete same-cell timing. It excludes native-error samples, diagnostics, unresolved blocked cases and evaluation/capture overhead. No total-campaign runtime is justified.

## Reproduction and preservation

Regenerate inventory, reconcile qualification, promote checked evaluations, then regenerate CSVs, TODO, reports and this handoff. The numerical evaluator has not changed. Review decisions fail closed if pinned evidence changes. Run `build_future_manifest.py` after source/input/asset refresh; ordinary validation is read-only and is not readiness approval. The historical authorship mapping and all original provenance hashes remain intact. The obsolete temporary pause remains explicitly revoked.
