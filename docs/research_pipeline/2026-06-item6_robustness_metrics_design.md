# WP-S2c-212 Item 6 Robustness Metrics Design

## Scope

This document designs item 6 robustness metrics for complete result populations. It is design-only. It does not compute PSR, DSR, MinTRL, or any other metric. It does not mutate result-population artifacts, create a robustness output artifact, rank variants, approve a strategy, create readiness or promotion authority, or contact runtime, paper, live, broker, exchange, OMS, reconciliation, risk, safe-mode, or protected execution paths.

## Current Repo State

RP-2134 is the first valid canonical 15m result population. It was generated from `STRAT-SPEC-0001`, `VM-0001`, and `SWEEP-PLAN-0001`.

RP-2134 contains seven variant rows and committed denominator 7. Its `committed_denominator_snapshot` records denominator basis `committed_pre_registered_population_count`, forbids winner-only, successful-only, and executed-only denominators, and preserves failed, errored, excluded, filtered, data-unavailable, not-attempted, invalid, and aborted variants as denominator members.

RP-2134 used a 96-row temporary 15m OHLCV CSV fixture/input. The committed artifact records `data_catalog_ref=15m_ohlcv_test_fixture_offline_only` and `data_slice_identity=csv_fixture:sha256:90c38fd1fe4f2e86ee0a2ad1a4efaca4af7fde0f8f5bc75d8b1cfe54c16dabd0`. It is pipeline evidence only, not strategy-quality evidence from production exchange history.

The current result-population schema records per-variant summary metrics but does not record per-bar return series, observation count, skewness, kurtosis, benchmark Sharpe, evaluation-period length, or annualization convention fields.

## Item 6 Purpose

Item 6 is robustness / multiple-testing-aware descriptive metrics over complete result populations.

Item 6 is not promotion authority, ranking authority, readiness authority, paper/live authority, strategy approval, gate authority, transition authority, or downstream lifecycle authority.

The design goal is to preserve population honesty while making future PSR, DSR, and MinTRL outputs inspectable as descriptive evidence. Any future implementation must keep the committed denominator visible and must disclose missing or assumed statistical inputs.

## Metrics

PSR, Probabilistic Sharpe Ratio, should describe the probability that an observed Sharpe exceeds a benchmark Sharpe under the declared sample-length and distribution assumptions. A rigorous implementation usually needs observed Sharpe, benchmark Sharpe, number of observations, skewness, and kurtosis. RP-2134 currently provides observed summary Sharpe only, so PSR cannot be computed rigorously from current artifact fields alone without additional inputs or explicit assumptions.

DSR, Deflated Sharpe Ratio, should adjust apparent Sharpe for multiple testing or selection across the committed variant population. For RP-2134, the committed population size is 7 and must be the denominator input. A rigorous implementation usually also needs the selected or observed best Sharpe convention, effective number of trials, sample length, and distribution assumptions such as skewness and kurtosis. RP-2134 does not record enough fields for a rigorous DSR formula without additional inputs or explicit assumptions.

MinTRL, Minimum Track Record Length, should describe the minimum observation length needed for a Sharpe estimate to reach a target confidence level against a declared benchmark Sharpe. A rigorous implementation usually needs observed Sharpe, benchmark Sharpe, target confidence, frequency / annualization convention, and distribution assumptions. RP-2134 does not record the required observation count or return-distribution fields, so MinTRL cannot be computed rigorously from the current artifact alone.

This design intentionally does not lock exact formulas because the current result-population artifact lacks several formula-critical inputs. Future implementation must either derive those inputs from a separately authorized return-series source or emit missing-input warnings and withhold affected metrics.

## Input Mapping

Current RP-2134 fields that can support future robustness reporting:

- `variant_result_rows[].variant_id`: variant identity.
- `variant_result_rows[].metrics.sharpe`: observed summary Sharpe.
- `variant_result_rows[].metrics.return_pct`: observed summary return.
- `variant_result_rows[].metrics.pnl`: observed summary PnL.
- `variant_result_rows[].metrics.trade_count`: trade count.
- `variant_result_rows[].metrics.drawdown`: drawdown summary.
- `variant_result_rows[].outcome_category`: closed outcome enum membership.
- `variant_result_rows[].attempted`: attempted status.
- `committed_denominator_snapshot.committed_denominator`: committed denominator for multiple-testing-aware metrics.
- `outcome_category_counts`: complete outcome-count accounting.
- `data_coverage_summary`: data source, timeframe, stream, missing-data posture, and fixture-only status.
- `backtest_assumption_summary`: fee, funding, slippage, fill, liquidation, mark-source, and bar-path assumptions.

Missing or weak inputs for rigorous PSR / DSR / MinTRL:

- Return series / per-bar returns: absent.
- Number of observations: absent.
- Skewness: absent.
- Kurtosis: absent.
- Benchmark Sharpe: absent.
- Evaluation period length: absent.
- Frequency / annualization convention: absent as a robustness input, though the artifact records 15m timeframe.
- Effective number of trials: absent as a distinct field; committed denominator 7 exists and must be the first denominator rule for RP-2134.
- Selection rule for which Sharpe is being tested: absent.
- Production exchange-history data basis: absent for RP-2134; it is fixture/input pipeline evidence only.

## Denominator Policy

DSR and any multiple-testing-aware metric must use the committed denominator, not a winner-only, successful-only, or executed-only denominator.

