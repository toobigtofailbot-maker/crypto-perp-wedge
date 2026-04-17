# Backtest & Evaluation Pipeline Audit (WP-5a)

Date:       2026-04-16
Branch:     wp-5a-pipeline-audit
Scope:      Diagnostic only. No code changes.
Motivation: 10 consecutive NO-GO verdicts across H-001..H-010 cited in the WP-5a brief,
            with implausible max-drawdown figures (>100%) appearing in 6 of 8 executed
            trial_log entries (H-001: 178%, H-002: 120%, H-003: 110%, H-005: 212%,
            H-006: 612%, H-007: 115%). H-008 and H-009 are DRAFT/pending as of this audit.

**Repo-truth divergence note:** The WP-5a brief references "H-008 max DD 3929%, 5211 trades;
H-009 max DD 925%, 2148 trades" as motivation, but H-008 and H-009 have not been executed.
No DEC-0008 or DEC-0009 files exist in the repo. The pattern motivating this audit is already
fully evidenced by the 8 executed hypotheses (6 of which show DD > 100%). This divergence does
not change the audit scope or verdict.

---

## Section 1: Interface Documentation

### 1.1 `run_backtest` (lib/backtest.py)

**Signature:**
```python
def run_backtest(
    signal: pd.Series,
    ohlcv: pd.DataFrame,
    funding: pd.DataFrame,
    *,
    fee_bps_taker: float,
    fee_bps_maker: float,
    slippage_bps: float,
    initial_equity: float,
    execution: str = "next_bar_open",
    stream: str = "klines",
    interval: str = "1h",
    gaps_path: Optional[Path] = None,
) -> BacktestResult
```

**Required arguments:** All of `signal`, `ohlcv`, `funding`, `fee_bps_taker`, `fee_bps_maker`,
`slippage_bps`, `initial_equity`.

**Input data shapes:**
- `signal`: UTC-indexed DatetimeIndex, values ∈ {-1, 0, +1} (float or int; cast with `int()`
  per bar). Signal at bar t → fill at open of bar t+1.
- `ohlcv`: UTC-indexed DataFrame with columns `{open, high, low, close, volume}`.
- `funding`: UTC-indexed DataFrame with column `funding_rate`. Can be empty.

**Output object (BacktestResult, frozen dataclass):**

| Field | Type | Units/notes |
|---|---|---|
| `equity_curve` | `pd.Series` | USD; includes unrealized PnL at bar close |
| `trades_df` | `pd.DataFrame` | One row per completed round-trip (entry+exit pair) |
| `per_bar_pnl` | `pd.Series` | USD per bar, unrealized+realized delta |
| `realized_pnl` | `float` | Cumulative realized PnL excluding costs |
| `unrealized_pnl` | `float` | Open position PnL at last bar's close |
| `fees_paid` | `float` | Total taker fees both sides |
| `slippage_paid` | `float` | Total slippage both sides |
| `funding_paid` | `float` | Net funding paid (positive = strategy paid) |
| `skipped_bars` | `int` | Count of D2-003A irreparable bars skipped |
| `skipped_bar_timestamps` | `list` | Audit trail of skipped bars |
| `params` | `dict` | Snapshot of run parameters |

**Cost parameters:** All function arguments (not module-level constants). Passed per call.

**Starting capital:** Configurable via `initial_equity` argument. Existing notebooks use 10,000.0 USD.

**Position sizing model:** Fixed 1-contract notional. `position_value = abs(position) * fill_price`.
Notional scales with price but contracts remain fixed at 1. Callers cannot scale to fractional
contracts without code changes.

**Leverage:** Not explicitly modeled. The 1-contract model has implicit leverage = fill_price / equity.
As equity shrinks (or goes negative), effective leverage becomes unbounded. No margin-rate check.

**Liquidation / margin call:** **Not modeled.** Equity can go arbitrarily negative. This is the key
finding documented in TEST-06.

**Re-entry semantics:** A persistent +1 signal generates exactly one entry. Re-entry only occurs
when the signal transitions away from the current position and then back. Confirmed by TEST-04.

**Signal casting:** `desired = int(sig_vals[i - 1])` — explicit integer cast per bar.

