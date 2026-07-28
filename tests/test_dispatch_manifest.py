import copy
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from tests import test_dispatch_authorization as authorization_support
from tools.canon_intake import dispatch_manifest as manifest_contract
from tools.canon_intake.dispatch_authorization import (
    DispatchAuthorizationError,
    serialize_dispatch_authorization,
    validate_dispatch_authorization,
    validate_dispatch_record_for_authorization,
)
from tools.canon_intake.dispatch_manifest import (
    DERIVATION_VERSION,
    DISPATCH_IMMUTABLE_POSTURE,
    DISPATCH_NON_AUTHORITY,
    DispatchManifestError,
    derive_dispatch_record,
    serialize_dispatch_manifest,
    validate_dispatch_manifest,
    write_dispatch_manifest,
)


def _hash(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _remove_readonly(function, path, exc_info):
    del exc_info
    os.chmod(path, 0o700)
    function(path)


@pytest.fixture
def source_repo() -> Path:
    return Path(__file__).resolve().parents[1]


def _fixture(tmp_path: Path, source_repo: Path, *, committed: bool) -> dict:
    fixture = authorization_support._fixture(
        tmp_path,
        source_repo,
        reservation_state="committed" if committed else "none",
    )
    shutil.copy2(
        source_repo / "research/schemas/canon_dispatch_record.schema.json",
        fixture["root"]
        / "research/schemas/canon_dispatch_record.schema.json",
    )
    return fixture


def _independent_expected_dispatch(fixture: dict) -> dict:
    manifest = fixture["manifest"]
    authorization = fixture["authorization"]
    authorization_raw = fixture["authorization_raw"]
    crossing = manifest["crossing_identities"]
    queue = manifest["queue_binding"]
    gate = queue["gate_q"]
    dataset = manifest["dataset"]
    return {
        "schema_version": "canon_dispatch_record_v1",
        "dispatch_id": crossing["dispatch_id"],
        "dispatch_record_path": crossing["dispatch_record_path"],
        "created_at": manifest["dispatch_created_at"],
        "dispatch_state": "dispatched",
        "manifest_derivation": {
            "manifest_id": manifest["manifest_id"],
            "manifest_path": manifest["manifest_target_path"],
            "manifest_whole_file_sha256": _hash(fixture["manifest_raw"]),
            "manifest_byte_length": len(fixture["manifest_raw"]),
            "manifest_canonicalization": "repo_canonical_json_v1",
            "dispatch_derivation_version": DERIVATION_VERSION,
        },
        "queue_binding": {
            "queue_item_id": queue["queue_item_id"],
            "path": queue["path"],
            "raw_sha256": queue["whole_file_sha256"],
            "admission_status": queue["required_state"],
        },
        "gate_q_binding": {
            "approval_id": gate["approval_id"],
            "path": gate["path"],
            "file_sha256": gate["whole_file_sha256"],
            "approval_core_sha256": gate["core_sha256"],
            "approval_core_hash_scope": gate["core_hash_scope"],
            "approval_core_canonicalization": gate[
                "core_canonicalization"
            ],
        },
        "dispatch_authorization": {
            "authorization_id": authorization["authorization_id"],
            "source_path": authorization[
                "authorization_artifact_target_path"
            ],
            "source_sha256": _hash(authorization_raw),
            "source_byte_length": len(authorization_raw),
            "authorization_core_sha256": authorization[
                "authorization_core_sha256"
            ],
            "authorization_core_hash_scope": (
                "dispatch_authorization_core_v1"
            ),
            "authorization_core_canonicalization": (
                "repo_canonical_json_v1"
            ),
            "authorized_by": authorization["approved_by"],
            "authorized_at": authorization["approved_at"],
            "authorization_scope": authorization["authorization_scope"],
            "authorized_queue_item_id": queue["queue_item_id"],
            "authorized_dispatch_id": crossing["dispatch_id"],
            "authorized_run_id": crossing["run_id"],
            "exact_content_and_target_only": True,
            "content_bound_freshness": True,
            "single_use_authorization_id": True,
            "no_downstream_authority": True,
        },
        "run_binding": {
            "run_id": crossing["run_id"],
            "execution_event_stream_path": crossing[
                "execution_event_stream_path"
            ],
        },
        "runner_binding": {
            field: manifest["runner"][field]
            for field in (
                "invocation_kind",
                "module",
                "source_path",
                "version",
                "source_sha256",
            )
        },
        "artifact_bindings": {
            field: {
                "artifact_id": manifest["lineage"][field]["artifact_id"],
                "path": manifest["lineage"][field]["path"],
                "sha256": manifest["lineage"][field][
                    "whole_file_sha256"
                ],
            }
            for field in ("strategy_spec", "variant_manifest", "sweep_plan")
        },
        "dataset_binding": {
            "dataset_id": dataset["dataset_id"],
            "snapshot_version": dataset["snapshot_version"],
            "path": dataset["data_path"],
            "sha256": dataset["data_sha256"],
            "market": dataset["market"],
            "timeframe": dataset["timeframe"],
            "unresolved_policy": "reject",
        },
        "denominator": copy.deepcopy(manifest["denominator"]),
        "budget": copy.deepcopy(manifest["budget"]),
        "execution_parameters": copy.deepcopy(
            manifest["execution_parameters"]
        ),
        "output_targets": {
            "scratch_run_directory": manifest["output_targets"][
                "scratch_run_directory"
            ],
            "provisional_result_paths": copy.deepcopy(
                manifest["output_targets"]["provisional_result_paths"]
            ),
            "execution_event_stream_path": manifest["output_targets"][
                "execution_event_stream_path"
            ],
        },
        "immutable_posture": copy.deepcopy(DISPATCH_IMMUTABLE_POSTURE),
        "non_authority_declaration": copy.deepcopy(DISPATCH_NON_AUTHORITY),
    }


def _write_dispatch(fixture: dict, dispatch: dict) -> Path:
    target = fixture["root"] / dispatch["dispatch_record_path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(serialize_dispatch_authorization(dispatch))
    return target


def test_manifest_kdauth_and_independently_derived_dispatch_validate(
    tmp_path, source_repo
):
    fixture = _fixture(tmp_path, source_repo, committed=True)
    manifest_validation = validate_dispatch_manifest(
        repo_root=fixture["root"],
        manifest_path=fixture["manifest_path"],
    )
    authorization_validation = validate_dispatch_authorization(
        repo_root=fixture["root"],
        authorization_path=fixture["authorization_path"],
    )
    derived = derive_dispatch_record(
        manifest=fixture["manifest"],
        manifest_raw=fixture["manifest_raw"],
        authorization=fixture["authorization"],
        authorization_raw=fixture["authorization_raw"],
    )
    assert derived == _independent_expected_dispatch(fixture)
    assert (
        serialize_dispatch_authorization(derived)
        == serialize_dispatch_authorization(
            _independent_expected_dispatch(fixture)
        )
    )
    target = _write_dispatch(fixture, derived)
    result = validate_dispatch_record_for_authorization(
        repo_root=fixture["root"],
        dispatch_path=target,
    )
    assert manifest_validation["whole_file_sha256"] == _hash(
        fixture["manifest_raw"]
    )
    assert authorization_validation["lifecycle_state"] == "created"
    assert result["dispatch_file_sha256"] == _hash(target.read_bytes())


def test_manifest_writer_exclusive_creates_exact_reviewed_bytes(
    tmp_path, source_repo
):
    fixture = _fixture(tmp_path, source_repo, committed=False)
    proposal = fixture["root"] / "review/dispatch_manifest.review.json"
    proposal.parent.mkdir(parents=True)
    proposal.write_bytes(fixture["manifest_raw"])
    fixture["manifest_path"].unlink()
    shutil.rmtree(
        fixture["root"] / ".git", onerror=_remove_readonly
    )
    subprocess.run(
        ["git", "init", "-q"], cwd=fixture["root"], check=True
    )
    subprocess.run(
        [
            "git",
            "add",
            ".",
        ],
        cwd=fixture["root"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-m",
            "synthetic manifest dependencies",
        ],
        cwd=fixture["root"],
        check=True,
        capture_output=True,
    )
    lock = fixture["root"] / manifest_contract.LOCK_PATH
    lock.write_bytes(b"active crossing\n")
    with pytest.raises(DispatchManifestError, match="lock exists"):
        write_dispatch_manifest(
            repo_root=fixture["root"],
            proposal_path=proposal,
            reviewed_whole_file_sha256=_hash(fixture["manifest_raw"]),
        )
    assert lock.read_bytes() == b"active crossing\n"
    lock.unlink()
    result = write_dispatch_manifest(
        repo_root=fixture["root"],
        proposal_path=proposal,
        reviewed_whole_file_sha256=_hash(fixture["manifest_raw"]),
    )
    assert result["manifest_created"] is True
    assert fixture["manifest_path"].read_bytes() == fixture["manifest_raw"]
    with pytest.raises(DispatchManifestError):
        write_dispatch_manifest(
            repo_root=fixture["root"],
            proposal_path=proposal,
            reviewed_whole_file_sha256=_hash(fixture["manifest_raw"]),
        )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.__setitem__("manifest_purpose", "other"),
        lambda value: value.__setitem__("self_sha256", "sha256:" + "0" * 64),
        lambda value: value.__setitem__(
            "future_kdauth",
            {
                "authorization_id": "KDAUTH-H004-R2-9001",
                "whole_file_sha256": "sha256:" + "1" * 64,
            },
        ),
        lambda value: value["output_targets"].__setitem__(
            "provisional_result_pattern", "scratch/FIXTURE-RUN/*.json"
        ),
        lambda value: value["output_targets"].__setitem__(
            "scratch_run_directory",
            value["output_targets"]["scratch_output_root"],
        ),
        lambda value: value["output_targets"].__setitem__(
            "provisional_result_paths",
            [
                value["output_targets"]["provisional_result_paths"][0],
                value["output_targets"]["provisional_result_paths"][0],
            ],
        ),
        lambda value: value.__setitem__(
            "dispatch_derivation_version", "unknown"
        ),
        lambda value: value.pop("budget"),
    ],
)
def test_manifest_rejects_unknown_circular_ambiguous_and_missing_content(
    tmp_path, source_repo, mutation
):
    fixture = _fixture(tmp_path, source_repo, committed=False)
    candidate = copy.deepcopy(fixture["manifest"])
    mutation(candidate)
    candidate_path = fixture["root"] / "review/candidate.json"
    candidate_path.parent.mkdir(parents=True)
    candidate_path.write_bytes(serialize_dispatch_manifest(candidate))
    with pytest.raises(DispatchManifestError):
        validate_dispatch_manifest(
            repo_root=fixture["root"],
            manifest_path=candidate_path,
            require_authoritative_path=False,
        )


