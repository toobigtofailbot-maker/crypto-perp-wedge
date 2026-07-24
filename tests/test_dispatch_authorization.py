import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest
from jsonschema import Draft7Validator

import tools.canon_intake.dispatch_authorization as validator
from tools.canon_intake.dispatch_authorization import (
    APPROVAL_STATEMENT,
    DispatchAuthorizationError,
    authorization_core_sha256,
    repo_canonical_json_v1,
    serialize_dispatch_authorization,
    validate_dispatch_authorization,
)
from tools.canon_intake.queue_admission import approval_core_sha256
from tools.data.register_binance_usdtm_1d_lineage import (
    REQUIRED_COLUMNS as CANONICAL_1D_SOURCE_COLUMNS,
    build_lineage as build_1d_lineage,
)


def _hash(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _write_json(path: Path, value: object) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    path.write_bytes(raw)
    return raw


def _ref(path: str, raw: bytes, artifact_id: str | None = None) -> dict:
    result = {
        "path": path,
        "whole_file_sha256": _hash(raw),
        "byte_length": len(raw),
    }
    if artifact_id is not None:
        result["artifact_id"] = artifact_id
    return result


def _authority_flags() -> dict:
    return {
        "authorizes_one_single_use_dispatch": True,
        "artifact_invokes_runner": False,
        "authorizes_runner_execution": False,
        "authorizes_result_population": False,
        "authorizes_ranking_recommendation": False,
        "authorizes_candidate_lifecycle": False,
        "authorizes_readiness_promotion": False,
        "authorizes_standing_dispatcher_scheduler": False,
        "authorizes_retry_recovery": False,
        "authorizes_paper_live_runtime": False,
        "authorizes_oms_risk_reconciliation": False,
        "authorizes_broker_exchange_orders_positions_balances_capital": False,
        "authorizes_notifications": False,
    }


def _audit_non_authority() -> dict:
    return {
        "lifecycle_history_only": True,
        "does_not_invoke_runner": True,
        "not_result_population_authority": True,
        "not_ranking_recommendation_authority": True,
        "not_candidate_readiness_promotion_authority": True,
        "not_runtime_paper_live_authority": True,
    }


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def _commit(root: Path, message: str) -> None:
    _git(root, "add", ".")
    _git(
        root,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        message,
    )


def _fixture(tmp_path: Path, source_repo: Path):
    root = tmp_path / "repo"
    schemas = root / "research/schemas"
    schemas.mkdir(parents=True)
    for name in (validator.APPROVAL_SCHEMA, validator.AUDIT_SCHEMA):
        shutil.copy2(source_repo / "research/schemas" / name, schemas / name)

    spec_rel = "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json"
    spec = {"schema_version": "v1", "strategy_spec_id": "STRAT-SPEC-9001"}
    spec_raw = _write_json(root / spec_rel, spec)
    spec_canonical_hash = _hash(repo_canonical_json_v1(spec))

    readiness_rel = (
        "research/strategy_spec_external_content_readiness/"
        "SS-ECR-STRAT-SPEC-9001.external_content_readiness.json"
    )
    readiness = {
        "schema_version": "strategy_spec_external_content_readiness_v1",
        "fact_id": "SS-ECR-STRAT-SPEC-9001",
        "fact_path": readiness_rel,
        "strategy_spec": {
            "strategy_spec_id": "STRAT-SPEC-9001",
            "path": spec_rel,
        },
        "content_binding": {
            "raw_byte_length": len(spec_raw),
            "raw_file_sha256": _hash(spec_raw),
            "canonicalization": "repo_canonical_json_v1",
            "full_repo_canonical_json_sha256": spec_canonical_hash,
        },
        "readiness_state": "external_content_ready",
    }
    readiness_raw = _write_json(root / readiness_rel, readiness)

    vp_rel = (
        "research/strategy_spec_variant_planning_approvals/"
        "VPAPP-20260720-TEST9001.variant_planning_approval.json"
    )
    vp = {
        "approval_id": "VPAPP-20260720-TEST9001",
        "approval_artifact_target_path": vp_rel,
        "contract_core_sha256": "sha256:" + "1" * 64,
    }
    vp_raw = _write_json(root / vp_rel, vp)

    vm_rel = "research/variant_manifests/VM-9001.variant_manifest.json"
    vm = {
        "schema_version": "v1",
        "variant_manifest_id": "VM-9001",
        "parent_strategy_spec": {"strategy_spec_id": "STRAT-SPEC-9001"},
        "variant_planning_approval": {
            "approval_id": vp["approval_id"],
            "path": vp_rel,
            "sha256": _hash(vp_raw),
            "contract_core_sha256": vp["contract_core_sha256"],
        },
        "population_governance": {
            "declared_population": {"committed_population_count": 4}
        },
    }
    vm_raw = _write_json(root / vm_rel, vm)

    sweep_rel = "research/sweep_plans/SWEEP-PLAN-9001.sweep_plan.json"
    sweep = {
        "schema_version": "v1",
        "sweep_plan_id": "SWEEP-PLAN-9001",
        "parent_variant_manifest": {
            "variant_manifest_id": "VM-9001",
            "manifest_committed_population_count": 4,
        },
    }
    sweep_raw = _write_json(root / sweep_rel, sweep)

    data_rel = "data/processed/synthetic_btcusdt_1d.parquet"
    day_ms = 86_400_000
    start_ms = int(pd.Timestamp("2026-01-01T00:00:00Z").timestamp() * 1000)
    rows = []
    for offset in range(4):
        open_time_ms = start_ms + offset * day_ms
        open_price = 100.0 + offset
        rows.append(
            {
                "open_time_ms": open_time_ms,
                "open": open_price,
                "high": open_price + 2.0,
                "low": open_price - 1.0,
                "close": open_price + 1.0,
                "volume": 10.0 + offset,
                "close_time_ms": open_time_ms + day_ms - 1,
                "quote_asset_volume": 1_000.0 + offset,
                "num_trades": 20 + offset,
                "taker_buy_base_vol": 5.0 + offset,
                "taker_buy_quote_vol": 500.0 + offset,
                "ignore": 0,
            }
        )
    data_path = root / data_rel
    data_path.parent.mkdir(parents=True)
    pd.DataFrame(rows, columns=CANONICAL_1D_SOURCE_COLUMNS).to_parquet(
        data_path,
        index=False,
    )
    data_raw = data_path.read_bytes()

    validator_rel = validator.CANONICAL_1D_VALIDATOR_PATH
    validator_path = root / validator_rel
    validator_path.parent.mkdir(parents=True)
    shutil.copy2(source_repo / validator_rel, validator_path)
    validator_raw = validator_path.read_bytes()

    catalog_rel = "research/data_slices/synthetic_1d.catalog_slice.json"
    catalog = build_1d_lineage(
        data_path,
        logical_path=data_rel,
        expected_sha256=_hash(data_raw).removeprefix("sha256:"),
    )
    catalog_raw = _write_json(root / catalog_rel, catalog)

    funding_data_rel = "data/processed/synthetic_funding.parquet"
    funding_data_raw = b"synthetic funding data bytes\n"
    (root / funding_data_rel).write_bytes(funding_data_raw)
    funding_rel = "research/data_provenance/funding/synthetic.funding_provenance.json"
    funding = {
        "schema_version": "funding_series_provenance_v1",
        "funding_series_id": "synthetic_funding_series_v1",
        "intended_funding_mode": "on",
        "provenance_artifact": {
            "artifact_id": "FUNDING-PROV-SYNTHETIC-1",
            "path": funding_rel,
        },
        "file_identity": {
            "source_data_path": funding_data_rel,
            "raw_sha256": _hash(funding_data_raw),
            "byte_length": len(funding_data_raw),
            "row_count": 4,
        },
        "coverage": {
            "start_utc": "2026-01-01T00:00:00Z",
            "end_utc": "2026-01-04T00:00:00Z",
        },
        "event_fields": {
            "timestamp": {"semantics": "actual_exchange_funding_event_timestamp"},
            "funding_rate": {
                "units": "decimal_fraction_of_notional_per_funding_event"
            },
        },
        "alignment": {"boundary_rule_id": "synthetic_boundary_v1"},
        "policies": {
            "backfill": "forbidden",
            "interpolation": "forbidden",
            "forward_fill": "forbidden",
            "zero_substitution": "forbidden",
        },
    }
    funding_raw = _write_json(root / funding_rel, funding)

    runner_rel = "tools/fixture_runner/offline_research.py"
    runner_raw = b'RUNNER_VERSION = "fixture-runner-v1"\n'
    (root / runner_rel).parent.mkdir(parents=True)
    (root / runner_rel).write_bytes(runner_raw)

    packet_rel = "scratch/STAGE-A/FIXTURE.dispatch_packet.json"
    packet = {
        "packet_id": "DISPATCH-PACKET-FIXTURE-1",
        "packet_purpose": "exact_offline_research_dispatch_stage_a",
        "packet_version": "fixture-v1",
        "placeholder": False,
    }
    packet_raw = _write_json(root / packet_rel, packet)

    queue_id = "QI-20260720-TEST9001"
    queue_rel = f"research/queue/admissions/{queue_id}.queue_item.json"
    gate_id = "GATE-Q-TEST-9001"
    gate_rel = (
        f"research/queue/gate_q_approvals/{gate_id}.gate_q_approval.json"
    )
    gate = {
        "schema_version": "gate_q_queue_admission_approval_v1",
        "approval_id": gate_id,
        "approval_artifact_target_path": gate_rel,
        "approved_by": "Karl",
        "approved_at": "2026-07-20T12:00:00Z",
        "approval_scope": "one_append_only_queue_admission",
        "artifact_refs": {
            "strategy_spec": {"path": spec_rel, "sha256": _hash(spec_raw)},
            "variant_manifest": {"path": vm_rel, "sha256": _hash(vm_raw)},
            "sweep_plan": {"path": sweep_rel, "sha256": _hash(sweep_raw)},
            "variant_planning_approval": {
                "approval_id": vp["approval_id"],
                "path": vp_rel,
                "sha256": _hash(vp_raw),
                "contract_core_sha256": vp["contract_core_sha256"],
            },
        },
        "proposed_queue_item": {
            "queue_item_id": queue_id,
            "target_path": queue_rel,
            "bytes_sha256": "sha256:" + "0" * 64,
            "byte_encoding": "utf8_exact_file_bytes",
        },
        "approval_core_sha256": "sha256:" + "0" * 64,
        "approval_core_hash_scope": "gate_q_approval_core_v1",
        "approval_core_canonicalization": "repo_canonical_json_v1",
    }
    gate["approval_core_sha256"] = approval_core_sha256(gate)
    queue = {
        "schema_version": "canon_queue_item_v1",
        "queue_item_id": queue_id,
        "status": "admitted_non_dispatched",
        "gate_q": {
            "approval_id": gate_id,
            "path": gate_rel,
            "approval_core_sha256": gate["approval_core_sha256"],
        },
    }
    queue_raw = _write_json(root / queue_rel, queue)
    gate["proposed_queue_item"]["bytes_sha256"] = _hash(queue_raw)
    gate_raw = _write_json(root / gate_rel, gate)

    dispatch_id = "DSP-20260720-TEST9001"
    run_id = "RUN-20260720-TEST9001"
    dispatch_path = (
        f"research/queue/dispatch_records/{dispatch_id}.dispatch_record.json"
    )
    stream_path = (
        f"research/queue/execution_events/{run_id}.execution_events.jsonl"
    )
    gate_ref = {
        "approval_id": gate_id,
        "path": gate_rel,
        "whole_file_sha256": _hash(gate_raw),
        "byte_length": len(gate_raw),
        "core_sha256": gate["approval_core_sha256"],
        "core_hash_scope": "gate_q_approval_core_v1",
        "core_canonicalization": "repo_canonical_json_v1",
    }
    flags = _authority_flags()
    core = {
        "queue_binding": {
            "queue_item_id": queue_id,
            "path": queue_rel,
            "whole_file_sha256": _hash(queue_raw),
            "byte_length": len(queue_raw),
            "required_state": "admitted_non_dispatched",
            "gate_q": gate_ref,
        },
        "crossing_identities": {
            "dispatch_id": dispatch_id,
            "run_id": run_id,
            "dispatch_record_path": dispatch_path,
            "execution_event_stream_path": stream_path,
        },
        "dispatcher_packet": {
            "packet_id": packet["packet_id"],
            "packet_purpose": packet["packet_purpose"],
            "packet_version": packet["packet_version"],
            "path": packet_rel,
            "whole_file_sha256": _hash(packet_raw),
            "byte_length": len(packet_raw),
            "byte_encoding": "utf8_exact_file_bytes",
            "serialization": "deterministic_json_one_lf",
            "placeholder_forbidden": True,
        },
        "lineage": {
            "strategy_spec": {
                **_ref(spec_rel, spec_raw, "STRAT-SPEC-9001"),
                "content_canonical_sha256": spec_canonical_hash,
            },
            "external_content_readiness": {
                **_ref(
                    readiness_rel,
                    readiness_raw,
                    "SS-ECR-STRAT-SPEC-9001",
                ),
                "strategy_spec_raw_sha256": _hash(spec_raw),
                "strategy_spec_canonical_sha256": spec_canonical_hash,
            },
            "variant_planning_approval": {
                **_ref(vp_rel, vp_raw, vp["approval_id"]),
                "core_sha256": vp["contract_core_sha256"],
            },
            "variant_manifest": _ref(vm_rel, vm_raw, "VM-9001"),
            "sweep_plan": _ref(sweep_rel, sweep_raw, "SWEEP-PLAN-9001"),
            "gate_q": copy.deepcopy(gate_ref),
        },
        "dataset": {
            "canonical_route": "1d",
            "dataset_id": catalog["dataset_id"],
            "snapshot_version": catalog["snapshot_version"],
            "catalog_status": catalog["catalog_status"],
            "catalog_path": catalog_rel,
            "catalog_sha256": _hash(catalog_raw),
            "catalog_byte_length": len(catalog_raw),
            "data_path": data_rel,
            "data_sha256": _hash(data_raw),
            "data_byte_length": len(data_raw),
            "row_count": 4,
            "market": "BTCUSDT_BINANCE_USDTM_PERPETUAL",
            "timeframe": "1d",
            "cadence_ms": day_ms,
            "timezone": "UTC",
            "columns_schema_identity": _hash(
                repo_canonical_json_v1(CANONICAL_1D_SOURCE_COLUMNS)
            ),
            "coverage_start_utc": catalog["coverage"]["start_open_utc"],
            "coverage_end_utc": catalog["coverage"]["end_close_utc"],
            "duplicate_count": 0,
            "gap_count": 0,
            "missing_bar_count": 0,
            "open_or_incomplete_bar_count": 0,
            "partial_window_posture": "completed_bars_only_reject_partial",
            "source_type": "direct_public_archive_snapshot",
            "parent_identity_absent": True,
            "derivation_identity_absent": True,
            "validator_path": validator_rel,
            "validator_sha256": _hash(validator_raw),
            "validator_byte_length": len(validator_raw),
            "validation_identity": _hash(
                repo_canonical_json_v1(
                    {
                        "catalog_sha256": _hash(catalog_raw),
                        "validator_path": validator_rel,
                        "validator_sha256": _hash(validator_raw),
                        "catalog_matches_rebuilt_lineage": True,
                    }
                )
            ),
        },
        "funding": {
            "funding_mode": "on",
            "funding_series_id": funding["funding_series_id"],
            "provenance_artifact_id": funding["provenance_artifact"][
                "artifact_id"
            ],
            "provenance_artifact_path": funding_rel,
            "provenance_artifact_sha256": _hash(funding_raw),
            "provenance_artifact_byte_length": len(funding_raw),
            "funding_data_path": funding_data_rel,
            "funding_data_sha256": _hash(funding_data_raw),
            "funding_data_byte_length": len(funding_data_raw),
            "row_count": 4,
            "coverage_start_utc": "2026-01-01T00:00:00Z",
            "coverage_end_utc": "2026-01-04T00:00:00Z",
            "timestamp_semantics": "actual_exchange_funding_event_timestamp",
            "rate_units": "decimal_fraction_of_notional_per_funding_event",
            "boundary_rule_id": "synthetic_boundary_v1",
            "fill_forbidden": True,
            "interpolation_forbidden": True,
            "backfill_forbidden": True,
            "rounding_forbidden": True,
            "zero_substitution_forbidden": True,
        },
        "runner": {
            "invocation_kind": "python_module",
            "module": "tools.fixture_runner.offline_research",
            "source_path": runner_rel,
            "source_sha256": _hash(runner_raw),
            "source_byte_length": len(runner_raw),
            "version": "fixture-runner-v1",
        },
        "denominator": {
            "basis": "committed_pre_registered_population_count",
            "planned": 4,
            "variant_manifest_value": 4,
            "sweep_plan_value": 4,
            "mismatch_policy": "reject",
        },
        "budget": {
            "metric": "variant_attempts",
            "upper_bound": 4,
            "unit": "attempts",
            "comparison": "actual_lte_upper_bound",
            "retries_included": True,
            "retry_allowance": 0,
            "mismatch_or_exceed_policy": "reject",
        },
        "execution_parameters": {
            "seed": 7,
            "workers": 1,
            "one_shot": True,
            "automatic_retry": False,
            "automatic_second_invocation": False,
        },
        "output_targets": {
            "scratch_output_root": "scratch/FIXTURE-RUN/",
            "execution_event_stream_path": stream_path,
            "canonical_result_population_target_forbidden": True,
        },
        "authority_flags": copy.deepcopy(flags),
    }
    authorization_id = "KDAUTH-TEST-R2-9001"
    authorization_rel = (
        "research/queue/dispatch_authorizations/"
        f"{authorization_id}.dispatch_authorization.json"
    )
    authorization = {
        "schema_version": "canon_dispatch_authorization_v1",
        "authorization_id": authorization_id,
        "authorization_artifact_target_path": authorization_rel,
        "approved_by": "Karl",
        "approved_at": "2026-07-20T12:30:00-05:00",
        "authorization_scope": "one_single_use_dispatch",
        "approval_statement": APPROVAL_STATEMENT,
        "authorization_core": core,
        "authorization_core_sha256": authorization_core_sha256(core),
        "authorization_core_hash_scope": "dispatch_authorization_core_v1",
        "authorization_core_canonicalization": "repo_canonical_json_v1",
        "exact_content_and_target_only": True,
        "append_only": True,
        "single_use_authorization_id": True,
        "content_bound_freshness": True,
        "amendment_revocation_policy": (
            "append_new_supersession_or_revocation_event_before_consumption_only"
        ),
        "authority_flags": copy.deepcopy(flags),
    }
    authorization_path = root / authorization_rel
    authorization_path.parent.mkdir(parents=True)
    authorization_raw = serialize_dispatch_authorization(authorization)
    authorization_path.write_bytes(authorization_raw)

    created = {
        "schema_version": "canon_dispatch_authorization_audit_event_v1",
        "event_id": f"KDAUTH-EVENT-{authorization_id}-000001",
        "sequence_number": 1,
        "event_type": "authorization_created",
        "authorization_id": authorization_id,
        "authorization_path": authorization_rel,
        "authorization_file_sha256": _hash(authorization_raw),
        "authorization_byte_length": len(authorization_raw),
        "authorization_core_sha256": authorization["authorization_core_sha256"],
        "authorization_core_hash_scope": "dispatch_authorization_core_v1",
        "queue_item_id": queue_id,
        "dispatch_id": dispatch_id,
        "run_id": run_id,
        "occurred_at": "2026-07-20T12:31:00-05:00",
        "actor": "Karl",
        "tool_identity": "synthetic-kdauth-writer-v1",
        "event_payload": {
            "event_kind": "authorization_created",
            "creation_posture": "protected_exclusive_create",
        },
        "non_authority_declaration": _audit_non_authority(),
    }
    audit_path = root / validator.AUDIT_PATH
    audit_path.parent.mkdir(parents=True)
    audit_path.write_bytes(repo_canonical_json_v1(created) + b"\n")

    _git(root, "init", "-q")
    _commit(root, "synthetic valid KDAUTH")
    return {
        "root": root,
        "authorization_path": authorization_path,
        "authorization": authorization,
        "authorization_raw": authorization_raw,
        "audit_path": audit_path,
        "created": created,
    }


def _resign(fixture: dict) -> None:
    authorization = fixture["authorization"]
    authorization["authorization_core_sha256"] = authorization_core_sha256(
        authorization["authorization_core"]
    )
    fixture["authorization_raw"] = serialize_dispatch_authorization(authorization)
    fixture["authorization_path"].write_bytes(fixture["authorization_raw"])
    created = fixture["created"]
    created["authorization_file_sha256"] = _hash(fixture["authorization_raw"])
    created["authorization_byte_length"] = len(fixture["authorization_raw"])
    created["authorization_core_sha256"] = authorization[
        "authorization_core_sha256"
    ]
    fixture["audit_path"].write_bytes(repo_canonical_json_v1(created) + b"\n")


def _validate(fixture: dict, **kwargs):
    return validate_dispatch_authorization(
        repo_root=fixture["root"],
        authorization_path=fixture["authorization_path"],
        **kwargs,
    )


@pytest.fixture
def repo_root():
    return Path(__file__).resolve().parents[1]


def test_schemas_are_closed_valid_draft7(repo_root):
    for name in (validator.APPROVAL_SCHEMA, validator.AUDIT_SCHEMA):
        schema = json.loads(
            (repo_root / "research/schemas" / name).read_text(encoding="utf-8")
        )
        Draft7Validator.check_schema(schema)

        def walk(value):
            if isinstance(value, dict):
                if value.get("type") == "object":
                    assert value.get("additionalProperties") is False
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(schema)


def test_valid_synthetic_authorization_and_created_audit_pass(
    tmp_path, repo_root
):
    fixture = _fixture(tmp_path, repo_root)
    result = _validate(
        fixture,
        expected_whole_file_sha256=_hash(fixture["authorization_raw"]),
        expected_byte_length=len(fixture["authorization_raw"]),
    )
    assert result["valid"] is True
    assert result["lifecycle_state"] == "created"
    assert result["freshness"] == "content_bound_exact_equality_only"
    assert result["non_authority"]["does_not_invoke_runner"] is True


def test_cli_is_read_only_and_returns_structured_result(tmp_path, repo_root):
    fixture = _fixture(tmp_path, repo_root)
    before = {
        path.relative_to(fixture["root"]).as_posix(): _hash(path.read_bytes())
        for path in fixture["root"].rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.canon_intake.dispatch_authorization",
            "--repo-root",
            str(fixture["root"]),
            "--authorization",
            str(fixture["authorization_path"]),
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["valid"] is True
    after = {
        path.relative_to(fixture["root"]).as_posix(): _hash(path.read_bytes())
        for path in fixture["root"].rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    assert after == before


@pytest.mark.parametrize(
    "raw_mutation",
    [
        lambda raw: raw[:-1],
        lambda raw: raw + b"\n",
        lambda raw: raw.replace(b"\n", b"\r\n"),
        lambda raw: b"\xef\xbb\xbf" + raw,
        lambda raw: raw + b"x",
        lambda raw: raw.replace(b'  "append_only"', b'  "append_only" '),
    ],
)
def test_exact_serialization_and_one_lf_fail_closed(
    tmp_path, repo_root, raw_mutation
):
    fixture = _fixture(tmp_path, repo_root)
    fixture["authorization_path"].write_bytes(
        raw_mutation(fixture["authorization_raw"])
    )
    with pytest.raises(DispatchAuthorizationError):
        _validate(fixture, scan_history=False)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.__setitem__("approved_by", "Not-Karl"),
        lambda value: value.__setitem__("approved_at", "2026-07-20T12:30:00"),
        lambda value: value.pop("approved_at"),
        lambda value: value.__setitem__("authorization_scope", "other"),
        lambda value: value.__setitem__("approval_statement", "approve"),
        lambda value: value.__setitem__("unexpected", True),
        lambda value: value["authority_flags"].__setitem__(
            "authorizes_result_population", True
        ),
    ],
)
def test_actor_time_scope_statement_extra_property_and_authority_fail(
    tmp_path, repo_root, mutation
):
    fixture = _fixture(tmp_path, repo_root)
    mutation(fixture["authorization"])
    _resign(fixture)
    with pytest.raises(DispatchAuthorizationError):
        _validate(fixture, scan_history=False)


def test_expected_whole_hash_and_length_mismatch_fail(tmp_path, repo_root):
    fixture = _fixture(tmp_path, repo_root)
    with pytest.raises(DispatchAuthorizationError, match="expected whole-file"):
        _validate(
            fixture,
            expected_whole_file_sha256="sha256:" + "0" * 64,
            scan_history=False,
        )
    with pytest.raises(DispatchAuthorizationError, match="expected byte length"):
        _validate(
            fixture,
            expected_byte_length=len(fixture["authorization_raw"]) + 1,
            scan_history=False,
        )


def test_core_hash_and_top_level_core_flags_mismatch_fail(tmp_path, repo_root):
    fixture = _fixture(tmp_path, repo_root)
    fixture["authorization"]["authorization_core_sha256"] = "sha256:" + "0" * 64
    fixture["authorization_path"].write_bytes(
        serialize_dispatch_authorization(fixture["authorization"])
    )
    with pytest.raises(DispatchAuthorizationError, match="core SHA-256"):
        _validate(fixture, require_audit=False, scan_history=False)

    fixture = _fixture(tmp_path / "flags", repo_root)
    fixture["authorization"]["authorization_core"]["authority_flags"][
        "authorizes_notifications"
    ] = True
    fixture["authorization"]["authorization_core_sha256"] = (
        authorization_core_sha256(
            fixture["authorization"]["authorization_core"]
        )
    )
    fixture["authorization_path"].write_bytes(
        serialize_dispatch_authorization(fixture["authorization"])
    )
    with pytest.raises(DispatchAuthorizationError):
        _validate(fixture, require_audit=False, scan_history=False)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.__setitem__("authorization_id", "KDAUTH-20260720-BAD"),
        lambda value: value.__setitem__(
            "authorization_artifact_target_path",
            "research/queue/dispatch_authorizations/KDAUTH-OTHER-R2-9001.dispatch_authorization.json",
        ),
        lambda value: value["authorization_core"]["queue_binding"].__setitem__(
            "path", "../queue.json"
        ),
    ],
)
def test_malformed_id_path_binding_and_traversal_fail(
    tmp_path, repo_root, mutation
):
    fixture = _fixture(tmp_path, repo_root)
    mutation(fixture["authorization"])
    _resign(fixture)
    with pytest.raises(DispatchAuthorizationError):
        _validate(fixture, require_audit=False, scan_history=False)


