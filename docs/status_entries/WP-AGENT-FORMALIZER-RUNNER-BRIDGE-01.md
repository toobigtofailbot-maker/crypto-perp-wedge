# WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01 Branch State

## Scope Summary

Adds a deterministic bridge from a human-approved formalizer scratch draft to
validator-compatible scratch Strategy Spec, Variant Manifest, and Sweep Plan
copies, then invokes the real offline runner on a local 15m fixture. All outputs
remain under the active package scratch prefix.

## Main Authorization

Main authorized this package as a non-canonical bridge only. It grants no
canonical artifact, evidence, candidate lifecycle, promotion, paper/live,
runtime, OMS, risk, reconciliation, capital, exchange, credential, or network
authority.

## Dependency on WP-AGENT-IDEA-FORMALIZER-01 and WP-AGENT-EXPERIMENT-RUNNER-01

The bridge requires the PR #544 `agent_formalized_idea_v1` output, its validated
scratch Strategy Spec draft for the merged `STRAT-SPEC-0003` family, and a new
colocated operator marker scoped to this bridge. PR #545 supplies the existing
approval/audit/denominator patterns but its fixture executor is not reused.

## Repo-Truth Discovery

`run_offline_sweep` already supports caller-supplied scratch inputs and a
non-canonical output directory while blocking canonical Result Population
writes. The VM/Sweep schemas require planning/frozen compatibility fields, and
the merged `VM-0003`/`SWEEP-PLAN-0003` pair supplies the narrow bounded grid.
Detailed discovery is in the package scratch note.

## ToolContext Integration

Adds the `formalizer_runner_bridge` role and the narrowly path-scoped
`noncanonical_offline_sweep_run` action. Formalizer reads, active scratch
reads/writes, validators, both real-runner invocations, and local fixture reads
are audited through ToolContext. Existing hard prohibitions remain unchanged.

## Input Contract

Inputs are an accepted BTCUSDT 15m SMA/stddev formalizer artifact, its produced
and validator-clean scratch Strategy Spec, a colocated operator approval marker,
and a repo-local 15m OHLCV CSV fixture. The formalizer, approval, draft, and data
are hash-bound into the deterministic bridge run ID.

## Human Approval Requirement

The marker must set `approved_for_noncanonical_runner_bridge=true`, identify
`approved_by=operator`, use
`approval_scope=noncanonical_scratch_runner_bridge_only`, include a timestamp,
and match `source_formalizer_run_id`. Missing or mismatched approval is blocked
and audited. Funding-on additionally requires an explicit funding-on approval,
but still blocks because current runner truth cannot execute it.

## Bridge Mapping

The bridge reuses the exact merged `STRAT-SPEC-0003` adapter output and the
bounded eight-variant VM/Sweep templates. It changes only scratch IDs, hashes,
paths, timestamps, lineage, and explicit non-authority review notes.

## Derived VM / Sweep Inputs

Derived inputs validate under the existing Strategy Spec and VM/Sweep
validators. Runner-required `approved_for_sweep_planning` and
`frozen_for_sweep_planning` fields are technical scratch compatibility metadata,
not canonical approval, preregistration, or freeze authority.

## Real Runner Integration

The bridge invokes `tools.research_runner.run_offline_sweep` in deterministic
`canonical_15m` fixture mode, writes its validated Result Population-shaped
artifact beneath package scratch, and uses no runner adapter, network, private
endpoint, credential, paper/live, or runtime path.

## Manual Run Reconciliation

After the bridged write run, the same validated inputs are passed through a
second dry-run manual-equivalent invocation. Trial count, variant IDs, outcomes,
core metrics, status counts, committed denominator, and result identity must
match or the bridge fails.

## Denominator Preservation

Every VM row is retained. Native runner outcomes map to the closed bridge ledger
statuses `completed`, `failed`, `invalid`, `pruned`, and `blocked`, while the
original runner outcome remains visible. A denominator equality assertion runs
before packet writes.

## Funding Mode Handling

Default funding mode is `off`, matching merged backtest truth and the runner's
zero-funding 15m fixture behavior. The runner has no explicit funding-on input,
so an approved funding-on request is recorded as blocked and never executed. No
global funding setting is changed.

## Data Availability Guard Handling

Full-history public runs block recent-only, snapshot-only, streaming-only,
vendor-only, and unknown features. Open interest is never reconstructed from
trades; liquidation history requires vendor/captured data; archive-derived taker
flow cannot use the OHLCV fixture and remains blocked because it is not encoded
by the first SMA/stddev draft adapter.

## Review Packet

The scratch review packet includes source/approval metadata, derived inputs,
runner invocation and artifacts, all five denominator counts, reconciliation,
metrics, ledger path, validation/data/funding state, and the explicit statements
`not canonical`, `not evidence`, `not candidate authority`, `not promotion
authority`, `not paper/live readiness`, and `human review required`.

## Adversarial Boundary Tests

Tests cover approval bypass; canonical Strategy Spec, VM, Sweep Plan, Result
Population, and trial-log writes; registration/promotion/freeze; runtime and
protected controls; private/credential/network access; global funding mutation;
evidence suppression/deletion; ToolContext bypass; constrained data; denominator
shrinkage; and output outside the active scratch prefix. Each denied ToolContext
attempt produces a blocked audit record.

## Validation Status

- Bridge, formalizer, experiment-runner, and ToolContext regressions: PASS,
  169 tests.
- Strategy Spec, Result Population, data-availability, and VM/Sweep validator
  tests: PASS, 213 tests.
- Strategy Spec validator: PASS.
- Variant Manifest / Sweep Plan validator: PASS.
- Result Population validator: PASS.
- Data feature availability validator: PASS.
- Query view discovery: PASS, 124 views.
- Full pytest initially completed with 2,068 passed, 1 skipped, 1 failed, and
  6 warnings. The sole failure was the documented isolated-worktree baseline
  `test_default_fixture_mapping_uses_rp_2592_lineage`, because its gitignored
  D4A normalized CSV was absent. After copying that existing local fixture from
  the root checkout into the same gitignored worktree path for validation only,
  the final full run passed: 2,071 passed, 1 skipped, 6 warnings.
- Diff-scope summary: PASS; intended files only and no forbidden-path match.
- `git diff --check`: PASS.
- Ambient Python 3.14 cannot collect runner tests because `pandas` is absent;
  validation uses the repo Python 3.11 virtual environment.

## Boundary Summary

No canonical artifact, schema, validator behavior, query behavior, runner,
backtester, compiler, config, dependency, data, runtime, paper/live, OMS, risk,
reconciliation, capital, broker/exchange, credential, or project-status file is
modified. Scratch Result Population-shaped output has no canonical authority.

## Non-Authority Statement

All bridge inputs, outputs, ledger rows, runner artifacts, and packets are
scratch-only, non-canonical, non-evidence, and human-review-required. They grant
no candidate, ranking, recommendation, promotion, readiness, paper/live,
runtime, risk, capital, or execution authority.
