# Lab State-Model Coverage Audit

## Status and Authority

This document records a **read-only coverage audit** of the lab coordinator
state model (`tools/lab_state`) and the four operator surfaces that consume it
(dashboard, brief/report, approval queue, scheduler shell). It answers one
question: **does the operator view represent every committed research artifact it
should — and which committed artifacts are silently omitted?**

The audit is descriptive only. It mutates no artifact, runs no strategy,
fetches no data, executes no transition, writes no canonical or candidate
lifecycle evidence, resumes no edge-search, and **changes no coordinator
bindings**. Coverage gaps are reported as findings plus recommended follow-up
packages; they are deliberately **not fixed** here.

It is implemented by `tools/lab_state_coverage_audit/` and exercised by
`tests/test_lab_state_coverage_audit.py`.

## How operator coverage is defined

All four surfaces resolve state from a single source — the `SUBJECTS` dict in
`tools/lab_state/run.py`:

- `tools/lab_dashboard/data_model.py` imports `SUBJECTS`;
- `tools/lab_reporting/report_model.py` consumes the dashboard data;
- `tools/lab_approval_queue/queue_model.py` imports `SUBJECTS`;
- `tools/lab_scheduler_shell/shell.py` validates run-queue `subject_id`s against
  the `SUBJECTS` subject ids.

So **operator-visible coverage equals the set of subjects bound in `SUBJECTS`**.
There are exactly two, by deliberate design (see `LAB_COORDINATOR_STATE_MODEL.md`,
edge-search held):

1. `funding_positioning_fade_no_go` (`H-FUNDING-RATE-POSITIONING-FADE-01`), `no_go`;
2. `oos_gate_fail_demo` (`OOS-GATE-FIXTURE-RP-2592`), `oos_gate_fail`.

These bind **8 coordinator-referenced artifact paths**, derived programmatically
from `SUBJECTS` so the audit cannot drift from the live binding:

- 4 **surface-rendered** (shown as content): the funding-fade synthesis, the OOS
  gate contract doc, the funding-fade conclusion traceability, the generic
  candidate-review reach record;
- 4 **consulted for state** (presence/parse drives a stage state): two
  formalization status entries, the replay fixture summary, the OOS fixture gate
  summary.

## Method

`tools/lab_state_coverage_audit/run.py` enumerates **git-tracked** files under
`docs/research`, `docs/status_entries`, `research`, and `scratch`, then classifies
each via the pure `classify_artifact` rules. JSON/JSONL artifacts in the
coverage-bearing sets are parsed; an unparseable one **fails closed** to
`requires_followup_mapping` / `malformed` rather than being inferred covered.

### Coverage categories

Every artifact resolves to exactly one descriptive category
(`coordinator_subject_covered`, `surface_visible`, `known_supporting_artifact`,
`known_fixture`, `status_entry_only`, `synthesis_or_report`,
`blocked_or_no_go_evidence`, `candidate_or_crossing_evidence`,
`orphan_research_artifact`, `requires_followup_mapping`,
`intentionally_out_of_scope`) and one coverage status (`covered`,
`out_of_scope`, `unmapped_gap`, `malformed`).

## Results (this audit run)

| Metric | Count |
| --- | --- |
| total discovered artifacts | 1281 |
| covered coordinator artifacts | 8 |
| surface-visible artifacts | 4 |
| unmapped gap artifacts | 99 |
| malformed / unreadable artifacts | 0 |

The bulk (`intentionally_out_of_scope`, 736) is edge-search-era research/process
evidence the coordinator deliberately does not surface while edge-search is held;
`known_supporting_artifact` (264) is lab tooling / integration scratch and
contract docs; `status_entry_only` (168) is the unbound repo status entries.

## Findings — silent evidence (unmapped committed conclusions)

99 committed artifacts are **operator-relevant conclusions that no coordinator
subject binds**, so the operator view does not represent them:

- `scratch/WP-RESEARCH-FUNDING-CARRY-01/` — concluded NO-GO (no_candidate_review_packet_reason), unbound;
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/` (+ `-FOLLOWUP-01`) — concluded run with RP-2009 / RP-7592, human review packet, NO-GO, unbound;
- `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/` — SMA-family result packet + blocked reasons, unbound;
- `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/` — ORB exit respec result packet + blocked reasons, unbound;
- `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/` + `docs/research/PRICEONLY_SYNTHESIS_2026-06.md` — price-only synthesis, unbound;
- `research/result_populations/**` (8 canonical Result Populations) and `research/candidate_registry.jsonl` — canonical evidence, unbound.

Only `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json`
among the WP-RESEARCH conclusions is bound (subject 1).

These are **real gaps**, not malformed data: the coordinator was scoped narrowly
(one end-to-end NO-GO binding + one OOS fixture) and additional concluded
research has accumulated since without being bound.

## Recommended follow-up (not implemented here)

- **WP-LAB-COORDINATOR-SUBJECT-COVERAGE-EXTENSION-01** — bind the unmapped
  committed research conclusions (funding-carry, SMA-family, ORB-respec,
  price-only synthesis, canonical Result Populations / candidate registry) as
  additional **read-only** coordinator subjects in `tools/lab_state/run.py` so the
  operator view stops omitting them. Mapping only; no new research, no edge-search,
  no lifecycle writes.

Editing `SUBJECTS` is outside this audit-only package's scope.

## Reproduce

```
python -m tools.lab_state_coverage_audit.run --report
python -m tools.lab_state_coverage_audit.run --summary --json
python -m tools.lab_state_coverage_audit.run --inventory --json
python -m tools.lab_state_coverage_audit.run --list-categories
```

## Non-Authority Boundary

The audit is read-only. It executes no transition, writes no canonical or
candidate lifecycle evidence, performs no canonical crossing, ranks/recommends no
strategy, and authorizes neither edge-search nor paper/live/runtime work. Acting
on any recommended follow-up requires separate operator authorization.