@pytest.mark.parametrize("kind", ["hash", "length", "state"])
def test_queue_hash_length_and_state_drift_fail(tmp_path, repo_root, kind):
    fixture = _fixture(tmp_path, repo_root)
    queue = fixture["authorization"]["authorization_core"]["queue_binding"]
    if kind == "hash":
        queue["whole_file_sha256"] = "sha256:" + "0" * 64
    elif kind == "length":
        queue["byte_length"] += 1
    else:
        queue["required_state"] = "admitted_non_dispatched"
        queue_path = fixture["root"] / queue["path"]
        item = json.loads(queue_path.read_text())
        item["status"] = "dispatched"
        queue_path.write_bytes(_write_json(queue_path, item))
        queue["whole_file_sha256"] = _hash(queue_path.read_bytes())
        queue["byte_length"] = len(queue_path.read_bytes())
    _resign(fixture)
    with pytest.raises(DispatchAuthorizationError):
        _validate(fixture, require_audit=False, scan_history=False)


@pytest.mark.parametrize("kind", ["whole", "core", "relationship"])
def test_gate_q_whole_core_and_relationship_mismatch_fail(
    tmp_path, repo_root, kind
):
    fixture = _fixture(tmp_path, repo_root)
    core = fixture["authorization"]["authorization_core"]
    gate = core["queue_binding"]["gate_q"]
    if kind == "whole":
        gate["whole_file_sha256"] = "sha256:" + "0" * 64
    elif kind == "core":
        gate["core_sha256"] = "sha256:" + "0" * 64
    else:
        core["lineage"]["gate_q"]["approval_id"] = "GATE-Q-OTHER-9001"
    _resign(fixture)
    with pytest.raises(DispatchAuthorizationError):
        _validate(fixture, require_audit=False, scan_history=False)


