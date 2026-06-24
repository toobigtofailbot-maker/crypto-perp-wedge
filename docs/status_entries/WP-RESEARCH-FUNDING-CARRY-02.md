# WP-RESEARCH-FUNDING-CARRY-02 Branch State

## Scope Summary

Run the frozen 36-row funding-rate positioning-fade hypothesis as non-canonical scratch research after local-only staging of the PR #560 ignored funding feature CSV.

## Main / Operator Direction

The operator authorized local staging or deterministic rematerialization followed by an unchanged retry. Canonical writes, crossing, candidate lifecycle, funding P&L, runtime, paper/live, and protected trading paths remained forbidden.

## Repo-Truth Discovery

PR #562 is merged at base `d08da05`. The staged PR #560 CSV has 220,128 rows, range `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`, and matching SHA256 `70cbe2040c8fb5987b2971a13c8bd4f66e91152331d5b641d684673364be3931`. Existing grammar represents the two exit modes through two validated 18-row spec/VM/sweep sets without compiler changes.

## Pre-Registered Hypothesis

`H-FUNDING-RATE-POSITIONING-FADE-01` uses 30/90/180-day rolling empirical funding percentiles, symmetric 0.10/0.90 and 0.05/0.95 entry tails, midline-or-max-hold and fixed-max-hold exit modes, and 16/32/96-bar maximum holds. Direction is contrarian only. No post-hoc changes occurred.

## Funding P&L Boundary

This is a price-P&L funding-rate signal test. Existing fees and slippage are enabled. Funding payments are not wired, `funding_cost_mode` remains off, and no funding accounting changed.

## Formalizer / Bridge Implementation

The formalizer adds one closed `funding_rate_positioning_fade_v1` adapter. The bridge accepts only this family under the funding WP, emits two validated 18-row artifact sets, invokes the existing offline runner, combines the denominator, and preserves all row outcomes. The sandbox grants the bridge read access only to the exact expected ignored funding CSV under this WP.

## Runner Result

Both scratch populations completed: `RP-2009` for fixed-max-hold and `RP-7592` for midline-or-max-hold. All 36 rows completed. Bridge/direct reconciliation passed independently for both populations.

## Full Denominator

The combined denominator is 36 planned, 36 complete, 0 failed, 0 invalid, 0 blocked, and 0 pruned. `denominator_preserved=true`; poor rows remain present.

## Metrics and Drawdown Screen

Classification is NO-GO. Full-history drawdown ranges from 85.68% to 100% for fixed-max-hold and 80.72% to 100% for midline-or-max-hold. Every row fails the primary 20% drawdown screen. Sharpe and return outliers do not override drawdown.

## Walk-Forward / OOS Status

The existing dry-run-only hook ran one non-overlapping window with 105,120 IS bars and 35,040 later OOS bars for all 36 variants. OOS minimum drawdown is 25.93% for fixed-max-hold and 29.26% for midline-or-max-hold; 7 of 36 OOS rows have positive P&L. No canonical walk-forward artifact was written.

## Robustness / Monte Carlo Status

Repo-native descriptive robustness reports preserve both 18-row denominators and withhold PSR, DSR, and MinTRL for missing inputs. Seeded 1,000-sample advisory bootstrap reports show mean drawdown near 98%–99%. Per-trade Monte Carlo is blocked because real per-trade rows are absent; none were fabricated. Parameter sensitivity is unavailable from the scratch RP lineage mapping.

## Candidate-Review Packet Status

No packet was generated because all 36 rows fail the existing primary drawdown screen. No candidate was registered and no crossing occurred.

## RP Replay / Determinism Harness

The report pins the input, Strategy Spec, VM, Sweep Plan, runner commit, Result Population, and normalized metrics hashes. Bridge/direct reruns match trial counts, variant IDs, outcomes, metrics, status counts, denominators, and result identities for both exit modes. This is scratch replay evidence only.

## Validation Status

Focused funding formalizer/bridge tests and the package-required compiler, runner, validator, registry, query, diff, and full-suite checks are recorded in `scratch/WP-RESEARCH-FUNDING-CARRY-02/validation_summary.txt`.

## Boundary Summary

No canonical research artifacts, trial log, candidate registry, crossing, funding P&L, runner/backtester semantics, runtime, paper/live, OMS, risk, reconciliation, capital, credentials, provider/API/network code, adoption PoC, dashboard, scheduler, notification, or large tracked data changed.

## Non-Authority Statement

All produced evidence is scratch-only, non-canonical, not crossed, not candidate authority, not paper-ready, not live-ready, and not execution authority.

## Research-Lab Completion Note

This WP adds the first completed funding-rate family population, local staging record, robustness summaries, and scratch replay proof. The Side 12 / operator research-lab target state remains incomplete. External adoption remains deferred in this WP.

## Open Decision Surfaces

- Whether future research tests another separately pre-registered data-derived family.
- Whether a future package adds real per-trade instrumentation or a reusable multi-population replay contract.
- Whether the Side 12 / operator target-state gaps are addressed through separately authorized packages.
