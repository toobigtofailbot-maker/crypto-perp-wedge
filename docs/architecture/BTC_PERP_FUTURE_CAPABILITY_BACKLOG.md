This document is non-authoritative architecture memory. It is an unordered inventory of future BTC perpetual research-lab and later bot capabilities. No item in this document authorizes implementation, sequencing, data acquisition, candidate lifecycle, promotion, paper/live execution, runtime behavior, OMS/risk changes, broker/exchange connectivity, collateral movement, or autonomy. Each item requires a scoped future package, validation plan, and explicit authorization before implementation.

# BTC Perp Future Capability Backlog

## Status / authority boundary

This backlog records future BTC perpetual capability ideas as planning memory only. It is not an approval surface, priority list, execution plan, roadmap commitment, or implementation queue.

This backlog does not create approval, priority, implementation authority, or sequencing authority by itself.

## Current architectural fit

The current repo direction remains research-first. Future BTC perp capability work should stay above the protected deterministic execution core unless a later package explicitly authorizes a protected-path change.

Automation remains advisory. It may prepare evidence inside scoped research workflows, but it cannot own execution, risk, promotion, live decisions, or runtime truth.

Result populations remain evidence/reference artifacts. `RP-7520` is canonical dynamic-sizing evidence, not candidate approval. `RP-6688` remains an append-only prior fixed-sizing artifact.

The intended order remains: lab-scale foundations first; crypto/perp research features second; execution-realism simulation third; paper/live guardrails fourth; autonomous or semi-autonomous runtime last, if explicitly authorized.

## Capability inventory

Research-lab and automation capabilities:

- strategy idea intake contract
- Strategy Spec generator / compiler-compatible DSL
- parameter sweep engine
- result store / run registry
- anti-overfit gates
- walk-forward / regime validation
- Monte Carlo / robustness engine
- candidate registry upgrade
- read-only dashboard expansion
- human-gated promotion workflow
- agent-assisted strategy drafting
- large-scale batch sweeps

Crypto/perp data and feature capabilities:

- funding-rate and basis features
- open-interest / liquidation feature track
- mark/index/premium basis features
- BTC dominance / alt-rotation regime features
- BTC correlation to Nasdaq/DXY/macro liquidity
- on-chain exchange inflow/outflow
- realized cap / UTXO age / HODL waves
- order-book imbalance research features

Execution-realism and later paper/live capabilities:

- smart order-router simulator
- stablecoin / collateral risk evaluator
- stablecoin depeg stress scenarios
- exchange outage / API degradation simulation
- counterparty / exchange risk monitor

## Suggested phase fit

Lab-scale foundations fit before new authority-bearing runtime work. This includes idea intake, Strategy Spec drafting support, sweep/run registries, anti-overfit checks, walk-forward and robustness surfaces, candidate registry improvements, read-only dashboard expansion, and bounded agent-assisted drafting.

Crypto/perp research features fit after the lab foundations can ingest and evaluate them with reproducible provenance. Funding, basis, mark/index/premium, open-interest, liquidation, BTC dominance, macro-correlation, on-chain, and order-book features all require their own data and validation packages before use.

Execution-realism simulation fits after comparable research evidence needs it. Smart-order routing simulation, stablecoin/collateral stress, exchange outage behavior, and counterparty monitoring remain simulation/planning surfaces until separately authorized.

Paper/live guardrails fit only after research and shadow evidence justify the next boundary package. Any movement toward runtime, paper/live, OMS/risk, broker/exchange, collateral, or autonomy remains outside this backlog's authority.

## Deferred / later-runtime items

These items are deferred later-runtime inventory, not near-term implementation authority:

- cross-venue latency arbitrage filters
- multi-venue smart order routing for real orders
- automated collateral balancers
- spoofing / iceberg detection
- on-chain fee market / Lightning settlement optimizer
- live exchange insolvency automation
- options volatility surface / Greeks engine
- sub-second HFT stack

## Deliberate exclusions for current phase

This backlog does not authorize implementation of any listed capability.

This backlog does not authorize data acquisition, schema or validator changes, query-layer behavior changes, result-population writes, candidate registration, variant ranking, readiness claims, strategy promotion, paper/live execution, runtime changes, OMS/risk changes, broker/exchange connectivity, collateral movement, or autonomous behavior.

No item here changes protected runtime boundaries: OMS truth, reconciliation truth, kill-switch semantics, D-0001 hard risk caps, bounded overlay semantics, paper ledger accounting, event-log discipline, safe mode, or live-trading paths.

## Locking policy

This file may be used as architecture memory when drafting future packages, but current merged repo truth and active package scope still win.

Each future capability requires a separately scoped package, explicit authorization, validation plan, changed-file boundary, and non-authority audit before implementation or evidence production.

Future packages may cite this file to preserve context, but citation does not weaken package-specific forbidden scope or protected runtime boundaries.
