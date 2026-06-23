# WP-AGENT-ROBUSTNESS-DIAGNOSTICIAN-01 Repo-Truth Discovery

## Base and bridge contract

- Base: `b69a918`, the PR #546 merge commit.
- The bridge writes generated outputs under
  `scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/<run_id>/`.
- `human_review_packet.json` binds the runner artifact and denominator ledger
  paths, source bridge run ID, funding mode, validation state, data-availability
  warnings/blockers, and non-authority flags.
- The runner artifact is a validator-compatible, scratch Result
  Population-shaped JSON containing one `variant_result_rows` entry per
  committed variant.
- `denominator_ledger.json` preserves every trial as `completed`, `failed`,
  `invalid`, `pruned`, or `blocked`, retaining the native runner outcome,
  parameters, reason, funding mode, and runner artifact lineage.

## Prerequisite artifact setup

Generated bridge outputs are scratch run products, not committed prerequisites.
The package tests invoke the merged `FormalizerRunnerBridge` helper against its
supported STRAT-SPEC-0003 / VM-0003 / SWEEP-PLAN-0003 and local OHLCV fixture
path, then pass the resulting real-runner packet, Result Population artifact,
and ledger to the diagnostician. Runtime callers supply the same four paths
directly; the production diagnostician has no fixture-generator dependency.

## Existing robustness and walk-forward tools

- `tools/robustness/seeded_advisory_mc.py` provides deterministic aggregate
  variant-metric bootstrap confidence intervals, parameter sensitivity, and
  explicit missing per-trade handling. The diagnostician reuses its bounded
  deterministic computation over already ToolContext-read payloads.
- `tools/robustness/robustness_depth.py` confirms that per-trade resampling must
  use real trade rows and that missing trade rows are an input gap.
- `tools/walkforward/purged_folds.py` can build purged/embargoed fold manifests,
  but bridge Result Population rows contain no fold-compatible fields. The
  diagnostician therefore reports `missing_fold_inputs` and queues follow-up;
  it does not synthesize folds.

## Supported aggregate diagnostics

- Completed runner rows expose finite per-variant metrics such as `return_pct`,
  `pnl`, `drawdown`, `sharpe`, `trade_count`, `win_rate`, `fees`, `funding`,
  `slippage`, and `exposure` where computed.
- Seeded bootstrap confidence intervals can operate on those completed rows
  without canonical writes.
- Bridge ledger `params` provides the variant-to-parameter mapping required for
  aggregate parameter sensitivity.
- Metrics are computed only from eligible completed rows, while the complete
  source denominator and every skipped-row reason remain in the review packet.

## Missing-data boundaries

- Bridge outputs do not contain real per-trade rows. Per-trade resampling is
  reported as `QUEUE_PER_TRADE_INSTRUMENTATION`; no rows are fabricated.
- Bridge outputs do not contain OOS/walk-forward fold inputs. The diagnostic is
  reported as `missing_fold_inputs`.
- PR #546 currently executes funding-off only. Funding stress is explicitly not
  performed when `funding_mode.requested` is `off`; funding-on blocked state or
  missing aggregate funding inputs remain visible.
- OI recent-only, vendor-only, liquidation-history, and other source warnings
  are propagated verbatim. OI is never treated as reconstructable from trades.

## Result validation and denominator integrity

- The existing Result Population validator accepts the scratch runner artifact
  when supplied the bridge-derived scratch Strategy Spec, Variant Manifest, and
  Sweep Plan directories. No schema or validator change is needed.
- Denominator integrity is independently checked across the review packet,
  ledger counts, declared row count, runner row count, and exact variant-ID set.
  A mismatch routes through the hard-blocked `evidence_suppression` action.

## ToolContext

- Gate: `tools/agent_sandbox/tool_context.py`.
- Policy: `tools/agent_sandbox/permissions.py`.
- The existing `robustness_diagnostician` role is used.
- Reads are limited to its active scratch prefix, PR #546 bridge output prefix,
  existing non-secret research/fixture paths, and allowed documentation.
- Writes and `run_scratch_robustness_diagnostic` are limited to
  `scratch/WP-AGENT-ROBUSTNESS-DIAGNOSTICIAN-01/outputs/`.
- Canonical writes, candidate lifecycle, paper/live/runtime, protected paths,
  credentials/private endpoints, funding mutation, evidence deletion,
  fabricated per-trade data, provider-memory authority, and network access
  remain hard blocked and audited.

## Repo-truth adjustments

- The first attempt incorrectly required generated PR #546 scratch artifacts to
  pre-exist in a clean worktree. They are correctly generated during test/demo
  validation through the merged bridge and are not committed.
- The robustness approval marker is a separate, source-run-bound operator gate;
  it is not evidence, promotion, readiness, or paper/live approval.
