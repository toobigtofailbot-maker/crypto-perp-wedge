"""Verify current scratch bytes and identities before durable trial commitment."""

from __future__ import annotations

import json
import stat
from pathlib import Path

from tools.lab_pipeline import runner_adapter as adapter
from tools.registry.validate_result_populations import validate_result_populations
from tools.registry.validate_walkforward_fold_manifest import validate_walkforward_fold_manifests
from tools.registry.validate_walkforward_run_report import validate_walkforward_run_reports
from tools.research_runner import run_offline_sweep as runner
from tools.research_search.contract import sha256_payload

from .mapper import ORIGINAL_SCHEMA, SOURCE_SPEC, committed_json, file_hash


class EvidenceBlocked(ValueError):
    """Evidence is missing, changed, ambiguous or insufficient; never zero-fill."""


def safe_file(root: Path, relative: str, *, scratch=False):
    if not isinstance(relative, str) or "\\" in relative:
        raise EvidenceBlocked("safe repo-relative file required")
    parts = relative.split("/")
    if any(p in {"", ".", ".."} for p in parts) or Path(relative).is_absolute() or ":" in parts[0]:
        raise EvidenceBlocked("unsafe evidence path")
    if scratch and parts[0] != "scratch":
        raise EvidenceBlocked("noncanonical scratch evidence required")
    cursor = root.resolve(strict=True)
    for part in parts:
        cursor /= part
        attrs = cursor.lstat()
        if stat.S_ISLNK(attrs.st_mode) or getattr(attrs, "st_file_attributes", 0) & 0x400:
            raise EvidenceBlocked("evidence indirection denied")
    if not cursor.is_file():
        raise EvidenceBlocked("ordinary evidence file required")
    return cursor


def bound_json(root, binding, *, scratch=True):
    path = safe_file(root, binding["path"], scratch=scratch)
    if file_hash(path) != binding["sha256"]:
        raise EvidenceBlocked("blocked_unverifiable_evidence: scratch bytes changed")
    return path, json.loads(path.read_text(encoding="utf-8"))


