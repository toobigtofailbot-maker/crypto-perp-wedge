"""Manual, non-authoritative whole-cohort research integration. No scientific executor."""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from tools.hermes import data_evidence_resolution as de
from tools.hermes import discovery_intent as di
from tools.hermes import discovery_intent_consumer as dc
from tools.hermes import intent_strategy_spec_handoff as hs
from tools.hermes import science_readiness as sr
from tools.mcp.project_evidence.models import RepoIdentity
from tools.mcp.project_evidence.resources import EvidenceResourceCatalog

SCHEMA = "cpw_hermes_research_cycle_v1"
FIXTURE = "LABELED_FIXTURE_NOT_MODEL_OUTPUT"
CAPTURE = "OPERATOR_CAPTURE_UNVERIFIED_AUTHORSHIP"
MAX_FILE = 2_000_000
MAX_TOTAL = 20_000_000
GATES = [
    "DATA_AUTHORITY_BLOCKED: no independently admitted historical partition; no physical open",
    "AWAITING_EXACT_SCIENTIFIC_APPROVAL: no exact native study/approval binding",
    "NATIVE_MAPPING_BLOCKED: external 02C drafts lack canonical admission, VM/Sweep and approved protocol",
    "SearchContract NOT_ISSUABLE: approved envelope/request and durable lineage required",
]


def _snapshot(directory: Path, allowed: set[str]) -> dict[str, bytes]:
    """Bounded external evidence only; reject indirection before reading any payload."""
    sr._check_paths(directory)
    if any((p / ".git").exists() for p in (directory.absolute(), *directory.absolute().parents)):
        raise hs.HandoffError("inputs must be external to every repository")
    paths = dc._ordinary_tree(directory)
    if set(paths) - allowed:
        raise hs.HandoffError("unexpected input inventory; no payload opened")
    if len(paths) > 64:
        raise hs.HandoffError("input inventory exceeds bound")
    sizes = [p.stat() for p in paths.values()]
    if any(s.st_nlink != 1 or s.st_size > MAX_FILE for s in sizes) or sum(
        s.st_size for s in sizes
    ) > MAX_TOTAL:
        raise hs.HandoffError("inputs must be bounded ordinary unlinked files")
    files = {}
    for name, path in paths.items():
        with path.open("rb") as handle:
            raw = handle.read(MAX_FILE + 1)
        if len(raw) > MAX_FILE:
            raise hs.HandoffError("input grew beyond bound")
        # Every cycle/response artifact is text. Secrets cannot enter published evidence.
        if di._contains_secret(raw.decode("utf-8-sig")):
            raise hs.HandoffError("credential text rejected")
        if name.endswith(".json"):
            hs._strict_json(raw.decode("utf-8-sig").encode())
        files[name] = raw
    return files


def _cycle_snapshot(directory: Path) -> dict[str, bytes]:
    roles = ("director-sources", "research-scout", "research-critic", "director-synthesis", di.HANDOFF_ROLE)
    files = _snapshot(directory, {*di.CYCLE_FILES, *(f"{r}.observations.json" for r in roles)})
    manifest = hs._strict_json(files["run_manifest.json"].decode("utf-8-sig").encode())
    names = [a["path"] for a in manifest["artifacts"]]
    if len(names) != len(set(names)) or set(files) != {"run_manifest.json", *names}:
        raise hs.HandoffError("cycle inventory must be closed and unique")
    if not set(di.CYCLE_FILES) <= set(files):
        raise hs.HandoffError("incomplete cycle")
    for name in names:
        if Path(name).name != name:
            raise hs.HandoffError("cycle files must be flat")
    # Nothing is fetched here. Private/local URLs must not be published as public citations.
    sources = hs._strict_json(files["source_index.json"].decode("utf-8-sig").encode())
    for source in sources:
        if source.get("kind") != "public":
            continue
        url = urlsplit(source["url_or_uri"])
        host = url.hostname or ""
        try:
            public = ipaddress.ip_address(host).is_global
        except ValueError:
            public = "." in host and not host.endswith((".local", ".internal", ".localhost"))
        if url.scheme != "https" or url.username or url.password or url.query or url.fragment or not public:
            raise hs.HandoffError("public citation must be a credential-free public HTTPS URL")
    return files


def _write(files: dict[str, bytes], directory: Path) -> None:
    directory.mkdir()
    for name, raw in files.items():
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(raw)


def _disjoint(*paths: Path) -> None:
    resolved = [p.resolve() for p in paths]
    for index, first in enumerate(resolved):
        for second in resolved[index + 1:]:
            if first == second or first in second.parents or second in first.parents:
                raise hs.HandoffError("input and output directories must be disjoint")


