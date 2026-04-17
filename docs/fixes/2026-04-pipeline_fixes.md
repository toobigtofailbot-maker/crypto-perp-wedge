# Pipeline Fixes (WP-5b)

Date:       2026-04-17
Branch:     wp-5b-pipeline-fixes
Scope:      F-001 (liquidation) and F-002 (Gate 5 pass/fail)
Triggered by: WP-5a audit findings

---

## Section 0: Discovery Results

### 0.1 Test directory and framework

- Test directory: `tests/`
- Framework: pytest
- Existing naming convention: `tests/test_*.py`
- Existing targeted baseline command:
  `.venv\Scripts\python.exe -m pytest tests/test_backtest.py tests/test_evaluation.py -q`
- Baseline result before WP-5b edits: 12 passed, 4 warnings

### 0.2 lib/backtest.py code-path summary

- `BacktestResult` dataclass starts at `lib/backtest.py:50`.
- `run_backtest(...)` starts at `lib/backtest.py:134`; signature unchanged.
- Per-bar equity update happens in the main bar loop. Funding is applied first, fills are applied at next-bar open, unrealized PnL is marked at bar close, and `equity_curve_vals[i]` receives cash equity plus unrealized PnL.
- Position sizing convention is fixed 1-contract exposure. `position` is one of `+1`, `-1`, or `0`; notional is based on the fill price.
- Starting capital is passed as `initial_equity`; existing audit notebooks use `10_000.0`.
- Pre-fix output fields were: `equity_curve`, `trades_df`, `per_bar_pnl`, `realized_pnl`, `unrealized_pnl`, `fees_paid`, `slippage_paid`, `funding_paid`, `skipped_bars`, `skipped_bar_timestamps`, `params`.
- WP-5b added only: `liquidated` and `liquidation_timestamp`.
- Pre-fix code had no equity floor, liquidation, or margin-call logic.

### 0.3 lib/evaluation.py Gate 5 current convention

- `check_promotion_gates(...)` starts at `lib/evaluation.py:419`; signature unchanged.
- `cost_drag(result)` computes:
  - `gross_pnl = result.realized_pnl + result.unrealized_pnl`
  - `total_cost = result.fees_paid + result.slippage_paid + result.funding_paid`
  - `cost_drag_fraction = total_cost / gross_pnl` when `gross_pnl != 0`, else NaN
- Reported field name: Gate 5 `value` from `cost_drag_fraction`.
- Numeric convention: fraction, not percentage. Example: `0.50` means 50%.
- Threshold: `0.50`.
- Previous pass condition: after converting NaN to `0.0`, `drag <= 0.50`.
- WP-5b preserves the formula, field name, scale, and threshold. It changes only Gate 5 pass/fail for `gross_pnl <= 0`.

### 0.4 Promotion-semantics convention

Promotion is all-gates-required:

```python
overall = all(g.passed for g in gates)
```

Any single failed gate means overall NO-GO. This confirms the promotion-semantics dependency for the I-4 verdict-preservation argument.

Repo-truth note: the WP-5a audit report narrative includes sections written when 8 hypotheses had executed, but current `origin/main` includes WP-4b2 and has 10 trial-log entries. WP-5b uses current repo truth: H-001 through H-010 are all concluded NO-GO and all 10 have `oos_sharpe < 1.0`.

---

## Section 1: F-001 Fix -- Liquidation / Bounded Equity

### 1.1 Problem (from WP-5a F-001)

`lib/backtest.py` previously allowed equity to go below zero. This made `max_drawdown(...)` mathematically unbounded above 100%, because drawdown is computed as `(equity - peak) / peak`.

### 1.2 Design decision

WP-5b implements a simple account-death model:

- Liquidation trigger: first bar-close marked equity `<= 0.0`.
- Equity floor: `0.0`.
- On liquidation, the open position is force-closed at a synthetic price that floors cash equity exactly at zero.
- No extra liquidation fee or slippage is introduced.
- After liquidation, equity and per-bar PnL stay at `0.0`; no further trades or funding are processed.

