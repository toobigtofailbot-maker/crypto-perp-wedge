"""Bounded ToolContext enforcement for non-authoritative research agents."""

from .audit import AuditRecord, JsonLinesAuditSink, MemoryAuditSink
from .permissions import POLICY_ID, ROLE_PERMISSIONS, SUPPORTED_ROLES
from .tool_context import BlockedActionError, ToolAction, ToolContext

__all__ = [
    "AuditRecord",
    "BlockedActionError",
    "JsonLinesAuditSink",
    "MemoryAuditSink",
    "POLICY_ID",
    "ROLE_PERMISSIONS",
    "SUPPORTED_ROLES",
    "ToolAction",
    "ToolContext",
]
