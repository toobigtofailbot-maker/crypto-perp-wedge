from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pytest

from tools.agent_sandbox import BlockedActionError, MemoryAuditSink, ToolAction, ToolContext
from tools.agent_sandbox.permissions import (
    BUILD_FIXTURE_CANONICAL_CROSSING,
    ROLE_PERMISSIONS,
)
import tools.candidate_lifecycle.canonical_crossing_build as crossing_build
from tools.candidate_lifecycle.canonical_crossing_build import (
    CanonicalCrossingBuildConfig,
    CanonicalCrossingBuildError,
    CanonicalCrossingFixtureBuilder,
    ROLE,
    WP_ID,
)
from tools.registry.validate_candidate_registry import validate_candidate_registries


FIXED_TIME = datetime(2026, 6, 23, 0, 0, 0, tzinfo=timezone.utc)


def _json_text(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _write_json(root: Path, relative: str, payload: dict) -> str:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json_text(payload), encoding="utf-8", newline="\n")
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_path(root: Path, relative: str) -> str:
    return "sha256:" + hashlib.sha256((root / relative).read_bytes()).hexdigest()


def _base_registry() -> dict:
    non_authority = {
        "not_candidate_approval": True,
        "not_paper_live_authority": True,
        "not_runtime_authority": True,
        "not_promotion_authority": True,
        "not_trading_recommendation": True,
        "not_broker_exchange_authority": True,
        "not_capital_authority": True,
        "notes": "Fixture-only registry creates no authority.",
    }
    return {
        "schema_version": "candidate_lifecycle_registry.v1",
        "registry_id": "CANDIDATE-REGISTRY-FIXTURE-9001",
        "registry_status": "test_fixture",
        "non_authority_declaration": copy.deepcopy(non_authority),
        "transition_rules": {
            "allowed_edges": [
                {
                    "from_status": "proposed",
                    "to_status": "validated_research",
                    "required_gate": "future_human_review_gate",
                    "notes": "Separate future gate required.",
                }
            ],
            "forbidden_principles": [
                "Fixture crossing creates no promotion, readiness, paper/live, runtime, or trading authority."
            ],
        },
        "candidates": [
            {
                "candidate_id": "CANDIDATE-FIXTURE-9001",
                "candidate_status": "proposed",
                "display_name": "Fixture canonical crossing candidate",
                "strategy_family": "fixture-crossing",
                "description": "Fake candidate used only to prove fixture crossing mechanics.",
                "market": "crypto_perpetual",
                "instrument": "BTCUSDT",
                "primary_timeframe": "15m",
                "allowed_confirmation_timeframes": [],
                "source_refs": {
                    "strategy_spec_refs": [],
                    "variant_manifest_refs": [],
                    "sweep_plan_refs": [],
                    "source_design_refs": [],
                    "approval_note_refs": [],
                },
                "evidence_links": [],
                "lifecycle_event_refs": [],
                "review_metadata": {
                    "created_at": "2026-06-23T00:00:00Z",
                    "created_by": "fixture",
                    "review_owner": "fixture",
                    "gate_owner": "fixture",
                    "review_due_at": None,
                    "decision_notes": "Fixture only.",
                    "unresolved_questions": ["first real crossing remains gated"],
                },
                "blocking_reason": None,
                "required_next_review": "fixture only",
                "non_authority_declaration": copy.deepcopy(non_authority),
            }
        ],
        "append_only_ledger": [],
        "validation_summary": {
            "fixture_only": True,
            "real_candidate_registered": False,
            "lifecycle_engine_implemented": False,
            "paper_live_authority_created": False,
            "runtime_authority_created": False,
            "capital_authority_created": False,
            "notes": "Pre-crossing fake registry copy.",
        },
    }


