"""Manual offline 02H study-plan preflight; structure only, no scientific authority."""

from __future__ import annotations

import argparse
import json
import sys
from itertools import pairwise
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, ValidationError

from tools.hermes import verified_data_signal_bridge as bridge

qp, de, hs = bridge.qp, bridge.de, bridge.hs
SCHEMA = "cpw_hermes_scientific_protocol_preflight_v1"
PROPOSAL_SCHEMA = "cpw_hermes_scientific_protocol_proposal_v1"
BASE_SHA = "cf4a456e54b7d0553c0be9282dcdc9f40cfe7ff5"
REVIEW_FILE = "review.md"
STRUCTURED = "PROPOSED_STRUCTURE_ONLY_REVIEW_REQUIRED"
PARTITIONS = ("construction", "validation", "final_holdout")
REQUIRED = (
    "source_sha256",
    "primary_timeframe",
    "windows",
    "purge_bars",
    "embargo_bars",
    "warmup_bars",
    "leakage_considerations",
    "costs",
    "budget",
    "robustness_plan",
    "multiple_testing_plan",
    "lineage_refs",
    "parameters",
)
# Every downstream binding a real scientific route needs; none is produced here.
DECISIONS = (
    "independent non-holdout/holdout partition provenance certification (none exists)",
    "human scientific protocol, leakage, purge/embargo and warmup adequacy authority",
    "human fee/slippage/funding cost-model authority",
    "Strategy Spec semantic review and canonical admission",
    "native scientific pipeline binding and genuine preregistration identity",
    "durable envelope, trial/denominator lineage and Stage 5B activation",
)
INPUT_MAP = {
    "strategy_spec": "DRAFT_HASH_FOR_REVIEW_NOT_CANONICAL",
    "data_source": "VERIFIED_SOURCE_IDENTITY_NO_PARTITION_CERTIFICATE",
    "scientific_protocol": "OPERATOR_PROPOSED_UNCERTIFIED",
    "cost_model": "OPERATOR_ASSUMPTION_UNCERTIFIED",
    "final_holdout": "BOUNDARY_COORDINATES_ONLY_NOT_CERTIFIED_NOT_INSPECTED",
    "preregistration": "NOT_ISSUABLE",
    "pipeline_request": "NOT_EMITTED",
    "search_contract": "NOT_ISSUABLE",
    "envelope_and_lineage": "ABSENT",
}
Text = Annotated[str, Field(min_length=1, max_length=4_000)]
Sha = Annotated[str, Field(pattern=hs._SHA)]
Bars = Annotated[int, Field(ge=0, le=100_000)]
Cost = Annotated[float, Field(ge=0, le=10_000, allow_inf_nan=False)]


class Window(hs._Strict):
    start: str
    end: str


class Windows(hs._Strict):
    construction: Window
    validation: Window
    final_holdout: Window


class Costs(hs._Strict):
    fee_bps: Cost
    slippage_bps: Cost
    funding_source: Text
    cost_source: Text


class Budget(hs._Strict):
    max_trials: Annotated[int, Field(ge=1, le=1_000_000)]
    max_compute_minutes: Annotated[int, Field(ge=1, le=1_000_000)]


class IdeaPlan(hs._Strict):
    """Missing fields are proposal gaps, never inferred defaults."""

    source_sha256: Sha | None = None
    primary_timeframe: Literal[de.TIMEFRAMES] | None = None
    windows: Windows | None = None
    purge_bars: Bars | None = None
    embargo_bars: Bars | None = None
    warmup_bars: Bars | None = None
    leakage_considerations: Text | None = None
    costs: Costs | None = None
    budget: Budget | None = None
    robustness_plan: Text | None = None
    multiple_testing_plan: Text | None = None
    lineage_refs: Annotated[list[Text], Field(min_length=1, max_length=32)] | None = None
    parameters: Annotated[list[str], Field(min_length=1, max_length=32)] | None = None
    features: Annotated[list[str], Field(max_length=32, default_factory=list)]


