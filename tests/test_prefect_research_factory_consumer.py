"""Engineering fixtures only: no marker here grants real scientific authority."""

import copy
import json
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from pathlib import Path
from threading import Barrier, Event

import pytest
from prefect.exceptions import FailedRun
from prefect.states import get_state_exception

from tests.test_research_factory_mapper import factory_fixture
from tools.prefect_integration import research_factory_consumer as consumer
from tools.research_autonomy.handoff import write_handoff
from tools.research_factory.mapper import file_hash, prepare_wave, write_once


@pytest.fixture
def fixture(tmp_path, monkeypatch):
    root, store, contract, handoff = factory_fixture(tmp_path)
    path = write_handoff(handoff, repo_root=root)
    inputs = {}
    for key in (
        "ohlcv_input",
        "d4_catalog_slice",
        "d2_import_report",
        "fold_manifest",
        "execute_approval",
    ):
        local = write_once(root / f"scratch/inputs/{key}.json", {"unit_fixture": True})
        inputs[key] = {"path": local.relative_to(root).as_posix(), "sha256": file_hash(local)}
    request = {
        "schema_version": "cpw_prefect_factory_request_v1",
        "handoff": {"path": path.relative_to(root).as_posix(), "sha256": file_hash(path)},
        "repo_sha": handoff.repo_sha,
        "campaign_id": handoff.campaign_id,
        "search_id": handoff.search_id,
        "contract_hash": handoff.contract_hash,
        "handoff_content_sha256": handoff.content_sha256,
        "scientific_trial_ids": [
            p.scientific_trial_id
            for p in handoff.proposal_records
            if p.status == "ACCEPTED_FOR_SCIENTIFIC_EXECUTION"
        ],
        "created_at_utc": "2026-10-08T00:00:00Z",
        "preparation_root": "scratch/prepared",
        "output_root": "scratch/WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04/outputs/unit",
        **inputs,
    }
    # These two stubs isolate real data/approval/fold execution, never the mapper or claim.
    monkeypatch.setattr(consumer, "_approval", lambda *args: None)
    # This synthetic repository has an exact metadata-only HEAD, not deployed code.
    monkeypatch.setattr(consumer, "_verify_consumer_source", lambda *args: None)
    monkeypatch.setattr(consumer, "verify_fold_manifest", lambda *args, **kwargs: None)
    monkeypatch.setattr(consumer.adapter, "REPO_ROOT", root)
    monkeypatch.setattr(
        consumer.adapter,
        "DEFAULT_OUTPUT_ROOT",
        root / "scratch/WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04/outputs",
    )
    store.load_scientific_protocol = lambda *_: {"purge_bars": 96, "embargo_bars": 32}
    store._transaction = lambda: nullcontext(None)
    store._search_active = lambda *args: None
    calls = []

    def manual(**kwargs):
        calls.append(kwargs)
        return {
            "disposition": "research_completed",
            "withholding_reasons": ["OOS withheld"],
            "runner_calls": 2,
            "scientific_denominator": 2,
        }

    monkeypatch.setattr(consumer, "manual_research_loop", manual)
    return root, store, contract, handoff, request, calls


def invoke(fixture, request=None, *, human=True):
    root, store, _, _, original, _ = fixture
    request = original if request is None else request
    manifest = root / ".cpw/active/prefect/research-factory/request.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(request))
    return consumer.run_manual_factory_request(
        manifest.relative_to(root).as_posix(),
        file_hash(manifest),
        human_invocation=human,
        store=store,
        repo_root=root,
    )


def test_default_off_does_not_read_or_dispatch(fixture):
    result = consumer.run_manual_factory_request("unused", "unused")
    assert result["withholding_reasons"] == ["factory_default_OFF"]
    assert fixture[-1] == []
    assert not list(fixture[0].glob(".cpw/active/prefect/research-factory/claims/*"))


@pytest.mark.parametrize(
    "change", ["missing", "extra", "source", "trial", "timestamp", "path", "marker", "data"]
)
def test_closed_invalid_requests_block_before_dispatch(fixture, change):
    request = copy.deepcopy(fixture[4])
    if change == "missing":
        request.pop("execute_approval")
    elif change == "extra":
        request["flow_run_id"] = "new-operational-id"
    elif change == "source":
        request["repo_sha"] = "a" * 40
    elif change == "trial":
        request["scientific_trial_ids"] = ["substituted"]
    elif change == "timestamp":
        request["created_at_utc"] = "bad"
    elif change == "path":
        request["preparation_root"] = "scratch/../escape"
    elif change == "marker":
        request["execute_approval"]["sha256"] = "sha256:" + "0" * 64
    elif change == "data":
        request["ohlcv_input"]["sha256"] = "sha256:" + "0" * 64
    result = invoke(fixture, request)
    assert result["operational_status"] == "blocked" and result["runner_calls"] == 0
    assert fixture[-1] == []


