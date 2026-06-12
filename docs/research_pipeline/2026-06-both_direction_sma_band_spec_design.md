# Both-Direction SMA-Band Strategy Spec Design

## 1. Scope And Non-Authority

WP-SPEC-BOTHDIR-01a is a T1 docs-only design package.

This document records a lock-candidate Strategy Spec design for a symmetric
both-direction SMA-band mean-reversion research candidate. It does not create a
committed Strategy Spec instance, variant manifest, sweep plan, result
population, canonical artifact, dashboard output, data artifact, or executable
research artifact.

This document creates no ranking, recommendation, readiness, approval,
promotion, transition, paper/live, runtime, order, broker, exchange, OMS, risk,
or execution authority. Downstream instance authoring and canonical sweeps
remain separate Karl-gated packages.

## 2. Repo-Truth Basis

Repo files inspected for this design:

- `docs/project_status.md`
- `CLAUDE_START_HERE.md`
- `docs/runbook.md`
- `AGENTS.md`
- `docs/ai/codex/WP_DRAFTING_STANDARD.md`
- `docs/ai/codex/COMPACT_WP_TEMPLATE.md`
- `docs/ai/codex/WP_EXECUTION_REPORT.md`
- `docs/status_entries/README.md`
- `docs/research_pipeline/README.md`
- `docs/research_pipeline/2026-06-both_direction_semantics_lock.md`
- `docs/status_entries/WP-COMP-BOTHDIR-01c.md`
- `docs/status_entries/WP-COMP-BOTHDIR-01d.md`
- `docs/data_catalog.md`
- `docs/data/2026-06-binance_usdtm_15m_data_contract.md`
- `docs/data/2026-06-binance_usdtm_15m_gap_policy.md`
- `docs/data/2026-06-binance_usdtm_15m_catalog_and_slice_identity.md`
- `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json`
- `research/schemas/strategy_spec.schema.json`
- `tools/registry/validate_strategy_specs.py`
- `tools/research_runner/spec_signal_compiler.py`
- `tests/test_validate_strategy_specs.py`
- `tests/test_spec_signal_compiler.py`
- `research/strategy_specs/STRAT-SPEC-0001.strategy_spec.json`
- `research/variant_manifests/VM-0001.variant_manifest.json`
- `research/sweep_plans/SWEEP-PLAN-0001.sweep_plan.json`

Capability basis confirmed from current merged repo truth:

- `direction: "both"` semantics are locked in
  `docs/research_pipeline/2026-06-both_direction_semantics_lock.md`.
- Both-direction schema and validator support exists from
  `WP-COMP-BOTHDIR-01c`.
- Both-direction compiler support exists from `WP-COMP-BOTHDIR-01d`.
- Explicit long/short side labels are supported for root entry groups and
  side-specific exit groups.
- `scale_by_one_minus_parameter` and `scale_by_one_plus_parameter` are
  schema-valid, validator-accepted, and compiler-supported composed operands.
- `sma` is present in the current indicator catalog and compiler builtin set.
- Parameter-bound indicator lookbacks are supported in
  `indicator_ref.lookback`, including inside composed operand base operands.
- BTCUSDT 15m OHLCV data references exist in `docs/data_catalog.md` and the
  committed D4A catalog/slice artifact chain.

## 3. Strategy Family Summary

| Field | Design value |
|---|---|
| Market | BTCUSDT perpetual futures |
| Venue context | Binance USDT-M |
| Data stream | OHLCV |
| Timeframe | 15m |
| Direction | both |
| Family | SMA-band symmetric mean reversion |

Research-candidate description: test whether deviations outside a symmetric
SMA band revert toward the SMA centerline on BTCUSDT 15m OHLCV data.

This is a research candidate description only. It is not a profitability claim,
recommendation, approval, promotion, or execution instruction.

## 4. Entry Logic

Conceptual long entry:

```text
close < SMA(N) * (1 - p)
```

Conceptual short entry:

```text
close > SMA(N) * (1 + p)
```

Strategy Spec design representation:

- `entry_logic.direction` is `both`.
- Long and short entries are explicit root groups.
- The long root group has `side: "long"`.
- The short root group has `side: "short"`.
- The long lower band uses `scale_by_one_minus_parameter`.
- The short upper band uses `scale_by_one_plus_parameter`.
- No compiler mirroring is used.
- No expression language, formula field, or new operator is used.
- Condition group depth remains at root depth 1 and below the repo cap of 3.

Long entry condition shape:

