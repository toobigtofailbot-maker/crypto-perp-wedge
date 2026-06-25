# Lab Operator Daily Brief (read-only)

_schema: `lab_operator_brief_report_v1` -- as of 2026-06-25_

> Read-only operator surface. Descriptive only: no recommendation, ranking, promotion/decision label, readiness verdict, edge-search suggestion, auto-send, notification, or scheduler.

> No further edge-search is authorized by the coordinator state model. Strategy generation/search remains held until separate operator authorization.

## At a glance

- subjects: 2
- completed runs: 2
- blocked runs: 0
- NO-GOs: 1
- open decision surfaces: 0
- candidate-review evidence: 0

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

- `H-FUNDING-RATE-POSITIONING-FADE-01` -- replay `replay_checked`; OOS gate `oos_gate_blocked` (STATE_OOS_DRY_RUN_ONLY) (evidence completed_dry_run_only); robustness `robustness_advisory`
- `OOS-GATE-FIXTURE-RP-2592` -- replay `replay_checked`; OOS gate `oos_gate_fail` (OOS_GATE_FAIL) (evidence completed_dry_run_only); robustness `robustness_advisory`

## Candidate-review readiness

_Surfaced only when packet evidence exists; never a readiness verdict or promotion._

- none (no candidate-review packet evidence)

## Withheld statistics and caveats

- withheld statistics: DSR, MinTRL, PSR
- This surface shows the full denominator (every run and state), not winners only.
- Evidence shown is non-canonical / scratch-only unless a row's evidence class says otherwise; nothing here is crossed, candidate-registered, paper-ready, or live-ready.
- Dry-run-only OOS evidence is not a rigorous gate pass.
- Withheld statistics (e.g. PSR / DSR / MinTRL) are shown explicitly rather than fabricated.
- Ordering is deterministic display order only and confers no ranking, recommendation, readiness, or promotion authority.
- Any real transition or approval requires separate human action through the candidate lifecycle engine; this dashboard cannot grant it.
