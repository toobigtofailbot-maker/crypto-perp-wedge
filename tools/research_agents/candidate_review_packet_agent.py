"""Scratch-only candidate review packet agent over bounded agent outputs."""

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
    BUILD_SCRATCH_CANDIDATE_REVIEW_PACKET,
    READ_NON_SECRET,
    WRITE_SCRATCH,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
WP_ID = "WP-AGENT-CANDIDATE-REVIEW-PACKET-01"
ROLE = "candidate_review_packet_preparer"
OUTPUT_ROOT = Path("scratch") / WP_ID / "outputs"
APPROVAL_SCOPE = "noncanonical_scratch_candidate_review_only"
PACKET_VERSION = "candidate-review-packet-v1"
TRIAL_STATUSES = ("completed", "failed", "invalid", "pruned", "blocked")
NON_AUTHORITY_FLAGS = (
    "not canonical",
    "not evidence",
    "not candidate authority",
    "not promotion authority",
    "not ranking authority",
    "not paper/live readiness",
    "not a trading signal",
    "human review required",
)
LIFECYCLE_HELPER_PATHS = (
    "tools/candidate_lifecycle/lifecycle_engine.py",
    "tools/candidate_lifecycle/build_candidate_review_packet.py",
    "scratch/WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01/candidate_review_packet.md",
    "scratch/WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01/candidate_lifecycle_report.json",
)


class CandidateReviewPacketError(ValueError):
    """Raised when source packets cannot safely support candidate-review synthesis."""


@dataclass(frozen=True)
class CandidateReviewPacketConfig:
    timestamp_utc: str = "2026-06-22T00:00:00Z"

    def __post_init__(self) -> None:
        if not self.timestamp_utc:
            raise ValueError("timestamp_utc is required")


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


