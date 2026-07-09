# Denominator Scale Evidence

## Focused Evidence

The focused runner adapter tests prove:

- default product runner path preserves the existing 8-row denominator;
- explicit 5-row synthetic denominator maps all supported status buckets;
- 1000-row synthetic bounded sweep preserves full denominator with:
  - `completed = 200`
  - `failed = 200`
  - `invalid = 200`
  - `pruned = 200`
  - `blocked = 200`
- budget-exceeded approval fails closed before runner invocation;
- post-run row shrinkage fails closed.

The focused gates adapter test proves:

- advisory packets include `scale_budget`;
- advisory packets include `largest_tested_denominator`;
- advisory packets preserve scale caveats;
- candidate-surface routing remains advisory-only.

## Largest Tested Denominator

`1000`

## Denominator Caveat

The current product runner outcome vocabulary does not include a native `no_trade` category. Current support preserves all repo-supported runner outcomes and maps `not_attempted` into `blocked`. Future no-trade vocabulary must be mapped explicitly before claiming no-trade support.
