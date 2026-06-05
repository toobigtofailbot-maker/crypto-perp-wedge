# First Canonical SMA-Distance Strategy Spec Design

## Status / Authority

This is a design and structure-surfacing document only. It does not create a Strategy Spec instance. It does not authorize variant manifest or sweep plan creation. It does not authorize a canonical sweep. It does not authorize canonical writes. It does not modify compiler, catalog, schema, runner, or backtester behavior. It does not create ranking, readiness, recommendation, approval, or runtime authority.

## Intended First-Spec Shape

Main/Karl selected the constrained first canonical path after the WP-S2c-200 computation-binding checkpoint.

| Field | Design value |
|---|---|
| Direction | long-only |
| Strategy family | SMA-distance mean reversion |
| Instrument | BTCUSDT perpetual |
| Timeframe | 15m |
| Data | OHLCV-only |
| Core idea | Enter long when close is sufficiently below SMA; exit when close returns to or above SMA. |
| Purpose | Pipeline validation, not strategy attractiveness. |

## Current Compiler Constraints

Repo-truth basis: `tools/research_runner/spec_signal_compiler.py`, `tests/test_spec_signal_compiler.py`, and `docs/research_pipeline/2026-06-computation_binding_tranche_checkpoint.md`.

| Surface | Current support |
|---|---|
| Operands | `data_ref`, `indicator_ref`, `parameter_ref`, `constant` |
| Operators | `gt`, `gte`, `lt`, `lte`, `eq`, `neq` |
| Directions | `long`, `short` |
| Unsupported direction/operator cases | `both`, `crosses_above`, `crosses_below`, `in_set`, `is_true`, `is_false` fail closed |
| Indicator refs | `sma`, `ema`, `atr`, `stddev` |
| Lookbacks | literal `operand.lookback.bars` only |
| Unsupported composition | no arithmetic expressions, no formula fields, no z_score, no SMA-distance expression, no multi-timeframe/session support |

Condition roles and group roles are also narrower in the compiler than in the schema:

| Context | Compatible group roles | Compatible condition roles |
|---|---|---|
| Entry/filter entry path | entry-like `required`, `confirming`, `filter`, `regime`, `session`, `funding`, `volatility`, `other`; blocking groups `blocking`, `no_trade`, `cooldown` suppress entry | entry-like `required`, `confirming`, `filter`; blocking groups use `blocking` |
| Exit path | `exit`, `invalidation`, `risk_exit`, `time_stop` | `exit`, `invalidation` |

## Exact Proposed Condition Structure

### Entry Candidate: Close Below Fixed SMA

Computable baseline condition:

```json
{
  "group_id": "ENTRY-001",
  "group_role": "required",
  "logic": "all",
  "conditions": [
    {
      "condition_id": "ENTRY-CLOSE-LT-SMA",
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
        "operand_type": "indicator_ref",
        "ref": "sma",
        "field": "value",
        "timeframe": null,
        "lookback": { "bars": 20 }
      },
      "units": null,
      "notes": null
    }
  ],
  "subgroups": [],
  "notes": null
}
```

Meaning: `close < sma(close, 20)`.

Compile-probe result: pass.

### Exit Candidate: Close At Or Above Fixed SMA

Computable exit condition:

```json
{
  "group_id": "EXIT-001",
  "group_role": "exit",
  "logic": "all",
  "conditions": [
    {
      "condition_id": "EXIT-CLOSE-GTE-SMA",
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
      },
      "units": null,
      "notes": null
    }
  ],
  "subgroups": [],
  "notes": null
}
```

Meaning: `close >= sma(close, 20)`.

Compile-probe result: pass.

### Entry-Distance Threshold

Intended condition:

```text
close sufficiently below SMA by entry_distance_threshold
```

Current compiler-compatible representation found: none.

Reason: the current compiler evaluates one left operand, one closed comparison operator, and one right operand. It cannot express any of these required SMA-distance forms:

```text
close <= sma * (1 - threshold)
sma - close >= threshold
(sma - close) / sma >= threshold
```

A probe using `indicator_ref sma gt parameter_ref entry_distance_threshold` compiles, but it does not compare close to SMA distance. It only compares the SMA value to a scalar parameter and is not a valid SMA-distance threshold.

Decision impact: the current first spec can only express the simpler `close < sma` entry unless Main/Karl authorizes a compiler-extension tranche or selects a different current-compiler-compatible shape.

### ATR Stop Multiplier / Risk

`research/schemas/strategy_spec.schema.json` allows `risk_model.stop_distance` to record a distance value, including a `parameter_ref`. This can pre-register an ATR stop multiplier as schema metadata.

Repo truth shows no current active consumer:

- `tools/research_runner/spec_signal_compiler.py` does not read `risk_model.stop_distance`.
- `tools/research_runner/run_offline_sweep.py` validates parent artifacts and uses synthetic runner inputs; it does not compile or apply Strategy Spec risk stops.
- `lib/backtest.py` consumes a precomputed `signal` and does not consume Strategy Spec `risk_model`, ATR stop distance, or target distance fields.

