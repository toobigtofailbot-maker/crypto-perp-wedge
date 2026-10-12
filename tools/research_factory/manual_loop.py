"""Explicit call-only factory slice. Default OFF, no orchestration or next wave."""

from __future__ import annotations

import json
from pathlib import Path

from tools.lab_pipeline import runner_adapter as adapter
from tools.research_autonomy.contract_builder import contract_from_payload
from tools.research_autonomy.handoff import validate_handoff
from tools.robustness.seeded_advisory_mc import build_report
from tools.walkforward.run_walkforward_scratch import run_walkforward_scratch

from .evidence import (
    EvidenceBlocked,
    bound_json,
    safe_file,
    verify_fold_manifest,
    verify_fold_report,
    verify_population,
)
from .mapper import MappingBlocked, file_hash, prepare_wave, write_once


def _binding(root, path):
    return {"path": path.relative_to(root).as_posix(), "sha256": file_hash(path)}


def _report(prepared=None, *, status="research_blocked", reason=None, **evidence):
    report = {
        "schema_version": "research_factory_report_v1",
        "factory_enabled": False,
        "noncanonical": True,
        "disposition": status,
        "withholding_reasons": [reason] if reason else [],
        "prefect_operational_summary": "not_integrated",
        "candidate_authority": False,
        "canonical_authority": False,
        "runtime_authority": False,
        "capital_authority": False,
        "prepared": prepared,
        **evidence,
    }
    if status not in {
        "research_completed",
        "research_completed_no_edge",
        "research_failed",
        "research_terminated",
        "research_duplicate",
        "research_insufficient_evidence",
        "research_blocked",
    }:
        raise ValueError("unsupported bounded research disposition")
    # No NaN, no implied gate PASS, and no candidate/lifecycle verdict.
    if report["noncanonical"] is not True or any(
        report[key] is not False
        for key in (
            "factory_enabled",
            "candidate_authority",
            "canonical_authority",
            "runtime_authority",
            "capital_authority",
        )
    ):
        raise ValueError("non-authoritative default-OFF report required")
    if prepared and (
        len(prepared["mapping"]) != prepared["scientific_denominator"]
        or prepared["proposal_counts"]["accepted"] != prepared["scientific_denominator"]
    ):
        raise ValueError("report mapping denominator mismatch")
    json.dumps(report, allow_nan=False)
    return report