def verify_population(root, prepared, summary_binding, contract):
    """Validate unchanged existing runner output, parity, source and every variant."""
    summary_path, summary = bound_json(root, summary_binding)
    if (
        summary.get("adapter_status") != "completed"
        or summary.get("full_denominator_preserved") is not True
    ):
        raise EvidenceBlocked("completed full-population runner summary required")
    bindings = summary["source_bindings"]
    execution = bindings.get("execution")
    if not execution or execution.get("mode") != "canonical_15m_d4_provenance":
        raise EvidenceBlocked("real 15m D4 runner evidence required")
    if (
        prepared["contract_hash"] != contract.contract_hash
        or prepared["repo_sha"] != contract.repo_sha
    ):
        raise EvidenceBlocked("prepared contract identity mismatch")
    paths = [safe_file(root, prepared["paths"][k], scratch=True) for k in ("spec", "vm", "sweep")]
    for k, path in zip(("spec", "vm", "sweep"), paths):
        if file_hash(path) != prepared["hashes"][k]:
            raise EvidenceBlocked("prepared input bytes changed")
    spec, vm, sweep = runner._validate_parent_inputs(*paths)
    original = prepared.get("schema_version") == ORIGINAL_SCHEMA
    source_path = prepared["source_paths"]["spec"] if original else SOURCE_SPEC
    source = committed_json(root, source_path, contract.repo_sha, original=original)
    if file_hash(root / source_path) != contract.strategy_spec_hash:
        raise EvidenceBlocked("committed source spec mismatch")
    for field in (
        "entry_logic",
        "exit_logic",
        "filters",
        "instruments",
        "timeframe_and_data",
        "free_parameters",
        "constraints",
        "risk_model",
        "backtest_realism_assumptions",
    ):
        if sha256_payload(source[field]) != sha256_payload(spec[field]):
            raise EvidenceBlocked("prepared strategy semantics differ from frozen source")
    if original:
        from .original_source import ROUTE_PREFIX, OriginalBlocked, verify

        try:
            proof = verify(root, contract, prepared.get("original_evidence"))
        except OriginalBlocked as exc:
            raise EvidenceBlocked(str(exc)) from None
        if proof["original_parent"] != prepared["original_parent"]:
            raise EvidenceBlocked("BLOCKED_ORIGINAL_PARENT_SUBSTITUTION")
        source_ref = [r for r in spec["provenance"]["source_refs"] if r.startswith(ROUTE_PREFIX)]
        expected_route = {"schema_version": "cpw_original_runner_route_v1",
                          "source_proof_sha256": prepared["source_proof_sha256"],
                          "contract_hash": contract.contract_hash,
                          "original_parent_sha256": proof["original_parent"]["original_parent_sha256"]}
        if len(source_ref) != 1 or not source_ref[0].endswith("#" + prepared["source_proof_sha256"]) or bindings.get("original_route") != expected_route:
            raise EvidenceBlocked("BLOCKED_ORIGINAL_ROUTE_EVIDENCE")
        source_relative, source_sha = source_ref[0][len(ROUTE_PREFIX):].split("#")
        _, source_snapshot = bound_json(root, {"path": source_relative, "sha256": source_sha})
        if source_snapshot != {"evidence": prepared["original_evidence"], "contract_hash": contract.contract_hash,
                              "parent": prepared["original_parent"]}:
            raise EvidenceBlocked("BLOCKED_ORIGINAL_SOURCE_SNAPSHOT")
        # No historical re-read outside custody: bind to the durable custody use receipt instead.
        from tools.research_autonomy.envelope import content_hash

        receipt = bindings.get("custody_receipt") or {}
        settings = {
            "mode": "canonical_15m_d4_provenance",
            "canonical_15m": True,
            "deterministic_seed": contract.seed,
            "funding_cost_mode": "off",
            "sizing_mode": runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
            "target_leverage": 1.0,
            "timeframe": "15m",
        }
        if (
            receipt.get("execution_sha256") != content_hash(dict(execution))
            or receipt.get("approval_sha256") != bindings["execute_approval_sha256"]
            or any(execution.get(k) != v for k, v in settings.items())
        ):
            raise EvidenceBlocked("BLOCKED_NONHOLDOUT_CUSTODY: custody receipt/execution mismatch")
    else:
        expected_execution = adapter._execution_binding(
            canonical_15m=True,
            ohlcv_input_path=execution["ohlcv_input_path"],
            d4_catalog_slice_path=execution["d4_catalog_slice_path"],
            d2_import_report_path=execution["d2_import_report_path"],
            deterministic_seed=contract.seed,
        )
        if execution != expected_execution:
            raise EvidenceBlocked("execution settings/seed mismatch")
    approval_path = safe_file(root, bindings["execute_approval_path"])
    approval, approval_hash = adapter._require_execute_approval(
        approval_path=approval_path,
        prepared_strategy_spec_path=prepared["paths"]["spec"],
        prepared_variant_manifest_path=prepared["paths"]["vm"],
        prepared_sweep_plan_path=prepared["paths"]["sweep"],
        bridge_preparation_run_id=prepared["preparation_id"],
        product_pipeline_run_id=prepared["pipeline_id"],
        output_root=bindings["product_output_root"],
        execution=execution,
    )
    if approval_hash != bindings["execute_approval_sha256"]:
        raise EvidenceBlocked("runner approval bytes changed")
    if original:
        if approval.get("original_route") != expected_route:
            raise EvidenceBlocked("BLOCKED_ORIGINAL_ROUTE_APPROVAL")
        identity = execution["data_slice_identity"]
    else:
        adapter._validate_real_execution(execution)
        catalog = json.loads(safe_file(root, execution["d4_catalog_slice_path"]).read_text())
        identity = catalog["slice_identity"]["data_slice_identity"]
    if identity != contract.data_identity:
        raise EvidenceBlocked("frozen development data identity mismatch")
    outputs = summary["runner_outputs"]
    result_path = safe_file(root, outputs["adapter_result_population_path"], scratch=True)
    direct_path = safe_file(root, outputs["direct_result_population_path"], scratch=True)
    for path, key in (
        (result_path, "adapter_result_population_sha256"),
        (direct_path, "direct_result_population_sha256"),
    ):
        if file_hash(path) != outputs[key]:
            raise EvidenceBlocked("runner scratch output bytes changed")
        errors = validate_result_populations(
            result_populations_dir=path.parent,
            strategy_specs_dir=paths[0].parent,
            variant_manifests_dir=paths[1].parent,
            sweep_plans_dir=paths[2].parent,
        )
        if errors:
            raise EvidenceBlocked("invalid Result Population: " + "; ".join(errors))
    parity = adapter._reconcile_outputs(result_path, direct_path)
    parity["execution_binding"] = dict(execution)
    if summary["direct_runner_reconciliation"] != parity:
        raise EvidenceBlocked("parity evidence mismatch")
    result = json.loads(result_path.read_text())
    adapter._assert_real_population_inputs(result, execution)
    adapter._assert_real_population_inputs(json.loads(direct_path.read_text()), execution)
    for population in (result, json.loads(direct_path.read_text())):
        adapter._assert_result_population_preserves_budget(
            result_population=population,
            approved_budget=summary["approved_sweep_budget"],
            expected_variant_ids=adapter._expected_variant_ids_from_sweep(
                prepared["paths"]["sweep"]
            ),
        )
    if (
        summary["denominator_counts"] != adapter._status_counts(result)
        or summary["largest_tested_denominator"] != len(prepared["mapping"])
        or summary["budget_exceeded"] is not False
        or summary["winner_narrowing"] is not False
    ):
        raise EvidenceBlocked("runner summary denominator mismatch")
    expected = {m["variant_id"]: m for m in prepared["mapping"]}
    assigned = {r["variant_id"]: r for r in vm["variant_assignments"]}
    rows = result["variant_result_rows"]
    if (
        len(rows) != len(expected)
        or len(assigned) != len(expected)
        or {r["variant_id"] for r in rows} != set(expected)
        or set(sweep["test_selection"]["selected_variant_ids"]) != set(expected)
    ):
        raise EvidenceBlocked("full population/denominator mismatch")
    for row in rows:
        mapping = expected[row["variant_id"]]
        if (
            mapping["params_fingerprint"] != sha256_payload(mapping["parameter_values"])
            or row["assignment_hash"] != mapping["params_fingerprint"]
            or assigned[row["variant_id"]]["parameter_values"] != mapping["parameter_values"]
        ):
            raise EvidenceBlocked("variant parameter identity mismatch")
        coverage = row["data_coverage"]
        if (
            coverage["data_slice_identity"] != contract.data_identity
            or coverage["timeframe"] != "15m"
        ):
            raise EvidenceBlocked("result row data identity mismatch")
    return result_path, result, summary, approval_hash


