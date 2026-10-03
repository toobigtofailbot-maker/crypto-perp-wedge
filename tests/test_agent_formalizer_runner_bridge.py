from __future__ import annotations

import copy
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from tools.agent_sandbox import BlockedActionError, MemoryAuditSink, ToolAction, ToolContext
from tools.agent_sandbox.permissions import READ_NON_SECRET, RUN_NONCANONICAL_OFFLINE_SWEEP
from tools.registry.validate_strategy_specs import validate_strategy_specs
from tools.registry.validate_variant_sweep_artifacts import validate_variant_sweep_artifacts
from tools.research_agents.formalizer_runner_bridge import (
    APPROVAL_SCOPE,
    FORMALIZER_OUTPUT_PREFIX,
    PRODUCT_APPROVAL_CONTENT_HASH_FIELD,
    PRODUCT_APPROVAL_SCOPE,
    PRODUCT_APPROVAL_SCHEMA_VERSION,
    PRODUCT_APPROVAL_STATEMENT,
    PRODUCT_BRIDGE_INVOCATION_MODE,
    PRODUCT_BRIDGE_PREPARE_WP_ID,
    PRODUCT_BRIDGE_STAGE_IDENTITY,
    PRODUCT_FALSE_AUTHORITY_FLAGS,
    NON_AUTHORITY_FLAGS,
    ROLE,
    TRIAL_STATUSES,
    WP_ID,
    FormalizerRunnerBridge,
    FormalizerRunnerBridgeConfig,
    FormalizerRunnerBridgeError,
    FUNDING_RESEARCH_WP_ID,
    _approval_content_hash,
)
from tools.research_agents.idea_formalizer_agent import (
    AVAILABILITY_CATALOG_PATH,
    INDICATOR_CATALOG_PATH,
    STRATEGY_TEMPLATE_PATH,
    IdeaFormalizerAgent,
    IdeaFormalizerConfig,
)
from tools.research_agents.reasoning_providers import FakeOfflineProvider
from tools.research_runner.spec_signal_compiler import compile_signal


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXED_TIME = datetime(2026, 6, 22, 1, 2, 3, tzinfo=timezone.utc)


def _write_json(root: Path, relative: str, payload: dict) -> str:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return relative


