# Binance USDT-M 15m OHLCV Data Contract

## Scope

This D1 contract defines the repo-governed data contract for real Binance USDT-M 15m OHLCV research history.

Package posture:

- Design only.
- Offline research data only.
- No ingestion implementation.
- No canonical data import.
- No validators, schemas, catalog artifacts, slice artifacts, or result populations.
- No runtime, paper, live, OMS, reconciliation, risk, safe-mode, credential, or exchange-order contact.

## Repo-Truth Baseline

Fact:

- `docs/data_catalog.md` already records BTCUSDT 15m OHLCV full history at `data/processed/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`, sourced from `data.binance.vision` bulk archives plus Binance Futures API repair, with SHA256 `3fd05b841210962147a92bd77167ccefce57f6eb812cb55565d6f6cbb5154c31`.
- `docs/data/intraday_data_assessment.md` records that existing 15m OHLCV coverage is continuous for 2020-01-01 through 2026-04-11 and data-ready for future OHLCV-only 15m hypotheses.
- `research/result_populations/RP-2134.result_population.json` is pipeline evidence from a temporary 96-row CSV fixture, with `data_catalog_ref=15m_ohlcv_test_fixture_offline_only`; it is not production exchange-history strategy-quality evidence.
- `STRAT-SPEC-0001`, `VM-0001`, and `SWEEP-PLAN-0001` define the current first canonical 15m SMA-distance parent set with committed denominator 7.

Inference:

- D2 can use the prior Phase 2 data-foundation pattern as a reference, but D1 does not promote any existing local data file into a new canonical real-data sweep slice.

Decision:

- This contract treats `data.binance.vision` offline bulk archives as the preferred canonical ingestion source for D2.
- Binance REST repair may be a bounded secondary official repair source if D2/D3 explicitly authorizes and documents it, but canonical ingestion must not depend on live runtime paths, exchange keys, or paper/live systems.

Open question:

- The exact D2 manifest/catalog artifact shape is intentionally deferred. D1 specifies required identity fields, not an implementation format.

Future option:

- Multi-symbol and non-15m extensions may reuse this shape later, but are out of scope for Data Block 1.

## Source Policy

Canonical research ingestion must use official Binance USDT-M Futures market-data sources.

Preferred source:

- Offline bulk archives from `data.binance.vision`.

Permitted only when explicitly authorized by a later D2/D3 package:

- Official Binance Futures REST repair for bounded source gaps after bulk archive checks.

Forbidden for canonical research ingestion:

- Exchange credentials.
- Private account endpoints.
- Runtime, paper, live, OMS, reconciliation, risk, or safe-mode paths.
- Any ingestion path that requires placing, canceling, simulating, or supervising orders.
- Any live API dependency as the normal canonical data path.

## Instrument And Timeframe

Initial scope:

- Instrument: BTCUSDT.
- Venue/market: Binance USDT-M perpetual futures.
- Stream: OHLCV klines.
- Timeframe: 15m.
- Symbol scope: single-symbol first.

Deferred:

- Multi-symbol data contracts.
- Sub-15m data.
- Tick, book, trades, mark, index, premium, funding, or cross-stream contracts unless separately authorized.

## Normalized Fields

Required normalized fields:

| Field | Required | Type expectation | Meaning |
|---|---:|---|---|
| `open_time` or `timestamp` | Yes | UTC timestamp | Bar-open timestamp and canonical index. |
| `open` | Yes | Numeric decimal-compatible | First traded price in the bar. |
| `high` | Yes | Numeric decimal-compatible | Highest traded price in the bar. |
| `low` | Yes | Numeric decimal-compatible | Lowest traded price in the bar. |
| `close` | Yes | Numeric decimal-compatible | Last traded price in the bar. |
| `volume` | Yes | Numeric decimal-compatible | Base asset volume. |
| `close_time` | Optional | UTC timestamp | Source-provided close timestamp, if retained as metadata. |
| `quote_volume` | Optional | Numeric decimal-compatible | Quote asset volume, if source provides it. |
| `trade_count` | Optional | Integer | Number of trades, if source provides it. |
| `taker_buy_base_volume` | Optional | Numeric decimal-compatible | Source metadata, if retained. |
| `taker_buy_quote_volume` | Optional | Numeric decimal-compatible | Source metadata, if retained. |

Requirements:

- Numeric OHLCV fields must parse deterministically and must not contain mixed units.
- Timestamp fields must parse as timezone-aware UTC or be normalized to timezone-aware UTC.
- Optional source metadata must not be required by strategy code unless a later package explicitly adds that data dependency.

## Timestamp Semantics

Canonical timestamp policy:

- UTC only.
- Bar-open timestamp is the canonical index.
- Bars are exactly 15 minutes apart except for explicitly recorded gaps.
- Bar interval convention is `[open_time, open_time + 15m)`.
- No duplicate `open_time` values.
- Canonical research slices contain closed candles only.
- The final candle must be excluded if it is incomplete at import time.

Close-time policy:

- If source `close_time` is retained, it is metadata only.
- Any source format with close-time-like values, including millisecond endpoints such as `00:14:59.999`, must be normalized so downstream identity and spacing use bar-open time.

