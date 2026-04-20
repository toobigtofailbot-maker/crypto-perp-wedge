# Score Bucket Mapper

## Why The Mapper Is Next

WP-7a proved the first deterministic advisory Regime/Scoring agent output.
WP-6j adds the first consumer of that output: a bounded score bucket mapper that
translates committed Z2 evidence into the locked Z3 advisory bucket domain.

This proves the translation contract while keeping all execution boundaries
closed.

## Frozen Mapping Rule

WP-6j uses `score_thresholds_with_confidence_floor_v1`:

- If `confidence < 0.60`, map to `BLOCK` with `size_multiplier = 0.0`.
- Else if `setup_score >= 80.0`, map to `ALLOW` with
  `size_multiplier = 1.0`.
- Else if `setup_score >= 60.0`, map to `ALLOW_REDUCED` with
  `size_multiplier = 0.5`.
- Else map to `BLOCK` with `size_multiplier = 0.0`.

For `AOUT-0001`, the committed values are `setup_score = 72.95` and
`confidence = 0.891`, so `BMAP-0001` maps to `ALLOW_REDUCED` with
`size_multiplier = 0.5`.

## Why Option A Was Chosen

Option A keeps the first mapper deterministic and easy to audit: setup score is
the primary bucket signal, while confidence is a secondary hard floor. A low
confidence output cannot create an advisory allow bucket, even when the score is
high.

## Why This Remains Advisory-Only

The mapper reads committed agent-output artifacts and writes committed
bucket-mapping artifacts. It does not import overlay, OMS, risk, execution, or
paper-runtime paths. Its output is exposed only through validation and the
read-only query layer.

## Why Overlay Contact Is Deferred

Overlay-adjacent wiring would be a higher-risk package because it could affect
trading behavior. WP-6j intentionally stops at the evidence boundary so the
mapping contract can be reviewed independently before any shadow or
overlay-adjacent work is considered.

## Future Preparation

The mapper gives a later package a stable reviewed artifact family:
schema-validated source references, copied score/confidence values, deterministic
method metadata, bounded buckets, and explicit advisory-only notes.
