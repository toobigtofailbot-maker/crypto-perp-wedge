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
        if "funding_rate" in lower or "funding rate" in lower:
            features.append("funding_rate")
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
        family_id = self._draft_family_id(draft)

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
        spec["title"] = {
            "donchian_channel_breakout_v1": "Draft deterministic Donchian channel-breakout Strategy Spec",
            "funding_rate_positioning_fade_v1": "Draft funding-rate positioning-fade Strategy Spec",
        }.get(family_id, "Draft provider-assisted SMA/stddev mean-reversion Strategy Spec")
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
                {
                    "donchian_channel_breakout_v1": (
                        "Scratch-only draft produced by the bounded "
                        "donchian_channel_breakout_v1 adapter."
                    ),
                    "funding_rate_positioning_fade_v1": (
                        "Scratch-only draft produced by the bounded "
                        "funding_rate_positioning_fade_v1 adapter."
                    ),
                }.get(
                    family_id,
                    "Scratch-only draft adapted from the merged STRAT-SPEC-0003 capability family.",
                ),
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
        if family_id == "donchian_channel_breakout_v1":
            self._apply_donchian_strategy_body(spec)
        elif family_id == "funding_rate_positioning_fade_v1":
            self._apply_funding_strategy_body(spec, exit_mode="midline_reversion_or_max_hold")
        return spec

    @staticmethod
    def _funding_percentile_operand() -> dict[str, Any]:
        return {
            "operand_type": "composed_operand",
            "composition_type": "rolling_empirical_percentile_v1",
            "source_operand": {
                "operand_type": "data_ref",
                "ref": "funding_rate",
                "field": "funding_rate",
                "timeframe": None,
                "lookback": None,
            },
            "lookback": {"bars_parameter_ref": "funding_lookback_bars"},
            "min_periods_policy": "full_window",
            "tie_policy": "weak_rank",
            "nan_policy": "null_output",
        }

    @staticmethod
    def _parameter_operand(name: str) -> dict[str, Any]:
        return {
            "operand_type": "parameter_ref",
            "ref": name,
            "field": None,
            "timeframe": None,
            "lookback": None,
        }

    @staticmethod
    def _constant_operand(value: float) -> dict[str, Any]:
        return {
            "operand_type": "constant",
            "ref": value,
            "field": None,
            "timeframe": None,
            "lookback": None,
        }

    @classmethod
    def _funding_condition(
        cls, condition_id: str, operator: str, right_operand: dict[str, Any], role: str
    ) -> dict[str, Any]:
        return {
            "condition_id": condition_id,
            "condition_role": role,
            "left_operand": cls._funding_percentile_operand(),
            "operator": operator,
            "right_operand": right_operand,
            "units": "percentile",
            "notes": "Trailing full-window funding-rate empirical percentile; no future fitting.",
        }

    @staticmethod
    def _funding_parameter(
        name: str,
        *,
        label: str,
        parameter_type: str,
        units: str,
        default: int | float,
        allowed_values: list[int | float],
        role: str,
    ) -> dict[str, Any]:
        numeric = [float(value) for value in allowed_values]
        positive_steps = [b - a for a, b in zip(numeric, numeric[1:]) if b > a]
        step: int | float = min(positive_steps) if positive_steps else 1
        if parameter_type == "integer":
            step = int(step)
        return {
            "name": name,
            "label": label,
            "description": f"Closed preregistered funding-family parameter: {name}.",
            "type": parameter_type,
            "units": units,
            "default": default,
            "range": {
                "min": min(allowed_values),
                "max": max(allowed_values),
                "step": step,
                "inclusive_min": True,
                "inclusive_max": True,
            },
            "allowed_values": allowed_values,
            "is_free_parameter": True,
            "included_in_variant_generation": True,
            "role": role,
            "rationale": "Frozen H-FUNDING-RATE-POSITIONING-FADE-01 denominator axis.",
            "constraints": ["No post-hoc values or adaptive fitting."],
        }

    @classmethod
    def _apply_funding_strategy_body(
        cls, spec: dict[str, Any], *, exit_mode: str
    ) -> None:
        timeframe = spec["timeframe_and_data"]["primary_timeframe"]
        spec["short_name"] = f"funding-positioning-fade-{exit_mode}-15m"
        spec["instruments"]["directions_allowed"] = ["long", "short"]
        spec["timeframe_and_data"]["host_data_refs"] = [
            {
                "stream": "ohlcv",
                "timeframe": timeframe,
                "field": field,
                "availability": "required",
            }
            for field in ("open", "high", "low", "close", "volume")
        ] + [
            {
                "stream": "funding",
                "timeframe": timeframe,
                "field": "funding_rate",
                "availability": "required",
            }
        ]
        spec["entry_logic"] = {
            "direction": "both",
            "groups": [
                {
                    "group_id": "ENTRY-LONG-FUNDING-LOW-TAIL",
                    "group_role": "required",
                    "logic": "all",
                    "conditions": [cls._funding_condition(
                        "LONG-FUNDING-PERCENTILE-LTE-LOWER",
                        "lte",
                        cls._parameter_operand("lower_entry_percentile"),
                        "required",
                    )],
                    "subgroups": [],
                    "notes": "Contrarian long entry at the preregistered lower tail.",
                    "side": "long",
                },
                {
                    "group_id": "ENTRY-SHORT-FUNDING-HIGH-TAIL",
                    "group_role": "required",
                    "logic": "all",
                    "conditions": [cls._funding_condition(
                        "SHORT-FUNDING-PERCENTILE-GTE-UPPER",
                        "gte",
                        cls._parameter_operand("upper_entry_percentile"),
                        "required",
                    )],
                    "subgroups": [],
                    "notes": "Contrarian short entry at the preregistered upper tail.",
                    "side": "short",
                },
            ],
            "notes": "Funding-rate positioning fade; contrarian direction only.",
        }
        exit_groups: list[dict[str, Any]] = []
        if exit_mode == "midline_reversion_or_max_hold":
            exit_groups = [
                {
                    "group_id": "EXIT-LONG-FUNDING-MIDLINE",
                    "group_role": "exit",
                    "logic": "all",
                    "conditions": [cls._funding_condition(
                        "LONG-FUNDING-PERCENTILE-GTE-MIDLINE",
                        "gte",
                        cls._constant_operand(0.5),
                        "exit",
                    )],
                    "subgroups": [],
                    "notes": "Long exits when funding percentile reverts to the midline.",
                    "side": "long",
                },
                {
                    "group_id": "EXIT-SHORT-FUNDING-MIDLINE",
                    "group_role": "exit",
                    "logic": "all",
                    "conditions": [cls._funding_condition(
                        "SHORT-FUNDING-PERCENTILE-LTE-MIDLINE",
                        "lte",
                        cls._constant_operand(0.5),
                        "exit",
                    )],
                    "subgroups": [],
                    "notes": "Short exits when funding percentile reverts to the midline.",
                    "side": "short",
                },
            ]
        spec["exit_logic"] = {
            "groups": exit_groups,
            "max_holding_period": {
                "enabled": True,
                "bars": {"parameter_ref": "max_hold_bars"},
            },
            "notes": f"Frozen exit_mode={exit_mode}; max hold is always active.",
        }
        spec["filters"] = {"groups": [], "none_declared": True}
        spec["free_parameters"] = {
            "max_free_parameters": 5,
            "counting_rule": (
                "parameters contains only entries where is_free_parameter=true; maxItems 5 "
                "enforces the D2-006-style MVP free-parameter cap"
            ),
            "parameters": [
                cls._funding_parameter(
                    "funding_lookback_bars", label="Funding percentile lookback", parameter_type="integer",
                    units="bars", default=2880, allowed_values=[2880, 8640, 17280], role="entry"
                ),
                cls._funding_parameter(
                    "lower_entry_percentile", label="Lower entry percentile", parameter_type="number",
                    units="ratio", default=0.1, allowed_values=[0.05, 0.1], role="entry"
                ),
                cls._funding_parameter(
                    "upper_entry_percentile", label="Upper entry percentile", parameter_type="number",
                    units="ratio", default=0.9, allowed_values=[0.9, 0.95], role="entry"
                ),
                cls._funding_parameter(
                    "max_hold_bars", label="Maximum holding period", parameter_type="integer",
                    units="bars", default=16, allowed_values=[16, 32, 96], role="exit"
                ),
            ],
            "no_free_parameters_declared": False,
        }
        spec["constraints"] = {
            "invalid_parameter_combinations": [],
            "unavailable_data_blockers": [],
            "deferred_pattern_blockers": [
                "Funding payments are not wired; funding_cost_mode remains off.",
                "This is a price-P&L funding-rate signal test.",
            ],
            "none_declared": False,
        }
        spec["provenance"]["unresolved_claims"] = [
            "Scratch-only non-canonical research artifact.",
            "Funding payments are excluded; this is not complete carry P&L.",
        ]

    @staticmethod
    def _indicator_operand(field: str) -> dict[str, Any]:
        return {
            "operand_type": "indicator_ref",
            "ref": "donchian",
            "field": field,
            "timeframe": None,
            "lookback": {"bars_parameter_ref": "channel_lookback_bars"},
        }

    @staticmethod
    def _close_operand() -> dict[str, Any]:
        return {
            "operand_type": "data_ref",
            "ref": "close",
            "field": "close",
            "timeframe": None,
            "lookback": None,
        }

    @classmethod
    def _donchian_condition(
        cls, condition_id: str, operator: str, field: str, role: str, notes: str
    ) -> dict[str, Any]:
        return {
            "condition_id": condition_id,
            "condition_role": role,
            "left_operand": cls._close_operand(),
            "operator": operator,
            "right_operand": cls._indicator_operand(field),
            "units": None,
            "notes": notes,
        }

    @classmethod
    def _apply_donchian_strategy_body(cls, spec: dict[str, Any]) -> None:
        timeframe = spec["timeframe_and_data"]["primary_timeframe"]
        spec["short_name"] = f"draft-donchian-breakout-{timeframe}"
        spec["timeframe_and_data"]["host_data_refs"] = [
            {
                "stream": "ohlcv",
                "timeframe": timeframe,
                "field": field,
                "availability": "required",
            }
            for field in ("open", "high", "low", "close", "volume")
        ] + [
            {
                "stream": "indicator_catalog",
                "timeframe": None,
                "field": "donchian",
                "availability": "required",
            }
        ]
        spec["entry_logic"] = {
            "direction": "both",
            "groups": [
                {
                    "group_id": "ENTRY-GROUP-LONG-DONCHIAN",
                    "group_role": "required",
                    "logic": "all",
                    "conditions": [
                        cls._donchian_condition(
                            "LONG-CLOSE-GT-DONCHIAN-UPPER-LAG1",
                            "gt",
                            "upper_lag1",
                            "required",
                            "Long entry when completed-bar close exceeds the prior Donchian upper channel.",
                        )
                    ],
                    "subgroups": [],
                    "notes": "Explicit long channel-breakout entry; no compiler mirroring.",
                    "side": "long",
                },
                {
                    "group_id": "ENTRY-GROUP-SHORT-DONCHIAN",
                    "group_role": "required",
                    "logic": "all",
                    "conditions": [
                        cls._donchian_condition(
                            "SHORT-CLOSE-LT-DONCHIAN-LOWER-LAG1",
                            "lt",
                            "lower_lag1",
                            "required",
                            "Short entry when completed-bar close falls below the prior Donchian lower channel.",
                        )
                    ],
                    "subgroups": [],
                    "notes": "Explicit short channel-breakout entry; no compiler mirroring.",
                    "side": "short",
                },
            ],
            "notes": "Both-direction close-confirmed breakout against lagged channel fields.",
        }
        spec["exit_logic"] = {
            "groups": [
                {
                    "group_id": "EXIT-GROUP-LONG-OPPOSITE-CHANNEL",
                    "group_role": "exit",
                    "logic": "all",
                    "conditions": [
                        cls._donchian_condition(
                            "LONG-CLOSE-LT-DONCHIAN-LOWER-LAG1",
                            "lt",
                            "lower_lag1",
                            "exit",
                            "Long exit on a completed-bar break below the prior lower channel.",
                        )
                    ],
                    "subgroups": [],
                    "notes": "Opposite-channel long exit.",
                    "side": "long",
                },
                {
                    "group_id": "EXIT-GROUP-SHORT-OPPOSITE-CHANNEL",
                    "group_role": "exit",
                    "logic": "all",
                    "conditions": [
                        cls._donchian_condition(
                            "SHORT-CLOSE-GT-DONCHIAN-UPPER-LAG1",
                            "gt",
                            "upper_lag1",
                            "exit",
                            "Short exit on a completed-bar break above the prior upper channel.",
                        )
                    ],
                    "subgroups": [],
                    "notes": "Opposite-channel short exit.",
                    "side": "short",
                },
            ],
            "max_holding_period": {"enabled": False, "bars": None},
            "notes": "Opposite-channel exits only; no invented stop or time-exit semantics.",
        }
        spec["risk_model"].update(
            {
                "stop_distance": None,
                "target_distance": None,
                "exposure_limits": [
                    "Scratch runner validation uses the existing 1.0 target-leverage realism surface."
                ],
                "leverage_visibility": "No runtime, paper/live, or capital authority.",
                "liquidation_sensitivity_notes": (
                    "No dedicated stop is encoded because this adapter may use only existing "
                    "validated grammar; opposite-channel exit is the bounded invalidation."
                ),
            }
        )
        spec["filters"] = {
            "groups": [],
            "none_declared": True,
        }
        spec["free_parameters"] = {
            "max_free_parameters": 5,
            "counting_rule": (
                "parameters contains only entries where is_free_parameter=true; maxItems 5 "
                "enforces the D2-006-style MVP free-parameter cap"
            ),
            "parameters": [
                {
                    "name": "channel_lookback_bars",
                    "label": "Donchian channel lookback bars",
                    "description": "Integer lookback for lagged Donchian upper/lower channels.",
                    "type": "integer",
                    "units": "bars",
                    "default": 20,
                    "range": {
                        "min": 20,
                        "max": 55,
                        "step": 35,
                        "inclusive_min": True,
                        "inclusive_max": True,
                    },
                    "allowed_values": [20, 55],
                    "is_free_parameter": True,
                    "included_in_variant_generation": True,
                    "role": "entry",
                    "rationale": "Bounded non-adaptive channel horizon grid for adapter validation.",
                    "constraints": [
                        "Binds only to donchian indicator_ref lookback via bars_parameter_ref."
                    ],
                }
            ],
            "no_free_parameters_declared": False,
        }
        spec["constraints"] = {
            "invalid_parameter_combinations": [],
            "unavailable_data_blockers": [],
            "deferred_pattern_blockers": [
                "No new indicator or compiler operator.",
                "No intrabar breakout semantics.",
                "No ATR stop, target, session exit, funding signal, or post-hoc narrowing.",
                "Distinct from STRAT-SPEC-0003 and RP-7134; this is not a novelty claim because prior Donchian experiment reports exist.",
            ],
            "none_declared": False,
        }
        spec["provenance"]["unresolved_claims"] = [
            "Adapter output is scratch-only and is not a research conclusion.",
            "H-002/REP-0003 and H-012/REP-0032 are prior Donchian evidence; no novelty is claimed.",
            "No canonical Donchian Result Population was found at adapter implementation time.",
        ]
        spec["backtest_realism_assumptions"].update(
            {
                "order_size_assumption": (
                    "Scratch offline runner validation uses the existing "
                    "dynamic_equity_target_leverage model at target_leverage=1.0."
                ),
                "liquidity_capacity_assumption": (
                    "Not active in this scratch adapter-validation artifact."
                ),
            }
        )


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
        features = set(draft.get("features", []))
        if "funding_rate" in features and not features.intersection({"sma", "stddev", "donchian"}):
            return "funding_rate_positioning_fade_v1"
        if "donchian" in features and not features.intersection({"sma", "stddev"}):
            return "donchian_channel_breakout_v1"
        if {"sma", "stddev"}.issubset(features) and "donchian" not in features:
            return "sma_stddev_mean_reversion_v1"
        return None

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

        adapted_draft = copy.deepcopy(parsed.draft)
        if (
            adapted_draft is not None
            and self._draft_family_id(adapted_draft) == "donchian_channel_breakout_v1"
        ):
            adapted_draft["parameter_bounds"] = [
                {"name": "channel_lookback_bars", "minimum": 20.0, "maximum": 55.0}
            ]

        if parsed.decision == "rejected" or parsed.draft is None:
            base_result["status"] = "rejected"
            base_result["rejection_reasons"] = list(parsed.rejection_reasons)
        else:
            base_result["status"] = "accepted"
            base_result["research_object"] = copy.deepcopy(adapted_draft)
            family_id = self._draft_family_id(adapted_draft)
            base_result["adapter_metadata"] = {
                "family_id": family_id,
                "freshness_distinct_from": (
                    ["STRAT-SPEC-0003", "VM-0003", "SWEEP-PLAN-0003", "RP-7134"]
                    if family_id == "donchian_channel_breakout_v1"
                    else []
                ),
                "unsupported_capabilities": (
                    [
                        "intrabar breakout",
                        "ATR stop/target",
                        "session/time exit",
                        "funding signal",
                    ]
                    if family_id == "donchian_channel_breakout_v1"
                    else []
                ),
                "prior_family_evidence": (
                    ["H-002/REP-0003", "H-012/REP-0032"]
                    if family_id == "donchian_channel_breakout_v1"
                    else []
                ),
            }
            blockers = list(assessment["blocking_features"])
            if blockers:
                base_result["status"] = "needs_data"
                base_result["draft_strategy_spec"]["blockers"] = [
                    f"missing historical/compiler support: {item}" for item in blockers
                ]
            elif not self._draft_family_supported(adapted_draft, assessment):
                base_result["draft_strategy_spec"]["blockers"] = [
                    "no validated draft adapter exists for this exact primitive family"
                ]

        formalized_path = self._write_json(run_dir / "formalized_idea.json", base_result)
        if (
            base_result["status"] == "accepted"
            and adapted_draft is not None
            and self._draft_family_supported(adapted_draft, assessment)
        ):
            spec = self._build_strategy_spec(
                run_id=run_id,
                draft=adapted_draft,
                provider_metadata=base_result["provider_metadata"],
                formalized_path=formalized_path,
            )
            spec_path = run_dir / f"{spec['strategy_spec_id']}.strategy_spec.json"
            self._write_json(spec_path, spec)
            if family_id == "funding_rate_positioning_fade_v1":
                fixed_spec = copy.deepcopy(spec)
                fixed_spec["strategy_spec_id"] = f"STRAT-SPEC-{int(spec['strategy_spec_id'][-4:]) + 1:04d}"
                fixed_spec["title"] = "Draft funding-rate positioning-fade fixed-max-hold Strategy Spec"
                self._apply_funding_strategy_body(fixed_spec, exit_mode="fixed_max_hold_only")
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
