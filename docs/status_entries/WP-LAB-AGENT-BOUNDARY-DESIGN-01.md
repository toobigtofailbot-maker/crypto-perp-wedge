# WP-LAB-AGENT-BOUNDARY-DESIGN-01 - Bounded research-agent authority model

## WP id / title

- WP id: `WP-LAB-AGENT-BOUNDARY-DESIGN-01`
- Title: Design bounded research-agent authority model.
- Decision: `COMPLETE`.

## Branch / PR

- Branch: `docs/agent-boundary-design-01`
- Dedicated worktree:
  `C:\GitHub\crypto-perp-wedge-worktrees\docs-agent-boundary-design-01`
- Base: `origin/main` at `4da388a`.
- Rebase result: clean worktree created from refreshed `origin/main`.
- PR: `https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/530`

## Package class

Docs-only / Karl-gated design.

## Repo-truth discovery

- Startup anchors read: `docs/project_status.md`, `CLAUDE_START_HERE.md`,
  `docs/runbook.md`, and `AGENTS.md`.
- Active package brief read from the provided Codex attachment.
- Required package docs read:
  `docs/architecture/2026-06-side12-external-adoption-pilot-plan.md`,
  `docs/status_entries/WP-PLAN-SIDE12-ADOPTION-LOCK-01.md`,
  `docs/status_entries/WP-LAB-IDEA-INTAKE-FORMALIZATION-01.md`,
  `docs/status_entries/WP-LAB-WALKFORWARD-RUN-01.md`, and
  `docs/architecture/candidate_lifecycle_design.md`.
- Required optional docs checked and absent on current `origin/main`:
  `docs/status_entries/WP-PILOT-NOTIFICATIONS-APPROVALS-01.md` and
  `docs/status_entries/WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01.md`.
- Adjacent boundary docs read:
  `docs/architecture/2026-06-two_lane_sandbox_wall.md`,
  `docs/research_pipeline/2026-05-permanent_human_gate_preservation_sketch.md`,
  `docs/dashboard/README.md`, and
  `docs/status_entries/WP-GUIDE-AGENT-STD.md`.
- Existing docs and tooling were searched for agent, autonomy, sandbox,
  authority, approval, promotion, freeze, candidate registration, scratch-only,
  and non-canonical terms before drafting.
- Repo convention found: `docs/architecture/` has no README index, so no
  architecture README update was required.
- Repo-truth mismatch noted: the package brief listed PR #528 as merged, while
  refreshed `origin/main` for this worktree is `4da388a`, merge PR #527. The
  current branch state was treated as controlling.

## Scope summary

This package adds a docs-only architecture design for bounded future research
agents. The model defines agent roles, allowed future actions, hard
prohibitions, Karl/Main/human/audit/blocked gates, ToolContext-style sandbox
enforcement concepts, audit and blocked-action records, stop conditions, and a
future Phase C implementation sequence.

The design locks the principle that agents are agent-operated, not
agent-authorized, and it requires Karl blessing before any agent implementation
WP starts.

## Changed files

- `docs/architecture/2026-06-bounded_research_agent_authority_model.md`
- `docs/status_entries/WP-LAB-AGENT-BOUNDARY-DESIGN-01.md`

## Validation summary

- `python tools/dev/diff_scope_summary.py`: PASS; only the two scoped docs
  files were reported as untracked, and no forbidden-path matches were found.
- `git diff --check`: PASS.
- `python -m tools.research_query.run --list-views`: PASS.
- Ambient Python 3.14 `python -m pytest -q`: FAIL during collection in 6.26
  seconds because the ambient interpreter lacks repo dependencies (`binance`,
  `pandas`, and `numpy`); not used as passing merge evidence.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`: TIMED
  OUT after 1,204 seconds with no visible output; not used as passing merge
  evidence.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q -x`: FAIL
  in 75.61 seconds at
  `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage`
  because `fixture["normalized_data_local_exists"]` was `False` instead of
  `True`. This matches the isolated-worktree local-data availability failure
  disclosed by adjacent recent packages and is not a docs-only package failure.
  The rerun reached 518 passed, 1 skipped, and 1 failed before stopping after
  the first failure.
- Focused tests: not applicable; this is a docs-only design package with no
  package-specific code, schema, validator, query, artifact, or runtime
  behavior change.

## Boundary summary

- Canonical writes: none.
- Canonical Strategy Specs, Variant Manifests, Sweep Plans, Result Populations,
  trial log, candidate registry, and canonical walk-forward evidence mutated:
  none.
- Agent, orchestration, automation, LangGraph, Prefect, Claude Agent SDK, or
  ToolContext code implemented: none.
- Runner/backtester, `lib/backtest.py`, `lib/evaluation.py`, compiler, schema,
  validator, query-layer, dashboard implementation, and dependency files
  changed: none.
- Runtime, paper/live, OMS, risk, reconciliation, safe-mode, kill-switch,
  broker, exchange, order, capital, credential, private endpoint, and protected
  paths touched: none.
- Agent/external tool canonical, candidate, readiness, promotion, ranking,
  recommendation, approval, paper/live, runtime, or execution authority granted:
  none.
- `docs/project_status.md` changed: no.

## Active-WP requirement traceability

| Active-WP requirement | Evidence location | Status |
|---|---|---|
| Create bounded-agent authority design | `docs/architecture/2026-06-bounded_research_agent_authority_model.md` | satisfied |
| Include agent role taxonomy | Future Agent Role Taxonomy section | satisfied |
| Include allowed actions | Allowed Future Actions section | satisfied |
| Include hard prohibitions | Hard Prohibitions section | satisfied |
| Define Karl/Main/human/audit/blocked gates | Gate Model section | satisfied |
| Define ToolContext / sandbox concept | Enforcement Concept section | satisfied |
| Define audit/log requirements | Audit log and Blocked-action record sections | satisfied |
| Define stop conditions | Stop Conditions section | satisfied |
| Define future implementation WP sequence | Phase C Future Implementation Sequence section | satisfied |
| End with Karl blessing requirement | Acceptance / Blessing Statement section | satisfied |
| Avoid forbidden files and protected paths | Changed files and Boundary summary | satisfied |

## Merge status

- Local branch validation: complete.
- Push status: pushed to `origin/docs/agent-boundary-design-01`.
- PR status: PR #530 is open and ready for Karl/Main review.

## Next dependency / runway note

Karl blessing is required before any agent implementation WP starts. The future
ToolContext, audit-log, idea-formalizer wrapper, non-canonical runner,
robustness diagnostic, candidate-review packet, and notification assistant WPs
listed in the design are future options only and create no current
implementation or authority.
