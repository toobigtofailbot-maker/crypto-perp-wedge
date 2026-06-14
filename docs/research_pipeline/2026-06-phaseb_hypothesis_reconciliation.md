# Phase-B Hypothesis Reconciliation

## Status / Authority Boundary

Status: `design reconciliation`.

This note binds the first Phase-B hypothesis design draft to the current merged
A1 / A2 / A3 Strategy Spec grammar. It is not a pre-registration, not frozen,
not a Strategy Spec, not a variant manifest, not a sweep plan, not a candidate
registry entry, not canonical evidence, and not executable authority.

It authorizes no compiler, schema, validator, catalog, runner, backtester,
library, result-population, trial-log, candidate lifecycle, ranking, readiness,
promotion, paper/live/runtime, OMS/risk/reconciliation, broker/exchange,
collateral, data-acquisition, or autonomous behavior change.

Future freeze and canonical execution require separate Karl-gated packages.

## Repo-Truth Basis

Fact: `WP-EXPRESS-A1` is merged and adds the closed
`composition_type: "z_score"` composed operand with `value_operand`,
`center_operand`, `scale_operand`, and `zero_scale_policy: "null_output"`.

Fact: `WP-EXPRESS-A2` is merged and compiler-supported `trend` and existing
`regime` group roles are accepted as entry-gate roles. In a both-direction
shape, non-side-labeled shared gates compile through `filters.groups`; root
`entry_logic.groups` for `direction: "both"` must be side-labeled `long` or
`short`.

Fact: `WP-EXPRESS-A3` is merged and adds optional
`entry_logic.entry_controls.min_bars_between_entries` as an integer literal in
`[1, 100000]`. The current compiler applies it as a shared final-stream
throttle for both-direction specs.

Fact: `WP-ROBUST-C3` is merged and the read-only robustness helper reports both
the committed result-population denominator and the current trial-log
denominator. Numeric PSR, DSR, and MinTRL remain withheld when required formula
inputs are absent.

Fact: `RP-7520` is canonical dynamic-equity-target-leverage evidence for
`STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002` over BTCUSDT 15m D4 data. It
has committed denominator `10`, actual result rows `10`, and `10` successful
rows. Its rows do not reproduce the prior uniform liquidation artifact, but the
population remains materially negative and cost-dragged.

Inference: `RP-7520` motivates a next design that tests whether
volatility-normalized distance, trend/regime entry gating, and explicit
re-entry throttling can reduce raw SMA-band churn and cost drag. It does not
prove that the new design has edge.

Decision in this reconciliation: the first Phase-B design remains a BTCUSDT
15m volatility-normalized, regime-gated mean-reversion research question, with
both-direction posture retained for symmetry and with shared trend/regime gates
expressed through `filters.groups` under current compiler truth.

## Economic Rationale

Volatility-normalized distance is the hypothesis core because the same raw
price distance from a moving centerline has different information content
across volatility regimes. A percentage or absolute SMA band can be too tight
in high volatility and too loose in low volatility. The merged A1 `z_score`
operand lets the spec express `(close - centerline) / scale` through reviewed
compiler-owned code, using closed `data_ref` and `indicator_ref` operands
instead of an expression language.

Trend/regime gating is intended to avoid structurally bad mean-reversion
conditions. A standardized dislocation against persistent directional pressure
can become a sequence of losing fades. The merged A2 entry-gate role support
lets the future design require deterministic trend and regime predicates before
normal long/short dislocation entries can fire.

`min_bars_between_entries` is intended to reduce cost drag and overtrading. The
RP-7520 SMA-band population had high trade counts and materially negative net
returns after fees and fixed-bps slippage. A shared A3 re-entry throttle should
test whether fewer repeated entries around the centerline can lower turnover
without using post-hoc variant selection.

RP-7520 motivates the direction by showing that raw both-direction SMA bands,
even after dynamic 1x sizing removed the fixed-size liquidation artifact, did
not show evidence-level edge and remained cost-dragged. This motivation is not
evidence that the reconciled Phase-B shape will pass.

Fees, fixed-bps slippage, and funding remain research-realism inputs to inspect
in later evidence. This note does not provide execution guidance, order
placement guidance, or live-trading advice.

