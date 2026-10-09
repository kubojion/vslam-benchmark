# Result storage and browser design

Status: implemented 2026-08-26; operational limitations reviewed 2026-10-01.

The current store is not a finalized campaign: see [the status audit](campaigns/server-status-20261001.md).
COMPLETE permits both `ok` and `scale_collapse`; it does not certify tracking success.
Cell replacement removes the old result before all new repetitions succeed, and the batch
wrapper evaluates after all repetitions, so interruption can leave successful output unscored.
Preserve such output before recovery. Five COMPLETE smoke runs currently remain under
headline roots and need exclusion; root CSVs and browser snapshots are not synchronized.
The design below does not imply these operational gaps have been closed.

## Purpose

This document defines a simpler layout for generated benchmark results. All
artifacts stay inside the repository working directory under one Git-ignored
`results/` directory. The five aggregate benchmark CSVs remain tracked so a
fresh clone still contains the numbers needed to compare algorithms.

The design has no campaign registry, database, MLflow service, cloud storage,
or automatic result history. Development results are replaced when an
algorithm is rerun. When the final result set is ready, it can be copied or
moved manually as a single directory.

## Scope

This proposal changes only how generated results are stored and discovered:

- trajectories and algorithm-native output;
- run metadata, logs, and resource measurements;
- evaluation JSON and plots;
- per-algorithm metrics and reports;
- the five benchmark CSVs;
- a generated manifest and static result browser.

It does not change datasets, model weights, configurations, algorithm options,
available compute, run-type definitions, or evaluation formulas. Algorithms
remain free to produce and retain all native artifacts, including large maps,
databases, and diagnostic plots.

## Proposed layout

Use the repository's existing ignored `results/` directory as the only generated
result root:

```text
vslam-benchmark/
├── results/                         # Git-ignored
│   ├── manifest.json                # generated index of current results
│   ├── vo/
│   ├── vo-lc/
│   ├── vio/
│   ├── vio-lc/
│   ├── gnss-vio/
│   ├── site/                        # generated static browser
│   ├── .locks/                      # active algorithm-cell locks
│   └── .staging/                    # optional temporary generation area
├── benchmark-vo.csv                 # Git-tracked
├── benchmark-vo-lc.csv              # Git-tracked
├── benchmark-vio.csv                # Git-tracked
├── benchmark-vio-lc.csv             # Git-tracked
└── benchmark-gnss-vio.csv           # Git-tracked
```

The five run types continue to mean exactly what they mean now. They are merely
directories beneath one common result root instead of five repository-level
trees.

Each run-type tree retains the current dataset/sequence/algorithm hierarchy:

```text
results/<run-type>/
└── <dataset>/
    └── <sequence>/
        └── <algorithm>/
            ├── metrics.csv
            ├── report.md
            ├── <algorithm-level plots>
            └── run<N>/
                ├── COMPLETE
                ├── trajectory.txt
                ├── run_meta.json
                ├── run_eval.json
                ├── run_log.txt
                ├── resources.csv
                ├── segment_map.png
                ├── segment_map_3d.png
                └── <algorithm-specific artifacts>
```

Run directories remain flat because existing runners and evaluators already use
these filenames. Large or algorithm-specific files do not require a separate
storage class; they remain beside the other output from that run.

## Result ownership and replacement

The replacement unit is one complete algorithm result cell:

```text
results/<run-type>/<dataset>/<sequence>/<algorithm>/
```

When an algorithm is rerun for the same run type, dataset, and sequence, the
previous cell is no longer relevant. The benchmark driver should clear that
whole cell before beginning the replacement. It must not clear only `run1/`
because the algorithm directory also contains aggregate metrics, reports, and
potentially many generated images and plots.

For example, rerunning ORB-SLAM3 on EuRoC MH_01 in VO replaces:

```text
results/vo/euroc_mav/MH_01_easy/orbslam3/
```

This removes all old repetitions and derived output for that comparison cell,
then recreates the cell from fresh executions.

The benchmark driver owns replacement. Individual algorithm runners should not
rename, archive, or delete old run directories themselves. They should receive
a fresh output directory and write only their own run.

