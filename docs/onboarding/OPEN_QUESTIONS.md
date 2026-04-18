# Open Questions (Phase 2)

Phase 2 now includes candidate-agnostic research machine foundation work before Strategy v1 lock-in. These questions should guide registry, schema, pipeline, and bounded research automation packages without changing protected execution semantics.

## Candidate Registry

* What fields are required to track a candidate before, during, and after hypothesis pre-registration?
* How should candidate stages be represented: backlog, draft, registered, running, concluded, ranked, shadow-ready, archived?
* How should H-011-style future candidates be tracked without making them the organizing principle or bypassing pre-registration?

## Experiment Artifacts

* What structured fields belong in experiment plans before a run is eligible for trial-log entry?
* What report schema should capture metrics, gate results, failure modes, data references, and decision links?
* How should artifact hashes, dataset provenance, and irreparable-gap handling be represented for repeatable multi-candidate work?

## Comparison / Ranking

* What evidence fields are safe to compare across candidates without creating an overfitting leaderboard?
* How should ranking distinguish raw performance, robustness, cost drag, parameter stability, regime concentration, and implementation readiness?
* How should concluded NO-GO evidence remain visible so future work does not retest near-duplicates accidentally?

## Bounded Research Automation

* Which bounded agent interfaces are needed first: registry drafting, artifact validation, report assembly, candidate comparison, or evidence summarization?
* What permissions and output contracts keep bounded research automation out of execution, risk, and promotion authority?
* How should automation support exploratory EDA while preserving the distinction between scratch exploration and registered evidence?

## Human-Gated Promotion

* What structured artifacts should human reviewers consume before approving shadow readiness or Strategy v1 selection?
* How should promotion gates consume registry status, experiment reports, trial logs, and decision records without changing D2-006 thresholds?
* What explicit review checkpoints are required before any candidate can move from research evidence to shadow integration?

## Data / Query Layer

* What query layer is needed for systematic multi-candidate and multi-timeframe analysis over catalogued BTCUSDT data?
* How should pipeline foundations expose data readiness, known gaps, and timeframe status without duplicating repo truth?
* What summaries should be generated for candidate discovery while keeping raw data, notebooks, and audit artifacts out of normal package scope?
