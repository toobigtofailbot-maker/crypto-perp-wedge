"""Bounded scratch-only experiment runner for approved formalizer outputs."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from tools.agent_sandbox import BlockedActionError, ToolAction, ToolContext
from tools.agent_sandbox.permissions import (
    READ_NON_SECRET,
    RUN_NONCANONICAL_EXPERIMENT,
    WRITE_SCRATCH,
)
from tools.research_domain.contracts import TRIAL_STATUSES
from tools.research_domain.scientific_accounting import (
    validate_declared_trials,
    validate_trial_denominator,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
WP_ID = "WP-AGENT-EXPERIMENT-RUNNER-01"
ROLE = "experiment_runner"
OUTPUT_ROOT = Path("scratch") / WP_ID / "outputs"
FORMALIZER_OUTPUT_PREFIX = "scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/"
APPROVAL_SCOPE = "noncanonical_scratch_only"
NON_AUTHORITY_FLAGS = (
    "not canonical",
    "not evidence",
    "not candidate authority",
    "not promotion authority",
    "not paper/live readiness",
    "human review required",
)


class ExperimentRunnerError(ValueError):
    """Raised when an approved scratch experiment packet is malformed."""


@dataclass(frozen=True)
class ExperimentRunnerConfig:
    funding_cost_mode: str = "off"
    experiment_scope: str = "full_history_public"
    limitation_acknowledgement: str | None = None
    data_fixture_paths: tuple[str, ...] = ()
    timestamp_utc: str = "2026-06-22T00:00:00Z"

    def __post_init__(self) -> None:
        if self.funding_cost_mode not in {"off", "on"}:
            raise ValueError("funding_cost_mode must be 'off' or 'on'")
        if self.experiment_scope not in {"full_history_public", "limited_noncanonical"}:
            raise ValueError(
                "experiment_scope must be 'full_history_public' or 'limited_noncanonical'"
            )


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


class FixtureExperimentExecutor:
    """Deterministic local executor; it performs no runner, file, network, or API call."""

    execution_mode = "fixture_local_no_network"

    def execute(self, trial: Mapping[str, Any]) -> dict[str, Any]:
        status = str(trial.get("fixture_status", "completed"))
        if status not in TRIAL_STATUSES:
            return {
                "trial_status": "invalid",
                "status_reason": f"unsupported fixture_status={status}",
                "metrics_summary": None,
            }
        metrics = None
        if status == "completed":
            metrics = copy.deepcopy(
                trial.get(
                    "metrics_summary",
                    {"sharpe": 0.0, "return_pct": 0.0, "max_drawdown": 0.0},
                )
            )
        return {
            "trial_status": status,
            "status_reason": str(trial.get("status_reason") or f"fixture {status}"),
            "metrics_summary": metrics,
        }


class ExperimentRunnerAgent:
    """Consumes an approved PR #544 output and writes only scratch review artifacts."""

    def __init__(
        self,
        *,
        config: ExperimentRunnerConfig,
        tool_context: ToolContext,
        repo_root: Path = REPO_ROOT,
    ) -> None:
        if tool_context.role != ROLE or tool_context.wp_id != WP_ID:
            raise ValueError("ExperimentRunnerAgent requires its exact ToolContext role and WP")
        self.config = config
        self.tool_context = tool_context
        self.repo_root = repo_root.resolve()
        self.executor = FixtureExperimentExecutor()

    def _repo_relative(self, path: Path | str) -> str:
        candidate = Path(path)
        if candidate.is_absolute():
            candidate = candidate.resolve().relative_to(self.repo_root)
        normalized = candidate.as_posix()
        if normalized == ".." or normalized.startswith("../"):
            raise ValueError("path must remain inside the repo")
        return normalized

    def _read_text(self, path: Path | str) -> str:
        relative = self._repo_relative(path)
        return self.tool_context.run_allowed(
            ToolAction(READ_NON_SECRET, relative),
            lambda: (self.repo_root / relative).read_text(encoding="utf-8"),
        )

    def _read_json(self, path: Path | str) -> dict[str, Any]:
        payload = json.loads(self._read_text(path))
        if not isinstance(payload, dict):
            raise ExperimentRunnerError(f"JSON root must be an object: {path}")
        return payload

    def _write_json(self, path: Path, payload: Mapping[str, Any]) -> str:
        relative = self._repo_relative(path)

        def operation() -> None:
            target = self.repo_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )

        self.tool_context.run_allowed(ToolAction(WRITE_SCRATCH, relative), operation)
        return relative

    @staticmethod
    def _validate_formalizer_contract(path: str, payload: Mapping[str, Any]) -> None:
        if not path.startswith(FORMALIZER_OUTPUT_PREFIX) or not path.endswith(
            "/formalized_idea.json"
        ):
            raise ExperimentRunnerError("formalizer output must be the scoped scratch artifact")
        if payload.get("schema_version") != "agent_formalized_idea_v1":
            raise ExperimentRunnerError("unsupported formalizer output schema")
        if payload.get("status") not in {"accepted", "needs_data"}:
            raise ExperimentRunnerError("formalizer output is not eligible for experiment review")
        if not isinstance(payload.get("run_id"), str) or not payload.get("run_id"):
            raise ExperimentRunnerError("formalizer run_id is required")
        if not isinstance(payload.get("research_object"), Mapping):
            raise ExperimentRunnerError("formalizer research_object is required")
        non_authority = payload.get("non_authority")
        if not isinstance(non_authority, Mapping) or not non_authority.get("scratch_only"):
            raise ExperimentRunnerError("formalizer non-authority contract is missing")

    def _require_approval(
        self,
        approval: Mapping[str, Any],
        *,
        source_run_id: str,
        approval_path: str,
        formalizer_path: str,
    ) -> None:
        expected_approval_prefix = formalizer_path.rsplit("/", 1)[0] + "/"
        valid = (
            approval_path.startswith(expected_approval_prefix)
            and approval.get("approved_for_noncanonical_experiment") is True
            and approval.get("approved_by") == "operator"
            and approval.get("approval_scope") == APPROVAL_SCOPE
            and isinstance(approval.get("approval_timestamp_utc"), str)
            and bool(approval.get("approval_timestamp_utc"))
            and approval.get("source_formalizer_run_id") == source_run_id
        )
        if valid:
            return
        try:
            self.tool_context.require_allowed(ToolAction("approval_gate_bypass", approval_path))
        except BlockedActionError:
            raise
        raise AssertionError("unapproved experiment was unexpectedly allowed")

    def _fixture_hashes(self) -> dict[str, str]:
        hashes: dict[str, str] = {}
        for fixture_path in self.config.data_fixture_paths:
            relative = self._repo_relative(fixture_path)
            content = self._read_text(relative)
            hashes[relative] = "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()
        return hashes

    def _availability_blockers(
        self, formalized: Mapping[str, Any], fixture_hashes: Mapping[str, str]
    ) -> list[str]:
        assessment = formalized.get("capability_assessment")
        rows = assessment.get("feature_assessments", []) if isinstance(assessment, Mapping) else []
        blockers: list[str] = []
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            feature = str(row.get("feature", "unknown"))
            coverage = str(row.get("coverage_class", ""))
            source = str(row.get("source_class", ""))
            testability = str(row.get("historical_testability", ""))
            if feature in {
                "taker_buy_sell_ratio",
                "taker_buy_volume",
                "taker_sell_volume",
            } and source == "CANONICAL_D4_KLINE_DERIVATION":
                if not fixture_hashes:
                    blockers.append(
                        f"{feature} requires a present provenance-bound D4-derived feature table/manifest"
                    )
                continue
            constrained = coverage in {
                "PUBLIC_SNAPSHOT_ONLY",
                "RECENT_ONLY_PUBLIC_REST",
                "STREAMING_ONLY_PUBLIC_CAPTURE",
                "VENDOR_ONLY_FOR_HISTORY",
            } or testability in {"vendor_or_capture_constrained", "blocked_unknown"}
            if self.config.experiment_scope == "full_history_public" and constrained:
                blockers.append(
                    f"{feature} cannot run as full-history public data ({coverage or testability})"
                )
            elif constrained and not self.config.limitation_acknowledgement:
                blockers.append(
                    f"{feature} requires an explicit noncanonical limitation acknowledgement"
                )
            if feature in {"open_interest", "open_interest_value"} and source.startswith("PUBLIC_"):
                blockers.append("open interest cannot be reconstructed from trades")
            if feature == "liquidation_volume" and not fixture_hashes:
                blockers.append("liquidation history requires vendor/captured fixture data")
        return list(dict.fromkeys(blockers))

    @staticmethod
    def _validate_trials(trials: Sequence[Mapping[str, Any]]) -> None:
        try:
            validate_declared_trials(trials)
        except ValueError as exc:
            raise ExperimentRunnerError(str(exc)) from exc

    @staticmethod
    def _assert_denominator(ledger: Sequence[Mapping[str, Any]], expected_ids: set[str]) -> None:
        try:
            validate_trial_denominator(ledger, expected_ids)
        except ValueError as exc:
            raise ExperimentRunnerError(str(exc)) from exc

    def run(
        self,
        *,
        formalizer_output_path: Path | str,
        approval_path: Path | str,
        trials: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        formalizer_path = self._repo_relative(formalizer_output_path)
        approval_relative = self._repo_relative(approval_path)
        formalized = self._read_json(formalizer_path)
        self._validate_formalizer_contract(formalizer_path, formalized)
        approval = self._read_json(approval_relative)
        self._require_approval(
            approval,
            source_run_id=str(formalized["run_id"]),
            approval_path=approval_relative,
            formalizer_path=formalizer_path,
        )
        self._validate_trials(trials)
        fixture_hashes = self._fixture_hashes()
        blockers = self._availability_blockers(formalized, fixture_hashes)

        draft_path = formalized.get("draft_strategy_spec", {}).get("path")
        draft_hash = None
        if draft_path:
            if not str(draft_path).startswith(FORMALIZER_OUTPUT_PREFIX):
                raise ExperimentRunnerError("draft Strategy Spec must remain in formalizer scratch")
            draft_hash = _sha256(self._read_json(str(draft_path)))

        run_identity = {
            "source_formalizer_run_id": formalized["run_id"],
            "formalizer_output_path": formalizer_path,
            "approval": approval,
            "config": {
                "funding_cost_mode": self.config.funding_cost_mode,
                "experiment_scope": self.config.experiment_scope,
                "limitation_acknowledgement": self.config.limitation_acknowledgement,
                "data_fixture_hashes": fixture_hashes,
            },
            "trials": list(trials),
        }
        run_id = hashlib.sha256(_canonical_bytes(run_identity)).hexdigest()[:16]
        run_dir = OUTPUT_ROOT / run_id
        run_target = (run_dir / "experiment_run_packet.json").as_posix()

        def execute_all() -> list[dict[str, Any]]:
            ledger: list[dict[str, Any]] = []
            for trial in trials:
                input_hash = _sha256(trial)
                outcome = (
                    {
                        "trial_status": "blocked",
                        "status_reason": "; ".join(blockers),
                        "metrics_summary": None,
                    }
                    if blockers
                    else self.executor.execute(trial)
                )
                metrics = outcome["metrics_summary"]
                ledger.append(
                    {
                        "run_id": run_id,
                        "source_formalizer_run_id": formalized["run_id"],
                        "source_formalizer_artifact_path": formalizer_path,
                        "approval_scope": approval["approval_scope"],
                        "strategy_family": str(trial["strategy_family"]),
                        "variant_id": str(trial["variant_id"]),
                        "trial_id": str(trial["trial_id"]),
                        "trial_status": outcome["trial_status"],
                        "status_reason": outcome["status_reason"],
                        "params": copy.deepcopy(dict(trial["params"])),
                        "input_hash": input_hash,
                        "output_hash": _sha256(metrics) if metrics is not None else None,
                        "metrics_summary": metrics,
                        "started_at_utc": self.config.timestamp_utc,
                        "finished_at_utc": self.config.timestamp_utc,
                        "non_authority_flags": list(NON_AUTHORITY_FLAGS),
                    }
                )
            return ledger

        ledger = self.tool_context.run_allowed(
            ToolAction(RUN_NONCANONICAL_EXPERIMENT, run_target), execute_all
        )
        self._assert_denominator(ledger, {str(trial["trial_id"]) for trial in trials})
        counts = Counter(row["trial_status"] for row in ledger)
        denominator_counts = {status: counts.get(status, 0) for status in TRIAL_STATUSES}
        completed = [row for row in ledger if row["trial_status"] == "completed"]
        top_metrics = completed[0]["metrics_summary"] if completed else None

        ledger_packet = {
            "schema_version": "agent_experiment_denominator_ledger_v1",
            "run_id": run_id,
            "declared_trial_count": len(trials),
            "denominator_preserved": True,
            "trial_status_counts": denominator_counts,
            "rows": ledger,
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
        ledger_path = self._write_json(run_dir / "denominator_ledger.json", ledger_packet)
        result_packet = {
            "schema_version": "agent_experiment_result_population_like_v1",
            "artifact_type": "scratch_result_population_like_review_only",
            "run_id": run_id,
            "trial_status_counts": denominator_counts,
            "trial_rows": ledger,
            "canonical_result_population": False,
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
        result_path = self._write_json(run_dir / "scratch_results.json", result_packet)
        run_packet = {
            "schema_version": "agent_experiment_run_packet_v1",
            "run_id": run_id,
            "source_formalizer_run_id": formalized["run_id"],
            "source_formalizer_artifact_path": formalizer_path,
            "source_draft_strategy_spec_path": draft_path,
            "source_draft_strategy_spec_hash": draft_hash,
            "approval_metadata": copy.deepcopy(dict(approval)),
            "runner_configuration": {
                "executor": self.executor.execution_mode,
                "real_offline_sweep_integration": "blocked_not_contract_compatible",
                "funding_cost_mode": self.config.funding_cost_mode,
                "funding_explicitly_enabled": self.config.funding_cost_mode == "on",
                "experiment_scope": self.config.experiment_scope,
                "limitation_acknowledgement": self.config.limitation_acknowledgement,
                "data_fixture_hashes": fixture_hashes,
            },
            "trial_denominator_counts": denominator_counts,
            "validation_status": "blocked" if blockers else "passed",
            "blockers": blockers,
            "runner_integration_blockers": [
                "PR #544 output has no frozen Variant Manifest or Sweep Plan; real "
                "run_offline_sweep integration remains blocked for a later approved contract."
            ],
            "artifact_paths": {
                "denominator_ledger": ledger_path,
                "scratch_results": result_path,
            },
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
        run_packet_path = self._write_json(run_dir / "experiment_run_packet.json", run_packet)
        review_packet = {
            "schema_version": "agent_experiment_human_review_packet_v1",
            "run_id": run_id,
            "source_idea_formalizer_summary": copy.deepcopy(formalized.get("research_object")),
            "approval_metadata": copy.deepcopy(dict(approval)),
            "runner_configuration": copy.deepcopy(run_packet["runner_configuration"]),
            "trial_denominator_counts": denominator_counts,
            "completed_trial_count": denominator_counts["completed"],
            "failed_trial_count": denominator_counts["failed"],
            "invalid_trial_count": denominator_counts["invalid"],
            "pruned_trial_count": denominator_counts["pruned"],
            "blocked_trial_count": denominator_counts["blocked"],
            "top_metrics": top_metrics,
            "full_ledger_path": ledger_path,
            "artifact_paths": {
                **run_packet["artifact_paths"],
                "experiment_run_packet": run_packet_path,
            },
            "validation_status": run_packet["validation_status"],
            "blockers": blockers,
            "runner_integration_blockers": run_packet["runner_integration_blockers"],
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
        review_path = self._write_json(run_dir / "human_review_packet.json", review_packet)
        return {
            "run_id": run_id,
            "status": "blocked" if blockers else "completed",
            "trial_status_counts": denominator_counts,
            "artifact_paths": {
                **review_packet["artifact_paths"],
                "human_review_packet": review_path,
            },
            "blockers": blockers,
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
