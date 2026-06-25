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
