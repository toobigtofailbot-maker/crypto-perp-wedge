# Research Machine Direction

## Purpose

This note records the accepted Phase 2 direction shift before WP-6a. It is a reference for future packages that need to build candidate-agnostic BTC research machine foundations without contradicting the locked Phase 2 baseline or weakening the protected deterministic execution core.

## What Changed

The earlier Phase 2 framing could be read as candidate-first: register the next hypothesis, execute it, and move directly toward Strategy v1 if something survives. That interpretation is now too narrow.

Phase 2 still exists to find promotable BTCUSDT perp edge, but the near-term architecture path may build reusable research foundations first. Strategy v1 is not locked now. H-011 and later ideas remain future candidates, not the organizing principle for the next architecture step.

## Why Single-Strategy Framing Is Insufficient

H-001 through H-010 produced no promotable candidate. WP-5a audited the research instrument, and WP-5b applied bounded pipeline fixes while preserving all existing overall NO-GO verdicts.

The repo now needs a more systematic way to discover, track, test, compare, and rank candidates. A single immediate candidate path would keep repeating manual package structure without improving the evidence system that future candidates need.

## Target System

The target is a candidate-agnostic research machine for BTCUSDT perp strategy research:

- Candidate discovery and backlog tracking.
- Structured experiment plans and reports.
- Reproducible evidence collection linked to datasets, configs, trial logs, and decisions.
- Multi-candidate comparison and ranking without overfitting shortcuts.
- Human-gated promotion from research evidence to shadow readiness.
- Bounded research automation that prepares evidence but does not own decisions.

The long-term goal remains a BTC trading model supported by continuous candidate discovery, testing, comparison, and later human-gated promotion.

## Protected And Unchanged

The protected deterministic execution core is unchanged:

- OMS truth and reconciliation truth.
- Kill-switch semantics.
- D-0001 hard risk caps.
- Overlay output set and bounded overlay behavior.
- Paper ledger accounting.
- Event-log discipline.
- No direct agent deployment to live.
- No agentic execution, risk changes, or promotion authority.

Research automation sits above this core. It can prepare structured evidence, but it cannot change runtime decisions or execution semantics.

## In Scope Now

Near-term packages may build candidate-agnostic research machine foundations, including:

- Candidate registry structure.
- Experiment artifact schemas for plans and reports.
- Candidate stage representation.
- Evidence comparison and ranking conventions.
- Data/query foundations for systematic multi-candidate work.
- Bounded research-agent interfaces for drafting, validation, reporting, and summarization.
- Human-review inputs for later promotion gates.

These foundations should preserve DSR, trial-log discipline, pre-registration, and existing promotion-gate thresholds.

## Out Of Scope Now

The accepted shift does not authorize:

- Strategy v1 lock-in.
- H-011 pre-registration or execution.
- Backtests, notebook execution, trial-log updates, or decision records.
- Candidate registry implementation unless specifically scoped by a later package.
- Runtime, OMS, reconciliation, overlay, risk-cap, or paper-ledger changes.
- Agentic execution or direct deployment to live.
- Numeric promotion-gate changes.
- Paid data, sub-15m data, or multi-venue expansion.

## Direction Mapping

Bounded research automation may help discover candidates, prepare experiment plans, validate report shape, summarize evidence, and compare candidates. It must remain advisory.

Candidate discovery / testing / comparison should be represented through structured artifacts linked to repo truth, not through hidden chat memory or untracked dashboards.

Structured evidence collection should make it easier for humans to understand why a candidate is backlog, registered, concluded, ranked, or shadow-ready.

Human approval is required before promotion. No automated process can approve Strategy v1, shadow deployment, live deployment, risk changes, or kill decisions.

The protected deterministic execution core remains the boundary below the research machine. Nothing in this direction changes live or paper execution semantics.
