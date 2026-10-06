from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from tools.mcp.project_evidence.domain_tools import (
    CPW_DOMAIN_TOOL_NAMES,
    CapabilityAssessmentInput,
    FormalizeStrategyDraftInput,
    PreregistrationPacketInput,
    TrialDenominatorInput,
)
from tools.mcp.project_evidence.models import ResourceDeniedError
from tools.mcp.project_evidence.service import ProjectEvidenceService

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_SHA = "1" * 40
OLD_TOOL_NAMES = {
    "project_evidence_manifest",
    "list_project_resources",
    "read_project_resource",
    "run_evidence_query",
    "lookup_research_memory",
    "check_dependency_security_watch",
    "submit_proposal",
    "submit_prepared_payload",
}


@pytest.fixture()
def service(tmp_path: Path) -> ProjectEvidenceService:
    return ProjectEvidenceService(
        REPO_ROOT,
        repo_sha=REPO_SHA,
        branch="test",
        outbox_root=tmp_path / "outbox",
    )


def _draft(*, features: list[str] | None = None, timeframe: str = "15m") -> dict[str, object]:
    return {
        "summary": "Bounded research draft",
        "causal_rationale": "Positioning pressure or breakout momentum may persist.",
        "falsifiable_prediction": "The completed-bar signal has positive OOS expectancy.",
        "symbols": ["BTCUSDT"],
        "timeframe": timeframe,
        "features": features or ["donchian", "ohlcv"],
        "entry_concept": "Enter at the next bar open after confirmation.",
        "exit_concept": "Exit at the declared opposite condition.",
        "parameter_bounds": [{"name": "lookback", "minimum": 10.0, "maximum": 20.0}],
        "stop_conditions": ["Stop if preregistered OOS thresholds fail."],
    }


def _formalize_input(**updates: object) -> dict[str, object]:
    value: dict[str, object] = {
        "idea": "BTCUSDT price donchian breakout momentum",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "constraints": [],
        "reasoned_draft": _draft(),
        "evidence_resource_uris": [],
    }
    value.update(updates)
    return value


def _prereg_input() -> dict[str, object]:
    return {
        "pipeline_run_id": "LPIPE-HERMES-1",
        "request": {"request_id": "REQ-HERMES-1", "idea": "bounded"},
        "formalized": {"status": "accepted"},
        "availability": {"status": "ready", "blocking_reasons": []},
    }


def _rehash_packet(packet: dict[str, object]) -> None:
    unhashed = copy.deepcopy(packet)
    unhashed.pop("packet_sha256", None)
    canonical = json.dumps(
        unhashed, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    packet["packet_sha256"] = "sha256:" + hashlib.sha256(canonical).hexdigest()


def test_inventory_is_exactly_fourteen_without_generic_invoke() -> None:
    source = (REPO_ROOT / "tools/mcp/project_evidence/server.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    registered = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and any(
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Attribute)
            and decorator.func.attr == "tool"
            for decorator in node.decorator_list
        )
    }
    assert registered == OLD_TOOL_NAMES
    assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "_CPW_DOMAIN_TOOL_HANDLERS"
            for target in node.targets
        )
    )
    handlers = {
        item.id
        for item in assignment.value.elts
        if isinstance(item, ast.Name)  # type: ignore[union-attr]
    }
    inventory = registered | handlers
    assert handlers == set(CPW_DOMAIN_TOOL_NAMES)
    integration_assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name)
            and target.id == "_BOUNDED_RESEARCH_INTENT_HANDLERS"
            for target in node.targets
        )
    )
    integration_handlers = {
        item.id
        for item in integration_assignment.value.elts
        if isinstance(item, ast.Name)  # type: ignore[union-attr]
    }
    inventory |= integration_handlers
    assert integration_handlers == {"cpw_build_bounded_research_intent"}
    assert inventory == OLD_TOOL_NAMES | set(CPW_DOMAIN_TOOL_NAMES) | integration_handlers
    assert len(inventory) == 14
    assert not any("invoke" in name for name in inventory)


