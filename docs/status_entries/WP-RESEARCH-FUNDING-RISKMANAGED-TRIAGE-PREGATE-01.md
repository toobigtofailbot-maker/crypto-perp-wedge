# WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-PREGATE-01

## Status

Complete on branch `research/funding-riskmanaged-triage-pregate-01` from refreshed `origin/main` `2249e6e` after PR #576.

## Objective

Freeze the pre-run approval package for `H-FUNDING-FADE-RISKMANAGED-01`: hypothesis selection, repo-grounded rationale, one-year Stage 1 window, a-priori risk-control ranges, denominator, real-runner reconciliation plan, stop/go criteria, protected-boundary statement, and Karl sign-off packet.

## Repo-Truth Discovery

The prior funding-fade family is scratch-only, non-canonical, and concluded NO-GO under price-PnL signal semantics after preserving all 36 planned rows. Its primary failure was drawdown: every row failed the 20% screen. Funding payments were not wired and `funding_cost_mode` remained off.

Current merged code supports closed ATR-stop Strategy Spec grammar/compiler behavior, max-hold parameter binding, dynamic equity target leverage in the offline runner, and an optional non-canonical vectorbt sidecar. The existing funding formalizer bridge remains narrower than this risk-managed design because it generates only the prior two-exit funding denominator; Stage 1 therefore requires either manually authored scratch runner inputs or a separately authorized adapter-extension package before execution.

## Delivered

- Added `docs/research/H_FUNDING_FADE_RISKMANAGED_TRIAGE_PREGATE.md`.
- Added scratch pre-gate artifacts under `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-PREGATE-01/`.
- Frozen Stage 1 evaluation window: `2024-01-01T00:00:00Z` inclusive through `2025-01-01T00:00:00Z` exclusive, with warmup input beginning no later than `2023-07-05T00:00:00Z`.
- Frozen denominator: 108 rows total, made of 36 same-window no-ATR comparison rows plus 72 ATR-stop rows.
- Frozen variable risk control: ATR stop with lookback `14` and multipliers `2.0` and `3.0`; dynamic equity target leverage fixed at `1.0`.

## Boundary

This package ran no strategy, backtest, sweep, or sidecar triage. It wrote no canonical Result Population, candidate lifecycle record, registry row, promotion/readiness claim, runtime/paper/live path, OMS/risk/reconciliation/order/exchange path, funding accounting change, or private provider/API access. Funding-with-risk-management is recorded as test traffic for the generic Side 12 lab, not a funding-specific lab pivot.
