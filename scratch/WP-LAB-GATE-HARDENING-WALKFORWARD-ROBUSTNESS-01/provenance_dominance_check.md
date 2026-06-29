# Provenance Dominance Check

## Fact

PR #583 baseline payloads are permanent construction payloads:

- `construction_payload=true`
- `non_promotable=true`
- `candidate_eligible=false`
- `promotion_eligible=false`
- `paper_live_eligible=false`
- `canonical_crossing_allowed=false`

## Decision

The standard gate layer must evaluate provenance before interpreting any numeric WFO/OOS, robustness, MC, PSR, DSR, MinTRL, dashboard, reporting, agent, or operator-visible result.

## Required Behavior

If either `construction_payload=true` or `non_promotable=true` is present:

- candidate eligibility is `reject_by_construction`;
- crossing is `reject_by_construction`;
- paper/live eligibility is false;
- edge claims are forbidden;
- numeric overrides are forbidden;
- retuning/rescue interpretation is forbidden.

## Failure Mode

Any surface that displays a PR #583 baseline as a candidate, edge, GO evidence, readiness item, promotion input, crossing input, paper/live input, or ranking/recommendation item has violated the contract.

## Current Package Check

This package does not execute any baseline, synthesize any metric, create any candidate artifact, write any result population, or modify any crossing/candidate path. The dominance rule is recorded as a contract for later consumers.
