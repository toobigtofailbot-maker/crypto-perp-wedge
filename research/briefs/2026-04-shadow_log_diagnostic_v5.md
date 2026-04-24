# Shadow-Log Diagnostic Brief v5

**Date:** 2026-04-24
**Scope:** Committed overlay shadow-log evidence exposed by the current query layer after the helper-produced corpus expansion through `OSH-0010`.
**Evidence source:** Stored SQL queries and JSON outputs under `research/briefs/2026-04-shadow_log_diagnostic_v5/`.
**Does not introduce:** Shadow-log entries, fixtures, advisory artifacts, query-layer changes, schema changes, validator changes, helper changes, or runtime behavior.
**Does not recommend:** Signal semantics, overlay influence, promotion, demotion, override policy, or non-shadow execution use.

## 1. Purpose

This brief is the fifth diagnostic consumption of committed overlay shadow-log evidence and the first one over the expanded two-axis corpus that now varies along both advisory lineage and overlay-input fixture identity. It follows the same diagnostic-only discipline as v4 while extending the output set to cover the committed corpus through `OSH-0010` and the `_02` overlay-input pair (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q06`, `outputs/Q06.json`; `Q07`, `outputs/Q07.json`; `Q08`, `outputs/Q08.json`; `Q09`, `outputs/Q09.json`).

What changed since v4 is structural, not semantic. The committed corpus expanded from `n = 6` to `n = 10`; the first committed noncanonical-overlay-input shadow batch added `OSH-0007` through `OSH-0010`; and the second overlay-input identity is now committed evidence rather than dry-run-only fixture evidence (`Q01`, `outputs/Q01.json`; `Q06`, `outputs/Q06.json`; `Q09`, `outputs/Q09.json`).

The purpose remains interpretation discipline, not policy action. This brief records what the current committed evidence says across both dimensions, where observed differences are attributable, where they are only associated, and where the evidence remains insufficient for causal weight (`Q03`, `outputs/Q03.json`; `Q08`, `outputs/Q08.json`; `Q09`, `outputs/Q09.json`).

## 2. Evidence Scope And Query Bundle

Q01 through Q05 preserve the established v4 diagnostic surfaces: entry-level overview, latest-per-lineage, advisory-source agreement summary, zero-override audit, and reference integrity audit (`Q01`, `outputs/Q01.json`; `Q02`, `outputs/Q02.json`; `Q03`, `outputs/Q03.json`; `Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`).

Q06 through Q09 add the two-axis segmentation without changing the query layer. They read the committed `overlay_shadow_logs` relation directly so the brief can segment on `observation_source.snapshot_path` plus `observation_source.config_path` while still using the existing repo-truth views for the core overview and audit surfaces (`Q06`, `outputs/Q06.json`; `Q07`, `outputs/Q07.json`; `Q08`, `outputs/Q08.json`; `Q09`, `outputs/Q09.json`).

The output naming follows the established diagnostic-bundle idiom: `run_all_queries.py` writes `outputs/Q01.json` through `outputs/Q09.json` rather than descriptive JSON filenames. That mirrors v2-v4 exactly and keeps the bundle aligned with the current local naming convention.

## 3. Current Two-Axis Evidence State

The current corpus contains `n = 10` committed shadow rows (`Q01`, `outputs/Q01.json`). Q06 shows two committed overlay-input fixture identities:

- `canonical`: `tests/fixtures/context_snapshot_sample.json` plus `configs/fmp_macro_flags.json`
- `_02`: `tests/fixtures/context_snapshot_sample_02.json` plus `configs/fmp_macro_flags_02.json`

The advisory-source view alone does not explain the comparison class. Q03 reports that both `BMAP` and `PGAS` now contain one `MATCH` lineage and one `MISMATCH` lineage: `BMAP MATCH = 2`, `BMAP MISMATCH = 3`, `PGAS MATCH = 2`, and `PGAS MISMATCH = 3` (`Q03`, `outputs/Q03.json`).

The fixture-identity view alone also does not explain the comparison class inside a lineage. Q09 shows four advisory lineages, and every one of them preserves the same comparison class across the canonical pair and the `_02` pair:

- `BMAP` + `BMAP-0001` remains `MISMATCH` on both fixture identities
- `PGAS` + `BMAP-0001` + `PGAS-0002` remains `MISMATCH` on both fixture identities
- `BMAP` + `BMAP-0002` remains `MATCH` on both fixture identities
- `PGAS` + `BMAP-0002` + `PGAS-0003` remains `MATCH` on both fixture identities

That makes the current observed class difference most strongly associated with advisory artifact lineage, not with advisory source alone and not with fixture identity alone. The `BMAP-0001` / `PGAS-0002` lineages remain mismatch lineages, while the `BMAP-0002` / `PGAS-0003` lineages remain match lineages (`Q06`, `outputs/Q06.json`; `Q08`, `outputs/Q08.json`; `Q09`, `outputs/Q09.json`).

## 4. Attribution Discipline

The current corpus supports attribution at the level of stable observation, not stable cause. It is fair to say that pattern differences are source-lineage-associated because the comparison class changes with the advisory artifact lineage and remains stable when the fixture identity changes within that lineage (`Q09`, `outputs/Q09.json`).

It is also fair to say that some latest-row shifts are fixture-driven in a structural sense. For all four lineages, the latest overall row now lives on the `_02` fixture pair rather than the canonical pair, but the advisory source, lineage membership, observed overlay bucket, mapped bucket, and comparison class stay unchanged when that latest-row shift occurs (`Q07`, `outputs/Q07.json`; `Q09`, `outputs/Q09.json`).

It is not yet honest to assign causal weight to fixture identity, advisory source family, or lineage-specific upstream conditions beyond that observed association. The current two-axis corpus is still a small committed sample, and this package does not define what `MATCH` or `MISMATCH` should mean operationally (`Q03`, `outputs/Q03.json`; `Q08`, `outputs/Q08.json`; `Q09`, `outputs/Q09.json`).

## 5. Latest-State Summary By Lineage

Q02 preserves the existing latest-per-lineage surface and Q09 makes the fixture transition explicit. The current latest rows are:

- `OSH-0007` for `BMAP` + `BMAP-0001`
- `OSH-0009` for `BMAP` + `BMAP-0002`
- `OSH-0008` for `PGAS` + `BMAP-0001` + `PGAS-0002`
- `OSH-0010` for `PGAS` + `BMAP-0002` + `PGAS-0003`

Each of those latest rows is on the `_02` fixture identity (`Q02`, `outputs/Q02.json`; `Q07`, `outputs/Q07.json`; `Q09`, `outputs/Q09.json`).

The latest-row shift to `_02` does not change the comparison class inside any lineage. The canonical/latest pair for each mismatch lineage stays `MISMATCH`, and the canonical/latest pair for each match lineage stays `MATCH` (`Q07`, `outputs/Q07.json`; `Q09`, `outputs/Q09.json`).

## 6. Boundary Checks

Q04 returns an empty JSON array, so the zero-override audit remains clean in the current committed corpus (`Q04`, `outputs/Q04.json`).

Q05 also returns an empty JSON array, so the shadow-reference integrity surface remains clean in the current committed corpus (`Q05`, `outputs/Q05.json`).

These clean audit outputs confirm that the current diagnostic brief remains an evidence-consumption package only. They do not justify any downstream signal definition, override path, or runtime influence.

## 7. Evidence Limit

The expanded corpus now supports honest two-axis observation at `n = 10`. It is enough to say that:

- both source families now contain both `MATCH` and `MISMATCH` evidence
- both committed fixture identities now contain both `MATCH` and `MISMATCH` evidence
- the current comparison class is stable within each advisory lineage across canonical and `_02` fixture identity
- some latest-row changes are associated with fixture identity, but attribution remains limited

It is not enough to infer a stable agreement rate, disagreement rate, fixture-quality ranking, source-family quality ranking, or causal explanation. The evidence remains diagnostic-only and insufficient for policy inference.

## 8. Explicit Conclusion

The honest current conclusion is that the expanded corpus now supports joint observation across advisory lineage and overlay-input fixture identity, while remaining evidence-limited. Observed pattern differences are currently associated most strongly with advisory lineage, not advisory source alone and not fixture identity alone, but the evidence is still insufficient to attribute causal weight (`Q03`, `outputs/Q03.json`; `Q08`, `outputs/Q08.json`; `Q09`, `outputs/Q09.json`).

All four latest lineage rows now live on the `_02` fixture identity, yet their lineage-level comparison classes remain unchanged. Override audit remains zero, integrity refs remain clean, and this package does not define what agreement or disagreement should mean operationally (`Q04`, `outputs/Q04.json`; `Q05`, `outputs/Q05.json`; `Q09`, `outputs/Q09.json`).

## 9. Artifacts In This Directory

- `queries/Q01..Q09*.sql`: exact read-only SQL used for this brief.
- `outputs/Q01.json` through `outputs/Q09.json`: committed JSON outputs from the stored SQL.
- `run_all_queries.py`: convenience helper to regenerate the JSON outputs through the read-only query CLI.
