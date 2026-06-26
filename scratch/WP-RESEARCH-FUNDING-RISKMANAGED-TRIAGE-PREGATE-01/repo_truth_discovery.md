# Repo-Truth Discovery

## Base

- Branch: `research/funding-riskmanaged-triage-pregate-01`.
- Base: refreshed `origin/main` at `2249e6e`, merge commit for PR #576.
- Package class: docs/scratch-only pre-registration and no-run approval gate.

## Files and Surfaces Inspected

Required repo-truth surfaces inspected:

- `docs/research/LAB_COMPLETION_MAP.md`
- `docs/research/LAB_COORDINATOR_STATE_MODEL.md`
- `docs/research/LAB_STATE_MODEL_COVERAGE_AUDIT.md`
- `docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md`
- `docs/research/PRICEONLY_SYNTHESIS_2026-06.md`
- `docs/status_entries/WP-LAB-COVERAGE-GAP-CLOSE-01.md`
- `scratch/WP-LAB-COVERAGE-GAP-CLOSE-01/post_gap_summary.json`
- `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/**`
- `scratch/WP-RESEARCH-FUNDING-CARRY-01/**`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/**`
- `research/result_populations/**`
- `research/candidate_registry.jsonl`
- `tools/lab_state/run.py`
- `tools/lab_dashboard/data_model.py`
- `tools/lab_approval_queue/queue_model.py`

Targeted implementation/capability surfaces inspected:

- `tools/research_runner/run_offline_sweep.py`
- `tools/research_runner/spec_signal_compiler.py`
- `tools/research_agents/formalizer_runner_bridge.py`
- `tools/research_agents/idea_formalizer_agent.py`
- `tools/registry/validate_strategy_specs.py`
- `tools/registry/validate_result_populations.py`
- `tools/sidecars/vectorbt_triage_sidecar.py`
- `lib/backtest.py`
- relevant tests for ATR stop, funding bridge, runner sizing, and validators

## Fact: Funding-Fade Evidence Exists

`docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md` and `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json` record `H-FUNDING-RATE-POSITIONING-FADE-01 = NO-GO under the tested price-P&L funding-rate signal interpretation`.

The prior family preserved its full 36-row denominator:

- 3 funding-percentile lookbacks: 30d, 90d, 180d;
- 2 symmetric tail pairs: `0.10/0.90`, `0.05/0.95`;
- 2 exit modes: `fixed_max_hold_only`, `midline_reversion_or_max_hold`;
- 3 max-hold values: `16`, `32`, `96` bars.

The prior primary failure was drawdown, not missing denominator evidence:

- fixed max-hold full-history drawdown range: 85.68% to 100%;
- midline-or-max-hold full-history drawdown range: 80.72% to 100%;
- all 36 rows failed the 20% primary drawdown screen.

## Inference: Why This Is the Selected First Hypothesis

Funding-with-risk-management is selected first because the prior family has a clear, repo-visible failure mode that a risk layer can test without retuning the signal: the contrarian funding signal was already frozen, the full denominator was preserved, and drawdown was the dominant blocker.

This is narrower and more auditable than restarting price-only exploration, taker-flow work, or open-interest work:

- price-only evidence already contains multiple concluded NO-GO or blocked attempts, and the price-only synthesis does not identify a ready first run;
- taker-flow remains blocked by runner/data support according to the current price-only/data-derived synthesis;
- open-interest is not represented as a runner-ready full-history hypothesis in the inspected current repo truth.

## Fact: Signal Parameters Frozen From Prior Evidence

The signal parameters remain:

- `funding_lookback_bars`: `2880`, `8640`, `17280`;
- coupled entry tails: lower/upper `0.10/0.90`, `0.05/0.95`;
- `exit_mode`: `fixed_max_hold_only`, `midline_reversion_or_max_hold`;
- `max_hold_bars`: `16`, `32`, `96`;
- contrarian direction only;
- BTCUSDT 15m primary timeframe.

No signal threshold, direction, lookback family, exit family, or timeframe is retuned in this pre-gate.

## Fact: Risk-Control Primitives Available

Current merged repo truth supports the following relevant primitives without modifying code:

- ATR stop: `tools/research_runner/spec_signal_compiler.py` supports closed `exit_logic.atr_stop`, including ATR lookback, ATR multiplier, next-bar-open entry reference, close evaluation, and bar-close timing. `tools/registry/validate_strategy_specs.py` validates that closed grammar.
- Max hold: `exit_logic.max_holding_period` supports parameter-bound integer bars. The prior funding specs already used this shape.
- Dynamic sizing: `lib/backtest.py` and `tools/research_runner/run_offline_sweep.py` support opt-in `dynamic_equity_target_leverage` with `target_leverage`.
- Vectorbt sidecar: `tools/sidecars/vectorbt_triage_sidecar.py` exists, but is non-canonical, optional, bounded, and cannot confirm finalists.

## Decision: Expressibility

The risk-managed hypothesis can be expressed without runner/backtester/funding-PnL changes if Stage 1 uses manually authored scratch Strategy Spec / Variant Manifest / Sweep Plan inputs validated by existing validators and executed through `tools.research_runner.run_offline_sweep`.

The existing funding formalizer bridge is not sufficient by itself for this exact risk-managed denominator because it hard-codes the prior funding adapter path into two exit-mode specs and derives the old 36-row family. That is an adapter-generation gap, not a runner/backtester capability blocker.

## Decision: Funding-PnL Boundary

Stage 1 can proceed only as a price-PnL funding-rate signal triage. It must keep funding payments/accounting out of scope. If interpreting the result requires enabling or changing funding PnL/accounting, Stage 1 must stop and report blocked.

## Decision: Vectorbt

Vectorbt may be used only as an optional sidecar preview. It cannot write canonical evidence, cannot rank/select finalists as authority, and cannot replace the real runner. Any sidecar-observed continue signal must be reconciled against the repo-owned runner before a GO decision is trusted.

## Implementation Gap

No code change is required for the pre-gate package. The exact Stage 1 execution route still needs Karl approval:

1. manually authored scratch runner inputs using existing grammar, validators, and offline runner; or
2. a separately authorized adapter-extension work package to make the funding bridge generate the risk-managed denominator.

Either route must preserve the 108-row planned denominator and write only scratch outputs unless a later package explicitly authorizes canonical writes.
