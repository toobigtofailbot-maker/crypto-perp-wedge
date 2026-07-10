"""Models for the isolated Agent Inbox intake draft service."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class IntakeDraftRequest(BaseModel):
    """Bounded operator payload for one scratch-only draft packet."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=120)
    hypothesis_text: str = Field(..., min_length=1, max_length=4000)
    market_hint: str | None = Field(default="BTCUSDT", max_length=80)
    timeframe_hint: str | None = Field(default="15m", max_length=10)
    constraints_notes: str | None = Field(default=None, max_length=1200)
    submitter_label: str | None = Field(default=None, max_length=80)
    client_draft_id: str | None = Field(default=None, max_length=80)


class IntakeDraftError(ValueError):
    """Raised when a request fails closed before a draft packet can be written."""


class DraftHistoryError(ValueError):
    """Raised when stored draft history cannot be read honestly."""


class DraftIdError(DraftHistoryError):
    """Raised when a requested draft identifier is unsafe or malformed."""


class DraftNotFoundError(LookupError):
    """Raised when a well-formed draft identifier has no stored packet."""