Do not preserve old results by renaming `run1` to names such as `run1_old` or
`run1_backup` inside the algorithm directory. Existing discovery patterns use
`run*`, so those names can be mistaken for benchmark repetitions. If an output
needs temporary manual preservation, move it outside `results/<run-type>/`, for
example into the existing `experiments/` area.

## Preventing stale output

The current overwrite behavior is acceptable because old results are not
valuable after a deliberate rerun. The important requirement is that files from
the old and new executions must never be mixed.

The initial implementation should use four small safeguards.

### 1. Clear the whole algorithm cell once

`run_benchmark.sh` clears the algorithm cell before the first repetition. It
does not clear the directory between repetitions and individual runners do not
perform replacement.

Before any recursive removal, the helper must:

1. canonicalize the run type and dataset name;
2. reject empty, `.` or `..` path components;
3. resolve the target path;
4. verify that it is below the expected `results/<run-type>/` root;
5. verify that the relative suffix contains exactly dataset, sequence, and
   algorithm components;
6. print the exact cell being replaced.

If validation fails, the benchmark must stop without deleting anything.

### 2. Require fresh run directories

Each algorithm runner must refuse to write into an existing nonempty `run<N>`
directory. Under normal operation this cannot occur because the benchmark
driver has already replaced the cell. The check protects direct runner use and
incorrect orchestration.

The runner must not silently use `mkdir -p` to merge a new execution with an old
run directory.

### 3. Write completion last

After the algorithm exits successfully, evaluation finishes, and required files
are validated, the benchmark driver writes an empty `COMPLETE` marker as the
last file in the run directory.

A run without `COMPLETE` is incomplete regardless of which other files happen
to exist. Failed execution may leave logs, trajectories, or partial plots, but
those files cannot enter aggregate or repository-level benchmark tables.

### 4. Aggregate only complete runs

`_aggregate_runs.py`, `build_benchmark_csv.py`, report generation, and the static
site generator must require `COMPLETE`. They must not infer success merely from
the presence of an old `run_eval.json`.

Together these rules address stale output without campaign tracking or automatic
archiving.

## Failure behavior

If a rerun fails after the old algorithm cell was cleared:

- the new partial files remain available for diagnosis;
- no `COMPLETE` marker is written;
- the run is excluded from aggregates and the tracked benchmark CSVs;
- the previous result is not restored automatically.

Losing the old result in this situation is an accepted consequence of the
simpler replacement model. If preserving the last successful cell becomes
important later, the driver can generate into `.staging/` and swap the completed
cell into place. That is an optional improvement, not a requirement for the
initial implementation.

Concurrent invocations targeting the same algorithm cell must be rejected. A
lock beneath `results/.locks/` is sufficient; unrelated algorithms or sequences
may still run concurrently.

## Result manifest

`results/manifest.json` is a generated index of the current result tree. It is
not a history and is not manually edited. Rebuilding it replaces the previous
manifest.

The manifest should contain:

- schema version and generation time;
- repository commit and dirty-state indicator;
- a pseudonymous machine ID and non-identifying hardware profile;
- one entry for every discovered run;
- run type, dataset, sequence, algorithm, and repetition;
- status: `complete`, `failed`, `incomplete`, or `invalid`;
- paths to common files and available previews;
- selected metrics copied from `run_eval.json`;
- SHA-256 hashes for the canonical trajectory, `run_meta.json`, and
  `run_eval.json` when present;
- an inventory of additional files with paths and sizes.
- provenance and measurement status (`complete`, `legacy`, or `invalid`) and
  schema versions.

New executions use the mandatory schema described in
[run-provenance.md](run-provenance.md). Migrated historical runs remain
discoverable as `legacy`; the manifest does not invent missing execution-time
identity for them.

Measurement schema 1 is documented in
[run-measurements.md](run-measurements.md). It keeps historical runs visible as
`legacy` while preventing whole-system resources or pose-rate FPS from being
presented as estimator performance for new runs.

Example:

