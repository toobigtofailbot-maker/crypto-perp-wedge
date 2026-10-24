"""Default-OFF batch consumer: verified 02A discovery packet -> native research intents.

Every idea keeps its source order, Hermes-authored fields, critic assessment and
gaps. A `TYPED_VALID` idea is re-validated against the existing native draft
contract, its evidence anchors are re-resolved against current committed bytes,
and only then the existing `BoundedResearchIntentBuilder` binds it with the
DB-enforced read-only Research Memory reader. Nothing here selects, ranks or
rewrites strategy reasoning. The batch output is review-only with zero authority
and no consumer: it never admits, schedules, runs or promotes anything.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import shutil
import stat
import sys
import uuid
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pydantic import ValidationError

from tools.hermes import discovery_intent as di
from tools.mcp.project_evidence.models import ProjectEvidenceError, RepoIdentity
from tools.mcp.project_evidence.research_intent import (
    BoundedResearchIntentBuilder,
    BoundedResearchIntentDraftInput,
    BoundedResearchIntentV1,
    BoundedResearchRequestV1,
    semantic_content_sha256,
)
from tools.mcp.project_evidence.resources import EvidenceResourceCatalog
from tools.research_memory.fingerprint import FINGERPRINT_VERSION, HypothesisDefinition, fingerprint
from tools.research_memory.repo_source import NEGATIVE_CLASSIFICATIONS

BATCH_SCHEMA_VERSION = "cpw_hermes_discovery_native_intent_batch_v1"
SOURCE_SUFFIX = ".discovery-intent"
SUMMARY_FILE = "summary.json"
INTENT_DIR = "intents"
MAX_FILES = 64
MAX_FILE_BYTES = 4_000_000
MAX_TOTAL_BYTES = 32_000_000
_AT_FDCWD = -100  # Linux <fcntl.h>
_RENAME_NOREPLACE = 1  # Linux <linux/fs.h>; renameat2 fails with EEXIST instead of replacing
BUILT = "NATIVE_INTENT_BUILT_REVIEW_REQUIRED"
LEAD = "NOT_READY_LEAD"
BLOCKED_MEMORY = "BLOCKED_MEMORY_UNAVAILABLE"
BLOCKED_EVIDENCE = "BLOCKED_EVIDENCE_UNVERIFIED"
BLOCKED_NATIVE = "BLOCKED_NATIVE_BUILD_FAILED"
PACKET_KEYS = frozenset({
    "schema_version", "authority", "repo_sha", "repo_branch", "cycle", "model_turn_receipts",
    "sources", "independent_critic", "ideas", "summary", "content_sha256"})
IDEA_KEYS = frozenset({
    "idea_id", "hermes_authored", "typed_status", "validated_request", "validated_draft_input",
    "evidence_anchors", "fingerprint", "request_id", "failures", "next_legal_investigation", "memory"})
BATCH_AUTHORITY = {
    "not_authority": True, "review_required": True, "admission_authority": False,
    "scientific_execution_authority": False, "policy_or_contract_creation_authority": False,
    "scheduler_prefect_optuna_runner_governor_authority": False,
    "canonical_write_authority": False, "candidate_or_promotion_authority": False,
    "runtime_paper_live_authority": False, "capital_authority": False, "automatic_consumers": [],
}
_NATIVE_FALSE_FLAGS = (
    "canonical_write_authority", "approval_authority", "candidate_or_promotion_authority",
    "search_governor_authority", "final_holdout_authority", "scheduler_or_autonomy_authority",
    "runner_or_backtest_authority", "runtime_or_risk_authority", "paper_live_authority",
    "capital_authority")


class ConsumerError(RuntimeError):
    """The batch as a whole is untrustworthy; nothing is written."""


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _is_link(path: Path) -> bool:
    return path.is_symlink() or bool(getattr(path, "is_junction", lambda: False)()) or bool(
        getattr(os.lstat(path), "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _ordinary_tree(directory: Path, expected: set[str] | None = None) -> dict[str, Path]:
    """Bounded inventory of ordinary files; any link, junction or special file fails closed."""
    if not directory.is_dir() or _is_link(directory):
        raise ConsumerError(f"not an ordinary directory: {directory.name}")
    files: dict[str, Path] = {}
    total = 0
    for path in sorted(directory.rglob("*")):
        if _is_link(path):
            raise ConsumerError("symlink or junction inside a batch directory")
        if path.is_dir():
            continue
        if not stat.S_ISREG(os.lstat(path).st_mode):
            raise ConsumerError("non-regular file inside a batch directory")
        size = path.stat().st_size
        total += size
        if size > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES or len(files) >= MAX_FILES:
            raise ConsumerError("batch directory exceeds the file size or count bound")
        files[path.relative_to(directory).as_posix()] = path
    if expected is not None and set(files) != expected:
        raise ConsumerError("directory holds unexpected or missing files")
    return files


def _same(actual: Any, expected: Any, what: str) -> None:
    if actual != expected:
        raise ConsumerError(f"source packet inconsistency: {what}")


def load_source_packet(directory: Path) -> dict[str, Any]:
    """Strictly re-verify one 02A packet directory without trusting its self-description."""
    if not directory.name.endswith(SOURCE_SUFFIX):
        raise ConsumerError(f"source must be one existing *{SOURCE_SUFFIX} directory")
    files = _ordinary_tree(directory)
    packet = di.verify_directory(directory)
    _same(set(packet), set(PACKET_KEYS), "top-level fields")
    _same(packet["authority"], di.NON_AUTHORITY, "non-authority flags")
    inputs = directory / "inputs"
    manifest = json.loads((inputs / "run_manifest.json").read_text(encoding="utf-8-sig"))
    _same(set(packet["cycle"]["inputs"]), set(di._cycle_inputs(manifest)), "retained input set")
    _same(set(files), {"packet.json", "SHA256SUMS", *(f"inputs/{name}" for name in packet["cycle"]["inputs"])},
          "unrecorded files")
    # Reuse the 02A cycle gate bound to the packet's own SHA: COMPLETED non-authority manifest,
    # artifact hashes, exact five-turn sequence, independent critic, strict handoff schema.
    bound = RepoIdentity(repo_sha=packet["repo_sha"], branch=str(packet.get("repo_branch") or "DETACHED"))
    loaded = di.DiscoveryIntentAdapter(REPO_ROOT, bound, git=di.GitHead(REPO_ROOT))._load_cycle(inputs)
    _same(packet["model_turn_receipts"], [{key: item.get(key) for key in (
        "role", "invocation_id", "session_id", "exit_code", "prompt_sha256")}
        for item in manifest["invocations"]], "model-turn receipts")
    critic = loaded["invocations"]["research-critic"]
    _same(packet["independent_critic"], {
        "role": "research-critic", "session_id": critic["session_id"],
        "invocation_id": critic["invocation_id"], "artifact": "critic_result.md",
        "sha256": packet["cycle"]["inputs"]["critic_result.md"]}, "independent critic receipt")
    _same(packet["repo_branch"], manifest.get("repo_branch"), "repo branch")
    authored = loaded["handoff"].ideas
    ideas = packet["ideas"]
    _same(len(ideas), len(authored), "idea count")
    ids = [idea.get("idea_id") for idea in ideas]
    if len(ids) != len(set(ids)):
        raise ConsumerError("source packet inconsistency: duplicate idea ids")
    for index, (idea, raw) in enumerate(zip(ideas, authored)):
        _same(set(idea), set(IDEA_KEYS), f"idea[{index}] fields")
        _same(idea["hermes_authored"], raw, f"idea[{index}] Hermes-authored fields or order")
        _same(idea["idea_id"], raw.get("idea_id"), f"idea[{index}] id")
        if idea["typed_status"] == "TYPED_VALID":
            _verify_typed(index, idea)
        else:
            _same(idea["typed_status"], "NOT_READY", f"idea[{index}] typed status")
    _same(packet["summary"], {
        "typed_valid": [i["idea_id"] for i in ideas if i["typed_status"] == "TYPED_VALID"],
        "not_ready_leads": [i["idea_id"] for i in ideas if i["typed_status"] != "TYPED_VALID"],
        "memory_states": {i["idea_id"]: i["memory"]["state"] for i in ideas}}, "summary block")
    return packet


def _verify_typed(index: int, idea: dict[str, Any]) -> None:
    native = idea["hermes_authored"].get("native_draft")
    if not isinstance(native, dict) or idea["failures"] != []:
        raise ConsumerError(f"source packet inconsistency: idea[{index}] TYPED_VALID without a clean draft")
    try:
        draft = BoundedResearchIntentDraftInput.model_validate(native)
        request = BoundedResearchRequestV1.model_validate(
            {key: value for key, value in native.items() if key in BoundedResearchRequestV1.model_fields})
    except ValidationError as exc:
        raise ConsumerError(f"source packet inconsistency: idea[{index}] draft fails native validation") from exc
    _same(idea["validated_draft_input"], draft.model_dump(mode="json"), f"idea[{index}] validated draft")
    _same(idea["validated_request"], request.model_dump(mode="json"), f"idea[{index}] validated request")
    _same(idea["request_id"], draft.request_id, f"idea[{index}] request id")
    _same(idea["fingerprint"], {"version": FINGERPRINT_VERSION, "sha256": fingerprint(_definition(draft))},
          f"idea[{index}] fingerprint")
    _same([anchor.get("resource_uri") for anchor in idea["evidence_anchors"]], draft.evidence_resource_uris,
          f"idea[{index}] anchor set")


def _definition(draft: BoundedResearchIntentDraftInput) -> HypothesisDefinition:
    return HypothesisDefinition.from_mapping({key: getattr(draft, key) for key in (
        "strategy_family", "mechanism", "primary_timeframe", "required_data_features", "free_parameter_count")})


def require_current_head(packet: dict[str, Any], identity: RepoIdentity) -> None:
    if packet["repo_sha"] != identity.repo_sha:
        raise ConsumerError("source packet is bound to a different repo SHA (historical/stale); "
                            "it is never rebound to the current HEAD")


class _RecordingReader:
    """Pass-through to the injected read-only reader that keeps what the native builder saw."""

    def __init__(self, reader: Any) -> None:
        self._reader = reader
        self.lookup: dict[str, Any] | None = None
        self.error: BaseException | None = None

    def lookup_definition(self, definition: Any) -> dict[str, Any]:
        try:
            self.lookup = self._reader.lookup_definition(definition)
        except BaseException as exc:
            self.error = exc
            raise
        return self.lookup


def _cause(exc: BaseException) -> str:
    # Our own Project-Evidence errors carry fixed, secret-free text; anything else is named only.
    return f"{type(exc).__name__}: {exc}" if isinstance(exc, ProjectEvidenceError) else type(exc).__name__


class DiscoveryIntentConsumer:
    def __init__(self, repo_root: Path, identity: RepoIdentity, *, memory_reader: Any | None,
                 memory_unavailable_reason: str = "RESEARCH_MEMORY_READONLY_DSN not configured",
                 git: Any | None = None) -> None:
        self._identity = identity
        self._catalog = EvidenceResourceCatalog(repo_root, identity)
        self._git = git or di.GitHead(repo_root)
        self._reader = memory_reader
        self._reader_reason = memory_unavailable_reason

    def _quote_in_head(self, relative_path: str, quote: Any) -> bool:
        if not isinstance(quote, str) or len(di._compact(quote)) < di.MIN_QUOTE_CHARS:
            return False
        content = self._git.blob(relative_path)
        return content is not None and di._compact(quote) in di._compact(content.decode("utf-8", "replace"))

    def _reresolve(self, idea: dict[str, Any], sources: dict[str, dict[str, Any]],
                   problems: list[str]) -> list[dict[str, Any]]:
        anchors = []
        for anchor in idea["evidence_anchors"]:
            uri = anchor["resource_uri"]
            try:
                evidence = self._catalog.read(uri)["evidence"]
            except (ProjectEvidenceError, OSError) as exc:
                problems.append(f"{uri}: not resolvable through the CPW catalog ({type(exc).__name__})")
                continue
            head_sha = self._git.blob_sha256(evidence["path"])
            source = sources.get(str(anchor.get("source_id")))
            current = {"resource_uri": uri, "repo_path": evidence["path"],
                       "artifact_sha256": evidence["artifact_sha256"], "repo_sha": evidence["repo_sha"],
                       "head_blob_sha256": head_sha, "support_role": anchor.get("support_role"),
                       "source_id": anchor.get("source_id"),
                       "quote_verified": self._quote_in_head(evidence["path"], anchor.get("quote")),
                       "semantic_relevance": "REVIEWER_CHECK_REQUIRED"}
            for key in ("repo_path", "artifact_sha256", "repo_sha", "head_blob_sha256"):
                if anchor.get(key) != current[key]:
                    problems.append(f"{uri}: {key} drifted from the source packet")
            if head_sha != evidence["artifact_sha256"]:
                problems.append(f"{uri}: working-tree content differs from the HEAD blob")
            if not current["quote_verified"]:
                problems.append(f"{uri}: anchor quote is not verbatim current HEAD content")
            if anchor.get("semantic_relevance") != "REVIEWER_CHECK_REQUIRED":
                problems.append(f"{uri}: semantic relevance was not left as a reviewer check")
            if source is None or source.get("kind") != "repo" or source.get("url_or_uri") != uri:
                problems.append(f"{uri}: anchor is not backed by a repo source; public sources are never anchors")
            elif source.get("sha256_or_unknown") != evidence["artifact_sha256"]:
                problems.append(f"{uri}: cited repo source hash differs from current bytes")
            if any(other.get("kind") != "repo" and other.get("url_or_uri") == uri for other in sources.values()):
                problems.append(f"{uri}: a public source claims an internal CPW resource identity")
            anchors.append(current)
        return anchors

    def _refreshed_memory(self, recording: _RecordingReader | None) -> dict[str, Any]:
        if recording is None:
            return {"status": "MEMORY_UNAVAILABLE", "reason": self._reader_reason}
        if recording.error is not None or recording.lookup is None:
            reason = _cause(recording.error) if recording.error else "lookup not reached"
            return {"status": "MEMORY_UNAVAILABLE", "reason": reason}
        records = recording.lookup.get("records", [])
        negative = [record for record in records if record.get("classification") in NEGATIVE_CLASSIFICATIONS]
        state = ("PRIOR_FAILED_INVESTIGATION" if negative else "EXACT_DUPLICATE"
                 if recording.lookup.get("matched") else "NO_EXACT_POSTGRES_MATCH_NOT_NOVELTY")
        return {"status": "OK", "lookup": "postgres:research_memory.hypothesis_items (read-only)",
                "state": state, "matched": bool(recording.lookup.get("matched")),
                "record_count": len(records), "negative_record_count": len(negative)}

    def _check_native(self, intent: BoundedResearchIntentV1, idea: dict[str, Any],
                      draft: BoundedResearchIntentDraftInput, anchors: list[dict[str, Any]]) -> list[str]:
        problems = []
        payload = intent.model_dump(mode="json")
        if BoundedResearchIntentV1.model_validate(payload) != intent:
            problems.append("native intent does not round-trip its own contract")
        if intent.content_sha256 != semantic_content_sha256(intent):
            problems.append("native semantic content hash does not verify")
        if intent.fingerprint_sha256 != idea["fingerprint"]["sha256"]:
            problems.append("native fingerprint differs from the source packet fingerprint")
        if intent.repo_sha != self._identity.repo_sha or intent.research_memory.repo_sha != self._identity.repo_sha:
            problems.append("native repo identity differs from the current HEAD")
        if [(a.resource_uri, a.repo_path, a.artifact_sha256, a.repo_sha) for a in intent.evidence_anchors] != [
                (a["resource_uri"], a["repo_path"], a["artifact_sha256"], a["repo_sha"]) for a in anchors]:
            problems.append("native evidence anchors differ from the re-resolved anchors")
        if any(getattr(intent, flag) is not False for flag in _NATIVE_FALSE_FLAGS) or \
                intent.automatic_consumers or intent.index_not_truth is not True:
            problems.append("native non-authority flags do not hold")
        for key in ("request_id", "research_question", "causal_rationale", "falsifiable_prediction",
                    "falsification_stop_conditions", "proposed_objective_intent", "unresolved_assumptions"):
            if getattr(intent, key) != getattr(draft, key):
                problems.append(f"native {key} differs from the model-authored draft")
        return problems

    def _idea(self, index: int, idea: dict[str, Any], sources: dict[str, dict[str, Any]]) -> tuple[dict, Any]:
        authored = idea["hermes_authored"]
        critic = authored.get("critic_assessment") or {}
        out: dict[str, Any] = {
            "index": index, "idea_id": idea["idea_id"], "title": authored.get("title"),
            "source_typed_status": idea["typed_status"], "status": LEAD, "request_id": idea["request_id"],
            "fingerprint": idea["fingerprint"], "source_ids": authored.get("source_ids"),
            "source_claims": authored.get("source_claims"), "critic_assessment": critic,
            "missing_evidence": authored.get("missing_evidence"),
            "source_failures": idea["failures"], "next_legal_investigation": idea["next_legal_investigation"],
            "original_memory": idea["memory"], "refreshed_memory": None,
            "memory_note": "original 02A memory state is historical context; the refreshed read-only "
                           "lookup is separate and may disagree; no match is never novelty",
            "evidence_anchors": [], "block_reasons": [], "native_intent": None,
            "review_requirements": [],
        }
        if idea["typed_status"] != "TYPED_VALID":
            out["review_requirements"] = ["retained NOT_READY lead; never admitted"]
            return out, None
        draft = BoundedResearchIntentDraftInput.model_validate(authored["native_draft"])
        problems: list[str] = []
        out["evidence_anchors"] = self._reresolve(idea, sources, problems)
        out["review_requirements"] = [
            *(f"SEMANTIC_RELEVANCE REVIEWER_CHECK_REQUIRED: {a['resource_uri']} ({a['support_role']})"
              for a in out["evidence_anchors"]),
            "DATA_AVAILABILITY_AND_COVERAGE_UNPROVEN: a valid hash proves identity, not data coverage",
            "MECHANISM_UNPROVEN: model-authored reasoning; no scientific question is settled here",
            *(f"CRITIC_GAP: {gap}" for gap in critic.get("evidence_gaps", [])),
            *(f"UNRESOLVED_ASSUMPTION: {item}" for item in draft.unresolved_assumptions)]
        if problems:
            out.update(status=BLOCKED_EVIDENCE, block_reasons=problems)
            return out, None
        recording = None if self._reader is None else _RecordingReader(self._reader)
        if recording is None:
            out.update(status=BLOCKED_MEMORY, refreshed_memory=self._refreshed_memory(None),
                       block_reasons=[f"MEMORY_UNAVAILABLE: {self._reader_reason}"])
            return out, None
        builder = BoundedResearchIntentBuilder(self._catalog, recording, self._identity)  # type: ignore[arg-type]
        try:
            intent = builder.build(draft)
        except Exception as exc:  # noqa: BLE001 - every failure is a recorded, non-admitted block
            out["refreshed_memory"] = self._refreshed_memory(recording)
            if recording.error is not None:
                out.update(status=BLOCKED_MEMORY, block_reasons=[f"MEMORY_UNAVAILABLE: {_cause(exc)}"])
            else:
                out.update(status=BLOCKED_NATIVE, block_reasons=[f"native builder failed: {_cause(exc)}"])
            return out, None
        out["refreshed_memory"] = self._refreshed_memory(recording)
        problems = self._check_native(intent, idea, draft, out["evidence_anchors"])
        if problems:
            out.update(status=BLOCKED_NATIVE, block_reasons=problems)
            return out, None
        out["status"] = BUILT
        return out, intent

    def build_batch(self, source_dir: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
        packet = load_source_packet(source_dir)
        require_current_head(packet, self._identity)
        sources = {str(source.get("id")): source for source in packet["sources"]}
        ideas, intents = [], {}
        for index, idea in enumerate(packet["ideas"]):
            out, intent = self._idea(index, idea, sources)
            if intent is not None:
                name = f"{INTENT_DIR}/{index:02d}.native_intent.json"
                raw = (json.dumps(intent.model_dump(mode="json"), indent=2, sort_keys=True) + "\n").encode("utf-8")
                intents[name] = raw
                out["native_intent"] = {"file": name, "file_sha256": _sha256_bytes(raw),
                                        "content_sha256": intent.content_sha256,
                                        "fingerprint_sha256": intent.fingerprint_sha256}
            ideas.append(out)
        source_files = {name: _sha256_bytes((source_dir / name).read_bytes()) for name in ("packet.json", "SHA256SUMS")}
        summary = {
            "schema_version": BATCH_SCHEMA_VERSION, "authority": dict(BATCH_AUTHORITY),
            "repo_sha": self._identity.repo_sha,
            "source_packet": {"schema_version": packet["schema_version"], "content_sha256": packet["content_sha256"],
                              "repo_sha": packet["repo_sha"], "files_sha256": source_files,
                              "inputs": packet["cycle"]["inputs"],
                              "independent_critic": packet["independent_critic"]},
            "memory_reader": {"status": "CONFIGURED_READ_ONLY"} if self._reader is not None
            else {"status": "MEMORY_UNAVAILABLE", "reason": self._reader_reason},
            "ideas": ideas,
            "counts": {status: [i["idea_id"] for i in ideas if i["status"] == status]
                       for status in (BUILT, LEAD, BLOCKED_EVIDENCE, BLOCKED_MEMORY, BLOCKED_NATIVE)},
        }
        summary["content_sha256"] = di.canonical_sha256(summary)
        if di._contains_secret(json.dumps(summary)) or any(di._contains_secret(raw.decode()) for raw in intents.values()):
            raise ConsumerError("credential text detected; nothing written")
        return summary, intents


def _render(summary: dict[str, Any], intents: dict[str, bytes]) -> dict[str, bytes]:
    files = {SUMMARY_FILE: (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode("utf-8"), **intents}
    sums = "".join(f"{_sha256_bytes(files[name])}  {name}\n" for name in sorted(files))
    return {**files, "SHA256SUMS": sums.encode("utf-8")}


def _check_output_target(output: Path) -> Path:
    output = Path(os.path.abspath(output))
    if output.exists() or output.is_symlink():
        raise ConsumerError("output must be new; no overwrite")
    parent = output.parent
    if not parent.is_dir():
        raise ConsumerError("output parent must exist")
    for cursor in (parent, *parent.parents):
        if cursor.exists() and _is_link(cursor) and cursor != Path(cursor.anchor):
            raise ConsumerError("output path must not traverse a symlink or junction")
    try:
        output.resolve().relative_to(REPO_ROOT)
    except ValueError:
        return output
    raise ConsumerError("output must be external to the repository (noncanonical)")


def _rename_noreplace(source: Path, target: Path) -> None:
    """Atomically publish a directory; an existing target, even one created after preflight, is never replaced."""
    if sys.platform == "win32":
        # CPython's os.rename is MoveFileExW without MOVEFILE_REPLACE_EXISTING: an existing target always fails.
        try:
            os.rename(source, target)
        except FileExistsError as exc:
            raise ConsumerError("output appeared during publication; no overwrite") from exc
        return
    if sys.platform.startswith("linux"):
        import ctypes
        renameat2 = getattr(ctypes.CDLL(None, use_errno=True), "renameat2", None)
        if renameat2 is None:
            raise ConsumerError("renameat2 is unavailable; refusing non-atomic publication")
        renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        if renameat2(_AT_FDCWD, os.fsencode(source), _AT_FDCWD, os.fsencode(target), _RENAME_NOREPLACE) != 0:
            code = ctypes.get_errno()
            if code == errno.EEXIST:
                raise ConsumerError("output appeared during publication; no overwrite")
            raise ConsumerError(f"no-replace publication failed or unsupported: {errno.errorcode.get(code, code)}")
        return
    raise ConsumerError(f"no atomic no-replace directory primitive on {sys.platform}; refusing to publish")


def write_batch(summary: dict[str, Any], intents: dict[str, bytes], output: Path) -> None:
    output = _check_output_target(output)
    stage = output.with_name(f"{output.name}.partial-{uuid.uuid4().hex}")
    stage.mkdir()
    try:
        for name, raw in _render(summary, intents).items():
            target = stage / name
            target.parent.mkdir(exist_ok=True)
            with open(target, "xb") as handle:  # exclusive create
                handle.write(raw)
        verify_batch(stage)
        _rename_noreplace(stage, output)
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def verify_batch(directory: Path) -> dict[str, Any]:
    files = _ordinary_tree(directory)
    if "SHA256SUMS" not in files or SUMMARY_FILE not in files:
        raise ConsumerError("batch is missing summary.json or SHA256SUMS")
    sums = {}
    for line in files["SHA256SUMS"].read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        sums[name] = digest
    actual = {name: _sha256_bytes(path.read_bytes()) for name, path in files.items() if name != "SHA256SUMS"}
    if sums != actual:
        raise ConsumerError("SHA256SUMS inventory does not match batch contents")
    summary = json.loads(files[SUMMARY_FILE].read_text(encoding="utf-8"))
    body = {key: value for key, value in summary.items() if key != "content_sha256"}
    if summary.get("schema_version") != BATCH_SCHEMA_VERSION or di.canonical_sha256(body) != summary.get("content_sha256"):
        raise ConsumerError("batch summary content hash does not verify")
    if summary["authority"] != BATCH_AUTHORITY:
        raise ConsumerError("batch authority flags were altered")
    declared = {idea["native_intent"]["file"]: idea for idea in summary["ideas"] if idea["native_intent"]}
    built = [idea["idea_id"] for idea in summary["ideas"] if idea["status"] == BUILT]
    if set(declared) != set(actual) - {SUMMARY_FILE} or built != summary["counts"][BUILT] or \
            built != [idea["idea_id"] for idea in declared.values()]:
        raise ConsumerError("intent files do not match the built ideas exactly")
    for name, idea in declared.items():
        intent = BoundedResearchIntentV1.model_validate_json(files[name].read_text(encoding="utf-8"))
        ref = idea["native_intent"]
        if (actual[name] != ref["file_sha256"] or intent.content_sha256 != semantic_content_sha256(intent)
                or intent.content_sha256 != ref["content_sha256"]
                or intent.fingerprint_sha256 != ref["fingerprint_sha256"]
                or intent.repo_sha != summary["repo_sha"]):
            raise ConsumerError(f"native intent does not verify: {name}")
    return summary


def replay_batch(consumer: DiscoveryIntentConsumer, batch_dir: Path, source_dir: Path) -> dict[str, Any]:
    """Rebuild in memory from the same source, repo and read-only memory state; no writes."""
    recorded = verify_batch(batch_dir)
    rebuilt, intents = consumer.build_batch(source_dir)
    rendered = _render(rebuilt, intents)
    if rebuilt["content_sha256"] != recorded["content_sha256"] or any(
            rendered[name] != (batch_dir / name).read_bytes() for name in rendered):
        raise ConsumerError("replay did not reproduce the batch byte-for-byte")
    return recorded


def inspect_source(source_dir: Path, identity: RepoIdentity) -> dict[str, Any]:
    """Verify a source packet and report its ideas; a historical packet stays historical evidence."""
    packet = load_source_packet(source_dir)
    return {"source_content_sha256": packet["content_sha256"], "source_repo_sha": packet["repo_sha"],
            "current_repo_sha": identity.repo_sha,
            "binding": "CURRENT_HEAD" if packet["repo_sha"] == identity.repo_sha
            else "HISTORICAL_SOURCE_SHA_NOT_CURRENT_HEAD_MATERIALIZATION_REFUSED",
            "ideas": [{"idea_id": idea["idea_id"], "typed_status": idea["typed_status"],
                       "original_memory_state": idea["memory"]["state"]} for idea in packet["ideas"]]}


def _consumer() -> DiscoveryIntentConsumer:
    identity = RepoIdentity.resolve(REPO_ROOT)
    dsn = (os.environ.get("RESEARCH_MEMORY_READONLY_DSN") or "").strip()
    reader = None
    if dsn:
        from tools.mcp.project_evidence.memory_reader import ReadOnlyResearchMemoryReader
        reader = ReadOnlyResearchMemoryReader(dsn, EvidenceResourceCatalog(REPO_ROOT, identity))
    return DiscoveryIntentConsumer(REPO_ROOT, identity, memory_reader=reader)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", help="verify a source packet and list its ideas; writes nothing")
    inspect.add_argument("--packet-dir", type=Path, required=True)
    materialize = commands.add_parser("materialize", help="write a new external review-only batch directory")
    materialize.add_argument("--packet-dir", type=Path, required=True)
    materialize.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify", help="recheck batch hashes; --packet-dir replays from the source")
    verify.add_argument("--batch-dir", type=Path, required=True)
    verify.add_argument("--packet-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "inspect":
            print(json.dumps(inspect_source(args.packet_dir, RepoIdentity.resolve(REPO_ROOT)), sort_keys=True))
            return 0
        if args.command == "materialize":
            summary, intents = _consumer().build_batch(args.packet_dir)
            write_batch(summary, intents, args.output)
        elif args.packet_dir is not None:
            summary = replay_batch(_consumer(), args.batch_dir, args.packet_dir)
        else:
            summary = verify_batch(args.batch_dir)
    except (ConsumerError, di.PacketError, ProjectEvidenceError, ValidationError, OSError,
            json.JSONDecodeError, KeyError, ValueError, TypeError, AttributeError) as exc:
        print(f"DISCOVERY_INTENT_CONSUMER_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"content_sha256": summary["content_sha256"], **summary["counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
