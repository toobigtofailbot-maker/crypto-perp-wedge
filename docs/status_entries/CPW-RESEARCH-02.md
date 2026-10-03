# CPW-RESEARCH-02 — Data/feature expansion

Status: D4-native implementation and focused physical acceptance complete on
`codex/cpw-research-02-data-feature-expansion`; final full-release and
publication evidence are recorded before PR handoff.

## Source-contract closure

The authoritative full-history source for `taker_buy_volume`,
`taker_sell_volume`, and `taker_buy_sell_ratio` is now
`CANONICAL_D4_KLINE_DERIVATION`. Recent-only REST catalog entries remain
unchanged. `PUBLIC_TRADE_ARCHIVE_DERIVATION` is no longer an authoritative
full-history catalog entry.

The parent is the canonical Binance USD-M BTCUSDT 15m D4 slice:

```text
binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664
c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab
2020-01-01T00:00:00Z inclusive to 2026-04-12T00:00:00Z exclusive
```

## Physical proof

- Parent rows: 220,128.
- Derived feature rows: 220,128.
- Missing bars: 0.
- Duplicate timestamps: 0.
- Invalid buy rows: 0.
- Invalid sell rows: 0.
- Zero-sell rows: 15.
- Null-ratio rows: 15, exactly the zero-sell rows.
- Every other ratio is present and finite.
- Exact one-to-one D4 alignment: 220,128.
- Repeat output and feature-table identities: equal.

```text
feature output SHA-256:
c726d5a73a2d2168404c2a3599c477f9bea7ab5066d59c3f090a456b8efeffba

source_set_identity:
sha256:a706affa0f3b3be362ffeb523d8dcd6805235127618760e13a16b7d6969f411e

feature_table_identity:
sha256:0ab8af18c78d274d7ac4e3b11a9701d7e604e5c9a8e746b6000e1cca4f79403c

three-column projection SHA-256:
35b29807d6347cb46c552f8b2a1f0f409221d601f9c6a8b503d3d48890de5aba
```

## Historical comparison

The accepted May-2023 raw-trade proof remains diagnostic evidence. D4-native
buy, sell, and ratio match all 2,976 rows exactly with zero mismatches.

At `2024-05-06T07:00:00Z`, both official monthly and complete daily-union raw
trades report volume `1726.888`, trade count `29673`, buy `823.011`, and sell
`903.877`; canonical D4 reports `1725.914`, `29627`, `822.33`, and `903.584`.
The raw sources were not accepted, corrected, averaged, spliced, or
tolerance-adjusted. Canonical D4 is authoritative.

The 12 accepted 2020 raw-trade cache/result pairs remain intact as local
historical diagnostic evidence. No remaining raw-trade history was processed.

## Consumer and boundary result

Availability validation, formalization, experiment-runner/bridge blocking,
readiness projection, feature-table schema/domain validation, generic runner
integration, and Result Population source binding use the new source class.
The preserved runner hook remains source-agnostic and contains no D4 formulas.

Raw archive helpers are diagnostic-only. The obsolete TRADES hydration manifest
and the unnecessary `tools/research_domain/__init__.py` re-export change are not
part of the final diff.

All outputs remain noncanonical offline research/workbench artifacts. This
package grants no execution, candidate, promotion, runtime, paper/live, OMS,
reconciliation, risk, capital, or self-merge authority.