class CandidateReviewPacketAgent:
    """ToolContext-routed packet builder with no lifecycle or promotion authority."""

    def __init__(
        self,
        *,
        config: CandidateReviewPacketConfig,
        tool_context: ToolContext,
        repo_root: Path = REPO_ROOT,
    ) -> None:
        if tool_context.role != ROLE or tool_context.wp_id != WP_ID:
            raise ValueError("CandidateReviewPacketAgent requires its exact role and WP")
        self.config = config
        self.tool_context = tool_context
        self.repo_root = repo_root.resolve()

    def _repo_relative(self, path: Path | str) -> str:
        candidate = Path(path)
        if candidate.is_absolute():
            try:
                candidate = candidate.resolve().relative_to(self.repo_root)
            except ValueError as exc:
                raise CandidateReviewPacketError("path must remain inside the repo") from exc
        normalized = candidate.as_posix()
        if normalized == ".." or normalized.startswith("../"):
            raise CandidateReviewPacketError("path must remain inside the repo")
        return normalized

    def _read_bytes(self, path: Path | str) -> tuple[str, bytes, str]:
        relative = self._repo_relative(path)
        content = self.tool_context.run_allowed(
            ToolAction(READ_NON_SECRET, relative),
            lambda: (self.repo_root / relative).read_bytes(),
        )
        return relative, content, _sha256_bytes(content)

    def _read_json(self, path: Path | str) -> tuple[str, dict[str, Any], str]:
        relative, content, digest = self._read_bytes(path)
        try:
            payload = json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise CandidateReviewPacketError(f"invalid JSON: {relative}") from exc
        if not isinstance(payload, dict):
            raise CandidateReviewPacketError(f"JSON root must be an object: {relative}")
        return relative, payload, digest

    def _write_text(self, path: Path, content: str) -> str:
        relative = self._repo_relative(path)

        def operation() -> None:
            target = self.repo_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")

        self.tool_context.run_allowed(ToolAction(WRITE_SCRATCH, relative), operation)
        return relative

    def _write_json(self, path: Path, payload: Mapping[str, Any]) -> str:
        return self._write_text(
            path, json.dumps(payload, indent=2, sort_keys=True) + "\n"
        )

    def _block(self, action_type: str, target_path: str, message: str) -> None:
        self.tool_context.require_allowed(ToolAction(action_type, target_path))
        raise AssertionError(message)

    def _read_lifecycle_helper_refs(self) -> list[dict[str, str]]:
        refs: list[dict[str, str]] = []
        for path in LIFECYCLE_HELPER_PATHS:
            relative, _content, digest = self._read_bytes(path)
            refs.append({"path": relative, "sha256": digest, "role": "read_only_context"})
        return refs

    def _require_approval(
        self,
        approval: Mapping[str, Any],
        *,
        approval_path: str,
        bridge_run_id: str,
        robustness_run_id: str,
    ) -> None:
        valid = (
            approval.get("approved_for_noncanonical_candidate_review_packet") is True
            and approval.get("approved_by") == "operator"
            and approval.get("approval_scope") == APPROVAL_SCOPE
            and isinstance(approval.get("approval_timestamp_utc"), str)
            and bool(approval.get("approval_timestamp_utc"))
            and approval.get("source_bridge_run_id") == bridge_run_id
            and approval.get("source_robustness_run_id") == robustness_run_id
        )
        if not valid:
            self._block(
                "approval_gate_bypass",
                approval_path,
                "invalid candidate-review approval was unexpectedly allowed",
            )

    @staticmethod
    def _require_flags(payload: Mapping[str, Any], *, label: str) -> None:
        if label == "formalizer":
            non_authority = payload.get("non_authority")
            if isinstance(non_authority, Mapping) and non_authority.get("scratch_only"):
                return
        flags = payload.get("non_authority_flags")
        if not isinstance(flags, list):
            raise CandidateReviewPacketError(f"{label} lacks non-authority flags")
        required = set(NON_AUTHORITY_FLAGS) - {"not a trading signal"}
        if label == "bridge":
            required.remove("not ranking authority")
        if not required.issubset(set(flags)):
            raise CandidateReviewPacketError(f"{label} lacks required non-authority flags")

    @staticmethod
    def _status_counts(value: Any) -> dict[str, int] | None:
        if not isinstance(value, Mapping):
            return None
        counts: dict[str, int] = {}
        for status in TRIAL_STATUSES:
            item = value.get(status)
            if not isinstance(item, int) or item < 0:
                return None
            counts[status] = item
        return counts

    def _validate_lineage(
        self,
        *,
        formalizer_path: str,
        formalizer: Mapping[str, Any],
        bridge_path: str,
        bridge: Mapping[str, Any],
        ledger_path: str,
        ledger: Mapping[str, Any],
        robustness_diagnostics_path: str,
        robustness_diagnostics: Mapping[str, Any],
        robustness_review_path: str,
        robustness_review: Mapping[str, Any],
        result_path: str | None,
    ) -> dict[str, Any]:
        formalizer_run_id = formalizer.get("run_id")
        bridge_run_id = bridge.get("run_id")
        robustness_run_id = robustness_review.get("run_id")
        if not all(isinstance(item, str) and item for item in (formalizer_run_id, bridge_run_id)):
            raise CandidateReviewPacketError("formalizer and bridge run IDs are required")
        if ledger.get("run_id") != bridge_run_id:
            raise CandidateReviewPacketError("bridge review and ledger run IDs do not match")
        if robustness_diagnostics.get("source_bridge_run_id") != bridge_run_id:
            raise CandidateReviewPacketError("robustness diagnostics source bridge ID mismatch")
        source_bridge = robustness_review.get("source_bridge_metadata")
        if not isinstance(source_bridge, Mapping) or source_bridge.get("run_id") != bridge_run_id:
            raise CandidateReviewPacketError("robustness review source bridge ID mismatch")
        if robustness_review.get("robustness_diagnostics_path") != robustness_diagnostics_path:
            raise CandidateReviewPacketError("robustness review does not bind diagnostics path")
        if robustness_diagnostics.get("run_id") != robustness_run_id:
            raise CandidateReviewPacketError("robustness diagnostics and review IDs do not match")
        if bridge.get("full_ledger_path") != ledger_path:
            raise CandidateReviewPacketError("bridge review does not bind denominator ledger")
        if result_path is not None and result_path not in bridge.get("runner_artifact_paths", []):
            raise CandidateReviewPacketError("optional runner artifact is not bound by bridge")

        rows = ledger.get("rows")
        if not isinstance(rows, list) or not all(isinstance(row, Mapping) for row in rows):
            raise CandidateReviewPacketError("denominator ledger rows are invalid")
        row_formalizer_ids = {row.get("source_formalizer_run_id") for row in rows}
        row_formalizer_paths = {row.get("source_formalizer_artifact_path") for row in rows}
        if row_formalizer_ids != {formalizer_run_id} or row_formalizer_paths != {formalizer_path}:
            raise CandidateReviewPacketError("formalizer lineage is not preserved in ledger rows")

        bridge_counts = self._status_counts(bridge.get("denominator_counts"))
        ledger_counts = self._status_counts(ledger.get("trial_status_counts"))
        diagnostics_counts = self._status_counts(
            robustness_diagnostics.get("denominator_integrity", {}).get("source_status_counts")
        )
        review_counts = self._status_counts(
            robustness_review.get("denominator_integrity_status", {}).get(
                "source_status_counts"
            )
        )
        computed_counts = {
            status: Counter(row.get("trial_status") for row in rows).get(status, 0)
            for status in TRIAL_STATUSES
        }
        denominator_preserved = (
            bridge_counts is not None
            and bridge_counts == ledger_counts
            and bridge_counts == diagnostics_counts
            and bridge_counts == review_counts
            and bridge_counts == computed_counts
            and ledger.get("declared_trial_count") == len(rows)
            and ledger.get("denominator_preserved") is True
            and sum(bridge_counts.values()) == len(rows)
        )
        if not denominator_preserved:
            self._block(
                "evidence_suppression",
                f"scratch/{WP_ID}/outputs/blocked/candidate_review_packet.json",
                "denominator shrinkage was unexpectedly allowed",
            )
        return {
            "status": "passed",
            "source_formalizer_run_id": formalizer_run_id,
            "source_bridge_run_id": bridge_run_id,
            "source_robustness_run_id": robustness_run_id,
            "denominator_counts": bridge_counts,
            "ledger_row_count": len(rows),
            "all_source_rows_preserved": True,
            "result_artifact_bound": result_path is None or result_path in bridge.get(
                "runner_artifact_paths", []
            ),
        }

    @staticmethod
    def _diagnostic_gap_summary(
        robustness_review: Mapping[str, Any], robustness_diagnostics: Mapping[str, Any]
    ) -> dict[str, Any]:
        skipped = robustness_review.get("diagnostics_skipped", [])
        if not isinstance(skipped, list):
            skipped = []
        missing = {
            "per_trade": robustness_review.get("per_trade_status"),
            "oos_walkforward": robustness_review.get("oos_walkforward_status"),
            "funding_stress": robustness_review.get("funding_stress_status"),
        }
        gaps: list[str] = []
        per_trade = missing["per_trade"]
        if isinstance(per_trade, Mapping) and per_trade.get("fabricated_per_trade_data") is False:
            gaps.append("needs real trade rows for per-trade diagnostics")
        oos = missing["oos_walkforward"]
        if isinstance(oos, Mapping) and oos.get("status") == "missing_fold_inputs":
            gaps.append("needs fold/OOS inputs for walk-forward diagnostics")
        funding = missing["funding_stress"]
        if isinstance(funding, Mapping) and funding.get("status") == "not_applicable_funding_mode_off":
            gaps.append("needs separately authorized funding-on test before funding stress")
        metric_skips = robustness_diagnostics.get("metric_diagnostics_skipped", [])
        if isinstance(metric_skips, list):
            gaps.extend(
                f"metric diagnostic skipped: {item.get('metric') or item.get('reason')}"
                for item in metric_skips
                if isinstance(item, Mapping)
            )
        return {
            "diagnostics_completed": list(robustness_review.get("diagnostics_completed", [])),
            "diagnostics_skipped": skipped,
            "missing_diagnostic_inputs": missing,
            "evidence_gaps": list(dict.fromkeys(item for item in gaps if item)),
        }

    @staticmethod
    def _strategy_summary(
        formalizer: Mapping[str, Any],
        bridge: Mapping[str, Any],
        draft_strategy_spec: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        research_object = formalizer.get("research_object")
        if not isinstance(research_object, Mapping):
            research_object = bridge.get("source_idea_formalizer_summary", {})
        draft_summary = None
        if isinstance(draft_strategy_spec, Mapping):
            draft_summary = {
                "strategy_spec_id": draft_strategy_spec.get("strategy_spec_id"),
                "status": draft_strategy_spec.get("status"),
                "title": draft_strategy_spec.get("title"),
                "primary_timeframe": draft_strategy_spec.get(
                    "timeframe_and_data", {}
                ).get("primary_timeframe")
                if isinstance(draft_strategy_spec.get("timeframe_and_data"), Mapping)
                else None,
            }
        return {
            "strategy_family": "strat-spec-0003-sma-stddev-mean-reversion",
            "idea_summary": research_object.get("summary") if isinstance(research_object, Mapping) else None,
            "symbols": research_object.get("symbols") if isinstance(research_object, Mapping) else None,
            "timeframe": research_object.get("timeframe") if isinstance(research_object, Mapping) else None,
            "features": research_object.get("features") if isinstance(research_object, Mapping) else None,
            "draft_strategy_spec_summary": draft_summary,
        }

    @staticmethod
    def _markdown(packet: Mapping[str, Any]) -> str:
        lines = [
            "# Candidate Review Packet",
            "",
            f"- Run ID: {packet['run_id']}",
            "- Posture: scratch-only, advisory, human-review-required",
            "- Strongest allowed summary: candidate may be worth human review for further evidence",
            "",
            "## Non-Authority Flags",
        ]
        lines.extend(f"- {flag}" for flag in packet["non_authority_flags"])
        lines.extend(
            [
                "",
                "## Sources",
                f"- Formalizer: {packet['source_formalizer']['path']} ({packet['source_formalizer']['sha256']})",
                f"- Bridge packet: {packet['source_bridge']['review_packet_path']} ({packet['source_bridge']['review_packet_sha256']})",
                f"- Denominator ledger: {packet['denominator_snapshot']['ledger_path']} ({packet['denominator_snapshot']['ledger_sha256']})",
                f"- Robustness diagnostics: {packet['source_robustness']['diagnostics_path']} ({packet['source_robustness']['diagnostics_sha256']})",
                f"- Robustness packet: {packet['source_robustness']['review_packet_path']} ({packet['source_robustness']['review_packet_sha256']})",
                "",
                "## Denominator",
            ]
        )
        counts = packet["denominator_snapshot"]["counts"]
        lines.extend(f"- {status}: {counts[status]}" for status in TRIAL_STATUSES)
        lines.extend(
            [
                f"- All source rows preserved: {packet['denominator_snapshot']['all_source_rows_preserved']}",
                "",
                "## Evidence Summary",
                f"- Strategy family: {packet['strategy_summary']['strategy_family']}",
                f"- Idea summary: {packet['strategy_summary']['idea_summary']}",
                f"- Funding mode: {packet['data_and_funding_summary']['funding_mode']}",
                f"- Data warnings: {packet['data_and_funding_summary']['data_availability_warnings'] or ['none']}",
                f"- Data blockers: {packet['data_and_funding_summary']['data_availability_blockers'] or ['none']}",
                "",
                "## Robustness",
            ]
        )
        lines.extend(
            f"- Completed: {item}"
            for item in packet["robustness_summary"]["diagnostics_completed"]
        )
        if not packet["robustness_summary"]["diagnostics_completed"]:
            lines.append("- Completed: none")
        lines.append("- Skipped diagnostics:")
        for item in packet["robustness_summary"]["diagnostics_skipped"] or ["none"]:
            lines.append(f"  - {item}")
        lines.extend(
            [
                "",
                "## Gaps And Follow-Ups",
                "- Evidence gaps:",
            ]
        )
        lines.extend(f"  - {item}" for item in packet["evidence_gaps"] or ["none"])
        lines.append("- Blockers:")
        lines.extend(f"  - {item}" for item in packet["blockers"] or ["none"])
        lines.append("- Recommended human review questions:")
        lines.extend(f"  - {item}" for item in packet["recommended_human_review_questions"])
        lines.append("- Recommended next evidence steps:")
        lines.extend(f"  - {item}" for item in packet["recommended_next_evidence_steps"])
        return "\n".join(lines) + "\n"

    def _build_packet(
        self,
        *,
        run_id: str,
        formalizer_path: str,
        formalizer: Mapping[str, Any],
        formalizer_hash: str,
        draft_path: str | None,
        draft: Mapping[str, Any] | None,
        draft_hash: str | None,
        bridge_path: str,
        bridge: Mapping[str, Any],
        bridge_hash: str,
        ledger_path: str,
        ledger: Mapping[str, Any],
        ledger_hash: str,
        result_path: str | None,
        result_hash: str | None,
        robustness_diagnostics_path: str,
        robustness_diagnostics: Mapping[str, Any],
        robustness_diagnostics_hash: str,
        robustness_review_path: str,
        robustness_review: Mapping[str, Any],
        robustness_review_hash: str,
        approval_path: str,
        approval: Mapping[str, Any],
        approval_hash: str,
        lineage: Mapping[str, Any],
        lifecycle_refs: Sequence[Mapping[str, str]],
    ) -> dict[str, Any]:
        diagnostic_summary = self._diagnostic_gap_summary(
            robustness_review, robustness_diagnostics
        )
        data_warnings = list(bridge.get("data_availability_warnings", []))
        data_blockers = list(bridge.get("data_availability_blockers", []))
        evidence_gaps = list(diagnostic_summary["evidence_gaps"])
        evidence_gaps.extend(data_blockers)
        if result_path is None:
            evidence_gaps.append("optional bridge Result Population artifact path was not supplied")
        blockers = list(data_blockers)
        if bridge.get("validation_status") == "blocked":
            blockers.append("bridge validation status is blocked")
        return {
            "schema_version": "candidate_review_packet_v1",
            "packet_version": PACKET_VERSION,
            "run_id": run_id,
            "created_at_utc": self.config.timestamp_utc,
            "source_formalizer": {
                "path": formalizer_path,
                "sha256": formalizer_hash,
                "run_id": formalizer.get("run_id"),
                "draft_strategy_spec_path": draft_path,
                "draft_strategy_spec_sha256": draft_hash,
            },
            "source_bridge": {
                "review_packet_path": bridge_path,
                "review_packet_sha256": bridge_hash,
                "run_id": bridge.get("run_id"),
                "runner_artifact_path": result_path,
                "runner_artifact_sha256": result_hash,
            },
            "source_robustness": {
                "diagnostics_path": robustness_diagnostics_path,
                "diagnostics_sha256": robustness_diagnostics_hash,
                "review_packet_path": robustness_review_path,
                "review_packet_sha256": robustness_review_hash,
                "run_id": robustness_review.get("run_id"),
            },
            "operator_approval": {
                "path": approval_path,
                "sha256": approval_hash,
                "metadata": copy.deepcopy(dict(approval)),
                "not_candidate_registration": True,
                "not_evidence_approval": True,
                "not_paper_live_approval": True,
            },
            "lineage_consistency": dict(lineage),
            "candidate_lifecycle_context_refs": list(lifecycle_refs),
            "strategy_summary": self._strategy_summary(formalizer, bridge, draft),
            "data_and_funding_summary": {
                "data_availability_warnings": data_warnings,
                "data_availability_blockers": data_blockers,
                "funding_mode": copy.deepcopy(bridge.get("funding_mode")),
                "funding_stress_status": copy.deepcopy(
                    robustness_review.get("funding_stress_status")
                ),
            },
            "denominator_snapshot": {
                "ledger_path": ledger_path,
                "ledger_sha256": ledger_hash,
                "counts": dict(lineage["denominator_counts"]),
                "declared_trial_count": ledger.get("declared_trial_count"),
                "all_source_rows_preserved": True,
                "row_disposition": [
                    {
                        "variant_id": row.get("variant_id"),
                        "trial_status": row.get("trial_status"),
                        "status_reason": row.get("status_reason"),
                    }
                    for row in ledger.get("rows", [])
                ],
            },
            "runner_metrics_summary": {
                "top_metrics": copy.deepcopy(bridge.get("top_metrics")),
                "manual_reconciliation_result": copy.deepcopy(
                    bridge.get("manual_reconciliation_result")
                ),
            },
            "robustness_summary": {
                **diagnostic_summary,
                "bootstrap_mc_summary": copy.deepcopy(
                    robustness_review.get("bootstrap_mc_summary")
                ),
                "parameter_sensitivity_summary": copy.deepcopy(
                    robustness_review.get("parameter_sensitivity_summary")
                ),
            },
            "missing_data_limitations": diagnostic_summary["missing_diagnostic_inputs"],
            "evidence_gaps": list(dict.fromkeys(evidence_gaps)),
            "blockers": list(dict.fromkeys(blockers)),
            "recommended_human_review_questions": [
                "Do the source packets preserve enough lineage for a future lifecycle review?",
                "Are denominator failures, invalid rows, pruned rows, and blocked rows acceptable to investigate further?",
                "Which missing diagnostics must be collected before any future canonical evidence package?",
                "Does the data availability/funding posture require a separate approved package?",
            ],
            "recommended_next_evidence_steps": [
                "collect real trade rows before per-trade diagnostics",
                "collect fold/OOS inputs before walk-forward robustness claims",
                "run funding-on evidence only under a separate approved package",
                "prepare candidate lifecycle review only through a later human-gated path",
            ],
            "allowed_summary_language": (
                "candidate may be worth human review for further evidence"
            ),
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }

    def run(
        self,
        *,
        formalizer_research_object_path: Path | str,
        bridge_review_packet_path: Path | str,
        bridge_denominator_ledger_path: Path | str,
        robustness_diagnostics_path: Path | str,
        robustness_review_packet_path: Path | str,
        operator_candidate_review_approval_path: Path | str,
        formalizer_draft_strategy_spec_path: Path | str | None = None,
        bridge_result_population_artifact_path: Path | str | None = None,
    ) -> dict[str, Any]:
        formalizer_path, formalizer, formalizer_hash = self._read_json(
            formalizer_research_object_path
        )
        bridge_path, bridge, bridge_hash = self._read_json(bridge_review_packet_path)
        ledger_path, ledger, ledger_hash = self._read_json(bridge_denominator_ledger_path)
        diagnostics_path, diagnostics, diagnostics_hash = self._read_json(
            robustness_diagnostics_path
        )
        robustness_path, robustness_review, robustness_hash = self._read_json(
            robustness_review_packet_path
        )
        approval_path, approval, approval_hash = self._read_json(
            operator_candidate_review_approval_path
        )
        draft_path = draft_hash = result_path = result_hash = None
        draft: dict[str, Any] | None = None
        if formalizer_draft_strategy_spec_path is not None:
            draft_path, draft, draft_hash = self._read_json(formalizer_draft_strategy_spec_path)
        if bridge_result_population_artifact_path is not None:
            result_path, _result, result_hash = self._read_json(
                bridge_result_population_artifact_path
            )

        self._require_flags(formalizer, label="formalizer")
        self._require_flags(bridge, label="bridge")
        self._require_flags(robustness_review, label="robustness review")
        lineage = self._validate_lineage(
            formalizer_path=formalizer_path,
            formalizer=formalizer,
            bridge_path=bridge_path,
            bridge=bridge,
            ledger_path=ledger_path,
            ledger=ledger,
            robustness_diagnostics_path=diagnostics_path,
            robustness_diagnostics=diagnostics,
            robustness_review_path=robustness_path,
            robustness_review=robustness_review,
            result_path=result_path,
        )
        self._require_approval(
            approval,
            approval_path=approval_path,
            bridge_run_id=str(lineage["source_bridge_run_id"]),
            robustness_run_id=str(lineage["source_robustness_run_id"]),
        )
        lifecycle_refs = self._read_lifecycle_helper_refs()

        run_identity = {
            "formalizer_hash": formalizer_hash,
            "draft_hash": draft_hash,
            "bridge_hash": bridge_hash,
            "ledger_hash": ledger_hash,
            "result_hash": result_hash,
            "diagnostics_hash": diagnostics_hash,
            "robustness_hash": robustness_hash,
            "approval_hash": approval_hash,
            "config": self.config.__dict__,
            "packet_version": PACKET_VERSION,
        }
        run_id = hashlib.sha256(_canonical_bytes(run_identity)).hexdigest()[:16]
        run_dir = OUTPUT_ROOT / run_id
        json_target = (run_dir / "candidate_review_packet.json").as_posix()
        packet = self.tool_context.run_allowed(
            ToolAction(BUILD_SCRATCH_CANDIDATE_REVIEW_PACKET, json_target),
            lambda: self._build_packet(
                run_id=run_id,
                formalizer_path=formalizer_path,
                formalizer=formalizer,
                formalizer_hash=formalizer_hash,
                draft_path=draft_path,
                draft=draft,
                draft_hash=draft_hash,
                bridge_path=bridge_path,
                bridge=bridge,
                bridge_hash=bridge_hash,
                ledger_path=ledger_path,
                ledger=ledger,
                ledger_hash=ledger_hash,
                result_path=result_path,
                result_hash=result_hash,
                robustness_diagnostics_path=diagnostics_path,
                robustness_diagnostics=diagnostics,
                robustness_diagnostics_hash=diagnostics_hash,
                robustness_review_path=robustness_path,
                robustness_review=robustness_review,
                robustness_review_hash=robustness_hash,
                approval_path=approval_path,
                approval=approval,
                approval_hash=approval_hash,
                lineage=lineage,
                lifecycle_refs=lifecycle_refs,
            ),
        )
        packet_path = self._write_json(run_dir / "candidate_review_packet.json", packet)
        markdown_path = self._write_text(
            run_dir / "candidate_review_packet.md", self._markdown(packet)
        )
        return {
            "run_id": run_id,
            "status": "completed",
            "artifact_paths": {
                "candidate_review_packet_json": packet_path,
                "candidate_review_packet_markdown": markdown_path,
            },
            "source_bridge_run_id": lineage["source_bridge_run_id"],
            "source_robustness_run_id": lineage["source_robustness_run_id"],
            "source_denominator_counts": dict(lineage["denominator_counts"]),
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
