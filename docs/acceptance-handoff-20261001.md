# Acceptance handoff — 2026-10-01

Generated from the checked inventory. The [claim review](paper-acceptance-20261001.md) defines eligibility, limitations and evidence. This includes the [matched-session calibration review](reference-review-20261001.md): Rosario frame-dependent metrics were corrected; accepted EuRoC values and original attempts are preserved. **Acceptance review complete; focused EuRoC OpenVINS/AirSLAM execution validated. ZED short-check readiness is recorded separately below.**

| Mode | Protocol-verified N=3 cells | Accepted accuracy claims | Limited accuracy claims | Failure-only claim observations | Required reruns | Missing | Blocked |
|---|---:|---:|---:|---:|---:|---:|---:|
| vo | 0 | 0 | 0 | 0 | 0 | 138 | 192 |
| vo-lc | 0 | 0 | 0 | 0 | 0 | 66 | 144 |
| vio | 0 | 0 | 0 | 0 | 0 | 132 | 168 |
| vio-lc | 0 | 0 | 0 | 0 | 0 | 114 | 96 |
| gnss-vio | 0 | 0 | 0 | 0 | 0 | 0 | 60 |

Protocol counts are separate from claim-status counts above. Success means a clean final export; native errors after saving remain failures with potentially usable accuracy.

| Mode | Verified attempts | Verified failures | Attempts | Evaluated | Clean exports | Observed failures | Unknown |
|---|---:|---:|---:|---:|---:|---:|---:|
| vo | 0 | 0 | 186 | 183 | 178 | 8 | 0 |
| vo-lc | 0 | 0 | 139 | 137 | 128 | 10 | 1 |
| vio | 0 | 0 | 160 | 160 | 151 | 9 | 0 |
| vio-lc | 0 | 0 | 88 | 86 | 86 | 2 | 0 |
| gnss-vio | 0 | 0 | 20 | 20 | 0 | 1 | 19 |

**OpenVINS cohort completeness:** each EuRoC sequence has historical N=1 plus patched N=2. The selected logical slots are consumed. One additional patched repetition per sequence would complete that implementation cohort, only if separately authorized. These three potential additions are separate from the 81 absent planned slots and are not scheduled here. Old cohorts are not resampled for success.


Future default actions: 0 reusable observations, 174 required reruns, 517 missing repetitions, 419 blocked. The separately authorized focused EuRoC campaign is complete; its 24 attempts yielded 23 final evaluations and one retained native refinement failure. The later ZED preparation used bounded diagnostics only; no ZED production repetitions or push occurred.

## Protocol-verified N=3 cells

| Cell | Accepted claim |
|---|---|

## Limited results and accepted failures

| Attempt | Acceptance | Specific limit |
|---|---|---|

## Exact required reruns

There are 174 remaining distinct confirmed cases after the current cohort selection. Superseded affected AirSLAM attempts remain in their original directories and the historical-cohort CSV. Preserve every original attempt and use a new physical ID/cohort.

