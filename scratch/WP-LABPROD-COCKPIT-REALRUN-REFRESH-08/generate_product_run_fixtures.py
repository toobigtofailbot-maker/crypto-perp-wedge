"""Reproducibly generate committed real product-pipeline run fixtures.

The read-only cockpit product real-run panel projects the *real* product
pipeline output chain — product bridge prepare -> product runner adapter
(PR #623) -> product gates adapters (PR #624). No product runs are committed on
``origin/main`` (the adapters write to gitignored package ``outputs/`` roots), so
this script drives the real chain once into a throwaway temp repo and copies the
honest terminal artifacts into a small, committable package-local fixture the
cockpit can render.

Every artifact is produced by the *real* adapters (never hand-authored): the
existing product bridge, the existing offline runner via the runner adapter, and
the existing WFO/OOS, robustness, and candidate-review agents via the gates
adapter. The generator reuses the repository's own end-to-end test helpers so the
fixture tracks the true product-run output shape.

Two post-processing passes make the fixture safe and deterministic to commit:

1. **Path sanitization.** The chain embeds the throwaway temp-repo absolute
   prefix in a few reference fields (e.g. the candidate-surface decision's
   ``advisory_packet_ref.path``). Every such absolute prefix is rewritten to the
   repo-relative fixture path, so nothing machine-specific or absolute lands in
   the committed bytes.
2. **Deterministic run-index.** The generator writes a ``run_index.json`` — the
   cockpit's single read-only entry point per run — carrying the honest stage
   ladder, provenance ids, denominator counts, advisory surface status, and a
   repo-relative artifact manifest with present/missing + sha markers.

Run from the repo root with the project virtualenv (pandas is required by the
real runner)::

    .venv/Scripts/python.exe \
        scratch/WP-LABPROD-COCKPIT-REALRUN-REFRESH-08/generate_product_run_fixtures.py
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from tools.lab_pipeline import gates_adapter, runner_adapter
from tools.lab_pipeline.gates_adapter import run_product_gates_adapters
from tools.lab_pipeline.state import file_sha256, read_json, write_json
from tools.research_agents.candidate_review_packet_agent import CandidateReviewPacketConfig
from tools.research_agents.robustness_diagnostician_agent import RobustnessDiagnosticianConfig

# The real end-to-end test helpers drive the existing bridge + runner adapter.
from tests.test_agent_formalizer_runner_bridge import _run_product
from tests.test_lab_pipeline_runner_adapter import _run_valid_adapter, _write_execute_approval

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ID = "WP-LABPROD-COCKPIT-REALRUN-REFRESH-08"
FIXTURE_REL = f"scratch/{PACKAGE_ID}/product_runs"
FIXTURE_ROOT = REPO_ROOT / "scratch" / PACKAGE_ID / "product_runs"

RUN_INDEX_SCHEMA = "lab_product_cockpit_real_run_index_v1"

# Terminal display state vocabulary the cockpit distinguishes. Kept here so the
# generator and the read-only model agree on the same honest state ladder.
STAGE_LADDER = (
    ("idea_formalized", "Idea formalized (product bridge)"),
    ("bridge_prepared", "Strategy Spec / Variant Manifest / Sweep Plan prepared"),
    ("execute_approval_consumed", "Exact-content execute approval consumed"),
    ("runner_executed", "Offline runner executed; Result Population produced"),
    ("advisory_packet_ready", "Advisory review packet assembled"),
)

# Real artifacts copied verbatim from the gates/runner outputs into the fixture.
# ``candidate_surface_decision.json`` is intentionally excluded: it is an
# invocation-local gate-action record whose ``gate_action_id`` derives from the
# ephemeral invocation path, so it is not byte-reproducible. The advisory packet
# already carries the deterministic ``candidate_surface_routing`` the cockpit uses.
_GATES_ARTIFACT_FILES = (
    "advisory_review_packet.json",
    "advisory_review_packet.md",
    "gates_adapter_result.json",
    "wfo_oos_result.json",
    "robustness_result.json",
    "candidate_review_result.json",
    "direct_agent_reconciliation.json",
)
_RUNNER_ARTIFACT_FILE = "runner_adapter_result.json"


def _configure_temp_repo(tmp: Path) -> tuple[Path, Path]:
    """Point the runner + gates adapters at a throwaway temp repo (real code)."""
    runner_output_root = tmp / "scratch" / runner_adapter.WP_ID / "outputs"
    gates_output_root = tmp / "scratch" / gates_adapter.WP_ID / "outputs"
    runner_adapter.REPO_ROOT = tmp
    runner_adapter.DEFAULT_OUTPUT_ROOT = runner_output_root
    gates_adapter.REPO_ROOT = tmp
    # Lifecycle helper templates are read from the real repo, not the temp repo.
    gates_adapter.SOURCE_REPO_ROOT = REPO_ROOT
    gates_adapter.DEFAULT_SCRATCH_ROOT = tmp / "scratch" / gates_adapter.WP_ID
    gates_adapter.DEFAULT_OUTPUT_ROOT = gates_output_root
    return runner_output_root, gates_output_root


def _sanitize_file(path: Path, abs_prefixes: list[str], rel_prefix: str) -> None:
    """Rewrite throwaway temp-repo absolute prefixes to the fixture-relative path."""
    text = path.read_text(encoding="utf-8")
    changed = False
    for abs_prefix in abs_prefixes:
        if abs_prefix in text:
            text = text.replace(abs_prefix, rel_prefix)
            changed = True
    if changed:
        path.write_text(text, encoding="utf-8", newline="\n")


def _artifact_manifest(run_dir: Path, files: list[str]) -> list[dict]:
    manifest = []
    for name in files:
        target = run_dir / name
        present = target.is_file()
        manifest.append(
            {
                "filename": name,
                "path": f"{FIXTURE_REL}/{run_dir.name}/{name}",
                "present": present,
                "sha256": file_sha256(target) if present else None,
            }
        )
    return manifest


def _build_run_index(
    *,
    run_dir: Path,
    advisory: dict,
    runner_summary: dict,
    provenance: dict,
) -> dict:
    denominator = dict(advisory["denominator_counts"])
    routing = advisory["candidate_surface_routing"]
    stage_records = [
        {"stage": stage, "label": label, "reached": True}
        for stage, label in STAGE_LADDER
    ]
    files = list(_GATES_ARTIFACT_FILES) + [_RUNNER_ARTIFACT_FILE]
    return {
        "schema_version": RUN_INDEX_SCHEMA,
        "package_id": PACKAGE_ID,
        "gates_adapter_run_id": advisory["gates_adapter_run_id"],
        "provenance": provenance,
        "terminal_state": "advisory_packet_ready",
        "terminal_label": "ADVISORY PACKET READY",
        "adapter_status": advisory["adapter_status"],
        "posture": advisory["posture"],
        "real_run": True,
        "runner_invoked": True,
        "stage_ladder": stage_records,
        "denominator_counts": denominator,
        "full_denominator_preserved": bool(advisory["full_denominator_preserved"]),
        # Advisory-only routing derived from the deterministic advisory packet.
        # This is a review-routing value, never a candidate admission.
        "candidate_surface_status": routing["surface_status"],
        "candidate_surface_allowed_statuses": list(
            routing.get("allowed_statuses", [])
        ),
        "candidate_lifecycle_written": bool(
            routing.get("candidate_lifecycle_written", False)
        ),
        "go_auto_admission": bool(routing.get("go_auto_admission", False)),
        "go_auto_crossing": bool(routing.get("go_auto_crossing", False)),
        "go_auto_promotion": bool(routing.get("go_auto_promotion", False)),
        "non_promotion_posture": dict(advisory["non_promotion_posture"]),
        "runner_denominator_counts": dict(runner_summary["denominator_counts"]),
        "artifacts": _artifact_manifest(run_dir, files),
    }


def _generate_one(tmp: Path) -> str:
    runner_output_root, gates_output_root = _configure_temp_repo(tmp)

    bridge_result, _ = _run_product(tmp)
    bridge_review = read_json(tmp / bridge_result["artifact_paths"]["human_review_packet"])
    metadata = bridge_review["product_bridge_preparation_metadata"]
    approval_path = _write_execute_approval(
        tmp, runner_output_root, bridge_result, bridge_review
    )
    runner_result = _run_valid_adapter(
        tmp, runner_output_root, bridge_result, bridge_review, approval_path
    )
    gates_result = run_product_gates_adapters(
        runner_adapter_result_path=runner_result.artifact_paths["runner_adapter_result"],
        output_root=gates_output_root,
        robustness_config=RobustnessDiagnosticianConfig(bootstrap_samples=50),
        candidate_review_config=CandidateReviewPacketConfig(
            timestamp_utc="2026-07-08T00:00:00Z"
        ),
    )

    gates_run_dir = gates_result.output_dir
    runner_run_dir = (tmp / runner_result.artifact_paths["runner_adapter_result"]).parent
    run_id = gates_result.gates_adapter_run_id
    dest = FIXTURE_ROOT / run_id
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    for name in _GATES_ARTIFACT_FILES:
        shutil.copyfile(gates_run_dir / name, dest / name)
    shutil.copyfile(runner_run_dir / _RUNNER_ARTIFACT_FILE, dest / _RUNNER_ARTIFACT_FILE)

    # Sanitize any throwaway temp-repo absolute prefix out of committed bytes.
    abs_prefixes = [
        tmp.resolve().as_posix(),
        str(tmp.resolve()),
    ]
    rel_prefix = f"{FIXTURE_REL}/{run_id}/_invocation_local"
    for path in sorted(dest.rglob("*")):
        if path.is_file():
            _sanitize_file(path, abs_prefixes, rel_prefix)

    advisory = read_json(dest / "advisory_review_packet.json")
    runner_summary = read_json(dest / _RUNNER_ARTIFACT_FILE)
    provenance = {
        "product_pipeline_run_id": metadata["product_pipeline_run_id"],
        "bridge_preparation_run_id": bridge_result["run_id"],
        "runner_adapter_run_id": runner_result.runner_adapter_run_id,
        "gates_adapter_run_id": run_id,
    }
    run_index = _build_run_index(
        run_dir=dest,
        advisory=advisory,
        runner_summary=runner_summary,
        provenance=provenance,
    )
    write_json(dest / "run_index.json", run_index)
    print(f"{run_id} -> terminal={run_index['terminal_state']} "
          f"surface={run_index['candidate_surface_status']} "
          f"denominator={run_index['denominator_counts']}")
    return run_id


def main() -> None:
    FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="labprod-realrun-fixture-") as tmp:
        _generate_one(Path(tmp))
    print(f"fixtures written under {FIXTURE_REL}")


if __name__ == "__main__":
    main()
