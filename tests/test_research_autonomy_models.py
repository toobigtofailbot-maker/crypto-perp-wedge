import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from tools.research_autonomy.envelope import envelope_hash, validate_control, validate_envelope
from tools.research_autonomy.models import BoundedResearchEnvelope

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/research_autonomy"
BASE = "9d9f8a94405ded76bbef0163488b9a8e0596371a"


def envelope_payload():
    return json.loads((FIXTURES / "bounded_research_envelope.fixture.json").read_text())


def test_schemas_and_fixtures_are_closed_and_hash_bound():
    for name in ("bounded_research_envelope", "bounded_research_envelope_control"):
        schema = json.loads((ROOT / f"research/schemas/{name}.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False
        assert all(d.get("additionalProperties") is False for d in schema["$defs"].values() if d.get("type") == "object")
    e = validate_envelope(envelope_payload(), repo_sha=BASE)
    control = json.loads((FIXTURES / "bounded_research_envelope_control.fixture.json").read_text())
    assert validate_control(control, envelope=e).action == "revoke"
    assert not (ROOT / "research/autonomy/envelopes").exists()


@pytest.mark.parametrize("field,value", [("approved_by", "Hermes"), ("extra", 1), ("envelope_version", True), ("content_sha256", "sha256:" + "1" * 64)])
def test_envelope_fails_closed(field, value):
    payload = envelope_payload()
    payload[field] = value
    with pytest.raises(Exception):
        validate_envelope(payload, repo_sha=BASE)


def test_nested_unknown_authority_and_repo_mismatch_fail():
    for group in ("authority", "budgets", "surface", "search_policy", "scientific_protocol", "evidence_policy"):
        payload = envelope_payload()
        payload[group]["extra"] = "not authority"
        payload["content_sha256"] = envelope_hash(payload)
        with pytest.raises(Exception):
            validate_envelope(payload, repo_sha=BASE)
    payload = envelope_payload()
    payload["authority"]["capital"] = True
    payload["content_sha256"] = envelope_hash(payload)
    with pytest.raises(Exception):
        validate_envelope(payload, repo_sha=BASE)
    with pytest.raises(ValueError, match="repo SHA"):
        validate_envelope(envelope_payload(), repo_sha="f" * 40)


def test_control_cross_binding_and_replacement_are_strict():
    envelope = validate_envelope(envelope_payload(), repo_sha=BASE)
    payload = json.loads((FIXTURES / "bounded_research_envelope_control.fixture.json").read_text())
    for update in ({"approved_by": "Prefect"}, {"action": "replace"}, {"envelope_content_sha256": "sha256:" + "0" * 64}, {"successor": {"envelope_id": "different", "envelope_version": 1, "content_sha256": "sha256:" + "0" * 64}}, {"runtime_authority": True}):
        with pytest.raises(Exception):
            validate_control({**payload, **update}, envelope=envelope)


def test_semantic_hash_excludes_only_hash_and_models_are_frozen():
    value = envelope_payload()
    changed = copy.deepcopy(value)
    changed["approved_at"] = "2026-10-07T00:00:00+00:00"
    assert envelope_hash(changed) != envelope_hash(value)
    envelope = BoundedResearchEnvelope.model_validate_json(json.dumps(value))
    with pytest.raises(Exception):
        envelope.envelope_version = 2
