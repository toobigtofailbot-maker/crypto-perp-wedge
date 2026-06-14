# WP-ROBUST-C3 - Read-only trial accounting / multiple-testing diagnostics

- Package class: T3 read-only research diagnostics / tooling.
- Branch: `robust/c3-trial-accounting-dsr-gates`.
- Dedicated worktree: `C:\GitHub\crypto-perp-wedge-WP-ROBUST-C3`.
- Base: `origin/main` after PR #459 (`WP-ROBUST-C1`), PR #460
  (`WP-ROBUST-C2-DESIGN`), and PR #461 (`WP-EXPRESS-A1`) were present.
- Isolation summary: Other active worktrees were listed and not touched. The
  C3 work was created and executed only in the dedicated C3 worktree.
- Scope summary: Extends the existing C1 read-only robustness diagnostic helper
  with trial-log accounting and definition-only anti-overfit threshold
  diagnostics. The helper reads committed result populations and a configured
  trial-log JSONL path, reports trial-log presence, count source, countable
  denominator, invalid/duplicate-row posture, hypothesis counts, and
  unavailable failed/aborted-trial visibility limits without mutating any input.
- Existing repo-truth surface: `tools/research_runner/generate_robustness_report.py`
  remained the chosen implementation surface because C1 already established it
  as a derived, non-authoritative, read-only result-population diagnostic helper.
- Trial-log posture: The current committed `research/trial_log.jsonl` is present
  and contains 32 valid rows, 0 invalid rows, and 32 unique trial IDs. The
  denominator source is the full valid JSONL row count, not a winner-only,
  successful-only, or executed-only subset. Missing trial-log paths are reported
  as missing inputs rather than fabricated counts.
- DSR / multiple-testing posture: PSR, DSR, and MinTRL numeric values remain
  withheld because required formula inputs are still incomplete. The diagnostic
  now distinguishes available committed-population and trial-log denominators
  from still-missing effective independent-trial count, return-distribution
  moments, benchmark Sharpe, and declared selection-rule inputs.
- Anti-overfit threshold definitions: The report defines committed-population
  denominator, trial-log denominator, effective independent trials, benchmark
  Sharpe, and minimum track record length as definitions only. These definitions
  create no candidate gate, ranking, readiness, recommendation, selection,
  transition, paper/live, runtime, or protected-path authority.
- RP-7520 handling: A read-only diagnostic run over `RP-7520` reports result
  population denominator 10 and committed trial-log denominator 32 while
  preserving `numeric_values_emitted=false`.
- Boundary summary: No result populations, trial logs, schemas, validators,
  query-layer behavior, compiler, runner, backtester, lib, src, data catalog,
  canonical data, candidate lifecycle, ranking, promotion, readiness,
  paper/live/runtime, OMS/risk, broker/exchange, dependencies, CI, or protected
  execution paths changed.

## Validation Detail

- `git diff --check`: pass.
- `git diff --cached --check`: pass.
- `git diff --name-only`: pass; tracked diff listed
  `docs/status_entries/WP-ROBUST-C3.md`,
  `tests/test_generate_robustness_report.py`, and
  `tools/research_runner/generate_robustness_report.py`.
- `python tools/dev/diff_scope_summary.py --check-forbidden`: pass; forbidden
  path matches none.
- `python -m tools.registry.validate_result_populations`: pass.
- `python -m tools.research_query.run --list-views`: pass.
- `python -m tools.research_runner.generate_robustness_report --result-population research/result_populations/RP-7520.result_population.json --format json`: pass; stdout included `input_result_population_id=RP-7520`,
  committed result-population denominator 10, trial-log denominator 32, and
  `numeric_values_emitted=false`.
- `python -m pytest tests/test_generate_robustness_report.py -q`: pass;
  `14 passed`.
- `python -m pytest -q`: collection failed under system Python 3.14 because
  that interpreter lacks project dependencies (`binance`, `numpy`, `pandas`);
  this matches prior dependency-environment posture and is superseded by the
  venv full-suite run.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`: pass;
  `1405 passed, 1 skipped, 6 warnings` in `1258.74s`.
