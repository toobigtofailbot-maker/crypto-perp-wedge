from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path

import pytest

from tools.execution_evidence_contract import (
    CANONICALIZATION,
    RESULT_ENVELOPE_SCHEMA_VERSION,
    RUN_REQUEST_SCHEMA_VERSION,
    build_result_envelope,
    build_run_request,
    canonical_json_bytes,
    content_sha256,
    validate_result_envelope,
    validate_run_request,
)
from tools.execution_evidence_legacy_rp import (
    LEGACY_ADAPTER_VERSION,
    project_result_population_v1,
)
from tools.research_replay.normalization import CONTRACT_VERSION


REPO_ROOT = Path(__file__).resolve().parents[1]
RP_PATH = REPO_ROOT / "research/result_populations/RP-7520.result_population.json"
SHA_A = "sha256:" + "a" * 64
SHA_B = "sha256:" + "b" * 64
OUTCOME_CATEGORIES = (
    "successful",
    "failed",
    "invalid",
    "excluded",
    "errored",
    "aborted",
    "filtered",
    "data_unavailable",
    "not_attempted",
)


def _request(**overrides: object) -> dict:
    values = {
        "parent_identities": {
            "strategy_spec": {"id": "STRAT-SPEC-1", "content_sha256": SHA_A},
            "variant_manifest": {"id": "VM-1", "content_sha256": SHA_A},
            "sweep_plan": {"id": "SWEEP-1", "content_sha256": SHA_A},
        },
        "declared_variant_ids": ["VAR-1", "VAR-2"],
        "committed_denominator": 2,
        "data_identity": {
            "catalog_ref": "catalog",
            "slice_identity": "slice-1",
            "timeframe": "1h",
            "stream": "ohlcv",
        },
        "determinism": {"seed": 7},
        "scientific_assumptions": {
            "backtest_assumption_summary": {"fees": "taker"},
            "sizing_metadata": {"mode": "dynamic"},
            "data_availability_claim": None,
        },
    }
    values.update(overrides)
    return build_run_request(**values)


def _rows() -> list[dict]:
    return [
        {
            "variant_id": variant_id,
            "assignment_hash": SHA_A,
            "outcome_category": "successful",
            "attempted": True,
            "metrics": {"pnl": pnl, "sharpe": pnl / 10},
            "non_success": {"reason": None},
            "error": {"category": None},
            "data_coverage": {"slice": "slice-1"},
            "lineage": {"parent_variant_id": variant_id},
        }
        for variant_id, pnl in (("VAR-1", 10.0), ("VAR-2", 20.0))
    ]


def _provenance(engine: str = "engine-a") -> dict:
    return {
        "engine_id": engine,
        "engine_version": "1",
        "adapter_id": f"{engine}-adapter",
        "repo_commit": "abc",
        "environment_summary": ["offline"],
        "dependency_summary": [],
        "source_ref": None,
        "source_raw_sha256": None,
    }


def _envelope(*, rows: list[dict] | None = None, engine: str = "engine-a") -> dict:
    request = _request()
    result_rows = rows or _rows()
    counts = {category: 0 for category in OUTCOME_CATEGORIES}
    for row in result_rows:
        counts[row["outcome_category"]] += 1
    return build_result_envelope(
        request_content_sha256=request["request_content_sha256"],
        committed_denominator=len(result_rows),
        outcome_category_counts=counts,
        variant_result_rows=result_rows,
        execution_provenance=_provenance(engine),
    )


def test_canonical_serialization_is_order_independent_and_utf8() -> None:
    left = {"z": "café", "a": [1, True, None]}
    right = {"a": [1, True, None], "z": "café"}
    assert canonical_json_bytes(left) == canonical_json_bytes(right)
    assert canonical_json_bytes(left) == b'{"a":[1,true,null],"z":"caf\xc3\xa9"}'
    assert content_sha256(left) == content_sha256(right)
    assert not canonical_json_bytes(left).endswith(b"\n")
    assert CANONICALIZATION == "cpw_engine_neutral_json_v1"


@pytest.mark.parametrize("value", [{1: "bad"}, object(), float("nan"), float("inf"), -float("inf")])
def test_canonical_serialization_rejects_non_json_content(value: object) -> None:
    with pytest.raises(ValueError):
        canonical_json_bytes(value)


def test_request_identity_is_deterministic_engine_free_and_science_sensitive() -> None:
    baseline = _request()
    assert baseline == _request()
    assert "engine" not in json.dumps(baseline).lower()
    assert baseline["schema_version"] == RUN_REQUEST_SCHEMA_VERSION

    changed_parent = copy.deepcopy(baseline["parent_identities"])
    changed_parent["strategy_spec"]["content_sha256"] = SHA_B
    changed_data = copy.deepcopy(baseline["data_identity"])
    changed_data["slice_identity"] = "slice-2"
    changed_assumptions = copy.deepcopy(baseline["scientific_assumptions"])
    changed_assumptions["backtest_assumption_summary"]["fees"] = "maker"
    mutations = (
        _request(parent_identities=changed_parent),
        _request(data_identity=changed_data),
        _request(determinism={"seed": 8}),
        _request(scientific_assumptions=changed_assumptions),
    )
    assert all(
        request["request_content_sha256"] != baseline["request_content_sha256"]
        for request in mutations
    )


def test_result_identity_excludes_provenance_but_retains_it() -> None:
    left = _envelope(engine="engine-a")
    right = _envelope(engine="engine-b")
    assert left["evidence_content_sha256"] == right["evidence_content_sha256"]
    assert left["execution_provenance"] != right["execution_provenance"]
    assert left["execution_provenance"]["engine_id"] == "engine-a"
    assert right["execution_provenance"]["adapter_id"] == "engine-b-adapter"


