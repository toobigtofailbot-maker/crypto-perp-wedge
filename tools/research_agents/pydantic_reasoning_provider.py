"""Offline-only Pydantic AI adapter for the repo-owned ReasoningProvider seam."""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field
from enum import Enum
from importlib.metadata import version
from threading import Event
from types import MappingProxyType
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.models.test import TestModel

from .reasoning_providers import (
    BaseProvider,
    ProviderRequest,
    ProviderResponse,
    ProviderResponseError,
    ProviderUnavailableError,
)

RUNTIME_DISTRIBUTION = "pydantic-ai-slim"
ADAPTER_VERSION = "pydantic-reasoning-provider-v1"
NON_AUTHORITY = (
    "reasoning metadata only; no canonical, promotion, dispatch, runtime, OMS, risk, "
    "reconciliation, exchange, order, capital, credential, or ToolContext-bypass authority"
)


class CapabilityTier(str, Enum):
    CHEAP = "CHEAP"
    STANDARD = "STANDARD"
    FRONTIER = "FRONTIER"


@dataclass(frozen=True)
class PydanticTierProfile:
    tier: CapabilityTier
    provider: str
    model: str
    reasoning_configuration: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not self.provider or not self.model:
            raise ValueError("tier provider and model must be non-empty")
        object.__setattr__(
            self,
            "reasoning_configuration",
            MappingProxyType(copy.deepcopy(dict(self.reasoning_configuration))),
        )


@dataclass(frozen=True)
class PydanticTierCatalog:
    profiles: Mapping[CapabilityTier, PydanticTierProfile]

    def __post_init__(self) -> None:
        normalized = {CapabilityTier(key): value for key, value in self.profiles.items()}
        expected = set(CapabilityTier)
        if set(normalized) != expected:
            missing = sorted(item.value for item in expected - set(normalized))
            extra = sorted(str(item) for item in set(normalized) - expected)
            raise ValueError(
                "tier catalog must define CHEAP/STANDARD/FRONTIER; "
                f"missing={missing}, extra={extra}"
            )
        for tier, profile in normalized.items():
            if profile.tier != tier:
                raise ValueError(f"tier catalog key/profile mismatch: {tier.value}")
        object.__setattr__(self, "profiles", MappingProxyType(normalized))

    def select(self, tier: CapabilityTier) -> PydanticTierProfile:
        return self.profiles[CapabilityTier(tier)]


@dataclass(frozen=True)
class PydanticRuntimeConfig:
    tier: CapabilityTier
    tier_catalog: PydanticTierCatalog
    timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.tier_catalog.select(self.tier)


class ProviderCancellationToken:
    """Small caller-owned cancellation signal for the synchronous provider seam."""

    def __init__(self) -> None:
        self._event = Event()

    def cancel(self) -> None:
        self._event.set()

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()


class ProviderTimeoutError(ProviderUnavailableError):
    """Raised when a bounded Pydantic reasoning run exceeds its configured timeout."""


class ProviderCancelledError(ProviderUnavailableError):
    """Raised when a caller cancels a bounded Pydantic reasoning run."""


@dataclass(frozen=True)
class ProviderTraceEvent:
    event: str
    request_id: str
    provider: str
    model: str
    reasoning_tier: str
    runtime_distribution: str
    runtime_version: str
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "details", MappingProxyType(copy.deepcopy(dict(self.details))))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": self.event,
            "request_id": self.request_id,
            "provider": self.provider,
            "model": self.model,
            "reasoning_tier": self.reasoning_tier,
            "runtime_distribution": self.runtime_distribution,
            "runtime_version": self.runtime_version,
            "details": copy.deepcopy(dict(self.details)),
        }


class ProviderTraceSink(Protocol):
    def emit(self, event: ProviderTraceEvent) -> None: ...


class MemoryProviderTraceSink:
    """Local deterministic trace seam; P3 may adapt this protocol to OTel later."""

    def __init__(self) -> None:
        self.events: list[ProviderTraceEvent] = []

    def emit(self, event: ProviderTraceEvent) -> None:
        self.events.append(event)


class _NullProviderTraceSink:
    def emit(self, event: ProviderTraceEvent) -> None:
        del event


