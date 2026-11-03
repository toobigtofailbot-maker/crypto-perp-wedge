"""Whole-cohort SOFTWARE FIXTURES, never physical Hermes/scientific evidence."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from test_hermes_discovery_intent_consumer import FrozenMemory, _idea, _native, make_packet
from test_hermes_intent_strategy_spec_handoff import _don_native, respond

from tools.hermes import research_cycle_coordinator as rc


@pytest.fixture
def cycle(tmp_path):
    make_packet(tmp_path, [_idea("DON", _don_native()), _idea("FLOW", _native(free_parameter_count=1)), _idea("LOB", None)],
                repo_sha=rc.RepoIdentity.resolve(rc.di.REPO_ROOT).repo_sha)
    return tmp_path / "cycle"


def build(cycle, output, **kwargs):
    return rc.ResearchCycle(memory_reader=FrozenMemory()).build(cycle, output, label=rc.FIXTURE, **kwargs)


def test_whole_cohort_native_chain_and_exact_replay(cycle, tmp_path):
    output = tmp_path / "first"
    build(cycle, output)
    responses = tmp_path / "developer"
    respond(output / "02c-prepared", responses, 0)
    respond(output / "02c-prepared", responses, 1)
    second = tmp_path / "second"
    result = build(cycle, second, responses=responses)
    assert [i["idea_id"] for i in result["ideas"]] == ["DON", "FLOW", "LOB"]
    assert [i["native_statuses"]["02c"] for i in result["ideas"]] == [rc.hs.DRAFTED, rc.hs.UNSUPPORTED, rc.hs.LEAD]
    assert result["ideas"][0]["technical_checks"][0]["compiler"]["status"] == "PASSED"
    assert result["ideas"][0]["technical_checks"][0]["compiler"]["label"] == "SYNTHETIC_TECHNICAL_ONLY"
    assert all(i["disposition"] == "blocked" and i["source_claims"] and i["critic_assessment"] for i in result["ideas"])
    assert result["kpis"]["native_eligible"] == result["kpis"]["genuine_experiments_completed"] == 0
    assert result["kpis"]["distinct_hypotheses"] == result["kpis"]["criticized_hypotheses"] == 3
    assert result["kpis"]["retained_scientific_denominator"] == 0
    assert result["provenance"] == rc.FIXTURE
    assert {r["role"] for r in result["model_turn_receipts"]} == {
        "director-sources", "research-scout", "research-critic", "director-synthesis", "director-intent"}
    assert rc.ResearchCycle(memory_reader=FrozenMemory()).replay(
        cycle, second, responses=responses, label=rc.FIXTURE) == result
    pending = json.loads((second / "memory-index-request.json").read_bytes())
    assert len(pending["records"]) == 3
    assert all(not r["successful_experiment"] and r["feedback"]["observed_metrics"] is None for r in pending["records"])
    request = json.loads((second / "study-request.json").read_bytes())
    assert request["execution_command"] is request["approval_marker"] is request["selected_idea"] is None
    assert "STRAT-SPEC-0003" in request["missing_mapping"]
    assert all(v == 0 for v in result["effects"].values())


def test_missing_memory_retains_all_ideas_and_never_means_novel(cycle, tmp_path):
    result = rc.ResearchCycle().build(cycle, tmp_path / "out", label=rc.CAPTURE)
    assert len(result["ideas"]) == 3 and result["kpis"]["model_cycles"] == 0
    assert all(i["native_statuses"]["02b"] == rc.dc.BLOCKED_MEMORY for i in result["ideas"][:2])
    assert all(not i["drafts"] for i in result["ideas"])


def test_cli_exercises_build_and_replay(cycle, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(rc, "_coordinator", lambda root: rc.ResearchCycle(memory_reader=FrozenMemory()))
    args = ["--cycle", str(cycle), "--output", str(tmp_path / "out"), "--provenance", rc.FIXTURE]
    assert rc.main(["build", *args]) == rc.main(["replay", *args]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert json.loads(lines[-1])["content_sha256"] == json.loads(lines[-2])["content_sha256"]


def test_collision_and_replay_tamper_fail_closed(cycle, tmp_path):
    out = tmp_path / "out"
    build(cycle, out)
    before = rc.hs._read_tree(out)
    with pytest.raises(rc.hs.HandoffError.__bases__[0], match="new; no overwrite"):
        build(cycle, out)
    assert rc.hs._read_tree(out) == before
    (out / "memory-index-request.json").write_text("{}")
    with pytest.raises(RuntimeError, match="inventory"):
        rc.ResearchCycle().replay(cycle, out, label=rc.FIXTURE)


def test_output_cannot_write_temporary_files_inside_frozen_input(cycle):
    before = rc._cycle_snapshot(cycle)
    with pytest.raises(RuntimeError, match="disjoint"):
        build(cycle, cycle / "nested-output")
    assert rc._cycle_snapshot(cycle) == before


@pytest.mark.parametrize("attack", ["extra", "duplicate_inventory", "stale_head", "secret", "private_url", "changed_source"])
def test_untrusted_cycle_inputs_are_refused(cycle, tmp_path, attack):
    manifest_path = cycle / "run_manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    if attack == "extra":
        (cycle / "unrecorded.json").write_text("{}")
    elif attack == "duplicate_inventory":
        manifest["artifacts"].append(manifest["artifacts"][0])
        manifest_path.write_text(json.dumps(manifest))
    elif attack == "stale_head":
        manifest["repo_sha"] = "0" * 40
        manifest_path.write_text(json.dumps(manifest))
    elif attack == "secret":
        (cycle / "critic_result.md").write_text("Bearer " + "x" * 32)
    elif attack == "private_url":
        source_path = cycle / "source_index.json"
        sources = json.loads(source_path.read_bytes())
        sources[0]["url_or_uri"] = "https://127.0.0.1/private"
        source_path.write_text(json.dumps(sources))
    else:
        (cycle / "critic_result.md").write_text("altered dissent")
    out = tmp_path / "out"
    with pytest.raises((RuntimeError, ValueError)):
        build(cycle, out)
    assert not out.exists()


def test_duplicate_semantics_cannot_be_three_hypotheses(tmp_path):
    make_packet(tmp_path, [_idea(f"COPY{n}", _native(request_id=f"REQ{n}")) for n in range(3)],
                repo_sha=rc.RepoIdentity.resolve(rc.di.REPO_ROOT).repo_sha)
    with pytest.raises(RuntimeError, match="distinct hypothesis"):
        build(tmp_path / "cycle", tmp_path / "out")


def test_cross_idea_or_widened_developer_response_is_not_admitted(cycle, tmp_path):
    build(cycle, tmp_path / "prepared")
    responses = tmp_path / "responses"
    respond(tmp_path / "prepared/02c-prepared", responses, 0)
    path = responses / "00.response.json"
    response = json.loads(path.read_bytes())
    response["reasoned_draft"]["parameter_bounds"][0]["maximum"] = 100000.0
    path.write_text(json.dumps(response))
    result = build(cycle, tmp_path / "widened", responses=responses)
    assert result["ideas"][0]["native_statuses"]["02c"] == rc.hs.INVALID
    assert not result["ideas"][0]["drafts"]
    response["request_id"] = "foreign-idea"
    path.write_text(json.dumps(response))
    with pytest.raises(RuntimeError, match="different request"):
        build(cycle, tmp_path / "substituted", responses=responses)


def test_production_tripwires_missing_or_forged_science_never_dispatches(cycle, tmp_path, monkeypatch):
    # Native call sites, not coordinator counters: every effect is forbidden on this blocked path.
    from tools.research_factory import manual_loop, mapper
    from tools.research_autonomy import contract_builder
    from tools.research_runner import run_offline_sweep
    from tools.research_memory.repository import ResearchMemoryRepository
    from tools.prefect_integration import research_factory_consumer as prefect_consumer
    import psycopg

    def forbidden(*args, **kwargs):
        pytest.fail("production scientific effect invoked")

    monkeypatch.setattr(mapper, "prepare_wave", forbidden)
    monkeypatch.setattr(manual_loop, "manual_research_loop", forbidden)
    monkeypatch.setattr(contract_builder.ContractBuilder, "build", forbidden)
    monkeypatch.setattr(run_offline_sweep, "main", forbidden)
    monkeypatch.setattr(rc.de, "inspect_local", forbidden)
    monkeypatch.setattr(psycopg, "connect", forbidden)
    monkeypatch.setattr(ResearchMemoryRepository, "put_non_authoritative", forbidden)
    monkeypatch.setattr(prefect_consumer, "register_research_factory_deployment", forbidden)
    monkeypatch.setattr(prefect_consumer, "run_manual_factory_request", forbidden)
    result = build(cycle, tmp_path / "blocked")
    assert all(n == 0 for n in result["effects"].values())
    # Forged approval is outside the closed input grammar, regardless of its prose or timestamps.
    for name in ("absent", "wrong", "stale", "expired", "holdout-overlap", "changed-costs", "out-of-budget"):
        (cycle / "approval.json").write_text(json.dumps({"approval": name}))
        with pytest.raises(RuntimeError, match="inventory"):
            build(cycle, tmp_path / name)
        (cycle / "approval.json").unlink()


def test_unknown_raw_file_refused_before_open(cycle, tmp_path, monkeypatch):
    raw = cycle / "history.csv"
    raw.write_text("TRIPWIRE_SYNTHETIC_NOT_HISTORICAL")
    original = Path.open
    def guarded(self, *args, **kwargs):
        if self == raw:
            pytest.fail("unexpected file opened before inventory refusal")
        return original(self, *args, **kwargs)
    monkeypatch.setattr(Path, "open", guarded)
    with pytest.raises(RuntimeError, match="no payload opened"):
        build(cycle, tmp_path / "out")


def test_replay_raw_directory_refused_before_open(cycle, tmp_path, monkeypatch):
    directory = tmp_path / "not-a-cycle"
    directory.mkdir()
    raw = directory / "history.csv"
    raw.write_text("TRIPWIRE_SYNTHETIC_NOT_HISTORICAL")
    original = Path.open
    def guarded(self, *args, **kwargs):
        if self == raw:
            pytest.fail("replay opened raw file before inventory refusal")
        return original(self, *args, **kwargs)
    monkeypatch.setattr(Path, "open", guarded)
    with pytest.raises(RuntimeError, match="no payload opened"):
        rc.ResearchCycle().replay(cycle, directory, label=rc.FIXTURE)


def test_head_changes_during_assembly_refuse_publication(cycle, tmp_path, monkeypatch):
    coordinator = rc.ResearchCycle(memory_reader=FrozenMemory())
    original = coordinator._head
    calls = []
    def changed():
        calls.append(None)
        if len(calls) == 2:
            raise rc.hs.HandoffError("repository identity changed during cycle")
        original()
    monkeypatch.setattr(coordinator, "_head", changed)
    with pytest.raises(RuntimeError, match="identity changed"):
        coordinator.build(cycle, tmp_path / "out", label=rc.FIXTURE)
    assert not (tmp_path / "out").exists()


def test_no_default_model_call_or_retry(cycle, tmp_path, monkeypatch):
    run = rc.subprocess.run
    def forbidden(*args, **kwargs):
        if args[0][0] == "git":
            return run(*args, **kwargs)
        pytest.fail("unexpected model launch")
    monkeypatch.setattr(rc, "_coordinator", lambda root: rc.ResearchCycle())
    monkeypatch.setattr(rc.subprocess, "run", forbidden)
    # No launch for a fixture discover request; refuse before touching a provider.
    assert rc.main(["discover", "--cycle", str(cycle), "--output", str(tmp_path / "out"),
                    "--provenance", rc.FIXTURE, "--theme", "bounded research"]) == 1


def test_discover_delegates_once_and_preserves_native_turn_receipts(cycle, tmp_path, monkeypatch):
    import shutil
    original = rc.subprocess.run
    launches = []
    target = tmp_path / "native-capture"
    def launch(command, **kwargs):
        if command[0] == "git":
            return original(command, **kwargs)
        assert command[0] == "pwsh" and "-StructuredIntentHandoff" in command
        launches.append(command)
        shutil.copytree(cycle, target)  # SOFTWARE FIXTURE, no provider or subprocess launch.
        return rc.subprocess.CompletedProcess(command, 0)
    monkeypatch.setattr(rc.subprocess, "run", launch)
    monkeypatch.setattr(rc, "_coordinator", lambda root: rc.ResearchCycle())
    assert rc.main(["discover", "--cycle", str(target), "--output", str(tmp_path / "out"),
                    "--provenance", rc.CAPTURE, "--theme", "bounded research"]) == 0
    result = json.loads((tmp_path / "out/cycle-summary.json").read_bytes())
    assert len(launches) == 1 and result["budget"]["captured_native_turn_receipts"] == 5
    assert result["budget"]["automatic_retries"] == 0
    assert result["authorship"] == "NOT_INDEPENDENTLY_VERIFIED" and result["kpis"]["model_cycles"] == 0


@pytest.mark.parametrize("suffix", ["", ".discovery-intent"])
def test_discover_overlap_refused_before_model_launch(tmp_path, monkeypatch, suffix):
    original = rc.subprocess.run
    def no_model(command, **kwargs):
        if command[0] == "git":
            return original(command, **kwargs)
        pytest.fail("model launched for overlapping destinations")
    monkeypatch.setattr(rc.subprocess, "run", no_model)
    target = tmp_path / "native"
    assert rc.main(["discover", "--cycle", str(target), "--output", str(target) + suffix,
                    "--provenance", rc.CAPTURE, "--theme", "bounded research"]) == 1


def test_failed_discover_retains_attempt_without_retry(tmp_path, monkeypatch):
    original = rc.subprocess.run
    launches = []
    target = tmp_path / "failed-native"
    def failed(command, **kwargs):
        if command[0] == "git":
            return original(command, **kwargs)
        launches.append(command)
        target.mkdir()
        (target / "run_manifest.json").write_text('{"state":"FAILED","not_authority":true}')
        raise rc.subprocess.CalledProcessError(1, command)
    monkeypatch.setattr(rc.subprocess, "run", failed)
    assert rc.main(["discover", "--cycle", str(target), "--output", str(tmp_path / "out"),
                    "--provenance", rc.CAPTURE, "--theme", "bounded research"]) == 1
    assert len(launches) == 1 and (target / "run_manifest.json").is_file()
    assert not (tmp_path / "out").exists()


def test_discover_existing_native_packet_refused_before_launch(tmp_path, monkeypatch):
    original = rc.subprocess.run
    def no_model(command, **kwargs):
        if command[0] == "git":
            return original(command, **kwargs)
        pytest.fail("model launched despite existing native packet")
    monkeypatch.setattr(rc.subprocess, "run", no_model)
    target = tmp_path / "native"
    packet = Path(str(target) + rc.dc.SOURCE_SUFFIX)
    packet.mkdir()
    (packet / "sentinel").write_text("retained")
    assert rc.main(["discover", "--cycle", str(target), "--output", str(tmp_path / "out"),
                    "--provenance", rc.CAPTURE, "--theme", "bounded research"]) == 1
    assert (packet / "sentinel").read_text() == "retained"


def test_discover_other_checkout_refused_before_launch(tmp_path, monkeypatch):
    original = rc.subprocess.run
    def no_model(command, **kwargs):
        if command[0] == "git":
            return original(command, **kwargs)
        pytest.fail("model launched with another checkout as output")
    monkeypatch.setattr(rc.subprocess, "run", no_model)
    checkout = tmp_path / "other-checkout"
    checkout.mkdir()
    (checkout / ".git").write_text("gitdir: metadata-only marker")
    assert rc.main(["discover", "--cycle", str(tmp_path / "native"), "--output", str(checkout / "out"),
                    "--provenance", rc.CAPTURE, "--theme", "bounded research"]) == 1
