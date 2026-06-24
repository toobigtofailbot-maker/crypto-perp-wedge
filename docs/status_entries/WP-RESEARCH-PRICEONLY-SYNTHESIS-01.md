# WP-RESEARCH-PRICEONLY-SYNTHESIS-01 Branch State

## Scope Summary

Creates a neutral evidence synthesis for the BTCUSDT 15m price-only research lane, recent blocked research-machine reach attempts, data-derived frontier status, canonical crossing status, and remaining Side 12 / operator lab gaps.

Primary synthesis: `docs/research/PRICEONLY_SYNTHESIS_2026-06.md`.

Path choice: no existing `docs/research` directory was present, but the package specified `docs/research/PRICEONLY_SYNTHESIS_2026-06.md` as the preferred path, so this package creates that directory and uses the requested path.

## Main / Operator Authorization

Main surfaced the sequence `B then A`; this package implements only B, the neutral synthesis step. It does not implement runner/data-path foundations and does not run edge discovery.

## Repo-Truth Discovery

Discovery is recorded in `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/repo_truth_discovery.md`.

Key findings:

- Local `main` includes PR #557 merge commit `1e85394`.
- BTCUSDT 15m price-only canonical populations include `RP-4492`, `RP-6688`, `RP-7520`, `RP-7134`, `RP-2592`, and `RP-3731`.
- Recent ORB and SMA/stddev research-machine attempts are blocked/non-canonical.
- Donchian adapter work is adapter-smoke only and does not reopen prior Donchian `NO-GO` evidence.
- Taker-flow adapter/downstream reach is blocked by runner/data-path support.
- Canonical crossing remains fixture-only for current real use.
- Side 12 / operator research-lab target state remains incomplete.

## Evidence Classification

The synthesis uses the package vocabulary for research evidence state, outcome state, family class, and authority status. The structured classification lives in `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/evidence_index.json`.

## Price-Only Findings

Committed BTCUSDT 15m price-only families tested or recorded so far have not produced a candidate worth crossing:

- `RP-6688` / `RP-7520`: SMA-band line records no evidence-level edge under current comparable dynamic-sizing measurement.
- `RP-7134`: z-score trend-gated mean reversion frozen screen `NO-GO`.
- `RP-2592`: SMA crossover momentum frozen screen `NO-GO`.
- `RP-3731`: momentum v2 ATR-stop frozen screen `NO-GO`.
- `RP-4492`: descriptive non-authority SMA-distance checkpoint; not candidate-crossing evidence.

This synthesis does not generalize to "price-only can never work" or "BTC 15m is impossible."

## Blocked Research-Machine Attempts

- ORB exit re-spec: blocked by missing ORB formalizer/bridge support and missing MFE/MAE/exit_reason/per-trade/gross diagnostics.
- SMA/stddev fresh edge attempt: blocked because the supported path duplicates concluded `RP-7134`.
- Donchian adapter: completed fixture-backed adapter smoke only; no canonical evidence or fresh Donchian conclusion.
- Taker-flow adapter: blocked before implementation because archive-derived non-OHLCV columns are not runner-consumable through the current path.

## Data-Derived Frontier Status

Data-derived infrastructure exists in parts: compiler data refs, availability labels, taker-flow archive reconstruction, and funding default-off cost-mode support.

Current repo truth does not show a committed equivalent taker-flow canonical RP/REP or GO/NO-GO strategy conclusion. The taker-flow adapter/downstream frontier remains `BLOCKED` / `NOT_TESTED` until runner/data-path support exists.

## Research-Lab Completion Status

The lab has partial surfaces for idea intake, bounded agents, scratch candidate review, fixture-only crossing, walk-forward, robustness, dashboard operator review, and notifications/approvals.

The lab is not complete against the Side 12 / operator target state.

## Side 12 / Operator Lab-Gap Checklist

Structured checklist: `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/lab_gap_checklist.json`.

Summary:

- `not built`: always-on scheduler, autonomous scout, real agent-produced lifecycle packet, first real canonical crossing, daily brief, weekly report, live/paper monitor, paper/live/runtime execution-machine phase.
- `partial`: idea intake, broader adapters, diagnostics, walk-forward/OOS gate reach, Monte Carlo/robustness gate reach, dashboard breadth, notifications/approvals, regime/parameter advisor.
- `built for one path only`: generic downstream robustness/candidate-review reach.
- `blocked by current infrastructure`: full data-derived support and runner/data path for non-OHLCV columns.

## Canonical Crossing Status

`WP-AGENT-CANONICAL-CROSSING-BUILD-01` is fixture-only. No real canonical crossing has been executed. Current repo truth contains no real candidate-review packet worth crossing.

## Validation Status

Validation results are recorded in `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/validation_summary.txt`.

- `python -m tools.research_query.run --list-views`: PASS, 124 views listed.
- `python -m tools.registry.validate_candidate_registry`: PASS.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python -m tools.registry.validate_data_feature_availability`: PASS.
- `python tools/dev/diff_scope_summary.py`: PASS; intended docs/scratch files only and no forbidden-path matches.
- `git diff --check`: PASS.
- JSON scratch files: PASS.
- Full pytest: not passing evidence. Ambient Python failed collection because dependencies are absent; repo virtualenv full pytest timed out after 20 minutes with no failure details emitted.

## Boundary Summary

No strategy run, backtest, canonical Result Population write, canonical Strategy Spec, Variant Manifest, Sweep Plan, trial log, candidate registry write, lifecycle write, crossing output, promotion/freeze/registration, paper/live/runtime path, OMS/risk/reconciliation/capital path, broker/exchange/order path, provider/API/network path, compiler, runner, backtester, data ingestion, schema, validator, or query behavior changed.

Changed files are limited to:

- `docs/research/PRICEONLY_SYNTHESIS_2026-06.md`
- `docs/status_entries/WP-RESEARCH-PRICEONLY-SYNTHESIS-01.md`
- `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/*`

## Non-Authority Statement

This package is docs/evidence synthesis only. It creates no candidate, ranking, recommendation, readiness, promotion, lifecycle, crossing, paper/live/runtime, risk, capital, broker/exchange, or execution authority.

## Open Decision Surfaces

Main may choose whether to commit to runner/data-path work for data-derived families.

Main may choose whether to resume taker-flow/funding adapter work after runner/data-path support exists.

Main may choose whether to add more price-only adapters despite the current synthesis.

Main may choose whether to expand dashboards/reporting/operator surfaces before additional research execution.

Main may choose whether to hold canonical crossing until a real candidate-review packet exists.
