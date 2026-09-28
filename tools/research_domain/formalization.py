"""Pure CPW idea formalization and Strategy-Spec draft construction."""

from __future__ import annotations

import copy
import re
from collections.abc import Collection, Mapping
from itertools import pairwise
from typing import Any

from .contracts import LOCKED_TIMEFRAMES


def detect_features(idea: str, indicator_ids: Collection[str]) -> list[str]:
    """Detect the current supported features in stable legacy order."""

    if not isinstance(idea, str) or not all(isinstance(item, str) for item in indicator_ids):
        raise ValueError("idea and indicator_ids must contain strings")
    lower = idea.casefold()
    features = sorted(
        feature for feature in indicator_ids if re.search(rf"\b{re.escape(feature)}\b", lower)
    )
    if any(term in lower for term in ("taker flow", "taker-flow", "aggressive buy", "aggtrades")):
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


def assess_capabilities(
    idea: str,
    indicator_catalog: Mapping[str, Any],
    availability_catalog: Mapping[str, Any],
) -> dict[str, Any]:
    """Assess already-loaded catalog data without file or provider access."""

    indicator_ids = {
        entry["indicator_id"]
        for entry in indicator_catalog.get("entries", [])
        if isinstance(entry, Mapping) and isinstance(entry.get("indicator_id"), str)
    }
    detected = detect_features(idea, indicator_ids)
    entries = [
        entry for entry in availability_catalog.get("entries", []) if isinstance(entry, Mapping)
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
            warnings.extend(
                [
                    "Compiler field existence does not provide full historical OI data.",
                    "Trades and aggregate trades cannot reconstruct true open interest.",
                ]
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
        if item["historical_testability"] in {"vendor_or_capture_constrained", "blocked_unknown"}
        or not item["compiler_field_exists"]
    ]
    return {
        "detected_features": detected,
        "feature_assessments": assessments,
        "historically_testable_now": bool(assessments) and not blockers,
        "blocking_features": blockers,
        "distinction": "compiler field existence is separate from historical testability",
    }


def _draft_family_id(draft: Mapping[str, Any]) -> str | None:
    features = set(draft.get("features", []))
    if "funding_rate" in features and not features.intersection({"sma", "stddev", "donchian"}):
        return "funding_rate_positioning_fade_v1"
    if "donchian" in features and not features.intersection({"sma", "stddev"}):
        return "donchian_channel_breakout_v1"
    if {"sma", "stddev"}.issubset(features) and "donchian" not in features:
        return "sma_stddev_mean_reversion_v1"
    return None


def _replace_timeframe(value: Any, timeframe: str) -> Any:
    if isinstance(value, dict):
        return {key: _replace_timeframe(child, timeframe) for key, child in value.items()}
    if isinstance(value, list):
        return [_replace_timeframe(child, timeframe) for child in value]
    if isinstance(value, str):
        return re.sub(r"\b15m\b", timeframe, value)
    return value


def build_strategy_spec(
    *,
    run_id: str,
    draft: Mapping[str, Any],
    template: Mapping[str, Any],
    provider_metadata: Mapping[str, Any] | None = None,
    formalized_path: str | None = None,
    source_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the exact current scratch Strategy-Spec draft without I/O."""

    try:
        numeric_id = 9000 + (int(run_id[:8], 16) % 1000)
        timeframe = str(draft["timeframe"])
        symbols = list(draft["symbols"])
        rationale = str(draft["causal_rationale"])
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        raise ValueError("invalid Strategy-Spec draft inputs") from exc
    if not symbols:
        raise ValueError("draft symbols must not be empty")
    if source_context is None:
        if provider_metadata is None or not formalized_path:
            raise ValueError("provider metadata and formalized path are required")
        try:
            provider_values = {
                key: provider_metadata[key]
                for key in ("provider_mode", "provider_id", "request_id", "response_source")
            }
        except (KeyError, TypeError) as exc:
            raise ValueError("invalid Strategy-Spec source context") from exc
        source_context = {
            "source_type": "manual_idea",
            "source_refs": [formalized_path],
            "prepared_by": "bounded idea_formalizer agent",
            "source_constraints": [
                f"provider_mode={provider_values['provider_mode']}",
                f"provider_id={provider_values['provider_id']}",
                f"request_id={provider_values['request_id']}",
                f"response_source={provider_values['response_source']}",
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
    try:
        source_type = str(source_context["source_type"])
        source_refs = [str(item) for item in source_context["source_refs"]]
        prepared_by = str(source_context["prepared_by"])
        source_constraints = [str(item) for item in source_context["source_constraints"]]
        unresolved_claims = [str(item) for item in source_context["unresolved_claims"]]
        review_notes = [str(item) for item in source_context["review_notes"]]
        lineage_ref_path = str(source_context["lineage_ref_path"])
        default_title = str(
            source_context.get(
                "default_title", "Draft CPW-domain SMA/stddev mean-reversion Strategy Spec"
            )
        )
    except (KeyError, TypeError) as exc:
        raise ValueError("invalid Strategy-Spec source context") from exc
    if (
        not all(
            (
                source_type,
                source_refs,
                prepared_by,
                source_constraints,
                unresolved_claims,
                review_notes,
            )
        )
        or not lineage_ref_path
    ):
        raise ValueError("invalid Strategy-Spec source context")
    family_id = _draft_family_id(draft)
    spec = _replace_timeframe(copy.deepcopy(dict(template)), timeframe)
    try:
        spec["strategy_spec_id"] = f"STRAT-SPEC-{numeric_id:04d}"
        spec["title"] = {
            "donchian_channel_breakout_v1": "Draft deterministic Donchian channel-breakout Strategy Spec",
            "funding_rate_positioning_fade_v1": "Draft funding-rate positioning-fade Strategy Spec",
        }.get(family_id, default_title)
        spec["short_name"] = f"draft-idea-{run_id}"
        spec["status"] = "draft"
        spec["instruments"]["symbols"] = symbols
        spec["timeframe_and_data"]["gap_handling_assumption"] = (
            f"Use existing cataloged {symbols[0]} {timeframe} OHLCV and the "
            "merged research-workbench gap policy; do not interpolate or silently fill gaps."
        )
        spec["provenance"] = {
            "source_type": source_type,
            "source_refs": source_refs,
            "prepared_by": prepared_by,
            "created_at": None,
            "updated_at": None,
            "rationale": rationale,
            "source_constraints": source_constraints
            + [
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
            "unresolved_claims": unresolved_claims,
        }
        spec["review"].update(
            {
                "reviewer": None,
                "reviewed_at": None,
                "review_notes": review_notes,
                "approval_scope": "none",
            }
        )
        spec["lineage"] = {
            "parent_refs": [
                {
                    "ref_type": "concept",
                    "ref_id": f"IDEA-{run_id.upper()}",
                    "ref_path": lineage_ref_path,
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
    except (KeyError, TypeError) as exc:
        raise ValueError("invalid Strategy-Spec template") from exc
    if family_id == "donchian_channel_breakout_v1":
        _apply_donchian_strategy_body(spec)
    elif family_id == "funding_rate_positioning_fade_v1":
        _apply_funding_strategy_body(spec, exit_mode="midline_reversion_or_max_hold")
    return spec


def formalize_reasoned_strategy_draft(
    *,
    idea: str,
    symbol: str,
    timeframe: str,
    constraints: Collection[str],
    reasoned_draft: Mapping[str, Any],
    indicator_catalog: Mapping[str, Any],
    availability_catalog: Mapping[str, Any],
    strategy_spec_template: Mapping[str, Any],
    run_id: str,
    source_context: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply the current CPW reasoned-draft semantics without I/O or authority."""

    if not isinstance(idea, str) or not idea.strip():
        raise ValueError("idea must be non-empty")
    if symbol != "BTCUSDT":
        raise ValueError("current repo capability is bounded to BTCUSDT")
    if timeframe not in LOCKED_TIMEFRAMES:
        raise ValueError(f"timeframe must be one of {sorted(LOCKED_TIMEFRAMES)}")
    if not all(isinstance(item, str) for item in constraints):
        raise ValueError("constraints must contain strings")
    if not isinstance(reasoned_draft, Mapping):
        raise ValueError("reasoned_draft must be an object")  # noqa: TRY004

    assessment = assess_capabilities(idea.strip(), indicator_catalog, availability_catalog)
    declared_features = set(reasoned_draft.get("features", []))
    detected_features = set(assessment["detected_features"])
    response_contract_errors: list[str] = []
    if not declared_features.issubset(detected_features):
        response_contract_errors.append(
            "provider response claims features not detected in the operator idea"
        )
    if reasoned_draft.get("symbols") != [symbol]:
        response_contract_errors.append(
            "provider response symbols do not match the bounded operator input"
        )
    if reasoned_draft.get("timeframe") != timeframe:
        response_contract_errors.append(
            "provider response timeframe does not match the bounded operator input"
        )
    if response_contract_errors:
        return {
            "status": "rejected",
            "capability_assessment": assessment,
            "research_object": None,
            "rejection_reasons": response_contract_errors,
            "adapter_metadata": {
                "family_id": None,
                "freshness_distinct_from": [],
                "unsupported_capabilities": [],
            },
            "draft_strategy_specs": [],
            "draft_strategy_spec": {"produced": False, "blockers": []},
        }

    adapted_draft = copy.deepcopy(dict(reasoned_draft))
    family_id = _draft_family_id(adapted_draft)
    if family_id == "donchian_channel_breakout_v1":
        adapted_draft["parameter_bounds"] = [
            {"name": "channel_lookback_bars", "minimum": 20.0, "maximum": 55.0}
        ]
    adapter_metadata = {
        "family_id": family_id,
        "freshness_distinct_from": (
            ["STRAT-SPEC-0003", "VM-0003", "SWEEP-PLAN-0003", "RP-7134"]
            if family_id == "donchian_channel_breakout_v1"
            else []
        ),
        "unsupported_capabilities": (
            ["intrabar breakout", "ATR stop/target", "session/time exit", "funding signal"]
            if family_id == "donchian_channel_breakout_v1"
            else []
        ),
        "prior_family_evidence": (
            ["H-002/REP-0003", "H-012/REP-0032"]
            if family_id == "donchian_channel_breakout_v1"
            else []
        ),
    }
    blockers = [
        f"missing historical/compiler support: {item}" for item in assessment["blocking_features"]
    ]
    status = "needs_data" if blockers else "accepted"
    if not blockers and (family_id is None or not assessment["historically_testable_now"]):
        blockers = ["no validated draft adapter exists for this exact primitive family"]

    specs: list[dict[str, Any]] = []
    if status == "accepted" and not blockers:
        primary = build_strategy_spec(
            run_id=run_id,
            draft=adapted_draft,
            template=strategy_spec_template,
            source_context=source_context,
        )
        specs.append(primary)
        if family_id == "funding_rate_positioning_fade_v1":
            fixed = copy.deepcopy(primary)
            fixed["strategy_spec_id"] = (
                f"STRAT-SPEC-{int(primary['strategy_spec_id'][-4:]) + 1:04d}"
            )
            fixed["title"] = "Draft funding-rate positioning-fade fixed-max-hold Strategy Spec"
            _apply_funding_strategy_body(fixed, exit_mode="fixed_max_hold_only")
            specs.append(fixed)

    return {
        "status": status,
        "capability_assessment": assessment,
        "research_object": adapted_draft,
        "rejection_reasons": [],
        "adapter_metadata": adapter_metadata,
        "draft_strategy_specs": specs,
        "draft_strategy_spec": {"produced": bool(specs), "blockers": blockers},
    }


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


def _parameter_operand(name: str) -> dict[str, Any]:
    return {
        "operand_type": "parameter_ref",
        "ref": name,
        "field": None,
        "timeframe": None,
        "lookback": None,
    }


def _constant_operand(value: float) -> dict[str, Any]:
    return {
        "operand_type": "constant",
        "ref": value,
        "field": None,
        "timeframe": None,
        "lookback": None,
    }


def _funding_condition(
    condition_id: str, operator: str, right_operand: dict[str, Any], role: str
) -> dict[str, Any]:
    return {
        "condition_id": condition_id,
        "condition_role": role,
        "left_operand": _funding_percentile_operand(),
        "operator": operator,
        "right_operand": right_operand,
        "units": "percentile",
        "notes": "Trailing full-window funding-rate empirical percentile; no future fitting.",
    }


def _funding_parameter(
    name: str,
    *,
    label: str,
    parameter_type: str,
    units: str,
    default: float,
    allowed_values: list[float],
    role: str,
) -> dict[str, Any]:
    numeric = [float(value) for value in allowed_values]
    positive_steps = [b - a for a, b in pairwise(numeric) if b > a]
    step = min(positive_steps) if positive_steps else 1
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


def _apply_funding_strategy_body(spec: dict[str, Any], *, exit_mode: str) -> None:
    timeframe = spec["timeframe_and_data"]["primary_timeframe"]
    spec["short_name"] = f"funding-positioning-fade-{exit_mode}-15m"
    spec["instruments"]["directions_allowed"] = ["long", "short"]
    spec["timeframe_and_data"]["host_data_refs"] = [
        {"stream": "ohlcv", "timeframe": timeframe, "field": field, "availability": "required"}
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
                "conditions": [
                    _funding_condition(
                        "LONG-FUNDING-PERCENTILE-LTE-LOWER",
                        "lte",
                        _parameter_operand("lower_entry_percentile"),
                        "required",
                    )
                ],
                "subgroups": [],
                "notes": "Contrarian long entry at the preregistered lower tail.",
                "side": "long",
            },
            {
                "group_id": "ENTRY-SHORT-FUNDING-HIGH-TAIL",
                "group_role": "required",
                "logic": "all",
                "conditions": [
                    _funding_condition(
                        "SHORT-FUNDING-PERCENTILE-GTE-UPPER",
                        "gte",
                        _parameter_operand("upper_entry_percentile"),
                        "required",
                    )
                ],
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
                "conditions": [
                    _funding_condition(
                        "LONG-FUNDING-PERCENTILE-GTE-MIDLINE", "gte", _constant_operand(0.5), "exit"
                    )
                ],
                "subgroups": [],
                "notes": "Long exits when funding percentile reverts to the midline.",
                "side": "long",
            },
            {
                "group_id": "EXIT-SHORT-FUNDING-MIDLINE",
                "group_role": "exit",
                "logic": "all",
                "conditions": [
                    _funding_condition(
                        "SHORT-FUNDING-PERCENTILE-LTE-MIDLINE",
                        "lte",
                        _constant_operand(0.5),
                        "exit",
                    )
                ],
                "subgroups": [],
                "notes": "Short exits when funding percentile reverts to the midline.",
                "side": "short",
            },
        ]
    spec["exit_logic"] = {
        "groups": exit_groups,
        "max_holding_period": {"enabled": True, "bars": {"parameter_ref": "max_hold_bars"}},
        "notes": f"Frozen exit_mode={exit_mode}; max hold is always active.",
    }
    spec["filters"] = {"groups": [], "none_declared": True}
    spec["free_parameters"] = {
        "max_free_parameters": 5,
        "counting_rule": "parameters contains only entries where is_free_parameter=true; maxItems 5 enforces the D2-006-style MVP free-parameter cap",
        "parameters": [
            _funding_parameter(
                "funding_lookback_bars",
                label="Funding percentile lookback",
                parameter_type="integer",
                units="bars",
                default=2880,
                allowed_values=[2880, 8640, 17280],
                role="entry",
            ),
            _funding_parameter(
                "lower_entry_percentile",
                label="Lower entry percentile",
                parameter_type="number",
                units="ratio",
                default=0.1,
                allowed_values=[0.05, 0.1],
                role="entry",
            ),
            _funding_parameter(
                "upper_entry_percentile",
                label="Upper entry percentile",
                parameter_type="number",
                units="ratio",
                default=0.9,
                allowed_values=[0.9, 0.95],
                role="entry",
            ),
            _funding_parameter(
                "max_hold_bars",
                label="Maximum holding period",
                parameter_type="integer",
                units="bars",
                default=16,
                allowed_values=[16, 32, 96],
                role="exit",
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


def _indicator_operand(field: str) -> dict[str, Any]:
    return {
        "operand_type": "indicator_ref",
        "ref": "donchian",
        "field": field,
        "timeframe": None,
        "lookback": {"bars_parameter_ref": "channel_lookback_bars"},
    }


def _close_operand() -> dict[str, Any]:
    return {
        "operand_type": "data_ref",
        "ref": "close",
        "field": "close",
        "timeframe": None,
        "lookback": None,
    }


def _donchian_condition(
    condition_id: str, operator: str, field: str, role: str, notes: str
) -> dict[str, Any]:
    return {
        "condition_id": condition_id,
        "condition_role": role,
        "left_operand": _close_operand(),
        "operator": operator,
        "right_operand": _indicator_operand(field),
        "units": None,
        "notes": notes,
    }


def _apply_donchian_strategy_body(spec: dict[str, Any]) -> None:
    timeframe = spec["timeframe_and_data"]["primary_timeframe"]
    spec["short_name"] = f"draft-donchian-breakout-{timeframe}"
    spec["timeframe_and_data"]["host_data_refs"] = [
        {"stream": "ohlcv", "timeframe": timeframe, "field": field, "availability": "required"}
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
                    _donchian_condition(
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
                    _donchian_condition(
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
                    _donchian_condition(
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
                    _donchian_condition(
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
            "liquidation_sensitivity_notes": "No dedicated stop is encoded because this adapter may use only existing validated grammar; opposite-channel exit is the bounded invalidation.",
        }
    )
    spec["filters"] = {"groups": [], "none_declared": True}
    spec["free_parameters"] = {
        "max_free_parameters": 5,
        "counting_rule": "parameters contains only entries where is_free_parameter=true; maxItems 5 enforces the D2-006-style MVP free-parameter cap",
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
            "order_size_assumption": "Scratch offline runner validation uses the existing dynamic_equity_target_leverage model at target_leverage=1.0.",
            "liquidity_capacity_assumption": "Not active in this scratch adapter-validation artifact.",
        }
    )
