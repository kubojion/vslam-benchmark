# Author-Sourced Quality Configuration Audit

> **Status note 2026-10-01:** this is the August configuration-policy record. The executed campaign used N=3 without GNSS, not the proposed N=5. Later Basalt VO, ZED calibration and OKVIS2 full-BA changes require cohort reconciliation; see [the current audit](campaigns/server-status-20261001.md). The noise procedure is documented in [noise derivation](okvis-imu-noise-derivation.md).

> **Repair update:** Basalt VO now explicitly selects 0.03 m only for Rosario's
> 0.0497337 m baseline; the other datasets retain the upstream 0.05 m gate. This is
> a disclosed geometry compatibility exception to the August fixed-profile policy.
> ORB selects the sequence-specific ZED 10 FPS profile; historical 15 FPS runs need
> a corrected cohort. See [the repair evidence](repair-audit-20261001.md#configuration-selection-and-native-export-checks).
> The future target is N=3 across all five modes, retaining algorithm exclusions;
> preparation is ongoing and no campaign is authorized by this documentation change.

**Date:** 2026-08-26
**Scope:** algorithms represented in the five benchmark tables (`vo`, `vo-lc`,
`vio`, `vio-lc`, and `gnss-vio`)
**Status:** implemented on 2026-08-26; final campaign validation remains

## 1. Backup made before the audit

The pre-audit configuration state is preserved outside the repository at:

`/data/imoroz/vslam-config-backups/2026-08-26-before-author-quality-audit/`

The directory contains `configuration-snapshot.tar.gz` and `CONTENTS.md`. The
archive contains all benchmark configs and runners plus the relevant
configuration trees from the checked-out upstream sources.

- Archive entries: 481
- Archive size: 3.4 MB
- SHA-256:
  `bfc211ad4bd8342f50d6658f4f22671298373a473b2f5a6f1ae73a3f92790bc3`
- `gzip -t` verification: passed
- Repository commit at capture time: `f38545b`

## 2. What “author quality configuration” means here

Upstream projects use the word “configuration” differently. Only OV²SLAM and
MAC-VO publish an explicitly accuracy-oriented profile. Some projects publish
the exact evaluation or paper configuration, most publish a dataset example,
and some publish no universal quality preset at all.

This audit assigns each source one of four evidence levels:

1. **Explicit quality profile:** authors label a profile as accurate,
   performant, or best-performing.
2. **Paper/evaluation profile:** authors say that an evaluation script or config
   was used for reported results.
3. **Official dataset example:** the authors' supported example, but not a claim
   that the values maximize accuracy.
4. **No universal author profile:** a framework or a benchmark-created
   composite for which no author-endorsed cross-dataset quality config exists.

“Official example” must not be described in the paper as “optimal.” Likewise,
an adjustment made by this benchmark must be labelled as such rather than
attributed to the authors.

## 3. Recommended cross-dataset policy

Use one frozen **algorithm profile** per algorithm and run type. Keep sensor and
dataset facts in a separate **sensor profile**.

The algorithm profile may contain feature thresholds, keypoint budgets,
windows, optimizer settings, robust-estimation settings, neural checkpoints,
and loop-closure settings. These values remain fixed across all datasets.

The sensor profile may vary only where the physical input varies:

- camera model, resolution, intrinsics, distortion, and stereo extrinsics;
- camera-to-IMU and antenna lever-arm transforms;
- measured frame and IMU rates, time offsets, and rolling-shutter facts;
- IMU noise values obtained from the sensor specification or Allan analysis;
- GNSS timestamps, coordinate convention, covariance, and quality variant;
- paths, topics, and output locations.

Run-type switches are also allowed: IMU is enabled only in `vio`, `vio-lc`, and
`gnss-vio`; loop closure is enabled only in `vo-lc` and `vio-lc`.

For this quality-only campaign:

- process every available frame (`stride=1`, no deliberate frame dropping);
- disable external real-time enforcement and transport-induced dropping;
- disable viewers and plotting only when an A/B check confirms that they do not
  change estimates;
- give the active run the full machine and execute cells serially;
- use the authors' released checkpoint without dataset fine-tuning;
- do not search parameters against final evaluation ground truth;
- use N=5 where the implementation is stochastic or thread scheduling causes
  material variation.

This is a reproducible, no-sweep policy. It supports the defensible paper claim
“author-recommended quality/paper configuration, adapted only for sensor facts
and unrestricted offline processing.” It does not support the stronger and
usually unprovable claim that every algorithm reached its absolute optimum.

## 4. Source and action summary

| Algorithm | Best primary author source | Evidence | Recommended action |
|---|---|---|---|
| ORB-SLAM3 | Official EuRoC stereo and stereo-inertial examples | Dataset example | Use the official ORB frontend globally; sensor calibration varies |
| OKVIS2 | Official `config/euroc.yaml` | Dataset example | Remove HortiMulti frontend tuning; use the upstream estimator profile globally |
| OKVIS2-X | Paper configs under `config/euroc` | Paper/evaluation | Use the paper state-estimator profile; vary only sensors and declared mode |
| AirSLAM | Official EuRoC VO, camera, and map-refinement configs | Dataset/paper example | Retain the author VO/map-refinement profile and measured IMU fields |
| Basalt | Official EuRoC VO and VIO JSON configs | Dataset/paper example | Use the distinct upstream VO and VIO configs; remove HortiMulti algorithm tuning |
| OV²SLAM | Upstream `parameter_files/accurate` | Explicit quality | Use `accurate` globally; change only calibration and LC mode |
| DPVO / DPV-SLAM | Upstream `config/default.yaml` and loop-closure defaults | Official accuracy-oriented default | Keep the released default; all frames; LC only in DPV-SLAM mode |
| MAC-VO | `MACVO_Performant.yaml` | Explicit quality | Already selected; remove viewer overhead |
| OpenVINS | Official EuRoC config and calibration documentation | Dataset example | Freeze official algorithm values; replace local 250-point variants with 200 |
| Voxel-SVIO | Official `config/euroc.yaml` | Paper/dataset example | Current algorithm fields largely match; retain them globally |
| MegaSaM | Official evaluation pipeline scripts | Paper/evaluation | Reproduce script defaults; remove or wire the currently unused benchmark YAMLs |
| MASt3R-SLAM | Official evaluation config/scripts and `base.yaml` | Paper/evaluation | Use calibrated base profile with all frames; disclose departure from paper subsampling |
| CIFASIS GNSS-SI | Official Rosario config | Dataset/paper example | Retain author ORB settings; substitute only measured rig/GNSS facts |
| VINS-Fusion+GPS | Official EuRoC stereo-IMU and KITTI GPS examples | Dataset examples | Retain author estimator values but remove the quality campaign's solver-time restriction |
| RTAB-Map+GPS | Official launch and parameter reference | No universal profile | Freeze one documented benchmark profile based on defaults; do not call it author-optimal |
| OpenVINS+GPS | OpenVINS config plus `robot_localization` GPS guide | Benchmark composite | Use the OpenVINS profile and documented GPS-fusion semantics; label as a composite |

## 5. Per-algorithm findings and links

### 5.1 ORB-SLAM3

Primary sources:

- [Official EuRoC stereo configuration](https://github.com/UZ-SLAMLab/ORB_SLAM3/blob/master/Examples/Stereo/EuRoC.yaml)
- [Official EuRoC stereo-inertial configuration](https://github.com/UZ-SLAMLab/ORB_SLAM3/blob/master/Examples/Stereo-Inertial/EuRoC.yaml)
- [Author EuRoC execution and evaluation instructions](https://github.com/UZ-SLAMLab/ORB_SLAM3/blob/master/README.md#5-euroc-examples)

The official EuRoC profile uses 1200 ORB features, scale factor 1.2, eight
pyramid levels, and FAST thresholds 20/7. These should be the frozen algorithm
fields for every rig. The current ZED2i configs use 2000 features and should be
returned to 1200 under the no-sweep policy. `Camera.RGB` is ignored for
grayscale input, so its present value is not an accuracy parameter.

### 5.2 OKVIS2

Primary sources:

- [Official repository and configuration guidance](https://github.com/ethz-mrl/okvis2)
- [Official EuRoC configuration](https://github.com/ethz-mrl/okvis2/blob/main/config/euroc.yaml)

The authors describe the config directory as examples with accuracy/compute
trade-offs, not as a universal optimum. The official EuRoC frontend uses
detection/absolute/matching thresholds 38/150/60, at most 700 keypoints, 0.60
overlap, and four matching threads. Current HortiMulti VO/VIO variants use
20/80, 1000 keypoints, and 0.55 overlap. That is undeclared dataset-specific
algorithm tuning and should be replaced by the official profile. Calibration,
IMU noise, IMU use, and LC use remain separate inputs.

### 5.3 OKVIS2-X

Primary sources:

- [Official README, synchronous paper applications and configuration semantics](https://github.com/ethz-mrl/OKVIS2-X/blob/main/README.md#running-the-synchronous-applications-for-dataset-processing)
- [Official EuRoC state-estimator configuration](https://github.com/ethz-mrl/OKVIS2-X/blob/main/config/euroc/okvis2.yaml)

The synchronous applications are explicitly identified as the applications
used for paper results. The current HortiMulti frontend has the same local
20/80/1000/0.55 tuning as OKVIS2 and should return to the paper profile. The
authors require the GNSS antenna offset `r_SA`; it must be measured and cannot
be left at zero merely to make a run start. Dense-mapping display/output can be
disabled when benchmarking only the estimator.

### 5.4 AirSLAM

Primary sources:

- [Official EuRoC visual-odometry configuration](https://github.com/sair-lab/AirSLAM/blob/master/configs/visual_odometry/vo_euroc.yaml)
- [Official EuRoC camera and IMU configuration](https://github.com/sair-lab/AirSLAM/blob/master/configs/camera/euroc.yaml)
- [Official EuRoC map-refinement configuration](https://github.com/sair-lab/AirSLAM/blob/master/configs/map_refinement/mr_euroc.yaml)
- [Official repository instructions](https://github.com/sair-lab/AirSLAM)

The author VO profile uses SuperPoint, LightGlue, 400 maximum keypoints, a
0.004 point threshold, a 0.75 line threshold, and 50-pixel minimum line length.
The benchmark already uses 400 keypoints. Keep the complete upstream VO and
map-refinement parameter sets fixed, while replacing camera and IMU fields with
measured rig values. The TensorRT engine is a compiled artifact of the same
author model, not an algorithm configuration. Dense trajectory export is an
output-validity fix and does not justify retuning the estimator.

### 5.5 Basalt

Primary sources:

- [Official Basalt data/configuration directory](https://gitlab.com/VladyslavUsenko/basalt/-/tree/master/data)
- [Official EuRoC VO configuration](https://gitlab.com/VladyslavUsenko/basalt/-/blob/master/data/euroc_config_vo.json)
- [Official EuRoC VIO configuration](https://gitlab.com/VladyslavUsenko/basalt/-/blob/master/data/euroc_config.json)

Basalt publishes different VO and VIO configurations. The runner currently
uses `configs/basalt/vo_config.json` for both and only toggles `--use-imu`.
It should instead select the upstream VO base for `vo` and the upstream VIO
base for `vio`. The local HortiMulti file also changes grid size and estimator
weights; remove those algorithm changes. Camera/IMU calibration remains
dataset-specific. Basalt has no loop closure and must not populate `vio-lc` as
if it did.

### 5.6 OV²SLAM

Primary source:

- [Official repository and accurate/average/fast profile definitions](https://github.com/ov2slam/ov2slam#parameters-file-description)
- [Official `accurate` parameter directory](https://github.com/ov2slam/ov2slam/tree/main/parameters_files/accurate)

This is the strongest author evidence in the audit: `accurate` is explicitly
described as the parameters used in the paper for the full method with loop
closure. Use its algorithm fields globally, set `force_realtime: 0`, and switch
`buse_loop_closer` only according to the run type. Current `nmaxdist` varies by
dataset (30, 35, 45, and 55), which violates the one-profile policy and should
be replaced by the selected accurate-profile value. Keep N=5 because robust
estimation is randomized.

### 5.7 DPVO / DPV-SLAM

Primary sources:

- [Official released configuration](https://github.com/princeton-vl/DPVO/blob/main/config/default.yaml)
- [Official configuration defaults and loop-closure settings](https://github.com/princeton-vl/DPVO/blob/main/dpvo/config.py)
- [Official demo entry point](https://github.com/princeton-vl/DPVO/blob/main/demo.py)

The authors mark the patch/window block as values that may be increased for
accuracy, but do not publish a single larger universal optimum. Therefore keep
the released `default.yaml`; do not invent a larger setting or tune it on test
sequences. The benchmark's stride 1 is a declared all-frames input policy. Set
loop closure only for the DPV-SLAM/`vo-lc` mode, use the same checkpoint, and
record predetermined seeds because patch selection is randomized.

### 5.8 MAC-VO

Primary sources:

- [Official repository and mode comparison](https://github.com/MAC-VO/MAC-VO#3-run-mac-vo)
- [Official performant configuration](https://github.com/MAC-VO/MAC-VO/blob/main/Config/Experiment/MACVO/MACVO_Performant.yaml)

The authors describe Performant Mode as their best-performing mode at moderate
speed. The runner selects it and now omits `--useRR`, which starts the optional
Rerun visualizer and is not part of estimation. Startup and 150 frames were
validated without the viewer; the complete final validation run remains part
of campaign qualification. Continue using the same frontend and pose-network
checkpoints on every dataset.

### 5.9 OpenVINS

Primary sources:

- [Official EuRoC configuration directory](https://github.com/rpng/open_vins/tree/master/config/euroc_mav)
- [Official getting-started tutorial](https://docs.openvins.com/gs-tutorial.html)
- [Official calibration guidance](https://docs.openvins.com/gs-calibration.html)

OpenVINS publishes a supported EuRoC example rather than a quality preset. Use
its algorithm settings globally. In particular, the current EuRoC/HortiMulti
configs use 200 tracked points while Rosario and ZED2i use 250; restore 200 for
one consistent profile. Dynamic initialization may be enabled globally when
the benchmark sequences begin in motion. IMU and camera-chain files are sensor
measurements, and their noise values should come from calibration rather than
accuracy tuning.

### 5.10 Voxel-SVIO

Primary sources:

- [Official repository and EuRoC invocation](https://github.com/ZikangYuan/voxel_svio#1-run-on-euroc_mav)
- [Official EuRoC configuration](https://github.com/ZikangYuan/voxel_svio/blob/main/config/euroc.yaml)

There is no fast/quality split. The official paper example already uses a large
feature/map profile, including 500 tracked points. Current benchmark algorithm
fields are largely consistent across datasets and should remain fixed. Only
the rig calibration, IMU noise, rates, and the documented MH01 initialization
window exception should vary.

### 5.11 MegaSaM

Primary sources:

- [Official repository](https://github.com/mega-sam/mega-sam)
- [Official demo evaluation pipeline](https://github.com/mega-sam/mega-sam/blob/main/tools/evaluate_demo.sh)
- [Official camera-tracking entry point](https://github.com/mega-sam/mega-sam/blob/main/camera_tracking_scripts/test_demo.py)

MegaSaM publishes evaluation scripts rather than YAML quality profiles. The
benchmark runner correctly reproduces the three pose-producing stages and
omits depth-only post-refinement. At audit time, `configs/megasam/*.yaml` was
not read by `run_megasam.sh` and gave a false impression that camera and stride
settings were effective. The implementation removed those files and now passes
and records the official tracking-script defaults explicitly.

### 5.12 MASt3R-SLAM

Primary sources:

- [Official evaluation instructions](https://github.com/rmurai0610/MASt3R-SLAM#running-evaluations)
- [Official calibrated evaluation config](https://github.com/rmurai0610/MASt3R-SLAM/blob/main/config/eval_calib.yaml)
- [Official base config](https://github.com/rmurai0610/MASt3R-SLAM/blob/main/config/base.yaml)
- [Official EuRoC evaluation script](https://github.com/rmurai0610/MASt3R-SLAM/blob/main/scripts/eval_euroc.sh)

The paper evaluation runs single-threaded and uses `dataset.subsample: 2`.
That is the exact reproduction profile, but it conflicts with this campaign's
declared all-frames, full-machine quality policy. Use the calibrated base
profile with `subsample: 1`, and state clearly that this is an input-policy
adaptation rather than the exact paper evaluation. Keep retrieval `k=3` for
`vo-lc` and disable candidates for `vo`. Do not tune matching/tracking values by
dataset.

### 5.13 CIFASIS GNSS-SI

Primary sources:

- [Official repository and Rosario invocation](https://github.com/CIFASIS/gnss-stereo-inertial-fusion#rosario-dataset)
- [Official Rosario configuration](https://github.com/CIFASIS/gnss-stereo-inertial-fusion/blob/main/Examples/Stereo-Inertial/rosario_dataset/Rosario_3_0.yaml)

Use the author's ORB/estimator values as the fixed algorithm profile. The
converted Rosario v2 input necessarily needs its own resolution, calibration,
timestamps, coordinate conversion, and measured antenna lever arm. Use real
GNSS covariance for real measurements and keep simulated GNSS noise disabled
unless a separately labelled synthetic-noise experiment is being reproduced.

### 5.14 VINS-Fusion+GPS

Primary sources:

- [Official EuRoC stereo-IMU example](https://github.com/HKUST-Aerial-Robotics/VINS-Fusion/blob/master/config/euroc/euroc_stereo_imu_config.yaml)
- [Official KITTI GPS example](https://github.com/HKUST-Aerial-Robotics/VINS-Fusion/blob/master/config/kitti_raw/kitti_10_03_config.yaml)
- [Official execution instructions](https://github.com/HKUST-Aerial-Robotics/VINS-Fusion#3-euroc-example)

The official estimator profile uses 150 features, 30-pixel spacing, 10 Hz
feature publication, eight solver iterations, and 10-pixel keyframe parallax.
The current configs preserve these values. The official `max_solver_time` is
explicitly a real-time guarantee, so it is incompatible with the stated
quality-only campaign. Set it high enough that the eight-iteration/convergence
limit, rather than wall time, terminates every optimization, and record this as
a benchmark adaptation. `estimate_td` and the camera/IMU/GNSS facts remain
sensor-specific.

The upstream GPS fusion is described as a toy example. Results must be labelled
accordingly; there is no author-published agricultural quality preset.

### 5.15 RTAB-Map+GPS

Primary sources:

- [Official ROS 2 launch file](https://github.com/introlab/rtabmap_ros/blob/ros2/rtabmap_launch/launch/rtabmap.launch.py)
- [Official core parameter definitions](https://github.com/introlab/rtabmap/blob/master/corelib/include/rtabmap/core/Parameters.h)
- [Official parameter documentation](https://github.com/introlab/rtabmap/blob/master/doxygen/mainpage.md)

RTAB-Map is a configurable framework and does not publish one universal
stereo+IMU+GPS quality profile. Start from the official defaults, freeze one
benchmark-owned algorithm profile, and document every override. Set
`odom_always_process_most_recent_frame=false` so offline overload does not skip
queued frames. Current HortiMulti commentary describes dataset-specific
loop/GPS changes; separate actual sensor covariance from algorithm thresholds
before freezing the profile. The final paper must call this a documented
benchmark profile, not an author-optimal config.

### 5.16 OpenVINS+GPS composite

Primary sources:

- [OpenVINS EuRoC configuration](https://github.com/rpng/open_vins/tree/master/config/euroc_mav)
- [`robot_localization` GPS integration guide](https://github.com/cra-ros-pkg/robot_localization/blob/rolling-devel/doc/integrating_gps.rst)
- [`navsat_transform_node` reference](https://github.com/cra-ros-pkg/robot_localization/blob/rolling-devel/doc/navsat_transform_node.rst)
- [Official navsat parameter template](https://github.com/cra-ros-pkg/robot_localization/blob/rolling-devel/params/navsat_transform.yaml)

This is not an algorithm configuration published by the OpenVINS authors. It
is a benchmark composite: OpenVINS odometry plus `robot_localization`. Apply the
frozen OpenVINS profile, then follow the GPS integration requirements: ENU
heading convention, valid heading and covariance, and
`odomN_differential=false` for the transformed GPS odometry. Report it as
“OpenVINS + robot_localization,” not as native OpenVINS GNSS fusion.

## 6. Implemented changes

The approved implementation completed the following:

1. Basalt now selects the installed upstream VO or VIO profile and rejects LC
   modes it does not implement.
2. HortiMulti OKVIS2/OKVIS2-X frontends now use the same upstream profile as
   every other dataset. Rosario/HortiMulti IMU priors have a reproducible
   signal-derived basis documented in `docs/okvis-imu-noise-derivation.md`.
3. OKVIS2-X GNSS configurations now contain the calibrated antenna lever arms.
4. OV²SLAM uses `nmaxdist: 35` from the accurate profile everywhere.
5. ORB-SLAM3 uses 1200 features and OpenVINS uses 200 points everywhere.
6. MegaSaM explicitly passes and records its upstream tracking defaults; the
   unused benchmark YAMLs were removed.
7. MAC-VO runs without the optional Rerun viewer and rejects non-VO modes.
8. VINS-Fusion's offline solver is allowed to terminate by convergence or its
   eight-iteration limit rather than the upstream real-time deadline.
9. RTAB-Map uses one small documented INI and is instructed to process every
   queued odometry frame.

Validation is for correctness, complete input consumption, and detecting
regressions—not for choosing whichever config wins on the final datasets.

No broad parameter sweep is required. Validation is for correctness, complete
input consumption, and detecting regressions—not for choosing whichever config
wins on the final datasets.
