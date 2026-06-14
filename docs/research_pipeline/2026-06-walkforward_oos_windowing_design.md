# Walk-Forward / OOS Windowing Design

## Status / Authority Boundary

`WP-ROBUST-C2-DESIGN` is a docs-only design package for future walk-forward and
out-of-sample windowing in the research lab.

It creates no implementation authority and changes no runner, backtester,
schema, validator, query-layer behavior, result-population artifact, Strategy
Spec, variant manifest, sweep plan, data lineage, candidate lifecycle,
ranking, promotion, readiness, paper/live/runtime behavior, OMS/risk/
reconciliation behavior, broker/exchange connectivity, collateral handling, or
autonomous behavior.

Any future implementation requires a separately authorized package. No
canonical result-population write may use this design unless Main/Karl later
authorizes the exact implementation and write path.

## Purpose

Walk-forward / OOS validation is the future chronology-aware outer-validation
layer for the research lab. Its purpose is to test whether a strategy family or
variant population remains coherent after selection decisions are made on
earlier data and evaluated on later, unseen data.

It addresses failure modes that a single full-period result or a winner-only
summary cannot expose:

- hidden lookahead or leakage from future bars into selection logic;
- overfitting to a single historical interval;
- unstable performance across market regimes;
- parameter choices that work only in the selection window;
- cost, drawdown, liquidation, or trade-count fragility concentrated in later
  holdout windows;
- survivor bias from dropping failed, errored, invalid, excluded,
  data-unavailable, aborted, or otherwise non-successful variants.

Walk-forward / OOS validation is separate from PSR, DSR, and MinTRL
diagnostics. Windowing defines chronological evidence structure and the
selection/evaluation boundary. PSR, DSR, and MinTRL are statistical diagnostic
families over declared inputs. A future result may need both layers, but
neither layer substitutes for the other.

## Terminology

In-sample means the historical interval used to design, fit, select, or choose
among variants inside a declared family. In-sample data may include indicator
warmup data when explicitly identified.

Out-of-sample means a later historical interval withheld from selection and
used for evaluation after the selection rule is fixed. OOS results are
evidence, not approval or promotion authority.

Train / selection window means the in-sample interval where parameters,
variant choices, or selection rules are applied. For pre-registered grids, the
selection rule may be "evaluate the complete population and carry all rows
forward" rather than choosing a single winner.

Evaluation / holdout window means the later interval used to measure the
selection result without reselecting from that window.

Rolling windows use a moving selection interval and a later moving evaluation
interval. The oldest data can fall out of the selection window as the fold
advances.

Expanding windows use a selection interval that grows forward over time while
each evaluation interval remains later than the selection end.

Anchored windows use a fixed start date for the selection interval. Expanding
anchored windows are common; rolling anchored windows are not the default
meaning unless a future manifest defines them explicitly.

Non-anchored windows do not keep a fixed start date. Their start and end dates
must be explicit because implicit shifting is a source of ambiguity.

Purge and embargo are future concepts for preventing leakage around boundary
events, overlapping labels, or lookback-dependent features. This package does
not choose purge or embargo rules. If later implemented, purge and embargo must
be explicit per window and validator-checked.

CPCV, bootstrap, Monte Carlo, and permutation tests are later or conditional
robustness tools. They are not required by this design and are not implemented
here.

## Future Design Constraints

Chronology must be preserved. A future runner or manifest must not permit a
selection window to use bars later than its paired evaluation window start.

No lookahead is allowed. Feature warmup, indicator windows, resampling,
funding alignment, mark/index/premium alignment, and any future multi-timeframe
alignment must be defined so later information cannot leak backward.

Selection and evaluation windows must be explicit. A future artifact should
record exact inclusive/exclusive boundary semantics, timezone, timeframe,
stream, data slice identity, and any warmup interval.

All trial populations must remain retained. A future windowed run must preserve
the complete declared population for each window, including successful,
failed, errored, invalid, excluded, filtered, data-unavailable, not-attempted,
and aborted rows.

Denominator honesty must be preserved. DSR and multiple-testing-aware
diagnostics must use the committed pre-registered population count or a later
explicit denominator rule that preserves all tested or declared exposure. The
denominator must not silently shrink to winners, successful rows, executed
rows, or rows with convenient data availability.

Selection rules must be declared before evaluation. A future windowed protocol
should say whether each window carries a full population forward, selects a
single variant, selects a region, or applies another fixed rule. The rule must
not be inferred from the holdout result.

Missing-data posture must be visible per window. Known irreparable gaps,
skipped bars, data-unavailable variants, and gap-handling decisions must remain
inspectable rather than being hidden by aggregate reporting.

