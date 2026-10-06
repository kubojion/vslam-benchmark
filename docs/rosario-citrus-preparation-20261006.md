# Rosario Option A and Citrus Rule C preparation, 6 October 2026

This implements `benchmark-decisions-20261006.md`. No estimator, pilot, image build,
repetition launcher or future campaign was executed during preparation. Native
loading/delivery and independent readiness review remain gates before production.

## Configuration and regeneration

`configs/sensors/imu-noise-rule-20261006.json` extends the original immutable rule
with hash-pinned Rosario and Citrus Allan sources. Author ratios remain defined
once, in the original rule. Four continuous-time sigmas are transferred separately;
no extra sample-rate conversion is applied. EuRoC/ZED activation and Horti values
and rule receipts retain their earlier behaviour.

Use `scripts/setup/prepare_rule_c_20261006.py --dataset rosariov2 --dataset citrusfarm`
with the macvo Python environment to reproduce configuration changes from the
reviewed existing configs. This command never executes an estimator. It preserves
non-sensor algorithm settings, Citrus visual configs and GNSS configs. The Citrus
builder now defaults to this noise-only update; its historical envelope template
recipe requires explicit `--noise-policy legacy-envelope --envelope FILE` and
must only be used in an isolated historical reconstruction.

## Rosario input version

`scripts/setup/_rosario_rectified.py` computes the common camera geometry from the
hash-pinned stereo-IMU Kalibr bundle. The frozen derived record is
`configs/sensors/rosario-rectification-20261006.json`.

`scripts/data/prepare_rosario_option_a.py prepare --sequence sequence1 --sequence sequence5`
creates `.profiles/rosario-kalibr-rectified-ruleC-20261006` under the Rosario dataset.
It uses OpenCV 4.11.0, alpha=-1, CALIB_ZERO_DISPARITY, 1280x720, bilinear
interpolation, constant-zero borders and PNG compression 3. No crop or resize is
introduced. Both cameras share K′, zero distortion and baseline 0.05024089082502646 m.
The native camera-IMU poses are composed with each rectification rotation.

The IMU CSV timestamps are shifted once by -4,098,308 ns; sample value bytes and
camera timestamps are preserved. The alternate `imu.csv` is rebuilt from the same
integer stamps and measurement strings, correcting its legacy float-second
representation without changing measurements. Fixed native offsets are zero;
OpenVINS retains online residual time estimation. The right-minus-left Kalibr
offset (12.583 microseconds) is recorded; camera pairing stays unchanged.

`activate` retains original inputs in `.profiles/original-20261006`, leaves the
canonical sequence directories and tracked reference/timing bytes in place, and
selects the derived image/IMU files using relative symlinks. Both existing `/ws`
and `/datasets` mounts therefore resolve them. Per-file original and derived
SHA-256 records are in each derived `manifest.json`. Re-preparation or activation
on an already prepared version is refused. `verify` checks both copies and the
exact IMU shift. Bulk versions/manifests are deliberately outside Git; the source
calibration, generator and frozen geometry are tracked.

These selected inputs apply only to VO/VIO/VO-LC/VIO-LC. Original GNSS recipes are
unchanged and must not consume this new profile. Input capture rejects GNSS modes
on Option A; GNSS work must explicitly select its reviewed original inputs later.

## Saved-output interpretation

Input capture creates a compact `provenance/rosario-input-profile.json` before
estimation, tied to the captured input digest. Metadata enrichment snapshots it
under the `rosario_input_profile` artifact role. Evaluation uses that saved marker,
never the current dataset/config to reinterpret historical runs.

Camera or virtual-body exports are converted from rectified axes back to the
original left-camera axes. Inertial body exports already use the unchanged,
independently recorded physical reference transform, so they receive no second
rotation. The physical reference file is unchanged. Historical frame policies
and numerical results are regression-checked; new evaluation provenance naturally
has a new evaluator code hash and evaluation timestamp. Existing evaluation files
are not overwritten.

## OpenVINS delivery

`multi_threading_subs: false` is explicit in Rosario, preserving the previous
default and joined-thread path. Native code is unchanged. The player preserves
replay speed, scheduling and QoS and adds `openvins_delivery.json` for Rosario and
Citrus. It records publisher counts, startup subscribers, scheduling lateness,
event processing duration (image decoding plus publication) and camera-update/propagated output counts. These are not proof
of internal IMU receipt. Existing poseimu sidecars remain separate from odomimu.

`scripts/analysis/openvins_delivery_audit.py RUN_DIRECTORY` combines the sidecar
with completed native camera-callback TIME lines. Native printed lag must be
multiplied by ten because the inspected source converts seconds with 100 instead
of 1000. No ATE enters delivery assessment. Slower playback is not selected here.
Full-length checks on both Rosario sequences remain required before broad N=1.
The pinned runner disables native full-state history; camera-update timestamps
include online residual time offset. Do not claim that the poseimu sidecar alone
provides per-update calibration history or exact camera receipt counts.

## Handoff boundaries

Per-dataset readiness pins are intentionally stale after these changes. Refresh
only reviewed Rosario/Citrus prerequisites after independent review; do not use old
execution manifests. `build_execution_assets.py --inputs --dataset rosariov2 --refresh`
now supports a genuinely scoped input refresh. Preparation does not execute it or
refresh review JSONs. Current implementation captures also need review/refresh
because shared Python helpers changed, although protected runners/configs did not.

Native preflight must confirm loaded camera/noise/time values, source/input/runtime
identity, initial IMU support, delivery/draining and LC export/shutdown. Setup
correctness is the gate; initialization failure or poor ATE under a verified Rule C
setup is an outcome. A shared setup defect invalidates all affected attempts,
not just the cell that exposed it. Reuse valid existing Citrus visual repetitions.
