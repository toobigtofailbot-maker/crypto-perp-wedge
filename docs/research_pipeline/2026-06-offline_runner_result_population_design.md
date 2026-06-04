# Offline Runner / Result-Population Design

## 1. Scope

WP-12hh / WP-S2c-187 is a Tier 1 documentation-only design-opening package for roadmap item 5: offline research runner / result-population architecture.

It creates this design document and updates `docs/project_status.md` only.

It creates no schema, validator, query view, code, tests, artifact instance, result-population instance, runner, backtest, sweep, result computation, canonical sweep run, canonical evidence, runtime behavior, paper/live behavior, protected-path change, approval, recommendation, ranking/scoring, readiness, transition, or human-gate execution authority.

## 2. Main authorization basis

Main reviewed the WP-S2c-186 item 4 checkpoint and authorized the item 5 sequence:

- WP-S2c-187: offline runner / result-population design opening.
- Mandatory Main result-population schema-shape review after WP-S2c-187 merge and before WP-S2c-188.
- WP-S2c-188: result-population schema introduction.
- WP-S2c-189: result-population validator implementation.
- Mandatory Main runner execution-surface review after WP-S2c-189 merge and before WP-S2c-190.
- WP-S2c-190: offline runner implementation.
- WP-S2c-191: result-population query-layer extension.
- WP-S2c-192: item 5 tranche checkpoint.
- Mandatory Main re-engagement after WP-S2c-192 for roadmap item 6 and the first-sweep-run question.

WP-S2c-187 is authorized directly after WP-S2c-186 merge, refreshed-main preflight, and no stop trigger. WP-S2c-188 is not authorized for direct drafting until Main reviews the schema shape surfaced here.

## 3. Repo-truth dependency basis

Repo truth is refreshed `main` after WP-12hg / WP-S2c-186, merged at `4977d923ff1a073bcee06a7a62ed1fed3bb58979`.

Current dependency facts:

- WP-S2c-186 closed roadmap item 4 and authorized WP-S2c-187 as the item 5 design opening.
- Variant manifest and sweep plan schemas exist at `research/schemas/variant_manifest.schema.json` and `research/schemas/sweep_plan.schema.json`.
- The variant/sweep validator exists at `tools/registry/validate_variant_sweep_artifacts.py`.
- Read-only variant/sweep query visibility exists through `tools/research_query/query_layer.py` and `tools/research_query/views.sql`.
- Strategy Spec schema, validator, and read-only query visibility exist as upstream planning surfaces.
- WP-S2c-172 through WP-S2c-176 completed the backtest-realism implementation tranche in the research backtester.
- Current repo truth contains no canonical Strategy Spec instances, variant manifests, sweep plans, result populations, runner authorization, canonical sweep run, or paper/live/runtime authorization.

## 4. Design objective

This document defines the architecture and artifact-grammar posture for the future offline runner and future result-population artifact.

The objective is to describe how a later runner may consume a validated parent Strategy Spec, validated frozen variant manifest, and validated sweep plan, call the realism-corrected research backtester, and write a complete result-population artifact without shrinking the committed population denominator.

This document does not implement that flow.

## 5. Non-authority boundary

Result populations are future non-authoritative research artifacts. They are not EXP / REP / trial-log / OL / REC / DEC replacements.

They do not approve, recommend, rank, transition, create readiness, execute gates, satisfy D2-006, satisfy REC-5, or create paper/live/runtime authority.

The future offline runner is a research tool only. It is not a scheduler, runtime component, broker/exchange/order path, paper/live bridge, OMS component, reconciliation component, risk control, safe-mode component, kill-switch component, approval tool, ranking tool, or human-gate executor.

## 6. Offline-only boundary

Item 5 remains offline research only.

The future runner must not contact runtime, paper/live, OMS, reconciliation, kill-switch, broker, exchange, order, risk, safe-mode, overlay, Tier 4, config, deployment, or protected paths.

The runner may call the research backtester only after WP-S2c-190 is explicitly authorized. This design package does not authorize a runner implementation or any backtest invocation.

## 7. Relationship to item 4 variant/sweep grammar

Item 5 depends on item 4 surfaces:

- variant manifest schema, validator, and query views;
- sweep plan schema, validator, and query views;
- immutable supersession / no-supersession-after-results posture;
- fresh-denominator posture for new manifests;
- committed-population denominator preservation;
- parent Strategy Spec hash posture;
- selected-variant and validation-method declarations;
- result-capture expectations.

