# Canonical Funding-Series Provenance Contract

## Purpose and authority

This contract defines a closed, machine-validated provenance binding for an
offline exchange funding-event series. It records data identity and alignment
semantics only. It creates no runner readiness, dispatch, execution, Result
Population, candidate, promotion, paper/live, runtime, OMS, risk, or
reconciliation authority.

The first bound series is the existing local BTCUSDT Binance USDT-M perpetual
funding Parquet. The source data remains gitignored and read-only. The
provenance artifact does not copy, rewrite, normalize, repair, download, or
regenerate the source.

## Verified source facts

- Logical path:
  `data/processed/binance_um_perp_BTCUSDT_funding_8h_2019-09-10_2026-04-12_2026-04-12T1655Z.parquet`
- Whole-file SHA-256:
  `5f0da7478ccf3514af41dff9958b579cd2f797a2716001b0fa10a11059912798`
- Byte length: `126987`.
- Rows: `7220`.
- Ordered Arrow columns:
  `symbol: large_string`, `fundingTime: int64`, `fundingRate: double`,
  `markPrice: double`.
- `symbol`, `fundingTime`, and `fundingRate` contain no nulls. `markPrice` is
  nullable and has `4536` nulls.
- `fundingTime` is the actual exchange funding-event time stored as UTC epoch
  milliseconds. No timestamp is rounded for application.
- `fundingRate` is a decimal fraction of notional per funding event. For
  example, `0.0001` is `0.01%`; positive rates mean longs pay and shorts
  receive under the existing backtest sign convention.
- Coverage is `2019-09-10T08:00:00Z` through
  `2026-04-12T16:00:00Z`, inclusive of the recorded endpoint events.
- Timestamps are strictly increasing and contain zero duplicates.
- All `7220` nominal UTC 8-hour slots in the inclusive coverage are present.
  Actual exchange timestamps are 0 through 47 milliseconds after their
  nominal slots. The completeness check permits at most one minute of
  timestamp jitter solely to classify slots; it preserves every actual
  timestamp. The gap count and gap inventory are both zero.
- The source adapter is `scripts/fetch_btcusdt_funding_bulk.py`, which records
  the public Binance `/fapi/v1/fundingRate` response. The filename and catalog
  evidence record collection at `2026-04-12T16:55:00Z` with minute precision.
- The producer coerces numeric fields, calls
  `drop_duplicates(subset=["fundingTime"])` with keep-first behavior, sorts by
  `fundingTime`, resets the index, and serializes Parquet with `index=false`.
  No retained raw API snapshot or producer counter proves the pre-dedup row
  count or how many rows, if any, that step removed. The artifact records that
  unresolved history explicitly; it does not infer zero. The exact bound
  Parquet itself has zero duplicate timestamps, and no post-materialization
  repair is permitted or performed by this contract or validator.

## Required artifact shape

Every production artifact must validate against Draft 7 schema
`research/schemas/funding_series_provenance.schema.json`. The schema is closed:
unknown properties fail validation. The artifact binds all of the following:

- schema version, funding-series ID, artifact ID, and artifact path;
- venue, market type, contract type, and instrument;
- public source adapter and endpoint, with network/private/credential access
  forbidden for validation;
- event timestamp field, storage, semantics, and UTC timezone;
- funding-rate field, storage, units, and sign semantics;
- snapshot timestamp and precision;
- exact coverage, expected cadence, gap-classification tolerance, and maximum
  observed slot offset;
- source path, format, ordered column schema, row count, byte length, and raw
  SHA-256;
- evidenced producer operations, the unresolved pre-dedup count, and the
  no-post-materialization-repair posture;
- exact duplicate and gap findings;
- all repair, fill, substitution, and fail-closed policies;
- the existing backtest boundary rule;
- intended future funding mode `on`;
- downstream identity requirements and a strict non-authority declaration.

The artifact path is derived from the funding-series ID:
`research/data_provenance/funding/<funding_series_id>.funding_provenance.json`.
The series ID must bind the first 16 hexadecimal characters of the full raw
SHA-256. The full SHA remains mandatory in `file_identity.raw_sha256`.

## Event boundary and position rule

The locked rule is
`existing_backtest_left_open_right_closed_pre_fill_v1`:

1. For consecutive research bars, an actual funding event applies when its
   exchange timestamp is in `(previous_bar_timestamp, current_bar_timestamp]`.
2. The position must be nonzero before the current bar's funding phase.
3. A funding event exactly at the current bar timestamp is included for a
   pre-existing position.
4. An entry filled at that same current-bar timestamp is excluded because the
   existing backtester processes funding before the current bar's fill.
5. No bar-level interpolation, forward fill, backfill, timestamp rounding,
   synthetic event, or synthetic zero is permitted.

This contract documents the current `lib/backtest.py` behavior. It does not
change funding sign, notional, timing, cost mathematics, fills, or position
accounting.

## Gap and missing-event policy

Completeness classification maps each actual event timestamp to the nearest
nominal UTC 8-hour slot with a maximum one-minute tolerance. This mapping is a
validation-only gap check; it never replaces the actual event timestamp.

The validator requires strictly sequential unique nominal slots. A missing
slot, duplicate timestamp, same-slot collision, timestamp outside the declared
coverage, or event outside the tolerance fails closed. Gap inventory must
exactly match the validator's deterministic nominal-slot inventory. Missing
required events are not interpolated, carried, backfilled, or valued at zero.

## Validator contract

`tools/registry/validate_funding_series_provenance.py` is offline and
read-only. It must:

- confine the artifact and source to configured roots and reject any symlink
  component;
- require file existence and Parquet format;
- verify exact byte length and whole-file SHA-256;
- verify ordered Arrow columns, Arrow types, physical nullability, observed
  null counts, and required non-null columns;
- verify row count, instrument identity, UTC epoch-millisecond timestamps,
  strict ordering, duplicate count, exact coverage, cadence slots, gap
  inventory, and maximum observed offset;
- reject malformed or non-finite funding rates;
- verify the funding-series ID, artifact ID, and artifact path bindings;
- reject any schema posture that permits network/private access, repair,
  interpolation, forward fill, backfill, zero substitution, or authority;
- compare source size and modification time before and after validation and
  fail if the source changes during the read;
- emit deterministic sorted errors and never mutate the artifact or data.

An isolated worktree may validate the logical `data/processed/...` binding
against a separately configured clean checkout root containing the exact local
gitignored bytes. The logical path and all identity checks remain unchanged.

## Downstream identity requirement

A later separately authorized runner integration must include these fields in
scientific input identity:

- funding mode;
- funding-series ID;
- provenance artifact ID, path, and whole-file SHA-256;
- funding Parquet path and whole-file SHA-256;
- coverage start and end;
- timestamp semantics;
- rate units;
- boundary-rule ID.

Equivalent bindings are required where applicable in the later scratch
manifest, Result Population input identity, and Option-C dispatch record. This
contract does not modify any of those consumers and does not declare them
ready.

## Rejection posture

Validation fails closed on hash, length, row, schema, identity, timezone,
units, coverage, cadence, gap, duplicate, null-required-field, non-finite rate,
path, symlink, mutation, repair-policy, zero-substitution, private/network
source, or authority mismatch. Unknown or load-bearing unresolved facts are not
inferred.
