"""Small checksum-locked SQL migration runner backed by psycopg 3."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import psycopg

MIGRATIONS_DIR = Path(__file__).resolve().with_name("migrations")


@dataclass(frozen=True)
class MigrationResult:
    applied: tuple[str, ...]
    already_applied: tuple[str, ...]


def _migration_files() -> tuple[Path, ...]:
    files = tuple(sorted(MIGRATIONS_DIR.glob("[0-9][0-9][0-9][0-9]_*.sql")))
    if not files:
        raise FileNotFoundError(f"no research-memory migrations found: {MIGRATIONS_DIR}")
    return files


def apply_migrations(dsn: str) -> MigrationResult:
    applied: list[str] = []
    existing: list[str] = []
    with psycopg.connect(dsn) as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS research_memory")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS research_memory.schema_migrations (
                version TEXT PRIMARY KEY,
                content_sha256 CHAR(64) NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CHECK (content_sha256 ~ '^[0-9a-f]{64}$')
            )
            """
        )
        conn.commit()

        for path in _migration_files():
            version = path.stem
            sql = path.read_text(encoding="utf-8")
            checksum = hashlib.sha256(path.read_bytes()).hexdigest()
            row = conn.execute(
                """
                SELECT content_sha256
                FROM research_memory.schema_migrations
                WHERE version = %s
                """,
                (version,),
            ).fetchone()
            if row:
                if row[0] != checksum:
                    raise RuntimeError(
                        f"applied migration checksum mismatch for {version}: {row[0]} != {checksum}"
                    )
                existing.append(version)
                conn.commit()
                continue
            with conn.transaction():
                conn.execute(sql)
                conn.execute(
                    """
                    INSERT INTO research_memory.schema_migrations(version, content_sha256)
                    VALUES (%s, %s)
                    """,
                    (version, checksum),
                )
            applied.append(version)
    return MigrationResult(tuple(applied), tuple(existing))
