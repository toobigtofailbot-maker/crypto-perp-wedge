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
from tools.research_domain.feature_data import (
    CANONICAL_KLINE_TAKER_DERIVATION_VERSION,
    CANONICAL_KLINE_TAKER_SOURCE_CLASS,
    D4_TAKER_DERIVATION_VERSION,
    D4_TAKER_FEATURE_DEFINITIONS,
    D4_TAKER_PARENT_FIELDS,
    D4_TAKER_SOURCE_CLASS,
    FeatureDataContractError,
    build_composite_research_data_identity,
    build_feature_table_identity,
    build_source_set_identity,
    validate_feature_table_contract,
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
                "source_class": "CANONICAL_D4_KLINE_DERIVATION",
                "coverage_class": "FULL_HISTORY_PUBLIC_ARCHIVE",
                "canonical_full_history_allowed": "conditional",
                "compiler_visible": True,
                "history_limitation": "requires D4-native materialization",
                "conditions": ["canonical D4 parent"],
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


@pytest.mark.parametrize(
    "feature",
    ["taker_buy_volume", "taker_sell_volume", "taker_buy_sell_ratio"],
)
def test_all_taker_fields_prefer_canonical_d4_source(feature: str) -> None:
    catalog = {
        "entries": [
            {
                "feature_name": name,
                "source_class": source,
                "coverage_class": coverage,
                "canonical_full_history_allowed": allowed,
                "compiler_visible": True,
                "requires_vendor_or_captured_data": source == "PUBLIC_REST_TAKER_RATIO",
                "history_limitation": source,
                "conditions": ["canonical D4 parent"] if "D4" in source else [],
            }
            for name in ("taker_buy_volume", "taker_sell_volume", "taker_buy_sell_ratio")
            for source, coverage, allowed in (
                ("PUBLIC_REST_TAKER_RATIO", "RECENT_ONLY_PUBLIC_REST", "no"),
                ("CANONICAL_D4_KLINE_DERIVATION", "FULL_HISTORY_PUBLIC_ARCHIVE", "conditional"),
            )
        ]
    }
    assessment = assess_capabilities(feature, {"entries": []}, catalog)
    item = next(row for row in assessment["feature_assessments"] if row["feature"] == feature)
    assert item["source_class"] == "CANONICAL_D4_KLINE_DERIVATION"
    assert item["historical_testability"] == "available_when_source_bars_exist"


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


def _feature_contract() -> dict[str, object]:
    contract: dict[str, object] = {
        "schema_version": "cpw_research_feature_table_v1",
        "family_id": "fixture_family_v1",
        "market_identity": {"venue": "Binance", "market_type": "USD-M perpetual", "symbol": "BTCUSDT"},
        "timeframe": "15m",
        "feature_names": ["taker_buy_volume"],
        "source_class": "PUBLIC_DIAGNOSTIC_FIXTURE",
        "availability_assertions": [{"feature_name": "taker_buy_volume", "source_class": "PUBLIC_DIAGNOSTIC_FIXTURE", "condition_assertions": ["fixture complete"]}],
        "source_set_identity": "sha256:" + "1" * 64,
        "output_identity": {"format": "CSV UTF-8 LF", "sha256": "2" * 64, "row_count": 2, "columns": ["timestamp", "taker_buy_volume"]},
        "coverage": {"start_utc_inclusive": "2024-01-01T00:00:00.000Z", "end_utc_exclusive": "2024-01-01T00:30:00.000Z", "expected_row_count": 2, "observed_row_count": 2, "complete": True},
        "causality": {"timestamp_semantics": "UTC bar open", "feature_available_at_semantics": "exclusive bar close", "completed_bar_only": True, "future_events_can_change_prior_completed_bars": False},
        "quality_policy": {"fill": "forbidden", "forward_fill": "forbidden", "backfill": "forbidden", "interpolation": "forbidden", "timestamp_tolerance": "forbidden", "missing_row": "fail_closed", "duplicate_join_key": "fail_closed"},
        "feature_table_identity": "",
        "non_authority": {"authorizes_execution": False, "authorizes_result_population": False, "authorizes_candidate": False, "authorizes_promotion": False, "authorizes_runtime_paper_live": False, "authorizes_oms_risk_reconciliation": False},
    }
    contract["feature_table_identity"] = build_feature_table_identity(contract)
    return contract


def test_feature_source_set_identity_is_order_and_path_independent() -> None:
    first = {"logical_filename": "b.zip", "sha256": "b" * 64, "size_bytes": 2, "parsed_row_count": 3, "source_type": "aggTrades", "path": "C:/one/b.zip"}
    second = {"logical_filename": "a.zip", "sha256": "a" * 64, "size_bytes": 1, "parsed_row_count": 2, "source_type": "aggTrades", "path": "D:/two/a.zip"}
    identity = build_source_set_identity([first, second])
    assert identity == build_source_set_identity([{**second, "path": "X:/elsewhere/a.zip"}, {**first, "path": "Y:/elsewhere/b.zip"}])
    assert identity != build_source_set_identity([{**first, "sha256": "c" * 64}, second])


def test_feature_table_and_composite_identities_are_deterministic_and_material() -> None:
    contract = _feature_contract()
    assert build_feature_table_identity(contract) == contract["feature_table_identity"]
    changed = copy.deepcopy(contract)
    changed["coverage"]["end_utc_exclusive"] = "2024-01-01T00:45:00.000Z"
    assert build_feature_table_identity(changed) != contract["feature_table_identity"]
    kwargs = dict(
        base_data_slice_identity="base:sha256:" + "3" * 64,
        base_normalized_sha256="4" * 64,
        feature_table_identity=str(contract["feature_table_identity"]),
        feature_output_sha256="2" * 64,
        market_identity={"venue": "Binance", "market_type": "USD-M perpetual", "symbol": "BTCUSDT"},
        timeframe="15m",
        coverage_start_utc_inclusive="2024-01-01T00:00:00.000Z",
        coverage_end_utc_exclusive="2024-01-01T00:30:00.000Z",
        joined_row_count=2,
        selected_feature_names=["taker_buy_volume"],
    )
    identity = build_composite_research_data_identity(**kwargs)
    assert identity == build_composite_research_data_identity(**kwargs)
    assert identity != build_composite_research_data_identity(**{**kwargs, "base_data_slice_identity": "other"})
    assert identity != build_composite_research_data_identity(**{**kwargs, "feature_output_sha256": "5" * 64})


def test_feature_contract_rejects_unknown_semantics_and_authority_expansion() -> None:
    contract = _feature_contract()
    validate_feature_table_contract(contract)
    unknown = copy.deepcopy(contract)
    unknown["unknown"] = True
    with pytest.raises(FeatureDataContractError, match="unknown"):
        validate_feature_table_contract(unknown)
    authority = copy.deepcopy(contract)
    authority["non_authority"]["authorizes_execution"] = True
    authority["feature_table_identity"] = build_feature_table_identity(authority)
    with pytest.raises(FeatureDataContractError, match="authority"):
        validate_feature_table_contract(authority)


def _canonical_taker_contract(timeframe: str, *, legacy: bool = False) -> dict[str, object]:
    contract = _feature_contract()
    source_class = D4_TAKER_SOURCE_CLASS if legacy else CANONICAL_KLINE_TAKER_SOURCE_CLASS
    hash_label = "identity_sha256" if timeframe == "1d" else "sha256"
    contract.update(
        {
            "timeframe": timeframe,
            "feature_names": [item["feature_name"] for item in D4_TAKER_FEATURE_DEFINITIONS],
            "source_class": source_class,
            "availability_assertions": [
                {"feature_name": item["feature_name"], "source_class": source_class, "condition_assertions": ["bound canonical parent"]}
                for item in D4_TAKER_FEATURE_DEFINITIONS
            ],
            "parent_identity": {
                "data_slice_identity": f"binance_usdtm_btcusdt_ohlcv_{timeframe}:{hash_label}:" + "3" * 64,
                "normalized_sha256": "4" * 64,
                "row_count": 2,
                "coverage_start_utc_inclusive": "2024-01-01T00:00:00.000Z",
                "coverage_end_utc_exclusive": "2024-01-01T00:30:00.000Z",
            },
            "derivation": {
                "derivation_version": D4_TAKER_DERIVATION_VERSION if legacy else CANONICAL_KLINE_TAKER_DERIVATION_VERSION,
                "parent_fields": list(D4_TAKER_PARENT_FIELDS),
                "features": [dict(item) for item in D4_TAKER_FEATURE_DEFINITIONS],
            },
            "output_identity": {
                "format": "CSV UTF-8 LF", "sha256": "2" * 64, "row_count": 2,
                "columns": ["timestamp", *[item["feature_name"] for item in D4_TAKER_FEATURE_DEFINITIONS]],
            },
        }
    )
    contract["feature_table_identity"] = build_feature_table_identity(contract)
    return contract


@pytest.mark.parametrize("timeframe", ["30m", "1h", "4h", "1d"])
def test_generic_canonical_taker_contract_accepts_exact_identity_family(timeframe: str) -> None:
    validate_feature_table_contract(_canonical_taker_contract(timeframe))


def test_canonical_taker_contract_rejects_source_timeframe_and_identity_mismatch() -> None:
    with pytest.raises(FeatureDataContractError, match="only for"):
        validate_feature_table_contract(_canonical_taker_contract("15m"))
    with pytest.raises(FeatureDataContractError, match="only for"):
        validate_feature_table_contract(_canonical_taker_contract("30m", legacy=True))
    mismatch = _canonical_taker_contract("30m")
    mismatch["parent_identity"]["data_slice_identity"] = "binance_usdtm_btcusdt_ohlcv_1h:sha256:" + "3" * 64
    mismatch["feature_table_identity"] = build_feature_table_identity(mismatch)
    with pytest.raises(FeatureDataContractError, match="identity family"):
        validate_feature_table_contract(mismatch)


# SYNTHETIC_FIXTURE: bounded adapter mechanics, never a model run or science.
def _sma_trend_inputs():
    def load(path):
        return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))

    return {
        "idea": "BTCUSDT 4h price SMA trend persistence",
        "symbol": "BTCUSDT",
        "timeframe": "4h",
        "constraints": [],
        "reasoned_draft": {
            "summary": "SYNTHETIC_FIXTURE: price trend test, not actual research",
            "causal_rationale": "Persistence is an unproven possibility.",
            "falsifiable_prediction": "A future held-out test may reject persistence.",
            "symbols": ["BTCUSDT"],
            "timeframe": "4h",
            "features": ["sma", "ohlcv"],
            "entry_concept": "Completed close above/below trailing SMA(50); next open only.",
            "exit_concept": "Persist until relationship changes; flat warmup or invalid input.",
            "parameter_bounds": [{"name": "lookback", "minimum": 50.0, "maximum": 50.0}],
            "stop_conditions": [
                "No execution; uncertain costs, funding, holdout and prior history."
            ],
        },
        "indicator_catalog": load(
            "research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json"
        ),
        "availability_catalog": load(
            "research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
        ),
        "strategy_spec_template": load(
            "research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json"
        ),
        "run_id": "123456789abc",
        "source_context": {
            "source_type": "manual_idea",
            "source_refs": ["project://indicator-catalog"],
            "prepared_by": "SYNTHETIC_FIXTURE",
            "source_constraints": ["scratch only"],
            "unresolved_claims": ["human review required"],
            "review_notes": ["not approval"],
            "lineage_ref_path": None,
            "lineage_ref_hash": "sha256:synthetic-input",
        },
    }


