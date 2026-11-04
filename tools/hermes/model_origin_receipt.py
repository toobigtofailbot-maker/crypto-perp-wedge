"""Verify a host-observed Hermes cycle receipt (proof B). Read-only; never self-signs B.

The receipt is written by the host launcher (`research_turn.ps1 -HostObservationReceipt`),
not by Hermes. Its SHA-256 must be anchored out of band by the operator; without that
anchor, or with a test observer, B is never reported as verified. This is not a provider
signature and does not defend against a compromised host or administrator.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from tools.hermes import discovery_intent as di

SCHEMA = "cpw_hermes_origin_verification_v1"
RECEIPT_SCHEMA = "cpw_hermes_host_observation_receipt_v1"
OBSERVER = "cpw_research_turn_host_observer_v1"
TEST_OBSERVER = "TEST_ONLY_FIXTURE_OBSERVER"
ROLES = ("director-sources", "research-scout", "research-critic", "director-synthesis", di.HANDOFF_ROLE)
RESPONSE_FILES = dict(zip(ROLES, (
    "director_sources.json", "scout_result.md", "critic_result.md",
    "research_opportunity_brief.md", di.HANDOFF_FILE,
)))
VERIFIED, FIXTURE, BLOCKED = "B_MODEL_ORIGIN_VERIFIED", "B_TEST_FIXTURE_ONLY", "BLOCKED_ORIGIN_UNVERIFIED"
ASSURANCE = ("host-observed Docker exec stdout with operator-anchored receipt hash; not provider-signed; "
             "no defence against a compromised host, administrator or provider")
HEX = re.compile(r"^[0-9a-f]{64}$")
SESSION = re.compile(r"^[A-Za-z0-9_.:-]{8,128}$")
RECEIPT_KEYS = {"schema_version", "not_authority", "observer", "repo_sha", "repo_branch", "compose_project",
                "container_id", "image_id", "image_ref", "cycle_state", "cycle_directory",
                "run_manifest_sha256", "role_order", "turns", "assurance_limits"}
TURN_KEYS = {"role", "invocation_id", "started_utc", "finished_utc", "docker_exit_code", "session_id",
             "command_sha256", "prompt_sha256", "stdout_sha256", "terminal_text_sha256", "response_file",
             "response_file_sha256", "observations_file_sha256"}
MAX_BYTES = 2_000_000


class OriginUnverified(ValueError):
    """Stable refusal code only."""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _read(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400:
        raise OriginUnverified("ORDINARY_FILE_REQUIRED")
    raw = path.read_bytes()
    if len(raw) > MAX_BYTES:
        raise OriginUnverified("FILE_TOO_LARGE")
    if di._contains_secret(raw.decode("utf-8-sig")):
        raise OriginUnverified("CREDENTIAL_TEXT")
    return raw


def _json(raw: bytes):
    def strict(pairs):
        keys = [k for k, _ in pairs]
        if len(keys) != len(set(keys)):
            raise OriginUnverified("DUPLICATE_JSON_KEY")
        return dict(pairs)

    try:
        return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=strict)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise OriginUnverified("MALFORMED_JSON") from exc


def _terminal_text(raw: bytes) -> bytes:
    # Set-Content appends exactly one platform newline after the observed terminal text.
    for ending in (b"\r\n", b"\n"):
        if raw.endswith(ending):
            return raw[: -len(ending)]
    raise OriginUnverified("RESPONSE_FILE_FRAMING")


def _check(condition: bool, code: str) -> None:
    if not condition:
        raise OriginUnverified(code)


def _verify(cycle: Path, receipt_path: Path, anchor_sha256: str | None, expected_repo_sha: str) -> dict:
    receipt_raw = _read(receipt_path)
    receipt = _json(receipt_raw)
    _check(isinstance(receipt, dict) and set(receipt) == RECEIPT_KEYS, "RECEIPT_KEYS")
    _check(receipt["schema_version"] == RECEIPT_SCHEMA and receipt["not_authority"] is True, "RECEIPT_SCHEMA")
    observer = receipt["observer"]
    _check(isinstance(observer, dict) and observer.get("identity") in {OBSERVER, TEST_OBSERVER}, "OBSERVER_IDENTITY")
    _check(HEX.fullmatch(str(observer.get("host_fingerprint_sha256", ""))) is not None, "OBSERVER_CONTEXT")
    _check(receipt["repo_sha"] == expected_repo_sha and re.fullmatch(r"[0-9a-f]{40}", expected_repo_sha) is not None,
           "REPO_SHA")
    image = str(receipt["image_id"])
    _check(re.fullmatch(r"sha256:[0-9a-f]{64}", image) is not None and image != "sha256:" + "0" * 64, "IMAGE_DIGEST")
    _check(re.fullmatch(r"[0-9a-f]{12,64}", str(receipt["container_id"])) is not None, "CONTAINER_ID")
    _check(receipt["cycle_state"] == "COMPLETED" and receipt["cycle_directory"] == cycle.name, "CYCLE_STATE")

    manifest_raw = _read(cycle / "run_manifest.json")
    manifest = _json(manifest_raw)
    _check(_sha(manifest_raw) == receipt["run_manifest_sha256"], "RUN_MANIFEST_HASH")
    _check(manifest.get("state") == "COMPLETED" and manifest.get("repo_sha") == expected_repo_sha, "MANIFEST_BINDING")
    _check(tuple(receipt["role_order"]) == ROLES, "ROLE_ORDER")
    invocations = manifest.get("invocations", [])
    _check([i.get("role") for i in invocations] == list(ROLES), "MANIFEST_ROLE_ORDER")
    artifacts = {a["path"]: a["sha256"] for a in manifest.get("artifacts", [])}
    _check(len(artifacts) == len(manifest.get("artifacts", [])), "DUPLICATE_ARTIFACT")
    turns = receipt["turns"]
    _check(isinstance(turns, list) and len(turns) == len(ROLES), "TURN_COUNT")
    sessions, invocation_ids = set(), set()
    texts = {}
    for role, turn, invoked in zip(ROLES, turns, invocations, strict=True):
        _check(isinstance(turn, dict) and set(turn) == TURN_KEYS and turn["role"] == role, "TURN_KEYS")
        _check(turn["docker_exit_code"] == 0 and invoked.get("exit_code") == 0, "TURN_EXIT")
        session = str(turn["session_id"])
        _check(SESSION.fullmatch(session) is not None and len(set(session)) > 3, "SESSION_PLACEHOLDER")
        _check(session == invoked.get("session_id") and turn["invocation_id"] == invoked.get("invocation_id"),
               "SESSION_BINDING")
        _check(turn["prompt_sha256"] == invoked.get("prompt_sha256"), "PROMPT_BINDING")
        for key in ("command_sha256", "prompt_sha256", "stdout_sha256", "terminal_text_sha256",
                    "response_file_sha256", "observations_file_sha256"):
            _check(HEX.fullmatch(str(turn[key])) is not None and turn[key] != "0" * 64, "ZERO_OR_MALFORMED_DIGEST")
        command = invoked.get("command")
        _check(isinstance(command, list) and bool(command)
               and all(isinstance(arg, str) for arg in command), "COMMAND_BINDING")
        _check(_sha(json.dumps(command, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
               == turn["command_sha256"], "COMMAND_BINDING")
        _check(turn["response_file"] == RESPONSE_FILES[role], "RESPONSE_FILE_ROLE")
        raw = _read(cycle / RESPONSE_FILES[role])
        _check(_sha(raw) == turn["response_file_sha256"] == artifacts.get(RESPONSE_FILES[role]), "RESPONSE_HASH")
        text = _terminal_text(raw)
        _check(_sha(text) == turn["terminal_text_sha256"], "TERMINAL_TEXT_HASH")
        observed = _read(cycle / f"{role}.observations.json")
        _check(_sha(observed) == turn["observations_file_sha256"] == artifacts.get(f"{role}.observations.json"),
               "OBSERVATION_HASH")
        events = _json(observed)
        events = events if isinstance(events, list) else [events]
        terminal = [e for e in events if isinstance(e, dict) and e.get("type") == "result"]
        _check(len(terminal) == 1 and terminal[0].get("session_id") == session, "OBSERVED_SESSION")
        sessions.add(session)
        invocation_ids.add(turn["invocation_id"])
        texts[role] = text.decode("utf-8")
    _check(len(sessions) == len(ROLES) and len(invocation_ids) == len(ROLES), "DUPLICATE_SESSION")

    # Intent/critic/source content chain: verbatim excerpts must come from the observed turns.
    handoff = _json(texts[di.HANDOFF_ROLE].encode())
    source_raw = _read(cycle / "source_index.json")
    _check(_sha(source_raw) == artifacts.get("source_index.json"), "SOURCE_INDEX_HASH")
    source_rows = _json(source_raw)
    _check(source_rows == _json(texts["director-sources"].encode()).get("sources"), "SOURCE_TURN_BINDING")
    sources = {s.get("id"): s for s in source_rows}
    _check(len(sources) == len(source_rows), "DUPLICATE_SOURCE")
    ideas = []
    _check(isinstance(handoff, dict) and isinstance(handoff.get("ideas"), list) and handoff["ideas"], "INTENT_IDEAS")
    for idea in handoff["ideas"]:
        _check("hermes_authored" not in idea and "b_verified" not in idea, "SELF_DECLARED_AUTHORSHIP")
        excerpt = (idea.get("critic_assessment") or {}).get("critic_excerpt", "")
        _check(bool(excerpt) and excerpt in texts["research-critic"], "CRITIC_CHAIN")
        for claim in idea.get("source_claims", []):
            source = sources.get(claim.get("source_id"))
            _check(source is not None and claim.get("excerpt", "") in source.get("excerpt", ""), "SOURCE_CHAIN")
        ideas.append({"idea_id": idea.get("idea_id"), "original_hypothesis_sha256": di.canonical_sha256(idea)})
    _check(len({i["idea_id"] for i in ideas}) == len(ideas), "DUPLICATE_IDEA")

    receipt_sha = _sha(receipt_raw)
    test_only = observer["identity"] == TEST_OBSERVER
    anchored = anchor_sha256 is not None and anchor_sha256 == receipt_sha
    # A consistent but unanchored cohort keeps its idea hashes (A may proceed) but is never B.
    reason = None
    if not test_only and not anchored:
        reason = "TRUST_ANCHOR_MISSING" if anchor_sha256 is None else "TRUST_ANCHOR_MISMATCH"
    return {
        "status": FIXTURE if test_only else BLOCKED if reason else VERIFIED,
        "B_verified": not test_only and reason is None,
        "reason": reason,
        "observed_host_receipt_sha256": receipt_sha,
        "trust_anchor_ref": "operator_pinned_receipt_sha256" if anchored else None,
        "observer_identity": observer["identity"],
        "cycle_manifest_sha256": receipt["run_manifest_sha256"],
        "image_digest": image,
        "invocations": [{k: t[k] for k in ("role", "invocation_id", "session_id", "prompt_sha256",
                                            "terminal_text_sha256")} for t in turns],
        "critic_sha256": turns[2]["terminal_text_sha256"],
        "intent_sha256": turns[4]["terminal_text_sha256"],
        "source_packet_sha256": artifacts.get("source_index.json"),
        "ideas": ideas,
    }


def verify_origin(cycle: Path, receipt: Path, *, anchor_sha256: str | None, expected_repo_sha: str) -> dict:
    """Return a non-authoritative projection; any defect yields BLOCKED_ORIGIN_UNVERIFIED."""
    base = {"schema_version": SCHEMA, "not_authority": True, "repo_sha": expected_repo_sha,
            "assurance_limits": ASSURANCE}
    try:
        return base | _verify(Path(cycle), Path(receipt), anchor_sha256, expected_repo_sha)
    except OriginUnverified as exc:
        return base | {"status": BLOCKED, "B_verified": False, "reason": str(exc)}
    except (OSError, KeyError, TypeError, AttributeError, ValueError):
        return base | {"status": BLOCKED, "B_verified": False, "reason": "MALFORMED_EVIDENCE"}


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cycle", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--anchor-sha256")
    parser.add_argument("--repo-sha", required=True)
    args = parser.parse_args(argv)
    result = verify_origin(args.cycle, args.receipt, anchor_sha256=args.anchor_sha256, expected_repo_sha=args.repo_sha)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["status"] != BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())
