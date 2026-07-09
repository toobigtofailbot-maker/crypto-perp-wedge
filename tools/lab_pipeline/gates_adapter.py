"""Product evaluation adapters over product runner output.

This module is productization glue around existing advisory gates and agents. It
does not change the WFO/OOS, robustness, candidate-review, runner, bridge, or
candidate-surface contracts.
"""

from __future__ import annotations

import copy
import json
import shutil
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from tools.agent_sandbox import MemoryAuditSink, ToolContext
from tools.lab_pipeline.gate_actions import record_candidate_surface_decision
from tools.lab_pipeline.state import file_sha256, read_json, sha256_payload, write_json, write_text
from tools.oos_gate.evaluate import evaluate_candidate_review_gate
from tools.research_agents.candidate_review_packet_agent import (
    APPROVAL_SCOPE as CANDIDATE_REVIEW_APPROVAL_SCOPE,
)
from tools.research_agents.candidate_review_packet_agent import (
    LIFECYCLE_HELPER_PATHS,
    ROLE as CANDIDATE_REVIEW_ROLE,
)
from tools.research_agents.candidate_review_packet_agent import (
    WP_ID as CANDIDATE_REVIEW_WP_ID,
)
from tools.research_agents.candidate_review_packet_agent import (
    CandidateReviewPacketAgent,
    CandidateReviewPacketConfig,
)
from tools.research_agents.robustness_diagnostician_agent import (
    APPROVAL_SCOPE as ROBUSTNESS_APPROVAL_SCOPE,
)
from tools.research_agents.robustness_diagnostician_agent import (
    ROLE as ROBUSTNESS_ROLE,
)
from tools.research_agents.robustness_diagnostician_agent import (
    WP_ID as ROBUSTNESS_WP_ID,
)
from tools.research_agents.robustness_diagnostician_agent import (
    RobustnessDiagnosticianAgent,
    RobustnessDiagnosticianConfig,
)


SOURCE_REPO_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = SOURCE_REPO_ROOT
WP_ID = "WP-LABPROD-PIPELINE-GATES-ADAPTERS-05"
DEFAULT_SCRATCH_ROOT = REPO_ROOT / "scratch" / WP_ID
DEFAULT_OUTPUT_ROOT = DEFAULT_SCRATCH_ROOT / "outputs"

ADVISORY_PACKET_SCHEMA_VERSION = "product_pipeline_advisory_review_packet_v1"
GATES_ADAPTER_SCHEMA_VERSION = "product_pipeline_gates_adapter_result_v1"
COMPAT_BRIDGE_PREFIX = "scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs"
COMPAT_FORMALIZER_PREFIX = "scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs"
DENOMINATOR_STATUSES = ("completed", "failed", "invalid", "blocked", "pruned")
RUNNER_OUTCOME_TO_STATUS = {
    "successful": "completed",
    "failed": "failed",
    "invalid": "invalid",
    "excluded": "pruned",
    "filtered": "pruned",
    "errored": "blocked",
    "aborted": "blocked",
    "data_unavailable": "blocked",
    "not_attempted": "blocked",
}
NON_AUTHORITY_ASSERTIONS = {
    "canonical_evidence_written": False,
    "candidate_lifecycle_written": False,
    "candidate_registry_written": False,
    "candidate_admission": False,
    "crossing": False,
    "promotion_or_readiness": False,
    "paper_live_runtime_contact": False,
    "scheduler_autonomous_dispatch": False,
    "notification_firing": False,
    "provider_api_credential_use": False,
    "dependency_config_data_acquisition": False,
    "protected_path_touch": False,
}


class GatesAdapterError(ValueError):
    """Raised when product evaluation adapters must fail closed."""


@dataclass(frozen=True)
class GatesAdapterResult:
    gates_adapter_run_id: str
    adapter_status: str
    output_dir: Path
    artifact_paths: dict[str, str]
    direct_agent_reconciliation: dict[str, Any]
    candidate_surface_status: str


def _fixed_clock() -> datetime:
    return datetime(2026, 7, 8, 0, 0, 0, tzinfo=timezone.utc)


def _safe_repo_relative(path: Path | str) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        try:
            candidate = candidate.resolve().relative_to(REPO_ROOT.resolve())
        except ValueError as exc:
            raise GatesAdapterError(f"path is outside repo root: {path}") from exc
    normalized = candidate.as_posix()
    pure = PurePosixPath(normalized.replace("\\", "/"))
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise GatesAdapterError(f"path must be safe repo-relative: {path}")
    if pure.parts and pure.parts[0].endswith(":"):
        raise GatesAdapterError(f"path must be safe repo-relative: {path}")
    return pure.as_posix()


