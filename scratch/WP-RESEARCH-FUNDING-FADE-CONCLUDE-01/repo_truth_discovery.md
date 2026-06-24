# Repo-Truth Discovery

## Base

- Worktree branch: `research/funding-fade-conclude-01`.
- Base: refreshed `origin/main` at `2b2c3d8`, merge commit for PR #563.
- Target synthesis/status files did not exist before this package.

## Required Upstream Artifacts Inspected

- `docs/status_entries/WP-RESEARCH-FUNDING-CARRY-02.md`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/denominator_manifest.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/runner_result_summary.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/metrics_summary.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/robustness_summary.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/walk_forward_summary.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/no_candidate_review_packet_reason.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/rp_replay_harness_report.json`

Additional relevant upstream artifacts inspected:

- `scratch/WP-RESEARCH-FUNDING-CARRY-02/repo_truth_discovery.md`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/funding_pnl_boundary_note.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/pre_registered_hypothesis.md`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo_summary.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/main_report_back_guardrail.txt`

## Search Discovery

The required term search was run over `docs`, `research`, `scratch`, and `tools` markdown/json/python surfaces for:

`WP-RESEARCH-FUNDING-CARRY-02|H-FUNDING-RATE-POSITIONING-FADE-01|RP-2009|RP-7592|funding_rate_positioning_fade_v1|NO-GO|drawdown|funding_rate|price-P&L|funding_cost_mode|candidate_review|canonical crossing`

Relevant funding-fade hits confirmed:

- `docs/status_entries/WP-RESEARCH-FUNDING-CARRY-02.md` records the completed scratch funding-rate positioning-fade run.
- `docs/status_entries/WP-RESEARCH-FUNDING-CARRY-01.md` records the prior pre-registration and boundary framing.
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/**` contains the denominator, metrics, OOS, robustness, Monte Carlo, no-packet reason, and replay evidence.
- Code surfaces contain support for `funding_rate_positioning_fade_v1` and candidate-review/crossing machinery, but this package did not modify them.

## Facts Carried Forward

- Hypothesis: `H-FUNDING-RATE-POSITIONING-FADE-01`.
- Conclusion basis: scratch-only price-P&L funding-rate signal evidence.
- Data: BTCUSDT 15m, 220,128 bars, `funding_rate` column staged from PR #560 local ignored data.
- Populations: `RP-2009` (`fixed_max_hold_only`) and `RP-7592` (`midline_reversion_or_max_hold`).
- Denominator: 36 planned / 36 complete / 0 failed / 0 invalid / 0 blocked / 0 pruned.
- Primary failure: all rows failed the 20% drawdown screen.
- Full-history drawdown: 85.68% to 100% for `fixed_max_hold_only`; 80.72% to 100% for `midline_reversion_or_max_hold`.
- OOS: dry-run-only one-window OOS did not rescue the result; OOS drawdowns remained above the primary screen.
- Robustness: descriptive reports produced; unavailable statistics withheld; per-trade Monte Carlo blocked because real per-trade rows are unavailable.
- Candidate/crossing: no candidate-review packet, no candidate registration, no canonical crossing.
- Funding boundary: funding payments were not wired, `funding_cost_mode` was off, and this was not a complete funding-carry-P&L test.

## Decision

Continue with docs/evidence-only NO-GO conclusion. No parallel overlap detected inside the owned file set.