@pytest.mark.parametrize(
    "section",
    [
        "dispatcher_packet",
        "strategy_spec",
        "external_content_readiness",
        "variant_planning_approval",
        "variant_manifest",
        "sweep_plan",
    ],
)
def test_packet_and_each_lineage_hash_mismatch_fail(
    tmp_path, repo_root, section
):
    fixture = _fixture(tmp_path, repo_root)
    core = fixture["authorization"]["authorization_core"]
    target = (
        core["dispatcher_packet"]
        if section == "dispatcher_packet"
        else core["lineage"][section]
    )
    target["whole_file_sha256"] = "sha256:" + "0" * 64
    _resign(fixture)
    with pytest.raises(DispatchAuthorizationError):
        _validate(fixture, require_audit=False, scan_history=False)


@pytest.mark.parametrize("kind", ["dispatch_path", "run_path"])
def test_dispatch_and_run_path_mismatch_fail(tmp_path, repo_root, kind):
    fixture = _fixture(tmp_path, repo_root)
    crossing = fixture["authorization"]["authorization_core"][
        "crossing_identities"
    ]
    if kind == "dispatch_path":
        crossing["dispatch_record_path"] = (
            "research/queue/dispatch_records/"
            "DSP-20260720-OTHER001.dispatch_record.json"
        )
    else:
        crossing["execution_event_stream_path"] = (
            "research/queue/execution_events/"
            "RUN-20260720-OTHER001.execution_events.jsonl"
        )
    _resign(fixture)
    with pytest.raises(DispatchAuthorizationError):
        _validate(fixture, require_audit=False, scan_history=False)