The future runner may consume only validated and pre-registered inputs. It must not infer authority from draft, stale, mismatched, or invalid artifacts.

## 8. Relationship to WP-S2c-172 through WP-S2c-176 backtest-realism tranche

WP-S2c-172 through WP-S2c-176 made research-backtester assumptions explicit for fee side, exchange-constraint disclosure, funding notional, slippage/fill/size/liquidity, liquidation/maintenance margin/mark source, and bar-path assumptions.

The future runner depends on that realism-corrected research backtester. It records and preserves assumption metadata exposed by the parent Strategy Spec, sweep plan, and backtester outputs.

This package does not modify `lib/backtest.py` or `lib/evaluation.py`, does not change backtest assumptions, and does not authorize future modification of those files.

## 9. Offline runner purpose

The future offline runner is a deterministic offline research tool that may later:

1. consume a validated parent Strategy Spec;
2. consume a validated frozen/pre-registered variant manifest;
3. consume a validated sweep plan;
4. call the realism-corrected research backtester for every committed variant row when separately authorized;
5. preserve success and non-success outcomes for the complete committed population;
6. write one complete result-population artifact;
7. leave all canonical evidence, review, and decision authority outside the runner.

The future runner does not choose candidates, tune adaptively, approve outputs, compute authority-bearing rankings, or trigger paper/live behavior.

## 10. Offline runner conceptual inputs

Future conceptual inputs include:

- variant manifest reference: ID, hash, frozen/pre-registered status, committed population count, variant assignment rows, and manifest schema version;
- sweep plan reference: ID, identity/hash if defined, selected variants, validation-method declarations, data/timeframe assumptions, backtest-realism assumptions, denominator/trial-accounting posture, and sweep plan schema version;
- parent Strategy Spec reference: ID, hash, schema version, and non-executing planning status;
- backtester interface reference: realism-corrected research backtester and exposed assumption metadata;
- data catalog / data source reference: locked data catalog, read-only data access, data slice identity, missing-data policy, and irreparable-gap posture;
- runner configuration: deterministic seed if randomization is later authorized, environment metadata, code version/commit hash posture, output destination, and explicit no-adaptive-search declaration.

## 11. Offline runner conceptual outputs

Future conceptual outputs include:

- one result-population artifact for one sweep plan over one variant manifest;
- one represented result row or explicit non-success row for every committed variant;
- outcome category counts reconciled to the committed denominator;
- backtester assumption summary;
- data coverage and error summaries;
- identity hash and audit envelope;
- append-only ledger events;
- validation summary after WP-S2c-189 exists;
- read-only query visibility after WP-S2c-191 exists.

This package creates none of these outputs.

## 12. Result-population purpose

A result population is the durable complete outcome ledger for one sweep plan over one variant manifest.

Its purpose is to preserve every variant outcome in the committed pre-registered population, preserve denominator integrity, preserve lineage from Strategy Spec to variant manifest to sweep plan to result population, and provide non-authoritative research visibility for later review.

It is an evidence input / index only if later authorized. It is not a decision surface.

## 13. Result-population conceptual artifact structure

Future schema shape should consider these conceptual groups:

- artifact identity;
- schema version;
- non-authority declaration;
- parent Strategy Spec reference;
- parent variant manifest reference;
- parent sweep plan reference;
- execution environment / code reference;
- input identity hash;
- result-population identity hash;
- audit envelope;
- committed denominator snapshot;
- variant result rows;
- outcome category counts;
- append-only ledger / event log;
- validation summary;
- error summary;
- data coverage summary;
- backtest assumption summary;
- lineage;
- review posture.

These are design groups only, not locked final field names.

## 14. Complete-population preservation

Future result populations must preserve exactly one result row per committed variant, or an explicit non-success row for every variant that did not produce a numeric result.

All variant IDs from the parent manifest must be represented. Missing variant rows, winner-only retention, post-hoc cleanup, denominator shrinkage, silent exclusion after results, and hidden population expansion are forbidden.

All outcome categories remain visible.

## 15. Committed-population denominator preservation

`committed_population_count` is inherited from the parent manifest and sweep plan.

The result-population denominator must equal the committed pre-registered population count. Executed-only and successful-only denominators are forbidden.

Result count plus non-success category counts must reconcile to the committed population count. Item 6 may later add effective-trial diagnostics, but those diagnostics do not replace the raw committed denominator.

