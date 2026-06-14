# WP-ROBUST-C1 - Read-only robustness compute bring-up

- Package class: T3 tooling / read-only research diagnostics.
- Branch: `robust/c1-readonly-robustness-compute`.
- Dedicated worktree: `C:\GitHub\crypto-perp-wedge-WP-ROBUST-C1`.
- Base: `origin/main` after PR #458 merge (`71d3df5`).
- Scope summary: Generalizes the existing derived robustness report helper so it can emit read-only Markdown or JSON diagnostics for committed result populations beyond RP-2134, including RP-7520, while preserving denominator honesty and withholding numeric PSR / DSR / MinTRL values when required formula inputs are absent.
- Existing repo-truth surface: `tools/research_runner/generate_robustness_report.py` already implemented a derived, non-authoritative Item 6 report for RP-2134, and `tests/test_generate_robustness_report.py` already verified read-only behavior, denominator policy, missing-input warnings, and stdout/scratch-path output.
- Result-population inventory inspected: `RP-2134`, `RP-4492`, `RP-6688`, and `RP-7520`.
- RP-7520 handling: Adds focused smoke coverage over the committed RP-7520 population with denominator 10, 10 result rows, 10 successful outcome rows, D4 BTCUSDT 15m offline data posture, observed summary Sharpe rows, and explicit non-authoritative caveat text. The tool reads RP-7520 without mutation and emits no canonical artifact.
- Missing-input behavior: PSR, DSR, and MinTRL remain `withheld_missing_inputs`; the diagnostic lists missing return series, effective sample length, skewness, kurtosis, benchmark Sharpe, annualization convention, selection rule, and effective independent-trial count.
- Output behavior: Markdown remains the default output; `--format json` now emits the same derived diagnostic as JSON to stdout or an explicitly supplied scratch path.
- Boundary summary: No result populations, schemas, validators, query-layer behavior, compiler, runner, backtester, lib, data, candidate lifecycle, ranking, promotion, readiness, paper/live/runtime, OMS/risk, broker/exchange, or protected execution paths changed.
- Isolation summary: A1 was found dirty at `C:\GitHub\crypto-perp-wedge` on `express/a1-zscore-volnorm-distance` and was not edited. C1 work was created and executed only in `C:\GitHub\crypto-perp-wedge-WP-ROBUST-C1`.

## Validation Detail

- `git diff --check`: pass.
- `git diff --cached --check`: pass.
- `git diff --name-only`: pass; tracked diff listed `tests/test_generate_robustness_report.py` and `tools/research_runner/generate_robustness_report.py` before this status fragment was added.
- `python tools/dev/diff_scope_summary.py --check-forbidden`: pass; forbidden-path matches none.
- `python -m tools.registry.validate_result_populations`: pass.
- `python -m tools.research_query.run --list-views`: pass.
- `python -m tools.research_runner.generate_robustness_report --result-population research/result_populations/RP-7520.result_population.json --format json`: pass; stdout included `input_result_population_id=RP-7520`, `committed_denominator=10`, and `numeric_values_emitted=false`.
- `python -m tools.research_runner.generate_robustness_report --result-population research/result_populations/RP-7520.result_population.json`: pass; stdout included RP-7520, denominator 10, committed offline data posture, and withheld fabricated PSR / DSR / MinTRL values.
- `python -m pytest tests/test_generate_robustness_report.py -q`: pass; `9 passed`.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations`: pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`: pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_runner.generate_robustness_report --result-population research/result_populations/RP-7520.result_population.json --format json`: pass; stdout included `input_result_population_id=RP-7520`, `committed_denominator=10`, and `numeric_values_emitted=false`.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_generate_robustness_report.py -q`: pass; `9 passed`.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`: pass; `1385 passed, 1 skipped, 6 warnings` in `1330.87s`.

## Non-Evidence Runs

- `python -m pytest -q` with system Python 3.14: collection failed because that interpreter lacks project dependencies (`binance`, `numpy`, `pandas`); superseded by the passing venv full-pytest run.
