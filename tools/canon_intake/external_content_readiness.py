"""Protected immutable writer and validator for H-004 Strategy Spec content readiness.

This module creates no dispatch, execution, runner, or Result Population record.
Production scope is intentionally closed to STRAT-SPEC-0007.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, Iterator, Mapping

from jsonschema import Draft7Validator, FormatChecker

from tools.registry.validate_variant_sweep_artifacts import canonical_json_bytes


PRODUCTION_SPEC_ID = "STRAT-SPEC-0007"
PRODUCTION_SPEC_PATH = Path(
    "research/strategy_specs/STRAT-SPEC-0007.strategy_spec.json"
)
PRODUCTION_FACT_ID = "SS-ECR-STRAT-SPEC-0007"
PRODUCTION_FACT_PATH = Path(
    "research/strategy_spec_external_content_readiness/"
    "SS-ECR-STRAT-SPEC-0007.external_content_readiness.json"
)
FACT_ROOT = Path("research/strategy_spec_external_content_readiness")
LOCK_PATH = FACT_ROOT / ".external_content_readiness.lock"
SCHEMA_PATH = Path(
    "research/schemas/strategy_spec_external_content_readiness.schema.json"
)
CANONICALIZER_IDENTITY = "strategy_spec_vm_parent_lineage_canonicalizer"
CANONICALIZER_PATH = Path("tools/registry/validate_variant_sweep_artifacts.py")
CANONICALIZATION = "repo_canonical_json_v1"
WRITER_VERSION = "strategy_spec_external_content_readiness_writer_v1"

LOCKED_SPEC_RAW_LENGTH = 19880
LOCKED_SPEC_RAW_SHA256 = (
    "sha256:b23ebc1093df51b7fab5e39c46fd2b96b5e71d35300134eb319a5cbc32d0857c"
)
LOCKED_SPEC_CANONICAL_SHA256 = (
    "sha256:8b6f7dd7a3e12b934c1038ae113aa25aa79f0b3cc6a336b25bd58164f5cc92db"
)
LOCKED_SPEC_BLOB_SHA = "ac5a493cb5b7d1a5de3647df07bd3151a8e4a440"
LOCKED_VM_SHA256 = (
    "sha256:822da9ca46eca4f3a9d4d86936fdd3447004ef77806fc3ce60ab0cf979ea171d"
)
LOCKED_SWEEP_SHA256 = (
    "sha256:66d48ec6d57048012dcd243ca7dda25dcf59241b1a3733dc05796eb46d7af2f0"
)


class ExternalContentReadinessError(ValueError):
    """Raised when the protected crossing must fail closed."""


class ExternalContentReadinessIntegrityCriticalError(ExternalContentReadinessError):
    """Raised after a partial crossing or failed lock cleanup requires inspection."""


def _sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def _issue(
    issue_type: str,
    *,
    source_field: str,
    expected_value: Any,
    actual_value: Any,
    fact_id: str | None = None,
) -> dict[str, Any]:
    return {
        "issue_type": issue_type,
        "strategy_spec_id": PRODUCTION_SPEC_ID,
        "fact_id": fact_id,
        "source_field": source_field,
        "expected_value": None if expected_value is None else str(expected_value),
        "actual_value": None if actual_value is None else str(actual_value),
    }


def _lexical_absolute(repo_root: Path, path: Path) -> Path:
    return path.absolute() if path.is_absolute() else (repo_root / path).absolute()


def _reject_symlink_components(repo_root: Path, path: Path, label: str) -> Path:
    root = repo_root.absolute()
    candidate = _lexical_absolute(root, path)
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise ExternalContentReadinessError(f"{label} escapes the repository") from exc
    current = root
    if current.is_symlink():
        raise ExternalContentReadinessError(f"{label} repository root is a symlink")
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ExternalContentReadinessError(
                f"{label} contains a symlinked path component: {current}"
            )
    return candidate


def _repo_path(repo_root: Path, value: str, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ExternalContentReadinessError(
            f"{label} must be a non-empty repo-relative POSIX path"
        )
    posix = PurePosixPath(value)
    if posix.is_absolute() or ".." in posix.parts or "." in posix.parts:
        raise ExternalContentReadinessError(f"{label} is not path-confined")
    return _reject_symlink_components(
        repo_root, repo_root.joinpath(*posix.parts), label
    )


def _regular_file(repo_root: Path, path: Path, label: str) -> Path:
    candidate = _reject_symlink_components(repo_root, path, label)
    if candidate.is_symlink() or not candidate.is_file():
        raise ExternalContentReadinessError(
            f"{label} must be a regular non-symlink file"
        )
    return candidate


def _load_object(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExternalContentReadinessError(
            f"{label} is not exactly one readable UTF-8 JSON value"
        ) from exc
    if not isinstance(value, dict):
        raise ExternalContentReadinessError(f"{label} root must be a JSON object")
    return value, raw


def _git(repo_root: Path, *args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if check and completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise ExternalContentReadinessError(
            f"Git verification failed for {' '.join(args)}: {detail}"
        )
    return completed.stdout.strip()


def _git_blob_at(repo_root: Path, commit: str, path: Path) -> str:
    output = _git(repo_root, "ls-tree", commit, "--", path.as_posix())
    lines = [line for line in output.splitlines() if line]
    if len(lines) != 1 or "\t" not in lines[0]:
        raise ExternalContentReadinessError(
            f"source Git commit does not contain exactly {path.as_posix()}"
        )
    metadata, actual_path = lines[0].split("\t", 1)
    parts = metadata.split()
    if len(parts) != 3 or parts[1] != "blob" or actual_path != path.as_posix():
        raise ExternalContentReadinessError("source Git tree binding is malformed")
    return parts[2]


def _is_ancestor(repo_root: Path, ancestor: str, descendant: str) -> bool:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if completed.returncode not in (0, 1):
        raise ExternalContentReadinessError("source Git ancestry check failed")
    return completed.returncode == 0


def _schema_errors(repo_root: Path, fact: Mapping[str, Any]) -> list[str]:
    schema_file = _regular_file(repo_root, repo_root / SCHEMA_PATH, "fact schema")
    schema, _ = _load_object(schema_file, "fact schema")
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    messages: list[str] = []
    for error in sorted(validator.iter_errors(fact), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path)
        messages.append(f"{location}: {error.message}" if location else error.message)
    return messages


def _history_paths_and_blobs(repo_root: Path) -> dict[str, set[str]]:
    commits = _git(
        repo_root, "rev-list", "--all", "--", FACT_ROOT.as_posix(), check=False
    )
    paths: dict[str, set[str]] = {}
    for commit in commits.splitlines():
        tree = _git(
            repo_root,
            "ls-tree",
            "-r",
            commit,
            "--",
            FACT_ROOT.as_posix(),
        )
        for line in tree.splitlines():
            if not line or "\t" not in line:
                continue
            metadata, path = line.split("\t", 1)
            parts = metadata.split()
            if len(parts) == 3 and parts[1] == "blob":
                paths.setdefault(path, set()).add(parts[2])
    return paths


def _current_fact_files(repo_root: Path) -> tuple[list[Path], list[dict[str, Any]]]:
    root = _reject_symlink_components(repo_root, repo_root / FACT_ROOT, "fact root")
    issues: list[dict[str, Any]] = []
    if not root.exists():
        return [], issues
    if root.is_symlink() or not root.is_dir():
        issues.append(
            _issue(
                "external_content_readiness_fact_root_invalid",
                source_field="fact_root",
                expected_value="regular non-symlink directory",
                actual_value=str(root),
            )
        )
        return [], issues
    files: list[Path] = []
    for child in sorted(root.iterdir()):
        if child.name == LOCK_PATH.name:
            continue
        if child.is_symlink() or not child.is_file():
            issues.append(
                _issue(
                    "external_content_readiness_unexpected_path",
                    source_field="fact_path",
                    expected_value=PRODUCTION_FACT_PATH.as_posix(),
                    actual_value=child.relative_to(repo_root).as_posix(),
                )
            )
            continue
        files.append(child)
    return files, issues


def _validate_fact(
    *,
    repo_root: Path,
    fact: Mapping[str, Any],
    fact_raw: bytes,
    actual_path: Path,
    require_source_commit_head: bool,
) -> list[dict[str, Any]]:
    fact_id = fact.get("fact_id") if isinstance(fact.get("fact_id"), str) else None
    issues: list[dict[str, Any]] = []
    for message in _schema_errors(repo_root, fact):
        issues.append(
            _issue(
                "external_content_readiness_schema_violation",
                fact_id=fact_id,
                source_field="schema",
                expected_value="Draft 7 valid readiness fact",
                actual_value=message,
            )
        )
    if issues:
        return issues

    spec = fact["strategy_spec"]
    expected_path = PRODUCTION_FACT_PATH.as_posix()
    exact = {
        "fact_id": (fact["fact_id"], PRODUCTION_FACT_ID),
        "fact_path": (fact["fact_path"], expected_path),
        "scope": (fact["scope"], "h004_dispatch_external_content_readiness"),
        "strategy_spec.strategy_spec_id": (
            spec["strategy_spec_id"],
            PRODUCTION_SPEC_ID,
        ),
        "strategy_spec.path": (spec["path"], PRODUCTION_SPEC_PATH.as_posix()),
    }
    actual_repo_path = actual_path.relative_to(repo_root).as_posix()
    exact["actual_path"] = (actual_repo_path, expected_path)
    for field, (actual, expected) in exact.items():
        if actual != expected:
            issues.append(
                _issue(
                    "external_content_readiness_identity_mismatch",
                    fact_id=fact_id,
                    source_field=field,
                    expected_value=expected,
                    actual_value=actual,
                )
            )
    if issues:
        return issues

    try:
        spec_path = _regular_file(
            repo_root, repo_root / PRODUCTION_SPEC_PATH, "Strategy Spec source"
        )
        spec_payload, spec_raw = _load_object(spec_path, "Strategy Spec source")
    except ExternalContentReadinessError as exc:
        return [
            _issue(
                "external_content_readiness_source_invalid",
                fact_id=fact_id,
                source_field="strategy_spec.path",
                expected_value=PRODUCTION_SPEC_PATH.as_posix(),
                actual_value=str(exc),
            )
        ]

    content = fact["content_binding"]
    canonical_hash = _sha256(canonical_json_bytes(spec_payload))
    source_checks = {
        "strategy_spec.strategy_spec_id": (
            spec_payload.get("strategy_spec_id"),
            PRODUCTION_SPEC_ID,
        ),
        "content_binding.raw_byte_length": (
            content["raw_byte_length"],
            len(spec_raw),
        ),
        "content_binding.raw_file_sha256": (
            content["raw_file_sha256"],
            _sha256(spec_raw),
        ),
        "content_binding.canonicalization": (
            content["canonicalization"],
            CANONICALIZATION,
        ),
        "content_binding.full_repo_canonical_json_sha256": (
            content["full_repo_canonical_json_sha256"],
            canonical_hash,
        ),
    }
    locked_checks = {
        "locked.raw_byte_length": (len(spec_raw), LOCKED_SPEC_RAW_LENGTH),
        "locked.raw_file_sha256": (_sha256(spec_raw), LOCKED_SPEC_RAW_SHA256),
        "locked.full_repo_canonical_json_sha256": (
            canonical_hash,
            LOCKED_SPEC_CANONICAL_SHA256,
        ),
        "locked.blob_sha": (_git_blob_sha(spec_raw), LOCKED_SPEC_BLOB_SHA),
    }
    for field, (actual, expected) in {**source_checks, **locked_checks}.items():
        if actual != expected:
            issues.append(
                _issue(
                    "external_content_readiness_content_mismatch",
                    fact_id=fact_id,
                    source_field=field,
                    expected_value=expected,
                    actual_value=actual,
                )
            )

    legacy = fact["legacy_internal_hash"]
    pinning = spec_payload.get("hash_pinning", {})
    legacy_checks = {
        "legacy_internal_hash.hash_status_observed": (
            legacy["hash_status_observed"],
            pinning.get("hash_status"),
        ),
        "legacy_internal_hash.hash_scope_version_observed": (
            legacy["hash_scope_version_observed"],
            pinning.get("hash_scope_version"),
        ),
        "legacy_internal_hash.canonical_spec_hash_observed": (
            legacy["canonical_spec_hash_observed"],
            pinning.get("canonical_spec_hash"),
        ),
        "legacy_internal_hash.legacy_hash_scope_reproducibility": (
            legacy["legacy_hash_scope_reproducibility"],
            "unresolved",
        ),
    }
    for field, (actual, expected) in legacy_checks.items():
        if actual != expected:
            issues.append(
                _issue(
                    "external_content_readiness_legacy_observation_mismatch",
                    fact_id=fact_id,
                    source_field=field,
                    expected_value=expected,
                    actual_value=actual,
                )
            )

    try:
        head = _git(repo_root, "rev-parse", "HEAD")
        commit = fact["source_git"]["commit_sha"]
        if require_source_commit_head and commit != head:
            raise ExternalContentReadinessError(
                f"source commit must equal write-time HEAD {head}; got {commit}"
            )
        if not _is_ancestor(repo_root, commit, head):
            raise ExternalContentReadinessError(
                "source commit is not retained in current HEAD ancestry"
            )
        spec_blob = _git_blob_at(repo_root, commit, PRODUCTION_SPEC_PATH)
        if spec_blob != fact["source_git"]["blob_sha"]:
            raise ExternalContentReadinessError("fact source Git blob binding mismatch")
        if spec_blob != _git_blob_sha(spec_raw) or spec_blob != LOCKED_SPEC_BLOB_SHA:
            raise ExternalContentReadinessError("source Git blob is stale for current bytes")

        tool_path = fact["computation"]["tool_path"]
        if tool_path != CANONICALIZER_PATH.as_posix():
            raise ExternalContentReadinessError("computation tool path is not locked")
        tool_file = _regular_file(
            repo_root, repo_root / CANONICALIZER_PATH, "canonicalizer tool"
        )
        tool_raw = tool_file.read_bytes()
        tool_blob = _git_blob_at(repo_root, commit, CANONICALIZER_PATH)
        computation_checks = {
            "computation.tool_identity": (
                fact["computation"]["tool_identity"],
                CANONICALIZER_IDENTITY,
            ),
            "computation.tool_sha256": (
                fact["computation"]["tool_sha256"],
                _sha256(tool_raw),
            ),
            "computation.tool_version": (
                fact["computation"]["tool_version"],
                f"git-blob:{tool_blob}",
            ),
            "computation.current_tool_blob": (tool_blob, _git_blob_sha(tool_raw)),
        }
        for field, (actual, expected) in computation_checks.items():
            if actual != expected:
                issues.append(
                    _issue(
                        "external_content_readiness_tool_mismatch",
                        fact_id=fact_id,
                        source_field=field,
                        expected_value=expected,
                        actual_value=actual,
                    )
                )
    except ExternalContentReadinessError as exc:
        issues.append(
            _issue(
                "external_content_readiness_git_binding_mismatch",
                fact_id=fact_id,
                source_field="source_git",
                expected_value="current exact source/tool blob binding",
                actual_value=str(exc),
            )
        )

    try:
        vm_path = _regular_file(
            repo_root,
            repo_root / "research/variant_manifests/VM-0007.variant_manifest.json",
            "VM-0007",
        )
        sweep_path = _regular_file(
            repo_root,
            repo_root / "research/sweep_plans/SWEEP-PLAN-0007.sweep_plan.json",
            "SWEEP-PLAN-0007",
        )
        vm, vm_raw = _load_object(vm_path, "VM-0007")
        sweep, sweep_raw = _load_object(sweep_path, "SWEEP-PLAN-0007")
        lineage_checks = {
            "VM-0007.raw_sha256": (_sha256(vm_raw), LOCKED_VM_SHA256),
            "VM-0007.parent_strategy_spec_id": (
                vm.get("parent_strategy_spec", {}).get("strategy_spec_id"),
                PRODUCTION_SPEC_ID,
            ),
            "VM-0007.parent_strategy_spec_hash": (
                vm.get("parent_strategy_spec", {}).get("strategy_spec_hash"),
                canonical_hash,
            ),
            "SWEEP-PLAN-0007.raw_sha256": (
                _sha256(sweep_raw),
                LOCKED_SWEEP_SHA256,
            ),
            "SWEEP-PLAN-0007.parent_variant_manifest_id": (
                sweep.get("parent_variant_manifest", {}).get("variant_manifest_id"),
                "VM-0007",
            ),
        }
        for field, (actual, expected) in lineage_checks.items():
            if actual != expected:
                issues.append(
                    _issue(
                        "external_content_readiness_lineage_mismatch",
                        fact_id=fact_id,
                        source_field=field,
                        expected_value=expected,
                        actual_value=actual,
                    )
                )
    except ExternalContentReadinessError as exc:
        issues.append(
            _issue(
                "external_content_readiness_lineage_mismatch",
                fact_id=fact_id,
                source_field="VM/Sweep lineage",
                expected_value="locked VM-0007 and SWEEP-PLAN-0007",
                actual_value=str(exc),
            )
        )

    del fact_raw  # exact bytes are preserved by the exclusive writer and Git history scan.
    return issues


def validate_external_content_readiness_corpus(
    repo_root: Path,
) -> list[dict[str, Any]]:
    """Return deterministic integrity rows; an empty list is externally ready."""

    root = repo_root.absolute()
    spec_path = _lexical_absolute(root, root / PRODUCTION_SPEC_PATH)
    if not spec_path.exists():
        return []

    files, issues = _current_fact_files(root)
    if not files:
        issues.append(
            _issue(
                "external_content_readiness_fact_missing",
                source_field="fact_path",
                expected_value=PRODUCTION_FACT_PATH.as_posix(),
                actual_value=None,
            )
        )
        return issues

    seen_ids: dict[str, Path] = {}
    seen_specs: dict[str, Path] = {}
    for path in files:
        try:
            fact, raw = _load_object(path, "external content readiness fact")
        except ExternalContentReadinessError as exc:
            issues.append(
                _issue(
                    "external_content_readiness_fact_invalid",
                    source_field="fact_path",
                    expected_value="readable UTF-8 JSON object",
                    actual_value=str(exc),
                )
            )
            continue
        fact_id = fact.get("fact_id")
        spec_id = fact.get("strategy_spec", {}).get("strategy_spec_id")
        if isinstance(fact_id, str) and fact_id in seen_ids:
            issues.append(
                _issue(
                    "external_content_readiness_duplicate_fact",
                    fact_id=fact_id,
                    source_field="fact_id",
                    expected_value="unique",
                    actual_value=f"{seen_ids[fact_id].name},{path.name}",
                )
            )
        elif isinstance(fact_id, str):
            seen_ids[fact_id] = path
        if isinstance(spec_id, str) and spec_id in seen_specs:
            issues.append(
                _issue(
                    "external_content_readiness_duplicate_spec",
                    fact_id=fact_id if isinstance(fact_id, str) else None,
                    source_field="strategy_spec.strategy_spec_id",
                    expected_value="one immutable fact",
                    actual_value=f"{seen_specs[spec_id].name},{path.name}",
                )
            )
        elif isinstance(spec_id, str):
            seen_specs[spec_id] = path
        issues.extend(
            _validate_fact(
                repo_root=root,
                fact=fact,
                fact_raw=raw,
                actual_path=path,
                require_source_commit_head=False,
            )
        )

    if len(files) != 1:
        issues.append(
            _issue(
                "external_content_readiness_fact_count_mismatch",
                source_field="fact_count",
                expected_value=1,
                actual_value=len(files),
            )
        )

    try:
        history = _history_paths_and_blobs(root)
        for path, blobs in sorted(history.items()):
            if path != PRODUCTION_FACT_PATH.as_posix():
                issues.append(
                    _issue(
                        "external_content_readiness_retained_history_duplicate",
                        source_field="historical_fact_path",
                        expected_value=PRODUCTION_FACT_PATH.as_posix(),
                        actual_value=path,
                    )
                )
            if len(blobs) > 1:
                issues.append(
                    _issue(
                        "external_content_readiness_historical_mutation",
                        source_field="historical_fact_blob_count",
                        expected_value=1,
                        actual_value=len(blobs),
                    )
                )
    except ExternalContentReadinessError as exc:
        issues.append(
            _issue(
                "external_content_readiness_history_scan_failed",
                source_field="retained_history",
                expected_value="complete deterministic scan",
                actual_value=str(exc),
            )
        )
    return issues


def _assert_candidate_valid(
    repo_root: Path, proposed_path: Path, *, require_source_commit_head: bool
) -> tuple[dict[str, Any], bytes]:
    proposed = _regular_file(repo_root, proposed_path, "proposed fact")
    fact, raw = _load_object(proposed, "proposed fact")
    issues = _validate_fact(
        repo_root=repo_root,
        fact=fact,
        fact_raw=raw,
        actual_path=repo_root / PRODUCTION_FACT_PATH,
        require_source_commit_head=require_source_commit_head,
    )
    if issues:
        raise ExternalContentReadinessError(
            f"proposed fact validation failed: {issues[0]['issue_type']}: "
            f"{issues[0]['actual_value']}"
        )
    return fact, raw


def _assert_unused(repo_root: Path) -> None:
    files, issues = _current_fact_files(repo_root)
    if issues:
        raise ExternalContentReadinessError(
            f"production fact corpus is not clean: {issues[0]['issue_type']}"
        )
    if files:
        raise ExternalContentReadinessError(
            "production fact ID, path, or Strategy Spec was already used"
        )
    history = _history_paths_and_blobs(repo_root)
    if history:
        raise ExternalContentReadinessError(
            "retained history already contains an external readiness fact; "
            "delete/recreate and superseding are forbidden"
        )


@contextmanager
def _crossing_lock(repo_root: Path) -> Iterator[dict[str, bool]]:
    lock = _reject_symlink_components(repo_root, repo_root / LOCK_PATH, "crossing lock")
    lock.parent.mkdir(parents=False, exist_ok=True)
    state = {"crossing_committed": False}
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ExternalContentReadinessError(
            "external readiness crossing lock exists; operator inspection required"
        ) from exc
    try:
        os.write(fd, f"pid={os.getpid()}\nwriter={WRITER_VERSION}\n".encode())
        os.fsync(fd)
        os.close(fd)
        fd = -1
        yield state
    finally:
        if fd >= 0:
            os.close(fd)
        try:
            lock.unlink()
        except FileNotFoundError:
            pass
        except OSError as exc:
            suffix = (
                " crossing committed; automatic retry is forbidden"
                if state["crossing_committed"]
                else ""
            )
            raise ExternalContentReadinessIntegrityCriticalError(
                "external readiness lock cleanup failed; operator inspection required;"
                + suffix
            ) from exc


def write_external_content_readiness_fact(
    *, repo_root: Path, proposed_fact_path: Path
) -> dict[str, Any]:
    """Validate twice and exclusive-create the one authorized production fact."""

    root = repo_root.absolute()
    proposed = _regular_file(root, proposed_fact_path, "proposed fact")
    _assert_candidate_valid(root, proposed, require_source_commit_head=True)
    _assert_unused(root)

    fact_root = _reject_symlink_components(root, root / FACT_ROOT, "fact root")
    fact_root.mkdir(parents=False, exist_ok=True)
    with _crossing_lock(root) as state:
        fact, exact_raw = _assert_candidate_valid(
            root, proposed, require_source_commit_head=True
        )
        _assert_unused(root)
        target = _repo_path(
            root, fact["fact_path"], "external readiness fact target"
        )
        if target != root / PRODUCTION_FACT_PATH:
            raise ExternalContentReadinessError("fact target derivation is not exact")
        if target.exists() or target.is_symlink():
            raise ExternalContentReadinessError(
                "fact target already exists; overwrite/delete-recreate is forbidden"
            )
        try:
            with target.open("xb") as handle:
                written = handle.write(exact_raw)
                if written != len(exact_raw):
                    raise OSError("partial immutable fact write")
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as exc:
            raise ExternalContentReadinessIntegrityCriticalError(
                "immutable fact crossing did not complete; target must not be deleted, "
                "recreated, overwritten, or automatically retried"
            ) from exc
        state["crossing_committed"] = True
        return fact


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--proposed-fact", type=Path)
    args = parser.parse_args()
    try:
        if args.proposed_fact is not None:
            fact = write_external_content_readiness_fact(
                repo_root=args.repo_root,
                proposed_fact_path=args.proposed_fact,
            )
            print(json.dumps(fact, indent=2, sort_keys=True))
            return 0
        issues = validate_external_content_readiness_corpus(args.repo_root)
        if issues:
            print(json.dumps(issues, indent=2, sort_keys=True))
            return 1
        print("VALIDATION PASS: exact STRAT-SPEC-0007 external content readiness fact")
        return 0
    except ExternalContentReadinessError as exc:
        parser.exit(2, f"External content readiness stopped: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