def _copy_templates(root: Path) -> None:
    for relative in (
        "research/variant_manifests/VM-0003.variant_manifest.json",
        "research/sweep_plans/SWEEP-PLAN-0003.sweep_plan.json",
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((REPO_ROOT / relative).read_bytes())


def _draft_strategy_spec(formalizer_path: str) -> dict:
    spec = copy.deepcopy(
        json.loads(
            (REPO_ROOT / "research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json").read_text()
        )
    )
    spec["strategy_spec_id"] = "STRAT-SPEC-9001"
    spec["title"] = "Draft provider-assisted SMA/stddev mean-reversion Strategy Spec"
    spec["short_name"] = "draft-bridge-test"
    spec["status"] = "draft"
    spec["provenance"] = {
        "source_type": "manual_idea",
        "source_refs": [formalizer_path],
        "prepared_by": "bounded idea_formalizer agent",
        "created_at": None,
        "updated_at": None,
        "rationale": "Test the merged SMA/stddev mean-reversion family.",
        "source_constraints": [
            "Scratch-only draft adapted from the merged STRAT-SPEC-0003 capability family."
        ],
        "unresolved_claims": ["Human review required."],
    }
    spec["review"].update(
        {
            "reviewer": None,
            "reviewed_at": None,
            "review_notes": ["Scratch-only provider-assisted draft."],
            "approval_scope": "none",
        }
    )
    spec["lineage"] = {
        "parent_refs": [
            {
                "ref_type": "concept",
                "ref_id": "IDEA-BRIDGE-TEST",
                "ref_path": formalizer_path,
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


def _feature_assessment(
    feature: str,
    *,
    coverage: str = "FULL_HISTORY_PUBLIC_ARCHIVE",
    source: str = "INDICATOR_DERIVED_FROM_OHLCV",
    testability: str = "available_when_source_bars_exist",
) -> dict:
    return {
        "feature": feature,
        "compiler_field_exists": True,
        "historical_testability": testability,
        "coverage_class": coverage,
        "source_class": source,
        "warnings": [],
    }


def _write_ohlcv_fixture(root: Path) -> str:
    relative = f"scratch/{WP_ID}/fixtures/canonical_15m_ohlcv.csv"
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    index = pd.date_range("2026-01-01T00:00:00Z", periods=160, freq="15min")
    pattern = [100.0] * 40 + [94.0, 98.0, 101.0, 90.0, 96.0, 102.0, 88.0, 100.0]
    close = (pattern * 4)[: len(index)]
    pd.DataFrame(
        {
            "timestamp": index,
            "open": [value + 0.1 for value in close],
            "high": [value + 1.0 for value in close],
            "low": [value - 1.0 for value in close],
            "close": close,
            "volume": [1000.0] * len(index),
        }
    ).to_csv(path, index=False)
    return relative


def _setup_source(
    root: Path,
    *,
    approved: bool = True,
    extra_assessments: list[dict] | None = None,
    funding_approved: bool = False,
) -> tuple[str, str, str]:
    run_id = "formalizerbridge1"
    prefix = f"{FORMALIZER_OUTPUT_PREFIX}{run_id}"
    formalizer_path = f"{prefix}/formalized_idea.json"
    draft_path = f"{prefix}/STRAT-SPEC-9001.strategy_spec.json"
    assessments = [_feature_assessment("sma"), _feature_assessment("stddev")]
    assessments.extend(extra_assessments or [])
    payload = {
        "schema_version": "agent_formalized_idea_v1",
        "run_id": run_id,
        "status": "accepted",
        "input": {
            "idea": "Fade z-score extremes using SMA and standard deviation.",
            "symbol": "BTCUSDT",
            "timeframe": "15m",
        },
        "capability_assessment": {
            "detected_features": [row["feature"] for row in assessments],
            "feature_assessments": assessments,
            "historically_testable_now": True,
            "blocking_features": [],
        },
        "research_object": {
            "summary": "bounded SMA/stddev mean-reversion idea",
            "symbols": ["BTCUSDT"],
            "timeframe": "15m",
            "features": [row["feature"] for row in assessments],
        },
        "draft_strategy_spec": {"produced": True, "path": draft_path, "blockers": []},
        "non_authority": {"scratch_only": True, "not_canonical": True},
    }
    _write_json(root, draft_path, _draft_strategy_spec(formalizer_path))
    _write_json(root, formalizer_path, payload)
    approval = {
        "approved_for_noncanonical_runner_bridge": approved,
        "approved_by": "operator",
        "approval_scope": APPROVAL_SCOPE,
        "approval_timestamp_utc": "2026-06-22T00:00:00Z",
        "source_formalizer_run_id": run_id,
    }
    if funding_approved:
        approval["approved_funding_cost_mode"] = "on"
    approval_path = _write_json(root, f"{prefix}/operator_bridge_approval.json", approval)
    fixture_path = _write_ohlcv_fixture(root)
    return formalizer_path, approval_path, fixture_path


def _file_sha256(root: Path, relative: str) -> str:
    return "sha256:" + hashlib.sha256((root / relative).read_bytes()).hexdigest()


def _setup_product_source(
    root: Path,
    *,
    approval_overrides: dict | None = None,
    corrupt_approval_content_hash: bool = False,
    approval_path_override: str | None = None,
    product_packet_path_override: str | None = None,
    formalizer_path_override: str | None = None,
) -> tuple[str, str, str, str]:
    run_id = "productbridge1"
    prefix = f"scratch/{PRODUCT_BRIDGE_PREPARE_WP_ID}/outputs/{run_id}"
    formalizer_path = formalizer_path_override or f"{prefix}/formalized_idea.json"
    draft_path = f"{prefix}/STRAT-SPEC-9001.strategy_spec.json"
    product_packet_path = product_packet_path_override or f"{prefix}/source_product_packet.json"
    output_root = f"scratch/{PRODUCT_BRIDGE_PREPARE_WP_ID}/outputs"
    assessments = [_feature_assessment("sma"), _feature_assessment("stddev")]
    formalized = {
        "schema_version": "agent_formalized_idea_v1",
        "run_id": run_id,
        "status": "accepted",
        "input": {
            "idea": "Fade z-score extremes using SMA and standard deviation.",
            "symbol": "BTCUSDT",
            "timeframe": "15m",
        },
        "capability_assessment": {
            "detected_features": [row["feature"] for row in assessments],
            "feature_assessments": assessments,
            "historically_testable_now": True,
            "blocking_features": [],
        },
        "research_object": {
            "summary": "bounded SMA/stddev mean-reversion idea",
            "symbols": ["BTCUSDT"],
            "timeframe": "15m",
            "features": [row["feature"] for row in assessments],
        },
        "draft_strategy_spec": {"produced": True, "path": draft_path, "blockers": []},
        "non_authority": {"scratch_only": True, "not_canonical": True},
    }
    product_packet = {
        "schema_version": "lab_product_bridge_source_packet_v1",
        "pipeline_run_id": "PIPELINE-PRODUCT-BRIDGE-0001",
        "bridge_stage_identity": PRODUCT_BRIDGE_STAGE_IDENTITY,
        "source_formalizer_output_path": formalizer_path,
        "non_authority": {"scratch_only": True},
    }
    _write_json(root, draft_path, _draft_strategy_spec(formalizer_path))
    _write_json(root, formalizer_path, formalized)
    _write_json(root, product_packet_path, product_packet)
    approval = {
        "schema_version": PRODUCT_APPROVAL_SCHEMA_VERSION,
        "approved_by": "Karl",
        "approval_scope": PRODUCT_APPROVAL_SCOPE,
        "approval_statement": PRODUCT_APPROVAL_STATEMENT,
        "approval_timestamp_utc": "2000-01-01T00:00:00Z",
        "source_product_packet_path": product_packet_path,
        "source_product_packet_sha256": _file_sha256(root, product_packet_path),
        "source_formalizer_output_path": formalizer_path,
        "source_formalizer_output_sha256": _file_sha256(root, formalizer_path),
        "source_formalizer_run_id": run_id,
        "product_pipeline_run_id": product_packet["pipeline_run_id"],
        "bridge_stage_identity": PRODUCT_BRIDGE_STAGE_IDENTITY,
        "product_mode_output_root": output_root,
        "authorizes_bridge_preparation": True,
        **{field: False for field in PRODUCT_FALSE_AUTHORITY_FLAGS},
    }
    approval.update(approval_overrides or {})
    approval[PRODUCT_APPROVAL_CONTENT_HASH_FIELD] = _approval_content_hash(approval)
    if corrupt_approval_content_hash:
        approval[PRODUCT_APPROVAL_CONTENT_HASH_FIELD] = "sha256:" + "0" * 64
    approval_path = approval_path_override or f"{prefix}/karl_bridge_preparation_approval.json"
    _write_json(root, approval_path, approval)
    fixture_path = _write_ohlcv_fixture(root)
    return formalizer_path, approval_path, product_packet_path, fixture_path


def _context() -> tuple[ToolContext, MemoryAuditSink]:
    sink = MemoryAuditSink()
    return (
        ToolContext(wp_id=WP_ID, role=ROLE, audit_sink=sink, clock=lambda: FIXED_TIME),
        sink,
    )


def _product_context() -> tuple[ToolContext, MemoryAuditSink]:
    sink = MemoryAuditSink()
    return (
        ToolContext(
            wp_id=PRODUCT_BRIDGE_PREPARE_WP_ID,
            role=ROLE,
            audit_sink=sink,
            clock=lambda: FIXED_TIME,
        ),
        sink,
    )


def _run(root: Path, *, config: FormalizerRunnerBridgeConfig | None = None, **source_kwargs):
    _copy_templates(root)
    formalizer_path, approval_path, fixture_path = _setup_source(root, **source_kwargs)
    context, sink = _context()
    bridge = FormalizerRunnerBridge(
        config=config or FormalizerRunnerBridgeConfig(ohlcv_input_path=fixture_path),
        tool_context=context,
        repo_root=root,
    )
    return (
        bridge.run(
            formalizer_output_path=formalizer_path,
            approval_path=approval_path,
        ),
        sink,
    )


def _run_product(
    root: Path,
    *,
    approval_overrides: dict | None = None,
    corrupt_approval_content_hash: bool = False,
):
    _copy_templates(root)
    formalizer_path, approval_path, product_packet_path, fixture_path = _setup_product_source(
        root,
        approval_overrides=approval_overrides,
        corrupt_approval_content_hash=corrupt_approval_content_hash,
    )
    context, sink = _product_context()
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(ohlcv_input_path=fixture_path),
        tool_context=context,
        repo_root=root,
        bridge_invocation_mode=PRODUCT_BRIDGE_INVOCATION_MODE,
    )
    return (
        bridge.run(
            formalizer_output_path=formalizer_path,
            approval_path=approval_path,
            source_product_packet_path=product_packet_path,
        ),
        sink,
    )


def test_approved_bridge_runs_real_runner_and_reconciles(tmp_path: Path):
    result, sink = _run(tmp_path)

    assert result["status"] == "completed"
    assert result["manual_reconciliation_result"]["passed"] is True
    assert result["trial_status_counts"]["completed"] == 8
    assert sum(result["trial_status_counts"].values()) == 8
    assert result["artifact_paths"]["runner_result"].startswith(
        f"scratch/{WP_ID}/outputs/"
    )
    assert (tmp_path / result["artifact_paths"]["runner_result"]).is_file()

    input_dir = (tmp_path / result["artifact_paths"]["strategy_spec"]).parent
    assert validate_strategy_specs(strategy_specs_dir=input_dir) == []
    assert (
        validate_variant_sweep_artifacts(
            strategy_specs_dir=input_dir,
            variant_manifests_dir=input_dir,
            sweep_plans_dir=input_dir,
        )
        == []
    )
    manifest = json.loads((tmp_path / result["artifact_paths"]["variant_manifest"]).read_text())
    assert manifest["status"] == "approved_for_sweep_planning"
    assert "grants no canonical freeze authority" in " ".join(manifest["lineage"]["audit_notes"])

    ledger = json.loads((tmp_path / result["artifact_paths"]["denominator_ledger"]).read_text())
    assert ledger["denominator_preserved"] is True
    assert len(ledger["rows"]) == 8
    assert all(row["funding_cost_mode"] == "off" for row in ledger["rows"])
    assert all(row["non_authority_flags"] == list(NON_AUTHORITY_FLAGS) for row in ledger["rows"])
    review = json.loads((tmp_path / result["artifact_paths"]["human_review_packet"]).read_text())
    assert review["manual_reconciliation_result"]["passed"] is True
    assert review["full_ledger_path"] == result["artifact_paths"]["denominator_ledger"]
    assert review["runner_artifact_paths"] == [result["artifact_paths"]["runner_result"]]
    assert review["funding_mode"]["effective"] == "off"
    assert any(
        record.action_type == RUN_NONCANONICAL_OFFLINE_SWEEP and record.decision == "allowed"
        for record in sink.records
    )


def test_legacy_bridge_byte_regression_fixture_remains_stable(tmp_path: Path):
    result, sink = _run(tmp_path)

    assert result["run_id"] == "c81e86a223723b97"
    assert result["status"] == "completed"
    assert result["trial_status_counts"] == {
        "completed": 8,
        "failed": 0,
        "invalid": 0,
        "pruned": 0,
        "blocked": 0,
    }
    expected_paths = {
        "strategy_spec": (
            "scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/"
            "c81e86a223723b97/inputs/STRAT-SPEC-9001.strategy_spec.json"
        ),
        "variant_manifest": (
            "scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/"
            "c81e86a223723b97/inputs/VM-9746.variant_manifest.json"
        ),
        "sweep_plan": (
            "scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/"
            "c81e86a223723b97/inputs/SWEEP-PLAN-9746.sweep_plan.json"
        ),
        "denominator_ledger": (
            "scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/"
            "c81e86a223723b97/denominator_ledger.json"
        ),
        "human_review_packet": (
            "scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/"
            "c81e86a223723b97/human_review_packet.json"
        ),
        "runner_result": (
            "scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/"
            "c81e86a223723b97/runner_artifacts/RP-6770.result_population.json"
        ),
    }
    expected_hashes = {
        "strategy_spec": "sha256:2152be54645c20bc0a320142002abfb3a223f28f7ca7c1f9cbbd638d9e03caae",
        "variant_manifest": "sha256:ad0ec366a903bbd12f8a06d50d6a61cdff452d4bdeab6d859ce29f2bd13f947c",
        "sweep_plan": "sha256:9dce4b61acfad4b04f1e38836b3fb8297122a6a6b0e82e6c35c2ab1a591c2254",
        "denominator_ledger": "sha256:eee66974a3962b7b620da8a3da08072bb358967a32ab982a9236ce4086966138",
        "human_review_packet": "sha256:cb1bf1d50456dc721b7fed32bb8b76f097b832da790fc7d144471f4268328f7a",
        "runner_result": "sha256:5ff8257d833a92e95ec9c137fde001c3085d150ef97fd8983765c7b7202f8f64",
    }
    for key, expected_path in expected_paths.items():
        assert result["artifact_paths"][key] == expected_path
        assert _file_sha256(tmp_path, expected_path) == expected_hashes[key]
    assert (
        sum(
            1
            for record in sink.records
            if record.action_type == RUN_NONCANONICAL_OFFLINE_SWEEP
            and record.decision == "allowed"
        )
        == 2
    )


def test_product_bridge_prepare_only_writes_product_scratch_and_never_runs_runner(
    tmp_path: Path,
):
    result, sink = _run_product(tmp_path)

    assert result["status"] == "prepared"
    assert result["trial_status_counts"] == {
        "completed": 0,
        "failed": 0,
        "invalid": 0,
        "pruned": 0,
        "blocked": 8,
    }
    assert result["artifact_paths"]["runner_result"] is None
    assert result["artifact_paths"]["runner_results"] == {}
    assert not any(record.action_type == RUN_NONCANONICAL_OFFLINE_SWEEP for record in sink.records)
    assert (
        sum(record.action_type == "run_read_only_validation" for record in sink.records)
        >= 3
    )
    assert not (tmp_path / f"scratch/{PRODUCT_BRIDGE_PREPARE_WP_ID}/outputs" / result["run_id"] / "runner_artifacts").exists()
    for path in (
        result["artifact_paths"]["strategy_spec"],
        result["artifact_paths"]["variant_manifest"],
        result["artifact_paths"]["sweep_plan"],
        result["artifact_paths"]["denominator_ledger"],
        result["artifact_paths"]["human_review_packet"],
    ):
        assert path.startswith(f"scratch/{PRODUCT_BRIDGE_PREPARE_WP_ID}/outputs/")
        assert (tmp_path / path).is_file()
    review = json.loads((tmp_path / result["artifact_paths"]["human_review_packet"]).read_text())
    assert review["validation_status"] == "prepared"
    assert review["runner_invocation_metadata"]["runner_invoked"] is False
    assert review["runner_invocation_metadata"]["runner_boundary"] == "not_requested"
    assert review["runner_artifact_paths"] == []
    assert (
        review["product_bridge_preparation_metadata"]["stale_approval_policy"]
        == "content_bound_no_wall_clock_expiry"
    )
    input_dir = (tmp_path / result["artifact_paths"]["strategy_spec"]).parent
    assert validate_strategy_specs(strategy_specs_dir=input_dir) == []
    assert (
        validate_variant_sweep_artifacts(
            strategy_specs_dir=input_dir,
            variant_manifests_dir=input_dir,
            sweep_plans_dir=input_dir,
        )
        == []
    )


@pytest.mark.parametrize(
    "approval_overrides",
    [
        {"approved_by": "operator"},
        {"approval_scope": APPROVAL_SCOPE},
        {"approval_statement": "Approve something broader."},
        {"approval_timestamp_utc": ""},
        {"approval_timestamp_utc": "not-a-timestamp"},
        {"source_product_packet_sha256": "sha256:" + "1" * 64},
        {"source_formalizer_output_sha256": "sha256:" + "2" * 64},
        {"source_formalizer_run_id": "other-run"},
        {"product_pipeline_run_id": "other-product-run"},
        {"bridge_stage_identity": "runner_execution"},
        {"product_mode_output_root": "scratch/other/outputs"},
        {"authorizes_bridge_preparation": False},
    ],
)
def test_product_bridge_approval_mismatch_fails_closed(
    tmp_path: Path,
    approval_overrides: dict,
):
    with pytest.raises(BlockedActionError):
        _run_product(tmp_path, approval_overrides=approval_overrides)


@pytest.mark.parametrize("flag", PRODUCT_FALSE_AUTHORITY_FLAGS)
def test_product_bridge_rejects_any_protected_authority_flag_true(
    tmp_path: Path,
    flag: str,
):
    with pytest.raises(BlockedActionError):
        _run_product(tmp_path, approval_overrides={flag: True})


def test_product_bridge_rejects_approval_content_hash_mismatch(tmp_path: Path):
    with pytest.raises(BlockedActionError):
        _run_product(tmp_path, corrupt_approval_content_hash=True)


def test_product_bridge_rejects_legacy_operator_approval(tmp_path: Path):
    _copy_templates(tmp_path)
    formalizer_path, _, product_packet_path, fixture_path = _setup_product_source(tmp_path)
    approval_path = _write_json(
        tmp_path,
        f"scratch/{PRODUCT_BRIDGE_PREPARE_WP_ID}/outputs/productbridge1/operator_bridge_approval.json",
        {
            "approved_for_noncanonical_runner_bridge": True,
            "approved_by": "operator",
            "approval_scope": APPROVAL_SCOPE,
            "approval_timestamp_utc": "2026-06-22T00:00:00Z",
            "source_formalizer_run_id": "productbridge1",
        },
    )
    context, _ = _product_context()
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(ohlcv_input_path=fixture_path),
        tool_context=context,
        repo_root=tmp_path,
        bridge_invocation_mode=PRODUCT_BRIDGE_INVOCATION_MODE,
    )

    with pytest.raises(BlockedActionError):
        bridge.run(
            formalizer_output_path=formalizer_path,
            approval_path=approval_path,
            source_product_packet_path=product_packet_path,
        )


def test_product_bridge_rejects_broad_pipeline_prereg_approval(tmp_path: Path):
    _copy_templates(tmp_path)
    formalizer_path, _, product_packet_path, fixture_path = _setup_product_source(tmp_path)
    approval_path = _write_json(
        tmp_path,
        f"scratch/{PRODUCT_BRIDGE_PREPARE_WP_ID}/outputs/productbridge1/pipeline_prereg_approval.json",
        {
            "schema_version": "lab_pipeline_prereg_approval_v1",
            "approved_by": "Karl",
            "approval_scope": "noncanonical_offline_research_execution_only",
            "approval_statement": (
                "Authorizes only non-canonical offline research execution for the exact "
                "frozen preregistration packet content."
            ),
            "approval_timestamp_utc": "2026-07-08T00:00:00Z",
            "authorizes_noncanonical_offline_research_execution": True,
            "authorizes_canonical_write": False,
            "authorizes_candidate_lifecycle": False,
            "authorizes_paper_live_runtime": False,
            "authorizes_scheduler_autonomy": False,
            "authorizes_notifications": False,
        },
    )
    context, _ = _product_context()
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(ohlcv_input_path=fixture_path),
        tool_context=context,
        repo_root=tmp_path,
        bridge_invocation_mode=PRODUCT_BRIDGE_INVOCATION_MODE,
    )

    with pytest.raises(BlockedActionError):
        bridge.run(
            formalizer_output_path=formalizer_path,
            approval_path=approval_path,
            source_product_packet_path=product_packet_path,
        )


def test_product_bridge_accepts_old_timestamp_without_wall_clock_expiry(tmp_path: Path):
    result, _ = _run_product(
        tmp_path,
        approval_overrides={"approval_timestamp_utc": "1999-12-31T23:59:59Z"},
    )

    assert result["status"] == "prepared"


def test_product_bridge_does_not_call_runner_even_with_unblocked_inputs(
    tmp_path: Path,
    monkeypatch,
):
    def fail_runner(*args, **kwargs):
        raise AssertionError("product mode must not invoke the runner")

    monkeypatch.setattr(FormalizerRunnerBridge, "_invoke_runner", fail_runner)
    result, sink = _run_product(tmp_path)

    assert result["status"] == "prepared"
    assert not any(record.action_type == RUN_NONCANONICAL_OFFLINE_SWEEP for record in sink.records)


def test_product_bridge_invalid_draft_fails_closed_without_runner_artifacts(
    tmp_path: Path,
):
    _copy_templates(tmp_path)
    formalizer_path, approval_path, product_packet_path, fixture_path = _setup_product_source(tmp_path)
    formalized = json.loads((tmp_path / formalizer_path).read_text())
    draft_path = formalized["draft_strategy_spec"]["path"]
    draft = json.loads((tmp_path / draft_path).read_text())
    draft["strategy_spec_id"] = ""
    _write_json(tmp_path, draft_path, draft)
    context, sink = _product_context()
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(ohlcv_input_path=fixture_path),
        tool_context=context,
        repo_root=tmp_path,
        bridge_invocation_mode=PRODUCT_BRIDGE_INVOCATION_MODE,
    )

    with pytest.raises(FormalizerRunnerBridgeError, match="draft Strategy Spec validation failed"):
        bridge.run(
            formalizer_output_path=formalizer_path,
            approval_path=approval_path,
            source_product_packet_path=product_packet_path,
        )
    product_outputs = tmp_path / "scratch" / PRODUCT_BRIDGE_PREPARE_WP_ID / "outputs"
    assert not list(product_outputs.rglob("runner_artifacts"))
    assert not list(product_outputs.rglob("denominator_ledger.json"))
    assert not list(product_outputs.rglob("human_review_packet.json"))
    assert not any(record.action_type == RUN_NONCANONICAL_OFFLINE_SWEEP for record in sink.records)


