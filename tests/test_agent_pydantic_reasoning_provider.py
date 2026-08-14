from __future__ import annotations

import asyncio
import shutil
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from threading import Timer

import pytest
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.models.test import TestModel

from tools.agent_sandbox import (
    BlockedActionError,
    MemoryAuditSink,
    ToolAction,
    ToolContext,
)
from tools.agent_sandbox.permissions import WRITE_SCRATCH
from tools.research_agents.idea_formalizer_agent import (
    AVAILABILITY_CATALOG_PATH,
    INDICATOR_CATALOG_PATH,
    STRATEGY_TEMPLATE_PATH,
    IdeaFormalizerAgent,
    IdeaFormalizerConfig,
)
from tools.research_agents.pydantic_reasoning_provider import (
    CapabilityTier,
    MemoryProviderTraceSink,
    ProviderCancellationToken,
    ProviderCancelledError,
    ProviderTimeoutError,
    PydanticReasoningProvider,
    PydanticRuntimeConfig,
    PydanticTierCatalog,
    PydanticTierProfile,
)
from tools.research_agents.reasoning_providers import (
    ProviderResponseError,
    ProviderUnavailableError,
)

WP_ID = "WP-ACCEPT-AGENT-RUNTIME-PYDANTIC-01"
FIXED_TIME = datetime(2026, 8, 14, 12, 0, tzinfo=UTC)
ROOT = Path(__file__).resolve().parents[1]


def _profile(
    tier: CapabilityTier,
    *,
    provider: str = "test",
    model: str | None = None,
) -> PydanticTierProfile:
    return PydanticTierProfile(
        tier=tier,
        provider=provider,
        model=model or f"offline-{tier.value.casefold()}-v1",
        reasoning_configuration={"effort": tier.value.casefold()},
    )


def _catalog(
    *, selected_tier: CapabilityTier | None = None, provider: str = "test", model: str | None = None
) -> PydanticTierCatalog:
    profiles = {tier: _profile(tier) for tier in CapabilityTier}
    if selected_tier is not None:
        profiles[selected_tier] = _profile(selected_tier, provider=provider, model=model)
    return PydanticTierCatalog(profiles)


def _context(request_id: str = "accept-pydantic-001") -> dict[str, object]:
    return {
        "request_id": request_id,
        "idea": "BTCUSDT SMA mean reverts because temporary liquidity pressure fades.",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "detected_features": ["sma", "ohlcv"],
    }


def _accepted_payload(
    request_id: str,
    *,
    features: list[str] | None = None,
    summary: str = "SMA mean reversion",
) -> dict[str, object]:
    return {
        "schema_version": "agent_idea_draft_v1",
        "request_id": request_id,
        "decision": "accepted",
        "draft": {
            "summary": summary,
            "causal_rationale": "Temporary liquidity pressure mean reverts.",
            "falsifiable_prediction": "Positive OOS expectancy after costs.",
            "symbols": ["BTCUSDT"],
            "timeframe": "15m",
            "features": features or ["sma", "ohlcv"],
            "entry_concept": "Completed-bar signal with next-bar entry.",
            "exit_concept": "Centerline or bounded holding limit.",
            "parameter_bounds": [{"name": "center_lookback_bars", "minimum": 50, "maximum": 100}],
            "stop_conditions": ["Stop if preregistered OOS thresholds fail."],
        },
        "rejection_reasons": [],
    }


