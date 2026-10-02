# Rosario/TODO integration into main — pending ZED completion

**Final destination:** `/data/imoroz/vslam-benchmark`, branch `main`.
Reuse `/data/imoroz/vslam-todo-review-20261002`; create no further checkout and
repeat no calibration audit. Candidate preparation is complete; integration and
Rosario execution readiness are distinct and remain incomplete.

The user explicitly instructed this continuation to update documentation and
**pause the Codex goal** if the ZED batch or its evidence capture is running.
The initial process check found controller **PID 1519727** live, elapsed
**02:12:39**, running
`logs/zed-vio-first-20261002-launch2/batch.py`. The batch remains untouched.
After recording this handoff, pause this goal and do not keep polling. The user
will resume it after ZED finishes. This is a new, explicit integration pause;
the old authorship-maintenance pause remains revoked.

Resume check (2026-10-02T14:54:24.246457+00:00): controller PID 1519727 is still live, elapsed
03:24:05. Integration remains pending. The goal is paused per the explicit user
instruction; batch execution and campaign inputs are untouched. Earlier checks
are preserved in the companion JSON. No further polling is scheduled.

## Already present in main

These four files were byte-identical to the review checkout at the start of this
continuation. The first three now also link this main-destination handoff; those
new main edits must survive later integration.

| File | Applied state |
|---|---|
| `TODO.md` | Five matrices, unchanged A/E/S/F/U counts and red/yellow/readiness markers; failure-inclusive N=3 legend; Rosario preparation notice |
| `docs/todo-status-details.md` | Exact historical attempts, failure evidence and six Rosario candidate-preparation notes; execution remains unverified |
| `docs/rosario-vio-candidates-20261002.md` | Calibration comparison, four prepared profiles, 14 replacements, four missing slots, author questions and native prerequisites |
| `docs/rosario-vio-candidate-validation-20261002.json` | Historical preparation evidence; not a launch manifest or verification of integration into main |

Main HEAD observed: `1458a9c3caeca35926d2ac53293055f5162df4d4`.
The previous **70 passing checks ran in the review checkout**, not against an
integrated main tree. No red marker is removed on that basis. The main goal file
is still evidence-pinned and has not been replaced.

## Pending committed and uncommitted work

Review HEAD: `18dc9d9374755b24e1b1c23a2f0b62a9b2b7d6a9`.
Review commit `18dc9d9` changes six files; uncommitted work further refines five
tracked files and adds the Rosario candidates/scripts/tests/evidence. Review the
**combined final contents**, not only the uncommitted diff or only the commit.

| Pending component | Integration scope |
|---|---|
| TODO generator | Merge final `scripts/campaign/update_todo_matrices.py`; preserve the newer main documentation and current batch outcomes |
| Reporting tests | Add final `scripts/campaign/tests/test_todo_presentation.py`; also merge the two committed assertion changes in `test_acceptance_ledger.py` from `✅ Protocol N=3` to `✅ N=3` |
| Candidate preparation | Add `scripts/campaign/prepare_rosario_vio_candidates.py` and all 27 files under `configs/candidates/rosario-vio-20261002/` |
| Candidate verification | Add `scripts/campaign/validate_rosario_vio_candidates.py` and `scripts/campaign/tests/test_rosario_vio_candidates.py` |
| Validator dependency | Copy only the four pinned Basalt source excerpts and `sources.json` under `review-evidence/rosario-vio-20261002/upstream/`; the validator currently requires these relative paths |
| Goal/documentation | Merge the relevant preparation/formatting/integration sections into main's existing goal; retain other continuations and historical provenance. Update current-location statements to main after integration |

The [file inventory](rosario-main-integration-20261002.json) gives all **38 pending
code/config/test/evidence paths**, source hashes, and destination state. It also
records the documentation state before this handoff. Revalidate hashes and
concurrent edits at resume; do not treat this inventory as overwrite permission.

