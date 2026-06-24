"""Bridge approved formalizer drafts into scratch-only real offline sweeps."""

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
    RUN_NONCANONICAL_OFFLINE_SWEEP,
    RUN_READ_ONLY_VALIDATION,
    WRITE_SCRATCH,
)
from tools.registry.validate_strategy_specs import validate_strategy_specs
from tools.registry.validate_variant_sweep_artifacts import validate_variant_sweep_artifacts
from tools.research_runner.run_offline_sweep import run_offline_sweep


REPO_ROOT = Path(__file__).resolve().parents[2]
WP_ID = "WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01"
DONCHIAN_ADAPTER_WP_ID = "WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01"
FUNDING_RESEARCH_WP_ID = "WP-RESEARCH-FUNDING-CARRY-02"
ROLE = "formalizer_runner_bridge"
OUTPUT_ROOT = Path("scratch") / WP_ID / "outputs"
FORMALIZER_OUTPUT_PREFIX = "scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/"
DONCHIAN_FORMALIZER_OUTPUT_PREFIX = (
    "scratch/WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01/formalizer/outputs/"
)
FUNDING_FORMALIZER_OUTPUT_PREFIX = "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/"
APPROVAL_SCOPE = "noncanonical_scratch_runner_bridge_only"
BRIDGE_VERSION = "formalizer-runner-bridge-v1"
VARIANT_TEMPLATE_PATH = Path("research/variant_manifests/VM-0003.variant_manifest.json")
SWEEP_TEMPLATE_PATH = Path("research/sweep_plans/SWEEP-PLAN-0003.sweep_plan.json")
STRATEGY_VALIDATOR_PATH = "tools/registry/validate_strategy_specs.py"
VARIANT_SWEEP_VALIDATOR_PATH = "tools/registry/validate_variant_sweep_artifacts.py"
TRIAL_STATUSES = ("completed", "failed", "invalid", "pruned", "blocked")
NON_AUTHORITY_FLAGS = (
    "not canonical",
    "not evidence",
    "not candidate authority",
    "not promotion authority",
    "not paper/live readiness",
    "human review required",
)
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


class FormalizerRunnerBridgeError(ValueError):
    """Raised when bridge inputs cannot safely satisfy the bounded contract."""


@dataclass(frozen=True)
class FormalizerRunnerBridgeConfig:
    ohlcv_input_path: str
    funding_cost_mode: str = "off"
    experiment_scope: str = "full_history_public"
    deterministic_seed: int = 0
    timestamp_utc: str = "2026-06-22T00:00:00Z"

    def __post_init__(self) -> None:
        if self.funding_cost_mode not in {"off", "on"}:
            raise ValueError("funding_cost_mode must be 'off' or 'on'")
        if self.experiment_scope not in {"full_history_public", "limited_noncanonical"}:
            raise ValueError(
                "experiment_scope must be 'full_history_public' or 'limited_noncanonical'"
            )
        if not self.ohlcv_input_path:
            raise ValueError("ohlcv_input_path is required")


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _get_path(payload: Mapping[str, Any], dotted_path: str) -> Any:
    current: Any = payload
    for part in dotted_path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            raise FormalizerRunnerBridgeError(f"manifest hash scope is missing {dotted_path}")
        current = current[part]
    return current


def _refresh_manifest_hash(manifest: dict[str, Any]) -> str:
    pinning = manifest["manifest_hash_pinning"]
    scoped = {path: _get_path(manifest, path) for path in pinning["hash_scope"]}
    digest = _sha256(scoped)
    pinning["manifest_hash"] = digest
    return digest


