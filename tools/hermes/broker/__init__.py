"""Hermes BROKER-1 verification-only authority contract.

This package deliberately stops before reservation, dispatch, or any adapter call.
"""

from .models import (
    ApprovalClaimPayload,
    BrokerDecision,
    DecisionReason,
    ExecutableAction,
    SignedApprovalClaim,
)
from .registry import ActionRegistry, RegistryEntry, production_registry
from .verification import verify_approval

__all__ = [
    "ActionRegistry",
    "ApprovalClaimPayload",
    "BrokerDecision",
    "DecisionReason",
    "ExecutableAction",
    "RegistryEntry",
    "SignedApprovalClaim",
    "production_registry",
    "verify_approval",
]
