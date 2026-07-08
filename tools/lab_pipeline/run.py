"""CLI for the non-canonical lab pipeline orchestrator.

The CLI writes deterministic scratch packets only. It does not create canonical
evidence, candidate lifecycle entries, scheduler actions, notifications, or any
paper/live/runtime contact.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.lab_pipeline.gate_actions import (
    ALLOWED_CANDIDATE_SURFACE_DECISIONS,
    APPROVAL_REQUIRED_FIELDS,
    GateActionError,
    create_prereg_approval_marker,
    preview_prereg_approval,
    record_candidate_surface_decision,
)
from tools.lab_pipeline.orchestrator import (
    DEFAULT_OUTPUT_ROOT,
    approval_template_for,
    run_pipeline,
)
from tools.lab_pipeline.state import write_json


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, help="Pipeline request JSON")
    parser.add_argument("--approval", type=Path, help="Optional prereg approval marker JSON")
    parser.add_argument(
        "--out-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Output root for pipeline run packets",
    )
    parser.add_argument(
        "--run-adapters",
        action="store_true",
        help="After exact prereg approval, run the package-local adapter-backed flow",
    )
    parser.add_argument(
        "--adapter-out-root",
        type=Path,
        help="Output root for adapter packets; defaults to the adapter package scratch root",
    )
    parser.add_argument(
        "--write-approval-template",
        type=Path,
        help="Write an approval template for an existing preregistration packet and exit",
    )
    parser.add_argument(
        "--gate-action",
        choices=("prereg-preview", "prereg-approve", "candidate-decision"),
        help="Run a local non-canonical gate action and exit",
    )
    parser.add_argument("--approval-requirement", type=Path, help="approval_requirement.json path")
    parser.add_argument("--preregistration-packet", type=Path, help="preregistration_packet.json path")
    parser.add_argument("--output", type=Path, help="Gate-action output file")
    parser.add_argument("--gate-action-id", help="Optional explicit gate action ID")
    parser.add_argument("--schema-version", help="Approval marker schema version")
    parser.add_argument("--approved-by", help="Approval actor; must be Karl for prereg approval")
    parser.add_argument("--approval-scope", help="Approval scope")
    parser.add_argument("--approval-statement", help="Exact approval statement")
    parser.add_argument("--approval-timestamp-utc", help="Explicit approval timestamp")
    parser.add_argument(
        "--authorizes-noncanonical-offline-research-execution",
        type=_parse_bool,
        help="Explicit boolean approval flag",
    )
    parser.add_argument("--authorizes-canonical-write", type=_parse_bool)
    parser.add_argument("--authorizes-candidate-lifecycle", type=_parse_bool)
    parser.add_argument("--authorizes-paper-live-runtime", type=_parse_bool)
    parser.add_argument("--authorizes-scheduler-autonomy", type=_parse_bool)
    parser.add_argument("--authorizes-notifications", type=_parse_bool)
    parser.add_argument("--preregistration-packet-sha256", help="Packet hash supplied by operator")
    parser.add_argument("--authorizes-crossing", type=_parse_bool)
    parser.add_argument("--authorizes-promotion-or-readiness", type=_parse_bool)
    parser.add_argument("--authorizes-provider-api-or-credentials", type=_parse_bool)
    parser.add_argument("--authorizes-dependency-config-data-acquisition", type=_parse_bool)
    parser.add_argument("--authorizes-protected-path-touch", type=_parse_bool)
    parser.add_argument(
        "--decision",
        choices=sorted(ALLOWED_CANDIDATE_SURFACE_DECISIONS),
        help="Candidate-surface advisory decision",
    )
    parser.add_argument("--decided-by", help="Decision actor")
    parser.add_argument("--decision-timestamp-utc", help="Explicit decision timestamp")
    parser.add_argument("--decision-rationale", default="", help="Optional decision rationale")
    parser.add_argument("--advisory-packet", type=Path, help="Optional advisory packet JSON")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    return parser


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise argparse.ArgumentTypeError("expected true or false")


def _operator_fields_from_args(args: argparse.Namespace) -> dict[str, object]:
    names = set(APPROVAL_REQUIRED_FIELDS) | {
        "authorizes_crossing",
        "authorizes_promotion_or_readiness",
        "authorizes_provider_api_or_credentials",
        "authorizes_dependency_config_data_acquisition",
        "authorizes_protected_path_touch",
    }
    fields: dict[str, object] = {}
    for name in names:
        value = getattr(args, name, None)
        if value is not None:
            fields[name] = value
    return fields


def _run_gate_action(args: argparse.Namespace) -> int:
    try:
        if args.gate_action == "prereg-preview":
            if args.approval_requirement is None or args.preregistration_packet is None:
                raise GateActionError("--approval-requirement and --preregistration-packet are required")
            result = preview_prereg_approval(
                approval_requirement_path=args.approval_requirement,
                preregistration_packet_path=args.preregistration_packet,
                output_file=args.output,
                gate_action_id=args.gate_action_id,
            )
        elif args.gate_action == "prereg-approve":
            if args.approval_requirement is None or args.preregistration_packet is None:
                raise GateActionError("--approval-requirement and --preregistration-packet are required")
            result = create_prereg_approval_marker(
                approval_requirement_path=args.approval_requirement,
                preregistration_packet_path=args.preregistration_packet,
                operator_fields=_operator_fields_from_args(args),
                output_file=args.output,
                gate_action_id=args.gate_action_id,
            )
        elif args.gate_action == "candidate-decision":
            if args.decision is None:
                raise GateActionError("--decision is required")
            if args.decided_by is None or args.decision_timestamp_utc is None:
                raise GateActionError("--decided-by and --decision-timestamp-utc are required")
            result = record_candidate_surface_decision(
                decision=args.decision,
                decided_by=args.decided_by,
                decision_timestamp_utc=args.decision_timestamp_utc,
                advisory_packet_path=args.advisory_packet,
                rationale=args.decision_rationale,
                output_file=args.output,
                gate_action_id=args.gate_action_id,
            )
        else:
            raise GateActionError(f"unknown gate action: {args.gate_action}")
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    else:
        print(f"gate_action_id: {result.gate_action_id}")
        print(f"action_kind: {result.action_kind}")
        print(f"output_path: {result.output_path.as_posix()}")
        print(f"output_sha256: {result.output_sha256}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.gate_action is not None:
        return _run_gate_action(args)
    if args.write_approval_template is not None:
        template = approval_template_for(args.write_approval_template)
        target = args.write_approval_template.with_name("approval_marker.template.json")
        write_json(target, template)
        print(target.as_posix())
        return 0
    if args.request is None:
        print("ERROR: --request is required unless --gate-action or --write-approval-template is used", file=sys.stderr)
        return 1

    try:
        result = run_pipeline(
            request_path=args.request,
            approval_path=args.approval,
            output_root=args.out_root,
            run_adapters=args.run_adapters,
            adapter_output_root=args.adapter_out_root,
        )
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    payload = {
        "pipeline_run_id": result.pipeline_run_id,
        "pipeline_status": result.pipeline_status,
        "current_stage": result.current_stage,
        "output_dir": result.output_dir.as_posix(),
        "blocked_reasons": list(result.blocked_reasons),
        "artifact_paths": result.artifact_paths,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"pipeline_run_id: {result.pipeline_run_id}")
        print(f"pipeline_status: {result.pipeline_status}")
        print(f"current_stage: {result.current_stage}")
        print(f"output_dir: {result.output_dir.as_posix()}")
        if result.blocked_reasons:
            print("blocked_reasons:")
            for reason in result.blocked_reasons:
                print(f"  - {reason}")
    if result.pipeline_status == "complete":
        return 0
    if result.pipeline_status == "awaiting_prereg_approval":
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
