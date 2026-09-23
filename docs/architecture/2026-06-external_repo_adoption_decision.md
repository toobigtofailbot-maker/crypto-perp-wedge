# External Repo Adoption Decision

> **Prospective supersession — 2026-09-23:** This document preserves the June
> evaluation and adoption evidence as historical truth. Current migration
> ownership, proof sequencing, and version targets are controlled by
> `docs/architecture/2026-09-adoption_first_migration_architecture_freeze.md`.
> In particular, its Nautilus GO/paper-shadow trigger is superseded for bounded,
> non-capital N1/N2/N3 engineering proof. Nautilus receives no authority until
> the applicable proof and later ownership-transfer package pass.

## Authority / Send Condition

This is a docs-only architecture decision for the external-repo integration and
evaluation runway completed by PRs #514 through #519.

It creates no implementation authority, no canonical authority grant by default,
no runner/backtester replacement authority, no paper/live/runtime authority, no
candidate promotion authority, and no screen-gate or readiness authority.

Repo-owned outputs created by the six source work packages remain bounded by
their original package scopes. Research, advisory, sidecar, simulator, and
scratch artifacts are not execution authority unless a later approved package
explicitly promotes a specific surface.

## Evidence Sources

| Component | Source package | PR | Status / report reference | Decision evidence |
|---|---|---:|---|---|
| CCXT funding adapter | `EXT-INTEG-CCXT-FUNDING-ADAPTER-01` | #514 | `docs/status_entries/EXT-INTEG-CCXT-FUNDING-ADAPTER-01.md` | Decision label `ADOPT_AS_PUBLIC_DATA_ADAPTER`; public CCXT funding snapshot validated with no private credentials or backtest wiring. |
| Robustness MC | `EXT-INTEG-ROBUSTNESS-MC-01` | #515 | `docs/status_entries/EXT-INTEG-ROBUSTNESS-MC-01.md` | Decision label `ADOPT_AS_ROBUSTNESS_LAYER`; seeded advisory bootstrap diagnostics over existing Result Population rows. |
| Workflow-gen | `EXT-INTEG-WORKFLOW-GEN-01` | #516 | `docs/status_entries/EXT-INTEG-WORKFLOW-GEN-01.md` | Decision label `ADOPT_AS_WORKFLOW_ACCELERATOR`; deterministic scratch draft grid generation with structural validator checks. |
| Vectorbt | `EXT-INTEG-VECTORBT-TRIAGE-SIDECAR-01` | #517 | `docs/status_entries/EXT-INTEG-VECTORBT-TRIAGE-SIDECAR-01.md` | Decision label `ADOPT_AS_NON_CANONICAL_TRIAGE_SIDECAR`; optional dependency-isolated fast triage only. |
| Analytics metrics | `EXT-INTEG-ANALYTICS-METRICS-01` | #518 | `docs/status_entries/EXT-INTEG-ANALYTICS-METRICS-01.md` | Decision label `FORMULA_ADAPT_REPO_NATIVE`; repo-native advisory formulas and bounded report surface. |
| Nautilus | `EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01` | #519 | `docs/status_entries/EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01.md`; `scratch/EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01/nautilus_mapping_report.md` | Decision label `VIABLE_CANONICAL_GRADE_SIMULATOR_CANDIDATE`; deterministic bounded mapping spike with explicit unsupported semantics. |

The Nautilus report checksum is recorded in
`scratch/EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01/nautilus_mapping_report.sha256` as
`4c3d84f639c4da9e20c064cc5e6b6f15cbe4110693d23aa6e48f11c1739772a5`.

## Decision Summary

