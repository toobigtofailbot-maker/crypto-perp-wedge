# Runbook (Ops)

## Start/Stop

* Start:
* Stop:
* Restart:

## API key handling (rules)

* Never commit secrets
* Use .env locally only
* Rotate keys if leaked

## Kill-switch procedure

* When to trigger:
* How to trigger:
* Post-mortem steps:



\## How to run single\_trade with config (required)



1\) Open PowerShell in repo root:

&nbsp;  - `cd C:\\GitHub\\crypto-perp-wedge`

2\) Activate venv:

&nbsp;  - `.\\.venv\\Scripts\\Activate.ps1`

3\) Run single trade runner (module mode):

&nbsp;  - `python -m scripts.backtest\_single\_trade`



Expected:

\- A report JSON is written to `reports/` containing:

&nbsp; - config\_sha256

&nbsp; - dataset\_hashes (klines + funding)

&nbsp; - git\_commit\_id

&nbsp; - run\_timestamp\_utc

&nbsp; - decision\_id


------------

## Data validation gate (required)

Run (from repo root, venv active):
- python scripts/validate_data.py

Expected:
- "VALIDATION PASS"
- exit code = 0
- reports/validation_report.json exists and status=PASS

Fail behavior:
- exit code != 0 => STOP. Fix data/validator before any further backtest steps.


## Phase 2 history fetch

### Overview

Phase 2 requires full BTCUSDT USDT-M perpetual history for research. This section documents how to fetch the canonical datasets.

### OHLCV klines (all timeframes)

Fetch full history for each timeframe:

```bash
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_klines_bulk.py --interval 15m
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_klines_bulk.py --interval 30m
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_klines_bulk.py --interval 1h
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_klines_bulk.py --interval 4h
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_klines_bulk.py --interval 1d
```

Expected runtime: 10-30 minutes per timeframe depending on network speed.

Output: `data/processed/binance_um_perp_BTCUSDT_{interval}_{start}_{end}_{created}.parquet`

### Funding rates (full history)

Fetch full funding rate history:

```bash
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_funding_bulk.py
```

Expected runtime: 5-10 minutes.

Output: `data/processed/binance_um_perp_BTCUSDT_funding_8h_{start}_{end}_{created}.parquet`

### Mark / index / premium index klines (repaired official-source history)

Fetch each stream and timeframe with the corrected three-stage pipeline:

```bash
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_mark_index_premium_bulk.py --stream markPriceKlines --interval 15m
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_mark_index_premium_bulk.py --stream markPriceKlines --interval 30m
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_mark_index_premium_bulk.py --stream markPriceKlines --interval 1h
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_mark_index_premium_bulk.py --stream markPriceKlines --interval 4h
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_mark_index_premium_bulk.py --stream markPriceKlines --interval 1d
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_mark_index_premium_bulk.py --stream indexPriceKlines --interval 15m
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_mark_index_premium_bulk.py --stream indexPriceKlines --interval 30m
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_mark_index_premium_bulk.py --stream indexPriceKlines --interval 1h
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_mark_index_premium_bulk.py --stream indexPriceKlines --interval 4h
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_mark_index_premium_bulk.py --stream indexPriceKlines --interval 1d
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_mark_index_premium_bulk.py --stream premiumIndexKlines --interval 15m
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_mark_index_premium_bulk.py --stream premiumIndexKlines --interval 30m
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_mark_index_premium_bulk.py --stream premiumIndexKlines --interval 1h
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_mark_index_premium_bulk.py --stream premiumIndexKlines --interval 4h
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/fetch_btcusdt_mark_index_premium_bulk.py --stream premiumIndexKlines --interval 1d
```

Pipeline:
- monthly data.binance.vision archives are the base layer
- full historical daily archives fill bars missing from the monthly layer
- targeted Binance REST requests fill bars still missing after the daily overlay
- bars still absent from all three official sources are recorded in `data/irreparable_gaps.json`

Expected runtime: about 10-30 minutes per stream/timeframe depending on network speed.

Output: `data/processed/binance_um_perp_BTCUSDT_{mark_price|index_price|premium_index}_{interval}_{start}_{end}_{created}.parquet`

Each output includes `is_repaired=true` for bars sourced from the daily overlay or REST backfill. Known irreparable official-source gaps are tracked in `data/irreparable_gaps.json` under D2-003A in `docs/decisions.md`. Downstream research must consult the manifest and skip or explicitly handle affected bars; silent interpolation is forbidden.

### Expected row counts (minimum thresholds for ~6 years)

| Timeframe | Minimum rows |
| --------- | ------------ |
| 15m       | 210,000      |
| 30m       | 105,000      |
| 1h        | 55,000       |
| 4h        | 13,750       |
| 1d        | 2,300        |
| Funding   | 6,500        |

### Validation

After fetching, run the validator:

```bash
/c/GitHub/crypto-perp-wedge/.venv/Scripts/python scripts/validate_data.py
```

Check `reports/validation_report.json` for status and any gaps.

### Data location

All Parquet files are stored in `data/processed/` which is gitignored. Files are NOT committed to the repository. Each operator fetches independently.

