# Search Policy and Proposal-Wave Handoff Lock

## 1. Status and authority

- Status: **LOCKED ARCHITECTURE / DECISION ONLY**.
- Package: `WP-V2-INTEGRATION-01B-ARCH-01`.
- Decision: `D2-023 — Search Policy Binding and Proposal-Wave Handoff`.
- Base: `f2dbcb73a25d5ce271a29915b54ae6647aee5570`.
- Authority class: documentation and architecture only.

This record locks the remaining inputs and recovery boundary required before a
separately authorized V2-INTEGRATION-01B implementation may be drafted. It
implements no policy model, builder, schema, validator, storage writer,
Prefect flow, Governor integration, Optuna operation, runner, or result path.

## 2. Repo-truth basis

At the locked base, V2-INTEGRATION-01A is merged through PR #729 and its
`BoundedResearchIntent v1` handoff is physically proven. D2-020 requires
cumulative scientific history across amendments and follow-ups, while D2-022
reserves intent-to-`SearchContract` conversion to CPW and requires fresh 01B
dependency research. The long-term durable cumulative scientific-lineage store
remains open.

The existing Search Governor owns proposal legality, scientific-trial identity,
budgets, duplicate and retry meaning, final-holdout denial, and bounded
snapshot/restore. Its current snapshot contract permits snapshots only at a
finalized wave boundary. Optuna 4.9.0 is proposal-only behind the Governor,
Prefect 3.8.6 is operational-only, and `.cpw/active/` is the approved
noncanonical active/provisional workspace. The governed pilot's hard-coded
fixture contract is evidence of one engineering proof, not a generic policy
source.

## 3. Decision A — `SearchPolicyBinding v1`

`SearchPolicyBinding v1` is a strict CPW-owned logical object that supplies
every authoritative scientific-policy field required to convert an accepted
`BoundedResearchIntent v1` into a frozen `SearchContract`.

For the pre-Stage-5B path, a human supplies this explicit manual input and CPW
validates it strictly. It is not model-generated policy, Prefect policy, or
Optuna policy.

### Identity and lineage

- schema version and policy-binding ID;
- exact repo SHA and exact source-intent content hash;
- campaign ID and search ID;
- `parent_search_id = null`;
- `reason_for_change = null`.

### Strategy binding

- exact Strategy-Spec ID and content hash;
- exact strategy family and hypothesis identity consistent with the accepted
  intent.

### Data binding

- exact development-data identity and version;
- exact split-protocol ID and development-data reference/window;
- opaque final-holdout reference;
- final-holdout access fixed to prohibited.

### Search legality

- legal parameter space;
- conditional rules and relational constraints;
- forbidden regions;
- objective and scientific constraints.

### Budgets and execution shape

- maximum proposals and maximum scientific trials;
- wave size and concurrency;
- seed.

### Proposer

- backend;
- exact Optuna version;
- proposer configuration.

### Policies

- duplicate policy;
- invalid-proposal policy;
- failed-software retry policy;
- performance-result classification;
- pruning policy;
- retry limit;
- stop rule.

### Cumulative fields

For the first 01B generation only:

```text
campaign_proposals_before_search = 0
campaign_scientific_trials_before_search = 0
```

The binding must reject nonzero values.

`SearchPolicyBinding v1` creates no canonical-write, candidate/promotion,
runner, final-holdout, scheduler/autonomy, runtime/risk, paper/live, or capital
authority.

## 4. Decision B — first 01B is new-campaign-only

Until a durable CPW cumulative scientific-lineage surface exists, the first
01B implementation is limited to a brand-new campaign and search:

```text
parent_search_id = null
reason_for_change = null
campaign_proposals_before_search = 0
campaign_scientific_trials_before_search = 0
```

Child or successor searches, amendments, older-campaign resume, imported
historical proposal or scientific-trial counts, and budget reset by rename or
restart are forbidden. `.cpw`, Prefect, Hermes, Research Memory, and a new
search ID are not durable cumulative lineage. Any history-bearing campaign
requires the future durable lineage surface or another explicit reviewed
architecture decision.

## 5. Decision C — CPW intent-to-contract ownership

The future deterministic CPW builder takes exactly:

```text
accepted BoundedResearchIntent v1
+ validated SearchPolicyBinding v1
+ exact repo evidence
-> frozen SearchContract
```

It must fail closed on an intent/policy repo-SHA mismatch, intent-hash mismatch,
strategy identity or Strategy-Spec hash mismatch, data-identity mismatch,
parameter-space widening beyond validated policy, any missing field, nonzero
cumulative history, parent/successor identity, or holdout-policy violation.

Hermes reasoning may inform a human policy author's decision, but cannot fill
or override policy fields. Prefect run IDs and Optuna defaults cannot supply
missing scientific policy.

## 6. Decision D — `ProposalWaveHandoff v1`

`ProposalWaveHandoff v1` is a CPW-owned noncanonical object carrying enough
scientific state to re-establish one active Governor proposal wave across a
Prefect or process restart before the real product runner exists.

It must contain:

- schema version and exact repo SHA;
- source `BoundedResearchIntent` hash;
- source `SearchPolicyBinding` hash;
- exact frozen `SearchContract` and its exact hash;
- exact finalized **pre-wave** Governor snapshot;
- exact requested wave count;
- exact proposal records generated from that snapshot;
- exact proposal IDs and scientific-trial IDs;
- exact proposal parameter fingerprints;
- exact scientific denominator after proposal generation;
- deterministic handoff content hash;
- explicit noncanonical and non-authority flags.

