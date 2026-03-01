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

