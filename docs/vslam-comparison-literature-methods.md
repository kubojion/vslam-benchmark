# How VSLAM comparison papers configure and evaluate algorithms

## Purpose

This report reviews comparison papers that are methodologically relevant to the
agricultural VSLAM benchmark in this repository. The focus is not which algorithm
won each paper, but how the authors handled:

- algorithm configuration and tuning;
- dataset-specific calibration and modality choices;
- computational limits and input delivery;
- repeated runs and nondeterminism;
- initialization failures and incomplete trajectories;
- trajectory alignment and aggregate metrics;
- reproducibility of software and configurations.

The benchmark in this repository is a quality-only comparison. It uses five
capability groups (`vo`, `vo-lc`, `vio`, `vio-lc`, and `gnss-vio`) and seeks one
algorithm configuration that works across all applicable datasets. It does not
seek a real-time-versus-quality Pareto frontier.

## Executive conclusion

The literature uses four broad approaches:

1. **Author-recommended settings fixed across all trials.** Delmerico and
   Scaramuzza asked algorithm authors for suitable general-purpose settings and
   retained them across sequences. Bujanca et al. used parameters from original
   papers or repositories, falling back to defaults. Merzlyakov and Macenski used
   author-provided settings that reproduced published results. This is the best
   match for the present benchmark.
2. **Empirical tuning for the evaluation environment.** Schmidt et al. tuned
   frontend feature extraction for unstructured outdoor data. Cremona et al.
   tuned each method for their agricultural data and changed some IMU noise
   parameters substantially. This can improve absolute results, but without a
   held-out tuning set it entangles algorithm quality with evaluator effort and
   knowledge of the test data.
3. **Defaults plus necessary sensor or mode adaptation.** Hroob et al. mostly
   retained defaults while changing camera parameters, disabling unavailable
   GNSS, or selecting a launch mode. This is simple, but defaults may not
   represent every algorithm's attainable quality.
4. **Explicit parameter design-space search.** SLAMBench2 exposes parameters and
   searches accuracy, speed, memory, and energy trade-offs. This is appropriate
   when the Pareto frontier is itself the research question. It is excessive and
   difficult to make equally thorough for a quality-only comparison of many
   heterogeneous systems.

No reviewed paper supplies a perfect solution. The most defensible synthesis for
this repository is:

- use a documented author-recommended **quality profile** for each algorithm;
- freeze that profile across datasets and sequences;
- keep dataset-specific sensor calibration, timing, masks, vocabulary paths,
  and modality wiring in a separate **sensor profile**;
- process every input without algorithm-induced frame dropping;
- report all planned runs, their success/coverage, and median accuracy rather
  than selecting the best successful run;
- treat initialization failure, tracking loss, and incomplete output as results,
  not as trials to silently discard.

This gives every algorithm access to its intended capabilities without tuning it
against the final benchmark trajectories.

## Comparison of relevant papers

