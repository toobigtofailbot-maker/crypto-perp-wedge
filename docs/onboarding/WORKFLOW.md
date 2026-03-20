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
