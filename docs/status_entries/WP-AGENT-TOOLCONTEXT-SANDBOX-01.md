# WP-AGENT-TOOLCONTEXT-SANDBOX-01 Branch State

## Scope Summary

This package adds a repo-owned, closed-default ToolContext permission layer for
future bounded research-agent tool use. It adds role capability allowlists,
hard semantic and path prohibitions, deterministic allowed/blocked audit
records, and a fake-agent test harness that cannot invoke its file operation
before ToolContext authorization.

Branch: `agent/toolcontext-sandbox-01`.
Base: refreshed `origin/main` at `21b7a7695378b4daa364bafb44c3bdce3b4794de`
after PR #539 merge.

## Authorization

The active package records Main scope and Karl authorization of the
agent-boundary design gate. The merged design sources
`docs/architecture/2026-06-bounded_research_agent_authority_model.md` and
`docs/status_entries/WP-LAB-AGENT-BOUNDARY-DESIGN-01.md` were present and read
before implementation.

This package builds only the ToolContext cage. It adds no autonomous agent,
agent reasoning, scheduling, orchestration, network call, external write, or
authority-bearing decision logic.

## Roles

The implementation follows the merged design taxonomy rather than the
illustrative aliases in the execution package:

- `research_scout`
- `idea_formalizer`
- `draft_generator`
- `non_canonical_runner`
- `robustness_diagnostician`
- `candidate_review_packet_preparer`
- `notification_assistant`

Each role has an explicit immutable action allowlist. Unknown roles and
unlisted actions fail closed.

## Allowed Actions

The narrow capability vocabulary is:

- read architecture, status-entry, and research-pipeline documentation;
- read non-sensitive research artifacts and test fixtures;
- write only beneath `scratch/<active-wp-id>/` for roles granted scratch writes;
- target repo-owned read-only validators for the non-canonical runner;
- target the narrow repo-owned scratch-tool prefixes granted to diagnostic or
  non-canonical roles.

No network capability is allowed. All path inputs must be safe repo-relative
paths; absolute paths and traversal are rejected before operation execution.

## Hard Prohibitions

Every configured role inherits hard blocks covering:

- canonical Strategy Spec, Variant Manifest, Sweep Plan, Result Population,
  canonical walk-forward, trial-log, and candidate-registry writes;
- candidate registration, lifecycle transition, promotion, readiness, and
  freeze actions;
- overlay, execution, runtime, paper, live, OMS, risk, reconciliation,
  safe-mode, kill-switch, broker, exchange, order, and capital actions or paths;
- credentials, secrets, private endpoints, and network access;
- dependency-file mutation;
- `docs/project_status.md` mutation.

Hard semantic blocks are evaluated before role permissions. Generic scratch
write capability cannot bypass canonical, dependency, trial-log,
candidate-registry, or project-status path blocks.

## Audit Logging

Every authorization decision emits one record before an allowed operation can
run or a blocked exception is raised. Records include deterministic
`timestamp_utc`, `wp_id`, `role`, `action_type`, normalized `target_path`,
`decision`, `reason`, `policy_id`, and a non-authority statement.

The package provides in-memory and deterministic key-sorted JSONL sinks.
Blocked records contain no action metadata or secret payloads. Audit-sink
failure occurs before operation execution and therefore fails closed.

## Fake-Agent Harness

The test harness exposes a fixed file-write method. That method constructs a
`ToolAction` and delegates execution to `ToolContext.run_allowed`; it exposes no
direct generic mutation method. Tests prove an allowed active-WP scratch write
runs and a canonical Strategy Spec write is blocked, logged, and leaves the
target file unchanged.

The harness is test-only. No actual agent implementation is added.

## Boundary Summary

Changed files are limited to:

- `tools/agent_sandbox/__init__.py`
- `tools/agent_sandbox/audit.py`
- `tools/agent_sandbox/permissions.py`
- `tools/agent_sandbox/tool_context.py`
- `tests/test_agent_toolcontext_sandbox.py`
- `docs/status_entries/WP-AGENT-TOOLCONTEXT-SANDBOX-01.md`

No canonical artifact, schema, validator, query-layer, dependency, research
runner, backtester, runtime, paper/live, OMS, risk, reconciliation, overlay,
safe-mode, kill-switch, broker, exchange, order, capital, credential, private
endpoint, config, `lib/`, `src/`, or `docs/project_status.md` file changed.

## Validation Status

- `python -m pytest tests/test_agent_toolcontext_sandbox.py -q`: PASS, 60
  passed.
- `python -m pytest tests/test_validate_strategy_specs.py tests/test_validate_result_populations.py -q`:
  PASS, 155 passed.
- `python -m tools.registry.validate_strategy_specs`: PASS.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python -m tools.research_query.run --list-views`: PASS.
- `python -m compileall -q tools/agent_sandbox tests/test_agent_toolcontext_sandbox.py`:
  PASS.
- Ambient Python 3.14 `python -m pytest -q`: FAIL during collection because
  the ambient interpreter lacks repo dependencies `binance`, `pandas`, and
  `numpy`; not passing merge evidence.
- Repo-venv `python -m pytest -q`: baseline-limited, 1,925 passed, 1 skipped,
  and 1 failed in 1,413.62 seconds. The sole failure is
  `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage`
  because isolated-worktree local normalized data is absent
  (`normalized_data_local_exists` is false). This is the known adjacent-package
  local-data availability failure and is unrelated to this package diff.
- `python tools/dev/diff_scope_summary.py --check-forbidden` with the six exact
  allowed files: PASS; six intended files, no forbidden matches, and no
  allowed-file violations.
- `git diff --check`: PASS.

## Active-WP Requirement Traceability

| Requirement | Source | Evidence | Status |
|---|---|---|---|
| Per-role allowed actions | WP section 3 / 7 | `ROLE_PERMISSIONS` and role-policy test | satisfied |
| Route fake-agent actions through ToolContext | WP section 3 / 11 | fixed-method fake harness tests | satisfied |
| Structurally block hard prohibitions | WP section 8 | semantic/path policy and parameterized tests | satisfied |
| Deterministic blocked-action audit | WP section 3 / 6 / 11 | audit module and fixed-clock JSONL test | satisfied |
| Allowed actions pass | WP section 11 | document read, scratch write, validator-target tests | satisfied |
| Blocked actions do not mutate | WP section 11 | canonical-write non-mutation test | satisfied |
| All roles inherit hard prohibitions | WP section 11 | cross-product role/prohibition test | satisfied |
| No protected or forbidden scope touched | WP section 10 | changed-file inspection and scope helper | satisfied |
| Required validation | WP section 12 | Validation Status | satisfied with disclosed baseline-only full-suite failure |

## PR Status

- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/540
- Title: `WP-AGENT-TOOLCONTEXT-SANDBOX-01: Add ToolContext sandbox enforcement`
- GitHub state at final inspection: non-draft, mergeable, merge state `CLEAN`,
  with no status checks reported.
- Ready for Main/Karl review: yes.

## Non-Authority Statement

This package creates no canonical-write, candidate registration, lifecycle,
promotion, readiness, freeze, ranking, recommendation, approval, overlay,
execution, risk, capital, paper/live, runtime, credential, private-endpoint, or
human-gate authority. Research/workbench and audit artifacts remain
non-canonical and have no execution authority unless separately promoted by a
later explicitly authorized package.