def _new_external(path: Path) -> Path:
    target = dc._check_output_target(path)
    if any((parent / ".git").exists() for parent in target.parents):
        raise hs.HandoffError("output must be external to every repository")
    return target


def _read_output(directory: Path) -> dict[str, bytes]:
    sr._check_paths(directory)
    if any((parent / ".git").exists() for parent in (directory.absolute(), *directory.absolute().parents)):
        raise hs.HandoffError("replay output must be external to every repository")
    paths = dc._ordinary_tree(directory)
    root_files = {"SHA256SUMS", "cycle-summary.json", "study-request.json", "memory-index-request.json"}
    stages = {"cycle", "responses", "02a.discovery-intent", "02b", "02c-prepared", "02c", "02d", "02e"}
    if not root_files <= set(paths):
        raise hs.HandoffError("missing coordinator inventory; no payload opened")
    for name, path in paths.items():
        parts = Path(name).parts
        if (path.stat().st_nlink != 1 or (len(parts) == 1 and name not in root_files)
                or (len(parts) > 1 and (parts[0] not in stages
                    or (path.name != "SHA256SUMS" and path.suffix not in {".json", ".md"})))):
            raise hs.HandoffError("unexpected replay inventory; no payload opened")
    return hs._read_tree(directory)


class ResearchCycle:
    def __init__(self, root: Path = di.REPO_ROOT, *, memory_reader=None):
        self.root = root
        self.identity = RepoIdentity.resolve(root)
        self.memory_reader = memory_reader

    def _head(self):
        if RepoIdentity.resolve(self.root) != self.identity:
            raise hs.HandoffError("repository identity changed during cycle")

    def _assemble(self, cycle: Path, workspace: Path, responses: Path | None, label: str) -> dict:
        self._head()
        if label not in (FIXTURE, CAPTURE):
            raise hs.HandoffError("explicit capture provenance label required")
        frozen = _cycle_snapshot(cycle)
        allowed_replies = {f"{n:02d}.{kind}.json" for n in range(3) for kind in ("response", "capture")}
        replies = _snapshot(responses, allowed_replies) if responses else {}
        _write(frozen, workspace / "cycle")
        _write(replies, workspace / "responses")
        packet = di.DiscoveryIntentAdapter(
            self.root, self.identity, postgres_reader=self.memory_reader
        ).build(workspace / "cycle")
        if len(packet["ideas"]) != 3:
            raise hs.HandoffError("whole cohort requires exactly three retained ideas")
        definitions = [i["fingerprint"]["sha256"] if i["fingerprint"] else di.canonical_sha256(
            {k: i["hermes_authored"].get(k) for k in ("title", "native_draft", "next_investigation")}
        ) for i in packet["ideas"]]
        if len(set(definitions)) != 3:
            raise hs.HandoffError("three distinct hypothesis definitions required; labels are insufficient")
        di.write_packet_directory(packet, workspace / "cycle", workspace / "02a.discovery-intent")
        summary, intents = dc.DiscoveryIntentConsumer(
            self.root, self.identity, memory_reader=self.memory_reader
        ).build_batch(workspace / "02a.discovery-intent")
        dc.write_batch(summary, intents, workspace / "02b")
        handoff = hs.IntentStrategySpecHandoff(self.root, self.identity)
        _write(handoff.prepare_files(hs._read_tree(workspace / "02b")), workspace / "02c-prepared")
        handoff.load_prepared(workspace / "02c-prepared")
        _write(handoff.build_files(workspace / "02c-prepared", workspace / "responses"), workspace / "02c")
        built = hs.verify_built(workspace / "02c")
        readiness = sr.ScienceReadiness(self.root)
        _write(readiness.build_files(workspace / "02c", workspace / "02c-prepared", workspace / "responses"),
               workspace / "02d")
        # No requests/local_root: catalog metadata only. Never invoke 02F/02G physical loaders.
        _write(de.DataEvidenceResolution(self.root).build_files(
            workspace / "02d", workspace / "02c", workspace / "02c-prepared", workspace / "responses"
        ), workspace / "02e")
        data = hs._strict_json((workspace / "02e" / hs.SUMMARY_FILE).read_bytes())
        ideas = []
        for origin, intent, draft, metadata in zip(
            packet["ideas"], summary["ideas"], built["ideas"], data["ideas"], strict=True
        ):
            if len({i["idea_id"] for i in (origin, intent, draft, metadata)}) != 1:
                raise hs.HandoffError("cross-stage hypothesis substitution")
            receipt = hs._strict_json((workspace / "02d" / f"ideas/{intent['index']:02d}.receipt.json").read_bytes())
            data_receipt = hs._strict_json((workspace / "02e" / metadata["receipt"]).read_bytes())
            memory = intent["refreshed_memory"] or intent["original_memory"]
            idea = {
                "index": intent["index"], "idea_id": origin["idea_id"],
                "hypothesis_sha256": di.canonical_sha256(origin["hermes_authored"]),
                "fingerprint": origin["fingerprint"], "source_ids": intent["source_ids"],
                "source_claims": intent["source_claims"], "critic_assessment": intent["critic_assessment"],
                "memory": memory, "original_memory": intent["original_memory"],
                "native_statuses": {"02a": origin["typed_status"], "02b": intent["status"], "02c": draft["status"]},
                "disposition": "duplicate" if memory.get("state") == "EXACT_DUPLICATE" else "blocked",
                "science_status": "NOT_READY", "search_contract_status": "NOT_ISSUABLE",
                "drafts": draft["drafts"], "technical_checks": receipt["technical_checks"],
                "data_gaps": data_receipt["next_investigations"],
                "block_reasons": [*intent["block_reasons"], *receipt["source_02c"]["block_reasons"], *GATES],
                "next_investigation": intent["next_legal_investigation"],
                "feedback": {"observed_metrics": None, "critic_vs_outcome": "NO_EXPERIMENT_NO_OUTCOME_COMPARISON",
                             "falsifiable_prediction": (origin["validated_draft_input"] or {}).get("falsifiable_prediction"),
                             "next_investigation": intent["next_legal_investigation"],
                             "scientific_disposition": "NOT_EVALUATED"},
            }
            ideas.append(idea)
        request = hs._hashed({
            "schema_version": "cpw_hermes_cycle_blocked_study_request_v1", "repo_sha": self.identity.repo_sha,
            "authority": hs.AUTHORITY, "status": "NO_ELIGIBLE_NATIVE_STUDY", "selected_idea": None,
            "ideas": [{"idea_id": i["idea_id"], "hypothesis_sha256": i["hypothesis_sha256"],
                       "drafts": i["drafts"], "block_reasons": i["block_reasons"]} for i in ideas],
            "execution_command": None, "approval_marker": None,
            "missing_mapping": "02C noncanonical drafts cannot enter the exact STRAT-SPEC-0003/VM-0003/"
                               "SWEEP-PLAN-0003 15m factory mapper; no generic contract is inferred",
            "native_requirements": sr.PREREG_MISSING,
            "physical_stages": {"02f": "NOT_INVOKED_DATA_AUTHORITY_BLOCKED", "02g": "NOT_INVOKED_DATA_AUTHORITY_BLOCKED",
                                "02h": "NOT_INVOKED_NO_GENUINE_BOUND_02G_AND_PROTOCOL_PROPOSAL"},
        })
        (workspace / "study-request.json").write_bytes(hs._json_bytes(request))
        memory_request = hs._hashed({
            "schema_version": "cpw_hermes_cycle_memory_index_request_v1", "authority": hs.AUTHORITY,
            "repo_sha": self.identity.repo_sha, "status": "PENDING_NOT_INDEXED_NONAUTHORITATIVE",
            "study_request_sha256": request["content_sha256"],
            "records": [{"idea_id": i["idea_id"], "hypothesis_sha256": i["hypothesis_sha256"],
                         "memory": i["memory"], "source_claims": i["source_claims"],
                         "critic_assessment": i["critic_assessment"], "feedback": i["feedback"],
                         "successful_experiment": False} for i in ideas],
        })
        (workspace / "memory-index-request.json").write_bytes(hs._json_bytes(memory_request))
        result = hs._hashed({
            "schema_version": SCHEMA, "authority": hs.AUTHORITY, "repo_sha": self.identity.repo_sha,
            "provenance": label, "authorship": "NOT_INDEPENDENTLY_VERIFIED", "status": "NO_ELIGIBLE_NATIVE_STUDY",
            "physical_milestone": "PHYSICAL_MILESTONE_NOT_YET_PROVEN", "ideas": ideas,
            "scientific_history": {"cumulative_denominator": None, "status": "NOT_READ_NOT_RESET",
                                   "denominator_kpi_scope": "new scientific trials in this captured cycle only"},
            "model_turn_receipts": packet["model_turn_receipts"],
            "study_request_sha256": request["content_sha256"], "memory_request_sha256": memory_request["content_sha256"],
            "kpis": {"model_cycles": 0, "captured_cycles": 1, "distinct_hypotheses": 3,
                     "criticized_hypotheses": sum(bool(i["critic_assessment"]) for i in ideas),
                     "native_eligible": 0, "native_blocked_with_reason": len(ideas),
                     "genuine_experiments_completed": 0, "retained_scientific_denominator": 0,
                     "rejected_or_advanced": 0, "Memory_native_records_or_pending": {"native": 0, "pending": len(ideas)},
                     "human_strategy_selections": 0, "automatic_unauthorized_trials": 0},
            "effects": {"runner_calls": 0, "scientific_db_mutations": 0, "scheduler_invocations": 0,
                        "memory_authoritative_writes": 0, "holdout_reads": 0},
            "budget": {"pipeline_model_calls": 0, "captured_native_turn_receipts": len(packet["model_turn_receipts"]),
                       "captured_cycle_max_turns": 5, "scientific_trials": 0, "automatic_retries": 0,
                       "scope": "pipeline_model_calls counts assembly only; discover separately launches the native five-turn cycle"},
            "limitations": ["capture receipts and hashes do not prove genuine model authorship or source truth",
                            "02D compiler probes are synthetic; no historical/holdout bytes opened",
                            "blocked study request is not approval-ready and supplies no execution command"],
        })
        (workspace / "cycle-summary.json").write_bytes(hs._json_bytes(result))
        if _cycle_snapshot(cycle) != frozen or (responses and _snapshot(responses, allowed_replies) != replies):
            raise hs.HandoffError("inputs changed during assembly")
        self._head()
        return result

    def build(self, cycle: Path, output: Path, *, responses: Path | None = None, label: str) -> dict:
        output = _new_external(output)
        sr._check_paths(cycle, *([responses] if responses else []))
        _disjoint(cycle, output, *([responses] if responses else []))
        with tempfile.TemporaryDirectory(prefix="cpw-02k-", dir=output.parent) as temp:
            stage = Path(temp) / "packet"
            stage.mkdir()
            result = self._assemble(cycle, stage, responses, label)
            files = {n: p.read_bytes() for n, p in dc._ordinary_tree(stage).items()}
            files = hs.IntentStrategySpecHandoff._guard(files)
            (stage / "SHA256SUMS").write_bytes(hs._render(files)["SHA256SUMS"])
            hs._read_tree(stage)
            dc._rename_noreplace(stage, output)
        return result

    def replay(self, cycle: Path, output: Path, *, responses: Path | None = None, label: str) -> dict:
        recorded = _read_output(output)
        with tempfile.TemporaryDirectory(prefix="cpw-02k-replay-") as temp:
            target = Path(temp) / "packet"
            result = self.build(cycle, target, responses=responses, label=label)
            if hs._read_tree(target) != recorded:
                raise hs.HandoffError("cycle replay differs from frozen evidence")
        return result


