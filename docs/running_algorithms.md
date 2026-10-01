# Running and recovering benchmark attempts

Updated after the focused EuRoC campaign (2026-10-02 local). Its six OpenVINS and 18 corrected AirSLAM repetitions are complete; no further estimator execution is authorized. Other paths retain the guarded manifest prerequisites. Existing exclusions
remain: DROID-SLAM, MASt3R-SLAM and MegaSaM. The older
[algorithm walkthrough](running_algorithms-before-repair-20261001.md) is historical;
its replacement behavior and several dataset/config assumptions are superseded.

The EuRoC OpenVINS runner selects `openvins:humble-shutdown-20261001`. EuRoC AirSLAM inertial modes require `/root/catkin_ws_rectified_20261001/devel` in `air_slam`; the original build remains for other paths. Native exits are captured directly and refinement has one attempt. See [build and execution evidence](euroc-focused-campaign-20261001.md).

## Scope and prerequisites

The planned future campaign covers VO, VO-LC, VIO, VIO-LC and GNSS-VIO, with three
logical repetitions per default cell. The previous executed campaign covered the
four modes without GNSS. Its results and the legacy GNSS input variants are retained.
Membership is explicit in the inventory and campaign manifest, not discovered from
whatever result directories happen to exist.

Before future execution, establish the physical sensor/reference calibration,
freeze the applicable algorithm profile and disclose adaptations. Verify source,
executable/model, container, dataset input and effective config identities. Resolve
confirmed invalid configs and retain their historical cohorts. See
[saved parameters](saved-parameter-review-20261001.md),
[qualification](publication-qualification-20261001.md), and
[runner isolation](runner-isolation-audit.md). A syntax check does not establish
native execution readiness. No native crash is claimed fixed by a wrapper change.

Inputs are prepared beneath `datasets/<dataset>/<sequence>/`: image streams under
`mav0/cam0/data` and `mav0/cam1/data`, camera nanosecond timestamps in `times.txt`,
applicable `mav0/imu0/data.csv`, raw reference `gt_tum.txt`, and GNSS inputs where
applicable. Some datasets also expose compatibility symlinks. Use the actual runner's
validated paths; do not guess calibration from a dataset name.

## Read-only campaign preflight

```bash
python3 scripts/campaign/build_repair_inventory.py
python3 scripts/campaign/build_future_manifest.py
python3 scripts/campaign/run_future_manifest.py results/repair-20261001/future-n3-manifest.json
python3 scripts/campaign/run_future_manifest.py results/repair-20261001/future-n3-manifest.json --require-ready
```

Ordinary validation checks structure and evidence hashes. `--require-ready` currently
rejects all actions because prerequisites remain unresolved. This is the expected
result. The future execution interface adds `--run`, optionally with `--action`
for exact logical repetition IDs; it must not be invoked under the current restriction.
Inherited config, playback, GNSS input, seed and numerical-runtime overrides are
rejected unless represented by a separately reviewed recipe.

## Per-run resumption and evaluation-only recovery

`run_benchmark.sh` delegates to `scripts/campaign/run_repetitions.py`. Its positional
interface is `<dataset> <sequence> <algorithm> [N=3] [run_type=vo]`; additional flags
are shown by `python3 scripts/campaign/run_repetitions.py --help`.

The controller preserves existing attempt directories. It never re-estimates an
occupied ID, and does not clear a whole cell. Every completed repetition is evaluated
immediately. A nonzero estimator exit remains recorded even when a usable trajectory
can be recovered. Failure cannot be replaced by sampling until three successes remain.
New corrected cohorts use fresh IDs and retain the originals.

For an existing cell, the controller's `--recover-only` flag prohibits estimator
launches. To evaluate one known saved trajectory directly:

```bash
/data/imoroz/conda/envs/macvo/bin/python scripts/eval/_evaluate_run.py \
  euroc_mav MH_01_easy macvo 1 vo
```

This replaces only the derived evaluation after preserving its previous bytes.
It checks saved inputs and reports qualification separately. Rebuild the authoritative
inventory and reports afterward; for this repair, refresh/check staging before
promotion as described in [evaluation](evaluation.md).

## Configuration and execution details

- ORB selects the sequence-specific ZED 10 Hz profile; its historical 15 FPS VO/VO-LC
  cohort remains a required rerun. Horti VIO-LC now composes the rectified IMU rotation.
- Basalt uses different VO/VIO profiles and an explicit Rosario VO geometry exception.
- AirSLAM's EuRoC inertial rectification patch is prepared but not applied/built/run.
  Sparse keyframe export remains distinct from dense tracking. Refinement retries
  are disabled to preserve the first attempt's outcome.
- OKVIS2 and OKVIS2-X LC profiles differ in final BA. Keep that difference explicit.
- ROS wrappers use owned process stages and private transport. Native/Conda wrappers
  keep outputs within each attempt. See the runner audit for unverified native behavior.
- GNSS variants require an explicit source file. The selected input is copied and
  hashed before execution, and its covariance/status policy is recorded. Historical
  variant names alone do not prove the source used.
- DPVO uses a predetermined recorded seed and stride 1. MAC-VO uses its official
  Performant profile. Neither label implies exact reproduction of an upstream paper.

After new authorization and successful readiness validation, run serially and retain
all attempts. Follow [future preparation](campaigns/future-n3-preparation.md), not
old N=5 or whole-cell replacement examples. All-mode runtime estimates remain partial.
