"""Strict non-authoritative HERMES-02 bounded research-intent contract."""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from collections.abc import Mapping
from datetime import date, datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator, model_validator

from tools.research_memory.fingerprint import (
    DEFAULT_INSTRUMENT_SCOPE,
    FINGERPRINT_VERSION,
    HypothesisDefinition,
    fingerprint,
)

from .memory_reader import ReadOnlyResearchMemoryReader
from .models import EvidenceUnavailableError, RepoIdentity
from .resources import EvidenceResourceCatalog

REQUEST_SCHEMA_VERSION = "cpw_bounded_research_request_v1"
INTENT_SCHEMA_VERSION = "cpw_bounded_research_intent_v1"
MAX_FREE_PARAMETERS = 32
MAX_LIST_ITEMS = 64
MAX_REASONING_LENGTH = 8_192
_SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_CONTENT_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMMAND_SEMANTICS = re.compile(
    r"(?:\bshell\b|\bterminal\b|\bcommand\b|\bexecutable\b|\bdocker\b|"
    r"\bsubprocess\b|\btool[-_ ]?enable|\binstall\b|\bcurl\b|\bwget\b)",
    re.IGNORECASE,
)

ShortString = Annotated[str, Field(min_length=1, max_length=256)]
ReasoningString = Annotated[str, Field(min_length=1, max_length=MAX_REASONING_LENGTH)]
ResourceUri = Annotated[str, Field(min_length=1, max_length=512)]


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


def _normalized_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).strip().split())


def _normalized_identity(value: str) -> str:
    return _normalized_text(value).lower()


def _validate_nonempty(value: str) -> str:
    normalized = _normalized_text(value)
    if not normalized:
        raise ValueError("value must not be empty")
    return normalized


def _validate_unique(values: list[str], *, identity: bool = False) -> list[str]:
    normalized = [(_normalized_identity(value) if identity else _validate_nonempty(value)) for value in values]
    if len(normalized) != len(set(normalized)):
        raise ValueError("list identities must be unique")
    return normalized


class BoundedResearchRequestV1(_StrictModel):
    schema_version: Literal[REQUEST_SCHEMA_VERSION]
    request_id: Annotated[str, Field(min_length=1, max_length=128)]
    research_question: ReasoningString
    strategy_family: ShortString
    mechanism: ReasoningString
    primary_timeframe: Literal["15m", "30m", "1h", "4h", "1d"]
    required_data_features: Annotated[list[ShortString], Field(min_length=1, max_length=MAX_LIST_ITEMS)]
    free_parameter_count: Annotated[int, Field(ge=0, le=MAX_FREE_PARAMETERS)]
    evidence_resource_uris: Annotated[list[ResourceUri], Field(min_length=1, max_length=MAX_LIST_ITEMS)]
    constraints: Annotated[list[ReasoningString], Field(max_length=MAX_LIST_ITEMS)]

    @field_validator("request_id")
    @classmethod
    def _request_id(cls, value: str) -> str:
        if _SAFE_REQUEST_ID.fullmatch(value) is None or ".." in value:
            raise ValueError("request_id must be one safe identifier")
        return value

    @field_validator("research_question", "mechanism")
    @classmethod
    def _reasoning_text(cls, value: str) -> str:
        return _validate_nonempty(value)

    @field_validator("strategy_family")
    @classmethod
    def _family(cls, value: str) -> str:
        return _normalized_identity(value)

    @field_validator("required_data_features")
    @classmethod
    def _features(cls, value: list[str]) -> list[str]:
        return _validate_unique(value, identity=True)

    @field_validator("evidence_resource_uris")
    @classmethod
    def _resource_uris(cls, value: list[str]) -> list[str]:
        normalized = _validate_unique(value)
        for uri in normalized:
            if not uri.startswith(("project://", "evidence://")):
                raise ValueError("evidence resource must use project:// or evidence://")
            if ".." in uri or "\\" in uri or "?" in uri or "#" in uri:
                raise ValueError("evidence resource identity has path or URL semantics")
        return normalized

    @field_validator("constraints")
    @classmethod
    def _constraints(cls, value: list[str]) -> list[str]:
        normalized = _validate_unique(value)
        if any(_COMMAND_SEMANTICS.search(item) for item in normalized):
            raise ValueError("constraints may contain reasoning constraints only")
        return normalized


class ProposedParameterBound(_StrictModel):
    name: ShortString
    minimum: float
    maximum: float

    @field_validator("name")
    @classmethod
    def _name(cls, value: str) -> str:
        return _normalized_identity(value)

    @model_validator(mode="after")
    def _finite_ordered(self) -> ProposedParameterBound:
        if not math.isfinite(self.minimum) or not math.isfinite(self.maximum):
            raise ValueError("parameter bounds must be finite")
        if self.minimum > self.maximum:
            raise ValueError("parameter minimum must be <= maximum")
        return self


