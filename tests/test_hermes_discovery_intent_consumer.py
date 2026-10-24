"""02B batch consumer: verified 02A packet -> review-only native intents, fail-closed."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

from tools.hermes import discovery_intent as di
from tools.hermes import discovery_intent_consumer as dc
from tools.mcp.project_evidence.models import RepoIdentity, ResourceDeniedError
from tools.mcp.project_evidence.research_intent import (
    BoundedResearchIntentV1,
    semantic_content_sha256,
)
from tools.research_memory.fingerprint import FINGERPRINT_VERSION, fingerprint
from tools.research_memory.repo_source import load_repo_memory_seeds

ROOT = Path(__file__).resolve().parents[1]
HEAD = RepoIdentity.resolve(ROOT)
HISTORICAL_SHA = "023d51c31b0589b54085ef82abcfa0878e47dc28"
FEATURES = "research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
CRITIC = "The critic dissents: taker archive alignment to 1h bars is unverified and costs may dominate."
QUOTES = {
    "project://feature-availability": "This source class is limited to canonical 30m, 1h, 4h, and 1d bases; "
                                      "legacy 15m remains CANONICAL_D4_KLINE_DERIVATION.",
    "evidence://hypothesis/H-002": "# Hypothesis H-002: Donchian Channel Trend-Following (4h)",
    "evidence://hypothesis/H-005": "# Hypothesis H-005: Hourly MACD with Price Structure Confirmation",
}
PATHS = {"project://feature-availability": FEATURES,
         "evidence://hypothesis/H-002": "research/hypotheses/H-002/HYPOTHESIS.md",
         "evidence://hypothesis/H-005": "research/hypotheses/H-005/HYPOTHESIS.md"}
ROLES = {"project://feature-availability": "DATA_AVAILABILITY"}


def _sources(repo_sha: str) -> list[dict]:
    public = {"id": "P1", "kind": "public", "title": "Order flow paper", "publisher": "Journal",
              "date_or_unknown": "UNKNOWN", "observed_utc": "2026-10-23T00:00:00Z",
              "url_or_uri": "https://example.org/flow", "evidence_path_or_unknown": "UNKNOWN",
              "sha256_or_unknown": "UNKNOWN", "repo_sha_or_unknown": "UNKNOWN",
              "excerpt": "Signed aggressive order flow predicts short-horizon returns in some markets."}
    repo = [{"id": f"R{n}", "kind": "repo", "title": path, "publisher": "CPW", "date_or_unknown": "UNKNOWN",
             "observed_utc": "2026-10-23T00:00:00Z", "url_or_uri": uri, "evidence_path_or_unknown": path,
             "sha256_or_unknown": hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
             "repo_sha_or_unknown": repo_sha, "excerpt": QUOTES[uri]}
            for n, (uri, path) in enumerate(PATHS.items(), 1)]
    return [public, *repo]


def _native(**updates) -> dict:
    value = {
        "schema_version": "cpw_bounded_research_request_v1", "request_id": "REQ-FLOW-1H",
        "research_question": "Does completed-bar taker imbalance inform the next 1h return after costs?",
        "strategy_family": "order_flow_imbalance",
        "mechanism": "Aggressive taker imbalance may reflect demand not absorbed within one bar.",
        "primary_timeframe": "1h", "required_data_features": ["ohlcv_1h", "taker_buy_volume", "taker_sell_volume"],
        "free_parameter_count": 2, "evidence_resource_uris": ["project://feature-availability"],
        "constraints": ["Use completed bars only"],
        "causal_rationale": "Liquidity providers may re-price slowly after one-sided flow.",
        "falsifiable_prediction": "Imbalance-conditioned forward return is indistinguishable from zero after costs.",
        "falsification_stop_conditions": ["Stop if preregistered OOS expectancy after costs is not positive"],
        "proposed_parameter_bounds": [{"name": "lookback", "minimum": 1.0, "maximum": 24.0}],
        "proposed_objective_intent": "Evaluate OOS after-cost expectancy only.",
        "unresolved_assumptions": ["1h taker volume exists only if the exact canonical base covers the window"],
    }
    value.update(updates)
    return value


def _vol_native() -> dict:
    # A second, unrelated family and timeframe; nothing in the consumer prefers either.
    return _native(request_id="REQ-VOL-4H", strategy_family="volatility_regime_transition",
                   mechanism="Compressed realized range may precede a volatility expansion regime.",
                   primary_timeframe="4h", required_data_features=["ohlcv_4h", "realized_range_4h"],
                   free_parameter_count=1,
                   evidence_resource_uris=["project://feature-availability", "evidence://hypothesis/H-005"],
                   proposed_parameter_bounds=[{"name": "window", "minimum": 5.0, "maximum": 40.0}])


def _h002_native() -> dict:
    seed = next(s for s in load_repo_memory_seeds(ROOT) if s.source_key == "H-002").definition
    return _native(request_id="REQ-H002", strategy_family=seed.strategy_family, mechanism=seed.mechanism,
                   primary_timeframe=seed.primary_timeframe, required_data_features=list(seed.required_data_features),
                   free_parameter_count=seed.free_parameter_count,
                   evidence_resource_uris=["evidence://hypothesis/H-002"], proposed_parameter_bounds=[])


def _idea(idea_id: str, native: dict | None, **updates) -> dict:
    uris = native["evidence_resource_uris"] if native else []
    value = {
        "idea_id": idea_id, "title": f"Idea {idea_id}",
        "source_ids": ["P1", *(f"R{list(PATHS).index(uri) + 1}" for uri in uris)],
        "source_claims": [{"source_id": "P1", "claim": "Flow can lead returns",
                           "excerpt": "Signed aggressive order flow predicts short-horizon returns"}],
        "scout_observation": "Scout ranked this for testability.",
        "critic_assessment": {"stance": "MIXED", "critic_excerpt": "taker archive alignment to 1h bars is unverified",
                              "evidence_gaps": [f"gap for {idea_id}"], "failure_modes": ["costs"],
                              "counterarguments": ["regime"]},
        "anchor_relevance": [{"resource_uri": uri, "support_role": ROLES.get(uri, "PRIOR_INVESTIGATION"),
                              "quote": QUOTES[uri], "relevance": "Documents feature lineage or prior work."}
                             for uri in uris],
        "native_draft": native, "missing_evidence": [] if native else ["No CPW order-book capture exists"],
        "next_investigation": f"Next investigation for {idea_id}.",
    }
    value.update(updates)
    return value


class _WorkingTreeGit:
    def blob(self, relative_path: str) -> bytes | None:
        return (ROOT / relative_path).read_bytes()

    def blob_sha256(self, relative_path: str) -> str | None:
        return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def make_packet(tmp_path: Path, ideas: list[dict], *, repo_sha: str = HEAD.repo_sha, name: str = "cycle") -> Path:
    cycle = tmp_path / name
    cycle.mkdir()
    sources = _sources(repo_sha)
    files = {
        "director_sources.json": json.dumps({"sources": sources, "hypotheses": ["a", "b", "c"]}),
        "source_index.json": json.dumps(sources), "scout_result.md": "Scout comparison of three hypotheses.",
        "critic_result.md": CRITIC, "research_opportunity_brief.md": "Brief ranked for investigation only.",
        di.HANDOFF_FILE: json.dumps({"schema_version": di.HANDOFF_SCHEMA_VERSION, "ideas": ideas}),
    }
    roles = ["director-sources", "research-scout", "research-critic", "director-synthesis", di.HANDOFF_ROLE]
    for file_name, text in files.items():
        (cycle / file_name).write_text(text, encoding="utf-8")
    manifest = {"package": "CPW-HERMES-RESEARCH-TURN-01", "not_authority": True, "repo_sha": repo_sha,
                "repo_branch": "test", "state": "COMPLETED",
                "invocations": [{"role": role, "invocation_id": f"inv-{n}", "session_id": f"sess-{n}",
                                 "exit_code": 0, "prompt_sha256": "0" * 64, "command": ["hermes", "-p", role]}
                                for n, role in enumerate(roles)],
                "artifacts": [{"path": file_name, "sha256": hashlib.sha256((cycle / file_name).read_bytes()).hexdigest()}
                              for file_name in files]}
    (cycle / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    identity = RepoIdentity(repo_sha=repo_sha, branch="test")
    packet = di.DiscoveryIntentAdapter(ROOT, identity, git=_WorkingTreeGit()).build(cycle)
    out = tmp_path / f"{name}.discovery-intent"
    di.write_packet_directory(packet, cycle, out)
    return out


def resign(packet_dir: Path, mutate) -> None:
    """Rewrite packet.json and SHA256SUMS consistently, as a forger could; checks must not rely on self-hashes."""
    packet = json.loads((packet_dir / "packet.json").read_text(encoding="utf-8"))
    mutate(packet)
    packet.pop("content_sha256", None)
    packet["content_sha256"] = di.canonical_sha256(packet)
    (packet_dir / "packet.json").write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(packet_dir).as_posix()}"
             for p in sorted(packet_dir.rglob("*")) if p.is_file() and p.name != "SHA256SUMS"]
    (packet_dir / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


class FrozenMemory:
    """Frozen read-only Research Memory fixture with the native reader's lookup shape."""

    def __init__(self, *, negative: set[str] = frozenset(), matched: set[str] = frozenset(),
                 fail: BaseException | None = None) -> None:
        self.negative, self.matched, self.fail = negative, matched | negative, fail
        self.calls = 0

    def lookup_definition(self, definition):
        self.calls += 1
        if self.fail is not None:
            raise self.fail
        fp = fingerprint(definition)
        records = []
        if fp in self.matched:
            records = [{"source_key": "PG-1", "authority_state": "REPO_INDEX",
                        "classification": "NO-GO" if fp in self.negative else "PENDING",
                        "resolved_classification": None, "evidence": []}]
        return {"matched": fp in self.matched, "fingerprint_version": FINGERPRINT_VERSION,
                "fingerprint_sha256": fp, "definition": definition.canonical_mapping(),
                "index_not_truth": True, "records": records, "repo_sha": HEAD.repo_sha,
                "postgres_boundary": "default_transaction_read_only=on; SET TRANSACTION READ ONLY",
                "authority": {"not_scientific_truth": True}}


