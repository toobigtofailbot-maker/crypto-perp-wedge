# Verify 04 Authorized Paths

Package label: `WP-VERIFY-04`

## Problem

The plain scope helper intentionally treats broad research and protected prefixes as forbidden by default. That strict default is useful for unauthorized-path detection, but it produced noisy false positives when a package explicitly authorized exact Strategy Spec schema or preregistration paths.

The recent `WP-ONLINE-OHLCV-PRIMITIVE-IMPL-01` package is the regression example: `research/schemas/strategy_spec.schema.json` was package-authorized, but plain `diff_scope_summary.py --check-forbidden` still failed on the broad `research/` prefix.

## Behavior Before

- `python tools/dev/diff_scope_summary.py --check-forbidden` failed on any changed `research/schemas/strategy_spec.schema.json` path.
- The helper already had partial authorized-path support, but `--authorized-path` did not require an explicit package id.
- The scope recognizer did not cover package-scoped Strategy Spec preregistration paths or research-pipeline prereg/status documentation categories.

## Behavior After

The strict default remains unchanged:

```powershell
python tools/dev/diff_scope_summary.py --check-forbidden
```

Package-authorized paths require all three explicit inputs:

```powershell
python tools/dev/diff_scope_summary.py --check-forbidden `
  --authorized-package WP-ONLINE-OHLCV-PRIMITIVE-IMPL-01 `
  --authorized-scope strategy-spec-schema `
  --authorized-path research/schemas/strategy_spec.schema.json
```

The authorized path is exact. Authorizing `research/schemas/strategy_spec.schema.json` does not authorize another file under `research/schemas/`, another Strategy Spec artifact, a Result Population, or a runtime/protected path.

`tools/dev/verify.py` forwards the same explicit authorization fields when supplied. Its default invocation still delegates to plain strict `diff_scope_summary.py --check-forbidden`.

## Supported Authorized Scopes

- `strategy-spec-schema`: exact `research/schemas/*.schema.json` paths.
- `strategy-spec-prereg`: exact `research/strategy_specs/STRAT-SPEC-<digits>.strategy_spec.json` paths.
- `research-validator` / `schema-validator-tooling`: exact `tools/registry/validate_*.py` validator paths.
- `research-compiler`: exact `tools/research_runner/spec_signal_compiler.py`.
- `research-pipeline-prereg`: exact `docs/research_pipeline/*prereg*.md` preregistration docs.
- `research-pipeline-status`: exact `docs/status_entries/WP-*.md` status entries.

Unsupported scopes fail closed. Missing package, missing scope, or missing path fails argument parsing.

## Validation Summary

- `python -m pytest tests/test_diff_scope_summary.py -q`: PASS
- `python -m pytest tests/test_verify.py -q`: PASS

The tests cover strict default failure, exact authorized-path pass, different protected path failure, missing package/scope rejection, Strategy Spec prereg path pass, Result Population rejection under Strategy Spec scope, and wrapper strict-default preservation.

## Boundary Confirmation

This package changes verification tooling and tests only. It does not modify Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, compiler behavior, runner behavior, data, runtime, paper/live, OMS, risk, reconciliation, broker/exchange, capital, or credentials paths.
