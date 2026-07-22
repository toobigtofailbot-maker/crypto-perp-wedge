from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

from tools.canon_intake import external_content_readiness as readiness
from tools.registry.validate_variant_sweep_artifacts import canonical_json_bytes


REPO_ROOT = Path(__file__).resolve().parents[1]


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()


def _copy(root: Path, relative: str) -> None:
    source = REPO_ROOT / relative
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def _fact(root: Path) -> dict[str, Any]:
    spec_raw = (root / readiness.PRODUCTION_SPEC_PATH).read_bytes()
    spec = json.loads(spec_raw)
    tool_raw = (root / readiness.CANONICALIZER_PATH).read_bytes()
    head = _git(root, "rev-parse", "HEAD")
    tool_blob = _git(root, "hash-object", readiness.CANONICALIZER_PATH.as_posix())
    return {
        "schema_version": "strategy_spec_external_content_readiness_v1",
        "fact_id": readiness.PRODUCTION_FACT_ID,
        "fact_path": readiness.PRODUCTION_FACT_PATH.as_posix(),
        "scope": "h004_dispatch_external_content_readiness",
        "strategy_spec": {
            "strategy_spec_id": readiness.PRODUCTION_SPEC_ID,
            "path": readiness.PRODUCTION_SPEC_PATH.as_posix(),
        },
        "content_binding": {
            "raw_byte_length": len(spec_raw),
            "raw_file_sha256": readiness._sha256(spec_raw),
            "canonicalization": readiness.CANONICALIZATION,
            "full_repo_canonical_json_sha256": readiness._sha256(
                canonical_json_bytes(spec)
            ),
        },
        "source_git": {
            "commit_sha": head,
            "blob_sha": _git(
                root, "hash-object", readiness.PRODUCTION_SPEC_PATH.as_posix()
            ),
        },
        "computation": {
            "tool_identity": readiness.CANONICALIZER_IDENTITY,
            "tool_path": readiness.CANONICALIZER_PATH.as_posix(),
            "tool_sha256": readiness._sha256(tool_raw),
            "tool_version": f"git-blob:{tool_blob}",
        },
        "computed_at": "2026-07-22T20:00:00Z",
        "readiness_state": "external_content_ready",
        "legacy_internal_hash": {
            "hash_status_observed": "not_computed",
            "hash_scope_version_observed": "strategy_spec_hash_scope_v1",
            "canonical_spec_hash_observed": None,
            "legacy_hash_scope_reproducibility": "unresolved",
        },
        "no_mutation_proof": {
            "strategy_spec_bytes_unchanged": True,
            "variant_manifest_parent_binding_unchanged": True,
            "sweep_plan_unchanged": True,
            "source_bytes_revalidated_immediately_before_write": True,
        },
        "immutability": {
            "exclusive_create": True,
            "overwrite_forbidden": True,
            "delete_recreate_forbidden": True,
            "in_place_repair_forbidden": True,
            "duplicate_fact_forbidden": True,
            "superseding_fact_forbidden": True,
        },
        "dispatch_prerequisite_only": True,
        "non_authority_declaration": {
            "content_integrity_only": True,
            "not_repo_wide_hash_migration": True,
            "not_legacy_hash_reinterpretation": True,
            "not_dispatch_authority": True,
            "not_execution_authority": True,
            "not_result_population_authority": True,
            "not_ranking_authority": True,
            "not_readiness_beyond_content_integrity": True,
            "not_runtime_authority": True,
            "not_paper_live_authority": True,
            "not_oms_risk_reconciliation_authority": True,
        },
    }


def _write_proposed(root: Path, fact: dict[str, Any]) -> Path:
    path = root / "scratch" / "proposed.external_content_readiness.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(fact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path


@pytest.fixture()
def synthetic_repo(tmp_path: Path) -> tuple[Path, dict[str, Any], Path]:
    for relative in (
        readiness.PRODUCTION_SPEC_PATH.as_posix(),
        "research/variant_manifests/VM-0007.variant_manifest.json",
        "research/sweep_plans/SWEEP-PLAN-0007.sweep_plan.json",
        readiness.SCHEMA_PATH.as_posix(),
        readiness.CANONICALIZER_PATH.as_posix(),
    ):
        _copy(tmp_path, relative)
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "tests@example.invalid")
    _git(tmp_path, "config", "user.name", "Readiness Tests")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "synthetic locked source")
    fact = _fact(tmp_path)
    proposed = _write_proposed(tmp_path, fact)
    return tmp_path, fact, proposed