def consumer(memory=None, git=None) -> dc.DiscoveryIntentConsumer:
    return dc.DiscoveryIntentConsumer(ROOT, HEAD, memory_reader=memory, git=git)


def _by_id(summary: dict) -> dict:
    return {idea["idea_id"]: idea for idea in summary["ideas"]}


@pytest.fixture
def batch_packet(tmp_path):
    return make_packet(tmp_path, [_idea("FLOW", _native()), _idea("VOL", _vol_native()), _idea("LOB", None)])


def test_all_typed_ideas_become_native_intents_and_lead_is_retained(tmp_path, batch_packet):
    summary, intents = consumer(FrozenMemory()).build_batch(batch_packet)
    got = _by_id(summary)
    source = _by_id(di.verify_directory(batch_packet))
    assert [i["idea_id"] for i in summary["ideas"]] == ["FLOW", "VOL", "LOB"]  # source order, no ranking
    assert summary["counts"][dc.BUILT] == ["FLOW", "VOL"] and summary["counts"][dc.LEAD] == ["LOB"]
    families = set()
    for idea_id in ("FLOW", "VOL"):
        ref = got[idea_id]["native_intent"]
        intent = BoundedResearchIntentV1.model_validate_json(intents[ref["file"]])
        families.add(intent.strategy_family)
        assert intent.content_sha256 == semantic_content_sha256(intent) == ref["content_sha256"]
        assert intent.fingerprint_sha256 == got[idea_id]["fingerprint"]["sha256"]
        assert intent.repo_sha == HEAD.repo_sha and intent.automatic_consumers == []
        assert all(a["semantic_relevance"] == "REVIEWER_CHECK_REQUIRED" for a in got[idea_id]["evidence_anchors"])
        assert any(r.startswith("SEMANTIC_RELEVANCE REVIEWER_CHECK_REQUIRED") for r in got[idea_id]["review_requirements"])
        assert any(r.startswith("DATA_AVAILABILITY_AND_COVERAGE_UNPROVEN") for r in got[idea_id]["review_requirements"])
        assert f"CRITIC_GAP: gap for {idea_id}" in got[idea_id]["review_requirements"]
        # Original 02A memory (no Postgres) is kept; the fresh lookup is separate and never novelty.
        assert got[idea_id]["original_memory"] == source[idea_id]["memory"]
        assert got[idea_id]["original_memory"]["state"] != "NEW_UNMATCHED"
        assert got[idea_id]["refreshed_memory"]["state"] == "NO_EXACT_POSTGRES_MATCH_NOT_NOVELTY"
    assert families == {"order_flow_imbalance", "volatility_regime_transition"}
    lead = got["LOB"]
    assert lead["native_intent"] is None and lead["source_typed_status"] == "NOT_READY"
    assert "No CPW order-book capture exists" in lead["missing_evidence"]
    assert lead["critic_assessment"]["stance"] == "MIXED" and lead["next_legal_investigation"]
    assert summary["authority"] == dc.BATCH_AUTHORITY and summary["authority"]["not_authority"] is True
    assert summary["source_packet"]["content_sha256"] == di.verify_directory(batch_packet)["content_sha256"]


