# Acceptance handoff — 2026-10-01

Generated from the checked inventory. The [claim review](paper-acceptance-20261001.md) defines eligibility, limitations and evidence. This includes the [matched-session calibration review](reference-review-20261001.md): Rosario frame-dependent metrics were corrected; accepted EuRoC values and original attempts are preserved. **Acceptance review complete; focused EuRoC OpenVINS/AirSLAM execution validated. Other native paths remain unverified.**

| Mode | Clean accepted N=3 cells | Accepted repetitions | Limited repetitions | Observed failures accepted | Required reruns | Missing | Blocked |
|---|---:|---:|---:|---:|---:|---:|---:|
| vo | 17 | 53 | 19 | 4 | 3 | 6 | 107 |
| vo-lc | 9 | 33 | 21 | 2 | 3 | 5 | 80 |
| vio | 11 | 39 | 24 | 2 | 38 | 22 | 43 |
| vio-lc | 8 | 26 | 9 | 2 | 24 | 8 | 27 |
| gnss-vio | 0 | 0 | 0 | 0 | 5 | 40 | 15 |

Future default actions: 234 reusable observations, 73 required reruns, 81 missing repetitions, 272 blocked. The separately authorized focused EuRoC campaign is complete; its 24 attempts yielded 23 final evaluations and one retained native refinement failure. No other paths were executed and no push occurred.

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
| `results/vo/rosariov2/sequence1/orbslam3/run1` | valid_observed_failure | fused_stereo_imu_ppk_reference_not_independent_ground_truth; no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator |
| `results/vo/rosariov2/sequence5/orbslam3/run1` | valid_observed_failure | fused_stereo_imu_ppk_reference_not_independent_ground_truth; no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator |
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
| `results/vo/zed2i/field1_110426_full_10fps_q90/okvis2/run2` | valid_observed_failure | collapse_under_recorded_reference_diagnostic_not_verified_physical_scale; no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo-lc/rosariov2/sequence1/orbslam3/run1` | valid_observed_failure | fused_stereo_imu_ppk_reference_not_independent_ground_truth; no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator |
| `results/vo-lc/rosariov2/sequence1/ov2slam/run2` | valid_observed_failure | collapse_under_recorded_reference_diagnostic_not_verified_physical_scale; fused_stereo_imu_ppk_reference_not_independent_ground_truth; no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator |
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
| `results/vio/euroc_mav/MH_01_easy/airslam/run4` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_01_easy/airslam/run5` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_01_easy/airslam/run6` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_01_easy/openvins/run1` | accepted_with_limitation | saved_accuracy_with_recorded_nonzero_exit_no_clean_success |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run1` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick; native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run2` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick; native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run3` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick; native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_03_medium/orbslam3/run2` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick |
| `results/vio/euroc_mav/MH_03_medium/airslam/run4` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_03_medium/airslam/run5` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_03_medium/airslam/run6` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_03_medium/openvins/run1` | accepted_with_limitation | saved_accuracy_with_recorded_nonzero_exit_no_clean_success |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_05_difficult/airslam/run4` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_05_difficult/airslam/run5` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_05_difficult/airslam/run6` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_05_difficult/openvins/run1` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick |
| `results/vio/euroc_mav/MH_05_difficult/openvins/run2` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick |
| `results/vio/euroc_mav/MH_05_difficult/openvins/run3` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | valid_observed_failure | no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator; serial_specific_imu_rotation_and_timing_unverified; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run1` | valid_observed_failure | collapse_under_recorded_reference_diagnostic_not_verified_physical_scale; no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator; serial_specific_imu_rotation_and_timing_unverified; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vio-lc/euroc_mav/MH_01_easy/airslam/run4` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |
| `results/vio-lc/euroc_mav/MH_01_easy/airslam/run5` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |
| `results/vio-lc/euroc_mav/MH_01_easy/airslam/run6` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |
| `results/vio-lc/euroc_mav/MH_03_medium/orbslam3/run1` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick |
| `results/vio-lc/euroc_mav/MH_03_medium/airslam/run4` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |
| `results/vio-lc/euroc_mav/MH_03_medium/airslam/run5` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |
| `results/vio-lc/euroc_mav/MH_03_medium/airslam/run6` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |
| `results/vio-lc/euroc_mav/MH_05_difficult/airslam/run4` | valid_observed_failure | retain_failure_in_attempt_denominator; no_final_vio_lc_trajectory_no_accuracy_claim; intermediate_odometry_is_diagnostic_only; native_junction_database_segfault_root_cause_unresolved |
| `results/vio-lc/euroc_mav/MH_05_difficult/airslam/run5` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |
| `results/vio-lc/euroc_mav/MH_05_difficult/airslam/run6` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | valid_observed_failure | no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator; serial_specific_imu_rotation_and_timing_unverified; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |

## Exact required reruns

There are 73 remaining distinct confirmed cases after the current cohort selection. Superseded affected AirSLAM attempts remain in their original directories and the historical-cohort CSV. Preserve every original attempt and use a new physical ID/cohort.

| Cell | Logical repetitions | Concrete defect |
|---|---|---|
| `vo/zed2i/field1_110426_full_10fps_q90/orbslam3` | r1, r2, r3 | camera_fps_changed_15_to_10 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | r1, r2, r3 | camera_fps_changed_15_to_10 |
| `vio/rosariov2/sequence1/basalt` | r1, r2, r3 | rosario_identity_camera_imu_extrinsic |
| `vio/rosariov2/sequence1/openvins` | r1 | rosario_identity_camera_imu_extrinsic |
| `vio/rosariov2/sequence1/voxel_svio` | r1, r2, r3 | rosario_identity_camera_imu_extrinsic |
| `vio/rosariov2/sequence5/basalt` | r1, r2, r3 | rosario_identity_camera_imu_extrinsic |
| `vio/rosariov2/sequence5/openvins` | r1 | rosario_identity_camera_imu_extrinsic |
| `vio/rosariov2/sequence5/voxel_svio` | r1, r2, r3 | rosario_identity_camera_imu_extrinsic |
| `vio/hortimulti/strawberry02/orbslam3` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry02/okvis2` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry02/okvis2x` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry02/airslam` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry03/orbslam3` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry03/okvis2` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry03/okvis2x` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry03/airslam` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry02/orbslam3` | r1, r2, r3 | orb_horti_rectified_camera_imu_extrinsic;horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry02/okvis2` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry02/okvis2x` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry02/airslam` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry03/orbslam3` | r1, r2, r3 | orb_horti_rectified_camera_imu_extrinsic;horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry03/okvis2` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry03/okvis2x` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry03/airslam` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `gnss-vio/rosariov2/sequence1/cifasis_gnss_si` | r1 | rosario_v1_antenna_lever_arm_used_on_v2 |
| `gnss-vio/rosariov2/sequence1/okvis2x` | r1 | gnss_zero_antenna_lever_arm_in_native_log |
| `gnss-vio/rosariov2/sequence5/okvis2x` | r1 | gnss_zero_antenna_lever_arm_in_native_log |
| `gnss-vio/hortimulti/strawberry02/okvis2x` | r1 | gnss_zero_antenna_lever_arm_in_native_log |
| `gnss-vio/hortimulti/strawberry03/okvis2x` | r1 | gnss_zero_antenna_lever_arm_in_native_log |

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
| estimate_frame_unverified: output frame not established for cifasis_gnss_si | 3 |
| estimate_frame_unverified: output frame not established for openvins_gps | 4 |
| estimate_frame_unverified: output frame not established for rtabmap_gps | 4 |
| estimate_frame_unverified: output frame not established for vins_fusion_gps | 4 |
| gnss_reference_independence_and_global_frame_not_established | 15 |
| historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified | 15 |
| historical_workspace_digest_differs_keep_cohorts_separate | 6 |
| horti_february_reference_generation_origin_and_timestamp_linkage_unresolved | 103 |
| native_execution_cause_and_usable_export_missing | 2 |
| rosario_unchanged_images_virtual_projection_and_baseline_consistency_unresolved | 129 |
| zed_gnss_quality_support_and_3d_reference_uncertainty_unresolved | 40 |
| zed_reference_orientation_unavailable | 38 |
| zed_serial_specific_imu_rotation_and_time_offset_unverified | 8 |