This is intentionally not a full margin engine. It restores bounded-equity semantics without adding leverage, maintenance margin, or partial liquidation scope.

### 1.3 Code changes (file, lines, diff summary)

- `lib/backtest.py:68`: added `liquidated`.
- `lib/backtest.py:69`: added `liquidation_timestamp`.
- `lib/backtest.py:247`: initializes liquidation state.
- `lib/backtest.py:338`: detects first bar-close equity floor breach.
- `lib/backtest.py:344`: records a normal-schema forced close trade when a position exists.
- `lib/backtest.py:415`: returns the new fields.

Existing output fields and the `run_backtest(...)` signature are preserved.

### 1.4 Regression tests and results

New file: `tests/test_backtest_liquidation.py`

Tests:

- `test_normal_path_always_flat`
- `test_buy_and_hold_unchanged_on_benign_window`
- `test_liquidation_on_catastrophic_short`
- `test_liquidation_idempotent_after_trigger`
- `test_drawdown_bounded_under_previously_unbounded_scenario`

Result:

```text
.venv\Scripts\python.exe -m pytest tests/test_backtest.py tests/test_evaluation.py tests/test_backtest_liquidation.py tests/test_evaluation_cost_drag.py -q
23 passed, 4 warnings
```

### 1.5 Post-fix audit evidence (TEST-06 POSTFIX, TEST-01 POSTFIX)

- `research/audits/2026-04-pipeline-audit/TEST-06_drawdown_semantics_POSTFIX.ipynb`
  - Shows WP-5a-style negative-equity drawdown above 100% as the pre-fix semantic.
  - Shows the patched backtester liquidating and bounding DD to 100%.
  - Verdict: PASS.
- `research/audits/2026-04-pipeline-audit/TEST-01_buy_and_hold_POSTFIX.ipynb`
  - Confirms final equity `75787.26692`.
  - Confirms max DD `0.7408575150756737`.
  - Confirms trade count `0`.
  - Confirms `liquidated == False`.
  - Verdict: PASS.

### 1.6 Normal-path preservation confirmation (I-1)

The benign buy-and-hold scenario matches WP-5a TEST-01 exactly:

- Final equity: `75787.26692`
- Max DD: `0.7408575150756737`
- Trade count: `0`
- Liquidation: `False`

---

## Section 2: F-002 Fix -- Gate 5 Pass/Fail for Non-Positive gross_pnl

### 2.1 Problem (from WP-5a F-002)

Gate 5 previously passed mechanically when:

- `gross_pnl < 0`, because the reported cost-drag fraction was negative and therefore `<= 0.50`.
- `gross_pnl == 0`, because NaN was converted to `0.0`, then passed.

### 2.2 Design decision

WP-5b preserves the reported-value convention and changes only the boolean:

- `gross_pnl > 0`: unchanged formula and unchanged `drag <= 0.50` pass condition.
- `gross_pnl == 0`: reported Gate 5 value remains `0.0`; Gate 5 fails.
- `gross_pnl < 0`: reported negative diagnostic fraction is preserved; Gate 5 fails.

### 2.3 Code changes (file, lines, diff summary)

- `lib/evaluation.py:536`: reads `gross_pnl` from the existing `cost_drag(...)` result.
- `lib/evaluation.py:537`: keeps positive-gross behavior unchanged.
- `lib/evaluation.py:540`: keeps zero-gross reported value at `0.0` but fails the gate.
- `lib/evaluation.py:544`: fails negative gross PnL while preserving the negative diagnostic value.

The `check_promotion_gates(...)` signature, output structure, field names, and thresholds are unchanged.

### 2.4 Reported-value convention preservation (I-3)

For `gross_pnl > 0`, the reported value is still:

```python
(fees_paid + slippage_paid + funding_paid) / (realized_pnl + unrealized_pnl)
```

The scale remains a fraction. No silent percent conversion or denominator change was made.

### 2.5 Regression tests and results

New file: `tests/test_evaluation_cost_drag.py`

Tests:

- `test_gate_5_positive_gross_pnl_low_drag`
- `test_gate_5_positive_gross_pnl_high_drag`
- `test_gate_5_positive_gross_pnl_at_threshold`
- `test_gate_5_zero_gross_pnl_fails`
- `test_gate_5_negative_gross_pnl_fails`
- `test_gate_5_reported_value_scale_preserved`

Result: all included in the `23 passed` targeted test run.

### 2.6 Post-fix audit evidence (TEST-07 POSTFIX)

`research/audits/2026-04-pipeline-audit/TEST-07_cost_drag_denominator_POSTFIX.ipynb` confirms:

- Positive gross PnL uses the same reported value and same threshold behavior.
- Zero gross PnL reports `0.0` and now fails.
- Negative gross PnL reports a negative diagnostic value and now fails.
- Reported value scale remains a fraction; threshold remains `0.50`.

Verdict: PASS.

---

## Section 3: Verdict-Preservation Argument (I-4)

### 3.1 Logical argument from WP-5a audit (Gate 1 / Sharpe driven)

Current repo truth has 10 trial-log entries, H-001 through H-010. All 10 have `oos_sharpe < 1.0`:

- H-001: `-0.3897788502290693`
- H-002: `0.07581376350868253`
- H-003: `-0.40644276086066977`
- H-004: `0.746191460507614`
- H-005: `0.3751092454780985`
- H-006: `-0.35122389498871254`
- H-007: `-0.6416904457583815`
- H-008: `-0.15021289072842162`
- H-009: `-0.16384370990793867`
- H-010: `0.46477526210643`

Gate 1 is `OOS Sharpe >= 1.0`. WP-5b does not modify Sharpe calculation, Gate 1 threshold, or Gate 1 pass/fail logic. Therefore every existing trial still fails Gate 1. Because promotion requires all gates to pass, every existing overall verdict remains NO-GO.

### 3.2 Why gate-count identity is NOT required

Gate-count identity is not an invariant. F-002 is expected to flip some Gate 5 mechanical passes to failures when `gross_pnl <= 0`. F-001 may change Gate 3 values by bounding drawdown to 100%. Those changes do not alter the overall verdict for any existing trial because Gate 1 failures are unaffected.

### 3.3 Promotion-semantics dependency

I-4 depends on:

- I-5: Sharpe / Gate 1 untouched.
- Promotion semantics: `overall_pass = all(g.passed for g in gates)`.

Both are confirmed in repo truth.

---

## Section 4: Interpretation Implications

### 4.1 Gate 3 (max DD)

Previously, Gate 3 could operate on drawdown values above 100% because equity could go negative. After WP-5b, the backtester floors equity at zero after liquidation. DD is bounded to `[0, 100]%`.

### 4.2 Gate 5 (cost drag)

Previously, Gate 5 could mechanically pass when `gross_pnl <= 0`. After WP-5b, zero and negative gross PnL fail Gate 5 while preserving the reported diagnostic value convention.

### 4.3 Implications for existing H-001..H-010

All 10 existing hypotheses remain overall NO-GO because all fail Gate 1 and Gate 1 is untouched. Cold Storage status is preserved. Individual Gate 3 or Gate 5 assignments may differ post-fix; this is expected and does not alter any overall NO-GO verdict.

### 4.4 Implications for future hypotheses

Gate 3 and Gate 5 are now trustworthy for future research. No hypothesis re-execution is required by this fix.

---

## Section 5: Out-of-Scope Items (Intentionally Deferred)

- Re-running any existing hypothesis
- Re-computing stored trial_log metrics under the fixed pipeline
- Monte Carlo infrastructure
- Gate threshold changes (D2-006 unchanged)
- Cost parameter changes (fees, slippage unchanged)
- Skills install

---

## Section 6: Verdict

Fix status: COMPLETE

Invariant status:

- I-1 Normal-path preservation:         PASS
- I-2 run_backtest output fields:       PASS
- I-3 evaluation output format + scale: PASS
- I-4 Overall verdicts preserved (arg): PASS
- I-5 Sharpe / Gate 1 untouched:        PASS
- I-6 Signature stability:              PASS

Pipeline is now suitable for further research.
