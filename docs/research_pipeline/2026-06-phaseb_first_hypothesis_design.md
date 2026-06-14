# Phase-B First Hypothesis Design Draft

## Status / Authority Boundary

Status: `design draft`.

This note is not frozen, not executable, not a Strategy Spec, not a variant
manifest, not a sweep plan, not a candidate registry entry, not evidence, not
a canonical artifact, and not candidate authority.

It authorizes no implementation, schema change, validator change, compiler
change, runner change, result-population write, data acquisition, candidate
lifecycle action, ranking, readiness claim, promotion, paper/live/runtime
behavior, OMS/risk/reconciliation behavior, broker/exchange connectivity,
collateral movement, or autonomous behavior.

Future execution requires separate explicit authorization after the required
primitive and validation surfaces are merged.

## Repo-Truth Basis

Fact: `WP-EXPRESS-A1` is merged on `origin/main` and adds a closed
`z_score` composed operand with fixed `value_operand`, `center_operand`,
`scale_operand`, and `zero_scale_policy: "null_output"` fields.

Fact: the A1 compiler-owned computation is `(value - center) / scale`; null or
zero scale yields null output, and null operands do not make entries true.

Fact: the current merged Strategy Spec surface includes both-direction
long/short semantics, existing OHLCV data refs, `sma`, `ema`, `atr`, and
`stddev` indicator support, `crosses_above` / `crosses_below`, and plus/minus
parameter scaling. A1 adds z-score vocabulary to that closed surface.

Fact: `WP-ROBUST-C1` provides read-only robustness diagnostics over committed
result populations and withholds numeric PSR, DSR, and MinTRL values when
required inputs are absent.

Fact: `WP-ROBUST-C2-DESIGN` is a docs-only walk-forward / OOS design. It
defines chronology, selection/evaluation boundary discipline, complete
population retention, and denominator honesty, but it does not implement a
window manifest, runner behavior, schema, validator, or query surface.

Fact: `RP-7520` is canonical dynamic-equity-target-leverage evidence for
`STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002` over BTCUSDT 15m D4 data. It
preserves denominator 10, records 10 successful rows, does not reproduce the
old uniform liquidation artifact, and shows no evidence-level edge for the raw
both-direction SMA-band family.

Inference: `RP-7520` motivates moving away from raw fixed-percentage SMA bands
toward volatility-normalized entries, trend/regime context, and lower-churn
entry discipline. It does not prove that any mean-reversion family has edge.

Decision in this design draft: the first Phase-B research question should be a
volatility-normalized mean-reversion hypothesis with future trend/regime and
trade-frequency gates, not another raw unnormalized band.

Open question: exact timeframe, window protocol, parameter grid, and trial
accounting posture remain unresolved until later pre-registration work.

## Hypothesis Title

Working title: `BTCUSDT 15m volatility-normalized regime-gated mean reversion`.

Design status: draft only.

This is not a frozen hypothesis, not a registered candidate, not a Strategy
Spec, not a variant population, and not a sweep instruction.

## Economic Rationale

Volatility-normalized deviation could matter because the same absolute or
percentage distance from a moving centerline has different meaning in calm and
volatile regimes. A close that is 0.5% below a centerline may be a small move
in a high-volatility interval and an extreme move in a low-volatility interval.
The merged A1 `z_score` vocabulary can express standardized distance without
opening arbitrary formulas.

Trend/regime context may reduce bad mean-reversion trades because mean
reversion entries taken against persistent directional pressure can become
repeated losing fades. A future gate should ask whether the market is in a
state where fading a standardized dislocation is plausible rather than blindly
fading every dislocation.

Trade-frequency controls are expected to reduce cost drag because RP-7520's
least-bad rows were still materially negative and the tight-band variants
generated thousands of trades. Fees and fixed-bps slippage scale with turnover,
so a Phase-B design should prefer fewer, more selective entries over continuous
re-entry around a centerline.

This rationale is not proof of profitability. It is a reason to draft the next
testable research question after the RP-7520 no-edge/cost-drag finding.

## Intended Closed-Spec Shape

The draft entry concept is a two-sided BTCUSDT 15m mean-reversion family:

- long-side entry concept: close is sufficiently below a centerline when
  measured by an A1 `z_score` or equivalent volatility-normalized distance;
- short-side entry concept: close is sufficiently above the same or equivalent
  centerline when measured by the same standardized distance convention;
- exit concept: return toward the centerline or a separately declared
  standardized-distance exit band;
- no open expression language, no arbitrary arithmetic, no custom script, and
  no data-interpreted computation.

A1-merged vocabulary that may be referenced later:

- `z_score(value_operand, center_operand, scale_operand)` with
  `zero_scale_policy: "null_output"`;
- existing `stddev` or `atr` as candidate scale operands, subject to later
  exact grammar and validation;
