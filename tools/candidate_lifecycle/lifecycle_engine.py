"""Build scratch-only candidate lifecycle reports and review packets.

This module links candidate lifecycle evidence for human review. It does not
write canonical evidence, approve candidates, start paper/live execution, or
create readiness authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CREATED_AT_UTC = "2026-06-20T12:00:00Z"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / "WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01"

LIFECYCLE_STATES = {
    "proposed",
    "in_research",
    "research_concluded",
    "paper_eligible",
    "paper_active",
    "paper_concluded",
    "live_eligible",
    "live_active",
    "halted",
    "archived",
}
ALLOWED_TRANSITIONS = {
    "proposed": {"in_research", "halted"},
    "in_research": {"research_concluded", "halted"},
    "research_concluded": {"paper_eligible", "archived", "halted"},
    "paper_eligible": {"paper_active", "archived", "halted"},
    "paper_active": {"paper_concluded", "halted", "archived"},
    "paper_concluded": {"live_eligible", "archived", "halted"},
    "live_eligible": {"live_active", "archived", "halted"},
    "live_active": {"paper_concluded", "halted", "archived"},
    "halted": {"archived"},
    "archived": set(),
}
HUMAN_GATED_TO_STATES = {"paper_eligible", "paper_active", "live_eligible", "live_active"}
FORBIDDEN_TO_STATES = {"paper_active", "live_eligible", "live_active"}
FORBIDDEN_STATE_ALIASES = {
    "ready_for_live",
    "promoted_live",
    "paper_running",
    "production_live",
}
REQUIRED_NON_AUTHORITY_FLAGS = [
    "human_gated",
    "not_auto_promotion",
    "not_readiness_authority",
    "not_paper_live",
    "not_canonical_evidence_mutation",
    "not_execution_authority",
]
EVIDENCE_FIELDS = [
    "result_population_ref",
    "walkforward_run_ref",
    "robustness_report_ref",
    "dashboard_review_ref",
    "idea_intake_ref",
]
FORBIDDEN_PACKET_PHRASES = [
    "approved",
    "safe to trade",
    "ready for live",
    "auto-promoted",
    "recommended for live",
]


class LifecycleEngineError(ValueError):
    """Raised when lifecycle input cannot be safely processed."""


@dataclass(frozen=True)
class EngineOutputs:
    report: dict[str, Any]
    packet_markdown: str
    provenance: dict[str, Any]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _stable_payload_hash(payload: dict[str, Any]) -> str:
    return _sha256_bytes(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _source_commit(repo_root: Path = REPO_ROOT) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return "unknown"
    return completed.stdout.strip()


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _evidence_refs(candidate: dict[str, Any]) -> dict[str, Any]:
    evidence = candidate.get("evidence_refs")
    if not isinstance(evidence, dict):
        return {}
    return {field: evidence.get(field) for field in EVIDENCE_FIELDS}


def _missing_required_evidence(candidate: dict[str, Any], requested_to_state: str) -> list[str]:
    evidence = _evidence_refs(candidate)
    required = ["idea_intake_ref"]
    if requested_to_state in {"research_concluded", "paper_eligible", "archived", "halted"}:
        required.append("result_population_ref")
    if requested_to_state == "paper_eligible":
        required.extend(["walkforward_run_ref", "dashboard_review_ref"])
    return [field for field in required if not evidence.get(field)]


def _optional_missing_evidence(candidate: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    evidence = _evidence_refs(candidate)
    if not evidence.get("robustness_report_ref"):
        missing.append("robustness_report_ref")
    return missing


def _has_forbidden_authority_request(candidate: dict[str, Any], requested_to_state: str) -> list[str]:
    blockers: list[str] = []
    for key in ("auto_promote", "mark_ready_for_live", "start_paper", "start_live", "mutate_evidence"):
        if candidate.get(key) is True:
            blockers.append(f"forbidden authority request: {key}=true")
    if requested_to_state in FORBIDDEN_TO_STATES or requested_to_state in FORBIDDEN_STATE_ALIASES:
        blockers.append(f"forbidden lifecycle target for this engine: {requested_to_state}")
    return blockers


def _validate_input(payload: dict[str, Any]) -> None:
    if payload.get("schema_version") != "candidate_lifecycle_engine_input.v1":
        raise LifecycleEngineError("schema_version must be candidate_lifecycle_engine_input.v1")
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise LifecycleEngineError("input must contain at least one candidate")
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise LifecycleEngineError("candidate entries must be objects")
        candidate_id = candidate.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            raise LifecycleEngineError("candidate_id is required")
        current_state = candidate.get("current_state")
        requested_to_state = candidate.get("requested_transition", {}).get("to_state")
        if current_state not in LIFECYCLE_STATES:
            raise LifecycleEngineError(f"{candidate_id}: unknown current_state {current_state}")
        if requested_to_state not in LIFECYCLE_STATES and requested_to_state not in FORBIDDEN_STATE_ALIASES:
            raise LifecycleEngineError(f"{candidate_id}: unknown requested to_state {requested_to_state}")


def _candidate_report(candidate: dict[str, Any]) -> dict[str, Any]:
    candidate_id = candidate["candidate_id"]
    current_state = candidate["current_state"]
    transition = candidate.get("requested_transition", {})
    requested_to_state = transition.get("to_state")
    blockers = list(_as_list(candidate.get("blockers")))
    blockers.extend(_has_forbidden_authority_request(candidate, str(requested_to_state)))

    allowed = requested_to_state in ALLOWED_TRANSITIONS.get(current_state, set())
    if not allowed and requested_to_state in LIFECYCLE_STATES:
        blockers.append(f"transition not allowed by repo lifecycle vocabulary: {current_state}->{requested_to_state}")

    missing_required = _missing_required_evidence(candidate, str(requested_to_state))
    for field in missing_required:
        blockers.append(f"missing required evidence: {field}")

    missing_optional = _optional_missing_evidence(candidate)
    unavailable_optional = sorted(set(_as_list(candidate.get("unavailable_optional_evidence"))))
    missing_evidence = sorted(set(missing_required + missing_optional))
    if "robustness_report_ref" in unavailable_optional and "robustness_report_ref" in missing_evidence:
        missing_evidence.remove("robustness_report_ref")

    if blockers:
        pending_state = "blocked"
    elif requested_to_state in HUMAN_GATED_TO_STATES:
        pending_state = "human_approval_required"
    else:
        pending_state = str(requested_to_state)

    return {
        "candidate_id": candidate_id,
        "candidate_name": candidate.get("candidate_name"),
        "current_state": current_state,
        "requested_transition": {
            "from_state": current_state,
            "to_state": requested_to_state,
            "transition_edge": f"{current_state}->{requested_to_state}",
            "allowed_by_vocab": allowed,
        },
        "pending_state": pending_state,
        "evidence_links": _evidence_refs(candidate),
        "notes": _as_list(candidate.get("notes")),
        "blockers": blockers,
        "missing_evidence": missing_evidence,
        "unavailable_optional_evidence": unavailable_optional,
        "caveats": [
            "Scratch lifecycle report only.",
            "Evidence links are references only and are not mutated.",
            "Promotion and paper/live decisions remain human-gated outside this engine.",
        ],
        "manual_approval_requirement": (
            "A human gate owner must make any promotion, paper, live, or readiness decision outside this engine."
        ),
        "non_authority_flags": REQUIRED_NON_AUTHORITY_FLAGS,
        "next_allowed_human_decisions": _next_allowed_human_decisions(current_state, str(requested_to_state), blockers),
    }


def _next_allowed_human_decisions(current_state: str, requested_to_state: str, blockers: list[str]) -> list[str]:
    if blockers:
        return ["resolve blockers", "reject", "archive", "request more evidence"]
    if requested_to_state == "paper_eligible":
        return ["record paper eligibility by separate human lifecycle change", "reject", "archive"]
    if requested_to_state == "research_concluded":
        return ["record research conclusion by lifecycle change", "archive", "halt"]
    return [f"record {current_state}->{requested_to_state} by lifecycle change", "halt", "archive"]


def build_lifecycle_report(payload: dict[str, Any], source_path: Path | None = None) -> dict[str, Any]:
    _validate_input(payload)
    created_at_utc = payload.get("created_at_utc", DEFAULT_CREATED_AT_UTC)
    candidate_reports = [_candidate_report(candidate) for candidate in payload["candidates"]]
    report = {
        "schema_version": "candidate_lifecycle_engine_report.v1",
        "engine_id": "WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01",
        "created_at_utc": created_at_utc,
        "source_commit": _source_commit(),
        "scratch_only": True,
        "canonical_authority": False,
        "input_ref": str(source_path).replace("\\", "/") if source_path else None,
        "candidate_count": len(candidate_reports),
        "candidate_reports": candidate_reports,
        "aggregate": {
            "blocked_count": sum(1 for item in candidate_reports if item["pending_state"] == "blocked"),
            "human_approval_required_count": sum(
                1 for item in candidate_reports if item["pending_state"] == "human_approval_required"
            ),
            "canonical_evidence_mutations": 0,
            "paper_live_actions": 0,
            "auto_promotions": 0,
        },
        "non_authority_flags": REQUIRED_NON_AUTHORITY_FLAGS,
    }
    report["report_identity_hash"] = _stable_payload_hash(report)
    return report


def build_review_packet(report: dict[str, Any]) -> str:
    lines = [
        "# Candidate Lifecycle Review Packet",
        "",
        f"- Engine: {report['engine_id']}",
        f"- Created at UTC: {report['created_at_utc']}",
        "- Posture: scratch-only, reference-only, human-gated",
        "",
        "## Non-Authority Flags",
    ]
    lines.extend(f"- {flag}" for flag in report["non_authority_flags"])
    for candidate in report["candidate_reports"]:
        lines.extend(
            [
                "",
                f"## {candidate['candidate_id']}",
                f"- Current state: {candidate['current_state']}",
                f"- Pending state: {candidate['pending_state']}",
                f"- Requested transition: {candidate['requested_transition']['transition_edge']}",
                "- Evidence links:",
            ]
        )
        for key, value in candidate["evidence_links"].items():
            lines.append(f"  - {key}: {value if value else 'missing'}")
        lines.extend(["- Blockers:"])
        lines.extend(f"  - {item}" for item in candidate["blockers"] or ["none"])
        lines.extend(["- Missing evidence:"])
        lines.extend(f"  - {item}" for item in candidate["missing_evidence"] or ["none"])
        lines.extend(["- Caveats:"])
        lines.extend(f"  - {item}" for item in candidate["caveats"])
        lines.append(f"- Manual gate requirement: {candidate['manual_approval_requirement']}")
        lines.extend(["- Next allowed human decisions:"])
        lines.extend(f"  - {item}" for item in candidate["next_allowed_human_decisions"])

    packet = "\n".join(lines) + "\n"
    lowered = packet.lower()
    forbidden = [phrase for phrase in FORBIDDEN_PACKET_PHRASES if phrase in lowered]
    if forbidden:
        raise LifecycleEngineError(f"review packet contains forbidden phrase(s): {', '.join(forbidden)}")
    return packet


def build_outputs(input_path: Path) -> EngineOutputs:
    payload = load_json(input_path)
    report = build_lifecycle_report(payload, source_path=input_path)
    packet = build_review_packet(report)
    provenance = {
        "schema_version": "candidate_lifecycle_engine_provenance.v1",
        "engine_id": "WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01",
        "created_at_utc": report["created_at_utc"],
        "source_commit": report["source_commit"],
        "input_path": str(input_path).replace("\\", "/"),
        "input_sha256": _sha256_bytes(input_path.read_bytes()),
        "report_identity_hash": report["report_identity_hash"],
        "canonical_writes": False,
        "paper_live_actions": False,
        "auto_promotion": False,
        "dependency_files_changed": False,
        "non_authority_flags": REQUIRED_NON_AUTHORITY_FLAGS,
    }
    return EngineOutputs(report=report, packet_markdown=packet, provenance=provenance)


def run(input_path: Path, output_dir: Path = DEFAULT_OUTPUT_DIR) -> EngineOutputs:
    outputs = build_outputs(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "candidate_lifecycle_report.json", outputs.report)
    (output_dir / "candidate_review_packet.md").write_text(outputs.packet_markdown, encoding="utf-8")
    write_json(output_dir / "provenance.json", outputs.provenance)
    readme = output_dir / "README.md"
    if not readme.exists():
        readme.write_text(
            "# WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01 Scratch Outputs\n\n"
            "Scratch-only lifecycle report, review packet, and provenance generated by "
            "`tools.candidate_lifecycle.lifecycle_engine`. These files are advisory "
            "references only and create no canonical evidence, promotion, readiness, "
            "paper/live, runtime, or execution authority.\n",
            encoding="utf-8",
        )
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    run(args.input, args.output_dir)
    print(f"OK: wrote candidate lifecycle outputs to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
