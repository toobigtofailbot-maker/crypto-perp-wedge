# WP-DATA-TAKERFLOW-ARCHIVE-RECON-01 Branch State

## Scope Summary

Adds a deterministic, offline reconstruction tool for local Binance USD-M
`trades` and `aggTrades` public archive CSV/ZIP files. The tool emits validated,
lineage-tracked JSON taker-flow slices and has no default or optional network
download path.

## Source Semantics

Only local public archive files are accepted. `FULL_HISTORY_PUBLIC_ARCHIVE` is
the required coverage class; recent-only REST is rejected as a historical
source. Parsers accept official headered or headerless layouts and fail closed
on missing, extra, malformed, blank, or invalid rows.

## buyerMaker Mapping

- `buyerMaker=true`: buyer is maker, seller is taker, so the row is taker sell.
- `buyerMaker=false`: buyer is taker, seller is maker, so the row is taker buy.

## Feature Outputs

Every bar includes taker buy, sell, net, and total base volume; buy/sell ratio;
and trade count. `trades` archives also preserve buy, sell, net, and total quote
volume. Exact decimal values are serialized as strings. For `aggTrades`, trade
count is the underlying trade-ID span, while quote features are omitted because
the archive does not supply quote quantity.

## Alignment Semantics

Bars use the repo's UTC bar-open convention and half-open membership
`[open_time, open_time + interval)`. Each row maps to one bar by epoch floor.
The tool sorts deterministically and performs no fill, backfill, interpolation,
or lookahead.

## Lineage Metadata

Slices record the source path/type/hash, symbol, USD-M perpetual market type,
interval, bar and source-event ranges, bar/source row counts, tool version,
generation time, public full-history coverage class, and explicit false flags
for private endpoint and network use. A caller may fix generation time for
byte-identical output.

## Boundary Summary

No dependencies, downloader, private endpoint, credential, vendor, backtester,
compiler, registry schema/validator, query layer, canonical RP, candidate
lifecycle, promotion/readiness, runtime, paper, live, OMS, reconciliation, risk,
overlay, safe-mode, config, or protected path is changed. Generated slices are
research/workbench artifacts with no execution or promotion authority.

## Validation Status

- Hand-calculation/parser/slice tests: PASS, 16 passed.
- Existing compiler and Strategy Spec regression tests: PASS, 336 passed.
- Strategy Spec validator: PASS.
- Result Population validator: PASS.
- Research query view discovery: PASS.
- Python compile check: PASS.
- Diff scope summary: PASS, five expected package files and no forbidden-path
  matches.
- `git diff --check`: PASS.
- Full pytest: PASS, 1,882 passed, 1 skipped, 6 existing warnings. The first
  isolated-worktree run had the known unrelated missing-local-D4A-file failure
  (1,881 passed); after copying the root checkout's gitignored normalized D4A
  CSV into this worktree for validation only, the failed test and full suite
  passed.

## Non-Authority Statement

This package reconstructs public data only. Its artifacts do not authorize
strategy evaluation, canonical evidence, candidate promotion/readiness,
backtester wiring, or runtime/paper/live use. Later use requires a separately
approved path.