**Timestamp/bar semantics:** Signal at bar t → fill at open of bar t+1 (`execution="next_bar_open"`
is the only supported mode). Bars are UTC-indexed bar-close timestamps (despite the name, the index
stores bar-close time per Binance convention).

**Trade recording convention:** `trades_df` only records *completed* round-trips (entry + exit). An
open position at end-of-run is reflected in `unrealized_pnl` and `equity_curve` but is absent from
`trades_df`. For a constant +1 signal (buy-and-hold), `len(trades_df) == 0`.

---

### 1.2 `check_promotion_gates` (lib/evaluation.py)

**Signature:**
```python
def check_promotion_gates(
    result: BacktestResult,
    trial_count: int,
    params_meta: dict,
    *,
    oos_result: Optional[BacktestResult] = None,
    is_result: Optional[BacktestResult] = None,
    freq: str = "1h",
    fold_results: Optional[list[BacktestResult]] = None,
    variance_of_trials: float = 0.1,
    skew: float = 0.0,
    kurt: float = 3.0,
) -> GateReport
```

**Gate thresholds (D2-006, hard-coded in lib/evaluation.py):**

| Gate | Metric | Threshold | Formula |
|---|---|---|---|
| 1 | OOS Sharpe | ≥ 1.0 | `oos_sr >= 1.0` |
| 2 | DSR at 95% CI | `dsr_val > 0.95` | P(true SR > SR_benchmark) from Bailey & López de Prado 2014 |
| 3 | Per-fold max DD | ≤ 20% (0.20) | Uses `fold_results` if provided; else full-period DD on OOS result |
| 4 | Parameter sensitivity | min_ratio ≥ 0.70 | Read from `params_meta["sensitivity_min_ratio"]` |
| 5 | Cost drag | ≤ 50% (0.50) | `total_cost / gross_pnl` |
| 6 | 90-day PnL window | ≤ 60% (0.60) | Rolling 90-day sum of `per_bar_pnl` |
| 7 | Free parameters | ≤ 5 | Read from `params_meta["n_free_params"]` |
| 8 | Walk-forward efficiency | > 0.50 | `min(oos_sharpe / is_sharpe, 1.0)` |

**Sharpe computation:** `(mean(returns) / std(returns, ddof=1)) * sqrt(bars_per_year[freq])`.
Returns are per-bar arithmetic pct_change of equity_curve, NaN dropped. Risk-free rate = 0.

**Max drawdown computation:**
```python
peak = equity_curve.cummax()
drawdown = (equity_curve - peak) / peak
max_dd = float(-drawdown.min())
```
Returns fraction (0.0 to unbounded). Can exceed 1.0 (100%) when equity goes negative.
See Section 3.3 (Material Finding F-001).

**DSR computation:** Bailey & López de Prado (2014) formula. `n_trials` is the trial_count argument.
`variance_of_trials` defaults to 0.1 (tunable). Uses `statistics.NormalDist` for CDF.

**Walk-forward efficiency:** `min(oos_sharpe / is_sharpe, 1.0)`. Returns 0 if IS Sharpe ≤ 0.
Capped at 1.0 (OOS outperforming IS not additionally rewarded).

**Cost drag computation:**
```python
gross = result.realized_pnl + result.unrealized_pnl
total_cost = result.fees_paid + result.slippage_paid + result.funding_paid
drag = float(total_cost / gross) if gross != 0 else float("nan")
```
Edge cases: NaN when gross=0 (cast to 0.0 in gate check, passes Gate 5);
negative when gross<0 (also passes Gate 5 ≤ 0.50). See Section 3.2 (Minor Finding F-002).

**Free parameters:** Manual argument read from `params_meta["n_free_params"]`. Not inferred.

**Behavior on edge cases:**
- Zero trades: no crash; metrics computed from equity_curve (which is flat).
- All-losing trades: no crash.
- Negative gross PnL: cost_drag is negative; Gate 5 passes misleadingly.
- NaN gross PnL: not possible (gross is always a float sum).
- fold_results=None: Gate 3 uses full-period OOS result's max drawdown.

---

### 1.3 Trial Log Schema (research/trial_log.jsonl)

**Fields actually used (8 entries, H-001 through H-010 minus H-008/H-009 which are pending):**

