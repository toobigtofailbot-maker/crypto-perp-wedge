"""Bounded advisory robustness diagnostics over real bridge scratch outputs."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from tools.agent_sandbox import ToolAction, ToolContext
from tools.agent_sandbox.permissions import (
    READ_NON_SECRET,
    RUN_READ_ONLY_VALIDATION,
    RUN_SCRATCH_ROBUSTNESS_DIAGNOSTIC,
    WRITE_SCRATCH,
)
from tools.registry.validate_result_populations import validate_result_populations
from tools.robustness import seeded_advisory_mc as seeded_mc


REPO_ROOT = Path(__file__).resolve().parents[2]
WP_ID = "WP-AGENT-ROBUSTNESS-DIAGNOSTICIAN-01"
ROLE = "robustness_diagnostician"
OUTPUT_ROOT = Path("scratch") / WP_ID / "outputs"
APPROVAL_SCOPE = "noncanonical_scratch_robustness_only"
DIAGNOSTIC_VERSION = "robustness-diagnostician-v1"
RESULT_VALIDATOR_PATH = "tools/registry/validate_result_populations.py"
TRIAL_STATUSES = ("completed", "failed", "invalid", "pruned", "blocked")
RUNNER_OUTCOME_TO_TRIAL_STATUS = {
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
BRIDGE_NON_AUTHORITY_FLAGS = (
    "not canonical",
    "not evidence",
    "not candidate authority",
    "not promotion authority",
    "not paper/live readiness",
    "human review required",
)
NON_AUTHORITY_FLAGS = (*BRIDGE_NON_AUTHORITY_FLAGS, "not ranking authority")


class RobustnessDiagnosticianError(ValueError):
    """Raised when bridge inputs cannot safely support diagnostics."""


@dataclass(frozen=True)
class RobustnessDiagnosticianConfig:
    deterministic_seed: int = 20260622
    bootstrap_samples: int = 1000
    confidence_level: float = 0.95
    timestamp_utc: str = "2026-06-22T00:00:00Z"

    def __post_init__(self) -> None:
        if self.bootstrap_samples <= 0:
            raise ValueError("bootstrap_samples must be positive")
        if not 0.0 < self.confidence_level < 1.0:
            raise ValueError("confidence_level must be between zero and one")


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _sha256(value: Any) -> str:
    return _sha256_bytes(_canonical_bytes(value))


class RobustnessDiagnosticianAgent:
    """ToolContext-routed diagnostician with no canonical or lifecycle authority."""

    def __init__(
        self,
        *,
        config: RobustnessDiagnosticianConfig,
        tool_context: ToolContext,
        repo_root: Path = REPO_ROOT,
    ) -> None:
        if tool_context.role != ROLE or tool_context.wp_id != WP_ID:
            raise ValueError("RobustnessDiagnosticianAgent requires its exact role and WP")
        self.config = config
        self.tool_context = tool_context
        self.repo_root = repo_root.resolve()

    def _repo_relative(self, path: Path | str) -> str:
        candidate = Path(path)
        if candidate.is_absolute():
            try:
                candidate = candidate.resolve().relative_to(self.repo_root)
            except ValueError as exc:
                raise RobustnessDiagnosticianError("path must remain inside the repo") from exc
        normalized = candidate.as_posix()
        if normalized == ".." or normalized.startswith("../"):
            raise RobustnessDiagnosticianError("path must remain inside the repo")
        return normalized

    def _read_json(self, path: Path | str) -> tuple[str, dict[str, Any], str]:
        relative = self._repo_relative(path)
        content = self.tool_context.run_allowed(
            ToolAction(READ_NON_SECRET, relative),
            lambda: (self.repo_root / relative).read_bytes(),
        )
        try:
            payload = json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise RobustnessDiagnosticianError(f"invalid JSON: {relative}") from exc
        if not isinstance(payload, dict):
            raise RobustnessDiagnosticianError(f"JSON root must be an object: {relative}")
        return relative, payload, _sha256_bytes(content)

    def _write_json(self, path: Path, payload: Mapping[str, Any]) -> str:
        relative = self._repo_relative(path)

        def operation() -> None:
            target = self.repo_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )

        self.tool_context.run_allowed(ToolAction(WRITE_SCRATCH, relative), operation)
        return relative

    def _block(self, action_type: str, target_path: str, message: str) -> None:
        self.tool_context.require_allowed(ToolAction(action_type, target_path))
        raise AssertionError(message)

    def _require_approval(
        self, approval: Mapping[str, Any], *, source_run_id: str, approval_path: str
    ) -> None:
        valid = (
            approval.get("approved_for_noncanonical_robustness_diagnostics") is True
            and approval.get("approved_by") == "operator"
            and approval.get("approval_scope") == APPROVAL_SCOPE
            and isinstance(approval.get("approval_timestamp_utc"), str)
            and bool(approval.get("approval_timestamp_utc"))
            and approval.get("source_bridge_run_id") == source_run_id
        )
        if not valid:
            self._block(
                "approval_gate_bypass",
                approval_path,
                "invalid robustness approval was unexpectedly allowed",
            )

    @staticmethod
    def _require_bridge_flags(review: Mapping[str, Any]) -> None:
        flags = review.get("non_authority_flags")
        if not isinstance(flags, list) or not set(BRIDGE_NON_AUTHORITY_FLAGS).issubset(flags):
            raise RobustnessDiagnosticianError("bridge packet lacks required non-authority flags")

    def _validate_paths(
        self,
        *,
        review: Mapping[str, Any],
        result_path: str,
        ledger_path: str,
    ) -> None:
        if result_path not in review.get("runner_artifact_paths", []):
            raise RobustnessDiagnosticianError("runner artifact path is not bound by bridge packet")
        if review.get("full_ledger_path") != ledger_path:
            raise RobustnessDiagnosticianError("denominator ledger path is not bound by bridge packet")

    def _validate_result_population(
        self, review: Mapping[str, Any], result_path: str
    ) -> dict[str, Any]:
        derived = review.get("derived_input_artifact_paths")
        if not isinstance(derived, Mapping):
            raise RobustnessDiagnosticianError("bridge-derived input paths are missing")
        required = ("strategy_spec", "variant_manifest", "sweep_plan")
        if any(not isinstance(derived.get(name), str) for name in required):
            raise RobustnessDiagnosticianError("bridge-derived input paths are incomplete")
        derived_paths = [self._repo_relative(str(derived[name])) for name in required]
        allowed_prefix = "scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/"
        if any(not path.startswith(allowed_prefix) for path in derived_paths):
            self._block(
                "toolcontext_bypass",
                next(path for path in derived_paths if not path.startswith(allowed_prefix)),
                "out-of-prefix validation input was unexpectedly allowed",
            )
        if not result_path.endswith(".result_population.json"):
            self._block(
                "toolcontext_bypass",
                result_path,
                "non-Result-Population runner artifact was unexpectedly allowed",
            )
        input_dirs = {str(Path(path).parent) for path in derived_paths}
        if len(input_dirs) != 1:
            raise RobustnessDiagnosticianError("bridge-derived inputs are not colocated")
        result_dir = self.repo_root / Path(result_path).parent
        input_dir = self.repo_root / input_dirs.pop()
        errors = self.tool_context.run_allowed(
            ToolAction(RUN_READ_ONLY_VALIDATION, RESULT_VALIDATOR_PATH),
            lambda: validate_result_populations(
                result_populations_dir=result_dir,
                strategy_specs_dir=input_dir,
                variant_manifests_dir=input_dir,
                sweep_plans_dir=input_dir,
            ),
        )
        return {"status": "passed" if not errors else "failed", "errors": errors}

    @staticmethod
    def _validate_result_shape(result: Mapping[str, Any]) -> list[Mapping[str, Any]]:
        rows = result.get("variant_result_rows")
        if not isinstance(rows, list) or not all(isinstance(row, Mapping) for row in rows):
            raise RobustnessDiagnosticianError("variant_result_rows must be an array of objects")
        if not isinstance(result.get("lineage"), Mapping):
            raise RobustnessDiagnosticianError("Result Population lineage is missing")
        return rows

    def _denominator_snapshot(
        self,
        *,
        review: Mapping[str, Any],
        ledger: Mapping[str, Any],
        result_rows: Sequence[Mapping[str, Any]],
        target_path: str,
    ) -> dict[str, Any]:
        rows = ledger.get("rows")
        declared = ledger.get("declared_trial_count")
        declared_counts = ledger.get("trial_status_counts")
        if not isinstance(rows, list) or not all(isinstance(row, Mapping) for row in rows):
            raise RobustnessDiagnosticianError("bridge denominator rows are invalid")
        actual_counts = Counter(row.get("trial_status") for row in rows)
        counts = {status: actual_counts.get(status, 0) for status in TRIAL_STATUSES}
        ledger_variants = [row.get("variant_id") for row in rows]
        result_variants = [row.get("variant_id") for row in result_rows]
        result_by_variant = {row.get("variant_id"): row for row in result_rows}
        outcomes_reconcile = all(
            row.get("runner_outcome_category")
            == result_by_variant.get(row.get("variant_id"), {}).get("outcome_category")
            and RUNNER_OUTCOME_TO_TRIAL_STATUS.get(row.get("runner_outcome_category"))
            == row.get("trial_status")
            for row in rows
        )
        valid = (
            ledger.get("denominator_preserved") is True
            and declared == len(rows)
            and isinstance(declared_counts, Mapping)
            and counts == {status: declared_counts.get(status, 0) for status in TRIAL_STATUSES}
            and counts == review.get("denominator_counts")
            and len(ledger_variants) == len(set(ledger_variants))
            and set(ledger_variants) == set(result_variants)
            and len(result_rows) == len(rows)
            and sum(counts.values()) == len(rows)
            and outcomes_reconcile
        )
        if not valid:
            self._block(
                "evidence_suppression",
                target_path,
                "denominator shrinkage was unexpectedly allowed",
            )
        return {
            "status": "passed",
            "source_declared_trial_count": declared,
            "source_status_counts": counts,
            "result_row_count": len(result_rows),
            "all_source_rows_preserved": True,
            "row_disposition": [
                {
                    "variant_id": row.get("variant_id"),
                    "trial_status": row.get("trial_status"),
                    "eligible_for_metrics": row.get("trial_status") == "completed",
                    "status_reason": row.get("status_reason"),
                }
                for row in rows
            ],
        }

    @staticmethod
    def _completed_rows(
        result_rows: Sequence[Mapping[str, Any]], ledger: Mapping[str, Any]
    ) -> list[dict[str, Any]]:
        params = {
            row["variant_id"]: row.get("params", {})
            for row in ledger["rows"]
            if row.get("trial_status") == "completed"
        }
        completed: list[dict[str, Any]] = []
        for row in result_rows:
            variant_id = row.get("variant_id")
            if variant_id not in params:
                continue
            if row.get("attempted") is not True or row.get("outcome_category") != "successful":
                raise RobustnessDiagnosticianError(
                    f"completed bridge row is not successful in runner artifact: {variant_id}"
                )
            enriched = copy.deepcopy(dict(row))
            enriched["parameter_values"] = copy.deepcopy(params[variant_id])
            completed.append(enriched)
        if len(completed) != len(params):
            raise RobustnessDiagnosticianError("completed-row mapping is incomplete")
        return sorted(completed, key=lambda row: str(row["variant_id"]))

    def _diagnose(
        self,
        *,
        result: Mapping[str, Any],
        completed_rows: list[dict[str, Any]],
        review: Mapping[str, Any],
        ledger: Mapping[str, Any],
        run_dir: Path,
    ) -> dict[str, Any]:
        target = (run_dir / "robustness_diagnostics.json").as_posix()

        def operation() -> tuple[dict[str, Any], list[dict[str, Any]], str, dict[str, Any]]:
            bootstrap, skipped, samples = seeded_mc._bootstrap_diagnostics(
                rows=completed_rows,
                seed=self.config.deterministic_seed,
                sample_count=self.config.bootstrap_samples,
                confidence_level=self.config.confidence_level,
            )
            sensitivity = seeded_mc._parameter_sensitivity(
                dict(result), completed_rows, sorted(bootstrap)
            )
            return bootstrap, skipped, seeded_mc._sha256_payload(samples), sensitivity

        bootstrap, metric_skips, samples_hash, sensitivity = self.tool_context.run_allowed(
            ToolAction(RUN_SCRATCH_ROBUSTNESS_DIAGNOSTIC, target), operation
        )
        has_folds = any(
            any(key in row for key in ("fold_id", "in_sample_metrics", "out_of_sample_metrics"))
            for row in completed_rows
        )
        oos_status = (
            {"status": "available", "reason": "fold_compatible_fields_present"}
            if has_folds
            else {"status": "missing_fold_inputs", "queued_follow_up": True}
        )
        has_trade_rows = any(isinstance(row.get("trade_rows"), list) for row in completed_rows)
        per_trade = (
            {"status": "available_not_run", "fabricated_per_trade_data": False}
            if has_trade_rows
            else seeded_mc._per_trade_diagnostic()
        )
        funding = review.get("funding_mode", {})
        funding_values = [
            seeded_mc._finite_number(row.get("metrics", {}).get("funding"))
            for row in completed_rows
            if isinstance(row.get("metrics"), Mapping)
        ]
        funding_values = [value for value in funding_values if value is not None]
        if funding.get("requested") == "off":
            funding_status = {"status": "not_applicable_funding_mode_off", "performed": False}
        elif not completed_rows:
            funding_status = {"status": "blocked_funding_on_condition", "performed": False}
        elif not funding_values:
            funding_status = {
                "status": "not_applicable_or_missing_funding_inputs",
                "performed": False,
            }
        else:
            funding_status = {
                "status": "aggregate_funding_visible_no_stress_assumption",
                "performed": False,
                "observed_row_count": len(funding_values),
            }
        return {
            "schema_version": "robustness_diagnostician_diagnostics_v1",
            "diagnostic_version": DIAGNOSTIC_VERSION,
            "seed": self.config.deterministic_seed,
            "bootstrap_sample_count": self.config.bootstrap_samples,
            "confidence_level": self.config.confidence_level,
            "completed_row_count": len(completed_rows),
            "bootstrap_mc_summary": bootstrap,
            "bootstrap_samples_hash": samples_hash,
            "metric_diagnostics_skipped": metric_skips,
            "parameter_sensitivity_summary": sensitivity,
            "oos_walkforward_status": oos_status,
            "per_trade_status": per_trade,
            "funding_stress_status": funding_status,
            "data_availability_warnings": list(review.get("data_availability_warnings", [])),
            "data_availability_blockers": list(review.get("data_availability_blockers", [])),
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }

    def run(
        self,
        *,
        bridge_review_packet_path: Path | str,
        bridge_result_population_artifact_path: Path | str,
        bridge_denominator_ledger_path: Path | str,
        operator_robustness_approval_path: Path | str,
    ) -> dict[str, Any]:
        review_path, review, review_hash = self._read_json(bridge_review_packet_path)
        result_path, result, result_hash = self._read_json(
            bridge_result_population_artifact_path
        )
        ledger_path, ledger, ledger_hash = self._read_json(bridge_denominator_ledger_path)
        approval_path, approval, approval_hash = self._read_json(
            operator_robustness_approval_path
        )
        source_run_id = review.get("run_id")
        if not isinstance(source_run_id, str) or ledger.get("run_id") != source_run_id:
            raise RobustnessDiagnosticianError("bridge run IDs do not match")
        self._require_bridge_flags(review)
        self._require_approval(
            approval, source_run_id=source_run_id, approval_path=approval_path
        )
        self._validate_paths(review=review, result_path=result_path, ledger_path=ledger_path)
        result_rows = self._validate_result_shape(result)
        result_validation = self._validate_result_population(review, result_path)
        if result_validation["status"] == "failed":
            raise RobustnessDiagnosticianError("scratch Result Population validation failed")
        run_identity = {
            "bridge_review_hash": review_hash,
            "result_population_hash": result_hash,
            "denominator_ledger_hash": ledger_hash,
            "approval_hash": approval_hash,
            "config": self.config.__dict__,
            "diagnostic_version": DIAGNOSTIC_VERSION,
        }
        run_id = hashlib.sha256(_canonical_bytes(run_identity)).hexdigest()[:16]
        run_dir = OUTPUT_ROOT / run_id
        denominator = self._denominator_snapshot(
            review=review,
            ledger=ledger,
            result_rows=result_rows,
            target_path=(run_dir / "robustness_diagnostics.json").as_posix(),
        )
        completed_rows = self._completed_rows(result_rows, ledger)
        if not completed_rows:
            raise RobustnessDiagnosticianError("no completed rows support aggregate diagnostics")
        diagnostics = self._diagnose(
            result=result,
            completed_rows=completed_rows,
            review=review,
            ledger=ledger,
            run_dir=run_dir,
        )
        diagnostics["run_id"] = run_id
        diagnostics["source_bridge_run_id"] = source_run_id
        diagnostics["denominator_integrity"] = denominator
        diagnostics["lineage_hash_preservation"] = {
            "status": "passed",
            "bridge_review_packet_path": review_path,
            "bridge_review_packet_hash": review_hash,
            "runner_artifact_path": result_path,
            "runner_artifact_hash": result_hash,
            "denominator_ledger_path": ledger_path,
            "denominator_ledger_hash": ledger_hash,
        }
        diagnostics_path = self._write_json(
            run_dir / "robustness_diagnostics.json", diagnostics
        )
        skipped = [
            {"diagnostic": "metric", **item}
            for item in diagnostics["metric_diagnostics_skipped"]
        ]
        for name in ("oos_walkforward_status", "per_trade_status", "funding_stress_status"):
            value = diagnostics[name]
            if value.get("status") not in {"available", "performed"}:
                skipped.append({"diagnostic": name, "reason": value.get("status")})
        packet = {
            "schema_version": "robustness_diagnostician_review_packet_v1",
            "run_id": run_id,
            "source_bridge_metadata": {
                "run_id": source_run_id,
                "review_packet_path": review_path,
                "review_packet_hash": review_hash,
            },
            "source_runner_artifact_path": result_path,
            "source_runner_artifact_hash": result_hash,
            "source_denominator_ledger_path": ledger_path,
            "source_denominator_ledger_hash": ledger_hash,
            "approval_metadata": copy.deepcopy(approval),
            "approval_marker_path": approval_path,
            "approval_marker_hash": approval_hash,
            "result_population_validation": result_validation,
            "diagnostics_attempted": [
                "seeded_variant_metric_bootstrap",
                "metric_confidence_intervals",
                "parameter_sensitivity",
                "denominator_integrity",
                "source_lineage_hash_preservation",
                "oos_walkforward",
                "per_trade_resampling",
                "funding_stress",
                "data_availability_propagation",
            ],
            "diagnostics_completed": [
                "seeded_variant_metric_bootstrap",
                "metric_confidence_intervals",
                "parameter_sensitivity",
                "denominator_integrity",
                "source_lineage_hash_preservation",
                "funding_mode_visibility",
                "data_availability_propagation",
            ],
            "diagnostics_skipped": skipped,
            "bootstrap_mc_summary": diagnostics["bootstrap_mc_summary"],
            "parameter_sensitivity_summary": diagnostics[
                "parameter_sensitivity_summary"
            ],
            "oos_walkforward_status": diagnostics["oos_walkforward_status"],
            "per_trade_status": diagnostics["per_trade_status"],
            "funding_stress_status": diagnostics["funding_stress_status"],
            "denominator_integrity_status": denominator,
            "data_availability_warnings": diagnostics["data_availability_warnings"],
            "data_availability_blockers": diagnostics["data_availability_blockers"],
            "recommended_follow_up_evidence_gaps": [
                item["reason"] for item in skipped if isinstance(item.get("reason"), str)
            ],
            "robustness_diagnostics_path": diagnostics_path,
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
        review_output_path = self._write_json(
            run_dir / "robustness_review_packet.json", packet
        )
        return {
            "run_id": run_id,
            "status": "completed",
            "artifact_paths": {
                "robustness_diagnostics": diagnostics_path,
                "robustness_review_packet": review_output_path,
            },
            "source_bridge_run_id": source_run_id,
            "source_denominator_counts": denominator["source_status_counts"],
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