def test_materialize_is_deterministic_verifies_and_replays(tmp_path, batch_packet):
    memory = FrozenMemory()
    for name in ("a", "b"):
        summary, intents = consumer(memory).build_batch(batch_packet)
        dc.write_batch(summary, intents, tmp_path / name)
    files_a = sorted(p.relative_to(tmp_path / "a").as_posix() for p in (tmp_path / "a").rglob("*") if p.is_file())
    assert files_a == ["SHA256SUMS", "intents/00.native_intent.json", "intents/01.native_intent.json", "summary.json"]
    for rel in files_a:
        assert (tmp_path / "a" / rel).read_bytes() == (tmp_path / "b" / rel).read_bytes()
    assert dc.verify_batch(tmp_path / "a")["content_sha256"] == summary["content_sha256"]
    assert dc.replay_batch(consumer(FrozenMemory()), tmp_path / "a", batch_packet)
    # A different memory state is a different batch; replay never papers over it.
    flow_fp = _by_id(summary)["FLOW"]["fingerprint"]["sha256"]
    with pytest.raises(dc.ConsumerError, match="replay"):
        dc.replay_batch(consumer(FrozenMemory(matched={flow_fp})), tmp_path / "a", batch_packet)


class _LeakyDriverError(Exception):
    pass


@pytest.mark.parametrize("memory, cause", [
    (None, "RESEARCH_MEMORY_READONLY_DSN not configured"),
    (FrozenMemory(fail=ResourceDeniedError("Research Memory role has mutation privilege on hypothesis_items")),
     "mutation privilege"),
    (FrozenMemory(fail=_LeakyDriverError("connect failed postgresql://reader:hunter2@db.internal/rm")),
     "_LeakyDriverError"),
])
def test_unavailable_or_write_capable_memory_fails_closed_and_keeps_leads(tmp_path, batch_packet, memory, cause):
    summary, intents = consumer(memory).build_batch(batch_packet)
    assert intents == {}
    got = _by_id(summary)
    assert summary["counts"][dc.BLOCKED_MEMORY] == ["FLOW", "VOL"] and summary["counts"][dc.LEAD] == ["LOB"]
    for idea_id in ("FLOW", "VOL"):
        assert got[idea_id]["native_intent"] is None
        assert got[idea_id]["refreshed_memory"]["status"] == "MEMORY_UNAVAILABLE"
        assert cause in got[idea_id]["block_reasons"][0]
    text = json.dumps(summary)
    assert "hunter2" not in text and "db.internal" not in text
    dc.write_batch(summary, intents, tmp_path / "out")
    assert not (tmp_path / "out" / dc.INTENT_DIR).exists()
    assert dc.verify_batch(tmp_path / "out")["counts"][dc.BUILT] == []