def verify_fold_manifest(root, binding, prepared, contract, *, purge_bars, embargo_bars):
    """Require explicit full-population windows and enforce actual purged boundaries."""
    path, manifest = bound_json(root, binding)
    errors = validate_walkforward_fold_manifests(explicit_paths=[path])
    if errors:
        raise EvidenceBlocked("invalid fold manifest: " + "; ".join(errors))
    if (
        manifest["timeframe"] != "15m"
        or manifest["data_slice_id"] != contract.data_identity
        or manifest["source_commit"] != contract.repo_sha
        or manifest["selection_rule"]["rule_type"] != "carry_full_population"
    ):
        raise EvidenceBlocked("fold frozen source/data/population mismatch")
    import pandas as pd

    if (
        type(purge_bars) is not int
        or type(embargo_bars) is not int
        or purge_bars < 1
        or embargo_bars < 1
    ):
        raise EvidenceBlocked("explicit positive purge and embargo required")
    parents = [
        json.loads(safe_file(root, prepared["paths"][k], scratch=True).read_text())
        for k in ("spec", "vm", "sweep")
    ]
    for key, value in zip(("strategy_spec_id", "variant_manifest_id", "sweep_plan_id"), parents):
        if manifest[key] != value[key]:
            raise EvidenceBlocked("fold prepared lineage mismatch")
    warmup = max(max(m["parameter_values"].values()) for m in prepared["mapping"])
    previous_end = None
    development_start, development_end = [
        pd.Timestamp(value) for value in contract.split_protocol.development_window.split("/")
    ]
    for fold in sorted(manifest["folds"], key=lambda f: f["fold_order"]):
        start, end, oos_start, oos_end = [
            pd.Timestamp(fold[key])
            for key in (
                "selection_window_start_utc",
                "selection_window_end_utc",
                "evaluation_window_start_utc",
                "evaluation_window_end_utc",
            )
        ]
        if (
            any(
                v.tzinfo is None or v.utcoffset().total_seconds() != 0
                for v in (start, end, oos_start, oos_end)
            )
            or start < development_start
            or oos_end > development_end
            or fold["purge"] != {"mode": "bars", "bars": purge_bars, "duration": None}
            or fold["embargo"] != {"mode": "bars", "bars": embargo_bars, "duration": None}
            or end + pd.Timedelta(minutes=15 * purge_bars) > oos_start
            or (
                previous_end is not None
                and start < previous_end + pd.Timedelta(minutes=15 * embargo_bars)
            )
            or min((end - start).total_seconds(), (oos_end - oos_start).total_seconds())
            <= 900 * (warmup + 2)
            or fold["declared_variant_count"] != len(prepared["mapping"])
        ):
            raise EvidenceBlocked("overlap, insufficient purge/embargo/warmup or denominator")
        previous_end = oos_end
    return path, manifest


