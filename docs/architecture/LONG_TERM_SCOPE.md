# Long-Term Architecture Scope

## Purpose

This file captures locked long-term architecture guidance for the BTCUSDT USDT-M perpetual futures repo. It is a stable scope reference for roadmap, automation boundaries, managed-agent timing, decision-pipeline timing, dashboard timing, and the later self-improvement research layer.

This document records architecture direction that should guide future execution packages. It does not authorize immediate implementation by itself. Revisions require explicit architecture review and should be made only when repo evidence or locked decisions justify the change.

## Current Position

The current adoption-first migration architecture is controlled by
`docs/architecture/2026-09-adoption_first_migration_architecture_freeze.md`.
Hermes is the target generic reasoning runtime, Prefect the target generic
orchestration owner, and NautilusTrader the target generic trading-mechanics
owner after bounded N1/N2/N3 proofs. CPW retains differentiated scientific,
canonical, safety, and approval semantics. Infrastructure buildability is not
candidate-gated; economic activation is. CPW-MIG-00 unlocks only CPW-MIG-01.

The repo is in Phase 2 research execution. Phase 2 remains research-first, but
engineering readiness and strategy readiness are separate under
`docs/decisions/ENGINEERING_VS_STRATEGY_READINESS.md`. Genuine candidate
evidence remains mandatory before real-capital authorization or deployment;
absence of profitable edge does not block candidate-agnostic construction or
engineering validation in disabled, simulation, or other non-capital modes.

The long-term target is a multi-strategy, multi-timeframe portfolio rather than a single winner-takes-all strategy. The current accepted direction adds a candidate-agnostic research machine buildout tranche before Strategy v1 lock-in.

The deterministic execution core remains protected. OMS truth, reconciliation truth, kill-switch semantics, D-0001 hard risk caps, overlay bounds, paper ledger accounting, and event-log discipline remain outside normal research automation authority.

## Research Machine Buildout

The repo has accepted a near-term candidate-agnostic research machine buildout tranche. Its priority is foundation work for systematic candidate discovery, testing, comparison, ranking, and later human-gated promotion.

This layer sits above the protected deterministic execution core. It may define registry, schema, artifact, query, and bounded research automation foundations, but it does not weaken OMS, reconciliation, kill-switch, risk-cap, overlay, paper ledger, event-log, or runtime decision semantics.

The currently designated H-004-R2 engineering dummy may exercise these
foundations and later lab/factory, paper/shadow, monitoring, and
live-capable-disabled plumbing under separately authorized packages. It remains
non-winning, non-production, structurally GO-forbidden, and unable to supply
strategy-performance or real-capital authority.

## Forward Roadmap

The long-term architecture progresses in staged layers:

1. Baseline hypothesis execution using the Phase 2 research workbench and the current registered hypotheses.
2. Candidate coverage expansion across the locked timeframe set, including meaningful future research on 15m, 30m, and 1h because the desired portfolio needs more frequent daily opportunity than slower bars alone can provide.
3. Parameter sensitivity and structured sweeps after baseline runs establish whether a candidate deserves deeper testing.
4. Walk-forward and regime validation to measure durability across time, market conditions, and cost assumptions.
5. Shadow deployment for candidates that pass research gates, using the protected runtime path without live execution authority.
6. Research automation for repeatable sweeps, reports, gate checks, trial-log discipline, and broader candidate coverage across timeframes.
7. Advisory decision pipeline that summarizes evidence and proposes bounded actions without owning execution truth.
8. Production execution only after shadow evidence, human approval, and protected runtime integration.
9. Multi-strategy management for independently validated strategy families across multiple timeframes.
10. Monitor and self-improvement research layer that watches performance, proposes variants, and routes evidence back into safe research workflows.

Activation and performance claims at each stage require the applicable
repo-recorded evidence and explicit execution package. This sequence is not a
linear prerequisite on engineering buildability: candidate-agnostic machinery
may be built and validated with the designated dummy before genuine edge exists,
provided it stays inside separately authorized non-capital modes and preserves
all protected gates.

The intended end state is not one active strategy. Each active timeframe may eventually host multiple independently validated strategies, roughly 2-3 candidates where research evidence justifies continued work. No timeframe receives a free pass: every candidate must still pass pre-registration, research evaluation, shadow/parity checks, and human-controlled promotion gates before trading.

## Managed Agents