def test_manifest_substitution_and_byte_drift_after_kdauth_fail(
    tmp_path, source_repo
):
    fixture = _fixture(tmp_path, source_repo, committed=False)
    changed = copy.deepcopy(fixture["manifest"])
    changed["dispatch_created_at"] = "2026-07-20T19:00:00Z"
    fixture["manifest_path"].write_bytes(
        serialize_dispatch_manifest(changed)
    )
    with pytest.raises(
        DispatchAuthorizationError, match="hash mismatch"
    ):
        validate_dispatch_authorization(
            repo_root=fixture["root"],
            authorization_path=fixture["authorization_path"],
            require_audit=False,
            scan_history=False,
        )


@pytest.mark.parametrize("kind", ["missing", "extra", "bad_hash"])
def test_kdauth_manifest_reference_is_exact_and_closed(
    tmp_path, source_repo, kind
):
    fixture = _fixture(tmp_path, source_repo, committed=False)
    reference = fixture["authorization"]["authorization_core"][
        "dispatch_manifest"
    ]
    if kind == "missing":
        reference.pop("byte_length")
    elif kind == "extra":
        reference["path"] = fixture["manifest"][
            "manifest_target_path"
        ]
    else:
        reference["whole_file_sha256"] = "sha256:" + "0" * 64
    authorization_support._resign(fixture)
    with pytest.raises(DispatchAuthorizationError):
        validate_dispatch_authorization(
            repo_root=fixture["root"],
            authorization_path=fixture["authorization_path"],
            require_audit=False,
            scan_history=False,
        )