def verify_fold_report(root, binding, manifest_binding, prepared, contract):
    path, report = bound_json(root, binding)
    errors = validate_walkforward_run_reports(explicit_paths=[path])
    if errors:
        raise EvidenceBlocked("invalid fold report: " + "; ".join(errors))
    _, manifest = bound_json(root, manifest_binding)
    if (
        report["source_commit"] != contract.repo_sha
        or report["walkforward_manifest_ref"] != manifest_binding["path"]
        or report["data_slice"]["data_slice_id"] != contract.data_identity
        or len(report["fold_results"]) != len(manifest["folds"])
    ):
        raise EvidenceBlocked("fold report source/manifest/data mismatch")
    expected = {m["variant_id"] for m in prepared["mapping"]}
    declared = {f["fold_id"]: f for f in manifest["folds"]}
    if {f["fold_id"] for f in report["fold_results"]} != set(declared):
        raise EvidenceBlocked("missing or substituted fold")
    for fold in report["fold_results"]:
        source = declared[fold["fold_id"]]
        if (
            fold["status"] != "successful"
            or fold["variant_count_posture"]["successful"] != len(expected)
            or len(fold["variant_results"]) != len(expected)
            or {r["variant_id"] for r in fold["variant_results"]} != expected
            or fold["selection_window"]
            != {
                "start_utc": source["selection_window_start_utc"],
                "end_utc": source["selection_window_end_utc"],
            }
            or fold["evaluation_window"]
            != {
                "start_utc": source["evaluation_window_start_utc"],
                "end_utc": source["evaluation_window_end_utc"],
            }
        ):
            raise EvidenceBlocked("partial, unavailable or different fold evidence")
    return report


