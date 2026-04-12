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