def test_prior_failure_duplicate_and_similarity_are_retained_not_equated(tmp_path):
    similar = _native(request_id="REQ-SIM", strategy_family="momentum", mechanism="Different wording entirely.")
    packet = make_packet(tmp_path, [_idea("H2", _h002_native()), _idea("SIM", similar),
                                    _idea("DUP", _native(request_id="REQ-DUP"))])
    h002_fp = fingerprint(next(s for s in load_repo_memory_seeds(ROOT) if s.source_key == "H-002").definition)
    dup_fp = di.verify_directory(packet)["ideas"][2]["fingerprint"]["sha256"]
    summary, intents = consumer(FrozenMemory(negative={h002_fp}, matched={dup_fp})).build_batch(packet)
    got = _by_id(summary)
    assert got["H2"]["original_memory"]["state"] == "PRIOR_FAILED_INVESTIGATION"
    assert got["H2"]["original_memory"]["retained_negative_findings"][0]["classification"] == "NO-GO"
    assert got["H2"]["refreshed_memory"]["state"] == "PRIOR_FAILED_INVESTIGATION"
    assert got["DUP"]["refreshed_memory"]["state"] == "EXACT_DUPLICATE"
    sim = got["SIM"]
    assert sim["original_memory"]["state"] == "POSSIBLE_SEMANTIC_SIMILARITY"
    assert all("not a proven duplicate" in f["assertion"] for f in sim["original_memory"]["semantic_similarity_flags"])
    assert sim["refreshed_memory"]["state"] == "NO_EXACT_POSTGRES_MATCH_NOT_NOVELTY"
    h2_intent = BoundedResearchIntentV1.model_validate_json(intents[got["H2"]["native_intent"]["file"]])
    assert h2_intent.research_memory.records[0]["classification"] == "NO-GO"  # negative carried, not hidden
    assert all(i["status"] == dc.BUILT for i in summary["ideas"])  # review-required, never admitted


