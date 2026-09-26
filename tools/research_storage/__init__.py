"""Non-authoritative local research workspace paths."""

from .workspace import (
    ACTIVE_WORKSPACE_RELATIVE_ROOT,
    EPHEMERAL_WORKSPACE_RELATIVE_ROOT,
    resolve_workspace_path,
)

__all__ = [
    "ACTIVE_WORKSPACE_RELATIVE_ROOT",
    "EPHEMERAL_WORKSPACE_RELATIVE_ROOT",
    "resolve_workspace_path",
]
