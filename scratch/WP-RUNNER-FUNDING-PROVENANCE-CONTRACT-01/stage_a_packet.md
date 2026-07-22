# WP-RUNNER-FUNDING-PROVENANCE-CONTRACT-01 Stage-A Packet

## A. Base, branch, worktree, and overlap preflight

- Package: `WP-RUNNER-FUNDING-PROVENANCE-CONTRACT-01`.
- Base and HEAD: `1c22edf602f748ed03d9304c66b4b40cd6f0d601`.
- Branch: `codex/wp-runner-funding-provenance-contract-01`.
- Isolated worktree:
  `C:/GitHub/crypto-perp-wedge-wp-runner-funding-provenance-contract-01`.
- Drafting base `1c22edf602f748ed03d9304c66b4b40cd6f0d601` is an ancestor of
  refreshed `origin/main`; at Stage-A start they are identical.
- Open-PR preflight found only PR #665,
  `WP-CANON-DISPATCH-CONTROL-PLANE-DESIGN-LOCK-01`; its file list is
  distinct from this package's allowlist and contains no funding-provenance
  path.
- No open PR modifies `docs/project_status.md`; this package does not modify
  that file.
- All proposed production files are under this package's uncommitted
  `scratch/.../proposed/` mirror. No authoritative target exists or was
  written.

## B. Exact local data identity

- Existing clean-checkout physical path:
  `C:/GitHub/crypto-perp-wedge/data/processed/binance_um_perp_BTCUSDT_funding_8h_2019-09-10_2026-04-12_2026-04-12T1655Z.parquet`.
- Contract logical path:
  `data/processed/binance_um_perp_BTCUSDT_funding_8h_2019-09-10_2026-04-12_2026-04-12T1655Z.parquet`.
- Whole-file SHA-256:
  `5f0da7478ccf3514af41dff9958b579cd2f797a2716001b0fa10a11059912798`.
- Byte length: `126987`.
- Row count: `7220`.
- File format: Parquet; Arrow writer metadata reports
  `parquet-cpp-arrow version 23.0.1`.
- Ordered Arrow schema and observed null counts:
  - `symbol`: `large_string`, physically nullable, `0` nulls, required
    non-null;
  - `fundingTime`: `int64`, physically nullable, `0` nulls, required
    non-null;
  - `fundingRate`: `double`, physically nullable, `0` nulls, required
    non-null;
  - `markPrice`: `double`, physically nullable, `4536` nulls, not required
    non-null.
- Venue / market / instrument: Binance / USDT-M perpetual / BTCUSDT.
- Source adapter and endpoint:
  `scripts/fetch_btcusdt_funding_bulk.py` /
  public `/fapi/v1/fundingRate`.
- Network used by this package: no. Private exchange access: no. Credentials:
  no.

## C. Timestamp, rate, coverage, and materialization findings

Facts:

- `fundingTime` stores the actual exchange funding-event timestamp as UTC
  epoch milliseconds.
- Coverage is exactly `2019-09-10T08:00:00Z` through
  `2026-04-12T16:00:00Z`.
- `fundingRate` is a decimal fraction of notional per event. The repo's
  existing backtest fixture treats `0.0001` as `0.01%` of notional; positive
  rates mean longs pay and shorts receive.
- The data catalog and filename record collection at
  `2026-04-12T16:55:00Z` with minute precision. The local file timestamp is
  `2026-04-12T16:55:04Z`, consistent with that minute-level record.
- The producer coerces numeric fields, converts `fundingTime` to nullable
  `Int64`, calls `drop_duplicates(subset=["fundingTime"])` with keep-first
  behavior, sorts ascending, resets the index, and serializes Parquet with
  `index=false`.
- No retained raw API snapshot or producer counter evidences the pre-dedup row
  count or how many rows, if any, the producer's deduplication removed.

Decision proposed for Karl:

