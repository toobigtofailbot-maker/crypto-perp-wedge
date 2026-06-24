# WP-RESEARCH-FUNDING-FADE-CONCLUDE-01

## Scope

Docs/evidence synthesis package to conclude `H-FUNDING-RATE-POSITIONING-FADE-01` as NO-GO in repo-visible records after PR #563 merged. The package performed no new research run and created no canonical artifact, candidate lifecycle entry, crossing, runtime change, funding-accounting change, or protected-path change.

## Base And Branch

- Base: refreshed `origin/main` at merge commit `2b2c3d8` (PR #563).
- Branch: `research/funding-fade-conclude-01`.

## Repo-Truth Discovery

- `docs/status_entries/WP-RESEARCH-FUNDING-CARRY-02.md` records the completed upstream scratch research package.
- The upstream denominator is 36 planned / 36 complete / 0 failed / 0 invalid / 0 blocked / 0 pruned.
- Result populations are `RP-2009` (`fixed_max_hold_only`) and `RP-7592` (`midline_reversion_or_max_hold`), both scratch-only and non-canonical.
- The evidence uses BTCUSDT 15m data with 220,128 bars and a `funding_rate` column staged from PR #560 local ignored data.
- The tested interpretation is price-P&L funding-rate signal evidence only. Funding payments were not wired and `funding_cost_mode` remained off.
- All 36 rows failed the 20% drawdown screen. Full-history drawdown ranged from 85.68% to 100% for `fixed_max_hold_only` and from 80.72% to 100% for `midline_reversion_or_max_hold`.
- Dry-run-only OOS did not rescue the result; OOS drawdowns remained above the primary screen.
- Descriptive robustness reports were produced, unavailable statistics were withheld, and per-trade Monte Carlo was blocked because real per-trade rows are unavailable.
- No candidate-review packet was generated, no candidate was registered, and no canonical crossing occurred.

## Delivered Files

- `docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md`
- `docs/status_entries/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01.md`
- `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/parallel_touched_file_forecast.md`
- `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/repo_truth_discovery.md`
- `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json`
- `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/validation_summary.txt`
- `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/main_report_back_guardrail.txt`

## Conclusion

`H-FUNDING-RATE-POSITIONING-FADE-01 = NO-GO under the tested price-P&L funding-rate signal interpretation.`

This conclusion is not a general verdict on funding-signal families, is not a broad predictive-value judgment about funding, and does not claim funding-payment or carry-P&L coverage.

## Drift Guardrail

This NO-GO does not automatically authorize another edge-search cycle. Additional data-derived families or funding variants require separate Main/operator authorization. Near-term lab-completion work is separate from new hypothesis search.

## Boundary Check

Changed files are limited to this status entry, the funding-positioning-fade synthesis document, and `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/**`.

No `tools/**`, `tests/**`, `schemas/**`, research canonical artifacts, candidate registry, Result Population validator, candidate-review logic, walk-forward/OOS code, replay/normalization code, `docs/project_status.md`, runtime, paper/live, OMS, risk, reconciliation, capital, broker/exchange, provider/API/network, dashboard, scheduler, or large tracked data files were changed.

## Validation

Recorded in `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/validation_summary.txt`.
