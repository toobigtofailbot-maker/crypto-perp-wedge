# Scratch-to-Canonical Intake Control Plane

Package: `WP-CANON-INTAKE-ARCHITECTURE-DESIGN-01`

Status: proposed architecture for Karl decision; design only. This document
implements no canonicalization, canonical write, queue write, execution, API,
UI, scheduler, or autonomy.

## 1. Decision summary

The proposed path is a fail-closed, two-gate control plane:

```text
Agent Inbox scratch draft
-> human clarification and deterministic validation
-> frozen canonicalization package candidate
-> Karl exact-content canonical-write approval (Gate C)
-> append-only canonical Strategy Spec write
-> separately prepared, hash-pinned Variant Manifest and Sweep Plan
-> Karl exact-content queue-admission approval (Gate Q)
-> bounded offline-research queue item
-> Result Population
-> separately governed candidate-review package
```

Gate C and Gate Q are different approvals. Neither may be inferred from a UI
action, review state, file presence, PR label/comment, merge, agent output, or a
previous approval with another scope.

This is at least as strict as the current preregistration/freeze discipline. It
reuses the existing essential properties: Karl as gate owner, full content
surfaced before approval, exact scope, canonical SHA-256 binding, immutable
reviewed content, explicit non-authority fields, and fail-closed mismatch
handling. It adds a distinct canonical-write gate before the already separate
execution/admission decision.

## 2. Repo-truth basis

Facts:

- `tools.agent_inbox_intake` writes exactly one noncanonical packet beneath its
  package-local scratch root. Its flags explicitly deny Strategy Spec, Variant
  Manifest, Sweep Plan, Result Population, candidate, runner, pipeline,
  scheduler, paper/live, and runtime authority.
- The intake packet preserves the normalized source request, formalizer output,
  blockers, warnings, provenance, source hashes, and ToolContext audit.
- The existing concept-to-spec discipline requires human review, provenance,
  unsupported-claim separation, data/timeframe resolution, and rejection or
  deferral of protected or executable assumptions before Strategy Spec drafting.
- Current canonical Strategy Specs are schema-validated, non-executable,
  provenance-bearing, bounded to no more than five free parameters, and include
  review, lineage, hash-pinning, preregistration, data/timeframe, and realism
  surfaces.
- Current Variant Manifest and Sweep Plan schemas preserve bounded populations,
  invalid/excluded combinations, trial accounting, validation methods, data and
  realism assumptions, review, lineage, and hash-pinning.
- The lab pipeline's exact-content prereg gate requires `approved_by=Karl`, an
  exact approval scope and statement, and the frozen packet SHA-256; broad,
  missing, malformed, or mismatched approvals fail closed.
- Real offline runner use has a separate Karl execute approval bound to the
  prepared Strategy Spec, Variant Manifest, and Sweep Plan path/hash set and
  exact run context. A prereg approval cannot substitute for it.
- Scratch candidate-review packets and read-only approval queues have no
  canonical crossing, candidate, promotion, readiness, paper/live, or runtime
  authority.

Inference:

- Scratch review and canonical writing must remain separate trust domains.
- Canonical creation consumes neither compute nor candidate authority, but it
  changes repo truth and therefore requires a Karl exact-content gate.
- Queue admission consumes research budget and therefore needs a later,
  separately scoped Karl exact-content gate over a complete preregistered
  Spec/Manifest/Plan and budget envelope.

## 3. Human gate and exact approved content

`flagged_for_canonicalization` is annotation only. It may route a draft into a
human review list, but it authorizes no generation, validation pass, canonical
write, queue admission, or execution.

Before Gate C, a separate future canonicalization package may prepare a frozen
candidate bundle outside `tools.agent_inbox_intake`. The full bundle presented
to Karl must contain:

- the exact proposed Strategy Spec JSON bytes or their canonical JSON form;
- a canonical SHA-256 for that exact content;
- the source Agent Inbox draft path and hash;
- source-request and formalizer-result hashes already carried by the packet;
- a provenance and lineage map;
- a validation report containing every pass, warning, rejection reason,
  unresolved claim, ambiguity, clarification, duplicate assessment, and data or
  feature limitation;
- an explicit diff from the scratch source, identifying every generated,
  normalized, clarified, omitted, or rejected statement;
- non-authority declarations: no execution, queue, candidate, promotion,
  readiness, paper/live, runtime, scheduler, or notification authority.

Gate C is a structured approval record whose required semantics are:

- `approved_by` is exactly `Karl`;
- `approval_scope` is exactly one canonical Strategy Spec append-only write;
- `content_reviewed=true` and the approved Strategy Spec hash matches;
- source draft path/hash and validation-report path/hash match;
- `authorizes_canonical_write=true`;
- queue, execution, candidate lifecycle, promotion/readiness, paper/live,
  runtime, scheduler/autonomy, and notification flags are all false;
