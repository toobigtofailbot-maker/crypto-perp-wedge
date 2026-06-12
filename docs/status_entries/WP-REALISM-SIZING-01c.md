# WP-REALISM-SIZING-01c — Runner-side sizing resolution

- Package class: T3 implementation, runner/spec-side, non-protected.
- Branch: `runner/realism-sizing-01c-leverage-aware-order-size`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/444
- Scope summary: Implements runner-side leverage-aware fixed order-size
  resolution for offline sweeps as a build-and-test-only package.
- Authorization basis: Main/Karl authorized runner-side leverage-aware
  `order_size` resolution after `WP-REALISM-SIZING-01b` confirmed Option 1 can
  be implemented without immediate `lib/backtest.py` or `lib/evaluation.py`
  changes.
- Reasoning model: GPT-5.5 high; runner-side sizing/cost semantics
  implementation, non-protected but methodology-sensitive.
- Implementation summary: Adds `--target-leverage`, default `1.0`, validates
  target leverage as finite and positive, resolves a fixed `order_size` from
  the first in-sample open, passes that value to the existing backtester, and
  records sizing provenance in existing identity-scoped assumption text.
- Sizing formula:
  `resolved_order_size = target_leverage * initial_equity / first_in_sample_open`.
- Reference-price basis: first in-sample bar open from the actual OHLCV frame
  used by the runner; missing, zero, negative, NaN, or infinite values fail
  closed.
- Long-run drift limitation: Runner-side fixed order-size resolution caps
  leverage at the reference price only. Effective leverage can drift as price
  changes over long real-data slices. This package measures that drift in
  tests but does not solve it dynamically.
- Test summary: Focused runner tests cover target leverage resolution, default
  leverage, invalid target leverage, invalid reference price, no-lookahead,
  determinism, dry-run/no canonical write, short real-like fixture handling,
  and measured start-vs-end effective-leverage drift.
- Validation summary:
  - `python -m pytest tests/test_offline_research_runner.py -q`: pass, 62
    passed, 2 existing timestamp parsing warnings.
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - `python tools/dev/diff_scope_summary.py`: pass; no forbidden-path matches.
  - `git diff --check`: pass.
  - `python -m pytest -q`: environment-only failure in
    `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`
    because the isolated worktree lacks gitignored
    `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`;
    remaining suite result was 1333 passed, 1 failed, 6 warnings.
- No-canonical-write proof: Focused tests preserve dry-run behavior and include
  explicit canonical result-population directory immutability assertions.
  Direct checks showed no `research/result_populations` status or diff.
- Boundary summary: No `lib/backtest.py`, `lib/evaluation.py`, schema,
  validator, Strategy Spec, variant manifest, sweep plan, result population,
  data, candidate registry, dashboard implementation, runtime, paper/live,
  OMS/risk, broker/exchange, or protected path changed.
- Merge status: PR #444 is open as a ready-for-review, non-draft PR. Final
  local rebase onto `origin/main` was a no-op; post-rebase validation is
  recorded above. GitHub reports `mergeable=MERGEABLE`.
- Next authority: This package is build-and-test only. It does not authorize a
  canonical re-run, new result population, sizing metadata schema package, or
  dynamic lib-core sizing. Main/Karl review is required after merge to choose
  the fixed-good-enough vs dynamic-required fork.
- Authority/finality audit: Completed over changed lines and new docs. Hits
  are implementation-scope statements, formula/reference-price behavior,
  validation command/result references, source artifact/status identifiers,
  limitation language, future fork labels, non-authority caveats, or
  forbidden-scope statements. No wording creates strategy ranking, readiness,
  promotion, profitability, paper/live/runtime, or execution authority.

## Active-WP requirement traceability

| Requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Use dedicated worktree from refreshed `origin/main` | WP sections 4 and 10 | `C:\GitHub\crypto-perp-wedge-realism-sizing-01c` on `runner/realism-sizing-01c-leverage-aware-order-size` | satisfied |
| Verify PR #443 / 01b merged and source artifacts exist | WP section 9 | Base `origin/main` at PR #443 merge; source files inspected | satisfied |
| Modify only allowed implementation/test files | WP sections 12 and 13 | `tools/research_runner/run_offline_sweep.py`, `tests/test_offline_research_runner.py` | satisfied |
| Add implementation note | WP section 18 | `docs/research_pipeline/2026-06-realism_sizing_runner_resolution_impl_note.md` | satisfied |
| Add status fragment | WP section 17 | this file | satisfied |
| Update project status compactly | WP section 19 | `docs/project_status.md` | satisfied |
| Update research pipeline README index | WP section 20 | `docs/research_pipeline/README.md` | satisfied |
| Run required validation | WP section 21 | validation summary | satisfied |
| Prove no canonical result-population changes | WP sections 16 and 21 | no-canonical-write proof | satisfied |
| Prove no `lib/` changes | WP sections 13 and 21 | boundary summary | satisfied |
| Complete authority/finality audit | WP section 22 | authority/finality audit summary | satisfied |