class ProposalV1(hs._Strict):
    schema_version: Literal[PROPOSAL_SCHEMA]
    source_02g: Sha
    provenance: Literal[bridge.FIXTURE, "OPERATOR_PROPOSED_HISTORICAL"]
    # A real certificate does not exist yet; anything but this acknowledgment is refused.
    non_holdout_certificate: Literal["NOT_AVAILABLE"]
    operator: Annotated[str, Field(pattern=hs._SAFE_ID)]
    rationale: Text
    ideas: Annotated[dict[str, IdeaPlan], Field(min_length=1, max_length=hs.MAX_IDEAS)]


def _ts(value: str):
    return de.pd.Timestamp(value)


def _structure(plan: IdeaPlan, base: dict) -> list[str]:
    """Structural window/coverage findings from operator coordinates and verified metadata only."""
    findings = []
    bar = de.pd.Timedelta(plan.primary_timeframe)
    windows = {}
    for name in PARTITIONS:
        window = getattr(plan.windows, name).model_dump()
        try:
            qp._window(window)
        except (hs.HandoffError, ValueError) as exc:
            findings.append(f"{name}: {exc}")
            continue
        a, b = _ts(window["start"]), _ts(window["end"])
        if (a - _ts("1970-01-01T00:00:00Z")) % bar or (b - _ts("1970-01-01T00:00:00Z")) % bar:
            findings.append(f"{name}: boundaries not aligned to {plan.primary_timeframe} bars")
        windows[name] = (a, b)
    if len(windows) != len(PARTITIONS):
        return findings
    separation = (plan.purge_bars + plan.embargo_bars) * bar
    for first, second in pairwise(PARTITIONS):
        gap = windows[second][0] - windows[first][1]
        if gap < de.pd.Timedelta(0):
            findings.append(f"{first}/{second}: partitions overlap or are out of order")
        elif gap < separation:
            findings.append(f"{first}/{second}: gap shorter than declared purge+embargo bars")
    start, end = _ts(base["coverage_start"]), _ts(base["coverage_end_exclusive"])
    if windows["construction"][0] - plan.warmup_bars * bar < start:
        findings.append("construction: declared warmup precedes verified source coverage")
    if windows["final_holdout"][1] > end:
        findings.append("final_holdout: boundary exceeds verified source coverage metadata")
    return findings


