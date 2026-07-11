import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

import tools.canon_intake.spec_writer as writer
from tools.canon_intake.spec_writer import GateCWriteError, write_approved_strategy_spec


def _sha(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _write(path: Path, value: object) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(raw)
    return raw


def _fixture_repo(tmp_path: Path, source_repo: Path):
    shutil.copytree(source_repo / "research/schemas", tmp_path / "research/schemas")
    shutil.copytree(source_repo / "research/strategy_specs", tmp_path / "research/strategy_specs")
    draft_id = "AIDRAFT-0123456789ABCDEF"
    draft = json.loads((source_repo / "scratch/WP-DASH-AGENT-INBOX-WRITE-01A/sample_draft_packet.json").read_text(encoding="utf-8"))
    draft["draft_id"] = draft_id
    draft["provenance"]["output_path"] = f"scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/{draft_id}.draft_packet.json"
    draft_path = tmp_path / draft["provenance"]["output_path"]
    draft_raw = _write(draft_path, draft)
    review_path = tmp_path / f"scratch/WP-DASH-AGENT-INBOX-WRITE-01A/reviews/{draft_id}.review_events.jsonl"
    review = {"schema_version": "agent_inbox_draft_review_event_v1", "event_id": "AIREVIEW-0123456789ABCDEF", "draft_id": draft_id, "append_index": 1, "review_state": "reviewed", "reviewer_label": "Karl-test-fixture", "timestamp_utc": "2026-07-10T11:00:00Z", "rationale": "Reviewed for isolated writer test.", "clarification_request": None, "non_authority_flags": {"scratch_only": True, "annotation_only": True, "not_canonicalization_approval": True, "not_queue_admission": True, "not_research_execution": True, "not_candidate_creation": True, "not_runtime_action": True}}
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_raw = (json.dumps(review, sort_keys=True, separators=(",", ":")) + "\n").encode()
    review_path.write_bytes(review_raw)
    refs = {"source_draft": {"path": draft_path.relative_to(tmp_path).as_posix(), "sha256": _sha(draft_raw)}, "review_trail": {"path": review_path.relative_to(tmp_path).as_posix(), "sha256": _sha(review_raw)}}
    eligibility = {"schema_version": "canon_intake_eligibility_report_v1", "draft_id": draft_id, "source_draft_path": refs["source_draft"]["path"], "source_draft_hash": refs["source_draft"]["sha256"], "review_trail_path": refs["review_trail"]["path"], "review_trail_hash": refs["review_trail"]["sha256"], "reviewed_state_summary": {"event_count": 1, "latest_state": "reviewed", "flagged_for_canonicalization": False}, "eligibility_status": "eligible_for_gate_c_review", "advisory_only": True, "canonical_authority": False, "gate_c_authority": False, "queue_authority": False, "non_authority_flags": {"not_approval": True, "not_canonical_write": True, "not_gate_c": True, "not_queue_admission": True, "not_candidate_creation": True, "not_research_execution": True, "not_runtime_action": True}}
    eligibility_path = tmp_path / f"scratch/WP-CANON-ELIGIBILITY-VALIDATOR-01/reports/{draft_id}.eligibility_report.json"
    eligibility_raw = _write(eligibility_path, eligibility)
    refs["eligibility_report"] = {"path": eligibility_path.relative_to(tmp_path).as_posix(), "sha256": _sha(eligibility_raw)}
    spec = json.loads((source_repo / "research/strategy_specs/STRAT-SPEC-0006.strategy_spec.json").read_text(encoding="utf-8"))
    spec["strategy_spec_id"] = "STRAT-SPEC-9999"
    spec["title"] = "Gate C fixture exact-content spec"
    spec["provenance"]["source_refs"] = [f"{name}:{refs[name]['path']}#{refs[name]['sha256']}" for name in ("source_draft", "review_trail", "eligibility_report")] + ["gate_c_approval:GATE-C-TEST-0001"]
    proposed = tmp_path / "scratch/proposed.json"
    proposed_raw = _write(proposed, spec)
    gate = {
        "schema_version": "gate_c_strategy_spec_approval_v1",
        "approval_id": "GATE-C-TEST-0001",
        "approved_by": "Karl",
        "approved_at": "2026-07-10T12:00:00Z",
        "approval_scope": "one_append_only_canonical_strategy_spec_write",
        "source_draft_id": draft_id,
        "source_hashes": draft["source_hashes"],
        "content_reviewed": True,
        "authorizes_canonical_write": True,
        "append_only": True,
        "exact_content_and_target_only": True,
        "authorizes_queue": False,
        "authorizes_execution": False,
        "authorizes_candidate_lifecycle": False,
        "authorizes_promotion_readiness": False,
        "authorizes_paper_live_runtime": False,
        "authorizes_scheduler_autonomy": False,
        "authorizes_notifications": False,
        "approved_content_sha256": _sha(proposed_raw),
        "canonical_target_path": "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json",
        **refs,
    }
    gate_path = tmp_path / "scratch/gate_c.json"
    _write(gate_path, gate)
    return proposed, gate_path, gate


def _run(repo: Path, proposed: Path, gate: Path):
    return write_approved_strategy_spec(repo_root=repo, proposed_content_path=proposed, gate_c_path=gate, now=datetime(2026, 7, 10, 12, 30, tzinfo=timezone.utc))


def _assert_no_write(repo: Path):
    assert not (repo / "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json").exists()
    assert not (repo / "research/canonical_crossing_audit/strategy_spec_writes.jsonl").exists()


def _replace_source(repo: Path, proposed: Path, gate_path: Path, gate: dict, name: str, value: object, *, jsonl=False):
    path = repo / gate[name]["path"]
    raw = ((json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n") if jsonl else (json.dumps(value, indent=2, sort_keys=True) + "\n")).encode()
    path.write_bytes(raw)
    gate[name]["sha256"] = _sha(raw)
    spec = json.loads(proposed.read_text(encoding="utf-8"))
    spec["provenance"]["source_refs"] = [f"{key}:{gate[key]['path']}#{gate[key]['sha256']}" for key in ("source_draft", "review_trail", "eligibility_report")] + [f"gate_c_approval:{gate['approval_id']}"]
    proposed_raw = _write(proposed, spec)
    gate["approved_content_sha256"] = _sha(proposed_raw)
    _write(gate_path, gate)


def test_no_gate_c_no_write(tmp_path, repo_root):
    proposed, gate, _ = _fixture_repo(tmp_path, repo_root)
    gate.unlink()
    with pytest.raises(GateCWriteError):
        _run(tmp_path, proposed, gate)
    _assert_no_write(tmp_path)


def test_eligibility_or_flag_without_gate_c_has_no_authority(tmp_path, repo_root):
    proposed, gate, _ = _fixture_repo(tmp_path, repo_root)
    gate.unlink()
    _write(tmp_path / "scratch/eligibility_only.json", {"eligibility_status": "eligible_for_gate_c_review", "review_state": "flagged_for_canonicalization"})
    with pytest.raises(GateCWriteError):
        _run(tmp_path, proposed, gate)
    _assert_no_write(tmp_path)


@pytest.mark.parametrize("field,value", [("approved_content_sha256", "sha256:" + "0" * 64), ("canonical_target_path", "research/strategy_specs/STRAT-SPEC-9998.strategy_spec.json")])
def test_hash_or_target_mismatch_no_write(tmp_path, repo_root, field, value):
    proposed, gate_path, gate = _fixture_repo(tmp_path, repo_root)
    gate[field] = value
    _write(gate_path, gate)
    with pytest.raises(GateCWriteError):
        _run(tmp_path, proposed, gate_path)
    _assert_no_write(tmp_path)


def test_target_exists_no_overwrite(tmp_path, repo_root):
    proposed, gate, _ = _fixture_repo(tmp_path, repo_root)
    target = tmp_path / "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json"
    target.write_text("existing\n", encoding="utf-8")
    with pytest.raises(GateCWriteError):
        _run(tmp_path, proposed, gate)
    assert target.read_text(encoding="utf-8") == "existing\n"
    assert not (tmp_path / "research/canonical_crossing_audit/strategy_spec_writes.jsonl").exists()


def test_exclusive_create_collision_fails_without_audit(tmp_path, repo_root, monkeypatch):
    proposed, gate_path, _ = _fixture_repo(tmp_path, repo_root)
    original = Path.open
    def collide(path, mode="r", *args, **kwargs):
        if path.name == "STRAT-SPEC-9999.strategy_spec.json" and mode == "xb":
            raise FileExistsError("simulated concurrent create")
        return original(path, mode, *args, **kwargs)
    monkeypatch.setattr(Path, "open", collide)
    with pytest.raises(GateCWriteError, match="crossing rolled back"):
        _run(tmp_path, proposed, gate_path)
    _assert_no_write(tmp_path)


def test_malformed_spec_rejected_even_when_eligibility_says_eligible(tmp_path, repo_root):
    proposed, gate_path, gate = _fixture_repo(tmp_path, repo_root)
    spec = json.loads(proposed.read_text(encoding="utf-8"))
    del spec["entry_logic"]
    raw = _write(proposed, spec)
    gate["approved_content_sha256"] = _sha(raw)
    _write(gate_path, gate)
    with pytest.raises(GateCWriteError, match="structural validation"):
        _run(tmp_path, proposed, gate_path)
    _assert_no_write(tmp_path)


def test_valid_gate_writes_exact_bytes_and_appends_audit(tmp_path, repo_root):
    proposed, gate_path, gate = _fixture_repo(tmp_path, repo_root)
    raw = proposed.read_bytes()
    audit = tmp_path / "research/canonical_crossing_audit/strategy_spec_writes.jsonl"
    audit.parent.mkdir(parents=True)
    audit.write_text(json.dumps({"strategy_spec_id": "STRAT-SPEC-9000", "canonical_target_path": "research/strategy_specs/STRAT-SPEC-9000.strategy_spec.json"}) + "\n", encoding="utf-8")
    first = _run(tmp_path, proposed, gate_path)
    target = tmp_path / gate["canonical_target_path"]
    assert target.read_bytes() == raw
    assert first["eligibility_report"]["advisory_only"] is True
    assert len(audit.read_text(encoding="utf-8").splitlines()) == 2
    assert not (tmp_path / "research/queue").exists()
    assert not (tmp_path / "research/candidates").exists()


def test_audit_prevents_reuse_after_target_removed(tmp_path, repo_root):
    proposed, gate_path, gate = _fixture_repo(tmp_path, repo_root)
    _run(tmp_path, proposed, gate_path)
    (tmp_path / gate["canonical_target_path"]).unlink()
    with pytest.raises(GateCWriteError, match="audit already records"):
        _run(tmp_path, proposed, gate_path)


def test_wrong_draft_id_and_arbitrary_hash_valid_draft_fail(tmp_path, repo_root):
    proposed, gate_path, gate = _fixture_repo(tmp_path, repo_root)
    draft = json.loads((tmp_path / gate["source_draft"]["path"]).read_text())
    draft["draft_id"] = "AIDRAFT-FFFFFFFFFFFFFFFF"
    _replace_source(tmp_path, proposed, gate_path, gate, "source_draft", draft)
    with pytest.raises(GateCWriteError, match="identity"):
        _run(tmp_path, proposed, gate_path)
    _assert_no_write(tmp_path)


@pytest.mark.parametrize("state", ["rejected", "needs_clarification"])
def test_review_wrong_lineage_order_or_terminal_state_fails(tmp_path, repo_root, state):
    proposed, gate_path, gate = _fixture_repo(tmp_path, repo_root)
    review = json.loads((tmp_path / gate["review_trail"]["path"]).read_text())
    review["review_state"] = state
    _replace_source(tmp_path, proposed, gate_path, gate, "review_trail", review, jsonl=True)
    with pytest.raises(GateCWriteError, match="latest review state"):
        _run(tmp_path, proposed, gate_path)


def test_review_wrong_draft_and_broken_append_order_fail(tmp_path, repo_root):
    for field, value in (("draft_id", "AIDRAFT-FFFFFFFFFFFFFFFF"), ("append_index", 2)):
        repo = tmp_path / field
        proposed, gate_path, gate = _fixture_repo(repo, repo_root)
        review = json.loads((repo / gate["review_trail"]["path"]).read_text())
        review[field] = value
        _replace_source(repo, proposed, gate_path, gate, "review_trail", review, jsonl=True)
        with pytest.raises(GateCWriteError, match="review event contract"):
            _run(repo, proposed, gate_path)


@pytest.mark.parametrize("field,value", [("draft_id", "AIDRAFT-FFFFFFFFFFFFFFFF"), ("canonical_authority", True), ("source_draft_hash", "sha256:" + "0" * 64)])
def test_eligibility_identity_lineage_and_authority_fail(tmp_path, repo_root, field, value):
    proposed, gate_path, gate = _fixture_repo(tmp_path, repo_root)
    report = json.loads((tmp_path / gate["eligibility_report"]["path"]).read_text())
    report[field] = value
    _replace_source(tmp_path, proposed, gate_path, gate, "eligibility_report", report)
    with pytest.raises(GateCWriteError, match="eligibility report"):
        _run(tmp_path, proposed, gate_path)


def test_gate_source_hash_mismatch_and_generic_provenance_fail(tmp_path, repo_root):
    proposed, gate_path, gate = _fixture_repo(tmp_path, repo_root)
    gate["source_hashes"]["source_request_sha256"] = "sha256:" + "0" * 64
    _write(gate_path, gate)
    with pytest.raises(GateCWriteError, match="source_hashes"):
        _run(tmp_path, proposed, gate_path)
    proposed, gate_path, gate = _fixture_repo(tmp_path / "generic", repo_root)
    spec = json.loads(proposed.read_text())
    spec["provenance"]["source_refs"] = ["generic"]
    raw = _write(proposed, spec)
    gate["approved_content_sha256"] = _sha(raw)
    _write(gate_path, gate)
    with pytest.raises(GateCWriteError, match="provenance"):
        _run(tmp_path / "generic", proposed, gate_path)


def test_approval_id_is_single_use_across_different_target(tmp_path, repo_root):
    proposed, gate_path, gate = _fixture_repo(tmp_path, repo_root)
    _run(tmp_path, proposed, gate_path)
    (tmp_path / gate["canonical_target_path"]).unlink()
    spec = json.loads(proposed.read_text())
    spec["strategy_spec_id"] = "STRAT-SPEC-9998"
    raw = _write(proposed, spec)
    gate["canonical_target_path"] = "research/strategy_specs/STRAT-SPEC-9998.strategy_spec.json"
    gate["approved_content_sha256"] = _sha(raw)
    _write(gate_path, gate)
    audit_before = (tmp_path / writer.AUDIT_PATH).read_bytes()
    with pytest.raises(GateCWriteError, match="approval_id"):
        _run(tmp_path, proposed, gate_path)
    assert (tmp_path / writer.AUDIT_PATH).read_bytes() == audit_before
    assert not (tmp_path / gate["canonical_target_path"]).exists()


def test_audit_open_failure_removes_new_target(tmp_path, repo_root, monkeypatch):
    proposed, gate_path, _ = _fixture_repo(tmp_path, repo_root)
    monkeypatch.setattr(writer, "_open_audit", lambda path: (_ for _ in ()).throw(OSError("injected open failure")))
    with pytest.raises(GateCWriteError, match="rolled back"):
        _run(tmp_path, proposed, gate_path)
    _assert_no_write(tmp_path)


def test_partial_audit_write_restores_original_bytes(tmp_path, repo_root, monkeypatch):
    proposed, gate_path, _ = _fixture_repo(tmp_path, repo_root)
    audit = tmp_path / writer.AUDIT_PATH
    audit.parent.mkdir(parents=True)
    original = b'{"approval_id":"older"}\n'
    audit.write_bytes(original)
    class Partial:
        def __init__(self, handle): self.handle = handle
        def __getattr__(self, name): return getattr(self.handle, name)
        def write(self, data):
            self.handle.write(data[:7])
            return 7
    monkeypatch.setattr(writer, "_open_audit", lambda path: (Partial(path.open("r+b")), False))
    with pytest.raises(GateCWriteError, match="rolled back"):
        _run(tmp_path, proposed, gate_path)
    assert audit.read_bytes() == original
    assert not (tmp_path / "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json").exists()


def test_existing_lock_fails_closed(tmp_path, repo_root):
    proposed, gate_path, _ = _fixture_repo(tmp_path, repo_root)
    lock = tmp_path / writer.LOCK_PATH
    lock.parent.mkdir(parents=True)
    lock.write_text("stale-or-active\n")
    with pytest.raises(GateCWriteError, match="explicit operator inspection"):
        _run(tmp_path, proposed, gate_path)
    _assert_no_write(tmp_path)


@pytest.fixture
def repo_root():
    return Path(__file__).resolve().parents[1]
