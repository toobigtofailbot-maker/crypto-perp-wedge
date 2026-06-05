# Closed Composition Extension Design

## Status / Authority

This is a design document only.

It does not implement schema changes. It does not implement compiler changes. It does not authorize first canonical Strategy Spec creation, canonical sweeps, result population creation, catalog changes, runner changes, backtester changes, or lib behavior changes. It creates no runtime, paper/live, OMS, reconciliation, risk, safe-mode, kill-switch, broker, exchange, order, or protected-path authority.

## Problem Statement

WP-S2c-201 surfaced a specific blocker in the intended first canonical SMA-distance Strategy Spec.

The first canonical SMA-distance spec needs a swept `entry_distance_threshold`. Current compiler behavior can express:

```text
close < SMA(20)
```

but cannot express:

```text
close < SMA(20) * (1 - entry_distance_threshold)
```

Without composition, the first sweep degenerates to zero active swept parameters. A degenerate single-variant sweep is not sufficient to validate the population path.

## Repo-Truth Discovery

Facts from refreshed `main`:

- `docs/project_status.md` records WP-S2c-201 / PR #378 as merged and says the SMA-distance threshold is blocked under the current compiler/runner/backtester surface.
- `docs/research_pipeline/2026-06-first_canonical_sma_distance_spec_design.md` records the compile-compatible baseline as `close < SMA(20)` entry plus `close >= SMA(20)` exit, and records `entry_distance_threshold` as not currently consumed.
- `docs/research_pipeline/2026-06-computation_binding_tranche_checkpoint.md` records current operands as `data_ref`, `indicator_ref`, `parameter_ref`, and `constant`; operators as `gt`, `gte`, `lt`, `lte`, `eq`, and `neq`; and composition as not implemented.
- `research/schemas/strategy_spec.schema.json` defines one closed `operand` object with required `operand_type`, `ref`, `field`, `timeframe`, and `lookback`; `operand_type` is currently limited to `data_ref`, `indicator_ref`, `parameter_ref`, and `constant`; `additionalProperties` is false.
- `research/schemas/indicator_catalog.schema.json` and `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json` preserve Option A: catalog interface only, compiler-owned implementation, no computation in catalog data.
- `tools/registry/validate_strategy_specs.py` is schema-first and adds semantic checks for closed operators, max condition depth, free-parameter rules, forbidden executable keys, non-authority flags, and host-data-reference safety.
- `tools/registry/validate_indicator_catalogs.py` recursively rejects forbidden executable/authority keys and enforces the exact SMA/EMA/ATR/StdDev catalog entry set and builtin pairing.
- `tools/research_runner/spec_signal_compiler.py` resolves operands through `_resolve_operand`, compares scalar/series values through closed stateless operators, rejects `both`, `crosses_*`, `in_set`, `is_true`, `is_false`, non-empty operand timeframes, non-literal indicator lookbacks, missing parameter refs, forbidden keys, and unknown operand types.
- `tests/test_spec_signal_compiler.py` covers data refs, indicator refs, parameter refs, constants, unsupported operators, null-never-true behavior, max holding period, forbidden keys, no writes, and backtester consumability.
- `tools/research_runner/run_offline_sweep.py` validates Strategy Spec / variant manifest / sweep plan parents, rejects formula execution in sweep plans, uses synthetic runner inputs, and does not compile Strategy Specs into real signals.
- `lib/backtest.py` consumes a precomputed signal and OHLCV/funding frames; it does not consume Strategy Spec operands, composition, risk model stop distances, or catalog data.
- `lib/evaluation.py` consumes backtest results and parameter metadata; it does not consume Strategy Spec operands or composition.

Inference from these facts:

- WP-S2c-205 would likely need Strategy Spec schema changes, and possibly Strategy Spec validator semantic checks.
- WP-S2c-206 would likely need compiler and compiler-test changes.
- Runner, backtester, and evaluation changes are not required for the proposed closed operand composition. If later repo truth shows they are required, that is a halt condition rather than scope expansion.

## Non-Executable Boundary

The extension must preserve Option A:

```text
Catalog remains interface-only.
Compiler owns reviewed computation.
Strategy Spec remains declarative.
Composition is closed and schema-validated.
Compiler evaluates only reviewed closed forms.
No open arithmetic.
No expression language.
No arbitrary formulas.
No notes-as-computation.
```

