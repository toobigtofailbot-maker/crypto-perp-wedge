from tools.research_memory.fingerprint import HypothesisDefinition, fingerprint


def test_fingerprint_normalizes_only_deterministic_equivalents() -> None:
    left = {
        "strategy_family": " Funding_Momentum ",
        "mechanism": "Funding momentum   confirmation on FOUR hour bars.",
        "primary_timeframe": "4H",
        "required_data_features": ["ohlcv_4h", "funding_8h", "ohlcv_4h"],
        "free_parameter_count": 2,
    }
    right = {
        "strategy_family": "funding_momentum",
        "mechanism": "funding momentum confirmation on four hour bars.",
        "primary_timeframe": "4h",
        "required_data_features": ["FUNDING_8H", "OHLCV_4H"],
        "free_parameter_count": 2,
    }

    assert fingerprint(left) == fingerprint(right)
    assert HypothesisDefinition.from_mapping(left).canonical_mapping() == (
        HypothesisDefinition.from_mapping(right).canonical_mapping()
    )


def test_fingerprint_changes_for_material_structured_difference() -> None:
    base = {
        "strategy_family": "trend_following",
        "mechanism": "Donchian breakout",
        "primary_timeframe": "4h",
        "required_data_features": ["ohlcv_4h"],
        "free_parameter_count": 1,
    }
    changed = {**base, "primary_timeframe": "1h"}

    assert fingerprint(base) != fingerprint(changed)
