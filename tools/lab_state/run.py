"""CLI that prints a static, read-only lab coordinator state snapshot.

The CLI binds the committed funding NO-GO / replay / OOS / robustness scratch
artifacts into one subject and prints the resolved snapshot. It performs no
writes, runs no strategy, and executes no transition.

Usage::

    python -m tools.lab_state.run --snapshot            # funding subject (default)
    python -m tools.lab_state.run --snapshot --json
    python -m tools.lab_state.run --list-states
    python -m tools.lab_state.run --subject oos_gate_fail_demo --json
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from tools.lab_state import model
from tools.lab_state.resolver import REPO_ROOT, build_snapshot


def _supplemental(paths: list[str], role: str, note: str) -> list[dict[str, str]]:
    return [{"role": role, "path": path, "note": note} for path in sorted(paths)]


LEGACY_CANONICAL_EVIDENCE_PATHS: list[str] = [
    "research/candidate_registry.jsonl",
    "research/result_populations/RP-2134.result_population.json",
    "research/result_populations/RP-2592.result_population.json",
    "research/result_populations/RP-3731.result_population.json",
    "research/result_populations/RP-4492.result_population.json",
    "research/result_populations/RP-6236.result_population.json",
    "research/result_populations/RP-6688.result_population.json",
    "research/result_populations/RP-7134.result_population.json",
    "research/result_populations/RP-7520.result_population.json",
]

FUNDING_CARRY_01_PATHS: list[str] = [
    "scratch/WP-RESEARCH-FUNDING-CARRY-01/blocked_bridge_reason.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-01/blocked_formalizer_reason.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-01/blocked_robustness_reason.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-01/blocked_rp_replay_harness_reason.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-01/blocked_runner_reason.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-01/denominator_manifest.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-01/funding_family_adapter_contract.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-01/funding_pnl_boundary_note.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-01/main_report_back_guardrail.txt",
    "scratch/WP-RESEARCH-FUNDING-CARRY-01/no_candidate_review_packet_reason.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-01/pre_registered_hypothesis.md",
    "scratch/WP-RESEARCH-FUNDING-CARRY-01/repo_truth_discovery.md",
    "scratch/WP-RESEARCH-FUNDING-CARRY-01/sweep_plan_summary.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-01/validation_summary.txt",
]

FUNDING_CARRY_02_PATHS: list[str] = [
    "scratch/WP-RESEARCH-FUNDING-CARRY-02-FOLLOWUP-01/local_data_staging_report.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02-FOLLOWUP-01/repo_truth_data_contract.md",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02-FOLLOWUP-01/retry_decision.md",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/bridge_output.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/denominator_manifest.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/formalizer_output.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/funding_family_adapter_contract.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/funding_pnl_boundary_note.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/main_report_back_guardrail.txt",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/metrics_summary.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo/fixed/bootstrap_samples.sha256",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo/fixed/seeded_advisory_mc_report.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo/fixed/seeded_advisory_mc_report.md",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo/midline/bootstrap_samples.sha256",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo/midline/seeded_advisory_mc_report.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo/midline/seeded_advisory_mc_report.md",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo_summary.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/no_candidate_review_packet_reason.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/denominator_ledger.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/fixed_max_hold_only/inputs/STRAT-SPEC-9478.strategy_spec.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/fixed_max_hold_only/inputs/SWEEP-PLAN-9933.sweep_plan.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/fixed_max_hold_only/inputs/VM-9933.variant_manifest.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/fixed_max_hold_only/inputs/bridge_metadata.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/fixed_max_hold_only/runner_artifacts/RP-2009.result_population.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/human_review_packet.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/midline_reversion_or_max_hold/inputs/STRAT-SPEC-9477.strategy_spec.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/midline_reversion_or_max_hold/inputs/SWEEP-PLAN-9934.sweep_plan.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/midline_reversion_or_max_hold/inputs/VM-9934.variant_manifest.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/midline_reversion_or_max_hold/inputs/bridge_metadata.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/midline_reversion_or_max_hold/runner_artifacts/RP-7592.result_population.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/b191967d3aff/STRAT-SPEC-9477.strategy_spec.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/b191967d3aff/STRAT-SPEC-9478.strategy_spec.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/b191967d3aff/formalized_idea.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/b191967d3aff/human_review_packet.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/b191967d3aff/operator_bridge_approval.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/pre_registered_hypothesis.md",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/repo_truth_discovery.md",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/robustness_fixed.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/robustness_midline.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/robustness_summary.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/rp_replay_harness_report.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/runner_result_summary.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/sweep_plan_summary.json",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/validation_summary.txt",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/walk_forward_summary.json",
]

FUNDING_FADE_RISKMANAGED_CONCLUDE_PATHS: list[str] = [
    "docs/status_entries/WP-RESEARCH-FUNDING-FADE-RISKMANAGED-CONCLUDE-01.md",
    "docs/status_entries/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01.md",
    "docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md",
    "scratch/WP-RESEARCH-FUNDING-FADE-RISKMANAGED-CONCLUDE-01/conclusion_summary.json",
    "scratch/WP-RESEARCH-FUNDING-FADE-RISKMANAGED-CONCLUDE-01/conclusion_summary.md",
    "scratch/WP-RESEARCH-FUNDING-FADE-RISKMANAGED-CONCLUDE-01/no_retuning_attestation.md",
    "scratch/WP-RESEARCH-FUNDING-FADE-RISKMANAGED-CONCLUDE-01/operator_visibility_binding.json",
    "scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/stage1_verdict.json",
    "scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/stop_go_evaluation.json",
    "scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/row_accounting.json",
    "scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/complete_108_row_denominator.json",
    "scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/complete_108_row_denominator.csv",
    "scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/no_atr_slice_summary.json",
    "scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/atr_20_slice_summary.json",
    "scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/atr_30_slice_summary.json",
]

EDGE_SMA_PATHS: list[str] = [
    "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_bridge_reason.json",
    "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_candidate_review_reason.json",
    "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_robustness_reason.json",
    "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_sweep_plan_reason.json",
    "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_variant_manifest_reason.json",
    "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/denominator_audit.json",
    "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/formalizer_output_reference.json",
    "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/missing_diagnostics.json",
    "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/repo_truth_discovery.md",
    "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/sma_family_research_idea.json",
    "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/sma_family_result_packet.json",
    "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/sma_family_summary.md",
    "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/strategy_spec_reference.json",
]

ORB_EXIT_RESPEC_PATHS: list[str] = [
    "scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/blocked_bridge_reason.json",
    "scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/blocked_candidate_review_reason.json",
    "scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/blocked_robustness_reason.json",
    "scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/denominator_audit.json",
    "scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/formalizer_output_reference.json",
    "scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/missing_diagnostics.json",
    "scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/orb_exit_respec_idea.json",
    "scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/orb_exit_respec_result_packet.json",
    "scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/orb_exit_respec_summary.md",
    "scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/repo_truth_discovery.md",
]

PRICEONLY_SYNTHESIS_PATHS: list[str] = [
    "docs/research/PRICEONLY_SYNTHESIS_2026-06.md",
    "scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/evidence_index.json",
    "scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/lab_gap_checklist.json",
    "scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/main_report_back_guardrail.txt",
    "scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/open_decision_surfaces.txt",
    "scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/priceonly_synthesis_source_audit.json",
    "scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/repo_truth_discovery.md",
    "scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/validation_summary.txt",
]


# Subjects are read-only bindings over already-committed artifacts.
SUBJECTS: dict[str, dict[str, Any]] = {
    # Primary end-to-end binding: funding-rate positioning fade concluded NO-GO.
    "funding_positioning_fade_no_go": {
        "subject_id": "H-FUNDING-RATE-POSITIONING-FADE-01",
        "subject_label": "funding_rate_positioning_fade",
        "oos_from_conclusion": True,
        "review_example_id": "funding_rate_positioning_fade_no_go",
        "artifacts": {
            "formalization": "docs/status_entries/WP-LAB-IDEA-INTAKE-FORMALIZATION-01.md",
            "experiment_run": "scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json",
            "replay_normalization": "scratch/WP-LAB-RP-REPLAY-NORMALIZATION-CONTRACT-01/replay_fixture_summary.json",
            "walkforward_oos_gate": "",
            "candidate_review_reach": "scratch/WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01/generic_review_contract.json",
            "reporting": "docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md",
        },
    },
    # Secondary binding exercising oos_gate_fail from the OOS gate fixture.
    "oos_gate_fail_demo": {
        "subject_id": "OOS-GATE-FIXTURE-RP-2592",
        "subject_label": "walkforward_oos_gate_fixture",
        "oos_from_conclusion": False,
        "review_example_id": "donchian_oos_gate_blocked",
        "artifacts": {
            "formalization": "docs/status_entries/WP-LAB-WALKFORWARD-OOS-GATE-01.md",
            "experiment_run": "scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json",
            "replay_normalization": "scratch/WP-LAB-RP-REPLAY-NORMALIZATION-CONTRACT-01/replay_fixture_summary.json",
            "walkforward_oos_gate": "scratch/WP-LAB-WALKFORWARD-OOS-GATE-01/fixture_gate_summary.json",
            "candidate_review_reach": "scratch/WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01/generic_review_contract.json",
            "reporting": "docs/research/WALKFORWARD_OOS_GATE_CONTRACT.md",
        },
    },
    # Historical committed registry / Result Population evidence. This is a
    # visibility subject only; it never creates a candidate-ready or gate state.
    "historical_canonical_evidence_bundle": {
        "subject_id": "HISTORICAL-CANONICAL-EVIDENCE",
        "subject_label": "candidate_registry_and_result_populations",
        "overall_override": "experiment_complete",
        "artifacts": {},
        "supplemental_artifacts": _supplemental(
            LEGACY_CANONICAL_EVIDENCE_PATHS,
            "canonical_evidence_reference",
            "Committed registry / Result Population evidence surfaced read-only.",
        ),
    },
    "funding_carry_01_blocked_no_go": {
        "subject_id": "WP-RESEARCH-FUNDING-CARRY-01",
        "subject_label": "funding_carry_initial_blocked_no_go",
        "artifacts": {
            "formalization": "scratch/WP-RESEARCH-FUNDING-CARRY-01/pre_registered_hypothesis.md",
            "experiment_run": "scratch/WP-RESEARCH-FUNDING-CARRY-01/denominator_manifest.json",
            "candidate_review_reach": "scratch/WP-RESEARCH-FUNDING-CARRY-01/no_candidate_review_packet_reason.json",
            "reporting": "scratch/WP-RESEARCH-FUNDING-CARRY-01/main_report_back_guardrail.txt",
        },
        "supplemental_artifacts": _supplemental(
            FUNDING_CARRY_01_PATHS,
            "legacy_research_evidence",
            "Funding-carry initial blocked/NO-GO evidence bundle.",
        ),
    },
    "funding_carry_02_no_go": {
        "subject_id": "WP-RESEARCH-FUNDING-CARRY-02",
        "subject_label": "funding_carry_retry_no_go",
        "artifacts": {
            "formalization": "scratch/WP-RESEARCH-FUNDING-CARRY-02/pre_registered_hypothesis.md",
            "experiment_run": "scratch/WP-RESEARCH-FUNDING-CARRY-02/denominator_manifest.json",
            "candidate_review_reach": "scratch/WP-RESEARCH-FUNDING-CARRY-02/no_candidate_review_packet_reason.json",
            "reporting": "scratch/WP-RESEARCH-FUNDING-CARRY-02/main_report_back_guardrail.txt",
        },
        "supplemental_artifacts": _supplemental(
            FUNDING_CARRY_02_PATHS,
            "legacy_research_evidence",
            "Funding-carry retry evidence bundle, including follow-up staging.",
        ),
    },
    "funding_fade_riskmanaged_no_go": {
        "subject_id": "H-FUNDING-FADE-RISKMANAGED-01",
        "subject_label": "funding_fade_riskmanaged_stage1_no_go",
        "artifacts": {
            "formalization": "docs/status_entries/WP-RESEARCH-FUNDING-FADE-RISKMANAGED-CONCLUDE-01.md",
            "experiment_run": "scratch/WP-RESEARCH-FUNDING-FADE-RISKMANAGED-CONCLUDE-01/conclusion_traceability.json",
            "candidate_review_reach": "scratch/WP-RESEARCH-FUNDING-FADE-RISKMANAGED-CONCLUDE-01/no_candidate_review_packet_reason.json",
            "reporting": "docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md",
        },
        "supplemental_artifacts": _supplemental(
            FUNDING_FADE_RISKMANAGED_CONCLUDE_PATHS,
            "riskmanaged_conclusion_evidence",
            "Risk-managed funding-fade Stage-1 NO-GO conclusion bundle.",
        ),
    },
    "edge_sma_family_blocked": {
        "subject_id": "WP-RESEARCH-EDGE-SMA-FAMILY-01",
        "subject_label": "edge_sma_family_blocked",
        "artifacts": {
            "formalization": "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/sma_family_research_idea.json",
            "experiment_run": "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/denominator_audit.json",
            "candidate_review_reach": "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_candidate_review_reason.json",
            "reporting": "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/sma_family_summary.md",
        },
        "supplemental_artifacts": _supplemental(
            EDGE_SMA_PATHS,
            "legacy_research_evidence",
            "Blocked SMA-family research evidence bundle.",
        ),
    },
    "orb_exit_respec_blocked": {
        "subject_id": "WP-RESEARCH-ORB-EXIT-RESPEC-01",
        "subject_label": "orb_exit_respec_blocked",
        "artifacts": {
            "formalization": "scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/orb_exit_respec_idea.json",
            "experiment_run": "scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/denominator_audit.json",
            "candidate_review_reach": "scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/blocked_candidate_review_reason.json",
            "reporting": "scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/orb_exit_respec_summary.md",
        },
        "supplemental_artifacts": _supplemental(
            ORB_EXIT_RESPEC_PATHS,
            "legacy_research_evidence",
            "Blocked ORB exit re-spec evidence bundle.",
        ),
    },
    "priceonly_synthesis_reported": {
        "subject_id": "WP-RESEARCH-PRICEONLY-SYNTHESIS-01",
        "subject_label": "priceonly_synthesis_reported",
        "artifacts": {
            "reporting": "docs/research/PRICEONLY_SYNTHESIS_2026-06.md",
        },
        "supplemental_artifacts": _supplemental(
            PRICEONLY_SYNTHESIS_PATHS,
            "legacy_research_evidence",
            "Price-only synthesis and source audit bundle.",
        ),
    },
}

DEFAULT_SUBJECT = "funding_positioning_fade_no_go"


def _format_snapshot(snapshot: dict[str, Any]) -> str:
    lines = [
        f"Lab coordinator state snapshot ({snapshot['schema_version']})",
        f"  subject: {snapshot['subject_id']}  [{snapshot['subject_label']}]",
        f"  overall_state: {snapshot['overall_state']}",
        "",
        "  Stages:",
    ]
    for stage in snapshot["stages"]:
        reason = f"  ({stage['reason_code']})" if stage["reason_code"] else ""
        lines.append(f"    {stage['stage']:<24} {stage['state']}{reason}")
        if stage["detail"]:
            lines.append(f"        {stage['detail']}")
    lines.append("")
    lines.append(f"  {snapshot['edge_search_hold']}")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--snapshot", action="store_true", help="Print a state snapshot")
    mode.add_argument("--list-states", action="store_true", help="List the state vocabulary")
    mode.add_argument("--list-stages", action="store_true", help="List pipeline stages")
    mode.add_argument("--list-subjects", action="store_true", help="List known subjects")
    parser.add_argument(
        "--subject", default=DEFAULT_SUBJECT, help="Subject key for --snapshot"
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.list_states:
        print(json.dumps(list(model.STATES), indent=2) if args.json else "\n".join(model.STATES))
        return 0
    if args.list_stages:
        print(json.dumps(list(model.STAGES), indent=2) if args.json else "\n".join(model.STAGES))
        return 0
    if args.list_subjects:
        keys = sorted(SUBJECTS)
        print(json.dumps(keys, indent=2) if args.json else "\n".join(keys))
        return 0

    subject = SUBJECTS.get(args.subject)
    if subject is None:
        print(f"ERROR: unknown subject: {args.subject}", file=sys.stderr)
        print("Available subjects:", file=sys.stderr)
        for key in sorted(SUBJECTS):
            print(f"  {key}", file=sys.stderr)
        return 1

    snapshot = build_snapshot(subject, REPO_ROOT)
    if args.json:
        print(json.dumps(snapshot, indent=2, default=str))
    else:
        print(_format_snapshot(snapshot))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
