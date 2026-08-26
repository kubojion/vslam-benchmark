# Algorithm Setup and Fair-Comparison Audit

**Date:** 2026-08-26
**Scope:** Five-table benchmark (`vo`, `vo-lc`, `vio`, `vio-lc`, and `gnss-vio`) on the RTX 4090 server
**Detailed setup evidence:** EuRoC-MAV VO sweep of Basalt, AirSLAM, OKVIS2, OKVIS2-X, ORB-SLAM3, OV²SLAM, DPVO, and MAC-VO

## Executive summary

The server installation is fundamentally healthy, and the core EuRoC camera configurations are coherent. The stereo algorithms use consistent image dimensions, intrinsics, distortion parameters, timestamps, and stereo extrinsics. The VO configurations also disable loop closure as intended.

The repository already has the correct high-level comparison structure: five result tables, one for each run type. Algorithms should be compared against the other algorithms in every run type they genuinely support. They should not be forced into a common sensor modality, feature count, thread count, memory budget, or simplified configuration. An algorithm that supports only monocular vision may use monocular input; an algorithm that supports stereo may use stereo; an algorithm in a VIO table may use its complete visual-inertial pipeline.

Fairness in this benchmark therefore means consistent **run-type semantics, dataset source, ground truth, evaluation, provenance, and opportunity to run at full potential**. It does not mean reducing every algorithm to the same internal architecture or compute budget.

The benchmark is not yet rigorous enough for definitive rankings within all five tables. The most important limitations are benchmark protocol and artifact validity rather than camera calibration:

1. Some runners can leave or accept stale artifacts after a failed execution.
2. Not every run records the complete effective configuration, model, and runtime defaults.
3. Algorithms are executed under different feeding and timing regimes.
4. Output trajectory density varies from a few hundred keyframes to every input frame.
5. Current CPU, RAM, GPU, and FPS measurements are not process-isolated or directly comparable.
6. OKVIS2 and OKVIS2-X exhibit substantial run-to-run variation despite currently being classified as deterministic.
7. ORB-SLAM3 and DPVO have not yet completed clean N=5 server runs after the headless fixes.

The recommended solution is to retain the five existing run-type tables, allow every supported algorithm to use its strongest valid configuration in each table, and strengthen the controls surrounding those runs. Before the final campaign, the runners should be made transactional, provenance should be completed, and trajectory evaluation should use a common timestamp grid. Real-time and resource measurements should be supplemental analyses rather than a sixth accuracy table.

No algorithms were rerun and no files other than this report were changed during the audit.

## 1. Audit scope and interpretation

“Full potential” and “fair comparison” are compatible when fairness is defined at the run-type level:

- **Full potential** means using the strongest stable configuration the algorithm supports for that run type, with full image resolution, all applicable sensor streams, all frames, its native preprocessing, and access to the available machine resources.
- **Fair comparison** means that the run-type contract is identical, the underlying dataset and sensor measurements are consistent, ground truth and evaluation are identical, and all algorithm-specific choices are declared and reproducible.

The table defines which external capabilities are allowed. For example, `vo` excludes IMU and loop closure, while `vio-lc` allows both. Within that contract, algorithms are not required to use identical visual modalities or internal techniques. DPVO may use its native monocular input in `vo`; ORB-SLAM3 may use stereo; learned systems may use their intended pretrained networks; and each remains comparable as a complete algorithm solving the same run type. Modality and alignment differences must remain visible in the report.

An algorithm should be omitted from a run-type table when it does not genuinely support that mode. It should not be forced through an artificial fallback merely to fill every cell.

## 2. Configuration and calibration assessment

### 2.1 Camera calibration

The EuRoC configurations consistently use the published 752x480 camera model and stereo geometry:

- AirSLAM consumes raw distorted stereo images and performs its own rectification.
- ORB-SLAM3 consumes raw stereo images and builds OpenCV rectification maps internally.
- OKVIS2 and OKVIS2-X use the raw radtan camera models and EuRoC extrinsics.
- OV²SLAM retains the raw distortion model and undistorts feature coordinates internally.
- MAC-VO rectifies the stereo pair in its EuRoC data loader.
- DPVO uses cam0 only and undistorts it as a monocular stream.
- Basalt uses its calibrated double-sphere camera representation rather than the radtan parameterization used by most of the other runners.

