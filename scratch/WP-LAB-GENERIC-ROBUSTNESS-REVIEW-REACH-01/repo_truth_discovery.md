# WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01 Repo-Truth Discovery

## Base And Branch

- Worktree: `C:\GitHub\crypto-perp-wedge-worktrees\lab-generic-robustness-review-reach-01`
- Branch: `lab/generic-robustness-review-reach-01`
- Base: `origin/main` at `2b2c3d886fde7e5ed01eed87bba3dbf0ea10c94a`
- Base commit is PR #563 merge: `Merge pull request #563 ... research/funding-carry-02-retry-01`

## Search Scope

Searched repo markdown, Python, JSON, and scratch/research surfaces for robustness, candidate-review, review packet, PSR, DSR, MinTRL, Monte Carlo, family, funding-rate positioning fade, SMA, Donchian, Result Population, gate, and `WP-RESEARCH-FUNDING-CARRY-02`.

## Inspected Surfaces

- Robustness diagnostician: `tools/research_agents/robustness_diagnostician_agent.py`
- Candidate-review packet agent: `tools/research_agents/candidate_review_packet_agent.py`
- Candidate lifecycle packet wrapper: `tools/candidate_lifecycle/build_candidate_review_packet.py`
- Advisory robustness MC: `tools/robustness/seeded_advisory_mc.py`
- Robustness depth: `tools/robustness/robustness_depth.py`
- Candidate registry validator: `tools/registry/validate_registry.py`
- Result Population validator: `tools/registry/validate_result_populations.py`
- Query views: `tools/research_query/views.sql`
- Candidate registry: `research/candidate_registry.jsonl`
- Result Population schema: `research/schemas/result_population.schema.json`
- Candidate registry schema: `research/schemas/candidate_registry.schema.json`
- PR #563 status entry: `docs/status_entries/WP-RESEARCH-FUNDING-CARRY-02.md`
- Existing tests for robustness/candidate-review packet behavior.

## Facts

- Current merged repo truth includes `WP-RESEARCH-FUNDING-CARRY-02` as a scratch-only funding-rate positioning-fade run.
- PR #563 added scratch funding-family artifacts, two scratch Result Population-shaped outputs (`RP-2009`, `RP-7592`), robustness summaries, a no-candidate-review-packet reason artifact, and validation evidence.
- The funding package records 36 planned and 36 completed rows with denominator preserved.
- The funding package records NO-GO because all 36 rows failed the existing primary drawdown screen.
- The funding package records that no candidate-review packet was generated.
- The funding package records PSR, DSR, and MinTRL withheld for missing inputs rather than fabricated.
- The funding package records no candidate registration, no crossing, no funding P&L/accounting change, no runtime/paper/live contact, and no protected-path authority.
- Existing robustness diagnostician and candidate-review packet agents are scratch-only, non-authoritative, and ToolContext-routed.
- Existing candidate-review packet agent contains SMA-specific strategy summary text, so it is not used as the generic implementation path in this reduced-mode package.
- Existing query views expose candidate families, result-population integrity, and non-authority surfaces, but this package does not edit query-layer behavior.
- Candidate registry currently includes multiple families: funding directional, trend following, mean reversion, momentum, breakout, funding momentum composite, multi-timeframe alignment, basis mean reversion, and cross-asset reserved slot.

## Inferences

- A generic review reach contract can be authored without replay/OOS API dependencies if it treats replay/OOS status as optional or blocked.
- Deeper implementation in shared `tools/robustness/**` or candidate-review tooling would risk overlapping active robustness/candidate-review work and could require unmerged replay/OOS contracts.
- The safe reduced-mode path is docs plus scratch fixtures plus isolated tests.

## Decision

- Continue in reduced mode.
- Do not edit `tools/robustness/**`, `tools/candidate_review/**`, replay/normalization code, OOS gate code, candidate lifecycle artifacts, Result Populations, registry, schemas, validators, query-layer behavior, runtime, paper/live, OMS, risk, reconciliation, capital, funding P&L/accounting, provider/API/network, dashboard, scheduler, or large data paths.

## Open Questions

- Future implementation may need a merged replay-normalization contract before normalizing Result Population identity across scratch and canonical sources.
- Future implementation may need a merged OOS gate contract before machine-checking `oos_gate_status`.
- Future candidate-review packet tooling may need a separate genericization package to remove SMA-specific strategy summary assumptions.