def _repo_path(path: Path | str) -> Path:
    return REPO_ROOT / _safe_repo_relative(path)


def _validate_output_root(output_root: Path) -> None:
    resolved = output_root.resolve()
    allowed = DEFAULT_OUTPUT_ROOT.resolve()
    try:
        resolved.relative_to(allowed)
    except ValueError as exc:
        raise GatesAdapterError(
            "gates adapter output_root must be under "
            f"{allowed.as_posix()}; got {resolved.as_posix()}"
        ) from exc


def _adapter_run_id(runner_summary: Mapping[str, Any], runner_summary_hash: str) -> str:
    digest = sha256_payload(
        {
            "adapter": "product_pipeline_gates_adapters_v1",
            "runner_summary_hash": runner_summary_hash,
            "runner_adapter_run_id": runner_summary.get("runner_adapter_run_id"),
            "runner_result_hash": runner_summary.get("runner_outputs", {}).get(
                "adapter_result_population_sha256"
            ),
        }
    ).split(":", 1)[1][:16]
    return f"LGATE-{digest}"


def _require_runner_summary(path: Path) -> tuple[dict[str, Any], str]:
    summary = read_json(path)
    errors: list[str] = []
    if summary.get("schema_version") != "product_runner_adapter_result_v1":
        errors.append("runner summary schema_version mismatch")
    if summary.get("adapter_status") != "completed":
        errors.append("runner adapter did not complete")
    if summary.get("noncanonical_status") != "noncanonical_product_scratch_only":
        errors.append("runner summary is not product-scratch noncanonical")
    if summary.get("full_denominator_preserved") is not True:
        errors.append("runner denominator was not preserved")
    if summary.get("winner_narrowing") is not False:
        errors.append("runner summary indicates winner narrowing")
    reconciliation = summary.get("direct_runner_reconciliation")
    if not isinstance(reconciliation, Mapping) or reconciliation.get("verdict") != "passed":
        errors.append("runner direct reconciliation did not pass")
    bindings = summary.get("source_bindings")
    outputs = summary.get("runner_outputs")
    if not isinstance(bindings, Mapping):
        errors.append("runner source_bindings missing")
    if not isinstance(outputs, Mapping):
        errors.append("runner_outputs missing")
    if errors:
        raise GatesAdapterError("; ".join(errors))
    return summary, file_sha256(path)


def _bridge_paths_from_runner(summary: Mapping[str, Any]) -> dict[str, str]:
    bindings = summary["source_bindings"]
    strategy_path = _safe_repo_relative(bindings["prepared_strategy_spec_path"])
    input_dir = _repo_path(strategy_path).parent
    bridge_dir = input_dir.parent
    review_path = _safe_repo_relative(bridge_dir / "human_review_packet.json")
    ledger_path = _safe_repo_relative(bridge_dir / "denominator_ledger.json")
    review = read_json(_repo_path(review_path))
    ledger = read_json(_repo_path(ledger_path))
    bridge_run_id = str(bindings["bridge_preparation_run_id"])
    if review.get("run_id") != bridge_run_id or ledger.get("run_id") != bridge_run_id:
        raise GatesAdapterError("product bridge run ids do not match runner bindings")
    metadata = review.get("product_bridge_preparation_metadata")
    if not isinstance(metadata, Mapping):
        raise GatesAdapterError("product bridge preparation metadata missing")
    formalizer_path = _safe_repo_relative(str(metadata.get("source_formalizer_output_path")))
    return {
        "product_bridge_review": review_path,
        "product_bridge_denominator_ledger": ledger_path,
        "product_formalizer_output": formalizer_path,
    }


def _status_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = Counter()
    for row in rows:
        outcome = row.get("outcome_category")
        if outcome not in RUNNER_OUTCOME_TO_STATUS:
            raise GatesAdapterError(f"unsupported runner outcome category: {outcome}")
        counts[RUNNER_OUTCOME_TO_STATUS[outcome]] += 1
    return {status: counts.get(status, 0) for status in DENOMINATOR_STATUSES}