def test_exclusive_create_and_deterministic_validation(
    synthetic_repo: tuple[Path, dict[str, Any], Path]
) -> None:
    root, fact, proposed = synthetic_repo
    proposed_raw = proposed.read_bytes()

    written = readiness.write_external_content_readiness_fact(
        repo_root=root, proposed_fact_path=proposed
    )
    target = root / readiness.PRODUCTION_FACT_PATH

    assert written == fact
    assert target.read_bytes() == proposed_raw
    assert readiness.validate_external_content_readiness_corpus(root) == []
    assert readiness.validate_external_content_readiness_corpus(root) == []
    assert not (root / readiness.LOCK_PATH).exists()
    assert not (root / "research/dispatch_records").exists()
    assert not (root / "research/execution_events").exists()
    assert not (root / "research/result_populations").exists()


@pytest.mark.parametrize(
    ("path", "value", "expected_text"),
    [
        ("fact_id", "SS-ECR-STRAT-SPEC-9999", "identity_mismatch"),
        (
            "fact_path",
            "research/strategy_spec_external_content_readiness/wrong.json",
            "schema_violation",
        ),
        ("strategy_spec.strategy_spec_id", "STRAT-SPEC-0006", "identity_mismatch"),
        ("content_binding.raw_byte_length", 1, "content_mismatch"),
        (
            "content_binding.raw_file_sha256",
            "sha256:" + "0" * 64,
            "content_mismatch",
        ),
        (
            "content_binding.full_repo_canonical_json_sha256",
            "sha256:" + "0" * 64,
            "content_mismatch",
        ),
        ("content_binding.canonicalization", "another_algorithm", "schema_violation"),
        ("source_git.commit_sha", "0" * 40, "git_binding_mismatch"),
        ("source_git.blob_sha", "0" * 40, "git_binding_mismatch"),
        ("computation.tool_identity", "wrong_tool", "tool_mismatch"),
        ("computation.tool_sha256", "sha256:" + "0" * 64, "tool_mismatch"),
        ("computation.tool_version", "git-blob:" + "0" * 40, "tool_mismatch"),
        (
            "legacy_internal_hash.hash_status_observed",
            "computed",
            "legacy_observation_mismatch",
        ),
        (
            "legacy_internal_hash.legacy_hash_scope_reproducibility",
            "verified",
            "schema_violation",
        ),
        (
            "non_authority_declaration.not_repo_wide_hash_migration",
            False,
            "schema_violation",
        ),
        (
            "non_authority_declaration.not_dispatch_authority",
            False,
            "schema_violation",
        ),
        (
            "non_authority_declaration.not_execution_authority",
            False,
            "schema_violation",
        ),
        (
            "non_authority_declaration.not_runtime_authority",
            False,
            "schema_violation",
        ),
    ],
)
def test_mutations_fail_closed(
    synthetic_repo: tuple[Path, dict[str, Any], Path],
    path: str,
    value: Any,
    expected_text: str,
) -> None:
    root, fact, _ = synthetic_repo
    mutated = copy.deepcopy(fact)
    current: dict[str, Any] = mutated
    parts = path.split(".")
    for part in parts[:-1]:
        current = current[part]
    current[parts[-1]] = value
    proposed = _write_proposed(root, mutated)

    with pytest.raises(readiness.ExternalContentReadinessError) as caught:
        readiness.write_external_content_readiness_fact(
            repo_root=root, proposed_fact_path=proposed
        )

    assert expected_text in str(caught.value)
    assert not (root / readiness.PRODUCTION_FACT_PATH).exists()


def test_overwrite_and_second_fact_are_rejected(
    synthetic_repo: tuple[Path, dict[str, Any], Path]
) -> None:
    root, _, proposed = synthetic_repo
    readiness.write_external_content_readiness_fact(
        repo_root=root, proposed_fact_path=proposed
    )
    before = (root / readiness.PRODUCTION_FACT_PATH).read_bytes()

    with pytest.raises(readiness.ExternalContentReadinessError, match="already used"):
        readiness.write_external_content_readiness_fact(
            repo_root=root, proposed_fact_path=proposed
        )

    assert (root / readiness.PRODUCTION_FACT_PATH).read_bytes() == before