| Study | Configuration policy | Execution and repetitions | Failures and metrics | Lesson for this benchmark |
|---|---|---|---|---|
| [Delmerico and Scaramuzza, 2018](https://rpg.ifi.uzh.ch/docs/ICRA18_Delmerico.pdf) | Algorithm authors supplied manually tuned, general flying-robot settings; these were maintained across trials. Some feature/window limits were reduced for the onboard platform. | Real-time playback; compiler optimization and SIMD enabled; timing and resource use measured. | Failed initialization was restarted and the first successful run was used. Sim(3)-aligned RMSE and fixed-distance odometric error were reported. | Strong precedent for author-derived, cross-dataset fixed settings. Do not copy the successful-restart selection or compute-driven quality reductions. |
| [Bujanca et al., 2021](https://arxiv.org/pdf/2109.13160) ([project](https://robustslam.github.io/evaluation/)) | Hyperparameters followed original papers/repositories, otherwise defaults. Common dependencies and optimized builds were used where possible. | Ten runs per algorithm/sequence on each of three platforms. Inputs were delivered only after the previous frame completed, preventing algorithm-induced drops. | Median translational ATE-RMSE over ten runs, normalized by path length; continuous error and Correct Rate of Tracking; crashes and inconsistency retained. | Strongest template for a quality-only protocol: fixed provenance, offline/backpressured input, repeated runs, median result, and coverage beside accuracy. |
| [Cremona, Comelli, and Pire, 2022](https://arxiv.org/pdf/2206.05066) ([repository](https://github.com/CIFASIS/slam_agricultural_evaluation)) | Each VIO method was tuned “up to a feasible point”; some IMU noise values were raised by one or two orders of magnitude. Stereo-inertial mode was preferred when available. | Same workstation, Docker isolation, ROS wrappers, and multiple executions. Dataset intervals were adjusted to accommodate stationary initialization. | ATE with Umeyama alignment. The minimum error among repeated runs was reported; the repeat count was not specified in the paper. | Highly relevant agricultural precedent, but best-run selection and test-environment tuning are optimistic. Retain all repetitions and avoid changing final sequences for an algorithm. |
| [Schmidt et al., 2024 (revised 2025)](https://arxiv.org/pdf/2408.01716) ([repository](https://github.com/iis-esslingen/vi-slam_lc_benchmark)) | Frontend feature extraction was empirically tuned because outdoor conditions differed from defaults. Loop closure and input frame rate were controlled explicitly. | Containerized methods on one specified workstation; evaluations at 30, 15, and 5 FPS; loop closure enabled/disabled. | Accuracy, processing time, and resource use; missing output or error above 100 m marked as failure. Unsupported/unreliable modes were excluded or constrained. | Closest modern unstructured-outdoor benchmark and good precedent for explicit capability modes. Its empirical tuning is less defensible without a stated held-out tuning protocol. |
| [Merzlyakov and Macenski, 2021](https://arxiv.org/pdf/2107.07589) | Recommended release builds and author-provided tuned settings that reproduced earlier results; only online optimization, without postprocessing. | Ten executions per sequence on the same PC/OS. Methods were grouped by supported modality. | Mean and standard deviation of RMSE plus crashes, early termination, tracking loss, and runtime. Alignment matched observability: Sim(3) monocular, SE(3) stereo/RGB-D, and 4-DoF visual-inertial. | Good precedent for author provenance, repetition, modality grouping, and observability-aware alignment. Median is preferable to mean for occasional catastrophic SLAM failures. |
| [Bodin et al., 2018, SLAMBench2](https://arxiv.org/pdf/1808.06820) | Parameters are exposed through a common framework and can be automatically explored. The work demonstrates that defaults need not lie on the speed/accuracy Pareto frontier. | Unified dataset I/O, API, and measurements across platforms; accuracy, frame rate, memory, and energy are jointly evaluated. | Multi-objective Pareto analysis rather than one prescribed quality configuration. | Valuable when studying tuning trade-offs. A comprehensive search is not necessary here because this campaign has no real-time objective and cannot guarantee equally exhaustive search spaces across algorithms. |
| [Hroob et al., 2021](https://arxiv.org/pdf/2107.05283) | Mostly default configurations, with camera parameters adapted, unavailable GNSS disabled, and selected launch/mapping modes. | Four algorithms on simulated vineyard scenarios; no repeated-run protocol is stated. | EVO ATE statistics including maximum, mean, median, RMSE, and standard deviation. | Shows the importance of separating required sensor/mode adaptation from algorithm tuning. Cross-modality comparisons and apparent single runs limit the conclusions. |
| [Sharafutdinov et al., 2023](https://arxiv.org/pdf/2108.01654) | Practical setup based on available repositories, ROS integration, and reproducible containers; exact tuning and repetition policy is less explicit. | Same platform across many methods and datasets, with Docker/ROS wrappers. | Failed cases are shown rather than removed; the paper emphasizes deployment and reproducibility problems. | Useful evidence that dependency/version reproducibility is part of comparison validity, but not a sufficiently precise configuration-selection protocol by itself. |

## Detailed findings

### 1. Author-derived configurations are a recognized alternative to parameter sweeps

Delmerico and Scaramuzza explicitly involved the authors of each evaluated
algorithm to obtain manual settings suitable for general flying robots. Their
reasoning is particularly applicable here: a deployed system cannot perform an
offline parameter search for every new environment, so its configuration should
generalize. They kept those settings across all trials.

Bujanca et al. use a more scalable version of the same policy: follow the
original paper or repository and use defaults when no recommendation exists.
Merzlyakov and Macenski additionally checked that supplied parameters reproduced
previously reported behavior.

This supports the current author-quality-config audit. It does not guarantee
that every author's configuration is globally optimal, but it gives an
auditable and algorithm-neutral selection rule. A broad evaluator-designed sweep
would instead favor methods with small, familiar, or inexpensive search spaces.

### 2. Per-environment tuning is common, but it answers a different question

The closest outdoor benchmark, Schmidt et al., states that conditions differed
from algorithm defaults and therefore empirically tunes frontend feature
extraction. The agricultural comparison by Cremona et al. similarly tunes each
method to a feasible point and changes sensitive IMU noise values.

Those studies ask, approximately, “how well can an experienced evaluator make
these systems work here?” The proposed benchmark asks, “how well does a
documented, generally applicable quality configuration transfer across
agricultural datasets?” Both are legitimate, but their results should not be
presented as the same experiment.

If any future tuning is performed, it should use development data disjoint from
the final evaluation sequences, a declared objective, a fixed budget per
algorithm, and a frozen choice before final runs. Otherwise knowledge of the
test trajectories leaks into the configuration.

### 3. Calibration is not tuning

Several studies necessarily adapt camera calibration, IMU parameters, input
topics, and supported sensor modes. SLAMBench2 also demonstrates that blindly
reusing raw parameter values across datasets can be invalid. These adaptations
must not be confused with selecting algorithmic behavior to improve a score.

For this repository:

- **Sensor profile:** image dimensions, camera model and intrinsics, stereo
  extrinsics/baseline, camera–IMU transform, IMU rate/noise values derived from
  sensor calibration, timestamps, masks for vehicle-fixed occlusions, GNSS
  frame/covariance, and input paths/topics. This may vary by dataset or sensor.
- **Algorithm quality profile:** feature counts and thresholds, pyramid levels,
  keyframe policy, optimization windows/iterations, loop detection thresholds,
  backend settings, map limits, and learned-model inference settings. This stays
  fixed across all applicable datasets.
- **Capability mode:** visual versus visual-inertial, loop closure off/on, GNSS
  off/on. These are compared in the existing five separate tables, rather than
  mixed into a single ranking.

Changing an algorithm parameter because one evaluation trajectory scores poorly
is tuning even if the parameter happens to have “camera”, “noise”, or “feature”
in its name. Every variable therefore needs a recorded source and classification.

### 4. Quality-only execution should use backpressure, not frame dropping

Bujanca et al. feed a new frame only after the previous one is processed. This
separates algorithmic estimation quality from the speed of the evaluation
machine. It is the most appropriate precedent for this benchmark because the
paper does not include a real-time campaign.

All methods should receive the full ordered sensor stream. Recorded timestamps
and IMU-image synchronization must remain unchanged, but the runner may wait for
the algorithm rather than dropping queued inputs. Thread counts, GPU visibility,
and memory must not be artificially restricted unless a common resource-limit
experiment is later added as a separate study. Runtime and peak resource use can
still be recorded as descriptive secondary outputs.

### 5. Repetition policy materially changes the claimed result

Bujanca et al. and Merzlyakov and Macenski each use ten executions per sequence.
Cremona et al. use multiple executions but publish the minimum error. Delmerico
and Scaramuzza restart failed initialization and take the first successful run.
The latter two policies discard evidence about practical reliability and produce
optimistic estimates.

For the present campaign:

1. Declare the planned number of runs before looking at results. The existing
   `N=5` plan is a reasonable resource-aware minimum across the full matrix; ten
   runs is the stronger literature precedent when feasible.
2. Use fixed, recorded seeds where the algorithm exposes them. A fixed seed makes
   a run reproducible; different predetermined seeds across repetitions measure
   stochastic variability.
3. Report the median accuracy across all valid runs, dispersion (interquartile
   range or min–max), and the success fraction `successful/planned`.
4. Never replace a failed planned run with an extra successful run. Diagnostic
   reruns may be made, but must be labeled and excluded from the primary
   aggregate unless the entire protocol is restarted for all methods.
5. Do not publish the minimum/best run as the headline result.

### 6. Accuracy requires a coverage or tracking-completeness metric

ATE computed only on the trajectory portion that an algorithm produced can make
an early failure look deceptively accurate. Bujanca et al.'s Correct Rate of
Tracking directly addresses this. Other papers explicitly mark tracking loss,
crashes, missing output, or extreme errors.

Each result here should therefore include at least:

- run status (`success`, `initialization_failure`, `tracking_lost`, `crash`,
  `timeout`, `invalid_output`);
- estimated duration or frames divided by the evaluable reference duration or
  frames;
- start and end time offsets relative to the common evaluation interval;
- ATE/RPE only when the minimum overlap requirement is met;
- success fraction across repetitions.

An algorithm that completes 60% of a sequence should not be ranked solely by
the ATE of that 60%. The partial metric can be retained for diagnosis, while the
table identifies it as incomplete.

### 7. Alignment must follow what each mode can observe

Merzlyakov and Macenski distinguish Sim(3), SE(3), and 4-DoF alignment based on
sensor modality. A single alignment rule for every table can either penalize an
unobservable degree of freedom or remove an error that a sensor-fusion system is
expected to estimate.

The evaluation should declare alignment per capability group before the final
run:

- monocular visual-only trajectories generally require Sim(3) unless scale is
  otherwise provided;
- stereo/RGB-D visual-only trajectories generally use SE(3);
- visual-inertial trajectories have metric scale and should not receive Sim(3)
  scale correction; an alignment consistent with gravity observability should
  be used and documented;
- GNSS-aided trajectories should additionally be assessed in the global frame
  without a free post-hoc transform that removes the global-position error the
  method is intended to estimate.

The exact primary and supplementary alignment metrics should be identical for
all algorithms within a table.

## Recommended protocol for this repository

### Configuration selection

1. Back up the current configurations and record their hashes.
2. For every algorithm, select one quality-oriented configuration using this
   evidence order:
   1. official configuration for the same sensor mode and closest environment;
   2. settings stated in the original paper or official supplementary material;
   3. official general/default configuration;
   4. current repository configuration when no better primary source exists.
3. Record the source URL, upstream commit/tag, copied parameters, deliberate
   deviations, and rationale in the configuration audit.
4. Allow only sensor-profile values to vary by dataset.
5. Freeze algorithm profiles before the final evaluation and verify their hashes
   in every run manifest.

### Execution

1. Run a correctness smoke test on development sequences. Fix integration bugs,
   invalid calibration conversion, broken model paths, and unsupported input
   wiring without optimizing benchmark scores.
2. Deliver the complete data stream with backpressure and no real-time frame
   dropping.
3. Give algorithms the hardware they can normally use. Do not equalize them by
   disabling threads, CUDA, loop closure, or supported sensors; instead compare
   like capability modes in the five existing tables.
4. Use a predefined run count and seeds. Run methods in a shuffled or balanced
   order if thermal or shared-machine state may matter.
5. Save exact repository/submodule commits, container image digest, model-file
   hashes, resolved configuration, command, seed, and environment alongside each
   result.

### Reporting

For every algorithm–dataset pair, report:

- median primary error and dispersion over the planned runs;
- completed trajectory fraction and successful/planned runs;
- all failure categories;
- secondary trajectory metrics using the predeclared alignment policy;
- runtime and resource use as descriptive information, not as an admission gate;
- whether the output used loop closure, IMU, GNSS, or learned weights.

CSV summaries should remain tracked in Git so a clone contains the comparison.
Large trajectories, logs, images, maps, and plots can remain in the gitignored
results store, referenced by the existing manifest design.

## How this differs from the reviewed work

The proposed protocol combines the strongest elements found in the literature:

- author-derived, fixed settings from Delmerico and Scaramuzza, Bujanca et al.,
  and Merzlyakov and Macenski;
- full-stream, non-dropping quality evaluation and robust aggregation from
  Bujanca et al.;
- explicit loop-closure/capability separation from Schmidt et al.;
- agricultural sensor awareness and containerized reproducibility from Cremona
  et al.;
- explicit parameter and provenance management emphasized by SLAMBench2.

It is stricter than several precedents because it does not tune on final
sequences, report the best repeat, retry until success, or hide incomplete
trajectories. It also improves interpretability by preserving the five capability
tables rather than combining systems that receive materially different sensor or
loop-closure information.

The result is not a claim that every method has been individually optimized for
every field. It is a stronger and more transferable claim: each method is run in
a reproducible, author-supported quality configuration, receives every supported
input and available compute resource, and is evaluated consistently across all
applicable agricultural data.

## Primary sources

- Delmerico, J., and Scaramuzza, D. (2018), [A Benchmark Comparison of Monocular
  Visual-Inertial Odometry Algorithms for Flying Robots](https://rpg.ifi.uzh.ch/docs/ICRA18_Delmerico.pdf).
- Bujanca, M. et al. (2021), [Robust SLAM Systems: Are We There
  Yet?](https://arxiv.org/pdf/2109.13160), with the [official evaluation
  site](https://robustslam.github.io/evaluation/).
- Cremona, L., Comelli, R., and Pire, T. (2022), [Experimental Evaluation of
  Visual-Inertial Odometry Systems for Arable
  Farming](https://arxiv.org/pdf/2206.05066), with the [official benchmark
  repository](https://github.com/CIFASIS/slam_agricultural_evaluation).
- Schmidt, M. et al. (2024; revised 2025), [Visual-Inertial SLAM for Unstructured Outdoor
  Environments: Benchmarking the Benefits and Computational Costs of Loop
  Closing](https://arxiv.org/pdf/2408.01716), with the [official benchmark
  repository](https://github.com/iis-esslingen/vi-slam_lc_benchmark).
- Merzlyakov, A., and Macenski, S. (2021), [A Comparison of Modern
  General-Purpose Visual SLAM Approaches](https://arxiv.org/pdf/2107.07589).
- Bodin, B. et al. (2018), [SLAMBench2: Multi-Objective Head-to-Head Benchmarking
  for Visual SLAM](https://arxiv.org/pdf/1808.06820).
- Hroob, D. et al. (2021), [Benchmark of Visual and 3D Lidar SLAM Systems in
  Simulation Environment for Vineyards](https://arxiv.org/pdf/2107.05283).
- Sharafutdinov, D. et al. (2023), [Comparison of Modern Open-Source Visual SLAM
  Approaches](https://arxiv.org/pdf/2108.01654).