## Future Artifact Implications

A future implementation likely needs a window manifest or equivalent artifact.
This design does not create that artifact or its schema.

A future window manifest should be able to link to:

- Strategy Spec identity;
- Variant Manifest identity;
- Sweep Plan identity;
- data catalog and data-slice identities;
- result-population identity or planned result-population output;
- optional run manifest or runner invocation identity;
- later EXP / REP, OL, REC, DEC, or human-review packet references where
  separately authorized.

Per-window lineage should identify the selection interval, evaluation interval,
warmup interval, purge/embargo posture if any, timeframe, stream, data source,
data-slice identity, and gap posture.

Aggregate reporting should not replace per-window reporting. A future output
may report aggregate statistics, but it must keep per-window rows visible
enough to diagnose instability, concentrated losses, missing data, and
selection-rule effects.

Result-population storage may later need a representation for folds or windows.
That representation is deferred. If it is implemented inside result
populations, the identity-hash scope, denominator snapshot, and old-artifact
compatibility posture must be explicitly designed first.

Windowing can create multiple evidence grains: per-variant per-window rows,
per-window selected rows, and aggregate family summaries. Future artifacts must
avoid treating aggregate summaries as a substitute for full-population
retention.

## Future Validation Expectations

Future validators should check chronological ordering:

- selection start before selection end;
- evaluation start after selection end, plus any required purge or embargo;
- no overlap unless a later design explicitly allows and explains it;
- warmup data not counted as evaluation data;
- all timestamps normalized to the declared timezone convention.

Future validators should check lineage and denominator integrity:

- referenced Strategy Spec, Variant Manifest, Sweep Plan, and data-slice
  identities are present where required;
- per-window declared population counts match committed denominator posture;
- failed, excluded, errored, data-unavailable, not-attempted, invalid, aborted,
  filtered, and successful variants remain visible;
- aggregate counts reconcile to per-window rows.

Future query/list-view work, if authorized, should expose window manifests,
per-window outcomes, aggregate outcomes, data-gap posture, and integrity views.
Query surfaces must remain read-only and descriptive unless a later package
explicitly authorizes more.

Future integrity views should flag overlapping or reversed windows, missing
lineage, denominator shrinkage, missing gap posture, aggregate/per-window count
mismatches, and any result population that claims windowed evidence without
window identity.

No canonical write should occur without Karl/Main authorization for the exact
window protocol, runner behavior, artifact/schema/query impact, and validation
evidence.

## Relationship To WP-ROBUST-C1

WP-ROBUST-C1 brought up read-only robustness diagnostics over existing
committed result populations. It reports denominator posture and withholds
numeric PSR, DSR, and MinTRL values when required formula inputs are absent.

`WP-ROBUST-C2-DESIGN` defines a future chronology-aware validation layer. It
does not change the C1 diagnostic, does not convert C1 output into authority,
does not compute PSR / DSR / MinTRL, and does not create a result-population or
query-layer dependency.

The two layers are complementary:

- C1 asks what statistical robustness diagnostics can be described from a
  committed result population.
- C2 asks how future evidence should preserve chronological selection and
  evaluation boundaries before any statistical or advisory consumer interprets
  the output.

Neither layer approves a strategy, ranks a candidate with authority, satisfies
D2-006, satisfies REC-5, creates readiness, creates promotion authority, or
contacts paper/live/runtime/protected paths.

## Explicit Deferrals

Deferred and unauthorized in this package:

- runner or backtester changes;
- schema changes;
- validator changes;
- query-layer changes;
- result-population writes or mutations;
- window-manifest artifact creation;
- Strategy Spec, variant manifest, or sweep plan changes;
- canonical data-lineage changes;
- PSR / DSR / MinTRL formula implementation;
- CPCV, bootstrap, Monte Carlo, or permutation implementation;
- strategy ranking, recommendation, readiness, promotion, or lifecycle action;
- dashboard or operator-review implementation;
- paper/live/runtime authority;
- OMS, risk, reconciliation, safe-mode, broker, exchange, collateral, or
  protected-path changes;
- autonomous agent behavior.

## Future Package Shape

A safe future sequence would likely split work into narrow packages:

1. docs-only window protocol lock with exact boundary, purge/embargo, and
   denominator rules;
2. schema/validator support for a window manifest or equivalent artifact if
   Main/Karl chooses an artifact-backed path;
3. runner dry-run support with no canonical write;
4. query/integrity surfaces if artifact-backed window evidence is committed;
5. separately authorized canonical windowed result-population write.

Each package must start from refreshed repo truth, preserve protected
boundaries, inspect actual changed files, and validate its exact package class.