@pytest.mark.parametrize("tier", list(CapabilityTier))
def test_typed_offline_output_and_exact_metadata_for_every_tier(tier: CapabilityTier):
    trace = MemoryProviderTraceSink()
    models: list[TestModel] = []

    def factory(request, profile):
        model = TestModel(
            custom_output_args=_accepted_payload(request.request_id),
            model_name=profile.model,
        )
        models.append(model)
        return model

    provider = PydanticReasoningProvider(
        config=PydanticRuntimeConfig(tier=tier, tier_catalog=_catalog()),
        model_factory=factory,
        trace_sink=trace,
    )
    request = provider.build_request(_context(f"accept-{tier.value.casefold()}"))

    response = provider.complete(request)
    parsed = provider.parse_response(response)

    assert parsed.decision == "accepted"
    assert parsed.draft is not None
    assert parsed.draft["features"] == ["sma", "ohlcv"]
    assert response.run_metadata is not None
    assert {
        key: response.run_metadata[key]
        for key in (
            "adapter_version",
            "provider",
            "model",
            "reasoning_tier",
            "reasoning_configuration",
            "runtime_distribution",
            "runtime_version",
            "offline_only",
            "provider_api_call_made",
            "project_tool_count",
        )
    } == {
        "adapter_version": "pydantic-reasoning-provider-v1",
        "provider": "test",
        "model": f"offline-{tier.value.casefold()}-v1",
        "reasoning_tier": tier.value,
        "reasoning_configuration": {"effort": tier.value.casefold()},
        "runtime_distribution": "pydantic-ai-slim",
        "runtime_version": version("pydantic-ai-slim"),
        "offline_only": True,
        "provider_api_call_made": False,
        "project_tool_count": 0,
    }
    assert response.run_metadata["usage"]["input_tokens"] > 0
    assert response.run_metadata["usage"]["output_tokens"] > 0
    assert response.run_metadata["usage"]["requests"] == 1
    assert response.run_metadata["usage"]["tool_calls"] == 0
    assert response.provenance["request_id"] == request.request_id
    assert len(response.provenance["request_context_sha256"]) == 64
    assert len(response.provenance["response_payload_sha256"]) == 64
    assert response.provenance["no_project_tools_exposed"] is True
    assert [event.event for event in trace.events] == ["started", "completed"]
    assert models[0].last_model_request_parameters.function_tools == []
    assert [tool.name for tool in models[0].last_model_request_parameters.output_tools] == [
        "final_result"
    ]


