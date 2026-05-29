from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from tools.shadow.parity import (
    MIN_SHADOW_WINDOW_DAYS,
    PNL_DEVIATION_THRESHOLD,
    TRADE_COUNT_DEVIATION_THRESHOLD,
    ShadowParityObservation,
    measure_parity,
)


def test_pnl_deviation_calculation_is_correct_for_passing_case():
    observation = measure_parity(
        observed_pnl=Decimal("108"),
        reference_pnl=Decimal("100"),
        observed_trade_count=100,
        reference_trade_count=100,
        observed_window_days=14,
    )

    assert observation.pnl_deviation == Decimal("0.08")
    assert observation.pnl_threshold_satisfied is True


def test_trade_count_deviation_calculation_is_correct_for_passing_case():
    observation = measure_parity(
        observed_pnl=Decimal("100"),
        reference_pnl=Decimal("100"),
        observed_trade_count=104,
        reference_trade_count=100,
        observed_window_days=14,
    )

    assert observation.trade_count_deviation == Decimal("0.04")
    assert observation.trade_count_threshold_satisfied is True


def test_threshold_flags_pass_when_all_d2_007_thresholds_are_satisfied():
    observation = measure_parity(
        observed_pnl=Decimal("90"),
        reference_pnl=Decimal("100"),
        observed_trade_count=95,
        reference_trade_count=100,
        observed_window_days=14,
    )

    assert observation.pnl_deviation == PNL_DEVIATION_THRESHOLD
    assert observation.trade_count_deviation == TRADE_COUNT_DEVIATION_THRESHOLD
    assert observation.shadow_window_complete is True
    assert observation.parity_thresholds_satisfied is True


def test_threshold_flags_fail_when_pnl_deviation_exceeds_threshold():
    observation = measure_parity(
        observed_pnl=Decimal("111"),
        reference_pnl=Decimal("100"),
        observed_trade_count=100,
        reference_trade_count=100,
        observed_window_days=14,
    )

    assert observation.pnl_deviation == Decimal("0.11")
    assert observation.pnl_threshold_satisfied is False
    assert observation.parity_thresholds_satisfied is False


def test_threshold_flags_fail_when_trade_count_deviation_exceeds_threshold():
    observation = measure_parity(
        observed_pnl=Decimal("100"),
        reference_pnl=Decimal("100"),
        observed_trade_count=106,
        reference_trade_count=100,
        observed_window_days=14,
    )

    assert observation.trade_count_deviation == Decimal("0.06")
    assert observation.trade_count_threshold_satisfied is False
    assert observation.parity_thresholds_satisfied is False


def test_window_completeness_fails_when_observed_window_is_less_than_minimum():
    observation = measure_parity(
        observed_pnl=Decimal("100"),
        reference_pnl=Decimal("100"),
        observed_trade_count=100,
        reference_trade_count=100,
        observed_window_days=13,
    )

    assert MIN_SHADOW_WINDOW_DAYS == 14
    assert observation.shadow_window_complete is False
    assert observation.parity_thresholds_satisfied is False


def test_zero_reference_values_are_handled_without_division_by_zero():
    zero_match = measure_parity(
        observed_pnl=Decimal("0"),
        reference_pnl=Decimal("0"),
        observed_trade_count=0,
        reference_trade_count=0,
        observed_window_days=14,
    )
    zero_mismatch = measure_parity(
        observed_pnl=Decimal("1"),
        reference_pnl=Decimal("0"),
        observed_trade_count=1,
        reference_trade_count=0,
        observed_window_days=14,
    )

    assert zero_match.pnl_deviation == Decimal("0")
    assert zero_match.trade_count_deviation == Decimal("0")
    assert zero_match.pnl_denominator_zero is False
    assert zero_match.trade_count_denominator_zero is False
    assert zero_match.parity_thresholds_satisfied is True

    assert zero_mismatch.pnl_deviation is None
    assert zero_mismatch.trade_count_deviation is None
    assert zero_mismatch.pnl_denominator_zero is True
    assert zero_mismatch.trade_count_denominator_zero is True
    assert zero_mismatch.parity_thresholds_satisfied is False


def test_observation_carries_decision_support_only_non_authority_flags():
    observation = measure_parity(
        observed_pnl=Decimal("100"),
        reference_pnl=Decimal("100"),
        observed_trade_count=100,
        reference_trade_count=100,
        observed_window_days=14,
    )

    assert observation.decision_support_only is True
    assert observation.canonical is False
    assert observation.readiness_authority is False
    assert observation.transition_authority is False
    assert observation.ranking_authority is False
    assert observation.scoring_authority is False
    assert observation.recommendation_authority is False


def test_module_does_not_expose_authority_or_execution_behavior():
    public_names = set(getattr(__import__("tools.shadow.parity", fromlist=["__all__"]), "__all__"))

    assert public_names == {
        "MIN_SHADOW_WINDOW_DAYS",
        "PNL_DEVIATION_THRESHOLD",
        "ShadowParityObservation",
        "TRADE_COUNT_DEVIATION_THRESHOLD",
        "measure_parity",
    }
    forbidden_terms = (
        "rank",
        "score",
        "recommend",
        "ready",
        "readiness",
        "transition",
        "execute",
        "execution",
        "order",
    )
    assert not any(term in name.lower() for name in public_names for term in forbidden_terms)


def test_parity_module_creates_no_output_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    observation = measure_parity(
        observed_pnl=Decimal("100"),
        reference_pnl=Decimal("100"),
        observed_trade_count=100,
        reference_trade_count=100,
        observed_window_days=14,
    )

    assert list(Path(tmp_path).iterdir()) == []
    assert isinstance(observation, ShadowParityObservation)


def test_decimal_inputs_remain_deterministic_and_metadata_is_preserved_defensively():
    metadata = {"source": "local-shadow-window"}

    observation = measure_parity(
        observed_pnl="99.5",
        reference_pnl=Decimal("100"),
        observed_trade_count=100,
        reference_trade_count=100,
        observed_window_days=14,
        window_start_utc="2026-05-01T00:00:00Z",
        window_end_utc="2026-05-15T00:00:00Z",
        candidate_id="H-005",
        observation_id="parity-observation-1",
        metadata=metadata,
    )
    metadata["source"] = "mutated"

    assert observation.observed_pnl == Decimal("99.5")
    assert observation.reference_pnl == Decimal("100")
    assert observation.pnl_deviation == Decimal("0.005")
    assert observation.window_start_utc == "2026-05-01T00:00:00Z"
    assert observation.window_end_utc == "2026-05-15T00:00:00Z"
    assert observation.candidate_id == "H-005"
    assert observation.observation_id == "parity-observation-1"
    assert observation.metadata == {"source": "local-shadow-window"}


def test_boundary_cases_exactly_at_thresholds_and_window_minimum_pass():
    observation = measure_parity(
        observed_pnl=Decimal("-110"),
        reference_pnl=Decimal("-100"),
        observed_trade_count=105,
        reference_trade_count=100,
        observed_window_days=MIN_SHADOW_WINDOW_DAYS,
    )

    assert observation.pnl_deviation == PNL_DEVIATION_THRESHOLD
    assert observation.trade_count_deviation == TRADE_COUNT_DEVIATION_THRESHOLD
    assert observation.shadow_window_complete is True
    assert observation.parity_thresholds_satisfied is True
