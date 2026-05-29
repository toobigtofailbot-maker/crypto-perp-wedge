from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from src.execution.interfaces import DesiredPosition
from tools.shadow.adapter import ShadowSignalObservation
from tools.shadow.evidence import (
    NO_READINESS_TRANSITION_APPROVAL_STATEMENT,
    ShadowDisclosure,
    ShadowEvidenceRecord,
    build_shadow_evidence,
    disclosure_counts,
    has_any_disclosure,
)
from tools.shadow.parity import ShadowParityObservation, measure_parity


def _signal_observation() -> ShadowSignalObservation:
    return ShadowSignalObservation(
        evaluation_time_utc="2026-05-29T00:00:00Z",
        inputs_snapshot={"symbol": "BTCUSDT"},
        desired_position=DesiredPosition(
            symbol="BTCUSDT",
            target_qty=Decimal("1"),
            target_notional=None,
            timestamp_utc="2026-05-29T00:00:00Z",
            source_timeframe="1h",
            decision_id="decision-1",
            correlation_id="correlation-1",
            run_id="run-1",
        ),
        candidate_id="H-005",
        provider_name="candidate-provider",
        observation_id="signal-observation-1",
    )


def _parity_observation() -> ShadowParityObservation:
    return measure_parity(
        observed_pnl=Decimal("99"),
        reference_pnl=Decimal("100"),
        observed_trade_count=101,
        reference_trade_count=100,
        observed_window_days=14,
        window_start_utc="2026-05-15T00:00:00Z",
        window_end_utc="2026-05-29T00:00:00Z",
        candidate_id="H-005",
        observation_id="parity-observation-1",
        metadata={"source": "local-parity"},
    )


def test_evidence_record_combines_signal_and_parity_observations():
    signal = _signal_observation()
    parity = _parity_observation()

    record = build_shadow_evidence(
        signal_observation=signal,
        parity_observation=parity,
        evidence_id="evidence-1",
        candidate_id="H-005",
        generated_at_utc="2026-05-29T00:01:00Z",
    )

    assert isinstance(record, ShadowEvidenceRecord)
    assert record.signal_observation is signal
    assert record.parity_observation is parity
    assert record.evidence_id == "evidence-1"
    assert record.candidate_id == "H-005"
    assert record.generated_at_utc == "2026-05-29T00:01:00Z"


def test_evidence_record_carries_decision_support_only_non_authority_flags():
    record = build_shadow_evidence(
        signal_observation=_signal_observation(),
        parity_observation=_parity_observation(),
    )

    assert record.decision_support_only is True
    assert record.canonical is False
    assert record.readiness_authority is False
    assert record.transition_authority is False
    assert record.approval_authority is False
    assert record.human_gate_execution is False
    assert record.ranking_authority is False
    assert record.scoring_authority is False
    assert record.recommendation_authority is False
    assert record.no_readiness_transition_approval_statement == (
        NO_READINESS_TRANSITION_APPROVAL_STATEMENT
    )


def test_disclosure_surface_records_all_required_disclosure_types():
    record = build_shadow_evidence(
        signal_observation=_signal_observation(),
        parity_observation=_parity_observation(),
        interruptions=["local process interrupted"],
        invalid_observations=["invalid signal observation excluded"],
        missing_data=["missing local comparison row"],
        observation_resets=["shadow window reset noted"],
    )

    assert has_any_disclosure(record) is True
    assert disclosure_counts(record) == {
        "interruption": 1,
        "invalid_observation": 1,
        "missing_data": 1,
        "observation_reset": 1,
    }
    assert record.disclosure_complete is True
    assert [item.disclosure_type for item in record.disclosures] == [
        "interruption",
        "invalid_observation",
        "missing_data",
        "observation_reset",
    ]


def test_disclosure_completeness_is_descriptive_only():
    record = build_shadow_evidence(
        signal_observation=_signal_observation(),
        parity_observation=_parity_observation(),
        interruptions=["interruption"],
        invalid_observations=["invalid"],
        missing_data=["missing"],
        observation_resets=["reset"],
    )

    assert record.disclosure_complete is True
    assert "descriptive local context only" in record.disclosure_completeness_statement
    assert record.readiness_authority is False
    assert record.transition_authority is False
    assert record.approval_authority is False


def test_lineage_references_are_defensively_copied_and_preserved():
    lineage = ["signal-observation-1", "parity-observation-1"]

    record = build_shadow_evidence(
        signal_observation=_signal_observation(),
        parity_observation=_parity_observation(),
        lineage_references=lineage,
    )
    lineage.append("mutated")

    assert record.lineage_references == (
        "signal-observation-1",
        "parity-observation-1",
    )


