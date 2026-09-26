"""Contained repo-local paths for non-authoritative active research work."""

from __future__ import annotations

import re
from pathlib import Path, PureWindowsPath

ACTIVE_WORKSPACE_RELATIVE_ROOT = Path(".cpw/active")
EPHEMERAL_WORKSPACE_RELATIVE_ROOT = Path(".cpw/ephemeral")

_SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_ROOTS = {
    "active": ACTIVE_WORKSPACE_RELATIVE_ROOT,
    "provisional": ACTIVE_WORKSPACE_RELATIVE_ROOT,
    "ephemeral": EPHEMERAL_WORKSPACE_RELATIVE_ROOT,
}


def _safe_parts(value: str | Path, *, label: str) -> tuple[str, ...]:
    raw = str(value)
    if not raw or "\x00" in raw:
        raise ValueError(f"{label} must be a non-empty safe relative path")
    windows = PureWindowsPath(raw)
    if windows.is_absolute() or windows.drive or raw.startswith(("/", "\\")):
        raise ValueError(f"{label} must be relative and drive-free")
    normalized = raw.replace("\\", "/")
    parts = tuple(normalized.split("/"))
    if any(
        not part
        or part in {".", ".."}
        or not _SAFE_COMPONENT.fullmatch(part)
        or part.endswith((".", " "))
        for part in parts
    ):
        raise ValueError(f"{label} contains an unsafe path component")
    return parts


def _contained(path: Path, root: Path, *, label: str) -> Path:
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{label} escapes the selected .cpw workspace root") from exc
    return resolved


def resolve_workspace_path(
    *,
    repo_root: Path,
    storage_class: str,
    namespace: str | Path,
    artifact_path: str | Path | None = None,
    create_parent: bool = False,
) -> Path:
    """Resolve a contained active/provisional or ephemeral workspace path."""

    try:
        relative_root = _ROOTS[storage_class]
    except KeyError as exc:
        raise ValueError("storage_class must be active, provisional, or ephemeral") from exc
    repo = Path(repo_root).resolve(strict=True)
    if not repo.is_dir():
        raise ValueError("repo_root must be an existing directory")
    cpw_root = _contained((repo / ".cpw").resolve(strict=False), repo, label=".cpw root")
    class_root = _contained(
        (repo / relative_root).resolve(strict=False), cpw_root, label="storage class root"
    )
    relative_parts = list(_safe_parts(namespace, label="namespace"))
    if artifact_path is not None:
        relative_parts.extend(_safe_parts(artifact_path, label="artifact_path"))
    target = _contained(class_root.joinpath(*relative_parts), class_root, label="workspace path")
    if create_parent:
        parent = target.parent if artifact_path is not None else target
        _contained(parent, class_root, label="workspace parent").mkdir(parents=True, exist_ok=True)
    return target
