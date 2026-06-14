# WP-EXPRESS-DESIGN-01 - Design expressiveness primitive tranche

- Package class: T1 docs-only design / architecture planning.
- Branch: `docs/expressiveness-primitive-design`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/456
- Authorization basis: Main authorizes WP-EXPRESS-DESIGN-01 to design the next closed expressiveness primitive tranche for future BTCUSDT perpetual strategy research.
- Scope summary: Creates a docs-only expressiveness primitive design surface for future closed Strategy Spec / compiler primitive families after the `RP-7520` cost-drag finding.
- Created design file: `docs/research_pipeline/2026-06-expressiveness_primitive_design.md`.
- README pointer: Added a compact entry for `2026-06-expressiveness_primitive_design.md` in `docs/research_pipeline/README.md`.
- Project-status update: Added the compact WP-EXPRESS-DESIGN-01 branch-state line to `docs/project_status.md`.
- Priority summary: Highest-priority design areas are `z_score` / volatility-normalized distance, trend/regime filters, and trade-frequency controls including cooldown / re-entry gates. Medium-priority families are RVOL / volume anomaly filters, Donchian/channel primitives, RSI, and `offset_by_parameter` forms. Rolling VWAP, UTC-only time filters, multi-timeframe confirmation, ATR-stop consumption, funding/basis hooks, and open-interest/liquidation hooks are deferred pending exact semantics, data contracts, or runner/backtester design.
- Deferred/excluded summary: The design excludes arbitrary arithmetic language, formula strings, expression parsers, user-defined functions, `eval` / lambda / custom scripts, unrestricted boolean DSLs, catalog-data-interpreted computation, and open AST semantics. It defers MTF, ATR-stop, and data-driven feature implementation until separate alignment, stop-consumption, and provenance designs exist.
- Boundary summary: Docs/status only. No schema, validator, compiler, runner, backtester, catalog, Strategy Spec, variant manifest, sweep plan, result population, candidate registry, dashboard implementation, generated dashboard output, data acquisition, runtime, paper/live, OMS/risk/reconciliation, broker/exchange, collateral, or autonomous behavior is changed or authorized.
- Validation summary: `git diff --check` passed; `python tools/dev/diff_scope_summary.py` passed with no forbidden-path matches; `python -m tools.registry.validate_result_populations` passed; `python -m tools.research_query.run --list-views` passed; all 55 discovered `v_integrity_*` views returned zero rows via one-process query-layer execution after the per-view CLI loop exceeded the tool timeout.
- Authority/finality audit: Package-authored hits for authority-sensitive terms are classified as non-authority boundary statements, design-only capability discussion, evidence-level interpretation, deferred/forbidden-scope statements, or validation/status text. No hit implies candidate lifecycle action, primitive implementation authority, paper/live/runtime authority, deployment selection, variant/strategy ranking for use, or profitability.
- Merge status: PR #456 is open for review.
- Next authority: This package authorizes no primitive implementation. Future work requires separately scoped packages and explicit authorization.
