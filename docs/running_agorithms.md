# Running the algorithms

The framework expects a sequence under

```
datasets/<dataset>/<seq>/
├── cam0/        # rectified left images  (PNG/JPG, sorted by filename)
├── cam1/        # rectified right images
├── times.txt    # one line per frame, nanosecond timestamps
└── gt_tum.txt   # ground truth in TUM format (timestamp tx ty tz qx qy qz qw, seconds)
```

`scripts/data/convert_*.sh` produce this layout from raw rosbags (Rosario v2, HortiMulti, LFSD).

Worked example: a new **Rosario sequence 2**.

## 1. Prepare the dataset

```bash
# put the .bag and *_pgt.bag inside datasets/rosariov2/sequence2/
bash scripts/data/convert_rosario_to_tum.sh datasets/rosariov2/sequence2
```

This populates `cam0/`, `cam1/`, `times.txt`, `gt_tum.txt`.

## 2. Add config files

* ORB-SLAM3 — reuse the dataset-level file `configs/orbslam3/rosariov2_stereo.yaml` (same calibration).
* DROID-SLAM — reuse `configs/droidslam/rosariov2.txt`.
* MAC-VO — add a new per-sequence file `configs/macvo/rosariov2_sequence2.yaml` (copy `rosariov2_sequence1.yaml` and change `name:` + `root:` — keep the `__WS__` placeholder).

## 3. Run each algorithm three times

```bash
# All three with the standard 3-run + evaluation pipeline:
bash scripts/run/run_benchmark.sh rosariov2 sequence2 orbslam3 3
bash scripts/run/run_benchmark.sh rosariov2 sequence2 droidslam 3
bash scripts/run/run_benchmark.sh rosariov2 sequence2 macvo 3
```

`run_benchmark.sh` calls the per-algorithm runner N times then evaluates each
run and aggregates the results (see [evaluation.md](evaluation.md)).

If you only want a single ad-hoc run:

```bash
bash scripts/run/run_orbslam3.sh  rosariov2 sequence2 1
bash scripts/run/run_droidslam.sh rosariov2 sequence2 1
bash scripts/run/run_macvo.sh     rosariov2 sequence2 1
```

Per-run output: `results/<dataset>/<seq>/<algo>/run<N>/{trajectory.txt, run_log.txt, resources.csv}`.

## Notes per algorithm

* **ORB-SLAM3** needs the executable `stereo_euroc` from `src/ORB_SLAM3/Examples/Stereo/`. Re-run `./build.sh` if it's missing.
* **DROID-SLAM** runs in the `droidenv` conda env. With `stride=2` it processes every second frame; trajectory length will be ~half the input.
* **MAC-VO** runs in the `macvo` conda env. The config's `root:` field uses a `__WS__` placeholder that `run_macvo.sh` substitutes with the workspace root at launch — never hardcode a path.

## Other datasets

The flow is identical:

```bash
bash scripts/data/convert_hortimulti.sh datasets/hortimulti/strawberry04
bash scripts/run/run_benchmark.sh hortimulti strawberry04 orbslam3 3
```

For HortiMulti add `configs/macvo/hortimulti_strawberry04.yaml`; ORB-SLAM3 / DROID configs are dataset-level and need no change.