def verify_commitment(root, payload, contract):
    """No caller-supplied verified flag: independently re-resolve evidence bytes."""
    from tools.research_autonomy.m1_source import M1_MAPPING, M1_VERSION

    if getattr(contract, "data_version", None) == M1_VERSION:
        raise EvidenceBlocked("M1 TEST_ONLY cannot create a terminal scientific commitment")
    required = {
        "campaign_id",
        "search_id",
        "contract_hash",
        "proposal_id",
        "scientific_trial_id",
        "variant_id",
        "params_fingerprint",
        "attempt_number",
        "idempotency_id",
        "classification",
        "approval_id",
        "approval_sha256",
        "prepared_hashes",
        "runner_result_sha256",
        "authority_lineage_version",
        "authority_lineage_sha256",
        "mapping_binding",
        "summary_binding",
        "fold_binding",
        "fold_manifest_binding",
        "fold_sha256",
        "robustness_binding",
        "robustness_sha256",
        "purge_bars",
        "embargo_bars",
    }
    if set(payload) != required:
        raise EvidenceBlocked("closed trial commitment metadata required; no metric payloads")
    _, prepared = bound_json(root, payload["mapping_binding"])
    if prepared.get("schema_version") == M1_MAPPING:
        raise EvidenceBlocked("M1 TEST_ONLY cannot create a terminal scientific commitment")
    if prepared.get("schema_version") == ORIGINAL_SCHEMA:
        from tools.research_autonomy.store import ResearchAuthorityStore, _terminal_evidence

        transaction = _terminal_evidence.get()
        if (transaction is None or type(transaction[0]) is not ResearchAuthorityStore
                or transaction[2] != Path(root).resolve() or transaction[3] != contract):
            raise EvidenceBlocked("BLOCKED_ATOMIC_CUSTODY_COMMIT: active native terminal transaction required")
    result_path, result, summary, approval_hash = verify_population(
        root, prepared, payload["summary_binding"], contract
    )
    if prepared.get("schema_version") == ORIGINAL_SCHEMA:
        from tools.research_autonomy.historical_source_gate import HistoricalSourceGate

        request = HistoricalSourceGate(transaction[0], root).verify_commit(
            summary["source_bindings"]["custody_receipt"], _transaction=transaction)
        transaction[0]._search_active(transaction[1], contract)
        if (request.search_id != contract.search_id or request.campaign_id != contract.campaign_id
                or request.contract_hash != contract.contract_hash
                or request.original_parent_sha256 != prepared["original_parent"]["original_parent_sha256"]):
            raise EvidenceBlocked("BLOCKED_ORIGINAL_CUSTODY_STUDY_BINDING")
    mapping = [
        m for m in prepared["mapping"] if m["scientific_trial_id"] == payload["scientific_trial_id"]
    ]
    if len(mapping) != 1:
        raise EvidenceBlocked("exact scientific mapping required")
    m = mapping[0]
    for key in (
        "campaign_id",
        "search_id",
        "contract_hash",
        "proposal_id",
        "variant_id",
        "params_fingerprint",
    ):
        if payload[key] != m[key]:
            raise EvidenceBlocked("commitment mapping substitution")
    rows = [r for r in result["variant_result_rows"] if r["variant_id"] == m["variant_id"]]
    classification = (
        "PERFORMANCE_RESULT"
        if rows[0]["outcome_category"] in {"successful", "failed"}
        else "SOFTWARE_FAILED"
        if rows[0]["outcome_category"] == "errored"
        else None
    )
    if classification is None or payload["classification"] != classification:
        raise EvidenceBlocked("blocked_unverifiable_evidence: missing/ambiguous terminal outcome")
    if (
        payload["approval_sha256"] != approval_hash
        or payload["approval_id"] != summary["runner_adapter_run_id"]
        or payload["prepared_hashes"] != prepared["hashes"]
        or payload["runner_result_sha256"] != file_hash(result_path)
    ):
        raise EvidenceBlocked("commitment approval/input/output hashes mismatch")
    if payload["fold_binding"]:
        if payload["fold_sha256"] != payload["fold_binding"]["sha256"]:
            raise EvidenceBlocked("fold hash mismatch")
        verify_fold_manifest(
            root,
            payload["fold_manifest_binding"],
            prepared,
            contract,
            purge_bars=payload["purge_bars"],
            embargo_bars=payload["embargo_bars"],
        )
        verify_fold_report(
            root, payload["fold_binding"], payload["fold_manifest_binding"], prepared, contract
        )
    elif payload["fold_sha256"] is not None:
        raise EvidenceBlocked("missing fold artifact")
    if payload["robustness_binding"]:
        _, robustness = bound_json(root, payload["robustness_binding"])
        if (
            payload["robustness_sha256"] != payload["robustness_binding"]["sha256"]
            or robustness["seed"] != contract.seed
            or robustness["fixture"]["checksum"] != payload["runner_result_sha256"]
        ):
            raise EvidenceBlocked("advisory MC input/seed binding mismatch")
        from tools.robustness.seeded_advisory_mc import build_report

        recomputed, _ = build_report(result_population_path=result_path, seed=contract.seed)
        if sha256_payload(recomputed) != sha256_payload(robustness):
            raise EvidenceBlocked(
                "advisory computation differs from existing seeded implementation"
            )
    elif payload["robustness_sha256"] is not None:
        raise EvidenceBlocked("missing advisory artifact")
    return prepared, m, rows[0]