@pytest.mark.parametrize(
    "section",
    [
        "dataset",
        "dataset_identity",
        "dataset_partial",
        "dataset_validator",
        "funding",
        "runner",
        "runner_module",
    ],
)
def test_dataset_funding_and_runner_identity_mismatch_fail(
    tmp_path, repo_root, section
):
    fixture = _fixture(tmp_path, repo_root)
    core = fixture["authorization"]["authorization_core"]
    if section == "dataset":
        core["dataset"]["data_sha256"] = "sha256:" + "0" * 64
    elif section == "dataset_identity":
        core["dataset"]["validation_identity"] = "other-1d-validator"
    elif section == "dataset_partial":
        catalog_path = fixture["root"] / core["dataset"]["catalog_path"]
        catalog = json.loads(catalog_path.read_text())
        catalog["findings"]["open_or_incomplete_bar_count"] = 1
        catalog_raw = _write_json(catalog_path, catalog)
        core["dataset"]["catalog_sha256"] = _hash(catalog_raw)
        core["dataset"]["catalog_byte_length"] = len(catalog_raw)
    elif section == "dataset_validator":
        core["dataset"]["validator_sha256"] = "sha256:" + "0" * 64
    elif section == "funding":
        core["funding"]["funding_mode"] = "off"
    elif section == "runner":
        core["runner"]["version"] = "unknown-version"
    else:
        core["runner"]["module"] = "tools.other.offline_research"
    _resign(fixture)
    with pytest.raises(DispatchAuthorizationError):
        _validate(fixture, require_audit=False, scan_history=False)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda core: core["denominator"].__setitem__("planned", 5),
        lambda core: core["budget"].__setitem__("upper_bound", 5),
        lambda core: core["budget"].__setitem__("retry_allowance", 1),
        lambda core: core["execution_parameters"].__setitem__(
            "automatic_retry", True
        ),
        lambda core: core["output_targets"].__setitem__(
            "scratch_output_root", "research/result_populations/"
        ),
    ],
)
def test_denominator_budget_retry_and_output_mismatch_fail(
    tmp_path, repo_root, mutation
):
    fixture = _fixture(tmp_path, repo_root)
    mutation(fixture["authorization"]["authorization_core"])
    _resign(fixture)
    with pytest.raises(DispatchAuthorizationError):
        _validate(fixture, require_audit=False, scan_history=False)