- The contract binds the exact materialized Parquet bytes used downstream.
  It explicitly records the known producer operations and the unresolved
  pre-dedup count; it does not infer zero removals. `repair=none` means no
  post-materialization repair by the provenance contract or validator. Karl's
  approval wording below explicitly acknowledges this treatment.

Current merged runner fact:

- `tools/research_runner/run_offline_sweep.py` supports canonical 15m and 4h
  inputs and constructs synthetic zero funding on those paths. It contains no
  canonical 1d funding-on integration. No merged H-004-R2 1d Result Population
  or blocked runner-result artifact exists on this base. This package neither
  adds that path nor invokes the runner.

## D. Duplicate and gap analysis

- Actual duplicate timestamp rows: `0`.
- Timestamps strictly increasing: yes.
- Nominal expected cadence: UTC `PT8H`.
- Expected inclusive nominal-slot count: `7220`.
- Observed sequential nominal-slot count: `7220`.
- Completeness classification: nearest nominal UTC 8-hour slot, with a
  validation-only tolerance of `PT1M`; actual timestamps are never rounded or
  substituted.
- Observed actual timestamp offset from nominal slot: minimum `0 ms`, maximum
  `47 ms`, all after the nominal boundary.
- Missing nominal slots / gap count: `0`.
- Gap inventory: `[]`.
- Every apparent interval slightly above or below eight hours is fully
  explained by the recorded 0-47 ms exchange timestamp jitter; there is no
  unexplained missing event in the bound file.

## E. Exact boundary rule

Rule ID: `existing_backtest_left_open_right_closed_pre_fill_v1`.

1. An actual funding event is eligible in
   `(previous_bar_timestamp,current_bar_timestamp]`.
2. The position must be nonzero before the current bar's funding phase.
3. A funding event exactly at `current_bar_timestamp` is included for a
   pre-existing position.
4. An entry filled at that same timestamp is excluded because the existing
   backtester processes funding before the current bar's fill.
5. Actual exchange timestamps only: no interpolation, forward fill, backfill,
   timestamp rounding, synthetic event, or synthetic zero.

This is grounded in current `lib/backtest.py` and its boundary tests. No
backtest behavior or cost mathematics changes in this package.

## F. Proposed identities, paths, and exact hashes

Funding-series ID:

`binance_usdtm_btcusdt_funding_events_20190910t080000z_20260412t160000z_sha256_5f0da7478ccf3514`

Provenance artifact ID:

`FUNDING-PROV-BINANCE-USDTM-BTCUSDT-20190910T080000Z-20260412T160000Z-5F0DA7478CCF3514`

Proposed production files and full-file SHA-256 values:

- `docs/data/canon_funding_series_provenance_contract.md`:
  `sha256:64537a3ad6a6626019af05da4af53d0857c980032d2ef42cdc37c92c447c0b1d`.
- `research/schemas/funding_series_provenance.schema.json`:
  `sha256:945b6e1988c7378b3b30f14b45282a35a1f1a851f05f1eeeab1f2ea07f4e5341`.
- `research/data_provenance/funding/binance_usdtm_btcusdt_funding_events_20190910t080000z_20260412t160000z_sha256_5f0da7478ccf3514.funding_provenance.json`:
  `sha256:fe84062a6426b7b5aa1653e87eb0038486925f5c5c6263cc33595870d4e6c692`.
- `tools/registry/validate_funding_series_provenance.py`:
  `sha256:349540f8cfc27a4f8c3507a438f949e0ca818c9b25ad4a3c0bfb5172469eb0d7`.
- `tests/test_funding_series_provenance.py`:
  `sha256:2655a46b4196f3c62021448bc9f2be36af5fd0b6df32e8c0eb8b46c4b7eba358`.

The Draft 7 schema is closed. The artifact fixes intended funding mode `on`,
actual exchange timestamps, UTC, decimal-fraction-per-event units, zero
duplicates, zero gaps, no post-materialization repair, no zero substitution,
no interpolation/forward-fill/backfill, fail-closed missing events, and all
downstream identity fields required by the package.

