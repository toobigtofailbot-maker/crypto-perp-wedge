from __future__ import annotations

from pathlib import Path

import pytest

from tools.agent_sandbox import BlockedActionError, MemoryAuditSink, ToolContext
from tools.lab_pipeline.adapter_contract import build_adapter_registry
from tools.research_agents.formalizer_runner_bridge import (
    APPROVAL_SCOPE,
    ROLE,
    WP_ID,
    FormalizerRunnerBridge,
    FormalizerRunnerBridgeConfig,
    FormalizerRunnerBridgeError,
)


PACKAGE_ID = "WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03"


def _context(wp_id: str = WP_ID) -> tuple[ToolContext, MemoryAuditSink]:
    sink = MemoryAuditSink()
    return ToolContext(wp_id=wp_id, role=ROLE, audit_sink=sink), sink


def test_bridge_adapter_registry_records_hard_blocker() -> None:
    registry = {record.stage: record for record in build_adapter_registry(PACKAGE_ID)}
    bridge = registry["bridge_spec_variant_sweep_preparation"]

    assert bridge.implementation_status == "blocked"
    assert bridge.authority_flags.scratch_only is True
    assert bridge.authority_flags.writes_canonical_evidence is False
    assert "ToolContext WP allowlist" in str(bridge.blocker_reason)
    assert "source formalizer scratch prefixes" in str(bridge.blocker_reason)
    assert "legacy operator approval shape" in str(bridge.blocker_reason)


def test_existing_bridge_rejects_lab_pipeline_package_toolcontext(tmp_path: Path) -> None:
    context, _ = _context(PACKAGE_ID)

    with pytest.raises(ValueError, match="exact ToolContext role and WP"):
        FormalizerRunnerBridge(
            config=FormalizerRunnerBridgeConfig(ohlcv_input_path="scratch/fixture.csv"),
            tool_context=context,
            repo_root=tmp_path,
        )


def test_existing_bridge_output_root_is_not_package_local(tmp_path: Path) -> None:
    context, _ = _context()
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(ohlcv_input_path="scratch/fixture.csv"),
        tool_context=context,
        repo_root=tmp_path,
    )

    assert bridge.output_root.as_posix() == f"scratch/{WP_ID}/outputs"
    assert not bridge.output_root.as_posix().startswith(f"scratch/{PACKAGE_ID}/")


def test_existing_bridge_rejects_package_local_formalizer_prefix(tmp_path: Path) -> None:
    context, _ = _context()
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(ohlcv_input_path="scratch/fixture.csv"),
        tool_context=context,
        repo_root=tmp_path,
    )
    formalized = {
        "schema_version": "agent_formalized_idea_v1",
        "run_id": "labbridge0001",
        "status": "accepted",
        "research_object": {
            "symbols": ["BTCUSDT"],
            "timeframe": "15m",
            "features": ["sma", "stddev"],
        },
        "draft_strategy_spec": {
            "produced": True,
            "path": f"scratch/{PACKAGE_ID}/outputs/labbridge0001/STRAT-SPEC-9001.strategy_spec.json",
        },
        "non_authority": {"scratch_only": True},
    }

    with pytest.raises(FormalizerRunnerBridgeError, match="scoped scratch artifact"):
        bridge._validate_formalizer_contract(
            f"scratch/{PACKAGE_ID}/outputs/labbridge0001/formalized_idea.json",
            formalized,
        )


def test_existing_bridge_rejects_karl_hash_bound_approval_shape(tmp_path: Path) -> None:
    context, sink = _context()
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(ohlcv_input_path="scratch/fixture.csv"),
        tool_context=context,
        repo_root=tmp_path,
    )
    approval = {
        "schema_version": "lab_pipeline_bridge_adapter_approval_v1",
        "approved_by": "Karl",
        "approval_scope": APPROVAL_SCOPE,
        "approval_statement": "Approve exact noncanonical bridge preparation only.",
        "approval_timestamp_utc": "2026-07-08T00:00:00Z",
        "approved_for_noncanonical_runner_bridge": True,
        "source_formalizer_run_id": "labbridge0001",
        "authorizes_bridge_spec_variant_sweep_preparation": True,
        "authorizes_runner_execution": False,
        "authorizes_canonical_write": False,
    }

    with pytest.raises(BlockedActionError):
        bridge._require_approval(
            approval,
            source_run_id="labbridge0001",
            approval_path=(
                "scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/"
                "labbridge0001/operator_bridge_approval.json"
            ),
            formalizer_path=(
                "scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/"
                "labbridge0001/formalized_idea.json"
            ),
        )
    assert sink.records[-1].action_type == "approval_gate_bypass"
    assert sink.records[-1].decision == "blocked"
