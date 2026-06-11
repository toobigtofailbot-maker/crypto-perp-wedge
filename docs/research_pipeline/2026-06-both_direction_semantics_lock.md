# Both-Direction Strategy Spec Semantics Lock

## Scope And Authority

This document is the committed Main 5 lock for closed `direction: "both"` Strategy Spec semantics.

It records the semantics that later schema, validator, and compiler packages must cite. It implements nothing. It creates no schema, validator, compiler, test, Strategy Spec, variant, sweep, result population, catalog, dashboard, data acquisition, simulator, runtime, paper/live, OMS/risk, broker/exchange, or protected-path authority.

This lock is repo-truth for semantics only. It is not implementation authority and does not authorize downstream packages before their gates are satisfied.

## Basis

`WP-COMP-BOTHDIR-01a` is merged on `main` via PR #433 and created `docs/research_pipeline/2026-06-both_direction_semantics_design.md`.

Main 5 accepted the `WP-COMP-BOTHDIR-01a` recommendation as-written. Current merged repo truth remains authoritative over older summaries, handoffs, and chat text.

Current repo facts supporting this lock:

- `entry_logic.direction` currently admits `long`, `short`, and `both`.
- The current Strategy Spec schema has no side-labeled entry representation.
- The current compiler still rejects `direction: "both"` with `UnsupportedSpecSignalCompilerFeature`.
- Current compiler output is one position-intent signal stream: long, short, or flat.

## Locked Semantics

Main 5 locks these semantics exactly:

- explicit side-labeled long/short entry groups; no compiler mirroring
- no-entry / flat when long and short entries both fire on the same bar while flat
- side-specific exits (long exits apply to long state, short exits to short state)
- single-stream mutual exclusivity (per-bar signal is long XOR short XOR flat)
- opposite-side entry while already in a position does NOT silently flip (flip deferred to a later explicit lock)
- closed grammar preserved: no new operators, no expression language, depth <= 3

## Representation Lock

Later schema and validator work must express long and short entry groups explicitly.

The compiler must not infer the short side by mirroring long-side conditions. Mirroring is rejected because it hides semantics outside the Strategy Spec artifact and makes review depend on compiler transformations rather than visible repo content.

Side labels must be closed, not free-form. The semantic domain is long and short. Exact key names are left to the later schema package, but the semantics are locked: a `direction: "both"` Strategy Spec must make both side entry branches explicit.

The later schema package may choose the exact JSON shape, but it must preserve:

- explicit long entry group representation;
- explicit short entry group representation;
- closed side labels;
- condition group depth no greater than 3;
- no expression language;
- no new operator requirement from this lock.

## Conflict Rule Lock

While flat, if long and short entries both fire on the same bar, output/intent is flat / no entry.

There is no priority ordering. There is no long-first, short-first, last-side, volatility, recency, random, or expression-based tie-break policy.

This rule is deterministic, no-lookahead-safe, and auditable from the same bar's closed entry predicates.

## Exit Lock

Long exits close long state only.

Short exits close short state only.

Side-specific exits must be represented explicitly in later grammar. Shared exits are not authorized by this lock unless a later Main decision explicitly locks shared-exit semantics.

`max_holding_period`, if retained for both-direction specs, must apply to the currently held side's duration only and must not imply hedge mode or runtime position inventory changes.

## No-Flip Lock

Opposite-side entry while already in a position does not silently reverse the state.

Same-bar exit plus opposite-side entry must not create an implicit reversal. If a side-specific exit fires, the locked posture is to resolve that bar to flat rather than entering the opposite side on the same bar.

Position-flip semantics are deferred to a later explicit Main lock. Later packages must not implement flip behavior as an incidental result of both-direction support.

## Determinism, No-Lookahead, And Closed Grammar Lock

Later implementation must preserve:

- no future-bar reads;
- same input produces same output;
- no expression language;
- no new operators from this lock;
- no new data stream;
- no nesting expansion;
- depth <= 3;
- no hedge-mode or two-output position model;
- no runtime, paper/live, OMS, risk, broker, exchange, or protected-path implication.

The locked output intent remains a single mutually exclusive stream: long XOR short XOR flat.

## Downstream Package Gates

The downstream sequence is:

```text
WP-COMP-BOTHDIR-01c: schema + validator + tests only, after 01b merge
WP-COMP-BOTHDIR-01d: compiler + tests only, after 01c merge
mandatory report-back to Main after 01d validates
```

Neither downstream package is authorized until its gate is satisfied. `WP-COMP-BOTHDIR-01c` must not include compiler implementation unless later explicitly rescoped. `WP-COMP-BOTHDIR-01d` must not change schema or validator semantics unless later explicitly rescoped.

If a downstream package cannot implement this lock without non-closed grammar, expression language, new operators, depth greater than 3, hedge-mode output, runtime/paper/live implications, or protected-path contact, it must stop for Main/Karl rather than implement around the ambiguity.
