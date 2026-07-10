# Architecture Decision Record

## Context

The Agent Inbox can create noncanonical scratch draft packets. Turning arbitrary
typed content into repo-canonical Strategy Spec truth, then into a
compute-consuming research request, crosses two protected authority boundaries.

## Proposed decision for Karl

Adopt a two-gate, fail-closed control plane:

1. Gate C: Karl reviews the full canonicalization candidate bundle and approves
   exactly one Strategy Spec hash and append-only canonical target.
2. Gate Q: after separately prepared and frozen Variant Manifest/Sweep Plan,
   Karl approves their exact hashes plus a bounded budget, priority, dataset,
   denominator, and offline queue target.

The canonical writer is a future CLI-first package separate from
`tools.agent_inbox_intake`. Queue admission does not dispatch. Runner execution,
canonical evidence, candidate review/crossing, promotion/readiness, and
paper/live/runtime remain separate gates.

## Rejected alternatives

- Treat `flagged_for_canonicalization` as approval: rejected; annotation is not
  exact-content human approval.
- Let an Inbox or dashboard button write canonical truth: rejected; it weakens
  the current prereg/freeze boundary and conflates presentation with authority.
- Use one approval for canonicalization and queue execution: rejected; canonical
  truth creation and research-budget consumption are distinct scopes.
- Allow agent/model confidence to waive clarification or validation: rejected;
  model output is untrusted draft material and cannot create repo truth.
- Put canonical writing inside `tools.agent_inbox_intake`: rejected; it breaks
  physical and permission separation from arbitrary typed input.
- Auto-dispatch admitted work: rejected; no scheduler/autonomy is authorized.

## Consequences

- The path is deliberately slower at authority boundaries but auditable and
  equivalent to or stricter than current Karl exact-content freeze discipline.
- Content mutation invalidates approval and requires revalidation/reapproval.
- Near-duplicates consume no budget without explicit justification and Karl
  acknowledgement.
- Future implementation needs narrow schemas/validators and append-only failure
  handling, each in separately approved capsules.

## Open Karl decisions

- Approve/reject Gate C and Gate Q as separate Karl-only exact-content gates.
- Approve/reject CLI-first separate writer placement.
- Approve/reject the UI read/annotate/prepare-only posture.
- Approve/reject exact-duplicate rejection and near-duplicate exception policy.
- Approve/reject queue admission without dispatch and continued scheduler hold.

Until those decisions are approved, capsules C1-C5 are not draftable.
