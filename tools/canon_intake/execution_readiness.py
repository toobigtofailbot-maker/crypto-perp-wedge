"""Zero-effect readiness checks for one exact protected execution request.

This module has no execution authority.  It does not invoke the runner, append
an execution event, bootstrap a directory, or persist any output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from tools.canon_intake import execution_event_writer, execution_runner_adapter
from tools.canon_intake.dispatch_authorization_writer import _AnchoredDirectory
from tools.canon_intake.execution_event import (
    EXECUTION_ROOT,
    EXECUTION_WRITER_INTEGRITY_ROOT,
    read_and_validate_execution_stream,
)
from tools.canon_intake.execution_event_writer import LOCK_ROOT
from tools.canon_intake.scratch_persistence import preflight_provisional_result_target
from tools.research_runner import run_offline_sweep as offline_runner

EXPECTED_LEASE_LABELS = (
    "dispatch record",
    "dispatch manifest",
    "runner source",
    "strategy spec",
    "variant manifest",
    "sweep plan",
    "funding provenance",
    "funding data",
    "dataset catalog",
    "dispatch dataset",
    "dataset validator",
)
FIXTURE_PARITY = (
    {
        "setup": "execution stream parent exists before writer/adapter call",
        "classification": "REQUIRED IN REAL WORKTREE",
        "coverage": "execution_stream_parent",
    },
    {
        "setup": "execution-writer integrity parent exists before writer/adapter call",
        "classification": "REQUIRED IN REAL WORKTREE",
        "coverage": "execution_writer_integrity_parent",
    },
    {
        "setup": "execution-event schema copied into a synthetic repository",
        "classification": "TEST-ONLY",
        "coverage": "dispatch_and_stream_validation",
    },
    {
        "setup": "synthetic bound artifacts and Git history are provisioned",
        "classification": "TEST-ONLY",
        "coverage": "dispatch_and_leased_input_validation",
    },
)


class ExecutionReadinessError(ValueError):
    """Raised only when the readiness request itself is malformed."""


def _digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _normalized_digest(value: str, label: str) -> str:
    if not isinstance(value, str):
        raise ExecutionReadinessError(f"{label} must be a SHA-256 string")
    normalized = value if value.startswith("sha256:") else f"sha256:{value}"
    if len(normalized) != 71:
        raise ExecutionReadinessError(f"{label} must be one exact SHA-256")
    try:
        int(normalized.removeprefix("sha256:"), 16)
    except ValueError as exc:
        raise ExecutionReadinessError(f"{label} must be one exact SHA-256") from exc
    return normalized.lower()


def _is_link_or_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except OSError:
        return False
    return bool(attributes & getattr(os.stat_result, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _safe_repo_path(root: Path, value: str | Path, label: str) -> Path:
    selected = Path(value)
    candidate = selected if selected.is_absolute() else root / selected
    try:
        candidate.absolute().relative_to(root)
    except ValueError as exc:
        raise ExecutionReadinessError(f"{label} escapes repository root") from exc
    relative = candidate.absolute().relative_to(root)
    if any(part in {"", ".", ".."} for part in relative.parts):
        raise ExecutionReadinessError(f"{label} contains an unsafe path component")
    current = root
    for component in relative.parts:
        current /= component
        if os.path.lexists(os.fspath(current)) and _is_link_or_reparse(current):
            raise ExecutionReadinessError(f"{label} contains a symlink or reparse component")
    return candidate.absolute()


def _check(
    checks: list[dict[str, Any]],
    *,
    check_id: str,
    passed: bool,
    subject: str,
    expected: Any,
    actual: Any,
    reason: str,
    bootstrap_candidate: bool = False,
) -> None:
    row: dict[str, Any] = {
        "check_id": check_id,
        "status": "pass" if passed else "fail",
        "subject": subject,
        "expected": expected,
        "actual": actual,
        "blocking": not passed,
        "reason": reason,
    }
    if bootstrap_candidate:
        row["bootstrap_candidate"] = True
        row["bootstrap_object"] = "empty ordinary directory"
    checks.append(row)


def _anchored_directory_check(
    checks: list[dict[str, Any]],
    *,
    root: Path,
    relative: Path,
    check_id: str,
    label: str,
    allow_bootstrap_candidate: bool = False,
) -> bool:
    exact = root / relative
    anchor: _AnchoredDirectory | None = None
    try:
        anchor = _AnchoredDirectory(root=root, relative=relative, label=label)
        anchor.assert_current()
    except Exception as exc:  # noqa: BLE001 - convert filesystem failures to findings
        bootstrap_candidate = False
        if allow_bootstrap_candidate and not os.path.lexists(os.fspath(exact)):
            parent: _AnchoredDirectory | None = None
            try:
                parent = _AnchoredDirectory(
                    root=root,
                    relative=relative.parent,
                    label=f"{label} bootstrap parent",
                )
                parent.assert_current()
                bootstrap_candidate = relative == EXECUTION_ROOT
            except Exception:  # noqa: BLE001 - failure means no safe-bootstrap classification
                bootstrap_candidate = False
            finally:
                if parent is not None:
                    parent.close()
        _check(
            checks,
            check_id=check_id,
            passed=False,
            subject=relative.as_posix(),
            expected="existing ordinary non-reparse directory; descriptor anchor opens",
            actual="missing" if not os.path.lexists(os.fspath(exact)) else str(exc),
            reason=f"{label} is not physically ready: {exc}",
            bootstrap_candidate=bootstrap_candidate,
        )
        return False
    finally:
        if anchor is not None:
            anchor.close()
    _check(
        checks,
        check_id=check_id,
        passed=True,
        subject=relative.as_posix(),
        expected="existing ordinary non-reparse directory; descriptor anchor opens",
        actual="descriptor-anchored open and identity recheck succeeded",
        reason=f"{label} is physically ready",
    )
    return True


def _source_identity(
    checks: list[dict[str, Any]],
    *,
    root: Path,
    check_id: str,
    path: str,
    expected_sha256: str,
    expected_version: str | None = None,
    actual_version: str | None = None,
) -> None:
    selected = root / Path(path)
    try:
        raw = selected.read_bytes()
        actual_sha = _digest(raw)
        ordinary = selected.is_file() and not _is_link_or_reparse(selected)
    except OSError as exc:
        actual_sha = f"unavailable: {exc}"
        ordinary = False
    passed = ordinary and actual_sha == expected_sha256
    if expected_version is not None:
        passed = passed and actual_version == expected_version
    _check(
        checks,
        check_id=check_id,
        passed=passed,
        subject=path,
        expected={"sha256": expected_sha256, "version": expected_version},
        actual={"sha256": actual_sha, "version": actual_version, "ordinary_file": ordinary},
        reason="executable identity matches" if passed else "executable identity mismatch",
    )


def _git_local_data_state(root: Path, relative: str) -> dict[str, Any]:
    ignored = _run_git(root, "check-ignore", "-q", "--", relative).returncode == 0
    tracked = _run_git(root, "ls-files", "--error-unmatch", "--", relative).returncode == 0
    staged = bool(_run_git(root, "diff", "--cached", "--name-only", "--", relative).stdout.strip())
    return {"gitignored": ignored, "tracked": tracked, "staged": staged}


def _data_check(
    checks: list[dict[str, Any]],
    *,
    root: Path,
    check_id: str,
    path: str,
    expected_sha256: str,
    expected_byte_length: int,
) -> None:
    selected = root / Path(path)
    try:
        raw = selected.read_bytes()
        actual_identity: dict[str, Any] = {
            "sha256": _digest(raw),
            "byte_length": len(raw),
            "ordinary_file": selected.is_file() and not _is_link_or_reparse(selected),
        }
    except OSError as exc:
        actual_identity = {
            "sha256": None,
            "byte_length": None,
            "ordinary_file": False,
            "error": str(exc),
        }
    git_state = _git_local_data_state(root, path)
    actual = {**actual_identity, **git_state}
    expected = {
        "sha256": expected_sha256,
        "byte_length": expected_byte_length,
        "ordinary_file": True,
        "gitignored": True,
        "tracked": False,
        "staged": False,
    }
    passed = actual == expected
    _check(
        checks,
        check_id=check_id,
        passed=passed,
        subject=path,
        expected=expected,
        actual=actual,
        reason="local canonical data identity and Git posture match"
        if passed
        else ("local canonical data identity or Git posture mismatch"),
    )


def _load_manifest(root: Path, dispatch: Mapping[str, Any]) -> Mapping[str, Any]:
    binding = dispatch["manifest_derivation"]
    path = _safe_repo_path(root, binding["manifest_path"], "dispatch manifest")
    raw = path.read_bytes()
    if _digest(raw) != binding["manifest_whole_file_sha256"]:
        raise ExecutionReadinessError("dispatch manifest bytes differ from dispatch binding")
    if len(raw) != binding["manifest_byte_length"]:
        raise ExecutionReadinessError("dispatch manifest length differs from dispatch binding")
    value = json.loads(raw)
    if not isinstance(value, Mapping):
        raise ExecutionReadinessError("dispatch manifest is not one JSON object")
    return value


def check_execution_readiness(
    *,
    repo_root: Path,
    dispatch_path: Path,
    reviewed_dispatch_whole_file_sha256: str,
    run_id: str,
    stream_path: str,
    actor_id: str,
    expected_runner_version: str,
    expected_runner_source_sha256: str,
    expected_adapter_version: str,
    expected_adapter_source_sha256: str,
    expected_scratch_source_sha256: str,
    expected_writer_source_sha256: str,
    result_population_id: str,
    expected_head: str | None = None,
    require_clean: bool = False,
    expected_python_executable: Path | None = None,
    require_virtual_environment: bool = False,
) -> dict[str, Any]:
    """Return zero-effect readiness findings for one exact first-run request."""

    expected_dispatch_sha = _normalized_digest(
        reviewed_dispatch_whole_file_sha256, "reviewed dispatch whole-file SHA-256"
    )
    expected_runner_sha = _normalized_digest(expected_runner_source_sha256, "runner source SHA-256")
    expected_adapter_sha = _normalized_digest(
        expected_adapter_source_sha256, "adapter source SHA-256"
    )
    expected_scratch_sha = _normalized_digest(
        expected_scratch_source_sha256, "scratch source SHA-256"
    )
    expected_writer_sha = _normalized_digest(expected_writer_source_sha256, "writer source SHA-256")
    if not all(isinstance(value, str) and value for value in (run_id, stream_path, actor_id)):
        raise ExecutionReadinessError("run_id, stream_path, and actor_id must be explicit")
    if not isinstance(result_population_id, str) or not result_population_id:
        raise ExecutionReadinessError("result_population_id must be explicit")

    checks: list[dict[str, Any]] = []
    lexical_root = Path(repo_root).absolute()
    root_ready = lexical_root.is_dir() and not _is_link_or_reparse(lexical_root)
    resolved_root = lexical_root.resolve() if root_ready else lexical_root
    _check(
        checks,
        check_id="repo_root",
        passed=root_ready,
        subject=str(lexical_root),
        expected="existing ordinary non-reparse directory",
        actual={
            "is_directory": lexical_root.is_dir(),
            "redirected": _is_link_or_reparse(lexical_root),
        },
        reason="repository root is ordinary"
        if root_ready
        else "repository root is unavailable or redirected",
    )
    if not root_ready:
        return _result(checks)
    root = resolved_root

    head_result = _run_git(root, "rev-parse", "HEAD")
    current_head = head_result.stdout.strip() if head_result.returncode == 0 else None
    head_passed = current_head is not None and (
        expected_head is None or current_head == expected_head
    )
    _check(
        checks,
        check_id="git_head",
        passed=head_passed,
        subject="HEAD",
        expected=expected_head or "visible current HEAD",
        actual=current_head or head_result.stderr.strip(),
        reason="current HEAD is visible and matches"
        if head_passed
        else "current HEAD is unavailable or differs",
    )
    status = _run_git(root, "status", "--porcelain=v1", "--untracked-files=no")
    clean = status.returncode == 0 and not status.stdout.strip()
    _check(
        checks,
        check_id="git_tracked_index_clean",
        passed=clean or not require_clean,
        subject=str(root),
        expected="clean tracked/index state"
        if require_clean
        else "cleanliness reported; not required",
        actual={"clean": clean, "porcelain": status.stdout.splitlines()},
        reason=(
            "tracked/index state satisfies request"
            if clean or not require_clean
            else "tracked/index state is dirty"
        ),
    )

    dispatch: Mapping[str, Any] | None = None
    dispatch_selected: Path | None = None
    dispatch_actual: dict[str, Any]
    try:
        dispatch_selected = _safe_repo_path(root, dispatch_path, "dispatch record")
        raw = dispatch_selected.read_bytes()
        dispatch = json.loads(raw)
        if not isinstance(dispatch, Mapping):
            raise ExecutionReadinessError("dispatch record is not one JSON object")
        dispatch_actual = {
            "path": dispatch_selected.relative_to(root).as_posix(),
            "sha256": _digest(raw),
            "byte_length": len(raw),
            "ordinary_file": dispatch_selected.is_file()
            and not _is_link_or_reparse(dispatch_selected),
        }
        dispatch_passed = (
            dispatch_actual["sha256"] == expected_dispatch_sha and dispatch_actual["ordinary_file"]
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ExecutionReadinessError) as exc:
        dispatch_actual = {"error": str(exc)}
        dispatch_passed = False
    _check(
        checks,
        check_id="dispatch_exact_bytes",
        passed=dispatch_passed,
        subject=str(dispatch_path),
        expected={"sha256": expected_dispatch_sha, "ordinary_file": True},
        actual=dispatch_actual,
        reason="dispatch exact bytes are present"
        if dispatch_passed
        else "dispatch exact bytes are unavailable or differ",
    )

    binding_passed = False
    if dispatch is not None:
        actual_binding = {
            "run_id": dispatch.get("run_binding", {}).get("run_id"),
            "stream_path": dispatch.get("run_binding", {}).get("execution_event_stream_path"),
            "output_stream_path": dispatch.get("output_targets", {}).get(
                "execution_event_stream_path"
            ),
            "dispatch_record_path": dispatch.get("dispatch_record_path"),
        }
        expected_binding = {
            "run_id": run_id,
            "stream_path": stream_path,
            "output_stream_path": stream_path,
            "dispatch_record_path": (
                dispatch_selected.relative_to(root).as_posix() if dispatch_selected else None
            ),
        }
        binding_passed = (
            actual_binding == expected_binding and Path(stream_path).parent == EXECUTION_ROOT
        )
    else:
        actual_binding = {"error": "dispatch unavailable"}
        expected_binding = {"run_id": run_id, "stream_path": stream_path}
    _check(
        checks,
        check_id="dispatch_run_stream_binding",
        passed=binding_passed,
        subject=str(dispatch_path),
        expected=expected_binding,
        actual=actual_binding,
        reason="dispatch binds the exact run and production stream"
        if binding_passed
        else ("dispatch run/stream/path binding mismatch"),
    )

    stream_validation: Mapping[str, Any] | None = None
    if dispatch_passed and binding_passed and dispatch_selected is not None:
        try:
            stream_validation = read_and_validate_execution_stream(
                repo_root=root,
                dispatch_path=dispatch_selected,
                reviewed_dispatch_whole_file_sha256=expected_dispatch_sha,
                allow_missing=True,
                require_terminal=False,
                scan_retained_history=True,
            )
            validator_passed = (
                stream_validation["valid"]
                and stream_validation["dispatch_validation"]["lifecycle_state"] == "consumed"
            )
            validator_actual: Any = {
                "valid": stream_validation["valid"],
                "lifecycle_state": stream_validation["dispatch_validation"]["lifecycle_state"],
                "stream_state": stream_validation["state"],
            }
        except Exception as exc:  # noqa: BLE001 - existing validators fail closed
            validator_passed = False
            validator_actual = str(exc)
    else:
        validator_passed = False
        validator_actual = "exact dispatch binding unavailable"
    _check(
        checks,
        check_id="dispatch_consumed_validation",
        passed=validator_passed,
        subject=str(dispatch_path),
        expected="existing validators accept exact dispatch and consumed KDAUTH lifecycle",
        actual=validator_actual,
        reason="dispatch/KDAUTH consumed state is valid"
        if validator_passed
        else ("dispatch/KDAUTH consumed state is not proven"),
    )

    _anchored_directory_check(
        checks,
        root=root,
        relative=EXECUTION_ROOT,
        check_id="execution_stream_parent",
        label="execution stream parent",
        allow_bootstrap_candidate=True,
    )
    lock_parent_ready = _anchored_directory_check(
        checks,
        root=root,
        relative=LOCK_ROOT,
        check_id="execution_lock_parent",
        label="execution append lock parent",
    )
    integrity_parent_ready = _anchored_directory_check(
        checks,
        root=root,
        relative=EXECUTION_WRITER_INTEGRITY_ROOT,
        check_id="execution_writer_integrity_parent",
        label="execution-writer integrity parent",
    )

    lock_relative = LOCK_ROOT / f".{run_id}.execution_event_append.lock"
    lock_exists = os.path.lexists(os.fspath(root / lock_relative))
    _check(
        checks,
        check_id="stale_execution_append_lock_absent",
        passed=lock_parent_ready and not lock_exists,
        subject=lock_relative.as_posix(),
        expected="absent",
        actual="present" if lock_exists else "absent",
        reason="no stale per-run append lock"
        if lock_parent_ready and not lock_exists
        else ("lock parent is unavailable or stale per-run append lock exists"),
    )

    residue = (
        sorted(path.name for path in (root / EXECUTION_WRITER_INTEGRITY_ROOT).glob(f"{run_id}-*"))
        if integrity_parent_ready
        else []
    )
    _check(
        checks,
        check_id="execution_writer_residue_absent",
        passed=integrity_parent_ready and not residue,
        subject=EXECUTION_WRITER_INTEGRITY_ROOT.as_posix(),
        expected={"run_id_prefix": f"{run_id}-", "matching_entries": []},
        actual={"matching_entries": residue},
        reason="no per-run writer residue"
        if integrity_parent_ready and not residue
        else ("integrity parent is unavailable or per-run writer residue exists"),
    )

    history = stream_validation.get("history_validation") if stream_validation else None
    stream_missing = bool(
        stream_validation
        and stream_validation.get("state") == "missing"
        and isinstance(history, Mapping)
        and history.get("current_exists") is False
        and history.get("retained_version_count") == 0
    )
    _check(
        checks,
        check_id="execution_stream_first_run_state",
        passed=stream_missing,
        subject=stream_path,
        expected={"state": "missing", "current_exists": False, "retained_version_count": 0},
        actual={
            "state": stream_validation.get("state") if stream_validation else None,
            "history": history,
        },
        reason="stream is in exact missing pre-run state"
        if stream_missing
        else ("stream is not proven to be in exact missing pre-run state"),
    )

    scratch_ready = False
    scratch_target: str | None = None
    if dispatch is not None:
        try:
            target = preflight_provisional_result_target(repo_root=root, dispatch=dispatch)
            scratch_target = target.provisional_result_path
            scratch_ready = True
            scratch_actual: Any = {
                "target": scratch_target,
                "exists": os.path.lexists(os.fspath(root / scratch_target)),
                "preflight": "production zero-effect preflight passed",
            }
        except Exception as exc:  # noqa: BLE001 - production preflight fails closed
            scratch_actual = str(exc)
    else:
        scratch_actual = "dispatch unavailable"
    _check(
        checks,
        check_id="scratch_provisional_preflight",
        passed=scratch_ready,
        subject=scratch_target or "dispatch output_targets.provisional_result_paths[0]",
        expected="production zero-effect preflight passes and target is absent",
        actual=scratch_actual,
        reason="scratch target is safe and absent"
        if scratch_ready
        else ("scratch target is not safe and absent"),
    )

    rp_root = root / "research/result_populations"
    rp_matches = sorted(
        path.relative_to(root).as_posix() for path in rp_root.glob(f"{result_population_id}*")
    )
    _check(
        checks,
        check_id="result_population_absent",
        passed=not rp_matches,
        subject=f"research/result_populations/{result_population_id}*",
        expected=[],
        actual=rp_matches,
        reason="no target Result Population exists"
        if not rp_matches
        else ("target Result Population evidence already exists"),
    )

    manifest: Mapping[str, Any] | None = None
    if dispatch is not None:
        try:
            manifest = _load_manifest(root, dispatch)
        except (OSError, UnicodeError, json.JSONDecodeError, ExecutionReadinessError):
            manifest = None
    if manifest is not None:
        dataset = manifest["dataset"]
        funding = manifest["funding"]
        _data_check(
            checks,
            root=root,
            check_id="canonical_dataset_local_identity",
            path=dataset["data_path"],
            expected_sha256=dataset["data_sha256"],
            expected_byte_length=dataset["data_byte_length"],
        )
        _data_check(
            checks,
            root=root,
            check_id="canonical_funding_local_identity",
            path=funding["funding_data_path"],
            expected_sha256=funding["funding_data_sha256"],
            expected_byte_length=funding["funding_data_byte_length"],
        )
    else:
        for check_id, subject in (
            ("canonical_dataset_local_identity", "dispatch manifest dataset binding"),
            ("canonical_funding_local_identity", "dispatch manifest funding binding"),
        ):
            _check(
                checks,
                check_id=check_id,
                passed=False,
                subject=subject,
                expected="exact ordinary gitignored/untracked/unstaged local data",
                actual="dispatch manifest unavailable",
                reason="local canonical data readiness is not proven",
            )

    leases_actual: Any
    leases_passed = False
    request = None
    if dispatch is not None and dispatch_selected is not None and dispatch_passed:
        try:
            request = execution_runner_adapter._prepare_runner_request(
                root,
                dispatch,
                dispatch_path=dispatch_selected,
                reviewed_dispatch_whole_file_sha256=expected_dispatch_sha,
            )
            labels = tuple(lease.label for lease in request.input_leases)
            identities = [
                {
                    "label": lease.label,
                    "path": lease.path.relative_to(root).as_posix(),
                    "sha256": _digest(lease.raw),
                }
                for lease in request.input_leases
            ]
            request.close_input_leases()
            released = all(lease.stream.closed for lease in request.input_leases)
            leases_passed = labels == EXPECTED_LEASE_LABELS and released
            leases_actual = {
                "count": len(labels),
                "labels": list(labels),
                "released": released,
                "identities": identities,
            }
        except Exception as exc:  # noqa: BLE001 - real preparation fails closed
            leases_actual = str(exc)
        finally:
            if request is not None:
                request.close_input_leases()
    else:
        leases_actual = "exact dispatch unavailable"
    _check(
        checks,
        check_id="leased_input_preparation",
        passed=leases_passed,
        subject="execution_runner_adapter._prepare_runner_request",
        expected={"count": 11, "labels": list(EXPECTED_LEASE_LABELS), "released": True},
        actual=leases_actual,
        reason="all exact leased inputs prepared and released"
        if leases_passed
        else ("all exact leased inputs were not prepared and released"),
    )

    _source_identity(
        checks,
        root=root,
        check_id="runner_executable_identity",
        path=execution_runner_adapter.RUNNER_SOURCE_PATH,
        expected_sha256=expected_runner_sha,
        expected_version=expected_runner_version,
        actual_version=offline_runner.RUNNER_VERSION,
    )
    _source_identity(
        checks,
        root=root,
        check_id="adapter_executable_identity",
        path=execution_runner_adapter.ADAPTER_SOURCE_PATH,
        expected_sha256=expected_adapter_sha,
        expected_version=expected_adapter_version,
        actual_version=execution_runner_adapter.ADAPTER_VERSION,
    )
    _source_identity(
        checks,
        root=root,
        check_id="scratch_persistence_identity",
        path="tools/canon_intake/scratch_persistence.py",
        expected_sha256=expected_scratch_sha,
    )
    _source_identity(
        checks,
        root=root,
        check_id="execution_event_writer_identity",
        path="tools/canon_intake/execution_event_writer.py",
        expected_sha256=expected_writer_sha,
    )
    _check(
        checks,
        check_id="execution_actor_identity",
        passed=actor_id == "codex-execution-runner",
        subject="actor_id",
        expected="codex-execution-runner",
        actual=actor_id,
        reason="explicit execution actor matches"
        if actor_id == "codex-execution-runner"
        else ("explicit execution actor differs"),
    )

    current_python = Path(sys.executable).resolve()
    expected_python = (
        Path(expected_python_executable).resolve()
        if expected_python_executable is not None
        else current_python
    )
    virtual_environment = sys.prefix != sys.base_prefix
    runtime_passed = (
        current_python == expected_python
        and (virtual_environment or not require_virtual_environment)
        and callable(offline_runner.run_offline_sweep)
        and callable(execution_runner_adapter.run_consumed_dispatch)
        and callable(execution_event_writer.write_execution_event)
        and callable(preflight_provisional_result_target)
    )
    _check(
        checks,
        check_id="runtime_import_prerequisites",
        passed=runtime_passed,
        subject=str(current_python),
        expected={
            "python_executable": str(expected_python),
            "virtual_environment": True if require_virtual_environment else "reported",
            "required_repo_imports": "callable",
            "network_required": False,
        },
        actual={
            "python_executable": str(current_python),
            "virtual_environment": virtual_environment,
            "required_repo_imports": "callable" if runtime_passed else "unavailable",
            "network_required": False,
            "python_version": sys.version.split()[0],
        },
        reason="production imports are loaded with no network prerequisite"
        if runtime_passed
        else ("production imports are not ready"),
    )

    parity_passed = {
        row["coverage"]
        for row in FIXTURE_PARITY
        if row["classification"] == "REQUIRED IN REAL WORKTREE"
    } == {
        "execution_stream_parent",
        "execution_writer_integrity_parent",
    }
    _check(
        checks,
        check_id="fixture_to_production_parity",
        passed=parity_passed,
        subject="execution writer/adapter fixture setup",
        expected="all real-worktree prerequisites mechanically covered",
        actual=list(FIXTURE_PARITY),
        reason="fixture setup is explicitly classified and covered"
        if parity_passed
        else ("fixture setup parity coverage is incomplete"),
    )

    prior_effects_absent = (
        stream_missing and scratch_ready and not rp_matches and not lock_exists and not residue
    )
    _check(
        checks,
        check_id="prior_protected_effect_absence",
        passed=prior_effects_absent,
        subject=run_id,
        expected={
            "durable_execution_event": False,
            "runner_start_evidence": False,
            "scratch_or_provisional": False,
            "result_population": False,
            "stale_lock": False,
            "writer_residue": False,
        },
        actual={
            "stream_missing": stream_missing,
            "scratch_preflight_passed": scratch_ready,
            "result_population_matches": rp_matches,
            "stale_lock": lock_exists,
            "writer_residue": residue,
        },
        reason="no prior protected execution effect is visible"
        if prior_effects_absent
        else ("prior-effect absence is not fully proven"),
    )
    return _result(checks)


def _result(checks: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    blocking = [dict(row) for row in checks if row["blocking"]]
    return {
        "ready": not blocking,
        "checks": [dict(row) for row in checks],
        "blocking_findings": blocking,
        "non_authority": True,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--dispatch-path", type=Path, required=True)
    parser.add_argument("--dispatch-sha256", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--stream-path", required=True)
    parser.add_argument("--actor-id", required=True)
    parser.add_argument("--runner-version", required=True)
    parser.add_argument("--runner-sha256", required=True)
    parser.add_argument("--adapter-version", required=True)
    parser.add_argument("--adapter-sha256", required=True)
    parser.add_argument("--scratch-sha256", required=True)
    parser.add_argument("--writer-sha256", required=True)
    parser.add_argument("--result-population-id", required=True)
    parser.add_argument("--expected-head")
    parser.add_argument("--require-clean", action="store_true")
    parser.add_argument("--expected-python-executable", type=Path)
    parser.add_argument("--require-virtual-environment", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = check_execution_readiness(
            repo_root=args.repo_root,
            dispatch_path=args.dispatch_path,
            reviewed_dispatch_whole_file_sha256=args.dispatch_sha256,
            run_id=args.run_id,
            stream_path=args.stream_path,
            actor_id=args.actor_id,
            expected_runner_version=args.runner_version,
            expected_runner_source_sha256=args.runner_sha256,
            expected_adapter_version=args.adapter_version,
            expected_adapter_source_sha256=args.adapter_sha256,
            expected_scratch_source_sha256=args.scratch_sha256,
            expected_writer_source_sha256=args.writer_sha256,
            result_population_id=args.result_population_id,
            expected_head=args.expected_head,
            require_clean=args.require_clean,
            expected_python_executable=args.expected_python_executable,
            require_virtual_environment=args.require_virtual_environment,
        )
    except (ExecutionReadinessError, OSError, KeyError, TypeError, ValueError) as exc:
        print(
            json.dumps({"error": str(exc), "ready": False, "non_authority": True}, sort_keys=True)
        )
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