class BoundedResearchIntentDraftInput(_StrictModel):
    schema_version: Literal[REQUEST_SCHEMA_VERSION]
    request_id: Annotated[str, Field(min_length=1, max_length=128)]
    research_question: ReasoningString
    strategy_family: ShortString
    mechanism: ReasoningString
    primary_timeframe: Literal["15m", "30m", "1h", "4h", "1d"]
    required_data_features: Annotated[list[ShortString], Field(min_length=1, max_length=MAX_LIST_ITEMS)]
    free_parameter_count: Annotated[int, Field(ge=0, le=MAX_FREE_PARAMETERS)]
    evidence_resource_uris: Annotated[list[ResourceUri], Field(min_length=1, max_length=MAX_LIST_ITEMS)]
    constraints: Annotated[list[ReasoningString], Field(max_length=MAX_LIST_ITEMS)]
    causal_rationale: ReasoningString
    falsifiable_prediction: ReasoningString
    falsification_stop_conditions: Annotated[list[ReasoningString], Field(min_length=1, max_length=MAX_LIST_ITEMS)]
    proposed_parameter_bounds: Annotated[list[ProposedParameterBound], Field(max_length=MAX_FREE_PARAMETERS)]
    proposed_objective_intent: ReasoningString
    unresolved_assumptions: Annotated[list[ReasoningString], Field(max_length=MAX_LIST_ITEMS)]

    @model_validator(mode="after")
    def _request_and_reasoning_contract(self) -> BoundedResearchIntentDraftInput:
        BoundedResearchRequestV1.model_validate(
            self.model_dump(
                include={
                    "schema_version", "request_id", "research_question", "strategy_family",
                    "mechanism", "primary_timeframe", "required_data_features",
                    "free_parameter_count", "evidence_resource_uris", "constraints",
                }
            )
        )
        names = [bound.name for bound in self.proposed_parameter_bounds]
        if len(names) != len(set(names)):
            raise ValueError("proposed parameter names must be unique")
        for field_name in (
            "falsification_stop_conditions", "unresolved_assumptions"
        ):
            values = getattr(self, field_name)
            normalized = [_validate_nonempty(value) for value in values]
            if len(normalized) != len(set(normalized)):
                raise ValueError(f"{field_name} must contain unique non-empty values")
        return self


class EvidenceAnchor(_StrictModel):
    resource_uri: ResourceUri
    repo_path: Annotated[str, Field(min_length=1, max_length=512)]
    artifact_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    repo_sha: Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]


class ResearchMemoryContext(_StrictModel):
    fingerprint_version: Literal[FINGERPRINT_VERSION]
    fingerprint_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    matched: bool
    index_not_truth: Literal[True]
    records: list[dict[str, JsonValue]]
    repo_sha: Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
    postgres_boundary: Annotated[str, Field(min_length=1, max_length=512)]
    authority: dict[str, bool]


class BoundedResearchIntentV1(_StrictModel):
    schema_version: Literal[INTENT_SCHEMA_VERSION]
    request_id: Annotated[str, Field(min_length=1, max_length=128)]
    repo_sha: Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
    content_sha256: Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]
    strategy_family: ShortString
    mechanism: ReasoningString
    primary_timeframe: Literal["15m", "30m", "1h", "4h", "1d"]
    required_data_features: Annotated[list[ShortString], Field(min_length=1, max_length=MAX_LIST_ITEMS)]
    free_parameter_count: Annotated[int, Field(ge=0, le=MAX_FREE_PARAMETERS)]
    instrument_scope: Literal[DEFAULT_INSTRUMENT_SCOPE]
    fingerprint_version: Literal[FINGERPRINT_VERSION]
    fingerprint_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    research_question: ReasoningString
    causal_rationale: ReasoningString
    falsifiable_prediction: ReasoningString
    falsification_stop_conditions: Annotated[list[ReasoningString], Field(min_length=1, max_length=MAX_LIST_ITEMS)]
    proposed_parameter_bounds: Annotated[list[ProposedParameterBound], Field(max_length=MAX_FREE_PARAMETERS)]
    proposed_objective_intent: ReasoningString
    unresolved_assumptions: Annotated[list[ReasoningString], Field(max_length=MAX_LIST_ITEMS)]
    evidence_anchors: Annotated[list[EvidenceAnchor], Field(min_length=1, max_length=MAX_LIST_ITEMS)]
    research_memory: ResearchMemoryContext
    hermes_session_id: Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")] | None = None
    hermes_session_identity_is_operational_only: Literal[True] = True
    canonical_write_authority: Literal[False] = False
    approval_authority: Literal[False] = False
    candidate_or_promotion_authority: Literal[False] = False
    search_governor_authority: Literal[False] = False
    final_holdout_authority: Literal[False] = False
    scheduler_or_autonomy_authority: Literal[False] = False
    runner_or_backtest_authority: Literal[False] = False
    runtime_or_risk_authority: Literal[False] = False
    paper_live_authority: Literal[False] = False
    capital_authority: Literal[False] = False
    index_not_truth: Literal[True] = True
    automatic_consumers: Annotated[list[str], Field(max_length=0)] = Field(default_factory=list)