```json
{
  "schema_version": 1,
  "generated_at_utc": "2026-08-26T19:42:08Z",
  "git_commit": "a13ce4f...",
  "git_dirty": false,
  "machine_id": "machine-7f3a91c2d804",
  "runs": [
    {
      "path": "vo/euroc_mav/MH_01_easy/orbslam3/run1",
      "run_type": "vo",
      "dataset": "euroc_mav",
      "sequence": "MH_01_easy",
      "algorithm": "orbslam3",
      "repeat": 1,
      "status": "complete",
      "trajectory_sha256": "...",
      "run_meta_sha256": "...",
      "run_eval_sha256": "...",
      "metrics": {
        "ate_rmse": 0.041,
        "coverage": 0.997,
        "fps": 31.2
      },
      "artifacts": [
        {"path": "segment_map.png", "size_bytes": 123456},
        {"path": "run_log.txt", "size_bytes": 98765}
      ]
    }
  ]
}
```

### Privacy rules

The manifest and generated website must not expose a hostname, username, home
directory, IP or MAC address, hardware serial number, or another
organization-specific identifier.

Generate `machine_id` automatically on the host. The preferred input is the
high-entropy value in `/etc/machine-id`, combined with a fixed
project-and-schema namespace and passed through an application-specific
cryptographic digest. Store only a short prefix of the digest:

```text
machine-7f3a91c2d804
```

The same physical machine will therefore receive the same pseudonym across
result rebuilds, while different machines will normally receive different
pseudonyms. The raw machine ID must never be copied into the repository,
manifest, run metadata, logs produced by the result tooling, or website.

The derivation should be equivalent to:

```python
namespace = b"vslam-benchmark/result-machine-id/v1"
digest = hmac_sha256(key=machine_id_bytes, message=namespace)
public_id = "machine-" + digest.hexdigest()[:12]
```

Run this helper on the host, not inside an algorithm container, because a
container may expose a different or deployment-specific machine identity.

If `/etc/machine-id` is missing or invalid, generate a random UUID on first use
and persist it with mode `0600` under the user's local configuration directory,
for example `~/.config/vslam-benchmark/machine-id`. Later runs reuse that value.
This fallback is also automatic and its backing file is never included in
result artifacts.

Do not hash the hostname directly. Hostnames often come from a small, guessable
set, so an ordinary or truncated hostname hash provides weak anonymity. The
automatic machine-ID derivation provides stability without manual configuration
and without using the machine's name.

Continue collecting non-identifying reproducibility information such as CPU and
GPU model, core count, RAM size, OS version, driver version, and Python version.
The existing `_system_info.py` collector already deliberately excludes hostname
and username; that property must be preserved.

All paths written to the manifest and website must be relative to the repository
or `results/` root. Raw logs remain local and Git-ignored, but any future export
outside the SSH-only browser should be checked separately for absolute paths or
other incidental identifiers.

The existing `run_meta.json` and `run_eval.json` remain the detailed sources.
The manifest provides discovery, status, hashes, and a convenient input for the
browser.

Manifest generation must be deterministic: paths and runs are sorted, JSON keys
have stable ordering, and rebuilding without result changes produces identical
run content apart from the generation timestamp.

## Tracked CSV results

The five root benchmark CSVs remain tracked:

```text
benchmark-vo.csv
benchmark-vo-lc.csv
benchmark-vio.csv
benchmark-vio-lc.csv
benchmark-gnss-vio.csv
```

This allows anyone cloning the repository to compare the published algorithm
numbers without downloading server artifacts.

Normal development runs do not automatically rewrite those files. The
publication workflow is:

1. run and inspect algorithms under ignored `results/`;
2. rebuild and validate `results/manifest.json`;
3. explicitly run `python3 scripts/eval/build_benchmark_csv.py all` when the
   current complete results are intended for publication;
4. review the five tracked CSV diffs before committing them.

Generated Markdown tables and report figures under `docs/generated/` may remain
tracked as publication output.

## Static result browser

The browser is generated from `results/manifest.json`, the five CSVs, existing
JSON metadata, and existing plot images. It has no database and no write API.

The first version should provide:

- one tab for each run type;
- the tracked or current benchmark comparison table;
- filters for dataset, sequence, and algorithm;
- clear complete, failed, incomplete, and invalid status display;
- run details and provenance;
- inline PNG trajectory and segment plots;
- text and JSON viewing for logs, metadata, and evaluation;
- individual download links for other artifacts.

The generator writes to `results/site/`. It should rebuild the site completely
instead of merging with a previous build, preventing stale pages or images.

Serve the site on the server loopback interface:

```bash
python3 -m http.server 8080 \
  --bind 127.0.0.1 \
  --directory results/site
```

From a laptop:

```bash
ssh -N -L 8080:127.0.0.1:8080 <user>@<benchmark-server>
```

Then open `http://localhost:8080`. Only requested HTML, plots, logs, or artifacts
are transferred. The result directory does not need to be copied to the laptop
or opened through VS Code.

## Implemented changes

### 1. Centralize result paths

Update `scripts/_paths.sh` to map run types as follows:

```text
vo       -> <repo>/results/vo
vo-lc    -> <repo>/results/vo-lc
vio      -> <repo>/results/vio
vio-lc   -> <repo>/results/vio-lc
gnss-vio -> <repo>/results/gnss-vio
```

Update `scripts/eval/_run_type.py` to use the same layout. Keep run-type alias
normalization centralized so shell and Python code cannot disagree.

### 2. Add result helpers

Add a small `scripts/results/` directory:

```text
scripts/results/
├── machine_id.py            derive the stable pseudonymous machine ID
├── prepare_cell.py          safely replace and lock one algorithm cell
├── validate_run.py          validate required files and write COMPLETE
├── build_manifest.py        rebuild results/manifest.json
├── build_site.py            rebuild results/site/
└── serve_site.sh            loopback-only HTTP helper
```

The helpers must reject paths that resolve outside the repository `results/`
root. Cleanup and site generation must fail closed when path validation fails.

### 3. Update the benchmark driver

Update `scripts/run/run_benchmark.sh` to:

1. calculate and lock the exact algorithm cell;
2. replace the entire cell before the first repetition;
3. invoke each runner with a fresh `run<N>` directory;
4. evaluate each successful execution;
5. validate it and write `COMPLETE` last;
6. aggregate only complete repetitions;
7. rebuild the result manifest and static site;
8. release the cell lock on exit.

Direct single-run scripts should refuse an existing nonempty output directory.
They should not implement backup naming or independent retention logic.

### 4. Update evaluation discovery

Update these consumers to use `results/<run-type>` and require `COMPLETE`:

- `scripts/eval/_evaluate_run.py` where applicable;
- `scripts/eval/_aggregate_runs.py`;
- `scripts/eval/build_benchmark_csv.py`;
- report table and figure generators;
- one-off analyses containing hard-coded `results-*` paths.

Aggregate files and plots at the algorithm level are regenerated after the cell
has been cleared, so old plots cannot survive a rerun.

### 5. Update container mounts

Several container integrations currently mount individual repository-level
`results-*` directories. Mount the common host directory once:

```text
<repo>/results -> /results
```

Then use `/results/<run-type>/...` inside containers. Audit at least AirSLAM,
Voxel-SVIO, OV2SLAM, CIFASIS GNSS-SI, and VINS-Fusion GPS setup and run scripts
for hard-coded legacy paths.

This changes output routing only. It must not change algorithm configuration,
inputs, or resource access.

### 6. Simplify Git ignores

The repository already ignores `results/`. After migration, also ignore the
five old roots completely so a stale script cannot repopulate them unnoticed:

```gitignore
/results-vo/
/results-vo-lc/
/results-vio/
/results-vio-lc/
/results-gnss-vio/
```

Remove their generated contents from Git tracking only after the migrated copies
have been verified. Keep all five root `benchmark-*.csv` files tracked.

## Server migration procedure

Migration must preserve the current dirty result trees until all server outputs
have been accounted for.

1. Create `results/{vo,vo-lc,vio,vio-lc,gnss-vio}`.
2. Inventory tracked, modified, untracked, and ignored files under the five old
   roots.
3. Move each old tree to its new run-type directory on the same filesystem so
   file contents and inode data are preserved without temporarily doubling the
   roughly 4 GiB store.
4. Validate pre/post file counts and byte totals for every run type.
5. Validate existing runs and add `COMPLETE` only where required output and
   evaluation are genuinely present.
6. Build `results/manifest.json` and inspect all incomplete or invalid entries.
7. Leave the tracked benchmark CSVs unchanged during migration; rebuilding them
   remains an explicit publication action.
8. Build the static site and verify tables, plots, logs, and downloads through
   an SSH tunnel.