def test_sma_trend_body_schema_lineage_and_no_template_leakage():
    from jsonschema import Draft7Validator

    inputs = _sma_trend_inputs()
    before = copy.deepcopy(inputs)
    result = formalize_reasoned_strategy_draft(**inputs)
    assert result == formalize_reasoned_strategy_draft(**inputs)
    assert inputs == before
    assert result["status"] == "accepted"
    assert result["adapter_metadata"]["family_id"] == "price_sma_trend_persistence_v1"
    assert len(result["draft_strategy_specs"]) == 1
    spec = result["draft_strategy_specs"][0]
    schema = json.loads((REPO_ROOT / "research/schemas/strategy_spec.schema.json").read_text())
    Draft7Validator(schema).validate(spec)
    assert spec["strategy_spec_id"] == "STRAT-SPEC-9896"
    assert spec["status"] == "draft"
    assert spec["review"]["reviewer"] is None
    assert spec["review"]["approval_scope"] == "none"
    assert all(spec["review"]["non_authority_acknowledgement"].values())
    assert spec["hash_pinning"]["hash_status"] == "not_computed"
    assert spec["hash_pinning"]["canonical_spec_hash"] is None
    assert spec["pre_registration_support"] == {
        "intended_for_variant_manifest": False,
        "variant_manifest_ref": None,
        "frozen_snapshot_ref": None,
    }
    assert spec["lineage"]["parent_refs"][0]["ref_hash"] == "sha256:synthetic-input"
    assert spec["provenance"]["source_refs"] == inputs["source_context"]["source_refs"]
    assert spec["entry_logic"]["direction"] == "both"
    assert "entry_controls" not in spec["entry_logic"]
    assert spec["timeframe_and_data"]["primary_timeframe"] == "4h"
    assert {ref["field"] for ref in spec["timeframe_and_data"]["host_data_refs"]} == {
        "open",
        "high",
        "low",
        "close",
        "volume",
        "sma",
    }
    assert spec["filters"] == {"groups": [], "none_declared": True}
    assert spec["free_parameters"]["parameters"] == []
    assert spec["free_parameters"]["no_free_parameters_declared"] is True
    assert spec["exit_logic"]["max_holding_period"] == {"enabled": False, "bars": None}
    assert spec["risk_model"]["stop_distance"] is spec["risk_model"]["target_distance"] is None
    for name, operators in [("entry_logic", ["gt", "lt"]), ("exit_logic", ["lte", "gte"])]:
        groups = spec[name]["groups"]
        assert [g["side"] for g in groups] == ["long", "short"]
        for group, operator in zip(groups, operators, strict=True):
            assert group["logic"] == "all" and group["subgroups"] == []
            (condition,) = group["conditions"]
            assert condition["operator"] == operator
            assert condition["left_operand"] == domain_formalization._close_operand()
            assert condition["right_operand"] == {
                "operand_type": "indicator_ref",
                "ref": "sma",
                "field": "value",
                "timeframe": None,
                "lookback": {"bars": 50},
            }
    claims = " ".join(spec["provenance"]["unresolved_claims"])
    assert all(word in claims for word in ["bytes", "warmup", "NaN", "flip", "15m", "next"])
    assert "human review required" in claims


