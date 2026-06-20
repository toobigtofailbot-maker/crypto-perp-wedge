from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.notifications_poc import run_notifications_approvals_poc as subject
from tools.notifications_poc.approval_models import NON_AUTHORITY_FLAGS


def test_pilot_writes_dry_run_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(subject, "REPO_ROOT", tmp_path)
    output_dir = tmp_path / "scratch" / subject.PACKAGE_ID

    provenance = subject.run_pilot(output_dir=output_dir, dry_run=True)

    expected = {
        "README.md",
        "notification_log.jsonl",
        "approval_queue_sample.json",
        "issueops_dry_run_payload.json",
        "blocked_action_report.json",
        "recommendation_report.md",
        "provenance.json",
        "dependency_probe.json",
        "requirements.poc.txt",
    }
    assert {path.name for path in output_dir.iterdir()} == expected
    assert provenance["dry_run"] is True
    assert provenance["github_write_performed"] is False
    assert provenance["real_notification_sent"] is False


def test_approval_queue_remains_pending_and_non_authoritative(tmp_path, monkeypatch):
    monkeypatch.setattr(subject, "REPO_ROOT", tmp_path)
    output_dir = tmp_path / "scratch" / subject.PACKAGE_ID
    subject.run_pilot(output_dir=output_dir, dry_run=True)

    approval = json.loads((output_dir / "approval_queue_sample.json").read_text())

    assert approval["approval_id"] == "APR-PILOT-0001"
    assert approval["required_human"] is True
    assert approval["status"] == "pending"
    assert set(NON_AUTHORITY_FLAGS).issubset(set(approval["non_authority_flags"]))
    assert "approved" not in approval["request_type"]


def test_notification_log_shape(tmp_path, monkeypatch):
    monkeypatch.setattr(subject, "REPO_ROOT", tmp_path)
    output_dir = tmp_path / "scratch" / subject.PACKAGE_ID
    subject.run_pilot(output_dir=output_dir, dry_run=True)

    lines = (output_dir / "notification_log.jsonl").read_text().splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])

    assert event["event_id"] == "NOTIF-PILOT-0001"
    assert event["severity"] == "blocked"
    assert event["channel_kind"] == "local_jsonl_noop"
    assert event["dry_run"] is True
    assert event["requires_action"] is True
    assert event["evidence_links"]


def test_blocked_action_report_demonstrates_required_blocks(tmp_path, monkeypatch):
    monkeypatch.setattr(subject, "REPO_ROOT", tmp_path)
    output_dir = tmp_path / "scratch" / subject.PACKAGE_ID
    subject.run_pilot(output_dir=output_dir, dry_run=True)

    report = json.loads((output_dir / "blocked_action_report.json").read_text())
    kinds = {item["attempt_kind"] for item in report["blocked_actions"]}

    assert kinds == {
        "canonical write attempt",
        "candidate promotion attempt",
        "paper/live activation attempt",
        "private credential/API attempt",
    }
    assert all(item["status"] == "blocked" for item in report["blocked_actions"])
    assert all(item["authority_granted"] is False for item in report["blocked_actions"])
    assert all(report["non_authority_flags"][flag] is True for flag in NON_AUTHORITY_FLAGS)


def test_issueops_payload_is_dry_run_only(tmp_path, monkeypatch):
    monkeypatch.setattr(subject, "REPO_ROOT", tmp_path)
    output_dir = tmp_path / "scratch" / subject.PACKAGE_ID
    subject.run_pilot(output_dir=output_dir, dry_run=True)

    payload = json.loads((output_dir / "issueops_dry_run_payload.json").read_text())

    assert payload["dry_run"] is True
    assert payload["github_write_performed"] is False
    assert payload["status_transition_policy"]["agent_can_approve"] is False
    assert payload["status_transition_policy"]["no_auto_approval"] is True


def test_rejects_non_dry_run_and_non_scratch_output(tmp_path, monkeypatch):
    monkeypatch.setattr(subject, "REPO_ROOT", tmp_path)
    with pytest.raises(subject.NotificationsApprovalsPilotError, match="only supports --dry-run"):
        subject.run_pilot(output_dir=tmp_path / "scratch" / subject.PACKAGE_ID, dry_run=False)
    with pytest.raises(subject.NotificationsApprovalsPilotError, match="scratch"):
        subject.run_pilot(output_dir=tmp_path / "reports", dry_run=True)
