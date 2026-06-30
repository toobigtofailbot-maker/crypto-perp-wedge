import copy
from pathlib import Path

from tools.lab_event_tape.validate import validate_tape


REFERENCE_TAPE = Path("scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/reference_event_tape.json")


def test_reference_tape_validates_identically_twice():
    first = validate_tape(REFERENCE_TAPE)
    second = validate_tape(REFERENCE_TAPE)

    assert first.valid
    assert second.valid
    assert first.to_dict() == second.to_dict()
    assert first.summary["event_count"] >= 40
    assert first.summary["job_count"] >= 10
    assert first.summary["source_reference_validation_mode"] == "strict_row_reference_validation"


def test_reference_tape_remains_non_promotable():
    result = validate_tape(REFERENCE_TAPE)

    assert result.summary["construction_payload_all_events"] is True
    assert result.summary["non_promotable_all_events"] is True
    assert result.summary["operating_test_evidence_all_events"] is True
    assert result.summary["strategy_evidence_any"] is False
    assert result.summary["candidate_eligible_any"] is False
    assert result.summary["promotion_eligible_any"] is False
    assert result.summary["paper_live_eligible_any"] is False
    assert result.summary["canonical_crossing_allowed_any"] is False
    assert result.summary["edge_claim_allowed_any"] is False
    assert result.summary["real_notification_sending_allowed_any"] is False
    assert result.summary["autonomous_scheduler_allowed_any"] is False


def test_closed_enum_violation_fails(tmp_path):
    tape = validate_tape(REFERENCE_TAPE).summary
    assert tape["tape_id"] == "LAB-EVENT-TAPE-REFERENCE-001"

    import json

    payload = json.loads(REFERENCE_TAPE.read_text(encoding="utf-8"))
    bad_payload = copy.deepcopy(payload)
    bad_payload["events"][0]["event_type"] = "candidate_promoted"
    bad_path = tmp_path / "bad_event_tape.json"
    bad_path.write_text(json.dumps(bad_payload), encoding="utf-8")

    result = validate_tape(bad_path)

    assert not result.valid
    assert result.closed_enum_validation == "fail"
    assert any("invalid event_type" in error for error in result.errors)


def test_promotable_flag_violation_fails(tmp_path):
    import json

    payload = json.loads(REFERENCE_TAPE.read_text(encoding="utf-8"))
    bad_payload = copy.deepcopy(payload)
    bad_payload["events"][0]["candidate_eligible"] = True
    bad_path = tmp_path / "bad_authority_event_tape.json"
    bad_path.write_text(json.dumps(bad_payload), encoding="utf-8")

    result = validate_tape(bad_path)

    assert not result.valid
    assert result.non_promotable_validation == "fail"
    assert any("candidate_eligible" in error for error in result.errors)