## G. Exact Stage-B changed-file allowlist

Only these tracked paths may be created in Stage B:

1. `docs/data/canon_funding_series_provenance_contract.md`
2. `docs/status_entries/WP-RUNNER-FUNDING-PROVENANCE-CONTRACT-01.md`
3. `research/schemas/funding_series_provenance.schema.json`
4. `research/data_provenance/funding/binance_usdtm_btcusdt_funding_events_20190910t080000z_20260412t160000z_sha256_5f0da7478ccf3514.funding_provenance.json`
5. `tools/registry/validate_funding_series_provenance.py`
6. `tests/test_funding_series_provenance.py`
7. `scratch/WP-RUNNER-FUNDING-PROVENANCE-CONTRACT-01/stage_a_packet.md`
8. `scratch/WP-RUNNER-FUNDING-PROVENANCE-CONTRACT-01/preservation_manifest.json`
9. `scratch/WP-RUNNER-FUNDING-PROVENANCE-CONTRACT-01/stage_a_validation.json`

No query-layer or registry-aggregator change is required: the dedicated
validator provides the package's minimum provenance-integrity surface, and the
repo has no mandatory central validator aggregator for this artifact family.
`docs/data_catalog.md` already identifies the exact Parquet, so it is not in
the allowlist. `docs/project_status.md` is expressly excluded.

Preservation hashes are recorded in
`scratch/WP-RUNNER-FUNDING-PROVENANCE-CONTRACT-01/preservation_manifest.json`.
They bind `lib/backtest.py`, the offline runner, H-004-R2 Strategy Spec / VM /
Sweep, the inert queue admission and Gate-Q approval, the 1d catalog slice,
the raw funding file, and the current integrity baseline.

## H. Stage-A validation completed

- Raw hash / bytes / rows / schema / coverage: pass.
- Duplicate and gap analysis: pass, `0` / `0`.
- Draft 7 schema meta-validation: pass.
- Proposed artifact exact local-data validation: pass.
- Validator Python compilation: pass.
- Proposed focused tests: `25 passed, 1 skipped`. The skip is the Windows
  environment's unavailable symlink creation; path-escape validation passed,
  and the symlink rejection test runs where fixture creation is permitted.
- Exact local 7,220-row production-artifact test: passed with
  `FUNDING_PROVENANCE_DATA_ROOT=C:/GitHub/crypto-perp-wedge`.
- Current integrity baseline: 58 `v_integrity_*` views executed; 57 empty and
  one accepted pre-existing row for `STRAT-SPEC-0007 hash_status=not_computed`.
- `git diff --check`: pass with no tracked diff. A subsequent Git
  `--no-index --check` attempt could not open the over-260-character
  package-local proposed artifact path on Windows; a direct whitespace/final-
  newline scan over every untracked text file passed. Stage B will run normal
  `git diff --check` and `git diff --cached --check` after the approved bytes
  are copied to their shorter authoritative paths.
- Authoritative paths absent: confirmed.
- No data mutation, network/private access, runner invocation, H-004 execution,
  commit, push, or PR.

## I. Stage-B validation plan after exact approval

Stage B will:

1. refresh and re-check base/open-PR overlap;
2. copy the five approved proposed production files byte-for-byte to their
   authoritative targets;
3. create only the allowlisted status entry and retain the three allowlisted
   Stage-A evidence files;
4. verify every approved production-file SHA before staging;
5. run schema meta-validation, focused validator tests, exact production
   artifact validation against the read-only local Parquet, all repository JSON
   parsing, relevant registry validators, all 58 integrity views, and full
   pytest;
6. re-check preservation hashes, exact allowlist, forbidden paths,
   `git diff --check`, and `git diff --cached --check`;
7. confirm no runner, canonical Result Population, H-004 dispatch, data fetch,
   or data mutation occurred;
8. only then commit, push, and open one non-draft PR; do not merge.