class ScientificProtocolPreflight:
    def __init__(self, root: Path = de.ROOT):
        self.bridge = bridge.VerifiedDataSignalBridge(root)

    def build_files(
        self,
        signal_dir: Path,
        preparation_dir: Path,
        evidence_dir: Path,
        chain: tuple,
        workspace: Path,
        *,
        proposal: Path | None = None,
        **options,
    ) -> dict[str, bytes]:
        before = hs._read_tree(signal_dir)
        upstream = self.bridge.verify(
            signal_dir, preparation_dir, evidence_dir, chain, workspace, **options
        )
        raw = None
        plans = {}
        if proposal is not None:
            raw = de._local(proposal.absolute().parent, proposal.name).read_bytes()
            try:
                parsed = ProposalV1.model_validate(hs._strict_json(raw))
            except ValidationError as exc:
                raise hs.HandoffError(
                    f"proposal schema refused: {exc.error_count()} errors"
                ) from exc
            if parsed.source_02g != upstream["content_sha256"]:
                raise hs.HandoffError("proposal is bound to a different 02G packet")
            if (parsed.provenance == bridge.FIXTURE) != (upstream["label"] == bridge.FIXTURE):
                raise hs.HandoffError("synthetic fixture and historical provenance confused")
            if set(parsed.ideas) - {i["idea_id"] for i in upstream["ideas"]}:
                raise hs.HandoffError("proposal contains unknown ideas")
            plans = parsed.ideas
        ideas = [self._idea(entry, plans.get(entry["idea_id"])) for entry in upstream["ideas"]]
        shared = {}
        for idea in ideas:
            for base in idea["source_02g_idea"]["source_02e_recheck"]["bases"]:
                key = f"{base['timeframe']}:{base['local'].get('sha256')}"
                shared.setdefault(key, {"timeframe": base["timeframe"], "ideas": []})
                shared[key]["ideas"].append(idea["idea_id"])
        if hs._read_tree(signal_dir) != before or (
            proposal is not None
            and de._local(proposal.absolute().parent, proposal.name).read_bytes() != raw
        ):
            raise hs.HandoffError("02G packet or proposal changed during preflight")
        summary = hs._hashed(
            {
                "schema_version": SCHEMA,
                "authority": hs.AUTHORITY,
                "repo_sha": upstream["repo_sha"],
                "base_sha": BASE_SHA,
                "source_02g": upstream["content_sha256"],
                "source_02g_label": upstream["label"],
                "source_packet_hashes": {n: de.dc._sha256_bytes(v) for n, v in before.items()},
                "proposal_sha256": de.dc._sha256_bytes(raw) if raw else None,
                "proposal_provenance": parsed.provenance if raw else None,
                "limitation": "PROPOSED_STRUCTURE_ONLY; no scientific eligibility, "
                "holdout certification, preregistration or execution authority",
                "non_holdout_certificate": "NOT_AVAILABLE",
                "final_holdout_contents": "NEVER_READ",
                "science_status": "NOT_READY",
                "search_contract_status": "NOT_ISSUABLE",
                "stage_5b_active": False,
                "canonical_write_allowed": False,
                "selection": "NONE_ALL_IDEAS_RETAINED",
                "shared_source_requirements": dict(sorted(shared.items())),
                "material_decisions": list(DECISIONS),
                "investigation_queue": upstream["investigation_queue"],
                "ideas": ideas,
            }
        )
        files = {hs.SUMMARY_FILE: hs._json_bytes(summary), REVIEW_FILE: _review(summary)}
        return self.bridge.preparation.evidence.readiness.handoff._guard(hs._render(files))

    def _idea(self, entry: dict, plan: IdeaPlan | None) -> dict:
        retained = entry["source_02e_recheck"]
        bases = retained["bases"]
        drafts = [c["draft"] for c in entry["compilations"]]
        names = {p["name"] for c in entry["compilations"] for p in c["parameters"]["parameters"]}
        result = {
            "idea_id": entry["idea_id"],
            "index": entry["index"],
            "source_02g_status": entry["status"],
            # The complete verified 02G entry: drafts, critique, memory, data and science gaps.
            "source_02g_idea": entry,
            "draft_sha256s": [d["file_sha256"] for d in drafts],
            "parameter_names": sorted(names),
            "plan": plan.model_dump() if plan else None,
            "missing_inputs": [],
            "structural_findings": [],
            "science_status": "NOT_READY",
            "input_map": INPUT_MAP,
        }
        if plan is None:
            result["status"] = "NOT_READY_PROPOSAL_MISSING"
            return result
        # Identity mismatches are refusals, not gaps: substitutions must never be reviewed as plans.
        if set(plan.parameters or ()) - names:
            raise hs.HandoffError(f"{entry['idea_id']}: unknown parameter for its verified draft")
        known = {f["feature"]: f["status"] for f in retained["features"]}
        if set(plan.features) - set(known):
            raise hs.HandoffError(f"{entry['idea_id']}: feature not in verified evidence")
        base = bases[0] if len(bases) == 1 else None
        if plan.source_sha256 is not None and (
            base is None or plan.source_sha256 != base["local"].get("sha256")
        ):
            raise hs.HandoffError(f"{entry['idea_id']}: source differs from verified source")
        if plan.primary_timeframe is not None and (
            base is None or plan.primary_timeframe != base["timeframe"]
        ):
            raise hs.HandoffError(f"{entry['idea_id']}: timeframe differs from verified source")
        result["missing_inputs"] = [k for k in REQUIRED if getattr(plan, k) is None]
        result["missing_inputs"] += [
            f"feature_evidence:{f}" for f in plan.features if known[f] == "NOT_READY"
        ]
        # 02G PASS already implies exactly one WINDOW_VERIFIED base of the primary timeframe.
        if entry["status"] != "PASS":
            result["status"] = "NOT_READY_UPSTREAM_NOT_COMPILED"
        elif result["missing_inputs"]:
            result["status"] = "NOT_READY_PROPOSAL_INCOMPLETE"
        else:
            result["structural_findings"] = _structure(plan, base["local"])
            result["status"] = (
                "NOT_READY_STRUCTURE_INVALID" if result["structural_findings"] else STRUCTURED
            )
        return result

    @staticmethod
    def _disjoint(output: Path, signal_dir: Path, inputs: tuple, options: dict) -> None:
        for path in (signal_dir, *inputs[:2], *inputs[2], inputs[3], *options.values()):
            if isinstance(path, Path):
                qp._separate(output, path)

    def build(self, output: Path, signal_dir: Path, *inputs, **options):
        self._disjoint(output, signal_dir, inputs, options)
        qp._external_target(output)
        files = self.build_files(signal_dir, *inputs, **options)
        hs._publish(files, output, lambda p: self.verify(p, signal_dir, *inputs, **options))
        return hs._strict_json(files[hs.SUMMARY_FILE])

    def verify(self, output: Path, signal_dir: Path, *inputs, **options):
        self._disjoint(output, signal_dir, inputs, options)
        qp._packet_paths(output)
        files = hs._read_tree(output)
        summary = hs._strict_json(files[hs.SUMMARY_FILE])
        hs._check_hash(summary, SCHEMA)
        if files != self.build_files(signal_dir, *inputs, **options):
            raise hs.HandoffError("02H replay did not reproduce exact bytes")
        return summary


