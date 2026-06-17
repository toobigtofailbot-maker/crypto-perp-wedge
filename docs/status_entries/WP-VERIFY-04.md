# WP-VERIFY-04

## Package Class

Tooling-only validation / scope-control improvement.

## Branch / Worktree / Base

- Branch: `tooling/verify-04-authorized-paths`
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-VERIFY-04`
- Base: `origin/main` at `e613545`

## Changed Files

- `tools/dev/diff_scope_summary.py`
- `tools/dev/verify.py`
- `tests/test_diff_scope_summary.py`
- `tests/test_verify.py`
- `docs/research_pipeline/2026-06-verify_04_authorized_paths.md`
- `docs/status_entries/WP-VERIFY-04.md`

## Repo-Truth Discovery

- Current forbidden-prefix logic still uses broad defaults including `research/`, `lib/`, `src/`, `scripts/`, `configs/`, `data/`, `.claude/`, `pyproject.toml`, and `requirements`.
- `diff_scope_summary.py` already supported partial authorized canonical Result Population writes and general authorized paths.
- `verify.py` delegates scope checking to `diff_scope_summary.py --check-forbidden` and forwards authorization arguments only when explicitly supplied.
- Existing tests covered forbidden-prefix behavior, canonical Result Population authorization, partial schema-path authorization, wrapper command construction, and fail-closed command behavior.

## Delivered Change

General authorized-path bypasses now require explicit package, scope, and path inputs. The scope recognizer is expanded for package-authorized Strategy Spec schema edits, Strategy Spec preregistration artifacts, validator tooling, compiler tooling, research-pipeline prereg docs, and status entries.

The default check remains strict:

```powershell
python tools/dev/diff_scope_summary.py --check-forbidden
```

The explicit package-authorized form is:

```powershell
python tools/dev/diff_scope_summary.py --check-forbidden --authorized-package WP-ONLINE-OHLCV-PRIMITIVE-IMPL-01 --authorized-scope strategy-spec-schema --authorized-path research/schemas/strategy_spec.schema.json
```

## Validation Summary

- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_diff_scope_summary.py -q`: PASS, 28 passed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_verify.py -q`: PASS, 21 passed.
- `git diff --check`: PASS.
- `git diff --cached --check`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py --check-forbidden`: PASS; no forbidden-path matches.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/verify.py --integrity-views --integrity-max-workers 4 --timeout-seconds 300 --max-output-chars 6000 --json`: PASS; all discovered integrity views clean.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_strategy_specs`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_variant_sweep_artifacts`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_indicator_catalogs`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_candidate_registry`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_paper_state`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`: PASS.

## Boundary Summary

Runtime, paper/live, OMS, risk, reconciliation, broker/exchange, capital, data, Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, compiler behavior, runner behavior, schema artifacts, and validator behavior were not changed.

The tooling change reduces false positives only for exact package-authorized paths. Unauthorized protected-path detection remains strict.
