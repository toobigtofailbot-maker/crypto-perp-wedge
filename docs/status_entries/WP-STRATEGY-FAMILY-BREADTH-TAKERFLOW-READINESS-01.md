# WP-STRATEGY-FAMILY-BREADTH-TAKERFLOW-READINESS-01 Branch State

## Verdict

`READY-FOR-HYDRATION`.

The deterministic offline materializer is implemented and fixture-validated. The
exact worktree contains zero of the 76 required full-history monthly BTCUSDT
`aggTrades` archives, so this package does not claim `DATA-READY`.

This is data readiness only. It is not a strategy conclusion, candidate decision,
Result Population, edge claim, GO/NO-GO, promotion, runtime, or execution state.

## Repo-Truth Discovery

- Base: `6994e9000aa6dcf56a7f1a4a08712ba778ea8bbe`.
- Funding carry is already concluded and was not built or retested.
- `tools/data_ingestion/takerflow_archive_recon.py` already provides strict
  single-archive `trades` / `aggTrades` parsing and buyer-maker direction.
- The stale prior taker-flow blocker said non-OHLCV columns were stripped. Current
  repo truth is newer: commit `4c2cf40` already makes
  `tools/research_runner/run_offline_sweep.py` collect and retain declared
  non-OHLCV columns when they are present in the runner's combined OHLCV CSV.
- The remaining data blocker was multi-archive materialization, duplicate/gap and
  denominator accounting, full requested-range coverage, and source/output
  identities. The runner still has no provenance-bound feature-table join seam.

## Delivered Files

- `tools/data/materialize_takerflow_features.py`: local-file-only multi-archive
  streaming materializer and hydration/checksum checker. It retains bar aggregates
  rather than six years of event rows in memory.
- `tests/test_takerflow_feature_materialization.py`: fixture-backed direction,
  bucketing, causality, duplicates, gaps, coverage, hashing, hydration, and
  fail-closed tests.
- `research/data_feature_availability/BINANCE-USDM-BTCUSDT-AGGTRADES-HYDRATION-0001.json`:
  exact full-history local hydration contract.

No large dataset is committed. Fixture-run CSV/manifest outputs remain ignored
under `data/processed/`.

## Accepted Source Formats

Each materialization run accepts one homogeneous source type; `trades` and
`aggTrades` are never mixed or double-counted in one run.

| Source | Local container | Exact fields | Event count semantics |
| --- | --- | --- | --- |
| Binance USD-M `trades` | UTF-8 CSV or ZIP with exactly one CSV member; header or official headerless layout | `trade_id, price, qty, quote_qty, time, is_buyer_maker` | one source row equals one trade |
| Binance USD-M `aggTrades` | UTF-8 CSV or ZIP with exactly one CSV member; header or official headerless layout | `agg_trade_id, price, quantity, first_trade_id, last_trade_id, transact_time, is_buyer_maker` | underlying trade count is `last_trade_id - first_trade_id + 1` |

The exact full-history hydration contract selects monthly `aggTrades` because it
contains all required base-volume, taker-direction, event-time, identity, and
underlying-trade-count fields at a smaller local footprint than raw `trades`.

## Buyer-Maker Direction

Binance's flag identifies whether the buyer was the maker, not whether the buyer
was the taker:

- `is_buyer_maker=true`: buyer supplied liquidity, seller was the aggressor/taker,
  so quantity contributes to taker sell volume.
- `is_buyer_maker=false`: seller supplied liquidity, buyer was the
  aggressor/taker, so quantity contributes to taker buy volume.

Both source shapes and both directions are covered by hand-calculated fixtures.

## Output Feature Schema

Schema version: `takerflow-feature-table-v1`. Output is deterministic UTF-8/LF
CSV for consistency with the existing declared-column runner input convention.
Decimal feature values are canonical base-asset decimal text; ratios use decimal
precision 38 rather than binary floating-point aggregation.

| Column | Meaning |
| --- | --- |
| `timestamp` | UTC bar open, ISO-8601 |
| `open_time_ms` | UTC bar open epoch milliseconds |
| `feature_available_at` | exclusive UTC bar close; earliest causal observation time |
| `feature_available_at_ms` | same boundary in epoch milliseconds |
| `taker_buy_volume` | base quantity where buyer was taker; already compiler-visible |
| `taker_sell_volume` | base quantity where seller was taker; already compiler-visible |
| `taker_total_volume` | buy plus sell base quantity |
| `taker_net_volume` | buy minus sell base quantity |
| `taker_imbalance` | `(buy - sell) / (buy + sell)` |
| `taker_buy_sell_ratio` | `buy / sell`, null when sell is zero; already compiler-visible |
| `trade_count` | underlying trades, including aggregate-trade ID spans |
| `source_record_count` | archive rows contributing to the bar |

The three compiler-visible names are taken from the current feature-availability
catalog and compiler vocabulary. The total/net/imbalance and count columns are
diagnostic materialization fields only; this package does not add them to the
compiler catalog.

## Causal Alignment and Quality Rules