For RP-2134, the committed denominator is 7. All seven variants are currently `successful`, but that fact must not weaken the rule for future populations. Failed, errored, invalid, excluded, filtered, data-unavailable, not-attempted, and aborted variants remain denominator members.

No post-hoc cleanup is allowed. Any future treatment of failed, errored, data-unavailable, or otherwise non-successful variants must be explicit, denominator-preserving, and visible in output notes or warnings.

## Output Posture

Future outputs may use descriptive terms such as:

- `psr`
- `dsr`
- `min_trl`
- `benchmark_sharpe`
- `input_population_id`
- `committed_denominator_used`
- `assumption_notes`
- `missing_input_warnings`

Future outputs must not use authority-bearing terms unless Main later authorizes promotion semantics. Forbidden terms include:

- `approved`
- `recommended`
- `ready`
- `selected`
- `winner`
- `ranked_best`
- `paper_ready`
- `live_ready`
- `promotion`

Derived robustness outputs must state that they are descriptive only and do not replace EXP, REP, OL, REC, DEC, lifecycle, approval, gate, paper/live, or runtime authority.

## Implementation Options

Option A: compute robustness metrics as a derived non-authoritative view/report over existing result populations.

- Scope: narrowest if implemented as a read-only report or CLI printout that consumes committed result populations.
- Schema impact: none if no artifact is committed and no schema is changed.
- Query impact: none if implemented outside the query layer; query impact appears only if a view is added.
- Validator impact: none if no new artifact family or schema field is introduced.
- Artifact mutation risk: low if RP-2134 and future result populations remain immutable inputs.
- Speed: highest.
- Boundary risk: lowest, provided unsupported metrics are withheld or warning-only.

Option B: create a new robustness artifact family.

- Scope: larger because it needs artifact grammar, schema, validator, storage convention, and likely query visibility.
- Schema impact: new schema required.
- Query impact: likely additive query registration and views.
- Validator impact: new validator required.
- Artifact mutation risk: low for result populations, but new artifact lifecycle and identity rules must be designed.
- Speed: medium / slower.
- Boundary risk: moderate because output language must avoid authority semantics.

Option C: extend `result_population` schema to include `robustness_summary`.

- Scope: largest and most invasive for current item 6.
- Schema impact: changes existing result-population schema.
- Query impact: likely query and test updates.
- Validator impact: validator update required.
- Artifact mutation risk: high if existing committed populations are expected to gain the field; RP-2134 must not be mutated in place.
- Speed: lowest.
- Boundary risk: highest because summary fields inside a result population could be misread as part of the population's scientific identity unless carefully isolated.

Preferred design direction: Option A for the first implementation attempt, with strict missing-input behavior.

## Recommended 212a Path

Classification: `212a-narrow`, with a constraint.

WP-S2c-212a can proceed narrowly only if it implements a derived, non-authoritative report/view surface that reads existing result populations, does not mutate RP-2134, does not change schemas, does not change the query layer, and withholds rigorous PSR / DSR / MinTRL computations when required inputs are absent. For RP-2134 specifically, a narrow 212a should be allowed to report denominator 7, observed summary Sharpe values, fixture-only data posture, and explicit missing-input warnings.

If Main requires actual PSR / DSR / MinTRL numeric computation from committed artifacts, the path becomes `212a-expanded` or later split work because current artifacts do not carry return-series, observation-count, skewness, kurtosis, benchmark-Sharpe, or annualization inputs.

## Stop Conditions For 212a

Stop any implementation follow-up if it requires:

- Mutating RP-2134.
- Creating promotion, ranking, readiness, transition, paper/live, or strategy-approval semantics.
- Changing `result_population` schema.
- Changing query-layer behavior.
- Computing formulas with unsupported or hidden inputs.
- Contacting runtime, paper, live, broker, exchange, OMS, reconciliation, risk, safe-mode, or protected execution paths.
- Treating fixture metrics as strategy-quality evidence.
- Dropping failed, errored, data-unavailable, not-attempted, or otherwise non-successful variants from the committed denominator.

## Relationship To Faster Execution Model

Item 6 fits Research Block 1 as design plus a possible narrow derived implementation. Routine document mechanics do not need report-back, but the implementation path decision does.

If Main accepts the narrow path, WP-S2c-212a can proceed as a derived non-authoritative implementation with no schema change and no result-population mutation. If Main wants schema-backed robustness artifacts, query-layer surfaces, validator-backed outputs, or numeric formulas that require absent inputs, the work must split before implementation.

## Decision For Report-Back

Fact: RP-2134 has denominator 7 and summary metrics only, over a 96-row 15m fixture/input.

Inference: Current artifact fields are sufficient for denominator-honesty reporting and missing-input diagnostics, but insufficient for rigorous PSR / DSR / MinTRL computation without added inputs or explicit assumptions.

Decision: Recommend `212a-narrow` only for a derived descriptive report/view that does not mutate artifacts and withholds unsupported metric values. Numeric PSR / DSR / MinTRL computation should wait for a separately scoped path if Main wants return-series-backed formulas or schema/query-backed committed outputs.

Open question: Should Main accept a first 212a that reports denominator policy and missing-input warnings only, or require a split package that first adds return-series / observation-count support before computing robustness metrics?

Future option: A later artifact family may be useful once formula inputs are available and Main wants committed robustness evidence. That is not needed for the narrow 212a path.