Hard prohibitions:

- no `expression`, `formula`, `code`, `script`, `eval`, `exec`, `lambda`, `function`, `callback`, `python`, `javascript`, `sql`, `shell`, `url`, or `file_path` fields;
- no free-form arithmetic strings;
- no operator-precedence language;
- no nested arbitrary AST;
- no user-defined functions;
- no catalog-data-interpreted computation;
- no dynamic import;
- no runtime action.

## Proposed Representation Options

### Option A - New Operand Type: `composed_operand`

Example:

```json
{
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
```

Evaluation:

- Schema clarity: strong. The schema can branch between normal operands and a separate composed shape.
- Compiler implementation simplicity: strong. `_resolve_operand` can dispatch to one reviewed closed composition resolver.
- Backward compatibility: controlled. Existing operands remain unchanged.
- Forbidden-key safety: strong. The composed shape can have a tiny required-key set and `additionalProperties: false`.
- Risk of becoming expression language: lower than a generic wrapper because composition is visible and auditable at the operand type boundary.
- Ease of validation: strong. Validators can count and reject composed operands in contexts where they are not authorized.
- Scope containment: strong. The extension does not turn every operand into a possible hidden computation surface.

### Option B - Composition Wrapper On Existing Operand

Example:

```json
{
  "operand_type": "indicator_ref",
  "ref": "sma",
  "field": "value",
  "timeframe": null,
  "lookback": { "bars": 20 },
  "composition": {
    "composition_type": "scale_by_one_minus_parameter",
    "parameter_ref": "entry_distance_threshold"
  }
}
```

Evaluation:

- Schema clarity: weaker. The existing operand definition would need a new optional `composition` surface.
- Compiler implementation simplicity: mixed. Existing operand resolvers would need to check whether an otherwise ordinary operand has hidden post-processing.
- Backward compatibility: reasonable if optional, but it changes the semantics of existing operand objects.
- Forbidden-key safety: adequate only if the wrapper is tightly closed.
- Risk of becoming expression language: higher because every operand can become a carrier for hidden arithmetic.
- Ease of validation: weaker. Auditing all composition locations requires inspecting optional keys across all operand types.
- Scope containment: weaker. The wrapper broadens the meaning of ordinary operands.

### Recommendation

Recommend Option A: a distinct `operand_type = "composed_operand"`.

Reason: current repo truth already has one closed operand definition and one compiler dispatch point. A distinct operand type is easier to schema-validate, easier to reject in old or unauthorized contexts, easier to count and audit, and less likely to turn every existing operand into a hidden expression surface.

## Closed Composition Forms

Possible closed enum candidates:

```text
scale_by_one_minus_parameter
scale_by_one_plus_parameter
offset_minus_parameter
offset_plus_parameter
```

Recommended minimum set for WP-S2c-205 / WP-S2c-206:

```text
scale_by_one_minus_parameter
```

This is the only form required to unblock:

```text
close < SMA(20) * (1 - entry_distance_threshold)
```

`scale_by_one_plus_parameter` may be useful for later symmetric short or upper-threshold logic, but it is not needed for the first long-only spec. `offset_minus_parameter` and `offset_plus_parameter` are not needed for the first spec and should be deferred unless Main explicitly wants them in the first extension.

Explicitly rejected for this extension:

- arbitrary multiply;
- arbitrary add/subtract;
- nested compositions;
- composition of `composed_operand`;
- multi-parameter compositions;
- constant coefficients outside the closed form;
- string formulas;
- ASTs.

## Proposed Condition Encoding

Target condition:

```json
{
  "condition_id": "ENTRY-CLOSE-LT-SMA-SCALED",
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
  },
  "units": "ratio",
  "notes": null
}
```

Semantics:

```text
right_series = SMA(20) * (1 - entry_distance_threshold)
condition true when close < right_series
```

## Parameter Constraints

Recommended `entry_distance_threshold` declaration constraints:

```text
type: number
role: entry
units: ratio
range min: 0
range max: 0.20
inclusive_min: false
inclusive_max: true
included_in_variant_generation: true
is_free_parameter: true
```

