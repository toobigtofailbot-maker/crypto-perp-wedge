"""D2-007 advisory-only shadow parity measurement.

This module computes local in-memory parity observations for decision support.
It creates no canonical artifacts and has no readiness, transition, ranking,
scoring, recommendation, paper/live, broker, exchange, or runtime authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

PNL_DEVIATION_THRESHOLD = Decimal("0.10")
TRADE_COUNT_DEVIATION_THRESHOLD = Decimal("0.05")
MIN_SHADOW_WINDOW_DAYS = 14


@dataclass(frozen=True)
class ShadowParityObservation:
    """Local non-canonical observation of D2-007 parity measurements."""

    observed_pnl: Decimal
    reference_pnl: Decimal
    pnl_deviation: Decimal | None
    pnl_denominator_zero: bool
    pnl_threshold_satisfied: bool
    observed_trade_count: int
    reference_trade_count: int
    trade_count_deviation: Decimal | None
    trade_count_denominator_zero: bool
    trade_count_threshold_satisfied: bool
    observed_window_days: int
    shadow_window_complete: bool
    parity_thresholds_satisfied: bool
    window_start_utc: str | None = None
    window_end_utc: str | None = None
    candidate_id: str | None = None
    observation_id: str | None = None
    metadata: dict[str, Any] | None = None
    decision_support_only: bool = True
    canonical: bool = False
    readiness_authority: bool = False
    transition_authority: bool = False
    ranking_authority: bool = False
    scoring_authority: bool = False
    recommendation_authority: bool = False


def _to_decimal(value: Decimal | int | str) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _relative_deviation(
    observed: Decimal,
    reference: Decimal,
) -> tuple[Decimal | None, bool]:
    if reference == 0:
        return (Decimal("0"), False) if observed == 0 else (None, True)
    return abs(observed - reference) / abs(reference), False


def measure_parity(
    *,
    observed_pnl: Decimal | int | str,
    reference_pnl: Decimal | int | str,
    observed_trade_count: int,
    reference_trade_count: int,
    observed_window_days: int,
    window_start_utc: str | None = None,
    window_end_utc: str | None = None,
    candidate_id: str | None = None,
    observation_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> ShadowParityObservation:
    """Measure bounded D2-007 parity without creating authority."""

    observed_pnl_decimal = _to_decimal(observed_pnl)
    reference_pnl_decimal = _to_decimal(reference_pnl)
    pnl_deviation, pnl_denominator_zero = _relative_deviation(
        observed_pnl_decimal,
        reference_pnl_decimal,
    )

    observed_trade_decimal = Decimal(observed_trade_count)
    reference_trade_decimal = Decimal(reference_trade_count)
    trade_count_deviation, trade_count_denominator_zero = _relative_deviation(
        observed_trade_decimal,
        reference_trade_decimal,
    )

    pnl_threshold_satisfied = (
        pnl_deviation is not None and pnl_deviation <= PNL_DEVIATION_THRESHOLD
    )
    trade_count_threshold_satisfied = (
        trade_count_deviation is not None
        and trade_count_deviation <= TRADE_COUNT_DEVIATION_THRESHOLD
    )
    shadow_window_complete = observed_window_days >= MIN_SHADOW_WINDOW_DAYS

    return ShadowParityObservation(
        observed_pnl=observed_pnl_decimal,
        reference_pnl=reference_pnl_decimal,
        pnl_deviation=pnl_deviation,
        pnl_denominator_zero=pnl_denominator_zero,
        pnl_threshold_satisfied=pnl_threshold_satisfied,
        observed_trade_count=observed_trade_count,
        reference_trade_count=reference_trade_count,
        trade_count_deviation=trade_count_deviation,
        trade_count_denominator_zero=trade_count_denominator_zero,
        trade_count_threshold_satisfied=trade_count_threshold_satisfied,
        observed_window_days=observed_window_days,
        shadow_window_complete=shadow_window_complete,
        parity_thresholds_satisfied=(
            pnl_threshold_satisfied
            and trade_count_threshold_satisfied
            and shadow_window_complete
        ),
        window_start_utc=window_start_utc,
        window_end_utc=window_end_utc,
        candidate_id=candidate_id,
        observation_id=observation_id,
        metadata=dict(metadata) if metadata is not None else None,
    )


__all__ = [
    "MIN_SHADOW_WINDOW_DAYS",
    "PNL_DEVIATION_THRESHOLD",
    "ShadowParityObservation",
    "TRADE_COUNT_DEVIATION_THRESHOLD",
    "measure_parity",
]
