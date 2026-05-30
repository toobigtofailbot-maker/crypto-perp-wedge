# Research Query Layer (WP-6d)

## Purpose

The research query layer makes cross-candidate questions queryable instead of
document-walkable. It is read-only by design and exists to inspect the registry,
experiment plans, experiment reports, and trial log without creating new
research evidence.

## What It Loads

- `research/candidate_registry.jsonl` -> `candidates`
- `research/experiments/EXP-*.plan.json` -> `exp_plans`
- `research/experiments/REP-*.report.json` -> `exp_reports`
- `research/trial_log.jsonl` -> `trial_log`
- `research/shadow_signal_summaries_v2/*.shadow_signal_summary.json` -> `shadow_signal_summaries_v2`
- `research/r2s_approval_records/*.r2s_approval_record.json` -> `r2s_approval_records`
- `research/shadow_evidence_retention/*.shadow_evidence_retention.json` -> `shadow_evidence_retention`
- `research/s2p_approval_records/*.s2p_approval_record.json` -> `s2p_approval_records`

The DuckDB connection is in-memory. No `.duckdb` file is created.
Missing Scope 6 artifact directories and zero committed Scope 6 instances are
healthy empty state.

## Named Views

| View | Purpose | Example question |
|---|---|---|
| `v_candidate_overview` | One row per registry candidate with lifecycle, evidence paths, and trial count. | Which candidates exist and where is their evidence? |
| `v_concluded_candidates` | Concluded subset of the candidate overview. | Which candidates should default multi-candidate analysis use? |
| `v_experiment_instances` | One row per matched plan/report pair. | Which plans have reports and when were they executed? |
| `v_oos_metrics_by_candidate` | Out-of-sample report metrics joined to registry family/timeframe fields. | Which candidates had the least-bad OOS Sharpe or cost drag? |
| `v_is_metrics_by_candidate` | In-sample Sharpe and provenance fields from current reports. | What IS Sharpe convention was recorded for each report? |
| `v_gate_results_flat` | One row per candidate/report/gate result. | Which candidates failed a specific D2-006 gate? |
| `v_candidate_by_family` | Counts by strategy family, timeframe, and verdict bucket. | Have we already tried this family on this timeframe? |
| `v_information_inputs` | One row per candidate information input. | Which candidates used funding or premium data? |
| `v_integrity_plan_report_pairs` | Broken EXP/REP relationships, while allowing bounded pre-execution EXP plans for pending pre-registered candidates. Expected empty. | Are any EXP/REP pairings missing outside legitimate pre-execution state? |
| `v_integrity_candidate_refs` | Broken candidate references from EXP/REP artifacts. Expected empty. | Do all artifacts point to real registry candidates? |
| `v_shadow_signal_summaries_v2_overview` | One row per committed SSS v2 segment with schema version, segmentation axes, corpus window, segment keys, counts, rates, and outcome fields. | What committed SSS v2 segment evidence exists? |
| `v_integrity_shadow_signal_summary_v2_derivation` | SSS v2 derivation drift check against committed overlay shadow logs. Expected empty for supported healthy instances. | Does committed SSS v2 content still match the cited corpus? |
| `v_r2s_approval_records` | One row per future R2S approval record with candidate, decision, REC-5, preservation, and non-authority fields. | What R2S approval-record artifacts exist for inspection? |
| `v_shadow_evidence_retention` | One row per future shadow-evidence retention record with shadow-window, D2-007, parity, disclosure, mismatch, and non-authority fields. | What retained shadow-evidence records exist for review? |
| `v_s2p_approval_records` | One row per future S2P approval record with shadow-evidence reference, decision, preservation, and non-authority fields. | What S2P approval-record artifacts exist for inspection? |
| `v_scope6_candidate_packaging_overview` | Candidate-level Scope 6 artifact inventory counts and booleans only. | Which candidates have Scope 6 packaging artifacts present? |
| `v_s2p_shadow_evidence_links` | S2P-to-shadow-evidence reference inspection with candidate-ID consistency. | Do S2P records resolve to the retained shadow-evidence record they cite? |
| `v_integrity_r2s_approval_candidate_refs` | Broken R2S approval-record candidate references. Expected empty. | Do all R2S records point to real registry candidates? |
| `v_integrity_shadow_evidence_candidate_refs` | Broken shadow-evidence retention candidate references. Expected empty. | Do all retained shadow-evidence records point to real registry candidates? |
| `v_integrity_s2p_approval_candidate_refs` | Broken S2P approval-record candidate references. Expected empty. | Do all S2P records point to real registry candidates? |
| `v_integrity_r2s_rec5_candidate_consistency` | R2S top-level candidate versus nested REC-5 candidate mismatch check. Expected empty. | Does nested REC-5 evidence stay on the same candidate? |
| `v_integrity_s2p_shadow_evidence_refs` | Missing S2P shadow-evidence references. Expected empty. | Does every S2P record resolve to its referenced shadow evidence? |
| `v_integrity_s2p_shadow_evidence_candidate_consistency` | S2P candidate versus referenced shadow-evidence candidate mismatch check. Expected empty. | Do linked S2P and shadow-evidence records agree on candidate ID? |
| `v_integrity_scope6_authority_flags` | Scope 6 forbidden-authority and required non-authority flag drift. Expected empty. | Did any Scope 6 record acquire authority-bearing flags? |
| `v_integrity_scope6_preservation_flags` | Scope 6 preservation and D2-007 boundary flag drift. Expected empty. | Did any Scope 6 record lose required preservation confirmations? |