`inclusive_min: false` is recommended because a zero threshold collapses back to `close < SMA(20)` and weakens the point of the first canonical swept parameter. `0.20` is a conservative upper bound for a ratio threshold and keeps the first extension bounded. Main/Karl may choose a different upper bound during the later instance package.

This design does not define the exact sweep grid for WP-S2c-202. Non-binding future examples could include small ratios such as `0.0025`, `0.005`, or `0.01`, but grid selection belongs to a later authorized Strategy Spec / variant package.

## Compiler Evaluation Surface

WP-S2c-206 should evaluate the closed form through one reviewed path:

1. Resolve `base_operand` using the existing operand resolver.
2. Resolve `parameter_operand` using the existing `parameter_ref` resolver.
3. Validate `composition_type` is exactly in the closed enum.
4. For `scale_by_one_minus_parameter`, compute `base_series * (1 - parameter_value)`.
5. Preserve index alignment with the OHLCV index.
6. Preserve null behavior: null operand implies the condition is false through the existing comparison evaluator.
7. Preserve no-lookahead: base series must already be no-lookahead.
8. Return the composed series as operand value to the existing comparison evaluator.

No other computation path is authorized by this design.

## Schema / Validator Implications For WP-S2c-205

WP-S2c-205 likely needs to modify:

```text
research/schemas/strategy_spec.schema.json
possibly tools/registry/validate_strategy_specs.py if semantic checks are needed
tests for strategy spec validation
```

This package does not modify those files.

Likely schema constraints:

- `operand_type` enum extends with `composed_operand`;
- `composed_operand` requires `composition_type`, `base_operand`, and `parameter_operand`;
- `composition_type` is a closed enum;
- `base_operand` is initially restricted to `data_ref` or `indicator_ref`;
- `parameter_operand` is restricted to `parameter_ref`;
- no nested `composed_operand`;
- no `additionalProperties`;
- no forbidden keys.

## Compiler / Test Implications For WP-S2c-206

WP-S2c-206 likely needs to modify:

```text
tools/research_runner/spec_signal_compiler.py
tests/test_spec_signal_compiler.py
```

Expected compiler behavior is limited to operand resolution and existing comparison evaluation. No changes are expected for:

```text
tools/research_runner/run_offline_sweep.py
lib/backtest.py
lib/evaluation.py
```

If later repo truth proves runner, backtester, or evaluation changes are required, that should halt the package rather than broaden it.

## Explicit Deferrals

Out of scope and deferred:

- ATR-stop consumption;
- `risk_model.stop_distance` consumer behavior;
- lookback parameter binding;
- `both` direction;
- `crosses_above` / `crosses_below`;
- `in_set` / `is_true` / `is_false`;
- `z_score` composition;
- VWAP / RVOL / Donchian / RSI;
- session or multi-timeframe support;
- order-book, liquidation, CME, or other advanced data features;
- runner, backtester, or lib modification;
- canonical Strategy Spec instances;
- canonical sweeps or result populations.

## Success / Failure Criteria

Success:

- Main/Karl can review a closed composition representation.
- The representation is schema-validatable.
- The representation is not an expression language.
- It unblocks `close < SMA(20) * (1 - entry_distance_threshold)`.
- It does not require runner, backtester, or lib changes.
- It provides a narrow path for WP-S2c-205 and WP-S2c-206.

Failure:

- design requires arbitrary arithmetic;
- design creates expression-language shape;
- design requires formulas or notes-as-computation;
- design requires runner, backtester, or lib changes;
- design creeps into ATR-stop, lookback-binding, `both`, `crosses_*`, or `z_score`;
- design cannot be schema-validated cleanly.

## Recommended Report-Back Questions

1. Is the recommended representation accepted: `composed_operand` or wrapper composition?
2. Is the first closed form limited to `scale_by_one_minus_parameter`?
3. Should `scale_by_one_plus_parameter` be included now or deferred?
4. Should offset forms be deferred?
5. Are base operands initially limited to `data_ref` and `indicator_ref`?
6. Are parameter operands limited to `parameter_ref` only?
7. Is no nested composition accepted as a hard rule?
8. May Side auto-draft WP-S2c-205 after this design review clears?
