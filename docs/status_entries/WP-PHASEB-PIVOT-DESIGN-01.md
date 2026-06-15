# WP-PHASEB-PIVOT-DESIGN-01 - Phase-B momentum pivot design

- Package class: T1 docs-only design.
- Branch: `docs/phaseb-pivot-design-01`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-PHASEB-PIVOT-DESIGN-01`.
- Base: `origin/main` at PR #471 merge `1f26038`.
- Scope summary: Adds a docs-only design for the first non-fade Phase-B
  trend/momentum pivot hypothesis after `RP-7520` and `RP-7134` fade NO-GOs.
- Changed files:
  - `docs/research_pipeline/2026-06-phaseb_pivot_design_01.md`
  - `docs/research_pipeline/README.md`
  - `docs/status_entries/WP-PHASEB-PIVOT-DESIGN-01.md`
  - `docs/project_status.md`
- Evidence inputs: `RP-7520`, `RP-7134`, Phase-B trial screen verdict,
  Phase-B v1 failure decomposition, current Strategy Spec schema, indicator
  catalog, compiler, compiler tests, and relevant status entries inspected
  read-only.
- Design conclusion: Select a both-direction SMA crossover trend-continuation
  design as the narrow default path. Long entries use fast SMA crossing above
  slow SMA with optional close-above-trend confirmation; short entries use fast
  SMA crossing below slow SMA with optional close-below-trend confirmation.
  Exits use opposite crossover invalidation.
- Compile feasibility: YES for the selected primary design under current
  merged closed vocabulary. A no-write synthetic compiler probe passed with
  the repo virtualenv. The default `python` lacked `pandas`, so it was not a
  valid environment for the probe.
- Primitive gaps:
  - Required before pre-registration: finite fast/slow/trend lookback axes and
    invalid-combination handling; fixed throttle decision.
  - Optional / future: ATR-stop or fixed stop-loss, A3 throttle sweep binding,
    slope/momentum-strength primitive, volatility filter, breakout channel.
  - Rejected for now: making ATR-stop a prerequisite for this first crossover
    design, trailing stop, rolling high-low breakout, and slope confirmation.
- Future screen framing: complete denominator, net-of-cost performance,
  churn/frequency guard, explicit cost burden, net performance, drawdown,
  sensitivity across axes, and C3/DSR posture if evaluable.
- Boundary summary: no Strategy Spec, Variant Manifest, Sweep Plan, canonical
  result population, candidate, walk-forward, compiler/schema/catalog/lib/
  runner change, data change, paper/live/runtime, OMS/risk/reconciliation,
  broker/exchange, or trading authority created.
- Next decision: Main/Karl review should decide whether to proceed to a future
  `WP-PHASEB-MOMENTUM-PREREG-01`, require a stop-loss primitive first, revise
  the design, or pause strategy hypotheses for tooling such as VERIFY-02.

## Validation

- No-write compile-feasibility probe with default `python`: NOT RUN to
  completion; environment lacked `pandas` (`ModuleNotFoundError`).
- No-write compile-feasibility probe with
  `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe`: PASS;
  `COMPILE_PROBE_PASS`, `unique_values=0.0,1.0`, `nonzero_count=4`.
- `git diff --check`: PASS.
- `git diff --cached --check`: PASS at pre-stage check and after staging.
- `git status --short`: PASS; only the four expected docs/status files were
  modified or untracked.
- `python tools/dev/diff_scope_summary.py --check-forbidden`: PASS; no
  forbidden-path matches.
- `python -m tools.registry.validate_strategy_specs`: PASS.
- `python -m tools.registry.validate_variant_sweep_artifacts`: PASS.
- `python -m tools.registry.validate_indicator_catalogs`: PASS.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python -m tools.research_query.run --list-views`: PASS; listed 118 views.
- `python tools/dev/verify.py --help`: PASS.

## PR status

- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/473