_OPERATIONAL_FIELDS = {"content_sha256", "hermes_session_id", "hermes_session_identity_is_operational_only"}


def semantic_content(value: BoundedResearchIntentV1 | Mapping[str, Any]) -> dict[str, Any]:
    intent = value if isinstance(value, BoundedResearchIntentV1) else BoundedResearchIntentV1.model_validate(value)
    return intent.model_dump(mode="json", exclude=_OPERATIONAL_FIELDS)


def semantic_content_sha256(value: BoundedResearchIntentV1 | Mapping[str, Any]) -> str:
    encoded = json.dumps(
        semantic_content(value), sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _json_safe(value: Any) -> JsonValue:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise EvidenceUnavailableError("Research Memory returned non-finite JSON")
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    raise EvidenceUnavailableError("Research Memory returned non-JSON content")


class BoundedResearchIntentBuilder:
    """Bind untrusted Hermes reasoning to exact CPW evidence and memory context."""

    def __init__(
        self,
        catalog: EvidenceResourceCatalog,
        memory: ReadOnlyResearchMemoryReader,
        identity: RepoIdentity,
    ) -> None:
        self._catalog = catalog
        self._memory = memory
        self._identity = identity

    def build(
        self, draft: BoundedResearchIntentDraftInput | Mapping[str, Any]
    ) -> BoundedResearchIntentV1:
        validated = (
            draft if isinstance(draft, BoundedResearchIntentDraftInput)
            else BoundedResearchIntentDraftInput.model_validate(draft)
        )
        definition = HypothesisDefinition.from_mapping(
            {
                "strategy_family": validated.strategy_family,
                "mechanism": validated.mechanism,
                "primary_timeframe": validated.primary_timeframe,
                "required_data_features": validated.required_data_features,
                "free_parameter_count": validated.free_parameter_count,
                "instrument_scope": DEFAULT_INSTRUMENT_SCOPE,
            }
        )
        fingerprint_sha256 = fingerprint(definition)
        anchors = []
        for uri in validated.evidence_resource_uris:
            resolved = self._catalog.read(uri)
            evidence = resolved["evidence"]
            anchors.append(
                EvidenceAnchor(
                    resource_uri=uri,
                    repo_path=evidence["path"],
                    artifact_sha256=evidence["artifact_sha256"],
                    repo_sha=evidence["repo_sha"],
                )
            )
        lookup = self._memory.lookup_definition(definition)
        if lookup.get("repo_sha") != self._identity.repo_sha:
            raise EvidenceUnavailableError("Research Memory repo identity mismatch")
        if lookup.get("fingerprint_sha256") != fingerprint_sha256:
            raise EvidenceUnavailableError("Research Memory fingerprint mismatch")
        memory_context = ResearchMemoryContext.model_validate(
            {
                "fingerprint_version": lookup["fingerprint_version"],
                "fingerprint_sha256": lookup["fingerprint_sha256"],
                "matched": lookup["matched"],
                "index_not_truth": lookup["index_not_truth"],
                "records": _json_safe(lookup["records"]),
                "repo_sha": lookup["repo_sha"],
                "postgres_boundary": lookup["postgres_boundary"],
                "authority": lookup["authority"],
            }
        )
        payload = {
            "schema_version": INTENT_SCHEMA_VERSION,
            "request_id": validated.request_id,
            "repo_sha": self._identity.repo_sha,
            "content_sha256": "sha256:" + "0" * 64,
            **definition.canonical_mapping(),
            "fingerprint_sha256": fingerprint_sha256,
            "research_question": validated.research_question,
            "causal_rationale": validated.causal_rationale,
            "falsifiable_prediction": validated.falsifiable_prediction,
            "falsification_stop_conditions": validated.falsification_stop_conditions,
            "proposed_parameter_bounds": validated.proposed_parameter_bounds,
            "proposed_objective_intent": validated.proposed_objective_intent,
            "unresolved_assumptions": validated.unresolved_assumptions,
            "evidence_anchors": anchors,
            "research_memory": memory_context,
        }
        provisional = BoundedResearchIntentV1.model_validate(payload)
        return provisional.model_copy(
            update={"content_sha256": semantic_content_sha256(provisional)}
        )
