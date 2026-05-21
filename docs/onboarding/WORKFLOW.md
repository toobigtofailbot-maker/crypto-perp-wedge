# Workflow (tool-agnostic)

## Roles

* Architecture Owner: sets decisions, phase mandates, allowed/forbidden scopes.
* Execution Operator: implements work packages exactly, runs gates, opens PRs, reports evidence.
* Code Generator (Claude Code): produces code changes inside allowed scope; never decides policy.
* Reviewer: verifies scope control + gates + correctness-first constraints.

## Source of truth

* Repo is the truth. Chats are planning and review layers.

## Standard delivery loop

1. Architecture defines work package (deliverable, scope, acceptance, gates).
2. Code Generator implements on a branch.
3. Operator runs gates and provides evidence.
4. Reviewer approves/requests changes.
5. Merge to main; tag when closing phases.

## Guardrail

Anything execution-critical must be deterministic and auditable. AI can accelerate research and implementation, but it must not “freewheel” in the critical path.

---

## Phase 2 Operating Model

### Chat Roles

**Main Architecture chat** — sole authority to lock/unlock decisions. Owns D2-xxx entries in `docs/decisions.md`. No other chat can modify locked decisions.

**Architecture Karl / Architecture Santi** — implementation coordinators. Turn locked decisions into execution-ready work packages. Prepare briefs for Execution chats. Review report-backs. Never redesign the locked baseline.

**Execution chats** — one per work package. Run Claude Code within the exact scope specified in the execution brief. Report back with evidence. Do not improvise or make decisions.

### Source of Truth

**Repo is the arbiter.** Chat agreement without a repo commit is not a decision.

- Locked decisions: `docs/decisions.md`
- Phase 2 baseline: `docs/onboarding/PHASE2_BASELINE.md`
- Work package evidence: PRs with validation gate outputs

### Work Package Flow

1. Main Architecture locks decisions
2. Architecture coordinator prepares execution brief
3. Execution chat implements on feature branch
4. Execution chat runs validation gates and reports back
5. Architecture coordinator reviews report-back
6. Karl or Santi approves and merges PR
7. Repo truth is updated

---

## Stage 2c Workflow Efficiency Lock

Canonical lock: `docs/research_pipeline/2026-05-stage2c_workflow_efficiency_operating_model_lock.md`.

Codex token-efficiency and context-hygiene guidance lives at `docs/ai/codex/CODEX_TOKEN_EFFICIENCY.md`. It is guidance-only and cannot weaken the tier model, authority split, validation discipline, H-005 preservation, project-status overlap guardrail, or active package scope.

Repo truth and active package scope still outrank this summary.

### Tiered Workflow Model

- Tier 0 - Strategy / boundary decisions: Karl/Main authority; package size varies; validation depends on the locked decision; re-engagement is required for boundary, methodology, runtime, or protected-path changes.
- Tier 1 - Safe documentation / planning packages: Karl/Main may authorize bounded docs/planning locks; packages should be small and mergeable; validation remains repo-required; re-engage Main/Karl when docs would change authority or sequencing.
- Tier 2 - Research artifacts / query packages: require approved package scope; validation must include integrity/query and registry checks as applicable; re-engage Main/Karl on evidence drift, authority questions, or stop triggers.
- Tier 3 - Local automation infrastructure: requires explicit package authority; validation must prove bounded local behavior and no runtime influence; re-engage Main/Karl before scheduler, trigger, runtime, or protected-path implications.
- Tier 4 - Runtime / paper / live / OMS / risk / protected paths: strict Main/Karl boundary authority only; this lock does not accelerate or relax Tier 4.

Package-specific forbidden scope overrides the general tier model.

### Authority Split

Main/Karl sets strategy, unlocks boundaries, approves methodology changes, and resolves Tier 0 and Tier 4 decisions. Side may draft packages inside approved envelopes, but must inspect repo truth and stop on boundary conflict. Codex executes only the active work package from refreshed `main` within exact scope and does not decide policy, methodology, lifecycle, promotion/demotion, scoring/ranking, runtime, paper/live, or downstream authority.

### Project-Status Overlap Guardrail

No simultaneous open PRs may modify `docs/project_status.md` unless the later PR is refreshed or rebased after the earlier PR merges. Every work package touching `docs/project_status.md` must start from refreshed `main`; before opening a PR that edits it, Codex must check for open PRs touching that file when feasible and stop if one exists. This is a merge-control rule, not a Main authorization gate.

### Standing Efficiency Authorization

Main may continue surfacing workload-reduction ideas, classified as safe to adopt now, needs design first, or risky / not recommended. Safe reductions may be adopted only when they do not weaken validation, repo truth, stop triggers, protected boundaries, or package-specific scope. Design-first reductions require a Tier 1 design package and Karl/Main approval before use.

### Validation, Reporting, and Handoffs

Refreshed-main preflight, integrity views, registry validators where repo convention requires them, and full pytest remain mandatory unless a future repo-approved validation-tier document changes that rule. Concise report-backs should use `A. Scope`, `B. Changed files`, `C. Validation`, `D. Boundary check`, and `E. Decision`, expanding for Tier 2/3/4, artifacts, stop triggers, validation failures, or package-specific requirements. Handoffs must state current merged WP, active next WP, open PR conflicts, current protected boundaries, and whether the package touches `docs/project_status.md`; reviews must inspect actual changed files.

### H-005 Preservation and R1/R2 Sequencing

H-005 continues under the strict exact-segment runway and is not changed mid-runway by workflow-efficiency design work. WP-S2c-21b may design paired-source reuse methodology and WP-S2c-21c may design batched REP+OL+REC cycle methodology, but WP-S2c-21c drafts only after WP-S2c-21b merges. Mandatory Main re-engagement is required after WP-S2c-21c report-back before R1/R2 may be applied to H-006 or later implementation runways. This lock does not authorize paired-source reuse implementation, batched-cycle implementation, H-006 implementation, or Path B.
