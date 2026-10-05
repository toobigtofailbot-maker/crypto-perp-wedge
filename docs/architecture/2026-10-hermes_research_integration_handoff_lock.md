# Hermes Research Integration Handoff Lock

## Status and purpose

- Status: **LOCKED / DOCUMENTATION-ONLY**.
- Package: `WP-V2-INTEGRATION-01-ARCHITECTURE-LOCK-01`.
- Decision: `D2-022`.
- Effective base: `a295299cb18ca247c14114cd9f06f7b4e29c90c5`.
- Purpose: lock the first bounded Hermes-to-Prefect operational invocation and
  the CPW-owned boundary from Hermes reasoning through Research Memory context
  to a later frozen `SearchContract`.

This record implements no code, invokes no service, and grants no execution,
canonical-write, scheduler, research-autonomy, runtime, paper/live, or capital
authority. V2-INTEGRATION-01A and 01B remain separate future implementation
packages.

## Authority and ownership

| Owner | Owns at this boundary | Does not own |
| --- | --- | --- |
| Hermes | One bounded reasoning turn, research reasoning content, session mechanics, and typed tool invocation. | Evidence truth, scientific policy, `SearchContract`, search legality, budgets, holdout state, trial identity, approval, promotion, runtime, or capital. |
| Project-Evidence / CPW | Exact repo/evidence resolution, strict handoff validation, `hypothesis-v1` normalization, exact read-only dedup lookup, and repo/evidence binding. | Autonomous scheduling, approval, promotion, trading, or capital. |
| Research Memory | Exact-match index, retrieval, deduplication, and context. | Canonical truth, scientific denominator, cumulative lineage, freshness, performance-prior, candidate, execution, or promotion authority. |
| CPW intent-to-contract builder | Future deterministic conversion of an accepted intent plus explicit CPW policy/evidence/lineage into a frozen `SearchContract`. | Defaults inferred from model or operational identifiers. |
| Search Governor | Frozen-contract enforcement, proposal legality, budgets, duplicate meaning, scientific trial identity, retry meaning, holdout denial, and snapshot/restore. | Promotion, paper/live, runtime, or capital authority. |
| Optuna | Capability-gated proposal generation behind the Governor. | Scientific policy, direct control, winner/GO/promotion, or readiness meaning. |
| Prefect | Operational task/flow invocation, run state/history, process-worker execution, and operational recovery. | Scientific identity, denominator, policy, holdout legality, or `SearchContract` construction. |
| Humans | Existing approval, promotion, protected-runtime, live, and capital decisions. | No automation may manufacture or infer these decisions. |

## Repo-truth dependency basis

At the locked base:

- Hermes remains pinned to
  `nousresearch/hermes-agent:v2026.8.13@sha256:68e15ae2a6d894d0ccbd9f8aacbbe13d4d28fa5dc9b6a303970b67bb2499b1a6`.
  Its command is `gateway run --no-supervise --external-supervisor`; it has no
  repository mount, no host-published project port, and Project-Evidence is its
  sole CPW MCP surface. Shell, terminal, file, code-execution, browser, network
  search, delegation, and equivalent escalation toolsets remain disabled.
- The exact pinned upstream CLI supports `hermes chat -q` one-shot
  non-interactive use, `--quiet` programmatic output, and `--source tool`.
- `hypothesis-v1` remains the exact deterministic Research Memory fingerprint.
  `ResearchMemoryRepository.has_this_been_tried(...)` exists, while Hermes's
  current MCP surface exposes only alias/name lookup. The Hermes database role
  is DB-enforced read-only, and repo evidence must re-resolve exactly before a
  repo-backed conclusion is current.
- `SearchGovernor` remains sole owner of the frozen contract, legality,
  budgets, final-holdout denial, scientific trial identity, duplicate/retry
  meaning, and bounded snapshot/restore. Optuna 4.9.0 remains behind its
  capability boundary. The pilot still constructs an engineering-fixture
  contract for `STRAT-SPEC-0007`; it is not a generic intent-to-contract
  builder.
- CPW-PREFECT-02 / PR #727 is merged as the first real Prefect consumer
  cutover. Its topology is the accepted PostgreSQL-backed server, deployment,
  process work pool, and process worker. It added no schedule or trigger.
  Operational run/retry identity remains distinct from scientific identity.
- `SearchGovernorCampaignPreparedPayload` still fixes
  `governor_call=false`; `PrefectWorkflowPreparedPayload` fixes
  `prefect_call=false`, `deployment_creation=false`, and
  `workflow_run=false`. Tests prohibit prepared-payload consumers across the
  Governor, Prefect, runner, canonical/control-plane, and protected surfaces.