def test_result_identity_changes_with_metric_outcome_or_population() -> None:
    baseline = _envelope()
    metric_rows = _rows()
    metric_rows[0]["metrics"]["pnl"] = 11.0
    outcome_rows = _rows()
    outcome_rows[0]["outcome_category"] = "failed"
    population_rows = _rows()[:1]
    assert _envelope(rows=metric_rows)["evidence_content_sha256"] != baseline["evidence_content_sha256"]
    assert _envelope(rows=outcome_rows)["evidence_content_sha256"] != baseline["evidence_content_sha256"]
    assert _envelope(rows=population_rows)["evidence_content_sha256"] != baseline["evidence_content_sha256"]


def test_legacy_projection_preserves_history_denominator_rows_and_input() -> None:
    source_bytes = RP_PATH.read_bytes()
    source = json.loads(RP_PATH.read_text(encoding="utf-8"))
    before = copy.deepcopy(source)
    request, envelope = project_result_population_v1(source, repo_root=REPO_ROOT)

    assert source == before
    assert request["schema_version"] == RUN_REQUEST_SCHEMA_VERSION
    assert request["scientific_assumptions"]["sizing_metadata"] == source["sizing_metadata"]
    assert envelope["schema_version"] == RESULT_ENVELOPE_SCHEMA_VERSION
    compatibility = envelope["compatibility_evidence"]
    assert compatibility["input_identity_hash"] == source["input_identity_hash"]
    assert compatibility["result_population_identity_hash"] == source["result_population_identity_hash"]
    assert compatibility["replay_normalization_contract_version"] == CONTRACT_VERSION
    assert envelope["execution_provenance"]["adapter_id"] == LEGACY_ADAPTER_VERSION
    assert request["request_content_sha256"].startswith("sha256:")
    assert envelope["evidence_content_sha256"].startswith("sha256:")
    assert request["request_content_sha256"] not in {
        source["input_identity_hash"]["hash"],
        source["result_population_identity_hash"]["hash"],
    }
    assert envelope["scientific_result"]["committed_denominator"] == len(
        source["variant_result_rows"]
    )
    assert len(envelope["scientific_result"]["variant_result_rows"]) == len(
        source["variant_result_rows"]
    )
    _, path_envelope = project_result_population_v1(RP_PATH, repo_root=REPO_ROOT)
    assert RP_PATH.read_bytes() == source_bytes
    assert path_envelope["execution_provenance"]["source_ref"] == (
        "research/result_populations/RP-7520.result_population.json"
    )
    assert path_envelope["execution_provenance"]["source_raw_sha256"] == (
        "sha256:" + hashlib.sha256(source_bytes).hexdigest()
    )


def test_legacy_row_ids_and_hashes_do_not_define_forward_evidence_identity() -> None:
    source = json.loads(RP_PATH.read_text(encoding="utf-8"))
    changed = copy.deepcopy(source)
    changed["variant_result_rows"][0]["row_id"] = "RP-9999-ROW-999999"
    changed["variant_result_rows"][0]["row_identity_hash"] = SHA_B
    _, baseline = project_result_population_v1(source, repo_root=REPO_ROOT)
    _, projected = project_result_population_v1(changed, repo_root=REPO_ROOT)
    assert projected["evidence_content_sha256"] == baseline["evidence_content_sha256"]
    assert (
        projected["compatibility_evidence"]["replay_normalized_stable_hash"]
        != baseline["compatibility_evidence"]["replay_normalized_stable_hash"]
    )


@pytest.mark.parametrize(
    "mutator,validator",
    [
        (lambda value: value.pop("data_identity"), validate_run_request),
        (lambda value: value.__setitem__("unknown", True), validate_run_request),
        (lambda value: value.__setitem__("unknown", True), validate_result_envelope),
        (lambda value: value.__setitem__("request_content_sha256", "sha256:BAD"), validate_run_request),
        (lambda value: value["determinism"].__setitem__("seed", 99), validate_run_request),
        (
            lambda value: value["scientific_result"]["variant_result_rows"][0]["metrics"].__setitem__(
                "pnl", 999.0
            ),
            validate_result_envelope,
        ),
        (
            lambda value: value["scientific_result"].__setitem__("committed_denominator", 3),
            validate_result_envelope,
        ),
    ],
)
def test_closed_contract_rejects_invalid_shapes_hashes_and_denominator(mutator, validator) -> None:
    value = _request() if validator is validate_run_request else _envelope()
    mutator(value)
    with pytest.raises(ValueError):
        validator(value)


def test_production_modules_keep_forbidden_frameworks_and_paths_unreachable() -> None:
    forbidden = (
        "prefect",
        "nautilus",
        "hermes",
        "tools.canon_intake",
        "tools.research_runner",
        "lib.backtest",
        "runtime",
        "paper",
        "live",
        "requests",
        "httpx",
        "urllib",
    )
    for relative in (
        "tools/execution_evidence_contract.py",
        "tools/execution_evidence_legacy_rp.py",
    ):
        path = REPO_ROOT / relative
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports: list[str] = []
        calls: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imports.append(node.module)
            elif isinstance(node, ast.Call):
                parts: list[str] = []
                target = node.func
                while isinstance(target, ast.Attribute):
                    parts.append(target.attr)
                    target = target.value
                if isinstance(target, ast.Name):
                    parts.append(target.id)
                    calls.append(".".join(reversed(parts)))
        assert not [name for name in imports if name.lower().startswith(forbidden)]
        assert not [name for name in calls if name.lower().startswith(forbidden)]