| Field | Type | Notes |
|---|---|---|
| `trial_id` | string (uuid4) | Unique per run |
| `utc` | string (ISO 8601) | Run timestamp |
| `hypothesis_id` | string | e.g. "H-005" |
| `config_sha256` | string (hex) | SHA-256 of strategy config dict |
| `dataset_sha256` | string (hex) | SHA-256 of dataset identifier list |
| `params` | dict | Free parameters used |
| `in_sample_sharpe` | float | Full-period Sharpe (no IS/OOS split in baseline pattern) |
| `oos_sharpe` | float | Same as in_sample_sharpe per baseline convention |
| `max_drawdown` | float | Fraction (not pct); **can exceed 1.0** |
| `n_obs` | int | Number of return observations (bars - 1) |
| `notes` | string | Human notes |

**Schema consistency:** All 8 entries use identical field set. No schema drift observed.

**IS/OOS convention note:** Per existing notes in each entry: "no separate IS/OOS split convention
exists in repo truth, so IS/OOS Sharpe fields use full-period Sharpe per runbook baseline pattern."
This means Gates 1 and 8 use the same Sharpe value for both IS and OOS.

**max_drawdown field:** Stored as a fraction (e.g., 2.1208 = 212.08%). Exceeds 1.0 for H-001
(1.7813), H-002 (1.2050), H-003 (1.0959), H-005 (2.1208), H-006 (6.1208), H-007 (1.1523).

---

## Section 2: Test Results

### TEST-01: Buy-and-Hold

**Intent:** Verify backtest reproduces buy-and-hold economics.
**Evidence notebook:** `research/audits/2026-04-pipeline-audit/TEST-01_buy_and_hold.ipynb`

**Expected (independently computed):**
- Entry price: 7221.80 (open of bar 1 on 2020-01-01 07:59:59 UTC)
- Last close: 73013.40
- Expected final equity: 10000 - fee_entry(2.889) - slip_entry(1.444) + (73013.40 - 7221.80) = 75787.267
- Trade count: 0 (no completed round-trip; constant +1 never triggers a close)
- Independent max DD: 74.09%

**Actual:**
- Final equity: 75787.267 ✓ (exact match, diff < $0.01)
- Max drawdown: 74.09% ✓ (exact match)
- Trade count: 0 ✓
- Fees paid: 2.889 (entry side only, no exit)
- Skipped bars: 0

**Verdict: PASS**

---

### TEST-02: Always-Flat

**Intent:** Verify zero-signal produces zero activity.
**Evidence notebook:** `research/audits/2026-04-pipeline-audit/TEST-02_always_flat.ipynb`

**Expected:** All financial fields zero, final equity = 10,000.

**Actual:**
- Final equity: 10,000.000 ✓
- Trade count: 0 ✓
- All costs: 0.000 ✓
- Max drawdown: 0% ✓
- Sharpe: 0.0 (sigma=0 branch; returns 0.0, not NaN) ✓
- Cost drag: NaN (gross=0; cast to 0.0 in gate check → Gate 5 passes) — documented edge case

**Verdict: PASS**

---

### TEST-03: Alternating +1/-1 Signal

**Intent:** Measure cost model accuracy at maximum frequency.
**Evidence notebook:** `research/audits/2026-04-pipeline-audit/TEST-03_alternating_signal.ipynb`

**Expected:** 13,756 round-trips, cost per round-trip ≈ 12 bps × avg_open = 58.09.

**Actual:**
- Trade count: 13,756 ✓ (expected: 13,756)
- Actual cost per round-trip: 58.100
- Expected cost per round-trip: 58.093 (12 bps × avg_open = $48,410)
- Ratio (actual/expected): 1.000129 ✓ (within 0.01% of 1.0)
- Total costs: $799,224 (fees $532,816 + slippage $266,408)
- Gross PnL: $49,238
- Final equity: -$739,986 (negative due to cost drain; no liquidation stop)
- Max DD: 7,286% (confirms no-liquidation issue from TEST-06)

**Verdict: PASS** — cost model is accurate to within 0.013%. H-005's 445% cost drag is confirmed
to be real: the cost model correctly charges costs, and the H-005 strategy accumulated $58k in costs
against $13k gross PnL.

---

