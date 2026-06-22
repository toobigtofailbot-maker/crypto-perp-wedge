"""Provider-switchable reasoning seam with no live API implementation."""

from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol

from jsonschema import Draft7Validator


PROVIDER_RESPONSE_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "request_id", "decision", "draft", "rejection_reasons"],
    "properties": {
        "schema_version": {"const": "agent_idea_draft_v1"},
        "request_id": {"type": "string", "minLength": 1},
        "decision": {"enum": ["accepted", "rejected"]},
        "draft": {
            "type": ["object", "null"],
            "additionalProperties": False,
            "required": [
                "summary",
                "causal_rationale",
                "falsifiable_prediction",
                "symbols",
                "timeframe",
                "features",
                "entry_concept",
                "exit_concept",
                "parameter_bounds",
                "stop_conditions",
            ],
            "properties": {
                "summary": {"type": "string", "minLength": 1},
                "causal_rationale": {"type": "string", "minLength": 1},
                "falsifiable_prediction": {"type": "string", "minLength": 1},
                "symbols": {
                    "type": "array",
                    "minItems": 1,
                    "uniqueItems": True,
                    "items": {"type": "string", "minLength": 1},
                },
                "timeframe": {"enum": ["15m", "30m", "1h", "4h", "1d"]},
                "features": {
                    "type": "array",
                    "minItems": 1,
                    "uniqueItems": True,
                    "items": {"type": "string", "minLength": 1},
                },
                "entry_concept": {"type": "string", "minLength": 1},
                "exit_concept": {"type": "string", "minLength": 1},
                "parameter_bounds": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["name", "minimum", "maximum"],
                        "properties": {
                            "name": {"type": "string", "minLength": 1},
                            "minimum": {"type": "number"},
                            "maximum": {"type": "number"},
                        },
                    },
                },
                "stop_conditions": {
                    "type": "array",
                    "minItems": 1,
                    "items": {"type": "string", "minLength": 1},
                },
            },
        },
        "rejection_reasons": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
    },
    "allOf": [
        {
            "if": {"properties": {"decision": {"const": "accepted"}}},
            "then": {
                "properties": {
                    "draft": {"type": "object"},
                    "rejection_reasons": {"maxItems": 0},
                }
            },
            "else": {
                "properties": {
                    "draft": {"type": "null"},
                    "rejection_reasons": {"minItems": 1},
                }
            },
        }
    ],
}


@dataclass(frozen=True)
class ProviderRequest:
    request_id: str
    provider_mode: str
    provider_id: str
    context: Mapping[str, Any]


@dataclass(frozen=True)
class ProviderResponse:
    request_id: str
    status: str
    response_source: str
    payload: Mapping[str, Any] | None


@dataclass(frozen=True)
class StructuredAgentDraft:
    decision: str
    draft: Mapping[str, Any] | None
    rejection_reasons: tuple[str, ...]


class ProviderResponseError(ValueError):
    """Raised when an imported or generated provider response is invalid."""


class ProviderUnavailableError(RuntimeError):
    """Raised by explicit future-provider placeholders."""


class ReasoningProvider(Protocol):
    provider_id: str
    mode: str

    def build_request(self, context: Mapping[str, Any]) -> ProviderRequest: ...

    def complete(self, request: ProviderRequest) -> ProviderResponse: ...

    def parse_response(self, response: ProviderResponse) -> StructuredAgentDraft: ...


def validate_provider_payload(payload: Mapping[str, Any], *, expected_request_id: str) -> list[str]:
    validator = Draft7Validator(PROVIDER_RESPONSE_SCHEMA)
    errors = []
    for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"{location}: {error.message}")
    if payload.get("request_id") != expected_request_id:
        errors.append("request_id does not match the active provider request")
    draft = payload.get("draft")
    if isinstance(draft, Mapping):
        for index, bound in enumerate(draft.get("parameter_bounds", [])):
            minimum = bound.get("minimum") if isinstance(bound, Mapping) else None
            maximum = bound.get("maximum") if isinstance(bound, Mapping) else None
            if (
                isinstance(minimum, (int, float))
                and isinstance(maximum, (int, float))
                and minimum > maximum
            ):
                errors.append(f"draft.parameter_bounds.{index}: minimum must be <= maximum")
    return errors


class BaseProvider:
    mode = "base"
    provider_id = "base"

    def build_request(self, context: Mapping[str, Any]) -> ProviderRequest:
        return ProviderRequest(
            request_id=str(context["request_id"]),
            provider_mode=self.mode,
            provider_id=self.provider_id,
            context=copy.deepcopy(dict(context)),
        )

    def parse_response(self, response: ProviderResponse) -> StructuredAgentDraft:
        if response.status != "completed" or response.payload is None:
            raise ProviderResponseError(f"provider response is not complete: {response.status}")
        errors = validate_provider_payload(
            response.payload, expected_request_id=response.request_id
        )
        if errors:
            raise ProviderResponseError("; ".join(errors))
        return StructuredAgentDraft(
            decision=str(response.payload["decision"]),
            draft=copy.deepcopy(response.payload["draft"]),
            rejection_reasons=tuple(response.payload["rejection_reasons"]),
        )