Using different native camera models is acceptable when each model describes the same physical cameras and the algorithm performs the expected preprocessing. There is no evidence of a camera calibration mismatch that would explain the observed result differences.

### 2.2 Loop closure and sensor modes

Loop closure is explicitly disabled in the stereo VO configuration for ORB-SLAM3. AirSLAM, OKVIS2, OKVIS2-X, and OV²SLAM also select their non-loop-closing VO paths.

DPVO is monocular and up to scale. Its primary metric must therefore be Sim(3)-aligned ATE. Its SE(3) error and recovered scale may be retained as diagnostics but must not be used to rank it against metric stereo algorithms.

MAC-VO is stereo. The statement near the top of `scripts/run/run_macvo.sh` that describes it as monocular is incorrect documentation; the configured `EuRoC_NoIMU` loader consumes both cam0 and cam1.

### 2.3 Low-priority semantic mismatch

The ORB-SLAM3 EuRoC configuration states that `Camera.RGB: 0` means grayscale but currently sets the value to `1`. The input images are already one-channel grayscale, so this is effectively inert in the current path. It should still be changed to `0` for semantic correctness and to prevent surprises if the input loader changes.

## 3. Evidence from the current EuRoC VO runs

This section is evidence from the server setup gate, not an audit of every existing `vo-lc`, `vio`, `vio-lc`, or `gnss-vio` result. The following values are the server N=5 SE(3) ATE results for algorithms that completed the EuRoC VO sweep. ORB-SLAM3 and DPVO values still present in the result tree are committed reference-machine evaluations, not clean N=5 server results.

| Algorithm | MH01 median (range), m | MH03 median (range), m | MH05 median (range), m | Assessment |
|---|---:|---:|---:|---|
| Basalt | 0.080444 (0.080442–0.080445) | 0.132372 (0.131580–0.133935) | 0.186968 (0.186956–0.187006) | Full coverage and highly repeatable |
| AirSLAM | 0.108296 (0.108005–0.108417) | 0.155450 (0.154736–0.156344) | 0.224293 (0.224176–0.224434) | Processing completed; keyframe-only export is not ranking-eligible under the current coverage rule |
| OKVIS2 | 0.072975 (0.053584–0.084859) | 0.162279 (0.142656–0.282407) | 0.227585 (0.156565–0.267055) | Substantial run-to-run variation |
| OKVIS2-X | 0.062008 (0.060993–0.134430) | 0.195414 (0.144637–0.294361) | 0.244752 (0.191237–0.346956) | Substantial run-to-run variation |
| OV²SLAM | 0.053355 (0.042209–0.061688) | 0.052739 (0.043161–0.062692) | 0.107640 (0.084917–0.127784) | Full coverage; N=5 is necessary |
| MAC-VO | 0.194925 (0.190168–0.199046) | 0.327803 (0.317383–0.332614) | 0.477001 (0.469085–0.479293) | Full coverage and relatively stable |

### 3.1 Coverage and trajectory density

Basalt, OKVIS2, OKVIS2-X, OV²SLAM, and MAC-VO produced almost one pose per input frame and achieved 100% gap-aware coverage.

AirSLAM saved only its keyframe trajectory:

| Sequence | Input frames | Saved AirSLAM poses | Associated ATE pairs | Gap-aware coverage |
|---|---:|---:|---:|---:|
| MH01 | 3682 | 272 | 265 | 86.3% |
| MH03 | 2700 | 293 | 292 | 87.7% |
| MH05 | 2273 | 185 | 182 | 94.0% |

This is not evidence that AirSLAM stopped processing. Every one of the five server logs records all 3682, 2700, and 2273 input frames respectively, followed by `Average FPS`, `Map building has been stopped`, and `Map saveing done`. The final saved keyframes are also close to the sequence ends: 0.65 s short on MH01, 3.00 s short on MH03, and 0.85 s short on MH05.

The reduced coverage comes from long intervals between saved keyframes. The largest gaps are 25.30 s on MH01, 10.05 s on MH03, and 4.45 s on MH05. `_coverage.py` correctly interprets large gaps in an ordinary pose trajectory as missing coverage, but it cannot distinguish a real tracking hole from a keyframe-only exporter. AirSLAM continued processing and publishing per-frame poses during these intervals while `SaveTrajectory()` wrote only `SaveKeyframeTrajectory()`.

