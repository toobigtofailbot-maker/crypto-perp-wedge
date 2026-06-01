# Research Pipeline Index Consolidation Design

## 1. Scope

WP-S2c-134 / WP-12fn is a Tier 1 documentation-only design package.

This package creates only this design document and updates `docs/project_status.md`.
It does not implement the `docs/research_pipeline/README.md` index.

Validation profile: CS12 T1-doc-narrow.

## 2. Authorization basis

Main 4.0 authorized WP-S2c-134 as AUTHORIZED NOW in the 12-WP batch.

WP-S2c-135 is authorized only after WP-S2c-134 merges. WP-S2c-135 remains a
future implementation package and must still pass refreshed-main preflight and
stop-trigger checks before drafting.

## 3. Current navigation problem

`docs/research_pipeline/` has accumulated many design, schema, query-layer,
brief, locking, and tranche checkpoint documents across the Phase 2 to Phase 3
transition.

The current README has useful topic sections, but it does not yet provide a
consolidated maintenance-oriented index for the recent package stream. Future
package authorship benefits from a categorized index that points to the right
document quickly without rewriting, moving, deleting, or reinterpreting the
underlying documents.

## 4. Design objective

The future README update should create an additive, low-risk index pattern.

The index should make it easier to locate:

- schema and artifact grammar docs;
- query-layer and integrity docs;
- cross-candidate and shadow diagnostic brief docs;
- Path B design, locking, tranche, checkpoint, and integrity-refinement docs;
- Scope 6 and Stage 6-7 approval and shadow-evidence docs.

The index must avoid rewriting existing content. It must also avoid making the
README a source of truth that overrides the source documents, canonical
artifacts, locked decisions, or package-specific evidence.

## 5. Proposed README index shape

WP-S2c-135 should update `docs/research_pipeline/README.md` additively.

Prefer adding a new section named `## Consolidated Package Index` below the
existing high-level sections, unless refreshed repo-local style suggests a
better placement.

The section should include category subsections. Each entry should include:

- file path;
- one-line purpose;
- status or surface type.

Existing README bullets should remain in place. WP-S2c-135 may add pointers
without removing or reordering existing README content.

## 6. Category model

WP-S2c-135 should categorize existing research-pipeline documents without
rewriting or moving them. The index should include at least these categories:

- Core foundation and registry docs.
- Experiment / report / trial-log grammar.
- Outcome-ledger and reconciliation grammar.
- Query-layer and integrity docs.
- Scope 6 / Stage 6-7 approval and shadow-evidence docs.
- Advisory / macro / pre-gate / overlay diagnostic docs.
- Cross-candidate and shadow diagnostic briefs.
- Path B design, locking, tranche, checkpoint, and integrity-refinement docs.
- Navigation / index-maintenance docs.

The category model is navigational. It must not imply package precedence,
candidate ranking, route selection, readiness, transition, approval, or
promotion.

## 7. Entry format

Use concise bullets. Long prose summaries should stay out of the index.

Example:

- `2026-04-query_layer.md` - read-only DuckDB query layer and integrity views;
  query-layer foundation.

Entries should not include claims of current candidate state unless they point
to current brief or checkpoint documents that are already committed as source
context. Entries should not include verdict, ranking, recommendation,
readiness, transition, or route-selection language.

## 8. Maintenance rule

Future packages should add one concise index entry when they create a new
research-pipeline document.

Future packages should not rewrite old entries unless correcting a factual
path, title, or surface-type error. The index is navigational only and is not
authoritative over the source docs.

## 9. What stays out

The README index should not include:

- registry contents;
- performance metrics;
- candidate rankings;
- readiness or transition status;
- reproduction of full brief conclusions;
- locked decision reinterpretation;
- deleted, moved, renamed, or restructured files.

The index must not become a compact replacement for canonical artifacts,
query outputs, decision records, or locked architecture documents.

## 10. WP-S2c-135 implementation boundary

WP-S2c-135 may modify only:

- `docs/research_pipeline/README.md`;
- `docs/project_status.md`.

WP-S2c-135 must implement the README index additively according to this design.
It must not modify existing research-pipeline documents, canonical artifacts,
schemas, validators, query views, tools, code, tests, registry rows, trial-log
rows, EXP, REP, OL, REC, DEC, hypotheses, or notebooks.

WP-S2c-135 must not create code or tests.

## 11. Validation posture

WP-S2c-134 and WP-S2c-135 use CS12 T1-doc-narrow unless refreshed repo truth or
package-specific scope requires a stricter profile.

Validation should confirm:

- exact changed-file scope;
- `git diff --check`;
- query-layer list-view command behavior;
- all discovered `v_integrity_*` views return empty results;
- registry validators pass under current doc-narrow convention;
- experiment artifact validators pass under current doc-narrow convention;
- outcome-ledger and reconciliation validators pass under current doc-narrow
  convention;
- targeted pytest required by current CS12 T1-doc-narrow convention.

Validation output may be summarized, but the underlying commands must actually
run.

## 12. Stop conditions

Stop if the design or implementation requires:

- moving, renaming, deleting, or restructuring files;
- modifying existing research-pipeline documents besides the future README
  implementation package;
- touching locked decisions, canonical artifacts, code, tests, schemas,
  validators, query views, tools, runtime paths, or protected paths;
- readiness, recommendation, ranking, scoring, approval, transition, promotion,
  policy, or route-selection language;
- weakening validation, integrity checks, or refreshed-main preflight;
- proceeding after validation failure.

## 13. Non-authority boundary

This design creates no gate execution, candidate recommendation, transition
authority, readiness authority, policy change, locked-decision change, runtime
authority, protected-path authority, or human-gate execution authority.

The future README index will be a navigation aid only. It will not supersede
source documents, artifacts, query outputs, decision records, schemas,
validators, or locked baseline documents.

## 14. Next-package posture

After WP-S2c-134 merges, Side may auto-draft WP-S2c-135 under Main
authorization after refreshed-main preflight and no stop trigger.

WP-S2c-135 should implement the additive README index and update
`docs/project_status.md` only.