## Gap Policy

Validators in D2/D3 must detect and report:

- Missing 15m open-time intervals.
- Duplicate open times.
- Out-of-order bars.
- Non-15m spacing that is not represented as an explicit gap.
- Known exchange-source outages or official-source gaps.

Forbidden:

- Silent OHLCV forward fill.
- Silent OHLCV interpolation.
- Synthetic candles represented as real exchange bars.
- Dropping missing bars without preserving a gap report.

Valid slice policy:

- A slice is valid only when missing intervals are either zero or explicitly documented under a repo-approved gap policy.
- Any gap threshold must be locked by D2/D3 before a real-data sweep. Until then, D5 must treat unresolved gap ambiguity as blocking.
- Known exchange outages must be recorded as explicit source exceptions, not hidden inside the normalized file.

Relationship to existing policy:

- `docs/irreparable_gaps_policy.md` governs known irreparable official-source gaps for prior Phase 2 streams.
- D2/D3 may reuse that policy shape for OHLCV only if validation proves the official-source gap cannot be repaired and the package explicitly records the exception.

## Duplicate Policy

Duplicate `open_time` values are invalid unless D2/D3 defines a deterministic, auditable source-precedence rule.

Any deduplication rule must preserve:

- The raw conflicting rows.
- The selected normalized row.
- The reason for selection.
- The source layer that supplied each conflicting row.
- The resulting normalized file hash.

## Integrity And Provenance

Every D2/D3 canonical slice must preserve or derive the following identity fields:

- `data_contract_version`.
- Source URL or source path for each raw archive.
- Raw file SHA256 for each downloaded archive.
- Normalized file SHA256.
- Import/download timestamp in UTC.
- Symbol: `BTCUSDT`.
- Market type: `USDT-M perpetual`.
- Stream: `ohlcv`.
- Timeframe: `15m`.
- Date range start and end.
- Row count.
- Expected row count.
- Gap summary.
- Duplicate summary.
- Normalization tool or process identity.
- Data catalog reference.
- Stable `data_slice_identity`.

Hash policy:

- Raw-source hashes must identify exact downloaded files.
- Normalized-file hashes must identify exact normalized output bytes.
- `data_slice_identity` must be stable across deterministic re-imports of the same source content and normalization rules.
- Any change to normalization rules, gap handling, date range, or source files must produce a distinct slice identity.

## Storage Format And Layout

D1 recommends, without implementing:

- Preserve raw archives outside committed repo history unless a later data package explicitly authorizes committed raw artifacts.
- Normalize to Parquet or the repo-approved research format used by D2.
- Keep normalized data under the repo's data-processing convention, currently represented by `data/processed/`.
- Record canonical metadata in a manifest/catalog entry rather than relying on filenames alone.
- Keep large raw and normalized data files out of ordinary docs-only packages.

Suggested naming convention for D2 consideration:

- Raw archive path records source, market, symbol, timeframe, and source date.
- Normalized path records market, symbol, stream, timeframe, date range, and created timestamp.
- Manifest/catalog identity records the same facts plus hashes and gap summary.

## D2/D3 Validation Requirements

D2/D3 validators or test evidence must cover:

- Required column/schema validation.
- Timestamp parse and UTC normalization.
- Monotonic open-time ordering.
- Exact 15m spacing except explicit gaps.
- Duplicate detection.
- OHLC consistency: `high >= max(open, close)`, `low <= min(open, close)`, and `high >= low`.
- Nonnegative volume.
- Row count expected versus actual.
- Raw-file hash verification.
- Normalized-file hash verification.
- Gap report generation.
- Duplicate report generation.
- Deterministic normalization on repeated import.
- Closed-candle final-bar exclusion.
- Explicit failure on unresolved source, timestamp, or gap ambiguity.

## D5 First Real-Data Sweep Readiness

D5 must not write a canonical real-data result population unless all of these are true:

- The D2/D3 15m OHLCV slice is validated.
- The slice has a stable `data_slice_identity`.
- Source, timestamp, gap, duplicate, and hash policies are unambiguous.
- The data catalog or manifest entry records enough provenance to reproduce the slice.
- `STRAT-SPEC-0001`, `VM-0001`, and `SWEEP-PLAN-0001` or their explicitly superseding frozen parents are still valid.
- The committed denominator remains 7 for the current first canonical parent set unless a future approved package supersedes it.
- All seven variants remain represented in result-population accounting.
- Karl authorization exists before the canonical real-data write.

## Stop Conditions

Stop before ingestion, validation, cataloging, or sweep work if any of the following are true:

- Live API contact is required.
- Credentials are required.
- The source is ambiguous.
- Timestamp semantics are ambiguous.
- Gap handling is ambiguous.
- Duplicate handling is ambiguous.
- Raw or normalized data identity is untrusted.
- The implementation would need runtime, paper, live, OMS, reconciliation, risk, safe-mode, config, or protected-path changes.
- The implementation would need to mutate frozen Strategy Spec, Variant Manifest, Sweep Plan, or existing result-population artifacts without explicit authorization.
- A first real-data canonical write is requested without Karl authorization.