@pytest.mark.parametrize(
    "scratch_output_root",
    [
        "scratch/../research/result_populations/",
        "scratch/foo/../../research/queue/",
        "scratch/./foo/",
        "scratch//foo/",
        "scratch\\foo\\",
        "/scratch/foo/",
        "C:/scratch/foo/",
        "scratch/foo",
        "scratch/",
    ],
)
def test_scratch_output_root_lexical_escape_fails(
    tmp_path, repo_root, scratch_output_root
):
    fixture = _fixture(tmp_path, repo_root)
    fixture["authorization"]["authorization_core"]["output_targets"][
        "scratch_output_root"
    ] = scratch_output_root
    _resign(fixture)
    with pytest.raises(DispatchAuthorizationError):
        _validate(fixture, require_audit=False, scan_history=False)


def test_valid_nested_scratch_output_root_is_read_only(tmp_path, repo_root):
    fixture = _fixture(tmp_path, repo_root)
    nested = "scratch/FIXTURE-RUN/nested.output/"
    target = fixture["root"] / nested
    fixture["authorization"]["authorization_core"]["output_targets"][
        "scratch_output_root"
    ] = nested
    _resign(fixture)
    assert not target.exists()
    assert _validate(fixture, require_audit=False, scan_history=False)["valid"]
    assert not target.exists()