| Component | Disposition | Current allowed use | Not-authorized use | Follow-on trigger |
|---|---|---|---|---|
| CCXT funding adapter | Adopted as public-data adapter | Repo-owned public funding ingestion and frozen scratch/catalog-lineage evidence under the adapter's package boundaries. | Private/authenticated APIs, credentials, account/balance/position/order methods, backtest cost-model wiring, runtime/paper/live use, or canonical data promotion by default. | Later explicit funding-into-backtest or canonical-data-promotion package. |
| Robustness MC | Adopted as advisory robustness layer | Seeded advisory row-level bootstrap and parameter-sensitivity diagnostics over existing Result Population rows. | Per-trade MC fabrication, screen-gate authority, promotion/readiness/ranking authority, canonical Result Population mutation, or runtime influence. | Later package if real per-trade instrumentation is authorized and available. |
| Workflow-gen | Adopted as draft workflow accelerator | Deterministic scratch-only draft Strategy Spec / Variant Manifest / Sweep Plan-style artifact generation for human review. | Canonical preregistration, candidate evidence, screen-gate or promotion authority, optimizer/ranker/recommender authority, or artifact mutation outside scratch. | Human/Karl-gated draft-to-prereg promotion package. |
| Analytics metrics | Adopted as repo-native advisory analytics | Repo-native advisory formulas and reports over inputs that honestly expose required chronological equity/return fields or aggregate-only limitations. | Invented return/equity paths, gate authority, candidate evidence, ranking/promotion/readiness authority, schema/runner mutation, or runtime influence. | Later advisory input-surface package if chronological equity/return data is authorized. |
| Vectorbt | Adopted as non-canonical fast triage sidecar | Optional dependency-isolated, non-canonical variant triage ordered by variant id, with deterministic deferred output when vectorbt is unavailable. | Canonical runner/backtester replacement, metric-ranked finalist confirmation, dependency-file mutation, canonical Result Population writes, or promotion/readiness/screen-gate authority. | Later canonical runner confirmation for any surfaced finalist; no automatic bridge. |
| Nautilus | Historical June posture: shelved / preserved as viable canonical-grade simulator candidate | Preserve the historical evaluation and mapping notes. Current proof sequencing is governed by CPW-MIG-00. | Canonical simulator authority now, runner/backtester replacement now, paper/live/runtime use now, or candidate evidence/readiness/promotion authority now. | Historical trigger was GO/paper-shadow; prospectively superseded for bounded non-capital N1/N2/N3 proof. |

## CCXT Funding Adapter

Decision: adopted as public-data adapter.

Fact: PR #514 merged a repo-owned CCXT public funding adapter under
`tools/data_ingestion/` with frozen scratch outputs, validation report,
checksum, provenance, and catalog lineage. Its status fragment records public
method `ccxt.binanceusdm.fapiPublicGetFundingRate`, credentials used `false`,
expected and observed 8h events `6879`, and no missing events.

Decision: the adapter is acceptable for public funding data acquisition and
lineage work inside later explicitly scoped data packages.

Not authorized: no private/authenticated API use, no account/balance/position
or order method use, no runtime/paper/live use, no funding-into-backtest wiring,
and no canonical data promotion by default.

Future option: funding-into-backtest remains gated and later.

## Robustness MC

Decision: adopted as advisory robustness layer.

Fact: PR #515 merged seeded advisory robustness tooling under
`tools/robustness/`. The committed report uses existing Result Population rows
and records that per-trade Monte Carlo is queued because committed Result
Populations do not contain per-trade rows.

Decision: the robustness layer may be used for advisory diagnostics over
available committed evidence. It is not an approval gate.

Not authorized: no fabricated per-trade data, no canonical Result Population
mutation, no Strategy Spec / Variant Manifest / Sweep Plan mutation, no
promotion/readiness/screen-gate/ranking authority, and no runtime influence.

Future option: per-trade MC instrumentation may be considered only if a later
package explicitly pulls real per-trade instrumentation into scope.

## Workflow-Gen

Decision: adopted as draft workflow accelerator.

Fact: PR #516 merged deterministic draft grid generation under
`tools/research_workflow/`. Generated outputs are scratch-only and explicitly
labeled as draft workflow output, not canonical preregistration, not candidate
evidence, and not screen-gate or promotion authority.

Decision: workflow-gen may accelerate draft artifact preparation for human
review.

Not authorized: generated drafts are not canonical artifacts, do not register or
promote candidates, do not bypass preregistration review, and do not create
screen-gate, readiness, ranking, recommendation, paper/live, or runtime
authority.

Future option: draft-to-prereg promotion remains human/Karl-gated and requires a
separate package.

## Analytics Metrics

Decision: adopted as repo-native advisory analytics.

Fact: PR #518 merged repo-native advisory analytics formulas and reporting
under `tools/analytics/`. The fixture report over `RP-7134` honestly marks
path-dependent metrics unavailable because the committed Result Population
contains aggregate per-variant metrics rather than chronological equity or
return series.