class FormalizerRunnerBridge:
    """ToolContext-routed bridge for the bounded supported formalizer families."""

    def __init__(
        self,
        *,
        config: FormalizerRunnerBridgeConfig,
        tool_context: ToolContext,
        repo_root: Path = REPO_ROOT,
    ) -> None:
        if tool_context.role != ROLE or tool_context.wp_id not in {
            WP_ID,
            DONCHIAN_ADAPTER_WP_ID,
            FUNDING_RESEARCH_WP_ID,
        }:
            raise ValueError("FormalizerRunnerBridge requires its exact ToolContext role and WP")
        self.config = config
        self.tool_context = tool_context
        self.repo_root = repo_root.resolve()
        self.output_root = Path("scratch") / tool_context.wp_id / "outputs"

    def _repo_relative(self, path: Path | str) -> str:
        candidate = Path(path)
        if candidate.is_absolute():
            try:
                candidate = candidate.resolve().relative_to(self.repo_root)
            except ValueError as exc:
                raise FormalizerRunnerBridgeError("path must remain inside the repo") from exc
        normalized = candidate.as_posix()
        if normalized == ".." or normalized.startswith("../"):
            raise FormalizerRunnerBridgeError("path must remain inside the repo")
        return normalized

    def _read_bytes(self, path: Path | str) -> bytes:
        relative = self._repo_relative(path)
        return self.tool_context.run_allowed(
            ToolAction(READ_NON_SECRET, relative),
            lambda: (self.repo_root / relative).read_bytes(),
        )

    def _read_json(self, path: Path | str) -> dict[str, Any]:
        relative = self._repo_relative(path)
        try:
            payload = json.loads(self._read_bytes(relative))
        except (json.JSONDecodeError, OSError) as exc:
            raise FormalizerRunnerBridgeError(f"cannot read JSON object: {relative}") from exc
        if not isinstance(payload, dict):
            raise FormalizerRunnerBridgeError(f"JSON root must be an object: {relative}")
        return payload

    def _write_json(self, path: Path | str, payload: Mapping[str, Any]) -> str:
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

    def _validate_formalizer_contract(
        self, path: str, payload: Mapping[str, Any]
    ) -> str:
        expected_prefix = {
            DONCHIAN_ADAPTER_WP_ID: DONCHIAN_FORMALIZER_OUTPUT_PREFIX,
            FUNDING_RESEARCH_WP_ID: FUNDING_FORMALIZER_OUTPUT_PREFIX,
        }.get(self.tool_context.wp_id, FORMALIZER_OUTPUT_PREFIX)
        if not path.startswith(expected_prefix) or not path.endswith("/formalized_idea.json"):
            raise FormalizerRunnerBridgeError(
                "formalizer output must be the scoped scratch artifact"
            )
        if payload.get("schema_version") != "agent_formalized_idea_v1":
            raise FormalizerRunnerBridgeError("unsupported formalizer output schema")
        if payload.get("status") != "accepted":
            raise FormalizerRunnerBridgeError("formalizer output must be accepted")
        if not isinstance(payload.get("run_id"), str) or not payload["run_id"]:
            raise FormalizerRunnerBridgeError("formalizer run_id is required")
        research_object = payload.get("research_object")
        if not isinstance(research_object, Mapping):
            raise FormalizerRunnerBridgeError("formalizer research_object is required")
        if research_object.get("symbols") != ["BTCUSDT"] or research_object.get(
            "timeframe"
        ) != "15m":
            raise FormalizerRunnerBridgeError("bridge supports only BTCUSDT 15m")
        features = set(research_object.get("features", []))
        if "funding_rate" in features and not features.intersection({"sma", "stddev", "donchian"}):
            family_id = "funding_rate_positioning_fade_v1"
        elif "donchian" in features and not features.intersection({"sma", "stddev"}):
            family_id = "donchian_channel_breakout_v1"
        elif {"sma", "stddev"}.issubset(features) and "donchian" not in features:
            family_id = "sma_stddev_mean_reversion_v1"
        else:
            raise FormalizerRunnerBridgeError(
                "bridge requires an unambiguous supported formalizer family; "
                "Donchian cannot resolve through the SMA/stddev adapter"
            )
        if (
            self.tool_context.wp_id == DONCHIAN_ADAPTER_WP_ID
            and family_id != "donchian_channel_breakout_v1"
        ):
            raise FormalizerRunnerBridgeError(
                "Donchian adapter WP accepts only donchian_channel_breakout_v1"
            )
        if (
            self.tool_context.wp_id == FUNDING_RESEARCH_WP_ID
            and family_id != "funding_rate_positioning_fade_v1"
        ):
            raise FormalizerRunnerBridgeError(
                "funding research WP accepts only funding_rate_positioning_fade_v1"
            )
        draft = payload.get("draft_strategy_spec")
        if not isinstance(draft, Mapping) or draft.get("produced") is not True or not draft.get(
            "path"
        ):
            raise FormalizerRunnerBridgeError(
                "validated formalizer draft Strategy Spec is required"
            )
        non_authority = payload.get("non_authority")
        if not isinstance(non_authority, Mapping) or not non_authority.get("scratch_only"):
            raise FormalizerRunnerBridgeError("formalizer non-authority contract is missing")
        metadata = payload.get("adapter_metadata")
        if family_id in {"donchian_channel_breakout_v1", "funding_rate_positioning_fade_v1"} and (
            not isinstance(metadata, Mapping) or metadata.get("family_id") != family_id
        ):
            raise FormalizerRunnerBridgeError("family adapter metadata is missing or mismatched")
        return family_id

    def _require_approval(
        self,
        approval: Mapping[str, Any],
        *,
        source_run_id: str,
        approval_path: str,
        formalizer_path: str,
    ) -> None:
        expected_prefix = formalizer_path.rsplit("/", 1)[0] + "/"
        valid = (
            approval_path.startswith(expected_prefix)
            and approval.get("approved_for_noncanonical_runner_bridge") is True
            and approval.get("approved_by") == "operator"
            and approval.get("approval_scope") == APPROVAL_SCOPE
            and isinstance(approval.get("approval_timestamp_utc"), str)
            and bool(approval.get("approval_timestamp_utc"))
            and approval.get("source_formalizer_run_id") == source_run_id
        )
        if self.config.funding_cost_mode == "on":
            valid = valid and approval.get("approved_funding_cost_mode") == "on"
        if valid:
            return
        try:
            self.tool_context.require_allowed(ToolAction("approval_gate_bypass", approval_path))
        except BlockedActionError:
            raise
        raise AssertionError("unapproved bridge was unexpectedly allowed")

    def _validate_draft(self, draft_path: str, *, family_id: str) -> dict[str, Any]:
        expected_prefix = (
            DONCHIAN_FORMALIZER_OUTPUT_PREFIX
            if family_id == "donchian_channel_breakout_v1"
            else FUNDING_FORMALIZER_OUTPUT_PREFIX
            if family_id == "funding_rate_positioning_fade_v1"
            else FORMALIZER_OUTPUT_PREFIX
        )
        if not draft_path.startswith(expected_prefix):
            raise FormalizerRunnerBridgeError(
                "draft Strategy Spec must remain in formalizer scratch"
            )
        draft = self._read_json(draft_path)
        errors = self.tool_context.run_allowed(
            ToolAction(RUN_READ_ONLY_VALIDATION, STRATEGY_VALIDATOR_PATH),
            lambda: validate_strategy_specs(
                strategy_specs_dir=(self.repo_root / draft_path).parent,
                repo_root=self.repo_root,
            ),
        )
        if errors:
            raise FormalizerRunnerBridgeError(
                "draft Strategy Spec validation failed: " + "; ".join(errors)
            )
        constraints = draft.get("provenance", {}).get("source_constraints", [])
        expected_marker = (
            "donchian_channel_breakout_v1 adapter"
            if family_id == "donchian_channel_breakout_v1"
            else "funding_rate_positioning_fade_v1 adapter"
            if family_id == "funding_rate_positioning_fade_v1"
            else "STRAT-SPEC-0003 capability family"
        )
        if not any(expected_marker in str(item) for item in constraints):
            raise FormalizerRunnerBridgeError(
                f"draft does not declare the supported {family_id} adapter"
            )
        serialized = json.dumps(draft, sort_keys=True)
        if family_id == "donchian_channel_breakout_v1":
            if '"ref": "donchian"' not in serialized or any(
                token in serialized for token in ('"ref": "sma"', '"ref": "stddev"')
            ):
                raise FormalizerRunnerBridgeError(
                    "Donchian draft must use only Donchian indicator references"
                )
        elif family_id == "funding_rate_positioning_fade_v1":
            if '"composition_type": "rolling_empirical_percentile_v1"' not in serialized:
                raise FormalizerRunnerBridgeError("funding draft must use rolling empirical percentile")
            if '"ref": "funding_rate"' not in serialized:
                raise FormalizerRunnerBridgeError("funding draft must reference funding_rate")
        return draft

    def _availability_blockers(
        self, formalized: Mapping[str, Any], *, family_id: str
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
            allowed_features = (
                {"donchian", "ohlcv"}
                if family_id == "donchian_channel_breakout_v1"
                else {"funding_rate"}
                if family_id == "funding_rate_positioning_fade_v1"
                else {"sma", "stddev"}
            )
            if feature not in allowed_features:
                blockers.append(
                    f"{feature} is not encoded by the supported {family_id} draft adapter"
                )
            if feature == "taker_buy_sell_ratio" and source == "PUBLIC_TRADE_ARCHIVE_DERIVATION":
                blockers.append(
                    "taker flow requires a distinct referenced archive-derived fixture/source; "
                    "the OHLCV runner fixture is insufficient"
                )
                continue
            constrained = coverage in {
                "PUBLIC_SNAPSHOT_ONLY",
                "RECENT_ONLY_PUBLIC_REST",
                "STREAMING_ONLY_PUBLIC_CAPTURE",
                "STREAMING_ONLY_PUBLIC_WS",
                "VENDOR_ONLY_FOR_HISTORY",
                "UNKNOWN_OR_BLOCKED",
            } or testability in {"vendor_or_capture_constrained", "blocked_unknown"}
            if self.config.experiment_scope == "full_history_public" and constrained:
                blockers.append(
                    f"{feature} cannot run as full-history public data ({coverage or testability})"
                )
            if feature in {"open_interest", "open_interest_value"}:
                blockers.append("open interest cannot be reconstructed from trades")
            if feature == "liquidation_volume":
                blockers.append("liquidation history requires vendor/captured data")
        if self.config.funding_cost_mode == "on":
            blockers.append(
                "real offline runner has no explicit funding-on input; "
                "zero-funding execution cannot be mislabeled"
            )
        return list(dict.fromkeys(blockers))

    def _derive_inputs(
        self,
        *,
        run_id: str,
        run_dir: Path,
        formalized: Mapping[str, Any],
        formalizer_path: str,
        formalizer_hash: str,
        approval_path: str,
        approval_hash: str,
        draft: Mapping[str, Any],
        family_id: str,
        funding_exit_mode: str | None = None,
        numeric_offset: int = 0,
    ) -> dict[str, str]:
        inputs_dir = run_dir / "inputs"
        spec = copy.deepcopy(dict(draft))
        spec_id = str(spec["strategy_spec_id"])
        spec_path = (inputs_dir / f"{spec_id}.strategy_spec.json").as_posix()
        spec_hash = _sha256(spec)

        manifest = copy.deepcopy(self._read_json(VARIANT_TEMPLATE_PATH))
        numeric_id = 9000 + ((int(run_id[:8], 16) + numeric_offset) % 1000)
        manifest_id = f"VM-{numeric_id:04d}"
        manifest_path = (inputs_dir / f"{manifest_id}.variant_manifest.json").as_posix()
        manifest["variant_manifest_id"] = manifest_id
        manifest["parent_strategy_spec"].update(
            {
                "strategy_spec_id": spec_id,
                "strategy_spec_hash": spec_hash,
                "strategy_spec_ref": spec_path,
            }
        )
        manifest["manifest_hash_pinning"]["frozen_at"] = self.config.timestamp_utc
        manifest["lineage"].update(
            {
                "parent_refs": [
                    {
                        "ref_type": "strategy_spec",
                        "ref_id": spec_id,
                        "ref_path": spec_path,
                        "ref_hash": spec_hash,
                    }
                ],
                "source_refs": [
                    {
                        "ref_type": "concept",
                        "ref_id": f"FORMALIZER-{formalized['run_id']}",
                        "ref_path": formalizer_path,
                        "ref_hash": formalizer_hash,
                    },
                    {
                        "ref_type": "manual_review",
                        "ref_id": "OPERATOR-BRIDGE-APPROVAL",
                        "ref_path": approval_path,
                        "ref_hash": approval_hash,
                    },
                ],
                "created_at": self.config.timestamp_utc,
                "updated_at": self.config.timestamp_utc,
                "audit_notes": [
                    "Scratch-only compatibility copy of merged VM-0003 semantics.",
                    "frozen_for_sweep_planning is required by the runner contract "
                    "and grants no canonical freeze authority.",
                    "Human approval is scoped only to this non-canonical scratch bridge run.",
                ],
                "hash_refs": [spec_hash, formalizer_hash, approval_hash],
            }
        )
        manifest["review"].update(
            {
                "reviewer": None,
                "reviewed_at": None,
                "review_notes": [
                    "Scratch-only runner compatibility artifact; not canonical approval or freeze.",
                    "Human review remains required after execution.",
                ],
                "approval_scope": "sweep_planning_only",
            }
        )
        if family_id == "donchian_channel_breakout_v1":
            self._apply_donchian_manifest(manifest)
        elif family_id == "funding_rate_positioning_fade_v1":
            if funding_exit_mode is None:
                raise FormalizerRunnerBridgeError("funding exit mode is required")
            self._apply_funding_manifest(
                manifest,
                exit_mode=funding_exit_mode,
                variant_start=1 if funding_exit_mode == "midline_reversion_or_max_hold" else 19,
            )
        manifest_hash = _refresh_manifest_hash(manifest)

        sweep = copy.deepcopy(self._read_json(SWEEP_TEMPLATE_PATH))
        sweep_id = f"SWEEP-PLAN-{numeric_id:04d}"
        sweep_path = (inputs_dir / f"{sweep_id}.sweep_plan.json").as_posix()
        sweep["sweep_plan_id"] = sweep_id
        sweep["parent_variant_manifest"].update(
            {"variant_manifest_id": manifest_id, "manifest_hash": manifest_hash}
        )
        sweep["lineage"].update(
            {
                "parent_manifest_ref": {
                    "ref_type": "variant_manifest",
                    "ref_id": manifest_id,
                    "ref_path": manifest_path,
                    "ref_hash": manifest_hash,
                },
                "parent_strategy_spec_ref": {
                    "ref_type": "strategy_spec",
                    "ref_id": spec_id,
                    "ref_path": spec_path,
                    "ref_hash": spec_hash,
                },
                "source_refs": [
                    {
                        "ref_type": "other",
                        "ref_id": f"FORMALIZER-{formalized['run_id']}",
                        "ref_path": formalizer_path,
                        "ref_hash": formalizer_hash,
                    },
                    {
                        "ref_type": "manual_review",
                        "ref_id": "OPERATOR-BRIDGE-APPROVAL",
                        "ref_path": approval_path,
                        "ref_hash": approval_hash,
                    },
                ],
                "created_at": self.config.timestamp_utc,
                "updated_at": self.config.timestamp_utc,
                "audit_notes": [
                    "Scratch-only compatibility copy of merged SWEEP-PLAN-0003 semantics.",
                    "This artifact grants no canonical sweep, evidence, or execution authority.",
                ],
            }
        )
        sweep["review"].update(
            {
                "reviewer": None,
                "reviewed_at": None,
                "review_notes": [
                    "Scratch-only runner compatibility artifact; not canonical approval.",
                    "Human review remains required after execution.",
                ],
                "approval_scope": "offline_run_planning_only",
            }
        )
        if family_id == "donchian_channel_breakout_v1":
            self._apply_donchian_sweep(sweep)
        elif family_id == "funding_rate_positioning_fade_v1":
            if funding_exit_mode is None:
                raise FormalizerRunnerBridgeError("funding exit mode is required")
            self._apply_funding_sweep(
                sweep,
                exit_mode=funding_exit_mode,
                variant_start=1 if funding_exit_mode == "midline_reversion_or_max_hold" else 19,
            )

        written = {
            "strategy_spec": self._write_json(spec_path, spec),
            "variant_manifest": self._write_json(manifest_path, manifest),
            "sweep_plan": self._write_json(sweep_path, sweep),
        }
        metadata = {
            "schema_version": "formalizer_runner_bridge_input_metadata_v1",
            "source_formalizer_run_id": formalized["run_id"],
            "source_formalized_idea_path": formalizer_path,
            "source_draft_strategy_spec_path": formalized["draft_strategy_spec"]["path"],
            "approval_marker_path": approval_path,
            "approval_marker_hash": approval_hash,
            "bridge_tool_version": BRIDGE_VERSION,
            "strategy_family": family_id,
            "funding_exit_mode": funding_exit_mode,
            "created_at_utc": self.config.timestamp_utc,
            "funding_cost_mode": self.config.funding_cost_mode,
            "data_assumptions": {
                "experiment_scope": self.config.experiment_scope,
                "ohlcv_input_path": self.config.ohlcv_input_path,
                "runner_mode": "canonical_15m_fixture_offline",
            },
            "compatibility_status_not_authority": True,
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
        written["bridge_metadata"] = self._write_json(inputs_dir / "bridge_metadata.json", metadata)
        return written

    @staticmethod
    def _apply_donchian_manifest(manifest: dict[str, Any]) -> None:
        population = manifest["population_governance"]
        population["population_cap"]["max_variants"] = 2
        population["declared_population"].update(
            {
                "committed_population_count": 2,
                "declared_variant_count": 2,
                "included_variant_count": 2,
                "excluded_variant_count": 0,
                "invalid_variant_count": 0,
                "not_attempted_variant_count": 0,
            }
        )
        population["trial_budget"].update(
            {
                "planned_trial_count": 2,
                "trial_budget_denominator": 2,
                "denominator_count": 2,
            }
        )
        population["multiple_testing_accounting"].update(
            {
                "search_family_id": "SF-DONCHIAN-CHANNEL-BREAKOUT-15M-SCRATCH-0001",
                "search_family_method": "manual_grid",
                "adaptive_search_used": False,
            }
        )
        manifest["parameter_axes"] = [
            {
                "axis_id": "AXIS-001",
                "parameter_name": "channel_lookback_bars",
                "parent_strategy_spec_parameter_ref": (
                    "free_parameters.parameters.channel_lookback_bars"
                ),
                "parameter_type": "integer",
                "units": "bars",
                "axis_kind": "free_parameter",
                "generator_method": "manual_grid",
                "allowed_values": [20, 55],
                "range": {
                    "min": 20,
                    "max": 55,
                    "step": 35,
                    "inclusive_min": True,
                    "inclusive_max": True,
                },
                "counts_toward_parent_free_parameter_cap": True,
                "is_declared_in_parent_strategy_spec": True,
                "invalid_combination_rule_refs": [],
                "notes": "Bounded non-adaptive Donchian adapter validation grid [20, 55].",
            }
        ]
        manifest["invalid_combination_rules"] = []
        manifest["exclusion_rules"] = []
        manifest["variant_assignments"] = []
        for index, value in enumerate((20, 55), start=1):
            parameter_values = {"channel_lookback_bars": value}
            manifest["variant_assignments"].append(
                {
                    "variant_id": f"VAR-{index:06d}",
                    "assignment_status": "included",
                    "parameter_values": parameter_values,
                    "parameter_value_hash": _sha256(parameter_values),
                    "axis_refs": ["AXIS-001"],
                    "exclusion_rule_refs": [],
                    "invalid_combination_rule_refs": [],
                    "status_reason": None,
                    "lineage": {
                        "generated_by_rule": "manual-grid",
                        "generation_order": index,
                    },
                }
            )
        manifest["lineage"]["audit_notes"] = [
            "Scratch-only Donchian channel-breakout manual grid [20, 55].",
            "No post-hoc narrowing, canonical freeze, or research conclusion authority.",
            "All included, failed, invalid, excluded, and blocked rows remain in the denominator.",
        ]
        manifest["review"]["review_notes"] = [
            "Scratch-only Donchian runner compatibility artifact; not canonical approval or freeze.",
            "Prior Donchian evidence exists in REP-0003 and REP-0032; no novelty is claimed.",
        ]

    @staticmethod
    def _apply_donchian_sweep(sweep: dict[str, Any]) -> None:
        sweep["parent_variant_manifest"].update(
            {
                "manifest_population_count": 2,
                "manifest_committed_population_count": 2,
                "manifest_population_cap": 2,
            }
        )
        sweep["test_selection"].update(
            {
                "selected_variant_ids": ["VAR-000001", "VAR-000002"],
                "excluded_variant_ids": [],
            }
        )
        sweep["validation_methods"]["backtest"]["notes"] = (
            "Scratch-only real offline runner smoke for the Donchian adapter."
        )
        sweep["realism_assumptions"]["order_size_assumption"] = (
            "Scratch offline runner validation uses dynamic_equity_target_leverage at "
            "target_leverage=1.0; no runtime or canonical authority."
        )
        sweep["validation_methods"]["dsr_psr_mintrl_accounting"].update(
            {
                "denominator_ref": "committed_population_count",
                "computation_deferred": True,
                "notes": (
                    "Denominator is the full bounded scratch population of 2; "
                    "no research conclusion."
                ),
            }
        )
        sweep["trial_accounting"].update(
            {
                "committed_population_count": 2,
                "selected_variant_count": 2,
                "executed_variant_count": 0,
                "successful_variant_count": 0,
                "failed_variant_count": 0,
                "errored_variant_count": 0,
                "aborted_variant_count": 0,
                "filtered_variant_count": 0,
                "data_unavailable_variant_count": 0,
                "excluded_variant_count": 0,
                "not_attempted_variant_count": 2,
                "multiple_testing_denominator": 2,
            }
        )
        sweep["lineage"]["search_family_id"] = (
            "SF-DONCHIAN-CHANNEL-BREAKOUT-15M-SCRATCH-0001"
        )
        sweep["lineage"]["audit_notes"] = [
            "Scratch-only Donchian adapter smoke; no canonical sweep or evidence authority.",
            "The full two-row denominator is retained regardless of runner outcome.",
        ]
        sweep["review"]["review_notes"] = [
            "Scratch-only Donchian runner compatibility artifact; not canonical approval.",
            "Metrics, if produced, are adapter validation only and carry no GO/NO-GO meaning.",
        ]

    @staticmethod
    def _apply_funding_manifest(
        manifest: dict[str, Any], *, exit_mode: str, variant_start: int
    ) -> None:
        count = 18
        population = manifest["population_governance"]
        population["population_cap"]["max_variants"] = count
        population["declared_population"].update(
            {
                "committed_population_count": count,
                "declared_variant_count": count,
                "included_variant_count": count,
                "excluded_variant_count": 0,
                "invalid_variant_count": 0,
                "not_attempted_variant_count": 0,
            }
        )
        population["trial_budget"].update(
            {
                "planned_trial_count": count,
                "trial_budget_denominator": count,
                "denominator_count": count,
            }
        )
        population["multiple_testing_accounting"].update(
            {
                "search_family_id": f"SF-FUNDING-POSITIONING-FADE-{exit_mode.upper()}-0001",
                "search_family_method": "manual_grid",
                "adaptive_search_used": False,
            }
        )
        axes = (
            ("funding_lookback_bars", "integer", "bars", [2880, 8640, 17280]),
            ("lower_entry_percentile", "number", "ratio", [0.05, 0.10]),
            ("upper_entry_percentile", "number", "ratio", [0.90, 0.95]),
            ("max_hold_bars", "integer", "bars", [16, 32, 96]),
        )
        manifest["parameter_axes"] = []
        for index, (name, parameter_type, units, values) in enumerate(axes, start=1):
            numeric = [float(value) for value in values]
            manifest["parameter_axes"].append(
                {
                    "axis_id": f"AXIS-{index:03d}",
                    "parameter_name": name,
                    "parent_strategy_spec_parameter_ref": f"free_parameters.parameters.{name}",
                    "parameter_type": parameter_type,
                    "units": units,
                    "axis_kind": "free_parameter",
                    "generator_method": "manual_grid",
                    "allowed_values": values,
                    "range": {
                        "min": min(values),
                        "max": max(values),
                        "step": min(b - a for a, b in zip(numeric, numeric[1:])),
                        "inclusive_min": True,
                        "inclusive_max": True,
                    },
                    "counts_toward_parent_free_parameter_cap": True,
                    "is_declared_in_parent_strategy_spec": True,
                    "invalid_combination_rule_refs": [],
                    "notes": "Frozen H-FUNDING-RATE-POSITIONING-FADE-01 axis.",
                }
            )
        manifest["invalid_combination_rules"] = []
        manifest["exclusion_rules"] = []
        manifest["variant_assignments"] = []
        generation_order = 0
        for lookback in (2880, 8640, 17280):
            for lower, upper in ((0.10, 0.90), (0.05, 0.95)):
                for max_hold in (16, 32, 96):
                    generation_order += 1
                    values = {
                        "funding_lookback_bars": lookback,
                        "lower_entry_percentile": lower,
                        "upper_entry_percentile": upper,
                        "max_hold_bars": max_hold,
                    }
                    manifest["variant_assignments"].append(
                        {
                            "variant_id": f"VAR-{variant_start + generation_order - 1:06d}",
                            "assignment_status": "included",
                            "parameter_values": values,
                            "parameter_value_hash": _sha256(values),
                            "axis_refs": ["AXIS-001", "AXIS-002", "AXIS-003", "AXIS-004"],
                            "exclusion_rule_refs": [],
                            "invalid_combination_rule_refs": [],
                            "status_reason": None,
                            "lineage": {
                                "generated_by_rule": "frozen-manual-grid",
                                "generation_order": generation_order,
                            },
                        }
                    )
        manifest["lineage"]["audit_notes"] = [
            f"Scratch-only funding positioning-fade exit_mode={exit_mode}.",
            "Entry-tail pairs are frozen as 0.10/0.90 and 0.05/0.95.",
            "Funding payments remain off; price-P&L funding-rate signal test only.",
            "All denominator outcomes remain visible.",
        ]
        manifest["review"]["review_notes"] = [
            "Non-canonical preregistered funding-family research input.",
            "No crossing, candidate, promotion, paper, live, or runtime authority.",
        ]

    @staticmethod
    def _apply_funding_sweep(
        sweep: dict[str, Any], *, exit_mode: str, variant_start: int
    ) -> None:
        count = 18
        variant_ids = [f"VAR-{value:06d}" for value in range(variant_start, variant_start + count)]
        sweep["parent_variant_manifest"].update(
            {
                "manifest_population_count": count,
                "manifest_committed_population_count": count,
                "manifest_population_cap": count,
            }
        )
        sweep["test_selection"].update(
            {"selected_variant_ids": variant_ids, "excluded_variant_ids": []}
        )
        sweep["validation_methods"]["backtest"]["notes"] = (
            f"Price-P&L funding-rate signal test; exit_mode={exit_mode}; costs enabled by runner convention."
        )
        sweep["validation_methods"]["dsr_psr_mintrl_accounting"].update(
            {
                "denominator_ref": "committed_population_count",
                "computation_deferred": True,
                "notes": "One frozen 18-row half of the combined 36-row funding denominator.",
            }
        )
        sweep["trial_accounting"].update(
            {
                "committed_population_count": count,
                "selected_variant_count": count,
                "executed_variant_count": 0,
                "successful_variant_count": 0,
                "failed_variant_count": 0,
                "errored_variant_count": 0,
                "aborted_variant_count": 0,
                "filtered_variant_count": 0,
                "data_unavailable_variant_count": 0,
                "excluded_variant_count": 0,
                "not_attempted_variant_count": count,
                "multiple_testing_denominator": count,
            }
        )
        sweep["lineage"]["search_family_id"] = (
            f"SF-FUNDING-POSITIONING-FADE-{exit_mode.upper()}-0001"
        )
        sweep["lineage"]["audit_notes"] = [
            "Scratch-only, non-canonical funding research sweep.",
            "Funding P&L is not wired; funding_cost_mode remains off.",
            "Combined family denominator is 36 across the two frozen exit modes.",
        ]
        sweep["review"]["review_notes"] = [
            "Human review required; no candidate or crossing authority.",
        ]

    def _validate_derived_inputs(self, paths: Mapping[str, str]) -> None:
        inputs_dir = (self.repo_root / paths["strategy_spec"]).parent
        strategy_errors = self.tool_context.run_allowed(
            ToolAction(RUN_READ_ONLY_VALIDATION, STRATEGY_VALIDATOR_PATH),
            lambda: validate_strategy_specs(
                strategy_specs_dir=inputs_dir,
                repo_root=self.repo_root,
            ),
        )
        variant_errors = self.tool_context.run_allowed(
            ToolAction(RUN_READ_ONLY_VALIDATION, VARIANT_SWEEP_VALIDATOR_PATH),
            lambda: validate_variant_sweep_artifacts(
                variant_manifests_dir=inputs_dir,
                sweep_plans_dir=inputs_dir,
                strategy_specs_dir=inputs_dir,
            ),
        )
        errors = [*strategy_errors, *variant_errors]
        if errors:
            raise FormalizerRunnerBridgeError(
                "derived input validation failed: " + "; ".join(errors)
            )

    def _invoke_runner(
        self,
        *,
        run_dir: Path,
        input_paths: Mapping[str, str],
        ohlcv_path: str,
        write_result_population: bool,
        invocation_name: str,
    ) -> dict[str, Any]:
        target = (run_dir / "runner_artifacts" / invocation_name).as_posix()

        def operation() -> dict[str, Any]:
            return run_offline_sweep(
                self.repo_root / input_paths["strategy_spec"],
                self.repo_root / input_paths["variant_manifest"],
                self.repo_root / input_paths["sweep_plan"],
                self.repo_root / run_dir / "runner_artifacts",
                write_result_population=write_result_population,
                run_label=invocation_name,
                deterministic_seed=self.config.deterministic_seed,
                canonical_15m=True,
                ohlcv_input_path=self.repo_root / ohlcv_path,
            )

        return self.tool_context.run_allowed(
            ToolAction(
                RUN_NONCANONICAL_OFFLINE_SWEEP,
                target,
                metadata={"network": False, "scratch_only": True},
            ),
            operation,
        )

    @staticmethod
    def _reconcile(bridged: Mapping[str, Any], direct: Mapping[str, Any]) -> dict[str, Any]:
        bridged_rows = bridged["result_population"]["variant_result_rows"]
        direct_rows = direct["result_population"]["variant_result_rows"]
        comparisons = {
            "trial_count": len(bridged_rows) == len(direct_rows),
            "variant_ids": [row["variant_id"] for row in bridged_rows]
            == [row["variant_id"] for row in direct_rows],
            "outcomes": [row["outcome_category"] for row in bridged_rows]
            == [row["outcome_category"] for row in direct_rows],
            "core_metrics": [row["metrics"] for row in bridged_rows]
            == [row["metrics"] for row in direct_rows],
            "status_counts": bridged["outcome_category_counts"]
            == direct["outcome_category_counts"],
            "committed_denominator": bridged["committed_denominator"]
            == direct["committed_denominator"],
            "result_identity": bridged["result_population"]["result_population_identity_hash"]
            == direct["result_population"]["result_population_identity_hash"],
        }
        return {"passed": all(comparisons.values()), "comparisons": comparisons}

    @staticmethod
    def _ledger_rows(
        *,
        run_id: str,
        runner_invocation_id: str,
        formalizer_run_id: str,
        formalizer_path: str,
        approval_scope: str,
        input_paths: Mapping[str, str],
        manifest: Mapping[str, Any],
        runner_result: Mapping[str, Any] | None,
        runner_artifact_path: str | None,
        blockers: Sequence[str],
        funding_cost_mode: str,
        timestamp_utc: str,
        strategy_family: str = "sma_stddev_mean_reversion_v1",
    ) -> list[dict[str, Any]]:
        variants = {row["variant_id"]: row for row in manifest["variant_assignments"]}
        if runner_result is None:
            source_rows = [
                {
                    "variant_id": variant_id,
                    "outcome_category": "not_attempted",
                    "non_success": {"reason": "; ".join(blockers)},
                    "metrics": None,
                    "row_identity_hash": None,
                }
                for variant_id in sorted(variants)
            ]
        else:
            source_rows = runner_result["result_population"]["variant_result_rows"]
        rows: list[dict[str, Any]] = []
        for index, runner_row in enumerate(source_rows, start=1):
            variant = variants[runner_row["variant_id"]]
            outcome = runner_row["outcome_category"]
            trial_status = RUNNER_OUTCOME_TO_TRIAL_STATUS[outcome]
            metrics = runner_row.get("metrics") if trial_status == "completed" else None
            reason = runner_row.get("non_success", {}).get("reason") or f"runner {outcome}"
            rows.append(
                {
                    "run_id": run_id,
                    "source_formalizer_run_id": formalizer_run_id,
                    "source_formalizer_artifact_path": formalizer_path,
                    "approval_scope": approval_scope,
                    "bridge_input_paths": dict(input_paths),
                    "runner_invocation_id": runner_invocation_id,
                    "strategy_family": strategy_family,
                    "variant_id": runner_row["variant_id"],
                    "trial_id": f"{run_id}-TRIAL-{index:03d}",
                    "trial_status": trial_status,
                    "status_reason": reason,
                    "runner_outcome_category": outcome,
                    "params": copy.deepcopy(variant["parameter_values"]),
                    "funding_cost_mode": funding_cost_mode,
                    "input_hash": _sha256(variant),
                    "output_hash": runner_row.get("row_identity_hash"),
                    "metrics_summary": metrics,
                    "runner_artifact_path": runner_artifact_path,
                    "started_at_utc": timestamp_utc,
                    "finished_at_utc": timestamp_utc,
                    "non_authority_flags": list(NON_AUTHORITY_FLAGS),
                }
            )
        return rows

    def _assert_denominator(
        self,
        rows: Sequence[Mapping[str, Any]],
        manifest: Mapping[str, Any],
        *,
        target_path: str,
    ) -> None:
        expected = {row["variant_id"] for row in manifest["variant_assignments"]}
        actual = {row.get("variant_id") for row in rows}
        if actual != expected or len(rows) != len(expected):
            self.tool_context.require_allowed(ToolAction("evidence_suppression", target_path))
            raise AssertionError("denominator suppression was unexpectedly allowed")
        if any(row.get("trial_status") not in TRIAL_STATUSES for row in rows):
            raise FormalizerRunnerBridgeError("denominator ledger contains an unsupported status")

    def run(
        self,
        *,
        formalizer_output_path: Path | str,
        approval_path: Path | str,
    ) -> dict[str, Any]:
        formalizer_path = self._repo_relative(formalizer_output_path)
        approval_relative = self._repo_relative(approval_path)
        formalizer_bytes = self._read_bytes(formalizer_path)
        formalized = json.loads(formalizer_bytes)
        family_id = self._validate_formalizer_contract(formalizer_path, formalized)
        approval_bytes = self._read_bytes(approval_relative)
        approval = json.loads(approval_bytes)
        if not isinstance(approval, dict):
            raise FormalizerRunnerBridgeError("approval marker must be a JSON object")
        self._require_approval(
            approval,
            source_run_id=formalized["run_id"],
            approval_path=approval_relative,
            formalizer_path=formalizer_path,
        )
        draft_paths: dict[str, str] = {
            "default": str(formalized["draft_strategy_spec"]["path"])
        }
        if family_id == "funding_rate_positioning_fade_v1":
            metadata = formalized.get("adapter_metadata")
            declared_paths = metadata.get("strategy_spec_paths") if isinstance(metadata, Mapping) else None
            expected_modes = {"midline_reversion_or_max_hold", "fixed_max_hold_only"}
            if not isinstance(declared_paths, Mapping) or set(declared_paths) != expected_modes:
                raise FormalizerRunnerBridgeError("funding adapter must declare both frozen exit-mode specs")
            draft_paths = {str(mode): str(path) for mode, path in declared_paths.items()}
        drafts = {
            mode: self._validate_draft(path, family_id=family_id)
            for mode, path in draft_paths.items()
        }
        ohlcv_path = self._repo_relative(self.config.ohlcv_input_path)
        ohlcv_hash = _sha256_bytes(self._read_bytes(ohlcv_path))

        run_identity = {
            "formalizer_hash": _sha256_bytes(formalizer_bytes),
            "approval_hash": _sha256_bytes(approval_bytes),
            "draft_hashes": {mode: _sha256(draft) for mode, draft in drafts.items()},
            "ohlcv_hash": ohlcv_hash,
            "config": self.config.__dict__,
            "bridge_version": BRIDGE_VERSION,
        }
        run_id = hashlib.sha256(_canonical_bytes(run_identity)).hexdigest()[:16]
        run_dir = self.output_root / run_id
        blockers = self._availability_blockers(formalized, family_id=family_id)
        if blockers:
            record = self.tool_context.authorize(
                ToolAction("data_availability_bypass", formalizer_path)
            )
            if record.decision != "blocked":
                raise AssertionError("data-availability bypass was unexpectedly allowed")
        all_input_paths: dict[str, dict[str, str]] = {}
        runner_artifact_paths: dict[str, str] = {}
        reconciliations: dict[str, dict[str, Any]] = {}
        ledger_rows: list[dict[str, Any]] = []
        runner_invocation_ids: dict[str, str] = {}
        for index, (mode, draft) in enumerate(drafts.items()):
            mode_dir = run_dir if mode == "default" else run_dir / mode
            input_paths = self._derive_inputs(
                run_id=run_id,
                run_dir=mode_dir,
                formalized=formalized,
                formalizer_path=formalizer_path,
                formalizer_hash=run_identity["formalizer_hash"],
                approval_path=approval_relative,
                approval_hash=run_identity["approval_hash"],
                draft=draft,
                family_id=family_id,
                funding_exit_mode=None if mode == "default" else mode,
                numeric_offset=index,
            )
            self._validate_derived_inputs(input_paths)
            all_input_paths[mode] = input_paths
            manifest = self._read_json(input_paths["variant_manifest"])
            runner_invocation_id = hashlib.sha256(
                _canonical_bytes(
                    {"run_id": run_id, "mode": mode, "inputs": input_paths, "seed": self.config.deterministic_seed}
                )
            ).hexdigest()[:16]
            runner_invocation_ids[mode] = runner_invocation_id
            runner_result: dict[str, Any] | None = None
            runner_artifact_path: str | None = None
            reconciliation: dict[str, Any] = {"passed": False, "not_run_reasons": blockers}
            if not blockers:
                runner_result = self._invoke_runner(
                    run_dir=mode_dir,
                    input_paths=input_paths,
                    ohlcv_path=ohlcv_path,
                    write_result_population=True,
                    invocation_name="bridged",
                )
                direct_result = self._invoke_runner(
                    run_dir=mode_dir,
                    input_paths=input_paths,
                    ohlcv_path=ohlcv_path,
                    write_result_population=False,
                    invocation_name="direct-manual-equivalent",
                )
                reconciliation = self._reconcile(runner_result, direct_result)
                if not reconciliation["passed"]:
                    raise FormalizerRunnerBridgeError(f"manual runner reconciliation failed for {mode}")
                runner_artifact_path = self._repo_relative(str(runner_result["output_path"]))
                runner_artifact_paths[mode] = runner_artifact_path
            reconciliations[mode] = reconciliation
            mode_rows = self._ledger_rows(
                run_id=run_id,
                runner_invocation_id=runner_invocation_id,
                formalizer_run_id=formalized["run_id"],
                formalizer_path=formalizer_path,
                approval_scope=approval["approval_scope"],
                input_paths=input_paths,
                manifest=manifest,
                runner_result=runner_result,
                runner_artifact_path=runner_artifact_path,
                blockers=blockers,
                funding_cost_mode=self.config.funding_cost_mode,
                timestamp_utc=self.config.timestamp_utc,
                strategy_family=family_id,
            )
            if family_id == "funding_rate_positioning_fade_v1":
                for row in mode_rows:
                    row["exit_mode"] = mode
            self._assert_denominator(
                mode_rows,
                manifest,
                target_path=(mode_dir / "denominator_ledger.json").as_posix(),
            )
            ledger_rows.extend(mode_rows)
        expected_count = 36 if family_id == "funding_rate_positioning_fade_v1" else len(ledger_rows)
        if len(ledger_rows) != expected_count or len({row["variant_id"] for row in ledger_rows}) != expected_count:
            self.tool_context.require_allowed(
                ToolAction("evidence_suppression", (run_dir / "denominator_ledger.json").as_posix())
            )
            raise AssertionError("combined denominator suppression was unexpectedly allowed")
        if family_id == "funding_rate_positioning_fade_v1":
            reconciliation = {
                "passed": bool(reconciliations)
                and all(item.get("passed") for item in reconciliations.values()),
                "by_exit_mode": reconciliations,
            }
            review_input_paths: Mapping[str, Any] = all_input_paths
            invocation_identity: dict[str, Any] = {
                "runner_invocation_ids": runner_invocation_ids
            }
        else:
            reconciliation = reconciliations["default"]
            review_input_paths = all_input_paths["default"]
            invocation_identity = {
                "runner_invocation_id": runner_invocation_ids["default"]
            }
        counts = Counter(row["trial_status"] for row in ledger_rows)
        count_packet = {status: counts.get(status, 0) for status in TRIAL_STATUSES}
        ledger = {
            "schema_version": "formalizer_runner_bridge_denominator_ledger_v1",
            "run_id": run_id,
            "declared_trial_count": len(ledger_rows),
            "denominator_preserved": True,
            "trial_status_counts": count_packet,
            "rows": ledger_rows,
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
        ledger_path = self._write_json(run_dir / "denominator_ledger.json", ledger)
        completed = [row for row in ledger_rows if row["trial_status"] == "completed"]
        review = {
            "schema_version": "formalizer_runner_bridge_human_review_packet_v1",
            "run_id": run_id,
            "source_idea_formalizer_summary": copy.deepcopy(formalized["research_object"]),
            "approval_metadata": copy.deepcopy(approval),
            "derived_input_artifact_paths": review_input_paths,
            "runner_invocation_metadata": {
                "runner": "tools.research_runner.run_offline_sweep",
                **invocation_identity,
                "mode": "canonical_15m_fixture_offline",
                "deterministic_seed": self.config.deterministic_seed,
                "ohlcv_input_path": ohlcv_path,
                "ohlcv_input_hash": ohlcv_hash,
                "network": False,
            },
            "denominator_counts": count_packet,
            "completed_trial_count": count_packet["completed"],
            "failed_trial_count": count_packet["failed"],
            "invalid_trial_count": count_packet["invalid"],
            "pruned_trial_count": count_packet["pruned"],
            "blocked_trial_count": count_packet["blocked"],
            "manual_reconciliation_result": reconciliation,
            "top_metrics": completed[0]["metrics_summary"] if completed else None,
            "full_ledger_path": ledger_path,
            "runner_artifact_paths": list(runner_artifact_paths.values()),
            "validation_status": "blocked" if blockers else "passed",
            "data_availability_blockers": blockers,
            "data_availability_warnings": [],
            "funding_mode": {
                "requested": self.config.funding_cost_mode,
                "effective": "off" if not blockers else "not_run",
                "default_off": True,
                "global_mode_mutated": False,
            },
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
        review_path = self._write_json(run_dir / "human_review_packet.json", review)
        return {
            "run_id": run_id,
            "status": "blocked" if blockers else "completed",
            "trial_status_counts": count_packet,
            "manual_reconciliation_result": reconciliation,
            "artifact_paths": {
                "denominator_ledger": ledger_path,
                "human_review_packet": review_path,
                "runner_result": next(iter(runner_artifact_paths.values()), None),
                "runner_results": runner_artifact_paths,
                "input_sets": all_input_paths,
                **(all_input_paths.get("default") or {}),
            },
            "blockers": blockers,
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
