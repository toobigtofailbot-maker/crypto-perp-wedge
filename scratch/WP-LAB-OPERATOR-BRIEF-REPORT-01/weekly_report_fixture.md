# Lab Weekly Research Report (read-only)

_schema: `lab_operator_brief_report_v1` -- period 2026-W26_

> Read-only operator surface. Descriptive only: no recommendation, ranking, promotion/decision label, readiness verdict, edge-search suggestion, auto-send, notification, or scheduler.

> No further edge-search is authorized by the coordinator state model. Strategy generation/search remains held until separate operator authorization.

## Summary counts

- subjects: 2
- completed runs: 2
- blocked runs: 0
- NO-GOs: 1
- open decision surfaces: 0
- candidate-review evidence: 0

### Subjects by overall state (full population)

| overall state | count |
| --- | ---: |
| `not_started` | 0 |
| `formalized` | 0 |
| `experiment_complete` | 0 |
| `replay_checked` | 0 |
| `oos_gate_fail` | 1 |
| `oos_gate_blocked` | 0 |
| `candidate_review_blocked` | 0 |
| `robustness_advisory` | 0 |
| `no_go` | 1 |
| `blocked` | 0 |
| `candidate_ready_for_human_review` | 0 |
| `operator_gate_pending` | 0 |
| `reported` | 0 |

_Charting deferred: Charting deferred: weekly report is table-based static output only; no safe dependency-light static-chart path is adopted._

## Completed runs

- `H-FUNDING-RATE-POSITIONING-FADE-01` -- overall `no_go` (evidence non_canonical)
- `OOS-GATE-FIXTURE-RP-2592` -- overall `oos_gate_fail` (evidence non_canonical)

## Blocked runs

- none

## NO-GOs

- `H-FUNDING-RATE-POSITIONING-FADE-01` -- overall `no_go` (evidence non_canonical)

## Open decision surfaces

- none

## Validation status

| subject | replay | OOS gate | OOS evidence | robustness | withheld |
| --- | --- | --- | --- | --- | --- |
| `H-FUNDING-RATE-POSITIONING-FADE-01` | `replay_checked` | `oos_gate_blocked` | completed_dry_run_only | `robustness_advisory` | PSR, DSR, MinTRL |
| `OOS-GATE-FIXTURE-RP-2592` | `replay_checked` | `oos_gate_fail` | completed_dry_run_only | `robustness_advisory` | PSR, DSR, MinTRL |

## Candidate-review readiness

_Surfaced only when packet evidence exists; never a readiness verdict or promotion._

- `H-FUNDING-RATE-POSITIONING-FADE-01` [no evidence] -- `candidate_review_not_created` (NO_GO_PRIMARY_RISK_SCREEN_FAILED): No candidate-review packet evidence to surface (state `candidate_review_not_created`).
- `OOS-GATE-FIXTURE-RP-2592` [no evidence] -- `candidate_review_blocked` (BLOCKED_OOS_GATE_UNAVAILABLE): No candidate-review packet evidence to surface (state `candidate_review_blocked`).

## NO-GO caveats

- `H-FUNDING-RATE-POSITIONING-FADE-01`:
  - NO-GO on the primary drawdown screen (threshold 0.2).
  - Funding payments were not wired; this is a price/PnL signal test, not a complete funding-carry PnL test.
  - The NO-GO is about this hypothesis only, not a statement about all funding strategies.

## Artifact links

- `H-FUNDING-RATE-POSITIONING-FADE-01` [reporting_doc] `docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md` (present)
- `H-FUNDING-RATE-POSITIONING-FADE-01` [formalization_status_entry] `docs/status_entries/WP-LAB-IDEA-INTAKE-FORMALIZATION-01.md` (present)
- `H-FUNDING-RATE-POSITIONING-FADE-01` [generic_review_contract] `scratch/WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01/generic_review_contract.json` (present)
- `H-FUNDING-RATE-POSITIONING-FADE-01` [replay_fixture_summary] `scratch/WP-LAB-RP-REPLAY-NORMALIZATION-CONTRACT-01/replay_fixture_summary.json` (present)
- `H-FUNDING-RATE-POSITIONING-FADE-01` [conclusion_traceability] `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json` (present)
- `OOS-GATE-FIXTURE-RP-2592` [reporting_doc] `docs/research/WALKFORWARD_OOS_GATE_CONTRACT.md` (present)
- `OOS-GATE-FIXTURE-RP-2592` [formalization_status_entry] `docs/status_entries/WP-LAB-WALKFORWARD-OOS-GATE-01.md` (present)
- `OOS-GATE-FIXTURE-RP-2592` [generic_review_contract] `scratch/WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01/generic_review_contract.json` (present)
- `OOS-GATE-FIXTURE-RP-2592` [replay_fixture_summary] `scratch/WP-LAB-RP-REPLAY-NORMALIZATION-CONTRACT-01/replay_fixture_summary.json` (present)
- `OOS-GATE-FIXTURE-RP-2592` [oos_gate_summary] `scratch/WP-LAB-WALKFORWARD-OOS-GATE-01/fixture_gate_summary.json` (present)
- `OOS-GATE-FIXTURE-RP-2592` [conclusion_traceability] `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json` (present)

## Withheld statistics and caveats

- withheld statistics: DSR, MinTRL, PSR
- This surface shows the full denominator (every run and state), not winners only.
- Evidence shown is non-canonical / scratch-only unless a row's evidence class says otherwise; nothing here is crossed, candidate-registered, paper-ready, or live-ready.
- Dry-run-only OOS evidence is not a rigorous gate pass.
- Withheld statistics (e.g. PSR / DSR / MinTRL) are shown explicitly rather than fabricated.
- Ordering is deterministic display order only and confers no ranking, recommendation, readiness, or promotion authority.
- Any real transition or approval requires separate human action through the candidate lifecycle engine; this dashboard cannot grant it.