def test_exact_delegation_and_duplicate_without_completion(fixture):
    first = invoke(fixture)
    assert first["operational_status"] == "completed"
    kwargs = fixture[-1][0]
    request = fixture[4]
    assert kwargs["created_at_utc"] == request["created_at_utc"]
    assert kwargs["human_invocation"] is True
    assert kwargs["execute_approval_path"] == request["execute_approval"]["path"]
    assert kwargs["fold_manifest_binding"] == request["fold_manifest"]
    assert kwargs["handoff"].content_sha256 == fixture[3].content_sha256
    second = invoke(fixture)
    assert second["runner_calls"] == 0
    assert second["withholding_reasons"] == ["investigate_possible_physical_execution_before_rerun"]
    assert len(fixture[-1]) == 1


@pytest.mark.parametrize(
    "key,value",
    [
        ("created_at_utc", "2026-10-09T00:00:00Z"),
        ("output_root", "scratch/WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04/outputs/changed"),
        ("preparation_root", "scratch/elsewhere"),
    ],
)
def test_changed_request_over_claimed_science_cannot_dispatch(fixture, key, value):
    invoke(fixture)
    claim = next(fixture[0].glob(".cpw/active/prefect/research-factory/claims/*.json"))
    before = claim.read_bytes()
    changed = copy.deepcopy(fixture[4])
    changed[key] = value
    result = invoke(fixture, changed)
    assert result["withholding_reasons"] == ["investigate_conflicting_claim"]
    assert len(fixture[-1]) == 1 and claim.read_bytes() == before


@pytest.mark.parametrize("failure", [RuntimeError("secret database string"), KeyboardInterrupt()])
def test_crash_retains_claim_and_never_creates_scientific_failure(fixture, monkeypatch, failure):
    def crash(**kwargs):
        fixture[-1].append(kwargs)
        raise failure

    monkeypatch.setattr(consumer, "manual_research_loop", crash)
    if isinstance(failure, Exception):
        result = invoke(fixture)
        assert result["disposition"] == "research_blocked"
        assert "secret" not in json.dumps(result)
    else:
        with pytest.raises(KeyboardInterrupt):
            invoke(fixture)
    result = invoke(fixture)
    assert result["runner_calls"] == 0 and len(fixture[-1]) == 1


def test_concurrent_invocations_dispatch_once(fixture, monkeypatch):
    entered, finish = Event(), Event()
    original = consumer.manual_research_loop

    def slow(**kwargs):
        result = original(**kwargs)
        entered.set()
        assert finish.wait(10)
        return result

    monkeypatch.setattr(consumer, "manual_research_loop", slow)
    # Persist the manifest once; concurrent calls use identical frozen bytes.
    invoke(fixture, human=False)
    manifest = fixture[0] / ".cpw/active/prefect/research-factory/request.json"
    args = (manifest.relative_to(fixture[0]).as_posix(), file_hash(manifest))
    kwargs = {"human_invocation": True, "store": fixture[1], "repo_root": fixture[0]}
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(consumer.run_manual_factory_request, *args, **kwargs)
        assert entered.wait(10)
        second = pool.submit(consumer.run_manual_factory_request, *args, **kwargs).result()
        finish.set()
        assert first.result()["operational_status"] == "completed"
    assert second["operational_status"] == "blocked" and len(fixture[-1]) == 1


def test_invalid_or_revoked_exact_approval_has_zero_dispatch(fixture, monkeypatch):
    def reject(*args):
        raise consumer.adapter.RunnerAdapterError("invalid exact v2")

    monkeypatch.setattr(consumer, "_approval", reject)
    result = invoke(fixture)
    assert result["runner_calls"] == 0 and fixture[-1] == []
    assert not list(fixture[0].glob(".cpw/active/prefect/research-factory/claims/*"))


def test_simultaneous_claim_publication_has_one_winner(fixture, monkeypatch):
    barrier = Barrier(2)
    monkeypatch.setattr(
        consumer, "verify_fold_manifest", lambda *args, **kwargs: barrier.wait(timeout=15)
    )
    invoke(fixture, human=False)
    manifest = fixture[0] / ".cpw/active/prefect/research-factory/request.json"
    args = (manifest.relative_to(fixture[0]).as_posix(), file_hash(manifest))
    kwargs = {"human_invocation": True, "store": fixture[1], "repo_root": fixture[0]}
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = [
            f.result()
            for f in [
                pool.submit(consumer.run_manual_factory_request, *args, **kwargs) for _ in range(2)
            ]
        ]
    assert sorted(r["operational_status"] for r in results) == ["blocked", "completed"]
    assert len(fixture[-1]) == 1