def _make_fixture_tree(root: Path) -> dict[str, str]:
    prefix = "tests/fixtures/candidate_lifecycle_crossing"
    formalizer_path = f"{prefix}/formalized_idea.json"
    bridge_path = f"{prefix}/human_review_packet.json"
    robustness_path = f"{prefix}/robustness_diagnostics.json"
    ledger_path = f"{prefix}/denominator_ledger.json"
    registry_path = f"{prefix}/empty_fake_registry.candidate_lifecycle_registry.json"
    _write_json(root, formalizer_path, {"schema_version": "fixture_formalizer", "run_id": "FORM-FIXTURE"})
    _write_json(root, bridge_path, {"schema_version": "fixture_bridge", "run_id": "BRIDGE-FIXTURE"})
    _write_json(root, robustness_path, {"schema_version": "fixture_robustness", "run_id": "ROBUST-FIXTURE"})
    _write_json(
        root,
        ledger_path,
        {
            "schema_version": "fixture_ledger",
            "declared_trial_count": 5,
            "trial_status_counts": {
                "completed": 2,
                "failed": 1,
                "invalid": 1,
                "pruned": 1,
                "blocked": 0,
            },
        },
    )
    packet_path = f"{prefix}/candidate_review_packet.json"
    packet = {
        "schema_version": "candidate_review_packet_v1",
        "source_formalizer": {
            "path": formalizer_path,
            "sha256": _hash_path(root, formalizer_path),
            "draft_strategy_spec_path": None,
            "draft_strategy_spec_sha256": None,
        },
        "source_bridge": {
            "review_packet_path": bridge_path,
            "review_packet_sha256": _hash_path(root, bridge_path),
            "runner_artifact_path": None,
            "runner_artifact_sha256": None,
        },
        "source_robustness": {
            "diagnostics_path": robustness_path,
            "diagnostics_sha256": _hash_path(root, robustness_path),
            "review_packet_path": None,
            "review_packet_sha256": None,
        },
        "operator_approval": {"path": None, "sha256": None},
        "data_and_funding_summary": {
            "data_availability_warnings": [
                "open_interest_recent_only_not_reconstructable_from_trades"
            ],
            "data_availability_blockers": [
                "no full-history public liquidation history available in packet evidence"
            ],
            "funding_mode": {"requested": "off", "effective": "off", "default_off": True},
            "funding_stress_status": {
                "status": "not_applicable_funding_mode_off",
                "performed": False,
                "skipped_reason": "funding mode off",
            },
        },
        "data_availability_coverage_classes": ["RECENT_ONLY_PUBLIC_REST"],
        "data_availability_constraint_classes": ["recent_only"],
        "data_availability_caveats": ["recent-only source remains a caveat"],
        "denominator_snapshot": {
            "ledger_path": ledger_path,
            "ledger_sha256": _hash_path(root, ledger_path),
            "counts": {
                "completed": 2,
                "failed": 1,
                "invalid": 1,
                "pruned": 1,
                "blocked": 0,
            },
            "declared_trial_count": 5,
            "all_source_rows_preserved": True,
            "row_disposition": [
                {"variant_id": "VAR-000001", "trial_status": "completed", "status_reason": "ok"},
                {"variant_id": "VAR-000002", "trial_status": "completed", "status_reason": "ok"},
                {"variant_id": "VAR-000003", "trial_status": "failed", "status_reason": "runner failed"},
                {"variant_id": "VAR-000004", "trial_status": "invalid", "status_reason": "invalid params"},
                {"variant_id": "VAR-000005", "trial_status": "pruned", "status_reason": "pruned"},
            ],
        },
        "robustness_summary": {
            "diagnostics_completed": ["denominator_integrity"],
            "diagnostics_skipped": [
                {"diagnostic": "oos_walkforward_status", "reason": "missing_fold_inputs"},
                {"diagnostic": "per_trade_status", "reason": "QUEUE_PER_TRADE_INSTRUMENTATION"},
                {"diagnostic": "funding_stress_status", "reason": "not_applicable_funding_mode_off"},
            ],
        },
        "missing_data_limitations": {
            "per_trade": {
                "status": "QUEUE_PER_TRADE_INSTRUMENTATION",
                "performed": False,
                "reason": "no per-trade rows",
                "fabricated_per_trade_data": False,
            },
            "oos_walkforward": {
                "status": "missing_fold_inputs",
                "performed": False,
                "reason": "no folds",
                "queued_follow_up": True,
            },
            "funding_stress": {
                "status": "not_applicable_funding_mode_off",
                "performed": False,
                "reason": "funding mode off",
            },
        },
        "non_authority_flags": [
            "not canonical",
            "not evidence",
            "not candidate authority",
            "not promotion authority",
            "not ranking authority",
            "not paper/live readiness",
            "not a trading signal",
            "human review required",
        ],
    }
    _write_json(root, packet_path, packet)
    approval_path = f"{prefix}/crossing_approval.json"
    approval = {
        "approval_id": "CROSSING-APPROVAL-FIXTURE-9001",
        "approved_by": "operator",
        "approval_timestamp_utc": "2026-06-23T00:00:00Z",
        "approval_scope": "fixture_only_canonical_crossing_build",
        "content_reviewed": True,
        "content_reviewed_hash": _hash_path(root, packet_path),
        "content_reviewed_at_utc": "2026-06-23T00:00:00Z",
        "canonical_crossing_allowed": True,
        "fixture_only": True,
        "source_candidate_review_packet_path": packet_path,
        "source_candidate_review_packet_hash": _hash_path(root, packet_path),
        "source_formalizer_artifact_path": formalizer_path,
        "source_formalizer_artifact_hash": _hash_path(root, formalizer_path),
        "source_bridge_artifact_path": bridge_path,
        "source_bridge_artifact_hash": _hash_path(root, bridge_path),
        "source_robustness_artifact_path": robustness_path,
        "source_robustness_artifact_hash": _hash_path(root, robustness_path),
        "source_denominator_ledger_path": ledger_path,
        "source_denominator_ledger_hash": _hash_path(root, ledger_path),
        "append_only": True,
        "no_promotion": True,
        "no_readiness": True,
        "operator_acknowledges_missing_diagnostics": True,
        "operator_acknowledges_data_availability_warnings": True,
        "operator_acknowledges_funding_mode": True,
    }
    _write_json(root, approval_path, approval)
    _write_json(root, registry_path, _base_registry())
    return {
        "packet": packet_path,
        "approval": approval_path,
        "registry": registry_path,
    }