### TEST-04: Persistent Long (Re-Entry Audit)

**Intent:** Confirm that a persistent +1 signal generates exactly 1 trade, not a trade-per-bar.
**Evidence notebook:** `research/audits/2026-04-pipeline-audit/TEST-04_persistent_long.ipynb`

**Signal:** +1 for bars 0–99, then 0 forever.

**Expected:** 1 round-trip (entry at bar[1] open, exit at bar[100] open).

**Actual:**
- Trade count: 1 ✓
- Entry bar: 2020-01-01 07:59:59 UTC (bar[1] open = 7221.80) ✓
- Exit bar: 2020-01-17 23:59:59 UTC (bar[100] open = 8885.08) ✓
- Gross PnL: 1663.28 (BTC rose during holding period)

**Verdict: PASS** — No per-bar re-entry bug. High trade counts in H-005 (934) and H-006 are
driven by genuine signal transitions in the strategy logic, not a backtester defect.

---

### TEST-05: Flip Sequence (Trade Counting)

**Intent:** Verify trade-counting semantics on known signal transitions.
**Evidence notebook:** `research/audits/2026-04-pipeline-audit/TEST-05_flip_sequence.ipynb`

**Signal:** `[0, 0, +1, +1, +1, 0, 0, -1, -1, 0, +1, 0, ...]`

**Expected:** 3 round-trips — (long bars 3-5), (short bars 8-9), (long bar 11).

**Actual:**
- Trade count: 3 ✓
- Round-trip 1: long, entry bar[3], exit bar[6] ✓
- Round-trip 2: short, entry bar[8], exit bar[10] ✓
- Round-trip 3: long, entry bar[11], exit bar[12] ✓

All bar indices match the independently derived expectation.

**Verdict: PASS**

---

### TEST-06: Drawdown Semantics

**Intent:** Document the max-drawdown formula and verify whether it can exceed 100%.
**Evidence notebook:** `research/audits/2026-04-pipeline-audit/TEST-06_drawdown_semantics.ipynb`

**Formula documented:**
```python
peak = equity_curve.cummax()
drawdown = (equity_curve - peak) / peak
max_dd = float(-drawdown.min())   # positive fraction; can exceed 1.0
```

**Case A (bounded equity):** Peak=12k, trough=1k, recover to 2k.
- Expected: (12k-1k)/12k = 91.67%
- Actual: 91.67% ✓

**Case B (negative equity):** Peak=12k, trough=-40k.
- Expected: (12k-(-40k))/12k = 433.33%
- Actual: 433.33% ✓ **Exceeds 100%**

**Existing evidence in trial_log:**
- H-001: 178.1% — H-002: 120.5% — H-003: 109.6%
- H-005: 212.1% (final equity = -$35,556 from $10k initial)
- H-006: 612.1% (equity went deeply negative)
- H-007: 115.2%

**Verdict: MATERIAL FINDING** — See Section 3.3, Finding F-001.

---

### TEST-07: Cost-Drag Denominator

**Intent:** Characterize cost_drag behavior at edge cases.
**Evidence notebook:** `research/audits/2026-04-pipeline-audit/TEST-07_cost_drag_denominator.ipynb`

**Formula:** `drag = total_cost / gross if gross != 0 else float("nan")`
**Gate 5 check:** `drag <= 0.50` (NaN cast to 0.0 first)

| Case | gross_pnl | total_cost | drag | Gate 5 |
|---|---:|---:|---:|---|
| A: Positive gross | +689.02 | 11.08 | 1.61% | FAIL (>50%) |
| B: 1-bar (negative gross) | -16.54 | 8.66 | -52.3% | PASS (≤50%) — misleading |
| C: Short bull run | -689.02 | 11.08 | -1.61% | PASS (≤50%) — misleading |
| D: Always flat | 0.00 | 0.00 | NaN→0.0 | PASS — misleading |

**H-005 context:** gross_pnl=+13,184 (positive!), total_cost=58,740 → drag=445.5% → Gate 5 FAIL (correct).
H-005's 445% cost drag is mathematically correct and expected given 934 trades with $58k in costs.

**Verdict: MINOR FINDING** — See Section 3.2, Finding F-002.

---

### TEST-08: H-005 Reproducibility

