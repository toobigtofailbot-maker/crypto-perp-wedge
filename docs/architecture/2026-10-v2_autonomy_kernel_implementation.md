# Scientific Autonomy Kernel Implementation

Package: `WP-V2-AUTONOMY-KERNEL-01`. Branch implementation under D2-026;
this record creates no new architecture decision or activation authority.

Exact base: `9d9f8a94405ded76bbef0163488b9a8e0596371a`.
Semantic head and final validation evidence are recorded in the companion
`docs/status_entries/WP-V2-AUTONOMY-KERNEL-01.md` after acceptance.

## Human envelope and control contracts

`cpw_bounded_research_envelope_v1` and
`cpw_bounded_research_envelope_control_v1` are closed JSON Schema/Pydantic
contracts. Nested policy is explicit, frozen, and rejects unknown fields.
Approval is exactly Karl with an aware timestamp. Semantic SHA-256 uses sorted,
compact ASCII JSON excluding only `content_sha256`; timestamps remain exact
strings. No operational identifier participates in envelope identity.

The envelope defines allowed instruments, venues, market types, timeframes,
families, mechanisms, sources, features and Strategy-Spec/DSL surface; exact
objectives, constraints, proposer configurations, splits and data bindings;
parameter ceilings, scientific protocol, evidence/memory/dispositions and
stop/escalation policy. All economic/protected/canonical authority flags are
explicitly false. Only synthetic fixtures are created.

Registration retains exact validated bytes/policy identity; shape alone does
not establish a usable envelope. Separate current control state supports exact
human revoke/replace records. Replacement requires a distinct registered,
active successor. Revoked/replaced state never returns to active.

The approved envelope also binds a contamination domain. A holdout identity
cannot be rebound to another domain merely by opening another campaign.

## PostgreSQL authority and writer

The logically separate `research_authority` database schema has checksum-locked
migrations and thirteen tables: envelope registry/control, campaign/search,
reservations, proposals, scientific trials/software attempts, holdout,
contamination ancestry, evidence references, audit and migration ledger.
It retains identity/accounting and exact reference hashes, never objective or
performance result payloads. Research Memory owns neither these rows nor their
migrations. Deployment credentials are outside this package.

The NOLOGIN group `cpw_research_authority_writer` is NOSUPERUSER, NOCREATEDB,
NOCREATEROLE, NOINHERIT and NOBYPASSRLS. It has schema USAGE, required SELECT/
INSERT, and guarded-state UPDATE privileges only. It cannot own/drop the
schema, disable guards, mutate unrelated stores, manage roles/databases or
write the migration ledger. Immutable tables reject UPDATE/DELETE/TRUNCATE.
Deferred constraints verify retained identities, reservations and current
audit binding at commit.

## Transactional audit, accounting and lineage

Authority writes serialize through a PostgreSQL transaction advisory lock,
then row locks. This deliberately conservative first-kernel implementation
serializes cross-campaign contamination and hypothesis reservations too.
Each accepted transaction appends one event with deterministic input, type,
campaign, sequence, previous hash, content hash and transaction timestamp.
Current campaign version/hash points to the last event. Database guards and
recovery reads reject discontinuity; exact idempotency replays do not append
new events and conflicting input fails closed. Audited outcomes retain the
original accounting/holdout snapshot without a self-referential lineage hash;
replay restores that event's version/hash, even after later transactions.
Current authority is always read separately from the durable current state.
Input and proposal replay comparisons use canonical JSON, preserving numeric
and boolean types; mathematical equality cannot substitute for exact identity.

Search open reserves local proposal/trial ceilings before returning its frozen
contract. Campaign used plus reserved cannot exceed its immutable ceilings.
Hypothesis usage plus reservations are aggregated across campaigns under the
same envelope, using Governor hypothesis fingerprints, including finalized
searches. A successor requires the exact finalized parent in the same campaign.
Conflicting successor opens have one legal winner. Search finalization closes
its authority reservation and releases unused ceilings; it does not fabricate
Governor results or scientific conclusions.

The store verifies deterministic Governor wave replay and retains all charged
proposals, including rejected/duplicate records, plus accepted scientific-trial
identities. Software attempts retain an existing trial ID and do not increase
the independent denominator. They cannot exceed the frozen retry limit.

## CPW contract construction and continuation

The strict request contains proposed local selections and policy, with no
cumulative history, remaining budget, lineage or freshness fields. The CPW
builder validates accepted-intent semantic/fingerprint identity, exact Git
HEAD, envelope identity, metadata path bytes/hashes, approved surface, exact
policy and numerical/domain subsets. It opens the search transactionally from
the durable snapshot; caller-authored cumulative values are never accepted.

Frozen `SearchContract` now requires envelope ID/version/hash, contamination
domain, authority lineage version/hash, and retains DB-derived cumulative
counts. All fields enter the existing serialized contract hash. Historical
pilot/test successor behavior remains explicit fixture behavior; no autonomy
module uses it. Search Governor and Optuna keep their existing ownership.

The kernel rejects missing authority and exhausted budgets. Compute/runtime,
concurrency and recovery requests must fit explicit envelope limits; this
package executes no scientific job, compute scheduler or product runner.

## Holdout and contamination

Only opaque synthetic identities are used. `unexposed -> attempted_isolated`
does not consume information. Informative escape atomically records consumed
state, exact source search/campaign/domain, ancestry and audit. No consumed
state can be restored. Any informative escape contaminates the bound domain;
later builders fail closed even with a new search/campaign/operational ID.
There is no machine-declared isolation exception and no holdout data reader.

## Active handoff and restart

The existing storage resolver owns deterministic, contained, gitignored paths
under `.cpw/active/research-autonomy/`. Atomic publication binds exact contract,
repo/intent/envelope identities, durable lineage, finalized pre-wave snapshot,
all proposal records/IDs/fingerprints and resulting denominator. It explicitly
denies approval, execution, canonical, candidate and economic authority.

Recovery first verifies current repo/evidence, exact active envelope/search,
retained DB proposals and lineage. It reconstructs the exact stored contract,
restores the finalized pre-wave snapshot and calls `propose_wave()` once.
Proposal order/parameters/IDs/fingerprints/hash/denominator must match exactly.
Performance-bearing snapshots are denied rather than copied into handoffs;
this proposal-only package creates no result-recovery path. Deleting `.cpw`
cannot modify any authority row.

Physical acceptance separately rebuilds Research Memory through its unchanged
migration/repository path, then proves authority rows, cumulative history,
lineage and holdout consumption survive. The two test DSNs resolve to different
loopback logical test databases; connection strings are not evidence artifacts.

## Acceptance and boundary

Cases A-K and focused, adjacent, live PostgreSQL, validator and full-release
results are recorded at the committed semantic head in the companion status
entry. Pending validation is not acceptance.

No Stage 5B or autonomous research activation, Hermes/Prefect coupling,
product runner/backtest/WFO-OOS/robustness/Monte Carlo, real final-holdout access,
Result Population/canonical write, candidate/promotion, protected runtime/risk/
OMS/reconciliation/overlay/safe-mode, paper/live/exchange/order or capital
authority is gained. The next separately authorized dependency is
`V2-RESEARCH-FACTORY-LOOP-01`; Side 22 exact-head review remains required.