def _make_builder(root: Path) -> tuple[CanonicalCrossingFixtureBuilder, MemoryAuditSink]:
    sink = MemoryAuditSink()
    context = ToolContext(wp_id=WP_ID, role=ROLE, audit_sink=sink, clock=lambda: FIXED_TIME)
    builder = CanonicalCrossingFixtureBuilder(
        config=CanonicalCrossingBuildConfig(),
        tool_context=context,
        repo_root=root,
    )
    return builder, sink


def _run_valid(root: Path) -> tuple[dict, CanonicalCrossingFixtureBuilder, MemoryAuditSink]:
    paths = _make_fixture_tree(root)
    builder, sink = _make_builder(root)
    result = builder.run(
        candidate_review_packet_path=paths["packet"],
        crossing_approval_path=paths["approval"],
        fake_registry_input_path=paths["registry"],
    )
    return result, builder, sink


def _rewrite_packet_and_approval(root: Path, paths: dict[str, str], packet: dict, approval: dict) -> None:
    _write_json(root, paths["packet"], packet)
    approval["content_reviewed_hash"] = _hash_path(root, paths["packet"])
    approval["source_candidate_review_packet_hash"] = _hash_path(root, paths["packet"])
    _write_json(root, paths["approval"], approval)


def _assert_rejected_without_crossing(root: Path, paths: dict[str, str], sink: MemoryAuditSink) -> dict:
    output_dir = root / "scratch" / WP_ID / "outputs" / "fixture-crossing-run"
    result_packet = json.loads((output_dir / "crossing_result_packet.json").read_text(encoding="utf-8"))
    audit_payload = json.loads((output_dir / "crossing_audit_log.json").read_text(encoding="utf-8"))

    assert result_packet["status"] == "rejected"
    assert result_packet["reason_code"] == "reject_by_construction"
    assert result_packet["candidate_lifecycle_written"] is False
    assert result_packet["canonical_crossing_written"] is False
    assert result_packet["promotion_or_readiness_created"] is False
    assert result_packet["paper_live_eligible"] is False
    assert result_packet["operator_gate_pending"] is False
    assert result_packet["edge_claim_allowed"] is False
    assert not (output_dir / "fake_registry_after.candidate_lifecycle_registry.json").exists()
    assert not (root / "research" / "candidate_registry.jsonl").exists()
    assert not (root / "research" / "result_populations").exists()
    assert (root / paths["registry"]).exists()
    assert any(item["decision"] == "rejected" for item in audit_payload["decisions"])
    assert not any(record.action_type == BUILD_FIXTURE_CANONICAL_CROSSING for record in sink.records)
    return result_packet