The committed reference machine behaved essentially the same:

| Sequence | Server poses / coverage | Reference poses / coverage | Server / reference maximum keyframe gap |
|---|---:|---:|---:|
| MH01 | 272 / 86.3% | 268 / 86.1% | 25.30 s / 25.30 s |
| MH03 | 293 / 87.7% | 294 / 88.1% | 10.05 s / 10.00 s |
| MH05 | 185 / 94.0% | 183 / 93.3% | 4.45 s / 7.00 s |

The current report generator appropriately prevents these rows from winning because the evaluated timestamps are sparse and differently distributed. That exclusion is an evaluation-format safeguard, not an AirSLAM execution-failure diagnosis. The proper fix is to export the per-frame causal trajectory for `vo` and `vio`. For `vo-lc` and `vio-lc`, the final optimized keyframe corrections must also be propagated to the per-frame poses, or every algorithm must be evaluated on a declared common resampled grid.

### 3.2 Repeatability

Basalt is effectively repeatable in this campaign. MAC-VO is also stable enough that its small spread is unlikely to alter broad conclusions.

OKVIS2 and OKVIS2-X cannot currently be treated as deterministic. The observed ranges are too wide for N=1 reporting or a fixed 10% fallback uncertainty band. Possible contributors include parallel feature detection/matching, optimizer scheduling, and internal robust-estimation choices. These should be investigated with controlled CPU affinity and thread-count A/B tests.

OV²SLAM explicitly enables randomized robust estimation through `bdo_random: 1`; N=5 reporting is appropriate unless a seed is exposed and recorded.

DPVO’s default configuration uses `CENTROID_SEL_STRAT: RANDOM`, while the demo runner does not set the seed used by upstream evaluation scripts. DPVO should also be treated as non-deterministic until repeated seeded runs demonstrate otherwise.

### 3.3 Cross-machine consistency

The cross-machine comparison provides useful evidence about the installation:

- Basalt reproduces the reference machine almost exactly.
- MAC-VO remains within a few percent of the reference values.
- AirSLAM changes more across machines and uses a GPU-specific TensorRT engine.
- OKVIS2, OKVIS2-X, and OV²SLAM show enough dispersion that a single reference run is not a reliable target.

This pattern supports the conclusion that the core installation and calibration are correct. The larger differences are associated with algorithm variability, GPU-specific execution, and sampling rather than a common setup failure.

## 4. Critical benchmark-validity issues

### 4.1 Stale-output risk

Basalt currently suppresses the executable’s return status with `|| true` and tests only whether `trajectory.txt` exists. It does not remove a previous trajectory before launching. A failed rerun in an existing result directory could therefore accept an old trajectory as a new result.

Other runners and `run_benchmark.sh` can leave old `run_eval.json` files and trajectories beside logs from a new failed attempt. This has already created an inconsistent state for the failed ORB-SLAM3 and DPVO server cells: reference evaluation artifacts coexist with new failure logs and resource files.

Every runner should use this lifecycle:

1. Resolve and validate inputs.
2. Create a temporary run directory.
3. Run the algorithm while preserving its real exit status.
4. Validate that the trajectory is new, non-empty, timestamp-monotonic, and credible.
5. Write explicit success or failure metadata.
6. Atomically replace the final run directory only after success.

A known destructor-only shutdown fault may be whitelisted only after confirming that the complete trajectory was written before the fault. It should still be recorded in metadata.

### 4.2 Incomplete provenance

The provenance helper can record a configuration hash, container image, playback rate, environment overrides, workspace state, and machine identity. However, several runners do not pass their canonical effective config variable to it:

- Basalt uses `VO_CFG` and a separate calibration file.
- AirSLAM uses both a camera config and a VO config.
- MAC-VO uses an odometry config plus a generated dataset config.
- DPVO uses calibration, default algorithm config, and model weights.
- OV²SLAM records only a config override, not its default resolved config.

Each run should record:

- All effective config paths and SHA-256 hashes.
- Model, vocabulary, and calibration hashes.
- Algorithm source commit or immutable package version.
- Docker image ID or conda environment lock hash.
- Effective defaults such as playback rate `1.0`, DPVO stride `1`, and skip `0`.
- CUDA, cuDNN, TensorRT, Torch, compiler, and relevant native-library versions.
- CPU/thread allocation and random seeds.