def test_existing_file_cannot_be_a_scratch_output_root(tmp_path, repo_root):
    fixture = _fixture(tmp_path, repo_root)
    target = fixture["root"] / "scratch/FIXTURE-FILE"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("not a directory", encoding="utf-8")
    fixture["authorization"]["authorization_core"]["output_targets"][
        "scratch_output_root"
    ] = "scratch/FIXTURE-FILE/"
    _resign(fixture)
    with pytest.raises(DispatchAuthorizationError, match="resolve to a directory"):
        _validate(fixture, require_audit=False, scan_history=False)


def test_scratch_output_symlink_or_junction_escape_fails_closed(
    tmp_path, repo_root
):
    fixture = _fixture(tmp_path, repo_root)
    scratch = fixture["root"] / "scratch"
    scratch.mkdir(exist_ok=True)
    outside = tmp_path / "outside-scratch"
    outside.mkdir()
    escape = scratch / "escape"
    try:
        escape.symlink_to(outside, target_is_directory=True)
    except OSError:
        if os.name != "nt":
            pytest.skip("directory symlinks are unavailable in this environment")
        created = subprocess.run(
            ["cmd.exe", "/c", "mklink", "/J", str(escape), str(outside)],
            text=True,
            capture_output=True,
            check=False,
        )
        if created.returncode != 0:
            pytest.skip("directory symlinks and junctions are unavailable")
    fixture["authorization"]["authorization_core"]["output_targets"][
        "scratch_output_root"
    ] = "scratch/escape/nested/"
    _resign(fixture)
    with pytest.raises(DispatchAuthorizationError, match="symlinked|escapes"):
        _validate(fixture, require_audit=False, scan_history=False)