@pytest.fixture
def agent_repo(tmp_path: Path) -> Path:
    for relative in (
        INDICATOR_CATALOG_PATH,
        AVAILABILITY_CATALOG_PATH,
        STRATEGY_TEMPLATE_PATH,
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return tmp_path


def test_existing_idea_formalizer_seam_carries_runtime_metadata_and_uses_toolcontext(
    agent_repo: Path,
):
    sink = MemoryAuditSink()
    tool_context = ToolContext(
        wp_id=WP_ID,
        role="idea_formalizer",
        audit_sink=sink,
        clock=lambda: FIXED_TIME,
    )
    trace = MemoryProviderTraceSink()
    models: list[TestModel] = []

    def factory(request, profile):
        model = TestModel(
            custom_output_args=_accepted_payload(
                request.request_id,
                features=list(request.context["detected_features"]),
                summary=str(request.context["idea"]),
            ),
            model_name=profile.model,
        )
        models.append(model)
        return model

    provider = PydanticReasoningProvider(
        config=PydanticRuntimeConfig(
            tier=CapabilityTier.STANDARD,
            tier_catalog=_catalog(),
        ),
        model_factory=factory,
        trace_sink=trace,
    )
    agent = IdeaFormalizerAgent(
        config=IdeaFormalizerConfig(provider.mode, provider.provider_id),
        tool_context=tool_context,
        provider=provider,
        repo_root=agent_repo,
    )

    result = agent.run(
        idea=("BTCUSDT 15m SMA mean reverts because temporary liquidity pressure dislocates price.")
    )

    assert result["status"] == "accepted"
    assert result["provider_metadata"]["api_call_made"] is False
    assert result["provider_metadata"]["runtime"]["reasoning_tier"] == "STANDARD"
    assert result["provider_metadata"]["runtime"]["runtime_version"] == version("pydantic-ai-slim")
    assert result["provider_metadata"]["provenance"]["no_project_tools_exposed"] is True
    assert models[0].last_model_request_parameters.function_tools == []
    assert any(record.action_type == WRITE_SCRATCH for record in sink.records)
    assert all(record.decision == "allowed" for record in sink.records)
    assert [event.event for event in trace.events] == ["started", "completed"]


def _slow_provider(
    *, timeout_seconds: float
) -> tuple[PydanticReasoningProvider, MemoryProviderTraceSink]:
    trace = MemoryProviderTraceSink()
    tier = CapabilityTier.STANDARD
    catalog = _catalog(
        selected_tier=tier,
        provider="function",
        model="offline-slow-standard-v1",
    )

    async def slow_function(messages, info):
        del messages, info
        await asyncio.sleep(10)
        raise AssertionError("slow offline model must be cancelled before completion")

    provider = PydanticReasoningProvider(
        config=PydanticRuntimeConfig(
            tier=tier,
            tier_catalog=catalog,
            timeout_seconds=timeout_seconds,
        ),
        model_factory=lambda request, profile: FunctionModel(
            slow_function, model_name=profile.model
        ),
        trace_sink=trace,
    )
    return provider, trace


def test_timeout_cancels_the_inflight_offline_model():
    provider, trace = _slow_provider(timeout_seconds=0.03)
    request = provider.build_request(_context("accept-timeout"))

    with pytest.raises(ProviderTimeoutError, match="timed out after 0.03s"):
        provider.complete(request)

    assert [event.event for event in trace.events] == ["started", "timed_out"]


def test_caller_cancellation_cancels_the_inflight_offline_model():
    provider, trace = _slow_provider(timeout_seconds=1.0)
    request = provider.build_request(_context("accept-cancel"))
    token = ProviderCancellationToken()
    timer = Timer(0.03, token.cancel)
    timer.start()
    try:
        with pytest.raises(ProviderCancelledError, match="request cancelled"):
            provider.complete(request, cancellation_token=token)
    finally:
        timer.join(timeout=1)

    assert token.cancelled is True
    assert [event.event for event in trace.events] == ["started", "cancelled"]


def test_non_test_model_factory_is_rejected_before_any_model_request():
    trace = MemoryProviderTraceSink()
    provider = PydanticReasoningProvider(
        config=PydanticRuntimeConfig(
            tier=CapabilityTier.CHEAP,
            tier_catalog=_catalog(),
        ),
        model_factory=lambda request, profile: object(),  # type: ignore[return-value]
        trace_sink=trace,
    )
    request = provider.build_request(_context("accept-live-denial"))

    with pytest.raises(ProviderUnavailableError, match="live provider/network activation"):
        provider.complete(request)

    assert [event.event for event in trace.events] == ["started", "blocked"]


def test_malformed_structured_output_fails_closed_at_the_typed_boundary():
    trace = MemoryProviderTraceSink()

    def factory(request, profile):
        payload = _accepted_payload(request.request_id)
        payload["unexpected_authority"] = "promote"
        return TestModel(custom_output_args=payload, model_name=profile.model)

    provider = PydanticReasoningProvider(
        config=PydanticRuntimeConfig(
            tier=CapabilityTier.CHEAP,
            tier_catalog=_catalog(),
        ),
        model_factory=factory,
        trace_sink=trace,
    )
    request = provider.build_request(_context("accept-invalid-output"))

    with pytest.raises(ProviderResponseError, match="typed output validation failed"):
        provider.complete(request)

    assert [event.event for event in trace.events] == ["started", "invalid_output"]


@pytest.mark.parametrize(
    ("action_type", "target_path"),
    [
        ("canonical_write", "research/strategy_specs/STRAT-SPEC-9999.json"),
        ("candidate_registration", "research/candidate_registry.jsonl"),
        ("candidate_promotion", "research/candidate_registry.jsonl"),
        ("dispatch_authorization_access", "research/queue/dispatch_authorizations/KDAUTH.json"),
        ("kdauth_access", "research/queue/dispatch_authorizations/KDAUTH.json"),
        ("project_status_mutation", "docs/project_status.md"),
        ("runtime_control", "src/runtime/runner.py"),
        ("paper_control", "src/paper/runner.py"),
        ("live_control", "src/live/runner.py"),
        ("oms_access", "src/oms/state.py"),
        ("risk_control", "src/risk/caps.py"),
        ("reconciliation_control", "src/reconciliation/state.py"),
        ("safe_mode_control", "src/safe_mode/control.py"),
        ("exchange_access", "src/exchange/client.py"),
        ("order_access", "src/orders/create.py"),
        ("capital_access", "src/capital/allocation.py"),
        ("credential_access", "secrets/exchange.key"),
        ("network_access", "provider/network"),
        ("provider_api_call", "provider/api"),
        ("toolcontext_bypass", "tools/agent_sandbox/tool_context.py"),
        (WRITE_SCRATCH, "src/runtime/protected-write.json"),
    ],
)
def test_all_authority_leakage_attempts_fail_closed_and_are_audited(
    action_type: str, target_path: str
):
    sink = MemoryAuditSink()
    context = ToolContext(
        wp_id=WP_ID,
        role="idea_formalizer",
        audit_sink=sink,
        clock=lambda: FIXED_TIME,
    )
    mutations: list[str] = []

    with pytest.raises(BlockedActionError):
        context.run_allowed(ToolAction(action_type, target_path), lambda: mutations.append("ran"))

    assert mutations == []
    assert len(sink.records) == 1
    assert sink.records[0].decision == "blocked"
    assert sink.records[0].action_type == action_type
    assert sink.records[0].target_path == target_path.casefold()
    assert "no canonical" in sink.records[0].non_authority