The current untracked `BASALT_VERSION` records `0.1.7`; this information should be incorporated into each Basalt run’s provenance rather than existing only as a workspace file.

### 4.3 Invalid resource comparison

Implementation status (2026-08-26): addressed for new runs by measurement
schema 1. Native/Conda algorithms use process-tree accounting, Docker
algorithms use container PID accounting, and hybrid pipelines combine both.
Historical whole-system samples remain legacy and are not promoted to scoped
performance metrics.

`_resource_monitor.py` reads whole-GPU memory/utilization and whole-system CPU/RAM. These values include unrelated processes, Xorg, containers, caches, and any concurrent workload. They are useful for operational monitoring but are not suitable for per-algorithm efficiency claims.

For a performance campaign, collect:

- Process-tree CPU time and peak resident memory.
- Container/cgroup CPU and memory for Docker algorithms.
- Per-PID GPU memory and utilization where the driver exposes them.
- Input frames, processed frames, output poses, dropped frames, and deadline misses.
- Initialization, processing, final optimization, and shutdown time separately.
- Model/engine compilation as a one-time setup cost rather than steady-state runtime.

### 4.4 Invalid FPS comparison

Implementation status (2026-08-26): addressed for new runs by measurement
schema 1. Processing FPS is emitted only for unpaced maximum-throughput
execution; end-to-end FPS, trajectory pose rate, and real-time factor are
stored separately. Paced and ROS transport runs leave processing FPS null.

The current `fps` field is generally `output_poses / wall_time`. This is not a common processing-rate definition:

- AirSLAM exports keyframes only.
- ORB-SLAM3 intentionally sleeps to match dataset timestamps.
- OV²SLAM receives real-time ROS messages.
- Basalt, OKVIS, DPVO, and MAC-VO run offline at their maximum available speed.
- Some algorithms may omit poses for untracked frames.

The benchmark should store distinct fields:

- `input_frames`
- `processed_frames`
- `output_poses`
- `dropped_frames`
- `processing_time_s`
- `end_to_end_time_s`
- `processing_fps`
- `trajectory_pose_rate`
- `realtime_factor`

## 5. The five existing comparison tables

The benchmark should retain its five current run-type tables. These are capability tables, not compute-normalized or camera-modality-normalized tables.

| Run type | Contract | Eligible algorithms | Primary interpretation |
|---|---|---|---|
| `vo` | Vision only; no IMU; no loop closure | Every algorithm with a genuine non-LC visual mode | Metric methods use SE(3); scale-unobservable monocular methods use Sim(3) |
| `vo-lc` | Vision only; loop closure enabled | Every algorithm with a genuine visual LC/SLAM mode | Global trajectory accuracy after the algorithm's native LC or global optimization |
| `vio` | Visual input plus IMU; no loop closure | Every algorithm with a genuine VIO mode | Metric SE(3), local drift, coverage, and failure rate |
| `vio-lc` | Visual input plus IMU; loop closure enabled | Every algorithm with a genuine visual-inertial SLAM mode | Metric SE(3), LC benefit, coverage, and failure rate |
| `gnss-vio` | Visual input, IMU, and the declared GNSS stream | Every genuine GNSS-aided visual-inertial method | Origin-aligned/global-frame ATE is primary; SE(3), scale, and local drift remain diagnostic |

Within a table, each algorithm may use:

- Its native monocular, stereo, or other supported visual input from the dataset.
- Its complete frontend, backend, learned models, robust estimation, and optimization.
- Algorithm-specific feature counts, keyframe policies, window sizes, and thread counts.
- The full server CPU, GPU, RAM, and VRAM when runs are executed serially.
- Offline/global optimization when it is part of that run type's declared output, especially `vo-lc` and `vio-lc`.

The benchmark should not impose a common feature count, common number of threads, common memory ceiling below the machine limit, or common frontend. Those restrictions would prevent some algorithms from reaching their potential. Instead, resource consumption and wall time should be measured and reported as outcomes.

Monocular and metric algorithms may remain in the same run-type table, as they currently do, but the metric must be explicit. DPVO's Sim(3) result must not be silently treated as equivalent to a stereo algorithm's SE(3) result. The table may compare complete systems while still withholding a mathematically invalid common winner between incompatible alignment classes.

