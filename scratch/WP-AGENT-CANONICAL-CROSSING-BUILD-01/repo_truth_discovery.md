# WP-AGENT-CANONICAL-CROSSING-BUILD-01 Repo-Truth Discovery

## Scope

Build and fixture-prove the canonical crossing mechanism without writing real
canonical candidate lifecycle registry artifacts or executing the first real
crossing.

This package is build-and-test-only. It does not authorize candidate
registration, freeze, promotion, readiness, paper/live, runtime, OMS, risk,
reconciliation, capital, broker/exchange, credentials, provider/API, network,
canonical Result Population, Strategy Spec, Variant Manifest, Sweep Plan, or
trial-log writes.

## Branch / Base

- Branch: `agent/canonical-crossing-build-01`
- Worktree:
  `C:\GitHub\crypto-perp-wedge-worktrees\agent-canonical-crossing-build-01`
- Base: refreshed `origin/main` at `19613ef`, the PR #551 merge commit for
  `WP-AGENT-CANDIDATE-SCHEMA-ALIGNMENT-01`.

## PR #549 Crossing Design Requirements

Repo-truth facts from
`docs/architecture/2026-06-agent_canonical_crossing_design.md`:

- The crossing must require full content-before-lock review, not label, PR
  merge, comment, status entry, agent recommendation, or summary-only review.
- Approval must be explicit and structured.
- Source paths and hashes must be recomputed before any write.
- Denominator counts, row dispositions, skipped diagnostics, data availability
  warnings/blockers, funding mode, and non-authority flags must be preserved.
- Writes must be append-only and must not overwrite or delete prior evidence.
- ToolContext must audit allow/block decisions.
- The first real crossing remains separately Karl-gated.

## PR #551 Schema / Event Shape

Repo-truth facts from
`docs/architecture/2026-06-candidate_schema_alignment_for_agent_crossing.md`
and `research/schemas/candidate_lifecycle_registry.schema.json`:

- `event_type=candidate_review_packet_crossed` is the schema-approved event
  type for preserving scratch candidate-review packet content.
- Crossing events must be first-entry-shaped:
  `from_status=null`, `to_status=proposed`.
- `crossing_evidence` is required for crossing events and may appear only on
  crossing events.
- `crossing_evidence` preserves `source_lineage`,
  `denominator_snapshot`, `diagnostics_summary`, `data_availability`,
  `funding`, `non_authority_flags`, and `append_only_semantics`.
- No real `research/candidate_lifecycle_registry/` artifact exists in merged
  repo truth.

## Candidate-Review Packet Contract

Current packet shape from
`scratch/WP-AGENT-CANDIDATE-REVIEW-PACKET-01/outputs/dba42387c2e4f679/candidate_review_packet.json`
includes:

- `schema_version=candidate_review_packet_v1`;
- source formalizer, bridge, robustness, denominator ledger, and operator
  approval path/hash refs;
- denominator counts for `completed`, `failed`, `invalid`, `pruned`, and
  `blocked`;
- full row disposition;
- completed/skipped robustness diagnostics;
- missing per-trade, OOS/walk-forward, and funding-stress states;
- data/funding summary;
- required non-authority flags.

Repo-truth adjustment: the packet records
`source_robustness.diagnostics_sha256=sha256:3b47f445...`, while the current
raw file at
`scratch/WP-AGENT-ROBUSTNESS-DIAGNOSTICIAN-01/outputs/9309de71e35fc40f/robustness_diagnostics.json`
hashes to `sha256:a9bf4e44...` in this worktree. A real hash preflight over
that scratch family would correctly block. Positive crossing tests therefore
use controlled test fixtures with matching byte hashes rather than weakening
the source-hash check.

## Fake Fixture Registry Shape

The existing fixture
`tests/fixtures/candidate_lifecycle_registry/valid_candidate_review_packet_crossing.candidate_lifecycle_registry.json`
proved that a complete crossing event shape can validate.

This package's builder writes only fake registry copies under
`scratch/WP-AGENT-CANONICAL-CROSSING-BUILD-01/outputs/<run_id>/`. Tests use
temp-root fixture registry copies with one fake candidate and no pre-existing
event for that candidate, then append one
`candidate_review_packet_crossed` event.

## Candidate Registry Validator Invocation

Post-write validation uses the existing entrypoint:

```text
tools.registry.validate_candidate_registry.validate_candidate_registries(registry_dir=<run_dir>)
```

No `tools/registry` behavior is changed. The package also runs
`python -m tools.registry.validate_candidate_registry` for committed fixture
regression coverage.

## ToolContext Roles / Actions

Existing ToolContext policy is closed by default and already hard-blocks
canonical writes, lifecycle transitions, promotion/readiness, trial-log
mutation, runtime/paper/live, OMS, risk, reconciliation, safe-mode, kill-switch,
broker/exchange/order/capital, credentials, private endpoints, network,
provider API calls, gate bypass, evidence suppression/deletion, and provider
memory as truth.

This package adds only:

```text
role: canonical_crossing_builder_fixture
action: build_fixture_canonical_crossing
```

The action is allowed only under the active WP scratch output prefix. The
builder further restricts inputs to `tests/fixtures/` or the active WP scratch
prefix and blocks real `research/` candidate registry outputs.

## Existing Helper Behavior

`tools/candidate_lifecycle/lifecycle_engine.py` remains scratch-only and uses a
different lifecycle vocabulary from the candidate lifecycle registry schema.
This package does not modify that helper or use it as a canonical write path.

## Forbidden Real Canonical Write Paths

Forbidden for this package:

- `research/candidate_lifecycle_registry/`
- `research/candidate_registry.jsonl`
- `research/result_populations/`
- `research/strategy_specs/`
- `research/variant_manifests/`
- `research/sweep_plans/`
- `research/trial_log.jsonl`
- runtime, paper/live, OMS, risk, reconciliation, safe-mode, broker/exchange,
  order, capital, credential, private endpoint, provider/API, and network
  paths.

## Repo-Truth Adjustments

- The schema target is no longer unresolved after PR #551; the event target is
  `candidate_review_packet_crossed` with `crossing_evidence`.
- The build can be proven against fixtures without changing schema, validator,
  query-layer, or real canonical artifacts.
- The first real crossing remains outside this package and must be separately
  Karl-gated.
