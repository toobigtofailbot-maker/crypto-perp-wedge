from __future__ import annotations

from typing import Any, Protocol

from src.execution.interfaces import DesiredPosition
from src.signal.flat_signal import FlatSignalProvider


class SignalProvider(Protocol):
    def compute_desired_position(self, evaluation_time_utc: str, inputs: dict[str, Any]) -> DesiredPosition:
        """Compute a deterministic desired position for the current evaluation timestamp."""


def build_signal_provider(provider_name: str) -> SignalProvider:
    selected = provider_name.strip().lower()
    if selected == "flat":
        return FlatSignalProvider()
    raise ValueError(f"Unsupported signal_provider: {provider_name}")
