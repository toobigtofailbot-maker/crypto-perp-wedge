"""Bounded provider-flexible idea formalizer with ToolContext-routed actions."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

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
ROLE = "idea_formalizer"
OUTPUT_ROOT = Path("scratch") / WP_ID
INDICATOR_CATALOG_PATH = Path("research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json")
AVAILABILITY_CATALOG_PATH = Path(
    "research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
)
STRATEGY_TEMPLATE_PATH = Path("research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json")
STRATEGY_SCHEMA_PATH = REPO_ROOT / "research/schemas/strategy_spec.schema.json"
VALIDATOR_PATH = "tools/registry/validate_strategy_specs.py"
LOCKED_TIMEFRAMES = {"15m", "30m", "1h", "4h", "1d"}
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
        re.compile(r"write.+canonical.+strategy spec", re.I),
        WRITE_SCRATCH,
        "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json",
        "canonical Strategy Spec write requested",
    ),
    (
        re.compile(r"write.+canonical.+result population", re.I),
        WRITE_SCRATCH,
        "research/result_populations/RP-9999.result_population.json",
        "canonical Result Population write requested",
    ),
    (
        re.compile(r"write.+canonical.+(variant manifest|sweep plan|trial log|evidence)", re.I),
        "canonical_write",
        "research/canonical-artifact",
        "canonical research artifact write requested",
    ),
    (
        re.compile(r"\bpromote\b", re.I),
        "candidate_promotion",
        "research/candidate_registry.jsonl",
        "candidate promotion requested",
    ),
    (
        re.compile(r"\bfreeze\b", re.I),
        "candidate_freeze",
        "research/candidate_registry.jsonl",
        "candidate freeze requested",
    ),
    (
        re.compile(r"\bregister.+candidate\b", re.I),
        "candidate_registration",
        "research/candidate_registry.jsonl",
        "candidate registration requested",
    ),
    (
        re.compile(r"\b(run|launch|execute).+backtest\b", re.I),
        "backtest_execution",
        "tools/research_runner",
        "backtest execution requested",
    ),
    (
        re.compile(r"\b(run|launch|execute).+sweep\b", re.I),
        "sweep_execution",
        "tools/research_runner",
        "sweep execution requested",
    ),
    (
        re.compile(r"change.+funding mode.+globally", re.I),
        "funding_mode_mutation",
        "configs/research.json",
        "global funding-mode mutation requested",
    ),
    (
        re.compile(r"private endpoint", re.I),
        "private_endpoint_access",
        "exchange/private",
        "private endpoint access requested",
    ),
    (
        re.compile(r"\b(api key|credentials?|secret key)\b", re.I),
        "credential_access",
        ".env",
        "credential access requested",
    ),
    (
        re.compile(r"\b(live provider|live api|call.+api)\b", re.I),
        "network_access",
        "provider/network",
        "live provider/API call requested",
    ),
    (
        re.compile(
            r"(?:\b(paper|live|runtime)\b.+\b(run|launch|change|touch|control|trade)\b|"
            r"\b(run|launch|change|touch|control|trade)\b.+\b(paper|live|runtime)\b)",
            re.I,
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
            re.I,
        ),
        "risk_control",
        "src/risk",
        "protected trading-control action requested",
    ),
    (
        re.compile(r"hide.+failed|winner.?only", re.I),
        "evidence_suppression",
        "research",
        "failed-evidence suppression requested",
    ),
    (
        re.compile(r"delete.+evidence", re.I),
        "evidence_deletion",
        "research",
        "evidence deletion requested",
    ),
    (
        re.compile(r"bypass.+toolcontext", re.I),
        "toolcontext_bypass",
        "tools/agent_sandbox",
        "ToolContext bypass requested",
    ),
    (
        re.compile(r"bypass.+\b(gate|gates|validator|validation)\b", re.I),
        "gate_bypass",
        "tools/registry",
        "repo gate or validator bypass requested",
    ),
    (
        re.compile(r"provider memory|chatgpt memory|claude memory", re.I),
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
            raise ValueError(f"JSON root must be an object: {path}")
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
        lower = idea.casefold()
        features = sorted(
            feature for feature in indicator_ids if re.search(rf"\b{re.escape(feature)}\b", lower)
        )
        if any(
            term in lower for term in ("taker flow", "taker-flow", "aggressive buy", "aggtrades")
        ):
            features.append("taker_buy_sell_ratio")
        if re.search(r"\b(open interest|oi divergence)\b", lower):
            features.append("open_interest")
        if "long/short ratio" in lower or "long short ratio" in lower:
            features.append("global_long_short_account_ratio")
        if "liquidation" in lower:
            features.append("liquidation_volume")
        if any(term in lower for term in ("ohlcv", "price", "close", "volume")):
            features.append("ohlcv")
        return list(dict.fromkeys(features))

    def _assess_capabilities(self, idea: str) -> dict[str, Any]:
        indicator_catalog = self._read_json(INDICATOR_CATALOG_PATH)
        availability_catalog = self._read_json(AVAILABILITY_CATALOG_PATH)
        indicator_ids = {
            entry["indicator_id"]
            for entry in indicator_catalog.get("entries", [])
            if isinstance(entry, dict) and isinstance(entry.get("indicator_id"), str)
        }
        detected = self._detect_features(idea, indicator_ids)
        entries = [
            entry for entry in availability_catalog.get("entries", []) if isinstance(entry, dict)
        ]
        assessments: list[dict[str, Any]] = []
        for feature in detected:
            if feature == "ohlcv":
                assessments.append(
                    {
                        "feature": feature,
                        "compiler_field_exists": True,
                        "historical_testability": "available_public_archive",
                        "coverage_class": "FULL_HISTORY_PUBLIC_ARCHIVE",
                        "source_class": "PUBLIC_OHLCV_ARCHIVE",
                        "warnings": [],
                    }
                )
                continue
            if feature in indicator_ids:
                assessments.append(
                    {
                        "feature": feature,
                        "compiler_field_exists": True,
                        "historical_testability": "available_when_source_bars_exist",
                        "coverage_class": "FULL_HISTORY_PUBLIC_ARCHIVE",
                        "source_class": "INDICATOR_DERIVED_FROM_OHLCV",
                        "warnings": [],
                    }
                )
                continue
            candidates = [entry for entry in entries if entry.get("feature_name") == feature]
            if feature == "taker_buy_sell_ratio":
                preferred = next(
                    (
                        entry
                        for entry in candidates
                        if entry.get("source_class") == "PUBLIC_TRADE_ARCHIVE_DERIVATION"
                    ),
                    None,
                )
            else:
                preferred = candidates[0] if candidates else None
            if preferred is None:
                assessments.append(
                    {
                        "feature": feature,
                        "compiler_field_exists": False,
                        "historical_testability": "blocked_unknown",
                        "coverage_class": "UNKNOWN_OR_BLOCKED",
                        "source_class": "UNKNOWN_SOURCE",
                        "warnings": ["No repo availability entry exists."],
                    }
                )
                continue
            coverage = str(preferred["coverage_class"])
            conditional_archive = (
                coverage == "FULL_HISTORY_PUBLIC_ARCHIVE"
                and preferred.get("canonical_full_history_allowed") == "conditional"
            )
            testability = (
                "conditionally_public_archive_backfillable"
                if conditional_archive
                else "vendor_or_capture_constrained"
                if preferred.get("requires_vendor_or_captured_data")
                else "available_public_archive"
            )
            warnings = [str(preferred.get("history_limitation", ""))]
            if feature in {"open_interest", "open_interest_value"}:
                warnings.append(
                    "Compiler field existence does not provide full historical OI data."
                )
                warnings.append(
                    "Trades and aggregate trades cannot reconstruct true open interest."
                )
            assessments.append(
                {
                    "feature": feature,
                    "compiler_field_exists": bool(preferred.get("compiler_visible")),
                    "historical_testability": testability,
                    "coverage_class": coverage,
                    "source_class": preferred.get("source_class"),
                    "warnings": warnings,
                    "conditions": preferred.get("conditions", []),
                }
            )
        blockers = [
            item["feature"]
            for item in assessments
            if item["historical_testability"]
            in {"vendor_or_capture_constrained", "blocked_unknown"}
            or not item["compiler_field_exists"]
        ]
        return {
            "detected_features": detected,
            "feature_assessments": assessments,
            "historically_testable_now": bool(assessments) and not blockers,
            "blocking_features": blockers,
            "distinction": "compiler field existence is separate from historical testability",
        }

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
        spec = copy.deepcopy(self._read_json(STRATEGY_TEMPLATE_PATH))
        numeric_id = 9000 + (int(run_id[:8], 16) % 1000)
        timeframe = str(draft["timeframe"])

        def replace_timeframe(value: Any) -> Any:
            if isinstance(value, dict):
                return {key: replace_timeframe(child) for key, child in value.items()}
            if isinstance(value, list):
                return [replace_timeframe(child) for child in value]
            if isinstance(value, str):
                return re.sub(r"\b15m\b", timeframe, value)
            return value

        spec = replace_timeframe(spec)
        spec["strategy_spec_id"] = f"STRAT-SPEC-{numeric_id:04d}"
        spec["title"] = "Draft provider-assisted SMA/stddev mean-reversion Strategy Spec"
        spec["short_name"] = f"draft-idea-{run_id}"
        spec["status"] = "draft"
        spec["instruments"]["symbols"] = list(draft["symbols"])
        spec["timeframe_and_data"]["gap_handling_assumption"] = (
            f"Use existing cataloged {draft['symbols'][0]} {timeframe} OHLCV and the "
            "merged research-workbench gap policy; do not interpolate or silently fill gaps."
        )
        spec["provenance"] = {
            "source_type": "manual_idea",
            "source_refs": [formalized_path],
            "prepared_by": "bounded idea_formalizer agent",
            "created_at": None,
            "updated_at": None,
            "rationale": str(draft["causal_rationale"]),
            "source_constraints": [
                f"provider_mode={provider_metadata['provider_mode']}",
                f"provider_id={provider_metadata['provider_id']}",
                f"request_id={provider_metadata['request_id']}",
                f"response_source={provider_metadata['response_source']}",
                "Scratch-only draft adapted from the merged STRAT-SPEC-0003 capability family.",
            ],
            "unresolved_claims": [
                "Provider output is advisory and requires human review.",
                "No preregistration, sweep, evidence, or execution is authorized.",
            ],
        }
        spec["review"].update(
            {
                "reviewer": None,
                "reviewed_at": None,
                "review_notes": [
                    "Scratch-only provider-assisted draft; validator success is not approval."
                ],
                "approval_scope": "none",
            }
        )
        spec["lineage"] = {
            "parent_refs": [
                {
                    "ref_type": "concept",
                    "ref_id": f"IDEA-{run_id.upper()}",
                    "ref_path": formalized_path,
                    "ref_hash": None,
                }
            ],
            "supersedes": [],
            "amendment_of": None,
        }
        spec["hash_pinning"].update({"canonical_spec_hash": None, "hash_status": "not_computed"})
        spec["pre_registration_support"] = {
            "intended_for_variant_manifest": False,
            "variant_manifest_ref": None,
            "frozen_snapshot_ref": None,
        }
        return spec

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
    def _draft_family_supported(draft: Mapping[str, Any], assessment: Mapping[str, Any]) -> bool:
        features = set(draft.get("features", []))
        return {"sma", "stddev"}.issubset(features) and bool(
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
        run_dir = OUTPUT_ROOT / "outputs" / run_id
        provider_dir = OUTPUT_ROOT / "provider_packets"
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

        assessment = self._assess_capabilities(idea)
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

        if parsed.draft is not None:
            declared_features = set(parsed.draft.get("features", []))
            detected_features = set(assessment["detected_features"])
            response_contract_errors = []
            if not declared_features.issubset(detected_features):
                response_contract_errors.append(
                    "provider response claims features not detected in the operator idea"
                )
            if parsed.draft.get("symbols") != [symbol]:
                response_contract_errors.append(
                    "provider response symbols do not match the bounded operator input"
                )
            if parsed.draft.get("timeframe") != timeframe:
                response_contract_errors.append(
                    "provider response timeframe does not match the bounded operator input"
                )
            if response_contract_errors:
                base_result["status"] = "rejected"
                base_result["rejection_reasons"] = response_contract_errors
                self._write_json(run_dir / "formalized_idea.json", base_result)
                self._write_json(run_dir / "human_review_packet.json", base_result)
                return base_result

        if parsed.decision == "rejected" or parsed.draft is None:
            base_result["status"] = "rejected"
            base_result["rejection_reasons"] = list(parsed.rejection_reasons)
        else:
            base_result["status"] = "accepted"
            base_result["research_object"] = copy.deepcopy(parsed.draft)
            blockers = list(assessment["blocking_features"])
            if blockers:
                base_result["status"] = "needs_data"
                base_result["draft_strategy_spec"]["blockers"] = [
                    f"missing historical/compiler support: {item}" for item in blockers
                ]
            elif not self._draft_family_supported(parsed.draft, assessment):
                base_result["draft_strategy_spec"]["blockers"] = [
                    "no validated draft adapter exists for this exact primitive family"
                ]

        formalized_path = self._write_json(run_dir / "formalized_idea.json", base_result)
        if (
            base_result["status"] == "accepted"
            and parsed.draft is not None
            and self._draft_family_supported(parsed.draft, assessment)
        ):
            spec = self._build_strategy_spec(
                run_id=run_id,
                draft=parsed.draft,
                provider_metadata=base_result["provider_metadata"],
                formalized_path=formalized_path,
            )
            spec_path = run_dir / f"{spec['strategy_spec_id']}.strategy_spec.json"
            self._write_json(spec_path, spec)
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
