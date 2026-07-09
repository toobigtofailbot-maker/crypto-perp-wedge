"""Pydantic response models for the read-only operator dashboard API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


SCHEMA_VERSION = "operator_dashboard_api_v1"


class ProvenanceRef(BaseModel):
    """Repo artifact or reader used to derive an API projection."""

    path: str
    role: str
    note: str | None = None
    sha256: str | None = None


class ApiEnvelope(BaseModel):
    """Common response envelope for every endpoint."""

    schema_version: str = SCHEMA_VERSION
    source: str
    provenance: list[ProvenanceRef] = Field(default_factory=list)
    authority: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    withheld: dict[str, Any] = Field(default_factory=dict)
    unavailable: dict[str, Any] = Field(default_factory=dict)
    data: Any


READ_ONLY_AUTHORITY: dict[str, bool | str] = {
    "api_projection_only": True,
    "repo_artifacts_remain_truth": True,
    "read_only": True,
    "get_endpoints_only": True,
    "not_execution_authority": True,
    "not_approval_authority": True,
    "not_recommendation_authority": True,
    "not_ranking_authority": True,
    "not_readiness_authority": True,
    "not_promotion_authority": True,
    "not_runtime_authority": True,
    "not_paper_live_authority": True,
    "not_broker_exchange_order_authority": True,
    "not_agent_inbox_write_authority": True,
    "not_scheduler_authority": True,
    "not_notification_authority": True,
    "control_surface": "none",
}


DERIVED_PROJECTION_WARNING = (
    "This API response is a derived read-only projection for local dashboard "
    "inspection. Committed repo artifacts and protected runtime truth, where "
    "later authorized snapshots exist, remain authoritative."
)