def _extract_bound(text: str, name: str, default: tuple[int, int]) -> dict[str, Any]:
    pattern = re.compile(
        rf"\b{name.replace('_', '[ _-]')}\b[^.;]*?\b(?:from|between)\s+"
        rf"(-?\d+(?:\.\d+)?)\s+(?:to|and)\s+(-?\d+(?:\.\d+)?)",
        re.I,
    )
    match = pattern.search(text)
    low, high = default if match is None else (float(match.group(1)), float(match.group(2)))
    low, high = sorted((low, high))
    return {"name": name, "minimum": low, "maximum": high}


class FakeOfflineProvider(BaseProvider):
    """Deterministic rule-based provider for tests and CI."""

    mode = "fake_offline"
    provider_id = "fake-rule-v1"

    def complete(self, request: ProviderRequest) -> ProviderResponse:
        idea = str(request.context["idea"]).strip()
        lower = idea.casefold()
        has_causal_signal = any(
            marker in lower
            for marker in ("because", "due to", "mean revert", "momentum", "liquidity", "pressure")
        )
        known_features = [
            feature
            for feature in request.context.get("detected_features", [])
            if isinstance(feature, str)
        ]
        if not has_causal_signal:
            payload: dict[str, Any] = {
                "schema_version": "agent_idea_draft_v1",
                "request_id": request.request_id,
                "decision": "rejected",
                "draft": None,
                "rejection_reasons": ["idea lacks an explicit causal mechanism"],
            }
        elif not known_features:
            payload = {
                "schema_version": "agent_idea_draft_v1",
                "request_id": request.request_id,
                "decision": "rejected",
                "draft": None,
                "rejection_reasons": ["idea names no supported data or indicator primitive"],
            }
        else:
            symbol = str(request.context.get("symbol") or "BTCUSDT")
            timeframe = str(request.context.get("timeframe") or "15m")
            payload = {
                "schema_version": "agent_idea_draft_v1",
                "request_id": request.request_id,
                "decision": "accepted",
                "draft": {
                    "summary": idea,
                    "causal_rationale": idea,
                    "falsifiable_prediction": (
                        "The completed-bar signal has positive out-of-sample expectancy after costs."
                    ),
                    "symbols": [symbol],
                    "timeframe": timeframe,
                    "features": known_features,
                    "entry_concept": "Evaluate on completed bars and enter at the next bar open.",
                    "exit_concept": "Exit on the declared signal reversal or bounded holding limit.",
                    "parameter_bounds": [
                        _extract_bound(idea, "center_lookback_bars", (50, 100)),
                        _extract_bound(idea, "vol_lookback_bars", (30, 50)),
                        _extract_bound(idea, "trend_lookback_bars", (100, 200)),
                    ],
                    "stop_conditions": ["Stop if preregistered out-of-sample thresholds fail."],
                },
                "rejection_reasons": [],
            }
        return ProviderResponse(
            request_id=request.request_id,
            status="completed",
            response_source="deterministic_fake",
            payload=payload,
        )


class ChatGPTAccountPacketProvider(BaseProvider):
    """Operator-mediated ChatGPT mode; never invokes a network or API client."""

    mode = "chatgpt_account_packet"
    provider_id = "chatgpt-account-operator-v1"

    def __init__(self, response_loader: Callable[[], str] | None = None) -> None:
        self._response_loader = response_loader

    def complete(self, request: ProviderRequest) -> ProviderResponse:
        if self._response_loader is None:
            return ProviderResponse(
                request_id=request.request_id,
                status="pending_operator",
                response_source="operator_pending",
                payload=None,
            )
        try:
            payload = json.loads(self._response_loader())
        except json.JSONDecodeError as exc:
            raise ProviderResponseError(f"provider response is not valid JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise ProviderResponseError("provider response JSON root must be an object")
        return ProviderResponse(
            request_id=request.request_id,
            status="completed",
            response_source="operator_imported_local_file",
            payload=payload,
        )


class DisabledProvider(BaseProvider):
    """Explicit placeholder for future providers requiring separate authority."""

    def __init__(self, mode: str) -> None:
        if mode not in {"openai_api_disabled", "anthropic_api_disabled", "local_model_disabled"}:
            raise ValueError(f"unsupported disabled provider mode: {mode}")
        self.mode = mode
        self.provider_id = mode

    def complete(self, request: ProviderRequest) -> ProviderResponse:
        del request
        raise ProviderUnavailableError(
            f"{self.mode} is disabled; future explicit configuration and authority are required"
        )