def manual_research_loop(
    *,
    store,
    handoff,
    repo_root: Path,
    preparation_root: Path,
    output_root: Path,
    created_at_utc: str,
    human_invocation: bool = False,
    execute_approval_path=None,
    ohlcv_input_path=None,
    d4_catalog_slice_path=None,
    d2_import_report_path=None,
    fold_manifest_binding=None,
    tool_context=None,
):
    """One human-triggered wave. Reconcile an interrupted run before any rerun."""
    if human_invocation is not True:
        return _report(reason="factory_default_OFF")
    root = repo_root.resolve(strict=True)
    handoff = validate_handoff(handoff)
    contract = contract_from_payload(handoff.frozen_contract.model_dump(mode="json"))
    # Durable records take precedence over active-workspace caches and a stale wave lineage.
    accepted = [
        r for r in handoff.proposal_records if r.status == "ACCEPTED_FOR_SCIENTIFIC_EXECUTION"
    ]
    recovered = [store.load_trial_result(r.scientific_trial_id, repo_root=root) for r in accepted]
    if any(recovered):
        if not all(recovered):
            return _report(
                reason="investigate_partial_terminal_commitment",
                terminal_commitments=[r["audit_event_id"] for r in recovered if r],
            )
        payloads = [json.loads(row["evidence_payload"]) for row in recovered]
        complete = all(
            payload["fold_binding"] and payload["robustness_binding"] for payload in payloads
        )
        failed = any(row["classification"] == "SOFTWARE_FAILED" for row in recovered)
        return _report(
            status="research_failed"
            if failed
            else "research_completed"
            if complete
            else "research_insufficient_evidence",
            reason="withheld_missing_walkforward_oos_inputs: existing evaluator requires candidate-review input; no synthetic candidate",
            terminal_commitments=[r["audit_event_id"] for r in recovered],
            recovered=True,
            runner_calls=0,
            scientific_denominator=len(recovered),
            numeric_proposer_resumption=False,
        )
    try:
        prepared = prepare_wave(
            store=store,
            handoff=handoff,
            contract=contract,
            repo_root=root,
            output_root=preparation_root,
            created_at_utc=created_at_utc,
        )
    except MappingBlocked as exc:
        return _report(reason=str(exc), runner_calls=0)
    namespace = (root / prepared["paths"]["spec"]).parent
    mapping_path = namespace / "mapping.json"
    checkpoint_path = namespace / "execution_checkpoint.json"
    if checkpoint_path.exists():
        checkpoint = json.loads(
            safe_file(root, checkpoint_path.relative_to(root).as_posix(), scratch=True).read_text()
        )
        if checkpoint["mapping_sha256"] != file_hash(mapping_path):
            raise EvidenceBlocked("checkpoint mapping bytes changed")
        if checkpoint.get("summary_binding"):
            return reconcile_manual_run(
                store=store, repo_root=root, checkpoint_path=checkpoint_path
            )
        return _report(prepared, reason="investigate_possible_physical_execution_before_rerun")
    route = dict(
        canonical_15m=True,
        ohlcv_input_path=ohlcv_input_path,
        d4_catalog_slice_path=d4_catalog_slice_path,
        d2_import_report_path=d2_import_report_path,
        deterministic_seed=contract.seed,
    )
    kwargs = dict(
        prepared_strategy_spec_path=prepared["paths"]["spec"],
        prepared_variant_manifest_path=prepared["paths"]["vm"],
        prepared_sweep_plan_path=prepared["paths"]["sweep"],
        bridge_preparation_run_id=prepared["preparation_id"],
        product_pipeline_run_id=prepared["pipeline_id"],
        output_root=output_root,
        **route,
    )
    if execute_approval_path is None:
        request = {
            "prepared": prepared,
            "runner_settings": {
                "seed": contract.seed,
                "funding_cost_mode": "off",
                "sizing_mode": "dynamic_equity_target_leverage",
                "target_leverage": 1.0,
            },
            "approval_contract": "product_runner_execute_approval_v2",
            "approved": False,
            "preparation_approval": "not_applicable: mapper does not invoke formalizer bridge",
            "instruction": "Karl supplies an actual exact marker via local file; this request is not approval.",
        }
        if all(
            p is not None for p in (ohlcv_input_path, d4_catalog_slice_path, d2_import_report_path)
        ):
            template = adapter.approval_template(**kwargs)
            # Explicit unsigned request; cannot pass _require_execute_approval.
            template.update(
                approved_by=None, approval_timestamp_utc=None, authorizes_runner_execution=False
            )
            request["unsigned_marker_fields"] = template
        write_once(namespace / "operator_request.json", request)
        return _report(
            prepared,
            reason="blocked_approval",
            runner_calls=0,
            operator_request_path=(namespace / "operator_request.json")
            .relative_to(root)
            .as_posix(),
        )
    execution = adapter._execution_binding(**route)
    approval_rel = adapter._safe_repo_relative(execute_approval_path)
    approval, approval_hash = adapter._require_execute_approval(
        approval_path=root / approval_rel,
        prepared_strategy_spec_path=kwargs["prepared_strategy_spec_path"],
        prepared_variant_manifest_path=kwargs["prepared_variant_manifest_path"],
        prepared_sweep_plan_path=kwargs["prepared_sweep_plan_path"],
        bridge_preparation_run_id=prepared["preparation_id"],
        product_pipeline_run_id=prepared["pipeline_id"],
        output_root=adapter._validate_product_output_root(output_root),
        execution=execution,
    )
    adapter._validate_real_execution(execution)
    snapshot = store.load_snapshot(contract.campaign_id)
    # Recheck durable wave immediately before leaving a checkpoint for physical work.
    store.verify_recovery_binding(handoff, repo_root=root)
    if snapshot.holdout.state != "unexposed" or snapshot.holdout.contaminated:
        raise EvidenceBlocked("holdout not unexposed")
    protocol = store.load_scientific_protocol(contract.search_id)
    if fold_manifest_binding:
        verify_fold_manifest(
            root,
            fold_manifest_binding,
            prepared,
            contract,
            purge_bars=protocol["purge_bars"],
            embargo_bars=protocol["embargo_bars"],
        )
    checkpoint = {
        "mapping_sha256": file_hash(mapping_path),
        "mapping_binding": _binding(root, mapping_path),
        "contract": contract.to_dict(),
        "approval_sha256": approval_hash,
        "execution": execution,
        "state": "physical_execution_may_have_started",
        "summary_binding": None,
        "fold_manifest_binding": fold_manifest_binding,
        "purge_bars": protocol["purge_bars"],
        "embargo_bars": protocol["embargo_bars"],
        "fold_binding": None,
        "robustness_binding": None,
    }
    try:
        write_once(checkpoint_path, checkpoint, exclusive=True)
    except FileExistsError:
        return _report(
            prepared, reason="investigate_possible_physical_execution_before_rerun", runner_calls=0
        )
    # A failure from this point retains the checkpoint and every run artifact. No automatic retry.
    result = adapter.run_product_runner_adapter(
        **kwargs, execute_approval_path=execute_approval_path, tool_context=tool_context
    )
    summary_path = root / result.artifact_paths["runner_adapter_result"]
    checkpoint["summary_binding"] = _binding(root, summary_path)
    write_once(namespace / "runner_completed_checkpoint.json", checkpoint)
    result_path, population, summary, _ = verify_population(
        root, prepared, checkpoint["summary_binding"], contract
    )
    if fold_manifest_binding:
        fold_path, _ = bound_json(root, fold_manifest_binding)
        report_path, _ = run_walkforward_scratch(
            walkforward_manifest_path=fold_path,
            strategy_spec_path=root / prepared["paths"]["spec"],
            variant_manifest_path=root / prepared["paths"]["vm"],
            sweep_plan_path=root / prepared["paths"]["sweep"],
            ohlcv_input_path=root / execution["ohlcv_input_path"],
            d4_catalog_slice_path=root / execution["d4_catalog_slice_path"],
            d2_import_report_path=root / execution["d2_import_report_path"],
            output_dir=namespace / "folds",
            created_at_utc=created_at_utc,
            sizing_mode=execution["sizing_mode"],
            target_leverage=execution["target_leverage"],
        )
        checkpoint["fold_binding"] = _binding(root, report_path)
        verify_fold_report(
            root, checkpoint["fold_binding"], fold_manifest_binding, prepared, contract
        )
    robustness, _ = build_report(result_population_path=result_path, seed=contract.seed)
    robustness_path = write_once(namespace / "advisory_mc.json", robustness)
    checkpoint["robustness_binding"] = _binding(root, robustness_path)
    completed = write_once(namespace / "evidence_completed_checkpoint.json", checkpoint)
    return reconcile_manual_run(
        store=store, repo_root=root, checkpoint_path=completed, physical_run_completed=True
    )


