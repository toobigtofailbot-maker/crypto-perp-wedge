"""Manual boundary and recovery tests; no test marker is real Karl approval."""

import json
from pathlib import Path

import pytest

from tests.test_research_factory_mapper import factory_fixture
from tools.research_factory.evidence import EvidenceBlocked, bound_json, verify_fold_manifest
from tools.research_factory.manual_loop import manual_research_loop
from tools.research_factory.mapper import file_hash, prepare_wave, write_once
from tools.walkforward.purged_folds import PurgedFoldConfig, build_purged_manifest_and_comparison


def test_default_off_does_no_work():
    result = manual_research_loop(
        store=None,
        handoff=None,
        repo_root=Path("unused"),
        preparation_root=Path("unused"),
        output_root=Path("unused"),
        created_at_utc="unused",
    )
    assert result["factory_enabled"] is False
    assert result["disposition"] == "research_blocked"


def test_missing_approval_maps_then_stops_with_zero_runner_calls(tmp_path, monkeypatch):
    root, store, contract, handoff = factory_fixture(tmp_path)
    from tools.research_factory import manual_loop

    calls = []
    monkeypatch.setattr(
        manual_loop.adapter, "run_product_runner_adapter", lambda **kwargs: calls.append(kwargs)
    )
    result = manual_research_loop(
        store=store,
        handoff=handoff,
        repo_root=root,
        preparation_root=root / "scratch/prepared",
        output_root=root / "scratch/outputs",
        created_at_utc="2026-10-08T00:00:00Z",
        human_invocation=True,
    )
    assert result["withholding_reasons"] == ["blocked_approval"]
    assert calls == []
    assert json.loads((root / result["operator_request_path"]).read_text())["approved"] is False


def test_changed_scratch_hash_fails_closed(tmp_path):
    path = tmp_path / "scratch/a.json"
    write_once(path, {"synthetic_fixture": True})
    binding = {"path": "scratch/a.json", "sha256": file_hash(path)}
    path.write_text("{}")
    with pytest.raises(EvidenceBlocked, match="bytes changed"):
        bound_json(tmp_path, binding)


def test_exclusive_checkpoint_denies_replay_and_preserves_first_claim(tmp_path):
    checkpoint = tmp_path / "scratch/checkpoint.json"
    payload = {"state": "physical_execution_may_have_started", "unit_test_only": True}
    write_once(checkpoint, payload, exclusive=True)
    original = checkpoint.read_bytes()
    with pytest.raises(FileExistsError):
        write_once(checkpoint, payload, exclusive=True)
    assert checkpoint.read_bytes() == original


def test_fold_contract_enforces_real_purge_embargo_and_denominator(tmp_path):
    root, store, contract, handoff = factory_fixture(tmp_path)
    prepared = prepare_wave(
        store=store,
        handoff=handoff,
        contract=contract,
        repo_root=root,
        output_root=root / "scratch/prepared",
        created_at_utc="2026-10-08T00:00:00Z",
    )
    ids = [
        json.loads((root / prepared["paths"][k]).read_text())[key]
        for k, key in (
            ("spec", "strategy_spec_id"),
            ("vm", "variant_manifest_id"),
            ("sweep", "sweep_plan_id"),
        )
    ]
    config = PurgedFoldConfig(
        "WFM-9001",
        "2026-10-08T00:00:00Z",
        *ids,
        contract.data_identity,
        "15m",
        "2020-01-01T00:00:00Z",
        600,
        400,
        96,
        32,
        2,
        2,
    )
    manifest, _ = build_purged_manifest_and_comparison(config, source_commit=contract.repo_sha)
    path = write_once(root / "scratch/folds.json", manifest)
    binding = {"path": "scratch/folds.json", "sha256": file_hash(path)}
    verify_fold_manifest(root, binding, prepared, contract, purge_bars=96, embargo_bars=32)
    manifest["folds"][0]["selection_window_end_utc"] = manifest["folds"][0][
        "evaluation_window_start_utc"
    ]
    path.write_text(json.dumps(manifest))
    binding["sha256"] = file_hash(path)
    with pytest.raises(EvidenceBlocked):
        verify_fold_manifest(root, binding, prepared, contract, purge_bars=96, embargo_bars=32)
