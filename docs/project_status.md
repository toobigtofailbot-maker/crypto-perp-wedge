# Project Status

This file is the current-state anchor. Read it before architecture, execution, implementation, or review work. Update it after meaningful merges that change repo state.

Startup read order:

1. `docs/project_status.md`
2. `CLAUDE_START_HERE.md`
3. `docs/runbook.md`

## Project Identity

- Instrument: BTCUSDT Binance USDT-M perpetual.
- Runtime foundation: deterministic paper/runtime core from Phase 1.
- Current program: Phase 2 candidate-agnostic research machine progression toward structured BTC strategy evidence, comparison, and later human-gated promotion.
- Locked Phase 2 timeframe set: `15m`, `30m`, `1h`, `4h`, `1d`.
- Timeframe rule: no single global primary timeframe is fixed. Each candidate declares its primary timeframe and any allowed confirmation timeframes before testing.

## Current Phase / Repo State

- Phase 1 is closed.
- Phase 2 baseline is locked in `docs/onboarding/PHASE2_BASELINE.md`.
- WP-1a Batch 1, WP-1a Batch 2 corrected, WP-1b, WP-1c, the current-state-anchor package, OPS-02, WP-2b, WP-2c, WP-3b, WP-3c, WP-4a, WP-4b1, WP-4b2, WP-5a, and WP-5b are merged to `main`.
- Current repo state is research-first: build a candidate-agnostic BTC research machine for systematic candidate discovery, testing, comparison, and later human-gated promotion without weakening protected execution boundaries.
- Strategy v1 is not locked. Immediate architecture work may be registry / schemas / pipeline foundations rather than candidate-specific execution.
- H-011 remains a possible future backlog candidate, not the organizing principle of the next architecture step.

## Key Architecture References

- Long-term roadmap, automation, managed-agent, dashboard, and self-improvement scope is locked in `docs/architecture/LONG_TERM_SCOPE.md`.
- Accepted research machine direction is documented in `docs/architecture/RESEARCH_MACHINE_DIRECTION.md`.

## Merged Work Package Ledger

Naming convention: `WP-*` is reserved for Main Architecture research/execution work packages. `OPS-*` is reserved for repo-maintenance, workflow, and entrypoint addenda outside the main research package chain.

| Package | Status | PR / merge ref | Outcome |
|---|---|---|---|
| WP-0 baseline lock | Merged | PR #17 / `b0149b2` | Locked Phase 2 baseline and D2-001 through D2-017 references. |
| WP-1a Batch 1 | Merged | PR #18 / `1282f4f` | Added full BTCUSDT history foundation for locked research timeframes and funding. |
| WP-1a Batch 2 corrected | Merged | PR #19 / `284a7f8` | Added corrected mark/index/premium history and irreparable official-source-gap policy. |
| WP-1b | Merged | PR #20 / `42b450a` | Added research workbench, backtest/evaluation scaffolding, trial log support, and dependencies. |
| WP-1c | Merged | PR #21 / `f51ec44` | Added orchestration scaffold, agent/skill definitions, and research/evaluation prompt artifacts. |
| OPS-01 - current-state anchor | Merged | PR #22 / `77d9ec5` | Added this current-state anchor and entrypoint references. |
| WP-5a pipeline audit | Merged | PR #35 / `032a6d8` | Audited the research instrument and found minor pipeline issues; existing NO-GO verdicts remained valid. |
| WP-5b pipeline fixes | Merged | PR #36 / `cbb6877` | Fixed bounded-equity / liquidation semantics and Gate 5 pass/fail behavior; preserved all 10 overall NO-GO verdicts. |

## Locked / Do-Not-Touch Boundaries

Protected unless a package explicitly authorizes the change and the locked decision process supports it:

- OMS truth / reconciliation truth.
- Kill-switch semantics.
- D-0001 hard risk caps.
- Overlay output set `{ALLOW, ALLOW_REDUCED=0.5, BLOCK}` and fail-open behavior.
- Paper ledger accounting math.
- Event log schema except explicit additive changes.
- No agentic execution or autonomous risk/execution changes.
- Phase 1 paper runtime remains protected while Phase 2 research proceeds through the workbench and later shadow path.

## Data Status

