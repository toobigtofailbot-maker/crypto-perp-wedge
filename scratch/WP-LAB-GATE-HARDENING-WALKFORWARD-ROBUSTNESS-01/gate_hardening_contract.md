# Gate Hardening Contract

## Purpose

This contract hardens WFO/OOS and robustness/MC as standard candidate-gate concepts for future research-lab candidate consideration.

It is non-promoting. It authorizes no strategy execution, backtest, sweep, canonical write, candidate lifecycle write, crossing, promotion, paper/live/runtime work, or protected-path contact.

## Standard Gate Concepts

The standard gate concepts are:

- `wfo_oos_gate`
- `robustness_mc_gate`
- `statistical_diagnostics_gate`
- `denominator_integrity_gate`
- `construction_payload_provenance_gate`
- `candidate_eligibility_gate`

Allowed outcomes are:

- `pass`
- `fail`
- `blocked`
- `insufficient`
- `withheld`
- `not_applicable`
- `reject_by_construction`

## Dominance Rule

`construction_payload=true` or `non_promotable=true` dominates every numeric, WFO/OOS, robustness, MC, PSR, DSR, MinTRL, dashboard, agent, or operator-visible result.

No favorable metric can override construction-only provenance. Any consumer that cannot preserve that dominance rule must stop or record a blocker.

## Denominator Rule

Gate consumers must preserve full declared populations. Failed, invalid, no-trade, blocked, data-unavailable, aborted, filtered, not-attempted, and successful rows remain visible. Winner-only review is forbidden.

## Missing-Input Rule

Missing return paths, per-trade rows, fold outputs, trial-population metadata, MC inputs, or diagnostic formulas produce `withheld`, `insufficient`, or `blocked` states. They do not produce fabricated confidence.

## Baseline Payload Rule

PR #583 baselines are construction payloads only. They may validate plumbing, denominator handling, negative/no-candidate rendering, dashboard/report rendering, and crossing rejection. They may not become candidates, claim edge, authorize paper/live work, or support real canonical crossing.
