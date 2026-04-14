# SKILL: run-evaluation

**Purpose:** Run the Auditor workflow for a candidate strategy using
`lib.backtest` and `lib.evaluation`, then produce a GateReport summary against
the D2-006 promotion gates.

**When to use:** Use this skill after a hypothesis has been pre-registered and
a candidate signal function exists in an allowed strategy module.

---

## Inputs

- Candidate hypothesis directory under `research/hypotheses/<id>/`
- Candidate signal function from the approved strategy module
- Merged dataset for BTCUSDT USDT-M perpetual research
- Current `research/trial_log.jsonl`
- Strategy configuration and parameter metadata

---

## Workflow

### Step 1 - Verify pre-registration

Read the hypothesis before running anything. Confirm it has economic rationale,
primary timeframe, optional confirmation timeframes, success criteria, kill
criteria, free parameters, and expected trial count.

If the pre-registration is missing or ambiguous, stop and escalate.

### Step 2 - Load the candidate signal function

Load the signal function read-only from the candidate strategy module. Do not
modify strategy code during evaluation.

### Step 3 - Load the merged dataset

Load the OHLCV and funding inputs for the hypothesis timeframe. Preserve the
existing D2-003A irreparable-gap policy. Silent interpolation over irreparable
gaps is forbidden.

### Step 4 - Run the backtest

Call `lib.backtest.run_backtest` with the candidate signal, OHLCV frame,
funding frame, configured fee and slippage assumptions, and the
pre-registered primary timeframe as `interval`.

Record `BacktestResult.skipped_bars` and `BacktestResult.skipped_bar_timestamps`
in the evaluation artifact so D2-003A skip-count is auditable.

### Step 5 - Determine trial count

Read the current number of rows in `research/trial_log.jsonl` before appending
the new trial. Use that value as the `trial_count` input for
`lib.evaluation.check_promotion_gates`.

### Step 6 - Run the gate suite

Call `lib.evaluation.check_promotion_gates` with the `BacktestResult`, current
trial count, parameter metadata, and any in-sample, out-of-sample, or fold
results required by the evaluation plan.

The GateReport must include all eight gates with finite numeric `value` fields.

### Step 7 - Append the trial

Create a `TrialEntry` with `lib.evaluation.make_trial_entry`, then append it
with `lib.evaluation.append_trial(Path("research/trial_log.jsonl"), entry)`.
The trial log is append-only. Never edit existing rows.

### Step 8 - Write the evaluation summary

Write the Auditor output under `research/evaluations/`. Include:

- Hypothesis ID
- Dataset identifiers
- Strategy config hash inputs
- Trial count before append
- Trial ID appended
- D2-003A skipped bar count
- GateReport summary and all eight gate values
- Auditor verdict as PASS or FAIL against gates only
- Note that promotion remains a human decision

---

## Guardrails

- Do not override D2-006 gate thresholds.
- Do not approve your own evaluation.
- Do not modify `lib/evaluation.py`, `lib/backtest.py`, or `strategies/`.
- Do not access live trading endpoints.
- Do not interpolate over D2-003A irreparable gaps.
