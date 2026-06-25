# WP-LAB-APPROVAL-QUEUE-SURFACE-01 — Repo-truth discovery

## Dependency check

`WP-LAB-COORDINATOR-STATE-MODEL-01` is **merged** (PR #568, commit `5107b86`).
`tools/lab_state/` (`model.py`, `resolver.py`, `run.py`) and
`docs/research/LAB_COORDINATOR_STATE_MODEL.md` are present on the base. **Not
blocked.**

## What already exists (consumed read-only)

- `tools/lab_state/model.py` — canonical state/stage vocabulary and reason-code
  families. Carries `operator_gate_pending`, `candidate_review_blocked`,
  `candidate_review_not_created`, `candidate_ready_for_human_review`,
  `oos_gate_fail`/`oos_gate_blocked`, plus `NO_PACKET_REASON_CODES` and
  `BLOCKED_REASON_CODES`. The queue reuses these verbatim; it invents no state.
- `tools/lab_state/resolver.py` — `build_snapshot()` resolves per-stage states
  including `resolve_operator_gate()` (pending only when a candidate is ready)
  and `resolve_candidate_review_reach()` (reads `candidate_review_packet_created`
  / `no_candidate_review_packet_reason` / `blocked_review_reason`). The queue
  reuses `build_snapshot` and `_select_review_example`.
- `tools/lab_state/run.py` — `SUBJECTS` read-only bindings over the two committed
  artifact sets (funding NO-GO, OOS-gate-fail fixture). The queue reuses these.
- `tools/lab_dashboard/` — the merged read-only results dashboard (PR #569). Same
  architecture (data_model + render + run CLI over `tools/lab_state`). The
  approval queue follows that pattern exactly but exposes a *gate / decision*
  view rather than a results view.
- `scratch/WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01/generic_review_contract.json`
  — the candidate-review reach contract with `no_candidate_review_packet_reason`
  / `blocked_review_reason` and a `sma_review_packet_shape` example that records
  `candidate_review_packet_created: true` (used only to exercise the
  evidence-backed path in a unit test; not bound into the default queue).
- `docs/research/GENERIC_ROBUSTNESS_REVIEW_REACH_CONTRACT.md`,
  `WALKFORWARD_OOS_GATE_CONTRACT.md` — reason-code / gate-decision repo truth.
- `tools/candidate_lifecycle/lifecycle_engine.py` — the human-gated lifecycle
  engine (`HUMAN_GATED_TO_STATES`). This is the **owner** of real transitions;
  the queue references it as the place a human decision is executed but never
  writes to it.
- `tools/notifications_poc/approval_models.py` — a scratch-only notifications /
  approvals pilot (`ApprovalStatus = pending|approved|rejected|blocked`). The
  queue aligns terminology (pending gate) but does **not** import or write it; it
  fires no notification and writes no approval.

## Honest current state

Both committed subjects conclude **NO-GO** / **blocked**. No committed evidence
records `candidate_review_packet_created: true`. Therefore the queue honestly
shows `operator_gate_pending_count = 0`, `candidate_review_packet_created_count
= 0`, `nothing_candidate_ready = true`, and only NO-GO / blocked / advisory-only
lanes are populated. This is correct, not an error; no fake candidate-ready
entries were created.

## Design decision

Add a new focused `tools/lab_approval_queue` module (package §5 allows it),
mirroring `tools/lab_dashboard`. It reuses `tools/lab_state` as the single
source of state truth, introduces no new state vocabulary, is deterministic, and
renders no executable control. It buckets existing coordinator states into
operator-facing queue lanes (`operator_gate_pending` / `no_go` /
`blocked_validation` / `advisory_only` / `not_actionable`) and surfaces the
`no_candidate_review_packet_reason` / `blocked_review_reason` / blockers /
artifact references the package requires.