def test_product_bridge_rejects_paths_outside_product_scratch(tmp_path: Path):
    _copy_templates(tmp_path)
    formalizer_path, approval_path, product_packet_path, fixture_path = _setup_product_source(
        tmp_path,
        product_packet_path_override="scratch/OTHER-PACKAGE/source_product_packet.json",
    )
    context, _ = _product_context()
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(ohlcv_input_path=fixture_path),
        tool_context=context,
        repo_root=tmp_path,
        bridge_invocation_mode=PRODUCT_BRIDGE_INVOCATION_MODE,
    )

    with pytest.raises(FormalizerRunnerBridgeError, match="source product packet"):
        bridge.run(
            formalizer_output_path=formalizer_path,
            approval_path=approval_path,
            source_product_packet_path=product_packet_path,
        )


def test_product_bridge_rejects_output_root_outside_product_scratch(tmp_path: Path):
    context, _ = _product_context()

    with pytest.raises(FormalizerRunnerBridgeError, match="product output root"):
        FormalizerRunnerBridge(
            config=FormalizerRunnerBridgeConfig(ohlcv_input_path="unused.csv"),
            tool_context=context,
            repo_root=tmp_path,
            bridge_invocation_mode=PRODUCT_BRIDGE_INVOCATION_MODE,
            product_output_root="scratch/OTHER-PACKAGE/outputs",
        )


