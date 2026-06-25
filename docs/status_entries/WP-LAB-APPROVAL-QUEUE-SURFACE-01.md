# WP-LAB-APPROVAL-QUEUE-SURFACE-01 — Read-only research-lab approval / gate queue surface

## Package

- Package: `WP-LAB-APPROVAL-QUEUE-SURFACE-01`
- Decision: `COMPLETE`
- Package class: research-lab operator gate surface.
- Execution mode: repo-first, fresh isolated worktree, read-only queue surface,
  no writes, no edge-search.

## Objective

Build a read-only surface for pending human gates, blocked validation states,
and candidate-review readiness *when evidence actually exists*. **This WP
displays gates. It does not execute gates.**

## Dependency

`WP-LAB-COORDINATOR-STATE-MODEL-01` is **merged** (PR #568, commit `5107b86`),
providing `tools/lab_state/` and `docs/research/LAB_COORDINATOR_STATE_MODEL.md`.
Not blocked.

## Repo-Truth Discovery

Recorded in `scratch/WP-LAB-APPROVAL-QUEUE-SURFACE-01/repo_truth_discovery.md`.
Key findings: the coordinator state model already carries the exact gate
vocabulary (`operator_gate_pending`, `candidate_review_blocked`,
`candidate_review_not_created`, `candidate_ready_for_human_review`,
`oos_gate_fail`/`oos_gate_blocked`) and reason-code families
(`NO_PACKET_REASON_CODES`, `BLOCKED_REASON_CODES`); the generic robustness review
reach contract carries `no_candidate_review_packet_reason` /
`blocked_review_reason` and the only `candidate_review_packet_created: true`
example; `tools/candidate_lifecycle` owns real human-gated transitions. A new
focused `tools/lab_approval_queue` module (mirroring the merged
`tools/lab_dashboard`) is the correct low-risk choice: it reuses
`tools/lab_state` as the single source of state truth, adds no new state
vocabulary, and renders no executable control.

## Delivered

- `docs/research/LAB_APPROVAL_QUEUE_SURFACE.md` — surface contract.
- `docs/status_entries/WP-LAB-APPROVAL-QUEUE-SURFACE-01.md` — this entry.
- `tools/lab_approval_queue/__init__.py`.
- `tools/lab_approval_queue/queue_model.py` — deterministic read-only projection
  of coordinator-state snapshots into queue entries + summary.
- `tools/lab_approval_queue/render.py` — static HTML / markdown renderers (tables
  and text only; no scripts/controls).
- `tools/lab_approval_queue/run.py` — CLI (`--data-json` / `--html` /
  `--markdown` / `--list-statuses` / `--out-dir`).
- `tests/test_lab_approval_queue.py` — 11 tests.
- `scratch/WP-LAB-APPROVAL-QUEUE-SURFACE-01/repo_truth_discovery.md`
- `scratch/WP-LAB-APPROVAL-QUEUE-SURFACE-01/approval_queue_contract.json`
- `scratch/WP-LAB-APPROVAL-QUEUE-SURFACE-01/approval_queue_fixture.json`
- `scratch/WP-LAB-APPROVAL-QUEUE-SURFACE-01/validation_summary.txt`
- `scratch/WP-LAB-APPROVAL-QUEUE-SURFACE-01/main_report_back_guardrail.txt`

## What the queue exposes

- `operator_gate_pending` — held human decision when a candidate is ready.
- `blocked_validation` — replay / OOS-gate / robustness / candidate-review
  blockers, each with stage, state, reason code, and detail.
- `no_candidate_review_packet_reason` and `blocked_review_reason` — surfaced
  verbatim from the generic review reach contract.
- `candidate_review_packet_created` — True **only** when committed evidence
  records it.
- OOS-gate / replay / robustness blockers via `blocker_kind`.
- human decision surfaces (pending, explicitly not executable here).
- de-duplicated artifact references with present/missing flags.

## Honest current state

Both committed subjects conclude NO-GO / blocked, and no committed evidence
records a created candidate-review packet. The queue therefore shows
`operator_gate_pending_count = 0`, `candidate_review_packet_created_count = 0`,
`nothing_candidate_ready = true`, with only NO-GO / blocked / advisory-only lanes
populated. This is the correct honest state, asserted by a test. No fake
candidate-ready entries were created.

## Boundary Summary

- No gate executed; descriptive read-only projection only.
- No approval write, no candidate-lifecycle write, no notification firing, no
  canonical crossing, no promotion, no readiness declaration, no execution
  authority.
- No strategy run/generation, no edge-search, no backtest (reads committed
  JSON/markdown only).
- No Strategy Spec, Variant Manifest, Sweep Plan, canonical Result Population,
  trial log, candidate registry, or candidate lifecycle write.
- No runtime, paper/live, OMS, risk, reconciliation, capital, broker, exchange,
  provider/API/network, funding accounting, or scheduler autonomy.
- No queue execution control (no approve/reject/promote/run button, no scheduler
  toggle, no live fetch, no auto-refresh) and no large tracked data.

## Determinism

No clock, no git, no network. JSON emitted with sorted keys; HTML/markdown are
pure functions of the model. Two `--data-json` builds are byte-identical
(sha256 `dd7234cfab0e4c1d4cf756b7fa1c1d97ac8ceeb64ecb4f215816bd13e5eb7013`).

## Edge-Search Hold

No further edge-search is authorized by this surface. Strategy
generation/search remains held until separate operator authorization.

## Validation

Recorded in `scratch/WP-LAB-APPROVAL-QUEUE-SURFACE-01/validation_summary.txt`.
Scoped pytest (`tests/test_lab_approval_queue.py`, 11 passed; with
`tests/test_lab_state*.py`, 31 passed; shared-module regression
`tests/test_lab_dashboard.py`, 9 passed), candidate registry validator (OK),
research query `--list-views` (unchanged), diff scope summary (no forbidden-path
matches), and `git diff --check` (clean). Full repo pytest was not run to
completion and is not claimed as passed; the new code is stdlib-only and its
scoped suites pass.

## Merge Status

Ready for review after push.
