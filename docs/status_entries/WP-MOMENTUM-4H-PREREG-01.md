# WP-MOMENTUM-4H-PREREG-01

Status: branch-state draft-and-surface package.

`WP-MOMENTUM-4H-PREREG-01` adds a reviewable 4h momentum preregistration
surface after the scratch-only 4h premise probe returned
`PREMISE-CONFIRMED`. It creates `STRAT-SPEC-0006`, `VM-0006`,
`SWEEP-PLAN-0006`, and `docs/research_pipeline/2026-06-momentum_4h_prereg_0006.md`;
updates the research-pipeline README index and query-test corpus expectations
only as needed.

The 0006 draft preserves the 0005 both-direction SMA crossover plus fixed A6
ATR-stop structure, uses the derived 4h data lineage from
`WP-DATA-RESAMPLE-4H-01`, and freezes an eight-row rescaled grid:
fast `[2, 3]`, slow `[6, 12]`, trend `[19, 25]`. It records the synthetic zero
funding limitation and the known dependency that current official canonical
runner/data-path support cannot consume 4h without a future narrow capability
package or approved execution route.

A scratch-only local compile/nondegeneracy sanity probe was run with direct
`compile_signal` plus `run_backtest`: all 8 proposed rows compiled and produced
nonzero trades. The probe wrote no committed output and is not canonical
evidence.

No Result Population is written, no canonical trial is run, and no 0004/0005
artifacts, `RP-3731`, 4h data metadata, compiler, schema, validator, runner,
query-layer logic, `lib/`, runtime, paper/live, OMS/risk/reconciliation,
broker/exchange, candidate, walk-forward, or capital authority is changed or
created. Freeze/finalization remains subject to explicit you/Main gate review.