Any approved production byte, identity, path, policy, boundary rule, raw-data
identity, or allowlist change requires fresh Karl exact-content approval.

## J. Exact Karl approval wording

> I, Karl, approve Stage B only for
> `WP-RUNNER-FUNDING-PROVENANCE-CONTRACT-01` on base/head
> `1c22edf602f748ed03d9304c66b4b40cd6f0d601`. I approve Draft 7 schema target
> `research/schemas/funding_series_provenance.schema.json` at full-file SHA-256
> `sha256:945b6e1988c7378b3b30f14b45282a35a1f1a851f05f1eeeab1f2ea07f4e5341`;
> provenance artifact ID
> `FUNDING-PROV-BINANCE-USDTM-BTCUSDT-20190910T080000Z-20260412T160000Z-5F0DA7478CCF3514`,
> target
> `research/data_provenance/funding/binance_usdtm_btcusdt_funding_events_20190910t080000z_20260412t160000z_sha256_5f0da7478ccf3514.funding_provenance.json`,
> and full-file SHA-256
> `sha256:fe84062a6426b7b5aa1653e87eb0038486925f5c5c6263cc33595870d4e6c692`.
> I approve funding-series ID
> `binance_usdtm_btcusdt_funding_events_20190910t080000z_20260412t160000z_sha256_5f0da7478ccf3514`
> bound to logical Parquet path
> `data/processed/binance_um_perp_BTCUSDT_funding_8h_2019-09-10_2026-04-12_2026-04-12T1655Z.parquet`,
> full raw SHA-256
> `sha256:5f0da7478ccf3514af41dff9958b579cd2f797a2716001b0fa10a11059912798`,
> byte length `126987`, row count `7220`, and coverage
> `2019-09-10T08:00:00Z` through `2026-04-12T16:00:00Z`. I approve zero
> duplicate timestamps, zero gaps, empty gap inventory, actual exchange
> `fundingTime` UTC epoch-millisecond semantics, `fundingRate` decimal fraction
> of notional per event units, positive-rate longs-pay/shorts-receive semantics,
> expected UTC 8-hour cadence with one-minute validation-only slot tolerance,
> and observed maximum slot offset `47 ms`. I approve boundary rule
> `existing_backtest_left_open_right_closed_pre_fill_v1`: actual events in
> `(previous_bar_timestamp,current_bar_timestamp]` apply only to a position
> nonzero before the current bar's funding phase; a current-timestamp event is
> included for a pre-existing position and excluded for an entry filled at that
> same timestamp because funding is processed first. I approve intended funding
> mode `on`, no post-materialization repair, no zero substitution, no
> interpolation, no forward fill, no backfill, and fail-closed missing,
> malformed, non-finite, duplicate, identity-mismatched, or out-of-coverage
> data. I acknowledge the recorded producer keep-first deduplication operation
> and that its pre-dedup row/removal count is not evidenced; this approval binds
> the exact materialized Parquet bytes and does not infer a zero producer-removal
> count. I approve contract, validator, and test target hashes
> `sha256:64537a3ad6a6626019af05da4af53d0857c980032d2ef42cdc37c92c447c0b1d`,
> `sha256:349540f8cfc27a4f8c3507a438f949e0ca818c9b25ad4a3c0bfb5172469eb0d7`,
> and
> `sha256:2655a46b4196f3c62021448bc9f2be36af5fd0b6df32e8c0eb8b46c4b7eba358`,
> respectively. I approve exactly the nine-path Stage-B changed-file allowlist
> in this packet. This approval authorizes only authoritative contract,
> provenance, validator, tests, status/evidence, validation, commit, push, and
> one non-draft PR. It does not authorize runner integration, `canonical_1d`,
> H-004 execution or dispatch, Result Population work, data acquisition or
> mutation, backtest or funding-math changes, Option-C schema changes,
> scheduler/autonomy, runtime, paper/live, OMS, risk, or reconciliation work.

AWAITING KARL EXACT-CONTENT APPROVAL
