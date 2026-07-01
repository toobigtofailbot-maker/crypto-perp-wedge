# LAB-RT-HYP-004R Momentum Distinctness Check

## Result

`pass_with_caution`, pending Main verification.

## Repo-Truth Basis

Inspected the revised proposal, freshness matrix, concluded-family inventory, `RP-2592`, `RP-3731`, `RP-6236`, `STRAT-SPEC-0004`, `STRAT-SPEC-0005`, `STRAT-SPEC-0006`, their VMs and sweep plans, the indicator catalog, and compiler references.

## Mechanical Check

The concluded RP-2592 / RP-3731 / RP-6236 family is SMA crossover momentum. Entries are fast SMA crossing slow SMA with side-specific trend SMA confirmation. RP-3731 and RP-6236 add a fixed ATR stop, but the entry event remains crossover-based.

HYP-004R proposes EMA-side impulse continuation with candle body size normalized by ATR, RVOL participation, UTC session windows, and weekend exclusion. The session filter is load-bearing because `session_hours_utc` is a declared denominator axis, not a note.

## Overlap

The overlap is broad continuation/momentum membership, moving-average context, and ATR risk vocabulary. Those overlaps are real, so this is not a zero-risk pass.

## Decision

As written, HYP-004R is mechanically distinct from the SMA crossover families because it has no fast/slow crossover trigger. If a later Strategy Spec or adapter reduces the surface to fast/slow moving-average crossover plus a session wrapper, it should be treated as duplicate and dropped.
