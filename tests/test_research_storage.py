from __future__ import annotations

import ast
import os
from pathlib import Path

import pytest

from tools.research_storage.workspace import (
    ACTIVE_WORKSPACE_RELATIVE_ROOT,
    EPHEMERAL_WORKSPACE_RELATIVE_ROOT,
    resolve_workspace_path,
)


def test_active_provisional_and_ephemeral_roots_are_fixed(tmp_path: Path) -> None:
    active = resolve_workspace_path(
        repo_root=tmp_path,
        storage_class="active",
        namespace="cpw-mig-01",
        artifact_path="results/output.json",
    )
    provisional = resolve_workspace_path(
        repo_root=tmp_path,
        storage_class="provisional",
        namespace="cpw-mig-01",
        artifact_path="results/output.json",
    )
    ephemeral = resolve_workspace_path(
        repo_root=tmp_path,
        storage_class="ephemeral",
        namespace="cpw-mig-01",
        artifact_path="cache/item.tmp",
    )
    assert ACTIVE_WORKSPACE_RELATIVE_ROOT == Path(".cpw/active")
    assert EPHEMERAL_WORKSPACE_RELATIVE_ROOT == Path(".cpw/ephemeral")
    assert (
        active == provisional == (tmp_path / ".cpw/active/cpw-mig-01/results/output.json").resolve()
    )
    assert ephemeral == (tmp_path / ".cpw/ephemeral/cpw-mig-01/cache/item.tmp").resolve()
    assert active == resolve_workspace_path(
        repo_root=tmp_path,
        storage_class="active",
        namespace="cpw-mig-01",
        artifact_path="results/output.json",
    )


@pytest.mark.parametrize(
    "namespace,artifact",
    [
        ("/absolute", None),
        (r"C:\qualified", None),
        ("C:drive-relative", None),
        ("../escape", None),
        ("safe", "../../escape"),
        ("", None),
        ("safe//empty", None),
        ("safe", ""),
        ("safe", "research/result.json"),
    ],
)
def test_unsafe_or_authority_shaped_paths_are_rejected(
    tmp_path: Path, namespace: str, artifact: str | None
) -> None:
    if namespace == "safe" and artifact == "research/result.json":
        # This is still contained beneath .cpw; it cannot target repo research/.
        resolved = resolve_workspace_path(
            repo_root=tmp_path,
            storage_class="active",
            namespace=namespace,
            artifact_path=artifact,
        )
        assert resolved.is_relative_to((tmp_path / ".cpw/active").resolve())
        assert resolved != (tmp_path / artifact).resolve()
        return
    with pytest.raises(ValueError):
        resolve_workspace_path(
            repo_root=tmp_path,
            storage_class="active",
            namespace=namespace,
            artifact_path=artifact,
        )


def test_unknown_storage_class_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="storage_class"):
        resolve_workspace_path(
            repo_root=tmp_path,
            storage_class="canonical",
            namespace="attempt",
        )


def test_parent_creation_stays_below_selected_root(tmp_path: Path) -> None:
    target = resolve_workspace_path(
        repo_root=tmp_path,
        storage_class="ephemeral",
        namespace="task-1",
        artifact_path="nested/output.json",
        create_parent=True,
    )
    assert target.parent.is_dir()
    assert target.parent.is_relative_to((tmp_path / ".cpw/ephemeral").resolve())
    assert not target.exists()
    assert not (tmp_path / "research").exists()
    assert not (tmp_path / "src").exists()


def test_existing_symlink_escape_is_rejected(tmp_path: Path) -> None:
    class_root = tmp_path / ".cpw/active"
    class_root.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    link = class_root / "escape"
    try:
        os.symlink(outside, link, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")
    with pytest.raises(ValueError, match="escapes"):
        resolve_workspace_path(
            repo_root=tmp_path,
            storage_class="active",
            namespace="escape",
            artifact_path="output.json",
        )


def test_cpw_root_symlink_escape_is_rejected(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir(exist_ok=True)
    try:
        os.symlink(outside, tmp_path / ".cpw", target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")
    with pytest.raises(ValueError, match="escapes"):
        resolve_workspace_path(
            repo_root=tmp_path,
            storage_class="active",
            namespace="task",
        )


def test_storage_api_has_no_network_runtime_or_authority_state() -> None:
    source = Path("tools/research_storage/workspace.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    assert imports == ["__future__", "re", "pathlib"]
    assert "canonical" not in source.casefold()
    assert "authority" not in source.casefold()