@pytest.mark.parametrize(
    "model,payload",
    [
        (CapabilityAssessmentInput, {"idea": "x", "shell": "cmd"}),
        (CapabilityAssessmentInput, {"idea": "   "}),
        (FormalizeStrategyDraftInput, _formalize_input(symbol="ETHUSDT")),
        (FormalizeStrategyDraftInput, _formalize_input(timeframe="5m")),
        (
            FormalizeStrategyDraftInput,
            _formalize_input(reasoned_draft={**_draft(), "unknown": True}),
        ),
        (
            FormalizeStrategyDraftInput,
            _formalize_input(
                reasoned_draft={
                    **_draft(),
                    "parameter_bounds": [
                        {"name": "lookback", "minimum": float("nan"), "maximum": 20.0}
                    ],
                }
            ),
        ),
        (
            FormalizeStrategyDraftInput,
            _formalize_input(evidence_resource_uris=["../../secrets/.env"]),
        ),
        (
            PreregistrationPacketInput,
            {**_prereg_input(), "output_path": "research/strategy_specs/new.json"},
        ),
        (
            TrialDenominatorInput,
            {
                "declared_trials": [
                    {"strategy_family": "f", "variant_id": "v", "trial_id": "t", "params": {}},
                    {"strategy_family": "f", "variant_id": "v2", "trial_id": "t", "params": {}},
                ],
                "ledger": [],
            },
        ),
        (
            TrialDenominatorInput,
            {
                "declared_trials": [
                    {"strategy_family": "f", "variant_id": "v", "trial_id": "t", "params": {}}
                ],
                "ledger": [{"trial_id": "t", "trial_status": "winner"}],
            },
        ),
    ],
)
def test_strict_inputs_fail_closed(model: object, payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        model.model_validate(payload)  # type: ignore[attr-defined]


def test_fixed_and_caller_evidence_are_reresolved(service: ProjectEvidenceService) -> None:
    request = _formalize_input(evidence_resource_uris=["project://status"])
    result = service.domain_tools.formalize_strategy_draft(request)

    anchors = result["evidence_anchors"]
    assert [item["resource_uri"] for item in anchors[:4]] == [
        "project://indicator-catalog",
        "project://feature-availability",
        "project://strategy-spec-template",
        "project://strategy-spec-schema",
    ]
    assert anchors[-1]["resource_uri"] == "project://status"
    assert all(item["repo_sha"] == REPO_SHA for item in anchors)
    assert all(len(item["artifact_sha256"]) == 64 for item in anchors)
    assert all(item["repo_path"] for item in anchors)
    with pytest.raises(ResourceDeniedError):
        service.domain_tools.formalize_strategy_draft(
            _formalize_input(evidence_resource_uris=["project://runtime"])
        )


def test_capability_assessment_is_deterministic_compute_only(
    service: ProjectEvidenceService,
) -> None:
    request = {"idea": "BTCUSDT price donchian breakout momentum"}
    before = (REPO_ROOT / "research/strategy_specs").glob("*")
    before_names = sorted(path.name for path in before)
    first = service.domain_tools.assess_research_capabilities(request)
    second = service.domain_tools.assess_research_capabilities(request)

    assert first == second
    assert first["domain_semantics"]["detected_features"] == ["donchian", "ohlcv"]
    assert first["boundary"]["cpw_domain_semantics"] is True
    assert first["boundary"]["canonical_write"] is False
    assert (
        sorted(path.name for path in (REPO_ROOT / "research/strategy_specs").glob("*"))
        == before_names
    )


def test_supported_formalization_is_schema_valid_deterministic_and_truthful(
    service: ProjectEvidenceService,
) -> None:
    request = _formalize_input()
    first = service.domain_tools.formalize_strategy_draft(request)
    second = service.domain_tools.formalize_strategy_draft(copy.deepcopy(request))

    assert first == second
    semantics = first["domain_semantics"]
    assert semantics["status"] == "accepted"
    assert semantics["research_object"]["parameter_bounds"] == [
        {"name": "channel_lookback_bars", "minimum": 20.0, "maximum": 55.0}
    ]
    assert len(semantics["draft_strategy_specs"]) == 1
    spec = semantics["draft_strategy_specs"][0]
    provenance = spec["provenance"]
    assert provenance["prepared_by"] == "bounded CPW Project-Evidence Hermes domain tool"
    assert provenance["source_refs"] == [item["resource_uri"] for item in first["evidence_anchors"]]
    assert "provider_mode=" not in json.dumps(provenance)
    assert "idea_formalizer agent" not in json.dumps(provenance)
    parent = spec["lineage"]["parent_refs"][0]
    assert parent["ref_type"] == "concept"
    assert parent["ref_path"] is None
    assert parent["ref_hash"] == first["input_sha256"]


def test_formalization_preserves_rejection_unsupported_and_needs_data(
    service: ProjectEvidenceService,
) -> None:
    claimed = service.domain_tools.formalize_strategy_draft(
        _formalize_input(reasoned_draft=_draft(features=["sma", "ohlcv"]))
    )["domain_semantics"]
    assert claimed["status"] == "rejected"
    assert claimed["draft_strategy_specs"] == []

    unsupported = service.domain_tools.formalize_strategy_draft(
        _formalize_input(
            idea="BTCUSDT price ema momentum",
            reasoned_draft=_draft(features=["ema", "ohlcv"]),
        )
    )["domain_semantics"]
    assert unsupported["status"] == "accepted"
    assert unsupported["draft_strategy_specs"] == []
    assert unsupported["draft_strategy_spec"]["blockers"] == [
        "no validated draft adapter exists for this exact primitive family"
    ]

    needs_data = service.domain_tools.formalize_strategy_draft(
        _formalize_input(
            idea="BTCUSDT price liquidation pressure",
            reasoned_draft=_draft(features=["liquidation_volume", "ohlcv"]),
        )
    )["domain_semantics"]
    assert needs_data["status"] == "needs_data"
    assert needs_data["draft_strategy_specs"] == []


def test_symbol_timeframe_mismatch_and_funding_dual_specs(service: ProjectEvidenceService) -> None:
    wrong_symbol = service.domain_tools.formalize_strategy_draft(
        _formalize_input(reasoned_draft={**_draft(), "symbols": ["ETHUSDT"]})
    )["domain_semantics"]
    assert wrong_symbol["status"] == "rejected"

    wrong_timeframe = service.domain_tools.formalize_strategy_draft(
        _formalize_input(reasoned_draft=_draft(timeframe="1h"))
    )["domain_semantics"]
    assert wrong_timeframe["status"] == "rejected"

    funding = service.domain_tools.formalize_strategy_draft(
        _formalize_input(
            idea="BTCUSDT funding rate because positioning pressure mean reverts",
            reasoned_draft=_draft(features=["funding_rate"]),
        )
    )["domain_semantics"]
    assert funding["status"] == "accepted"
    assert len(funding["draft_strategy_specs"]) == 2
    assert [spec["exit_logic"]["notes"] for spec in funding["draft_strategy_specs"]] == [
        "Frozen exit_mode=midline_reversion_or_max_hold; max hold is always active.",
        "Frozen exit_mode=fixed_max_hold_only; max hold is always active.",
    ]


def test_preregistration_and_requirement_preserve_non_authority(
    service: ProjectEvidenceService,
) -> None:
    packet_result = service.domain_tools.build_preregistration_packet(_prereg_input())
    packet = packet_result["domain_semantics"]
    assert packet_result == service.domain_tools.build_preregistration_packet(_prereg_input())
    assert packet["frozen_content"]["canonical_write_allowed"] is False
    assert packet["frozen_content"]["paper_live_runtime_contact_allowed"] is False
    assert packet["frozen_content"]["scheduler_autonomy_allowed"] is False

    requirement = service.domain_tools.build_approval_requirement(
        {"preregistration_packet": packet}
    )["domain_semantics"]
    assert requirement["required_fields"]["approved_by"] == "Karl"
    assert requirement["required_fields"]["authorizes_canonical_write"] is False
    encoded = json.dumps(requirement).lower()
    assert "approval_token" not in encoded
    assert "gate_action_id" not in requirement
    assert "approval_timestamp_utc" not in requirement


@pytest.mark.parametrize(
    "tamper",
    (
        "canonical_write_allowed",
        "execution_scope",
        "non_authority_flags",
        "extra_top_level",
        "approval_binding",
    ),
)
def test_approval_requirement_rejects_rehashed_altered_packets(
    service: ProjectEvidenceService, tamper: str
) -> None:
    packet = copy.deepcopy(
        service.domain_tools.build_preregistration_packet(_prereg_input())["domain_semantics"]
    )
    if tamper == "canonical_write_allowed":
        packet["frozen_content"]["canonical_write_allowed"] = True
    elif tamper == "execution_scope":
        packet["frozen_content"]["execution_scope"] = "canonical_or_live"
    elif tamper == "non_authority_flags":
        packet["non_authority_flags"]["canonical_write"] = True
    elif tamper == "extra_top_level":
        packet["extra"] = "caller-controlled"
    else:
        packet["approval_binding"]["required_approval_scope"] = "unbounded"
    _rehash_packet(packet)

    with pytest.raises(ValueError, match="not the exact locked CPW packet"):
        service.domain_tools.build_approval_requirement({"preregistration_packet": packet})


def test_denominator_preserves_all_rows_and_reports_stable_failure(
    service: ProjectEvidenceService,
) -> None:
    trials = [
        {"strategy_family": "f", "variant_id": "v1", "trial_id": "t1", "params": {}},
        {"strategy_family": "f", "variant_id": "v2", "trial_id": "t2", "params": {}},
        {"strategy_family": "f", "variant_id": "v3", "trial_id": "t3", "params": {}},
        {"strategy_family": "f", "variant_id": "v4", "trial_id": "t4", "params": {}},
    ]
    ledger = [
        {"trial_id": "t1", "trial_status": "completed"},
        {"trial_id": "t2", "trial_status": "failed"},
        {"trial_id": "t3", "trial_status": "pruned"},
        {"trial_id": "t4", "trial_status": "blocked"},
    ]
    valid = service.domain_tools.validate_trial_denominator(
        {"declared_trials": trials, "ledger": ledger}
    )["domain_semantics"]
    assert valid["valid"] is True
    assert valid["declared_count"] == valid["ledger_count"] == 4
    assert valid["trial_status_counts"] == {
        "completed": 1,
        "failed": 1,
        "invalid": 0,
        "pruned": 1,
        "blocked": 1,
    }

    invalid = service.domain_tools.validate_trial_denominator(
        {"declared_trials": trials, "ledger": ledger[:-1]}
    )["domain_semantics"]
    assert invalid["valid"] is False
    assert invalid["error_code"] == "invalid_trial_denominator"
    assert invalid["ledger_trial_ids"] == ["t1", "t2", "t3"]


def test_domain_tool_module_cannot_import_protected_surfaces() -> None:
    path = REPO_ROOT / "tools/mcp/project_evidence/domain_tools.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    forbidden = (
        "prefect",
        "tools.research_search",
        "tools.research_runner",
        "tools.canon_intake",
        "tools.hermes.broker",
        "lib.backtest",
        "src.",
    )
    assert not [name for name in imports if name.startswith(forbidden)]