def test_dirty_bound_source_blocks_before_dispatch(fixture):
    (fixture[0] / "research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json").write_text(
        "changed"
    )
    assert invoke(fixture)["operational_status"] == "blocked"
    assert fixture[-1] == []


def test_revoked_envelope_blocks_before_dispatch(fixture):
    def revoked(*args):
        raise ValueError("inactive")

    fixture[1]._search_active = revoked
    assert invoke(fixture)["runner_calls"] == 0 and fixture[-1] == []


def test_terminal_recovery_resolves_original_checkpoint_without_dispatch(fixture, monkeypatch):
    root, store, contract, handoff, request, calls = fixture
    prepared = prepare_wave(
        store=store,
        handoff=handoff,
        contract=contract,
        repo_root=root,
        output_root=root / request["preparation_root"],
        created_at_utc=request["created_at_utc"],
    )
    mapping = (root / prepared["paths"]["spec"]).parent / "mapping.json"
    binding = {"path": mapping.relative_to(root).as_posix(), "sha256": file_hash(mapping)}
    payload = {
        "mapping_binding": binding,
        "fold_manifest_binding": request["fold_manifest"],
        "approval_sha256": request["execute_approval"]["sha256"],
        "summary_binding": None,
        "fold_binding": None,
        "robustness_binding": None,
        "purge_bars": 96,
        "embargo_bars": 32,
    }
    write_once(
        mapping.parent / "evidence_completed_checkpoint.json",
        {
            **payload,
            "contract": contract.to_dict(),
            "mapping_sha256": binding["sha256"],
            "state": "physical_execution_may_have_started",
            "execution": None,
        },
    )
    store.load_trial_result = lambda *args, **kwargs: {"evidence_payload": json.dumps(payload)}

    def recovered(**kwargs):
        assert "execute_approval_path" not in kwargs  # Existing durable-only early return.
        return {
            "disposition": "research_completed",
            "withholding_reasons": ["OOS withheld"],
            "runner_calls": 0,
            "scientific_denominator": 2,
            "recovered": True,
        }

    monkeypatch.setattr(consumer, "manual_research_loop", recovered)
    result = invoke(fixture)
    assert result["operational_status"] == "recovered" and result["runner_calls"] == 0
    assert result["scientific_denominator"] == 2 and calls == []
    mapping.write_text("{}")
    assert invoke(fixture)["operational_status"] == "blocked"


def test_partial_terminal_outcome_is_investigation_only(fixture):
    first = fixture[4]["scientific_trial_ids"][0]
    fixture[1].load_trial_result = lambda trial, **kwargs: (
        {} if trial != first else {"audit": "partial"}
    )
    result = invoke(fixture)
    assert result["withholding_reasons"] == ["investigate_partial_terminal_commitment"]
    assert fixture[-1] == []


def test_reparse_path_denied_without_privilege(fixture, monkeypatch):
    original = Path.lstat

    class Reparse:
        st_mode = 0
        st_file_attributes = 0x400

    def lstat(path, *args, **kwargs):
        return Reparse() if path.name == "inputs" else original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "lstat", lstat)
    assert invoke(fixture)["operational_status"] == "blocked" and fixture[-1] == []


def test_flow_deployment_contract_and_no_success_on_block(monkeypatch, tmp_path):
    assert consumer.research_factory_consumer.retries == 0
    assert consumer.research_factory_consumer.persist_result is False
    monkeypatch.setattr(consumer, "_local_prefect", lambda: None)
    monkeypatch.setattr(
        consumer, "run_manual_factory_request", lambda *args, **kwargs: consumer._result()
    )
    state = consumer.research_factory_consumer.fn("manifest", "hash")
    assert state.is_failed() and json.loads(state.message)["runner_calls"] == 0
    exception = get_state_exception(state)
    assert isinstance(exception, FailedRun)
    assert json.loads(str(exception))["operational_status"] == "blocked"
    captured = {}

    class Sourced:
        def deploy(self, **kwargs):
            captured.update(kwargs)
            return "fixture"

    monkeypatch.setattr(
        type(consumer.research_factory_consumer),
        "from_source",
        staticmethod(lambda **kwargs: Sourced()),
    )
    monkeypatch.setattr(consumer, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(consumer, "_verify_consumer_source", lambda *args: None)
    monkeypatch.setattr(consumer, "_head", lambda *_: "a" * 40)
    monkeypatch.setattr(consumer.subprocess, "check_output", lambda *args, **kwargs: b"")
    consumer.register_research_factory_deployment(repo_root=tmp_path, version="a" * 40)
    assert captured["schedules"] == captured["triggers"] == []
    assert captured["build"] is False and captured["push"] is False
    assert captured["concurrency_limit"] == 1 and captured["version"] == "a" * 40