SHA256 checksums are recorded in `docs/data_catalog.md` for reproducibility verification.

## G4 API smoke test (live UM Futures)

- Script: `python scripts/g4_api_smoke_test.py --env LIVE --symbol BTCUSDT`
- Endpoint: `https://fapi.binance.com` (LIVE only)
- Connector: `binance-futures-connector` via `UMFutures` (no custom signer)
- Credentials: `BINANCE_API_KEY` and `BINANCE_API_SECRET` read at runtime via `os.getenv`
- Flow: `exchange_info` -> compute far-away `LIMIT` (within symbol filters) -> optional `/fapi/v1/order/test` -> place `LIMIT` -> immediate cancel -> post checks (`open_orders_count==0` and `position_amt==0`)
- Report output: `reports/g4_api_smoke_test/g4_api_smoke_test_report.json`
- Local logs only (gitignored): `logs/g4_api_smoke_test/`
- Exit codes: PASS => 0, FAIL => 1
- Safety: places a far-away LIVE `LIMIT` and immediately cancels (minimize fill chance; still a LIVE order).

## Phase-0 Gate G4 â€” Binance USD-M Futures LIVE API Smoke Test

**Purpose:** Validate LIVE connectivity + permissions (USD-M Futures) and confirm "place LIMIT â†’ immediate cancel" leaves zero open orders and zero position.

**Command (Windows / PowerShell):**
cd C:\GitHub\crypto-perp-wedge
.\.venv\Scripts\Activate.ps1
$env:BINANCE_API_KEY="..."
$env:BINANCE_API_SECRET="..."
python scripts\g4_api_smoke_test.py --env LIVE --symbol BTCUSDT
echo $LASTEXITCODE

**PASS criteria (must all be true):**
- Exit code == 0
- Report exists at:
  `reports/g4_api_smoke_test/g4_api_smoke_test_report.json`
- Report fields:
  - status == "PASS"
  - env == "LIVE"
  - base_url == "https://fapi.binance.com"
  - post_state.open_orders_count == 0
  - post_state.position_amt == "0"

**Evidence:**
- Committed JSON report:
  `reports/g4_api_smoke_test/g4_api_smoke_test_report.json`
- Local logs (not committed):
  `logs/g4_api_smoke_test/`

**Deterministic Preconditions (portability):**
- USD-M Futures permission enabled for the API key.
- Sufficient available margin for minNotional constraints (else -2019).
- Account position mode may affect required order params (Hedge Mode may require positionSide).

## P1-E Batch 2 — deterministic bar-close scheduler + freshness gate

Run one deterministic cycle at a specific UTC 1h bar close:

```bash
python -m src.runtime.paper_trader --once-at 2026-01-01T01:00:00Z --config configs/paper_runtime.json
```

Run continuous UTC 1h bar-close loop:

```bash
python -m src.runtime.paper_trader --loop --config configs/paper_runtime.json
```

Expected stale-data behavior:
- Runtime compares configured `latest_bar_time_path` timestamp to the cycle `bar_close_time_utc`.
- If outside `freshness_tolerance_seconds`, cycle is skipped.
- Skip is recorded as `SystemEvent` with `payload.phase="skip"` and `payload.reason="stale_data"`.
- Event log remains append-only JSONL, including start/skip/end events for skipped cycles.
## P1-E Batch 1 — paper trader once-run

Run:
```powershell
.\.venv\Scripts\python.exe -m src.runtime.paper_trader --once --config configs\paper_runtime.json
```

## Phase 1 baseline

Run the frozen Phase 1 closure baseline with:

```powershell
python -m src.runtime.paper_trader --once-at 2026-01-01T01:00:00Z --config configs\paper_runtime.phase1_closed.json
```

## Dispatch-authorization parent bootstrap

Before the first dispatch-authorization/KDAUTH crossing in a fresh clone or checkout where the control-plane roots are absent, create exactly these two empty ordinary directories:

```powershell
New-Item -ItemType Directory -Path research\queue\dispatch_authorizations
New-Item -ItemType Directory -Path research\queue\dispatch_authorization_audit
```

Both directories must pre-exist, resolve beneath the repository root, remain empty before first use, and contain no symlink, junction, reparse point, mount redirect, or equivalent indirection. Do not place `.gitkeep` or any other sentinel in either controlled directory. The protected writer verifies these parents but does not create them.

## Phase 2 research workbench

### Overview

The research workbench (`lib/backtest.py` + `lib/evaluation.py`) consumes the
merged dataset from WP-1a and produces reproducible, statistically-disciplined
backtest results.

### How to import lib.backtest

```python
from lib.backtest import run_backtest, BacktestResult
from lib.evaluation import (
    check_promotion_gates, append_trial, make_trial_entry,
    sharpe, max_drawdown,
)
```

Ensure the repo root is on your Python path (or activate the venv from the
repo root).

### Minimal end-to-end example against merged dataset

