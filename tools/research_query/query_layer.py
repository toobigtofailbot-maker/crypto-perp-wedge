"""Read-only query layer. This module MUST NOT write to any research artifact."""

from __future__ import annotations

import re
import hashlib
import json
from pathlib import Path
from typing import Any

import duckdb


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "research" / "candidate_registry.jsonl"
EXPERIMENTS_DIR = REPO_ROOT / "research" / "experiments"
DECISION_CHANGES_DIR = REPO_ROOT / "research" / "decision_changes"
RELEASE_NOTES_DIR = REPO_ROOT / "research" / "release_notes"
LIFECYCLE_CHANGES_DIR = REPO_ROOT / "research" / "lifecycle_changes"
OUTCOME_LEDGERS_DIR = REPO_ROOT / "research" / "outcome_ledgers"
RECONCILIATIONS_DIR = REPO_ROOT / "research" / "reconciliations"
AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "agent_outputs"
MACRO_WINDOW_AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "macro_window_agent_outputs"
BUCKET_MAPPINGS_DIR = REPO_ROOT / "research" / "bucket_mappings"
PRE_GATE_ADVISORY_SNAPSHOTS_DIR = REPO_ROOT / "research" / "pre_gate_advisory_snapshots"
OVERLAY_SHADOW_LOGS_DIR = REPO_ROOT / "research" / "overlay_shadow_logs"
SHADOW_SIGNAL_SUMMARIES_DIR = REPO_ROOT / "research" / "shadow_signal_summaries"
SHADOW_SIGNAL_SUMMARIES_V2_DIR = REPO_ROOT / "research" / "shadow_signal_summaries_v2"
R2S_APPROVAL_RECORDS_DIR = REPO_ROOT / "research" / "r2s_approval_records"
SHADOW_EVIDENCE_RETENTION_DIR = REPO_ROOT / "research" / "shadow_evidence_retention"
S2P_APPROVAL_RECORDS_DIR = REPO_ROOT / "research" / "s2p_approval_records"
STRATEGY_SPECS_DIR = REPO_ROOT / "research" / "strategy_specs"
TRIAL_LOG_PATH = REPO_ROOT / "research" / "trial_log.jsonl"
VIEWS_PATH = Path(__file__).resolve().with_name("views.sql")

WRITE_OR_STATE_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "CREATE",
    "DROP",
    "ALTER",
    "ATTACH",
    "DETACH",
    "COPY",
    "EXPORT",
    "IMPORT",
    "REPLACE",
    "MERGE",
    "TRUNCATE",
    "VACUUM",
    "PRAGMA",
    "CALL",
}
EXTERNAL_SOURCE_PATTERNS = (
    r"\bread_json\w*\b",
    r"\bread_csv\w*\b",
    r"\bread_parquet\b",
    r"\bparquet_scan\b",
    r"\bsqlite_scan\b",
    r"\bpostgres_scan\b",
    r"\bmysql_scan\b",
    r"\bglob\b",
)


class ReadOnlyQueryError(ValueError):
    """Raised when SQL cannot be proven to be a single read-only query."""


def _sql_path(path: Path) -> str:
    return path.as_posix().replace("'", "''")


