from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from tools.agent_sandbox import (
    BlockedActionError,
    JsonLinesAuditSink,
    MemoryAuditSink,
    POLICY_ID,
    ROLE_PERMISSIONS,
    ToolAction,
    ToolContext,
)


FIXED_TIME = datetime(2026, 6, 21, 12, 34, 56, tzinfo=timezone.utc)
WP_ID = "WP-AGENT-TOOLCONTEXT-SANDBOX-01"


def make_context(role: str = "research_scout") -> tuple[ToolContext, MemoryAuditSink]:
    sink = MemoryAuditSink()
    context = ToolContext(wp_id=WP_ID, role=role, audit_sink=sink, clock=lambda: FIXED_TIME)
    return context, sink


class FakeAgentHarness:
    """Test harness whose fixed file tool delegates through ToolContext."""

    def __init__(self, context: ToolContext, repo_root: Path) -> None:
        self.__context = context
        self.__repo_root = repo_root

    def write_text(self, target_path: str, content: str) -> None:
        action = ToolAction("write_scratch", target_path)
        self.__context.run_allowed(
            action,
            lambda: (self.__repo_root / target_path).write_text(content, encoding="utf-8"),
        )


def test_allowed_safe_document_read_passes_and_is_audited():
    context, sink = make_context()

    result = context.run_allowed(
        ToolAction("read_repo_docs", "docs/status_entries/WP-LAB-AGENT-BOUNDARY-DESIGN-01.md"),
        lambda: "contents",
    )

    assert result == "contents"
    assert sink.records[0].decision == "allowed"


def test_allowed_active_wp_scratch_write_passes():
    context, sink = make_context("draft_generator")

    result = context.run_allowed(
        ToolAction("write_scratch", f"scratch/{WP_ID}/drafts/advisory.md"),
        lambda: "written",
    )

    assert result == "written"
    assert sink.records[0].decision == "allowed"


def test_repo_truth_role_taxonomy_and_role_specific_permissions_are_enforced():
    assert set(ROLE_PERMISSIONS) == {
        "research_scout",
        "idea_formalizer",
        "draft_generator",
        "non_canonical_runner",
        "robustness_diagnostician",
        "candidate_review_packet_preparer",
        "notification_assistant",
    }
    scout_context, scout_sink = make_context("research_scout")
    runner_context, runner_sink = make_context("non_canonical_runner")

    with pytest.raises(BlockedActionError, match="does not allow"):
        scout_context.require_allowed(
            ToolAction("write_scratch", f"scratch/{WP_ID}/drafts/scout.md")
        )
    runner_context.require_allowed(
        ToolAction("run_read_only_validation", "tools/registry/validate_strategy_specs.py")
    )

    assert scout_sink.records[-1].decision == "blocked"
    assert runner_sink.records[-1].decision == "allowed"


@pytest.mark.parametrize(
    ("action_type", "target_path"),
    [
        ("write_scratch", "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json"),
        ("write_scratch", "research/result_populations/RP-9999.result_population.json"),
        ("candidate_promotion", "research/candidate_registry.jsonl"),
        ("candidate_freeze", "research/candidate_registry.jsonl"),
        ("candidate_registration", "research/candidate_registry.jsonl"),
        ("trial_log_mutation", "research/trial_log.jsonl"),
        ("overlay_control", "src/overlay/controller.py"),
        ("execution_control", "src/execution/controller.py"),
        ("risk_control", "src/risk/caps.py"),
        ("capital_access", "src/capital/allocation.py"),
        ("runtime_control", "runtime/runner.py"),
        ("paper_control", "paper/runner.py"),
        ("live_control", "live/runner.py"),
        ("dependency_mutation", "requirements.txt"),
        ("credential_access", ".env"),
        ("private_endpoint_access", "exchange/private/orders"),
        ("network_access", "public.example/api"),
        ("project_status_mutation", "docs/project_status.md"),
    ],
)
def test_hard_prohibitions_are_blocked_and_logged(action_type: str, target_path: str):
    context, sink = make_context("non_canonical_runner")

    with pytest.raises(BlockedActionError) as exc_info:
        context.run_allowed(ToolAction(action_type, target_path), lambda: "must not run")

    record = sink.records[0]
    assert exc_info.value.record is record
    assert record.timestamp_utc == "2026-06-21T12:34:56Z"
    assert record.wp_id == WP_ID
    assert record.role == "non_canonical_runner"
    assert record.action_type == action_type
    assert record.target_path == target_path.casefold()
    assert record.decision == "blocked"
    assert "prohibition" in record.reason
    assert record.policy_id == POLICY_ID
    assert "no canonical" in record.non_authority