## Decision A — first HERMES-02 invocation mechanism

The first bounded V2 proof uses a **CPW-owned fixed-command host-side
invocation adapter** under Prefect operational control:

```text
Prefect process-worker task
-> CPW fixed-command Hermes invocation adapter
-> existing pinned Hermes container
-> one non-interactive Hermes reasoning turn
-> Project-Evidence MCP only
-> strict returned CPW handoff validation
```

The adapter may use the host's existing Docker/Compose control plane to invoke
the pinned container. It must use a subprocess argument vector, never a shell
string. The fixed command shape targets the existing compose file and service:

```text
docker compose
-f tools/hermes/compose.yaml
exec -T hermes
/opt/hermes/hermes chat
-q <bounded prompt>
--quiet
--source tool
```

The lock concerns this fixed-command mechanism, not incidental parser ordering
when the exact pinned CLI requires equivalent ordering. The caller cannot
select the executable, compose file, service/container, subcommand, or extra
arguments. There is no `shell=True`, generic subprocess helper exposed to
Hermes, Docker socket or repository mount inside Hermes, new host-published
Hermes API, generic gateway execution interface, H2/H2.5 outbox consumption,
or Prefect-owned scientific meaning. This is a bounded migration adapter, not
a general Docker execution platform. Replacing it requires a later explicit
architecture decision.

## Decision B — `BoundedResearchIntent v1`

The strict CPW-owned logical handoff is `BoundedResearchIntent v1`. Its exact
Python class and file are deferred to 01A, but these semantic field groups are
locked.

### Identity

- schema version;
- exact repo SHA;
- deterministic input/content SHA-256;
- explicit Hermes operational/session identity when available, marked
  operational-only.

### Structured hypothesis identity

Fields compatible with `hypothesis-v1`:

- `strategy_family`;
- `mechanism`;
- `primary_timeframe`;
- `required_data_features`;
- `free_parameter_count`;
- fixed and validated instrument scope.

### Research reasoning

- bounded research question;
- causal rationale;
- falsifiable prediction;
- falsification/stop criteria;
- proposed parameter bounds/search intent;
- proposed objective intent;
- unresolved assumptions/open questions.

These are untrusted model reasoning until CPW validation accepts them.

### Evidence

- exact Project-Evidence repo SHA;
- exact resolved resource/evidence identities;
- no caller-supplied path or hash accepted as truth.

### Research Memory context

- exact `hypothesis-v1` fingerprint;
- match/no-match result;
- `index_not_truth=true`;
- matching memory/index records when present;
- repo-evidence resolution status;
- resolved classification only when exact repo evidence still validates it.

### Explicit non-authority

The intent must deny canonical-write, approval, promotion/candidate, Search
Governor, final-holdout, scheduler/autonomy, runner/backtest execution,
runtime/risk, paper/live, and capital authority. It contains no approval token,
dispatch token, broker authorization, campaign-budget authority,
scientific-trial minting authority, model-visible final-holdout reference, or
automatic successor-job instruction.

## Decision C — construction ownership

Hermes may produce reasoning content but cannot authoritatively instantiate
scientific policy. Project-Evidence / CPW must:

1. re-resolve repo evidence;
2. validate model-provided reasoning;
3. normalize the exact Research Memory fingerprint input;
4. perform the read-only exact Research Memory lookup;
5. emit or validate the strict `BoundedResearchIntent v1` envelope; and
6. bind it to exact repo/evidence identity.

The one-shot turn may be required to return exact JSON, but the Prefect-side
adapter must parse and strictly validate it before any downstream action.
Plain prose is never an executable handoff.

## Decision D — Research Memory exact-dedup seam

01A may add only a narrow Project-Evidence exact structured-hypothesis lookup
using existing `hypothesis-v1` semantics and the existing DB-enforced read-only
role. This lock authorizes no Research Memory schema change.

Research Memory remains an index for retrieval, deduplication, and context. It
is not the scientific denominator, cumulative scientific lineage, a
performance-prior or freshness authority, candidate authority, or execution
authority. A hit cannot establish a FACT by itself; current repo evidence must
still resolve exactly.

## Decision E — CPW owns intent to `SearchContract`

A later CPW-owned deterministic builder is the only allowed converter from an
accepted `BoundedResearchIntent v1`, plus explicit CPW policy/evidence/lineage
inputs, to a frozen `SearchContract`. Hermes, Prefect, and Optuna cannot create
authoritative contracts.