9. Update all runners, evaluators, and container mounts.
10. Exercise representative native, Conda, persistent-container, and one-shot
    container runners in the new layout.
11. Stop tracking the old generated result trees and add full ignore rules for
    them.
12. Confirm that no legacy result root was recreated.

No existing result file is deleted by the migration; directory trees are
renamed within the same filesystem.

## Manual final-result handling

The automated system does not distinguish development campaigns from a final
campaign. `results/` is always the current server result set.

When the final run is accepted:

1. regenerate and validate `results/manifest.json`;
2. explicitly rebuild and review the five tracked benchmark CSVs;
3. regenerate tracked report tables and figures;
4. commit the small publication files;
5. optionally copy or move the complete ignored `results/` directory manually
   to a final archival location.

This manual transition is intentional. There is no campaign naming convention,
automatic archive, or retained sequence of overwritten development results.

## Migration outcome (2026-08-26)

The five server trees were renamed into `results/` on the same filesystem. The
pre/post inventories matched exactly:

| Run type | Files | Bytes |
|---|---:|---:|
| `vo` | 1,555 | 3,212,439,272 |
| `vo-lc` | 417 | 306,509,856 |
| `vio` | 696 | 566,308,671 |
| `vio-lc` | 289 | 106,011,265 |
| `gnss-vio` | 261 | 146,877,872 |

The first manifest contains 333 run directories: 319 complete and 14
incomplete. Twelve incomplete directories have an evaluation but lack the now
required `run_meta.json`; two are empty failed-output placeholders. They remain
available for inspection but are excluded from future aggregation. The five
tracked benchmark CSVs were not rewritten during migration.

Existing persistent benchmark containers still carry the retired bind-mount
definitions. Docker cannot change mounts on an existing container, so AirSLAM,
CIFASIS GNSS-SI, OV2SLAM, VINS-Fusion, and Voxel-SVIO containers must be stopped,
removed, and recreated with their updated setup scripts before their next run.
Removing those containers does not remove bind-mounted source, datasets,
configs, or results.

## Acceptance criteria

The change is complete when:

- all five run types write beneath `results/`;
- no normal benchmark execution modifies tracked result artifacts;
- the five root benchmark CSVs remain available in a fresh clone;
- rerunning an algorithm replaces its whole result cell, including old plots;
- individual runners refuse nonempty run directories;
- incomplete runs never receive `COMPLETE`;
- aggregates and benchmark CSVs ignore runs without `COMPLETE`;
- concurrent writes to the same algorithm cell are rejected;
- the generated manifest accurately classifies every run;
- the manifest and website use only the automatically derived pseudonymous
  `machine_id` and contain no raw host or user identity;
- deleting and rebuilding `results/site/` produces a correct browser;
- plots and logs can be viewed from a laptop through an SSH tunnel;
- algorithms, datasets, weights, configurations, and evaluation formulas remain
  unchanged.

## Benefits over the current system

| Previous system | Implemented system |
|---|---|
| Five result roots mixed with repository content | One ignored `results/` root |
| Git tracks only selected parts of runs | All raw artifacts remain together but ignored |
| Reruns may merge with old files | Whole algorithm cell is cleared before rerun |
| Old aggregate images may survive | Metrics, reports, and plots are regenerated from a fresh cell |
| Renamed backup runs can match `run*` discovery | No automatic backup naming inside result trees |
| Success inferred from whichever files exist | Explicit `COMPLETE` marker and validation |
| Remote inspection requires shell or VS Code navigation | Generated read-only website over SSH |
| Folder contents have no central inventory | One rebuildable manifest for the current result set |
| Large artifacts complicate Git | Only compact benchmark CSVs and reports are tracked |
| Campaign management would add overhead | Current results are simply replaced; final handling is manual |

## Accepted limitations

- The system keeps no automatic history of overwritten development results.
- A failed rerun can leave the previous successful cell unavailable; the failed
  replacement is excluded because it lacks `COMPLETE`.
- Local results are not a backup and remain dependent on the server filesystem.
- The static browser is read-only and optimized for inspection rather than
  arbitrary database queries.
- Manual final archiving and deletion require operator care.

These limitations match the intended workflow and keep the implementation
smaller than the current fragmented result handling.
