# Lab Coordinator State Model

## Status and Authority

This document defines the canonical **read-only** research-lab coordinator state
model that operator surfaces (dashboard, brief/report surface, approval queue,
scheduler shell) consume so they read one coherent status vocabulary instead of
inventing separate ones.

The model is descriptive only. It does **not** execute a transition, run or
generate a strategy, resume edge-search, write canonical evidence, write
candidate lifecycle records, execute canonical crossing, rank or recommend,
declare readiness or promotion, or touch runtime, paper/live, OMS, risk,
reconciliation, capital, broker, exchange, provider/API, or funding accounting
paths.

It is implemented by `tools/lab_state/` and exercised by
`tests/test_lab_state_model.py` and `tests/test_lab_state_resolver.py`.

## Edge-Search Hold

> No further edge-search is authorized by the coordinator state model. Strategy
> generation/search remains held until separate operator authorization.

The state model makes the lab legible. It does not authorize a new hypothesis
search cycle.

## Pipeline Stages

The model spans the lab lifecycle as an ordered pipeline:

```
idea_intake -> formalization -> experiment_run -> replay_normalization
  -> walkforward_oos_gate -> robustness -> candidate_review_reach
  -> reporting -> operator_gate
```

## State Vocabulary

The model introduces **no new status names**. Every state below already exists
in merged repo truth and is composed into one vocabulary:

| State | Stage(s) | Repo-truth source |
| --- | --- | --- |
| `not_started` | any | stage not reached |
| `formalized` | idea_intake, formalization | idea-intake / formalizer status entries |
| `experiment_complete` | experiment_run | Result Population + preserved denominator |
| `no_go` | overall | NO-GO conclusion (primary screen failure) |
| `blocked` | several | inputs unavailable / sequencing unmet |
| `replay_checked` | replay_normalization | `RP_REPLAY_NORMALIZATION_CONTRACT.md` (#565) |
| `oos_gate_pass` | walkforward_oos_gate | OOS `gate_decision=pass` (#567) |
| `oos_gate_fail` | walkforward_oos_gate | OOS `gate_decision=fail` (#567) |
| `oos_gate_blocked` | walkforward_oos_gate | OOS `gate_decision=blocked`/`advisory_only`, or dry-run-only (#567) |
| `robustness_advisory` | robustness | `GENERIC_ROBUSTNESS_REVIEW_REACH_CONTRACT.md` advisory summary (#566) |
| `candidate_review_blocked` | candidate_review_reach | `blocked_review_reason` (`BLOCKED_*`) (#566) |
| `candidate_review_not_created` | candidate_review_reach | `no_candidate_review_packet_reason` (`NO_GO_*`) (#566) |
| `candidate_ready_for_human_review` | candidate_review_reach | `candidate_review_packet_created=true` (#566) |
| `reported` | reporting | synthesis doc / status entry / conclusion traceability |
| `operator_gate_pending` | operator_gate | candidate lifecycle human-gated boundary |

## Reason Codes

Reason codes are re-used from existing contracts; the model adds only
namespaced `STATE_*` legibility codes that describe *why a stage reads the way it
does*, never a judgement about a strategy.

- **No-packet (`NO_GO_*`)** and **blocked (`BLOCKED_*`)** codes are taken
  verbatim from the generic robustness review reach contract (#566).
- **OOS gate decisions** (`pass` / `fail` / `blocked` / `advisory_only`) come
  verbatim from the OOS gate contract (#567) and map to coordinator states via
  `OOS_DECISION_TO_STATE`.
- **`STATE_*`** codes (e.g. `STATE_ARTIFACT_MISSING`, `STATE_OOS_DRY_RUN_ONLY`,
  `STATE_NO_CANDIDATE_PRODUCED`) are read-only legibility annotations.

## Artifact Reference Model

Every resolved stage carries `artifact_refs`: read-only pointers to the repo
artifacts consulted, each recording `role`, repo-relative `path`, and a
`present` flag. The resolver never fabricates progress: a missing or unreadable
artifact resolves fail-closed to `not_started` / `blocked` with an explicit
`STATE_*` reason code.

## Resolver Semantics

The resolver (`tools/lab_state/resolver.py`) reads committed JSON / markdown
artifacts and reports per-stage state plus one overall snapshot. Reading is
separated from resolving so the per-stage `resolve_*` helpers are pure and
testable.

Overall-state precedence (most dominant first):

```
candidate_ready_for_human_review > operator_gate_pending > no_go > blocked
  > oos_gate_fail > oos_gate_blocked > candidate_review_blocked
  > robustness_advisory > reported > replay_checked > experiment_complete
  > formalized > not_started
```

A NO-GO no-packet review (`candidate_review_not_created` with a `NO_GO_*`
reason) is normalized to the dominant overall `no_go`. The operator gate is
`operator_gate_pending` only when a candidate is ready for human review;
otherwise nothing exists to gate and it stays `not_started`. The model never
auto-promotes — the human-gated candidate lifecycle engine
(`tools/candidate_lifecycle/lifecycle_engine.py`) owns any real transition.

## Reference Binding

The committed end-to-end binding is `H-FUNDING-RATE-POSITIONING-FADE-01`:

- `formalized` (idea-intake / formalizer status entries),
- `experiment_complete` (`RP-2009` / `RP-7592`, denominator 36/36 preserved),
- `replay_checked` (both Result Populations normalize; they intentionally do not
  match each other),
- `oos_gate_blocked` (OOS evidence dry-run-only, purge/embargo deferred — not a
  rigorous gate pass),
- `robustness_advisory` (PSR / DSR / MinTRL withheld, per-trade Monte Carlo
  blocked rather than fabricated),
- `candidate_review_not_created` (`NO_GO_PRIMARY_RISK_SCREEN_FAILED`),
- `reported` (`FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md`),
- overall `no_go`; operator gate not pending.

A second binding (OOS gate fixture `RP-2592` / `WF-RUN-40BB0B209274054B`,
`gate_decision=fail`) exercises `oos_gate_fail`.

The static snapshot is printed by:

```
python -m tools.lab_state.run --snapshot
python -m tools.lab_state.run --snapshot --json
python -m tools.lab_state.run --list-states
python -m tools.lab_state.run --list-subjects
```

## Non-Authority Boundary

Every snapshot carries a `non_authority_declaration`. The model is read-only,
executes no transition, writes no canonical or candidate lifecycle evidence,
performs no canonical crossing, ranks/recommends nothing, and authorizes neither
edge-search nor paper/live/runtime work. Any such action remains outside this
package and requires separate operator authorization.
