"""The one structurally inert BROKER-3 no-op adapter.

This module is intentionally minimal. It has no clock, environment, randomness,
uuid, file, database, network, child-process, or retry surface. It is a pure
deterministic function over the closed dry-run projection model.
"""

from __future__ import annotations

from typing import Literal

from pydantic import model_validator

from .models import Sha256, StrictBrokerModel
from .projection import (
    DRY_RUN_PROOF_ADAPTER_ID,
    DRY_RUN_PROOF_ADAPTER_VERSION,
    DryRunProjection,
)

ADAPTER_ID = DRY_RUN_PROOF_ADAPTER_ID
ADAPTER_VERSION = DRY_RUN_PROOF_ADAPTER_VERSION
DRY_RUN_FAILED_REASON = "dry_run_requested_failure"


class DryRunAdapterResult(StrictBrokerModel):
    """Deterministic inert dry-run result; it never carries a real side effect."""

    adapter_id: Literal["broker3-dry-run-noop"]
    adapter_version: Literal["1.0.0"]
    projection_sha256: Sha256
    outcome: Literal["completed", "failed"]
    reason_code: str | None
    downstream_side_effect: Literal[False]

    @model_validator(mode="after")
    def validate_outcome(self) -> DryRunAdapterResult:
        if self.outcome == "completed":
            if self.reason_code is not None:
                raise ValueError("completed dry-run result cannot carry a reason")
        elif not (self.reason_code and self.reason_code.strip()):
            raise ValueError("failed dry-run result requires a reason")
        return self


def dry_run_noop(projection: DryRunProjection) -> DryRunAdapterResult:
    """Return the deterministic dry-run result for one projection and nothing else."""

    if not isinstance(projection, DryRunProjection):
        raise TypeError("the fixed no-op adapter accepts only a DryRunProjection")
    outcome = projection.projected_parameters.requested_dry_run_outcome
    reason_code = None if outcome == "completed" else DRY_RUN_FAILED_REASON
    return DryRunAdapterResult(
        adapter_id=ADAPTER_ID,
        adapter_version=ADAPTER_VERSION,
        projection_sha256=projection.projection_sha256,
        outcome=outcome,
        reason_code=reason_code,
        downstream_side_effect=False,
    )
