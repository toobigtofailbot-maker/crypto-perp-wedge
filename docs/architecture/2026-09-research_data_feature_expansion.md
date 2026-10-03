# Research Data/Feature Expansion Architecture

## Ownership and source contract

The authoritative RESEARCH-02 producer derives the three research-visible
taker-flow fields directly from the canonical Binance USD-M BTCUSDT 15-minute
D4 parent. Its source class is `CANONICAL_D4_KLINE_DERIVATION`; the coverage
class remains `FULL_HISTORY_PUBLIC_ARCHIVE` and is conditional on the exact D4
identity and coverage window.

The locked formulas are:

```text
taker_buy_volume = taker_buy_base_vol
taker_sell_volume = volume - taker_buy_base_vol
taker_buy_sell_ratio = null when taker_sell_volume == 0,
                       otherwise taker_buy_volume / taker_sell_volume
```

`tools.research_domain.feature_data` owns the engine-neutral feature-data
identity and semantic contract. `tools.data.research_feature_table` owns local
byte validation, parent binding, formula/null validation, and the exact causal
join. The compiler consumes the resulting columns but owns neither their
derivation nor their identity. The offline runner remains a source-agnostic
compatibility consumer of the generic resolver; it contains no D4 formulas.

## Parent and derived identity

The authoritative parent is fixed to:

```text
data-slice identity:
binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664

normalized SHA-256:
c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab

coverage:
2020-01-01T00:00:00Z inclusive to 2026-04-12T00:00:00Z exclusive

rows: 220128
```

The manifest binds that parent identity, normalized hash, row count, coverage,
derivation version, exact formulas, ratio-null policy, feature list,
availability timing, output count, and output hash. A parent hash or identity
change necessarily changes the source-set and feature-table identities.

The composite runner `data_slice_identity` commits to the verified D4 parent,
feature-table identity, selected feature names, and exact join contract.
Machine-local paths, mtimes, hostnames, PIDs, temporary directories, and wall
clock values are excluded from scientific identities.

The accepted physical proof identities are:

```text
source_set_identity:
sha256:a706affa0f3b3be362ffeb523d8dcd6805235127618760e13a16b7d6969f411e

feature_table_identity:
sha256:0ab8af18c78d274d7ac4e3b11a9701d7e604e5c9a8e746b6000e1cca4f79403c

feature CSV SHA-256:
c726d5a73a2d2168404c2a3599c477f9bea7ab5066d59c3f090a456b8efeffba

three-column projection SHA-256:
35b29807d6347cb46c552f8b2a1f0f409221d601f9c6a8b503d3d48890de5aba
```

Two complete materializations produced identical identities and output hashes.

## Causality and null semantics

Every feature row is stamped at parent bar open and has
`feature_available_at = open + 15m`, the exclusive completed-bar close. The
resolver requires exact one-to-one timestamp equality and permits no fill,
interpolation, tolerance, or as-of join. Derivation is row-local, so future bars
cannot modify a completed row. Existing signal-at-completed-bar and
next-bar-open-fill semantics remain unchanged.

The complete parent contains 15 valid zero-trade/zero-volume bars. Their derived
sell volume is zero and the ratio is null. Null is forbidden for buy and sell,
and forbidden for ratio on every nonzero-sell row. The compiler already
preserves null data-derived inputs without filling; no compiler or backtester
semantic change is part of RESEARCH-02.

## Raw-archive diagnostic posture

Raw `trades` and `aggTrades` parsing/reconstruction remain historical diagnostic
tools only. They do not determine authoritative feature values, coverage,
completeness, source class, or accepted RESEARCH-02 cache authority. The 12
accepted 2020 raw-trade partitions and the accepted May-2023 proof remain local
diagnostic evidence and are not recomputed or extended.

May 2023 establishes an exact comparison anchor: D4-native buy, sell, and ratio
match all 2,976 accepted raw-trade bars with zero mismatches.

At `2024-05-06T07:00:00Z`, both the official monthly raw archive and the complete
31-day daily union disagree with D4:

| Quantity | Canonical D4 | Monthly and daily-union raw trades | Raw minus D4 |
|---|---:|---:|---:|
| volume | 1725.914 | 1726.888 | +0.974 |
| trade count | 29627 | 29673 | +46 |
| taker buy | 822.33 | 823.011 | +0.681 |
| taker sell | 903.584 | 903.877 | +0.293 |

No tolerance, splice, repair, or averaging is authorized. The authoritative row
is the canonical D4 row.

## No dual authority and retirement

The runner passes parent and feature artifacts to the generic resolver and
records its composite identity and provenance notes. It cannot infer taker-flow
values or accept plain five-column OHLCV as satisfying declared taker-flow
fields. The compatibility hook remains transitional and may be removed at
`N1-03 / RETIRE-03` once a production research consumer owns the same resolver
boundary.

## Non-authority

This capability creates noncanonical offline research/workbench data only. It
grants no strategy, candidate, Result Population, edge, promotion, runtime,
paper/live, OMS, reconciliation, risk, capital, or canonical-result authority.