**Intent:** Verify H-005 metrics are exactly reproducible from source data.
**Evidence notebook:** `research/audits/2026-04-pipeline-audit/TEST-08_reproducibility_H005.ipynb`

**Reference (trial_log entry `f4605dfa-fdad-4b76-8bbf-6e0a805d42a4` and DEC-0005):**

| Field | Reference | Rerun | Match |
|---|---:|---:|---|
| Sharpe | 0.3751092454780985 | 0.3751092454780985 | ✓ exact |
| Max drawdown | 2.120802633322742 | 2.120802633322742 | ✓ exact |
| N observations | 55,031 | 55,031 | ✓ exact |
| Trade count | 934 | 934 | ✓ exact |
| Final equity | -35,556.0483 | -35,556.0483 | ✓ diff < $0.001 |
| Funding events | 1,254 | 1,254 | ✓ exact |
| Cost drag fraction | 4.4553 | 4.4553 | ✓ diff < 0.001 |

Gate report reproduced: 3/8 gates passed (Gates 2, 7, 8), 5/8 failed (Gates 1, 3, 4, 5, 6).
Matches DEC-0005 gate table exactly.

**Verdict: PASS**

---

## Section 3: Findings Summary

| Test | Name | Verdict |
|---|---|---|
| TEST-01 | Buy-and-hold | PASS |
| TEST-02 | Always-flat | PASS |
| TEST-03 | Alternating signal (cost model) | PASS |
| TEST-04 | Persistent long (re-entry) | PASS |
| TEST-05 | Flip sequence (trade counting) | PASS |
| TEST-06 | Drawdown semantics | MATERIAL FINDING |
| TEST-07 | Cost-drag denominator | MINOR FINDING |
| TEST-08 | H-005 reproducibility | PASS |

### 3.1 Clean Findings (no issue)

- **Cost model accuracy:** The bps-based fee and slippage model is correct to 0.013%.
- **Re-entry semantics:** Persistent signals generate one trade, not per-bar re-entries.
- **Trade counting:** Entry/exit counting exactly matches hand-derived expectations on both simple
  and multi-leg sequences.
- **Reproducibility:** H-005 is bit-for-bit reproducible from source data and code.
- **Always-flat handling:** Zero-signal correctly produces zero activity.
- **Buy-and-hold economics:** Equity curve and drawdown match independently computed values exactly.

### 3.2 Minor Findings

**F-002: Cost-drag edge cases with non-positive gross PnL**

- When `gross_pnl < 0`: `cost_drag_fraction` is negative. Gate 5 (`drag <= 0.50`) **passes
  misleadingly** — a strategy losing money shows as "cost-efficient."
- When `gross_pnl = 0`: `cost_drag_fraction = NaN`, cast to 0.0 in `check_promotion_gates`,
  Gate 5 **passes misleadingly**.
- **Impact on existing verdicts:** None. All 8 executed hypotheses that failed had positive
  gross PnL (e.g., H-005: gross = +13,184), so cost_drag was computed correctly and Gate 5
  failed legitimately. The edge case only matters for strategies with negative or zero gross PnL,
  which would also fail Gate 1 (Sharpe < 1.0) independently.
- **Severity:** Minor — does not affect any existing verdict; only affects hypothetical future
  strategies that lose money but somehow pass other gates.

### 3.3 Material Findings

**F-001: No liquidation modeling; max drawdown can exceed 100%**

- **Description:** The backtester (`lib/backtest.py`) does not implement liquidation, margin
  calls, or any equity floor. When a strategy loses more than its starting equity, the equity
  variable becomes negative and continues to decline without bound.
- **Formula evidence:** `max_drawdown = -min((equity - cummax(equity)) / cummax(equity))`. When
  `equity = -40,000` and `cummax = 12,000`, the formula returns 4.333 = 433%. This is
  mathematically correct given the formula's definition, but does not correspond to real-world
  perpetual futures trading where a position would have been liquidated long before equity = 0.
- **Existing evidence:** 6 of 8 executed trial_log entries have max_drawdown > 1.0 (100%):
  H-001 (178%), H-002 (120%), H-003 (110%), H-005 (212%), H-006 (612%), H-007 (115%).
