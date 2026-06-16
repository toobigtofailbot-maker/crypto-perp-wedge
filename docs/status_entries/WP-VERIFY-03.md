# WP-VERIFY-03 - Pytest throughput and authorized-path advisory policy

## Branch / PR

- Branch: `tools/verify-03-throughput-authorized-paths`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/486

## Package Class

- T3 tooling / tests / docs.

## Scope Summary

- Extends `tools/dev/diff_scope_summary.py` with bounded exact-path
  authorization evidence for package-authorized research schema, compiler, and
  validator paths.
- Preserves the existing
  `--authorized-canonical-result-population-write` behavior unchanged, including
  existing-RP mutation rejection.
- Extends `tools/dev/verify.py` to pass the new authorization flags through to
  diff-scope, add a docs-only validation preset, and run deterministic
  dependency-free full-pytest file shards with per-shard command, timeout,
  elapsed-time, and status evidence.
- Adds docs-only validation policy wording that distinguishes
  `full pytest: NOT RUN - docs-only policy` from `TIMED OUT`.
- Changes no result populations, Strategy Specs, variant manifests, sweep plans,
  schemas, validators, compiler behavior, query-layer behavior, runner,
  backtester, data, dashboard implementation, runtime, paper/live paths, OMS,
  reconciliation, risk, broker/exchange, credentials, or capital controls.

## Changed Files

- `tools/dev/diff_scope_summary.py`
- `tools/dev/verify.py`
- `tests/test_diff_scope_summary.py`
- `tests/test_verify.py`
- `docs/ai/codex/VALIDATION_POLICY.md`
- `docs/ai/codex/WP_DRAFTING_STANDARD.md`
- `docs/status_entries/WP-VERIFY-03.md`

## Validation Summary

- `git fetch origin`: pass; local `main` matched `origin/main` at
  `0d1248d8caa57e4d74d859a60dac984496473b4d` before worktree creation.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_diff_scope_summary.py tests/test_verify.py -q`:
  pass, 42 tests.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -q`:
  initial 180s command timeout with no failure output, rerun with longer timeout
  passed, 64 tests in 550.59s.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_strategy_specs`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_variant_sweep_artifacts`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_candidate_registry`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/verify.py --integrity-views --integrity-max-workers 4 --timeout-seconds 300 --max-output-chars 6000 --json`:
  pass; 55 discovered `v_integrity_*` views returned zero rows.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/verify.py --validation-preset docs-only --timeout-seconds 300 --max-output-chars 6000 --json`:
  pass; docs-only preset did not run full pytest.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/verify.py --full-pytest-sharded --pytest-shards 4 --pytest-shard-workers 4 --timeout-seconds 300 --full-pytest-timeout-seconds 1800 --max-output-chars 6000 --json`:
  pass; 68 test files split into four 17-file shards, all shards passed, one
  environment skip retained. Wall time was 975.6s; slowest shard was 963.0s.

## Throughput Evidence

- Package baseline context: prior serial full pytest had measured about 1263s.
- New sharded full-suite run completed in 975.6s wall time on this worktree.
- Failure behavior is fail-closed: any failed or timed-out shard is included in
  `failures` and makes `overall_status=fail`.
- Empty shards are rejected before execution so an empty file list cannot
  accidentally run unsharded full pytest.

## Authorization Evidence

- Existing canonical result-population authorization tests still prove a new
  canonical RP path can pass only when explicitly authorized and matching
  `research/result_populations/RP-<digits>.result_population.json`.
- Existing RP mutation tests still fail because paths present in `HEAD` are
  rejected.
- New tests prove exact authorized research schema paths pass, unauthorized
  research schema paths fail, compiler scope only accepts the exact compiler
  path, schema scope does not allow `lib/`, and mixed authorized/unauthorized
  diffs still fail.

## Boundary Summary

- Forbidden-path detection weakened: no.
- Existing RP mutation allowed: no.
- Tests skipped or removed to improve speed: no.
- Research artifacts changed: no.
- Runtime, paper/live, OMS, risk, reconciliation, broker/exchange, credentials,
  capital, data, runner, backtester, compiler behavior, schemas, validators, and
  query-layer behavior changed: no.

## Merge Status

- Ready for review. PR #486 is open as a ready PR, not draft.