## Scope 6 Query-Layer Support

WP-S2c-117 adds read-only in-memory query support for future Scope 6
R2S approval-record, shadow-evidence retention, and S2P approval-record
artifact families. The query layer registers these optional families as
in-memory DuckDB views only. It does not create files or directories, and
missing directories or zero matching instances are healthy empty state.

The Scope 6 views expose inventory, artifact references, preservation flags,
non-authority flags, and consistency diagnostics only. They create no artifacts
and grant no readiness, approval, transition, promotion, ranking, scoring,
recommendation, policy, runtime, or human-gate execution authority.

## SSS v2 Query-Layer Support

WP-8c adds read-only central query-layer support for committed SSS v2 content.
The relation loads committed artifacts only from
`research/shadow_signal_summaries_v2/` and exposes them through the canonical
research query surface.

This support replaces the WP-8b bounded consumer workaround that registered
local temporary DuckDB relations inside the brief bundle. WP-8c does not create,
mutate, or validate new SSS instances; it only makes existing committed SSS v2
content queryable centrally.

The SSS v2 integrity view is expected to return no rows in healthy state for
supported v2 instance shapes. It supports advisory-source-only v2 summaries,
advisory-lineage v2 summaries encoded by `advisory_source`,
`source_bucket_mapping_id`, and `source_pre_gate_advisory_snapshot_id`, and
fixture-only v2 summaries encoded by `fixture_identity`. Unsupported future v2
segmentation shapes are surfaced as integrity rows until a later package
explicitly extends coverage.

## Invocation

List views:

```powershell
.venv\Scripts\python.exe -m tools.research_query.run --list-views
```

Run a view:

```powershell
.venv\Scripts\python.exe -m tools.research_query.run --view v_candidate_overview
```

Run ad-hoc SQL:

```powershell
.venv\Scripts\python.exe -m tools.research_query.run --sql "SELECT candidate_id, status FROM v_candidate_overview"
```

Emit JSON:

```powershell
.venv\Scripts\python.exe -m tools.research_query.run --view v_oos_metrics_by_candidate --json
```

## Read-Only Contract

The query layer must not write to research artifacts. It opens an in-memory
DuckDB connection, registers views over existing repo files, and only exposes
ad-hoc execution through a conservative read-only guard.

The guard rejects write-capable and state-changing SQL such as `INSERT`,
`UPDATE`, `DELETE`, `CREATE`, `DROP`, `ALTER`, `ATTACH`, `COPY`, `PRAGMA`, and
`CALL`. It also rejects ad-hoc file-reading functions and URL-like inputs so
the CLI cannot be turned into an external data loader.

## Single-Statement Restriction

Ad-hoc SQL must be exactly one statement. A single trailing semicolon is allowed,
but multi-statement input is rejected even when the first statement is a harmless
`SELECT`.

This prevents inputs such as:

```sql
SELECT 1 AS x; DROP VIEW candidates
```

The guard favors false negatives over permissive execution.

## What This Layer Does NOT Do

- No writes to any research artifact
- No external data sources
- No network access
- No agents or LLM calls
- No dashboards or UI
- No persisted database file
- No backtest execution
- No promotion, risk, OMS, or execution-core behavior
- No runtime, policy, override, OMS, risk, or execution behavior from SSS v2 query-layer support
- No readiness, approval, transition, promotion, ranking, scoring, recommendation, policy, runtime, or human-gate execution authority from Scope 6 query-layer support

## Example Queries

Concluded candidate overview:

```sql
SELECT candidate_id, strategy_family, timeframe, overall_verdict
FROM v_concluded_candidates
ORDER BY candidate_id;
```

Out-of-sample metrics by family:

```sql
SELECT candidate_id, strategy_family, timeframe, oos_sharpe, oos_cost_drag
FROM v_oos_metrics_by_candidate
ORDER BY oos_sharpe DESC;
```

Gate failures:

```sql
SELECT candidate_id, report_id, gate_id, observed
FROM v_gate_results_flat
WHERE pass = false
ORDER BY candidate_id, gate_id;
```

Information inputs:

```sql
SELECT information_input, COUNT(*) AS n_candidates
FROM v_information_inputs
GROUP BY information_input
ORDER BY n_candidates DESC, information_input;
```

Integrity checks:

```sql
SELECT * FROM v_integrity_plan_report_pairs;
```

`v_integrity_plan_report_pairs` treats an EXP without REP as healthy only while it is attached to a known `DRAFT` / `PENDING` / `pre_registered` candidate with empty `trial_ids` and null `decision_record_path`. The exception ends once trial evidence or decision state exists, and REP artifacts that reference unknown plan IDs remain integrity issues. This preserves pre-registration discipline by allowing a committed EXP before backtest/REP creation without fake placeholder reports.

```sql
SELECT * FROM v_integrity_candidate_refs;
```