- target path and new artifact identifier are exact and non-existing;
- approval timestamp and approval-record identity are present.

Any content change after approval invalidates Gate C. The changed bundle must be
revalidated, re-frozen, and reapproved. A summary-only, label-only, UI-only, or
hash-free approval fails closed.

## 4. Canonicalization validation

Validation produces findings; it never grants approval. All blocking findings
must be resolved before a Gate C candidate can be presented.

### 4.1 Hypothesis and scope

Require one falsifiable mechanism with observable inputs, deterministic signal
conditions, specified entry/exit/risk concepts, expected direction, and an
explicit disconfirmation condition. Reject tautologies, outcome-defined
signals, hindsight-dependent rules, and claims that cannot be disproved.

Require a bounded market, instrument, and timeframe. Current repo truth limits
this path to BTCUSDT Binance USDT-M perpetual and the locked timeframe set unless
a separate package authorizes expansion. Confirmation timeframes must also be
declared and locked.

### 4.2 Feature, data, and historical testability

Every feature must map to an approved, deterministic repo capability or be
blocking. Verify historical coverage, timestamp/alignment semantics, warm-up,
irreparable-gap handling, frequency, lookahead safety, and required funding,
mark, index, premium, or OHLCV streams against repo truth. Hidden external,
paid, online, runtime, broker, account, sentiment, news, order-book, or future
data dependencies block canonicalization.

Historical testability requires deterministic reconstruction from identified
data without discretionary interpretation. Untestable narratives or features
requiring unavailable inputs enter clarification/data-blocked state, not
canonical state.

### 4.3 Parameters and stop conditions

Declare every selectable value, type, range or finite set, default/reference
value, rationale, and invalid combination. Count any value later selectable in
search as free. Enforce the current maximum of five free parameters unless a
future explicit Main/Karl exception exists. Reject open-ended ranges, adaptive
post-result choices, hidden degrees of freedom, and combinatorial expansion
without a bounded population and budget.

The spec must state thesis-level stop conditions: unavailable/invalid data,
compiler or runner incompatibility, denominator loss, validation failure,
predeclared evidence failure, or any need to mutate frozen content after seeing
results. Stop conditions do not themselves execute a run or gate.

### 4.4 Duplicate and near-duplicate control

Compare the proposed mechanism, family, instruments, timeframes, features,
entry/exit topology, risk model, filters, and parameter domains against all
existing Strategy Specs, candidate records, concluded families, and relevant
Result Populations. Exact duplicates are rejected. Near-duplicates require:

- named related artifact and family identifiers;
- a material-difference statement;
- why existing evidence does not already answer the question;
- incremental compute justification;
- Karl acknowledgement in Gate C if the candidate still proceeds.

Cosmetic renaming, parameter relabeling, or a small range change is not a new
family. Uncertain duplicate status blocks pending human resolution.

### 4.5 Claims, provenance, and ambiguity

Every claim must be classified as source statement, human clarification,
generated normalization/inference, assumption, or evidence-backed repo fact.
Source locators and hashes are required where available. Generated content may
organize or translate source material but must never invent economic logic,
data availability, prior evidence, expected performance, or implementation
capability.

Unsupported performance or edge claims remain hypotheses/test targets, never
evidence. Unresolved claims must be listed. Any unresolved claim material to
signal logic, data, parameter bounds, stop conditions, or test interpretation
blocks canonicalization.

Ambiguity is not silently defaulted. The package emits a concrete clarification
request, records the human answer with identity/time/provenance, regenerates the
candidate, and reruns validation. Multiple plausible interpretations require
the human to select one or explicitly split the idea.

### 4.6 Rejection reasons

Rejection/defer codes should be stable and machine-readable, including at least:
`VAGUE_OR_NON_FALSIFIABLE`, `SCOPE_UNBOUNDED`, `FEATURE_UNAVAILABLE`,
`HISTORICALLY_UNTESTABLE`, `DATA_UNAVAILABLE`, `PARAMETERS_UNBOUNDED`,
`PARAMETER_LIMIT_EXCEEDED`, `DUPLICATE`, `NEAR_DUPLICATE_UNJUSTIFIED`,
`PROVENANCE_INSUFFICIENT`, `UNRESOLVED_MATERIAL_CLAIM`, `AMBIGUITY_REQUIRES_HUMAN`,
`UNSUPPORTED_CLAIM`, `HIDDEN_RUNTIME_ASSUMPTION`, `PROTECTED_BOUNDARY_REQUIRED`,
and `MODEL_GENERATED_LOGIC_UNVERIFIED`.

