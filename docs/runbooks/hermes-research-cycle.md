# Manual Hermes research cycle (02K)

This entrypoint composes the existing discovery, whole-cohort native intent,
strategy-developer handoff, synthetic compiler readiness and data-catalog
metadata checks. It preserves exactly three distinct hypotheses, in director
order, including blocked ideas, criticism and negative/unknown Memory state.
It is default OFF: run it manually. No scheduled deployment is installed.

Use the repository's existing Python environment. All inputs and destinations
must be external ordinary directories; destinations must be new, with an
existing parent. Evidence directories must not contain secrets or raw history.

For an already captured `research_turn.ps1 -StructuredIntentHandoff` cycle:

```powershell
python -B -m tools.hermes.research_cycle_coordinator build --cycle C:\proof\cycle --output C:\proof\integrated-new --provenance OPERATOR_CAPTURE_UNVERIFIED_AUTHORSHIP
python -B -m tools.hermes.research_cycle_coordinator replay --cycle C:\proof\cycle --output C:\proof\integrated-new --provenance OPERATOR_CAPTURE_UNVERIFIED_AUTHORSHIP
```

The model must author all scientific fields. No model text is parsed into
approval. A capture label and session IDs alone do not independently establish
model authorship, source truth, scientific eligibility or profitable edge.
Engineering fixtures must use `LABELED_FIXTURE_NOT_MODEL_OUTPUT` instead.

Only when this worktree already owns an approved isolated F1/F2 environment,
existing authenticated provider access and a fixed budget for one supervised
cycle (five native turns; no retries), the same operator action can discover
and integrate:

```powershell
python -B -m tools.hermes.research_cycle_coordinator discover --cycle C:\proof\native-cycle-new --output C:\proof\integrated-new --provenance OPERATOR_CAPTURE_UNVERIFIED_AUTHORSHIP --theme "Compare three falsifiable BTCUSDT perpetual hypotheses using public evidence; retain unknowns and critic dissent"
```

This delegates to the unchanged `research_turn.ps1`; its ownership, credentials,
head/branch, independent scout/critic and bounded-tool checks still apply.
It neither starts a service nor provisions/copies credentials. Failure retains
the native launcher's evidence; there is no automatic retry. Never reuse
another worktree's Compose project/home. The launcher may also leave its native
adjacent `.discovery-intent` output; that is retained, not erased.

The output includes a closed, hashed inventory and:

- `cycle/`, `responses/`, `02a.discovery-intent/`, `02b/`, `02c-prepared/`,
  `02c/`, `02d/`, `02e/`: original evidence and actual native receipts.
- `02c-prepared/requests/`: native request JSON and prompts for a separately
  captured strategy-developer response. Use the existing 02C capture contract:
  exact request/prompt/intent/fingerprint identities, response and capture pairs.
  Supply that external directory with `--responses C:\proof\responses` when
  building a **new** output from the same cycle and HEAD. Reuse the exact frozen
  Memory state; Memory drift correctly invalidates byte replay.
- `study-request.json`: exact cohort/draft identities and missing native inputs.
  `NO_ELIGIBLE_NATIVE_STUDY` is a block, not an approval-ready experiment.
- `memory-index-request.json`: pending, non-authoritative per-idea lessons.
  No native Memory write or scientific result is asserted.
- `cycle-summary.json`: dispositions, per-idea data gaps, provenance limits,
  compiler checks, critic-vs-outcome caveats and KPI counts.

`model_cycles` counts independently verified genuine cycles and stays zero for
fixtures or unverified imports; `captured_cycles` and native turn receipt counts
are separate. `pipeline_model_calls=0` describes deterministic assembly only.
`discover` additionally launches the unchanged five-turn native cycle once;
fixture receipts do not count as paid/model execution or scientific trials.
The denominator KPI counts new trials in this cycle only. Existing cumulative
scientific history is not queried, assumed zero or reset.

02D compiler probes use explicitly synthetic bars. 02E is invoked without a
local data root or physical input requests. 02F/02G physical loaders and 02H
protocol review are not called without their genuine bound prerequisites.
No raw history or holdout file is opened to diagnose a block.

Current native integration limit: 02C creates noncanonical drafts; 02D leaves
science NOT_READY and SearchContracts NOT_ISSUABLE. The factory mapper accepts
only exact `STRAT-SPEC-0003` / `VM-0003` / `SWEEP-PLAN-0003`, 15m, its frozen
data identity/partition and supported proposer. It is not a generic consumer
of Hermes drafts. Governor, Optuna and Prefect cannot repair this mismatch or
confer eligibility. No replacement mapper, policy or scientific executor is
introduced here. An eligible exact study must first satisfy the existing
canonical, semantic, data-custody, protocol, durable-lineage and owner gates.

Consequently the blocked request has no execution command or approval marker.
Do not approve it as an experiment or ask Karl to select a strategy. Preserve
the whole cohort for review; resolve the exact missing native inputs/mapping
before any scientific approval request. All runner/DB/scheduler/holdout effects
remain zero. There is no Stage 5B, unattended successor or capital authority.

Rollback: stop invoking the entrypoint or revert this software addition. Keep
external immutable evidence, including failed attempts; never delete scientific
history to reset a denominator. Replays compare all bytes and perform no
scientific execution.
