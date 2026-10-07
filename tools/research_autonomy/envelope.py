"""Exact semantic/hash/repository binding for immutable human records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .models import BoundedResearchEnvelope, EnvelopeControlAction

SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "research/schemas"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def content_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def envelope_hash(value: dict[str, Any]) -> str:
    return content_hash({key: val for key, val in value.items() if key != "content_sha256"})


def _validated(value, model, schema_name):
    payload = value.model_dump(mode="json") if isinstance(value, model) else value
    schema = json.loads((SCHEMA_ROOT / schema_name).read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(payload)
    return model.model_validate_json(canonical_json(payload))


def validate_envelope(value, *, repo_sha: str) -> BoundedResearchEnvelope:
    envelope = _validated(value, BoundedResearchEnvelope, "bounded_research_envelope.schema.json")
    payload = envelope.model_dump(mode="json")
    if envelope.repo_sha != repo_sha:
        raise ValueError("envelope repo SHA mismatch")
    if envelope.content_sha256 != envelope_hash(payload):
        raise ValueError("envelope content hash mismatch")
    return envelope


def validate_control(value, *, envelope: BoundedResearchEnvelope) -> EnvelopeControlAction:
    control = _validated(value, EnvelopeControlAction, "bounded_research_envelope_control.schema.json")
    if (control.envelope_id, control.envelope_version, control.envelope_content_sha256, control.repo_sha) != (
        envelope.envelope_id, envelope.envelope_version, envelope.content_sha256, envelope.repo_sha
    ):
        raise ValueError("control envelope binding mismatch")
    return control
