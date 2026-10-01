# Documentation index (status reviewed 2026-10-01)

Start with [the final repair handoff](repair-handoff-20261001.md) and
[the current TODO](../TODO.md). The [server status audit](campaigns/server-status-20261001.md)
is the preserved pre-repair inventory. Generated numeric tables/claims remain
provisional; repair completion does not certify publication or native execution readiness.

| where | what |
|---|---|
| `setup.md`, `running_algorithms.md`, `evaluation.md`, `result-storage-design.md`, `zed2i_setup.md`, `zed2i-imu-extrinsics.md` | **Core how-tos** — install, run, evaluate, browse results; metric definitions and pipeline conventions |
| `generated/` | **Auto-generated, never hand-edited**: result tables (`tables.md`, per-run-type), `verified-claims.md` (numbers for report prose), `figures/` (report figures). Regenerate: `make_report_tables.py`, `verify_claims.py`, `make_report_figures.py` |
| `campaigns/` | **Agent briefs + campaign records** (written for/by Claude): `machine-b-brief.md` (the cross-machine task brief), `machine-b-report-20260806.md` (execution report), `machine-b-verification-20260806.md` (independent verification), `server-campaign-plan.md` (original N=5 protocol with current N=3 scope note), `server-status-20261001.md` (current artifact inventory), `server-n3-manifest-20260826.json` (executed manifest snapshot), `todo-before-status-audit-20261001.md` (historical TODO) |
| `private/` | gitignored scratch/planning |

The superseded report draft lives in `obsolete/report-draft-20260805.md` (gitignored) —
report content is now written from `generated/`, never the other way around.