def test_historical_packet_is_refused_and_inspectable_only(tmp_path):
    packet = make_packet(tmp_path, [_idea("FLOW", _native())], repo_sha=HISTORICAL_SHA)
    report = dc.inspect_source(packet, HEAD)
    assert report["binding"] == "HISTORICAL_SOURCE_SHA_NOT_CURRENT_HEAD_MATERIALIZATION_REFUSED"
    assert report["source_repo_sha"] == HISTORICAL_SHA and report["ideas"][0]["typed_status"] == "TYPED_VALID"
    memory = FrozenMemory()
    with pytest.raises(dc.ConsumerError, match="never rebound"):
        consumer(memory).build_batch(packet)
    assert memory.calls == 0
    # Rebinding the packet SHA alone is caught by the retained, hashed run manifest.
    resign(packet, lambda p: p.update(repo_sha=HEAD.repo_sha))
    with pytest.raises(di.PacketError, match="repo SHA"):
        consumer(memory).build_batch(packet)


class _DriftedGit(_WorkingTreeGit):
    def blob(self, relative_path):
        raw = super().blob(relative_path)
        return raw + b"\n" if relative_path.endswith("H-005/HYPOTHESIS.md") else raw

    def blob_sha256(self, relative_path):
        return hashlib.sha256(self.blob(relative_path)).hexdigest()


