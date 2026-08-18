"""Checksum-locked PostgreSQL migrations for durable Hermes broker state."""

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
        raise FileNotFoundError(f"no Hermes broker migrations found: {MIGRATIONS_DIR}")
    return files


def apply_migrations(dsn: str) -> MigrationResult:
    """Apply immutable broker-owned migrations and reject changed applied bytes."""

    applied: list[str] = []
    existing: list[str] = []
    with psycopg.connect(dsn) as connection:
        connection.execute("CREATE SCHEMA IF NOT EXISTS hermes_broker")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS hermes_broker.schema_migrations (
                version TEXT PRIMARY KEY,
                content_sha256 CHAR(64) NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
                CHECK (content_sha256 ~ '^[0-9a-f]{64}$')
            )
            """
        )
        connection.commit()

        for path in _migration_files():
            version = path.stem
            sql = path.read_text(encoding="utf-8")
            checksum = hashlib.sha256(path.read_bytes()).hexdigest()
            row = connection.execute(
                """
                SELECT content_sha256
                FROM hermes_broker.schema_migrations
                WHERE version = %s
                """,
                (version,),
            ).fetchone()
            if row is not None:
                if row[0] != checksum:
                    raise RuntimeError(
                        f"applied migration checksum mismatch for {version}: {row[0]} != {checksum}"
                    )
                existing.append(version)
                connection.commit()
                continue
            with connection.transaction():
                connection.execute(sql)
                connection.execute(
                    """
                    INSERT INTO hermes_broker.schema_migrations(version, content_sha256)
                    VALUES (%s, %s)
                    """,
                    (version, checksum),
                )
            applied.append(version)
    return MigrationResult(tuple(applied), tuple(existing))
