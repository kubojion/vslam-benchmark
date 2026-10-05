# HortiMulti rerun decisions and fixes (5 October 2026)

Decided by the user on 5 October 2026 after a read-only audit of every saved HortiMulti
VO, VIO, VO-LC and VIO-LC run (inputs and calibration, parameter fairness, run outcomes),
recorded by Claude. GNSS-VIO was out of scope; its HortiMulti offsets were zeroed only so
the camera-clock IMU input below is not applied twice. Attempt-level records:
`docs/campaigns/user-rerun-decisions-20261005.json`. Original run folders are kept.

## 1. Changes

| Change | Files | Why |
|---|---|---|
| One IMU noise profile for every HortiMulti estimator: gyro/accel noise density 0.0035 / 0.110 (recording-derived envelope), random walks 3.22094e-5 / 4.584471e-5 (published calibration) | ORB-SLAM3 inertial configs, AirSLAM `hortimulti_camera.yaml`, OpenVINS `kalibr_imu_chain.yaml`, Voxel-SVIO, Basalt (noise **and** bias walk), `configs/sensors/hortimulti.json` (cuVSLAM, MASt3R-Fusion). OKVIS2, OKVIS2-X and SVO Pro already used it. | Saved runs used three profiles: dataset Allan values (ORB-SLAM3, AirSLAM, OpenVINS, Voxel-SVIO), the envelope (OKVIS2, OKVIS2-X), and Basalt's July sweep leftovers (0.5 / 0.006, bias 0.1 / 0.001). Same rule as ZED and CitrusFarm. |
| Camera-clock IMU input: `datasets/hortimulti/<seq>/mav0/imu0/data.csv` = IMU-clock stamps − 9.160379 ms; original kept in `sources/microstrain_imu_clock.csv`, both digests in `manifest.json` (`scripts/data/hortimulti_imu_camera_clock.py`) | Every native offset set to 0: OKVIS2/OKVIS2-X `image_delay` (VIO, VIO-LC, OKVIS2-X GNSS-VIO), Basalt `cam_time_offset_ns`, Voxel-SVIO `timeshift_cam_imu_*`, VINS-Fusion `td`, sensor profile `camera_imu_time_offset_s` | The published Kalibr relation (`calibration.yaml` imu0, t_imu = t_cam + 9.160379 ms) had four treatments: not applied (ORB-SLAM3, AirSLAM, and OKVIS in every saved run), half applied (Voxel-SVIO initializer), estimated online from zero (OpenVINS), declared but with a disabled native path (Basalt). One input for everyone; outputs stay on the camera clock. Same mechanism as CitrusFarm. |
| OpenVINS `track_frequency` 10 → 31 on HortiMulti, ZED and CitrusFarm | `configs/openvins/{hortimulti,zed2i,citrusfarm}/estimator_config.yaml` | OpenVINS' ROS front end drops a frame arriving less than 1/track_frequency after the last accepted one (`ROS2Visualizer.cpp`). With 10 Hz cameras it processed 62 % (HortiMulti, 5946/9530 updates), 51 % (ZED: frames alternate 0.067/0.133 s) and about 63 % (CitrusFarm). 31 passes every frame of the three recordings (shortest interval 0.033 s). Rosario is unchanged and parked: its full runs keep 40–53 % of frames for a different, undiagnosed reason (the throttle passes 98–99 %). |
| OpenVINS also records `/ov_msckf/poseimu` → `trajectory_poseimu.txt` | `scripts/run/openvins_data_player.py` | The evaluated `odomimu` is IMU-rate propagation; `poseimu` is the filter state after each camera update (stamped camera time + online offset), as other estimators export. Which one is scored is an evaluation decision. |
| OV2SLAM `finit_parallax` 15 → 20, `nmin_covscore` 20 → 25 | `configs/ov2slam/hortimulti_vo{,_lc}.yaml` | HortiMulti-only values (July, no recorded reason); upstream accurate profile and every other dataset use 20 / 25. |
| Repaired native builds on HortiMulti | `scripts/run/run_voxel_svio.sh` (shutdown + initializer repair + v3 parameter audit build), `scripts/run/run_openvins.sh` (shutdown-repaired image) | Both runners had left HortiMulti alone on the old builds; a rerun would have used the Voxel-SVIO build with the initializer-offset defect. |

## 2. Values reviewed and kept