class PydanticParameterBound(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    minimum: float
    maximum: float

    @model_validator(mode="after")
    def minimum_not_above_maximum(self) -> PydanticParameterBound:
        if self.minimum > self.maximum:
            raise ValueError("minimum must be <= maximum")
        return self


class PydanticAgentDraft(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    summary: str = Field(min_length=1)
    causal_rationale: str = Field(min_length=1)
    falsifiable_prediction: str = Field(min_length=1)
    symbols: list[str] = Field(min_length=1)
    timeframe: Literal["15m", "30m", "1h", "4h", "1d"]
    features: list[str] = Field(min_length=1)
    entry_concept: str = Field(min_length=1)
    exit_concept: str = Field(min_length=1)
    parameter_bounds: list[PydanticParameterBound]
    stop_conditions: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_non_empty_lists(self) -> PydanticAgentDraft:
        if any(not item for item in self.symbols + self.features + self.stop_conditions):
            raise ValueError("symbols, features, and stop_conditions must be non-empty strings")
        if len(set(self.symbols)) != len(self.symbols):
            raise ValueError("symbols must be unique")
        if len(set(self.features)) != len(self.features):
            raise ValueError("features must be unique")
        return self


class PydanticProviderPayload(BaseModel):
    """Typed counterpart of the existing agent_idea_draft_v1 JSON contract."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["agent_idea_draft_v1"]
    request_id: str = Field(min_length=1)
    decision: Literal["accepted", "rejected"]
    draft: PydanticAgentDraft | None
    rejection_reasons: list[str]

    @model_validator(mode="after")
    def decision_shape(self) -> PydanticProviderPayload:
        if self.decision == "accepted" and (self.draft is None or self.rejection_reasons):
            raise ValueError("accepted output requires a draft and no rejection reasons")
        if self.decision == "rejected" and (self.draft is not None or not self.rejection_reasons):
            raise ValueError("rejected output requires no draft and at least one rejection reason")
        if any(not reason for reason in self.rejection_reasons):
            raise ValueError("rejection reasons must be non-empty strings")
        return self


OfflineModel = TestModel | FunctionModel
OfflineModelFactory = Callable[[ProviderRequest, PydanticTierProfile], OfflineModel]


class PydanticReasoningProvider(BaseProvider):
    """Pydantic AI reasoning adapter with no live-provider or project-tool surface."""

    mode = "pydantic_ai_offline"

    def __init__(
        self,
        *,
        config: PydanticRuntimeConfig,
        model_factory: OfflineModelFactory,
        trace_sink: ProviderTraceSink | None = None,
    ) -> None:
        self.config = config
        self.profile = config.tier_catalog.select(config.tier)
        self.provider_id = self.profile.provider
        self._model_factory = model_factory
        self._trace_sink = trace_sink or _NullProviderTraceSink()
        self.runtime_version = version(RUNTIME_DISTRIBUTION)

    def _trace(self, event: str, request_id: str, **details: Any) -> None:
        self._trace_sink.emit(
            ProviderTraceEvent(
                event=event,
                request_id=request_id,
                provider=self.profile.provider,
                model=self.profile.model,
                reasoning_tier=self.profile.tier.value,
                runtime_distribution=RUNTIME_DISTRIBUTION,
                runtime_version=self.runtime_version,
                details=details,
            )
        )

    @staticmethod
    def _canonical_json(value: Mapping[str, Any]) -> str:
        try:
            return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        except (TypeError, ValueError) as exc:
            raise ProviderResponseError(
                f"provider request context is not JSON serializable: {exc}"
            ) from exc

    def _make_offline_model(self, request: ProviderRequest) -> OfflineModel:
        model = self._model_factory(request, self.profile)
        if not isinstance(model, (TestModel, FunctionModel)):
            raise ProviderUnavailableError(
                "Pydantic runtime accepts only injected TestModel or FunctionModel instances; "
                "live provider/network activation remains disabled"
            )
        actual_provider = str(model.system)
        actual_model = str(model.model_name)
        if actual_provider != self.profile.provider or actual_model != self.profile.model:
            raise ProviderUnavailableError(
                "injected offline model identity does not match the selected tier profile: "
                f"expected={self.profile.provider}/{self.profile.model}, "
                f"actual={actual_provider}/{actual_model}"
            )
        return model

    async def _run_agent(
        self,
        agent: Agent[None, PydanticProviderPayload],
        prompt: str,
        request_id: str,
        cancellation_token: ProviderCancellationToken | None,
    ) -> Any:
        if cancellation_token is not None and cancellation_token.cancelled:
            raise ProviderCancelledError(f"Pydantic reasoning request cancelled: {request_id}")
        task = asyncio.create_task(agent.run(prompt, run_id=request_id))
        loop = asyncio.get_running_loop()
        deadline = loop.time() + self.config.timeout_seconds
        try:
            while True:
                if cancellation_token is not None and cancellation_token.cancelled:
                    raise ProviderCancelledError(
                        f"Pydantic reasoning request cancelled: {request_id}"
                    )
                remaining = deadline - loop.time()
                if remaining <= 0:
                    raise ProviderTimeoutError(
                        "Pydantic reasoning request timed out after "
                        f"{self.config.timeout_seconds:g}s: {request_id}"
                    )
                done, _ = await asyncio.wait(
                    {task}, timeout=min(0.01, remaining), return_when=asyncio.FIRST_COMPLETED
                )
                if task in done:
                    return task.result()
        finally:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    def complete(
        self,
        request: ProviderRequest,
        *,
        cancellation_token: ProviderCancellationToken | None = None,
    ) -> ProviderResponse:
        if request.provider_mode != self.mode or request.provider_id != self.provider_id:
            raise ProviderResponseError("provider request identity does not match Pydantic adapter")
        context_json = self._canonical_json(request.context)
        context_sha256 = hashlib.sha256(context_json.encode("utf-8")).hexdigest()
        self._trace(
            "started",
            request.request_id,
            adapter_version=ADAPTER_VERSION,
            context_sha256=context_sha256,
            offline_only=True,
            project_tool_count=0,
        )
        try:
            model = self._make_offline_model(request)
            agent: Agent[None, PydanticProviderPayload] = Agent(
                model,
                output_type=PydanticProviderPayload,
                instructions=(
                    "Return only the typed advisory research draft. Do not call project tools, "
                    "claim authority, or request network/provider access."
                ),
            )
            prompt = f"Bounded repo-provided reasoning context:\n{context_json}"
            result = asyncio.run(
                self._run_agent(agent, prompt, request.request_id, cancellation_token)
            )
        except ProviderTimeoutError:
            self._trace("timed_out", request.request_id, context_sha256=context_sha256)
            raise
        except ProviderCancelledError:
            self._trace("cancelled", request.request_id, context_sha256=context_sha256)
            raise
        except ProviderUnavailableError:
            self._trace("blocked", request.request_id, context_sha256=context_sha256)
            raise
        except UnexpectedModelBehavior as exc:
            self._trace("invalid_output", request.request_id, context_sha256=context_sha256)
            raise ProviderResponseError(f"Pydantic typed output validation failed: {exc}") from exc

        output = result.output
        if not isinstance(output, PydanticProviderPayload):
            self._trace("invalid_output", request.request_id, context_sha256=context_sha256)
            raise ProviderResponseError("Pydantic runtime returned an unexpected output type")
        payload = output.model_dump(mode="json")
        if payload["request_id"] != request.request_id:
            self._trace("invalid_output", request.request_id, context_sha256=context_sha256)
            raise ProviderResponseError("request_id does not match the active provider request")
        payload_json = self._canonical_json(payload)
        response_sha256 = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
        usage = asdict(result.usage)
        run_metadata = {
            "adapter_version": ADAPTER_VERSION,
            "provider": self.profile.provider,
            "model": self.profile.model,
            "reasoning_tier": self.profile.tier.value,
            "reasoning_configuration": copy.deepcopy(dict(self.profile.reasoning_configuration)),
            "runtime_distribution": RUNTIME_DISTRIBUTION,
            "runtime_version": self.runtime_version,
            "offline_only": True,
            "provider_api_call_made": False,
            "project_tool_count": 0,
            "usage": usage,
        }
        provenance = {
            "request_id": request.request_id,
            "request_context_sha256": context_sha256,
            "response_payload_sha256": response_sha256,
            "response_source": "pydantic_ai_injected_offline_model",
            "tool_context_boundary": "existing_repo_owned_tool_context",
            "no_project_tools_exposed": True,
            "non_authority": NON_AUTHORITY,
        }
        self._trace(
            "completed",
            request.request_id,
            context_sha256=context_sha256,
            response_sha256=response_sha256,
            usage=usage,
        )
        return ProviderResponse(
            request_id=request.request_id,
            status="completed",
            response_source="pydantic_ai_injected_offline_model",
            payload=payload,
            run_metadata=run_metadata,
            provenance=provenance,
        )
