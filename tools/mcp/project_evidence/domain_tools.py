"""Strict compute-only transport adapters for CPW-owned research semantics."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from collections.abc import Mapping
from typing import Annotated, Any, Literal

from jsonschema import Draft7Validator
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator, model_validator

from tools.research_domain import (
    TRIAL_STATUSES,
    assess_capabilities,
    build_approval_requirement,
    build_preregistration_packet,
    formalize_reasoned_strategy_draft,
    validate_declared_trials,
    validate_trial_denominator,
)

from .models import RepoIdentity
from .resources import EvidenceResourceCatalog

CPW_DOMAIN_TOOLS_SCHEMA_VERSION = "cpw_hermes_domain_tools_v1"
CPW_DOMAIN_TOOL_RESULT_SCHEMA_VERSION = "cpw_domain_tool_result_v1"

CPW_DOMAIN_TOOL_NAMES = (
    "cpw_assess_research_capabilities",
    "cpw_formalize_strategy_draft",
    "cpw_build_preregistration_packet",
    "cpw_build_approval_requirement",
    "cpw_validate_trial_denominator",
)

INDICATOR_CATALOG_URI = "project://indicator-catalog"
FEATURE_AVAILABILITY_URI = "project://feature-availability"
STRATEGY_SPEC_TEMPLATE_URI = "project://strategy-spec-template"
STRATEGY_SPEC_SCHEMA_URI = "project://strategy-spec-schema"

NonEmptyString = Annotated[str, Field(min_length=1, max_length=8_192)]
ShortString = Annotated[str, Field(min_length=1, max_length=256)]


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


def _reject_non_finite(value: JsonValue) -> JsonValue:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite numeric values are not allowed")
    if isinstance(value, list):
        for item in value:
            _reject_non_finite(item)
    elif isinstance(value, dict):
        for item in value.values():
            _reject_non_finite(item)
    return value


class CapabilityAssessmentInput(_StrictModel):
    idea: NonEmptyString

    @field_validator("idea")
    @classmethod
    def _strip_idea(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("idea must be non-empty")
        return value.strip()


class ParameterBound(_StrictModel):
    name: ShortString
    minimum: float
    maximum: float

    @model_validator(mode="after")
    def _ordered_finite_bounds(self) -> ParameterBound:
        if not math.isfinite(self.minimum) or not math.isfinite(self.maximum):
            raise ValueError("parameter bounds must be finite")
        if self.minimum > self.maximum:
            raise ValueError("parameter bound minimum must be <= maximum")
        return self


class ReasonedDraft(_StrictModel):
    summary: NonEmptyString
    causal_rationale: NonEmptyString
    falsifiable_prediction: NonEmptyString
    symbols: Annotated[list[ShortString], Field(min_length=1, max_length=1)]
    timeframe: Literal["15m", "30m", "1h", "4h", "1d"]
    features: Annotated[list[ShortString], Field(min_length=1, max_length=32)]
    entry_concept: NonEmptyString
    exit_concept: NonEmptyString
    parameter_bounds: Annotated[list[ParameterBound], Field(max_length=32)]
    stop_conditions: Annotated[list[NonEmptyString], Field(min_length=1, max_length=32)]

    @model_validator(mode="after")
    def _unique_features_and_bounds(self) -> ReasonedDraft:
        if len(self.features) != len(set(self.features)):
            raise ValueError("reasoned_draft features must be unique")
        names = [item.name for item in self.parameter_bounds]
        if len(names) != len(set(names)):
            raise ValueError("reasoned_draft parameter bound names must be unique")
        return self


class FormalizeStrategyDraftInput(_StrictModel):
    idea: NonEmptyString
    symbol: Literal["BTCUSDT"]
    timeframe: Literal["15m", "30m", "1h", "4h", "1d"]
    constraints: Annotated[list[NonEmptyString], Field(max_length=64)]
    reasoned_draft: ReasonedDraft
    evidence_resource_uris: Annotated[list[ShortString], Field(max_length=64)]

    @model_validator(mode="after")
    def _validate_identity_lists(self) -> FormalizeStrategyDraftInput:
        if not self.idea.strip():
            raise ValueError("idea must be non-empty")
        if len(self.evidence_resource_uris) != len(set(self.evidence_resource_uris)):
            raise ValueError("evidence_resource_uris must be unique")
        for uri in self.evidence_resource_uris:
            if not uri.startswith(("project://", "evidence://")) or ".." in uri:
                raise ValueError("evidence resource identity is invalid")
        return self


class PreregistrationPacketInput(_StrictModel):
    pipeline_run_id: ShortString
    request: dict[str, JsonValue]
    formalized: dict[str, JsonValue]
    availability: dict[str, JsonValue]

    @model_validator(mode="after")
    def _validate_json_objects(self) -> PreregistrationPacketInput:
        if not isinstance(self.request.get("request_id"), str) or not self.request["request_id"]:
            raise ValueError("request.request_id is required")
        for value in (self.request, self.formalized, self.availability):
            _reject_non_finite(value)
        return self


class ApprovalRequirementInput(_StrictModel):
    preregistration_packet: dict[str, JsonValue]

    @field_validator("preregistration_packet")
    @classmethod
    def _validate_packet_json(cls, value: dict[str, JsonValue]) -> dict[str, JsonValue]:
        _reject_non_finite(value)
        return value


class DeclaredTrial(_StrictModel):
    strategy_family: ShortString
    variant_id: ShortString
    trial_id: ShortString
    params: dict[str, JsonValue]

    @field_validator("params")
    @classmethod
    def _validate_params(cls, value: dict[str, JsonValue]) -> dict[str, JsonValue]:
        _reject_non_finite(value)
        return value


class TrialLedgerRow(_StrictModel):
    trial_id: ShortString
    trial_status: Literal["completed", "failed", "invalid", "pruned", "blocked"]


class TrialDenominatorInput(_StrictModel):
    declared_trials: Annotated[list[DeclaredTrial], Field(min_length=1, max_length=10_000)]
    ledger: Annotated[list[TrialLedgerRow], Field(max_length=10_000)]

    @model_validator(mode="after")
    def _unique_declared_trials(self) -> TrialDenominatorInput:
        trial_ids = [trial.trial_id for trial in self.declared_trials]
        if len(trial_ids) != len(set(trial_ids)):
            raise ValueError("trial_id values must be unique")
        return self


class CpwDomainTools:
    """Evidence-bound adapters; all scientific meaning remains in research_domain."""

    def __init__(self, resources: EvidenceResourceCatalog, identity: RepoIdentity) -> None:
        self.resources = resources
        self.identity = identity

    @staticmethod
    def _typed(model_type: type[_StrictModel], value: _StrictModel | Mapping[str, Any]) -> Any:
        return value if isinstance(value, model_type) else model_type.model_validate(value)

    @staticmethod
    def _anchor(resource: Mapping[str, Any]) -> dict[str, Any]:
        evidence = resource["evidence"]
        return {
            "resource_uri": resource["resource_uri"],
            "repo_path": evidence["path"],
            "artifact_sha256": evidence["artifact_sha256"],
            "repo_sha": evidence["repo_sha"],
        }

    def _read_json(self, uri: str) -> tuple[dict[str, Any], dict[str, Any]]:
        resource = self.resources.read(uri)
        try:
            payload = json.loads(resource["content"])
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError(f"approved resource is not valid JSON: {uri}") from exc
        if not isinstance(payload, dict):
            raise TypeError(f"approved resource JSON root must be an object: {uri}")
        return payload, self._anchor(resource)

    @staticmethod
    def _input_sha256(typed_input: _StrictModel, anchors: list[dict[str, Any]]) -> str:
        canonical = json.dumps(
            {"input": typed_input.model_dump(mode="json"), "evidence_anchors": anchors},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
        return "sha256:" + hashlib.sha256(canonical).hexdigest()

    def _envelope(
        self,
        *,
        tool_name: str,
        typed_input: _StrictModel,
        anchors: list[dict[str, Any]],
        domain_semantics: Any,
    ) -> dict[str, Any]:
        return {
            "schema_version": CPW_DOMAIN_TOOL_RESULT_SCHEMA_VERSION,
            "tool_name": tool_name,
            "repo_sha": self.identity.repo_sha,
            "branch": self.identity.branch,
            "input_sha256": self._input_sha256(typed_input, anchors),
            "evidence_anchors": anchors,
            "domain_semantics": domain_semantics,
            "boundary": {
                "cpw_domain_semantics": True,
                "canonical_evidence": False,
                "canonical_write": False,
                "execution_authority": False,
                "approval_authority": False,
                "candidate_or_promotion_authority": False,
                "scheduler_or_prefect_authority": False,
                "runtime_or_risk_authority": False,
                "paper_live_authority": False,
                "capital_authority": False,
                "automatic_consumers": [],
            },
        }

    def assess_research_capabilities(
        self, request: CapabilityAssessmentInput | Mapping[str, Any]
    ) -> dict[str, Any]:
        typed = self._typed(CapabilityAssessmentInput, request)
        indicator, indicator_anchor = self._read_json(INDICATOR_CATALOG_URI)
        availability, availability_anchor = self._read_json(FEATURE_AVAILABILITY_URI)
        anchors = [indicator_anchor, availability_anchor]
        result = assess_capabilities(typed.idea, indicator, availability)
        return self._envelope(
            tool_name="cpw_assess_research_capabilities",
            typed_input=typed,
            anchors=anchors,
            domain_semantics=result,
        )

    def formalize_strategy_draft(
        self, request: FormalizeStrategyDraftInput | Mapping[str, Any]
    ) -> dict[str, Any]:
        typed = self._typed(FormalizeStrategyDraftInput, request)
        fixed: dict[str, dict[str, Any]] = {}
        anchors: list[dict[str, Any]] = []
        for uri in (
            INDICATOR_CATALOG_URI,
            FEATURE_AVAILABILITY_URI,
            STRATEGY_SPEC_TEMPLATE_URI,
            STRATEGY_SPEC_SCHEMA_URI,
        ):
            payload, anchor = self._read_json(uri)
            fixed[uri] = payload
            anchors.append(anchor)
        for uri in typed.evidence_resource_uris:
            anchors.append(self._anchor(self.resources.read(uri)))

        input_sha = self._input_sha256(typed, anchors)
        source_refs = [anchor["resource_uri"] for anchor in anchors]
        source_context = {
            "source_type": "manual_idea",
            "source_refs": source_refs,
            "prepared_by": "bounded CPW Project-Evidence Hermes domain tool",
            "source_constraints": [
                f"tool_schema={CPW_DOMAIN_TOOLS_SCHEMA_VERSION}",
                "Hermes/model reasoned draft is untrusted input, not repo evidence.",
                *[
                    f"evidence={anchor['resource_uri']}@{anchor['artifact_sha256']}"
                    for anchor in anchors
                ],
            ],
            "unresolved_claims": [
                "Noncanonical in-memory CPW domain draft; human review remains required.",
                "No approval, execution, candidate, promotion, runtime, or capital authority.",
            ],
            "review_notes": [
                "In-memory schema validation succeeds only as a format check, not approval."
            ],
            "lineage_ref_path": None,
            "lineage_ref_hash": input_sha,
            "default_title": "Draft CPW-domain SMA/stddev mean-reversion Strategy Spec",
        }
        result = formalize_reasoned_strategy_draft(
            idea=typed.idea,
            symbol=typed.symbol,
            timeframe=typed.timeframe,
            constraints=typed.constraints,
            reasoned_draft=typed.reasoned_draft.model_dump(mode="json"),
            indicator_catalog=fixed[INDICATOR_CATALOG_URI],
            availability_catalog=fixed[FEATURE_AVAILABILITY_URI],
            strategy_spec_template=fixed[STRATEGY_SPEC_TEMPLATE_URI],
            run_id=input_sha.removeprefix("sha256:")[:12],
            source_context=source_context,
        )
        validator = Draft7Validator(fixed[STRATEGY_SPEC_SCHEMA_URI])
        for spec in result["draft_strategy_specs"]:
            errors = sorted(validator.iter_errors(spec), key=lambda error: list(error.path))
            if errors:
                first = errors[0]
                location = ".".join(str(item) for item in first.path) or "<root>"
                raise ValueError(f"Strategy-Spec draft schema validation failed at {location}")
        return self._envelope(
            tool_name="cpw_formalize_strategy_draft",
            typed_input=typed,
            anchors=anchors,
            domain_semantics=result,
        )

    def build_preregistration_packet(
        self, request: PreregistrationPacketInput | Mapping[str, Any]
    ) -> dict[str, Any]:
        typed = self._typed(PreregistrationPacketInput, request)
        result = build_preregistration_packet(
            pipeline_run_id=typed.pipeline_run_id,
            request=typed.request,
            formalized=typed.formalized,
            availability=typed.availability,
        )
        return self._envelope(
            tool_name="cpw_build_preregistration_packet",
            typed_input=typed,
            anchors=[],
            domain_semantics=result,
        )

    def build_approval_requirement(
        self, request: ApprovalRequirementInput | Mapping[str, Any]
    ) -> dict[str, Any]:
        typed = self._typed(ApprovalRequirementInput, request)
        packet = self._validate_exact_preregistration_packet(typed.preregistration_packet)
        result = build_approval_requirement(packet)
        return self._envelope(
            tool_name="cpw_build_approval_requirement",
            typed_input=typed,
            anchors=[],
            domain_semantics=result,
        )

    @staticmethod
    def _validate_exact_preregistration_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
        try:
            pipeline_run_id = packet["pipeline_run_id"]
            frozen_content = packet["frozen_content"]
            if not isinstance(pipeline_run_id, str) or not pipeline_run_id:
                raise ValueError("pipeline_run_id is required")
            if not isinstance(frozen_content, Mapping):
                raise TypeError("frozen_content must be an object")
            request = frozen_content["request"]
            formalized = frozen_content["formalized_idea"]
            availability = frozen_content["availability_check"]
            if not all(isinstance(item, Mapping) for item in (request, formalized, availability)):
                raise TypeError("frozen preregistration inputs must be objects")
            reconstructed = build_preregistration_packet(
                pipeline_run_id=pipeline_run_id,
                request=request,
                formalized=formalized,
                availability=availability,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("preregistration packet is not the exact locked CPW packet") from exc
        if packet != reconstructed:
            raise ValueError("preregistration packet is not the exact locked CPW packet")
        return reconstructed

    def validate_trial_denominator(
        self, request: TrialDenominatorInput | Mapping[str, Any]
    ) -> dict[str, Any]:
        typed = self._typed(TrialDenominatorInput, request)
        declared = [item.model_dump(mode="json") for item in typed.declared_trials]
        ledger = [item.model_dump(mode="json") for item in typed.ledger]
        ordered_ids = [item["trial_id"] for item in declared]
        error_text: str | None = None
        try:
            validate_declared_trials(declared)
            validate_trial_denominator(ledger, ordered_ids)
        except ValueError as exc:
            error_text = str(exc)
        result = {
            "valid": error_text is None,
            "declared_count": len(declared),
            "ledger_count": len(ledger),
            "declared_trial_ids": ordered_ids,
            "ledger_trial_ids": [item["trial_id"] for item in ledger],
            "trial_status_counts": {
                status: Counter(item["trial_status"] for item in ledger).get(status, 0)
                for status in TRIAL_STATUSES
            },
            "error_code": None if error_text is None else "invalid_trial_denominator",
            "error_text": error_text,
        }
        return self._envelope(
            tool_name="cpw_validate_trial_denominator",
            typed_input=typed,
            anchors=[],
            domain_semantics=result,
        )