def load_m1_fixture_preparation(root, prepared, contract, request):
    """Revalidate the exact prepared artifact chain before a TEST_ONLY reader use."""
    from tools.research_autonomy.m1_source import M1_MAPPING, M1_ROOT, M1_VERSION

    source = request.source
    if (contract.data_version != M1_VERSION
            or prepared.get("schema_version") != M1_MAPPING
            or (prepared["repo_sha"], prepared["contract_hash"], prepared["m1_source"])
            != (contract.repo_sha, contract.contract_hash, source.model_dump(mode="json"))
            or request.contract_hash != contract.contract_hash
            or request.data_identity != contract.data_identity):
        raise EvidenceBlocked("M1 fixture mapping/source substitution")
    names = ("spec", "vm", "sweep")
    if any(not prepared["paths"][key].startswith(M1_ROOT) for key in names):
        raise EvidenceBlocked("M1 prepared paths must remain in TEST_ONLY scratch")
    paths = [safe_file(root, prepared["paths"][key], scratch=True) for key in names]
    if any(file_hash(path) != prepared["hashes"][key] for key, path in zip(names, paths)):
        raise EvidenceBlocked("M1 prepared input hash mismatch")
    spec, vm, sweep = runner._validate_parent_inputs(*paths)
    if any(file_hash(path) != prepared["hashes"][key] for key, path in zip(names, paths)):
        raise EvidenceBlocked("M1 prepared inputs changed during validation")
    source.require_spec(spec)
    canonical_path = f"research/strategy_specs/{contract.strategy_spec_id}.strategy_spec.json"
    original = committed_json(root, canonical_path, contract.repo_sha, original=True)
    if file_hash(root / canonical_path) != contract.strategy_spec_hash or any(
        original[field] != spec[field] for field in (
            "entry_logic", "exit_logic", "filters", "instruments", "timeframe_and_data",
            "free_parameters", "constraints", "risk_model", "backtest_realism_assumptions",
        )
    ):
        raise EvidenceBlocked("M1 prepared strategy semantics substitution")
    return spec, vm, sweep


def verify_m1_fixture_population(gate, contract, prepared, report, *, record=False):
    """Recheck native custody and the complete in-memory denominator, without a write."""
    from tools.research_autonomy.envelope import content_hash
    from tools.research_autonomy.historical_source_gate import M1Request

    receipt = report["custody_receipt"]
    request = gate.verify_commit(receipt)
    if (type(request) is not M1Request or report["mode"] != "TEST_ONLY"
            or report["not_authority"] is not True or report["real_scientific_trials"] != 0
            or report["schema_version"] != "cpw_m1_fixture_observation_v1"):
        raise EvidenceBlocked("M1 TEST_ONLY reader receipt required")
    execution = request.execution_binding(mapping_sha256=content_hash(prepared), seed=contract.seed)
    if (request.contract_hash != contract.contract_hash
            or report["execution"] != execution
            or receipt["execution_sha256"] != content_hash(execution)
            or receipt["approval_sha256"] != content_hash({"TEST_ONLY": execution["mapping_sha256"]})):
        raise EvidenceBlocked("M1 reader execution binding mismatch")
    population = report["population"]
    runner._validate_in_memory_payload(population)
    spec, vm, sweep = load_m1_fixture_preparation(gate.root, prepared, contract, request)
    if population["lineage"]["parent_hash_chain"] != {
        "strategy_spec_hash": runner._sha256_prefixed(spec),
        "variant_manifest_hash": vm["manifest_hash_pinning"]["manifest_hash"],
        "sweep_plan_identity_hash": runner._sha256_prefixed(sweep),
        "input_identity_hash": population["input_identity_hash"]["hash"],
    }:
        raise EvidenceBlocked("M1 population parent hash mismatch")
    expected = {row["variant_id"]: row for row in prepared["mapping"]}
    rows = population["variant_result_rows"]
    if (len(rows) != len(expected) or len(expected) != prepared["scientific_denominator"]
            or len({row["scientific_trial_id"] for row in expected.values()}) != len(expected)
            or {row["variant_id"] for row in rows} != set(expected)
            or set(sweep["test_selection"]["selected_variant_ids"]) != set(expected)
            or len(vm["variant_assignments"]) != len(expected)
            or report["population_sha256"] != content_hash(population)
            or population["committed_denominator_snapshot"]["committed_denominator"] != len(expected)):
        raise EvidenceBlocked("M1 fixture population denominator mismatch")
    assignments = {row["variant_id"]: row["parameter_values"] for row in vm["variant_assignments"]}
    for row in rows:
        mapped = expected[row["variant_id"]]
        coverage = row["data_coverage"]
        if (mapped["contract_hash"] != contract.contract_hash
                or mapped["parameter_values"] != assignments.get(row["variant_id"])
                or sha256_payload(mapped["parameter_values"]) != mapped["params_fingerprint"]
                or row["assignment_hash"] != mapped["params_fingerprint"]
                or coverage["timeframe"] != request.timeframe
                or coverage["data_slice_identity"] != request.data_identity):
            raise EvidenceBlocked("M1 fixture population variant or source substitution")
    gate.m1_observation(receipt, content_hash(report), record=record)
    return len(expected)