- Free Binance sources are the authoritative Phase 2 dataset path.
- Current repo documentation covers full BTCUSDT OHLCV, funding, mark price, index price, and premium index history for the locked timeframe set.
- Provenance belongs in `docs/data_catalog.md`; raw and processed data contents are not package-edit targets unless explicitly authorized.
- Known irreparable official-source gaps are tracked by `data/irreparable_gaps.json` and governed by D2-003A plus `docs/irreparable_gaps_policy.md`.
- WP-3b intraday assessment confirms existing 1h and 30m OHLCV data are sufficient for H-005 / H-006 baseline execution; 15m OHLCV is also ready for future OHLCV-only hypotheses.

## Research / Workbench Status

- Phase 2 uses the lightweight research backtester/evaluation path for hypothesis testing.
- The audited research instrument exists and WP-5b bounded fixes are merged.
- Promotion gates, DSR/trial-log discipline, and pre-registration remain the overfitting firewall.
- Final Strategy v1 is not locked.
- Candidate-agnostic research machine foundation work is now explicitly in scope before Strategy v1 lock-in.
- Long-term research direction targets a multi-strategy, multi-timeframe portfolio rather than concentration in a single strategy or timeframe.
- H-001 and H-002 are CONCLUDED / NO-GO after 4h baseline execution.
- H-003 and H-004 are CONCLUDED / NO-GO after 1d baseline execution; 1d is in Cold Storage.
- H-005 is CONCLUDED / NO-GO after 1h baseline execution.
- H-006 is CONCLUDED / NO-GO after 30m baseline execution.
- WP-3b created DEC-0003 and DEC-0004 and grew `research/trial_log.jsonl` from 2 to 4 rows.
- WP-3c created DEC-0005 and DEC-0006 and grew `research/trial_log.jsonl` from 4 to 6 rows.
- WP-4a created the H-001 through H-006 failure analysis, documented alternative families, and registered H-007 through H-010 without new backtests or trial-log entries.
- WP-4b1 executed H-007 and H-010 4h cross-stream baselines, created DEC-0007 and DEC-0010, and grew `research/trial_log.jsonl` from 6 to 8 rows.
- H-007 is CONCLUDED / NO-GO after 4h funding + momentum baseline execution.
- H-010 is CONCLUDED / NO-GO after 4h basis / premium mean-reversion baseline execution.
- WP-4b2 executed H-008 and H-009 intraday confirmation baselines, created DEC-0008 and DEC-0009, and grew `research/trial_log.jsonl` from 8 to 10 rows.
- H-008 is CONCLUDED / NO-GO after 1h premium-confirmed momentum baseline execution (Sharpe -0.15, Max DD 3929%, 5211 trades, 3/8 gates).
- H-009 is CONCLUDED / NO-GO after 30m multi-timeframe alignment baseline execution (Sharpe -0.16, Max DD 925%, 2148 trades, 2/8 gates).
- Hypothesis status count: 10 CONCLUDED / NO-GO; 0 DRAFT / pending.
- 4h is back in Cold Storage after H-007 and H-010 also failed D2-006 promotion gates.
- 1h is now in Cold Storage after H-005 and H-008 both failed D2-006 promotion gates (two hypothesis cycles exhausted per D2-017).
- 30m is now in Cold Storage after H-006 and H-009 both failed D2-006 promotion gates (two hypothesis cycles exhausted per D2-017).
- Brief phase note: WP-4b2 executed; reset batch complete (H-007..H-010). Zero passing candidates across entire reset batch. All tested timeframes (1d, 4h, 1h, 30m) now in Cold Storage. Only 15m remains in PLANNING.
- DEC-0008: research/decisions/DEC-0008.md | DEC-0009: research/decisions/DEC-0009.md

## Orchestration / Skills / Prompts Status

- `.claude/` contains bounded agent operating guidance and role/skill scaffolding from WP-1c.
- `prompts/` contains execution, report-back, review, hypothesis, and evaluation templates.
- Orchestration is a thin repo-first workflow layer. It does not own runtime state or execution decisions.
- Default execution flow is Main Architecture -> Claude Code / Codex direct execution brief. Separate Karl Architecture handoff/review is optional and used only when explicitly requested.
- OPS-CODEX-01 branch-state: repo-side Codex operating-model guidance added via `AGENTS.md`, protected-path overrides, and `docs/ai/codex` guidance; no runtime, research artifact, schema, validator, query-layer, or execution behavior changed.
- OPS-CODEX-02 branch-state: Codex guidance precedence order is now explicit; current merged repo truth and active work package scope outrank general Codex guidance, no runtime authority was added, and no code behavior changed.

