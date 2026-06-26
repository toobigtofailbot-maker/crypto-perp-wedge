# Lab State-Model Coverage Audit

## Status and Authority

This document records the **read-only coverage audit** of the lab coordinator
state model (`tools/lab_state`) and the operator surfaces that consume it
(dashboard, brief/report, approval queue, scheduler shell, unified operator
surface index). It answers one question: **does the operator view represent every
committed research artifact it should — and which committed artifacts are
silently omitted?**

The audit is descriptive only. It mutates no historical research artifact, runs
no strategy, fetches no data, executes no transition, writes no canonical or
candidate lifecycle evidence, resumes no edge-search, and creates no approval /
promotion / readiness state.

It is implemented by `tools/lab_state_coverage_audit/` and exercised by
`tests/test_lab_state_coverage_audit.py`.

## How operator coverage is defined

Operator surfaces resolve state from a single source — the `SUBJECTS` dict in
`tools/lab_state/run.py`:

- `tools/lab_dashboard/data_model.py` imports `SUBJECTS`;
- `tools/lab_reporting/report_model.py` consumes the dashboard data;
- `tools/lab_approval_queue/queue_model.py` imports `SUBJECTS`;
- `tools/lab_scheduler_shell/shell.py` validates run-queue `subject_id`s against
  the `SUBJECTS` subject ids.

So **operator-visible coverage equals the set of subjects and supplemental
artifact references bound in `SUBJECTS`**. After
`WP-LAB-COVERAGE-GAP-CLOSE-01`, there are eight coordinator subjects:

1. `funding_positioning_fade_no_go` (`H-FUNDING-RATE-POSITIONING-FADE-01`), `no_go`;
2. `oos_gate_fail_demo` (`OOS-GATE-FIXTURE-RP-2592`), `oos_gate_fail`;
3. `funding_carry_01_blocked_no_go` (`WP-RESEARCH-FUNDING-CARRY-01`), `no_go`;
4. `funding_carry_02_no_go` (`WP-RESEARCH-FUNDING-CARRY-02`), `no_go`;
5. `edge_sma_family_blocked` (`WP-RESEARCH-EDGE-SMA-FAMILY-01`), `blocked`;
6. `orb_exit_respec_blocked` (`WP-RESEARCH-ORB-EXIT-RESPEC-01`), `blocked`;
7. `priceonly_synthesis_reported` (`WP-RESEARCH-PRICEONLY-SYNTHESIS-01`), `reported`;
8. `historical_canonical_evidence_bundle`
   (`HISTORICAL-CANONICAL-EVIDENCE`), `experiment_complete`.

These bind **107 coordinator/operator-visible artifact paths** derived
programmatically from `SUBJECTS` so the audit cannot drift from the live binding:
103 surface-visible paths (stage documents plus supplemental drill-down evidence)
and 4 consulted-only paths.

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

## Results

| Metric | Count |
| --- | --- |
| total discovered artifacts | 1303 |
| covered coordinator artifacts | 107 |
| surface-visible artifacts | 103 |
| unmapped gap artifacts | 0 |
| malformed / unreadable artifacts | 0 |

The package brief quoted an earlier audit total of 1281 discovered artifacts.
Refreshed `origin/main` at `b64c4f2` enumerates 1303 tracked artifacts under the
audited roots, while preserving the exact pre-binding 99 unmapped gap artifacts.

The bulk (`intentionally_out_of_scope`, 736) remains edge-search-era
research/process evidence the coordinator deliberately does not surface while
edge-search is held; `known_supporting_artifact` (283) is lab tooling /
integration scratch and contract docs; `status_entry_only` (171) is unbound repo
status entries.

## Findings — silent evidence (unmapped committed conclusions)

The pre-binding refreshed audit found 99 committed artifacts that were
operator-relevant conclusions or evidence references but not bound to any
coordinator subject:

- `scratch/WP-RESEARCH-FUNDING-CARRY-01/` — concluded NO-GO (no_candidate_review_packet_reason), unbound;
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/` (+ `-FOLLOWUP-01`) — concluded run with RP-2009 / RP-7592, human review packet, NO-GO, unbound;
- `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/` — SMA-family result packet + blocked reasons, unbound;
- `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/` — ORB exit respec result packet + blocked reasons, unbound;
- `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/` + `docs/research/PRICEONLY_SYNTHESIS_2026-06.md` — price-only synthesis, unbound;
- `research/result_populations/**` (8 canonical Result Populations) and `research/candidate_registry.jsonl` — canonical evidence, unbound.

Before `WP-LAB-COVERAGE-GAP-CLOSE-01`, only
`scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json`
among the WP-RESEARCH conclusions was bound (subject 1).

These were **real gaps**, not malformed data: the coordinator had been scoped
narrowly (one end-to-end NO-GO binding + one OOS fixture) and additional
concluded research had accumulated since without being bound.

## Closure

`WP-LAB-COVERAGE-GAP-CLOSE-01` binds all 99 former gap artifacts into
read-only coordinator/operator visibility. None remain unmapped, and none are
classified malformed or unreadable.

No historical artifact content is changed. The binding is strategy-agnostic:
funding, SMA, ORB, price-only synthesis, candidate registry, and Result
Population evidence are represented as committed history rather than as a new
strategy lead.

Candidate-ready remains zero and operator-gate-pending remains zero. Historical
NO-GOs and blocked attempts remain NO-GO / blocked; the canonical evidence
bundle is visible as evidence, not as candidate promotion or approval authority.

## Recommended follow-up

- none for the audited 99 former gap artifacts.

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
