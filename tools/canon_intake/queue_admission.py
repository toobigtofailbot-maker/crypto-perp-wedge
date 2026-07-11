"""Gate-Q exact-content writer for one inert offline-research queue admission."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Mapping

from jsonschema import Draft7Validator, RefResolver

from tools.registry.validate_strategy_specs import validate_strategy_specs
from tools.registry.validate_variant_sweep_artifacts import validate_variant_sweep_artifacts

WRITER_VERSION = "gate_q_queue_admission_writer_v1"
APPROVAL_ROOT = Path("research/queue/gate_q_approvals")
ADMISSION_ROOT = Path("research/queue/admissions")
AUDIT_PATH = Path("research/queue/admission_audit/queue_admissions.jsonl")
LOCK_PATH = Path("research/queue/admission_audit/.queue_admission.lock")
GATE_C_AUDIT = "research/canonical_crossing_audit/strategy_spec_writes.jsonl"


class QueueAdmissionError(ValueError):
    """Admission failed closed before or during the protected crossing."""


class QueueAdmissionIntegrityCriticalError(QueueAdmissionError):
    """Manual inspection is required and automatic retry is forbidden."""


def _digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _reject_floats(value: Any) -> None:
    if isinstance(value, float):
        raise QueueAdmissionError("floating-point values are forbidden in repo_canonical_json_v1")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise QueueAdmissionError("canonical JSON object keys must be strings")
            _reject_floats(child)
    elif isinstance(value, list):
        for child in value:
            _reject_floats(child)


def repo_canonical_json_v1(value: Any) -> bytes:
    """Return the locked compact UTF-8 canonical representation."""
    _reject_floats(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def approval_core_sha256(gate_q: Mapping[str, Any]) -> str:
    core = {key: value for key, value in gate_q.items() if key not in {"proposed_queue_item", "approval_core_sha256"}}
    return _digest(repo_canonical_json_v1(core))


def _load_object(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    if path.is_symlink() or not path.is_file():
        raise QueueAdmissionError(f"{label} must be a regular non-symlink file")
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise QueueAdmissionError(f"{label} is not readable UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise QueueAdmissionError(f"{label} must be a JSON object")
    return value, raw


def _repo_path(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value or Path(value).is_absolute():
        raise QueueAdmissionError(f"{label} must be a repo-relative POSIX path")
    path = (root / value).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise QueueAdmissionError(f"{label} escapes the repository") from exc
    return path


def _verify_ref(root: Path, ref: Any, label: str) -> tuple[Path, bytes]:
    if not isinstance(ref, dict):
        raise QueueAdmissionError(f"{label} reference is invalid")
    path = _repo_path(root, ref.get("path"), f"{label}.path")
    if path.is_symlink() or not path.is_file():
        raise QueueAdmissionError(f"{label} must resolve to a regular non-symlink file")
    raw = path.read_bytes()
    if ref.get("sha256") != _digest(raw):
        raise QueueAdmissionError(f"{label} hash mismatch")
    return path, raw


def _validator(root: Path, schema_name: str) -> Draft7Validator:
    schema_dir = root / "research/schemas"
    schema = json.loads((schema_dir / schema_name).read_text(encoding="utf-8"))
    store = {}
    for path in schema_dir.glob("*.schema.json"):
        candidate = json.loads(path.read_text(encoding="utf-8"))
        store[path.name] = candidate
        if "$id" in candidate:
            store[candidate["$id"]] = candidate
    return Draft7Validator(schema, resolver=RefResolver((schema_dir / schema_name).as_uri(), schema, store=store))


def _schema_check(root: Path, name: str, value: Any, label: str) -> None:
    errors = sorted(_validator(root, name).iter_errors(value), key=lambda e: list(e.path))
    if errors:
        raise QueueAdmissionError(f"{label} schema validation failed: {errors[0].message}")


def _equal(label: str, *values: Any) -> None:
    if not values or any(value != values[0] for value in values[1:]):
        raise QueueAdmissionError(f"{label} mismatch")


def _validate_gate_c_record(root: Path, ref: Mapping[str, Any], spec: Mapping[str, Any], spec_hash: str) -> None:
    if ref.get("audit_path") != GATE_C_AUDIT:
        raise QueueAdmissionError("Gate-C audit path mismatch")
    audit = _repo_path(root, GATE_C_AUDIT, "Gate-C audit path")
    if audit.is_symlink() or not audit.is_file():
        raise QueueAdmissionError("Gate-C audit must be a regular non-symlink file")
    lines = audit.read_bytes().splitlines(keepends=True)
    number = ref.get("line_number")
    if not isinstance(number, int) or number < 1 or number > len(lines):
        raise QueueAdmissionError("Gate-C audit line does not exist")
    raw = lines[number - 1]
    if not raw.endswith(b"\n"):
        raise QueueAdmissionError("Gate-C audit referenced record lacks its required line terminator")
    if _digest(raw) != ref.get("raw_record_sha256"):
        raise QueueAdmissionError("Gate-C audit raw-record hash mismatch")
    try:
        record = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise QueueAdmissionError("Gate-C audit record is invalid") from exc
    expected = {"approval_id": ref.get("gate_c_approval_id"), "strategy_spec_id": ref.get("strategy_spec_id"), "canonical_target_path": ref.get("canonical_target_path"), "approved_content_sha256": spec_hash}
    if any(record.get(key) != value for key, value in expected.items()):
        raise QueueAdmissionError("Gate-C audit identity/content binding mismatch")
    matches = 0
    for candidate_raw in lines:
        try:
            candidate = json.loads(candidate_raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise QueueAdmissionError("Gate-C audit contains an invalid record") from exc
        if all(candidate.get(key) == value for key, value in expected.items()):
            matches += 1
    if matches != 1:
        raise QueueAdmissionError("Gate-C audit must contain exactly one matching record")
    if spec.get("strategy_spec_id") != ref.get("strategy_spec_id"):
        raise QueueAdmissionError("Strategy Spec ID does not match Gate-C audit")


def _validate_artifact_validators(root: Path, spec_path: Path, vm_path: Path, sweep_path: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="gate-q-validation-") as temp:
        base = Path(temp)
        specs, vms, sweeps = base / "strategy_specs", base / "variant_manifests", base / "sweep_plans"
        for directory in (specs, vms, sweeps):
            directory.mkdir()
        shutil.copy2(spec_path, specs / spec_path.name)
        shutil.copy2(vm_path, vms / vm_path.name)
        shutil.copy2(sweep_path, sweeps / sweep_path.name)
        errors = validate_strategy_specs(specs, root / "research/schemas/strategy_spec.schema.json", root)
        errors += validate_variant_sweep_artifacts(vms, sweeps, specs, root / "research/schemas/variant_manifest.schema.json", root / "research/schemas/sweep_plan.schema.json", root / "research/schemas/strategy_spec.schema.json", root)
        if errors:
            raise QueueAdmissionError("artifact validator failed: " + errors[0])


def _validate_dataset(root: Path, dataset: Mapping[str, Any], spec: Mapping[str, Any], sweep: Mapping[str, Any]) -> None:
    path, _ = _verify_ref(root, {"path": dataset.get("path"), "sha256": dataset.get("sha256")}, "dataset")
    del path
    if dataset.get("market") != "BTCUSDT_BINANCE_USDTM_PERPETUAL":
        raise QueueAdmissionError("dataset market mismatch")
    timeframe = dataset.get("timeframe")
    spec_tf = spec.get("timeframe_and_data", {}).get("primary_timeframe")
    sweep_tf = sweep.get("data_and_timeframe_assumptions", {}).get("primary_timeframe")
    _equal("dataset timeframe", timeframe, spec_tf, sweep_tf)
    if not dataset.get("dataset_id") or not dataset.get("snapshot_version"):
        raise QueueAdmissionError("dataset identity/version is unresolved")


def _read_audit(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    if path.is_symlink() or not path.is_file():
        raise QueueAdmissionError("admission audit must be a regular non-symlink file")
    try:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise QueueAdmissionError("existing admission audit is unreadable") from exc


def _check_reuse(records: list[dict[str, Any]], approval_id: str, item_id: str, target: str) -> None:
    if any(r.get("gate_q_approval_id") == approval_id or r.get("queue_item_id") == item_id or r.get("queue_item_path") == target for r in records):
        raise QueueAdmissionError("Gate-Q approval, queue-item ID, or target path was already used")


@contextmanager
def _crossing_lock(root: Path):
    path = _repo_path(root, LOCK_PATH.as_posix(), "queue admission lock path")
    path.parent.mkdir(parents=True, exist_ok=True)
    state = {"crossing_committed": False}
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise QueueAdmissionError("queue admission lock exists; operator inspection required") from exc
    try:
        os.write(fd, f"pid={os.getpid()}\n".encode())
        os.fsync(fd)
        os.close(fd)
        fd = -1
        yield state
    finally:
        if fd >= 0:
            os.close(fd)
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        except OSError as exc:
            suffix = " admission committed; automatic retry forbidden" if state["crossing_committed"] else ""
            raise QueueAdmissionIntegrityCriticalError("queue lock cleanup failed; operator inspection required;" + suffix) from exc


def _open_audit(path: Path) -> tuple[BinaryIO, bool]:
    try:
        return path.open("x+b"), True
    except FileExistsError:
        return path.open("r+b"), False


def admit_queue_item(*, repo_root: Path, gate_q_path: Path, proposed_queue_item_path: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    gate, gate_raw = _load_object(gate_q_path.resolve(), "Gate-Q approval")
    item, item_raw = _load_object(proposed_queue_item_path.resolve(), "proposed queue item")
    _schema_check(root, "gate_q_approval.schema.json", gate, "Gate-Q approval")
    _schema_check(root, "canon_queue_item.schema.json", item, "queue item")
    approval_id, item_id = gate["approval_id"], item["queue_item_id"]
    gate_rel = (APPROVAL_ROOT / f"{approval_id}.gate_q_approval.json").as_posix()
    authoritative_gate = _repo_path(root, gate_rel, "Gate-Q authoritative path")
    if gate.get("approval_artifact_target_path") != gate_rel or gate_q_path.resolve() != authoritative_gate:
        raise QueueAdmissionError("Gate-Q approval is not at its authoritative ID-derived path")
    proposed = gate["proposed_queue_item"]
    target_rel = (ADMISSION_ROOT / f"{item_id}.queue_item.json").as_posix()
    _equal("queue-item ID", proposed.get("queue_item_id"), item_id)
    _equal("queue-item target", proposed.get("target_path"), target_rel)
    if proposed.get("bytes_sha256") != _digest(item_raw):
        raise QueueAdmissionError("exact proposed queue-item bytes hash mismatch")
    core_hash = approval_core_sha256(gate)
    _equal("approval core", core_hash, gate.get("approval_core_sha256"), item.get("gate_q", {}).get("approval_core_sha256"))
    _equal("Gate-Q binding", approval_id, item["gate_q"].get("approval_id"))
    _equal("Gate-Q path binding", gate_rel, item["gate_q"].get("path"))
    try:
        admitted = datetime.fromisoformat(item["admitted_at"].replace("Z", "+00:00"))
    except (ValueError, TypeError) as exc:
        raise QueueAdmissionError("admitted_at is invalid") from exc
    if item_id[3:11] != admitted.strftime("%Y%m%d"):
        raise QueueAdmissionError("queue-item ID date does not equal admitted_at UTC date")
    for name in ("strategy_spec", "variant_manifest", "sweep_plan"):
        _equal(f"{name} reference", gate["artifact_refs"].get(name), item["artifact_refs"].get(name))
    for name in ("source_draft", "review_trail", "eligibility_report", "gate_c_approval"):
        _equal(f"{name} lineage", gate["lineage"].get(name), item["lineage"].get(name))
        _verify_ref(root, gate["lineage"][name], name)
    _equal("Gate-C audit reference", gate["artifact_refs"]["gate_c_crossing_audit_record"], item["lineage"]["gate_c_crossing_audit_record"])
    spec_path, spec_raw = _verify_ref(root, gate["artifact_refs"]["strategy_spec"], "Strategy Spec")
    vm_path, vm_raw = _verify_ref(root, gate["artifact_refs"]["variant_manifest"], "Variant Manifest")
    sweep_path, sweep_raw = _verify_ref(root, gate["artifact_refs"]["sweep_plan"], "Sweep Plan")
    spec, vm, sweep = (json.loads(raw.decode("utf-8")) for raw in (spec_raw, vm_raw, sweep_raw))
    if gate["artifact_refs"]["strategy_spec"]["path"] != f"research/strategy_specs/{spec.get('strategy_spec_id')}.strategy_spec.json":
        raise QueueAdmissionError("Strategy Spec ID/path binding mismatch")
    _validate_gate_c_record(root, gate["artifact_refs"]["gate_c_crossing_audit_record"], spec, _digest(spec_raw))
    _validate_artifact_validators(root, spec_path, vm_path, sweep_path)
    spec_id = spec.get("strategy_spec_id")
    _equal("VM/Sweep Strategy Spec ID", spec_id, vm.get("parent_strategy_spec", {}).get("strategy_spec_id"), sweep.get("lineage", {}).get("parent_strategy_spec_ref", {}).get("ref_id"))
    _equal("Sweep/VM ID", vm.get("variant_manifest_id"), sweep.get("parent_variant_manifest", {}).get("variant_manifest_id"))
    count = gate["denominator"]["committed_population_count"]
    vm_gov = vm.get("population_governance", {})
    _equal("committed denominator", count, gate["denominator"]["variant_manifest_value"], gate["denominator"]["sweep_plan_value"], item["denominator"]["committed_population_count"], vm_gov.get("declared_population", {}).get("committed_population_count"), vm_gov.get("trial_budget", {}).get("trial_budget_denominator"), sweep.get("trial_accounting", {}).get("committed_population_count"), sweep.get("trial_accounting", {}).get("multiple_testing_denominator"), sweep.get("parent_variant_manifest", {}).get("manifest_committed_population_count"))
    _equal("dataset", gate["dataset"], item["dataset"])
    _validate_dataset(root, gate["dataset"], spec, sweep)
    _equal("budget", gate["budget"], item["budget"])
    if gate["budget"].get("upper_bound") != count:
        raise QueueAdmissionError("budget upper bound must equal committed denominator")
    _equal("priority", gate["priority"], item["priority"])
    _equal("queue target", gate["queue_target"], item["queue_target"])
    required_hashes = {_digest(raw) for raw in (spec_raw, vm_raw, sweep_raw)} | {gate["dataset"]["sha256"]} | {ref["sha256"] for ref in gate["lineage"].values()}
    if not required_hashes <= set(item.get("traceability_hashes", [])):
        raise QueueAdmissionError("queue-item traceability hashes are incomplete")
    target = _repo_path(root, target_rel, "queue-item target")
    audit = _repo_path(root, AUDIT_PATH.as_posix(), "admission audit path")
    target.parent.mkdir(parents=True, exist_ok=True)
    audit.parent.mkdir(parents=True, exist_ok=True)
    record = {"schema_version": "queue_admission_audit_record_v1", "audit_record_id": f"QAUDIT-{item_id}", "queue_item_id": item_id, "queue_item_path": target_rel, "queue_item_sha256": _digest(item_raw), "gate_q_approval_id": approval_id, "gate_q_approval_path": gate_rel, "gate_q_approval_file_sha256": _digest(gate_raw), "gate_q_approval_core_sha256": core_hash, "strategy_spec_id": spec_id, "strategy_spec_path": gate["artifact_refs"]["strategy_spec"]["path"], "strategy_spec_sha256": _digest(spec_raw), "variant_manifest_path": gate["artifact_refs"]["variant_manifest"]["path"], "variant_manifest_sha256": _digest(vm_raw), "sweep_plan_path": gate["artifact_refs"]["sweep_plan"]["path"], "sweep_plan_sha256": _digest(sweep_raw), "admitted_at": item["admitted_at"], "writer_version": WRITER_VERSION, "validation_outcome": "passed_before_admission", "no_dispatch": True, "no_execution": True}
    _schema_check(root, "queue_admission_audit_record.schema.json", record, "admission audit record")
    line = repo_canonical_json_v1(record) + b"\n"
    with _crossing_lock(root) as state:
        _check_reuse(_read_audit(audit), approval_id, item_id, target_rel)
        if target.exists() or target.is_symlink():
            raise QueueAdmissionError("queue-item target already exists; overwrite is forbidden")
        handle = None
        created_audit = False
        prior_length = 0
        created_target = False
        try:
            with target.open("xb") as output:
                created_target = True
                if output.write(item_raw) != len(item_raw):
                    raise OSError("partial queue-item write")
                output.flush(); os.fsync(output.fileno())
            handle, created_audit = _open_audit(audit)
            handle.seek(0, os.SEEK_END); prior_length = handle.tell()
            if handle.write(line) != len(line):
                raise OSError("partial audit append")
            handle.flush(); os.fsync(handle.fileno()); handle.close()
            state["crossing_committed"] = True
            return record
        except (OSError, ValueError) as exc:
            failures = []
            if handle is not None:
                try:
                    handle.seek(prior_length); handle.truncate(); handle.flush(); os.fsync(handle.fileno()); handle.close()
                    if created_audit and prior_length == 0: audit.unlink()
                except OSError as rollback: failures.append(f"audit rollback failed: {rollback}")
            if created_target:
                try: target.unlink()
                except OSError as rollback: failures.append(f"queue-item rollback failed: {rollback}")
            if failures:
                raise QueueAdmissionIntegrityCriticalError("; ".join(failures) + "; automatic retry forbidden") from exc
            raise QueueAdmissionError("admission crossing failed and was rolled back") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate-q", type=Path, required=True)
    parser.add_argument("--proposed-queue-item", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        record = admit_queue_item(repo_root=args.repo_root, gate_q_path=args.gate_q, proposed_queue_item_path=args.proposed_queue_item)
    except QueueAdmissionError as exc:
        parser.exit(2, f"Gate-Q queue admission stopped: {exc}\n")
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