def test_valid_fixture_crosses_into_fake_registry_copy(tmp_path: Path):
    result, _builder, sink = _run_valid(tmp_path)

    assert result["status"] == "completed"
    output_path = tmp_path / result["outputs"]["fake_registry_after"]
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    event = payload["append_only_ledger"][0]
    crossing = event["crossing_evidence"]
    assert event["event_type"] == "candidate_review_packet_crossed"
    assert event["from_status"] is None
    assert event["to_status"] == "proposed"
    assert crossing["denominator_snapshot"]["failed_count"] == 1
    assert crossing["denominator_snapshot"]["invalid_count"] == 1
    assert crossing["denominator_snapshot"]["pruned_count"] == 1
    assert len(crossing["denominator_snapshot"]["row_disposition"]) == 5
    assert crossing["diagnostics_summary"]["skipped_diagnostics"]
    assert crossing["diagnostics_summary"]["missing_diagnostics"]["per_trade"][
        "fabricated_per_trade_data"
    ] is False
    assert crossing["data_availability"]["warnings"]
    assert crossing["data_availability"]["blockers"]
    assert crossing["funding"]["funding_cost_mode"] == "off"
    assert all(crossing["non_authority_flags"].values())
    assert all(crossing["append_only_semantics"].values())
    assert validate_candidate_registries(registry_dir=output_path.parent) == []
    assert (output_path.parent / "crossing_audit_log.json").exists()
    assert any(
        record.action_type == BUILD_FIXTURE_CANONICAL_CROSSING and record.decision == "allowed"
        for record in sink.records
    )
    assert not (tmp_path / "research" / "candidate_lifecycle_registry").exists()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("construction_payload", True),
        ("non_promotable", True),
        ("candidate_eligible", False),
        ("promotion_eligible", False),
        ("paper_live_eligible", False),
        ("canonical_crossing_allowed", False),
        ("edge_claim_allowed", False),
    ],
)
def test_nonpromotable_guard_rejects_eligibility_flags_before_crossing(tmp_path: Path, field: str, value: bool):
    paths = _make_fixture_tree(tmp_path)
    packet = json.loads((tmp_path / paths["packet"]).read_text(encoding="utf-8"))
    approval = json.loads((tmp_path / paths["approval"]).read_text(encoding="utf-8"))
    packet["construction_provenance"] = {field: value}
    packet["performance_summary"] = {
        "sharpe": 99.0,
        "max_drawdown": 0.001,
        "net_pnl": 1_000_000.0,
        "interpretation": "favorable metrics are fixture data and cannot override provenance",
    }
    _rewrite_packet_and_approval(tmp_path, paths, packet, approval)
    before_registry = (tmp_path / paths["registry"]).read_text(encoding="utf-8")
    builder, sink = _make_builder(tmp_path)

    with pytest.raises(CanonicalCrossingBuildError, match="construction or non-promotable"):
        builder.run(
            candidate_review_packet_path=paths["packet"],
            crossing_approval_path=paths["approval"],
            fake_registry_input_path=paths["registry"],
        )

    assert (tmp_path / paths["registry"]).read_text(encoding="utf-8") == before_registry
    result_packet = _assert_rejected_without_crossing(tmp_path, paths, sink)
    assert f"{field}={str(value).lower()}" in result_packet["details"]["triggers"]


