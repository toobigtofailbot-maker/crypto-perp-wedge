# WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01 Branch State

## Scope Summary

Defines a generic robustness and candidate-review reach contract across supported research families in parallel-safe reduced mode. The package uses docs, scratch fixtures, and isolated tests only.

## Branch And Base

- Branch: `lab/generic-robustness-review-reach-01`
- Base: refreshed `origin/main` at `2b2c3d886fde7e5ed01eed87bba3dbf0ea10c94a`
- Base includes PR #563 / `WP-RESEARCH-FUNDING-CARRY-02`.

## Repo-Truth Discovery

Discovery is recorded in `scratch/WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01/repo_truth_discovery.md`. Current merged truth shows the funding-rate positioning-fade scratch package completed as NO-GO, preserved a 36-row denominator, withheld PSR/DSR/MinTRL rather than fabricating inputs, and generated no candidate-review packet because all rows failed the primary drawdown screen.

## Parallel Forecast

The first edit was `scratch/WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01/parallel_touched_file_forecast.md`. Decision: `continue`. Conditional implementation files under `tools/robustness/**` and `tools/candidate_review/**` were avoided.

## Delivered Contract

`docs/research/GENERIC_ROBUSTNESS_REVIEW_REACH_CONTRACT.md` defines required family-neutral inputs and outputs, reason-code families, and review rules. It distinguishes:

- `candidate_review_packet_created`
- `no_candidate_review_packet_reason`
- `blocked_review_reason`
- `advisory_only_summary`

## Scratch Fixtures

`scratch/WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01/generic_review_contract.json` provides family-neutral examples for funding NO-GO, blocked Donchian/OOS unavailability, and an SMA packet-created shape. `family_fixture_summary.json` records observed family coverage and non-authority assertions.

## Tests

`tests/test_generic_robustness_review_reach.py` validates the fixture contract semantics:

- funding NO-GO produces `no_candidate_review_packet_reason`
- blocked families produce `blocked_review_reason`
- PSR/DSR/MinTRL are withheld rather than fabricated
- metadata is family-neutral and not SMA-only
- candidate lifecycle and runtime authority are not created

## Boundary Summary

No replay/normalization code, OOS gate code, `tools/robustness/**`, `tools/candidate_review/**`, candidate lifecycle artifacts, Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, candidate registry, schemas, validators, query-layer behavior, data, runtime, paper/live, OMS, risk, reconciliation, capital, funding P&L/accounting, provider/API/network, dashboard, scheduler, or large tracked data were changed.

## Sequence Dependency

No dependency on unmerged replay/OOS contracts was introduced. Future implementation can consume those contracts only after they are merged and separately authorized.

## Validation

Validation results are recorded in `scratch/WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01/validation_summary.txt`.