def test_product_bridge_rejects_legacy_wp_identity_in_product_mode(tmp_path: Path):
    context, _ = _context()

    with pytest.raises(ValueError, match="product bridge preparation"):
        FormalizerRunnerBridge(
            config=FormalizerRunnerBridgeConfig(ohlcv_input_path="unused.csv"),
            tool_context=context,
            repo_root=tmp_path,
            bridge_invocation_mode=PRODUCT_BRIDGE_INVOCATION_MODE,
        )


def test_legacy_mode_rejects_product_wp_and_product_approval(tmp_path: Path):
    context, _ = _product_context()
    with pytest.raises(ValueError, match="exact ToolContext role and WP"):
        FormalizerRunnerBridge(
            config=FormalizerRunnerBridgeConfig(ohlcv_input_path="unused.csv"),
            tool_context=context,
            repo_root=tmp_path,
        )

    _copy_templates(tmp_path)
    _, approval_path, _, fixture_path = _setup_product_source(tmp_path)
    legacy_context, _ = _context()
    legacy_bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(ohlcv_input_path=fixture_path),
        tool_context=legacy_context,
        repo_root=tmp_path,
    )
    approval = json.loads((tmp_path / approval_path).read_text())
    with pytest.raises(BlockedActionError):
        legacy_bridge._require_approval(
            approval,
            source_run_id="productbridge1",
            approval_path=(
                "scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/"
                "productbridge1/karl_bridge_preparation_approval.json"
            ),
            formalizer_path=(
                "scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/"
                "productbridge1/formalized_idea.json"
            ),
        )