OKVIS2 and OKVIS2-X should populate every existing table they genuinely support. Their IMU-disabled `vo` and `vo-lc` cells remain informative even though these are best-effort modes; their `vio` and `vio-lc` cells demonstrate the algorithms under their native visual-inertial design.

For `gnss-vio`, every algorithm in the same cell must receive the same GNSS position samples, timestamps, coordinate conversion, covariance values, and GNSS quality variant. Conventional, PPK, and other GNSS variants must remain separately labeled. An algorithm may use its native fusion architecture and tuning, but it may not receive a better GNSS source than its competitors without creating a distinct variant comparison.

### 5.1 Current run-type support matrix

The current runner design already follows the principle that algorithms appear only where they support the run type. This matrix should remain capability-driven rather than being filled by artificial fallback modes.

| Algorithm | `vo` | `vo-lc` | `vio` | `vio-lc` | `gnss-vio` |
|---|:---:|:---:|:---:|:---:|:---:|
| ORB-SLAM3 | yes | yes | yes | yes | — |
| OKVIS2 | yes | yes, experimental | yes | yes | — |
| OKVIS2-X | yes, best-effort | yes, experimental | yes | yes | yes |
| AirSLAM | yes | yes | yes | yes | — |
| Basalt | yes | — | yes | — | — |
| OV²SLAM | yes | yes | — | — | — |
| DPVO / DPV-SLAM | yes | yes | — | — | — |
| MAC-VO | yes | — | — | — | — |
| OpenVINS | — | — | yes | — | — |
| Voxel-SVIO | — | — | yes | — | — |
| MegaSaM | yes | — | — | — | — |
| MASt3R-SLAM | yes | yes | — | — | — |
| CIFASIS GNSS-SI | — | — | — | — | yes |
| VINS-Fusion+GPS | — | — | — | — | yes |
| RTAB-Map+GPS | — | — | — | — | yes |
| OpenVINS+GPS | — | — | — | — | yes |

An em dash means unsupported or not represented by a genuine current runner; it is not a failure or a penalty. DROID-SLAM is omitted because it has already been dropped from the reporting scope.

## 6. Recommended execution protocols

### 6.1 Accuracy protocol

The five main tables should be produced by an unrestricted accuracy protocol. The goal is to let each algorithm produce its best valid result for the run type without transport-induced frame loss or artificial resource limits:

1. Run only one benchmark cell at a time on an otherwise idle machine.
2. Give the active algorithm access to the full server unless its own recommended configuration deliberately uses less.
3. Disable visualizers, plots, and unrelated publishers only when they are not part of the estimator and do not change its result.
4. Keep artificial real-time enforcement disabled unless the algorithm requires it for correct operation.
5. Feed ROS-dependent algorithms slowly enough to verify zero transport-induced drops; record the effective rate.
6. Supply every sensor stream permitted by the run type and supported by the algorithm.
7. Use the same underlying dataset files, timestamps, IMU data, GNSS variant, and ground truth across a table.
8. Freeze configs, source commits, model hashes, seeds, and environment locks before launch.
9. Run N=5 for every final result unless repeatability has been formally demonstrated.

Slowing a ROS player is not a runtime-performance claim. It is an accommodation used to measure the algorithm’s achievable accuracy without transport-induced frame loss.

### 6.2 Supplemental real-time protocol

Real-time behavior should be measured independently from the five main accuracy tables:

1. Feed every algorithm at EuRoC’s 20 Hz rate.
2. Let the algorithm use the full server, as in the accuracy campaign.
3. Do not run cells concurrently.
4. Record end-to-end latency, internal processing time, queue depth, dropped frames, and tracking failures.
5. Define the deadline and failure criterion before the campaign.
6. Report accuracy only for the portion processed under the real-time constraint, with coverage beside it.

This supplemental analysis must not replace or constrain the five run-type accuracy tables. ORB-SLAM3’s EuRoC executable sleeps between frames to reproduce dataset timing. That behavior is appropriate for the real-time analysis but makes its current wall-clock FPS unsuitable for an offline throughput comparison. A separate no-sleep executable or internal tracking-time metric is needed for offline throughput.

## 7. Evaluation protocol improvements

### 7.1 Common-grid evaluation

The evaluator currently associates ground truth at each algorithm’s output timestamps. This means dense and sparse algorithms weight the path differently.

For the final comparison:

