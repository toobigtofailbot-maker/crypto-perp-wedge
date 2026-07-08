"""Reproducibly generate committed, repo-relative lab-pipeline run fixtures.

The read-only cockpit pipeline-state panel projects real ``tools/lab_pipeline``
output packets. No pipeline runs are committed on ``origin/main`` (the
orchestrator writes to a gitignored ``outputs/`` root), so this script produces
a small, honest set of package-local fixture runs the cockpit can render.

Each fixture is produced by the *real* orchestrator (``run_pipeline``) — never
hand-authored — so the fixtures track the true pipeline output shape. Two
post-processing passes make them safe to commit:

1. **Path sanitization.** The orchestrator embeds absolute machine paths in
   ``artifact_refs`` / ``artifact_index`` / the operator review packet. Every
   absolute run-directory prefix is rewritten to the repo-relative fixture path,
   so nothing machine-specific or absolute is committed.
2. **Hash refresh.** After sanitization the artifact bytes change, so
   ``artifact_index.json`` hashes are recomputed over the final committed files
   and stay honest.

Scenarios cover the three operator-meaningful states: an approved *spine-only*
completion (``runner_invoked=false``), an *awaiting prereg approval* halt, and an
*availability-blocked* run. No approval is ever a real hypothesis run; the
approved run is the deterministic spine proof only.

Run from the repo root::

    python scratch/WP-LABPROD-COCKPIT-PIPELINE-STATE-02/generate_pipeline_run_fixtures.py
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from tools.lab_pipeline.orchestrator import (
    approval_template_for,
    run_pipeline,
)
from tools.lab_pipeline.state import file_sha256, write_json

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = (
    REPO_ROOT
    / "scratch"
    / "WP-LABPROD-COCKPIT-PIPELINE-STATE-02"
    / "pipeline_runs"
)
FIXTURE_REL = "scratch/WP-LABPROD-COCKPIT-PIPELINE-STATE-02/pipeline_runs"

# Distinct requests -> distinct deterministic run ids -> distinct fixture dirs.
SCENARIOS = (
    {
        "name": "complete_spine",
        "approve": True,
        "request": {
            "source_idea": "RVOL breakout continuation on BTCUSDT with a 15m volatility filter",
            "symbol": "BTCUSDT",
            "timeframe": "15m",
            "requested_by": "Karl",
        },
    },
    {
        "name": "awaiting_approval",
        "approve": False,
        "request": {
            "source_idea": "Funding-carry mean reversion on BTCUSDT over the 1h research timeframe",
            "symbol": "BTCUSDT",
            "timeframe": "1h",
            "requested_by": "Karl",
        },
    },
    {
        "name": "availability_blocked",
        "approve": False,
        "request": {
            "source_idea": "Momentum idea on an unsupported research timeframe",
            "symbol": "BTCUSDT",
            "timeframe": "3m",
            "requested_by": "Karl",
        },
    },
)


def _sanitize_dir(run_dir: Path, abs_prefix: str, rel_prefix: str) -> None:
    """Rewrite absolute run-dir path prefixes to the repo-relative fixture path."""
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if abs_prefix in text:
            path.write_text(text.replace(abs_prefix, rel_prefix), encoding="utf-8", newline="\n")


def _refresh_index(run_dir: Path) -> None:
    """Recompute artifact_index hashes over the final (sanitized) committed files."""
    index_path = run_dir / "artifact_index.json"
    if not index_path.exists():
        return
    index = json.loads(index_path.read_text(encoding="utf-8"))
    for name, entry in index.get("artifacts", {}).items():
        rel = Path(entry["path"]).name
        artifact = run_dir / rel
        entry["sha256"] = file_sha256(artifact) if artifact.exists() else None
    write_json(index_path, index)


def _generate_one(scenario: dict, tmp_out: Path) -> str:
    request_path = tmp_out / f"{scenario['name']}_request.json"
    request_path.write_text(json.dumps(scenario["request"]), encoding="utf-8")

    result = run_pipeline(request_path=request_path, output_root=tmp_out)
    run_dir = result.output_dir
    if scenario["approve"]:
        template = approval_template_for(run_dir / "preregistration_packet.json")
        approval_path = tmp_out / f"{scenario['name']}_approval.json"
        write_json(approval_path, template)
        result = run_pipeline(
            request_path=request_path,
            approval_path=approval_path,
            output_root=tmp_out,
        )
        run_dir = result.output_dir

    run_id = result.pipeline_run_id
    dest = FIXTURE_ROOT / run_id
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(run_dir, dest)

    abs_prefix = run_dir.resolve().as_posix()
    rel_prefix = f"{FIXTURE_REL}/{run_id}"
    _sanitize_dir(dest, abs_prefix, rel_prefix)
    _refresh_index(dest)
    print(f"{scenario['name']:22s} -> {run_id} ({result.pipeline_status})")
    return run_id


def main() -> None:
    FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_out = Path(tmp)
        for scenario in SCENARIOS:
            _generate_one(scenario, tmp_out)
    print(f"fixtures written under {FIXTURE_REL}")


if __name__ == "__main__":
    main()