def test_funding_bridge_emits_valid_18_row_halves_and_compiles(tmp_path: Path):
    _copy_templates(tmp_path)
    for relative in (INDICATOR_CATALOG_PATH, AVAILABILITY_CATALOG_PATH, STRATEGY_TEMPLATE_PATH):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / relative, target)
    sink = MemoryAuditSink()
    formalizer_context = ToolContext(
        wp_id=FUNDING_RESEARCH_WP_ID,
        role="idea_formalizer",
        audit_sink=sink,
        clock=lambda: FIXED_TIME,
    )
    formalizer = IdeaFormalizerAgent(
        config=IdeaFormalizerConfig(),
        tool_context=formalizer_context,
        provider=FakeOfflineProvider(),
        repo_root=tmp_path,
    )
    formalized = formalizer.run(
        idea=(
            "BTCUSDT 15m funding_rate extremes mean revert because crowded perpetual "
            "positioning unwinds."
        )
    )
    bridge_context = ToolContext(
        wp_id=FUNDING_RESEARCH_WP_ID,
        role=ROLE,
        audit_sink=MemoryAuditSink(),
        clock=lambda: FIXED_TIME,
    )
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(ohlcv_input_path="unused.csv"),
        tool_context=bridge_context,
        repo_root=tmp_path,
    )
    for index, mode in enumerate(("midline_reversion_or_max_hold", "fixed_max_hold_only")):
        draft_path = formalized["adapter_metadata"]["strategy_spec_paths"][mode]
        draft = json.loads((tmp_path / draft_path).read_text(encoding="utf-8"))
        paths = bridge._derive_inputs(
            run_id="abcdef0123456789",
            run_dir=Path(f"scratch/{FUNDING_RESEARCH_WP_ID}/outputs/test/{mode}"),
            formalized=formalized,
            formalizer_path=f"scratch/{FUNDING_RESEARCH_WP_ID}/outputs/source/formalized_idea.json",
            formalizer_hash="sha256:" + "1" * 64,
            approval_path=f"scratch/{FUNDING_RESEARCH_WP_ID}/outputs/source/operator_bridge_approval.json",
            approval_hash="sha256:" + "2" * 64,
            draft=draft,
            family_id="funding_rate_positioning_fade_v1",
            funding_exit_mode=mode,
            numeric_offset=index,
        )
        bridge._validate_derived_inputs(paths)
        manifest = json.loads((tmp_path / paths["variant_manifest"]).read_text(encoding="utf-8"))
        assert len(manifest["variant_assignments"]) == 18
        index_values = pd.date_range("2020-01-01T00:00:00Z", periods=18000, freq="15min")
        frame = pd.DataFrame(
            {
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
                "volume": 1000.0,
                "funding_rate": [((value % 19) - 9) / 100000 for value in range(18000)],
            },
            index=index_values,
        )
        signal = compile_signal(draft, manifest["variant_assignments"][0], frame)
        assert len(signal) == len(frame)


