# WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-RUN-01

## Status

Blocked before strategy execution on branch `research/funding-riskmanaged-triage-run-01` from refreshed `origin/main` `5cdc2289311d6ee45ff6b04c68815c939e154d11` after PR #577.

## Frozen Packet Source

The package read the merged frozen packet from `WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-PREGATE-01`. Integrity checks confirmed `H-FUNDING-FADE-RISKMANAGED-01`, the `2024-01-01T00:00:00Z` to `2025-01-01T00:00:00Z` Stage-1 window, warmup required no later than `2023-07-05T00:00:00Z`, planned denominator `108`, signal retuning forbidden, and risk layer status `frozen_before_execution`.

## Execution Route

No strategy run executed. The manually authored scratch Strategy Spec / Variant Manifest / Sweep Plan route could not honestly execute the frozen Stage-1 denominator through the current repo-owned runner without code or data-path work outside package authority.

Primary blocker: `tools/research_runner/run_offline_sweep.py` has no authorized route that compiles the signal with the required warmup prefix while restricting reported metrics to the frozen 2024 evaluation window. The normal canonical sweep scores the full supplied frame, and the existing walk-forward path slices before compiling/backtesting, which does not preserve warmup state for OOS-only scoring.

Secondary blockers: current `exit_logic.atr_stop` grammar is parent-spec scoped rather than a per-row VM axis, requiring multiple scratch parent spec sets or an authorized wrapper to preserve the single 108-row denominator; the active worktree also lacked the ignored runner-consumable BTCUSDT 15m funding-feature CSV needed for declared `funding_rate` canonical-15m execution.

## Denominator Result

Planned rows: `108`. Complete rows: `0`. Blocked rows: `108`. Failed, invalid, and missing rows: `0`. Winner-only reporting did not occur.

## Verdict

Decision: `blocked`. This is not a hypothesis NO-GO and not a continue signal. Stage 2 is not authorized here.

## Boundary

No canonical Result Population, candidate registry/lifecycle record, Strategy Spec, Variant Manifest, Sweep Plan, result population, data, runner, compiler, schema, validator, query-layer, `lib/`, runtime, paper/live, OMS/risk/reconciliation/order/exchange, funding accounting, config, private provider/API, or credential path was changed. No vectorbt sidecar preview was used.

## Validation Summary

Validation was limited to repo-truth inspection and scope/diff validation because no executable scratch inputs or run outputs were produced. Package artifacts are under `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-RUN-01/**` plus this status entry.