The historical deferral of managed-agent infrastructure is superseded for the
adoption-first migration. Hermes may be proven and adopted as the sole generic
reasoning runtime through separately authorized packages; CPW-specific domain
logic, canonical truth, promotion, risk, trading truth, and economic authority
remain outside it.

Managed agents are research, monitoring, and proposal infrastructure. They are never execution truth, risk truth, OMS truth, or promotion authority.

## Research Automation

Research automation may proceed through target-compatible seams after MIG-01.
Generic orchestration mechanics belong to Prefect after proof, rather than to
continued custom scheduler/queue/retry/run-state expansion. The safe automation
surface includes:

- Parameter sweeps within approved hypothesis boundaries.
- Experiment plans derived from registered hypotheses.
- Automated reports from repo artifacts and evaluation outputs.
- Gate checking against locked promotion criteria.
- Trial logging with reproducible config, dataset, and metric metadata.
- Candidate coverage tracking across locked timeframes, especially 15m, 30m, and 1h as intraday research expands.

Automation should reduce manual repetition and improve evidence quality. It must not bypass pre-registration, inflate trial counts with non-evidence runs, silently modify promotion gates, or promote candidates without human review.

Future BTC-perp-specific research, data, regime, execution-realism, and paper/live operational capabilities are tracked in `docs/architecture/BTC_PERP_FUTURE_CAPABILITY_BACKLOG.md`. That backlog is planning memory only; each capability still requires an explicit package, validation path, and authorization before implementation.

## Decision Pipeline

The decision pipeline is advisory first.

Decision outputs should be schema-validated, evidence-linked, and traceable to repo artifacts. Later phases may add deterministic mapping from advisory outputs into bounded overlays or execution configuration proposals, but risk and OMS truth remain dominant.

No agent or automation deploys directly to live execution. Live promotion, risk changes, strategy activation, and kill decisions require explicit human approval through the locked decision process.

## Dashboard / Visibility

Visibility should be derived from repo truth.

The first layer is lightweight reports generated from existing artifacts: hypotheses, trial logs, evaluation outputs, gate reports, data manifests, and shadow reports. A later dashboard may read repo artifacts, JSON outputs, and generated reports, but it must not create a separate shadow truth outside the repo.

If a dashboard disagrees with repo artifacts, the repo artifacts win until the discrepancy is investigated and corrected.

## Monitor / Self-Improvement Layer

The monitor and self-improvement layer is a long-term target, not an immediate Phase 2 deliverable.

Its role is to detect performance deterioration, identify regime or cost changes, propose new hypotheses or variants, and initiate safe research workflows inside approved boundaries.

Human approval remains mandatory for promotions, execution changes, risk parameter changes, and any change that alters live or shadow behavior.

## Permanent Human Gates

The following gates remain human-controlled:

- Hypothesis approval.
- Decision records and go/no-go decisions.
- Shadow promotion.
- Live promotion.
- Risk parameter changes.
- Kill decisions.
- Novel strategy-family introduction.

Automation may prepare evidence for these gates, but it may not approve them.

## Safe-to-Automate Areas

The following areas are safe to automate when bounded by existing repo rules and explicit package scope:

- Data refresh.
- Trial logging.
- Metric computation.
- Parameter sweeps.
- Report generation.
- Gate checking.
- Alerts.
- Research proposal generation within approved boundaries.

Automation in these areas must preserve provenance, reproducibility, and the existing trial-log and promotion-gate discipline.

## Deferred Items

The following items remain deferred unless a later architecture package explicitly unlocks them:

- 4h routine research work, while it remains in Cold Storage after the H-001 and H-002 baseline failures.
- Real-capital activation and speculative production expansion before genuine
  strategy evidence requires them. Engineering construction and validation of
  live-capable components in disabled/non-capital modes remains permitted under
  `docs/decisions/ENGINEERING_VS_STRATEGY_READINESS.md` and separately
  authorized protected packages.
- CCXT adoption for execution abstraction.
- Duplicate generic agent runtimes or broader LLM-routing/provider complexity
  outside the Hermes adoption path.

These deferrals protect research focus and avoid unscoped operational
complexity. They are not a blanket strategy-evidence prerequisite for
separately authorized engineering construction/non-capital validation; genuine
strategy evidence remains the gate for performance claims and real-capital
activation.

## Revision Policy

Revisions to this file require explicit architecture review.

Changes should be evidence-based, tied to repo artifacts or locked decisions, and scoped to the minimum needed update. Silent drift is not allowed: when long-term architecture direction changes, this file must be updated deliberately and reviewed as an architecture change.
