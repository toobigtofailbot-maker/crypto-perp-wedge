"""PostgreSQL adapter for bounded hypothesis memory and exact repo evidence refs."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Self

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from tools.research_memory.fingerprint import FINGERPRINT_VERSION, HypothesisDefinition, fingerprint
from tools.research_memory.repo_source import (
    NEGATIVE_CLASSIFICATIONS,
    EvidenceSeed,
    MemorySeed,
    load_repo_memory_seeds,
)

_ALIAS_WHITESPACE = re.compile(r"\s+")
_TERMINAL_STATUSES = frozenset(
    {
        "CONCLUDED",
        "ARCHIVED",
        "PROMOTED",
        "BLOCKED",
        "INVALID",
        "INCOMPLETE",
        "SUPERSEDED",
        "REJECTED",
    }
)


def _normalize_alias(value: str) -> str:
    normalized = _ALIAS_WHITESPACE.sub(" ", value.strip()).lower()
    if not normalized:
        raise ValueError("alias must not be empty")
    return normalized


def _resolved_repo_path(repo_root: Path, relative_path: str) -> Path | None:
    candidate = Path(relative_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    cursor = repo_root
    for part in candidate.parts:
        cursor /= part
        if cursor.is_symlink():
            return None
    resolved = (repo_root / candidate).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError:
        return None
    if not resolved.is_file():
        return None
    return resolved


def _resolve_evidence(repo_root: Path | None, row: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(row)
    if repo_root is None:
        result["resolution"] = "UNVERIFIED"
        return result
    path = _resolved_repo_path(repo_root.resolve(), row["artifact_path"])
    if path is None:
        result["resolution"] = "MISSING_OR_UNSAFE"
        return result
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    result["actual_content_sha256"] = actual
    result["resolution"] = "EXACT" if actual == row["artifact_content_sha256"] else "HASH_MISMATCH"
    return result


class ResearchMemoryRepository:
    def __init__(self, connection: psycopg.Connection[Any]):
        self.connection = connection

    @classmethod
    def connect(cls, dsn: str) -> ResearchMemoryRepository:
        return cls(psycopg.connect(dsn, row_factory=dict_row))

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def refresh_from_repo(self, repo_root: Path, *, rebuild: bool = False) -> dict[str, int]:
        seeds = load_repo_memory_seeds(repo_root)
        return self._refresh(seeds, rebuild=rebuild)

    def _refresh(self, seeds: Sequence[MemorySeed], *, rebuild: bool) -> dict[str, int]:
        source_keys = [seed.source_key for seed in seeds]
        with self.connection.transaction():
            if rebuild:
                self.connection.execute(
                    "DELETE FROM research_memory.memory_aliases WHERE authority_state = 'REPO_INDEX'"
                )
                self.connection.execute(
                    "DELETE FROM research_memory.memory_records WHERE authority_state = 'REPO_INDEX'"
                )

            self.connection.execute(
                "DELETE FROM research_memory.memory_aliases WHERE authority_state = 'REPO_INDEX'"
            )
            for seed in seeds:
                item_id = self._upsert_item(seed.definition)
                record_id = self._upsert_record(item_id, seed)
                self.connection.execute(
                    "DELETE FROM research_memory.evidence_references WHERE memory_record_id = %s",
                    (record_id,),
                )
                for evidence in seed.evidence:
                    self._insert_evidence(record_id, evidence)
                for alias_kind, alias in seed.aliases:
                    self.connection.execute(
                        """
                        INSERT INTO research_memory.memory_aliases(
                            memory_item_id, authority_state, source_key, alias_kind, alias_key
                        ) VALUES (%s, 'REPO_INDEX', %s, %s, %s)
                        ON CONFLICT (authority_state, source_key, alias_kind, alias_key)
                        DO UPDATE SET memory_item_id = EXCLUDED.memory_item_id
                        """,
                        (item_id, seed.source_key, alias_kind, _normalize_alias(alias)),
                    )

            if source_keys:
                self.connection.execute(
                    """
                    DELETE FROM research_memory.memory_records
                    WHERE authority_state = 'REPO_INDEX'
                      AND NOT (source_key = ANY(%s))
                    """,
                    (source_keys,),
                )
            else:
                self.connection.execute(
                    "DELETE FROM research_memory.memory_records WHERE authority_state = 'REPO_INDEX'"
                )
            self.connection.execute(
                """
                DELETE FROM research_memory.hypothesis_items AS item
                WHERE NOT EXISTS (
                    SELECT 1 FROM research_memory.memory_records AS record
                    WHERE record.memory_item_id = item.memory_item_id
                )
                """
            )

        return self.counts()

    def _upsert_item(self, definition: HypothesisDefinition) -> int:
        canonical = definition.canonical_mapping()
        row = self.connection.execute(
            """
            INSERT INTO research_memory.hypothesis_items(
                fingerprint_version, fingerprint_sha256, strategy_family, mechanism,
                primary_timeframe, instrument_scope, required_data_features,
                free_parameter_count, canonical_definition
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (fingerprint_sha256) DO UPDATE SET
                strategy_family = EXCLUDED.strategy_family,
                mechanism = EXCLUDED.mechanism,
                primary_timeframe = EXCLUDED.primary_timeframe,
                instrument_scope = EXCLUDED.instrument_scope,
                required_data_features = EXCLUDED.required_data_features,
                free_parameter_count = EXCLUDED.free_parameter_count,
                canonical_definition = EXCLUDED.canonical_definition,
                updated_at = CURRENT_TIMESTAMP
            RETURNING memory_item_id
            """,
            (
                FINGERPRINT_VERSION,
                fingerprint(definition),
                definition.strategy_family,
                definition.mechanism,
                definition.primary_timeframe,
                definition.instrument_scope,
                list(definition.required_data_features),
                definition.free_parameter_count,
                Jsonb(canonical),
            ),
        ).fetchone()
        assert row is not None
        return row[0] if not isinstance(row, Mapping) else row["memory_item_id"]

    def _upsert_record(self, item_id: int, seed: MemorySeed) -> int:
        row = self.connection.execute(
            """
            INSERT INTO research_memory.memory_records(
                memory_item_id, authority_state, source_key, title, status, classification,
                negative_reason, source_created_at, source_updated_at, source_metadata
            ) VALUES (%s, 'REPO_INDEX', %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (authority_state, source_key) DO UPDATE SET
                memory_item_id = EXCLUDED.memory_item_id,
                title = EXCLUDED.title,
                status = EXCLUDED.status,
                classification = EXCLUDED.classification,
                negative_reason = EXCLUDED.negative_reason,
                source_created_at = EXCLUDED.source_created_at,
                source_updated_at = EXCLUDED.source_updated_at,
                source_metadata = EXCLUDED.source_metadata,
                refreshed_at = CURRENT_TIMESTAMP
            RETURNING memory_record_id
            """,
            (
                item_id,
                seed.source_key,
                seed.title,
                seed.status,
                seed.classification,
                seed.negative_reason,
                seed.source_created_at,
                seed.source_updated_at,
                Jsonb(seed.source_metadata),
            ),
        ).fetchone()
        assert row is not None
        return row[0] if not isinstance(row, Mapping) else row["memory_record_id"]

    def _insert_evidence(self, record_id: int, evidence: EvidenceSeed) -> None:
        self.connection.execute(
            """
            INSERT INTO research_memory.evidence_references(
                memory_record_id, artifact_path, artifact_id, evidence_role,
                artifact_content_sha256, source_record_sha256, supports_conclusion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                record_id,
                evidence.artifact_path,
                evidence.artifact_id,
                evidence.evidence_role,
                evidence.artifact_content_sha256,
                evidence.source_record_sha256,
                evidence.supports_conclusion,
            ),
        )

    def put_non_authoritative(
        self,
        definition: HypothesisDefinition | Mapping[str, Any],
        *,
        source_key: str,
        title: str,
        status: str,
        classification: str,
        negative_reason: str | None = None,
        source_metadata: Mapping[str, Any] | None = None,
    ) -> int:
        """Store mutable pre-canonical memory with explicit non-authority."""

        normalized = (
            definition
            if isinstance(definition, HypothesisDefinition)
            else HypothesisDefinition.from_mapping(definition)
        )
        if classification in NEGATIVE_CLASSIFICATIONS and not negative_reason:
            raise ValueError("negative non-authoritative memory requires negative_reason")
        with self.connection.transaction():
            item_id = self._upsert_item(normalized)
            row = self.connection.execute(
                """
                INSERT INTO research_memory.memory_records(
                    memory_item_id, authority_state, source_key, title, status,
                    classification, negative_reason, source_metadata
                ) VALUES (%s, 'NON_AUTHORITATIVE', %s, %s, %s, %s, %s, %s)
                ON CONFLICT (authority_state, source_key) DO UPDATE SET
                    memory_item_id = EXCLUDED.memory_item_id,
                    title = EXCLUDED.title,
                    status = EXCLUDED.status,
                    classification = EXCLUDED.classification,
                    negative_reason = EXCLUDED.negative_reason,
                    source_metadata = EXCLUDED.source_metadata,
                    refreshed_at = CURRENT_TIMESTAMP
                RETURNING memory_record_id
                """,
                (
                    item_id,
                    source_key,
                    title,
                    status,
                    classification,
                    negative_reason,
                    Jsonb(dict(source_metadata or {})),
                ),
            ).fetchone()
        assert row is not None
        return row[0] if not isinstance(row, Mapping) else row["memory_record_id"]

    def has_this_been_tried(
        self,
        definition: HypothesisDefinition | Mapping[str, Any],
        *,
        repo_root: Path | None = None,
    ) -> dict[str, Any]:
        return self._lookup_by_clause(
            "item.fingerprint_sha256 = %s", (fingerprint(definition),), repo_root=repo_root
        )

    def lookup_alias(
        self, alias: str, *, alias_kind: str = "candidate_id", repo_root: Path | None = None
    ) -> dict[str, Any]:
        return self._lookup_by_clause(
            """
            EXISTS (
                SELECT 1 FROM research_memory.memory_aliases AS alias
                WHERE alias.memory_item_id = item.memory_item_id
                  AND alias.alias_kind = %s AND alias.alias_key = %s
            )
            """,
            (alias_kind, _normalize_alias(alias)),
            repo_root=repo_root,
        )

    def _lookup_by_clause(
        self, clause: str, params: Sequence[Any], *, repo_root: Path | None
    ) -> dict[str, Any]:
        item = self.connection.execute(
            f"""
            SELECT item.*
            FROM research_memory.hypothesis_items AS item
            WHERE {clause}
            ORDER BY item.memory_item_id
            LIMIT 1
            """,
            params,
        ).fetchone()
        if item is None:
            return {
                "matched": False,
                "has_been_tried_index_hint": False,
                "index_not_truth": True,
                "records": [],
            }
        item_dict = dict(item)
        records = self.connection.execute(
            """
            SELECT * FROM research_memory.memory_records
            WHERE memory_item_id = %s
            ORDER BY authority_state, source_key
            """,
            (item_dict["memory_item_id"],),
        ).fetchall()
        materialized = [self._materialize_record(dict(record), repo_root) for record in records]
        return {
            "matched": True,
            "fingerprint_sha256": item_dict["fingerprint_sha256"],
            "fingerprint_version": item_dict["fingerprint_version"],
            "definition": item_dict["canonical_definition"],
            "has_been_tried_index_hint": any(
                record["status"] in _TERMINAL_STATUSES for record in materialized
            ),
            "index_not_truth": True,
            "records": materialized,
        }

    def _materialize_record(self, record: dict[str, Any], repo_root: Path | None) -> dict[str, Any]:
        evidence_rows = self.connection.execute(
            """
            SELECT artifact_path, artifact_id, evidence_role, artifact_content_sha256,
                   source_record_sha256, supports_conclusion
            FROM research_memory.evidence_references
            WHERE memory_record_id = %s
            ORDER BY evidence_role, artifact_path
            """,
            (record["memory_record_id"],),
        ).fetchall()
        evidence = [_resolve_evidence(repo_root, dict(row)) for row in evidence_rows]
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

    def negative_results(
        self,
        *,
        repo_root: Path | None = None,
        strategy_family: str | None = None,
        primary_timeframe: str | None = None,
    ) -> list[dict[str, Any]]:
        where = ["record.classification = ANY(%s)"]
        params: list[Any] = [sorted(NEGATIVE_CLASSIFICATIONS)]
        if strategy_family is not None:
            where.append("item.strategy_family = %s")
            params.append(strategy_family.strip().lower())
        if primary_timeframe is not None:
            where.append("item.primary_timeframe = %s")
            params.append(primary_timeframe.strip().lower())
        rows = self.connection.execute(
            f"""
            SELECT record.*
            FROM research_memory.memory_records AS record
            JOIN research_memory.hypothesis_items AS item
              ON item.memory_item_id = record.memory_item_id
            WHERE {" AND ".join(where)}
            ORDER BY record.source_key
            """,
            params,
        ).fetchall()
        return [self._materialize_record(dict(row), repo_root) for row in rows]

    def counts(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for name in ("hypothesis_items", "memory_records", "memory_aliases", "evidence_references"):
            row = self.connection.execute(
                f"SELECT COUNT(*) AS count FROM research_memory.{name}"
            ).fetchone()
            assert row is not None
            result[name] = row[0] if not isinstance(row, Mapping) else row["count"]
        return result
