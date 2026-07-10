"""Scratch-only Agent Inbox intake draft packet writer.

This module is intentionally separate from ``tools.operator_dashboard_api``.
It writes one noncanonical draft packet under the package scratch root and does
not create dashboard routes, canonical artifacts, candidates, runner jobs, or
pipeline actions.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from tools.agent_inbox_intake.models import (
    DraftHistoryError,
    DraftIdError,
    DraftNotFoundError,
    IntakeDraftError,
    IntakeDraftRequest,
)
from tools.agent_sandbox import MemoryAuditSink, ToolAction, ToolContext
from tools.agent_sandbox.audit import AuditRecord
from tools.agent_sandbox.permissions import WRITE_SCRATCH
from tools.lab_state.resolver import REPO_ROOT
from tools.research_agents.idea_formalizer_agent import (
    IdeaFormalizerAgent,
    IdeaFormalizerConfig,
    LOCKED_TIMEFRAMES,
    ROLE as FORMALIZER_ROLE,
    make_provider,
)


PACKAGE_ID = "WP-DASH-AGENT-INBOX-WRITE-01A"
SCHEMA_VERSION = "agent_inbox_intake_draft_packet_v1"
SERVICE_NAMESPACE = "tools.agent_inbox_intake"
DEFAULT_OUTPUT_ROOT = Path("scratch") / PACKAGE_ID / "drafts"
MAX_COMBINED_TEXT_LENGTH = 5200
CLIENT_DRAFT_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")
DRAFT_ID_RE = re.compile(r"^AIDRAFT-[A-F0-9]{16}$")
DRAFT_FILENAME_RE = re.compile(r"^(AIDRAFT-[A-F0-9]{16})\.draft_packet\.json$")
HYPOTHESIS_PREVIEW_LENGTH = 160

NON_AUTHORITY_FLAGS: dict[str, bool] = {
    "scratch_only": True,
    "noncanonical": True,
    "draft_only": True,
    "review_only": True,
    "fabricated": False,
    "not_strategy_spec": True,
    "not_variant_manifest": True,
    "not_sweep_plan": True,
    "not_result_population": True,
    "not_candidate_registry": True,
    "not_candidate_lifecycle": True,
    "not_approval": True,
    "not_promotion": True,
    "not_execution": True,
    "not_runner_job": True,
    "not_pipeline_run": True,
    "not_scheduler": True,
    "not_notification": True,
    "not_runtime": True,
    "not_paper_live": True,
    "not_provider_api": True,
}

FORBIDDEN_TARGET_PREFIXES = (
    "research/strategy_specs/",
    "research/variant_manifests/",
    "research/sweep_plans/",
    "research/result_populations/",
    "research/candidate_registry.jsonl",
    "src/",
    "lib/",
    "configs/",
    "data/",
    "tools/research_runner/",
    "tools/lab_pipeline/",
    "tools/operator_dashboard_api/",
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _format_utc(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256_json(payload: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _repo_relative(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _ensure_repo_scratch_path(path: Path, repo_root: Path) -> str:
    relative = _repo_relative(path, repo_root)
    allowed_prefix = f"scratch/{PACKAGE_ID}/"
    if not relative.startswith(allowed_prefix):
        raise IntakeDraftError(f"output path must remain under {allowed_prefix}")
    return relative


def _write_json_scratch(path: Path, payload: Mapping[str, Any], repo_root: Path) -> str:
    relative = _ensure_repo_scratch_path(path, repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return relative


def _draft_root(repo_root: Path, output_root: Path) -> Path:
    root = output_root if output_root.is_absolute() else repo_root / output_root
    _ensure_repo_scratch_path(root / "path_probe.json", repo_root)
    return root


def _validate_draft_id(draft_id: str) -> None:
    if not DRAFT_ID_RE.fullmatch(draft_id):
        raise DraftIdError("draft_id must match AIDRAFT-<16 uppercase hex characters>")


def _read_stored_packet(path: Path, *, expected_draft_id: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DraftHistoryError(f"stored draft packet is unreadable: {path.name}") from exc
    if not isinstance(payload, dict):
        raise DraftHistoryError(f"stored draft packet must be a JSON object: {path.name}")
    if payload.get("draft_id") != expected_draft_id:
        raise DraftHistoryError(f"stored draft_id does not match filename: {path.name}")
    required_types = {
        "created_at": str,
        "schema_version": str,
        "source_request": dict,
        "blockers": list,
        "warnings": list,
        "open_questions": list,
        "non_authority_flags": dict,
        "fabricated": bool,
    }
    for field, expected_type in required_types.items():
        if not isinstance(payload.get(field), expected_type):
            raise DraftHistoryError(
                f"stored draft packet has invalid or missing {field}: {path.name}"
            )
    try:
        created_at = datetime.fromisoformat(payload["created_at"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise DraftHistoryError(f"stored draft packet has invalid created_at: {path.name}") from exc
    if created_at.tzinfo is None or created_at.utcoffset() != timedelta(0):
        raise DraftHistoryError(f"stored draft packet has non-UTC created_at: {path.name}")
    request = payload["source_request"]
    for field in ("title", "hypothesis_text"):
        if not isinstance(request.get(field), str):
            raise DraftHistoryError(
                f"stored draft packet has invalid source_request.{field}: {path.name}"
            )
    for field in ("submitter_label", "market_hint", "timeframe_hint"):
        if request.get(field) is not None and not isinstance(request[field], str):
            raise DraftHistoryError(
                f"stored draft packet has invalid source_request.{field}: {path.name}"
            )
    for field in (
        "scratch_only",
        "noncanonical",
        "draft_only",
        "review_only",
        "not_approval",
        "not_promotion",
        "not_execution",
    ):
        if not isinstance(payload["non_authority_flags"].get(field), bool):
            raise DraftHistoryError(
                f"stored draft packet has invalid non_authority_flags.{field}: {path.name}"
            )
    return payload


def _hypothesis_preview(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    compact = " ".join(value.split())
    if len(compact) <= HYPOTHESIS_PREVIEW_LENGTH:
        return compact
    return compact[: HYPOTHESIS_PREVIEW_LENGTH - 1].rstrip() + "…"


def _non_authority_summary(flags: Mapping[str, Any]) -> dict[str, bool]:
    names = (
        "scratch_only",
        "noncanonical",
        "draft_only",
        "review_only",
        "not_approval",
        "not_promotion",
        "not_execution",
    )
    return {name: flags.get(name) is True for name in names}


def list_intake_drafts(
    *,
    repo_root: Path = REPO_ROOT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> dict[str, Any]:
    """Return deterministic compact metadata for stored scratch draft packets."""

    repo_root = repo_root.resolve()
    root = _draft_root(repo_root, output_root)
    storage_source = _repo_relative(root, repo_root)
    if not root.exists():
        return {
            "status": "empty",
            "count": 0,
            "drafts": [],
            "storage_source": storage_source,
            "scratch_only": True,
        }
    if not root.is_dir():
        raise DraftHistoryError("draft history storage source is not a directory")

    drafts: list[dict[str, Any]] = []
    for path in root.glob("*.draft_packet.json"):
        match = DRAFT_FILENAME_RE.fullmatch(path.name)
        if match is None:
            raise DraftHistoryError(f"stored draft packet has invalid filename: {path.name}")
        _ensure_repo_scratch_path(path, repo_root)
        draft_id = match.group(1)
        packet = _read_stored_packet(path, expected_draft_id=draft_id)
        request = packet["source_request"]
        flags = packet["non_authority_flags"]
        drafts.append(
            {
                "draft_id": draft_id,
                "created_at": packet["created_at"],
                "schema_version": packet["schema_version"],
                "title": request.get("title"),
                "submitter_label": request.get("submitter_label"),
                "market_hint": request.get("market_hint"),
                "timeframe_hint": request.get("timeframe_hint"),
                "hypothesis_preview": _hypothesis_preview(request.get("hypothesis_text")),
                "blocker_count": len(packet["blockers"]),
                "warning_count": len(packet["warnings"]),
                "open_question_count": len(packet["open_questions"]),
                "fabricated": packet["fabricated"],
                "non_authority": _non_authority_summary(flags),
                "source_packet_path": _repo_relative(path, repo_root),
            }
        )
    drafts.sort(key=lambda item: item["draft_id"])
    drafts.sort(key=lambda item: item["created_at"], reverse=True)
    return {
        "status": "available" if drafts else "empty",
        "count": len(drafts),
        "drafts": drafts,
        "storage_source": storage_source,
        "scratch_only": True,
    }


def get_intake_draft(
    draft_id: str,
    *,
    repo_root: Path = REPO_ROOT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> dict[str, Any]:
    """Return one exact stored scratch packet by its validated identifier."""

    _validate_draft_id(draft_id)
    repo_root = repo_root.resolve()
    root = _draft_root(repo_root, output_root)
    path = root / f"{draft_id}.draft_packet.json"
    if not path.is_file():
        raise DraftNotFoundError(f"draft not found: {draft_id}")
    _ensure_repo_scratch_path(path, repo_root)
    return _read_stored_packet(path, expected_draft_id=draft_id)


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _normalise_request(request: IntakeDraftRequest) -> dict[str, Any]:
    payload = request.model_dump()
    cleaned = {
        key: _clean_text(value) if isinstance(value, str) else value
        for key, value in payload.items()
    }
    if not cleaned["title"]:
        raise IntakeDraftError("title must be non-empty")
    if not cleaned["hypothesis_text"]:
        raise IntakeDraftError("hypothesis_text must be non-empty")
    combined_length = (
        len(cleaned["title"])
        + len(cleaned["hypothesis_text"])
        + len(cleaned.get("constraints_notes") or "")
    )
    if combined_length > MAX_COMBINED_TEXT_LENGTH:
        raise IntakeDraftError("combined intake text exceeds bounded service limit")
    client_draft_id = cleaned.get("client_draft_id")
    if client_draft_id is not None and not CLIENT_DRAFT_ID_RE.fullmatch(client_draft_id):
        raise IntakeDraftError("client_draft_id contains unsupported characters")
    market_hint = cleaned.get("market_hint") or "BTCUSDT"
    if "BTCUSDT" not in market_hint.upper().replace("-", "").replace("_", ""):
        raise IntakeDraftError("market_hint must remain bounded to BTCUSDT")
    timeframe = (cleaned.get("timeframe_hint") or "15m").strip()
    if timeframe not in LOCKED_TIMEFRAMES:
        raise IntakeDraftError(f"timeframe_hint must be one of {sorted(LOCKED_TIMEFRAMES)}")
    cleaned["market_hint"] = market_hint
    cleaned["timeframe_hint"] = timeframe
    return cleaned


class PacketOnlyIdeaFormalizer(IdeaFormalizerAgent):
    """Use formalizer logic while preventing formalizer artifact writes.

    The underlying formalizer normally persists ``formalized_idea.json`` and can
    produce scratch Strategy Spec drafts for supported primitive families. Agent
    Inbox packets are narrower: this subclass captures formalizer writes in
    memory and declares every primitive family unsupported for Strategy Spec
    emission, so the service writes exactly one draft packet.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.captured_json_writes: dict[str, Any] = {}
        self.captured_text_writes: dict[str, str] = {}

    @classmethod
    def _draft_family_supported(
        cls, draft: Mapping[str, Any], assessment: Mapping[str, Any]
    ) -> bool:
        del draft, assessment
        return False

    def _write_text(self, path: Path | str, content: str) -> str:
        relative = self._repo_relative(path)
        self.tool_context.require_allowed(ToolAction(WRITE_SCRATCH, relative))
        self.captured_text_writes[relative] = content
        return relative

    def _write_json(self, path: Path | str, payload: Mapping[str, Any]) -> str:
        relative = self._repo_relative(path)
        self.tool_context.require_allowed(ToolAction(WRITE_SCRATCH, relative))
        self.captured_json_writes[relative] = json.loads(json.dumps(payload, sort_keys=True))
        return relative


