# Walk-Forward / OOS Gate Contract

## V2 final-holdout clarification

Ordinary WFO/OOS evidence under this contract is not the protected final
holdout. Final confirmation has separate contamination-aware exposure and
consumption semantics under `D2-020`: CPW durable scientific lineage records
holdout identity/state and information-contamination ancestry, and Research
Memory is non-authoritative. A new hypothesis, lineage, branch, or run ID does
not restore holdout freshness after informative exposure unless strict
information isolation is proven.

The `pass` decision below remains scientific gate evidence only. It is not
candidate promotion, readiness, paper/live authority, or economic approval.
See `docs/architecture/2026-10-bounded_autonomous_research_v2_architecture.md`.

## Status and Authority

This contract defines a standard non-canonical walk-forward / out-of-sample
candidate gate input for research review.

It does not approve candidates, rank candidates, recommend promotion, create
readiness, write candidate lifecycle events, write Result Populations, mutate
trial logs, or contact runtime, paper/live, OMS, risk, reconciliation, broker,
exchange, or execution paths.

## Gate Artifact

The standard artifact is a JSON object with `schema_version` equal to
`oos_gate_contract.v1`. It records:

- `source_result_population`: source Result Population id, repo path, input
  identity hash, and result population identity hash.
- `source_walkforward_run`: source walk-forward run id and report path.
- `split`: split method, in-sample period, out-of-sample period, purge period,
  embargo period, window count, and minimum required windows.
- `oos_metrics`: OOS metric summary used by the gate.
- `row_variant_mapping`: row / variant mapping posture and denominator
  preservation.
- `gate_decision`: one of `pass`, `fail`, `blocked`, or `advisory_only`.
- `reason_codes`: closed-enough reason strings for review and audit.
- `canonical_status`: `non_canonical` unless a later separately authorized
  crossing package creates a canonical artifact.
- `non_authority_declaration`: explicit non-authority flags.

## Gate Semantics

`pass` means the artifact is complete and the declared OOS thresholds are met
for the non-canonical gate review. It is not promotion, readiness, ranking, or
candidate approval.

`fail` means the artifact is complete, but one or more declared OOS thresholds
are not met.

`blocked` means the artifact or inputs are incomplete, invalid, mismatched, or
not rigorous enough to evaluate.

`advisory_only` means evidence may be useful for review but must not satisfy
the candidate gate.

Candidate-review integration is read-only: a review input may cite an
`oos_gate_ref`, a `result_population_ref`, and a `walkforward_run_ref`. The
gate evaluator blocks if OOS evidence is missing, if source references do not
match, if the artifact is invalid, or if `gate_decision` is `fail`, `blocked`,
or `advisory_only`.

## Purge and Embargo

Purge and embargo are explicit required split fields:

- `purge.mode`: `bars`
- `purge.bars`: non-negative integer
- `embargo.mode`: `bars`
- `embargo.bars`: non-negative integer

If a future package cannot safely implement or validate purge/embargo, the OOS
gate artifact must use `gate_decision=blocked` or `advisory_only` with a clear
reason code. It must not pretend that an unpurged or unembargoed summary is a
rigorous gate pass.

## Candidate Gate Blocking Rules

The OOS gate blocks candidate-review passage when:

- the candidate evidence lacks an `oos_gate_ref`;
- the gate artifact is missing or invalid;
- the candidate `result_population_ref` does not match the gate source Result
  Population id;
- the candidate `walkforward_run_ref` does not match the gate source
  walk-forward report path;
- the gate artifact decision is `fail`, `blocked`, or `advisory_only`.

This blocking behavior is implemented as read-only evaluation in
`tools/oos_gate/evaluate.py`. It records zero canonical writes, zero candidate
lifecycle writes, and zero runtime actions.

## Current Fixture Decision

The package fixture uses the existing purged scratch walk-forward run
`WF-RUN-40BB0B209274054B` over source Result Population `RP-2592`.

The fixture decision is `fail` because the second OOS window has negative mean
Sharpe, below the declared minimum OOS Sharpe threshold. The maximum OOS
drawdown remains below the fixture drawdown threshold, but that does not
override the failed Sharpe criterion.

## Non-Authority Boundary

This contract does not make walk-forward / OOS evidence canonical. Any
canonical crossing, Result Population write, candidate lifecycle action,
promotion, readiness decision, paper/live work, runtime work, or protected-path
change remains outside this package and requires separate authorization.
