# Run provenance

New benchmark runs use provenance schema 2. The schema makes every completed
result traceable to the effective estimator inputs and executable environment
without storing usernames, hostnames, or private absolute paths.

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

Historical runs migrated into `results/` before schema 2 remain valid and are
labelled `legacy` rather than being retroactively assigned provenance that was
not captured at execution time.

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
  --check-only --require-provenance 2 --require-measurements 2
```

`build_manifest.py` reports provenance and measurements independently as
`complete`, `legacy`, or `invalid`. The generated HTTP result browser shows the
same statuses on the run table and detail pages, and exposes the snapshotted
inputs alongside plots and logs.

Run the focused tests with:

```bash
python3 -m unittest discover -s scripts/results/tests -v
```