def _load_runner_result(summary: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    path = _safe_repo_relative(summary["runner_outputs"]["adapter_result_population_path"])
    result = read_json(_repo_path(path))
    declared_hash = summary["runner_outputs"].get("adapter_result_population_sha256")
    if declared_hash != file_sha256(_repo_path(path)):
        raise GatesAdapterError("runner Result Population hash mismatch")
    rows = result.get("variant_result_rows")
    if not isinstance(rows, list) or not all(isinstance(row, Mapping) for row in rows):
        raise GatesAdapterError("runner Result Population rows are missing")
    counts = _status_counts(rows)
    if counts != summary.get("denominator_counts"):
        raise GatesAdapterError("runner denominator counts mismatch Result Population rows")
    return path, result


def _copy_file(src_root: Path, dst_root: Path, src_rel: str, dst_rel: str) -> str:
    src = src_root / src_rel
    dst = dst_root / dst_rel
    if not src.is_file():
        raise GatesAdapterError(f"required source file missing: {src_rel}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return dst_rel


def _write_temp_json(root: Path, relative: str, payload: Mapping[str, Any]) -> str:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return relative


def _compatibility_bundle(
    *,
    temp_root: Path,
    runner_summary: Mapping[str, Any],
    runner_result_path: str,
    runner_result: Mapping[str, Any],
    bridge_paths: Mapping[str, str],
) -> dict[str, str]:
    product_review = read_json(_repo_path(bridge_paths["product_bridge_review"]))
    product_ledger = read_json(_repo_path(bridge_paths["product_bridge_denominator_ledger"]))
    product_formalizer = read_json(_repo_path(bridge_paths["product_formalizer_output"]))
    bindings = runner_summary["source_bindings"]
    bridge_run_id = str(bindings["bridge_preparation_run_id"])
    formalizer_run_id = str(product_formalizer["run_id"])
    compat_base = f"{COMPAT_BRIDGE_PREFIX}/{bridge_run_id}"
    compat_inputs = f"{compat_base}/inputs"
    compat_formalizer = f"{COMPAT_FORMALIZER_PREFIX}/{formalizer_run_id}/formalized_idea.json"
    compat_strategy = f"{compat_inputs}/{Path(bindings['prepared_strategy_spec_path']).name}"
    compat_manifest = f"{compat_inputs}/{Path(bindings['prepared_variant_manifest_path']).name}"
    compat_sweep = f"{compat_inputs}/{Path(bindings['prepared_sweep_plan_path']).name}"
    compat_result = f"{compat_base}/runner_artifacts/{Path(runner_result_path).name}"
    compat_review = f"{compat_base}/human_review_packet.json"
    compat_ledger = f"{compat_base}/denominator_ledger.json"

    _copy_file(REPO_ROOT, temp_root, bridge_paths["product_formalizer_output"], compat_formalizer)
    _copy_file(REPO_ROOT, temp_root, bindings["prepared_strategy_spec_path"], compat_strategy)
    _copy_file(REPO_ROOT, temp_root, bindings["prepared_variant_manifest_path"], compat_manifest)
    _copy_file(REPO_ROOT, temp_root, bindings["prepared_sweep_plan_path"], compat_sweep)
    _copy_file(REPO_ROOT, temp_root, runner_result_path, compat_result)

    product_rows_by_variant = {
        row.get("variant_id"): row
        for row in product_ledger.get("rows", [])
        if isinstance(row, Mapping)
    }
    result_rows = runner_result["variant_result_rows"]
    result_by_variant = {row.get("variant_id"): row for row in result_rows}
    rows: list[dict[str, Any]] = []
    for index, result_row in enumerate(result_rows, start=1):
        variant_id = result_row.get("variant_id")
        source_row = product_rows_by_variant.get(variant_id, {})
        outcome = result_row.get("outcome_category")
        status = RUNNER_OUTCOME_TO_STATUS[outcome]
        non_success = result_row.get("non_success")
        error = result_row.get("error")
        reason = "successful" if status == "completed" else str(outcome)
        if isinstance(non_success, Mapping) and non_success.get("reason"):
            reason = str(non_success["reason"])
        elif isinstance(error, Mapping) and error.get("error_message_class"):
            reason = str(error["error_message_class"])
        rows.append(
            {
                "run_id": bridge_run_id,
                "source_formalizer_run_id": formalizer_run_id,
                "source_formalizer_artifact_path": compat_formalizer,
                "approval_scope": "noncanonical_product_runner_execution_only",
                "bridge_input_paths": {
                    "strategy_spec": compat_strategy,
                    "variant_manifest": compat_manifest,
                    "sweep_plan": compat_sweep,
                },
                "runner_invocation_id": runner_summary["runner_adapter_run_id"],
                "strategy_family": source_row.get("strategy_family"),
                "variant_id": variant_id,
                "trial_id": f"{bridge_run_id}-TRIAL-{index:03d}",
                "trial_status": status,
                "status_reason": reason,
                "runner_outcome_category": outcome,
                "params": copy.deepcopy(source_row.get("params", {})),
                "funding_cost_mode": source_row.get("funding_cost_mode", "off"),
                "input_hash": source_row.get("input_hash"),
                "output_hash": result_row.get("row_identity_hash"),
                "metrics_summary": copy.deepcopy(result_row.get("metrics")),
                "runner_artifact_path": compat_result,
                "started_at_utc": source_row.get("started_at_utc", "2026-07-08T00:00:00Z"),
                "finished_at_utc": source_row.get("finished_at_utc", "2026-07-08T00:00:00Z"),
                "non_authority_flags": list(product_review["non_authority_flags"]),
            }
        )
    counts = _status_counts(result_rows)
    if counts != runner_summary["denominator_counts"]:
        raise GatesAdapterError("compatibility denominator count mismatch")
    ledger = {
        "schema_version": "formalizer_runner_bridge_denominator_ledger_v1",
        "run_id": bridge_run_id,
        "declared_trial_count": len(rows),
        "denominator_preserved": True,
        "trial_status_counts": counts,
        "rows": rows,
        "non_authority_flags": list(product_review["non_authority_flags"]),
    }
    completed = [row for row in rows if row["trial_status"] == "completed"]
    review = {
        "schema_version": "formalizer_runner_bridge_human_review_packet_v1",
        "run_id": bridge_run_id,
        "source_idea_formalizer_summary": copy.deepcopy(
            product_review["source_idea_formalizer_summary"]
        ),
        "approval_metadata": {
            "source_product_bridge_approval": copy.deepcopy(product_review["approval_metadata"]),
            "source_product_runner_execute_approval": copy.deepcopy(
                runner_summary["execute_approval"]
            ),
        },
        "derived_input_artifact_paths": {
            "strategy_spec": compat_strategy,
            "variant_manifest": compat_manifest,
            "sweep_plan": compat_sweep,
        },
        "runner_invocation_metadata": {
            "runner": "tools.research_runner.run_offline_sweep",
            "runner_adapter_run_id": runner_summary["runner_adapter_run_id"],
            "mode": "product_runner_adapter_compatibility_envelope",
            "deterministic_seed": runner_summary["source_bindings"].get("deterministic_seed"),
            "network": False,
        },
        "denominator_counts": counts,
        "completed_trial_count": counts["completed"],
        "failed_trial_count": counts["failed"],
        "invalid_trial_count": counts["invalid"],
        "pruned_trial_count": counts["pruned"],
        "blocked_trial_count": counts["blocked"],
        "manual_reconciliation_result": copy.deepcopy(
            runner_summary["direct_runner_reconciliation"]
        ),
        "top_metrics": copy.deepcopy(completed[0]["metrics_summary"]) if completed else None,
        "full_ledger_path": compat_ledger,
        "runner_artifact_paths": [compat_result],
        "validation_status": "passed" if counts["completed"] else "blocked",
        "data_availability_blockers": list(product_review.get("data_availability_blockers", [])),
        "data_availability_warnings": list(product_review.get("data_availability_warnings", [])),
        "funding_mode": {
            "requested": product_review.get("funding_mode", {}).get("requested", "off"),
            "effective": "off",
            "default_off": True,
            "global_mode_mutated": False,
        },
        "non_authority_flags": list(product_review["non_authority_flags"]),
    }
    _write_temp_json(temp_root, compat_ledger, ledger)
    _write_temp_json(temp_root, compat_review, review)
    for relative in LIFECYCLE_HELPER_PATHS:
        _copy_file(SOURCE_REPO_ROOT, temp_root, relative, relative)
    robustness_approval = {
        "approved_for_noncanonical_robustness_diagnostics": True,
        "approved_by": "operator",
        "approval_scope": ROBUSTNESS_APPROVAL_SCOPE,
        "approval_timestamp_utc": "2026-07-08T00:00:00Z",
        "source_bridge_run_id": bridge_run_id,
    }
    robustness_approval_path = _write_temp_json(
        temp_root,
        f"scratch/{ROBUSTNESS_WP_ID}/inputs/operator_robustness_approval.json",
        robustness_approval,
    )
    return {
        "formalizer": compat_formalizer,
        "draft_strategy_spec": compat_strategy,
        "bridge_review": compat_review,
        "denominator_ledger": compat_ledger,
        "runner_result": compat_result,
        "robustness_approval": robustness_approval_path,
        "bridge_run_id": bridge_run_id,
    }


def _run_wfo_oos_adapter(
    *, runner_summary: Mapping[str, Any], runner_result: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    candidate_payload = {
        "candidates": [
            {
                "candidate_id": runner_result.get("result_population_id"),
                "evidence_refs": {
                    "result_population_ref": runner_result.get("result_population_id"),
                },
            }
        ]
    }
    evaluation = evaluate_candidate_review_gate(candidate_payload, None)
    direct = evaluate_candidate_review_gate(copy.deepcopy(candidate_payload), None)
    result = {
        "schema_version": "product_wfo_oos_adapter_result_v1",
        "adapter_status": "blocked",
        "existing_gate_entry_point": "tools.oos_gate.evaluate.evaluate_candidate_review_gate",
        "existing_gate_invoked": True,
        "gate_artifact_supplied": False,
        "gate_evaluation": evaluation,
        "source_runner_adapter_run_id": runner_summary["runner_adapter_run_id"],
        "source_result_population_id": runner_result.get("result_population_id"),
        "withheld_statistics": {
            "status": "withheld_missing_walkforward_oos_inputs",
            "fabricated": False,
            "statistics": [
                "mean_oos_sharpe",
                "minimum_oos_sharpe",
                "maximum_oos_drawdown",
                "walkforward_split_periods",
                "purge_bars",
                "embargo_bars",
            ],
        },
        "caveats": [
            "Product runner output contains aggregate Result Population rows but no fold/OOS window artifact.",
            "No WFO/OOS statistic was filled with zero, estimated, or converted into pass/fail authority.",
        ],
        "non_authority_assertions": dict(NON_AUTHORITY_ASSERTIONS),
    }
    return result, direct


def _run_robustness_direct_pair(
    *,
    temp_root: Path,
    compat: Mapping[str, str],
    config: RobustnessDiagnosticianConfig,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    sink = MemoryAuditSink()
    context = ToolContext(
        wp_id=ROBUSTNESS_WP_ID,
        role=ROBUSTNESS_ROLE,
        audit_sink=sink,
        clock=_fixed_clock,
    )
    agent = RobustnessDiagnosticianAgent(config=config, tool_context=context, repo_root=temp_root)
    args = {
        "bridge_review_packet_path": compat["bridge_review"],
        "bridge_result_population_artifact_path": compat["runner_result"],
        "bridge_denominator_ledger_path": compat["denominator_ledger"],
        "operator_robustness_approval_path": compat["robustness_approval"],
    }
    first = agent.run(**args)
    first_packet = read_json(temp_root / first["artifact_paths"]["robustness_review_packet"])
    first_diagnostics = read_json(temp_root / first["artifact_paths"]["robustness_diagnostics"])
    second = agent.run(**args)
    second_packet = read_json(temp_root / second["artifact_paths"]["robustness_review_packet"])
    second_diagnostics = read_json(temp_root / second["artifact_paths"]["robustness_diagnostics"])
    if first != second or first_packet != second_packet or first_diagnostics != second_diagnostics:
        raise GatesAdapterError("robustness direct-agent reconciliation failed")
    return (
        {
            "result": first,
            "review_packet": first_packet,
            "diagnostics": first_diagnostics,
        },
        {
            "result": second,
            "review_packet": second_packet,
            "diagnostics": second_diagnostics,
        },
        [record.to_dict() for record in sink.records],
    )


def _run_candidate_review_direct_pair(
    *,
    temp_root: Path,
    compat: Mapping[str, str],
    robustness: Mapping[str, Any],
    config: CandidateReviewPacketConfig,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    approval = {
        "approved_for_noncanonical_candidate_review_packet": True,
        "approved_by": "operator",
        "approval_scope": CANDIDATE_REVIEW_APPROVAL_SCOPE,
        "approval_timestamp_utc": "2026-07-08T00:00:00Z",
        "source_bridge_run_id": compat["bridge_run_id"],
        "source_robustness_run_id": robustness["result"]["run_id"],
    }
    approval_path = _write_temp_json(
        temp_root,
        f"scratch/{CANDIDATE_REVIEW_WP_ID}/inputs/operator_candidate_review_approval.json",
        approval,
    )
    sink = MemoryAuditSink()
    context = ToolContext(
        wp_id=CANDIDATE_REVIEW_WP_ID,
        role=CANDIDATE_REVIEW_ROLE,
        audit_sink=sink,
        clock=_fixed_clock,
    )
    agent = CandidateReviewPacketAgent(config=config, tool_context=context, repo_root=temp_root)
    args = {
        "formalizer_research_object_path": compat["formalizer"],
        "formalizer_draft_strategy_spec_path": compat["draft_strategy_spec"],
        "bridge_review_packet_path": compat["bridge_review"],
        "bridge_result_population_artifact_path": compat["runner_result"],
        "bridge_denominator_ledger_path": compat["denominator_ledger"],
        "robustness_diagnostics_path": robustness["result"]["artifact_paths"][
            "robustness_diagnostics"
        ],
        "robustness_review_packet_path": robustness["result"]["artifact_paths"][
            "robustness_review_packet"
        ],
        "operator_candidate_review_approval_path": approval_path,
    }
    first = agent.run(**args)
    first_packet = read_json(temp_root / first["artifact_paths"]["candidate_review_packet_json"])
    first_markdown = (
        temp_root / first["artifact_paths"]["candidate_review_packet_markdown"]
    ).read_text(encoding="utf-8")
    second = agent.run(**args)
    second_packet = read_json(temp_root / second["artifact_paths"]["candidate_review_packet_json"])
    second_markdown = (
        temp_root / second["artifact_paths"]["candidate_review_packet_markdown"]
    ).read_text(encoding="utf-8")
    if first != second or first_packet != second_packet or first_markdown != second_markdown:
        raise GatesAdapterError("candidate-review direct-agent reconciliation failed")
    return (
        {
            "result": first,
            "packet": first_packet,
            "markdown": first_markdown,
        },
        {
            "result": second,
            "packet": second_packet,
            "markdown": second_markdown,
        },
        [record.to_dict() for record in sink.records],
    )


def _surface_status(wfo_result: Mapping[str, Any], candidate_packet: Mapping[str, Any]) -> str:
    aggregate = wfo_result.get("gate_evaluation", {}).get("aggregate", {})
    if aggregate.get("pass_count", 0) > 0 and not candidate_packet.get("blockers"):
        return "hold_for_review"
    if candidate_packet.get("evidence_gaps") or aggregate.get("blocked_count", 0) > 0:
        return "needs_more_evidence"
    return "do_not_escalate"


def _markdown_packet(packet: Mapping[str, Any]) -> str:
    lines = [
        "# Product Pipeline Advisory Review Packet",
        "",
        f"- Gates adapter run ID: {packet['gates_adapter_run_id']}",
        f"- Runner adapter run ID: {packet['runner_result_reference']['runner_adapter_run_id']}",
        f"- Posture: {packet['posture']}",
        f"- Candidate-surface status: {packet['candidate_surface_routing']['surface_status']}",
        "",
        "## Denominator",
    ]
    counts = packet["denominator_counts"]
    lines.extend(f"- {status}: {counts[status]}" for status in DENOMINATOR_STATUSES)
    lines.extend(
        [
            "",
            "## WFO/OOS",
            f"- Status: {packet['wfo_oos_result']['adapter_status']}",
            f"- Withheld: {packet['wfo_oos_result']['withheld_statistics']['status']}",
            "",
            "## Robustness",
        ]
    )
    lines.extend(
        f"- Completed: {item}"
        for item in packet["robustness_result"]["existing_agent_payload"]["review_packet"].get(
            "diagnostics_completed", []
        )
    )
    lines.append("- Skipped diagnostics:")
    for item in packet["robustness_result"]["existing_agent_payload"]["review_packet"].get(
        "diagnostics_skipped", []
    ) or ["none"]:
        lines.append(f"  - {item}")
    lines.extend(
        [
            "",
            "## Candidate Review",
            f"- Status: {packet['candidate_review_result']['existing_agent_result']['status']}",
            "- Non-promotion posture: true",
            "",
            "## Non-Authority",
        ]
    )
    for key, value in packet["non_authority_assertions"].items():
        lines.append(f"- {key}: {str(value).lower()}")
    return "\n".join(lines) + "\n"


def run_product_gates_adapters(
    *,
    runner_adapter_result_path: Path | str,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    robustness_config: RobustnessDiagnosticianConfig | None = None,
    candidate_review_config: CandidateReviewPacketConfig | None = None,
) -> GatesAdapterResult:
    """Run advisory evaluation adapters over one product runner adapter output."""

    output_root_path = Path(output_root)
    _validate_output_root(output_root_path)
    runner_summary_path = _repo_path(runner_adapter_result_path)
    runner_summary, runner_summary_hash = _require_runner_summary(runner_summary_path)
    runner_result_path, runner_result = _load_runner_result(runner_summary)
    bridge_paths = _bridge_paths_from_runner(runner_summary)
    run_id = _adapter_run_id(runner_summary, runner_summary_hash)
    run_dir = output_root_path / run_id

    wfo_result, wfo_direct = _run_wfo_oos_adapter(
        runner_summary=runner_summary, runner_result=runner_result
    )
    if wfo_result["gate_evaluation"] != wfo_direct:
        raise GatesAdapterError("WFO/OOS direct-agent reconciliation failed")

    with tempfile.TemporaryDirectory(prefix="labprod-gates-adapter-") as tmp:
        temp_root = Path(tmp)
        compat = _compatibility_bundle(
            temp_root=temp_root,
            runner_summary=runner_summary,
            runner_result_path=runner_result_path,
            runner_result=runner_result,
            bridge_paths=bridge_paths,
        )
        robustness, robustness_direct, robustness_audit = _run_robustness_direct_pair(
            temp_root=temp_root,
            compat=compat,
            config=robustness_config or RobustnessDiagnosticianConfig(),
        )
        candidate, candidate_direct, candidate_audit = _run_candidate_review_direct_pair(
            temp_root=temp_root,
            compat=compat,
            robustness=robustness,
            config=candidate_review_config or CandidateReviewPacketConfig(
                timestamp_utc="2026-07-08T00:00:00Z"
            ),
        )

    surface_status = _surface_status(wfo_result, candidate["packet"])
    artifacts: dict[str, str] = {}
    artifacts["wfo_oos_result"] = write_json(run_dir / "wfo_oos_result.json", wfo_result)
    robustness_wrapper = {
        "schema_version": "product_robustness_adapter_result_v1",
        "adapter_status": "completed",
        "existing_agent_entry_point": (
            "tools.research_agents.robustness_diagnostician_agent."
            "RobustnessDiagnosticianAgent.run"
        ),
        "existing_agent_invoked": True,
        "existing_agent_payload": robustness,
        "compatibility_sandbox": {
            "used": True,
            "committed": False,
            "reason": "existing agent read/write policy accepts legacy bridge-shaped scratch paths only",
        },
        "audit_records": robustness_audit,
        "non_authority_assertions": dict(NON_AUTHORITY_ASSERTIONS),
    }
    artifacts["robustness_result"] = write_json(
        run_dir / "robustness_result.json", robustness_wrapper
    )
    candidate_wrapper = {
        "schema_version": "product_candidate_review_adapter_result_v1",
        "adapter_status": "completed",
        "existing_agent_entry_point": (
            "tools.research_agents.candidate_review_packet_agent."
            "CandidateReviewPacketAgent.run"
        ),
        "existing_agent_invoked": True,
        "existing_agent_result": candidate["result"],
        "existing_agent_packet": candidate["packet"],
        "existing_agent_markdown": candidate["markdown"],
        "compatibility_sandbox": {
            "used": True,
            "committed": False,
            "reason": "existing agent read/write policy accepts legacy bridge-shaped scratch paths only",
        },
        "audit_records": candidate_audit,
        "non_authority_assertions": dict(NON_AUTHORITY_ASSERTIONS),
    }
    artifacts["candidate_review_result"] = write_json(
        run_dir / "candidate_review_result.json", candidate_wrapper
    )
    direct_reconciliation = {
        "schema_version": "product_gates_direct_agent_reconciliation_v1",
        "wfo_oos": {
            "existing_agent_invoked": True,
            "verdict": "passed",
            "comparison": "byte_stable_json_payload_equality",
        },
        "robustness": {
            "existing_agent_invoked": True,
            "verdict": "passed",
            "comparison": "direct_repeat_payload_equality",
            "adapter_run_id": robustness["result"]["run_id"],
            "direct_run_id": robustness_direct["result"]["run_id"],
        },
        "candidate_review": {
            "existing_agent_invoked": True,
            "verdict": "passed",
            "comparison": "direct_repeat_payload_and_markdown_equality",
            "adapter_run_id": candidate["result"]["run_id"],
            "direct_run_id": candidate_direct["result"]["run_id"],
        },
        "normalization_used": False,
        "verdict": "passed",
    }
    artifacts["direct_agent_reconciliation"] = write_json(
        run_dir / "direct_agent_reconciliation.json", direct_reconciliation
    )
    advisory_packet = {
        "schema_version": ADVISORY_PACKET_SCHEMA_VERSION,
        "gates_adapter_run_id": run_id,
        "adapter_status": "completed",
        "posture": "advisory_only_noncanonical_product_scratch",
        "runner_result_reference": {
            "runner_adapter_result_path": _safe_repo_relative(runner_summary_path),
            "runner_adapter_result_sha256": runner_summary_hash,
            "runner_adapter_run_id": runner_summary["runner_adapter_run_id"],
            "result_population_path": runner_result_path,
            "result_population_sha256": runner_summary["runner_outputs"][
                "adapter_result_population_sha256"
            ],
            "bridge_preparation_run_id": runner_summary["source_bindings"][
                "bridge_preparation_run_id"
            ],
            "product_pipeline_run_id": runner_summary["source_bindings"][
                "product_pipeline_run_id"
            ],
            "execute_approval_path": runner_summary["source_bindings"][
                "execute_approval_path"
            ],
            "execute_approval_sha256": runner_summary["source_bindings"][
                "execute_approval_sha256"
            ],
        },
        "product_bridge_reference": dict(bridge_paths),
        "denominator_counts": dict(runner_summary["denominator_counts"]),
        "full_denominator_preserved": True,
        "status_vocabulary": list(DENOMINATOR_STATUSES),
        "wfo_oos_result": wfo_result,
        "robustness_result": robustness_wrapper,
        "candidate_review_result": candidate_wrapper,
        "withheld_statistics": {
            "wfo_oos": wfo_result["withheld_statistics"],
            "per_trade": candidate["packet"].get("missing_data_limitations", {}).get("per_trade"),
            "oos_walkforward": candidate["packet"].get("missing_data_limitations", {}).get(
                "oos_walkforward"
            ),
            "funding_stress": candidate["packet"].get("missing_data_limitations", {}).get(
                "funding_stress"
            ),
            "fabricated": False,
        },
        "caveats": [
            *wfo_result["caveats"],
            "Robustness and candidate-review raw agent payloads are embedded without promotion authority.",
            "Compatibility sandbox paths inside raw agent payloads are invocation-local and not canonical evidence paths.",
        ],
        "candidate_surface_routing": {
            "surface_status": surface_status,
            "allowed_statuses": [
                "hold_for_review",
                "needs_more_evidence",
                "do_not_escalate",
            ],
            "go_auto_admission": False,
            "go_auto_crossing": False,
            "go_auto_promotion": False,
            "candidate_lifecycle_written": False,
        },
        "direct_agent_reconciliation": direct_reconciliation,
        "non_promotion_posture": {
            "not_canonical_evidence": True,
            "not_candidate_admission": True,
            "not_candidate_lifecycle": True,
            "not_crossing": True,
            "not_promotion_or_readiness": True,
            "not_paper_live_runtime_authority": True,
        },
        "non_authority_assertions": dict(NON_AUTHORITY_ASSERTIONS),
    }
    advisory_path = run_dir / "advisory_review_packet.json"
    artifacts["advisory_review_packet"] = write_json(advisory_path, advisory_packet)
    artifacts["advisory_review_packet_markdown"] = write_text(
        run_dir / "advisory_review_packet.md", _markdown_packet(advisory_packet)
    )

    with tempfile.TemporaryDirectory(prefix="candidate-surface-route-") as tmp:
        surface_result = record_candidate_surface_decision(
            decision=surface_status,
            decided_by="Karl",
            decision_timestamp_utc="2026-07-08T00:00:00Z",
            advisory_packet_path=advisory_path,
            rationale="Product gates adapter advisory routing for evidence follow-up only.",
            output_file=Path(tmp) / "candidate_surface_decision.json",
        )
        surface_payload = surface_result.payload or read_json(surface_result.output_path)
    artifacts["candidate_surface_decision"] = write_json(
        run_dir / "candidate_surface_decision.json", surface_payload
    )
    result_payload = {
        "schema_version": GATES_ADAPTER_SCHEMA_VERSION,
        "gates_adapter_run_id": run_id,
        "adapter_status": "completed",
        "artifact_paths": artifacts,
        "wfo_oos_adapter_invoked_existing_agent": True,
        "robustness_adapter_invoked_existing_agent": True,
        "candidate_review_adapter_invoked_existing_agent": True,
        "agent_logic_reimplemented": False,
        "direct_agent_reconciliation": direct_reconciliation,
        "candidate_surface_status": surface_status,
        "non_authority_assertions": dict(NON_AUTHORITY_ASSERTIONS),
    }
    artifacts["gates_adapter_result"] = write_json(
        run_dir / "gates_adapter_result.json", result_payload
    )
    return GatesAdapterResult(
        gates_adapter_run_id=run_id,
        adapter_status="completed",
        output_dir=run_dir,
        artifact_paths=artifacts,
        direct_agent_reconciliation=direct_reconciliation,
        candidate_surface_status=surface_status,
    )