@pytest.mark.parametrize(
    "field,value",
    [
        ("timeframe", "1h"),
        ("symbols", ["ETHUSDT"]),
        ("features", ["sma"]),
        ("features", ["sma", "ohlcv", "ema"]),
        ("entry_concept", "SMA trend"),
        ("entry_concept", "Long below SMA(50), short above; mean reversion."),
        ("entry_concept", "Completed close above/below trailing SMA(20); next open only."),
        (
            "entry_concept",
            "Completed close above/below trailing SMA(50); next open only. Add ATR stop.",
        ),
        ("exit_concept", "Take profit at 2R or stop loss at 1%."),
        ("exit_concept", "Persist forever."),
        ("summary", "SMA mean reversion"),
        ("summary", "Buy below SMA and sell above."),
        ("parameter_bounds", []),
        ("parameter_bounds", [{"name": "lookback", "minimum": 20, "maximum": 50}]),
        ("parameter_bounds", [{"name": "lookback", "minimum": True, "maximum": 50}]),
        ("parameter_bounds", [{"name": "other", "minimum": 50, "maximum": 50}]),
    ],
)
def test_sma_trend_unsupported_drafts_produce_no_spec(field, value):
    inputs = _sma_trend_inputs()
    inputs["reasoned_draft"][field] = value
    if field == "features":
        inputs["idea"] += " ema"
    result = formalize_reasoned_strategy_draft(**inputs)
    assert result["draft_strategy_specs"] == []
    assert result["draft_strategy_spec"]["produced"] is False


