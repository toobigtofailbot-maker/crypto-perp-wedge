# WP-A6-ATRSTOP-01 - Closed ATR-stop compiler primitive

- Package class: compiler/schema/validator/tests/docs package.
- Branch: `feature/a6-atrstop-01`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-A6-ATRSTOP-01`.
- Base: `origin/main` at PR #482 merge `b0e9187`.
- Scope summary: Adds an optional closed `exit_logic.atr_stop` Strategy Spec
  shape and compiler-generated ATR-stop exit signal for offline research
  compilation only.
- Changed files:
  - `tools/research_runner/spec_signal_compiler.py`
  - `research/schemas/strategy_spec.schema.json`
  - `tools/registry/validate_strategy_specs.py`
  - `tests/test_spec_signal_compiler.py`
  - `tests/test_validate_strategy_specs.py`
  - `docs/status_entries/WP-A6-ATRSTOP-01.md`
- Locked semantics: `atr_stop` is absent-by-default. When present, it must use
  `enabled=true`, literal bounded `atr_lookback`, literal bounded
  `atr_multiplier`, `entry_reference_price=next_bar_open_pre_fee_slippage`,
  `evaluation_price=close`, and `evaluation_timing=bar_close`.
- Entry reference and ATR capture: the compiler emits the entry signal under
  existing signal semantics, then captures the modeled fill reference from the
  next bar open and freezes ATR from the entry signal bar, the last closed bar
  available before that next-open fill.
- Stop levels: long stop is `entry_ref - atr_multiplier * ATR_entry`; short
  stop is `entry_ref + atr_multiplier * ATR_entry`.
- Evaluation and precedence: the stop is evaluated on bar close while a modeled
  position is active. It is additive beside existing exit groups and
  `max_holding_period`; any trigger can emit the flat exit signal. No ranking,
  conflict authority, or reversal-on-exit behavior is introduced.
- Default preservation: specs without `exit_logic.atr_stop` compile under the
  existing path and existing schema/validator behavior remains valid.
- Methodology caveat: this is a bar-close stop signal for the offline
  next-open execution model. It does not model intrabar stop touches, stop
  orders, partial fills, slippage beyond existing backtest assumptions, or live
  execution realism; intrabar/fill realism remains deferred.
- Boundary summary: no `lib/backtest.py`, runner orchestration, Strategy Spec
  artifact, Variant Manifest, Sweep Plan, Result Population, data/catalog
  lineage, query layer, candidate/promotion artifact, paper/live/runtime,
  OMS/risk/reconciliation, broker/exchange, safe-mode, kill-switch, credential,
  or canonical evidence file is changed.

## Validation

- `git status --short`: PASS; only expected package files are modified or
  untracked.
- `git diff --check`: PASS.
- `git diff --cached --check`: PASS; no staged files at final pre-stage check.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_spec_signal_compiler.py -q`:
  PASS, 170 passed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_validate_strategy_specs.py -q`:
  PASS, 94 passed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -q`:
  PASS, 64 passed in 416.58s after rerun with a long enough timeout. Earlier
  120s and 420s tool timeouts did not indicate test failure.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest`: PASS,
  1483 passed, 1 skipped, 6 warnings in 1263.48s.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_strategy_specs`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_variant_sweep_artifacts`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_indicator_catalogs`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations`:
  PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`:
  PASS; listed query views.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py --check-forbidden`:
  FAIL by helper rule only; the helper flags
  `research/schemas/strategy_spec.schema.json` because `research/` is a broad
  built-in forbidden prefix. That schema file is explicitly allowed by this
  package; no result populations, Strategy Specs, variants, sweep plans,
  query-layer files, runtime files, or protected execution files are changed.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/verify.py --integrity-views --integrity-max-workers 4 --timeout-seconds 300 --max-output-chars 6000`:
  FAIL only because it delegates to the same broad `diff_scope_summary.py
  --check-forbidden` rule above. Its registry/query subcommands passed, and
  all 55 discovered `v_integrity_*` views were clean.

## Next authority

This package does not create momentum v2 preregistration authority, canonical
trial authority, candidate lifecycle authority, paper/live/runtime authority,
or any promotion/readiness authority. Future use in a Strategy Spec or sweep
requires a separate approved package.
