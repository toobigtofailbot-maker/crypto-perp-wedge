# Side 12 External Adoption Pilot Plan

> **Prospective supersession — 2026-09-23:** This plan remains historical pilot
> evidence. Current migration ownership and sequencing are controlled by
> `docs/architecture/2026-09-adoption_first_migration_architecture_freeze.md`.
> Its Prefect deferral, Nautilus GO/paper-shadow trigger, and bespoke generic
> backbone direction do not control future migration work.

## Authority / Send Condition

This is a docs-only planning lock for Side 12 external-repo research triage.
It records current tool dispositions, pilot runway, simulator posture, and
adoption criteria. It does not implement any pilot and does not grant any
external tool canonical, runtime, paper/live, promotion, approval, ranking,
recommendation, or execution authority.

Current merged repo truth remains controlling. The earlier Phase 2 baseline
D2-010 tool lock remains unchanged. Where this plan mentions later agent-phase
reconsideration, that means no current adoption and no override of existing
Phase 2 rejection or deferral language unless a later approved package changes
repo truth.

## Current Adoption Posture

Fact: Side 12 external-repo research is folded into active research-lab
planning.

Decision: the posture is adoption-positive, pilot-now, and repo-controlled.

Decision: the governing pattern is pilot -> evidence ->
adopt/sidecar/borrow/preserve/reject.

Decision: licensing and source metadata should be recorded for provenance and
for any future public-commercial trigger. Licensing metadata is not a current
internal blocker by itself.

Open question: any dependency promotion, public-commercial use, or source-code
copying path still requires a later package to inspect license obligations at
the point of use.

## Tool Disposition Table

| Tool / family | Current disposition | Candidate posture | Boundary note |
|---|---|---|---|
| `purgedcv` | Pilot now | Borrow-candidate | Pilot may study purge/embargo CV mechanics. Repo-owned walk-forward and evidence contracts stay authoritative. |
| Optuna | Pilot now | Sidecar-candidate | Search may be non-canonical advisory only. It cannot mutate canonical Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, trial log, or promotion state. |
| Apprise + GitHub IssueOps | Pilot now | Adopt-candidate | Notifications and approval ergonomics may be piloted as operator workflow support only. No dashboard approval/execution controls or runtime authority. |
| `arch` | Next-wave robustness-depth | Borrow-candidate | Future robustness/statistical depth may borrow formulas or approaches without adopting dependency authority by default. |
| Quarto | Next-wave reporting | Sidecar-or-borrow candidate | Future reporting may use sidecar publishing or borrow report structure. It cannot replace canonical evidence artifacts. |
| Aim | Skip now | Redundant unless a specific gap appears | Current run registry and committed evidence surfaces remain the controlling lineage path. |
| QuantStats | Skip now | Redundant unless a specific gap appears | Repo-native analytics and honest unavailable-field posture remain preferred. |
| DVC | Skip now | Redundant unless a specific gap appears | Existing catalog/checksum provenance remains controlling. |
| Panel / Bokeh | Skip now | Redundant unless a specific gap appears | Existing static dashboard/operator review surface remains controlling. |
| Prefect | Historical disposition: defer to Phase C agents | Prospectively superseded by CPW-MIG-00 | Prefect is the target generic orchestration owner after P1/P2/P3 proofs; this plan grants no implementation authority. |
| LangGraph | Defer to Phase C agents only if later reopened | No current adoption; D2-010 Phase 2 rejection remains current truth | Earlier Phase 2 baseline rejected LangGraph as overkill for the Claude-only stack. This plan does not reverse that decision. |
| NautilusTrader | Historical disposition: preserve | Prospectively superseded by CPW-MIG-00 | Bounded non-capital N1/N2/N3 proofs are not GO-gated; no current simulator or trading authority is created here. |
| LEAN | Preserve/reference | No current implementation | Concepts may be referenced later; no simulator implementation is authorized. |
| Backtrader / Freqtrade / Backtesting.py | Reference / low-value unless a specific gap appears | No current implementation | Earlier Backtrader rejection remains controlling. Reference use creates no dependency or simulator authority. |

## Active Pilot Runway

Active Side 12 pilot packages:

- `WP-PILOT-PURGEDCV-01`
- `WP-PILOT-OPTUNA-SEARCH-SIDECAR-01`
- `WP-PILOT-NOTIFICATIONS-APPROVALS-01`

This plan-lock package:

- `WP-PLAN-SIDE12-ADOPTION-LOCK-01`

Decision: these packages are separate work packages. This plan does not
complete, implement, merge, or validate any pilot package by implication.

