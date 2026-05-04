# Outcome Ledger Retrospective Backfill Methodology (WP-9m)

## Purpose

This methodology governs retrospective outcome-ledger backfill from committed
REP artifacts.

WP-9m commits one seed outcome-ledger artifact only. WP-9n or a later scoped
package applies this methodology to the remaining eligible retrospective source
REPs.

REP remains the authoritative research record. Outcome-ledger entries are
structured derivations from REP/EXP repo truth.

## Scope

WP-9m creates one seed outcome-ledger artifact and this methodology.

This package does not perform bulk backfill, change schemas, change validators,
change query-layer behavior, add an ingestion helper, create REC/reconciliation
artifacts, define promotion or demotion policy, add paper/live semantics, add
evidence-quality scoring, or change runtime/deployment behavior.

## Source Selection Rules

Every retrospective outcome-ledger entry must be derived from committed repo
truth:

- the candidate must exist in `research/candidate_registry.jsonl`
- the source REP must exist and validate
- the source REP path must satisfy the outcome-ledger validator
- the source REP must provide all required WP-9k metric fields
- source EXP/provenance references must be copied from repo truth

If multiple REP artifacts exist for one candidate or pipeline split, each
source REP must become a separate future outcome-ledger entry unless Main 3.0
later decides otherwise. The H-004 `REP-0005` / `REP-0011` split must not be
collapsed silently.

## ID Allocation Rules

WP-9m reserves and uses `OL-0001`.

Future retrospective backfill continues with `OL-0002`, `OL-0003`, and so on.
Outcome-ledger IDs are append-only and must not be renumbered after merge.

Do not create duplicate `(candidate_id, source_artifact_id, pipeline_version)`
entries unless later architecture explicitly justifies the duplicate.

## Field Mapping Rules

Map fields from committed REP/EXP truth:

- `candidate_id`: source REP candidate ID, which must resolve to the registry
- `outcome_kind`: `research_oos`
- `lifecycle_state_during_window`: `in_research`
- evaluation windows: source EXP/REP OOS window endpoints, or `null` / `null`
  when repo truth preserves the no-formal-split convention
- `metrics`: source REP `metrics.out_of_sample` values using WP-9k names
- `data_provenance`: source EXP data requirements and committed source-data
  window endpoints when present
- `derivation_record`: `from_rep_artifact`, source REP ID/path, and the
  backfill derivation timestamp
- `pipeline_version`: `pre_wp_5b` or `post_wp_5b` from repo-truth semantics
- `linked_artifacts`: at least the source REP and safely linked EXP
- `linked_advisory_artifacts`: copy only explicit safe committed advisory links
- `retrospective_flag`: `true`
- `retrospective_disclosure`: disclose post-hoc derivation and non-authority
- `notes`: concise factual clarifications only

## Metric Rules

Metric names must match the WP-9k schema and committed REP metric names.

Do not invent missing metrics, rename metrics, or derive new metrics during
backfill unless a later package explicitly authorizes that. Optional post-WP-5b
diagnostic fields may be copied only when present in the source REP.

## Pipeline-Version Rules

`pre_wp_5b` and `post_wp_5b` are disclosure labels. Entries with different
pipeline versions are not automatically comparable.

The H-004 split must preserve pipeline distinction: `REP-0005` records
historical retrospective pre-WP-5b evidence, while `REP-0011` records the later
post-WP-5b forward-flow re-execution.

Future consumers must respect the OL-4 insufficient-evidence floor.

## Window Rules

No-formal-split source artifacts may use `null` / `null` window pairs.

One-sided null windows are invalid. If both endpoints exist, the end must be
greater than or equal to the start.

Artifact timestamp gaps and derivation timestamps do not become evaluation
window boundaries.

## Validation Requirements

Every future backfill package must run:

- outcome-ledger validator
- existing validators
- outcome-ledger overview and integrity views
- all discovered `v_integrity_*` views
- targeted tests
- full pytest
- `git diff --check`
- preservation hash checks

## Non-Claims

Outcome-ledger retrospective backfill creates no:

- promotion or demotion conclusion
- candidate-quality ranking
- evidence-quality scoring
- REC/reconciliation conclusion
- paper/live eligibility
- fast-track conclusion
- runtime/deployment authority
- strategy adjustment authority
- claim that one seed entry satisfies the OL-4 inference floor

## WP-9n Handoff

WP-9n should consume this methodology unchanged unless repo truth reveals a
contradiction.

WP-9n should backfill remaining eligible REP-derived outcome-ledger entries,
handle the H-004 `REP-0005` / `REP-0011` split explicitly, avoid duplicating
`OL-0001`, report any REP that cannot populate required schema fields, and not
introduce policy, REC/reconciliation, promotion, paper/live, helper, runtime,
or deployment behavior.

## WP-9n Application Note

WP-9n applied this methodology unchanged to the remaining eligible committed
REP-derived retrospective sources. `OL-0001` was preserved, `OL-0002` through
`OL-0011` were allocated append-only by remaining source REP order, and the
H-004 `REP-0005` / `REP-0011` split was preserved as distinct pre-WP-5b and
post-WP-5b outcome-ledger entries.

This application note changes no methodology rules and adds no policy,
REC/reconciliation, promotion, paper/live, helper, runtime, or deployment
behavior.
