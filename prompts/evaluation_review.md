# Evaluation Review Prompt

Use this prompt for a Claude Code session operating as the Auditor, or for a
human reviewing an Auditor output.

---

## Role

You are reviewing an evaluation produced under `.claude/agents/auditor.md` and
`.claude/skills/run-evaluation.md`.

---

## Review checklist

### 1. Pre-registration

- Confirm the referenced `HYPOTHESIS.md` exists.
- Confirm the hypothesis declares economic rationale, primary timeframe,
  success criteria, kill criteria, free parameters, and expected trial count.
- Confirm no evaluation appears to have selected a timeframe after seeing
  results.

### 2. Dataset and D2-003A handling

- Confirm the evaluation names the dataset identifiers used.
- Confirm the D2-003A skip-count is recorded.
- Confirm irreparable gaps were skipped, not silently interpolated.

### 3. GateReport completeness

- Confirm every one of the eight D2-006 gates is present.
- Confirm every gate has a numeric `value`.
- Confirm every gate has a threshold.
- Confirm the GateReport has an `overall_pass` boolean.
- Confirm the summary includes the trial count used for DSR.

### 4. Trial log append

- Confirm `research/trial_log.jsonl` was appended correctly.
- Confirm exactly one new row corresponds to the reviewed evaluation.
- Confirm the appended row is valid JSON.
- Confirm `trial_id`, `hypothesis_id`, `config_sha256`, `dataset_sha256`,
  `params`, `in_sample_sharpe`, `oos_sharpe`, `max_drawdown`, and `n_obs`
  are present.
- Confirm existing rows were not edited.

### 5. Scope boundaries

- Confirm the Auditor did not modify `lib/evaluation.py`, `lib/backtest.py`,
  `strategies/`, `src/`, `configs/`, docs locked truth, or live-system files.
- Confirm the Auditor did not approve its own evaluation.

---

## Response format

```text
EVALUATION REVIEW
Decision: ACCEPT | REVISE | ESCALATE

Pre-registration: PASS | FAIL - <note>
D2-003A skip-count: PASS | FAIL - <note>
GateReport numeric gates: PASS | FAIL - <note>
Trial log append: PASS | FAIL - <note>
Scope boundaries: PASS | FAIL - <note>

Required corrections:
  1. <item or NONE>
```
