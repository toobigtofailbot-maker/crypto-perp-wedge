# Binance USDT-M 15m Catalog And Slice Identity

## Scope

WP-D4 adds an offline catalog and slice-identity layer for D2-normalized and
D3-validated Binance USDT-M BTCUSDT 15m OHLCV CSV data.

Package posture:

- Offline catalog/provenance only.
- Local files only.
- No live API.
- No exchange keys.
- No runtime, paper, live, OMS, reconciliation, risk, safe-mode, or execution contact.
- No canonical sweep.
- No result-population write.
- No Strategy Spec, variant manifest, or sweep-plan mutation.
- D5 remains Karl-gated.

## Repo-Truth Baseline

Fact:

- D2 added `tools/data/import_binance_usdtm_15m.py` for deterministic offline
  CSV/ZIP normalization.
- D3 added `tools/data/validate_binance_usdtm_15m.py` and the D3 validation
  and gap policy.
- `docs/data_catalog.md` is the older reproducibility catalog for existing
  local data files. It is not a deterministic D4 slice registry.

Inference:

- D4 should establish the deterministic slice identity contract and local tool
  surface without committing production-scale data.

Decision:

- D4 catalog entries are generated from local normalized CSV bytes, a PASS D3
  validation report, and raw-source hash provenance from either the D2 import
  report or an explicit caller-supplied raw SHA256.

Open question:

- The future committed location for production catalog entries is deferred to a
  later approved package. D4 defines the entry shape and tool behavior only.

Future option:

- Later packages may add committed catalog-entry directories or multi-symbol
  extensions if explicitly authorized.

## Catalog Ref Naming

The D4 dataset id is:

```text
binance_usdtm_btcusdt_ohlcv_15m
```

The generated catalog ref shape is:

```text
binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.<start_utc_compact>.<end_utc_compact>.sha256_<slice_hash_prefix>
```

The ref intentionally includes `offline_local` and `15m` so a future D5 runner
cannot silently confuse this slice with a live source, another timeframe, or a
different market-data stream.

## Required Entry Facts

Every usable D4 catalog entry must record:

- dataset id / catalog ref;
- symbol `BTCUSDT`;
- venue `Binance`;
- market type `USDT-M perpetual`;
- stream `ohlcv`;
- timeframe `15m`;
- source type `offline_bulk_or_local_file`;
- raw source SHA256;
- normalized file SHA256;
- validation report SHA256;
- timestamp range;
- row count;
- expected row count;
- gap facts;
- duplicate facts;
- D3 validation status;
- D2 normalization version;
- D3 validator version;
- gap-policy reference;
- slice identity hash;
- identity input ordering.

## Slice Identity

Slice identity is:

```text
binance_usdtm_btcusdt_ohlcv_15m:sha256:<sha256>
```

The SHA256 is computed over canonical JSON using sorted keys, minified
separators, and ASCII output. The identity input object contains:

- slice identity version;
- dataset id;
- symbol;
- venue;
- market type;
- stream;
- timeframe;
- source type;
- raw source SHA256;
- normalized SHA256;
- validation report SHA256;
- validation status;
- normalization version;
- validator version;
- gap-policy reference;
- timestamp range;
- row count;
- expected row count;
- gap summary;
- duplicate summary.

Identity invalidation rule:

- Any source file content change changes identity through `raw_source_sha256`.
- Any normalized file content change changes identity through
  `normalized_sha256`.
- Any timestamp range or row-count change changes identity through `range`.
- Any symbol, venue, market type, stream, or timeframe change changes identity.
- Any normalization behavior change changes identity through
  `normalization_version`.
- Any gap-policy change changes identity through `gap_policy_ref` or gap facts.
- Any validation report or validation result change changes identity through
  `validation_report_sha256` and `validation_status`.
- Any duplicate or gap fact change changes identity through the duplicate and
  gap summary fields.

Determinism rule:

- Same valid inputs produce the same slice identity.
- Any material identity input change produces a different slice identity.

## Invalid Data Posture

Invalid data cannot become a usable D4 catalog slice.

The catalog tool fails without writing a catalog output when:

- the D3 validation report is not `ok=true`;
- validation status is not `PASS`;
- the normalized file hash does not match the validation report source hash;
- row count differs from expected row count;
- missing bars or duplicate rows are present;
- required raw source hash provenance is absent.

Report-only invalid D3 validation remains report-only. It does not produce a
usable catalog ref.

Forbidden:

- cataloging invalid data as usable;
- best-effort usable slice;
- fill;
- interpolation;
- silent deduplication;
- synthetic candles;
- synthetic-as-real data.

Review question:

```text
Can invalid data become a cataloged slice that D5 could consume as valid?
```

For D4, the required answer is no.

## D5 Handoff Contract

A future Karl-gated D5 package must consume:

- frozen strategy parents;
- a specific validated D4 catalog ref;
- a specific D4 data slice identity;
- validation report identity;
- row count;
- timestamp range;
- gap facts;
- duplicate facts;
- D3 validation `PASS` status;
- D4 catalog/slice identity `PASS` status.

D4 does not create a result population, does not run a sweep, does not rank or
recommend a strategy, and does not authorize D5. Karl approval remains required
before any real-data canonical sweep.

## Tool Usage

Example local command:

```powershell
python -m tools.data.catalog_binance_usdtm_15m `
  --normalized path\to\validated_15m.csv `
  --import-report path\to\import_report.json `
  --validation-report path\to\validation_report.json `
  --output path\to\catalog_entry.json
```

If no D2 import report is available, the caller must supply:

```powershell
--raw-source-sha256 <sha256>
```

The command is offline/local-file only and writes sorted deterministic JSON only
after all catalog preconditions pass.
