# WP-AGENT-ROBUSTNESS-DIAGNOSTICIAN-01 Branch State

## Scope Summary

Adds a deterministic, ToolContext-routed diagnostician that consumes a real
PR #546 bridge review packet, scratch Result Population artifact, denominator
ledger, and explicit operator robustness approval. It writes only scratch
advisory diagnostics and a human-review packet.

## Main Authorization

Main authorized this third bounded research agent after the formalizer-runner
bridge. The package grants no canonical, evidence, candidate lifecycle,
ranking, readiness, paper/live, runtime, risk, capital, or execution authority.

## Dependency on WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01

The branch is based on `b69a918`, the PR #546 merge. Tests generate inputs
through the merged bridge and its real offline runner path; fixture-only
experiment-runner outputs are not used.

## Prerequisite Artifact Setup

The first attempt stopped because no generated PR #546 bridge artifacts existed
in the clean worktree. This WP now generates deterministic bridge artifacts
through the merged PR #546 bridge path during validation instead of requiring
pre-existing untracked scratch outputs.

## Repo-Truth Discovery

The bridge packet binds its scratch runner artifact and full denominator ledger.
Completed runner rows support aggregate seeded bootstrap and metric confidence
intervals; ledger parameters support sensitivity summaries. Fold and real
per-trade inputs are absent. Detailed discovery is in the package scratch note.

## ToolContext Integration

The existing `robustness_diagnostician` role gains read-only validation and one
new `run_scratch_robustness_diagnostic` action. Bridge reads are limited to the
PR #546 output prefix; diagnostic actions and writes are limited to the active
WP output prefix. Fabricated per-trade data is explicitly hard blocked.

## Input Contract

Required runtime inputs are the bridge review packet, bridge scratch Result
Population artifact, bridge denominator ledger, and operator robustness
approval marker. Paths remain caller-supplied and are cross-bound against the
bridge packet; the production API does not depend on test setup.

## Human Approval Requirement

Approval must set
`approved_for_noncanonical_robustness_diagnostics=true`, identify
`approved_by=operator`, use scope
`noncanonical_scratch_robustness_only`, include a timestamp, and match the
source bridge run ID. Missing, false, or mismatched approval is blocked and
audited before outputs are created.

## Diagnostic Scope

Supported diagnostics are deterministic seeded bootstrap confidence intervals
over finite completed-row metrics, aggregate parameter sensitivity, denominator
integrity, source lineage/hash preservation, funding visibility, and warning
propagation. Diagnostics do not score or rank candidates.

## Denominator Preservation

The agent requires equality across ledger declared count, all five ledger status
counts, review-packet counts, runner row count, and exact variant-ID sets. It
records every row's status, eligibility, and reason while using only completed
rows for metrics. Shrinkage routes through the blocked
`evidence_suppression` action.

## Funding Mode Handling

PR #546 bridge truth is funding-off. The packet preserves requested/effective
mode and explicitly records that funding stress was not performed. No global
funding mode is changed.

## Data Availability Guard Handling

Bridge OI, recent-only, vendor-only, liquidation-history, and other warnings or
blockers propagate without reinterpretation. The agent does not reconstruct OI
from trades or claim unavailable liquidation history.

## Missing-Data Handling

Absent real trade rows produce `QUEUE_PER_TRADE_INSTRUMENTATION` with
`fabricated_per_trade_data=false`. Absent fold inputs produce
`missing_fold_inputs`. Funding-off produces
`not_applicable_funding_mode_off`. Missing metrics are listed with exact skipped
rows rather than imputed.

## Review Packet

The scratch review packet includes source paths and SHA-256 hashes, approval
metadata, validator status, attempted/completed/skipped diagnostics, bootstrap
and sensitivity summaries, denominator snapshot, missing-data states, warnings,
follow-up gaps, and all required non-authority flags including `not ranking
authority`.

## Adversarial Boundary Tests

Tests cover approval bypass, canonical Strategy Spec/VM/Sweep/Result Population
and trial-log writes, candidate registration/freeze/promotion/readiness,
paper/live/runtime and protected controls, private/credential/network access,
funding mutation, denominator shrinkage, evidence deletion, ToolContext bypass,
fabricated trades, provider-memory authority, and out-of-prefix outputs. Each
denial is audited and no forbidden artifact is mutated.

## Validation Status

- Robustness diagnostician, bridge, experiment-runner, formalizer, and
  ToolContext regressions: PASS, 204 tests.
- Result Population and data-availability validator tests: PASS, 69 tests.
- Existing seeded MC, robustness-depth, and purged-fold regressions: PASS, 32
  tests.
- Result Population registry validator: PASS.
- Data feature availability registry validator: PASS.
- Query view discovery: PASS, 124 views.
- Full pytest initially completed with 2,104 passed, 1 skipped, 1 failed, and 6
  warnings. The sole failure was the documented isolated-worktree baseline
  `test_default_fixture_mapping_uses_rp_2592_lineage`, because its gitignored
  D4A normalized CSV was absent. After copying the existing local fixture from
  the root checkout to the same gitignored worktree path for validation only,
  the final full run passed: 2,106 passed, 1 skipped, 6 warnings.

## Boundary Summary

No canonical artifact, schema, validator, query layer, runner, backtester,
compiler, config, dependency, data, project-status, runtime, paper/live, OMS,
risk, reconciliation, capital, broker/exchange, credential, or existing
canonical artifact is modified.

## Non-Authority Statement

All diagnostics and review packets are scratch-only, non-canonical,
non-evidence, not candidate authority, not promotion authority, not ranking
authority, not paper/live readiness, and human-review-required.
