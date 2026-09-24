"""Stable CPW-owned research-domain constants.

These values describe non-canonical research meaning only.  They grant no
canonical, candidate, execution, promotion, runtime, or economic authority.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Final, Mapping

LOCKED_TIMEFRAMES: Final[tuple[str, ...]] = ("15m", "30m", "1h", "4h", "1d")
TRIAL_STATUSES: Final[tuple[str, ...]] = (
    "completed",
    "failed",
    "invalid",
    "pruned",
    "blocked",
)

PREREG_APPROVAL_SCHEMA_VERSION: Final = "lab_pipeline_prereg_approval_v1"
PREREG_APPROVAL_SCOPE: Final = "noncanonical_offline_research_execution_only"
PREREG_APPROVAL_STATEMENT: Final = (
    "Authorizes only non-canonical offline research execution for the exact "
    "frozen preregistration packet content."
)

PREREG_APPROVAL_REQUIRED_FIELDS: Final[tuple[str, ...]] = (
    "schema_version",
    "approved_by",
    "approval_scope",
    "approval_statement",
    "approval_timestamp_utc",
    "authorizes_noncanonical_offline_research_execution",
    "authorizes_canonical_write",
    "authorizes_candidate_lifecycle",
    "authorizes_paper_live_runtime",
    "authorizes_scheduler_autonomy",
    "authorizes_notifications",
    "preregistration_packet_sha256",
)

PREREG_APPROVAL_EXTRA_FALSE_FIELDS: Final[tuple[str, ...]] = (
    "authorizes_crossing",
    "authorizes_promotion_or_readiness",
    "authorizes_provider_api_or_credentials",
    "authorizes_dependency_config_data_acquisition",
    "authorizes_protected_path_touch",
)

PREREG_NON_AUTHORITY_ASSERTIONS: Final[Mapping[str, bool]] = MappingProxyType(
    {
        "canonical_write": False,
        "candidate_lifecycle_write": False,
        "crossing": False,
        "promotion_or_readiness": False,
        "paper_live_runtime": False,
        "scheduler_autonomy": False,
        "notification_sending": False,
        "provider_api_credential": False,
        "dependency_config_data_acquisition": False,
        "protected_path_touch": False,
    }
)

LAB_NON_AUTHORITY_FLAGS: Final[Mapping[str, bool]] = MappingProxyType(
    {
        "noncanonical_only": True,
        "scratch_only": True,
        "offline_only": True,
        "writes_canonical_evidence": False,
        "writes_candidate_lifecycle": False,
        "executes_canonical_crossing": False,
        "authorizes_promotion_or_readiness": False,
        "contacts_paper_live_runtime": False,
        "uses_scheduler_or_autonomy": False,
        "fires_notifications": False,
        "uses_provider_api_or_credentials": False,
        "human_review_required_for_prereg": True,
        "separate_authorization_required_for_canonical_or_runtime": True,
    }
)
