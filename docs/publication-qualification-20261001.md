# Publication qualification of retained results — 2026-10-01

The focused [paper acceptance review](paper-acceptance-20261001.md) now supersedes
this document's earlier blanket hold. Explicit evidence-pinned decisions accept
recorded-profile EuRoC claims and narrowly defined observed failures. Agricultural
accuracy and historical GNSS claims remain blocked by material evidence gaps.
The original provenance findings below remain valid disclosures; incomplete build
history alone is no longer treated as proof that every result is invalid.

`scripts/campaign/qualification_review.py` replays the explicit ledger, verifies
original evidence and numerical content, and blocks stale decisions. Unreviewed
artifacts retain the conservative fallback. Acceptance, outcome, repetition count
and execution readiness remain separate. See the generated acceptance handoff for
current counts and exact actions. The matched-session review now establishes 91 distinct estimator-side reruns; see
[the evidence and unresolved physical questions](reference-review-20261001.md).

## What prevents a stronger certificate

All schema-2 historical workspace records examined in this inventory identify a
dirty runner checkout by commit and diff digest, without preserving the diff bytes.
A digest can verify recovered bytes; it cannot reconstruct them. Comparing the
recorded digests with the available checkpoint/stash tree differences did not
recover an exact historical runner tree. The current repaired runner therefore
cannot certify exactly what conversion, selection or override code ran previously.
This affects even otherwise promising EuRoC MAC-VO and DPVO results. It does not
invalidate their recorded clean upstream commits, model/config hashes, full export
coverage or corrected numerical metrics. The subsequent acceptance review weighs native/configuration evidence for a
stated recorded-profile claim. Exact historical rebuild certification would still
require a matching working-tree snapshot or equivalent reconstruction evidence.

The following additional provenance gaps are concrete:

- OKVIS2 and OKVIS2-X have the same dirty-diff digest because their recorded parent
  diffs only say that `external/DBoW2` and `external/opengv` are dirty at the same
  revisions. Reproducing that digest from the current parent diff, after the
  historical collector's whitespace stripping, succeeds. It does **not** identify
  the actual nested changes at execution time. Native binary hashes are retained.
- ORB records its small example launcher executable, but not the dynamically
  linked estimator library. The source checkout identity and executable alone do
  not identify that historical library build.
- AirSLAM, OV2SLAM and Voxel-SVIO record container image identities and
  source revisions, but no run-time native executable hash. A mutable container
  or mounted build can differ from the immutable image. This is a provenance gap,
  not proof of a mismatched executable.
- OpenVINS uses a fresh container whose `/colcon_ws/install` is inside the immutable
  image, not a mounted mutable build. Its image ID therefore identifies those
  installed bytes. Historical dirty runner bytes and runtime resolution/build-source
  linkage remain unverified; do not describe this as evidence of a mutable estimator
  binary. The present read-only asset audit does not retroactively supply that proof.
- Basalt records a native binary hash; the corresponding installed package/source
  revision is not established. It must not be silently assigned the revision used
  to inspect its output convention.
- Historical GNSS results generally lack effective saved source/config/input
  evidence. Current GNSS preparation repairs cannot certify those older runs.

Independent reference issues remain on all agricultural datasets: Horti's original
reference-to-camera transform, Rosario's image/projection/baseline consistency (its physical reference chain is now resolved), and ZED's
position-only reference and lever-arm assumptions. ZED inertial modes additionally
need serial-specific rotation and time-offset evidence. GNSS requires an explicit
reference-independence and global-frame assessment. See the
[repair audit](repair-audit-20261001.md) for the actual frames and evidence.

## What the existing evidence does establish

Hash-verified historical config snapshots pass the selected mode checks documented
in the [saved parameter review](saved-parameter-review-20261001.md), subject to its
explicit unverified checks. Within-cell config equality is checked independently
from implementation/hardware cohort equality. EuRoC frame conversions and all
five modes' metrics have independent numerical checks. These remain useful results;
the review does not replace their measured values with failure placeholders.

Disclose rig-specific settings, MAC-VO's Performant profile, monocular Sim(3), sparse
AirSLAM exports and OKVIS2/OKVIS2-X final-BA differences. Those are claim limitations
or configuration-policy choices, not automatic evidence of incorrect execution.
No measured estimator processing-rate, deadline or real-time guarantee can be
derived from nominal input count divided by wrapper elapsed time.

A genuine scale collapse, incomplete export or nonzero exit remains an observed
outcome. Resolving its protocol evidence can make the outcome reusable for failure
statistics; it cannot turn it into a clean successful repetition. Partial saved
trajectories can support appropriately scoped analysis. A clean N=3 tick additionally
requires three qualified, consistent-cohort, valid trajectories, zero exits and at
least 95% dense export coverage each. This threshold is an explicit reporting gate,
not proof that every input frame was processed or that tracking was error-free.

## Next decisions and execution readiness

The user-authorized focused acceptance review now records the claim decisions in
[the ledger](campaigns/paper-acceptance-20261001.json). It discloses incomplete
historical build detail without waiving calibration/reference defects. It does
not request reruns to improve poor scores. A green tick is scoped to the documented
comparison and clean criteria, not a guarantee against every possible uncertainty.

Review completion means the available evidence was assessed and blockers are
specific. It is distinct from native execution readiness after runner repairs.
The future campaign remains guarded, and no estimator execution is authorized.