def test_old_opaque_packet_cannot_authorize_manifest_dispatch(
    tmp_path, source_repo
):
    fixture = _fixture(tmp_path, source_repo, committed=False)
    core = fixture["authorization"]["authorization_core"]
    core.pop("dispatch_manifest")
    core["dispatcher_packet"] = {
        "packet_id": "OLD-PACKET",
        "packet_purpose": "exact_offline_research_dispatch_stage_a",
        "packet_version": "old",
        "path": "scratch/OLD.dispatch_packet.json",
        "whole_file_sha256": "sha256:" + "0" * 64,
        "byte_length": 1,
        "byte_encoding": "utf8_exact_file_bytes",
        "serialization": "deterministic_json_one_lf",
        "placeholder_forbidden": True,
    }
    authorization_support._resign(fixture)
    with pytest.raises(DispatchAuthorizationError):
        validate_dispatch_authorization(
            repo_root=fixture["root"],
            authorization_path=fixture["authorization_path"],
            require_audit=False,
            scan_history=False,
        )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.__setitem__(
            "created_at", "2026-07-20T19:00:00Z"
        ),
        lambda value: value["queue_binding"].__setitem__(
            "raw_sha256", "sha256:" + "0" * 64
        ),
        lambda value: value["gate_q_binding"].__setitem__(
            "file_sha256", "sha256:" + "0" * 64
        ),
        lambda value: value["runner_binding"].__setitem__(
            "version", "other"
        ),
        lambda value: value["artifact_bindings"]["strategy_spec"].__setitem__(
            "sha256", "sha256:" + "0" * 64
        ),
        lambda value: value["dataset_binding"].__setitem__(
            "sha256", "sha256:" + "0" * 64
        ),
        lambda value: value["denominator"].__setitem__("planned", 3),
        lambda value: value["budget"].__setitem__("upper_bound", 3),
        lambda value: value["output_targets"].__setitem__(
            "scratch_run_directory", "scratch/FIXTURE-RUN/other/"
        ),
        lambda value: value["output_targets"].__setitem__(
            "provisional_result_paths",
            ["scratch/FIXTURE-RUN/dispatch/other.json"],
        ),
        lambda value: value["manifest_derivation"].__setitem__(
            "dispatch_derivation_version", "other"
        ),
    ],
)
def test_every_dispatch_field_and_exact_leaf_drift_is_rejected(
    tmp_path, source_repo, mutation
):
    fixture = _fixture(tmp_path, source_repo, committed=True)
    dispatch = derive_dispatch_record(
        manifest=fixture["manifest"],
        manifest_raw=fixture["manifest_raw"],
        authorization=fixture["authorization"],
        authorization_raw=fixture["authorization_raw"],
    )
    mutation(dispatch)
    target = _write_dispatch(fixture, dispatch)
    with pytest.raises(DispatchAuthorizationError):
        validate_dispatch_record_for_authorization(
            repo_root=fixture["root"],
            dispatch_path=target,
        )


def test_manifest_has_no_production_authority_or_circular_fields(
    tmp_path, source_repo
):
    fixture = _fixture(tmp_path, source_repo, committed=False)
    manifest = json.loads(fixture["manifest_raw"].decode("utf-8"))
    serialized = fixture["manifest_raw"].decode("utf-8")
    assert manifest["non_authority_declaration"] == (
        manifest_contract.MANIFEST_NON_AUTHORITY
    )
    assert "authorization_id" not in serialized
    assert "authorization_core_sha256" not in serialized
    assert "manifest_whole_file_sha256" not in serialized
    assert "dispatcher_packet" not in serialized
    assert not any(
        key in manifest
        for key in ("self_sha256", "byte_length", "future_kdauth")
    )
