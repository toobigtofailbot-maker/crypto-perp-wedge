"""Bounded provider-flexible idea formalizer with ToolContext-routed actions."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.agent_sandbox import (
    BlockedActionError,
    JsonLinesAuditSink,
    ToolAction,
    ToolContext,
)
from tools.agent_sandbox.permissions import (
    READ_NON_SECRET,
    RUN_READ_ONLY_VALIDATION,
    WRITE_SCRATCH,
)
from tools.registry.validate_strategy_specs import validate_strategy_specs
from tools.research_domain import formalization as domain_formalization
from tools.research_domain.contracts import LOCKED_TIMEFRAMES as DOMAIN_LOCKED_TIMEFRAMES
from tools.research_domain.formalization import (
    assess_capabilities,
    build_strategy_spec,
    detect_features,
    formalize_reasoned_strategy_draft,
)

from .provider_packets import render_chatgpt_request_packet
from .reasoning_providers import (
    ChatGPTAccountPacketProvider,
    DisabledProvider,
    FakeOfflineProvider,
    ProviderResponseError,
    ProviderUnavailableError,
    ReasoningProvider,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
WP_ID = "WP-AGENT-IDEA-FORMALIZER-01"
DONCHIAN_ADAPTER_WP_ID = "WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01"
FUNDING_RESEARCH_WP_ID = "WP-RESEARCH-FUNDING-CARRY-02"
ROLE = "idea_formalizer"
OUTPUT_ROOT = Path("scratch") / WP_ID
INDICATOR_CATALOG_PATH = Path("research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json")
AVAILABILITY_CATALOG_PATH = Path(
    "research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
)
STRATEGY_TEMPLATE_PATH = Path("research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json")
STRATEGY_SCHEMA_PATH = REPO_ROOT / "research/schemas/strategy_spec.schema.json"
VALIDATOR_PATH = "tools/registry/validate_strategy_specs.py"
LOCKED_TIMEFRAMES = set(DOMAIN_LOCKED_TIMEFRAMES)
NON_AUTHORITY = {
    "draft_only": True,
    "scratch_only": True,
    "not_canonical": True,
    "not_evidence": True,
    "not_candidate_authority": True,
    "not_promotion_authority": True,
    "not_paper_live_runtime_authority": True,
    "human_review_required": True,
}


@dataclass(frozen=True)
class IdeaFormalizerConfig:
    provider_mode: str = "fake_offline"
    provider_id: str = "fake-rule-v1"


BOUNDARY_PATTERNS: tuple[tuple[re.Pattern[str], str, str, str], ...] = (
    (
        re.compile(r"write.+canonical.+strategy spec", re.IGNORECASE),
        WRITE_SCRATCH,
        "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json",
        "canonical Strategy Spec write requested",
    ),
    (
        re.compile(r"write.+canonical.+result population", re.IGNORECASE),
        WRITE_SCRATCH,
        "research/result_populations/RP-9999.result_population.json",
        "canonical Result Population write requested",
    ),
    (
        re.compile(
            r"write.+canonical.+(variant manifest|sweep plan|trial log|evidence)", re.IGNORECASE
        ),
        "canonical_write",
        "research/canonical-artifact",
        "canonical research artifact write requested",
    ),
    (
        re.compile(r"\bpromote\b", re.IGNORECASE),
        "candidate_promotion",
        "research/candidate_registry.jsonl",
        "candidate promotion requested",
    ),
    (
        re.compile(r"\bfreeze\b", re.IGNORECASE),
        "candidate_freeze",
        "research/candidate_registry.jsonl",
        "candidate freeze requested",
    ),
    (
        re.compile(r"\bregister.+candidate\b", re.IGNORECASE),
        "candidate_registration",
        "research/candidate_registry.jsonl",
        "candidate registration requested",
    ),
    (
        re.compile(r"\b(run|launch|execute).+backtest\b", re.IGNORECASE),
        "backtest_execution",
        "tools/research_runner",
        "backtest execution requested",
    ),
    (
        re.compile(r"\b(run|launch|execute).+sweep\b", re.IGNORECASE),
        "sweep_execution",
        "tools/research_runner",
        "sweep execution requested",
    ),
    (
        re.compile(r"change.+funding mode.+globally", re.IGNORECASE),
        "funding_mode_mutation",
        "configs/research.json",
        "global funding-mode mutation requested",
    ),
    (
        re.compile(r"private endpoint", re.IGNORECASE),
        "private_endpoint_access",
        "exchange/private",
        "private endpoint access requested",
    ),
    (
        re.compile(r"\b(api key|credentials?|secret key)\b", re.IGNORECASE),
        "credential_access",
        ".env",
        "credential access requested",
    ),
    (
        re.compile(r"\b(live provider|live api|call.+api)\b", re.IGNORECASE),
        "network_access",
        "provider/network",
        "live provider/API call requested",
    ),
    (
        re.compile(
            r"(?:\b(paper|live|runtime)\b.+\b(run|launch|change|touch|control|trade)\b|"
            r"\b(run|launch|change|touch|control|trade)\b.+\b(paper|live|runtime)\b)",
            re.IGNORECASE,
        ),
        "runtime_control",
        "src/runtime",
        "paper/live/runtime action requested",
    ),
    (
        re.compile(
            r"(?:\b(oms|risk|reconciliation|capital|safe mode)\b.+"
            r"\b(change|touch|control|access)\b|"
            r"\b(change|touch|control|access)\b.+"
            r"\b(oms|risk|reconciliation|capital|safe mode)\b)",
            re.IGNORECASE,
        ),
        "risk_control",
        "src/risk",
        "protected trading-control action requested",
    ),
    (
        re.compile(r"hide.+failed|winner.?only", re.IGNORECASE),
        "evidence_suppression",
        "research",
        "failed-evidence suppression requested",
    ),
    (
        re.compile(r"delete.+evidence", re.IGNORECASE),
        "evidence_deletion",
        "research",
        "evidence deletion requested",
    ),
    (
        re.compile(r"bypass.+toolcontext", re.IGNORECASE),
        "toolcontext_bypass",
        "tools/agent_sandbox",
        "ToolContext bypass requested",
    ),
    (
        re.compile(r"bypass.+\b(gate|gates|validator|validation)\b", re.IGNORECASE),
        "gate_bypass",
        "tools/registry",
        "repo gate or validator bypass requested",
    ),
    (
        re.compile(r"provider memory|chatgpt memory|claude memory", re.IGNORECASE),
        "provider_memory_as_truth",
        "provider/memory",
        "provider memory requested as repo truth",
    ),
)


class IdeaFormalizerAgent:
    def __init__(
        self,
        *,
        config: IdeaFormalizerConfig,
        tool_context: ToolContext,
        provider: ReasoningProvider,
        repo_root: Path = REPO_ROOT,
    ) -> None:
        if provider.mode != config.provider_mode or provider.provider_id != config.provider_id:
            raise ValueError("provider instance does not match provider configuration")
        self.config = config
        self.tool_context = tool_context
        self.provider = provider
        self.repo_root = repo_root.resolve()
        self.output_root = Path("scratch") / tool_context.wp_id
        if tool_context.wp_id == DONCHIAN_ADAPTER_WP_ID:
            self.output_root /= "formalizer"

    def _repo_relative(self, path: Path | str) -> str:
        candidate = Path(path)
        if candidate.is_absolute():
            candidate = candidate.resolve().relative_to(self.repo_root)
        normalized = candidate.as_posix()
        if normalized.startswith("../") or normalized == "..":
            raise ValueError("path must remain inside the repo")
        return normalized

    def _read_text(self, path: Path | str) -> str:
        relative = self._repo_relative(path)
        return self.tool_context.run_allowed(
            ToolAction(READ_NON_SECRET, relative),
            lambda: (self.repo_root / relative).read_text(encoding="utf-8"),
        )

    def _read_json(self, path: Path | str) -> dict[str, Any]:
        payload = json.loads(self._read_text(path))
        if not isinstance(payload, dict):
            raise ValueError(f"JSON root must be an object: {path}")  # noqa: TRY004
        return payload

    def _write_text(self, path: Path | str, content: str) -> str:
        relative = self._repo_relative(path)

        def operation() -> None:
            target = self.repo_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")

        self.tool_context.run_allowed(ToolAction(WRITE_SCRATCH, relative), operation)
        return relative

    def _write_json(self, path: Path | str, payload: Mapping[str, Any]) -> str:
        return self._write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")

    @staticmethod
    def _run_id(
        idea: str,
        symbol: str,
        timeframe: str,
        config: IdeaFormalizerConfig,
        constraints: list[str] | None = None,
    ) -> str:
        raw = json.dumps(
            {
                "idea": idea,
                "symbol": symbol,
                "timeframe": timeframe,
                "constraints": constraints or [],
                "provider_mode": config.provider_mode,
                "provider_id": config.provider_id,
            },
            sort_keys=True,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]

    def _detect_features(self, idea: str, indicator_ids: set[str]) -> list[str]:
        return detect_features(idea, indicator_ids)

    def _assess_capabilities(self, idea: str) -> dict[str, Any]:
        indicator_catalog = self._read_json(INDICATOR_CATALOG_PATH)
        availability_catalog = self._read_json(AVAILABILITY_CATALOG_PATH)
        return assess_capabilities(idea, indicator_catalog, availability_catalog)

    def _boundary_rejection(self, idea: str) -> tuple[str, Any] | None:
        for pattern, action_type, target_path, reason in BOUNDARY_PATTERNS:
            if not pattern.search(idea):
                continue
            try:
                self.tool_context.require_allowed(ToolAction(action_type, target_path))
            except BlockedActionError as exc:
                return reason, exc.record.to_dict()
            raise AssertionError(f"boundary action unexpectedly allowed: {action_type}")
        return None

    def _build_strategy_spec(
        self,
        *,
        run_id: str,
        draft: Mapping[str, Any],
        provider_metadata: Mapping[str, Any],
        formalized_path: str,
    ) -> dict[str, Any]:
        return build_strategy_spec(
            run_id=run_id,
            draft=draft,
            provider_metadata=provider_metadata,
            formalized_path=formalized_path,
            template=self._read_json(STRATEGY_TEMPLATE_PATH),
        )

    @staticmethod
    def _apply_funding_strategy_body(spec: dict[str, Any], *, exit_mode: str) -> None:
        domain_formalization._apply_funding_strategy_body(spec, exit_mode=exit_mode)

    @staticmethod
    def _apply_donchian_strategy_body(spec: dict[str, Any]) -> None:
        domain_formalization._apply_donchian_strategy_body(spec)

    def _validate_draft_dir(self, path: Path) -> list[str]:
        return self.tool_context.run_allowed(
            ToolAction(RUN_READ_ONLY_VALIDATION, VALIDATOR_PATH),
            lambda: validate_strategy_specs(
                strategy_specs_dir=self.repo_root / path,
                schema_path=STRATEGY_SCHEMA_PATH,
                repo_root=self.repo_root,
            ),
        )

    @staticmethod
    def _draft_family_id(draft: Mapping[str, Any]) -> str | None:
        return domain_formalization._draft_family_id(draft)

    @classmethod
    def _draft_family_supported(
        cls, draft: Mapping[str, Any], assessment: Mapping[str, Any]
    ) -> bool:
        return cls._draft_family_id(draft) is not None and bool(
            assessment.get("historically_testable_now")
        )

    def run(
        self,
        *,
        idea: str,
        symbol: str = "BTCUSDT",
        timeframe: str = "15m",
        constraints: list[str] | None = None,
    ) -> dict[str, Any]:
        idea = idea.strip()
        if not idea:
            raise ValueError("idea must be non-empty")
        if symbol != "BTCUSDT":
            raise ValueError("current repo capability is bounded to BTCUSDT")
        if timeframe not in LOCKED_TIMEFRAMES:
            raise ValueError(f"timeframe must be one of {sorted(LOCKED_TIMEFRAMES)}")
        constraints = constraints or []
        run_id = self._run_id(idea, symbol, timeframe, self.config, constraints)
        run_dir = self.output_root / "outputs" / run_id
        provider_dir = self.output_root / "provider_packets"
        base_result: dict[str, Any] = {
            "schema_version": "agent_formalized_idea_v1",
            "run_id": run_id,
            "status": "pending",
            "input": {
                "idea": idea,
                "symbol": symbol,
                "timeframe": timeframe,
                "constraints": constraints,
            },
            "provider_metadata": {
                "provider_mode": self.config.provider_mode,
                "provider_id": self.config.provider_id,
                "request_id": run_id,
                "response_source": None,
                "api_call_made": False,
            },
            "capability_assessment": None,
            "research_object": None,
            "rejection_reasons": [],
            "blocked_action": None,
            "draft_strategy_spec": {"produced": False, "path": None, "blockers": []},
            "adapter_metadata": {
                "family_id": None,
                "freshness_distinct_from": [],
                "unsupported_capabilities": [],
            },
            "non_authority": copy.deepcopy(NON_AUTHORITY),
        }

        boundary = self._boundary_rejection("\n".join([idea, *constraints]))
        if boundary is not None:
            reason, audit_record = boundary
            base_result.update(
                {
                    "status": "rejected",
                    "rejection_reasons": [reason],
                    "blocked_action": audit_record,
                }
            )
            self._write_json(run_dir / "formalized_idea.json", base_result)
            self._write_json(run_dir / "human_review_packet.json", base_result)
            return base_result

        indicator_catalog = self._read_json(INDICATOR_CATALOG_PATH)
        availability_catalog = self._read_json(AVAILABILITY_CATALOG_PATH)
        assessment = assess_capabilities(idea, indicator_catalog, availability_catalog)
        base_result["capability_assessment"] = assessment
        context = {
            "request_id": run_id,
            "idea": idea,
            "symbol": symbol,
            "timeframe": timeframe,
            "constraints": constraints,
            "detected_features": assessment["detected_features"],
            "capability_assessment": assessment,
        }
        request = self.provider.build_request(context)
        if self.config.provider_mode == "chatgpt_account_packet":
            packet_path = provider_dir / f"{run_id}_chatgpt_request.md"
            base_result["provider_metadata"]["request_packet_path"] = self._write_text(
                packet_path, render_chatgpt_request_packet(request)
            )
        try:
            response = self.provider.complete(request)
            base_result["provider_metadata"]["response_source"] = response.response_source
            if response.run_metadata is not None:
                base_result["provider_metadata"]["runtime"] = copy.deepcopy(
                    dict(response.run_metadata)
                )
            if response.provenance is not None:
                base_result["provider_metadata"]["provenance"] = copy.deepcopy(
                    dict(response.provenance)
                )
            if response.status == "pending_operator":
                base_result["status"] = "awaiting_provider_response"
                base_result["rejection_reasons"] = [
                    "operator-mediated provider response has not been imported"
                ]
                self._write_json(run_dir / "human_review_packet.json", base_result)
                return base_result
            parsed = self.provider.parse_response(response)
        except (ProviderResponseError, ProviderUnavailableError) as exc:
            base_result["status"] = "rejected"
            base_result["rejection_reasons"] = [str(exc)]
            self._write_json(run_dir / "formalized_idea.json", base_result)
            self._write_json(run_dir / "human_review_packet.json", base_result)
            return base_result

        if parsed.draft is None:
            base_result["status"] = "rejected"
            base_result["rejection_reasons"] = list(parsed.rejection_reasons)
        else:
            formalized_path = self._repo_relative(run_dir / "formalized_idea.json")
            source_context = {
                "source_type": "manual_idea",
                "source_refs": [formalized_path],
                "prepared_by": "bounded idea_formalizer agent",
                "source_constraints": [
                    f"provider_mode={base_result['provider_metadata']['provider_mode']}",
                    f"provider_id={base_result['provider_metadata']['provider_id']}",
                    f"request_id={base_result['provider_metadata']['request_id']}",
                    f"response_source={base_result['provider_metadata']['response_source']}",
                ],
                "unresolved_claims": [
                    "Provider output is advisory and requires human review.",
                    "No preregistration, sweep, evidence, or execution is authorized.",
                ],
                "review_notes": [
                    "Scratch-only provider-assisted draft; validator success is not approval."
                ],
                "lineage_ref_path": formalized_path,
                "default_title": "Draft provider-assisted SMA/stddev mean-reversion Strategy Spec",
            }
            domain_result = formalize_reasoned_strategy_draft(
                idea=idea,
                symbol=symbol,
                timeframe=timeframe,
                constraints=constraints,
                reasoned_draft=parsed.draft,
                indicator_catalog=indicator_catalog,
                availability_catalog=availability_catalog,
                strategy_spec_template=self._read_json(STRATEGY_TEMPLATE_PATH),
                run_id=run_id,
                source_context=source_context,
            )
            base_result["status"] = domain_result["status"]
            base_result["capability_assessment"] = domain_result["capability_assessment"]
            base_result["research_object"] = domain_result["research_object"]
            base_result["rejection_reasons"] = domain_result["rejection_reasons"]
            base_result["adapter_metadata"] = domain_result["adapter_metadata"]
            base_result["draft_strategy_spec"] = domain_result["draft_strategy_spec"]
            if parsed.decision == "rejected" and domain_result["status"] != "rejected":
                base_result["status"] = "rejected"
                base_result["rejection_reasons"] = list(parsed.rejection_reasons)
                domain_result["draft_strategy_specs"] = []

        formalized_path = self._write_json(run_dir / "formalized_idea.json", base_result)
        if parsed.draft is not None:
            specs = domain_result["draft_strategy_specs"]
        else:
            specs = []
        if specs:
            spec = specs[0]
            spec_path = run_dir / f"{spec['strategy_spec_id']}.strategy_spec.json"
            self._write_json(spec_path, spec)
            if len(specs) == 2:
                fixed_spec = specs[1]
                fixed_path = run_dir / f"{fixed_spec['strategy_spec_id']}.strategy_spec.json"
                self._write_json(fixed_path, fixed_spec)
                base_result["adapter_metadata"]["strategy_spec_paths"] = {
                    "midline_reversion_or_max_hold": spec_path.as_posix(),
                    "fixed_max_hold_only": fixed_path.as_posix(),
                }
            validation_errors = self._validate_draft_dir(run_dir)
            base_result["draft_strategy_spec"] = {
                "produced": not validation_errors,
                "path": spec_path.as_posix() if not validation_errors else None,
                "blockers": validation_errors,
                "validator": VALIDATOR_PATH,
            }
            self._write_json(run_dir / "formalized_idea.json", base_result)

        self._write_json(run_dir / "human_review_packet.json", base_result)
        return base_result


def make_provider(
    config: IdeaFormalizerConfig,
    *,
    response_loader: Any = None,
) -> ReasoningProvider:
    if config.provider_mode == "fake_offline":
        return FakeOfflineProvider()
    if config.provider_mode == "chatgpt_account_packet":
        return ChatGPTAccountPacketProvider(response_loader=response_loader)
    return DisabledProvider(config.provider_mode)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--idea", required=True)
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--timeframe", default="15m", choices=sorted(LOCKED_TIMEFRAMES))
    parser.add_argument(
        "--provider-mode",
        default="fake_offline",
        choices=[
            "fake_offline",
            "chatgpt_account_packet",
            "openai_api_disabled",
            "anthropic_api_disabled",
            "local_model_disabled",
        ],
    )
    parser.add_argument("--provider-id")
    parser.add_argument("--response-file", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    default_ids = {
        "fake_offline": "fake-rule-v1",
        "chatgpt_account_packet": "chatgpt-account-operator-v1",
        "openai_api_disabled": "openai_api_disabled",
        "anthropic_api_disabled": "anthropic_api_disabled",
        "local_model_disabled": "local_model_disabled",
    }
    config = IdeaFormalizerConfig(
        provider_mode=args.provider_mode,
        provider_id=args.provider_id or default_ids[args.provider_mode],
    )
    audit_path = REPO_ROOT / OUTPUT_ROOT / "audit" / "actions.jsonl"
    context = ToolContext(
        wp_id=WP_ID,
        role=ROLE,
        audit_sink=JsonLinesAuditSink(audit_path),
    )
    response_loader = None
    if args.response_file is not None:
        response_path = args.response_file
        if response_path.is_absolute():
            response_path = response_path.resolve().relative_to(REPO_ROOT)
        response_target = REPO_ROOT / response_path

        def response_loader() -> str:
            return context.run_allowed(
                ToolAction(READ_NON_SECRET, response_path.as_posix()),
                lambda: response_target.read_text(encoding="utf-8"),
            )

    try:
        provider = make_provider(config, response_loader=response_loader)
        agent = IdeaFormalizerAgent(config=config, tool_context=context, provider=provider)
        result = agent.run(idea=args.idea, symbol=args.symbol, timeframe=args.timeframe)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] in {"accepted", "awaiting_provider_response"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
