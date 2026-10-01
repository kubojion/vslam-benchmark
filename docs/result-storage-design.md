# Result storage and browser

Updated 2026-10-01. All five result trees, root CSVs, cell reports and the browser
now use the reconciled schema-3 evidence. Scientific qualification remains separate;
see [publication qualification](publication-qualification-20261001.md). The original
[pre-repair design](result-storage-design-before-repair-20261001.md) is historical.
Its whole-cell deletion and COMPLETE-only aggregation rules are superseded.

## Current layout

```text
benchmark-{vo,vo-lc,vio,vio-lc,gnss-vio}.csv  # tracked derived comparisons
results/                                 # ignored raw and derived artifacts
  <mode>/<dataset>/<sequence>/<algorithm>/
    run<N>/                              # immutable physical attempt identity
      trajectory.txt
      run_meta.json                      # original process/configuration evidence
      run_eval.json                      # current schema-3 evaluation and review
      .evaluation_history/<sha256>.json  # independently preserved prior evaluation
      provenance/                        # saved effective inputs
      processes/                         # new attempts: owned process-stage records
      native/                            # new attempts: private native exports
    metrics.csv                          # planned repetition rows, including failures
    summary.json                         # separate configuration/source cohorts
    report.md
    variants/<variant>/                  # separate GNSS experiment summaries
  manifest.json                          # 690 planned/retained browser records
  site/                                  # generated browser
  repair-20261001/                        # inventory, staging, validation, future manifest
  .implementation-blobs/sha256/           # private exact source bytes; preserve with results
  .derived-history/                      # content-addressed previous derived bytes
  .derived-sites/                        # independently retained previous sites
```

New attempts use an unused physical ID. The future manifest allocates IDs starting
above 10000 and records their logical repetition and cohort separately. A failed,
partial or completed directory is never deleted to make room for another attempt.
The repetition controller evaluates each available trajectory before advancing and
can retry evaluation without launching estimation. Locks protect controller writes;
they do not control unrelated manually launched jobs. See [runner isolation](runner-isolation-audit.md).

`COMPLETE` is a historical execution/artifact marker, not a scientific certificate.
Recovery does not invent missing markers. The inventory includes saved evaluated
outputs without COMPLETE, missing repetitions and failed attempts. Historical
excluded algorithms and smoke tests remain inspectable but are excluded from the
headline CSVs and default browser filter. Six GNSS variants stay separate from the
660 default planned repetitions.

## Publication and preservation

Numerical status, exit code, dense export coverage, reference support, scientific
review and cohort identity are separate fields. All 593 current evaluations were
promoted from checked staging; `results/repair-20261001/promotion-manifest.json`
records old/new hashes and archive locations. No original trajectory, run metadata,
config snapshot, log or COMPLETE marker was changed by promotion. A historical
`previous_evaluation.path` identifies the path at evaluation time; its original
bytes are recoverable by hash under `.evaluation_history/` and the external backup.

Rebuilding an inventory verifies input and saved-config hashes. CSV/table/figure
and browser generators then verify the inventory and reject stale CSVs rather than
mixing snapshots. Matching published and staged evaluations use the normal result
path in CSV links. Distinct cohorts and GNSS variants are not pooled. No clean N=3
tick is inferred from count or one successful repetition.

Original backup: `/data/imoroz/vslam-repair-backups/20261001T102654Z-vo-pre-repair/`.
It contains restoration instructions, verified checksum inventories, Git history,
all five result trees and nested source changes. Superseded generated documentation
is retained under [historical-before-repair-20261001](generated/historical-before-repair-20261001/README.md).
Raw evidence is not disposable cleanup material. Git does not back up ignored results;
preserve the external backup and result store independently.

## Regeneration and local browsing

Use the scientific Python environment and the commands in [evaluation](evaluation.md).
After successful regeneration, serve the site locally with:

```bash
bash scripts/results/serve_site.sh 8080
```

The server binds to localhost. An SSH tunnel can expose it to your laptop. The
browser separates current JSONs from historical plots and redacts identifying paths
in displayed logs/metadata. It does not turn an artifact into qualified evidence.
Native containers, calibration and missing historical provenance still have the
specific prerequisites in the [future manifest](campaigns/future-n3-preparation.md).