## 16. Identity-hash vs audit-envelope split

Per Main direction, item 5 incorporates the Side Research finding as supporting input: identity hash and audit envelope should be separated.

The identity hash scientifically defines the run/result population. Proposed identity-hash scope should include parent Strategy Spec hash, variant manifest hash, sweep plan identity/hash, committed population count, variant result-row identities, outcome categories, backtest assumption identity, data catalog/data slice identity, runner version/code reference, and result metrics that define the scientific output.

The audit envelope preserves administrative and review metadata without unnecessarily changing scientific identity. It may include timestamps, authorship, review notes, operator comments, validation run logs, and administrative lineage.

This split is a proposed schema-shape area for Main review after WP-S2c-187.

## 17. Append-only population/result ledger posture

Future result populations should carry append-only ledger posture for:

- creation event;
- validation events;
- amendment or supersession references if applicable;
- review events;
- correction events.

Scientific identity must not mutate silently after finalization. Corrections require append-only correction or supersession posture, old result populations remain referenceable, and exact mechanics are deferred to WP-S2c-188, WP-S2c-189, and WP-S2c-190.

## 18. Parent artifact reference and hash posture

Future result populations should reference:

- parent Strategy Spec ID, schema version, and hash;
- parent variant manifest ID, schema version, manifest hash, frozen/pre-registered status, and committed population count;
- parent sweep plan ID, schema version, identity/hash if defined, selected-variant posture, validation-method declarations, and denominator posture.

Missing, stale, mismatched, or invalid parent hashes should block clean runner output when implementation exists. This package does not implement blockers.

## 19. Variant outcome category posture

Future result-population outcome categories should include:

- successful;
- failed;
- invalid;
- excluded;
- errored;
- aborted;
- filtered;
- data_unavailable;
- not_attempted.

All categories remain part of the committed denominator unless Main later authorizes a more precise item 6 statistical distinction. The raw committed denominator is not replaced.

## 20. Error/abort/filter/data-unavailable/not-attempted posture

Non-success rows must be first-class rows, not missing data.

Errors should distinguish infrastructure or deterministic backtester failure from strategy underperformance. Aborts should record whether the abort was global or variant-local. Filtered and excluded rows should reference pre-result rules. Data-unavailable rows should preserve the data-source and gap posture. Not-attempted rows should record why the committed variant was not run.

No category may be used to hide a committed variant or shrink the denominator.

## 21. Determinism posture

Future runner behavior must preserve:

- stable input ordering;
- stable variant ordering;
- stable output ordering;
- stable hash inputs;
- deterministic random seeds if random components are ever authorized;
- stable environment/code reference metadata;
- repeat-run reproducibility checks.

WP-S2c-190 will need a determinism check: identical manifest, sweep plan, data, and code reference must produce an identical result population.

## 22. Backtester call boundary

The runner may call the backtester only after WP-S2c-190 is explicitly authorized.

The runner must not modify `lib/backtest.py` or `lib/evaluation.py`, must not change backtest assumptions, and must not bypass the assumptions declared by Strategy Spec, sweep plan, or backtester output.

The runner must not call runtime, paper/live, broker, exchange, order, OMS, reconciliation, risk, safe-mode, kill-switch, overlay, or Tier 4 paths.

## 23. Locked data catalog / data-read posture

Future runner data access must be read-only and limited to repo-authorized research data sources and locked data catalog references.

The future result population should preserve data catalog identity, data slice identity, timeframe, data stream, gap-handling posture, and missing-data outcomes.

This package does not fetch data, modify `data/`, change the data catalog, or authorize silent interpolation.

## 24. No first canonical sweep-run boundary

No first real or canonical sweep run is authorized in WP-S2c-187 through WP-S2c-191.

Item 5 may later build and test runner behavior using temporary fixtures only where package scope authorizes it. The first canonical sweep run remains a separate Main-authorized moment surfaced at WP-S2c-192.

## 25. Future result-population schema surface for WP-S2c-188

Proposed default for Main review: one schema file at `research/schemas/result_population.schema.json`.

Proposed top-level groups:

- `schema_version`;
- `result_population_id`;
- `status`;
- `non_authority_declaration`;
- `parent_strategy_spec`;
- `parent_variant_manifest`;
- `parent_sweep_plan`;
- `execution_context`;
- `input_identity_hash`;
- `result_population_identity_hash`;
- `audit_envelope`;
- `committed_denominator_snapshot`;
- `variant_result_rows`;
- `outcome_category_counts`;
- `append_only_ledger`;
- `validation_summary`;
- `error_summary`;
- `data_coverage_summary`;
- `backtest_assumption_summary`;
- `lineage`;
- `review`.