@pytest.mark.parametrize(
    "idea,constraints",
    [
        ("BTCUSDT 4h price SMA trend persistence with ema", []),
        ("BTCUSDT 4h price SMA(20) trend persistence", []),
        ("BTCUSDT 4h price SMA trend persistence with a stop loss", []),
        ("BTCUSDT 4h price SMA trend persistence", ["Add a trailing stop"]),
    ],
)
def test_sma_trend_does_not_drop_operator_mechanics(idea, constraints):
    inputs = _sma_trend_inputs()
    inputs.update(idea=idea, constraints=constraints)
    assert formalize_reasoned_strategy_draft(**inputs)["draft_strategy_specs"] == []


def test_sma_trend_missing_indicator_catalog_is_blocked():
    inputs = _sma_trend_inputs()
    inputs["indicator_catalog"] = {"entries": []}
    result = formalize_reasoned_strategy_draft(**inputs)
    assert result["draft_strategy_specs"] == []


def test_sma_trend_compiler_observed_semantics():
    import pandas as pd

    from tools.research_runner.spec_signal_compiler import compile_signal

    (spec,) = formalize_reasoned_strategy_draft(**_sma_trend_inputs())["draft_strategy_specs"]
    close = [100.0] * 50 + [110.0, 110.0, 90.0, 90.0, 120.0, 120.0]
    index = pd.date_range("2026-01-01", periods=len(close), freq="4h", tz="UTC")
    bars = pd.DataFrame(
        {
            "open": close,
            "high": [x + 1 for x in close],
            "low": [x - 1 for x in close],
            "close": close,
            "volume": 1000.0,
        },
        index=index,
    )
    before = bars.copy(deep=True)
    signal = compile_signal(spec, {"parameter_values": {}}, bars)
    assert signal.tolist() == [0.0] * 50 + [1.0, 1.0, 0.0, -1.0, 0.0, 1.0]
    pd.testing.assert_frame_equal(bars, before)
    pd.testing.assert_series_equal(signal, compile_signal(spec, {}, bars))
    altered = bars.copy()
    altered.loc[index[-1], ["open", "high", "low", "close"]] = [50, 51, 49, 50]
    pd.testing.assert_series_equal(signal.iloc[:-1], compile_signal(spec, {}, altered).iloc[:-1])
    # Equality closes an existing side; the compiler never flips on the exit bar.
    equal = bars.iloc[:52].copy()
    equal.iloc[-1, equal.columns.get_loc("close")] = (49 * 100.0 + 110.0) / 50
    assert compile_signal(spec, {}, equal).iloc[-1] == 0.0
    # Existing compiler comparisons are false for NaN: no new entry, but a held side persists.
    invalid = bars.copy()
    invalid.loc[index[51], "close"] = float("nan")
    assert compile_signal(spec, {}, invalid).iloc[50:54].tolist() == [1.0] * 4
    invalid.loc[index[49], "close"] = float("nan")
    assert compile_signal(spec, {}, invalid).eq(0.0).all()


@pytest.mark.parametrize(
    "constraints", [[], ["Noncanonical supervised admission only; no scientific execution."]]
)
def test_sma_trend_explicit_sides_and_native_admission_constraint(constraints):
    inputs = _sma_trend_inputs()
    inputs["constraints"] = constraints
    inputs["reasoned_draft"].update(
        entry_concept="Long when completed close > trailing SMA(50); short when completed close < trailing SMA(50); next open only.",
        exit_concept="Long exits on completed close <= SMA(50); short exits on completed close >= SMA(50).",
    )
    assert len(formalize_reasoned_strategy_draft(**inputs)["draft_strategy_specs"]) == 1