## Closed-Spec Shape

Chosen design posture: both-direction BTCUSDT 15m mean reversion.

Merged grammar elements used:

- A1: `operand_type: "composed_operand"` with `composition_type: "z_score"`.
- A2: shared `filters.groups` with `group_role: "trend"` and
  `group_role: "regime"` as entry gates.
- A3: `entry_logic.entry_controls.min_bars_between_entries`.

Intended groups:

- Long root entry group: side-labeled `required` group. Entry when
  `z_score(close, SMA(center_lookback_bars), STDDEV(vol_lookback_bars))` is
  below a negative threshold.
- Short root entry group: side-labeled `required` group. Entry when the same
  z-score is above a positive threshold.
- Shared trend gate: `group_role: "trend"` in `filters.groups`, using closed
  SMA comparison grammar such as `close > SMA(trend_lookback_bars)`.
- Shared regime gate: `group_role: "regime"` in `filters.groups`, using closed
  volatility grammar such as `STDDEV(vol_lookback_bars) > fixed minimum`.
- Exits: side-specific centerline exits, long on `close >= SMA(center)`, short
  on `close <= SMA(center)`.
- Entry throttle: literal `min_bars_between_entries` value materialized in
  `entry_logic.entry_controls`.

NON-FROZEN COMPILE PROBE SHAPE:

```text
strategy_spec_id: STRAT-SPEC-9999  # in-memory probe only; not committed
status: draft
entry_logic:
  direction: both
  entry_controls:
    min_bars_between_entries: 8
  groups:
    - group_id: PROBE-LONG-ZSCORE-ENTRY
      group_role: required
      side: long
      condition:
        left_operand:
          operand_type: composed_operand
          composition_type: z_score
          value_operand: close
          center_operand: sma(center_lookback_bars)
          scale_operand: stddev(vol_lookback_bars)
          zero_scale_policy: null_output
        operator: lt
        right_operand: -1.5
    - group_id: PROBE-SHORT-ZSCORE-ENTRY
      group_role: required
      side: short
      condition:
        left_operand: same z_score operand
        operator: gt
        right_operand: 1.5
filters:
  groups:
    - group_role: trend
      condition: close gt sma(trend_lookback_bars)
    - group_role: regime
      condition: stddev(vol_lookback_bars) gt 1.0
exit_logic:
  groups:
    - group_role: exit
      side: long
      condition: close gte sma(center_lookback_bars)
    - group_role: exit
      side: short
      condition: close lte sma(center_lookback_bars)
```

The probe shape compiles under current merged grammar. It is not a frozen
Strategy Spec and does not reserve `STRAT-SPEC-9999`.

## Draft Grid / Free Parameters

Draft future freeze grid:

| Axis | Draft values | Free parameter? | Notes |
|---|---:|---|---|
| `center_lookback_bars` | `50`, `100` | yes | SMA centerline lookback. |
| `vol_lookback_bars` | `30`, `50` | yes | STDDEV scale lookback for z-score. |
| `trend_lookback_bars` | `100`, `200` | yes | Slow SMA trend gate lookback. |
| `min_bars_between_entries` | `8`, `24` | yes | A3 literal per variant in future materialization. |

Free-parameter count: `4`.

Fixed design constants in this reconciliation:

- primary timeframe: `15m`;
- direction: `both`;
- z-score entry thresholds: `-1.5` for long and `1.5` for short;
- regime minimum: `stddev(vol_lookback_bars) > 1.0`;
- exit rule: centerline return;
- sizing and cost model: inherit later authorized runner/backtest-realism
  surface, expected to use the current comparable dynamic-equity 1x realism
  model unless a later package explicitly changes that.

Draft denominator implication: a future sweep denominator should be the full
Cartesian product of declared axes, plus any explicitly retained failed,
errored, invalid, excluded, filtered, data-unavailable, not-attempted, or
aborted variants according to repo denominator rules. The four-axis grid above
implies `2 * 2 * 2 * 2 = 16` declared variants before any explicitly retained
non-success rows.

If a future freeze wants z-threshold as a swept symmetric axis, it must first
confirm an exact closed representation that does not require unapproved
arithmetic or hidden derived parameters.

## Success Criteria For Later Review

