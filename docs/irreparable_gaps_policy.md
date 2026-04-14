# Irreparable Official-Source Gaps Policy

An irreparable official-source gap is a bar that remains missing after checking all three official Binance source paths used by the Phase 2 data pipeline:

1. `data.binance.vision` monthly archive.
2. `data.binance.vision` historical daily archive.
3. Binance official REST endpoint.

This policy is the explanation and exception registry contract for those gaps. It is not raw data.

## Manifest Relationship

`data/irreparable_gaps.json` is the manifest of known irreparable gaps. It records the stream, interval, UTC range, bar count, and verification date for each accepted exception.

Do not edit the manifest as part of docs/workflow packages. Data packages must update it only when validation proves the official-source gap still cannot be repaired.

## Validator Behavior

Validators may accept a dataset with irreparable gaps only when the bounded D2-003A tolerances are met for the affected `(stream, interval)` file:

- Total irreparable bars are no more than `0.01%` of expected bars.
- No single contiguous irreparable window exceeds `8` bars.
- No irreparable window falls within the most recent `90` days of the declared range.

Any breach fails validation and blocks the package until the data issue is repaired or escalated through the decision process.

## Downstream Research / Backtests

Research and backtest code must consult `data/irreparable_gaps.json` and either skip affected bars or handle them explicitly. Silent interpolation is forbidden.

Treat these entries as documented official-source exceptions, not as permission to ignore data quality.