def reconcile_manual_run(
    *, store, repo_root: Path, checkpoint_path: Path, physical_run_completed=False
):
    """Explicit recovery of already computed evidence, with zero runner calls."""
    root = repo_root.resolve(strict=True)
    path = safe_file(root, checkpoint_path.relative_to(root).as_posix(), scratch=True)
    checkpoint = json.loads(path.read_text())
    _, prepared = bound_json(root, checkpoint["mapping_binding"])
    if checkpoint["mapping_sha256"] != checkpoint["mapping_binding"]["sha256"]:
        raise EvidenceBlocked("checkpoint immutable mapping mismatch")
    contract = contract_from_payload(checkpoint["contract"])
    if not checkpoint["summary_binding"]:
        return _report(prepared, reason="investigate_possible_physical_execution_before_rerun")
    result_path, population, summary, approval_hash = verify_population(
        root, prepared, checkpoint["summary_binding"], contract
    )
    commitments = []
    for mapping in prepared["mapping"]:
        prior = store.load_trial_result(mapping["scientific_trial_id"], repo_root=root)
        if prior:
            commitments.append(prior["audit_event_id"])
            continue
        row = next(
            r for r in population["variant_result_rows"] if r["variant_id"] == mapping["variant_id"]
        )
        classification = (
            "PERFORMANCE_RESULT"
            if row["outcome_category"] in {"successful", "failed"}
            else "SOFTWARE_FAILED"
            if row["outcome_category"] == "errored"
            else None
        )
        if classification is None:
            return _report(
                prepared, reason="blocked_unverifiable_evidence", terminal_commitments=commitments
            )
        current = store.load_snapshot(contract.campaign_id)
        payload = {
            k: mapping[k]
            for k in (
                "campaign_id",
                "search_id",
                "contract_hash",
                "proposal_id",
                "scientific_trial_id",
                "variant_id",
                "params_fingerprint",
            )
        }
        payload.update(
            attempt_number=1,
            idempotency_id=summary["runner_adapter_run_id"] + "-" + mapping["variant_id"],
            classification=classification,
            approval_id=summary["runner_adapter_run_id"],
            approval_sha256=approval_hash,
            prepared_hashes=prepared["hashes"],
            runner_result_sha256=file_hash(result_path),
            authority_lineage_version=current.lineage_version,
            authority_lineage_sha256=current.lineage_sha256,
            mapping_binding=checkpoint["mapping_binding"],
            summary_binding=checkpoint["summary_binding"],
            fold_binding=checkpoint["fold_binding"],
            fold_manifest_binding=checkpoint["fold_manifest_binding"],
            fold_sha256=checkpoint["fold_binding"]["sha256"]
            if checkpoint["fold_binding"]
            else None,
            robustness_binding=checkpoint["robustness_binding"],
            robustness_sha256=checkpoint["robustness_binding"]["sha256"]
            if checkpoint["robustness_binding"]
            else None,
            purge_bars=checkpoint["purge_bars"],
            embargo_bars=checkpoint["embargo_bars"],
        )
        committed = store.commit_trial_result(payload, repo_root=root)
        commitments.append(committed["audit_event_id"])
    disposition = (
        "research_completed"
        if checkpoint["fold_binding"] and checkpoint["robustness_binding"]
        else "research_insufficient_evidence"
    )
    if any(
        r["outcome_category"] not in {"successful", "failed"}
        for r in population["variant_result_rows"]
    ):
        disposition = "research_failed"
    report = _report(
        prepared,
        status=disposition,
        terminal_commitments=commitments,
        runner_parity=summary["direct_runner_reconciliation"],
        scratch_result_sha256=file_hash(result_path),
        fold_binding=checkpoint["fold_binding"],
        advisory_mc_binding=checkpoint["robustness_binding"],
        oos_gate="withheld_missing_walkforward_oos_inputs: existing evaluator requires candidate-review input; no synthetic candidate",
        accepted_proposal_count=prepared["proposal_counts"]["accepted"],
        rejected_proposal_count=prepared["proposal_counts"]["rejected"],
        duplicate_proposal_count=prepared["proposal_counts"]["duplicate"],
        scientific_denominator=prepared["scientific_denominator"],
        approval_decision="verified_exact_v2",
        approval_sha256=approval_hash,
        fold_completeness="verified_full_population"
        if checkpoint["fold_binding"]
        else "withheld_missing_folds",
        advisory_mc_status="advisory_only" if checkpoint["robustness_binding"] else "missing",
        recovered=not physical_run_completed,
        runner_calls=2 if physical_run_completed else 0,
        historical_adapter_invocations=1,
        historical_parity_verification_invocations=1,
    )
    report["withholding_reasons"] = [report["oos_gate"]]
    if not checkpoint["fold_binding"]:
        report["withholding_reasons"].append("withheld_missing_folds")
    write_once(path.parent / "research_factory_report.json", report)
    return report
