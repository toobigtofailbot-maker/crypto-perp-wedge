# Lab Approval / Gate Queue Surface (read-only)

Status: read-only operator surface. **This surface displays gates. It does not
execute gates.**

## Purpose

Give a lab operator one legible view of:

- **pending human gates** — where a candidate is ready for human review and an
  operator go/no-go decision is held;
- **blocked validation states** — replay / OOS-gate / robustness / candidate-
  review blockers, with reason codes;
- **candidate-review readiness when evidence actually exists** —
  `candidate_review_packet_created` is shown True *only* when committed evidence
  records it.

It is a projection of the merged coordinator state model
(`tools/lab_state`, `WP-LAB-COORDINATOR-STATE-MODEL-01`). It adds no new state
vocabulary, re-ranks nothing, and holds no execution authority.

## What it is not

It writes no approval, fires no notification, writes no candidate-lifecycle
record, executes no canonical crossing or promotion, and declares no readiness.
Any real operator decision happens separately through the human-gated candidate
lifecycle engine (`tools/candidate_lifecycle`); this queue cannot grant it.

## Module

- `tools/lab_approval_queue/queue_model.py` — deterministic read-only projection
  of coordinator-state snapshots into queue entries + a queue summary.
- `tools/lab_approval_queue/render.py` — static HTML and markdown renderers
  (tables and text only; no scripts, no buttons, no forms, no auto-refresh).
- `tools/lab_approval_queue/run.py` — CLI:
  `--data-json` / `--html` / `--markdown` / `--list-statuses` / `--out-dir`.

## Queue status vocabulary

Each entry is bucketed deterministically from the coordinator overall state and
the `operator_gate` stage. No new *state* names are introduced; these are
operator-facing lanes over existing states.

| queue status | meaning |
| --- | --- |
| `operator_gate_pending` | a candidate is ready for human review; the operator decision is held (the only operator-actionable lane) |
| `no_go` | concluded NO-GO; nothing to gate |
| `blocked_validation` | a validation stage (replay / OOS / robustness / candidate-review) is blocked or failed |
| `advisory_only` | progress recorded (advisory robustness / replay-checked / reported); nothing to gate |
| `not_actionable` | an earlier stage; not yet reached an actionable state |

## Blocker kinds

`validation_blocker`, `replay_blocker`, `oos_gate_blocker`,
`robustness_blocker`, `candidate_review_blocker` — derived from the blocking
coordinator states (`blocked`, `oos_gate_fail`, `oos_gate_blocked`,
`candidate_review_blocked`). The held `operator_gate` is a human decision
surface, not a blocker, and is reported separately.

## Reason codes

`no_candidate_review_packet_reason` and `blocked_review_reason` are surfaced
verbatim from the generic robustness review reach contract
(`GENERIC_ROBUSTNESS_REVIEW_REACH_CONTRACT.md`) — the queue never re-invents a
code.

## Honest current state

Both committed subjects conclude NO-GO / blocked, and no committed evidence
records a created candidate-review packet. The queue therefore shows
`nothing_candidate_ready = true` and only NO-GO / blocked / advisory-only lanes
populated. **That is the correct honest state, not an error.** No fake
candidate-ready entries are created.

## Determinism

No clock, no git, no network. JSON is emitted with sorted keys; HTML and
markdown are pure functions of the data model. Two builds over the same checkout
are byte-identical.

## Edge-search hold

No further edge-search is authorized by this surface. Strategy
generation/search remains held until separate operator authorization.
