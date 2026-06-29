# Robustness / MC Gate Contract

## Status

Robustness / MC is a standard candidate-gate concept before any future candidate consideration.

This package defines semantics only. It does not run MC, bootstrap, PSR, DSR, MinTRL, or any other robustness computation.

## Required Future Semantics

Future robustness gates must:

- operate on full populations, not winner-only rows;
- preserve failed, invalid, no-trade, blocked, data-unavailable, and not-attempted rows in denominator accounting;
- treat PSR, DSR, MinTRL, MC, bootstrap, and per-trade diagnostics as pass/fail/insufficient/withheld depending on available inputs;
- withhold or mark insufficient when per-trade rows, return paths, fold outputs, or trial-population metadata are unavailable;
- avoid converting missing data into confidence.

## Baseline Construction Payloads

Robustness cannot promote construction payloads.

A favorable robustness diagnostic cannot override `construction_payload=true` or `non_promotable=true`.

No robustness statistic may be fabricated for PR #583 baselines.

## Outcome Mapping For PR #583 Baselines

- `known_losing_baseline`: `fail`, `insufficient`, or `withheld`.
- `known_neutral_or_no_trade_baseline`: `withheld` or `insufficient`.
- `known_degenerate_or_invalid_baseline`: `withheld` / invalid.

All three map candidate eligibility and crossing to `reject_by_construction`.

## Deferred Implementation

Actual MC/robustness compute integration, PSR/DSR/MinTRL formula implementation, per-trade instrumentation, fixture-artifact schema support, and candidate/crossing integration remain deferred for separately authorized packages.
