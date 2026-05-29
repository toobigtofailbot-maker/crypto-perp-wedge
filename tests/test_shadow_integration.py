from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

from src.execution.interfaces import DesiredPosition
from tools.shadow.adapter import observe_signal
from tools.shadow.evidence import build_shadow_evidence, disclosure_counts
from tools.shadow.parity import measure_parity


class FakeSignalProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def compute_desired_position(
        self,
        evaluation_time_utc: str,
        inputs: dict[str, Any],
    ) -> DesiredPosition:
        self.calls.append((evaluation_time_utc, inputs))
        return DesiredPosition(
            symbol=inputs["symbol"],
            target_qty=Decimal("1.25"),
            target_notional=None,
            timestamp_utc=evaluation_time_utc,
            source_timeframe="1h",
            decision_id=inputs["decision_id"],
            correlation_id="shadow-correlation-1",
            run_id="shadow-run-1",
        )


def _run_local_shadow_flow():
    provider = FakeSignalProvider()

    signal_observation = observe_signal(
        provider,
        "2026-05-29T00:00:00Z",
        {"symbol": "BTCUSDT", "decision_id": "decision-1"},
        candidate_id="H-005",
        provider_name="fake-signal-provider",
        observation_id="signal-observation-1",
    )
    parity_observation = measure_parity(
        observed_pnl=Decimal("99"),
        reference_pnl=Decimal("100"),
        observed_trade_count=101,
        reference_trade_count=100,
        observed_window_days=14,
        window_start_utc="2026-05-15T00:00:00Z",
        window_end_utc="2026-05-29T00:00:00Z",
        candidate_id="H-005",
        observation_id="parity-observation-1",
        metadata={"source": "local-integration-test"},
    )
    evidence_record = build_shadow_evidence(
        signal_observation=signal_observation,
        parity_observation=parity_observation,
        lineage_references=["signal-observation-1", "parity-observation-1"],
        interruptions=["local observation pause example"],
        invalid_observations=["invalid local signal observation example"],
        missing_data=["missing local parity input example"],
        observation_resets=["local observation reset example"],
        evidence_id="shadow-evidence-1",
        candidate_id="H-005",
        generated_at_utc="2026-05-29T00:01:00Z",
        metadata={"scope": "local-shadow-integration"},
    )

    return provider, signal_observation, parity_observation, evidence_record


def test_end_to_end_local_flow_produces_signal_parity_and_evidence_record():
    provider, signal_observation, parity_observation, evidence_record = (
        _run_local_shadow_flow()
    )

    assert provider.calls == [
        (
            "2026-05-29T00:00:00Z",
            {"symbol": "BTCUSDT", "decision_id": "decision-1"},
        )
    ]
    assert signal_observation.desired_position.symbol == "BTCUSDT"
    assert signal_observation.desired_position.target_qty == Decimal("1.25")
    assert signal_observation.non_executing is True

    assert parity_observation.pnl_deviation == Decimal("0.01")
    assert parity_observation.trade_count_deviation == Decimal("0.01")
    assert parity_observation.shadow_window_complete is True
    assert parity_observation.parity_thresholds_satisfied is True

    assert evidence_record.signal_observation is signal_observation
    assert evidence_record.parity_observation is parity_observation
    assert evidence_record.evidence_id == "shadow-evidence-1"


def test_end_to_end_evidence_links_local_signal_and_parity_observation_ids():
    _, _, _, evidence_record = _run_local_shadow_flow()

    local_dict = evidence_record.to_local_dict()

    assert evidence_record.lineage_references == (
        "signal-observation-1",
        "parity-observation-1",
    )
    assert local_dict["signal_observation_id"] == "signal-observation-1"
    assert local_dict["parity_observation_id"] == "parity-observation-1"


def test_end_to_end_output_remains_non_canonical_decision_support_only():
    signal_observation, parity_observation, evidence_record = (
        _run_local_shadow_flow()[1:]
    )
    local_dict = evidence_record.to_local_dict()

    assert signal_observation.decision_support_only is True
    assert signal_observation.canonical is False
    assert parity_observation.decision_support_only is True
    assert parity_observation.canonical is False
    assert evidence_record.decision_support_only is True
    assert evidence_record.canonical is False
    assert local_dict["decision_support_only"] is True
    assert local_dict["canonical"] is False
    assert "decision-support only" in local_dict[
        "no_readiness_transition_approval_statement"
    ]


def test_end_to_end_output_has_no_readiness_transition_approval_or_execution_authority():
    signal_observation, parity_observation, evidence_record = (
        _run_local_shadow_flow()[1:]
    )
    local_dict = evidence_record.to_local_dict()

    assert signal_observation.readiness_authority is False
    assert signal_observation.transition_authority is False
    assert signal_observation.execution_authority is False

    assert parity_observation.readiness_authority is False
    assert parity_observation.transition_authority is False
    assert parity_observation.ranking_authority is False
    assert parity_observation.scoring_authority is False
    assert parity_observation.recommendation_authority is False

    assert evidence_record.readiness_authority is False
    assert evidence_record.transition_authority is False
    assert evidence_record.approval_authority is False
    assert evidence_record.human_gate_execution is False
    assert evidence_record.ranking_authority is False
    assert evidence_record.scoring_authority is False
    assert evidence_record.recommendation_authority is False

    assert local_dict["readiness_authority"] is False
    assert local_dict["transition_authority"] is False
    assert local_dict["approval_authority"] is False
    assert local_dict["human_gate_execution"] is False
    assert local_dict["ranking_authority"] is False
    assert local_dict["scoring_authority"] is False
    assert local_dict["recommendation_authority"] is False


def test_end_to_end_flow_records_all_required_disclosure_types():
    _, _, _, evidence_record = _run_local_shadow_flow()

    assert disclosure_counts(evidence_record) == {
        "interruption": 1,
        "invalid_observation": 1,
        "missing_data": 1,
        "observation_reset": 1,
    }
    assert evidence_record.disclosure_complete is True
    assert [
        disclosure.disclosure_type for disclosure in evidence_record.disclosures
    ] == [
        "interruption",
        "invalid_observation",
        "missing_data",
        "observation_reset",
    ]


def test_end_to_end_flow_creates_no_output_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    _run_local_shadow_flow()

    assert list(Path(tmp_path).iterdir()) == []


def test_end_to_end_flow_is_deterministic_for_same_local_inputs():
    first = _run_local_shadow_flow()
    second = _run_local_shadow_flow()

    assert first[0].calls == second[0].calls
    assert first[1] == second[1]
    assert first[2] == second[2]
    assert first[3] == second[3]
    assert first[3].to_local_dict() == second[3].to_local_dict()


def test_end_to_end_flow_requires_only_minimal_local_signal_provider_surface():
    provider, signal_observation, parity_observation, evidence_record = (
        _run_local_shadow_flow()
    )

    assert sorted(name for name in dir(provider) if not name.startswith("_")) == [
        "calls",
        "compute_desired_position",
    ]
    assert signal_observation.desired_position.decision_id == "decision-1"
    assert parity_observation.metadata == {"source": "local-integration-test"}
    assert dict(evidence_record.metadata) == {"scope": "local-shadow-integration"}