Decision: analytics formulas are acceptable advisory analytics when their input
requirements are satisfied, and they must preserve honest unavailability labels
when inputs are aggregate-only.

Not authorized: no invented return paths, no invented equity paths, no schema or
runner changes by implication, no gate/promotion/readiness/candidate-evidence
authority, and no runtime influence.

Future option: advisory analytics can expand when a later authorized surface
provides real chronological equity or return inputs.

## Vectorbt

Decision: adopted as non-canonical fast triage sidecar.

Fact: PR #517 merged a bounded vectorbt sidecar under `tools/sidecars/`. It is
dependency-isolated, optional, non-canonical, ordered by variant id rather than
metric rank, capped by `--max-variants`, and writes a deterministic deferred
report if vectorbt is unavailable.

Decision: vectorbt may be used as a fast triage sidecar only.

Not authorized: vectorbt does not replace the canonical runner/backtester, does
not confirm finalists, does not write canonical Result Populations, does not
mutate dependency files, and does not create promotion/readiness/screen-gate
authority.

Future option: any candidate or variant surfaced by vectorbt requires separate
confirmation through the repo-owned canonical runner and evidence path.

## Nautilus

The status and trigger in this section record the June 2026 decision at the
time. CPW-MIG-00 prospectively supersedes the GO/paper-shadow prerequisite for
engineering/adoption proof; it does not rewrite or invalidate this evidence.

Status: SHELVED / preserved for future trigger.

Classification: `viable-canonical-grade-simulator-candidate`.

Historical trigger: when a GO strategy enters the paper/shadow track.

Fact: PR #519 merged a bounded NautilusTrader 1.221.0 offline mapping spike
under `tools/simulators/` and scratch evidence. It attempted and expressed all
eight `VM-0004` / `SWEEP-PLAN-0004` variants over the checksum-verified D4A
slice, matched RP trade counts for all variants, repeated deterministically, and
reported maximum absolute return delta versus `RP-2592` of
`0.004382623128073526`. The status fragment states the `0.005` bounded-spike
tolerance is not a canonical acceptance threshold.

Known gaps to resolve at trigger:

- zero-equity liquidation rule not exposed in bounded Nautilus mapping;
- continuous canonical quantities rounded to 8 decimal places by synthetic
  offline instrument.

Historical decision: Nautilus was preserved as a credible future simulator
candidate and shelved pending its then-current trigger. The evidence remains
retained and does not itself grant canonical authority.

Not authorized: Nautilus is not the canonical simulator, not a runner/backtester
replacement, not paper/live/runtime authority, and not candidate
promotion/readiness/screen-gate authority.

Current direction: bounded N1/N2/N3 non-capital proofs may occur before GO under
separately approved packages. Mapping completeness, determinism, auditability,
provenance, explicit semantic-gap closure, and a later ownership-transfer
decision remain mandatory before canonical use.

## Protected Boundary

This decision preserves the following boundaries:

- no runtime/paper/live behavior change;
- no private APIs, credentials, account, balance, position, or order methods;
- no OMS, risk, reconciliation, safe-mode, kill-switch, broker, exchange, or
  order-path drift;
- no runner/backtester replacement;
- no `lib/backtest.py` authority or mutation;
- no canonical Result Population, Strategy Spec, Variant Manifest, or Sweep Plan
  mutation;
- no candidate promotion, readiness, screen-gate, ranking, recommendation, or
  candidate-evidence authority.

## Follow-On List

- Funding-into-backtest remains gated and later.
- Per-trade MC instrumentation remains possible only if pulled by a later
  authorized package using real per-trade data.
- Draft-to-prereg promotion remains human/Karl-gated.
- The former Nautilus GO/paper-shadow trigger remains historical evidence and
  is prospectively superseded by CPW-MIG-00 for bounded non-capital proof.
- Vectorbt remains triage-only and non-canonical.
- Analytics, MC, and dashboard-facing outputs remain advisory unless later
  explicitly promoted through an approved path.

## Next Runway Pointer

Historical note: this decision closed its external-repo adoption runway without
implementing the then-following packages. The current migration runway is
CPW-MIG-01 only, as defined by CPW-MIG-00.
