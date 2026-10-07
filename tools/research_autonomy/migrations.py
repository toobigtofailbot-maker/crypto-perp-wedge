"""Checksum-locked authority migrations, independent of Research Memory."""

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


def apply_migrations(dsn: str) -> MigrationResult:
    applied, existing = [], []
    paths = tuple(sorted(MIGRATIONS_DIR.glob("[0-9][0-9][0-9][0-9]_*.sql")))
    if not paths:
        raise FileNotFoundError("authority migrations absent")
    with psycopg.connect(dsn) as conn:
        # One transaction and lock also serialize concurrent first applications.
        conn.execute("SELECT pg_advisory_xact_lock(721026001)")
        conn.execute("CREATE SCHEMA IF NOT EXISTS research_authority")
        conn.execute("""CREATE TABLE IF NOT EXISTS research_authority.schema_migrations (
            version TEXT PRIMARY KEY, content_sha256 TEXT NOT NULL
                CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
            applied_at TIMESTAMPTZ NOT NULL DEFAULT transaction_timestamp())""")
        for path in paths:
            raw = path.read_bytes()
            checksum = hashlib.sha256(raw).hexdigest()
            row = conn.execute("SELECT content_sha256 FROM research_authority.schema_migrations WHERE version=%s", (path.stem,)).fetchone()
            if row:
                if row[0] != checksum:
                    raise RuntimeError(f"applied migration checksum mismatch: {path.stem}")
                existing.append(path.stem)
            else:
                conn.execute(raw.decode("utf-8"))
                conn.execute("INSERT INTO research_authority.schema_migrations(version,content_sha256) VALUES (%s,%s)", (path.stem, checksum))
                applied.append(path.stem)
    return MigrationResult(tuple(applied), tuple(existing))
