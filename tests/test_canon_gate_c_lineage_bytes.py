import hashlib
import json
from pathlib import Path

import tools.canon_intake.spec_writer as spec_writer
from tools.registry.validate_strategy_specs import validate_strategy_specs


REPO_ROOT = Path(__file__).resolve().parents[1]
DRAFT_PATH = Path(
    "scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/"
    "AIDRAFT-2B5725C1A8349863.draft_packet.json"
)
ELIGIBILITY_PATH = Path(
    "scratch/WP-CANON-ELIGIBILITY-VALIDATOR-01/reports/"
    "AIDRAFT-2B5725C1A8349863.eligibility_report.json"
)
REVIEW_PATH = Path(
    "scratch/WP-DASH-AGENT-INBOX-WRITE-01A/reviews/"
    "AIDRAFT-2B5725C1A8349863.review_events.jsonl"
)
APPROVAL_PATH = Path(
    "scratch/WP-CANON-FIRST-GATE-C-CROSSING-GATED-02C/approvals/"
    "GATE-C-H004-R2-0001.gate_c_approval.json"
)
FROZEN_APPROVAL_PATH = Path(
    "scratch/WP-CANON-FIRST-GATE-C-CROSSING-GATED-02C/"
    "frozen_gate_c_approval.json"
)
AUDIT_PATH = Path("research/canonical_crossing_audit/strategy_spec_writes.jsonl")
SPEC_PATH = Path("research/strategy_specs/STRAT-SPEC-0007.strategy_spec.json")

EXPECTED_HASHES = {
    "source_draft": "sha256:7c4e53c5cceefc23dc2c242102c0a5c744355d7fafff4ebd892944cf13c5193a",
    "eligibility_report": "sha256:76a0654144d215d62932568b5627d6838f3613e36238bebccaac25d55b873dd9",
    "review_trail": "sha256:a0e3174758316a18ff0f4f207886d2cb1704eaad609e397fd1aee1e0f4339230",
    "approval": "sha256:b05753fe01cc99aa2c4f0e419fca88f4f843154f12843f01aae775eb1e4e68cd",
    "audit_line": "sha256:ef5a452a4aff61a35fdbdfcf16162362400345f28af67b7bb41aa4ae36024be2",
    "strategy_spec": "sha256:b23ebc1093df51b7fab5e39c46fd2b96b5e71d35300134eb319a5cbc32d0857c",
}
EXPECTED_SEMANTIC_HASHES = {
    "source_draft": "sha256:0f4aed048b37927a14269d1b94f8e1e9bdee7bc224fe38d64d23ce12450e1c22",
    "eligibility_report": "sha256:3436ce41e22b61e279ed76fe76bd4e7f1cd7e5bf042eae7c1170263009d7adbe",
}


def _sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _semantic_sha256(value: object) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return _sha256(raw)


def _assert_crlf_only(raw: bytes) -> None:
    assert b"\r\n" in raw
    assert b"\r" not in raw.replace(b"\r\n", b"")
    assert b"\n" not in raw.replace(b"\r\n", b"")


def test_h004_r2_gate_c_lineage_replays_from_immutable_attested_bytes():
    draft_raw = (REPO_ROOT / DRAFT_PATH).read_bytes()
    eligibility_raw = (REPO_ROOT / ELIGIBILITY_PATH).read_bytes()
    review_raw = (REPO_ROOT / REVIEW_PATH).read_bytes()
    approval_raw = (REPO_ROOT / APPROVAL_PATH).read_bytes()
    spec_raw = (REPO_ROOT / SPEC_PATH).read_bytes()

    _assert_crlf_only(draft_raw)
    _assert_crlf_only(eligibility_raw)
    assert _sha256(draft_raw) == EXPECTED_HASHES["source_draft"]
    assert _sha256(eligibility_raw) == EXPECTED_HASHES["eligibility_report"]
    assert _sha256(review_raw) == EXPECTED_HASHES["review_trail"]
    assert _sha256(approval_raw) == EXPECTED_HASHES["approval"]
    assert approval_raw == (REPO_ROOT / FROZEN_APPROVAL_PATH).read_bytes()
    assert _sha256(spec_raw) == EXPECTED_HASHES["strategy_spec"]

    draft = json.loads(draft_raw.decode("utf-8"))
    eligibility = json.loads(eligibility_raw.decode("utf-8"))
    approval = json.loads(approval_raw.decode("utf-8"))
    spec = json.loads(spec_raw.decode("utf-8"))
    assert _semantic_sha256(draft) == EXPECTED_SEMANTIC_HASHES["source_draft"]
    assert (
        _semantic_sha256(eligibility)
        == EXPECTED_SEMANTIC_HASHES["eligibility_report"]
    )

    audit_lines = (REPO_ROOT / AUDIT_PATH).read_bytes().splitlines(keepends=True)
    assert len(audit_lines) == 1
    assert _sha256(audit_lines[0]) == EXPECTED_HASHES["audit_line"]
    audit = json.loads(audit_lines[0].decode("utf-8"))
    assert audit["approval_id"] == "GATE-C-H004-R2-0001"
    assert approval["approval_id"] == audit["approval_id"]
    assert audit["approval_record_sha256"] == EXPECTED_HASHES["approval"]
    assert audit["canonical_target_path"] == SPEC_PATH.as_posix()
    assert audit["approved_content_sha256"] == EXPECTED_HASHES["strategy_spec"]

    refs = {}
    for name in ("source_draft", "review_trail", "eligibility_report"):
        approval_ref = approval[name]
        audit_ref = audit[name]
        assert audit_ref["path"] == approval_ref["path"]
        assert audit_ref["sha256"] == approval_ref["sha256"]
        refs[name] = spec_writer._verify_ref(REPO_ROOT, approval_ref, name)

    spec_writer._validate_draft(
        draft,
        refs["source_draft"][0],
        approval["source_draft_id"],
        approval["source_hashes"],
    )
    review_summary = spec_writer._validate_reviews(
        refs["review_trail"][3], approval["source_draft_id"]
    )
    spec_writer._validate_eligibility(
        eligibility, approval["source_draft_id"], refs, review_summary
    )
    spec_writer._independent_checks(
        spec, audit["canonical_target_path"], refs, approval["approval_id"]
    )

    assert eligibility["source_draft_path"] == DRAFT_PATH.as_posix()
    assert eligibility["source_draft_hash"] == EXPECTED_HASHES["source_draft"]
    assert any(
        item == {
            "path": DRAFT_PATH.as_posix(),
            "sha256": EXPECTED_HASHES["source_draft"],
        }
        for item in eligibility["source_artifacts_read"]
    )
    assert validate_strategy_specs(repo_root=REPO_ROOT) == []
    assert sum(
        1
        for path in (REPO_ROOT / "research/strategy_specs").glob(
            "STRAT-SPEC-0007.strategy_spec.json"
        )
        if path.is_file()
    ) == 1
