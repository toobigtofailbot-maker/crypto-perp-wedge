# Compiler Multi-Timeframe No-Lookahead Design

## Authority And Boundary

This document is design only.

It creates no implementation, compiler behavior, schema behavior, validator behavior, indicator catalog behavior, runner behavior, backtester behavior, canonical evidence, strategy approval, ranking, recommendation, readiness, promotion, runtime, paper, live, OMS, risk, reconciliation, safe-mode, kill-switch, broker, exchange, or order authority.

Current repo truth remains unchanged:

- Strategy Specs are declarative and non-executable.
- Indicator catalog entries declare interfaces only.
- The compiler owns reviewed computation.
- Catalog data is not interpreted as formulas or executable logic.
- There is no expression language, `eval`, `exec`, lambda, dynamic import, notes-as-computation, or catalog-data computation path.
- Non-empty Strategy Spec operand `timeframe` values currently fail closed in `tools/research_runner/spec_signal_compiler.py`.
- No multi-timeframe alignment implementation exists in the current compiler, runner, or backtester path.

## Repo-Truth Basis

Files inspected for this design:

- `research/schemas/strategy_spec.schema.json`
- `tools/research_runner/spec_signal_compiler.py`
- `tests/test_spec_signal_compiler.py`
- `docs/status_entries/WP-EXPRESS-A1.md`
- `docs/status_entries/WP-EXPRESS-A2.md`
- `docs/status_entries/WP-EXPRESS-A3.md`
- `docs/research_pipeline/2026-06-compiler_extension_tranche_plan.md`
- `docs/research_pipeline/2026-06-compiler_indicator_first_block_options.md`
- `docs/research_pipeline/2026-06-computation_binding_tranche_checkpoint.md`

Repo-truth findings:

- A1 z-score support is already compiler-owned as a closed composed operand. This design does not reimplement it as an indicator.
- A2 `trend` and `regime` group roles are already compiler-supported entry gates. This design does not re-add group-role semantics.
- A3 `entry_logic.entry_controls.min_bars_between_entries` already exists. This design does not alter trade-frequency or cooldown semantics.
- Multi-timeframe handling remains deferred because data alignment, runner input contracts, compiler alignment, gap handling, and no-lookahead proof are not compiler-only concerns.

## Concepts

**Base timeframe:** The timeframe of the primary signal grid. The compiled output index is the base timeframe index. Example: a 15m Strategy Spec producing one signal value per 15m bar.

**Informative timeframe:** A coarser timeframe used as confirmation or context for the base timeframe. Example: 1h trend state used by 15m entry logic.

**Closed informative candle:** An informative candle whose full interval has ended and whose OHLCV values are complete. A 1h candle covering 10:00:00 through 10:59:59 UTC is closed at 11:00:00 UTC, assuming the data source uses left-labeled open timestamps.

**Availability timestamp:** The earliest timestamp at which a closed informative candle may be visible to the base timeframe alignment resolver. For OHLCV candles, this is the candle close timestamp, not the candle open timestamp.

**Forward fill:** Carrying the most recent already-closed informative value onto later base bars until a newer informative candle becomes available. Forward fill is allowed only from closed informative values and only after the availability timestamp.

**Causal shift:** The mandatory alignment shift that prevents a higher-timeframe candle value from being visible on lower-timeframe bars before the higher-timeframe candle closes. With left-labeled informative candles, causal shift maps each informative value from its open timestamp label to its close or availability timestamp before any lower-timeframe merge.

**Warmup:** The period before an informative indicator has enough prior informative candles to produce a valid value and before that value is available on the base grid. Warmup nulls must block conditions or fail closed according to the future grammar's null policy.

**Missing informative value:** Any informative value that is absent because the candle is missing, incomplete, invalid, outside the available history, blocked by gap policy, or still in warmup. Missing informative values must remain null or fail closed. They must not be guessed, backfilled, interpolated, or silently replaced.

## No-Lookahead Rules

Future implementation must satisfy these rules before any multi-timeframe Strategy Spec path is allowed to compile:

1. A higher-timeframe value can only be visible to a lower-timeframe bar after the higher-timeframe candle is closed.
2. A same-open higher-timeframe value is not available before its close. A 1h value labeled `10:00` is not available to 15m bars at `10:00`, `10:15`, `10:30`, or `10:45`.
3. Forward-filled informative values must be the last closed informative candle value, shifted to its availability timestamp before fill.
4. Informative timeframe must be greater than or equal to the base timeframe. Downsampling from a lower-than-base informative timeframe is out of scope until a later design explicitly handles it.
5. Informative and base indexes must be timezone-aware UTC or otherwise normalized to an explicitly proven UTC contract before alignment.
6. Informative data must be monotonic and duplicate-free before alignment.
7. Incomplete informative candles must not be exposed.
8. Missing informative data must fail closed or remain null, not be guessed, backfilled, interpolated, or filled from future values.
9. A base bar may consume an informative value only when `informative_availability_timestamp <= base_bar_timestamp`, subject to the future package's exact signal timing contract.
10. The compiler must preserve existing closed computation boundaries: no formula strings, no dynamic indicator definitions, and no catalog-data-interpreted computation.

## Borrowed Patterns

These are design references only. They do not import external code, external APIs, external semantics, dependencies, or canonical output into this repo.

- Freqtrade documents an informative-data merge helper intended to merge informative data into a main dataframe without lookahead bias and with optional forward fill: [Freqtrade strategy customization](https://www.freqtrade.io/en/stable/strategy-customization/).
- Freqtrade separately documents lookahead-analysis concerns for full-dataframe backtests where future candles can be accidentally referenced: [Freqtrade lookahead analysis](https://www.freqtrade.io/en/stable/lookahead-analysis/).
- Backtrader documents resampling and multiple-timeframe behavior where larger timeframes can delay strategy operation until sufficient larger-timeframe data exists: [Backtrader data resampling](https://www.backtrader.com/docu/data-resampling/data-resampling/) and [Backtrader multiple timeframes](https://www.backtrader.com/docu/data-multitimeframe/data-multitimeframe/).

Repo decision: these patterns are useful references for causal shifting, optional forward fill from closed values, and warmup/start-delay awareness. The future repo implementation must still be owned by this repo's schema, validator, compiler, data contracts, tests, and artifact provenance.

## Fixture-Style Example

Assumptions:

- Base timeframe: 15m.
- Informative timeframe: 1h.
- Timestamps are UTC.
- Candles are left-labeled by open time.
- The 1h candle labeled `10:00` covers `[10:00, 11:00)` and closes at `11:00`.
- Future policy allows a closed informative value to be used on the base bar whose timestamp equals the informative close timestamp.

| Base bar timestamp | Informative candle label | Informative candle status at base timestamp | Correct aligned informative value | Invalid leaked value |
|---|---:|---|---|---|
| 10:00 | 10:00 | open, not closed | previous closed 1h value or null | 10:00 1h close |
| 10:15 | 10:00 | open, not closed | previous closed 1h value or null | 10:00 1h close |
| 10:30 | 10:00 | open, not closed | previous closed 1h value or null | 10:00 1h close |
| 10:45 | 10:00 | open, not closed | previous closed 1h value or null | 10:00 1h close |
| 11:00 | 10:00 | closed and available | 10:00 1h closed value | 11:00 1h close |
| 11:15 | 11:00 | open, not closed | 10:00 1h closed value | 11:00 1h close |

Correct alignment:

```text
1h raw label:          10:00
1h candle interval:    [10:00, 11:00)
1h availability:       11:00
15m visible from:      11:00, 11:15, 11:30, 11:45
```

Invalid leaked alignment:

```text
1h raw label 10:00 value is merged directly onto 15m bars from 10:00 onward.
This exposes the 10:00-10:59 1h close, high, low, volume, or derived indicator
before the 1h candle is closed.
```

## Future Implementation Sketch

Future implementation should be split into explicit packages. This document does not authorize any of them.

**Schema fields:**

- Add a closed multi-timeframe declaration under the Strategy Spec grammar only after Main/Karl authorization.
- Candidate fields may include `base_timeframe`, `informative_timeframes`, `alignment_policy`, `availability_policy`, `forward_fill_policy`, `missing_informative_policy`, and `allowed_timeframe_pairs`.
- Preserve existing declarative/non-executable posture and forbid formula fields.

**Compiler resolver:**

- Resolve base operands on the base OHLCV frame as today.
- Resolve informative operands only through a repo-owned alignment resolver.
- Shift informative candle labels to availability timestamps before joining to the base index.
- Forward-fill only closed informative values when the policy allows it.
- Preserve null/warmup values so existing condition evaluation can fail closed.
- Reject unsupported timeframe relationships rather than falling back to primary data.

**Tests:**

- Synthetic 15m/1h fixture proving the `10:00` 1h candle is invisible before `11:00`.
- Mutation test proving changes to an incomplete or future informative candle do not alter earlier base signals.
- Warmup tests for informative indicators.
- Missing/incomplete informative candle fail-closed tests.
- Duplicate, non-monotonic, and ambiguous timezone rejection tests.
- Forward-fill tests proving only last closed values are carried.
- Determinism tests for repeated compile runs.

**Fixtures:**

- Minimal UTC 15m base OHLCV fixture.
- Minimal UTC 1h informative OHLCV fixture.
- Explicit invalid leaked-alignment fixture for rejection or assertion.
- Optional gap/incomplete-candle fixture.

**Validator updates:**

- Enforce supported timeframe ordering.
- Enforce declared informative timeframes are in the locked timeframe set unless a later data package authorizes otherwise.
- Enforce paired data source declarations for every informative timeframe.
- Reject unknown alignment policies, missing availability policy, and executable/protected keys.

**Data alignment helper:**

- Provide a pure deterministic helper that accepts base and informative frames and returns an aligned informative series or frame.
- Require UTC monotonic duplicate-free indexes.
- Require explicit candle duration or a locked timeframe parser.
- Refuse incomplete final informative candles unless future data provenance proves closure.
- Return alignment facts for provenance and tests.

**Status and provenance:**

- Future result populations using MTF must record the base timeframe, informative timeframe set, alignment policy version, source data identities, gap policy, missing-data counts, and aligned-row counts.
- Any alignment policy version change must be identity-bearing for future canonical results.
- Existing result populations must not be mutated to backfill MTF metadata.

## Stop Conditions For Future Implementation

Future implementation packages must stop and report if any of these cases arise:

- Informative timeframe is lower than the base timeframe.
- Timestamp timezone is ambiguous, missing, mixed, or not provably UTC.
- Informative close timestamp or candle duration cannot be derived from a locked contract.
- Base or informative index is non-monotonic.
- Base or informative index contains duplicate timestamps.
- Informative candle is incomplete.
- Alignment would expose a future candle to an earlier base bar.
- Alignment requires backfill, interpolation, guessed values, or silent gap repair.
- Required informative data source is absent from committed repo truth or lacks provenance.
- Gap policy conflicts with `data/irreparable_gaps.json` or existing data-catalog rules.
- A safe implementation would require changes to runtime, paper/live, OMS, risk, reconciliation, safe-mode, kill-switch, broker, exchange, order, or protected execution paths.
- The package pressure shifts from design/compiler/data alignment into candidate promotion, readiness, ranking, recommendation, or runtime use.

## Future Decision Points

Future Main/Karl decisions needed before implementation:

- Whether first MTF support should consume pre-existing coarser OHLCV files, derive coarser bars from base data, or support both under separate provenance.
- Whether equality at `availability_timestamp == base_bar_timestamp` is allowed for signal evaluation, or whether the signal timing contract requires the next base bar after availability.
- Whether forward fill is mandatory, optional, or disabled by default.
- Whether MTF alignment belongs in a data-layer helper first, runner input contract first, compiler resolver first, or a staged split.
- Whether funding and non-OHLCV informative streams reuse the same availability model or require stream-specific designs.