@pytest.mark.parametrize(
    "baseline_id",
    [
        "known_losing_baseline",
        "known_neutral_or_no_trade_baseline",
        "known_degenerate_or_invalid_baseline",
    ],
)
def test_pr583_baseline_fixtures_reject_even_with_required_nonpromotable_semantics(
    tmp_path: Path, baseline_id: str
):
    paths = _make_fixture_tree(tmp_path)
    packet = json.loads((tmp_path / paths["packet"]).read_text(encoding="utf-8"))
    approval = json.loads((tmp_path / paths["approval"]).read_text(encoding="utf-8"))
    packet["construction_provenance"] = {
        "baseline_id": baseline_id,
        "construction_payload": True,
        "non_promotable": True,
        "candidate_eligible": False,
        "promotion_eligible": False,
        "paper_live_eligible": False,
        "canonical_crossing_allowed": False,
        "edge_claim_allowed": False,
    }
    packet["performance_summary"] = {
        "sharpe": 42.0,
        "sortino": 42.0,
        "net_pnl": 42_000.0,
    }
    _rewrite_packet_and_approval(tmp_path, paths, packet, approval)
    before_registry = (tmp_path / paths["registry"]).read_text(encoding="utf-8")
    builder, sink = _make_builder(tmp_path)

    with pytest.raises(CanonicalCrossingBuildError, match="construction or non-promotable"):
        builder.run(
            candidate_review_packet_path=paths["packet"],
            crossing_approval_path=paths["approval"],
            fake_registry_input_path=paths["registry"],
        )

    assert (tmp_path / paths["registry"]).read_text(encoding="utf-8") == before_registry
    result_packet = _assert_rejected_without_crossing(tmp_path, paths, sink)
    assert baseline_id in result_packet["details"]["baseline_ids"]
    assert "pr583_baseline_reference" in result_packet["details"]["triggers"]