def test_funding_bridge_data_read_allowance_is_exact():
    context = ToolContext(
        wp_id=FUNDING_RESEARCH_WP_ID,
        role=ROLE,
        audit_sink=MemoryAuditSink(),
        clock=lambda: FIXED_TIME,
    )
    exact = (
        "data/processed/d4a/"
        "binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_funding_feature_v1.csv"
    )
    context.require_allowed(ToolAction(READ_NON_SECRET, exact))
    with pytest.raises(BlockedActionError):
        context.require_allowed(ToolAction(READ_NON_SECRET, exact.replace("funding_feature_v1", "other")))


def test_missing_bridge_approval_is_blocked_and_audited(tmp_path: Path):
    _copy_templates(tmp_path)
    formalizer_path, approval_path, fixture_path = _setup_source(tmp_path, approved=False)
    context, sink = _context()
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(ohlcv_input_path=fixture_path),
        tool_context=context,
        repo_root=tmp_path,
    )

    with pytest.raises(BlockedActionError):
        bridge.run(formalizer_output_path=formalizer_path, approval_path=approval_path)
    assert sink.records[-1].action_type == "approval_gate_bypass"
    assert sink.records[-1].decision == "blocked"


def test_explicit_funding_on_is_approval_gated_then_blocked_as_runner_unsupported(tmp_path: Path):
    config = FormalizerRunnerBridgeConfig(
        ohlcv_input_path=f"scratch/{WP_ID}/fixtures/canonical_15m_ohlcv.csv",
        funding_cost_mode="on",
    )
    result, sink = _run(tmp_path, config=config, funding_approved=True)

    assert result["status"] == "blocked"
    assert "no explicit funding-on input" in result["blockers"][0]
    assert result["trial_status_counts"] == {
        "completed": 0,
        "failed": 0,
        "invalid": 0,
        "pruned": 0,
        "blocked": 8,
    }
    review = json.loads((tmp_path / result["artifact_paths"]["human_review_packet"]).read_text())
    assert review["funding_mode"]["requested"] == "on"
    assert review["funding_mode"]["effective"] == "not_run"
    assert not any(
        record.action_type == RUN_NONCANONICAL_OFFLINE_SWEEP and record.decision == "allowed"
        for record in sink.records
    )


