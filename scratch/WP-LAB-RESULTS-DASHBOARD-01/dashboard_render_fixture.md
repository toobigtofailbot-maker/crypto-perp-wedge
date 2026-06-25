# Lab Results Dashboard (read-only)

_schema: `lab_results_dashboard_v1` -- read_only_operator_visibility_

> Read-only operator visibility surface. No executable controls: no run, approve, promote, retry, scheduler, or live-fetch.

> No further edge-search is authorized by the coordinator state model. Strategy generation/search remains held until separate operator authorization.

## Denominator summary (full population, not winners only)

- subjects: 2
- completed experiment runs reached: 2
- NO-GO: 1
- blocked: 0
- candidate ready for human review: 0
- operator gate pending: 0

### Subjects by overall state

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

### Trial denominator over 1 distinct Result Population set(s)

| planned | complete | failed | invalid | blocked | pruned |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 36 | 36 | 0 | 0 | 0 | 0 |

## Caveats

- This surface shows the full denominator (every run and state), not winners only.
- Evidence shown is non-canonical / scratch-only unless a row's evidence class says otherwise; nothing here is crossed, candidate-registered, paper-ready, or live-ready.
- Dry-run-only OOS evidence is not a rigorous gate pass.
- Withheld statistics (e.g. PSR / DSR / MinTRL) are shown explicitly rather than fabricated.
- Ordering is deterministic display order only and confers no ranking, recommendation, readiness, or promotion authority.
- Any real transition or approval requires separate human action through the candidate lifecycle engine; this dashboard cannot grant it.

## Subjects

### H-FUNDING-RATE-POSITIONING-FADE-01 -- `no_go`

- label: funding_rate_positioning_fade
- evidence class: `non_canonical`
- denominator: planned 36, complete 36, failed 0, invalid 0, blocked 0, pruned 0 (preserved=True)
- replay: `replay_checked` (STATE_REPLAY_NORMALIZED)
- OOS gate: `oos_gate_blocked` (STATE_OOS_DRY_RUN_ONLY); evidence status: completed_dry_run_only
- robustness: `robustness_advisory` (STATE_ROBUSTNESS_ADVISORY_ONLY); withheld statistics: PSR, DSR, MinTRL
- candidate review: `candidate_review_not_created` (NO_GO_PRIMARY_RISK_SCREEN_FAILED)
- reporting: `reported`; operator gate: `not_started`
- Result Populations: RP-2009 (18 rows), RP-7592 (18 rows)
- NO-GO caveats:
  - NO-GO on the primary drawdown screen (threshold 0.2).
  - Funding payments were not wired; this is a price/PnL signal test, not a complete funding-carry PnL test.
  - The NO-GO is about this hypothesis only, not a statement about all funding strategies.
- artifact drill-down:
  - `docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md` [reporting_doc] (present)
  - `docs/status_entries/WP-LAB-IDEA-INTAKE-FORMALIZATION-01.md` [formalization_status_entry] (present)
  - `scratch/WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01/generic_review_contract.json` [generic_review_contract] (present)
  - `scratch/WP-LAB-RP-REPLAY-NORMALIZATION-CONTRACT-01/replay_fixture_summary.json` [replay_fixture_summary] (present)
  - `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json` [conclusion_traceability] (present)

### OOS-GATE-FIXTURE-RP-2592 -- `oos_gate_fail`

- label: walkforward_oos_gate_fixture
- evidence class: `non_canonical`
- denominator: planned 36, complete 36, failed 0, invalid 0, blocked 0, pruned 0 (preserved=True)
- replay: `replay_checked` (STATE_REPLAY_NORMALIZED)
- OOS gate: `oos_gate_fail` (OOS_GATE_FAIL); evidence status: completed_dry_run_only
- robustness: `robustness_advisory` (STATE_ROBUSTNESS_ADVISORY_ONLY); withheld statistics: PSR, DSR, MinTRL
- candidate review: `candidate_review_blocked` (BLOCKED_OOS_GATE_UNAVAILABLE)
- reporting: `reported`; operator gate: `not_started`
- Result Populations: RP-2009 (18 rows), RP-7592 (18 rows)
- artifact drill-down:
  - `docs/research/WALKFORWARD_OOS_GATE_CONTRACT.md` [reporting_doc] (present)
  - `docs/status_entries/WP-LAB-WALKFORWARD-OOS-GATE-01.md` [formalization_status_entry] (present)
  - `scratch/WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01/generic_review_contract.json` [generic_review_contract] (present)
  - `scratch/WP-LAB-RP-REPLAY-NORMALIZATION-CONTRACT-01/replay_fixture_summary.json` [replay_fixture_summary] (present)
  - `scratch/WP-LAB-WALKFORWARD-OOS-GATE-01/fixture_gate_summary.json` [oos_gate_summary] (present)
  - `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json` [conclusion_traceability] (present)
