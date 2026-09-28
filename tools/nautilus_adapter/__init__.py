"""Bounded CPW-owned adapters for offline Nautilus research proofs."""

from tools.nautilus_adapter.research import (
    ADAPTER_ID,
    NAUTILUS_TARGET_VERSION,
    SUPPORTED_PROFILE,
    NautilusAdapterError,
    NautilusResearchResult,
    ResolvedResearchInputs,
    execute_nautilus_research,
    validate_resolved_inputs,
)

__all__ = [
    "ADAPTER_ID",
    "NAUTILUS_TARGET_VERSION",
    "SUPPORTED_PROFILE",
    "NautilusAdapterError",
    "NautilusResearchResult",
    "ResolvedResearchInputs",
    "execute_nautilus_research",
    "validate_resolved_inputs",
]