def _review(summary: dict) -> bytes:
    lines = [
        "# 02H scientific protocol preflight (structure only)",
        "",
        f"- 02G source: `{summary['source_02g']}` ({summary['source_02g_label']})",
        f"- Proposal: `{summary['proposal_sha256']}`",
        "- Science NOT_READY; SearchContract NOT_ISSUABLE; Stage 5B inactive; no canonical write.",
        "- No non-holdout certificate exists; final-holdout contents were never read.",
        "",
        "| # | Idea | 02G | 02H status | Missing | Findings |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for i in summary["ideas"]:
        lines.append(
            f"| {i['index']} | {i['idea_id']} | {i['source_02g_status']} | {i['status']} | "
            f"{', '.join(i['missing_inputs']) or '-'} | {'; '.join(i['structural_findings']) or '-'} |"
        )
    lines += ["", "## Decisions this tool cannot make", ""]
    lines += [f"- {d}" for d in summary["material_decisions"]]
    return ("\n".join(lines) + "\n").encode("utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify", "replay"))
    for name in (
        "output",
        "signal-dir",
        "preparation-dir",
        "evidence-dir",
        "readiness-dir",
        "built-dir",
        "prepared-dir",
        "responses-dir",
        "workspace",
    ):
        parser.add_argument("--" + name, required=True, type=Path)
    for name in (
        "proposal",
        "designation",
        "local-root",
        "inventory",
        "requests",
        "evidence-local-root",
    ):
        parser.add_argument("--" + name, type=Path)
    parser.add_argument("--materialize", action="store_true")
    args = parser.parse_args(argv)
    options = {
        key: getattr(args, key)
        for key in (
            "proposal",
            "designation",
            "local_root",
            "inventory",
            "requests",
            "evidence_local_root",
            "materialize",
        )
    }
    try:
        adapter = ScientificProtocolPreflight()
        chain = (args.readiness_dir, args.built_dir, args.prepared_dir, args.responses_dir)
        method = adapter.build if args.command == "build" else adapter.verify
        result = method(
            args.output,
            args.signal_dir,
            args.preparation_dir,
            args.evidence_dir,
            chain,
            args.workspace,
            **options,
        )
    except (ValueError, OSError, KeyError, TypeError, RuntimeError, de.dc.ConsumerError) as exc:
        print(f"SCIENTIFIC_PROTOCOL_PREFLIGHT_FAILED: {type(exc).__name__}", file=sys.stderr)
        return 1
    print(json.dumps({k: result[k] for k in ("content_sha256", "science_status")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
