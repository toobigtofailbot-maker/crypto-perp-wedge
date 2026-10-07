# Scientific Autonomy Kernel Durable Authority and Storage

## 1. Status and controlling authority

- Status: **LOCKED ARCHITECTURE / DECISION ONLY**.
- Package: `WP-V2-AUTONOMY-KERNEL-ARCH-01`.
- Decision: `D2-026 — Scientific Autonomy Kernel Durable Authority and Storage`.
- Approval: Karl, 2026-10-07, through the executable docs-only package.
- Exact base: `200276fd4407e4a13a912a6b475ab9ab38a1de70`.
- Authority class: T0 documentation / architecture / process-policy only.

On accepted merge, this record controls the future autonomy kernel's durable
authority and storage design. It closes D2-020's deferred backend selection
without changing its scientific policy or Stage 5B gate. D2-019 ownership,
D2-021 data identity, D2-022 handoff ownership, D2-023 proof controls, and
D2-024/D2-025 capability and orchestration boundaries remain intact.

Statements labeled **Architecture fact** describe inspected merged truth.
**Locked decision** identifies the approved future design. **Deferred
implementation detail** requires the later executable WP. **Future option**
is not implementation or activation authority.

## 2. Problem being closed

**Architecture fact:** D2-020 requires CPW-owned durable cumulative lineage and
final-holdout state but deliberately chooses no schema, path, backend, or
writer. D2-023's manual `SearchPolicyBinding v1`, new-campaign-only/zero-history
restriction, and noncanonical `ProposalWaveHandoff v1` avoid that unresolved
dependency; they do not solve it. Generic continuation and contamination
ancestry remain deferred.

PR #733 / `WP-EXTREME-HERMES-01` is merged at the exact base. Its F1/F2
capability proof is complete, with F1/F2 stopped and F0 rollback proven. Broad
Hermes capability creates no scientific execution authority. D2-024/D2-025
place the scientific autonomy kernel next, before product-loop integration and
Stage 5B activation.

**Locked decision:** choose durable scientific authority explicitly before
drafting `V2-AUTONOMY-KERNEL-01`; implementation may not silently choose it.

## 3. Existing proof primitives retained

**Architecture fact:** `tools/research_search/contract.py` defines frozen
campaign/search/parent identities and cumulative proposal/trial fields. Its
caller-side `successor(...)` accepts observed counts; that is existing proof
behavior, not the future production continuation source.

`tools/research_search/governor.py` owns proposal legality/accounting,
scientific-trial identity and denominator, duplicate/retry meaning, final-
holdout denial, and finalized-wave snapshot/restore. The Optuna adapter is
capability-gated and proposal-only. `BoundedResearchIntent v1` remains a strict
non-authoritative reasoning/evidence handoff, not approval or execution input
by itself. D2-022's inert H2/H2.5 boundaries remain in force.

**Locked decision:** retain these ownership primitives; the kernel supplies
durable campaign authority without becoming a second search-legality owner.
No existing proof behavior is changed by this document.

## 4. Human-owned immutable envelope

**Locked decision:** the future production envelope is a CPW repo artifact in
the family `research/autonomy/envelopes/`, validated against a future strict
schema family under `research/schemas/`. Each envelope is versioned, immutable,
content-hash bound, and binds exact repo identity and explicit human/Karl
approval metadata.

Karl owns approval, revocation, replacement, and material change. Automation
may read and validate an envelope, but may not create, edit, expand,
reinterpret, replace, or self-authorize one. Replacement or revocation creates
explicit new human-controlled state, never in-place policy mutation. Campaign
scope, ceilings, scientific policy, and bounded recovery remain envelope-owned.

**Deferred implementation detail:** exact schema, artifact filenames, approval
and revocation representation, and validation APIs belong to the executable
kernel WP. That WP may use test fixtures only. This package creates no schema
or envelope instance. A real approved production envelope becomes operational
only at the later explicit Stage 5B activation boundary.