def test_explicit_funding_on_without_matching_approval_is_blocked_and_audited(tmp_path: Path):
    _copy_templates(tmp_path)
    formalizer_path, approval_path, fixture_path = _setup_source(tmp_path)
    context, sink = _context()
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(
            ohlcv_input_path=fixture_path,
            funding_cost_mode="on",
        ),
        tool_context=context,
        repo_root=tmp_path,
    )

    with pytest.raises(BlockedActionError):
        bridge.run(formalizer_output_path=formalizer_path, approval_path=approval_path)
    assert sink.records[-1].action_type == "approval_gate_bypass"
    assert sink.records[-1].decision == "blocked"


@pytest.mark.parametrize(
    "assessment, expected",
    [
        (
            _feature_assessment(
                "open_interest",
                coverage="PUBLIC_SNAPSHOT_ONLY",
                source="PUBLIC_SNAPSHOT",
                testability="vendor_or_capture_constrained",
            ),
            "open interest cannot be reconstructed from trades",
        ),
        (
            _feature_assessment(
                "liquidation_volume",
                coverage="VENDOR_ONLY_FOR_HISTORY",
                source="VENDOR_HISTORICAL_DATASET",
                testability="vendor_or_capture_constrained",
            ),
            "liquidation history requires vendor/captured data",
        ),
        (
            _feature_assessment(
                "taker_buy_sell_ratio",
                coverage="FULL_HISTORY_PUBLIC_ARCHIVE",
                source="CANONICAL_D4_KLINE_DERIVATION",
                testability="available_when_source_bars_exist",
            ),
            "plain five-column OHLCV is insufficient",
        ),
    ],
)
def test_constrained_full_history_data_is_blocked_before_runner(
    tmp_path: Path, assessment, expected
):
    result, sink = _run(tmp_path, extra_assessments=[assessment])

    assert result["status"] == "blocked"
    assert any(expected in blocker for blocker in result["blockers"])
    assert result["trial_status_counts"]["blocked"] == 8
    assert not any(record.action_type == RUN_NONCANONICAL_OFFLINE_SWEEP for record in sink.records)
    assert any(
        record.action_type == "data_availability_bypass" and record.decision == "blocked"
        for record in sink.records
    )