def test_metadata_is_defensively_copied_and_preserved():
    tags = ["local", "shadow"]
    metadata = {"source": "manual-local", "tags": tags}

    record = build_shadow_evidence(
        signal_observation=_signal_observation(),
        parity_observation=_parity_observation(),
        metadata=metadata,
    )
    metadata["source"] = "mutated"
    tags.append("mutated")

    assert dict(record.metadata) == {"source": "manual-local", "tags": ["local", "shadow"]}
    with pytest.raises(TypeError):
        record.metadata["source"] = "mutated"  # type: ignore[index]


def test_caller_mutation_after_construction_does_not_mutate_disclosures():
    disclosure = ShadowDisclosure(
        disclosure_type="interruption",
        description="interrupted locally",
        metadata={"refs": ["before"]},
    )
    disclosures = [disclosure]

    record = build_shadow_evidence(
        signal_observation=_signal_observation(),
        parity_observation=_parity_observation(),
        interruptions=disclosures,
    )
    disclosures.append(
        ShadowDisclosure(
            disclosure_type="interruption",
            description="mutated list entry",
        )
    )
    disclosure.metadata["refs"].append("after")

    assert len(record.disclosures) == 1
    assert record.disclosures[0].description == "interrupted locally"
    assert dict(record.disclosures[0].metadata) == {"refs": ["before"]}


def test_local_dict_representation_is_non_canonical_and_non_authoritative():
    record = build_shadow_evidence(
        signal_observation=_signal_observation(),
        parity_observation=_parity_observation(),
        lineage_references=["signal-observation-1"],
        interruptions=["interruption"],
        invalid_observations=["invalid"],
        missing_data=["missing"],
        observation_resets=["reset"],
    )

    local_dict = record.to_local_dict()

    assert local_dict["canonical"] is False
    assert local_dict["decision_support_only"] is True
    assert local_dict["readiness_authority"] is False
    assert local_dict["transition_authority"] is False
    assert local_dict["approval_authority"] is False
    assert local_dict["human_gate_execution"] is False
    assert "no readiness" in local_dict["no_readiness_transition_approval_statement"]
    assert local_dict["signal_observation_id"] == "signal-observation-1"
    assert local_dict["parity_observation_id"] == "parity-observation-1"
    assert local_dict["disclosure_counts"] == {
        "interruption": 1,
        "invalid_observation": 1,
        "missing_data": 1,
        "observation_reset": 1,
    }


def test_module_does_not_expose_authority_execution_or_canonical_artifact_behavior():
    public_names = set(getattr(__import__("tools.shadow.evidence", fromlist=["__all__"]), "__all__"))

    assert public_names == {
        "DISCLOSURE_COMPLETENESS_STATEMENT",
        "NO_READINESS_TRANSITION_APPROVAL_STATEMENT",
        "DisclosureType",
        "ShadowDisclosure",
        "ShadowEvidenceRecord",
        "build_shadow_evidence",
        "disclosure_counts",
        "has_any_disclosure",
    }
    behavior_names = {
        name
        for name in public_names
        if name
        not in {
            "DISCLOSURE_COMPLETENESS_STATEMENT",
            "NO_READINESS_TRANSITION_APPROVAL_STATEMENT",
        }
    }
    forbidden_terms = (
        "ready",
        "readiness",
        "transition",
        "approval",
        "rank",
        "score",
        "recommend",
        "execute",
        "execution",
        "order",
        "artifact",
        "schema",
        "registry",
        "query",
    )
    assert not any(term in name.lower() for name in behavior_names for term in forbidden_terms)


def test_evidence_module_creates_no_output_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    record = build_shadow_evidence(
        signal_observation=_signal_observation(),
        parity_observation=_parity_observation(),
    )

    assert list(Path(tmp_path).iterdir()) == []
    assert isinstance(record, ShadowEvidenceRecord)


def test_empty_disclosures_are_deterministic():
    first = build_shadow_evidence(
        signal_observation=_signal_observation(),
        parity_observation=_parity_observation(),
        metadata={"source": "local"},
    )
    second = build_shadow_evidence(
        signal_observation=_signal_observation(),
        parity_observation=_parity_observation(),
        metadata={"source": "local"},
    )

    assert first == second
    assert has_any_disclosure(first) is False
    assert first.disclosure_complete is False
    assert disclosure_counts(first) == {
        "interruption": 0,
        "invalid_observation": 0,
        "missing_data": 0,
        "observation_reset": 0,
    }


def test_wrong_disclosure_type_in_typed_list_is_rejected():
    with pytest.raises(ValueError, match="wrong type"):
        build_shadow_evidence(
            signal_observation=_signal_observation(),
            parity_observation=_parity_observation(),
            interruptions=[
                ShadowDisclosure(
                    disclosure_type="missing_data",
                    description="wrong list",
                )
            ],
        )
