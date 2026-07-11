"""Gate-C-only protected writer for one canonical Strategy Spec."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Mapping

from tools.registry.validate_strategy_specs import validate_strategy_specs


WRITER_VERSION = "gate_c_strategy_spec_writer_v2"
LOCKED_TIMEFRAMES = frozenset({"15m", "30m", "1h", "4h", "1d"})
CANONICAL_DIR = Path("research/strategy_specs")
AUDIT_PATH = Path("research/canonical_crossing_audit/strategy_spec_writes.jsonl")
LOCK_PATH = Path("research/canonical_crossing_audit/.strategy_spec_write.lock")
DRAFT_ROOT = Path("scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts")
REVIEW_ROOT = Path("scratch/WP-DASH-AGENT-INBOX-WRITE-01A/reviews")
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
DRAFT_ID_RE = re.compile(r"^AIDRAFT-[A-F0-9]{16}$")
REVIEW_STATES = frozenset({"needs_clarification", "reviewed", "rejected", "flagged_for_canonicalization"})
FORBIDDEN_AUTHORITY_KEYS = frozenset({"queue_entry", "queue_admission", "dispatch_action", "candidate_creation", "promotion_action", "runtime_action", "paper_action", "live_action", "oms_action", "reconciliation_action"})


class GateCWriteError(ValueError):
    """Raised before authority is exercised or when a write fails closed."""


class GateCIntegrityCriticalError(GateCWriteError):
    """Raised when rollback cannot restore the protected crossing boundary."""


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _load_object(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GateCWriteError(f"{label} is not readable JSON: {path}") from exc
    if not isinstance(value, dict):
        raise GateCWriteError(f"{label} must be a JSON object")
    return value, raw


def _repo_path(repo_root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value or Path(value).is_absolute():
        raise GateCWriteError(f"{label} must be a non-empty repo-relative POSIX path")
    path = (repo_root / value).resolve()
    try:
        path.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise GateCWriteError(f"{label} escapes the repository") from exc
    return path


def _verify_ref(repo_root: Path, ref: Any, label: str) -> tuple[str, str, Path, bytes]:
    if not isinstance(ref, dict):
        raise GateCWriteError(f"{label} must contain path and sha256")
    path = _repo_path(repo_root, ref.get("path"), f"{label}.path")
    if not path.is_file() or path.is_symlink():
        raise GateCWriteError(f"{label} source is not a regular file: {path}")
    raw = path.read_bytes()
    actual = _digest(raw)
    if ref.get("sha256") != actual:
        raise GateCWriteError(f"{label} hash mismatch")
    return ref["path"], actual, path, raw


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key).lower()
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def _validate_draft(packet: Mapping[str, Any], path: str, draft_id: str, source_hashes: Any) -> None:
    expected = (DRAFT_ROOT / f"{draft_id}.draft_packet.json").as_posix()
    if path != expected or not DRAFT_ID_RE.fullmatch(draft_id):
        raise GateCWriteError("source draft identity/path is outside the Agent Inbox contract")
    if packet.get("schema_version") != "agent_inbox_intake_draft_packet_v1" or packet.get("draft_id") != draft_id:
        raise GateCWriteError("source draft identity or schema is invalid")
    request, formalizer = packet.get("source_request"), packet.get("formalizer_result")
    if not isinstance(request, dict) or not all(isinstance(request.get(k), str) and request[k].strip() for k in ("title", "hypothesis_text")):
        raise GateCWriteError("source draft request contract is invalid")
    if not isinstance(formalizer, dict) or not isinstance(formalizer.get("research_object"), dict):
        raise GateCWriteError("source draft formalizer lineage is invalid")
    actual_hashes = packet.get("source_hashes")
    if not isinstance(actual_hashes, dict) or not actual_hashes or actual_hashes != source_hashes:
        raise GateCWriteError("Gate C source_hashes do not exactly match the draft lineage")
    if not all(isinstance(v, str) and SHA256_RE.fullmatch(v) for v in actual_hashes.values()):
        raise GateCWriteError("source lineage contains a malformed SHA-256 value")


def _validate_reviews(raw: bytes, draft_id: str) -> None:
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeError as exc:
        raise GateCWriteError("review trail is not UTF-8 JSONL") from exc
    if not lines:
        raise GateCWriteError("review trail is empty")
    events = []
    for index, line in enumerate(lines, 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise GateCWriteError(f"malformed review event at line {index}") from exc
        required_flags = event.get("non_authority_flags") if isinstance(event, dict) else None
        if (not isinstance(event, dict) or event.get("schema_version") != "agent_inbox_draft_review_event_v1"
                or event.get("draft_id") != draft_id or event.get("append_index") != index
                or event.get("review_state") not in REVIEW_STATES
                or not isinstance(event.get("event_id"), str) or not isinstance(event.get("reviewer_label"), str)
                or not isinstance(event.get("timestamp_utc"), str) or not isinstance(event.get("rationale"), str)
                or not isinstance(required_flags, dict) or required_flags.get("not_canonicalization_approval") is not True):
            raise GateCWriteError(f"invalid review event contract at line {index}")
        events.append(event)
    if events[-1]["review_state"] not in {"reviewed", "flagged_for_canonicalization"}:
        raise GateCWriteError("latest review state is not eligible for Gate C consideration")


def _validate_eligibility(report: Mapping[str, Any], draft_id: str, refs: Mapping[str, tuple[str, str, Path, bytes]]) -> None:
    exact = {
        "schema_version": "canon_intake_eligibility_report_v1", "draft_id": draft_id,
        "source_draft_path": refs["source_draft"][0], "source_draft_hash": refs["source_draft"][1],
        "review_trail_path": refs["review_trail"][0], "review_trail_hash": refs["review_trail"][1],
        "advisory_only": True, "canonical_authority": False, "gate_c_authority": False, "queue_authority": False,
    }
    if any(report.get(k) != v for k, v in exact.items()):
        raise GateCWriteError("eligibility report identity, lineage, or authority flags are invalid")
    flags = report.get("non_authority_flags")
    required = {"not_approval", "not_canonical_write", "not_gate_c", "not_queue_admission", "not_candidate_creation", "not_research_execution", "not_runtime_action"}
    if not isinstance(flags, dict) or any(flags.get(key) is not True for key in required):
        raise GateCWriteError("eligibility report non-authority flags are inconsistent")


def _independent_checks(spec: Mapping[str, Any], target: str, refs: Mapping[str, tuple[str, str, Path, bytes]], approval_id: str) -> None:
    spec_id = spec.get("strategy_spec_id")
    if target != f"research/strategy_specs/{spec_id}.strategy_spec.json":
        raise GateCWriteError("target path does not match the Strategy Spec identifier")
    instruments = spec.get("instruments")
    if not isinstance(instruments, dict) or instruments.get("symbols") != ["BTCUSDT"] or instruments.get("instrument_family") != "crypto_perp" or instruments.get("market_type") != "perpetual":
        raise GateCWriteError("Strategy Spec market must be exactly BTCUSDT crypto perpetual")
    directions = instruments.get("directions_allowed")
    if not isinstance(directions, list) or not directions or not set(directions) <= {"long", "short"}:
        raise GateCWriteError("Strategy Spec directions must be bounded")
    timeframe = spec.get("timeframe_and_data")
    if not isinstance(timeframe, dict) or timeframe.get("primary_timeframe") not in LOCKED_TIMEFRAMES or not set(timeframe.get("confirmation_timeframes", [])) <= LOCKED_TIMEFRAMES:
        raise GateCWriteError("Strategy Spec timeframe is outside the locked set")
    parameters = spec.get("free_parameters")
    if not isinstance(parameters, dict) or not isinstance(parameters.get("parameters"), list) or len(parameters["parameters"]) > 5:
        raise GateCWriteError("Strategy Spec parameters are not bounded")
    expected_refs = [f"{name}:{refs[name][0]}#{refs[name][1]}" for name in ("source_draft", "review_trail", "eligibility_report")]
    expected_refs.append(f"gate_c_approval:{approval_id}")
    provenance = spec.get("provenance")
    if not isinstance(provenance, dict) or provenance.get("source_refs") != expected_refs:
        raise GateCWriteError("Strategy Spec provenance is not exactly bound to the approved source chain")
    for key in _walk_keys(spec):
        if key.replace("-", "_") in FORBIDDEN_AUTHORITY_KEYS:
            raise GateCWriteError(f"forbidden downstream authority field in Strategy Spec: {key}")


def _validate_candidate(repo_root: Path, proposed_path: Path, proposed_raw: bytes) -> None:
    with tempfile.TemporaryDirectory(prefix="gate-c-spec-") as temp:
        specs = Path(temp) / "strategy_specs"
        shutil.copytree(repo_root / CANONICAL_DIR, specs)
        (specs / proposed_path.name).write_bytes(proposed_raw)
        errors = validate_strategy_specs(strategy_specs_dir=specs, schema_path=repo_root / "research/schemas/strategy_spec.schema.json", repo_root=repo_root)
        if errors:
            raise GateCWriteError("Strategy Spec structural validation failed: " + errors[0])


@contextmanager
def _crossing_lock(repo_root: Path):
    path = repo_root / LOCK_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise GateCWriteError("canonical crossing lock exists; stale locks require explicit operator inspection") from exc
    try:
        os.write(fd, f"pid={os.getpid()}\n".encode())
        os.fsync(fd)
        os.close(fd)
        fd = -1
        yield
    finally:
        if fd >= 0:
            os.close(fd)
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def _open_audit(path: Path) -> tuple[BinaryIO, bool]:
    try:
        return path.open("x+b"), True
    except FileExistsError:
        return path.open("r+b"), False


def _read_audit(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GateCWriteError("existing audit is unreadable; refusing to append") from exc


def write_approved_strategy_spec(*, repo_root: Path, proposed_content_path: Path, gate_c_path: Path, now: datetime | None = None) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    spec, proposed_raw = _load_object(proposed_content_path.resolve(), "proposed Strategy Spec")
    gate, gate_raw = _load_object(gate_c_path.resolve(), "Gate C record")
    required_exact = {"schema_version": "gate_c_strategy_spec_approval_v1", "approved_by": "Karl", "approval_scope": "one_append_only_canonical_strategy_spec_write", "content_reviewed": True, "authorizes_canonical_write": True, "append_only": True, "authorizes_queue": False, "authorizes_execution": False, "authorizes_candidate_lifecycle": False, "authorizes_promotion_readiness": False, "authorizes_paper_live_runtime": False, "authorizes_scheduler_autonomy": False, "authorizes_notifications": False, "exact_content_and_target_only": True}
    for field, expected in required_exact.items():
        if gate.get(field) != expected:
            raise GateCWriteError(f"Gate C {field} must equal {expected!r}")
    approval_id, draft_id = gate.get("approval_id"), gate.get("source_draft_id")
    if not isinstance(approval_id, str) or not approval_id.strip() or not isinstance(gate.get("approved_at"), str) or not gate["approved_at"].strip() or not isinstance(draft_id, str):
        raise GateCWriteError("Gate C approval identity, timestamp, and source draft ID are required")
    content_hash = _digest(proposed_raw)
    if gate.get("approved_content_sha256") != content_hash:
        raise GateCWriteError("Gate C approved content hash mismatch")
    target_value = gate.get("canonical_target_path")
    target = _repo_path(repo_root, target_value, "canonical_target_path")
    canonical_root = (repo_root / CANONICAL_DIR).resolve()
    if target.parent != canonical_root or target.is_symlink():
        raise GateCWriteError("Gate C target is not an allowed canonical Strategy Spec path")
    refs = {name: _verify_ref(repo_root, gate.get(name), name) for name in ("source_draft", "review_trail", "eligibility_report")}
    draft = json.loads(refs["source_draft"][3].decode("utf-8"))
    eligibility = json.loads(refs["eligibility_report"][3].decode("utf-8"))
    _validate_draft(draft, refs["source_draft"][0], draft_id, gate.get("source_hashes"))
    _validate_reviews(refs["review_trail"][3], draft_id)
    _validate_eligibility(eligibility, draft_id, refs)
    _independent_checks(spec, target_value, refs, approval_id)
    _validate_candidate(repo_root, target, proposed_raw)
    audit_path = (repo_root / AUDIT_PATH).resolve()
    if audit_path.is_symlink():
        raise GateCWriteError("audit path may not be a symlink")
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    record = {"schema_version": "gate_c_strategy_spec_write_audit_v1", "approval_id": approval_id, "approval_record_sha256": _digest(gate_raw), "approved_by": "Karl", "approved_at": gate["approved_at"], "written_at": timestamp, "writer_version": WRITER_VERSION, "strategy_spec_id": spec["strategy_spec_id"], "source_draft_id": draft_id, "source_hashes": gate["source_hashes"], "canonical_target_path": target_value, "approved_content_sha256": content_hash, "source_draft": {"path": refs["source_draft"][0], "sha256": refs["source_draft"][1]}, "review_trail": {"path": refs["review_trail"][0], "sha256": refs["review_trail"][1]}, "eligibility_report": {"path": refs["eligibility_report"][0], "sha256": refs["eligibility_report"][1], "advisory_only": True}, "validation_outcome": "passed_before_write", "no_queue_candidate_runtime_outputs": True}
    line = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
    with _crossing_lock(repo_root):
        prior = _read_audit(audit_path)
        if any(isinstance(r, dict) and (r.get("canonical_target_path") == target_value or r.get("strategy_spec_id") == spec.get("strategy_spec_id") or r.get("approval_id") == approval_id) for r in prior):
            raise GateCWriteError("audit already records this target, Strategy Spec identifier, or approval_id")
        if target.exists():
            raise GateCWriteError("canonical target already exists; overwrite is forbidden")
        audit_handle = None
        audit_created = False
        pre_length = 0
        target_created = False
        try:
            with target.open("xb") as handle:
                target_created = True
                if handle.write(proposed_raw) != len(proposed_raw):
                    raise OSError("partial canonical target write")
                handle.flush()
                os.fsync(handle.fileno())
            audit_handle, audit_created = _open_audit(audit_path)
            audit_handle.seek(0, os.SEEK_END)
            pre_length = audit_handle.tell()
            if audit_handle.write(line) != len(line):
                raise OSError("partial audit append")
            audit_handle.flush()
            os.fsync(audit_handle.fileno())
            audit_handle.close()
            return record
        except (OSError, ValueError) as exc:
            rollback_errors = []
            if audit_handle is not None:
                try:
                    audit_handle.seek(pre_length)
                    audit_handle.truncate()
                    audit_handle.flush()
                    os.fsync(audit_handle.fileno())
                    audit_handle.close()
                    if audit_created and pre_length == 0:
                        audit_path.unlink()
                except OSError as rollback_exc:
                    rollback_errors.append(f"audit rollback failed: {rollback_exc}")
            if target_created:
                try:
                    target.unlink()
                except OSError as rollback_exc:
                    rollback_errors.append(f"target rollback failed: {rollback_exc}")
            if rollback_errors:
                raise GateCIntegrityCriticalError("; ".join(rollback_errors)) from exc
            raise GateCWriteError("canonical write or audit append failed; crossing rolled back") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposed-content", type=Path, required=True)
    parser.add_argument("--gate-c", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        record = write_approved_strategy_spec(repo_root=args.repo_root, proposed_content_path=args.proposed_content, gate_c_path=args.gate_c)
    except GateCWriteError as exc:
        parser.exit(2, f"Gate C canonical write stopped: {exc}\n")
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