## Deferred But Intentional Items

- Final candidate selection and promotion decisions.
- Shadow adapter and research-to-paper parity package.
- Phase 3 live-path hardening and monitoring.
- Platform migration or deeper execution refactors unless later justified by locked architecture.
- Sub-15m and paid/tick-level data work for Phase 2.

## Current Open Risks / Architecture Questions

- Which fields belong in the candidate registry so future H-011-style candidates can be tracked without pre-registering them prematurely.
- Which experiment plan and report schemas are required before further multi-candidate work.
- How candidate stages, ranking, comparison, and evidence status should be represented without weakening DSR/trial-log discipline.
- Which bounded research-agent interfaces are useful first, while keeping agents out of execution, risk, and promotion authority.
- What query/data layer is required for systematic multi-candidate work while preserving irreparable-gap handling and provenance.

## Next Expected Package / Immediate Architecture Need

WP-5b is merged and the audited research instrument is suitable for further research. The reset batch (H-007..H-010) is fully concluded with zero passing candidates. All tested timeframes (1d, 4h, 1h, 30m) are now in Cold Storage.

The accepted next architecture tranche is candidate-agnostic research machine foundation work: registry, schemas, evidence/report conventions, and pipeline foundations. The next package class is not immediate Strategy v1 lock-in and not automatic H-011 execution.