Rejection is not candidate-lifecycle rejection. It is only intake disposition.

## 5. Canonical write boundary

`tools.agent_inbox_intake` must never import, call, or receive permission to
write a canonical artifact. Its scratch prefix and non-authority flags remain
unchanged.

A future implementation should use a separately reviewed package such as
`tools/canonical_intake/` with a narrow CLI-first surface. It would read a frozen
candidate bundle and Gate C record, re-hash and revalidate both, then perform
one append-only write beneath the existing canonical Strategy Spec path
convention (`research/strategy_specs/STRAT-SPEC-NNNN.strategy_spec.json`). This
path is proposed, not implemented here.

The writer must reject overwrite, identifier collision, path traversal,
symlinks escaping the target, stale source hashes, unclean validation, approval
scope mismatch, and target/content mismatch. It must write an audit receipt and
run post-write schema/content/provenance validation. Partial failure must leave
no apparently valid canonical artifact; recovery semantics require design in
the future implementation package.

Canonical Strategy Spec status authorizes only the downstream preparation
allowed by its reviewed status. It does not create a Variant Manifest, Sweep
Plan, queue item, Result Population, candidate, ranking, recommendation,
promotion, readiness, or execution authority.

## 6. Queue admission

The exact Gate-Q and append-only queue-item contract is now locked in
`docs/architecture/canon_queue_control_plane.md`; that contract controls the
queue layout, bounded vocabularies, hash scopes, and no-dispatch semantics.

Queue admission occurs only after canonical Strategy Spec creation and separate
human-reviewed preparation of a hash-pinned Variant Manifest and Sweep Plan.
The existing schemas and validators remain authoritative; this design changes
none of them.

Gate Q must bind Karl's exact-content approval to:

- canonical Strategy Spec path/hash;
- Variant Manifest path/hash and exact variant denominator;
- Sweep Plan path/hash, validation methods, trial accounting, and result-capture
  expectations;
- immutable data identities/time ranges and realism assumptions;
- a bounded compute budget (maximum variants, trials, wall time, CPU/memory or
  repo-approved resource units, and retry policy);
- explicit priority selected by a human from a future bounded vocabulary;
- exact queue item identifier and offline output root;
- no automatic expansion, retry beyond budget, successor creation, or dispatch;
- false authority flags for candidate promotion/readiness and all paper/live,
  runtime, scheduler/autonomy, notification, broker/exchange, OMS, risk,
  reconciliation, and safe-mode actions.

The conceptual queue item contains identity/version, the Gate Q record,
Spec/Manifest/Plan refs and hashes, dataset refs, denominator, budget, priority,
requested-by/approved-by, admission timestamp, blocked prerequisites, and
non-authority flags. It is an offline research work request only.

Admission is a write to a queue, not execution. No scheduler or autonomous
dispatcher is authorized. A later explicitly authorized operator command may
select an admitted item for offline execution, and the execution surface must
revalidate hashes, approval, budget, data, and prerequisites. Gate C cannot
substitute for Gate Q, and Gate Q cannot substitute for any runner-specific
execute approval repo truth requires.

Traceability is mandatory and bidirectional:

```text
idea/source -> scratch draft -> review/clarification history
-> Gate C frozen bundle and approval -> canonical Strategy Spec
-> Variant Manifest -> Sweep Plan -> Gate Q and queue item
-> execution/run identity -> Result Population -> candidate-review package
```

No Result Population automatically creates or promotes a candidate. Candidate
review and any canonical crossing remain separate Karl/Main-gated processes.

## 7. Authority state model

| State | What it authorizes | What it does not authorize |
|---|---|---|
| Scratch draft | Human review, clarification, discard, or annotation. | Canonical writing, queueing, execution, evidence, candidate action. |
| Reviewed scratch draft | Records that content was inspected and findings exist. | Passing validation or any downstream write. |
| `flagged_for_canonicalization` | Routing/attention annotation only. | Generation, approval, canonicalization, queueing, execution. |
| Karl-approved canonicalization package | Exactly one append-only Gate C write of the hash-bound Strategy Spec. | VM/Sweep creation, queueing, execution, evidence, candidate action. |
| Canonical Strategy Spec | Canonical declarative repo truth; downstream human-reviewed planning according to status. | Execution, queueing, evidence, candidate/promotion/readiness authority. |
| Sweep Plan / Variant Manifest | Frozen bounded test population and plan when separately approved. | Admission, execution, budget expansion, evidence, candidate action. |
| Research queue item | A bounded offline request eligible for later operator-controlled handling. | Automatic dispatch, scheduler/autonomy, paper/live/runtime, promotion. |
| Result Population | Canonical or package-authorized result evidence with full denominator and lineage. | Edge certainty, ranking, recommendation, candidate creation/promotion. |
| Candidate review package | Presents evidence, caveats, blockers, and questions to a human gate. | Candidate crossing, promotion, readiness, paper/live/runtime action. |

