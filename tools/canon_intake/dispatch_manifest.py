"""Canonical non-authorizing dispatch manifest contract and protected writer."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import stat
import subprocess
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, Iterator, Mapping

from jsonschema import Draft7Validator, FormatChecker, RefResolver


SCHEMA_NAME = "canon_dispatch_manifest.schema.json"
SCHEMA_VERSION = "canon_dispatch_manifest_v1"
DERIVATION_VERSION = "canon_dispatch_from_manifest_v1"
MANIFEST_ROOT = Path("research/queue/dispatch_manifests")
LOCK_PATH = MANIFEST_ROOT / ".dispatch_manifest.lock"
WRITER_IDENTITY = "dispatch_manifest_writer_v1"
MANIFEST_ID_RE = re.compile(r"^DMAN-H004-R2-[0-9]{4}$")
BINARY_FLAG = getattr(os, "O_BINARY", 0)

MANIFEST_NON_AUTHORITY = {
    "commitment_evidence_only": True,
    "does_not_authorize_dispatch": True,
    "does_not_create_kdauth": True,
    "does_not_invoke_runner": True,
    "does_not_authorize_retry": True,
    "not_result_population_authority": True,
    "not_ranking_recommendation_authority": True,
    "not_candidate_readiness_promotion_authority": True,
    "not_runtime_paper_live_authority": True,
}

DISPATCH_IMMUTABLE_POSTURE = {
    "exclusive_create_required": True,
    "append_only_identity_history": True,
    "overwrite_forbidden": True,
    "delete_forbidden": True,
    "repair_in_place_forbidden": True,
    "single_use_dispatch_id": True,
    "single_use_run_id": True,
    "single_use_queue_authorization_pair": True,
    "single_use_target_paths": True,
    "reuse_scan_includes_historical_records": True,
}

DISPATCH_NON_AUTHORITY = {
    "control_plane_history_only": True,
    "not_canonical_strategy_performance_evidence": True,
    "not_result_population_authority": True,
    "not_exp_replacement": True,
    "not_rep_replacement": True,
    "not_outcome_ledger_replacement": True,
    "not_recommendation_replacement": True,
    "not_decision_replacement": True,
    "not_ranking_authority": True,
    "not_recommendation_authority": True,
    "not_readiness_authority": True,
    "not_promotion_authority": True,
    "not_candidate_authority": True,
    "not_scheduler_authority": True,
    "not_runtime_authority": True,
    "not_paper_live_authority": True,
    "canonical_result_population_write_forbidden": True,
}


class DispatchManifestError(ValueError):
    """Manifest validation or pre-crossing failure."""


class DispatchManifestIntegrityCriticalError(DispatchManifestError):
    """An immutable manifest crossing or its cleanup is uncertain."""


def _digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def repo_canonical_json_v1(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise DispatchManifestError("value is not canonical JSON") from exc


def serialize_dispatch_manifest(value: Any) -> bytes:
    repo_canonical_json_v1(value)
    return (
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _lexical_absolute(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


def _is_link_or_reparse(path: Path) -> bool:
    try:
        metadata = os.lstat(path)
    except OSError:
        return False
    if stat.S_ISLNK(metadata.st_mode):
        return True
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    attributes = getattr(metadata, "st_file_attributes", 0)
    return bool(reparse and attributes & reparse)


def _reject_link_components(path: Path, label: str) -> Path:
    lexical = _lexical_absolute(path)
    for component in reversed([lexical, *lexical.parents]):
        if os.path.lexists(component) and _is_link_or_reparse(component):
            raise DispatchManifestError(
                f"{label} contains a symlink, junction, or reparse component"
            )
    return lexical


def _resolve_root(repo_root: Path) -> Path:
    root = _reject_link_components(Path(repo_root), "repo root")
    if not root.is_dir():
        raise DispatchManifestError("repo root must be an existing directory")
    return root.resolve()


def _repo_path(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise DispatchManifestError(
            f"{label} must be a repo-relative POSIX path"
        )
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(
        part in {"", ".", ".."} for part in pure.parts
    ):
        raise DispatchManifestError(
            f"{label} must not contain traversal or empty components"
        )
    lexical = _reject_link_components(
        root.joinpath(*pure.parts), label
    )
    resolved = lexical.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise DispatchManifestError(f"{label} escapes the repository") from exc
    return resolved


def _schema_validator(root: Path) -> Draft7Validator:
    schema_path = root / "research/schemas" / SCHEMA_NAME
    auth_schema_path = (
        root / "research/schemas/canon_dispatch_authorization.schema.json"
    )
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        auth_schema = json.loads(auth_schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DispatchManifestError(
            "dispatch manifest schema dependency is unreadable"
        ) from exc
    Draft7Validator.check_schema(schema)
    Draft7Validator.check_schema(auth_schema)
    resolver = RefResolver(
        base_uri=schema_path.as_uri(),
        referrer=schema,
        store={
            auth_schema_path.as_uri(): auth_schema,
            auth_schema["$id"]: auth_schema,
            "canon_dispatch_authorization.schema.json": auth_schema,
        },
    )
    return Draft7Validator(
        schema, resolver=resolver, format_checker=FormatChecker()
    )


def _schema_check(root: Path, manifest: Mapping[str, Any]) -> None:
    errors = sorted(
        _schema_validator(root).iter_errors(manifest),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        location = ".".join(
            str(part) for part in errors[0].absolute_path
        )
        suffix = f" at {location}" if location else ""
        raise DispatchManifestError(
            f"dispatch manifest schema validation failed{suffix}: "
            f"{errors[0].message}"
        )


def _read_manifest(path: Path) -> tuple[dict[str, Any], bytes]:
    selected = _reject_link_components(path, "dispatch manifest")
    if selected.is_symlink() or not selected.is_file():
        raise DispatchManifestError(
            "dispatch manifest must be a regular non-link file"
        )
    try:
        raw = selected.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DispatchManifestError(
            "dispatch manifest must be readable UTF-8 JSON"
        ) from exc
    if not isinstance(value, dict):
        raise DispatchManifestError("dispatch manifest must be an object")
    if raw != serialize_dispatch_manifest(value):
        raise DispatchManifestError(
            "dispatch manifest is not canonical sorted two-space JSON plus one LF"
        )
    return value, raw


def _validate_semantics(
    root: Path,
    manifest: Mapping[str, Any],
    *,
    validate_references: bool,
) -> None:
    manifest_id = manifest["manifest_id"]
    expected_path = (
        MANIFEST_ROOT / f"{manifest_id}.dispatch_manifest.json"
    ).as_posix()
    if manifest["manifest_target_path"] != expected_path:
        raise DispatchManifestError("manifest ID/path mismatch")
    crossing = manifest["crossing_identities"]
    dispatch_date = crossing["dispatch_id"].split("-")[1]
    run_date = crossing["run_id"].split("-")[1]
    try:
        from datetime import datetime, timezone

        created = datetime.fromisoformat(
            manifest["dispatch_created_at"].replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise DispatchManifestError(
            "dispatch_created_at must be RFC3339"
        ) from exc
    if created.tzinfo is None or created.utcoffset() is None:
        raise DispatchManifestError(
            "dispatch_created_at must be timezone-aware"
        )
    created_date = created.astimezone(timezone.utc).strftime("%Y%m%d")
    if created_date != dispatch_date or run_date != dispatch_date:
        raise DispatchManifestError(
            "manifest dispatch/run IDs and dispatch_created_at dates differ"
        )
    outputs = manifest["output_targets"]
    if (
        outputs["execution_event_stream_path"]
        != crossing["execution_event_stream_path"]
    ):
        raise DispatchManifestError(
            "manifest execution-event target does not equal the run binding"
        )
    scratch_root = outputs["scratch_output_root"]
    scratch_run = outputs["scratch_run_directory"]
    if scratch_run == scratch_root or not scratch_run.startswith(scratch_root):
        raise DispatchManifestError(
            "scratch run directory must be one exact descendant, not a root permission"
        )
    for target in outputs["provisional_result_paths"]:
        if target.startswith(scratch_run) is False:
            raise DispatchManifestError(
                "each provisional result must be an exact leaf beneath the run directory"
            )
    denominator = manifest["denominator"]
    budget = manifest["budget"]
    values = (
        denominator["planned"],
        denominator["variant_manifest_value"],
        denominator["sweep_plan_value"],
        budget["upper_bound"],
    )
    if len(set(values)) != 1:
        raise DispatchManifestError(
            "manifest denominator and budget values must be identical"
        )
    if (
        manifest["queue_binding"]["gate_q"]
        != manifest["lineage"]["gate_q"]
    ):
        raise DispatchManifestError(
            "manifest queue and lineage Gate-Q bindings differ"
        )
    if manifest["non_authority_declaration"] != MANIFEST_NON_AUTHORITY:
        raise DispatchManifestError(
            "manifest non-authority declaration is not exact"
        )

    if not validate_references:
        return

    projected_core = {
        "queue_binding": manifest["queue_binding"],
        "crossing_identities": manifest["crossing_identities"],
        "lineage": manifest["lineage"],
        "dataset": manifest["dataset"],
        "funding": manifest["funding"],
        "runner": manifest["runner"],
        "denominator": manifest["denominator"],
        "budget": manifest["budget"],
        "execution_parameters": manifest["execution_parameters"],
        "output_targets": {
            "scratch_output_root": outputs["scratch_output_root"],
            "execution_event_stream_path": outputs[
                "execution_event_stream_path"
            ],
            "canonical_result_population_target_forbidden": True,
        },
    }
    try:
        from tools.canon_intake.dispatch_authorization import (
            _validate_crossing_identities,
            _validate_dataset,
            _validate_denominator_budget_and_outputs,
            _validate_funding,
            _validate_lineage,
            _validate_queue_and_gate,
            _validate_runner,
        )

        _validate_queue_and_gate(root, projected_core)
        _validate_crossing_identities(projected_core)
        _validate_lineage(root, projected_core)
        _validate_dataset(root, projected_core)
        _validate_funding(root, projected_core)
        _validate_runner(root, projected_core)
        _validate_denominator_budget_and_outputs(root, projected_core)
    except Exception as exc:
        if isinstance(exc, DispatchManifestError):
            raise
        raise DispatchManifestError(str(exc)) from exc


def validate_dispatch_manifest(
    *,
    repo_root: Path,
    manifest_path: Path,
    expected_whole_file_sha256: str | None = None,
    expected_byte_length: int | None = None,
    require_authoritative_path: bool = True,
    validate_references: bool = True,
) -> dict[str, Any]:
    root = _resolve_root(repo_root)
    selected = Path(manifest_path)
    if not selected.is_absolute():
        selected = root / selected
    manifest, raw = _read_manifest(selected)
    _schema_check(root, manifest)
    _validate_semantics(
        root, manifest, validate_references=validate_references
    )
    expected_path = _repo_path(
        root, manifest["manifest_target_path"], "manifest target path"
    )
    if require_authoritative_path and selected.resolve() != expected_path:
        raise DispatchManifestError(
            "dispatch manifest is not at its authoritative ID-derived path"
        )
    whole_hash = _digest(raw)
    if (
        expected_whole_file_sha256 is not None
        and whole_hash != expected_whole_file_sha256
    ):
        raise DispatchManifestError("dispatch manifest whole-file hash mismatch")
    if (
        expected_byte_length is not None
        and len(raw) != expected_byte_length
    ):
        raise DispatchManifestError("dispatch manifest byte-length mismatch")
    return {
        "valid": True,
        "manifest_id": manifest["manifest_id"],
        "manifest_path": manifest["manifest_target_path"],
        "whole_file_sha256": whole_hash,
        "byte_length": len(raw),
        "dispatch_derivation_version": manifest[
            "dispatch_derivation_version"
        ],
        "manifest": manifest,
        "raw": raw,
        "non_authority": True,
    }


def validate_manifest_authorization_binding(
    manifest: Mapping[str, Any],
    authorization_core: Mapping[str, Any],
) -> None:
    """Prove that KDAUTH duplicates no intent different from its manifest."""
    pairs = {
        "queue_binding": manifest["queue_binding"],
        "crossing_identities": manifest["crossing_identities"],
        "lineage": manifest["lineage"],
        "dataset": manifest["dataset"],
        "funding": manifest["funding"],
        "runner": manifest["runner"],
        "denominator": manifest["denominator"],
        "budget": manifest["budget"],
        "execution_parameters": manifest["execution_parameters"],
    }
    for field, expected in pairs.items():
        if authorization_core.get(field) != expected:
            raise DispatchManifestError(
                f"KDAUTH {field} differs from the committed dispatch manifest"
            )
    outputs = manifest["output_targets"]
    expected_outputs = {
        "scratch_output_root": outputs["scratch_output_root"],
        "execution_event_stream_path": outputs[
            "execution_event_stream_path"
        ],
        "canonical_result_population_target_forbidden": True,
    }
    if authorization_core.get("output_targets") != expected_outputs:
        raise DispatchManifestError(
            "KDAUTH output roots differ from the committed dispatch manifest"
        )


def derive_dispatch_record(
    *,
    manifest: Mapping[str, Any],
    manifest_raw: bytes,
    authorization: Mapping[str, Any],
    authorization_raw: bytes,
) -> dict[str, Any]:
    """Pure deterministic manifest + existing KDAUTH -> dispatch transform."""
    core = authorization["authorization_core"]
    validate_manifest_authorization_binding(manifest, core)
    manifest_ref = core["dispatch_manifest"]
    if (
        manifest_ref["manifest_id"] != manifest["manifest_id"]
        or manifest_ref["whole_file_sha256"] != _digest(manifest_raw)
        or manifest_ref["byte_length"] != len(manifest_raw)
    ):
        raise DispatchManifestError(
            "KDAUTH does not commit the exact manifest bytes"
        )
    crossing = manifest["crossing_identities"]
    queue = manifest["queue_binding"]
    gate = queue["gate_q"]
    dataset = manifest["dataset"]
    authorization_path = authorization[
        "authorization_artifact_target_path"
    ]
    return {
        "schema_version": "canon_dispatch_record_v1",
        "dispatch_id": crossing["dispatch_id"],
        "dispatch_record_path": crossing["dispatch_record_path"],
        "created_at": manifest["dispatch_created_at"],
        "dispatch_state": "dispatched",
        "manifest_derivation": {
            "manifest_id": manifest["manifest_id"],
            "manifest_path": manifest["manifest_target_path"],
            "manifest_whole_file_sha256": _digest(manifest_raw),
            "manifest_byte_length": len(manifest_raw),
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
            "source_path": authorization_path,
            "source_sha256": _digest(authorization_raw),
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


def serialize_derived_dispatch_record(
    *,
    manifest: Mapping[str, Any],
    manifest_raw: bytes,
    authorization: Mapping[str, Any],
    authorization_raw: bytes,
) -> bytes:
    from tools.canon_intake.dispatch_authorization import (
        serialize_dispatch_authorization,
    )

    return serialize_dispatch_authorization(
        derive_dispatch_record(
            manifest=manifest,
            manifest_raw=manifest_raw,
            authorization=authorization,
            authorization_raw=authorization_raw,
        )
    )


def _git(root: Path, *args: str, check: bool = True) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise DispatchManifestError("git history is unavailable") from exc
    if check and result.returncode != 0:
        raise DispatchManifestError(
            f"git history command failed: {result.stderr.strip()}"
        )
    return result.stdout


def _assert_identity_unused(
    root: Path, manifest_id: str, target_path: str
) -> None:
    target = _repo_path(root, target_path, "manifest target")
    if os.path.lexists(target):
        raise DispatchManifestError(
            "dispatch manifest target already exists; overwrite is forbidden"
        )
    if (
        _git(root, "rev-parse", "--is-inside-work-tree", check=False).strip()
        != "true"
    ):
        raise DispatchManifestError("retained Git history is unavailable")
    commits = _git(
        root,
        "log",
        "--all",
        "--format=%H",
        "--",
        MANIFEST_ROOT.as_posix(),
    ).splitlines()
    for commit in commits:
        paths = _git(
            root,
            "ls-tree",
            "-r",
            "--name-only",
            commit,
            "--",
            MANIFEST_ROOT.as_posix(),
        ).splitlines()
        for path in paths:
            if path == target_path or manifest_id in Path(path).name:
                raise DispatchManifestError(
                    "retained history already consumes the manifest identity"
                )


@contextmanager
def _manifest_lock(root: Path) -> Iterator[dict[str, bool]]:
    lock = _repo_path(root, LOCK_PATH.as_posix(), "manifest crossing lock")
    if not lock.parent.is_dir():
        raise DispatchManifestError(
            "dispatch manifest root must already exist"
        )
    state = {"crossing_committed": False}
    fd: int | None = None
    acquired = False
    try:
        fd = os.open(
            lock,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY | BINARY_FLAG,
            0o600,
        )
        acquired = True
        raw = (
            json.dumps(
                {
                    "lock_kind": "dispatch_manifest_crossing",
                    "pid": os.getpid(),
                    "writer_identity": WRITER_IDENTITY,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode("utf-8")
        if os.write(fd, raw) != len(raw):
            raise OSError("partial manifest lock write")
        os.fsync(fd)
        os.close(fd)
        fd = None
        yield state
    except FileExistsError as exc:
        raise DispatchManifestError(
            "dispatch manifest lock exists; stale locks fail closed"
        ) from exc
    finally:
        if fd is not None:
            os.close(fd)
        if acquired:
            try:
                lock.unlink()
                if os.name != "nt":
                    parent_fd = os.open(
                        lock.parent,
                        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
                    )
                    try:
                        os.fsync(parent_fd)
                    finally:
                        os.close(parent_fd)
            except FileNotFoundError:
                pass
            except OSError as exc:
                raise DispatchManifestIntegrityCriticalError(
                    "manifest lock cleanup failed; operator inspection required"
                ) from exc


def write_dispatch_manifest(
    *,
    repo_root: Path,
    proposal_path: Path,
    reviewed_whole_file_sha256: str,
) -> dict[str, Any]:
    """Validate twice and exclusive-create one immutable manifest."""
    root = _resolve_root(repo_root)
    selected = Path(proposal_path)
    if not selected.is_absolute():
        selected = root / selected
    pre = validate_dispatch_manifest(
        repo_root=root,
        manifest_path=selected,
        expected_whole_file_sha256=reviewed_whole_file_sha256,
        require_authoritative_path=False,
    )
    _assert_identity_unused(
        root, pre["manifest_id"], pre["manifest_path"]
    )
    target = _repo_path(root, pre["manifest_path"], "manifest target")
    from tools.canon_intake.dispatch_authorization_writer import (
        _AnchoredDirectory,
        _write_all,
    )

    try:
        pre_parent = _AnchoredDirectory(
            root=root,
            relative=target.parent.relative_to(root),
            label="dispatch manifest parent",
        )
        try:
            pre_parent.assert_current()
            pre_parent.fsync()
            expected_parent_identity = pre_parent.identity
        finally:
            pre_parent.close()
    except Exception as exc:
        raise DispatchManifestError(
            "descriptor-anchored no-reparse manifest parent is unavailable"
        ) from exc
    result: dict[str, Any] | None = None
    with _manifest_lock(root) as state:
        locked = validate_dispatch_manifest(
            repo_root=root,
            manifest_path=selected,
            expected_whole_file_sha256=reviewed_whole_file_sha256,
            expected_byte_length=pre["byte_length"],
            require_authoritative_path=False,
        )
        if locked["raw"] != pre["raw"]:
            raise DispatchManifestError("manifest proposal bytes changed in-lock")
        _assert_identity_unused(
            root, locked["manifest_id"], locked["manifest_path"]
        )
        target = _repo_path(
            root, locked["manifest_path"], "manifest target"
        )
        anchored = None
        target_file = None
        try:
            anchored = _AnchoredDirectory(
                root=root,
                relative=target.parent.relative_to(root),
                label="dispatch manifest parent",
            )
            if anchored.identity != expected_parent_identity:
                raise OSError("manifest parent identity changed in-lock")
            anchored.assert_current()
            anchored.require_absent(target.name)
            target_file = anchored.create(target.name)
            _write_all(target_file.fd, locked["raw"])
            target_file.fsync()
            anchored.fsync()
            anchored.assert_current()
            anchored.verify_reference(
                target.name,
                expected_identity=target_file.identity,
                expected_raw=locked["raw"],
            )
            if target_file.read() != locked["raw"]:
                raise OSError("manifest target reread mismatch")
        except OSError as exc:
            raise DispatchManifestIntegrityCriticalError(
                "manifest crossing is uncertain; preserve evidence and inspect"
            ) from exc
        finally:
            if target_file is not None:
                target_file.close()
            if anchored is not None:
                anchored.close()
        state["crossing_committed"] = True
        result = {
            "manifest_created": True,
            "manifest_id": locked["manifest_id"],
            "manifest_path": locked["manifest_path"],
            "whole_file_sha256": locked["whole_file_sha256"],
            "byte_length": locked["byte_length"],
            "writer_identity": WRITER_IDENTITY,
            "non_authority": True,
        }
    if result is None:
        raise DispatchManifestIntegrityCriticalError(
            "manifest crossing ended without a result"
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expected-whole-file-sha256")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        if args.write:
            if not args.expected_whole_file_sha256:
                raise DispatchManifestError(
                    "--write requires --expected-whole-file-sha256"
                )
            result = write_dispatch_manifest(
                repo_root=args.repo_root,
                proposal_path=args.manifest,
                reviewed_whole_file_sha256=args.expected_whole_file_sha256,
            )
        else:
            result = validate_dispatch_manifest(
                repo_root=args.repo_root,
                manifest_path=args.manifest,
                expected_whole_file_sha256=args.expected_whole_file_sha256,
            )
            result = {
                key: value
                for key, value in result.items()
                if key not in {"manifest", "raw"}
            }
    except DispatchManifestError as exc:
        parser.exit(2, f"Dispatch manifest stopped: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