The existing review artifact
`review-evidence/rosario-vio-20261002/candidate-and-todo-code.patch`
is **incomplete as a standalone integration package**: its 32-file list omits
the committed acceptance-test update and the five upstream-evidence dependency
files. Its previous apply check proves applicability of those hunks only.
Do not blindly apply it, cherry-pick the whole review commit, or copy the entire
review directory. Keep the historical preparation/preservation records intact.

## Steps after the user resumes this goal

1. Re-read both Git statuses/history. Confirm the saved controller has terminated
   and identify any remaining runner, evaluator or evidence-capture processes
   belonging to that batch. Inspect terminal receipts and final captures. An old
   lock or status file alone is insufficient. If any owned work is still live,
   retain the documentation-only restriction and the requested pause behavior.
   Do not restart or stop the benchmark to make integration possible.
2. Preserve the completed ZED outputs, executed manifest/selection and source/input
   captures before changing files or refreshing evidence. Keep run IDs, failures,
   evaluations and original provenance hashes. Leave colleagues' unrelated edits
   and repositories untouched; use current main as the destination.
3. Review `git diff 1458a9c..18dc9d9`, the current uncommitted diff and the 38-path
   inventory together. Merge only the reviewed files into main. Keep the four
   already-applied documents, merge newer annotations, and add current integration
   status to the existing goal rather than replacing it with the review copy.
   Update the generator's candidate note: it must no longer describe the final
   files as remaining in a separate checkout. Preserve matrix shape, counts,
   valid failures, excluded algorithms and all unresolved readiness markers.
4. Keep all four candidate profiles **inactive**. Default runner configuration
   selection must remain unchanged; no configuration-file existence, static test,
   or integration success may set `verified_ready_to_run` true. Retain 14 confirmed
   replacements and four missing OpenVINS repetitions separately. Author questions,
   Basalt offset/parser checks, Voxel shutdown/time conversion and OpenVINS native
   image/time/frame checks remain explicit. No Rosario estimator execution is
   authorized by this goal.
5. From main, run the same focused pytest selection: candidate, TODO-presentation,
   acceptance-ledger, protocol-status and repair-plan tests. Verify candidate source
   hashes and deterministic generation; run `validate_rosario_vio_candidates.py`
   with `--evidence-root /data/imoroz/vslam-benchmark` and a **new integration
   validation report path**. The old preparation report remains historical evidence.
   Confirm candidate inspection rejects readiness, runners still select their
   existing defaults, and protected trajectories/evaluations/CSVs are unchanged.
6. Refresh affected **future** campaign evidence after preserving its old versions.
   Source capture and `pipeline_files` cover `scripts` and `configs`, so adding
   candidates and reporting tests affects shared workspace identities for all
   algorithms, not only Rosario. Reconcile newly finished ZED attempts first so
   they are not scheduled again. Use `build_execution_assets.py --sources --refresh`
   for reviewed current captures; verify unchanged inputs/runtime and refresh them
   only if their evidence actually changed. Rebuild the future manifests with
   `build_future_manifest.py` and the applicable ZED builder, keeping executed
   manifests archived and original historical captures immutable. Do not hand-edit
   hashes, rewrite original run records, or widen readiness flags.
7. The current `build_zed_manifest.py` hardcodes the old category totals
   (27 reusable, 17 replacements, 25 missing, six cohort completions). After the
   running batch, review that selection against actual completed attempts before
   regeneration; do not force new evidence into old totals or silently overwrite
   the executed plan. This is a reconciliation prerequisite, not permission to
   repeat the campaign. Regenerate TODO/details from the reconciled inventory and
   validate source/input/manifest pins with read-only preflight. A blocked Rosario
   readiness result is expected until its genuine prerequisites are met.
8. Finish with integrated main paths, the actual main-tree test results, preservation
   checks and exact remaining prerequisites. Record the integration in Git only
   after re-reading current status/history and selecting the reviewed files.
   No push is authorized. Change 🔴 to 🔄 only for independently verified readiness;
   this integration itself cannot establish native readiness.

No source/config/test integration, campaign evidence refresh, estimator launch,
commit or push occurs while the batch is live. No further polling is needed in
this paused continuation.
