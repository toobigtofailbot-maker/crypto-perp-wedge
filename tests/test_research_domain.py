from __future__ import annotations

import ast
import copy
import json
from collections.abc import Mapping
from pathlib import Path

import pytest

from tools.lab_pipeline import adapters, gate_actions, orchestrator
from tools.research_agents.idea_formalizer_agent import IdeaFormalizerAgent
from tools.research_domain import formalization as domain_formalization
from tools.research_domain.contracts import (
    PREREG_APPROVAL_SCOPE,
    PREREG_NON_AUTHORITY_ASSERTIONS,
    TRIAL_STATUSES,
)
from tools.research_domain.formalization import (
    assess_capabilities,
    build_strategy_spec,
    detect_features,
    formalize_reasoned_strategy_draft,
)
from tools.research_domain.preregistration import (
    build_approval_marker,
    build_approval_requirement,
    build_approval_template,
    build_preregistration_packet,
    validate_bound_requirement,
    validate_prereg_approval,
)
from tools.research_domain.scientific_accounting import (
    build_bridge_ledger_rows,
    compare_result_populations,
    validate_declared_trials,
    validate_trial_denominator,
    validate_variant_denominator,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _packet() -> dict[str, object]:
    request = {
        "request_id": "REQ-1",
        "source_idea": "BTCUSDT 15m close mean reversion",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
    }
    return build_preregistration_packet(
        pipeline_run_id="LPIPE-1",
        request=request,
        formalized={"request_id": "REQ-1", "source_idea": request["source_idea"]},
        availability={"status": "ready", "blocking_reasons": []},
    )


def _approval(packet: dict[str, object]) -> dict[str, object]:
    return build_approval_template(packet, approval_timestamp_utc="2026-07-08T00:00:00Z")


def test_domain_packages_have_only_framework_neutral_imports() -> None:
    forbidden = (
        "pydantic_ai",
        "prefect",
        "nautilus",
        "tools.agent_sandbox",
        "tools.lab_pipeline",
        "tools.lab_scheduler_shell",
        "tools.lab_state",
        "tools.research_automation",
        "tools.canon_intake",
        "tools.hermes",
        "lib.backtest",
        "src.",
    )
    for path in sorted((REPO_ROOT / "tools/research_domain").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imports.append(node.module)
        assert not [name for name in imports if name.lower().startswith(forbidden)]


def test_formalization_is_deterministic_and_preserves_wrapper_output() -> None:
    idea = "BTCUSDT price and donchian breakout using taker flow"
    assert detect_features(idea, {"donchian", "sma"}) == [
        "donchian",
        "taker_buy_sell_ratio",
        "ohlcv",
    ]
    indicator_catalog = {"entries": [{"indicator_id": "donchian"}]}
    availability_catalog = {
        "entries": [
            {
                "feature_name": "taker_buy_sell_ratio",
                "source_class": "PUBLIC_TRADE_ARCHIVE_DERIVATION",
                "coverage_class": "FULL_HISTORY_PUBLIC_ARCHIVE",
                "canonical_full_history_allowed": "conditional",
                "compiler_visible": True,
                "history_limitation": "requires archive materialization",
                "conditions": ["public archive"],
            }
        ]
    }
    first = assess_capabilities(idea, indicator_catalog, availability_catalog)
    assert first == assess_capabilities(idea, indicator_catalog, availability_catalog)

    template = json.loads(
        (REPO_ROOT / "research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json").read_text(
            encoding="utf-8"
        )
    )
    draft = {
        "timeframe": "15m",
        "symbols": ["BTCUSDT"],
        "causal_rationale": "Break prior completed-bar channel extremes.",
        "features": ["donchian", "ohlcv"],
    }
    provider = {
        "provider_mode": "fake_offline",
        "provider_id": "fake-rule-v1",
        "request_id": "REQ-PROVIDER-1",
        "response_source": "fixture",
    }
    pure = build_strategy_spec(
        run_id="123456789abc",
        draft=draft,
        provider_metadata=provider,
        formalized_path="scratch/WP/outputs/formalized.json",
        template=template,
    )
    agent = object.__new__(IdeaFormalizerAgent)
    agent._read_json = lambda _path: copy.deepcopy(template)  # type: ignore[method-assign]
    legacy = agent._build_strategy_spec(
        run_id="123456789abc",
        draft=draft,
        provider_metadata=provider,
        formalized_path="scratch/WP/outputs/formalized.json",
    )
    assert pure == legacy
    assert pure["strategy_spec_id"] == "STRAT-SPEC-9896"
    assert (
        pure["entry_logic"]["groups"][0]["conditions"][0]["right_operand"]["field"] == "upper_lag1"
    )
    assert pure["lineage"]["parent_refs"] == [
        {
            "ref_type": "concept",
            "ref_id": "IDEA-123456789ABC",
            "ref_path": "scratch/WP/outputs/formalized.json",
            "ref_hash": None,
        }
    ]
    assert template["strategy_spec_id"] == "STRAT-SPEC-0003"


def test_reasoned_draft_domain_owner_and_legacy_delegation() -> None:
    indicator_catalog = json.loads(
        (
            REPO_ROOT / "research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json"
        ).read_text(encoding="utf-8")
    )
    availability_catalog = json.loads(
        (
            REPO_ROOT
            / "research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
        ).read_text(encoding="utf-8")
    )
    template = json.loads(
        (REPO_ROOT / "research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json").read_text(
            encoding="utf-8"
        )
    )
    draft = {
        "summary": "donchian breakout",
        "causal_rationale": "breakout momentum",
        "falsifiable_prediction": "positive OOS expectancy",
        "symbols": ["BTCUSDT"],
        "timeframe": "15m",
        "features": ["donchian", "ohlcv"],
        "entry_concept": "break channel",
        "exit_concept": "opposite channel",
        "parameter_bounds": [{"name": "lookback", "minimum": 10, "maximum": 100}],
        "stop_conditions": ["stop on OOS failure"],
    }
    source = {
        "source_type": "manual_idea",
        "source_refs": ["project://indicator-catalog"],
        "prepared_by": "CPW domain test",
        "source_constraints": ["bounded"],
        "unresolved_claims": ["human review required"],
        "review_notes": ["not approval"],
        "lineage_ref_path": None,
        "lineage_ref_hash": "sha256:reasoned-draft-input",
    }
    result = formalize_reasoned_strategy_draft(
        idea="BTCUSDT price donchian breakout momentum",
        symbol="BTCUSDT",
        timeframe="15m",
        constraints=[],
        reasoned_draft=draft,
        indicator_catalog=indicator_catalog,
        availability_catalog=availability_catalog,
        strategy_spec_template=template,
        run_id="123456789abc",
        source_context=source,
    )
    assert result["status"] == "accepted"
    assert result["research_object"]["parameter_bounds"] == [
        {"name": "channel_lookback_bars", "minimum": 20.0, "maximum": 55.0}
    ]
    assert len(result["draft_strategy_specs"]) == 1
    assert result["draft_strategy_specs"][0]["lineage"]["parent_refs"][0] == {
        "ref_type": "concept",
        "ref_id": "IDEA-123456789ABC",
        "ref_path": None,
        "ref_hash": "sha256:reasoned-draft-input",
    }
    with pytest.raises(ValueError, match="bounded to BTCUSDT"):
        formalize_reasoned_strategy_draft(
            idea="x",
            symbol="ETHUSDT",
            timeframe="15m",
            constraints=[],
            reasoned_draft=draft,
            indicator_catalog=indicator_catalog,
            availability_catalog=availability_catalog,
            strategy_spec_template=template,
            run_id="123456789abc",
            source_context=source,
        )
    agent_source = (REPO_ROOT / "tools/research_agents/idea_formalizer_agent.py").read_text(
        encoding="utf-8"
    )
    assert "domain_result = formalize_reasoned_strategy_draft(" in agent_source


def test_legacy_family_compatibility_methods_delegate_to_domain(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, object]] = []

    def family_id(draft: Mapping[str, object]) -> str:
        calls.append(("family", draft))
        return "domain-owned-family"

    def funding_body(spec: dict[str, object], *, exit_mode: str) -> None:
        calls.append(("funding", (spec, exit_mode)))

    def donchian_body(spec: dict[str, object]) -> None:
        calls.append(("donchian", spec))

    monkeypatch.setattr(domain_formalization, "_draft_family_id", family_id)
    monkeypatch.setattr(domain_formalization, "_apply_funding_strategy_body", funding_body)
    monkeypatch.setattr(domain_formalization, "_apply_donchian_strategy_body", donchian_body)

    draft: dict[str, object] = {"features": ["funding_rate"]}
    funding_spec: dict[str, object] = {}
    donchian_spec: dict[str, object] = {}
    assert IdeaFormalizerAgent._draft_family_id(draft) == "domain-owned-family"
    IdeaFormalizerAgent._apply_funding_strategy_body(funding_spec, exit_mode="fixed_max_hold_only")
    IdeaFormalizerAgent._apply_donchian_strategy_body(donchian_spec)

    assert calls == [
        ("family", draft),
        ("funding", (funding_spec, "fixed_max_hold_only")),
        ("donchian", donchian_spec),
    ]


def test_legacy_wrapper_contains_only_thin_family_delegates() -> None:
    source = (REPO_ROOT / "tools/research_agents/idea_formalizer_agent.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    agent_class = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "IdeaFormalizerAgent"
    )
    methods = {
        node.name: node
        for node in agent_class.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    removed_support_helpers = {
        "_funding_percentile_operand",
        "_parameter_operand",
        "_constant_operand",
        "_funding_condition",
        "_funding_parameter",
        "_indicator_operand",
        "_close_operand",
        "_donchian_condition",
    }
    assert removed_support_helpers.isdisjoint(methods)

    for method_name, domain_name in (
        ("_draft_family_id", "_draft_family_id"),
        ("_apply_funding_strategy_body", "_apply_funding_strategy_body"),
        ("_apply_donchian_strategy_body", "_apply_donchian_strategy_body"),
    ):
        body = methods[method_name].body
        assert len(body) == 1
        statement = body[0]
        expression = statement.value if isinstance(statement, (ast.Expr, ast.Return)) else None
        assert isinstance(expression, ast.Call)
        assert isinstance(expression.func, ast.Attribute)
        assert isinstance(expression.func.value, ast.Name)
        assert expression.func.value.id == "domain_formalization"
        assert expression.func.attr == domain_name


def test_preregistration_hash_requirement_and_approval_are_deterministic() -> None:
    packet = _packet()
    assert packet == _packet()
    requirement = build_approval_requirement(packet)
    assert validate_bound_requirement(requirement, packet) == ()
    approval = _approval(packet)
    assert validate_prereg_approval(approval, packet, requirement=requirement) == ()


@pytest.mark.parametrize(
    "field,value,error",
    [
        ("preregistration_packet_sha256", "sha256:wrong", "approval_hash_mismatch"),
        ("approved_by", "operator", "approval_actor_not_karl"),
        ("approval_scope", "canonical", "approval_scope_not_noncanonical_offline_only"),
        ("approval_statement", "approve", "approval_statement_not_exact"),
        ("schema_version", "other", "approval_schema_version_mismatch"),
        ("approval_timestamp_utc", "", "approval_timestamp_missing"),
        ("authorizes_canonical_write", True, "approval_too_broad:authorizes_canonical_write"),
    ],
)
def test_preregistration_approval_fails_closed(field: str, value: object, error: str) -> None:
    packet = _packet()
    approval = _approval(packet)
    approval[field] = value
    assert error in validate_prereg_approval(approval, packet)


def test_preregistration_packet_and_requirement_tampering_fail_closed() -> None:
    packet = _packet()
    requirement = build_approval_requirement(packet)
    packet["request_id"] = "REQ-TAMPERED"
    errors = validate_bound_requirement(requirement, packet)
    assert "preregistration_packet_hash_mismatch" in errors
    assert "approval_requirement_request_id_mismatch" in errors


def test_gate_marker_uses_locked_non_authority_assertions() -> None:
    packet = _packet()
    requirement = build_approval_requirement(packet)
    operator_fields = _approval(packet)
    marker = build_approval_marker(
        action_id="GATE-1",
        requirement=requirement,
        packet=packet,
        operator_fields=operator_fields,
    )
    assert marker["approval_scope"] == PREREG_APPROVAL_SCOPE
    assert marker["non_authority_assertions"] == dict(PREREG_NON_AUTHORITY_ASSERTIONS)
    assert marker["authorizes_crossing"] is False
    assert marker["authorizes_promotion_or_readiness"] is False


def test_scoped_lab_consumers_delegate_to_research_domain() -> None:
    assert orchestrator.build_preregistration_packet is build_preregistration_packet
    assert orchestrator.validate_prereg_approval is validate_prereg_approval
    assert adapters.validate_prereg_approval is validate_prereg_approval
    assert gate_actions.validate_bound_requirement is validate_bound_requirement
    assert gate_actions.build_approval_marker is build_approval_marker


def test_declared_trial_and_denominator_validation_is_exact() -> None:
    trials = [
        {"strategy_family": "family", "variant_id": "V1", "trial_id": "T1", "params": {}},
        {"strategy_family": "family", "variant_id": "V2", "trial_id": "T2", "params": {}},
    ]
    validate_declared_trials(trials)
    ledger = [
        {"trial_id": "T1", "trial_status": "completed"},
        {"trial_id": "T2", "trial_status": "failed"},
    ]
    validate_trial_denominator(ledger, {"T1", "T2"})
    with pytest.raises(ValueError, match="preserve every declared trial"):
        validate_trial_denominator(ledger[:1], {"T1", "T2"})
    with pytest.raises(ValueError, match="preserve every declared trial"):
        validate_trial_denominator([*ledger, ledger[0]], {"T1", "T2"})
    with pytest.raises(ValueError, match="unsupported statuses"):
        validate_trial_denominator([{"trial_id": "T1", "trial_status": "winner"}], {"T1"})
    assert TRIAL_STATUSES == ("completed", "failed", "invalid", "pruned", "blocked")


def test_bridge_ledger_is_deterministic_and_validates_full_denominator() -> None:
    manifest = {
        "variant_assignments": [
            {"variant_id": "V2", "parameter_values": {"lookback": 20}},
            {"variant_id": "V1", "parameter_values": {"lookback": 10}},
        ]
    }
    kwargs = {
        "run_id": "RUN-1",
        "runner_invocation_id": "INV-1",
        "formalizer_run_id": "FORM-1",
        "formalizer_path": "scratch/formalized.json",
        "approval_scope": "noncanonical",
        "input_paths": {"strategy_spec": "scratch/spec.json"},
        "manifest": manifest,
        "runner_result": None,
        "runner_artifact_path": None,
        "blockers": ["fixture unavailable"],
        "funding_cost_mode": "off",
        "timestamp_utc": "2026-07-08T00:00:00Z",
    }
    rows = build_bridge_ledger_rows(**kwargs)
    assert rows == build_bridge_ledger_rows(**kwargs)
    assert [row["variant_id"] for row in rows] == ["V1", "V2"]
    validate_variant_denominator(rows, manifest)
    with pytest.raises(ValueError, match="declared variant"):
        validate_variant_denominator(rows[:1], manifest)


def test_result_population_comparison_preserves_exact_field_set() -> None:
    result = {
        "result_population": {
            "variant_result_rows": [
                {"variant_id": "V1", "outcome_category": "successful", "metrics": {"return": 1}}
            ],
            "result_population_identity_hash": "sha256:same",
        },
        "outcome_category_counts": {"successful": 1},
        "committed_denominator": 1,
    }
    comparison = compare_result_populations(result, copy.deepcopy(result))
    assert comparison == {
        "passed": True,
        "comparisons": {
            "trial_count": True,
            "variant_ids": True,
            "outcomes": True,
            "core_metrics": True,
            "status_counts": True,
            "committed_denominator": True,
            "result_identity": True,
        },
    }
    changed = copy.deepcopy(result)
    changed["result_population"]["variant_result_rows"][0]["metrics"] = {"return": 2}
    assert compare_result_populations(result, changed)["passed"] is False


def test_domain_functions_expose_no_authority_or_side_effect_fields(tmp_path: Path) -> None:
    before = list(tmp_path.iterdir())
    packet = _packet()
    build_approval_requirement(packet)
    build_approval_template(packet, approval_timestamp_utc="2026-07-08T00:00:00Z")
    assert list(tmp_path.iterdir()) == before
    public_names = {
        name
        for name in (
            "rank_candidates",
            "promote_candidate",
            "write_canonical",
            "mark_ready",
        )
        if hasattr(__import__("tools.research_domain", fromlist=[name]), name)
    }
    assert public_names == set()
