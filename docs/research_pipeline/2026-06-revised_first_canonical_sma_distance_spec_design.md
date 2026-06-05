# Revised First Canonical SMA-Distance Strategy Spec Design

## Status / Authority

This is a design and condition-structure surfacing document only.

It does not create a Strategy Spec instance. It does not authorize variant manifest or sweep plan creation. It does not authorize a canonical sweep. It does not authorize canonical writes. It does not modify compiler, catalog, schema, runner, or backtester behavior. It does not create ranking, readiness, recommendation, approval, or runtime authority.

## Intended First-Spec Shape

Main/Karl selected this revised first canonical shape for review:

| Field | Design value |
|---|---|
| Direction | long-only |
| Strategy family | SMA-distance mean reversion |
| Instrument | BTCUSDT perpetual |
| Timeframe | 15m |
| Data | OHLCV-only |
| Core idea | Enter long when close is sufficiently below SMA(20); exit when close returns to or above SMA(20). |
| Purpose | Pipeline validation with a genuine swept parameter, not strategy attractiveness. |

## Current Compiler Constraints

Repo-truth basis: `research/schemas/strategy_spec.schema.json`, `tools/registry/validate_strategy_specs.py`, `tools/research_runner/spec_signal_compiler.py`, `tests/test_validate_strategy_specs.py`, `tests/test_spec_signal_compiler.py`, `tools/research_runner/run_offline_sweep.py`, `lib/backtest.py`, and `lib/evaluation.py`.

| Surface | Current support |
|---|---|
| Operands | `data_ref`, `indicator_ref`, `parameter_ref`, `constant`, `composed_operand` |
| Composed form | `scale_by_one_minus_parameter` only |
| Composed base operands | `data_ref` or `indicator_ref` only |
| Composed parameter operand | `parameter_ref` only |
| Operators | `gt`, `gte`, `lt`, `lte`, `eq`, `neq` |
| Directions | `long`, `short` |
| Lookbacks | literal `operand.lookback.bars` only |
| Unsupported | `both`, `crosses_*`, `in_set`, `is_true`, `is_false`, lookback binding, `scale_by_one_plus_parameter`, offset forms, `z_score`, multi-timeframe/session support |

`risk_model.stop_distance` and ATR-stop metadata remain unconsumed by the current compiler, offline runner, backtester, and evaluation path. `tools/research_runner/run_offline_sweep.py` validates parent artifacts and uses synthetic runner inputs; `lib/backtest.py` consumes a precomputed signal; `lib/evaluation.py` consumes backtest results and parameter metadata. No runner/backtester/lib change is required for this design.

## Exact Proposed Condition Structure

### Entry Condition

Target:

```text
close < SMA(20) * (1 - entry_distance_threshold)
```

Strategy Spec-style pseudostructure:

```json
{
  "condition_id": "ENTRY-CLOSE-LT-SMA20-SCALED-BY-THRESHOLD",
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
      "lookback": { "bars": 20 }
    },
    "parameter_operand": {
      "operand_type": "parameter_ref",
      "ref": "entry_distance_threshold",
      "field": null,
      "timeframe": null,
      "lookback": null
    }
  }
}
```

### Exit Condition

Target:

```text
close >= SMA(20)
```

Strategy Spec-style pseudostructure:

```json
{
  "condition_id": "EXIT-CLOSE-GTE-SMA20",
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
    "lookback": { "bars": 20 }
  }
}
```

## Entry Parameter Design

Proposed active swept parameter:

| Field | Design value |
|---|---|
| name | `entry_distance_threshold` |
| type | `number` |
| role | `entry` |
| units | `ratio` |
| is_free_parameter | `true` |
| included_in_variant_generation | `true` |
| range | `min > 0`, `max < 1` |
| proposed first-sweep sub-range | `0.005` to `0.05` |

Proposed future grid for WP-S2c-209, not authorization in this package:

```text
0.005
0.010
0.015
0.020
0.030
0.040
0.050
```

This gives a committed denominator of 7 if no other parameter is swept.

## Fixed And Omitted Controls

- SMA lookback: fixed literal 20; not swept.
- `max_holding_period.bars`: omitted.
- ATR-stop: excluded from active spec; may be mentioned only as deferred metadata.
- ATR-stop multiplier: not swept, because no active consumer exists.

## Economic Rationale

Mean-reversion hypothesis: a downside deviation from a short SMA may revert toward the local mean. `entry_distance_threshold` controls how far below SMA(20) price must be before entry. This is a research hypothesis only. No profitability claim, ranking, recommendation, readiness, approval, or execution authority is created.

## Success / Failure Criteria

Success for this path means:

- condition structure validates;
- condition structure compiles;
- variant manifest can create bounded denominator greater than 1;
- sweep plan can commit denominator and hash chain;
- later sweep can preserve complete population;
- failures can be preserved;
- result population can validate;
- no unsupported capability is required.

Failure means:

- condition structure cannot compile;
- entry parameter cannot satisfy schema/validator;
- runner/backtester/lib changes are required;
- active ATR-stop claim appears;
- lookback binding is required;
- `both`, `crosses_*`, `z_score`, or session logic is required;
- denominator is not greater than 1.

## Compile Probe Result

Compile probe result: PASS.

Non-committed local compatibility probe:

| Probe item | Result |
|---|---|
| Minimal in-memory Strategy Spec-like dict with long-only entry and exit groups | PASS |
| Full temporary Strategy Spec-shaped payload schema validation | PASS |
| Temporary payload validation through `tools.registry.validate_strategy_specs` | PASS |
| Entry `close < SMA(20) * (1 - entry_distance_threshold)` with value `0.02` | PASS |
| Exit `close >= SMA(20)` | PASS |
| Synthetic 15m OHLCV with enough bars for SMA20 warmup | PASS |
| Warmup bars do not create true signals | PASS: first 19 bars had zero nonzero signal values |
| Threshold materially affects entries versus strict threshold and plain `close < SMA(20)` | PASS: entry transitions were 4 for threshold `0.02`, 2 for threshold `0.05`, and 5 for plain `close < SMA(20)` |
| Deterministic signal values | PASS: output values were `[0.0, 1.0]` |

No probe files were committed.

## WP-S2c-209 Readiness Assessment

WP-S2c-209 ready after Main/Karl review: YES.

This readiness is limited to drafting a future package that creates frozen Strategy Spec / variant manifest / sweep-plan instances after Main/Karl accepts the surfaced condition structure. It does not authorize that package here.

## Report-Back Questions

1. Is the surfaced condition structure accepted?
2. Is SMA lookback 20 fixed literal accepted?
3. Is `entry_distance_threshold` range `0.005` to `0.05` accepted?
4. Is the proposed 7-value grid acceptable for WP-S2c-209?
5. Is `max_holding_period.bars` omitted accepted?
6. Is ATR-stop excluded from active spec accepted?
7. May Side draft WP-S2c-209 to create frozen spec/manifest/sweep-plan instances after this design review clears?
