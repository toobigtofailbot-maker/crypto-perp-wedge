"""Proof-B receipt verifier. Every fixture here is labeled TEST_ONLY and can never yield B."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.hermes import model_origin_receipt as mor

SHA = "a" * 40
CRITIC = "Independent critic: funding regime risk is UNKNOWN and costs may dominate."
SOURCES = [{"id": "S1", "kind": "public", "url_or_uri": "https://example.org/a", "excerpt": "Funding resets every 8h."}]
IDEA = {
    "idea_id": "IDEA-1",
    "title": "Labeled fixture idea",
    "source_ids": ["S1"],
    "source_claims": [{"source_id": "S1", "claim": "c", "excerpt": "Funding resets every 8h."}],
    "critic_assessment": {"stance": "MIXED", "critic_excerpt": "costs may dominate"},
    "native_draft": None,
}


def _h(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def build(tmp_path: Path, *, observer=mor.TEST_OBSERVER, mutate=None):
    """Write a TEST_ONLY cycle and host receipt shaped exactly like research_turn.ps1 output."""
    cycle = tmp_path / "cycle"
    cycle.mkdir()
    texts = {
        "director-sources": json.dumps({"sources": SOURCES, "hypotheses": ["a", "b", "c"]}),
        "research-scout": "Scout comparison.",
        "research-critic": CRITIC,
        "director-synthesis": "Brief.",
        "director-intent": json.dumps({"schema_version": "cpw_hermes_structured_intent_handoff_v1", "ideas": [IDEA]}),
    }
    (cycle / "source_index.json").write_bytes(json.dumps(SOURCES).encode())
    invocations, turns, artifacts = [], [], {}
    for n, role in enumerate(mor.ROLES):
        name = mor.RESPONSE_FILES[role]
        raw = texts[role].encode() + b"\n"
        (cycle / name).write_bytes(raw)
        session = f"session-{role}-{n}x"
        obs = json.dumps([{"type": "result", "session_id": session, "exit_code": 0}]).encode()
        (cycle / f"{role}.observations.json").write_bytes(obs)
        prompt = _h(f"prompt-{role}".encode())
        invocations.append({"role": role, "invocation_id": f"inv-{n}", "exit_code": 0,
                            "session_id": session, "prompt_sha256": prompt,
                            "command": ["TEST_ONLY", role]})
        artifacts[name] = _h(raw)
        artifacts[f"{role}.observations.json"] = _h(obs)
        turns.append({"role": role, "invocation_id": f"inv-{n}", "started_utc": "t0", "finished_utc": "t1",
                      "docker_exit_code": 0, "session_id": session,
                      "command_sha256": _h(json.dumps(["TEST_ONLY", role], separators=(",", ":")).encode()),
                      "prompt_sha256": prompt, "stdout_sha256": _h(b"out" + bytes([n])),
                      "terminal_text_sha256": _h(texts[role].encode()), "response_file": name,
                      "response_file_sha256": _h(raw), "observations_file_sha256": _h(obs)})
    artifacts["source_index.json"] = _h((cycle / "source_index.json").read_bytes())
    manifest = {"state": "COMPLETED", "repo_sha": SHA, "invocations": invocations,
                "artifacts": [{"path": k, "sha256": v} for k, v in artifacts.items()]}
    receipt = {
        "schema_version": mor.RECEIPT_SCHEMA, "not_authority": True,
        "observer": {"identity": observer, "host_fingerprint_sha256": "b" * 64},
        "repo_sha": SHA, "repo_branch": "x", "compose_project": "cpw-hermes-research-t",
        "container_id": "c" * 12, "image_id": "sha256:" + "d" * 64, "image_ref": "hermes:t",
        "cycle_state": "COMPLETED", "cycle_directory": "cycle", "run_manifest_sha256": None,
        "role_order": list(mor.ROLES), "turns": turns, "assurance_limits": "x",
    }
    if mutate:
        mutate(cycle, manifest, receipt)
    (cycle / "run_manifest.json").write_bytes(json.dumps(manifest).encode())
    if receipt["run_manifest_sha256"] is None:
        receipt["run_manifest_sha256"] = _h((cycle / "run_manifest.json").read_bytes())
    path = tmp_path / "cycle.host-receipt.json"
    path.write_bytes(json.dumps(receipt).encode())
    return cycle, path


def verify(cycle, receipt, anchor="auto"):
    if anchor == "auto":
        anchor = _h(receipt.read_bytes())
    return mor.verify_origin(cycle, receipt, anchor_sha256=anchor, expected_repo_sha=SHA)


def test_consistent_test_fixture_is_fixture_only_never_b(tmp_path):
    result = verify(*build(tmp_path))
    assert result["status"] == mor.FIXTURE and result["B_verified"] is False
    assert result["ideas"] == [{"idea_id": "IDEA-1", "original_hypothesis_sha256": mor.di.canonical_sha256(IDEA)}]
    assert result["not_authority"] is True and "not provider-signed" in result["assurance_limits"]


def test_production_observer_without_or_with_wrong_anchor_is_blocked(tmp_path):
    cycle, receipt = build(tmp_path, observer=mor.OBSERVER)
    assert verify(cycle, receipt, anchor=None)["reason"] == "TRUST_ANCHOR_MISSING"
    assert verify(cycle, receipt, anchor="e" * 64)["reason"] == "TRUST_ANCHOR_MISMATCH"


def _turn(i, key, value):
    def mutate(cycle, manifest, receipt):
        receipt["turns"][i][key] = value
    return mutate


def _set(key, value):
    def mutate(cycle, manifest, receipt):
        receipt[key] = value
    return mutate


def _swap_roles(cycle, manifest, receipt):
    receipt["turns"][1], receipt["turns"][2] = receipt["turns"][2], receipt["turns"][1]


def _critic_substituted(cycle, manifest, receipt):
    raw = b"A different critic text.\n"
    (cycle / "critic_result.md").write_bytes(raw)


def _self_declared(cycle, manifest, receipt):
    idea = dict(IDEA, hermes_authored=True)
    text = json.dumps({"ideas": [idea]}).encode()
    (cycle / "structured_intent_drafts.json").write_bytes(text + b"\n")
    receipt["turns"][4].update(terminal_text_sha256=_h(text), response_file_sha256=_h(text + b"\n"))
    for a in manifest["artifacts"]:
        if a["path"] == "structured_intent_drafts.json":
            a["sha256"] = _h(text + b"\n")


def _stale_source_quote(cycle, manifest, receipt):
    (cycle / "source_index.json").write_bytes(json.dumps([dict(SOURCES[0], excerpt="Other text.")]).encode())


@pytest.mark.parametrize("mutate,reason", [
    (_set("image_id", "sha256:" + "0" * 64), "IMAGE_DIGEST"),
    (_set("repo_sha", "f" * 40), "REPO_SHA"),
    (_set("cycle_state", "FAILED"), "CYCLE_STATE"),
    (_set("run_manifest_sha256", "1" * 64), "RUN_MANIFEST_HASH"),
    (_set("observer", {"identity": "hermes", "host_fingerprint_sha256": "b" * 64}), "OBSERVER_IDENTITY"),
    (_set("extra_flag", True), "RECEIPT_KEYS"),
    (_swap_roles, "TURN_KEYS"),
    (_turn(0, "session_id", "aaaaaaaa"), "SESSION_PLACEHOLDER"),
    (_turn(1, "session_id", "invented-session-id"), "SESSION_BINDING"),
    (_turn(2, "prompt_sha256", "2" * 64), "PROMPT_BINDING"),
    (_turn(3, "stdout_sha256", "0" * 64), "ZERO_OR_MALFORMED_DIGEST"),
    (_turn(3, "terminal_text_sha256", "3" * 64), "TERMINAL_TEXT_HASH"),
    (_turn(4, "response_file_sha256", "4" * 64), "RESPONSE_HASH"),
    (_critic_substituted, "RESPONSE_HASH"),
    (_self_declared, "SELF_DECLARED_AUTHORSHIP"),
    (_stale_source_quote, "SOURCE_INDEX_HASH"),
])
def test_forged_or_mutated_receipts_are_blocked(tmp_path, mutate, reason):
    result = verify(*build(tmp_path, mutate=mutate))
    assert result["status"] == mor.BLOCKED and result["B_verified"] is False
    assert result["reason"] == reason


def test_copied_model_json_or_secret_text_is_blocked(tmp_path, monkeypatch):
    cycle, receipt = build(tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-marker-value-1234567890")
    (cycle / "scout_result.md").write_bytes(b"leak sk-test-marker-value-1234567890\n")
    assert verify(cycle, receipt)["reason"] == "CREDENTIAL_TEXT"


def test_receipt_reuse_against_other_cycle_is_blocked(tmp_path):
    (tmp_path / "one").mkdir()
    _cycle, receipt = build(tmp_path / "one")
    (tmp_path / "two").mkdir()
    other, _ = build(tmp_path / "two")
    (other / "scout_result.md").write_bytes(b"Different scout.\n")
    assert verify(other, receipt)["status"] == mor.BLOCKED


def test_consistent_unanchored_cohort_keeps_ideas_but_is_not_b(tmp_path):
    cycle, receipt = build(tmp_path, observer=mor.OBSERVER)
    result = verify(cycle, receipt, anchor=None)
    assert result["status"] == mor.BLOCKED and result["B_verified"] is False
    assert result["ideas"][0]["idea_id"] == "IDEA-1"