def test_evidence_hash_drift_blocks_only_that_idea(tmp_path, batch_packet):
    summary, intents = consumer(FrozenMemory(), git=_DriftedGit()).build_batch(batch_packet)
    got = _by_id(summary)
    assert got["FLOW"]["status"] == dc.BUILT and list(intents) == ["intents/00.native_intent.json"]
    assert got["VOL"]["status"] == dc.BLOCKED_EVIDENCE and got["VOL"]["native_intent"] is None
    assert any("evidence://hypothesis/H-005" in reason for reason in got["VOL"]["block_reasons"])

    def drift(packet):
        packet["ideas"][0]["evidence_anchors"][0]["artifact_sha256"] = "0" * 64
    resign(batch_packet, drift)
    got = _by_id(consumer(FrozenMemory()).build_batch(batch_packet)[0])
    assert got["FLOW"]["status"] == dc.BLOCKED_EVIDENCE
    assert any("artifact_sha256 drifted" in reason for reason in got["FLOW"]["block_reasons"])


def test_public_source_cannot_be_forged_into_repo_anchor(tmp_path, batch_packet):
    def forge(packet):
        source = next(s for s in packet["sources"] if s["url_or_uri"] == "project://feature-availability")
        source["kind"] = "public"
    resign(batch_packet, forge)
    summary, intents = consumer(FrozenMemory()).build_batch(batch_packet)
    assert intents == {} and summary["counts"][dc.BLOCKED_EVIDENCE] == ["FLOW", "VOL"]
    assert any("public" in r for r in _by_id(summary)["FLOW"]["block_reasons"])


def _set(path, value):
    def mutate(packet):
        target = packet
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return mutate


@pytest.mark.parametrize("mutate", [
    _set(["schema_version"], "cpw_hermes_discovery_intent_packet_v2"),
    _set(["unexpected"], True),
    _set(["ideas", 0, "unexpected"], True),
    _set(["ideas", 0, "validated_draft_input", "mechanism"], "A rewritten mechanism."),
    _set(["ideas", 0, "hermes_authored", "title"], "Retitled"),
    _set(["ideas", 1, "idea_id"], "FLOW"),
    _set(["ideas", 2, "typed_status"], "TYPED_VALID"),
    _set(["ideas", 0, "fingerprint", "sha256"], "0" * 64),
    _set(["authority", "admission_authority"], True),
    _set(["model_turn_receipts", 2, "session_id"], "sess-0"),
    _set(["summary", "typed_valid"], ["FLOW"]),
    lambda p: p["ideas"].reverse(),
])
def test_resigned_tampering_fails_globally_with_no_output(tmp_path, batch_packet, mutate):
    resign(batch_packet, mutate)
    with pytest.raises((dc.ConsumerError, di.PacketError)):
        summary, intents = consumer(FrozenMemory()).build_batch(batch_packet)
        dc.write_batch(summary, intents, tmp_path / "out")
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("case", ["input", "unrecorded", "sums"])
def test_unsigned_tampering_and_unrecorded_files_fail_globally(tmp_path, batch_packet, case):
    if case == "input":
        (batch_packet / "inputs" / "critic_result.md").write_text("tampered", encoding="utf-8")
    elif case == "unrecorded":
        (batch_packet / "inputs" / "extra.json").write_text("{}", encoding="utf-8")
        resign(batch_packet, lambda p: None)  # inventory covers it, but no manifest records it
    else:
        (batch_packet / "SHA256SUMS").write_text("", encoding="utf-8")
    with pytest.raises((dc.ConsumerError, di.PacketError)):
        consumer(FrozenMemory()).build_batch(batch_packet)


def _link(link: Path, target: Path) -> None:
    if sys.platform == "win32":
        import _winapi
        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