Authority changes only at Gate C (one canonical Spec write), Gate Q (one bounded
queue admission), separately authorized execution, canonical Result Population
write, and separately governed candidate decisions. State names or UI display
must not blur these boundaries.

## 8. Fail-closed behavior and escalation

Stop without writing when any required source is missing, malformed, mutable,
unhashed, stale, ambiguous, unsupported, or inconsistent; when validation or
duplicate checks are incomplete; when approval is absent, broad, wrong-owner,
wrong-scope, or hash-mismatched; when the target exists; or when a requested
action crosses protected scope.

Stop and escalate to Karl/Main if:

- any proposed UI action would itself grant approval or write canonical truth;
- the proposed gate is weaker than current Karl exact-content freeze;
- schema/provenance requirements conflict with the source bundle;
- canonicalization requires a schema, validator, query, runtime, or protected
  change not explicitly authorized;
- queue admission precedes complete canonical validation or frozen sweep plan;
- duplicate status, data availability, feature semantics, or material logic
  remains unresolved;
- a future implementation cannot keep scratch intake and canonical writer
  physically and permission-wise separate.

## 9. Karl decision points

Karl must approve or reject before any implementation capsule is drafted:

1. Gate C: Karl-only exact-content approval bound to one Strategy Spec hash and
   one append-only target.
2. Gate Q: a separate Karl-only approval bound to Spec/Manifest/Plan hashes and
   a bounded budget/priority envelope.
3. UI posture: UI may display, annotate, and prepare/download review material,
   but cannot itself approve or write canonical/queue artifacts.
4. Writer placement: a separate CLI-first `tools/canonical_intake/` trust domain,
   never an extension of `tools.agent_inbox_intake`.
5. Duplicate policy: exact duplicate rejection and Karl-acknowledged,
   compute-justified near-duplicate exception.
6. Queue posture: admission does not dispatch; scheduler/autonomy remains a
   separately prohibited capability unless later authorized.

## 10. Proposed future implementation capsules

These are sequencing proposals only. They are **not draftable or authorized
until Karl approves this architecture and the relevant decision points**.

### C1. Canonicalization validator/schema package

Define the frozen candidate bundle, validation-report and Gate C schemas plus
read-only validators. Forbidden: canonical instances/writes, intake changes,
queue, execution, candidate lifecycle, UI/API, runtime/protected paths.
Validation concept: positive/negative corpus, hash canonicalization, ambiguity,
duplicate, provenance, parameter, capability, and forbidden-authority tests.

### C2. Draft-to-spec candidate generator

Generate scratch-only candidate bundles from intake packets with explicit
source-to-output diffs and clarification records. Forbidden: canonical writes,
approval creation, queue, execution, candidate lifecycle, UI/API, arbitrary
model logic, runtime/protected paths. Validation concept: deterministic fixtures,
no unsupported field synthesis, complete lineage, fail-closed unsupported ideas.

### C3. Karl exact-content freeze and canonical writer

Add the separate CLI-first Gate C approval validator and one append-only
canonical Strategy Spec writer. Forbidden: changes to Agent Inbox, VM/Sweep/RP,
queue, runner, candidate lifecycle, UI/API, paper/live/runtime/protected paths.
Validation concept: wrong actor/scope/hash/target/broad flags/stale content,
collision and partial-failure tests, post-write validator and audit receipt.

### C4. Queue admission package

Define Gate Q and bounded offline queue-item schema/validator/writer over an
already canonical, validated, hash-pinned Spec/Manifest/Plan set. Forbidden:
dispatch, scheduler/autonomy, runner changes, Result Population creation,
candidate lifecycle, UI/API, notifications, paper/live/runtime/protected paths.
Validation concept: budget/priority bounds, lineage and hash mismatch, duplicate
admission/idempotency, broad approval, and zero-dispatch proof.

### C5. Dashboard visibility package

Expose read-only status and lineage for scratch review, Gate C, canonical Spec,
Gate Q, queue, and downstream evidence. Forbidden: approve/reject buttons that
write authority, canonical/queue mutation, execution, scheduler, candidate
action, paper/live/runtime/protected paths. Validation concept: read-only route
and UI tests, honest missing/blocked state, non-authority labels, no write calls.

## 11. Non-authority

This design creates no implementation or authority. No Strategy Spec, Variant
Manifest, Sweep Plan, queue entry, Result Population, candidate record, API,
UI, scheduler, notification, runner, paper/live/runtime, OMS, risk,
reconciliation, safe-mode, config, dependency, provider, broker, exchange, or
credential surface is created or modified.