def test_runner_outcomes_map_to_complete_denominator_statuses(tmp_path: Path):
    outcomes = ["successful", "failed", "invalid", "filtered", "data_unavailable"]
    manifest = {
        "variant_assignments": [
            {
                "variant_id": f"VAR-{index:06d}",
                "parameter_values": {"lookback": index},
            }
            for index in range(1, 6)
        ]
    }
    runner_result = {
        "result_population": {
            "variant_result_rows": [
                {
                    "variant_id": f"VAR-{index:06d}",
                    "outcome_category": outcome,
                    "non_success": {"reason": outcome},
                    "metrics": {"sharpe": 1.0},
                    "row_identity_hash": f"sha256:{index:064x}",
                }
                for index, outcome in enumerate(outcomes, start=1)
            ]
        }
    }
    rows = FormalizerRunnerBridge._ledger_rows(
        run_id="run",
        runner_invocation_id="invocation",
        formalizer_run_id="formalizer",
        formalizer_path="scratch/source.json",
        approval_scope=APPROVAL_SCOPE,
        input_paths={"strategy_spec": "scratch/spec.json"},
        manifest=manifest,
        runner_result=runner_result,
        runner_artifact_path="scratch/result.json",
        blockers=[],
        funding_cost_mode="off",
        timestamp_utc="2026-06-22T00:00:00Z",
    )

    assert [row["trial_status"] for row in rows] == list(TRIAL_STATUSES)
    context, sink = _context()
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(
            ohlcv_input_path=f"scratch/{WP_ID}/fixtures/unused.csv"
        ),
        tool_context=context,
        repo_root=tmp_path,
    )
    target = f"scratch/{WP_ID}/outputs/run/denominator_ledger.json"
    bridge._assert_denominator(rows, manifest, target_path=target)
    with pytest.raises(BlockedActionError):
        bridge._assert_denominator(rows[:-1], manifest, target_path=target)
    assert sink.records[-1].action_type == "evidence_suppression"
    assert sink.records[-1].decision == "blocked"


@pytest.mark.parametrize(
    "action_type,target_path",
    [
        ("write_scratch", "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json"),
        ("write_scratch", "research/variant_manifests/VM-9999.variant_manifest.json"),
        ("write_scratch", "research/sweep_plans/SWEEP-PLAN-9999.sweep_plan.json"),
        ("write_scratch", "research/result_populations/RP-9999.result_population.json"),
        ("trial_log_mutation", "research/trial_log.jsonl"),
        ("candidate_promotion", "research/candidate_registry.jsonl"),
        ("candidate_registration", "research/candidate_registry.jsonl"),
        ("candidate_freeze", "research/candidate_registry.jsonl"),
        ("runtime_control", "src/runtime/paper_trader.py"),
        ("oms_access", "src/oms/state.py"),
        ("risk_control", "src/risk/caps.py"),
        ("reconciliation_control", "src/reconciliation/state.py"),
        ("capital_access", "src/capital/state.py"),
        ("private_endpoint_access", "exchange/private"),
        ("credential_access", ".env"),
        ("funding_mode_mutation", "configs/research.json"),
        ("evidence_suppression", "scratch/evidence.json"),
        ("evidence_deletion", "scratch/evidence.json"),
        ("toolcontext_bypass", "tools/agent_sandbox"),
        ("network_access", "provider/network"),
        (RUN_NONCANONICAL_OFFLINE_SWEEP, "scratch/other/outputs/run.json"),
    ],
)
def test_adversarial_actions_are_blocked_and_audited(action_type: str, target_path: str):
    context, sink = _context()

    with pytest.raises(BlockedActionError):
        context.require_allowed(ToolAction(action_type, target_path))
    assert sink.records[-1].decision == "blocked"
    assert sink.records[-1].action_type == action_type


def test_bridge_source_has_no_provider_or_network_client():
    source = (REPO_ROOT / "tools/research_agents/formalizer_runner_bridge.py").read_text()
    for forbidden in ("requests", "httpx", "urllib", "OpenAI", "Anthropic", "socket"):
        assert forbidden not in source
