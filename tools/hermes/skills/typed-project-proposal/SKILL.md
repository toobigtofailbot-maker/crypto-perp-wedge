---
name: typed-project-proposal
description: Generate one evidence-anchored inert proposal.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [proposal, evidence, readonly]
    category: research
    requires_toolsets: [mcp-project-evidence]
---

# Typed Project Proposal

## When to use

Use only when asked to generate one of the seven supported review proposals:
`StrategyProposal`, `StrategyAdjustmentProposal`, `BugFixProposal`,
`LabImprovementProposal`, `DataAcquisitionProposal`,
`DependencyUpgradeProposal`, or `InvestigationProposal`.

## Procedure

1. Call `project_evidence_manifest` and bind its exact repo SHA.
2. Call `list_project_resources`, then read the smallest exact resources needed.
   A Research Memory result is an index/hint only; resolve its references through
   Project-Evidence before using them as FACT evidence.
3. For each resource anchor, copy the returned resource URI, evidence path,
   artifact SHA-256, and repo SHA exactly. For query evidence, copy every returned
   evidence input path/hash and the exact query limit. Never invent a hash.
4. Separate `facts`, `inferences`, and `open_questions`. Every FACT must cite one
   or more references present in both `evidence_refs` and `evidence_anchors`.
   Unsupported content is UNKNOWN or an OPEN QUESTION.
5. Select exactly one machine-readable affected domain and authority class. Use
   A0 for any protected or ambiguous scope. A1 and A2 remain proposal-only.
6. Fill every envelope and type-specific field required by the
   `submit_proposal` tool schema. Set `approval_required`, `not_authority`, and
   `review_required` to true; set `automatic_consumers` to an empty list. The
   requested authority kind is only `human_review_for_separate_work_package`,
   with self-approval, direct execution, and standing authority all false.
7. Call `submit_proposal` once. If validation rejects the proposal, do not weaken
   or bypass the contract; report the exact failure and leave the outbox unchanged.

## A0 protected domains

Use A0 for canonical evidence writes, Result Population mutation, authoritative
Strategy Spec mutation, promotion/GO, dispatch/KDAUTH, OMS, reconciliation, hard
risk, safe mode/kill switch, live strategy parameters, paper/live runtime,
exchange/order/capital access, private credentials, Search Governor legality,
holdout or budget bypass, and any ambiguous protected scope.

## Type constraints

- Strategy proposals are lab-evaluation concepts and make no readiness claim.
- Strategy adjustments target future lab evaluation only, never paper/live parameters.
- Bug fixes identify UNKNOWN root causes honestly and request no direct apply/merge.
- Data proposals permit no silent repair or fabrication.
- Dependency proposals permit no automatic install or update.
- Every proposal has validation and rollback/stop conditions.

## Authority boundary

This skill can only read exact Project-Evidence and write a validated inert JSON
proposal through the existing outbox. It cannot prepare executable payloads,
approve itself, act, apply, merge, promote, dispatch, trade, mutate the repository,
run shell or SQL, update dependencies, acquire data, or enable tools. It cannot
self-enable broader authority. H2.5, H3, and H4 are not started.

## Verification

The tool result says `not_authority=true`, `review_required=true`, and
`automatic_consumers=[]`; it reports the exact proposal type, authority class,
and repo SHA. Otherwise the result is UNKNOWN and must not be treated as valid.