def test_baseline_catalog_reference_without_provenance_rejects_not_passes(tmp_path: Path):
    paths = _make_fixture_tree(tmp_path)
    packet = json.loads((tmp_path / paths["packet"]).read_text(encoding="utf-8"))
    approval = json.loads((tmp_path / paths["approval"]).read_text(encoding="utf-8"))
    packet["source_catalog_refs"] = [
        {
            "path": "scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_payload_catalog.json",
            "baseline_id": "known_losing_baseline",
        }
    ]
    _rewrite_packet_and_approval(tmp_path, paths, packet, approval)
    before_registry = (tmp_path / paths["registry"]).read_text(encoding="utf-8")
    builder, sink = _make_builder(tmp_path)

    with pytest.raises(CanonicalCrossingBuildError, match="missing required non-promotable"):
        builder.run(
            candidate_review_packet_path=paths["packet"],
            crossing_approval_path=paths["approval"],
            fake_registry_input_path=paths["registry"],
        )

    assert (tmp_path / paths["registry"]).read_text(encoding="utf-8") == before_registry
    result_packet = _assert_rejected_without_crossing(tmp_path, paths, sink)
    assert result_packet["check"] == "baseline_provenance_missing_or_weakened"
    assert "known_losing_baseline" in result_packet["details"]["baseline_ids"]
    assert "construction_payload" in result_packet["details"]["missing_or_weakened_fields"]


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda approval, packet, registry: approval.pop("fixture_only"), "missing fields"),
        (lambda approval, packet, registry: approval.update({"fixture_only": False}), "fixture_only"),
        (lambda approval, packet, registry: approval.update({"content_reviewed": False}), "content_reviewed"),
        (
            lambda approval, packet, registry: approval.update({"content_reviewed_hash": "sha256:" + "0" * 64}),
            "content_reviewed_hash",
        ),
        (
            lambda approval, packet, registry: approval.update(
                {"source_candidate_review_packet_hash": "sha256:" + "1" * 64}
            ),
            "packet hash",
        ),
        (
            lambda approval, packet, registry: approval.update(
                {"source_formalizer_artifact_hash": "sha256:" + "2" * 64}
            ),
            "source_formalizer_artifact_hash",
        ),
        (
            lambda approval, packet, registry: approval.update(
                {"source_bridge_artifact_hash": "sha256:" + "3" * 64}
            ),
            "source_bridge_artifact_hash",
        ),
        (
            lambda approval, packet, registry: approval.update(
                {"source_robustness_artifact_hash": "sha256:" + "4" * 64}
            ),
            "source_robustness_artifact_hash",
        ),
        (
            lambda approval, packet, registry: approval.update(
                {"source_denominator_ledger_hash": "sha256:" + "5" * 64}
            ),
            "source_denominator_ledger_hash",
        ),
        (
            lambda approval, packet, registry: packet["denominator_snapshot"]["counts"].pop("failed"),
            "denominator count",
        ),
        (
            lambda approval, packet, registry: packet["denominator_snapshot"].pop("row_disposition"),
            "row_disposition",
        ),
        (
            lambda approval, packet, registry: packet["denominator_snapshot"]["counts"].update({"failed": 0}),
            "row_disposition counts",
        ),
        (
            lambda approval, packet, registry: packet["robustness_summary"].pop("diagnostics_skipped"),
            "skipped diagnostics",
        ),
        (
            lambda approval, packet, registry: packet["data_and_funding_summary"].pop(
                "data_availability_warnings"
            ),
            "data_availability_warnings",
        ),
        (
            lambda approval, packet, registry: packet["data_and_funding_summary"].pop("funding_mode"),
            "funding_mode",
        ),
        (
            lambda approval, packet, registry: packet["non_authority_flags"].remove(
                "not promotion authority"
            ),
            "non-authority",
        ),
        (
            lambda approval, packet, registry: approval.update({"promotion_allowed": True}),
            "promotion_allowed",
        ),
        (
            lambda approval, packet, registry: approval.update({"no_readiness": False}),
            "no_readiness",
        ),
        (
            lambda approval, packet, registry: registry["append_only_ledger"].append(
                {
                    "event_id": "CLE-FIXTURE-9001",
                    "candidate_id": "CANDIDATE-FIXTURE-9001",
                }
            ),
            "event_id collision",
        ),
    ],
)
def test_adversarial_fixture_cases_block_and_audit(tmp_path: Path, mutate, message: str):
    paths = _make_fixture_tree(tmp_path)
    approval = json.loads((tmp_path / paths["approval"]).read_text(encoding="utf-8"))
    packet = json.loads((tmp_path / paths["packet"]).read_text(encoding="utf-8"))
    registry = json.loads((tmp_path / paths["registry"]).read_text(encoding="utf-8"))
    mutate(approval, packet, registry)
    _write_json(tmp_path, paths["packet"], packet)
    if message != "packet hash":
        approval["source_candidate_review_packet_hash"] = _hash_path(tmp_path, paths["packet"])
    approval["content_reviewed_hash"] = approval.get(
        "content_reviewed_hash", _hash_path(tmp_path, paths["packet"])
    )
    if message not in {"content_reviewed_hash", "packet hash"}:
        approval["content_reviewed_hash"] = _hash_path(tmp_path, paths["packet"])
    _write_json(tmp_path, paths["approval"], approval)
    _write_json(tmp_path, paths["registry"], registry)
    before_registry = (tmp_path / paths["registry"]).read_text(encoding="utf-8")
    builder, sink = _make_builder(tmp_path)

    with pytest.raises(CanonicalCrossingBuildError, match=message):
        builder.run(
            candidate_review_packet_path=paths["packet"],
            crossing_approval_path=paths["approval"],
            fake_registry_input_path=paths["registry"],
        )

    assert (tmp_path / paths["registry"]).read_text(encoding="utf-8") == before_registry
    audit_log = (
        tmp_path / "scratch" / WP_ID / "outputs" / "fixture-crossing-run" / "crossing_audit_log.json"
    )
    assert audit_log.exists()
    audit_payload = json.loads(audit_log.read_text(encoding="utf-8"))
    assert audit_payload["status"] == "blocked"
    assert any(item["decision"] == "blocked" for item in audit_payload["decisions"])
    assert sink.records