1. Define a common evaluation timestamp grid, for example the camera frame timestamps.
2. Interpolate estimated pose only between nearby valid estimates.
3. Do not interpolate across tracking gaps larger than a declared threshold.
4. Evaluate every algorithm on the common valid grid.
5. Require at least 95% common-grid coverage for ranking.
6. Report the number of evaluated timestamps and excluded gaps.

If AirSLAM can export its full per-frame pose stream, that is preferable to reconstructing a dense trajectory from keyframes. Its current implementation calls `SaveKeyframeTrajectory`, even though frame poses are also published through ROS.

### 7.2 Metrics

The existing evaluator already provides the essential foundations:

- SE(3)-aligned ATE for metric stereo/VIO methods.
- Sim(3)-aligned ATE for monocular methods.
- Tight timestamp association through interpolated ground truth.
- Scale diagnostics.
- Scale-unadjusted relative drift metrics.
- Gap-aware coverage.

Final reports should include, at minimum:

- Median ATE and min–max across runs.
- Fixed-distance translational and rotational RPE.
- Coverage and associated-pair count.
- Failure/initialization rate.
- Scale factor for diagnostic purposes.
- End-of-run drift.
- Origin-aligned/global-frame ATE for `gnss-vio`.
- Real-time deadline performance only in the supplemental real-time analysis.

ATE should never be published without coverage. An accurate estimate of a short or selectively sampled subpath is not equivalent to completing the sequence.

### 7.3 Randomness and repeats

Use a predetermined seed list, such as five fixed seeds, where the algorithm exposes seed control. Record the seed in `run_meta.json`.

Where deterministic control is unavailable, run at least N=5 and report median, minimum, and maximum. Do not label OKVIS2, OKVIS2-X, OV²SLAM, or DPVO deterministic until repeated evidence supports that classification.

Thread control should not arbitrarily handicap an algorithm. Final accuracy runs should give the active algorithm access to the full server and let its strongest stable configuration choose the effective thread count. CPU affinity or a single-thread A/B is useful for diagnosing OKVIS repeatability, but it should not automatically become the final full-performance setting. The actual allocation and utilization must be recorded so performance cost remains visible.

## 8. Per-algorithm recommendations

### 8.1 Basalt

Current status:

- Correct stereo VO mode with IMU disabled.
- Full output coverage.
- Exceptional N=5 repeatability.
- Offline maximum-speed execution with all available threads.

Recommendations:

1. Keep the current configuration as the initial frozen baseline.
2. Remove stale trajectories before execution and stop suppressing the executable’s status.
3. Record both VO config and camera-calibration hashes.
4. Record Basalt version/source and the effective thread/core allocation.
5. Add a separate VIO result to demonstrate full native capability.

### 8.2 AirSLAM

Current status:

- Raw stereo calibration is coherent.
- SuperPoint and LightGlue are enabled with a maximum of 400 keypoints.
- TensorRT execution is hardware-specific.
- All input frames are processed, but only keyframe poses are saved; the gap-aware evaluator therefore reports less than 95% pose coverage on all three sequences.

Recommendations:

1. Save the full frame-pose trajectory or record the published frame-pose topic for `vo` and `vio`.
2. Rebuild, hash, and record the TensorRT engine on every GPU model.
3. Disable unnecessary ROS publication and visualization in a validation A/B.
4. For `vo-lc` and `vio-lc`, propagate optimized keyframe corrections to the dense frame trajectory or use the common-grid evaluation policy.
5. On held-out validation data, test whether a higher keypoint limit improves accuracy and robustness without unacceptable runtime cost; do not tune merely to game keyframe-density coverage.
6. Keep results in their appropriate existing `vo`, `vo-lc`, `vio`, and `vio-lc` tables.

### 8.3 OKVIS2

Current status:

- Correct EuRoC calibration and no-loop-closure VO configuration.
- IMU disabled in VO.
- Frontend uses up to 700 keypoints and four matching threads.
- Real-time enforcement is disabled.
- Wide N=5 dispersion despite full coverage.

Recommendations:

1. Treat VO as best-effort and add the native VIO track.
2. Run a repeatability diagnostic using fixed CPU affinity.
3. A/B the current four matching threads against a controlled thread configuration.
4. Inspect whether feature detection, matching, or robust estimation offers seed control.
5. Retain N=5 in final tables unless repeatability is proven.
6. Do not use final BA in the causal VO track; reserve final/global optimization for the appropriate SLAM track.

