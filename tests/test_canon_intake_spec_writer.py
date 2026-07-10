import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

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
    spec = json.loads((source_repo / "research/strategy_specs/STRAT-SPEC-0006.strategy_spec.json").read_text(encoding="utf-8"))
    spec["strategy_spec_id"] = "STRAT-SPEC-9999"
    spec["title"] = "Gate C fixture exact-content spec"
    spec["provenance"]["source_refs"] = ["scratch/draft.json", "scratch/review.jsonl", "scratch/eligibility.json"]
    proposed = tmp_path / "scratch/proposed.json"
    proposed_raw = _write(proposed, spec)
    refs = {}
    for name, value in (("source_draft", {"draft_id": "AIDRAFT-0123456789ABCDEF"}), ("review_trail", {"review_state": "reviewed"}), ("eligibility_report", {"eligibility_status": "eligible_for_gate_c_review", "advisory_only": True})):
        path = tmp_path / f"scratch/{name}.json"
        raw = _write(path, value)
        refs[name] = {"path": path.relative_to(tmp_path).as_posix(), "sha256": _sha(raw)}
    gate = {
        "schema_version": "gate_c_strategy_spec_approval_v1",
        "approval_id": "GATE-C-TEST-0001",
        "approved_by": "Karl",
        "approved_at": "2026-07-10T12:00:00Z",
        "approval_scope": "one_append_only_canonical_strategy_spec_write",
        "source_draft_id": "AIDRAFT-0123456789ABCDEF",
        "source_hashes": {"idea_sha256": "sha256:" + "1" * 64, "formalizer_sha256": "sha256:" + "2" * 64},
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


@pytest.fixture
def repo_root():
    return Path(__file__).resolve().parents[1]