Future evaluation questions:

- Does volatility normalization reduce the raw SMA-band cost-drag pattern
  observed in RP-7520?
- Does the trend/regime gate reduce adverse fades without removing so many
  opportunities that the evidence becomes sparse?
- Does `min_bars_between_entries` reduce trade count, fees, and fixed-bps
  slippage without depending on post-hoc variant selection?
- Does net PnL remain dominated by fees, slippage, or funding after the churn
  controls are applied?
- Are drawdown, trade count, and cost burden stable enough across declared
  variants to justify further review?
- Are denominator records complete and visible for successful and non-success
  rows?

Provisional pass/fail review criteria for a later single-slice trial:

- Favorable evidence would require materially lower trade counts and lower
  cost drag than the comparable RP-7520 family while avoiding near-total-loss
  drawdowns.
- Cost-drag mitigation should be inspected through fees, slippage, funding,
  gross PnL, net PnL, trade count, and return/drawdown together. Gross-only
  improvement is insufficient.
- No winner-only, successful-only, or executed-only denominator may be used.
- OOS/walk-forward expectations remain a future rigor layer under C2-style
  chronology discipline. They are not required for the first single-slice trial
  unless a later package explicitly authorizes that protocol.
- C1/C3 robustness diagnostics should be run read-only when later evidence
  exists; numeric PSR, DSR, or MinTRL values must remain withheld if required
  inputs are absent.

This section does not approve, recommend, select, rank, promote, or mark any
candidate as paper-ready or live-ready.

## C3 Trial-Accounting Interpretation

Read-only C3 diagnostic over current `RP-7520` reports:

- Result-population denominator: `10`.
- Trial-log denominator: `32` valid rows.
- Numeric PSR / DSR / MinTRL: withheld because required formula inputs remain
  absent.

Interpretation for future Phase-B trials:

- The result-population denominator is the committed pre-registered population
  count for that specific frozen Strategy Spec / Variant Manifest / Sweep Plan
  family. For the draft grid above, that would be `16` if frozen unchanged.
- The trial-log denominator is the full valid `research/trial_log.jsonl` row
  count available at evaluation time when trial-log DSR posture is inspected.
  Phase-B canonical trials would increase that count when they are genuine OOS
  evaluations and are logged under repo rules.
- Rigorous DSR still needs effective independent-trial count, benchmark Sharpe,
  return-distribution moments, sample length, and a declared selection rule.
  Current repo truth supports the denominator distinction, not fabricated
  numeric DSR.

No material denominator ambiguity was found for this reconciliation.

## Compile Probe

The compile probe used an in-memory Strategy Spec-like payload derived from
`STRAT-SPEC-0002`, modified only inside the Python process, and synthetic OHLCV
data. It wrote no Strategy Spec, variant manifest, sweep plan, result
population, scratch file, or test.

Command form:

```powershell
@'
# Python snippet:
# - loads research/schemas/strategy_spec.schema.json
# - loads research/strategy_specs/STRAT-SPEC-0002.strategy_spec.json as a shape base
# - replaces the body with the NON-FROZEN COMPILE PROBE SHAPE above
# - validates with jsonschema.Draft202012Validator(schema).validate(spec)
# - imports tools.research_runner.spec_signal_compiler.compile_signal
# - compiles against deterministic synthetic 15m OHLCV
'@ | C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -
```

Result:

```text
schema_validation=PASS
compiler_construction=PASS
signal_name=signal
signal_length=260
signal_index_start=2026-01-01T00:00:00+00:00
signal_index_end=2026-01-03T16:45:00+00:00
signal_unique_values=[-1.0, 0.0]
nonzero_count=18
probe_artifacts_written=NO
```

The probe proves schema acceptance and compiler construction for the intended
closed grammar shape. It does not re-prove no-lookahead, profitability,
robustness, or execution realism.

## Freeze Prerequisites

A later Karl-gated pre-registration package is required before any
`STRAT-SPEC`, `VM`, or `SWEEP-PLAN` freeze.

A later Karl-gated trial package is required before any canonical
result-population write.

This reconciliation creates no freeze authority, no pre-registration
authority, no canonical write authority, and no candidate/paper/live/runtime
authority.
