from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator, FormatChecker

from tools.registry.validate_variant_sweep_artifacts import canonical_json_bytes


REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE_PATH = (
    REPO_ROOT
    / "docs"
    / "architecture"
    / "canon_strategy_spec_dispatch_content_readiness.md"
)
SCHEMA_PATH = (
    REPO_ROOT
    / "research"
    / "schemas"
    / "strategy_spec_external_content_readiness.schema.json"
)
PACKAGE_ROOT = (
    REPO_ROOT / "scratch" / "WP-CANON-SPEC-HASH-CONTRACT-DESIGN-LOCK-01"
)
VALID_ROOT = PACKAGE_ROOT / "fixtures" / "valid"
INVALID_ROOT = PACKAGE_ROOT / "fixtures" / "invalid"
GENERIC_SPEC = PACKAGE_ROOT / "fixtures" / "specs" / "STRAT-SPEC-9000.strategy_spec.json"
PRODUCTION_FACT_ROOT = REPO_ROOT / "research" / "strategy_spec_external_content_readiness"


PRESERVED_STRATEGY_SPEC_HASHES = {
    "STRAT-SPEC-0001.strategy_spec.json": "a7e7bb5d4a5eda5a1d2ebb842d828f664064dae69859d8cda1ec5015ac5f342c",
    "STRAT-SPEC-0002.strategy_spec.json": "d2e0820864c882361fbd466c6ae0eaea03568e4ccc8dfaee4a3114a330f18574",
    "STRAT-SPEC-0003.strategy_spec.json": "b20e8df8e45d69da2c6d679e23e30147d6928dd63e7d216f493e0e671554a6c7",
    "STRAT-SPEC-0004.strategy_spec.json": "75aaeae687bc1976467c132bbcc1b146668bbce1082683608c41c9460856482a",
    "STRAT-SPEC-0005.strategy_spec.json": "1baeb4da177750795266091b2b7d50094f95d65c74059aa2ee1c5769171219b7",
    "STRAT-SPEC-0006.strategy_spec.json": "f0d8109822c75820aaf3e2837246ac2e5b14cb838b8cf40d5677e5720bceb0c5",
    "STRAT-SPEC-0007.strategy_spec.json": "b23ebc1093df51b7fab5e39c46fd2b96b5e71d35300134eb319a5cbc32d0857c",
}
PRESERVED_VARIANT_MANIFEST_HASHES = {
    "VM-0001.variant_manifest.json": "af790cb6d143907695031928d441c0d8e6c240a90c2d08610d4e930aea13d972",
    "VM-0002.variant_manifest.json": "766715c976c1b309add2b5ba031d5741c005a4678ac0bd17f570c2bcc1715eee",
    "VM-0003.variant_manifest.json": "069c4e505003b104a4b17f3e3ad8ca66240e205b615fdc77354c065373ffc1f2",
    "VM-0004.variant_manifest.json": "e408dbc7d562ff6377d9b9d40f33e867b55870fcce7e89e82516e77d8f07d429",
    "VM-0005.variant_manifest.json": "b198428d25c376c2e2e75f3237d842435d526192a297893b15a3952182e2ffe6",
    "VM-0006.variant_manifest.json": "fc8e87a1cc34c1b1fcec6ded9871ffeae5d26392dca3bff99235c80f9969aa6a",
    "VM-0007.variant_manifest.json": "822da9ca46eca4f3a9d4d86936fdd3447004ef77806fc3ce60ab0cf979ea171d",
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _validator() -> Draft7Validator:
    return Draft7Validator(_load(SCHEMA_PATH), format_checker=FormatChecker())


def _sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def _schema_error_text(fact: dict[str, Any]) -> str:
    messages = []
    for error in sorted(_validator().iter_errors(fact), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path)
        messages.append(f"{location}: {error.message}" if location else error.message)
    return "\n".join(messages)


def _set_path(value: dict[str, Any], dotted_path: str, replacement: Any) -> None:
    parts = dotted_path.split(".")
    current: dict[str, Any] = value
    for part in parts[:-1]:
        current = current[part]
    current[parts[-1]] = replacement


def _delete_path(value: dict[str, Any], dotted_path: str) -> None:
    parts = dotted_path.split(".")
    current: dict[str, Any] = value
    for part in parts[:-1]:
        current = current[part]
    del current[parts[-1]]


def _semantic_errors(fact: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    spec_id = fact["strategy_spec"]["strategy_spec_id"]
    expected_fact_id = f"SS-ECR-{spec_id}"
    expected_fact_path = (
        "research/strategy_spec_external_content_readiness/"
        f"{expected_fact_id}.external_content_readiness.json"
    )
    expected_spec_path = f"research/strategy_specs/{spec_id}.strategy_spec.json"
    if fact["fact_id"] != expected_fact_id:
        errors.append("fact ID does not derive from Strategy Spec ID")
    if fact["fact_path"] != expected_fact_path:
        errors.append("fact path does not derive from fact ID")
    if fact["strategy_spec"]["path"] != expected_spec_path:
        errors.append("Strategy Spec path does not derive from Strategy Spec ID")

    source = root / Path(fact["strategy_spec"]["path"])
    if not source.is_file():
        errors.append("Strategy Spec source is missing")
        return errors
    raw = source.read_bytes()
    payload = json.loads(raw.decode("utf-8"))
    if payload.get("strategy_spec_id") != spec_id:
        errors.append("Strategy Spec ID does not match source content")
    content = fact["content_binding"]
    if content["raw_byte_length"] != len(raw):
        errors.append("raw byte length mismatch")
    if content["raw_file_sha256"] != _sha256(raw):
        errors.append("raw file SHA-256 mismatch")
    canonical_hash = _sha256(canonical_json_bytes(payload))
    if content["full_repo_canonical_json_sha256"] != canonical_hash:
        errors.append("full repo-canonical JSON SHA-256 mismatch")

    if fact["source_git"]["commit_sha"] != "0" * 40:
        if fact["source_git"]["blob_sha"] != _git_blob_sha(raw):
            errors.append("source Git blob SHA mismatch")
    if "hash_pinning" in payload:
        legacy = fact["legacy_internal_hash"]
        pinning = payload["hash_pinning"]
        if legacy["hash_status_observed"] != pinning["hash_status"]:
            errors.append("legacy hash status observation mismatch")
        if legacy["hash_scope_version_observed"] != pinning["hash_scope_version"]:
            errors.append("legacy hash scope observation mismatch")
        if legacy["canonical_spec_hash_observed"] != pinning["canonical_spec_hash"]:
            errors.append("legacy canonical hash observation mismatch")

    vm_path = root / "research" / "variant_manifests" / f"VM-{spec_id[-4:]}.variant_manifest.json"
    if vm_path.is_file():
        vm = _load(vm_path)
        if vm["parent_strategy_spec"]["strategy_spec_hash"] != canonical_hash:
            errors.append("full canonical hash does not match VM parent binding")
    return errors


def _materialize_generic_root(tmp_path: Path) -> Path:
    target = tmp_path / "research" / "strategy_specs" / GENERIC_SPEC.name
    target.parent.mkdir(parents=True)
    shutil.copyfile(GENERIC_SPEC, target)
    return tmp_path


def test_schema_is_valid_draft7_and_closed() -> None:
    schema = _load(SCHEMA_PATH)
    Draft7Validator.check_schema(schema)
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert schema["additionalProperties"] is False


@pytest.mark.parametrize(
    ("name", "generic"),
    [
        ("STRAT-SPEC-0007.external_content_readiness.json", False),
        ("STRAT-SPEC-9000.external_content_readiness.json", True),
    ],
)
def test_valid_fixtures_pass_schema_and_semantics(
    name: str, generic: bool, tmp_path: Path
) -> None:
    fact = _load(VALID_ROOT / name)
    assert _schema_error_text(fact) == ""
    root = _materialize_generic_root(tmp_path) if generic else REPO_ROOT
    assert _semantic_errors(fact, root) == []


@pytest.mark.parametrize("case_path", sorted(INVALID_ROOT.glob("*.case.json")), ids=lambda p: p.stem)
def test_invalid_fixtures_fail_for_the_intended_reason(case_path: Path) -> None:
    case = _load(case_path)
    fact = copy.deepcopy(_load(VALID_ROOT / case["base"]))
    if case["operation"] == "set":
        _set_path(fact, case["path"], case["value"])
    elif case["operation"] == "set_many":
        for path, value in case["values"].items():
            _set_path(fact, path, value)
    elif case["operation"] == "delete":
        _delete_path(fact, case["path"])
    else:  # pragma: no cover - a malformed test case is itself a test failure
        raise AssertionError(f"unknown operation: {case['operation']}")
    errors = _schema_error_text(fact)
    if not errors:
        errors = "\n".join(_semantic_errors(fact, REPO_ROOT))
    assert case["expected_error"] in errors


def test_scope_canonicalization_and_readiness_are_exact_closed_constants() -> None:
    properties = _load(SCHEMA_PATH)["properties"]
    assert properties["scope"] == {"const": "h004_dispatch_external_content_readiness"}
    assert properties["readiness_state"] == {"const": "external_content_ready"}
    assert properties["content_binding"]["$ref"] == "#/definitions/content_binding"
    canonicalization = _load(SCHEMA_PATH)["definitions"]["content_binding"]["properties"][
        "canonicalization"
    ]
    assert canonicalization == {"const": "repo_canonical_json_v1"}


def test_legacy_unresolved_disclosure_is_mandatory_and_verification_is_impossible() -> None:
    legacy = _load(SCHEMA_PATH)["definitions"]["legacy_internal_hash"]
    assert "legacy_hash_scope_reproducibility" in legacy["required"]
    assert legacy["properties"]["legacy_hash_scope_reproducibility"] == {
        "const": "unresolved"
    }
    assert "legacy_internal_hash_verified" not in legacy["properties"]
    assert legacy["additionalProperties"] is False


def test_schema_cannot_claim_repo_wide_migration_or_authority() -> None:
    non_authority = _load(SCHEMA_PATH)["definitions"]["non_authority_declaration"]
    for field in (
        "not_repo_wide_hash_migration",
        "not_legacy_hash_reinterpretation",
        "not_dispatch_authority",
        "not_execution_authority",
        "not_ranking_authority",
        "not_readiness_beyond_content_integrity",
        "not_runtime_authority",
        "not_paper_live_authority",
        "not_oms_risk_reconciliation_authority",
    ):
        assert non_authority["properties"][field] == {"const": True}


def test_architecture_closes_h004_production_scope() -> None:
    architecture = ARCHITECTURE_PATH.read_text(encoding="utf-8")
    for required_text in (
        "current and only authorized production Strategy Spec under this decision is "
        "`STRAT-SPEC-0007`",
        "must reject an H-004-scoped production fact for any Strategy Spec not "
        "explicitly bound by the H-004 prerequisite chain",
        "The generic `STRAT-SPEC-9000` fixture tests schema and content-binding "
        "mechanics only",
        "It grants no production fact authority and is not an in-scope H-004 "
        "Strategy Spec",
        "at most one immutable fact for each explicitly in-scope H-004 Strategy Spec",
        "does not authorize a repository-wide production fact rollout",
    ):
        assert required_text in architecture
    assert "exactly one fact per Strategy Spec" not in architecture


def test_fact_contract_forbids_duplicate_superseding_and_source_mutation() -> None:
    definitions = _load(SCHEMA_PATH)["definitions"]
    assert definitions["immutability"]["properties"]["duplicate_fact_forbidden"] == {
        "const": True
    }
    assert definitions["immutability"]["properties"]["superseding_fact_forbidden"] == {
        "const": True
    }
    assert definitions["no_mutation_proof"]["properties"][
        "strategy_spec_bytes_unchanged"
    ] == {"const": True}


def test_strategy_spec_0007_reproduces_locked_raw_and_full_canonical_hashes() -> None:
    path = REPO_ROOT / "research" / "strategy_specs" / "STRAT-SPEC-0007.strategy_spec.json"
    raw = path.read_bytes()
    payload = json.loads(raw.decode("utf-8"))
    assert len(raw) == 19880
    assert _sha256(raw) == "sha256:b23ebc1093df51b7fab5e39c46fd2b96b5e71d35300134eb319a5cbc32d0857c"
    assert _sha256(canonical_json_bytes(payload)) == (
        "sha256:8b6f7dd7a3e12b934c1038ae113aa25aa79f0b3cc6a336b25bd58164f5cc92db"
    )
    assert payload["hash_pinning"]["hash_status"] == "not_computed"
    assert payload["hash_pinning"]["canonical_spec_hash"] is None


def test_all_strategy_specs_and_variant_manifests_remain_byte_identical() -> None:
    roots_and_hashes = (
        (REPO_ROOT / "research" / "strategy_specs", PRESERVED_STRATEGY_SPEC_HASHES),
        (REPO_ROOT / "research" / "variant_manifests", PRESERVED_VARIANT_MANIFEST_HASHES),
    )
    for root, expected in roots_and_hashes:
        actual = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in root.glob("*.json")}
        assert actual == expected


def test_all_full_canonical_strategy_spec_hashes_match_vm_parent_lineage() -> None:
    for index in range(1, 8):
        spec_path = REPO_ROOT / "research" / "strategy_specs" / f"STRAT-SPEC-{index:04d}.strategy_spec.json"
        vm_path = REPO_ROOT / "research" / "variant_manifests" / f"VM-{index:04d}.variant_manifest.json"
        spec = _load(spec_path)
        vm = _load(vm_path)
        assert vm["parent_strategy_spec"]["strategy_spec_id"] == spec["strategy_spec_id"]
        assert vm["parent_strategy_spec"]["strategy_spec_hash"] == _sha256(
            canonical_json_bytes(spec)
        )


def test_exactly_one_production_external_readiness_fact_exists_and_is_bound() -> None:
    facts = sorted(PRODUCTION_FACT_ROOT.glob("*.external_content_readiness.json"))
    assert [path.name for path in facts] == [
        "SS-ECR-STRAT-SPEC-0007.external_content_readiness.json"
    ]
    fact = _load(facts[0])
    assert _schema_error_text(fact) == ""
    assert _semantic_errors(fact, REPO_ROOT) == []
