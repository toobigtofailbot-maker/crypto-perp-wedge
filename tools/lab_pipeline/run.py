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

from tools.lab_pipeline.orchestrator import (
    DEFAULT_OUTPUT_ROOT,
    approval_template_for,
    run_pipeline,
)
from tools.lab_pipeline.state import write_json


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True, help="Pipeline request JSON")
    parser.add_argument("--approval", type=Path, help="Optional prereg approval marker JSON")
    parser.add_argument(
        "--out-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Output root for pipeline run packets",
    )
    parser.add_argument(
        "--write-approval-template",
        type=Path,
        help="Write an approval template for an existing preregistration packet and exit",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.write_approval_template is not None:
        template = approval_template_for(args.write_approval_template)
        target = args.write_approval_template.with_name("approval_marker.template.json")
        write_json(target, template)
        print(target.as_posix())
        return 0

    try:
        result = run_pipeline(
            request_path=args.request,
            approval_path=args.approval,
            output_root=args.out_root,
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
