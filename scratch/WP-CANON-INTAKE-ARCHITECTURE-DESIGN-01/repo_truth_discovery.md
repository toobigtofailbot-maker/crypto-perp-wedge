# Repo Truth Discovery

Package: `WP-CANON-INTAKE-ARCHITECTURE-DESIGN-01`

## Preflight

- Refreshed `main` from `origin/main`; it was already current at `1969251`.
- Requested branch already existed locally and was identical to refreshed
  `main`; it was reused without overwriting changes.
- PRs #635, #636, #638, and #639 are merged.
- The preflight working tree was clean.

## Facts inspected

- `tools/agent_inbox_intake/models.py`, `service.py`, and `app.py`: isolated,
  bounded BTCUSDT/locked-timeframe scratch writer; exactly one packet; canonical,
  runner, pipeline, candidate, scheduler, notification, paper/live, and runtime
  authority denied.
- `docs/architecture/operator_dashboard_agent_inbox_architecture_lock.md`: Agent
  Inbox is separate from the read-only dashboard and has no canonical authority.
- `docs/research_pipeline/2026-06-concept_to_spec_authoring_approval_discipline.md`:
  human review, provenance, unsupported-claim separation, missing-data handling,
  clarification, and protected-assumption rejection precede spec drafting.
- `research/schemas/strategy_spec.schema.json`: current canonical grammar includes
  non-execution, provenance, bounded instrument/data/timeframe, entry/exit/risk,
  filters, no more than five free parameters, constraints, review, lineage,
  hash-pinning, preregistration, and realism assumptions.
- `research/schemas/variant_manifest.schema.json` and `sweep_plan.schema.json`:
  bounded variant axes/denominator, invalid/excluded combinations, validation,
  trial accounting, lineage, review, and hash-pinning.
- `research/schemas/result_population.schema.json`: Result Populations preserve
  full denominator, input/result identity, validation/error/data/realism
  summaries, lineage, review, and non-authority.
- `tools/lab_pipeline/orchestrator.py` and package status: exact-content prereg
  approval requires Karl, exact scope/statement, and frozen packet hash; broad or
  mismatched approval fails closed and denies canonical/candidate/runtime scope.
- `tools/lab_pipeline/runner_adapter.py` and its status entry: real offline runner
  invocation requires a separate Karl execute approval bound to prepared
  Strategy Spec/Variant Manifest/Sweep Plan hashes and exact run context.
- `docs/architecture/2026-06-agent_canonical_crossing_design.md`: full content,
  source hashes, structured human approval, append-only write, pre/post
  validation, and audit are required for a different scratch-to-canonical
  crossing; approval cannot be inferred from a label, comment, merge, or summary.
- `docs/architecture/candidate_lifecycle_design.md` and
  `tools/lab_approval_queue/queue_model.py`: evidence display and review packets
  do not execute gates, cross candidates, promote, or declare readiness.

## Inferences

- The canonical-intake design can reuse established exact-content principles
  without changing current schemas or authority.
- Canonical write and compute-consuming queue admission are distinct authority
  transitions and need distinct Karl approvals.
- Physical separation from `tools.agent_inbox_intake` is mandatory; a future
  CLI-first canonical writer is the narrowest trust boundary.

## Conflicts and stop-condition result

No repo-truth conflict or unclear prereg/freeze rule was found. The proposal
preserves the current strict discipline and stops if a later design is weaker.
No canonical, schema, validator, query, queue, candidate, runtime, or protected
artifact was changed.
