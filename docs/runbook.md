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

## Local-evidence lifecycle

Local presence and durable repo truth are different states. A local file never
silently becomes merged repo truth, authority, or canonical evidence.

| Evidence class | Clean-worktree expectation | Local hydration/creation | Commit and persistence authority | Query/integrity interpretation |
| --- | --- | --- | --- | --- |
| A. Merged tracked repo truth | Present at the checked-out commit. | Restored only through ordinary Git checkout/fetch of the exact commit. | Already committed; modification requires an explicit WP covering the path and semantics. | Absence or byte drift from the checked-out commit is a repo-state failure. |
| B. Intentionally gitignored validation data | May be absent. | May be hydrated only by the named validation profile; exact-source/hash/byte/file-kind rules apply. | Must not be committed unless a later explicit data-persistence package authorizes it. | Absence is an input-availability condition when the named profile requires it; presence is valid only after profile verification. |
| C. Local untracked execution/control-plane evidence | Absent in a clean checkout; may exist in an evidence-bearing worktree. | May be created only by a separately authorized writer/crossing/execution flow, or copied only when an explicit profile permits exact-byte hydration. | Must not be committed without separate exact-content persistence authority and every applicable protected/canonical gate. | Interpret absence/presence against the explicitly named clean or evidence-bearing context; local presence is not merged persistence. |
| D. Scratch/provisional evidence | Normally absent and never required as merged truth. | May be created or hydrated only inside the active package's reversible scratch scope. | Must not be committed or promoted unless a later package explicitly authorizes the exact artifact and crossing. | Advisory/provisional only; absence is normal unless the active validation step requires it. Presence grants no canonical, promotion, execution, or runtime authority. |
| E. Canonical artifacts intended for durable repo persistence | Absent before an authorized crossing; present after the exact artifact is merged. | Do not hydrate a local substitute and call it canonical. Creation/persistence follows the authorized writer or exact-content crossing. | Requires explicit canonical persistence authority, applicable human gate, exact-content proof, and exact-head review. | Validate against exact merged repo truth and the artifact's schema/integrity contract; local pre-merge existence remains only a candidate for persistence. |

Hydration is validation setup, not authority. Checks must report which evidence
class and named validation context they used. They must not collapse a clean
checkout, an evidence-bearing worktree, and merged repo truth into one baseline.
This lifecycle policy does not retroactively authorize committing any current
H-004 local stream, audit, writer-integrity, or scratch evidence.

## Validation profile: H-004 exact local corpus v1

Any worktree that runs H-004/KDAUTH dispatch-authorization or reservation
integrity validation must contain this exact canonical local corpus:

- Canonical 1d dataset:
  - Path: `data/processed/binance_um_perp_BTCUSDT_1d_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`
  - Byte length: `200,961`
  - SHA-256: `c6e2e7ce030db6a710d95e48325fc77b27efbbdd441199b3d7458d4394795802`
  - Source of truth: `research/data_slices/binance_usdtm_btcusdt_1d/binance_usdtm_btcusdt_1d_20200101_20260411.catalog_slice.json` and the KDAUTH dataset binding.
- Canonical funding-events dataset:
  - Path: `data/processed/binance_um_perp_BTCUSDT_funding_8h_2019-09-10_2026-04-12_2026-04-12T1655Z.parquet`
  - Byte length: `126,987`
  - SHA-256: `5f0da7478ccf3514af41dff9958b579cd2f797a2716001b0fa10a11059912798`
  - Source of truth: `research/data_provenance/funding/binance_usdtm_btcusdt_funding_events_20190910t080000z_20260412t160000z_sha256_5f0da7478ccf3514.funding_provenance.json` and the KDAUTH funding binding.

Each path must be a regular non-symlink/non-reparse file and remain gitignored,
untracked, and unstaged. Copy only exact bytes from a verified canonical local
source; never fetch, regenerate, transform, or substitute either file. Missing
local validation inputs are input-availability conditions and must not be
interpreted as authorization-lineage corruption. Any path, byte-length, or
SHA-256 mismatch is a hard stop, not a provisioning convenience.

The profile has two explicit execution-stream contexts:

- `h004-clean`: the exact merged repo checkout plus the verified ignored dataset
  corpus above; the real H-004 execution stream is absent.
- `h004-evidence-bearing`: the exact merged repo checkout plus that corpus and
  the real local untracked execution stream at
  `research/queue/execution_events/RUN-20260804-H004R2A1.execution_events.jsonl`.

In `h004-clean`, `v_integrity_execution_streams` is expected to disclose exactly
the missing stream for dispatch `DSP-20260804-H004R2A1`, run
`RUN-20260804-H004R2A1`, at that path. In `h004-evidence-bearing`, the view may be
clean only when the exact real stream is present and passes its existing
integrity contract. This profile does not decide or authorize stream
persistence, copying, regeneration, rerun, or canonical write.

The locked `STRAT-SPEC-0007` row in
`v_integrity_strategy_spec_legacy_hash_scope_reproducibility` is a known
validation disclosure in both named H-004 contexts. It is not universally
ignorable outside that exact view and context.

### Known-state stop suppression

A locked disclosure or expected environment condition may be recorded in a
named validation profile. An exact match to the named expected state does not
require a new human stop on every run. Any delta in count, identity, content,
path, hash, file kind, tracking state, or semantics requires classification and
the active package's normal stop handling.