Recommended required groups for v1 are all groups needed to prove non-authority, parent references, denominator preservation, complete row coverage, outcome reconciliation, identity hash, and ledger posture. Optional groups may be limited to review notes, administrative comments, and future extension placeholders.

Artifact status should remain non-authoritative, with possible values such as `draft`, `generated`, `validation_passed`, `validation_failed`, `closed`, `superseded`, and `rejected`. Status must not mean approval, recommendation, ranking, readiness, transition, or gate satisfaction.

Parent refs/hashes should preserve Strategy Spec ID/hash/schema version, variant manifest ID/hash/schema version/committed population count/frozen status, and sweep plan ID/hash-or-identity/schema version/selected-variant posture.

Committed denominator snapshot should include inherited count, parent counts, selected count if different, outcome counts, and explicit forbidden executed-only/successful-only denominator flags.

Variant result rows should include variant ID, row identity/hash, assignment hash or reference, outcome category, attempted flag, metrics when successful, non-success reason when not successful, error class where applicable, data coverage notes, backtest assumption reference, and lineage to parent rows.

Outcome enum should include successful, failed, invalid, excluded, errored, aborted, filtered, data_unavailable, and not_attempted.

Complete-population reconciliation fields should prove no missing variant IDs, no extra variant IDs outside the parent manifest, row count equality, outcome-count reconciliation, and committed denominator equality.

Identity-hash fields should separate hash algorithm, hash scope version, hash scope, and computed hash. Audit-envelope fields should carry administrative metadata outside scientific identity where Main agrees.

Ledger/event structure should be append-only with event type, event timestamp, actor/tool context, reference IDs, and notes, while avoiding authority-bearing actions.

Environment/code/data reference fields should record commit hash posture, runner version, Python/dependency environment summary if later needed, data catalog references, and data slice identity.

Backtest assumption recording fields should preserve fee-side, exchange-constraint disclosure, funding notional, slippage/fill/size/liquidity, liquidation/maintenance margin/mark source, and bar-path assumptions where available.

Validation summary should capture schema/validator outcome, validator version, validation timestamp, and blocking errors after WP-S2c-189 exists.

Non-authority declarations should mirror item 4 style and explicitly reject runner authority, sweep authority, result authority, ranking, recommendation, approval, readiness, transition, runtime, paper/live, and gate authority.

Validator hard checks should enforce schema validity, ID/filename consistency, parent refs/hashes, identity hash, committed denominator equality, one accounted row per committed variant, no extra variants, outcome reconciliation, ledger fields, non-authority flags, and forbidden executable/authority keys.

Relationship to EXP / REP / trial-log / OL / REC / DEC should be reference-only. Result populations do not replace canonical evidence or decision surfaces.

Zero-instance posture should remain true in WP-S2c-188 unless Main explicitly authorizes a different scope. Proposed forbidden structures include executable code, runner commands, broker/order instructions, recommendations, ranking scores, readiness updates, gate triggers, paper/live actions, and hidden denominator changes.

WP-S2c-188 is gated by Main schema-shape review after WP-S2c-187.

## 26. Future result-population validator surface for WP-S2c-189

A future validator may enforce:

- schema validity;
- filename / ID consistency;
- duplicate result-population ID detection;
- parent Strategy Spec / manifest / sweep plan references and hashes;
- result-population identity hash;
- committed denominator equality;
- one row or accounted outcome per committed variant ID;
- no missing variant IDs;
- no extra variant IDs outside parent manifest;
- outcome category count reconciliation;
- no executed-only or successful-only denominator;
- append-only ledger required fields;
- non-authority flags;
- forbidden executable / authority keys.

The validator must not approve artifacts, recommend variants, rank variants with authority, execute gates, trigger transitions, run backtests, invoke the runner, create result populations, mutate evidence, update readiness, or contact runtime/paper/live/protected paths.

## 27. Future runner implementation surface for WP-S2c-190

WP-S2c-190 will be the first item 5 implementation package that may execute backtests at population scale, if Main authorizes it after WP-S2c-189.

Before WP-S2c-190, Main runner execution-surface review must surface:

- exact module path;
- CLI shape if any;
- inputs;
- outputs;
- result-population write path;
- exact backtester function/interface called;
- data path/catalog read posture;
- offline-only enforcement;
- deterministic ordering and seeding;
- complete-population output enforcement;
- failure capture without denominator shrinkage;
- tests and determinism checks.

WP-S2c-190 must not modify protected runtime/paper/live paths, `lib/backtest.py`, or `lib/evaluation.py` unless Main explicitly re-authorizes a different path. Current posture is consume/call, not modify.

## 28. Future query-layer surface for WP-S2c-191

WP-S2c-191 may later add read-only query visibility for result populations after schema and validator work exists.

Potential views may expose overview, parent lineage, committed denominator, variant rows, outcome-category counts, data coverage, error summary, backtest assumptions, identity/audit split, append-only ledger, and integrity checks.

Query views must remain descriptive and read-only. They must not approve, rank, recommend, execute, mutate artifacts, trigger runner behavior, or contact protected paths.

## 29. Item 6 deferrals

Item 6 remains deferred and includes:

- DSR / PSR / MinTRL computation;
- Monte Carlo / bootstrap;
- parameter sensitivity / stability maps;
- cost/funding/slippage stress computation;
- confirmatory vs exploratory population labels;
- raw committed denominator plus effective-trial diagnostics;
- robustness dashboard / advisory briefing logic if Main places it later.

Item 5 may reserve structures needed for item 6, but it does not compute item 6 statistics.

## 30. User end-state visibility

The user end-state remains visible and downstream:

- always-on, non-authoritative Strategy Research Lab;
- automated self-assessment;
- candidate generation;
- testing, comparison, and briefing;
- multiple paper candidates continuously tested;
- eventual multiple approved live strategies in parallel;
- central allocation/risk coordination before multi-strategy operation;
- human approval for all promotion, risk-change, paper/live, and live-deployment decisions.

These remain visible and unranked. They are downstream of core pipeline dependencies and are not authorized by WP-S2c-187 or item 5. No continuous lab, candidate queue, allocator, paper-live bridge, or live deployment work is pulled forward by this design.

## 31. Forbidden implications

This design explicitly rejects these implications:

- result-population schema creation in WP-S2c-187;
- result-population validator creation in WP-S2c-187;
- runner implementation in WP-S2c-187;
- query view creation in WP-S2c-187;
- artifact instances;
- canonical sweep run;
- backtest invocation;
- result computation;
- EXP / REP / trial-log / OL / REC / DEC replacement;
- runtime/paper/live/protected-path contact;
- modification of `lib/backtest.py` or `lib/evaluation.py`;
- non-deterministic execution;
- incomplete result population;
- denominator shrinkage;
- winner-only retention;
- post-hoc result cleanup;
- unlogged failed trials;
- hidden adaptive search;
- approval, recommendation, ranking, readiness, transition, or gate authority.

## 32. Stop / escalation conditions

Stop and escalate if future work requires:

- schema, validator, query-layer, code, test, or runner changes outside explicit package authority;
- Strategy Spec, variant manifest, sweep plan, or result-population instances without explicit authorization;
- backtest invocation or canonical sweep execution before the separate Main-authorized moment;
- runtime/paper/live/protected-path contact;
- modification of `lib/backtest.py`, `lib/evaluation.py`, or protected paths without explicit authorization;
- incomplete-population preservation, denominator shrinkage, winner-only reporting, executed-only denominator, or successful-only denominator;
- treating Side Research as repo truth or standalone authorization;
- weakening permanent human gates;
- creating approval, recommendation, ranking/scoring, readiness, transition, paper/live, runtime, or human-gate execution authority.

## 33. Validation posture

WP-S2c-187 uses T1-doc-narrow validation. Validation should prove exact changed-file scope, no forbidden-path changes, query-view listing health, clean integrity views, registry/artifact/outcome/reconciliation validators, Strategy Spec validator, variant/sweep validator, scoped query/registry/schema/validator pytest where repo convention expects it, and final clean status.

Full pytest is not required by the active package unless repo truth, validation failure, local convention, or Codex judgment indicates it is needed.

## 34. Next-package posture

After WP-S2c-187 merges, Side must report the result-population schema shape to Main.

WP-S2c-188 remains gated by Main result-population schema-shape review after this package. WP-S2c-190 remains gated by Main runner execution-surface review after WP-S2c-189.

First canonical sweep run remains separately unauthorized and should be surfaced at WP-S2c-192.