@pytest.mark.parametrize("role", sorted(ROLE_PERMISSIONS))
@pytest.mark.parametrize(
    ("action_type", "target_path"),
    [
        ("canonical_write", "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json"),
        ("candidate_registration", "research/candidate_registry.jsonl"),
        ("runtime_control", "src/runtime/paper_trader.py"),
        ("credential_access", "secrets/exchange.key"),
    ],
)
def test_all_configured_roles_inherit_hard_prohibitions(
    role: str, action_type: str, target_path: str
):
    context, sink = make_context(role)

    with pytest.raises(BlockedActionError):
        context.require_allowed(ToolAction(action_type, target_path))

    assert sink.records[-1].decision == "blocked"


def test_fake_agent_harness_cannot_bypass_context_or_mutate_on_block(tmp_path: Path):
    context, sink = make_context("draft_generator")
    harness = FakeAgentHarness(context, tmp_path)
    protected_file = (
        tmp_path / "research" / "strategy_specs" / "STRAT-SPEC-9999.strategy_spec.json"
    )
    protected_file.parent.mkdir(parents=True)
    protected_file.write_text("original\n", encoding="utf-8")

    with pytest.raises(BlockedActionError):
        harness.write_text(
            "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json",
            "mutated\n",
        )

    assert protected_file.read_text(encoding="utf-8") == "original\n"
    assert sink.records[-1].decision == "blocked"


def test_fake_agent_harness_routes_allowed_scratch_write(tmp_path: Path):
    context, sink = make_context("draft_generator")
    harness = FakeAgentHarness(context, tmp_path)
    target_path = f"scratch/{WP_ID}/drafts/advisory.md"
    (tmp_path / target_path).parent.mkdir(parents=True)

    harness.write_text(target_path, "advisory only\n")

    assert (tmp_path / target_path).read_text(encoding="utf-8") == "advisory only\n"
    assert sink.records[-1].decision == "allowed"


def test_closed_default_blocks_unlisted_action_and_out_of_scope_scratch_path():
    context, sink = make_context("draft_generator")

    with pytest.raises(BlockedActionError):
        context.require_allowed(ToolAction("unknown_action", "scratch/elsewhere/output.md"))
    with pytest.raises(BlockedActionError):
        context.require_allowed(ToolAction("write_scratch", "scratch/elsewhere/output.md"))

    assert [record.decision for record in sink.records] == ["blocked", "blocked"]


@pytest.mark.parametrize(
    "target_path",
    [
        "research/trial_log.jsonl",
        "research/candidate_registry.jsonl",
        "docs/project_status.md",
        "requirements.txt",
    ],
)
def test_generic_write_capability_cannot_bypass_hard_path_blocks(target_path: str):
    context, sink = make_context("draft_generator")

    with pytest.raises(BlockedActionError, match="hard prohibition"):
        context.require_allowed(ToolAction("write_scratch", target_path))

    assert sink.records[-1].target_path == target_path
    assert sink.records[-1].decision == "blocked"


def test_jsonlines_audit_sink_serializes_deterministically(tmp_path: Path):
    audit_path = tmp_path / "audit" / "actions.jsonl"
    context = ToolContext(
        wp_id=WP_ID,
        role="research_scout",
        audit_sink=JsonLinesAuditSink(audit_path),
        clock=lambda: FIXED_TIME,
    )

    with pytest.raises(BlockedActionError):
        context.require_allowed(ToolAction("candidate_promotion", "research/candidate_registry.jsonl"))

    assert audit_path.read_text(encoding="utf-8") == (
        '{"action_type":"candidate_promotion","decision":"blocked",'
        '"non_authority":"audit record only; no canonical, candidate-lifecycle, promotion, '
        'paper/live, runtime, or execution authority","policy_id":"bounded-research-agent-v1",'
        '"reason":"hard prohibition: action_type=candidate_promotion",'
        '"role":"research_scout","target_path":"research/candidate_registry.jsonl",'
        '"timestamp_utc":"2026-06-21T12:34:56Z",'
        '"wp_id":"WP-AGENT-TOOLCONTEXT-SANDBOX-01"}\n'
    )


@pytest.mark.parametrize(
    "target_path", ["../docs/project_status.md", "C:/secrets/key.pem", "/etc/passwd"]
)
def test_unsafe_target_paths_are_rejected_before_execution(target_path: str):
    context, sink = make_context()

    with pytest.raises(ValueError, match="safe repo-relative path"):
        context.run_allowed(ToolAction("read_repo_docs", target_path), lambda: None)

    assert sink.records == []
