# Acceptance review validation — 2026-10-01

> Historical validation of acceptance checkpoint `e0ee49b`. The subsequent
> [matched-session validation](reference-validation-20261001.md) supersedes current
> numerical-change and action counts. The checks below describe that earlier snapshot.

The focused review is complete within its no-estimation scope. See the
[acceptance handoff](acceptance-handoff-20261001.md) for decisions and remaining
actions, and [claim criteria](paper-acceptance-20261001.md) for their meaning.

- **154 tests and three subtests passed.** New tests check evidence-pinned decision
  replay, changed-evidence rejection, retained failures without trajectories,
  clean N=3 gates, native errors despite wrapper zero and consistent CSV/report
  rendering. Existing evaluator, source capture, safe resume and isolation tests
  remain passing. No native estimator was invoked by these tests.
- **593 evaluations are numerically identical** to the verified repair-completion
  backup at commit `973723731b83d6935ce259490b0f2fbd091dacd4`. Only qualification
  and qualification provenance changed; previous JSONs are archived.
- **3,471 original non-evaluation evidence files are unchanged**, checked against
  the preserved pre-measurement-repair inventory. Original trajectories, metadata,
  logs and effective config snapshots were not rewritten.
- All **666 CSV rows** retain every original non-qualification field. The ledger,
  inventory, 220 default cell summaries and five TODO matrices agree. All 226
  default/variant reports, tables, evidence counts and 19 figure/data outputs pass
  read-only regeneration checks. TODO matrix row/column layout and regeneration
  are unchanged.
- The browser contains **690 records, 696 HTML pages and 11,139 checked local
  links**, with zero broken links and zero previews of historical plots as current
  figures. It exposes native-error observations and claim limitations.
- The manifest has **212 reusable observations, 30 concrete reruns, 87 missing
  repetitions and 331 blocked cases**. It has zero verified-ready estimator actions.
  `--require-ready` correctly refuses the 448 non-reusable actions; the current
  inherited `LD_LIBRARY_PATH` is also rejected as an unreviewed launch override.
  No execution problem is certified fixed by this review.

Machine-readable preservation/reconciliation checks are in
`results/acceptance-20261001/validation.json`, with the read-only validation script
beside it. Detailed profile/repetition evidence and exact remaining IDs are in
that directory's `evidence.json` and `handoff.json`. These supplement the existing
verified raw-result and repair-completion backups. Current source/input/runtime
identities are refreshed after the local commit and validated without estimation;
they do not establish historical build linkage or physical calibration.

Historical provenance hashes and the authorized authorship mapping are preserved.
No estimator, parameter tuning, history rewrite or push was performed. The obsolete
temporary maintenance pause was explicitly revoked and has not been reapplied.
