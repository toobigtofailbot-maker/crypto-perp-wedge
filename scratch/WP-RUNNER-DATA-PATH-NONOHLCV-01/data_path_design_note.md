# Declared Non-OHLCV Data Path Design Note

## Fact

The compiler can already resolve allowed non-OHLCV `data_ref` fields from the supplied OHLCV frame when those fields are present. The runner previously dropped all columns except `open`, `high`, `low`, `close`, and `volume` during CSV materialization.

## Decision

Implement only runner-side declared-column preservation.

## Contract

- Always require `open`, `high`, `low`, `close`, `volume`.
- Collect declared non-OHLCV fields from Strategy Spec `data_ref` operands and `timeframe_and_data.host_data_refs`.
- Do not require or preserve timestamp-derived refs as CSV columns because they are derived from the UTC index.
- Preserve only declared non-OHLCV CSV columns.
- Drop undeclared extra CSV columns.
- Fail closed when a declared non-OHLCV column is absent from input.
- Fail closed when a declared non-OHLCV field lacks a `FULL_HISTORY_PUBLIC_ARCHIVE` availability label.
- Add `data_availability_claim` only when declared non-OHLCV fields exist.
- Include `data_availability_claim` in both input and result identity scopes when present.
- Leave the OHLCV-only default scope unchanged.

## Boundary

No changes were made to backtest fill logic, position accounting, fee/slippage/funding semantics, compiler operator semantics, canonical evidence rules, runtime, paper/live, OMS, risk, reconciliation, or capital paths.
