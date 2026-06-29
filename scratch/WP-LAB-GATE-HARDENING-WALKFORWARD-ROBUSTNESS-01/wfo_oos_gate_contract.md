# WFO/OOS Gate Contract

## Status

WFO/OOS is a standard candidate-gate concept before any future candidate consideration.

This package defines semantics only. It does not run WFO/OOS, change runner behavior, create canonical fold manifests, write Result Populations, register candidates, cross, promote, or touch paper/live/runtime paths.

## Required Future Semantics

Future WFO/OOS protocols must:

- preserve chronological ordering;
- define train/test split identity;
- define purge/embargo rules or explicitly state why they are not applicable;
- preserve full fold denominators;
- keep failure, blocked, invalid, no-trade, data-unavailable, and not-attempted folds visible;
- identify selection and evaluation windows before interpreting OOS outcomes;
- prevent aggregate summaries from hiding per-fold instability or denominator shrinkage.

## Baseline Construction Payloads

WFO/OOS cannot promote construction payloads.

A favorable OOS fold, favorable aggregate, or accidental pass-like metric cannot override `construction_payload=true` or `non_promotable=true`.

No WFO/OOS metric may be fabricated when data, fold manifests, fold outputs, return paths, or per-fold result rows are missing.

## Outcome Mapping For PR #583 Baselines

- `known_losing_baseline`: `fail` or `insufficient`.
- `known_neutral_or_no_trade_baseline`: `blocked` or `insufficient` for no-signal/no-trade posture.
- `known_degenerate_or_invalid_baseline`: `blocked` / invalid, with no metrics claimed.

All three map candidate eligibility and crossing to `reject_by_construction`.

## Deferred Implementation

Actual WFO/OOS runner execution, window-manifest schema changes, validator changes, query-layer changes, canonical writes, and candidate/crossing integration remain deferred for separately authorized packages.
