"""Tests for the inert, default-off research-lab scheduler shell.

These tests prove the package's required guarantees (§7):

- the default config disables every autonomous capability,
- a dry-run produces a no-op summary only (nothing is executed),
- the committed run-queue fixture validates against the schema,
- no write-capable action is exposed by the shell,
- runtime / paper / live flags remain ``False``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.lab_scheduler_shell import config as cfg
from tools.lab_scheduler_shell import model
from tools.lab_scheduler_shell.config import (
    DEFAULT_OFF_FLAGS,
    SchedulerConfigError,
    SchedulerShellConfig,
    default_config,
    validate_default_off,
)
from tools.lab_scheduler_shell.shell import (
    SCHEDULER_NON_AUTHORITY,
    SchedulerShell,
    plan_dry_run,
)
from tools.lab_state.resolver import REPO_ROOT
from tools.lab_state.run import SUBJECTS

FIXTURE = (
    REPO_ROOT
    / "scratch"
    / "WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01"
    / "run_queue_fixture.json"
)


# ---------------------------------------------------------------------------
# Default-off configuration.
# ---------------------------------------------------------------------------
def test_default_config_disables_all_autonomous_behavior() -> None:
    config = default_config()
    flags = config.as_dict()
    # Every required default-off guarantee is present and False.
    for name in DEFAULT_OFF_FLAGS:
        assert name in flags, f"missing default-off flag {name}"
        assert flags[name] is False, f"{name} must default to False"
    assert config.any_enabled() is False
    assert config.enabled_flags() == ()


def test_runtime_and_paper_live_flags_remain_false() -> None:
    config = default_config()
    assert config.runtime_contact_enabled is False
    assert config.paper_live_contact_enabled is False
    decl = SCHEDULER_NON_AUTHORITY
    assert decl["contacts_runtime"] is False
    assert decl["contacts_paper_or_live"] is False
    assert decl["authorizes_paper_live_runtime"] is False


def test_validate_default_off_passes_for_default() -> None:
    result = validate_default_off(default_config())
    assert result["all_default_off"] is True
    assert result["enabled_flags"] == []
    assert result["missing_flags"] == []
    assert set(result["checked_flags"]) == set(DEFAULT_OFF_FLAGS)


def test_assert_default_off_raises_when_a_flag_is_enabled() -> None:
    # A hand-built "enabled" config is rejected by the assertion helper; this
    # proves the guardrail detects a non-inert posture (the shell still has no
    # executor regardless).
    enabled = SchedulerShellConfig(autonomous_enabled=True, run_triggering_enabled=True)
    result = validate_default_off(enabled)
    assert result["all_default_off"] is False
    assert "autonomous_enabled" in result["enabled_flags"]
    with pytest.raises(SchedulerConfigError):
        cfg.assert_default_off(enabled)


def test_config_is_frozen() -> None:
    config = default_config()
    with pytest.raises(Exception):
        config.autonomous_enabled = True  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Queue fixture validation.
# ---------------------------------------------------------------------------
def test_committed_queue_fixture_validates() -> None:
    shell = SchedulerShell.from_fixture(FIXTURE)
    assert shell.queue.schema_version == model.SCHEMA_VERSION
    assert len(shell.queue.entries) == 4
    # Every entry binds to a real committed lab subject.
    known = {s["subject_id"] for s in SUBJECTS.values()}
    for entry in shell.queue.entries:
        assert entry.subject_id in known
        assert model.is_valid_status(entry.status)


def test_queue_rejects_unknown_status() -> None:
    raw = {
        "schema_version": model.SCHEMA_VERSION,
        "entries": [
            {
                "run_id": "X1",
                "subject_id": "",
                "target_stage": "",
                "status": "running",  # not in the inert vocabulary
            }
        ],
    }
    with pytest.raises(model.QueueValidationError):
        model.build_queue(raw, known_subject_ids=frozenset())


def test_queue_rejects_unknown_subject_and_bad_dependency() -> None:
    raw = {
        "schema_version": model.SCHEMA_VERSION,
        "entries": [
            {
                "run_id": "X1",
                "subject_id": "NOT-A-SUBJECT",
                "target_stage": "robustness",
                "status": "queued",
                "depends_on": ["MISSING"],
            }
        ],
    }
    with pytest.raises(model.QueueValidationError):
        model.build_queue(raw, known_subject_ids=frozenset({"REAL"}))


def test_queue_rejects_wrong_schema_version() -> None:
    with pytest.raises(model.QueueValidationError):
        model.build_queue(
            {"schema_version": "nope", "entries": []}, known_subject_ids=frozenset()
        )


def test_block_and_retry_states_are_surfaced() -> None:
    shell = SchedulerShell.from_fixture(FIXTURE)
    status = shell.queue_status()
    blocked = [e for e in status["entries"] if e["status"] == "blocked"]
    assert blocked, "fixture should exercise a blocked entry"
    codes = {e["retry"]["block_reason_code"] for e in blocked}
    assert codes <= set(model.BLOCK_REASON_CODES)
    assert "SCHED_RETRY_BUDGET_EXHAUSTED" in codes
    # Retry states are visible (recorded, never executed).
    retry_states = {e["retry"]["state"] for e in status["entries"]}
    assert retry_states <= set(model.RETRY_STATES)
    assert {"scheduled", "exhausted"} <= retry_states


# ---------------------------------------------------------------------------
# Dry-run no-op behavior.
# ---------------------------------------------------------------------------
def test_dry_run_produces_noop_summary_only() -> None:
    shell = SchedulerShell.from_fixture(FIXTURE)
    plan = shell.dry_run()
    assert plan["dry_run"] is True
    assert plan["executed_any_action"] is False
    assert plan["all_actions_noop"] is True
    assert plan["planned_action_count"] == plan["noop_action_count"]
    assert plan["noop_reason_code"] == "SCHED_AUTONOMY_DISABLED"
    for action in plan["planned_actions"]:
        assert action["executed"] is False
        assert action["action_kind"] == "no_op"


def test_dry_run_is_noop_even_if_a_config_were_enabled() -> None:
    # Defense in depth: planning over an "enabled" config still executes nothing,
    # because the shell has no executor. The reason advances but no action runs.
    shell = SchedulerShell.from_fixture(FIXTURE)
    enabled = SchedulerShellConfig(autonomous_enabled=True, run_triggering_enabled=True)
    plan = plan_dry_run(shell.queue, enabled)
    assert plan["executed_any_action"] is False
    assert plan["all_actions_noop"] is True
    assert plan["config_default_off"] is False
    assert plan["noop_reason_code"] == "SCHED_NO_EXECUTOR_PRESENT"
    # The emitted reason is a declared contract code.
    assert plan["noop_reason_code"] in model.NOOP_REASON_CODES
    assert plan["noop_reason_code"] in model.BLOCK_REASON_CODES


def test_no_executor_present_reason_is_declared() -> None:
    # The no-executor no-op reason must be part of the reason-code contract.
    assert "SCHED_NO_EXECUTOR_PRESENT" in model.BLOCK_REASON_CODES
    assert "SCHED_NO_EXECUTOR_PRESENT" in model.NOOP_REASON_CODES


def test_noop_reason_codes_are_declared() -> None:
    # Every noop_reason_code plan_dry_run can emit must be declared in the
    # scheduler-shell reason-code contract, across all config postures.
    shell = SchedulerShell.from_fixture(FIXTURE)
    postures = [
        SchedulerShellConfig(),  # default-off
        SchedulerShellConfig(autonomous_enabled=True),  # run-triggering still off
        SchedulerShellConfig(
            autonomous_enabled=True, run_triggering_enabled=True
        ),  # both on -> no-executor
    ]
    emitted = {plan_dry_run(shell.queue, p)["noop_reason_code"] for p in postures}
    assert emitted == {
        "SCHED_AUTONOMY_DISABLED",
        "SCHED_RUN_TRIGGERING_DISABLED",
        "SCHED_NO_EXECUTOR_PRESENT",
    }
    # Contract: the emitted set is exactly the declared NOOP subset, and each is
    # also a declared block reason code.
    assert emitted == set(model.NOOP_REASON_CODES)
    for code in emitted:
        assert code in model.BLOCK_REASON_CODES


def test_terminal_entries_plan_no_action() -> None:
    shell = SchedulerShell.from_fixture(FIXTURE)
    plan = shell.dry_run()
    terminal = [a for a in plan["planned_actions"] if a["skipped_terminal"]]
    assert terminal, "fixture has blocked (terminal) entries"
    for action in terminal:
        assert action["would_be_action"] == "none"
        assert action["executed"] is False


# ---------------------------------------------------------------------------
# No write-capable action exposed.
# ---------------------------------------------------------------------------
def test_no_write_capable_action_is_exposed() -> None:
    shell = SchedulerShell.from_fixture(FIXTURE)
    # The shell exposes only read-only views and a no-op planner.
    public = {n for n in dir(shell) if not n.startswith("_")}
    forbidden_verbs = (
        "create",
        "trigger",
        "execute",
        "run_now",
        "retry",
        "notify",
        "fire",
        "promote",
        "approve",
        "write",
        "commit",
        "submit",
        "enable",
    )
    offenders = {
        name
        for name in public
        for verb in forbidden_verbs
        if verb in name.lower()
    }
    assert offenders == set(), f"shell exposes write-capable-looking methods: {offenders}"
    decl = SCHEDULER_NON_AUTHORITY
    for guarantee in (
        "is_a_scheduler_service",
        "has_cron_or_ci_trigger",
        "has_background_daemon",
        "creates_runs",
        "generates_strategies",
        "executes_retries",
        "fires_notifications",
        "writes_approval_or_candidate_lifecycle",
        "contacts_runtime",
        "contacts_paper_or_live",
        "has_executor",
    ):
        assert decl[guarantee] is False


def test_snapshot_is_deterministic_and_holds_edge_search() -> None:
    first = SchedulerShell.from_fixture(FIXTURE).snapshot()
    second = SchedulerShell.from_fixture(FIXTURE).snapshot()
    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert "No further edge-search is authorized" in first["edge_search_hold"]
    assert first["default_off_config"]["edge_search_enabled"] is False


def test_run_queue_fixture_file_is_well_formed_json() -> None:
    raw = json.loads(Path(FIXTURE).read_text(encoding="utf-8"))
    assert raw["schema_version"] == model.SCHEMA_VERSION
    assert isinstance(raw["entries"], list) and raw["entries"]