```json
{
  "condition_id": "LONG-CLOSE-LT-SMA-SCALED-MINUS-P",
  "condition_role": "required",
  "left_operand": {
    "operand_type": "data_ref",
    "ref": "close",
    "field": "close",
    "timeframe": null,
    "lookback": null
  },
  "operator": "lt",
  "right_operand": {
    "operand_type": "composed_operand",
    "composition_type": "scale_by_one_minus_parameter",
    "base_operand": {
      "operand_type": "indicator_ref",
      "ref": "sma",
      "field": "value",
      "timeframe": null,
      "lookback": { "bars_parameter_ref": "sma_lookback_bars" }
    },
    "parameter_operand": {
      "operand_type": "parameter_ref",
      "ref": "band_threshold",
      "field": null,
      "timeframe": null,
      "lookback": null
    }
  }
}
```

Short entry condition shape:

```json
{
  "condition_id": "SHORT-CLOSE-GT-SMA-SCALED-PLUS-P",
  "condition_role": "required",
  "left_operand": {
    "operand_type": "data_ref",
    "ref": "close",
    "field": "close",
    "timeframe": null,
    "lookback": null
  },
  "operator": "gt",
  "right_operand": {
    "operand_type": "composed_operand",
    "composition_type": "scale_by_one_plus_parameter",
    "base_operand": {
      "operand_type": "indicator_ref",
      "ref": "sma",
      "field": "value",
      "timeframe": null,
      "lookback": { "bars_parameter_ref": "sma_lookback_bars" }
    },
    "parameter_operand": {
      "operand_type": "parameter_ref",
      "ref": "band_threshold",
      "field": null,
      "timeframe": null,
      "lookback": null
    }
  }
}
```

## 5. Exit Logic

Conceptual long exit:

```text
close >= SMA(N)
```

Conceptual short exit:

```text
close <= SMA(N)
```

Strategy Spec design representation:

- Exit groups are side-specific.
- The long exit root group has `side: "long"`.
- The short exit root group has `side: "short"`.
- There is no shared unlabeled exit group.
- There is no silent flip or implicit reversal.
- `max_holding_period.enabled` is false for this design surface.

Long exit condition shape:

```json
{
  "condition_id": "LONG-CLOSE-GTE-SMA",
  "condition_role": "exit",
  "left_operand": {
    "operand_type": "data_ref",
    "ref": "close",
    "field": "close",
    "timeframe": null,
    "lookback": null
  },
  "operator": "gte",
  "right_operand": {
    "operand_type": "indicator_ref",
    "ref": "sma",
    "field": "value",
    "timeframe": null,
    "lookback": { "bars_parameter_ref": "sma_lookback_bars" }
  }
}
```

Short exit condition shape:

```json
{
  "condition_id": "SHORT-CLOSE-LTE-SMA",
  "condition_role": "exit",
  "left_operand": {
    "operand_type": "data_ref",
    "ref": "close",
    "field": "close",
    "timeframe": null,
    "lookback": null
  },
  "operator": "lte",
  "right_operand": {
    "operand_type": "indicator_ref",
    "ref": "sma",
    "field": "value",
    "timeframe": null,
    "lookback": { "bars_parameter_ref": "sma_lookback_bars" }
  }
}
```

## 6. Both-Direction Conflict Semantics

This design relies on the locked compiler behavior from
`docs/research_pipeline/2026-06-both_direction_semantics_lock.md` and
`WP-COMP-BOTHDIR-01d`:

- If both long and short entries fire while flat, the output remains flat.
- The compiler emits one mutually exclusive signal stream: long XOR short XOR
  flat.
- Opposite-side entry while already in a position does not flip the position.
- Same-bar side-specific exit plus opposite-side entry resolves to flat, not to
  a reversal.
- Long exits close long state only.
- Short exits close short state only.

## 7. Parameters And Finite Grid

Proposed free parameters:

| Parameter | Type | Role | Proposed values | Counted free parameter |
|---|---:|---|---|---:|
| `sma_lookback_bars` | integer | entry | `{20, 50}` | yes |
| `band_threshold` | number ratio | entry | `{0.0025, 0.005, 0.01, 0.015, 0.02}` | yes |

Free-parameter count: 2.

Target count <= 3: satisfied.

Hard cap <= 5: satisfied.

Finite grid size: 10 variants if every combination is retained by a later
variant manifest.

`sma_lookback_bars` is proposed as a small finite axis because current repo
truth supports closed integer lookback binding for `indicator_ref.lookback`, and
the 15m data span can support both short and medium centerline anchors.

`band_threshold` is the symmetric band parameter. Values are ratios, not
percentage strings. The grid is intentionally finite and small. It does not
claim profitability or strategy quality.

## 8. Data Reference

Existing committed BTCUSDT 15m OHLCV references:

- Legacy data catalog entry:
  `data/processed/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`
  with SHA256
  `3fd05b841210962147a92bd77167ccefce57f6eb812cb55565d6f6cbb5154c31`.
- D4A dataset id: `binance_usdtm_btcusdt_ohlcv_15m`.
- D4A catalog ref:
  `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`.
- D4A data slice identity:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`.
- Symbol: `BTCUSDT`.
- Venue: Binance.
- Market type: USDT-M perpetual.
- Stream: `ohlcv`.
- Timeframe: `15m`.
- Source type: `offline_bulk_or_local_file`.
- Range: `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`.
- Row count and expected row count: `220128`.
- Gap facts: `gap_count=0`, `missing_bar_count=0`.
- Duplicate facts: `duplicate_group_count=0`, `duplicate_row_count=0`.
- D3 validation status: `PASS`.

This WP adds no data, performs no data acquisition, and does not authorize data
downloads or catalog mutation.

## 9. Backtest-Realism Assumptions

Repo-truth surfaces inspected:

- `docs/research_pipeline/2026-06-lab_validity_floor_backtest_realism_bounded_search_design.md`
- `research/strategy_specs/STRAT-SPEC-0001.strategy_spec.json`
- `research/sweep_plans/SWEEP-PLAN-0001.sweep_plan.json`
- `research/result_populations/RP-4492.result_population.json`

Design-level assumptions:

- Fees, slippage, funding, fill mode, order size, liquidity capacity,
  liquidation mode, mark price source, and bar-path assumptions must be
  declared by later instance/sweep/result packages.
- This design does not set final cost assumptions.
- Existing canonical parent examples use declarations such as
  `taker_entry_taker_exit`, `fixed_bps`, `complete`, `entry_price`,
  `zero_equity`, `close`, and `next_open_close_mark`, but those are not
  finalized for this candidate by this docs-only package.
- This design does not create a runner input, backtest run, result population,
  execution model, paper/live behavior, or promotion path.

## 10. Non-Committed Compile Probe

Probe result: PASS.

Probe method:

- Created a temporary full Strategy Spec-shaped scratch payload at
  `.local_tmp/wp-spec-bothdir-01a-probe/research/strategy_specs/STRAT-SPEC-9002.strategy_spec.json`.
- Validated that scratch payload with
  `tools.registry.validate_strategy_specs.validate_strategy_specs(strategy_specs_dir=<scratch dir>)`.
- Compiled the in-memory payload with
  `tools.research_runner.spec_signal_compiler.compile_signal`.
- Used synthetic 15m OHLCV only.
- Used the variant parameter values
  `sma_lookback_bars=20` and `band_threshold=0.02`.
- Deleted the scratch directory after the probe.

Probe evidence:

| Probe item | Result |
|---|---|
| Full scratch Strategy Spec-shaped payload validation | PASS |
| Explicit long and short root entry groups | PASS |
| Explicit long and short side-specific exit groups | PASS |
| `scale_by_one_minus_parameter` lower band | PASS |
| `scale_by_one_plus_parameter` upper band | PASS |
| Parameter-bound SMA lookback inside composed base operand | PASS |
| Compiler output signal domain | PASS: `[-1.0, 0.0, 1.0]` |
| Deterministic repeated compilation | PASS |
| Synthetic warmup nonzero check | PASS: first 19 rows had zero nonzero signals |
| Scratch files committed | No |

The probe is compatibility evidence only. It is not a committed Strategy Spec
instance, not pre-registration, not a variant manifest, not a sweep plan, not a
result population, and not strategy-quality evidence.

## 11. Authoring Friction / Gap Analysis

Observed friction:

- Catalog/data reference surfaces are split between legacy `docs/data_catalog.md`
  and D4A catalog/slice artifacts. Later instance authoring should choose the
  exact provenance reference explicitly.
- Backtest-realism assumptions are available as schema/report fields and prior
  examples, but this WP does not freeze final assumptions for this candidate.
- A later instance package must decide whether the 10-combination grid is the
  committed denominator or whether the grid should be narrowed before freezing.

No expressibility blocker was found for the proposed design under current closed
grammar, depth <= 3, existing `sma`, parameter-bound lookback support, plus/minus
composed operands, and both-direction compiler semantics.

No schema, validator, compiler, test, catalog, runner, backtester, or runtime
change is needed for this docs-only design package.

## 12. Downstream Gates

`WP-SPEC-BOTHDIR-01b` frozen instance authoring is Karl-gated.

`WP-SPEC-BOTHDIR-01c` canonical sweep/result-population work is Karl-gated.

No downstream WP is authorized by this document. Main/Karl must explicitly
approve any committed Strategy Spec instance, variant manifest, sweep plan,
canonical sweep write, result population, or interpretation package.
