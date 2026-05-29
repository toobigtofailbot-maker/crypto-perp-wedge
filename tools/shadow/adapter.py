"""Advisory-only shadow signal observation adapter.

This module observes SignalProvider-compatible candidates as local in-memory
decision support. It generates no orders, performs no execution, and has no
readiness, approval, transition, paper/live, broker, exchange, or runtime
authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from src.execution.interfaces import DesiredPosition
    from src.signal.provider import SignalProvider


@dataclass(frozen=True)
class ShadowSignalObservation:
    """Local non-canonical observation of one signal-provider evaluation."""

    evaluation_time_utc: str
    inputs_snapshot: Mapping[str, Any]
    desired_position: DesiredPosition
    candidate_id: str | None = None
    provider_name: str | None = None
    observation_id: str | None = None
    non_executing: bool = True
    decision_support_only: bool = True
    canonical: bool = False
    readiness_authority: bool = False
    transition_authority: bool = False
    execution_authority: bool = False


def observe_signal(
    provider: SignalProvider,
    evaluation_time_utc: str,
    inputs: Mapping[str, Any],
    *,
    candidate_id: str | None = None,
    provider_name: str | None = None,
    observation_id: str | None = None,
) -> ShadowSignalObservation:
    """Observe one provider output without creating execution authority."""

    provider_inputs = dict(inputs)
    inputs_snapshot = MappingProxyType(dict(provider_inputs))
    desired_position = provider.compute_desired_position(evaluation_time_utc, provider_inputs)
    return ShadowSignalObservation(
        evaluation_time_utc=evaluation_time_utc,
        inputs_snapshot=inputs_snapshot,
        desired_position=desired_position,
        candidate_id=candidate_id,
        provider_name=provider_name,
        observation_id=observation_id,
    )


__all__ = ["ShadowSignalObservation", "observe_signal"]
