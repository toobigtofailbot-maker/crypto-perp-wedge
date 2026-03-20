# Phase 2 Mandate — Strategy Research Program (Ambitious Option B)

## Goal

Build a small-scale, realistic but highly intelligent “Aladdin-like” research and decision-support layer:

* aggregate many relevant inputs (venue, stats, regimes, macro, narrative)
* produce structured outputs: rankings, confidence scores, setup evaluations
* keep execution core deterministic and safety-railed

## What Phase 2 must produce (deliverables)

1. Strategy Candidate Set (2–3 serious candidates)

   * each with a clear spec: entry/exit, regime logic, sizing, turnover controls, failure modes
2. Evaluation Protocol

   * segmentation, robustness checks, ablation expectations
   * paper evaluation plan
3. Strategy v1 selection + spec lock

   * one chosen v1 for paper → promotion gate decision
4. Promotion gates v1 (paper → staged live)

   * objective pass/fail criteria

## What Phase 2 must NOT do

* do not loosen D-0001 caps
* do not change OMS/reconciliation semantics
* do not introduce agentic execution

## Candidate exploration rule

Phase 2 is allowed to rethink the strategy approach.
However: every candidate must be testable with our current deterministic pipeline and must not require HFT infra.

## “Aladdin-like” interpretation (small-scale)

* The aim is not a single rigid strategy.
* The aim is a structured engine that:

  * generates hypotheses
  * tests them reproducibly
  * ranks setups with a confidence score
  * and only then routes to deterministic execution controls

## Output bias control

This repo intentionally does not preload “the best strategy”.
Phase 2 should propose candidates based on evidence and clear tradeoffs, not on prior chat opinions.