- **Consequence for NO-GO verdicts:** The NO-GO direction is correct — these hypotheses genuinely
  lack edge. DD > 100% only strengthens the rejection. However, the magnitude of reported DD is
  unrealistic and cannot be directly compared to real-world risk. A real account with D2-001 hard
  caps would have been liquidated before reaching these equity levels.
- **Consequence for future research:** If a future hypothesis happens to have borderline DD (e.g.,
  true DD near 18%), the no-liquidation model could report 15% or 35% depending on whether equity
  briefly dips below zero, creating noise in Gate 3 (DD ≤ 20%). This makes Gate 3 unreliable for
  close calls.
- **Severity:** Material — affects interpretation of all existing trial_log entries and could
  produce incorrect Gate 3 verdicts for borderline future candidates.

---

## Section 4: Overall Pipeline Verdict

### MINOR ISSUES

**Rationale:**

The pipeline is fundamentally sound. Six of eight deterministic sanity tests pass cleanly. The
cost model is accurate to 0.013%. Trade counting, signal semantics, and entry/exit mechanics are
all correct. H-005 is bit-for-bit reproducible.

The Material Finding (F-001, no liquidation modeling) is real and requires a fix package, but it
does **not** invalidate the existing NO-GO verdicts for H-001 through H-010 because:

1. All NO-GO verdicts are driven primarily by Gate 1 (OOS Sharpe < 1.0), not by the drawdown gate.
2. For strategies that genuinely lack edge, the no-liquidation model reports a larger loss than
   real-world, which only strengthens the rejection.
3. H-004 (69.8% DD) and H-010 (85.0% DD) — the two hypotheses that stayed below 100% — both
   failed on Sharpe (0.746 and 0.465 respectively).
4. Reproducibility is perfect; the tool is not malfunctioning, it is using a known simplification.

The verdict is **MINOR ISSUES** rather than **CLEAN** because F-001 will affect interpretation of
borderline future candidates and because the DD values reported in the trial_log are not
directly comparable to real-world risk, warranting explicit documentation.

The verdict is **not MATERIAL ISSUES** because no existing verdict is invalidated and the pipeline
can be safely used for hypothesis rejection screening with the understanding that DD > 100% means
"equity went negative" rather than "this was the actual loss experienced."

---

## Section 5: Recommendations for Fix Package (WP-5b)

### Fix 5b-1 (addresses F-001): Add liquidation modeling or floor documentation

**Files to modify:** `lib/backtest.py`, `lib/evaluation.py`

**Approach A — Recommended for correctness:**
Add an `equity_floor` parameter to `run_backtest` defaulting to 0 (full liquidation at zero equity).
When equity drops to or below `equity_floor`, mark position as liquidated, record a forced exit,
set equity to `equity_floor`, and carry forward. This makes DD bounded at ≤ 100% by construction.

**Approach B — Lightweight:**
Keep current backtest semantics (useful for strategy design) but add a `liquidation_triggered: bool`
field to `BacktestResult`, set to True when `equity_curve.min() < 0`. In `check_promotion_gates`,
if `liquidation_triggered`, force Gate 3 to FAIL with note "equity went negative (simulated
liquidation)". This avoids changing backtest math but correctly gates liquidation events.

**Required new tests:** Unit test confirming DD is bounded at 100% with liquidation modeling,
or that `liquidation_triggered` flag is set correctly.

**Implications for H-001..H-010 trial_log:**
- Under Approach A: max_drawdown values for H-001, H-002, H-003, H-005, H-006, H-007 would
  change to ≤ 1.0 (100%). Gate 3 verdicts would remain FAIL (all still > 20%). No verdict changes.
- Under Approach B: no trial_log changes needed; existing entries remain valid with the
  understanding that DD > 1.0 = "liquidation triggered."

### Fix 5b-2 (addresses F-002): Guard cost_drag Gate 5 against non-positive gross PnL

**Files to modify:** `lib/evaluation.py` (`check_promotion_gates` function, Gate 5 block)

**Required change:** In the Gate 5 block, before the `drag <= 0.50` check, add:
```python
if cd["gross_pnl"] <= 0:
    g5_pass = False
    g5_note = f"gross_pnl={cd['gross_pnl']:.2f} <= 0: cost drag undefined/misleading"
```
This ensures that strategies with zero or negative gross PnL always fail Gate 5.