### 8.4 OKVIS2-X

Current status:

- Camera and estimator settings match the OKVIS2 comparison closely.
- IMU disabled and submapping disabled in VO.
- Full coverage but substantial N=5 dispersion.

Recommendations:

1. Apply the same repeatability diagnostics as OKVIS2.
2. Add a native VIO evaluation.
3. Keep submapping or mapping enhancements in a separately named configuration if they change the estimator’s scope.
4. Retain N=5 and report the complete range.

### 8.5 ORB-SLAM3

Current status:

- Uses the official EuRoC-style stereo calibration.
- Loop closure is explicitly disabled for VO.
- Uses 1200 ORB features, eight pyramid levels, and standard FAST thresholds.
- The runner now supplies a virtual X display on a headless server.
- The EuRoC executable sleeps to match frame timing.
- A clean N=5 post-fix server result is still required.

Recommendations:

1. Complete a clean N=5 server run before drawing conclusions.
2. Correct `Camera.RGB` to `0` for grayscale semantic consistency.
3. On held-out validation data, test `nFeatures` values such as 1200, 1600, and 2000, then freeze one profile.
4. Use the current paced executable in the real-time campaign.
5. Use a no-sleep build or internal tracking-time statistics for offline throughput.
6. Add separate stereo-inertial and loop-closed tracks.

### 8.6 OV²SLAM

Current status:

- Coherent raw stereo camera model.
- Vision-only, loop closure disabled.
- CLAHE and KLT tracking enabled.
- Random robust estimation enabled.
- Full trajectory coverage.
- Data is supplied through a ROS player at a default rate of 1.0x.

Recommendations:

1. Use 0.5x playback for the accuracy campaign and 1.0x for real-time evaluation.
2. Always record the effective rate, including the default.
3. Expose and record a robust-estimation seed if practical.
4. Otherwise retain N=5 and report dispersion.
5. Count messages published, received, processed, and dropped.
6. Fix the shutdown-thread fault separately; do not discard valid complete trajectories solely because the process aborts after saving them.

### 8.7 DPVO

Current status:

- Monocular cam0 input.
- Stride 1 and skip 0 are suitable for the accuracy comparison.
- The default high-accuracy configuration uses 96 patches per frame and mixed precision.
- Centroid selection is randomized, but the demo runner does not set a seed.
- The correct model hash is available.
- A clean N=5 post-fix server result is still required.

Recommendations:

1. Add a fixed, recorded seed list and run N=5.
2. Record algorithm config, calibration, model hash, source commit, Torch/CUDA versions, stride, and skip.
3. Rank DPVO only by Sim(3) metrics in the monocular table.
4. On held-out validation data, optionally test larger patch and optimization-window budgets within the 24 GB VRAM limit.
5. Publish upstream-default and tuned profiles separately.
6. Do not fine-tune the network on final test sequences.

### 8.8 MAC-VO

Current status:

- Stereo EuRoC loader with native stereo rectification.
- Uses the upstream `MACVO_Performant` configuration.
- Full output coverage and relatively small N=5 dispersion.
- The configuration uses FP32 tensors but enables TF32/medium matmul precision internally.
- The runner unnecessarily enables the Rerun viewer through `--useRR`.

Recommendations:

1. Correct the runner documentation to identify MAC-VO as stereo.
2. Remove `--useRR` from benchmark runs.
3. Record both odometry and generated dataset config hashes plus the model hash.
4. Fail if the trajectory length does not match the expected input mapping rather than silently truncating timestamp assignment.
5. Report `Paper_Reproduce` and `MACVO_Performant` as separately named profiles.
6. Optionally A/B TF32 versus highest FP32 matmul precision on held-out validation data.

## 9. Parameter-tuning policy

Parameter tuning is allowed and desirable when the objective is to show each algorithm at its full potential. Fairness does not require identical parameter values or identical computational complexity. It requires a common tuning policy, declared search space, reproducible selection procedure, and no use of final test ground truth for configuration selection. Tuning directly on MH01, MH03, and MH05 and then reporting those same sequences as unseen tests would bias the comparison.

Use one of these defensible policies:

1. **Official-config policy:** use upstream/default dataset configurations without local accuracy tuning.
2. **Held-out validation policy:** choose parameters on separate sequences or a declared validation split, freeze them, and evaluate once on the test split.
3. **Nested evaluation policy:** rotate the held-out sequence and aggregate results, at substantially higher computational cost.

For learned algorithms, dataset adaptation may be used if it is part of the intended full-potential experiment, but it must be declared. Pretrained and adapted variants should be labeled separately, with their training data, initialization, and training compute documented. An adapted model must not train on the final evaluation trajectories or their ground truth.

Do not select the best seed or best run. Use predetermined seeds and aggregate all valid planned runs. Retries should be governed by a written failure policy, and both the original failure and retry should remain auditable.

## 10. Recommended implementation and campaign order

### Phase A: runner correctness

1. Add temporary run directories and atomic promotion.
2. Remove stale outputs before launch.
3. Preserve executable exit status.
4. Validate new trajectory timestamps, pose count, coverage, and freshness.
5. Write explicit failed-run metadata.

### Phase B: provenance and measurements

1. Record all configs, models, versions, commits, defaults, and seeds.
2. Replace whole-system resource fields for performance claims.
3. Split input count, output pose count, internal processing time, and end-to-end duration.
4. Record effective playback and real-time policy.

### Phase C: repeatability gate

1. Run all eight algorithms N=5 on MH01 with the server idle.
2. Confirm full coverage and consistent input counts.
3. Investigate algorithms with material dispersion.
4. Update deterministic/non-deterministic classifications from evidence.

### Phase D: validation-only tuning

1. Test only the small, declared parameter families described in this report.
2. Freeze the selected profiles before final test runs.
3. Keep upstream-default and tuned profiles separately identifiable.

### Phase E: final campaigns

1. Run the unrestricted accuracy protocol serially for every supported algorithm/run-type cell.
2. Regenerate the five existing `vo`, `vo-lc`, `vio`, `vio-lc`, and `gnss-vio` tables.
3. Verify that unsupported cells remain explicitly absent rather than being routed through a weaker substitute mode.
4. Run the supplemental real-time protocol independently where real-time behavior is in scope.
5. Generate supplemental robustness and efficiency tables without replacing the five accuracy tables.
6. Publish configs, hashes, seeds, failures, and complete N=5 distributions.

## 11. Final assessment

The algorithms are installed well enough to continue, and the common EuRoC calibration is not the limiting problem. Basalt and MAC-VO already provide strong evidence that the server can reproduce stable results. The most urgent issues are stale-artifact handling, incomplete provenance, sparse trajectory evaluation, mixed timing regimes, and unsupported deterministic assumptions.

Fixing those items will make the comparison fairer and may also improve measured accuracy by eliminating frame loss, viewer overhead, configuration ambiguity, and selective trajectory sampling. Algorithm-specific tuning should follow after those controls are in place and should be encouraged under a declared validation policy. The strongest valid algorithm configuration should then be used in every run type it supports, with results reported through the repository's existing five tables: `vo`, `vo-lc`, `vio`, `vio-lc`, and `gnss-vio`.

## Relevant repository references

- `scripts/run/run_basalt.sh`
- `scripts/run/run_airslam.sh`
- `scripts/run/run_okvis2.sh`
- `scripts/run/run_okvis2x.sh`
- `scripts/run/run_orbslam3.sh`
- `scripts/run/run_ov2slam.sh`
- `scripts/run/run_dpvo.sh`
- `scripts/run/run_macvo.sh`
- `scripts/run/_resource_monitor.py`
- `scripts/run/_enrich_run_meta.py`
- `scripts/eval/_evaluate_run.py`
- `scripts/eval/_coverage.py`
- `scripts/eval/make_report_tables.py`
- `configs/basalt/vo_config.json`
- `configs/airslam/euroc_mav_vo.yaml`
- `configs/okvis2/euroc_mav_MH_01_easy_vo.yaml`
- `configs/okvis2x/euroc_mav_MH_01_easy_vo.yaml`
- `configs/orbslam3/euroc_mav_stereo.yaml`
- `configs/ov2slam/euroc_mav_vo.yaml`
- `configs/dpvo/euroc_mav.txt`
- `src/DPVO/config/default.yaml`
- `src/MAC-VO/Config/Experiment/MACVO/MACVO_Performant.yaml`