## 5. PostgreSQL durable authority backend

**Locked decision:** the autonomy kernel uses a new CPW-owned PostgreSQL
scientific-authority database, logically separate from rebuildable Research
Memory. A separate logical database, separate migrations, and separate write
role are mandatory. Research Memory deletion/rebuild cannot delete, reset, or
redefine scientific history. Hermes, Prefect, and broker state cannot become
scientific lineage authority.

Recommended later database/role name family: `cpw_research_authority`.
Recommended schema family: `research_authority`.

**Architecture fact:** Research Memory and Hermes broker migration runners
already use checksum-locked SQL migrations, transactions, and DB constraints.
These are repo idioms, not existing kernel authority or permission to extend
those stores.

**Future option:** reuse the same physical PostgreSQL server/cluster while
preserving mandatory logical separation. **Deferred implementation detail:**
deployment credentials, host, port, grants, and connection configuration are
environment configuration, not scientific identity. No database is created here.

## 6. Durable lineage/accounting model

**Locked decision:** use transactional authoritative current state plus
append-only audit/event history, deterministic IDs and content hashes,
DB-enforced uniqueness/check constraints, atomic budget/state transitions,
and fail-closed idempotency/conflict handling.

Minimum future authority domains are:

- envelope registration/binding;
- campaign lineage and search lineage;
- scientific-trial identity/history;
- cumulative proposal/trial accounting;
- exact evidence/result references and hashes;
- holdout state and contamination-domain state;
- contamination ancestry;
- append-only authority audit.

The store durably preserves Governor-owned scientific identity/accounting;
it does not independently redefine what counts as a proposal or trial.
**Deferred implementation detail:** tables, indexes, transition/API contracts,
writer implementation, migration paths, and transaction strategy belong to
the executable WP. No universal event-sourcing framework is required or locked.

## 7. Scientific evidence boundary

**Locked decision:** the database owns scientific identity, lineage,
cumulative accounting, holdout state, and exact evidence/result references and
hashes. It must not become a second performance/result warehouse.

Existing/future CPW scientific evidence and Result Population surfaces retain
scientific payload semantics, complete-population meaning, and their existing
canonical gates. A stored reference is not permission to create a payload or
cross a canonical boundary. No candidate or promotion authority is created.
D2-021's canonical base/feature-parent identity remains unchanged.

## 8. `.cpw/active` non-authority

**Architecture fact:** `tools/research_storage/workspace.py` resolves contained
active/provisional `.cpw/active` and disposable `.cpw/ephemeral` workspace state.
D2-023's handoff is noncanonical and not durable lineage.

**Locked decision:** `.cpw/active` remains active/provisional only.
`ProposalWaveHandoff`-equivalent state may support in-flight recovery, but must
bind exact authoritative campaign/search/contract/lineage identity. Deletion
or recreation of `.cpw` cannot erase or reset scientific history. File presence
never creates authority; a workspace copy cannot override the authority store.

## 9. Envelope-derived SearchContract construction

**Locked decision:** a CPW-owned deterministic production builder takes:

```text
accepted BoundedResearchIntent
+ exact valid Karl-approved envelope
+ exact repo/evidence identity
+ authoritative durable-lineage state
-> frozen SearchContract
```

The future contract binds at least envelope ID, version, and content hash;
contamination-domain identity; authoritative lineage state/version/hash; and
authoritative cumulative proposal/trial counts, alongside existing exact
scientific policy/evidence bindings.

Hermes, Prefect, and Optuna may not supply or override cumulative counts,
remaining campaign budget, holdout freshness, envelope policy, scientific retry
semantics, or parameter/search-space widening. Missing, stale, conflicting, or
invalid authoritative input fails closed. Direct caller-supplied cumulative
history is not the production continuation path.

**Deferred implementation detail:** the builder and frozen-contract extension
are implemented only by the later authorized kernel WP. This decision does not
enable a consumer of the current non-authoritative intent.

## 10. Successor/generalized continuation