It must not contain a runner result, performance value, winner or best-trial
status, candidate status, final-holdout result, canonical-write authorization,
or promotion, live, or capital authority. It is not canonical evidence, a
Result Population, a trial-result store, or an approval.

## 7. Decision E — noncanonical storage

The future 01B implementation may persist `ProposalWaveHandoff v1` only beneath
`.cpw/active/` through the existing safe CPW storage resolver. Its namespace
and filename are deferred implementation details, but must be deterministic,
contained, gitignored, and noncanonical, and must not create a queue or outbox
authority.

File presence is not validity. A later consumer must validate schema, hashes,
and bindings. No canonical research path is authorized.

## 8. Decision F — active-wave recovery

Because the Governor cannot snapshot an active wave, recovery uses the last
valid finalized pre-wave snapshot:

1. Load and validate `ProposalWaveHandoff v1`.
2. Rebuild the exact frozen `SearchContract`.
3. Restore Search Governor from the embedded pre-wave snapshot.
4. Call `propose_wave()` exactly once with the recorded wave count.
5. Require exact deterministic equality with the recorded proposal order,
   proposal IDs, scientific-trial IDs, parameter values, parameter
   fingerprints, contract hash, and resulting scientific denominator.
6. Only after equality is proven, re-establish the active wave in memory.
7. Fail closed on any divergence.

Recovery must not mint a different wave, silently advance Optuna, change a
budget or search identity, change scientific-trial identity, or interpret a
Prefect retry as permission for a new wave.

## 9. Decision G — creation sequence

The future 01B implementation sequence is:

```text
validated 01A intent
-> validated SearchPolicyBinding v1
-> frozen SearchContract
-> initial/finalized pre-wave Governor snapshot
-> propose one bounded wave
-> build ProposalWaveHandoff v1
-> atomic noncanonical write under .cpw/active
-> verify replay/recovery equality
-> STOP before product runner
```

No runner result is submitted. The active wave remains intentionally
incomplete for the later runner bridge.

## 10. Decisions H and I — ownership

| Owner | Owns | Does not own |
| --- | --- | --- |
| Human policy author + CPW validation | Explicit pre-Stage-5B `SearchPolicyBinding v1` input and validation. | Model-generated defaults, runtime, promotion, live, or capital authority. |
| CPW intent-to-contract builder | Deterministic accepted-intent + validated-policy + exact-evidence conversion to the frozen contract. | Policy invention or operational-ID defaults. |
| Prefect | Manual flow invocation, task/run history, worker queueing, operational restart, and operational failure state. | Binding values, contract policy, proposal/trial identity, scientific denominator, retry authorization, or holdout state. |
| Search Governor | Contract enforcement, proposal legality/accounting, scientific-trial IDs and denominator, duplicate/retry semantics, final-holdout denial, and snapshot/restore. | Product-runner, candidate, promotion, paper/live, or capital authority. |
| Optuna | Capability-gated proposal generation behind the Governor. | Scientific policy, direct Hermes/Prefect control, winner/GO/promotion, or readiness meaning. |

A Prefect retry may call `propose_wave()` only while executing the locked exact
recovery algorithm against the same validated handoff. Direct Hermes ->
Optuna, Prefect -> Optuna, and policy-binding -> raw Optuna control paths are
forbidden.

## 11. Scientific and operational identity separation

Hermes sessions and Prefect flow/task/run IDs are operational identities only.
The frozen CPW contract owns campaign/search identity. Search Governor owns
proposal IDs, scientific-trial IDs, and denominator accounting. Restart or
retry cannot translate an operational identity into scientific identity,
policy, budget, or lineage authority.

## 12. Decision J — 01B stop boundary

The later 01B implementation must stop after one frozen `SearchContract`, one
bounded proposal wave, one validated `ProposalWaveHandoff v1`, and proven
deterministic recovery/replay exist.

It must not execute a product runner, backtest, WFO/OOS, robustness, Monte
Carlo, final holdout, result submission, wave finalization, candidate review,
promotion, canonical write, Stage 5B, autonomous scheduling, paper/live, or
capital action.

## 13. Decision K — durable lineage remains deferred

This lock does not solve D2-020's long-term durable scientific-lineage store.
That surface remains required before generic campaign continuation,
amendments, child searches, cross-search cumulative accounting, holdout-
contamination ancestry, or Stage 5B autonomous research.

The new-campaign-only restriction avoids that unresolved dependency for the
first 01B proof. No `.cpw` handoff may later be reclassified as durable lineage
authority without another explicit reviewed architecture decision.

## 14. Protected and non-authority boundaries

This lock changes no Python, dependency, config, schema, validator, query,
Research Memory, Hermes, Prefect, Search Governor, Optuna, Strategy Spec, data,
runner, canonical evidence, candidate lifecycle, runtime, OMS,
reconciliation, risk, overlay, safe mode, paper/live, exchange/order,
credential, or capital surface.

It grants no Stage 5B, autonomous research, runner, canonical-write,
candidate/promotion, runtime/risk, paper/live, or capital authority. This
package implements nothing.
