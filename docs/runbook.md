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