**Locked decision:** a legal successor requires exact campaign and parent
search identity, reason for change, exact parent lineage, authoritative
cumulative history, revalidation against the immutable envelope, and a new
frozen `SearchContract`. Rename, restart, or a new operational ID cannot reset
budgets. Parameter/search domains cannot widen outside the envelope.

Search Governor remains the search-legality/scientific-trial owner; Optuna
remains proposal-only. Durable continuation must preserve full applicable
scientific history rather than only the surviving child search.

D2-023's manual/new-campaign-only/zero-history path remains the existing proof
restriction until a separately authorized, validated kernel implementation
provides the replacement. This docs lock does not enable successors now.

## 11. Final-holdout and contamination semantics

**Locked decision:** final holdout remains unavailable to adaptive search.
Informative exposure is durably recorded. If informative holdout-derived
information escapes isolation, that holdout is consumed; consumption propagates
to influenced downstream lineage in the same contamination domain.

A new hypothesis, search, branch, Hermes session, Prefect run, or Research
Memory record cannot restore freshness. Exact operational retry may avoid
another exposure only when no informative result escaped. Absence of a
contamination edge is not proof of strict information isolation. Holdout
result -> adaptation -> same-holdout retest loops remain forbidden.

The first kernel must not implement an automatic machine path that declares
strict information isolation and restores freshness. **Future option:** any
isolation exemption requires a separate reviewed architecture/authority
decision; it is not an implementation discretion under this lock. D2-020's
scientific protocol and gate semantics remain intact; no threshold is invented.

## 12. Cumulative budget semantics

**Locked decision:** the human-approved envelope defines campaign ceilings.
The durable CPW authority store owns atomic usage/reservation; search-local
budget must fit remaining campaign/envelope budget. Concurrent starts cannot
oversubscribe the campaign.

The Governor retains proposal/trial legality and accounting meaning.
Same-scientific-trial software retry does not mint another independent trial.
Successor search, new ID, or restart cannot reset totals. Budget expansion
requires human envelope replacement/expansion through explicit new state.
Hermes, Prefect, and Optuna do not own remaining-budget truth.

**Deferred implementation detail:** concurrency control and reservation
transitions must prove these invariants in the later kernel WP.

## 13. Ownership matrix

| Surface | Owner |
| --- | --- |
| Research scope, budget and scientific policy | Karl-approved immutable envelope |
| Envelope validation/binding | CPW autonomy kernel |
| Durable lineage/cumulative history | CPW autonomy kernel |
| Holdout contamination/consumption | CPW autonomy kernel |
| Search legality/proposal/scientific-trial identity | Search Governor |
| Proposal generation | Optuna behind Governor |
| Research reasoning / proposed next action | Hermes |
| Operational flow/run/retry | Prefect |
| Retrieval/dedup context | Research Memory, non-authoritative |
| Scientific evidence payloads | Existing/future CPW evidence surfaces |
| Candidate promotion | Human-gated lifecycle |
| Protected runtime / OMS / reconciliation / hard risk | Existing protected owners |

## 14. Crash/restart/idempotency direction

**Locked decision:** authoritative budget/state transitions are atomic and
durable with append-only audit history. Deterministic IDs, exact content
bindings, and DB constraints must prevent duplicate scientific effects.
Conflicting identity/content, missing authority, or irreconcilable state fails
closed; operational recovery cannot manufacture new scientific authority.

Restart recovers against exact durable lineage and the frozen contract.
Provisional wave recovery preserves Governor-owned identity and exact replay
semantics, without treating a Prefect retry as a new proposal permission.
**Deferred implementation detail:** exact crash points, write/replay ordering,
idempotency keys, and recovery tests belong to the executable WP. No recovery
algorithm or writer is implemented by this lock.

## 15. Research Memory / Prefect / Hermes non-authority