def test_real_research_registry_output_path_blocks_and_audits(tmp_path: Path):
    context = ToolContext(wp_id=WP_ID, role=ROLE, audit_sink=MemoryAuditSink(), clock=lambda: FIXED_TIME)
    with pytest.raises(BlockedActionError):
        context.require_allowed(
            ToolAction(BUILD_FIXTURE_CANONICAL_CROSSING, "research/candidate_lifecycle_registry/real.json")
        )


def test_missing_approval_artifact_blocks_and_audits(tmp_path: Path):
    paths = _make_fixture_tree(tmp_path)
    (tmp_path / paths["approval"]).unlink()
    builder, _sink = _make_builder(tmp_path)

    with pytest.raises(CanonicalCrossingBuildError, match="file not found"):
        builder.run(
            candidate_review_packet_path=paths["packet"],
            crossing_approval_path=paths["approval"],
            fake_registry_input_path=paths["registry"],
        )

    audit_log = (
        tmp_path / "scratch" / WP_ID / "outputs" / "fixture-crossing-run" / "crossing_audit_log.json"
    )
    assert audit_log.exists()
    audit_payload = json.loads(audit_log.read_text(encoding="utf-8"))
    assert any(item["check"] == "input_exists" for item in audit_payload["decisions"])


def test_post_write_validator_failure_blocks_and_audits(tmp_path: Path, monkeypatch):
    paths = _make_fixture_tree(tmp_path)
    monkeypatch.setattr(
        crossing_build,
        "validate_candidate_registries",
        lambda registry_dir: ["forced fixture validator failure"],
    )
    builder, _sink = _make_builder(tmp_path)

    with pytest.raises(CanonicalCrossingBuildError, match="candidate registry validator failed"):
        builder.run(
            candidate_review_packet_path=paths["packet"],
            crossing_approval_path=paths["approval"],
            fake_registry_input_path=paths["registry"],
        )

    audit_log = (
        tmp_path / "scratch" / WP_ID / "outputs" / "fixture-crossing-run" / "crossing_audit_log.json"
    )
    assert audit_log.exists()
    audit_payload = json.loads(audit_log.read_text(encoding="utf-8"))
    assert any(item["check"] == "post_write_validation" for item in audit_payload["decisions"])


@pytest.mark.parametrize(
    "target_path",
    [
        "research/result_populations/RP-9999.result_population.json",
        "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json",
        "research/variant_manifests/VM-9999.variant_manifest.json",
        "research/sweep_plans/SWEEP-PLAN-9999.sweep_plan.json",
        "research/trial_log.jsonl",
        "src/runtime/paper_trader.py",
        "src/oms/orders.py",
        "src/risk/caps.py",
        "src/reconciliation/checks.py",
        "secrets/exchange.key",
    ],
)
def test_toolcontext_blocks_forbidden_fixture_crossing_targets(target_path: str):
    context = ToolContext(wp_id=WP_ID, role=ROLE, audit_sink=MemoryAuditSink(), clock=lambda: FIXED_TIME)

    with pytest.raises(BlockedActionError):
        context.require_allowed(ToolAction(BUILD_FIXTURE_CANONICAL_CROSSING, target_path))


def test_toolcontext_fixture_role_is_closed_to_production_actions():
    assert ROLE in ROLE_PERMISSIONS
    context = ToolContext(wp_id=WP_ID, role=ROLE, audit_sink=MemoryAuditSink(), clock=lambda: FIXED_TIME)

    for action_type in [
        "candidate_registration",
        "candidate_freeze",
        "candidate_promotion",
        "candidate_readiness",
        "paper_control",
        "live_control",
        "private_endpoint_access",
        "network_access",
        "provider_api_call",
        "toolcontext_bypass",
    ]:
        with pytest.raises(BlockedActionError):
            context.require_allowed(ToolAction(action_type, "scratch/WP-AGENT-CANONICAL-CROSSING-BUILD-01/outputs/x"))
