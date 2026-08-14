# WP-CANON-H004-EVALUATION-ADVISORY-01

## Branch / PR

- Branch: `codex/wp-canon-h004-evaluation-advisory-01`
- Base: `6994e9000aa6dcf56a7f1a4a08712ba778ea8bbe`
- PR: not created because required full-release validation is not green.
- Package class: T1 non-canonical research evaluation / advisory artifacts,
  elevated to full-release validation because this is the M1 integration
  boundary.

## Scope and result

This package reuses the merged dry-run WFO, item-6 robustness, seeded
aggregate-row Monte Carlo, and robustness-depth machinery over canonical
`RP-0007`. It records a Lane 0 / M1 advisory conclusion without changing the
source Result Population or evaluation tooling.

The conclusion is FAIL / insufficient / withheld as applicable. Both WFO folds
have negative mean OOS Sharpe; the later fold has 0 / 81 positive OOS Sharpe or
return rows. PSR, DSR, MinTRL, regime robustness, and per-trade Monte Carlo are
withheld or unavailable where required source inputs do not exist. No statistic
was fabricated.

## Denominator and integrity

RP-0007 remains at 81 rows / committed denominator 81 / 81 successful runner
completions and whole-file SHA-256
`ff1104cebcb2775f3f64d2e5bec72b3aaaeeb4187740978e79a26a4819ee2308`.
Every WFO window and aggregate robustness input preserves all 81 variants.

The known H004 integrity disclosures remain the absent execution stream and the
legacy Strategy Spec hash row already classified by the runbook. They are not
reclassified as corruption by this advisory package.

## Boundary summary

H004 remains the engineering dummy, non-winning, GO-forbidden,
non-promotable, and `reject_by_construction`. No candidate admission, selection,
promotion/readiness, paper/live, runtime, OMS/risk, reconciliation, order,
exchange, capital, or autonomous-dispatch authority is created. No canonical
artifact, Strategy Spec, Variant Manifest, Sweep Plan, trial log, data, schema,
validator, query layer, runner/backtester code, config, dependency, or protected
path is changed.

## Validation and merge status

- Focused evaluation surfaces: 72 passed, 1 environment-dependent skip.
- Walk-forward-selected runner tests: 5 passed, 96 deselected.
- Accepted WFO replay: exact match across 162 rows; dry run true; writes false.
- Deterministic artifact replay: exact item-6 and seeded-MC file hashes;
  robustness-depth output checksum match.
- Result-population validator: pass; RP-0007 remains 81 rows at its fixed hash.
- Scope/format checks: JSON parse pass; `git diff --check` pass; forbidden-path
  matches none.
- Full release: fail, not a timeout. The named balanced profile assigned all
  162 tracked test files uniquely across 48 shards; 46 shards passed and two
  failed. `tests/test_dispatch_authorization.py` and
  `tests/test_scratch_persistence.py` retain stale guards requiring RP-0007 to
  be absent, contradicting the merged persistence package on this exact base.
  Both failures reproduce serially.
- Integrity: 62 views ran; 60 clean; exactly two one-row known runbook
  disclosures (`execution_stream_missing` and the STRAT-SPEC-0007 legacy hash
  reproducibility row); no additional finding.

The exact changed files were inspected and no protected or canonical mutation
was found. This branch is not green and no ready-for-review PR is created. A
separately scoped stale-test reconciliation is required before rerunning
full-release and closing M1 integration.