**Architecture fact:** Research Memory explicitly stores a rebuildable index
and mutable non-authoritative context; repo-backed conclusions require exact
evidence re-resolution. Prefect's merged consumer cutover owns operational
flow/run history, not scientific identity or holdout meaning.

**Locked decision:** Research Memory may mirror/index/retrieve authority
history but cannot define, erase, or reset it. Hermes reasoning, memory,
sessions, Bots, and skills remain non-authoritative. Prefect run/task/retry
history and broker state remain distinct from scientific authority. D2-025's
Hermes intelligence wake-ups and Prefect durable workflow ownership do not
transfer scientific truth or activate autonomous schedules.

## 16. Future implementation boundary

**Deferred implementation detail:** after accepted merge and refreshed repo
truth, Side 22 may draft the separately authorized executable
`V2-AUTONOMY-KERNEL-01` covering the schema, fixture-only envelope, separate
authority database/migrations/write role, durable state, contract builder,
continuation, and validation. This record is architecture authority, not an
executable implementation package.

This decision does not implement the database, envelope schema, or autonomy
kernel, create a production envelope, schedule research, allow Hermes to
execute scientific experiments, call a runner/backtester, perform WFO/OOS or
robustness/Monte Carlo, write Result Populations, or promote candidates.

## 17. Stage 5B boundary

**Locked decision:** no Stage 5B activation occurs here or merely because a
kernel later exists. Stage 5B must be implemented, validated, explicitly
activated, and bound to a valid Karl-approved immutable production envelope.
Until that later boundary, current per-hypothesis and default-off restrictions
remain operational; no open autonomous research execution is authorized.

## 18. Protected/economic non-authority

**Locked decision:** no protected runtime/risk/OMS/reconciliation change,
paper/live enablement, exchange/order authority, or capital allocation occurs.
Hard risk caps, bounded overlay semantics, safe mode/kill switch, paper
accounting, canonical writers/crossings, candidate lifecycle, protected
recovery/reset, credentials, and human promotion/economic gates remain intact.
The package grants no envelope execution, scientific execution, Governor call,
autonomous scheduling, final-holdout access, candidate/promotion, protected
runtime/risk, paper/live, exchange/order, or capital authority.

## 19. Expected validation class for the later implementation

**Locked decision:** this package is T0; validate docs-only plus exact scope,
changed-file inspection, and authority preservation. It is not evidence that
the future implementation works.

**Deferred implementation detail:** Side 22 must classify the executable
kernel's actual schema/contract/production changes under current repo tiers
(at least T2 where applicable; T3 for any authorized protected writer/crossing).
Its required validation must prove strict envelope/hash/repo/approval binding,
DB role and migration separation, atomic concurrent budget enforcement,
durable lineage and same-trial retry, exact successor continuation,
contamination propagation, conservative holdout denial, crash/restart and
idempotency/conflict behavior, `.cpw` deletion and Research Memory rebuild
non-reset, evidence-reference integrity, and zero activation. Focused/adjacent
tests, affected validators/integrity checks, physical PostgreSQL proof, and
broader validation follow the later package's actual scope and current policy.
No tests, schemas, thresholds, or protected crossing are authorized here.

## 20. Roadmap continuation

```text
EXTREME-HERMES-01 F1/F2 proof (merged, no scientific activation)
-> WP-V2-AUTONOMY-KERNEL-ARCH-01 / D2-026 (this docs-only lock)
-> accepted merge + Side 22 refreshed exact-head truth
-> separately drafted/authorized V2-AUTONOMY-KERNEL-01
-> V2-RESEARCH-FACTORY-LOOP-01
-> EXTREME-HERMES-02 / explicit Stage 5B + valid production envelope
-> later EXTREME-HERMES-03 and human-gated economic progression
```

**Locked decision:** the executable kernel remains blocked until this decision
merges. Accepted merge allows Side 22 to draft it against refreshed repo truth,
not to assume it is already executable. D2-024/D2-025 remain controlling for
the wider roadmap and capability gates. Every downstream package needs its own
explicit scope, authorization, and validation.