## Repo-Owned Surfaces That Stay Repo-Owned

The following surfaces remain repo-owned and are not delegated to external
tools:

- Strategy Spec grammar
- Variant Manifest grammar
- Sweep Plan grammar
- validators
- canonical Result Population schema
- canonical walk-forward contract
- runner/backtester semantics
- candidate lifecycle state
- promotion gates
- human approval state
- dashboard authority boundaries
- paper/shadow/live activation boundaries
- OMS/risk/reconciliation/safe-mode/kill-switch later

Decision: external-tool output may inform research or operator workflow only
inside an approved package. It cannot become canonical authority unless a later
package explicitly promotes a specific surface through repo-owned validation and
boundary review.

## Adopt / Sidecar / Borrow / Preserve / Reject Criteria

Adopt:

- fills a real repo gap;
- fits cleanly with repo-owned contracts;
- is deterministic where possible;
- creates no authority creep.

Sidecar:

- useful for speed, triage, reporting, search, or ergonomics;
- remains non-canonical;
- writes scratch/advisory outputs only unless a later package scopes otherwise;
- cannot rank, recommend, approve, promote, or execute candidates.

Borrow:

- contains a valuable algorithm, formula, pattern, or approach;
- has an unwanted dependency shape, licensing issue, operational overhead, or
  easier repo-native implementation path;
- is implemented repo-native only if a later package authorizes that work.

Preserve:

- valuable later with an explicit trigger;
- no current implementation or authority grant;
- evidence and notes are retained for future evaluation.

Reject:

- specific redundancy, poor fit, negative ROI, unsafe authority shape, or
  implementation evidence supports rejection;
- rejection can be reopened only by later repo-truth change.

## Required Boundary Block

This plan and its follow-on pilots must not:

- touch runtime / paper / live paths;
- touch OMS / risk / reconciliation / safe-mode / kill-switch / broker /
  exchange / order / capital paths;
- use private/authenticated APIs;
- use credentials;
- mutate canonical Strategy Specs;
- mutate canonical Variant Manifests;
- mutate canonical Sweep Plans;
- mutate canonical Result Populations;
- mutate trial log;
- write canonical walk-forward evidence;
- replace the runner/backtester;
- change `lib/backtest.py` semantics;
- grant external tools canonical authority;
- grant external tools candidate/readiness/promotion authority;
- create winner-only reporting;
- create dashboard approval/execution controls;
- edit `docs/project_status.md` in this package;
- mutate repo dependency files unless explicitly scoped by Main later.

External-tool outputs must remain:

- scratch-only;
- non-canonical;
- advisory;
- deterministic where possible;
- status-fragment documented;
- checksum/provenance recorded where relevant.

## Simulator Posture

This section records the historical Side 12 posture. Its GO/paper-shadow trigger
is not current roadmap authority after CPW-MIG-00.

Fact: `docs/architecture/2026-06-external_repo_adoption_decision.md` preserves
NautilusTrader as a viable canonical-grade simulator candidate with the
paper/shadow trigger. That decision also records known semantic gaps and denies
current canonical simulator authority.

Historical decision: Side 12 preserved that simulator posture and did not
promote NautilusTrader. LEAN remained reference-only, while Backtrader,
Freqtrade, and Backtesting.py remained low-value/reference.

Current direction: separate packages may run bounded non-capital N1/N2/N3 proof
before edge/GO, while mapping completeness, determinism, auditability,
provenance, semantic-gap closure, and authority-promotion review remain required
before any ownership transfer.

## Parallel Execution Runway

Decision: pilot packages should remain narrow, separately branched, and
mergeable. Each package must state whether its outputs are scratch-only,
sidecar-only, borrowed-design-only, or repo-native.

Decision: any package that touches `docs/project_status.md` must follow the
repo's overlap guardrail. This plan package does not edit
`docs/project_status.md`.

Decision: if a pilot requires dependency-file mutation, protected-path contact,
schema/validator/query behavior, canonical evidence writes, or runtime/paper
path changes beyond its package scope, it must stop and escalate.

## WP Savings Expectation

Inference from Main's Side 12 triage: net realistic savings are approximately
5-10 WPs.

Inference: largest near-term savings are notifications/approvals and
search-sidecar triage.

Historical decision: the bespoke backbone was then retained for idea intake,
agents, walk-forward-run, dashboard, and canonical evidence. Prospectively,
generic agent, orchestration, and trading mechanics migrate according to
CPW-MIG-00, while CPW retains differentiated research and canonical semantics.
