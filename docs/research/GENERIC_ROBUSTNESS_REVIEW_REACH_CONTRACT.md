# Generic Robustness Review Reach Contract

## Scope

This contract defines a family-neutral review reach surface for downstream robustness and candidate-review infrastructure. It is descriptive only. It creates no strategy run, canonical crossing, candidate lifecycle write, ranking, recommendation, readiness, promotion, paper/live, runtime, OMS, risk, reconciliation, funding P&L, or capital authority.

The contract applies to supported research families that can expose bounded evidence through existing research artifacts, scratch artifacts, or future separately authorized artifacts. Family labels are metadata, not dispatch keys. Consumers must not special-case SMA, Donchian, funding, or any other family unless a later package explicitly authorizes a family adapter.

## Required Input Fields

Every review-reach record must carry:

- `strategy_family_label`: normalized family label such as `sma_crossover`, `donchian_breakout`, or `funding_rate_positioning_fade`.
- `evidence_class`: one of `canonical_result_population`, `noncanonical_scratch_result_population`, `scratch_diagnostic`, or `blocked_unavailable`.
- `result_population_identity`: Result Population ID, path, and identity hash when available. Scratch populations must be labeled non-canonical.
- `denominator_manifest`: planned, completed, failed, invalid, pruned, blocked, and total row counts; denominator shrinkage is forbidden.
- `primary_risk_screen`: primary eligibility/risk screen outcome and source.
- `drawdown_screen`: drawdown-specific screen outcome and source.
- `return_sharpe_metrics`: return, Sharpe, and related metric availability without inventing missing values.
- `oos_gate_status`: OOS gate status if available; otherwise an unavailable reason code.
- `robustness_status`: robustness diagnostics status, skipped diagnostics, and unavailable-stat reason codes.
- `unavailable_stat_reason_codes`: explicit codes for PSR, DSR, MinTRL, per-trade, OOS, funding-stress, or other unavailable statistics.
- `candidate_review_eligibility_reason_codes`: explicit eligibility, no-packet, or blocked reason codes.
- `noncanonical_canonical_state`: `canonical`, `noncanonical_scratch`, or `blocked_unavailable`.

## Required Output Fields

Every review-reach output must distinguish:

- `candidate_review_packet_created`: boolean. `true` only means a review packet was produced under its own non-authority boundary.
- `no_candidate_review_packet_reason`: null or an object with `code`, `source`, and `detail`. Use this when evidence is available and review is intentionally not created, for example a NO-GO primary screen.
- `blocked_review_reason`: null or an object with `code`, `source`, and `detail`. Use this when the review cannot be evaluated because required inputs are unavailable or a sequencing dependency is unmet.
- `advisory_only_summary`: short descriptive summary. It must not recommend, rank, promote, approve, or declare readiness.

`no_candidate_review_packet_reason` and `blocked_review_reason` are mutually exclusive.

## Reason Codes

### No-Packet Codes

- `NO_GO_PRIMARY_RISK_SCREEN_FAILED`: evidence exists and the primary screen failed.
- `NO_GO_DRAWDOWN_SCREEN_FAILED`: evidence exists and the drawdown screen failed.
- `NO_GO_RETURN_SHARPE_SCREEN_FAILED`: evidence exists and return/Sharpe screen failed.
- `NO_GO_DENOMINATOR_INTEGRITY_FAILED`: evidence exists but denominator integrity failed; do not create a packet.

### Blocked Codes

- `BLOCKED_REPLAY_CONTRACT_UNAVAILABLE`: normalized replay evidence is required but not available in merged repo truth.
- `BLOCKED_OOS_GATE_UNAVAILABLE`: OOS gate contract or source artifact is unavailable.
- `BLOCKED_DENOMINATOR_MANIFEST_UNAVAILABLE`: denominator cannot be verified.
- `BLOCKED_RESULT_POPULATION_UNAVAILABLE`: Result Population identity or path is unavailable.
- `BLOCKED_REQUIRED_STAT_INPUTS_UNAVAILABLE`: required inputs for a requested statistic are unavailable.
- `BLOCKED_PARALLEL_SEQUENCE`: active parallel ownership prevents a safe edit or evaluation.

### Unavailable-Stat Codes

- `UNAVAILABLE_PSR_MISSING_RETURN_SERIES`: PSR is withheld because no real chronological return series is available.
- `UNAVAILABLE_DSR_MISSING_TRIAL_CONTEXT`: DSR is withheld because required trial-count or benchmark context is unavailable.
- `UNAVAILABLE_MINTRL_MISSING_METHOD_CONTRACT`: MinTRL is withheld because the method contract or required inputs are unavailable.
- `UNAVAILABLE_PER_TRADE_ROWS_MISSING`: per-trade robustness is withheld because no real per-trade rows are available.
- `UNAVAILABLE_OOS_FOLDS_MISSING`: OOS/walk-forward statistics are withheld because no real fold inputs are available.
- `UNAVAILABLE_FUNDING_PNL_NOT_AUTHORIZED`: funding P&L stress is withheld because funding accounting is not authorized in the evidence package.

## Family-Neutral Review Rules

1. Use declared family metadata only for labeling and grouping.
2. Require complete denominator preservation before any packet is eligible.
3. Treat non-canonical scratch evidence as advisory only.
4. Treat missing statistics as unavailable with reason codes; do not synthesize placeholders.
5. A failed primary risk screen or drawdown screen produces `candidate_review_packet_created=false` with `no_candidate_review_packet_reason`.
6. Missing replay/OOS/denominator/Result Population inputs produce `blocked_review_reason`, not a NO-GO.
7. Candidate lifecycle writes are out of scope. A candidate-review packet, if created by later authorized tooling, is not registration, crossing, approval, readiness, or promotion.

## Current Repo-Truth Binding

PR #563 (`WP-RESEARCH-FUNDING-CARRY-02`) provides the first funding-rate family scratch population evidence. It remains non-canonical and concluded NO-GO under its own package because every row failed the primary drawdown screen. Its robustness reports withheld PSR, DSR, and MinTRL rather than fabricating missing inputs. No candidate-review packet was generated.

Existing merged candidate-review and robustness agents are scratch-only and non-authoritative. They do not provide a generic lifecycle write path and must not be used here as promotion, readiness, or candidate authority.
