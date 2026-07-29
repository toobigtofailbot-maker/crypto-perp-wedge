"""Protected append-only writer for one exact canonical dispatch record."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping

from tools.canon_intake.dispatch_authorization import (
    AUDIT_PATH,
    DISPATCH_ROOT,
    DispatchAuthorizationError,
    read_and_validate_dispatch_authorization_audit,
    validate_dispatch_authorization,
    validate_dispatch_authorization_for_consumption,
)
from tools.canon_intake.dispatch_authorization_reservation import (
    DispatchAuthorizationReservationError,
    DispatchAuthorizationReservationIntegrityCriticalError,
    dispatch_authorization_crossing_lock,
)
from tools.canon_intake.dispatch_authorization_writer import (
    DispatchAuthorizationWriterError,
    DispatchAuthorizationWriterIntegrityCriticalError,
    _AnchoredDirectory,
    _AnchoredFile,
    _write_all,
    append_dispatch_authorization_lifecycle_event,
)
from tools.canon_intake.dispatch_manifest import (
    DispatchManifestError,
    derive_dispatch_record,
    serialize_derived_dispatch_record,
    validate_dispatch_manifest,
)

WRITER_IDENTITY = "tools.canon_intake.dispatch_writer_v1"
LOCK_PATH = Path("research/queue/.canon_dispatch_writer.lock")


class DispatchWriterError(ValueError):
    """Fail-closed dispatch-writer rejection before durable success."""


class DispatchWriterIntegrityCriticalError(DispatchWriterError):
    """Uncertain or failed crossing that requires operator inspection."""


def _digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _selected_path(root: Path, selected: Path) -> Path:
    value = Path(selected)
    return value if value.is_absolute() else root / value


def _require_identity(label: str, supplied: str, actual: str) -> None:
    if not isinstance(supplied, str) or not supplied:
        raise DispatchWriterError(f"{label} must be explicitly supplied")
    if supplied != actual:
        raise DispatchWriterError(f"{label} differs from reviewed artifact")


def _load_authorization_bytes(path: Path) -> tuple[dict[str, Any], bytes]:
    if path.is_symlink() or not path.is_file():
        raise DispatchWriterError(
            "KDAUTH must be a regular non-symlink authoritative file"
        )
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DispatchWriterError("KDAUTH bytes are unreadable") from exc
    if not isinstance(value, dict):
        raise DispatchWriterError("KDAUTH must decode to one JSON object")
    return value, raw


def _validate_reviewed_inputs(
    *,
    root: Path,
    manifest_path: Path,
    reviewed_manifest_whole_file_sha256: str,
    manifest_id: str,
    authorization_path: Path,
    reviewed_authorization_whole_file_sha256: str,
    authorization_id: str,
    dispatch_id: str,
    run_id: str,
    expected_manifest_raw: bytes | None = None,
    expected_authorization_raw: bytes | None = None,
) -> dict[str, Any]:
    manifest_validation = validate_dispatch_manifest(
        repo_root=root,
        manifest_path=manifest_path,
        expected_whole_file_sha256=reviewed_manifest_whole_file_sha256,
        expected_byte_length=(
            len(expected_manifest_raw)
            if expected_manifest_raw is not None
            else None
        ),
        require_authoritative_path=True,
    )
    authorization_validation = validate_dispatch_authorization(
        repo_root=root,
        authorization_path=authorization_path,
        expected_whole_file_sha256=(
            reviewed_authorization_whole_file_sha256
        ),
        expected_byte_length=(
            len(expected_authorization_raw)
            if expected_authorization_raw is not None
            else None
        ),
        require_audit=True,
        scan_history=True,
    )
    authorization, authorization_raw = _load_authorization_bytes(
        authorization_path
    )
    manifest_raw = manifest_validation["raw"]
    if (
        expected_manifest_raw is not None
        and manifest_raw != expected_manifest_raw
    ):
        raise DispatchWriterError(
            "manifest bytes changed after pre-lock review"
        )
    if (
        expected_authorization_raw is not None
        and authorization_raw != expected_authorization_raw
    ):
        raise DispatchWriterError(
            "KDAUTH bytes changed after pre-lock review"
        )
    if (
        authorization_validation["whole_file_sha256"]
        != _digest(authorization_raw)
        or authorization_validation["byte_length"] != len(authorization_raw)
    ):
        raise DispatchWriterError(
            "KDAUTH bytes changed during authoritative validation"
        )

    manifest = manifest_validation["manifest"]
    _require_identity("manifest_id", manifest_id, manifest["manifest_id"])
    _require_identity(
        "authorization_id",
        authorization_id,
        authorization["authorization_id"],
    )
    crossing = authorization["authorization_core"]["crossing_identities"]
    _require_identity("dispatch_id", dispatch_id, crossing["dispatch_id"])
    _require_identity("run_id", run_id, crossing["run_id"])
    if manifest["crossing_identities"] != crossing:
        raise DispatchWriterError(
            "manifest crossing identities differ from exact KDAUTH"
        )

    dispatch = derive_dispatch_record(
        manifest=manifest,
        manifest_raw=manifest_raw,
        authorization=authorization,
        authorization_raw=authorization_raw,
    )
    dispatch_raw = serialize_derived_dispatch_record(
        manifest=manifest,
        manifest_raw=manifest_raw,
        authorization=authorization,
        authorization_raw=authorization_raw,
    )
    expected_dispatch_path = (
        DISPATCH_ROOT / f"{dispatch_id}.dispatch_record.json"
    ).as_posix()
    if dispatch["dispatch_record_path"] != expected_dispatch_path:
        raise DispatchWriterError(
            "derived dispatch target is not the ID-derived authoritative path"
        )
    return {
        "manifest": manifest,
        "manifest_raw": manifest_raw,
        "manifest_validation": manifest_validation,
        "authorization": authorization,
        "authorization_raw": authorization_raw,
        "authorization_validation": authorization_validation,
        "dispatch": dispatch,
        "dispatch_raw": dispatch_raw,
        "dispatch_path": root / Path(expected_dispatch_path),
    }


@contextmanager
def _dispatch_crossing_lock(
    *,
    root: Path,
    state: dict[str, bool],
) -> Iterator[None]:
    parent: _AnchoredDirectory | None = None
    lock_file = None
    try:
        parent = _AnchoredDirectory(
            root=root,
            relative=LOCK_PATH.parent,
            label="dispatch crossing lock parent",
        )
        parent.assert_current()
        parent.require_absent(LOCK_PATH.name)
        lock_file = parent.create(LOCK_PATH.name)
        raw = (
            json.dumps(
                {
                    "lock_kind": "canonical_dispatch_crossing",
                    "pid": os.getpid(),
                    "writer_identity": WRITER_IDENTITY,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode("utf-8")
        _write_all(lock_file.fd, raw)
        lock_file.fsync()
        parent.fsync()
        parent.verify_reference(
            LOCK_PATH.name,
            expected_identity=lock_file.identity,
            expected_raw=raw,
        )
        yield
    except FileExistsError as exc:
        raise DispatchWriterError(
            "dispatch crossing lock exists; stale locks fail closed"
        ) from exc
    except DispatchWriterError:
        raise
    except OSError as exc:
        raise DispatchWriterError(
            "descriptor-anchored dispatch lock is unavailable"
        ) from exc
    finally:
        cleanup_error: OSError | None = None
        if lock_file is not None:
            try:
                lock_file.delete()
                if parent is not None:
                    parent.fsync()
                    parent.assert_current()
            except OSError as exc:
                cleanup_error = exc
                lock_file.close()
        if parent is not None:
            parent.close()
        if cleanup_error is not None:
            error = DispatchWriterIntegrityCriticalError(
                "dispatch lock cleanup failed; operator inspection required"
            )
            error.failure_phase = "lock_cleanup"
            error.uncertainty_class = "lock_cleanup_uncertain"
            error.dispatch_durable = state["dispatch_durable"]
            raise error from cleanup_error


def _anchored_inputs_and_target(
    *,
    root: Path,
    manifest_path: Path,
    authorization_path: Path,
    dispatch_path: Path,
) -> ExitStack:
    stack = ExitStack()
    try:
        for label, path in (
            ("dispatch manifest parent", manifest_path.parent),
            ("KDAUTH parent", authorization_path.parent),
            ("KDAUTH audit parent", (root / AUDIT_PATH).parent),
            ("dispatch target parent", dispatch_path.parent),
        ):
            relative = path.relative_to(root)
            anchored = _AnchoredDirectory(
                root=root,
                relative=relative,
                label=label,
            )
            stack.callback(anchored.close)
            anchored.assert_current()
            anchored.fsync()
            setattr(stack, label.lower().replace(" ", "_"), anchored)
        return stack
    except Exception:
        stack.close()
        raise


def _create_and_prove_dispatch(
    *,
    root: Path,
    manifest_path: Path,
    authorization_path: Path,
    reviewed_manifest_whole_file_sha256: str,
    manifest_id: str,
    reviewed_authorization_whole_file_sha256: str,
    authorization_id: str,
    dispatch_id: str,
    run_id: str,
    preflight: Mapping[str, Any],
) -> dict[str, Any]:
    dispatch_path = preflight["dispatch_path"]
    with dispatch_authorization_crossing_lock(repo_root=root):
        with _anchored_inputs_and_target(
            root=root,
            manifest_path=manifest_path,
            authorization_path=authorization_path,
            dispatch_path=dispatch_path,
        ) as anchors:
            manifest_parent = anchors.dispatch_manifest_parent
            authorization_parent = anchors.kdauth_parent
            audit_parent = anchors.kdauth_audit_parent
            target_parent = anchors.dispatch_target_parent
            manifest_file = manifest_parent.open_existing(
                manifest_path.name, writable=False
            )
            authorization_file = authorization_parent.open_existing(
                authorization_path.name, writable=False
            )
            audit_file = audit_parent.open_existing(
                AUDIT_PATH.name, writable=False
            )
            target_file = None
            try:
                manifest_raw = manifest_file.read()
                authorization_raw = authorization_file.read()
                audit_raw = audit_file.read()
                locked = _validate_reviewed_inputs(
                    root=root,
                    manifest_path=manifest_path,
                    reviewed_manifest_whole_file_sha256=(
                        reviewed_manifest_whole_file_sha256
                    ),
                    manifest_id=manifest_id,
                    authorization_path=authorization_path,
                    reviewed_authorization_whole_file_sha256=(
                        reviewed_authorization_whole_file_sha256
                    ),
                    authorization_id=authorization_id,
                    dispatch_id=dispatch_id,
                    run_id=run_id,
                    expected_manifest_raw=preflight["manifest_raw"],
                    expected_authorization_raw=preflight[
                        "authorization_raw"
                    ],
                )
                rows, audit_length = (
                    read_and_validate_dispatch_authorization_audit(
                        repo_root=root
                    )
                )
                if (
                    manifest_raw != locked["manifest_raw"]
                    or authorization_raw != locked["authorization_raw"]
                    or audit_length != len(audit_raw)
                    or b"".join(line for _, line in rows) != audit_raw
                    or locked["dispatch_raw"] != preflight["dispatch_raw"]
                ):
                    raise DispatchWriterError(
                        "anchored inputs changed during in-lock validation"
                    )
                for anchored in (
                    manifest_parent,
                    authorization_parent,
                    audit_parent,
                    target_parent,
                ):
                    anchored.assert_current()
                manifest_parent.verify_reference(
                    manifest_path.name,
                    expected_identity=manifest_file.identity,
                    expected_raw=manifest_raw,
                )
                authorization_parent.verify_reference(
                    authorization_path.name,
                    expected_identity=authorization_file.identity,
                    expected_raw=authorization_raw,
                )
                audit_parent.verify_reference(
                    AUDIT_PATH.name,
                    expected_identity=audit_file.identity,
                    expected_raw=audit_raw,
                )
                target_parent.require_absent(dispatch_path.name)
                target_file = target_parent.create(dispatch_path.name)
                _write_all(target_file.fd, locked["dispatch_raw"])
                target_file.fsync()
                target_parent.fsync()
                target_parent.assert_current()
                target_parent.verify_reference(
                    dispatch_path.name,
                    expected_identity=target_file.identity,
                    expected_raw=locked["dispatch_raw"],
                )
                if target_file.read() != locked["dispatch_raw"]:
                    raise OSError("durable dispatch reread mismatch")
                validation = validate_dispatch_authorization_for_consumption(
                    repo_root=root,
                    authorization_path=authorization_path,
                    dispatch_path=dispatch_path,
                )
                if (
                    validation["dispatch_validation"][
                        "dispatch_file_sha256"
                    ]
                    != _digest(locked["dispatch_raw"])
                    or validation["dispatch_validation"][
                        "dispatch_byte_length"
                    ]
                    != len(locked["dispatch_raw"])
                ):
                    raise OSError(
                        "durable dispatch validation differs from derived bytes"
                    )
                target_parent.verify_reference(
                    dispatch_path.name,
                    expected_identity=target_file.identity,
                    expected_raw=locked["dispatch_raw"],
                )
                return {
                    **locked,
                    "dispatch_validation": validation[
                        "dispatch_validation"
                    ],
                }
            except Exception as exc:
                if target_file is not None:
                    raise OSError(
                        "dispatch target creation began but exact durable "
                        "validation did not complete"
                    ) from exc
                raise
            finally:
                if target_file is not None:
                    target_file.close()
                audit_file.close()
                authorization_file.close()
                manifest_file.close()


def write_dispatch_record(
    *,
    repo_root: Path,
    manifest_path: Path,
    reviewed_manifest_whole_file_sha256: str,
    manifest_id: str,
    authorization_path: Path,
    reviewed_authorization_whole_file_sha256: str,
    authorization_id: str,
    dispatch_id: str,
    run_id: str,
    actor: str,
) -> dict[str, Any]:
    """Create one exact durable dispatch, then consume its exact KDAUTH."""
    if not isinstance(actor, str) or not actor:
        raise DispatchWriterError("actor must be explicitly supplied")
    root = Path(repo_root).resolve()
    selected_manifest = _selected_path(root, manifest_path)
    selected_authorization = _selected_path(root, authorization_path)
    try:
        preflight = _validate_reviewed_inputs(
            root=root,
            manifest_path=selected_manifest,
            reviewed_manifest_whole_file_sha256=(
                reviewed_manifest_whole_file_sha256
            ),
            manifest_id=manifest_id,
            authorization_path=selected_authorization,
            reviewed_authorization_whole_file_sha256=(
                reviewed_authorization_whole_file_sha256
            ),
            authorization_id=authorization_id,
            dispatch_id=dispatch_id,
            run_id=run_id,
        )
    except (DispatchAuthorizationError, DispatchManifestError) as exc:
        raise DispatchWriterError(str(exc)) from exc

    state = {"dispatch_durable": False}
    try:
        with _dispatch_crossing_lock(root=root, state=state):
            try:
                durable = _create_and_prove_dispatch(
                    root=root,
                    manifest_path=selected_manifest,
                    authorization_path=selected_authorization,
                    reviewed_manifest_whole_file_sha256=(
                        reviewed_manifest_whole_file_sha256
                    ),
                    manifest_id=manifest_id,
                    reviewed_authorization_whole_file_sha256=(
                        reviewed_authorization_whole_file_sha256
                    ),
                    authorization_id=authorization_id,
                    dispatch_id=dispatch_id,
                    run_id=run_id,
                    preflight=preflight,
                )
            except (
                DispatchAuthorizationReservationIntegrityCriticalError
            ):
                raise
            except (
                DispatchAuthorizationError,
                DispatchAuthorizationReservationError,
                DispatchManifestError,
            ) as exc:
                raise DispatchWriterError(str(exc)) from exc
            except OSError as exc:
                error = DispatchWriterIntegrityCriticalError(
                    "dispatch creation or durable verification is uncertain; "
                    "preserve evidence and inspect"
                )
                error.failure_phase = "dispatch_creation"
                error.uncertainty_class = "dispatch_durability_uncertain"
                error.dispatch_durable = False
                raise error from exc
            except DispatchWriterError:
                raise
            except Exception as exc:
                error = DispatchWriterIntegrityCriticalError(
                    "dispatch crossing failed in an unclassified state; "
                    "preserve evidence and inspect"
                )
                error.failure_phase = "dispatch_creation"
                error.uncertainty_class = "unclassified_crossing_failure"
                error.dispatch_durable = False
                raise error from exc

            state["dispatch_durable"] = True
            try:
                consumption = (
                    append_dispatch_authorization_lifecycle_event(
                        repo_root=root,
                        authorization_path=selected_authorization,
                        event_type="authorization_consumed",
                        actor=actor,
                        event_payload={
                            "event_kind": "authorization_consumed",
                            "consumer_tool": WRITER_IDENTITY,
                            "dispatch_record_path": durable[
                                "dispatch"
                            ]["dispatch_record_path"],
                            "consumption_is_permanent": True,
                        },
                    )
                )
            except Exception as exc:
                error = DispatchWriterIntegrityCriticalError(
                    "durable dispatch exists but KDAUTH consumption failed or "
                    "is uncertain; preserve the record and inspect"
                )
                error.failure_phase = "authorization_consumption"
                error.uncertainty_class = (
                    "lifecycle_append_or_terminal_uncertain"
                )
                error.dispatch_durable = True
                raise error from exc
    except DispatchWriterIntegrityCriticalError:
        raise
    except DispatchWriterError:
        raise
    except (
        DispatchAuthorizationReservationIntegrityCriticalError,
        DispatchAuthorizationWriterIntegrityCriticalError,
    ) as exc:
        error = DispatchWriterIntegrityCriticalError(
            "protected lock or lifecycle cleanup is uncertain; preserve "
            "evidence and inspect"
        )
        error.failure_phase = "protected_cleanup"
        error.uncertainty_class = "protected_cleanup_uncertain"
        error.dispatch_durable = state["dispatch_durable"]
        raise error from exc
    except DispatchAuthorizationWriterError as exc:
        if state["dispatch_durable"]:
            error = DispatchWriterIntegrityCriticalError(
                "durable dispatch exists but lifecycle completion failed; "
                "preserve evidence and inspect"
            )
            error.failure_phase = "authorization_consumption"
            error.uncertainty_class = "lifecycle_append_failed"
            error.dispatch_durable = True
            raise error from exc
        raise DispatchWriterError(str(exc)) from exc

    return {
        "dispatch_created": True,
        "dispatch_id": dispatch_id,
        "dispatch_record_path": durable["dispatch"][
            "dispatch_record_path"
        ],
        "dispatch_file_sha256": durable["dispatch_validation"][
            "dispatch_file_sha256"
        ],
        "dispatch_byte_length": durable["dispatch_validation"][
            "dispatch_byte_length"
        ],
        "authorization_id": authorization_id,
        "authorization_consumed": True,
        "authorization_consumption_event_id": consumption["event_id"],
        "writer_identity": WRITER_IDENTITY,
        "non_authority": {
            "control_plane_history_only": True,
            "does_not_invoke_runner": True,
            "does_not_create_execution_event": True,
            "does_not_create_result_population": True,
            "does_not_authorize_runtime_paper_live_or_capital": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--reviewed-manifest-whole-file-sha256", required=True
    )
    parser.add_argument("--manifest-id", required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument(
        "--reviewed-authorization-whole-file-sha256", required=True
    )
    parser.add_argument("--authorization-id", required=True)
    parser.add_argument("--dispatch-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--actor", required=True)
    args = parser.parse_args()
    try:
        result = write_dispatch_record(
            repo_root=args.repo_root,
            manifest_path=args.manifest,
            reviewed_manifest_whole_file_sha256=(
                args.reviewed_manifest_whole_file_sha256
            ),
            manifest_id=args.manifest_id,
            authorization_path=args.authorization,
            reviewed_authorization_whole_file_sha256=(
                args.reviewed_authorization_whole_file_sha256
            ),
            authorization_id=args.authorization_id,
            dispatch_id=args.dispatch_id,
            run_id=args.run_id,
            actor=args.actor,
        )
    except DispatchWriterError as exc:
        parser.exit(2, f"dispatch writer stopped: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