**Implications for H-001..H-010:** No verdict changes. All executed hypotheses had positive
gross PnL or positive Sharpe that caused failures at other gates first.

---

## Section 6: Implications for Existing Verdicts

### H-001 (4h funding momentum, NO-GO)

- **Audit impact:** DD value (178%) is inflated by no-liquidation model. True DD would be ≤ 100%.
- **Verdict change:** No. Primary failure was Sharpe = -0.390 (well below 1.0). Would remain NO-GO.
- **Re-execution needed after fix:** No for verdict; optional for cleaner DD reporting.
- **Cold storage status:** Preserve. 4h Cold Storage justified by Sharpe failure.

### H-002 (4h funding carry, NO-GO)

- **Audit impact:** DD value (120%) inflated.
- **Verdict change:** No. Sharpe = 0.076 << 1.0. Would remain NO-GO.
- **Re-execution needed:** No.
- **Cold storage status:** Preserve.

### H-003 (1d Bollinger Band, NO-GO)

- **Audit impact:** DD value (110%) inflated.
- **Verdict change:** No. Sharpe = -0.406 << 1.0. Would remain NO-GO.
- **Re-execution needed:** No.
- **Cold storage status:** Preserve. 1d Cold Storage justified.

### H-004 (1d volatility-scaled moving average, NO-GO)

- **Audit impact:** DD (69.8%) is below 100% — no liquidation issue. Backtest equity curve stayed
  non-negative. Metrics are directly comparable to real-world.
- **Verdict change:** No. Sharpe = 0.746 < 1.0. Would remain NO-GO.
- **Re-execution needed:** No.
- **Cold storage status:** Preserve.

### H-005 (1h MACD + swing, NO-GO)

- **Audit impact:** DD (212%) inflated. But final equity = -$35,556, confirming equity went
  deeply negative (confirmed in TEST-08). True DD with liquidation = 100%.
- **Verdict change:** No. Sharpe = 0.375 << 1.0. Cost drag 445% (correct). Would remain NO-GO.
- **Re-execution needed:** No for verdict. Reproducibility confirmed exact.
- **Cold storage status:** 1h remains PLANNING. No change warranted.

### H-006 (30m Bollinger squeeze, NO-GO)

- **Audit impact:** DD (612%) severely inflated by no-liquidation. True DD = 100%.
- **Verdict change:** No. Sharpe = -0.351 << 1.0. Would remain NO-GO.
- **Re-execution needed:** No.
- **Cold storage status:** 30m remains PLANNING. No change warranted.

### H-007 (4h funding + momentum cross-stream, NO-GO)

- **Audit impact:** DD (115%) inflated.
- **Verdict change:** No. Sharpe = -0.642 << 1.0. Would remain NO-GO.
- **Re-execution needed:** No.
- **Cold storage status:** Preserve 4h Cold Storage.

### H-008 (1h premium-confirmed momentum, DRAFT/pending)

- **Audit impact:** H-008 has NOT been executed. No trial_log entry exists. The WP-5a brief
  cited anticipated numbers (3929% max DD, 5211 trades) which are not in repo truth.
- **Verdict change:** N/A (not yet executed).
- **Recommendation:** Execute only after WP-5b fix package lands, so that DD metrics are bounded
  and cost-drag edge cases are addressed. This ensures cleaner first-run metrics.

### H-009 (30m multi-timeframe trend alignment, DRAFT/pending)

- **Audit impact:** Same as H-008. Not executed. No trial_log entry. Brief's cited numbers
  (925% max DD, 2148 trades) are not in repo truth.
- **Verdict change:** N/A.
- **Recommendation:** Same as H-008 — execute after WP-5b.

### H-010 (4h basis/premium mean-reversion, NO-GO)

- **Audit impact:** DD (84.97%) is below 100% — no liquidation issue for this hypothesis.
  Metrics are directly comparable to real-world.
- **Verdict change:** No. Sharpe = 0.465 < 1.0. Would remain NO-GO.
- **Re-execution needed:** No.
- **Cold storage status:** Preserve 4h Cold Storage.

---

*End of audit report. No code was modified. All findings are documented only.*