| Cell | Logical repetitions | Concrete defect |
|---|---|---|
| `vo/rosariov2/sequence1/orbslam3` | r1 | historical_orb_library_identity_unverified |
| `vo/rosariov2/sequence5/orbslam3` | r1 | historical_orb_library_identity_unverified |
| `vo/hortimulti/strawberry02/orbslam3` | r1 | historical_orb_library_identity_unverified |
| `vo/hortimulti/strawberry03/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo/euroc_mav/MH_01_easy/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo/euroc_mav/MH_03_medium/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo/euroc_mav/MH_05_difficult/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo/zed2i/field1_110426_full_10fps_q90/orbslam3` | r1, r2, r3 | camera_fps_changed_15_to_10 |
| `vo-lc/rosariov2/sequence1/orbslam3` | r1 | historical_orb_library_identity_unverified |
| `vo-lc/rosariov2/sequence5/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo-lc/hortimulti/strawberry02/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo-lc/hortimulti/strawberry03/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo-lc/euroc_mav/MH_01_easy/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo-lc/euroc_mav/MH_03_medium/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo-lc/euroc_mav/MH_05_difficult/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | r1, r2, r3 | camera_fps_changed_15_to_10 |
| `vio/rosariov2/sequence1/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vio/rosariov2/sequence1/airslam` | r1, r2, r3 | rosario_identity_camera_imu_extrinsic |
| `vio/rosariov2/sequence1/basalt` | r1, r2, r3 | rosario_identity_camera_imu_extrinsic |
| `vio/rosariov2/sequence1/openvins` | r1 | rosario_identity_camera_imu_extrinsic |
| `vio/rosariov2/sequence1/voxel_svio` | r1, r2, r3 | rosario_identity_camera_imu_extrinsic |
| `vio/rosariov2/sequence5/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vio/rosariov2/sequence5/airslam` | r1, r2, r3 | rosario_identity_camera_imu_extrinsic |
| `vio/rosariov2/sequence5/basalt` | r1, r2, r3 | rosario_identity_camera_imu_extrinsic |
| `vio/rosariov2/sequence5/openvins` | r1 | rosario_identity_camera_imu_extrinsic |
| `vio/rosariov2/sequence5/voxel_svio` | r1, r2, r3 | rosario_identity_camera_imu_extrinsic |
| `vio/hortimulti/strawberry02/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified;horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry02/okvis2` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry02/okvis2x` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry02/airslam` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry02/basalt` | r1, r2, r3 | basalt_horti_undocumented_imu_noise |
| `vio/hortimulti/strawberry02/voxel_svio` | r1, r2, r3 | horti_voxel_initializer_camera_imu_offset_omitted |
| `vio/hortimulti/strawberry03/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified;horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry03/okvis2` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry03/okvis2x` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry03/airslam` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry03/basalt` | r1, r2, r3 | basalt_horti_undocumented_imu_noise |
| `vio/hortimulti/strawberry03/voxel_svio` | r1, r2, r3 | horti_voxel_initializer_camera_imu_offset_omitted |
| `vio/euroc_mav/MH_01_easy/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vio/euroc_mav/MH_01_easy/openvins` | r1, r2, r3 | openvins_euroc_vio_split_implementation_groups |
| `vio/euroc_mav/MH_03_medium/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vio/euroc_mav/MH_03_medium/openvins` | r1, r2, r3 | openvins_euroc_vio_split_implementation_groups |
| `vio/euroc_mav/MH_05_difficult/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vio/euroc_mav/MH_05_difficult/openvins` | r1, r2, r3 | openvins_euroc_vio_split_implementation_groups |
| `vio-lc/rosariov2/sequence1/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vio-lc/rosariov2/sequence1/airslam` | r1, r2, r3 | rosario_identity_camera_imu_extrinsic |
| `vio-lc/rosariov2/sequence5/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vio-lc/rosariov2/sequence5/airslam` | r1, r2, r3 | rosario_identity_camera_imu_extrinsic |
| `vio-lc/hortimulti/strawberry02/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified;orb_horti_rectified_camera_imu_extrinsic;horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry02/okvis2` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry02/okvis2x` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry02/airslam` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry03/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified;orb_horti_rectified_camera_imu_extrinsic;horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry03/okvis2` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry03/okvis2x` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry03/airslam` | r1, r2, r3 | horti_camera_imu_time_offset_uncompensated |
| `vio-lc/euroc_mav/MH_01_easy/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vio-lc/euroc_mav/MH_03_medium/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vio-lc/euroc_mav/MH_05_difficult/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | r1 | zed_factory_camera_imu_rotation_omitted |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2` | r1 | zed_factory_camera_imu_rotation_omitted |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2x` | r1 | zed_factory_camera_imu_rotation_omitted |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/airslam` | r1 | zed_factory_camera_imu_rotation_omitted |
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
| `vo/rosariov2/sequence1/cuvslam` | r1, r2, r3 |
| `vo/rosariov2/sequence1/svo_pro` | r1, r2, r3 |
| `vo/rosariov2/sequence1/dsol` | r1, r2, r3 |
| `vo/rosariov2/sequence5/orbslam3` | r2, r3 |
| `vo/rosariov2/sequence5/cuvslam` | r1, r2, r3 |
| `vo/rosariov2/sequence5/svo_pro` | r1, r2, r3 |
| `vo/rosariov2/sequence5/dsol` | r1, r2, r3 |
| `vo/hortimulti/strawberry02/orbslam3` | r2, r3 |
| `vo/hortimulti/strawberry02/cuvslam` | r1, r2, r3 |
| `vo/hortimulti/strawberry02/svo_pro` | r1, r2, r3 |
| `vo/hortimulti/strawberry02/dsol` | r1, r2, r3 |
| `vo/hortimulti/strawberry03/cuvslam` | r1, r2, r3 |
| `vo/hortimulti/strawberry03/svo_pro` | r1, r2, r3 |
| `vo/hortimulti/strawberry03/dsol` | r1, r2, r3 |
| `vo/euroc_mav/MH_01_easy/cuvslam` | r1, r2, r3 |
| `vo/euroc_mav/MH_01_easy/svo_pro` | r1, r2, r3 |
| `vo/euroc_mav/MH_01_easy/dsol` | r1, r2, r3 |
| `vo/euroc_mav/MH_03_medium/cuvslam` | r1, r2, r3 |
| `vo/euroc_mav/MH_03_medium/svo_pro` | r1, r2, r3 |
| `vo/euroc_mav/MH_03_medium/dsol` | r1, r2, r3 |
| `vo/euroc_mav/MH_05_difficult/cuvslam` | r1, r2, r3 |
| `vo/euroc_mav/MH_05_difficult/svo_pro` | r1, r2, r3 |
| `vo/euroc_mav/MH_05_difficult/dsol` | r1, r2, r3 |
| `vo/zed2i/field1_110426_full_10fps_q90/cuvslam` | r1, r2, r3 |
| `vo/zed2i/field1_110426_full_10fps_q90/svo_pro` | r1, r2, r3 |
| `vo/zed2i/field1_110426_full_10fps_q90/dsol` | r1, r2, r3 |
| `vo/citrusfarm/seq04/orbslam3` | r1, r2, r3 |
| `vo/citrusfarm/seq04/okvis2` | r1, r2, r3 |
| `vo/citrusfarm/seq04/okvis2x` | r1, r2, r3 |
| `vo/citrusfarm/seq04/airslam` | r1, r2, r3 |
| `vo/citrusfarm/seq04/basalt` | r1, r2, r3 |
| `vo/citrusfarm/seq04/ov2slam` | r1, r2, r3 |
| `vo/citrusfarm/seq04/dpvo` | r1, r2, r3 |
| `vo/citrusfarm/seq04/macvo` | r1, r2, r3 |
| `vo/citrusfarm/seq04/cuvslam` | r1, r2, r3 |
| `vo/citrusfarm/seq04/svo_pro` | r1, r2, r3 |
| `vo/citrusfarm/seq04/dsol` | r1, r2, r3 |
| `vo/citrusfarm/seq07/orbslam3` | r1, r2, r3 |
| `vo/citrusfarm/seq07/okvis2` | r1, r2, r3 |
| `vo/citrusfarm/seq07/okvis2x` | r1, r2, r3 |
| `vo/citrusfarm/seq07/airslam` | r1, r2, r3 |
| `vo/citrusfarm/seq07/basalt` | r1, r2, r3 |
| `vo/citrusfarm/seq07/ov2slam` | r1, r2, r3 |
| `vo/citrusfarm/seq07/dpvo` | r1, r2, r3 |
| `vo/citrusfarm/seq07/macvo` | r1, r2, r3 |
| `vo/citrusfarm/seq07/cuvslam` | r1, r2, r3 |
| `vo/citrusfarm/seq07/svo_pro` | r1, r2, r3 |
| `vo/citrusfarm/seq07/dsol` | r1, r2, r3 |
| `vo-lc/rosariov2/sequence1/orbslam3` | r2, r3 |
| `vo-lc/rosariov2/sequence1/cuvslam` | r1, r2, r3 |
| `vo-lc/rosariov2/sequence5/cuvslam` | r1, r2, r3 |
| `vo-lc/hortimulti/strawberry02/cuvslam` | r1, r2, r3 |
| `vo-lc/hortimulti/strawberry03/cuvslam` | r1, r2, r3 |
| `vo-lc/euroc_mav/MH_01_easy/cuvslam` | r1, r2, r3 |
| `vo-lc/euroc_mav/MH_03_medium/cuvslam` | r1, r2, r3 |
| `vo-lc/euroc_mav/MH_05_difficult/cuvslam` | r1, r2, r3 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2` | r3 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x` | r2, r3 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/cuvslam` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq04/orbslam3` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq04/okvis2` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq04/okvis2x` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq04/airslam` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq04/ov2slam` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq04/dpvo` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq04/cuvslam` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq07/orbslam3` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq07/okvis2` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq07/okvis2x` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq07/airslam` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq07/ov2slam` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq07/dpvo` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq07/cuvslam` | r1, r2, r3 |
| `vio/rosariov2/sequence1/openvins` | r2, r3 |
| `vio/rosariov2/sequence1/cuvslam` | r1, r2, r3 |
| `vio/rosariov2/sequence1/svo_pro` | r1, r2, r3 |
| `vio/rosariov2/sequence1/mast3r_fusion` | r1, r2, r3 |
| `vio/rosariov2/sequence5/openvins` | r2, r3 |
| `vio/rosariov2/sequence5/cuvslam` | r1, r2, r3 |
| `vio/rosariov2/sequence5/svo_pro` | r1, r2, r3 |
| `vio/rosariov2/sequence5/mast3r_fusion` | r1, r2, r3 |
| `vio/hortimulti/strawberry02/openvins` | r2, r3 |
| `vio/hortimulti/strawberry02/cuvslam` | r1, r2, r3 |
| `vio/hortimulti/strawberry02/svo_pro` | r1, r2, r3 |
| `vio/hortimulti/strawberry02/mast3r_fusion` | r1, r2, r3 |
| `vio/hortimulti/strawberry03/openvins` | r2, r3 |
| `vio/hortimulti/strawberry03/cuvslam` | r1, r2, r3 |
| `vio/hortimulti/strawberry03/svo_pro` | r1, r2, r3 |
| `vio/hortimulti/strawberry03/mast3r_fusion` | r1, r2, r3 |
| `vio/euroc_mav/MH_01_easy/cuvslam` | r1, r2, r3 |
| `vio/euroc_mav/MH_01_easy/svo_pro` | r1, r2, r3 |
| `vio/euroc_mav/MH_01_easy/mast3r_fusion` | r1, r2, r3 |
| `vio/euroc_mav/MH_03_medium/cuvslam` | r1, r2, r3 |
| `vio/euroc_mav/MH_03_medium/svo_pro` | r1, r2, r3 |
| `vio/euroc_mav/MH_03_medium/mast3r_fusion` | r1, r2, r3 |
| `vio/euroc_mav/MH_05_difficult/cuvslam` | r1, r2, r3 |
| `vio/euroc_mav/MH_05_difficult/svo_pro` | r1, r2, r3 |
| `vio/euroc_mav/MH_05_difficult/mast3r_fusion` | r1, r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/cuvslam` | r1, r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/svo_pro` | r1, r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/mast3r_fusion` | r1, r2, r3 |
| `vio/citrusfarm/seq04/orbslam3` | r1, r2, r3 |
| `vio/citrusfarm/seq04/okvis2` | r1, r2, r3 |
| `vio/citrusfarm/seq04/okvis2x` | r1, r2, r3 |
| `vio/citrusfarm/seq04/airslam` | r1, r2, r3 |
| `vio/citrusfarm/seq04/basalt` | r1, r2, r3 |
| `vio/citrusfarm/seq04/openvins` | r1, r2, r3 |
| `vio/citrusfarm/seq04/voxel_svio` | r1, r2, r3 |
| `vio/citrusfarm/seq04/cuvslam` | r1, r2, r3 |
| `vio/citrusfarm/seq04/svo_pro` | r1, r2, r3 |
| `vio/citrusfarm/seq04/mast3r_fusion` | r1, r2, r3 |
| `vio/citrusfarm/seq07/orbslam3` | r1, r2, r3 |
| `vio/citrusfarm/seq07/okvis2` | r1, r2, r3 |
| `vio/citrusfarm/seq07/okvis2x` | r1, r2, r3 |
| `vio/citrusfarm/seq07/airslam` | r1, r2, r3 |
| `vio/citrusfarm/seq07/basalt` | r1, r2, r3 |
| `vio/citrusfarm/seq07/openvins` | r1, r2, r3 |
| `vio/citrusfarm/seq07/voxel_svio` | r1, r2, r3 |
| `vio/citrusfarm/seq07/cuvslam` | r1, r2, r3 |
| `vio/citrusfarm/seq07/svo_pro` | r1, r2, r3 |
| `vio/citrusfarm/seq07/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/rosariov2/sequence1/cuvslam` | r1, r2, r3 |
| `vio-lc/rosariov2/sequence1/svo_pro` | r1, r2, r3 |
| `vio-lc/rosariov2/sequence1/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/rosariov2/sequence5/cuvslam` | r1, r2, r3 |
| `vio-lc/rosariov2/sequence5/svo_pro` | r1, r2, r3 |
| `vio-lc/rosariov2/sequence5/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/hortimulti/strawberry02/cuvslam` | r1, r2, r3 |
| `vio-lc/hortimulti/strawberry02/svo_pro` | r1, r2, r3 |
| `vio-lc/hortimulti/strawberry02/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/hortimulti/strawberry03/cuvslam` | r1, r2, r3 |
| `vio-lc/hortimulti/strawberry03/svo_pro` | r1, r2, r3 |
| `vio-lc/hortimulti/strawberry03/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_01_easy/cuvslam` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_01_easy/svo_pro` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_01_easy/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_03_medium/cuvslam` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_03_medium/svo_pro` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_03_medium/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_05_difficult/cuvslam` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_05_difficult/svo_pro` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_05_difficult/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2` | r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2x` | r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/airslam` | r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/cuvslam` | r1, r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/svo_pro` | r1, r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq04/orbslam3` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq04/okvis2` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq04/okvis2x` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq04/airslam` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq04/cuvslam` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq04/svo_pro` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq04/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq07/orbslam3` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq07/okvis2` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq07/okvis2x` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq07/airslam` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq07/cuvslam` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq07/svo_pro` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq07/mast3r_fusion` | r1, r2, r3 |
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
| execution_exit_nonzero_or_unverified | 3 |
| installed_basalt_binary_to_source_revision_not_established | 3 |
| keyframe_only_accuracy_not_dense_frame_comparison | 3 |
| native_build_source_linkage_and_loaded_dependency_closure_unverified | 18 |
| reviewed_evidence_changed:docs/reference-review-20261001.md | 401 |
| zed_reference_camera_lever_arm_heading_and_altitude_assumptions_unverified | 18 |
| zed_reference_orientation_unavailable | 18 |
| zed_serial_specific_imu_rotation_and_time_offset_unverified | 18 |

## Completed focused execution

The three EuRoC OpenVINS/AirSLAM integration targets and first full gates passed. All six missing OpenVINS repetitions and all 18 corrected AirSLAM slots were consumed once, with immediate evaluation where final output existed and no success-conditioned retries. MH05 VIO-LC run4 has a native refinement SIGSEGV without final output (later reproduced in the map publisher; exact cause unresolved); runs5–6 succeeded. See [the focused campaign](euroc-focused-campaign-20261001.md) for source, build, configuration, output and shutdown evidence. AirSLAM supports sparse-keyframe accuracy; OpenVINS original run1 limitations and its separate implementation cohort remain. Protocol ticks include verified failures and supported sparse/partial outputs; OpenVINS implementation cohorts remain N=1 and N=2.

## Remaining execution prerequisites

The [ZED preparation](zed-preparation-20261002.md) validates 15 repaired algorithm/mode paths on a fixed 60-second input, including all four ORB modes. Voxel shutdown/failure reporting is verified, but initialization and successful trajectory export remain unverified. The non-ZED ORB build and OV2SLAM shutdown issues remain prerequisites. Rosario/HortiMulti/GNSS calibration/reference blockers are unchanged. Historical OKVIS interruptions remain unresolved outcomes. No production execution is authorized by this handoff.

**ZED cohort plan:** retain nine complete N=3 cells (27 observations). The remaining sixteen cells need 48 new attempts: 17 setup replacements, 25 missing slots and six separately labelled cohort-completion attempts. The latter preserve historical outcomes and are not confirmed parameter defects. Use the alternative `results/zed-preparation-20261002/campaign/manifest.json`; do not execute it in addition to the overlapping all-mode plan. See the ZED report for bounded readiness and timing proxies.

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
| `vio/euroc_mav/MH_01_easy/cuvslam` | deferred | unknown |
| `vio-lc/euroc_mav/MH_01_easy/cuvslam` | deferred | unknown |
| `vo/euroc_mav/MH_01_easy/cuvslam` | deferred | unknown |
| `vo-lc/euroc_mav/MH_01_easy/cuvslam` | deferred | unknown |
| `vo/euroc_mav/MH_01_easy/dpvo` | deferred | 86.2 |
| `vo-lc/euroc_mav/MH_01_easy/dpvo` | deferred | 95.0 |
| `vo/euroc_mav/MH_01_easy/dsol` | deferred | unknown |
| `vo/euroc_mav/MH_01_easy/macvo` | deferred | 721.6 |
| `vio/euroc_mav/MH_01_easy/mast3r_fusion` | deferred | unknown |
| `vio-lc/euroc_mav/MH_01_easy/mast3r_fusion` | deferred | unknown |
| `vio/euroc_mav/MH_01_easy/okvis2` | deferred | 208.2 |
| `vio-lc/euroc_mav/MH_01_easy/okvis2` | deferred | 231.2 |
| `vo/euroc_mav/MH_01_easy/okvis2` | deferred | 229.8 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2` | ZED short check passed | 22199.5 |
| `gnss-vio/rosariov2/sequence1/okvis2x` | deferred | unknown |
| `vio/euroc_mav/MH_01_easy/okvis2x` | deferred | 203.5 |
| `vio-lc/euroc_mav/MH_01_easy/okvis2x` | deferred | 228.3 |
| `vo/euroc_mav/MH_01_easy/okvis2x` | deferred | 220.2 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x` | ZED short check passed | unknown |
| `vio/euroc_mav/MH_01_easy/openvins` | focused campaign validated | unknown |
| `gnss-vio/rosariov2/sequence1/openvins_gps` | deferred | unknown |
| `vio/zed2i/field1_110426_full_10fps_q90/orbslam3` | ZED short check passed | 5526.8 |
| `vio-lc/hortimulti/strawberry02/orbslam3` | deferred | unknown |
| `vo/zed2i/field1_110426_full_10fps_q90/orbslam3` | ZED short check passed | unknown |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | ZED short check passed | unknown |
| `vo/euroc_mav/MH_01_easy/ov2slam` | deferred | 194.1 |
| `vo-lc/euroc_mav/MH_01_easy/ov2slam` | deferred | 194.2 |
| `gnss-vio/rosariov2/sequence1/rtabmap_gps` | deferred | unknown |
| `vio/euroc_mav/MH_01_easy/svo_pro` | deferred | unknown |
| `vio-lc/euroc_mav/MH_01_easy/svo_pro` | deferred | unknown |
| `vo/euroc_mav/MH_01_easy/svo_pro` | deferred | unknown |
| `gnss-vio/rosariov2/sequence1/vins_fusion_gps` | deferred | unknown |
| `vio/euroc_mav/MH_03_medium/voxel_svio` | deferred | 147.1 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | ZED short check passed | unknown |

The timing subtotal is 6.2 serialized hours for 1 of the 691 required/missing actions; 690 have no comparable complete same-cell timing. It excludes native-error samples, diagnostics, unresolved blocked cases and evaluation/capture overhead. No total-campaign runtime is justified.

## Reproduction and preservation

Regenerate inventory, reconcile qualification, promote checked evaluations, then regenerate CSVs, TODO, reports and this handoff. Rosario evaluation uses the matched physical IMU-to-camera transform. The later ZED review uses the versioned nominal 3D position reference and recovered factory extrinsics; non-ZED numerical scores remain unchanged. Review decisions fail closed if pinned evidence changes. Run `build_future_manifest.py` after source/input/asset refresh; ordinary validation is read-only and is not readiness approval. The historical authorship mapping and all original provenance hashes remain intact. The obsolete temporary pause remains explicitly revoked.
