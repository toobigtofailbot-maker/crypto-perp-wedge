"""Read-only bounded envelope/control validator; absence is valid."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.research_autonomy.envelope import validate_control, validate_envelope

REPO_ROOT = Path(__file__).resolve().parents[2]


def validate_files(paths: list[Path], *, repo_sha: str) -> int:
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    envelopes = {}
    controls = []
    for payload in payloads:
        if payload.get("schema_version") == "cpw_bounded_research_envelope_control_v1":
            controls.append(payload)
        else:
            envelope = validate_envelope(payload, repo_sha=repo_sha)
            key = (envelope.envelope_id, envelope.envelope_version)
            if key in envelopes and envelopes[key] != envelope:
                raise ValueError("conflicting envelope identity")
            envelopes[key] = envelope
    actions = set()
    for payload in controls:
        key = (payload.get("envelope_id"), payload.get("envelope_version"))
        if key not in envelopes:
            raise ValueError("control requires exact target envelope file")
        control = validate_control(payload, envelope=envelopes[key])
        if control.control_action_id in actions:
            raise ValueError("duplicate control action ID")
        actions.add(control.control_action_id)
        if control.successor:
            successor = envelopes.get((control.successor.envelope_id, control.successor.envelope_version))
            if successor is None or successor.content_sha256 != control.successor.content_sha256:
                raise ValueError("replacement successor binding mismatch")
    return len(payloads)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=Path)
    parser.add_argument("--repo-sha")
    args = parser.parse_args(argv)
    paths = args.files or sorted((REPO_ROOT / "research/autonomy/envelopes").glob("*.json"))
    repo_sha = args.repo_sha or subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()
    try:
        count = validate_files(paths, repo_sha=repo_sha)
    except (ValueError, OSError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        # Schema/model failures are validation failures, never artifact writes.
        print(f"FAIL: {type(exc).__name__}", file=sys.stderr)
        return 1
    print(f"PASS: {count} bounded envelope/control files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
