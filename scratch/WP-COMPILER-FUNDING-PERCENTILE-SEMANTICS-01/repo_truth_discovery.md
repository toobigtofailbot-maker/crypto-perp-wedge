# Repo-Truth Discovery

## Base and precondition

- Base: `a713a39386114e01f5c06cbdfe518a666d33aa36` (`origin/main`).
- PR #561 is merged as `a713a39`; `WP-RESEARCH-FUNDING-CARRY-01` is present.
- The branch and worktree were created fresh and were clean before edits.

## Existing contract

- `research/schemas/strategy_spec.schema.json` permitted direct `data_ref` operands, but non-indicator lookbacks were literal-only.
- `tools/research_runner/spec_signal_compiler.py` rejected `bars_parameter_ref` on `data_ref`; there was no rolling empirical-percentile transform.
- The closed computation vocabulary was implemented through Strategy Spec schema enums plus compiler-owned closed builtin/composition constants. No free-form transform registry or expression evaluator existed.
- `tools/research_runner/run_offline_sweep.py` already preserved only declared non-OHLCV fields and checked full-history availability through `PERP-DERIVED-FEATURE-AVAILABILITY-0001.json`.
- Direct `funding_rate` compilation and runner preservation already existed.
- `exit_logic.max_holding_period.bars` was schema-limited and compiler-limited to a literal integer.
- The compiler consumed max hold inside its deterministic signal-state loop; no backtester change was required.
- Existing bounded integer binding used `{ "parameter_ref": "..." }` for numeric fields and `{ "bars_parameter_ref": "..." }` for indicator lookbacks, with Strategy Spec declarations and VM axes validated separately.

## Files requiring change

- Strategy Spec schema.
- Strategy Spec validator and VM/Sweep binding validator.
- Build-and-test signal compiler.
- Focused compiler/schema/validator tests.
- Package scratch and branch-status artifacts.

## Forbidden files and boundaries

- No canonical Strategy Spec, Variant Manifest, Sweep Plan, Result Population, trial log, registry, or crossing output.
- No runner input/loading change, backtester, funding P&L, fill, accounting, runtime, paper/live, OMS, risk, reconciliation, capital, provider, API, network, credential, or large-data change.

## Repo-truth adjustment

- A separate transform catalog file was unnecessary. The merged repo's closed catalog mechanism for composed semantics is the schema enum plus matching validator/compiler constants. The new transform follows that mechanism.
- Availability enforcement remains in the offline runner, where existing recent-only/full-history labels are authoritative. The compiler additionally requires the transformed field to be declared in `host_data_refs` and present in its input frame.
