import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

import tools.canon_intake.variant_planning_approval as writer
from tools.canon_intake.variant_planning_approval import (
    VariantPlanningApprovalError,
    VariantPlanningApprovalIntegrityCriticalError,
    contract_core_sha256,
    repo_canonical_json_v1,
    write_variant_planning_approval,
)


def _hash(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _write_json(path: Path, value: object) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(raw)
    return raw


def _write_approval(path: Path, approval: dict, *, resign: bool = False) -> bytes:
    if resign:
        approval["contract_core_sha256"] = contract_core_sha256(
            approval["variant_manifest_contract_core"]
        )
    return _write_json(path, approval)


def _authority_flags() -> dict:
    return {
        "authorizes_variant_manifest_preparation": True,
        "authorizes_one_manifest_only": True,
        "authorizes_strategy_spec_mutation": False,
        "authorizes_gate_c": False,
        "authorizes_gate_q": False,
        "authorizes_queue_admission": False,
        "authorizes_dispatch": False,
        "authorizes_research_execution": False,
        "authorizes_result_population": False,
        "authorizes_candidate_lifecycle": False,
        "authorizes_ranking": False,
        "authorizes_recommendation": False,
        "authorizes_promotion_readiness": False,
        "authorizes_scheduler_autonomy": False,
        "authorizes_notifications": False,
        "authorizes_runtime": False,
        "authorizes_paper_live": False,
        "authorizes_oms_risk_reconciliation": False,
    }


def _fixture(tmp_path: Path, source_repo: Path):
    root = tmp_path / "repo"
    schemas = root / "research/schemas"
    schemas.mkdir(parents=True)
    for name in (writer.APPROVAL_SCHEMA, writer.AUDIT_SCHEMA):
        shutil.copy2(source_repo / "research/schemas" / name, schemas / name)

    spec = {
        "schema_version": "v1",
        "strategy_spec_id": "STRAT-SPEC-9001",
        "status": "review_requested",
        "review": {"approval_scope": "none", "reviewer": None, "reviewed_at": None},
    }
    spec_path = root / "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json"
    spec_raw = _write_json(spec_path, spec)
    spec_hash = _hash(spec_raw)

    gate_record = {
        "schema_version": "gate_c_strategy_spec_write_audit_v1",
        "approval_id": "GATE-C-TEST-9001",
        "approved_by": "Karl",
        "strategy_spec_id": "STRAT-SPEC-9001",
        "canonical_target_path": "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json",
        "approved_content_sha256": spec_hash,
        "validation_outcome": "passed_before_write",
        "no_queue_candidate_runtime_outputs": True,
    }
    gate_raw = repo_canonical_json_v1(gate_record) + b"\n"
    gate_path = root / writer.GATE_C_AUDIT_PATH
    gate_path.parent.mkdir(parents=True)
    gate_path.write_bytes(gate_raw)

    core = {
        "strategy_spec_id": "STRAT-SPEC-9001",
        "strategy_spec_path": "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json",
        "strategy_spec_sha256": spec_hash,
        "variant_manifest_id": "VM-9001",
        "variant_manifest_path": "research/variant_manifests/VM-9001.variant_manifest.json",
        "search_family_id": "SF-TEST-PLANNING-1H-0001",
        "ordered_parameter_axes": [
            {"name": "fast_bars", "integer_values": [10, 20]},
            {"name": "threshold", "milli_values": [100, 200]},
        ],
        "population_cap": 4,
        "committed_population_count": 4,
        "denominator_basis": "committed_pre_registered_population_count",
        "adaptive_search": False,
        "post_hoc_mutation_forbidden": True,
        "authority": "one_bounded_variant_manifest_preparation_only",
    }
    approval = {
        "schema_version": "strategy_spec_variant_planning_approval_v1",
        "approval_id": "VPAPP-20260714-TEST0001",
        "approval_artifact_target_path": (
            "research/strategy_spec_variant_planning_approvals/"
            "VPAPP-20260714-TEST0001.variant_planning_approval.json"
        ),
        "approved_by": "Karl",
        "approved_at": "2026-07-14T12:00:00-05:00",
        "approval_scope": "one_bounded_variant_manifest_preparation",
        "exact_content_and_target_only": True,
        "append_only": True,
        "single_use_approval_id": True,
        "canonical_parent": {
            "strategy_spec_id": "STRAT-SPEC-9001",
            "path": "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json",
            "sha256": spec_hash,
            "embedded_status": "review_requested",
            "gate_c_audit": {
                "audit_path": writer.GATE_C_AUDIT_PATH,
                "line_number": 1,
                "raw_record_sha256": _hash(gate_raw),
                "gate_c_approval_id": "GATE-C-TEST-9001",
                "strategy_spec_id": "STRAT-SPEC-9001",
                "canonical_target_path": (
                    "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json"
                ),
            },
        },
        "variant_manifest_contract_core": core,
        "contract_core_sha256": contract_core_sha256(core),
        "contract_core_hash_scope": "variant_planning_contract_core_v1",
        "contract_core_canonicalization": "repo_canonical_json_v1",
        "amendment_revocation_policy": "supersede_with_new_approval_before_manifest_creation",
        "reuse_policy": "reject_all_identifier_path_and_search_family_reuse",
        "overwrite_forbidden": True,
        "authority_flags": _authority_flags(),
    }
    approval_path = root / "scratch/proposed.variant_planning_approval.json"
    approval_raw = _write_approval(approval_path, approval)
    return root, approval_path, approval, approval_raw, gate_path, spec_path


def _target(root: Path, approval: dict) -> Path:
    return root / approval["approval_artifact_target_path"]


def _audit(root: Path) -> Path:
    return root / writer.AUDIT_PATH


def _assert_no_crossing(root: Path, approval: dict) -> None:
    assert not _target(root, approval).exists()
    assert not _audit(root).exists()


def _distinct_approval(approval: dict, suffix: int = 2) -> dict:
    result = copy.deepcopy(approval)
    approval_id = f"VPAPP-20260714-TEST000{suffix}"
    vm_id = f"VM-900{suffix}"
    result["approval_id"] = approval_id
    result["approval_artifact_target_path"] = (
        "research/strategy_spec_variant_planning_approvals/"
        f"{approval_id}.variant_planning_approval.json"
    )
    core = result["variant_manifest_contract_core"]
    core["variant_manifest_id"] = vm_id
    core["variant_manifest_path"] = (
        f"research/variant_manifests/{vm_id}.variant_manifest.json"
    )
    core["search_family_id"] = f"SF-TEST-PLANNING-1H-000{suffix}"
    result["contract_core_sha256"] = contract_core_sha256(core)
    return result


@pytest.fixture
def repo_root():
    return Path(__file__).resolve().parents[1]


def test_schemas_are_closed_draft7_contracts(repo_root):
    for name in (writer.APPROVAL_SCHEMA, writer.AUDIT_SCHEMA):
        schema = json.loads((repo_root / "research/schemas" / name).read_text())
        Draft7Validator.check_schema(schema)

        def walk(value):
            if isinstance(value, dict):
                if value.get("type") == "object":
                    assert value.get("additionalProperties") is False
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(schema)


def test_valid_approval_writes_exact_bytes_and_one_canonical_lf_audit_line(
    tmp_path, repo_root
):
    root, approval_path, approval, approval_raw, _, _ = _fixture(tmp_path, repo_root)
    before = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    record = write_variant_planning_approval(
        repo_root=root, approval_path=approval_path
    )
    target = _target(root, approval)
    audit = _audit(root)
    after = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    assert target.read_bytes() == approval_raw
    assert record["approval_file_sha256"] == _hash(approval_raw)
    assert record["contract_core_sha256"] == contract_core_sha256(
        approval["variant_manifest_contract_core"]
    )
    assert audit.read_bytes() == repo_canonical_json_v1(record) + b"\n"
    assert after - before == {
        approval["approval_artifact_target_path"],
        writer.AUDIT_PATH.as_posix(),
    }
    assert not (root / writer.LOCK_PATH).exists()
    for forbidden in (
        "research/sweep_plans",
        "research/queue",
        "research/runs",
        "research/result_populations",
        "research/candidates",
        "src/runtime",
    ):
        assert not (root / forbidden).exists()


def test_cli_writes_only_synthetic_repository(tmp_path, repo_root):
    root, approval_path, approval, approval_raw, _, _ = _fixture(tmp_path, repo_root)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.canon_intake.variant_planning_approval",
            "--approval",
            str(approval_path),
            "--repo-root",
            str(root),
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["approval_id"] == approval["approval_id"]
    assert _target(root, approval).read_bytes() == approval_raw
    assert _audit(root).read_bytes().endswith(b"\n")


@pytest.mark.parametrize("kind", ["missing", "malformed", "non_object"])
def test_missing_or_malformed_approval_fails_without_write(
    tmp_path, repo_root, kind
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    if kind == "missing":
        approval_path.unlink()
    elif kind == "malformed":
        approval_path.write_bytes(b"not-json\n")
    else:
        approval_path.write_bytes(b"[]\n")
    with pytest.raises(VariantPlanningApprovalError):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _assert_no_crossing(root, approval)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.__setitem__("approved_by", "Not-Karl"),
        lambda value: value.__setitem__("approved_at", "2026-07-14T12:00:00"),
        lambda value: value.__setitem__("approval_scope", "queue_admission"),
        lambda value: value.__setitem__("exact_content_and_target_only", False),
        lambda value: value.__setitem__("append_only", False),
        lambda value: value.__setitem__("single_use_approval_id", False),
        lambda value: value.__setitem__("overwrite_forbidden", False),
        lambda value: value["authority_flags"].__setitem__(
            "authorizes_gate_q", True
        ),
        lambda value: value["authority_flags"].__setitem__(
            "authorizes_research_execution", True
        ),
        lambda value: value["authority_flags"].__setitem__(
            "authorizes_runtime", True
        ),
    ],
)
def test_wrong_actor_scope_timestamp_facts_or_broad_authority_fail_closed(
    tmp_path, repo_root, mutation
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    mutation(approval)
    _write_approval(approval_path, approval)
    with pytest.raises(VariantPlanningApprovalError):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _assert_no_crossing(root, approval)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.__setitem__("approval_id", "VPAPP-bad"),
        lambda value: value.__setitem__(
            "approval_artifact_target_path",
            "research/strategy_spec_variant_planning_approvals/"
            "VPAPP-20260714-TEST0009.variant_planning_approval.json",
        ),
        lambda value: value["canonical_parent"].__setitem__(
            "path", "../STRAT-SPEC-9001.strategy_spec.json"
        ),
        lambda value: value["canonical_parent"].__setitem__(
            "strategy_spec_id", "STRAT-SPEC-9002"
        ),
    ],
)
def test_malformed_identifier_path_binding_or_traversal_fails_closed(
    tmp_path, repo_root, mutation
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    mutation(approval)
    _write_approval(approval_path, approval)
    with pytest.raises(VariantPlanningApprovalError):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    assert not _audit(root).exists()


def test_parent_hash_file_status_and_core_binding_fail_closed(tmp_path, repo_root):
    cases = []
    for kind in ("hash", "file", "status", "core"):
        case_root = tmp_path / kind
        root, approval_path, approval, _, _, spec_path = _fixture(case_root, repo_root)
        if kind == "hash":
            approval["canonical_parent"]["sha256"] = "sha256:" + "0" * 64
        elif kind == "file":
            with spec_path.open("ab") as handle:
                handle.write(b"tamper")
        elif kind == "status":
            spec = json.loads(spec_path.read_text())
            spec["status"] = "approved_for_variant_planning"
            _write_json(spec_path, spec)
        else:
            approval["variant_manifest_contract_core"]["strategy_spec_sha256"] = (
                "sha256:" + "1" * 64
            )
            _write_approval(approval_path, approval, resign=True)
        if kind != "core":
            _write_approval(approval_path, approval)
        cases.append((root, approval_path, approval))
    for root, approval_path, approval in cases:
        with pytest.raises(VariantPlanningApprovalError):
            write_variant_planning_approval(repo_root=root, approval_path=approval_path)
        _assert_no_crossing(root, approval)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda ref: ref.__setitem__("raw_record_sha256", "sha256:" + "0" * 64),
        lambda ref: ref.__setitem__("line_number", 2),
        lambda ref: ref.__setitem__("gate_c_approval_id", "GATE-C-WRONG"),
        lambda ref: ref.__setitem__("strategy_spec_id", "STRAT-SPEC-9002"),
        lambda ref: ref.__setitem__(
            "canonical_target_path",
            "research/strategy_specs/STRAT-SPEC-9002.strategy_spec.json",
        ),
    ],
)
def test_wrong_gate_c_line_hash_approval_spec_or_target_fails_closed(
    tmp_path, repo_root, mutation
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    mutation(approval["canonical_parent"]["gate_c_audit"])
    _write_approval(approval_path, approval)
    with pytest.raises(VariantPlanningApprovalError):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _assert_no_crossing(root, approval)


@pytest.mark.parametrize("kind", ["duplicate", "malformed_later", "wrong_content", "no_lf"])
def test_gate_c_history_is_complete_unique_and_lf_bound(
    tmp_path, repo_root, kind
):
    root, approval_path, approval, _, gate_path, _ = _fixture(tmp_path, repo_root)
    first = gate_path.read_bytes()
    if kind == "duplicate":
        gate_path.write_bytes(first + first)
    elif kind == "malformed_later":
        gate_path.write_bytes(first + b"not-json\n")
    elif kind == "no_lf":
        raw = first.rstrip(b"\n")
        gate_path.write_bytes(raw)
        approval["canonical_parent"]["gate_c_audit"]["raw_record_sha256"] = _hash(raw)
    else:
        record = json.loads(first)
        record["approval_id"] = "GATE-C-SUBSTITUTE"
        raw = repo_canonical_json_v1(record) + b"\n"
        gate_path.write_bytes(raw)
        approval["canonical_parent"]["gate_c_audit"]["raw_record_sha256"] = _hash(raw)
    _write_approval(approval_path, approval)
    with pytest.raises(VariantPlanningApprovalError):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _assert_no_crossing(root, approval)


def test_float_anywhere_in_canonical_surface_is_rejected(tmp_path, repo_root):
    with pytest.raises(VariantPlanningApprovalError, match="floating-point"):
        contract_core_sha256({"nested": [1, {"float": 1.0}]})
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    approval["variant_manifest_contract_core"]["ordered_parameter_axes"][0][
        "integer_values"
    ][0] = 1.5
    _write_approval(approval_path, approval)
    with pytest.raises(VariantPlanningApprovalError, match="floating-point"):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _assert_no_crossing(root, approval)


def test_float_bearing_referenced_spec_and_vm_corpus_remain_readable(
    tmp_path, repo_root
):
    root, approval_path, approval, _, _, spec_path = _fixture(tmp_path, repo_root)
    spec = json.loads(spec_path.read_text())
    spec["schema_approved_numeric_reference"] = 1.25
    spec_raw = _write_json(spec_path, spec)
    spec_hash = _hash(spec_raw)
    approval["canonical_parent"]["sha256"] = spec_hash
    core = approval["variant_manifest_contract_core"]
    core["strategy_spec_sha256"] = spec_hash
    gate_path = root / writer.GATE_C_AUDIT_PATH
    gate_record = json.loads(gate_path.read_text())
    gate_record["approved_content_sha256"] = spec_hash
    gate_raw = repo_canonical_json_v1(gate_record) + b"\n"
    gate_path.write_bytes(gate_raw)
    approval["canonical_parent"]["gate_c_audit"]["raw_record_sha256"] = _hash(
        gate_raw
    )
    _write_json(
        root / "research/variant_manifests/VM-9998.variant_manifest.json",
        {
            "variant_manifest_id": "VM-9998",
            "schema_approved_numeric_reference": 0.5,
            "population_governance": {
                "multiple_testing_accounting": {
                    "search_family_id": "SF-OTHER-FLOAT-FAMILY-1H-0001"
                }
            },
        },
    )
    _write_approval(approval_path, approval, resign=True)
    write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    assert _target(root, approval).exists()


@pytest.mark.parametrize(
    "mutation",
    [
        lambda core: core["ordered_parameter_axes"].reverse(),
        lambda core: core["ordered_parameter_axes"][0].__setitem__(
            "name", "renamed_axis"
        ),
        lambda core: core["ordered_parameter_axes"][0]["integer_values"].append(30),
        lambda core: core.__setitem__("committed_population_count", 5),
        lambda core: core.__setitem__("denominator_basis", "executed_only"),
        lambda core: core.__setitem__("search_family_id", "SF-TEST-PLANNING-1H-0002"),
    ],
)
def test_changed_axis_order_name_values_population_denominator_or_family_breaks_hash(
    tmp_path, repo_root, mutation
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    mutation(approval["variant_manifest_contract_core"])
    _write_approval(approval_path, approval)
    with pytest.raises(VariantPlanningApprovalError):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _assert_no_crossing(root, approval)


@pytest.mark.parametrize("kind", ["wrong_hash", "duplicate_axis", "population", "cap"])
def test_core_hash_and_derived_population_semantics_fail_closed(
    tmp_path, repo_root, kind
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    core = approval["variant_manifest_contract_core"]
    if kind == "wrong_hash":
        approval["contract_core_sha256"] = "sha256:" + "f" * 64
        _write_approval(approval_path, approval)
    elif kind == "duplicate_axis":
        core["ordered_parameter_axes"][1]["name"] = "fast_bars"
        _write_approval(approval_path, approval, resign=True)
    elif kind == "population":
        core["committed_population_count"] = 5
        core["population_cap"] = 5
        _write_approval(approval_path, approval, resign=True)
    else:
        core["population_cap"] = 3
        _write_approval(approval_path, approval, resign=True)
    with pytest.raises(VariantPlanningApprovalError):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _assert_no_crossing(root, approval)


def test_symlinked_input_parent_and_authoritative_directory_fail_closed(
    tmp_path, repo_root, monkeypatch
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path / "input", repo_root)
    original_is_symlink = Path.is_symlink
    simulated = approval_path

    def is_simulated_symlink(self):
        return self == simulated or original_is_symlink(self)

    monkeypatch.setattr(Path, "is_symlink", is_simulated_symlink)
    with pytest.raises(VariantPlanningApprovalError, match="symlink"):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _assert_no_crossing(root, approval)
    monkeypatch.undo()

    root, approval_path, approval, _, _, _ = _fixture(tmp_path / "parent", repo_root)
    specs = root / "research/strategy_specs"
    original_is_symlink = Path.is_symlink
    simulated = specs

    def is_simulated_symlink(self):
        return self == simulated or original_is_symlink(self)

    monkeypatch.setattr(Path, "is_symlink", is_simulated_symlink)
    with pytest.raises(VariantPlanningApprovalError, match="symlink"):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _assert_no_crossing(root, approval)
    monkeypatch.undo()

    root, approval_path, approval, _, _, _ = _fixture(tmp_path / "target", repo_root)
    approval_root = root / writer.APPROVAL_ROOT
    approval_root.parent.mkdir(parents=True, exist_ok=True)
    approval_root.mkdir()
    original_is_symlink = Path.is_symlink
    simulated = approval_root

    def is_simulated_symlink(self):
        return self == simulated or original_is_symlink(self)

    monkeypatch.setattr(Path, "is_symlink", is_simulated_symlink)
    with pytest.raises(VariantPlanningApprovalError, match="symlink"):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _assert_no_crossing(root, approval)


def test_broken_symlink_component_is_rejected_without_exists_guard(
    tmp_path, monkeypatch
):
    simulated = tmp_path / "broken-link"
    original_is_symlink = Path.is_symlink

    def is_simulated_symlink(self):
        return self == simulated or original_is_symlink(self)

    monkeypatch.setattr(Path, "is_symlink", is_simulated_symlink)
    assert not simulated.exists()
    with pytest.raises(VariantPlanningApprovalError, match="symlink"):
        writer._reject_symlink_components(simulated / "child", "simulated path")


def test_existing_target_and_exact_duplicate_submission_reject(tmp_path, repo_root):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path / "existing", repo_root)
    target = _target(root, approval)
    target.parent.mkdir(parents=True)
    target.write_bytes(b"preexisting")
    with pytest.raises(VariantPlanningApprovalError, match="already exists"):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    assert target.read_bytes() == b"preexisting"
    assert not _audit(root).exists()

    root, approval_path, approval, _, _, _ = _fixture(tmp_path / "duplicate", repo_root)
    write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    audit_before = _audit(root).read_bytes()
    target_before = _target(root, approval).read_bytes()
    with pytest.raises(VariantPlanningApprovalError, match="duplicate submission"):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    assert _audit(root).read_bytes() == audit_before
    assert _target(root, approval).read_bytes() == target_before


@pytest.mark.parametrize("collision", ["variant_manifest_id", "search_family_id"])
def test_vm_corpus_reserves_vm_identity_path_and_search_family(
    tmp_path, repo_root, collision
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    core = approval["variant_manifest_contract_core"]
    vm_id = core["variant_manifest_id"] if collision == "variant_manifest_id" else "VM-9998"
    family = (
        core["search_family_id"]
        if collision == "search_family_id"
        else "SF-OTHER-FAMILY-1H-0001"
    )
    _write_json(
        root / f"research/variant_manifests/{vm_id}.variant_manifest.json",
        {
            "variant_manifest_id": vm_id,
            "population_governance": {
                "multiple_testing_accounting": {"search_family_id": family}
            },
        },
    )
    with pytest.raises(VariantPlanningApprovalError, match="already reserves"):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _assert_no_crossing(root, approval)


@pytest.mark.parametrize("collision", ["variant_manifest_id", "search_family_id"])
def test_approval_corpus_reserves_vm_identity_path_and_search_family(
    tmp_path, repo_root, collision
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    existing = _distinct_approval(approval, 2)
    if collision == "variant_manifest_id":
        existing_core = existing["variant_manifest_contract_core"]
        candidate_core = approval["variant_manifest_contract_core"]
        existing_core["variant_manifest_id"] = candidate_core["variant_manifest_id"]
        existing_core["variant_manifest_path"] = candidate_core["variant_manifest_path"]
    else:
        existing["variant_manifest_contract_core"]["search_family_id"] = approval[
            "variant_manifest_contract_core"
        ]["search_family_id"]
    existing["contract_core_sha256"] = contract_core_sha256(
        existing["variant_manifest_contract_core"]
    )
    existing_path = root / "scratch/existing-approval.json"
    _write_approval(existing_path, existing)
    write_variant_planning_approval(repo_root=root, approval_path=existing_path)
    audit_before = _audit(root).read_bytes()
    with pytest.raises(VariantPlanningApprovalError, match="reserves"):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    assert _audit(root).read_bytes() == audit_before
    assert not _target(root, approval).exists()
    assert _target(root, existing).exists()


@pytest.mark.parametrize("collision", ["variant_manifest_id", "search_family_id"])
def test_historical_audit_permanently_reserves_vm_and_search_family(
    tmp_path, repo_root, collision
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    second = _distinct_approval(approval, 2)
    if collision == "variant_manifest_id":
        second_core = second["variant_manifest_contract_core"]
        first_core = approval["variant_manifest_contract_core"]
        second_core["variant_manifest_id"] = first_core["variant_manifest_id"]
        second_core["variant_manifest_path"] = first_core["variant_manifest_path"]
    else:
        second["variant_manifest_contract_core"]["search_family_id"] = approval[
            "variant_manifest_contract_core"
        ]["search_family_id"]
    second_path = root / "scratch/second-approval.json"
    _write_approval(second_path, second, resign=True)
    audit_before = _audit(root).read_bytes()
    with pytest.raises(VariantPlanningApprovalError, match="permanently reserves"):
        write_variant_planning_approval(repo_root=root, approval_path=second_path)
    assert _audit(root).read_bytes() == audit_before
    assert not _target(root, second).exists()


@pytest.mark.parametrize("kind", ["malformed", "partial", "duplicate", "tampered_evidence"])
def test_complete_historical_replay_fails_closed(tmp_path, repo_root, kind):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    if kind in {"malformed", "partial"}:
        audit = _audit(root)
        audit.parent.mkdir(parents=True)
        audit.write_bytes(b"not-json\n" if kind == "malformed" else b"{}")
    else:
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
        audit = _audit(root)
        if kind == "duplicate":
            audit.write_bytes(audit.read_bytes() + audit.read_bytes())
        else:
            historical = json.loads(_target(root, approval).read_text())
            historical["approved_at"] = "2026-07-14T12:01:00-05:00"
            _write_approval(_target(root, approval), historical)
    second = _distinct_approval(approval, 2)
    second_path = root / "scratch/second-approval.json"
    _write_approval(second_path, second, resign=True)
    before = audit.read_bytes()
    with pytest.raises(VariantPlanningApprovalError):
        write_variant_planning_approval(repo_root=root, approval_path=second_path)
    assert audit.read_bytes() == before
    assert not _target(root, second).exists()


def test_valid_historical_replay_preserves_prior_line_and_allows_distinct_write(
    tmp_path, repo_root
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    first_record = write_variant_planning_approval(
        repo_root=root, approval_path=approval_path
    )
    first_line = _audit(root).read_bytes()
    second = _distinct_approval(approval, 2)
    second_path = root / "scratch/second-approval.json"
    _write_approval(second_path, second, resign=True)
    second_record = write_variant_planning_approval(
        repo_root=root, approval_path=second_path
    )
    lines = _audit(root).read_bytes().splitlines(keepends=True)
    assert len(lines) == 2
    assert lines[0] == first_line
    assert json.loads(lines[0]) == first_record
    assert lines[1] == repo_canonical_json_v1(second_record) + b"\n"
    assert _target(root, approval).exists()
    assert _target(root, second).exists()


def test_missing_historical_approval_evidence_blocks_later_write(tmp_path, repo_root):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _target(root, approval).unlink()
    second = _distinct_approval(approval, 2)
    second_path = root / "scratch/second-approval.json"
    _write_approval(second_path, second, resign=True)
    audit_before = _audit(root).read_bytes()
    with pytest.raises(VariantPlanningApprovalError, match="historical approval"):
        write_variant_planning_approval(repo_root=root, approval_path=second_path)
    assert _audit(root).read_bytes() == audit_before
    assert not _target(root, second).exists()


def test_orphan_approval_without_audit_blocks_later_write(tmp_path, repo_root):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    orphan = _distinct_approval(approval, 2)
    _write_approval(root / orphan["approval_artifact_target_path"], orphan)
    with pytest.raises(VariantPlanningApprovalError, match="corpus and audit history disagree"):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _assert_no_crossing(root, approval)


def test_noncanonical_historical_audit_line_blocks_later_write(tmp_path, repo_root):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    first_record = write_variant_planning_approval(
        repo_root=root, approval_path=approval_path
    )
    audit = _audit(root)
    noncanonical = json.dumps(first_record, sort_keys=True).encode("utf-8") + b"\n"
    assert noncanonical != repo_canonical_json_v1(first_record) + b"\n"
    audit.write_bytes(noncanonical)
    second = _distinct_approval(approval, 2)
    second_path = root / "scratch/second-approval.json"
    _write_approval(second_path, second, resign=True)
    with pytest.raises(VariantPlanningApprovalError, match="not canonical JSON"):
        write_variant_planning_approval(repo_root=root, approval_path=second_path)
    assert audit.read_bytes() == noncanonical
    assert not _target(root, second).exists()


def test_existing_lock_fails_closed_and_is_not_removed(tmp_path, repo_root):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    lock = root / writer.LOCK_PATH
    lock.parent.mkdir(parents=True)
    lock.write_text("stale-or-active\n")
    with pytest.raises(VariantPlanningApprovalError, match="stale locks"):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    assert lock.exists()
    _assert_no_crossing(root, approval)


def test_in_lock_revalidation_rejects_changed_reviewed_input(
    tmp_path, repo_root, monkeypatch
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    original_lock = writer._crossing_lock

    @contextmanager
    def mutating_lock(lock_root):
        with original_lock(lock_root) as state:
            approval_path.write_bytes(b"{}\n")
            yield state

    monkeypatch.setattr(writer, "_crossing_lock", mutating_lock)
    with pytest.raises(VariantPlanningApprovalError):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _assert_no_crossing(root, approval)


def test_concurrent_target_creation_never_appends_audit(
    tmp_path, repo_root, monkeypatch
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    target = _target(root, approval)
    original_open = Path.open

    def collide(self, mode="r", *args, **kwargs):
        if self == target and mode == "xb":
            self.write_bytes(b"concurrent-owner")
            raise FileExistsError("simulated concurrent create")
        return original_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", collide)
    with pytest.raises(VariantPlanningApprovalError, match="rolled back"):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    assert target.read_bytes() == b"concurrent-owner"
    assert not _audit(root).exists()


def test_audit_open_failure_rolls_back_new_approval(tmp_path, repo_root, monkeypatch):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    monkeypatch.setattr(
        writer,
        "_open_audit",
        lambda path: (_ for _ in ()).throw(OSError("audit open denied")),
    )
    with pytest.raises(VariantPlanningApprovalError, match="rolled back"):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _assert_no_crossing(root, approval)


class _AuditFailure:
    def __init__(self, handle, *, fail_write=False, fail_flush=False, fail_rollback=False):
        self.handle = handle
        self.fail_write = fail_write
        self.fail_flush = fail_flush
        self.fail_rollback = fail_rollback
        self.seeks = 0
        self.flushes = 0

    def __getattr__(self, name):
        return getattr(self.handle, name)

    def seek(self, *args):
        self.seeks += 1
        if self.fail_rollback and self.seeks > 1:
            raise ValueError("rollback seek denied")
        return self.handle.seek(*args)

    def write(self, data):
        if self.fail_write:
            amount = max(1, len(data) // 2)
            self.handle.write(data[:amount])
            return amount
        return self.handle.write(data)

    def flush(self):
        self.flushes += 1
        if self.fail_flush and self.flushes == 1:
            raise OSError("audit flush denied")
        return self.handle.flush()


@pytest.mark.parametrize("kind", ["write", "flush", "rollback"])
def test_audit_write_flush_and_rollback_failures_are_fail_closed(
    tmp_path, repo_root, monkeypatch, kind
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    audit = _audit(root)
    audit.parent.mkdir(parents=True)
    original = b""
    audit.write_bytes(original)

    def open_failure(path):
        return (
            _AuditFailure(
                path.open("r+b"),
                fail_write=kind in {"write", "rollback"},
                fail_flush=kind == "flush",
                fail_rollback=kind == "rollback",
            ),
            False,
        )

    monkeypatch.setattr(writer, "_open_audit", open_failure)
    expected = (
        VariantPlanningApprovalIntegrityCriticalError
        if kind == "rollback"
        else VariantPlanningApprovalError
    )
    with pytest.raises(expected, match="rollback failed|rolled back"):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    assert not _target(root, approval).exists()
    if kind != "rollback":
        assert audit.read_bytes() == original


class _TargetFailure:
    def __init__(self, handle, kind):
        self.handle = handle
        self.kind = kind

    def __getattr__(self, name):
        return getattr(self.handle, name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.handle.close()

    def write(self, data):
        if self.kind == "write":
            amount = max(1, len(data) // 2)
            self.handle.write(data[:amount])
            return amount
        return self.handle.write(data)

    def flush(self):
        if self.kind == "flush":
            raise OSError("approval flush denied")
        return self.handle.flush()


@pytest.mark.parametrize("kind", ["write", "flush", "fsync"])
def test_approval_write_flush_and_fsync_failures_roll_back(
    tmp_path, repo_root, monkeypatch, kind
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    target = _target(root, approval)
    original_open = Path.open
    original_fsync = os.fsync
    fsync_calls = 0

    def failing_open(self, mode="r", *args, **kwargs):
        handle = original_open(self, mode, *args, **kwargs)
        if self == target and mode == "xb" and kind in {"write", "flush"}:
            return _TargetFailure(handle, kind)
        return handle

    def failing_fsync(fd):
        nonlocal fsync_calls
        fsync_calls += 1
        if kind == "fsync" and fsync_calls == 2:
            raise OSError("approval fsync denied")
        return original_fsync(fd)

    monkeypatch.setattr(Path, "open", failing_open)
    monkeypatch.setattr(os, "fsync", failing_fsync)
    with pytest.raises(VariantPlanningApprovalError, match="rolled back"):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    _assert_no_crossing(root, approval)


def test_approval_rollback_failure_is_integrity_critical(
    tmp_path, repo_root, monkeypatch
):
    root, approval_path, approval, _, _, _ = _fixture(tmp_path, repo_root)
    target = _target(root, approval)
    original_unlink = Path.unlink
    monkeypatch.setattr(
        writer,
        "_open_audit",
        lambda path: (_ for _ in ()).throw(OSError("audit denied")),
    )

    def fail_target_rollback(self, *args, **kwargs):
        if self == target:
            raise OSError("approval rollback denied")
        return original_unlink(self, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fail_target_rollback)
    with pytest.raises(
        VariantPlanningApprovalIntegrityCriticalError,
        match="approval rollback failed.*automatic retry is forbidden",
    ):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    assert target.exists()
    assert not _audit(root).exists()


def test_post_commit_lock_cleanup_failure_preserves_commit_and_forbids_retry(
    tmp_path, repo_root, monkeypatch
):
    root, approval_path, approval, approval_raw, _, _ = _fixture(tmp_path, repo_root)
    lock = root / writer.LOCK_PATH
    original_unlink = Path.unlink

    def fail_lock_cleanup(self, *args, **kwargs):
        if self == lock:
            raise OSError("lock cleanup denied")
        return original_unlink(self, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fail_lock_cleanup)
    with pytest.raises(
        VariantPlanningApprovalIntegrityCriticalError,
        match="commit occurred.*automatic retry is forbidden.*operator inspection",
    ):
        write_variant_planning_approval(repo_root=root, approval_path=approval_path)
    assert _target(root, approval).read_bytes() == approval_raw
    lines = _audit(root).read_bytes().splitlines(keepends=True)
    assert len(lines) == 1 and lines[0].endswith(b"\n")
    assert lock.exists()
