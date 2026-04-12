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
