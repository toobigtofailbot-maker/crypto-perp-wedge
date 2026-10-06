from __future__ import annotations

import copy
from pathlib import Path

import pytest
from pydantic import ValidationError

from tools.mcp.project_evidence.models import EvidenceUnavailableError, RepoIdentity
from tools.mcp.project_evidence.research_intent import (
    INTENT_SCHEMA_VERSION,
    MAX_FREE_PARAMETERS,
    REQUEST_SCHEMA_VERSION,
    BoundedResearchIntentBuilder,
    BoundedResearchIntentDraftInput,
    BoundedResearchIntentV1,
    BoundedResearchRequestV1,
    semantic_content_sha256,
)
from tools.mcp.project_evidence.resources import EvidenceResourceCatalog
from tools.research_memory.fingerprint import (
    DEFAULT_INSTRUMENT_SCOPE,
    FINGERPRINT_VERSION,
    HypothesisDefinition,
    fingerprint,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_SHA = "1" * 40


def _request(**updates: object) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "request_id": "REQ-HERMES-02-1",
        "research_question": "Can completed-bar breakout pressure persist out of sample?",
        "strategy_family": " Breakout Momentum ",
        "mechanism": " Price expansion after compressed ranges ",
        "primary_timeframe": "1h",
        "required_data_features": ["OHLCV", " Donchian "],
        "free_parameter_count": 2,
        "evidence_resource_uris": ["project://status"],
        "constraints": ["Use completed bars only"],
    }
    value.update(updates)
    return value


def _draft(**updates: object) -> dict[str, object]:
    value = {
        **_request(),
        "causal_rationale": "Range expansion may reflect persistent information arrival.",
        "falsifiable_prediction": "Preregistered OOS expectancy is positive after costs.",
        "falsification_stop_conditions": ["Stop if the preregistered OOS gate fails"],
        "proposed_parameter_bounds": [
            {"name": "Lookback", "minimum": 20.0, "maximum": 55.0}
        ],
        "proposed_objective_intent": "Evaluate robust OOS risk-adjusted return.",
        "unresolved_assumptions": ["Regime persistence remains uncertain"],
    }
    value.update(updates)
    return value


class _Memory:
    def __init__(self, *, matched: bool = True, available: bool = True, stale: bool = False):
        self.matched = matched
        self.available = available
        self.stale = stale

    def lookup_definition(self, definition: HypothesisDefinition) -> dict[str, object]:
        if not self.available:
            raise EvidenceUnavailableError("Research Memory unavailable")
        record = {
            "authority_state": "REPO_INDEX",
            "classification": "NO-GO",
            "repo_evidence_current": not self.stale,
            "resolved_classification": None if self.stale else "NO-GO",
            "evidence": [],
        }
        return {
            "matched": self.matched,
            "fingerprint_version": FINGERPRINT_VERSION,
            "fingerprint_sha256": fingerprint(definition),
            "definition": definition.canonical_mapping(),
            "index_not_truth": True,
            "records": [record] if self.matched else [],
            "repo_sha": REPO_SHA,
            "postgres_boundary": "default_transaction_read_only=on; SET TRANSACTION READ ONLY",
            "authority": {"not_scientific_truth": True},
        }