def _coordinator(root: Path) -> ResearchCycle:
    reader = None
    dsn = (os.environ.get("RESEARCH_MEMORY_READONLY_DSN") or "").strip()
    if dsn:
        from tools.mcp.project_evidence.memory_reader import ReadOnlyResearchMemoryReader
        reader = ReadOnlyResearchMemoryReader(dsn, EvidenceResourceCatalog(root, RepoIdentity.resolve(root)))
    return ResearchCycle(root, memory_reader=reader)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "replay", "discover"))
    parser.add_argument("--cycle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--responses", type=Path)
    parser.add_argument("--provenance", choices=(FIXTURE, CAPTURE), required=True)
    parser.add_argument("--theme")
    args = parser.parse_args(argv)
    try:
        coordinator = _coordinator(di.REPO_ROOT)
        if args.command == "discover":
            if args.provenance != CAPTURE or not args.theme or args.responses:
                raise hs.HandoffError("discover needs capture provenance/theme and no preexisting responses")
            _new_external(args.output)
            _new_external(args.cycle)
            _new_external(Path(str(args.cycle) + dc.SOURCE_SUFFIX))
            _disjoint(args.cycle, args.output, Path(str(args.cycle) + dc.SOURCE_SUFFIX))
            # Existing launcher owns project/home isolation, model sessions and five bounded turns.
            subprocess.run(["pwsh", "-NoProfile", "-File", str(di.REPO_ROOT / "tools/hermes/research_turn.ps1"),
                            "-OutputRoot", str(args.cycle), "-RepoSha", coordinator.identity.repo_sha,
                            "-RepoBranch", coordinator.identity.branch, "-Theme", args.theme,
                            "-StructuredIntentHandoff", "-PythonExe", sys.executable], check=True)
        method = coordinator.replay if args.command == "replay" else coordinator.build
        result = method(args.cycle, args.output, responses=args.responses, label=args.provenance)
    except (RuntimeError, ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError):
        print("RESEARCH_CYCLE_FAILED: inputs, environment or native boundary rejected; no retry", file=sys.stderr)
        return 1
    print(json.dumps({k: result[k] for k in ("content_sha256", "status", "kpis")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
