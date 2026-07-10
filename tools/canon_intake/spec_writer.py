"""Gate-C-only append writer for one canonical Strategy Spec.

Eligibility and review state are inputs to lineage only.  Only a valid Karl
exact-content Gate C record authorizes this writer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from tools.registry.validate_strategy_specs import validate_strategy_specs


WRITER_VERSION = "gate_c_strategy_spec_writer_v1"
LOCKED_TIMEFRAMES = frozenset({"15m", "30m", "1h", "4h", "1d"})
CANONICAL_DIR = Path("research/strategy_specs")
AUDIT_PATH = Path("research/canonical_crossing_audit/strategy_spec_writes.jsonl")
FORBIDDEN_AUTHORITY_KEYS = frozenset({"queue_entry", "queue_admission", "dispatch_action", "candidate_creation", "promotion_action", "runtime_action", "paper_action", "live_action", "oms_action", "reconciliation_action"})


class GateCWriteError(ValueError):
    """Raised before authority is exercised or when a write cannot finish safely."""


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
    if not isinstance(value, str) or not value or "\\" in value:
        raise GateCWriteError(f"{label} must be a non-empty repo-relative POSIX path")
    path = (repo_root / value).resolve()
    try:
        path.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise GateCWriteError(f"{label} escapes the repository") from exc
    return path


def _verify_ref(repo_root: Path, ref: Any, label: str) -> tuple[str, str]:
    if not isinstance(ref, dict):
        raise GateCWriteError(f"{label} must contain path and sha256")
    path = _repo_path(repo_root, ref.get("path"), f"{label}.path")
    if not path.is_file():
        raise GateCWriteError(f"{label} source does not exist: {path}")
    actual = _digest(path.read_bytes())
    if ref.get("sha256") != actual:
        raise GateCWriteError(f"{label} hash mismatch")
    return ref["path"], actual


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key).lower()
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def _independent_checks(spec: Mapping[str, Any], target: str) -> None:
    spec_id = spec.get("strategy_spec_id")
    if target != f"research/strategy_specs/{spec_id}.strategy_spec.json":
        raise GateCWriteError("target path does not match the Strategy Spec identifier")
    instruments = spec.get("instruments")
    if not isinstance(instruments, dict) or instruments.get("symbols") != ["BTCUSDT"]:
        raise GateCWriteError("Strategy Spec market must be exactly BTCUSDT")
    if instruments.get("instrument_family") != "crypto_perp" or instruments.get("market_type") != "perpetual":
        raise GateCWriteError("Strategy Spec must describe a crypto perpetual")
    directions = instruments.get("directions_allowed")
    if not isinstance(directions, list) or not directions or not set(directions) <= {"long", "short"}:
        raise GateCWriteError("Strategy Spec directions must be bounded")
    timeframe = spec.get("timeframe_and_data")
    if not isinstance(timeframe, dict) or timeframe.get("primary_timeframe") not in LOCKED_TIMEFRAMES:
        raise GateCWriteError("Strategy Spec primary timeframe is outside the locked set")
    if not set(timeframe.get("confirmation_timeframes", [])) <= LOCKED_TIMEFRAMES:
        raise GateCWriteError("Strategy Spec confirmation timeframe is outside the locked set")
    parameters = spec.get("free_parameters")
    if not isinstance(parameters, dict) or not isinstance(parameters.get("parameters"), list) or len(parameters["parameters"]) > 5:
        raise GateCWriteError("Strategy Spec parameters are not bounded")
    provenance = spec.get("provenance")
    if not isinstance(provenance, dict) or not provenance.get("source_refs"):
        raise GateCWriteError("Strategy Spec provenance must contain source references")
    for key in _walk_keys(spec):
        normalized = key.replace("-", "_")
        if normalized in FORBIDDEN_AUTHORITY_KEYS:
            raise GateCWriteError(f"forbidden downstream authority field in Strategy Spec: {key}")


def _validate_candidate(repo_root: Path, proposed_path: Path, proposed_raw: bytes) -> None:
    with tempfile.TemporaryDirectory(prefix="gate-c-spec-") as temp:
        root = Path(temp)
        specs = root / "strategy_specs"
        shutil.copytree(repo_root / CANONICAL_DIR, specs)
        (specs / proposed_path.name).write_bytes(proposed_raw)
        errors = validate_strategy_specs(
            strategy_specs_dir=specs,
            schema_path=repo_root / "research/schemas/strategy_spec.schema.json",
            repo_root=repo_root,
        )
        if errors:
            raise GateCWriteError("Strategy Spec structural validation failed: " + errors[0])


def write_approved_strategy_spec(
    *, repo_root: Path, proposed_content_path: Path, gate_c_path: Path, now: datetime | None = None
) -> dict[str, Any]:
    """Write exactly one approved spec and one append-only audit record."""
    repo_root = repo_root.resolve()
    proposed_path = proposed_content_path.resolve()
    gate_path = gate_c_path.resolve()
    spec, proposed_raw = _load_object(proposed_path, "proposed Strategy Spec")
    gate, gate_raw = _load_object(gate_path, "Gate C record")
    required_exact = {
        "schema_version": "gate_c_strategy_spec_approval_v1",
        "approved_by": "Karl",
        "approval_scope": "one_append_only_canonical_strategy_spec_write",
        "content_reviewed": True,
        "authorizes_canonical_write": True,
        "append_only": True,
        "authorizes_queue": False,
        "authorizes_execution": False,
        "authorizes_candidate_lifecycle": False,
        "authorizes_promotion_readiness": False,
        "authorizes_paper_live_runtime": False,
        "authorizes_scheduler_autonomy": False,
        "authorizes_notifications": False,
        "exact_content_and_target_only": True,
    }
    for field, expected in required_exact.items():
        if gate.get(field) != expected:
            raise GateCWriteError(f"Gate C {field} must equal {expected!r}")
    if not isinstance(gate.get("approval_id"), str) or not gate["approval_id"].strip():
        raise GateCWriteError("Gate C approval_id is required")
    if not isinstance(gate.get("approved_at"), str) or not gate["approved_at"].strip():
        raise GateCWriteError("Gate C approved_at is required")
    if not isinstance(gate.get("source_draft_id"), str) or not gate["source_draft_id"].strip():
        raise GateCWriteError("Gate C source_draft_id is required")
    if not isinstance(gate.get("source_hashes"), dict) or not gate["source_hashes"]:
        raise GateCWriteError("Gate C source_hashes must preserve idea/formalizer lineage hashes")
    content_hash = _digest(proposed_raw)
    if gate.get("approved_content_sha256") != content_hash:
        raise GateCWriteError("Gate C approved content hash mismatch")
    target_value = gate.get("canonical_target_path")
    target = _repo_path(repo_root, target_value, "canonical_target_path")
    canonical_root = (repo_root / CANONICAL_DIR).resolve()
    if target.parent != canonical_root or target.is_symlink():
        raise GateCWriteError("Gate C target is not an allowed canonical Strategy Spec path")
    if target.exists():
        raise GateCWriteError("canonical target already exists; overwrite is forbidden")
    refs = {}
    for name in ("source_draft", "review_trail", "eligibility_report"):
        refs[name] = _verify_ref(repo_root, gate.get(name), name)
    _independent_checks(spec, target_value)
    _validate_candidate(repo_root, target, proposed_raw)

    audit_path = (repo_root / AUDIT_PATH).resolve()
    if audit_path.exists() and audit_path.is_symlink():
        raise GateCWriteError("audit path may not be a symlink")
    if audit_path.exists():
        try:
            prior_records = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines() if line]
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise GateCWriteError("existing audit is unreadable; refusing to append") from exc
        if any(record.get("canonical_target_path") == target_value or record.get("strategy_spec_id") == spec.get("strategy_spec_id") for record in prior_records if isinstance(record, dict)):
            raise GateCWriteError("audit already records this target or Strategy Spec identifier")
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    record = {
        "schema_version": "gate_c_strategy_spec_write_audit_v1",
        "approval_id": gate["approval_id"],
        "approval_record_sha256": _digest(gate_raw),
        "approved_by": "Karl",
        "approved_at": gate["approved_at"],
        "written_at": timestamp,
        "writer_version": WRITER_VERSION,
        "strategy_spec_id": spec["strategy_spec_id"],
        "source_draft_id": gate["source_draft_id"],
        "source_hashes": gate["source_hashes"],
        "canonical_target_path": target_value,
        "approved_content_sha256": content_hash,
        "source_draft": {"path": refs["source_draft"][0], "sha256": refs["source_draft"][1]},
        "review_trail": {"path": refs["review_trail"][0], "sha256": refs["review_trail"][1]},
        "eligibility_report": {"path": refs["eligibility_report"][0], "sha256": refs["eligibility_report"][1], "advisory_only": True},
        "validation_outcome": "passed_before_write",
        "no_queue_candidate_runtime_outputs": True,
    }
    try:
        target.write_bytes(proposed_raw)
        with audit_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    except OSError as exc:
        if target.exists():
            target.unlink()
        raise GateCWriteError("canonical write or audit append failed; spec write rolled back") from exc
    return record


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
