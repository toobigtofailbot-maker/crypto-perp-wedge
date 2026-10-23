"""Deterministic, fail-closed adapter from one Hermes research cycle to a draft packet.

Hermes authors every hypothesis field. This module only validates those drafts
against the native CPW contracts, resolves repo evidence anchors, computes the
native exact-definition fingerprint, and triages Research Memory state. It never
infers mechanisms, fills fields, chooses strategies, or invokes admission,
compilers, runners, schedulers, or backtests. The packet has zero authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Annotated, Any, Literal

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from tools.mcp.project_evidence.models import ProjectEvidenceError, RepoIdentity
from tools.mcp.project_evidence.research_intent import (
    BoundedResearchIntentDraftInput,
    BoundedResearchRequestV1,
)
from tools.mcp.project_evidence.resources import EvidenceResourceCatalog
from tools.research_memory.fingerprint import (
    FINGERPRINT_VERSION,
    HypothesisDefinition,
    fingerprint,
)
from tools.research_memory.repo_source import (
    NEGATIVE_CLASSIFICATIONS,
    load_repo_memory_seeds,
)

PACKET_SCHEMA_VERSION = "cpw_hermes_discovery_intent_packet_v1"
HANDOFF_SCHEMA_VERSION = "cpw_hermes_structured_intent_handoff_v1"
HANDOFF_FILE = "structured_intent_drafts.json"
HANDOFF_ROLE = "director-intent"
CYCLE_FILES = (
    "run_manifest.json", "director_sources.json", "source_index.json", "scout_result.md",
    "critic_result.md", "research_opportunity_brief.md", HANDOFF_FILE,
)
MAX_IDEAS = 3
MIN_QUOTE_CHARS = 24
NON_AUTHORITY = {
    "draft_only_not_strategy_spec": True, "admission_authority": False,
    "experiment_authority": False, "approval_authority": False,
    "canonical_write_authority": False, "scheduler_or_autonomy_authority": False,
    "runner_or_backtest_authority": False, "candidate_or_promotion_authority": False,
    "paper_live_or_capital_authority": False, "automatic_consumers": [],
}
_INJECTION = re.compile(
    r"(?i)(ignore (?:all |any )?(?:previous|prior|above) instructions|disregard (?:the )?"
    r"(?:system|previous|above)|you are now\b|system prompt|developer message|"
    r"<\s*/?\s*system\s*>|run (?:this|the following) command|execute (?:this|the following))"
)
_PROFIT_CLAIM = re.compile(
    r"(?i)(guaranteed|risk[- ]free|sure[- ]fire|proven (?:edge|profit)|"
    r"\bsharpe(?: ratio)?\s*(?:of|=|:|>|above)?\s*\d|"
    r"\b\d+(?:\.\d+)?\s*%\s*(?:annual|monthly|return|profit|cagr))"
)
_CREDENTIAL = re.compile(
    r"(?i)(Bearer\s+[a-z0-9._-]{16,}|sk-[a-z0-9_-]{16,}|eyJ[a-z0-9_-]{10,}\.[a-z0-9_-]{10,}\."
    r"[a-z0-9_-]+|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY|postgres(?:ql)?://[^\s\"']*:[^\s\"']*@)"
)
_SECRET_ENV = ("BROWSERBASE_API_KEY", "BROWSERBASE_PROJECT_ID", "OPENAI_API_KEY",
               "RESEARCH_MEMORY_READONLY_DSN")

Text = Annotated[str, Field(min_length=1, max_length=8192)]


class PacketError(RuntimeError):
    """The cycle as a whole cannot produce a trustworthy packet; nothing is published."""


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class SourceClaim(_Strict):
    source_id: Text
    claim: Text
    excerpt: Text


class AnchorRelevance(_Strict):
    # No MECHANISM role: causal support must come from cited public research.
    resource_uri: Text
    support_role: Literal["DATA_AVAILABILITY", "PRIOR_INVESTIGATION", "CONSTRAINT"]
    quote: Text
    relevance: Text


class CriticAssessment(_Strict):
    stance: Literal["AGREE", "DISAGREE", "MIXED"]
    critic_excerpt: Text
    evidence_gaps: list[Text]
    failure_modes: list[Text]
    counterarguments: list[Text]


class HandoffIdea(_Strict):
    idea_id: Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")]
    title: Text
    source_ids: Annotated[list[Text], Field(min_length=1)]
    source_claims: Annotated[list[SourceClaim], Field(min_length=1)]
    scout_observation: Text
    critic_assessment: CriticAssessment
    anchor_relevance: list[AnchorRelevance]
    native_draft: dict[str, Any] | None
    missing_evidence: list[Text]
    next_investigation: Text


class Handoff(_Strict):
    schema_version: Literal[HANDOFF_SCHEMA_VERSION]
    ideas: Annotated[list[dict[str, Any]], Field(min_length=1, max_length=MAX_IDEAS)]


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                         allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _compact(value: str) -> str:
    return " ".join(value.split())


def _strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _strings(item)


def _errors(exc: ValidationError, prefix: str) -> list[dict[str, str]]:
    # Never echo rejected input values; they are untrusted model output.
    return [{"field": ".".join([prefix, *map(str, error["loc"])]).strip("."),
             "reason": error["msg"]} for error in exc.errors()]


def _contains_secret(text: str) -> bool:
    for name in _SECRET_ENV:
        secret = os.environ.get(name)
        if secret and secret in text:
            return True
    return _CREDENTIAL.search(text) is not None


class GitHead:
    """Exact HEAD-blob identity and content for anchored repo paths."""

    def __init__(self, repo_root: Path) -> None:
        self._root = repo_root

    def blob(self, relative_path: str) -> bytes | None:
        result = subprocess.run(["git", "cat-file", "blob", f"HEAD:{relative_path}"],
                                cwd=self._root, capture_output=True, timeout=30, check=False)
        return result.stdout if result.returncode == 0 else None

    def blob_sha256(self, relative_path: str) -> str | None:
        content = self.blob(relative_path)
        return hashlib.sha256(content).hexdigest() if content is not None else None


class MemoryTriage:
    """Read-only exact-fingerprint lookups; similarity is flagged, never asserted."""

    def __init__(self, repo_root: Path, catalog: EvidenceResourceCatalog,
                 postgres_reader: Any | None, prior_packets: list[dict[str, Any]]) -> None:
        self._catalog = catalog
        self._postgres = postgres_reader
        self._prior = prior_packets
        try:
            self._seeds = load_repo_memory_seeds(repo_root)
            self._repo_status = {"lookup": "repo_index:research/candidate_registry.jsonl",
                                 "status": "OK", "seed_count": len(self._seeds)}
        except (OSError, ValueError, KeyError) as exc:
            self._seeds = ()
            self._repo_status = {"lookup": "repo_index:research/candidate_registry.jsonl",
                                 "status": "UNAVAILABLE", "reason": type(exc).__name__}

    def _negative_findings(self, seed: Any) -> dict[str, Any]:
        evidence = []
        for ref in seed.evidence:
            path = self._catalog.repo_root / ref.artifact_path
            actual = _sha256_file(path) if path.is_file() else None
            evidence.append({
                "artifact_path": ref.artifact_path, "artifact_id": ref.artifact_id,
                "evidence_role": ref.evidence_role,
                "indexed_sha256": ref.artifact_content_sha256, "current_sha256": actual,
                "resolution": "EXACT" if actual == ref.artifact_content_sha256 else "HASH_MISMATCH_OR_MISSING",
            })
        return {"source_key": seed.source_key, "title": seed.title,
                "classification": seed.classification, "negative_reason": seed.negative_reason,
                "evidence": evidence}

    def _postgres_lookup(self, definition: HypothesisDefinition) -> dict[str, Any]:
        if self._postgres is None:
            return {"lookup": "postgres:research_memory.hypothesis_items", "status": "UNAVAILABLE",
                    "reason": "RESEARCH_MEMORY_READONLY_DSN not configured"}
        try:
            result = self._postgres.lookup_definition(definition)
        except Exception as exc:  # noqa: BLE001 - any failure is UNKNOWN, never novelty
            return {"lookup": "postgres:research_memory.hypothesis_items", "status": "UNAVAILABLE",
                    "reason": type(exc).__name__}
        records = [{"source_key": record.get("source_key"),
                    "classification": record.get("classification"),
                    "resolved_classification": record.get("resolved_classification"),
                    "authority_state": record.get("authority_state"),
                    "negative_reason": record.get("negative_reason"),
                    "evidence": [{key: row.get(key) for key in (
                        "artifact_path", "artifact_content_sha256", "resolution")}
                        for row in record.get("evidence", [])]}
                   for record in result.get("records", [])]
        return {"lookup": "postgres:research_memory.hypothesis_items", "status": "OK",
                "matched": bool(result.get("matched")), "records": records}

    def classify(self, fingerprint_sha256: str | None, definition: HypothesisDefinition | None,
                 same_cycle: list[str]) -> dict[str, Any]:
        if fingerprint_sha256 is None or definition is None:
            return {"state": "UNKNOWN_MEMORY_STATE",
                    "basis": "fingerprint impossible; typed path failed closed", "lookups": []}
        exact_repo = [seed for seed in self._seeds if fingerprint(seed.definition) == fingerprint_sha256]
        postgres = self._postgres_lookup(definition)
        prior = [{"packet_content_sha256": packet["content_sha256"], "idea_id": idea["idea_id"],
                  "request_id": idea.get("request_id")}
                 for packet in self._prior for idea in packet["ideas"]
                 if idea.get("fingerprint", {}).get("sha256") == fingerprint_sha256]
        similar = []
        for seed in self._seeds:
            if fingerprint(seed.definition) == fingerprint_sha256:
                continue
            same_family = seed.definition.strategy_family == definition.strategy_family
            left, right = set(seed.definition.required_data_features), set(definition.required_data_features)
            overlap = len(left & right) / len(left | right) if left | right else 0.0
            if same_family or (seed.definition.primary_timeframe == definition.primary_timeframe
                               and overlap >= 0.5):
                similar.append({"source_key": seed.source_key, "classification": seed.classification,
                                "shared": "strategy_family" if same_family else "timeframe+features",
                                "assertion": "flagged for investigation; not a proven duplicate"})
        lookups = [
            {**self._repo_status, "exact_matches": [seed.source_key for seed in exact_repo]},
            postgres,
            {"lookup": "same_cycle_packet", "status": "OK", "exact_matches": same_cycle},
            {"lookup": "prior_packets", "status": "OK", "count": len(self._prior), "exact_matches": prior},
        ]
        postgres_records = postgres.get("records", []) if postgres["status"] == "OK" else []
        failed = [self._negative_findings(seed) for seed in exact_repo
                  if seed.classification in NEGATIVE_CLASSIFICATIONS]
        failed += [record for record in postgres_records
                   if record.get("classification") in NEGATIVE_CLASSIFICATIONS]
        if failed:
            state, basis = "PRIOR_FAILED_INVESTIGATION", "exact fingerprint matches a negative record"
        elif exact_repo or postgres.get("matched") or same_cycle or prior:
            state, basis = "EXACT_DUPLICATE", "exact fingerprint matches an existing identity"
        elif similar:
            state, basis = "POSSIBLE_SEMANTIC_SIMILARITY", "structured-field similarity only"
        elif postgres["status"] == "OK" and self._repo_status["status"] == "OK":
            state, basis = "NEW_UNMATCHED", "no exact match after successful repo and Postgres lookups"
        else:
            state = "UNKNOWN_MEMORY_STATE"
            basis = "no exact match in available lookups, but a mandatory identity index was unavailable"
        return {"state": state, "basis": basis, "lookups": lookups,
                "retained_negative_findings": failed, "semantic_similarity_flags": similar}


class DiscoveryIntentAdapter:
    def __init__(self, repo_root: Path, identity: RepoIdentity, *, postgres_reader: Any | None = None,
                 prior_packets: list[dict[str, Any]] | None = None, git: GitHead | None = None) -> None:
        self._identity = identity
        self._catalog = EvidenceResourceCatalog(repo_root, identity)
        self._git = git or GitHead(repo_root)
        self._memory = MemoryTriage(repo_root, self._catalog, postgres_reader, prior_packets or [])

    def _load_cycle(self, cycle: Path) -> dict[str, Any]:
        missing = [name for name in CYCLE_FILES if not (cycle / name).is_file()]
        if missing:
            raise PacketError(f"cycle is missing required files: {missing}")
        manifest = json.loads((cycle / "run_manifest.json").read_text(encoding="utf-8-sig"))
        if manifest.get("state") != "COMPLETED" or manifest.get("not_authority") is not True:
            raise PacketError("cycle manifest is not a COMPLETED non-authority cycle")
        if manifest.get("repo_sha") != self._identity.repo_sha:
            raise PacketError("cycle repo SHA does not match the bound repository HEAD")
        recorded = {item["path"]: item["sha256"] for item in manifest.get("artifacts", [])}
        for name in set(CYCLE_FILES[1:]) | set(recorded):
            path = cycle / name
            if Path(name).name != name or not path.is_file() or recorded.get(name) != _sha256_file(path):
                raise PacketError(f"cycle artifact hash mismatch or unrecorded: {name}")
        roles = [item.get("role") for item in manifest.get("invocations", [])]
        expected = ["director-sources", "research-scout", "research-critic", "director-synthesis", HANDOFF_ROLE]
        if roles != expected:
            raise PacketError(f"unexpected invocation sequence: {roles}")
        invocations = {item["role"]: item for item in manifest["invocations"]}
        if any(item.get("exit_code") != 0 or not item.get("session_id") for item in invocations.values()):
            raise PacketError("every model turn needs exit_code 0 and a native session id")
        critic = invocations["research-critic"]
        if critic["session_id"] in {item["session_id"] for role, item in invocations.items() if role != "research-critic"} \
                or "research-critic" not in critic.get("command", []):
            raise PacketError("critic turn is not an independent research-critic session")
        director = json.loads((cycle / "director_sources.json").read_text(encoding="utf-8-sig"))
        if len(director.get("hypotheses", [])) < 3:
            raise PacketError("director compared fewer than three hypotheses")
        sources = json.loads((cycle / "source_index.json").read_text(encoding="utf-8-sig"))
        if not isinstance(sources, list) or not sources:
            raise PacketError("source index is empty")
        try:
            handoff_raw = json.loads((cycle / HANDOFF_FILE).read_text(encoding="utf-8-sig"))
            handoff = Handoff.model_validate(handoff_raw)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise PacketError(f"structured handoff is not a valid {HANDOFF_SCHEMA_VERSION} object") from exc
        return {"manifest": manifest, "invocations": invocations, "sources": sources,
                "handoff": handoff, "critic_text": (cycle / "critic_result.md").read_text(encoding="utf-8-sig")}

    def _quote_in_head(self, uri: Any, quote: Any) -> bool:
        """Deterministic quote provenance against the committed blob; no interpretation."""
        if not isinstance(uri, str) or not isinstance(quote, str) or len(_compact(quote)) < MIN_QUOTE_CHARS:
            return False
        try:
            content = self._git.blob(self._catalog.spec_for_uri(uri).relative_path)
        except ProjectEvidenceError:
            return False
        return content is not None and _compact(quote) in _compact(content.decode("utf-8", "replace"))

    def _anchor(self, uri: str, sources_by_uri: dict[str, dict[str, Any]],
                relevance: AnchorRelevance | None, failures: list[dict[str, str]]) -> dict[str, Any] | None:
        try:
            evidence = self._catalog.read(uri)["evidence"]
        except (ProjectEvidenceError, OSError) as exc:
            failures.append({"field": f"evidence_resource_uris[{uri}]",
                             "reason": f"not resolvable through the CPW catalog ({type(exc).__name__})"})
            return None
        head_sha = self._git.blob_sha256(evidence["path"])
        anchor = {"resource_uri": uri, "repo_path": evidence["path"],
                  "artifact_sha256": evidence["artifact_sha256"], "repo_sha": evidence["repo_sha"],
                  "head_blob_sha256": head_sha,
                  # Identity and quote are proven here; whether the anchor bears on the idea is not.
                  "semantic_relevance": "REVIEWER_CHECK_REQUIRED"}
        if relevance is None:
            failures.append({"field": f"anchor_relevance[{uri}]",
                             "reason": "Hermes gave no role, quote and relevance for this anchor"})
        else:
            anchor.update(support_role=relevance.support_role, quote=relevance.quote,
                          relevance=relevance.relevance,
                          quote_verified=self._quote_in_head(uri, relevance.quote))
            if not anchor["quote_verified"]:
                failures.append({"field": f"anchor_relevance[{uri}].quote",
                                 "reason": f"not a verbatim quote (>= {MIN_QUOTE_CHARS} chars) of the HEAD blob"})
        if head_sha != evidence["artifact_sha256"]:
            failures.append({"field": f"evidence_resource_uris[{uri}]",
                             "reason": "working-tree content differs from the HEAD blob"})
        source = sources_by_uri.get(uri)
        if source is None:
            failures.append({"field": f"evidence_resource_uris[{uri}]",
                             "reason": "no repo source in the cycle source index cites this resource"})
            return anchor
        for key, actual in (("sha256_or_unknown", evidence["artifact_sha256"]),
                            ("evidence_path_or_unknown", evidence["path"]),
                            ("repo_sha_or_unknown", self._identity.repo_sha)):
            if source.get(key) != actual:
                failures.append({"field": f"evidence_resource_uris[{uri}]",
                                 "reason": f"source {source.get('id')} {key} does not match resolved identity"})
        if not self._quote_in_head(uri, source.get("excerpt")):
            failures.append({"field": f"evidence_resource_uris[{uri}]",
                             "reason": f"source {source.get('id')} excerpt is an unverified summary, not HEAD content"})
        anchor["source_id"] = source.get("id")
        return anchor

    def _idea(self, raw: dict[str, Any], sources: dict[str, dict[str, Any]],
              sources_by_uri: dict[str, dict[str, Any]], critic_text: str) -> dict[str, Any]:
        failures: list[dict[str, str]] = []
        result: dict[str, Any] = {"idea_id": raw.get("idea_id"), "hermes_authored": raw,
                                  "typed_status": "NOT_READY", "validated_request": None,
                                  "validated_draft_input": None, "evidence_anchors": [],
                                  "fingerprint": None, "request_id": None}
        try:
            idea = HandoffIdea.model_validate(raw)
        except ValidationError as exc:
            result["failures"] = _errors(exc, "idea")
            result["next_legal_investigation"] = ["Re-author the idea envelope with every required field."]
            return result
        text = "\n".join(_strings(raw))
        if _INJECTION.search(text):
            failures.append({"field": "idea", "reason": "contains instruction-injection text"})
        if _PROFIT_CLAIM.search(text):
            failures.append({"field": "idea", "reason": "contains an unsupported profitability claim"})
        for source_id in idea.source_ids:
            if source_id not in sources:
                failures.append({"field": "source_ids", "reason": f"unknown source id {source_id}"})
        for index, claim in enumerate(idea.source_claims):
            source = sources.get(claim.source_id)
            if source is None or _compact(claim.excerpt) not in _compact(str(source.get("excerpt", ""))):
                failures.append({"field": f"source_claims[{index}]",
                                 "reason": "excerpt is not traceable to the cited source excerpt"})
            elif source.get("kind") == "repo" and not self._quote_in_head(source.get("url_or_uri"), claim.excerpt):
                failures.append({"field": f"source_claims[{index}]",
                                 "reason": "repo excerpt is not verbatim HEAD content; unverified summary"})
        if idea.native_draft is not None and not any(
                sources.get(claim.source_id, {}).get("kind") == "public" for claim in idea.source_claims):
            failures.append({"field": "source_claims",
                             "reason": "mechanism needs a claim attributed to a cited public research source"})
        if _compact(idea.critic_assessment.critic_excerpt) not in _compact(critic_text):
            failures.append({"field": "critic_assessment.critic_excerpt",
                             "reason": "not a verbatim excerpt of the independent critic result"})
        definition = None
        if idea.native_draft is None:
            failures.append({"field": "native_draft", "reason": "no typed draft; retained as lead"})
        else:
            try:
                draft = BoundedResearchIntentDraftInput.model_validate(idea.native_draft)
                request_fields = set(BoundedResearchRequestV1.model_fields)
                request = BoundedResearchRequestV1.model_validate(
                    {key: value for key, value in idea.native_draft.items() if key in request_fields})
                result["request_id"] = draft.request_id
                result["validated_request"] = request.model_dump(mode="json")
                result["validated_draft_input"] = draft.model_dump(mode="json")
                definition = HypothesisDefinition.from_mapping(
                    {key: getattr(draft, key) for key in ("strategy_family", "mechanism",
                     "primary_timeframe", "required_data_features", "free_parameter_count")})
                result["fingerprint"] = {"version": FINGERPRINT_VERSION, "sha256": fingerprint(definition)}
                relevance = {item.resource_uri: item for item in idea.anchor_relevance}
                for uri in draft.evidence_resource_uris:
                    anchor = self._anchor(uri, sources_by_uri, relevance.get(uri), failures)
                    if anchor is not None:
                        result["evidence_anchors"].append(anchor)
            except ValidationError as exc:
                failures.extend(_errors(exc, "native_draft"))
            except (TypeError, ValueError) as exc:
                failures.append({"field": "native_draft", "reason": f"fingerprint impossible: {exc}"})
        result["_definition"] = definition
        result["failures"] = failures
        if not failures:
            result["typed_status"] = "TYPED_VALID"
        result["next_legal_investigation"] = [idea.next_investigation, *idea.missing_evidence,
                                              *(f"{item['field']}: {item['reason']}" for item in failures)]
        return result

    def build(self, cycle: Path) -> dict[str, Any]:
        loaded = self._load_cycle(cycle)
        sources = {str(source.get("id")): source for source in loaded["sources"]}
        sources_by_uri = {source.get("url_or_uri"): source for source in loaded["sources"]
                          if source.get("kind") == "repo"}
        ideas = [self._idea(raw, sources, sources_by_uri, loaded["critic_text"])
                 for raw in loaded["handoff"].ideas]
        ids = [idea["idea_id"] for idea in ideas]
        if len(ids) != len(set(ids)):
            raise PacketError("idea ids must be unique")
        for idea in ideas:
            fp = (idea["fingerprint"] or {}).get("sha256")
            same = [other["idea_id"] for other in ideas
                    if other is not idea and fp and (other["fingerprint"] or {}).get("sha256") == fp]
            idea["memory"] = self._memory.classify(fp, idea.pop("_definition", None), same)
        invocations = loaded["invocations"]
        packet = {
            "schema_version": PACKET_SCHEMA_VERSION, "authority": dict(NON_AUTHORITY),
            "repo_sha": self._identity.repo_sha, "repo_branch": loaded["manifest"].get("repo_branch"),
            "cycle": {"package": loaded["manifest"].get("package"),
                      "inputs": {name: _sha256_file(cycle / name) for name in _cycle_inputs(loaded["manifest"])}},
            "model_turn_receipts": [{key: item.get(key) for key in (
                "role", "invocation_id", "session_id", "exit_code", "prompt_sha256")}
                for item in loaded["manifest"]["invocations"]],
            "sources": [{**source, "screen": "INJECTION_PATTERN_TREATED_AS_DATA"
                         if _INJECTION.search("\n".join(_strings(source))) else "NONE",
                         "excerpt_verification": "PUBLIC_NOT_REPO_EVIDENCE" if source.get("kind") != "repo"
                         else "VERIFIED_IN_HEAD_BLOB" if self._quote_in_head(source.get("url_or_uri"),
                                                                             source.get("excerpt"))
                         else "UNVERIFIED_SUMMARY"}
                        for source in loaded["sources"]],
            "independent_critic": {
                "role": "research-critic", "session_id": invocations["research-critic"]["session_id"],
                "invocation_id": invocations["research-critic"]["invocation_id"],
                "artifact": "critic_result.md", "sha256": _sha256_file(cycle / "critic_result.md")},
            "ideas": ideas,
            "summary": {
                "typed_valid": [idea["idea_id"] for idea in ideas if idea["typed_status"] == "TYPED_VALID"],
                "not_ready_leads": [idea["idea_id"] for idea in ideas if idea["typed_status"] != "TYPED_VALID"],
                "memory_states": {idea["idea_id"]: idea["memory"]["state"] for idea in ideas}},
        }
        packet["content_sha256"] = canonical_sha256(packet)
        if _contains_secret(json.dumps(packet)):
            raise PacketError("credential text detected; no packet published")
        return packet


def _cycle_inputs(manifest: Mapping[str, Any]) -> list[str]:
    return sorted({"run_manifest.json", *(item["path"] for item in manifest["artifacts"])})


def verify_packet(packet: Mapping[str, Any]) -> None:
    body = {key: value for key, value in packet.items() if key != "content_sha256"}
    if packet.get("schema_version") != PACKET_SCHEMA_VERSION or canonical_sha256(body) != packet.get("content_sha256"):
        raise PacketError("packet content hash does not verify")


def verify_directory(directory: Path) -> dict[str, Any]:
    sums = {}
    for line in (directory / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        sums[name] = digest
    actual = {path.relative_to(directory).as_posix(): _sha256_file(path)
              for path in sorted(directory.rglob("*")) if path.is_file() and path.name != "SHA256SUMS"}
    if sums != actual:
        raise PacketError("SHA256SUMS inventory does not match directory contents")
    packet = json.loads((directory / "packet.json").read_text(encoding="utf-8"))
    verify_packet(packet)
    for name, digest in packet["cycle"]["inputs"].items():
        if actual.get(f"inputs/{name}") != digest:
            raise PacketError(f"retained input does not match packet: {name}")
    return packet


def write_packet_directory(packet: Mapping[str, Any], cycle: Path, output: Path) -> None:
    output = output.resolve()
    if output.exists():
        raise PacketError("output must be new; no overwrite")
    stage = output.with_name(f"{output.name}.partial-{uuid.uuid4().hex}")
    (stage / "inputs").mkdir(parents=True)
    try:
        for name in packet["cycle"]["inputs"]:
            shutil.copyfile(cycle / name, stage / "inputs" / name)
        (stage / "packet.json").write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        lines = [f"{_sha256_file(path)}  {path.relative_to(stage).as_posix()}"
                 for path in sorted(stage.rglob("*")) if path.is_file()]
        (stage / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
        verify_directory(stage)
        stage.rename(output)
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def _adapter(prior: list[Path]) -> DiscoveryIntentAdapter:
    identity = RepoIdentity.resolve(REPO_ROOT)
    reader = None
    dsn = os.environ.get("RESEARCH_MEMORY_READONLY_DSN")
    if dsn:
        from tools.mcp.project_evidence.memory_reader import ReadOnlyResearchMemoryReader
        reader = ReadOnlyResearchMemoryReader(dsn, EvidenceResourceCatalog(REPO_ROOT, identity))
    return DiscoveryIntentAdapter(REPO_ROOT, identity, postgres_reader=reader,
                                  prior_packets=[verify_directory(path) for path in prior])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="validate one completed cycle into a new packet directory")
    build.add_argument("--cycle-dir", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--prior-packet", type=Path, action="append", default=[])
    verify = commands.add_parser("verify", help="recheck hashes; --replay rebuilds from retained inputs")
    verify.add_argument("--packet-dir", type=Path, required=True)
    verify.add_argument("--replay", action="store_true")
    verify.add_argument("--prior-packet", type=Path, action="append", default=[])
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            packet = _adapter(args.prior_packet).build(args.cycle_dir)
            write_packet_directory(packet, args.cycle_dir, args.output)
        else:
            packet = verify_directory(args.packet_dir)
            if args.replay:
                rebuilt = _adapter(args.prior_packet).build(args.packet_dir / "inputs")
                if rebuilt["content_sha256"] != packet["content_sha256"]:
                    raise PacketError("replay did not reproduce the packet content hash")
    except (PacketError, ProjectEvidenceError, OSError, json.JSONDecodeError) as exc:
        print(f"DISCOVERY_INTENT_FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"content_sha256": packet["content_sha256"], **packet["summary"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
