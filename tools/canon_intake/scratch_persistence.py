"""Deterministic, non-canonical persistence for dispatch-bound runner output."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from tools.canon_intake.dispatch_authorization_writer import (
    _AnchoredDirectory,
    _write_all,
)


class ScratchPersistenceError(ValueError):
    """Raised when provisional scratch output cannot be persisted exactly."""


@dataclass(frozen=True)
class ProvisionalResultTarget:
    """One validated dispatch-bound provisional-result target."""

    scratch_run_directory: str
    provisional_result_path: str
    parent_relative: Path
    file_name: str


def _digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _is_link_or_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except OSError:
        return False
    return bool(attributes & getattr(os.stat_result, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _repo_root(repo_root: Path) -> Path:
    selected = Path(repo_root)
    lexical = selected if selected.is_absolute() else Path.cwd() / selected
    if not lexical.is_dir() or _is_link_or_reparse(lexical):
        raise ScratchPersistenceError("repository root must be a regular non-reparse directory")
    try:
        return lexical.resolve(strict=True)
    except OSError as exc:
        raise ScratchPersistenceError("repository root is unavailable") from exc


def _posix_parts(value: Any, *, label: str, directory: bool) -> tuple[str, ...]:
    if not isinstance(value, str) or not value:
        raise ScratchPersistenceError(f"{label} must be one non-empty repo POSIX path")
    if "\\" in value or PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute():
        raise ScratchPersistenceError(f"{label} must be one relative repo POSIX path")
    if directory:
        if not value.endswith("/"):
            raise ScratchPersistenceError(f"{label} must end with /")
        lexical = value[:-1]
    else:
        if value.endswith("/"):
            raise ScratchPersistenceError(f"{label} must name one file")
        lexical = value
    parts = tuple(lexical.split("/"))
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ScratchPersistenceError(f"{label} contains an unsafe path component")
    return parts


def _target_from_dispatch(dispatch: Mapping[str, Any]) -> ProvisionalResultTarget:
    if not isinstance(dispatch, Mapping):
        raise ScratchPersistenceError("dispatch must be one validated mapping")
    outputs = dispatch.get("output_targets")
    if not isinstance(outputs, Mapping):
        raise ScratchPersistenceError("dispatch output_targets must be one mapping")
    scratch_value = outputs.get("scratch_run_directory")
    scratch_parts = _posix_parts(
        scratch_value,
        label="scratch_run_directory",
        directory=True,
    )
    if scratch_parts[0] != "scratch":
        raise ScratchPersistenceError("scratch_run_directory must remain under scratch/")
    provisional_values = outputs.get("provisional_result_paths")
    if not isinstance(provisional_values, list) or len(provisional_values) != 1:
        raise ScratchPersistenceError("dispatch must bind exactly one provisional result path")
    provisional_value = provisional_values[0]
    provisional_parts = _posix_parts(
        provisional_value,
        label="provisional_result_paths[0]",
        directory=False,
    )
    if (
        len(provisional_parts) <= len(scratch_parts)
        or provisional_parts[: len(scratch_parts)] != scratch_parts
    ):
        raise ScratchPersistenceError(
            "provisional result must be underneath the dispatch-bound scratch directory"
        )
    return ProvisionalResultTarget(
        scratch_run_directory=scratch_value,
        provisional_result_path=provisional_value,
        parent_relative=Path(*provisional_parts[:-1]),
        file_name=provisional_parts[-1],
    )


def _require_safe_existing_components(root: Path, target: ProvisionalResultTarget) -> None:
    current = root
    for component in (*target.parent_relative.parts, target.file_name):
        current = current / component
        if not os.path.lexists(os.fspath(current)):
            break
        if _is_link_or_reparse(current):
            raise ScratchPersistenceError(
                f"provisional output path contains a symlink or reparse component: {component}"
            )
        if component != target.file_name and not current.is_dir():
            raise ScratchPersistenceError(
                f"provisional output parent component is not a directory: {component}"
            )
    final = root / target.parent_relative / target.file_name
    if os.path.lexists(os.fspath(final)):
        raise ScratchPersistenceError("provisional result already exists; overwrite is forbidden")


def preflight_provisional_result_target(
    *,
    repo_root: Path,
    dispatch: Mapping[str, Any],
) -> ProvisionalResultTarget:
    """Validate one dispatch target without creating a directory or file."""

    root = _repo_root(repo_root)
    target = _target_from_dispatch(dispatch)
    _require_safe_existing_components(root, target)
    return target


def serialize_provisional_result(runner_output: Mapping[str, Any]) -> bytes:
    """Return deterministic UTF-8 JSON that round-trips to the complete mapping."""

    if not isinstance(runner_output, Mapping):
        raise ScratchPersistenceError("runner_output must be one mapping")
    materialized = dict(runner_output)
    try:
        raw = (
            json.dumps(
                materialized,
                allow_nan=False,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
            + b"\n"
        )
        decoded = json.loads(raw)
    except (TypeError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        raise ScratchPersistenceError("runner_output is not deterministic finite JSON") from exc
    if decoded != materialized:
        raise ScratchPersistenceError("runner_output does not round-trip through JSON exactly")
    return raw


def _ensure_parent_directories(root: Path, relative: Path) -> None:
    current = root
    for component in relative.parts:
        current = current / component
        try:
            current.mkdir()
        except FileExistsError:
            pass
        except OSError as exc:
            raise ScratchPersistenceError(
                f"could not create provisional output parent: {component}"
            ) from exc
        if _is_link_or_reparse(current) or not current.is_dir():
            raise ScratchPersistenceError(
                f"provisional output parent is redirected or not a directory: {component}"
            )


def persist_provisional_result(
    *,
    repo_root: Path,
    dispatch: Mapping[str, Any],
    runner_output: Mapping[str, Any],
) -> dict[str, Any]:
    """Exclusively persist exactly one dispatch-bound non-canonical result."""

    root = _repo_root(repo_root)
    target = _target_from_dispatch(dispatch)
    _require_safe_existing_components(root, target)
    raw = serialize_provisional_result(runner_output)
    _ensure_parent_directories(root, target.parent_relative)

    parent: _AnchoredDirectory | None = None
    opened = None
    try:
        parent = _AnchoredDirectory(
            root=root,
            relative=target.parent_relative,
            label="provisional scratch parent",
        )
        parent.require_absent(target.file_name)
        opened = parent.create(target.file_name)
        if opened.fd is None:
            raise OSError("anchored provisional result is closed")
        _write_all(opened.fd, raw)
        opened.fsync()
        if opened.read() != raw:
            raise OSError("provisional result post-write reread mismatch")
        parent.verify_reference(
            target.file_name,
            expected_identity=opened.identity,
            expected_raw=raw,
        )
        parent.fsync()
        parent.assert_current()
    except Exception as exc:
        cleanup_error: Exception | None = None
        if opened is not None:
            try:
                opened.delete()
            except Exception as cleanup_exc:  # noqa: BLE001 - preserve both failures
                cleanup_error = cleanup_exc
        error = ScratchPersistenceError(
            "provisional result exclusive create/write/durability verification failed"
        )
        if cleanup_error is not None:
            error.cleanup_error = cleanup_error  # type: ignore[attr-defined]
        raise error from exc
    finally:
        if opened is not None:
            opened.close()
        if parent is not None:
            parent.close()

    return {
        "provisional_result_path": target.provisional_result_path,
        "byte_length": len(raw),
        "sha256": _digest(raw),
        "serialization": "utf8_sorted_compact_json_with_final_lf_v1",
        "non_authority": {
            "non_canonical_scratch_only": True,
            "not_result_population_authority": True,
            "not_evidence_or_decision_authority": True,
            "not_runtime_paper_live_or_capital_authority": True,
        },
    }
