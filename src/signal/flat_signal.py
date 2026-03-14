from __future__ import annotations

from decimal import Decimal
from typing import Any

from src.execution.interfaces import DesiredPosition


class FlatSignalProvider:
    """Deterministic signal provider that always targets a flat position."""

    def compute_desired_position(self, evaluation_time_utc: str, inputs: dict[str, Any]) -> DesiredPosition:
        symbol = str(inputs["symbol"])
        decision_id = str(inputs["decision_id"])
        correlation_id = str(inputs["correlation_id"])
        run_id = str(inputs["run_id"])
        source_timeframe = str(inputs.get("source_timeframe", "1m"))

        return DesiredPosition(
            symbol=symbol,
            target_qty=Decimal("0"),
            target_notional=None,
            timestamp_utc=evaluation_time_utc,
            source_timeframe=source_timeframe,
            decision_id=decision_id,
            correlation_id=correlation_id,
            run_id=run_id,
        )