def test_links_traversal_names_and_output_collision(tmp_path, batch_packet):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (elsewhere / "x.json").write_text("{}", encoding="utf-8")
    _link(batch_packet / "inputs" / "linked", elsewhere)
    with pytest.raises(dc.ConsumerError, match="symlink or junction"):
        consumer(FrozenMemory()).build_batch(batch_packet)
    os.rmdir(batch_packet / "inputs" / "linked") if sys.platform == "win32" else os.unlink(batch_packet / "inputs" / "linked")
    summary, intents = consumer(FrozenMemory()).build_batch(batch_packet)
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "keep.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(dc.ConsumerError, match="no overwrite"):
        dc.write_batch(summary, intents, occupied)
    assert [p.name for p in occupied.iterdir()] == ["keep.txt"]
    with pytest.raises(dc.ConsumerError, match="external"):
        dc.write_batch(summary, intents, ROOT / "scratch" / "dc-should-not-exist")
    with pytest.raises(dc.ConsumerError, match="parent"):
        dc.write_batch(summary, intents, tmp_path / "missing" / "out")
    _link(tmp_path / "linked-parent", elsewhere)
    with pytest.raises(dc.ConsumerError, match="symlink or junction"):
        dc.write_batch(summary, intents, tmp_path / "linked-parent" / "out")
    renamed = batch_packet.with_name("not-a-packet")
    batch_packet.rename(renamed)
    with pytest.raises(dc.ConsumerError, match="discovery-intent"):
        consumer(FrozenMemory()).build_batch(renamed)
    assert not list(tmp_path.glob("*.partial-*"))


@pytest.mark.parametrize("competitor", ["empty_dir", "dir_with_file", "file"])
def test_target_created_after_preflight_is_never_replaced(tmp_path, batch_packet, monkeypatch, competitor):
    summary, intents = consumer(FrozenMemory()).build_batch(batch_packet)
    output = tmp_path / "raced"
    real_verify = dc.verify_batch

    def verify_then_competitor_creates_target(directory):
        result = real_verify(directory)  # the staged batch is complete and valid at this point
        if competitor == "file":
            output.write_bytes(b"competitor")
        else:
            output.mkdir()
            if competitor == "dir_with_file":
                (output / "keep.txt").write_bytes(b"competitor")
        return result

    monkeypatch.setattr(dc, "verify_batch", verify_then_competitor_creates_target)
    with pytest.raises(dc.ConsumerError, match="no overwrite"):
        dc.write_batch(summary, intents, output)
    if competitor == "file":
        assert output.read_bytes() == b"competitor"
    else:
        assert sorted(p.name for p in output.iterdir()) == ([] if competitor == "empty_dir" else ["keep.txt"])
    assert not (output / dc.SUMMARY_FILE).exists() if output.is_dir() else True
    assert not list(tmp_path.glob("raced.partial-*"))  # staging cleaned up, nothing published
    monkeypatch.setattr(dc, "verify_batch", real_verify)
    dc.write_batch(summary, intents, tmp_path / "ordinary")  # ordinary publication still works
    assert dc.replay_batch(consumer(FrozenMemory()), tmp_path / "ordinary", batch_packet)


def test_noreplace_primitive_on_this_platform_and_explicit_refusal_elsewhere(tmp_path, monkeypatch):
    source, target = tmp_path / "src", tmp_path / "dst"
    source.mkdir()
    (source / "a.txt").write_bytes(b"a")
    target.mkdir()
    with pytest.raises(dc.ConsumerError, match="no overwrite"):
        dc._rename_noreplace(source, target)  # the real OS primitive (MoveFileExW / renameat2)
    assert (source / "a.txt").read_bytes() == b"a" and list(target.iterdir()) == []
    dc._rename_noreplace(source, tmp_path / "fresh")
    assert (tmp_path / "fresh" / "a.txt").read_bytes() == b"a" and not source.exists()
    monkeypatch.setattr(dc.sys, "platform", "sunos5")
    with pytest.raises(dc.ConsumerError, match="refusing to publish"):
        dc._rename_noreplace(tmp_path / "fresh", tmp_path / "other")
    assert (tmp_path / "fresh" / "a.txt").exists() and not (tmp_path / "other").exists()


