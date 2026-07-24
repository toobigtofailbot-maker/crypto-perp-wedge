# Karl content review — canonical dispatch authorization

Package: `WP-CANON-DISPATCH-AUTHORIZATION-CONTRACT-01`

Review purpose: confirm the exact KDAUTH content and lifecycle contract before
merge. This is content review only. It is not approval to write a production
authorization or create a dispatch.

## Exact artifact and audit paths

- Authorization:
  `research/queue/dispatch_authorizations/<authorization_id>.dispatch_authorization.json`
- H-004 family:
  `research/queue/dispatch_authorizations/KDAUTH-H004-R2-NNNN.dispatch_authorization.json`
- Lifecycle audit:
  `research/queue/dispatch_authorization_audit/dispatch_authorization_events.jsonl`

No file is created under either authoritative path by this package.

## Exact field tree

```text
canon_dispatch_authorization_v1
├── authorization_id
├── authorization_artifact_target_path
├── approved_by = Karl
├── approved_at
├── authorization_scope = one_single_use_dispatch
├── approval_statement
├── authorization_core
│   ├── queue_binding
│   │   ├── queue item ID/path/whole-file hash/byte length/state
│   │   └── Gate-Q ID/path/whole-file hash/byte length/core hash/scope/canonicalization
│   ├── crossing_identities
│   │   └── dispatch ID/path and run ID/execution-event-stream path
│   ├── dispatcher_packet
│   │   └── ID/purpose/version/path/whole-file hash/byte length/exact-byte posture
│   ├── lineage
│   │   ├── Strategy Spec raw and full canonical hashes
│   │   ├── external-content-readiness raw/canonical bindings
│   │   ├── variant-planning approval whole/core hashes
│   │   ├── Variant Manifest whole-file hash
│   │   ├── Sweep Plan whole-file hash
│   │   └── Gate-Q whole/core hashes
│   ├── dataset
│   │   └── canonical-route/status, 1d catalog/data hashes and lengths,
│       rows/UTC coverage, cadence/timezone/column identity, completed-bar
│       findings, direct-public-snapshot/underivation posture, validator
│       path/hash/length, and rebuilt-catalog validation identity
│   ├── funding
│   │   └── mode on, series/provenance/data identity, rows/coverage, timestamp/rate/
│       boundary semantics, no fill/interpolation/backfill/rounding/zero substitution
│   ├── runner
│   │   └── python module, source path/hash/length, version
│   ├── denominator
│   ├── budget
│   ├── execution_parameters
│   ├── output_targets
│   └── authority_flags
├── authorization_core_sha256
├── authorization_core_hash_scope = dispatch_authorization_core_v1
├── authorization_core_canonicalization = repo_canonical_json_v1
├── exact_content_and_target_only = true
├── append_only = true
├── single_use_authorization_id = true
├── content_bound_freshness = true
├── amendment_revocation_policy
└── authority_flags
```

The exact closed definitions are in
`research/schemas/canon_dispatch_authorization.schema.json`. The exact
synthetic artifact builder and validation fixture are `_fixture` in
`tests/test_dispatch_authorization.py`; it builds every referenced byte source,
places KDAUTH at the authoritative path inside a temporary repository, commits
retained history, and validates without touching the real authoritative path.

## Merged canonical 1d route binding

This review packet is refreshed from merged PRs #670 and #671 at base
`ed0227d57d882ec3442d39bde894ccfe01efa03e`. Neither PR overlaps the exact
19-path KDAUTH package:

- catalog:
  `research/data_slices/binance_usdtm_btcusdt_1d/binance_usdtm_btcusdt_1d_20200101_20260411.catalog_slice.json`,
  4,237 bytes,
  `sha256:51fc09918841cd3ac353efe375af91a4732080571f9b1af634f5d1a426217adb`;
- canonical local Parquet:
  `data/processed/binance_um_perp_BTCUSDT_1d_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`,
  200,961 bytes,
  `sha256:c6e2e7ce030db6a710d95e48325fc77b27efbbdd441199b3d7458d4394795802`;
- lineage validator:
  `tools/data/register_binance_usdtm_1d_lineage.py`, 15,005 bytes,
  `sha256:304677c9800763189424f2efa7900eeb2c2be2fce4b4bb99663bc8e409fbc8c1`;
- route validation identity:
  `sha256:268cb6ade6e2a3e71f5bbbe0c4dad5b720732310f8e966f901616845f13bd3b9`;
- runner:
  `tools.research_runner.run_offline_sweep` at
  `tools/research_runner/run_offline_sweep.py`, version
  `wp-s2c-190-build-test-v1`, 149,993 bytes,
  `sha256:b23c18a66c399b8f4575c6f51d421153d30f9afbffdc0e24c10a336cd6460e1d`.

These facts bind a later exact authorization; they do not invoke the route.
No production dispatcher-packet identity exists here. A real KDAUTH remains
impossible until a separately authorized refreshed Stage A freezes the exact
packet.

## Exact approval statement

> Karl approves one single-use offline research dispatch for the exact queue
> item, dispatch ID, run ID, frozen dispatcher packet, lineage, dataset,
> funding identity, runner, budget, and output targets bound by this artifact,
> and grants no downstream authority.

Any byte or wording difference fails validation.

## Serialization and hashes

The authorization file is UTF-8 without BOM, lexicographically sorted by key,
two-space indented, and ends with exactly one LF. CRLF, missing/double LF,
trailing bytes, trailing-space drift, or different key ordering fails closed.

The complete `authorization_core` is serialized with
`repo_canonical_json_v1` and hashed as
`authorization_core_sha256`. The whole authorization file does not contain its
own hash. Consumers compute the whole-file SHA-256 over exact bytes including
the final LF and also bind its byte length.

## Freshness

Freshness is exact-content equality only. `approved_at` is mandatory and
timezone-aware, but there is no expiry, same-day rule, Git-time comparison, or
wall-clock window. Any identity, field, hash, length, or referenced-byte drift
requires a new authorization.

## Lifecycle and permanent single use

The audit vocabulary is:

1. `authorization_created`, exactly once and first.
2. `authorization_superseded`, only before consumption and terminal.
3. `authorization_revoked`, only before consumption and terminal.
4. `authorization_consumed`, exactly once and terminal.

Events are append-only `repo_canonical_json_v1` lines plus LF. A malformed or
partial tail fails closed. Superseded, revoked, or consumed authorization
identity is permanently unavailable. Deletion does not release authorization,
dispatch, run, queue/authorization, dispatch-path, or stream-path identity.

## Authority flags

The only true authority flag is
`authorizes_one_single_use_dispatch=true`.

The artifact itself does not invoke or authorize runner execution. It grants no
Result Population, ranking/recommendation, candidate lifecycle,
readiness/promotion, standing dispatcher/scheduler, retry/recovery,
paper/live/runtime, OMS/risk/reconciliation, broker/exchange,
order/position/balance/capital, or notification authority.

## What Karl will later approve

After a separately authorized Stage A freezes one exact dispatcher packet, Karl
may review one exact KDAUTH artifact whose whole content binds that packet and
every prerequisite. A later protected KDAUTH writer—not this package—may then
exclusive-create the reviewed bytes and append `authorization_created`.

`THIS PACKAGE CREATES NO PRODUCTION DISPATCH AUTHORIZATION`