- WP-5a pipeline audit completed; see `docs/audits/2026-04-pipeline_audit.md`
- Audit verdict: MINOR ISSUES (no liquidation model; cost-drag edge cases; all NO-GO verdicts remain valid)
- WP-5b pipeline fixes completed; see `docs/fixes/2026-04-pipeline_fixes.md`
- F-001 bounded-equity / liquidation: fixed
- F-002 Gate 5 pass/fail for non-positive gross_pnl: fixed
- All 10 existing overall NO-GO verdicts preserved (logical argument, Section 3 of fix report); Gate 3/5 pass/fail assignments for individual trials may differ post-fix, which is expected
- WP-6a (reframed) merged: Candidate Registry and Experiment Plan/Report schemas introduced. H-001..H-010 backfilled; H-011 slot reserved (not pre-registered yet). Schemas validated by regression tests. Foundational data-layer for multi-candidate research pipeline; no execution-core changes, no strategy lock, no agent work. See docs/research_pipeline/README.md.
- WP-6b merged: first experiment plan/report instance (EXP-0001/REP-0001) created retrospectively for H-005 to exercise the artifact grammar end-to-end.
- WP-6c merged: retrospective EXP/REP backfill for H-001..H-004, H-006..H-010 (nine candidates). Artifact grammar coverage now symmetric across all ten concluded candidates. No schema changes. No registry changes. No backtests re-run.
- WP-6d merged: DuckDB read-only query layer over registry and experiments; cross-candidate analysis now queryable.
- WP-6e merged: first query-layer-driven cross-candidate diagnostic brief authored; Diagram 2 stages 1-2 exercised with committed evidence artifacts.
- WP-6f merged: schemas and validators for Diagram 2 stages 6-7 (decision_change, release_notes); query layer extended to recognize these artifact types. No instances authored.
- WP-6g merged: first retrospective decision_change + release_notes pair authored for H-005 historical NO-GO / cold-storage-equivalent outcome; Stage 6-7 loop now exercised with real instances.
- WP-6h merged: first real-time forward-flow plan/report pair executed for H-004 under the current post-WP-5b pipeline; historical retrospective H-004 artifacts preserved alongside the new run.
- WP-7a merged: first deterministic bounded advisory agent stub (Regime/Scoring) added with schema-validated agent output and additive query-layer support; no execution-side wiring.
- WP-6i merged: first forward-flow decision_change + release_notes pair authored for H-004 using REP-0011 as current evidence; loop now exercised end-to-end on fresh evidence.
- WP-6j merged: first deterministic advisory score bucket mapper stub added, translating Regime/Scoring agent output into bounded ALLOW / ALLOW_REDUCED / BLOCK bucket mappings with no overlay contact.
- WP-7c merged: first external overlay shadow hook added, logging mapper-vs-overlay comparison evidence with zero override and no `lib/` changes.
- WP-7d merged: first aggregate overlay-shadow signal views added, summarizing agreement/disagreement evidence and auditing zero-override behavior over the committed shadow-log family.
- WP-7e merged: first shadow-log diagnostic brief added, consuming aggregate shadow-signal views and documenting the current evidence state without recommending policy change.
- WP-7f merged: first deterministic macro/narrative advisory agent stub added, fixture-backed and candidate-agnostic, producing a macro-window output with no runtime influence.
- WP-7g merged: first pre-gate advisory snapshot family added, bundling regime output, bucket mapping, and macro-window output into one candidate-agnostic advisory snapshot with no combination rule or runtime influence.
- WP-7h branch-state: first pre-gate advisory combination rule v1 adds `MACRO_AWARE_FLOOR`, the first non-NONE `combination_rule_applied`, and the first committed combined-bucket PGAS instance (`PGAS-0002`) with no runtime influence.
- WP-7i branch-state: shadow hook v2 now consumes the PGAS combined advisory bucket additively, `OSH-0002` is the first PGAS-source overlay shadow log, and shadow evidence/query surfaces now distinguish `advisory_source` with no runtime influence.
- WP-7j branch-state: second shadow-log diagnostic brief consumes both `OSH-0001` and `OSH-0002`, uses advisory-source-segmented shadow evidence, and encodes no runtime influence or policy change.
- WP-7k branch-state: manual / on-demand shadow-run helper added under `tools/shadow`, dry-run remains the default, writes require an explicit flag and corpus validation, and the package introduces no scheduler, trigger infrastructure, committed new OSH entry, or runtime influence.
- WP-7l branch-state: first committed helper-produced shadow batch added `OSH-0003` and `OSH-0004`, extending the corpus beyond `OSH-0001` and `OSH-0002`; the batch size followed the locked diversity fallback rule and resolved to 2 because only two distinct helper-accepted combinations currently exist, with no helper/runtime/schema/query-layer behavior change and no policy or runtime influence encoded.
- WP-7m branch-state: third shadow-log diagnostic brief consumes the expanded committed corpus through `OSH-0004`, uses advisory-source-segmented shadow evidence, and encodes no runtime influence or policy change.
- WP-7n branch-state: advisory-input diversification adds a second committed upstream artifact set (`AOUT-0002`, `MOUT-0002`, `BMAP-0002`, `PGAS-0003`), so the mapper and rule-applied PGAS latest-state surfaces now observe differentiated committed inputs; no shadow entries were added, and no code/schema/query/runtime behavior change or policy/runtime influence is encoded.
- WP-7o branch-state: second helper-produced shadow batch adds `OSH-0005` and `OSH-0006`, extends the committed shadow corpus beyond `OSH-0004`, and exercises the diversified advisory-state path introduced by WP-7n; no helper/runtime/schema/query-layer behavior changed, and no policy or runtime influence is encoded.
- WP-7p branch-state: fourth shadow-log diagnostic brief consumes the committed shadow corpus through `OSH-0006`, records both the historical mismatch lineages and the first diversified match lineages, and encodes no runtime influence or policy change.
- WP-7q-prep branch-state: the manual shadow-run helper now accepts additive explicit overlay-input fixture paths through a paired helper-only CLI surface, canonical default behavior remains unchanged, both-or-neither explicit-path pairing is enforced, and no new fixtures, shadow entries, runtime influence, or policy change are encoded.
- WP-7q branch-state: additive overlay-input fixture diversification introduces a second committed overlay-input fixture set (`tests/fixtures/context_snapshot_sample_02.json` plus `configs/fmp_macro_flags_02.json`), documents that independent variation is honest across the four helper-consumable fixture combinations, and proves the merged helper can dry-run the new repo-resident fixture paths through the paired explicit-path surface; no shadow entries were added, and no helper/runtime/schema/query-layer behavior or policy/runtime influence is encoded.
- WP-7r-prep branch-state: the overlay-shadow-log schema and validator now accept explicit noncanonical committed overlay-input path references additively through `observation_source.snapshot_path` plus `observation_source.config_path`, existing canonical entries remain valid unchanged, explicit overlay-input pairing is enforced, and no new shadow rows, helper/runtime/query-layer behavior changes, or policy/runtime influence are encoded.
- WP-7r-helper branch-state: the manual shadow-run helper now sends explicit noncanonical overlay-input pairs through the same corpus validation path as canonical inputs, `--write` now succeeds for schema-valid explicit paired inputs, and the package changes only helper/documentation alignment with no schema/query/runtime/policy influence and no committed new shadow rows.
- WP-7r branch-state: third helper-produced shadow batch adds `OSH-0007` through `OSH-0010`, consumes the honest write-valid subset of the expanded combinatorial space through the `_02` explicit overlay-input pair, and changes no helper/runtime/schema/query-layer behavior while encoding no policy or runtime influence.
- WP-7s branch-state: fourth shadow-log diagnostic brief characterizes the expanded two-axis shadow corpus jointly across advisory lineage and overlay-input fixture identity, while changing no helper/runtime/schema/query-layer behavior and encoding no signal-definition, policy, or runtime influence.
- WP-7t branch-state: first committed shadow-signal summary family adds `research/schemas/shadow_signal_summary.schema.json`, `tools/registry/validate_shadow_signal_summaries.py`, additive query-layer summary/integrity surfaces, and `SSS-0001` over the current corpus through `OSH-0010`; Option A with a static floor of 10 observations per segment is now locked descriptively, while helper/runtime/shadow-evidence behavior remains unchanged and no override, policy, or runtime influence is encoded.
- WP-7u branch-state: first bounded consumer of the shadow-signal-summary layer reads the overlay-input fixture slice only, compares `canonical` versus `_02` through the committed summary surface, and records that the current slice remains below the locked floor for sufficient signal classification; no helper/runtime/schema/query-layer behavior changed, and no policy or runtime influence is encoded.
- WP-7v branch-state: second bounded consumer of the shadow-signal-summary layer reads the advisory-artifact-lineage slice only, compares the realized lineages through the committed summary surface, and records that the current lineage slice remains below the locked floor for sufficient signal classification; no helper/runtime/schema/query-layer behavior changed, and no policy or runtime influence is encoded.
- WP-7w branch-state: third bounded consumer of the shadow-signal-summary layer reads the advisory-source dimension from existing committed SSS content, completes the current three-consumer set, and changes no helper/runtime/schema/query-layer behavior while encoding no policy or runtime influence.
- WP-7x branch-state: synthesis brief over the completed three-consumer shadow-signal-summary set characterizes SSS v1 usefulness, the current floor-limited evidence state, and forward observation directions without changing helper/runtime/schema/query-layer behavior and without encoding policy or runtime influence.
- WP-7y branch-state: retrospective disclosure and stability-lock record for SSS v1 now captures the committed v1 schema shape, the completed consumer-set coverage, the current floor-limited evidence state, and the explicit WP-7w advisory-source readout constraint; the existing `shadow_signal_summary_option_a_floor_10_v1` derivation method is treated as the equivalent explicit version marker, no dedicated schema/validator patch is applied, and no helper/runtime/query-layer/policy influence is encoded.
- WP-7z branch-state: additive SSS v2 schema and standalone validator are now present for explicit `schema_version: "v2"` payloads and the permitted four-axis, advisory-source-only, fixture-only, and advisory-lineage segment forms; SSS v1 schema/validator/instances remain unchanged, no v2 instance is produced, and no helper/runtime/query-layer/policy influence is encoded.
- WP-8a branch-state: the first committed SSS v2 instance now exists as advisory-source-only single-axis summary `SSS-0002` over the committed shadow-log corpus through `OSH-0010`, the v2 schema/validator are exercised unchanged, SSS v1 schema/validator/instances remain unchanged, and no consumer brief, helper, query-layer, runtime, or policy influence is encoded.
- WP-8b branch-state: the first bounded consumer brief over committed SSS v2 now consumes advisory-source-only summary `SSS-0002`, compares its first-class v2 source-only instance shape structurally to the WP-7w v1 advisory-source readout, records the current floor-limited evidence state, and encodes no SSS instance, schema, validator, query-layer, helper, runtime, or policy influence.
- WP-8c branch-state: central read-only query-layer support for committed SSS v2 content now registers SSS v2 artifacts and exposes additive v2 overview / integrity views through the canonical research query surface; existing query-layer views and read-only guard behavior are preserved, no SSS schema, validator, committed instance, shadow-log corpus, helper, runtime, policy, or protected-path behavior is changed, and no new SSS instance or consumer brief is produced.
- WP-8d-prep branch-state: central SSS v2 query-layer integrity now supports the advisory-lineage segment form encoded by `advisory_source`, `source_bucket_mapping_id`, and `source_pre_gate_advisory_snapshot_id`; no `SSS-0003` was created, and no SSS schema, validator, committed SSS artifact, overlay-shadow corpus, helper, runtime, policy, or protected-path behavior changed.
- WP-8d branch-state: second committed SSS v2 instance `SSS-0003` now summarizes the existing committed shadow-log corpus through the advisory-lineage segment form encoded by `advisory_source`, `source_bucket_mapping_id`, and `source_pre_gate_advisory_snapshot_id`, with deterministic floor-10 segment semantics and a non-diagnostic artifact-production record; central SSS v2 query-layer integrity remains healthy, no SSS schema, validator, query-layer, committed prior instance, shadow-log corpus, helper, runtime, policy, or protected-path behavior is changed, and no consumer brief is produced.
- WP-8e branch-state: second bounded consumer brief over committed SSS v2 now consumes advisory-lineage summary `SSS-0003` through the canonical central v2 query-layer surface, compares it structurally with the WP-7v v1 advisory-lineage readout and the WP-8b advisory-source v2 consumer, records that all four lineage segments remain below floor 10 / `INSUFFICIENT_EVIDENCE`, and encodes no SSS instance, schema, validator, query-layer, helper, runtime, policy, or protected-path behavior change.
- WP-8f-prep branch-state: central SSS v2 query-layer integrity now supports the fixture-only segment form encoded by `fixture_identity`; no `SSS-0004` was created, and no SSS schema, validator, committed SSS artifact, overlay-shadow corpus, fixture/config, helper, runtime, policy, or protected-path behavior changed.
- WP-8f branch-state: third committed SSS v2 instance `SSS-0004` now summarizes the existing committed shadow-log corpus through the fixture-only segment form encoded by `fixture_identity`, with deterministic floor-10 segment semantics and a non-diagnostic artifact-production record; central SSS v2 query-layer integrity remains healthy, no SSS schema, validator, query-layer, committed prior instance, shadow-log corpus, helper, fixture/config, runtime, policy, or protected-path behavior is changed, and no consumer brief is produced.
- WP-8g branch-state: third bounded consumer brief over committed SSS v2 now consumes fixture-only summary `SSS-0004` through the canonical central v2 query-layer surface, compares it structurally with the WP-7u v1 overlay-input fixture readout and the WP-8b/WP-8e v2 consumers, records that both fixture segments remain below floor 10 / `INSUFFICIENT_EVIDENCE` and that all eight consumed v2 single-axis segments remain below floor, and encodes no SSS instance, schema, validator, query-layer, helper, runtime, policy, or protected-path behavior change.
- WP-8h branch-state: synthesis brief over the completed three-consumer SSS v2 set now characterizes advisory-source `SSS-0002`, advisory-lineage `SSS-0003`, and fixture-identity `SSS-0004` consumption as structurally complete but fully floor-limited at the current corpus size, with 8 consumed v2 single-axis segments, 0 above-floor segments, and 8 below-floor / `INSUFFICIENT_EVIDENCE` segments; the synthesis records forward observations without committing scope and changes no SSS instance, schema, validator, query-layer, helper, runtime, policy, or protected-path behavior.
- WP-8i branch-state: retrospective disclosure and stability-lock record for SSS v2 now captures the committed v2 schema shape, explicit `schema_version: "v2"` marker, completed single-axis instance coverage (`SSS-0002`, `SSS-0003`, `SSS-0004`), completed consumer-set coverage through WP-8h, and the current floor-limited evidence state; SSS v2 is locked as the consumed single-axis baseline for current repo state, future schema evolution must occur through explicit later versioned work, and no SSS schema, validator, instance, query-layer, helper, runtime, policy, or protected-path behavior is changed.
- WP-9a branch-state: Phase 9 direction is now repo-anchored as Outcome-Ingesting Research Lifecycle Foundation through a committed decision record, lifecycle state vocabulary, lifecycle transition graph, lifecycle-change artifact documentation, and the first `lifecycle_change` schema with explicit `schema_version: "v1"`; the package commits no LCH instances, validator, query-layer relation, outcome ledger, reconciliation artifact, policy schema, deployment artifact, runtime influence, automated promotion, or protected-path behavior change.
- WP-9b branch-state: LCH validation and central read-only query-layer support are now present for the Phase 9 lifecycle-change family through `tools/registry/validate_lifecycle_changes.py`, the additive `lifecycle_changes` relation, LCH overview/transition views, and expected-empty LCH integrity views; the package commits no LCH instances, changes no LCH schema or existing artifacts, and adds no outcome ledger, reconciliation artifact, promotion policy, deployment artifact, runtime influence, automated promotion, or protected-path behavior change.
- WP-9c branch-state: cross-family schema-versioning discipline is now documented for Phase 9 through a schema-versioning discipline record and schema-family inventory; future Phase 9 schemas must declare explicit top-level `schema_version` from `v1`, legacy families are classified without retroactive mutation, SSS v1 remains governed by its locked derivation-method marker, SSS v2 and LCH remain explicitly versioned, and no schema, validator, committed artifact, query-layer, runtime, policy, deployment, automated-promotion, or protected-path behavior is changed.
- WP-9d-prep branch-state: LCH reference integrity now normalizes unnested lifecycle reference values before known-pattern resolution, allowing `v_integrity_lifecycle_change_refs` to consume real repo-relative evidence refs and known artifact IDs without DuckDB conversion errors; the package adds no LCH instances, lifecycle methodology, schema, validator, registry, existing artifact, runtime, policy, deployment, automated-promotion, or protected-path behavior change.
- WP-9d branch-state: retrospective LCH backfill methodology is now documented and the first real lifecycle-change instances are committed for H-001 (`LCH-0001` through `LCH-0003`), mapping the historical path `proposed -> in_research -> research_concluded -> archived` from committed HYPOTHESIS / REP / DEC evidence; the package exercises the WP-9a/WP-9b LCH schema, validator, query-layer, and integrity views against real historical content while committing no H-002 through H-010 backfill, no LCH schema, validator, query-layer, registry, existing artifact, outcome ledger, reconciliation, promotion policy, deployment, runtime, automated-promotion, or protected-path behavior change.
- WP-9e branch-state: retrospective lifecycle-change coverage is now complete for historical candidates H-001 through H-010, with `LCH-0004` through `LCH-0030` bulk-applying the WP-9d methodology unchanged to H-002 through H-010 and preserving the `proposed -> in_research -> research_concluded -> archived` path; H-005 archival cites its DEC evidence plus `DCH-0001` and `REL-0001`; the package updates only direct lifecycle current-state tests and commits no LCH methodology change, schema, validator, query-layer, registry, existing evidence artifact, outcome ledger, reconciliation, promotion policy, deployment, runtime, automated-promotion, or protected-path behavior change.
- WP-9f branch-state: the first bounded lifecycle consumer brief is now committed for the populated `LCH-0001` through `LCH-0030` corpus, segmented by per-candidate lifecycle path and using the central query layer only; the brief observes that H-001 through H-010 share the retrospective `proposed -> in_research -> research_concluded -> archived` path, treats timing only as artifact commit timestamp gaps rather than operational lifecycle duration, surfaces the H-005 `DEC-0005` / `DCH-0001` / `REL-0001` evidence exception, and commits no LCH instance, schema, validator, query-layer, registry, evidence artifact, outcome ledger, reconciliation, promotion policy, deployment, runtime, automated-promotion, or protected-path behavior change.
- WP-9g branch-state: the second bounded lifecycle consumer brief is now committed for the populated `LCH-0001` through `LCH-0030` corpus, segmented by transition edge and using the central query layer only; the brief observes 10 rows on each retrospective edge, treats timing only as artifact commit timestamp gaps rather than operational lifecycle duration, surfaces the archival-edge H-005 `DEC-0005` / `DCH-0001` / `REL-0001` evidence exception, and commits no LCH instance, schema, validator, query-layer, registry, evidence artifact, prior consumer output, outcome ledger, reconciliation, promotion policy, deployment, runtime, automated-promotion, or protected-path behavior change.
- WP-9h branch-state: the third bounded lifecycle consumer brief is now committed for the populated `LCH-0001` through `LCH-0030` corpus, segmented by evidence artifact type and using the central query layer only; the brief observes 32 lifecycle evidence refs across HYPOTHESIS-path, REP, DEC-path, DCH, and REL families, confirms HYPOTHESIS/REP/DEC coverage across all ten candidates, surfaces H-005 as the only current DCH/REL cross-family archival evidence exception, and commits no LCH instance, schema, validator, query-layer, registry, evidence artifact, prior consumer output, evidence-quality ranking, outcome ledger, reconciliation, promotion policy, deployment, runtime, automated-promotion, or protected-path behavior change.
- WP-9i branch-state: the lifecycle consumer set synthesis is now committed over the WP-9f per-candidate, WP-9g per-transition-edge, and WP-9h per-evidence-artifact-type consumers for the populated `LCH-0001` through `LCH-0030` corpus; the synthesis confirms the three consumer axes are mutually consistent, preserves timing as retrospective artifact commit timestamp gaps rather than operational lifecycle duration, surfaces H-005 as the only current cross-family archival evidence exception, and commits no LCH instance, schema, validator, query-layer, registry, evidence artifact, prior consumer output, evidence-quality ranking, lifecycle policy, outcome ledger, reconciliation, promotion policy, deployment, runtime, automated-promotion, or protected-path behavior change.
- WP-9j branch-state: the lifecycle/LCH stability lock is now committed for the completed Phase 9 lifecycle tranche, locking the consumed LCH v1 retrospective baseline after WP-9f per-candidate, WP-9g per-transition-edge, WP-9h per-evidence-artifact-type, and WP-9i synthesis coverage; the lock records `LCH-0001` through `LCH-0030`, H-001 through H-010, the uniform retrospective `proposed -> in_research -> research_concluded -> archived` path, H-005 as the only current cross-family archival evidence exception, and the current unsupported/future-dependent boundaries for forward-flow, paper/live, fast-track, halted/recovery, outcome-learning, REC/reconciliation, promotion thresholds, evidence scoring, and runtime/deployment authority; it commits no LCH instance, schema, validator, query-layer, registry, evidence artifact, prior consumer output, lifecycle policy, outcome ledger, reconciliation, promotion policy, deployment, runtime, automated-promotion, or protected-path behavior change.
- WP-9k branch-state: the outcome ledger schema v1 foundation is now committed as the first package after the lifecycle/LCH stability lock; it adds `research/schemas/outcome_ledger.schema.json` and companion outcome-ledger artifact documentation, records OL-1 through OL-6 in the Phase 9 decision record, and registers outcome ledger as an explicit-versioned schema family in the repo-local inventory. Outcome ledger v1 supports `outcome_kind: research_oos` only, requires `schema_version: "v1"`, `pipeline_version`, and `derivation_record`, preserves optional advisory linkage for future Decision 8 coupling, and commits no validator, outcome instance, query-layer relation, integrity view, methodology, retrospective backfill, ingestion helper, REC/reconciliation, promotion policy, paper/live semantics, evidence-quality scoring, runtime, deployment, or protected-path behavior change.
- WP-9l branch-state: outcome-ledger validator and central query-layer support are now committed for the WP-9k outcome ledger v1 schema; the package adds `tools/registry/validate_outcome_ledger.py`, the `outcome_ledgers` query-layer relation, outcome-ledger overview/integrity views, and validator/query-layer tests while preserving missing/empty committed outcome-ledger state as healthy. It resolves schema-local artifact validation, candidate/source REP/reference checks, window-bound checks, and read-only query consumption, but commits no outcome-ledger instances, methodology, retrospective backfill, ingestion helper, REC/reconciliation, promotion policy, paper/live semantics, evidence-quality scoring, runtime, deployment, or protected-path behavior change.
- WP-9m branch-state: the first outcome-ledger seed artifact and retrospective backfill methodology are now committed for the WP-9k/WP-9l outcome-ledger foundation; the package adds exactly `research/outcome_ledgers/OL-0001.outcome_ledger.json` and `docs/research_pipeline/2026-04-outcome_ledger_backfill_methodology.md`, updates outcome-ledger docs/status for the corpus changing from empty to one row, and validates the seed through the outcome-ledger validator and query-layer integrity views. It does not perform the full REP retrospective backfill, does not modify schema, validator, query-layer code, source REP/EXP artifacts, candidate registry, lifecycle artifacts, REC/reconciliation, promotion policy, paper/live semantics, evidence-quality scoring, runtime, deployment, or protected-path behavior.

## Update Discipline

- Read this file first.
- Follow the startup read order above before drafting or executing a package.
- Prefer current repo truth over stale chat context.
- If this file conflicts with locked baseline docs, report the mismatch and follow the locked baseline until corrected.
- Update this file after meaningful merges that change current state, boundaries, data status, workbench status, orchestration status, or immediate next architecture needs.