Profile entries are evidence and context, not authority. Vague labels such as
`baseline` must not suppress new findings. The comparison baseline must be exact
merged repo truth or the explicitly named validation context, never whichever
local worktree is convenient.

## H-004 canonical execution actor identity

The exact execution-event `actor_id` for the separately authorized H-004
canonical Stage-B invocation is `codex-execution-runner`. This identifies the
automated system performing the execution and must still be passed explicitly
to `run_consumed_dispatch`; the adapter must not supply it as a default.

This execution identity does not replace or reinterpret the KDAUTH
`authorized_by` or lifecycle actor lineage, where Karl remains the authorization
actor. Recording `codex-execution-runner` here creates no execution authority by
itself. A real H-004 invocation still requires its separate exact-run gate.

## Dispatch-authorization parent bootstrap

Before the first dispatch-authorization/KDAUTH crossing or dispatch-record writer call in a fresh clone or checkout where the control-plane roots are absent, create exactly these three empty ordinary directories:

```powershell
New-Item -ItemType Directory -Path research\queue\dispatch_authorizations
New-Item -ItemType Directory -Path research\queue\dispatch_authorization_audit
New-Item -ItemType Directory -Path research\queue\dispatch_records
```

All three directories must pre-exist before the relevant protected writer call, resolve beneath the repository root, remain empty before first use, and contain no symlink, junction, reparse point, mount redirect, or equivalent indirection. Do not place `.gitkeep` or any other sentinel in any controlled directory. The protected writers verify these parents but do not create them. Git does not track empty directories, so every fresh clone or checkout must perform this bootstrap before its first relevant crossing; this prerequisite grants no crossing or execution authority.

## Protected-action authorization readiness

A protected execution or canonical crossing must not be surfaced for
authorization until it is physically ready in the current worktree and requires
zero additional reversible setup after authorization. Run the zero-effect
`tools.canon_intake.execution_readiness` checker for the exact dispatch, run,
stream, actor, executable identities, expected HEAD, and Result Population
identity. `READY` is an environment fact only; it grants no execution,
canonical, retry, recovery, runtime, paper/live, or capital authority.

The checker fails closed and reports machine-readable findings for these twelve
categories:

1. Repository/worktree: ordinary non-reparse root, visible expected/current
   HEAD, and clean tracked/index state when requested.
2. Dispatch: exact path, bytes, hash, run/stream binding, and consumed
   dispatch/KDAUTH state through the existing validators.
3. Execution stream parent: existing ordinary directory beneath the repository,
   opened and identity-rechecked through the writer's descriptor-anchored
   primitive.
4. Append-lock parent: the exact production lock root opens through that same
   primitive and has no target-run stale lock.
5. Execution-writer integrity parent: the production audit parent opens through
   that same primitive and has no target-run visibility/integrity residue.
6. First-run stream state: the target is absent, retained history has no target
   version, and stream integrity validation reports the missing pre-run state.
7. Scratch target: the existing production scratch preflight accepts the exact
   dispatch-bound target without creating it.
8. Local data: dataset and funding paths have exact bytes/hashes, are ordinary,
   and remain gitignored, untracked, and unstaged.
9. Leased inputs: the adapter's existing preparation path acquires all eleven
   exact read-only inputs and releases every lease without invoking the runner.
10. Executable and actor identities: runner, adapter, scratch persistence,
    execution-event writer, and explicit actor match the reviewed request.
11. Runtime and prior-effect absence: required production imports are already
    available without a fetch; no stream, runner-start evidence, scratch output,
    target Result Population, stale lock, or writer residue exists.
12. Fixture-to-production parity: every fixture setup action is classified and
    every real-worktree prerequisite is mechanically checked or explicitly
    bootstrapped before authorization.

Current fixture-to-production parity is:

| Fixture setup action | Classification | Durable coverage |
| --- | --- | --- |
| `stream_path.parent.mkdir(parents=True, exist_ok=True)` | REQUIRED IN REAL WORKTREE | Readiness checks the production execution-event parent with the writer's anchored-directory primitive. |
| Ensure `research/canonical_crossing_audit` exists | REQUIRED IN REAL WORKTREE | Readiness checks the production integrity parent with the writer's anchored-directory primitive. |
| Copy the execution-event schema into a synthetic repository | TEST-ONLY | A real checkout receives the committed schema; dispatch/stream validation proves availability. |
| Provision synthetic manifest, KDAUTH, dispatch, bound artifacts, data, and Git history | TEST-ONLY | Real requests use their exact committed dispatch bindings and separately controlled local canonical data. |

Before the first execution-event writer use in a fresh clone or worktree, create
the exact controlled empty execution-event parent only after readiness reports
it as a safe bootstrap candidate. For the current writer that parent is:

```powershell
New-Item -ItemType Directory -Path research\queue\execution_events
```

The parent must be an empty ordinary directory beneath the repository root, and
its existing parent must pass descriptor-anchored/no-reparse validation. It must
contain no symlink, junction, reparse point, mount redirect, or other indirection.
The production writer verifies but does not create this directory. Git does not
track empty directories, so every fresh clone or worktree must run readiness and
perform any approved empty-directory bootstrap before authorization. Do not add
`.gitkeep` or another sentinel to a controlled empty directory unless a future
explicit architecture decision changes this rule. Bootstrap is reversible
non-authority setup and grants no execution or canonical authority; the checker
reports candidates but never creates them.

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
