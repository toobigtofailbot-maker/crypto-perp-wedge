"""Small predeclared DuckDB reader over approved evidence families only."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import duckdb

from .models import NON_AUTHORITY, EvidenceUnavailableError, RepoIdentity, ResourceDeniedError

QUERY_NAMES = frozenset(
    {
        "candidate-overview",
        "experiment-report-overview",
        "result-population-overview",
        "result-population-denominator",
    }
)


def _sql_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


class ScopedDuckDBReader:
    """Materialize only allowlisted evidence, then disable external access."""

    def __init__(self, repo_root: Path, identity: RepoIdentity) -> None:
        self.repo_root = repo_root.resolve()
        self.identity = identity

    def _safe_inputs(self, relative_root: str, pattern: str) -> list[Path]:
        root = (self.repo_root / relative_root).resolve()
        try:
            root.relative_to(self.repo_root)
        except ValueError as exc:
            raise ResourceDeniedError("query input root escaped repo root") from exc
        if not root.is_dir() or root.is_symlink():
            raise EvidenceUnavailableError(f"query input directory unavailable: {relative_root}")
        result = []
        for path in sorted(root.glob(pattern)):
            if path.is_file() and not path.is_symlink() and path.resolve().parent == root:
                result.append(path.resolve())
        if not result:
            raise EvidenceUnavailableError(
                f"query input family is empty: {relative_root}/{pattern}"
            )
        return result

    def _single_input(self, relative_path: str) -> Path:
        path = (self.repo_root / relative_path).resolve()
        try:
            path.relative_to(self.repo_root)
        except ValueError as exc:
            raise ResourceDeniedError("query input escaped repo root") from exc
        if not path.is_file() or path.is_symlink():
            raise EvidenceUnavailableError(f"query input unavailable: {relative_path}")
        return path

    def _connection(self) -> tuple[duckdb.DuckDBPyConnection, list[Path]]:
        registry = self._single_input("research/candidate_registry.jsonl")
        reports = self._safe_inputs("research/experiments", "REP-*.report.json")
        populations = self._safe_inputs(
            "research/result_populations", "RP-*.result_population.json"
        )
        inputs = [registry, *reports, *populations]
        report_files = ",".join(_sql_string(path.as_posix()) for path in reports)
        population_files = ",".join(_sql_string(path.as_posix()) for path in populations)

        conn = duckdb.connect(database=":memory:")
        conn.execute(
            "CREATE TABLE approved_candidates AS SELECT * FROM read_json_auto(?, "
            "format='newline_delimited')",
            [registry.as_posix()],
        )
        conn.execute(
            "CREATE TABLE approved_reports AS SELECT * FROM read_json_auto(["
            + report_files
            + "], timestampformat='iso')"
        )
        conn.execute(
            "CREATE TABLE approved_result_populations AS SELECT * FROM read_json_auto(["
            + population_files
            + "], timestampformat='iso')"
        )
        conn.execute("SET enable_external_access = false")
        conn.execute(
            """
            CREATE VIEW v_candidate_overview AS
            SELECT candidate_id, name, status, overall_verdict, strategy_family,
                   timeframe, pipeline_stage, hypothesis_md_path, decision_record_path
            FROM approved_candidates
            ORDER BY candidate_id
            """
        )
        conn.execute(
            """
            CREATE VIEW v_experiment_report_overview AS
            SELECT report_id, plan_id, candidate_id, execution_date, overall_verdict,
                   len(trial_ids) AS trial_count
            FROM approved_reports
            ORDER BY report_id
            """
        )
        conn.execute(
            """
            CREATE VIEW v_result_population_overview AS
            SELECT result_population_id, status,
                   lineage.strategy_spec_id AS strategy_spec_id,
                   lineage.variant_manifest_id AS variant_manifest_id,
                   lineage.sweep_plan_id AS sweep_plan_id,
                   committed_denominator_snapshot.committed_denominator AS committed_denominator,
                   outcome_category_counts.successful AS successful_count,
                   execution_context.repo_commit AS source_repo_commit,
                   execution_context.offline_only AS offline_only,
                   non_authority_declaration.not_runtime_authority AS not_runtime_authority
            FROM approved_result_populations
            ORDER BY result_population_id
            """
        )
        conn.execute(
            """
            CREATE VIEW v_result_population_denominator AS
            SELECT result_population_id,
                   committed_denominator_snapshot.committed_denominator AS committed_denominator,
                   committed_denominator_snapshot.result_row_count AS result_row_count,
                   committed_denominator_snapshot.outcome_counts_sum AS outcome_counts_sum,
                   committed_denominator_snapshot.result_row_count_equals_committed_denominator
                       AS rows_match_denominator,
                   committed_denominator_snapshot.outcome_counts_sum_equals_committed_denominator
                       AS outcomes_match_denominator
            FROM approved_result_populations
            ORDER BY result_population_id
            """
        )
        return conn, inputs

    def run(self, query_name: str, *, limit: int = 100) -> dict[str, Any]:
        if query_name not in QUERY_NAMES:
            raise ResourceDeniedError("unknown query identity (default deny)")
        if not isinstance(limit, int) or not 1 <= limit <= 200:
            raise ResourceDeniedError("query limit must be between 1 and 200")
        conn, inputs = self._connection()
        view_name = "v_" + query_name.replace("-", "_")
        try:
            cursor = conn.execute(f'SELECT * FROM "{view_name}" LIMIT ?', [limit])
            columns = [item[0] for item in cursor.description or []]
            rows = [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]
        finally:
            conn.close()
        return {
            "query_name": query_name,
            "rows": rows,
            "row_count": len(rows),
            "truncated_at": limit,
            "repo_sha": self.identity.repo_sha,
            "evidence_inputs": [
                {
                    "path": path.relative_to(self.repo_root).as_posix(),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
                for path in inputs
            ],
            "query_boundary": (
                "predeclared in-memory DuckDB query; no caller SQL; external access disabled "
                "after approved inputs are materialized"
            ),
            "authority": dict(NON_AUTHORITY),
        }