def test_verify_detects_batch_tampering(tmp_path, batch_packet):
    summary, intents = consumer(FrozenMemory()).build_batch(batch_packet)
    for case in ("intent", "extra", "authority", "built-without-file"):
        out = tmp_path / case
        dc.write_batch(summary, intents, out)
        if case == "intent":
            (out / "intents" / "00.native_intent.json").write_text("{}", encoding="utf-8")
        elif case == "extra":
            (out / "intents" / "02.native_intent.json").write_text("{}", encoding="utf-8")
        else:
            body = json.loads((out / "summary.json").read_text(encoding="utf-8"))
            if case == "authority":
                body["authority"]["admission_authority"] = True
            else:
                body["ideas"][2]["status"] = dc.BUILT
                body["counts"][dc.BUILT].append("LOB")
            body.pop("content_sha256")
            body["content_sha256"] = di.canonical_sha256(body)
            (out / "summary.json").write_text(json.dumps(body), encoding="utf-8")
            sums = "".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out).as_posix()}\n"
                           for p in sorted(out.rglob("*")) if p.is_file() and p.name != "SHA256SUMS")
            (out / "SHA256SUMS").write_text(sums, encoding="utf-8")
        with pytest.raises(dc.ConsumerError):
            dc.verify_batch(out)


def test_secret_in_output_publishes_nothing(tmp_path, batch_packet, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "Idea FLOW")  # any configured secret value appearing in output
    with pytest.raises(dc.ConsumerError, match="credential"):
        consumer(FrozenMemory()).build_batch(batch_packet)


def test_cli_without_dsn_materializes_blocked_batch_and_refuses_stale(tmp_path, batch_packet, monkeypatch, capsys):
    monkeypatch.delenv("RESEARCH_MEMORY_READONLY_DSN", raising=False)
    out = tmp_path / "cli-out"
    assert dc.main(["inspect", "--packet-dir", str(batch_packet)]) == 0
    assert not out.exists()
    assert dc.main(["materialize", "--packet-dir", str(batch_packet), "--output", str(out)]) == 0
    printed = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert printed[dc.BLOCKED_MEMORY] == ["FLOW", "VOL"] and printed[dc.LEAD] == ["LOB"]
    assert dc.main(["verify", "--batch-dir", str(out)]) == 0
    assert dc.main(["verify", "--batch-dir", str(out), "--packet-dir", str(batch_packet)]) == 0
    stale = make_packet(tmp_path, [_idea("FLOW", _native())], repo_sha=HISTORICAL_SHA, name="old")
    assert dc.main(["materialize", "--packet-dir", str(stale), "--output", str(tmp_path / "stale-out")]) == 1
    assert "DISCOVERY_INTENT_CONSUMER_FAILED" in capsys.readouterr().err
    assert not (tmp_path / "stale-out").exists()


def test_consumer_reaches_no_execution_or_scientific_surface():
    lines = (ROOT / "tools/hermes/discovery_intent_consumer.py").read_text(encoding="utf-8").splitlines()
    imports = "\n".join(line for line in lines if line.lstrip().startswith(("import ", "from ")))
    for forbidden in ("research_admission", "submit_proposal", "prefect", "research_factory", "research_autonomy",
                      "optuna", "governor", "runner", "nautilus", "broker", "exchange", "compiler", "subprocess",
                      "requests", "httpx", "socket"):
        assert forbidden not in imports
    parser_options = {"--packet-dir", "--output", "--batch-dir"}
    source = "\n".join(lines)
    assert {opt for opt in ("--sql", "--dsn", "--command", "--script", "--prompt", "--url") if opt in source} == set()
    assert all(opt in source for opt in parser_options)
