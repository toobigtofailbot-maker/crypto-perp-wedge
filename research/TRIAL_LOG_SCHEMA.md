# Trial Log Schema

`research/trial_log.jsonl` stores one JSON object per line (JSONL format).
Each line is a `TrialEntry` produced by `lib/evaluation.append_trial()`.

---

## TrialEntry Fields

| Field              | Type     | Required | Description |
|--------------------|----------|----------|-------------|
| `trial_id`         | string   | yes      | UUID v4. Unique identifier for this trial run. |
| `utc`              | string   | yes      | ISO 8601 UTC timestamp of when the trial was logged (e.g. `"2026-04-13T10:00:00+00:00"`). |
| `hypothesis_id`    | string   | yes      | Reference to the hypothesis file entry (e.g. `"H-001"`). Must match a registered hypothesis in `research/templates/` or a `HYPOTHESIS.md` entry. |
| `config_sha256`    | string   | yes      | SHA-256 (hex, 64 chars) of the strategy configuration dict, serialised with `json.dumps(sort_keys=True)`. Used for reproducibility verification. |
| `dataset_sha256`   | string   | yes      | SHA-256 (hex, 64 chars) of the dataset identifier list, serialised with `json.dumps({"ids": sorted(dataset_ids)})`. Ties the trial to a specific data snapshot. |
| `params`           | object   | yes      | Free parameters used in this trial. Key-value pairs. All values must be JSON-serialisable. Example: `{"fast": 5, "slow": 20}`. |
| `in_sample_sharpe` | number   | yes      | Annualised Sharpe ratio on the in-sample period. |
| `oos_sharpe`       | number   | yes      | Annualised Sharpe ratio on the out-of-sample period. This is the figure evaluated against Gate 1. |
| `max_drawdown`     | number   | yes      | Maximum drawdown as a positive fraction in [0, 1]. E.g. `0.15` = 15% drawdown. |
| `n_obs`            | integer  | yes      | Number of bars in the evaluation period (OOS). Used in DSR calculation. |
| `notes`            | string   | no       | Free-text notes about this trial. Default `""`. |

---

## Example Row

```json
{
  "trial_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "utc": "2026-04-13T10:00:00+00:00",
  "hypothesis_id": "H-001",
  "config_sha256": "abc123...64hexchars",
  "dataset_sha256": "def456...64hexchars",
  "params": {"fast": 5, "slow": 20},
  "in_sample_sharpe": 1.5,
  "oos_sharpe": 1.2,
  "max_drawdown": 0.08,
  "n_obs": 5000,
  "notes": "baseline SMA crossover, 1h BTCUSDT"
}
```

---

## Usage

Append a trial programmatically:

```python
from pathlib import Path
from lib.evaluation import make_trial_entry, append_trial

entry = make_trial_entry(
    hypothesis_id="H-001",
    config={"fast": 5, "slow": 20},
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

---

## Constraints

- Each row must be valid JSON.
- The file is append-only; do not edit existing rows.
- `trial_id` must be unique per row.
- `config_sha256` and `dataset_sha256` must be exactly 64 hex characters (SHA-256).
- `params` must contain only JSON-serialisable values.
- `max_drawdown` is a fraction, not a percentage (0.15, not 15).
- `n_obs` must be an integer >= 1.

---

## Overfitting firewall (D2-004)

The trial log is the primary instrument for computing the Deflated Sharpe Ratio (DSR).
The total number of rows in `trial_log.jsonl` at evaluation time is passed as
`n_trials` to `lib/evaluation.deflated_sharpe_ratio()`.  Appending a trial
implicitly "spends" a multiple-testing budget — do not inflate the trial count
by logging test runs, parameter sweeps that share the same dataset, or aborted runs
unless they reflect a genuine strategy evaluation.
