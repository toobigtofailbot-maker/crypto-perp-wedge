"""Run the scratch-only notification and approval queue pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from tools.notifications_poc.approval_models import (
    NON_AUTHORITY_FLAGS,
    ApprovalRequest,
    NotificationEvent,
    non_authority_flag_map,
)
from tools.notifications_poc.notifier import LocalLogNotifier, probe_apprise


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ID = "WP-PILOT-NOTIFICATIONS-APPROVALS-01"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / PACKAGE_ID
DEFAULT_CREATED_AT_UTC = "2026-06-20T00:00:00Z"


class NotificationsApprovalsPilotError(RuntimeError):
    """Raised when the pilot cannot run within its dry-run boundary."""


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _run_git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        return "unknown"
    return completed.stdout.strip() or "unknown"


def _assert_scratch_output(output_dir: Path) -> Path:
    resolved = output_dir.resolve()
    scratch_root = (REPO_ROOT / "scratch").resolve()
    if resolved == scratch_root or scratch_root not in resolved.parents:
        raise NotificationsApprovalsPilotError("output-dir must remain under scratch/")
    return resolved


def _evidence_links(output_dir: Path) -> list[str]:
    base = _repo_relative(output_dir)
    return [
        "docs/status_entries/WP-LAB-DASHBOARD-EXPANSION-01.md",
        "docs/status_entries/WP-LAB-IDEA-INTAKE-FORMALIZATION-01.md",
        f"{base}/blocked_action_report.json",
        f"{base}/issueops_dry_run_payload.json",
    ]


def _approval_request(created_at_utc: str, output_dir: Path) -> ApprovalRequest:
    return ApprovalRequest(
        approval_id="APR-PILOT-0001",
        request_type="candidate_manual_review",
        requested_by=PACKAGE_ID,
        required_human=True,
        status="pending",
        evidence_links=_evidence_links(output_dir),
        non_authority_flags=list(NON_AUTHORITY_FLAGS),
        created_at_utc=created_at_utc,
        updated_at_utc=created_at_utc,
    )


def _blocked_action_report(created_at_utc: str) -> dict[str, Any]:
    attempts = [
        ("canonical-write-attempt", "canonical write attempt", "blocked_not_canonical_write"),
        ("candidate-promotion-attempt", "candidate promotion attempt", "blocked_not_candidate_promotion"),
        ("paper-live-activation-attempt", "paper/live activation attempt", "blocked_not_paper_live"),
        ("private-credential-api-attempt", "private credential/API attempt", "blocked_no_credentials_or_api"),
    ]
    return {
        "package_id": PACKAGE_ID,
        "created_at_utc": created_at_utc,
        "dry_run": True,
        "blocked_action_count": len(attempts),
        "non_authority_flags": non_authority_flag_map(),
        "blocked_actions": [
            {
                "attempt_id": attempt_id,
                "attempt_kind": attempt_kind,
                "status": "blocked",
                "block_reason": reason,
                "authority_granted": False,
                "created_at_utc": created_at_utc,
            }
            for attempt_id, attempt_kind, reason in attempts
        ],
    }


def _issueops_payload(approval: dict[str, Any], created_at_utc: str) -> dict[str, Any]:
    return {
        "package_id": PACKAGE_ID,
        "dry_run": True,
        "github_write_performed": False,
        "issueops_model": "dry_run_issue_payload_v1",
        "created_at_utc": created_at_utc,
        "issue": {
            "title": f"{PACKAGE_ID}: manual approval required for candidate review",
            "body": "\n".join(
                [
                    "Scratch-only dry-run IssueOps approval request.",
                    "No GitHub issue was created by this pilot.",
                    "Human approval remains pending outside this artifact.",
                ]
            ),
            "labels": [
                "approval-request",
                "manual-review-required",
                "dry-run",
                "scratch-only",
            ],
            "assignees": [],
        },
        "approval_ref": approval["approval_id"],
        "status_transition_policy": {
            "pending_to_approved_requires_human_comment": True,
            "agent_can_approve": False,
            "label_alone_is_not_execution_authority": True,
            "no_auto_approval": True,
        },
        "non_authority_flags": non_authority_flag_map(),
    }


def _notification_event(created_at_utc: str, output_dir: Path) -> NotificationEvent:
    return NotificationEvent(
        event_id="NOTIF-PILOT-0001",
        severity="blocked",
        channel_kind="local_jsonl_noop",
        dry_run=True,
        message=(
            "Research job completed with blockers; candidate requires manual approval; "
            "forbidden action attempts were blocked."
        ),
        evidence_links=_evidence_links(output_dir),
        requires_action=True,
        created_at_utc=created_at_utc,
    )


def _recommendation_report(dependency_probe: dict[str, Any]) -> str:
    if dependency_probe["real_apprise_exercised"]:
        apprise_answer = (
            "Conditional yes. Apprise was imported and exercised through a real "
            "apprise.Apprise object using a local in-process decorator target. "
            "No external notification, network service URL, credential, or "
            "GitHub write was used."
        )
    elif dependency_probe["import_available"]:
        apprise_answer = (
            "Conditional yes. Apprise is importable in this environment, but "
            "real behavior was not requested in this default local JSONL run."
        )
    else:
        apprise_answer = (
            "Conditional yes, subject to a later dependency decision. Apprise "
            "is not importable here, so behavior was not exercised."
        )
    return "\n".join(
        [
            f"# {PACKAGE_ID} Recommendation Report",
            "",
            "## Decision",
            "",
            "- Recommendation: `ADOPT_CANDIDATE_CONDITIONAL` for notification transport and IssueOps-shaped approval queues.",
            "- Scope: scratch-only, advisory, dry-run.",
            f"- Apprise version: `{dependency_probe['apprise_version']}`.",
            f"- Real Apprise exercised: `{str(dependency_probe['real_apprise_exercised']).lower()}`.",
            f"- Apprise delivery mode: `{dependency_probe['apprise_delivery_mode']}`.",
            "- External notification sent: `false`.",
            "- Credentials used: `false`.",
            "- GitHub write performed: `false`.",
            "- Dependency files touched: `false`.",
            "",
            "## Required Questions",
            "",
            f"- Can Apprise be adopted as notification transport? {apprise_answer}",
            "- Can GitHub IssueOps serve as approval queue? Conditional yes for human-readable queue shape, audit labels, comments, and manual status transitions; no GitHub write was performed here.",
            "- What exact repo-owned adapter would be needed? A repo-owned dry-run-first notification adapter, an allowlisted Apprise URL loader, a local audit log writer, and a GitHub IssueOps payload builder with write calls disabled by default and separately authorized.",
            "- What remains mocked? Apprise delivery, GitHub issue creation, label/comment ingestion, human identity verification, and any transition from pending to approved/rejected.",
            "- What future agent-phase pieces would consume this? Bounded research agents, lab monitors, blocked-action reporters, manual gate queues, and future research-to-shadow handoff packets.",
            "- What are the stop conditions? Real credentials, non-local URLs, GitHub write APIs, automatic approval, execution hooks, canonical writes, candidate promotion, paper/live activation, runtime/OMS/risk/reconciliation contact, or dependency-file mutation.",
            "",
            "## Boundary",
            "",
            "- One-way notification only.",
            "- Human approval remains pending.",
            "- This pilot grants no approval, execution, promotion, paper/live, runtime, or canonical-write authority.",
            "",
        ]
    )


def _readme() -> str:
    return "\n".join(
        [
            f"# {PACKAGE_ID}",
            "",
            "Scratch-only Apprise plus IssueOps approval-queue pilot.",
            "",
            "Run:",
            "",
            "```powershell",
            "python -m tools.notifications_poc.run_notifications_approvals_poc --output-dir scratch/WP-PILOT-NOTIFICATIONS-APPROVALS-01 --dry-run",
            "python -m tools.notifications_poc.run_notifications_approvals_poc --output-dir scratch/WP-PILOT-NOTIFICATIONS-APPROVALS-01 --dry-run --exercise-apprise",
            "```",
            "",
            "All outputs are local dry-run artifacts. The pilot does not send real notifications, create GitHub issues, use credentials, write canonical state, approve candidates, or touch paper/live/runtime paths.",
            "",
        ]
    )


def run_pilot(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    dry_run: bool = True,
    created_at_utc: str = DEFAULT_CREATED_AT_UTC,
    exercise_apprise: bool = False,
) -> dict[str, Any]:
    if dry_run is not True:
        raise NotificationsApprovalsPilotError("this pilot only supports --dry-run")

    output_dir = _assert_scratch_output(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    notification_log = output_dir / "notification_log.jsonl"
    if notification_log.exists():
        notification_log.unlink()

    dependency_probe = probe_apprise(exercise=exercise_apprise)
    approval = _approval_request(created_at_utc, output_dir).to_dict()
    blocked_report = _blocked_action_report(created_at_utc)
    issueops_payload = _issueops_payload(approval, created_at_utc)
    notification = _notification_event(created_at_utc, output_dir).to_dict()

    notifier = LocalLogNotifier(notification_log)
    notifier.notify(notification)

    artifacts = {
        "README.md": _readme(),
        "approval_queue_sample.json": approval,
        "issueops_dry_run_payload.json": issueops_payload,
        "blocked_action_report.json": blocked_report,
        "recommendation_report.md": _recommendation_report(dependency_probe),
        "dependency_probe.json": dependency_probe,
        "requirements.poc.txt": "apprise  # optional; not added to repo dependency files\n",
    }
    for name, payload in artifacts.items():
        path = output_dir / name
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8", newline="\n")
        else:
            _write_json(path, payload)

    artifact_paths = [
        output_dir / "README.md",
        notification_log,
        output_dir / "approval_queue_sample.json",
        output_dir / "issueops_dry_run_payload.json",
        output_dir / "blocked_action_report.json",
        output_dir / "recommendation_report.md",
        output_dir / "dependency_probe.json",
        output_dir / "requirements.poc.txt",
    ]
    provenance = {
        "package_id": PACKAGE_ID,
        "created_at_utc": created_at_utc,
        "source_commit": _run_git("rev-parse", "HEAD"),
        "source_branch": _run_git("branch", "--show-current"),
        "dry_run": True,
        "github_write_performed": False,
        "real_notification_sent": False,
        "external_notification_sent": False,
        "credential_access_attempted": False,
        "credentials_used": False,
        "dependency_files_touched": False,
        "apprise_import_available": dependency_probe["apprise_import_available"],
        "apprise_version": dependency_probe["apprise_version"],
        "real_apprise_exercised": dependency_probe["real_apprise_exercised"],
        "apprise_delivery_mode": dependency_probe["apprise_delivery_mode"],
        "recommendation": dependency_probe["recommendation"],
        "non_authority_flags": non_authority_flag_map(),
        "artifacts": [
            {"path": _repo_relative(path), "sha256": _sha256_file(path)}
            for path in artifact_paths
        ],
    }
    _write_json(output_dir / "provenance.json", provenance)
    return provenance


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dry-run", action="store_true", required=True)
    parser.add_argument("--created-at-utc", default=DEFAULT_CREATED_AT_UTC)
    parser.add_argument(
        "--exercise-apprise",
        action="store_true",
        help=(
            "Exercise real Apprise through a local in-process no-network target; "
            "requires Apprise to be importable in the active Python environment."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        provenance = run_pilot(
            output_dir=args.output_dir,
            dry_run=args.dry_run,
            created_at_utc=args.created_at_utc,
            exercise_apprise=args.exercise_apprise,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "package_id": provenance["package_id"],
                "output_dir": _repo_relative(args.output_dir),
                "artifact_count": len(provenance["artifacts"]),
                "dry_run": provenance["dry_run"],
                "github_write_performed": provenance["github_write_performed"],
                "real_notification_sent": provenance["real_notification_sent"],
                "real_apprise_exercised": provenance["real_apprise_exercised"],
                "apprise_delivery_mode": provenance["apprise_delivery_mode"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