def _builder(memory: _Memory | None = None) -> BoundedResearchIntentBuilder:
    identity = RepoIdentity(repo_sha=REPO_SHA, branch="test")
    catalog = EvidenceResourceCatalog(REPO_ROOT, identity)
    return BoundedResearchIntentBuilder(catalog, memory or _Memory(), identity)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "update",
    [
        {"schema_version": "wrong"},
        {"request_id": "../escape"},
        {"research_question": "   "},
        {"strategy_family": ""},
        {"primary_timeframe": "5m"},
        {"required_data_features": ["ohlcv", " OHLCV "]},
        {"free_parameter_count": True},
        {"free_parameter_count": -1},
        {"free_parameter_count": MAX_FREE_PARAMETERS + 1},
        {"evidence_resource_uris": ["C:/repo/file"]},
        {"evidence_resource_uris": ["project://status", "project://status"]},
        {"constraints": ["enable shell command"]},
        {"instrument_scope": DEFAULT_INSTRUMENT_SCOPE},
        {"unknown": "x"},
    ],
)
def test_request_contract_fails_closed(update: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        BoundedResearchRequestV1.model_validate(_request(**update))


def test_request_normalizes_identity_deterministically() -> None:
    request = BoundedResearchRequestV1.model_validate(_request())
    assert request.strategy_family == "breakout momentum"
    assert request.mechanism == "Price expansion after compressed ranges"
    assert request.required_data_features == ["ohlcv", "donchian"]
    assert not hasattr(request, "instrument_scope")


@pytest.mark.parametrize(
    "update",
    [
        {"shell": "cmd"},
        {"repo_sha": REPO_SHA},
        {"fingerprint_sha256": "0" * 64},
        {"search_budget": 5},
        {"proposed_parameter_bounds": [{"name": "x", "minimum": 2.0, "maximum": 1.0}]},
        {"proposed_parameter_bounds": [{"name": "x", "minimum": float("inf"), "maximum": 2.0}]},
        {"proposed_parameter_bounds": [
            {"name": "x", "minimum": 1.0, "maximum": 2.0},
            {"name": "X", "minimum": 2.0, "maximum": 3.0},
        ]},
        {"falsification_stop_conditions": []},
    ],
)
def test_draft_contract_fails_closed(update: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        BoundedResearchIntentDraftInput.model_validate(_draft(**update))


def test_builder_binds_existing_fingerprint_evidence_repo_and_authority() -> None:
    intent = _builder().build(_draft())
    definition = HypothesisDefinition.from_mapping(
        {
            "strategy_family": "breakout momentum",
            "mechanism": "Price expansion after compressed ranges",
            "primary_timeframe": "1h",
            "required_data_features": ["ohlcv", "donchian"],
            "free_parameter_count": 2,
            "instrument_scope": DEFAULT_INSTRUMENT_SCOPE,
        }
    )
    assert intent.schema_version == INTENT_SCHEMA_VERSION
    assert intent.repo_sha == REPO_SHA
    assert intent.instrument_scope == DEFAULT_INSTRUMENT_SCOPE
    assert intent.fingerprint_sha256 == fingerprint(definition)
    assert intent.fingerprint_version == FINGERPRINT_VERSION
    assert intent.evidence_anchors[0].resource_uri == "project://status"
    assert intent.evidence_anchors[0].repo_sha == REPO_SHA
    assert intent.research_memory.matched is True
    assert intent.research_memory.index_not_truth is True
    assert intent.index_not_truth is True
    assert intent.automatic_consumers == []
    for field in (
        "canonical_write_authority", "approval_authority",
        "candidate_or_promotion_authority", "search_governor_authority",
        "final_holdout_authority", "scheduler_or_autonomy_authority",
        "runner_or_backtest_authority", "runtime_or_risk_authority",
        "paper_live_authority", "capital_authority",
    ):
        assert getattr(intent, field) is False
    assert intent.content_sha256 == semantic_content_sha256(intent)


def test_builder_no_match_stale_suppression_and_unavailable_memory() -> None:
    no_match = _builder(_Memory(matched=False)).build(_draft())
    assert no_match.research_memory.matched is False
    assert no_match.research_memory.records == []

    stale = _builder(_Memory(stale=True)).build(_draft())
    assert stale.research_memory.records[0]["resolved_classification"] is None

    with pytest.raises(EvidenceUnavailableError, match="unavailable"):
        _builder(_Memory(available=False)).build(_draft())


def test_semantic_hash_is_deterministic_changes_with_reasoning_and_excludes_session() -> None:
    first = _builder().build(_draft())
    second = _builder().build(copy.deepcopy(_draft()))
    changed = _builder().build(_draft(causal_rationale="A different bounded mechanism."))
    assert first == second
    assert first.content_sha256 != changed.content_sha256

    with_session = BoundedResearchIntentV1.model_validate(
        {**first.model_dump(mode="json"), "hermes_session_id": "session-123"}
    )
    assert semantic_content_sha256(with_session) == first.content_sha256


def test_intent_rejects_unknown_or_widened_boundary_fields() -> None:
    payload = _builder().build(_draft()).model_dump(mode="json")
    with pytest.raises(ValidationError):
        BoundedResearchIntentV1.model_validate({**payload, "approval_authority": True})
    with pytest.raises(ValidationError):
        BoundedResearchIntentV1.model_validate({**payload, "broker_authority": False})