def _terminal_event(fixture: dict, event_type: str) -> dict:
    created = fixture["created"]
    payloads = {
        "authorization_revoked": {
            "event_kind": "authorization_revoked",
            "reason": "fixture revocation",
        },
        "authorization_superseded": {
            "event_kind": "authorization_superseded",
            "new_authorization_id": "KDAUTH-TEST-R2-9002",
            "new_authorization_path": (
                "research/queue/dispatch_authorizations/"
                "KDAUTH-TEST-R2-9002.dispatch_authorization.json"
            ),
            "reason": "fixture supersession",
        },
        "authorization_consumed": {
            "event_kind": "authorization_consumed",
            "consumer_tool": "fixture-dispatch-writer-v1",
            "dispatch_record_path": created["authorization_path"].replace(
                "dispatch_authorizations/KDAUTH-TEST-R2-9001.dispatch_authorization",
                "dispatch_records/DSP-20260720-TEST9001.dispatch_record",
            ),
            "consumption_is_permanent": True,
        },
    }
    event = copy.deepcopy(created)
    event["event_id"] = (
        f"KDAUTH-EVENT-{created['authorization_id']}-000002"
    )
    event["sequence_number"] = 2
    event["event_type"] = event_type
    event["occurred_at"] = "2026-07-20T12:32:00-05:00"
    event["event_payload"] = payloads[event_type]
    return event


@pytest.mark.parametrize(
    "event_type",
    [
        "authorization_revoked",
        "authorization_superseded",
        "authorization_consumed",
    ],
)
def test_revoked_superseded_and_consumed_authorizations_fail(
    tmp_path, repo_root, event_type
):
    fixture = _fixture(tmp_path, repo_root)
    terminal = _terminal_event(fixture, event_type)
    fixture["audit_path"].write_bytes(
        repo_canonical_json_v1(fixture["created"])
        + b"\n"
        + repo_canonical_json_v1(terminal)
        + b"\n"
    )
    with pytest.raises(DispatchAuthorizationError, match="not consumable"):
        _validate(fixture, scan_history=False)


@pytest.mark.parametrize("kind", ["partial", "wrong_first", "duplicate_created"])
def test_audit_partial_tail_and_ordering_fail(tmp_path, repo_root, kind):
    fixture = _fixture(tmp_path, repo_root)
    if kind == "partial":
        fixture["audit_path"].write_bytes(b'{"partial":true}')
    elif kind == "wrong_first":
        event = _terminal_event(fixture, "authorization_revoked")
        event["sequence_number"] = 1
        event["event_id"] = (
            f"KDAUTH-EVENT-{event['authorization_id']}-000001"
        )
        fixture["audit_path"].write_bytes(repo_canonical_json_v1(event) + b"\n")
    else:
        second = copy.deepcopy(fixture["created"])
        second["sequence_number"] = 2
        second["event_id"] = (
            f"KDAUTH-EVENT-{second['authorization_id']}-000002"
        )
        fixture["audit_path"].write_bytes(
            repo_canonical_json_v1(fixture["created"])
            + b"\n"
            + repo_canonical_json_v1(second)
            + b"\n"
        )
    with pytest.raises(DispatchAuthorizationError):
        _validate(fixture, scan_history=False)