Conclusion: ATR stop multiplier is design metadata / future execution-risk parameter only in the current path, not an active compiled stop for WP-S2c-202/203.

### Max Holding Period

`exit_logic.max_holding_period` is active in the current compiler when:

```json
{
  "enabled": true,
  "bars": 96
}
```

`bars` must be a literal integer. A non-committed probe with `bars` encoded as a `parameter_ref` failed with:

```text
SpecSignalCompilerError: enabled max_holding_period requires integer bars >= 1
```

Conclusion: max holding period can be fixed for this spec, but `max_holding_bars` cannot be swept under the current compiler.

## Proposed Fixed Lookbacks

| Fixed value | Proposed literal | Rationale |
|---|---:|---|
| `sma_lookback_bars` | 20 | Fixed short mean-reversion anchor for 15m bars; compiler-compatible literal lookback. |
| `atr_lookback_bars` | 14 | Fixed conventional ATR window for future risk metadata; not active in the current signal path. |
| `max_holding_period.bars` | 96 | Fixed 24-hour cap at 15m bars if Main/Karl wants a time stop; compiler-compatible only as a literal. |

These are design-review defaults only. They are not swept free parameters.

## Proposed Swept Parameters

| Parameter | Intended role | Active now? | Where consumed | Include in WP-S2c-202? |
|---|---|---:|---|---|
| `entry_distance_threshold` | Require close to be sufficiently below SMA. | No | Not consumed as true SMA-distance by current compiler. | No, unless Main/Karl authorizes compiler extension or changes spec shape. |
| `atr_stop_multiplier` | ATR-derived hard stop distance. | No | Schema metadata only in `risk_model.stop_distance`; not consumed by compiler, runner, or backtester. | No, unless Main/Karl accepts schema-only sweep, which would not be active evidence. |
| `max_holding_bars` | Time stop / holding cap. | Literal only | Compiler consumes `exit_logic.max_holding_period.bars` only as integer literal. | No as swept parameter; yes only as fixed literal if accepted. |

Current compatible parameter count for an active WP-S2c-202 instance is therefore zero. Adding any swept parameter from the candidate list would require either accepting an inactive/schema-only parameter or authorizing a compiler/backtest path extension.

## Economic Rationale

Mean-reversion hypothesis: a large downside deviation from a short SMA may revert toward the local mean. This is a research hypothesis only. No profitability claim, ranking, recommendation, readiness, approval, or execution authority is created.

## Success / Failure Criteria

Success for this first-spec path means:

- Strategy Spec instance validates;
- variant manifest and sweep plan can be created without schema/compiler changes;
- all variants compile;
- sweep produces a complete result population;
- committed denominator is preserved;
- no canonical-path or protected-boundary violation occurs;
- result population validates.

Failure means:

- selected condition structure cannot compile;
- threshold, ATR, or max-holding parameters are not actually consumed as claimed;
- schema changes are needed;
- compiler changes are needed;
- runner/backtester changes are needed;
- result population cannot preserve the denominator.

## WP-S2c-202 Readiness Assessment

WP-S2c-202 ready after Main/Karl review: NO.

Blocker: the selected SMA-distance threshold cannot be represented by the current compiler, and ATR stop multiplier is not consumed by the current compiler, runner, or backtester. The only currently compiler-compatible SMA mean-reversion entry is the simpler `close < SMA(20)` baseline with optional fixed literal max holding. Main/Karl must decide whether that simpler baseline is acceptable for WP-S2c-202 or whether to open a compiler-extension tranche first.

## Compile Probe Result

Non-committed local compatibility probe:

| Probe | Result | Notes |
|---|---|---|
| `close < SMA(20)` entry and `close >= SMA(20)` exit with synthetic 15m OHLCV | pass | Produced a deterministic long/flat signal with values `[0.0, 1.0]`. |
| Naive `SMA > entry_distance_threshold` | pass but invalid for intended semantics | It does not encode close-to-SMA distance. |
| Parameterized `max_holding_period.bars` | fail | Compiler requires integer literal bars. |

No probe files were committed.

## Report-Back Questions

1. Is the surfaced `close < SMA(20)` entry and `close >= SMA(20)` exit structure accepted as compiler-compatible?
2. Because SMA-distance threshold is not compiler-compatible, should WP-S2c-202 use a simpler `close < SMA` baseline, choose a different current-compiler-compatible shape, or open a compiler-extension tranche?
3. Which swept parameters are allowed for WP-S2c-202 after the consumption check?
4. Are fixed lookbacks 20 for SMA and 14 for ATR acceptable?
5. Is fixed literal `max_holding_period.bars = 96` acceptable, or should max holding be disabled?
6. Is WP-S2c-202 authorized to create frozen instances after this design review clears?
