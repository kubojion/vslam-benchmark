# docs/ layout (organized 2026-08-06)

| where | what |
|---|---|
| `setup.md`, `running_algorithms.md`, `evaluation.md`, `result-storage-design.md`, `zed2i_setup.md` | **Core how-tos** — install, run, evaluate, browse results; metric definitions and pipeline conventions |
| `generated/` | **Auto-generated, never hand-edited**: result tables (`tables.md`, per-run-type), `verified-claims.md` (numbers for report prose), `figures/` (report figures). Regenerate: `make_report_tables.py`, `verify_claims.py`, `make_report_figures.py` |
| `campaigns/` | **Agent briefs + campaign records** (written for/by Claude): `machine-b-brief.md` (the cross-machine task brief), `machine-b-report-20260806.md` (execution report), `machine-b-verification-20260806.md` (independent verification), `server-campaign-plan.md` (the N=5 plan) |
| `private/` | gitignored scratch/planning |

The superseded report draft lives in `obsolete/report-draft-20260805.md` (gitignored) —
report content is now written from `generated/`, never the other way around.