```python
import pandas as pd
from pathlib import Path
from lib.backtest import run_backtest
from lib.evaluation import sharpe, check_promotion_gates, make_trial_entry, append_trial

# 1. Load the 1h OHLCV dataset (adjust filename to latest)
ohlcv = pd.read_parquet(
    "data/processed/binance_um_perp_BTCUSDT_1h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet"
)
# Ensure UTC index
if ohlcv.index.tz is None:
    ohlcv.index = ohlcv.index.tz_localize("UTC")

# 2. Load funding rates (use latest file)
funding = pd.read_parquet(
    "data/processed/binance_um_perp_BTCUSDT_funding_8h_2019-09-10_2026-04-12_2026-04-12T1655Z.parquet"
)
if funding.index.tz is None:
    funding.index = funding.index.tz_localize("UTC")

# 3. Define a minimal SMA crossover signal
fast = ohlcv["close"].rolling(5).mean()
slow = ohlcv["close"].rolling(20).mean()
signal = pd.Series(0.0, index=ohlcv.index)
signal[fast > slow] = 1.0
signal[fast <= slow] = -1.0
signal[slow.isna()] = 0.0

# 4. Run the backtester
result = run_backtest(
    signal=signal,
    ohlcv=ohlcv,
    funding=funding,
    fee_bps_taker=4.0,    # 0.04% taker fee
    fee_bps_maker=2.0,    # 0.02% maker fee
    slippage_bps=1.0,     # 0.01% slippage
    initial_equity=10_000.0,
    stream="klines",
    interval="1h",
    # gaps_path defaults to data/irreparable_gaps.json
)

print(f"Final equity:   {result.equity_curve.iloc[-1]:,.2f}")
print(f"Fees paid:      {result.fees_paid:,.2f}")
print(f"Funding paid:   {result.funding_paid:,.2f}")
print(f"Skipped bars:   {result.skipped_bars}")

# 5. Evaluate
oos_returns = result.equity_curve.pct_change().dropna()
oos_sharpe = sharpe(oos_returns, "1h")
print(f"OOS Sharpe:     {oos_sharpe:.4f}")

# 6. Run promotion gates
report = check_promotion_gates(
    result=result,
    trial_count=1,
    params_meta={"n_free_params": 2, "sensitivity_min_ratio": 1.0},
    freq="1h",
)
import json
print(json.dumps(report.to_dict(), indent=2))

# 7. Log the trial
entry = make_trial_entry(
    hypothesis_id="H-001",
    config={"fast": 5, "slow": 20},
    dataset_ids=["binance_um_perp_BTCUSDT_1h"],
    params={"fast": 5, "slow": 20},
    in_sample_sharpe=oos_sharpe,
    oos_sharpe=oos_sharpe,
    max_dd=0.0,  # compute with max_drawdown(result.equity_curve)[0]
    n_obs=len(oos_returns),
    notes="minimal SMA crossover smoke test",
)
append_trial(Path("research/trial_log.jsonl"), entry)
```

### How to interpret a GateReport

`check_promotion_gates()` returns a `GateReport` dataclass.  Call
`.to_dict()` for a JSON-serialisable representation.

```json
{
  "overall_pass": false,
  "summary": {"n_passed": 5, "n_failed": 3, "n_total": 8, ...},
  "gates": [
    {"gate_id": 1, "gate_name": "OOS Sharpe >= 1.0", "passed": false, "value": 0.42, "threshold": 1.0, "note": ""},
    {"gate_id": 2, "gate_name": "DSR > 0.95 (95% CI)", "passed": false, "value": 0.31, "threshold": 0.95, "note": "SR benchmark=1.23"},
    ...
  ]
}
```

A strategy must pass **all 8 gates** to be promoted:

| Gate | Requirement |
|------|-------------|
| 1 | OOS Sharpe >= 1.0 |
| 2 | DSR > 0.95 (95% confidence vs. expected maximum from N trials) |
| 3 | Per-fold max drawdown <= 20% |
| 4 | Parameter sensitivity: min Sharpe ratio >= 70% at ±25% shift |
| 5 | Cost drag <= 50% of gross PnL |
| 6 | No 90-day window > 60% of total PnL |
| 7 | <= 5 free parameters |
| 8 | Walk-forward efficiency > 0.5 |

### Appending to trial_log.jsonl

Every genuine OOS evaluation must be logged:

```python
from pathlib import Path
from lib.evaluation import make_trial_entry, append_trial

entry = make_trial_entry(
    hypothesis_id="H-001",          # must match a registered hypothesis
    config={"fast": 5, "slow": 20}, # full config dict
    dataset_ids=["binance_um_perp_BTCUSDT_1h_2020-01-01_2026-04-11"],
    params={"fast": 5, "slow": 20},
    in_sample_sharpe=1.5,
    oos_sharpe=1.2,
    max_dd=0.08,
    n_obs=5000,
    notes="baseline run",
)
append_trial(Path("research/trial_log.jsonl"), entry)
```

The total number of rows in `trial_log.jsonl` is the `n_trials` input to the
DSR calculation.  Do not inflate this count with test runs or aborted evaluations.

### Running the test suite

```bash
# All tests (baseline + WP-1b)
.venv/Scripts/python.exe -m pytest -q

# WP-1b tests only
.venv/Scripts/python.exe -m pytest tests/test_backtest.py tests/test_evaluation.py -v
```
