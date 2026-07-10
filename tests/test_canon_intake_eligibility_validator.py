import copy
import json
from pathlib import Path

import pytest

from tools.canon_intake.eligibility_validator import (
    EligibilityValidationError,
    validate_draft_eligibility,
)


DRAFT_ID = "AIDRAFT-0123456789ABCDEF"


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def _packet(hypothesis="Price acceleration has positive out-of-sample expectancy after costs."):
    return {
        "schema_version": "agent_inbox_intake_draft_packet_v1",
        "draft_id": DRAFT_ID,
        "source_request": {
            "title": "Price acceleration continuation",
            "hypothesis_text": hypothesis,
            "market_hint": "BTCUSDT",
            "timeframe_hint": "15m",
        },
        "formalizer_result": {
            "research_object": {
                "summary": hypothesis,
                "falsifiable_prediction": "The signal has positive out-of-sample expectancy after costs.",
                "symbols": ["BTCUSDT"],
                "timeframe": "15m",
                "features": ["close"],
                "parameter_bounds": [{"name": "lookback", "minimum": 5, "maximum": 20}],
            }
        },
        "availability_primitive_check": {
            "feature_assessments": [{"feature": "close"}],
            "blocking_features": [],
            "historically_testable_now": True,
        },
        "provenance": {"package_id": "test"},
        "source_hashes": {"source_request_sha256": "sha256:test"},
        "blockers": [],
    }


def _repo(tmp_path: Path, packet=None, review_state="reviewed") -> Path:
    _write(tmp_path / "scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts" / f"{DRAFT_ID}.draft_packet.json", packet or _packet())
    if review_state:
        event = {"draft_id": DRAFT_ID, "append_index": 1, "review_state": review_state}
        path = tmp_path / "scratch/WP-DASH-AGENT-INBOX-WRITE-01A/reviews" / f"{DRAFT_ID}.review_events.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(event) + "\n", encoding="utf-8")
    _write(tmp_path / "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json", {"strategy_spec_id": "STRAT-SPEC-9999", "title": "Unrelated calendar strategy", "short_name": "calendar", "entry_logic": {}, "exit_logic": {}, "timeframe_and_data": {"primary_timeframe": "1d"}})
    _write(tmp_path / "research/result_populations/RP-9999.result_population.json", {"result_population_id": "RP-9999", "lineage": {"strategy_spec_id": "STRAT-SPEC-9999"}})
    registry = tmp_path / "research/candidate_registry.jsonl"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(json.dumps({"candidate_id": "H-999", "status": "CONCLUDED", "name": "Unrelated calendar strategy", "strategy_family": "calendar", "timeframe": "1d", "differentiation_summary": "Day of week"}) + "\n", encoding="utf-8")
    return tmp_path


def test_reviewed_draft_is_deterministic_and_advisory_only(tmp_path):
    root = _repo(tmp_path)
    first = validate_draft_eligibility(DRAFT_ID, repo_root=root)
    second = validate_draft_eligibility(DRAFT_ID, repo_root=root)
    assert first == second
    assert first["eligibility_status"] == "eligible_for_gate_c_review"
    assert first["advisory_only"] is True
    assert first["canonical_authority"] is False
    assert first["gate_c_authority"] is False
    assert first["queue_authority"] is False
    assert list((root / "scratch/WP-CANON-ELIGIBILITY-VALIDATOR-01/reports").glob("*"))
    assert not (root / "research/strategy_specs/STRAT-SPEC-0001.strategy_spec.json").exists()
    assert not (root / "research/candidate_registry.created.jsonl").exists()


def test_incomplete_draft_needs_clarification(tmp_path):
    packet = _packet()
    packet["formalizer_result"]["research_object"].pop("falsifiable_prediction")
    packet["formalizer_result"]["research_object"].pop("parameter_bounds")
    report = validate_draft_eligibility(DRAFT_ID, repo_root=_repo(tmp_path, packet))
    assert report["eligibility_status"] == "needs_clarification"
    assert report["checks"]["falsifiable_hypothesis"]["status"] == "unknown"


def test_malformed_draft_fails_closed_without_report(tmp_path):
    root = _repo(tmp_path)
    draft = root / "scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts" / f"{DRAFT_ID}.draft_packet.json"
    draft.write_text("{bad", encoding="utf-8")
    with pytest.raises(EligibilityValidationError):
        validate_draft_eligibility(DRAFT_ID, repo_root=root)
    assert not (root / "scratch/WP-CANON-ELIGIBILITY-VALIDATOR-01/reports").exists()


@pytest.mark.parametrize(("field", "value", "check"), [("market_hint", "ETHUSDT", "bounded_market"), ("timeframe_hint", "2h", "bounded_timeframe")])
def test_unbounded_market_or_timeframe_is_ineligible(tmp_path, field, value, check):
    packet = _packet()
    packet["source_request"][field] = value
    report = validate_draft_eligibility(DRAFT_ID, repo_root=_repo(tmp_path, packet))
    assert report["eligibility_status"] == "ineligible"
    assert report["checks"][check]["status"] == "fail"


def test_missing_provenance_is_reported(tmp_path):
    packet = _packet()
    packet.pop("provenance")
    report = validate_draft_eligibility(DRAFT_ID, repo_root=_repo(tmp_path, packet))
    assert report["checks"]["provenance_completeness"]["status"] == "fail"


def test_known_concluded_family_and_population_are_detected(tmp_path):
    packet = _packet("A 15m SMA distance mean reversion signal buys below the moving average and exits at the average.")
    packet["source_request"]["title"] = "SMA distance mean reversion"
    root = _repo(tmp_path, packet)
    registry = root / "research/candidate_registry.jsonl"
    registry.write_text(json.dumps({"candidate_id": "H-003", "status": "CONCLUDED", "name": "SMA Distance Mean Reversion", "strategy_family": "mean_reversion", "timeframe": "15m", "differentiation_summary": "Buy below moving average and exit at average"}) + "\n", encoding="utf-8")
    _write(root / "research/strategy_specs/STRAT-SPEC-0001.strategy_spec.json", {"strategy_spec_id": "STRAT-SPEC-0001", "title": "SMA Distance Mean Reversion", "short_name": "sma-distance-15m", "entry_logic": {"notes": "buy below moving average"}, "exit_logic": {"notes": "exit at moving average"}, "timeframe_and_data": {"primary_timeframe": "15m"}})
    _write(root / "research/result_populations/RP-2134.result_population.json", {"result_population_id": "RP-2134", "lineage": {"strategy_spec_id": "STRAT-SPEC-0001"}})
    report = validate_draft_eligibility(DRAFT_ID, repo_root=root)
    types = {item["match_type"] for item in report["duplicate_near_duplicate_candidates"]}
    assert "concluded_candidate_near_duplicate" in types
    assert "canonical_family_near_duplicate" in types
    assert "result_population_lineage_match" in types
    assert report["eligibility_status"] == "ineligible"
