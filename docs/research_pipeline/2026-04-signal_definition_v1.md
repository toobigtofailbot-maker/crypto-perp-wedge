# Signal Definition v1 (WP-7t)

## Purpose

WP-7t adds the first committed shadow-signal summary family over the existing
overlay shadow-log corpus. The family is descriptive only. It does not alter
shadow evidence, does not authorize runtime influence, and does not define an
override path, policy action, or execution consequence.

The family exists to lock what current shadow evidence means at the segment
level before downstream packages consume that meaning implicitly.

## Locked Option A Rule

The v1 derivation method is `shadow_signal_summary_option_a_floor_10_v1`.

Each segment records:

- `match_count`
- `mismatch_count`
- `abstention_count`
- `observation_count`
- `rate_denominator`

The rate denominator is `match_count + mismatch_count`. Abstentions remain
explicit but are not counted in the agreement/disagreement rate denominator.

The static sufficiency floor is `10` observations per segment.

- If `observation_count < 10`, the segment is marked
  `insufficient_evidence=true` and `signal_outcome=INSUFFICIENT_EVIDENCE`.
- If `observation_count >= 10`, the segment uses majority semantics:
  `AGREEMENT_SIGNAL`, `DISAGREEMENT_SIGNAL`, or `MIXED_SIGNAL` on tie.

This layer defines signal semantics only. It does not define what action should
follow from a sufficient agreement or disagreement state.

## Segment Key

The summary layer keys each segment explicitly by:

- `advisory_source`
- `source_bucket_mapping_id`
- `source_pre_gate_advisory_snapshot_id`
- `fixture_identity`

`source_pre_gate_advisory_snapshot_id` is `null` for `BMAP` segments and
required for `PGAS` segments.

`fixture_identity` is normalized from the committed overlay-input pair:

- `canonical` =
  `tests/fixtures/context_snapshot_sample.json` +
  `configs/fmp_macro_flags.json`
- `_02` =
  `tests/fixtures/context_snapshot_sample_02.json` +
  `configs/fmp_macro_flags_02.json`

WP-7t intentionally does not invent a third fixture-identity bucket. Unknown
path pairs are treated as derivation failure for v1.

## What `INSUFFICIENT_EVIDENCE` Means

`INSUFFICIENT_EVIDENCE` means the segment does not yet meet the locked floor for
reporting a normal usable agreement-rate signal. The segment still exposes raw
counts and timestamps, but it is not presented as a sufficient agreement or
disagreement state.

Under the current corpus, `SSS-0001` is expected to contain only
`INSUFFICIENT_EVIDENCE` segments. That is an honest result, not a failure of
the package.

## How `SSS-0001` Is Derived

`SSS-0001` covers the committed corpus `OSH-0001` through `OSH-0010`.

The derivation reads the committed `overlay_shadow_logs` relation, normalizes
fixture identity using the locked canonical / `_02` mapping, and aggregates one
segment row per realized combination of:

- advisory lineage (`advisory_source`, `source_bucket_mapping_id`,
  `source_pre_gate_advisory_snapshot_id`)
- fixture identity (`canonical`, `_02`)

The current corpus yields 8 realized segments:

- `BMAP / BMAP-0001 / null / canonical`
- `BMAP / BMAP-0001 / null / _02`
- `BMAP / BMAP-0002 / null / canonical`
- `BMAP / BMAP-0002 / null / _02`
- `PGAS / BMAP-0001 / PGAS-0002 / canonical`
- `PGAS / BMAP-0001 / PGAS-0002 / _02`
- `PGAS / BMAP-0002 / PGAS-0003 / canonical`
- `PGAS / BMAP-0002 / PGAS-0003 / _02`

All 8 are below the floor of 10 observations and are therefore encoded as
`INSUFFICIENT_EVIDENCE`.

## What This Layer Does Not Mean

This layer does not grant:

- runtime permission
- overlay authority
- override semantics
- policy authority
- OMS authority
- risk authority
- execution authority

The family is a bounded bridge from raw diagnostic evidence to deterministic
summary semantics only.

## Expected Future Consumption

Future slice packages may consume this layer as a committed summary surface
instead of re-deriving meanings ad hoc from raw shadow rows. Those consumers
must still decide their own scope explicitly. WP-7t does not prescribe any
runtime, policy, or promotion use.
