# Run provenance

New benchmark runs use provenance schema 2 with mandatory pre-estimation source,
input and known runtime-asset captures. These preserve concrete reproducibility
evidence; they do not establish physical calibration, build-source linkage or the
complete set of libraries loaded at runtime.

Runtime and resource semantics are specified separately in
[run-measurements.md](run-measurements.md). A new completed benchmark run must
pass both provenance schema 2 and measurement schema 2.

## What a completed run records

`run_meta.json` contains:

- SHA-256, size, and privacy-safe path for every effective config, calibration,
  vocabulary, model, TensorRT engine, and native executable;
- a privacy-normalized snapshot and stable snapshot hash for each small text
  input under `run<N>/provenance/`;
- the commit, tracked dirty state, and dirty-diff hash of each algorithm source
  checkout;
- the repository commit, tracked dirty state, and dirty-diff hash;
- effective runner parameters, including run-type switches, playback rate,
  concurrency controls, and deterministic seeds where applicable;
- either a Docker image ID, a normalized Conda package snapshot, or native
  package identity, depending on the runner;
- process exit status, pseudonymous machine ID, and non-identifying hardware
  and operating-system details.

Large files are hashed in place and are not copied. Hashes are cached beneath
`results/.cache/` using file identity, size, and modification time, so repeated
runs do not re-read unchanged multi-gigabyte models.

## Completion and failure rules

Provenance enrichment is mandatory. `run_benchmark.sh` validates schema 2 after
evaluation and writes `COMPLETE` only after the trajectory, evaluation, and
provenance contracts all pass. A nonzero estimator exit is rejected unless a
runner explicitly marks a narrowly documented shutdown status as accepted.

Failed and interrupted runs never receive `COMPLETE`. Runners that can safely
identify the primary process also write a failed `run_meta.json` with its real
exit code. Partial logs remain available for diagnosis.

Historical runs migrated into `results/` before schema 2 remain preserved and are
labelled `legacy`. Their scientific validity requires separate evidence; they are
not retroactively assigned provenance that was not captured at execution time.

The historical schema-2 collector stored dirty diff digests without the bytes and
did not identify every dynamically linked or container-built estimator binary.
Passing the schema contract therefore does not establish exact implementation
reproducibility. The [qualification review](publication-qualification-20261001.md)
records these gaps per run, including dirty nested-source summaries. Preserve
historical hashes and recover their underlying evidence rather than relabelling
them with today's source or repaired runner. Future capture now preserves exact
checkout bytes and known build assets. Build-source linkage and loaded dependency
resolution remain requirements before execution can be certified ready.

## Pre-estimation preservation

`prepare_fresh_run_dir` reserves an unused attempt and captures:

- `provenance/implementation.json`: exact tracked and non-ignored untracked runner,
  configuration and recursively nested algorithm files, including local edits,
  deletions, symlinks and permissions. Source bytes are independently stored in
  `results/.implementation-blobs/sha256/`, outside the browser's per-run tree.
- `provenance/inputs.json`: content hashes and membership of prepared camera images,
  camera CSVs/calibrations, timestamps, IMU, default GPS and reference files. Camera
  aliases must resolve to the same sensor directories. Large datasets are not copied.
  The private hash cache checks device, inode, size, mtime and ctime; any changed
  signature forces content rehashing. Custom GNSS inputs have their separate copy.
- `provenance/runtime-assets.json`: known native executables/libraries, models and
  vocabularies, immutable image identities and persistent-container build files.
  Container inspection/copying requires no estimator or container startup. Missing
  known assets reject a new attempt. This is a declared asset inventory, not proof
  of complete dynamic dependency resolution or which source built each binary.

Enrichment verifies these captures against the post-execution inputs and checkout.
New completion validation requires the captures and their hashes. Changed artifacts
prevent a completion marker; partial outputs and process records remain preserved.
Later historical validation checks preserved manifests/blobs without requiring
today's source or dataset to match an old run. Preserve the blob store with the
results: a manifest alone cannot restore source bytes. Raw source blobs are private
and may contain local paths; do not publish them blindly through the result browser.

Campaign preflight also checks selected configuration recipes and pinned source,
input and runtime identities. Each new runner checks its capture against the
campaign expectation, avoiding a silent substitution after preflight. Capture and
verification overhead lies outside the timed estimator/pipeline interval.

## Algorithm contracts

Required roles and parameters live in
`scripts/results/provenance_requirements.py`. Each runner passes explicit roles
to `scripts/run/_enrich_run_meta.py`; there is no generic best-effort config
guessing. Adding or changing a runner requires updating both its explicit
arguments and its contract.

DPVO is launched through `_seeded_python.py`. Its default seed is
`1000 + run_id` and can be overridden with `DPVO_SEED`. The wrapper seeds
Python, NumPy, PyTorch, and all visible CUDA devices before loading upstream
`demo.py`.

## Privacy

Stored paths are repository-relative. External inputs are represented by their
basename. Text snapshots and tracked environment overrides replace the current
repository and home paths with `<repo>` and `<home>`. Conda channel URLs are
reduced to their final channel name. Validation rejects private `/home/...` or
`/data/...` paths and hostnames in schema-2 metadata.

The machine identifier is an HMAC-derived local pseudonym; it is stable on one
server but does not reveal the host name or machine-id.

## Validation and browsing

Validate a newly produced run with:

```bash
python3 scripts/results/validate_run.py \
  results/<run-type>/<dataset>/<sequence>/<algorithm>/run<N> \
  --check-only --require-provenance 2 --require-measurements 2 \
  --require-implementation-capture
```

`build_manifest.py` reports provenance and measurements independently as
`complete`, `legacy`, or `invalid`. The generated HTTP result browser shows the
same statuses on the run table and detail pages, and exposes the snapshotted
inputs alongside plots and logs.

Run the focused tests with:

```bash
python3 -m unittest discover -s scripts/results/tests -v
```