def _sql_literal(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    return "'" + str(value).replace("'", "''") + "'"


def _require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found; preflight mismatch: {path}")


def _register_decision_changes(conn: duckdb.DuckDBPyConnection) -> None:
    decision_files = (
        sorted(DECISION_CHANGES_DIR.glob("*.decision_change.json"))
        if DECISION_CHANGES_DIR.exists()
        else []
    )
    if decision_files:
        conn.execute(
            f"""
            CREATE VIEW decision_changes AS
            SELECT * FROM read_json_auto('{_sql_path(DECISION_CHANGES_DIR / "*.decision_change.json")}')
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW decision_changes AS
        SELECT
            CAST(NULL AS VARCHAR) AS decision_change_id,
            CAST(NULL AS VARCHAR) AS candidate_id,
            CAST([] AS VARCHAR[]) AS report_ids,
            CAST(NULL AS VARCHAR) AS decision,
            CAST(NULL AS STRUCT(from_stage VARCHAR, to_stage VARCHAR)) AS stage_transition,
            CAST(NULL AS VARCHAR) AS decided_by,
            CAST(NULL AS VARCHAR) AS decided_at,
            CAST(NULL AS VARCHAR) AS rationale,
            CAST(NULL AS VARCHAR) AS evidence_summary,
            CAST(NULL AS VARCHAR) AS risk_acknowledgment,
            CAST(NULL AS VARCHAR) AS supersedes_decision_id,
            CAST(NULL AS VARCHAR) AS notes,
            CAST([] AS VARCHAR[]) AS conditions
        WHERE FALSE
        """
    )


def _register_release_notes(conn: duckdb.DuckDBPyConnection) -> None:
    release_files = (
        sorted(RELEASE_NOTES_DIR.glob("*.release_notes.json"))
        if RELEASE_NOTES_DIR.exists()
        else []
    )
    if release_files:
        conn.execute(
            f"""
            CREATE VIEW release_notes AS
            SELECT * FROM read_json_auto('{_sql_path(RELEASE_NOTES_DIR / "*.release_notes.json")}')
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW release_notes AS
        SELECT
            CAST(NULL AS VARCHAR) AS release_notes_id,
            CAST(NULL AS VARCHAR) AS decision_change_id,
            CAST(NULL AS VARCHAR) AS candidate_id,
            CAST(NULL AS VARCHAR) AS released_at,
            CAST(NULL AS VARCHAR) AS released_by,
            CAST(NULL AS VARCHAR) AS effective_stage,
            CAST(NULL AS STRUCT(
                metrics_tracked VARCHAR[],
                review_cadence VARCHAR,
                rollback_triggers VARCHAR[],
                alert_recipients VARCHAR[]
            )) AS monitoring_plan,
            CAST(NULL AS VARCHAR) AS rollback_plan,
            CAST(NULL AS VARCHAR) AS notes,
            CAST([] AS VARCHAR[]) AS linked_artifacts
        WHERE FALSE
        """
    )


def _register_lifecycle_changes(conn: duckdb.DuckDBPyConnection) -> None:
    lifecycle_change_files = (
        sorted(LIFECYCLE_CHANGES_DIR.glob("*.lifecycle_change.json"))
        if LIFECYCLE_CHANGES_DIR.exists()
        else []
    )
    if lifecycle_change_files:
        conn.execute(
            f"""
            CREATE VIEW lifecycle_changes AS
            SELECT * FROM read_json_auto('{_sql_path(LIFECYCLE_CHANGES_DIR / "*.lifecycle_change.json")}')
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW lifecycle_changes AS
        SELECT
            CAST(NULL AS VARCHAR) AS lifecycle_change_id,
            CAST(NULL AS VARCHAR) AS schema_version,
            CAST(NULL AS VARCHAR) AS candidate_id,
            CAST(NULL AS VARCHAR) AS from_state,
            CAST(NULL AS VARCHAR) AS to_state,
            CAST(NULL AS VARCHAR) AS transition_edge,
            CAST(NULL AS VARCHAR) AS decided_by,
            CAST(NULL AS VARCHAR) AS decided_at,
            CAST(NULL AS VARCHAR) AS evidence_summary,
            CAST(NULL AS VARCHAR) AS risk_acknowledgment,
            CAST([] AS VARCHAR[]) AS evidence_artifact_refs,
            CAST(NULL AS VARCHAR) AS supersedes_lch_id,
            CAST(NULL AS VARCHAR) AS notes,
            CAST([] AS VARCHAR[]) AS linked_advisory_artifacts,
            CAST(NULL AS BOOLEAN) AS retrospective_flag,
            CAST(NULL AS VARCHAR) AS retrospective_disclosure,
            CAST(NULL AS BOOLEAN) AS fast_track_flag,
            CAST([] AS VARCHAR[]) AS strong_candidate_criteria_refs
        WHERE FALSE
        """
    )


def _register_outcome_ledgers(conn: duckdb.DuckDBPyConnection) -> None:
    outcome_ledger_files = (
        sorted(OUTCOME_LEDGERS_DIR.glob("*.outcome_ledger.json"))
        if OUTCOME_LEDGERS_DIR.exists()
        else []
    )
    if outcome_ledger_files:
        conn.execute(
            f"""
            CREATE VIEW outcome_ledgers AS
            SELECT * FROM read_json_auto('{_sql_path(OUTCOME_LEDGERS_DIR / "*.outcome_ledger.json")}')
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW outcome_ledgers AS
        SELECT
            CAST(NULL AS VARCHAR) AS schema_version,
            CAST(NULL AS VARCHAR) AS outcome_id,
            CAST(NULL AS VARCHAR) AS candidate_id,
            CAST(NULL AS VARCHAR) AS lifecycle_state_during_window,
            CAST(NULL AS VARCHAR) AS evaluation_window_start,
            CAST(NULL AS VARCHAR) AS evaluation_window_end,
            CAST(NULL AS VARCHAR) AS outcome_kind,
            CAST(NULL AS STRUCT(
                source_field VARCHAR,
                window_convention VARCHAR,
                sharpe DOUBLE,
                max_drawdown DOUBLE,
                n_obs BIGINT,
                trades BIGINT,
                hit_rate DOUBLE,
                profit_factor DOUBLE,
                final_equity DOUBLE,
                total_pnl DOUBLE,
                gross_pnl DOUBLE,
                fees_paid DOUBLE,
                slippage_paid DOUBLE,
                funding_paid DOUBLE,
                cost_drag_fraction DOUBLE,
                dsr DOUBLE,
                walk_forward_efficiency DOUBLE,
                gates_passed BIGINT,
                gates_total BIGINT,
                funding_events_applied BIGINT,
                config_sha256 VARCHAR,
                dataset_sha256 VARCHAR,
                dsr_note VARCHAR,
                max_drawdown_peak VARCHAR,
                max_drawdown_trough VARCHAR,
                skipped_bars BIGINT,
                sensitivity_min_ratio DOUBLE,
                short_side_trades BIGINT,
                short_side_net_pnl DOUBLE,
                long_side_trades BIGINT,
                long_side_net_pnl DOUBLE,
                trial_count_before_append BIGINT,
                trial_count_after_append BIGINT
            )) AS metrics,
            CAST(NULL AS STRUCT(
                source_data_refs VARCHAR[],
                source_data_window_start VARCHAR,
                source_data_window_end VARCHAR,
                source_data_notes VARCHAR
            )) AS data_provenance,
            CAST(NULL AS STRUCT(
                derivation_method VARCHAR,
                source_artifact_id VARCHAR,
                source_artifact_path VARCHAR,
                derivation_timestamp VARCHAR,
                derivation_tool_version VARCHAR
            )) AS derivation_record,
            CAST(NULL AS VARCHAR) AS pipeline_version,
            CAST([] AS VARCHAR[]) AS linked_artifacts,
            CAST(NULL AS BOOLEAN) AS retrospective_flag,
            CAST([] AS VARCHAR[]) AS linked_advisory_artifacts,
            CAST(NULL AS VARCHAR) AS notes,
            CAST(NULL AS VARCHAR) AS retrospective_disclosure
        WHERE FALSE
        """
    )


def _register_reconciliations(conn: duckdb.DuckDBPyConnection) -> None:
    reconciliation_files = (
        sorted(RECONCILIATIONS_DIR.glob("*.reconciliation.json"))
        if RECONCILIATIONS_DIR.exists()
        else []
    )
    if reconciliation_files:
        conn.execute(
            f"""
            CREATE VIEW reconciliations AS
            SELECT * FROM read_json_auto('{_sql_path(RECONCILIATIONS_DIR / "*.reconciliation.json")}')
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW reconciliations AS
        SELECT
            CAST(NULL AS VARCHAR) AS schema_version,
            CAST(NULL AS VARCHAR) AS reconciliation_id,
            CAST(NULL AS VARCHAR) AS candidate_id,
            CAST(NULL AS VARCHAR) AS outcome_id,
            CAST(NULL AS VARCHAR) AS outcome_kind,
            CAST(NULL AS VARCHAR) AS pipeline_version,
            CAST(NULL AS VARCHAR) AS expectation_source_type,
            CAST(NULL AS VARCHAR) AS expectation_source_artifact_id,
            CAST(NULL AS VARCHAR) AS expectation_source_artifact_path,
            CAST(NULL AS STRUCT(
                source_type VARCHAR,
                source_artifact_id VARCHAR,
                source_artifact_path VARCHAR,
                extraction_method VARCHAR,
                extracted_at VARCHAR,
                metric_expectations STRUCT(
                    metric_name VARCHAR,
                    expected_operator VARCHAR,
                    expected_value JSON,
                    expected_unit VARCHAR,
                    source_field_path VARCHAR,
                    source_text VARCHAR,
                    notes VARCHAR
                )[]
            )) AS expectation_extracted,
            CAST(NULL AS STRUCT(
                source_field VARCHAR,
                window_convention VARCHAR,
                sharpe DOUBLE,
                max_drawdown DOUBLE,
                n_obs BIGINT,
                trades BIGINT,
                hit_rate DOUBLE,
                profit_factor DOUBLE,
                final_equity DOUBLE,
                total_pnl DOUBLE,
                gross_pnl DOUBLE,
                fees_paid DOUBLE,
                slippage_paid DOUBLE,
                funding_paid DOUBLE,
                cost_drag_fraction DOUBLE,
                dsr DOUBLE,
                walk_forward_efficiency DOUBLE,
                gates_passed BIGINT,
                gates_total BIGINT,
                funding_events_applied BIGINT,
                config_sha256 VARCHAR,
                dataset_sha256 VARCHAR,
                dsr_note VARCHAR,
                max_drawdown_peak VARCHAR,
                max_drawdown_trough VARCHAR,
                skipped_bars BIGINT,
                sensitivity_min_ratio DOUBLE,
                short_side_trades BIGINT,
                short_side_net_pnl DOUBLE,
                long_side_trades BIGINT,
                long_side_net_pnl DOUBLE,
                trial_count_before_append BIGINT,
                trial_count_after_append BIGINT
            )) AS realized_metrics,
            CAST(NULL AS STRUCT(
                metric_comparisons STRUCT(
                    metric_name VARCHAR,
                    expected_value JSON,
                    realized_value JSON,
                    delta_absolute DOUBLE,
                    delta_relative DOUBLE,
                    comparison_verdict VARCHAR,
                    comparison_notes VARCHAR
                )[]
            )) AS comparison,
            CAST(NULL AS VARCHAR) AS overall_verdict,
            CAST(NULL AS VARCHAR) AS interpretation,
            CAST(NULL AS STRUCT(
                derivation_method VARCHAR,
                source_artifact_id VARCHAR,
                source_artifact_path VARCHAR,
                derivation_timestamp VARCHAR,
                source_outcome_id VARCHAR,
                expectation_source_type VARCHAR,
                tool_version VARCHAR
            )) AS derivation_record,
            CAST(NULL AS BOOLEAN) AS retrospective_flag,
            CAST([] AS VARCHAR[]) AS linked_advisory_artifacts,
            CAST([] AS VARCHAR[]) AS linked_lifecycle_artifacts,
            CAST(NULL AS VARCHAR) AS notes,
            CAST(NULL AS VARCHAR) AS retrospective_disclosure
        WHERE FALSE
        """
    )


def _register_agent_outputs(conn: duckdb.DuckDBPyConnection) -> None:
    agent_output_files = (
        sorted(AGENT_OUTPUTS_DIR.glob("*.agent_output.json"))
        if AGENT_OUTPUTS_DIR.exists()
        else []
    )
    if agent_output_files:
        conn.execute(
            f"""
            CREATE VIEW agent_outputs AS
            SELECT * FROM read_json_auto('{_sql_path(AGENT_OUTPUTS_DIR / "*.agent_output.json")}')
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW agent_outputs AS
        SELECT
            CAST(NULL AS VARCHAR) AS agent_output_id,
            CAST(NULL AS VARCHAR) AS agent_type,
            CAST(NULL AS VARCHAR) AS generated_at,
            CAST([] AS STRUCT(path VARCHAR, sha256 VARCHAR, role VARCHAR)[]) AS input_data_refs,
            CAST(NULL AS VARCHAR) AS as_of_timestamp,
            CAST(NULL AS DOUBLE) AS setup_score,
            CAST(NULL AS DOUBLE) AS confidence,
            CAST(NULL AS STRUCT(
                method_id VARCHAR,
                realized_volatility DOUBLE,
                vol_component DOUBLE,
                funding_component DOUBLE,
                spread_component DOUBLE,
                stress_score DOUBLE
            )) AS scoring_method,
            CAST(NULL AS VARCHAR) AS rationale_summary,
            CAST(NULL AS BOOLEAN) AS deterministic,
            CAST(NULL AS VARCHAR) AS notes
        WHERE FALSE
        """
    )


def _resolve_repo_ref(ref_path: Any) -> Path | None:
    if not isinstance(ref_path, str) or not ref_path:
        return None
    candidate = Path(ref_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (REPO_ROOT / candidate).resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return None
    return resolved


def _macro_window_fixture_check_rows() -> list[dict[str, Any]]:
    if not MACRO_WINDOW_AGENT_OUTPUTS_DIR.exists():
        return []

    rows: list[dict[str, Any]] = []
    for output_path in sorted(MACRO_WINDOW_AGENT_OUTPUTS_DIR.glob("*.macro_window_agent_output.json")):
        try:
            payload = json.loads(output_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        source_fixture_path = payload.get("source_fixture_path")
        fixture_path = _resolve_repo_ref(source_fixture_path)
        fixture_exists = bool(fixture_path and fixture_path.exists())
        actual_sha256: str | None = None
        expected_flag: bool | None = None

        if fixture_path and fixture_path.exists():
            actual_sha256 = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
            try:
                fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                fixture = {}
            if "macro_event_window_active" in fixture:
                expected_flag = bool(fixture["macro_event_window_active"])

        rows.append(
            {
                "macro_window_agent_output_id": payload.get("macro_window_agent_output_id"),
                "source_fixture_path": source_fixture_path,
                "source_fixture_exists": fixture_exists,
                "actual_source_fixture_sha256": actual_sha256,
                "expected_macro_window_flag": expected_flag,
            }
        )

    return rows


def _register_macro_window_fixture_checks(conn: duckdb.DuckDBPyConnection) -> None:
    rows = _macro_window_fixture_check_rows()
    if rows:
        values = ",\n            ".join(
            "("
            + ", ".join(
                [
                    _sql_literal(row["macro_window_agent_output_id"]),
                    _sql_literal(row["source_fixture_path"]),
                    _sql_literal(row["source_fixture_exists"]),
                    _sql_literal(row["actual_source_fixture_sha256"]),
                    _sql_literal(row["expected_macro_window_flag"]),
                ]
            )
            + ")"
            for row in rows
        )
        conn.execute(
            f"""
            CREATE VIEW macro_window_agent_output_fixture_checks AS
            SELECT *
            FROM (VALUES
                {values}
            ) AS t(
                macro_window_agent_output_id,
                source_fixture_path,
                source_fixture_exists,
                actual_source_fixture_sha256,
                expected_macro_window_flag
            )
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW macro_window_agent_output_fixture_checks AS
        SELECT
            CAST(NULL AS VARCHAR) AS macro_window_agent_output_id,
            CAST(NULL AS VARCHAR) AS source_fixture_path,
            CAST(NULL AS BOOLEAN) AS source_fixture_exists,
            CAST(NULL AS VARCHAR) AS actual_source_fixture_sha256,
            CAST(NULL AS BOOLEAN) AS expected_macro_window_flag
        WHERE FALSE
        """
    )


def _register_macro_window_agent_outputs(conn: duckdb.DuckDBPyConnection) -> None:
    macro_window_agent_output_files = (
        sorted(MACRO_WINDOW_AGENT_OUTPUTS_DIR.glob("*.macro_window_agent_output.json"))
        if MACRO_WINDOW_AGENT_OUTPUTS_DIR.exists()
        else []
    )
    if macro_window_agent_output_files:
        conn.execute(
            f"""
            CREATE VIEW macro_window_agent_outputs AS
            SELECT * FROM read_json_auto('{_sql_path(MACRO_WINDOW_AGENT_OUTPUTS_DIR / "*.macro_window_agent_output.json")}')
            """
        )
        _register_macro_window_fixture_checks(conn)
        return

    conn.execute(
        """
        CREATE VIEW macro_window_agent_outputs AS
        SELECT
            CAST(NULL AS VARCHAR) AS macro_window_agent_output_id,
            CAST(NULL AS VARCHAR) AS generated_at,
            CAST(NULL AS VARCHAR) AS as_of_timestamp,
            CAST(NULL AS VARCHAR) AS source_fixture_path,
            CAST(NULL AS VARCHAR) AS source_fixture_sha256,
            CAST(NULL AS BOOLEAN) AS macro_window_flag,
            CAST(NULL AS VARCHAR) AS event_class,
            CAST(NULL AS VARCHAR) AS event_name,
            CAST(NULL AS BOOLEAN) AS deterministic,
            CAST(NULL AS BOOLEAN) AS advisory_only,
            CAST(NULL AS VARCHAR) AS notes
        WHERE FALSE
        """
    )
    _register_macro_window_fixture_checks(conn)


def _register_bucket_mappings(conn: duckdb.DuckDBPyConnection) -> None:
    bucket_mapping_files = (
        sorted(BUCKET_MAPPINGS_DIR.glob("*.bucket_mapping.json"))
        if BUCKET_MAPPINGS_DIR.exists()
        else []
    )
    if bucket_mapping_files:
        conn.execute(
            f"""
            CREATE VIEW bucket_mappings AS
            SELECT * FROM read_json_auto('{_sql_path(BUCKET_MAPPINGS_DIR / "*.bucket_mapping.json")}')
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW bucket_mappings AS
        SELECT
            CAST(NULL AS VARCHAR) AS bucket_mapping_id,
            CAST(NULL AS VARCHAR) AS source_agent_output_id,
            CAST(NULL AS VARCHAR) AS agent_type,
            CAST(NULL AS VARCHAR) AS generated_at,
            CAST(NULL AS VARCHAR) AS as_of_timestamp,
            CAST(NULL AS DOUBLE) AS source_setup_score,
            CAST(NULL AS DOUBLE) AS source_confidence,
            CAST(NULL AS VARCHAR) AS mapping_method,
            CAST(NULL AS DOUBLE) AS confidence_floor,
            CAST(NULL AS BOOLEAN) AS confidence_floor_triggered,
            CAST(NULL AS VARCHAR) AS mapped_bucket,
            CAST(NULL AS DOUBLE) AS size_multiplier,
            CAST(NULL AS BOOLEAN) AS deterministic,
            CAST(NULL AS BOOLEAN) AS advisory_only,
            CAST(NULL AS VARCHAR) AS notes
        WHERE FALSE
        """
    )


def _register_pre_gate_advisory_snapshots(conn: duckdb.DuckDBPyConnection) -> None:
    snapshot_files = (
        sorted(PRE_GATE_ADVISORY_SNAPSHOTS_DIR.glob("*.pre_gate_advisory_snapshot.json"))
        if PRE_GATE_ADVISORY_SNAPSHOTS_DIR.exists()
        else []
    )
    if snapshot_files:
        conn.execute(
            f"""
            CREATE VIEW pre_gate_advisory_snapshots AS
            SELECT * FROM read_json_auto('{_sql_path(PRE_GATE_ADVISORY_SNAPSHOTS_DIR / "*.pre_gate_advisory_snapshot.json")}')
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW pre_gate_advisory_snapshots AS
        SELECT
            CAST(NULL AS VARCHAR) AS pre_gate_advisory_snapshot_id,
            CAST(NULL AS VARCHAR) AS generated_at,
            CAST(NULL AS VARCHAR) AS as_of_timestamp,
            CAST(NULL AS VARCHAR) AS source_agent_output_id,
            CAST(NULL AS VARCHAR) AS source_bucket_mapping_id,
            CAST(NULL AS VARCHAR) AS source_macro_window_agent_output_id,
            CAST(NULL AS DOUBLE) AS setup_score,
            CAST(NULL AS DOUBLE) AS confidence,
            CAST(NULL AS VARCHAR) AS mapped_bucket,
            CAST(NULL AS DOUBLE) AS size_multiplier,
            CAST(NULL AS BOOLEAN) AS macro_window_flag,
            CAST(NULL AS BOOLEAN) AS deterministic,
            CAST(NULL AS BOOLEAN) AS advisory_only,
            CAST(NULL AS VARCHAR) AS combination_rule_applied,
            CAST(NULL AS VARCHAR) AS combined_bucket,
            CAST(NULL AS VARCHAR) AS notes
        WHERE FALSE
        """
    )


def _register_overlay_shadow_logs(conn: duckdb.DuckDBPyConnection) -> None:
    shadow_log_files = (
        sorted(OVERLAY_SHADOW_LOGS_DIR.glob("*.overlay_shadow_log.json"))
        if OVERLAY_SHADOW_LOGS_DIR.exists()
        else []
    )
    if shadow_log_files:
        conn.execute(
            f"""
            CREATE VIEW overlay_shadow_logs AS
            SELECT * FROM read_json_auto('{_sql_path(OVERLAY_SHADOW_LOGS_DIR / "*.overlay_shadow_log.json")}')
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW overlay_shadow_logs AS
        SELECT
            CAST(NULL AS VARCHAR) AS overlay_shadow_log_id,
            CAST(NULL AS VARCHAR) AS advisory_source,
            CAST(NULL AS VARCHAR) AS source_bucket_mapping_id,
            CAST(NULL AS VARCHAR) AS source_pre_gate_advisory_snapshot_id,
            CAST(NULL AS VARCHAR) AS source_agent_output_id,
            CAST(NULL AS VARCHAR) AS observed_overlay_bucket,
            CAST(NULL AS DOUBLE) AS observed_overlay_size_multiplier,
            CAST(NULL AS VARCHAR) AS mapped_bucket,
            CAST(NULL AS DOUBLE) AS size_multiplier,
            CAST(NULL AS VARCHAR) AS comparison_result,
            CAST(NULL AS BOOLEAN) AS override_applied,
            CAST(NULL AS BOOLEAN) AS fail_open_preserved,
            CAST(NULL AS BOOLEAN) AS advisory_only,
            CAST(NULL AS VARCHAR) AS observed_at,
            CAST(NULL AS STRUCT(
                source_type VARCHAR,
                snapshot_path VARCHAR,
                config_path VARCHAR,
                evaluation_time_utc VARCHAR,
                decision_id VARCHAR,
                context_missing BOOLEAN,
                reason_code VARCHAR
            )) AS observation_source,
            CAST(NULL AS VARCHAR) AS notes
        WHERE FALSE
        """
    )


def _register_shadow_signal_summaries(conn: duckdb.DuckDBPyConnection) -> None:
    summary_files = (
        sorted(SHADOW_SIGNAL_SUMMARIES_DIR.glob("*.shadow_signal_summary.json"))
        if SHADOW_SIGNAL_SUMMARIES_DIR.exists()
        else []
    )
    if summary_files:
        conn.execute(
            f"""
            CREATE VIEW shadow_signal_summaries AS
            SELECT * FROM read_json_auto('{_sql_path(SHADOW_SIGNAL_SUMMARIES_DIR / "*.shadow_signal_summary.json")}')
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW shadow_signal_summaries AS
        SELECT
            CAST(NULL AS VARCHAR) AS shadow_signal_summary_id,
            CAST(NULL AS VARCHAR) AS generated_at,
            CAST(NULL AS STRUCT(
                first_overlay_shadow_log_id VARCHAR,
                last_overlay_shadow_log_id VARCHAR,
                first_observed_at VARCHAR,
                last_observed_at VARCHAR,
                total_source_observation_count BIGINT
            )) AS corpus_window,
            CAST(NULL AS VARCHAR) AS derivation_method,
            CAST([] AS VARCHAR[]) AS segmentation_axes,
            CAST(NULL AS STRUCT(
                source_relation VARCHAR,
                source_artifact_family VARCHAR,
                fixture_identity_rule VARCHAR,
                rate_denominator_rule VARCHAR
            )) AS derivation_inputs,
            CAST([] AS STRUCT(
                advisory_source VARCHAR,
                source_bucket_mapping_id VARCHAR,
                source_pre_gate_advisory_snapshot_id VARCHAR,
                fixture_identity VARCHAR,
                match_count BIGINT,
                mismatch_count BIGINT,
                abstention_count BIGINT,
                observation_count BIGINT,
                rate_denominator BIGINT,
                agreement_rate DOUBLE,
                disagreement_rate DOUBLE,
                insufficient_evidence BOOLEAN,
                signal_outcome VARCHAR,
                first_observed_at VARCHAR,
                last_observed_at VARCHAR
            )[]) AS segments,
            CAST(NULL AS BOOLEAN) AS deterministic,
            CAST(NULL AS BOOLEAN) AS advisory_only,
            CAST(NULL AS VARCHAR) AS notes
        WHERE FALSE
        """
    )


def _register_shadow_signal_summaries_v2(conn: duckdb.DuckDBPyConnection) -> None:
    summary_files = (
        sorted(SHADOW_SIGNAL_SUMMARIES_V2_DIR.glob("*.shadow_signal_summary.json"))
        if SHADOW_SIGNAL_SUMMARIES_V2_DIR.exists()
        else []
    )
    if summary_files:
        conn.execute(
            f"""
            CREATE VIEW shadow_signal_summaries_v2 AS
            SELECT * FROM read_json_auto('{_sql_path(SHADOW_SIGNAL_SUMMARIES_V2_DIR / "*.shadow_signal_summary.json")}')
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW shadow_signal_summaries_v2 AS
        SELECT
            CAST(NULL AS VARCHAR) AS shadow_signal_summary_id,
            CAST(NULL AS VARCHAR) AS schema_version,
            CAST(NULL AS VARCHAR) AS generated_at,
            CAST(NULL AS STRUCT(
                first_overlay_shadow_log_id VARCHAR,
                last_overlay_shadow_log_id VARCHAR,
                first_observed_at VARCHAR,
                last_observed_at VARCHAR,
                total_source_observation_count BIGINT
            )) AS corpus_window,
            CAST(NULL AS VARCHAR) AS derivation_method,
            CAST([] AS VARCHAR[]) AS segmentation_axes,
            CAST(NULL AS STRUCT(
                source_relation VARCHAR,
                source_artifact_family VARCHAR,
                fixture_identity_rule VARCHAR,
                rate_denominator_rule VARCHAR
            )) AS derivation_inputs,
            CAST([] AS STRUCT(
                advisory_source VARCHAR,
                source_bucket_mapping_id VARCHAR,
                source_pre_gate_advisory_snapshot_id VARCHAR,
                fixture_identity VARCHAR,
                match_count BIGINT,
                mismatch_count BIGINT,
                abstention_count BIGINT,
                observation_count BIGINT,
                rate_denominator BIGINT,
                agreement_rate DOUBLE,
                disagreement_rate DOUBLE,
                insufficient_evidence BOOLEAN,
                signal_outcome VARCHAR,
                first_observed_at VARCHAR,
                last_observed_at VARCHAR
            )[]) AS segments,
            CAST(NULL AS BOOLEAN) AS deterministic,
            CAST(NULL AS BOOLEAN) AS advisory_only,
            CAST(NULL AS VARCHAR) AS notes
        WHERE FALSE
        """
    )


def _register_r2s_approval_records(conn: duckdb.DuckDBPyConnection) -> None:
    record_files = (
        sorted(R2S_APPROVAL_RECORDS_DIR.glob("*.r2s_approval_record.json"))
        if R2S_APPROVAL_RECORDS_DIR.exists()
        else []
    )
    if record_files:
        conn.execute(
            f"""
            CREATE VIEW r2s_approval_records AS
            SELECT * FROM read_json_auto('{_sql_path(R2S_APPROVAL_RECORDS_DIR / "*.r2s_approval_record.json")}')
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW r2s_approval_records AS
        SELECT
            CAST(NULL AS VARCHAR) AS schema_version,
            CAST(NULL AS VARCHAR) AS record_type,
            CAST(NULL AS VARCHAR) AS approval_record_id,
            CAST(NULL AS VARCHAR) AS candidate_id,
            CAST(NULL AS VARCHAR) AS strategy_or_candidate_family,
            CAST([] AS STRUCT(artifact_id_or_label VARCHAR, artifact_path VARCHAR, notes VARCHAR)[])
                AS evidence_snapshot_references,
            CAST(NULL AS STRUCT(artifact_id_or_label VARCHAR, artifact_path VARCHAR, notes VARCHAR))
                AS d2_006_gate_pass_evidence_reference_or_attestation,
            CAST(NULL AS STRUCT(
                candidate_id VARCHAR,
                outcome_kind VARCHAR,
                pipeline_version VARCHAR,
                expectation_source_type VARCHAR,
                evidence_references STRUCT(artifact_id_or_label VARCHAR, artifact_path VARCHAR, notes VARCHAR)[],
                no_pooled_or_cross_segment_inference_below_floor BOOLEAN
            )) AS rec5_exact_segment_evidence,
            CAST(NULL AS BOOLEAN) AS no_cross_segment_inference_below_rec5_floor,
            CAST(NULL AS VARCHAR) AS approver_identity,
            CAST(NULL AS VARCHAR) AS approval_timestamp_utc,
            CAST(NULL AS VARCHAR) AS decision_outcome,
            CAST(NULL AS STRUCT(
                permanent_human_gates_preserved BOOLEAN,
                d2_006_preserved BOOLEAN,
                d2_007_preserved BOOLEAN,
                rec5_preserved BOOLEAN,
                phase9_preserved BOOLEAN
            )) AS preservation_confirmation,
            CAST(NULL AS VARCHAR) AS transition_machinery_statement,
            CAST(NULL AS STRUCT(
                candidate_readiness_authority BOOLEAN,
                transition_authority BOOLEAN,
                promotion_authority BOOLEAN,
                gate_execution_authority BOOLEAN,
                runtime_authority BOOLEAN,
                tier4_authority BOOLEAN
            )) AS authority_flags
        WHERE FALSE
        """
    )


def _register_shadow_evidence_retention(conn: duckdb.DuckDBPyConnection) -> None:
    retention_files = (
        sorted(SHADOW_EVIDENCE_RETENTION_DIR.glob("*.shadow_evidence_retention.json"))
        if SHADOW_EVIDENCE_RETENTION_DIR.exists()
        else []
    )
    if retention_files:
        conn.execute(
            f"""
            CREATE VIEW shadow_evidence_retention AS
            SELECT * FROM read_json_auto('{_sql_path(SHADOW_EVIDENCE_RETENTION_DIR / "*.shadow_evidence_retention.json")}')
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW shadow_evidence_retention AS
        SELECT
            CAST(NULL AS VARCHAR) AS schema_version,
            CAST(NULL AS VARCHAR) AS record_type,
            CAST(NULL AS VARCHAR) AS shadow_evidence_id,
            CAST(NULL AS VARCHAR) AS candidate_id,
            CAST(NULL AS STRUCT(
                start_utc VARCHAR,
                end_utc VARCHAR,
                calendar_days_observed BIGINT
            )) AS shadow_window,
            CAST(NULL AS STRUCT(
                minimum_shadow_window_calendar_days BIGINT,
                pnl_deviation_max DOUBLE,
                trade_count_deviation_max DOUBLE
            )) AS d2_007_thresholds,
            CAST(NULL AS STRUCT(
                observed_pnl_deviation DOUBLE,
                observed_trade_count_deviation DOUBLE,
                parity_result_evidence_reference_or_attestation STRUCT(
                    artifact_id_or_label VARCHAR,
                    artifact_path VARCHAR,
                    notes VARCHAR
                )
            )) AS parity_result,
            CAST([] AS STRUCT(artifact_id_or_label VARCHAR, artifact_path VARCHAR, notes VARCHAR)[])
                AS shadow_observation_lineage,
            CAST(NULL AS STRUCT(
                interruptions STRUCT(
                    description VARCHAR,
                    evidence_reference_or_attestation STRUCT(artifact_id_or_label VARCHAR, artifact_path VARCHAR, notes VARCHAR)
                )[],
                invalid_observations STRUCT(
                    description VARCHAR,
                    evidence_reference_or_attestation STRUCT(artifact_id_or_label VARCHAR, artifact_path VARCHAR, notes VARCHAR)
                )[],
                missing_data STRUCT(
                    description VARCHAR,
                    evidence_reference_or_attestation STRUCT(artifact_id_or_label VARCHAR, artifact_path VARCHAR, notes VARCHAR)
                )[],
                observation_resets STRUCT(
                    description VARCHAR,
                    evidence_reference_or_attestation STRUCT(artifact_id_or_label VARCHAR, artifact_path VARCHAR, notes VARCHAR)
                )[]
            )) AS disclosure,
            CAST(NULL AS STRUCT(artifact_id_or_label VARCHAR, artifact_path VARCHAR, notes VARCHAR))
                AS evidence_retention_reference,
            CAST(NULL AS STRUCT(
                decision_support_only BOOLEAN,
                ranking_authority BOOLEAN,
                scoring_authority BOOLEAN,
                recommendation_authority BOOLEAN,
                transition_logic_authority BOOLEAN,
                diagnostic_references STRUCT(artifact_id_or_label VARCHAR, artifact_path VARCHAR, notes VARCHAR)[],
                notes VARCHAR
            )) AS mismatch_diagnostics,
            CAST(NULL AS STRUCT(
                candidate_readiness_authority BOOLEAN,
                transition_authority BOOLEAN,
                ranking_authority BOOLEAN,
                scoring_authority BOOLEAN,
                recommendation_authority BOOLEAN,
                gate_execution_authority BOOLEAN,
                runtime_authority BOOLEAN,
                tier4_authority BOOLEAN
            )) AS authority_flags
        WHERE FALSE
        """
    )


def _register_s2p_approval_records(conn: duckdb.DuckDBPyConnection) -> None:
    record_files = (
        sorted(S2P_APPROVAL_RECORDS_DIR.glob("*.s2p_approval_record.json"))
        if S2P_APPROVAL_RECORDS_DIR.exists()
        else []
    )
    if record_files:
        conn.execute(
            f"""
            CREATE VIEW s2p_approval_records AS
            SELECT * FROM read_json_auto('{_sql_path(S2P_APPROVAL_RECORDS_DIR / "*.s2p_approval_record.json")}')
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW s2p_approval_records AS
        SELECT
            CAST(NULL AS VARCHAR) AS schema_version,
            CAST(NULL AS VARCHAR) AS record_type,
            CAST(NULL AS VARCHAR) AS approval_record_id,
            CAST(NULL AS VARCHAR) AS candidate_id,
            CAST(NULL AS STRUCT(shadow_evidence_id VARCHAR, artifact_path VARCHAR, notes VARCHAR))
                AS shadow_window_evidence_reference,
            CAST(NULL AS STRUCT(artifact_id_or_label VARCHAR, artifact_path VARCHAR, notes VARCHAR))
                AS d2_007_parity_result_reference_or_attestation,
            CAST(NULL AS STRUCT(artifact_id_or_label VARCHAR, artifact_path VARCHAR, notes VARCHAR))
                AS interruption_or_invalid_observation_disclosure_reference,
            CAST(NULL AS BOOLEAN) AS paper_runtime_protection_confirmation,
            CAST(NULL AS VARCHAR) AS approver_identity,
            CAST(NULL AS VARCHAR) AS approval_timestamp_utc,
            CAST(NULL AS VARCHAR) AS decision_outcome,
            CAST(NULL AS STRUCT(
                permanent_human_gates_preserved BOOLEAN,
                d2_007_preserved BOOLEAN,
                phase1_paper_runtime_protection_preserved BOOLEAN,
                tier4_boundaries_preserved BOOLEAN
            )) AS preservation_confirmation,
            CAST(NULL AS VARCHAR) AS transition_machinery_statement,
            CAST(NULL AS STRUCT(
                candidate_readiness_authority BOOLEAN,
                transition_authority BOOLEAN,
                promotion_authority BOOLEAN,
                gate_execution_authority BOOLEAN,
                paper_runtime_authority BOOLEAN,
                runtime_authority BOOLEAN,
                tier4_authority BOOLEAN
            )) AS authority_flags
        WHERE FALSE
        """
    )


def _register_strategy_specs(conn: duckdb.DuckDBPyConnection) -> None:
    strategy_spec_files = (
        sorted(STRATEGY_SPECS_DIR.glob("*.strategy_spec.json"))
        if STRATEGY_SPECS_DIR.exists()
        else []
    )
    if strategy_spec_files:
        conn.execute(
            f"""
            CREATE VIEW strategy_specs AS
            SELECT * FROM read_json_auto('{_sql_path(STRATEGY_SPECS_DIR / "*.strategy_spec.json")}')
            """
        )
        return

    conn.execute(
        """
        CREATE VIEW strategy_specs AS
        SELECT
            CAST(NULL AS VARCHAR) AS schema_version,
            CAST(NULL AS VARCHAR) AS strategy_spec_id,
            CAST(NULL AS VARCHAR) AS title,
            CAST(NULL AS VARCHAR) AS short_name,
            CAST(NULL AS VARCHAR) AS status,
            CAST(NULL AS STRUCT(
                human_review_surface_only BOOLEAN,
                not_executable BOOLEAN,
                not_runtime_authority BOOLEAN,
                not_paper_live_authority BOOLEAN,
                not_gate_authority BOOLEAN,
                not_candidate_approval BOOLEAN,
                not_exp_approval BOOLEAN,
                not_sweep_authority BOOLEAN,
                not_ranking_authority BOOLEAN,
                not_recommendation_authority BOOLEAN,
                not_readiness_authority BOOLEAN,
                not_transition_authority BOOLEAN
            )) AS non_execution_declaration,
            CAST(NULL AS STRUCT(
                source_type VARCHAR,
                source_refs VARCHAR[],
                prepared_by VARCHAR,
                created_at VARCHAR,
                updated_at VARCHAR,
                rationale VARCHAR,
                source_constraints VARCHAR[],
                unresolved_claims VARCHAR[]
            )) AS provenance,
            CAST(NULL AS STRUCT(
                symbols VARCHAR[],
                instrument_family VARCHAR,
                venue_assumption VARCHAR,
                market_type VARCHAR,
                directions_allowed VARCHAR[],
                leverage_assumption DOUBLE,
                exchange_constraint_refs VARCHAR[],
                blockers VARCHAR[]
            )) AS instruments,
            CAST(NULL AS STRUCT(
                primary_timeframe VARCHAR,
                confirmation_timeframes VARCHAR[],
                host_data_refs STRUCT(stream VARCHAR, timeframe VARCHAR, field VARCHAR, availability VARCHAR)[],
                gap_handling_assumption VARCHAR,
                missing_data_blockers VARCHAR[]
            )) AS timeframe_and_data,
            CAST(NULL AS STRUCT(
                direction VARCHAR,
                groups STRUCT(
                    group_id VARCHAR,
                    group_role VARCHAR,
                    logic VARCHAR,
                    conditions STRUCT(condition_id VARCHAR)[],
                    subgroups STRUCT(group_id VARCHAR)[],
                    notes VARCHAR
                )[],
                notes VARCHAR
            )) AS entry_logic,
            CAST(NULL AS STRUCT(
                groups STRUCT(
                    group_id VARCHAR,
                    group_role VARCHAR,
                    logic VARCHAR,
                    conditions STRUCT(condition_id VARCHAR)[],
                    subgroups STRUCT(group_id VARCHAR)[],
                    notes VARCHAR
                )[],
                max_holding_period STRUCT(enabled BOOLEAN, bars BIGINT),
                notes VARCHAR
            )) AS exit_logic,
            CAST(NULL AS STRUCT(
                sizing_intent VARCHAR,
                exposure_limits VARCHAR[],
                stop_distance JSON,
                target_distance JSON,
                leverage_visibility VARCHAR,
                liquidation_sensitivity_notes VARCHAR
            )) AS risk_model,
            CAST(NULL AS STRUCT(
                groups STRUCT(
                    group_id VARCHAR,
                    group_role VARCHAR,
                    logic VARCHAR,
                    conditions STRUCT(condition_id VARCHAR)[],
                    subgroups STRUCT(group_id VARCHAR)[],
                    notes VARCHAR
                )[],
                none_declared BOOLEAN
            )) AS filters,
            CAST(NULL AS STRUCT(
                max_free_parameters BIGINT,
                counting_rule VARCHAR,
                parameters STRUCT(
                    name VARCHAR,
                    label VARCHAR,
                    description VARCHAR,
                    "type" VARCHAR,
                    units VARCHAR,
                    "default" JSON,
                    "range" STRUCT(
                        min DOUBLE,
                        max DOUBLE,
                        step DOUBLE,
                        inclusive_min BOOLEAN,
                        inclusive_max BOOLEAN
                    ),
                    allowed_values JSON[],
                    is_free_parameter BOOLEAN,
                    included_in_variant_generation BOOLEAN,
                    role VARCHAR,
                    rationale VARCHAR,
                    constraints VARCHAR[]
                )[],
                no_free_parameters_declared BOOLEAN
            )) AS free_parameters,
            CAST(NULL AS STRUCT(
                invalid_parameter_combinations STRUCT(
                    constraint_id VARCHAR,
                    description VARCHAR,
                    affected_parameters VARCHAR[]
                )[],
                unavailable_data_blockers VARCHAR[],
                deferred_pattern_blockers VARCHAR[],
                none_declared BOOLEAN
            )) AS constraints,
            CAST(NULL AS STRUCT(
                human_review_required BOOLEAN,
                reviewer VARCHAR,
                reviewed_at VARCHAR,
                review_notes VARCHAR[],
                approval_scope VARCHAR,
                non_authority_acknowledgement STRUCT(
                    not_candidate_approval BOOLEAN,
                    not_exp_approval BOOLEAN,
                    not_sweep_authority BOOLEAN,
                    not_ranking_authority BOOLEAN,
                    not_recommendation_authority BOOLEAN,
                    not_readiness_authority BOOLEAN,
                    not_transition_authority BOOLEAN,
                    not_runtime_authority BOOLEAN,
                    not_paper_live_authority BOOLEAN,
                    not_gate_satisfaction BOOLEAN
                )
            )) AS review,
            CAST(NULL AS STRUCT(
                parent_refs STRUCT(ref_type VARCHAR, ref_id VARCHAR, ref_path VARCHAR, ref_hash VARCHAR)[],
                supersedes STRUCT(strategy_spec_id VARCHAR, spec_hash VARCHAR)[],
                amendment_of STRUCT(strategy_spec_id VARCHAR, spec_hash VARCHAR, reason VARCHAR)
            )) AS lineage,
            CAST(NULL AS STRUCT(
                canonical_spec_hash VARCHAR,
                hash_algorithm VARCHAR,
                hash_scope_version VARCHAR,
                hash_scope VARCHAR[],
                hash_status VARCHAR
            )) AS hash_pinning,
            CAST(NULL AS STRUCT(
                intended_for_variant_manifest BOOLEAN,
                variant_manifest_ref VARCHAR,
                frozen_snapshot_ref VARCHAR
            )) AS pre_registration_support,
            CAST(NULL AS STRUCT(
                fee_side_assumption VARCHAR,
                exchange_constraints_disclosed BOOLEAN,
                funding_notional_mode VARCHAR,
                slippage_model VARCHAR,
                fill_mode VARCHAR,
                order_size_assumption VARCHAR,
                liquidity_capacity_assumption VARCHAR,
                liquidation_mode VARCHAR,
                maintenance_margin_assumption VARCHAR,
                mark_price_source VARCHAR,
                bar_path_assumption VARCHAR
            )) AS backtest_realism_assumptions,
            CAST(NULL AS BIGINT) AS max_condition_group_depth
        WHERE FALSE
        """
    )


def _rows_as_dicts(cursor: duckdb.DuckDBPyConnection) -> list[dict[str, Any]]:
    columns = [description[0] for description in cursor.description or []]
    return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _mask_literals_and_comments(sql: str) -> str:
    """Replace comments and quoted literals with spaces, preserving semicolon positions."""

    chars = list(sql)
    index = 0
    while index < len(chars):
        char = chars[index]
        next_char = chars[index + 1] if index + 1 < len(chars) else ""

        if char == "-" and next_char == "-":
            chars[index] = chars[index + 1] = " "
            index += 2
            while index < len(chars) and chars[index] not in "\r\n":
                chars[index] = " "
                index += 1
            continue

        if char == "/" and next_char == "*":
            chars[index] = chars[index + 1] = " "
            index += 2
            while index < len(chars):
                if chars[index] == "*" and index + 1 < len(chars) and chars[index + 1] == "/":
                    chars[index] = chars[index + 1] = " "
                    index += 2
                    break
                chars[index] = " "
                index += 1
            continue

        if char in ("'", '"'):
            quote = char
            chars[index] = " "
            index += 1
            while index < len(chars):
                if chars[index] == quote:
                    chars[index] = " "
                    if index + 1 < len(chars) and chars[index + 1] == quote:
                        chars[index + 1] = " "
                        index += 2
                        continue
                    index += 1
                    break
                chars[index] = " "
                index += 1
            continue

        index += 1

    return "".join(chars)


def _strip_one_trailing_semicolon(masked_sql: str) -> str:
    stripped = masked_sql.strip()
    if stripped.endswith(";"):
        stripped = stripped[:-1].strip()
    return stripped


def _validate_read_only_sql(sql: str) -> str:
    if not sql or not sql.strip():
        raise ReadOnlyQueryError("SQL must contain exactly one read-only SELECT statement")

    if "://" in sql:
        raise ReadOnlyQueryError("External URLs are not allowed in research queries")

    masked = _mask_literals_and_comments(sql)
    effective = _strip_one_trailing_semicolon(masked)

    if not effective:
        raise ReadOnlyQueryError("SQL must contain exactly one read-only SELECT statement")
    if ";" in effective:
        raise ReadOnlyQueryError("Only a single SQL statement is allowed")

    first_keyword = re.match(r"\A\s*([A-Za-z_][A-Za-z0-9_]*)\b", effective)
    if first_keyword is None:
        raise ReadOnlyQueryError("SQL must begin with SELECT or WITH")
    if first_keyword.group(1).upper() not in {"SELECT", "WITH"}:
        raise ReadOnlyQueryError("Only SELECT or WITH...SELECT statements are allowed")

    upper_effective = effective.upper()
    if first_keyword.group(1).upper() == "WITH" and not re.search(r"\bSELECT\b", upper_effective):
        raise ReadOnlyQueryError("WITH queries must resolve to a SELECT statement")

    for keyword in sorted(WRITE_OR_STATE_KEYWORDS):
        if re.search(rf"\b{keyword}\b", upper_effective):
            raise ReadOnlyQueryError(f"Read-only violation: {keyword} is not allowed")

    lower_effective = effective.lower()
    for pattern in EXTERNAL_SOURCE_PATTERNS:
        if re.search(pattern, lower_effective):
            raise ReadOnlyQueryError("External file-reading functions are not allowed in ad-hoc SQL")

    return sql.strip()


def init_duckdb(read_only: bool = True) -> duckdb.DuckDBPyConnection:
    """Create an in-memory DuckDB connection over repo research artifacts."""

    if not read_only:
        raise ValueError("write-enabled research query connections are not supported")

    _require_file(REGISTRY_PATH, "candidate registry")
    _require_file(TRIAL_LOG_PATH, "trial log")
    if not EXPERIMENTS_DIR.exists():
        raise FileNotFoundError(f"experiments directory not found; preflight mismatch: {EXPERIMENTS_DIR}")

    plan_files = sorted(EXPERIMENTS_DIR.glob("EXP-*.plan.json"))
    report_files = sorted(EXPERIMENTS_DIR.glob("REP-*.report.json"))
    if not plan_files:
        raise FileNotFoundError(f"no experiment plan files found; preflight mismatch: {EXPERIMENTS_DIR}")
    if not report_files:
        raise FileNotFoundError(f"no experiment report files found; preflight mismatch: {EXPERIMENTS_DIR}")

    conn = duckdb.connect(database=":memory:")
    conn.execute(
        f"""
        CREATE VIEW candidates AS
        SELECT * FROM read_json_auto('{_sql_path(REGISTRY_PATH)}', format='newline_delimited')
        """
    )
    conn.execute(
        f"""
        CREATE VIEW exp_plans AS
        SELECT * FROM read_json_auto('{_sql_path(EXPERIMENTS_DIR / "EXP-*.plan.json")}')
        """
    )
    conn.execute(
        f"""
        CREATE VIEW exp_reports AS
        SELECT * FROM read_json_auto('{_sql_path(EXPERIMENTS_DIR / "REP-*.report.json")}')
        """
    )
    conn.execute(
        f"""
        CREATE VIEW trial_log AS
        SELECT * FROM read_json_auto('{_sql_path(TRIAL_LOG_PATH)}', format='newline_delimited')
        """
    )
    _register_decision_changes(conn)
    _register_release_notes(conn)
    _register_lifecycle_changes(conn)
    _register_outcome_ledgers(conn)
    _register_reconciliations(conn)
    _register_agent_outputs(conn)
    _register_macro_window_agent_outputs(conn)
    _register_bucket_mappings(conn)
    _register_pre_gate_advisory_snapshots(conn)
    _register_overlay_shadow_logs(conn)
    _register_shadow_signal_summaries(conn)
    _register_shadow_signal_summaries_v2(conn)
    _register_r2s_approval_records(conn)
    _register_shadow_evidence_retention(conn)
    _register_s2p_approval_records(conn)
    _register_strategy_specs(conn)
    load_views(conn)
    return conn


def load_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Load trusted stable view definitions into the in-memory connection."""

    _require_file(VIEWS_PATH, "views SQL")
    conn.execute(VIEWS_PATH.read_text(encoding="utf-8"))


def list_views(conn: duckdb.DuckDBPyConnection) -> list[str]:
    """Return stable user-facing view names."""

    rows = conn.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'main'
          AND table_type = 'VIEW'
          AND table_name LIKE 'v\\_%' ESCAPE '\\'
        ORDER BY table_name
        """
    ).fetchall()
    return [row[0] for row in rows]


def run_named_view(conn: duckdb.DuckDBPyConnection, view_name: str) -> list[dict[str, Any]]:
    """Run SELECT * against a registered named view."""

    if view_name not in list_views(conn):
        raise ValueError(f"unknown view: {view_name}")
    return _rows_as_dicts(conn.execute(f"SELECT * FROM {_quote_identifier(view_name)}"))


def run_sql(conn: duckdb.DuckDBPyConnection, sql: str) -> list[dict[str, Any]]:
    """Execute a single read-only SELECT/WITH statement and return rows as dictionaries."""

    statement = _validate_read_only_sql(sql)
    return _rows_as_dicts(conn.execute(statement))
