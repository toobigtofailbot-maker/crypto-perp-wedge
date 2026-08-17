"""Technically read-only PostgreSQL Research Memory reader."""

from __future__ import annotations

import hashlib
import re
from typing import Any

import psycopg
from psycopg.rows import dict_row

from .models import NON_AUTHORITY, EvidenceUnavailableError, ResourceDeniedError
from .resources import EvidenceResourceCatalog

_ALIAS_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 .:_/-]{0,127}$")
_ALIAS_KINDS = frozenset({"candidate_id", "name"})
_TABLES = (
    "hypothesis_items",
    "memory_records",
    "memory_aliases",
    "evidence_references",
)


class ReadOnlyResearchMemoryReader:
    """Use a DB-enforced read-only transaction and reject write-capable roles."""

    def __init__(self, dsn: str | None, catalog: EvidenceResourceCatalog) -> None:
        self._dsn = dsn.strip() if dsn else None
        self._catalog = catalog

    @property
    def configured(self) -> bool:
        return self._dsn is not None

    def _connect(self) -> psycopg.Connection[Any]:
        if not self._dsn:
            raise EvidenceUnavailableError("Research Memory read-only DSN is not configured")
        connection = psycopg.connect(
            self._dsn,
            row_factory=dict_row,
            options="-c default_transaction_read_only=on",
        )
        try:
            default_read_only = connection.execute("SHOW default_transaction_read_only").fetchone()
            if not default_read_only or default_read_only["default_transaction_read_only"] != "on":
                raise ResourceDeniedError("PostgreSQL session is not default read-only")
            for table in _TABLES:
                privileges = connection.execute(
                    """
                    SELECT
                      has_schema_privilege(current_user, 'research_memory', 'USAGE') AS schema_use,
                      has_table_privilege(current_user, %s, 'SELECT') AS can_select,
                      (has_table_privilege(current_user, %s, 'INSERT') OR
                       has_table_privilege(current_user, %s, 'UPDATE') OR
                       has_table_privilege(current_user, %s, 'DELETE') OR
                       has_table_privilege(current_user, %s, 'TRUNCATE') OR
                       has_table_privilege(current_user, %s, 'REFERENCES') OR
                       has_table_privilege(current_user, %s, 'TRIGGER')) AS can_mutate
                    """,
                    [f"research_memory.{table}"] * 7,
                ).fetchone()
                if not privileges or not privileges["schema_use"] or not privileges["can_select"]:
                    raise ResourceDeniedError(f"read-only role cannot select {table}")
                if privileges["can_mutate"]:
                    raise ResourceDeniedError(
                        f"Research Memory role has mutation privilege on {table}"
                    )
            return connection
        except Exception:
            connection.close()
            raise

    def lookup_alias(self, alias: str, *, alias_kind: str = "candidate_id") -> dict[str, Any]:
        if alias_kind not in _ALIAS_KINDS:
            raise ResourceDeniedError("unknown Research Memory alias kind")
        if not isinstance(alias, str) or _ALIAS_RE.fullmatch(alias.strip()) is None:
            raise ResourceDeniedError("Research Memory alias is invalid")
        normalized = " ".join(alias.strip().lower().split())
        connection = self._connect()
        try:
            with connection.transaction():
                connection.execute("SET TRANSACTION READ ONLY")
                item = connection.execute(
                    """
                    SELECT item.*
                    FROM research_memory.hypothesis_items AS item
                    JOIN research_memory.memory_aliases AS alias
                      ON alias.memory_item_id = item.memory_item_id
                    WHERE alias.alias_kind = %s AND alias.alias_key = %s
                    ORDER BY item.memory_item_id
                    LIMIT 1
                    """,
                    (alias_kind, normalized),
                ).fetchone()
                if item is None:
                    return {
                        "matched": False,
                        "index_not_truth": True,
                        "records": [],
                        "repo_sha": self._catalog.identity.repo_sha,
                        "authority": dict(NON_AUTHORITY),
                    }
                records = connection.execute(
                    """
                    SELECT * FROM research_memory.memory_records
                    WHERE memory_item_id = %s
                    ORDER BY authority_state, source_key
                    """,
                    (item["memory_item_id"],),
                ).fetchall()
                materialized = [self._materialize(connection, dict(record)) for record in records]
                return {
                    "matched": True,
                    "fingerprint_sha256": item["fingerprint_sha256"],
                    "definition": item["canonical_definition"],
                    "index_not_truth": True,
                    "records": materialized,
                    "repo_sha": self._catalog.identity.repo_sha,
                    "postgres_boundary": (
                        "default_transaction_read_only=on; SET TRANSACTION READ ONLY; "
                        "role rejected if any mutation privilege exists"
                    ),
                    "authority": dict(NON_AUTHORITY),
                }
        finally:
            connection.close()

    def _materialize(
        self, connection: psycopg.Connection[Any], record: dict[str, Any]
    ) -> dict[str, Any]:
        rows = connection.execute(
            """
            SELECT artifact_path, artifact_id, evidence_role, artifact_content_sha256,
                   source_record_sha256, supports_conclusion
            FROM research_memory.evidence_references
            WHERE memory_record_id = %s
            ORDER BY evidence_role, artifact_path
            """,
            (record["memory_record_id"],),
        ).fetchall()
        evidence = []
        for row in rows:
            materialized = dict(row)
            try:
                path = self._catalog.approved_path(materialized["artifact_path"])
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                materialized["resolution"] = (
                    "EXACT"
                    if actual == materialized["artifact_content_sha256"]
                    else "HASH_MISMATCH"
                )
                materialized["actual_sha256"] = actual
            except (ResourceDeniedError, EvidenceUnavailableError):
                materialized["resolution"] = "NOT_ALLOWLISTED_OR_MISSING"
                materialized["actual_sha256"] = None
            evidence.append(materialized)
        all_exact = bool(evidence) and all(row["resolution"] == "EXACT" for row in evidence)
        has_support = any(row["supports_conclusion"] for row in evidence)
        repo_backed = record["authority_state"] == "REPO_INDEX"
        record["evidence"] = evidence
        record["repo_evidence_current"] = repo_backed and all_exact
        record["resolved_classification"] = (
            record["classification"] if repo_backed and all_exact and has_support else None
        )
        record["non_authoritative"] = not repo_backed
        return record
