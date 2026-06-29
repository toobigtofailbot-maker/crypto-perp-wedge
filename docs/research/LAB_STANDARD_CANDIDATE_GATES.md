# Lab Standard Candidate Gates

## Status And Authority

This document defines standard research-lab candidate-gate semantics for future candidate consideration.

It is descriptive and non-promoting. It does not run strategies, run backtests, run sweeps, compute robustness statistics, write canonical Result Populations, mutate trial logs, register candidates, execute crossing, approve readiness, promote anything, or touch paper/live/runtime, OMS, risk, reconciliation, broker, exchange, order, data, credential, or provider/API paths.

## Standard Gate Concepts

The standard candidate-gate concepts are:

- `wfo_oos_gate`
- `robustness_mc_gate`
- `statistical_diagnostics_gate`
- `denominator_integrity_gate`
- `construction_payload_provenance_gate`
- `candidate_eligibility_gate`

Allowed gate outcomes are:

- `pass`
- `fail`
- `blocked`
- `insufficient`
- `withheld`
- `not_applicable`
- `reject_by_construction`

Existing narrower contracts, such as `docs/research/WALKFORWARD_OOS_GATE_CONTRACT.md`, retain their current artifact-specific decision vocabulary. This document defines the broader standard vocabulary future gate consumers should preserve.

## WFO/OOS Gate

WFO/OOS is a standard gate concept before future candidate consideration.

Future protocols must preserve chronological ordering, declare train/test split identity, declare purge/embargo posture or why it is not applicable, preserve full fold denominators, and keep failed, blocked, invalid, no-trade, data-unavailable, not-attempted, and successful folds visible.

WFO/OOS cannot promote construction payloads. A favorable OOS fold or aggregate metric cannot override construction-only or non-promotable provenance.

## Robustness / MC Gate

Robustness / MC is a standard gate concept before future candidate consideration.

Future PSR, DSR, MinTRL, MC, bootstrap, per-trade, return-path, or fold-based diagnostics may pass, fail, withhold, block, or mark insufficient depending on available inputs.

Missing per-trade rows, return paths, fold outputs, trial-population metadata, or required method contracts must produce `withheld`, `insufficient`, or `blocked`, not fabricated confidence.

Robustness must operate on full populations. Winner-only robustness review is forbidden.

## Denominator Integrity Gate

Full declared populations must remain visible. Failed, invalid, no-trade, blocked, data-unavailable, aborted, filtered, not-attempted, and successful rows count in denominator posture.

Any gate consumer that shrinks a denominator to winners, successful rows only, rows with convenient data, or rows with favorable outcomes must fail or block.

## Construction Payload Provenance Gate

`construction_payload=true` or `non_promotable=true` dominates every numeric or diagnostic result.

When either flag is present:

- candidate eligibility is `reject_by_construction`;
- crossing is `reject_by_construction`;
- paper/live eligibility is false;
- edge claims are forbidden;
- metric overrides are forbidden;
- rescue or retuning interpretations are forbidden.

## PR #583 Baseline Payload Expectations

The baseline construction payloads from `WP-LAB-BASELINE-PAYLOAD-DEFINE-01` are fixtures for plumbing and guardrail validation only.

`known_losing_baseline`:

- WFO/OOS: `fail` or `insufficient`;
- robustness/MC: `fail`, `insufficient`, or `withheld`;
- candidate eligibility: `reject_by_construction`;
- crossing: `reject_by_construction`.

`known_neutral_or_no_trade_baseline`:

- WFO/OOS: `blocked` or `insufficient` for no-signal/no-trade posture;
- robustness/MC: `withheld` or `insufficient`;
- candidate eligibility: `reject_by_construction`;
- crossing: `reject_by_construction`.

`known_degenerate_or_invalid_baseline`:

- WFO/OOS: `blocked` / invalid with no metrics claimed;
- robustness/MC: `withheld` / invalid;
- candidate eligibility: `reject_by_construction`;
- crossing: `reject_by_construction`.

No favorable metric can override those expectations.

## Deferred Implementation

Deferred and unauthorized here:

- schema-level construction/non-promotable provenance fields;
- dedicated fixture-artifact schema or validator;
- actual WFO/OOS runner execution;
- actual MC, bootstrap, PSR, DSR, or MinTRL computation;
- candidate-review packet generation using baseline fixtures;
- crossing guard implementation;
- agent-loop exercise;
- dashboard/reporting proof for baseline fixtures;
- paper/live/runtime or protected-path work.
