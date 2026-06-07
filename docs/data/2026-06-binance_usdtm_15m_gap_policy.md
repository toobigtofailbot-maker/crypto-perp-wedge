# Binance USDT-M 15m OHLCV Validation And Gap Policy

## Scope

This D3 policy applies to D2-normalized Binance USDT-M BTCUSDT 15m OHLCV CSV outputs.

Package posture:

- Offline validation only.
- Local files only.
- No live API.
- No exchange keys.
- No runtime, paper, live, OMS, reconciliation, risk, safe-mode, or execution contact.
- No data catalog mutation.
- No result-population write.
- No canonical sweep.

## Validation Input

The validator expects the deterministic D2 normalized CSV column set:

```text
open_time_ms, open_time, open, high, low, close, volume, close_time_ms,
quote_asset_volume, num_trades, taker_buy_base_vol, taker_buy_quote_vol, ignore
```

The column order is part of the schema expectation. A different column set or order is not treated as a valid D2-normalized file.

## Timestamp Policy

Fact:

- Bar identity is `open_time`.
- The expected cadence is exactly 15 minutes, or `900000` milliseconds.
- `open_time_ms` and `open_time` must identify the same UTC instant.

Decision:

- `open_time_ms` must be integer milliseconds.
- `open_time` must parse as UTC.
- `open_time_ms` must align to a 15m UTC boundary.
- Rows must be ordered by increasing `open_time`.

Open question:

- D4 still owns final catalog/slice-identity shape.

## Gap Policy

Decision:

- Gaps are detected by comparing unique bar-open timestamps to the exact 15m cadence.
- A missing interval is reported with `start_utc`, `end_utc`, and `missing_bars`.
- Any gap makes validation fail unless a later approved package creates an explicit repo-approved exception policy.

Forbidden:

- Fill.
- Interpolation.
- Synthetic candles represented as exchange bars.
- Silent dropping of missing bars.

Future option:

- A later package may define repo-approved official-source exceptions, but D3 does not create that exception mechanism.

## Duplicate Policy

Decision:

- Duplicate `open_time` values are invalid.
- Duplicate groups are reported with UTC timestamp and duplicate row count.
- The validator does not select a winner.

Forbidden:

- Silent deduplication.
- Source-precedence selection.
- Any transformation that turns duplicate rows into a passing normalized output.

Future option:

- A later package may define a deterministic source-precedence rule only if it preserves raw conflicting rows, selected normalized row, selection reason, source layer, and resulting normalized hash.

## OHLCV Policy

Validation fails when:

- `high < max(open, close)`.
- `low > min(open, close)`.
- `high < low`.
- `volume < 0`.
- Numeric fields are null, non-numeric, or non-finite.

## Invalid-Data Output Policy

Decision:

- Invalid input may write validation/provenance reports only.
- Invalid input must not create a downstream-consumable validated output.
- Report-only invalid validation may return zero for workflow use, but it still writes no downstream-consumable output.
- Valid input may optionally write an exact-byte copy to a caller-supplied validated-output path after PASS.

Forbidden:

- Normalized output for invalid data.
- Best-effort valid-looking output for invalid data.
- Fill, interpolation, deduplication, or synthesis as a fix.

Review question:

```text
Can invalid data produce a file that downstream code might consume as valid?
```

For this D3 policy and validator, the required answer is no.

## Determinism

The validation report is serialized as sorted JSON with stable report fields. Re-running validation against the same file and paths produces the same report bytes.

## D4 Readiness

D4 catalog/slice identity may follow only after D3 lands cleanly. D3 does not promote any validated file into the data catalog and does not authorize D5 real-data canonical sweep output.