- existing closed comparisons against constant or parameter thresholds.

Future A2-dependent trend/regime gate, pending merge:

- gate entries using a closed, deterministic trend/regime predicate;
- prefer existing OHLCV and indicator primitives if sufficient;
- do not treat any unmerged A2 field, enum, schema shape, or compiler behavior
  as settled in this draft.

Future A3-dependent trade-frequency control, pending merge:

- require a cooldown or re-entry discipline after exits before another entry
  may be considered;
- preserve exits and existing both-direction conflict behavior;
- do not treat any unmerged A3 field, enum, schema shape, or state-machine
  behavior as settled in this draft.

This section sketches a shape only. It intentionally avoids a frozen Strategy
Spec, parameter grid, variant manifest, sweep plan, or canonical run.

## Cost-Drag-Mitigation Logic

The future design should treat fees, fixed-bps slippage, and funding as
first-class research realism constraints. It should not assume that a gross
mean-reversion signal can survive turnover costs.

Draft cost-control preferences:

- prefer wider standardized entry thresholds over tight always-on bands if the
  wider threshold materially reduces churn;
- prefer explicit re-entry discipline over immediate re-fading after each
  centerline exit;
- preserve full denominator accounting for all declared variants, including
  low-turnover and high-turnover variants;
- inspect trade count, fees, slippage, funding, gross PnL, net PnL, drawdown,
  and cost-drag behavior together;
- avoid execution guidance, order-placement claims, or live-trading advice.

Failure of cost discipline would be evidence against this Phase-B shape even if
some gross-return metric looks locally favorable.

## Future Test Design Questions

Expected market context: BTCUSDT Binance USDT-M perpetual research only, using
repo-governed data lineage and existing gap policy.

Primary timeframe is a design question. The current draft leans toward 15m
because RP-7520 and the A1 runway are centered on BTCUSDT 15m evidence, but
this is not a final choice. Any later candidate must declare its primary
timeframe and allowed confirmation timeframes before testing.

Potential future windows must follow the C2 posture:

- explicit selection and evaluation intervals;
- no chronology leakage;
- warmup handled outside evaluation counts where applicable;
- complete population retention;
- denominator honesty across all declared variants.

Potential future robustness diagnostics must follow C1 posture:

- report missing formula inputs rather than fabricating PSR, DSR, or MinTRL;
- preserve committed denominator as the first multiple-testing input;
- disclose when return-series, observation-count, skewness, kurtosis,
  benchmark-Sharpe, annualization, or selection-rule inputs are absent.

Trial-accounting dependency: if a later C3 or equivalent trial-accounting
surface exists by execution time, the pre-registration package should bind to
that current repo-truth surface. If no such surface exists, the package should
use the then-current result-population and trial-log discipline without
inventing a new denominator rule inside execution.

## Success And Failure Questions

These are draft evaluation questions, not locked thresholds.

Success questions for a later authorized test:

- Does volatility normalization reduce the raw-band cost-drag pattern observed
  in RP-7520?
- Does trend/regime gating reduce adverse fades without removing most valid
  dislocation opportunities?
- Does re-entry discipline lower trade count and slippage burden without
  relying on post-hoc variant selection?
- Are any observed favorable results stable across explicit OOS windows and
  not concentrated in one interval?
- Are denominator, failed-row, and missing-input records complete enough for
  robustness diagnostics?

Failure questions for a later authorized test:

- Does net performance remain dominated by fees, slippage, or funding despite
  lower turnover?
- Do standardized-distance entries still produce high drawdown or near-total
  loss under dynamic equity target leverage?
- Does the trend/regime gate only help through overfit parameter selection?
- Does the future A3-style re-entry control suppress trades so severely that
  evidence becomes sparse or non-informative?
- Do OOS windows, robustness diagnostics, or denominator checks contradict the
  apparent full-period result?

No draft question above creates approval, selection, readiness, or promotion
authority.

## Required Future Authorization Before Execution

Before this design can become an executable research package, future work must
be explicitly authorized for:

- A2 merge or a replacement merged trend/regime gate surface;
- A3 merge or a replacement merged trade-frequency control surface;
- pre-registration package;
- Strategy Spec creation and freeze;
- variant manifest creation and complete denominator freeze;
- sweep plan creation and freeze;
- canonical run authorization;
- result-population validation;
- candidate review only if later authorized by Main/Karl.

If a safe implementation would require treating unmerged A2/A3 semantics as
settled, changing protected runtime paths, changing OMS/risk/reconciliation, or
creating candidate/ranking/readiness/promotion authority, the future package
must stop and escalate.

## Non-Authority Close

This draft prepares one research question for Phase B. It does not pre-register
that question, execute it, rank it, select it, promote it, or approve it for
paper/live use.