def test_current_dispatch_reuse_fails(tmp_path, repo_root):
    fixture = _fixture(tmp_path, repo_root)
    core = fixture["authorization"]["authorization_core"]
    dispatch = {
        "dispatch_id": core["crossing_identities"]["dispatch_id"],
        "dispatch_record_path": core["crossing_identities"]["dispatch_record_path"],
        "queue_binding": {
            "queue_item_id": core["queue_binding"]["queue_item_id"]
        },
        "run_binding": {
            "run_id": core["crossing_identities"]["run_id"],
            "execution_event_stream_path": core["crossing_identities"][
                "execution_event_stream_path"
            ],
        },
        "dispatch_authorization": {
            "authorization_id": fixture["authorization"]["authorization_id"]
        },
    }
    _write_json(
        fixture["root"] / core["crossing_identities"]["dispatch_record_path"],
        dispatch,
    )
    with pytest.raises(DispatchAuthorizationError, match="already consumed"):
        _validate(fixture)


def test_other_authorization_cannot_reuse_queue_target(tmp_path, repo_root):
    fixture = _fixture(tmp_path, repo_root)
    other = copy.deepcopy(fixture["authorization"])
    other_id = "KDAUTH-TEST-R2-9002"
    other_path = (
        "research/queue/dispatch_authorizations/"
        f"{other_id}.dispatch_authorization.json"
    )
    other["authorization_id"] = other_id
    other["authorization_artifact_target_path"] = other_path
    crossing = other["authorization_core"]["crossing_identities"]
    crossing["dispatch_id"] = "DSP-20260720-TEST9002"
    crossing["run_id"] = "RUN-20260720-TEST9002"
    crossing["dispatch_record_path"] = (
        "research/queue/dispatch_records/"
        "DSP-20260720-TEST9002.dispatch_record.json"
    )
    crossing["execution_event_stream_path"] = (
        "research/queue/execution_events/"
        "RUN-20260720-TEST9002.execution_events.jsonl"
    )
    other["authorization_core"]["output_targets"][
        "execution_event_stream_path"
    ] = crossing["execution_event_stream_path"]
    other["authorization_core_sha256"] = authorization_core_sha256(
        other["authorization_core"]
    )
    (fixture["root"] / other_path).write_bytes(
        serialize_dispatch_authorization(other)
    )
    with pytest.raises(DispatchAuthorizationError, match="queue_item_id"):
        _validate(fixture)


def test_h004_id_requires_exact_h004_lineage_and_count(tmp_path, repo_root):
    fixture = _fixture(tmp_path, repo_root)
    authorization = fixture["authorization"]
    old_path = fixture["authorization_path"]
    authorization_id = "KDAUTH-H004-R2-9001"
    new_rel = (
        "research/queue/dispatch_authorizations/"
        f"{authorization_id}.dispatch_authorization.json"
    )
    authorization["authorization_id"] = authorization_id
    authorization["authorization_artifact_target_path"] = new_rel
    authorization["authorization_core_sha256"] = authorization_core_sha256(
        authorization["authorization_core"]
    )
    new_path = fixture["root"] / new_rel
    new_path.write_bytes(serialize_dispatch_authorization(authorization))
    old_path.unlink()
    fixture["authorization_path"] = new_path
    with pytest.raises(DispatchAuthorizationError, match="H-004"):
        _validate(fixture, require_audit=False, scan_history=False)


def test_deleted_dispatch_in_retained_history_still_consumes(
    tmp_path, repo_root
):
    fixture = _fixture(tmp_path, repo_root)
    core = fixture["authorization"]["authorization_core"]
    dispatch_path = (
        fixture["root"] / core["crossing_identities"]["dispatch_record_path"]
    )
    dispatch = {
        "dispatch_id": core["crossing_identities"]["dispatch_id"],
        "dispatch_record_path": core["crossing_identities"]["dispatch_record_path"],
        "queue_binding": {
            "queue_item_id": core["queue_binding"]["queue_item_id"]
        },
        "run_binding": {
            "run_id": core["crossing_identities"]["run_id"],
            "execution_event_stream_path": core["crossing_identities"][
                "execution_event_stream_path"
            ],
        },
        "dispatch_authorization": {
            "authorization_id": fixture["authorization"]["authorization_id"]
        },
    }
    _write_json(dispatch_path, dispatch)
    _commit(fixture["root"], "consume synthetic dispatch identity")
    dispatch_path.unlink()
    _commit(fixture["root"], "delete visible dispatch evidence")
    with pytest.raises(DispatchAuthorizationError, match="already consumed"):
        _validate(fixture)


def test_missing_git_history_fails_closed(tmp_path, repo_root):
    fixture = _fixture(tmp_path, repo_root)
    (fixture["root"] / ".git").rename(fixture["root"] / ".git-hidden")
    with pytest.raises(DispatchAuthorizationError, match="history is unavailable"):
        _validate(fixture)


def test_symlinked_reference_fails_closed(tmp_path, repo_root):
    fixture = _fixture(tmp_path, repo_root)
    runner = fixture["authorization"]["authorization_core"]["runner"]
    source = fixture["root"] / runner["source_path"]
    real = source.with_name("real_runner.py")
    source.rename(real)
    try:
        source.symlink_to(real)
    except OSError:
        pytest.skip("symlinks are unavailable in this Windows environment")
    with pytest.raises(DispatchAuthorizationError, match="symlinked"):
        _validate(fixture, require_audit=False, scan_history=False)


def test_no_production_kdauth_audit_dispatch_or_execution_created(repo_root):
    approval_root = repo_root / validator.APPROVAL_ROOT
    audit_path = repo_root / validator.AUDIT_PATH
    dispatch_root = repo_root / validator.DISPATCH_ROOT
    execution_root = repo_root / validator.EXECUTION_ROOT
    assert not approval_root.exists() or not list(
        approval_root.glob("*.dispatch_authorization.json")
    )
    assert not audit_path.exists()
    assert not dispatch_root.exists() or not list(
        dispatch_root.glob("*.dispatch_record.json")
    )
    assert not execution_root.exists() or not list(
        execution_root.glob("*.execution_events.jsonl")
    )