- Supported intervals are exactly the locked project set: `15m`, `30m`, `1h`,
  `4h`, and `1d`.
- UTC integer bucketing uses `[bar_open, bar_close)`. An event exactly on a close
  boundary belongs to the next bar.
- Output rows carry the bar-open timestamp but become usable only at the exclusive
  close in `feature_available_at`.
- A future event cannot change a prior completed bar; the fixture prefix test
  proves this invariant.
- Each archive must be internally monotonic by `(timestamp, event_id)`.
- Exact adjacent partition-boundary event-ID duplicates are deterministically
  removed and counted. A conflicting duplicate or broader out-of-order overlap
  fails closed.
- Internal event-ID gaps are listed explicitly.
- Empty expected bars are omitted, never zero-filled, and disclosed as exact
  missing-bar ranges. Full-range readiness requires zero missing bars.
- Parsed, deduplicated, in-range, before-range, and after-range counts have explicit
  accounting identities; invalid/blank rows fail rather than disappear.
- Every source file has path, byte length, SHA-256, parsed row count, and monotonic
  status in the manifest. The output has schema, row count, byte length, and
  SHA-256.

## Fixture Hash and Coverage Evidence

The committed `trades_hand_calc.csv` source SHA-256 is
`9dc905cad650b3df7b1c385555d382e8ec72c7d4b453714435c164421a747950`.

Two consecutive materializations produced the identical output SHA-256
`e9efdce17d786c304e237c3fc43358fee1da6230ead768b92ad571519ee7e367`.
The manifest-reported hash matched both filesystem hashes. Fixture coverage was
`3/3` expected bars, with zero missing bars and zero event-ID gaps.

## Exact Full-History Hydration Requirement

`BINANCE-USDM-BTCUSDT-AGGTRADES-HYDRATION-0001` requests:

- symbol/market: Binance USD-M perpetual `BTCUSDT`;
- source: public monthly `aggTrades` archives;
- window: `2020-01-01T00:00:00.000Z` inclusive through
  `2026-04-12T00:00:00.000Z` exclusive;
- output interval: `15m`;
- denominator: 220,128 requested bars;
- partitions: 76 monthly ZIPs, `BTCUSDT-aggTrades-2020-01.zip` through
  `BTCUSDT-aggTrades-2026-04.zip`;
- local ignored root:
  `data/raw/binance/futures/um/monthly/aggTrades/BTCUSDT`;
- integrity: verify every ZIP against its Binance `.CHECKSUM` sidecar before the
  offline materializer is run.

The hydration checker reports 0/76 archives and 0/76 checksum sidecars present,
with `READY-FOR-HYDRATION`. It verifies sidecar SHA-256 values when local files
exist and reports `BLOCKED` on a mismatch. The materializer performs no network
access.

## Exact Post-M1 Runner / Data-Source Follow-Up

No new column-preservation primitive is needed: current repo truth already retains
declared non-OHLCV fields when they are in the combined input CSV.

The exact later delta is one provenance-bound 15m composite-input seam, after M1:

1. accept the existing validated D4 OHLCV parent identity plus this materializer's
   feature-table manifest and output identity;
2. require the feature manifest to be `takerflow-completed-bars-v1`, requested-range
   complete, zero-gap, and bound to the same 220,128-bar UTC grid;
3. verify `timestamp` one-to-one, `feature_available_at = timestamp + 15m`, both
   parent hashes, output hash, schema version, and the three
   `PUBLIC_TRADE_ARCHIVE_DERIVATION` availability claims;
4. left/inner equivalence-check the join with no fill, interpolation, row loss, or
   timestamp tolerance, then pass only the already-declared
   `taker_buy_volume`, `taker_sell_volume`, and `taker_buy_sell_ratio` columns to
   the existing declared-column path;
5. record both parent identities and the join/materializer identities in execution
   provenance without changing signal timing, fills, fees, funding, sizing,
   backtest math, compiler grammar, or catalog vocabulary.

This follow-up is runner/data-source integration work and is not implemented or
authorized by this package.

## Validation

- Focused T1/T2 pytest over the materializer, prior archive reconstructor, public
  source adapter, and data-feature availability layer: `55 passed`.
- Direct `validate_data_feature_availability.py`: pass.
- Two consecutive fixture materializations plus manifest/filesystem comparison:
  identical SHA-256 `e9efdce17d786c304e237c3fc43358fee1da6230ead768b92ad571519ee7e367`.
- Hydration inspection: `READY-FOR-HYDRATION`, 76 archives missing, 76 checksum
  sidecars missing, zero checksum mismatches.
- `git diff --check`: pass.
- Full suite not run by package design because runner/compiler/runtime semantics
  are unchanged.

## Boundaries

No network fetch, vendor/private source, funding-carry work, canonical data
promotion, candidate/RP/REP/GO/NO-GO evidence, trial log, H004/M1 artifact,
compiler grammar/catalog, runner/backtester semantic, runtime, paper/live, OMS,
risk, reconciliation, safe-mode, config, or dependency path changed.
