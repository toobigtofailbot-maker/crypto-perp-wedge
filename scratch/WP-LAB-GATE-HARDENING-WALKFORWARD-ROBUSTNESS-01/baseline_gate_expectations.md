# Baseline Gate Expectations

## Source

These expectations consume:

- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_payload_catalog.json`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_ground_truth_contract.json`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/non_promotable_provenance_contract.md`

## Global Expectation

All PR #583 baselines are construction payloads and non-promotable. Candidate eligibility and crossing are always `reject_by_construction`, regardless of any future numeric result.

## `known_losing_baseline`

- WFO/OOS gate: `fail` or `insufficient`; never candidate-eligible.
- Robustness/MC gate: `fail`, `insufficient`, or `withheld`; never provenance-overriding.
- Statistical diagnostics: withheld or insufficient unless real required inputs exist.
- Denominator: all declared rows remain visible, including failed/loss rows.
- Candidate eligibility: `reject_by_construction`.
- Crossing: `reject_by_construction`.
- Numeric override allowed: false.
- Retuning allowed: false.

## `known_neutral_or_no_trade_baseline`

- WFO/OOS gate: `blocked` or `insufficient` for no-signal/no-valid-edge posture; not a pass.
- Robustness/MC gate: `withheld` or `insufficient`; no fabricated confidence.
- Statistical diagnostics: withheld or insufficient for no-signal/no-trade input gaps.
- Denominator: no-trade and unavailable rows remain visible.
- Candidate eligibility: `reject_by_construction`.
- Crossing: `reject_by_construction`.
- Numeric override allowed: false.
- Retuning allowed: false.

## `known_degenerate_or_invalid_baseline`

- WFO/OOS gate: `blocked` / invalid; no metrics claimed.
- Robustness/MC gate: `withheld` / invalid; no derived confidence.
- Statistical diagnostics: withheld / invalid.
- Denominator: invalid and blocked rows remain visible.
- Candidate eligibility: `reject_by_construction`.
- Crossing: `reject_by_construction`.
- Numeric override allowed: false.
- Retuning allowed: false.