def _formalize_packet_only(
    *,
    idea: str,
    timeframe: str,
    constraints: list[str],
    repo_root: Path,
    clock: Any,
) -> tuple[dict[str, Any], list[AuditRecord], list[str]]:
    sink = MemoryAuditSink()
    context = ToolContext(
        wp_id=PACKAGE_ID,
        role=FORMALIZER_ROLE,
        audit_sink=sink,
        clock=clock,
    )
    config = IdeaFormalizerConfig(provider_mode="fake_offline", provider_id="fake-rule-v1")
    agent = PacketOnlyIdeaFormalizer(
        config=config,
        tool_context=context,
        provider=make_provider(config),
        repo_root=repo_root,
    )
    result = agent.run(
        idea=idea,
        symbol="BTCUSDT",
        timeframe=timeframe,
        constraints=constraints,
    )
    return result, sink.records, sorted(agent.captured_json_writes)


def _collect_blockers(formalizer_result: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    blockers.extend(str(item) for item in formalizer_result.get("rejection_reasons") or [])
    draft_strategy_spec = formalizer_result.get("draft_strategy_spec") or {}
    blockers.extend(str(item) for item in draft_strategy_spec.get("blockers") or [])
    assessment = formalizer_result.get("capability_assessment") or {}
    blockers.extend(
        f"blocking feature: {item}" for item in assessment.get("blocking_features") or []
    )
    return list(dict.fromkeys(blockers))


def _audit_records_to_dicts(records: list[AuditRecord]) -> list[dict[str, str]]:
    return [record.to_dict() for record in records]


def _assert_no_forbidden_authorized_actions(records: list[AuditRecord]) -> None:
    for record in records:
        if record.decision != "allowed":
            continue
        if record.action_type not in {"read_non_secret_files", "write_scratch"}:
            raise IntakeDraftError(f"unexpected allowed action: {record.action_type}")
        if any(record.target_path.startswith(prefix) for prefix in FORBIDDEN_TARGET_PREFIXES):
            raise IntakeDraftError(f"forbidden target authorized: {record.target_path}")


def create_intake_draft(
    request: IntakeDraftRequest,
    *,
    repo_root: Path = REPO_ROOT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    clock: Any = _utc_now,
) -> dict[str, Any]:
    """Create one scratch-only Agent Inbox draft packet and return it."""

    repo_root = repo_root.resolve()
    output_root = _draft_root(repo_root, output_root)
    source_request = _normalise_request(request)
    constraints = []
    if source_request.get("constraints_notes"):
        constraints.append(str(source_request["constraints_notes"]))
    idea = f"{source_request['title']}. {source_request['hypothesis_text']}"
    source_hash = _sha256_json(source_request)
    draft_basis = source_request.get("client_draft_id") or source_hash
    draft_id = (
        "AIDRAFT-"
        + hashlib.sha256(str(draft_basis).encode("utf-8")).hexdigest()[:16].upper()
    )
    formalizer_result, audit_records, captured_paths = _formalize_packet_only(
        idea=idea,
        timeframe=source_request["timeframe_hint"],
        constraints=constraints,
        repo_root=repo_root,
        clock=clock,
    )
    _assert_no_forbidden_authorized_actions(audit_records)
    blockers = _collect_blockers(formalizer_result)
    formalizer_hash = _sha256_json(formalizer_result)
    created_at = _format_utc(clock())
    output_path = output_root / f"{draft_id}.draft_packet.json"
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "draft_id": draft_id,
        "created_at": created_at,
        "source_request": source_request,
        "formalizer_result": copy.deepcopy(formalizer_result),
        "availability_primitive_check": formalizer_result.get("capability_assessment"),
        "open_questions": [
            "Human review must decide whether this scratch draft should be revised, "
            "discarded, or promoted through a later authorized package."
        ],
        "blockers": blockers,
        "warnings": [
            "Scratch-only Agent Inbox draft packet; no canonical artifact, candidate, runner, pipeline, paper/live, scheduler, or notification authority."
        ],
        "non_authority_flags": dict(NON_AUTHORITY_FLAGS),
        "provenance": {
            "service_namespace": SERVICE_NAMESPACE,
            "package_id": PACKAGE_ID,
            "formalizer_module": "tools.research_agents.idea_formalizer_agent",
            "formalizer_mode": "fake_offline_packet_only",
            "provider_mode": "fake_offline",
            "provider_id": "fake-rule-v1",
            "tool_context_role": FORMALIZER_ROLE,
            "tool_context_wp_id": PACKAGE_ID,
            "formalizer_writes_captured_in_memory": True,
            "captured_formalizer_write_paths": captured_paths,
            "output_path": _repo_relative(output_path, repo_root),
        },
        "source_hashes": {
            "source_request_sha256": source_hash,
            "formalizer_result_sha256": formalizer_hash,
        },
        "tool_context_audit": _audit_records_to_dicts(audit_records),
        "fabricated": False,
    }
    _write_json_scratch(output_path, packet, repo_root)
    return packet
