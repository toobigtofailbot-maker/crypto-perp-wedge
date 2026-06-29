# Baseline Ground-Truth Contract

## Global Rules

Baseline payloads can validate lab plumbing, denominator preservation, negative/no-candidate review packets, dashboard/report rendering, and promotion/crossing rejection behavior.

Baseline payloads cannot become candidates, support paper/live execution, claim edge, authorize canonical crossing, or weaken any protected runtime boundary.

## `known_losing_baseline`

- Purpose: exercise lab handling of a deliberately non-edge, high-cost, gate-failing reference signal.
- Known property: later execution should report losing or materially gate-failing behavior.
- Denominator expectation: every declared variant remains in the denominator; losing rows are retained.
- Gate expectation: overall failure. Any favorable isolated metric is overridden by construction-only provenance.
- OOS/WFO expectation: insufficient or negative; no edge inference.
- Robustness expectation: failing or insufficient; no robustness override of fixture provenance.
- Candidate review expectation: negative fixture review only.
- Crossing expectation: reject by construction.
- Dashboard label: fixture, construction payload, non-promotable, not a candidate.
- Agent loop result: record plumbing behavior only; no rescue, retuning, ranking, or promotion.

## `known_neutral_or_no_trade_baseline`

- Purpose: exercise no-trade, empty-result, and denominator behavior.
- Known property: later execution should produce no trades or insufficient activity under unreachable or near-unreachable SMA / StdDev threshold logic.
- Denominator expectation: no-trade, filtered, data-unavailable, not-attempted, and failed rows stay visible.
- Gate expectation: blocked or failed for insufficient evidence/no signal.
- OOS/WFO expectation: no valid edge inference from no observations or near-zero PnL.
- Robustness expectation: withhold or mark insufficient rather than fabricating confidence.
- Candidate review expectation: no candidate-review packet or negative no-candidate packet only.
- Crossing expectation: reject by construction and for insufficient/no-signal evidence.
- Dashboard label: fixture, no-trade construction payload, non-promotable, not a candidate.
- Agent loop result: record no-signal behavior only.

## `known_degenerate_or_invalid_baseline`

- Purpose: exercise invalid/blocked/fail-closed row accounting without strategy execution.
- Known property: invalid SMA parameter relation must be preserved as invalid/blocked.
- Denominator expectation: invalid/blocked rows remain in the committed denominator.
- Execution-status expectation: fail closed before execution.
- Gate expectation: blocked invalid; no gate pass and no metric synthesis.
- OOS/WFO expectation: no OOS metrics claimed.
- Robustness expectation: invalid status preserved; derived confidence metrics withheld.
- Candidate review expectation: invalid fixture rejected.
- Crossing expectation: reject by construction and invalid status.
- Dashboard label: fixture, invalid construction payload, non-promotable, not a candidate.
- Agent loop result: report invalid denominator preservation only; no repair, mutation, or reroute.

## Forbidden Interpretations

No baseline may be interpreted as a profitable candidate, edge evidence, promotion-ready signal, paper/live input, automatic retuning opportunity, or permission to change protected paths.