The builder owns or verifies campaign/search identity, parent/amendment
lineage, exact data identity/version, exact repo SHA, exact Strategy-Spec
identity/hash where applicable, parameter space, conditional/relational
constraints, forbidden regions, objective, scientific constraints, proposal
and scientific-trial budgets, wave size/concurrency, split protocol,
final-holdout isolation, proposer/backend/version/config, seed, duplicate and
failed-software-retry policies, pruning, stop rule, and cumulative campaign
proposal/trial counts. It fails closed when an authoritative value is absent.
No Hermes, Prefect, Optuna, or operational-run-ID default may fill one.

## Decision F — Search Governor remains sole scientific/search owner

The Governor alone owns frozen-contract enforcement, proposal legality, budget
consumption, duplicate meaning, scientific-trial creation, trial-attempt
meaning, software-retry authorization, final-holdout denial, the governed
scientific denominator, and Governor snapshot/restore.

A Prefect retry never permits another `propose_wave()` call. Once a scientific
trial exists, operational retry preserves that scientific identity unless CPW
science explicitly creates a new trial.

## Decision G — Optuna remains proposer only

Optuna 4.9.0 stays behind the Governor capability boundary. No direct
Hermes-to-Optuna or Prefect-to-Optuna scientific-control path is allowed.
Optuna output cannot imply `best_trial`, winner, GO, promotion, readiness,
paper/live, or capital meaning.

## Decision H — H2/H2.5 remain inert

`SearchGovernorCampaignPreparedPayload`, `PrefectWorkflowPreparedPayload`, any
H2 typed proposal, and every H2.5 prepared payload remain inert human-review
content. They cannot become an executable integration message, queue item,
dispatch object, or automatic consumer input. This compatibility requirement
persists unless a later explicit architecture decision supersedes it.

## Decision I — implementation split

### V2-INTEGRATION-01A — HERMES-02 bounded handoff

01A may implement the fixed-command adapter, exact structured Research Memory
dedup lookup, and `BoundedResearchIntent v1` validation, then prove pinned
Hermes -> Project-Evidence -> typed CPW handoff. It is manual-trigger-only and
stops before Search Governor invocation.

01A excludes Governor calls, Optuna waves, product runner, WFO/OOS,
robustness, canonical writes, candidate review/promotion, Stage 5B, and
autonomous scheduling.

### V2-INTEGRATION-01B — CPW contract and Governor/Optuna orchestration

01B may implement the CPW-owned intent-to-`SearchContract` builder, invoke the
Governor, allow proposal waves only behind it, and use Prefect for bounded
operational proposal/recovery orchestration while preserving scientific
identity across retry/restart. It stops before real product-runner execution.

01B requires fresh pre-draft research after 01A to reverify exact scientific
policy inputs and durable cumulative-lineage dependencies.

## Decision J — no activation

This lock activates nothing. Until Stage 5B is separately implemented,
validated, explicitly activated, and a valid Karl-approved immutable bounded
research envelope exists, there is no continuous research loop, autonomous
Hermes scheduling, Prefect research schedule/trigger, self-generated successor
search, autonomous budget expansion, automatic Research Memory writeback,
candidate promotion, protected runtime, paper/live, or capital use.

## Scientific and operational identity

| Identity | Owner | Meaning | Retry/restart invariant |
| --- | --- | --- | --- |
| Hermes session/turn | Hermes; operational-only | One reasoning interaction and its trace. | Never becomes scientific identity or policy. |
| Prefect flow/task/run | Prefect; operational-only | Invocation, worker, state/history, and recovery. | Retry does not mint a proposal or scientific trial. |
| Proposal ID | Search Governor | One accounted proposal under the frozen contract. | Duplicate/invalid handling follows Governor policy only. |
| Scientific trial ID | Search Governor | One independent governed scientific observation. | Software retries retain the same ID and do not increase the denominator. |
| Campaign/search identity | CPW frozen contract and lineage | Scientific policy and cumulative bounded-search lineage. | Operational restart cannot reset budgets, lineage, or holdout state. |

Governor state may be restored only from its validated bounded snapshot at a
finalized wave boundary. Operational history is not a substitute for Governor
state, and Prefect retry is not scientific retry authorization.

## Protected scope and supersession

This record changes no dependency, config, schema, validator, query layer,
Hermes compose/configuration, Prefect implementation, Research Memory
implementation, Search Governor/Optuna code, runner, canonical writer,
research artifact, OMS, reconciliation, risk, overlay, safe mode, kill switch,
paper/live, exchange/order, credential, or capital surface.

A later record may supersede this architecture only through an explicit
reviewed decision that names the affected boundary. Implementation experience
alone, an operational identifier, a model response, a Research Memory hit, a
Prefect run, or an Optuna result cannot silently alter ownership or authority.
