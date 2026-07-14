# Repo-truth discovery

Original preserved base was `bfc15567850dd143dd064f688a0fa99fbeec9eff`. Refreshed `origin/main` and the reconciled package base are `aa56d412e6c625f24f1a9c2cb3e02a512fcb09bb`.

## Facts

- `STRAT-SPEC-0007` is 19,880 bytes, SHA-256 `b23ebc1093df51b7fab5e39c46fd2b96b5e71d35300134eb319a5cbc32d0857c`; status is `review_requested`, reviewer/reviewed_at are null, approval scope is `none`.
- Gate-C approval `GATE-C-H004-R2-0001` has SHA-256 `b05753fe01cc99aa2c4f0e419fca88f4f843154f12843f01aae775eb1e4e68cd`, scope `one_append_only_canonical_strategy_spec_write`, and false downstream flags.
- The crossing audit has one line. Its exact raw bytes including LF hash to `ef5a452a4aff61a35fdbdfcf16162362400345f28af67b7bb41aa4ae36024be2` and bind the Spec and Gate-C hashes.
- The review event hashes to `a0e3174758316a18ff0f4f207886d2cb1704eaad609e397fd1aee1e0f4339230`; it is annotation-only and denies canonical/downstream authority.
- VM schema v1 permits only `approved_for_variant_planning` at `parent_strategy_spec.strategy_spec_review_status`.
- `validate_variant_sweep_artifacts.py` schema-validates that literal and checks parent identity/hash, but does not compare it to canonical status or external approval.
- Existing canonical Specs 0001-0006 use the embedded-approved pathway; 0007 is review-requested. Existing VMs and Sweeps are the matching 0001-0006 pairs. No external planning transition exists.
- The queue contracts bind Gate-C, Spec, VM, Sweep, dataset, denominator, and budget, but currently have no planning-approval lineage.
- Direct Spec mutation changes Gate-C-approved bytes and breaks later admission replay.

## Inspection expansion

Focused validator tests were inspected because the required validator named them. Queue schemas/tests were inspected to establish replay fields. The strategy grammar and intake-control architecture were inspected to confirm approval meaning and authority separation. No runtime, candidate-quality, dashboard, broker, or deployment area was inspected.

## Decision

External append-only approval is compatible with current truth and is the only option that preserves both immutability and the human gate. No stop condition was found.

## Rebase reconciliation

- PR #654 (`8ad273516990e7b6ef8e6d18b6a69c0f863f50c8`) changed the supplemental-role coverage contract and its tests/evidence. It did not change canonical, VM/Sweep, Gate-Q, queue, or approval semantics, so no authority statement changed.
- PR #655 (`aa56d412e6c625f24f1a9c2cb3e02a512fcb09bb`) merged `WP-REPO-BASELINE-STALE-TEST-RECONCILE-01`. Its current evidence records two identical 2,849-node collections, 2,842 passed, the exact seven authorized environment skips, and zero failures/errors; it also confirms `STRAT-SPEC-0007` remains review-requested and non-authoritative.
- A repository-wide search found no merged Main/Karl selection between standalone Gate C-VP and a documented Gate-C variant-planning sub-gate. The design, options assessment, status entry, and follow-up sequence therefore now expose that single decision and prohibit implementation until it is closed and the design is merged.
- No other preserved design statement required reconciliation. Canonical/VM/Sweep inventories, exact hashes, Gate-C lineage, validator behavior, and Gate-Q/queue contracts remain as recorded above.
