# Canonical Binance USD-M BTCUSDT 30m and 1h Derived Lineage

## Authority and parent

D2-021 selects deterministic D4-derived canonical bases for 30m and 1h. Both
derive exclusively from the canonical D4 15m parent:

```text
data-slice identity:
binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664

normalized SHA-256:
c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab

validation-report SHA-256:
785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c

rows: 220128
coverage: 2020-01-01T00:00:00Z through 2026-04-11T23:45:00Z
cadence: 900000 ms
```

No fill, interpolation, deduplication, synthetic bar, repair, splice,
averaging, tolerance, or source switch is used.

## Canonical 30m slice

```text
local generated CSV:
data/processed/d4_30m/binance_um_perp_BTCUSDT_30m_2020-01-01_2026-04-11_d4_resampled.csv

CSV SHA-256:
05c5857d668d2d12bcc743a13ad92a34590bc1c37ff8ea1f5f54d5d1fbf379ba

validation-report SHA-256:
b6516d82c4509ccaa4d0df51b5a28415fc1a92bac2fe5dd81dd7f700f112ecde

derivation-report SHA-256:
0ac703aa6ce2170cdbd89dd40a5f02b6a558450a72ed84c69e33cc96c77cc3a2

catalog-slice SHA-256:
a6661249ef07b98f7a6a85a74346605be134c692d7e44f918e061eb02c83a1a1

data-slice identity:
binance_usdtm_btcusdt_ohlcv_30m:sha256:090f4fac75bedf64fd19dbbeec141169bd7eaeaaaef187038878a6242022b94e

rows: 110064
coverage: 2020-01-01T00:00:00Z through 2026-04-11T23:30:00Z
cadence: 1800000 ms
children per bar: 2
gaps / duplicate rows / partial groups: 0 / 0 / 0
```

Independent full-corpus recomputation from the D4 15m parent produced zero
mismatches in timestamps, OHLC, volume, quote volume, trade count, taker-buy
base/quote volume, and close time.

## Canonical 1h slice

```text
local generated CSV:
data/processed/d4_1h/binance_um_perp_BTCUSDT_1h_2020-01-01_2026-04-11_d4_resampled.csv

CSV SHA-256:
28b750e90ee9957e6fc22811c4ae632355a239f2b958ed65c9b3c56cb2d9e79e

validation-report SHA-256:
d5adf9635e4f84a0143ff0b421439da623059b255caabf166906d66627041d60

derivation-report SHA-256:
0807cac9f0be6508b3cf077463f90e06d73066bd9d399a03b18c791d6396438b

catalog-slice SHA-256:
c4d0fd62ef27aa398996f6128de6b3a5d6ae2da1dbdfc8b5d08292a960db5484

data-slice identity:
binance_usdtm_btcusdt_ohlcv_1h:sha256:9e0faa68eb84b1aa176a5857432840b71a6049765963637236241b91ae807877

rows: 55032
coverage: 2020-01-01T00:00:00Z through 2026-04-11T23:00:00Z
cadence: 3600000 ms
children per bar: 4
gaps / duplicate rows / partial groups: 0 / 0 / 0
```

Independent full-corpus recomputation from the D4 15m parent produced zero
mismatches. Independently aggregating each pair of derived 30m rows into 1h
also produced zero mismatches.

## Diagnostic-source divergence

The pinned direct Parquets remain diagnostic evidence only:

```text
30m SHA-256:
059cb1ab3e5194578a39823e787ab29f41f6ce061309371cd414e0936aa9625b

1h SHA-256:
9f77e67628e2ece56d114af1af45d732c840df569a5f51fda3ac2a923349da54
```

Exact comparison used deterministic decimal values and no tolerance.

| Field | 30m mismatches | 1h mismatches |
|---|---:|---:|
| `open_time_ms` | 0 | 0 |
| `close_time_ms` | 0 | 0 |
| `num_trades` | 2 | 4 |
| `open` | 0 | 1 |
| `high` | 0 | 1 |
| `low` | 0 | 2 |
| `close` | 0 | 1 |
| `volume` | 2 | 4 |
| `quote_asset_volume` | 73524 | 41896 |
| `taker_buy_base_vol` | 2 | 4 |
| `taker_buy_quote_vol` | 50769 | 30869 |

Most differences are quote-field decimal-scale differences. Substantive
OHLC/base-volume/trade-count divergence is bounded to these windows:

- 30m: `2023-11-10T16:30:00Z`, `2025-01-29T02:30:00Z`;
- 1h: `2023-11-10T15:00:00Z`, `2023-11-10T16:00:00Z`,
  `2025-01-29T01:00:00Z`, `2025-01-29T02:00:00Z`.

The direct 30m pair does not reproduce the direct 1h row at the first three 1h
windows above; only `2025-01-29T02:00:00Z` is mutually consistent. Therefore
the direct 30m and 1h sources are not one internally consistent hierarchy.

The accepted classification is `DIAGNOSTIC_SOURCE_DIVERGENCE`. Diagnostic
disagreement does not create dual authority. Under D2-021, canonical authority
remains the exact D4-derived 30m/1h lineage.

## Boundaries

These are offline research inputs. This record creates no FT-02 feature-table,
Result Population, candidate, promotion, autonomy, runtime, paper/live, OMS,
reconciliation, risk, capital, or economic authority. The canonical 15m, 4h,
and direct 1d routes remain unchanged.
