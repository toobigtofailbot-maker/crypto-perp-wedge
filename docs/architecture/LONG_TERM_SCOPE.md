# Long-Term Architecture Scope

## Purpose

This file captures locked long-term architecture guidance for the BTCUSDT USDT-M perpetual futures repo. It is a stable scope reference for roadmap, automation boundaries, managed-agent timing, decision-pipeline timing, dashboard timing, and the later self-improvement research layer.

This document records architecture direction that should guide future execution packages. It does not authorize immediate implementation by itself. Revisions require explicit architecture review and should be made only when repo evidence or locked decisions justify the change.

## Current Position

The repo is in Phase 2 research execution. Phase 2 remains research-first: validate or kill pre-registered BTCUSDT perpetual strategy hypotheses before expanding runtime scope.

The long-term target is a multi-strategy, multi-timeframe portfolio rather than a single winner-takes-all strategy. All locked Phase 2 timeframes remain in consideration for candidate research, with 4h in Cold Storage for now after H-001 and H-002 failed baseline gates.

The deterministic execution core remains protected. OMS truth, reconciliation truth, kill-switch semantics, D-0001 hard risk caps, overlay bounds, paper ledger accounting, and event-log discipline remain outside normal research automation authority.

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

Each stage should add capability only after the prior stage has produced repo-recorded evidence and an explicit execution package.

The intended end state is not one active strategy. Each active timeframe may eventually host multiple independently validated strategies, roughly 2-3 candidates where research evidence justifies continued work. No timeframe receives a free pass: every candidate must still pass pre-registration, research evaluation, shadow/parity checks, and human-controlled promotion gates before trading.

## Managed Agents

Managed agents are not a near-term implementation target.

They become relevant only after the repo has research automation, repeated parallel research workflows, and a clear orchestration need that cannot be handled by direct execution briefs, skills, prompts, and lightweight automation.

Managed agents are research, monitoring, and proposal infrastructure. They are never execution truth, risk truth, OMS truth, or promotion authority.

## Research Automation

Research automation should arrive before heavy managed-agent orchestration. The safe automation surface includes:

- Parameter sweeps within approved hypothesis boundaries.
- Experiment plans derived from registered hypotheses.
- Automated reports from repo artifacts and evaluation outputs.
- Gate checking against locked promotion criteria.
- Trial logging with reproducible config, dataset, and metric metadata.
- Candidate coverage tracking across locked timeframes, especially 15m, 30m, and 1h as intraday research expands.

Automation should reduce manual repetition and improve evidence quality. It must not bypass pre-registration, inflate trial counts with non-evidence runs, silently modify promotion gates, or promote candidates without human review.

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
- Heavy live-trading framework upgrades before research evidence requires them.
- CCXT adoption for execution abstraction.
- Managed agents now.
- Broader LLM routing or multi-provider complexity now.

These are deferred to protect research focus and avoid expanding operational complexity before there is strategy evidence to justify it.

## Revision Policy

Revisions to this file require explicit architecture review.

Changes should be evidence-based, tied to repo artifacts or locked decisions, and scoped to the minimum needed update. Silent drift is not allowed: when long-term architecture direction changes, this file must be updated deliberately and reviewed as an architecture change.
