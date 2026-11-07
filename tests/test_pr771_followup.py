"""Side 24 regressions. All bytes and identities are TEST_ONLY, never scientific evidence."""

from types import SimpleNamespace

import pytest

from tools.lab_pipeline import runner_adapter as adapter
from tools.research_autonomy import historical_source_gate as hsg


def _object(role, path):
    return {
        "role": role,
        "repo_path": path,
        "sha256": "sha256:" + "a" * 64,
        "byte_length": 1,
        "device": 0,
        "inode": 1,
    }


def test_d4_payload_has_its_own_role_scoped_root():
    assert hsg.HistoricalObject(**_object("ohlcv_input", "data/processed/d4a/TEST_ONLY.csv"))
    for role, path in [
        ("d4_catalog_slice", "data/processed/d4a/x.catalog_slice.json"),
        ("d2_import_report", "research/elsewhere/x.import_report.json"),
        ("ohlcv_input", "research/data_slices/x.csv"),
        ("ohlcv_input", "data/processed/d4a/../x.csv"),
        ("ohlcv_input", "data/processed/d4a//x.csv"),
        ("ohlcv_input", "C:/outside.csv"),
    ]:
        with pytest.raises(ValueError):
            hsg.HistoricalObject(**_object(role, path))


@pytest.mark.parametrize("canonical", [True, False])
def test_fake_custody_is_rejected_before_historical_reads(monkeypatch, canonical):
    class Fake:
        def require_preread(self, paths):
            pass

    def forbidden(*a, **k):
        pytest.fail("historical input touched before genuine custody check")

    monkeypatch.setattr(adapter, "_ordinary_input", forbidden)
    with pytest.raises(adapter.RunnerAdapterError, match="BLOCKED_NONHOLDOUT_CUSTODY"):
        adapter._execution_binding(
            canonical_15m=canonical,
            ohlcv_input_path="a",
            d4_catalog_slice_path="b",
            d2_import_report_path="c",
            custody=Fake(),
        )


def test_source_index_hash_and_exact_invocation_command_are_bound(tmp_path):
    from test_hermes_model_origin_receipt import build, verify

    cycle, receipt = build(tmp_path)
    (cycle / "source_index.json").write_bytes((cycle / "source_index.json").read_bytes() + b" ")
    assert verify(cycle, receipt)["reason"] == "SOURCE_INDEX_HASH"


def test_receipt_command_hash_is_not_just_syntactic(tmp_path):
    from test_hermes_model_origin_receipt import build, verify

    def mutate(cycle, manifest, receipt):
        receipt["turns"][0]["command_sha256"] = "f" * 64

    assert verify(*build(tmp_path, mutate=mutate))["reason"] == "COMMAND_BINDING"


def test_rehashed_source_index_must_still_match_observed_source_turn(tmp_path):
    import hashlib

    from test_hermes_model_origin_receipt import build, verify

    def mutate(cycle, manifest, receipt):
        raw = b'[{"id":"S1","excerpt":"fabricated source truth"}]'
        (cycle / "source_index.json").write_bytes(raw)
        for artifact in manifest["artifacts"]:
            if artifact["path"] == "source_index.json":
                artifact["sha256"] = hashlib.sha256(raw).hexdigest()

    assert verify(*build(tmp_path, mutate=mutate))["reason"] == "SOURCE_TURN_BINDING"


@pytest.mark.parametrize(
    "change", [None, "physical_tail", "catalog_range", "import_range", "development", "rows"]
)
def test_full_physical_coverage_is_the_signed_window(tmp_path, change):
    start, step = 1577836800000, hsg.CADENCE["15m"]
    window = hsg.Interval(start_ms=start, end_ms=start + 2 * step)
    request = SimpleNamespace(effective_window=window, data_version="TEST_ONLY")
    contract = SimpleNamespace(
        split_protocol=SimpleNamespace(
            development_window="2020-01-01T00:00:00Z/2020-01-01T00:30:00Z"
        )
    )
    coverage = {
        "start_utc": "2020-01-01T00:00:00Z",
        "end_utc": "2020-01-01T00:15:00Z",
        "row_count": 2,
        "expected_row_count": 2,
    }
    catalog = {
        "range": dict(coverage),
        "catalog_version": "TEST_ONLY",
        "source_type": "offline_bulk_or_local_file",
        "stream": "ohlcv",
    }
    report = {"range": dict(coverage)}
    times = [start, start + step]
    if change == "physical_tail":
        times.append(start + 2 * step)
    elif change == "catalog_range":
        catalog["range"]["end_utc"] = "2020-01-01T00:30:00Z"
    elif change == "import_range":
        report["range"]["start_utc"] = "2019-12-31T23:45:00Z"
    elif change == "development":
        contract.split_protocol.development_window = "2020-01-01T00:00:00Z/2020-01-01T00:15:00Z"
    elif change == "rows":
        catalog["range"]["row_count"] = 1
    path = tmp_path / "TEST_ONLY.csv"
    path.write_text("open_time_ms\n" + "\n".join(map(str, times)) + "\n")
    with path.open("rb") as stream:
        if change:
            with pytest.raises(hsg.Refused):
                hsg._verify_coverage(request, contract, catalog, report, stream.fileno())
        else:
            hsg._verify_coverage(request, contract, catalog, report, stream.fileno())


@pytest.mark.parametrize("receipt", [{}, {"execution_sha256": "sha256:" + "0" * 64}])
def test_original_population_requires_exact_custody_execution_receipt(
    tmp_path, monkeypatch, receipt
):
    from test_research_factory_mapper import factory_fixture

    from tools.research_factory import evidence, mapper

    root, store, contract, handoff = factory_fixture(tmp_path)
    prepared = mapper.prepare_wave(
        store=store,
        handoff=handoff,
        contract=contract,
        repo_root=root,
        output_root=root / "scratch/prepared",
        created_at_utc="2026-10-08T00:00:00Z",
    )
    prepared.update(
        schema_version=mapper.ORIGINAL_SCHEMA, source_paths={"spec": mapper.SOURCE_SPEC}
    )
    summary_path = mapper.write_once(
        root / "scratch/summary.json",
        {
            "adapter_status": "completed",
            "full_denominator_preserved": True,
            "source_bindings": {
                "execution": {"mode": "canonical_15m_d4_provenance"},
                "custody_receipt": receipt,
                "execute_approval_sha256": "sha256:" + "a" * 64,
            },
        },
    )

    def forbidden(*a, **k):
        pytest.fail("original evidence must not reread historical inputs")

    monkeypatch.setattr(adapter, "_execution_binding", forbidden)
    monkeypatch.setattr(adapter, "_validate_real_execution", forbidden)
    with pytest.raises(evidence.EvidenceBlocked, match="BLOCKED_ORIGINAL_SOURCE_REQUIRED"):
        evidence.verify_population(
            root,
            prepared,
            {"path": "scratch/summary.json", "sha256": mapper.file_hash(summary_path)},
            contract,
        )