## Completed focused execution

The three EuRoC OpenVINS/AirSLAM integration targets and first full gates passed. All six missing OpenVINS repetitions and all 18 corrected AirSLAM slots were consumed once, with immediate evaluation where final output existed and no success-conditioned retries. MH05 VIO-LC run4 has a native junction-database SIGSEGV without final output; runs5–6 succeeded. See [the focused campaign](euroc-focused-campaign-20261001.md) for source, build, configuration, output and shutdown evidence. AirSLAM supports sparse-keyframe accuracy; OpenVINS original run1 limitations and its separate implementation cohort remain. No automatic green tick follows from completing three exports.

## Remaining execution prerequisites

Resolve the remaining ORB FPS/IMU native loading, OV2SLAM/Voxel shutdown and ORB/OKVIS ZED failures before those paths are certified. Agricultural/GNSS reference, calibration and input blockers remain. No further estimator execution is authorized by this handoff.

The following representatives cover the other algorithm/mode branches; a validated EuRoC path does not certify another dataset.

| Diagnostic target | Execution status | Full-sequence historical seconds (not diagnostic estimate) |
|---|---|---:|
| `vio/euroc_mav/MH_01_easy/airslam` | focused campaign validated | unknown |
| `vio-lc/euroc_mav/MH_01_easy/airslam` | focused campaign validated | unknown |
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
| `vio/euroc_mav/MH_01_easy/openvins` | focused campaign validated | 191.8 |
| `gnss-vio/rosariov2/sequence1/openvins_gps` | deferred | unknown |
| `vio/zed2i/field1_110426_full_10fps_q90/orbslam3` | deferred | unknown |
| `vio-lc/hortimulti/strawberry02/orbslam3` | deferred | unknown |
| `vo/zed2i/field1_110426_full_10fps_q90/orbslam3` | deferred | unknown |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | deferred | unknown |
| `vo/euroc_mav/MH_01_easy/ov2slam` | deferred | unknown |
| `vo-lc/euroc_mav/MH_01_easy/ov2slam` | deferred | unknown |
| `gnss-vio/rosariov2/sequence1/rtabmap_gps` | deferred | unknown |
| `gnss-vio/rosariov2/sequence1/vins_fusion_gps` | deferred | unknown |
| `vio/euroc_mav/MH_03_medium/voxel_svio` | deferred | unknown |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | deferred | unknown |

The timing subtotal is 24.1 serialized hours for 11 of the 154 required/missing actions; 143 have no comparable complete same-cell timing. It excludes native-error samples, diagnostics, unresolved blocked cases and evaluation/capture overhead. No total-campaign runtime is justified.

## Reproduction and preservation

Regenerate inventory, reconcile qualification, promote checked evaluations, then regenerate CSVs, TODO, reports and this handoff. Rosario evaluation now uses the matched physical IMU-to-camera transform; other numerical fields are unchanged. Review decisions fail closed if pinned evidence changes. Run `build_future_manifest.py` after source/input/asset refresh; ordinary validation is read-only and is not readiness approval. The historical authorship mapping and all original provenance hashes remain intact. The obsolete temporary pause remains explicitly revoked.
