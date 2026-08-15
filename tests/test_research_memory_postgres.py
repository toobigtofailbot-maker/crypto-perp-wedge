from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path

import psycopg
import pytest

from tools.research_memory.migrations import apply_migrations
from tools.research_memory.repository import ResearchMemoryRepository

FIXTURE_REPO = Path(__file__).parent / "fixtures" / "research_memory" / "repo"
TEST_DSN_ENV = "RESEARCH_MEMORY_TEST_DSN"


def _test_dsn() -> str:
    dsn = os.environ.get(TEST_DSN_ENV)
    if not dsn:
        pytest.skip(f"{TEST_DSN_ENV} is required for PostgreSQL integration tests")
    with psycopg.connect(dsn) as connection:
        database = connection.execute("SELECT current_database()").fetchone()[0]
    if "test" not in database.lower():
        pytest.fail(f"{TEST_DSN_ENV} must target an isolated database whose name contains 'test'")
    return dsn


@pytest.fixture()
def postgres_repository() -> ResearchMemoryRepository:
    dsn = _test_dsn()
    with psycopg.connect(dsn, autocommit=True) as connection:
        connection.execute("DROP SCHEMA IF EXISTS research_memory CASCADE")
    first = apply_migrations(dsn)
    second = apply_migrations(dsn)
    assert first.applied == ("0001_research_memory",)
    assert second.already_applied == ("0001_research_memory",)
    with ResearchMemoryRepository.connect(dsn) as repository:
        yield repository
    with psycopg.connect(dsn, autocommit=True) as connection:
        connection.execute("DROP SCHEMA IF EXISTS research_memory CASCADE")


@pytest.fixture()
def fixture_repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(FIXTURE_REPO, target)
    return target


def _definition() -> dict[str, object]:
    return {
        "strategy_family": "funding_momentum",
        "mechanism": "funding momentum confirmation on four hour bars.",
        "primary_timeframe": "4h",
        "required_data_features": ["funding_8h", "ohlcv_4h"],
        "free_parameter_count": 2,
    }


def _repo_hashes(repo_root: Path) -> dict[str, str]:
    return {
        path.relative_to(repo_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(repo_root.rglob("*"))
        if path.is_file()
    }


def test_bootstrap_is_idempotent_and_resolves_duplicate_and_negative_evidence(
    postgres_repository: ResearchMemoryRepository, fixture_repo: Path
) -> None:
    first = postgres_repository.refresh_from_repo(fixture_repo)
    second = postgres_repository.refresh_from_repo(fixture_repo)

    assert first == second
    assert first == {
        "hypothesis_items": 2,
        "memory_records": 2,
        "memory_aliases": 4,
        "evidence_references": 7,
    }
    duplicate = postgres_repository.has_this_been_tried(
        {
            **_definition(),
            "strategy_family": " FUNDING_MOMENTUM ",
            "required_data_features": ["OHLCV_4H", "FUNDING_8H", "OHLCV_4H"],
        },
        repo_root=fixture_repo,
    )
    assert duplicate["matched"] is True
    assert duplicate["has_been_tried_index_hint"] is True
    record = duplicate["records"][0]
    assert record["resolved_classification"] == "NO-GO"
    assert record["repo_evidence_current"] is True
    assert record["negative_reason"]
    assert any(
        ref["artifact_id"] == "DEC-9901" and ref["resolution"] == "EXACT"
        for ref in record["evidence"]
    )

    negatives = postgres_repository.negative_results(
        repo_root=fixture_repo, strategy_family="funding_momentum"
    )
    assert [row["source_key"] for row in negatives] == ["H-901"]
    assert negatives[0]["resolved_classification"] == "NO-GO"


def test_rebuild_preserves_repo_truth_and_non_authoritative_memory(
    postgres_repository: ResearchMemoryRepository, fixture_repo: Path
) -> None:
    before = _repo_hashes(fixture_repo)
    postgres_repository.refresh_from_repo(fixture_repo)
    postgres_repository.put_non_authoritative(
        _definition(),
        source_key="scratch:block-1",
        title="Blocked scratch idea",
        status="BLOCKED",
        classification="BLOCKED",
        negative_reason="Required historical feature is unavailable.",
    )

    counts = postgres_repository.refresh_from_repo(fixture_repo, rebuild=True)
    after = _repo_hashes(fixture_repo)

    assert before == after
    assert counts["memory_records"] == 3
    result = postgres_repository.has_this_been_tried(_definition(), repo_root=fixture_repo)
    blocked = next(row for row in result["records"] if row["source_key"] == "scratch:block-1")
    assert blocked["non_authoritative"] is True
    assert blocked["resolved_classification"] is None
    assert blocked["negative_reason"] == "Required historical feature is unavailable."


def test_stale_index_never_resolves_a_scientific_conclusion(
    postgres_repository: ResearchMemoryRepository, fixture_repo: Path
) -> None:
    postgres_repository.refresh_from_repo(fixture_repo)
    decision = fixture_repo / "research" / "decisions" / "DEC-9901.md"
    decision.write_text(decision.read_text(encoding="utf-8") + "\nstale change\n", encoding="utf-8")

    result = postgres_repository.lookup_alias("H-901", repo_root=fixture_repo)
    record = result["records"][0]

    assert result["index_not_truth"] is True
    assert record["repo_evidence_current"] is False
    assert record["resolved_classification"] is None
    assert any(ref["resolution"] == "HASH_MISMATCH" for ref in record["evidence"])
