"""Read-only query layer. This module MUST NOT write to any research artifact."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import duckdb


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "research" / "candidate_registry.jsonl"
EXPERIMENTS_DIR = REPO_ROOT / "research" / "experiments"
DECISION_CHANGES_DIR = REPO_ROOT / "research" / "decision_changes"
RELEASE_NOTES_DIR = REPO_ROOT / "research" / "release_notes"
AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "agent_outputs"
BUCKET_MAPPINGS_DIR = REPO_ROOT / "research" / "bucket_mappings"
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
    _register_agent_outputs(conn)
    _register_bucket_mappings(conn)
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
