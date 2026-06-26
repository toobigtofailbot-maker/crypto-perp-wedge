# Operator Visibility Delta

| Metric | Before | After |
| --- | ---: | ---: |
| coordinator subjects | 2 | 8 |
| covered coordinator artifacts | 8 | 107 |
| surface-visible artifacts | 4 | 103 |
| unmapped gap artifacts | 99 | 0 |
| malformed / unreadable artifacts | 0 | 0 |
| candidate ready | 0 | 0 |
| operator gate pending | 0 | 0 |

## After-State Summary

- Dashboard by overall state: `{'not_started': 0, 'formalized': 0, 'experiment_complete': 1, 'replay_checked': 0, 'oos_gate_fail': 1, 'oos_gate_blocked': 0, 'candidate_review_blocked': 0, 'robustness_advisory': 0, 'no_go': 3, 'blocked': 2, 'candidate_ready_for_human_review': 0, 'operator_gate_pending': 0, 'reported': 1}`
- Queue by status: `{'operator_gate_pending': 0, 'no_go': 3, 'blocked_validation': 3, 'advisory_only': 2, 'not_actionable': 0}`
- Nothing candidate-ready: `True`
- Strategy-agnostic guardrail preserved: subjects cover funding, SMA, ORB, price-only synthesis, canonical registry, and Result Populations without making any family privileged.