| Setting | Kept | Evidence |
|---|---|---|
| ORB-SLAM3 `Stereo.ThDepth` | 40 | The ORB-SLAM2 paper's rule: "A stereo keypoint is classified as close if its associated depth is less than 40 times the stereo/RGB-D baseline" (Mur-Artal & Tardós 2017, Sec. III-A); 7 of 10 upstream ORB-SLAM3 stereo configs use 40. In image terms the close-point disparity fx/ThDepth is 6.6 px, inside the upstream range (TUM-VI 4.8 – KITTI 20.5 px) and close to EuRoC (7.6), Rosario (8.1) and CitrusFarm (6.6). 80 would give 3.3 px, below every upstream config, treating poorly triangulated points as close. |
| AirSLAM `depth_upper_thr` | 15 m | The minimum stereo disparity is bf/depth_upper_thr (`camera.cc`). 15 m gives 2.44 px, inside the AirSLAM authors' range for non-indoor configs (RealSense 2.10, UMA 2.61, TartanAir 2.67 px) and next to ZED (2.68). 50 m would give 0.73 px, below any upstream config. Rosario (0.65 px) and CitrusFarm (1.26 px) fall below that range: noted for their own review. |
| OKVIS2-X LC `num_loop_closure_frames` 5, `do_final_ba` and `do_extrinsics_final_ba` true | unchanged | Cross-dataset consistency (EuRoC, Rosario); disclosed. ZED and CitrusFarm VIO-LC use 3: a cross-dataset item. The pre-final-BA trajectory is saved, so the reported trajectory kind can be chosen in evaluation. |
| OKVIS `g0` from each sequence's stationary start | unchanged | Same on every non-EuRoC dataset; disclosure. |
| ORB-SLAM3 VO-LC exports its largest map | unchanged | Upstream behaviour; coverage is reported. |

## 3. Runs this creates (str02 + str03, three repetitions each)

| Mode | Algorithms | Runs |
|---|---|---|
| VIO | ORB-SLAM3, AirSLAM, OKVIS2, OKVIS2-X, Basalt, Voxel-SVIO, OpenVINS | 42 |
| VIO-LC | ORB-SLAM3, AirSLAM, OKVIS2, OKVIS2-X | 24 |
| VO, VO-LC | ORB-SLAM3 (library decision, 3 October), OV2SLAM | 24 |
| all | cuVSLAM, SVO Pro, DSOL, MASt3R-Fusion (not yet run) | 60 |

Plus OpenVINS VIO on ZED (3) and CitrusFarm (seq04, seq07: 6), and ORB-SLAM3 VO and VIO on CitrusFarm
seq04/seq07, whose r1 is replaced after the ORB-SLAM3 source commit (section 5). Kept and re-evaluated only:
Basalt VO, OKVIS2 and OKVIS2-X VO/VO-LC, AirSLAM VO/VO-LC, MAC-VO, DPVO and DPV-SLAM.

## 4. Evaluation-side items (no rerun)

- Reference origin: Ouster `os_sensor` as the working convention (str03 strongly supported;
  str02 unresolved), changeable in evaluation. See
  `/data/imoroz/hortimulti-reference-analysis-20261004/extension/reports/ADDENDUM.txt`.
- Every method fits scale ≈ 1.03–1.04 against the reference: report SE(3) and Sim(3), do not rescale.
- OKVIS2-X LC: final-BA (with extrinsics) versus saved pre-final-BA trajectory.
- AirSLAM LC: refined versus pre-refinement (`trajectory_v0`) trajectory.
- OpenVINS: `odomimu` versus `poseimu`.
- The 2048→640 resize leaves the principal point half a pixel off for every algorithm alike (disclosure).

## 5. Open

- ORB-SLAM3 `Examples/Stereo-Inertial/stereo_inertial_euroc.cc` bounds fix (str03's IMU starts 0.10 s after
  the first frame): compiled into the binary since 15 September and recorded per run as an uncommitted diff;
  committed in the submodule on 5 October (user). Because the recorded source identity changes, the
  CitrusFarm ORB-SLAM3 VO and VIO cells holding only r1 cannot be pooled with later repetitions, so r1 is
  replaced (`orb_source_commit_single_group`).
- Rosario (parked by the user): one IMU noise profile, OpenVINS frame loss, AirSLAM depth threshold.
