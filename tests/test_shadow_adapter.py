from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from src.execution.interfaces import DesiredPosition
from tools.shadow.adapter import ShadowSignalObservation, observe_signal


class FakeSignalProvider:
    def __init__(self, desired_position: DesiredPosition) -> None:
        self.desired_position = desired_position
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def compute_desired_position(self, evaluation_time_utc: str, inputs: dict[str, Any]) -> DesiredPosition:
        self.calls.append((evaluation_time_utc, inputs))
        return self.desired_position


class MutatingSignalProvider(FakeSignalProvider):
    def compute_desired_position(self, evaluation_time_utc: str, inputs: dict[str, Any]) -> DesiredPosition:
        self.calls.append((evaluation_time_utc, inputs))
        inputs["provider_mutation"] = "not recorded"
        return self.desired_position


def _desired_position() -> DesiredPosition:
    return DesiredPosition(
        symbol="BTCUSDT",
        target_qty=Decimal("1.25"),
        target_notional=None,
        timestamp_utc="2026-05-29T00:00:00Z",
        source_timeframe="1h",
        decision_id="decision-1",
        correlation_id="correlation-1",
        run_id="run-1",
    )


def test_observe_signal_calls_provider_once_with_expected_timestamp_and_inputs():
    desired = _desired_position()
    provider = FakeSignalProvider(desired)
    inputs = {"symbol": "BTCUSDT", "decision_id": "decision-1"}

    observation = observe_signal(provider, "2026-05-29T00:00:00Z", inputs)

    assert provider.calls == [("2026-05-29T00:00:00Z", inputs)]
    assert observation.desired_position is desired


def test_observation_records_defensive_input_snapshot():
    provider = FakeSignalProvider(_desired_position())
    inputs = {"symbol": "BTCUSDT", "decision_id": "decision-1"}

    observation = observe_signal(provider, "2026-05-29T00:00:00Z", inputs)
    inputs["symbol"] = "ETHUSDT"
    inputs["new_field"] = "mutated"

    assert dict(observation.inputs_snapshot) == {"symbol": "BTCUSDT", "decision_id": "decision-1"}
    with pytest.raises(TypeError):
        observation.inputs_snapshot["symbol"] = "ETHUSDT"  # type: ignore[index]


def test_provider_input_mutation_does_not_change_observation_snapshot():
    provider = MutatingSignalProvider(_desired_position())

    observation = observe_signal(provider, "2026-05-29T00:00:00Z", {"symbol": "BTCUSDT"})

    assert dict(observation.inputs_snapshot) == {"symbol": "BTCUSDT"}
    assert provider.calls[0][1]["provider_mutation"] == "not recorded"


def test_observation_carries_non_executing_decision_support_flags():
    observation = observe_signal(FakeSignalProvider(_desired_position()), "2026-05-29T00:00:00Z", {})

    assert observation.non_executing is True
    assert observation.decision_support_only is True
    assert observation.canonical is False
    assert observation.readiness_authority is False
    assert observation.transition_authority is False
    assert observation.execution_authority is False


def test_observation_preserves_optional_local_metadata():
    observation = observe_signal(
        FakeSignalProvider(_desired_position()),
        "2026-05-29T00:00:00Z",
        {},
        candidate_id="H-005",
        provider_name="candidate-provider",
        observation_id="shadow-observation-1",
    )

    assert observation.candidate_id == "H-005"
    assert observation.provider_name == "candidate-provider"
    assert observation.observation_id == "shadow-observation-1"


def test_observation_is_deterministic_for_same_provider_output_and_inputs():
    desired = _desired_position()
    first = observe_signal(FakeSignalProvider(desired), "2026-05-29T00:00:00Z", {"symbol": "BTCUSDT"})
    second = observe_signal(FakeSignalProvider(desired), "2026-05-29T00:00:00Z", {"symbol": "BTCUSDT"})

    assert first == second


def test_module_does_not_expose_order_generation_or_execution_behavior():
    public_names = set(getattr(__import__("tools.shadow.adapter", fromlist=["__all__"]), "__all__"))

    assert public_names == {"ShadowSignalObservation", "observe_signal"}
    assert not any("order" in name.lower() for name in public_names)
    assert not any("execute" in name.lower() or "execution" in name.lower() for name in public_names)


def test_adapter_creates_no_output_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    observe_signal(FakeSignalProvider(_desired_position()), "2026-05-29T00:00:00Z", {"symbol": "BTCUSDT"})

    assert list(Path(tmp_path).iterdir()) == []
    assert isinstance(
        observe_signal(FakeSignalProvider(_desired_position()), "2026-05-29T00:00:00Z", {}),
        ShadowSignalObservation,
    )