def test_retained_history_forbids_delete_recreate(
    synthetic_repo: tuple[Path, dict[str, Any], Path]
) -> None:
    root, _, proposed = synthetic_repo
    readiness.write_external_content_readiness_fact(
        repo_root=root, proposed_fact_path=proposed
    )
    _git(root, "add", ".")
    _git(root, "commit", "-m", "record readiness")
    (root / readiness.PRODUCTION_FACT_PATH).unlink()
    replacement = _fact(root)
    proposed = _write_proposed(root, replacement)

    with pytest.raises(readiness.ExternalContentReadinessError, match="retained history"):
        readiness.write_external_content_readiness_fact(
            repo_root=root, proposed_fact_path=proposed
        )


def test_duplicate_path_and_spec_are_visible_in_corpus_validation(
    synthetic_repo: tuple[Path, dict[str, Any], Path]
) -> None:
    root, fact, proposed = synthetic_repo
    readiness.write_external_content_readiness_fact(
        repo_root=root, proposed_fact_path=proposed
    )
    duplicate = root / readiness.FACT_ROOT / "duplicate.external_content_readiness.json"
    duplicate.write_text(json.dumps(fact), encoding="utf-8")

    issue_types = {
        row["issue_type"]
        for row in readiness.validate_external_content_readiness_corpus(root)
    }

    assert "external_content_readiness_duplicate_fact" in issue_types
    assert "external_content_readiness_duplicate_spec" in issue_types
    assert "external_content_readiness_fact_count_mismatch" in issue_types


def test_proposed_path_escape_is_rejected(
    synthetic_repo: tuple[Path, dict[str, Any], Path], tmp_path: Path
) -> None:
    root, fact, _ = synthetic_repo
    outside = tmp_path.parent / "outside-proposed.json"
    outside.write_text(json.dumps(fact), encoding="utf-8")

    with pytest.raises(readiness.ExternalContentReadinessError, match="escapes"):
        readiness.write_external_content_readiness_fact(
            repo_root=root, proposed_fact_path=outside
        )


def test_symlink_component_is_rejected_without_os_symlink(
    synthetic_repo: tuple[Path, dict[str, Any], Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, proposed = synthetic_repo
    original = Path.is_symlink

    def simulated(path: Path) -> bool:
        if path == proposed.parent:
            return True
        return original(path)

    monkeypatch.setattr(Path, "is_symlink", simulated)
    with pytest.raises(readiness.ExternalContentReadinessError, match="symlinked"):
        readiness.write_external_content_readiness_fact(
            repo_root=root, proposed_fact_path=proposed
        )


def test_source_mutation_before_locked_revalidation_is_rejected(
    synthetic_repo: tuple[Path, dict[str, Any], Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, proposed = synthetic_repo
    original = readiness._assert_unused
    calls = 0

    def mutate_after_preflight(repo_root: Path) -> None:
        nonlocal calls
        original(repo_root)
        calls += 1
        if calls == 1:
            source = repo_root / readiness.PRODUCTION_SPEC_PATH
            source.write_bytes(source.read_bytes() + b" ")

    monkeypatch.setattr(readiness, "_assert_unused", mutate_after_preflight)
    with pytest.raises(readiness.ExternalContentReadinessError, match="content_mismatch"):
        readiness.write_external_content_readiness_fact(
            repo_root=root, proposed_fact_path=proposed
        )

    assert not (root / readiness.PRODUCTION_FACT_PATH).exists()


def test_production_fact_hash_is_stable_after_write(
    synthetic_repo: tuple[Path, dict[str, Any], Path]
) -> None:
    root, _, proposed = synthetic_repo
    expected = hashlib.sha256(proposed.read_bytes()).hexdigest()
    readiness.write_external_content_readiness_fact(
        repo_root=root, proposed_fact_path=proposed
    )
    assert hashlib.sha256(
        (root / readiness.PRODUCTION_FACT_PATH).read_bytes()
    ).hexdigest() == expected
